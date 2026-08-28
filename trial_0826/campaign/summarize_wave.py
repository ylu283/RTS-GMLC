#!/usr/bin/env python3
"""Summarize a campaign wave's Prescient runs into objectives.csv + site_detail.csv.

Usage:
    python summarize_wave.py <wave_dir> [--base <base_case_dir>]

Accounting rules (doc 14 sec. 4):
- True curtailment EXCLUDES `*_PEM` units. A gen_PEM's "Curtailment" column
  is its withheld energy, i.e. the H2-bound stream (Prescient cannot tell
  priced withholding from curtailment).
- Thermal (nuclear) H2 = sum(p_max - Dispatch): with forced commitment and
  p_min = p_max - PEM_cap, the withheld band is exactly the PEM's intake.
- psi = 20 kg H2 per MWh (frozen convention).
- "Total costs" from Prescient is contaminated by synthetic bid costs at
  retrofitted sites: the thermal patch deletes the real fuel cost and prices
  the PEM band at B (so the retrofitted unit's entire Unit Cost is
  synthetic), and gen_PEM output is costed at B in the objective. We report
  the raw total, the synthetic component, and total-less-synthetic.
  NOTE: total-less-synthetic is still not a clean f5 vs the base case,
  because the base-case nuclear's real fuel cost is present in the base
  total but absent from the retrofit total. delta_cost_* is therefore
  APPROXIMATE until f5 accounting is finalized (doc 14 sec. 4, f5 bullet).
- Delta columns compare against the full-year base case and are emitted only
  for num_days == 366 rows (NaN otherwise).

Missing/incomplete runs are reported and skipped, never fatal.
"""
import argparse
import json
import sys
from pathlib import Path

import pandas as pd

PSI_KG_PER_MWH = 20.0
SENTINEL = "overall_simulation_output.csv"

CAMPAIGN_DIR = Path(__file__).resolve().parent
TRIAL_DIR = CAMPAIGN_DIR.parent
GEN_CSV = TRIAL_DIR.parent / "RTS_Data" / "SourceData" / "gen.csv"


def load_pmax_lookup():
    g = pd.read_csv(GEN_CSV, usecols=["GEN UID", "PMax MW"])
    return dict(zip(g["GEN UID"], g["PMax MW"]))


# g4 source (math-log §3): "Total reserve shortfall" in
# overall_simulation_output.csv — the annual total in MWh. Verified on the
# base case against reserves_detail.csv's per-hour "Shortfall" sum
# (203,681.35 MWh, agree to 1e-5); the overall column is used because it is
# one pre-aggregated number per run.
RESERVE_SHORTFALL_COL = "Total reserve shortfall"


def reserve_shortfall_mwh(ov: pd.DataFrame, where: str):
    if RESERVE_SHORTFALL_COL not in ov.columns:
        print(f"    WARNING: {where}: column {RESERVE_SHORTFALL_COL!r} absent from "
              f"{SENTINEL} — g4 emitted as NaN, NOT zero. Investigate before use.")
        return float("nan")
    return ov[RESERVE_SHORTFALL_COL].sum()


def _unit_state_bool(s: pd.Series):
    """Coerce thermal_detail 'Unit State' to bool. Real Prescient output
    parses as bool dtype (True/False strings); guard the numeric-0/1 and
    unparsed-string cases so a dtype drift can never silently miscount
    (bare astype(bool) would map ANY non-empty string, incl. 'False', to True)."""
    if s.dtype == bool:
        return s
    if s.dtype == object:
        mapped = s.map({"True": True, "False": False, True: True, False: False})
        assert not mapped.isna().any(), \
            f"unrecognized Unit State values: {sorted(s[mapped.isna()].unique())}"
        return mapped.astype(bool)
    return s.astype(float) > 0.5


def fleet_thermal_starts(run_dir: Path):
    """g5 (math-log §3): fleet startup count S = sum_g sum_t
    1[u_t = 1 and u_{t-1} = 0], per generator sorted by time; the first hour
    compares against itself (no start)."""
    td = pd.read_csv(run_dir / "thermal_detail.csv",
                     usecols=["Generator", "Date", "Hour", "Minute", "Unit State"])
    # ISO dates sort lexicographically; stable sort keeps file order within ties
    td = td.sort_values(["Generator", "Date", "Hour", "Minute"], kind="stable")
    starts = 0
    for _, grp in td.groupby("Generator", sort=False):
        u = _unit_state_bool(grp["Unit State"]).to_numpy()
        starts += int((u[1:] & ~u[:-1]).sum())
    return starts


def base_aggregates(base_dir: Path):
    ov = pd.read_csv(base_dir / SENTINEL)
    rd = pd.read_csv(base_dir / "renewables_detail.csv",
                     usecols=["Generator", "Curtailment"])
    return {
        "curtailment_mwh": rd["Curtailment"].sum(),
        "load_shed_mwh": ov["Total load shedding"].sum(),
        "total_cost_usd": ov["Total costs"].sum(),
        "reserve_shortfall_mwh": reserve_shortfall_mwh(ov, str(base_dir)),
        "thermal_starts": fleet_thermal_starts(base_dir),
    }


def summarize_run(run_dir: Path, retrofit: dict, pmax_lookup: dict):
    ov = pd.read_csv(run_dir / SENTINEL)
    rd = pd.read_csv(
        run_dir / "renewables_detail.csv",
        usecols=["Generator", "Output", "Curtailment",
                 "Unit Market Revenue", "Unit Uplift Payment"])
    is_pem = rd["Generator"].str.endswith("_PEM")

    row = {
        "true_curtailment_mwh": rd.loc[~is_pem, "Curtailment"].sum(),
        "load_shed_mwh": ov["Total load shedding"].sum(),
        "total_cost_raw_usd": ov["Total costs"].sum(),
        "reserve_shortfall_mwh": reserve_shortfall_mwh(ov, run_dir.name),
        "thermal_starts": fleet_thermal_starts(run_dir),
    }

    ren_groups = rd.groupby("Generator").sum(numeric_only=True)
    thermal_sites = [s for s in retrofit if s in pmax_lookup
                     and f"{s}_PEM" not in ren_groups.index and s not in ren_groups.index]
    # thermal detail only needed if any retrofitted site is thermal
    td_groups = None
    if thermal_sites:
        td = pd.read_csv(
            run_dir / "thermal_detail.csv",
            usecols=["Generator", "Dispatch", "Unit Cost",
                     "Unit Market Revenue", "Unit Uplift Payment"])
        td = td[td["Generator"].isin(thermal_sites)]
        td_counts = td.groupby("Generator").size()
        td_groups = td.groupby("Generator").sum(numeric_only=True)

    site_rows, synthetic_cost, h2_total_mwh = [], 0.0, 0.0
    for site, cfg in retrofit.items():
        bid = cfg["PEM_bid"]
        frac = cfg["PEM_fraction"]
        pem_name = f"{site}_PEM"
        if pem_name in ren_groups.index:  # renewable retrofit
            pem = ren_groups.loc[pem_name]
            parent_rev = (ren_groups.loc[site, "Unit Market Revenue"]
                          if site in ren_groups.index else 0.0)
            h2_mwh = pem["Curtailment"]
            syn = pem["Output"] * bid  # gen_PEM output costed at B in the objective
            site_rows.append({
                "site": site, "kind": "renewable",
                "pem_capacity_mw": frac * cfg["gen_pmax"], "pem_bid": bid,
                "h2_mwh": h2_mwh, "h2_kg": h2_mwh * PSI_KG_PER_MWH,
                "pem_grid_sales_mwh": pem["Output"],
                "site_market_revenue_usd": parent_rev + pem["Unit Market Revenue"],
                "uplift_usd": pem["Unit Uplift Payment"],
            })
        elif td_groups is not None and site in td_groups.index:  # thermal retrofit
            t = td_groups.loc[site]
            pmax = pmax_lookup[site]
            hours = int(td_counts[site])  # hourly rows for this unit
            h2_mwh = pmax * hours - t["Dispatch"]
            syn = t["Unit Cost"]  # real fuel cost deleted by the patch -> all synthetic
            site_rows.append({
                "site": site, "kind": "thermal",
                "pem_capacity_mw": frac * pmax, "pem_bid": bid,
                "h2_mwh": h2_mwh, "h2_kg": h2_mwh * PSI_KG_PER_MWH,
                "pem_grid_sales_mwh": float("nan"),
                "site_market_revenue_usd": t["Unit Market Revenue"],
                "uplift_usd": t["Unit Uplift Payment"],
            })
        else:
            print(f"    WARNING: retrofitted site {site} not found in run output")
            continue
        synthetic_cost += syn
        h2_total_mwh += h2_mwh

    row["synthetic_bid_cost_usd"] = synthetic_cost
    row["total_cost_less_synthetic_usd"] = row["total_cost_raw_usd"] - synthetic_cost
    row["pem_withheld_mwh_total"] = h2_total_mwh
    row["h2_kg_total"] = h2_total_mwh * PSI_KG_PER_MWH
    return row, site_rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("wave_dir", type=Path)
    ap.add_argument("--base", type=Path, default=TRIAL_DIR / "base_case_pcm_test",
                    help="full-year base-case output dir (delta baseline)")
    args = ap.parse_args()

    wave = args.wave_dir.resolve()
    dm = pd.read_csv(wave / "design_matrix.csv")
    pmax_lookup = load_pmax_lookup()
    base = base_aggregates(args.base.resolve())

    obj_rows, site_rows_all, missing = [], [], []
    for _, drow in dm.iterrows():
        i = int(drow["index"])
        run_dir = wave / "runs" / f"run_index_{i}"
        if not (run_dir / SENTINEL).is_file():
            missing.append(i)
            continue
        with open(wave / f"retrofit_gen_dict_{i}.json") as f:
            retrofit = json.load(f)
        row, site_rows = summarize_run(run_dir, retrofit, pmax_lookup)
        full_year = int(drow["num_days"]) == 366
        row = {
            "index": i,
            "oat_site": drow.get("oat_site", ""),
            "anchor": drow.get("anchor", False),
            "num_days": int(drow["num_days"]),
            "start_date": drow["start_date"],
            # v3 derived-bid scenario, passed through from the design matrix
            # (math-log §1.3); NaN for pre-v3 waves whose matrices lack it
            "rho_h2": float(drow["rho_h2"]) if "rho_h2" in dm.columns else float("nan"),
            **row,
            "delta_curtailment_mwh":
                row["true_curtailment_mwh"] - base["curtailment_mwh"] if full_year else float("nan"),
            "delta_load_shed_mwh":
                row["load_shed_mwh"] - base["load_shed_mwh"] if full_year else float("nan"),
            "delta_cost_less_synthetic_usd_APPROX":
                row["total_cost_less_synthetic_usd"] - base["total_cost_usd"] if full_year else float("nan"),
            "delta_reserve_shortfall_mwh":
                row["reserve_shortfall_mwh"] - base["reserve_shortfall_mwh"] if full_year else float("nan"),
            "delta_thermal_starts":
                row["thermal_starts"] - base["thermal_starts"] if full_year else float("nan"),
        }
        obj_rows.append(row)
        for s in site_rows:
            site_rows_all.append({"index": i, **s})

    if not obj_rows:
        # never overwrite a previous summary with an empty table: a wave whose
        # runs/ is absent (e.g. not yet synced from CRC) must be a no-op
        print(f"{wave.name}: NO completed runs found — objectives.csv untouched")
        print(f"MISSING (not summarized): indices {missing}")
        return 1

    obj = pd.DataFrame(obj_rows)
    site = pd.DataFrame(site_rows_all)
    obj.to_csv(wave / "objectives.csv", index=False)
    site.to_csv(wave / "site_detail.csv", index=False)

    print(f"{wave.name}: {len(obj_rows)} runs summarized -> objectives.csv, site_detail.csv")
    if missing:
        print(f"MISSING (not summarized): indices {missing}")
        print("Run resubmit_missing.py to regenerate, then re-run this script.")

    # repeat-consistency check: identical designs must yield identical objectives
    design_cols = [c for c in dm.columns
                   if c.endswith("_omega") or c.endswith("_bid")] + ["num_days", "oat_site"]
    merged = dm[["index"] + design_cols].merge(
        obj[["index", "true_curtailment_mwh", "load_shed_mwh", "total_cost_raw_usd"]],
        on="index")
    for _, grp in merged.groupby(design_cols, dropna=False):
        if len(grp) > 1:
            vals = grp[["true_curtailment_mwh", "load_shed_mwh", "total_cost_raw_usd"]]
            status = "IDENTICAL" if (vals.nunique() == 1).all() else "DIFFER (noise!)"
            print(f"repeat group (indices {sorted(grp['index'])}): objectives {status}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
