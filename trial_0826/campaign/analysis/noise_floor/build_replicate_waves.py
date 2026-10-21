"""Prompt 41: build the two replicate waves (replicate_C_noise_a / _b).

Re-runs the pre-registered design selection rule (prompt 41 §2) on the
304 non-grid pooled scenario-C runs, asserts the expected picks, and
writes two 6-row waves (per design: wave A = exact + perturb-1, wave B =
exact + perturb-2). Never submits.

  cd trial_0826/campaign && python analysis/noise_floor/build_replicate_waves.py [--check]

--check re-runs selection + assertions and writes nothing.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
CAMPAIGN = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, CAMPAIGN)
import pool  # noqa: E402
import design_tools  # noqa: E402
import make_batches  # noqa: E402
import submit_array  # noqa: E402
from tiers import RHO_SCENARIOS, stage2_tiers  # noqa: E402

T = pool.SORTED_TIERS
WAVES = {"a": "replicate_C_noise_a", "b": "replicate_C_noise_b"}
EXPECTED = {"LOW": "methods_C_P2_r3:7", "MID": "methods_C_P1_r3:8",
            "HIGH": "methods_C_P1_r3:3"}
DELTA = 0.001
LO, HI = float(pool.LO), float(pool.HI)
SOURCE = "prompt 41 replicate wave; parents listed"


def candidates():
    df, missing = pool.load_pool(groups=("space_filling", "bo"))
    assert len(df) == 304, len(df)
    df["key"] = df["wave"] + ":" + df["index"].astype(str)
    df["om"] = df[[f"{t}_omega" for t in T]].round(10).astype(str).agg(",".join, axis=1)
    df["accidental"] = df.duplicated("om", keep=False)
    return df, missing


def select(df):
    picks = {}
    s = df["load_shed_mwh"]
    masks = {"LOW": s <= 3000.0, "MID": (s > 3000.0) & (s < 25000.0), "HIGH": s >= 35000.0}
    for name, m in masks.items():
        sub = df[m].copy()
        acc = sub[sub["accidental"]].sort_values(["wave", "index"])
        if len(acc):
            pick, rule = acc.iloc[0], "accidental pair, (wave, index) sort"
        else:
            med = sub["load_shed_mwh"].median()
            sub["dist"] = (sub["load_shed_mwh"] - med).abs()
            pick, rule = sub.sort_values(["dist", "wave", "index"]).iloc[0], "closest to stratum median"
            rule += f" ({int((sub['dist'] == pick['dist']).sum())}-way tie, (wave, index) sort)"
        twins = df[(df["om"] == pick["om"]) & (df["key"] != pick["key"])]["key"].tolist()
        picks[name] = {"key": pick["key"], "wave": pick["wave"], "index": int(pick["index"]),
                       "omega": {t: float(pick[f"{t}_omega"]) for t in T},
                       "shed": float(pick["load_shed_mwh"]), "rule": rule,
                       "stratum_n": int(m.sum()), "existing_twins": twins}
    for k, v in EXPECTED.items():
        assert picks[k]["key"] == v, (k, picks[k]["key"], v)
    return picks


def perturbed(omega):
    """perturb-1 / perturb-2 (prompt 41 §2): largest-omega tier, ties by
    sorted tier order; interior -> +d / -d, at 1.0 -> -d / -2d, at 0.05 ->
    +d / +2d. Never clips onto a bound."""
    vals = np.array([omega[t] for t in T])
    j = int(np.flatnonzero(vals == vals.max())[0])
    t = T[j]
    w = omega[t]
    if np.isclose(w, HI):
        steps = (-DELTA, -2 * DELTA)
    elif np.isclose(w, LO):
        steps = (+DELTA, +2 * DELTA)
    else:
        steps = (+DELTA, -DELTA)
    out = []
    for st in steps:
        o = dict(omega)
        o[t] = round(w + st, 10)
        assert LO < o[t] < HI, o[t]  # never on a bound
        assert round(o[t], 4) == o[t], ("4-decimal rounding would alter", o[t])
        out.append((t, o))
    return out


def wave_rows(picks, which):
    tiers, prov = stage2_tiers()
    rows, meta = [], []
    i = 1
    for name in ("LOW", "MID", "HIGH"):
        p = picks[name]
        (pt1, o1), (pt2, o2) = perturbed(p["omega"])
        pert_t, pert_o, label = (pt1, o1, "perturb-1") if which == "a" else (pt2, o2, "perturb-2")
        for role, om in (("exact", p["omega"]), (label, pert_o)):
            rows.append(design_tools.make_row(tiers, om, index=i, num_days=366,
                                              provisional=prov, rho_h2=RHO_SCENARIOS["C"]))
            hn = float(np.sqrt(sum(((om[t] - p["omega"][t]) / (HI - LO)) ** 2 for t in T)))
            meta.append({"index": i, "design": name, "role": role, "parent": p["key"],
                         "existing_twins": p["existing_twins"],
                         "perturbed_tier": None if role == "exact" else pert_t,
                         "omega": om, "h_to_parent": hn})
            i += 1
    return tiers, design_tools.rows_to_matrix(rows, tiers), meta


def check_exact_vs_parent(wave_dir, meta):
    """Exact copies must reproduce the parent's retrofit dict and design row."""
    for m in meta:
        if m["role"] != "exact":
            continue
        pw, pi = m["parent"].split(":")
        pdir = os.path.join(CAMPAIGN, "waves", pw)
        a = json.load(open(os.path.join(pdir, f"retrofit_gen_dict_{pi}.json")))
        b = json.load(open(os.path.join(wave_dir, f"retrofit_gen_dict_{m['index']}.json")))
        assert a == b, ("exact copy dict differs from parent", m["parent"])
        pr = pd.read_csv(os.path.join(pdir, "design_matrix.csv")).set_index("index").loc[int(pi)]
        nr = pd.read_csv(os.path.join(wave_dir, "design_matrix.csv")).set_index("index").loc[m["index"]]
        cols = [c for c in pr.index if c in nr.index]
        for c in cols:
            x, y = pr[c], nr[c]
            assert (pd.isna(x) and pd.isna(y)) or x == y, (m["parent"], c, x, y)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args(argv)
    df, missing = candidates()
    picks = select(df)
    print(json.dumps({"missing_objectives": missing, "picks": picks}, indent=1))
    for which, wave in WAVES.items():
        tiers, dm, meta = wave_rows(picks, which)
        print(wave, json.dumps(meta, indent=1))
        if args.check:
            continue
        wdir = os.path.join(CAMPAIGN, "waves", wave)
        assert not os.path.exists(wdir), f"{wdir} exists — waves are written once"
        design_tools.write_wave(dm, wdir, tiers, manifest_extra={
            "source": SOURCE, "prompt": 41, "replicate_rows": meta,
            "selection": {k: {kk: v[kk] for kk in ("key", "shed", "rule", "stratum_n")}
                          for k, v in picks.items()}})
        check_exact_vs_parent(wdir, meta)
        submit_array.generate_script(wdir, max_concurrent=None)
        cpath = os.path.join(wdir, f"collect_{wave}.sh")
        with open(cpath, "w") as f:
            f.write(make_batches._render_random_collector(wave, 6))
        os.chmod(cpath, 0o755)
        print("wrote", wdir)


if __name__ == "__main__":
    main()
