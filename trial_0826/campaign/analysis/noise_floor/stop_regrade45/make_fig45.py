"""Prompt 45 §3.5 figure: fig_tau_regrade45.png/.pdf.

Plotting code reused from analysis/noise_floor/make_figs.py::fig_regrade
(prompt 40; style, colors, markers, rings, bold ticks). Changed: the two
panels are tau_old (ledger) and tau(285.3) read from tau_regrade45.csv;
every plotted ratio is asserted against tau_regrade45.json (gain / tau)
before drawing. CI / inferred / heteroscedastic rows are a TABLE in
TAU_REGRADE45.md, not plotted.
"""
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
INK, INK2, GRID = "#0b0b0b", "#52514e", "#e4e3df"
SERIES = {"P1": "#2a78d6", "P2": "#eb6834", "P3": "#1baf7a", "N1": "#eda100"}
MARK = {"P1": "o", "P2": "s", "P3": "^", "N1": "D"}
plt.rcParams.update({"font.size": 11, "axes.edgecolor": INK2, "axes.labelcolor": INK,
                     "xtick.color": INK2, "ytick.color": INK2, "axes.labelweight": "bold",
                     "figure.facecolor": "#fcfcfb", "axes.facecolor": "#fcfcfb"})


def bold_ticks(ax):
    for t in ax.get_xticklabels() + ax.get_yticklabels():
        t.set_fontweight("bold")


def fig_regrade45(rg, res):
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2), sharey=True)
    for ax, key, title in ((axes[0], "old_3000", "τ_old: shed floor 3,000 MWh (ledger)"),
                           (axes[1], "scalar_285.3", "τ(285.3): measured pooled shed sd")):
        ends = {}
        for arm in ("P1", "P2", "P3", "N1"):
            d = rg[(rg.arm == arm) & (rg.tau_row == key)].sort_values("round")
            tau = res["arms"][arm]["tau"][key]
            assert np.allclose(d["gain"] / tau, d["gain_over_tau"], rtol=1e-12)
            assert list(d["would_stop"]) == res["arms"][arm]["would_stop"][key]
            ax.plot(d["round"], d["gain_over_tau"], color=SERIES[arm], lw=2, marker=MARK[arm], ms=8,
                    markeredgecolor="#fcfcfb", markeredgewidth=1.5)
            ends[arm] = float(d.iloc[-1]["gain_over_tau"])
            stop = d[d["would_stop"].astype(bool)]
            ax.scatter(stop["round"], stop["gain_over_tau"], s=150, facecolor="none", edgecolor=INK,
                       lw=1.4, zorder=4)
        # end-of-line arm labels, dodged apart in log space (>= 0.075 decades)
        order = sorted(ends, key=ends.get)
        ys = [np.log10(ends[a]) for a in order]
        for i in range(1, len(ys)):
            ys[i] = max(ys[i], ys[i - 1] + 0.075)
        shift = (np.mean([np.log10(ends[a]) for a in order]) - np.mean(ys))
        for a, y in zip(order, ys):
            ax.annotate(a, (4, ends[a]), xytext=(4.12, 10 ** (y + shift)), va="center", fontsize=10,
                        fontweight="bold", color=INK,
                        arrowprops=dict(arrowstyle="-", color=SERIES[a], lw=1))
        ax.axhline(1.0, color=INK2, lw=1.2, ls="--")
        ax.text(4.45, 1.0, "gain = τ", va="bottom", ha="right", fontsize=9, fontweight="bold", color=INK2)
        ax.set_yscale("log")
        ax.set_xticks([1, 2, 3, 4])
        ax.set_xlim(0.8, 4.5)
        ax.set_xlabel("BO round")
        ax.set_title(title, fontsize=11, fontweight="bold", color=INK)
        ax.grid(color=GRID, lw=0.6)
        bold_ticks(ax)
    axes[0].set_ylabel("round HV gain / τ (log)")
    fig.text(0.5, -0.02, "ringed = would stop (two consecutive gains < τ); all arms graded through r4 (cap); "
             "P1 and N1 share τ", ha="center", fontsize=9, color=INK2, fontweight="bold")
    fig.tight_layout()
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(HERE, f"fig_tau_regrade45.{ext}"), dpi=200, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    fig_regrade45(pd.read_csv(os.path.join(HERE, "tau_regrade45.csv")),
                  json.load(open(os.path.join(HERE, "tau_regrade45.json"))))
    print("written fig_tau_regrade45.png/.pdf")
