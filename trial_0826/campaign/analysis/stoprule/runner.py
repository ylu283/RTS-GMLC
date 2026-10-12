"""Prompt 37 — one trajectory = (problem, method, replicate, cell variant).

Every 6-D run executes all rounds (default 8 x q = 8, n = 32 -> 96); stop
rules are applied POST HOC (rules.py). Per round the runner records the
queried lattice indices, the noisy observations, the method's own
acquisition outputs, and the calibration audit (PredGP per objective, fit
on rounds < k, graded on round k's batch). Checkpointed after every round
(resume = reload + continue; every per-round seed is a pure function of
the keys, so a resumed run equals an uninterrupted one).

Methods: M1 bogp q-ParEGO (frozen §1 call path), M3 qNEHVI (35's N1 copy,
`bogp-botorch` env), M4 random lattice (no repeats). M2 is conditional and
not implemented unless triggered (PREREG §M2).

CLI:
  runner.py run  --problem P --method M --seed s [--noise 1.0] [--q 8]
  runner.py task --tasks tasks.csv --row i          (CRC array entry)
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from sr_common import (  # noqa: E402
    D6, METHOD_IDS, calibration_stats, fit_prediction_gps, frozen_ref,
    hv, lattice_index, levels_of, mc_threshold, seed_int,
)
from problems import Problem  # noqa: E402

RESULTS = HERE / "results"
N0_6D, Q_6D, ROUNDS_6D = 32, 8, 8
N0_2D, Q_2D, ROUNDS_2D = 5, 2, 15
CAND_K = 20_000
START_KEY, M4_KEY, CAND_KEY, ACQ_KEY = 1000, 1004, 1005, 1001


def cell_name(problem: str, noise: float = 1.0, q: int | None = None) -> str:
    """results/<cell>/<method>/seed<s>.npz; the primary variant keeps the bare
    problem name."""
    q = q or (Q_2D if problem.startswith("R-") else Q_6D)
    tag = problem.replace(":", "__")
    if noise != 1.0:
        tag += f"__n{noise:g}"
    if q != (Q_2D if problem.startswith("R-") else Q_6D):
        tag += f"__q{q}"
    return tag


def result_path(problem: str, method: str, seed: int, noise: float = 1.0, q: int | None = None) -> Path:
    q = q or (Q_2D if problem.startswith("R-") else Q_6D)
    return RESULTS / cell_name(problem, noise, q) / method / f"seed{seed}.npz"


# --------------------------------------------------------------------------- #
# start sets (common to every method within a replicate)
# --------------------------------------------------------------------------- #
def sobol_starts_6d(rep: int, n0: int = N0_6D) -> np.ndarray:
    """Fresh scrambled-Sobol (d = 6, seed per replicate, never the Stage-2
    starts); u -> level min(floor(9u), 8); duplicates skipped, drawn until
    n0 unique lattice points."""
    from scipy.stats import qmc

    eng = qmc.Sobol(D6, scramble=True, seed=seed_int(START_KEY, rep))
    out: list[int] = []
    while len(out) < n0:
        lv = np.minimum(np.floor(eng.random(32) * 9), 8).astype(int)
        for i in lattice_index(lv):
            if int(i) not in out:
                out.append(int(i))
                if len(out) == n0:
                    break
    return np.array(out, np.int64)


def random_starts_2d(rep: int, n_cells: int = 81, n0: int = N0_2D) -> np.ndarray:
    return np.random.default_rng(seed_int(START_KEY, 2, rep)).choice(n_cells, n0, replace=False)


# --------------------------------------------------------------------------- #
# candidate rule (pre-registered; shared by M1-M3)
# --------------------------------------------------------------------------- #
def front_neighbours(idx_front: np.ndarray) -> np.ndarray:
    lv = levels_of(idx_front)
    nb = []
    for j in range(D6):
        for s in (-1, 1):
            m = lv.copy()
            m[:, j] += s
            ok = (m[:, j] >= 0) & (m[:, j] <= 8)
            nb.append(lattice_index(m[ok]))
    return np.unique(np.concatenate(nb)) if nb else np.empty(0, np.int64)


def candidate_set(prob: Problem, rule: str, evaluated: np.ndarray, Yobs: np.ndarray,
                  rep: int, k: int) -> np.ndarray:
    """Candidate lattice indices for round k (evaluated rows excluded)."""
    ev = np.zeros(prob.n_cand, bool)
    ev[evaluated] = True
    if prob.d != D6 or rule == "full":
        return np.flatnonzero(~ev)
    rng = np.random.default_rng(seed_int(CAND_KEY, prob.pid, rep, k))
    pool = np.flatnonzero(~ev)
    sub = rng.choice(pool, size=min(CAND_K, len(pool)), replace=False)
    from sr_common import nd_mask
    nb = front_neighbours(evaluated[nd_mask(Yobs)])
    nb = nb[~ev[nb]]
    return np.union1d(sub, nb)


# --------------------------------------------------------------------------- #
# one round's proposal
# --------------------------------------------------------------------------- #
def propose(method: str, prob: Problem, Xc: np.ndarray, idx_ev: np.ndarray, Yobs: np.ndarray,
            cand: np.ndarray, q: int, ref: np.ndarray, rep: int, k: int) -> tuple[np.ndarray, dict]:
    seed = seed_int(ACQ_KEY, prob.pid, METHOD_IDS[method], rep, k)
    if method == "M4":
        rng = np.random.default_rng(seed_int(M4_KEY, prob.pid, rep, k))
        return rng.choice(cand, size=q, replace=False), {}
    import torch
    torch.manual_seed(seed % (2 ** 31))
    if method == "M1":
        import gpytorch
        from bogp.mobo.qparego import propose_qparego_batch
        from sr_common import install_chunked_ei

        install_chunked_ei()
        # fast_pred_var: LOVE cache, exact while n < 100 (n <= 96 here)
        with gpytorch.settings.fast_pred_var():
            b = propose_qparego_batch(Xc[idx_ev], Yobs, q=q, candidates=Xc[cand], seed=seed)
        pick = cand[np.asarray(b["cand_idx"], int)]
        return pick, {"ei": np.asarray(b["ei"], float), "weights": np.asarray(b["weights"], float)}
    if method == "M3":
        import m3_qnehvi as m3

        b = m3.propose_qnehvi_batch(Xc[idx_ev], Yobs, Xc[cand], ref, prob.floors, q=q,
                                    seed=seed, log=lambda *a: None)
        # map back: propose_qnehvi_batch returns rows of the candidate array
        pick = cand[np.asarray(b["cand_idx"], int)]
        # S-model (E[HVI], 256 MC) is a 6-D rule; skipped on the 2-D replay
        ehvi = (m3.batch_ehvi(Xc[idx_ev], Yobs, Xc[pick], ref, prob.floors,
                              seed=seed_int(ACQ_KEY, 256, prob.pid, rep, k))
                if prob.d == D6 else float("nan"))
        return pick, {"acq_values": np.atleast_1d(np.asarray(b["acq_values"], float)),
                      "ehvi256": ehvi}
    raise ValueError(method)


# --------------------------------------------------------------------------- #
# trajectory
# --------------------------------------------------------------------------- #
def run(problem: str, method: str, rep: int, noise: float = 1.0, q: int | None = None,
        rounds: int | None = None, cand_rule: str = "subset", audit: bool | None = None,
        out: Path | None = None, verbose: bool = True) -> Path:
    prob = Problem(problem, noise_mult=noise)
    six = prob.d == D6
    q = q or (Q_6D if six else Q_2D)
    rounds = rounds or ((96 - N0_6D) // q if six else ROUNDS_2D)
    audit = six if audit is None else audit
    out = out or result_path(problem, method, rep, noise, q)
    out.parent.mkdir(parents=True, exist_ok=True)
    ckpt = out.with_suffix(".ckpt.npz")
    Xc = prob.candidates()

    if ckpt.exists():
        st = dict(np.load(ckpt, allow_pickle=True))
        idx = list(st["idx"].astype(int))
        Yobs = st["Yobs"]
        rec = json.loads(str(st["rec"]))
        k0 = int(st["k_done"]) + 1
    else:
        idx = list(sobol_starts_6d(rep) if six else random_starts_2d(rep, prob.n_cand))
        Yobs = prob.evaluate(idx, rep)
        ref = frozen_ref(Yobs)
        tau = mc_threshold(Yobs, ref, prob.floors)
        rec = {"problem": problem, "method": method, "seed": rep, "noise": noise, "q": q,
               "rounds": rounds, "cand_rule": cand_rule if six else "full", "n0": len(idx),
               "ref_frozen": ref.tolist(), "tau": tau, "hv0_obs": hv(Yobs, ref),
               "per_round": []}
        k0 = 1
    ref = np.asarray(rec["ref_frozen"], float)

    for k in range(k0, rounds + 1):
        t0 = time.time()
        idx_ev = np.asarray(idx, np.int64)
        cand = candidate_set(prob, cand_rule, idx_ev, Yobs, rep, k) if method != "M4" else \
            np.setdiff1d(np.arange(prob.n_cand), idx_ev)
        pick, info = propose(method, prob, Xc, idx_ev, Yobs, cand, q, ref, rep, k)
        pick = np.asarray(pick, np.int64)
        assert len(set(pick.tolist())) == q and not (set(pick.tolist()) & set(idx)), "bad batch"
        t_acq = time.time() - t0
        y_new = prob.evaluate(pick, rep)
        r = {"k": k, "n_cand": int(len(cand)), "t_acq": t_acq,
             **{kk: (v.tolist() if isinstance(v, np.ndarray) else v) for kk, v in info.items()}}
        if audit:
            # PredGP (the live grading layer) fit on rounds < k, graded on batch k;
            # also its mean at every point so far (for the H_{k} prediction)
            import torch
            torch.manual_seed(0)
            gps = fit_prediction_gps(Xc[idx_ev], Yobs, prob.floors)
            allx = Xc[np.r_[idx_ev, pick]]
            pm = np.column_stack([g.predict(allx)[0] for g in gps])
            ps = np.column_stack([g.predict(Xc[pick])[1] for g in gps])
            r["audit"] = [calibration_stats(y_new[:, j], pm[-q:, j], ps[:, j])
                          for j in range(prob.M)]
            r["pred_mean_all"] = pm.tolist()
            r["pred_sd_batch"] = ps.tolist()
        idx += pick.tolist()
        Yobs = np.vstack([Yobs, y_new])
        r["t_round"] = time.time() - t0
        rec["per_round"].append(r)
        np.savez_compressed(ckpt, idx=np.asarray(idx, np.int64), Yobs=Yobs,
                            rec=json.dumps(rec), k_done=k)
        if verbose:
            print(f"{problem} {method} s{rep} r{k}: n={len(idx)} acq {t_acq:.1f}s "
                  f"round {r['t_round']:.1f}s", flush=True)

    np.savez_compressed(out, idx=np.asarray(idx, np.int64), Yobs=Yobs, rec=json.dumps(rec))
    ckpt.unlink(missing_ok=True)
    return out


def run_task(tasks: Path, row: int) -> Path:
    with open(tasks) as f:
        rows = list(csv.DictReader(f))
    t = rows[row - 1]  # SGE_TASK_ID is 1-based
    assert int(t["task"]) == row, (t, row)
    return run(t["problem"], t["method"], int(t["seed"]), noise=float(t["noise"]),
               q=int(t["q"]), cand_rule=t["cand_rule"])


def main(argv=None):
    from sr_common import assert_bogp, set_threads

    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("run")
    a.add_argument("--problem", required=True)
    a.add_argument("--method", required=True)
    a.add_argument("--seed", type=int, required=True)
    a.add_argument("--noise", type=float, default=1.0)
    a.add_argument("--q", type=int, default=None)
    a.add_argument("--cand-rule", default="subset")
    b = sub.add_parser("task")
    b.add_argument("--tasks", required=True)
    b.add_argument("--row", type=int, required=True)
    args = p.parse_args(argv)
    set_threads(int(os.environ.get("NSLOTS", os.environ.get("OMP_NUM_THREADS", "4"))))
    print("bo-gp", assert_bogp(), flush=True)
    if args.cmd == "run":
        print(run(args.problem, args.method, args.seed, args.noise, args.q,
                  cand_rule=args.cand_rule))
    else:
        print(run_task(Path(args.tasks), args.row))


if __name__ == "__main__":
    main()
