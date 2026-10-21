"""fig_sd_heatmap.png — predictive-sd heatmaps (campaign-default GP, n0=48)
on a 2-D slice of the 6-D design space: shed vs curtailment, same two axes.

Axes = the two tiers with the SMALLEST curtailment ARD lengthscales (most
active); the other four omegas are held at the training median. sd is the
full predictive sd (incl. likelihood noise), shown in floor units, so the
shed panel reads ~1.0 everywhere (floor-pinned: noise-limited) while the
curtailment panel shows real structure (data-limited).

Run:  /opt/anaconda3/envs/bogp-botorch/bin/python make_fig_sdheat.py
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
from common import DEFAULT_CFG, FLOORS, M_COLS, FlexGP  # noqa: E402

import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

NAVY = "#0C2340"
GOLD = "#AE9342"

tiers = common.sorted_tiers()
X, Y = common.arm_data(48)

gps = {}
for j, col in enumerate(M_COLS):
    torch.manual_seed(0)
    gps[col] = FlexGP(X, Y[:, j], FLOORS[col], DEFAULT_CFG)

# pick the 2 most active dims by curtailment ARD lengthscale (standardized X)
curt = gps["true_curtailment_mwh"]
with torch.no_grad():
    ls = curt.model.covar_module.base_kernel.lengthscale.squeeze().numpy()
order = np.argsort(ls)
d1, d2 = int(order[0]), int(order[1])
print("curt ARD lengthscales (standardized):",
      {t: round(float(v), 2) for t, v in zip(tiers, ls)})
print(f"slice axes: {tiers[d1]} (ls {ls[d1]:.2f}), {tiers[d2]} (ls {ls[d2]:.2f})")

G = 80
g1 = np.linspace(X[:, d1].min(), X[:, d1].max(), G)
g2 = np.linspace(X[:, d2].min(), X[:, d2].max(), G)
A, B = np.meshgrid(g1, g2)
base = np.median(X, axis=0)
Xq = np.tile(base, (G * G, 1))
Xq[:, d1] = A.ravel()
Xq[:, d2] = B.ravel()

fig, axes = plt.subplots(1, 2, figsize=(11.6, 4.6), dpi=200)
panels = [("load_shed_mwh", "Load shed: sd pinned to the floor (noise-limited)"),
          ("true_curtailment_mwh",
           "Curtailment: sd follows data density (data-limited)")]
for ax, (col, title) in zip(axes, panels):
    _, sd = gps[col].predict_t(Xq)
    Z = (sd / FLOORS[col]).reshape(G, G)
    im = ax.pcolormesh(A, B, Z, cmap="viridis", shading="auto")
    cb = fig.colorbar(im, ax=ax, pad=0.02)
    cb.set_label("predictive sd / noise floor", fontweight="bold", fontsize=10)
    for lab in cb.ax.get_yticklabels():
        lab.set_fontweight("bold")
    ax.scatter(X[:, d1], X[:, d2], s=26, facecolor="white", edgecolor=NAVY,
               linewidth=1.0, zorder=3, label="48 training designs")
    ax.set_xlabel(f"{tiers[d1]} ω", fontweight="bold", fontsize=11)
    ax.set_ylabel(f"{tiers[d2]} ω", fontweight="bold", fontsize=11)
    ax.set_title(title, fontweight="bold", fontsize=12)
    ax.legend(frameon=True, fontsize=9, loc="upper right")
    for lab in ax.get_xticklabels() + ax.get_yticklabels():
        lab.set_fontweight("bold")
    print(f"{col}: sd/floor range {Z.min():.2f} – {Z.max():.2f}")

fig.suptitle("Uncertainty maps on the 2 most active tiers "
             "(other 4 ω at training median; campaign-default GP, n0 = 48)",
             fontweight="bold", fontsize=13, y=1.0)
fig.tight_layout(rect=(0, 0, 1, 0.97))
for ext in ("png", "pdf"):
    fig.savefig(os.path.join(HERE, f"fig_sd_heatmap.{ext}"),
                bbox_inches="tight")
print("wrote fig_sd_heatmap.png/.pdf")
