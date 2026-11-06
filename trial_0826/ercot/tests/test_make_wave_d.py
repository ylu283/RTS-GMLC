"""Prompt 58 T2 tests for tools/make_wave_d.py (wave D location_oat_v2).

Run:  cd trial_0826/ercot && python -m pytest tests/test_make_wave_d.py -q

Checks: 21 rows in the pinned order, fractions = pem_mw / nameplate (<= 1),
the <= 185.4 assert fires at 186, nuclear dict has no gen_pmax key, the
array script refuses without GAP_DECISION.json (bash -n + a dry call with a
missing file) and reads the identity from it when present, submit_this.sh
refuses without GAP_DECISION.json, .gitignore line present.
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
import make_wave_d as mw  # noqa: E402

WAVE = ERCOT / "waves" / "location_oat_v2"
HAVE_DATA = (ERCOT / mw.V2_DATA_REL / "gen.csv").is_file()
pytestmark = pytest.mark.skipif(not HAVE_DATA, reason="v2 data dir not on disk")

NAMEPLATE = {"163": 185.4, "140": 250.6, "146": 268.0, "270": 579.0, "110": 338.6, "274": 746.4}
BUS = {"163": 120, "140": 2, "146": 75, "270": 120, "110": 2, "274": 120}


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    waves = tmp_path_factory.mktemp("waves")
    d, rows = mw.build(waves=waves)
    return d, rows


def test_row_count_and_pinned_order(built):
    d, rows = built
    assert len(rows) == 21
    dm = pd.read_csv(d / "design_matrix.csv", dtype={"oat_site": str, "replicate_of": str})
    assert list(dm.columns) == ["index", "oat_site", "unit_type", "bus", "omega", "bid", "gen_pmax",
                                "start_date", "num_days", "replicate_of", "pem_mw", "level_id"]
    assert list(dm["index"]) == list(range(1, 22))
    exp_sites = [s for s in mw.SITES for _ in mw.LEVELS_MW] + ["1"] * 3
    assert list(dm["oat_site"]) == exp_sites
    assert list(dm["pem_mw"]) == [60.0, 120.0, 180.0] * 7
    assert list(dm["level_id"]) == ["L60", "L120", "L180"] * 7
    assert (dm["unit_type"].iloc[:18] == "WIND").all() and (dm["unit_type"].iloc[18:] == "NUC").all()
    assert (dm["bid"] == 40.0).all() and (dm["num_days"] == 365).all()
    assert (dm["start_date"] == "01-01-2019").all()
    assert dm["replicate_of"].isna().all()
    for s, b in BUS.items():
        assert (dm.loc[dm["oat_site"] == s, "bus"] == b).all()
    assert (dm.loc[dm["oat_site"] == "1", "bus"] == 107).all()


def test_fractions(built):
    d, rows = built
    dm = pd.read_csv(d / "design_matrix.csv", dtype={"oat_site": str})
    assert (dm["omega"] <= 1.0).all()
    for _, r in dm.iterrows():
        assert r["omega"] == pytest.approx(r["pem_mw"] / r["gen_pmax"], rel=1e-12)
        assert r["omega"] * r["gen_pmax"] == pytest.approx(r["pem_mw"], abs=1e-9)
    for s, p in NAMEPLATE.items():
        assert dm.loc[dm["oat_site"] == s, "gen_pmax"].iloc[0] == pytest.approx(p, abs=0.05)
    s163 = dm[dm["oat_site"] == "163"]["omega"].tolist()
    assert s163 == pytest.approx([0.3236, 0.6472, 0.9709], abs=5e-5)
    nuc = dm[dm["oat_site"] == "1"]
    assert (nuc["gen_pmax"] == 2430.0).all()
    assert nuc["omega"].tolist() == pytest.approx([60 / 2430, 120 / 2430, 180 / 2430], rel=1e-12)
    assert nuc["omega"].tolist() == pytest.approx([0.02469, 0.04938, 0.07407], abs=5e-6)


def test_max_level_assert_fires_at_186(tmp_path):
    with pytest.raises(AssertionError, match="min chosen nameplate"):
        mw.design_rows(levels=[60.0, 120.0, 186.0])
    # 185 passes the nameplate assert (185 <= 185.39998)
    rows = mw.design_rows(levels=[60.0, 120.0, 185.0])
    assert len(rows) == 21 and max(r["omega"] for r in rows) <= 1.0


def test_retrofit_dicts(built):
    d, rows = built
    for r in rows:
        dct = json.loads((d / f"retrofit_gen_dict_{r['index']}.json").read_text())
        assert list(dct) == [r["oat_site"]]
        v = dct[r["oat_site"]]
        assert v["PEM_bid"] == 40.0
        assert v["PEM_fraction"] == pytest.approx(r["pem_mw"] / r["gen_pmax"], rel=1e-12)
        if r["unit_type"] == "NUC":
            assert "gen_pmax" not in v, "nuclear dict must not carry gen_pmax (selection_t1_v2 convention)"
            assert set(v) == {"PEM_bid", "PEM_fraction"}
        else:
            assert v["gen_pmax"] == pytest.approx(r["gen_pmax"])
            assert set(v) == {"PEM_bid", "PEM_fraction", "gen_pmax"}
    # the nuclear dict has the shape of waves/selection_t1_v2/retrofit_gen_dict_6.json
    ref = json.loads((ERCOT / "waves" / "selection_t1_v2" / "retrofit_gen_dict_6.json").read_text())
    nuc = json.loads((d / "retrofit_gen_dict_19.json").read_text())
    assert set(ref) == set(nuc) == {"1"} and set(ref["1"]) == set(nuc["1"])


def _bash_n(path):
    subprocess.run(["bash", "-n", str(path)], check=True)


def test_scripts_parse(built):
    d, _ = built
    for f in ("location_oat_v2_array.sh", "collect_location_oat_v2.sh", "submit_this.sh"):
        _bash_n(d / f)
    arr = (d / "location_oat_v2_array.sh").read_text()
    assert "#$ -t 1-21" in arr and "#$ -pe smp 4" in arr and "#$ -r n" in arr and "#$ -q long" in arr
    assert "SMOKE_PASS" in arr and "GAP_DECISION.json" in arr
    assert '--ruc_mipgap "$RUC_MIPGAP"' in arr and '--ruc_time_limit "$RUC_TIME_LIMIT"' in arr
    assert "WAVE_D_START" in arr and "WAVE_D_END" in arr
    coll = (d / "collect_location_oat_v2.sh").read_text()
    assert "--full" in coll and "pool_objectives.py" in coll and "--run-dir" in coll
    assert "runtimes.csv" in coll and r"\.csv\.gz$" in coll
    sub = (d / "submit_this.sh").read_text()
    assert "GAP_DECISION.json" in sub and 'cat "$W/GAP_DECISION.json"' in sub and "SMOKE_PASS" in sub


def _gap_block(d):
    """The GAP_DECISION block of the array script as a standalone bash snippet
    (HEADER vars provided; no conda/module/qsub)."""
    arr = (d / "location_oat_v2_array.sh").read_text()
    start = arr.index("# --- identity from waves/GAP_DECISION.json")
    end = arr.index('eval "$(python')
    return arr[start:end]


def test_array_refuses_without_gap_decision(built, tmp_path):
    d, _ = built
    ercot = tmp_path / "ercot"
    (ercot / "waves").mkdir(parents=True)
    wave = tmp_path / "wave"
    wave.mkdir()
    script = (f'set -euo pipefail\nERCOT_DIR="{ercot}"\nWAVE_DIR="{wave}"\nSGE_TASK_ID=7\n'
              + _gap_block(d) + 'echo "REACHED_RUN"\n')
    r = subprocess.run(["bash", "-c", script], capture_output=True, text=True)
    assert r.returncode != 0 and "ABORT task 7" in r.stdout and "REACHED_RUN" not in r.stdout
    assert (wave / "FAILED_task_7_no_gap_decision.md").is_file()
    # with the file present the identity is read and printed
    (ercot / "waves" / "GAP_DECISION.json").write_text(json.dumps(
        {"ruc_mipgap": 0.001, "ruc_time_limit": 1200, "decided_by": "Kay",
         "date": "2026-11-07", "evidence": "extracts/smoke_gap"}))
    r = subprocess.run(["bash", "-c", script + 'echo "GAP=$RUC_MIPGAP TL=$RUC_TIME_LIMIT"\n'],
                       capture_output=True, text=True, env={**os.environ, "PATH": os.environ["PATH"]})
    assert r.returncode == 0, r.stdout + r.stderr
    assert "REACHED_RUN" in r.stdout and "GAP=0.001 TL=1200.0" in r.stdout
    assert "IDENTITY from GAP_DECISION.json: ruc_mipgap=0.001 ruc_time_limit=1200.0" in r.stdout


def test_submit_refuses_without_gap_decision(built, tmp_path):
    d, _ = built
    sub = (d / "submit_this.sh").read_text()
    # run the pre-flight only: stop before the git pull by faking git/qsub on PATH
    fake = tmp_path / "bin"
    fake.mkdir()
    (fake / "git").write_text('#!/bin/bash\ncase "$*" in *"branch --show-current"*) echo ercot/tx123;; *) exit 0;; esac\n')
    (fake / "git").chmod(0o755)
    (fake / "qsub").write_text('#!/bin/bash\necho "qsub must not run"; exit 99\n')
    (fake / "qsub").chmod(0o755)
    layout = tmp_path / "repo" / "trial_0826" / "ercot" / "waves" / "location_oat_v2"
    layout.mkdir(parents=True)
    (layout / "submit_this.sh").write_text(sub)
    r = subprocess.run(["bash", str(layout / "submit_this.sh")], capture_output=True, text=True,
                       env={**os.environ, "PATH": f"{fake}:{os.environ['PATH']}"}, input="no\n")
    assert r.returncode != 0 and "GAP_DECISION.json absent" in r.stdout, r.stdout + r.stderr
    assert "qsub must not run" not in r.stdout


def test_gitignore_line_present():
    gi = (ERCOT / ".gitignore").read_text()
    assert "extracts/location_oat_v2/**/*.csv.gz" in gi


def test_committed_wave_matches_builder(built):
    """waves/location_oat_v2 on disk == a fresh build (design matrix + dicts)."""
    d, _ = built
    if not (WAVE / "design_matrix.csv").is_file():
        pytest.skip("wave not built in the tree")
    assert (WAVE / "design_matrix.csv").read_text() == (d / "design_matrix.csv").read_text()
    for i in range(1, 22):
        assert ((WAVE / f"retrofit_gen_dict_{i}.json").read_text()
                == (d / f"retrofit_gen_dict_{i}.json").read_text())
