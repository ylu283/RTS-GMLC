"""Prompt 37 — shared machinery for the stop-rule validation (0 PCM runs).

Everything here is COPIED from the frozen Stage-2 code (analysis/bo_stage2/
acquire_next.py @ d1e3814) or the Stage-1 replay (analysis/bo_replay/
replay.py) rather than imported, because prompt 35 is editing
acquire_next.py concurrently. Copies are marked with their source.

Conventions: all objectives minimized; HV = bogp `hypervolume_exact`
(bo-gp feat/qparego @ 60e6328, frozen) on raw objective units.
"""

from __future__ import annotations

import itertools
import os
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
CAMPAIGN = HERE.parents[1]
BOGP_PATH = os.environ.get("BOGP_PATH", "/Users/yilu/Documents/GitHub/bo-gp-qparego")
if BOGP_PATH not in sys.path:
    sys.path.insert(0, BOGP_PATH)
if str(CAMPAIGN) not in sys.path:
    sys.path.insert(0, str(CAMPAIGN))

import bogp  # noqa: E402
from bogp.mobo.pareto import hypervolume_exact  # noqa: E402

BOGP_SHA = "60e6328"


def assert_bogp() -> str:
    """Prompt-37 §1: bogp must resolve to BOGP_PATH (both conda envs otherwise
    resolve it to GitHub/bo-gp, which lacks mobo/qparego.py) at SHA 60e6328,
    and the user site must be off. Returns the full SHA."""
    import subprocess

    assert os.environ.get("PYTHONNOUSERSITE") == "1", "set PYTHONNOUSERSITE=1"
    root = os.path.realpath(BOGP_PATH)
    assert os.path.realpath(bogp.__file__).startswith(root + os.sep), \
        f"bogp resolved to {bogp.__file__}, not under {root}"
    sha = subprocess.run(["git", "-C", root, "rev-parse", "HEAD"], capture_output=True,
                         text=True, check=True).stdout.strip()
    assert sha.startswith(BOGP_SHA), f"bo-gp SHA {sha} != {BOGP_SHA}"
    return sha


# every entry point (runner, collector, problems, analysis, `python -c`) imports
# this module, so the bogp path/SHA check runs at import (prompt 37 §1)
BOGP_FULL_SHA = assert_bogp()

# ---- Stage-2 constants (copied from acquire_next.py) ---------------------- #
M_COLS = ["load_shed_mwh", "true_curtailment_mwh", "total_cost_less_synthetic_usd"]
FLOORS = np.array([3000.0, 5000.0, 0.5e6])   # pi_0911 §3.5, M order
MC_SEED = 20261006                            # threshold MC seed (prompt 30)
N_MC = 1000
HARD_CAP = 4
SORTED_TIERS = sorted(["nuclear", "wind_303", "wind_317", "wind_122", "pv", "tail"])
# tiers.STAGE2_LATTICE = np.round(linspace(0.05, 1.0, 9), 10)
LAT = np.round(np.linspace(0.05, 1.0, 9), 10)
D6 = 6
N_LATTICE = 9 ** D6                           # 531,441

# ---- prompt-37 seeds (pre-registered in PREREG.md) ------------------------ #
P37_SEED = 20261012          # base for starts / acquisition / noise streams
N_SEEDS = 20

PROBLEM_IDS = {  # stable integer ids for seed streams
    "R-A": 1, "R-B": 2, "R-C": 3,
    "E-mean": 20, "E-path-1": 21, "E-path-2": 22, "E-path-3": 23, "E-path-4": 24,
    "E-path-5": 25, "E-short": 26, "Z-needle": 31, "Z-plateau": 32, "Z-dis": 33,
}
METHOD_IDS = {"M1": 1, "M2": 2, "M3": 3, "M4": 4}


def problem_id(name: str) -> int:
    if name in PROBLEM_IDS:
        return PROBLEM_IDS[name]
    assert name.startswith("R-PG:"), name
    # pair grids: 100 + stable index in the sorted list of the 14 waves
    from problems import PAIRGRID_WAVES
    return 100 + PAIRGRID_WAVES.index(name.split(":", 1)[1])


def seed_int(*keys: int) -> int:
    """Deterministic 32-bit integer from a key tuple (SeedSequence)."""
    return int(np.random.SeedSequence([P37_SEED, *keys]).generate_state(1)[0])


# --------------------------------------------------------------------------- #
# lattice
# --------------------------------------------------------------------------- #
def lattice_candidates() -> np.ndarray:
    """The full 9^6 product, same order as acquire_next.lattice_candidates
    (itertools.product over LAT, last tier fastest)."""
    return np.array(list(itertools.product(LAT, repeat=D6)), dtype=float)


def lattice_index(levels: np.ndarray) -> np.ndarray:
    """(n, 6) integer levels 0..8 -> flat index into lattice_candidates()."""
    levels = np.atleast_2d(levels).astype(np.int64)
    w = 9 ** np.arange(D6 - 1, -1, -1)
    return levels @ w


def levels_of(idx: np.ndarray) -> np.ndarray:
    idx = np.atleast_1d(np.asarray(idx, np.int64))
    out = np.empty((len(idx), D6), np.int64)
    r = idx.copy()
    for j in range(D6 - 1, -1, -1):
        out[:, j] = r % 9
        r //= 9
    return out


def x_to_index(X: np.ndarray) -> np.ndarray:
    """Omega rows on the lattice -> flat index (exact match required)."""
    X = np.atleast_2d(X)
    lv = np.abs(X[:, :, None] - LAT[None, None, :]).argmin(axis=2)
    assert np.allclose(LAT[lv], X, atol=1e-9), "off-lattice design"
    return lattice_index(lv)


# --------------------------------------------------------------------------- #
# Pareto / HV
# --------------------------------------------------------------------------- #
def nd_mask_3d(Y: np.ndarray) -> np.ndarray:
    """Non-dominated mask (minimization) for M = 3, O(n log n) skyline.

    Sort by (f1, f2, f3); a point is dominated iff some earlier point has
    f2 <= and f3 <= (weak in all, given f1 <=). Exact duplicates: the first
    copy is kept, later copies are marked dominated. The processed set is
    summarized by its (f2, f3) staircase: f2 ascending, f3 strictly
    descending; the query is the min f3 over staircase points with f2 <= p.f2.
    """
    import bisect

    Y = np.asarray(Y, float)
    assert Y.ndim == 2 and Y.shape[1] == 3
    order = np.lexsort((Y[:, 2], Y[:, 1], Y[:, 0]))
    mask = np.zeros(len(Y), dtype=bool)
    s2: list[float] = []   # staircase f2, ascending
    s3: list[float] = []   # staircase f3, descending
    for i in order:
        a, b = Y[i, 1], Y[i, 2]
        k = bisect.bisect_right(s2, a)       # staircase points with f2 <= a
        if k > 0 and s3[k - 1] <= b:         # min f3 among them is s3[k-1]
            continue                          # weakly dominated (or duplicate)
        mask[i] = True
        # insert (a, b); drop staircase points it dominates (f2 >= a, f3 >= b)
        j = k
        while j < len(s2) and s3[j] >= b:
            j += 1
        s2[k:j] = [a]
        s3[k:j] = [b]
    return mask


def nd_mask(Y: np.ndarray) -> np.ndarray:
    Y = np.asarray(Y, float)
    if Y.shape[1] == 3:
        return nd_mask_3d(Y)
    # small-n generic path (2-D replay problems, M = 4): first copy of
    # duplicates kept, as in nd_mask_3d
    n = len(Y)
    mask = np.ones(n, dtype=bool)
    for i in range(n):
        le = np.all(Y <= Y[i], axis=1)
        lt = np.any(Y < Y[i], axis=1)
        dom = le & lt
        dup = np.all(Y == Y[i], axis=1)
        dup[i:] = False
        if dom.any() or dup.any():
            mask[i] = False
    return mask


def hv3d(Y: np.ndarray, ref: np.ndarray) -> float:
    """Exact 3-D hypervolume (minimization), O(n log n + n*k) sweep along f3
    with an incrementally maintained 2-D staircase area. For large fronts
    (truth sets); tested equal to bogp `hypervolume_exact` on random sets."""
    import bisect

    Y = np.atleast_2d(np.asarray(Y, float))
    ref = np.asarray(ref, float)
    Y = Y[np.all(Y < ref, axis=1)]
    if len(Y) == 0:
        return 0.0
    Y = Y[np.argsort(Y[:, 2], kind="stable")]
    r1, r2 = ref[0], ref[1]
    xs: list[float] = []   # staircase f1 ascending
    ys: list[float] = []   # staircase f2 strictly descending
    area = 0.0
    total = 0.0
    for k in range(len(Y)):
        a, b = Y[k, 0], Y[k, 1]
        kr = bisect.bisect_right(xs, a)
        if not (kr > 0 and ys[kr - 1] <= b):
            # newly covered area over [a, x_end) at height r2 - b, minus old
            kl = bisect.bisect_left(xs, a)
            j = kl
            while j < len(xs) and ys[j] >= b:
                j += 1
            x_end = xs[j] if j < len(xs) else r1
            # old heights on [a, x_end): piecewise, starting from the point
            # left of a (if any) then the removed points kl..j-1
            h_left = (r2 - ys[kl - 1]) if kl > 0 else 0.0
            x_prev, h_prev = a, h_left
            old = 0.0
            for t in range(kl, j):
                old += (xs[t] - x_prev) * h_prev
                x_prev, h_prev = xs[t], r2 - ys[t]
            old += (x_end - x_prev) * h_prev
            area += (x_end - a) * (r2 - b) - old
            xs[kl:j] = [a]
            ys[kl:j] = [b]
        z_next = Y[k + 1, 2] if k + 1 < len(Y) else ref[2]
        total += area * (z_next - Y[k, 2])
    return float(total)


def hv(Y: np.ndarray, ref: np.ndarray) -> float:
    Y = np.atleast_2d(np.asarray(Y, float))
    if len(Y) == 0:
        return 0.0
    keep = np.all(Y < ref, axis=1)
    if not keep.any():
        return 0.0
    Y = Y[keep]
    if len(Y) > 64:
        Y = Y[nd_mask(Y)]
    return float(hypervolume_exact(Y, np.asarray(ref, float)))


def frozen_ref(Y_starts: np.ndarray) -> np.ndarray:
    """R_frozen formula (prompt 30 cmd_init): nadir of the starts + 10 % span."""
    return Y_starts.max(axis=0) + 0.1 * (Y_starts.max(axis=0) - Y_starts.min(axis=0))


def mc_threshold(Y_starts: np.ndarray, ref: np.ndarray, floors: np.ndarray,
                 n_mc: int = N_MC, seed: int = MC_SEED) -> float:
    """tau (prompt 30 cmd_init): std (ddof 0) of HV over n_mc perturbations
    of ALL start points by N(0, floor^2), no clipping, fixed ref."""
    rng = np.random.default_rng(seed)
    vals = np.empty(n_mc)
    for i in range(n_mc):
        vals[i] = hypervolume_exact(Y_starts + rng.normal(0.0, floors, size=Y_starts.shape), ref)
    return float(np.std(vals, ddof=0))


def hv_trajectory(Y: np.ndarray, n_per_round: list[int], ref: np.ndarray) -> np.ndarray:
    """Cumulative HV after round 0..R, where n_per_round[k] = number of rows
    available after round k (round 0 = the starts)."""
    return np.array([hv(Y[:n], ref) for n in n_per_round])


# --------------------------------------------------------------------------- #
# prediction GP (COPY of acquire_next.PredGP, plus a latent-sd option and
# float64 closed-form LOO in physical units). Layer ii: per objective,
# Matern-2.5 ARD, noise variance floored at floor^2.
# --------------------------------------------------------------------------- #
class PredGP:
    def __init__(self, X: np.ndarray, y: np.ndarray, floor: float):
        import gpytorch
        import torch
        from gpytorch.constraints import GreaterThan
        from bogp.gp_model import GPRegressionModel, train_gp

        self.mx = X.mean(axis=0)
        self.sx = np.where(X.std(axis=0) <= 0, 1.0, X.std(axis=0))
        self.my = float(y.mean())
        self.sy = float(np.std(y, ddof=0)) or 1.0
        floor_var = (floor / self.sy) ** 2
        tx = torch.tensor((X - self.mx) / self.sx, dtype=torch.float32)
        ty = torch.tensor((y - self.my) / self.sy, dtype=torch.float32)
        kernel = gpytorch.kernels.ScaleKernel(
            gpytorch.kernels.MaternKernel(nu=2.5, ard_num_dims=X.shape[1]))
        self.lik = gpytorch.likelihoods.GaussianLikelihood(
            noise_constraint=GreaterThan(floor_var))
        self.model = GPRegressionModel(tx, ty, self.lik, kernel)
        train_gp(self.model, self.lik, tx, ty)
        self.model.eval(); self.lik.eval()
        self._tx, self._ty = tx, ty

    def predict(self, Xq: np.ndarray, latent: bool = False,
                chunk: int = 50_000) -> tuple[np.ndarray, np.ndarray]:
        """Physical-unit posterior mean and sd. latent=False (default, as in
        acquire_next): noise-inclusive predictive sd; latent=True: f only."""
        import gpytorch
        import torch

        Xq = np.atleast_2d(Xq)
        ms, ss = [], []
        for i in range(0, len(Xq), chunk):
            xq = torch.tensor((Xq[i:i + chunk] - self.mx) / self.sx, dtype=torch.float32)
            with torch.no_grad(), gpytorch.settings.fast_pred_var():
                post = self.model(xq) if latent else self.lik(self.model(xq))
                ms.append(post.mean.numpy() * self.sy + self.my)
                ss.append(post.stddev.numpy() * self.sy)
        return np.concatenate(ms).astype(float), np.concatenate(ss).astype(float)

    def loo_residuals(self) -> np.ndarray:
        """Closed-form LOO residuals y_i - mu_{-i}, PHYSICAL units (float64)."""
        import torch

        with torch.no_grad():
            K = self.model.covar_module(self._tx).evaluate().double()
            Kn = K + self.lik.noise.double() * torch.eye(len(self._tx), dtype=torch.float64)
            Ki = torch.linalg.inv(Kn)
            mu0 = self.model.mean_module.constant.double()
            alpha = Ki @ (self._ty.double() - mu0)
            return (alpha / Ki.diagonal()).numpy() * self.sy

    def loo_sd(self) -> np.ndarray:
        """Closed-form LOO predictive sd (noise-inclusive), physical units."""
        import torch

        with torch.no_grad():
            K = self.model.covar_module(self._tx).evaluate().double()
            Kn = K + self.lik.noise.double() * torch.eye(len(self._tx), dtype=torch.float64)
            Ki = torch.linalg.inv(Kn)
            return np.sqrt(1.0 / Ki.diagonal().numpy()) * self.sy


def fit_prediction_gps(X: np.ndarray, Y: np.ndarray, floors: np.ndarray) -> list[PredGP]:
    return [PredGP(X, Y[:, j], float(floors[j])) for j in range(Y.shape[1])]


# --------------------------------------------------------------------------- #
# calibration audit (same statistic as BO_STAGE2 §3)
# --------------------------------------------------------------------------- #
RMS_BAND = (0.7, 1.3)
COV_MIN = 0.80


def calibration_stats(y_obs: np.ndarray, mean: np.ndarray, sd: np.ndarray) -> dict:
    z = (np.asarray(y_obs) - mean) / sd
    rms = float(np.sqrt(np.mean(z ** 2)))
    cov = float(np.mean(np.abs(z) <= 1.96))
    return {"mean_z": float(z.mean()), "rms_z": rms, "cov95": cov,
            "calibrated": bool(RMS_BAND[0] <= rms <= RMS_BAND[1] and cov >= COV_MIN)}


# --------------------------------------------------------------------------- #
# chunked EI patch (COPY of acquire_next._ei_chunked — evaluation-context
# adaptation that bounds gpytorch memory on 531,441 candidates; the library
# file at 60e6328 is untouched)
# --------------------------------------------------------------------------- #
def install_chunked_ei(chunk: int = 20_000) -> None:
    import bogp.mobo.qparego as _qparego
    from bogp.acquisition import expected_improvement as _ei_pointwise

    if getattr(_qparego.expected_improvement, "_p37_chunked", False):
        return

    def _ei_chunked(x, model, f_best, xi=0.01):
        out = [_ei_pointwise(x[i:i + chunk], model, f_best, xi=xi)
               for i in range(0, len(x), chunk)]
        return np.concatenate(out)

    _ei_chunked._p37_chunked = True
    _qparego.expected_improvement = _ei_chunked


def set_threads(n: int = 4) -> None:
    for v in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS",
              "VECLIB_MAXIMUM_THREADS"):
        os.environ.setdefault(v, str(n))
    try:
        import torch
        torch.set_num_threads(n)
    except ImportError:
        pass
