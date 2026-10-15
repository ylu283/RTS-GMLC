#!/usr/bin/env python
"""T0 base-case evidence for prompt 38 — all from the LOCAL no-PEM base
run (trial_0826/base_case_pcm_test). 0 Prescient runs.

Facts this script establishes:
  * where Prescient books load shed (reference bus vs load buses);
  * RT vs DA prices on the base shed hours (was the day-ahead short?);
  * available headroom on shed hours (hourly_gen_summary.csv);
  * the base-case event whose fractional MWh matches 22.425956.
Writes t0_base_evidence.txt in this directory.
"""
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
BASE = HERE.parents[2] / "base_case_pcm_test"
Q2_FRAC = 22.425956

out = []


def say(*parts):
    line = " ".join(str(p) for p in parts)
    out.append(line)
    print(line)


def main() -> None:
    h = pd.read_csv(BASE / "hourly_summary.csv")
    g = pd.read_csv(BASE / "hourly_gen_summary.csv")
    b = pd.read_csv(BASE / "bus_detail.csv")

    shed = h[h["LoadShedding"] > 0].copy()
    say(f"base shed hours: {len(shed)}, total {shed['LoadShedding'].sum():.3f} MWh")

    # 1. where is shed booked?
    bs = b[b["Shortfall"] > 0]
    per_bus = bs.groupby("Bus")["Shortfall"].sum()
    say("shed by bus:", per_bus.to_dict())
    arne = b[b["Bus"] == "Arne"]
    a_sh = arne[arne["Shortfall"] > 0]
    over = (a_sh["Shortfall"] > a_sh["Demand"]).mean()
    say(f"share of Arne shed hours where Shortfall > local Demand: {over:.2f} "
        f"(max shed {a_sh['Shortfall'].max():.1f} MW vs max Arne demand "
        f"{a_sh['Demand'].max():.1f} MW) -> slack-bus accounting, not local")

    # 2. RT vs DA price on shed hours
    say(f"RT LMP at Arne on shed hours: unique = {sorted(a_sh['LMP'].unique())}")
    say(f"DA LMP on shed hours: median {a_sh['LMP DA'].median():.2f}, "
        f"share < 40 (=B): {(a_sh['LMP DA'] < 40).mean():.2f}, "
        f"share == 0: {(a_sh['LMP DA'] == 0).mean():.2f}")

    # 3. headroom on shed hours
    gg = g.rename(columns={"Load shedding": "shed",
                           "Available headroom": "headroom"})
    sh_g = gg[gg["shed"] > 0]
    say(f"available headroom on shed hours: max {sh_g['headroom'].max():.1f}, "
        f"median {sh_g['headroom'].median():.1f} (MW)")
    say(f"available headroom on NON-shed hours: median "
        f"{gg[gg['shed'] == 0]['headroom'].median():.1f} MW")

    # 4. the 22.425956 fractional match
    frac = Q2_FRAC % 1
    cand = shed[((shed["LoadShedding"] % 1) - frac).abs() < 1e-6]
    say("\nbase hours whose shed has the same fractional part as 22.425956:")
    say(cand[["Date", "Hour", "LoadShedding", "ReserveShortfall",
              "Price", "Demand"]].to_string(index=False))
    for _, r in cand.iterrows():
        say(f"  {r['Date']} h{int(r['Hour'])}: {r['LoadShedding']:.6f} "
            f"- 22.425956 = {r['LoadShedding'] - Q2_FRAC:.6f} MWh")

    # 5. base reserve shortfall co-occurrence
    say(f"\nshed hours that also have reserve shortfall: "
        f"{(shed['ReserveShortfall'] > 0).mean():.2f} of shed hours")

    (HERE / "t0_base_evidence.txt").write_text("\n".join(out) + "\n")


if __name__ == "__main__":
    main()
