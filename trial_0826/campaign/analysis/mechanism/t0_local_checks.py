#!/usr/bin/env python
"""T0 local checks for prompt 38 (mechanism): run selection + all evidence
available from git summaries, before any CRC rsync.

Reads only wave summaries (objectives.csv, design_matrix.csv,
site_detail.csv) of the five finished waves and the local no-PEM base
case. Writes run_selection.csv and t0_summary.txt in this directory.
0 Prescient runs. <= 4 threads.
"""
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

HERE = Path(__file__).resolve().parent
CAMPAIGN = HERE.parents[1]
WAVES = CAMPAIGN / "waves"
BASE = CAMPAIGN.parent / "base_case_pcm_test"

FINISHED = ["stage2_C_n0", "stage2_C_n0b", "bo_C_r1", "bo_C_r2", "random_C"]
Q2_VALUE = 22.425956  # recurring shed value, MWh
Q2_TOL = 1e-3


def load_wave(name: str) -> pd.DataFrame:
    obj = pd.read_csv(WAVES / name / "objectives.csv")
    dm = pd.read_csv(WAVES / name / "design_matrix.csv")
    site = pd.read_csv(WAVES / name / "site_detail.csv")
    cap = site.groupby("index")["pem_capacity_mw"].sum().rename("total_pem_mw")
    cap_ren = (
        site[site["kind"] == "renewable"]
        .groupby("index")["pem_capacity_mw"].sum()
        .rename("renewable_pem_mw")
    )
    sales = (
        site.groupby("index")["pem_grid_sales_mwh"].sum(min_count=1)
        .rename("pem_grid_sales_mwh")
    )
    df = obj.merge(dm[[c for c in dm.columns if c.endswith("_omega") or c == "index"]],
                   on="index")
    df = df.merge(cap, on="index").merge(cap_ren, on="index").merge(sales, on="index")
    df.insert(0, "wave", name)
    return df


def main() -> None:
    df = pd.concat([load_wave(w) for w in FINISHED], ignore_index=True)
    out = []

    def say(*parts):
        line = " ".join(str(p) for p in parts)
        out.append(line)
        print(line)

    say(f"designs loaded: {len(df)} from {FINISHED}")

    # --- headline correlations (Q1 context, H4, H2-proxy) ---------------
    for col in ["load_shed_mwh", "reserve_shortfall_mwh", "true_curtailment_mwh",
                "thermal_starts", "pem_grid_sales_mwh"]:
        rho, p = spearmanr(df["total_pem_mw"], df[col])
        say(f"Spearman(total_pem_mw, {col}) = {rho:+.4f} (p={p:.2e})")
    rho, p = spearmanr(df["load_shed_mwh"], df["reserve_shortfall_mwh"])
    say(f"Spearman(load_shed_mwh, reserve_shortfall_mwh) = {rho:+.4f} (p={p:.2e})")
    rho, p = spearmanr(df["renewable_pem_mw"], df["load_shed_mwh"])
    say(f"Spearman(renewable_pem_mw, load_shed_mwh) = {rho:+.4f} (p={p:.2e})")

    # H4 sanity: base reserve shortfall vs design range
    say(f"reserve_shortfall_mwh range over designs: "
        f"{df['reserve_shortfall_mwh'].min():.1f} .. {df['reserve_shortfall_mwh'].max():.1f} "
        f"(base case: 203681.4)")
    say(f"load_shed_mwh range over designs: "
        f"{df['load_shed_mwh'].min():.3f} .. {df['load_shed_mwh'].max():.1f} "
        f"(base case: 41500.115)")

    # nuclear omega >= 0.05 in every design (u == 1 band always present)
    say(f"nuclear_omega min = {df['nuclear_omega'].min():.4f} "
        f"(>= 0.05 means the u==1 nuclear band is in every design)")

    # --- Q2 set ----------------------------------------------------------
    q2 = df[(df["load_shed_mwh"] - Q2_VALUE).abs() < Q2_TOL]
    say(f"\nQ2: designs with load_shed within {Q2_TOL} of {Q2_VALUE}: {len(q2)}")
    cols = ["wave", "index", "load_shed_mwh", "total_pem_mw", "renewable_pem_mw",
            "reserve_shortfall_mwh", "nuclear_omega", "wind_303_omega",
            "wind_317_omega", "wind_122_omega", "pv_omega", "tail_omega"]
    say(q2[cols].to_string(index=False))

    # nearby small-shed designs (different small value), for the Q2 contrast
    small = df[(df["load_shed_mwh"] > 0)
               & (df["load_shed_mwh"] < 500)
               & ((df["load_shed_mwh"] - Q2_VALUE).abs() >= Q2_TOL)]
    small = small.sort_values("load_shed_mwh")
    say(f"\nQ2 contrast candidates (0 < shed < 500, != 22.426): {len(small)}")
    say(small[cols].to_string(index=False))

    zero = df[df["load_shed_mwh"] == 0]
    say(f"\nexact-zero shed designs: {len(zero)}")

    # --- Q1 contrast set --------------------------------------------------
    d = df.sort_values("total_pem_mw")
    say("\nQ1: total_pem_mw vs shed, extremes:")
    say(d[["wave", "index", "total_pem_mw", "load_shed_mwh",
           "reserve_shortfall_mwh", "pem_grid_sales_mwh"]]
        .head(6).to_string(index=False))
    say("...")
    say(d[["wave", "index", "total_pem_mw", "load_shed_mwh",
           "reserve_shortfall_mwh", "pem_grid_sales_mwh"]]
        .tail(6).to_string(index=False))

    # fixed picks per spec: r2#3 (LOW), r1#5 (HIGH); fill the rest
    picks = []

    def pick(wave, index, role):
        row = df[(df["wave"] == wave) & (df["index"] == index)]
        assert len(row) == 1, (wave, index)
        picks.append((wave, index, role))

    pick("bo_C_r2", 3, "Q1 LOW (spec)")
    pick("bo_C_r1", 5, "Q1 HIGH (spec)")

    # LOW: next lowest total MW not already picked
    taken = {(w, i) for w, i, _ in picks}
    for _, r in d.iterrows():
        key = (r["wave"], int(r["index"]))
        if key not in taken:
            pick(*key, "Q1 LOW")
            taken.add(key)
            break
    # MID: two designs nearest the median total MW
    med = d["total_pem_mw"].median()
    d2 = d.assign(dist=(d["total_pem_mw"] - med).abs()).sort_values("dist")
    n_mid = 0
    for _, r in d2.iterrows():
        key = (r["wave"], int(r["index"]))
        if key not in taken:
            pick(*key, "Q1 MID")
            taken.add(key)
            n_mid += 1
            if n_mid == 2:
                break
    # HIGH: highest total MW not already picked
    for _, r in d.iloc[::-1].iterrows():
        key = (r["wave"], int(r["index"]))
        if key not in taken:
            pick(*key, "Q1 HIGH")
            taken.add(key)
            break

    # Q2 fetch set: all 22.426 designs + 2 different-small-shed designs
    for _, r in q2.iterrows():
        key = (r["wave"], int(r["index"]))
        if key not in taken:
            picks.append((*key, "Q2 22.426"))
            taken.add(key)
        else:
            picks.append((*key, "Q2 22.426 (also Q1)"))
    for _, r in small.head(2).iterrows():
        key = (r["wave"], int(r["index"]))
        if key not in taken:
            picks.append((*key, "Q2 contrast"))
            taken.add(key)

    sel = pd.DataFrame(picks, columns=["wave", "index", "role"])
    sel = sel.merge(
        df[["wave", "index", "total_pem_mw", "load_shed_mwh",
            "reserve_shortfall_mwh"]],
        on=["wave", "index"])
    sel.to_csv(HERE / "run_selection.csv", index=False)
    say(f"\nselected runs ({len(sel)} rows, "
        f"{sel[['wave','index']].drop_duplicates().shape[0]} unique run dirs):")
    say(sel.to_string(index=False))

    (HERE / "t0_summary.txt").write_text("\n".join(out) + "\n")


if __name__ == "__main__":
    main()
