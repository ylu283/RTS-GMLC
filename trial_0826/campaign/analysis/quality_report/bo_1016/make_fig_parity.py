"""fig_parity_holdout.png — predicted vs actual on the 48-design holdout,
default (campaign) GP, n0 = 16 / 32 / 48. Legacy-notebook-style parity view.

This is a RE-PLOT of the already-budgeted prompt-39 holdout scores, not a new
holdout touch: the fits are deterministic (torch.manual_seed(0), same config,
same data) and the script ASSERTS that the recomputed rmse_over_floor / cov95
match holdout_results.csv (role=default) exactly before drawing anything.

Run:  /opt/anaconda3/envs/bogp-botorch/bin/python make_fig_parity.py
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
IDIR = os.path.abspath(os.path.join(HERE, "..", "..", "initial_design"))
sys.path.insert(0, IDIR)

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

ref = pd.read_csv(os.path.join(IDIR, "holdout_results.csv"))
ref = ref[ref["role"] == "default"].set_index(["objective", "arm"])

Xh, Yh = common.load_wave_xy("random_C")
assert Xh.shape == (48, 6)

fig, axes = plt.subplots(3, 3, figsize=(11.2, 10.2), dpi=200)

for i, col in enumerate(M_COLS):
    s = SHORT[col]
    yh = Yh[:, i]
    y_range = float(yh.max() - yh.min())
    unit_lab, div = UNITS[s]
    for k, arm in enumerate((16, 32, 48)):
        X, Y = common.arm_data(arm)
        torch.manual_seed(0)
        gp = FlexGP(X, Y[:, i], FLOORS[col], DEFAULT_CFG)
        mu, sd = gp.predict_t(Xh)
        m, z = common.metrics(yh, mu, sd, DEFAULT_CFG[1], FLOORS[col],
                              y_range=y_range)
        r = ref.loc[(s, arm)]
        assert abs(m["rmse_over_floor"] - r["rmse_over_floor"]) < 1e-9, (s, arm)
        assert m["cov95"] == int(r["cov95"]), (s, arm)

        pred = common.median_raw(mu, DEFAULT_CFG[1]) / div
        lo = common.median_raw(mu - 1.96 * sd, DEFAULT_CFG[1]) / div
        hi = common.median_raw(mu + 1.96 * sd, DEFAULT_CFG[1]) / div
        act = yh / div

        ax = axes[i, k]
        lim_lo = min(act.min(), lo.min())
        lim_hi = max(act.max(), hi.max())
        pad = 0.04 * (lim_hi - lim_lo)
        lims = (lim_lo - pad, lim_hi + pad)
        ax.plot(lims, lims, "--", color=LINE, lw=1.2, zorder=1)
        ax.errorbar(act, pred, yerr=[pred - lo, hi - pred], fmt="o", ms=4.5,
                    color=DOT, ecolor=EBAR, elinewidth=1.2, capsize=2,
                    alpha=0.9, zorder=3)
        ax.set_xlim(lims)
        ax.set_ylim(lims)
        ax.set_aspect("equal")
        ax.annotate(f"RMSE/floor {m['rmse_over_floor']:.2f}\n"
                    f"cov95 {m['cov95']}/48", xy=(0.03, 0.97),
                    xycoords="axes fraction", va="top", fontsize=9.5,
                    fontweight="bold")
        if i == 0:
            ax.set_title(f"$n_0$ = {arm}", fontweight="bold", fontsize=13)
        if k == 0:
            ax.set_ylabel(f"Predicted\n{LABELS[s]} [{unit_lab}]",
                          fontweight="bold", fontsize=11)
        if i == 2:
            ax.set_xlabel(f"Actual [{unit_lab}]", fontweight="bold",
                          fontsize=11)
        for lab in ax.get_xticklabels() + ax.get_yticklabels():
            lab.set_fontweight("bold")
        ax.spines[["top", "right"]].set_visible(False)
        print(f"{s:8s} n0={arm:2d}  rmse/floor {m['rmse_over_floor']:7.3f} "
              f"(ref {r['rmse_over_floor']:7.3f})  cov95 {m['cov95']}/48 OK")

fig.suptitle("Holdout parity (48 unseen random designs, campaign-default GP): "
             "error bars shrink left to right", fontweight="bold", fontsize=14,
             y=0.995)
fig.tight_layout(rect=(0, 0, 1, 0.985))
for ext in ("png", "pdf"):
    fig.savefig(os.path.join(HERE, f"fig_parity_holdout.{ext}"),
                bbox_inches="tight")
print("wrote fig_parity_holdout.png/.pdf")
