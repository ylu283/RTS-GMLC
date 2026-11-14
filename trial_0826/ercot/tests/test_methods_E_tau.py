"""Prompt 55 tests — tau rulers (analysis/methods_E/tau_E.py).

Run:  cd trial_0826/ercot && BOGP_PATH=/Users/yilu/Documents/GitHub/bo-gp-qparego \
      /opt/anaconda3/envs/bogp-botorch/bin/python -m pytest tests/test_methods_E_tau.py -q

Port test: with the RTS 32 S1 starts and P1's frozen ref, tau_marginal with the
donor floors reproduces acquire_arm.TAU45_P1 / tau_regrade45.json BIT-FOR-BIT
(old_3000, scalar_285.3, het_ii) — skipped when the RTS checkout is absent.
"""
import json
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ERCOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ERCOT / "analysis" / "methods_E"))
import common_E  # noqa: E402  (pins the bo-gp-qparego worktree BEFORE any bogp import)
pytest.importorskip("bogp", reason="BOGP_PATH / bo-gp-qparego not importable")
import tau_E  # noqa: E402

RTS = Path("/Users/yilu/Documents/GitHub/RTS-GMLC/trial_0826/campaign")
HAVE_RTS = (RTS / "waves" / "stage2_C_n0b" / "objectives.csv").is_file()
TAU45_P1 = {"old_3000": 5.262996664950399e+16, "scalar_285.3": 6508669620258344.0, "het_ii": 3021374766420009.5}
M_RTS = ["load_shed_mwh", "true_curtailment_mwh", "total_cost_less_synthetic_usd"]


def _rts_starts():
    sys.path.insert(0, str(RTS))
    from tiers import TIERS  # noqa: F401
    Ys = []
    for w in ("stage2_C_n0", "stage2_C_n0b"):
        dm = pd.read_csv(RTS / "waves" / w / "design_matrix.csv")
        ob = pd.read_csv(RTS / "waves" / w / "objectives.csv")
        Ys.append(dm.merge(ob[["index"] + M_RTS], on="index")[M_RTS].to_numpy(float))
    Y = np.vstack(Ys)
    ref = np.asarray(json.load(open(RTS / "analysis" / "bo_stage2" / "ledger.json"))["ref_point"], float)
    return Y, ref


@pytest.mark.skipif(not HAVE_RTS, reason="RTS checkout not on disk")
def test_marginal_reproduces_donor_tau45_bit_for_bit():
    Y, ref = _rts_starts()
    assert Y.shape == (32, 3)
    t_old, _ = tau_E.tau_marginal(Y, ref, np.array([3000.0, 5000.0, 0.5e6]))
    t_285, _ = tau_E.tau_marginal(Y, ref, np.array([285.3, 5000.0, 0.5e6]))
    sig = tau_E.sigma_pwl(Y[:, 0], [429.5, 4672.0, 37834.0], [0.0, 13.34, 520.1])
    t_het, _ = tau_E.tau_marginal(Y, ref, np.column_stack([sig, np.full(32, 5000.0), np.full(32, 0.5e6)]))
    assert t_old == TAU45_P1["old_3000"]
    assert t_285 == TAU45_P1["scalar_285.3"]
    assert t_het == TAU45_P1["het_ii"]


def test_sigma_pwl_matches_donor_sigma_ii_form():
    y = np.array([0.0, 429.5, 1000.0, 4672.0, 20000.0, 37834.0, 50000.0])
    got = tau_E.sigma_pwl(y, [429.5, 4672.0, 37834.0], [0.0, 13.34, 520.1])
    s1 = 13.34 / (4672.0 - 429.5); s2 = (520.1 - 13.34) / (37834.0 - 4672.0)
    want = np.where(y <= 429.5, 0.0, np.where(y <= 4672.0, (y - 429.5) * s1, 13.34 + (y - 4672.0) * s2))
    np.testing.assert_allclose(got, want, rtol=0, atol=1e-9)
    assert got[-1] > 520.1                      # last slope extrapolated above the last anchor


def _toy():
    rng = np.random.default_rng(3)
    Y = rng.uniform(size=(20, 4)) * np.array([1e5, 1e9, 1e4, 1e3])
    ref = Y.max(0) + 0.1 * (Y.max(0) - Y.min(0))
    return Y, ref


def test_sigma_zero_branch_is_exact_zero_without_drawing():
    Y, ref = _toy()
    tj, hv = tau_E.tau_joint(Y, ref, Sigma=np.zeros((4, 4)), n_draws=5)
    tm, _ = tau_E.tau_marginal(Y, ref, np.zeros(4), n_draws=5)
    assert tj == 0.0 and tm == 0.0 and np.all(hv == common_E.hv_exact(Y, ref))
    out = tau_E.rulers_from_files(Y, ref, ["V1", "E1", "R4", "N1"], Sigma=np.zeros((4, 4)), n_draws=5)
    assert out["budget_cap_only"] and out["all_exact_zero"] and "budget-cap-only" in out["statement"]
    assert out["sensitivity_joint_over_marginal"] is None


def test_joint_homoscedastic_vs_marginal_and_determinism():
    Y, ref = _toy()
    sd = 0.02 * Y.std(0)
    S = np.diag(sd ** 2)
    tj1, _ = tau_E.tau_joint(Y, ref, Sigma=S, n_draws=200)
    tj2, _ = tau_E.tau_joint(Y, ref, Sigma=S, n_draws=200)
    tm, _ = tau_E.tau_marginal(Y, ref, sd, n_draws=200)
    assert tj1 == tj2 and tj1 > 0 and tm > 0
    assert 0.5 < tj1 / tm < 2.0               # same marginals, different stream: same magnitude
    out = tau_E.rulers_from_files(Y, ref, ["V1", "E1", "R4", "N1"], Sigma=S, n_draws=50)
    assert out["tau_joint"] > 0 and not out["budget_cap_only"] and out["heteroscedastic_objectives"] == []


def test_heteroscedastic_DCD_branch_and_correlation_helper():
    Y, ref = _toy()
    S = np.zeros((4, 4)); S[1, 1] = (0.01 * Y[:, 1].std()) ** 2        # only E1 noisy
    C = tau_E.correlation_from_cov(S)
    assert np.allclose(C, np.eye(4))
    S2 = np.array([[4.0, 1.0], [1.0, 9.0]])
    C2 = tau_E.correlation_from_cov(S2)
    assert np.isclose(C2[0, 1], 1.0 / 6.0) and np.allclose(np.diag(C2), 1)
    noise = {"per_candidate": {"V1": {"trigger": {"fires": True},
                                      "levels": [{"y": 1e4, "sd": 100.0}, {"y": 5e4, "sd": 500.0}, {"y": 9e4, "sd": 2000.0}]},
                               "E1": {"trigger": {"fires": False}}, "R4": {}, "N1": {}}}
    out = tau_E.rulers_from_files(Y, ref, ["V1", "E1", "R4", "N1"], Sigma=S, noise_json=noise, n_draws=50)
    assert out["heteroscedastic_objectives"] == ["V1"] and out["form"].startswith("heteroscedastic")
    assert out["tau_joint"] > 0 and out["tau_marginal"] > 0 and not out["budget_cap_only"]


def test_read_cov_csv_restricts_and_orders(tmp_path):
    ids = ["E1", "N1", "R4", "V1", "X1"]
    S = np.diag([2.0, 3.0, 4.0, 1.0, 9.0])
    pd.DataFrame(S, index=ids, columns=ids).to_csv(tmp_path / "cov.csv")
    got = tau_E.read_cov_csv(tmp_path / "cov.csv", ["V1", "E1", "R4", "N1"])
    np.testing.assert_array_equal(np.diag(got), [1.0, 2.0, 4.0, 3.0])
    with pytest.raises(AssertionError, match="missing"):
        tau_E.read_cov_csv(tmp_path / "cov.csv", ["V1", "Q9"])


def test_rider_levels_sensitivity_label():
    noise = {"noise_floor": {"floor": {"V1": 0.0, "E1": 12.5}},
             "per_candidate": {"V1": {"exact_zero": True, "levels": [{"sd": 3.0, "n": 4}, {"sd": 5.0, "n": 4}]},
                               "E1": {"exact_zero": False, "levels": [{"sd": 1.0, "n": 4}]}}}
    r = tau_E.rider_levels(noise, ["V1", "E1"])
    assert r["V1"]["label"].startswith("sensitivity-level rider") and r["V1"]["level"] == pytest.approx(np.sqrt((3 * 9 + 3 * 25) / 6))
    assert r["E1"]["label"].startswith("noise-level") and r["E1"]["level"] == 12.5
