#!/usr/bin/env python3
"""Screening TOP-UP wave (prompt 26 T4, 2026-09-21).

The base_2019 extract confirmed what block #4's gate suspected: the
availability proxy is a poor curtailment predictor here — only 3 of the 9
drafted OAT sites (275, 274, 30) sit in the base's actual top-12
curtailers. Curtailment concentrates at congestion-trapped sites, not big
ones (site 163: 185 MW, yet it curtails 2.5x its own delivered energy).

Resolution (two-arm design, no run wasted either way):
  * screening_ercot (v1) becomes the AVAILABILITY/CONTRAST arm — its
    high-availability low-curtailment sites test whether retrofit value
    tracks curtailment or just size; it also carries __ALL__ and the two
    replicate noise-ruler rows.
  * screening_topup (this wave) is the CURTAILMENT arm: the top-12 actual
    curtailers minus the 3 already in v1, capped at 7 by rank. Together
    the two arms cover the actual top-10 exactly.

Deterministic: slate computed from the committed base extract and the
committed v1 design matrix; ranking written alongside as provenance.
No extra replicates here — the TL=120 noise ruler rides in v1 (identical
config family). omega = 0.5 wind / 0.4 PV, bid = 40.0 (v1 convention).
"""
import csv
import json
from pathlib import Path

import pandas as pd

ERCOT_DIR = Path(__file__).resolve().parent
WAVE_DIR = ERCOT_DIR / "waves" / "screening_topup"
V1_DIR = ERCOT_DIR / "waves" / "screening_ercot"

BID = 40.0
OMEGA = {"WIND": 0.5, "PV": 0.4}
START_DATE, NUM_DAYS = "01-01-2019", 365
TOP_N, CAP = 12, 7


def main():
    WAVE_DIR.mkdir(parents=True, exist_ok=True)
    gs = pd.read_csv(ERCOT_DIR / "extracts" / "base_2019" / "gen_summary.csv")
    vre = (gs[gs.unit_type.isin(["WIND", "PV"])]  # HYDRO excluded: fake curtailment
           .sort_values("curtailment_mwh", ascending=False)
           .reset_index(drop=True))
    vre["rank"] = vre.index + 1
    vre.head(30)[["rank", "Generator", "unit_type", "curtailment_mwh",
                  "output_mwh", "pmax_mw"]].to_csv(
        WAVE_DIR / "curtailment_ranking_base2019.csv", index=False)

    v1 = pd.read_csv(V1_DIR / "design_matrix.csv")
    v1_sites = {s for s in v1["oat_site"].astype(str) if not s.startswith("__")}
    top = vre.head(TOP_N)
    slate = [str(g) for g in top["Generator"].astype(str) if str(g) not in v1_sites][:CAP]

    gen = pd.read_csv(ERCOT_DIR / "data" / "ercot123_2019" / "gen.csv")
    bus = dict(zip(gen["GEN UID"].astype(str), gen["Bus ID"]))
    info = vre.set_index(vre["Generator"].astype(str))

    rows, dicts = [], {}
    for i, s in enumerate(slate, start=1):
        ut = info.loc[s, "unit_type"]
        rows.append([i, s, ut, bus[s], OMEGA[ut], BID,
                     float(info.loc[s, "pmax_mw"]), START_DATE, NUM_DAYS, ""])
        dicts[i] = {s: {"PEM_bid": BID, "PEM_fraction": OMEGA[ut],
                        "gen_pmax": float(info.loc[s, "pmax_mw"])}}

    with open(WAVE_DIR / "design_matrix.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["index", "oat_site", "unit_type", "bus", "omega", "bid",
                    "gen_pmax", "start_date", "num_days", "replicate_of"])
        w.writerows(rows)
    for idx, d in dicts.items():
        with open(WAVE_DIR / f"retrofit_gen_dict_{idx}.json", "w") as f:
            json.dump(d, f, indent=2, sort_keys=True)
            f.write("\n")

    covered = v1_sites | set(slate)
    top10 = [str(g) for g in vre.head(10)["Generator"].astype(str)]
    print(f"{WAVE_DIR.name}: {len(rows)} OAT rows: {slate}")
    print(f"top-10 coverage across both arms: "
          f"{sum(s in covered for s in top10)}/10")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
