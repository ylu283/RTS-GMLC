"""Stage-1 discrete-BO replay harness on the 303x317 contour grids.

Prompt 21 / math-log §5.1. Candidate set = the 81 evaluated designs of a
scenario; every "evaluation" is a table lookup. All objectives are
minimized (Δ vs base, negative = improvement).

NO-LEAKAGE RULE (math-log §5.1, hard): inside every replay loop the GP,
its hyperparameters and the input/output scalers are fit ONLY on the
points queried so far. Nothing here calls `.fit(` on the full table; the
only full-table quantities are the *metric definitions* — grid minimum +
noise floor for "optimum found", and the ideal/nadir/reference point of
the hypervolume ratio — which define what is measured, not what the
optimizer knows. `QueriedGP` is the single fit path, and it only ever
receives the queried rows.

Requires bo-gp (branch feat/qparego) on PYTHONPATH for
`bogp.mobo.pareto.hypervolume_exact` (exact any-M hypervolume) and
`bogp.mobo.qparego` (the scalarization/weights shared with T-M8 and the
q-ParEGO batch loop for the smoke test).
"""

from __future__ import annotations

import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import norm, qmc
from sklearn.exceptions import ConvergenceWarning
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import ConstantKernel, Matern, WhiteKernel

HERE = Path(__file__).resolve().parent
CAMPAIGN = HERE.parents[1]
if str(CAMPAIGN) not in sys.path:
    sys.path.insert(0, str(CAMPAIGN))
from tiers import SOBOL_SEED  # noqa: E402  (single source of truth: 20260821)

from bogp.mobo.pareto import hypervolume_exact, non_dominated_mask  # noqa: E402
from bogp.mobo.qparego import (  # noqa: E402
    RHO_AUG,
    normalize_objectives,
    sample_simplex_weights,
    scalarize_tchebycheff,
)

SCENARIOS = ["A", "B", "C"]
INPUTS = ["wind_303_omega", "wind_317_omega"]
OBJECTIVES = [
    "delta_cost_less_synthetic_usd_APPROX",
    "delta_curtailment_mwh",
    "delta_load_shed_mwh",
    "delta_thermal_starts",
]
SHORT = {
    "delta_cost_less_synthetic_usd_APPROX": "cost",
    "delta_curtailment_mwh": "curt",
    "delta_load_shed_mwh": "shed",
    "delta_thermal_starts": "starts",
}
UNITS = {"cost": "M$", "curt": "GWh", "shed": "GWh", "starts": "starts"}
SCALE = {"cost": 1e-6, "curt": 1e-3, "shed": 1e-3, "starts": 1.0}

# Established floors (campaign noise model): shed 3,000 MWh, curtailment
# 5,000 MWh, cost $0.5M. Starts has NO established floor: 60 is a WORKING
# ASSUMPTION for this replay only (quadratic-surface residual RMSE ~48-54,
# rounded up), see REPLAY.md.
ESTABLISHED_FLOORS = {
    "delta_cost_less_synthetic_usd_APPROX": 0.5e6,
    "delta_curtailment_mwh": 5_000.0,
    "delta_load_shed_mwh": 3_000.0,
}
STARTS_WORKING_FLOOR = 60.0
STARTS_FLOOR_SENSITIVITY = (30.0, 60.0, 120.0)

N_INIT = 5           # random init cells per BO seed (stated choice; Stage 2 uses Sobol n0 = 16)
BO_SEEDS = range(20)
RANDOM_SEEDS = range(100)
HV_LEVELS = (0.90, 0.95, 0.99)


def floors() -> dict[str, float]:
    f = dict(ESTABLISHED_FLOORS)
    f["delta_thermal_starts"] = STARTS_WORKING_FLOOR
    return f


# --------------------------------------------------------------------------- #
# data
# --------------------------------------------------------------------------- #
def load_scenario(tag: str) -> pd.DataFrame:
    """81-row table: index, the two inputs, the M = 4 objectives (joined on `index`)."""
    wdir = CAMPAIGN / "waves" / f"contour_303x317_{tag}"
    dm = pd.read_csv(wdir / "design_matrix.csv")
    obj = pd.read_csv(wdir / "objectives.csv")
    df = dm[["index", *INPUTS]].merge(obj[["index", *OBJECTIVES]], on="index", how="inner")
    df = df.sort_values("index").reset_index(drop=True)
    assert len(df) == 81, f"{tag}: expected 81 rows, got {len(df)}"
    assert df[OBJECTIVES].notna().all().all(), f"{tag}: NaN objectives"
    return df


def xy(df: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    return df[INPUTS].to_numpy(float), df[OBJECTIVES].to_numpy(float)


# --------------------------------------------------------------------------- #
# surface diagnostics (honesty exhibit; full-table fits are NOT part of any loop)
# --------------------------------------------------------------------------- #
def quadratic_fit_stats(X: np.ndarray, y: np.ndarray) -> dict:
    """Full quadratic (6 terms) least squares: R^2 and residual RMSE (dof = n - 6)."""
    x1, x2 = X[:, 0], X[:, 1]
    A = np.column_stack([np.ones_like(x1), x1, x2, x1 * x1, x2 * x2, x1 * x2])
    coef, *_ = np.linalg.lstsq(A, y, rcond=None)
    resid = y - A @ coef
    ss_res = float(resid @ resid)
    ss_tot = float(((y - y.mean()) ** 2).sum())
    n, p = A.shape
    return {
        "r2": 1.0 - ss_res / ss_tot,
        "rmse_dof": float(np.sqrt(ss_res / (n - p))),
        "rmse_n": float(np.sqrt(ss_res / n)),
    }


def front_mask(Y: np.ndarray) -> np.ndarray:
    """Non-dominated mask, minimization, duplicates counted once."""
    _, first = np.unique(Y, axis=0, return_index=True)
    mask = np.zeros(len(Y), dtype=bool)
    sub = np.sort(first)
    mask[sub[non_dominated_mask(-Y[sub])]] = True
    return mask


def weakly_dominated_by(Y: np.ndarray, i: int) -> int:
    """Number of rows (excluding i) that row i weakly dominates (<= in every objective)."""
    return int(np.sum(np.all(Y[i] <= Y, axis=1)) - 1)


# --------------------------------------------------------------------------- #
# orderings
# --------------------------------------------------------------------------- #
def lattice_levels(X: np.ndarray) -> list[np.ndarray]:
    return [np.unique(X[:, j]) for j in range(X.shape[1])]


def sobol_order(X: np.ndarray, seed: int = SOBOL_SEED) -> np.ndarray:
    """Sobol ordering of the 81 cells: scrambled Sobol in [0,1]^2 (seed=20260821,
    fresh engine), each point mapped linearly onto the design box and snapped to
    the nearest lattice cell; already-visited cells are skipped; draw until all
    81 are ordered. The design matrices are raster-ordered — row order is NOT
    Sobol and is never used."""
    levels = lattice_levels(X)
    lo = np.array([lv.min() for lv in levels])
    hi = np.array([lv.max() for lv in levels])
    cell_of = {tuple(np.round(row, 9)): i for i, row in enumerate(X)}
    engine = qmc.Sobol(X.shape[1], scramble=True, seed=seed)
    order, seen = [], set()
    while len(order) < len(X):
        u = engine.random(128)
        for pt in lo + u * (hi - lo):
            snapped = tuple(np.round([lv[np.argmin(np.abs(lv - p))] for lv, p in zip(levels, pt)], 9))
            i = cell_of[snapped]
            if i not in seen:
                seen.add(i)
                order.append(i)
                if len(order) == len(X):
                    break
    return np.array(order, dtype=int)


def random_order(n: int, seed: int) -> np.ndarray:
    return np.random.default_rng(seed).permutation(n)


# --------------------------------------------------------------------------- #
# GP on queried points only
# --------------------------------------------------------------------------- #
class QueriedGP:
    """Matérn-2.5 ARD GP (sklearn) whose input scaler, output scaler and
    hyperparameters are fit on the queried points passed to `fit` — nothing else.
    `normalize_y=True` standardizes on the training targets only; inputs are
    min-max scaled on the training inputs only."""

    def __init__(self, seed: int = 0, n_restarts: int = 1, warm_start: bool = True):
        self.seed = seed
        self.n_restarts = n_restarts
        self.warm_start = warm_start
        self._kernel = None
        self._gpr = None
        self._lo = None
        self._span = None

    def _base_kernel(self, d: int):
        return (
            ConstantKernel(1.0, (1e-3, 1e3))
            * Matern(length_scale=np.ones(d), length_scale_bounds=(1e-2, 1e1), nu=2.5)
            + WhiteKernel(1e-4, (1e-6, 1e0))
        )

    def fit(self, Xq: np.ndarray, yq: np.ndarray) -> "QueriedGP":
        Xq = np.asarray(Xq, float)
        self._lo = Xq.min(axis=0)
        span = Xq.max(axis=0) - self._lo
        self._span = np.where(span <= 0, 1.0, span)
        kernel = self._kernel if (self.warm_start and self._kernel is not None) else self._base_kernel(Xq.shape[1])
        self._gpr = GaussianProcessRegressor(
            kernel=kernel, normalize_y=True, n_restarts_optimizer=self.n_restarts,
            random_state=self.seed, alpha=1e-8,
        )
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", ConvergenceWarning)
            self._gpr.fit((Xq - self._lo) / self._span, np.asarray(yq, float))
        self._kernel = self._gpr.kernel_
        return self

    def predict(self, Xc: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        # numpy on Apple Accelerate emits a spurious "divide by zero encountered in
        # matmul" RuntimeWarning on small finite matmuls (verified: finite alpha_,
        # finite K_trans); silence it and assert finiteness instead.
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            mu, sd = self._gpr.predict((np.asarray(Xc, float) - self._lo) / self._span, return_std=True)
        assert np.all(np.isfinite(mu)) and np.all(np.isfinite(sd)), "non-finite GP prediction"
        return mu, sd


def expected_improvement_min(mu: np.ndarray, sd: np.ndarray, f_best: float) -> np.ndarray:
    """EI for minimization; zero where the posterior is (numerically) certain."""
    sd = np.asarray(sd, float)
    imp = f_best - np.asarray(mu, float)
    ok = sd > 1e-12
    z = np.zeros_like(imp)
    z[ok] = imp[ok] / sd[ok]
    ei = np.where(ok, imp * norm.cdf(z) + sd * norm.pdf(z), 0.0)
    return np.clip(ei, 0.0, None)


def _argmax_tiebreak(vals: np.ndarray, rng: np.random.Generator) -> int:
    top = np.flatnonzero(vals >= vals.max() - 1e-12 * max(1.0, abs(vals.max())))
    return int(rng.choice(top))


def bo_single_order(X: np.ndarray, y: np.ndarray, seed: int, n_init: int = N_INIT) -> np.ndarray:
    """Single-objective BO replay: random init, then argmax-EI over the remaining
    candidates until all are queried. Returns the query order (indices)."""
    n = len(X)
    rng = np.random.default_rng(seed)
    order = list(rng.choice(n, n_init, replace=False))
    remaining = np.ones(n, dtype=bool)
    remaining[order] = False
    gp = QueriedGP(seed=seed)
    while remaining.any():
        q = np.array(order)
        gp.fit(X[q], y[q])                      # queried points only
        cand = np.flatnonzero(remaining)
        mu, sd = gp.predict(X[cand])
        ei = expected_improvement_min(mu, sd, float(y[q].min()))
        pick = cand[_argmax_tiebreak(ei, rng)]
        order.append(int(pick))
        remaining[pick] = False
    return np.array(order, dtype=int)


def parego_order(
    X: np.ndarray, Y: np.ndarray, seed: int, n_init: int = N_INIT, rho: float = RHO_AUG
) -> np.ndarray:
    """Sequential (q = 1) ParEGO replay: each iteration draws a simplex-uniform
    weight, normalizes the QUERIED objectives to [0,1] by their own ideal/nadir,
    fits the GP on the augmented-Tchebycheff scalarization of the queried points
    and picks argmax EI over the remaining candidates. Same scalarization,
    weights and rho as bogp.mobo.qparego (T-M8)."""
    n = len(X)
    rng = np.random.default_rng(seed)
    order = list(rng.choice(n, n_init, replace=False))
    remaining = np.ones(n, dtype=bool)
    remaining[order] = False
    gp = QueriedGP(seed=seed)
    while remaining.any():
        q = np.array(order)
        w = sample_simplex_weights(1, Y.shape[1], rng)[0]
        y_norm, _, _ = normalize_objectives(Y[q])       # queried points only
        g = scalarize_tchebycheff(y_norm, w, rho=rho)
        gp.fit(X[q], g)
        cand = np.flatnonzero(remaining)
        mu, sd = gp.predict(X[cand])
        ei = expected_improvement_min(mu, sd, float(g.min()))
        pick = cand[_argmax_tiebreak(ei, rng)]
        order.append(int(pick))
        remaining[pick] = False
    return np.array(order, dtype=int)


# --------------------------------------------------------------------------- #
# metrics
# --------------------------------------------------------------------------- #
def best_so_far(order: np.ndarray, y: np.ndarray) -> np.ndarray:
    return np.minimum.accumulate(y[order])


def evals_to_optimum(order: np.ndarray, y: np.ndarray, floor: float) -> int:
    """First n (1-based) with best-so-far <= grid-min + floor."""
    hit = np.flatnonzero(best_so_far(order, y) <= y.min() + floor)
    return int(hit[0]) + 1


def hv_reference(Y: np.ndarray) -> dict:
    """Per-scenario ideal, nadir and reference = nadir + 0.1 (nadir - ideal), on
    the full 81 (defines the metric, not the optimizer's information)."""
    ideal = Y.min(axis=0)
    nadir = Y.max(axis=0)
    return {"ideal": ideal, "nadir": nadir, "ref": nadir + 0.1 * (nadir - ideal)}


def hv_curve(order: np.ndarray, Y: np.ndarray, ref: np.ndarray, hv_all: float | None = None) -> np.ndarray:
    """n -> HV(first n queried) / HV(all rows). Exact hypervolume; recomputed
    only when the new point is not weakly dominated by the current set."""
    if hv_all is None:
        hv_all = hypervolume_exact(Y, ref)
    out = np.empty(len(order))
    cur = 0.0
    for k, i in enumerate(order):
        if k == 0 or not np.any(np.all(Y[order[:k]] <= Y[i], axis=1)):
            cur = hypervolume_exact(Y[order[: k + 1]], ref)
        out[k] = cur / hv_all
    return out


def n_at_recovery(curve: np.ndarray, level: float) -> int:
    hit = np.flatnonzero(curve >= level - 1e-12)
    return int(hit[0]) + 1 if len(hit) else len(curve) + 1


def summarize(values: np.ndarray) -> dict:
    v = np.asarray(values, float)
    return {"median": float(np.median(v)), "q25": float(np.percentile(v, 25)),
            "q75": float(np.percentile(v, 75)), "mean": float(v.mean()),
            "min": float(v.min()), "max": float(v.max()), "n": int(len(v))}


def band(curves: np.ndarray, lo: float = 20, hi: float = 80) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    c = np.asarray(curves, float)
    return np.median(c, axis=0), np.percentile(c, lo, axis=0), np.percentile(c, hi, axis=0)
