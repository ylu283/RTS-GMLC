"""Prompt 54 Part B v3.3 tests for analysis/ercot_gp/ercot_gp_partb.py (synthetic data only).

Run in bogp-botorch, by file name (contract §1 env note):
    cd trial_0826/ercot && /opt/anaconda3/envs/bogp-botorch/bin/python -m pytest tests/test_ercot_gp_partb.py -q
"""
import json
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ERCOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ERCOT))
from analysis.ercot_gp import ercot_gp_partb as P  # noqa: E402
from analysis.ercot_gp import ercot_gp_status as S  # noqa: E402

GRID = (24, 32, 40, 48)
SITES = [f"s{i}" for i in range(6)]


def _seed():
    rng = np.random.default_rng(3)
    return {"per_candidate": {"S1": {"sigma_c": 2e3, "df": 16, "sigma_c_ci95": [1.5e3, 3e3],
                                     "sd_by_design": [1.8e3, 2.1e3, 2.0e3, 2.2e3],
                                     "delta_seed": rng.normal(0, 2.8e3, 16).tolist(),
                                     "trigger": {"fires": False, "verdict": "x"}}}}


def test_seed_floor_rule():
    assert P.seed_floor(_seed(), "S1") == (2e3, 16, True)
    assert P.seed_floor(_seed(), "S2") == (0.0, 0, False)
    s = {"per_candidate": {"A": {"sigma_c": 1.0, "df": 2}, "B": {"sigma_c": 0.0, "df": 16}}}
    assert P.seed_floor(s, "A")[2] is False and P.seed_floor(s, "B")[2] is False


def _checks(rows):
    return pd.DataFrame(rows)


def test_n_star_rule_and_fallback():
    def row(obj, n, c1, c2, c3, ch=0.05):
        return {"objective": obj, "role": "seated", "n": n, "arm": "m52+std", "loo_cov95": 0, "bar_lo": 0,
                "bar_hi": 0, "c1_cov_in_bar": c1, "rmse_ratio_vs_48": 1.0, "c2_rmse_ok": c2,
                "ls_rel_change_max": ch, "ls_rel_change_median": 0.01, "c3_ls_stable": c3,
                "all_ok": c1 and c2 and c3}
    rows = []
    for obj in ("A", "B"):
        rows += [row(obj, 24, True, True, False, np.nan), row(obj, 32, True, True, True),
                 row(obj, 40, True, True, True), row(obj, 48, True, True, True)]
    c = _checks(rows)
    ns, reason, alt = P.n_star(c, ["A", "B"], [], GRID)
    assert ns == 32 and "n* = 32" in reason
    c.loc[(c.objective == "B") & (c.n == 32), "c2_rmse_ok"] = False
    assert P.n_star(c, ["A", "B"], [], GRID)[0] == 40
    c.loc[(c.objective == "B") & (c.n == 40), "c1_cov_in_bar"] = False
    ns, reason, _ = P.n_star(c, ["A", "B"], [], GRID)
    assert ns == 48 and "no n < 48" in reason
    # co-reported ids never bind the choice
    c2 = c.copy()
    c2.loc[c2.objective == "B", "role"] = "co-reported"
    assert P.n_star(c2, ["A"], ["B"], GRID)[0] == 32


@pytest.fixture(scope="module")
def e2e(tmp_path_factory):
    out = str(tmp_path_factory.mktemp("partb"))
    U, Y, sob, Uh, Yh = S.synthetic_inputs()
    roles = {"S1": "seated", "S2": "co-reported"}
    from analysis.ercot_gp import ercot_gp_mechanism as M
    calls = []

    def load_h():
        calls.append(1)
        return np.asarray(Uh, float), Yh
    rng = np.random.default_rng(9)
    Ulc = pd.DataFrame(rng.random((9, 6)), columns=[f"u_{s}" for s in SITES],
                       index=[f"location_contrast_E:{i}" for i in range(1, 10)])
    Ylc = pd.DataFrame({"S1": 2e6 * np.ones(9), "S2": 100.0 * np.ones(9)}, index=Ulc.index)
    lab = pd.Series([f"L{i}" for i in range(9)], index=Ulc.index)
    kw = {"n_paths": 16, "log2n": 7, "curves": M.wave_d_site_curves_synthetic(), "base": 1.0}
    gp_ = np.array([338.6, 250.6, 268.0, 185.4, 579.0, 746.4])
    res = P.run(U, Y, sob, load_h, _seed(), None, roles, SITES, gp_, out, "synthetic", grid=GRID,
                explore=True, mech=True, mech_kw=kw, lc=(Ulc, Ylc, lab), log=lambda *a: None)
    return out, res, (U, Y, sob, Uh, Yh, roles, gp_, kw, (Ulc, Ylc, lab)), calls


def test_e2e_measured_arm_live_and_study_shape(e2e):
    out, res, *_ = e2e
    d = res["study"]
    assert set(d[d.objective == "S1"].arm) >= {"m52+std", "m52+std+meas", "rbf+std"}
    assert "m52+std+meas" not in set(d[d.objective == "S2"].arm)
    assert (d.groupby(["objective", "n"])["selected"].sum() == 1).all()
    lsc = [f"ls_u_{s}" for s in SITES]
    assert np.isfinite(d[lsc].to_numpy(float)).all()
    meas = d[d.arm == "m52+std+meas"]
    assert (meas["floor"] == 2e3).all()
    assert set(res["exploratory"].arm) <= {a.name for a in P.EXPLORATORY}


def test_e2e_holdout_tiers_ledger_and_committed(e2e):
    out, res, _, calls = e2e
    assert len(calls) == 1
    tiers = res["tiers"]
    assert set(P.PLAN_TIERS) <= set(tiers) and res["n_star"] in tiers and len(tiers) <= 3
    led = S.read_ledger(out)
    assert len(led) == 2 * len(tiers)
    assert not led.duplicated(["objective", "n0"]).any()
    doc = json.load(open(os.path.join(out, S.COMMITTED)))
    for k in ("n_star", "n_star_reason", "n0_tier_recommended", "E-D7_decided", "objectives"):
        assert k in doc
    for obj, c in doc["objectives"].items():
        for k in ("cfg", "floor", "floor_rule", "loo_nlpd_mean", "holdout_cov95", "holdout_cov95_by_tier",
                  "exposure_rows", "n_star", "hyperparameters", "measured_floor_used", "seated"):
            assert k in c, (obj, k)
        assert len(c["exposure_rows"]) == len(tiers)
    assert doc["objectives"]["S1"]["seated"] and not doc["objectives"]["S2"]["seated"]
    for f in ("ercot_gp_status.csv", "ercot_gp_exploratory.csv", "ercot_gp_nstar_checks.csv",
              "ercot_gp_noise_crosscheck.csv", "ercot_gp_mechanism.json", "ercot_gp_lc_residuals.csv",
              "figs/fig_training_size_curves.png", "figs/fig_lengthscales_vs_n.png", "figs/fig_parity_holdout.png"):
        assert os.path.isfile(os.path.join(out, f)), f


def test_e2e_retired_then_replay_only(e2e):
    out, res, (U, Y, sob, Uh, Yh, roles, gp_, kw, lc), _ = e2e
    led0 = S.read_ledger(out)
    with pytest.raises(S.HoldoutRetired):
        P.run(U, Y, sob, lambda: (np.asarray(Uh, float), Yh), _seed(), None, roles, SITES, gp_, out, "synthetic",
              grid=GRID, explore=False, mech=False, log=lambda *a: None)
    r2 = P.run(U, Y, sob, lambda: (np.asarray(Uh, float), Yh), _seed(), None, roles, SITES, gp_, out, "synthetic",
               grid=GRID, explore=False, replay_only=True, mech=False, log=lambda *a: None)
    led1 = S.read_ledger(out)
    assert len(led1) == len(led0)                       # replays never append
    assert all(h["replay"] for o in r2["holdout"].values() for h in o.values())


def test_third_tier_admitted_only_when_passed(tmp_path):
    with pytest.raises(S.HoldoutRetired, match="not a plan tier"):
        S.score_holdout(None, S.DEFAULT_ARM, "V1", 28, None, np.zeros(48), str(tmp_path))
    with pytest.raises(S.HoldoutRetired, match="not a plan tier"):
        S.score_holdout(None, S.DEFAULT_ARM, "V1", 40, None, np.zeros(48), str(tmp_path), tiers=(28, 32, 48))


def test_report_renders(e2e):
    from types import SimpleNamespace
    from analysis.ercot_gp import ercot_gp_partb_report as R
    out, res, *_ = e2e
    res = dict(res)
    res["extra"] = {"n_refused": 0, "r1_max": 0.0, "r2_max": 1.0}
    ds = {"contract_version": "synthetic", "objective_rule": "x", "disclosure": "d"}
    md = R.write_all(res, _seed(), ds, SimpleNamespace(design_space="ds.json"))
    for h in ("## 2. Navigation tier n*", "## 4. Holdout", "## 5. Noise cross-check", "Mechanism sanity",
              "Prompt-61 residual row", "## 9. What changed vs plan", "Exploratory"):
        assert h in md, h
    assert os.path.isfile(os.path.join(out, "pi_agenda_E-D7_draft.md"))


def test_long_fit_diag_is_scoped_and_exploratory():
    U, Y, sob, *_ = S.synthetic_inputs()
    orig = S.common.train_gp
    with P.long_fit(900):
        assert S.common.train_gp is not orig and S.common.train_gp.keywords == {"n_epochs": 900}
    assert S.common.train_gp is orig
    y = Y["S1"].to_numpy(float)
    rows, w = P.study_long(np.asarray(U, float), y, sob, S.arm_set(y, True), 2e3, "S1", "seated", SITES,
                           grid=(32, 48), epochs=900)
    assert S.common.train_gp is orig
    assert {r["fit"] for r in rows} == {"adam900"} and set(w) == {32, 48}
