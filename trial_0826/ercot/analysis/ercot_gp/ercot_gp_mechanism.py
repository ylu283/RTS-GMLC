#!/usr/bin/env python3
"""Prompt 54 §3.5 (v3.2, widened 2026-11-17) — mechanism sanity: read-only flags.
Nothing here may change committed_configs.json, E-D7 or prompt 55.

Pinned BEFORE any n0_E Y is read (this file's first commit precedes the fit):

(a) Network facts, computed from `data/ercot123_2019_v2/branch.csv` and
    `extracts/base_v3/run_index_1/line_summary.csv` and asserted: buses 2 / 75 /
    121 (sites 110, 140 on bus 2; 146 on bus 75) form an appendage whose every
    branch to the rest of the grid lands on bus 120 (sites 163, 270, 274), so an
    injection anywhere in {2, 75, 121, 120} reaches the binding line L252
    (cont_rating 700 MW) with the same PTDF; L252's >= 99 % hours in base_v3.

(b) Location share L_j and interaction share I_j per objective from the
    COMMITTED config fitted on the grading tier, over S = 256 posterior sample
    paths on the ORIGINAL Y scale:
      L_j = 1 - Var(E[f_j | T]) / Var(f_j),  T = sum_s mw_s, E[f|T] by 40 quantile
            bins of T on a Sobol base of 2^13 points (seed MECH_SEED, separate);
      I_j = 1 - sum_s S_s, S_s = first-order Sobol indices (Jansen estimator) on
            the same base (A, B, A_B^(s)).
    Posterior paths: decoupled sampling (prior via random Fourier features of the
    fitted ARD Matern / RBF kernel + the exact canonical update on the 48
    training points), verified against the exact gpytorch posterior in the tests.
    Posterior median and 5-95 % band are reported.

(c) No-simulation NULL: an ADDITIVE truth from monotone PCHIP curves through
    wave D's per-site V1 at 0 / 60 / 120 / 180 MW (0 = base_v3; the curve is
    evaluated on [0, nameplate], the last PCHIP segment extrapolated beyond
    180 MW and floored at 0) and a TOTAL-ONLY concave truth (saturating
    exponential fitted to the same 19 points as a function of T), both evaluated
    at the n0_E X and refitted with the same config; the flag threshold is the
    null's 95th percentile (median also recorded).
    Flags: INTERACTION if the 5th percentile of I_j exceeds the additive null's
    95th; LOCATION if the 5th percentile of L_j exceeds the total-only null's
    95th; ADDITIVE / TOTAL-ONLY-COMPATIBLE if the 95th percentile is below the
    null median; UNRESOLVED otherwise. ARD lengthscales are descriptive only.
    R4 / N1 flags are suppressed unless their config passed [43, 48] and the
    prompt-52 ruler shows their chatter readable (RULER status, not RULER=0).

    python analysis/ercot_gp/ercot_gp_mechanism.py --null-only [--out-dir DIR]
        -> ercot_gp_null.json + fig_null_truths.png (reads wave D, base_v3, the
           n0_E design matrix X; NO n0_E Y)
    (Part B: `ercot_gp_status.py --real` calls mechanism_page() after the fit.)
"""
import argparse
import csv
import json
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ERCOT = os.path.abspath(os.path.join(HERE, "..", ".."))
if ERCOT not in sys.path:
    sys.path.insert(0, ERCOT)
from analysis.ercot_gp import ercot_gp_status as S  # noqa: E402  (FlexGP, fit, arms)

import torch  # noqa: E402

MECH_SEED = 5454              # separate pinned seed (prompt 54 §3.5 b)
N_PATHS = 256
N_BASE_LOG2 = 13              # Sobol base 2^13 points
N_BINS = 40
N_RFF = 8192
APPENDAGE = {2, 75, 121}
EXIT_BUS = 120
BINDING_LINE = "L252"
SITE_BUS = {"110": 2, "140": 2, "146": 75, "163": 120, "270": 120, "274": 120}
WAVE_D_LEVELS = (60.0, 120.0, 180.0)
FLAG_SUPPRESS = ("R4", "N1")


# --------------------------------------------------------------------------
# (a) network facts — computed and asserted
# --------------------------------------------------------------------------
def network_facts(branch_csv=None, line_summary_csv=None):
    branch_csv = branch_csv or os.path.join(ERCOT, "data", "ercot123_2019_v2", "branch.csv")
    line_summary_csv = line_summary_csv or os.path.join(ERCOT, "extracts", "base_v3", "run_index_1", "line_summary.csv")
    rows = list(csv.DictReader(open(branch_csv)))
    touching, exits = [], set()
    for r in rows:
        a, b = int(float(r["From Bus"])), int(float(r["To Bus"]))
        if a in APPENDAGE or b in APPENDAGE:
            touching.append((a, b, r["UID"]))
            for end in (a, b):
                if end not in APPENDAGE:
                    exits.add(end)
    assert exits == {EXIT_BUS}, f"appendage {sorted(APPENDAGE)} exits to {sorted(exits)}, expected only {EXIT_BUS}"
    ls = pd.read_csv(line_summary_csv)
    ls["Line"] = ls["Line"].astype(str)
    l = ls[ls["Line"] == BINDING_LINE]
    assert len(l) == 1, f"{BINDING_LINE} not in {line_summary_csv}"
    l = l.iloc[0]
    exit_lines = sorted(uid for a, b, uid in touching if EXIT_BUS in (a, b))
    return {
        "appendage_buses": sorted(APPENDAGE), "exit_bus": EXIT_BUS, "exit_lines": exit_lines,
        "appendage_branches": [uid for _, _, uid in touching],
        "site_bus": SITE_BUS,
        "binding_line": BINDING_LINE, "cont_rating_mw": float(l["cont_rating"]),
        "hours_ge_99pct_base_v3": int(l["hours_ge_99pct"]), "max_abs_flow_base_v3": float(l["max_abs_flow"]),
        "text": (f"Buses {sorted(APPENDAGE)} (sites 110 / 140 on bus 2, 146 on bus 75) drain only through bus "
                 f"{EXIT_BUS} (sites 163 / 270 / 274) via {exit_lines}; every MW injected at any of the six sites "
                 f"therefore reaches the binding line {BINDING_LINE} ({float(l['cont_rating']):.0f} MW, "
                 f"{int(l['hours_ge_99pct']):,} h/yr >= 99 % of rating in base_v3) with the same PTDF — the six "
                 "sites are one electrical location; location effects can come only from resource profiles and "
                 "nameplate caps."),
    }


# --------------------------------------------------------------------------
# (b) posterior sample paths: decoupled RFF prior + canonical update on a FlexGP
# --------------------------------------------------------------------------
class PathSampler:
    """Posterior sample paths of a fitted FlexGP (gpytorch ExactGP, ScaleKernel(Matern
    nu in {1.5, 2.5} | RBF, ARD), ConstantMean, Gaussian noise), in the GP's
    STANDARDIZED input/target space, de-standardized on request.

    f(x) = c + phi(x) w + k(x, X) (K + s2 I)^-1 (y - c - phi(X) w - eps),
    w ~ N(0, I_M), eps ~ N(0, s2 I): Wilson et al. 2020 'Efficiently sampling
    functions from GP posteriors' (prior: RFF, update: canonical basis)."""

    def __init__(self, gp, n_features=N_RFF, seed=MECH_SEED):
        self.gp = gp
        self.rng = np.random.default_rng(seed)
        cov = gp.model.covar_module
        base = cov.base_kernel
        self.ls = base.lengthscale.detach().double().numpy().reshape(-1)        # (d,) standardized x units
        self.s2f = float(cov.outputscale.detach().double())
        self.s2n = float(gp.lik.noise.detach().double())
        self.c = float(gp.model.mean_module.constant.detach().double())
        self.nu = float(getattr(base, "nu", np.inf))                               # Matern nu; inf = RBF
        self.X = gp._tx.detach().double().numpy()
        self.y = gp._ty.detach().double().numpy()
        n, d = self.X.shape
        M = int(n_features)
        z = self.rng.standard_normal((M, d))
        if np.isfinite(self.nu):                                                   # Matern spectral = t_{2nu}
            g = self.rng.gamma(shape=self.nu, scale=1.0 / self.nu, size=(M, 1))
            z = z / np.sqrt(g)
        self.omega = z / self.ls[None, :]
        self.b = self.rng.uniform(0.0, 2.0 * np.pi, size=M)
        self.M = M
        K = self._k(self.X, self.X) + self.s2n * np.eye(n)
        self.L = np.linalg.cholesky(K)

    def _k(self, A, B):
        D = (A[:, None, :] - B[None, :, :]) / self.ls[None, None, :]
        r2 = np.einsum("ijk,ijk->ij", D, D)
        if not np.isfinite(self.nu):
            return self.s2f * np.exp(-0.5 * r2)
        r = np.sqrt(np.clip(r2, 0.0, None))
        if abs(self.nu - 2.5) < 1e-9:
            a = np.sqrt(5.0) * r
            return self.s2f * (1.0 + a + a * a / 3.0) * np.exp(-a)
        if abs(self.nu - 1.5) < 1e-9:
            a = np.sqrt(3.0) * r
            return self.s2f * (1.0 + a) * np.exp(-a)
        raise ValueError(f"unsupported Matern nu {self.nu}")

    def _phi(self, Xs):
        with np.errstate(all="ignore"):          # macOS numpy: spurious matmul warnings on finite output
            return np.sqrt(2.0 * self.s2f / self.M) * np.cos(Xs @ self.omega.T + self.b[None, :])

    def standardize(self, U):
        return (np.asarray(U, float) - self.gp.mx) / self.gp.sx

    def sample_std(self, Xs, n_paths=N_PATHS):
        """(n_paths, len(Xs)) latent paths in standardized-target units at standardized Xs."""
        W = self.rng.standard_normal((self.M, n_paths))
        eps = self.rng.standard_normal((len(self.X), n_paths)) * np.sqrt(self.s2n)
        with np.errstate(all="ignore"):
            f0X = self._phi(self.X) @ W                                            # (n, S)
            resid = self.y[:, None] - self.c - f0X - eps
            v = np.linalg.solve(self.L.T, np.linalg.solve(self.L, resid))          # (n, S)
            f0 = self._phi(Xs) @ W                                                 # (N, S)
            f = self.c + f0 + self._k(Xs, self.X) @ v
        assert np.isfinite(f).all()
        return f.T

    def sample_raw(self, U, n_paths=N_PATHS):
        """Paths on the ORIGINAL Y scale at inputs U (u units)."""
        t = self.sample_std(self.standardize(U), n_paths) * self.gp.sy + self.gp.my
        return np.expm1(t) if self.gp.transform == "log1p" else t


def exact_posterior_std(gp, U):
    """Exact latent posterior mean / sd (standardized target units) for the tests."""
    import gpytorch
    xq = torch.tensor((np.atleast_2d(U) - gp.mx) / gp.sx, dtype=torch.float32)
    with torch.no_grad(), gpytorch.settings.fast_pred_var():
        p = gp.model(xq)
        return p.mean.numpy().astype(float), p.stddev.numpy().astype(float)


# --------------------------------------------------------------------------
# (b) the shares on a Sobol base
# --------------------------------------------------------------------------
def sobol_base(d, log2n=N_BASE_LOG2, seed=MECH_SEED):
    from scipy.stats import qmc
    Z = qmc.Sobol(d=2 * d, scramble=True, seed=seed).random_base2(log2n)
    return Z[:, :d], Z[:, d:]


def design_points(A, B):
    """A, B and A_B^(s) (column s of A replaced by B's) stacked: (N (d + 2), d)."""
    N, d = A.shape
    blocks = [A, B]
    for s in range(d):
        AB = A.copy()
        AB[:, s] = B[:, s]
        blocks.append(AB)
    return np.vstack(blocks)


def shares_from_paths(F, N, d, T_A, n_bins=N_BINS):
    """F: (S, N (d+2)) path values at design_points(A, B); T_A: (N,) total MW of A.
    Returns dict of arrays over paths: L, I, S_first (S, d), var_total."""
    S_, _ = F.shape
    fA, fB = F[:, :N], F[:, N:2 * N]
    fAB = [F[:, (2 + s) * N:(3 + s) * N] for s in range(d)]
    var_tot = np.var(np.hstack([fA, fB]), axis=1, ddof=0)
    S_first = np.empty((S_, d))
    for s in range(d):
        S_first[:, s] = 1.0 - np.mean((fB - fAB[s]) ** 2, axis=1) / (2.0 * var_tot)
    I = 1.0 - S_first.sum(axis=1)
    # L: variance of the binned conditional mean E[f | T] over quantile bins of T
    edges = np.quantile(T_A, np.linspace(0.0, 1.0, n_bins + 1))
    bins = np.clip(np.searchsorted(edges, T_A, side="right") - 1, 0, n_bins - 1)
    varA = np.var(fA, axis=1, ddof=0)
    counts = np.bincount(bins, minlength=n_bins).astype(float)
    sums = np.zeros((S_, n_bins))
    for k in range(n_bins):
        m = bins == k
        if m.any():
            sums[:, k] = fA[:, m].sum(axis=1)
    means = sums / np.where(counts > 0, counts, 1.0)[None, :]
    grand = fA.mean(axis=1, keepdims=True)
    var_cond = ((means - grand) ** 2 * counts[None, :]).sum(axis=1) / counts.sum()
    L = 1.0 - var_cond / varA
    return {"L": L, "I": I, "S_first": S_first, "var_total": var_tot, "var_A": varA}


def posterior_shares(gp, gen_pmax, n_paths=N_PATHS, log2n=N_BASE_LOG2, seed=MECH_SEED, n_features=N_RFF):
    """L_j / I_j distributions over posterior paths of one fitted FlexGP (inputs u)."""
    gen_pmax = np.asarray(gen_pmax, float)
    d = len(gen_pmax)
    A, B = sobol_base(d, log2n, seed)
    P = design_points(A, B)
    sampler = PathSampler(gp, n_features=n_features, seed=seed)
    F = sampler.sample_raw(P, n_paths)
    T_A = (A * gen_pmax[None, :]).sum(axis=1)
    out = shares_from_paths(F, len(A), d, T_A)
    out["lengthscales_std_x"] = sampler.ls.tolist()
    out["lengthscales_u"] = (sampler.ls * np.asarray(gp.sx, float)).tolist()
    return out


def summarize(arr):
    a = np.asarray(arr, float)
    return {"median": float(np.median(a)), "p05": float(np.percentile(a, 5)), "p95": float(np.percentile(a, 95)),
            "mean": float(a.mean()), "n_paths": int(len(a))}


# --------------------------------------------------------------------------
# (c) the null truths from wave D + base_v3, evaluated at the n0_E X
# --------------------------------------------------------------------------
def wave_d_site_curves(objective="V1", wide_csv=None, base_value=None, sites=None):
    """Per site: knots (0, 60, 120, 180) MW -> objective value (0 = base_v3)."""
    wide_csv = wide_csv or os.path.join(ERCOT, "analysis", "pool", "pool_wavedD_wide.csv")
    w = pd.read_csv(wide_csv, dtype={"site": str})
    w = w[w["unit_type"] == "WIND"]
    sites = sites or sorted(SITE_BUS)
    if base_value is None:
        base_value = base_v3_value(objective)
    curves = {}
    for s in sites:
        r = w[w["site"] == s].sort_values("pem_mw")
        assert list(np.round(r["pem_mw"].astype(float), 6)) == list(WAVE_D_LEVELS), (s, r["pem_mw"].tolist())
        curves[s] = {"mw": [0.0, *WAVE_D_LEVELS], "y": [float(base_value), *r[objective].astype(float).tolist()]}
    return curves, float(base_value)


def base_v3_value(objective, run_dir=None):
    import pool_objectives as po
    run_dir = run_dir or os.path.join(ERCOT, "extracts", "base_v3", "run_index_1")
    row = po.pool_row("base_v3:1", drow=po.BASE_DROW, d=run_dir)
    return float(row[objective])


def additive_truth(curves, base, sites, gen_pmax):
    """f_add(x) = base + sum_s (p_s(min(mw_s, pmax_s)) - base), p_s = PCHIP through the
    site's knots, last segment extrapolated, floored at 0."""
    from scipy.interpolate import PchipInterpolator
    interp = {s: PchipInterpolator(curves[s]["mw"], curves[s]["y"], extrapolate=True) for s in sites}

    def f(X_mw):
        X = np.atleast_2d(np.asarray(X_mw, float))
        out = np.full(len(X), base)
        for j, s in enumerate(sites):
            mw = np.clip(X[:, j], 0.0, gen_pmax[j])
            out = out + (np.clip(interp[s](mw), 0.0, None) - base)
        return out
    return f


def total_only_truth(curves, base, sites):
    """g(T) = base - a (1 - exp(-T / b)) least-squares fitted to the 18 wave-D points
    + base at T = 0 (monotone decreasing, concave in T for a > 0)."""
    from scipy.optimize import curve_fit
    T = [0.0] + [m for s in sites for m in curves[s]["mw"][1:]]
    y = [base] + [v for s in sites for v in curves[s]["y"][1:]]
    T, y = np.asarray(T, float), np.asarray(y, float)
    drop = base - y

    def model(t, a, b):
        return a * (1.0 - np.exp(-t / b))
    a0 = max(float(drop.max()), 1.0) * 2.0
    (a, b), _ = curve_fit(model, T, drop, p0=[a0, 500.0], bounds=([0.0, 1.0], [np.inf, 1e6]), maxfev=20000)

    def g(X_mw):
        X = np.atleast_2d(np.asarray(X_mw, float))
        return base - model(X.sum(axis=1), a, b)
    return g, {"a": float(a), "b": float(b), "form": "base - a (1 - exp(-T / b))"}


def n0_X(design_space=None, waves_dir=None):
    """n0_E X in MW and u from the design matrix (no Y, no extracts)."""
    from analysis.ercot_gp.ercot_gp_loader import read_design_space
    design_space = design_space or os.path.join(ERCOT, "waves", "design_space_E.json")
    ds = read_design_space(design_space)
    dm = pd.read_csv(os.path.join(waves_dir or os.path.join(ERCOT, "waves"), "n0_E", "design_matrix.csv"),
                     float_precision="round_trip")
    dm = dm.sort_values("sobol_index")
    sites = [s["site"] for s in ds["sites"]]
    gen_pmax = np.asarray([float(s["gen_pmax"]) for s in ds["sites"]], float)
    X = dm[[f"mw_{s}" for s in sites]].to_numpy(float)
    U = dm[[f"u_{s}" for s in sites]].to_numpy(float)
    return X, U, dm["sobol_index"].astype(int).to_numpy(), sites, gen_pmax, ds


def null_distributions(arm, X_mw, U, sites, gen_pmax, objective="V1", n_paths=N_PATHS, log2n=N_BASE_LOG2,
                       meas_sd=0.0, curves=None, base=None):
    """Fit `arm` (a status.Arm) to each null truth at the n0_E X; return the L / I
    distributions and the truths' own (noise-free) shares on the Sobol base."""
    if curves is None:
        curves, base = wave_d_site_curves(objective)
    f_add = additive_truth(curves, base, sites, gen_pmax)
    g_tot, tot_par = total_only_truth(curves, base, sites)
    A, B = sobol_base(len(sites), log2n, MECH_SEED)
    P = design_points(A, B)
    T_A = (A * gen_pmax[None, :]).sum(axis=1)
    out = {"objective": objective, "arm": arm.name, "cfg": list(arm.cfg), "n_paths": n_paths, "sobol_log2n": log2n,
           "seed": MECH_SEED, "curves": curves, "base_v3": base, "total_only_params": tot_par, "truths": {}}
    for name, fn in (("additive", f_add), ("total_only", g_tot)):
        y = fn(X_mw)
        assert np.isfinite(y).all() and y.std() > 0, name
        gp = S.fit(U, y, arm, meas_sd)
        sh = posterior_shares(gp, gen_pmax, n_paths=n_paths, log2n=log2n)
        truth = shares_from_paths(fn(P * gen_pmax[None, :])[None, :], len(A), len(sites), T_A)
        out["truths"][name] = {"L": summarize(sh["L"]), "I": summarize(sh["I"]),
                               "S_first_median": np.median(sh["S_first"], axis=0).tolist(),
                               "truth_L": float(truth["L"][0]), "truth_I": float(truth["I"][0]),
                               "y_range_at_n0X": [float(y.min()), float(y.max())],
                               "lengthscales_u": sh["lengthscales_u"]}
    out["thresholds"] = {"I_null95_additive": out["truths"]["additive"]["I"]["p95"],
                         "I_null_median_additive": out["truths"]["additive"]["I"]["median"],
                         "L_null95_total_only": out["truths"]["total_only"]["L"]["p95"],
                         "L_null_median_total_only": out["truths"]["total_only"]["L"]["median"]}
    return out


def flag(share_summary, null95, null_median, positive_label):
    """INTERACTION / LOCATION if p05 > null95; ADDITIVE / TOTAL-ONLY-COMPATIBLE if p95 < null median; else UNRESOLVED."""
    if share_summary["p05"] > null95:
        return positive_label
    if share_summary["p95"] < null_median:
        return "ADDITIVE" if positive_label == "INTERACTION" else "TOTAL-ONLY-COMPATIBLE"
    return "UNRESOLVED"


def mechanism_flags(obj_shares, null, holdout_pass=None, ruler_status=None):
    """obj_shares[obj] = posterior_shares(...) output of the committed fit; returns per-objective flags."""
    th = null["thresholds"]
    out = {}
    for obj, sh in obj_shares.items():
        Ls, Is = summarize(sh["L"]), summarize(sh["I"])
        fi = flag(Is, th["I_null95_additive"], th["I_null_median_additive"], "INTERACTION")
        fl = flag(Ls, th["L_null95_total_only"], th["L_null_median_total_only"], "LOCATION")
        suppressed = None
        if obj in FLAG_SUPPRESS:
            ok_h = bool(holdout_pass and holdout_pass.get(obj))
            ok_r = bool(ruler_status and ruler_status.get(obj) == "RULER")
            if not (ok_h and ok_r):
                suppressed = (f"flags suppressed: holdout pass = {ok_h}, 52 ruler status = {ruler_status.get(obj) if ruler_status else None} "
                              "(prompt 54 §3.5: R4 / N1 need the [43, 48] pass AND readable chatter)")
        out[obj] = {"L": Ls, "I": Is, "S_first_median": np.median(sh["S_first"], axis=0).tolist(),
                    "flag_interaction": fi, "flag_location": fl, "suppressed": suppressed,
                    "lengthscales_u_descriptive": sh["lengthscales_u"]}
    return out


# --------------------------------------------------------------------------
# figure + page
# --------------------------------------------------------------------------
def fig_null_truths(null, sites, gen_pmax, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.size": 14, "font.weight": "bold", "axes.labelweight": "bold",
                         "axes.titleweight": "bold"})
    curves, base = null["curves"], null["base_v3"]
    f_add = additive_truth(curves, base, sites, gen_pmax)
    g_tot, _ = total_only_truth(curves, base, sites)
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.5))
    ax = axes[0]
    for j, s in enumerate(sites):
        mw = np.linspace(0, gen_pmax[j], 200)
        X = np.zeros((200, len(sites)))
        X[:, j] = mw
        y = f_add(X)
        assert np.isfinite(y).all()
        ax.plot(mw, y / 1e6, lw=2, label=f"site {s} (bus {SITE_BUS[s]})")
        ax.plot(curves[s]["mw"], np.asarray(curves[s]["y"]) / 1e6, "o", color=ax.lines[-1].get_color())
    ax.set_xlabel("PEM MW at one site (others 0)")
    ax.set_ylabel(f"{null['objective']} (1e6 MWh)")
    ax.set_title("Additive null: per-site PCHIP through wave D (0 = base_v3)")
    ax.legend(fontsize=10)
    ax = axes[1]
    T = np.linspace(0, gen_pmax.sum(), 300)
    y = g_tot(np.column_stack([T] + [np.zeros_like(T)] * (len(sites) - 1)))
    assert np.isfinite(y).all()
    ax.plot(T, y / 1e6, lw=2.5, color="k")
    pts_T = [0.0] + [m for s in sites for m in curves[s]["mw"][1:]]
    pts_y = [base] + [v for s in sites for v in curves[s]["y"][1:]]
    ax.plot(pts_T, np.asarray(pts_y) / 1e6, "o", color="C3", label="wave D + base_v3 (19 points)")
    ax.set_xlabel("total PEM MW  T")
    ax.set_ylabel(f"{null['objective']} (1e6 MWh)")
    ax.set_title(f"Total-only concave null: {null['total_only_params']['form']}")
    ax.legend(fontsize=10)
    for a in axes:
        for t in a.get_xticklabels() + a.get_yticklabels():
            t.set_fontweight("bold")
        a.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(path, dpi=130)
    plt.close(fig)
    return path


def mechanism_md(facts, null, flags=None, extra_rows=None):
    th = null["thresholds"]
    L = ["## Mechanism sanity (prompt 54 §3.5 v3.2; read-only flags — nothing here changes committed_configs.json, E-D7 or 55)", "",
         "### (a) Network facts (computed from branch.csv and base_v3 line_summary.csv, asserted)", "",
         facts["text"], "",
         "### (c) No-simulation null (pinned before any n0_E Y was read)", "",
         f"Objective {null['objective']}; GP config {null['cfg']} ({null['arm']}); {null['n_paths']} posterior paths on a "
         f"Sobol base of 2^{null['sobol_log2n']} points (seed {null['seed']}); base_v3 = {null['base_v3']:.6g}; "
         f"total-only fit a = {null['total_only_params']['a']:.4g}, b = {null['total_only_params']['b']:.4g} MW.", "",
         "| null truth | truth L | truth I | posterior L median [5, 95] | posterior I median [5, 95] |", "|---|---|---|---|---|"]
    for name, t in null["truths"].items():
        L.append(f"| {name} | {t['truth_L']:.4f} | {t['truth_I']:.4f} | {t['L']['median']:.4f} [{t['L']['p05']:.4f}, {t['L']['p95']:.4f}] | "
                 f"{t['I']['median']:.4f} [{t['I']['p05']:.4f}, {t['I']['p95']:.4f}] |")
    L += ["", f"Thresholds: INTERACTION if I_p05 > {th['I_null95_additive']:.4f} (additive null 95th); ADDITIVE if I_p95 < "
          f"{th['I_null_median_additive']:.4f} (its median); LOCATION if L_p05 > {th['L_null95_total_only']:.4f} (total-only null "
          f"95th); TOTAL-ONLY-COMPATIBLE if L_p95 < {th['L_null_median_total_only']:.4f}; otherwise UNRESOLVED. "
          "L and I are scale-free shares, so the V1-built null thresholds are applied to every objective.", ""]
    if flags:
        L += ["### (b) Shares from the COMMITTED config on the grading tier", "",
              "| objective | L median [5, 95] | I median [5, 95] | first-order S_s median (sites in JSON order) | interaction flag | location flag | note |",
              "|---|---|---|---|---|---|---|"]
        for obj, f in flags.items():
            L.append(f"| {obj} | {f['L']['median']:.4f} [{f['L']['p05']:.4f}, {f['L']['p95']:.4f}] | "
                     f"{f['I']['median']:.4f} [{f['I']['p05']:.4f}, {f['I']['p95']:.4f}] | "
                     f"{', '.join(f'{v:.3f}' for v in f['S_first_median'])} | "
                     f"{'(suppressed) ' if f['suppressed'] else ''}{f['flag_interaction']} | "
                     f"{'(suppressed) ' if f['suppressed'] else ''}{f['flag_location']} | {f['suppressed'] or ''} |")
        L += ["", "ARD lengthscales (u units, DESCRIPTIVE only — they scale with 1 / gen_pmax): "
              + "; ".join(f"{obj} {['%.2f' % v for v in f['lengthscales_u_descriptive']]}" for obj, f in flags.items()), ""]
    if extra_rows:
        L += ["### Descriptive rows", ""] + [f"- {r}" for r in extra_rows] + [""]
    L += ["The direct 8-run check is prompt 61 (`location_contrast_E`); when it lands, its standardized residuals under the "
          "committed config are added here as one descriptive row.", ""]
    return "\n".join(L)


def run_null(out_dir, arm=None, n_paths=N_PATHS, log2n=N_BASE_LOG2, objective="V1"):
    os.makedirs(out_dir, exist_ok=True)
    arm = arm or S.DEFAULT_ARM
    facts = network_facts()
    X, U, sob, sites, gen_pmax, ds = n0_X()
    assert len(X) == 48 and sorted(sob) == list(range(48))
    null = null_distributions(arm, X, U, sites, gen_pmax, objective=objective, n_paths=n_paths, log2n=log2n)
    null["n0_E_X_rows"] = int(len(X))
    null["design_space_version"] = ds.get("contract_version")
    null["network_facts"] = facts
    with open(os.path.join(out_dir, "ercot_gp_null.json"), "w") as f:
        json.dump(null, f, indent=1, default=float)
    fig_null_truths(null, sites, gen_pmax, os.path.join(out_dir, "fig_null_truths.png"))
    with open(os.path.join(out_dir, "ERCOT_GP_MECHANISM_NULL.md"), "w") as f:
        f.write(mechanism_md(facts, null) + "\n")
    return null


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--null-only", action="store_true", required=True)
    ap.add_argument("--out-dir", default=HERE)
    ap.add_argument("--paths", type=int, default=N_PATHS)
    ap.add_argument("--log2n", type=int, default=N_BASE_LOG2)
    a = ap.parse_args(argv)
    null = run_null(a.out_dir, n_paths=a.paths, log2n=a.log2n)
    print(json.dumps({k: null[k] for k in ("thresholds",)}, indent=1))
    for name, t in null["truths"].items():
        print(name, "truth L/I", round(t["truth_L"], 4), round(t["truth_I"], 4), "posterior L", t["L"], "I", t["I"])


if __name__ == "__main__":
    main()
