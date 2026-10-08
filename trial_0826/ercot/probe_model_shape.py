"""Prompt 32 T1.0 gate (i): assert the ERCOT gen-1 model shape ON CRC.

Loads one day of the model exactly the way Prescient's provider does
(egret parse_to_cache + generate_model) and asserts the facts the thermal
patch depends on. Run under PCM_ERCOT on a login node or a short debug job:
    python probe_model_shape.py
Exit 0 = gate pass. Locally verified 2026-10-08 (ercot223 env): thermal,
p_min=729, parser emits p_fuel (fuel_curve) and NO p_cost -> the patch
takes its del-p_fuel branch.
"""

import json
import os
import sys
from datetime import datetime

from egret.parsers.rts_gmlc.parser import parse_to_cache

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data", "ercot123_2019")


def main():
    cache = parse_to_cache(DATA, datetime(2019, 1, 1), datetime(2019, 1, 3))
    md = cache.generate_model("DAY_AHEAD", datetime(2019, 1, 1),
                              datetime(2019, 1, 2))
    g = md.data["elements"]["generator"]["1"]
    assert g["generator_type"] == "thermal", g["generator_type"]
    assert "p_min" in g and float(g["p_min"]) == 729.0, g.get("p_min")
    has_fuel, has_cost = "p_fuel" in g, "p_cost" in g
    print(f"gen 1: thermal, p_min={g['p_min']}, p_max={g['p_max']}, "
          f"p_fuel={has_fuel}, p_cost={has_cost}")
    assert has_fuel or has_cost, "neither p_fuel nor p_cost — patch would KeyError"
    record = {"generator_type": g["generator_type"], "p_min": g["p_min"],
              "p_max": g["p_max"], "has_p_fuel": has_fuel,
              "has_p_cost": has_cost,
              "fuel_cost": g.get("fuel_cost"),
              "p_fuel_values": g.get("p_fuel", {}).get("values"),
              "min_up_time": g.get("min_up_time")}
    out = os.path.join(HERE, "analysis", "selection", "gen1_model_shape.json")
    with open(out, "w") as f:
        json.dump(record, f, indent=2)
        f.write("\n")
    print("PROBE PASS — recorded to", out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
