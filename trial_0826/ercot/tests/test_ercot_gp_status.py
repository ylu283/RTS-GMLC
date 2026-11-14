"""Prompt 54 Part A tests for analysis/ercot_gp/ercot_gp_status.py (plan §4, §5).

Run in bogp-botorch, by file name (contract §1 env note):
    cd trial_0826/ercot && /opt/anaconda3/envs/bogp-botorch/bin/python -m pytest tests/test_ercot_gp_status.py -q

Blocks: (1) pinned numbers (holdout bar, LOO bar, criterion text); (2) arm-set
inclusion rules; (3) NLPD + selection rule; (4) exposure ledger and holdout
retirement; (5) end-to-end on the synthetic 6-D function (~20 s).
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
from analysis.ercot_gp import ercot_gp_status as S  # noqa: E402


# --------------------------------------------------------------------------
# (1) pinned numbers
# --------------------------------------------------------------------------
def test_bars_use_level_090_not_common_default():
    assert S.HOLDOUT_BAR == (43, 48)
    assert S.LOO_BAR_32 == (28, 32)
    assert S.binom_band(48) == (42, 48)            # the plan §4 trap, documented


def test_sufficiency_criterion_text_pinned():
    assert S.SUFFICIENCY_CRITERION == (
        "32 is sufficient iff, for every objective, LOO cov95 at 32 is inside [28, 32] "
        "(binom.interval(0.90, 32, 0.95)) and LOO RMSE_32 / LOO RMSE_48 <= 1.1 and the "
        "committed config at 32 passes the holdout bar [43, 48]; otherwise the "
        "recommendation is 48.")


def test_default_arm_is_d1025():
    assert S.DEFAULT_ARM.cfg == ("m52", "std", "inferred", "none") == S.DEFAULT_CFG
    assert S.DEFAULT_ARM.floor(123.0) == 1e-9


# --------------------------------------------------------------------------
# (2) arm set
# --------------------------------------------------------------------------
def test_log1p_rule():
    assert S.log1p_eligible([0.0, 11.0])           # max / max(min, 1) = 11
    assert not S.log1p_eligible([0.0, 10.0])       # = 10, not > 10
    assert not S.log1p_eligible([-1.0, 100.0])     # min < 0
    assert S.log1p_eligible([5.0, 51.0])
    assert not S.log1p_eligible([5.0, 50.0])


def _noise(sd, df):
    return {"noise_floor": {"floor": {"V1": sd}}, "per_candidate": {"V1": {"exact_df": df}}}


def test_measured_floor_needs_both_halves():
    assert S.measured_floor(_noise(2.0, 3), "V1") == (2.0, 3, True)
    assert S.measured_floor(_noise(2.0, 2), "V1")[2] is False
    assert S.measured_floor(_noise(0.0, 8), "V1")[2] is False
    assert S.measured_floor(None, "V1") == (0.0, 0, False)
    assert S.measured_floor(_noise(2.0, 3), "E1") == (0.0, 0, False)


def test_arm_set_order_and_membership():
    names = lambda arms: [a.name for a in arms]  # noqa: E731
    assert names(S.arm_set([1.0, 2.0], False)) == ["m52+std", "rbf+std"]
    assert names(S.arm_set([0.0, 50.0], True)) == S.ARM_PRIORITY
    meas = S.arm_set([1.0, 2.0], True)[1]
    assert meas.cfg == S.DEFAULT_CFG and meas.floor(7.5) == 7.5


# --------------------------------------------------------------------------
# (3) NLPD and selection
# --------------------------------------------------------------------------
def test_nlpd_points_match_common_metrics():
    rng = np.random.default_rng(0)
    y = rng.uniform(1, 100, 20)
    for tr in ("std", "log1p"):
        t = np.log1p(y) if tr == "log1p" else y
        mu, sd = t + rng.normal(0, 0.1, 20), np.full(20, 0.3)
        m, _ = S.common.metrics(y, mu, sd, tr, 1.0)
        assert S.nlpd_points(y, mu, sd, tr).mean() == pytest.approx(m["nlpd"], rel=1e-12)


def test_paired_se():
    m, se = S.paired([1.0, 2.0, 3.0], [0.0, 0.0, 0.0])
    assert m == 2.0 and se == pytest.approx(1.0 / np.sqrt(3))


def test_recommend():
    ok = {"loo_cov95_32": 31, "loo_rmse_32": 1.05, "loo_rmse_48": 1.0, "holdout_pass_32": True}
    assert S.recommend({"V1": ok, "E1": ok}) == (32, [])
    for bad in ({"loo_cov95_32": 27}, {"loo_rmse_32": 1.11}, {"holdout_pass_32": False}):
        n, why = S.recommend({"V1": ok, "E1": {**ok, **bad}})
        assert n == 48 and len(why) == 1 and why[0].startswith("E1:")


# --------------------------------------------------------------------------
# (4) exposure ledger and retirement (refusals fire before the GP is touched)
# --------------------------------------------------------------------------
def _ledger(out, n):
    rows = [{c: 0 for c in S.LEDGER_COLS} | {"n_scoring": i + 1, "objective": f"o{i}", "n0": 32}
            for i in range(n)]
    pd.DataFrame(rows, columns=S.LEDGER_COLS).to_csv(os.path.join(out, S.LEDGER), index=False)


def test_refuses_25th_scoring(tmp_path):
    _ledger(tmp_path, 24)
    with pytest.raises(S.HoldoutRetired, match="exposure budget"):
        S.score_holdout(None, S.DEFAULT_ARM, "V1", 32, None, np.zeros(48), str(tmp_path))


def test_refuses_repeat_and_non_tier(tmp_path):
    _ledger(tmp_path, 1)                           # o0 at 32
    with pytest.raises(S.HoldoutRetired, match="already scored"):
        S.score_holdout(None, S.DEFAULT_ARM, "o0", 32, None, np.zeros(48), str(tmp_path))
    with pytest.raises(S.HoldoutRetired, match="not a plan tier"):
        S.score_holdout(None, S.DEFAULT_ARM, "V1", 40, None, np.zeros(48), str(tmp_path))


def test_refuses_after_committed(tmp_path):
    (tmp_path / S.COMMITTED).write_text("{}")
    with pytest.raises(S.HoldoutRetired, match="RETIRED"):
        S.score_holdout(None, S.DEFAULT_ARM, "V1", 32, None, np.zeros(48), str(tmp_path))
    with pytest.raises(S.HoldoutRetired):
        S.write_committed(str(tmp_path), {}, 48, "x")


# --------------------------------------------------------------------------
# (5) end-to-end, synthetic 6-D function on a scratch Sobol set
# --------------------------------------------------------------------------
@pytest.fixture(scope="module")
def e2e(tmp_path_factory):
    out = str(tmp_path_factory.mktemp("e2e"))
    U, Y, sob, Uh, Yh = S.synthetic_inputs()
    return out, S.run(U, Y, sob, Uh, Yh, None, out, "synthetic"), (U, Y, sob, Uh, Yh)


def test_e2e_outputs(e2e):
    out, res, _ = e2e
    for f in ("ercot_gp_status.csv", "ercot_gp_selection.csv", "ercot_gp_sufficiency.csv",
              "ercot_gp_recommendation.json", S.LEDGER, S.COMMITTED):
        assert os.path.isfile(os.path.join(out, f)), f
    st = res["status"]
    assert set(st["scope"]) == {"loo", "holdout"} and set(st["n0"]) == {32, 48}
    for c in ("rmse_raw", "cov95", "n", "inferred_noise_sd_raw", "median_95_halfwidth_raw",
              "latent_share_median"):
        assert c in st.columns
    h = st[st["scope"] == "holdout"]
    assert (h["n"] == 48).all() and h["latent_share_median"].between(0, 1).all()


def test_e2e_ledger_one_scoring_per_objective_tier(e2e):
    out, res, _ = e2e
    led = S.read_ledger(out)
    assert list(led["n_scoring"]) == [1, 2, 3, 4]
    assert sorted(zip(led["objective"], led["n0"])) == [("S1", 32), ("S1", 48), ("S2", 32), ("S2", 48)]
    assert (led["bar_lo"] == 43).all() and (led["bar_hi"] == 48).all()


def test_e2e_selection_rule_and_arms(e2e):
    _, res, _ = e2e
    sel = res["selection"]
    assert set(sel[sel["objective"] == "S1"]["arm"]) == {"m52+std", "rbf+std"}   # S1 < 0 never
    assert set(sel[sel["objective"] == "S2"]["arm"]) == set(S.ARM_PRIORITY) - {"m52+std+meas"}
    for (obj, n0), g in sel.groupby(["objective", "n0"]):
        assert g["selected"].sum() == 1
        w = g[g["selected"]].iloc[0]
        if w["arm"] != "m52+std":
            assert w["diff_vs_default"] < -2 * w["paired_se"]
        else:
            assert not g["beats_default"].any()


def test_e2e_sufficiency_is_loo_only_nested(e2e):
    _, res, _ = e2e
    suf = res["sufficiency"]
    assert list(suf.groupby("objective")["n"].apply(list).iloc[0]) == list(S.PREFIXES)
    assert set(suf.columns) == {"objective", "n", "arm", "loo_rmse", "loo_cov95", "loo_nlpd"}


def test_e2e_committed_schema_and_retirement(e2e):
    out, res, data = e2e
    doc = json.loads(Path(res["committed"]).read_text())
    assert doc["identity"] == "v3" and doc["E-D7_decided"] is None
    assert doc["n0_tier_recommended"] == res["recommendation"] in (32, 48)
    for obj, e in doc["objectives"].items():
        for k in ("cfg", "floor", "floor_rule", "loo_nlpd_mean", "holdout_cov95",
                  "holdout_rmse", "exposure_rows"):
            assert k in e, (obj, k)
        assert len(e["cfg"]) == 4 and e["holdout_cov95"][1] == 48
    rec = json.loads(Path(out, "ercot_gp_recommendation.json").read_text())
    assert rec["criterion"] == S.SUFFICIENCY_CRITERION
    with pytest.raises(S.HoldoutRetired):
        S.run(*data, None, out, "synthetic")
