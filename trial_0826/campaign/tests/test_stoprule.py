"""Prompt-37 stop-rule validation tests: truth enumeration (Pareto skyline +
exact 3-D HV vs bogp), RFF/pathwise sampler, lattice/seed determinism, every
stop rule on hand-made trajectories, the early/cap/late definitions on edge
cases, the bogp-path assertion, and a 2-D M1/M4 replay run incl. resume.

  BOGP_PATH=/Users/yilu/Documents/GitHub/bo-gp-qparego PYTHONNOUSERSITE=1 \
  /opt/anaconda3/envs/bogp/bin/python -m pytest tests/test_stoprule.py -v
"""

import os
import sys

import numpy as np
import pytest

torch = pytest.importorskip("torch")
if os.environ.get("BOGP_PATH"):
    sys.path.insert(0, os.environ["BOGP_PATH"])
pytest.importorskip("bogp.mobo.qparego")

CAMPAIGN_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(CAMPAIGN_DIR, "analysis", "stoprule"))

import sr_common as sc  # noqa: E402
import rules  # noqa: E402
from bogp.mobo.pareto import hypervolume_exact, non_dominated_mask  # noqa: E402


# --------------------------------------------------------------------------- #
# truth machinery
# --------------------------------------------------------------------------- #
def _ref_mask(Y):
    _, first = np.unique(Y, axis=0, return_index=True)
    s = np.sort(first)
    m = np.zeros(len(Y), bool)
    m[s[non_dominated_mask(-Y[s])]] = True
    return m


@pytest.mark.parametrize("t", range(60))
def test_skyline_and_hv3d_match_bogp(t):
    rng = np.random.default_rng(t)
    Y = rng.random((int(rng.integers(1, 80)), 3))
    if t % 3 == 0:
        Y = np.round(Y * 4) / 4          # ties and duplicates
    ref = np.array([1.05, 1.1, 0.9])
    assert abs(sc.hv3d(Y, ref) - hypervolume_exact(Y, ref)) <= 1e-12
    m, r = sc.nd_mask_3d(Y), _ref_mask(Y)
    assert m.sum() == r.sum() and set(map(tuple, Y[m])) == set(map(tuple, Y[r]))


def test_truth_enumeration_toy_lattice():
    """3^3 toy lattice, known front: f = (x, y, 2 - x - y) + z  -> front is z = 0
    plane with x + y <= 2 (all 9 cells at z = 0 are mutually non-dominated)."""
    g = np.array(np.meshgrid(range(3), range(3), range(3), indexing="ij")).reshape(3, -1).T
    T = np.column_stack([g[:, 0] + g[:, 2], g[:, 1] + g[:, 2], 4 - g[:, 0] - g[:, 1] + g[:, 2]])
    m = sc.nd_mask_3d(T)
    assert set(np.flatnonzero(m)) == set(np.flatnonzero(g[:, 2] == 0))
    ref = T.max(0) + 1.0
    assert sc.hv3d(T[m], ref) == pytest.approx(hypervolume_exact(T, ref), rel=1e-12)


def test_lattice_index_roundtrip():
    X = sc.lattice_candidates()
    assert X.shape == (sc.N_LATTICE, 6)
    i = np.array([0, 1, 9, 12345, sc.N_LATTICE - 1])
    assert np.array_equal(sc.x_to_index(X[i]), i)
    assert np.array_equal(sc.lattice_index(sc.levels_of(i)), i)


def test_rff_matches_matern32_and_pathwise_interpolates():
    import problems as pb

    rng = np.random.default_rng(0)
    U = rng.random((30, 6))
    y = np.sin(3 * U[:, 0]) + U[:, 1]
    f = pb.EFit.__new__(pb.EFit)
    f.ls, f.s2, f.noise, f.c = np.full(6, 0.6), 1.3, 1e-6, 0.0
    f.U, f.my, f.sy = U, 0.0, 1.0
    f.yz = y
    # pathwise posterior sample passes through (near-noise-free) data
    path = f.sample_path(U, np.random.default_rng(1))
    assert np.max(np.abs(path - y)) < 1e-2
    # RFF prior covariance ~ exact Matern-3/2 (average over many draws)
    Q = rng.random((5, 6))
    K = pb.matern32(Q, Q, f.ls, f.s2)
    f.yz = np.zeros(30)
    f.noise = 1e6   # data ignored -> prior draws
    S = np.array([f.sample_path(Q, np.random.default_rng(100 + s), n_feat=2048) for s in range(400)])
    assert np.max(np.abs(np.cov(S.T, bias=True) - K)) < 0.25 * f.s2


def test_needle_and_plateau_definitions():
    import problems as pb

    u = np.zeros((3, 6)) + 0.5
    u[1, 0], u[1, 2] = 1.0, 1.0            # needle centre, u1 = 1
    u[2, 0], u[2, 2] = 0.5, 1.0            # same u_{3:6} but u1 < 0.75: no well
    f = pb.z_needle_raw(u)
    base = pb.dtlz2(u)
    assert f[1, 2] < 1.0 < base[1, 2] and np.allclose(f[[0, 2]], base[[0, 2]])
    up = np.random.default_rng(0).random((2000, 6))
    assert 0.35 < np.mean(pb.z_plateau_raw(up)[:, 0] == 0) < 0.45


# --------------------------------------------------------------------------- #
# seeds / starts / CRN
# --------------------------------------------------------------------------- #
def test_starts_deterministic_and_fresh():
    import runner

    a, b, c = runner.sobol_starts_6d(0), runner.sobol_starts_6d(0), runner.sobol_starts_6d(1)
    assert np.array_equal(a, b) and len(set(a.tolist())) == 32
    assert not np.array_equal(a, c)
    import problems as pb
    X48, _, _ = pb.load_stage2(["stage2_C_n0", "stage2_C_n0b"])
    assert not set(sc.x_to_index(X48).tolist()) >= set(a.tolist())


def test_noise_is_common_random_numbers():
    import problems as pb

    p = pb.Problem.__new__(pb.Problem)
    p.T, p.pid, p.noise_mult = np.zeros((100, 3)), 21, 1.0
    p.noise_sd = np.array([1.0, 2.0, 3.0])
    y1 = p.evaluate([5, 7], replicate=3)
    y2 = p.evaluate([7, 5], replicate=3)
    assert np.array_equal(y1[0], y2[1]) and np.array_equal(y1[1], y2[0])
    assert not np.array_equal(y1, p.evaluate([5, 7], replicate=4))


def test_bogp_path_assertion():
    if os.environ.get("PYTHONNOUSERSITE") != "1":
        pytest.skip("run with PYTHONNOUSERSITE=1")
    assert sc.assert_bogp().startswith("60e6328")


# --------------------------------------------------------------------------- #
# rules on hand-made trajectories
# --------------------------------------------------------------------------- #
def test_s0_fires_caps_and_window():
    tau = 1.0
    assert rules.s0(np.array([0.5, 0.5, 5, 5]), tau, 2, 4) == (2, True)
    assert rules.s0(np.array([5, 0.5, 0.5, 5]), tau, 2, 4) == (3, True)
    assert rules.s0(np.array([5, 0.5, 5, 0.5, 0.5]), tau, 2, 4) == (4, False)   # cap
    assert rules.s0(np.array([5, 0.5, 5, 0.5, 0.5]), tau, 2, 8) == (5, True)
    assert rules.s0(np.array([1.0, 1.0]), tau, 2, 4) == (2, False)            # strict <
    assert rules.s0(np.array([5, 0.5]), tau, 1, 4) == (2, True)
    assert rules.s0(np.array([0.1, 0.1, 0.1]), tau, 3, 4) == (3, True)


def test_live_stage2_trajectory_stops_at_r2():
    """BO_STAGE2 ledger: tau 5.263e16, gains 3.63e16, 9.18e15 -> stop at r2."""
    g = np.array([3.629705777052557e16, 9.18e15])
    assert rules.s0(g, 5.262996664950399e16, 2, 4) == (2, True)


def test_s_rel_s_model_ocd_oracle():
    H = np.array([100.0, 110, 111, 111.5, 111.6])
    assert rules.s_rel(np.diff(H), H, 0.02, 4) == (2, True)
    e = np.array([5.0, 0.5, 0.4, 3.0])
    assert rules.s_model(e, 1.0, 2, 4) == (2, True)    # batches 2,3 predicted low
    assert rules.s_model(e, 1.0, 1, 4) == (1, True)    # batch 2 predicted low
    assert rules.s_model(np.array([5.0, 5, 5, 0.1]), 1.0, 1, 8) == (3, True)
    assert rules.s_model(np.array([5.0, 5, 5, 5]), 1.0, 2, 8) == (4, False)
    # OCD: steep linear trend with large variance -> neither test fires
    assert rules.s_ocd(np.array([100.0, 60, 20, -20]), 1.0, K=4) == (4, False)
    # flat series -> variance test fires at k = 3
    assert rules.s_ocd(np.array([0.01, 0.011, 0.012, 5]), 1.0, K=4) == (3, True)
    # oracle: argmin -H_r + tau r
    assert rules.oracle(np.array([0.0, 10, 10.5, 30, 30.2]), 1.0) == 3


def test_early_cap_late_definitions():
    Ht = np.array([0.0, 10, 10.2, 10.4, 10.6, 10.8, 11.0, 11.2, 11.4])  # gains 0.2 after r1
    m = rules.stop_metrics(2, True, 4, Ht, 20.0, tau=1.0, q=8)
    # r* = 1 (4-round future gain from r1 is 0.8 <= tau): a w = 2 rule that
    # stops at r2 has wasted exactly its 1-round detection delay
    assert not m["early"] and m["late"] and m["wasted"] == 1 and m["r_star"] == 1
    # cumulative: per-round gains 0.3 each but 4-round sum 1.2 > tau -> early
    Ht2 = np.array([0.0, 10, 10.3, 10.6, 10.9, 11.2, 11.5, 11.8, 12.1])
    m2 = rules.stop_metrics(2, True, 4, Ht2, 20.0, tau=1.0, q=8)
    assert m2["early"] and m2["future_gain_tau"] == pytest.approx(1.2)
    # cap stop is its own category and never 'early'
    m3 = rules.stop_metrics(4, False, 4, Ht2, 20.0, tau=1.0, q=8)
    assert m3["cap"] and not m3["early"]
    # late: nothing more to gain from r1 on, rule runs to 4 -> 3 wasted rounds
    Ht3 = np.array([0.0, 10, 10, 10, 10, 10, 10, 10, 10])
    m4 = rules.stop_metrics(4, False, 4, Ht3, 20.0, tau=1.0, q=8)
    assert m4["late"] and m4["wasted"] == 3 and m4["r_star"] == 1
    assert m4["regret_star"] == pytest.approx(0.5) and m4["regret_budget_tau"] == 0
    # stop at R: future gain 0, not early
    assert not rules.stop_metrics(8, True, 8, Ht2, 20.0, 1.0, 8)["early"]


def test_apply_all_shapes():
    Ho = np.array([100.0, 104, 105, 105.5, 106, 106.2, 106.3, 106.4, 106.5])
    rows = rules.apply_all({"H_obs": Ho, "H_true": Ho - 1, "H_star": 120.0, "tau": 2.0,
                            "q": 8, "ehvi": np.full(8, 0.5)})
    kinds = {r["rule"] for r in rows}
    assert kinds == {"S0", "S-rel", "S-OCD", "S-model", "S-fix", "Oracle"}
    assert sum(r["rule"] == "S0" for r in rows) == 2 * 3 * 10
    assert sum(r["rule"] == "S-fix" for r in rows) == 8


# --------------------------------------------------------------------------- #
# 2-D replay run (M1 + M4), resume determinism
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("method", ["M4", "M1"])
def test_replay_run_and_resume(tmp_path, method):
    import runner

    full = runner.run("R-B", method, 0, rounds=3, out=tmp_path / "a.npz", verbose=False)
    part = tmp_path / "b.npz"
    runner.run("R-B", method, 0, rounds=1, out=part, verbose=False)
    # promote the 1-round result to a checkpoint and resume to 3 rounds
    z = dict(np.load(part, allow_pickle=True))
    np.savez_compressed(part.with_suffix(".ckpt.npz"), idx=z["idx"], Yobs=z["Yobs"],
                        rec=z["rec"], k_done=1)
    part.unlink()
    import json
    rec = json.loads(str(z["rec"]))
    rec["rounds"] = 3
    zz = dict(np.load(part.with_suffix(".ckpt.npz"), allow_pickle=True))
    zz["rec"] = json.dumps(rec)
    np.savez_compressed(part.with_suffix(".ckpt.npz"), **zz)
    resumed = runner.run("R-B", method, 0, rounds=3, out=part, verbose=False)
    a, b = np.load(full), np.load(resumed)
    assert np.array_equal(a["idx"], b["idx"]) and len(a["idx"]) == 5 + 3 * 2
    assert len(set(a["idx"].tolist())) == len(a["idx"])


def test_m3_replay_round(tmp_path):
    """M3 (35's qNEHVI copy) runs 2 rounds on a 2-D grid."""
    pytest.importorskip("botorch")
    import json
    import runner

    out = runner.run("R-B", "M3", 0, rounds=2, out=tmp_path / "m3.npz", verbose=False)
    z = np.load(out, allow_pickle=True)
    rec = json.loads(str(z["rec"]))
    assert len(z["idx"]) == 9 and len(set(z["idx"].tolist())) == 9
    assert all(np.isnan(r["ehvi256"]) for r in rec["per_round"])   # 2-D: no S-model


def test_wasted_net_of_window():
    Ht = np.array([0.0, 10, 10, 10, 10, 10, 10, 10, 10])
    m = rules.stop_metrics(2, True, 4, Ht, 20.0, tau=1.0, q=8, w=2)
    assert m["wasted"] == 1 and m["wasted_net"] == 0 and m["late"] and not m["late_net"]
    m = rules.stop_metrics(4, False, 4, Ht, 20.0, tau=1.0, q=8, w=2)
    assert m["wasted"] == 3 and m["wasted_net"] == 2


def test_q4_variants():
    Ho = np.linspace(100, 110, 17)
    rows = rules.apply_q4({"H_obs": Ho, "H_true": Ho, "H_star": 120.0, "tau": 1.0, "q": 4})
    assert [r["variant"] for r in rows] == ["unscaled", "scaled_q/8", "window16"]
    assert all(r["K"] == 8 for r in rows)
