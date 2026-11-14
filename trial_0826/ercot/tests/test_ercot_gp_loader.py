"""Prompt 54 Part A tests for analysis/ercot_gp/ercot_gp_loader.py (contract 53-55 §6.1).

Run in bogp-botorch, by file name (contract §1 env note):
    cd trial_0826/ercot && /opt/anaconda3/envs/bogp-botorch/bin/python -m pytest tests/test_ercot_gp_loader.py -q

Blocks: (1) wave D's 18 WIND rows (rows 19-21 NUC refused); (2) noise_v3 A's
site-146 rows (sites 1 / 206 / 275 refused); (3) not-v3 / not-collected
refusals on a scratch copy; (4) multi-site `__ALL__` X / U / meta on a
synthetic design matrix (contract §5); (5) the design-space JSON.
"""
import json
import os
import shutil
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ERCOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ERCOT))
import pool_objectives as po  # noqa: E402
from analysis.ercot_gp import ercot_gp_loader as L  # noqa: E402

pytestmark = pytest.mark.filterwarnings("ignore:Downcasting object dtype arrays:FutureWarning")

# contract 53-55 §3 minus the four prose keys (guardrails, objective_rule, suspect,
# objective_source) the loader never reads; the file itself is prompt 53's
DESIGN_SPACE = {
    "contract_version": "2026-11-13", "identity": "v3",
    "slate_rule": "E-D3 fallback = wave-D top-6 (analysis/cost_fix/WAVE_D_TOPK_RULE.md); 32 T2 never bought",
    "sites": [
        {"site": "110", "unit_type": "WIND", "bus": 2, "gen_pmax": 338.599998942999},
        {"site": "140", "unit_type": "WIND", "bus": 2, "gen_pmax": 250.5999989428539},
        {"site": "146", "unit_type": "WIND", "bus": 75, "gen_pmax": 267.9999991911224},
        {"site": "163", "unit_type": "WIND", "bus": 120, "gen_pmax": 185.3999876467921},
        {"site": "270", "unit_type": "WIND", "bus": 120, "gen_pmax": 578.9999877407346},
        {"site": "274", "unit_type": "WIND", "bus": 120, "gen_pmax": 746.3999877635443}],
    "x_columns": ["mw_110", "mw_140", "mw_146", "mw_163", "mw_270", "mw_274"],
    "bounds_mw_lo": [0, 0, 0, 0, 0, 0],
    "bounds_mw_hi": [338.599998942999, 250.5999989428539, 267.9999991911224,
                     185.3999876467921, 578.9999877407346, 746.3999877635443],
    "u": "u_s = mw_s / gen_pmax_s in [0, 1]; the GP and acquisition input (plan §2); mw = 0 means site absent",
    "bid": 40.0,
    "tiers": {"nav": "E-D7 (32 or 48), decided after 54 Part B", "grading": 48, "holdout": 48},
    "objectives": {
        "V1": {"seat": "V", "status": "RECOMMENDED (E-D1b provisional standings, pi-agenda 11-07)"},
        "E1": {"seat": "E", "status": "PENDING plan §1.2 verdict from prompt 52 (READABLE -> E1 total_cost; else E3 var_cost)"},
        "R4": {"seat": "R", "status": "PROVISIONAL (E-D1b, PI)"},
        "N1": {"seat": "N", "status": "PROVISIONAL (E-D1b, PI)"}},
}
COLS = DESIGN_SPACE["x_columns"]
PMAX = pd.Series(DESIGN_SPACE["bounds_mw_hi"], index=COLS)
HAVE_D = (ERCOT / "extracts" / "location_oat_v2" / "run_index_18" / "overall.csv").is_file()
HAVE_N = (ERCOT / "extracts" / "noise_v3" / "A" / "run_index_3" / "overall.csv").is_file()


@pytest.fixture(scope="module")
def ds_path(tmp_path_factory):
    p = tmp_path_factory.mktemp("ds") / "design_space_E.json"
    p.write_text(json.dumps(DESIGN_SPACE))
    return str(p)


@pytest.fixture(scope="module")
def wave_d(ds_path):
    return L.load(["location_oat_v2"], design_space=ds_path, floors={"V1": 0.0})


# --------------------------------------------------------------------------
# (1) wave D
# --------------------------------------------------------------------------
@pytest.mark.skipif(not HAVE_D, reason="wave-D extracts not on disk")
def test_wave_d_18_wind_rows_nuc_refused(wave_d):
    X, U, Y, meta = wave_d
    keys = [f"location_oat_v2:{i}" for i in range(1, 19)]
    assert list(X.index) == keys and list(U.index) == keys
    assert list(Y.index) == keys and list(meta.index) == keys
    assert meta.attrs["refused"]["site_not_in_space"] == [f"location_oat_v2:{i}" for i in (19, 20, 21)]
    assert meta.attrs["refused"]["not_v3"] == [] and meta.attrs["refused"]["no_overall"] == []
    assert meta.attrs["n_refused"] == 3
    assert meta.attrs["floors"] == {"V1": 0.0}


@pytest.mark.skipif(not HAVE_D, reason="wave-D extracts not on disk")
def test_wave_d_one_site_mapping(wave_d):
    X, U, Y, meta = wave_d
    assert list(X.columns) == COLS and list(U.columns) == COLS
    dm = po.design_matrix("location_oat_v2")
    for key, r in X.iterrows():
        idx = int(key.split(":")[1])
        d = dm[dm["index"] == idx].iloc[0]
        col = f"mw_{d['oat_site']}"
        assert (r.drop(col) == 0).all()
        assert r[col] == pytest.approx(d["omega"] * d["gen_pmax"], rel=1e-12)
        assert r[col] == pytest.approx(d["pem_mw"], rel=1e-9)
    np.testing.assert_allclose(U.to_numpy(), (X / PMAX).to_numpy(), rtol=0, atol=0)
    assert ((U >= 0) & (U <= 1)).all().all()


@pytest.mark.skipif(not HAVE_D, reason="wave-D extracts not on disk")
def test_wave_d_y_and_meta_from_pool_row(wave_d):
    X, U, Y, meta = wave_d
    assert list(Y.columns) == ["V1", "E1", "R4", "N1"]          # JSON order
    assert list(meta.columns) == L.META_COLS and meta.index.name == "key"
    for key in ("location_oat_v2:1", "location_oat_v2:17"):
        row = po.pool_row(key)
        for c in Y.columns:
            assert Y.loc[key, c] == row[c]
        for c in ("G_run_usd", "R1", "R2"):
            assert meta.loc[key, c] == row[c]
    assert not meta["suspect"].any()
    assert (meta["identity"] == "v3").all()
    assert (meta["tier"] == "").all() and (meta["sobol_index"] == "").all()
    assert "R1" not in Y.columns and "G_run_usd" not in Y.columns


@pytest.mark.skipif(not HAVE_D, reason="wave-D extracts not on disk")
def test_objectives_override(ds_path):
    _, _, Y, _ = L.load(["location_oat_v2"], objectives=["E3", "V1"], design_space=ds_path)
    assert list(Y.columns) == ["E3", "V1"]


# --------------------------------------------------------------------------
# (2) noise_v3 A (batch-nested wave)
# --------------------------------------------------------------------------
@pytest.mark.skipif(not HAVE_N, reason="noise_v3 A extracts not on disk")
def test_noise_v3_a_site_146_only(ds_path):
    X, U, Y, meta = L.load(["noise_v3/A"], design_space=ds_path)
    assert list(X.index) == ["noise_v3/A:3", "noise_v3/A:7"]
    assert sorted(meta.attrs["refused"]["site_not_in_space"]) == sorted(
        f"noise_v3/A:{i}" for i in (1, 2, 4, 5, 6, 8))
    assert (X.drop(columns="mw_146") == 0).all().all()
    assert X.loc["noise_v3/A:3", "mw_146"] == pytest.approx(133.9999995955612, rel=1e-12)
    assert X.loc["noise_v3/A:7", "mw_146"] == pytest.approx(133.86599959596563, rel=1e-12)
    assert list(meta["wave"]) == ["noise_v3/A"] * 2


# --------------------------------------------------------------------------
# (3) refusals on a scratch copy
# --------------------------------------------------------------------------
SLIM = ["overall.csv", "daily_summary.csv", "gen_summary.csv", "committed_hourly.csv",
        "line_summary.csv", "ruc_quality.csv", "hourly_summary.csv",
        "renewables_hourly.csv", "reserves.csv", "identity.txt"]


def _copy_run(src, dst, identity=True):
    os.makedirs(dst, exist_ok=True)
    for f in SLIM:
        p = os.path.join(src, f)
        if os.path.isfile(p) and (identity or f != "identity.txt"):
            shutil.copy(p, dst)


@pytest.mark.skipif(not HAVE_D, reason="wave-D extracts not on disk")
def test_refuses_not_v3_and_not_collected(tmp_path, ds_path):
    extr, waves = tmp_path / "extracts", tmp_path / "waves"
    (waves / "w").mkdir(parents=True)
    shutil.copy(ERCOT / "waves" / "location_oat_v2" / "design_matrix.csv", waves / "w")
    src = ERCOT / "extracts" / "location_oat_v2"
    _copy_run(src / "run_index_1", extr / "w" / "run_index_1")                   # v3
    _copy_run(src / "run_index_2", extr / "w" / "run_index_2", identity=False)   # no identity
    _copy_run(src / "run_index_3", extr / "w" / "run_index_3")
    (extr / "w" / "run_index_3" / "identity.txt").write_text(
        "IDENTITY from GAP_DECISION.json: ruc_mipgap=0.01 ruc_time_limit=360.0 (v2)")
    (extr / "w" / "run_index_4").mkdir()                                         # not collected
    X, U, Y, meta = L.load(["w"], design_space=ds_path, extr=str(extr), waves_dir=str(waves))
    assert list(X.index) == ["w:1"]
    assert meta.attrs["refused"] == {"no_overall": ["w:4"], "not_v3": ["w:2", "w:3"],
                                     "site_not_in_space": []}
    assert meta.attrs["n_refused"] == 3


def test_is_v3():
    assert L.is_v3({"ruc_mipgap": 0.001, "ruc_time_limit": 1200.0})
    assert not L.is_v3({"ruc_mipgap": 0.001, "ruc_time_limit": 360.0})
    assert not L.is_v3({"ruc_mipgap": 0.001})
    assert not L.is_v3(None)


# --------------------------------------------------------------------------
# (4) multi-site __ALL__ rows (contract §5 schema)
# --------------------------------------------------------------------------
DM_COLS = (["index", "oat_site", "unit_type", "bus", "omega", "bid", "gen_pmax", "start_date",
            "num_days", "replicate_of", "pem_mw", "level_id", "tier", "sobol_index"]
           + COLS + [c.replace("mw_", "u_") for c in COLS])


def _all_rows(Uarr, tiers, sobol):
    rows, dicts = [], {}
    for i, (u, t, s) in enumerate(zip(Uarr, tiers, sobol), start=1):
        mw = u * PMAX.to_numpy()
        rows.append({"index": i, "oat_site": "__ALL__", "unit_type": "", "bus": "", "omega": "",
                     "bid": 40.0, "gen_pmax": "", "start_date": "01-01-2019", "num_days": 365,
                     "replicate_of": "", "pem_mw": float(mw.sum()), "level_id": "", "tier": t,
                     "sobol_index": s, **dict(zip(COLS, mw)),
                     **{c.replace("mw_", "u_"): v for c, v in zip(COLS, u)}})
        dicts[i] = {c[3:]: {"PEM_bid": 40.0, "PEM_fraction": float(v), "gen_pmax": float(p)}
                    for c, v, p in zip(COLS, u, PMAX) if v > 0}
    return pd.DataFrame(rows, columns=DM_COLS), dicts


@pytest.fixture
def multi(tmp_path):
    U = np.array([[0.1, 0.0, 0.5, 1.0, 0.25, 0.0],      # site absent = exactly 0
                  [1e-3, 0.2, 0.3, 0.4, 0.5, 0.6],
                  [0.9, 0.8, 0.7, 0.6, 0.5, 0.4]])
    dm, dicts = _all_rows(U, ["grading", "nav", "holdout"], [0, 5, ""])
    extr, waves = tmp_path / "extracts", tmp_path / "waves"
    (waves / "m").mkdir(parents=True)
    dm.to_csv(waves / "m" / "design_matrix.csv", index=False)
    for i, dct in dicts.items():
        (waves / "m" / f"retrofit_gen_dict_{i}.json").write_text(json.dumps(dct))
    return U, dm, extr, waves


@pytest.mark.skipif(not HAVE_D, reason="wave-D extracts not on disk (slim tables are copied)")
def test_multisite_x_u_meta(multi, ds_path):
    U, dm, extr, waves = multi
    for i in (1, 2, 3):   # any v3 slim tables stand in; Y on multi-site rows is a Part B assert
        _copy_run(ERCOT / "extracts" / "location_oat_v2" / "run_index_1", extr / "m" / f"run_index_{i}")
    X, Uo, Y, meta = L.load(["m"], design_space=ds_path, extr=str(extr), waves_dir=str(waves))
    assert list(X.index) == ["m:1", "m:2", "m:3"]
    np.testing.assert_allclose(X.to_numpy(), dm[COLS].to_numpy(float), rtol=0, atol=0)
    np.testing.assert_allclose(Uo.to_numpy(), U, rtol=1e-15, atol=1e-15)
    assert X.loc["m:1", "mw_140"] == 0.0 and X.loc["m:1", "mw_274"] == 0.0
    assert list(meta["tier"]) == ["grading", "nav", "holdout"]
    assert list(meta["sobol_index"]) == [0, 5, ""]
    assert meta.attrs["n_refused"] == 0


@pytest.mark.skipif(not HAVE_D, reason="wave-D extracts not on disk (slim tables are copied)")
def test_multisite_mw_must_match_retrofit_dict(multi, ds_path):
    U, dm, extr, waves = multi
    _copy_run(ERCOT / "extracts" / "location_oat_v2" / "run_index_1", extr / "m" / "run_index_1")
    bad = json.loads((waves / "m" / "retrofit_gen_dict_1.json").read_text())
    bad["110"]["PEM_fraction"] = 0.2
    (waves / "m" / "retrofit_gen_dict_1.json").write_text(json.dumps(bad))
    with pytest.raises(AssertionError, match="retrofit-dict pem_mw"):
        L.load(["m"], design_space=ds_path, extr=str(extr), waves_dir=str(waves))


# --------------------------------------------------------------------------
# (5) the design-space JSON
# --------------------------------------------------------------------------
def test_missing_design_space_names_owner(tmp_path):
    with pytest.raises(FileNotFoundError, match="prompt 53"):
        L.read_design_space(str(tmp_path / "nope.json"))


def test_gen_pmax_matches_wave_d_design_matrix():
    dm = po.design_matrix("location_oat_v2")
    for s in DESIGN_SPACE["sites"]:
        g = dm.loc[dm["oat_site"] == s["site"], "gen_pmax"].unique()
        assert len(g) == 1 and abs(g[0] - s["gen_pmax"]) <= 1e-6


@pytest.mark.skipif(not (ERCOT / "waves" / "design_space_E.json").is_file(),
                    reason="prompt 53's design_space_E.json not on this branch yet")
def test_committed_design_space_matches_contract():
    ds = L.read_design_space()
    for k in ("sites", "x_columns", "bounds_mw_lo", "bounds_mw_hi", "identity"):
        assert ds[k] == DESIGN_SPACE[k], k
