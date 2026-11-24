"""Prompt 55 — qNEHVI acquirer over the CONTINUOUS u-box [0, 1]^d (env bogp-botorch).

Pinned block (arms_E.json["qnehvi"]): botorch
`qNoisyExpectedHypervolumeImprovement`, ref_point = R (landing_R.json,
restricted to the objective list), alpha = 0.0 (exact partitioning at M = 4),
prune_baseline = True, `SobolQMCNormalSampler(sample_shape=128, seed=s)`,
`optimize_acqf(bounds=[0,1]^d, q=8, num_restarts=20, raw_samples=512,
sequential=True)`; `torch.manual_seed(s)` once per process before sampler
construction and optimisation. BoTorch maximizes, so objectives AND the
reference point are negated after the per-objective standardization (an
affine map per axis preserves the HV argmax).

GP per objective (ModelListGP of float64 SingleTaskGPs): the prompt-54
committed D-1025 4-tuple (kernel m52|m32|rbf, transform std|log1p, noise
inferred|fixed, prior none|gamma) and floor, trained by bogp `train_gp`
(Adam, 700 epochs, lr 0.01) — the donor methods_C/qnehvi.py model with the
FlexGP config axes added. Refit each round on the full accumulated lane set.

Constrained branch (plan 1.3, guardrail_mode = "constrain"): a shed GP on the
accumulated R1 column is appended as the LAST model output and passed as a
botorch constraint `shed <= violation_mwh` (feasible when the callable is
<= 0); the objective picks outputs 0..M-1. A constant shed column is a
degenerate GP -> feasibility = 1 -> the constraint is dropped and the fact is
recorded (`constraint: "degenerate_constant"`).

Lattice-free: there is no candidate set, no snapping; a proposal u is
returned at full float64 precision (exact 0 is allowed and means "site
absent", contract 5).
"""

from __future__ import annotations

import os
import sys
import time

import numpy as np

from common_E import pin_bogp

pin_bogp()

import torch  # noqa: E402
import gpytorch  # noqa: E402
from gpytorch.constraints import GreaterThan  # noqa: E402
from gpytorch.priors import GammaPrior  # noqa: E402

from bogp.gp_model import train_gp  # noqa: E402

DTYPE = torch.float64
FAST = os.environ.get("ERCOT_E_FAST", "") == "1"        # tests only: fewer restarts; recorded in the round


def _kernel(name, d, prior):
    ls_prior = GammaPrior(3.0, 6.0) if prior == "gamma" else None
    if name == "m52":
        base = gpytorch.kernels.MaternKernel(nu=2.5, ard_num_dims=d, lengthscale_prior=ls_prior)
    elif name == "m32":
        base = gpytorch.kernels.MaternKernel(nu=1.5, ard_num_dims=d, lengthscale_prior=ls_prior)
    elif name == "rbf":
        base = gpytorch.kernels.RBFKernel(ard_num_dims=d, lengthscale_prior=ls_prior)
    else:
        raise ValueError(name)
    return gpytorch.kernels.ScaleKernel(base)


class ObjGP:
    """One objective (or the shed constraint): transform, standardization, the
    float64 SingleTaskGP, predictions in raw units."""

    def __init__(self, tx, y, floor, cfg=("m52", "std", "inferred", "none"), negate=True, fitter=None, u_raw=None,
                 sx=None):
        """fitter = None / {"def": "house"} -> bogp.train_gp (Adam 700; the 55 build); {"def": "v2", "sigma_c": s} ->
        fit definition v2 (plan AMENDMENT 2026-11-24b): hyperparameters from prompt 54's FitV2 on the RAW u (u_raw),
        copied into this SingleTaskGP (lengthscale / sx because tx = (u - mx) / sx; mean constant negated)."""
        from botorch.models import SingleTaskGP
        kernel, transform, noise, prior = cfg
        self.cfg, self.transform, self.negate = tuple(cfg), transform, negate
        y = np.asarray(y, float)
        if transform == "log1p":
            assert (y >= 0).all(), "log1p transform needs y >= 0"
            self.y_med = float(np.median(y))
            floor_t = float(floor) / (1.0 + self.y_med)
            t = np.log1p(y)
        elif transform == "std":
            floor_t = float(floor)
            t = y
        else:
            raise ValueError(transform)
        self.my = float(t.mean())
        self.sy = float(np.std(t, ddof=0)) or 1.0
        self.floor_var = (floor_t / self.sy) ** 2
        self.constant = bool(np.std(t, ddof=0) == 0.0)
        ty = (t - self.my) / self.sy
        if negate:
            ty = -ty
        ty_t = torch.tensor(ty, dtype=DTYPE)
        if noise == "inferred":
            lik = gpytorch.likelihoods.GaussianLikelihood(noise_constraint=GreaterThan(self.floor_var))
        elif noise == "fixed":
            lik = gpytorch.likelihoods.GaussianLikelihood(noise_constraint=GreaterThan(1e-12))
            lik.noise = torch.tensor(self.floor_var, dtype=DTYPE)
            lik.raw_noise.requires_grad_(False)
        else:
            raise ValueError(noise)
        model = SingleTaskGP(tx, ty_t.unsqueeze(-1), likelihood=lik,
                             covar_module=_kernel(kernel, tx.shape[1], prior),
                             mean_module=gpytorch.means.ConstantMean(),
                             outcome_transform=None, input_transform=None).to(DTYPE)
        self.fit_def = (fitter or {}).get("def", "house")
        self.fit_info = {"fit_definition": self.fit_def}
        if self.fit_def == "v2":
            assert u_raw is not None and sx is not None and transform == "std", "v2 hook: needs u_raw, sx; std transform"
            fv = fit_v2(np.asarray(u_raw, float), y, cfg, float((fitter or {}).get("sigma_c", 0.0)))
            assert abs(fv.my - self.my) <= 1e-9 * max(1.0, abs(self.my)) and abs(fv.sy - self.sy) <= 1e-9 * self.sy
            with torch.no_grad():
                cm = model.covar_module
                cm.base_kernel.lengthscale = (fv.model.covar_module.base_kernel.lengthscale.detach().double()
                                              / torch.tensor(np.asarray(sx, float), dtype=DTYPE))
                cm.outputscale = fv.model.covar_module.outputscale.detach().double()
                lik.noise = torch.clamp(fv.lik.noise.detach().double(), min=self.floor_var * 1.0001 + 1e-12)
                c = fv.model.mean_module.constant.detach().double()
                model.mean_module.constant = -c if negate else c
            sig = float((fitter or {}).get("sigma_c", 0.0))
            self.fit_info.update({"converged": bool(fv.converged), "mode_gap_nats": float(fv.mode_gap_nats),
                                  "gap_second_nats": float(fv.gap_second_nats), "n_within_tol": int(fv.n_within_tol),
                                  "n_failed": int(fv.n_failed), "map_total": float(fv.map_total),
                                  "noise_sd_raw": float(np.sqrt(float(fv.lik.noise)) * fv.sy),
                                  "noise_over_sigma_c": (float(np.sqrt(float(fv.lik.noise)) * fv.sy) / sig) if sig > 0 else None})
        else:
            train_gp(model, model.likelihood, tx, model.train_targets)
        model.eval()
        self.model = model
        self._tx, self._ty = tx, ty_t

    def predict_raw(self, tx_q):
        """(mean, sd_total) in transformed-raw units t (= raw for std), noise included."""
        with torch.no_grad(), gpytorch.settings.fast_pred_var():
            post = self.model.likelihood(self.model(tx_q))
            mu = post.mean.numpy()
            sd = post.stddev.numpy()
        if self.negate:
            mu = -mu
        return mu * self.sy + self.my, sd * self.sy

    def loo_rms_z(self) -> float:
        with torch.no_grad():
            K = self.model.covar_module(self._tx).to_dense().double()
            Kn = K + self.model.likelihood.noise.double() * torch.eye(len(self._tx), dtype=torch.float64)
            Ki = torch.linalg.inv(Kn)
            alpha = Ki @ (self._ty.double() - self.model.mean_module.constant.double())
            z = (alpha / Ki.diagonal().sqrt()).numpy()
        return float(np.sqrt((z ** 2).mean()))

    def noise_raw(self) -> float:
        return float(np.sqrt(float(self.model.likelihood.noise.detach())) * self.sy)


BOUND_TOL = 1e-12


def snap_bounds(u):
    """In place: u < 1e-12 -> 0.0, u > 1 - 1e-12 -> 1.0. Bound cleanup after the standardized-space round trip
    (x * sx + mx leaves 5.55e-17 at a lower-bound optimum); NOT lattice snapping. Returns the counts."""
    lo = (u > 0.0) & (u < BOUND_TOL)
    hi = (u < 1.0) & (u > 1.0 - BOUND_TOL)
    u[u < BOUND_TOL] = 0.0
    u[u > 1.0 - BOUND_TOL] = 1.0
    return {"to_0": int(lo.sum()), "to_1": int(hi.sum()), "tol": BOUND_TOL,
            "note": "bound cleanup after x * sx + mx; not lattice snapping"}


def standardize_x(U):
    U = np.asarray(U, float)
    mx = U.mean(0)
    sx = np.where(U.std(0) <= 0, 1.0, U.std(0))
    return mx, sx


def fit_v2(U, y, cfg, sigma_c):
    """prompt 54's FitV2 (analysis/ercot_gp/ercot_gp_partb.py) on raw u; imported lazily (the house path never needs it)."""
    root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
    if root not in sys.path:
        sys.path.insert(0, root)
    from analysis.ercot_gp.ercot_gp_partb import FitV2
    return FitV2(np.asarray(U, float), np.asarray(y, float), 1e-9, tuple(cfg), sigma_c=float(sigma_c), measured=False)


def fit_models(U, Y, cfgs, floors, shed=None, shed_limit=None, fitters=None):
    """Fit the M objective GPs (+ the shed constraint GP when `shed` is given).
    Returns dict(models=ModelListGP, objs=[ObjGP], shed=ObjGP|None, mx, sx,
    constraint=...)."""
    from botorch.models import ModelListGP
    U = np.asarray(U, float); Y = np.asarray(Y, float)
    assert U.ndim == 2 and Y.ndim == 2 and len(U) == len(Y)
    assert np.isfinite(U).all() and np.isfinite(Y).all()
    mx, sx = standardize_x(U)
    tx = torch.tensor((U - mx) / sx, dtype=DTYPE)
    fitters = list(fitters) if fitters is not None else [None] * Y.shape[1]
    objs = [ObjGP(tx, Y[:, j], floors[j], cfgs[j], negate=True, fitter=fitters[j], u_raw=U, sx=sx)
            for j in range(Y.shape[1])]
    models = [o.model for o in objs]
    shed_gp, constraint = None, "none"
    if shed is not None:
        shed = np.asarray(shed, float)
        assert shed.shape == (len(U),)
        if np.std(shed, ddof=0) == 0.0:
            constraint = "degenerate_constant"          # plan 1.3: feasibility = 1, constraint dropped
        else:
            shed_gp = ObjGP(tx, shed, 1e-9, ("m52", "std", "inferred", "none"), negate=False)
            models.append(shed_gp.model)
            constraint = f"shed <= {shed_limit} MWh (GP on the accumulated R1 column)"
    return {"models": ModelListGP(*models), "objs": objs, "shed": shed_gp, "mx": mx, "sx": sx,
            "constraint": constraint, "shed_limit": shed_limit}


def propose(U, Y, ref_point, cfgs, floors, seed, q=8, qcfg=None, shed=None, shed_limit=None,
            guardrail_mode="monitor", log=print, fitters=None):
    """One acquisition round. U (n, d) in [0, 1], Y (n, M) raw (minimize), ref_point
    (M,) raw. Returns dict(u_batch (q, d), acq_values, pred_mean (q, M),
    pred_sd (q, M), seconds, fit=..., settings=...)."""
    from botorch.acquisition.multi_objective import qNoisyExpectedHypervolumeImprovement
    from botorch.acquisition.multi_objective.objective import IdentityMCMultiOutputObjective
    from botorch.optim import optimize_acqf
    from botorch.sampling import SobolQMCNormalSampler
    qcfg = dict(qcfg or {})
    mc = int(qcfg.get("mc_samples", 128))
    num_restarts = int(qcfg.get("num_restarts", 20))
    raw_samples = int(qcfg.get("raw_samples", 512))
    if FAST:
        num_restarts, raw_samples = 2, 64
    alpha = float(qcfg.get("alpha", 0.0))
    t0 = time.time()
    torch.manual_seed(int(seed))                         # once per process, before sampler + optimisation
    U = np.asarray(U, float); Y = np.asarray(Y, float)
    n, d = U.shape
    M = Y.shape[1]
    use_constraint = guardrail_mode == "constrain" and shed is not None
    fit = fit_models(U, Y, cfgs, floors, shed=shed if use_constraint else None, shed_limit=shed_limit, fitters=fitters)
    objs = fit["objs"]
    ref_std = np.array([-(float(ref_point[j]) - objs[j].my) / objs[j].sy if objs[j].transform == "std"
                        else -(np.log1p(float(ref_point[j])) - objs[j].my) / objs[j].sy for j in range(M)])
    tx = torch.tensor((U - fit["mx"]) / fit["sx"], dtype=DTYPE)
    kwargs = {}
    if fit["shed"] is not None:
        sg = fit["shed"]
        thr_std = (float(shed_limit) - sg.my) / sg.sy
        kwargs["objective"] = IdentityMCMultiOutputObjective(outcomes=list(range(M)))
        kwargs["constraints"] = [lambda Z, _t=thr_std: Z[..., M] - _t]       # feasible when <= 0
    acq = qNoisyExpectedHypervolumeImprovement(
        model=fit["models"], ref_point=torch.tensor(ref_std, dtype=DTYPE), X_baseline=tx,
        sampler=SobolQMCNormalSampler(sample_shape=torch.Size([mc]), seed=int(seed)),
        prune_baseline=bool(qcfg.get("prune_baseline", True)), alpha=alpha,
        cache_root=bool(qcfg.get("cache_root", True)), **kwargs)
    log(f"qNEHVI: n={n} d={d} M={M} fit {time.time() - t0:.1f} s; constraint={fit['constraint']}; "
        f"restarts={num_restarts} raw={raw_samples}{' FAST' if FAST else ''}")
    lo = (np.zeros(d) - fit["mx"]) / fit["sx"]
    hi = (np.ones(d) - fit["mx"]) / fit["sx"]
    bounds = torch.tensor(np.vstack([lo, hi]), dtype=DTYPE)
    xb, vals = optimize_acqf(acq, bounds=bounds, q=q, num_restarts=num_restarts, raw_samples=raw_samples,
                             sequential=bool(qcfg.get("sequential", True)))
    xb = xb.detach()
    u_batch = xb.numpy() * fit["sx"] + fit["mx"]
    u_batch = np.clip(u_batch, 0.0, 1.0)                 # optimize_acqf stays in the box; clip = exact-bound hygiene
    snaps = snap_bounds(u_batch)                         # prompt 66 (E): 5.55e-17 -> exact 0 (contract 5: site absent)
    assert u_batch.shape == (q, d)
    xb = torch.tensor((u_batch - fit["mx"]) / fit["sx"], dtype=DTYPE)   # predictions at the design that is run
    pm = np.empty((q, M)); ps = np.empty((q, M))
    for j, o in enumerate(objs):
        pm[:, j], ps[:, j] = o.predict_raw(xb)
    return {"u_batch": u_batch, "acq_values": np.atleast_1d(vals.detach().numpy()).tolist(),
            "pred_mean": pm, "pred_sd": ps, "seconds": time.time() - t0, "fit": fit,
            "transforms": [o.transform for o in objs],
            "loo_rms_z": [round(o.loo_rms_z(), 4) for o in objs],
            "noise_raw": [o.noise_raw() for o in objs],
            "fit_info": [o.fit_info for o in objs],
            "settings": {"mc_samples": mc, "num_restarts": num_restarts, "raw_samples": raw_samples,
                         "alpha": alpha, "prune_baseline": bool(qcfg.get("prune_baseline", True)),
                         "sequential": bool(qcfg.get("sequential", True)), "fast_mode": FAST,
                         "constraint": fit["constraint"], "guardrail_mode": guardrail_mode,
                         "seed": int(seed), "dtype": "float64", "bound_snaps": snaps}}
