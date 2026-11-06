#!/usr/bin/env python3
"""Prompt 58 T1 — read the RUC-gap smoke (waves/smoke_gap, E-D6). Pure pandas.

Two modes:

  --joblog <array .o file> --tolerance-out <csv>
      Parse ONE task's job log into the per-RUC-day table
      ruc_tolerance.csv (ruc_date, tolerance, n_mip_solves, n_time_limit).
      The tolerance is the value Gurobi prints in
      "Optimal solution found (tolerance 1.00e-03)"; segment boundaries are
      the same as extract_ercot.parse_ruc_quality (OPEN/CLOSE regexes).
      A lazy-PTDF RUC day can hold several MIP solves; the LAST tolerance
      line of the segment is kept and the count is reported.

  --extracts extracts/smoke_gap --ref extracts/smoke_v2 --out analysis/gap_smoke
      Read task_1..task_3 and write GAP_SMOKE.md + gap_smoke.csv (per task)
      + gap_smoke_days.csv (per task x day). Prints the pre-registered
      adoption rule's verdict (prompt 58 section 2). It NEVER writes
      waves/GAP_DECISION.json — the decision is Kay's (E-D6).

Pre-registered rule (printed, not decided here): adopt the TIGHTEST arm for
which (i) every RUC day is OPTIMAL with the tolerance line == the requested
gap, (ii) max per-day solve time <= 600 s, (iii) 365 x max solve time
<= 61 h; otherwise keep 0.01 / 120 and disclose.
"""
import argparse
import hashlib
import json
import os
import re
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ERCOT = os.path.abspath(os.path.join(HERE, "..", ".."))
if ERCOT not in sys.path:
    sys.path.insert(0, ERCOT)
import extract_ercot as ex  # noqa: E402  (segment regexes; pandas only)

# task -> (requested gap, time limit s); mirrors tools/make_smoke_gap.py
TASKS = {1: (0.01, 1200.0), 2: (0.001, 1200.0), 3: (0.0001, 1200.0)}
ROLE = {1: "control (identical to smoke_v2)", 2: "candidate", 3: "stretch"}
RULE = {"max_solve_s": 600.0, "max_year_h": 61.0, "days_per_year": 365}
REF_MEDIAN_SINGLE_SITE_USD = 11.3e6     # POOL_V2.md section 6.1 / prompt 58 section 0
FROZEN = {"ruc_mipgap": 0.01, "ruc_time_limit": 120.0}

TOL_RE = re.compile(r"Optimal solution found \(tolerance ([\d.eE+-]+)\)")
TL_RE = ex.TL_RE


# --------------------------------------------------------------------------
# job-log tolerance parse (collector mode)
# --------------------------------------------------------------------------
def parse_tolerance(joblog):
    rows = []
    cur = None
    pending_date = "start_date"
    with open(joblog, errors="replace") as f:
        for line in f:
            m = ex.DATE_RE.search(line)
            if m:
                pending_date = m.group(1)
                continue
            if ex.OPEN_RE.search(line):
                cur = {"ruc_date": pending_date, "tolerance": np.nan,
                       "n_mip_solves": 0, "n_time_limit": 0}
                continue
            if cur is None:
                continue
            m = TOL_RE.search(line)
            if m:
                cur["tolerance"] = float(m.group(1))
                cur["n_mip_solves"] += 1
            if TL_RE.search(line):
                cur["n_time_limit"] += 1
                cur["n_mip_solves"] += 1
            if ex.CLOSE_RE.search(line):
                rows.append(cur)
                cur = None
    return pd.DataFrame(rows, columns=["ruc_date", "tolerance", "n_mip_solves", "n_time_limit"])


# --------------------------------------------------------------------------
# reading mode
# --------------------------------------------------------------------------
def md5(path):
    with open(path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()


def wallclock_s(path):
    """Seconds between the SMOKE_GAP_START/END epoch stamps, NaN if absent."""
    if not os.path.isfile(path):
        return np.nan
    txt = open(path).read()
    s = re.search(r"SMOKE_GAP_START .*epoch=(\d+)", txt)
    e = re.search(r"SMOKE_GAP_END .*epoch=(\d+)", txt)
    return float(int(e.group(1)) - int(s.group(1))) if (s and e) else np.nan


def read_task(task_dir, task, requested_gap):
    rq = pd.read_csv(os.path.join(task_dir, "ruc_quality.csv"))
    rq = rq.copy()
    rq["task"] = task
    rq["requested_gap"] = requested_gap
    rq["requested_time_limit_s"] = TASKS[task][1]
    tol_path = os.path.join(task_dir, "ruc_tolerance.csv")
    if os.path.isfile(tol_path):
        tol = pd.read_csv(tol_path)
        tol = tol.copy()
        tol["tolerance"] = tol["tolerance"].astype(float)
        if len(tol) == len(rq):
            rq["tolerance"] = tol["tolerance"].to_numpy()
            rq["n_mip_solves"] = tol["n_mip_solves"].to_numpy()
            rq["n_time_limit"] = tol["n_time_limit"].to_numpy()
        else:
            rq["tolerance"] = np.nan
            rq["n_mip_solves"] = np.nan
            rq["n_time_limit"] = np.nan
            print(f"WARNING task {task}: ruc_tolerance.csv has {len(tol)} rows, "
                  f"ruc_quality.csv {len(rq)} — tolerance UNVERIFIED")
    else:
        rq["tolerance"] = np.nan
        rq["n_mip_solves"] = np.nan
        rq["n_time_limit"] = np.nan
    rq["tolerance_ok"] = np.isclose(rq["tolerance"].astype(float), requested_gap,
                                    rtol=1e-6, atol=0.0) & rq["tolerance"].notna()
    rq["status_ok"] = rq["status"].astype(str) == "OPTIMAL"
    rq["gap_le_requested"] = rq["final_gap_pct"].astype(float) <= 100.0 * requested_gap + 1e-9
    return rq


def task_summary(days, task_dir, ref_dir, task):
    o = pd.read_csv(os.path.join(task_dir, "overall.csv")).iloc[0]
    g = ex.pd.read_csv(os.path.join(task_dir, "gen_summary.csv"))
    ch = pd.read_csv(os.path.join(task_dir, "committed_hourly.csv"))
    is_pem = g["is_pem"].astype("boolean").fillna(False).astype(bool) if "is_pem" in g else pd.Series(False, index=g.index)
    vre = (~is_pem) & g["unit_type"].astype(str).isin(["WIND", "PV"])
    gap, tl = TASKS[task]
    st = days["solve_time_s"].astype(float)
    n = int(len(days))
    all_ok = bool(days["status_ok"].all() and days["tolerance_ok"].all()) if n else False
    year_med_h = float(RULE["days_per_year"] * st.median() / 3600.0) if n else np.nan
    year_max_h = float(RULE["days_per_year"] * st.max() / 3600.0) if n else np.nan
    row = {
        "task": task, "role": ROLE[task], "ruc_mipgap": gap, "ruc_time_limit_s": tl,
        "n_days": n,
        "n_optimal": int(days["status_ok"].sum()),
        "n_tolerance_ok": int(days["tolerance_ok"].sum()),
        "n_tolerance_read": int(days["tolerance"].notna().sum()),
        "n_time_limit_days": int((days["status"].astype(str) == "TIME_LIMIT").sum()),
        "solve_time_median_s": float(st.median()) if n else np.nan,
        "solve_time_max_s": float(st.max()) if n else np.nan,
        "solve_time_sum_s": float(st.sum()) if n else np.nan,
        "final_gap_pct_max": float(days["final_gap_pct"].astype(float).max()) if n else np.nan,
        "ruc_cost_sum_usd": float(days["ruc_cost"].astype(float).sum()) if n else np.nan,
        "G_run_usd": float((days["final_gap_pct"].astype(float) / 100.0
                            * days["ruc_cost"].astype(float)).sum()) if n else np.nan,
        "wallclock_s": wallclock_s(os.path.join(task_dir, "wallclock.txt")),
        "projected_year_ruc_h_median": year_med_h,
        "projected_year_ruc_h_max": year_max_h,
        "total_cost_usd": float(o["Total costs"]),
        "fixed_cost_usd": float(o["Total fixed costs"]),
        "variable_cost_usd": float(o["Total generation costs"]),
        "true_curt_mwh": float(g.loc[vre, "curtailment_mwh"].astype(float).sum()),
        "committed_mwh": float(ch["committed_mw"].astype(float).sum()),
        "onoffs": float(o["Total on/offs"]),
        "overall_md5": md5(os.path.join(task_dir, "overall.csv")),
        "rule_i_all_optimal_at_tolerance": all_ok,
        "rule_ii_max_solve_le_600s": bool(n and st.max() <= RULE["max_solve_s"]),
        "rule_iii_year_at_max_le_61h": bool(n and year_max_h <= RULE["max_year_h"]),
    }
    row["rule_pass"] = bool(row["rule_i_all_optimal_at_tolerance"]
                            and row["rule_ii_max_solve_le_600s"]
                            and row["rule_iii_year_at_max_le_61h"])
    if task == 1 and ref_dir:
        ref = md5(os.path.join(ref_dir, "overall.csv"))
        row["ref_overall_md5"] = ref
        row["byte_identical_to_ref"] = bool(ref == row["overall_md5"])
        # the manifest md5s of every table, if the reference has a manifest
        same, diff = [], []
        mp = os.path.join(ref_dir, "extract_manifest.json")
        if os.path.isfile(mp):
            ref_md5 = json.load(open(mp)).get("md5", {})
            for name, h in ref_md5.items():
                p = os.path.join(task_dir, name)
                if os.path.isfile(p):
                    (same if md5(p) == h else diff).append(name)
        row["ref_tables_identical"] = ";".join(sorted(same))
        row["ref_tables_different"] = ";".join(sorted(diff))
    return row


def read_smoke(extracts, ref_dir=None, tasks=TASKS):
    day_frames, rows = [], []
    for t, (gap, _) in tasks.items():
        td = os.path.join(extracts, f"task_{t}")
        if not os.path.isdir(td):
            print(f"WARNING: {td} missing — task {t} skipped")
            continue
        days = read_task(td, t, gap)
        day_frames.append(days)
        rows.append(task_summary(days, td, ref_dir, t))
    days = pd.concat(day_frames, ignore_index=True) if day_frames else pd.DataFrame()
    summ = pd.DataFrame(rows)
    if len(summ) and 1 in set(summ["task"]):
        b = summ[summ["task"] == 1].iloc[0]
        for c in ("total_cost_usd", "fixed_cost_usd", "variable_cost_usd",
                  "true_curt_mwh", "committed_mwh", "onoffs", "ruc_cost_sum_usd",
                  "solve_time_median_s", "solve_time_max_s"):
            summ[f"delta_{c}_vs_task1"] = summ[c].astype(float) - float(b[c])
        summ["delta_total_cost_scaled_year_usd"] = (
            summ["delta_total_cost_usd_vs_task1"] * (RULE["days_per_year"] / float(b["n_days"]))
            if float(b["n_days"]) > 0 else np.nan)
        summ["delta_total_cost_scaled_year_over_ref_median"] = (
            summ["delta_total_cost_scaled_year_usd"].abs() / REF_MEDIAN_SINGLE_SITE_USD)
    return days, summ


def verdict(summ):
    """Tightest passing arm, or the frozen identity with the reasons."""
    if not len(summ):
        return {"adopt": FROZEN, "reason": "no task read", "tightest_pass_task": None}
    passing = summ[summ["rule_pass"]].sort_values("ruc_mipgap")
    if len(passing):
        r = passing.iloc[0]
        return {"adopt": {"ruc_mipgap": float(r["ruc_mipgap"]),
                          "ruc_time_limit": float(r["ruc_time_limit_s"])},
                "tightest_pass_task": int(r["task"]),
                "reason": "tightest arm with (i) all days OPTIMAL at the requested tolerance, "
                          "(ii) max solve <= 600 s, (iii) 365 x max <= 61 h"}
    fails = []
    for _, r in summ.iterrows():
        why = [k for k in ("rule_i_all_optimal_at_tolerance", "rule_ii_max_solve_le_600s",
                           "rule_iii_year_at_max_le_61h") if not bool(r[k])]
        fails.append(f"task {int(r['task'])} (gap {r['ruc_mipgap']}): fails {', '.join(why)}")
    return {"adopt": FROZEN, "tightest_pass_task": None,
            "reason": "no arm passes the rule — keep 0.01 / 120 and disclose: " + "; ".join(fails)}


def fmt_md(days, summ, v, extracts, ref_dir):
    L = ["# GAP_SMOKE — RUC-gap smoke reading (prompt 58 T1, E-D6)", "",
         f"Extracts: `{os.path.relpath(extracts, ERCOT)}`; byte-identity reference: "
         f"`{os.path.relpath(ref_dir, ERCOT) if ref_dir else 'none'}`. "
         "Pure pandas; this file decides nothing. Kay writes `waves/GAP_DECISION.json`.", ""]
    L += ["## 1. Per task", "",
          "| task | role | gap | TL s | days | OPTIMAL | tol OK | tol read | max solve s | median solve s | "
          "max gap % | year RUC h (365 x median) | year RUC h (365 x max) | wall s | rule (i) | (ii) | (iii) | PASS |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for _, r in summ.iterrows():
        L.append(f"| {int(r['task'])} | {r['role']} | {r['ruc_mipgap']} | {r['ruc_time_limit_s']:.0f} | "
                 f"{int(r['n_days'])} | {int(r['n_optimal'])} | {int(r['n_tolerance_ok'])} | "
                 f"{int(r['n_tolerance_read'])} | {r['solve_time_max_s']:.1f} | "
                 f"{r['solve_time_median_s']:.1f} | {r['final_gap_pct_max']:.4f} | "
                 f"{r['projected_year_ruc_h_median']:.2f} | {r['projected_year_ruc_h_max']:.2f} | "
                 f"{r['wallclock_s']:.0f} | {'Y' if r['rule_i_all_optimal_at_tolerance'] else 'N'} | "
                 f"{'Y' if r['rule_ii_max_solve_le_600s'] else 'N'} | "
                 f"{'Y' if r['rule_iii_year_at_max_le_61h'] else 'N'} | "
                 f"{'PASS' if r['rule_pass'] else 'fail'} |")
    L += ["", "A task whose `tol read` < `days` has an UNVERIFIED tolerance (no job log or "
          "no Gurobi tolerance line) and cannot pass rule (i). A tolerance line that reads "
          "1.00e-02 on task 2 or 3 is a FAILED smoke, not a result.", ""]
    L += ["## 2. 3-day totals and delta vs task 1", "",
          "| task | total cost $ | fixed $ | variable $ | true curt MWh | committed MWh | on/offs | "
          "G_run $ | d total cost vs 1 | d fixed | d variable | d true curt | d committed | d on/offs |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for _, r in summ.iterrows():
        L.append(f"| {int(r['task'])} | {r['total_cost_usd']:,.0f} | {r['fixed_cost_usd']:,.0f} | "
                 f"{r['variable_cost_usd']:,.0f} | {r['true_curt_mwh']:,.1f} | {r['committed_mwh']:,.0f} | "
                 f"{r['onoffs']:.0f} | {r['G_run_usd']:,.0f} | "
                 f"{r.get('delta_total_cost_usd_vs_task1', np.nan):+,.0f} | "
                 f"{r.get('delta_fixed_cost_usd_vs_task1', np.nan):+,.0f} | "
                 f"{r.get('delta_variable_cost_usd_vs_task1', np.nan):+,.0f} | "
                 f"{r.get('delta_true_curt_mwh_vs_task1', np.nan):+,.1f} | "
                 f"{r.get('delta_committed_mwh_vs_task1', np.nan):+,.0f} | "
                 f"{r.get('delta_onoffs_vs_task1', np.nan):+.0f} |")
    L += ["", "## 3. Per task x day", "",
          "| task | gap | day | status | tolerance read | tol OK | final gap % | solve s | MIP solves | RUC cost $ |",
          "|---|---|---|---|---|---|---|---|---|---|"]
    for _, r in days.iterrows():
        tol = "—" if pd.isna(r["tolerance"]) else f"{float(r['tolerance']):.2e}"
        nm = "—" if pd.isna(r["n_mip_solves"]) else f"{int(r['n_mip_solves'])}"
        L.append(f"| {int(r['task'])} | {r['requested_gap']} | {r['ruc_date']} | {r['status']} | {tol} | "
                 f"{'Y' if r['tolerance_ok'] else 'N'} | {float(r['final_gap_pct']):.4f} | "
                 f"{float(r['solve_time_s']):.1f} | {nm} | {float(r['ruc_cost']):,.0f} |")
    L += ["", "## 4. Byte identity of the control arm (task 1 vs smoke_v2)", ""]
    if len(summ) and 1 in set(summ["task"]):
        b = summ[summ["task"] == 1].iloc[0]
        ok = bool(b.get("byte_identical_to_ref", False))
        L.append(f"- `overall.csv` md5 task 1 `{b['overall_md5']}` vs reference "
                 f"`{b.get('ref_overall_md5', '—')}` → **{'PASS' if ok else 'FAIL'}**.")
        L.append(f"- Tables identical to the reference manifest: `{b.get('ref_tables_identical', '')}`.")
        L.append(f"- Tables different: `{b.get('ref_tables_different', '') or 'none'}`.")
        L.append("- FAIL means the `--ruc_mipgap` plumbing changed something besides the gap "
                 "(or the 120 s TL bound in smoke_v2 after all): stop, do not decide.")
    else:
        L.append("- task 1 not read.")
    L += ["", "## 5. Pre-registered rule (prompt 58 section 2) — printed, not decided", "",
          f"- Tightest passing arm: **{v['tightest_pass_task'] if v['tightest_pass_task'] else 'none'}** → "
          f"adopt `ruc_mipgap = {v['adopt']['ruc_mipgap']}`, `ruc_time_limit = {v['adopt']['ruc_time_limit']:.0f}`.",
          f"- Reason: {v['reason']}.",
          "- Rule: (i) every day OPTIMAL with tolerance line == requested gap; (ii) max per-day "
          "solve <= 600 s; (iii) 365 x max solve <= 61 h. Otherwise keep 0.01 / 120 and disclose.",
          "- Kay writes `waves/GAP_DECISION.json` "
          '`{"ruc_mipgap": …, "ruc_time_limit": …, "decided_by": "Kay", "date": …, '
          '"evidence": "extracts/smoke_gap"}`. Wave D refuses to start without it.', "",
          "## 6. Was tightening worth it? (cost shift vs the $11.3M single-site median)", ""]
    for _, r in summ.iterrows():
        if int(r["task"]) == 1:
            continue
        sc = r.get("delta_total_cost_scaled_year_usd", np.nan)
        L.append(f"- task {int(r['task'])} (gap {r['ruc_mipgap']}) vs task 1: 3-day d total cost "
                 f"{r.get('delta_total_cost_usd_vs_task1', np.nan):+,.0f} $ → x 365/3 = "
                 f"**{sc:+,.0f} $/yr** = {abs(sc) / REF_MEDIAN_SINGLE_SITE_USD:.2f} x the $11.3M "
                 f"median single-site |d total cost| (POOL_V2 section 6.1). G_run at this gap: "
                 f"{r['G_run_usd']:,.0f} $ over 3 days.")
    L += ["", "The scaled shift is the solver-hidden cost the 1 % gap left on the table on these 3 "
          "days, extrapolated linearly; it is a size indication, not a year estimate.", ""]
    return "\n".join(L)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--joblog", help="collector mode: parse this array .o log")
    ap.add_argument("--tolerance-out", help="collector mode: write ruc_tolerance.csv here")
    ap.add_argument("--extracts", help="reading mode: extracts/smoke_gap")
    ap.add_argument("--ref", default=None, help="reading mode: extracts/smoke_v2 (byte identity)")
    ap.add_argument("--out", default=HERE, help="reading mode: output dir for GAP_SMOKE.md etc.")
    args = ap.parse_args(argv)
    if args.joblog:
        if not args.tolerance_out:
            raise SystemExit("--joblog needs --tolerance-out")
        tol = parse_tolerance(args.joblog)
        os.makedirs(os.path.dirname(os.path.abspath(args.tolerance_out)), exist_ok=True)
        tol.to_csv(args.tolerance_out, index=False)
        print(f"ruc_tolerance: {len(tol)} RUC days from {args.joblog}; tolerances "
              f"{sorted(set(tol['tolerance'].dropna().map('{:.2e}'.format)))}")
        return 0
    if not args.extracts:
        raise SystemExit("reading mode needs --extracts (or --joblog for collector mode)")
    days, summ = read_smoke(args.extracts, args.ref)
    v = verdict(summ)
    os.makedirs(args.out, exist_ok=True)
    summ.to_csv(os.path.join(args.out, "gap_smoke.csv"), index=False)
    days.to_csv(os.path.join(args.out, "gap_smoke_days.csv"), index=False)
    md = fmt_md(days, summ, v, args.extracts, args.ref)
    with open(os.path.join(args.out, "GAP_SMOKE.md"), "w") as f:
        f.write(md + "\n")
    print(md)
    print("\nVERDICT (rule, not decision):", json.dumps(v))
    return 0


if __name__ == "__main__":
    sys.exit(main())
