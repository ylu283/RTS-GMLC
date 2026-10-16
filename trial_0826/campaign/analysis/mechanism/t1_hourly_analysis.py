#!/usr/bin/env python
"""T1 hourly mechanism analysis for prompt 38.

Inputs: the 15 fetched run dirs under runs/ (gitignored) and the local
no-PEM base case. Outputs: t1_summary.txt, t1_h1_table.csv,
t1_decomposition.csv, t1_q2_events.csv. 0 Prescient runs; <= 4 threads.

Tests:
  H1  committed thermal capacity / online headroom on shed hours,
      LOW vs HIGH designs.
  H2  _PEM real-time dispatch on those hours; supply-difference
      decomposition quantifies the H1 vs H2 shares.
  H4  reserve shortfall on the same hours (closure).
  Q2  per-design shed events; the 2020-12-18 h7 residual and the
      962 MW decomposition vs the base case.
"""
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
RUNS = HERE / "runs"
TRIAL = HERE.parents[2]
BASE = TRIAL / "base_case_pcm_test"
GEN_CSV = TRIAL.parent / "RTS_Data" / "SourceData" / "gen.csv"

_g = pd.read_csv(GEN_CSV, usecols=["GEN UID", "PMax MW"])
PMAX = dict(zip(_g["GEN UID"], _g["PMax MW"]))

LOW = [("bo_C_r2", 3), ("random_C", 42)]
MID = [("stage2_C_n0", 16), ("random_C", 30)]
HIGH = [("bo_C_r1", 5), ("bo_C_r2", 2)]
Q2_SET = [("stage2_C_n0", 1), ("stage2_C_n0", 6), ("stage2_C_n0b", 6),
          ("bo_C_r2", 7), ("random_C", 5), ("random_C", 14),
          ("random_C", 15)]
Q2_CONTRAST = [("random_C", 39), ("bo_C_r1", 4)]
Q2_VALUE = 22.425956

out = []


def say(*parts):
    line = " ".join(str(p) for p in parts)
    out.append(line)
    print(line)


def rdir(wave, idx):
    return RUNS / wave / f"run_index_{idx}"


def name(wave, idx):
    return f"{wave}#{idx}"


def load_hourly(d):
    h = pd.read_csv(d / "hourly_summary.csv")
    h["key"] = h["Date"] + ":" + h["Hour"].astype(str)
    return h.set_index("key")


def thermal_at(d, keys):
    """Per-hour committed capacity, committed count, dispatch, headroom
    for the given Date:Hour keys."""
    t = pd.read_csv(d / "thermal_detail.csv",
                    usecols=["Date", "Hour", "Generator", "Dispatch",
                             "Dispatch DA", "Headroom", "Unit State"])
    t["key"] = t["Date"] + ":" + t["Hour"].astype(str)
    t = t[t["key"].isin(keys)]
    st = t["Unit State"]
    if st.dtype != bool:
        st = st.astype(str).str.strip().str.lower().map(
            {"true": True, "false": False, "1": True, "0": False})
        assert not st.isna().any(), "Unit State parse failure"
    t = t.assign(on=st, pmax=t["Generator"].map(PMAX))
    assert not t["pmax"].isna().any(), "missing PMax for a thermal unit"
    g = t.groupby("key").apply(
        lambda x: pd.Series({
            "committed_mw": (x["on"] * x["pmax"]).sum(),
            "committed_units": int(x["on"].sum()),
            "thermal_dispatch": x["Dispatch"].sum(),
            "thermal_dispatch_da": x["Dispatch DA"].sum(),
            "headroom": x["Headroom"].sum(),
        }), include_groups=False)
    return g


def renew_at(d, keys):
    """Per-hour renewable output split into _PEM and parent/other."""
    r = pd.read_csv(d / "renewables_detail.csv",
                    usecols=["Date", "Hour", "Generator", "Output",
                             "Output DA", "Curtailment"])
    r["key"] = r["Date"] + ":" + r["Hour"].astype(str)
    r = r[r["key"].isin(keys)]
    r["is_pem"] = r["Generator"].str.endswith("_PEM")
    g = r.groupby(["key", "is_pem"])["Output"].sum().unstack(fill_value=0.0)
    g = g.rename(columns={False: "ren_other", True: "pem_output"})
    if "pem_output" not in g.columns:
        g["pem_output"] = 0.0
    da = r.groupby("key")["Output DA"].sum().rename("ren_da")
    return g.join(da)


def main() -> None:
    # ------------------------------------------------------------------
    # Q2 — shed events per design
    # ------------------------------------------------------------------
    say("=" * 70)
    say("Q2 — shed events in each fetched run")
    q2_rows = []
    for wave, idx in Q2_SET + Q2_CONTRAST + LOW + MID + HIGH:
        h = load_hourly(rdir(wave, idx))
        sh = h[h["LoadShedding"] > 0]
        q2_rows.append({
            "run": name(wave, idx),
            "shed_hours": len(sh),
            "total_shed_mwh": sh["LoadShedding"].sum(),
            "events": "; ".join(f"{r['Date']} h{int(r['Hour'])}:"
                                f"{r['LoadShedding']:.6f}"
                                for _, r in sh.head(8).iterrows())
                      + (" ..." if len(sh) > 8 else ""),
        })
    q2df = pd.DataFrame(q2_rows)
    q2df.to_csv(HERE / "t1_q2_events.csv", index=False)
    say(q2df.to_string(index=False, max_colwidth=90))

    # confirm the 22.426 designs share the identical single event
    say("\nQ2 identity check (expect one event, 2020-12-18 h7, "
        f"{Q2_VALUE} MWh, at the slack bus):")
    for wave, idx in Q2_SET:
        h = load_hourly(rdir(wave, idx))
        sh = h[h["LoadShedding"] > 0]
        b = pd.read_csv(rdir(wave, idx) / "bus_detail.csv",
                        usecols=["Date", "Hour", "Bus", "Shortfall"])
        bs = b[b["Shortfall"] > 0]
        buses = sorted(bs["Bus"].unique())
        ok = (len(sh) == 1
              and sh.iloc[0]["Date"] == "2020-12-18"
              and int(sh.iloc[0]["Hour"]) == 7
              and abs(sh.iloc[0]["LoadShedding"] - Q2_VALUE) < 1e-6)
        say(f"  {name(wave, idx)}: events={len(sh)}, "
            f"first={sh.iloc[0]['Date']} h{int(sh.iloc[0]['Hour'])} "
            f"{sh.iloc[0]['LoadShedding']:.6f} MWh, buses={buses} "
            f"-> {'CONFIRMED' if ok else 'MISMATCH'}")

    # ------------------------------------------------------------------
    # Q2 — 962 MW decomposition at 2020-12-18 h7 (base vs one Q2 run)
    # ------------------------------------------------------------------
    key = {"2020-12-18:7"}
    say("\nQ2 — supply decomposition at 2020-12-18 h7 (vs no-PEM base):")
    tb = thermal_at(BASE, key)
    rb = renew_at(BASE, key)
    hb = load_hourly(BASE).loc["2020-12-18:7"]
    say(f"  base: shed={hb['LoadShedding']:.6f}, demand={hb['Demand']:.1f}, "
        f"committed={tb.iloc[0]['committed_mw']:.0f} MW "
        f"({tb.iloc[0]['committed_units']:.0f} units), "
        f"thermal disp={tb.iloc[0]['thermal_dispatch']:.1f}, "
        f"headroom={tb.iloc[0]['headroom']:.1f}, "
        f"renewables={rb.iloc[0]['ren_other']:.1f}")
    dec_rows = []
    for wave, idx in Q2_SET:
        t = thermal_at(rdir(wave, idx), key)
        r = renew_at(rdir(wave, idx), key)
        h = load_hourly(rdir(wave, idx)).loc["2020-12-18:7"]
        d_th = t.iloc[0]["thermal_dispatch"] - tb.iloc[0]["thermal_dispatch"]
        d_rp = r.iloc[0]["ren_other"] - rb.iloc[0]["ren_other"]
        d_pem = r.iloc[0]["pem_output"]
        d_shed = hb["LoadShedding"] - h["LoadShedding"]
        dec_rows.append({
            "run": name(wave, idx),
            "shed_mwh": h["LoadShedding"],
            "d_shed_vs_base": d_shed,
            "d_thermal_dispatch": d_th,
            "d_committed_mw": t.iloc[0]["committed_mw"] - tb.iloc[0]["committed_mw"],
            "d_committed_units": t.iloc[0]["committed_units"] - tb.iloc[0]["committed_units"],
            "d_parent_renewables": d_rp,
            "pem_output": d_pem,
            "residual": d_shed - (d_th + d_rp + d_pem),
        })
        say(f"  {name(wave, idx)}: Δshed={d_shed:.3f} = Δthermal {d_th:+.1f} "
            f"+ Δparent-renew {d_rp:+.1f} + PEM {d_pem:+.1f} "
            f"(resid {d_shed - (d_th + d_rp + d_pem):+.3f}); "
            f"Δcommitted {t.iloc[0]['committed_mw'] - tb.iloc[0]['committed_mw']:+.0f} MW "
            f"/ {t.iloc[0]['committed_units'] - tb.iloc[0]['committed_units']:+.0f} units")
    pd.DataFrame(dec_rows).to_csv(HERE / "t1_q2_decomposition.csv", index=False)

    # ------------------------------------------------------------------
    # H1 / H2 / H4 — LOW shed hours vs the same hours in HIGH designs
    # ------------------------------------------------------------------
    say("\n" + "=" * 70)
    say("H1/H2/H4 — LOW-design shed hours vs same hours in HIGH designs")
    h1_rows, dec_all = [], []
    for lw, li in LOW:
        hl = load_hourly(rdir(lw, li))
        shed_keys = set(hl[hl["LoadShedding"] > 0].index)
        say(f"\nLOW {name(lw, li)}: {len(shed_keys)} shed hours, "
            f"{hl['LoadShedding'].sum():.0f} MWh total")
        tl = thermal_at(rdir(lw, li), shed_keys)
        rl = renew_at(rdir(lw, li), shed_keys)
        for hw, hi in HIGH + MID:
            hh = load_hourly(rdir(hw, hi))
            th = thermal_at(rdir(hw, hi), shed_keys)
            rh = renew_at(rdir(hw, hi), shed_keys)
            j = (tl.add_prefix("L_").join(th.add_prefix("H_"))
                 .join(rl.add_prefix("L_")).join(rh.add_prefix("H_")))
            j["L_shed"] = hl.loc[list(shed_keys), "LoadShedding"]
            j["H_shed"] = hh["LoadShedding"].reindex(j.index).fillna(0.0)
            j["L_resshort"] = hl.loc[list(shed_keys), "ReserveShortfall"]
            j["H_resshort"] = hh["ReserveShortfall"].reindex(j.index).fillna(0.0)
            d_shed = (j["L_shed"] - j["H_shed"])
            d_th = (j["H_thermal_dispatch"] - j["L_thermal_dispatch"])
            d_rp = (j["H_ren_other"] - j["L_ren_other"])
            d_pem = (j["H_pem_output"] - j["L_pem_output"])
            resid = d_shed - (d_th + d_rp + d_pem)
            h1_rows.append({
                "low": name(lw, li), "high": name(hw, hi),
                "hours": len(j),
                "L_shed_mwh": j["L_shed"].sum(),
                "H_shed_mwh": j["H_shed"].sum(),
                "L_committed_mw_mean": j["L_committed_mw"].mean(),
                "H_committed_mw_mean": j["H_committed_mw"].mean(),
                "d_committed_mw_mean": (j["H_committed_mw"] - j["L_committed_mw"]).mean(),
                "L_units_mean": j["L_committed_units"].mean(),
                "H_units_mean": j["H_committed_units"].mean(),
                "L_headroom_mean": j["L_headroom"].mean(),
                "H_headroom_mean": j["H_headroom"].mean(),
                "d_thermal_sum": d_th.sum(),
                "d_parent_ren_sum": d_rp.sum(),
                "d_pem_sum": d_pem.sum(),
                "d_shed_sum": d_shed.sum(),
                "residual_sum": resid.sum(),
                "share_thermal": d_th.sum() / d_shed.sum(),
                "share_parent_ren": d_rp.sum() / d_shed.sum(),
                "share_pem": d_pem.sum() / d_shed.sum(),
                "L_resshort_mwh": j["L_resshort"].sum(),
                "H_resshort_mwh": j["H_resshort"].sum(),
            })
            r = h1_rows[-1]
            say(f"  vs {name(hw, hi)}: Δshed {r['d_shed_sum']:.0f} MWh over "
                f"{r['hours']} h | committed {r['L_committed_mw_mean']:.0f} -> "
                f"{r['H_committed_mw_mean']:.0f} MW "
                f"({r['d_committed_mw_mean']:+.0f}); units "
                f"{r['L_units_mean']:.1f} -> {r['H_units_mean']:.1f}; "
                f"headroom {r['L_headroom_mean']:.0f} -> "
                f"{r['H_headroom_mean']:.0f} MW | shares: thermal "
                f"{r['share_thermal']:+.2f}, parent-ren "
                f"{r['share_parent_ren']:+.2f}, PEM {r['share_pem']:+.2f} "
                f"(resid {r['residual_sum']:+.0f}) | res.short "
                f"{r['L_resshort_mwh']:.0f} -> {r['H_resshort_mwh']:.0f} MWh")
    pd.DataFrame(h1_rows).to_csv(HERE / "t1_h1_table.csv", index=False)

    (HERE / "t1_summary.txt").write_text("\n".join(out) + "\n")
    say("\nwrote t1_summary.txt, t1_q2_events.csv, t1_q2_decomposition.csv, "
        "t1_h1_table.csv")


if __name__ == "__main__":
    main()
