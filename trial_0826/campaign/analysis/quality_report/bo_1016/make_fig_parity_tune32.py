"""fig_parity_tune32.png — tuning before/after at n0 = 32, one parity panel
per objective, default GP (gray) overlaid with the Part-H winner (blue), both
scored on the same untouched 48-design holdout. NOT a new holdout touch:
deterministic refit; the script asserts BOTH roles' rmse_over_floor (1e-9)
and cov95 (exact) against holdout_results.csv before drawing.

Winners (fits.json, committed before any holdout call): shed/curt rbf+log1p,
cost rbf. Default: m52+std.

Run:  /opt/anaconda3/envs/bogp-botorch/bin/python make_fig_parity_tune32.py
"""
from __future__ import annotations

import json
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

DOT_D, EBAR_D = "#8C8C8C", "#D4D4D4"          # default GP: gray
DOT_W, EBAR_W = "#1F77B4", "#9ECAE1"          # winner GP: legacy blue
LINE = "black"

LABELS = {"shed": "Load shed", "curt": "Curtailment", "cost_ls": "Cost (less synth.)"}
UNITS = {"shed": ("MWh (thousands)", 1e3), "curt": ("MWh (thousands)", 1e3),
         "cost_ls": ("$M", 1e6)}
ARM = 32

winners = json.load(open(os.path.join(IDIR, "fits.json")))["winners"]
ref = pd.read_csv(os.path.join(IDIR, "holdout_results.csv"))

Xh, Yh = common.load_wave_xy("random_C")
assert Xh.shape == (48, 6)
X, Y = common.arm_data(ARM)

fig, axes = plt.subplots(1, 3, figsize=(13.2, 4.7), dpi=200)

for i, col in enumerate(M_COLS):
    s = SHORT[col]
    yh = Yh[:, i]
    y_range = float(yh.max() - yh.min())
    unit_lab, div = UNITS[s]
    ax = axes[i]
    stats = {}
    for role, cfg, dot, ebar, z in (
            ("default", DEFAULT_CFG, DOT_D, EBAR_D, 2),
            ("winner", tuple(winners[col]["config"]), DOT_W, EBAR_W, 4)):
        torch.manual_seed(0)
        gp = FlexGP(X, Y[:, i], FLOORS[col], cfg)
        mu, sd = gp.predict_t(Xh)
        m, _ = common.metrics(yh, mu, sd, cfg[1], FLOORS[col], y_range=y_range)
        r = ref[(ref.objective == s) & (ref.role == role) & (ref.arm == ARM)]
        assert len(r) == 1, (s, role)
        r = r.iloc[0]
        assert abs(m["rmse_over_floor"] - r["rmse_over_floor"]) < 1e-9, (s, role)
        assert m["cov95"] == int(r["cov95"]), (s, role)
        stats[role] = m
        pred = common.median_raw(mu, cfg[1]) / div
        lo = common.median_raw(mu - 1.96 * sd, cfg[1]) / div
        hi = common.median_raw(mu + 1.96 * sd, cfg[1]) / div
        ax.errorbar(yh / div, pred, yerr=[pred - lo, hi - pred], fmt="o", ms=4,
                    color=dot, ecolor=ebar, elinewidth=1.0, capsize=0,
                    alpha=0.85, zorder=z,
                    label=("default (m52)" if role == "default"
                           else f"winner ({'+'.join(c for c in cfg[:2] if c != 'std')})"))
        stats[role + "_pts"] = pred
    # limits from actuals + point predictions (log1p upper quantiles can
    # explode on shed; bars beyond the box are clipped, which is fine)
    allv = np.concatenate([yh / div, stats["default_pts"], stats["winner_pts"]])
    pad = 0.06 * (allv.max() - allv.min())
    lims = (float(allv.min() - pad), float(allv.max() + pad))
    ax.plot(lims, lims, "--", color=LINE, lw=1.2, zorder=1)
    ax.set_xlim(lims)
    ax.set_ylim(lims)
    ax.set_aspect("equal")
    ax.annotate(
        f"RMSE/floor {stats['default']['rmse_over_floor']:.2f} → "
        f"{stats['winner']['rmse_over_floor']:.2f}\n"
        f"cov95 {stats['default']['cov95']} → {stats['winner']['cov95']} /48",
        xy=(0.03, 0.97), xycoords="axes fraction", va="top",
        fontsize=10, fontweight="bold")
    ax.set_title(LABELS[s], fontweight="bold", fontsize=13)
    ax.set_xlabel(f"Actual [{unit_lab}]", fontweight="bold", fontsize=11)
    if i == 0:
        ax.set_ylabel(f"Predicted [{unit_lab}]", fontweight="bold", fontsize=11)
        ax.legend(loc="lower right", fontsize=9.5, frameon=False,
                  prop={"weight": "bold"})
    for lab in ax.get_xticklabels() + ax.get_yticklabels():
        lab.set_fontweight("bold")
    ax.spines[["top", "right"]].set_visible(False)
    print(f"{s:8s} default {stats['default']['rmse_over_floor']:6.2f} "
          f"cov {stats['default']['cov95']}  ->  winner "
          f"{stats['winner']['rmse_over_floor']:6.2f} cov {stats['winner']['cov95']}")

fig.suptitle("Tuning before → after at $n_0$ = 32 (same holdout; winners "
             "pre-committed before scoring)", fontweight="bold", fontsize=13.5,
             y=0.99)
fig.tight_layout(rect=(0, 0, 1, 0.96))
for ext in ("png", "pdf"):
    fig.savefig(os.path.join(HERE, f"fig_parity_tune32.{ext}"),
                bbox_inches="tight")
print("wrote fig_parity_tune32.png/.pdf")
