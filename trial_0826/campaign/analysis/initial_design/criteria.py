"""Prompt 39 §4 pre-registered evidence criteria E1/E2/E3, computed from
holdout_results.csv, e0_table.csv, fits.json, hbo_cell.json. Writes
criteria.json. No new fits, no holdout contact.
"""
import json
import os
from datetime import datetime, timezone

import pandas as pd

import common
from common import FLOORS, M_COLS, SHORT

HERE = os.path.dirname(os.path.abspath(__file__))
E2_BAND = (43, 48)   # smallest region with >= 95% coverage at n=48, p=0.95



def pick(df, obj, role, arm):
    m = (df["objective"] == obj) & (df["role"] == role) & (df["arm"] == arm)
    sub = df[m]
    assert len(sub) == 1, (obj, role, arm, len(sub))
    return sub.iloc[0]

def improvement(r_a, r_b, floor):
    """I(a->b) with the sub-floor zero rule."""
    if abs(r_a - r_b) < floor:
        return 0.0
    return (r_a - r_b) / r_a


def main():
    hold = pd.read_csv(os.path.join(HERE, "holdout_results.csv"))
    e0 = pd.read_csv(os.path.join(HERE, "e0_table.csv")).set_index(
        "objective")
    hbo = json.load(open(os.path.join(HERE, "hbo_cell.json")))["cells"]
    fits = json.load(open(os.path.join(HERE, "fits.json")))

    out = {"written_at": datetime.now(timezone.utc).isoformat(
        timespec="seconds"), "e2_band": list(E2_BAND)}

    # ---- E1: diminishing returns (per role) ----
    e1 = {}
    for role in ("default", "winner"):
        per, overall_cap_ok, passes = {}, True, 0
        for col in M_COLS:
            s = SHORT[col]
            floor = FLOORS[col]
            r = {a: float(pick(hold, s, role, a)["rmse"])
                 for a in (16, 32, 48)}
            i_16_32 = improvement(r[16], r[32], floor)
            i_32_48 = improvement(r[32], r[48], floor)
            noise_limited = float(e0.loc[col, "rmse_over_floor_32"]) <= 1.0
            if noise_limited:
                ok, rule = True, "noise-limited escape (32-pt LOO <= 1 x floor)"
            elif i_16_32 < 0.05:
                ok, rule = i_32_48 <= 0.10, "flat-curve escape: I(32->48) <= 0.10"
            else:
                ok, rule = i_32_48 <= i_16_32 / 3.0, "I(32->48) <= 1/3 I(16->32)"
            passes += ok
            overall_cap_ok &= (i_32_48 <= 0.25)
            per[s] = {"rmse_16": r[16], "rmse_32": r[32], "rmse_48": r[48],
                      "I_16_32": round(i_16_32, 4),
                      "I_32_48": round(i_32_48, 4),
                      "rule": rule, "pass": bool(ok)}
        e1[role] = {"per_objective": per,
                    "n_pass": int(passes),
                    "cap_I3248_le_025_all": bool(overall_cap_ok),
                    "overall_pass": bool(passes >= 2 and overall_cap_ok)}
    out["E1"] = e1

    # ---- E2: calibration at 32 (judged on the winner; default alongside) --
    e2 = {}
    for role in ("winner", "default"):
        cov = {SHORT[c]: int(pick(hold, SHORT[c], role, 32)["cov95"])
               for c in M_COLS}
        in_band = {k: E2_BAND[0] <= v <= E2_BAND[1] for k, v in cov.items()}
        n_in = sum(in_band.values())
        joint = n_in == 3 or (n_in == 2 and min(cov.values()) == 42)
        e2[role] = {"cov95": cov, "in_band": in_band,
                    "joint_pass": bool(joint)}
    out["E2"] = e2
    out["E2_caveat"] = ("holdout hits share hyperparameters; the binomial "
                        "band is approximate")

    # ---- E3: tuning verdict at 32 + H-BO cell ----
    e3 = {"delta_at_32": {}}
    degrade = False
    for col in M_COLS:
        s = SHORT[col]
        d = pick(hold, s, "default", 32)
        w = pick(hold, s, "winner", 32)
        dn = float(w["nlpd"]) - float(d["nlpd"])
        dc = int(w["cov95"]) - int(d["cov95"])
        e3["delta_at_32"][s] = {"d_nlpd": round(dn, 3), "d_cov95": dc,
                                "winner_cov95": int(w["cov95"])}
        if s in ("shed", "cost_ls"):
            if not (E2_BAND[0] <= int(w["cov95"]) <= E2_BAND[1]) \
                    or dn > 0.1:
                degrade = True
    curt_in = out["E2"]["winner"]["in_band"]["curt"]
    e3["tuning_helps"] = bool(curt_in and not degrade)
    e3["hbo"] = {SHORT[c]: {r: {k: hbo[c][r][k] for k in
                                ("mean_z", "rms_z", "cov95",
                                 "rmse_over_floor")}
                            for r in ("default", "winner")} for c in M_COLS}
    e3["hbo_verdict"] = ("tuned config restores r3 coverage: curt 5/8 -> "
                         f"{hbo['true_curtailment_mwh']['winner']['cov95']}/8,"
                         f" rms_z 2.008 -> "
                         f"{hbo['true_curtailment_mwh']['winner']['rms_z']}")
    out["E3"] = e3

    # ---- winner's-curse gap (LOOCV vs holdout at 32, winner config) ----
    gaps = {}
    for col in M_COLS:
        s = SHORT[col]
        loocv = fits["winners"][col]["loocv"]
        w = pick(hold, s, "winner", 32)
        gaps[s] = {"loo_rmse_over_floor": round(loocv["rmse_over_floor"], 3),
                   "holdout_rmse_over_floor": round(
                       float(w["rmse_over_floor"]), 3),
                   "loo_nlpd": round(loocv["nlpd"], 3),
                   "holdout_nlpd": round(float(w["nlpd"]), 3)}
    out["winner_loocv_vs_holdout"] = gaps

    with open(os.path.join(HERE, "criteria.json"), "w") as f:
        json.dump(out, f, indent=2)
        f.write("\n")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
