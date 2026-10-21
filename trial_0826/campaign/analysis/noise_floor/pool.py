"""Prompt 40 Part A: the pooled scenario-C design set (read-only).

Pool (prompt 40 §2): every scenario-C 6-d run with objectives. Grid waves
(sweep_C, contour_303x317_C, pairgrid_*_C) carry BLANK unswept tiers =
unretrofitted; they are encoded as omega = 0.0 for the distance computation.
These points sit off the 0.05-floor lattice. Excluded: scenario A/B,
screening (d = 14, pre-C), stage2_backfill_C (NaN omegas), and waves with no
objectives yet (methods_C_P2_r4, methods_C_P3_r4 at 2026-10-21).
"""
from __future__ import annotations

import glob
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
CAMPAIGN = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, CAMPAIGN)
from tiers import STAGE2_LATTICE, TIERS  # noqa: E402

M_COLS = ["load_shed_mwh", "true_curtailment_mwh",
          "total_cost_less_synthetic_usd"]
SORTED_TIERS = sorted(TIERS)
LAT = np.round(np.asarray(STAGE2_LATTICE, float), 10)
LO, HI = float(LAT.min()), float(LAT.max())

SPACE_FILLING = ["stage2_C_n0", "stage2_C_n0b", "methods_C_Q1", "methods_C_Q2",
                 "methods_C_Q3", "random_C", "methods_C_S2_n0", "methods_C_S3_n0"]
BO_FIXED = ["bo_C_r1", "bo_C_r2"]
BO_PATTERNS = ["methods_C_P1_r*", "methods_C_P2_r*", "methods_C_P3_r*",
               "methods_C_N1_r*"]
GRID = ["sweep_C", "contour_303x317_C"]
GRID_PATTERNS = ["pairgrid_*_C"]


def _expand(patterns):
    out = []
    for p in patterns:
        out += sorted(os.path.basename(d) for d in
                      glob.glob(os.path.join(CAMPAIGN, "waves", p)))
    return out


def wave_groups():
    bo = BO_FIXED + _expand(BO_PATTERNS)
    grid = GRID + _expand(GRID_PATTERNS)
    assert len(_expand(GRID_PATTERNS)) == 14, _expand(GRID_PATTERNS)
    return {"space_filling": SPACE_FILLING, "bo": bo, "grid": grid}


def load_wave(wave):
    wdir = os.path.join(CAMPAIGN, "waves", wave)
    ob_path = os.path.join(wdir, "objectives.csv")
    if not os.path.isfile(ob_path):
        return None
    dm = pd.read_csv(os.path.join(wdir, "design_matrix.csv"))
    ob = pd.read_csv(ob_path)
    df = dm.merge(ob[["index"] + M_COLS], on="index", validate="1:1")
    assert (df["rho_h2"] == 2.0).all(), wave                      # scenario C
    bids = df[[f"{t}_bid" for t in SORTED_TIERS]].to_numpy(float)
    assert np.all(np.isnan(bids) | (bids == 40.0)), wave          # B = 40
    om = df[[f"{t}_omega" for t in SORTED_TIERS]].to_numpy(float)
    blank = np.isnan(om)
    out = pd.DataFrame({"wave": wave, "index": df["index"].to_numpy()})
    for j, t in enumerate(SORTED_TIERS):
        out[f"{t}_omega"] = np.where(blank[:, j], 0.0, om[:, j])
    out["n_blank"] = blank.sum(axis=1)
    for c in M_COLS:
        out[c] = df[c].to_numpy(float)
    return out


def load_pool(groups=("space_filling", "bo", "grid"), drop_waves=()):
    g = wave_groups()
    frames, missing = [], []
    for grp in groups:
        for w in g[grp]:
            if w in drop_waves:
                continue
            f = load_wave(w)
            if f is None:
                missing.append(w)
                continue
            f["group"] = grp
            frames.append(f)
    df = pd.concat(frames, ignore_index=True)
    ok = np.isfinite(df[M_COLS].to_numpy()).all(axis=1)
    df = df[ok].reset_index(drop=True)
    return df, missing


def normalized_X(df):
    X = df[[f"{t}_omega" for t in SORTED_TIERS]].to_numpy(float)
    return (X - LO) / (HI - LO)


def pairs_below(Xn, h_max):
    """All i<j pairs with 0 <= h < h_max (blockwise, memory-safe)."""
    n = len(Xn)
    I, J, H = [], [], []
    for a in range(0, n, 512):
        d = np.sqrt(((Xn[a:a + 512, None, :] - Xn[None, :, :]) ** 2).sum(-1))
        ii, jj = np.nonzero(d < h_max)
        ii = ii + a
        keep = jj > ii
        I.append(ii[keep]); J.append(jj[keep]); H.append(d[ii[keep] - a, jj[keep]])
    return np.concatenate(I), np.concatenate(J), np.concatenate(H)
