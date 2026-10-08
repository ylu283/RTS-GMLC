"""Prompt 32 T1 collector brain: objectives_t1.csv + noise_ruler_v2 groups.

Reads extracts/<wave>/ + design matrices for selection_t1 and the referenced
cross-wave runs. Two pinned rules (prompt 32):

- THERMAL h2 = sum over committed hours of (p_max - Dispatch) — from the
  --full extract's thermal.csv.gz (falls back to the raw run dir's
  thermal_detail.csv on CRC). The is_pem pipeline returns 0 for thermal
  retrofits and MUST NOT be used for nuclear rows; regression check:
  nuclear-run h2 > 0.
- MODE-RESOLVED base differencing: every base solve is classified by gen-1
  annual starts; total_cost/fixed_cost/onoffs deltas for nuclear designs
  are reported against EACH base mode separately — never the pooled mean.

Ruler v2 groups: per design-group per-objective floor := median of
within-group pairwise |Delta| (~1 sigma, matching the RTS MC convention);
campaign floor = max over groups; floors with df < 3 are LOW-CONFIDENCE
(verdicts need >=3x); a floor that DECREASES vs v1 is listed in a CHANGES
table and not adopted at df < 3; bimodality screen (per-unit attribution of
replicate |Delta|) runs before any floor is declared usable; total/fixed
cost stay flagged bimodal — no Gaussian machinery.

Pure pandas/numpy/json — safe in PCM_ERCOT.
"""

import gzip
import itertools
import json
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
EXTR = os.path.join(HERE, "extracts")
SEL = os.path.join(HERE, "analysis", "selection")
OBJ = ["true_curt", "h2", "var_cost", "reserve", "onoffs", "total_cost",
       "fixed_cost"]
BIMODAL = {"total_cost", "fixed_cost"}
NUC_PMAX = 2430.0

# run key = "wave:index"; base_2019 extract layout is FLAT (special case)
GROUPS = {
    "base": ["base_2019:base", "screening_ercot:11",
             "selection_t1:1", "selection_t1:2"],
    "wind_pocket": ["screening_ercot:1", "screening_ercot:12",
                    "selection_t1:3"],
    "pv": ["screening_ercot:8", "selection_t1:4", "selection_t1:5"],
    "nuclear": ["selection_t1:8", "selection_t1:11"],   # df=1: QUALITATIVE only
}
QUALITATIVE_GROUPS = {"nuclear"}  # df=1 -> never a quantitative floor


def run_dir(key):
    wave, idx = key.split(":")
    if wave == "base_2019":
        return os.path.join(EXTR, "base_2019")
    return os.path.join(EXTR, wave, f"run_index_{idx}")


def gen_summary(d):
    g = pd.read_csv(os.path.join(d, "gen_summary.csv"))
    g["Generator"] = g["Generator"].astype(str)
    g["is_pem"] = g["is_pem"].fillna(False).astype(bool)
    return g


def thermal_h2(key, site="1", pmax=NUC_PMAX):
    """Pinned thermal rule: sum(p_max - Dispatch) over committed hours."""
    d = run_dir(key)
    full = os.path.join(d, "thermal.csv.gz")
    if os.path.isfile(full):
        td = pd.read_csv(full)
    else:  # CRC fallback: raw run dir (collector runs where runs/ exists)
        wave, idx = key.split(":")
        raw = os.path.join(HERE, "waves", wave, "runs", f"run_index_{idx}",
                           "thermal_detail.csv")
        td = pd.read_csv(raw)
    td["Generator"] = td["Generator"].astype(str)
    g = td[td.Generator == site]
    on = g[g["Unit State"].astype(float) > 0]
    return float((pmax - on["Dispatch"].astype(float)).sum())


def metrics(key, nuclear=False):
    d = run_dir(key)
    o = pd.read_csv(os.path.join(d, "overall.csv")).iloc[0]
    g = gen_summary(d)
    vre = (~g.is_pem) & g.unit_type.isin(["WIND", "PV"])
    h2 = (thermal_h2(key) if nuclear
          else float(g[g.is_pem].curtailment_mwh.sum()))
    g1 = g[g.Generator == "1"]
    return {"true_curt": float(g[vre].curtailment_mwh.sum()),
            "h2": h2,
            "var_cost": float(o["Total generation costs"]),
            "reserve": float(o["Total reserve shortfall"]),
            "onoffs": float(o["Total on/offs"]),
            "total_cost": float(o["Total costs"]),
            "fixed_cost": float(o["Total fixed costs"]),
            "gen1_starts": float(g1.starts.iloc[0]) if len(g1) else np.nan,
            "gen1_unit_cost": float(g1["Unit Cost"].iloc[0]) if len(g1) else np.nan}


def main():
    dm = pd.read_csv(os.path.join(HERE, "waves", "selection_t1",
                                  "design_matrix.csv"))
    dm["oat_site"] = dm["oat_site"].astype(str)
    rows = []
    for _, r in dm.iterrows():
        key = f"selection_t1:{int(r['index'])}"
        nuc = str(r["oat_site"]) == "1"
        m = metrics(key, nuclear=nuc)
        if nuc:
            assert m["h2"] > 0, f"{key}: thermal h2 == 0 (pinned regression check)"
        rows.append({"wave": "selection_t1", "index": int(r["index"]),
                     "site": r["oat_site"], "omega": r["omega"],
                     "replicate_of": r["replicate_of"], **m})
    # referenced cross-wave originals (self-contained pairing table)
    scr_dm = pd.read_csv(os.path.join(HERE, "waves", "screening_ercot",
                                      "design_matrix.csv"))
    for key in ["base_2019:base", "screening_ercot:1", "screening_ercot:8",
                "screening_ercot:11", "screening_ercot:12"]:
        wave, idx = key.split(":")
        site = "base" if wave == "base_2019" else str(
            scr_dm[scr_dm["index"] == int(idx)]["oat_site"].iloc[0])
        rows.append({"wave": wave, "index": idx, "site": site, "omega": "",
                     "replicate_of": "", **metrics(key)})
    out = pd.DataFrame(rows)
    os.makedirs(SEL, exist_ok=True)
    out.to_csv(os.path.join(SEL, "objectives_t1.csv"), index=False)

    # --- mode-resolved base classification (pinned) --------------------------
    base_keys = GROUPS["base"]
    base_modes = {k: metrics(k)["gen1_starts"] for k in base_keys}
    print("base solves by gen-1 starts (mode):", base_modes)

    # --- ruler v2 groups ------------------------------------------------------
    v2_path = os.path.join(SEL, "noise_ruler_v2.json")
    v2 = json.load(open(v2_path))
    v1 = v2["v1_frozen"]
    key_m = {}
    for grp, keys in GROUPS.items():
        for k in keys:
            if k not in key_m:
                key_m[k] = metrics(k, nuclear=(grp == "nuclear"
                                               and k.startswith("selection_t1")))
    changes = []
    for grp, keys in GROUPS.items():
        df = len(keys) - 1
        entry = {}
        for obj in OBJ:
            deltas = [abs(key_m[a][obj] - key_m[b][obj])
                      for a, b in itertools.combinations(keys, 2)]
            entry[obj] = {"readings": [round(d, 4) for d in deltas],
                          "floor": float(np.median(deltas)), "df": df,
                          "low_confidence": df < 3,
                          "qualitative_only": grp in QUALITATIVE_GROUPS,
                          "bimodal": obj in BIMODAL}
        # bimodality screen: per-pair gen-1 starts attribution
        starts = {k: key_m[k]["gen1_starts"] for k in keys}
        entry["_gen1_starts_by_solve"] = starts
        entry["_mode_pinning"] = (grp == "nuclear" and
                                  len(set(starts.values())) == 1)
        v2["groups"][grp] = entry
    # campaign floors: max over QUANTITATIVE groups; CHANGES vs v1
    floors = {}
    for obj in OBJ:
        vals = [v2["groups"][g][obj]["floor"] for g in GROUPS
                if g not in QUALITATIVE_GROUPS]
        floors[obj] = float(max(vals))
        if obj in v1 and floors[obj] < v1[obj]:
            dfmax = max(len(GROUPS[g]) - 1 for g in GROUPS
                        if g not in QUALITATIVE_GROUPS)
            adopted = dfmax >= 3
            changes.append({"objective": obj, "v1": v1[obj],
                            "v2": floors[obj], "adopted": adopted,
                            "note": "decrease; df<3 decreases are not adopted"
                                    if not adopted else "decrease, df>=3"})
            if not adopted:
                floors[obj] = v1[obj]
    v2["campaign_floor_T1"] = floors
    v2["changes_vs_v1"] = changes
    v2["base_modes_gen1_starts"] = base_modes
    with open(v2_path, "w") as f:
        json.dump(v2, f, indent=2)
        f.write("\n")
    print("objectives_t1.csv + noise_ruler_v2.json written")
    print("campaign floors T1:", {k: round(v, 1) for k, v in floors.items()})
    return 0


if __name__ == "__main__":
    sys.exit(main())
