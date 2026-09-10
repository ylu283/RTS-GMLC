#!/usr/bin/env python3
"""Extract mediation variables for the conservative-DA story (prompt 20 T4;
19b SC): per run, the twin sites' cleared-vs-withheld energy and the fleet's
committed thermal capacity, to test whether shed/reserve/starts move through
committed capacity as B varies.

Usage (on the CRC group clone, where waves/<wave>/runs/ exists):

    python extract_mediation.py waves/contour_303x317_A
    python extract_mediation.py waves/sweep_B

Writes <wave_dir>/mediation.csv with one row per run x retrofitted
renewable site (thermal retrofits carry no gen_PEM twin and are skipped for
the per-site columns):

    index, site, pem_bid, pem_fraction,
    pem_sales_mwh          gen_PEM cleared (sold) energy
    pem_withheld_mwh       gen_PEM withheld energy (the H2 stream)
    fleet_committed_mwh    sum over thermal units of Unit State x PMax hours
    committed_mwh_top5     the same, restricted to the top-5% net-load hours
                           (net load = Demand - available renewables, from
                           hourly_summary.csv; NaN + warning if not derivable)

File discovery and column conventions mirror summarize_wave.py (same run-dir
layout, same sentinel, same Unit State dtype guard). Missing files/columns
degrade to NaN with a WARNING — never guessed column names, never fake zeros.
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from summarize_wave import SENTINEL, _unit_state_bool, load_pmax_lookup

CAMPAIGN_DIR = Path(__file__).resolve().parent

TOP_FRACTION = 0.05  # "top-5% net-load hours"


def hourly_committed_mw(run_dir: Path, pmax_lookup: dict):
    """Per-hour committed thermal capacity [MW]: sum over thermal units of
    Unit State x PMax. Returns a DataFrame indexed by (Date, Hour) with a
    'committed_mw' column, or None (+ prints WARNING) if inputs are absent."""
    path = run_dir / "thermal_detail.csv"
    if not path.is_file():
        print(f"    WARNING: {run_dir.name}: thermal_detail.csv missing — "
              "committed-capacity columns emitted as NaN")
        return None
    td = pd.read_csv(path, usecols=["Date", "Hour", "Generator", "Unit State"])
    pmax = td["Generator"].map(pmax_lookup)
    missing = td.loc[pmax.isna(), "Generator"].unique()
    if len(missing):
        print(f"    WARNING: {run_dir.name}: generators missing from gen.csv "
              f"PMax lookup (excluded from committed capacity): {sorted(missing)}")
    committed = _unit_state_bool(td["Unit State"]).to_numpy() * pmax.fillna(0.0).to_numpy()
    out = (pd.DataFrame({"Date": td["Date"], "Hour": td["Hour"], "mw": committed})
           .groupby(["Date", "Hour"], sort=True)["mw"].sum().rename("committed_mw"))
    return out.reset_index()


def net_load(run_dir: Path):
    """Hourly net load [MW] = Demand - available renewables (RenewablesUsed +
    RenewablesCurtailment), from hourly_summary.csv. Note: with PEM twins the
    withheld H2 stream sits inside RenewablesCurtailment, so 'available
    renewables' means pre-diversion availability — a consistent stress metric
    across runs. Returns DataFrame (Date, Hour, net_load_mw) or None."""
    path = run_dir / "hourly_summary.csv"
    if not path.is_file():
        print(f"    WARNING: {run_dir.name}: hourly_summary.csv missing — "
              "top-5% net-load column emitted as NaN")
        return None
    hs = pd.read_csv(path)
    needed = {"Date", "Hour", "Demand", "RenewablesUsed", "RenewablesCurtailment"}
    absent = needed - set(hs.columns)
    if absent:
        print(f"    WARNING: {run_dir.name}: hourly_summary.csv lacks columns "
              f"{sorted(absent)} — top-5% net-load column emitted as NaN")
        return None
    hs = hs[list(needed)].copy()
    hs["net_load_mw"] = hs["Demand"] - (hs["RenewablesUsed"] + hs["RenewablesCurtailment"])
    return hs[["Date", "Hour", "net_load_mw"]]


def extract_run(run_dir: Path, retrofit: dict, pmax_lookup: dict):
    """Mediation rows for one completed run. Returns a list of dicts (one per
    retrofitted renewable site with a gen_PEM twin in the outputs)."""
    rd = pd.read_csv(run_dir / "renewables_detail.csv",
                     usecols=["Generator", "Output", "Curtailment"])
    per_gen = rd.groupby("Generator")[["Output", "Curtailment"]].sum()

    committed = hourly_committed_mw(run_dir, pmax_lookup)
    if committed is None:
        fleet_mwh = float("nan")
        top5_mwh = float("nan")
    else:
        fleet_mwh = float(committed["committed_mw"].sum())  # 1 h steps -> MWh
        nl = net_load(run_dir)
        if nl is None:
            top5_mwh = float("nan")
        else:
            merged = committed.merge(nl, on=["Date", "Hour"], how="inner")
            if len(merged) < len(committed):
                print(f"    WARNING: {run_dir.name}: only {len(merged)}/"
                      f"{len(committed)} committed hours matched net-load hours")
            thr = merged["net_load_mw"].quantile(1.0 - TOP_FRACTION)
            top5_mwh = float(merged.loc[merged["net_load_mw"] >= thr,
                                        "committed_mw"].sum())

    rows = []
    for site, cfg in retrofit.items():
        pem = f"{site}_PEM"
        if pem not in per_gen.index:
            # thermal retrofits (no twin) and absent sites: per-site columns
            # are about the renewable twin only
            if site in per_gen.index or "gen_pmax" in cfg:
                print(f"    WARNING: {run_dir.name}: no {pem} in "
                      "renewables_detail — site skipped")
            continue
        rows.append({
            "site": site,
            "pem_bid": cfg.get("PEM_bid", float("nan")),
            "pem_fraction": cfg.get("PEM_fraction", float("nan")),
            "pem_sales_mwh": float(per_gen.loc[pem, "Output"]),
            "pem_withheld_mwh": float(per_gen.loc[pem, "Curtailment"]),
            "fleet_committed_mwh": fleet_mwh,
            "committed_mwh_top5": top5_mwh,
        })
    return rows


def crosscheck_site_detail(wave: Path, med: pd.DataFrame):
    """pem_sales must reproduce site_detail.csv's pem_grid_sales_mwh."""
    sd_path = wave / "site_detail.csv"
    if not sd_path.is_file():
        print("  (no site_detail.csv — cross-check skipped)")
        return
    sd = pd.read_csv(sd_path)
    if not {"index", "site", "pem_grid_sales_mwh"} <= set(sd.columns):
        print("  WARNING: site_detail.csv lacks expected columns — cross-check skipped")
        return
    m = med.merge(sd[["index", "site", "pem_grid_sales_mwh"]],
                  on=["index", "site"], how="inner")
    if not len(m):
        print("  WARNING: cross-check found no overlapping (index, site) rows")
        return
    worst = float((m["pem_sales_mwh"] - m["pem_grid_sales_mwh"]).abs().max())
    status = "OK" if worst < 1.0 else "MISMATCH — investigate before use"
    print(f"  cross-check vs site_detail pem_grid_sales_mwh: "
          f"max |diff| = {worst:.3g} MWh over {len(m)} rows [{status}]")


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 1:
        raise SystemExit(__doc__)
    wave = (CAMPAIGN_DIR / argv[0]).resolve() if not Path(argv[0]).is_absolute() \
        else Path(argv[0])
    dm = pd.read_csv(wave / "design_matrix.csv")
    pmax_lookup = load_pmax_lookup()

    all_rows, missing = [], []
    for _, drow in dm.iterrows():
        i = int(drow["index"])
        run_dir = wave / "runs" / f"run_index_{i}"
        if not (run_dir / SENTINEL).is_file():
            missing.append(i)
            continue
        with open(wave / f"retrofit_gen_dict_{i}.json") as f:
            retrofit = json.load(f)
        for row in extract_run(run_dir, retrofit, pmax_lookup):
            all_rows.append({"index": i, **row})

    med = pd.DataFrame(all_rows)
    if not len(med):
        print(f"{wave.name}: NO runs with renewable twins found — nothing written")
        if missing:
            print(f"MISSING run dirs: indices {missing}")
        return 1
    med.to_csv(wave / "mediation.csv", index=False)
    print(f"{wave.name}: {med['index'].nunique()} runs, {len(med)} site-rows "
          "-> mediation.csv")
    if missing:
        print(f"MISSING (not extracted): indices {missing}")
    crosscheck_site_detail(wave, med)
    return 0


if __name__ == "__main__":
    sys.exit(main())
