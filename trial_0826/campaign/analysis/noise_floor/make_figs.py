"""Prompt 40 figures (ALL output under analysis/noise_floor/figs/).
Bold axis labels AND bold tick values. Every plotted number is read from
part_a.json / part_c_regrade.csv and asserted against them before drawing."""
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import part_a  # noqa: E402
import pool  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
FIGS = os.path.join(HERE, "figs")
os.makedirs(FIGS, exist_ok=True)
INK, INK2, GRID = "#0b0b0b", "#52514e", "#e4e3df"
SERIES = {"P1": "#2a78d6", "P2": "#eb6834", "P3": "#1baf7a", "N1": "#eda100"}
MARK = {"P1": "o", "P2": "s", "P3": "^", "N1": "D"}
plt.rcParams.update({"font.size": 11, "axes.edgecolor": INK2, "axes.labelcolor": INK,
                     "xtick.color": INK2, "ytick.color": INK2, "axes.labelweight": "bold",
                     "figure.facecolor": "#fcfcfb", "axes.facecolor": "#fcfcfb"})


def bold_ticks(ax):
    for t in ax.get_xticklabels() + ax.get_yticklabels():
        t.set_fontweight("bold")


def fig_variogram(res):
    b = res["shed"]["bins"]
    N, hb, g = np.array(b["N"]), np.array(b["hbar"], float), np.array(b["gamma_ch"], float)
    # recompute and assert against part_a.json
    df, _ = pool.load_pool()
    vg = part_a.Variogram(df)
    N2, hb2, g2 = vg.point(df["load_shed_mwh"].to_numpy(float))
    assert np.allclose(N, N2) and np.allclose(g[N > 0], g2[N2 > 0], rtol=1e-12)
    nug = part_a.wls_intercept(N2, hb2, g2)
    assert np.isclose(nug, res["shed"]["nugget_var_point"], rtol=1e-12)
    pop = np.nonzero(N > 0)[0][:part_a.K]
    x, y, w = hb[pop], g[pop], N[pop]
    xm, ym = np.average(x, weights=w), np.average(y, weights=w)
    slope = np.sum(w * (x - xm) * (y - ym)) / np.sum(w * (x - xm) ** 2)

    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.4), gridspec_kw={"width_ratios": [1.25, 1]})
    hh = np.linspace(0, 0.14, 50)
    a1.plot(hh, (nug + slope * hh) / 1e6, color=SERIES["P1"], lw=2, label="pinned WLS line (bins 2–5)")
    pk = N > 0
    a1.scatter(hb[pk], g[pk] / 1e6, s=np.clip(N[pk] / 8, 40, 320), color=SERIES["P1"],
               edgecolor="#fcfcfb", linewidth=2, zorder=3, label="Cressie–Hawkins γ(h), area ∝ pairs")
    for xi, yi, ni in zip(hb[pk], g[pk], N[pk]):
        a1.annotate(f"{int(ni):,}", (xi, yi / 1e6), textcoords="offset points", xytext=(6, 6),
                    fontsize=9, fontweight="bold", color=INK2)
    reps = pd.DataFrame(res["replicates_h0"])
    rep_var = 0.5 * reps["abs_d_load"].to_numpy() ** 2
    a1.scatter(np.zeros(len(rep_var)), rep_var / 1e6, marker="x", s=60, color=SERIES["P2"], zorder=4,
               label=f"h = 0 replicate pairs (n = {len(rep_var)}), ½Δ²")
    a1.axhline(3000 ** 2 / 1e6, color=INK2, lw=1, ls="--")
    a1.text(0.0, 3000 ** 2 / 1e6, "  old floor² (3,000 MWh)", ha="left", va="bottom", fontsize=9,
            color=INK2, fontweight="bold")
    a1.axhline(0, color=INK2, lw=0.8)
    a1.set_xlabel("normalized design distance h")
    a1.set_ylabel("shed semivariance (10⁶ MWh²)")
    a1.set_xlim(-0.006, 0.145)
    a1.grid(color=GRID, lw=0.6)
    a1.set_ylim(-0.4, 10.2)
    a1.legend(frameon=False, fontsize=9, loc="lower right")
    bold_ticks(a1)

    bs_p = [res["shed"][k] for k in ("boot_var_p5", "boot_var_p50", "boot_var_p90")]
    bs = vg.boot(df["load_shed_mwh"].to_numpy(float))
    q = np.quantile(bs[np.isfinite(bs)], [0.05, 0.5, 0.9])
    assert np.allclose(q, bs_p, rtol=1e-12)
    a2.hist(bs / 1e6, bins=60, color=SERIES["P1"], edgecolor="#fcfcfb", linewidth=0.6)
    for v, lab in zip(q, ("p5", "p50", "p90")):
        a2.axvline(v / 1e6, color=INK, lw=1.2, ls=":" if lab != "p90" else "-")
        a2.text(v / 1e6, a2.get_ylim()[1] * 0.95, f" {lab}", fontsize=9, fontweight="bold", color=INK)
    a2.axvline(0, color=SERIES["P2"], lw=1.5)
    a2.set_xlabel("bootstrapped nugget variance (10⁶ MWh²)")
    a2.set_ylabel("resamples (of 2,000)")
    a2.set_title(f"{100 * res['shed']['boot_frac_nonpositive']:.1f}% ≤ 0 → p5 < 0 → ABSTAIN",
                 fontsize=11, fontweight="bold", color=INK)
    a2.grid(color=GRID, lw=0.6)
    bold_ticks(a2)
    fig.tight_layout()
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(FIGS, f"fig_a_shed_variogram.{ext}"), dpi=200)
    plt.close(fig)


def fig_regrade(rg, pc):
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2), sharey=True)
    for ax, col, title, key in ((axes[0], "gain_over_tau_old", "τ at shed floor 3,000 MWh (ledger)", None),
                                (axes[1], "gain_over_tau_300", "τ at shed floor 300 MWh", "tau_300")):
        for arm in ("P1", "P2", "P3", "N1"):
            d = rg[rg.arm == arm]
            tau = pc["arms"][arm]["tau_old_ledger"] if key is None else pc["arms"][arm][key]
            assert np.allclose(d["gain"] / tau, d[col], rtol=1e-12)
            ax.plot(d["round"], d[col], color=SERIES[arm], lw=2, marker=MARK[arm], ms=8,
                    markeredgecolor="#fcfcfb", markeredgewidth=1.5)
            last = d.iloc[-1]
            ax.annotate(arm, (last["round"], last[col]), textcoords="offset points", xytext=(8, 0),
                        va="center", fontsize=10, fontweight="bold", color=INK)
            stop = d[d["would_stop_old" if key is None else "would_stop_300"]]
            ax.scatter(stop["round"], stop[col], s=150, facecolor="none", edgecolor=INK, lw=1.4, zorder=4)
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
    fig.text(0.5, -0.02, "ringed = would stop (two consecutive gains < τ); P2/P3 r4 not yet graded",
             ha="center", fontsize=9, color=INK2, fontweight="bold")
    fig.tight_layout()
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(FIGS, f"fig_c_stop_regrade.{ext}"), dpi=200, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    res = json.load(open(os.path.join(HERE, "part_a.json")))
    fig_variogram(res)
    fig_regrade(pd.read_csv(os.path.join(HERE, "part_c_regrade.csv")),
                json.load(open(os.path.join(HERE, "part_c.json"))))
    print("figs written:", sorted(os.listdir(FIGS)))
