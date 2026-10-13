"""BUILD-ONLY regression for the selection_t1_v2 tasks 6/7 deaths (2026-10-13):
"Generator 1 has less output at T0 than is feasible to ramp up to".

Parses one ERCOT v2 day exactly as Prescient's provider does (parse_to_cache
+ generate_model, then the parser's default T0 — no initial_status.csv: a
committed unit at its ORIGINAL p_min, 729 MW for gen 1), applies the thermal
patch to gen 1 at every omega of the selection lattice, and BUILDS the egret
UC model (Pyomo param validators run at construction). Nothing is solved, so
no solver is needed. Skips when egret or the v2 data dir is absent (e.g. the
RTS-only branches). Run with -s to see gen 1's ramp numbers.
"""

import os
import sys
from datetime import datetime

import pytest

MODULE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, MODULE_DIR)

from parameters import update_function_multi  # noqa: E402

V2_DIR = os.path.join(os.path.dirname(MODULE_DIR), "ercot", "data", "ercot123_2019_v2")
LATTICE = [0.05, 0.2875, 0.525, 0.7625, 1.0]

egret_parser = pytest.importorskip("egret.parsers.rts_gmlc.parser")
pytestmark = pytest.mark.skipif(not os.path.isfile(os.path.join(V2_DIR, "gen.csv")),
                                reason="ERCOT v2 data dir not present")


@pytest.fixture(scope="module")
def day1_model_data():
    cache = egret_parser.parse_to_cache(V2_DIR, datetime(2019, 1, 1), datetime(2019, 1, 2))
    md = cache.generate_model("DAY_AHEAD", datetime(2019, 1, 1), datetime(2019, 1, 2))
    egret_parser.set_t0_data(md.data, V2_DIR)   # no initial_status.csv -> parser defaults
    return md


def _build(md):
    from egret.models.unit_commitment import create_tight_unit_commitment_model
    return create_tight_unit_commitment_model(md, network_constraints="copperplate_power_flow")


def test_gen1_t0_and_ramp_facts(day1_model_data):
    g = day1_model_data.data["elements"]["generator"]["1"]
    print(f"\ngen 1 parsed: p_min {g['p_min']}, p_max {g['p_max']}, "
          f"ramp_up_60min {g['ramp_up_60min']} MW/h (gen.csv 'Ramp Rate MW/Min' x 60), "
          f"initial_status {g['initial_status']}, initial_p_output {g['initial_p_output']}")
    assert g["p_min"] == 729.0 and g["initial_status"] > 0 and g["initial_p_output"] == 729.0
    for w in LATTICE:
        cap = w * g["p_max"]
        print(f"  omega {w}: patched ramp_up_60min = PEM capacity {cap:.2f} MW/h; new p_min "
              f"{g['p_max'] - cap:.2f}; validator needs T0 >= {g['p_max'] - 2 * cap:.2f} "
              f"(T0 729 needs ramp >= {g['p_max'] - cap - 729:.2f})")


@pytest.mark.parametrize("omega", LATTICE)
def test_gen1_model_builds_at_every_lattice_omega(day1_model_data, omega):
    md = day1_model_data.clone()
    update_function_multi(md, {"1": {"PEM_bid": 40.0, "PEM_fraction": omega}})
    # build first: egret's PowerGeneratedT0 validator raises ValueError when
    # T0 < p_min - ramp_up_60min (omega 0.05 / 0.2875 without the fix)
    _build(md)
    # then the shared-T0 condition: omega 0.525 builds even without the fix
    # but would start day 1 by ramping up from the original 729 MW
    g = md.data["elements"]["generator"]["1"]
    assert g["initial_p_output"] >= g["p_min"]
