#!/usr/bin/env python3
"""Prompt 36 T0 — re-check the §0.1 source facts (read-only).

Reads the paper's data (Generator_data.xlsx), the authors' SCUC case pickle
(123bus_case_final.pkl) and the v1 gen.csv; asserts each fact and writes
  analysis/cost_fix/T0_FACTS.md          (tables + PASS/FAIL per fact)
  analysis/cost_fix/source_coeffs_tx123.csv  (frozen per-unit source snapshot
                                              the converter + tests consume,
                                              so CRC needs neither xlsx nor pkl)

Needs pandas + openpyxl (local: /opt/anaconda3/bin/python). The pickle's
classes live in the authors' power_mod.py, which imports pypower at module
level; pypower is stubbed (only loadcase is referenced, never called on load).
"""
import hashlib
import pickle
import sys
import types
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ERCOT = HERE.parents[1]
SRC = Path("/Users/yilu/Documents/development/nd/research/gtep/123_bus_coal/"
           "ERCOT_BUS123_base_XC_editeddata")
PUB = SRC / "original_data" / "Data_public_5year"
SCUC = PUB / "Sample_Codes_SCUC"
XLSX = PUB / "Generator_data.xlsx"
PKL = SCUC / "123bus_case_final.pkl"
V1_GEN = ERCOT / "data" / "ercot123_2019" / "gen.csv"

THERMAL = ("CT", "COAL", "NUC")
FACTOR_B = 0.7


def md5(p):
    return hashlib.md5(Path(p).read_bytes()).hexdigest()


def load_pkl():
    pp = types.ModuleType("pypower")
    lc = types.ModuleType("pypower.loadcase")
    lc.loadcase = lambda *a, **k: (_ for _ in ()).throw(NotImplementedError)
    pp.loadcase = lc
    sys.modules.setdefault("pypower", pp)
    sys.modules.setdefault("pypower.loadcase", lc)
    sys.path.insert(0, str(SCUC))
    with open(PKL, "rb") as fh:
        case = pickle.load(fh)
    sys.path.remove(str(SCUC))
    return case


def relerr(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    den = np.maximum(np.abs(b), 1e-300)
    m = (np.abs(a) + np.abs(b)) > 0
    return float(np.max(np.abs(a - b)[m] / den[m])) if m.any() else 0.0


def main():
    facts = []

    def fact(name, ok, detail=""):
        facts.append((name, bool(ok), detail))
        print(("PASS " if ok else "FAIL ") + name + (f" — {detail}" if detail else ""))

    x = pd.read_excel(XLSX)
    v1 = pd.read_csv(V1_GEN)
    case = load_pkl()
    g = case.gen

    # --- row alignment: xlsx Gen Number == v1 GEN UID == pkl index + 1 -----
    fact("292 rows in xlsx / v1 / pkl",
         len(x) == len(v1) == len(g.Pmax) == 292)
    fact("xlsx Gen Number == v1 GEN UID == 1..292 (row order)",
         (x["Gen Number"].values == np.arange(1, 293)).all()
         and (v1["GEN UID"].astype(int).values == np.arange(1, 293)).all())
    th0 = v1["Unit Type"].isin(THERMAL).values
    fact("bus aligned xlsx/v1/pkl (all 292); Pmax aligned on the 128 thermal",
         (x["Bus Number"].values == v1["Bus ID"].values).all()
         and (x["Bus Number"].values == g.bus).all()
         and relerr(g.Pmax[th0], x["Pmax (MW)"].values[th0]) == 0
         and relerr(v1["PMax MW"].values[th0], x["Pmax (MW)"].values[th0]) == 0)

    th = v1["Unit Type"].isin(THERMAL).values
    fact("128 thermal units (CT 113, COAL 13, NUC 2)", th.sum() == 128,
         str(v1.loc[th, "Unit Type"].value_counts().to_dict()))

    C0x = x["C0($/MWh)"].values.astype(float)
    C1x = x["C1($/MWh)"].values.astype(float)
    Csx = x["Csu($)"].values.astype(float)
    fact("xlsx has NO C2 column", not any("C2" in c for c in x.columns),
         str(x.columns.tolist()))

    # --- pkl = 0.7 × xlsx on the 128 thermal units ------------------------
    for nm, pv, xv in (("c0", g.c0, C0x), ("c1", g.c1, C1x), ("c_su", g.c_su, Csx)):
        e = relerr(np.asarray(pv)[th], FACTOR_B * xv[th])
        fact(f"pkl {nm} == 0.7 × xlsx on all 128 thermal", e < 1e-12, f"max rel err {e:.2e}")
    fact("pkl Pmin == xlsx Pmin (thermal)", relerr(g.Pmin[th], x["Pmin (MW)"].values[th]) == 0)
    fact("pkl ramp_agc == xlsx ramp (thermal)",
         relerr(g.ramp_agc[th], x["Ramping Rate(MW/min)"].values[th]) == 0)
    pv_m = (v1["Unit Type"] == "PV").values
    e = relerr(g.Pmax[pv_m], 0.3 * x["Pmax (MW)"].values[pv_m])
    fact("pkl PV Pmax == 0.3 × xlsx PV Pmax (all 72)", e < 1e-12, f"max rel err {e:.2e}")
    hy = (v1["Unit Type"] == "HYDRO").values
    fact("hydro cost 0 in pkl (c0, c1)", (np.asarray(g.c0)[hy] == 0).all() and (np.asarray(g.c1)[hy] == 0).all())

    # --- v1 gen.csv: C0/C1/Csu == xlsx; HR_avg_0 = Csu·Pmax/fp; HR_incr = ΔC/fp
    for col, xv in (("C0", C0x), ("C1", C1x), ("Csu", Csx)):
        e = relerr(v1[col].values[th], xv[th])
        fact(f"v1 {col} == xlsx (thermal)", e == 0, f"max rel err {e:.2e}")
    fp = v1["Fuel Price $/MMBTU"].values.astype(float)
    pmax = v1["PMax MW"].values.astype(float)
    pmin = v1["PMin MW"].values.astype(float)
    e = relerr(v1["HR_avg_0"].values[th], (Csx * pmax / fp)[th])
    fact("v1 HR_avg_0 == Csu·Pmax/fp on all 128 thermal (the bug)", e < 1e-14, f"max rel err {e:.2e}")
    # HR_incr_k = ΔC_k/fp with C(P) = C0 + C1 P + 0.0016 P²
    worst = 0.0
    for k in (1, 2, 3):
        a = v1[f"Output_pct_{k-1}"].values * pmax
        b = v1[f"Output_pct_{k}"].values * pmax
        dC = C1x * (b - a) + 0.0016 * (b**2 - a**2)
        worst = max(worst, relerr(v1[f"HR_incr_{k}"].values[th], (dC / fp)[th]))
    fact("v1 HR_incr_k == ΔC_k/fp (segment heat, not a rate; C2 = 0.0016 every unit)",
         worst < 1e-9, f"max rel err {worst:.2e}")
    for col in ("Start Heat Cold MBTU", "Start Heat Warm MBTU", "Start Heat Hot MBTU",
                "Non Fuel Start Cost $"):
        fact(f"v1 {col} == 1 (thermal)", (v1[col].values[th] == 1).all())
    fact("v1 C2 == 0.0016 for every thermal unit", (v1["C2"].values[th] == 0.0016).all())
    fact("thermal Pmin = 0.3·Pmax", relerr(pmin[th], 0.3 * pmax[th]) < 1e-12)
    fact("thermal Pmin ≥ 3 MW", pmin[th].min() >= 3, f"min {pmin[th].min()}")
    fact("thermal Start Time * Hr == 1", (v1.loc[th, ["Start Time Cold Hr", "Start Time Warm Hr",
                                                        "Start Time Hot Hr"]].values == 1).all())
    fuel_fp = v1.loc[th].groupby("Unit Type")["Fuel Price $/MMBTU"].unique().to_dict()
    fact("fuel prices gas 2.29 / coal 1.78 / nuclear 0.81035",
         {k: list(v) for k, v in fuel_fp.items()} == {"CT": [2.29], "COAL": [1.78], "NUC": [0.81035]},
         str({k: list(v) for k, v in fuel_fp.items()}))

    # --- v1 no-load as egret reads it --------------------------------------
    noload_v1 = v1["HR_avg_0"].values / 1000 * pmin * fp      # $/h at Pmin
    fact("v1 nuclear cost at Pmin ≈ $2.1–2.6M/h",
         (noload_v1[(v1["Unit Type"] == "NUC").values] > 2.0e6).all(),
         ", ".join(f"{c:,.0f}" for c in noload_v1[(v1['Unit Type'] == 'NUC').values]))

    # --- authors' SCUC: linear objective, CONOPT ---------------------------
    ucf = (SCUC / "UC_function.py").read_text()
    fact("authors' objective = gen_cost_P·p·BaseMVA + gen_cost_NL·u + gen_cost_SU·v (linear)",
         "model.gen_cost_P[g] * model.p_g_t[g, t]*BaseMVA + model.gen_cost_NL[g] * model.u_g_t[g, t]" in ucf)
    fact("authors' solve_UC uses CONOPT", "SolverFactory('conopt'" in ucf)
    run = (SCUC / "Run_SCUC_annual.py").read_text()
    fact("×0.7 documented only as a code comment", "after the generator cost adjustment" in run
         and "0.7" not in (PUB / "Readme.txt").read_text())

    # --- frozen source snapshot --------------------------------------------
    snap = pd.DataFrame({
        "GEN UID": v1["GEN UID"].astype(int), "Unit Type": v1["Unit Type"],
        "PMin MW": pmin, "PMax MW": pmax, "Fuel Price $/MMBTU": fp,
        "C0_xlsx": C0x, "C1_xlsx": C1x, "Csu_xlsx": Csx,
        "c0_pkl": np.asarray(g.c0, float), "c1_pkl": np.asarray(g.c1, float),
        "csu_pkl": np.asarray(g.c_su, float),
    })[th]
    snap_path = HERE / "source_coeffs_tx123.csv"
    snap.to_csv(snap_path, index=False)

    # --- (a)/(b)/(c) cost tables by type (report for Kay) ------------------
    rows = []
    for name, fac, quad in (("(c) linear ×1.0", 1.0, False), ("(b) linear ×0.7", FACTOR_B, False),
                            ("(a) quadratic ×1.0", 1.0, True)):
        for t in THERMAL:
            m = (snap["Unit Type"] == t).values
            s = snap[m]
            c0, c1 = fac * s["C0_xlsx"], fac * s["C1_xlsx"]
            c2 = 0.0016 if (quad and t == "COAL") else 0.0
            mc_min = c1 + 2 * c2 * s["PMin MW"]
            mc_max = c1 + 2 * c2 * s["PMax MW"]
            start = (fac * s["Csu_xlsx"] * s["PMax MW"]) if name.startswith("(c)") or quad \
                else fac * s["Csu_xlsx"]
            rows.append({"reading": name, "type": t, "n": int(m.sum()),
                         "no-load $/h (median)": c0.median(),
                         "no-load $/h (range)": f"{c0.min():.0f}–{c0.max():.0f}",
                         "MC@Pmin $/MWh": f"{mc_min.min():.2f}–{mc_min.max():.2f}",
                         "MC@Pmax $/MWh": f"{mc_max.min():.2f}–{mc_max.max():.2f}",
                         "start $ (median)": start.median(),
                         "start $ (range)": f"{start.min():,.0f}–{start.max():,.0f}"})
    tab = pd.DataFrame(rows)

    # B position: cumulative thermal capacity with marginal cost < B (linear readings)
    def stack(fac, B=40.0):
        s = snap.assign(mc=fac * snap["C1_xlsx"]).sort_values("mc")
        cum = s["PMax MW"].cumsum()
        below = s["mc"] < B
        return (cum[below].iloc[-1] if below.any() else 0.0), cum.iloc[-1], s["mc"].max()

    pos = []
    for name, fac, B in (("(c) ×1.0", 1.0, 40), ("(b) ×0.7", 0.7, 40), ("(b′) ×0.7", 0.7, 28)):
        below, tot, mx = stack(fac, B)
        pos.append(f"| {name} | {B} | {below/1e3:.1f} GW of {tot/1e3:.1f} GW | {mx:.2f} |")

    # sample units
    ct = snap[snap["Unit Type"] == "CT"].iloc[0]
    coal = snap[snap["Unit Type"] == "COAL"].iloc[0]
    samp = []
    for r in (snap.iloc[0], coal, ct):
        samp.append(f"| {int(r['GEN UID'])} | {r['Unit Type']} | {r['C0_xlsx']:g} | {r['c0_pkl']:g} | "
                    f"{r['C1_xlsx']:g} | {r['c1_pkl']:g} | {r['Csu_xlsx']:g} | {r['csu_pkl']:g} |")

    out = HERE / "T0_FACTS.md"
    with open(out, "w") as fh:
        fh.write("# Prompt 36 T0 — source facts (generated by `t0_verify_sources.py`)\n\n")
        fh.write("Sources (md5):\n\n")
        for p in (XLSX, PKL, SCUC / "UC_function.py", SCUC / "Run_SCUC_annual.py", V1_GEN,
                  SRC / "2302.13231v3.pdf"):
            fh.write(f"- `{p.relative_to(SRC.parent) if SRC.parent in p.parents else p}` `{md5(p)}`\n")
        fh.write("\n## Facts\n\n| fact | result | detail |\n|---|---|---|\n")
        for n, ok, d in facts:
            fh.write(f"| {n} | {'PASS' if ok else '**FAIL**'} | {d} |\n")
        fh.write("\n## xlsx vs pkl (×0.7) — sample units\n\n"
                 "| gen | type | C0 xlsx | c0 pkl | C1 xlsx | c1 pkl | Csu xlsx | c_su pkl |\n"
                 "|---|---|---|---|---|---|---|---|\n" + "\n".join(samp) + "\n")
        fh.write("\n## Cost by reading and type\n\n"
                 "Start $: (c)/(a) = Csu·Pmax (Csu in $/installed MW); (b) = c_su per start "
                 "(authors' code).\n\n")
        fh.write(tab.to_markdown(index=False, floatfmt=",.0f") + "\n")
        fh.write("\n## Where B sits (linear readings; merit order by C1)\n\n"
                 "| reading | B $/MWh | thermal capacity with C1 < B | max thermal C1 |\n"
                 "|---|---|---|---|\n" + "\n".join(pos) + "\n")
    print(f"wrote {out}\nwrote {snap_path}")
    n_fail = sum(not ok for _, ok, _ in facts)
    print(f"T0: {len(facts) - n_fail}/{len(facts)} PASS")
    return 1 if n_fail else 0


if __name__ == "__main__":
    sys.exit(main())
