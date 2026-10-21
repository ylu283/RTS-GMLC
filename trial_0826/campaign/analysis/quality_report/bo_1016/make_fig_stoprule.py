"""fig_stoprule_closed.png — P1 HV trajectory + per-round gain/tau, official ledger numbers.

Run:  /opt/anaconda3/envs/bogp-botorch/bin/python make_fig_stoprule.py
Data: analysis/methods_C/P1/ledger.json (graded on CRC; r4 = a8df435).
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
AN = HERE.parent.parent
led = json.load(open(AN / "methods_C/P1/ledger.json"))
tau = led["threshold"]
E = led["entries"]

n = [e["n"] for e in E]
hv = [e["hv"] / 1e17 for e in E]
gains = [(e["round"], e["gain"] / tau) for e in E if e["gain"] is not None]

NAVY = "#0C2340"
GOLD = "#AE9342"
RED = "#C0392B"
GRAY = "#8A8A8A"

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.0, 3.6), dpi=200)

# --- panel A: HV trajectory ---
ax1.plot(n[:3], hv[:3], "-o", color=NAVY, lw=2.2, ms=7, zorder=3, label="live campaign")
ax1.plot(n[2:], hv[2:], "--o", color=GRAY, lw=2.0, ms=7, zorder=2, label="overrun (record only)")
ax1.axvline(n[2], color=RED, lw=1.4, ls=":")
ax1.annotate("LIVE STOP (r2)", xy=(n[2], hv[0] + 0.12), color=RED, fontsize=10,
             fontweight="bold", ha="center",
             xytext=(n[2], hv[0] - 0.05))
for e in E:
    if e["gain"] is not None:
        ax1.annotate(f"{e['gain'] / tau:.2f}τ", xy=(e["n"], e["hv"] / 1e17),
                     xytext=(0, 9), textcoords="offset points", ha="center",
                     fontsize=9.5, fontweight="bold",
                     color=NAVY if e["round"] <= 2 else GRAY)
ax1.set_xlabel("Evaluations n", fontweight="bold", fontsize=12)
ax1.set_ylabel("Hypervolume ($\\times 10^{17}$)", fontweight="bold", fontsize=12)
ax1.set_xticks(n)
ax1.legend(frameon=False, fontsize=10, loc="lower right")
ax1.set_title("P1 hypervolume trajectory", fontweight="bold", fontsize=13)

# --- panel B: gain / tau per round ---
rounds = [f"r{r}" for r, _ in gains]
vals = [g for _, g in gains]
colors = [NAVY, NAVY, GRAY, GRAY]
bars = ax2.bar(rounds, vals, color=colors, width=0.62)
for b in bars[2:]:
    b.set_hatch("//")
    b.set_edgecolor("white")
ax2.axhline(1.0, color=RED, lw=1.6, ls="--")
ax2.annotate("stop threshold τ", xy=(0.02, 1.0), xycoords=("axes fraction", "data"),
             xytext=(0, 4), textcoords="offset points", color=RED, fontsize=10,
             fontweight="bold")
for b, v in zip(bars, vals):
    ax2.annotate(f"{v:.2f}", xy=(b.get_x() + b.get_width() / 2, v),
                 xytext=(0, 3), textcoords="offset points", ha="center",
                 fontsize=10, fontweight="bold")
ax2.set_ylim(0, 1.55)
ax2.set_xlabel("BO round", fontweight="bold", fontsize=12)
ax2.set_ylabel("HV gain / τ", fontweight="bold", fontsize=12)
ax2.set_title("Both overrun rounds fall below τ", fontweight="bold", fontsize=13)

for ax in (ax1, ax2):
    for lab in ax.get_xticklabels() + ax.get_yticklabels():
        lab.set_fontweight("bold")
    ax.spines[["top", "right"]].set_visible(False)

fig.tight_layout()
for ext in ("png", "pdf"):
    fig.savefig(HERE / f"fig_stoprule_closed.{ext}", bbox_inches="tight")
print("wrote fig_stoprule_closed.png/.pdf")
