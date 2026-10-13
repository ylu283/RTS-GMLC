"""Prompt 35 §3.2 — N1 replay gate (env `bogp-botorch`).

Runs N1's qNEHVI acquirer under the EXACT protocol of
analysis/bo_replay/qparego_smoke_C.csv (bo_replay.ipynb §4): scenario C
contour_303x317 81-cell grid, M = the 4 replay objectives, n0 = 8 random
cells (default_rng(s).choice(81, 8)), q = 8, 2 rounds, seeds 0..9, ref = the
full-81 nadir + 10 % span, HV recovery = HV / HV(all 81).
Gate (PREREG clarification 1): N1's median at n = 16 AND n = 24 inside the
min–max of q-ParEGO's 10 per-seed values. Writes replay_gate.json.
"""
import json
import os
import sys
import time

import numpy as np
import torch

torch.set_num_threads(4)
HERE = os.path.dirname(os.path.abspath(__file__))
CAMP = os.path.abspath(os.path.join(HERE, "..", ".."))
if os.environ.get("BOGP_PATH"):  # the qparego worktree, ahead of any installed bogp
    sys.path.insert(0, os.environ["BOGP_PATH"])
sys.path.insert(0, os.path.join(CAMP, "analysis", "bo_replay"))
sys.path.insert(0, HERE)
import replay as R  # noqa: E402
import qnehvi as qn  # noqa: E402
from bogp.mobo.pareto import hypervolume_exact  # noqa: E402

SEEDS, N0, Q, ROUNDS = list(range(10)), 8, 8, 2


def smoke_range():
    per = json.load(open(os.path.join(CAMP, "analysis", "bo_replay", "replay_results.json")))["qparego_smoke_C"]
    assert per["seeds"] == SEEDS and per["n0"] == N0 and per["q"] == Q and per["rounds"] == ROUNDS
    v16 = [p["hv_n16"] for p in per["per_seed"]]
    v24 = [p["hv_n24"] for p in per["per_seed"]]
    return {16: (min(v16), max(v16)), 24: (min(v24), max(v24))}


def amended_pass(g):
    """AMENDMENT 2026-10-12 (Kay, after the result; PREREG.md): ONE-SIDED gate —
    N1's median >= the q-ParEGO smoke MIN at both n = 16 and n = 24. The
    two-sided `PASS` stored in replay_gate.json is kept as the original record."""
    return all(g["median"][n] >= g["qparego_range"][n][0] for n in ("16", "24"))


def run_seed(s, X, Y, ref, hv_all, floors):
    idx = list(np.random.default_rng(s).choice(81, N0, replace=False))
    curve = [hypervolume_exact(Y[idx], ref) / hv_all]
    for r in range(ROUNDS):
        out = qn.propose_qnehvi_batch(X[idx], Y[idx], X, ref, floors, q=Q, seed=s * 100 + r, log=lambda *_: None)
        new = [int(i) for i in out["cand_idx"]]
        assert not set(new) & set(idx), "re-queried cell"
        idx += new
        curve.append(hypervolume_exact(Y[idx], ref) / hv_all)
    assert len(set(idx)) == N0 + Q * ROUNDS
    return curve


def main(seeds=SEEDS, write=True):
    X, Y = R.xy(R.load_scenario("C"))
    h = R.hv_reference(Y)
    ref, hv_all = h["ref"], hypervolume_exact(Y, h["ref"])
    fl = R.floors()
    floors = np.array([fl[o] for o in R.OBJECTIVES])
    t0 = time.time()
    curves = [run_seed(s, X, Y, ref, hv_all, floors) for s in seeds]
    c = np.array(curves)
    rng = smoke_range()
    med = {16: float(np.median(c[:, 1])), 24: float(np.median(c[:, 2]))}
    passed = all(rng[n][0] <= med[n] <= rng[n][1] for n in (16, 24))
    out = {"seeds": list(seeds), "curves_n8_n16_n24": c.tolist(), "median": med,
           "qparego_range": {str(k): v for k, v in rng.items()}, "PASS": bool(passed),
           "seconds": time.time() - t0, "floors": floors.tolist(), "objectives": R.OBJECTIVES}
    if write:
        json.dump(out, open(os.path.join(HERE, "replay_gate.json"), "w"), indent=2)
    print(json.dumps({k: out[k] for k in ("median", "qparego_range", "PASS", "seconds")}, indent=1))
    return out


if __name__ == "__main__":
    main()
