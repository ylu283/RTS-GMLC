"""Tests for tools/make_base_v3.py (waves/base_v3: the identity-v3 base run).

Run:  cd trial_0826/ercot && python -m pytest tests/test_make_base_v3.py -q

Checks: exactly one row (base token, full year, empty replicate_of), the
retrofit dict is {}, get_row.py reads the row, the array script reads the
identity from GAP_DECISION.json and refuses without it (bash -n + a dry call
with a missing file), submit_this.sh refuses without GAP_DECISION.json and
refuses a non-v3 decision, .gitignore line present, committed wave == fresh
build.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

import pandas as pd
import pytest

ERCOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ERCOT / "tools"))
import make_base_v3 as mb  # noqa: E402

WAVE = ERCOT / "waves" / "base_v3"
SCRIPTS = ("base_v3_array.sh", "collect_base_v3.sh", "submit_this.sh")


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    waves = tmp_path_factory.mktemp("waves")
    return mb.build(waves=waves)


def test_one_base_row(built):
    d, rows = built
    assert len(rows) == 1
    dm = pd.read_csv(d / "design_matrix.csv", dtype={"oat_site": str, "replicate_of": str})
    assert list(dm.columns) == mb.COLS
    assert len(dm) == 1 and dm.loc[0, "index"] == 1
    assert dm.loc[0, "oat_site"] == "__BASE_REPLICATE__"
    assert dm.loc[0, "start_date"] == "01-01-2019" and dm.loc[0, "num_days"] == 365
    assert dm["replicate_of"].isna().all()
    for c in ("unit_type", "bus", "omega", "bid", "gen_pmax"):
        assert dm[c].isna().all(), c
    # same schema and same row as the v2 base's row 1 (only the identity differs)
    ref = (ERCOT / "waves" / "base_2019_v2" / "design_matrix.csv").read_text().splitlines()
    assert (d / "design_matrix.csv").read_text().splitlines() == ref[:2]


def test_retrofit_dict_is_empty(built):
    d, rows = built
    assert json.loads((d / "retrofit_gen_dict_1.json").read_text()) == {}
    assert mb.retrofit_dict(rows[0]) == {}
    assert not (d / "retrofit_gen_dict_2.json").exists()


def test_get_row_reads_the_row(built):
    d, _ = built
    r = subprocess.run([sys.executable, str(ERCOT.parent / "campaign" / "get_row.py"), "1",
                        str(d / "design_matrix.csv")], capture_output=True, text=True, check=True)
    assert r.stdout.split() == ["INDEX=1", "NUM_DAYS=365", "START_DATE=01-01-2019"]


def test_scripts_parse(built):
    d, _ = built
    for f in SCRIPTS:
        subprocess.run(["bash", "-n", str(d / f)], check=True)
    arr = (d / "base_v3_array.sh").read_text()
    assert "#$ -t 1-1" in arr and "#$ -pe smp 4" in arr and "#$ -r n" in arr and "#$ -q long" in arr
    assert "SMOKE_PASS" in arr and "GAP_DECISION.json" in arr
    assert '--ruc_mipgap "$RUC_MIPGAP"' in arr and '--ruc_time_limit "$RUC_TIME_LIMIT"' in arr
    assert "BASE_V3_START" in arr and "BASE_V3_END" in arr
    assert "--ruc_mipgap 0.0" not in arr and "--ruc_time_limit 120" not in arr   # never hard-coded
    coll = (d / "collect_base_v3.sh").read_text()
    assert "--full" in coll and "pool_objectives.py" in coll and "--run-dir" in coll
    assert "pool_full_metrics.json" in coll and "runtimes.csv" in coll and "wallclock.csv" in coll
    assert "identity.txt" in coll and "GAP_DECISION_used.json" in coll and r"\.csv\.gz$" in coll
    assert "push_with_retries" in coll and "for attempt in 1 2 3 4 5" in coll
    assert "-M " not in coll   # email flags live on submit_this.sh only
    sub = (d / "submit_this.sh").read_text()
    assert "GAP_DECISION.json" in sub and 'cat "$W/GAP_DECISION.json"' in sub and "SMOKE_PASS" in sub
    assert '"$ANS" == "yes"' in sub and "-m ea collect_base_v3.sh" in sub
    assert "base_v3/\\*\\*/\\*.csv.gz" in sub


def _gap_block(d):
    """The GAP_DECISION block of the array script as a standalone bash snippet
    (HEADER vars provided; no conda/module/qsub)."""
    arr = (d / "base_v3_array.sh").read_text()
    start = arr.index("# --- identity from waves/GAP_DECISION.json")
    end = arr.index('eval "$(python')
    return arr[start:end]


def test_array_block_identical_to_wave_d(built):
    """The run-time identity read is the wave-D block, word for word except the
    wave name in the abort line."""
    d, _ = built
    ref = ERCOT / "waves" / "location_oat_v2" / "location_oat_v2_array.sh"
    if not ref.is_file():
        pytest.skip("wave D not in the tree")
    arr = ref.read_text()
    wd = arr[arr.index("# --- identity from waves/GAP_DECISION.json"):arr.index('eval "$(python')]
    assert _gap_block(d) == wd.replace("wave D runs only", "base_v3 runs only")


def test_array_refuses_without_gap_decision(built, tmp_path):
    d, _ = built
    ercot = tmp_path / "ercot"
    (ercot / "waves").mkdir(parents=True)
    wave = tmp_path / "wave"
    wave.mkdir()
    script = (f'set -euo pipefail\nERCOT_DIR="{ercot}"\nWAVE_DIR="{wave}"\nSGE_TASK_ID=1\n'
              + _gap_block(d) + 'echo "REACHED_RUN"\n')
    r = subprocess.run(["bash", "-c", script], capture_output=True, text=True)
    assert r.returncode != 0 and "ABORT task 1" in r.stdout and "REACHED_RUN" not in r.stdout
    assert (wave / "FAILED_task_1_no_gap_decision.md").is_file()
    # with the file present the identity is read and printed
    (ercot / "waves" / "GAP_DECISION.json").write_text(json.dumps(
        {"ruc_mipgap": 0.001, "ruc_time_limit": 1200, "decided_by": "Kay",
         "date": "2026-11-06", "evidence": "extracts/smoke_gap", "identity": "v3"}))
    r = subprocess.run(["bash", "-c", script + 'echo "GAP=$RUC_MIPGAP TL=$RUC_TIME_LIMIT"\n'],
                       capture_output=True, text=True, env={**os.environ, "PATH": os.environ["PATH"]})
    assert r.returncode == 0, r.stdout + r.stderr
    assert "REACHED_RUN" in r.stdout and "GAP=0.001 TL=1200.0" in r.stdout
    assert "IDENTITY from GAP_DECISION.json: ruc_mipgap=0.001 ruc_time_limit=1200.0" in r.stdout


def _run_submit(tmp_path, sub, gap_json=None):
    """Run submit_this.sh's pre-flight with fake git/qsub on PATH; answer 'no'."""
    fake = tmp_path / "bin"
    fake.mkdir(exist_ok=True)
    (fake / "git").write_text('#!/bin/bash\ncase "$*" in *"branch --show-current"*) echo ercot/tx123;; *) exit 0;; esac\n')
    (fake / "git").chmod(0o755)
    (fake / "qsub").write_text('#!/bin/bash\necho "qsub must not run"; exit 99\n')
    (fake / "qsub").chmod(0o755)
    waves = tmp_path / "repo" / "trial_0826" / "ercot" / "waves"
    layout = waves / "base_v3"
    layout.mkdir(parents=True, exist_ok=True)
    (layout / "submit_this.sh").write_text(sub)
    if gap_json is not None:
        (waves / "GAP_DECISION.json").write_text(json.dumps(gap_json))
    return subprocess.run(["bash", str(layout / "submit_this.sh")], capture_output=True, text=True,
                          env={**os.environ, "PATH": f"{fake}:{os.environ['PATH']}"}, input="no\n")


def test_submit_refuses_without_gap_decision(built, tmp_path):
    d, _ = built
    sub = (d / "submit_this.sh").read_text()
    r = _run_submit(tmp_path, sub)
    assert r.returncode != 0 and "GAP_DECISION.json absent" in r.stdout, r.stdout + r.stderr
    assert "qsub must not run" not in r.stdout


def test_submit_refuses_non_v3_decision(built, tmp_path):
    d, _ = built
    sub = (d / "submit_this.sh").read_text()
    r = _run_submit(tmp_path, sub, {"ruc_mipgap": 0.01, "ruc_time_limit": 120, "identity": "v2"})
    assert r.returncode != 0 and "not identity v3" in r.stdout, r.stdout + r.stderr
    assert "qsub must not run" not in r.stdout


def test_gitignore_line_present():
    gi = (ERCOT / ".gitignore").read_text()
    assert "extracts/base_v3/**/*.csv.gz" in gi


def test_committed_wave_matches_builder(built):
    """waves/base_v3 on disk == a fresh build (every file)."""
    d, _ = built
    if not (WAVE / "design_matrix.csv").is_file():
        pytest.skip("wave not built in the tree")
    for f in ("design_matrix.csv", "retrofit_gen_dict_1.json", "README.md") + SCRIPTS:
        assert (WAVE / f).read_text() == (d / f).read_text(), f
