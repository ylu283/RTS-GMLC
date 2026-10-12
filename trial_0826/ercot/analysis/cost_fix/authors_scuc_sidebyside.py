#!/usr/bin/env python3
"""Prompt 36 smoke gate, authors' side: run the TX-123BT authors' own SCUC
(`Sample_Codes_SCUC/UC_function.py`) on 2019 days 1–3 with the chosen cost
reading, a MIP solver instead of CONOPT, and write daily cost + hourly prices.

Changes vs the shipped code (everything else is theirs, run from a scratch copy):
  - costs: reading (c) — c0, c1 = pkl ÷ 0.7 (= xlsx C0, C1); start-up =
    (c_su ÷ 0.7)·Pmax (Csu in $/installed MW, as v2). `--reading b` keeps the pkl.
  - run 1: Gurobi MIP, MIPGap 1 % (their `mipgap = 0.01`), Threads 4;
  - run 2 (u fixed from run 1): v_g_t relaxed to continuous so the problem is
    an LP and the nodal-balance duals exist (with u fixed, v = max(0, Δu));
    prices = dual / BaseMVA, as their write_UCresult_day.
Kept as theirs: daily-minimum dynamic line ratings, reserve ≥ largest unit,
no min up/down, independent 24 h days, hydro at 0 cost.

Env: bogp conda (pyomo + gurobipy). Output: analysis/cost_fix/authors_scuc_<reading>_d1-3.json
"""
import argparse
import json
import os
import shutil
import sys
import tempfile
import types
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
SCUC = Path("/Users/yilu/Documents/development/nd/research/gtep/123_bus_coal/"
            "ERCOT_BUS123_base_XC_editeddata/original_data/Data_public_5year/"
            "Sample_Codes_SCUC")
THERMAL_FUELS = {"Natural Gas", "Coal", "Nuclear"}


def stub_pypower():
    pp = types.ModuleType("pypower")
    lc = types.ModuleType("pypower.loadcase")
    lc.loadcase = lambda *a, **k: (_ for _ in ()).throw(NotImplementedError)
    pp.loadcase = lc
    sys.modules.setdefault("pypower", pp)
    sys.modules.setdefault("pypower.loadcase", lc)


def day_inputs(case, d, ratings="dlr"):
    """Replicates run_annual_UC's per-day data preparation (Run_SCUC_annual.py).
    ratings="static" keeps the pkl rateA (== v1 branch.csv Cont Rating) instead
    of the daily-minimum dynamic rating — the like-for-like variant vs Prescient."""
    import UC_function as uc
    if ratings == "dlr":
        line_annual = np.loadtxt("Line_annual_Dmin.txt")
        for l in range(case.branchtotnum):
            case.branch.rateA[l] = line_annual[l][d - 1]
    solar_d = np.loadtxt(f"solar_annual/solar_annual_D{d}.txt")
    wind_d = np.loadtxt(f"wind_annual/wind_annual_D{d}.txt")
    load_d = np.loadtxt(f"load_annual/load_annual_D{d}.txt")
    s_idx, _ = uc.find_solar_bus(case)
    w_idx, _ = uc.find_wind_bus(case)
    load_b_t = np.transpose(load_d).copy()
    for h in range(24):
        for i, g in enumerate(w_idx):
            load_b_t[case.gen.bus[g] - 1, h] -= wind_d[i, h]
        for i, g in enumerate(s_idx):
            load_b_t[case.gen.bus[g] - 1, h] -= solar_d[i, h]
    return load_b_t, float(load_d.sum()), float(wind_d.sum() + solar_d.sum())


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--reading", choices=("c", "b"), default="c")
    ap.add_argument("--days", default="1,2,3")
    ap.add_argument("--time_limit", type=float, default=900)
    ap.add_argument("--ratings", choices=("dlr", "static"), default="dlr")
    a = ap.parse_args(argv)
    from pyomo.environ import NonNegativeReals, SolverFactory, value
    import pickle

    work = Path(tempfile.mkdtemp(prefix="authors_scuc_"))
    shutil.copytree(SCUC, work / "scuc", ignore=shutil.ignore_patterns("UC_results", "__pycache__"))
    os.chdir(work / "scuc")
    stub_pypower()
    sys.path.insert(0, str(work / "scuc"))
    import UC_function as uc

    with open("123bus_case_final.pkl", "rb") as fh:
        case = pickle.load(fh)
    g = case.gen
    th = np.array([f in THERMAL_FUELS for f in g.fuel_type])
    assert th.sum() == 128
    if a.reading == "c":
        g.c0 = np.where(th, np.asarray(g.c0) / 0.7, g.c0)
        g.c1 = np.where(th, np.asarray(g.c1) / 0.7, g.c1)
        g.c_su = np.where(th, np.asarray(g.c_su) / 0.7 * np.asarray(g.Pmax), g.c_su)

    out = {"reading": a.reading, "ratings": a.ratings, "solver": "gurobi_direct MIPGap 0.01 Threads 4; run2 LP (v relaxed)",
           "scratch": str(work), "days": {}}
    for d in [int(x) for x in a.days.split(",")]:
        load_b_t, load_mwh, ren_mwh = day_inputs(case, d, a.ratings)
        m1 = uc.build_UC_full(case, load_b_t)
        s1 = SolverFactory("gurobi_direct")
        s1.options.update({"MIPGap": 0.01, "Threads": 4, "TimeLimit": a.time_limit})
        r1 = s1.solve(m1, load_solutions=False)
        tc = str(r1.solver.termination_condition)
        try:
            m1.solutions.load_from(r1)
            mip_obj = value(m1.object)
        except (ValueError, RuntimeError):   # e.g. infeasible: the model has no load-shed slack
            out["days"][d] = {"load_mwh": load_mwh, "wind_solar_mwh": ren_mwh, "mip_status": tc}
            print(f"day {d}: MIP {tc} — no solution")
            continue
        m2 = uc.build_UC_full_Run2(case, m1, load_b_t)
        for v in m2.v_g_t.values():
            v.domain = NonNegativeReals
        s2 = SolverFactory("gurobi_direct")
        s2.options.update({"Threads": 4})
        r2 = s2.solve(m2, load_solutions=True)
        lmp = np.array([[m2.dual[m2.nodal_balance_cons[b, t]] / 100.0 for t in m2.TIME]
                        for b in m2.BUS])          # $/MWh [bus][hour]
        sys_mean = lmp.mean(axis=0)
        u = np.array([[m1.u_g_t[gg, t].value for t in m1.TIME] for gg in m1.GEN])
        starts = np.array([[m1.v_g_t[gg, t].value for t in m1.TIME] for gg in m1.GEN])
        p = np.array([[m1.p_g_t[gg, t].value * 100 for t in m1.TIME] for gg in m1.GEN])
        gi = np.array([int(gg) - 1 for gg in m1.GEN])      # model GEN = non-wind/solar units
        c0 = np.asarray(g.c0)[gi]; c1 = np.asarray(g.c1)[gi]; csu = np.asarray(g.c_su)[gi]
        thg = th[gi]
        fuel = np.array(g.fuel_type)[gi]
        out["days"][d] = {
            "load_mwh": load_mwh, "wind_solar_mwh": ren_mwh,
            "mip_status": str(r1.solver.termination_condition),
            "mip_objective": mip_obj,
            "noload_cost": float((c0[:, None] * u).sum()),
            "variable_cost": float((c1[:, None] * p).sum()),
            "startup_cost": float((csu[:, None] * starts).sum()),
            "lp_status": str(r2.solver.termination_condition),
            "lp_objective": value(m2.object),
            "lmp_system_mean_hourly": [round(float(x), 4) for x in sys_mean],
            "lmp_system_mean_day": float(sys_mean.mean()),
            "lmp_min_max": [float(lmp.min()), float(lmp.max())],
            "lmp_load_weighted_day": float((lmp * np.maximum(np.transpose(
                np.loadtxt(f"load_annual/load_annual_D{d}.txt")), 0)).sum()
                / np.maximum(np.loadtxt(f"load_annual/load_annual_D{d}.txt"), 0).sum()),
            "units_committed_mean": float(u[thg].sum(axis=0).mean()),
            "nuclear_on_hours": [int(round(u[i].sum())) for i in np.where(fuel == "Nuclear")[0]],
        }
        print(f"day {d}: MIP {out['days'][d]['mip_status']} obj ${mip_obj:,.0f}; "
              f"LP {out['days'][d]['lp_status']}; system-mean LMP {sys_mean.mean():.2f} $/MWh "
              f"(hourly {sys_mean.min():.2f}–{sys_mean.max():.2f})")
    dst = HERE / f"authors_scuc_{a.reading}_{a.ratings}_d{a.days.replace(',', '-')}.json"
    dst.write_text(json.dumps(out, indent=1))
    print(f"wrote {dst}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
