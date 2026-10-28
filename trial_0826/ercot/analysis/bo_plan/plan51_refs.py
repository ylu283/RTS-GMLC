"""Prompt 51: every number ERCOT_BO_PLAN.md quotes, computed from NAMED artifacts.

Zero simulation. Reads only artifacts present at HEAD 7c5fb8d (branch
ercot/tx123) — no v2 solver-identity confirm run exists or is read
(blind-freeze, prompt 51 §3.1). Writes plan51_refs.json beside this file.

Run (any python with pandas + scipy):
  /opt/anaconda3/envs/bogp-botorch/bin/python analysis/bo_plan/plan51_refs.py
"""
import json
import os

import numpy as np
import pandas as pd
from scipy.stats import binom

HERE = os.path.dirname(os.path.abspath(__file__))
ERCOT = os.path.abspath(os.path.join(HERE, "..", ".."))
EXTR = os.path.join(ERCOT, "extracts")

# --- named artifacts (prompt 51 §3.1: the readability test may use ONLY these)
BASE = [f"base_2019_v2/run_index_{i}" for i in (1, 2, 3)]
SCREEN_ERCOT = [f"screening_v2/ercot/run_index_{i}" for i in range(1, 13)]
SCREEN_TOPUP = [f"screening_v2/topup/run_index_{i}" for i in range(1, 8)]
# single-site rows: ercot 1-9 and topup 1-7 (ercot 10 = __ALL__, 11 = base replicate,
# 12 = replicate of row 1 — SCREENING / ERCOT_COST_FIX conventions)
SINGLE = [f"screening_v2/ercot/run_index_{i}" for i in range(1, 10)] + SCREEN_TOPUP
NUCLEAR = ("1", "93")


def read_run(key):
    d = os.path.join(EXTR, key)
    o = pd.read_csv(os.path.join(d, "overall.csv")).iloc[0]
    g = pd.read_csv(os.path.join(d, "gen_summary.csv"))
    g["Generator"] = g["Generator"].astype(str)
    q = pd.read_csv(os.path.join(d, "ruc_quality.csv"))
    return {"total": float(o["Total costs"]), "fixed": float(o["Total fixed costs"]),
            "var": float(o["Total generation costs"]), "shed": float(o["Total load shedding"]),
            "reserve": float(o["Total reserve shortfall"]),
            "nuc_starts": {k: float(g[g.Generator == k].starts.iloc[0]) for k in NUCLEAR},
            "ruc_status": sorted(q.status.astype(str).unique().tolist()),
            "ruc_n": int(len(q)), "max_gap_pct": float(q.final_gap_pct.max())}


def readability_refs():
    runs = {k: read_run(k) for k in BASE + SCREEN_ERCOT + SCREEN_TOPUP}
    ident = max(abs(r["total"] - r["fixed"] - r["var"]) for r in runs.values())
    b = runs[BASE[0]]
    d = np.array([[runs[k][c] - b[c] for c in ("total", "fixed", "var")] for k in SINGLE])
    rep_pairs = [(BASE[0], BASE[1]), (BASE[0], BASE[2]), (BASE[0], "screening_v2/ercot/run_index_11"),
                 ("screening_v2/ercot/run_index_1", "screening_v2/ercot/run_index_12")]
    rep = {f"{a} vs {c}": {k: abs(runs[a][k] - runs[c][k]) for k in ("total", "fixed", "var")}
           for a, c in rep_pairs}
    return {
        "artifacts": BASE + SCREEN_ERCOT + SCREEN_TOPUP,
        "n_runs": len(runs),
        "max_identity_residual_usd": ident,
        "all_shed_zero": all(r["shed"] == 0 for r in runs.values()),
        "nuclear_starts_all_zero": all(v == 0 for r in runs.values() for v in r["nuc_starts"].values()),
        "ruc_status_set": sorted({s for r in runs.values() for s in r["ruc_status"]}),
        "ruc_solves": sum(r["ruc_n"] for r in runs.values()),
        "max_final_gap_pct": max(r["max_gap_pct"] for r in runs.values()),
        "replicate_abs_delta_usd": rep,
        "single_site_n": len(SINGLE),
        "single_site_median_abs_delta_usd": {c: float(np.median(np.abs(d[:, j])))
                                             for j, c in enumerate(("total", "fixed", "var"))},
        "single_site_fixed_var_opposite_sign": int((np.sign(d[:, 1]) != np.sign(d[:, 2])).sum()),
        "single_site_median_ratio_absfixed_absvar": float(np.median(np.abs(d[:, 1]) / np.abs(d[:, 2]))),
        "single_site_rows_var_and_total_opposite_sign": int((np.sign(d[:, 0]) != np.sign(d[:, 2])).sum()),
        "base_reserve_shortfall_mwh": b["reserve"],
    }


def cov95_bar(alpha=0.10):
    out = {"alpha": alpha, "definition": "scipy.stats.binom.interval(1 - alpha, n, 0.95)"}
    out["bars"] = {n: [int(x) for x in binom.interval(1 - alpha, n, 0.95)] for n in (24, 32, 40, 48, 56, 64, 96)}
    assert out["bars"][48] == [43, 48]
    # every alpha reproducing [43, 48] at n = 48: P(X<=42) <= alpha/2 < P(X<=43)
    lo, hi = 2 * binom.cdf(42, 48, 0.95), 2 * binom.cdf(43, 48, 0.95)
    out["alpha_range_reproducing_43_48"] = [lo, hi]
    out["house_binom_band_default_level095_at48"] = [int(x) for x in binom.interval(0.95, 48, 0.95)]
    return out


def calib_gate():
    # per round q = 8 new points, pre-round GP 95% total band: P(covered <= k | 8, 0.95)
    return {"q": 8, "P_cov_le_k": {k: float(binom.cdf(k, 8, 0.95)) for k in range(0, 8)},
            "P_absz_gt3_ge3_of_8": float(binom.sf(2, 8, 2 * (1 - 0.99865)))}


def budget():
    perrun = {"v1_low": 60, "v1_high": 88, "v2_low": 12, "v2_high": 25}
    d = 6
    fixed_rows = {"replicates_52": 12, "n0_grading_53": max(8 * d, 48), "holdout_random_E": 48}
    options = {
        "A_minimal": {"arms": 1, "seeds": 1, "cap": 4},
        "B_pair": {"arms": 2, "seeds": 2, "cap": 4},
        "C_pi_seeds": {"arms": 1, "seeds": 5, "cap": 4},
        "D_full": {"arms": 2, "seeds": 5, "cap": 6},
    }
    q = 8
    rows = {}
    for name, o in options.items():
        bo = o["arms"] * o["seeds"] * o["cap"] * q
        for dual in (False, True):
            runs = fixed_rows["replicates_52"] + fixed_rows["n0_grading_53"] + bo + 48  # + baseline 48
            runs += 0 if dual else fixed_rows["holdout_random_E"]
            rows[f"{name}{'_dual' if dual else ''}"] = {
                **o, "bo_runs": bo, "total_runs": runs,
                "core_h": {k: runs * v for k, v in perrun.items()}}
    return {"d_assumed": d, "q": q, "per_run_core_h": perrun, "fixed_rows": fixed_rows,
            "baseline_runs": 48, "options": rows}


if __name__ == "__main__":
    out = {"readability": readability_refs(), "cov95": cov95_bar(), "calibration": calib_gate(),
           "budget": budget()}
    with open(os.path.join(HERE, "plan51_refs.json"), "w") as f:
        json.dump(out, f, indent=1)
        f.write("\n")
    print(json.dumps({k: out["readability"][k] for k in (
        "n_runs", "max_identity_residual_usd", "all_shed_zero", "nuclear_starts_all_zero",
        "ruc_status_set", "ruc_solves", "single_site_median_abs_delta_usd",
        "single_site_fixed_var_opposite_sign", "single_site_median_ratio_absfixed_absvar",
        "single_site_rows_var_and_total_opposite_sign")}, indent=1))
    print(json.dumps(out["cov95"], indent=1))
    print(json.dumps(out["calibration"], indent=1))
    for k, v in out["budget"]["options"].items():
        print(k, v["bo_runs"], v["total_runs"], v["core_h"])
