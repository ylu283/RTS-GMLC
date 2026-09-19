#!/usr/bin/env python3
"""Draft the ERCOT screening wave (prompt 26 T4). ~12 OAT runs at B = 40
(matches RTS Stage-2 C), sites seeded from a curtailment PROXY, plus the
2 replicate rows that establish the TL=120 solver-noise ruler.

PROXY NOTE (deviation from the prompt's de-risk plan, reported to Kay):
the existing GTEP full-year results were checked and their per-unit
Curtailment column is identically 0.0 for all 129 renewables over all
8,760 h (and that fleet contains 2035 investment units like 'pv_101-c'
absent from ercot123_2019) — no curtailment ranking can be extracted from
them. Seed used instead: annual AVAILABLE energy per unit from the
vendored 2019 profiles (deterministic; written to
availability_ranking_2019.csv). The ranking MUST be confirmed against the
actual base-case extract before the wave is submitted (block #4 does
this); rows are marked provisional until then.

Replicate rows (BLOCKER fix): index 11 re-runs the exact base config,
index 12 duplicates screening index 1. Under TimeLimit=120 the returned
incumbent is machine-load-dependent; the replicate spread IS the noise
model. Gate rule: any screening-delta claim requires |delta| >> replicate
spread; deltas inside the spread are "within solver noise", never effects.

Site slate (top available-energy, de-duplicated to spread buses, with two
deliberate probes):
  wind 275 (bus 120), 205 (77), 20 (32), 274 (120 — same-bus stacking
  probe), 204 (28), 91 (94), 206 (22 — largest unit 1.8 GW, CF 0.17),
  PV 30 (26), PV 142 (14), plus __ALL__ (all nine together).
omega = 0.5 wind / 0.4 PV, bid = 40.0 (RTS screening convention).
"""
import csv
import json
from pathlib import Path

import pandas as pd

ERCOT_DIR = Path(__file__).resolve().parent
DATA_DIR = ERCOT_DIR / "data" / "ercot123_2019"
WAVE_DIR = ERCOT_DIR / "waves" / "screening_ercot"

BID = 40.0
OMEGA = {"WIND": 0.5, "PV": 0.4}
START_DATE, NUM_DAYS = "01-01-2019", 365
WIND_SITES = ["275", "205", "20", "274", "204", "91", "206"]
PV_SITES = ["30", "142"]


def availability_ranking():
    gen = pd.read_csv(DATA_DIR / "gen.csv")
    pmax = dict(zip(gen["GEN UID"].astype(str), gen["PMax MW"]))
    bus = dict(zip(gen["GEN UID"].astype(str), gen["Bus ID"]))
    rows = []
    for f, t in [("DAY_AHEAD_wind.csv", "WIND"), ("DAY_AHEAD_solar.csv", "PV")]:
        df = pd.read_csv(DATA_DIR / f)
        df = df[df.Year == 2019]  # exclude the lookahead padding rows
        for c in df.columns[4:]:
            avail = df[c].sum()
            rows.append({"gen": c, "unit_type": t, "bus": bus[c],
                         "pmax_mw": pmax[c], "avail_gwh": avail / 1e3,
                         "cf": avail / (8760 * pmax[c])})
    return (pd.DataFrame(rows)
            .sort_values("avail_gwh", ascending=False).reset_index(drop=True))


def main():
    WAVE_DIR.mkdir(parents=True, exist_ok=True)
    rank = availability_ranking()
    rank.to_csv(WAVE_DIR / "availability_ranking_2019.csv", index=False)
    info = rank.set_index("gen")

    def retrofit(sites):
        return {s: {"PEM_bid": BID,
                    "PEM_fraction": OMEGA[info.loc[s, "unit_type"]],
                    "gen_pmax": float(info.loc[s, "pmax_mw"])}
                for s in sites}

    rows, dicts = [], {}
    oat = WIND_SITES + PV_SITES
    for i, s in enumerate(oat, start=1):
        rows.append([i, s, info.loc[s, "unit_type"], info.loc[s, "bus"],
                     OMEGA[info.loc[s, "unit_type"]], BID,
                     float(info.loc[s, "pmax_mw"]), START_DATE, NUM_DAYS, ""])
        dicts[i] = retrofit([s])
    i = len(oat) + 1
    rows.append([i, "__ALL__", "", "", "", BID, "", START_DATE, NUM_DAYS, ""])
    dicts[i] = retrofit(oat)
    i += 1
    rows.append([i, "__BASE_REPLICATE__", "", "", "", "", "", START_DATE,
                 NUM_DAYS, "base"])
    dicts[i] = {}
    i += 1
    rows.append([i, oat[0], info.loc[oat[0], "unit_type"],
                 info.loc[oat[0], "bus"], OMEGA[info.loc[oat[0], "unit_type"]],
                 BID, float(info.loc[oat[0], "pmax_mw"]), START_DATE,
                 NUM_DAYS, "1"])
    dicts[i] = retrofit([oat[0]])

    with open(WAVE_DIR / "design_matrix.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["index", "oat_site", "unit_type", "bus", "omega", "bid",
                    "gen_pmax", "start_date", "num_days", "replicate_of"])
        w.writerows(rows)
    for idx, d in dicts.items():
        with open(WAVE_DIR / f"retrofit_gen_dict_{idx}.json", "w") as f:
            json.dump(d, f, indent=2, sort_keys=True)
            f.write("\n")
    print(f"{WAVE_DIR.name}: {len(rows)} rows "
          f"({len(oat)} OAT + __ALL__ + 2 replicates)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
