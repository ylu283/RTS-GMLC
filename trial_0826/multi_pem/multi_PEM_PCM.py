import os
import json
from argparse import ArgumentParser
from parameters import update_function_multi

usage = "Run PCM sweep with NE+PEM model for multiple generators."

this_file_path = os.path.dirname(os.path.realpath(__file__))
data_path = os.path.join(this_file_path, "..","..", "RTS_Data", "SourceData")

# default some options
output_path = None
# Deliberate conventions (doc 14 §5.3):
#   price_threshold: 500 — caps scarcity LMPs (Prescient default is 10,000)
#   sced_horizon: 1      — zero real-time lookahead
#   reserve_factor: 0.1  — system reserve requirement
prescient_options = {
        "data_path":data_path,
        "reserve_factor": 0.1,
        "simulate_out_of_sample":True,
        "output_directory":output_path,
        "monitor_all_contingencies":False,
        "input_format":"rts-gmlc",
        "sced_horizon":1,
        "ruc_mipgap":0.01,
	    "deterministic_ruc_solver": "gurobi",
        "sced_solver":"gurobi",
        "sced_frequency_minutes":60,
	    "sced_solver_options" : {"threads":1},
        "ruc_horizon":36,
        "compute_market_settlements":True,
        "output_solver_logs":False,
        "price_threshold":500,
        "transmission_price_threshold":None,
        "contingency_price_threshold":None,
        "reserve_price_threshold":None,
        "day_ahead_pricing":"aCHP",
        "enforce_sced_shutdown_ramprate":False,
        "ruc_slack_type":"ref-bus-and-branches",
        "sced_slack_type":"ref-bus-and-branches",
	    "disable_stackgraphs":True,
        "symbolic_solver_labels":True,
        "output_ruc_solutions": False,
        "write_deterministic_ruc_instances": False,
        "write_sced_instances": False,
        "print_sced":False
        }


def parse_args(argv=None):
    parser = ArgumentParser(usage)

    parser.add_argument(
        "--index",
        dest="index",
        help="Indicate the simulation index. Accepts an integer or a string (e.g. '7_day_test').",
        action="store",
        type=str,
        default="0",
    )

    parser.add_argument(
        "--output_directory",
        dest="output_directory",
        help="Set the output directory name.",
        action="store",
        type=str,
        default="NE_PEM_sweep_multi",
    )

    parser.add_argument(
        "--retrofit_gen_dict",
        dest="retrofit_gen_dict",
        help="Set the retrofit generator dictionary as a JSON string, "
             "e.g. '{\"121_NUCLEAR_1\": {\"PEM_bid\": 25, \"PEM_fraction\": 0.5}}'.",
        action="store",
        default={},
    )

    parser.add_argument(
        "--num_days",
        dest="num_days",
        help="Number of days to simulate.",
        action="store",
        type=int,
        default=366,
    )

    parser.add_argument(
        "--start_date",
        dest="start_date",
        help="Simulation start date, MM-DD-YYYY.",
        action="store",
        type=str,
        default="01-01-2020",
    )

    return parser.parse_args(argv)


def main():
    options = parse_args()

    index = options.index
    prescient_options["output_directory"] = options.output_directory
    prescient_options["start_date"] = options.start_date
    prescient_options["num_days"] = options.num_days

    # Dictionary of generator name -> PEM data for that generator.
    # PEM_bid : PEM bid price in $/MWh ("PEM_indifference_point" is a deprecated alias)
    # PEM_fraction : PEM power as a ratio of the installed capacity
    # gen_pmax : installed capacity in MW (required for renewable generators only)
    if options.retrofit_gen_dict == {}:
        PEM_data = {
            "121_NUCLEAR_1": {"PEM_bid": 25, "PEM_fraction": 0.5},
            "303_WIND_1": {"PEM_bid": 20, "PEM_fraction": 0.2, "gen_pmax": 847},
        }
    elif isinstance(options.retrofit_gen_dict, dict):
        PEM_data = options.retrofit_gen_dict
    elif isinstance(options.retrofit_gen_dict, str):
        try:
            PEM_data = json.loads(options.retrofit_gen_dict)
        except json.JSONDecodeError as e:
            raise ValueError(
                f"--retrofit_gen_dict must be a valid JSON string, got: {options.retrofit_gen_dict!r}"
            ) from e
        if not isinstance(PEM_data, dict):
            raise ValueError(
                f"--retrofit_gen_dict must decode to a dict, got: {type(PEM_data).__name__}"
            )
    else:
        raise ValueError(
            f"--retrofit_gen_dict must be a dict or a JSON string, got: {type(options.retrofit_gen_dict).__name__}"
        )

    print(
        f"multi_PEM_PCM run: index={index} start_date={options.start_date} "
        f"num_days={options.num_days} output_directory={options.output_directory} "
        f"PEM_data={PEM_data}"
    )

    # Deferred import: utils pulls in prescient.simulator, which is not needed
    # (or installed) just to show --help.
    from utils import parameter_sweep_runner

    parameter_sweep_runner(update_function_multi, prescient_options, index, PEM_data)


if __name__ == "__main__":
    main()
