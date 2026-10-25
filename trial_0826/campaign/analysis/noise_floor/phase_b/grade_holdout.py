"""Prompt 43 Phase-B final grading (S7, D43-1c) and holdout retirement.

REFUSES to run unless winner_commit.json exists, parses, and its stored
sha256 matches a re-hash of loo_table.csv. Only then loads the frozen
holdout random_C (48 designs). Fits the committed winner at n0 =
16/32/48 (same converged definition) and scores ONCE PER n0 — 3
scorings total; one committed winner, one pass, no second model ever
touches the holdout.

Pinned bar: c1 cov95 in [43, 48] (total band) at every n0; c2a verbatim
sweep_converged.joint_bar() RMSE clause (rmse48 < rmse16 AND rmse32 <=
rmse16); c2b RMSE <= sd_strat = 130.4 MWh at every n0 (recomputed and
asserted; disclosed effectively dead); c3 max/min latent sd >= 2 over
the 48 holdout points at every n0. PASS = c1 AND (c2a OR c2b) AND c3,
evaluated only on converged rows (joint_bar()'s own gate).

Post-verdict CI-endpoint sensitivity (HIGH anchor at 294.6 / 1,939)
from the SAVED predictions only — recorded after the verdict, cannot
change it, no new holdout call.

Writes holdout_final.csv, train_predictions.csv, holdout_verdict.json;
appends to convergence_log.csv.

Run: /opt/anaconda3/envs/bogp-botorch/bin/python grade_holdout.py
"""
from __future__ import annotations

# --- path hygiene: the sibling pinned file select.py shadows the stdlib
# `select` module. Pre-cache the stdlib module with the script dir off
# sys.path, then restore it (mechanical; recorded in PHASE_B.md).
import os  # noqa: E402
import sys  # noqa: E402
_HERE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path = [p for p in sys.path
            if os.path.abspath(p or os.getcwd()) != _HERE_DIR]
import select as _stdlib_select  # noqa: E402,F401
import subprocess  # noqa: E402,F401
sys.path.insert(0, _HERE_DIR)

import hashlib
import json
from datetime import datetime, timezone

import numpy as np
import pandas as pd

import phaseb_common as pb
import common

HERE = os.path.dirname(os.path.abspath(__file__))
N0S = (16, 32, 48)
COV_BAND = (43, 48)                     # campaign-pinned, verbatim
SD_STRAT_PINNED = 130.4
PRIOR_EXPOSURE = 103                    # scorings before this prompt
CI_HIGH = (294.6, 1939.0)               # chi2 95% CI endpoints, HIGH anchor


def refuse(msg):
    print(f"REFUSED: {msg}")
    sys.exit(2)


def load_commit():
    path = os.path.join(HERE, "winner_commit.json")
    if not os.path.exists(path):
        refuse("winner_commit.json does not exist — run select.py first "
               "(or a STOP-FOR-DECISION is open)")
    try:
        with open(path) as fh:
            commit = json.load(fh)
        w = commit["winner"]
        _ = (w["name"], w["kernel"], w["transform"], w["noise_form"])
        stored = commit["loo_table_sha256"]
    except Exception as exc:  # noqa: BLE001
        refuse(f"winner_commit.json does not parse: {exc!r}")
    with open(os.path.join(HERE, "loo_table.csv"), "rb") as fh:
        actual = hashlib.sha256(fh.read()).hexdigest()
    if actual != stored:
        refuse(f"loo_table.csv re-hash {actual} != committed {stored}")
    return commit


def joint_bar(rows, sd_strat):
    """Verbatim sweep_converged.joint_bar() structure with the Phase-B
    c2b (RMSE <= sd_strat) in place of the floor clause."""
    r = {x["n0"]: x for x in rows}
    if not all(x.get("converged") for x in rows):
        return {"pass": False, "c1": False, "c2a": False, "c2b": False,
                "c3": False, "note": "not converged"}
    c1 = all(COV_BAND[0] <= r[n]["cov95"] <= COV_BAND[1] for n in N0S)
    c2a = r[48]["rmse"] < r[16]["rmse"] and r[32]["rmse"] <= r[16]["rmse"]
    c2b = all(r[n]["rmse"] <= sd_strat for n in N0S)
    c3 = all(r[n]["latent_sd_ratio"] >= 2 for n in N0S)
    clause = "a+b" if (c2a and c2b) else ("a" if c2a else
                                          ("b" if c2b else "-"))
    return {"pass": c1 and (c2a or c2b) and c3, "c1": c1, "c2a": c2a,
            "c2b": c2b, "c3": c3, "rmse_clause": clause}


def main():
    commit = load_commit()
    w = commit["winner"]
    arm = next(a for a in pb.ARMS if a.name == w["name"])
    assert (arm.kernel, arm.transform, arm.form) == \
        (w["kernel"], w["transform"], w["noise_form"])
    print(f"hash gate PASS; committed winner: {arm.name}")

    # ---- only now touch the frozen holdout
    Xh, Yh = common.load_wave_xy("random_C")
    assert Xh.shape == (48, 6)
    yh = Yh[:, pb.J_OBJ]
    strat_h = pb.stratum(yh)
    counts = {s: int((strat_h == s).sum()) for s in ("LOW", "MID", "HIGH")}
    assert counts == {"LOW": 18, "MID": 27, "HIGH": 3}, counts
    # c2b bound: model-independent, from OBSERVED holdout shed with the
    # form-(iii) map regardless of winner (S7); recompute and assert
    sd_strat = float(np.sqrt(np.mean(pb.sigma_iii(yh) ** 2)))
    assert abs(sd_strat - SD_STRAT_PINNED) <= 0.05, sd_strat
    print(f"holdout strata {counts}  max shed {yh.max():,.0f} MWh;"
          f"  sd_strat {sd_strat:.1f} MWh (pinned ~130.4; disclosed ex "
          f"ante: c2b is effectively unattainable at campaign-scale RMSE)")
    y_range = float(yh.max() - yh.min())

    conv_log, rows, pts, tr_pts = [], [], [], []
    preds_by_n0 = {}
    for n0 in N0S:
        X, Y = common.arm_data(n0)
        assert X.shape[0] == n0
        ytr = Y[:, pb.J_OBJ]
        gp, converged, info = pb.fit_phaseb(X, ytr, arm, "holdout", n0,
                                            conv_log)
        if gp is None:
            rows.append({"n0": n0, "config": arm.name, "converged": False,
                         "fit_error": info["fit_error"]})
            continue
        p = pb.predict_phaseb(gp, Xh)
        preds_by_n0[n0] = (gp, p)
        lo, hi = pb.band_raw(gp, p["mu_t"], p["total_sd_t"])
        lo_l, hi_l = pb.band_raw(gp, p["mu_t"], p["latent_sd_t"])
        m, z = common.metrics(yh, p["mu_t"], p["total_sd_t"],
                              arm.transform, floor=pb.POOLED_SD,
                              y_range=y_range)
        in_band = (yh >= lo) & (yh <= hi)
        assert int(in_band.sum()) == m["cov95"]
        # optional diagnostic (not a criterion): sigma at OBSERVED y
        jac_obs = (1.0 + yh) if arm.transform == "log1p" \
            else np.ones_like(yh)
        v_obs = (gp.sigma_fn(yh) / (jac_obs * gp.sy)) ** 2 + pb.JITTER_STD
        tot_obs = np.sqrt(p["latent_sd_t"] ** 2 + v_obs * gp.sy ** 2)
        lo_o, hi_o = pb.band_raw(gp, p["mu_t"], tot_obs)
        cov95_obs = int(((yh >= lo_o) & (yh <= hi_o)).sum())
        lat = p["latent_sd_t"]
        ratio = float(lat.max() / max(lat.min(), 1e-9 * lat.max()))
        rows.append({
            "n0": n0, "config": arm.name, "converged": converged,
            "extended_to_10000": info["extended"],
            "jitter_retry": info["jitter_retry"],
            "cov95": m["cov95"], "cov95_sigma_at_obs_diag": cov95_obs,
            "rmse": m["rmse"],
            "rmse_over_pooled_sd": m["rmse_over_floor"],  # relabeled
            "nlpd": m["nlpd"], "rms_z": m["rms_z"],
            "mean_z": m["mean_z"], "spearman": m["spearman"],
            "r2": m["r2"], "latent_sd_ratio": ratio,
            "median_halfwidth_latent_raw":
                float(np.median((hi_l - lo_l) / 2.0)),
            "median_halfwidth_total_raw":
                float(np.median((hi - lo) / 2.0)),
            "sd_strat": sd_strat, "fit_error": ""})
        for q in range(48):
            pts.append({"n0": n0, "i": q, "actual": yh[q],
                        "stratum": strat_h[q],
                        "pred_median_raw": p["median_raw"][q],
                        "mu_t": p["mu_t"][q],
                        "latent_sd_t": p["latent_sd_t"][q],
                        "total_sd_t": p["total_sd_t"][q],
                        "sigma_at_median": p["sigma_at_median"][q],
                        "v_q": p["v_q"][q],
                        "lo_raw": lo[q], "hi_raw": hi[q],
                        "lo_lat_raw": lo_l[q], "hi_lat_raw": hi_l[q],
                        "in_band": bool(in_band[q])})
        # training-point predictions (latent band) for fig1
        ptr = pb.predict_phaseb(gp, X)
        lo_t, hi_t = pb.band_raw(gp, ptr["mu_t"], ptr["latent_sd_t"])
        for q in range(n0):
            tr_pts.append({"n0": n0, "i": q, "actual": ytr[q],
                           "pred_median_raw": ptr["median_raw"][q],
                           "lo_lat_raw": lo_t[q], "hi_lat_raw": hi_t[q]})
        print(f"n0={n0}: conv {converged} ext {info['extended']}  "
              f"cov95 {m['cov95']}/48 (sigma-at-obs {cov95_obs}/48)  "
              f"rmse {m['rmse']:,.0f}  nlpd {m['nlpd']:.3f}  "
              f"latent ratio {ratio:.2f}  half-width lat/tot "
              f"{np.median((hi_l-lo_l)/2):,.0f}/"
              f"{np.median((hi-lo)/2):,.0f} MWh")

    bar = joint_bar(rows, sd_strat)
    print("\nVERDICT:", json.dumps(bar))

    # ---- post-verdict CI-endpoint sensitivity (saved predictions only)
    sens = []
    for s_high in CI_HIGH:
        sd_strat_s = float(np.sqrt(
            np.mean(pb.sigma_iii(yh, s_high) ** 2)))
        srows = []
        for n0 in N0S:
            if n0 not in preds_by_n0:
                continue
            gp, p = preds_by_n0[n0]
            jac = (1.0 + p["median_raw"]) if arm.transform == "log1p" \
                else np.ones_like(p["median_raw"])
            sig = gp.sigma_fn(p["median_raw"], s_high)
            v = (sig / (jac * gp.sy)) ** 2 + pb.JITTER_STD
            tot = np.sqrt(p["latent_sd_t"] ** 2 + v * gp.sy ** 2)
            lo, hi = pb.band_raw(gp, p["mu_t"], tot)
            cov = int(((yh >= lo) & (yh <= hi)).sum())
            r0 = next(r for r in rows if r["n0"] == n0)
            srows.append({"n0": n0, "cov95": cov, "rmse": r0["rmse"],
                          "rmse_le_sd_strat": r0["rmse"] <= sd_strat_s})
        c1s = all(COV_BAND[0] <= r["cov95"] <= COV_BAND[1] for r in srows) \
            and len(srows) == 3
        c2bs = all(r["rmse_le_sd_strat"] for r in srows) and len(srows) == 3
        sens.append({"high_anchor": s_high, "sd_strat": sd_strat_s,
                     "per_n0": srows, "c1": c1s,
                     "c2a": bar.get("c2a"),   # medians unchanged
                     "c2b": c2bs,
                     "note": "recorded AFTER the verdict; cannot change "
                             "it; no new holdout call"})
        print(f"sensitivity HIGH={s_high}: cov95 "
              f"{[r['cov95'] for r in srows]}  c1 {c1s}  "
              f"sd_strat {sd_strat_s:.1f}  c2b {c2bs}")

    pd.DataFrame(pts).to_csv(os.path.join(HERE, "holdout_final.csv"),
                             index=False)
    pd.DataFrame(tr_pts).to_csv(
        os.path.join(HERE, "train_predictions.csv"), index=False)
    clpath = os.path.join(HERE, "convergence_log.csv")
    pd.DataFrame(conv_log).to_csv(
        clpath, index=False, mode="a", header=not os.path.exists(clpath))
    verdict = {"winner": commit["winner"],
               "loo_table_sha256": commit["loo_table_sha256"],
               "graded_at_utc": datetime.now(timezone.utc).isoformat(
                   timespec="seconds"),
               "cov_band": list(COV_BAND), "sd_strat": sd_strat,
               "per_n0": rows, "bar": bar,
               "sensitivity_high_anchor_ci": sens,
               "exposure": {"prior": PRIOR_EXPOSURE, "this_prompt": 3,
                            "total": PRIOR_EXPOSURE + 3},
               "holdout_retired_for_shed_selection": True}
    with open(os.path.join(HERE, "holdout_verdict.json"), "w") as fh:
        json.dump(verdict, fh, indent=2)
        fh.write("\n")
    print(f"\nholdout exposure: {PRIOR_EXPOSURE} + 3 = "
          f"{PRIOR_EXPOSURE + 3} scorings (one per n0). The holdout is "
          f"RETIRED for shed selection.")
    print("PASS" if bar["pass"] else
          "FAIL -> pre-named next steps: targeted high-shed data "
          "(prompt 44 proposal) or form (i) amendment")


if __name__ == "__main__":
    main()
