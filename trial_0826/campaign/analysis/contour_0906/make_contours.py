"""Real-data contour atlas for the 303x317 pair grids (scenarios A/B/C).

Reads waves/contour_303x317_{A,B,C}/{design_matrix,objectives}.csv, pivots
each metric onto the 9x9 (omega_303, omega_317) grid, and renders:
  - per-metric 1x3 panels (A | B | C) on a shared symmetric diverging scale
  - per-metric price-shift maps (B-A | C-A)
  - H2 production panels (sequential scale)
Outputs PNG (for the HTML atlas) + PDF (paper) into figs/.
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
CAMPAIGN = HERE.parent.parent
FIGS = HERE / "figs"
FIGS.mkdir(exist_ok=True)

SCENARIOS = {"A": 1.0, "B": 1.5, "C": 2.0}

METRICS = {
    "delta_curtailment_mwh": dict(
        label="Δ curtailment [GWh]", scale=1e-3, fname="curtailment", fmt="%.0f"
    ),
    "delta_load_shed_mwh": dict(
        label="Δ load shed [MWh]", scale=1.0, fname="load_shed", fmt="%.0f"
    ),
    "delta_cost_less_synthetic_usd_APPROX": dict(
        label="Δ gen cost (APPROX) [M$]", scale=1e-6, fname="cost", fmt="%.1f"
    ),
    "delta_reserve_shortfall_mwh": dict(
        label="Δ reserve shortfall [GWh]", scale=1e-3, fname="reserve", fmt="%.0f"
    ),
    "delta_thermal_starts": dict(
        label="Δ thermal starts [count/yr]", scale=1.0, fname="starts", fmt="%.0f"
    ),
}


def load_wave(tag):
    wdir = CAMPAIGN / "waves" / f"contour_303x317_{tag}"
    dm = pd.read_csv(wdir / "design_matrix.csv")
    obj = pd.read_csv(wdir / "objectives.csv")
    df = dm[["index", "wind_303_omega", "wind_317_omega"]].merge(obj, on="index")
    assert len(df) == 81, f"{tag}: {len(df)} rows"
    return df


def pivot(df, col):
    p = df.pivot(index="wind_317_omega", columns="wind_303_omega", values=col)
    return p.columns.values, p.index.values, p.values


def draw_panel(ax, x, y, Z, norm, cmap, fmt, title):
    pm = ax.pcolormesh(x, y, Z, norm=norm, cmap=cmap, shading="gouraud")
    cs = ax.contour(x, y, Z, levels=8, colors="k", linewidths=0.5, alpha=0.6)
    ax.clabel(cs, fontsize=6, fmt=fmt)
    xx, yy = np.meshgrid(x, y)
    ax.plot(xx.ravel(), yy.ravel(), ".", color="k", ms=1.5, alpha=0.35)
    i, j = np.unravel_index(np.nanargmin(Z), Z.shape)
    ax.plot(x[j], y[i], "*", color="w", mec="k", ms=13, mew=0.8)
    ax.set_title(title, fontsize=10)
    ax.set_xlabel(r"$\omega_{303}$")
    return pm


def sym_norm(*arrays):
    m = max(np.nanmax(np.abs(a)) for a in arrays)
    return matplotlib.colors.TwoSlopeNorm(vmin=-m, vcenter=0.0, vmax=m)


def main():
    waves = {t: load_wave(t) for t in SCENARIOS}

    for col, mi in METRICS.items():
        grids = {}
        for t, df in waves.items():
            x, y, Z = pivot(df, col)
            grids[t] = Z * mi["scale"]

        # A | B | C shared-scale panels
        norm = sym_norm(*grids.values())
        fig, axes = plt.subplots(1, 3, figsize=(11.5, 3.8), sharey=True)
        for ax, (t, rho) in zip(axes, SCENARIOS.items()):
            pm = draw_panel(
                ax, x, y, grids[t], norm, "RdBu_r", mi["fmt"],
                rf"{t}: $\rho_{{H2}}$ = {rho} \$/kg (B = {int(20 * rho)} \$/MWh)",
            )
        axes[0].set_ylabel(r"$\omega_{317}$")
        cb = fig.colorbar(pm, ax=axes, shrink=0.9, pad=0.015)
        cb.set_label(mi["label"])
        fig.suptitle(
            f"{mi['label']} on the 303x317 grid (blue = improvement vs base; "
            "★ = grid best)", fontsize=11,
        )
        for ext in ("png", "pdf"):
            fig.savefig(FIGS / f"contour_{mi['fname']}.{ext}", dpi=150,
                        bbox_inches="tight")
        plt.close(fig)

        # price-shift maps B-A, C-A
        dBA, dCA = grids["B"] - grids["A"], grids["C"] - grids["A"]
        norm = sym_norm(dBA, dCA)
        fig, axes = plt.subplots(1, 2, figsize=(8.2, 3.8), sharey=True)
        for ax, (Z, ttl) in zip(
            axes, [(dBA, "B − A  (1.5 vs 1.0 $/kg)"), (dCA, "C − A  (2.0 vs 1.0 $/kg)")]
        ):
            pm = draw_panel(ax, x, y, Z, norm, "PuOr_r", mi["fmt"], ttl)
        axes[0].set_ylabel(r"$\omega_{317}$")
        cb = fig.colorbar(pm, ax=axes, shrink=0.9, pad=0.02)
        cb.set_label(f"shift in {mi['label']}")
        fig.suptitle(f"H2-price shift of {mi['label']}", fontsize=11)
        for ext in ("png", "pdf"):
            fig.savefig(FIGS / f"shift_{mi['fname']}.{ext}", dpi=150,
                        bbox_inches="tight")
        plt.close(fig)

    # H2 production (sequential — magnitude, not polarity)
    fig, axes = plt.subplots(1, 3, figsize=(11.5, 3.8), sharey=True)
    vmax = max(np.nanmax(pivot(df, "h2_kg_total")[2]) for df in waves.values()) / 1e6
    for ax, (t, rho) in zip(axes, SCENARIOS.items()):
        x, y, Z = pivot(waves[t], "h2_kg_total")
        Z = Z / 1e6
        pm = ax.pcolormesh(x, y, Z, vmin=0, vmax=vmax, cmap="viridis",
                           shading="gouraud")
        cs = ax.contour(x, y, Z, levels=6, colors="w", linewidths=0.5, alpha=0.7)
        ax.clabel(cs, fontsize=6, fmt="%.0f")
        ax.set_title(rf"{t}: $\rho_{{H2}}$ = {rho} \$/kg", fontsize=10)
        ax.set_xlabel(r"$\omega_{303}$")
    axes[0].set_ylabel(r"$\omega_{317}$")
    cb = fig.colorbar(pm, ax=axes, shrink=0.9, pad=0.015)
    cb.set_label("H2 production [kt/yr]")
    fig.suptitle("Annual H2 production on the 303x317 grid", fontsize=11)
    for ext in ("png", "pdf"):
        fig.savefig(FIGS / f"contour_h2.{ext}", dpi=150, bbox_inches="tight")
    plt.close(fig)

    # console summary: per-scenario best point per metric
    print("best (most negative) grid point per metric:")
    for col, mi in METRICS.items():
        for t, df in waves.items():
            r = df.loc[df[col].idxmin()]
            print(
                f"  {mi['fname']:<10} {t}: {r[col] * mi['scale']:>10.1f} "
                f"at w303={r.wind_303_omega:.3f} w317={r.wind_317_omega:.3f}"
            )
    print(f"\nfigures -> {FIGS}")


if __name__ == "__main__":
    main()
