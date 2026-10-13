"""Prompt 37 T2 — tables and figures from summary/trajectories*.json and
summary/stops*.csv (collector output). Every figure has bold axes.
Functions return DataFrames; the notebook prints them and writes CSVs.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from scipy import stats  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import rules  # noqa: E402

SUMMARY, FIGS, TABLES = HERE / "summary", HERE / "figs", HERE / "tables"
E_PATHS = [f"E-path-{i}" for i in range(1, 6)]

plt.rcParams.update({
    "font.weight": "bold", "axes.labelweight": "bold", "axes.titleweight": "bold",
    "axes.linewidth": 1.6, "xtick.major.width": 1.4, "ytick.major.width": 1.4,
    "font.size": 10, "savefig.dpi": 200, "savefig.bbox": "tight",
})


def bold_ticks(ax):
    for t in ax.get_xticklabels() + ax.get_yticklabels():
        t.set_fontweight("bold")


def save(fig, name):
    FIGS.mkdir(exist_ok=True)
    for ext in ("png", "pdf"):
        fig.savefig(FIGS / f"{name}.{ext}")
    plt.close(fig)


def load(tag: str = ""):
    traj = json.loads((SUMMARY / f"trajectories{tag}.json").read_text())
    stops = pd.read_csv(SUMMARY / f"stops{tag}.csv.gz")
    return traj, stops


def tab(df: pd.DataFrame, name: str) -> pd.DataFrame:
    TABLES.mkdir(exist_ok=True)
    df.to_csv(TABLES / f"{name}.csv", index=False)
    return df


# --------------------------------------------------------------------------- #
# method comparison at fixed budget
# --------------------------------------------------------------------------- #
def fixed_budget(traj: list[dict], box: str = "frozen") -> pd.DataFrame:
    rows = []
    for t in traj:
        b = t[box]
        Ht, Hs, tau = np.asarray(b["H_true"]), b["H_star"], b["tau"]
        for k in range(len(Ht)):
            rows.append({"cell": t["cell"], "problem": t["problem"], "method": t["method"],
                         "seed": t["seed"], "round": k, "n": t["n0"] + k * t["q"],
                         "H_ratio": Ht[k] / Hs, "regret_tau": (Hs - Ht[k]) / tau})
    return pd.DataFrame(rows)


def method_table(fb: pd.DataFrame, ns: list[int]) -> pd.DataFrame:
    d = fb[fb["n"].isin(ns)]
    g = d.groupby(["cell", "n", "method"])["H_ratio"]
    out = g.median().unstack("method").add_prefix("med_")
    q25 = g.quantile(0.25).unstack("method").add_prefix("q25_")
    q75 = g.quantile(0.75).unstack("method").add_prefix("q75_")
    out = pd.concat([out, q25, q75], axis=1).reset_index()
    # paired differences in tau units (same seed = same starts / noise)
    p = d.pivot_table(index=["cell", "n", "seed"], columns="method", values="regret_tau")
    for a, b in (("M1", "M3"), ("M1", "M4"), ("M3", "M4")):
        if a in p and b in p:
            diff = (p[b] - p[a]).groupby(level=["cell", "n"]).median()  # >0: a better
            out = out.merge(diff.rename(f"med_paired_regret_{b}_minus_{a}_tau").reset_index(),
                            on=["cell", "n"], how="left")
    return out


def fig_method(fb: pd.DataFrame, cells: list[str], ns: list[int], name: str, ncol: int = 5):
    methods = [m for m in ("M1", "M3", "M4") if m in fb["method"].unique()]
    colors = {"M1": "#1f5fa8", "M3": "#c2410c", "M4": "#6b7280"}
    nrow = int(np.ceil(len(cells) / ncol))
    fig, axes = plt.subplots(nrow, ncol, figsize=(3.0 * ncol, 2.6 * nrow), squeeze=False)
    for ax, c in zip(axes.flat, cells):
        d = fb[fb["cell"] == c]
        for m in methods:
            dm = d[d["method"] == m]
            piv = dm.pivot_table(index="seed", columns="n", values="H_ratio")
            for _, row in piv.iterrows():
                ax.plot(piv.columns, row.values, color=colors[m], alpha=0.12, lw=0.8)
            ax.plot(piv.columns, piv.median(), color=colors[m], lw=2.4, label=m)
        for n in ns:
            ax.axvline(n, color="k", ls=":", lw=1)
        ax.set_title(c.replace("R-PG__pairgrid_", "PG:").replace("_C", ""), fontsize=9)
        ax.set_xlabel("evaluations n")
        ax.set_ylabel("H_true / H*")
        bold_ticks(ax)
    for ax in list(axes.flat)[len(cells):]:
        ax.axis("off")
    axes.flat[0].legend(frameon=False, prop={"weight": "bold"})
    fig.tight_layout()
    save(fig, name)


# --------------------------------------------------------------------------- #
# operating characteristic
# --------------------------------------------------------------------------- #
def oc_table(stops: pd.DataFrame, box: str = "frozen") -> pd.DataFrame:
    s = stops[stops["box"] == box].copy()
    s["variant"] = s.apply(_variant, axis=1)
    g = s.groupby(["cell", "method", "variant"])
    out = g.agg(n_runs=("stop", "size"), mean_stop=("stop", "mean"),
                share_stop_r2=("stop", lambda x: float(np.mean(x == 2))),
                early=("early", "mean"), cap=("cap", "mean"), late=("late", "mean"),
                mean_wasted=("wasted", "mean"),
                med_regret_budget_tau=("regret_budget_tau", "median"),
                med_regret_star=("regret_star", "median"),
                mean_evals=("evals", "mean"),
                med_density=("density_at_stop", "median")).reset_index()
    return out


def _variant(r) -> str:
    if r["rule"] == "S0":
        unit = "τ" if r["tau_kind"] == "mult" else "%H0"
        val = r["tau_val"] if r["tau_kind"] == "mult" else 100 * r["tau_val"]
        return f"S0 {val:g}{unit} w{int(r['w'])} K{int(r['K'])}"
    if r["rule"] == "S-rel":
        return f"S-rel {100 * r['c']:g}% K{int(r['K'])}"
    if r["rule"] == "S-model":
        return f"S-model w{int(r['w'])} K{int(r['K'])}"
    if r["rule"] == "S-OCD":
        return f"S-OCD K{int(r['K'])}"
    if r["rule"] == "S-fix":
        return f"S-fix-{int(r['k'])}"
    return r["rule"]


PRIMARY_VARIANT = "S0 1τ w2 K4"


def primary_endpoints(stops: pd.DataFrame) -> dict:
    s = stops[(stops["box"] == "frozen") & stops["problem"].isin(E_PATHS)
              & (stops["noise"] == 1.0) & (stops["q"] == 8) & (stops["method"] == "M1")].copy()
    s["variant"] = s.apply(_variant, axis=1)
    p = s[s["variant"] == PRIMARY_VARIANT]
    early = rules.bootstrap_ci(p["early"].astype(float).values, np.mean, groups=p["problem"].values)
    reg = rules.bootstrap_ci(p["regret_budget_tau"].values, np.median, groups=p["problem"].values)
    line = fix_line(s)
    on_below = bool(np.median(p["regret_budget_tau"]) <= np.interp(p["stop"].mean(), *line) + 1e-12)
    return {"n_runs": int(len(p)), "early": early, "median_regret_tau": reg,
            "mean_stop": float(p["stop"].mean()), "share_r2": float(np.mean(p["stop"] == 2)),
            "fix_line": [list(map(float, line[0])), list(map(float, line[1]))],
            "on_or_below_fix_line": on_below,
            "accept_primary": bool(early[0] <= 0.20 and reg[0] <= 1.0 and on_below)}


def fix_line(s: pd.DataFrame):
    f = s[s["rule"] == "S-fix"].groupby("k")["regret_budget_tau"].median()
    return f.index.values.astype(float), f.values


# --------------------------------------------------------------------------- #
# gain-noise null, Stage-2 conditional check, calibration, density
# --------------------------------------------------------------------------- #
def gain_null(traj: list[dict]) -> pd.DataFrame:
    rows = []
    for t in traj:
        b = t["frozen"]
        go, gt, tau = np.diff(b["H_obs"]), np.diff(b["H_true"]), b["tau"]
        for k in range(len(go)):
            rows.append({"cell": t["cell"], "method": t["method"], "seed": t["seed"], "round": k + 1,
                         "obs_gain_tau": go[k] / tau, "true_gain_tau": gt[k] / tau, "tau": tau})
    return pd.DataFrame(rows)


def stage2_conditional(traj: list[dict], wide: bool = False) -> pd.DataFrame:
    lo1, hi1, lo2, hi2 = (0.025, 0.10, 0.0, 0.04) if wide else (0.035, 0.075, 0.005, 0.025)
    rows = []
    for t in traj:
        if t["method"] != "M1" or t["noise"] != 1.0 or t["q"] != 8 or t["problem"].startswith("R-"):
            continue
        b = t["frozen"]
        Ho, Ht, tau = np.asarray(b["H_obs"]), np.asarray(b["H_true"]), b["tau"]
        g1, g2 = (Ho[1] - Ho[0]) / Ho[0], (Ho[2] - Ho[1]) / Ho[0]
        if lo1 <= g1 <= hi1 and lo2 <= g2 <= hi2:
            rows.append({"problem": t["problem"], "seed": t["seed"], "g1_pct": 100 * g1,
                         "g2_pct": 100 * g2, "rem2_tau": (Ht[4] - Ht[2]) / tau,
                         "rem6_tau": (Ht[8] - Ht[2]) / tau,
                         "rem2_pctH0": 100 * (Ht[4] - Ht[2]) / Ht[0],
                         "rem6_pctH0": 100 * (Ht[8] - Ht[2]) / Ht[0]})
    return pd.DataFrame(rows)


def calibration_vs_error(traj: list[dict]) -> pd.DataFrame:
    rows = []
    for t in traj:
        if "audit_rms" not in t:
            continue
        tau, Ht = t["frozen"]["tau"], np.asarray(t["frozen"]["H_true"])
        Hp = t["H_pred"]   # Hp[k-1] = prediction of H_k (fit on rounds < k)
        for k in range(1, len(Hp)):           # audit of round k -> shortfall of round k+1
            rms = np.asarray(t["audit_rms"][k - 1])
            rows.append({"cell": t["cell"], "problem": t["problem"], "method": t["method"],
                         "seed": t["seed"], "round": k,
                         "audit_dev": float(np.max(np.abs(np.log(rms)))),
                         "audit_fail": not all(t["audit_ok"][k - 1]),
                         "abs_shortfall_tau": abs(Hp[k] - Ht[k + 1]) / tau})
    return pd.DataFrame(rows)


def spearman_strata(cv: pd.DataFrame) -> pd.DataFrame:
    out = []
    for (p, r), d in cv.groupby(["problem", "round"]):
        if len(d) >= 8 and d["audit_dev"].nunique() > 1:
            rho = stats.spearmanr(d["audit_dev"], d["abs_shortfall_tau"]).statistic
            rb = (stats.spearmanr(d["audit_fail"].astype(int), d["abs_shortfall_tau"]).statistic
                  if d["audit_fail"].nunique() > 1 else np.nan)
            out.append({"problem": p, "round": r, "n": len(d), "rho_dev": rho, "rho_fail": rb,
                        "share_fail": d["audit_fail"].mean()})
    return pd.DataFrame(out)


# --------------------------------------------------------------------------- #
# key figure
# --------------------------------------------------------------------------- #
def key_figure(stops: pd.DataFrame, cells: list[str], name: str = "fig_key"):
    s = stops[stops["box"] == "frozen"].copy()
    s["variant"] = s.apply(_variant, axis=1)
    fig, axes = plt.subplots(1, len(cells), figsize=(4.0 * len(cells), 3.6), squeeze=False)
    for ax, c in zip(axes.flat, cells):
        d = s[s["cell"].isin([c] if c != "E-path" else E_PATHS) & (s["method"] == "M1")]
        fx = d[d["rule"] == "S-fix"].groupby("evals")["regret_budget_tau"]
        ax.plot(fx.median().index, fx.median().values, "k-", lw=2, label="S-fix-k")
        ax.fill_between(fx.median().index, fx.quantile(0.25).values, fx.quantile(0.75).values,
                        color="k", alpha=0.12)
        orc = d[d["rule"] == "Oracle"]
        ax.plot(orc["evals"].median(), orc["regret_budget_tau"].median(), "k*", ms=12, label="oracle")
        marks = {"S0 0.5τ w2 K4": ("#1f5fa8", "o"), PRIMARY_VARIANT: ("#1f5fa8", "s"),
                 "S0 2τ w2 K4": ("#1f5fa8", "^"), "S-rel 2% K4": ("#15803d", "D"),
                 "S-OCD K4": ("#7c3aed", "v"), "S-model w2 K4": ("#c2410c", "P")}
        for v, (col, mk) in marks.items():
            dv = d[d["variant"] == v]
            if dv.empty:
                continue
            x, y = dv["evals"], dv["regret_budget_tau"]
            ax.errorbar(x.median(), y.median(),
                        xerr=[[x.median() - x.quantile(0.25)], [x.quantile(0.75) - x.median()]],
                        yerr=[[y.median() - y.quantile(0.25)], [y.quantile(0.75) - y.median()]],
                        fmt=mk, color=col, ms=7, capsize=3, label=v)
        ax.set_xlabel("evaluations used (BO rounds × q)")
        ax.set_ylabel("(H_8 − H_stop) / τ_j")
        ax.set_title(c)
        bold_ticks(ax)
        ins = ax.inset_axes([0.6, 0.55, 0.37, 0.4])
        p0 = d[d["variant"] == PRIMARY_VARIANT]["stop"]
        ins.hist(p0, bins=np.arange(0.5, 9.5, 1), color="#1f5fa8")
        ins.set_title("S0 stop round", fontsize=7)
        ins.tick_params(labelsize=6)
    axes.flat[0].legend(fontsize=6, frameon=False, loc="lower left")
    fig.tight_layout()
    save(fig, name)
