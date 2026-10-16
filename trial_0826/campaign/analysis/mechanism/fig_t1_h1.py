#!/usr/bin/env python
"""H1 evidence figure: on the 100 shed hours of the lowest-MW design
(bo_C_r2#3), committed thermal capacity and online headroom across
designs, and the decomposition of the shed difference. Reads
t1_h1_table.csv (run t1_hourly_analysis.py first)."""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

HERE = Path(__file__).resolve().parent
t = pd.read_csv(HERE / "t1_h1_table.csv")
t = t[t["low"] == "bo_C_r2#3"].reset_index(drop=True)

order = ["bo_C_r2#3", "random_C#30", "stage2_C_n0#16", "bo_C_r2#2", "bo_C_r1#5"]
mw = {"bo_C_r2#3": 407, "random_C#30": 1764, "stage2_C_n0#16": 1763,
      "bo_C_r2#2": 2622, "bo_C_r1#5": 2494}
committed = {"bo_C_r2#3": t.iloc[0]["L_committed_mw_mean"]}
headroom = {"bo_C_r2#3": t.iloc[0]["L_headroom_mean"]}
for _, r in t.iterrows():
    committed[r["high"]] = r["H_committed_mw_mean"]
    headroom[r["high"]] = r["H_headroom_mean"]

fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.4))

ax = axes[0]
x = range(len(order))
ax.bar(x, [committed[k] for k in order], color="#2b6cb0",
       label="Committed thermal (mean MW)")
ax.bar(x, [headroom[k] for k in order], color="#8fc1e8",
       bottom=[committed[k] - headroom[k] for k in order],
       label="of which online headroom")
ax.set_xticks(list(x))
ax.set_xticklabels([f"{k}\n{mw[k]} MW PEM" for k in order],
                   fontsize=7, fontweight="bold", rotation=20)
ax.set_ylabel("MW on the 100 shed hours of bo_C_r2#3",
              fontweight="bold")
ax.set_title("More PEM MW -> more thermal committed, headroom restored",
             fontsize=10, fontweight="bold")
ax.legend(fontsize=8, frameon=False)

ax = axes[1]
pair = t[t["high"] == "bo_C_r1#5"].iloc[0]
labels = ["Extra thermal\ndispatch", "Parent\nrenewables", "PEM slice\ngrid sales"]
shares = [pair["share_thermal"], pair["share_parent_ren"], pair["share_pem"]]
colors = ["#2b6cb0", "#a0a0a0", "#d33"]
ax.bar(labels, shares, color=colors)
ax.axhline(1.0, color="k", linestyle="--", linewidth=1)
ax.text(1.55, 1.03, "shed difference = 1.0", fontsize=8, fontweight="bold")
ax.axhline(0.0, color="k", linewidth=0.8)
ax.set_ylabel("Share of the 29,182 MWh shed difference",
              fontweight="bold")
ax.set_title("What covers the shed? (bo_C_r2#3 vs bo_C_r1#5)",
             fontsize=10, fontweight="bold")
for i, v in enumerate(shares):
    ax.text(i, v + (0.04 if v >= 0 else -0.10), f"{v:+.2f}",
            ha="center", fontsize=9, fontweight="bold")
ax.set_ylim(-1.0, 2.0)

for a in axes:
    for lab in a.get_xticklabels() + a.get_yticklabels():
        lab.set_fontweight("bold")

fig.suptitle("H1 (commitment headroom) is the mechanism: thermal, not the "
             "PEM slice, covers the shed", fontsize=11, fontweight="bold")
fig.tight_layout()
fig.savefig(HERE / "fig_h1_commitment.png", dpi=200)
print("wrote", HERE / "fig_h1_commitment.png")
