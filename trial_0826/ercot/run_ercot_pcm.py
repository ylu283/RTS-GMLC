#!/usr/bin/env python3
"""ERCOT (TX-123BT) driver wrapper (prompt 26 T1.3).

multi_PEM_PCM.py hardcodes data_path at module level (no CLI flag exists),
so this wrapper imports its option dict and overrides:

  - data_path -> trial_0826/ercot/data/ercot123_2019 (regenerated metadata)
  - deterministic_ruc_solver gurobi -> gurobi_persistent with
    TimeLimit=120 + explicit Threads (Kay 09-19 decision; riders in
    CONFIG_ERCOT.md), extensible via --ruc_solver_option (rider (iv):
    e.g. MIPFocus=1 if any probe day shows SolCount=0)
  - output_solver_logs=True on ALL runs (rider (i): the per-day
    MIPGap/status/SolCount log is parsed from the job's solver output —
    Prescient's own CSVs carry no gap/SolCount)
  - defaults start_date 01-01-2019, num_days 365 (full year; Sep-30 has
    float — never cut the horizon)

Everything else (sced_horizon=1, ruc_horizon=36, ruc_mipgap=0.01,
price_threshold=500, day_ahead_pricing=aCHP, reserve_factor=0.1,
sced threads=1, ref-bus-and-branches slack, default ptdf network,
compute_market_settlements=True) is inherited from multi_PEM_PCM — the
cross-campaign comparability surface. See CONFIG_ERCOT.md.

The default --retrofit_gen_dict '{}' runs the BASE case (no retrofit;
unlike multi_PEM_PCM.py, {} here never falls back to an RTS example dict).
Generator names in this dataset are bare numeric strings ("1", "93") —
fine for the retrofit dict and _PEM suffixing; nothing assumes RTS names.

Usage:
    python run_ercot_pcm.py --index base --num_days 365 \
        --start_date 01-01-2019 --output_directory <dir>/run \
        [--retrofit_gen_dict '{"91": {"PEM_bid": 40.0, "PEM_fraction": 0.5,
                               "gen_pmax": 250.0}}'] \
        [--ruc_threads 1] [--ruc_time_limit 120] \
        [--ruc_solver_option MIPFocus=1]
"""
import json
import os
import sys
from argparse import ArgumentParser

ERCOT_DIR = os.path.dirname(os.path.realpath(__file__))
MULTI_PEM_DIR = os.path.join(ERCOT_DIR, "..", "multi_pem")
sys.path.insert(0, MULTI_PEM_DIR)

import multi_PEM_PCM  # noqa: E402  (module-level prescient_options)
from parameters import update_function_multi  # noqa: E402


def parse_args(argv=None):
    p = ArgumentParser(__doc__)
    p.add_argument("--index", default="0")
    p.add_argument("--output_directory", default="ercot_pcm")
    p.add_argument("--retrofit_gen_dict", default="{}",
                   help="JSON dict of generator name -> PEM data; '{}' = base")
    p.add_argument("--num_days", type=int, default=365)
    p.add_argument("--start_date", default="01-01-2019")
    p.add_argument("--ruc_time_limit", type=float, default=120.0)
    p.add_argument("--ruc_threads", type=int, default=1,
                   help="Gurobi Threads for the RUC (= requested slot count)")
    p.add_argument("--ruc_solver_option", action="append", default=[],
                   metavar="KEY=VAL", help="extra gurobi RUC options, e.g. "
                   "MIPFocus=1 (rider (iv) incumbent-finding)")
    return p.parse_args(argv)


def build_options(args):
    opts = dict(multi_PEM_PCM.prescient_options)
    opts["data_path"] = os.path.join(ERCOT_DIR, "data", "ercot123_2019")
    opts["output_directory"] = args.output_directory
    opts["start_date"] = args.start_date
    opts["num_days"] = args.num_days
    opts["deterministic_ruc_solver"] = "gurobi_persistent"
    ruc_opts = {"TimeLimit": args.ruc_time_limit, "Threads": args.ruc_threads}
    for kv in args.ruc_solver_option:
        k, _, v = kv.partition("=")
        if not _:
            raise SystemExit(f"--ruc_solver_option needs KEY=VAL, got {kv!r}")
        try:
            ruc_opts[k] = int(v)
        except ValueError:
            ruc_opts[k] = float(v)
    opts["deterministic_ruc_solver_options"] = ruc_opts
    opts["output_solver_logs"] = True  # rider (i): gap/SolCount from logs
    return opts


def main():
    args = parse_args()
    pem_data = json.loads(args.retrofit_gen_dict)
    if not isinstance(pem_data, dict):
        raise SystemExit("--retrofit_gen_dict must decode to a dict")
    opts = build_options(args)
    print(f"run_ercot_pcm: index={args.index} start_date={opts['start_date']} "
          f"num_days={opts['num_days']} output={opts['output_directory']} "
          f"ruc_solver_options={opts['deterministic_ruc_solver_options']} "
          f"PEM_data={pem_data}")
    from utils import parameter_sweep_runner
    parameter_sweep_runner(update_function_multi, opts, args.index, pem_data)


if __name__ == "__main__":
    main()
