"""Prompt 54 §3.5 (v3.2) tests — analysis/ercot_gp/ercot_gp_mechanism.py.

Run:  cd trial_0826/ercot && /opt/anaconda3/envs/bogp-botorch/bin/python -m pytest tests/test_ercot_gp_mechanism.py -q

Network facts asserted from the committed data; the RFF posterior path sampler
against the exact gpytorch posterior; the share estimators on known truths
(additive -> I = 0, pure-T -> L = 0, first-order indices sum to 1); the null
truths (PCHIP through the knots, monotone per site, concave total-only); the
flag logic; R4 / N1 suppression; a small real null run (no n0_E Y is read).
"""
import json
import os
import sys
from pathlib import Path

import numpy as np
import pytest

ERCOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ERCOT))
from analysis.ercot_gp import ercot_gp_mechanism as M  # noqa: E402
from analysis.ercot_gp import ercot_gp_status as S  # noqa: E402

HAVE_DATA = ((ERCOT / "extracts" / "base_v3" / "run_index_1" / "overall.csv").is_file()
             and (ERCOT / "analysis" / "pool" / "pool_wavedD_wide.csv").is_file()
             and (ERCOT / "waves" / "n0_E" / "design_matrix.csv").is_file())
PMAX = np.array([338.599998942999, 250.5999989428539, 267.9999991911224, 185.3999876467921, 578.9999877407346, 746.3999877635443])
SITES = ["110", "140", "146", "163", "270", "274"]


@pytest.mark.skipif(not HAVE_DATA, reason="committed data not on disk")
def test_network_facts_asserted_from_data():
    f = M.network_facts()
    assert f["exit_bus"] == 120 and f["appendage_buses"] == [2, 75, 121]
    assert set(f["exit_lines"]) == {"L4", "L5", "L240"}
    assert f["binding_line"] == "L252" and f["cont_rating_mw"] == 700.0 and f["hours_ge_99pct_base_v3"] == 5426
    assert "one electrical location" in f["text"]


def _toy_gp(seed=0, n=48):
    rng = np.random.default_rng(seed)
    U = rng.random((n, 6))
    y = 3.0 * U[:, 0] + np.sin(2 * U[:, 1]) - 0.5 * U[:, 2] * U[:, 3] + rng.normal(0, 0.01, n)
    return U, y, S.fit(U, y, S.DEFAULT_ARM)


def test_path_sampler_matches_exact_posterior():
    U, y, gp = _toy_gp()
    rng = np.random.default_rng(1)
    Uq = rng.random((40, 6))
    mu, sd = M.exact_posterior_std(gp, Uq)
    ps = M.PathSampler(gp, n_features=4096, seed=3)
    F = ps.sample_std(ps.standardize(Uq), 4000)
    assert F.shape == (4000, 40)
    assert np.abs(F.mean(0) - mu).max() <= 0.1 * sd.max()
    ratio = F.std(0) / sd
    assert 0.75 <= ratio.min() and ratio.max() <= 1.3
    # raw-scale paths de-standardize with the GP's my / sy (std transform)
    R = ps.sample_raw(Uq, 10)
    assert R.shape == (10, 40) and np.isfinite(R).all()
    assert abs(R.mean() - (mu.mean() * gp.sy + gp.my)) < 5 * gp.sy


def test_share_estimators_on_known_truths():
    A, B = M.sobol_base(6, 11)
    P = M.design_points(A, B)
    assert P.shape == (2 ** 11 * 8, 6) and np.array_equal(P[: 2 ** 11], A)
    T_A = (A * PMAX).sum(1)
    f_add = (3 * P[:, 0] + np.sin(2 * P[:, 1]) - 0.5 * P[:, 2] + P[:, 5] ** 2)[None, :]
    sh = M.shares_from_paths(f_add, len(A), 6, T_A)
    assert abs(sh["I"][0]) < 0.01 and abs(sh["S_first"].sum() - 1.0) < 0.01     # additive: no interaction
    assert sh["L"][0] > 0.5                                                      # and strongly location-dependent
    f_tot = np.exp(-(P * PMAX).sum(1) / 800.0)[None, :]
    sh2 = M.shares_from_paths(f_tot, len(A), 6, T_A)
    assert abs(sh2["L"][0]) < 0.03                                              # pure function of T: L = 0
    assert sh2["I"][0] > 0.0                                                    # a nonlinear g(T) does interact
    s = M.summarize(np.arange(100.0))
    assert s["median"] == 49.5 and s["p05"] == pytest.approx(4.95) and s["p95"] == pytest.approx(94.05)


def test_posterior_shares_on_a_fitted_gp():
    U, y, gp = _toy_gp()
    out = M.posterior_shares(gp, PMAX, n_paths=64, log2n=10, n_features=2048)
    assert out["L"].shape == (64,) and out["S_first"].shape == (64, 6) and len(out["lengthscales_u"]) == 6
    assert np.all(np.isfinite(out["L"])) and np.all(np.isfinite(out["I"]))
    assert np.median(out["I"]) < 0.2            # the toy has one small interaction term


def _curves():
    base = 5.83e6
    y = {"110": [5.62e6, 5.43e6, 5.25e6], "140": [5.63e6, 5.44e6, 5.27e6], "146": [5.63e6, 5.46e6, 5.28e6],
         "163": [5.62e6, 5.41e6, 5.30e6], "270": [5.60e6, 5.41e6, 5.19e6], "274": [5.62e6, 5.41e6, 5.19e6]}
    return {s: {"mw": [0.0, 60.0, 120.0, 180.0], "y": [base, *v]} for s, v in y.items()}, base


def test_null_truths_pass_knots_monotone_and_concave():
    curves, base = _curves()
    f_add = M.additive_truth(curves, base, SITES, PMAX)
    for j, s in enumerate(SITES):
        X = np.zeros((4, 6)); X[:, j] = curves[s]["mw"]
        np.testing.assert_allclose(f_add(X), curves[s]["y"], rtol=1e-12)        # through the knots
        mw = np.linspace(0, PMAX[j], 400); X = np.zeros((400, 6)); X[:, j] = mw
        v = f_add(X)
        assert np.all(np.diff(v) <= 1e-6) and np.all(v >= 0)                     # monotone, floored
    X2 = np.zeros((1, 6)); X2[0, 0] = 60.0; X2[0, 3] = 60.0
    assert f_add(X2)[0] == pytest.approx(base + (curves["110"]["y"][1] - base) + (curves["163"]["y"][1] - base))
    g, par = M.total_only_truth(curves, base, SITES)
    assert par["a"] > 0 and par["b"] > 0
    T = np.linspace(0, PMAX.sum(), 300)
    v = g(np.column_stack([T] + [np.zeros_like(T)] * 5))
    assert np.all(np.diff(v) < 0) and np.all(np.diff(v, 2) > 0)                  # decreasing, convex-up drop = concave relief
    assert g(np.zeros((1, 6)))[0] == pytest.approx(base)
    # total-only truth is a function of T only: same T, different split -> same value
    Xa = np.zeros((1, 6)); Xa[0, 0] = 100.0; Xb = np.zeros((1, 6)); Xb[0, 4] = 100.0
    assert g(Xa)[0] == g(Xb)[0]


def test_flag_logic_and_suppression():
    assert M.flag({"p05": 0.3, "p95": 0.5}, 0.2, 0.1, "INTERACTION") == "INTERACTION"
    assert M.flag({"p05": 0.0, "p95": 0.05}, 0.2, 0.1, "INTERACTION") == "ADDITIVE"
    assert M.flag({"p05": 0.0, "p95": 0.05}, 0.2, 0.1, "LOCATION") == "TOTAL-ONLY-COMPATIBLE"
    assert M.flag({"p05": 0.05, "p95": 0.3}, 0.2, 0.1, "LOCATION") == "UNRESOLVED"
    rng = np.random.default_rng(2)
    sh = {"L": rng.uniform(0.6, 0.7, 50), "I": rng.uniform(0.3, 0.4, 50), "S_first": rng.random((50, 6)), "lengthscales_u": [1.0] * 6}
    null = {"thresholds": {"I_null95_additive": 0.1, "I_null_median_additive": 0.05,
                           "L_null95_total_only": 0.1, "L_null_median_total_only": 0.05}}
    noise = {"per_candidate": {"V1": {"perturbed_delta_signed": [1000.0, -2000.0, 1500.0, -500.0, 800.0, -1200.0, 300.0, -900.0]},
                               "R4": {"perturbed_delta_signed": [10, -20, 15, -5, 8, -12, 3, -9]},
                               "N1": {"perturbed_delta_signed": [0.0] * 8}}}
    bars = M.readability_bar(noise, ["V1", "R4", "N1"])
    d = np.array([1000.0, -2000.0, 1500.0, -500.0, 800.0, -1200.0, 300.0, -900.0])
    assert bars["V1"]["sigma_hat"] == pytest.approx(np.sqrt(np.mean(d ** 2))) and bars["V1"]["B"] == pytest.approx(max(3 * np.sqrt(np.mean(d ** 2)), 2000.0))
    assert bars["N1"]["B"] == 0.0 and not M.chatter_readable(bars["N1"], 1e9)
    assert M.chatter_readable(bars["R4"], 2 * bars["R4"]["B"]) and not M.chatter_readable(bars["R4"], 1.9 * bars["R4"]["B"])
    fl = M.mechanism_flags({"V1": sh, "R4": sh, "N1": sh}, null, holdout_pass={"V1": True, "R4": True, "N1": False},
                           bars=bars, y_ranges={"V1": 1e6, "R4": 1.0, "N1": 1e3})
    assert fl["V1"]["flag_interaction"] == "INTERACTION" and fl["V1"]["flag_location"] == "LOCATION" and fl["V1"]["suppressed"] is None
    assert fl["R4"]["suppressed"] and "chatter readable = False" in fl["R4"]["suppressed"]
    assert fl["N1"]["suppressed"] and "holdout pass = False" in fl["N1"]["suppressed"]
    fl2 = M.mechanism_flags({"R4": sh}, null, holdout_pass={"R4": True}, bars=bars, y_ranges={"R4": 1000.0})
    assert fl2["R4"]["suppressed"] is None
    md = M.mechanism_md({"text": "facts"}, {"objective": "V1", "cfg": ["m52", "std", "inferred", "none"], "arm": "m52+std",
                                           "n_paths": 50, "sobol_log2n": 9, "seed": 1, "base_v3": 1.0,
                                           "total_only_params": {"a": 1.0, "b": 2.0, "form": "f"},
                                           "truths": {"additive": {"truth_L": 0.5, "truth_I": 0.0, "L": M.summarize(sh["L"]), "I": M.summarize(sh["I"])}},
                                           "thresholds": null["thresholds"]}, fl)
    assert "(suppressed) INTERACTION" in md and "| V1 |" in md and "prompt 61" in md


@pytest.mark.skipif(not HAVE_DATA, reason="committed data not on disk")
def test_small_real_null_run_reads_no_y(tmp_path):
    """Builds the V1 null from wave D + base_v3 at the n0_E X (48 rows): the additive
    truth has I ~ 0 and the total-only truth has L ~ 0; JSON + figure + md written.
    Reads NO n0_E Y (design matrix X only)."""
    null = M.run_null(str(tmp_path), n_paths=32, log2n=9)
    assert null["n0_E_X_rows"] == 48 and null["objective"] == "V1" and null["base_v3"] == pytest.approx(5828726.2, rel=1e-6)
    t = null["truths"]
    assert abs(t["additive"]["truth_I"]) < 0.02 and t["total_only"]["truth_L"] < 0.05
    assert t["additive"]["truth_L"] > t["total_only"]["truth_L"]
    for k in ("I_null95_additive", "L_null95_total_only"):
        assert 0.0 <= null["thresholds"][k] <= 1.0
    assert all(len(null["curves"][s]["mw"]) == 4 for s in SITES)
    for f in ("ercot_gp_null.json", "fig_null_truths.png", "ERCOT_GP_MECHANISM_NULL.md"):
        assert (tmp_path / f).is_file()
    js = json.loads((tmp_path / "ercot_gp_null.json").read_text())
    assert js["network_facts"]["hours_ge_99pct_base_v3"] == 5426 and "n0_E_X_rows" in js
