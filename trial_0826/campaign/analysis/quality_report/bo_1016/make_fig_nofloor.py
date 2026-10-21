"""fig_shed_nofloor.png — shed parity WITH vs WITHOUT the 3,000 MWh noise
floor, n0 = 16/32/48. Post-hoc ILLUSTRATION only (the no-floor config was not
a pre-registered Part-H axis and is not a candidate): it answers "are the big
shed bars forced by the floor, or inferred from data?".

Mechanically: FlexGP with floor=1e-9 gives an effectively unconstrained
GaussianLikelihood (the floor enters FlexGP only through the GreaterThan
noise constraint); metrics are still computed against the REAL floor.

Run:  /opt/anaconda3/envs/bogp-botorch/bin/python make_fig_nofloor.py
"""
from __future__ import annotations

import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
IDIR = os.path.abspath(os.path.join(HERE, "..", "..", "initial_design"))
sys.path.insert(0, IDIR)

import torch  # noqa: E402

import common  # noqa: E402
from common import DEFAULT_CFG, FLOORS, FlexGP  # noqa: E402

import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

# legacy-notebook styling: matplotlib default blue, black dashed identity line
DOT = "#1F77B4"
EBAR = "#9ECAE1"
LINE = "black"

COL = "load_shed_mwh"
FLOOR = FLOORS[COL]
DIV = 1e3

Xh, Yh = common.load_wave_xy("random_C")
yh = Yh[:, 0]
y_range = float(yh.max() - yh.min())

fig, axes = plt.subplots(2, 3, figsize=(11.2, 7.2), dpi=200)

for row, (tag, floor_fit) in enumerate(
        (("with 3,000 MWh noise floor (campaign)", FLOOR),
         ("noise floor removed (illustration only)", 1e-9))):
    for k, arm in enumerate((16, 32, 48)):
        X, Y = common.arm_data(arm)
        torch.manual_seed(0)
        gp = FlexGP(X, Y[:, 0], floor_fit, DEFAULT_CFG)
        mu, sd = gp.predict_t(Xh)
        m, z = common.metrics(yh, mu, sd, DEFAULT_CFG[1], FLOOR,
                              y_range=y_range)
        noise_mwh = float(np.sqrt(float(gp.lik.noise)) * gp.sy)

        pred = mu / DIV
        half = 1.96 * sd / DIV
        act = yh / DIV

        ax = axes[row, k]
        lim_lo = min(act.min(), (pred - half).min())
        lim_hi = max(act.max(), (pred + half).max())
        pad = 0.04 * (lim_hi - lim_lo)
        lims = (lim_lo - pad, lim_hi + pad)
        ax.plot(lims, lims, "--", color=LINE, lw=1.2, zorder=1)
        ax.errorbar(act, pred, yerr=half, fmt="o", ms=4.5, color=DOT,
                    ecolor=EBAR, elinewidth=1.2, capsize=2, alpha=0.9,
                    zorder=3)
        ax.set_xlim(lims)
        ax.set_ylim(lims)
        ax.set_aspect("equal")
        ax.annotate(f"RMSE/floor {m['rmse_over_floor']:.2f}\n"
                    f"cov95 {m['cov95']}/48   rms z {m['rms_z']:.2f}\n"
                    f"inferred noise sd {noise_mwh:,.0f} MWh",
                    xy=(0.03, 0.97), xycoords="axes fraction", va="top",
                    fontsize=9, fontweight="bold")
        if row == 0:
            ax.set_title(f"$n_0$ = {arm}", fontweight="bold", fontsize=13)
        if k == 0:
            ax.set_ylabel(f"{tag}\nPredicted shed [MWh, thousands]",
                          fontweight="bold", fontsize=10)
        if row == 1:
            ax.set_xlabel("Actual [MWh, thousands]", fontweight="bold",
                          fontsize=11)
        for lab in ax.get_xticklabels() + ax.get_yticklabels():
            lab.set_fontweight("bold")
        ax.spines[["top", "right"]].set_visible(False)
        print(f"{tag[:12]:12s} n0={arm:2d}  rmse/floor {m['rmse_over_floor']:.3f}"
              f"  cov95 {m['cov95']}/48  rms_z {m['rms_z']:.2f}"
              f"  noise_sd {noise_mwh:,.0f} MWh")

fig.suptitle("Load shed: what the noise floor is doing to the error bars",
             fontweight="bold", fontsize=14, y=0.995)
fig.tight_layout(rect=(0, 0, 1, 0.985))
for ext in ("png", "pdf"):
    fig.savefig(os.path.join(HERE, f"fig_shed_nofloor.{ext}"),
                bbox_inches="tight")
print("wrote fig_shed_nofloor.png/.pdf")
