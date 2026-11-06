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

Prompt 58 adds --ruc_mipgap (default 0.01 = the inherited value, so every
existing wave is unchanged). Precedence, read from the source (Prescient
a4c0849 == local HEAD on these files; egret fork e4a244d == local HEAD):
  prescient/engine/egret/egret_plugin.py:49   mipgap = options.ruc_mipgap
  prescient/engine/egret/egret_plugin.py:51   -> _solve_unit_commitment(
                                                 instance, solver, mipgap,
                                                 None, ..., solver_options)
  prescient/engine/egret/egret_plugin.py:358  solver_options =
                                              options.deterministic_ruc_solver_options
  egret/common/solver_interface.py:145        _set_options(solver, mipgap,
                                              timelimit, solver_options)
  egret/common/solver_interface.py:44-45      solver.options.MIPGap = mipgap   (FIRST)
  egret/common/solver_interface.py:71-73      solver.options[key] = opt        (AFTER,
                                              for every deterministic_ruc_solver_options key)
So `ruc_mipgap` is written FIRST and a `MIPGap` key in
deterministic_ruc_solver_options would silently OVERRIDE it. This wrapper
therefore refuses `--ruc_solver_option MIPGap=...` (and TimeLimit=..., which
has its own flag): the gap has exactly one source, `--ruc_mipgap`. Prescient
passes timelimit=None to egret, so TimeLimit reaches Gurobi only through
deterministic_ruc_solver_options (= --ruc_time_limit). Verify in the job log:
`Optimal solution found (tolerance <gap>)` printed by Gurobi on every RUC day.

The default --retrofit_gen_dict '{}' runs the BASE case (no retrofit;
unlike multi_PEM_PCM.py, {} here never falls back to an RTS example dict).
Generator names in this dataset are bare numeric strings ("1", "93") —
fine for the retrofit dict and _PEM suffixing; nothing assumes RTS names.

Usage:
    python run_ercot_pcm.py --index base --num_days 365 \
        --start_date 01-01-2019 --output_directory <dir>/run \
        [--retrofit_gen_dict '{"91": {"PEM_bid": 40.0, "PEM_fraction": 0.5,
                               "gen_pmax": 250.0}}'] \
        [--ruc_threads 1] [--ruc_time_limit 120] [--ruc_mipgap 0.01] \
        [--ruc_solver_option MIPFocus=1]
"""
import json
import os
import sys
from argparse import ArgumentParser

ERCOT_DIR = os.path.dirname(os.path.realpath(__file__))
DEFAULT_DATA_DIR = os.path.join(ERCOT_DIR, "data", "ercot123_2019")
MULTI_PEM_DIR = os.path.join(ERCOT_DIR, "..", "multi_pem")
sys.path.insert(0, MULTI_PEM_DIR)

import multi_PEM_PCM  # noqa: E402  (module-level prescient_options)
from parameters import update_function_multi  # noqa: E402


def parse_args(argv=None):
    p = ArgumentParser(__doc__)
    p.add_argument("--index", default="0")
    p.add_argument("--data_dir", default=DEFAULT_DATA_DIR,
                   help="RTS-GMLC-format data dir (default: v1 ercot123_2019; "
                   "prompt 36 runs pass data/ercot123_2019_v2)")
    p.add_argument("--output_directory", default="ercot_pcm")
    p.add_argument("--retrofit_gen_dict", default="{}",
                   help="JSON dict of generator name -> PEM data; '{}' = base")
    p.add_argument("--num_days", type=int, default=365)
    p.add_argument("--start_date", default="01-01-2019")
    p.add_argument("--ruc_time_limit", type=float, default=120.0)
    p.add_argument("--ruc_mipgap", type=float, default=0.01,
                   help="Prescient ruc_mipgap (relative MIPGap of every RUC "
                   "solve); default 0.01 = the inherited multi_PEM value "
                   "(prompt 58). Set BEFORE deterministic_ruc_solver_options "
                   "by egret _set_options — see the module docstring.")
    p.add_argument("--ruc_threads", type=int, default=1,
                   help="Gurobi Threads for the RUC (= requested slot count)")
    p.add_argument("--ruc_solver_option", action="append", default=[],
                   metavar="KEY=VAL", help="extra gurobi RUC options, e.g. "
                   "MIPFocus=1 (rider (iv) incumbent-finding)")
    return p.parse_args(argv)


def build_options(args):
    opts = dict(multi_PEM_PCM.prescient_options)
    data_dir = os.path.realpath(args.data_dir)
    if not os.path.isfile(os.path.join(data_dir, "gen.csv")):
        raise SystemExit(f"--data_dir {data_dir} has no gen.csv")
    opts["data_path"] = data_dir
    opts["output_directory"] = args.output_directory
    opts["start_date"] = args.start_date
    opts["num_days"] = args.num_days
    opts["deterministic_ruc_solver"] = "gurobi_persistent"
    ruc_opts = {"TimeLimit": args.ruc_time_limit, "Threads": args.ruc_threads}
    for kv in args.ruc_solver_option:
        k, _, v = kv.partition("=")
        if not _:
            raise SystemExit(f"--ruc_solver_option needs KEY=VAL, got {kv!r}")
        if k.lower() in ("mipgap", "timelimit"):
            # egret _set_options applies deterministic_ruc_solver_options AFTER
            # ruc_mipgap: a MIPGap key here would silently override --ruc_mipgap.
            raise SystemExit(f"--ruc_solver_option {k} refused: use "
                             f"--ruc_mipgap / --ruc_time_limit (one source each)")
        try:
            ruc_opts[k] = int(v)
        except ValueError:
            ruc_opts[k] = float(v)
    opts["deterministic_ruc_solver_options"] = ruc_opts
    if not (0.0 <= args.ruc_mipgap < 1.0):
        raise SystemExit(f"--ruc_mipgap must be in [0, 1), got {args.ruc_mipgap}")
    opts["ruc_mipgap"] = args.ruc_mipgap  # prompt 58; 0.01 == inherited value
    opts["output_solver_logs"] = True  # rider (i): gap/SolCount from logs
    return opts


def main():
    args = parse_args()
    pem_data = json.loads(args.retrofit_gen_dict)
    if not isinstance(pem_data, dict):
        raise SystemExit("--retrofit_gen_dict must decode to a dict")
    opts = build_options(args)
    print(f"run_ercot_pcm: data_dir={opts['data_path']}")
    print(f"run_ercot_pcm: index={args.index} start_date={opts['start_date']} "
          f"num_days={opts['num_days']} output={opts['output_directory']} "
          f"ruc_mipgap={opts['ruc_mipgap']} "
          f"ruc_solver_options={opts['deterministic_ruc_solver_options']} "
          f"PEM_data={pem_data}")
    from utils import parameter_sweep_runner
    parameter_sweep_runner(update_function_multi, opts, args.index, pem_data)


if __name__ == "__main__":
    main()
