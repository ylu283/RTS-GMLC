import copy


def _update_thermal_generator(gen, gen_PEM_data, n_time_keys):
    PEM_capacity = gen_PEM_data["PEM_fraction"] * gen["p_max"]
    gen["p_min"] = gen["p_max"] - PEM_capacity

    if "p_cost" not in gen:
        del gen["p_fuel"]
        gen["p_cost"] = { "data_type" : "cost_curve", "cost_curve_type" : "piecewise" }
    gen["p_cost"]["values"] = [[gen["p_min"], 0.], [gen["p_max"], PEM_capacity*gen_PEM_data["PEM_indifference_point"]]]

    gen["ramp_up_60min"] = PEM_capacity*60
    gen["ramp_down_60min"] = PEM_capacity*60
    gen["fixed_commitment"] = {"data_type" : "time_series", "values" : [1]*n_time_keys}


def _update_renewable_generator(generators, gen_name, gen_PEM_data):
    gen = generators[gen_name]
    pem_name = gen_name + "_PEM"

    assert "gen_pmax" in gen_PEM_data, f"gen_pmax is required for renewable generator {gen_name}"
    PEM_power_capacity = gen_PEM_data["PEM_fraction"] * gen_PEM_data["gen_pmax"]

    pem = copy.deepcopy(gen)
    pem["p_min"] = 0.0
    pem["p_max"]["values"] = [min(PEM_power_capacity, val) for val in gen["p_max"]["values"]]
    pem["p_cost"] = gen_PEM_data["PEM_indifference_point"]

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
        PEM_data (dict) : mapping of generator_name -> {"PEM_indifference_point": ..., "PEM_fraction": ...,
            "gen_pmax": ...}. "gen_pmax" (installed capacity) is only required for renewable generators.
    """
    generators = model_data.data["elements"]["generator"]
    n_time_keys = len(model_data.data["system"]["time_keys"])

    for gen_name, gen_PEM_data in PEM_data.items():
        assert gen_name in generators, f"Generator {gen_name} not found in model data"
        _update_generator(generators, gen_name, gen_PEM_data, n_time_keys)