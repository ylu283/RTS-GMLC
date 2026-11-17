"""Prompt 62 Part C tests for tools/make_screening_v3.py (+ the make_wave_d refactor guard).

Run (same process as the wave-D tests, prompt 62 §4.3):
  cd trial_0826/ercot && /opt/anaconda3/bin/python -m pytest tests/test_make_wave_d.py tests/test_make_screening_v3.py -q
"""
import json
import subprocess
import sys
from pathlib import Path

import pandas as pd
import pytest

ERCOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ERCOT / "tools"))
sys.path.insert(0, str(ERCOT))
import make_screening_v3 as ms  # noqa: E402
import make_wave_d as mw  # noqa: E402
import pool_objectives as po  # noqa: E402

WAVE = ERCOT / "waves" / "screening_v3"
HAVE_DATA = (ERCOT / mw.V2_DATA_REL / "gen.csv").is_file()
pytestmark = pytest.mark.skipif(not HAVE_DATA, reason="v2 data dir not on disk")
RANK_7_16 = ["275", "116", "59", "30", "142", "91", "205", "206", "204", "20"]   # cross-check only
SCRIPTS = ("screening_v3_array.sh", "collect_screening_v3.sh", "submit_this.sh")


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    waves = tmp_path_factory.mktemp("waves")
    d, rows, cov = ms.build(waves=waves)
    return d, rows, cov


def test_rows_from_selection_file(built):
    d, rows, _ = built
    assert len(rows) == 11
    sel = json.load(open(ms.SELECTION))["ranked"]
    by = {r["rank"]: r for r in sel}
    assert [r["oat_site"] for r in rows[:10]] == [str(by[k]["site"]) for k in range(7, 17)] == RANK_7_16
    for r, k in zip(rows[:10], range(7, 17)):
        assert r["bus"] == by[k]["bus"] and r["unit_type"] == by[k]["unit_type"]
        assert r["gen_pmax"] == pytest.approx(by[k]["gen_pmax"], abs=1e-6)
    dm = pd.read_csv(d / "design_matrix.csv", dtype={"oat_site": str, "replicate_of": str})
    assert list(dm.columns) == mw.COLS and list(dm["index"]) == list(range(1, 12))
    assert (dm["level_id"] == "L180").all() and (dm["bid"] == 40.0).all() and (dm["pem_mw"] == 180.0).all()
    assert set(dm["unit_type"]) <= {"WIND", "PV"} and "NUC" not in set(dm["unit_type"])
    assert (dm["omega"] <= 1.0).all()
    assert dm["replicate_of"].iloc[:10].isna().all() and dm["replicate_of"].iloc[10] == "location_oat_v2:3"


def test_pem_mw_matches_reader(built):
    d, rows, _ = built
    for r in rows:
        drow = po.design_row(ms.WAVE, r["index"], str(d.parent))
        assert po.pem_mw(ms.WAVE, r["index"], drow, str(d.parent)) == pytest.approx(r["pem_mw"], abs=1e-9)


def test_replicate_row_equals_wave_d_row_3(built):
    d, _, _ = built
    new = (d / "design_matrix.csv").read_text().splitlines()[11].split(",")
    old = (ERCOT / "waves" / "location_oat_v2" / "design_matrix.csv").read_text().splitlines()[3].split(",")
    assert new[0] == "11" and old[0] == "3"
    assert new[1:9] == old[1:9] and new[10:] == old[10:]          # all but index and replicate_of
    assert (d / "retrofit_gen_dict_11.json").read_text() == (
        ERCOT / "waves" / "location_oat_v2" / "retrofit_gen_dict_3.json").read_text()


def test_retrofit_dicts(built):
    d, rows, _ = built
    for r in rows:
        v = json.loads((d / f"retrofit_gen_dict_{r['index']}.json").read_text())
        assert list(v) == [r["oat_site"]]
        assert set(v[r["oat_site"]]) == {"PEM_bid", "PEM_fraction", "gen_pmax"}   # WIND and PV alike


def test_scripts(built):
    d, _, _ = built
    for f in SCRIPTS:
        subprocess.run(["bash", "-n", str(d / f)], check=True)
        t = (d / f).read_text()
        assert "wave D" not in t and "location_oat_v2" not in t and "WAVE_D_" not in t and "Prompt 58" not in t, f
        assert "nuclear" not in t.lower(), f
    arr = (d / "screening_v3_array.sh").read_text()
    assert "#$ -t 1-11" in arr and "#$ -pe smp 4" in arr and "#$ -r n" in arr and "#$ -q long" in arr
    assert "GAP_DECISION.json" in arr and "ABORT task" in arr and "SCREENING_V3_START" in arr
    coll = (d / "collect_screening_v3.sh").read_text()
    assert "--full" in coll and "seq 1 11" in coll and "SCREENING_V3_START" in coll
    sub = (d / "submit_this.sh").read_text()
    assert 'grep -q "screening_v3/\\*\\*/\\*.csv.gz"' in sub and '[[ "$ANS" == "yes" ]]' in sub
    assert "GAP_DECISION.json absent" in sub and "merge-base --is-ancestor" not in sub


def test_gitignore_targets_screening_v3():
    assert "extracts/screening_v3/**/*.csv.gz" in (ERCOT / ".gitignore").read_text()


def test_covariates(built):
    _, _, cov = built
    assert len(cov) == 16 and cov["site"].is_unique
    assert {t: sorted(cov.loc[cov["tier"] == t, "site"]) for t in ms.TIERS} == {t: sorted(s) for t, s in ms.TIERS.items()}
    assert cov["slate"].sum() == 6 and (cov["n_hours_C"] == ms.N_C_HOURS).all()
    assert (cov["H_C_180_MWh"] > 0).all() and (cov["H_C_180_MWh"] <= 180.0 * ms.N_C_HOURS).all()
    pocket = [f"ptdf_{l}" for l in po.pocket_lines(str(ms.DATA), 120)]
    assert set(pocket) <= set(cov.columns)
    b120 = cov[cov["bus"] == 120]
    assert (b120[pocket].nunique() == 1).all()                    # same bus -> identical PTDF column
    assert cov.loc[cov["site"] == "163", "saturation_flag"].item() and cov.loc[cov["site"] == "116", "saturation_flag"].item()
    assert cov.loc[cov["site"] == "275", "source_row"].item() == "screening_v3:1"
    assert cov.loc[cov["site"] == "163", "source_row"].item() == "location_oat_v2:3"


def test_ptdf_distributed_slack_sums():
    P, w = ms.ptdf_distributed()
    assert abs(w.sum() - 1) < 1e-12
    assert abs(P.to_numpy() @ w).max() < 1e-9                      # load-weighted injection -> zero flow


def test_readme_carries_section_4_4_verbatim(built):
    d, _, _ = built
    t = (d / "README.md").read_text()
    assert ms.SECTION_4_4_4_5 in t and "Wave commit — STOP — Kay action" in t and "HL/B_j" in t
    d2, _, _ = ms.build(waves=d.parent.parent / "again")
    assert (d2 / "README.md").read_text() == t                     # deterministic


def test_committed_screening_v3_matches_builder(built):
    d, _, _ = built
    if not (WAVE / "design_matrix.csv").is_file():
        pytest.skip("wave not built in the tree")
    for f in sorted(p.name for p in d.iterdir()):
        assert (WAVE / f).read_bytes() == (d / f).read_bytes(), f


def test_wave_d_refactor_is_default_preserving(tmp_path):
    """Committed waves/location_oat_v2 == a fresh default build, EVERY file (scripts + README too)."""
    d, rows = mw.build(waves=tmp_path)
    committed = ERCOT / "waves" / "location_oat_v2"
    built = sorted(p.name for p in d.iterdir())
    assert len(built) == 26 and len(rows) == 21
    for f in built:
        assert (committed / f).read_bytes() == (d / f).read_bytes(), f
