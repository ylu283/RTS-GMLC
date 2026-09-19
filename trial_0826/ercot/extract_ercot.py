#!/usr/bin/env python3
"""Slimmed per-run extract for ERCOT runs (prompt 26 T3). Raw run dirs stay
in $GROUP storage; this writes the few-MB committed extract that October's
analysis reuses with the RTS objective-extraction code (RTS-matching column
names, one table per objective-pool member):

    <out_dir>/                                   [slim = every run]
      gen_summary.csv        annual per-generator rollup: output_mwh,
                             curtailment_mwh, starts, cost/revenue/uplift,
                             unit_type (the HYDRO filter column — hydro
                             rows carry fake 'curtailment' = backing-down;
                             exclude Unit Type == HYDRO from all
                             curtailment sums), is_pem, pmax_mw
      renewables_hourly.csv  hourly Output/Curtailment by unit_type x
                             is_pem (duration curves; H2 stream = is_pem
                             Curtailment)
      committed_hourly.csv   hourly committed thermal MW + unit count
                             (conservative-DA mediation analogue)
      line_summary.csv       per-line annual flow stats + hours at >=99%
                             rating (congestion signal)
      hourly_summary.csv     hourly load / shed / renewables (as written)
      reserves.csv           reserves_detail (requirement + shortfall —
                             the degenerate-g4 evidence)
      daily_summary.csv      per-day costs & counts (as written)
      overall.csv            overall_simulation_output.csv (as written)
      ruc_quality.csv        rider (i): per-RUC-day MIPGap/status/SolCount
                             parsed from the job's solver log (needs
                             output_solver_logs=True — Prescient's CSVs
                             carry no gap/SolCount)
      extract_manifest.json  row counts + md5s
    with --full (smoke + base only):
      bus_lmps.csv.gz        hourly bus LMPs (Date,Hour,Bus,LMP,LMP DA)
      renewables.csv.gz      hourly per-gen Output/Curtailment + unit_type
      thermal.csv.gz         hourly per-gen Dispatch/Unit State/costs
      line_flows.csv.gz      hourly line_detail

Usage:
    python extract_ercot.py <run_dir> <out_dir> [--joblog <job .o file>]
                            [--full]

Default is the SLIM extract (~1-2 MB: annual per-gen rollup + system-level
hourly tables) used for screening runs; --full additionally writes the
hourly per-bus/per-gen/per-line tables (bus_lmps, renewables, thermal,
line_flows; ~40 MB) and is passed by the smoke and base collectors only.
SolCount=0 on any day is run-invalidating (rider (iv)) — flagged loudly.
"""
import gzip
import hashlib
import json
import re
import shutil
import sys
from argparse import ArgumentParser
from pathlib import Path

import pandas as pd

ERCOT_DIR = Path(__file__).resolve().parent
GEN_CSV = ERCOT_DIR / "data" / "ercot123_2019" / "gen.csv"


def unit_type_map():
    gen = pd.read_csv(GEN_CSV, usecols=["GEN UID", "Unit Type", "PMax MW"])
    gen["GEN UID"] = gen["GEN UID"].astype(str)
    return gen


def add_unit_type(df, gen):
    df = df.copy()
    df["Generator"] = df["Generator"].astype(str)
    # "_PEM" twins inherit the parent's unit_type
    parent = df["Generator"].str.replace(r"_PEM$", "", regex=True)
    df["unit_type"] = parent.map(dict(zip(gen["GEN UID"], gen["Unit Type"])))
    n_unmapped = df["unit_type"].isna().sum()
    if n_unmapped:
        names = sorted(df.loc[df["unit_type"].isna(), "Generator"].unique())
        print(f"WARNING: {n_unmapped} rows with unmapped generator names "
              f"(left NaN): {names[:8]}")
    return df


# --- rider (i): per-day RUC solution quality from the gurobi log -----------
# Log anatomy (verified against the prior full-year .o file): each RUC day
# reads
#   Creating and solving SCED to determine UC initial conditions for date:
#       YYYY-MM-DD hour: 0            <- names the RUC date (absent on day 1)
#   Extracting scenario to simulate   <- RUC segment opens
#   <gurobi MIP log — only with output_solver_logs=True>
#   Pyomo model solve time: ...
#   Deterministic RUC Cost: ...       <- RUC segment closes
# Gurobi MIP summary lines (Best objective/Solution count/Time limit) inside
# an open segment belong to the RUC — the SCEDs and the aCHP pricing
# instance are LPs and print no MIP summary.
DATE_RE = re.compile(r"UC initial conditions for date: (\d{4}-\d{2}-\d{2})")
OPEN_RE = re.compile(r"Extracting scenario to simulate")
CLOSE_RE = re.compile(r"Deterministic RUC Cost: ([-\d.]+)")
SOLVETIME_RE = re.compile(r"Pyomo model solve time: ([\d.]+)")
GAP_RE = re.compile(r"Best objective ([-\d.e+]+), best bound ([-\d.e+]+), "
                    r"gap ([\d.e+-]+)%")
SOLCOUNT_RE = re.compile(r"Solution count (\d+)")
TL_RE = re.compile(r"Time limit reached")
OPT_RE = re.compile(r"Optimal solution found")
FAIL_RE = re.compile(r"Failed to solve deterministic RUC instance")


def parse_ruc_quality(joblog: Path) -> pd.DataFrame:
    rows = []
    cur = None
    pending_date = "start_date"  # day 1's RUC has no date announcement
    for line in joblog.open(errors="replace"):
        m = DATE_RE.search(line)
        if m:
            pending_date = m.group(1)
            continue
        if OPEN_RE.search(line):
            cur = {"ruc_date": pending_date, "final_gap_pct": None,
                   "sol_count": None, "status": "UNKNOWN",
                   "solve_time_s": None, "ruc_cost": None}
            continue
        if cur is None:
            continue
        m = GAP_RE.search(line)
        if m:
            cur["final_gap_pct"] = float(m.group(3))
        m = SOLCOUNT_RE.search(line)
        if m:
            cur["sol_count"] = int(m.group(1))
        if TL_RE.search(line):
            cur["status"] = "TIME_LIMIT"
        elif OPT_RE.search(line):
            cur["status"] = "OPTIMAL"
        elif FAIL_RE.search(line):
            cur["status"] = "FAILED"
        m = SOLVETIME_RE.search(line)
        if m:
            cur["solve_time_s"] = float(m.group(1))
        m = CLOSE_RE.search(line)
        if m:
            cur["ruc_cost"] = float(m.group(1))
            rows.append(cur)
            cur = None
    return pd.DataFrame(rows)


def write_gz(df, path):
    with gzip.open(path, "wt", newline="") as f:
        df.to_csv(f, index=False)


def main(argv=None):
    ap = ArgumentParser(__doc__)
    ap.add_argument("run_dir", type=Path)
    ap.add_argument("out_dir", type=Path)
    ap.add_argument("--joblog", type=Path, default=None,
                    help="the SGE .o file holding the run's solver logs")
    ap.add_argument("--full", action="store_true",
                    help="also write the hourly per-bus/gen/line tables "
                    "(smoke + base collectors only)")
    args = ap.parse_args(argv)
    run, out = args.run_dir, args.out_dir
    if not (run / "overall_simulation_output.csv").is_file():
        raise SystemExit(f"ABORT: {run} has no overall_simulation_output.csv "
                         "(incomplete run — never extract partials)")
    out.mkdir(parents=True, exist_ok=True)
    gen = unit_type_map()
    manifest = {"mode": "full" if args.full else "slim"}

    rd = add_unit_type(pd.read_csv(run / "renewables_detail.csv"), gen)
    rd["is_pem"] = rd["Generator"].str.endswith("_PEM")
    td = add_unit_type(pd.read_csv(run / "thermal_detail.csv"), gen)
    ld = pd.read_csv(run / "line_detail.csv")

    for src, dst in [("hourly_summary.csv", "hourly_summary.csv"),
                     ("reserves_detail.csv", "reserves.csv"),
                     ("daily_summary.csv", "daily_summary.csv"),
                     ("overall_simulation_output.csv", "overall.csv")]:
        shutil.copyfile(run / src, out / dst)
        manifest[dst] = sum(1 for _ in open(run / src)) - 1

    # annual per-generator rollup (curtailment/starts/revenue objectives)
    money = [c for c in ("Unit Market Revenue", "Unit Uplift Payment")
             if c in rd.columns]
    ren_annual = (rd.groupby(["Generator", "unit_type", "is_pem"],
                             dropna=False)[["Output", "Curtailment"] + money]
                  .sum().reset_index()
                  .rename(columns={"Output": "output_mwh",
                                   "Curtailment": "curtailment_mwh"}))
    td = td.sort_values(["Generator", "Date", "Hour"])
    st = td.groupby("Generator")["Unit State"].apply(
        lambda s: int((s.astype(float).diff() == 1).sum()))
    th_money = [c for c in ("Unit Cost", "Unit Market Revenue",
                            "Unit Uplift Payment") if c in td.columns]
    th_annual = (td.groupby(["Generator", "unit_type"], dropna=False)
                 .agg(**{"output_mwh": ("Dispatch", "sum"),
                         **{c: (c, "sum") for c in th_money}})
                 .reset_index())
    th_annual["starts"] = th_annual["Generator"].map(st)
    gs = pd.concat([ren_annual, th_annual], ignore_index=True)
    gs["pmax_mw"] = gs["Generator"].astype(str).str.replace(
        r"_PEM$", "", regex=True).map(dict(zip(gen["GEN UID"], gen["PMax MW"])))
    gs.to_csv(out / "gen_summary.csv", index=False)
    manifest["gen_summary"] = len(gs)

    # system-level hourly tables (slim carriers of the hourly signals)
    rh = (rd.groupby(["Date", "Hour", "unit_type", "is_pem"], dropna=False)
          [["Output", "Curtailment"]].sum().reset_index())
    rh.to_csv(out / "renewables_hourly.csv", index=False)
    manifest["renewables_hourly"] = len(rh)

    # committed thermal capacity (mediation analogue for conservative-DA)
    tpm = td["Generator"].astype(str).map(dict(zip(gen["GEN UID"],
                                                   gen["PMax MW"])))
    cm = td.assign(committed_mw=td["Unit State"].astype(float)
                   * tpm.fillna(0.0).to_numpy())
    ch = (cm.groupby(["Date", "Hour"])
          .agg(committed_mw=("committed_mw", "sum"),
               num_committed=("Unit State", lambda s: int(s.astype(float).sum())))
          .reset_index())
    ch.to_csv(out / "committed_hourly.csv", index=False)
    manifest["committed_hourly"] = len(ch)

    # per-line annual summary (congestion signal; rating from branch.csv)
    br = pd.read_csv(GEN_CSV.parent / "branch.csv")
    rating = dict(zip(br["UID"].astype(str), br["Cont Rating"]))
    ld2 = ld.assign(abs_flow=ld["Flow"].abs())
    lname = (ld2["Line"].astype(str)
             .str.replace(r"\.0$", "", regex=True))   # float-read "1.0" -> "1"
    # our branch UIDs carry the L prefix (see make_metadata.fix_branch_csv);
    # bare-numeric names (e.g. prior GTEP outputs) fall back to L<name>
    ld2["cont_rating"] = lname.map(rating).fillna(("L" + lname).map(rating))
    lsum = (ld2.groupby("Line")
            .agg(cont_rating=("cont_rating", "first"),
                 max_abs_flow=("abs_flow", "max"),
                 p99_abs_flow=("abs_flow", lambda s: s.quantile(0.99)),
                 mean_abs_flow=("abs_flow", "mean"),
                 sum_violation=("Violation", "sum")).reset_index())
    at_limit = (ld2[ld2["abs_flow"] >= 0.99 * ld2["cont_rating"]]
                .groupby("Line").size())
    lsum["hours_ge_99pct"] = lsum["Line"].map(at_limit).fillna(0).astype(int)
    lsum.to_csv(out / "line_summary.csv", index=False)
    manifest["line_summary"] = len(lsum)

    if args.full:
        bd = pd.read_csv(run / "bus_detail.csv",
                         usecols=["Date", "Hour", "Bus", "LMP", "LMP DA"])
        write_gz(bd, out / "bus_lmps.csv.gz")
        manifest["bus_lmps"] = len(bd)
        write_gz(rd, out / "renewables.csv.gz")
        manifest["renewables"] = len(rd)
        keep = [c for c in ("Date", "Hour", "Generator", "Dispatch",
                            "Unit State", "Unit Cost", "Unit Market Revenue",
                            "unit_type") if c in td.columns]
        write_gz(td[keep], out / "thermal.csv.gz")
        manifest["thermal"] = len(td)
        write_gz(ld, out / "line_flows.csv.gz")
        manifest["line_flows"] = len(ld)

    if args.joblog and args.joblog.is_file():
        rq = parse_ruc_quality(args.joblog)
        rq.to_csv(out / "ruc_quality.csv", index=False)
        manifest["ruc_quality"] = len(rq)
        if len(rq):
            n_tl = (rq["status"] == "TIME_LIMIT").sum()
            zeros = rq[rq["sol_count"].fillna(1) == 0]
            print(f"ruc_quality: {len(rq)} RUC days, {n_tl} hit the time "
                  f"limit, median gap "
                  f"{rq['final_gap_pct'].median():.3g}% , P95 "
                  f"{rq['final_gap_pct'].quantile(0.95):.3g}%")
            if len(zeros):
                print(f"*** SolCount=0 on {len(zeros)} day(s) "
                      f"{list(zeros['ruc_date'])} — RUN-INVALIDATING "
                      "(rider (iv)): report, never average over. ***")
        else:
            print("WARNING: joblog parsed to 0 RUC days — wrong file, or "
                  "output_solver_logs was off")
    else:
        print("WARNING: no --joblog given/found — ruc_quality.csv NOT "
              "written (rider (i) unmet for this run)")

    for f in sorted(out.iterdir()):
        if f.name != "extract_manifest.json":
            manifest.setdefault("md5", {})[f.name] = hashlib.md5(
                f.read_bytes()).hexdigest()
    (out / "extract_manifest.json").write_text(json.dumps(manifest, indent=1))
    total = sum(f.stat().st_size for f in out.iterdir()) / 1e6
    print(f"extract complete: {out} ({total:.1f} MB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
