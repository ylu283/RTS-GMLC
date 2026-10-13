#!/usr/bin/env python3
"""Prompt 36 wave D: apply the pre-registered top-k rule (WAVE_D_TOPK_RULE.md,
committed 4fb3b1f before any per-site screening_v2 value was read).

Per-site rows: screening_v2/ercot 1-9 and screening_v2/topup 1-7. Excluded
from ranking: ercot 10 (__ALL__, every site at once; not a single-site row),
ercot 11 (base replicate), ercot 12 (replicate of row 1; reported only).
Δ = row true_curt - base true_curt (compute_objectives.metrics, non-PEM
WIND + PV); relief = -Δ; PEM MW = PEM_fraction * gen_pmax from the row's
retrofit dict; rank by relief per MW, largest first. Ruler = A replicate
pairwise |Δ| (t3_base_read.json).

Output: analysis/cost_fix/wave_d_selection.json (+ printed table).
"""
import json
import sys
from pathlib import Path

import pandas as pd

ERCOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ERCOT))
import compute_objectives as co  # noqa: E402

BASE = "base_2019_v2:1"
ROWS = [("ercot", i) for i in range(1, 10)] + [("topup", i) for i in range(1, 8)]
K, K_MIN = 6, 4


def row_info(sub, i):
    wave = ERCOT / "waves" / "screening_v2" / sub
    dm = pd.read_csv(wave / "design_matrix.csv").set_index("index").loc[i]
    (site, cfg), = json.loads((wave / f"retrofit_gen_dict_{i}.json").read_text()).items()
    assert str(site) == str(dm.oat_site)
    return {"row": f"{sub}:{i}", "site": str(site), "unit_type": dm.unit_type, "bus": int(dm.bus),
            "gen_pmax": float(cfg["gen_pmax"]), "pem_mw": float(cfg["PEM_fraction"] * cfg["gen_pmax"])}


def main():
    t3 = json.loads((HERE / "t3_base_read.json").read_text())
    ruler = t3["v2"]["replicates"]["pairwise"]["true_curt"]["median"]
    thr = 2 * ruler
    base = co.metrics(BASE)["true_curt"]
    recs = []
    for sub, i in ROWS:
        r = row_info(sub, i)
        m = co.metrics(f"screening_v2/{sub}:{i}")
        r["true_curt"] = m["true_curt"]
        r["delta"] = m["true_curt"] - base
        r["relief_per_mw"] = -r["delta"] / r["pem_mw"]
        r["h2"] = m["h2"]
        r["qualifies"] = abs(r["delta"]) > thr
        recs.append(r)
    recs.sort(key=lambda r: r["relief_per_mw"], reverse=True)
    for n, r in enumerate(recs, 1):
        r["rank"] = n
    qual = [r for r in recs if r["qualifies"]]
    if len(qual) >= K:
        chosen, how = qual[:K], f"k = {K}: {len(qual)} sites qualify; top {K} by rank"
    elif len(qual) >= K_MIN:
        chosen, how = qual, f"all {len(qual)} qualifying"
    else:
        chosen = qual + [r for r in recs if not r["qualifies"]][:K_MIN - len(qual)]
        how = f"{len(qual)} qualify; filled by rank to {K_MIN}"
    if ruler == 0:
        how += " (A ruler = 0: byte-identical replicates, threshold 0, rule = top 6 by rank)"

    rep = co.metrics("screening_v2/ercot:12")["true_curt"] - base
    out = {"rule": "WAVE_D_TOPK_RULE.md (4fb3b1f)", "base_true_curt": base, "a_ruler": ruler,
           "threshold": thr, "selection": how, "chosen": [r["row"] for r in chosen],
           "smallest_chosen_gen_pmax": min(r["gen_pmax"] for r in chosen),
           "replicate_check_ercot12_minus_ercot1": rep - next(r["delta"] for r in recs if r["row"] == "ercot:1"),
           "ranked": recs}
    (HERE / "wave_d_selection.json").write_text(json.dumps(out, indent=1, default=float))
    print(f"base true_curt {base:,.0f} MWh; A ruler {ruler}; threshold {thr}")
    print(f"{'rank':>4} {'row':>9} {'site':>5} {'type':>5} {'bus':>4} {'gen_pmax':>9} {'PEM MW':>7} "
          f"{'Δ true_curt MWh':>16} {'relief/MW':>10} qual chosen")
    ids = {r["row"] for r in chosen}
    for r in recs:
        print(f"{r['rank']:>4} {r['row']:>9} {r['site']:>5} {r['unit_type']:>5} {r['bus']:>4} {r['gen_pmax']:>9.1f} "
              f"{r['pem_mw']:>7.1f} {r['delta']:>16,.0f} {r['relief_per_mw']:>10.1f} "
              f"{'y' if r['qualifies'] else 'n':>4} {'*' if r['row'] in ids else ''}")
    print(how)
    print(f"smallest chosen gen_pmax = {out['smallest_chosen_gen_pmax']:.1f} MW; "
          f"ercot:12 - ercot:1 Δ = {out['replicate_check_ercot12_minus_ercot1']:,.1f} MWh")


if __name__ == "__main__":
    main()
