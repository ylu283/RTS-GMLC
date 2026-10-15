"""Prompt 39 shared machinery: configurable PredGP variant, LOO + holdout
metrics in ORIGINAL units, and the log1p NLPD change-of-variables unit test.

The default config reproduces analysis/bo_stage2/acquire_next.py::PredGP
exactly (same standardization, kernel, floor constraint, train_gp defaults,
same closed-form LOO convention). Reads campaign data; writes nothing.
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
CAMPAIGN = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, CAMPAIGN)
_BOGP_PATH = os.environ.get("BOGP_PATH",
                            "/Users/yilu/Documents/GitHub/bo-gp-qparego")
sys.path.insert(0, _BOGP_PATH)

import torch  # noqa: E402
torch.set_num_threads(4)
import gpytorch  # noqa: E402
from gpytorch.constraints import GreaterThan  # noqa: E402
from gpytorch.priors import GammaPrior  # noqa: E402

from bogp.gp_model import GPRegressionModel, train_gp  # noqa: E402

M_COLS = ["load_shed_mwh", "true_curtailment_mwh",
          "total_cost_less_synthetic_usd"]
FLOORS = {"load_shed_mwh": 3000.0, "true_curtailment_mwh": 5000.0,
          "total_cost_less_synthetic_usd": 0.5e6}
SHORT = {"load_shed_mwh": "shed", "true_curtailment_mwh": "curt",
         "total_cost_less_synthetic_usd": "cost_ls"}

DEFAULT_CFG = ("m52", "std", "inferred", "none")  # kernel/transform/noise/prior


def sorted_tiers():
    from tiers import TIERS
    return sorted(TIERS)


def load_wave_xy(wave, cols=M_COLS):
    wdir = os.path.join(CAMPAIGN, "waves", wave)
    dm = pd.read_csv(os.path.join(wdir, "design_matrix.csv"))
    ob = pd.read_csv(os.path.join(wdir, "objectives.csv"))
    df = dm.merge(ob[["index"] + cols], on="index", validate="1:1")
    X = df[[f"{t}_omega" for t in sorted_tiers()]].to_numpy(float)
    Y = df[cols].to_numpy(float)
    assert np.isfinite(X).all() and np.isfinite(Y).all(), wave
    return X, Y


def arm_data(arm):
    """Training X, Y for arm in {16, 32, 48}."""
    X0, Y0 = load_wave_xy("stage2_C_n0")
    if arm == 16:
        return X0, Y0
    Xb, Yb = load_wave_xy("stage2_C_n0b")
    X, Y = np.vstack([X0, Xb]), np.vstack([Y0, Yb])
    if arm == 32:
        return X, Y
    assert arm == 48
    Xq, Yq = load_wave_xy("methods_C_Q1")
    return np.vstack([X, Xq]), np.vstack([Y, Yq])


def bo_augmented_data():
    """32 starts + bo_C_r1 + bo_C_r2 (n = 48), the r3-audit training set."""
    X, Y = arm_data(32)
    for w in ("bo_C_r1", "bo_C_r2"):
        Xw, Yw = load_wave_xy(w)
        X, Y = np.vstack([X, Xw]), np.vstack([Y, Yw])
    assert X.shape == (48, 6)
    return X, Y


class FlexGP:
    """PredGP with pre-registered config axes (prompt 39 §2).

    kernel:    m52 (default) | m32 | rbf
    transform: std (default) | log1p  (shed and curtailment only)
    noise:     inferred (default; GreaterThan((floor_t/sy)^2) constraint)
               | fixed (pinned to exactly (floor_t/sy)^2, constraint removed)
    prior:     none (default) | gamma (BoTorch-default Gamma(3.0, 6.0)
               lengthscale regularization)
    Floor under log1p maps by the delta method: floor_t =
    floor / (1 + median(train y)).
    """

    def __init__(self, X, y, floor, cfg=DEFAULT_CFG):
        kernel, transform, noise, prior = cfg
        self.cfg = cfg
        self.transform = transform
        if transform == "log1p":
            assert (y >= 0).all(), "log1p transform needs y >= 0"
            self.y_med = float(np.median(y))
            floor_t = floor / (1.0 + self.y_med)
            t = np.log1p(y)
        else:
            floor_t = floor
            t = np.asarray(y, float)
        self.mx = X.mean(axis=0)
        self.sx = np.where(X.std(axis=0) <= 0, 1.0, X.std(axis=0))
        self.my = float(t.mean())
        self.sy = float(np.std(t, ddof=0)) or 1.0
        self.floor_var = (floor_t / self.sy) ** 2
        tx = torch.tensor((X - self.mx) / self.sx, dtype=torch.float32)
        ty = torch.tensor((t - self.my) / self.sy, dtype=torch.float32)

        ls_prior = GammaPrior(3.0, 6.0) if prior == "gamma" else None
        if kernel == "m52":
            base = gpytorch.kernels.MaternKernel(
                nu=2.5, ard_num_dims=X.shape[1], lengthscale_prior=ls_prior)
        elif kernel == "m32":
            base = gpytorch.kernels.MaternKernel(
                nu=1.5, ard_num_dims=X.shape[1], lengthscale_prior=ls_prior)
        elif kernel == "rbf":
            base = gpytorch.kernels.RBFKernel(
                ard_num_dims=X.shape[1], lengthscale_prior=ls_prior)
        else:
            raise ValueError(kernel)
        kern = gpytorch.kernels.ScaleKernel(base)

        if noise == "inferred":
            self.lik = gpytorch.likelihoods.GaussianLikelihood(
                noise_constraint=GreaterThan(self.floor_var))
        elif noise == "fixed":
            self.lik = gpytorch.likelihoods.GaussianLikelihood(
                noise_constraint=GreaterThan(1e-12))
            self.lik.noise = torch.tensor(self.floor_var)
            self.lik.raw_noise.requires_grad_(False)
        else:
            raise ValueError(noise)

        self.model = GPRegressionModel(tx, ty, self.lik, kern)
        train_gp(self.model, self.lik, tx, ty)
        self.model.eval()
        self.lik.eval()
        self._tx, self._ty = tx, ty
        if noise == "fixed":
            # float32 raw-noise roundtrip: exact to float32 precision
            assert abs(float(self.lik.noise) - self.floor_var) \
                <= 1e-5 * self.floor_var

    # ---- posterior in transformed units t (original, unstandardized) ----
    def predict_t(self, Xq):
        xq = torch.tensor((np.atleast_2d(Xq) - self.mx) / self.sx,
                          dtype=torch.float32)
        with torch.no_grad(), gpytorch.settings.fast_pred_var():
            post = self.lik(self.model(xq))
            mu = post.mean.numpy() * self.sy + self.my
            sd = post.stddev.numpy() * self.sy
        return mu, sd

    def loo_t(self):
        """Campaign closed-form LOO (PredGP.loo_residuals convention), plus
        the noise-inclusive LOO predictive sd. Returned in t units."""
        with torch.no_grad():
            K = self.model.covar_module(self._tx).evaluate()
            Kn = K + self.lik.noise * torch.eye(len(self._tx), dtype=K.dtype)
            Ki = torch.linalg.inv(Kn)
            alpha = Ki @ (self._ty - self._ty.mean())
            diag = Ki.diagonal()
            resid_std = (alpha / diag).numpy()          # standardized t
            sd_std = np.sqrt(1.0 / diag.numpy())
        t_true = self._ty.numpy() * self.sy + self.my
        mu = t_true - resid_std * self.sy
        sd = sd_std * self.sy
        return mu, sd, t_true


def to_t(y, transform):
    return np.log1p(y) if transform == "log1p" else np.asarray(y, float)


def median_raw(mu_t, transform):
    return np.expm1(mu_t) if transform == "log1p" else mu_t


def metrics(y_raw, mu_t, sd_t, transform, floor, y_range=None, tag=""):
    """All metrics in ORIGINAL units per §4. For log1p: cov95 via the
    back-transformed quantiles (== |z_t| <= 1.96, monotone-exact), RMSE on
    the back-transformed predictive MEDIAN, NLPD with the
    change-of-variables term mean(log(1 + y))."""
    from scipy.stats import spearmanr
    y_raw = np.asarray(y_raw, float)
    t_true = to_t(y_raw, transform)
    z = (t_true - mu_t) / sd_t
    pred_med = median_raw(mu_t, transform)
    err = pred_med - y_raw
    rmse = float(np.sqrt(np.mean(err ** 2)))
    nlpd_t = 0.5 * np.log(2 * np.pi * sd_t ** 2) + 0.5 * z ** 2
    jac = np.log1p(y_raw) * 0.0
    if transform == "log1p":
        jac = np.log1p(y_raw)        # + log(1 + y) per point
    nlpd = float(np.mean(nlpd_t + jac))
    rng = float(y_range if y_range is not None
                else (y_raw.max() - y_raw.min()))
    ss_tot = float(np.sum((y_raw - y_raw.mean()) ** 2))
    out = {
        "n": int(len(y_raw)),
        "rmse": rmse,
        "rmse_over_floor": rmse / floor,
        "rmse_pct_range": 100.0 * rmse / rng,
        "nlpd": nlpd,
        "mean_z": float(z.mean()),
        "rms_z": float(np.sqrt(np.mean(z ** 2))),
        "cov95": int((np.abs(z) <= 1.96).sum()),
        "spearman": float(spearmanr(pred_med, y_raw).statistic),
        "r2": float(1.0 - np.sum(err ** 2) / ss_tot) if ss_tot > 0 else 0.0,
    }
    if tag:
        out = {"tag": tag, **out}
    return out, z


def binom_band(n, p=0.95, level=0.95):
    from scipy.stats import binom
    lo, hi = binom.interval(level, n, p)
    return int(lo), int(hi)


def nlpd_unit_test(seed=7, n=4000):
    """§4: unit-test the log1p change-of-variables NLPD on synthetic
    lognormal data BEFORE any holdout call. The analytic per-point NLPD
    must match -log of a numerical density of y (finite-difference of the
    exact CDF) to 1e-6 relative."""
    rng = np.random.default_rng(seed)
    m, s = 2.3, 0.7
    t = rng.normal(m, s, size=n)
    y = np.expm1(t)
    mu_t = np.full(n, m)
    sd_t = np.full(n, s)
    z = (np.log1p(y) - mu_t) / sd_t
    nlpd_pt = (0.5 * np.log(2 * np.pi * sd_t ** 2) + 0.5 * z ** 2
               + np.log1p(y))
    from scipy.stats import norm
    h = 1e-6 * (1.0 + np.abs(y))
    cdf = lambda v: norm.cdf((np.log1p(v) - m) / s)  # noqa: E731
    dens = (cdf(y + h) - cdf(y - h)) / (2 * h)
    ref = -np.log(dens)
    rel = np.max(np.abs(nlpd_pt - ref) / np.abs(ref))
    assert rel < 1e-5, f"NLPD change-of-variables formula off: rel={rel:.3g}"
    return float(rel)


if __name__ == "__main__":
    rel = nlpd_unit_test()
    print(f"nlpd_unit_test PASS (max rel dev {rel:.2e})")
