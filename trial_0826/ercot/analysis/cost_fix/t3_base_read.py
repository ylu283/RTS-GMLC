#!/usr/bin/env python3
"""Prompt 36 T3 base read: v1 base_2019 vs v2 base_2019_v2 (wave A, 3 rows)
plus screening_v2/ercot row 11 (base replicate). Report only.

Curtailment = compute_objectives.metrics()["true_curt"] (non-PEM WIND + PV
rows of gen_summary), never the overall.csv curtailment. Reads only base
runs: no per-site screening_v2 row is touched here.

Output: analysis/cost_fix/t3_base_read.json (+ printed tables).
Env: /opt/anaconda3/bin/python (pandas).
"""
import itertools
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ERCOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ERCOT))
import compute_objectives as co  # noqa: E402

TL = 120.0
V1 = "base_2019:base"
V2_FULL = "base_2019_v2:1"
V2_REPS = ["base_2019_v2:1", "base_2019_v2:2", "base_2019_v2:3", "screening_v2/ercot:11"]
NUC = ("1", "93")


def d(key):
    return Path(co.run_dir(key))


def lmp_stats(key):
    lmp = pd.read_csv(d(key) / "bus_lmps.csv.gz")
    hs = pd.read_csv(d(key) / "hourly_summary.csv")
    short = set(map(tuple, hs[(hs.LoadShedding > 0) | (hs.ReserveShortfall > 0)][["Date", "Hour"]].values))
    keep = ~pd.Series([(a, b) in short for a, b in zip(lmp.Date, lmp.Hour)], index=lmp.index)
    sysmean = lmp[keep].groupby(["Date", "Hour"]).LMP.mean()
    return {"rt_mean": float(lmp.LMP[keep].mean()), "rt_median": float(lmp.LMP[keep].median()),
            "da_mean": float(lmp["LMP DA"][keep].mean()), "da_median": float(lmp["LMP DA"][keep].median()),
            "rt_mean_all_hours": float(lmp.LMP.mean()),
            "sys_hourly_mean_p05_p50_p95": [float(x) for x in sysmean.quantile([.05, .5, .95])],
            "rt_bus_min_max": [float(lmp.LMP.min()), float(lmp.LMP.max())],
            "shortfall_hours_excluded": len(short),
            "hourly_price_mean": float(hs.Price.mean())}


def nuclear(key):
    td = pd.read_csv(d(key) / "thermal.csv.gz")
    td["Generator"] = td.Generator.astype(str)
    g = co.gen_summary(str(d(key)))
    out = {}
    for u in NUC:
        t = td[td.Generator == u]
        on = t["Unit State"].astype(str).isin(["True", "1", "1.0"])
        pmax = float(g[g.Generator == u].pmax_mw.iloc[0])
        out[u] = {"on_hours": int(on.sum()), "hours": len(t),
                  "starts": float(g[g.Generator == u].starts.iloc[0]),
                  "mean_dispatch_when_on": float(t.Dispatch[on].mean()) if on.any() else 0.0,
                  "hours_at_pmax": int((t.Dispatch >= pmax - 1e-3).sum()), "pmax": pmax}
    return out


def overall(key):
    o = pd.read_csv(d(key) / "overall.csv").iloc[0]
    return {"total_cost": float(o["Total costs"]), "fixed_cost": float(o["Total fixed costs"]),
            "variable_cost": float(o["Total generation costs"]), "load_shed": float(o["Total load shedding"]),
            "reserve_shortfall": float(o["Total reserve shortfall"]), "on_offs": float(o["Total on/offs"]),
            "cum_avg_price": float(o["Cumulative average price"]),
            "overall_csv_curtailment_NOT_USED": float(o["Total renewables curtailment"])}


def cost_by_type(key):
    g = co.gen_summary(str(d(key)))
    th = g[g.unit_type.isin(["CT", "CC", "STEAM", "NUC", "COAL", "GAS"]) | g["Unit Cost"].notna()]
    s = th.groupby("unit_type")["Unit Cost"].sum()
    s = s[s != 0]
    return {k: {"cost": float(v), "share": float(v / s.sum())} for k, v in s.items()}


def ruc(keys):
    q = pd.concat([pd.read_csv(d(k) / "ruc_quality.csv").assign(run=k) for k in keys])
    out = {"n_solves": len(q), "status_counts": q.status.value_counts().to_dict(),
           "gap_pct_p50_p90_max": [float(x) for x in q.final_gap_pct.quantile([.5, .9, 1.0])],
           "solve_s_p50_p90_max": [float(x) for x in q.solve_time_s.quantile([.5, .9, 1.0])],
           "capped_share": float((q.solve_time_s >= 0.98 * TL).mean())}
    per = {k: float((g.solve_time_s >= 0.98 * TL).mean()) for k, g in q.groupby("run")}
    out["capped_share_per_run"] = per
    gaps = q.pivot_table(index="ruc_date", columns="run", values="final_gap_pct")
    out["gap_identical_across_reps"] = bool((gaps.nunique(axis=1) == 1).all())
    return out


def main():
    res = {"v1": {}, "v2": {}}
    for tag, key in (("v1", V1), ("v2", V2_FULL)):
        res[tag]["lmp"] = lmp_stats(key)
        res[tag]["overall"] = overall(key)
        res[tag]["objectives"] = co.metrics(key)
        res[tag]["nuclear"] = nuclear(key)
        res[tag]["cost_by_type"] = cost_by_type(key)
    res["v1"]["ruc"] = ruc([V1])
    res["v2"]["ruc"] = ruc(V2_REPS)

    reps = {k: co.metrics(k) for k in V2_REPS}
    pair = {}
    for obj in co.OBJ:
        dl = [abs(reps[a][obj] - reps[b][obj]) for a, b in itertools.combinations(V2_REPS, 2)]
        pair[obj] = {"pairwise_abs_delta": dl, "median": float(np.median(dl)), "max": float(max(dl))}
    res["v2"]["replicates"] = {"runs": V2_REPS, "df": len(V2_REPS) - 1, "values": reps, "pairwise": pair}
    files = ["overall.csv", "gen_summary.csv", "daily_summary.csv", "hourly_summary.csv", "committed_hourly.csv"]
    res["v2"]["replicates"]["byte_identical"] = {
        f: len({(d(k) / f).read_bytes() for k in V2_REPS}) == 1 for f in files}

    out = HERE / "t3_base_read.json"
    out.write_text(json.dumps(res, indent=1, default=float))
    print(json.dumps(res, indent=1, default=float))
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
