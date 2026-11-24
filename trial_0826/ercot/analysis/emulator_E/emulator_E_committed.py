#!/usr/bin/env python3
"""Prompt 66 — COMMITTED-FIT block of the EMULATOR BO dry run (after 54's fit-v2 round, tx123 240bde1).

Variants (emulator_E.VARIANTS):
  committed  truth = each objective's committed fit definition (V1 house fallback, E1 fit v2);
             BO GP = the same definition per objective (55 hook, common_E.gp_fitters)
  mmA        model-mismatch check: truth = house fit for BOTH objectives; BO GP = committed (mixed)
  mmB        model-mismatch check: truth = fit v2 for BOTH (V1-v2 EXPLORATORY, not committed); BO GP = committed

    PY=/opt/anaconda3/envs/bogp-botorch/bin/python
    $PY analysis/emulator_E/emulator_E_committed.py collect   # emulator_E_single_committed.csv, emulator_E_multi_committed.csv, summary
    $PY analysis/emulator_E/emulator_E_committed.py figs      # assert-before-draw, figs/*_committed.png

EMULATOR output only: a machinery check, never data.
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import sys

import numpy as np
import pandas as pd
from scipy.stats import poisson

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import emulator_E as em  # noqa: E402
import emulator_E_report as R  # noqa: E402

VARS = ("committed", "mmA", "mmB")
SINGLE_CSV = os.path.join(HERE, "emulator_E_single_committed.csv")
MULTI_CSV = os.path.join(HERE, "emulator_E_multi_committed.csv")
SUMMARY = os.path.join(HERE, "emulator_E_summary_committed.json")
SEEDS = (0, 1, 2, 3, 4)
LABEL = {"committed": "committed (truth = committed fits; BO = committed fits)",
         "mmA": "mismatch A (truth = house fit for both; BO = committed)",
         "mmB": "mismatch B (truth = fit v2 for both, V1-v2 EXPLORATORY; BO = committed)"}


def _x(v):
    return R._load(os.path.join(em.RUNS, f"EMU_extras_{v}.json"))


def _params(truth):
    return R._load(em.TRUTH_PARAMS[truth])


def _sigc():
    cc = R._load(em.CONFIGS)
    return {o: float(cc["objectives"][o]["sigma_c"]) for o in em.SEATED}


def collect():
    single, multi = R._runs(VARS)
    sig = _sigc()
    rows = []
    for d in single:
        P = _params(d["truth"])
        r0 = d["records"][0]
        o = d["objective"]
        ls_t = np.asarray(P["objectives"][o]["ls_std"], float) * np.asarray(P["objectives"][o]["sx"], float)
        ls0 = np.asarray(r0["gp"]["ls_u"], float) if "gp" in r0 else None
        for r in d["records"]:
            row = {"label": "EMULATOR", "variant": d["variant"], "truth": d["truth"], "bo_fit": d["bo_fit"],
                   "bo_fit_definition": (d.get("bo_fitter") or {}).get("def", "house"), "objective": o,
                   "method": d["method"], "seed_id": d["seed_id"], "round": r["round"], "n": r["n"],
                   "f_star": d["f_star"], "B": d["B"], "regret_best_obs_B": r["regret_best_obs_B"],
                   "gap_obs_B": r["gap_obs_B"], "regret_pm_opt_B": r.get("regret_pm_opt_B"),
                   "r0_plugin_regret_B": r0.get("regret_pm_opt_B"), "best_obs_u": json.dumps(r["best_obs_u"])}
            c = r.get("calibration")
            if c:
                row.update({"cov95": c["cov95"], "rms_z": c["rms_z"], "mean_z": c["mean_z"],
                            "n_abs_z_gt3": c["n_abs_z_gt3"], "C2": c["C2"], "C3": c["C3"]})
            g = r.get("gp")
            if g:
                ls = np.asarray(g["ls_u"], float)
                fi = g.get("fit_info") or {}
                U_ = np.asarray(r.get("u_new") or [[np.nan] * 6], float)
                row.update({"n_at_origin": int(np.all(U_ == 0, 1).sum()) if r["round"] else None,
                            "n_unique_designs": len({tuple(x) for x in np.round(U_, 10).tolist()}) if r["round"] else None})
                row.update({"noise_sd_raw": g["noise_sd_raw"], "noise_over_sigma_c": g["noise_sd_raw"] / sig[o],
                            "noise_over_chatter": g["noise_sd_raw"] / P["sigma_c"]["sd"][em.SEATED.index(o)],
                            "ls_drift_vs_r0_max": float(np.max(np.abs(ls / ls0 - 1))),
                            "ls_ratio_vs_truth_max": float(np.max(np.abs(ls / ls_t - 1))),
                            "v2_converged": fi.get("converged"), "mode_gap_v2": fi.get("mode_gap_nats"),
                            "gap_second_v2": fi.get("gap_second_nats"), "loo_rms_z": g.get("loo_rms_z")})
            row.update({"acq_s": r.get("acq_s"), "fit_s": r.get("fit_s"), "wall_s": r.get("wall_s")})
            rows.append(row)
    sdf = pd.DataFrame(rows).sort_values(["variant", "objective", "method", "seed_id", "round"])
    sdf.to_csv(SINGLE_CSV, index=False, float_format="%.10g")
    mrows = []
    for d in multi:
        X = _x(d["variant"])
        hb = X["best_known"]["hv_best_known"]
        Bb = _x("committed")["baselines"]
        P = _params(d["truth"])
        base = {"label": "EMULATOR", "variant": d["variant"], "truth": d["truth"], "bo_fit": d["bo_fit"],
                "scenario": d["scenario"], "seed_id": d["seed_id"], "tau_res": d["tau_res"]["tau_res"],
                "budget_cap_only": d["tau_exact"]["budget_cap_only"],
                "fit_def_V1": d["gp_fitters"]["V1"]["def"], "fit_def_E1": d["gp_fitters"]["E1"]["def"]}
        mrows.append({**base, "round": 0, "n": 48, "hv": d["hv0"], "hv_true_f": d["hv0_true_f"],
                      "hv_true_frac_best": d["hv0_true_f"] / hb, "wall_s": d["init_s"]})
        for r in d["rounds"]:
            if "hv" not in r:
                mrows.append({**base, "round": r["round"], "propose_refused": r.get("propose_refused")})
                continue
            k = r["round"]
            fb = r["hv_true_f"] / hb
            row = {**base, "round": k, "n": r["n"], "n_hv": r["n_hv"], "hv": r["hv"], "hv_true_f": r["hv_true_f"],
                   "hv_true_frac_best": fb, "gain_over_tau_res": r["gain_over_tau_res"],
                   "would_stop_joint": r["would_stop_joint"], "gain_tau_joint": r["gain_tau_joint"],
                   "C1_ok": r["C1_ok"], "C2": r["C2"], "C3": r["C3"], "n_violations": len(r["violations"]),
                   "guardrail_mode_after": r["guardrail_mode_after"], "constraint_used": r["constraint_used"],
                   "halt": r["halt"], "r2_flag": r["r2_flag"], "r2_max": r["r2_max"], "n1_off_flag_a": r["n1_off_flag_a"],
                   "propose_s": r["propose_s"], "qnehvi_s": r["qnehvi_s"], "grade_s": r["grade_s"], "wall_s": r["wall_s"]}
            if d["variant"] == "committed":
                row.update({"effect_vs_vertices_p95": fb - Bb["vertices"]["p95"][k],
                            "effect_vs_plugin_random_p95": fb - Bb["plugin_random"]["p95"][k],
                            "effect_vs_plugin_spread": fb - Bb["plugin_spread"]["p50"][k]})
            for o in em.SEATED:
                c = (r.get("calibration") or {}).get(o, {})
                fi = (r.get("fit_info") or {}).get(o, {})
                nr = (r.get("noise_raw") or {}).get(o)
                row.update({f"{o}_cov95": c.get("cov95"), f"{o}_rms_z": c.get("rms_z"),
                            f"{o}_n_abs_z_gt3": c.get("n_abs_z_gt3"), f"{o}_noise_raw_pre": nr,
                            f"{o}_noise_over_sigma_c": (nr / sig[o]) if nr is not None else None,
                            f"{o}_noise_over_emulator": (nr / P["sigma_c"]["sd"][em.SEATED.index(o)]) if nr is not None else None,
                            f"{o}_v2_converged": fi.get("converged"), f"{o}_mode_gap_v2": fi.get("mode_gap_nats"),
                            f"{o}_gap_second_v2": fi.get("gap_second_nats")})
            mrows.append(row)
    mdf = pd.DataFrame(mrows).sort_values(["variant", "scenario", "seed_id", "round"])
    mdf.to_csv(MULTI_CSV, index=False, float_format="%.10g")
    summ = summarize(sdf, mdf, single, multi)
    with open(SUMMARY, "w") as f:
        json.dump(summ, f, indent=1, default=float)
        f.write("\n")
    print(json.dumps(summ["pass_fail"], indent=1, default=str))
    return sdf, mdf, summ


def summarize(sdf, mdf, single, multi):
    pf = []
    cs = sdf[sdf.variant == "committed"]
    cm = mdf[(mdf.variant == "committed") & (mdf["round"] >= 1) & mdf["hv"].notna()]
    got_s = {(d["objective"], d["method"], d["seed_id"]) for d in single if d["variant"] == "committed"}
    got_m = {(d["scenario"], d["seed_id"]) for d in multi if d["variant"] == "committed"}
    ends = {(d["scenario"], d["seed_id"]): [r["round"] for r in d["rounds"] if "hv" in r] for d in multi
            if d["variant"] == "committed"}
    ok_ends = all((v == [1, 2, 3, 4]) if k[0] in ("s0", "s1") else (v == [1]) for k, v in ends.items())
    pf.append({"n": 1, "check": "No crash; each lane ends where its scenario says",
               "result": f"single {len(got_s)}/12, multi {len(got_m)}/15, ends as expected = {ok_ends}",
               "pass": bool(len(got_s) == 12 and len(got_m) == 15 and ok_ends)})
    pf.append({"n": 2, "check": "C1 ingest on every emulated round", "result": f"{int(cm['C1_ok'].astype(bool).sum())}/{len(cm)}",
               "pass": bool(cm["C1_ok"].astype(bool).all())})
    per = {}
    for o in em.SEATED:
        sb = cs[(cs.objective == o) & (cs.method == "bo") & (cs["round"] >= 1)]
        n = len(sb) + len(cm)
        c2 = int(sb["C2"].astype(bool).sum() + (cm[f"{o}_cov95"] <= 4).sum())
        c3 = int(sb["C3"].astype(bool).sum() + (cm[f"{o}_n_abs_z_gt3"] >= 3).sum())
        e2 = n * R.C2_RATE
        rz = pd.concat([sb["rms_z"], cm[f"{o}_rms_z"]])
        per[o] = {"cells": n, "C2": c2, "C3": c3, "expected_C2": e2, "limit_C2": int(poisson.ppf(0.95, e2)),
                  "rms_z_median": float(rz.median()), "rms_z_range": [float(rz.min()), float(rz.max())],
                  "cov95_batches": [int(x) for x in pd.concat([sb["cov95"], cm[f"{o}_cov95"]])]}
    pf.append({"n": 3, "check": "C2/C3 per objective (power statement, not a pass/fail on its own)",
               "result": "; ".join(f"{o}: C2 {per[o]['C2']}, C3 {per[o]['C3']} in {per[o]['cells']} (round, objective) cells; "
                                   f"rms z median {per[o]['rms_z_median']:.2f}" for o in em.SEATED), "pass": None})
    within, beats = {}, {}
    for o in em.SEATED:
        b4 = cs[(cs.objective == o) & (cs.method == "bo") & (cs["round"] == 4)].set_index("seed_id")["regret_best_obs_B"]
        r4 = cs[(cs.objective == o) & (cs.method == "random") & (cs["round"] == 4)].set_index("seed_id")["regret_best_obs_B"]
        within[o] = int((b4 <= 2).sum())
        beats[o] = {"bo_mean": float(b4.mean()), "random_mean": float(r4.mean()),
                    "per_seed": {int(s): bool(b4[s] < r4[s]) for s in b4.index}}
    pf.append({"n": 4, "check": "Single-objective within 2 B_j by r4 on >= 2 of 3 seeds",
               "result": "; ".join(f"{o} {within[o]}/3" for o in em.SEATED), "pass": all(v >= 2 for v in within.values())})
    pf.append({"n": 5, "check": "Single-objective BO beats random-8 at r4 on every objective",
               "result": "; ".join(f"{o} BO {beats[o]['bo_mean']:.3f} B vs random {beats[o]['random_mean']:.2f} B" for o in em.SEATED),
               "pass": all(b["bo_mean"] < b["random_mean"] and all(b["per_seed"].values()) for b in beats.values())})

    def lane(sc, s):
        return next(d for d in multi if d["variant"] == "committed" and d["scenario"] == sc and d["seed_id"] == s)
    s0 = all(lane("s0", s)["guardrail_mode"] == "monitor" and not lane("s0", s)["halt"] for s in SEEDS)
    s1 = all(lane("s1", s)["guardrail_flipped_at_round"] == 1 and
             all("shed <=" in (lane("s1", s)["settings"][str(k)] or {}).get("constraint", "") for k in (2, 3, 4))
             and [r["n_hv"] for r in lane("s1", s)["rounds"]] == [55, 63, 71, 79] for s in SEEDS)
    s2 = all(lane("s2", s)["halt"] and lane("s2", s)["halt_file"] and "HALT" in (lane("s2", s)["rounds"][-1].get("propose_refused") or "")
             for s in SEEDS)
    pf.append({"n": 6, "check": "Branches: s0 monitor to the cap; s1 constrained from r2, n_hv 55/63/71/79; s2 HALT + refusal (5 lanes each)",
               "result": f"s0 {s0}, s1 {s1}, s2 {s2}", "pass": bool(s0 and s1 and s2)})
    tz = bool(cm["budget_cap_only"].astype(bool).all() and cm["gain_tau_joint"].isna().all()
              and (~cm["would_stop_joint"].astype(bool)).all())
    mon = bool((~cm["r2_flag"].astype(bool)).all() and (~cm["n1_off_flag_a"].astype(bool)).all())
    pf.append({"n": 7, "check": "tau_exact = 0 -> cap-only; R2 / N1_off no flags", "result": f"cap-only {tz}; monitors quiet {mon}",
               "pass": bool(tz and mon)})
    v2c = mdf[(mdf.variant == "committed") & mdf["E1_v2_converged"].notna()]["E1_v2_converged"].astype(bool)
    sv2 = cs[(cs.objective == "E1") & cs["v2_converged"].notna()]["v2_converged"].astype(bool)
    pf.append({"n": 8, "check": "Fit v2 (E1) converged at every round fit (>= 2 restarts within 1e-3 n nats)",
               "result": f"multi {int(v2c.sum())}/{len(v2c)}, single {int(sv2.sum())}/{len(sv2)}",
               "pass": bool(v2c.all() and sv2.all())})
    f4 = cm[(cm.scenario == "s0") & (cm["round"] == 4)]["hv_true_frac_best"]
    pf.append({"n": 9, "check": "HV fraction of the best-known front (true f; upper bounds)",
               "result": f"s0 r4 {f4.min():.3f}–{f4.max():.3f}", "pass": None})
    return {"label": "EMULATOR", "pass_fail": pf, "per_objective_gates": per, "within_2B": within, "beats_random": beats}


def _assert_frozen(sdf, mdf):
    single, multi = R._runs(VARS)
    n = 0
    for d in single:
        em.set_truth(d["truth"])
        f = em.load_emulator()["f"][d["objective"]]
        for r in d["records"]:
            row = sdf[(sdf.variant == d["variant"]) & (sdf.objective == d["objective"]) & (sdf.method == d["method"])
                      & (sdf.seed_id == d["seed_id"]) & (sdf["round"] == r["round"])]
            reg = (f(np.asarray([r["best_obs_u"]]))[0] - d["f_star"]) / d["B"]
            assert len(row) == 1 and abs(reg - float(row["regret_best_obs_B"].iloc[0])) <= 1e-6 * max(1, abs(reg))
            n += 1
    for d in multi:
        em.set_truth(d["truth"])
        emu = em.load_emulator()
        hb = _x(d["variant"])["best_known"]["hv_best_known"]
        Fa = [np.asarray(emu["P"]["start_set"]["f"], float)]
        for r in d["rounds"]:
            if "hv" not in r:
                continue
            w = f"methods_E_EMU_{d['variant']}_{d['scenario']}_s{d['seed_id']}_r{r['round']}"
            tab = pd.read_csv(os.path.join(HERE, "waves", w, "objectives_EMULATOR.csv"))
            dm = pd.read_csv(os.path.join(HERE, "waves", w, "design_matrix.csv"), float_precision="round_trip").sort_values("index")
            U = dm[[c for c in dm.columns if c.startswith("u_")]].to_numpy(float)
            assert not np.any((U > 0) & (U < 1e-9))
            Fa.append(em.true_f(U)[tab["R1"].to_numpy(float) <= 1.0])
            row = mdf[(mdf.variant == d["variant"]) & (mdf.scenario == d["scenario"]) & (mdf.seed_id == d["seed_id"])
                      & (mdf["round"] == r["round"])]
            assert abs(em.hv2d(np.vstack(Fa), emu["R"]) / hb - float(row["hv_true_frac_best"].iloc[0])) <= 1e-8
            n += 1
    em.set_truth("house")
    return n


def figs():
    plt = R._plt()
    sdf = pd.read_csv(SINGLE_CSV)
    mdf = pd.read_csv(MULTI_CSV)
    n = _assert_frozen(sdf, mdf)
    print(f"assert-before-draw (committed block): {n} plotted values recomputed == CSV")
    out = []
    floor = 1e-3
    marks = {0: "o", 1: "s", 2: "^"}
    # 1 single regret
    fig, axes = plt.subplots(1, 2, figsize=(14, 4.8))
    for ax, o in zip(axes, em.SEATED):
        for (v, me), sty in {("committed", "bo"): dict(color="C0", lw=2, ls="-"),
                             ("committed", "random"): dict(color="0.45", lw=1.5, ls="--"),
                             ("mmA", "bo"): dict(color="C1", lw=1.6, ls="-."), ("mmB", "bo"): dict(color="C2", lw=1.6, ls=":")}.items():
            g = sdf[(sdf.objective == o) & (sdf.variant == v) & (sdf.method == me)]
            assert len(g) > 0 and g["regret_best_obs_B"].notna().all()
            for s, gs in g.groupby("seed_id"):
                lab = {"committed": f"{'BO' if me == 'bo' else 'random-8'}, committed", "mmA": "BO, mismatch A",
                       "mmB": "BO, mismatch B"}[v]
                ax.plot(gs["round"], np.maximum(gs["regret_best_obs_B"], floor), marker=marks[s], ms=5,
                        label=f"{lab}, seed {s}", **sty)
        plug = float(sdf[(sdf.objective == o) & (sdf.variant == "committed") & (sdf.method == "bo")]["r0_plugin_regret_B"].iloc[0])
        ax.axhline(max(plug, floor), color="C4", ls="--", lw=1.3, label="r0 plug-in optimum (committed BO GP)")
        ax.axhline(2.0, color="C3", ls="-.", lw=1.3, label="2 B_j")
        ax.set_yscale("log")
        ax.set_xticks([0, 1, 2, 3, 4])
        ax.set_xlabel("Round (8 designs per round)")
        ax.set_ylabel(f"Regret of best observed, {o} (B units)")
        fd = sdf[(sdf.objective == o) & (sdf.variant == "committed") & (sdf.method == "bo")]["bo_fit_definition"].iloc[0]
        ax.set_title(f"{o} (BO fit: {fd}; values < {floor:g} drawn at the floor)")
        if o == "E1":
            gE = sdf[(sdf.variant == "committed") & (sdf.objective == "E1") & (sdf.method == "bo") & (sdf["round"] >= 2)]
            n0, nt = int(gE["n_at_origin"].sum()), 8 * len(gE)
            assert nt == 72 and n0 <= nt
            ax.annotate(f"r2–r4: {n0} of {nt} designs at u = 0\n(replicate collapse; regret = r0 plug-in)", (2.5, floor),
                        xytext=(1.2, 0.05), fontsize=9, fontweight="bold", arrowprops=dict(arrowstyle="->"))
        R._bold(ax)
    h, l = axes[0].get_legend_handles_labels()
    fig.legend(h, l, loc="center left", bbox_to_anchor=(1.0, 0.5), fontsize=8.5)
    fig.suptitle("EMULATOR (committed fits) — single-objective regret", fontweight="bold")
    fig.tight_layout()
    p = os.path.join(em.FIGS, "fig_EMU_single_regret_committed.png")
    fig.savefig(p, dpi=150, bbox_inches="tight")
    plt.close(fig)
    out.append(p)
    # 2 multi
    X = _x("committed")
    fig, ax = plt.subplots(figsize=(9, 5.2))
    ks = [0, 1, 2, 3, 4]
    for name, col in (("uniform", "0.6"), ("vertices", "C4"), ("plugin_random", "C1")):
        b = X["baselines"][name]
        ax.fill_between(ks, b["p5"], b["p95"], color=col, alpha=0.3, label=f"{R.BASE_NAMES[name]}: 5–95 % ({b['n_rep']} reps; committed truth only)")
    ax.plot(ks, X["baselines"]["plugin_spread"]["p50"], color="C1", lw=2, ls="-.", marker="D", ms=4, label=R.BASE_NAMES["plugin_spread"])
    for (v, sc), sty in {("committed", "s0"): dict(color="C0", lw=2), ("committed", "s1"): dict(color="C9", lw=1.5, ls="--"),
                         ("mmA", "s0"): dict(color="C5", lw=1.6, ls="-."), ("mmB", "s0"): dict(color="C2", lw=1.6, ls=":")}.items():
        g = mdf[(mdf.variant == v) & (mdf.scenario == sc) & mdf["hv"].notna()]
        assert len(g) > 0 and g["hv_true_frac_best"].between(0, 1 + 1e-12).all()
        for i, (s, gs) in enumerate(g.groupby("seed_id")):
            ax.plot(gs["round"], gs["hv_true_frac_best"], marker="o", ms=4,
                    label=(f"qNEHVI {sc}, {LABEL[v].split(' (')[0]}" if i == 0 else None), **sty)
    g2 = mdf[(mdf.variant == "committed") & (mdf.scenario == "s2") & (mdf["round"] == 1)]
    ax.scatter(g2["round"], g2["hv_true_frac_best"], marker="x", s=50, c="C3", zorder=5, label="qNEHVI s2 (HALT after r1)")
    ax.set_xticks(ks)
    ax.set_xlabel("Round")
    ax.set_ylabel("True-f HV / HV(best-known front of its truth)")
    ax.set_title("EMULATOR (committed fits) — multi-objective vs matched-budget baselines")
    ax.legend(fontsize=8.5, loc="center left", bbox_to_anchor=(1.01, 0.5))
    R._bold(ax)
    fig.tight_layout()
    p = os.path.join(em.FIGS, "fig_EMU_multi_hv_committed.png")
    fig.savefig(p, dpi=150, bbox_inches="tight")
    plt.close(fig)
    out.append(p)
    # 3 front
    em.set_truth("committed")
    P = em.load_emulator()["P"]
    bk = np.asarray(X["best_known"]["front"], float)
    F0 = np.asarray(P["start_set"]["f"], float)
    vmin = P["objectives"]["V1"]["y_train_min"]
    Rr = P["R"]
    fig, ax = plt.subplots(figsize=(9, 6.2))
    ax.axvspan(0.85, vmin / 1e6, color="C1", alpha=0.12, label=f"V1 < {vmin / 1e6:.3f} TWh: outside observed data")
    ax.scatter(F0[:, 0] / 1e6, F0[:, 1] / 1e9, s=18, c="0.5", label="start set (f)")
    for s in SEEDS:
        U = np.vstack([pd.read_csv(os.path.join(HERE, "waves", f"methods_E_EMU_committed_s0_s{s}_r{k}", "design_matrix.csv"))
                       .filter(like="u_").to_numpy(float) for k in range(1, 5)])
        F = em.true_f(U)
        assert F.shape == (32, 2) and np.isfinite(F).all()
        ax.scatter(F[:, 0] / 1e6, F[:, 1] / 1e9, s=16, c="C0", alpha=0.6, label="qNEHVI s0, 5 lanes (f)" if s == 0 else None)
    ax.step(bk[:, 0] / 1e6, bk[:, 1] / 1e9, where="post", color="k", lw=1.6, label="best-known front")
    ax.plot([ax.get_xlim()[0], Rr["V1"] / 1e6, Rr["V1"] / 1e6], [Rr["E1"] / 1e9, Rr["E1"] / 1e9, ax.get_ylim()[0]],
            color="C4", ls="--", lw=1.4, label="R box")
    ax.set_xlabel("V1 curtailment f (TWh)")
    ax.set_ylabel("E1 system cost f ($B)")
    ax.set_title("EMULATOR (committed fits) — objective space, true f")
    ax.legend(fontsize=8.5, loc="center left", bbox_to_anchor=(1.01, 0.5))
    R._bold(ax)
    fig.tight_layout()
    p = os.path.join(em.FIGS, "fig_EMU_front_committed.png")
    fig.savefig(p, dpi=150, bbox_inches="tight")
    plt.close(fig)
    out.append(p)
    em.set_truth("house")
    # 4 calibration: cov95 per batch
    fig, axes = plt.subplots(1, 2, figsize=(14, 4.8))
    for ax, o in zip(axes, em.SEATED):
        sb = sdf[(sdf.variant == "committed") & (sdf.objective == o) & (sdf.method == "bo") & (sdf["round"] >= 1)]
        cm = mdf[(mdf.variant == "committed") & (mdf["round"] >= 1) & mdf["hv"].notna()]
        assert sb["cov95"].between(0, 8).all() and cm[f"{o}_cov95"].between(0, 8).all()
        rng = np.random.default_rng(0)
        ax.scatter(sb["round"] - 0.15 + rng.uniform(-0.05, 0.05, len(sb)), sb["cov95"], s=36, c="C0", marker="o",
                   label="single-objective BO (3 seeds)")
        ax.scatter(cm["round"] + 0.15 + rng.uniform(-0.05, 0.05, len(cm)), cm[f"{o}_cov95"], s=36, c="C9", marker="^",
                   label="multi (55 grade_round; s0/s1/s2 lanes)")
        ax.axhline(4.5, color="C3", ls="-.", lw=1.4, label="C2 fires at cov95 <= 4")
        ax.set_ylim(-0.5, 8.5)
        ax.set_xticks([1, 2, 3, 4])
        ax.set_xlabel("Round")
        ax.set_ylabel(f"{o}: cov95 of the 8 new points")
        fd = "house fallback" if o == "V1" else "fit v2"
        ax.set_title(f"{o} ({fd}): cov95 of each round's 8 new points")
        R._bold(ax)
    h, l = axes[0].get_legend_handles_labels()
    fig.legend(h, l, loc="center left", bbox_to_anchor=(1.0, 0.5), fontsize=9)
    fig.suptitle("EMULATOR (committed fits) — cov95 of each round's 8 new points (C2 = REVIEW flag at <= 4)", fontweight="bold")
    fig.tight_layout()
    p = os.path.join(em.FIGS, "fig_EMU_calibration_committed.png")
    fig.savefig(p, dpi=150, bbox_inches="tight")
    plt.close(fig)
    out.append(p)
    print("\n".join(out))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["collect", "figs"])
    a = ap.parse_args(argv)
    collect() if a.cmd == "collect" else figs()
    return 0


if __name__ == "__main__":
    sys.exit(main())


# --------------------------------------------------------------------------- #
# EMULATOR_BO.md section (prepended by emulator_E_report.write_md)
# --------------------------------------------------------------------------- #

def _r(s, fmt="{:.3f}"):
    s = pd.Series(s).dropna()
    return f"{fmt.format(s.min())}–{fmt.format(s.max())}"


def md_lines():
    sdf = pd.read_csv(SINGLE_CSV)
    mdf = pd.read_csv(MULTI_CSV)
    S = R._load(SUMMARY)
    hs = pd.read_csv(R.SINGLE_CSV)
    hm = pd.read_csv(R.MULTI_CSV)
    HX = R._load(os.path.join(em.RUNS, "EMU_extras.json"))
    X = _x("committed")
    Pc = _params("committed")
    Pv = _params("v2both")
    Ph = R._load(em.PARAMS)
    cc = R._load(em.CONFIGS)
    sig = _sigc()
    cs = sdf[sdf.variant == "committed"]
    cb = cs[cs.method == "bo"]
    cm = mdf[(mdf.variant == "committed") & (mdf["round"] >= 1) & mdf["hv"].notna()]
    hb_ = hs[(hs.variant == "house") & (hs.method == "bo")]
    hmm = hm[(hm.variant == "house") & (hm["round"] >= 1) & hm["hv"].notna()]
    po = S["per_objective_gates"]
    f4c = cm[(cm.scenario == "s0") & (cm["round"] == 4)]
    f4h = hmm[(hmm.scenario == "s0") & (hmm["round"] == 4)]
    E1n = pd.concat([cb[(cb.objective == "E1")]["noise_over_sigma_c"], cm["E1_noise_over_sigma_c"]])
    V1n = pd.concat([cb[(cb.objective == "V1")]["noise_over_sigma_c"], cm["V1_noise_over_sigma_c"]])
    E1nh = pd.concat([hb_[hb_.objective == "E1"]["noise_sd_raw"], hmm["E1_noise_raw_pre"]]) / sig["E1"]
    V1nh = pd.concat([hb_[hb_.objective == "V1"]["noise_sd_raw"], hmm["V1_noise_raw_pre"]]) / sig["V1"]
    rzE_h = pd.concat([hb_[(hb_.objective == "E1") & (hb_["round"] >= 1)]["rms_z"], hmm["E1_rms_z"]])
    rzE_c = pd.concat([cb[(cb.objective == "E1") & (cb["round"] >= 1)]["rms_z"], cm["E1_rms_z"]])
    rzV_c = pd.concat([cb[(cb.objective == "V1") & (cb["round"] >= 1)]["rms_z"], cm["V1_rms_z"]])
    gaps = pd.concat([cb[cb.objective == "E1"]["mode_gap_v2"], cm["E1_mode_gap_v2"]]).dropna()
    gsec = pd.concat([cb[cb.objective == "E1"]["gap_second_v2"], cm["E1_gap_second_v2"]]).dropna()
    conv = pd.concat([cb[cb.objective == "E1"]["v2_converged"], cm["E1_v2_converged"]]).dropna().astype(bool)
    e1c2 = cb[(cb.objective == "E1") & (cb["round"] >= 1) & (cb["C2"] == True)]  # noqa: E712
    fE_h, fE_c = Ph["objectives"]["E1"]["f_star"], Pc["objectives"]["E1"]["f_star"]
    emin = Pc["objectives"]["E1"]["y_train_min"]
    b4 = lambda df, o, me: df[(df.objective == o) & (df.method == me) & (df["round"] == 4)]["regret_best_obs_B"]  # noqa: E731
    plug = lambda df, o: float(df[(df.objective == o) & (df.method == "bo")]["r0_plugin_regret_B"].iloc[0])  # noqa: E731
    eff_c = f4c["effect_vs_plugin_spread"]
    eff_h = f4h["effect_vs_plugin_spread"]
    wall_c = cm[cm.scenario == "s0"]["wall_s"].mean(); wall_h = hmm[hmm.scenario == "s0"]["wall_s"].mean()
    fitE_c = cb[(cb.objective == "E1") & (cb["round"] >= 1)]["fit_s"].mean()
    fitE_h = hb_[(hb_.objective == "E1") & (hb_["round"] >= 1)]["fit_s"].mean()
    ov = X["seed_overlap"]
    from scipy.stats import norm
    emu_sd = {o: Pc["sigma_c"]["sd"][i] for i, o in enumerate(em.SEATED)}
    E1e = pd.concat([cb[cb.objective == "E1"]["noise_sd_raw"], cm["E1_noise_raw_pre"]]) / emu_sd["E1"]
    V1e = pd.concat([cb[cb.objective == "V1"]["noise_sd_raw"], cm["V1_noise_raw_pre"]]) / emu_sd["V1"]
    gE = cb[(cb.objective == "E1") & (cb["round"] >= 1)].sort_values(["seed_id", "round"])
    col_txt = "; ".join(f"seed {s}: " + " ".join(f"({int(a)},{int(b)})" for a, b in zip(g["n_at_origin"], g["n_unique_designs"]))
                        for s, g in gE.groupby("seed_id"))
    n0_r24, nt_r24 = int(gE[gE["round"] >= 2]["n_at_origin"].sum()), 8 * int((gE["round"] >= 2).sum())
    gEh = hb_[(hb_.objective == "E1") & (hb_["round"] >= 2)]
    hs_runs = {s: R._load(os.path.join(em.RUNS, "single", f"EMU_single_house_E1_bo_s{s}.json")) for s in (0, 1, 2)}
    n0_house = sum(int(np.all(np.asarray(r["u_new"]) == 0, 1).sum()) for d in hs_runs.values() for r in d["records"][2:])
    # the flagged batch: single E1 seed 0, r2 (replicated design) — mechanism
    d0 = R._load(os.path.join(em.RUNS, "single", "EMU_single_committed_E1_bo_s0.json"))
    r1_, r2_ = d0["records"][1], d0["records"][2]
    U2 = np.asarray(r2_["u_new"]); ps2 = np.asarray(r2_["pred_sd"]); pm2 = np.asarray(r2_["pred_mean"])
    f2 = np.asarray(r2_["f_new"]); y2 = np.asarray(r2_["y_new"])
    n_r1_origin = int(np.all(np.asarray(r1_["u_new"]) == 0, 1).sum())
    nf1 = r1_["gp"]["noise_sd_raw"]; rho = nf1 / emu_sd["E1"]
    cov_rep = 2 * norm.cdf(1.96 * rho) - 1
    pm_err = float(((f2 - pm2) / ps2).mean())
    slat = float(np.sqrt(max(ps2[0] ** 2 - nf1 ** 2, 0.0)))
    rs = np.random.default_rng(66)
    zz = (rs.normal(0, slat, (200000, 1)) + rs.normal(0, emu_sd["E1"], (200000, 8))) / ps2[0]
    cv = (np.abs(zz) <= 1.96).sum(1); n3 = (np.abs(zz) > 3).sum(1)
    pC2, pC3, pB = float((cv <= 4).mean()), float((n3 >= 3).mean()), float(((cv <= 4) & (n3 >= 3)).mean())
    cmE1min = int(cm["E1_cov95"].min()); cmE1c2 = int((cm["E1_cov95"] <= 4).sum())
    # mismatch B V1 detail
    dB = R._load(os.path.join(em.RUNS, "single", "EMU_single_mmB_V1_bo_s0.json"))
    mfe = [r["min_f_evaluated_B"] for r in dB["records"]]
    pmr = [r.get("regret_pm_opt_B") for r in dB["records"]]
    nz = [(r["gap_obs_B"] - r["regret_best_obs_B"]) * em.B["V1"] / emu_sd["V1"] for r in dB["records"]]
    XA, XB = _x("mmA"), _x("mmB")
    mvA = float(mdf[(mdf.variant == "mmA") & (mdf.scenario == "s0") & (mdf["round"] == 4)]["hv_true_frac_best"].iloc[0])
    mvB = float(mdf[(mdf.variant == "mmB") & (mdf.scenario == "s0") & (mdf["round"] == 4)]["hv_true_frac_best"].iloc[0])
    lsE = Pc["objectives"]["E1"]["hyperparameters"]["ls_u"]
    U0c = np.asarray(Pc["start_set"]["U"], float)
    lsv = np.asarray(list(lsE.values()), float)
    near = float(np.sqrt(((U0c / lsv) ** 2).sum(1)).min())
    cE = Pc["objectives"]["E1"]["mean_const_std"]
    L = []
    A = L.append
    A("# A. Committed-fit rerun (fit=committed; tx123 240bde1)\n")
    A("This block repeats the dry run on the committed fits after 54's fit-v2 round. `committed_configs.json` now names a "
      "fit definition per objective: **V1 = house (fallback)** (rbf+std; fit v2 failed its holdout, 37/48) and **E1 = fit v2** "
      "(m52+std; holdout 48/48). The emulator truth uses each objective's committed definition. The BO's own GP uses the SAME "
      "definition per objective (plan AMENDMENT 2026-11-24b §3, last sentence) through a new 55 hook (§A.6). The house block "
      "(section B below) is kept as run.\n")
    A("## A.0 Answer in two minutes\n")
    A(f"1. **What changed in the truth?** V1 is unchanged (house fallback; same f, f* = {Pc['objectives']['V1']['f_star'] / 1e6:.3f} TWh). "
      f"E1 is now the fit-v2 posterior mean: longer lengthscales ({' / '.join(f'{v:.3f}' for v in lsE.values())} vs 0.96–1.90), a "
      f"smoother surface, and f*(E1) = ${fE_c / 1e6:,.1f}M at the no-PEM vertex u = 0 (house truth: ${fE_h / 1e6:,.1f}M near it), "
      f"${(emin - fE_c) / 1e6:.0f}M = {(emin - fE_c) / em.B['E1']:.1f} B below the lowest observed E1. **This is a smooth-trend "
      f"model claim, not data:** u = 0 lies {near:.2f} lengthscales from the nearest start point and the fitted constant mean is "
      f"{cE:.1f} s_y, so the value at the origin comes from the trend. The first real round tests it. Both optima are still box "
      "vertices outside the data.")
    A(f"2. **What changed in the BO GP and its bands?** The E1 GP now infers noise at {_r(E1n, '{:.2f}')} × the committed σ_c "
      f"(house: {_r(E1nh, '{:.2f}')} ×). The emulator adds the shrunk Σ_c chatter, sd {emu_sd['E1'] / 1e3:,.0f}k = "
      f"{emu_sd['E1'] / sig['E1']:.3f} σ_c, so against the noise actually present the E1 GP noise is {_r(E1e, '{:.2f}')} × — it "
      f"UNDER-estimates the noise in {int((E1e < 1).sum())} of {len(E1e)} round fits. E1 rms z median {rzE_c.median():.2f} "
      f"(house {rzE_h.median():.2f}). V1 keeps the house fit: noise {_r(V1e, '{:.1f}')} × the emulator noise, rms z median "
      f"{rzV_c.median():.2f}. Fit v2 converged at every "
      f"E1 round fit ({int(conv.sum())}/{len(conv)}); the best two restarts agree to ≤ {gsec.max():.1e} nats; the gap to the next "
      f"mode is {gaps.min():.1f}–{gaps.max():.1f} nats (`mode_gap_v2`).")
    A(f"3. **What do the gates do now?** **V1: no power** — C2 {po['V1']['C2']}, C3 {po['V1']['C3']} in {po['V1']['cells']} cells; "
      f"rms z median {po['V1']['rms_z_median']:.2f}, i.e. the V1 bands are ≈ {1 / po['V1']['rms_z_median']:.0f}× too wide. A V1 misfit "
      f"is invisible to C2/C3. **E1: the v2 bands are narrow enough that a flag is possible; the multi path never fired** "
      f"(E1 C2 {cmE1c2} of {len(cm)} batches, minimum cov95 {cmE1min}). The one E1 event (C2 + C3) is single-objective seed 0 "
      f"round 2: 8 IDENTICAL designs at u = 0, a point already observed {n_r1_origin}× in r1. All 8 z share one posterior-mean "
      f"error ({pm_err:+.2f} predictive sd) plus independent noise draws. The mechanism is under-estimated noise at a replicated "
      f"design (r1 fit noise {nf1 / sig['E1']:.3f} σ_c vs emulator noise {emu_sd['E1'] / sig['E1']:.3f} σ_c, ρ = {rho:.2f}; "
      f"coverage at a replicate 2Φ(1.96ρ) − 1 = {cov_rep:.2f}), not distance from the start set. Simulated for this batch "
      f"(latent sd from the predictive sd minus the fitted noise; emulated chatter; 200,000 draws): P(C2) {pC2:.2f}, "
      f"P(C3) {pC3:.3f}, both {pB:.3f} per batch (the review's model gave 0.22 / 0.083 / 0.07). C2 and C3 are record + REVIEW "
      "only (acquire_E.py): the real campaign would get two REVIEW entries, no stop.")
    _ = None
    A(f"4. **Did the search change?** No. Single-objective V1 reaches {S['beats_random']['V1']['bo_mean']:.2f} B by r4 on 3/3 "
      f"seeds (r0 plug-in {plug(cs, 'V1'):.3f} B). **Single-objective E1 collapses to replicating u = 0:** (designs at u = 0, "
      f"unique designs) per round — {col_txt}; {n0_r24} of {nt_r24} r2–r4 designs sit at the exact origin (house block: "
      f"{n0_house} of 72). \"E1 0.000 B\" is the r0 plug-in ({plug(cs, 'E1'):.1e} B); single-objective E1 says nothing about "
      "search. It is direct evidence that a v2 GP + noisy EI replicates the incumbent (§A.7). The multi path did not "
      f"(minimum proposal distance to the evaluated set {min(d['min_dist_to_evaluated'] for d in ov['min_dist']):.3f}). "
      f"Multi s0 reaches {_r(f4c['hv_true_frac_best'])} of the best-known front (house block {_r(f4h['hv_true_frac_best'])}); "
      f"BO − r0 plug-in spread = {_r(eff_c, '{:+.3f}')}. **On a self-consistent truth BO ≈ plug-in. Under V1 mismatch BO "
      f"recovers from a {float(XB['r0_plugin']['mmB']['objectives']['V1']['regret_B']):.2f} B plug-in error** (§A.5). The machinery "
      "took every expected branch (s0 cap, s1 constrained from r2, s2 HALT), C1 45/45.")
    A(f"5. **Cost.** Fit v2 on E1 (16 restarts) takes {fitE_c:.1f} s per fit here (house {fitE_h:.1f} s); a multi-objective round "
      f"takes {wall_c:.1f} s (house {wall_h:.1f} s) at 2 threads. On CRC expect tens of seconds; < 1 % of a PCM round.\n")
    A("## A.1 Verdict (committed block)\n")
    A("| # | check | result | verdict |")
    A("|---|---|---|---|")
    for r in S["pass_fail"]:
        v = "reported" if r["pass"] is None else ("PASS" if r["pass"] else "FAIL")
        if r["n"] == 3:
            v = ("V1: NO POWER (house fallback). E1: a flag is possible; the multi path never fired; the single E1 event is "
                 "replicate-noise under-estimation at u = 0 (A.0 item 3). REVIEW only, never a stop")
        A(f"| {r['n']} | {r['check']} | {r['result']} | {v} |")
    A("")
    A("## A.2 House vs committed, per metric\n")
    Bh, Bc = HX["baselines"], X["baselines"]
    rows = [
        ("E1 truth f*", f"${fE_h / 1e6:,.2f}M near u = 0", f"${fE_c / 1e6:,.2f}M at u = 0"),
        ("E1 truth lengthscales (u)", " / ".join(f"{v:.2f}" for v in Ph["objectives"]["E1"]["hyperparameters"]["ls_u"].values()),
         " / ".join(f"{v:.2f}" for v in Pc["objectives"]["E1"]["hyperparameters"]["ls_u"].values())),
        ("BO fit V1 / E1", "house / house", "house (fallback) / fit v2"),
        ("single r4 regret V1, mean (B)", f"{b4(hs[hs.variant == 'house'], 'V1', 'bo').mean():.3f}", f"{b4(cs, 'V1', 'bo').mean():.3f}"),
        ("single r4 regret E1, mean (B)", f"{b4(hs[hs.variant == 'house'], 'E1', 'bo').mean():.3f}", f"{b4(cs, 'E1', 'bo').mean():.3f}"),
        ("r0 plug-in regret V1 / E1 (B)", f"{plug(hs[hs.variant == 'house'], 'V1'):.3f} / {plug(hs[hs.variant == 'house'], 'E1'):.3f}",
         f"{plug(cs, 'V1'):.3f} / {plug(cs, 'E1'):.1e}"),
        ("random-8 r4 regret V1 / E1, mean (B)", f"{b4(hs[hs.variant == 'house'], 'V1', 'random').mean():.1f} / {b4(hs[hs.variant == 'house'], 'E1', 'random').mean():.1f}",
         f"{b4(cs, 'V1', 'random').mean():.1f} / {b4(cs, 'E1', 'random').mean():.1f}"),
        ("multi s0 r4, true-f HV / best-known", _r(f4h["hv_true_frac_best"]), _r(f4c["hv_true_frac_best"])),
        ("random vertices r4 p95 / plug-in spread", f"{Bh['vertices']['p95'][4]:.3f} / {Bh['plugin_spread']['p50'][4]:.3f}",
         f"{Bc['vertices']['p95'][4]:.3f} / {Bc['plugin_spread']['p50'][4]:.3f}"),
        ("BO − plug-in spread, r4", _r(eff_h, "{:+.3f}"), _r(eff_c, "{:+.3f}")),
        ("E1 inferred noise / committed σ_c", _r(E1nh, "{:.2f}"), _r(E1n, "{:.2f}")),
        ("E1 inferred noise / emulator noise (shrunk Σ_c sd)", _r(E1nh * sig["E1"] / emu_sd["E1"], "{:.2f}"), _r(E1e, "{:.2f}")),
        ("V1 inferred noise / committed σ_c", _r(V1nh, "{:.1f}"), _r(V1n, "{:.1f}")),
        ("V1 inferred noise / emulator noise", _r(V1nh * sig["V1"] / emu_sd["V1"], "{:.1f}"), _r(V1e, "{:.1f}")),
        ("single E1 designs at u = 0, r2–r4", f"{n0_house} of 72", f"{n0_r24} of {nt_r24}"),
        ("E1 rms z, median (single + multi)", f"{rzE_h.median():.2f}", f"{rzE_c.median():.2f}"),
        ("E1 C2 / C3 (single + multi cells)", "0 / 0", f"{po['E1']['C2']} / {po['E1']['C3']}"),
        ("V1 C2 / C3", "0 / 0", f"{po['V1']['C2']} / {po['V1']['C3']}"),
        ("E1 fit v2 converged / mode gap (nats)", "-", f"{int(conv.sum())}/{len(conv)} / {gaps.min():.1f}–{gaps.max():.1f}"),
        ("r1 unique designs across 5 lanes / duplicate r1 runs", f"{HX['seed_overlap']['per_round'][0]['n_unique']}/40 / "
         f"{HX['seed_overlap']['r1_duplicate_runs_of_40']}", f"{ov['per_round'][0]['n_unique']}/40 / {ov['r1_duplicate_runs_of_40']}"),
        ("min distance proposal → evaluated set (u)", f"{min(d['min_dist_to_evaluated'] for d in HX['seed_overlap']['min_dist']):.3f}",
         f"{min(d['min_dist_to_evaluated'] for d in ov['min_dist']):.3f}"),
        ("E1 fit time per fit (s) / multi round wall (s)", f"{fitE_h:.1f} / {wall_h:.1f}", f"{fitE_c:.1f} / {wall_c:.1f}"),
    ]
    A("| metric | house block (B) | committed block (A) |")
    A("|---|---|---|")
    for r in rows:
        A(f"| {r[0]} | {r[1]} | {r[2]} |")
    A("")
    A("## A.3 Calibration per objective (committed)\n")
    A(f"- E1 cov95 per batch (single seeds 0–2, r1–r4, then multi lanes): {', '.join(str(x) for x in po['E1']['cov95_batches'])}. "
      f"Multi path: minimum {cmE1min}, no C2.")
    A(f"- The one E1 C2 + C3 is the replicated-origin batch (single seed 0, r2). Mechanism: under-estimated noise at a replicate "
      f"(ρ = {rho:.2f}, replicate coverage {cov_rep:.2f}); P(C2) {pC2:.2f}, P(C3) {pC3:.3f} per batch by simulation. It is not a "
      "hull effect: every proposed design lies outside the start-set hull (`emulator_E_calib_hull_committed.csv`), and the "
      f"other out-of-hull E1 batches keep cov95 ≥ {int(min(c for c in po['E1']['cov95_batches'] if c != min(po['E1']['cov95_batches'])))} "
      "— far from the data the posterior variance dominates the band, so low noise alone does not break coverage. A "
      "replicate removes that posterior variance and exposes the noise estimate.")
    A(f"- Single-objective E1 replicate collapse: (designs at u = 0, unique) per round — {col_txt}.")
    A(f"- V1 cov95 per batch: all {sorted(set(po['V1']['cov95_batches']))} (house-fit bands ≈ {1 / po['V1']['rms_z_median']:.0f}× too wide).")
    A(f"- Noise references: `noise_over_sigma_c` divides by the committed σ_c (E1 {sig['E1']:,.0f}; V1 {sig['V1']:,.0f}); the "
      f"emulator adds the shrunk Σ_c sd (E1 {emu_sd['E1']:,.0f} = {emu_sd['E1'] / sig['E1']:.3f} σ_c; V1 {emu_sd['V1']:,.0f} = "
      f"{emu_sd['V1'] / sig['V1']:.3f} σ_c). Against the emulator noise: E1 {_r(E1e, '{:.2f}')}, V1 {_r(V1e, '{:.1f}')} "
      "(`*_noise_over_emulator` columns).")
    A(f"- E1 per-round fit v2: `mode_gap_v2` = best MAP minus the best restart outside the 1e-3·n-nat tolerance (54's "
      f"`mode_gap_nats`): {gaps.min():.1f}–{gaps.max():.1f} nats; best-vs-second restart (`gap_second_v2`) ≤ {gsec.max():.1e} nats.\n")
    A("![single committed](figs/fig_EMU_single_regret_committed.png)")
    A("![multi committed](figs/fig_EMU_multi_hv_committed.png)")
    A("![front committed](figs/fig_EMU_front_committed.png)")
    A("![calibration committed](figs/fig_EMU_calibration_committed.png)\n")
    A("### A.3.1 Lanes (committed)\n")
    A("| scen | seed | graded | true-f HV / best-known, r1–r4 | E1 cov95 r1–r4 | E1 noise/σ_c r1–r4 | E1 mode gap (nats) | wall s |")
    A("|---|---|---|---|---|---|---|---|")
    for (sc, s), g in cm.groupby(["scenario", "seed_id"]):
        g = g.sort_values("round")
        A(f"| {sc} | {s} | {len(g)}{' (HALT)' if sc == 's2' else ''} | {'/'.join(f'{x:.3f}' for x in g['hv_true_frac_best'])} | "
          f"{'/'.join(str(int(x)) for x in g['E1_cov95'])} | {'/'.join(f'{x:.2f}' for x in g['E1_noise_over_sigma_c'])} | "
          f"{'/'.join(('—' if pd.isna(x) else f'{x:.0f}') for x in g['E1_mode_gap_v2'])} | {'/'.join(f'{x:.1f}' for x in g['wall_s'])} |")
    A("")
    A("Mode gap \"—\" = every finite restart lies within the 1e-3·n-nat tolerance of the best (one mode found).\n")
    A("## A.4 Matched-budget baselines and seed overlap (committed truth)\n")
    A("| baseline | r4 p5 / p50 / p95 | r4 max |")
    A("|---|---|---|")
    for name in ("uniform", "vertices", "plugin_random", "plugin_spread"):
        b = Bc[name]
        A(f"| {R.BASE_NAMES[name]} | {b['p5'][4]:.3f} / {b['p50'][4]:.3f} / {b['p95'][4]:.3f} | {b['max'][4]:.3f} |")
    A(f"| qNEHVI s0 (5 lanes) | {_r(f4c['hv_true_frac_best'])} | {f4c['hv_true_frac_best'].max():.3f} |")
    A("")
    bk = X["best_known"]
    A(f"Best-known front (committed truth): HV {bk['hv_best_known']:.5g} = {bk['best_over_polished']:.4f} × polished; Sobol "
      f"reference {bk['sobol_over_best']:.3f} of best-known (not a front). Seed overlap: r1 {ov['per_round'][0]['n_unique']}/40 "
      f"unique ({ov['per_round'][0]['frac_exact_vertex']:.0%} exact vertices), r2–r4 "
      f"{'/'.join(str(r['n_unique']) for r in ov['per_round'][1:])} of 40; Jaccard {ov['jaccard_range'][0]:.2f}–"
      f"{ov['jaccard_range'][1]:.2f}; minimum proposal distance to the evaluated set "
      f"{min(d['min_dist_to_evaluated'] for d in ov['min_dist']):.3f} (no re-proposal). {ov['statement']}\n")
    A("## A.5 Model-mismatch check (non-circular; 1 seed each)\n")
    A("The main run puts the same fit on both sides (truth and BO GP), which flatters the BO. Two checks break that symmetry.\n")
    A("| run | truth V1 / E1 | BO GP V1 / E1 | single r4 regret V1 / E1 (B) | multi s0 seed 0 HV / best-known, r4 | C2 (single + multi) |")
    A("|---|---|---|---|---|---|")
    for v, tv in (("committed", "house / v2"), ("mmA", "house / house"), ("mmB", "v2 (EXPLORATORY) / v2")):
        sv = sdf[(sdf.variant == v) & (sdf.method == "bo") & (sdf.seed_id == 0) & (sdf["round"] == 4)].set_index("objective")
        mv = mdf[(mdf.variant == v) & (mdf.scenario == "s0") & (mdf.seed_id == 0) & (mdf["round"] == 4)]
        sc2 = int(sdf[(sdf.variant == v) & (sdf.method == "bo") & (sdf.seed_id == 0)]["C2"].fillna(False).astype(bool).sum())
        mc2 = int(mdf[(mdf.variant == v) & (mdf.scenario == "s0") & (mdf.seed_id == 0)]["C2"].fillna(False).astype(bool).sum())
        A(f"| {LABEL[v].split(' (')[0]} | {tv} | house / v2 | {sv.loc['V1', 'regret_best_obs_B']:.3f} / {sv.loc['E1', 'regret_best_obs_B']:.3f} | "
          f"{float(mv['hv_true_frac_best'].iloc[0]):.3f} | {sc2} + {mc2} |")
    mb = sdf[(sdf.variant == "mmB") & (sdf.objective == "V1") & (sdf.method == "bo")].sort_values("round")
    A("")
    A("| truth | random vertices r4 p95 | r0 plug-in spread r4 | BO multi s0 seed 0, r4 |")
    A("|---|---|---|---|")
    for lab, XX, mv in (("committed", X, float(f4c[f4c.seed_id == 0]["hv_true_frac_best"].iloc[0])), ("mismatch A", XA, mvA),
                        ("mismatch B", XB, mvB)):
        A(f"| {lab} | {XX['baselines']['vertices']['p95'][4]:.3f} | {XX['baselines']['plugin_spread']['p50'][4]:.3f} | {mv:.3f} |")
    A("")
    A(f"Non-circular evidence (mismatch B, V1): the r0 plug-in regret is {pmr[0]:.2f} B; BO's minimum true f among evaluated "
      f"designs reaches {mfe[2]:.3f} B by r2; the posterior-mean optimum regret goes {pmr[2]:.3f} → {pmr[4]:.3f} B (r2 → r4). The "
      f"rising best-observed regret ({dB['records'][2]['regret_best_obs_B']:.3f} → {dB['records'][4]['regret_best_obs_B']:.3f} B) is "
      f"winner's curse on noisy incumbents: the best observation's noise is {nz[3]:+.2f} and {nz[4]:+.2f} chatter sd at r3 / r4. "
      "The house GP does not mis-steer. **Recommendation for the real campaign: report incumbents by posterior mean or by "
      "replicates, not by best observed. A V1 misfit will be invisible to C2/C3.**\n")
    A(f"Reading: with the truth fitted differently from the BO GP, the search still reaches the vertex optima. Mismatch B is the "
      f"hardest case for V1: the fit-v2 V1 truth puts f* at the all-PEM vertex ({Pv['objectives']['V1']['f_star'] / 1e6:.3f} TWh, "
      f"{(Pv['objectives']['V1']['y_train_min'] - Pv['objectives']['V1']['f_star']) / em.B['V1']:.0f} B below the data) and the "
      f"house-fit V1 GP has to find it: regret by round {'/'.join(f'{x:.3f}' for x in mb['regret_best_obs_B'])} B (r0 plug-in "
      f"{float(mb['r0_plugin_regret_B'].iloc[0]):.2f} B); after r2 the best-observed design drifts (a low noisy "
      f"observation at a worse design), while the posterior-mean optimum reaches {float(mb['regret_pm_opt_B'].iloc[-1]):.3f} B by r4. Mismatch A (house E1 truth, fit-v2 E1 GP) gives E1 regret "
      f"{float(sdf[(sdf.variant == 'mmA') & (sdf.objective == 'E1') & (sdf.method == 'bo') & (sdf['round'] == 4)]['regret_best_obs_B'].iloc[0]):.3f} B "
      "and no C2. In mismatch B the E1 truth, E1 GP and noise stream equal the committed run, so its single E1 trajectory "
      "(and its one C2 at r2) is the committed one; the mismatch there is V1 only. The multi-objective mismatch lanes raise no "
      "C2. Each mismatch is scored against the best-known front of its own truth (`EMU_extras_mmA.json`, "
      "`EMU_extras_mmB.json`).\n")
    A("## A.6 55 change for this block\n")
    A(f"- `{R._sha('methods_E(66 v2 hook')}` (methods_E 66 v2 hook): `common_E.gp_fitters` reads `fit_definition` per objective; `qnehvi_E.ObjGP(fitter=v2)` "
      "runs 54's `FitV2` on raw u and copies the MAP hyperparameters into the float64 SingleTaskGP (lengthscale / sx, negated "
      "constant); `fit_info` (converged, mode gap, noise / σ_c) goes into every round record. The house path is unchanged. A "
      "test checks that the hook reproduces FitV2's posterior mean and sd on synthetic 6-D data.")
    A("- The house block (B) reads `committed_configs_housefit.json`, so it stays house-fit end to end.\n")
    A("## A.7 Remaining 55 Part B items (unchanged list, status after this block)\n")
    A("1. Fit v2 in `qnehvi_E` per `fit_definition`: **done (hook)**; per-round convergence flag recorded (not yet a gate).")
    A("2. New `committed_configs.json`: **landed (240bde1)**. E-D7 still null — the Part B guard (refuses a provisional tier) applies.")
    A(f"3. **Duplicate / replicate rule (direct evidence now):** single-objective E1 with the v2 GP and noisy EI put {n0_r24} of "
      f"{nt_r24} r2–r4 designs on the incumbent u = 0. The 55 multi path did not replicate here, but nothing prevents it; the "
      "re-proposal assert in `propose_round` would stop a lane that does. Declare the rule (replicate allowed, or re-optimize "
      "the slot) before launch.")
    A("4. Still open: idempotent grading + commit before propose; E-D5 amendment; `arms_E.json` complete "
      "(`gp.train` text, `part = \"B\"`, R3 / N3 / N1_off wired); τ_res into the ledger; stale README / runbook text; "
      "`dry_round_E.py` alignment + tests for the c7576a6 branches; real-loader ingest test on a fake methods_E wave; Kay's "
      f"duplicate-run decision (≈ {ov['r1_duplicate_runs_of_40']} of 40 r1 runs); CRC `--check-env` / `GAP_DECISION` / "
      "`--dry-run`, one lane first; what a C2 REVIEW flag on a replicated design means (noise estimate, not model failure).\n")
    A("---\n")
    A("# B. House-fit block (first run, kept as run)\n")
    A("Written before fit v2 landed. Section A supersedes B.0 items 3–4 (the v2 rerun is done) and adds the per-objective "
      "gate-power statement. Numbers in B are the house-fit run as committed.\n")
    return L
