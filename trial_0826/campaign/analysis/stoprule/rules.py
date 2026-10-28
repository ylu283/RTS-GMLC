"""Prompt 37 — stopping rules (post hoc on trajectories) and the
pre-registered metrics (PREREG.md §5). Pure numpy/scipy; no model code.

Indexing: round k = 0 is the starts; H_obs[k], H_true[k] for k = 0..R are
cumulative HVs after round k at the run's box R_j. gain_k = H_obs[k] -
H_obs[k-1], k = 1..R. A rule returns the STOP ROUND s in 1..R (rounds
actually run) and whether it FIRED (False = reached its cap K or R).
"""

from __future__ import annotations

import numpy as np
from scipy import stats

HORIZON = 4  # early/late look-ahead (rounds)


# --------------------------------------------------------------------------- #
# rules
# --------------------------------------------------------------------------- #
def s0(gains: np.ndarray, tau: float, w: int = 2, K: int = 4) -> tuple[int, bool]:
    """Live rule: stop after round k if the last w gains are all < tau
    (strict); hard cap K (stop at K without firing)."""
    R = len(gains)
    for k in range(w, min(K, R) + 1):
        if np.all(gains[k - w:k] < tau):
            return k, True
    return min(K, R), False


def s_fix(k: int, R: int) -> tuple[int, bool]:
    return min(k, R), False


def s_rel(gains: np.ndarray, H_obs: np.ndarray, c: float, K: int = 4) -> tuple[int, bool]:
    """Stop after round k when gain_k < c * H_obs[k] (window 1, literal)."""
    R = len(gains)
    for k in range(1, min(K, R) + 1):
        if gains[k - 1] < c * H_obs[k]:
            return k, True
    return min(K, R), False


def s_model(ehvi: np.ndarray, tau: float, w: int = 2, K: int = 4) -> tuple[int, bool]:
    """M3 only. ehvi[k-1] = E[HVI] of batch k, computed when batch k was
    proposed (data <= k-1). After round k the live loop would propose k+1
    and see ehvi[k]; stop after round k if ehvi of the batches k-w+2..k+1
    are all < tau (w consecutive predicted gains, the last one being the
    batch that is then NOT evaluated). Cannot fire at k = R (no ehvi[R])."""
    R = len(ehvi)
    for k in range(max(1, w - 1), min(K, R) + 1):
        if k >= R:
            break
        win = ehvi[k + 1 - w:k + 1]
        if len(win) == w and np.all(win < tau):
            return k, True
    return min(K, R), False


def s_ocd(gains: np.ndarray, tau: float, alpha: float = 0.05, K: int = 4,
          k_min: int = 3) -> tuple[int, bool]:
    """OCD-style (Wagner, Trautmann & Naujoks, EMO 2009: stop when EITHER
    test indicates convergence). Series = all gains so far g_1..g_k
    (k >= k_min = 3, so the slope test has >= 1 dof):
      (a) chi^2 variance test, one-sided: (k-1) s^2 / tau^2 below the
          alpha quantile of chi^2_{k-1} -> variance < tau^2 -> converged;
      (b) t-test on the OLS slope of g vs round, two-sided: p > alpha
          -> no significant trend -> converged."""
    R = len(gains)
    for k in range(k_min, min(K, R) + 1):
        g = gains[:k]
        var_ok = (k - 1) * np.var(g, ddof=1) / tau ** 2 < stats.chi2.ppf(alpha, k - 1)
        slope_p = stats.linregress(np.arange(1, k + 1), g).pvalue
        trend_none = not (slope_p <= alpha)   # nan (constant series) counts as no trend
        if var_ok or trend_none:
            return k, True
    return min(K, R), False


def oracle(H_true: np.ndarray, tau: float) -> int:
    """argmin_{r in 1..R} (H* - H_r) + tau * r  ==  argmin -H_r + tau r."""
    r = np.arange(1, len(H_true))
    return int(r[np.argmin(-H_true[1:] + tau * r)])


# --------------------------------------------------------------------------- #
# metrics for one (run, rule)
# --------------------------------------------------------------------------- #
def future_gain(H_true: np.ndarray, r: int, horizon: int = HORIZON) -> float:
    """max_{r < m <= min(r + horizon, R)} (H_m - H_r); 0 if r = R."""
    R = len(H_true) - 1
    hi = min(r + horizon, R)
    return float(max(0.0, (H_true[r + 1:hi + 1] - H_true[r]).max())) if hi > r else 0.0


def stop_metrics(s: int, fired: bool, K: int, H_true: np.ndarray, H_star: float,
                 tau: float, q: int, w: int = 1) -> dict:
    R = len(H_true) - 1
    fg = future_gain(H_true, s)
    early = bool(s < K and s < R and fg > tau)
    cap = bool(not fired)
    # late: first round r >= 1 from which the true cumulative gain over the
    # next HORIZON rounds is <= tau; continuing past it wastes s - r* rounds
    r_star = next(r for r in range(1, R + 1) if future_gain(H_true, r) <= tau)
    wasted = max(0, s - r_star)
    # net of the rule's own detection delay: a w-round window needs w - 1
    # rounds after r* before it can fire
    wasted_net = max(0, wasted - (w - 1))
    # prompt 50 guard: tau <= 0 (exact, no epsilon) occurs only for Z-dis x
    # union box (no start inside R_union -> HV == 0 under every MC draw). The
    # /tau columns and the tau-comparison columns are undefined there -> NaN;
    # the rule itself was evaluated with tau as-is by the caller.
    degenerate = bool(tau <= 0)
    inv_tau = np.nan if degenerate else None
    out = {"stop": s, "fired": fired, "early": early, "cap": cap,
           "late": wasted > 0, "wasted": wasted, "late_net": wasted_net > 0,
           "wasted_net": wasted_net, "r_star": r_star,
           "future_gain_tau": fg * inv_tau if degenerate else fg / tau,
           "regret_star": (H_star - H_true[s]) / H_star,
           "regret_budget_tau": (H_true[R] - H_true[s]) * inv_tau if degenerate
           else (H_true[R] - H_true[s]) / tau,
           "regret_star_tau": (H_star - H_true[s]) * inv_tau if degenerate
           else (H_star - H_true[s]) / tau,
           "evals": s * q, "tau_degenerate": degenerate}
    if degenerate:
        for c in ("early", "late", "wasted", "late_net", "wasted_net", "r_star"):
            out[c] = np.nan
    return out


# --------------------------------------------------------------------------- #
# rule grid (pre-registered)
# --------------------------------------------------------------------------- #
TAU_MULTS = (0.25, 0.5, 1.0, 1.5, 2.0)
TAU_PCTS = (0.01, 0.02, 0.05, 0.08, 0.10)
WINDOWS = (1, 2, 3)
CAPS = (4, 8)
REL_CS = (0.01, 0.02, 0.05)


def apply_all(traj: dict) -> list[dict]:
    """traj: H_obs, H_true (R+1,), H_star, tau, q, method, ehvi (R,) or None.
    Returns one row per rule variant with its stop metrics."""
    Ho, Ht = np.asarray(traj["H_obs"], float), np.asarray(traj["H_true"], float)
    tau, q, Hs = float(traj["tau"]), int(traj["q"]), float(traj["H_star"])
    R = len(Ho) - 1
    gains = np.diff(Ho)
    rows = []

    def add(rule, params, K, sf):
        s, fired = sf
        rows.append({"rule": rule, **params, "K": K,
                     **stop_metrics(s, fired, K, Ht, Hs, tau, q, int(params.get("w", 1)))})

    for K in CAPS:
        for w in WINDOWS:
            for m in TAU_MULTS:
                add("S0", {"tau_kind": "mult", "tau_val": m, "w": w}, K, s0(gains, m * tau, w, K))
            for p in TAU_PCTS:
                add("S0", {"tau_kind": "pct", "tau_val": p, "w": w}, K,
                    s0(gains, p * Ho[0], w, K))
        for c in REL_CS:
            add("S-rel", {"c": c}, K, s_rel(gains, Ho, c, K))
        add("S-OCD", {}, K, s_ocd(gains, tau, K=K))
        if traj.get("ehvi") is not None:
            for w in WINDOWS:
                add("S-model", {"w": w}, K, s_model(np.asarray(traj["ehvi"], float), tau, w, K))
    for k in range(1, R + 1):
        add("S-fix", {"k": k}, R, s_fix(k, R))
    o = oracle(Ht, tau)
    add("Oracle", {}, R, (o, True))
    return rows


def apply_q4(traj: dict) -> list[dict]:
    """Block D (q = 4, 16 rounds): S0 (w = 2, cap = 8 rounds = 32 evals,
    the live evaluation budget) with tau unscaled, tau * q/8, and a
    16-evaluation window (w = 4 rounds of 4, tau unscaled)."""
    Ho, Ht = np.asarray(traj["H_obs"], float), np.asarray(traj["H_true"], float)
    tau, q, Hs = float(traj["tau"]), int(traj["q"]), float(traj["H_star"])
    gains = np.diff(Ho)
    K = 32 // q
    out = []
    for name, t, w in (("unscaled", tau, 2), ("scaled_q/8", tau * q / 8, 2), ("window16", tau, 16 // q)):
        s, f = s0(gains, t, w, K)
        out.append({"rule": "S0-q4", "variant": name, "w": w, "K": K,
                    **stop_metrics(s, f, K, Ht, Hs, tau, q, w)})
    return out


def bootstrap_ci(x: np.ndarray, stat=np.mean, n_boot: int = 10_000, seed: int = 20261012,
                 groups: np.ndarray | None = None) -> tuple[float, float, float]:
    """Seed-bootstrap 95 % percentile CI. With `groups` (e.g. problem id for
    the pooled E-path cell) resampling is stratified within group."""
    x = np.asarray(x, float)
    rng = np.random.default_rng(seed)
    if groups is None:
        bs = np.array([stat(x[rng.integers(0, len(x), len(x))]) for _ in range(n_boot)])
    else:
        groups = np.asarray(groups)
        parts = [np.flatnonzero(groups == g) for g in np.unique(groups)]
        bs = np.array([stat(np.concatenate([x[p[rng.integers(0, len(p), len(p))]]
                                            for p in parts])) for _ in range(n_boot)])
    return float(stat(x)), float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))
