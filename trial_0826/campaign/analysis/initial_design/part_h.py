"""Prompt 39 Part H: pre-registered hyperparameter study, LOOCV on the 32
starts ONLY. No holdout contact in this script.

Main-effects set per objective (default + one change at a time), then the
best-combination fit. Winner rule (pre-registered in PROGRESS.md 07:32Z):
primary = LOO NLPD in original units; ties within 0.02 nats break by LOO
RMSE. Writes part_h_loocv.csv and fits.json (the winner commitment).
"""
import itertools
import json
import os
from datetime import datetime, timezone

import numpy as np
import pandas as pd
import torch

import common
from common import DEFAULT_CFG, FLOORS, M_COLS, SHORT, FlexGP

HERE = os.path.dirname(os.path.abspath(__file__))

AXES = {  # axis -> non-default levels
    "kernel": ["m32", "rbf"],
    "transform": ["log1p"],          # shed and curtailment only
    "noise": ["fixed"],
    "prior": ["gamma"],
}
AXIS_POS = {"kernel": 0, "transform": 1, "noise": 2, "prior": 3}


def cfg_name(cfg):
    k, t, n, p = cfg
    bits = []
    if k != "m52":
        bits.append(k)
    if t != "std":
        bits.append(t)
    if n != "inferred":
        bits.append("fixnoise")
    if p != "none":
        bits.append("gammaprior")
    return "default" if not bits else "+".join(bits)


def fit_and_score(X, y, col, cfg):
    torch.manual_seed(0)
    gp = FlexGP(X, y, FLOORS[col], cfg)
    mu, sd, t_true = gp.loo_t()
    y_raw = y  # original units
    m, z = common.metrics(y_raw, mu, sd, cfg[1], FLOORS[col])
    hyp = {
        "lengthscales": [round(float(v), 6) for v in
                         gp.model.covar_module.base_kernel.lengthscale
                         .detach().numpy().ravel()],
        "outputscale": round(float(gp.model.covar_module.outputscale
                                   .detach()), 6),
        "noise_std": round(float(gp.lik.noise) ** 0.5, 6),
        "noise_floor_std": round(gp.floor_var ** 0.5, 6),
        "mean_const": round(float(gp.model.mean_module.constant), 6),
    }
    return m, hyp


def main():
    X, Y = common.arm_data(32)
    band = common.binom_band(32)
    print(f"LOO cov95 95% binomial band at n=32, p=0.95: {band}")

    fits = {"created_at": datetime.now(timezone.utc).isoformat(
        timespec="seconds"),
        "selection_rule": "primary LOO NLPD (original units); ties within "
                          "0.02 nats -> LOO RMSE. Pre-registered "
                          "PROGRESS.md 2026-10-15T07:32Z.",
        "torch_seed": 0, "n_train": 32, "fits": []}
    rows = []

    winners = {}
    for j, col in enumerate(M_COLS):
        y = Y[:, j]
        configs = [DEFAULT_CFG]
        for ax, levels in AXES.items():
            if ax == "transform" and col == "total_cost_less_synthetic_usd":
                continue  # log1p is shed/curt only (and cost_ls can be < 0)
            for lv in levels:
                c = list(DEFAULT_CFG)
                c[AXIS_POS[ax]] = lv
                configs.append(tuple(c))

        scored = {}
        for cfg in configs:
            m, hyp = fit_and_score(X, y, col, cfg)
            scored[cfg] = m
            rows.append({"objective": SHORT[col], "config": cfg_name(cfg),
                         "stage": "main_effects", **m})
            fits["fits"].append({"objective": col, "config": list(cfg),
                                 "config_name": cfg_name(cfg),
                                 "stage": "main_effects",
                                 "loocv": m, "hyperparameters": hyp})
            print(f"{SHORT[col]:8s} {cfg_name(cfg):22s} "
                  f"rmse/floor {m['rmse_over_floor']:7.3f}  "
                  f"nlpd {m['nlpd']:8.3f}  rms_z {m['rms_z']:5.2f}  "
                  f"cov95 {m['cov95']}/32")

        # best combination: every axis level that beats default on primary
        d_nlpd = scored[DEFAULT_CFG]["nlpd"]
        combo = list(DEFAULT_CFG)
        for cfg, m in scored.items():
            if cfg == DEFAULT_CFG or m["nlpd"] >= d_nlpd:
                continue
            diff = [i for i in range(4) if cfg[i] != DEFAULT_CFG[i]]
            assert len(diff) == 1
            i = diff[0]
            if combo[i] == DEFAULT_CFG[i]:
                combo[i] = cfg[i]
            else:  # two levels of the same axis both beat default: keep better
                alt = list(DEFAULT_CFG); alt[i] = combo[i]
                if m["nlpd"] < scored[tuple(alt)]["nlpd"]:
                    combo[i] = cfg[i]
        combo = tuple(combo)
        if combo not in scored:
            m, hyp = fit_and_score(X, y, col, combo)
            scored[combo] = m
            rows.append({"objective": SHORT[col], "config": cfg_name(combo),
                         "stage": "best_combo", **m})
            fits["fits"].append({"objective": col, "config": list(combo),
                                 "config_name": cfg_name(combo),
                                 "stage": "best_combo",
                                 "loocv": m, "hyperparameters": hyp})
            print(f"{SHORT[col]:8s} {cfg_name(combo):22s} "
                  f"rmse/floor {m['rmse_over_floor']:7.3f}  "
                  f"nlpd {m['nlpd']:8.3f}  rms_z {m['rms_z']:5.2f}  "
                  f"cov95 {m['cov95']}/32   [combo]")

        # interaction check (pre-registration item 3): combo worse than the
        # best single-change config -> run pairwise crosses of beneficial axes
        singles = {c: m for c, m in scored.items() if c != combo}
        best_single = min(singles, key=lambda c: singles[c]["nlpd"])
        extra_note = ""
        if scored[combo]["nlpd"] > singles[best_single]["nlpd"] + 1e-9 \
                and combo != best_single:
            ben_axes = [i for i in range(4) if combo[i] != DEFAULT_CFG[i]]
            if len(ben_axes) > 2:
                extra_note = "interaction: ran pairwise crosses"
                for i, k in itertools.combinations(ben_axes, 2):
                    c = list(DEFAULT_CFG); c[i] = combo[i]; c[k] = combo[k]
                    c = tuple(c)
                    if c in scored:
                        continue
                    m, hyp = fit_and_score(X, y, col, c)
                    scored[c] = m
                    rows.append({"objective": SHORT[col],
                                 "config": cfg_name(c),
                                 "stage": "pairwise_cross", **m})
                    fits["fits"].append({"objective": col, "config": list(c),
                                         "config_name": cfg_name(c),
                                         "stage": "pairwise_cross",
                                         "loocv": m, "hyperparameters": hyp})
                    print(f"{SHORT[col]:8s} {cfg_name(c):22s} "
                          f"nlpd {m['nlpd']:8.3f}   [cross]")

        # winner per pre-registered rule
        order = sorted(scored, key=lambda c: (scored[c]["nlpd"],
                                              scored[c]["rmse"]))
        top = order[0]
        for c in order[1:]:
            if scored[c]["nlpd"] <= scored[top]["nlpd"] + 0.02 \
                    and scored[c]["rmse"] < scored[top]["rmse"]:
                top = c
        winners[col] = {"config": list(top), "config_name": cfg_name(top),
                        "loocv": scored[top],
                        "loocv_default": scored[DEFAULT_CFG],
                        "note": extra_note}
        print(f"--> {SHORT[col]} WINNER: {cfg_name(top)}  "
              f"(nlpd {scored[top]['nlpd']:.3f} vs default "
              f"{scored[DEFAULT_CFG]['nlpd']:.3f})\n")

    fits["loo_cov95_band_n32"] = list(band)
    fits["winners"] = winners
    fits["winner_committed_at"] = datetime.now(timezone.utc).isoformat(
        timespec="seconds")
    with open(os.path.join(HERE, "fits.json"), "w") as f:
        json.dump(fits, f, indent=2)
        f.write("\n")
    pd.DataFrame(rows).to_csv(os.path.join(HERE, "part_h_loocv.csv"),
                              index=False)
    print("fits.json + part_h_loocv.csv written; winner committed at",
          fits["winner_committed_at"])


if __name__ == "__main__":
    main()
