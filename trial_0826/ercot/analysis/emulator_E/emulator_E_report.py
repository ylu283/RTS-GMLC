#!/usr/bin/env python3
"""Prompt 66 — collect / figs / report for the EMULATOR BO dry run.

    PY=/opt/anaconda3/envs/bogp-botorch/bin/python
    $PY analysis/emulator_E/emulator_E_report.py collect    # -> emulator_E_single.csv, emulator_E_multi.csv, emulator_E_summary.json
    $PY analysis/emulator_E/emulator_E_report.py figs       # assert-before-draw against the CSVs, then figs/
    $PY analysis/emulator_E/emulator_E_report.py report     # -> EMULATOR_BO.md (regenerated in full)

Reads only committed files (runs_compact/, waves/, lanes/, emulator_E_params.json), so a clean checkout
reproduces every figure and the report. Everything here is EMULATOR output (prompt 66): a machinery check.
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import subprocess
import sys

import numpy as np
import pandas as pd
from scipy.stats import poisson

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import emulator_E as em  # noqa: E402

SINGLE_CSV = os.path.join(HERE, "emulator_E_single.csv")
MULTI_CSV = os.path.join(HERE, "emulator_E_multi.csv")
HULL_CSV = os.path.join(HERE, "emulator_E_calib_hull.csv")
SUMMARY = os.path.join(HERE, "emulator_E_summary.json")
MD = os.path.join(HERE, "EMULATOR_BO.md")
C2_RATE, C3_RATE = 3.7e-4, 1.1e-6
SEEDS_MULTI = (0, 1, 2, 3, 4)
BASE_NAMES = {"uniform": "i.i.d. uniform", "vertices": "random box vertices", "plugin_random": "r0 plug-in front, random 32",
              "plugin_spread": "r0 plug-in front, spread (no exploration)"}


def _load(p):
    with open(p) as f:
        return json.load(f)


def _runs(variants=("house", "long")):
    single = [d for d in (_load(p) for p in sorted(glob.glob(os.path.join(em.RUNS, "single", "EMU_single_*.json"))))
              if d["variant"] in variants]
    multi = [d for d in (_load(p) for p in sorted(glob.glob(os.path.join(em.RUNS, "multi", "EMU_multi_*.json"))))
             if d["variant"] in variants]
    return single, multi


def _extras():
    return _load(os.path.join(em.RUNS, "EMU_extras.json"))


# --------------------------------------------------------------------------- #
# collect
# --------------------------------------------------------------------------- #

def collect():
    P = _load(em.PARAMS)
    front = _load(os.path.join(em.RUNS, "EMU_front.json"))
    pool = _load(os.path.join(em.RUNS, "EMU_random_pool.json"))
    X = _extras()
    hb = X["best_known"]["hv_best_known"]
    npz_p = os.path.join(em.RUNS_BIG, "EMU_random_pool_subsets.npz")
    npz = np.load(npz_p) if os.path.isfile(npz_p) else None
    sites = P["sites"]
    single, multi = _runs()
    rows = []
    for d in single:
        r0 = d["records"][0]
        ls0 = np.asarray(r0["gp"]["ls_u"], float) if "gp" in r0 else None
        ls_emu = np.asarray(P["objectives"][d["objective"]]["ls_std"], float) * np.asarray(P["objectives"][d["objective"]]["sx"], float)
        plug = X["r0_plugin"][d["variant"]]["objectives"][d["objective"]]["regret_B"]
        for r in d["records"]:
            row = {"label": "EMULATOR", "variant": d["variant"], "fit_epochs": d["fit_epochs"], "objective": d["objective"],
                   "method": d["method"], "seed_id": d["seed_id"], "round": r["round"], "n": r["n"],
                   "acq_seed": r.get("seed"), "best_obs": r["best_obs"], "f_at_best_obs": r["f_at_best_obs"],
                   "f_star": d["f_star"], "B": d["B"], "regret_best_obs_B": r["regret_best_obs_B"],
                   "gap_obs_B": r["gap_obs_B"], "min_f_evaluated_B": r["min_f_evaluated_B"],
                   "regret_pm_opt_B": r.get("regret_pm_opt_B"), "pm_opt_f": r.get("pm_opt_f"),
                   "r0_plugin_regret_B": r0.get("regret_pm_opt_B", plug), "r0_plugin_regret_common_fit_B": plug}
            c = r.get("calibration")
            if c:
                row.update({"cov95": c["cov95"], "rms_z": c["rms_z"], "mean_z": c["mean_z"],
                            "n_abs_z_gt3": c["n_abs_z_gt3"], "C2": c["C2"], "C3": c["C3"]})
            g = r.get("gp")
            if g:
                ls = np.asarray(g["ls_u"], float)
                row.update({f"ls_u_{s}": v for s, v in zip(sites, ls)})
                row.update({"ls_drift_vs_r0_max": float(np.max(np.abs(ls / ls0 - 1))),
                            "ls_ratio_vs_emulator_max": float(np.max(np.abs(ls / ls_emu - 1))),
                            "outputscale_sd_t": g["outputscale_sd_t"], "noise_sd_raw": g["noise_sd_raw"],
                            "loo_rms_z": g["loo_rms_z"]})
            bs = r.get("bound_snaps") or {}
            row.update({"acq_s": r.get("acq_s"), "fit_s": r.get("fit_s"), "wall_s": r.get("wall_s"),
                        "acq_warnings": sum((r.get("acq_warnings") or {}).values()) if r["round"] else None,
                        "bound_snaps_to_0": bs.get("to_0"), "bound_snaps_to_1": bs.get("to_1"),
                        "mode_gap_v2": np.nan})
            rows.append(row)
    sdf = pd.DataFrame(rows).sort_values(["variant", "objective", "method", "seed_id", "round"])
    sdf.to_csv(SINGLE_CSV, index=False, float_format="%.10g")

    hvF, hvP = front["hv_front"], front["hv_front_polished"]
    B = X["baselines"]
    mrows = []
    for d in multi:
        plug = X["r0_plugin"][d["variant"]]["objectives"]
        base = {"label": "EMULATOR", "variant": d["variant"], "fit_epochs": d["fit_epochs"], "scenario": d["scenario"],
                "seed_id": d["seed_id"], "tau_exact_joint": d["tau_exact"]["tau_joint"],
                "budget_cap_only": d["tau_exact"]["budget_cap_only"], "tau_res": d["tau_res"]["tau_res"],
                "n0_tier": d["n0_tier"], "loader": d["loader"], "configs_source": d["configs_source"],
                "r0_plugin_regret_V1_B": plug["V1"]["regret_B"], "r0_plugin_regret_E1_B": plug["E1"]["regret_B"],
                "mode_gap_v2": np.nan}
        mrows.append({**base, "round": 0, "n": 48, "n_hv": 48, "hv": d["hv0"], "hv_true_f": d["hv0_true_f"],
                      "hv_true_frac_best": d["hv0_true_f"] / hb, "hv_obs_frac_best": d["hv0"] / hb,
                      "hv_true_frac_polished": d["hv0_true_f"] / hvP, "hv_true_frac_sobol": d["hv0_true_f"] / hvF,
                      "wall_s": d["init_s"]})
        for r in d["rounds"]:
            if "hv" not in r:
                mrows.append({**base, "round": r["round"], "propose_refused": r.get("propose_refused"),
                              "C1_ok": r.get("C1_ok")})
                continue
            k = r["round"]
            fb = r["hv_true_f"] / hb
            st = (d["settings"].get(str(k)) or {}).get("bound_snaps") or {}
            row = {**base, "round": k, "n": r["n"], "n_hv": r["n_hv"], "hv": r["hv"], "hv_true_f": r["hv_true_f"],
                   "gain": r["gain"], "gain_over_tau_res": r["gain_over_tau_res"], "gain_tau_joint": r["gain_tau_joint"],
                   "would_stop_joint": r["would_stop_joint"], "would_stop_marginal": r["would_stop_marginal"],
                   "hv_true_frac_best": fb, "hv_obs_frac_best": r["hv"] / hb,
                   "hv_true_frac_polished": r["hv_true_f"] / hvP, "hv_true_frac_sobol": r["hv_true_f"] / hvF,
                   "effect_vs_uniform_p95": fb - B["uniform"]["p95"][k], "effect_vs_vertices_p95": fb - B["vertices"]["p95"][k],
                   "effect_vs_plugin_random_p95": fb - B["plugin_random"]["p95"][k],
                   "effect_vs_plugin_spread": fb - B["plugin_spread"]["p50"][k],
                   "p_random_prompt34_saturated": em.percentile(r["hv"], npz[f"k{k}"]) if npz is not None else np.nan,
                   "C1_ok": r["C1_ok"], "C2": r["C2"], "C3": r["C3"], "n_violations": len(r["violations"]),
                   "n_suspects": len(r["suspects"]), "guardrail_mode_after": r["guardrail_mode_after"],
                   "constraint_used": r["constraint_used"], "halt": r["halt"], "r2_flag": r["r2_flag"],
                   "r2_max": r["r2_max"], "n1_off_flag_a": r["n1_off_flag_a"], "n1_off_max": r["n1_off_max"],
                   "N4_mean": r["N4_mean"], "propose_s": r["propose_s"], "qnehvi_s": r["qnehvi_s"],
                   "grade_s": r["grade_s"], "wall_s": r["wall_s"],
                   "propose_warnings": sum((r.get("propose_warnings") or {}).values()),
                   "bound_snaps_to_0": st.get("to_0"), "bound_snaps_to_1": st.get("to_1")}
            for o in em.SEATED:
                c = (r.get("calibration") or {}).get(o, {})
                row.update({f"{o}_cov95": c.get("cov95"), f"{o}_rms_z": c.get("rms_z"), f"{o}_mean_z": c.get("mean_z"),
                            f"{o}_n_abs_z_gt3": c.get("n_abs_z_gt3")})
                row[f"{o}_loo_rms_z_pre"] = (r.get("loo_rms_z") or {}).get(o)
                row[f"{o}_noise_raw_pre"] = (r.get("noise_raw") or {}).get(o)
            if k == 4 and npz is not None:
                ps = np.array([em.percentile(r["hv"], b) for b in npz["boot"]])
                row["p_random_lo"], row["p_random_hi"] = float(np.percentile(ps, 5)), float(np.percentile(ps, 95))
            mrows.append(row)
    mdf = pd.DataFrame(mrows).sort_values(["variant", "scenario", "seed_id", "round"])
    mdf.to_csv(MULTI_CSV, index=False, float_format="%.10g")
    summ = summarize(P, front, pool, X, sdf, mdf, single, multi)
    with open(SUMMARY, "w") as f:
        json.dump(summ, f, indent=1, default=float)
        f.write("\n")
    print(json.dumps(summ["pass_fail"], indent=1, default=str))
    return sdf, mdf, summ


def summarize(P, front, pool, X, sdf, mdf, single, multi):
    pf = []
    hs = sdf[(sdf.variant == "house")]
    exp_single = {(o, m, s) for o in em.SEATED for m in ("bo", "random") for s in em.SEED_IDS_SINGLE}
    got_single = {(d["objective"], d["method"], d["seed_id"]) for d in single if d["variant"] == "house"}
    exp_multi = {(sc, s) for sc in em.SCEN for s in SEEDS_MULTI}
    got_multi = {(d["scenario"], d["seed_id"]) for d in multi if d["variant"] == "house"}
    hm = mdf[(mdf.variant == "house") & (mdf["round"] >= 1) & mdf["hv"].notna()]
    ends = {(d["scenario"], d["seed_id"]): [r["round"] for r in d["rounds"] if "hv" in r] for d in multi if d["variant"] == "house"}
    ok_ends = all((ends[k] == [1, 2, 3, 4]) if k[0] in ("s0", "s1") else (ends[k] == [1]) for k in ends)
    pf.append({"n": 1, "check": "No crash: 12 single-objective house runs and 15 multi-objective house lanes finish; each lane "
                                "ends where its scenario says",
               "result": f"{len(got_single)}/12, {len(got_multi)}/15, ends as expected",
               "pass": bool(got_single == exp_single and got_multi == exp_multi and ok_ends),
               "verdict": "PASS after a 55 fix. As built, the multi-seed init CRASHED at seed 1 (section 7, change 2c)"})
    c1 = mdf[(mdf["round"] >= 1) & mdf["C1_ok"].notna()]["C1_ok"].astype(bool)
    pf.append({"n": 2, "check": "C1 ingest passes on every emulated round (55 `ingest_gate`)",
               "result": f"{int(c1.sum())}/{len(c1)} rounds", "pass": bool(c1.all() and len(c1) > 0), "verdict": "PASS"})
    sb = hs[(hs.method == "bo") & (hs["round"] >= 1)]
    n_so = len(sb)
    c2_so, c3_so = int(sb["C2"].astype(bool).sum()), int(sb["C3"].astype(bool).sum())
    n_mo = len(hm) * len(em.SEATED)
    c2_mo = int(sum((hm[f"{o}_cov95"] <= 4).sum() for o in em.SEATED))
    c3_mo = int(sum((hm[f"{o}_n_abs_z_gt3"] >= 3).sum() for o in em.SEATED))
    e2, e3 = (n_so + n_mo) * C2_RATE, (n_so + n_mo) * C3_RATE
    lim2, lim3 = int(poisson.ppf(0.95, e2)), int(poisson.ppf(0.95, e3))
    lng = sdf[(sdf.variant == "long") & (sdf.method == "bo") & (sdf["round"] >= 1)]
    pf.append({"n": 3, "check": "C2/C3 flag counts at or below nominal (Poisson 95 % limit of the expected count)",
               "result": f"C2 {c2_so + c2_mo}, C3 {c3_so + c3_mo} in {n_so + n_mo} (round, objective) cells; expected C2 {e2:.3f}",
               "pass": bool(c2_so + c2_mo <= lim2 and c3_so + c3_mo <= lim3),
               "verdict": "PASS — NO POWER. The Poisson limit is 0 flags, and the house-fit bands are 2–6× too wide (§4.3). "
                          f"With a converged-fit proxy, C2 fires {int(lng['C2'].astype(bool).sum())} times (§5)."})
    within, beats = {}, {}
    for o in em.SEATED:
        b4 = hs[(hs.objective == o) & (hs.method == "bo") & (hs["round"] == 4)].set_index("seed_id")["regret_best_obs_B"]
        r4 = hs[(hs.objective == o) & (hs.method == "random") & (hs["round"] == 4)].set_index("seed_id")["regret_best_obs_B"]
        within[o] = int((b4 <= 2.0).sum())
        beats[o] = {"bo_mean": float(b4.mean()), "random_mean": float(r4.mean()),
                    "per_seed": {int(s): bool(b4[s] < r4[s]) for s in b4.index}}
    pf.append({"n": 4, "check": "Single-objective BO within 2 B_j of the emulator optimum by round 4 on >= 2 of 3 seeds",
               "result": "; ".join(f"{o} {within[o]}/3" for o in em.SEATED), "pass": all(v >= 2 for v in within.values()),
               "verdict": "PASS (easy case: both optima are box vertices, and optimize_acqf goes to vertices)"})
    pf.append({"n": 5, "check": "Single-objective BO beats random-8 at matched budget (round 4, 80 evaluations) on every objective",
               "result": ("On this emulator, where both optima are box vertices outside the data hull: "
                          f"V1 {beats['V1']['bo_mean']:.2f} B vs {beats['V1']['random_mean']:.1f} B; "
                          f"E1 {beats['E1']['bo_mean']:.3f} B vs {beats['E1']['random_mean']:.1f} B; every seed. "
                          "Uniform draws in [0,1]^6 almost never reach a vertex, so this gap does not predict the gap on PCM."),
               "pass": all(b["bo_mean"] < b["random_mean"] and all(b["per_seed"].values()) for b in beats.values()),
               "verdict": "PASS"})

    def lane(sc, s, v="house"):
        return next(d for d in multi if d["scenario"] == sc and d["seed_id"] == s and d["variant"] == v)
    s0_ok = all(lane("s0", s)["guardrail_mode"] == "monitor" and not lane("s0", s)["halt"] for s in SEEDS_MULTI)
    s1_ok = all(lane("s1", s)["guardrail_flipped_at_round"] == 1
                and all("shed <=" in (lane("s1", s)["settings"][str(k)] or {}).get("constraint", "") for k in (2, 3, 4))
                and (lane("s1", s)["settings"]["1"] or {}).get("constraint") == "none"
                and [r["n_hv"] for r in lane("s1", s)["rounds"]] == [55, 63, 71, 79] for s in SEEDS_MULTI)
    s2_ok = all(lane("s2", s)["halt"] and lane("s2", s)["halt_file"]
                and "HALT" in (lane("s2", s)["rounds"][-1].get("propose_refused") or "") for s in SEEDS_MULTI)
    pf.append({"n": 6, "check": "Multi s0 (clean): 4 rounds, monitor mode, no halt, 5 lanes", "result": "yes" if s0_ok else "NO",
               "pass": s0_ok, "verdict": "PASS" if s0_ok else "FAIL"})
    pf.append({"n": 7, "check": "Multi s1 (one shed violation in r1): mode flips at r1; r2–r4 constrained qNEHVI with the shed GP; "
                                "the violating run is out of HV (n_hv 55/63/71/79); 5 lanes",
               "result": "yes" if s1_ok else "NO", "pass": s1_ok, "verdict": "PASS" if s1_ok else "FAIL"})
    pf.append({"n": 8, "check": "Multi s2 (two violations in r1): `HALT_FOR_DECISION.md` written; `propose --round 2` refused; 5 lanes",
               "result": "yes" if s2_ok else "NO", "pass": s2_ok, "verdict": "PASS" if s2_ok else "FAIL"})
    ws = mdf[(mdf["round"] >= 1) & mdf["hv"].notna()]
    tz = all(d["tau_exact"]["budget_cap_only"] and d["tau_exact"]["tau_joint"] == 0 for d in multi)
    tz2 = bool(tz and (~ws["would_stop_joint"].astype(bool)).all() and ws["gain_tau_joint"].isna().all())
    pf.append({"n": 9, "check": "tau_exact = 0 -> budget-cap-only: gain/tau_exact null, would_stop never fires, every lane runs to the cap",
               "result": "yes" if tz2 else "NO", "pass": tz2, "verdict": "PASS" if tz2 else "FAIL"})
    mon = bool((~ws["r2_flag"].astype(bool)).all() and (~ws["n1_off_flag_a"].astype(bool)).all())
    pf.append({"n": 10, "check": "R2 and N1_off monitors at base + chatter raise no flag",
               "result": f"R2 max {ws['r2_max'].max():.1f} MWh (< 312.16); N1_off max {ws['n1_off_max'].max():,.0f} (dN1_off < 462.7)",
               "pass": mon, "verdict": "PASS" if mon else "FAIL"})
    hm4 = mdf[(mdf.variant == "house") & (mdf["round"] == 4) & (mdf.scenario == "s0")]["hv_true_frac_best"]
    pf.append({"n": 11, "check": "HV fraction of the best-known emulator front reported (no threshold)",
               "result": f"s0 round 4, true f: {hm4.min():.3f}–{hm4.max():.3f} of the best-known front. The reference is a lower "
                         "bound on the true front, so these fractions are upper bounds",
               "pass": True, "verdict": "reported"})
    return {"label": "EMULATOR", "pass_fail": pf, "within_2B": within, "beats_random": beats,
            "c_counts": {"single_C2": c2_so, "single_C3": c3_so, "multi_C2": c2_mo, "multi_C3": c3_mo,
                         "n_single": n_so, "n_multi": n_mo, "expected_C2": e2, "expected_C3": e3,
                         "long_single_C2": int(lng["C2"].astype(bool).sum()), "long_single_C3": int(lng["C3"].astype(bool).sum())},
            "s0_r4_frac_best": [float(hm4.min()), float(hm4.max())],
            "hv_front_sobol": front["hv_front"], "hv_front_polished": front["hv_front_polished"],
            "hv_best_known": X["best_known"]["hv_best_known"],
            "hv_random48_obs": pool["hv_all48_obs"], "hv_random48_true": pool["hv_all48_true"]}


# --------------------------------------------------------------------------- #
# figs (assert-before-draw)
# --------------------------------------------------------------------------- #

def _plt():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.size": 12, "font.weight": "bold", "axes.labelweight": "bold",
                         "axes.titleweight": "bold", "legend.title_fontsize": 10})
    return plt


def _bold(ax):
    ax.figure.canvas.draw()
    for t in ax.get_xticklabels() + ax.get_yticklabels():
        t.set_fontweight("bold")
    ax.grid(alpha=0.3)


def _assert_frozen(sdf, mdf):
    """Recompute every plotted number from the committed run files and the frozen emulator; assert == CSV."""
    emu = em.load_emulator()
    single, multi = _runs()
    X = _extras()
    hb = X["best_known"]["hv_best_known"]
    n = 0
    for d in single:
        f = emu["f"][d["objective"]]
        for r in d["records"]:
            row = sdf[(sdf.variant == d["variant"]) & (sdf.objective == d["objective"]) & (sdf.method == d["method"])
                      & (sdf.seed_id == d["seed_id"]) & (sdf["round"] == r["round"])]
            assert len(row) == 1
            reg = (f(np.asarray([r["best_obs_u"]]))[0] - d["f_star"]) / d["B"]
            assert abs(reg - float(row["regret_best_obs_B"].iloc[0])) <= 1e-6 * max(1.0, abs(reg)), (d["objective"], reg)
            n += 1
    P = emu["P"]
    Y0 = np.asarray(P["start_set"]["y_obs"], float)
    F0 = np.asarray(P["start_set"]["f"], float)
    R = emu["R"]
    for d in multi:
        Ya, Fa = [Y0], [F0]
        for r in d["rounds"]:
            if "hv" not in r:
                continue
            k = r["round"]
            w = f"methods_E_EMU_{d['variant']}_{d['scenario']}_s{d['seed_id']}_r{k}"
            tab = pd.read_csv(os.path.join(HERE, "waves", w, "objectives_EMULATOR.csv"), float_precision="round_trip")
            ok = tab["R1"].to_numpy(float) <= 1.0
            Ya.append(tab[["V1", "E1"]].to_numpy(float)[ok])
            dm = pd.read_csv(os.path.join(HERE, "waves", w, "design_matrix.csv"), float_precision="round_trip").sort_values("index")
            U = dm[[c for c in dm.columns if c.startswith("u_")]].to_numpy(float)
            assert not np.any((U > 0) & (U < 1e-9)), (w, "near-zero site")
            Fa.append(em.true_f(U)[ok])
            row = mdf[(mdf.variant == d["variant"]) & (mdf.scenario == d["scenario"]) & (mdf.seed_id == d["seed_id"])
                      & (mdf["round"] == k)]
            hv, hvt = em.hv2d(np.vstack(Ya), R), em.hv2d(np.vstack(Fa), R)
            assert abs(hv - float(row["hv"].iloc[0])) <= 1e-9 * hv, (w, hv)
            assert abs(hvt / hb - float(row["hv_true_frac_best"].iloc[0])) <= 1e-8, (w, hvt)
            n += 1
    bk = np.asarray(X["best_known"]["front"], float)
    assert abs(em.hv2d(bk, R) - hb) <= 1e-9 * hb
    return n


def figs():
    plt = _plt()
    sdf = pd.read_csv(SINGLE_CSV)
    mdf = pd.read_csv(MULTI_CSV)
    hull = pd.read_csv(HULL_CSV)
    n = _assert_frozen(sdf, mdf)
    print(f"assert-before-draw: {n} plotted values recomputed from the committed run files == CSV")
    os.makedirs(em.FIGS, exist_ok=True)
    X = _extras()
    out = []
    marks = {0: "o", 1: "s", 2: "^"}
    floor = 1e-3
    # 1 single-objective regret
    fig, axes = plt.subplots(1, 2, figsize=(14, 4.8))
    for ax, o in zip(axes, em.SEATED):
        for (var, meth), sty in {("house", "bo"): dict(color="C0", lw=2.0, ls="-"),
                                 ("long", "bo"): dict(color="C2", lw=1.5, ls=":"),
                                 ("house", "random"): dict(color="0.45", lw=1.5, ls="--")}.items():
            g = sdf[(sdf.objective == o) & (sdf.variant == var) & (sdf.method == meth)]
            assert g["seed_id"].nunique() == 3 and g["regret_best_obs_B"].notna().all()
            for s, gs in g.groupby("seed_id"):
                lab = {"bo": f"BO qLogNEI, {'long fit (exploratory, 10,000 steps)' if var == 'long' else 'house fit'}",
                       "random": "random-8 (uniform u)"}[meth]
                ax.plot(gs["round"], np.maximum(gs["regret_best_obs_B"], floor), marker=marks[s], ms=5,
                        label=f"{lab}, seed {s}", **sty)
                for _, rr in gs[gs["regret_best_obs_B"] < floor].iterrows():
                    ax.annotate(f"{rr['regret_best_obs_B']:.1e} (drawn at floor)", (rr["round"], floor), xytext=(-60, 14),
                                textcoords="offset points", fontsize=8, fontweight="bold", arrowprops=dict(arrowstyle="->"))
        plug = float(sdf[(sdf.objective == o) & (sdf.variant == "house") & (sdf.method == "bo")]["r0_plugin_regret_B"].iloc[0])
        ax.axhline(max(plug, floor), color="C1", lw=1.4, ls="--", label="r0 plug-in optimum (start-set GP, house fit)")
        ax.axhline(2.0, color="C3", lw=1.4, ls="-.", label="2 B_j")
        ax.set_yscale("log")
        ax.set_xticks([0, 1, 2, 3, 4])
        ax.set_xlabel("Round (8 designs per round)")
        ax.set_ylabel(f"Regret of best observed, {o} (B units)")
        ax.set_title(f"{o}: B = " + ("18,739 MWh" if o == "V1" else "$1.862M"))
        _bold(ax)
    h, l = axes[0].get_legend_handles_labels()
    fig.legend(h, l, loc="center left", bbox_to_anchor=(1.0, 0.5), fontsize=8.5)
    fig.suptitle(f"EMULATOR — single-objective regret (floor {floor:g} for display)", fontweight="bold")
    fig.tight_layout()
    p = os.path.join(em.FIGS, "fig_EMU_single_regret.png")
    fig.savefig(p, dpi=150, bbox_inches="tight")
    plt.close(fig)
    out.append(p)
    # 2 multi: TRUE-f fraction of the best-known front + matched-budget bands
    fig, ax = plt.subplots(figsize=(9, 5.2))
    ks = [0, 1, 2, 3, 4]
    for name, col in (("uniform", "0.6"), ("vertices", "C4"), ("plugin_random", "C1")):
        b = X["baselines"][name]
        ax.fill_between(ks, b["p5"], b["p95"], color=col, alpha=0.3, label=f"{BASE_NAMES[name]}: 5–95 % ({b['n_rep']} reps)")
    ax.plot(ks, X["baselines"]["plugin_spread"]["p50"], color="C1", lw=2, ls="-.", marker="D", ms=4,
            label=BASE_NAMES["plugin_spread"])
    for (sc, var), sty in {("s0", "house"): dict(color="C0", lw=2), ("s1", "house"): dict(color="C9", lw=1.5, ls="--"),
                           ("s0", "long"): dict(color="C2", lw=1.5, ls=":")}.items():
        g = mdf[(mdf.scenario == sc) & (mdf.variant == var) & mdf["hv"].notna()]
        assert len(g) > 0 and g["hv_true_frac_best"].between(0, 1 + 1e-12).all()
        for i, (s, gs) in enumerate(g.groupby("seed_id")):
            ax.plot(gs["round"], gs["hv_true_frac_best"], marker="o", ms=4,
                    label=(f"qNEHVI {sc}, {'long fit (exploratory)' if var == 'long' else 'house fit'}" if i == 0 else None), **sty)
    g2 = mdf[(mdf.scenario == "s2") & mdf["hv"].notna() & (mdf["round"] == 1)]
    ax.scatter(g2["round"], g2["hv_true_frac_best"], marker="x", s=50, c="C3", zorder=5,
               label="qNEHVI s2 (HALT after r1; 2 runs out of HV)")
    ax.axhline(X["best_known"]["sobol_over_best"], color="C3", ls=":", lw=1.2, label="Sobol 2^14 reference (not a front)")
    ax.set_xticks(ks)
    ax.set_xlabel("Round")
    ax.set_ylabel("True-f HV / HV(best-known front)")
    ax.set_title("EMULATOR — multi-objective (55 machinery) vs matched-budget baselines")
    ax.legend(fontsize=8.5, loc="center left", bbox_to_anchor=(1.01, 0.5))
    _bold(ax)
    fig.tight_layout()
    p = os.path.join(em.FIGS, "fig_EMU_multi_hv.png")
    fig.savefig(p, dpi=150, bbox_inches="tight")
    plt.close(fig)
    out.append(p)
    # 3 objective space
    P = _load(em.PARAMS)
    F0 = np.asarray(P["start_set"]["f"], float)
    front = _load(os.path.join(em.RUNS, "EMU_front.json"))
    bk = np.asarray(X["best_known"]["front"], float)
    fs = np.asarray(front["front"], float)
    pool = _load(os.path.join(em.RUNS, "EMU_random_pool.json"))
    Fp = np.asarray(pool["f"], float)
    vmin_obs = P["objectives"]["V1"]["y_train_min"]
    R = P["R"]
    fig, ax = plt.subplots(figsize=(9, 6.2))
    ax.axvspan(0.9, vmin_obs / 1e6, color="C1", alpha=0.12, label=f"V1 < {vmin_obs / 1e6:.3f} TWh: outside observed data")
    ax.scatter(F0[:, 0] / 1e6, F0[:, 1] / 1e9, s=18, c="0.5", label="start set (n0_E designs, f)")
    ax.scatter(Fp[:, 0] / 1e6, Fp[:, 1] / 1e9, s=18, marker="x", c="0.3", label="random 48 (f)")
    for s in SEEDS_MULTI:
        U = []
        for k in range(1, 5):
            dm = pd.read_csv(os.path.join(HERE, "waves", f"methods_E_EMU_house_s0_s{s}_r{k}", "design_matrix.csv"))
            U.append(dm[[c for c in dm.columns if c.startswith("u_")]].to_numpy(float))
        F = em.true_f(np.vstack(U))
        assert F.shape == (32, 2) and np.isfinite(F).all()
        ax.scatter(F[:, 0] / 1e6, F[:, 1] / 1e9, s=16, c="C0", alpha=0.6, label="qNEHVI s0, 5 lanes (f)" if s == 0 else None)
    ax.plot(fs[:, 0] / 1e6, fs[:, 1] / 1e9, "-", color="C3", lw=1.2, label="Sobol 2^14 non-dominated set (not a front)")
    ax.step(bk[:, 0] / 1e6, bk[:, 1] / 1e9, where="post", color="k", lw=1.6, label="best-known front")
    ax.plot([ax.get_xlim()[0], R["V1"] / 1e6, R["V1"] / 1e6], [R["E1"] / 1e9, R["E1"] / 1e9, ax.get_ylim()[0]],
            color="C4", ls="--", lw=1.4, label="R box (landing_R.json)")
    ax.set_xlabel("V1 curtailment f (TWh)")
    ax.set_ylabel("E1 system cost f ($B)")
    ax.set_title("EMULATOR — objective space (true f at every evaluated design)")
    ax.legend(fontsize=8.5, loc="center left", bbox_to_anchor=(1.01, 0.5))
    _bold(ax)
    fig.tight_layout()
    p = os.path.join(em.FIGS, "fig_EMU_front.png")
    fig.savefig(p, dpi=150, bbox_inches="tight")
    plt.close(fig)
    out.append(p)
    # 4 calibration: cov95 per batch, C2 line, hull split
    fig, axes = plt.subplots(1, 2, figsize=(14, 4.8))
    for ax, o in zip(axes, em.SEATED):
        for (kind, var), col in {("single", "house"): "C0", ("multi", "house"): "C9", ("single", "long"): "C2",
                                 ("multi", "long"): "C8"}.items():
            g = hull[(hull.objective == o) & (hull.kind == kind) & (hull.variant == var)]
            assert len(g) > 0 and g["cov95"].between(0, 8).all()
            off = {"single": -0.15, "multi": 0.15}[kind]
            for allout, mk in ((True, "o"), (False, "s")):
                gg = g[(g["n_outside_hull"] == 8) == allout]
                ax.scatter(gg["round"] + off + np.random.default_rng(0).uniform(-0.05, 0.05, len(gg)), gg["cov95"],
                           marker=mk, s=34, c=col, alpha=0.8,
                           label=f"{kind}, {'house fit' if var == 'house' else 'long fit (expl.)'}, "
                                 f"{'all 8 outside hull' if allout else 'some inside hull'}")
        ax.axhline(4.5, color="C3", lw=1.4, ls="-.", label="C2 fires at cov95 <= 4")
        ax.set_xticks([1, 2, 3, 4])
        ax.set_ylim(-0.5, 8.5)
        ax.set_xlabel("Round")
        ax.set_ylabel(f"{o}: cov95 of the 8 new points")
        ax.set_title(f"{o}: cov95 of each round's 8 new points")
        _bold(ax)
    h, l = axes[0].get_legend_handles_labels()
    fig.legend(h, l, loc="center left", bbox_to_anchor=(1.0, 0.5), fontsize=8.5)
    fig.suptitle("EMULATOR — calibration of each round's 8 new points vs the start-set hull", fontweight="bold")
    fig.tight_layout()
    p = os.path.join(em.FIGS, "fig_EMU_calibration.png")
    fig.savefig(p, dpi=150, bbox_inches="tight")
    plt.close(fig)
    out.append(p)
    print("\n".join(out))
    return out


# --------------------------------------------------------------------------- #
# report (EMULATOR_BO.md, regenerated in full)
# --------------------------------------------------------------------------- #

def _sha(grep):
    r = subprocess.run(["git", "-C", HERE, "log", "-1", "--format=%h", "--fixed-strings", f"--grep={grep}"],
                       capture_output=True, text=True)
    return r.stdout.strip() or "(uncommitted)"


def _rng(s, fmt="{:.2f}"):
    s = pd.Series(s).dropna()
    return f"{fmt.format(s.min())}–{fmt.format(s.max())}"


def write_md():
    sdf = pd.read_csv(SINGLE_CSV)
    mdf = pd.read_csv(MULTI_CSV)
    hull = pd.read_csv(HULL_CSV)
    S = _load(SUMMARY)
    X = _extras()
    P = _load(em.PARAMS)
    front = _load(os.path.join(em.RUNS, "EMU_front.json"))
    pool = _load(os.path.join(em.RUNS, "EMU_random_pool.json"))
    single, multi = _runs()
    bk = X["best_known"]
    hb = bk["hv_best_known"]
    pl = X["r0_plugin"]
    ov = X["seed_overlap"]
    fr = S["s0_r4_frac_best"]
    frac_txt = f"{fr[0]:.3f}–{fr[1]:.3f}"
    hs = sdf[sdf.variant == "house"]
    lg = sdf[(sdf.variant == "long") & (sdf.method == "bo")]
    hb_bo = hs[hs.method == "bo"]
    plugV, plugE = pl["house"]["objectives"]["V1"]["regret_B"], pl["house"]["objectives"]["E1"]["regret_B"]
    sha = {k: _sha(v) for k, v in {
        "step0": "methods_E(66 step 0", "c": "methods_E(66, as 55's proxy, disclosed)", "B": "methods_E(66 B,",
        "E": "methods_E(66 E,", "F": "methods_E(66 F,", "G": "methods_E(66 G,", "code1": "emulator(66 code)",
        "out1": "emulator(66 outputs)"}.items()}
    longE_r0 = lg[(lg.objective == "E1") & (lg["round"] == 0)]["noise_sd_raw"]
    longV_r0 = lg[(lg.objective == "V1") & (lg["round"] == 0)]["noise_sd_raw"]
    chat = P["sigma_c"]["sd"]
    lm = mdf[(mdf.variant == "long") & (mdf["round"] >= 1) & mdf["hv"].notna()]
    hm = mdf[(mdf.variant == "house") & (mdf["round"] >= 1) & mdf["hv"].notna()]
    rmsz_long = pd.concat([lg[lg["round"] >= 1]["rms_z"], lm["V1_rms_z"], lm["E1_rms_z"]])
    rmsz_house = pd.concat([hb_bo[hb_bo["round"] >= 1]["rms_z"], hm["V1_rms_z"], hm["E1_rms_z"]])
    ls_h = hb_bo[hb_bo["round"] >= 0]["ls_ratio_vs_emulator_max"]
    ls_l = lg["ls_ratio_vs_emulator_max"]
    noise_h = hb_bo["noise_sd_raw"].groupby(hb_bo.objective).mean()
    noise_l = lg.groupby("objective")["noise_sd_raw"]
    wall_s_h = hb_bo[hb_bo["round"] >= 1]["wall_s"].mean(); wall_s_l = lg[lg["round"] >= 1]["wall_s"].mean()
    wall_m_h = hm[hm.scenario == "s0"]["wall_s"].mean(); wall_m_l = lm["wall_s"].mean()
    lr1E = lg[(lg.objective == "E1") & (lg["round"] == 1)].sort_values("seed_id")
    vmin = P["objectives"]["V1"]["y_train_min"]; emin = P["objectives"]["E1"]["y_train_min"]
    fV, fE = P["objectives"]["V1"]["f_star"], P["objectives"]["E1"]["f_star"]
    Bb = X["baselines"]
    s0r4 = mdf[(mdf.variant == "house") & (mdf.scenario == "s0") & (mdf["round"] == 4)]
    old = None
    oldp = os.path.join(HERE, "runs_compact", "EMU_rerun_check.json")
    if os.path.isfile(oldp):
        old = _load(oldp)
    L = []
    A = L.append
    A("# EMULATOR BO dry run on the committed GPs (prompt 66, 2026-11-24)\n")
    A("**EMULATOR. This is a machinery check, not a result.** No PCM ran. No CRC job ran. Nothing here enters a "
      "ledger, the plan, a decision row or the paper's claims. \"Truth\" means the emulator's truth (the posterior "
      "mean of the committed GPs), not the ERCOT system.\n")
    import emulator_E_committed as EC
    if os.path.isfile(EC.SUMMARY):
        L += EC.md_lines()
    A("## B.0 Answer in two minutes (house block)\n")
    A("1. **Did the BO machinery run end to end on ERCOT?** Yes, after one change to 55. As built, the multi-seed init "
      "crashed at seed 1. qNEHVI puts 4–5 of the 8 r1 designs on the same box vertices in every seed lane, and 55 asserted "
      "disjoint r1 sets. I relaxed the assert to the prompt-55 text (\"sets differ\"). After that change, 12/12 "
      "single-objective runs and 15/15 multi-objective lanes finished. Each scenario took its expected branch: s0 monitor "
      "to the cap, s1 constrained from r2, s2 HALT at r1. **Kay: accept or reject this change (section 7, change 2c).**")
    A(f"2. **Are the committed GPs good enough to drive it?** They are good enough to steer, but not to check themselves. "
      f"On this emulator, BO gets to {S['beats_random']['V1']['bo_mean']:.2f} B (V1) and {S['beats_random']['E1']['bo_mean']:.3f} B "
      f"(E1) of the emulator optimum by round 4 on 3/3 seeds — but the r0 start-set GP's own optimum already has regret "
      f"{plugV:.2f} / {plugE:.3f} B, so this measures optimize_acqf and bound handling, not search. The front reaches "
      f"{frac_txt} of the best-known emulator front. The house fit sets the noise sd at 6× (V1) and 2.3× (E1) the emulated "
      f"chatter. Every 95 % band is too wide (rms z {_rng(rmsz_house)}), so C2 and C3 cannot fire. Do not read "
      "\"C2/C3 = 0\" as evidence of calibration.")
    A(f"3. **What changes with a converged fit?** The nearest proxy for fit v2 is the long fit (exploratory, 10,000 steps) "
      "(it is NOT v2 — no priors, single start). It gives the same search result "
      f"(V1 ≤ {lg[(lg.objective == 'V1') & (lg['round'] == 4)]['regret_best_obs_B'].max():.2f} B, "
      f"E1 {lg[(lg.objective == 'E1') & (lg['round'] == 4)]['regret_best_obs_B'].max():.3f} B, HV "
      f"{float(lm[lm['round'] == 4]['hv_true_frac_best'].iloc[0]):.3f}). The gates get power: C2 fires at E1 r1 on "
      f"{int(lr1E['C2'].astype(bool).sum())} of 3 seeds. Two causes: all 8 r1 designs lie outside the start set's hull, and "
      f"the r0 long fit sets the E1 noise at ${longE_r0.mean() / 1e3:.0f}k, {longE_r0.mean() / chat[1]:.2f}× the chatter "
      "(noise collapse). Expect C2 REVIEW flags at r1 under fit v2 unless v2 gives a stable noise estimate.")
    A("4. **What remains before a real launch?** Land fit v2, then rerun this dry run (truth and BO GP both change; add the "
      "v2 convergence flag per round fit). Decide the 55 r1-assert change (item 1) and E-D7. Decide what a C2 flag at r1 on "
      "an out-of-hull batch means (review, not halt; report hull distance). Replace the repeat-design assert in "
      "propose_round with a declared rule. Align dry_round_E.py. Decide the cross-lane duplicate-vertex runs "
      f"(≈ {ov['r1_duplicate_runs_of_40']} of 40 r1 runs under option C). The full checklist is section 8.\n")
    A(f"**Limits of this test.** Both emulator optima sit on box vertices outside the data. f*(V1) is "
      f"{(vmin - fV) / em.B['V1']:.0f} B below the lowest observed V1. f*(E1) is {(emin - fE) / em.B['E1']:.1f} B below the lowest "
      "observed E1. The regrets measure how well the machinery finds a vertex. They do not measure the ERCOT optimum. Both "
      f"front end points lie outside the R box (V1-corner E1 ${bk['front'][0][1] / 1e6:,.1f}M > R_E1; E1-corner V1 "
      f"{bk['front'][-1][0] / 1e6:.2f} TWh > R_V1), so the extrapolated V1 corner adds zero HV.\n")
    # verdict
    A("## 0. Verdict\n")
    A("| # | check (prompt 66 pass criteria) | result | verdict |")
    A("|---|---|---|---|")
    for r in S["pass_fail"]:
        A(f"| {r['n']} | {r['check']} | {r['result']} | {r['verdict']} |")
    A("")
    A(f"p_random = 1 [1, 1] in every lane has no power. All 48 random designs together reach only "
      f"{pool['hv_all48_true'] / hb:.3f} of the front, and BO's r1 already reaches "
      f"{_rng(mdf[(mdf.variant == 'house') & (mdf.scenario == 's0') & (mdf['round'] == 1)]['hv_true_frac_best'])}. "
      "The matched-budget baselines in §3.2 give the effect size instead.\n")
    # 1 emulator
    A("## 1. Emulator (prompt 66 §1)\n")
    A("- Training rows: the n* = 48 grading rows of `n0_E` (Sobol 0–47), read by the real 54 loader "
      "`analysis.ercot_gp.ercot_gp_loader.load` with `waves/design_space_E_2026-11-24.json`. 0 refused, 0 SUSPECT, R1 max 0.")
    A("- Fit: `ercot_gp_status.fit` (D-1025 FlexGP, `bogp.train_gp` Adam 700 steps, lr 0.01, float32, "
      "`torch.manual_seed(0)`), floor 0 → inferred-only 1e-9. This is the house fit, the code path 54 used for "
      "`committed_configs.json`.")
    mx = max(P["objectives"][o]["reproduces_committed"][k] for o in ("V1", "E1", "N4") for k in P["objectives"][o]["reproduces_committed"])
    A(f"- f_j(u) = the posterior mean, frozen in a float64 closed form (`emulator_E_params.json`). It matches FlexGP's mean "
      f"on 1,024 Sobol points to {P['objectives']['V1']['closed_form_vs_flexgp_mean']['max_abs']:.0f} MWh (V1), "
      f"${P['objectives']['E1']['closed_form_vs_flexgp_mean']['max_abs']:.0f} (E1) and "
      f"{P['objectives']['N4']['closed_form_vs_flexgp_mean']['max_abs']:.3f} (N4). The refit reproduces the committed "
      f"hyperparameters to ≤ {mx:.1e} relative.\n")
    A("| id | role | arm | ARD lengthscales (u; 110 / 140 / 146 / 163 / 270 / 274) | outputscale sd | noise sd | f* at u* | f* (Sobol 2^14) |")
    A("|---|---|---|---|---|---|---|---|")
    for o in ("V1", "E1", "N4"):
        q = P["objectives"][o]
        h = q["hyperparameters"]
        A(f"| {o} | {q['role']} | {q['arm']} | {' / '.join(f'{v:.4f}' for v in h['ls_u'].values())} | "
          f"{h['outputscale_sd_t']:,.5g} | {h['noise_sd_raw']:,.5g} | {q['f_star']:,.6g} at "
          f"[{', '.join(f'{v:.2f}' for v in q['u_star'])}] | {q['f_star_sobol_2^14']:,.6g} |")
    A("")
    A(f"Caution: both emulator optima are extrapolations to box vertices. f*(V1) = {fV / 1e6:.3f} TWh at the all-PEM corner is "
      f"{(vmin - fV) / 1e6:.2f} TWh ({(vmin - fV) / em.B['V1']:.0f} B) below the lowest observed V1 ({vmin / 1e6:.3f} TWh). "
      f"f*(E1) = ${fE / 1e6:,.2f}M near the no-PEM corner is ${(emin - fE) / 1e6:.1f}M ({(emin - fE) / em.B['E1']:.1f} B) below "
      f"the lowest observed E1 (${emin / 1e6:,.2f}M). The regrets below are measured against these extrapolations. They test "
      "the machinery, not the ERCOT optimum.\n")
    A(f"- Observation: y = f(u) + eps, eps ~ N(0, Sigma_c[V1, E1]) from `analysis/noise_v3/ercot_noise_seed_sigma_c.csv` "
      f"(prompt-63 Seed chatter, LW-shrunk): sd V1 {chat[0]:,.0f} MWh, sd E1 ${chat[1] / 1e6:.3f}M, corr {P['sigma_c']['corr']:.3f}.")
    A("- Streams: numpy `default_rng([6666, family, seed_id, scenario, variant])`. BO and its random baseline share one "
      "stream (common random numbers).")
    A("- Start set: the 48 n0_E designs with EMULATED values f(u_i) + eps_i (`default_rng(6666)`, first 48 × 2 draw). One "
      "generating process makes every Y the BO sees.")
    m = P["monitor_chatter"]
    A(f"- Guardrails: R1 = 0 (except injected rows), R2 = 156.08 + N(0, {m['R2_sd']:.1f}²) MWh, N1_off = 30,750 + "
      f"N(0, {m['N1_off_sd']:.1f}²) line-h, N4 = f_N4 + N(0, {m['N4_sd']:.1f}²) on an independent monitor stream.")
    A(f"- R (`waves/n0_E/landing_R.json`): V1 {P['R']['V1']:,.0f} MWh, E1 ${P['R']['E1'] / 1e6:,.2f}M. B_V1 18,739 MWh, "
      "B_E1 $1.862M.\n")
    # 2 single
    A("## 2. Single-objective BO (prompt 66 §2)\n")
    A("Settings: botorch `qLogNoisyExpectedImprovement`, `SobolQMCNormalSampler(128, seed s)`, `prune_baseline`, "
      "`cache_root`, `optimize_acqf` over [0, 1]^6, q 8, 20 restarts × 512 raw samples, sequential. s = 20261007 + 100 "
      "seed_id + k. GP = 55's `qnehvi_E.ObjGP` (float64, house fit) with the committed kernel and transform, floor 1e-9, "
      "refitted each round. Proposals get the same bound cleanup as 55 (`snap_bounds`). Random baseline = 8 i.i.d. "
      "uniform u per round from `default_rng(s)`, same s, same noise stream. Regret = f(best-observed design) − f*, in B_j.\n")
    A(f"**r0 plug-in.** The start-set GP (house fit, round 0) already puts its posterior-mean optimum at regret "
      f"{plugV:.3f} B (V1) and {plugE:.3f} B (E1). Criteria 4 and 5 therefore validate optimize_acqf and bound handling, "
      "not search: the GP that BO starts from already knows where the optimum is.\n")
    A("| obj | fit | method | seed | r0 plug-in | r0 | r1 | r2 | r3 | r4 | posterior-mean optimum r4 | cov95 r1–r4 | rms z r1–r4 |")
    A("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for (o, v, me, s), g in sdf.groupby(["objective", "variant", "method", "seed_id"]):
        g = g.sort_values("round")
        b = g[g["round"] >= 1]
        bo = me == "bo"
        A(f"| {o} | {'house' if v == 'house' else 'long (expl.)'} | {me} | {s} | "
          f"{g['r0_plugin_regret_B'].iloc[0]:.3f} | " + " | ".join(f"{x:.3f}" for x in g["regret_best_obs_B"]) + " | "
          + (f"{g['regret_pm_opt_B'].iloc[-1]:.3f}" if bo else "-") + " | "
          + ("/".join(str(int(x)) for x in b["cov95"]) if bo else "-") + " | "
          + ("/".join(f"{x:.2f}" for x in b["rms_z"]) if bo else "-") + " |")
    A("")
    A("The best observed can get worse when a noisy low observation at a slightly worse design replaces the best. The "
      "posterior-mean optimum stays at 0.01–0.03 B.\n")
    A("![single](figs/fig_EMU_single_regret.png)\n")
    # 3 multi
    A("## 3. Multi-objective, 55 machinery (prompt 66 §3)\n")
    A("`acquire_E.Lane` + `cmd_init` + `propose_round` + `ingest_gate` (C1) + `grade_round`, with the section-7 changes. "
      "Root = `analysis/emulator_E/`: waves `waves/methods_E_EMU_<fit>_<scen>_s<seed>_r<k>/` (55 wave writer output + "
      "`objectives_EMULATOR.csv`); ledgers `lanes/<fit>/<scen>/s<seed>/`. Config = `arms_E.json` with absolute paths, "
      "`part = \"EMULATOR\"`, `n0_tier_provisional = 48`. Loader = the real 54 loader for n0_E (keys, U, meta, identity "
      "gate) with Y replaced by the emulated start values, plus the emulated wave tables. qNEHVI block as pinned, acq seed "
      "20261006 + 100 seed_id + k, cap 4. Seed lane 0 ran first (s0), then seeds 1–4.\n")
    A("- tau_exact: `ercot_noise_exact_cov.csv` is identically 0 for V1 and E1, so tau_joint = tau_marginal = 0 and "
      "`budget_cap_only = true`. The ledger records gain/tau = null and would_stop = false in every round.")
    A(f"- tau_res (REPORT-ONLY, `tau_E.tau_res`, Sigma_c[V1, E1], 1,000 draws, `default_rng(20261006)`): "
      f"{float(mdf['tau_res'].iloc[0]):.4g} (HV units, MWh × $).")
    A(f"- **Best-known front** (the reference): {bk['rule']}. HV = {hb:.5g} = {bk['best_over_polished']:.4f} × the "
      f"polished front (Sobol + vertices + scalarizations); polished ∪ the lane designs alone = "
      f"{bk['polished_plus_lane_designs_over_polished']:.4f} × polished. Sobol reference = {bk['sobol_over_best']:.3f} of "
      "best-known; not a front.")
    A("- prompt-34 p (one 48-pool, 8k-subsets, ties ½, seed 20261012, interval from 1,000 × 2,000 pool resamples) is kept "
      "as specified in `emulator_E_multi.csv` (`p_random_prompt34_saturated`): saturated; see effect size.\n")
    A("### 3.1 Lanes\n")
    A("| scen | fit | seed | graded | true-f HV / best-known, r0–r4 | effect vs vertices p95, r4 | gain / tau_res, r1–r4 | C2/C3 | wall s per round |")
    A("|---|---|---|---|---|---|---|---|---|")
    for (sc, v, s), g in mdf.groupby(["scenario", "variant", "seed_id"]):
        g = g[g["hv"].notna()].sort_values("round")
        gr = g[g["round"] >= 1]
        last = gr.iloc[-1]
        A(f"| {sc} | {'house' if v == 'house' else 'long (expl.)'} | {s} | {len(gr)}{' (HALT)' if sc == 's2' else ''} | "
          + "/".join(f"{x:.3f}" for x in g["hv_true_frac_best"]) + " | "
          + (f"{last['effect_vs_vertices_p95']:+.3f}" if last["round"] == 4 else "-") + " | "
          + "/".join(f"{x:.1f}" for x in gr["gain_over_tau_res"]) + " | "
          + f"{int(gr['C2'].astype(bool).sum())}/{int(gr['C3'].astype(bool).sum())} | "
          + "/".join(f"{x:.1f}" for x in gr["wall_s"]) + " |")
    A("")
    A("### 3.2 Matched-budget baselines (true-f HV / best-known front; same 48 starts; 8 per round × 4)\n")
    A(f"Rule: {X['baseline_rule']}.\n")
    A("| baseline | reps | r1 p5/p50/p95 | r2 p50 | r3 p50 | r4 p5/p50/p95 | r4 max |")
    A("|---|---|---|---|---|---|---|")
    for name in ("uniform", "vertices", "plugin_random", "plugin_spread"):
        b = Bb[name]
        A(f"| {BASE_NAMES[name]} | {b['n_rep']} | {b['p5'][1]:.3f}/{b['p50'][1]:.3f}/{b['p95'][1]:.3f} | {b['p50'][2]:.3f} | "
          f"{b['p50'][3]:.3f} | {b['p5'][4]:.3f}/{b['p50'][4]:.3f}/{b['p95'][4]:.3f} | {b['max'][4]:.3f} |")
    A(f"| qNEHVI s0 (5 lanes) | 5 | {_rng(mdf[(mdf.variant == 'house') & (mdf.scenario == 's0') & (mdf['round'] == 1)]['hv_true_frac_best'], '{:.3f}')} | "
      f"{_rng(mdf[(mdf.variant == 'house') & (mdf.scenario == 's0') & (mdf['round'] == 2)]['hv_true_frac_best'], '{:.3f}')} | "
      f"{_rng(mdf[(mdf.variant == 'house') & (mdf.scenario == 's0') & (mdf['round'] == 3)]['hv_true_frac_best'], '{:.3f}')} | "
      f"{_rng(s0r4['hv_true_frac_best'], '{:.3f}')} | {s0r4['hv_true_frac_best'].max():.3f} |")
    A("")
    eff_v = s0r4["effect_vs_vertices_p95"]; eff_ps = s0r4["effect_vs_plugin_spread"]; eff_pr = s0r4["effect_vs_plugin_random_p95"]
    A(f"Effect size at r4 (s0, house fit): BO − vertices p95 = {_rng(eff_v, '{:+.3f}')}; BO − plug-in random p95 = "
      f"{_rng(eff_pr, '{:+.3f}')}; BO − plug-in spread = {_rng(eff_ps, '{:+.3f}')}.")
    if eff_ps.abs().max() < 0.01:
        A("BO and the r0 plug-in exploit end within 0.01 of each other: **this emulator cannot separate the acquisition "
          "function from a plug-in exploit of the start-set GP.**\n")
    elif eff_ps.min() > 0:
        A("BO ends above the plug-in exploit in every lane, but by little; the emulator separates acquisition from a plug-in "
          "exploit only weakly.\n")
    else:
        A("The plug-in exploit matches or beats BO in some lanes: **the emulator cannot separate the acquisition function "
          "from a plug-in exploit of the start-set GP.**\n")
    A("![multi](figs/fig_EMU_multi_hv.png)\n")
    A("### 3.3 Seed overlap (input to E-D4)\n")
    A("| round | designs (5 lanes) | unique | exact vertices |")
    A("|---|---|---|---|")
    for r in ov["per_round"]:
        A(f"| r{r['round']} | {r['n_designs']} | {r['n_unique']} | {r['frac_exact_vertex']:.0%} |")
    A("")
    md = pd.DataFrame(ov["min_dist"])
    A(f"Pairwise Jaccard of the 32-design lane sets: {ov['jaccard_range'][0]:.2f}–{ov['jaccard_range'][1]:.2f}. Final "
      f"true-f HV spread across the 5 lanes: {_rng(s0r4['hv_true_frac_best'], '{:.3f}')}. Minimum distance (u, Euclidean) of "
      f"a proposal to the lane's already-evaluated set: {md['min_dist_to_evaluated'].min():.3g}; proposals within 1e-6: "
      f"{int(md['n_below_1e-6'].sum())}; within 0.05: {int(md['n_below_0.05'].sum())} (re-proposal risk, F6). "
      f"**{ov['statement']}**\n")
    A("- s1: r1 is unconstrained (the violation is not yet known). From r2 the round record says `constraint: shed <= 1.0 "
      "MWh (GP on the accumulated R1 column)`. The violating run stays in GP training and is out of HV.")
    A("- s2: grade r1 writes `HALT_FOR_DECISION.md`; the next `propose_round` raises the REFUSED SystemExit.")
    A(f"- Wall time per round (house fit, s0): {wall_m_h:.1f} s mean (propose + emulate + C1 + grade); qNEHVI fit + "
      f"optimize {hm['qnehvi_s'].mean():.1f} s mean at 2 threads.")
    A(f"- botorch emits ~{hm['propose_warnings'].mean():.0f} warnings per propose (restart retries, numerics); counts are "
      "in `emulator_E_multi.csv`. None stopped a round.\n")
    A("![front](figs/fig_EMU_front.png)\n")
    # 4 calibration
    A("## 4. Calibration and lengthscales\n")
    c = S["c_counts"]
    A(f"### 4.1 Counts\n\nC2 (covered ≤ 4 of 8) and C3 (≥ 3 of 8 with |z| > 3), computed exactly as 55 "
      f"(`acquire_E._calibration`; `emulator_E.calib` is tested equal). House fit: {c['single_C2']} C2, {c['single_C3']} C3 "
      f"in {c['n_single']} single-objective rounds; {c['multi_C2']} C2, {c['multi_C3']} C3 in {c['n_multi']} multi-objective "
      f"(round, objective) cells. Expected under the nominal rates: {c['expected_C2']:.3f} (C2), {c['expected_C3']:.1e} (C3).\n")
    A("### 4.2 Start-set hull split\n")
    A("A design is inside the hull when it is a convex combination of the 48 start designs (LP feasibility in u).\n")
    if (hull["n_inside"] == 0).all():
        A(f"**Every proposed design in every batch ({len(hull)} (batch, objective) rows, both fits) lies outside the start "
          "set's convex hull.** The inside/outside split is therefore degenerate: all calibration here is extrapolation. "
          "The 48 Sobol starts fill the interior; BO goes to faces and vertices.\n")
    A("| kind | fit | round | (batch, objective) rows | mean fraction outside hull | exact vertices / batch | cov95 inside (pooled) | cov95 outside (pooled) | rms z inside | rms z outside | C2 batches |")
    A("|---|---|---|---|---|---|---|---|---|---|---|")
    for (kd, v, rd), g in hull.groupby(["kind", "variant", "round"]):
        ni = int(g["n_inside"].sum()); no = int(g["n_outside_hull"].sum())
        ci = g["cov95_inside"].fillna(0).sum(); co = g["cov95_outside"].fillna(0).sum()
        A(f"| {kd} | {'house' if v == 'house' else 'long (expl.)'} | r{rd} | {len(g)} | {g['frac_outside_hull'].mean():.2f} | "
          f"{g['n_exact_vertex'].mean():.1f} | {int(ci)}/{ni} | {int(co)}/{no} | "          + (f"{g['rms_z_inside'].mean():.2f}" if g['rms_z_inside'].notna().any() else "-") + " | "
          + (f"{g['rms_z_outside'].mean():.2f}" if g['rms_z_outside'].notna().any() else "-")
          + f" | {int(g['C2'].astype(bool).sum())} |")
    A("")
    A(f"### 4.3 Lengthscale drift (house fit)\n\nMax relative change of the BO GP's ARD lengthscales (u) from r0 to r4: "
      f"{_rng(hb_bo[hb_bo['round'] == 4]['ls_drift_vs_r0_max'])}. Distance from the emulator's lengthscales: ≤ {ls_h.max():.2f}. "
      "The refit is stable.\n")
    A(f"### 4.4 Power caveat\n\nThe house-fit BO GP infers noise sd {noise_h['V1']:,.0f} MWh (V1) and "
      f"${noise_h['E1'] / 1e6:.2f}M (E1) on average, {noise_h['V1'] / chat[0]:.0f}× and {noise_h['E1'] / chat[1]:.1f}× the "
      f"emulated chatter. Its 95 % bands are too wide, rms z is {_rng(rmsz_house)}, and C2/C3 cannot fire on an "
      "under-covering model. The zero flag count is weak evidence. (54's ERCOT_GP_STATUS reports 3.97× / 2.65× against the "
      f"df-16 σ_c; this file uses the LW-shrunk Σ_c sd {chat[0]:,.0f} MWh / ${chat[1] / 1e6:.3f}M.)\n")
    A("![calibration](figs/fig_EMU_calibration.png)\n")
    # 5 exploratory
    A("## 5. EXPLORATORY — long fit (exploratory, 10,000 steps) of the BO's internal GP (nothing committed)\n")
    A("Same emulator truth (the committed house-fit f). Only the BO's own GP fit changes: `qnehvi_E.train_gp` → "
      "`bogp.train_gp(n_epochs=10000)`. This is NOT fit v2 (no priors, single start).\n")
    lgV = lg[lg.objective == "V1"]; lgE = lg[lg.objective == "E1"]
    A("| item | house fit (700 steps) | long fit (exploratory, 10,000 steps) |")
    A("|---|---|---|")
    for o in ("V1", "E1"):
        h4 = hb_bo[(hb_bo.objective == o) & (hb_bo["round"] == 4)].sort_values("seed_id")["regret_best_obs_B"]
        l4 = lg[(lg.objective == o) & (lg["round"] == 4)].sort_values("seed_id")["regret_best_obs_B"]
        A(f"| single {o} regret r4, seeds 0/1/2 (B) | {' / '.join(f'{x:.3f}' for x in h4)} | {' / '.join(f'{x:.3f}' for x in l4)} |")
    A(f"| inferred noise sd V1 / E1 | mean {noise_h['V1'] / 1e3:.1f}k MWh / ${noise_h['E1'] / 1e6:.2f}M | mean "
      f"{lgV['noise_sd_raw'].mean() / 1e3:.1f}k MWh / ${lgE['noise_sd_raw'].mean() / 1e6:.2f}M; range "
      f"{lgV['noise_sd_raw'].min() / 1e3:.1f}k–{lgV['noise_sd_raw'].max() / 1e3:.1f}k MWh / "
      f"${lgE['noise_sd_raw'].min() / 1e3:.0f}k–${lgE['noise_sd_raw'].max() / 1e3:.0f}k; r0 (start set) "
      f"{longV_r0.mean() / 1e3:.1f}k MWh / ${longE_r0.mean() / 1e3:.0f}k (E1 {longE_r0.mean() / chat[1]:.2f}× chatter) |")
    A(f"| rms z of new batches (single and multi) | {_rng(rmsz_house)} | {_rng(rmsz_long)} |")
    A(f"| C2 flags (single, 24 rounds) | {c['single_C2']} | {c['long_single_C2']} (E1 r1 cov95 "
      f"{', '.join(str(int(x)) for x in lr1E['cov95'])} of 8) |")
    A(f"| C3 flags (single) | {c['single_C3']} | {c['long_single_C3']} |")
    A(f"| lengthscale distance to the emulator (max over sites) | ≤ {ls_h.max():.2f} | {ls_l.min():.2f}–{ls_l.max():.2f} "
      f"({ls_l.min():.0%}–{ls_l.max():.0%}) |")
    A(f"| multi s0 seed 0: true-f HV / best-known r4 | "
      f"{float(s0r4[s0r4.seed_id == 0]['hv_true_frac_best'].iloc[0]):.3f} | {float(lm[lm['round'] == 4]['hv_true_frac_best'].iloc[0]):.3f} |")
    A(f"| multi s0 seed 0: C2/C3 | 0/0 | {int(lm['C2'].astype(bool).sum())}/{int(lm['C3'].astype(bool).sum())} |")
    A(f"| wall s per round, mean over r1–r4 (single / multi) | {wall_s_h:.1f} / {wall_m_h:.1f} | {wall_s_l:.1f} / {wall_m_l:.1f} |")
    A("")
    A("Reading: the optimizer-limited house fit does not hurt the BO's search on this emulator. Both fits reach the same "
      "regret and front fraction. The long fit is better calibrated after round 1. In round 1 it under-covers the E1 vertex "
      f"batch (cov95 {', '.join(str(int(x)) for x in lr1E['cov95'])} of 8), so C2 fires. Two causes act together. First, all "
      f"8 designs are outside the start set's hull. Second, the r0 long fit sets the E1 noise at ${longE_r0.mean() / 1e3:.0f}k, "
      f"{longE_r0.mean() / chat[1]:.2f}× the chatter. The long fit's noise is unstable (54 Part B saw the same multimodal "
      "likelihood). Fit v2 must show a stable noise estimate before C2 means anything. This emulator's truth is itself a "
      "house-fit posterior mean; a converged-fit truth could change the comparison.\n")
    # 6 parameters
    A("## 6. Every parameter, environment and file\n")
    A("- Branch `ercot/66-emulator-bo`, worktree `RTS-GMLC-e66`, based on `ercot/tx123`. Environment bogp-botorch "
      "(botorch 0.16.1, torch 2.12.0, gpytorch 1.15.2). bo-gp-qparego 60e6328 (= `bogp_sha_expected`).")
    A("- Plan AMENDMENT 2026-11-24b (ERCOT_BO_PLAN.md, 93c81a4) replaces the house fit with fit definition v2 (MAP, "
      "L-BFGS-B, 16 restarts) for every fit from that block on. This run uses the committed configs as they stand (house "
      "fit) for both the emulator truth and the BO GP. Mode-gap columns (`mode_gap_v2`) are empty and wait for the v2 rerun.")
    A("- n* = 48 (54, provisional; E-D7 null). q 8, cap 4, rounds 4.")
    A("- Seeds: emulator 6666; single acq 20261007 + 100 seed_id + k (seed_ids 0–2); multi acq 20261006 + 100 seed_id + k "
      f"(seed_ids 0–4); tau 20261006; prompt-34 subsets 20261012; pool `default_rng([6666, 4, 1])`; Sobol front 6614; "
      f"plug-in front Sobol 6615; matched-budget baselines `default_rng({em.BASE_SEED})`, {em.N_REP} replicates.")
    A("- MC 128 Sobol QMC, 20 restarts, 512 raw, sequential greedy, float64. Bound cleanup `snap_bounds` (tol 1e-12).")
    A("- Scenarios: s1 injects R1 = 2.5 MWh on r1 run 3; s2 injects R1 = 1.5 and 40.0 MWh on r1 runs 2 and 6.")
    A("- Files: `emulator_E_params.json` (emulator, hyperparameters, start set); `emulator_E_single.csv`, "
      "`emulator_E_multi.csv`, `emulator_E_calib_hull.csv`, `emulator_E_summary.json` (pass/fail); `runs_compact/` "
      "(single and multi run records with every design u, `EMU_front.json`, `EMU_random_pool.json`, `EMU_extras.json`: "
      "plug-in, best-known front, baselines, seed overlap); `lanes/`, `waves/`, `figs/`. `runs/` is gitignored "
      "(trial_0826/ercot/**/runs/) and holds only logs and the prompt-34 subset-HV npz; the report and figures read "
      "only committed files, so a clean checkout reproduces them (assert-before-draw recomputes every plotted value).")
    A("- Code: `emulator_E.py`, `emulator_E_report.py`, `test_emulator_E.py` (toy 2-D function).\n")
    A("Reproduce (bogp-botorch, from `trial_0826/ercot`):\n")
    A("    PY=/opt/anaconda3/envs/bogp-botorch/bin/python")
    A("    $PY analysis/emulator_E/emulator_E.py fit-emulator && $PY analysis/emulator_E/emulator_E.py front && $PY analysis/emulator_E/emulator_E.py random-pool")
    A("    for o in V1 E1; do for s in 0 1 2; do for m in bo random; do $PY analysis/emulator_E/emulator_E.py single --obj $o --seed $s --method $m; done; $PY analysis/emulator_E/emulator_E.py single --obj $o --seed $s --variant long; done; done")
    A("    for sc in s0 s1 s2; do $PY analysis/emulator_E/emulator_E.py multi --scenario $sc --seeds 0,1,2,3,4; done")
    A("    $PY analysis/emulator_E/emulator_E.py multi --scenario s0 --seeds 0 --variant long && $PY analysis/emulator_E/emulator_E.py extras")
    A("    $PY analysis/emulator_E/emulator_E_report.py collect && $PY analysis/emulator_E/emulator_E_report.py figs && $PY analysis/emulator_E/emulator_E_report.py report\n")
    # 7 changes
    A("## 7. Changes to 55 code and config (as 55's proxy) and deviations\n")
    A(f"1. `{sha['step0']}` `arms_E.json`: dated design space; objectives [V1, E1]; R2 base 156.08 / flag 312.16 MWh; "
      "N1_off monitor. `_scratch_E.py` writes the design space at the configured path; three M = 4 test asserts read the config.")
    A(f"2. `{sha['c']}` `acquire_E.py` / `common_E.py`: (a) `Lane(loader=...)` takes an injected loader; (b) `n0_tier` uses "
      "`n0_tier_provisional` ONLY while `E-D7_decided` is null; (c) **the r1 cross-seed assert checks \"sets differ\" "
      "(prompt 55 §2.1 text) instead of \"pairwise disjoint\" and records the shared count. Kay: accept or reject.**")
    A(f"3. `{sha['B']}` hardening: (a) a second r1 cross-seed assert — at least one design per seed pair differs by > 1e-6 "
      "in u; (b) the provisional-n* fallback REFUSES when `part == \"B\"`; (c) a comment at the re-proposal assert "
      "(rule unchanged; a 55 Part B decision).")
    A(f"4. `{sha['E']}` **zero-site fix (HIGH).** `qnehvi_E.propose` mapped x·sx + mx back to u and clipped, so a "
      "lower-bound optimum came back as 5.55e-17. The wave writer then wrote a `<site>_PEM` unit with PEM_fraction ~5e-17, "
      "a different model instance from \"site absent\" (contract §5). The first emulated waves had 57 of 2,352 u cells in "
      "(0, 1e-9); `ingest_gate` did not see them. Now `snap_bounds` sets u < 1e-12 to 0 and u > 1 − 1e-12 to 1 "
      "(`settings.bound_snaps`; bound cleanup, not lattice snapping), predictions use the snapped design, and "
      "`wave_writer_E.design_rows` refuses u in (0, 1e-9). Two tests added. I regenerated every wave and result after the fix.")
    if old:
        A(f"   Rerun check: {old['statement']}")
    A(f"5. `{sha['F']}` `HALT_FOR_DECISION.md` printed a literal `HALT_r{{k}}_DECIDED.md`; fixed (f-string).")
    A(f"6. `{sha['G']}` `arms_E.json` carries the R3 and N3 monitors from the design space as config text only.")
    A("7. `dry_round_E.py` still asserts DISJOINT r1 sets on stub data. This is inconsistent with change 2c; left for 55 Part B.")
    A("8. Interpretation: start-set observations are emulated (f + eps), not the real n0_E Y (section 1).")
    A("9. The headline HV fraction uses the best-known front (true f); the spec's Sobol 2^14 figure is reported as a reference.")
    A("10. The exploratory long fit repeat covers all 3 single-objective seeds; multi is s0 seed 0 only, as asked.")
    A("11. The audience review named three STE-100 sentence rewrites that were not in the message I received; I applied "
      "the given texts and the one-name-per-fit rule.\n")
    # 8 remains
    A("## 8. What remains before a real launch (pre-launch checklist, 55 Part B)\n")
    items = [
        "Zero-site fix landed (change 4) — keep the test; add a real-loader ingest test on a fake methods_E wave copied from one n0_E run.",
        "Duplicate-proposal path: replace the re-proposal assert with a declared rule (re-optimize the duplicate slot or allow a replicate); make grade_round idempotent; commit before propose.",
        "Fit v2 in `qnehvi_E` per `committed_configs.json` `fit_definition` (MAP, L-BFGS-B, 16 restarts); add a per-round convergence flag.",
        "New `committed_configs.json` under fit v2 (54 re-open round), then rerun this dry run.",
        "E-D7 decided in `committed_configs.json`; the Part B guard (change 3b) then never sees the provisional tier.",
        "E-D5 amendment appended; README wording switched.",
        "`arms_E.json` complete: `gp.train` = fit v2, `part = \"B\"`; R3 / N3 / N1_off wired into grading (today config text only).",
        "τ_res written into the ledger (today report-only, computed here outside the machinery).",
        "Stale text: README / runbook M = 4 and \"pairwise distinct\" wording; the HALT placeholder (fixed, change 5).",
        "`dry_round_E.py` aligned with change 2c; tests for the c7576a6 branches (injected loader, provisional tier, Part B refusal).",
        "Real-loader ingest test on a fake `__ALL__` methods_E wave copied from one n0_E run.",
        f"Kay's decision on cross-lane duplicate runs (≈ {ov['r1_duplicate_runs_of_40']} of 40 r1 runs under option C): shared replicates vs run all.",
        "CRC: `acquire_E_job.sh --check-env`, `GAP_DECISION.json` present, `submit_ready_E.sh --dry-run`, then one lane first.",
    ]
    for i, t in enumerate(items, 1):
        A(f"{i}. {t}")
    A("")
    A("**Code paths NOT exercised here:** `submit_state_E.py`, `acquire_E_job.sh`, the array and collector scripts, the "
      "ercot-bot commit / push, a real `__ALL__` wave ingest through `pool_objectives`, SUSPECT, a true R2 flag, resume "
      "after HALT (rename + rerun), and the Part B asserts.\n")
    A(f"**Runtime note.** qNEHVI took {hm['qnehvi_s'].min():.1f}–{hm['qnehvi_s'].max():.1f} s per propose at 2 threads here. "
      "Expect 10–30 s plus the fit v2 restarts on CRC; that is < 1 % of a round (8 PCM runs × 5–11 h).\n")
    with open(MD, "w") as f:
        f.write("\n".join(L))
    print(f"wrote {MD} ({len(L)} lines)")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["collect", "figs", "report"])
    a = ap.parse_args(argv)
    if a.cmd == "collect":
        collect()
    elif a.cmd == "figs":
        figs()
    elif a.cmd == "report":
        write_md()
    return 0


if __name__ == "__main__":
    sys.exit(main())
