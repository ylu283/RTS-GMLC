"""Prompt 39 secondary: acquisition replay (descriptive, 0 PCM runs).

Imports analysis/bo_stage2/acquire_next.py AS A LIBRARY (never its CLI —
`propose` rewrites the frozen waves/bo_C_r1 and appends to the campaign
ledger). Proposes a RECORD-ONLY r1 batch from the 16-, 32- and 48-start
GPs with the real r1 seed rule (torch.manual_seed(0) then
propose_qparego_batch seed = acq_seed_base + 1 = 20261007, derived from
acquire_next.main/propose_round and confirmed by round_records.json), and
computes the pairwise candidate overlap vs waves/bo_C_r1 plus the Spearman
correlation of the scalarized posterior mean over the full lattice between
arms (definition pre-registered in PROGRESS.md 07:32Z item 5).
Writes ONLY under analysis/initial_design/ (replay_r1.json).
"""
import json
import os
import sys
from datetime import datetime, timezone

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
CAMPAIGN = os.path.abspath(os.path.join(HERE, "..", ".."))
os.environ.setdefault("BOGP_PATH",
                      "/Users/yilu/Documents/GitHub/bo-gp-qparego")
sys.path.insert(0, os.path.join(CAMPAIGN, "analysis", "bo_stage2"))
sys.path.insert(0, HERE)

import common  # noqa: E402  (sets torch threads to 4)
import acquire_next as an  # noqa: E402  (library import; NO CLI)
import torch  # noqa: E402
import gpytorch  # noqa: E402
from scipy.stats import spearmanr  # noqa: E402

torch.set_num_threads(4)

ARMS = (16, 32, 48)
RHO = 0.05  # augmented Tchebycheff rho (bogp.mobo.qparego.RHO_AUG)


def design_keys(X):
    return {tuple(r) for r in np.round(np.atleast_2d(X), 10).tolist()}


def main():
    led = json.load(open(os.path.join(CAMPAIGN, "analysis", "bo_stage2",
                                      "ledger.json")))
    recs = json.load(open(os.path.join(CAMPAIGN, "analysis", "bo_stage2",
                                       "round_records.json")))
    seed = led["acq_seed_base"] + 1
    assert seed == recs["1"]["acq_seed"] == 20261007
    real = np.asarray(recs["1"]["designs"], float)

    cand = an.lattice_candidates()
    assert cand.shape == (9 ** 6, 6)

    out = {"written_at": datetime.now(timezone.utc).isoformat(
        timespec="seconds"), "acq_seed": seed, "arms": {}}
    batches, scal = {}, {}
    for arm in ARMS:
        X, Y = common.arm_data(arm)
        torch.manual_seed(0)  # the rule acquire_next.main applies
        gps = an.fit_prediction_gps(X, Y)
        with gpytorch.settings.fast_pred_var():
            batch = an.propose_qparego_batch(
                X, Y, q=8, candidates=cand, seed=seed)
        designs = np.asarray(batch["x_batch"], float)
        an.assert_on_lattice(designs)
        batches[arm] = designs
        out["arms"][str(arm)] = {
            "designs": designs.tolist(),
            "weights": np.asarray(batch["weights"]).tolist(),
            "overlap_vs_real_r1": len(design_keys(designs)
                                      & design_keys(real)),
        }
        print(f"arm {arm}: overlap vs real bo_C_r1 = "
              f"{out['arms'][str(arm)]['overlap_vs_real_r1']}/8")

        # scalarized posterior mean over the full lattice (preregistered)
        mus = np.empty((len(cand), 3))
        for j in range(3):
            parts = []
            for chunk in np.array_split(cand, 27):
                parts.append(gps[j].predict(chunk)[0])
            mus[:, j] = np.concatenate(parts)
        ideal, nadir = Y.min(axis=0), Y.max(axis=0)
        span = np.where((nadir - ideal) <= 0, 1.0, nadir - ideal)
        mn = (mus - ideal) / span
        rng = np.random.default_rng(seed)
        W = rng.dirichlet(np.ones(3), size=8)  # the r1 weight rule
        assert np.allclose(W, np.asarray(batch["weights"]), atol=1e-12)
        g = np.empty((len(cand), 8))
        for k in range(8):
            wy = W[k] * mn
            g[:, k] = wy.max(axis=1) + RHO * wy.sum(axis=1)
        scal[arm] = g

    # pairwise batch overlap between arms
    out["pairwise_batch_overlap"] = {}
    for a in ARMS:
        for b in ARMS:
            if a < b:
                ov = len(design_keys(batches[a]) & design_keys(batches[b]))
                out["pairwise_batch_overlap"][f"{a}-{b}"] = ov
                print(f"batch overlap {a} vs {b}: {ov}/8")

    # Spearman of the scalarized posterior mean over the lattice
    out["spearman_scalarized"] = {}
    for a in ARMS:
        for b in ARMS:
            if a < b:
                rs = [float(spearmanr(scal[a][:, k], scal[b][:, k]).statistic)
                      for k in range(8)]
                out["spearman_scalarized"][f"{a}-{b}"] = {
                    "mean": round(float(np.mean(rs)), 4),
                    "min": round(min(rs), 4), "max": round(max(rs), 4),
                    "per_weight": [round(v, 4) for v in rs]}
                print(f"spearman {a}-{b}: mean {np.mean(rs):.4f} "
                      f"range [{min(rs):.4f}, {max(rs):.4f}]")

    with open(os.path.join(HERE, "replay_r1.json"), "w") as f:
        json.dump(out, f, indent=2)
        f.write("\n")
    print("replay_r1.json written")


if __name__ == "__main__":
    main()
