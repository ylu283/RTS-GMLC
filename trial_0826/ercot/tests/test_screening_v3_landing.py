"""Prompt 62 Part C §4.5 tests for analysis/pool/screening_v3_landing.py.

Run: cd trial_0826/ercot && /opt/anaconda3/bin/python -m pytest tests/test_screening_v3_landing.py -q
"""
import ast
import math
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from scipy import stats

ERCOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ERCOT / "analysis" / "pool"))
sys.path.insert(0, str(ERCOT))
import screening_v3_landing as L  # noqa: E402

HAVE_Y = (ERCOT / "extracts" / "screening_v3" / "run_index_11" / "overall.csv").is_file()
needs_y = pytest.mark.skipif(not HAVE_Y, reason="screening_v3 extracts not on disk")


def test_exact_null_matches_scipy():
    pmf = L.exact_u_null(8, 5)
    assert len(pmf) == 41 and abs(pmf.sum() - 1) < 1e-12 and pmf[0] == pytest.approx(1 / math.comb(13, 5))
    c, u = np.arange(8) + 10.0, np.arange(5) + 0.0               # complete separation
    assert stats.mannwhitneyu(c, u, method="exact").pvalue == pytest.approx(2 * pmf[0])


def test_moses_interval_coverage_and_hl():
    k, cov = L.moses_k(8, 5)
    F = np.cumsum(L.exact_u_null(8, 5))
    assert F[k - 2] <= 0.025 < F[k - 1] and cov >= 0.95
    rng = np.random.default_rng(0)
    c, u = rng.normal(3, 1, 8), rng.normal(0, 1, 5)
    r = L.hl_read(c, u)
    d = np.sort((c[:, None] - u[None, :]).ravel())
    assert r["HL"] == pytest.approx(np.median(d)) and r["lo"] == d[k - 1] and r["hi"] == d[40 - k]
    assert r["r_rb"] == pytest.approx(2 * r["U"] / 40 - 1)


def test_holm():
    p = [0.01, 0.04, 0.03, 0.5]
    assert np.allclose(L.holm(p), [0.04, 0.09, 0.09, 0.5])
    assert np.allclose(L.holm([0.001554] * 3), [0.004662] * 3)


def test_locational_verdict_needs_all_three():
    B = 1.0
    ok = {"p_holm": 0.01, "HL": -3.0, "lo": -4.0, "hi": -2.0}
    assert L.locational_verdict(ok, B)[0] == "LOCATIONAL"
    assert L.locational_verdict({**ok, "p_holm": 0.06}, B)[0] == "NOT LOCATIONAL"
    assert L.locational_verdict({**ok, "HL": -1.9}, B)[0] == "NOT LOCATIONAL"
    assert L.locational_verdict({**ok, "hi": 0.0}, B)[0] == "NOT LOCATIONAL"


def test_dominance_and_margin():
    z = pd.DataFrame({"V1": [-10, -5, -12], "E1": [1, 2, 0.5]}, index=["t", "s1", "s2"])
    d = L.dominance(z, ["t"], ["s1", "s2"], ("V1", "E1")).set_index("site")
    assert d.loc["s1", "dominated"] and d.loc["s1", "dominated_by"] == "t"
    assert not d.loc["s2", "dominated"] and d.loc["s2", "margin_bars"] == pytest.approx(2.0)


def test_ranking_ties():
    cov = pd.DataFrame({"rank_v2": range(1, 9), "relief_per_mw_v2": 0.0, "bus": 120, "unit_type": "WIND",
                        "omega_180": 0.5, "tier": "far", "slate": False}, index=list("abcdefgh"))
    rel = pd.Series([100, 90, 80, 70, 60, 50, 45, 10.0], index=list("abcdefgh"))
    tab = L.ranking(rel, cov, band=6.0)
    assert list(tab.index[tab["top6_v3"]]) == list("abcdef")
    assert tab.loc["f", "TIED"] and tab.loc["g", "TIED"] and not tab.loc["h", "TIED"] and not tab.loc["e", "TIED"]


def test_source_never_reads_random_or_gp_loader_load():
    tree = ast.parse((ERCOT / "analysis" / "pool" / "screening_v3_landing.py").read_text())
    src = (ERCOT / "analysis" / "pool" / "screening_v3_landing.py").read_text()
    assert "land_ercot_n0" not in src and "ercot_gp_loader import load" not in src
    for n in ast.walk(tree):
        if isinstance(n, ast.Constant) and isinstance(n.value, str) and "random_E" in n.value:
            assert "Not read" in n.value or "never" in n.value, n.value


@needs_y
def test_committed_outputs_reproduce(tmp_path):
    figs = tmp_path / "figs"
    L.run(out_dir=str(tmp_path), figs_dir=str(figs), make_figs=False, append=False)
    for f in ("screening_v3_sites.csv", "screening_v3_locational.csv", "screening_v3_covariate_rho.csv",
              "screening_v3_ranking.csv", "screening_v3_dominance.csv"):
        a = pd.read_csv(tmp_path / f)
        b = pd.read_csv(ERCOT / "analysis" / "pool" / f)
        pd.testing.assert_frame_equal(a, b, check_exact=False, rtol=1e-12)


@needs_y
def test_landing_reads(tmp_path):
    sites, loc, crho, rk, dom, info, B = L.compute()
    assert len(sites) == 16 and info["n_suspect"] == 0 and len(loc) == 23 and "D2" not in set(loc["id"])
    assert info["replicate"]["new"] == "screening_v3:11"
    assert set(sites.index[sites["slate"].astype(bool)]) == set(L.SLATE)
    assert info["rank"]["band"] == pytest.approx(B.loc["V1", "B_j"] / 180)


def test_part_c_append_is_idempotent(tmp_path):
    md = tmp_path / "S.md"
    md.write_text("# x\n\n## E. table\n\nrow\n\n## Deviations\n\n- d\n")
    csv = tmp_path / "c.csv"
    pd.DataFrame({"id": ["V1", "E5"], "status": ["OBJECTIVE", "DEAD"]}).to_csv(csv, index=False)
    loc = pd.DataFrame({"id": ["V1", "E1", "N1", "N4"], "HL_over_B": [-33.1, -8.7, -3.0, -2.7],
                        "p_holm": [0.0357, 0.0357, 0.65, 0.047], "B_seed": [1.0] * 4, "HL_over_B_seed": [-30, -9, -1.4, -2.2],
                        "verdict": ["LOCATIONAL", "LOCATIONAL", "NOT LOCATIONAL", "LOCATIONAL"],
                        "verdict_B_seed": ["LOCATIONAL", "LOCATIONAL", "NOT LOCATIONAL", "LOCATIONAL"]})
    rinfo = {"top6": ["270"], "bus_set_holds": True, "entered": ["275"], "left": ["163"], "tied_sites": []}
    dom = pd.DataFrame({"objectives": ["V1/E1/N1", "V1/E1/N4"], "site": ["116", "116"], "dominated": [False, True]})
    L.append_part_c(loc, rinfo, dom, {}, md_path=md, csv_path=csv)
    once = md.read_text(), csv.read_text()
    L.append_part_c(loc, rinfo, dom, {}, md_path=md, csv_path=csv)
    assert (md.read_text(), csv.read_text()) == once
    t = once[0]
    assert t.index(L.BEGIN) < t.index("## Deviations") and t.count(L.BEGIN) == 1
    c = pd.read_csv(csv, keep_default_na=False)
    assert list(c["C_locational"]) == ["LOCATIONAL", "n/a"] and list(c["status"]) == ["OBJECTIVE", "DEAD"]
