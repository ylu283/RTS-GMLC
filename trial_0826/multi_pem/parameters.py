import copy


def _get_bid(gen_PEM_data):
    """Return the PEM bid price ($/MWh).

    "PEM_bid" is the preferred key; "PEM_indifference_point" is accepted as a
    deprecated alias (under the frozen /10 convention B is a bid, not the
    theoretical indifference point). Raises if both are present with
    different values.
    """
    has_bid = "PEM_bid" in gen_PEM_data
    has_legacy = "PEM_indifference_point" in gen_PEM_data
    if has_bid and has_legacy and gen_PEM_data["PEM_bid"] != gen_PEM_data["PEM_indifference_point"]:
        raise ValueError(
            "Conflicting bid values: PEM_bid="
            f"{gen_PEM_data['PEM_bid']} vs deprecated PEM_indifference_point="
            f"{gen_PEM_data['PEM_indifference_point']}; provide only 'PEM_bid'"
        )
    if has_bid:
        return gen_PEM_data["PEM_bid"]
    if has_legacy:
        return gen_PEM_data["PEM_indifference_point"]
    raise KeyError("PEM data must contain 'PEM_bid' (or the deprecated alias 'PEM_indifference_point')")


def _update_thermal_generator(gen, gen_PEM_data, n_time_keys):
    PEM_capacity = gen_PEM_data["PEM_fraction"] * gen["p_max"]
    gen["p_min"] = gen["p_max"] - PEM_capacity

    if "p_cost" not in gen:
        del gen["p_fuel"]
        gen["p_cost"] = { "data_type" : "cost_curve", "cost_curve_type" : "piecewise" }
    else:
        assert isinstance(gen["p_cost"], dict) and gen["p_cost"].get("cost_curve_type") == "piecewise", (
            f"Cannot overwrite p_cost: expected a piecewise cost-curve dict, got {gen['p_cost']!r}"
        )
    gen["p_cost"]["values"] = [[gen["p_min"], 0.], [gen["p_max"], PEM_capacity*_get_bid(gen_PEM_data)]]

    # Egret ramp units are MW/h; the flexible band is exactly the PEM capacity.
    gen["ramp_up_60min"] = PEM_capacity
    gen["ramp_down_60min"] = PEM_capacity
    gen["fixed_commitment"] = {"data_type" : "time_series", "values" : [1]*n_time_keys}


def _update_renewable_generator(generators, gen_name, gen_PEM_data):
    gen = generators[gen_name]
    pem_name = gen_name + "_PEM"

    # Splitting a must-take unit (nonzero p_min, e.g. RTPV/HYDRO) would make the model infeasible.
    pmin = gen.get("p_min", 0.)
    if isinstance(pmin, dict):
        assert all(val == 0 for val in pmin["values"]), (
            f"Renewable generator {gen_name} has a nonzero p_min time series (must-take unit); "
            "applying the PEM split would make the model infeasible"
        )
    else:
        assert pmin == 0, (
            f"Renewable generator {gen_name} has nonzero p_min={pmin} (must-take unit); "
            "applying the PEM split would make the model infeasible"
        )

    assert "gen_pmax" in gen_PEM_data, f"gen_pmax is required for renewable generator {gen_name}"
    PEM_power_capacity = gen_PEM_data["PEM_fraction"] * gen_PEM_data["gen_pmax"]

    pem = copy.deepcopy(gen)
    pem["p_min"] = 0.0
    pem["p_max"]["values"] = [min(PEM_power_capacity, val) for val in gen["p_max"]["values"]]
    pem["p_cost"] = _get_bid(gen_PEM_data)

    generators[pem_name] = pem

    for idx, val in enumerate(gen["p_max"]["values"]):
        gen["p_max"]["values"][idx] = max(0., val - PEM_power_capacity)


def _update_generator(generators, gen_name, gen_PEM_data, n_time_keys):
    gen = generators[gen_name]

    if gen["generator_type"] == "thermal":
        assert "p_min" in gen
        _update_thermal_generator(gen, gen_PEM_data, n_time_keys)
    elif gen["generator_type"] == "renewable":
        _update_renewable_generator(generators, gen_name, gen_PEM_data)
    else:
        raise ValueError(f"Unsupported generator_type {gen['generator_type']!r} for generator {gen_name}")


def update_function_multi(model_data, PEM_data):
    """
    Update multiple generators with their own PEM data.

    Args:
        model_data : the Prescient model data instance
        PEM_data (dict) : mapping of generator_name -> dict with keys:
            "PEM_bid" : PEM bid price in $/MWh (preferred; "PEM_indifference_point"
                is a deprecated alias),
            "PEM_fraction" : PEM power as a ratio of installed capacity,
            "gen_pmax" : installed capacity in MW — required for renewable generators only.

    Mechanics:
        Thermal: p_min is raised to p_max - PEM_capacity, the band is priced at the
            bid with forced commitment (the unit diverts to H2 when LMP < bid).
        Renewable: the unit is split into the parent (availability minus PEM_capacity,
            floored at 0) and a "<name>_PEM" unit (p_max = min(PEM_capacity,
            availability), scalar p_cost = bid) — priced withholding.

    Warning:
        Prescient reports gen_PEM's withheld (H2) energy as *Curtailment* of the
        "<name>_PEM" unit — post-processing must exclude "*_PEM" units from
        curtailment sums (that column is the H2 production time series).
    """
    generators = model_data.data["elements"]["generator"]
    n_time_keys = len(model_data.data["system"]["time_keys"])

    for gen_name, gen_PEM_data in PEM_data.items():
        assert gen_name in generators, f"Generator {gen_name} not found in model data"
        _update_generator(generators, gen_name, gen_PEM_data, n_time_keys)