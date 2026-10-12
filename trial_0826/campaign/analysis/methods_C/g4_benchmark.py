"""Prompt 35 G4 — one full-lattice qNEHVI proposal (n = 40 = S1 + bo_C_r1,
q = 8, float64, max_batch_size 512), wall + peak RSS. Run under
`/usr/bin/time -l` (macOS) for the OS-level peak; also records
resource.getrusage. Writes g4_benchmark.json. 4 threads (concurrency cap)."""
import json, os, resource, sys, time
import numpy as np
import torch
torch.set_num_threads(4)
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "bo_stage2"))
import acquire_next as an  # noqa: E402
import qnehvi as qn  # noqa: E402

CAMP = os.path.abspath(os.path.join(HERE, "..", ".."))
X, Y = an.load_training(CAMP, 1)
assert X.shape == (40, 6)
led = an.load_ledger(CAMP)
cand = an.lattice_candidates()
t0 = time.time()
r = qn.propose_qnehvi_batch(X, Y, cand, led["ref_point"], an.FLOORS, q=8, seed=20261006 + 400 + 1)
wall = time.time() - t0
peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss  # bytes on macOS
import botorch
out = {"n_train": 40, "q": 8, "n_candidates": int(len(cand)), "wall_s": wall,
       "peak_rss_gb": peak / 1e9, "threads": torch.get_num_threads(),
       "mc_samples": qn.MC_SAMPLES, "max_batch_size": qn.MAX_BATCH_SIZE,
       "botorch": botorch.__version__, "torch": torch.__version__,
       "picks": r["x_batch"].tolist(), "machine": os.uname().machine}
json.dump(out, open(os.path.join(HERE, "g4_benchmark.json"), "w"), indent=2)
print(json.dumps({k: v for k, v in out.items() if k != "picks"}, indent=1))
