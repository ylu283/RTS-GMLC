"""Build figs/ for the ERCOT objective-selection deck (prompt 64). Zero simulation.

Run:  /opt/anaconda3/bin/python make_objective_figs.py        (from analysis/pi_objectives/)
Out:  figs/fig_envelope_total_mw.png   (slide 4)  wave D vs n0_E total PEM MW per row
      figs/fig_hero_idr_over_bar.png   (slide 7)  IDR / bar per candidate, perturbed vs Seed bar
      figs/fig_relief_vs_total_mw.png  (slide 10) V1 relief vs total MW (P1 joints, ΣOAT, P2, P3, pool)
      figs/eq_seat_rules.png           (slide 5)  the frozen n0_E rules in math font (mathtext)

Kay's standing rule: bold axis labels AND bold tick values (rcParams + bold_ticks on every axis).
Assert-before-draw: every plotted array is re-read from its source cell and compared before plotting.
Numbers come from objective_facts.py (which reads the source files; see its docstring).
"""

from __future__ import annotations

import math

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

import objective_facts as F  # noqa: E402

FIGS = F.HERE / "figs"
FIGS.mkdir(exist_ok=True)

TICK, LABEL, TITLE, LEGEND = 14, 15, 15, 11
plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.weight": "bold",
    "axes.labelweight": "bold",
    "axes.titleweight": "bold",
    "xtick.labelsize": TICK,
    "ytick.labelsize": TICK,
    "axes.labelsize": LABEL,
    "axes.titlesize": TITLE,
    "legend.fontsize": LEGEND,
    "mathtext.fontset": "cm",
})
FAMILY_COLORS = {"V": "#009E73", "E": "#0072B2", "X": "#6B6B6B", "R": "#D55E00", "N": "#CC79A7", "D": "#999999"}
GREY = "#BBBBBB"


def bold_ticks(ax):
    for lab in ax.get_xticklabels() + ax.get_yticklabels():
        lab.set_fontweight("bold")
        lab.set_fontsize(TICK)


# =============================================================================
# slide 4: total PEM MW per row, wave D vs n0_E
# =============================================================================
def fig_envelope():
    dmD, dm0 = F.dmD, F.dm0
    wind = dmD[dmD.unit_type == "WIND"]["pem_mw"].to_numpy(float)
    nuc = dmD[dmD.unit_type == "NUC"]["pem_mw"].to_numpy(float)
    n0 = dm0["pem_mw"].to_numpy(float)
    # assert before draw
    assert len(wind) == 18 and len(nuc) == 3 and len(n0) == F.N_N0E
    assert np.allclose(np.sort(n0), np.sort(F.dm0[F.N0_MW_COLS].sum(axis=1).to_numpy()))
    assert abs(n0.min() - F.N0_MIN) < 1e-9 and abs(n0.max() - F.N0_MAX) < 1e-9
    assert set(wind) == {60.0, 120.0, 180.0} and set(nuc) == {60.0, 120.0, 180.0}

    fig, ax = plt.subplots(figsize=(11, 4.6))
    rng = np.random.default_rng(64)
    yD, y0 = 1.0, 0.0
    # wave D: 6 WIND rows at each level stacked vertically so all 18 are visible
    for lv in (60.0, 120.0, 180.0):
        k = int((wind == lv).sum())
        ax.scatter(np.full(k, lv), yD + np.linspace(-0.18, 0.18, k), s=70, color="#0072B2", edgecolor="k", zorder=3,
                   label="wave D, WIND site (1 site per row)" if lv == 60.0 else None)
    ax.scatter(nuc, np.full(3, yD + 0.3), s=90, marker="D", color="white", edgecolor="k", zorder=3,
               label="wave D, nuclear gen 1 (overlay)")
    ax.scatter(n0, y0 + rng.uniform(-0.2, 0.2, len(n0)), s=70, color="#D55E00", edgecolor="k", zorder=3,
               label=f"n0_E Sobol design (6 sites per row)")
    ax.axvspan(n0.min(), n0.max(), ymin=0.05, ymax=0.45, color="#D55E00", alpha=0.10, zorder=1)
    ax.axvspan(0, 180, ymin=0.55, ymax=0.95, color="#0072B2", alpha=0.10, zorder=1)
    ax.text(n0.min(), -0.42, f"{n0.min():,.1f} MW", ha="center", fontsize=12, fontweight="bold")
    ax.text(n0.max(), -0.42, f"{n0.max():,.1f} MW", ha="center", fontsize=12, fontweight="bold")
    ax.text(180, 1.47, "180 MW", ha="center", fontsize=12, fontweight="bold")
    ax.set_yticks([y0, yD])
    ax.set_yticklabels([f"n0_E\n({len(n0)} rows)", f"wave D\n({len(wind) + len(nuc)} rows)"])
    ax.set_ylim(-0.55, 1.6)
    ax.set_xlim(0, 2000)
    ax.set_xlabel("total PEM MW in the run")
    ax.grid(axis="x", alpha=0.3)
    ax.legend(loc="upper right", frameon=True)
    bold_ticks(ax)
    fig.tight_layout()
    out = FIGS / "fig_envelope_total_mw.png"
    fig.savefig(out, dpi=200)
    plt.close(fig)
    return out


# =============================================================================
# slide 7: hero, IDR / bar on a log axis
# =============================================================================
NAMED = ["V1", "E1", "R4", "N1", "N4"]
SO = {"V1": (10, -14, "left"), "N1": (10, -14, "left")}   # Seed-label offsets (render overlap fixes)


def fig_hero():
    n0, seed = F.n0, F.seed
    order = n0.sort_values("global_order").index.tolist()
    fig, ax = plt.subplots(figsize=(13, 5.6))
    xs = np.arange(len(order))
    for i, j in enumerate(order):
        r = n0.loc[j]
        dead = r["respond_label"].startswith("DEAD") or r["respond_label"].startswith("READABLE (RULER=0)")
        undirected = r["dir"] not in ("min", "max")
        grey = dead or undirected
        col = GREY if grey else FAMILY_COLORS[r["family"]]
        if j == "E9":   # seedbar re-grade: B_seed 1.342, IDR 0 -> NOT RESPONDS (0 cannot sit on a log axis)
            assert F.sb.loc[j, "IDR_over_B"] == 0 and F.sb.loc[j, "status"] == "DIAGNOSTIC"
            ax.text(i, 0.13, "0 (Seed)", ha="center", va="bottom", fontsize=10, color="#888888", fontweight="bold", rotation=90)
            continue
        if dead or not (r["B_j"] > 0):
            ax.text(i, 0.13, "n/a", ha="center", va="bottom", fontsize=10, color="#888888", fontweight="bold", rotation=90)
            continue
        vp = r["IDR"] / r["B_j"]
        # assert before draw: the plotted value is the csv ratio column
        assert abs(vp - r["IDR_over_B"]) < 1e-9, j
        ax.scatter(i, vp, s=110, color=col, edgecolor="k", zorder=4)
        show_seed = (j in NAMED) or (seed.loc[j, "A3"] == "DISAGREE")
        if show_seed and seed.loc[j, "B_seed"] > 0:
            vs = F.sb.loc[j, "IDR_over_B_seed_sensitivity"]          # seedbar csv (62 re-grade)
            assert abs(vs - r["IDR"] / seed.loc[j, "B_seed"]) < 1e-9, j   # == IDR / B_seed (63 json)
            ax.scatter(i, vs, s=110, facecolor="white", edgecolor=col if not grey else "k", linewidth=2.2, zorder=5)
            ax.plot([i, i], [vp, vs], color=col, lw=1.5, zorder=3)
        if j in NAMED:
            po = {"R4": (-10, 2, "right")}.get(j, (8, 4, "left"))
            ax.annotate(f"{vp:.1f}", (i, vp), xytext=po[:2], textcoords="offset points", ha=po[2], fontsize=11, fontweight="bold")
            if seed.loc[j, "B_seed"] > 0:
                vs = r["IDR"] / seed.loc[j, "B_seed"]
                ax.annotate(f"{vs:.2f}" if j == "N1" else f"{vs:.1f}", (i, vs), xytext=SO.get(j, (-10, -5, "right"))[:2],
                            textcoords="offset points", ha=SO.get(j, (-10, -5, "right"))[2], fontsize=11, fontweight="bold", color="#444444")
    for y, ls, lab in [(2, "--", "2 = RESPONDS bar"), (3, ":", "3 = top of BORDERLINE [2, 3)"), (10, "-.", "10 = STRONG")]:
        ax.axhline(y, color="k", ls=ls, lw=1.3, zorder=2)
        ax.text(len(order) - 0.4, y * 1.08, lab, ha="right", fontsize=11, fontweight="bold")
    ax.axhspan(2, 3, color="#F0E442", alpha=0.25, zorder=1)
    ax.set_yscale("log")
    ax.set_ylim(0.1, 2000)
    ax.set_xticks(xs)
    ax.set_xticklabels(order, rotation=0)
    for lab, j in zip(ax.get_xticklabels(), order):
        r = n0.loc[j]
        if r["dir"] not in ("min", "max") or r["respond_label"].startswith(("DEAD", "READABLE (RULER=0)")):
            lab.set_color("#999999")
    ax.set_xlim(-0.7, len(order) - 0.3)
    ax.set_xlabel("candidate (pool global order; grey = dead, ruler-0 or undirected)")
    ax.set_ylabel("IDR / bar  (48 n0_E designs)")
    ax.grid(axis="y", which="both", alpha=0.25)
    from matplotlib.lines import Line2D
    h = [Line2D([], [], marker="o", ls="", ms=10, color=c, markeredgecolor="k", label=f"family {f}")
         for f, c in FAMILY_COLORS.items() if f != "D"]
    h += [Line2D([], [], marker="o", ls="", ms=10, color="#444444", markeredgecolor="k", label="filled = perturbed bar B_j"),
          Line2D([], [], marker="o", ls="", ms=10, markerfacecolor="white", markeredgecolor="k", markeredgewidth=2,
                 label="open = Seed bar B^seed")]
    ax.legend(handles=h, loc="upper center", ncol=7, fontsize=10, frameon=True, bbox_to_anchor=(0.5, 1.13))
    bold_ticks(ax)
    fig.tight_layout()
    out = FIGS / "fig_hero_idr_over_bar.png"
    fig.savefig(out, dpi=200)
    plt.close(fig)
    return out


# =============================================================================
# slide 10: V1 relief vs total MW
# =============================================================================
def fig_relief():
    lc = F.lc
    p1 = {m: (6 * m, -lc("delta", f"P1_{m}", "V1") / 1e6) for m in (60, 120, 180)}
    soat = {m: (6 * m, -lc("A", f"P1_{m}", "V1") / 1e6) for m in (60, 120, 180)}
    p2 = {it: (F.LC_PEM[it], -lc("delta", it, "V1") / 1e6)
          for it in ["P2_800_b120", "P2_800_b275", "P2_800_all", "P2_500_270", "P2_500_110_140"]}
    p3 = (F.LC_PEM["P3_1500_all"], -lc("delta", "P3_1500_all", "V1") / 1e6)
    # assert before draw
    for m in (60, 120, 180):
        assert abs(F.LC_PEM[f"P1_{m}"] - 6 * m) < 1e-6
        ssum = sum(-lc("delta", f"s{s}_L{m}", "V1") for s in (163, 140, 146, 270, 110, 274)) / 1e6
        assert abs(ssum - soat[m][1]) < 1e-9, m
        g = (soat[m][1] - p1[m][1]) / p1[m][1]   # g = (ΣR − R_J) / R_J (LOCATION_CONTRAST_E §3.1)
        assert abs(g - F.G[m]) < 1e-9, m
    assert abs(p3[1] - F.R9_TWH) < 1e-12

    fig, ax = plt.subplots(figsize=(9.5, 6.0))
    ax.plot([v[0] for v in soat.values()], [v[1] for v in soat.values()], "s--", color="#0072B2", ms=10, mec="k",
            label="Σ of six single-site OAT runs (wave D)")
    ax.plot([v[0] for v in p1.values()], [v[1] for v in p1.values()], "o-", color="#D55E00", ms=11, mec="k",
            label="P1: all six sites, joint")
    for m in (60, 120, 180):
        ax.annotate(f"g = {F.G[m]:.3f}", (p1[m][0], p1[m][1]), xytext=(10, -22), textcoords="offset points",
                    fontsize=12, fontweight="bold")
    mk = {"P2_800_b120": ("^", "#009E73", "P2 800 MW, bus-120 sites"), "P2_800_b275": ("v", "#CC79A7", "P2 800 MW, bus-2/75 sites"),
          "P2_800_all": ("P", "#E69F00", "P2 800 MW, all six pro-rata"), "P2_500_270": ("^", "#009E73", None),
          "P2_500_110_140": ("v", "#CC79A7", None)}
    for it, (xv, yv) in p2.items():
        m, c, lab = mk[it]
        ax.scatter(xv, yv, marker=m, s=130, color=c, edgecolor="k", zorder=5, label=lab)
    ax.scatter(*p3, marker="*", s=380, color="#F0E442", edgecolor="k", zorder=6, label="P3 1,500 MW, all six")
    ax.axhline(F.POOL_TWH, color="k", ls=":", lw=1.5)
    ax.text(150, F.POOL_TWH + 0.06, f"behind-cut curtailment pool {F.POOL_TWH:.2f} TWh (base_v3)", fontsize=11,
            fontweight="bold")
    ax.annotate(f"{F.R9_TWH:.2f} TWh = {100 * F.R9_SHARE:.0f} % of the pool", p3, xytext=(900, 4.45),
                textcoords="data", fontsize=11, fontweight="bold", arrowprops=dict(arrowstyle="->"))
    ax.set_xlim(0, 1650)
    ax.set_ylim(0, 5.4)
    ax.set_xlabel("total PEM MW (six slate sites)")
    ax.set_ylabel("V1 curtailment relief vs base_v3 (TWh)")
    ax.grid(alpha=0.3)
    ax.legend(loc="lower right", fontsize=10, frameon=True)
    bold_ticks(ax)
    fig.tight_layout()
    out = FIGS / "fig_relief_vs_total_mw.png"
    fig.savefig(out, dpi=200)
    plt.close(fig)
    return out


# =============================================================================
# slide 5: the frozen rules in math font
# =============================================================================
EQS = [
    r"$\mathrm{IDR}_j \;=\; Q_{90}(y_j) - Q_{10}(y_j)\ \ \mathrm{over\ 48\ designs}\;\; \geq\;\; 2\,B_j$",
    r"$p_{\mathrm{Mantel}}(|y_i-y_k|,\ \|u_i-u_k\|) \;\leq\; 0.01\qquad (9{,}999\ \mathrm{permutations})$",
    r"$1 - \frac{\hat\sigma_j^{\,2}/2}{\mathrm{Var}(y_j)} \;\geq\; 0.5\qquad \mathrm{(signal\ share)}$",
    r"$\mathrm{REDUNDANT}(a,b) \Leftrightarrow \rho^{\mathrm{raw}}_{\mathrm{or}} \geq 0.90 \;\wedge\; \rho^{\mathrm{resid}(T)}_{\mathrm{or}} \geq 0.50$",
    r"$B_j \;=\; \max(3\sqrt{\overline{\delta_j^{\,2}}},\ \max_i|\delta_{ij}|)\qquad \delta:\ \pm 0.1\,\%\ \mathrm{perturbed\ copies}$",
    r"$\mathrm{seat} \;=\; \mathrm{first\ eligible\ id\ in\ global\_order},\ \ \leq 1\ \mathrm{per\ family},\ \ M \leq 4\ \ (M<4\ \mathrm{allowed})$",
]


def fig_equations():
    fig = plt.figure(figsize=(12, 5.2))
    for i, e in enumerate(EQS):
        fig.text(0.02, 0.92 - i * 0.165, e, fontsize=21, va="top")
    out = FIGS / "eq_seat_rules.png"
    fig.savefig(out, dpi=200, bbox_inches="tight", pad_inches=0.08)
    plt.close(fig)
    return out


if __name__ == "__main__":
    for f in (fig_envelope, fig_hero, fig_relief, fig_equations):
        print("wrote", f())
