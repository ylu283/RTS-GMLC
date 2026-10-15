"""Prompt 39 E0: extend the PI's LOO table (pi_1008) from 16/32 to 48 with
the IDENTICAL sklearn recipe (analysis/stage2/n0_refresh_32.ipynb cell 3 /
stage2_quicklook.ipynb cell 9, verbatim), metrics and floors. The 16/32
columns must reproduce n0_gp_loo.csv and n0_32pt_gp_loo.csv before the 48
column is added. Pure LOO — zero holdout contact. Writes e0_table.csv.
"""
import os
import sys
import warnings

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
CAMPAIGN = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, CAMPAIGN)

from sklearn.gaussian_process import GaussianProcessRegressor  # noqa: E402
from sklearn.gaussian_process.kernels import (  # noqa: E402
    ConstantKernel, Matern, WhiteKernel)
from sklearn.exceptions import ConvergenceWarning  # noqa: E402

from tiers import TIERS  # noqa: E402

OBJ_COLS = ["load_shed_mwh", "true_curtailment_mwh", "total_cost_raw_usd",
            "total_cost_less_synthetic_usd", "reserve_shortfall_mwh",
            "thermal_starts"]
FLOORS = {"load_shed_mwh": 3000.0, "true_curtailment_mwh": 5000.0,
          "total_cost_raw_usd": 0.5e6, "total_cost_less_synthetic_usd": 0.5e6,
          "reserve_shortfall_mwh": None, "thermal_starts": None}
SORTED_TIERS = sorted(TIERS)


def load_wave(name):
    wdir = os.path.join(CAMPAIGN, "waves", name)
    dm = pd.read_csv(os.path.join(wdir, "design_matrix.csv"))
    ob = pd.read_csv(os.path.join(wdir, "objectives.csv"))
    return dm.merge(ob[["index"] + OBJ_COLS], on="index", validate="1:1")


def loo_preds(X, y, seed=0):
    """VERBATIM pi_1008 recipe (n0_refresh_32.ipynb cell 3)."""
    n = len(y)
    preds = np.empty(n)
    for i in range(n):
        tr = np.arange(n) != i
        Xtr, ytr = X[tr], y[tr]
        lo = Xtr.min(axis=0)
        span = np.where((Xtr.max(0) - lo) <= 0, 1.0, Xtr.max(0) - lo)
        kernel = (ConstantKernel(1.0, (1e-3, 1e3))
                  * Matern(length_scale=np.ones(X.shape[1]),
                           length_scale_bounds=(1e-2, 1e1), nu=2.5)
                  + WhiteKernel(1e-4, (1e-6, 1e0)))
        gpr = GaussianProcessRegressor(kernel=kernel, normalize_y=True,
                                       n_restarts_optimizer=1,
                                       random_state=seed, alpha=1e-8)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", ConvergenceWarning)
            gpr.fit((Xtr - lo) / span, ytr)
        preds[i] = gpr.predict(((X[i] - lo) / span).reshape(1, -1))[0]
    return preds


def loo_stats(X, y):
    p = loo_preds(X, y)
    rmse = float(np.sqrt(np.mean((p - y) ** 2)))
    r2 = float(1 - np.sum((p - y) ** 2) / np.sum((y - y.mean()) ** 2))
    return rmse, r2


def main():
    n0 = load_wave("stage2_C_n0")
    n0b = load_wave("stage2_C_n0b")
    q1 = load_wave("methods_C_Q1")
    assert len(n0) == 16 and len(n0b) == 16 and len(q1) == 16
    cols = [f"{t}_omega" for t in SORTED_TIERS]
    arms = {16: n0, 32: pd.concat([n0, n0b], ignore_index=True),
            48: pd.concat([n0, n0b, q1], ignore_index=True)}

    rec16 = pd.read_csv(os.path.join(CAMPAIGN, "analysis", "stage2",
                                     "n0_gp_loo.csv")).set_index("objective")
    rec32 = pd.read_csv(os.path.join(
        CAMPAIGN, "analysis", "stage2",
        "n0_32pt_gp_loo.csv")).set_index("objective")

    rows = []
    worst_rel = 0.0
    for obj in OBJ_COLS:
        row = {"objective": obj}
        for arm, df in arms.items():
            X = df[cols].to_numpy(float)
            y = df[obj].to_numpy(float)
            rmse, r2 = loo_stats(X, y)
            row[f"loo_rmse_{arm}"] = rmse
            row[f"loo_R2_{arm}"] = r2
            if FLOORS[obj]:
                row[f"rmse_over_floor_{arm}"] = rmse / FLOORS[obj]
        # reproduction asserts BEFORE trusting the 48 column
        for rec, arm, k_rmse, k_r2 in ((rec16, 16, "loo_rmse", "loo_R2"),
                                       (rec32, 32, "loo_rmse_32",
                                        "loo_R2_32")):
            dr = abs(row[f"loo_rmse_{arm}"] - rec.loc[obj, k_rmse]) \
                / rec.loc[obj, k_rmse]
            d2 = abs(row[f"loo_R2_{arm}"] - rec.loc[obj, k_r2])
            worst_rel = max(worst_rel, dr, d2)
            assert dr < 1e-6 and d2 < 1e-6, (obj, arm, dr, d2)
        rows.append(row)
        f = FLOORS[obj]
        if f:
            print(f"{obj:32s} rmse/floor {row['rmse_over_floor_16']:7.2f} -> "
                  f"{row['rmse_over_floor_32']:6.2f} -> "
                  f"{row['rmse_over_floor_48']:6.2f}   R2 "
                  f"{row['loo_R2_16']:.3f} -> {row['loo_R2_32']:.3f} -> "
                  f"{row['loo_R2_48']:.3f}")
        else:
            print(f"{obj:32s} rmse {row['loo_rmse_16']:10.1f} -> "
                  f"{row['loo_rmse_32']:10.1f} -> {row['loo_rmse_48']:10.1f}"
                  f"   R2 {row['loo_R2_16']:.3f} -> {row['loo_R2_32']:.3f}"
                  f" -> {row['loo_R2_48']:.3f}")

    print(f"\n16/32 reproduction: worst relative deviation {worst_rel:.2e} "
          "(asserted < 1e-6) — recorded values REPRODUCED")
    pd.DataFrame(rows).to_csv(os.path.join(HERE, "e0_table.csv"), index=False)
    print("e0_table.csv written")


if __name__ == "__main__":
    main()
