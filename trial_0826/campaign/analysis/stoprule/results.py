"""Prompt 50 — the truth-known analysis of the prompt-37 suite (PREREG §5,
§6, Amendment 1). Reads summary/ (CRC bot commit + local Block R), writes
tables/*.csv (frozen; figures are drawn from these CSVs after asserting
their shape) and figs/*, and prints the numbers STOPRULE_RESULTS.md quotes.

  BOGP_PATH=... PYTHONNOUSERSITE=1 python results.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import analysis as A  # noqa: E402
import rules  # noqa: E402
from analysis import E_PATHS, PRIMARY_VARIANT, bold_ticks, plt, save, tab  # noqa: E402

OUT: dict = {}
SIX_CELLS_C = ["E-mean", "E-short", "Z-needle", "Z-plateau", "Z-dis"]
REPLAY_SMOKE = ("R-C", 0)          # Amendment 1: R-C seed 0 = pre-PREREG smoke


def is_2d(p: pd.Series) -> pd.Series:
    return p.str.startswith("R-")


def with_variant(s: pd.DataFrame) -> pd.DataFrame:
    s = s.copy()
    s["variant"] = s.apply(A._variant, axis=1)
    return s


# --------------------------------------------------------------------------- #
# load + integrity
# --------------------------------------------------------------------------- #
def load_all():
    traj, stops = A.load()
    traj_r, stops_r = A.load("_R-")
    assert len(traj) == 1540 and len(stops) == 247_020, (len(traj), len(stops))
    assert len(traj_r) == 680 and len(stops_r) == 114_240
    # degenerate tau: Z-dis x union box only (prompt 50 §1)
    deg = stops[stops["tau_degenerate"]]
    assert set(deg["problem"]) == {"Z-dis"} and set(deg["box"]) == {"union"}
    assert not stops_r["tau_degenerate"].any()
    OUT["tau_degenerate"] = {
        "rows": int(len(deg)),
        "zdis_union_seeds": sorted(deg["seed"].unique().tolist()),
        "frozen_tau_min": min(t["frozen"]["tau"] for t in traj),
    }
    # S-model rows on 2-D runs come from the NaN ehvi array -> junk, excluded
    n_junk = int(((stops["rule"] == "S-model") & is_2d(stops["problem"])).sum())
    stops = stops[~((stops["rule"] == "S-model") & is_2d(stops["problem"]))]
    OUT["excluded_2d_smodel_rows"] = n_junk
    return traj, with_variant(stops), traj_r, with_variant(stops_r)


# --------------------------------------------------------------------------- #
# primary + Z-needle legs
# --------------------------------------------------------------------------- #
def primary(stops):
    pe = A.primary_endpoints(stops)
    assert pe["n_runs"] == 250, pe["n_runs"]
    pe["fix_interp_at_mean_stop"] = float(np.interp(pe["mean_stop"], *map(np.asarray, pe["fix_line"])))
    p = stops[(stops["box"] == "frozen") & stops["problem"].isin(E_PATHS) & (stops["noise"] == 1.0)
              & (stops["q"] == 8) & (stops["method"] == "M1") & (stops["variant"] == PRIMARY_VARIANT)]
    pe["cap_rate"] = float(p["cap"].mean())
    pe["late_rate"] = float(p["late"].mean())
    pe["late_net_rate"] = float(p["late_net"].mean())
    pe["median_regret_star"] = float(p["regret_star"].median())
    per_path = p.groupby("problem").agg(n=("stop", "size"), early=("early", "mean"),
                                        cap=("cap", "mean"), mean_stop=("stop", "mean"),
                                        med_regret_tau=("regret_budget_tau", "median")).reset_index()
    tab(per_path, "primary_per_path")
    OUT["primary"] = pe
    return p


def zneedle(traj, stops):
    z = stops[(stops["box"] == "frozen") & (stops["problem"] == "Z-needle") & (stops["method"] == "M1")]
    p = z[z["variant"] == PRIMARY_VARIANT]
    assert len(p) == 20, len(p)
    early = rules.bootstrap_ci(p["early"].values, np.mean)
    reg = rules.bootstrap_ci(p["regret_budget_tau"].values, np.median)
    f = z[z["rule"] == "S-fix"].groupby("k")["regret_budget_tau"].median()
    interp = float(np.interp(p["stop"].mean(), f.index.values.astype(float), f.values))
    gate = {}
    for m in ("M1", "M3"):
        tz = [t for t in traj if t["problem"] == "Z-needle" and t["method"] == m]
        assert len(tz) == 20
        gate[m] = {"share_found": float(np.mean([t["needle_round"] is not None for t in tz])),
                   "found_at_round0": int(sum(t["needle_round"] == 0 for t in tz)),
                   "rounds": [t["needle_round"] for t in tz]}
    informative = max(g["share_found"] for g in gate.values()) >= 0.25
    med = float(np.median(p["regret_budget_tau"]))
    OUT["zneedle"] = {"n_runs": 20, "early": early, "median_regret_tau": reg,
                      "mean_stop": float(p["stop"].mean()), "fix_line": f.to_dict(),
                      "fix_interp_at_mean_stop": interp, "on_or_below": bool(med <= interp + 1e-12),
                      "gate": gate, "informative": informative,
                      "accept": bool(early[0] <= 0.20 and reg[0] <= 1.0 and med <= interp + 1e-12)}


def named_readings(traj, stops, p):
    """PREREG §6 pre-registered readings, evaluated on the primary cell."""
    prim = [t for t in traj if t["problem"] in E_PATHS and t["noise"] == 1.0 and t["q"] == 8
            and t["method"] == "M1"]
    triv = np.mean([np.all(np.diff(t["frozen"]["H_true"]) < t["frozen"]["tau"]) for t in prim])
    fix2 = stops[(stops["box"] == "frozen") & stops["problem"].isin(E_PATHS) & (stops["noise"] == 1.0)
                 & (stops["q"] == 8) & (stops["method"] == "M1") & (stops["rule"] == "S0")
                 & (stops["tau_kind"] == "mult") & (stops["w"] == 2) & (stops["K"] == 4)]
    adapt = fix2.groupby("tau_val")["stop"].agg(share_r2=lambda x: float(np.mean(x == 2)),
                                               mean_stop="mean").reset_index()
    tab(adapt, "primary_S0_tau_mult_w2K4_stop")
    OUT["readings"] = {"share_stop_r2_primary": float(np.mean(p["stop"] == 2)),
                       "share_trivially_safe_runs": float(triv),
                       "S0_w2K4_by_tau_mult": adapt.to_dict("records")}


# --------------------------------------------------------------------------- #
# OC tables (both boxes), sensitivity blocks
# --------------------------------------------------------------------------- #
def oc(stops):
    six = stops[~is_2d(stops["problem"])]
    for box in ("frozen", "union"):
        t = A.oc_table(six, box)
        t["tau_note"] = np.where(t["n_tau_degenerate"] > 0,
                                 "τ degenerate (0 for " + t["n_tau_degenerate"].astype(int).astype(str)
                                 + "/" + t["n_runs"].astype(str) + " runs); τ columns over the remaining runs only, "
                                 "whose τ is 10³–10⁴× below typical (Z-dis seeds 5, 11) — not interpretable", "")
        tab(t, f"oc_6d_{box}")
    d = stops[(stops["box"] == "frozen") & stops["cell"].str.endswith("__q4") & (stops["rule"] == "S0-q4")]
    q4 = d.groupby(["method", "variant"]).agg(
        n_runs=("stop", "size"), mean_stop=("stop", "mean"), mean_evals=("evals", "mean"),
        early=("early", "mean"), cap=("cap", "mean"), late=("late", "mean"),
        med_regret_tau=("regret_budget_tau", "median")).reset_index()
    tab(q4, "blockD_q4")
    b = stops[(stops["box"] == "frozen") & stops["problem"].isin(E_PATHS) & (stops["q"] == 8)
              & (stops["variant"] == PRIMARY_VARIANT)]
    nz = b.groupby(["noise", "method"]).agg(
        n_runs=("stop", "size"), mean_stop=("stop", "mean"), early=("early", "mean"),
        cap=("cap", "mean"), late=("late", "mean"),
        med_regret_tau=("regret_budget_tau", "median")).reset_index()
    tab(nz, "blockB_noise_S0primary")
    OUT["blockD"] = q4.to_dict("records")
    OUT["blockB"] = nz.to_dict("records")


def secondary_cells(stops):
    s = stops[(stops["box"] == "frozen") & stops["cell"].isin(SIX_CELLS_C + E_PATHS)
              & (stops["variant"] == PRIMARY_VARIANT)]
    t = s.groupby(["problem", "method"]).agg(
        n_runs=("stop", "size"), mean_stop=("stop", "mean"), early=("early", "mean"),
        cap=("cap", "mean"), late=("late", "mean"), late_net=("late_net", "mean"),
        med_regret_tau=("regret_budget_tau", "median"),
        med_regret_star=("regret_star", "median")).reset_index()
    tab(t, "S0primary_by_cell_method")
    OUT["S0_by_cell"] = t.to_dict("records")


# --------------------------------------------------------------------------- #
# PREREG §5 deliverables
# --------------------------------------------------------------------------- #
def gain_null_tables(traj):
    six = [t for t in traj if not t["problem"].startswith("R-")]
    g = A.gain_null(six)
    g["problem"] = g["cell"]
    null = g[g["true_gain_tau"] < 0.1]
    t = null.groupby("cell").agg(n_rounds=("obs_gain_tau", "size"),
                                 med_obs_gain_tau=("obs_gain_tau", "median"),
                                 q90_obs_gain_tau=("obs_gain_tau", lambda x: x.quantile(0.9)),
                                 false_continue=("obs_gain_tau", lambda x: float(np.mean(x >= 1)))
                                 ).reset_index()
    cv = pd.DataFrame([{"cell": t_["cell"], "method": t_["method"], "tau": t_["frozen"]["tau"]}
                       for t_ in six]).drop_duplicates(["cell", "tau"])
    cvt = cv.groupby("cell")["tau"].agg(lambda x: x.std(ddof=1) / x.mean()).rename("tau_cv").reset_index()
    t = t.merge(cvt, on="cell", how="left")
    tab(t, "gain_null")
    prim = null[null["cell"].isin(E_PATHS)]
    OUT["gain_null_primary"] = {"n_rounds": int(len(prim)),
                                "false_continue": float(np.mean(prim["obs_gain_tau"] >= 1)),
                                "share_true_null": float(len(prim) / len(g[g["cell"].isin(E_PATHS)]))}
    # true per-round gains on the primary cell (M1): context for 'early'
    pg = g[g["cell"].isin(E_PATHS) & (g["method"] == "M1")]
    tg = pg.groupby("round")["true_gain_tau"].median()
    tab(tg.reset_index(), "primary_M1_true_gain_by_round")
    OUT["primary_true_gain_tau_median_by_round"] = tg.to_dict()


def stage2_check(traj):
    s = A.stage2_conditional(traj)
    wide = len(s) < 10
    if wide:
        s = A.stage2_conditional(traj, wide=True)
    tab(s, "stage2_conditional")
    OUT["stage2"] = {"n_match": int(len(s)), "widened": wide,
                     "by_problem": s.groupby("problem").size().to_dict() if len(s) else {},
                     "median": s[["rem2_tau", "rem6_tau", "rem2_pctH0", "rem6_pctH0"]].median().to_dict()
                     if len(s) else {},
                     "q25": s[["rem2_tau", "rem6_tau"]].quantile(0.25).to_dict() if len(s) else {},
                     "q75": s[["rem2_tau", "rem6_tau"]].quantile(0.75).to_dict() if len(s) else {}}


def calibration(traj):
    cv = A.calibration_vs_error([t for t in traj if not t["problem"].startswith("R-")])
    sp = A.spearman_strata(cv)
    tab(sp, "calibration_spearman")
    agg = cv.groupby("audit_fail")["abs_shortfall_tau"].median()
    OUT["calibration"] = {"n_rounds": int(len(cv)), "share_fail": float(cv["audit_fail"].mean()),
                          "rho_dev_median": float(sp["rho_dev"].median()),
                          "rho_dev_q25_q75": [float(sp["rho_dev"].quantile(.25)),
                                              float(sp["rho_dev"].quantile(.75))],
                          "rho_fail_median": float(sp["rho_fail"].median()),
                          "n_strata": int(len(sp)),
                          "med_abs_shortfall_by_fail": {str(k): float(v) for k, v in agg.items()}}


def density(stops):
    s = stops[(stops["box"] == "frozen") & ~is_2d(stops["problem"]) & (stops["variant"] == PRIMARY_VARIANT)]
    t = s.groupby(["problem", "stop"]).agg(n=("density_at_stop", "size"),
                                           med_density=("density_at_stop", "median")).reset_index()
    tab(t, "density_at_stop")
    p = s[s["problem"].isin(E_PATHS) & (s["method"] == "M1") & (s["noise"] == 1.0) & (s["q"] == 8)]
    OUT["density_primary"] = p.groupby("stop")["density_at_stop"].median().to_dict()


def methods_6d(traj):
    six = [t for t in traj if not t["problem"].startswith("R-")]
    fb = A.fixed_budget(six)
    mt = A.method_table(fb, [64, 96])
    tab(mt, "method_6d")
    # M2 trigger (pre-registered): |median(M1) - median(M3)| of H_n^true / tau_j > 1
    # at n = 64 or 96, pooled primary (E-path-1..5, m = 1, q = 8)
    pr = fb[fb["cell"].isin(E_PATHS) & fb["n"].isin([64, 96])]
    med = pr.groupby(["n", "method"])["H_tau"].median().unstack()
    diff = (med["M1"] - med["M3"]).to_dict()
    pp = pr.pivot_table(index=["cell", "seed", "n"], columns="method", values="H_tau")
    paired = (pp["M1"] - pp["M3"]).groupby(level="n").median().to_dict()
    OUT["M2_trigger"] = {"median_M1_minus_M3_H_tau": diff, "paired_median": paired,
                         "fires": bool(any(abs(v) > 1 for v in diff.values()))}
    hr = pr.groupby(["n", "method"])["H_ratio"].median().unstack()
    OUT["primary_H_ratio_median"] = {int(n): r.to_dict() for n, r in hr.iterrows()}
    return fb


def replay(traj, traj_r):
    e = [t for t in traj if t["problem"].startswith("R-")]
    assert len(e) == 340 and {t["method"] for t in e} == {"M3"}
    fb = A.fixed_budget(e + traj_r)
    out = []
    for label, d in (("incl", fb), ("excl", fb[~((fb["cell"] == REPLAY_SMOKE[0])
                                                 & (fb["seed"] == REPLAY_SMOKE[1]))])):
        mt = A.method_table(d, [21, 35])
        mt["smoke"] = label
        out.append(mt)
    mt = pd.concat(out, ignore_index=True)
    tab(mt, "replay_method_M1_M3_M4")
    m35 = mt[(mt["n"] == 35) & (mt["smoke"] == "incl")]
    OUT["replay_n35"] = {
        "M3_beats_M1": int((m35["med_M3"] > m35["med_M1"]).sum()),
        "M1_beats_M3": int((m35["med_M1"] > m35["med_M3"]).sum()),
        "M3_beats_M4": int((m35["med_M3"] > m35["med_M4"]).sum()),
        "n_grids": int(len(m35))}
    return fb


# --------------------------------------------------------------------------- #
# D49-4 cap input
# --------------------------------------------------------------------------- #
def cap_input(p, stops):
    h = p["stop"].value_counts().reindex(range(1, 5), fill_value=0)
    ev = p["evals"]
    t = pd.DataFrame({"stop_round": h.index, "n_runs": h.values, "share": h.values / h.sum(),
                      "evals": h.index * 8})
    tab(t, "cap_input_primary_hist")
    d = stops[(stops["box"] == "frozen") & stops["cell"].str.endswith("__q4") & (stops["rule"] == "S0-q4")
              & (stops["method"] == "M1")]
    dq = d.groupby("variant")["evals"].describe(percentiles=[.1, .25, .5, .75, .9])
    tab(dq.reset_index(), "cap_input_blockD_evals")
    OUT["cap_input"] = {"hist": dict(zip(map(int, h.index), map(int, h.values))),
                        "evals_quantiles": {str(q): float(ev.quantile(q)) for q in (.1, .25, .5, .75, .9)},
                        "evals_mean": float(ev.mean()),
                        "blockD_M1_evals": dq[["mean", "50%", "90%"]].to_dict("index")}


# --------------------------------------------------------------------------- #
# figures (from the frozen CSVs, shapes asserted first)
# --------------------------------------------------------------------------- #
def figures(stops, fb6, fbr):
    # 1. OC rates: S0 primary variant per cell, M1/M3/M4
    t = pd.read_csv(A.TABLES / "S0primary_by_cell_method.csv")
    assert len(t) == 30 and set(t["method"]) == {"M1", "M3", "M4"}
    cells = E_PATHS + SIX_CELLS_C
    fig, axes = plt.subplots(1, 3, figsize=(13, 3.8), sharey=True)
    cols = {"M1": "#1f5fa8", "M3": "#c2410c", "M4": "#6b7280"}
    for ax, met in zip(axes, ("early", "cap", "late")):
        for i, m in enumerate(("M1", "M3", "M4")):
            d = t[t["method"] == m].set_index("problem").reindex(cells)
            ax.bar(np.arange(len(cells)) + (i - 1) * 0.27, d[met], 0.27, color=cols[m], label=m)
        if met == "early":
            ax.axhline(0.20, color="k", ls="--", lw=1.4)
        ax.set_xticks(np.arange(len(cells)))
        ax.set_xticklabels(cells, rotation=60, ha="right")
        ax.set_title(f"S0 (1·τ, w2, K4): {met} rate")
        ax.set_ylabel("share of runs")
        bold_ticks(ax)
    axes[0].legend(frameon=False, prop={"weight": "bold"})
    fig.tight_layout()
    save(fig, "fig_oc_rates")

    # 2. regret distributions (primary cell, M1): S0 primary vs S-fix-k vs Oracle
    s = stops[(stops["box"] == "frozen") & stops["problem"].isin(E_PATHS) & (stops["noise"] == 1.0)
              & (stops["q"] == 8) & (stops["method"] == "M1")]
    vs = [PRIMARY_VARIANT] + [f"S-fix-{k}" for k in range(1, 9)] + ["Oracle"]
    data = [s[s["variant"] == v]["regret_budget_tau"].values for v in vs]
    assert all(len(x) == 250 for x in data)
    fig, ax = plt.subplots(figsize=(9, 3.8))
    ax.boxplot(data, showfliers=False)
    ax.axhline(1.0, color="k", ls="--", lw=1.4)
    ax.set_xticks(range(1, len(vs) + 1))
    ax.set_xticklabels([v.replace(" ", "\n", 1) for v in vs], fontsize=8)
    ax.set_ylabel("(H_8 − H_stop) / τ_j")
    ax.set_title("Primary cell (E-path-1…5, M1, 250 runs): regret at stop")
    bold_ticks(ax)
    fig.tight_layout()
    save(fig, "fig_regret_primary")

    # 3. S0-vs-S-fix frontier
    A.key_figure(stops, ["E-path", "Z-needle", "E-short"], "fig_frontier")

    # 4. method comparison (6-D at n = 64/96; replay at 21/35)
    mt = pd.read_csv(A.TABLES / "method_6d.csv")
    assert len(mt) == 25 * 2, len(mt)          # 10 m=1 cells + 10 noise + 5 q4, n = 64 / 96
    A.fig_method(fb6[fb6["cell"].isin(cells)], cells, [64, 96], "fig_method_6d")
    rt = pd.read_csv(A.TABLES / "replay_method_M1_M3_M4.csv")
    assert len(rt) == 2 * 2 * 17, len(rt)
    rcells = sorted(fbr["cell"].unique())
    A.fig_method(fbr, rcells, [21, 35], "fig_replay_methods_M1_M3_M4", ncol=6)

    # 5. cap input histogram
    h = pd.read_csv(A.TABLES / "cap_input_primary_hist.csv")
    assert len(h) == 4 and h["n_runs"].sum() == 250
    fig, ax = plt.subplots(figsize=(4.6, 3.4))
    ax.bar(h["stop_round"], h["n_runs"], color="#1f5fa8")
    ax.set_xlabel("S0 stop round s (evals = 8·s)")
    ax.set_ylabel("runs (of 250)")
    ax.set_title("Primary cell: S0 stop rounds\n(DESCRIPTIVE — rule not accepted)")
    ax.set_xticks([1, 2, 3, 4])
    bold_ticks(ax)
    fig.tight_layout()
    save(fig, "fig_cap_input")


def main():
    traj, stops, traj_r, stops_r = load_all()
    p = primary(stops)
    zneedle(traj, stops)
    named_readings(traj, stops, p)
    oc(stops)
    secondary_cells(stops)
    gain_null_tables(traj)
    stage2_check(traj)
    calibration(traj)
    density(stops)
    fb6 = methods_6d(traj)
    fbr = replay(traj, traj_r)
    cap_input(p, stops)
    figures(stops, fb6, fbr)
    (A.TABLES / "results_numbers.json").write_text(json.dumps(OUT, indent=1, default=float) + "\n")
    print(json.dumps(OUT, indent=1, default=float))


if __name__ == "__main__":
    main()
