#!/usr/bin/env python3
"""T-M1: base-case per-site distributions -> omega bounds (doc 14 section 3.1, section 6).

Reads the full-year Prescient base-case output in ../base_case_pcm_test/ and
RTS_Data/SourceData/{gen,bus}.csv, produces tm1_per_site_stats.csv and the
tables consumed by tm1_report.md. Deterministic, seed-free, re-runnable.
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
BASE = HERE.parent / "base_case_pcm_test"
SRC = HERE.parent.parent / "RTS_Data" / "SourceData"

SITES = [
    "303_WIND_1", "317_WIND_1", "122_WIND_1", "319_PV_1", "310_PV_2",
    "324_PV_3", "324_PV_2", "309_WIND_1", "324_PV_1", "320_PV_1",
]
HOURS_EXPECTED = 8784
SYSTEM_CURT_EXPECTED = 1_688_576.0   # MWh, doc 14 section 1
SITE303_CURT_EXPECTED = 620_727.0    # MWh
LMP_THRESHOLDS = [10.0, 15.0, 25.0]
CURT_HOUR_MW = 5.0                   # site curtailment > 5 MW defines a curtailment-hour
OMEGA_MIN = {"WIND": 0.05, "PV": 0.02}
INFO_CURT_GWH = 20.0                 # report-only threshold for extra units


def die(msg):
    sys.exit(f"SANITY CHECK FAILED: {msg}")


def pctl(x, q):
    x = np.asarray(x, dtype=float)
    return float(np.percentile(x, q)) if x.size else float("nan")


def main():
    # ---------------- Task 1: load and validate ----------------
    ren = pd.read_csv(BASE / "renewables_detail.csv")
    need = {"Date", "Hour", "Generator", "Output", "Curtailment"}
    if not need.issubset(ren.columns):
        die(f"renewables_detail.csv missing columns {need - set(ren.columns)}")

    nan_counts = ren[["Output", "Curtailment"]].isna().sum()
    if nan_counts.any():
        die(f"NaNs in renewables_detail: {nan_counts.to_dict()}")

    per_gen_hours = ren.groupby("Generator").size()
    bad = per_gen_hours[per_gen_hours != HOURS_EXPECTED]
    if len(bad):
        die(f"generators without {HOURS_EXPECTED} rows: {bad.to_dict()}")

    ren["Available"] = ren["Output"] + ren["Curtailment"]
    curt_by_gen = ren.groupby("Generator")["Curtailment"].sum()
    system_curt = float(curt_by_gen.sum())
    if abs(system_curt - SYSTEM_CURT_EXPECTED) > 0.01 * SYSTEM_CURT_EXPECTED:
        die(f"system curtailment {system_curt:,.0f} MWh vs expected {SYSTEM_CURT_EXPECTED:,.0f} (+/-1%)")
    c303 = float(curt_by_gen["303_WIND_1"])
    if abs(c303 - SITE303_CURT_EXPECTED) > 0.01 * SITE303_CURT_EXPECTED:
        die(f"303_WIND_1 curtailment {c303:,.0f} MWh vs expected {SITE303_CURT_EXPECTED:,.0f} (+/-1%)")

    gen_src = pd.read_csv(SRC / "gen.csv")
    bus_src = pd.read_csv(SRC / "bus.csv")
    gen2bus = gen_src.set_index("GEN UID")["Bus ID"].to_dict()
    bus2name = bus_src.set_index("Bus ID")["Bus Name"].to_dict()
    pmax = gen_src.set_index("GEN UID")["PMax MW"].to_dict()

    site_bus = {s: (gen2bus[s], bus2name[gen2bus[s]]) for s in SITES}

    bus = pd.read_csv(BASE / "bus_detail.csv", usecols=["Date", "Hour", "Bus", "LMP"])
    lmp_nans = int(bus["LMP"].isna().sum())
    if lmp_nans:
        die(f"NaNs in bus_detail LMP: {lmp_nans}")
    bus_names_needed = {name for _, name in site_bus.values()}
    lmp = {}
    for name in sorted(bus_names_needed):
        sub = bus[bus["Bus"] == name].sort_values(["Date", "Hour"])
        if len(sub) != HOURS_EXPECTED:
            die(f"bus {name} has {len(sub)} rows, expected {HOURS_EXPECTED}")
        lmp[name] = sub["LMP"].to_numpy()

    print(f"Sanity checks PASSED: {len(per_gen_hours)} generators x {HOURS_EXPECTED} h; "
          f"system curtailment {system_curt:,.0f} MWh; 303_WIND_1 {c303:,.0f} MWh; "
          f"0 NaNs in Output/Curtailment/LMP columns used.")

    # ---------------- Task 3: ranking (29 WIND/PV, system denominator) ----------------
    types = gen_src.set_index("GEN UID")["Unit Type"].to_dict()
    windpv = sorted(g for g in curt_by_gen.index if types.get(g) in ("WIND", "PV"))
    avail_max = ren.groupby("Generator")["Available"].max()
    rank = (
        pd.DataFrame({
            "generator": windpv,
            "unit_type": [types[g] for g in windpv],
            "nameplate_mw": [float(pmax.get(g) if pd.notna(pmax.get(g)) else avail_max[g]) for g in windpv],
            "annual_curtailment_mwh": [float(curt_by_gen[g]) for g in windpv],
        })
        .sort_values("annual_curtailment_mwh", ascending=False)
        .reset_index(drop=True)
    )
    rank["share_of_system"] = rank["annual_curtailment_mwh"] / system_curt
    rank["cumulative_share"] = rank["share_of_system"].cumsum()
    rank.to_csv(HERE / "tm1_ranking.csv", index=False)

    extra = rank[(rank["annual_curtailment_mwh"] > INFO_CURT_GWH * 1000)
                 & (~rank["generator"].isin(SITES))]
    print("Informational >20 GWh non-campaign units:",
          {r.generator: round(r.annual_curtailment_mwh) for r in extra.itertuples()} or "none")

    # ---------------- Tasks 2 & 4: per-site stats ----------------
    rows = []
    for s in SITES:
        g = ren[ren["Generator"] == s].sort_values(["Date", "Hour"])
        curt = g["Curtailment"].to_numpy()
        avail = g["Available"].to_numpy()
        bus_id, bus_name = site_bus[s]
        p = lmp[bus_name]
        np_mw = float(pmax.get(s) if pd.notna(pmax.get(s)) else avail_max[s])
        utype = types[s]

        row = {
            "site": s, "unit_type": utype, "bus_id": bus_id, "bus_name": bus_name,
            "nameplate_mw": np_mw,
            "annual_curtailment_mwh": float(curt.sum()),
            "curt_mean_mw": float(curt.mean()),
            "curt_p50_mw": pctl(curt, 50), "curt_p90_mw": pctl(curt, 90),
            "curt_p95_mw": pctl(curt, 95), "curt_p99_mw": pctl(curt, 99),
            "curt_max_mw": float(curt.max()),
        }

        for thr in LMP_THRESHOLDS:
            m = p < thr
            a = avail[m]
            t = int(thr)
            row[f"hours_lmp_lt{t}"] = int(m.sum())
            row[f"frac_hours_lmp_lt{t}"] = float(m.mean())
            row[f"avail_lmp_lt{t}_mean_mw"] = float(a.mean()) if a.size else float("nan")
            row[f"avail_lmp_lt{t}_p90_mw"] = pctl(a, 90)
            row[f"avail_lmp_lt{t}_p95_mw"] = pctl(a, 95)
            # informational daylight-only (available > 0) P90
            row[f"avail_lmp_lt{t}_p90_daylight_mw"] = pctl(a[a > 0], 90)

        ch = curt > CURT_HOUR_MW
        row["curtailment_hours_gt5mw"] = int(ch.sum())
        row["frac_curt_hours_lmp_le1"] = float((p[ch] <= 1.0).mean()) if ch.any() else float("nan")

        # Task 4: omega bounds. Raw ratio from P90(avail | LMP<15); floor at
        # curtailment P95 ratio, cap at 1.0, then round UP to one decimal.
        raw = row["avail_lmp_lt15_p90_mw"] / np_mw
        floor = row["curt_p95_mw"] / np_mw
        bounded = min(max(raw, floor), 1.0)
        omega_max = float(np.ceil(bounded * 10) / 10)
        row["omega_ratio_raw"] = raw
        row["omega_ratio_curt_p95"] = floor
        row["omega_min"] = OMEGA_MIN[utype]
        row["omega_max_recommended"] = omega_max
        row["omega_oat_reference"] = round(omega_max / 2, 2)
        rows.append(row)

    stats = pd.DataFrame(rows)
    stats.to_csv(HERE / "tm1_per_site_stats.csv", index=False)
    print(f"Wrote {HERE / 'tm1_per_site_stats.csv'} ({len(stats)} sites) and tm1_ranking.csv "
          f"({len(rank)} WIND/PV units).")
    with pd.option_context("display.width", 250, "display.max_columns", 100):
        print(stats[["site", "bus_name", "nameplate_mw", "curt_p95_mw",
                     "avail_lmp_lt15_p90_mw", "avail_lmp_lt15_p90_daylight_mw",
                     "omega_min", "omega_max_recommended", "omega_oat_reference"]])


if __name__ == "__main__":
    main()
