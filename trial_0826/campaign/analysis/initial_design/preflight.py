"""Prompt 39 §3 pre-flight asserts. Read-only; writes nothing outside stdout.

(i)   regenerate Sobol draws 1-48 from seed 20260821; assert pre-snap
      equality with the three waves' snap_map.json bit-for-bit;
(ii)  assert the snapped designs equal the stage2_C_n0 / stage2_C_n0b /
      methods_C_Q1 design matrices;
(iii) read skip values from the manifests (n_drawn_total), never literals;
(iv)  assert zero design overlap between the 48-point train set and the
      holdout, keyed by lattice indices.
"""
import json
import os
import sys

import numpy as np
import pandas as pd
from scipy.stats import qmc

HERE = os.path.dirname(os.path.abspath(__file__))
CAMPAIGN = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, CAMPAIGN)

from tiers import TIERS, STAGE2_LATTICE, SOBOL_SEED  # noqa: E402

LAT = np.round(np.asarray(STAGE2_LATTICE, float), 10)
LO, HI = float(LAT[0]), float(LAT[-1])
TIER_ORDER = list(TIERS)            # snap_map / manifest tier order
SORTED_TIERS = sorted(TIERS)
WAVES = ["stage2_C_n0", "stage2_C_n0b", "methods_C_Q1"]


def wave_path(w, f):
    return os.path.join(CAMPAIGN, "waves", w, f)


def main():
    # (iii) skips from manifests, never literals
    skips, blocks = {}, {}
    prev_total = 0
    for w in WAVES:
        man = json.load(open(wave_path(w, "manifest.json")))["sobol"]
        assert man["seed"] == SOBOL_SEED == 20260821, (w, man["seed"])
        assert man["skip"] == prev_total, (w, man["skip"], prev_total)
        skips[w] = man["skip"]
        blocks[w] = man["n"]
        prev_total = man["n_drawn_total"]
        print(f"(iii) {w}: skip={man['skip']} n={man['n']} "
              f"n_drawn_total={man['n_drawn_total']}  OK")
    assert prev_total == 48

    # (i) regenerate draws 1-48 and compare bit-for-bit with snap_map pre_snap
    eng = qmc.Sobol(6, scramble=True, seed=SOBOL_SEED)
    unit = eng.random(48)
    pre_all = LO + unit * (HI - LO)
    off = 0
    for w in WAVES:
        sm = json.load(open(wave_path(w, "snap_map.json")))
        assert sm["tier_order"] == TIER_ORDER, (w, sm["tier_order"])
        draws = sm["draws"]
        assert len(draws) == blocks[w], (w, len(draws))
        for j, d in enumerate(draws):
            assert d["draw"] == off + j + 1, (w, d["draw"], off + j + 1)
            rec = np.asarray(d["pre_snap"], float)
            gen = pre_all[off + j]
            assert np.array_equal(rec, gen), (
                w, d["draw"], rec - gen)  # bit-for-bit
            assert d["kept_index"] == j + 1, (w, d["draw"], d["kept_index"])
        off += blocks[w]
        print(f"(i)   {w}: {blocks[w]} pre-snap draws bit-identical  OK")

    # (ii) snapped designs equal the design matrices
    def snap(row):
        return np.array([LAT[np.argmin(np.abs(v - LAT))] for v in row])

    off = 0
    for w in WAVES:
        dm = pd.read_csv(wave_path(w, "design_matrix.csv")).sort_values("index")
        X = dm[[f"{t}_omega" for t in TIER_ORDER]].to_numpy(float)
        snapped = np.vstack([snap(r) for r in pre_all[off:off + blocks[w]]])
        assert np.array_equal(np.round(X, 10), np.round(snapped, 10)), w
        # and equal to the recorded post_snap
        sm = json.load(open(wave_path(w, "snap_map.json")))
        post = np.asarray([d["post_snap"] for d in sm["draws"]], float)
        assert np.array_equal(np.round(post, 10), np.round(snapped, 10)), w
        off += blocks[w]
        print(f"(ii)  {w}: snapped designs == design_matrix == snap_map  OK")

    # (iv) zero overlap between the 48-point train set and the holdout,
    # keyed by lattice indices
    def lattice_idx(X):
        out = np.empty(X.shape, dtype=int)
        for i, row in enumerate(np.atleast_2d(X)):
            for j, v in enumerate(row):
                hit = np.flatnonzero(np.isclose(LAT, v, atol=1e-12))
                assert len(hit) == 1, (i, j, v)
                out[i, j] = hit[0]
        return out

    train = []
    for w in WAVES:
        dm = pd.read_csv(wave_path(w, "design_matrix.csv"))
        train.append(dm[[f"{t}_omega" for t in SORTED_TIERS]].to_numpy(float))
    train = np.vstack(train)
    assert train.shape == (48, 6)
    hold = pd.read_csv(wave_path("random_C", "design_matrix.csv"))
    Xh = hold[[f"{t}_omega" for t in SORTED_TIERS]].to_numpy(float)
    assert Xh.shape == (48, 6)
    tkeys = {tuple(r) for r in lattice_idx(train).tolist()}
    hkeys = {tuple(r) for r in lattice_idx(Xh).tolist()}
    assert len(tkeys) == 48 and len(hkeys) == 48, "duplicate designs"
    assert not (tkeys & hkeys), f"train/holdout overlap: {tkeys & hkeys}"
    print("(iv)  48-point train set vs random_C holdout: zero overlap, "
          "48 unique keys each  OK")

    print("ALL PRE-FLIGHT ASSERTS PASS")


if __name__ == "__main__":
    main()
