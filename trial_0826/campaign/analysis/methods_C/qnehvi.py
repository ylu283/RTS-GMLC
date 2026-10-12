"""Prompt 35 §3.2 — qNEHVI acquirer for arm N1 (env `bogp-botorch` / `BOGP_CRC_botorch`).

BoTorch `qNoisyExpectedHypervolumeImprovement`, q members chosen by
sequential greedy over a DISCRETE candidate set (evaluated rows excluded),
fixed MC sampler seed, float64. BoTorch maximizes, so objectives AND the
reference point are negated (after the same per-objective z-scoring the
model uses — an affine map per axis, which preserves HV argmax).

Model: one SingleTaskGP per objective (ModelListGP), mirroring
acquire_next.PredGP — z-scored X and y, ScaleKernel(Matern-5/2, ARD),
ConstantMean, Gaussian noise LOWER-BOUNDED at (floor / sigma_y)^2 (not
fixed), trained by the same bogp `train_gp` loop (Adam, 700 epochs, lr 0.01).
Remaining differences vs q-ParEGO's model (listed in METHODS_C.md):
  1. q-ParEGO fits ONE GP to an augmented-Tchebycheff scalarization per
     batch member (default likelihood, Adam 300 epochs lr 0.05, float32);
     qNEHVI models the M objectives jointly-independent and integrates HVI;
  2. float64 here vs float32 in bogp's q-ParEGO / PredGP;
  3. noise lower bound at the floor (PredGP's grading layer) vs q-ParEGO's
     unconstrained default noise;
  4. q-ParEGO normalizes objectives by the observed ideal/nadir; qNEHVI
     uses z-scored objectives against a fixed reference point;
  5. kriging-believer fantasies (q-ParEGO) vs qNEHVI's joint MC posterior
     over pending points (sequential greedy with X_pending).
"""

from __future__ import annotations

import os
import sys
import time

import numpy as np

_BOGP_PATH = os.environ.get("BOGP_PATH")
if _BOGP_PATH and _BOGP_PATH not in sys.path:
    sys.path.insert(0, _BOGP_PATH)

import torch  # noqa: E402
import gpytorch  # noqa: E402
from gpytorch.constraints import GreaterThan  # noqa: E402

from bogp.gp_model import train_gp  # noqa: E402

MC_SAMPLES = 128
MAX_BATCH_SIZE = 512
DTYPE = torch.float64


def _single_task_gp(tx, ty, floor_var):
    from botorch.models import SingleTaskGP
    kernel = gpytorch.kernels.ScaleKernel(
        gpytorch.kernels.MaternKernel(nu=2.5, ard_num_dims=tx.shape[1]))
    lik = gpytorch.likelihoods.GaussianLikelihood(
        noise_constraint=GreaterThan(floor_var))
    model = SingleTaskGP(tx, ty.unsqueeze(-1), likelihood=lik, covar_module=kernel,
                         mean_module=gpytorch.means.ConstantMean(),
                         outcome_transform=None, input_transform=None)
    model = model.to(DTYPE)
    # bogp's loop expects a (n,) target; SingleTaskGP stores (n,) for m = 1
    train_gp(model, model.likelihood, tx, model.train_targets)
    model.eval()
    return model


def fit_model(X, Y, floors):
    """Return (model_list, transform) with transform = (mx, sx, my, sy)."""
    from botorch.models import ModelListGP
    X = np.asarray(X, float); Y = np.asarray(Y, float)
    mx = X.mean(0); sx = np.where(X.std(0) <= 0, 1.0, X.std(0))
    my = Y.mean(0); sy = np.where(Y.std(0) <= 0, 1.0, Y.std(0))
    tx = torch.tensor((X - mx) / sx, dtype=DTYPE)
    # negate AFTER z-scoring: BoTorch maximizes
    tyn = -(Y - my) / sy
    models = [_single_task_gp(tx, torch.tensor(tyn[:, j], dtype=DTYPE),
                              float((floors[j] / sy[j]) ** 2))
              for j in range(Y.shape[1])]
    return ModelListGP(*models), (mx, sx, my, sy)


def propose_qnehvi_batch(X, Y, candidates, ref_point, floors, q=8, seed=0,
                         mc_samples=MC_SAMPLES, max_batch_size=MAX_BATCH_SIZE,
                         log=print):
    """q designs from `candidates` (raw units) by sequential-greedy qNEHVI.

    X (n, d), Y (n, M) raw units, all objectives minimized; ref_point (M,)
    raw units (minimization convention). Returns dict(x_batch, cand_idx,
    acq_values, seconds)."""
    from botorch.acquisition.multi_objective import qNoisyExpectedHypervolumeImprovement
    from botorch.optim import optimize_acqf_discrete
    from botorch.sampling import SobolQMCNormalSampler

    t0 = time.time()
    torch.manual_seed(seed)
    model, (mx, sx, my, sy) = fit_model(X, Y, floors)
    ref_t = torch.tensor(-(np.asarray(ref_point, float) - my) / sy, dtype=DTYPE)
    cand = np.asarray(candidates, float)
    observed = np.zeros(len(cand), bool)
    for xo in np.asarray(X, float):
        observed |= np.all(np.isclose(cand, xo, rtol=0.0, atol=1e-12), axis=1)
    keep = np.flatnonzero(~observed)
    cand_t = torch.tensor((cand[keep] - mx) / sx, dtype=DTYPE)
    tx = torch.tensor((np.asarray(X, float) - mx) / sx, dtype=DTYPE)
    acq = qNoisyExpectedHypervolumeImprovement(
        model=model, ref_point=ref_t, X_baseline=tx,
        sampler=SobolQMCNormalSampler(sample_shape=torch.Size([mc_samples]), seed=seed),
        prune_baseline=True, cache_root=True)
    log(f"qNEHVI: model fit + setup {time.time() - t0:.1f} s; {len(keep)} candidates")
    with torch.no_grad():
        xb, vals = optimize_acqf_discrete(acq, q=q, choices=cand_t,
                                          max_batch_size=max_batch_size, unique=True)
    xb = xb.numpy()
    # map back to candidate rows (exact: same float64 transform of the same rows)
    picks = []
    ct = cand_t.numpy()
    for row in xb:
        hit = np.flatnonzero(np.all(np.isclose(ct, row, rtol=0, atol=1e-9), axis=1))
        assert len(hit) == 1, f"ambiguous candidate match ({len(hit)})"
        picks.append(int(keep[hit[0]]))
    assert len(set(picks)) == q, "duplicate picks"
    return {"x_batch": cand[picks], "cand_idx": np.array(picks),
            "acq_values": vals.numpy() if hasattr(vals, "numpy") else np.asarray(vals),
            "seconds": time.time() - t0}
