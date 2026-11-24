#!/usr/bin/env python3
"""Prompt 66 — EMULATOR BO dry run on the committed GPs (no PCM, no CRC).

MACHINERY CHECK, not a scientific result: nothing here enters a ledger, the
plan, a decision row or the paper's claims. Every output is labelled EMULATOR
and lives under analysis/emulator_E/ only.

    PY=/opt/anaconda3/envs/bogp-botorch/bin/python
    $PY analysis/emulator_E/emulator_E.py fit-emulator          # truth f_j, hyperparameters, f* (writes emulator_E_params.json)
    $PY analysis/emulator_E/emulator_E.py single --obj V1 --seed 0 --method bo [--variant long]
    $PY analysis/emulator_E/emulator_E.py multi --scenario s0 --seeds 0 [--variant long]
    $PY analysis/emulator_E/emulator_E.py random-pool           # the 48 i.i.d. emulated points + prompt-34 subset HVs
    $PY analysis/emulator_E/emulator_E.py front                 # emulator Pareto front (dense Sobol 2^14 on f)
    $PY analysis/emulator_E/emulator_E.py collect               # emulator_E_single.csv, emulator_E_multi.csv
    $PY analysis/emulator_E/emulator_E.py figs                  # assert-before-draw, then figs/
    $PY analysis/emulator_E/emulator_E.py report                # EMULATOR_BO.md

Emulator (prompt 66 §1). For each objective j in {V1, E1} (seated) and N4
(co-reported, logged only): f_j(u) = the posterior mean of the committed GP
(committed_configs.json cfg; fitted by the SAME code path as prompt 54 —
`ercot_gp_status.fit` = D-1025 FlexGP, bogp.train_gp Adam 700 epochs, float32,
torch.manual_seed(0) — on the n* = 48 grading rows of n0_E read by the real
54 loader). The fitted hyperparameters are frozen into a float64 closed form
f(u) = my + sy * (c + k(x, X) (K + s2 I)^-1 (ty - c)), checked against FlexGP's
own predictive mean. Observation y_j(u) = f_j(u) + eps, eps ~ N(0, Sigma_c[V1, E1])
(prompt-63 Seed chatter covariance, ercot_noise_seed_sigma_c.csv), numpy
default_rng streams rooted at 6666. Guardrails: R1 shed = 0 (except injected
scenario rows), R2 = 156.08 + chatter, N1_off = 30,750 + chatter (independent
monitor stream). The START SET is the same 48 n0_E designs with EMULATED values
f(u_i) + eps_i (eps from default_rng(6666), first draw): one generating process
for every Y the BO sees.
"""

from __future__ import annotations

import argparse
import functools
import glob
import json
import os
import shutil
import sys
import time
import warnings

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ERCOT = os.path.abspath(os.path.join(HERE, "..", ".."))
METHODS = os.path.join(ERCOT, "analysis", "methods_E")
for p in (METHODS, ERCOT):
    if p not in sys.path:
        sys.path.insert(0, p)

import common_E as ce  # noqa: E402  (pins bo-gp-qparego first)

import torch  # noqa: E402

np.seterr(all="ignore") if os.environ.get("EMU_NUMPY_QUIET", "1") == "1" else None   # macOS numpy: spurious matmul warnings
torch.set_num_threads(int(os.environ.get("EMU_THREADS", "2")))

DS_PATH = os.path.join(ERCOT, "waves", "design_space_E_2026-11-24.json")
CONFIGS = os.path.join(ERCOT, "analysis", "ercot_gp", "committed_configs.json")
LANDING_R = os.path.join(ERCOT, "waves", "n0_E", "landing_R.json")
SIGMA_C_CSV = os.path.join(ERCOT, "analysis", "noise_v3", "ercot_noise_seed_sigma_c.csv")
ARMS_E = os.path.join(METHODS, "arms_E.json")
PARAMS = os.path.join(HERE, "emulator_E_params.json")
RUNS = os.path.join(HERE, "runs_compact")          # committed (the report reads only these)
RUNS_BIG = os.path.join(HERE, "runs")             # gitignored (trial_0826/ercot/**/runs/): logs + subset-HV npz
FIGS = os.path.join(HERE, "figs")

SEATED = ["V1", "E1"]
CO_REPORTED = ["N4"]
B = {"V1": 18739.0, "E1": 1.862e6}           # rule-v2 bars B_j (prompt 66 brief)
N_STAR = 48                                    # 54's n*, navigation tier (provisional; E-D7 open)
EMU_SEED = 6666
R2_BASE, R2_FLAG = 156.08, 312.16
N1OFF_BASE, N1OFF_FLAG_A = 30750.0, 462.7
SINGLE_SEED_BASE = 20261007                    # prompt 66 §2: seed 20261007 (+ 100 * seed_id + k, the 55 rule)
SO = {"q": 8, "rounds": 4, "num_restarts": 20, "raw_samples": 512, "mc_samples": 128, "sequential": True}
SEED_IDS_SINGLE = (0, 1, 2)
LONG_EPOCHS = 10000
SUBSET_SEED = 20261012                         # prompt 34 sampler seed
N_SUBSETS, N_BOOT, N_BOOT_SUBSETS = 100_000, 1000, 2000
FAMILY = {"single_V1": 1, "single_E1": 2, "multi": 3, "pool": 4}
SCEN = {"s0": 0, "s1": 1, "s2": 2}
INJECT = {"s0": {}, "s1": {3: 2.5}, "s2": {2: 1.5, 6: 40.0}}   # round-1 run index -> injected shed (MWh)
VARIANT = {"house": 0, "long": 1}


def now():
    return ce.now()


class WarnCount:
    """Count (and silence) warnings raised inside a block, by category name; recorded per round."""

    def __enter__(self):
        self._cm = warnings.catch_warnings(record=True)
        self.w = self._cm.__enter__()
        warnings.simplefilter("always")
        return self

    def __exit__(self, *exc):
        self._cm.__exit__(*exc)
        self.counts = {}
        for x in self.w:
            k = x.category.__name__
            self.counts[k] = self.counts.get(k, 0) + 1
        return False


# --------------------------------------------------------------------------- #
# Sigma_c
# --------------------------------------------------------------------------- #

def sigma_c(ids, path=SIGMA_C_CSV):
    df = pd.read_csv(path, index_col=0)
    S = df.loc[ids, ids].to_numpy(float)
    S = 0.5 * (S + S.T)
    assert np.all(np.linalg.eigvalsh(S) >= -1e-9 * np.abs(S).max()), "Sigma_c block not PSD"
    return S


# --------------------------------------------------------------------------- #
# the emulator: frozen float64 closed form of a fitted FlexGP posterior mean
# --------------------------------------------------------------------------- #

def _kern(name, A, Bm):
    """A (n, d), Bm (m, d) already divided by the lengthscales; numpy or torch."""
    if isinstance(A, torch.Tensor):
        d2 = ((A[:, None, :] - Bm[None, :, :]) ** 2).sum(-1)
        if name == "rbf":
            return torch.exp(-0.5 * d2)
        r = torch.sqrt(d2.clamp_min(1e-30))
        r = torch.where(d2 > 0, r, torch.zeros_like(r))
        if name == "m52":
            return (1 + np.sqrt(5) * r + 5.0 / 3.0 * d2) * torch.exp(-np.sqrt(5) * r)
        if name == "m32":
            return (1 + np.sqrt(3) * r) * torch.exp(-np.sqrt(3) * r)
        raise ValueError(name)
    d2 = ((A[:, None, :] - Bm[None, :, :]) ** 2).sum(-1)
    if name == "rbf":
        return np.exp(-0.5 * d2)
    r = np.sqrt(d2)
    if name == "m52":
        return (1 + np.sqrt(5) * r + 5.0 / 3.0 * d2) * np.exp(-np.sqrt(5) * r)
    if name == "m32":
        return (1 + np.sqrt(3) * r) * np.exp(-np.sqrt(3) * r)
    raise ValueError(name)


class GPMean:
    """f(u) = my + sy * (c + os * k((x - X)/ls) alpha), x = (u - mx) / sx, transform std."""

    def __init__(self, p: dict):
        self.p = p
        self.kernel = p["cfg"][0]
        assert p["cfg"][1] == "std", "emulator closed form implemented for the std transform (committed V1/E1/N4)"
        self.mx, self.sx = np.asarray(p["mx"], float), np.asarray(p["sx"], float)
        self.my, self.sy = float(p["my"]), float(p["sy"])
        self.ls = np.asarray(p["ls_std"], float)
        self.os, self.c = float(p["outputscale_std"]), float(p["mean_const_std"])
        self.tx = np.asarray(p["tx_train"], float)
        self.alpha = np.asarray(p["alpha"], float)
        self._t = {k: torch.tensor(v, dtype=torch.float64) for k, v in
                   (("mx", self.mx), ("sx", self.sx), ("ls", self.ls), ("tx", self.tx), ("alpha", self.alpha))}

    @staticmethod
    def build(U, y, ls_std, outputscale_std, noise_var_std, mean_const_std, mx, sx, my, sy, cfg):
        U = np.asarray(U, float)
        y = np.asarray(y, float)
        tx = (U - mx) / sx
        ty = (y - my) / sy
        ls = np.asarray(ls_std, float)
        K = outputscale_std * _kern(cfg[0], tx / ls, tx / ls) + noise_var_std * np.eye(len(U))
        L = np.linalg.cholesky(K)
        alpha = np.linalg.solve(L.T, np.linalg.solve(L, ty - mean_const_std))
        return {"cfg": list(cfg), "mx": list(map(float, mx)), "sx": list(map(float, sx)), "my": float(my),
                "sy": float(sy), "ls_std": list(map(float, ls)), "outputscale_std": float(outputscale_std),
                "noise_var_std": float(noise_var_std), "mean_const_std": float(mean_const_std),
                "tx_train": tx.tolist(), "alpha": alpha.tolist(), "cond_K": float(np.linalg.cond(K))}

    def __call__(self, U):
        U = np.atleast_2d(np.asarray(U, float))
        x = (U - self.mx) / self.sx
        ks = self.os * _kern(self.kernel, x / self.ls, self.tx / self.ls)
        return self.my + self.sy * (self.c + ks @ self.alpha)

    def torch(self, u):
        """u: (n, d) float64 tensor in [0, 1]; differentiable."""
        t = self._t
        x = (u - t["mx"]) / t["sx"]
        ks = self.os * _kern(self.kernel, x / t["ls"], t["tx"] / t["ls"])
        return self.my + self.sy * (self.c + ks @ t["alpha"])


def minimize_fn(fn_torch, d, seed=0, n_sobol=2 ** 14, n_starts=32):
    """Multi-start L-BFGS-B on [0, 1]^d: dense scrambled Sobol screen, best n_starts polished.
    Returns (u*, f*, sobol_min)."""
    from scipy.optimize import minimize
    from scipy.stats import qmc
    S = qmc.Sobol(d, scramble=True, seed=seed).random(n_sobol)
    with torch.no_grad():
        fs = fn_torch(torch.tensor(S, dtype=torch.float64)).numpy()
    starts = S[np.argsort(fs)[:n_starts]]

    def fg(u):
        ut = torch.tensor(u[None, :], dtype=torch.float64, requires_grad=True)
        v = fn_torch(ut).sum()
        v.backward()
        return float(v), ut.grad.numpy().reshape(-1).astype(float)

    best_u, best_f = None, np.inf
    for s0 in starts:
        r = minimize(fg, s0, jac=True, method="L-BFGS-B", bounds=[(0.0, 1.0)] * d,
                     options={"maxiter": 500, "ftol": 1e-15, "gtol": 1e-12})
        if r.fun < best_f:
            best_u, best_f = np.clip(r.x, 0, 1), float(r.fun)
    return best_u, best_f, float(fs.min())


# --------------------------------------------------------------------------- #
# fit the emulator (54's code path) and freeze it
# --------------------------------------------------------------------------- #

def real_start_set():
    """The n* = 48 grading rows of n0_E through the REAL 54 loader (sobol order)."""
    from analysis.ercot_gp.ercot_gp_loader import load
    X, U, Y, meta = load(["n0_E"], SEATED + CO_REPORTED + ["N1"], DS_PATH)
    sob = pd.to_numeric(meta["sobol_index"], errors="coerce")
    keep = sob.notna() & (sob < N_STAR)
    assert int(keep.sum()) == N_STAR and not meta["suspect"][keep].any()
    idx = X.index[keep][np.argsort(sob[keep].to_numpy())]
    return X.loc[idx], U.loc[idx], Y.loc[idx], meta.loc[idx]


def fit_emulator(write=True, log=print):
    from analysis.ercot_gp import ercot_gp_status as S
    from analysis.ercot_gp.ercot_gp_partb import hyper
    cc = json.load(open(CONFIGS))
    X, U, Y, meta = real_start_set()
    Un = U.to_numpy(float)
    sites = [c.replace("mw_", "").replace("u_", "") for c in U.columns]
    out = {"label": "EMULATOR truth (prompt 66 §1) — NOT data", "generated_utc": now(),
           "fit_code_path": "analysis.ercot_gp.ercot_gp_status.fit (D-1025 FlexGP, bogp.train_gp Adam 700 epochs lr 0.01, "
                            "float32, torch.manual_seed(0)), inferred floor 1e-9 — prompt 54's committed fit",
           "training": {"wave": "n0_E", "n": int(len(U)), "keys": list(map(str, U.index)),
                        "loader": "analysis.ercot_gp.ercot_gp_loader.load (real, prompt 54)",
                        "design_space": os.path.relpath(DS_PATH, ERCOT)},
           "committed_configs_generated_utc": cc.get("generated_utc"), "E-D7_decided": cc.get("E-D7_decided"),
           "n_star": cc["n_star"], "sites": sites, "objectives": {}}
    assert cc["n_star"] == N_STAR
    from scipy.stats import qmc
    Uchk = qmc.Sobol(6, scramble=True, seed=66).random(1024)
    for o in SEATED + CO_REPORTED:
        c = cc["objectives"][o]
        arm = S.Arm(c["arm"], tuple(c["cfg"]), "inferred")
        assert float(c["floor"]) == 0.0 and not c["measured_floor_used"]
        y = Y[o].to_numpy(float)
        gp = S.fit(Un, y, arm, 0.0)
        h = hyper(gp)
        cov = gp.model.covar_module
        p = GPMean.build(Un, y, cov.base_kernel.lengthscale.detach().double().numpy().reshape(-1),
                         float(cov.outputscale.detach().double()), float(gp.lik.noise.detach().double()),
                         float(gp.model.mean_module.constant.detach().double()), gp.mx, gp.sx, gp.my, gp.sy, arm.cfg)
        f = GPMean(p)
        mu_flex, _ = gp.predict_t(Uchk)
        dev = np.abs(f(Uchk) - mu_flex)
        com = c["hyperparameters"]
        ls_c = np.asarray([com["lengthscales_u"][s] for s in sites], float)
        hyp = {"ls_u": dict(zip(sites, h["ls_u"])), "outputscale_sd_t": h["outputscale_sd_t"],
               "noise_sd_raw": h["noise_sd_raw"], "mean_const_std": h["mean_const_std"],
               "noise_at_floor": h["noise_at_floor"]}
        rep = {"ls_u_max_rel_diff": float(np.max(np.abs(np.asarray(h["ls_u"]) / ls_c - 1))),
               "outputscale_rel_diff": float(abs(h["outputscale_sd_t"] / com["outputscale_sd_t"] - 1)),
               "noise_rel_diff": float(abs(h["noise_sd_raw"] / com["noise_sd_raw"] - 1))}
        ustar, fstar, fsob = minimize_fn(f.torch, 6, seed=0)
        umax, fmax_neg, _ = minimize_fn(lambda u: -f.torch(u), 6, seed=1)
        p.update({"objective": o, "role": c["role"], "arm": c["arm"], "hyperparameters": hyp,
                  "committed_hyperparameters": com, "reproduces_committed": rep,
                  "closed_form_vs_flexgp_mean": {"n_check": 1024, "max_abs": float(dev.max()),
                                                 "max_abs_over_B": float(dev.max() / B[o]) if o in B else None,
                                                 "max_abs_over_sy": float(dev.max() / gp.sy)},
                  "f_star": fstar, "u_star": ustar.tolist(), "f_star_sobol_2^14": fsob, "f_max": -fmax_neg,
                  "u_max": umax.tolist(), "y_train_min": float(y.min()), "y_train_max": float(y.max()),
                  "f_train_resid_rms": float(np.sqrt(np.mean((f(Un) - y) ** 2)))})
        out["objectives"][o] = p
        log(f"[emulator] {o} {c['arm']}: ls_u {np.round(h['ls_u'], 4).tolist()} os_sd {h['outputscale_sd_t']:.6g} "
            f"noise_sd {h['noise_sd_raw']:.6g}; reproduces committed {rep}; closed form vs FlexGP max |d| "
            f"{dev.max():.4g}; f* {fstar:.8g} at {np.round(ustar, 4).tolist()} (Sobol min {fsob:.8g})")
    S2 = sigma_c(SEATED)
    out["sigma_c"] = {"ids": SEATED, "matrix": S2.tolist(), "sd": np.sqrt(np.diag(S2)).tolist(),
                      "corr": float(S2[0, 1] / np.sqrt(S2[0, 0] * S2[1, 1])), "source": os.path.relpath(SIGMA_C_CSV, ERCOT),
                      "note": "prompt-63 Seed chatter covariance (LW-shrunk), per-run"}
    Sm = sigma_c(["N4", "R2", "N1"])
    out["monitor_chatter"] = {"N4_sd": float(np.sqrt(Sm[0, 0])), "R2_sd": float(np.sqrt(Sm[1, 1])),
                              "N1_off_sd": float(np.sqrt(Sm[2, 2] + Sm[0, 0] - 2 * Sm[0, 2])),
                              "note": "independent monitor stream default_rng([6666, 99, family, seed_id, scenario, variant]); "
                                      "N1_off chatter sd = sd(eps_N1 - eps_N4) from the Sigma_c N1/N4 block"}
    eps0 = np.random.default_rng(EMU_SEED).multivariate_normal(np.zeros(2), S2, size=N_STAR, method="svd")
    F0 = np.column_stack([GPMean(out["objectives"][o])(Un) for o in SEATED])
    out["start_set"] = {"keys": list(map(str, U.index)), "U": Un.tolist(), "f": F0.tolist(), "eps": eps0.tolist(),
                        "y_obs": (F0 + eps0).tolist(),
                        "f_N4": GPMean(out["objectives"]["N4"])(Un).tolist(),
                        "real_Y": Y[SEATED].to_numpy(float).tolist(),
                        "note": "start-set observations = f(u_i) + eps_i, eps from default_rng(6666) (first draw, 48 x 2)"}
    land = json.load(open(LANDING_R))
    out["R"] = {o: float(land["R"][o]) for o in SEATED}
    out["B"] = B
    if write:
        with open(PARAMS, "w") as fh:
            json.dump(out, fh, indent=1, default=float)
            fh.write("\n")
    return out


_EMU = None


def load_emulator():
    global _EMU
    if _EMU is None:
        P = json.load(open(PARAMS))
        _EMU = {"P": P, "f": {o: GPMean(P["objectives"][o]) for o in SEATED + CO_REPORTED},
                "S2": np.asarray(P["sigma_c"]["matrix"], float), "mon": P["monitor_chatter"],
                "R": np.asarray([P["R"][o] for o in SEATED], float)}
    return _EMU


class Observer:
    """Emulated observations along one experiment stream (common random numbers across methods
    sharing the stream key)."""

    def __init__(self, key: tuple, emu=None):
        self.emu = emu or load_emulator()
        self.key = tuple(int(k) for k in key)
        self.rng = np.random.default_rng([EMU_SEED, *self.key])
        self.rng_mon = np.random.default_rng([EMU_SEED, 99, *self.key])

    def __call__(self, U):
        U = np.atleast_2d(np.asarray(U, float))
        e = self.emu
        F = np.column_stack([e["f"][o](U) for o in SEATED])
        eps = self.rng.multivariate_normal(np.zeros(2), e["S2"], size=len(U), method="svd")
        m = self.rng_mon.standard_normal((len(U), 3))
        fN4 = e["f"]["N4"](U)
        return {"f": F, "eps": eps, "y": F + eps, "f_N4": fN4, "N4": fN4 + e["mon"]["N4_sd"] * m[:, 0],
                "R1": np.zeros(len(U)), "R2": R2_BASE + e["mon"]["R2_sd"] * m[:, 1],
                "N1_off": N1OFF_BASE + e["mon"]["N1_off_sd"] * m[:, 2]}


def true_f(U, emu=None):
    emu = emu or load_emulator()
    U = np.atleast_2d(np.asarray(U, float))
    return np.column_stack([emu["f"][o](U) for o in SEATED])


# --------------------------------------------------------------------------- #
# calibration exactly as 55 computes it (acquire_E._calibration)
# --------------------------------------------------------------------------- #

def calib(y, pm, ps, transform="std"):
    y = np.asarray(y, float)
    t = np.log1p(y) if transform == "log1p" else y
    z = (t - np.asarray(pm, float)) / np.asarray(ps, float)
    cov = int((np.abs(z) <= 1.96).sum())
    n3 = int((np.abs(z) > 3.0).sum())
    return {"mean_z": round(float(z.mean()), 3), "rms_z": round(float(np.sqrt((z ** 2).mean())), 3),
            "cov95": cov, "n_abs_z_gt3": n3, "transform": transform, "C2": bool(cov <= 4), "C3": bool(n3 >= 3)}


# --------------------------------------------------------------------------- #
# single-objective BO (prompt 66 §2) — generic in d and in the truth
# --------------------------------------------------------------------------- #

def set_fit_epochs(epochs):
    """BO-internal GP fit budget: 700 (house, bogp.train_gp default) or LONG_EPOCHS (EXPLORATORY).
    Only the BO's GP changes; the emulator truth is frozen in emulator_E_params.json."""
    import qnehvi_E
    from bogp.gp_model import train_gp as _orig
    qnehvi_E.train_gp = _orig if epochs == 700 else functools.partial(_orig, n_epochs=int(epochs))
    return qnehvi_E


def _gp_summary(obj_gp, sx):
    cov = obj_gp.model.covar_module
    ls = cov.base_kernel.lengthscale.detach().double().numpy().reshape(-1) * np.asarray(sx, float)
    return {"ls_u": ls.tolist(), "outputscale_sd_t": float(np.sqrt(float(cov.outputscale.detach())) * obj_gp.sy),
            "noise_sd_raw": obj_gp.noise_raw(), "loo_rms_z": obj_gp.loo_rms_z()}


def _pm_optimum(fit, d, seed, settings):
    """Posterior-mean optimum of a fitted (negated) ObjGP: optimize_acqf on PosteriorMean."""
    from botorch.acquisition.analytic import PosteriorMean
    from botorch.optim import optimize_acqf
    model = fit["objs"][0].model
    lo = (np.zeros(d) - fit["mx"]) / fit["sx"]
    hi = (np.ones(d) - fit["mx"]) / fit["sx"]
    torch.manual_seed(int(seed))
    xb, _ = optimize_acqf(PosteriorMean(model), bounds=torch.tensor(np.vstack([lo, hi]), dtype=torch.float64), q=1,
                          num_restarts=settings["num_restarts"], raw_samples=settings["raw_samples"])
    u = np.clip(xb.detach().numpy() * fit["sx"] + fit["mx"], 0, 1)
    pm, _ = fit["objs"][0].predict_raw(xb.detach())
    return u[0], float(pm[0])


def so_bo(U0, y0, f0, observe, f_true, f_star, cfg, floor, seed_base, method="bo", settings=None, B_unit=1.0,
          log=print):
    """Single-objective BO (qLogNEI) or random baseline. Minimization.
    U0 (n0, d), y0 (n0,) observed, f0 (n0,) true values at U0; observe(U) -> (y, f) for new rows;
    f_true(U) -> (n,) truth. seed for round k = seed_base + k. Returns the per-round records."""
    import qnehvi_E
    from botorch.acquisition.logei import qLogNoisyExpectedImprovement
    from botorch.optim import optimize_acqf
    from botorch.sampling import SobolQMCNormalSampler
    st = dict(SO, **(settings or {}))
    q, d = st["q"], U0.shape[1]
    U, y, f = np.array(U0, float), np.array(y0, float), np.array(f0, float)
    recs = []

    def snapshot(k, fit, extra):
        ib = int(np.argmin(y))
        r = {"round": k, "n": int(len(y)), "best_obs": float(y[ib]), "best_obs_u": U[ib].tolist(),
             "f_at_best_obs": float(f[ib]), "regret_best_obs_B": float((f[ib] - f_star) / B_unit),
             "gap_obs_B": float((y[ib] - f_star) / B_unit), "min_f_evaluated_B": float((f.min() - f_star) / B_unit)}
        if fit is not None:
            gs = _gp_summary(fit["objs"][0], fit["sx"])
            u_pm, pm = _pm_optimum(fit, d, seed_base + 1000 + k, st)
            r.update({"gp": gs, "pm_opt_u": u_pm.tolist(), "pm_opt_pred": pm,
                      "pm_opt_f": float(f_true(u_pm[None, :])[0]),
                      "regret_pm_opt_B": float((f_true(u_pm[None, :])[0] - f_star) / B_unit)})
        r.update(extra)
        return r

    fit = None
    if method == "bo":
        t0 = time.time()
        torch.manual_seed(seed_base)
        fit = qnehvi_E.fit_models(U, y[:, None], [cfg], [floor])
        fit_s = time.time() - t0
    recs.append(snapshot(0, fit, {"wall_s": 0.0, "fit_s": fit_s if method == "bo" else 0.0}))
    for k in range(1, st["rounds"] + 1):
        t0 = time.time()
        s = int(seed_base + k)
        extra = {"seed": s}
        if method == "bo":
            torch.manual_seed(s)
            o = fit["objs"][0]
            tx = torch.tensor((U - fit["mx"]) / fit["sx"], dtype=torch.float64)
            acq = qLogNoisyExpectedImprovement(model=o.model, X_baseline=tx,
                                               sampler=SobolQMCNormalSampler(sample_shape=torch.Size([st["mc_samples"]]), seed=s),
                                               prune_baseline=True, cache_root=True)
            lo = (np.zeros(d) - fit["mx"]) / fit["sx"]
            hi = (np.ones(d) - fit["mx"]) / fit["sx"]
            with WarnCount() as wc:
                xb, _ = optimize_acqf(acq, bounds=torch.tensor(np.vstack([lo, hi]), dtype=torch.float64), q=q,
                                      num_restarts=st["num_restarts"], raw_samples=st["raw_samples"],
                                      sequential=st["sequential"])
            extra["acq_warnings"] = wc.counts
            xb = xb.detach()
            Unew = np.clip(xb.numpy() * fit["sx"] + fit["mx"], 0.0, 1.0)
            extra["bound_snaps"] = qnehvi_E.snap_bounds(Unew)              # same bound cleanup as 55 (prompt 66 E)
            xb = torch.tensor((Unew - fit["mx"]) / fit["sx"], dtype=torch.float64)
            pm, ps = o.predict_raw(xb)
            acq_s = time.time() - t0
        else:
            Unew = np.random.default_rng(s).uniform(size=(q, d))
            pm = ps = None
            acq_s = 0.0
        ynew, fnew = observe(Unew)
        if pm is not None:
            extra["calibration"] = calib(ynew, pm, ps)
            extra["pred_mean"], extra["pred_sd"] = np.asarray(pm).tolist(), np.asarray(ps).tolist()
        U = np.vstack([U, Unew]); y = np.concatenate([y, ynew]); f = np.concatenate([f, fnew])
        extra.update({"u_new": Unew.tolist(), "y_new": np.asarray(ynew).tolist(), "f_new": np.asarray(fnew).tolist(),
                      "acq_s": acq_s})
        t1 = time.time()
        if method == "bo":
            torch.manual_seed(s)
            fit = qnehvi_E.fit_models(U, y[:, None], [cfg], [floor])      # refit: hyperparameters re-estimated
        extra["fit_s"] = time.time() - t1
        extra["wall_s"] = time.time() - t0
        recs.append(snapshot(k, fit, extra))
        log(f"  r{k}: best_obs regret {recs[-1]['regret_best_obs_B']:.3f} B"
            + (f", pm-opt regret {recs[-1]['regret_pm_opt_B']:.3f} B, cal {extra['calibration']}" if method == "bo" else "")
            + f" ({extra['wall_s']:.1f} s)")
    return recs


def run_single(obj, seed_id, method, variant, log=print):
    emu = load_emulator()
    P = emu["P"]
    j = SEATED.index(obj)
    st0 = P["start_set"]
    U0 = np.asarray(st0["U"], float)
    Y0 = np.asarray(st0["y_obs"], float)
    F0 = np.asarray(st0["f"], float)
    c = P["objectives"][obj]
    cfg = tuple(c["cfg"])
    floor = 1e-9                                                           # committed floor 0 -> inferred-only 1e-9
    set_fit_epochs(LONG_EPOCHS if variant == "long" else 700)
    obs = Observer((FAMILY[f"single_{obj}"], seed_id, 0, 0))              # same stream for BO and random (CRN)

    def observe(U):
        o = obs(U)
        return o["y"][:, j], o["f"][:, j]

    fj = emu["f"][obj]
    t0 = time.time()
    log(f"[single EMULATOR] {obj} seed_id {seed_id} {method} variant {variant}")
    recs = so_bo(U0, Y0[:, j], F0[:, j], observe, lambda U: fj(U), float(c["f_star"]), cfg, floor,
                 SINGLE_SEED_BASE + 100 * seed_id, method=method, B_unit=B[obj], log=log)
    out = {"label": "EMULATOR", "kind": "single", "objective": obj, "seed_id": seed_id, "method": method,
           "variant": variant, "fit_epochs": LONG_EPOCHS if variant == "long" else 700, "cfg": list(cfg),
           "floor": floor, "f_star": c["f_star"], "B": B[obj], "settings": SO,
           "acq": "qLogNoisyExpectedImprovement (botorch), SobolQMCNormalSampler(128, seed s), prune_baseline, cache_root"
                  if method == "bo" else "uniform random u ~ default_rng(s), 8 per round",
           "seed_rule": "s = 20261007 + 100 * seed_id + k", "noise_stream": [EMU_SEED, FAMILY[f"single_{obj}"], seed_id, 0, 0],
           "records": recs, "wall_s": time.time() - t0, "finished_utc": now()}
    os.makedirs(os.path.join(RUNS, "single"), exist_ok=True)
    p = os.path.join(RUNS, "single", f"EMU_single_{variant}_{obj}_{method}_s{seed_id}.json")
    with open(p, "w") as fh:
        json.dump(out, fh, indent=1, default=float)
    return out


# --------------------------------------------------------------------------- #
# multi-objective: 55's machinery (acquire_E) on the emulator
# --------------------------------------------------------------------------- #

EMU_LOADER_LABEL = "real(n0_E: analysis.ercot_gp.ercot_gp_loader.load; Y replaced by the EMULATED start values)+EMULATOR wave tables"


class EmuLoader:
    """Contract 6.1 signature. n0_E rows: the REAL 54 loader (keys, U, meta, identity gate); Y replaced
    by the emulated start-set observations (f + eps, emulator_E_params.json). Emulated waves: the
    design_matrix + objectives_EMULATOR.csv written in <root>/waves/<wave>/."""

    def __init__(self):
        P = load_emulator()["P"]
        self.start = dict(zip(P["start_set"]["keys"], np.asarray(P["start_set"]["y_obs"], float)))
        self.calls = 0

    def __call__(self, waves, objectives=None, design_space=DS_PATH, extr=None, floors=None, waves_dir=None):
        from analysis.ercot_gp.ercot_gp_loader import load as real_load
        self.calls += 1
        objectives = list(objectives or SEATED)
        assert objectives == SEATED, objectives
        ds = json.load(open(design_space))
        cols = list(ds["x_columns"])
        pmax = np.asarray([float(s["gen_pmax"]) for s in ds["sites"]], float)
        parts = []
        for w in waves:
            if w == "n0_E":
                X, U, Y, meta = real_load(["n0_E"], objectives, design_space)
                for k in Y.index:
                    if k in self.start:
                        Y.loc[k, objectives] = self.start[k]
                meta = meta.copy()
                meta["identity"] = "v3 (real) / Y EMULATED"
                assert set(self.start) <= set(Y.index), "start-set keys missing from the real n0_E load"
                parts.append((X, U, Y, meta))
                continue
            wdir = os.path.join(waves_dir, w)
            dm = pd.read_csv(os.path.join(wdir, "design_matrix.csv"), dtype={"oat_site": str}, float_precision="round_trip")
            ob = pd.read_csv(os.path.join(wdir, "objectives_EMULATOR.csv"), float_precision="round_trip")
            m = dm.merge(ob, on="index", how="inner", validate="one_to_one")
            keys = [f"{w}:{int(i)}" for i in m["index"]]
            X = pd.DataFrame(m[cols].to_numpy(float), columns=cols, index=pd.Index(keys, name="key"))
            U = X / pmax                                     # column names as the real loader (mw_*)
            Y = pd.DataFrame(m[objectives].to_numpy(float), columns=objectives, index=X.index)
            meta = pd.DataFrame({"key": keys, "wave": w, "index": m["index"].astype(int).to_numpy(), "tier": "bo",
                                 "sobol_index": "", "identity": "EMULATOR", "G_run_usd": np.nan,
                                 "R1": m["R1"].to_numpy(float), "R2": m["R2"].to_numpy(float),
                                 "suspect": m["suspect"].astype(bool).to_numpy()}, index=X.index)
            parts.append((X, U, Y, meta))
        X = pd.concat([p[0] for p in parts]); U = pd.concat([p[1] for p in parts])
        Y = pd.concat([p[2] for p in parts]); meta = pd.concat([p[3] for p in parts])
        meta.attrs["refused"] = {}
        meta.attrs["n_refused"] = 0
        meta.attrs["floors"] = floors
        meta.attrs["loader"] = EMU_LOADER_LABEL
        return X, U, Y, meta


def emu_cfg(variant, scenario):
    cfg = json.load(open(ARMS_E))
    for k in ("design_space", "committed_configs", "landing_R", "noise_json", "noise_exact_cov", "noise_perturbed_cov"):
        cfg[k] = os.path.join(ERCOT, cfg[k])                          # absolute: the emulator root is analysis/emulator_E
    assert os.path.abspath(cfg["design_space"]) == os.path.abspath(DS_PATH), "arms_E.json must name the dated design space"
    assert cfg["objectives"] == SEATED
    cfg["part"] = "EMULATOR"
    cfg["n0_tier_provisional"] = N_STAR
    cfg["repo_branch"] = "NONE (emulator: never committed or pushed by the machinery)"
    a = dict(cfg["arms"]["qnehvi"])
    a.update({"dir": f"lanes/{variant}/{scenario}", "lane_dir_pattern": f"lanes/{variant}/{scenario}/s{{seed}}",
              "round_wave_pattern": f"methods_E_EMU_{variant}_{scenario}_s{{seed}}_r{{k}}"})
    cfg["arms"] = {"qnehvi": a}
    return cfg


def ensure_emu_root():
    gi = os.path.join(HERE, ".gitignore")
    want = "extracts/methods_E_*/**/*.csv.gz"
    if not os.path.isfile(gi) or want not in [ln.strip() for ln in open(gi)]:
        with open(gi, "a") as fh:
            fh.write("# wave_writer_E.assert_gitignore (55) checks this line on the emulator root\n" + want + "\n")
    os.makedirs(os.path.join(HERE, "waves"), exist_ok=True)


def hv2d(Y, R):
    """Exact 2-D hypervolume (minimization) of the rows strictly below R."""
    Y = np.atleast_2d(np.asarray(Y, float))
    Y = Y[np.all(Y < R, axis=1)]
    if len(Y) == 0:
        return 0.0
    Y = Y[np.lexsort((Y[:, 1], Y[:, 0]))]
    best = np.minimum.accumulate(Y[:, 1])
    keep = np.concatenate([[True], best[1:] < best[:-1]])
    P = Y[keep]
    P[:, 1] = best[keep]
    x_next = np.append(P[1:, 0], R[0])
    return float(np.sum((x_next - P[:, 0]) * (R[1] - P[:, 1])))


def write_emulated_wave(lane, k, obs: Observer, scenario):
    wdir = os.path.join(lane.root, "waves", lane.wave(k))
    dm = pd.read_csv(os.path.join(wdir, "design_matrix.csv"), float_precision="round_trip").sort_values("index")
    U = dm[lane.ds.u_columns].to_numpy(float)
    o = obs(U)
    R1 = o["R1"].copy()
    inj = INJECT[scenario] if k == 1 else {}
    for i, v in inj.items():
        R1[int(i) - 1] = float(v)
    tab = pd.DataFrame({"index": dm["index"].astype(int).to_numpy(), "V1": o["y"][:, 0], "E1": o["y"][:, 1],
                        "N4": o["N4"], "R1": R1, "R2": o["R2"], "N1_off": o["N1_off"], "suspect": False,
                        "f_V1": o["f"][:, 0], "f_E1": o["f"][:, 1], "f_N4": o["f_N4"],
                        "eps_V1": o["eps"][:, 0], "eps_E1": o["eps"][:, 1],
                        "injected_shed": [int(i) in inj for i in dm["index"].astype(int)]})
    tab.to_csv(os.path.join(wdir, "objectives_EMULATOR.csv"), index=False, float_format="%.17g")
    with open(os.path.join(wdir, "EMULATOR.txt"), "w") as fh:
        fh.write("EMULATOR wave (prompt 66): objectives_EMULATOR.csv = f_j(u) + Sigma_c chatter from the committed GPs; "
                 "no PCM ran; never submit, never ingest into a real ledger.\n")
    return tab


def run_multi(scenario, seed_id, variant, fresh=True, log=print):
    import acquire_E as ae
    emu = load_emulator()
    set_fit_epochs(LONG_EPOCHS if variant == "long" else 700)
    ensure_emu_root()
    cfg = emu_cfg(variant, scenario)
    loader = EmuLoader()
    lane = ae.Lane(HERE, cfg, "qnehvi", seed_id, loader=(loader, EMU_LOADER_LABEL))
    if fresh:
        shutil.rmtree(lane.dir, ignore_errors=True)
        for k in range(1, cfg["hard_cap"] + 1):
            shutil.rmtree(os.path.join(HERE, "waves", lane.wave(k)), ignore_errors=True)
    obs = Observer((FAMILY["multi"], seed_id, SCEN[scenario], VARIANT[variant]))
    R = emu["R"]
    P = emu["P"]
    Y0 = np.asarray(P["start_set"]["y_obs"], float)
    F0 = np.asarray(P["start_set"]["f"], float)
    import tau_E
    tres = tau_E.tau_res(Y0, R, emu["S2"])
    log(f"[multi EMULATOR] {scenario} seed_id {seed_id} variant {variant}: tau_res {tres['tau_res']:.6g}")
    t0 = time.time()
    led = ae.cmd_init(lane, bo_gp_sha=ce.bogp_sha())
    init_s = time.time() - t0
    rounds = []
    Facc, Yacc, Vacc = [F0], [Y0], [np.zeros(len(F0), bool)]
    halted = False
    for k in range(1, cfg["hard_cap"] + 1):
        r = {"round": k}
        t0 = time.time()
        try:
            with WarnCount() as wc:
                ae.propose_round(lane, k)
        except SystemExit as ex:                                  # HALT refusal path
            r["propose_refused"] = str(ex)
            rounds.append(r)
            break
        r["propose_warnings"] = wc.counts
        r["propose_s"] = time.time() - t0
        rec = ae.load_records(lane.dir)[str(k)]
        r["qnehvi_s"] = rec.get("qnehvi_seconds")
        tab = write_emulated_wave(lane, k, obs, scenario)
        ok, why, info = ae.ingest_gate(lane, k)
        r["C1_ok"], r["C1_reason"], r["C1_info"] = bool(ok), why, info
        if not ok:
            rounds.append(r)
            log(f"  r{k}: C1 FAILED: {why}")
            break
        t1 = time.time()
        led, halted = ae.grade_round(lane, k)
        r["grade_s"] = time.time() - t1
        r["wall_s"] = time.time() - t0
        e = led["entries"][-1]
        rec = ae.load_records(lane.dir)[str(k)]
        viol = tab["R1"].to_numpy(float) > lane.violation_mwh
        Facc.append(tab[["f_V1", "f_E1"]].to_numpy(float)); Yacc.append(tab[["V1", "E1"]].to_numpy(float)); Vacc.append(viol)
        Fa, Ya, Va = np.vstack(Facc), np.vstack(Yacc), np.concatenate(Vacc)
        hv_true = hv2d(Fa[~Va], R)
        hv_obs = hv2d(Ya[~Va], R)
        assert abs(hv_obs - e["hv"]) <= 1e-9 * max(1.0, abs(e["hv"])), ("ledger HV != recomputed", hv_obs, e["hv"])
        r.update({"hv": e["hv"], "gain": e["gain"], "gain_tau_joint": e["gain_tau_joint"],
                  "would_stop_joint": e["would_stop_joint"], "would_stop_marginal": e["would_stop_marginal"],
                  "gain_over_tau_res": (e["gain"] / tres["tau_res"]) if tres["tau_res"] > 0 else None,
                  "hv_true_f": hv_true, "n": e["n"], "n_hv": e["n_hv"], "violations": e["violations"],
                  "suspects": e["suspects"], "r2_flag": e["r2_flag"], "r2_max": rec.get("r2_max_mwh"),
                  "C2": e["C2_review"], "C3": e["C3_review"], "calibration": rec.get("calibration"),
                  "guardrail_mode_after": led["guardrail_mode"], "constraint_used": rec.get("settings", {}).get("constraint"),
                  "n1_off_max": float(tab["N1_off"].max()),
                  "n1_off_flag_a": bool((tab["N1_off"] - N1OFF_BASE).max() >= N1OFF_FLAG_A),
                  "N4_mean": float(tab["N4"].mean()), "halt": bool(halted), "decision": e["decision"],
                  "loo_rms_z": rec.get("loo_rms_z"), "noise_raw": rec.get("noise_raw")})
        rounds.append(r)
        log(f"  r{k}: hv {e['hv']:.6g} (true {hv_true:.6g}) gain/tau_res {r['gain_over_tau_res']} C1 ok C2 {e['C2_review']} "
            f"C3 {e['C3_review']} viol {e['violations']} mode->{led['guardrail_mode']} constraint {r['constraint_used']} "
            f"halt {halted} ({r['wall_s']:.1f} s)")
        if halted:
            # the machinery refuses to propose while HALT_FOR_DECISION.md exists: exercise the refusal
            try:
                ae.propose_round(lane, k + 1)
                rounds.append({"round": k + 1, "propose_refused": "NOT REFUSED (unexpected)"})
            except SystemExit as ex:
                rounds.append({"round": k + 1, "propose_refused": str(ex)})
            break
    # proposals per round (u) + the constrained-branch record from r2
    recs = ae.load_records(lane.dir)
    led = ae.load_ledger(lane.dir)
    out = {"label": "EMULATOR", "kind": "multi", "scenario": scenario, "seed_id": seed_id, "variant": variant,
           "fit_epochs": LONG_EPOCHS if variant == "long" else 700, "lane_dir": os.path.relpath(lane.dir, HERE),
           "init_s": init_s, "tau_exact": led["tau"], "tau_res": tres, "R": R.tolist(), "hv0": led["entries"][0]["hv"],
           "hv0_true_f": hv2d(F0, R), "n0_tier": led["n0_tier"], "n0_source": led["n0_source"], "loader": led["loader"],
           "configs_source": led["configs_source"], "acq_seeds": {k: v.get("acq_seed") for k, v in recs.items()},
           "settings": {k: v.get("settings") for k, v in recs.items()},
           "designs_u": {k: v.get("designs_u") for k, v in recs.items()},
           "guardrail_mode": led["guardrail_mode"], "guardrail_flipped_at_round": led["guardrail_flipped_at_round"],
           "halt": led["halt"], "halt_file": os.path.isfile(ae.halt_path(lane.dir)),
           "first_fire_round": led["first_fire_round"], "rounds": rounds,
           "noise_stream": [EMU_SEED, FAMILY["multi"], seed_id, SCEN[scenario], VARIANT[variant]],
           "loader_calls": loader.calls, "finished_utc": now()}
    os.makedirs(os.path.join(RUNS, "multi"), exist_ok=True)
    with open(os.path.join(RUNS, "multi", f"EMU_multi_{variant}_{scenario}_s{seed_id}.json"), "w") as fh:
        json.dump(out, fh, indent=1, default=float)
    return out


# --------------------------------------------------------------------------- #
# random-48 pool (prompt 34 percentile) and the emulator front
# --------------------------------------------------------------------------- #

def percentile(bo_hv, sub_hvs):
    """prompt 34: fraction of random subsets with HV below BO's; ties within 1e-12 relative count 1/2."""
    s = np.asarray(sub_hvs, float)
    tie = np.abs(s - bo_hv) <= 1e-12 * max(1.0, abs(bo_hv))
    return float(((s < bo_hv) & ~tie).mean() + 0.5 * tie.mean())


def random_pool(log=print):
    emu = load_emulator()
    P = emu["P"]
    R = emu["R"]
    Y0 = np.asarray(P["start_set"]["y_obs"], float)
    F0 = np.asarray(P["start_set"]["f"], float)
    obs = Observer((FAMILY["pool"], 0, 0, 0))
    Upool = np.random.default_rng([EMU_SEED, FAMILY["pool"], 1]).uniform(size=(48, 6))
    o = obs(Upool)
    Yp, Fp = o["y"], o["f"]
    rng = np.random.default_rng(SUBSET_SEED)
    t0 = time.time()
    sub = {}
    for k in (1, 2, 3, 4):
        m = 8 * k
        hv = np.empty(N_SUBSETS)
        for i in range(N_SUBSETS):
            idx = rng.choice(48, size=m, replace=False)
            hv[i] = hv2d(np.vstack([Y0, Yp[idx]]), R)
        sub[k] = hv
        log(f"[pool] {m}-subsets: p10/p50/p90 {np.percentile(hv, [10, 50, 90]).round(1).tolist()} ({time.time() - t0:.0f} s)")
    boot = np.empty((N_BOOT, N_BOOT_SUBSETS))
    for b in range(N_BOOT):
        pos = rng.integers(0, 48, size=48)                 # resample the pool with replacement (by position)
        for i in range(N_BOOT_SUBSETS):
            idx = pos[rng.choice(48, size=32, replace=False)]
            boot[b, i] = hv2d(np.vstack([Y0, Yp[idx]]), R)
    log(f"[pool] bootstrap {N_BOOT} x {N_BOOT_SUBSETS} done ({time.time() - t0:.0f} s)")
    os.makedirs(RUNS_BIG, exist_ok=True)
    np.savez_compressed(os.path.join(RUNS_BIG, "EMU_random_pool_subsets.npz"), **{f"k{k}": v for k, v in sub.items()}, boot=boot)
    out = {"label": "EMULATOR", "U": Upool.tolist(), "y": Yp.tolist(), "f": Fp.tolist(),
           "hv_all48_obs": hv2d(np.vstack([Y0, Yp]), R), "hv_all48_true": hv2d(np.vstack([F0, Fp]), R),
           "subset_quantiles": {k: np.percentile(v, [10, 50, 90]).tolist() for k, v in sub.items()},
           "sampler_seed": SUBSET_SEED, "n_subsets": N_SUBSETS, "n_boot": N_BOOT, "n_boot_subsets": N_BOOT_SUBSETS,
           "rule": "prompt 34 §3.1: p = fraction of random 8k-subsets (k = rounds) of the 48-pool with HV(starts U subset) "
                   "below the lane's HV (ties 1/2); interval at k = 4 = 5th-95th pct of p over 1,000 pool resamples "
                   "(2,000 subsets each, drawn by position)", "wall_s": time.time() - t0}
    with open(os.path.join(RUNS, "EMU_random_pool.json"), "w") as fh:
        json.dump(out, fh, indent=1, default=float)
    return out


def pareto_mask(Y):
    Y = np.asarray(Y, float)
    o = np.lexsort((Y[:, 1], Y[:, 0]))
    keep = np.zeros(len(Y), bool)
    best = np.inf
    for i in o:
        if Y[i, 1] < best:
            keep[i] = True
            best = Y[i, 1]
    return keep


def emulator_front(log=print):
    from scipy.stats import qmc
    emu = load_emulator()
    R = emu["R"]
    S = qmc.Sobol(6, scramble=True, seed=6614).random(2 ** 14)
    F = true_f(S)
    m = pareto_mask(F)
    out = {"label": "EMULATOR", "n_sobol": 2 ** 14, "sobol_seed": 6614, "hv_front": hv2d(F, R),
           "front": F[m][np.argsort(F[m][:, 0])].tolist(), "front_u": S[m][np.argsort(F[m][:, 0])].tolist(),
           "n_front": int(m.sum()), "f_ranges": {"V1": [float(F[:, 0].min()), float(F[:, 0].max())],
                                                 "E1": [float(F[:, 1].min()), float(F[:, 1].max())]}}
    # polished reference (reported beside the spec's Sobol front): + the 64 box vertices + L-BFGS
    # scalarizations (weighted sum and augmented Chebyshev, 49 weights each, ranges normalised)
    V = np.array(np.meshgrid(*[[0.0, 1.0]] * 6)).reshape(6, -1).T
    lo, span = F.min(0), F.max(0) - F.min(0)
    fV, fE = emu["f"]["V1"].torch, emu["f"]["E1"].torch
    extra_u = [V]
    for w in np.linspace(0.02, 0.98, 49):
        for kind in ("ws", "cheb"):
            def g(u, w=w, kind=kind):
                a = (fV(u) - lo[0]) / span[0]
                b = (fE(u) - lo[1]) / span[1]
                if kind == "ws":
                    return w * a + (1 - w) * b
                return torch.maximum(w * a, (1 - w) * b) + 0.01 * (a + b)
            u_, _, _ = minimize_fn(g, 6, seed=int(w * 1000), n_sobol=2 ** 12, n_starts=8)
            extra_u.append(u_[None, :])
    Ux = np.vstack([S] + extra_u)
    Fx = true_f(Ux)
    mx = pareto_mask(Fx)
    out.update({"hv_front_polished": hv2d(Fx, R), "n_front_polished": int(mx.sum()),
                "front_polished": Fx[mx][np.argsort(Fx[mx][:, 0])].tolist(),
                "polish_rule": "Sobol 2^14 + 64 box vertices + 2 x 49 L-BFGS-B scalarizations (weighted sum, augmented "
                               "Chebyshev rho 0.01) on range-normalised (f_V1, f_E1)",
                "f_star": {o: emu["P"]["objectives"][o]["f_star"] for o in SEATED}})
    log(f"[front] HV(front, R) = {out['hv_front']:.6g}; {out['n_front']} non-dominated of 2^14; "
        f"polished {out['hv_front_polished']:.6g} ({out['hv_front'] / out['hv_front_polished']:.4f} of polished)")
    with open(os.path.join(RUNS, "EMU_front.json"), "w") as fh:
        json.dump(out, fh, indent=1, default=float)
    return out


# --------------------------------------------------------------------------- #
# prompt 66 review additions (A1-A6): r0 plug-in, best-known front, matched-budget
# baselines, calibration split by start-set hull, seed overlap
# --------------------------------------------------------------------------- #

VERTICES = np.array(np.meshgrid(*[[0.0, 1.0]] * 6)).reshape(6, -1).T
N_REP = 1000
BASE_SEED = 20261166


def in_hull(P, X):
    """bool per row of X: inside the convex hull of the rows of P (LP feasibility)."""
    from scipy.optimize import linprog
    P = np.asarray(P, float)
    A = np.vstack([P.T, np.ones(len(P))])
    out = []
    for x in np.atleast_2d(X):
        r = linprog(np.zeros(len(P)), A_eq=A, b_eq=np.append(x, 1.0), bounds=[(0, None)] * len(P), method="highs")
        out.append(bool(r.status == 0))
    return np.asarray(out)


def _pm_torch(objgp, mx, sx):
    """raw-unit posterior mean of a (negated) ObjGP as a differentiable function of u."""
    mxt, sxt = torch.tensor(mx, dtype=torch.float64), torch.tensor(sx, dtype=torch.float64)

    def f(u):
        m = objgp.model(((u - mxt) / sxt)).mean
        return -m * objgp.sy + objgp.my
    return f


def r0_plugin(variant="house", log=print):
    """GPs fitted on the start set only (the 55 model, committed cfg): per-objective posterior-mean optimum regret
    and the plug-in (posterior-mean) Pareto front."""
    from scipy.stats import qmc
    qn = set_fit_epochs(LONG_EPOCHS if variant == "long" else 700)
    emu = load_emulator()
    P = emu["P"]
    U0 = np.asarray(P["start_set"]["U"], float)
    Y0 = np.asarray(P["start_set"]["y_obs"], float)
    cfgs = [tuple(P["objectives"][o]["cfg"]) for o in SEATED]
    torch.manual_seed(20261006)
    fit = qn.fit_models(U0, Y0, cfgs, [1e-9, 1e-9])
    out = {"variant": variant, "objectives": {}}
    fns = []
    for j, o in enumerate(SEATED):
        og = fit["objs"][j]
        og.model.eval()
        fn = _pm_torch(og, fit["mx"], fit["sx"])
        fns.append(fn)
        u, v, _ = minimize_fn(fn, 6, seed=j, n_sobol=2 ** 12, n_starts=16)
        reg = (float(emu["f"][o](u[None, :])[0]) - P["objectives"][o]["f_star"]) / B[o]
        out["objectives"][o] = {"pm_opt_u": u.tolist(), "pm_opt_pred": v, "regret_B": reg,
                                "noise_sd_raw": og.noise_raw(), "ls_u": (og.model.covar_module.base_kernel.lengthscale
                                                                         .detach().numpy().reshape(-1) * fit["sx"]).tolist()}
    S = qmc.Sobol(6, scramble=True, seed=6615).random(2 ** 14)
    cand = [S, VERTICES]
    with torch.no_grad():
        Ms = np.column_stack([fn(torch.tensor(np.vstack(cand), dtype=torch.float64)).numpy() for fn in fns])
    lo, span = Ms.min(0), Ms.max(0) - Ms.min(0)
    extra = []
    for w in np.linspace(0.02, 0.98, 49):
        for kind in ("ws", "cheb"):
            def g(u, w=w, kind=kind):
                a = (fns[0](u) - lo[0]) / span[0]
                b = (fns[1](u) - lo[1]) / span[1]
                return w * a + (1 - w) * b if kind == "ws" else torch.maximum(w * a, (1 - w) * b) + 0.01 * (a + b)
            u_, _, _ = minimize_fn(g, 6, seed=int(w * 1000) + 7, n_sobol=2 ** 10, n_starts=4)
            extra.append(u_)
    Uc = np.vstack(cand + [np.asarray(extra)])
    with torch.no_grad():
        Mc = np.column_stack([fn(torch.tensor(Uc, dtype=torch.float64)).numpy() for fn in fns])
    m = pareto_mask(Mc)
    order = np.argsort(Mc[m][:, 0])
    out["plugin_front_u"] = Uc[m][order].tolist()
    out["plugin_front_pred"] = Mc[m][order].tolist()
    log(f"[r0 plug-in {variant}] regret V1 {out['objectives']['V1']['regret_B']:.4f} B, E1 "
        f"{out['objectives']['E1']['regret_B']:.4f} B; plug-in front {int(m.sum())} designs")
    return out


def _hv_traj(F0, Fd, R, q=8, rounds=4):
    return [hv2d(np.vstack([F0, Fd[:q * k]]), R) for k in range(rounds + 1)]


def baselines(plug, log=print):
    """Matched budget (8 per round x 4, same 48 starts), true-f HV per round; N_REP replicates each."""
    emu = load_emulator()
    R = emu["R"]
    F0 = np.asarray(emu["P"]["start_set"]["f"], float)
    rng = np.random.default_rng(BASE_SEED)
    U_pf = np.asarray(plug["plugin_front_u"], float)
    out = {}
    designs = {}
    # (i) uniform, (ii) random vertices (32 of 64 without replacement), (iii-r) random 32 of the plug-in front
    for name in ("uniform", "vertices", "plugin_random"):
        H = np.empty((N_REP, 5))
        allU = []
        for r in range(N_REP):
            if name == "uniform":
                U = rng.uniform(size=(32, 6))
            elif name == "vertices":
                U = VERTICES[rng.choice(64, size=32, replace=False)]
            else:
                U = U_pf[rng.choice(len(U_pf), size=min(32, len(U_pf)), replace=False)]
            H[r] = _hv_traj(F0, true_f(U), R)
            allU.append(U)
        out[name] = H.tolist()
        designs[name] = np.vstack(allU)
        log(f"[baseline] {name}: HV r4 p5/p50/p95 {np.percentile(H[:, 4], [5, 50, 95]).round(-9).tolist()}")
    # (iii) deterministic plug-in exploit: 32 designs spread along the plug-in front (quantiles of predicted V1);
    # round k gets every 4th starting at k-1, so each round spans the front. No exploration.
    idx = np.unique(np.round(np.linspace(0, len(U_pf) - 1, 32)).astype(int))
    Ud = U_pf[idx]
    Ud = np.vstack([Ud[k::4] for k in range(4)])
    out["plugin_spread"] = [_hv_traj(F0, true_f(Ud), R)]
    designs["plugin_spread"] = Ud
    return out, designs


def best_known_front(extra_U, log=print):
    """Non-dominated set (true f) of Sobol 2^14 + vertices + scalarizations (EMU_front.json polished front) +
    EVERY design evaluated by any lane, single run or baseline."""
    emu = load_emulator()
    R = emu["R"]
    fr = json.load(open(os.path.join(RUNS, "EMU_front.json")))
    parts = [np.asarray(fr["front_polished"], float)]
    srcs = {"polished_front": len(parts[0])}
    for d in glob.glob(os.path.join(HERE, "waves", "methods_E_EMU_*", "design_matrix.csv")):
        dm = pd.read_csv(d, float_precision="round_trip")
        parts.append(true_f(dm[[c for c in dm.columns if c.startswith("u_")]].to_numpy(float)))
    srcs["lane_waves"] = len(glob.glob(os.path.join(HERE, "waves", "methods_E_EMU_*")))
    for p in glob.glob(os.path.join(RUNS, "single", "*.json")):
        d = json.load(open(p))
        U = [u for r in d["records"][1:] for u in r["u_new"]]
        parts.append(true_f(np.asarray(U, float)))
    pool = json.load(open(os.path.join(RUNS, "EMU_random_pool.json")))
    parts.append(np.asarray(pool["f"], float))
    parts.append(np.asarray(emu["P"]["start_set"]["f"], float))
    for k, U in extra_U.items():
        parts.append(true_f(U))
    F = np.vstack(parts)
    m = pareto_mask(F)
    hvb = hv2d(F[m], R)
    hv_pol = fr["hv_front_polished"]
    hv_pol_bo = hv2d(np.vstack([parts[0]] + parts[1:1 + srcs["lane_waves"]]), R)
    log(f"[best-known] HV {hvb:.6g} = {hvb / hv_pol:.4f} x polished; polished U lane designs {hv_pol_bo / hv_pol:.4f} x; "
        f"Sobol {fr['hv_front'] / hvb:.4f} of best-known")
    return {"hv_best_known": hvb, "hv_polished": hv_pol, "hv_sobol": fr["hv_front"],
            "best_over_polished": hvb / hv_pol, "polished_plus_lane_designs_over_polished": hv_pol_bo / hv_pol,
            "sobol_over_best": fr["hv_front"] / hvb, "front": F[m][np.argsort(F[m][:, 0])].tolist(),
            "n_points": int(len(F)), "sources": srcs,
            "rule": "non-dominated set (true f) of Sobol 2^14 + 64 vertices + 98 scalarizations + every design evaluated "
                    "by any lane, single run, random pool or matched-budget baseline; a LOWER bound on the true front"}


def calib_split(log=print):
    """Per batch: fraction of designs outside the start-set hull (u); cov95 / rms z inside vs outside."""
    emu = load_emulator()
    U0 = np.asarray(emu["P"]["start_set"]["U"], float)
    rows = []

    def stats(z):
        z = np.asarray(z, float)
        if len(z) == 0:
            return None, None
        return int((np.abs(z) <= 1.96).sum()), float(np.sqrt(np.mean(z ** 2)))

    for p in sorted(glob.glob(os.path.join(RUNS, "single", "*_bo_*.json"))):
        d = json.load(open(p))
        for r in d["records"][1:]:
            U = np.asarray(r["u_new"], float)
            z = (np.asarray(r["y_new"]) - np.asarray(r["pred_mean"])) / np.asarray(r["pred_sd"])
            h = in_hull(U0, U)
            ci, ri = stats(z[h]); co, ro = stats(z[~h])
            rows.append({"kind": "single", "variant": d["variant"], "scenario": "", "objective": d["objective"],
                         "seed_id": d["seed_id"], "round": r["round"], "n_outside_hull": int((~h).sum()),
                         "frac_outside_hull": float((~h).mean()), "n_exact_vertex": int(np.all((U == 0) | (U == 1), 1).sum()),
                         "cov95_inside": ci, "n_inside": int(h.sum()), "rms_z_inside": ri,
                         "cov95_outside": co, "rms_z_outside": ro, "cov95": r["calibration"]["cov95"],
                         "C2": r["calibration"]["C2"]})
    for w in sorted(glob.glob(os.path.join(HERE, "waves", "methods_E_EMU_*"))):
        name = os.path.basename(w)
        _, _, _, var, sc, sd, rk = name.split("_")
        dm = pd.read_csv(os.path.join(w, "design_matrix.csv"), float_precision="round_trip").sort_values("index")
        ob = pd.read_csv(os.path.join(w, "objectives_EMULATOR.csv")).sort_values("index")
        pr = pd.read_csv(os.path.join(w, "predictions.csv")).sort_values("index")
        U = dm[[c for c in dm.columns if c.startswith("u_")]].to_numpy(float)
        h = in_hull(U0, U)
        for o in SEATED:
            z = (ob[o].to_numpy(float) - pr[f"{o}_pred_mean"].to_numpy(float)) / pr[f"{o}_pred_sd"].to_numpy(float)
            ci, ri = stats(z[h]); co, ro = stats(z[~h])
            cov = int((np.abs(z) <= 1.96).sum())
            rows.append({"kind": "multi", "variant": var, "scenario": sc, "objective": o, "seed_id": int(sd[1:]),
                         "round": int(rk[1:]), "n_outside_hull": int((~h).sum()), "frac_outside_hull": float((~h).mean()),
                         "n_exact_vertex": int(np.all((U == 0) | (U == 1), 1).sum()),
                         "cov95_inside": ci, "n_inside": int(h.sum()), "rms_z_inside": ri, "cov95_outside": co,
                         "rms_z_outside": ro, "cov95": cov, "C2": bool(cov <= 4)})
    df = pd.DataFrame(rows)
    log(f"[hull] batches {len(df)}; mean fraction outside the start-set hull {df['frac_outside_hull'].mean():.3f}")
    return df


def seed_overlap(variant="house", scenario="s0", seeds=(0, 1, 2, 3, 4), log=print):
    """E-D4 statistics across the seed lanes of one scenario."""
    emu = load_emulator()
    U0 = np.asarray(emu["P"]["start_set"]["U"], float)
    lanes = {}
    for s in seeds:
        lanes[s] = []
        for k in range(1, 5):
            dm = pd.read_csv(os.path.join(HERE, "waves", f"methods_E_EMU_{variant}_{scenario}_s{s}_r{k}", "design_matrix.csv"),
                             float_precision="round_trip").sort_values("index")
            lanes[s].append(dm[[c for c in dm.columns if c.startswith("u_")]].to_numpy(float))
    key = lambda U: {tuple(r) for r in np.round(U, 10).tolist()}  # noqa: E731
    per_round = []
    for k in range(4):
        allU = np.vstack([lanes[s][k] for s in seeds])
        per_round.append({"round": k + 1, "n_designs": int(len(allU)), "n_unique": len(key(allU)),
                          "frac_exact_vertex": float(np.all((allU == 0) | (allU == 1), 1).mean())})
    sets = {s: key(np.vstack(lanes[s])) for s in seeds}
    jac = {f"{a}-{b}": len(sets[a] & sets[b]) / len(sets[a] | sets[b]) for i, a in enumerate(seeds) for b in seeds[i + 1:]}
    mind = []
    for s in seeds:
        ev = U0.copy()
        for k in range(4):
            Uk = lanes[s][k]
            d = np.sqrt(((Uk[:, None, :] - ev[None, :, :]) ** 2).sum(-1)).min(1)
            mind.append({"seed_id": s, "round": k + 1, "min_dist_to_evaluated": float(d.min()),
                         "n_below_1e-6": int((d < 1e-6).sum()), "n_below_0.05": int((d < 0.05).sum())})
            ev = np.vstack([ev, Uk])
    r1 = per_round[0]
    dup = r1["n_designs"] - r1["n_unique"]
    out = {"variant": variant, "scenario": scenario, "per_round": per_round, "jaccard_32": jac,
           "jaccard_range": [min(jac.values()), max(jac.values())], "min_dist": mind,
           "r1_duplicate_runs_of_40": int(dup),
           "statement": (f"Under option C, {dup} of the {r1['n_designs']} r1 PCM runs would duplicate another lane's design "
                         "(exact match to 1e-10 in u). Shared replicates vs run all is a decision for Kay.")}
    log(f"[overlap] r1 unique {r1['n_unique']}/{r1['n_designs']}, vertices {r1['frac_exact_vertex']:.2f}; "
        f"Jaccard {out['jaccard_range']}; min dist to evaluated {min(m['min_dist_to_evaluated'] for m in mind):.3g}")
    return out


def extras(log=print):
    plug_h = r0_plugin("house", log)
    plug_l = r0_plugin("long", log)
    base, bdes = baselines(plug_h, log)
    bk = best_known_front(bdes, log)
    cs = calib_split(log)
    cs.to_csv(os.path.join(HERE, "emulator_E_calib_hull.csv"), index=False, float_format="%.6g")
    ov = seed_overlap(log=log)
    hb = bk["hv_best_known"]
    bsum = {}
    for name, H in base.items():
        Hf = np.asarray(H, float) / hb
        bsum[name] = {"n_rep": int(len(Hf)), "p5": np.percentile(Hf, 5, axis=0).tolist(),
                      "p50": np.percentile(Hf, 50, axis=0).tolist(), "p95": np.percentile(Hf, 95, axis=0).tolist(),
                      "max": Hf.max(0).tolist()}
    out = {"label": "EMULATOR", "r0_plugin": {"house": plug_h, "long": plug_l}, "best_known": bk,
           "baselines": bsum, "baseline_rule": ("matched budget: same 48 starts (true f), 8 designs per round x 4, "
                                                "true-f HV / best-known HV per round; uniform = i.i.d. u; vertices = 32 of "
                                                "the 64 box vertices without replacement; plugin_random = 32 random designs "
                                                "of the r0 plug-in front; plugin_spread = 32 designs at quantiles of the "
                                                f"plug-in front (1 replicate, no exploration); {N_REP} replicates, "
                                                f"default_rng({BASE_SEED})"),
           "seed_overlap": ov}
    with open(os.path.join(RUNS, "EMU_extras.json"), "w") as fh:
        json.dump(out, fh, indent=1, default=float)
    return out


# --------------------------------------------------------------------------- #
# CLI (collect / figs / report live in emulator_E_report.py)
# --------------------------------------------------------------------------- #

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("fit-emulator")
    s = sub.add_parser("single")
    s.add_argument("--obj", choices=SEATED, required=True)
    s.add_argument("--seed", type=int, required=True)
    s.add_argument("--method", choices=["bo", "random"], default="bo")
    s.add_argument("--variant", choices=list(VARIANT), default="house")
    m = sub.add_parser("multi")
    m.add_argument("--scenario", choices=list(SCEN), required=True)
    m.add_argument("--seeds", default="0")
    m.add_argument("--variant", choices=list(VARIANT), default="house")
    sub.add_parser("random-pool")
    sub.add_parser("front")
    sub.add_parser("extras")
    a = ap.parse_args(argv)
    os.makedirs(RUNS, exist_ok=True)
    os.makedirs(RUNS_BIG, exist_ok=True)
    if a.cmd == "fit-emulator":
        fit_emulator()
    elif a.cmd == "single":
        run_single(a.obj, a.seed, a.method, a.variant)
    elif a.cmd == "multi":
        for sd in [int(x) for x in a.seeds.split(",")]:
            run_multi(a.scenario, sd, a.variant)
    elif a.cmd == "random-pool":
        random_pool()
    elif a.cmd == "front":
        emulator_front()
    elif a.cmd == "extras":
        extras()
    return 0


if __name__ == "__main__":
    sys.exit(main())
