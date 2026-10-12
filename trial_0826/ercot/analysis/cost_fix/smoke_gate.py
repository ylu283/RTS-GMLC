#!/usr/bin/env python3
"""Prompt 36 smoke gate: Prescient v2 smoke (3 days from 2019-01-01) vs the
authors' SCUC on the same days (authors_scuc_sidebyside.py output).

Gate (prompt 36 §3, per day the authors' model solves):
  - Prescient RT system-mean LMP (unweighted mean over the 123 buses; hours
    with load shedding or reserve shortfall excluded) within ±$5/MWh OR ±20 %
    of the authors' system-mean LMP;
  - daily production cost (Prescient fixed + generation costs; authors' MIP
    objective = no-load + variable + start-up) within ±15 %.
Also reported: DA system-mean LMP, load-weighted prices, RUC gap / solve time /
capped-day share (TL = 120 s), nuclear on-hours.

Writes analysis/cost_fix/SMOKE_REPORT.md always; waves/smoke_v2/SMOKE_PASS only
when every gate passes and --write_pass is given. Reference = the authors' code
as shipped (daily-minimum DLR); the static-rating run is reported alongside.
"""
import argparse
import json
from datetime import date, timedelta
from pathlib import Path

import pandas as pd

ERCOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
TL = 120.0


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
                  "prod_cost": float(D["Fixed costs"] + D["Generation costs"]),
                  "fixed_cost": float(D["Fixed costs"]), "gen_cost": float(D["Generation costs"])}
    return out


def ruc_quality(ext):
    p = ext / "ruc_quality.csv"
    if not p.is_file():
        return None
    q = pd.read_csv(p)
    return {"n": len(q), "gap_pct_median": float(q["final_gap_pct"].median()),
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
    rows, ok_all, n_cmp = [], True, 0
    for d, p in P.items():
        for r, days in refs.items():
            au = days.get(str(d), {})
            if "lmp_system_mean_day" not in au:
                rows.append(f"| {p['date']} | {r} | {p['rt_lmp_mean']:.2f} | {p['da_lmp_mean']:.2f} | "
                            f"— ({au.get('mip_status', 'not run')}) | — | {p['prod_cost']:,.0f} | — | — | n/a |")
                continue
            dl = p["rt_lmp_mean"] - au["lmp_system_mean_day"]
            lmp_ok = abs(dl) <= 5 or abs(dl) <= 0.2 * abs(au["lmp_system_mean_day"])
            dc = (p["prod_cost"] - au["mip_objective"]) / au["mip_objective"]
            cost_ok = abs(dc) <= 0.15
            gate = lmp_ok and cost_ok
            if r == "dlr":
                ok_all &= gate
                n_cmp += 1
            rows.append(f"| {p['date']} | {r} | {p['rt_lmp_mean']:.2f} | {p['da_lmp_mean']:.2f} | "
                        f"{au['lmp_system_mean_day']:.2f} | {dl:+.2f} | {p['prod_cost']:,.0f} | "
                        f"{au['mip_objective']:,.0f} | {dc:+.1%} | "
                        f"{'PASS' if gate else 'FAIL'}{'' if r == 'dlr' else ' (context)'} |")
    ok_all &= n_cmp > 0
    rq = ruc_quality(a.extract)
    nh = nuclear_hours(a.extract)

    with open(a.report, "w") as fh:
        fh.write(f"# Smoke gate — Prescient v2 vs authors' SCUC (reading {a.reading})\n\n"
                 f"Prescient extract: `{a.extract.relative_to(ERCOT) if ERCOT in a.extract.parents else a.extract}`. "
                 "Authors: `authors_scuc_sidebyside.py` (Gurobi MIP 1 %, LP re-solve for prices). "
                 "Gate reference = authors' code as shipped (daily-minimum DLR); static-rating rows are context.\n\n"
                 "| day | authors ratings | Prescient RT mean LMP | Prescient DA mean LMP | authors mean LMP | Δ LMP | "
                 "Prescient prod. cost $ | authors cost $ | Δ cost | gate |\n"
                 "|---|---|---|---|---|---|---|---|---|---|\n" + "\n".join(rows) + "\n\n")
        fh.write("Prescient per day (RT hourly `Price` mean; LMP range; shortfall hours excluded from LMP means):\n\n")
        for d, p in P.items():
            fh.write(f"- {p['date']}: Price {p['rt_price_hourly_mean']:.2f}, RT LMP range {p['rt_lmp_min_max']}, "
                     f"shortfall hours {p['shortfall_hours']}, fixed ${p['fixed_cost']:,.0f}, "
                     f"generation ${p['gen_cost']:,.0f}\n")
        fh.write(f"\nRUC quality (TL = {TL:.0f} s): {rq}\n\nNuclear committed hours (gen 1, 93): {nh}; "
                 "authors: " + ", ".join(f"day {k}: {v.get('nuclear_on_hours')}" for k, v in refs['dlr'].items()) + "\n")
        fh.write(f"\n**Gate: {'PASS' if ok_all else 'FAIL'}** ({n_cmp} day(s) compared vs DLR reference)\n")
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
