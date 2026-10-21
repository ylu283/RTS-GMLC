"""Prompt 42 Amendment 1 figures, drawn from the CONVERGED sweep ONLY.

Fig 1  criteria-vs-floor map + metric curves (CI band [180, 880],
       break-even floors 1,133 / 1,726 / 1,997, bound-INACTIVE shading).
Fig 2  1x3 shed parity row (n0 = 16/32/48) at floor 306, selected winner.
Fig 3  shed parity n0 = 32, floor 3,000 vs floor 306 side by side, with the
       floor-preview CI text printed ON the figure.

No model is refitted: panels use predictions_converged.csv saved by
sweep_converged.py. Every annotation is ASSERTED against the _converged
CSVs before drawing. Bold axis labels AND bold tick values; PROVISIONAL
watermark on every figure. Style ref: quality_report/bo_1016/
make_fig_parity_winner.py.
"""
from __future__ import annotations

import os

import numpy as np
import pandas as pd

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
DOT = "#1F77B4"
EBAR = "#9ECAE1"
N0S = (16, 32, 48)
N0_COLORS = {16: "#C7652A", 32: "#1F77B4", 48: "#2A7E43"}
F = [180.0, 306.0, 500.0, 880.0, 1500.0, 1800.0, 3000.0]
CI_BAND = (180.0, 880.0)
BREAK_EVENS = (1133.0, 1726.0, 1997.0)
COV_BAND = (43, 48)

sweep = pd.read_csv(os.path.join(HERE, "provisional_sweep_converged.csv"))
bars = pd.read_csv(os.path.join(HERE, "joint_bar_converged.csv"))
preds = pd.read_csv(os.path.join(HERE, "predictions_converged.csv"))

assert sorted(sweep["floor"].unique()) == F
assert sorted(bars["floor"].unique()) == F


def bold_ticks(ax):
    for lab in ax.get_xticklabels() + ax.get_yticklabels():
        lab.set_fontweight("bold")


def watermark(fig):
    fig.text(0.5, 0.5, "PROVISIONAL", fontsize=58, color="gray", alpha=0.16,
             ha="center", va="center", rotation=28, fontweight="bold", zorder=0)


def winner_cfg(f):
    w = bars[(bars.floor == f) & (bars.role == "winner")]
    assert len(w) == 1
    return w.iloc[0]["config"]


def parity_panel(ax, f, n0, cfg_name, div=1e3, annotate_pass=None):
    """One parity panel from the saved predictions; asserts cov95 and RMSE
    against provisional_sweep_converged.csv before drawing."""
    p = preds[(preds.floor == f) & (preds.config == cfg_name) & (preds.n0 == n0)]
    assert len(p) == 48, (f, cfg_name, n0, len(p))
    row = sweep[(sweep.floor == f) & (sweep.config == cfg_name) & (sweep.n0 == n0)].iloc[0]
    act, pm = p["actual"].to_numpy(), p["pred_median_raw"].to_numpy()
    lo, hi = p["lo_raw"].to_numpy(), p["hi_raw"].to_numpy()
    cov = int(((act >= lo) & (act <= hi)).sum())
    rmse = float(np.sqrt(np.mean((pm - act) ** 2)))
    assert cov == int(row["cov95"]), (f, cfg_name, n0, cov, row["cov95"])
    # 1e-6 relative: predict_t is float32, so the CSV round-trip carries
    # ~1e-8 relative noise; annotations print whole MWh.
    assert abs(rmse - row["rmse"]) <= 1e-6 * max(1.0, row["rmse"]), (f, cfg_name, n0)

    a, m = act / div, pm / div
    allv = np.concatenate([a, m])
    pad = 0.06 * (allv.max() - allv.min())
    lims = (float(allv.min() - pad), float(allv.max() + pad))
    ax.plot(lims, lims, "--", color="black", lw=1.2, zorder=1)
    ax.errorbar(a, m, yerr=[m - lo / div, hi / div - m], fmt="o", ms=4.5,
                color=DOT, ecolor=EBAR, elinewidth=1.2, capsize=2,
                alpha=0.9, zorder=3)
    ax.set_xlim(lims)
    ax.set_ylim(lims)
    ax.set_aspect("equal")
    txt = f"RMSE {rmse:,.0f} MWh\ncov95 {cov}/48"
    if annotate_pass is not None:
        txt += f"\n{annotate_pass}"
    ax.annotate(txt, xy=(0.03, 0.97), xycoords="axes fraction", va="top",
                fontsize=9.5, fontweight="bold")
    ax.spines[["top", "right"]].set_visible(False)
    bold_ticks(ax)
    return cov, rmse


# ------------------------------------------------------------------ Fig 1
def fig1():
    fig = plt.figure(figsize=(12.6, 11.2), dpi=200)
    gs = fig.add_gridspec(3, 2, height_ratios=(1.15, 1, 1), hspace=0.42, wspace=0.26)

    # ---- panel A: criteria map (per-floor winner + default sensitivity)
    axm = fig.add_subplot(gs[0, :])
    roles = [("winner", "per-floor winner"), ("default", "default m52+std")]
    crits = [("c1", "cov95 in [43,48]"), ("c2a", "RMSE falls with n0 (a)"),
             ("c2b", "RMSE <= floor (b)"), ("c3", "latent ratio >= 2"),
             ("pass", "JOINT PASS")]
    ny = len(roles) * len(crits)
    for yi, (role, rlab) in enumerate(roles):
        for ci, (ck, clab) in enumerate(crits):
            yrow = ny - 1 - (yi * len(crits) + ci)
            for xi, f in enumerate(F):
                r = bars[(bars.floor == f) & (bars.role == role)]
                assert len(r) == 1
                ok = bool(r.iloc[0][ck])
                axm.add_patch(plt.Rectangle(
                    (xi, yrow), 1, 1,
                    facecolor=("#2A7E43" if ok else "#C23B22"),
                    alpha=0.9 if ck == "pass" else 0.55, edgecolor="white", lw=1.5))
                axm.text(xi + 0.5, yrow + 0.5, "P" if ok else "F", ha="center",
                         va="center", fontsize=9, fontweight="bold", color="white")
    axm.set_xlim(0, len(F))
    axm.set_ylim(0, ny)
    axm.set_xticks([i + 0.5 for i in range(len(F))])
    axm.set_xticklabels([f"{f:,.0f}" for f in F])
    labels = [f"{rl}: {cl}" for _, rl in roles for _, cl in crits]
    axm.set_yticks([ny - 0.5 - i for i in range(ny)])
    axm.set_yticklabels(labels, fontsize=8.5)
    axm.set_xlabel("Shed noise floor f [MWh]", fontweight="bold", fontsize=11)
    axm.set_title("Criteria vs floor, CONVERGED fits (P = met at all three $n_0$; "
                  "winner arm decides F_pass, default arm = sensitivity; red floors = CI [180, 880])",
                  fontweight="bold", fontsize=11.5)
    bold_ticks(axm)
    # CI band on the map: red tick labels for floors inside [180, 880]
    for lab, f in zip(axm.get_xticklabels(), F):
        if CI_BAND[0] <= f <= CI_BAND[1]:
            lab.set_color("#8B0000")

    # ---- panels B-E: metric curves (winner solid, default dotted)
    inactive = sorted(bars[bars["bound_active_n0"].astype(str).str.contains("i")]["floor"].unique())

    def curves(ax, metric, title, ylab, hline=None, band=None, logy=False):
        for role, ls in (("winner", "-"), ("default", ":")):
            for n0 in N0S:
                g = sweep[(sweep.role == role) & (sweep.n0 == n0)].sort_values("floor")
                assert list(g["floor"]) == F
                ax.plot(g["floor"], g[metric], ls, marker="o", ms=4,
                        color=N0_COLORS[n0], lw=1.8 if role == "winner" else 1.2,
                        label=f"{role} $n_0$={n0}" if metric == "cov95" else None)
        ax.axvspan(*CI_BAND, color="#777777", alpha=0.12)
        for be in BREAK_EVENS:
            ax.axvline(be, color="#999999", ls="--", lw=0.9)
        for f in inactive:
            ax.axvspan(f * 0.97, f * 1.03, color="#C7A500", alpha=0.25)
        if band:
            ax.axhspan(*band, color="#2A7E43", alpha=0.10)
        if hline is not None:
            ax.axhline(hline, color="#2A7E43", ls="-", lw=1.0, alpha=0.6)
        ax.set_xscale("log")
        ax.set_xticks(F)
        ax.set_xticklabels([f"{f:,.0f}" for f in F], rotation=45, fontsize=8)
        ax.minorticks_off()
        if logy:
            ax.set_yscale("log")
        ax.set_xlabel("Floor f [MWh]", fontweight="bold", fontsize=10.5)
        ax.set_ylabel(ylab, fontweight="bold", fontsize=10.5)
        ax.set_title(title, fontweight="bold", fontsize=11)
        ax.spines[["top", "right"]].set_visible(False)
        bold_ticks(ax)

    axb = fig.add_subplot(gs[1, 0])
    curves(axb, "cov95", "Holdout cov95 (bar: [43, 48])", "cov95 of 48", band=COV_BAND)
    axb.legend(fontsize=7, ncol=2, frameon=False)
    axc = fig.add_subplot(gs[1, 1])
    curves(axc, "rmse", "Holdout RMSE (gray band = floor CI [180, 880];\n"
                        "dashes = break-evens 1,133 / 1,726 / 1,997)", "RMSE [MWh]")
    axd = fig.add_subplot(gs[2, 0])
    curves(axd, "latent_sd_ratio", "Latent-sd ratio (bar: >= 2)", "max/min latent sd")
    axd.axhline(2.0, color="#2A7E43", ls="-", lw=1.2, alpha=0.8)
    axe = fig.add_subplot(gs[2, 1])
    curves(axe, "median_halfwidth_raw", "Median 95%-band half-width (recorded, not a criterion)",
           "half-width [MWh]", logy=True)

    note = ("CONVERGED fits (5,000 Adam steps; Amendment 1). Noise bound ACTIVE at every floor"
            if not inactive else
            "Pinned ACTIVE flag (1.001) reads INACTIVE (gold) at floors "
            + ", ".join(f"{int(v):,}" for v in inactive)
            + " - learned noise sits 0.1-3% above the bound (context only)")
    fig.suptitle("Prompt 42 Amendment 1 - shed GP criteria vs provisional floor (CONVERGED fits)\n"
                 + note, fontweight="bold", fontsize=13, y=0.995)
    watermark(fig)
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(HERE, f"fig1_criteria_vs_floor_converged.{ext}"),
                    bbox_inches="tight")
    plt.close(fig)
    print("fig1 written; bound-INACTIVE floors:", inactive)


# ------------------------------------------------------------------ Fig 2
def fig2():
    f = 306.0
    cfg = winner_cfg(f)
    wrow = bars[(bars.floor == f) & (bars.role == "winner")].iloc[0]
    fig, axes = plt.subplots(1, 3, figsize=(12.0, 4.4), dpi=200)
    for k, n0 in enumerate(N0S):
        ax = axes[k]
        parity_panel(ax, f, n0, cfg)
        ax.set_title(f"$n_0$ = {n0}", fontweight="bold", fontsize=13)
        if k == 0:
            ax.set_ylabel("Predicted load shed\n[MWh, thousands]",
                          fontweight="bold", fontsize=11)
        ax.set_xlabel("Actual [MWh, thousands]", fontweight="bold", fontsize=11)
    verdict = "JOINT PASS" if bool(wrow["pass"]) else "joint bar NOT met"
    fig.suptitle(f"Shed parity on the frozen holdout at floor 306 MWh - "
                 f"selected winner {cfg} (CONVERGED fits); {verdict}",
                 fontweight="bold", fontsize=12.5, y=1.0)
    watermark(fig)
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(HERE, f"fig2_parity_306_converged.{ext}"),
                    bbox_inches="tight")
    plt.close(fig)
    print(f"fig2 written (winner at 306: {cfg}, pass={bool(wrow['pass'])})")


# ------------------------------------------------------------------ Fig 3
def fig3():
    n0 = 32
    fig, axes = plt.subplots(1, 2, figsize=(9.6, 5.0), dpi=200)
    for ax, f in zip(axes, (3000.0, 306.0)):
        cfg = winner_cfg(f)
        parity_panel(ax, f, n0, cfg)
        ax.set_title(f"floor = {f:,.0f} MWh\nwinner {cfg}", fontweight="bold",
                     fontsize=12)
        ax.set_xlabel("Actual [MWh, thousands]", fontweight="bold", fontsize=11)
    axes[0].set_ylabel("Predicted load shed [MWh, thousands]",
                       fontweight="bold", fontsize=11)
    fig.suptitle("Shed parity, $n_0$ = 32: campaign floor 3,000 vs provisional 306 "
                 "(CONVERGED fits)", fontweight="bold", fontsize=12.5, y=0.99)
    fig.text(0.5, 0.015,
             "floor preview 306 MWh, 95% CI [180, 880], n = 4; measurement in flight",
             ha="center", fontsize=11, fontweight="bold", color="#8B0000")
    watermark(fig)
    fig.tight_layout(rect=(0, 0.05, 1, 0.92))
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(HERE, f"fig3_parity_3000_vs_306_converged.{ext}"),
                    bbox_inches="tight")
    plt.close(fig)
    print("fig3 written")


if __name__ == "__main__":
    fig1()
    fig2()
    fig3()
