"""Prompt 39 H-BO cell: refit the default AND the Part-H winner on the
BO-augmented set (32 starts + bo_C_r1 + bo_C_r2, n = 48), predict the 8
methods_C_P1_r3 designs, compute the same z-stats as the r3 audit
(mean_z / rms_z / cov95, noise-inclusive sd). Descriptive; zero holdout
contact; zero PCM runs. Writes hbo_cell.json.
"""
import json
import os
from datetime import datetime, timezone

import numpy as np
import torch

import common
from common import DEFAULT_CFG, FLOORS, M_COLS, SHORT, FlexGP

HERE = os.path.dirname(os.path.abspath(__file__))

R3_AUDIT = {  # P1 round_records.json r3 (recorded; cite-not-rederive)
    "load_shed_mwh": {"mean_z": 0.731, "rms_z": 1.706, "cov95": 7},
    "true_curtailment_mwh": {"mean_z": 1.426, "rms_z": 2.008, "cov95": 5},
    "total_cost_less_synthetic_usd": {"mean_z": -0.751, "rms_z": 0.829,
                                      "cov95": 8},
}


def zstats(y, mu_t, sd_t, transform):
    t_true = common.to_t(y, transform)
    z = (t_true - mu_t) / sd_t
    return {"mean_z": round(float(z.mean()), 3),
            "rms_z": round(float(np.sqrt((z ** 2).mean())), 3),
            "cov95": int((np.abs(z) <= 1.96).sum())}


def main():
    winners = json.load(open(os.path.join(HERE, "fits.json")))["winners"]
    X, Y = common.bo_augmented_data()
    Xq, Yq = common.load_wave_xy("methods_C_P1_r3")
    assert Xq.shape == (8, 6)

    out = {"written_at": datetime.now(timezone.utc).isoformat(
        timespec="seconds"),
        "train": "stage2_C_n0 + n0b + bo_C_r1 + bo_C_r2 (n=48)",
        "test": "methods_C_P1_r3 (8 BO-selected designs)",
        "r3_audit_recorded": R3_AUDIT, "cells": {}}
    for j, col in enumerate(M_COLS):
        wcfg = tuple(winners[col]["config"])
        cell = {}
        for role, cfg in (("default", DEFAULT_CFG), ("winner", wcfg)):
            torch.manual_seed(0)
            gp = FlexGP(X, Y[:, j], FLOORS[col], cfg)
            mu, sd = gp.predict_t(Xq)
            s = zstats(Yq[:, j], mu, sd, cfg[1])
            pred_med = common.median_raw(mu, cfg[1])
            s["rmse_over_floor"] = round(float(np.sqrt(np.mean(
                (pred_med - Yq[:, j]) ** 2))) / FLOORS[col], 3)
            cell[role] = {"config": winners[col]["config_name"]
                          if role == "winner" else "default", **s}
            print(f"{SHORT[col]:8s} {role:8s} mean_z {s['mean_z']:7.3f}  "
                  f"rms_z {s['rms_z']:6.3f}  cov95 {s['cov95']}/8  "
                  f"rmse/floor {s['rmse_over_floor']:7.3f}")
        out["cells"][col] = cell

    # sanity: default cell should resemble the recorded r3 audit (same
    # training set + model family; the audit GP was fit at r3 proposal time)
    with open(os.path.join(HERE, "hbo_cell.json"), "w") as f:
        json.dump(out, f, indent=2)
        f.write("\n")
    print("hbo_cell.json written")


if __name__ == "__main__":
    main()
