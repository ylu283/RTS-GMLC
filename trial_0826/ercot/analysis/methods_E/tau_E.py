"""Prompt 55 — the stop-rule rulers tau_joint / tau_marginal, M-general (plan 6.2).

tau = std (ddof 0) of the EXACT hypervolume over N = 1,000 MC draws,
`numpy.random.default_rng(20261006)`, every start of the arm's start set
perturbed in each draw:

  * tau_joint (HEADLINE): noise vectors drawn JOINTLY, eps_i ~ N(0, Sigma_i).
      - homoscedastic: Sigma_i = Sigma_exact for every start
        (`ercot_noise_exact_cov.csv`, the covariance of the EXACT cross-batch
        replicate deltas, plan 3 / contract 6.3 — never the perturbed
        `ercot_noise_cov.csv`, which feeds the plan-7 rider only);
      - heteroscedastic (52 trigger fired for objective j): Sigma_i = D_i C D_i
        with C the exact-delta correlation matrix and D_i = diag sigma_j(y_i),
        sigma_j piecewise-linear through the 52 per-level anchors (RTS form ii).
      - **Sigma = 0 exactly -> tau = 0 without drawing** (plan 3: the rule is
        budget-cap-only and the cap governs).
  * tau_marginal (RECORDED): independent per-objective normals with the
    marginal sds (the diagonal of Sigma_i). With constant sds this is the
    donor `part_c45.tau` / `acquire_arm.tau45` stream bit-for-bit (same rng,
    same `rng.normal(0, sd, size=Y.shape)` per draw) — the port test.
  * sensitivity row (plan 6.2 fallback, third ledger column):
    tau_joint / tau_marginal, plus the per-ruler would_stop columns.

Draw order is pinned: one rng per ruler, draws consumed in draw-major order.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from common_E import hv_exact

TAU_SEED = 20261006
N_DRAWS = 1000


# --------------------------------------------------------------------------- #
# heteroscedastic sigma_j(y): piecewise-linear through anchors (RTS form ii)
# --------------------------------------------------------------------------- #

def sigma_pwl(y, anchors_y, anchors_sd):
    """Piecewise-linear sd through (anchors_y, anchors_sd); below the first
    anchor = first sd, above the last anchor the LAST slope is extrapolated
    (the part_c45 / PHASE_B convention), clipped at 0."""
    y = np.asarray(y, float)
    ay = np.asarray(anchors_y, float)
    asd = np.asarray(anchors_sd, float)
    assert ay.ndim == 1 and ay.shape == asd.shape and len(ay) >= 1
    assert np.all(np.diff(ay) > 0), "anchors_y must be strictly increasing"
    if len(ay) == 1:
        return np.full_like(y, asd[0])
    out = np.interp(y, ay, asd)
    slope = (asd[-1] - asd[-2]) / (ay[-1] - ay[-2])
    above = y > ay[-1]
    out = np.where(above, asd[-1] + (y - ay[-1]) * slope, out)
    return np.clip(out, 0.0, None)


def correlation_from_cov(Sigma):
    """Correlation matrix of Sigma; a zero-variance objective gets C_jj = 1 and
    zero correlation with everything (its draws are identically 0 anyway)."""
    S = np.asarray(Sigma, float)
    sd = np.sqrt(np.clip(np.diag(S), 0.0, None))
    C = np.eye(len(sd))
    nz = sd > 0
    if nz.any():
        sub = S[np.ix_(nz, nz)] / np.outer(sd[nz], sd[nz])
        C[np.ix_(nz, nz)] = sub
    np.fill_diagonal(C, 1.0)
    return C


# --------------------------------------------------------------------------- #
# the rulers
# --------------------------------------------------------------------------- #

def _check(Y, ref):
    Y = np.atleast_2d(np.asarray(Y, float))
    ref = np.asarray(ref, float)
    assert Y.ndim == 2 and ref.shape == (Y.shape[1],), (Y.shape, ref.shape)
    assert np.isfinite(Y).all() and np.isfinite(ref).all()
    return Y, ref


def tau_joint(Y, ref, Sigma=None, C=None, sd_matrix=None, n_draws=N_DRAWS, seed=TAU_SEED):
    """Joint ruler. Either `Sigma` (M x M, homoscedastic) or (`C` correlation
    M x M + `sd_matrix` n x M, heteroscedastic). Returns (tau, hvs)."""
    Y, ref = _check(Y, ref)
    n, M = Y.shape
    rng = np.random.default_rng(seed)
    if sd_matrix is None:
        S = np.asarray(Sigma, float)
        assert S.shape == (M, M), S.shape
        assert np.allclose(S, S.T, atol=1e-12), "Sigma must be symmetric"
        if np.all(S == 0.0):
            return 0.0, np.full(n_draws, hv_exact(Y, ref))      # plan 3: Sigma = 0 -> tau = 0
        with np.errstate(all="ignore"):   # macOS numpy: spurious matmul warnings on finite output
            eps = rng.multivariate_normal(np.zeros(M), S, size=(n_draws, n), method="svd")
        assert np.isfinite(eps).all()
    else:
        Cm = np.asarray(C, float)
        sd = np.asarray(sd_matrix, float)
        assert Cm.shape == (M, M) and sd.shape == (n, M), (Cm.shape, sd.shape)
        if np.all(sd == 0.0):
            return 0.0, np.full(n_draws, hv_exact(Y, ref))
        with np.errstate(all="ignore"):
            z = rng.multivariate_normal(np.zeros(M), Cm, size=(n_draws, n), method="svd")
        assert np.isfinite(z).all()
        eps = z * sd[None, :, :]                                   # D_i C D_i per start
    hvs = np.empty(n_draws)
    for i in range(n_draws):
        hvs[i] = hv_exact(Y + eps[i], ref)
    return float(np.std(hvs, ddof=0)), hvs


def tau_marginal(Y, ref, sd, n_draws=N_DRAWS, seed=TAU_SEED):
    """Marginal ruler: independent normals, `sd` of shape (M,) or (n, M).
    With constant sd this is `part_c45.tau` / `acquire_arm.tau45` bit-for-bit."""
    Y, ref = _check(Y, ref)
    n, M = Y.shape
    sd = np.asarray(sd, float)
    if sd.ndim == 1:
        assert sd.shape == (M,), sd.shape
        floors = sd
    else:
        assert sd.shape == (n, M), sd.shape
        floors = sd
    if np.all(floors == 0.0):
        return 0.0, np.full(n_draws, hv_exact(Y, ref))
    rng = np.random.default_rng(seed)
    hvs = np.empty(n_draws)
    for i in range(n_draws):
        hvs[i] = hv_exact(Y + rng.normal(0.0, floors, size=Y.shape), ref)
    return float(np.std(hvs, ddof=0)), hvs


# --------------------------------------------------------------------------- #
# Sigma_exact from the prompt-52 files (contract 6.3)
# --------------------------------------------------------------------------- #

def read_cov_csv(path, objectives):
    """Square CSV (ids as index and columns) restricted to `objectives`, in order."""
    df = pd.read_csv(path, index_col=0)
    df.index = df.index.astype(str)
    df.columns = df.columns.astype(str)
    missing = [o for o in objectives if o not in df.index or o not in df.columns]
    assert not missing, f"{path}: ids missing from the covariance file: {missing}"
    S = df.loc[objectives, objectives].to_numpy(float)
    assert np.isfinite(S).all(), f"{path}: non-finite entries"
    return 0.5 * (S + S.T)


def level_anchors(noise, obj):
    """(anchors_y, anchors_sd) for objective `obj` from ercot_noise.json
    per_candidate.<id>.levels[] (sd + the level's y anchor). Defensive on the
    anchor key name; Part B pins it against the real file."""
    levels = noise["per_candidate"][obj]["levels"]
    ys, sds = [], []
    for lv in levels:
        yk = next((k for k in ("y", "mean", "level_mean", "value", "center") if k in lv), None)
        assert yk is not None, f"{obj}: level entry has no y anchor key: {sorted(lv)}"
        ys.append(float(lv[yk])); sds.append(float(lv["sd"]))
    order = np.argsort(ys)
    return np.asarray(ys)[order], np.asarray(sds)[order]


def rulers_from_files(Y, ref, objectives, exact_cov_csv=None, noise_json=None, Sigma=None,
                      n_draws=N_DRAWS, seed=TAU_SEED):
    """Compute both rulers + the sensitivity row from the 52 outputs (or an
    explicit `Sigma`, Part A placeholder). Returns a JSON-able dict."""
    Y, ref = _check(Y, ref)
    n, M = Y.shape
    if Sigma is None:
        assert exact_cov_csv is not None
        Sigma = read_cov_csv(exact_cov_csv, objectives)
        sigma_source = str(exact_cov_csv)
    else:
        Sigma = np.asarray(Sigma, float)
        sigma_source = "explicit (Part A placeholder)"
    het = {}
    if noise_json is not None:
        for j, o in enumerate(objectives):
            pc = noise_json.get("per_candidate", {}).get(o, {})
            if pc.get("trigger", {}).get("fires"):
                het[o] = level_anchors(noise_json, o)
    all_zero = bool(np.all(Sigma == 0.0)) and not het
    sd_diag = np.sqrt(np.clip(np.diag(Sigma), 0.0, None))
    if het:
        sd_matrix = np.tile(sd_diag, (n, 1))
        for o, (ay, asd) in het.items():
            j = objectives.index(o)
            sd_matrix[:, j] = sigma_pwl(Y[:, j], ay, asd)
        C = correlation_from_cov(Sigma)
        tj, hv_j = tau_joint(Y, ref, C=C, sd_matrix=sd_matrix, n_draws=n_draws, seed=seed)
        tm, hv_m = tau_marginal(Y, ref, sd_matrix, n_draws=n_draws, seed=seed)
        form = "heteroscedastic (D_i C D_i; sigma_j piecewise-linear through the 52 per-level anchors)"
    else:
        tj, hv_j = tau_joint(Y, ref, Sigma=Sigma, n_draws=n_draws, seed=seed)
        tm, hv_m = tau_marginal(Y, ref, sd_diag, n_draws=n_draws, seed=seed)
        form = "homoscedastic (Sigma_exact for every start)"
    out = {
        "tau_joint": tj, "tau_marginal": tm,
        "sensitivity_joint_over_marginal": (tj / tm) if tm > 0 else None,
        "all_exact_zero": all_zero,
        "budget_cap_only": all_zero,
        "form": form,
        "sigma_source": sigma_source,
        "sigma_exact": Sigma.tolist(),
        "sd_marginal": sd_diag.tolist(),
        "heteroscedastic_objectives": sorted(het),
        "n_starts": int(n), "M": int(M), "n_draws": int(n_draws), "seed": int(seed),
        "hv0": hv_exact(Y, ref),
        "hv_joint_mean": float(np.mean(hv_j)), "hv_marginal_mean": float(np.mean(hv_m)),
        "recipe": ("std (ddof 0) of the exact HV over N draws, default_rng(seed); every start perturbed "
                   "jointly by multivariate_normal(0, Sigma, method='svd') (joint) or by independent "
                   "normals with the marginal sds (marginal); Sigma = 0 -> tau = 0 without drawing"),
    }
    if all_zero:
        out["statement"] = ("The exact cross-batch replicate covariance is identically zero, so "
                            "tau_joint = tau_marginal = 0: the stop rule is budget-cap-only and the cap "
                            "governs (plan section 3). This is a finding about a deterministic instrument, "
                            "not a failure.")
    return out


# --------------------------------------------------------------------------- #
# plan 7 rider levels (recorded at init; the rider itself is graded later)
# --------------------------------------------------------------------------- #

def rider_levels(noise_json, objectives):
    """Per objective: exact sd (noise level) if > 0, else the 52 PERTURBED
    population sd labelled 'sensitivity-level rider' (plan 7). The median-|Delta|
    `ruler` is the readability ruler and is NOT a rider level."""
    out = {}
    for o in objectives:
        pc = noise_json["per_candidate"][o]
        exact_sd = float(noise_json["noise_floor"]["floor"].get(o, 0.0))
        if exact_sd > 0 and not pc.get("exact_zero", False):
            out[o] = {"level": exact_sd, "label": "noise-level rider (exact replicate sd)"}
        else:
            lv = [float(x["sd"]) for x in pc.get("levels", []) if np.isfinite(float(x.get("sd", np.nan)))]
            n_lv = [int(x.get("n", 0)) for x in pc.get("levels", [])]
            if lv and sum(n_lv) > 0 and len(n_lv) == len(lv):
                pooled = float(np.sqrt(sum((n - 1) * s ** 2 for n, s in zip(n_lv, lv)) / max(sum(n - 1 for n in n_lv), 1)))
            else:
                pooled = float(np.sqrt(np.mean(np.square(lv)))) if lv else 0.0
            out[o] = {"level": pooled, "label": "sensitivity-level rider (52 perturbed-population sd; NOT a noise level)"}
    return out
