#!/usr/bin/env python3
"""Prompt 52 v2.1 — read the noise_v3 extracts and write ERCOT_NOISE.md (zero simulation).

    cd trial_0826/ercot && python analysis/noise_v3/read_noise.py
        [--extr extracts] [--waves waves] [--out-dir analysis/noise_v3] [--no-strict]

Inputs: extracts/noise_v3/<batch>/run_index_N (slim tables + pool_full_metrics.json
+ identity.txt; the gz tables stay on CRC), extracts/noise_v3/<batch>/wallclock.csv,
GAP_DECISION_used.json, waves/noise_v3/<batch>/design_matrix.csv. Every candidate
value comes from pool_objectives.pool_row (reused, not copied); E8/E9/N5 come
from the CRC-computed pool_full_metrics.json when the gz tables are absent here.

Two populations, never pooled (prompt 52 section 1):
- EXACT cross-batch pairs (A exact vs B exact of the same design): the noise
  population tau. Expected 0; reported as exact zeros when 0.
- PERTURBED copies (delta = 0.001 relative on pem_mw) vs the exact copy of the
  same design in the same batch: local input sensitivity; |delta| population,
  median = ruler_j (prompt 57 section 3 A4), min, max, RULER=0 flag.

Per objective: per-level (= per design) sd with chi-square CIs, pooled sd with
Satterthwaite df, the variance-ratio trigger (F test alpha = 0.05 AND point
ratio > 3) with one family-wise disclosure line; the cross-objective covariance
matrix of the perturbed deltas; the shed == 0 assert; the runtime table
(wall-clock per run -> core-h). pandas/numpy only (the chi-square and F
quantiles are computed here from the incomplete gamma / beta functions).

Outputs (--out-dir): ERCOT_NOISE.md (STE-100), ercot_noise.csv, ercot_noise.json,
ercot_noise_cov.csv.
"""
import argparse
import json
import math
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ERCOT = os.path.abspath(os.path.join(HERE, "..", ".."))
if ERCOT not in sys.path:
    sys.path.insert(0, ERCOT)
import pool_objectives as po  # noqa: E402

WAVE = "noise_v3"
BATCHES = ("A", "B")
ALPHA = 0.05
POINT_RATIO = 3.0
SLOTS = 4
FULL_ONLY = ("E8", "E9", "N5")
JSON_OVERRIDE = ("E8", "E9", "N5", "N5_unweighted_check", "E9_lmp_max")
PLAN_UNKNOWN = "Per-run core-h on v2 is UNKNOWN"
EXACT_ZERO_FINDING = ("If their sd is 0, τ collapses toward 0 and the stop rule becomes "
                      "budget-cap-only — that is a FINDING about a deterministic instrument, "
                      "stated in exactly those words, not a failure.")


# --------------------------------------------------------------------------
# special functions (numpy/math only; validated against scipy in the tests)
# --------------------------------------------------------------------------
def _gammainc_P(a, x, eps=1e-14, itmax=500):
    """Regularized lower incomplete gamma P(a, x) (series / continued fraction)."""
    if x <= 0.0:
        return 0.0
    gln = math.lgamma(a)
    if x < a + 1.0:
        ap, s, d = a, 1.0 / a, 1.0 / a
        for _ in range(itmax):
            ap += 1.0
            d *= x / ap
            s += d
            if abs(d) < abs(s) * eps:
                break
        return s * math.exp(-x + a * math.log(x) - gln)
    b, c, d = x + 1.0 - a, 1.0 / 1e-300, 1.0 / (x + 1.0 - a)
    h = d
    for i in range(1, itmax + 1):
        an = -i * (i - a)
        b += 2.0
        d = an * d + b
        d = 1e-300 if abs(d) < 1e-300 else d
        c = b + an / c
        c = 1e-300 if abs(c) < 1e-300 else c
        d = 1.0 / d
        de = d * c
        h *= de
        if abs(de - 1.0) < eps:
            break
    return 1.0 - math.exp(-x + a * math.log(x) - gln) * h


def _betacf(a, b, x, eps=1e-14, itmax=500):
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c, d = 1.0, 1.0 - qab * x / qap
    d = 1e-300 if abs(d) < 1e-300 else d
    d = 1.0 / d
    h = d
    for m in range(1, itmax + 1):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        d = 1e-300 if abs(d) < 1e-300 else d
        c = 1.0 + aa / c
        c = 1e-300 if abs(c) < 1e-300 else c
        d = 1.0 / d
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        d = 1e-300 if abs(d) < 1e-300 else d
        c = 1.0 + aa / c
        c = 1e-300 if abs(c) < 1e-300 else c
        d = 1.0 / d
        de = d * c
        h *= de
        if abs(de - 1.0) < eps:
            break
    return h


def _betainc(a, b, x):
    """Regularized incomplete beta I_x(a, b)."""
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    bt = math.exp(math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b)
                  + a * math.log(x) + b * math.log(1.0 - x))
    if x < (a + 1.0) / (a + b + 2.0):
        return bt * _betacf(a, b, x) / a
    return 1.0 - bt * _betacf(b, a, 1.0 - x) / b


def chi2_cdf(x, k):
    return _gammainc_P(k / 2.0, x / 2.0)


def chi2_ppf(q, k, tol=1e-12):
    """Quantile by bisection (k > 0, 0 < q < 1)."""
    lo, hi = 0.0, max(10.0, 10.0 * k)
    while chi2_cdf(hi, k) < q:
        hi *= 2.0
    for _ in range(300):
        mid = 0.5 * (lo + hi)
        if chi2_cdf(mid, k) < q:
            lo = mid
        else:
            hi = mid
        if hi - lo < tol * max(1.0, hi):
            break
    return 0.5 * (lo + hi)


def f_cdf(x, d1, d2):
    if x <= 0.0:
        return 0.0
    if not np.isfinite(x):
        return 1.0
    return _betainc(d1 / 2.0, d2 / 2.0, d1 * x / (d1 * x + d2))


def f_sf(x, d1, d2):
    return 1.0 - f_cdf(x, d1, d2)


def sd_ci(s, df, alpha=ALPHA):
    """Chi-square CI for a standard deviation with df degrees of freedom."""
    if df <= 0 or not np.isfinite(s):
        return (np.nan, np.nan)
    return (s * math.sqrt(df / chi2_ppf(1.0 - alpha / 2.0, df)),
            s * math.sqrt(df / chi2_ppf(alpha / 2.0, df)))


# --------------------------------------------------------------------------
# inputs
# --------------------------------------------------------------------------
def candidate_ids(defs):
    gradable = list(defs["global_order"][:22])
    reported = [c for c in po.CAND_IDS if c not in gradable]
    return gradable, gradable + reported


def read_wallclock(path):
    if not os.path.isfile(path):
        return {}
    w = pd.read_csv(path)
    return {int(r["task"]): (float(r["wall_s"]) if pd.notna(r["wall_s"]) else np.nan)
            for _, r in w.iterrows()}


def read_identity(run_dir):
    p = os.path.join(run_dir, "identity.txt")
    if not os.path.isfile(p):
        return None
    line = open(p).read().strip()
    out = {"line": line}
    for tok in line.split():
        if tok.startswith("ruc_mipgap="):
            out["ruc_mipgap"] = float(tok.split("=", 1)[1])
        elif tok.startswith("ruc_time_limit="):
            out["ruc_time_limit"] = float(tok.split("=", 1)[1])
    return out


def read_runtimes(run_dir):
    p = os.path.join(run_dir, "runtimes.csv")
    if not os.path.isfile(p):
        return {"runtimes_present": False}
    try:
        t = pd.read_csv(p)
    except Exception as e:  # noqa: BLE001
        return {"runtimes_present": True, "runtimes_error": str(e)}
    out = {"runtimes_present": True, "runtimes_rows": int(len(t)), "runtimes_columns": list(map(str, t.columns))}
    num = t.select_dtypes("number")
    if len(num.columns):
        out["runtimes_numeric_sums"] = {str(c): float(num[c].sum()) for c in num.columns}
    return out


def load_rows(extr, waves, data_dir=po.DATA, defs=None, wave=WAVE, batches=BATCHES):
    """One record per extracted run (pool_row + design-matrix copy metadata +
    pool_full_metrics.json + identity + wall-clock). Missing extracts are listed."""
    defs = defs or po.load_defs()
    recs, missing, gap_used = [], [], {}
    for b in batches:
        bwave = f"{wave}/{b}"
        dm = pd.read_csv(os.path.join(waves, bwave, "design_matrix.csv"),
                         dtype={"oat_site": str, "replicate_of": str, "unit_type": str,
                                "copy_type": str, "batch": str, "design_id": str})
        bextr = os.path.join(extr, bwave)
        wall = read_wallclock(os.path.join(bextr, "wallclock.csv"))
        gp = os.path.join(bextr, "GAP_DECISION_used.json")
        if os.path.isfile(gp):
            with open(gp) as f:
                gap_used[b] = json.load(f)
        for _, r in dm.iterrows():
            idx = int(r["index"])
            key = f"{bwave}:{idx}"
            d = po.run_dir(key, extr)
            if not os.path.isfile(os.path.join(d, "overall.csv")):
                missing.append(key)
                continue
            row = po.pool_row(key, extr=extr, waves=waves, data_dir=data_dir, defs=defs)
            jp = os.path.join(d, "pool_full_metrics.json")
            row["pool_full_metrics_present"] = os.path.isfile(jp)
            if row["pool_full_metrics_present"]:
                with open(jp) as f:
                    pm = json.load(f)
                for c in JSON_OVERRIDE:
                    v = pm.get(c)
                    v = np.nan if v is None else float(v)
                    if np.isfinite(row.get(c, np.nan)) and np.isfinite(v):
                        assert abs(row[c] - v) <= 1e-6 * max(1.0, abs(v)), (key, c, row[c], v)
                    row[c] = v if np.isfinite(v) else row.get(c, np.nan)
                row["full_extract"] = bool(pm.get("full_extract", row["full_extract"]))
                row["n_ruc_time_limit"] = pm.get("n_ruc_time_limit")
                row["gz_verified"] = pm.get("manifest", {}).get("gz_verified")
            row.update({"batch": b, "copy_type": str(r["copy_type"]), "design_no": int(r["design_no"]),
                        "design_id": str(r["design_id"]), "perturb_sign": int(r["perturb_sign"]),
                        "delta_rel": float(r["delta_rel"]), "pem_mw_design": float(r["pem_mw"]),
                        "pem_mw_origin": float(r["pem_mw_origin"]), "origin_key": str(r["replicate_of"]),
                        "wall_s": wall.get(idx, np.nan), "identity": read_identity(d)})
            row.update(read_runtimes(d))
            recs.append(row)
    return recs, missing, gap_used


# --------------------------------------------------------------------------
# populations
# --------------------------------------------------------------------------
def _val(rec, c):
    v = rec.get(c, np.nan)
    try:
        return float(v)
    except (TypeError, ValueError):
        return np.nan


def exact_pairs(recs, ids):
    """Per design: B exact - A exact for every candidate; md5 identity of overall.csv."""
    out = {}
    byd = {}
    for r in recs:
        if r["copy_type"] == "exact":
            byd.setdefault(r["design_no"], {})[r["batch"]] = r
    for n in sorted(byd):
        pair = byd[n]
        if "A" not in pair or "B" not in pair:
            out[n] = {"complete": False, "present": sorted(pair)}
            continue
        a, b = pair["A"], pair["B"]
        out[n] = {"complete": True, "key_A": a["key"], "key_B": b["key"],
                  "overall_md5_equal": a["overall_md5"] == b["overall_md5"],
                  "delta": {c: _val(b, c) - _val(a, c) for c in ids}}
    return out


def perturbed_deltas(recs, ids):
    """Per perturbed run: value - exact copy of the same design in the same batch
    (fallback: the batch-A exact). Rows = perturbed runs."""
    ex = {(r["design_no"], r["batch"]): r for r in recs if r["copy_type"] == "exact"}
    rows = []
    for r in recs:
        if r["copy_type"] != "perturbed":
            continue
        ref = ex.get((r["design_no"], r["batch"])) or ex.get((r["design_no"], "A"))
        if ref is None:
            continue
        d = {"key": r["key"], "design_no": r["design_no"], "batch": r["batch"], "ref_key": ref["key"],
             "perturb_sign": r["perturb_sign"], "delta_rel": r["delta_rel"],
             "pem_mw": r["pem_mw_design"], "pem_mw_ref": ref["pem_mw_design"]}
        for c in ids:
            d[c] = _val(r, c) - _val(ref, c)
        rows.append(d)
    return pd.DataFrame(rows)


def level_sd(deltas):
    """sd of {0} U deltas (the exact copy and its perturbed copies), ddof = 1."""
    v = np.array([0.0] + [float(x) for x in deltas if np.isfinite(x)])
    nu = len(v) - 1
    if nu < 1:
        return np.nan, 0
    return float(np.std(v, ddof=1)), nu


def pooled_sd(levels):
    """levels = [(s_i, nu_i)]; pooled sd and Satterthwaite df for the pooled variance."""
    lv = [(s, nu) for s, nu in levels if nu >= 1 and np.isfinite(s)]
    if not lv:
        return np.nan, 0
    num = sum(nu * s * s for s, nu in lv)
    den = sum(nu for _, nu in lv)
    sp = math.sqrt(num / den)
    if num == 0.0:
        return 0.0, den
    df = num * num / sum((nu * s * s) ** 2 / nu for s, nu in lv)
    return sp, float(df)


def trigger(levels, alpha=ALPHA, point=POINT_RATIO):
    """Variance-ratio trigger per objective: max s^2 / min s^2 over levels with
    nu >= 1; F test one-sided at alpha AND point ratio > point."""
    lv = [(s, nu) for s, nu in levels if nu >= 1 and np.isfinite(s)]
    out = {"n_levels": len(lv), "ratio": np.nan, "p": np.nan, "df_num": None, "df_den": None,
           "fires": False, "verdict": "no level with df >= 1"}
    if len(lv) < 2:
        return out
    var = [(s * s, nu) for s, nu in lv]
    vmax, numax = max(var, key=lambda t: t[0])
    vmin, numin = min(var, key=lambda t: t[0])
    out.update({"df_num": numax, "df_den": numin})
    if vmax == 0.0:
        out["verdict"] = "all levels sd 0 (exact zeros): not detectable at this df"
        out["ratio"] = np.nan
        return out
    if vmin == 0.0:
        out["ratio"] = float("inf")
        out["p"] = 0.0
        out["fires"] = True
        out["verdict"] = ("TRIGGER: a level has sd 0 and another sd > 0 (ratio undefined); "
                          "scalar sd rejected per objective")
        return out
    ratio = vmax / vmin
    p = f_sf(ratio, numax, numin)
    fires = bool(p < alpha and ratio > point)
    out.update({"ratio": float(ratio), "p": float(p), "fires": fires,
                "verdict": (f"TRIGGER: scalar sd rejected (ratio {ratio:.2f} > {point:g}, p = {p:.3g} < {alpha})"
                            if fires else
                            f"not detectable at this df (ratio {ratio:.2f}, p = {p:.3g}; df {numax}/{numin})")})
    return out


def summarize(recs, ids, gradable, defs, missing):
    ex = exact_pairs(recs, ids)
    pert = perturbed_deltas(recs, ids)
    per_cand = {}
    for c in ids:
        cd = defs["candidates"].get(c, {})
        # exact population
        ed = [ex[n]["delta"][c] for n in ex if ex[n]["complete"]]
        ed_f = [x for x in ed if np.isfinite(x)]
        ex_levels = [(abs(x) / math.sqrt(2.0), 1) for x in ed_f]
        ex_sp, ex_df = pooled_sd(ex_levels)
        # perturbed population
        if len(pert):
            pv = pert[c].to_numpy(dtype=float)
            pabs = np.abs(pv[np.isfinite(pv)])
            levels = []
            for n in sorted(pert["design_no"].unique()):
                s, nu = level_sd(pert.loc[pert["design_no"] == n, c].to_numpy(dtype=float))
                levels.append((n, s, nu))
        else:
            pabs, levels = np.array([]), []
        sp, df = pooled_sd([(s, nu) for _, s, nu in levels])
        tr = trigger([(s, nu) for _, s, nu in levels])
        available = len(pabs) > 0
        ruler = float(np.median(pabs)) if available else np.nan
        lo, hi = sd_ci(sp, df) if available and np.isfinite(sp) else (np.nan, np.nan)
        exact_zero = bool(len(ed_f) > 0 and all(x == 0.0 for x in ed_f))
        per_cand[c] = {
            "id": c, "family": cd.get("family"), "name": cd.get("name"), "unit": cd.get("unit"),
            "dir": cd.get("dir"), "gradable": c in gradable, "needs_full": bool(cd.get("needs_full", False)),
            "n_exact_pairs": len(ed_f), "exact_delta": ed, "exact_abs_delta_max": (max(abs(x) for x in ed_f) if ed_f else np.nan),
            "exact_zero": exact_zero, "exact_pooled_sd": ex_sp, "exact_df": ex_df,
            "n_perturbed": int(len(pabs)), "perturbed_abs_delta": [float(x) for x in pabs],
            "perturbed_delta_signed": ([float(x) for x in pert[c].to_numpy(dtype=float)] if len(pert) else []),
            "ruler": ruler, "ruler_min": (float(pabs.min()) if available else np.nan),
            "ruler_max": (float(pabs.max()) if available else np.nan),
            "ruler_status": ("RULER UNAVAILABLE" if not available else ("RULER=0" if ruler == 0.0 else "RULER")),
            "levels": [{"design_no": int(n), "sd": s, "df": nu, "sd_ci95": list(sd_ci(s, nu)) if nu >= 1 and np.isfinite(s) else [np.nan, np.nan]}
                       for n, s, nu in levels],
            "pooled_sd": sp, "pooled_df_satterthwaite": df, "pooled_sd_ci95": [lo, hi],
            "trigger": tr,
        }
    ruler_zero = [c for c in gradable if per_cand[c]["ruler_status"] == "RULER=0"]
    ruler_unavail = [c for c in gradable if per_cand[c]["ruler_status"] == "RULER UNAVAILABLE"]
    all_exact_zero = all(per_cand[c]["exact_zero"] for c in gradable if per_cand[c]["n_exact_pairs"] > 0)
    n_pairs = sum(1 for n in ex if ex[n]["complete"])
    md5_equal = sum(1 for n in ex if ex[n]["complete"] and ex[n]["overall_md5_equal"])
    # covariance of the perturbed deltas (rows = perturbed runs)
    if len(pert):
        cols = [c for c in ids if np.isfinite(pert[c].to_numpy(dtype=float)).all()]
        M = pert[cols].to_numpy(dtype=float)
        cov = pd.DataFrame(np.cov(M, rowvar=False, ddof=1) if len(M) > 1 else np.full((len(cols), len(cols)), np.nan),
                           index=cols, columns=cols)
    else:
        cov = pd.DataFrame()
    # shed assert
    shed = [(_val(r, "R1"), r["key"]) for r in recs]
    shed_ok = bool(recs) and all(np.isfinite(v) and v == 0.0 for v, _ in shed)
    # runtime table
    rt = []
    for r in recs:
        w = r["wall_s"]
        rt.append({"key": r["key"], "batch": r["batch"], "index": r["index"], "design_no": r["design_no"],
                   "copy_type": r["copy_type"], "site": r["site"], "unit_type": r["unit_type"],
                   "pem_mw": r["pem_mw_design"], "wall_s": w, "wall_h": (w / 3600.0 if np.isfinite(w) else np.nan),
                   "core_h": (w / 3600.0 * SLOTS if np.isfinite(w) else np.nan),
                   "n_ruc": r.get("n_ruc"), "n_ruc_optimal": r.get("n_ruc_optimal"),
                   "n_ruc_time_limit": r.get("n_ruc_time_limit"), "max_gap_pct": r.get("max_gap_pct"),
                   "G_run_usd": r.get("G_run_usd"), "runtimes_present": r.get("runtimes_present")})
    rt = pd.DataFrame(rt)
    ch = rt["core_h"].dropna() if len(rt) else pd.Series(dtype=float)
    runtime = {"slots": SLOTS, "n_with_wallclock": int(len(ch)),
               "core_h_median": (float(ch.median()) if len(ch) else np.nan),
               "core_h_min": (float(ch.min()) if len(ch) else np.nan),
               "core_h_max": (float(ch.max()) if len(ch) else np.nan),
               "core_h_total": (float(ch.sum()) if len(ch) else np.nan),
               "replaces": f"ERCOT_BO_PLAN.md section 8 '{PLAN_UNKNOWN}'"}
    # identity check
    idl = [r["identity"] for r in recs if r.get("identity")]
    ident = {"n_runs": len(recs), "n_with_identity_line": len(idl),
             "ruc_mipgap_values": sorted({i.get("ruc_mipgap") for i in idl if "ruc_mipgap" in i}),
             "ruc_time_limit_values": sorted({i.get("ruc_time_limit") for i in idl if "ruc_time_limit" in i})}
    return {"per_candidate": per_cand, "exact_pairs": ex, "perturbed": pert, "cov": cov,
            "ruler_zero": ruler_zero, "ruler_unavailable": ruler_unavail,
            "all_exact_zero": all_exact_zero, "n_exact_pairs": n_pairs, "n_md5_equal": md5_equal,
            "shed_ok": shed_ok, "shed_values": shed, "runtime_table": rt, "runtime": runtime,
            "identity": ident, "missing": missing}


# --------------------------------------------------------------------------
# free data (prompt 52 section 2) — read if present, quoted as history only
# --------------------------------------------------------------------------
def free_data(ercot=ERCOT):
    out = {}
    p = os.path.join(ercot, "analysis", "pool", "pool_replicate_zero_check_v2.csv")
    if os.path.isfile(p):
        z = pd.read_csv(p)
        out["v2_replicate_groups"] = {"groups": sorted(z["distinct_design_id"].unique().tolist()),
                                      "max_abs_within_delta": float(z["max_abs_within_delta"].max())}
    p = os.path.join(ercot, "analysis", "screening_noise_ruler.json")
    if os.path.isfile(p):
        with open(p) as f:
            out["v1_screening_ruler_history"] = json.load(f)
    p = os.path.join(ercot, "analysis", "selection", "noise_ruler_v2.json")
    if os.path.isfile(p):
        with open(p) as f:
            j = json.load(f)
        out["v1_selection_ruler_history"] = {k: j[k] for k in ("schema", "provenance", "replicate_definition") if k in j}
    return out


# --------------------------------------------------------------------------
# outputs
# --------------------------------------------------------------------------
def _f(v, nd=4):
    if v is None or (isinstance(v, float) and not np.isfinite(v)):
        return "n/a" if not (isinstance(v, float) and v == float("inf")) else "inf"
    if isinstance(v, (int, np.integer)):
        return str(int(v))
    a = abs(v)
    if a == 0:
        return "0"
    if a >= 1e5 or a < 1e-3:
        return f"{v:.{nd - 1}e}"
    return f"{v:.{nd}g}"


def to_frame(S, ids):
    rows = []
    for c in ids:
        p = S["per_candidate"][c]
        t = p["trigger"]
        rows.append({"id": c, "family": p["family"], "name": p["name"], "unit": p["unit"], "dir": p["dir"],
                     "gradable": p["gradable"], "n_exact_pairs": p["n_exact_pairs"],
                     "exact_abs_delta_max": p["exact_abs_delta_max"], "exact_zero": p["exact_zero"],
                     "exact_pooled_sd": p["exact_pooled_sd"], "exact_df": p["exact_df"],
                     "n_perturbed": p["n_perturbed"], "ruler": p["ruler"], "ruler_min": p["ruler_min"],
                     "ruler_max": p["ruler_max"], "ruler_status": p["ruler_status"],
                     "perturbed_abs_delta": "|".join(f"{x:.10g}" for x in p["perturbed_abs_delta"]),
                     "pooled_sd": p["pooled_sd"], "pooled_df_satterthwaite": p["pooled_df_satterthwaite"],
                     "pooled_sd_ci95_lo": p["pooled_sd_ci95"][0], "pooled_sd_ci95_hi": p["pooled_sd_ci95"][1],
                     "level_sd_min": (min(lv["sd"] for lv in p["levels"]) if p["levels"] else np.nan),
                     "level_sd_max": (max(lv["sd"] for lv in p["levels"]) if p["levels"] else np.nan),
                     "level_df": (p["levels"][0]["df"] if p["levels"] else 0),
                     "trigger_ratio": t["ratio"], "trigger_p": t["p"], "trigger_fires": t["fires"],
                     "trigger_verdict": t["verdict"]})
    return pd.DataFrame(rows)


def fmt_md(S, ids, gradable, recs, gap_used, fd, out_dir):
    pc = S["per_candidate"]
    g = next(iter(gap_used.values()), None)
    gid = (f"ruc_mipgap {g['ruc_mipgap']}, ruc_time_limit {g['ruc_time_limit']} s"
           if g else "ruc_mipgap 0.001, ruc_time_limit 1200 s (GAP_DECISION_used.json not yet in extracts)")
    idn = S["identity"]
    L = ["# ERCOT_NOISE — noise_v3 reading (prompt 52 v2.1)", "",
         f"Extracts: `extracts/{WAVE}/A`, `extracts/{WAVE}/B`. Pure pandas/numpy; every candidate value "
         "comes from `pool_objectives.pool_row`. This file decides nothing.", "",
         "## 0. Identity (v3)", "",
         f"1. Every noise_v3 run is a v3 run: {gid}, read at run time from `waves/GAP_DECISION.json` "
         f"(copied to `extracts/{WAVE}/<batch>/GAP_DECISION_used.json`); task logs: "
         f"{idn['n_with_identity_line']} of {idn['n_runs']} runs carry the identity line, values "
         f"ruc_mipgap {idn['ruc_mipgap_values']} / ruc_time_limit {idn['ruc_time_limit_values']}.",
         "2. Gate G1 is MET by `analysis/gap_smoke/GAP_SMOKE.md`: control arm byte-identical to smoke_v2, "
         "tolerance verified per RUC day, 0 time-limit hits.",
         "3. The identity is recorded in `ERCOT_BO_PLAN.md` AMENDMENT 2026-11-06b (E-D6, Kay). No v2-identity "
         "value enters this file; the v2 table chose the designs only (`waves/noise_v3/PICK_RULE.md`).", ""]
    if S["missing"]:
        L += [f"**WARNING: {len(S['missing'])} extracts missing: {', '.join(S['missing'])}. The reading below is partial.**", ""]
    # 1 runs
    L += ["## 1. Runs", "",
          "| key | batch | design | copy | site | type | PEM MW | overall md5 | RUC optimal / TL | max gap % | wall h | core-h |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in recs:
        w = r["wall_s"]
        L.append(f"| {r['key']} | {r['batch']} | D{r['design_no']} | {r['copy_type']} | {r['site']} | {r['unit_type']} | "
                 f"{r['pem_mw_design']:.4f} | `{r['overall_md5'][:8]}` | {r.get('n_ruc_optimal')} / {r.get('n_ruc_time_limit')} | "
                 f"{_f(r.get('max_gap_pct'))} | {_f(w / 3600.0 if np.isfinite(w) else np.nan, 3)} | "
                 f"{_f(w / 3600.0 * SLOTS if np.isfinite(w) else np.nan, 3)} |")
    L += [""]
    # 2 exact pairs
    L += ["## 2. Exact cross-batch pairs (the noise population tau)", "",
          f"{S['n_exact_pairs']} pairs (A exact vs B exact); overall.csv byte-identical on {S['n_md5_equal']} of {S['n_exact_pairs']}.",
          ""]
    if S["all_exact_zero"] and S["n_exact_pairs"] > 0:
        L += ["**Every gradable candidate shows an exact-pair |Δ| of 0 — reported as exact zeros.** "
              "Finding, pre-registered (prompt 52 section 1): " + EXACT_ZERO_FINDING,
              "The GP noise floor (ERCOT_BO_PLAN.md section 3): exact sd = 0, so the floor is 0 and the GP noise is "
              "INFERRED-only with the 1e-9 bound (the D-1025 pattern).", ""]
    elif S["n_exact_pairs"] > 0:
        nz = [c for c in gradable if not pc[c]["exact_zero"] and pc[c]["n_exact_pairs"] > 0]
        L += [f"**Exact pairs differ on {len(nz)} gradable candidates: {', '.join(nz)}.** The instrument is NOT "
              "byte-deterministic under v3 on these runs. Read the per-objective exact sd below; the GP noise floor "
              "is the exact sd where it is > 0 (ERCOT_BO_PLAN.md section 3).", ""]
    L += ["| id | name | unit | pairs | max exact pair |Δ| | exact zero | exact pooled sd (df) |", "|---|---|---|---|---|---|---|"]
    for c in ids:
        p = pc[c]
        L.append(f"| {c} | {p['name']} | {p['unit']} | {p['n_exact_pairs']} | {_f(p['exact_abs_delta_max'])} | "
                 f"{'yes' if p['exact_zero'] else 'no'} | {_f(p['exact_pooled_sd'])} ({_f(p['exact_df'], 3)}) |")
    L += [""]
    # 3 perturbed
    pert = S["perturbed"]
    L += ["## 3. Perturbed copies (local input sensitivity; the ruler)", "",
          f"{len(pert)} perturbed runs (delta = 0.001 relative on pem_mw; sign and inward rule in "
          "`waves/noise_v3/PICK_RULE.md`), each read against the exact copy of the same design in the same batch. "
          "`ruler_j` = median |Δ_j| (prompt 57 section 3 A4). This population is never pooled with section 2.", ""]
    if len(pert):
        L += ["| perturbed key | design | ref key | PEM MW | ref PEM MW | sign | delta_rel |", "|---|---|---|---|---|---|---|"]
        for _, r in pert.iterrows():
            L.append(f"| {r['key']} | D{r['design_no']} | {r['ref_key']} | {r['pem_mw']:.4f} | {r['pem_mw_ref']:.4f} | "
                     f"{int(r['perturb_sign']):+d} | {r['delta_rel']:.3f} |")
        L += [""]
    L += ["| id | name | unit | n | ruler_j (median |Δ|) | min | max | status | |Δ| values |", "|---|---|---|---|---|---|---|---|---|"]
    for c in ids:
        p = pc[c]
        L.append(f"| {c} | {p['name']} | {p['unit']} | {p['n_perturbed']} | {_f(p['ruler'])} | {_f(p['ruler_min'])} | "
                 f"{_f(p['ruler_max'])} | {p['ruler_status']} | {', '.join(_f(x) for x in p['perturbed_abs_delta'])} |")
    L += ["", f"`RULER=0` candidates (gradable): {', '.join(S['ruler_zero']) if S['ruler_zero'] else 'none'} — "
          "readable iff |Δ| >= 1 natural unit (prompt 57 section 3 A4); continuous candidates report the raw Δ with the tag.",
          f"`RULER UNAVAILABLE` (gradable): {', '.join(S['ruler_unavailable']) if S['ruler_unavailable'] else 'none'}.",
          "Readable means, in exactly these words: \"exceeds twice the median response to a 0.1 % input perturbation at the "
          "prompt-52 designs.\" An effect that fails reads \"not readable above the perturbation response\", never \"zero\".", ""]
    # 4 sd + trigger
    L += ["## 4. Per-level and pooled sd of the perturbed population; variance-ratio trigger", "",
          "Level = design. Per-level sd = sd of {exact, perturbed copies} of that design (ddof 1, df = number of perturbed "
          "copies). Pooled sd = sqrt(Σ df_i s_i² / Σ df_i) with Satterthwaite df = (Σ df_i s_i²)² / Σ (df_i s_i²)² / df_i. "
          "CIs are chi-square 95 %. Trigger per objective: F test of max s² / min s² at alpha = 0.05 AND point ratio > 3. "
          "A non-firing trigger reads \"not detectable at this df\", never \"homoscedastic confirmed\" (prompt 52 section 3 "
          "precision budget).", "",
          f"**Family-wise disclosure:** {len(gradable)} gradable candidates are tested at alpha = 0.05 each with no "
          "family-wise correction; a false trigger only replaces a scalar sd by per-level sds (conservative), so none is applied.", "",
          "| id | per-level sd (df) [95 % CI] | pooled sd | Satterthwaite df | pooled 95 % CI | ratio | p | verdict |",
          "|---|---|---|---|---|---|---|---|"]
    for c in ids:
        p = pc[c]
        t = p["trigger"]
        lv = "; ".join(f"D{x['design_no']} {_f(x['sd'])} ({x['df']}) [{_f(x['sd_ci95'][0])}, {_f(x['sd_ci95'][1])}]" for x in p["levels"])
        L.append(f"| {c} | {lv or 'n/a'} | {_f(p['pooled_sd'])} | {_f(p['pooled_df_satterthwaite'], 3)} | "
                 f"[{_f(p['pooled_sd_ci95'][0])}, {_f(p['pooled_sd_ci95'][1])}] | {_f(t['ratio'], 3)} | {_f(t['p'], 3)} | {t['verdict']} |")
    L += [""]
    # 5 covariance
    cov = S["cov"]
    L += ["## 5. Cross-objective covariance of the perturbed deltas", "",
          f"`ercot_noise_cov.csv` ({cov.shape[0]} x {cov.shape[1]}; rows = perturbed runs, ddof 1; candidates with a finite "
          "delta on every perturbed run). Prompt 55 samples noise vectors JOINTLY from it, or marginal with a joint-vs-marginal "
          "sensitivity row. Candidates with an all-zero column have zero covariance with everything.", ""]
    if len(cov):
        diag = [(c, float(cov.loc[c, c])) for c in cov.columns]
        L += ["| id | variance of Δ | sd of Δ |", "|---|---|---|"]
        L += [f"| {c} | {_f(v)} | {_f(math.sqrt(v) if v >= 0 else np.nan)} |" for c, v in diag]
        L += [""]
    # 6 shed
    L += ["## 6. Load shed assert (protects E-D1)", "",
          (f"shed ≡ 0 on all {len(recs)} runs: **PASS**." if S["shed_ok"] else
           "**FAIL: load shed is not 0 on every run: " + ", ".join(f"{k} = {_f(v)}" for v, k in S["shed_values"] if not (np.isfinite(v) and v == 0.0)) + ". STOP. Re-read E-D1 before any use.**"), ""]
    # 7 runtime
    rt = S["runtime"]
    L += ["## 7. Runtime (wall-clock per run -> core-h at 4 slots)", "",
          f"{rt['n_with_wallclock']} of {len(recs)} runs carry a wall-clock stamp. core-h median {_f(rt['core_h_median'], 3)}, "
          f"min {_f(rt['core_h_min'], 3)}, max {_f(rt['core_h_max'], 3)}, total {_f(rt['core_h_total'], 4)}. "
          f"This replaces the line \"{PLAN_UNKNOWN}\" of ERCOT_BO_PLAN.md section 8 (budget actuals).", ""]
    rtt = S["runtime_table"]
    if len(rtt):
        L += ["| key | design | copy | wall h | core-h | RUC optimal | TL hits | Prescient runtimes.csv |", "|---|---|---|---|---|---|---|---|"]
        for _, r in rtt.iterrows():
            L.append(f"| {r['key']} | D{r['design_no']} | {r['copy_type']} | {_f(r['wall_h'], 3)} | {_f(r['core_h'], 3)} | "
                     f"{r['n_ruc_optimal']} | {r['n_ruc_time_limit']} | {'yes' if r['runtimes_present'] else 'no'} |")
        L += [""]
    # 8 free data
    L += ["## 8. Free data first (prompt 52 section 2; history only)", ""]
    if "v2_replicate_groups" in fd:
        z = fd["v2_replicate_groups"]
        L.append(f"- v2 byte-identical groups {', '.join(z['groups'])}: max within-group |Δ| over every candidate = "
                 f"{_f(z['max_abs_within_delta'])} (`analysis/pool/pool_replicate_zero_check_v2.csv`). v2 identity; not pooled with v3.")
    if "v1_screening_ruler_history" in fd:
        h = fd["v1_screening_ruler_history"]
        L.append(f"- v1 screening ruler (SUPERSEDED, `analysis/INVALID_v1_costs.md`): var_cost {_f(h.get('var_cost'))} $, "
                 f"total_cost {_f(h.get('total_cost'))} $ (bimodal TL=120 race). Quoted as history only.")
    if "v1_selection_ruler_history" in fd:
        L.append(f"- v1 selection ruler `analysis/selection/noise_ruler_v2.json` (v1-extract based): "
                 f"{fd['v1_selection_ruler_history'].get('replicate_definition', '')}. History only.")
    L += ["- The prompt-33 TL=360 base x3 is an old-identity anchor and is not read here.", ""]
    # 9 deviations
    L += ["## 9. Deviations and limits", "",
          "- Batch split: per design exact A + exact B + one perturbed copy in A (layout 12), unless `waves/noise_v3/README.md` "
          "section 5 says layout 16. The ruler population size is the `n` column of section 3.",
          "- With df = 1 per level the F test rejects only at observed ratios > 161 (alpha 0.05, one-sided); the trigger is an "
          "order-of-magnitude detector. Pooled sd CIs are wide at these df; read the CI, not the point.",
          "- E8, E9, N5 use the CRC-computed `pool_full_metrics.json` (the gz tables are not in git).",
          f"- Outputs: `{os.path.relpath(out_dir, ERCOT)}/ercot_noise.csv`, `ercot_noise.json`, `ercot_noise_cov.csv`.", ""]
    return "\n".join(L)


def write_outputs(S, ids, gradable, recs, gap_used, fd, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    df = to_frame(S, ids)
    df.to_csv(os.path.join(out_dir, "ercot_noise.csv"), index=False)
    S["cov"].to_csv(os.path.join(out_dir, "ercot_noise_cov.csv"))
    runs = []
    for r in recs:
        runs.append({k: r.get(k) for k in ("key", "batch", "index", "design_no", "design_id", "copy_type", "site",
                                          "unit_type", "pem_mw_design", "omega", "origin_key", "perturb_sign",
                                          "delta_rel", "overall_md5", "full_extract", "n_ruc", "n_ruc_optimal",
                                          "n_ruc_time_limit", "max_gap_pct", "G_run_usd", "wall_s", "identity",
                                          "pool_full_metrics_present", "runtimes_present", "gz_verified")})
    js = {"prompt": "52 v2.1", "wave": WAVE, "identity": {"gap_decision_used": gap_used, "task_logs": S["identity"],
                                                            "G1": "analysis/gap_smoke/GAP_SMOKE.md",
                                                            "amendment": "ERCOT_BO_PLAN.md AMENDMENT 2026-11-06b"},
          "populations": {"exact": "A exact vs B exact per design (tau); never pooled with perturbed",
                          "perturbed": "perturbed copy vs the exact copy of the same design in the same batch; delta 0.001 relative on pem_mw"},
          "noise_floor": {"definition": "exact sd if > 0, else inferred-only with the 1e-9 bound (D-1025 pattern)",
                          "all_exact_zero": S["all_exact_zero"],
                          "floor": {c: (0.0 if S["per_candidate"][c]["exact_zero"] else S["per_candidate"][c]["exact_pooled_sd"]) for c in gradable}},
          "exact_zero_finding": (EXACT_ZERO_FINDING if S["all_exact_zero"] else None),
          "trigger_rule": {"alpha": ALPHA, "point_ratio": POINT_RATIO, "family_wise": "no correction; conservative consequence"},
          "ruler_zero": S["ruler_zero"], "ruler_unavailable": S["ruler_unavailable"],
          "n_exact_pairs": S["n_exact_pairs"], "n_md5_equal": S["n_md5_equal"], "shed_ok": S["shed_ok"],
          "runtime": S["runtime"], "runtime_table": S["runtime_table"].to_dict(orient="records"),
          "per_candidate": S["per_candidate"],
          "exact_pairs": {str(k): v for k, v in S["exact_pairs"].items()},
          "perturbed_deltas": S["perturbed"].to_dict(orient="records"),
          "covariance": {"ids": list(S["cov"].columns), "matrix": S["cov"].to_numpy().tolist()},
          "free_data": fd, "missing_extracts": S["missing"], "runs": runs,
          "generated_utc": pd.Timestamp.now(tz="UTC").strftime("%Y-%m-%dT%H:%M:%SZ"), "git_head": po.git_head()}
    with open(os.path.join(out_dir, "ercot_noise.json"), "w") as f:
        json.dump(po._json_safe(js), f, indent=1, default=str)
        f.write("\n")
    md = fmt_md(S, ids, gradable, recs, gap_used, fd, out_dir)
    with open(os.path.join(out_dir, "ERCOT_NOISE.md"), "w") as f:
        f.write(md + "\n")
    return df, md


def read_noise(extr=po.EXTR, waves=po.WAVES, data_dir=po.DATA, out_dir=HERE, defs=None, ercot=ERCOT):
    defs = defs or po.load_defs()
    gradable, ids = candidate_ids(defs)
    recs, missing, gap_used = load_rows(extr, waves, data_dir, defs)
    if not recs:
        raise SystemExit(f"no noise_v3 extracts under {extr}/{WAVE} (missing: {missing})")
    S = summarize(recs, ids, gradable, defs, missing)
    fd = free_data(ercot)
    df, md = write_outputs(S, ids, gradable, recs, gap_used, fd, out_dir)
    return S, df, md


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--extr", default=po.EXTR)
    ap.add_argument("--waves", default=po.WAVES)
    ap.add_argument("--data_dir", default=po.DATA)
    ap.add_argument("--out-dir", default=HERE)
    ap.add_argument("--no-strict", action="store_true", help="do not exit 1 on a failed shed assert")
    args = ap.parse_args(argv)
    S, df, md = read_noise(args.extr, args.waves, args.data_dir, args.out_dir)
    print(df[["id", "n_exact_pairs", "exact_zero", "n_perturbed", "ruler", "ruler_status", "pooled_sd",
              "trigger_fires"]].to_string(index=False))
    print(f"exact pairs {S['n_exact_pairs']} (md5 equal {S['n_md5_equal']}); all exact zero: {S['all_exact_zero']}; "
          f"RULER=0: {S['ruler_zero']}; shed ok: {S['shed_ok']}; core-h median {S['runtime']['core_h_median']}")
    if S["missing"]:
        print(f"WARNING missing extracts: {S['missing']}")
    if not S["shed_ok"] and not args.no_strict:
        print("SHED ASSERT FAILED (outputs written; exit 1)")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
