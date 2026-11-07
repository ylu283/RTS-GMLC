"""Build figs/ for the ERCOT wave-D location deck (prompt 59). No PCM, no CRC.

Run:  /opt/anaconda3/bin/python make_location_figs.py        (from analysis/pi_location/)
Out:  figs/oat_curves_ercot.png, figs/sprime_bars.png, figs/ancova_ercot.png, figs/ancova_ercot.csv

Inputs (read-only, all under analysis/pool/):
  pool_standings_levels.csv   per-site x level raw values (18 VRE rows per candidate)
  pool_wavedD_wide.csv        21 wave-D rows incl. nuclear gen 1 (rows 19-21)
  pool_standings.csv          S' per level, W p, status, global order, survivor flag
  pool_definitions.json       names, units (frozen f76d897)

Site colours are fixed ONCE here (SITE_COLORS) and reused by every figure; nuclear is
dashed black. Kay's standing rule: bold axis labels AND bold tick labels, tick labels >= 14 pt.

ANCOVA (slide 7): on the 18 VRE rows of each candidate, three nested OLS models
  model 0: y ~ 1 + MW + MW^2                   (2 slope df; residual df 15)
  model 1: model 0 + site intercepts           (+5 df;    residual df 10)
  model 2: model 1 + site x MW slopes          (+5 df;    residual df 5)
R2adj = 1 - (RSS/(n-p)) / (TSS/(n-1)). Only dR2adj is reported. NO F test: no ruler, no F.
"""

from __future__ import annotations

import json
import textwrap
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402

HERE = Path(__file__).resolve().parent
POOL = HERE.parent / "pool"
FIGS = HERE / "figs"
FIGS.mkdir(exist_ok=True)

# ---- fixed colours (6 WIND sites + nuclear), Okabe-Ito, reused on every figure -----------
SITE_ORDER = [163, 140, 146, 270, 110, 274]           # wave-D row order (slate rank 1..6)
SITE_COLORS = {
    163: "#E69F00",  # orange
    140: "#56B4E9",  # sky blue
    146: "#009E73",  # bluish green
    270: "#D55E00",  # vermillion
    110: "#CC79A7",  # reddish purple
    274: "#0072B2",  # blue
}
NUC_COLOR = "#000000"
FAMILY_COLORS = {"V": "#009E73", "E": "#0072B2", "R": "#D55E00", "N": "#CC79A7", "X": "#6B6B6B"}
LEVELS = ["L60", "L120", "L180"]
MW = {"L60": 60, "L120": 120, "L180": 180}

TICK = 14
LABEL = 15
TITLE = 16
LEGEND = 11

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "axes.labelweight": "bold",
    "axes.titleweight": "bold",
    "xtick.labelsize": TICK,
    "ytick.labelsize": TICK,
    "axes.labelsize": LABEL,
    "axes.titlesize": TITLE,
    "legend.fontsize": LEGEND,
})


def bold_ticks(ax):
    for lab in ax.get_xticklabels() + ax.get_yticklabels():
        lab.set_fontweight("bold")
        lab.set_fontsize(TICK)


# ---- data --------------------------------------------------------------------------------
defs = json.load(open(POOL / "pool_definitions.json"))["candidates"]
levels = pd.read_csv(POOL / "pool_standings_levels.csv")
wide = pd.read_csv(POOL / "pool_wavedD_wide.csv")
stand = pd.read_csv(POOL / "pool_standings.csv")
nuc = wide[wide["is_nuclear_design"] == True].set_index("level_id")  # noqa: E712

UNCORRECTED = {r.id for r in stand.itertuples() if isinstance(r.nuc_tag, str) and "UNCORRECTED" in r.nuc_tag}


def pivot(cid: str) -> pd.DataFrame:
    """6 sites x 3 levels raw values for one candidate (VRE rows only)."""
    sub = levels[levels["id"] == cid]
    return sub.pivot(index="site", columns="level_id", values="value")[LEVELS].loc[SITE_ORDER]


def label_of(cid: str) -> str:
    d = defs[cid]
    return f"{cid} {d['name']} [{d['unit']}]"


# ---- Fig 1: OAT curves, 2 x 3 panels -------------------------------------------------------
OAT_IDS = ["V1", "E1", "R4", "N1", "R2", "X1"]


def scale_for(cid: str, vals: np.ndarray):
    """Pick a unit scale so tick labels stay short."""
    m = np.nanmax(np.abs(vals))
    if m >= 1e9:
        return 1e9, "G"
    if m >= 1e6:
        return 1e6, "M"
    if m >= 1e4:
        return 1e3, "k"
    return 1.0, ""


def fig_oat():
    fig, axes = plt.subplots(2, 3, figsize=(20, 11))
    for ax, cid in zip(axes.ravel(), OAT_IDS):
        pv = pivot(cid)
        allvals = pv.values.copy()
        show_nuc = cid not in UNCORRECTED and cid in nuc.columns
        if show_nuc:
            allvals = np.concatenate([allvals.ravel(), nuc.loc[LEVELS, cid].values.astype(float)])
        div, pre = scale_for(cid, allvals)
        x = [MW[l] for l in LEVELS]
        for site in SITE_ORDER:
            ax.plot(x, pv.loc[site].values / div, marker="o", lw=2.2, ms=7,
                    color=SITE_COLORS[site], label=f"site {site}")
        if show_nuc:
            ax.plot(x, nuc.loc[LEVELS, cid].values.astype(float) / div, marker="s", ms=7, lw=2.0,
                    ls="--", color=NUC_COLOR, label="nuclear gen 1 (overlay)")
        leg_title = None if show_nuc else "nuclear omitted: cost UNCORRECTED"
        d = defs[cid]
        ax.set_title(f"{cid} {d['name']}", fontweight="bold")
        ax.set_xlabel("PEM size [MW]", fontweight="bold")
        ax.set_ylabel(f"{d['unit']}" + (f" (x{pre})" if pre else ""), fontweight="bold")
        ax.set_xticks(x)
        ax.grid(alpha=0.3)
        lo, hi = ax.get_ylim()
        ax.set_ylim(lo - 0.45 * (hi - lo), hi + 0.04 * (hi - lo))  # room for the legend below the curves
        ax.legend(loc="lower center", frameon=True, ncol=4, fontsize=10, title=leg_title,
                  title_fontsize=10, columnspacing=0.8, handlelength=1.6)
        bold_ticks(ax)
        # make sure the offset text (if any) is suppressed: we scaled by hand
        ax.ticklabel_format(axis="y", style="plain", useOffset=False)
    fig.suptitle("ERCOT wave D: raw value vs PEM MW, one line per site (identity v3, 18 VRE rows + nuclear overlay)",
                 fontsize=18, fontweight="bold", y=0.995)
    fig.tight_layout(rect=(0, 0, 1, 0.97))
    out = FIGS / "oat_curves_ercot.png"
    fig.savefig(out, dpi=160)
    plt.close(fig)
    print("wrote", out)


# ---- Fig 2: S' grouped bars for the 16 survivors, global order ---------------------------
def fig_sprime():
    surv = stand[stand["is_survivor"] == True].sort_values("global_order_rank")  # noqa: E712
    ids = surv["id"].tolist()
    n = len(ids)
    fig, ax = plt.subplots(figsize=(18, 7.5))
    width = 0.26
    alphas = {"L60": 0.45, "L120": 0.72, "L180": 1.0}
    xs = np.arange(n)
    for j, lev in enumerate(LEVELS):
        for i, r in enumerate(surv.itertuples()):
            ax.bar(xs[i] + (j - 1) * width, getattr(r, f"S_prime_{lev}"), width,
                   color=FAMILY_COLORS[r.family], alpha=alphas[lev], edgecolor="black", lw=0.6)
    ax.axhline(0.5, ls="--", color="black", lw=1.6)
    ax.text(-0.45, 0.5, "S' = 0.5 rule", va="bottom", ha="left", fontsize=12, fontweight="bold")
    ax.set_yscale("log")
    ax.set_xticks(xs)
    ax.set_xticklabels([r.id + "\n" + textwrap.fill(r.name, 13) for r in surv.itertuples()], rotation=0, fontsize=TICK)
    ax.set_ylabel("S' = between-site range / within-site size effect (log)", fontweight="bold")
    ax.set_xlabel("survivor candidates, global order left to right", fontweight="bold")
    ax.grid(axis="y", alpha=0.3, which="both")
    # legends: family colours + level shading
    fam_handles = [Patch(facecolor=FAMILY_COLORS[f], edgecolor="black", label=f"family {f}") for f in ["V", "E", "R", "N"]]
    lev_handles = [Patch(facecolor="#808080", alpha=alphas[l], edgecolor="black", label=f"{l} ({MW[l]} MW)") for l in LEVELS]
    leg1 = ax.legend(handles=fam_handles, loc="upper left", title="family", frameon=True)
    ax.add_artist(leg1)
    ax.legend(handles=lev_handles, loc="upper left", bbox_to_anchor=(0.13, 1.0), title="level", frameon=True)
    bold_ticks(ax)
    for lab in ax.get_xticklabels():
        lab.set_fontsize(11)
        lab.set_fontweight("bold")
    ax.set_title("S' at 60 / 120 / 180 MW for the 16 survivors; LOCATION-SENSITIVE iff S' >= 0.5 at 2 of 3 levels (base-free; ruler pending)",
                 fontweight="bold")
    fig.tight_layout()
    out = FIGS / "sprime_bars.png"
    fig.savefig(out, dpi=160)
    plt.close(fig)
    print("wrote", out)


# ---- Fig 3: ANCOVA increments (R2adj of 3 nested models on 18 VRE rows) ------------------
def r2adj(y: np.ndarray, X: np.ndarray) -> tuple[float, int]:
    n, p = X.shape
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    rss = float(np.sum((y - X @ beta) ** 2))
    tss = float(np.sum((y - y.mean()) ** 2))
    if tss == 0:
        return float("nan"), n - p
    return 1.0 - (rss / (n - p)) / (tss / (n - 1)), n - p


def ancova_table() -> pd.DataFrame:
    rows = []
    for cid in OAT_IDS:
        sub = levels[levels["id"] == cid].copy()
        sub = sub.sort_values(["site", "pem_mw"])
        y = sub["value"].values.astype(float)
        mw = sub["pem_mw"].values.astype(float)
        mwc = (mw - 120.0) / 60.0  # centred, scaled: -1, 0, +1
        sites = sub["site"].values
        site_levels = SITE_ORDER
        D = np.column_stack([(sites == s).astype(float) for s in site_levels[1:]])  # 5 dummies (ref = 163)
        X0 = np.column_stack([np.ones_like(mwc), mwc, mwc ** 2])
        X1 = np.column_stack([X0, D])
        X2 = np.column_stack([X1, D * mwc[:, None]])
        r0, df0 = r2adj(y, X0)
        r1, df1 = r2adj(y, X1)
        r2, df2 = r2adj(y, X2)
        d1, d2 = r1 - r0, r2 - r1
        # reading rule (stated on the slide): threshold 0.10 on dR2adj
        if max(r0, r1, r2) < 0.30:
            read = "no fit"          # neither MW nor site explains the 18 rows (R2adj < 0.3 at every model)
        elif d1 < 0.10 and d2 < 0.10:
            read = "mostly size"
        elif d2 >= d1 and d2 >= 0.10:
            read = "slopes differ"
        else:
            read = "level shift"
        rows.append(dict(id=cid, name=defs[cid]["name"], unit=defs[cid]["unit"], n=len(y),
                         R2adj_m0_quadratic_MW=r0, dR2adj_m1_site_intercepts=d1, dR2adj_m2_site_x_MW=d2,
                         R2adj_m2_total=r2, resid_df_m0=df0, resid_df_m1=df1, resid_df_m2=df2, reading=read))
    return pd.DataFrame(rows)


def fig_ancova(tab: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(14, 7.8))
    xs = np.arange(len(tab))
    base = tab["R2adj_m0_quadratic_MW"].values
    d1 = tab["dR2adj_m1_site_intercepts"].values
    d2 = tab["dR2adj_m2_site_x_MW"].values
    c0, c1, c2 = "#9DB4C8", "#0072B2", "#E69F00"
    ax.bar(xs, base, 0.6, color=c0, edgecolor="black", lw=0.6, label="model 0: quadratic in MW (2 df)")
    # stack increments; negative increments drawn downward from the running top
    top = base.copy()
    for i in range(len(tab)):
        b = top[i] if d1[i] >= 0 else top[i] + d1[i]
        ax.bar(xs[i], abs(d1[i]), 0.6, bottom=b, color=c1, edgecolor="black", lw=0.6,
               hatch="" if d1[i] >= 0 else "//", label="+ site intercepts (5 df)" if i == 0 else None)
        top[i] += d1[i]
    for i in range(len(tab)):
        b = top[i] if d2[i] >= 0 else top[i] + d2[i]
        ax.bar(xs[i], abs(d2[i]), 0.6, bottom=b, color=c2, edgecolor="black", lw=0.6,
               hatch="" if d2[i] >= 0 else "//", label="+ site x MW slopes (5 df; resid. df 5)" if i == 0 else None)
        top[i] += d2[i]
    for i, r in enumerate(tab.itertuples()):
        ax.text(xs[i], max(top[i], base[i], 0) + 0.02, f"{r.reading}\nR²adj₂ = {r.R2adj_m2_total:.2f}",
                ha="center", va="bottom", fontsize=11, fontweight="bold")
    ax.axhline(0, color="black", lw=1)
    ax.set_xticks(xs)
    ax.set_xticklabels([f"{r.id}\n{r.name}" for r in tab.itertuples()])
    ax.set_ylabel("R²adj (model 0) and ΔR²adj increments", fontweight="bold")
    ax.set_xlabel("candidate (18 VRE rows each; hatched = negative increment)", fontweight="bold")
    ax.set_ylim(min(-0.25, float(np.nanmin(np.minimum(base, 0))) - 0.1), 1.25)
    ax.grid(axis="y", alpha=0.3)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.17), ncol=3, frameon=True)
    bold_ticks(ax)
    for lab in ax.get_xticklabels():
        lab.set_fontsize(12)
        lab.set_fontweight("bold")
    ax.set_title("Variance explained beyond PEM MW: site intercepts, then site x MW (no ruler, no F)", fontweight="bold")
    fig.tight_layout()
    out = FIGS / "ancova_ercot.png"
    fig.savefig(out, dpi=160)
    plt.close(fig)
    print("wrote", out)


if __name__ == "__main__":
    fig_oat()
    fig_sprime()
    tab = ancova_table()
    tab.to_csv(FIGS / "ancova_ercot.csv", index=False)
    print(tab.to_string())
    fig_ancova(tab)
