"""Prompt 43 Phase-B shared machinery (v3 FINAL spec, 2026-10-25).

Heteroscedastic shed GP with MEASURED per-point noise (fixed, never
learned). Float64 end-to-end. New code only: no frozen file is touched,
no frozen fit path (FlexGP.loo_t / predict_t) is reused.

Pinned elements implemented here (spec section in parentheses):
- noise forms (ii) piecewise-linear and (iii) per-stratum, plus the
  homoscedastic 285.3 reference; one unit chain
  v_i = (sigma(y_i) / (J_i * sy))**2 + 1e-12 (S3);
- FixedNoiseGaussianLikelihood(learn_additional_noise=False) built
  inside min_fixed_noise overridden to 1e-14 for double, with a hard
  torch.equal assert against the intended vector (S4);
- direct common.train_gp calls (n_epochs 5000/10000, lr 0.01, seed 0
  per fit), dloss100 rule, jitter-retry failure policy (S4);
- closed-form LOO with the LEARNED constant mean, Cholesky-only (S4);
- the frozen-hyperparameter LOO unit test, NO Adam refits (S4);
- the explicit latent+total prediction path (S5).
"""
from __future__ import annotations

import contextlib
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..",
                                                "initial_design")))

import common  # noqa: E402  (sets torch threads = 4; BOGP_PATH default)
import torch  # noqa: E402
import gpytorch  # noqa: E402

torch.set_default_dtype(torch.float64)  # S4: float64 end-to-end

COL = "load_shed_mwh"
J_OBJ = common.M_COLS.index(COL)
POOLED_SD = 285.3          # reference scalar; also metrics() floor arg
LR = 0.01
EPOCHS = 5000
EPOCHS_EXT = 10000
TOL = 2e-3
JITTER_STD = 1e-12         # standardized VARIANCE, added to every point

# ---------------------------------------------------------------- anchors (S3)
# Pinned Population-1 per-design sd estimates (REPLICATE_RESULT S3).
ANCHOR_Y = (429.5, 4672.0, 37834.0)
ANCHOR_SD = (0.0, 13.34, 520.1)
ANCHOR_DF = (2, 3, 3)
ANCHOR_CI = ((0.0, 0.0), (7.56, 49.7), (294.6, 1939.0))

SLOPE1 = (ANCHOR_SD[1] - ANCHOR_SD[0]) / (ANCHOR_Y[1] - ANCHOR_Y[0])
SLOPE2 = (ANCHOR_SD[2] - ANCHOR_SD[1]) / (ANCHOR_Y[2] - ANCHOR_Y[1])
SLOPE1_PINNED = 0.0031444
SLOPE2_PINNED = 0.0152813
# Pinned check: recomputed slopes must agree with the pinned printed
# values. The spec's 1e-6 RELATIVE tolerance is unreachable against its
# own 7-decimal printed constants (actual rel diffs 8.8e-6 / 3.0e-6 are
# pure printing error), so the assert is half-ulp of the printed
# precision plus an exact round-trip (deviation D1, PHASE_B.md).
assert abs(SLOPE1 - SLOPE1_PINNED) <= 5e-8 and \
    round(SLOPE1, 7) == SLOPE1_PINNED, SLOPE1
assert abs(SLOPE2 - SLOPE2_PINNED) <= 5e-8 and \
    round(SLOPE2, 7) == SLOPE2_PINNED, SLOPE2

STRATA_BOUNDS = (2000.0, 15000.0)  # form (iii), pinned pre-results


def sigma_ii(y, s_high=ANCHOR_SD[2]):
    """Form (ii): piecewise-linear through the anchors; sigma = 0 below
    the LOW anchor; the last slope continues above the HIGH anchor.
    s_high only moves the MID->HIGH slope (CI-endpoint sensitivity)."""
    y = np.asarray(y, float)
    slope2 = (s_high - ANCHOR_SD[1]) / (ANCHOR_Y[2] - ANCHOR_Y[1])
    return np.where(
        y <= ANCHOR_Y[0], 0.0,
        np.where(y <= ANCHOR_Y[1], (y - ANCHOR_Y[0]) * SLOPE1,
                 ANCHOR_SD[1] + (y - ANCHOR_Y[1]) * slope2))


def sigma_iii(y, s_high=ANCHOR_SD[2]):
    """Form (iii): per-stratum constants, boundaries 2,000 / 15,000."""
    y = np.asarray(y, float)
    return np.where(y < STRATA_BOUNDS[0], 0.0,
                    np.where(y < STRATA_BOUNDS[1], ANCHOR_SD[1], s_high))


def sigma_ref(y, s_high=None):
    """Reference arms: homoscedastic pooled scalar 285.3 (rejected
    framing; reference only, not eligible to win)."""
    return np.full_like(np.asarray(y, float), POOLED_SD)


NOISE_FORMS = {"ii": sigma_ii, "iii": sigma_iii, "ref": sigma_ref}


def stratum(y):
    y = np.asarray(y, float)
    return np.where(y < STRATA_BOUNDS[0], "LOW",
                    np.where(y < STRATA_BOUNDS[1], "MID", "HIGH"))


# ------------------------------------------------------------------- grid (S6)
class Arm:
    def __init__(self, idx, kernel, transform, form, reference):
        self.idx = idx
        self.kernel = kernel
        self.transform = transform
        self.form = form
        self.reference = reference
        self.name = f"{kernel}+{transform}+{form}"


def build_arms():
    """8 competing + 4 reference arms, deterministic order (S6)."""
    arms, i = [], 0
    for kernel in ("m52", "rbf"):
        for transform in ("log1p", "std"):
            for form in ("ii", "iii"):
                arms.append(Arm(i, kernel, transform, form, False))
                i += 1
    for kernel in ("m52", "rbf"):
        for transform in ("log1p", "std"):
            arms.append(Arm(i, kernel, transform, "ref", True))
            i += 1
    assert len(arms) == 12
    return arms


ARMS = build_arms()


# ------------------------------------------------------------------ model (S4)
class PhaseBExactGP(gpytorch.models.ExactGP):
    """Plain ExactGP + the campaign kernel configs (ConstantMean +
    ScaleKernel(Matern52|RBF, ARD)). New class; nothing frozen reused."""

    def __init__(self, train_x, train_y, likelihood, kernel):
        super().__init__(train_x, train_y, likelihood)
        self.mean_module = gpytorch.means.ConstantMean()
        self.covar_module = kernel

    def forward(self, x):
        return gpytorch.distributions.MultivariateNormal(
            self.mean_module(x), self.covar_module(x))


def build_kernel(kernel, d=6):
    if kernel == "m52":
        base = gpytorch.kernels.MaternKernel(nu=2.5, ard_num_dims=d)
    elif kernel == "rbf":
        base = gpytorch.kernels.RBFKernel(ard_num_dims=d)
    else:
        raise ValueError(kernel)
    return gpytorch.kernels.ScaleKernel(base)


def _fast_off():
    """Cholesky-only: no fast_pred_var anywhere in Phase-B (S4)."""
    return gpytorch.settings.fast_computations(
        covar_root_decomposition=False, log_prob=False, solves=False)


def _min_var():
    """Override gpytorch's posterior-variance clamp (double default
    1e-10) to 1e-14 so near-zero-noise predictions are not silently
    floored — same rationale as the pinned min_fixed_noise override."""
    return gpytorch.settings.min_variance(double_value=1e-14)


class PhaseBGP:
    """Heteroscedastic fixed-noise GP on shed. Builds only; call
    fit_phaseb() to train under the pinned convergence policy."""

    def __init__(self, X, y, kernel, transform, form, s_high=ANCHOR_SD[2]):
        X = np.asarray(X, float)
        y = np.asarray(y, float)
        self.kernel, self.transform, self.form = kernel, transform, form
        if transform == "log1p":
            assert (y >= 0).all(), "log1p transform needs y >= 0"
            t = np.log1p(y)
        elif transform == "std":
            t = y.copy()
        else:
            raise ValueError(transform)
        self.mx = X.mean(axis=0)
        self.sx = np.where(X.std(axis=0) <= 0, 1.0, X.std(axis=0))
        self.my = float(t.mean())
        self.sy = float(np.std(t, ddof=0)) or 1.0
        self.tx = torch.tensor((X - self.mx) / self.sx, dtype=torch.float64)
        self.ty = torch.tensor((t - self.my) / self.sy, dtype=torch.float64)

        # S3 unit chain: v_i = (sigma(y_i) / (J_i * sy))**2 + 1e-12
        self.sigma_fn = NOISE_FORMS[form]
        self.s_high = s_high
        sig = self.sigma_fn(y, s_high)
        jac = (1.0 + y) if transform == "log1p" else np.ones_like(y)
        v_np = (sig / (jac * self.sy)) ** 2 + JITTER_STD
        v = torch.tensor(v_np, dtype=torch.float64)
        with gpytorch.settings.min_fixed_noise(double_value=1e-14):
            self.lik = gpytorch.likelihoods.FixedNoiseGaussianLikelihood(
                noise=v, learn_additional_noise=False)
        # hard failure on any clamp (S4)
        assert torch.equal(self.lik.noise, v), \
            "min_fixed_noise clamped the noise vector — hard failure"
        # structural: no trainable noise hyperparameters
        assert sum(p.numel() for p in self.lik.parameters()
                   if p.requires_grad) == 0
        self.model = PhaseBExactGP(self.tx, self.ty, self.lik,
                                   build_kernel(kernel, X.shape[1]))
        # raw-MWh equivalent of the standardized jitter at the largest
        # training point (printed per arm, S3)
        jmax = (1.0 + y.max()) if transform == "log1p" else 1.0
        self.jitter_raw_mwh = math.sqrt(JITTER_STD) * self.sy * jmax


def fit_phaseb(X, y, arm, context, n0, conv_log, s_high=ANCHOR_SD[2]):
    """Pinned fit policy (S4): seed 0 immediately before every fit;
    5,000 Adam steps via common.train_gp DIRECTLY; dloss100 =
    losses[-101] - losses[-1]; if > 2e-3, refit from scratch at 10,000
    (same seed). Fit failure: one retry under cholesky_jitter(1e-4);
    double failure -> FAILED. Returns (gp_or_None, converged, info)."""
    err = None
    for attempt, jit in ((0, None), (1, 1e-4)):
        try:
            d5000, extended = None, False
            for epochs in (EPOCHS, EPOCHS_EXT):
                torch.manual_seed(0)
                gp = PhaseBGP(X, y, arm.kernel, arm.transform, arm.form,
                              s_high)
                cm = (gpytorch.settings.cholesky_jitter(
                          float_value=jit, double_value=jit)
                      if jit is not None else contextlib.nullcontext())
                with cm:
                    losses = common.train_gp(gp.model, gp.lik, gp.tx,
                                             gp.ty, n_epochs=epochs, lr=LR)
                assert len(losses) == epochs
                d = losses[-101] - losses[-1]
                if epochs == EPOCHS:
                    d5000 = d
                    if d <= TOL:
                        break
                    extended = True
            converged = bool(d <= TOL)
            gp.model.eval()
            gp.lik.eval()
            conv_log.append({
                "context": context, "config": arm.name,
                "noise_form": arm.form, "n0": n0,
                "epochs": EPOCHS_EXT if extended else EPOCHS, "lr": LR,
                "dloss100_at_5000": d5000, "dloss100_final": d,
                "extended_to_10000": extended, "converged": converged,
                "jitter_retry": attempt == 1,
                "final_loss": losses[-1],
                "jitter_raw_equiv_mwh": gp.jitter_raw_mwh,
                "fit_error": ""})
            return gp, converged, {"extended": extended, "d5000": d5000,
                                   "dfinal": d, "jitter_retry": attempt == 1}
        except Exception as exc:  # noqa: BLE001  record, never crash
            err = repr(exc)
    conv_log.append({
        "context": context, "config": arm.name, "noise_form": arm.form,
        "n0": n0, "epochs": None, "lr": LR, "dloss100_at_5000": None,
        "dloss100_final": None, "extended_to_10000": None,
        "converged": False, "jitter_retry": True, "final_loss": None,
        "jitter_raw_equiv_mwh": None, "fit_error": err})
    return None, False, {"fit_error": err}


# -------------------------------------------------------------------- LOO (S4)
def loo_closed_form(gp):
    """Closed-form LOO, reimplemented. Kn = K + diag(lik.noise) (vector
    AS STORED, post-assert); alpha = Kn^-1 (ty - m_hat) with m_hat the
    LEARNED constant mean; Cholesky solves only. LOO sd =
    1/sqrt([Kn^-1]_ii) (noise-inclusive). LOO mu_i (standardized) =
    ty_i - alpha_i/[Kn^-1]_ii. Returned de-standardized in t units."""
    with torch.no_grad():
        K = gp.model.covar_module(gp.tx).to_dense()
        Kn = K + torch.diag(gp.lik.noise)
        L = torch.linalg.cholesky(Kn)
        n = Kn.shape[0]
        Kinv = torch.cholesky_solve(torch.eye(n, dtype=torch.float64), L)
        m_hat = gp.model.mean_module.constant.detach().reshape(())
        alpha = torch.cholesky_solve(
            (gp.ty - m_hat).unsqueeze(-1), L).squeeze(-1)
        diag = Kinv.diagonal()
        mu_std = gp.ty - alpha / diag
        sd_std = torch.sqrt(1.0 / diag)
    mu_t = mu_std.numpy() * gp.sy + gp.my
    sd_t = sd_std.numpy() * gp.sy
    return mu_t, sd_t


UNIT_TEST_IDX = (0, 7, 15, 23, 31)


def loo_unit_test(gp, mu_t, sd_t):
    """Pinned unit test (S4): for the pinned indices, re-condition the
    SAME frozen hyperparameters on the other 31 points (rebuild the
    ExactGP state; NO retraining, NO Adam refits) and assert, in t
    units, |d mu_t| <= 1e-6*sy and |d sd_t|/sd_t <= 1e-6 vs the closed
    form. Returns the max deviations actually seen."""
    n = len(gp.ty)
    state_mean = gp.model.mean_module.state_dict()
    state_cov = gp.model.covar_module.state_dict()
    worst_mu, worst_sd = 0.0, 0.0
    for i in UNIT_TEST_IDX:
        keep = [j for j in range(n) if j != i]
        tx2, ty2 = gp.tx[keep], gp.ty[keep]
        v2 = gp.lik.noise[keep].clone()
        with gpytorch.settings.min_fixed_noise(double_value=1e-14):
            lik2 = gpytorch.likelihoods.FixedNoiseGaussianLikelihood(
                noise=v2, learn_additional_noise=False)
        assert torch.equal(lik2.noise, v2)
        m2 = PhaseBExactGP(tx2, ty2, lik2,
                           build_kernel(gp.kernel, gp.tx.shape[1]))
        m2.mean_module.load_state_dict(state_mean)
        m2.covar_module.load_state_dict(state_cov)
        m2.eval()
        lik2.eval()
        with torch.no_grad(), _fast_off(), _min_var():
            post = m2(gp.tx[i:i + 1])
            mu2_std = float(post.mean[0])
            var2 = float(post.variance[0]) + float(gp.lik.noise[i])
        mu2_t = mu2_std * gp.sy + gp.my
        sd2_t = math.sqrt(var2) * gp.sy
        dmu = abs(mu2_t - mu_t[i])
        dsd = abs(sd2_t - sd_t[i]) / sd_t[i]
        assert dmu <= 1e-6 * gp.sy, (i, dmu, 1e-6 * gp.sy)
        assert dsd <= 1e-6, (i, dsd)
        worst_mu = max(worst_mu, dmu / gp.sy)
        worst_sd = max(worst_sd, dsd)
    return worst_mu, worst_sd


# ------------------------------------------------------------- prediction (S5)
def predict_phaseb(gp, Xq, s_high=None):
    """Pinned prediction path (S5); FlexGP.predict_t is NOT reused.
    (1) latent mu/sd from gp.model(xq) (no likelihood), de-standardized;
    (2) predicted raw median; (3) test noise v_q from the S3 chain at
    that median (one pass); (4) total sd_t = sqrt(latent^2 + v_q*sy^2).
    Returns dict of arrays (t units + raw medians + noise pieces)."""
    if s_high is None:
        s_high = gp.s_high
    xq = torch.tensor((np.atleast_2d(Xq) - gp.mx) / gp.sx,
                      dtype=torch.float64)
    with torch.no_grad(), _fast_off(), _min_var():
        post = gp.model(xq)
        mu_std = post.mean.numpy()
        lat_sd_std = post.stddev.numpy()
    mu_t = mu_std * gp.sy + gp.my
    lat_sd_t = lat_sd_std * gp.sy
    if gp.transform == "log1p":
        med = np.expm1(mu_t)
        jac = 1.0 + med
    else:
        med = mu_t.copy()
        jac = np.ones_like(med)
    sig_q = gp.sigma_fn(med, s_high)
    # negative std-config median -> sigma = 0 by construction (noted)
    v_q = (sig_q / (jac * gp.sy)) ** 2 + JITTER_STD
    tot_sd_t = np.sqrt(lat_sd_t ** 2 + v_q * gp.sy ** 2)
    return {"mu_t": mu_t, "latent_sd_t": lat_sd_t, "total_sd_t": tot_sd_t,
            "median_raw": med, "sigma_at_median": sig_q, "v_q": v_q}


def band_raw(gp, mu_t, sd_t):
    """mu_t +/- 1.96 sd_t mapped back per transform."""
    lo_t, hi_t = mu_t - 1.96 * sd_t, mu_t + 1.96 * sd_t
    if gp.transform == "log1p":
        return np.expm1(lo_t), np.expm1(hi_t)
    return lo_t, hi_t


def nlpd_pointwise(y_raw, mu_t, sd_t, transform):
    """Per-point NLPD in ORIGINAL units — the common.metrics definition
    (log1p change-of-variables term +log(1+y) per point)."""
    y_raw = np.asarray(y_raw, float)
    t_true = common.to_t(y_raw, transform)
    z = (t_true - mu_t) / sd_t
    pt = 0.5 * np.log(2 * np.pi * sd_t ** 2) + 0.5 * z ** 2
    if transform == "log1p":
        pt = pt + np.log1p(y_raw)
    return pt
