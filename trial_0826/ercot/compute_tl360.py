"""Prompt 33 collector brain: TL=360 readings — QUARANTINED solver identity.

Writes analysis/tl360_probe/objectives_tl360.csv (per-run metrics incl.
gen-1 starts + gap stats) and tl360_readings.json (3 pairwise |Delta| per
objective, df = 2). NEVER touches noise_ruler_v2.json — TL=360 readings
must not mix with TL=120 rulers (prompt 33 red line). Pure pandas/numpy.
"""

import itertools
import json
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
EXTR = os.path.join(HERE, "extracts", "tl360_probe")
OUT = os.path.join(HERE, "analysis", "tl360_probe")
OBJ = ["true_curt", "h2", "var_cost", "reserve", "onoffs", "total_cost",
       "fixed_cost"]


def metrics(i):
    d = os.path.join(EXTR, f"run_index_{i}")
    o = pd.read_csv(os.path.join(d, "overall.csv")).iloc[0]
    g = pd.read_csv(os.path.join(d, "gen_summary.csv"))
    g["Generator"] = g["Generator"].astype(str)
    g["is_pem"] = g["is_pem"].fillna(False).astype(bool)
    vre = (~g.is_pem) & g.unit_type.isin(["WIND", "PV"])
    g1 = g[g.Generator == "1"].iloc[0]
    rq = pd.read_csv(os.path.join(d, "ruc_quality.csv"))
    rq = rq[rq.ruc_date != "start_date"]
    gaps = rq.final_gap_pct.astype(float)
    capped = (rq.status == "TIME_LIMIT").mean()
    return {"true_curt": float(g[vre].curtailment_mwh.sum()),
            "h2": float(g[g.is_pem].curtailment_mwh.sum()),
            "var_cost": float(o["Total generation costs"]),
            "reserve": float(o["Total reserve shortfall"]),
            "onoffs": float(o["Total on/offs"]),
            "total_cost": float(o["Total costs"]),
            "fixed_cost": float(o["Total fixed costs"]),
            "gen1_starts": float(g1["starts"]),
            "gen1_unit_cost": float(g1["Unit Cost"]),
            "gen1_output_mwh": float(g1["output_mwh"]),
            "gap_median_pct": float(gaps.median()),
            "gap_p95_pct": float(gaps.quantile(0.95)),
            "frac_capped": float(capped),
            "solve_time_median_s": float(rq.solve_time_s.astype(float).median())}


def main():
    os.makedirs(OUT, exist_ok=True)
    rows = [{"wave": "tl360_probe", "index": i,
             "ruc_time_limit": 360, **metrics(i)} for i in (1, 2, 3)]
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(OUT, "objectives_tl360.csv"), index=False)

    readings = {"solver_identity": "TL=360 — QUARANTINED from all TL=120 "
                                   "rulers/deltas (prompt 33 red line)",
                "df": 2}
    for obj in OBJ:
        vals = df[obj].to_numpy(float)
        deltas = [abs(a - b) for a, b in itertools.combinations(vals, 2)]
        readings[obj] = {"values": [round(v, 4) for v in vals],
                         "pairwise_abs_delta": [round(d, 4) for d in deltas]}
    readings["gen1_starts_by_solve"] = df.gen1_starts.tolist()
    readings["gen1_pinned"] = bool(df.gen1_starts.nunique() == 1)
    readings["gaps"] = df[["gap_median_pct", "gap_p95_pct",
                           "frac_capped"]].to_dict("records")
    with open(os.path.join(OUT, "tl360_readings.json"), "w") as f:
        json.dump(readings, f, indent=2)
        f.write("\n")
    print("gen-1 starts by solve:", df.gen1_starts.tolist(),
          "| pinned:", readings["gen1_pinned"])
    print("total_cost pairwise |D|:",
          readings["total_cost"]["pairwise_abs_delta"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
