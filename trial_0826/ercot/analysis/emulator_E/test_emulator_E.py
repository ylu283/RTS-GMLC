"""Prompt 66 — tests for emulator_E.py on a TOY 2-D function (no n0_E, no PCM).

    /opt/anaconda3/envs/bogp-botorch/bin/python -m pytest analysis/emulator_E/test_emulator_E.py -q -p no:cacheprovider
"""

import json
import os
import sys

import numpy as np
import pandas as pd
import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import emulator_E as em  # noqa: E402
import torch  # noqa: E402
from scipy.stats import qmc  # noqa: E402


def toy(U):
    """Smooth 2-D toy with an interior minimum near (0.3, 0.7) and a boundary ridge."""
    U = np.atleast_2d(U)
    return (U[:, 0] - 0.3) ** 2 + 2 * (U[:, 1] - 0.7) ** 2 + 0.3 * np.sin(3 * U[:, 0]) * U[:, 1]


@pytest.fixture(scope="module")
def toy_fit():
    from analysis.ercot_gp import ercot_gp_status as S
    U = qmc.Sobol(2, scramble=True, seed=3).random(24)
    y = toy(U)
    out = {}
    for name, cfg in (("rbf+std", ("rbf", "std", "inferred", "none")), ("m52+std", ("m52", "std", "inferred", "none"))):
        gp = S.fit(U, y, S.Arm(name, cfg, "inferred"), 0.0)
        cov = gp.model.covar_module
        p = em.GPMean.build(U, y, cov.base_kernel.lengthscale.detach().double().numpy().reshape(-1),
                            float(cov.outputscale.detach().double()), float(gp.lik.noise.detach().double()),
                            float(gp.model.mean_module.constant.detach().double()), gp.mx, gp.sx, gp.my, gp.sy, cfg)
        out[name] = (gp, em.GPMean(p))
    return U, y, out


def test_closed_form_equals_flexgp_mean(toy_fit):
    U, y, fits = toy_fit
    Uq = qmc.Sobol(2, scramble=True, seed=9).random(256)
    for name, (gp, f) in fits.items():
        mu, _ = gp.predict_t(Uq)
        assert np.max(np.abs(f(Uq) - mu)) <= 2e-3 * gp.sy, name          # float32 FlexGP vs float64 closed form
        with torch.no_grad():
            ft = f.torch(torch.tensor(Uq, dtype=torch.float64)).numpy()
        assert np.allclose(ft, f(Uq), rtol=0, atol=1e-9 * max(1.0, abs(gp.sy))), name


def test_minimize_fn_interior_and_boundary():
    u, fv, fs = em.minimize_fn(lambda t: ((t[:, 0] - 0.3) ** 2 + (t[:, 1] - 0.7) ** 2), 2, n_sobol=256, n_starts=4)
    assert np.allclose(u, [0.3, 0.7], atol=1e-5) and fv <= fs + 1e-12
    u, fv, _ = em.minimize_fn(lambda t: t[:, 0] + 2 * t[:, 1], 2, n_sobol=256, n_starts=4)
    assert np.allclose(u, [0.0, 0.0], atol=1e-9) and abs(fv) < 1e-12


def test_so_bo_toy_runs_and_records(toy_fit):
    U0 = qmc.Sobol(2, scramble=True, seed=5).random(10)
    rng = np.random.default_rng(0)
    fstar = float(toy(np.array([[0.3, 0.7]]))[0])
    u_s, f_s, _ = em.minimize_fn(lambda t: (t[:, 0] - 0.3) ** 2 + 2 * (t[:, 1] - 0.7) ** 2
                                 + 0.3 * torch.sin(3 * t[:, 0]) * t[:, 1], 2, n_sobol=1024, n_starts=8)
    assert f_s <= fstar + 1e-12

    def observe(U):
        f = toy(U)
        return f + 0.01 * rng.standard_normal(len(f)), f

    st = {"q": 2, "rounds": 2, "num_restarts": 2, "raw_samples": 32, "mc_samples": 32}
    for method in ("bo", "random"):
        recs = em.so_bo(U0, observe(U0)[0], toy(U0), observe, toy, f_s, ("m52", "std", "inferred", "none"), 1e-9,
                        1234, method=method, settings=st, B_unit=0.05, log=lambda *_: None)
        assert [r["round"] for r in recs] == [0, 1, 2] and [r["n"] for r in recs] == [10, 12, 14]
        assert all(np.isfinite(r["regret_best_obs_B"]) and r["regret_best_obs_B"] >= -1e-9 for r in recs)
        best = [r["best_obs"] for r in recs]
        assert all(b <= a + 1e-15 for a, b in zip(best, best[1:]))
        if method == "bo":
            c = recs[1]["calibration"]
            assert set(c) >= {"cov95", "rms_z", "n_abs_z_gt3", "C2", "C3"} and 0 <= c["cov95"] <= 2
            assert len(recs[2]["gp"]["ls_u"]) == 2 and "regret_pm_opt_B" in recs[2]
            assert np.all(np.asarray(recs[1]["u_new"]) >= 0) and np.all(np.asarray(recs[1]["u_new"]) <= 1)
        else:
            assert "calibration" not in recs[1]


def test_calib_equals_55(tmp_path):
    """em.calib reproduces acquire_E._calibration (C2 cov <= 4 of 8; C3 >= 3 of 8 with |z| > 3)."""
    import acquire_E as ae
    rng = np.random.default_rng(1)
    y = rng.normal(size=8) * 3
    pm, ps = np.zeros(8), np.ones(8)
    wave = "methods_E_toy_r1"
    os.makedirs(tmp_path / "waves" / wave)
    pd.DataFrame({"index": range(1, 9), "V1_pred_mean": pm, "V1_pred_sd": ps, "V1_transform": "std"}).to_csv(
        tmp_path / "waves" / wave / "predictions.csv", index=False)

    class L:
        root, objectives, cfg = str(tmp_path), ["V1"], {"q": 8}

        @staticmethod
        def wave(k):
            return wave

    cal55, c2, c3 = ae._calibration(L, 1, pd.DataFrame({"V1": y}))
    mine = em.calib(y, pm, ps)
    assert {k: cal55["V1"][k] for k in ("mean_z", "rms_z", "cov95", "n_abs_z_gt3")} == \
           {k: mine[k] for k in ("mean_z", "rms_z", "cov95", "n_abs_z_gt3")}
    assert (c2, c3) == (mine["C2"], mine["C3"])


def test_hv2d_equals_hypervolume_exact():
    import common_E as ce
    rng = np.random.default_rng(2)
    for n in (1, 3, 20, 80):
        Y = rng.uniform(size=(n, 2))
        R = np.array([0.9, 0.95])
        m = np.all(Y < R, 1)
        want = ce.hv_exact(Y[m], R) if m.any() else 0.0
        assert abs(em.hv2d(Y, R) - want) <= 1e-12
    assert em.hv2d(np.array([[2.0, 2.0]]), np.array([1.0, 1.0])) == 0.0


def test_percentile_ties_half():
    assert em.percentile(5.0, [1.0, 5.0, 9.0]) == pytest.approx(1.5 / 3)
    assert em.percentile(10.0, [1.0, 2.0]) == 1.0 and em.percentile(0.0, [1.0, 2.0]) == 0.0


def test_pareto_mask_toy():
    Y = np.array([[1, 5], [2, 3], [3, 4], [4, 1], [2, 3.5]], float)
    assert em.pareto_mask(Y).tolist() == [True, True, False, True, False]


def test_observer_streams_and_covariance():
    S2 = np.array([[4.0, 1.2], [1.2, 1.0]])
    fake = {"f": {"V1": toy, "E1": lambda U: 2 * toy(U), "N4": lambda U: np.zeros(len(np.atleast_2d(U)))},
            "S2": S2, "mon": {"N4_sd": 1.0, "R2_sd": 2.0, "N1_off_sd": 3.0}}
    U = np.random.default_rng(0).uniform(size=(20000, 2))
    a, b = em.Observer((1, 0, 0, 0), emu=fake)(U), em.Observer((1, 0, 0, 0), emu=fake)(U)
    assert np.array_equal(a["y"], b["y"]) and np.array_equal(a["R2"], b["R2"])           # same key -> same stream
    c = em.Observer((1, 1, 0, 0), emu=fake)(U)
    assert not np.array_equal(a["eps"], c["eps"])
    assert np.allclose(np.cov(a["eps"].T), S2, atol=0.08)
    assert np.allclose(a["y"] - a["eps"], a["f"]) and (a["R1"] == 0).all()
    assert abs(a["R2"].mean() - em.R2_BASE) < 0.1 and abs(a["N1_off"].std() - 3.0) < 0.1
