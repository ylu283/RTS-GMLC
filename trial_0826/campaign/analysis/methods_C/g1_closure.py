#!/usr/bin/env python3
"""Prompt 35 G1 — curtailment closure on existing runs.

For every retrofitted renewable site s and every hour:
    available(s) = dispatched (s Output + s_PEM Output)
                 + parent curtailment (s Curtailment)
                 + PEM withheld (s_PEM Curtailment)
must equal the site's availability in the un-retrofitted base case
(base Output + base Curtailment of s), to 1e-6 relative (1e-6 MW absolute
for near-zero hours). Also checks:
  - the split (multi_pem/parameters.py): PEM block = min(cap, avail),
    parent block = max(avail - cap, 0), cap = PEM_fraction * gen_pmax;
  - every NON-retrofitted renewable is unchanged vs the base case;
  - summarize_wave's true curtailment = sum of non-*_PEM Curtailment, and it
    equals the wave's objectives.csv row (the PEM column is excluded).

Usage:
    python g1_closure.py --base <base_run_dir> --wave <wave_dir> --index 3 [--index 17 ...]
Exit 0 = PASS for every run; 1 = FAIL (details printed).
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REL, ABS = 1e-6, 1e-6
KEYS = ["Date", "Hour", "Minute"]


def _avail(rd):
    rd = rd.assign(avail=rd["Output"] + rd["Curtailment"])
    return rd.pivot_table(index=KEYS, columns="Generator", values="avail", aggfunc="sum")


def _close(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    err = np.abs(a - b)
    ok = err <= np.maximum(ABS, REL * np.abs(b))
    return bool(ok.all()), float(err.max()) if err.size else 0.0


def check_run(base_rd, run_dir, retrofit, objectives_row=None):
    rd = pd.read_csv(run_dir / "renewables_detail.csv",
                     usecols=KEYS + ["Generator", "Output", "Curtailment"])
    A_base, A_run = _avail(base_rd), _avail(rd)
    common = A_base.index.intersection(A_run.index)
    assert len(common) == len(A_run.index), "run hours missing from the base case"
    A_base, A_run = A_base.loc[common], A_run.loc[common]
    out, ok_all = [], True
    renew = [s for s in retrofit if f"{s}_PEM" in A_run.columns]
    for s in renew:
        cap = retrofit[s]["PEM_fraction"] * retrofit[s]["gen_pmax"]
        site = A_run[s].fillna(0) + A_run[f"{s}_PEM"].fillna(0)
        ok1, e1 = _close(site, A_base[s])
        ok2, e2 = _close(A_run[f"{s}_PEM"], np.minimum(cap, A_base[s]))
        ok3, e3 = _close(A_run[s].fillna(0), np.maximum(A_base[s] - cap, 0.0))
        out.append({"site": s, "cap_mw": cap, "hours": len(common),
                    "closure_ok": ok1, "closure_max_err": e1,
                    "pem_split_ok": ok2, "pem_max_err": e2,
                    "parent_split_ok": ok3, "parent_max_err": e3,
                    "pem_withheld_mwh": float(rd.loc[rd.Generator == f"{s}_PEM", "Curtailment"].sum()),
                    "parent_curt_mwh": float(rd.loc[rd.Generator == s, "Curtailment"].sum())})
        ok_all &= ok1 and ok2 and ok3
    others = [g for g in A_base.columns if g in A_run.columns and g not in renew
              and not g.endswith("_PEM")]
    ok4, e4 = _close(A_run[others].fillna(0), A_base[others].fillna(0))
    ok_all &= ok4
    is_pem = rd["Generator"].str.endswith("_PEM")
    true_curt = float(rd.loc[~is_pem, "Curtailment"].sum())
    res = {"run": run_dir.name, "sites": out, "others_unchanged_ok": ok4,
           "others_max_err": e4, "true_curtailment_mwh": true_curt,
           "pem_curtailment_excluded_mwh": float(rd.loc[is_pem, "Curtailment"].sum())}
    if objectives_row is not None:
        ok5, e5 = _close([true_curt], [objectives_row["true_curtailment_mwh"]])
        res.update(objectives_match=ok5, objectives_err=e5)
        ok_all &= ok5
    res["PASS"] = bool(ok_all)
    return res


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True, type=Path)
    ap.add_argument("--wave", required=True, type=Path)
    ap.add_argument("--index", type=int, action="append", required=True)
    ap.add_argument("--runs-subdir", default="runs")
    a = ap.parse_args(argv)
    base_rd = pd.read_csv(a.base / "renewables_detail.csv",
                          usecols=KEYS + ["Generator", "Output", "Curtailment"])
    obj_path = a.wave / "objectives.csv"
    obj = pd.read_csv(obj_path).set_index("index") if obj_path.exists() else None
    allok = True
    for i in a.index:
        retro = json.load(open(a.wave / f"retrofit_gen_dict_{i}.json"))
        res = check_run(base_rd, a.wave / a.runs_subdir / f"run_index_{i}", retro,
                        None if obj is None else obj.loc[i])
        allok &= res["PASS"]
        print(json.dumps(res, indent=1, default=float))
    print("G1", "PASS" if allok else "FAIL")
    return 0 if allok else 1


if __name__ == "__main__":
    sys.exit(main())
