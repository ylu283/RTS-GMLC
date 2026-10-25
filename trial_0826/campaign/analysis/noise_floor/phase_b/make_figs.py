"""Prompt 43 Phase-B figures (S8). All four figures are drawn FROM THE
SAVED CSVs (no refit, no new holdout scoring), assert-before-draw
against those CSVs. Conventions: bo_1021/make_fig_parity_latent_306.py
(dual bands: latent dark inside total pale; training points in a second
colour), PROVISIONAL watermark, bold axis labels AND bold tick values.

fig1  winner holdout parity at n0 = 16/32/48, dual bands + training pts
fig2  LOO parity at n0 = 32 (selection-side view)
fig3  sigma(y) overlay: forms (ii) + (iii) + anchors with chi2 CIs
fig4  before/after: prompt-42 converged winner (floor 306, redrawn from
      provisional/predictions_converged.csv) beside the Phase-B winner,
      same axes, n0 = 48

Run: /opt/anaconda3/envs/bogp-botorch/bin/python make_figs.py
"""
from __future__ import annotations

# --- path hygiene: the sibling pinned file select.py shadows the stdlib
# `select` module (see PHASE_B.md deviations).
import os  # noqa: E402
import sys  # noqa: E402
_HERE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path = [p for p in sys.path
            if os.path.abspath(p or os.getcwd()) != _HERE_DIR]
import select as _stdlib_select  # noqa: E402,F401
import subprocess  # noqa: E402,F401
sys.path.insert(0, _HERE_DIR)

import json

import numpy as np
import pandas as pd

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

import phaseb_common as pb  # noqa: E402

HERE = _HERE_DIR
PROV = os.path.abspath(os.path.join(HERE, "..", "provisional"))
K = 1000.0  # axis units: thousands of MWh

C_HOLD = "#2b7bba"
C_HOLD_E = "#5a9bc9"
C_TOT = "#cfe3f0"
C_TRAIN = "#d95f02"
C_TRAIN_E = "#f3b283"

# Lazy-loaded: fig3 must stay drawable under an open STOP-FOR-DECISION
# (no committed winner, holdout untouched); figs 1/2/4 need the full run.
COMMIT = WINNER = VERDICT = None
HOLD = TRAIN = LOO_TAB = LOO_PRED = None


def _load_winner_outputs():
    global COMMIT, WINNER, VERDICT, HOLD, TRAIN, LOO_TAB, LOO_PRED
    if COMMIT is not None:
        return
    with open(os.path.join(HERE, "winner_commit.json")) as fh:
        COMMIT = json.load(fh)
    WINNER = COMMIT["winner"]["name"]
    with open(os.path.join(HERE, "holdout_verdict.json")) as fh:
        VERDICT = json.load(fh)
    HOLD = pd.read_csv(os.path.join(HERE, "holdout_final.csv"))
    TRAIN = pd.read_csv(os.path.join(HERE, "train_predictions.csv"))
    LOO_TAB = pd.read_csv(os.path.join(HERE, "loo_table.csv"))
    LOO_PRED = pd.read_csv(os.path.join(HERE, "loo_predictions.csv"))


def bold_ticks(ax):
    for t in ax.get_xticklabels() + ax.get_yticklabels():
        t.set_fontweight("bold")


def watermark(ax):
    ax.text(0.5, 0.5, "PROVISIONAL", transform=ax.transAxes, fontsize=40,
            color="0.85", alpha=0.55, ha="center", va="center",
            rotation=30, zorder=1)


def save(fig, stem):
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(HERE, f"{stem}.{ext}"), dpi=180)
    plt.close(fig)
    print(f"saved {stem}.png/.pdf")


def vrow(n0):
    return next(r for r in VERDICT["per_n0"] if r["n0"] == n0)


def panel_holdout(ax, n0, show_label=True):
    """One winner-holdout parity panel from the saved CSVs, with the
    pinned assert-before-draw checks. Returns axis limit."""
    g = HOLD[HOLD.n0 == n0].sort_values("i")
    tr = TRAIN[TRAIN.n0 == n0].sort_values("i")
    r = vrow(n0)
    assert len(g) == 48 and len(tr) == n0
    # assert-before-draw against the CSVs / verdict
    rmse = float(np.sqrt(np.mean((g.pred_median_raw - g.actual) ** 2)))
    assert abs(rmse - r["rmse"]) <= 1e-6 * max(r["rmse"], 1.0), (rmse, r)
    cov = int(((g.actual >= g.lo_raw) & (g.actual <= g.hi_raw)).sum())
    assert cov == r["cov95"] == int(g.in_band.sum()), (cov, r["cov95"])
    half_l = float(np.median((g.hi_lat_raw - g.lo_lat_raw) / 2.0))
    half_t = float(np.median((g.hi_raw - g.lo_raw) / 2.0))
    assert abs(half_l - r["median_halfwidth_latent_raw"]) <= 1e-6 * \
        max(half_l, 1.0)
    assert abs(half_t - r["median_halfwidth_total_raw"]) <= 1e-6 * \
        max(half_t, 1.0)

    a, m = g.actual.values, g.pred_median_raw.values
    ax.errorbar(a / K, m / K,
                yerr=[(m - g.lo_raw.values) / K, (g.hi_raw.values - m) / K],
                fmt="none", ecolor=C_TOT, elinewidth=3.2, capsize=0,
                zorder=2)
    ax.errorbar(a / K, m / K,
                yerr=[(m - g.lo_lat_raw.values) / K,
                      (g.hi_lat_raw.values - m) / K],
                fmt="o", ms=6, color=C_HOLD, ecolor=C_HOLD_E,
                elinewidth=1.6, capsize=2.5, zorder=3,
                label="holdout (48 designs)")
    at, mt = tr.actual.values, tr.pred_median_raw.values
    ax.errorbar(at / K, mt / K,
                yerr=[(mt - tr.lo_lat_raw.values) / K,
                      (tr.hi_lat_raw.values - mt) / K],
                fmt="s", ms=6, color=C_TRAIN, ecolor=C_TRAIN_E,
                elinewidth=1.6, capsize=2.5, zorder=4,
                label="training points (latent band)")
    lim = max(a.max(), m.max(), at.max()) / K * 1.04
    ax.plot([0, lim], [0, lim], "k--", lw=1.4, zorder=2)
    ax.set_xlim(-0.6, lim)
    ax.set_ylim(-0.6, lim)
    ax.set_title(f"$n_0$ = {n0}", fontsize=17, fontweight="bold")
    ax.text(0.03, 0.97,
            f"RMSE {r['rmse']:,.0f} MWh   cov95 {r['cov95']}/48\n"
            f"median half-width latent {half_l:,.0f} / "
            f"total {half_t:,.0f} MWh",
            transform=ax.transAxes, va="top", fontsize=11,
            fontweight="bold")
    if show_label:
        ax.set_xlabel("Actual [MWh, thousands]", fontsize=14,
                      fontweight="bold")
    bold_ticks(ax)
    watermark(ax)
    print(f"fig panel n0={n0}: asserts PASS (rmse {rmse:,.0f}; cov95 "
          f"{cov}/48; half-widths {half_l:,.0f}/{half_t:,.0f})")
    return lim


# ------------------------------------------------------------------ fig1
def fig1():
    _load_winner_outputs()
    fig, axes = plt.subplots(1, 3, figsize=(16.5, 5.8), sharey=True)
    for ax, n0 in zip(axes, (16, 32, 48)):
        panel_holdout(ax, n0)
    axes[0].set_ylabel("Predicted load shed\n[MWh, thousands]",
                       fontsize=14, fontweight="bold")
    axes[0].legend(fontsize=11, loc="lower right", frameon=True)
    fig.suptitle(
        f"Phase-B winner {WINNER}: holdout parity, LATENT band (dark) "
        f"inside TOTAL band (pale), measured per-point noise",
        fontsize=15.5, fontweight="bold")
    fig.text(0.5, 0.012,
             "Dark = latent (model-only) band; pale = total band with the "
             "measured sigma(y) at the predicted median. cov95 attaches "
             "to the TOTAL band only. Bars clipped at the frame.",
             ha="center", fontsize=11, color="#8b1a1a", fontweight="bold")
    fig.tight_layout(rect=(0, 0.04, 1, 0.94))
    save(fig, "fig1_parity_winner_3n0")


# ------------------------------------------------------------------ fig2
def fig2():
    _load_winner_outputs()
    g = LOO_PRED[LOO_PRED.config == WINNER].sort_values("i")
    assert len(g) == 32
    row = LOO_TAB[LOO_TAB.config == WINNER].iloc[0]
    rmse = float(np.sqrt(np.mean((g.loo_median_raw - g.actual) ** 2)))
    assert abs(rmse - row.loo_rmse) <= 1e-6 * max(rmse, 1.0)
    cov = int(((g.actual >= g.lo_raw) & (g.actual <= g.hi_raw)).sum())
    assert cov == int(row.loo_cov95), (cov, row.loo_cov95)
    tr = row.transform
    pt = pb.nlpd_pointwise(g.actual.values, g.loo_mu_t.values,
                           g.loo_sd_t.values, tr)
    assert abs(pt.mean() - row.loo_nlpd) <= 1e-9, (pt.mean(), row.loo_nlpd)

    fig, ax = plt.subplots(figsize=(7.0, 6.2))
    a, m = g.actual.values, g.loo_median_raw.values
    ax.errorbar(a / K, m / K,
                yerr=[(m - g.lo_raw.values) / K, (g.hi_raw.values - m) / K],
                fmt="o", ms=6, color=C_HOLD, ecolor=C_HOLD_E,
                elinewidth=1.6, capsize=2.5, zorder=3,
                label="LOO prediction (noise-inclusive band)")
    lim = max(a.max(), m.max()) / K * 1.04
    ax.plot([0, lim], [0, lim], "k--", lw=1.4, zorder=2)
    ax.set_xlim(-0.6, lim)
    ax.set_ylim(-0.6, lim)
    ax.set_xlabel("Actual [MWh, thousands]", fontsize=14,
                  fontweight="bold")
    ax.set_ylabel("LOO predicted load shed [MWh, thousands]",
                  fontsize=14, fontweight="bold")
    ax.set_title(f"Selection-side view: closed-form LOO, $n_0$ = 32,\n"
                 f"winner {WINNER}", fontsize=14, fontweight="bold")
    ax.text(0.03, 0.97,
            f"LOO NLPD {row.loo_nlpd:.3f}   RMSE {rmse:,.0f} MWh\n"
            f"cov95 {cov}/32   rms_z {row.loo_rms_z:.2f}",
            transform=ax.transAxes, va="top", fontsize=11,
            fontweight="bold")
    ax.legend(fontsize=10, loc="lower right", frameon=True)
    bold_ticks(ax)
    watermark(ax)
    fig.tight_layout()
    save(fig, "fig2_loo_parity_n32")
    print(f"fig2 asserts PASS (rmse {rmse:,.0f}; cov95 {cov}/32; nlpd "
          f"{pt.mean():.3f})")


# ------------------------------------------------------------------ fig3
def fig3():
    # assert-before-draw: the slope asserts live in phaseb_common import;
    # re-assert the anchors are reproduced by both forms
    ys = np.array(pb.ANCHOR_Y)
    assert np.allclose(pb.sigma_ii(ys), pb.ANCHOR_SD, atol=1e-9)
    assert np.allclose(pb.sigma_iii(ys), pb.ANCHOR_SD, atol=1e-9)

    yy = np.linspace(0.0, 40000.0, 4001)
    fig, ax = plt.subplots(figsize=(8.0, 5.8))
    ax.plot(yy / K, pb.sigma_ii(yy), lw=2.4, color="#2b7bba",
            label="form (ii): piecewise-linear through the anchors")
    ax.step(yy / K, pb.sigma_iii(yy), lw=2.4, color="#d95f02",
            where="post",
            label="form (iii): per-stratum (bounds 2,000 / 15,000)")
    ax.axhline(pb.POOLED_SD, color="0.45", lw=1.6, ls=":",
               label="pooled scalar 285.3 (reference only)")
    lo = [c[0] for c in pb.ANCHOR_CI]
    hi = [c[1] for c in pb.ANCHOR_CI]
    sd = np.array(pb.ANCHOR_SD)
    ax.errorbar(ys / K, sd, yerr=[sd - np.array(lo), np.array(hi) - sd],
                fmt="D", ms=8, color="k", ecolor="k", elinewidth=1.6,
                capsize=4, zorder=5,
                label=r"anchors $\pm$ 95% $\chi^2$ CI (df 2/3/3)")
    ax.set_ylim(-60, 2000)
    ax.set_xlabel("Shed level y [MWh, thousands]", fontsize=14,
                  fontweight="bold")
    ax.set_ylabel(r"$\sigma(y)$ [MWh]", fontsize=14, fontweight="bold")
    ax.set_title("Measured per-design noise vs shed level\n"
                 "(Population-1 anchors; one design per stratum — "
                 "design and level confounded)",
                 fontsize=11.5, fontweight="bold")
    ax.annotate("HIGH-anchor CI\nreaches 1,939", xy=(37.834, 1939),
                xytext=(27, 1550), fontsize=10, fontweight="bold",
                arrowprops=dict(arrowstyle="->", lw=1.2))
    ax.legend(fontsize=10, loc="upper left", frameon=True)
    bold_ticks(ax)
    watermark(ax)
    fig.tight_layout()
    save(fig, "fig3_sigma_overlay")
    print("fig3 asserts PASS (both forms hit the anchors exactly)")


# ------------------------------------------------------------------ fig4
def fig4():
    _load_winner_outputs()
    n0 = 48
    preds42 = pd.read_csv(os.path.join(PROV, "predictions_converged.csv"))
    swp42 = pd.read_csv(os.path.join(PROV,
                                     "provisional_sweep_converged.csv"))
    g42 = preds42[(preds42.floor == 306.0)
                  & (preds42.config == "rbf+log1p")
                  & (preds42.n0 == n0)].sort_values("i")
    assert len(g42) == 48
    ref = swp42[(swp42.role == "winner") & (swp42.floor == 306.0)
                & (swp42.n0 == n0)].iloc[0]
    assert ref.config == "rbf+log1p"
    rmse42 = float(np.sqrt(np.mean(
        (g42.pred_median_raw - g42.actual) ** 2)))
    assert abs(rmse42 - ref.rmse) <= 1e-4 * max(rmse42, 1.0), \
        (rmse42, ref.rmse)
    cov42 = int(((g42.actual >= g42.lo_raw)
                 & (g42.actual <= g42.hi_raw)).sum())
    assert cov42 == int(ref.cov95), (cov42, ref.cov95)
    half42 = float(np.median((g42.hi_raw - g42.lo_raw) / 2.0))

    fig, axes = plt.subplots(1, 2, figsize=(12.0, 5.9), sharey=True,
                             sharex=True)
    # BEFORE: prompt-42 converged winner at floor 306 (redrawn, no refit)
    ax = axes[0]
    a, m = g42.actual.values, g42.pred_median_raw.values
    ax.errorbar(a / K, m / K,
                yerr=[(m - g42.lo_raw.values) / K,
                      (g42.hi_raw.values - m) / K],
                fmt="o", ms=6, color="0.35", ecolor="0.6",
                elinewidth=1.6, capsize=2.5, zorder=3,
                label="holdout (total band)")
    ax.set_title("BEFORE — prompt 42 converged winner\n"
                 "rbf+log1p, learned noise, floor 306", fontsize=13,
                 fontweight="bold")
    ax.text(0.03, 0.97,
            f"RMSE {rmse42:,.0f} MWh   cov95 {cov42}/48\n"
            f"median half-width (total) {half42:,.0f} MWh",
            transform=ax.transAxes, va="top", fontsize=11,
            fontweight="bold")
    ax.set_ylabel("Predicted load shed [MWh, thousands]", fontsize=13,
                  fontweight="bold")
    ax.legend(fontsize=10, loc="lower right", frameon=True)

    # AFTER: Phase-B winner (same axes); dual bands as fig1
    lim = panel_holdout(axes[1], n0, show_label=False)
    axes[1].set_title(f"AFTER — Phase-B winner {WINNER}\n"
                      "measured per-point noise (fixed)", fontsize=13,
                      fontweight="bold")
    axes[1].legend(fontsize=10, loc="lower right", frameon=True)
    lim = max(lim, max(a.max(), m.max()) / K * 1.04)
    for ax in axes:
        ax.plot([0, lim], [0, lim], "k--", lw=1.4, zorder=2)
        ax.set_xlim(-0.6, lim)
        ax.set_ylim(-0.6, lim)
        ax.set_xlabel("Actual [MWh, thousands]", fontsize=13,
                      fontweight="bold")
        bold_ticks(ax)
    watermark(axes[0])
    fig.suptitle("Before/after at $n_0$ = 48: learned-noise floor model "
                 "vs measured-noise Phase-B model (one-look answer to "
                 "1016-D2)", fontsize=14, fontweight="bold")
    fig.tight_layout(rect=(0, 0.0, 1, 0.94))
    save(fig, "fig4_before_after")
    print(f"fig4 asserts PASS (before: rmse {rmse42:,.0f} cov95 "
          f"{cov42}/48 vs saved sweep row)")


if __name__ == "__main__":
    fig3()
    if os.path.exists(os.path.join(HERE, "winner_commit.json")) and \
            os.path.exists(os.path.join(HERE, "holdout_verdict.json")):
        fig1()
        fig2()
        fig4()
    else:
        print("STOP-FOR-DECISION open (no winner_commit.json / holdout "
              "verdict): figs 1, 2, 4 are deferred; fig3 only.")
