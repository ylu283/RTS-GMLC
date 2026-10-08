import os
import subprocess
import sys

import pytest

MODULE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, MODULE_DIR)

from parameters import update_function_multi  # noqa: E402

N_HOURS = 4
AVAIL = [0.0, 50.0, 120.0, 200.0]


class FakeModelData:
    def __init__(self, generators, n_hours=N_HOURS):
        self.data = {
            "elements": {"generator": generators},
            "system": {"time_keys": [str(i + 1) for i in range(n_hours)]},
        }


def thermal_gen():
    return {
        "generator_type": "thermal",
        "p_max": 400.0,
        "p_min": 160.0,
        "p_fuel": {"data_type": "fuel_curve", "values": [[160.0, 100.0], [400.0, 250.0]]},
    }


def renewable_gen(p_min=0.0):
    return {
        "generator_type": "renewable",
        "p_min": p_min,
        "p_max": {"data_type": "time_series", "values": list(AVAIL)},
    }


def ercot_gen1():
    """Mirror of the ACTUAL built ERCOT gen-1 dict (TX-123BT, egret 0.6.2;
    probed locally 2026-10-08 via parse_to_cache + generate_model — see
    ercot/probe_model_shape.py, which re-verifies on CRC). The parser emits
    p_fuel (fuel_curve) and NO p_cost, so the patch must take its
    del-p_fuel branch; p_min=729 is the fact the retrofit arithmetic uses.
    The synthetic RTS fixture above does not cover this shape (4-point
    curve, fuel_cost, startup_fuel, 48 h min up/down)."""
    return {
        "generator_type": "thermal",
        "p_max": 2430.0,
        "p_min": 729.0,
        "fuel_cost": 0.81035,
        "p_fuel": {"data_type": "fuel_curve",
                   "values": [[729.0, 2623266.49], [1296.0, 2631470.84],
                              [1863.0, 2640395.01], [2430.0, 2650039.0]]},
        "startup_fuel": [(48.0, 1.0)],
        "non_fuel_startup_cost": 1.0,
        "min_up_time": 48.0,
        "min_down_time": 48.0,
        "ramp_up_60min": 7290.0,
        "ramp_down_60min": 7290.0,
    }


def test_thermal_patch():
    generators = {"121_NUCLEAR_1": thermal_gen()}
    md = FakeModelData(generators)
    update_function_multi(md, {"121_NUCLEAR_1": {"PEM_bid": 25.0, "PEM_fraction": 0.5}})

    gen = generators["121_NUCLEAR_1"]
    pem_cap = 0.5 * 400.0
    assert gen["p_min"] == 400.0 - pem_cap
    assert "p_fuel" not in gen
    assert gen["p_cost"]["cost_curve_type"] == "piecewise"
    assert gen["p_cost"]["values"] == [[200.0, 0.0], [400.0, pem_cap * 25.0]]
    assert gen["ramp_up_60min"] == pem_cap
    assert gen["ramp_down_60min"] == pem_cap
    assert gen["fixed_commitment"]["values"] == [1] * N_HOURS


def test_thermal_patch_full_fraction():
    # omega = 1.0 (stage-2 lattice top): the entire unit becomes the PEM band.
    # This regime has never run in Prescient — the patch must produce p_min = 0
    # with the cost curve spanning [0, p_max] (prompt 27 T1.4).
    generators = {"121_NUCLEAR_1": thermal_gen()}
    md = FakeModelData(generators)
    update_function_multi(md, {"121_NUCLEAR_1": {"PEM_bid": 40.0, "PEM_fraction": 1.0}})

    gen = generators["121_NUCLEAR_1"]
    assert gen["p_min"] == 0.0
    assert gen["p_cost"]["values"] == [[0.0, 0.0], [400.0, 400.0 * 40.0]]
    assert gen["ramp_up_60min"] == 400.0
    assert gen["ramp_down_60min"] == 400.0
    assert gen["fixed_commitment"]["values"] == [1] * N_HOURS


def test_thermal_patch_omega_above_half():
    # omega = 0.7625 (a stage-2 lattice level above the old 0.5 cap):
    # p_min = p_max - PEM_cap stays positive but below half load.
    generators = {"121_NUCLEAR_1": thermal_gen()}
    md = FakeModelData(generators)
    update_function_multi(md, {"121_NUCLEAR_1": {"PEM_bid": 40.0, "PEM_fraction": 0.7625}})

    gen = generators["121_NUCLEAR_1"]
    pem_cap = 0.7625 * 400.0
    assert gen["p_min"] == 400.0 - pem_cap == 95.0
    assert gen["p_cost"]["values"] == [[95.0, 0.0], [400.0, pem_cap * 40.0]]
    assert gen["ramp_up_60min"] == pem_cap
    assert gen["ramp_down_60min"] == pem_cap
    assert gen["fixed_commitment"]["values"] == [1] * N_HOURS


def test_renewable_patch():
    generators = {"303_WIND_1": renewable_gen()}
    md = FakeModelData(generators)
    update_function_multi(
        md, {"303_WIND_1": {"PEM_bid": 20.0, "PEM_fraction": 0.2, "gen_pmax": 500.0}}
    )

    pem_cap = 0.2 * 500.0
    assert "303_WIND_1_PEM" in generators
    pem = generators["303_WIND_1_PEM"]
    parent = generators["303_WIND_1"]

    assert pem["p_min"] == 0.0
    assert pem["p_cost"] == 20.0
    assert pem["p_max"]["values"] == [min(pem_cap, val) for val in AVAIL]
    assert parent["p_max"]["values"] == [max(0.0, val - pem_cap) for val in AVAIL]
    # availability conserved hour-by-hour
    for orig, p_val, pem_val in zip(AVAIL, parent["p_max"]["values"], pem["p_max"]["values"]):
        assert p_val + pem_val == orig


def test_renewable_nonzero_scalar_pmin_raises():
    generators = {"303_WIND_1": renewable_gen(p_min=5.0)}
    md = FakeModelData(generators)
    with pytest.raises(AssertionError):
        update_function_multi(
            md, {"303_WIND_1": {"PEM_bid": 20.0, "PEM_fraction": 0.2, "gen_pmax": 500.0}}
        )


def test_renewable_nonzero_timeseries_pmin_raises():
    # must-take form: RTPV/HYDRO carry a PMin time series
    pmin = {"data_type": "time_series", "values": [3.0, 0.0, 0.0, 0.0]}
    generators = {"313_RTPV_1": renewable_gen(p_min=pmin)}
    md = FakeModelData(generators)
    with pytest.raises(AssertionError):
        update_function_multi(
            md, {"313_RTPV_1": {"PEM_bid": 20.0, "PEM_fraction": 0.2, "gen_pmax": 500.0}}
        )


def test_thermal_non_piecewise_p_cost_raises_assertion_not_attribute_error():
    gen = thermal_gen()
    gen["p_cost"] = 12.0
    generators = {"121_NUCLEAR_1": gen}
    md = FakeModelData(generators)
    with pytest.raises(AssertionError):
        update_function_multi(md, {"121_NUCLEAR_1": {"PEM_bid": 25.0, "PEM_fraction": 0.5}})


def test_missing_generator_raises():
    md = FakeModelData({"121_NUCLEAR_1": thermal_gen()})
    with pytest.raises(AssertionError):
        update_function_multi(md, {"NOT_A_GEN": {"PEM_bid": 25.0, "PEM_fraction": 0.5}})


def test_conflicting_bid_keys_raise():
    generators = {"121_NUCLEAR_1": thermal_gen()}
    md = FakeModelData(generators)
    with pytest.raises(ValueError):
        update_function_multi(
            md,
            {
                "121_NUCLEAR_1": {
                    "PEM_bid": 25.0,
                    "PEM_indifference_point": 30.0,
                    "PEM_fraction": 0.5,
                }
            },
        )


@pytest.mark.parametrize("bid_key", ["PEM_bid", "PEM_indifference_point"])
def test_bid_keys_work_alone_thermal(bid_key):
    generators = {"121_NUCLEAR_1": thermal_gen()}
    md = FakeModelData(generators)
    update_function_multi(md, {"121_NUCLEAR_1": {bid_key: 25.0, "PEM_fraction": 0.5}})
    gen = generators["121_NUCLEAR_1"]
    assert gen["p_cost"]["values"][-1] == [400.0, 200.0 * 25.0]


@pytest.mark.parametrize("bid_key", ["PEM_bid", "PEM_indifference_point"])
def test_bid_keys_work_alone_renewable(bid_key):
    generators = {"303_WIND_1": renewable_gen()}
    md = FakeModelData(generators)
    update_function_multi(
        md, {"303_WIND_1": {bid_key: 20.0, "PEM_fraction": 0.2, "gen_pmax": 500.0}}
    )
    assert generators["303_WIND_1_PEM"]["p_cost"] == 20.0


def test_driver_help_smoke():
    # runs without prescient installed thanks to the deferred utils import;
    # absolute script path makes cwd irrelevant (sys.path[0] = script dir)
    script = os.path.join(MODULE_DIR, "multi_PEM_PCM.py")
    result = subprocess.run(
        [sys.executable, script, "--help"], capture_output=True, text=True
    )
    assert result.returncode == 0, result.stderr
    assert "--num_days" in result.stdout
    assert "--start_date" in result.stdout
    assert "--retrofit_gen_dict" in result.stdout


def test_ercot_gen1_full_fraction():
    """Prompt 32 T1.0 gate (ii): the never-executed ERCOT thermal path at
    omega = 1.0 — p_min -> 0 on the fixed-committed unit, whole fuel curve
    deleted, flat band at B = 40."""
    generators = {"1": ercot_gen1()}
    md = FakeModelData(generators)
    update_function_multi(md, {"1": {"PEM_bid": 40.0, "PEM_fraction": 1.0}})
    gen = generators["1"]
    assert gen["p_min"] == 0.0
    assert "p_fuel" not in gen
    assert gen["p_cost"]["cost_curve_type"] == "piecewise"
    assert gen["p_cost"]["values"] == [[0.0, 0.0], [2430.0, 2430.0 * 40.0]]
    assert gen["ramp_up_60min"] == 2430.0 and gen["ramp_down_60min"] == 2430.0
    assert all(v == 1 for v in gen["fixed_commitment"]["values"])
    # untouched fields survive (startup never incurred under u==1, but the
    # dict must not be mangled)
    assert gen["min_up_time"] == 48.0 and gen["fuel_cost"] == 0.81035


def test_ercot_gen1_midlattice():
    """omega = 0.525 (the T1 replicate level): band = 1275.75 MW,
    p_min = 1154.25 — above the unit's native PMin 729, which the patch
    overwrites by design (recorded ERCOT fact, same as RTS)."""
    generators = {"1": ercot_gen1()}
    md = FakeModelData(generators)
    update_function_multi(md, {"1": {"PEM_bid": 40.0, "PEM_fraction": 0.525}})
    gen = generators["1"]
    cap = 0.525 * 2430.0
    assert gen["p_min"] == 2430.0 - cap
    assert gen["p_cost"]["values"] == [[2430.0 - cap, 0.0], [2430.0, cap * 40.0]]
    assert gen["ramp_up_60min"] == cap
