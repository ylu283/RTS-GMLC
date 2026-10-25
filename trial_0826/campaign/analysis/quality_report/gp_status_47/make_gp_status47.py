"""Prompt 47: GP status pack — the deployed GP (D-1025) at n0 = 32 and 48.

PROVENANCE: a COPY of quality_report/bo_1025/make_fig_deployed_gp.py
(itself a byte-identical refit of bo_1016/make_fig_parity_nofloor.py).
Kept unchanged: DEFAULT_CFG (m52+std), FLOORS, the 1e-9 free-noise
constant, torch.manual_seed(0) immediately before EVERY FlexGP call,
common.metrics (with the same y_range argument), common.load_wave_xy
("random_C") read-only. Each fit is independently re-seeded, so loop order
does not affect reproduction.
Restructured: the arm loop is split into fit_all() (all three n0 fitted so
the recorded triplets assert) and a per-n0 figure function fig_n0() (PLOTS
only n0 = 32 and 48).
Dropped (disclosed): the floored companion fit that the source ran only to
print its noise beside the free one — it never entered a plotted number.
Added: latent sd (bo_1021 convention, inlined below), median 95% half-width,
the table outputs.

Assert source: bo_1025/SLIDE_TEXT_1025.md (no stdout log exists):
shed RMSE/floor 0.582 / 0.494 / 0.325; cov95 shed 45/45/48, curt 44/45/47,
cost 48/48/48; inferred shed noise 332 / 317 / 527 (n0 = 16 / 32 / 48).
Any mismatch HALTS (never a refit license).

Holdout is RETIRED for selection: this is a deterministic replay of the
recorded scorings of the decided config only — no new model–holdout pair.

Run: /opt/anaconda3/envs/bogp-botorch/bin/python make_gp_status47.py
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
IDIR = os.path.abspath(os.path.join(HERE, "..", "..", "initial_design"))
sys.path.insert(0, IDIR)

import gpytorch  # noqa: E402
import torch  # noqa: E402

import common  # noqa: E402
from common import DEFAULT_CFG, FLOORS, M_COLS, SHORT, FlexGP  # noqa: E402

import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

# legacy-notebook styling: matplotlib default blue, black dashed identity line
DOT = "#1F77B4"
EBAR = "#9ECAE1"
LINE = "black"

LABELS = {"shed": "Load shed", "curt": "Curtailment", "cost_ls": "Cost (less synth.)"}
UNITS = {"shed": ("MWh (thousands)", 1e3), "curt": ("MWh (thousands)", 1e3),
         "cost_ls": ("$M", 1e6)}
HW_UNIT = {"shed": "GWh", "curt": "GWh", "cost_ls": "$M"}
N0S = (16, 32, 48)
PLOT_N0S = (32, 48)

RECORDED = {  # bo_1025/SLIDE_TEXT_1025.md
    ("shed", "rmse_over_floor"): (0.582, 0.494, 0.325),
    ("shed", "cov95"): (45, 45, 48),
    ("curt", "cov95"): (44, 45, 47),
    ("cost_ls", "cov95"): (48, 48, 48),
    ("shed", "noise"): (332, 317, 527),
}


def latent_sd_t(gp, Xq):
    """Inlined from floor40 noise_floor/provisional/sweep_converged.py::latent_sd_t
    (the bo_1021 convention): latent (noise-free) posterior sd, original units
    for the std transform."""
    xq = torch.tensor((np.atleast_2d(Xq) - gp.mx) / gp.sx, dtype=torch.float32)
    with torch.no_grad(), gpytorch.settings.fast_pred_var():
        return gp.model(xq).stddev.numpy() * gp.sy


def fit_all(Xh, Yh):
    res = {}
    for i, col in enumerate(M_COLS):
        s = SHORT[col]
        yh = Yh[:, i]
        y_range = float(yh.max() - yh.min())
        for arm in N0S:
            X, Y = common.arm_data(arm)
            torch.manual_seed(0)
            gp = FlexGP(X, Y[:, i], 1e-9, DEFAULT_CFG)               # free noise
            noise_u = float(np.sqrt(float(gp.lik.noise.detach())) * gp.sy)
            mu, sd = gp.predict_t(Xh)
            m, z = common.metrics(yh, mu, sd, DEFAULT_CFG[1], FLOORS[col],
                                  y_range=y_range)
            lat = latent_sd_t(gp, Xh)
            res[(s, arm)] = {"col": col, "mu": mu, "sd": sd, "yh": yh, "m": m,
                             "noise": noise_u, "half_med": float(np.median(1.96 * sd)),
                             "latent_share": float(np.median(lat / sd))}
            print(f"{s:8s} n0={arm:2d}  rmse {m['rmse']:14,.1f}  rmse/floor {m['rmse_over_floor']:7.3f}  "
                  f"cov95 {m['cov95']}/48  noise free {noise_u:14,.1f}  "
                  f"half95 med {res[(s, arm)]['half_med']:14,.1f}  latent share {res[(s, arm)]['latent_share']:.3f}")
    return res


def check_recorded(res):
    bad = []
    for (s, key), want in RECORDED.items():
        for arm, w in zip(N0S, want):
            r = res[(s, arm)]
            got = {"rmse_over_floor": round(r["m"]["rmse_over_floor"], 3),
                   "cov95": r["m"]["cov95"], "noise": round(r["noise"])}[key]
            if got != w:
                bad.append((s, key, arm, got, w))
    if bad:
        raise SystemExit(f"HALT: recorded-number mismatch {bad}")
    print("recorded triplets: ALL MATCH")


def fig_n0(res, arm):
    fig, axes = plt.subplots(1, 3, figsize=(16.0, 6.2), dpi=200)
    for ax, col in zip(axes, M_COLS):
        s = SHORT[col]
        r = res[(s, arm)]
        unit_lab, div = UNITS[s]
        pred, half, act = r["mu"] / div, 1.96 * r["sd"] / div, r["yh"] / div
        lim_lo = min(act.min(), (pred - half).min())
        lim_hi = max(act.max(), (pred + half).max())
        pad = 0.04 * (lim_hi - lim_lo)
        lims = (lim_lo - pad, lim_hi + pad)
        ax.plot(lims, lims, "--", color=LINE, lw=1.2, zorder=1)
        ax.errorbar(act, pred, yerr=half, fmt="o", ms=4.5,
                    color=DOT, ecolor=EBAR, elinewidth=1.2, capsize=2,
                    alpha=0.9, zorder=3)
        ax.set_xlim(lims)
        ax.set_ylim(lims)
        ax.set_aspect("equal")
        ax.annotate(f"RMSE/floor {r['m']['rmse_over_floor']:.2f}\n"
                    f"cov95 {r['m']['cov95']}/48\n"
                    f"median 95% half-width {r['half_med'] / div:,.2f} {HW_UNIT[s]}",
                    xy=(0.03, 0.97), xycoords="axes fraction", va="top", fontsize=11,
                    fontweight="bold")
        ax.set_title(LABELS[s], fontweight="bold", fontsize=14)
        ax.set_ylabel(f"Predicted [{unit_lab}]", fontweight="bold", fontsize=12)
        ax.set_xlabel(f"Actual [{unit_lab}]", fontweight="bold", fontsize=12)
        for lab in ax.get_xticklabels() + ax.get_yticklabels():
            lab.set_fontweight("bold")
            lab.set_fontsize(11)
        ax.spines[["top", "right"]].set_visible(False)
    fig.suptitle(f"Deployed GP (D-1025): m52+std, noise inferred — $n_0$ = {arm}, "
                 "48-design random_C holdout", fontweight="bold", fontsize=15)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(HERE, f"fig_gp{arm}.{ext}"), bbox_inches="tight")
    plt.close(fig)


def table(res):
    rows = []
    for col in M_COLS:
        s = SHORT[col]
        for arm in PLOT_N0S:
            r = res[(s, arm)]
            rows.append({"objective": s, "n0": arm, "rmse_raw": r["m"]["rmse"],
                         "assumed_floor": FLOORS[col],
                         "rmse_over_assumed_floor": r["m"]["rmse_over_floor"],
                         "cov95_of_48": r["m"]["cov95"], "inferred_noise_sd_raw": r["noise"],
                         "median_95_halfwidth_raw": r["half_med"],
                         "latent_share_median": r["latent_share"]})
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(HERE, "gp_status_table.csv"), index=False)
    return df


if __name__ == "__main__":
    torch.set_num_threads(4)
    Xh, Yh = common.load_wave_xy("random_C")
    assert Xh.shape == (48, 6)
    res = fit_all(Xh, Yh)
    check_recorded(res)
    for arm in PLOT_N0S:
        fig_n0(res, arm)
    print(table(res).to_string(index=False))
    print("wrote fig_gp32/fig_gp48 (.png/.pdf), gp_status_table.csv")
