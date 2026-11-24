#!/usr/bin/env python3
"""Prompt 66 — collect / figs / report for the EMULATOR BO dry run.

    PY=/opt/anaconda3/envs/bogp-botorch/bin/python
    $PY analysis/emulator_E/emulator_E_report.py collect    # -> emulator_E_single.csv, emulator_E_multi.csv, emulator_E_summary.json
    $PY analysis/emulator_E/emulator_E_report.py figs       # assert-before-draw against the CSVs, then figs/
    $PY analysis/emulator_E/emulator_E_report.py report     # markdown tables (stdout) pasted into EMULATOR_BO.md

Everything here is EMULATOR output (prompt 66): a machinery check, never data.
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

SINGLE_CSV = os.path.join(HERE, "emulator_E_single.csv")
MULTI_CSV = os.path.join(HERE, "emulator_E_multi.csv")
SUMMARY = os.path.join(HERE, "emulator_E_summary.json")
MD = os.path.join(HERE, "EMULATOR_BO.md")
C2_RATE, C3_RATE = 3.7e-4, 1.1e-6
SEEDS_MULTI = (0, 1, 2, 3, 4)


def _load(p):
    with open(p) as f:
        return json.load(f)


def _runs():
    single = [_load(p) for p in sorted(glob.glob(os.path.join(em.RUNS, "single", "EMU_single_*.json")))]
    multi = [_load(p) for p in sorted(glob.glob(os.path.join(em.RUNS, "multi", "EMU_multi_*.json")))]
    return single, multi


# --------------------------------------------------------------------------- #
# collect
# --------------------------------------------------------------------------- #

def collect():
    P = _load(em.PARAMS)
    front = _load(os.path.join(em.RUNS, "EMU_front.json"))
    pool = _load(os.path.join(em.RUNS, "EMU_random_pool.json"))
    npz = np.load(os.path.join(em.RUNS, "EMU_random_pool_subsets.npz"))
    sites = P["sites"]
    single, multi = _runs()
    rows = []
    for d in single:
        r0 = d["records"][0]
        ls0 = np.asarray(r0["gp"]["ls_u"], float) if "gp" in r0 else None
        ls_emu = np.asarray(P["objectives"][d["objective"]]["ls_std"], float) * np.asarray(P["objectives"][d["objective"]]["sx"], float)
        for r in d["records"]:
            row = {"label": "EMULATOR", "variant": d["variant"], "fit_epochs": d["fit_epochs"], "objective": d["objective"],
                   "method": d["method"], "seed_id": d["seed_id"], "round": r["round"], "n": r["n"],
                   "acq_seed": r.get("seed"), "best_obs": r["best_obs"], "f_at_best_obs": r["f_at_best_obs"],
                   "f_star": d["f_star"], "B": d["B"], "regret_best_obs_B": r["regret_best_obs_B"],
                   "gap_obs_B": r["gap_obs_B"], "min_f_evaluated_B": r["min_f_evaluated_B"],
                   "regret_pm_opt_B": r.get("regret_pm_opt_B"), "pm_opt_f": r.get("pm_opt_f")}
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
            row.update({"acq_s": r.get("acq_s"), "fit_s": r.get("fit_s"), "wall_s": r.get("wall_s"),
                        "acq_warnings": sum((r.get("acq_warnings") or {}).values()) if r["round"] else None})
            rows.append(row)
    sdf = pd.DataFrame(rows).sort_values(["variant", "objective", "method", "seed_id", "round"])
    sdf.to_csv(SINGLE_CSV, index=False, float_format="%.10g")

    R = np.asarray([P["R"][o] for o in em.SEATED], float)
    hvF, hvP = front["hv_front"], front["hv_front_polished"]
    mrows = []
    for d in multi:
        base = {"label": "EMULATOR", "variant": d["variant"], "fit_epochs": d["fit_epochs"], "scenario": d["scenario"],
                "seed_id": d["seed_id"], "tau_exact_joint": d["tau_exact"]["tau_joint"],
                "budget_cap_only": d["tau_exact"]["budget_cap_only"], "tau_res": d["tau_res"]["tau_res"],
                "n0_tier": d["n0_tier"], "loader": d["loader"], "configs_source": d["configs_source"]}
        mrows.append({**base, "round": 0, "n": 48, "n_hv": 48, "hv": d["hv0"], "hv_true_f": d["hv0_true_f"],
                      "hv_obs_frac_polished": d["hv0"] / hvP, "hv_true_frac_polished": d["hv0_true_f"] / hvP,
                      "hv_true_frac_sobol": d["hv0_true_f"] / hvF, "wall_s": d["init_s"]})
        for r in d["rounds"]:
            if "hv" not in r:
                mrows.append({**base, "round": r["round"], "propose_refused": r.get("propose_refused"),
                              "C1_ok": r.get("C1_ok")})
                continue
            k = r["round"]
            row = {**base, "round": k, "n": r["n"], "n_hv": r["n_hv"], "hv": r["hv"], "hv_true_f": r["hv_true_f"],
                   "gain": r["gain"], "gain_over_tau_res": r["gain_over_tau_res"], "gain_tau_joint": r["gain_tau_joint"],
                   "would_stop_joint": r["would_stop_joint"], "would_stop_marginal": r["would_stop_marginal"],
                   "hv_obs_frac_polished": r["hv"] / hvP, "hv_true_frac_polished": r["hv_true_f"] / hvP,
                   "hv_true_frac_sobol": r["hv_true_f"] / hvF, "hv_obs_frac_sobol": r["hv"] / hvF,
                   "p_random": em.percentile(r["hv"], npz[f"k{k}"]),
                   "C1_ok": r["C1_ok"], "C2": r["C2"], "C3": r["C3"], "n_violations": len(r["violations"]),
                   "n_suspects": len(r["suspects"]), "guardrail_mode_after": r["guardrail_mode_after"],
                   "constraint_used": r["constraint_used"], "halt": r["halt"], "r2_flag": r["r2_flag"],
                   "r2_max": r["r2_max"], "n1_off_flag_a": r["n1_off_flag_a"], "n1_off_max": r["n1_off_max"],
                   "N4_mean": r["N4_mean"], "propose_s": r["propose_s"], "qnehvi_s": r["qnehvi_s"],
                   "grade_s": r["grade_s"], "wall_s": r["wall_s"],
                   "propose_warnings": sum((r.get("propose_warnings") or {}).values())}
            for o in em.SEATED:
                c = (r.get("calibration") or {}).get(o, {})
                row.update({f"{o}_cov95": c.get("cov95"), f"{o}_rms_z": c.get("rms_z"), f"{o}_mean_z": c.get("mean_z"),
                            f"{o}_n_abs_z_gt3": c.get("n_abs_z_gt3")})
                row[f"{o}_loo_rms_z_pre"] = (r.get("loo_rms_z") or {}).get(o)
                row[f"{o}_noise_raw_pre"] = (r.get("noise_raw") or {}).get(o)
            if k == 4:
                ps = np.array([em.percentile(r["hv"], b) for b in npz["boot"]])
                row["p_random_lo"], row["p_random_hi"] = float(np.percentile(ps, 5)), float(np.percentile(ps, 95))
            mrows.append(row)
    mdf = pd.DataFrame(mrows).sort_values(["variant", "scenario", "seed_id", "round"])
    mdf.to_csv(MULTI_CSV, index=False, float_format="%.10g")
    summ = summarize(P, front, pool, sdf, mdf, single, multi)
    with open(SUMMARY, "w") as f:
        json.dump(summ, f, indent=1, default=float)
        f.write("\n")
    print(json.dumps(summ["pass_fail"], indent=1, default=str))
    return sdf, mdf, summ


def summarize(P, front, pool, sdf, mdf, single, multi):
    pf = []
    hs = sdf[(sdf.variant == "house")]
    # 1 no crash: expected run files
    exp_single = {(o, m, s) for o in em.SEATED for m in ("bo", "random") for s in em.SEED_IDS_SINGLE}
    got_single = {(d["objective"], d["method"], d["seed_id"]) for d in single if d["variant"] == "house"}
    exp_multi = {(sc, s) for sc in em.SCEN for s in SEEDS_MULTI}
    got_multi = {(d["scenario"], d["seed_id"]) for d in multi if d["variant"] == "house"}
    hm = mdf[(mdf.variant == "house") & (mdf["round"] >= 1) & mdf["hv"].notna()]
    ends = {}
    for d in multi:
        if d["variant"] != "house":
            continue
        graded = [r["round"] for r in d["rounds"] if "hv" in r]
        ends[(d["scenario"], d["seed_id"])] = graded
    ok_ends = all((ends[k] == [1, 2, 3, 4]) if k[0] in ("s0", "s1") else (ends[k] == [1]) for k in ends)
    pf.append({"check": "no crash: every planned run finished (12 single house, 15 multi house lanes) and each lane "
                        "ended where its scenario says (s0/s1: 4 graded rounds; s2: r1 then HALT)",
               "result": f"single {len(got_single)}/12, multi {len(got_multi)}/15, lane ends as expected = {ok_ends}",
               "pass": bool(got_single == exp_single and got_multi == exp_multi and ok_ends),
               "note": "AS BUILT the multi-seed init CRASHED at seed 1 (55's r1 pairwise-disjointness assert; "
                       "shared vertex designs); PASS is after the disclosed one-line 55 change"})
    c1 = mdf[(mdf["round"] >= 1) & mdf["C1_ok"].notna()]["C1_ok"].astype(bool)
    pf.append({"check": "C1 ingest passes on every emulated round (55 ingest_gate)", "result": f"{int(c1.sum())}/{len(c1)}",
               "pass": bool(c1.all() and len(c1) > 0)})
    # C2 / C3 counts vs nominal
    sb = hs[(hs.method == "bo") & (hs["round"] >= 1)]
    n_so = len(sb)
    c2_so, c3_so = int(sb["C2"].astype(bool).sum()), int(sb["C3"].astype(bool).sum())
    n_mo = len(hm) * len(em.SEATED)
    c2_mo = int(sum((hm[f"{o}_cov95"] <= 4).sum() for o in em.SEATED))
    c3_mo = int(sum((hm[f"{o}_n_abs_z_gt3"] >= 3).sum() for o in em.SEATED))
    n_all = n_so + n_mo
    e2, e3 = n_all * C2_RATE, n_all * C3_RATE
    lim2, lim3 = int(poisson.ppf(0.95, e2)), int(poisson.ppf(0.95, e3))
    pf.append({"check": "C2 / C3 flag counts at or below nominal (per (round, objective): C2 3.7e-4, C3 1.1e-6; "
                        "PASS iff count <= Poisson 95 % quantile of the expected count)",
               "result": f"C2 {c2_so + c2_mo} (single {c2_so}/{n_so}, multi {c2_mo}/{n_mo}; expected {e2:.3f}, limit {lim2}); "
                         f"C3 {c3_so + c3_mo} (expected {e3:.1e}, limit {lim3})",
               "pass": bool(c2_so + c2_mo <= lim2 and c3_so + c3_mo <= lim3)})
    within, beats = {}, {}
    for o in em.SEATED:
        b4 = hs[(hs.objective == o) & (hs.method == "bo") & (hs["round"] == 4)].set_index("seed_id")["regret_best_obs_B"]
        r4 = hs[(hs.objective == o) & (hs.method == "random") & (hs["round"] == 4)].set_index("seed_id")["regret_best_obs_B"]
        within[o] = int((b4 <= 2.0).sum())
        beats[o] = {"bo_mean": float(b4.mean()), "random_mean": float(r4.mean()),
                    "per_seed": {int(s): bool(b4[s] < r4[s]) for s in b4.index}}
    pf.append({"check": "single-objective BO within 2 B_j of the emulator optimum by round 4 on >= 2 of 3 seeds "
                        "(regret of the best-observed design, true f)",
               "result": "; ".join(f"{o}: {within[o]}/3" for o in em.SEATED), "pass": all(v >= 2 for v in within.values())})
    pf.append({"check": "single-objective BO beats the random-8 baseline at matched budget (round 4, 80 evaluations) "
                        "on every objective (mean regret over 3 seeds; per-seed shown)",
               "result": "; ".join(f"{o}: BO {beats[o]['bo_mean']:.3f} B vs random {beats[o]['random_mean']:.3f} B, "
                                   f"per seed {beats[o]['per_seed']}" for o in em.SEATED),
               "pass": all(b["bo_mean"] < b["random_mean"] and all(b["per_seed"].values()) for b in beats.values())})
    # branch behaviour
    def lane(sc, s, v="house"):
        return next(d for d in multi if d["scenario"] == sc and d["seed_id"] == s and d["variant"] == v)
    s0_ok = all(lane("s0", s)["guardrail_mode"] == "monitor" and not lane("s0", s)["halt"] for s in SEEDS_MULTI)
    s1_ok = all(lane("s1", s)["guardrail_flipped_at_round"] == 1
                and all("shed <=" in (lane("s1", s)["settings"][str(k)] or {}).get("constraint", "") for k in (2, 3, 4))
                and (lane("s1", s)["settings"]["1"] or {}).get("constraint") == "none"
                and [r["n_hv"] for r in lane("s1", s)["rounds"]] == [55, 63, 71, 79] for s in SEEDS_MULTI)
    s2_ok = all(lane("s2", s)["halt"] and lane("s2", s)["halt_file"]
                and "HALT" in (lane("s2", s)["rounds"][-1].get("propose_refused") or "") for s in SEEDS_MULTI)
    pf.append({"check": "multi s0 clean: 4 rounds, guardrail_mode monitor, no halt (5 lanes)", "result": str(s0_ok), "pass": s0_ok})
    pf.append({"check": "multi s1 one injected shed violation in r1: mode flips at r1, constrained qNEHVI (shed GP) in r2-r4, "
                        "violating run out of HV (n_hv 55/63/71/79), r1 unconstrained (5 lanes)", "result": str(s1_ok), "pass": s1_ok})
    pf.append({"check": "multi s2 two injected violations in r1: HALT_FOR_DECISION.md written, propose r2 REFUSED (5 lanes)",
               "result": str(s2_ok), "pass": s2_ok})
    tz = all(d["tau_exact"]["budget_cap_only"] and d["tau_exact"]["tau_joint"] == 0 for d in multi)
    ws = mdf[(mdf["round"] >= 1) & mdf["hv"].notna()]
    tz2 = bool(tz and (~ws["would_stop_joint"].astype(bool)).all() and ws["gain_tau_joint"].isna().all())
    pf.append({"check": "tau_exact = 0 -> budget-cap-only: gain/tau_exact null, would_stop never fires, every lane to the cap",
               "result": str(tz2), "pass": tz2})
    mon = bool((~ws["r2_flag"].astype(bool)).all() and (~ws["n1_off_flag_a"].astype(bool)).all())
    pf.append({"check": "R2 / N1_off monitors at base + chatter: no flags (R2 > 312.16 MWh; dN1_off >= 462.7 line-h)",
               "result": f"R2 max {ws['r2_max'].max():.1f} MWh; N1_off max {ws['n1_off_max'].max():.0f}", "pass": mon})
    hm4 = mdf[(mdf.variant == "house") & (mdf["round"] == 4)]
    pf.append({"check": "HV fraction of the emulator front reported (no threshold; a finding)",
               "result": f"s0 true-f HV / polished front: {hm4[hm4.scenario == 's0']['hv_true_frac_polished'].round(4).tolist()}",
               "pass": True})
    return {"label": "EMULATOR", "pass_fail": pf, "within_2B": within, "beats_random": beats,
            "c_counts": {"single_C2": c2_so, "single_C3": c3_so, "multi_C2": c2_mo, "multi_C3": c3_mo,
                         "n_single": n_so, "n_multi": n_mo, "expected_C2": e2, "expected_C3": e3},
            "hv_front_sobol": front["hv_front"], "hv_front_polished": front["hv_front_polished"],
            "hv_random48_obs": pool["hv_all48_obs"], "hv_random48_true": pool["hv_all48_true"]}


# --------------------------------------------------------------------------- #
# figs (assert-before-draw)
# --------------------------------------------------------------------------- #

def _plt():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.size": 12, "font.weight": "bold", "axes.labelweight": "bold",
                         "axes.titleweight": "bold"})
    return plt


def _bold(ax):
    ax.figure.canvas.draw()
    for t in ax.get_xticklabels() + ax.get_yticklabels():
        t.set_fontweight("bold")
    ax.grid(alpha=0.3)


def _assert_frozen(sdf, mdf):
    """Recompute every plotted number from the raw run files and the frozen emulator; assert == CSV."""
    emu = em.load_emulator()
    single, multi = _runs()
    n = 0
    for d in single:
        f = emu["f"][d["objective"]]
        for r in d["records"]:
            row = sdf[(sdf.variant == d["variant"]) & (sdf.objective == d["objective"]) & (sdf.method == d["method"])
                      & (sdf.seed_id == d["seed_id"]) & (sdf["round"] == r["round"])]
            assert len(row) == 1
            reg = (f(np.asarray([r["best_obs_u"]]))[0] - d["f_star"]) / d["B"]       # independent path: u -> f
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
            Fa.append(em.true_f(dm[[c for c in dm.columns if c.startswith("u_")]].to_numpy(float))[ok])
            row = mdf[(mdf.variant == d["variant"]) & (mdf.scenario == d["scenario"]) & (mdf.seed_id == d["seed_id"])
                      & (mdf["round"] == k)]
            hv, hvt = em.hv2d(np.vstack(Ya), R), em.hv2d(np.vstack(Fa), R)
            assert abs(hv - float(row["hv"].iloc[0])) <= 1e-9 * hv, (w, hv)
            assert abs(hvt - float(row["hv_true_f"].iloc[0])) <= 1e-6 * hvt, (w, hvt)
            n += 1
    return n


def figs():
    plt = _plt()
    sdf = pd.read_csv(SINGLE_CSV)
    mdf = pd.read_csv(MULTI_CSV)
    n = _assert_frozen(sdf, mdf)
    print(f"assert-before-draw: {n} plotted values recomputed from the run files == CSV")
    os.makedirs(em.FIGS, exist_ok=True)
    out = []
    # 1 single-objective regret
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.6))
    for ax, o in zip(axes, em.SEATED):
        for (var, meth), sty in {("house", "bo"): dict(color="C0", lw=2.2, ls="-"),
                                 ("long", "bo"): dict(color="C2", lw=1.6, ls=":"),
                                 ("house", "random"): dict(color="0.45", lw=1.6, ls="--")}.items():
            g = sdf[(sdf.objective == o) & (sdf.variant == var) & (sdf.method == meth)]
            assert g["seed_id"].nunique() == 3 and g["regret_best_obs_B"].notna().all()
            for i, (s, gs) in enumerate(g.groupby("seed_id")):
                ax.plot(gs["round"], np.maximum(gs["regret_best_obs_B"], 1e-3), marker="o", ms=4,
                        label=((f"BO qLogNEI ({'Adam 10k, EXPLORATORY' if var == 'long' else 'house fit'})" if meth == 'bo' else 'random-8 (uniform u)')
                               if i == 0 else None), **sty)
        ax.axhline(2.0, color="C3", lw=1.4, ls="-.", label="2 B_j")
        ax.set_yscale("log")
        ax.set_xticks([0, 1, 2, 3, 4])
        ax.set_xlabel("Round (8 designs per round)")
        ax.set_ylabel(f"Regret of best observed, {o} (B units)")
        ax.set_title(f"{o}: B = {em.B[o]:,.0f}" + (" MWh" if o == "V1" else " $"))
        _bold(ax)
    axes[0].legend(fontsize=9, loc="center right")
    fig.suptitle("EMULATOR — single-objective BO vs random (3 seeds; floor 1e-3 for display)", fontweight="bold")
    fig.tight_layout()
    p = os.path.join(em.FIGS, "fig_EMU_single_regret.png")
    fig.savefig(p, dpi=150)
    plt.close(fig)
    out.append(p)
    # 2 multi HV trajectory vs random band
    pool = _load(os.path.join(em.RUNS, "EMU_random_pool.json"))
    front = _load(os.path.join(em.RUNS, "EMU_front.json"))
    hvP = front["hv_front_polished"]
    fig, ax = plt.subplots(figsize=(8.5, 5))
    q = pool["subset_quantiles"]
    ks = [1, 2, 3, 4]
    hv0 = float(mdf[(mdf["round"] == 0)]["hv"].iloc[0])
    lo = [hv0 / hvP] + [q[str(k)][0] / hvP for k in ks]
    hi = [hv0 / hvP] + [q[str(k)][2] / hvP for k in ks]
    ax.fill_between([0] + ks, lo, hi, color="0.75", alpha=0.6, label="random 8k-subsets p10-p90 (48-pool)")
    for (sc, var), sty in {("s0", "house"): dict(color="C0", lw=2), ("s1", "house"): dict(color="C1", lw=1.6, ls="--"),
                           ("s0", "long"): dict(color="C2", lw=1.6, ls=":")}.items():
        g = mdf[(mdf.scenario == sc) & (mdf.variant == var) & mdf["hv"].notna()]
        assert len(g) > 0
        for i, (s, gs) in enumerate(g.groupby("seed_id")):
            ax.plot(gs["round"], gs["hv"] / hvP, marker="o", ms=4,
                    label=(f"qNEHVI {sc}{' (Adam 10k, EXPLORATORY)' if var == 'long' else ''}" if i == 0 else None), **sty)
    ax.axhline(front["hv_front"] / hvP, color="C3", ls="-.", lw=1.3, label="dense Sobol 2^14 front (spec)")
    ax.axhline(1.0, color="k", lw=1.2, label="polished emulator front")
    ax.set_xticks([0, 1, 2, 3, 4])
    ax.set_xlabel("Round")
    ax.set_ylabel("Observed HV / HV(polished emulator front)")
    ax.set_title("EMULATOR — qNEHVI (55 machinery) HV trajectory, 5 seed lanes")
    ax.legend(fontsize=9, loc="lower right")
    _bold(ax)
    fig.tight_layout()
    p = os.path.join(em.FIGS, "fig_EMU_multi_hv.png")
    fig.savefig(p, dpi=150)
    plt.close(fig)
    out.append(p)
    # 3 objective space
    P = _load(em.PARAMS)
    F0 = np.asarray(P["start_set"]["f"], float)
    fr = np.asarray(front["front_polished"], float)
    fs = np.asarray(front["front"], float)
    Fp = np.asarray(pool["f"], float)
    fig, ax = plt.subplots(figsize=(8.5, 6))
    ax.scatter(F0[:, 0] / 1e6, F0[:, 1] / 1e9, s=18, c="0.5", label="start set (n0_E, f)")
    ax.scatter(Fp[:, 0] / 1e6, Fp[:, 1] / 1e9, s=18, marker="x", c="0.3", label="random 48 (f)")
    for s in SEEDS_MULTI:
        U = []
        for k in range(1, 5):
            dm = pd.read_csv(os.path.join(HERE, "waves", f"methods_E_EMU_house_s0_s{s}_r{k}", "design_matrix.csv"))
            U.append(dm[[c for c in dm.columns if c.startswith("u_")]].to_numpy(float))
        F = em.true_f(np.vstack(U))
        assert F.shape == (32, 2) and np.isfinite(F).all()
        ax.scatter(F[:, 0] / 1e6, F[:, 1] / 1e9, s=16, c="C0", alpha=0.6, label="qNEHVI s0, 5 lanes (f)" if s == 0 else None)
    ax.plot(fs[:, 0] / 1e6, fs[:, 1] / 1e9, "-", color="C3", lw=1.3, label="front, Sobol 2^14 (spec)")
    ax.plot(fr[:, 0] / 1e6, fr[:, 1] / 1e9, "-", color="k", lw=1.6, label="front, polished")
    R = P["R"]
    ax.axvline(R["V1"] / 1e6, color="C4", ls=":", lw=1.2)
    ax.axhline(R["E1"] / 1e9, color="C4", ls=":", lw=1.2, label="R (landing_R.json)")
    ax.set_xlabel("V1 curtailment f (TWh)")
    ax.set_ylabel("E1 system cost f ($B)")
    ax.set_title("EMULATOR — objective space (true f at every evaluated design)")
    ax.legend(fontsize=8.5, loc="upper right")
    _bold(ax)
    fig.tight_layout()
    p = os.path.join(em.FIGS, "fig_EMU_front.png")
    fig.savefig(p, dpi=150)
    plt.close(fig)
    out.append(p)
    # 4 calibration
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.4))
    for ax, o in zip(axes, em.SEATED):
        for var, sty in {"house": dict(color="C0"), "long": dict(color="C2")}.items():
            g = sdf[(sdf.objective == o) & (sdf.method == "bo") & (sdf.variant == var) & (sdf["round"] >= 1)]
            assert g["rms_z"].notna().all()
            ax.scatter(g["round"] - 0.12, g["rms_z"], marker="o", s=30,
                       label=f"single, {'house' if var == 'house' else 'Adam 10k (EXPL.)'}", **sty)
            gm = mdf[(mdf.variant == var) & (mdf.scenario != "s2") & (mdf["round"] >= 1) & mdf["hv"].notna()]
            ax.scatter(gm["round"] + 0.12, gm[f"{o}_rms_z"], marker="^", s=30,
                       label=f"multi (55 grade_round), {'house' if var == 'house' else 'Adam 10k (EXPL.)'}", **sty)
        ax.axhline(1.0, color="k", lw=1.2, label="calibrated (rms z = 1)")
        ax.set_xticks([1, 2, 3, 4])
        ax.set_xlabel("Round")
        ax.set_ylabel(f"{o}: rms z of the 8 new points")
        ax.set_title(f"{o}: pre-round GP vs emulated outcome")
        _bold(ax)
    axes[1].legend(fontsize=8.5)
    fig.suptitle("EMULATOR — calibration of each round's 8 points (C2/C3 inputs)", fontweight="bold")
    fig.tight_layout()
    p = os.path.join(em.FIGS, "fig_EMU_calibration.png")
    fig.savefig(p, dpi=150)
    plt.close(fig)
    out.append(p)
    print("\n".join(out))
    return out


def tables():
    """Markdown tables for EMULATOR_BO.md, from the frozen CSVs."""
    sdf = pd.read_csv(SINGLE_CSV)
    mdf = pd.read_csv(MULTI_CSV)
    print("### single (regret of the best-observed design, B units; r0 = start set)\n")
    print("| variant | obj | method | seed | r0 | r1 | r2 | r3 | r4 | pm-opt r4 | cov95 r1-r4 | rms_z r1-r4 | ls drift r4 vs r0 | wall s |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for (v, o, m, s), g in sdf.groupby(["variant", "objective", "method", "seed_id"]):
        g = g.sort_values("round")
        reg = " | ".join(f"{x:.3f}" for x in g["regret_best_obs_B"])
        b = g[g["round"] >= 1]
        pm = f"{g['regret_pm_opt_B'].iloc[-1]:.3f}" if m == "bo" else "-"
        cov = "/".join(str(int(x)) for x in b["cov95"]) if m == "bo" else "-"
        rz = "/".join(f"{x:.2f}" for x in b["rms_z"]) if m == "bo" else "-"
        ld = f"{g['ls_drift_vs_r0_max'].iloc[-1]:.2f}" if m == "bo" else "-"
        print(f"| {v} | {o} | {m} | {s} | {reg} | {pm} | {cov} | {rz} | {ld} | {b['wall_s'].sum():.1f} |")
    print("\n### multi (observed HV / polished front; true-f HV / polished; p_random)\n")
    print("| variant | scen | seed | rounds graded | obs frac r1..r4 | true frac r4 | true frac r4 vs Sobol front | gain/tau_res r1..r4 | p_random r1..r4 | p interval r4 | C2/C3 | wall s per round |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for (v, sc, s), g in mdf.groupby(["variant", "scenario", "seed_id"]):
        g = g[(g["round"] >= 1) & g["hv"].notna()].sort_values("round")
        last = g.iloc[-1]
        print(f"| {v} | {sc} | {s} | {len(g)} | {'/'.join(f'{x:.4f}' for x in g['hv_obs_frac_polished'])} | "
              f"{last['hv_true_frac_polished']:.4f} | {last['hv_true_frac_sobol']:.4f} | "
              f"{'/'.join(f'{x:.1f}' for x in g['gain_over_tau_res'])} | {'/'.join(f'{x:.3f}' for x in g['p_random'])} | "
              + (f"[{last['p_random_lo']:.3f}, {last['p_random_hi']:.3f}]" if 'p_random_lo' in g and pd.notna(last.get('p_random_lo')) else "-")
              + f" | {int(g['C2'].astype(bool).sum())}/{int(g['C3'].astype(bool).sum())} | {'/'.join(f'{x:.1f}' for x in g['wall_s'])} |")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["collect", "figs", "report"])
    a = ap.parse_args(argv)
    if a.cmd == "collect":
        collect()
    elif a.cmd == "figs":
        figs()
    elif a.cmd == "report":
        tables()
    return 0


if __name__ == "__main__":
    sys.exit(main())
