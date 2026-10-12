"""Prompt 37 (v2) — problems with known truth.

6-D problems live on the 9^6 Stage-2 lattice; M = 3 in M_COLS order
{shed, curt, cost}, all minimized, physical units:

  E-path-1..5  GP posterior SAMPLE PATHS (RFF prior + pathwise update), fit on
               the 96 evaluated Stage-2 designs with a kernel different from
               PredGP: Matern-3/2 ARD on [0,1]-scaled inputs, Gamma(3, 6)
               lengthscale prior, Gamma(2, 0.15) outputscale prior, noise
               variance >= (floor/sd_y)^2. One path per objective per problem.
  E-mean       posterior mean of the same fit (smooth; secondary).
  E-short      one sample path with every lengthscale x 0.5 (harder).
  Z-needle     DTLZ2 + a small hidden basin at a box edge that improves one
               front corner (positive control for early stops).
  Z-plateau    DTLZ2 with the shed objective clipped at 0 on ~40 % of the
               lattice (Stage-2-like zero-shed plateau).
  Z-dis        DTLZ7-type disconnected front.

Z outputs: per objective, the [1 %, 99 %] lattice quantile range maps
affinely onto the observed Stage-2 range [min, max] of the 96 designs.

Noise (6-D): N(0, (m * rho_i * span_i)^2), rho_i = floor_i / span_i^S2
(span over the 96 observed Stage-2 values), span_i = range of the problem's
truth at the 96 Stage-2 design points, m in {0.5, 1, 2}. The noise draw is
keyed by (problem, noise level, replicate, lattice index): common random
numbers across methods within a replicate.

2-D replay grids (R-A/B/C, R-PG:<wave>): the 81-cell table is the truth and
is returned NOISE-FREE (label: noise-free). Objectives/floors = Stage-1
replay (replay.OBJECTIVES order, floors incl. the 60-start working floor).

Build: `python problems.py build [names...]` -> problems/<name>.npz +
problems/problems.json (truth sha256, front sizes, checks).
"""

from __future__ import annotations

import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from sr_common import (  # noqa: E402
    CAMPAIGN, D6, FLOORS, LAT, M_COLS, N_LATTICE, PredGP, hv, hv3d,
    lattice_candidates, nd_mask, problem_id, seed_int, x_to_index,
)

PROB_DIR = HERE / "problems"

# ---- 2-D replay ------------------------------------------------------------ #
REPLAY_OBJECTIVES = [
    "delta_cost_less_synthetic_usd_APPROX",
    "delta_curtailment_mwh",
    "delta_load_shed_mwh",
    "delta_thermal_starts",
]
REPLAY_FLOORS = np.array([0.5e6, 5_000.0, 3_000.0, 60.0])  # replay.floors(), same order
CONTOURS = {"R-A": "contour_303x317_A", "R-B": "contour_303x317_B", "R-C": "contour_303x317_C"}
PAIRGRID_WAVES = sorted(p.name for p in (CAMPAIGN / "waves").glob("pairgrid_*_C"))
STAGE2_WAVES = ["stage2_C_n0", "stage2_C_n0b", "bo_C_r1", "bo_C_r2", "random_C"]
TIER_COLS = [f"{t}_omega" for t in sorted(["nuclear", "wind_303", "wind_317",
                                            "wind_122", "pv", "tail"])]

E_PATHS = [f"E-path-{i}" for i in range(1, 6)]
PROBLEMS_6D = E_PATHS + ["E-mean", "E-short", "Z-needle", "Z-plateau", "Z-dis"]
NOISE_MULTS = (0.5, 1.0, 2.0)
RFF_FEATURES = 4096
NU_E = 1.5


def problem_names_2d() -> list[str]:
    return list(CONTOURS) + [f"R-PG:{w}" for w in PAIRGRID_WAVES]


def load_grid(name: str) -> dict:
    """81-cell table -> {X (81, 2) omega, Y (81, 4), inputs, floors}."""
    wave = CONTOURS[name] if name in CONTOURS else name.split(":", 1)[1]
    wdir = CAMPAIGN / "waves" / wave
    dm = pd.read_csv(wdir / "design_matrix.csv")
    ob = pd.read_csv(wdir / "objectives.csv")
    om = [c for c in dm.columns if c.endswith("_omega") and dm[c].nunique() > 1]
    assert len(om) == 2, (name, om)
    df = dm[["index", *om]].merge(ob[["index", *REPLAY_OBJECTIVES]], on="index",
                                  validate="1:1").sort_values("index")
    assert len(df) == 81 and df[REPLAY_OBJECTIVES].notna().all().all(), name
    return {"name": name, "wave": wave, "inputs": om,
            "X": df[om].to_numpy(float), "Y": df[REPLAY_OBJECTIVES].to_numpy(float),
            "floors": REPLAY_FLOORS.copy(), "m_cols": REPLAY_OBJECTIVES}


# ---- Stage-2 data ------------------------------------------------------------ #
def load_stage2(waves=STAGE2_WAVES) -> tuple[np.ndarray, np.ndarray, list[str]]:
    xs, ys, src = [], [], []
    for w in waves:
        wdir = CAMPAIGN / "waves" / w
        dm = pd.read_csv(wdir / "design_matrix.csv")
        ob = pd.read_csv(wdir / "objectives.csv")
        df = dm.merge(ob[["index"] + M_COLS], on="index", validate="1:1").sort_values("index")
        xs.append(df[TIER_COLS].to_numpy(float))
        ys.append(df[M_COLS].to_numpy(float))
        src += [f"{w}#{i}" for i in df["index"]]
    X, Y = np.vstack(xs), np.vstack(ys)
    assert np.isfinite(X).all() and np.isfinite(Y).all()
    assert len(set(x_to_index(X).tolist())) == len(X), "duplicate Stage-2 designs"
    return X, Y, src


def stage2_rho() -> np.ndarray:
    _, Y, _ = load_stage2()
    return FLOORS / (Y.max(axis=0) - Y.min(axis=0))


def unit(X: np.ndarray) -> np.ndarray:
    """Omega -> [0, 1] (level / 8 on the lattice)."""
    return (np.asarray(X, float) - LAT[0]) / (LAT[-1] - LAT[0])


# ---- E: Matern-3/2 fit + pathwise sample paths --------------------------------- #
def matern32(A: np.ndarray, B: np.ndarray, ls: np.ndarray, s2: float) -> np.ndarray:
    r = np.sqrt(np.maximum(((A[:, None, :] - B[None, :, :]) / ls) ** 2, 0).sum(-1))
    t = np.sqrt(3.0) * r
    return s2 * (1.0 + t) * np.exp(-t)


class EFit:
    """Per-objective Matern-3/2 GP on u = unit(X), y z-scored; MAP fit
    (Adam, float64, priors included in the mll). Hyperparameters only;
    conditioning/sampling is done in numpy below."""

    def __init__(self, U: np.ndarray, y: np.ndarray, floor: float, seed: int = 0,
                 iters: int = 600, lr: float = 0.05):
        import gpytorch
        import torch
        from gpytorch.constraints import GreaterThan
        from gpytorch.priors import GammaPrior

        torch.manual_seed(seed)
        self.my, self.sy = float(y.mean()), float(np.std(y)) or 1.0
        tx = torch.tensor(U, dtype=torch.float64)
        ty = torch.tensor((y - self.my) / self.sy, dtype=torch.float64)
        lik = gpytorch.likelihoods.GaussianLikelihood(
            noise_constraint=GreaterThan((floor / self.sy) ** 2)).double()
        kern = gpytorch.kernels.ScaleKernel(
            gpytorch.kernels.MaternKernel(nu=NU_E, ard_num_dims=U.shape[1],
                                          lengthscale_prior=GammaPrior(3.0, 6.0)),
            outputscale_prior=GammaPrior(2.0, 0.15)).double()

        class _M(gpytorch.models.ExactGP):
            def __init__(s):
                super().__init__(tx, ty, lik)
                s.mean_module = gpytorch.means.ConstantMean()
                s.covar_module = kern

            def forward(s, x):
                return gpytorch.distributions.MultivariateNormal(
                    s.mean_module(x), s.covar_module(x))

        model = _M().double()
        model.train(); lik.train()
        opt = torch.optim.Adam(model.parameters(), lr=lr)
        mll = gpytorch.mlls.ExactMarginalLogLikelihood(lik, model)
        for _ in range(iters):
            opt.zero_grad()
            loss = -mll(model(tx), ty)
            loss.backward()
            opt.step()
        self.ls = model.covar_module.base_kernel.lengthscale.detach().numpy().ravel().astype(float)
        self.s2 = float(model.covar_module.outputscale.item())
        self.noise = float(lik.noise.item())
        self.c = float(model.mean_module.constant.item())
        self.U = np.asarray(U, float)
        self.yz = (np.asarray(y, float) - self.my) / self.sy

    def _solve(self, ls_mult: float = 1.0):
        ls = self.ls * ls_mult
        K = matern32(self.U, self.U, ls, self.s2) + self.noise * np.eye(len(self.U))
        L = np.linalg.cholesky(K)
        return ls, L

    def mean(self, Uq: np.ndarray, chunk: int = 20_000) -> np.ndarray:
        ls, L = self._solve()
        alpha = np.linalg.solve(L.T, np.linalg.solve(L, self.yz - self.c))
        out = np.empty(len(Uq))
        for i in range(0, len(Uq), chunk):
            out[i:i + chunk] = self.c + matern32(Uq[i:i + chunk], self.U, ls, self.s2) @ alpha
        return out * self.sy + self.my

    def loo(self) -> tuple[np.ndarray, np.ndarray]:
        """Closed-form LOO residual y - mu_-i and predictive sd (physical)."""
        _, L = self._solve()
        Ki = np.linalg.inv(L @ L.T)
        a = Ki @ (self.yz - self.c)
        return a / np.diag(Ki) * self.sy, np.sqrt(1.0 / np.diag(Ki)) * self.sy

    def sample_path(self, Uq: np.ndarray, rng: np.random.Generator, ls_mult: float = 1.0,
                    n_feat: int = RFF_FEATURES, chunk: int = 20_000) -> np.ndarray:
        """One posterior sample path at Uq (physical units): RFF prior draw for
        Matern-nu (spectral density = multivariate t with 2nu dof, scale 1/ls)
        + pathwise (Matheron) update with the exact kernel."""
        ls, L = self._solve(ls_mult)
        d = self.U.shape[1]
        dof = 2.0 * NU_E
        omega = rng.standard_normal((n_feat, d)) * np.sqrt(dof / rng.chisquare(dof, n_feat))[:, None]
        omega = omega / ls
        b = rng.uniform(0.0, 2.0 * np.pi, n_feat)
        w = rng.standard_normal(n_feat)
        amp = np.sqrt(2.0 * self.s2 / n_feat)

        def prior(Ux):
            return amp * np.cos(Ux @ omega.T + b) @ w

        eps = rng.normal(0.0, np.sqrt(self.noise), len(self.U))
        v = np.linalg.solve(L.T, np.linalg.solve(L, self.yz - self.c - prior(self.U) - eps))
        out = np.empty(len(Uq))
        for i in range(0, len(Uq), chunk):
            Ui = Uq[i:i + chunk]
            out[i:i + chunk] = self.c + prior(Ui) + matern32(Ui, self.U, ls, self.s2) @ v
        # numpy/Accelerate emits spurious matmul RuntimeWarnings on finite
        # inputs on this Mac (see bo_replay); assert finiteness instead
        assert np.all(np.isfinite(out)), "non-finite sample path"
        return out * self.sy + self.my


def fit_e(X: np.ndarray, Y: np.ndarray) -> list[EFit]:
    U = unit(X)
    return [EFit(U, Y[:, j], float(FLOORS[j]), seed=j) for j in range(3)]


def build_e(name: str, fits: list[EFit]) -> np.ndarray:
    Ul = unit(lattice_candidates())
    pid = problem_id(name)
    cols = []
    for j, f in enumerate(fits):
        if name == "E-mean":
            cols.append(f.mean(Ul))
        else:
            rng = np.random.default_rng(seed_int(pid, 7, j))
            cols.append(f.sample_path(Ul, rng, ls_mult=0.5 if name == "E-short" else 1.0))
    return np.column_stack(cols)


def emulator_checks(fits: list[EFit]) -> dict:
    """LOO of the E-fit; holdout (fit on 32 starts + 48 random -> predict BO's
    16 picks), for the E-fit AND for PredGP (the live model) side by side."""
    X, Y, src = load_stage2()
    out = {"e_fit": {}, "holdout": {}}
    for j, col in enumerate(M_COLS):
        r, s = fits[j].loo()
        out["e_fit"][col] = {
            "lengthscales_unit": fits[j].ls.tolist(), "outputscale": fits[j].s2,
            "noise_sd_phys": float(np.sqrt(fits[j].noise) * fits[j].sy),
            "loo_rmse": float(np.sqrt(np.mean(r ** 2))),
            "loo_rmse_over_floor": float(np.sqrt(np.mean(r ** 2)) / FLOORS[j]),
            "loo_q2": float(1 - np.sum(r ** 2) / np.sum((Y[:, j] - Y[:, j].mean()) ** 2)),
            "loo_rms_z": float(np.sqrt(np.mean((r / s) ** 2))),
            "loo_cov95": float(np.mean(np.abs(r / s) <= 1.96)),
            "worst_design": src[int(np.abs(r).argmax())]}
    Xtr, Ytr, _ = load_stage2(["stage2_C_n0", "stage2_C_n0b", "random_C"])
    Xte, Yte, _ = load_stage2(["bo_C_r1", "bo_C_r2"])
    ho = fit_e(Xtr, Ytr)
    import torch
    torch.manual_seed(0)
    for j, col in enumerate(M_COLS):
        mu_e = ho[j].mean(unit(Xte))
        pg = PredGP(Xtr, Ytr[:, j], float(FLOORS[j]))
        mu_p, sd_p = pg.predict(Xte)
        out["holdout"][col] = {
            "e_fit_rmse": float(np.sqrt(np.mean((mu_e - Yte[:, j]) ** 2))),
            "predgp_rmse": float(np.sqrt(np.mean((mu_p - Yte[:, j]) ** 2))),
            "predgp_rms_z": float(np.sqrt(np.mean(((Yte[:, j] - mu_p) / sd_p) ** 2))),
            "floor": float(FLOORS[j]), "test_sd": float(np.std(Yte[:, j]))}
    return out


# ---- Z: synthetic ------------------------------------------------------------- #
def _unit_lattice() -> np.ndarray:
    return np.round(unit(lattice_candidates()) * 8) / 8


def dtlz2(u: np.ndarray, g: np.ndarray | None = None) -> np.ndarray:
    if g is None:
        g = np.sum((u[:, 2:] - 0.5) ** 2, axis=1)
    a, b = u[:, 0] * np.pi / 2, u[:, 1] * np.pi / 2
    return np.column_stack([(1 + g) * np.cos(a) * np.cos(b),
                            (1 + g) * np.cos(a) * np.sin(b),
                            (1 + g) * np.sin(a)])


NEEDLE = {"centre": (1.0, 0.5, 0.5, 0.5), "depth": 0.5, "width": 0.15, "u1_min": 0.75}


def z_needle_raw(u: np.ndarray) -> np.ndarray:
    """DTLZ2; for u1 >= 0.75 (the f3-heavy corner) g gets a Gaussian well of
    depth 0.5, width 0.15 centred at u_{3:6} = (1, .5, .5, .5) — a box edge
    two lattice steps from the base optimum u_{3:6} = 0.5. Inside the well
    1 + g < 1, so that corner of the front moves inward; the base front is
    unchanged elsewhere."""
    c = np.asarray(NEEDLE["centre"])
    g = np.sum((u[:, 2:] - 0.5) ** 2, axis=1)
    well = NEEDLE["depth"] * np.exp(-np.sum((u[:, 2:] - c) ** 2, axis=1)
                                    / (2 * NEEDLE["width"] ** 2))
    g = g - well * (u[:, 0] >= NEEDLE["u1_min"])
    return dtlz2(u, g)


def z_plateau_raw(u: np.ndarray) -> np.ndarray:
    """DTLZ2 with objective 0 (shed) clipped: max(0, f1 - t), t = the 40th
    lattice percentile of f1 -> ~40 % of the lattice ties at exactly 0."""
    f = dtlz2(u)
    t = np.percentile(f[:, 0], 40)
    f[:, 0] = np.maximum(0.0, f[:, 0] - t)
    return f


def z_dis_raw(u: np.ndarray) -> np.ndarray:
    """DTLZ7 (M = 3, n = 6): f1 = u1, f2 = u2, g = 1 + 9/4 sum u_{3:6},
    f3 = (1+g)(3 - sum_i f_i/(1+g) (1 + sin(3 pi f_i))); 4 disconnected
    front regions; g minimal at u_{3:6} = 0 (lattice level 0)."""
    g = 1 + 9.0 / 4.0 * np.sum(u[:, 2:], axis=1)
    f1, f2 = u[:, 0], u[:, 1]
    h = 3 - sum(fi / (1 + g) * (1 + np.sin(3 * np.pi * fi)) for fi in (f1, f2))
    return np.column_stack([f1, f2, (1 + g) * h])


Z_FUNCS = {"Z-needle": z_needle_raw, "Z-plateau": z_plateau_raw, "Z-dis": z_dis_raw}


def scale_to_stage2(raw: np.ndarray, lo: np.ndarray, hi: np.ndarray) -> tuple[np.ndarray, dict]:
    q1, q99 = np.percentile(raw, [1, 99], axis=0)
    a = (hi - lo) / (q99 - q1)
    return lo + (raw - q1) * a, {"q01": q1.tolist(), "q99": q99.tolist(), "slope": a.tolist()}


def build_z(name: str) -> tuple[np.ndarray, dict]:
    _, Y96, _ = load_stage2()
    raw = Z_FUNCS[name](_unit_lattice())
    truth, sc = scale_to_stage2(raw, Y96.min(axis=0), Y96.max(axis=0))
    meta = {"scaling": sc, "definition": Z_FUNCS[name].__doc__.strip()}
    if name == "Z-needle":
        u = _unit_lattice()
        # the base problem under the needle problem's own affine map
        base = Y96.min(axis=0) + (dtlz2(u) - np.asarray(sc["q01"])) * np.asarray(sc["slope"])
        bf = base[nd_mask(base)]
        c = np.asarray(NEEDLE["centre"])
        well = NEEDLE["depth"] * np.exp(-np.sum((u[:, 2:] - c) ** 2, axis=1)
                                        / (2 * NEEDLE["width"] ** 2)) * (u[:, 0] >= NEEDLE["u1_min"])
        # material part of the well only (>= 10 % of its depth)
        cand = np.flatnonzero(well >= 0.1 * NEEDLE["depth"])
        # basin = cells whose needle value is NOT weakly dominated by the base
        # front (they extend the front beyond what the base problem allows)
        dom = np.zeros(len(cand), bool)
        for i in range(0, len(cand), 1000):
            ti = truth[cand[i:i + 1000]]
            dom[i:i + 1000] = np.any(np.all(bf[None, :, :] <= ti[:, None, :], axis=2), axis=1)
        basin = cand[~dom]
        diff = well >= 0.1 * NEEDLE["depth"]
        meta["needle"] = {**NEEDLE, "n_cells_changed": int(diff.sum()),
                          "basin_idx": basin.tolist(), "n_basin": int(len(basin)),
                          "p_random_hit_64": float(1 - np.prod(
                              1 - len(basin) / (N_LATTICE - 32 - np.arange(64))))}
    return truth, meta


# ---- truth summaries ----------------------------------------------------------- #
def sha256_array(a: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(a, dtype=np.float64).tobytes()).hexdigest()


def stage2_density_check(truth: np.ndarray, noise_sd: np.ndarray, pid: int) -> dict:
    """Front density at the 48 Stage-2 designs (32 starts + 16 BO) under the
    problem's truth + one noise draw, vs the real 26/48."""
    X48, _, _ = load_stage2(["stage2_C_n0", "stage2_C_n0b", "bo_C_r1", "bo_C_r2"])
    idx = x_to_index(X48)
    rng = np.random.default_rng(seed_int(pid, 9))
    Y = truth[idx] + rng.normal(0, noise_sd, (48, 3))
    return {"nd_48_true": int(nd_mask(truth[idx]).sum()), "nd_48_noisy": int(nd_mask(Y).sum()),
            "stage2_real": 26}


def build_one(name: str, fits: list[EFit] | None) -> dict:
    t0 = time.time()
    if name.startswith("E-"):
        truth, meta = build_e(name, fits), {}
    else:
        truth, meta = build_z(name)
    X96, Y96, _ = load_stage2()
    i96 = x_to_index(X96)
    span = truth[i96].max(axis=0) - truth[i96].min(axis=0)
    rho = stage2_rho()
    sigma1 = rho * span
    m = nd_mask(truth)
    front = truth[m]
    nad, ide = front.max(axis=0), front.min(axis=0)
    ref_union = nad + 0.1 * (nad - ide)
    PROB_DIR.mkdir(exist_ok=True)
    np.savez_compressed(PROB_DIR / f"{name}.npz", truth=truth, front_idx=np.flatnonzero(m))
    rec = {"kind": "6d", "m_cols": M_COLS, "truth_sha256": sha256_array(truth),
           "n_front": int(m.sum()), "front_share": float(m.mean()),
           "front_ideal": ide.tolist(), "front_nadir": nad.tolist(),
           "ref_union": ref_union.tolist(), "hv_union": hv3d(front, ref_union),
           "span96": span.tolist(), "rho": rho.tolist(),
           "noise_sd": {str(k): (k * sigma1).tolist() for k in NOISE_MULTS},
           "truth_min": truth.min(axis=0).tolist(), "truth_max": truth.max(axis=0).tolist(),
           "rmse_vs_stage2_at_96": np.sqrt(((truth[i96] - Y96) ** 2).mean(axis=0)).tolist(),
           "density_check": stage2_density_check(truth, sigma1, problem_id(name)),
           "build_secs": round(time.time() - t0, 1), **meta}
    return rec


def build(names: list[str]) -> dict:
    path = PROB_DIR / "problems.json"
    index = json.loads(path.read_text()) if path.exists() else {}
    PROB_DIR.mkdir(exist_ok=True)
    for name in problem_names_2d():
        g = load_grid(name)
        m = nd_mask(g["Y"])
        nad, ide = g["Y"][m].max(axis=0), g["Y"][m].min(axis=0)
        index[name] = {"kind": "2d", "wave": g["wave"], "inputs": g["inputs"],
                       "m_cols": g["m_cols"], "floors": g["floors"].tolist(),
                       "noise": "none (table values; noise-free)",
                       "n_front": int(m.sum()), "truth_sha256": sha256_array(g["Y"]),
                       "ref_union": (nad + 0.1 * (nad - ide)).tolist()}
    fits = None
    if any(n.startswith("E-") for n in names):
        X, Y, _ = load_stage2()
        fits = fit_e(X, Y)
        index["_emulator"] = emulator_checks(fits)
        print(json.dumps(index["_emulator"], indent=1, default=float), flush=True)
    for name in names:
        index[name] = build_one(name, fits)
        r = index[name]
        print(f"{name}: front {r['n_front']} ({100 * r['front_share']:.2f} %), "
              f"density48 {r['density_check']}, {r['build_secs']} s", flush=True)
    path.write_text(json.dumps(index, indent=1, default=float) + "\n")
    return index


# ---- runtime access ------------------------------------------------------------ #
class Problem:
    """candidates() (n_cand, d), truth T (n_cand, M), noise sd, evaluate()."""

    def __init__(self, name: str, noise_mult: float = 1.0, verify_sha: bool = True):
        self.name = name
        self.pid = problem_id(name)
        meta = json.loads((PROB_DIR / "problems.json").read_text())[name]
        self.meta = meta
        self.noise_mult = float(noise_mult)
        self.ref_union = np.asarray(meta["ref_union"], float)
        if meta["kind"] == "2d":
            g = load_grid(name)
            self.X, self.T = g["X"], g["Y"]
            self.noise_sd = np.zeros(self.T.shape[1])
            self.floors = g["floors"]           # tau MC uses the replay floors
            self.d = 2
            self.front_idx = np.flatnonzero(nd_mask(self.T))
        else:
            z = np.load(PROB_DIR / f"{name}.npz")
            self.T = z["truth"]
            self.front_idx = z["front_idx"]
            if verify_sha:
                assert sha256_array(self.T) == meta["truth_sha256"], f"{name}: truth sha256 mismatch"
            self.X = None
            self.noise_sd = np.asarray(meta["noise_sd"][str(self.noise_mult)], float)
            self.floors = self.noise_sd             # the rule knows its noise level
            self.d = D6
        self.n_cand = len(self.T)
        self.M = self.T.shape[1]

    @property
    def noisy(self) -> bool:
        return bool(np.any(self.noise_sd > 0))

    def candidates(self) -> np.ndarray:
        if self.X is None:
            self.X = lattice_candidates()
        return self.X

    def true_front(self) -> np.ndarray:
        return self.T[self.front_idx]

    def hv_star(self, ref: np.ndarray) -> float:
        f = self.true_front()
        return hv3d(f, ref) if self.M == 3 else hv(f, ref)

    def evaluate(self, idx, replicate: int) -> np.ndarray:
        idx = np.atleast_1d(np.asarray(idx, np.int64))
        y = self.T[idx].copy()
        if self.noisy:
            lvl = int(round(self.noise_mult * 100))
            for r, i in enumerate(idx):
                rng = np.random.default_rng(seed_int(self.pid, 0, lvl, replicate, int(i)))
                y[r] += rng.normal(0.0, self.noise_sd)
        return y


if __name__ == "__main__":
    if sys.argv[1] == "build":
        from sr_common import assert_bogp, set_threads
        set_threads(4)
        assert_bogp()
        names = sys.argv[2:] or PROBLEMS_6D
        build([] if names == ["2d"] else names)
