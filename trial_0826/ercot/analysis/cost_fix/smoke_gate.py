#!/usr/bin/env python3
"""Prompt 36 smoke gate: Prescient v2 smoke (3 days from 2019-01-01) vs the
authors' SCUC on the same days (authors_scuc_sidebyside.py output).

Gate (prompt 36 §3 as amended 10-12, before any smoke result):
  - daily production cost (Prescient fixed + generation costs; authors' MIP
    objective = no-load + variable + start-up) within ±15 % of the authors'
    SCUC (daily-minimum DLR, as shipped), on every day the authors' model solves;
  - every RUC solve OPTIMAL or final gap <= 1 % (mipgap);
  - Prescient RT system-mean LMP (unweighted mean over the 123 buses; hours
    with load shedding or reserve shortfall excluded) inside the $10–60/MWh
    sanity band (Table VI envelope), every day;
  - no load shed outside the known pattern (v1: zero shed everywhere -> zero).
REPORTED, not gated: the LMP side-by-side vs the authors' duals (the dual
extraction is not trusted — amendment), DA LMP, load-weighted prices, reserve
shortfall, solve times / capped-day share (TL = 120 s), gen-1 / gen-93 on-hours.

Writes analysis/cost_fix/SMOKE_REPORT.md always; waves/smoke_v2/SMOKE_PASS only
when every gate passes and --write_pass is given. Static-rating authors' rows
are context only.
"""
import argparse
import json
from datetime import date, timedelta
from pathlib import Path

import pandas as pd

ERCOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
TL = 120.0
LMP_BAND = (10.0, 60.0)
COST_TOL = 0.15
GAP_MAX_PCT = 1.0


def prescient_days(ext):
    lmp = pd.read_csv(ext / "bus_lmps.csv.gz")
    hs = pd.read_csv(ext / "hourly_summary.csv")
    ds = pd.read_csv(ext / "daily_summary.csv")
    short = hs[(hs["LoadShedding"] > 0) | (hs["ReserveShortfall"] > 0)][["Date", "Hour"]]
    key = set(map(tuple, short.values))
    lmp["short"] = [(d, h) in key for d, h in zip(lmp["Date"], lmp["Hour"])]
    out = {}
    for i, day in enumerate(sorted(ds["Date"].unique()), start=1):
        L = lmp[(lmp["Date"] == day) & ~lmp["short"]]
        H = hs[hs["Date"] == day]
        D = ds[ds["Date"] == day].iloc[0]
        out[i] = {"date": day,
                  "rt_lmp_mean": float(L["LMP"].mean()) if len(L) else float("nan"),
                  "da_lmp_mean": float(L["LMP DA"].mean()) if len(L) else float("nan"),
                  "rt_price_hourly_mean": float(H["Price"].mean()),
                  "rt_lmp_min_max": [float(L["LMP"].min()), float(L["LMP"].max())] if len(L) else None,
                  "shortfall_hours": int(((H["LoadShedding"] > 0) | (H["ReserveShortfall"] > 0)).sum()),
                  "load_shed_mwh": float(H["LoadShedding"].sum()),
                  "reserve_shortfall_mwh": float(H["ReserveShortfall"].sum()),
                  "prod_cost": float(D["Fixed costs"] + D["Generation costs"]),
                  "fixed_cost": float(D["Fixed costs"]), "gen_cost": float(D["Generation costs"])}
    return out


def ruc_quality(ext):
    p = ext / "ruc_quality.csv"
    if not p.is_file():
        return None
    q = pd.read_csv(p)
    gap_ok = (q["status"].astype(str).str.upper() == "OPTIMAL") | (q["final_gap_pct"] <= GAP_MAX_PCT)
    return {"n": len(q), "all_ok": bool(gap_ok.all()),
            "statuses": q["status"].astype(str).tolist(),
            "gaps_pct": [round(float(x), 4) for x in q["final_gap_pct"]],
            "gap_pct_median": float(q["final_gap_pct"].median()),
            "gap_pct_max": float(q["final_gap_pct"].max()),
            "solve_s_median": float(q["solve_time_s"].median()),
            "solve_s_max": float(q["solve_time_s"].max()),
            "capped_share": float((q["solve_time_s"] >= 0.98 * TL).mean())}


def nuclear_hours(ext):
    p = ext / "thermal.csv.gz"
    if not p.is_file():
        return None
    td = pd.read_csv(p)
    td["Generator"] = td["Generator"].astype(str)
    return {g: int((td[td.Generator == g]["Unit State"].astype(float) > 0).sum()) for g in ("1", "93")}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--extract", type=Path, default=ERCOT / "extracts" / "smoke_v2")
    ap.add_argument("--reading", default="c")
    ap.add_argument("--report", type=Path, default=HERE / "SMOKE_REPORT.md")
    ap.add_argument("--write_pass", action="store_true")
    a = ap.parse_args(argv)

    P = prescient_days(a.extract)
    refs = {r: json.loads((HERE / f"authors_scuc_{a.reading}_{r}_d1-2-3.json").read_text())["days"]
            for r in ("dlr", "static")}
    rq = ruc_quality(a.extract)
    nh = nuclear_hours(a.extract)
    rows, sanity, n_cmp = [], [], 0
    cost_ok_all = True
    for d, p in P.items():
        for r, days in refs.items():
            au = days.get(str(d), {})
            if "mip_objective" not in au:
                rows.append(f"| {p['date']} | {r} | {p['prod_cost']:,.0f} | — ({au.get('mip_status', 'not run')}) | — | "
                            f"n/a | {p['rt_lmp_mean']:.2f} | — | — |")
                continue
            dc = (p["prod_cost"] - au["mip_objective"]) / au["mip_objective"]
            cost_ok = abs(dc) <= COST_TOL
            if r == "dlr":
                cost_ok_all &= cost_ok
                n_cmp += 1
            rows.append(f"| {p['date']} | {r} | {p['prod_cost']:,.0f} | {au['mip_objective']:,.0f} | {dc:+.1%} | "
                        f"{'PASS' if cost_ok else 'FAIL'}{'' if r == 'dlr' else ' (context)'} | "
                        f"{p['rt_lmp_mean']:.2f} | {au['lmp_system_mean_day']:.2f} | "
                        f"{p['rt_lmp_mean'] - au['lmp_system_mean_day']:+.2f} |")
        lmp_ok = LMP_BAND[0] <= p["rt_lmp_mean"] <= LMP_BAND[1]
        shed_ok = p["load_shed_mwh"] == 0
        sanity.append((p, lmp_ok, shed_ok))
    gates = {
        f"cost within ±{COST_TOL:.0%} of authors (DLR), {n_cmp} day(s)": cost_ok_all and n_cmp > 0,
        f"every RUC OPTIMAL or gap <= {GAP_MAX_PCT:g} %": bool(rq and rq["all_ok"]),
        f"RT system-mean LMP in ${LMP_BAND[0]:.0f}–{LMP_BAND[1]:.0f}/MWh every day": all(x[1] for x in sanity),
        "zero load shed (known pattern)": all(x[2] for x in sanity),
    }
    ok_all = all(gates.values())

    with open(a.report, "w") as fh:
        fh.write(f"# Smoke gate — Prescient v2 vs authors' SCUC (reading {a.reading})\n\n"
                 f"Prescient extract: `{a.extract.relative_to(ERCOT) if ERCOT in a.extract.parents else a.extract}`. "
                 "Authors: `authors_scuc_sidebyside.py` (Gurobi MIP 1 %, LP re-solve for prices). "
                 "Gate per prompt 36 §3 AMENDMENT 10-12: cost ±15 % vs the authors' code as shipped "
                 "(daily-minimum DLR) + RUC solves + LMP sanity band + shed. "
                 "Static-rating rows and the LMP side-by-side are reported, not gated.\n\n")
        fh.write("## Gate\n\n| check | result |\n|---|---|\n"
                 + "".join(f"| {k} | {'PASS' if v else 'FAIL'} |\n" for k, v in gates.items())
                 + f"\n**Gate: {'PASS' if ok_all else 'FAIL'}**\n\n")
        fh.write("## Daily production cost (gated vs DLR) and LMP side-by-side (reported only)\n\n"
                 "| day | authors ratings | Prescient prod. cost $ | authors cost $ | Δ cost | cost gate | "
                 "Prescient RT mean LMP | authors mean LMP | Δ LMP |\n"
                 "|---|---|---|---|---|---|---|---|---|\n" + "\n".join(rows) + "\n\n")
        fh.write("## Prescient per day\n\n| day | RT mean LMP | in band | DA mean LMP | hourly Price mean | RT LMP range | "
                 "load shed MWh | reserve shortfall MWh | fixed $ | generation $ |\n|---|---|---|---|---|---|---|---|---|---|\n")
        for p, lmp_ok, shed_ok in sanity:
            rng = "—" if p["rt_lmp_min_max"] is None else f"{p['rt_lmp_min_max'][0]:.2f} – {p['rt_lmp_min_max'][1]:.2f}"
            fh.write(f"| {p['date']} | {p['rt_lmp_mean']:.2f} | {'yes' if lmp_ok else 'NO'} | {p['da_lmp_mean']:.2f} | "
                     f"{p['rt_price_hourly_mean']:.2f} | {rng} | {p['load_shed_mwh']:,.1f} | "
                     f"{p['reserve_shortfall_mwh']:,.1f} | {p['fixed_cost']:,.0f} | {p['gen_cost']:,.0f} |\n")
        fh.write(f"\nShortfall hours (shed or reserve shortfall) are excluded from the LMP means.\n\n"
                 f"RUC quality (TL = {TL:.0f} s): {rq}\n\nNuclear committed hours (gen 1, 93): {nh}; "
                 "authors (DLR): " + ", ".join(f"day {k}: {v.get('nuclear_on_hours')}" for k, v in refs['dlr'].items()) + "\n")
    print(a.report.read_text())
    if ok_all and a.write_pass:
        sp = ERCOT / "waves" / "smoke_v2" / "SMOKE_PASS"
        sp.write_text(f"SMOKE PASS {date.today().isoformat()} — {a.report.name}\n")
        print(f"wrote {sp}")
    elif a.write_pass:
        print("gate FAILED — SMOKE_PASS not written (Kay decides)")
    return 0 if ok_all else 1


if __name__ == "__main__":
    raise SystemExit(main())
