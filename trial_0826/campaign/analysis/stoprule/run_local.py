"""Run local_tasks.csv rows (filter by block) on the Mac: 4 worker processes
x 1 thread each (the session's 4-thread cap); finished runs are skipped,
interrupted ones resume from their checkpoint.

  python run_local.py R      # 2-D replay, M1 + M4
  python run_local.py A B C D   # 6-D M4 (after the truth build)
"""
import csv
import os
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent


def _one(t):
    os.environ["OMP_NUM_THREADS"] = "1"
    sys.path.insert(0, str(HERE))
    import torch
    torch.set_num_threads(1)
    import warnings
    warnings.simplefilter("ignore")
    import runner
    p = runner.result_path(t["problem"], t["method"], int(t["seed"]), float(t["noise"]), int(t["q"]))
    if p.exists():
        return "skip"
    runner.run(t["problem"], t["method"], int(t["seed"]), noise=float(t["noise"]), q=int(t["q"]),
               cand_rule=t["cand_rule"], verbose=False)
    return "done"


if __name__ == "__main__":
    sys.path.insert(0, str(HERE))
    from sr_common import assert_bogp
    print("bo-gp", assert_bogp(), flush=True)
    blocks = set(sys.argv[1:])
    rows = [r for r in csv.DictReader(open(HERE / "local_tasks.csv")) if r["block"] in blocks]
    print(len(rows), "tasks", flush=True)
    with ProcessPoolExecutor(4) as ex:
        for i, r in enumerate(ex.map(_one, rows, chunksize=1), 1):
            if i % 50 == 0:
                print(i, r, flush=True)
    print("all done", flush=True)
