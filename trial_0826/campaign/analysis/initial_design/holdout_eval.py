"""Prompt 39 holdout pass. Touch budget (pre-registered, PROGRESS 07:32Z
item 7): per objective exactly two configs — the campaign default and the
fits.json winner — each scored once per arm (16/32/48) on waves/random_C,
plus the §3 ribbon supplement (default config, 10 random 16-subsets of the
32, subset seed 20261015). The E2 read reuses the winner's 32-arm scores
(no extra fit). Writes holdout_results.csv, holdout_z.json, ribbon.csv.
Also records each arm's FlexGP LOO (train-side, not a holdout touch) for
the fits ledger.
"""
import json
import os
from datetime import datetime, timezone

import numpy as np
import pandas as pd
import torch

import common
from common import DEFAULT_CFG, FLOORS, M_COLS, SHORT, FlexGP

HERE = os.path.dirname(os.path.abspath(__file__))
RIBBON_SEED = 20261015


def main():
    assert common.nlpd_unit_test() < 1e-5  # §4: unit test before any holdout call
    winners = json.load(open(os.path.join(HERE, "fits.json")))["winners"]

    Xh, Yh = common.load_wave_xy("random_C")
    assert Xh.shape == (48, 6)

    rows, zrec, loo_rows = [], {}, []
    for j, col in enumerate(M_COLS):
        wcfg = tuple(winners[col]["config"])
        configs = [("default", DEFAULT_CFG)]
        if wcfg != DEFAULT_CFG:
            configs.append(("winner", wcfg))
        yh = Yh[:, j]
        y_range = float(yh.max() - yh.min())
        for arm in (16, 32, 48):
            X, Y = common.arm_data(arm)
            for role, cfg in configs:
                torch.manual_seed(0)
                gp = FlexGP(X, Y[:, j], FLOORS[col], cfg)
                mu, sd = gp.predict_t(Xh)
                m, z = common.metrics(yh, mu, sd, cfg[1], FLOORS[col],
                                      y_range=y_range)
                pred_med = common.median_raw(mu, cfg[1])
                # shed supplement (pre-registered)
                if col == "load_shed_mwh":
                    hi = yh > FLOORS[col]
                    m["rmse_above_floor"] = float(np.sqrt(np.mean(
                        (pred_med[hi] - yh[hi]) ** 2)))
                    m["n_above_floor"] = int(hi.sum())
                    m["floor_exceed_acc"] = float(np.mean(
                        (pred_med > FLOORS[col]) == hi))
                rows.append({"objective": SHORT[col], "role": role,
                             "config": "+".join(
                                 c for c in cfg if c not in
                                 ("m52", "std", "inferred", "none"))
                             or "default",
                             "arm": arm, **m})
                zrec[f"{SHORT[col]}|{role}|{arm}"] = [round(float(v), 5)
                                                      for v in z]
                # train-side LOO for the ledger (not a holdout touch)
                lmu, lsd, lt = gp.loo_t()
                lm, _ = common.metrics(Y[:, j], lmu, lsd, cfg[1], FLOORS[col])
                loo_rows.append({"objective": SHORT[col], "role": role,
                                 "arm": arm,
                                 "loo_rmse_over_floor": lm["rmse_over_floor"],
                                 "loo_r2": lm["r2"],
                                 "loo_nlpd": lm["nlpd"],
                                 "loo_rms_z": lm["rms_z"],
                                 "loo_cov95": lm["cov95"]})
                print(f"{SHORT[col]:8s} {role:8s} n0={arm:2d}  "
                      f"rmse/floor {m['rmse_over_floor']:7.3f}  "
                      f"nlpd {m['nlpd']:8.3f}  rms_z {m['rms_z']:5.2f}  "
                      f"cov95 {m['cov95']}/48  rho_s {m['spearman']:.3f}")

    # §3 ribbon: 10 random 16-subsets of the 32, default config
    X32, Y32 = common.arm_data(32)
    rng = np.random.default_rng(RIBBON_SEED)
    rib = []
    for s in range(10):
        idx = rng.choice(32, size=16, replace=False)
        for j, col in enumerate(M_COLS):
            torch.manual_seed(0)
            gp = FlexGP(X32[idx], Y32[idx, j], FLOORS[col], DEFAULT_CFG)
            mu, sd = gp.predict_t(Xh)
            m, _ = common.metrics(Yh[:, j], mu, sd, "std", FLOORS[col])
            lmu, lsd, _ = gp.loo_t()
            lm, _ = common.metrics(Y32[idx, j], lmu, lsd, "std", FLOORS[col])
            rib.append({"subset": s + 1, "objective": SHORT[col],
                        "holdout_rmse": m["rmse"],
                        "holdout_rmse_over_floor": m["rmse_over_floor"],
                        "holdout_nlpd": m["nlpd"],
                        "loo_rmse_over_floor": lm["rmse_over_floor"]})
    ribdf = pd.DataFrame(rib)
    ribdf.to_csv(os.path.join(HERE, "ribbon.csv"), index=False)
    print("\nribbon spread (holdout rmse/floor), by objective:")
    print(ribdf.groupby("objective")["holdout_rmse_over_floor"]
          .agg(["min", "median", "max"]).round(3))

    pd.DataFrame(rows).to_csv(os.path.join(HERE, "holdout_results.csv"),
                              index=False)
    pd.DataFrame(loo_rows).to_csv(os.path.join(HERE, "arm_loo_flexgp.csv"),
                                  index=False)
    with open(os.path.join(HERE, "holdout_z.json"), "w") as f:
        json.dump({"written_at": datetime.now(timezone.utc).isoformat(
            timespec="seconds"), "z": zrec}, f)
        f.write("\n")
    print("\nholdout_results.csv, arm_loo_flexgp.csv, ribbon.csv, "
          "holdout_z.json written")


if __name__ == "__main__":
    main()
