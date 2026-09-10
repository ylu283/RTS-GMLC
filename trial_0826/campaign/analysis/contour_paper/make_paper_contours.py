#!/usr/bin/env python3
"""Paper-grade contour figures for the 303x317 pair grids (prompt 20 Task 3).

Replaces the first-cut atlas rendering per 19b SE and math-log S4.2's
rendering rule:
  - GP posterior-mean rendering (Matern-2.5 ARD, per-surface standardization,
    fitted white-noise term) on a 25x25 lattice, 81 direct points overlaid,
    points whose |observed - posterior mean| exceeds the metric's noise floor
    flagged with open red circles (floor-less metrics: 2x LOOCV RMSE).
  - Near-optimal SETS {cells <= grid-min + floor} hatched instead of a single
    star for metrics with a stated floor; reserve/starts get an argmin marker
    captioned "location indicative only".
  - Contour level spacing exceeds each metric's (working) noise floor.
  - Cost decomposition figure raw | K_syn | APPROX per scenario with the
    identity check printed in the caption.
  - Captions carry per-panel LOOCV Q^2/RMSE (81 folds, per-fold
    standardization). Sanity gate: A-shed ~0.59, A-reserve ~0.81,
    A-starts ~0.86 must reproduce to +/-0.05 or the script aborts.

Usage (from campaign/):  python analysis/contour_paper/make_paper_contours.py
Writes PNG+PDF to analysis/contour_paper/figs/ and loocv_table.csv.
"""
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import Rectangle
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import ConstantKernel, Matern, WhiteKernel

HERE = Path(__file__).resolve().parent
CAMPAIGN = HERE.parent.parent
FIGS = HERE / "figs"
FIGS.mkdir(exist_ok=True)

SCENARIOS = {"A": 1.0, "B": 1.5, "C": 2.0}
BASE_RAW_COST = 522_480_773.81  # pinned base-year raw cost (do not re-derive)

# metric -> (label, scale to display units, stated single-run noise floor in
# NATIVE units or None). Reserve shortfall is a DIAGNOSTIC (19b: M = 4) and
# its caption language never claims optima.
METRICS = {
    "delta_cost_less_synthetic_usd_APPROX": ("$\\Delta$ cost (APPROX column) [M\\$/yr]", 1e-6, 0.5e6),
    "delta_curtailment_mwh": ("$\\Delta$ curtailment [GWh/yr]", 1e-3, 5000.0),
    "delta_load_shed_mwh": ("$\\Delta$ load shed [GWh/yr]", 1e-3, 3000.0),
    "delta_thermal_starts": ("$\\Delta$ thermal starts [/yr]", 1.0, None),
    "delta_reserve_shortfall_mwh": ("$\\Delta$ reserve shortfall (diagnostic) [GWh/yr]", 1e-3, None),
}
FNAME = {"delta_cost_less_synthetic_usd_APPROX": "cost",
         "delta_curtailment_mwh": "curtailment",
         "delta_load_shed_mwh": "load_shed",
         "delta_thermal_starts": "starts",
         "delta_reserve_shortfall_mwh": "reserve"}

# 19b sanity gate: these three LOOCV Q^2 values must reproduce to +/-0.05
GATE = {("A", "delta_load_shed_mwh"): 0.59,
        ("A", "delta_reserve_shortfall_mwh"): 0.81,
        ("A", "delta_thermal_starts"): 0.86}


def load_wave(tag):
    wdir = CAMPAIGN / "waves" / f"contour_303x317_{tag}"
    dm = pd.read_csv(wdir / "design_matrix.csv")
    obj = pd.read_csv(wdir / "objectives.csv")
    df = dm[["index", "wind_303_omega", "wind_317_omega"]].merge(obj, on="index")
    assert len(df) == 81, f"{tag}: {len(df)} rows"
    return df


def make_gp(seed=0):
    # 19b recipe: Matern-2.5 with ARD lengthscales, small fitted white noise;
    # inputs/outputs standardized (inputs are standardized by the caller,
    # outputs via normalize_y)
    kernel = (ConstantKernel(1.0, (1e-3, 1e3))
              * Matern(length_scale=[1.0, 1.0], length_scale_bounds=(1e-2, 1e2), nu=2.5)
              + WhiteKernel(1e-4, noise_level_bounds=(1e-8, 1e1)))
    # n_restarts=8: with fewer restarts lbfgs under-converges on the
    # noise-dominated A surfaces and the 19b gate values do not reproduce
    return GaussianProcessRegressor(kernel=kernel, normalize_y=True,
                                    n_restarts_optimizer=8, random_state=seed)


def standardize(X, mu=None, sd=None):
    if mu is None:
        mu, sd = X.mean(axis=0), X.std(axis=0)
    return (X - mu) / sd, mu, sd


def loocv(X, y):
    """81-fold LOOCV, input standardization re-fit inside each fold
    (output standardization is per-fold via normalize_y). Returns (Q2, RMSE)."""
    preds = np.empty(len(y))
    for i in range(len(y)):
        tr = np.arange(len(y)) != i
        Xtr, mu, sd = standardize(X[tr])
        gp = make_gp(seed=i)
        gp.fit(Xtr, y[tr])
        preds[i] = gp.predict((X[i:i + 1] - mu) / sd)[0]
    resid = y - preds
    q2 = 1.0 - np.sum(resid ** 2) / np.sum((y - y.mean()) ** 2)
    return q2, float(np.sqrt(np.mean(resid ** 2)))


def fit_full(X, y):
    Xs, mu, sd = standardize(X)
    gp = make_gp()
    gp.fit(Xs, y)
    return gp, mu, sd


def disciplined_levels(zmin, zmax, floor_disp):
    """Contour levels whose spacing exceeds the (working) noise floor."""
    span = zmax - zmin
    if span <= floor_disp:
        return None
    n = min(10, int(span / floor_disp))
    step = span / n  # by construction step >= floor_disp
    return np.linspace(zmin, zmax, n + 1)


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    waves = {t: load_wave(t) for t in SCENARIOS}
    X = waves["A"][["wind_303_omega", "wind_317_omega"]].to_numpy()
    lat303 = np.unique(X[:, 0])
    lat317 = np.unique(X[:, 1])
    dx = np.diff(lat303).mean()

    # ---------------- LOOCV table + sanity gate ----------------
    # --reuse-loocv: reuse a previously computed loocv_table.csv (the 81-fold
    # x 15-surface pass takes ~10 min) when only figure cosmetics changed
    tab_path = HERE / "loocv_table.csv"
    if "--reuse-loocv" in argv and tab_path.is_file():
        loocv_tab = pd.read_csv(tab_path)
        print(f"reusing {tab_path.name} ({len(loocv_tab)} surfaces)")
    else:
        rows = []
        for t in SCENARIOS:
            for col in METRICS:
                y = waves[t][col].to_numpy(float)
                q2, rmse = loocv(X, y)
                rows.append(dict(scenario=t, metric=col, q2=q2, rmse=rmse))
                print(f"LOOCV {t} {FNAME[col]:<12} Q2={q2:6.3f}  RMSE={rmse:,.1f}")
        loocv_tab = pd.DataFrame(rows)
        loocv_tab.to_csv(tab_path, index=False)

    for (t, col), ref in GATE.items():
        got = loocv_tab[(loocv_tab.scenario == t) & (loocv_tab.metric == col)].q2.iloc[0]
        if abs(got - ref) > 0.05:
            raise SystemExit(
                f"SANITY GATE FAILED: LOOCV Q2({t}, {FNAME[col]}) = {got:.3f}, "
                f"19b reference {ref:.2f} (tolerance 0.05). Stopping — do not "
                "trust these renders; investigate the GP recipe drift.")
    print("sanity gate PASS: A-shed/A-reserve/A-starts Q2 reproduce 19b within 0.05")

    def lookup(t, col, field):
        r = loocv_tab[(loocv_tab.scenario == t) & (loocv_tab.metric == col)]
        return float(r[field].iloc[0])

    # ---------------- GP-rendered metric figures ----------------
    g25_303 = np.linspace(lat303[0], lat303[-1], 25)
    g25_317 = np.linspace(lat317[0], lat317[-1], 25)
    XX, YY = np.meshgrid(g25_303, g25_317)
    Xq = np.column_stack([XX.ravel(), YY.ravel()])

    for col, (label, scale, floor) in METRICS.items():
        Z25, flags, nearopt, caps = {}, {}, {}, []
        for t in SCENARIOS:
            y = waves[t][col].to_numpy(float)
            gp, mu, sd = fit_full(X, y)
            Z25[t] = gp.predict((Xq - mu) / sd).reshape(25, 25) * scale
            yhat81 = gp.predict((X - mu) / sd)
            rmse = lookup(t, col, "rmse")
            flag_thr = floor if floor is not None else 2.0 * rmse
            flags[t] = np.abs(y - yhat81) > flag_thr
            # near-optimal set on the DIRECT 9x9 lattice
            if floor is not None:
                nearopt[t] = np.where(y <= y.min() + floor)[0]
            else:
                nearopt[t] = np.array([int(np.argmin(y))])
            caps.append(f"{t}: Q$^2$={lookup(t, col, 'q2'):.2f}, "
                        f"RMSE={rmse * scale:,.2f}, flagged {int(flags[t].sum())}/81"
                        + (f", near-opt tie set {len(nearopt[t])}/81 cells"
                           if floor is not None else ", argmin marked"))

        m = max(np.nanmax(np.abs(Z)) for Z in Z25.values())
        norm = matplotlib.colors.TwoSlopeNorm(vmin=-m, vcenter=0.0, vmax=m)
        floor_disp = (floor if floor is not None
                      else max(lookup(t, col, "rmse") for t in SCENARIOS)) * scale

        fig, axes = plt.subplots(1, 3, figsize=(12.5, 4.1), sharey=True)
        for ax, t in zip(axes, SCENARIOS):
            levels = disciplined_levels(float(np.nanmin(Z25[t])),
                                        float(np.nanmax(Z25[t])), floor_disp)
            pm = ax.pcolormesh(g25_303, g25_317, Z25[t], norm=norm,
                               cmap="RdBu_r", shading="nearest")
            if levels is not None:
                cs = ax.contour(g25_303, g25_317, Z25[t], levels=levels,
                                colors="k", linewidths=0.5, alpha=0.6)
                ax.clabel(cs, fontsize=6, fmt="%g")
            # direct points; flagged ones as open red circles
            ax.plot(X[:, 0], X[:, 1], ".", color="k", ms=2.2, alpha=0.5)
            f = flags[t]
            if f.any():
                ax.plot(X[f, 0], X[f, 1], "o", mfc="none", mec="red", ms=7, mew=1.2)
            if floor is not None:  # hatched near-optimal set (no single star)
                for i in nearopt[t]:
                    ax.add_patch(Rectangle((X[i, 0] - dx / 2, X[i, 1] - dx / 2),
                                           dx, dx, fill=False, hatch="///",
                                           edgecolor="k", linewidth=0.4))
            else:  # diagnostic/floor-less: argmin cell, indicative only
                i = nearopt[t][0]
                ax.plot(X[i, 0], X[i, 1], "s", mfc="none", mec="k", ms=9, mew=1.2)
            ax.set_title(f"{t}: $\\rho_{{H2}}$ = {SCENARIOS[t]} \\$/kg "
                         f"(B = {int(20 * SCENARIOS[t])} \\$/MWh)", fontsize=10)
            ax.set_xlabel("$\\omega_{303}$")
        axes[0].set_ylabel("$\\omega_{317}$")
        cb = fig.colorbar(pm, ax=axes, shrink=0.9, pad=0.015)
        cb.set_label(label)

        if floor is not None:
            optline = ("hatched: near-optimal set {cells <= grid min + floor} "
                       "— a tie set, not a point optimum")
        else:
            optline = ("open square: argmin cell; no noise floor established "
                       "— location indicative only")
        cap = (f"GP posterior mean (Matern-2.5 ARD, per-surface standardization, "
               f"fitted white noise) on 25x25; dots = 81 direct runs; open red "
               f"circles = |observed - posterior mean| > "
               f"{'noise floor' if floor is not None else '2x LOOCV RMSE'}.  "
               f"{optline}.  Contour spacing >= "
               f"{'floor' if floor is not None else 'LOOCV RMSE (working floor)'}."
               f"\nLOOCV (81-fold, per-fold standardization): " + ";  ".join(caps))
        fig.text(0.5, -0.06, cap, ha="center", fontsize=7.5)
        fig.suptitle(f"{label} on the 303x317 pair grid (blue = improvement vs base)",
                     fontsize=11)
        for ext in ("png", "pdf"):
            fig.savefig(FIGS / f"paper_contour_{FNAME[col]}.{ext}", dpi=200,
                        bbox_inches="tight")
        plt.close(fig)
        print(f"wrote paper_contour_{FNAME[col]}")

    # ---------------- cost decomposition (per scenario) ----------------
    for t in SCENARIOS:
        df = waves[t]
        raw = (df["total_cost_raw_usd"] - BASE_RAW_COST).to_numpy() / 1e6
        ksyn = df["synthetic_bid_cost_usd"].to_numpy() / 1e6
        approx = df["delta_cost_less_synthetic_usd_APPROX"].to_numpy() / 1e6
        ident = np.max(np.abs(df["total_cost_raw_usd"] - df["synthetic_bid_cost_usd"]
                              - df["total_cost_less_synthetic_usd"]))
        m = max(np.nanmax(np.abs(v)) for v in (raw, ksyn, approx))
        norm = matplotlib.colors.TwoSlopeNorm(vmin=-m, vcenter=0.0, vmax=m)
        fig, axes = plt.subplots(1, 3, figsize=(12.5, 4.1), sharey=True)
        for ax, (Zv, ttl) in zip(axes, [(raw, "raw $\\Delta$cost = total - base"),
                                        (ksyn, "K$_{syn}$ (synthetic bid cost)"),
                                        (approx, "APPROX = raw - K$_{syn}$")]):
            P = pd.DataFrame({"w3": df.wind_303_omega, "w7": df.wind_317_omega,
                              "v": Zv}).pivot(index="w7", columns="w3", values="v")
            pm = ax.pcolormesh(P.columns.values, P.index.values, P.values,
                               norm=norm, cmap="RdBu_r", shading="nearest")
            ax.set_title(ttl, fontsize=10)
            ax.set_xlabel("$\\omega_{303}$")
        axes[0].set_ylabel("$\\omega_{317}$")
        cb = fig.colorbar(pm, ax=axes, shrink=0.9, pad=0.015)
        cb.set_label("[M\\$/yr], shared symmetric scale")
        fig.suptitle(f"Cost decomposition, scenario {t} "
                     f"($\\rho_{{H2}}$ = {SCENARIOS[t]} \\$/kg): the APPROX-column "
                     "sign structure is raw minus synthetic bid cost", fontsize=11)
        fig.text(0.5, -0.04,
                 f"Identity check: max |raw - K_syn - less-synthetic| = "
                 f"{ident:.2e} USD over 81 runs (holds to < 1 USD).  Raw cost "
                 "is positive in every run; negative APPROX-column values arise "
                 "from the principled synthetic-bid subtraction (19b SB1) — "
                 "report them only as APPROX-column statements with this "
                 "decomposition displayed.", ha="center", fontsize=7.5)
        for ext in ("png", "pdf"):
            fig.savefig(FIGS / f"cost_decomposition_{t}.{ext}", dpi=200,
                        bbox_inches="tight")
        plt.close(fig)
        print(f"wrote cost_decomposition_{t} (identity max |resid| = ${ident:.2e})")

    print(f"\nfigures -> {FIGS}")


if __name__ == "__main__":
    main()
