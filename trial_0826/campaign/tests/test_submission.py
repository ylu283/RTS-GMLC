import csv
import os

import pytest

import get_row
import resubmit_missing
import submit_array


def test_sge_script_contents(pilot_wave):
    script = os.path.join(pilot_wave, "pilot_array.sh")
    text = open(script).read()
    assert "#$ -t 1-12" in text
    assert "#$ -tc" in text
    assert "#$ -cwd" in text
    assert "#$ -q long" in text
    assert "set -euo pipefail" in text
    assert "-m ae" not in text
    assert "/Users/" not in text  # committed script must run on CRC unchanged
    assert 'eval "$(python "$TRIAL_DIR/campaign/get_row.py"' in text
    assert os.access(script, os.X_OK)


def test_sge_script_asserts_contiguous_indices(tmp_path, tiers):
    import design_tools as dt
    rows = [dt.make_row(tiers, {"nuclear": (0.1, 20.0)}, index=i) for i in (1, 3)]
    df = dt.rows_to_matrix(rows, tiers)
    wave_dir = tmp_path / "gap"
    wave_dir.mkdir()
    df.to_csv(wave_dir / "design_matrix.csv", index=False)
    with pytest.raises(AssertionError):
        submit_array.generate_script(str(wave_dir))


def test_get_row_scalars_only(pilot_wave):
    lines = get_row.shell_assignments(5, os.path.join(pilot_wave, "design_matrix.csv"))
    assert lines == ["INDEX=5", "NUM_DAYS=7", "START_DATE=01-01-2020"]
    lines = get_row.shell_assignments(1, os.path.join(pilot_wave, "design_matrix.csv"))
    assert "NUM_DAYS=366" in lines
    assert not any("{" in line for line in lines)  # never the JSON


def make_fake_wave(tmp_path, n=12, missing=(3, 5, 6, 7, 12), partial=()):
    wave_dir = tmp_path / "fake"
    runs = wave_dir / "runs"
    runs.mkdir(parents=True)
    with open(wave_dir / "design_matrix.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["index", "num_days", "start_date"])
        for i in range(1, n + 1):
            writer.writerow([i, 366, "01-01-2020"])
    for i in range(1, n + 1):
        if i in missing:
            if i in partial:
                (runs / f"run_index_{i}").mkdir()  # dir exists, no sentinel
            continue
        run_dir = runs / f"run_index_{i}"
        run_dir.mkdir()
        (run_dir / "overall_simulation_output.csv").write_text("ok\n")
    return str(wave_dir)


def test_resubmit_missing_ranges(tmp_path):
    wave_dir = make_fake_wave(tmp_path)
    missing = resubmit_missing.missing_indices(wave_dir)
    assert missing == [3, 5, 6, 7, 12]
    assert resubmit_missing.contiguous_ranges(missing) == [(3, 3), (5, 7), (12, 12)]
    commands = resubmit_missing.resubmit_commands(wave_dir, missing)
    assert commands == [
        "qsub -t 3-3 fake_array.sh",
        "qsub -t 5-7 fake_array.sh",
        "qsub -t 12-12 fake_array.sh",
    ]
    # SGE -t takes only n[-m[:s]] — comma lists are Torque/SLURM syntax
    assert not any("," in cmd for cmd in commands)


def test_resubmit_missing_deletes_partials_with_yes(tmp_path, capsys):
    wave_dir = make_fake_wave(tmp_path, partial=(5, 6))
    resubmit_missing.main([wave_dir, "--yes"])
    out = capsys.readouterr().out
    assert not os.path.isdir(os.path.join(wave_dir, "runs", "run_index_5"))
    assert not os.path.isdir(os.path.join(wave_dir, "runs", "run_index_6"))
    assert "qsub -t 5-7 fake_array.sh" in out
    assert "qsub" not in out.split("resubmit with")[0]  # commands printed, never executed
