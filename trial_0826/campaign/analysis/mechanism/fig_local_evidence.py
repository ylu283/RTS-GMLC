#!/usr/bin/env python
"""Local evidence figure for prompt 38: load shed and reserve shortfall
vs total PEM MW over the 96 Stage-2 designs (H4 test + Q1 context).
All data from git wave summaries; no raw run files needed."""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from scipy.stats import spearmanr

HERE = Path(__file__).resolve().parent
WAVES = HERE.parents[1] / "waves"
FINISHED = ["stage2_C_n0", "stage2_C_n0b", "bo_C_r1", "bo_C_r2", "random_C"]

rows = []
for w in FINISHED:
    obj = pd.read_csv(WAVES / w / "objectives.csv")
    site = pd.read_csv(WAVES / w / "site_detail.csv")
    cap = site.groupby("index")["pem_capacity_mw"].sum().rename("total_pem_mw")
    rows.append(obj.merge(cap, on="index").assign(wave=w))
df = pd.concat(rows, ignore_index=True)

fig, axes = plt.subplots(1, 2, figsize=(10, 4.2), sharex=True)
specs = [
    ("load_shed_mwh", "Load shed (MWh/yr)", axes[0]),
    ("reserve_shortfall_mwh", "Reserve shortfall (MWh/yr)", axes[1]),
]
for col, ylab, ax in specs:
    rho, _ = spearmanr(df["total_pem_mw"], df[col])
    ax.scatter(df["total_pem_mw"], df[col], s=22, alpha=0.75,
               edgecolor="k", linewidth=0.4, color="#2b6cb0")
    q2 = df[(df["load_shed_mwh"] - 22.425956).abs() < 1e-3]
    ax.scatter(q2["total_pem_mw"], q2[col], s=40, color="#d33",
               edgecolor="k", linewidth=0.6, zorder=3,
               label="shed = 22.426 MWh (7 designs)")
    ax.set_xlabel("Total PEM capacity (MW)", fontweight="bold")
    ax.set_ylabel(ylab, fontweight="bold")
    ax.set_title(f"Spearman = {rho:+.3f}", fontweight="bold")
    for lab in ax.get_xticklabels() + ax.get_yticklabels():
        lab.set_fontweight("bold")
axes[0].legend(fontsize=8, frameon=False)
fig.suptitle("96 Stage-2 designs (scenario C): both penalties FALL with PEM MW"
             " — no shed-to-reserve substitution (H4 contradicted)",
             fontsize=10, fontweight="bold")
fig.tight_layout()
fig.savefig(HERE / "fig_shed_shortfall_vs_mw.png", dpi=200)
print("wrote", HERE / "fig_shed_shortfall_vs_mw.png")
