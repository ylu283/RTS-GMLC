#!/usr/bin/env python3
"""MODEL-LEVEL verification of the regenerated ERCOT metadata (prompt 26
T1.2). CSV-vs-CSV checks are not enough: the egret rts-gmlc parser silently
`continue`s + `dropna`s pointer rows whose Object doesn't match a skeleton
element — a typo'd or str/int-mangled Object produces NO error, just a
renewable frozen at scalar p_max or a bus at static load. So this script
parses the data dir exactly the way Prescient's GmlcDataProvider does and
asserts on the RESULTING models:

  - parse_to_cache over the provider's actual full-year window
    (2019-01-01 .. 2020-01-01 12:00 = 365 d + (ruc_horizon-24) h,
    honor_lookahead=False) — proves the year-end padding covers the final
    RUC's lookahead tail;
  - all 123 areas carry time-series MW Load of the expected hourly length
    (8772 = 8760 + 12) in BOTH simulation types;
  - a DA and an RT model are generated; all 154 wind+solar p_max are
    time-series dicts of the requested length in BOTH; exactly the 10
    HYDRO p_max remain scalar (documented decision); all 123 bus loads
    are time-series.

Needs an env with gridx-prescient 2.2.3 (local: ~/venvs/ercot223; CRC:
PCM_ERCOT). Exit 0 + "VERIFY PASS" on success.
"""
import sys
from datetime import datetime, timedelta
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent / "data" / "ercot123_2019"

RUC_HORIZON = 36          # CONFIG_ERCOT.md settled row
EXPECTED_HOURS = 8760 + (RUC_HORIZON - 24)


def main():
    from egret.parsers.rts_gmlc.parser import parse_to_cache

    start = datetime(2019, 1, 1, 0)
    end = datetime(2020, 1, 1, RUC_HORIZON - 24)  # provider's _end_time
    cache = parse_to_cache(str(DATA_DIR), start, end, honor_lookahead=False)

    gens = cache.skeleton["elements"]["generator"]
    by_type = {}
    for name, g in gens.items():
        by_type.setdefault(g["unit_type"], []).append(name)
    counts = {t: len(v) for t, v in sorted(by_type.items())}
    print(f"skeleton: {len(gens)} generators {counts}, "
          f"{len(cache.skeleton['elements']['bus'])} buses, "
          f"{len(cache.skeleton['elements']['area'])} areas")
    assert counts == {"COAL": 13, "CT": 113, "HYDRO": 10, "NUC": 2,
                      "PV": 72, "WIND": 82}, counts

    # --- timeseries coverage in the parsed cache ---------------------------
    df = cache.timeseries_df
    for sim in ("DAY_AHEAD", "REAL_TIME"):
        sub = df[df["Simulation"] == sim]
        loads = sub[(sub["Category"] == "Area") & (sub["Parameter"] == "MW Load")]
        assert len(loads) == 123, (sim, len(loads))
        lens = {len(s) for s in loads["Series"]}
        assert lens == {EXPECTED_HOURS}, (
            f"{sim} area-load series lengths {lens} != {{{EXPECTED_HOURS}}} — "
            "year-end padding not covering the provider window?")
        ren = sub[(sub["Category"] == "Generator") & (sub["Parameter"] == "PMax MW")]
        assert len(ren) == 154, (sim, len(ren))
        assert set(ren["Object"]) == set(by_type["WIND"]) | set(by_type["PV"])
        lens = {len(s) for s in ren["Series"]}
        assert lens == {EXPECTED_HOURS}, (sim, lens)
        print(f"{sim}: 123 area loads + 154 renewable PMax series, "
              f"all {EXPECTED_HOURS} h")

    # --- generated models (what the simulation actually sees) --------------
    for sim, hours in (("DAY_AHEAD", 48), ("REAL_TIME", 4)):
        md = cache.generate_model(sim, datetime(2019, 1, 1, 0),
                                  datetime(2019, 1, 1, 0)
                                  + timedelta(hours=hours))
        g = md.data["elements"]["generator"]
        ts = {name for name, d in g.items()
              if isinstance(d["p_max"], dict)
              and d["p_max"].get("data_type") == "time_series"}
        expect_ts = set(by_type["WIND"]) | set(by_type["PV"])
        assert ts == expect_ts, (
            f"{sim}: time-series p_max mismatch: missing "
            f"{sorted(expect_ts - ts)}, unexpected {sorted(ts - expect_ts)}")
        for name in expect_ts:
            assert len(g[name]["p_max"]["values"]) == hours, (sim, name)
        scalars = {name for name, d in g.items()
                   if d["unit_type"] == "HYDRO"}
        for name in scalars:
            assert isinstance(g[name]["p_max"], float), (sim, name)
        loads = md.data["elements"]["load"]
        assert len(loads) == 123, (sim, len(loads))
        for name, d in loads.items():
            assert (isinstance(d["p_load"], dict)
                    and len(d["p_load"]["values"]) == hours), (sim, name)
        peak = max(sum(d["p_load"]["values"][t] for d in loads.values())
                   for t in range(hours))
        print(f"{sim} model ({hours} h): 154 renewable time-series p_max, "
              f"10 scalar-PMax hydro, 123 bus loads (window peak "
              f"{peak:,.0f} MW)")

    print("VERIFY PASS — metadata is model-complete for both simulation types")
    return 0


if __name__ == "__main__":
    sys.exit(main())
