"""Pair-grid waves (prompt 28 T1): pair enumeration, 81-row grid structure,
exact lattice membership, derived bids, manifest pair identity, no -tc,
per-wave support scripts, and the make_batches.py `all` refusal."""

import json
import os
import stat

import numpy as np
import pandas as pd
import pytest

import make_batches
import submit_array
from tiers import STAGE2_LATTICE, TIERS

LATTICE = [float(w) for w in STAGE2_LATTICE]
SORTED_TIERS = sorted(TIERS)


@pytest.fixture(scope="session")
def pairgrid_wave(waves_root):
    wave_dir = make_batches.build_pairgrid("nuclear", "wind_317",
                                           waves_root=waves_root)
    name = os.path.basename(wave_dir)
    submit_array.generate_script(
        wave_dir, max_concurrent=make_batches.WAVE_MAX_CONCURRENT[name])
    return wave_dir


def test_pair_enumeration():
    pairs = make_batches.PAIRGRID_PAIRS
    assert len(pairs) == 14
    assert ("wind_303", "wind_317") not in pairs  # exists as contour_303x317_C
    for a, b in pairs:
        assert (a, b) == tuple(sorted((a, b))), f"unsorted pair ({a}, {b})"
        assert a in TIERS and b in TIERS
    # all 15 combinations minus the wind pair, each exactly once
    all_pairs = {(a, b) for i, a in enumerate(SORTED_TIERS)
                 for b in SORTED_TIERS[i + 1:]}
    assert set(pairs) == all_pairs - {("wind_303", "wind_317")}
    assert len(set(pairs)) == 14


def test_unsorted_pair_refused(waves_root):
    with pytest.raises(AssertionError, match="sorted tier order"):
        make_batches.build_pairgrid("wind_317", "nuclear", waves_root=waves_root)


def test_pairgrid_design_matrix(pairgrid_wave):
    df = pd.read_csv(os.path.join(pairgrid_wave, "design_matrix.csv"))
    assert list(df["index"]) == list(range(1, 82))
    assert (df["num_days"] == 366).all()
    assert (df["rho_h2"] == 2.0).all()

    om = df[[c for c in df.columns if c.endswith("_omega")]]
    pair_cols = ["nuclear_omega", "wind_317_omega"]
    other_cols = [c for c in om.columns if c not in pair_cols]
    # pair-only non-absent; other four tiers absent on every row
    assert om[pair_cols].notna().all().all()
    assert om[other_cols].isna().all().all()
    # exact lattice membership (decimal-clean STAGE2_LATTICE, no ulp slop)
    for col in pair_cols:
        assert om[col].isin(LATTICE).all(), f"{col} off-lattice"
    # 81 distinct rows = the full 9x9 product, row-major, sorted-first outer
    assert len(om[pair_cols].drop_duplicates()) == 81
    expect_outer = np.repeat(LATTICE, 9)
    expect_inner = np.tile(LATTICE, 9)
    assert np.array_equal(om["nuclear_omega"].to_numpy(), expect_outer)
    assert np.array_equal(om["wind_317_omega"].to_numpy(), expect_inner)

    # bids all 40 (derived, scenario C) on the pair; NaN elsewhere
    bids = df[[c for c in df.columns if c.endswith("_bid")]]
    assert (bids[["nuclear_bid", "wind_317_bid"]] == 40.0).all().all()
    assert bids[[c for c in bids.columns
                 if c not in ("nuclear_bid", "wind_317_bid")]].isna().all().all()


def test_pairgrid_retrofit_dicts(pairgrid_wave):
    df = pd.read_csv(os.path.join(pairgrid_wave, "design_matrix.csv"))
    d1 = json.load(open(os.path.join(pairgrid_wave, "retrofit_gen_dict_1.json")))
    assert set(d1) == {"121_NUCLEAR_1", "317_WIND_1"}
    assert all(entry["PEM_bid"] == 40.0 for entry in d1.values())
    assert "gen_pmax" not in d1["121_NUCLEAR_1"]      # thermal: no pmax entry
    assert d1["317_WIND_1"]["gen_pmax"] == 799.1
    # row 81 = both tiers at omega 1.0 (nuclear above the old 0.5 cap)
    d81 = json.load(open(os.path.join(pairgrid_wave, "retrofit_gen_dict_81.json")))
    assert d81["121_NUCLEAR_1"]["PEM_fraction"] == 1.0
    assert float(df.loc[80, "nuclear_omega"]) == 1.0


def test_pairgrid_manifest(pairgrid_wave):
    manifest = json.load(open(os.path.join(pairgrid_wave, "manifest.json")))
    assert manifest["pair"] == ["nuclear", "wind_317"]  # the authority on identity
    assert manifest["lattice"] == LATTICE
    assert manifest["sobol"] is None                     # pair never rides in sobol
    assert list(manifest["tiers"]["nuclear"]["omega"]) == [0.05, 1.0]
    assert manifest["n_rows"] == 81


def test_pairgrid_array_script_no_tc(pairgrid_wave):
    name = os.path.basename(pairgrid_wave)
    text = open(os.path.join(pairgrid_wave, f"{name}_array.sh")).read()
    assert "#$ -t 1-81" in text
    assert "-tc" not in text                             # fully concurrent
    assert "#$ -cwd" in text and "set -euo pipefail" in text
    assert "/Users/" not in text


def test_generate_script_none_vs_capped(tmp_path, tiers):
    import design_tools as dt
    rows = [dt.make_row(tiers, {"nuclear": (0.1, 20.0)}, index=1)]
    wave_dir = tmp_path / "tcprobe"
    wave_dir.mkdir()
    dt.rows_to_matrix(rows, tiers).to_csv(wave_dir / "design_matrix.csv", index=False)
    text = open(submit_array.generate_script(str(wave_dir), max_concurrent=None)).read()
    assert "-tc" not in text
    text = open(submit_array.generate_script(str(wave_dir), max_concurrent=7)).read()
    assert "#$ -tc 7" in text                            # legacy path untouched


def test_pairgrid_support_files(pairgrid_wave):
    name = os.path.basename(pairgrid_wave)
    readme = open(os.path.join(pairgrid_wave, "README.md")).read()
    for phrase in ("nuclear", "wind_317", "ABSENT", "manifest.json"):
        assert phrase in readme

    submit_path = os.path.join(pairgrid_wave, "submit_this.sh")
    submit = open(submit_path).read()
    assert os.stat(submit_path).st_mode & stat.S_IXUSR
    assert 'qsub -terse -t 1-81' in submit and "cut -d. -f1" in submit
    assert '[[ "$J" =~ ^[0-9]+$ ]]' in submit
    assert f'qsub -hold_jid "$J" -cwd -M ylu28@nd.edu -m ea collect_{name}.sh' in submit
    assert '== "d6"' in submit and "pull --rebase --autostash" in submit
    assert "qstat -u ylu28" in submit

    collect_path = os.path.join(pairgrid_wave, f"collect_{name}.sh")
    collect = open(collect_path).read()
    assert os.stat(collect_path).st_mode & stat.S_IXUSR
    assert 'user.name="pairgrid-bot"' in collect
    assert f"pairgrid-bot: {name} results" in collect
    assert "for attempt in 1 2 3 4 5" in collect         # retry LOOP, not once
    assert "sleep $((30 + RANDOM % 60))" in collect
    assert "resubmit_missing.py (interactive)" in collect
    assert f"FAILED_{name}.md" in collect
    # single-wave: commits its own wave's CSVs only
    assert '"$WAVE_DIR/objectives.csv" "$WAVE_DIR/site_detail.csv"' in collect


def test_wave_max_concurrent_entries():
    for a, b in make_batches.PAIRGRID_PAIRS:
        assert make_batches.WAVE_MAX_CONCURRENT[make_batches.pairgrid_wave_name(a, b)] is None
    # legacy entries and fallback untouched
    assert make_batches.WAVE_MAX_CONCURRENT["stage2_C_n0"] == 12
    assert make_batches.WAVE_MAX_CONCURRENT["stage2_backfill_C"] == 12
    assert make_batches.WAVE_MAX_CONCURRENT.get("pilot", 20) == 20


def test_main_refuses_all_and_default():
    with pytest.raises(SystemExit, match="REFUSED"):
        make_batches.main(["all"])
    with pytest.raises(SystemExit, match="REFUSED"):
        make_batches.main([])
