"""Prompt 34 T2 — subset-percentile machinery for the random baseline.

The primary statistic treats the 48 random designs as ONE i.i.d. pool: every
function here takes plain objective matrices (M order, raw units) and never
sees the `arm` provenance column. Worker functions live at module level so
`multiprocessing` (spawn on macOS) can pickle them.
"""

from __future__ import annotations

import os
import sys

import numpy as np

M_COLS = ["load_shed_mwh", "true_curtailment_mwh", "total_cost_less_synthetic_usd"]
FLOORS = np.array([3000.0, 5000.0, 0.5e6])  # M order (prompt-30 floors)
SUBSET_SEED = 20261012   # §3.1 sampler seed
PERTURB_SEED = 20261006  # §3.3 (the prompt-30 MC seed)
TIE_REL = 1e-12


def _hv():
    bogp = os.environ.get("BOGP_PATH", "/Users/yilu/Documents/GitHub/bo-gp-qparego")
    if bogp not in sys.path:
        sys.path.insert(0, bogp)
    from bogp.mobo.pareto import hypervolume_exact
    return hypervolume_exact


def pool_matrix(df):
    """The random pool as an (n, 3) matrix in `index` order. Ignores `arm`."""
    return df.sort_values("index")[M_COLS].to_numpy(float)


def subset_positions(rng, n_pool, size, n_subsets):
    """`n_subsets` draws of `size` positions without replacement from 0..n_pool-1."""
    return np.argsort(rng.random((n_subsets, n_pool)), axis=1)[:, :size]


def subset_hvs(Y_starts, Y_pool, positions, ref, hv=None):
    hv = hv or _hv()
    return np.array([hv(np.vstack([Y_starts, Y_pool[p]]), ref) for p in positions])


def percentile_of(bo_hv, hvs):
    """Fraction of subset HVs below BO's; ties within 1e-12 relative count 1/2."""
    tie = np.abs(hvs - bo_hv) <= TIE_REL * abs(bo_hv)
    return float(((hvs < bo_hv) & ~tie).mean() + 0.5 * tie.mean())


def p_hat(Y_starts, Y_pool, bo_hv, ref, size, n_subsets, rng, hv=None):
    pos = subset_positions(rng, len(Y_pool), size, n_subsets)
    hvs = subset_hvs(Y_starts, Y_pool, pos, ref, hv)
    return percentile_of(bo_hv, hvs), hvs


# ---- bootstrap over the pool (one replicate per task) -------------------- #

def boot_task(args):
    """Replicate b: resample the pool with replacement, then draw subsets BY
    POSITION (a duplicated design can appear twice in one subset)."""
    b, Y_starts, Y_pool, bo_hv, ref, size, n_subsets = args
    rng = np.random.default_rng([SUBSET_SEED, 1, size, b])
    Yb = Y_pool[rng.integers(0, len(Y_pool), len(Y_pool))]
    p, _ = p_hat(Y_starts, Yb, bo_hv, ref, size, n_subsets, rng)
    return p


# ---- §3.3 paired floor perturbation (one draw per task) ------------------ #

def perturb_task(args):
    """Draw d: N(0, floor^2) per objective added to every evaluated point; the
    32 starts get ONE common perturbation used for both BO and the subsets.
    R_frozen fixed; HV0 recomputed from the perturbed starts."""
    d, Y_starts, Y_bo, Y_pool, ref, n_subsets = args
    hv = _hv()
    rng = np.random.default_rng([PERTURB_SEED, d])
    S = Y_starts + rng.normal(0, FLOORS, Y_starts.shape)
    B = Y_bo + rng.normal(0, FLOORS, Y_bo.shape)
    P = Y_pool + rng.normal(0, FLOORS, Y_pool.shape)
    hv0 = hv(S, ref)
    bo_hv = hv(np.vstack([S, B]), ref)
    p, _ = p_hat(S, P, bo_hv, ref, len(Y_bo), n_subsets, rng, hv)
    return p, bo_hv / hv0


def verdict_row(p, lo=None, hi=None):
    """§3.2 rows. With no interval -> the §3.3 point row only."""
    if lo is None:
        return "above" if p >= 0.90 else ("matched" if p <= 0.10 else "comparable")
    if p >= 0.90 and lo >= 0.50:
        return "above"
    if p <= 0.10 and hi <= 0.50:
        return "matched"
    return "comparable"
