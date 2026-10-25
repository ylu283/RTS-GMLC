"""Prompt 45 §3.4: measured-shed re-run of the prompt-34 §3.3 rider (zero simulation).

Machinery: analysis/random_baseline/rb_hv.py (imported, unmodified). Its
perturb_task reads the module constant FLOORS; perturb_task_floors below is
that function with the floors passed in — nothing else differs (same seed
default_rng([20261006, d]), same draw order, same 2,000 subsets per draw,
R_frozen fixed, HV0 from the perturbed starts). Data and point row exactly
as random_baseline.ipynb cells 3/9/14: Y_S/Y_BO = an.load_training(CAMP, 2),
Y_POOL = random_C in index order, deterministic point row from p_hat48 at
R_frozen (t2_summary.json).

Step 1 (reproduce): old floors (3,000, 5,000, 0.5e6) must give the recorded
rows {'above': 467, 'comparable': 531, 'matched': 2} exactly.
Step 2 (re-run): shed level 285.3 (measured); curt 5,000 MWh and cost $0.5M
stay at their ASSUMED floors (only shed was measured).
Writes rider45.json. 4 worker processes (one heavy local job at a time).
"""
from __future__ import annotations

import json
import multiprocessing as mp
import os
import sys
import time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
CAMP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
RB = os.path.join(CAMP, "analysis", "random_baseline")
os.environ.setdefault("BOGP_PATH", "/Users/yilu/Documents/GitHub/bo-gp-qparego")
for p in (os.environ["BOGP_PATH"], os.path.join(CAMP, "analysis", "bo_stage2"), CAMP, RB):
    if p not in sys.path:
        sys.path.insert(0, p)
import rb_hv as rb  # noqa: E402

N_DRAWS, N_SUB, NPROC = 1000, 2000, 4
OLD_FLOORS = (3000.0, 5000.0, 0.5e6)
NEW_FLOORS = (285.3, 5000.0, 0.5e6)
RECORDED = {"above": 467, "comparable": 531, "matched": 2}


def perturb_task_floors(args):
    """rb.perturb_task with FLOORS passed in (body otherwise identical)."""
    d, Y_starts, Y_bo, Y_pool, ref, n_subsets, floors = args
    floors = np.asarray(floors, float)
    hv = rb._hv()
    rng = np.random.default_rng([rb.PERTURB_SEED, d])
    S = Y_starts + rng.normal(0, floors, Y_starts.shape)
    B = Y_bo + rng.normal(0, floors, Y_bo.shape)
    P = Y_pool + rng.normal(0, floors, Y_pool.shape)
    hv0 = hv(S, ref)
    bo_hv = hv(np.vstack([S, B]), ref)
    p, _ = rb.p_hat(S, P, bo_hv, ref, len(Y_bo), n_subsets, rng, hv)
    return p, bo_hv / hv0


def load():
    import acquire_next as an
    led = an.load_ledger(CAMP)
    _, Y48 = an.load_training(CAMP, 2)
    Y_S, Y_BO = Y48[:32], Y48[32:]
    w = os.path.join(CAMP, "waves", "random_C")
    dm = pd.read_csv(os.path.join(w, "design_matrix.csv"))
    ob = pd.read_csv(os.path.join(w, "objectives.csv"))
    R = dm.merge(ob[["index"] + rb.M_COLS], on="index", validate="1:1").sort_values("index")
    assert len(R) == 48 and list(R["index"]) == list(range(1, 49))
    Y_POOL = rb.pool_matrix(R)
    return Y_S, Y_BO, Y_POOL, np.asarray(led["ref_point"], float)


def run(pool, data, floors):
    Y_S, Y_BO, Y_POOL, ref = data
    t0 = time.time()
    pert = pool.map(perturb_task_floors,
                    [(d, Y_S, Y_BO, Y_POOL, ref, N_SUB, floors) for d in range(N_DRAWS)], chunksize=8)
    p = np.array([x for x, _ in pert])
    b = np.array([x for _, x in pert])
    rows = pd.Series([rb.verdict_row(x) for x in p]).value_counts().to_dict()
    return p, b, rows, time.time() - t0


def main():
    t2 = json.load(open(os.path.join(RB, "t2_summary.json")))
    det = t2["robust"]["det_point_row"]
    p48 = next(r["p_hat"] for r in t2["primary"] if r["ref"] == "R_frozen" and r["n"] == 48)
    assert rb.verdict_row(p48) == det == "above"
    assert np.allclose(rb.FLOORS, OLD_FLOORS)
    data = load()
    out = {"det_point_row": det, "p_hat48_R_frozen": p48, "n_draws": N_DRAWS, "n_subsets": N_SUB,
           "seed": "default_rng([20261006, d])", "threshold_frac": 0.8}
    with mp.get_context("spawn").Pool(NPROC) as pool:
        for name, fl in (("old_floors_reproduce", OLD_FLOORS), ("measured_shed_285.3", NEW_FLOORS)):
            p, b, rows, sec = run(pool, data, fl)
            frac = float(np.mean([rb.verdict_row(x) == det for x in p]))
            out[name] = {"floors": list(fl), "rows": {k: int(v) for k, v in rows.items()},
                         "frac_match": frac, "robust": frac >= 0.8,
                         "p_pert_p5_p50_p95": np.percentile(p, [5, 50, 95]).tolist(),
                         "bo_hv_over_hv0_p5_p50_p95": np.percentile(b, [5, 50, 95]).tolist(),
                         "seconds": sec}
            print(name, json.dumps(out[name], default=float))
            if name == "old_floors_reproduce":
                assert out[name]["rows"] == RECORDED, out[name]["rows"]
                assert np.allclose(out[name]["p_pert_p5_p50_p95"], t2["robust"]["p_pert_p5_p50_p95"], rtol=1e-12)
    with open(os.path.join(HERE, "rider45.json"), "w") as f:
        json.dump(out, f, indent=1, default=float)
        f.write("\n")


if __name__ == "__main__":
    main()
