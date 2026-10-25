"""Prompt 43 Phase-B selection (S6): 12 fits (8 competing + 4 reference)
on the n0 = 32 training arm ONLY; closed-form LOO; rank by LOO NLPD in
original units with the part_h.py:163-169 tie walk over the 8 competing
arms; a separate 12-arm walk is the STOP-FOR-DECISION trigger.

This script never reads the frozen holdout and contains no reference to
it. Writes loo_table.csv, loo_predictions.csv, winner_commit.json
(winner config, LOO-table sha256, UTC timestamp), convergence_log.csv.
On STOP-FOR-DECISION it writes STOP_FOR_DECISION.json INSTEAD of
winner_commit.json, so grading cannot run.

Run: /opt/anaconda3/envs/bogp-botorch/bin/python select.py
"""
from __future__ import annotations

# --- path hygiene: this file's pinned name shadows the stdlib `select`
# module. Pre-cache the stdlib module with the script dir off sys.path,
# then restore it (mechanical; recorded in PHASE_B.md deviations).
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


def tie_walk(cands, stats):
    """part_h.py:163-169 semantics verbatim: sort by (nlpd, rmse, idx);
    the 0.02-nat window is relative to the CURRENT leader, chained hops
    allowed; an arm inside the window with strictly lower RMSE takes
    the win."""
    order = sorted(cands, key=lambda a: (stats[a]["nlpd"],
                                         stats[a]["rmse"],
                                         stats[a]["idx"]))
    top = order[0]
    for c in order[1:]:
        if stats[c]["nlpd"] <= stats[top]["nlpd"] + 0.02 \
                and stats[c]["rmse"] < stats[top]["rmse"]:
            top = c
    return top, order


def main():
    assert common.nlpd_unit_test() < 1e-5
    X, Y = common.arm_data(32)
    assert X.shape == (32, 6)
    y = Y[:, pb.J_OBJ]
    # structural disclosure checks (S3): no HIGH-stratum training point
    strat = pb.stratum(y)
    counts = {s: int((strat == s).sum()) for s in ("LOW", "MID", "HIGH")}
    assert counts == {"LOW": 14, "MID": 18, "HIGH": 0}, counts
    assert y.max() < pb.STRATA_BOUNDS[1], y.max()
    print(f"train-32 strata {counts}  max shed {y.max():,.0f} MWh "
          f"(< 15,000: selection cannot test the HIGH-stratum noise)")

    conv_log, rows, pred_rows = [], [], []
    stats = {}          # name -> dict for the tie walks
    nlpd_pt = {}        # name -> per-point NLPD vector (paired deltas)
    ut_results = {}
    for arm in pb.ARMS:
        gp, converged, info = pb.fit_phaseb(X, y, arm, "loo_n32", 32,
                                            conv_log)
        if gp is None:
            print(f"{arm.name:16s} FAILED: {info['fit_error']}")
            rows.append({"idx": arm.idx, "config": arm.name,
                         "kernel": arm.kernel, "transform": arm.transform,
                         "noise_form": arm.form,
                         "reference": arm.reference, "status": "FAILED",
                         "converged": False, "eligible": False,
                         "fit_error": info["fit_error"]})
            continue
        mu_t, sd_t = pb.loo_closed_form(gp)
        wmu, wsd = pb.loo_unit_test(gp, mu_t, sd_t)   # pinned indices
        ut_results[arm.name] = (wmu, wsd)
        m, z = common.metrics(y, mu_t, sd_t, arm.transform,
                              floor=pb.POOLED_SD)
        pt = pb.nlpd_pointwise(y, mu_t, sd_t, arm.transform)
        assert abs(pt.mean() - m["nlpd"]) <= 1e-9, "NLPD defs disagree"
        nlpd_pt[arm.name] = pt
        rms_z = {s: float(np.sqrt(np.mean(z[strat == s] ** 2)))
                 if (strat == s).any() else float("nan")
                 for s in ("LOW", "MID", "HIGH")}
        eligible = converged and not arm.reference
        row = {
            "idx": arm.idx, "config": arm.name, "kernel": arm.kernel,
            "transform": arm.transform, "noise_form": arm.form,
            "reference": arm.reference,
            "status": "ok" if converged else "FLAGGED_unconverged",
            "converged": converged, "eligible": eligible,
            "extended_to_10000": info["extended"],
            "dloss100_at_5000": info["d5000"],
            "dloss100_final": info["dfinal"],
            "jitter_retry": info["jitter_retry"],
            "loo_nlpd": m["nlpd"], "loo_rmse": m["rmse"],
            "rmse_over_pooled_sd": m["rmse_over_floor"],  # relabeled
            "loo_cov95": m["cov95"], "loo_rms_z": m["rms_z"],
            "mean_z": m["mean_z"], "spearman": m["spearman"],
            "r2": m["r2"],
            "rms_z_low": rms_z["LOW"], "rms_z_mid": rms_z["MID"],
            "rms_z_high": rms_z["HIGH"],
            "jitter_raw_equiv_mwh": gp.jitter_raw_mwh,
            "unit_test_max_dmu_over_sy": wmu,
            "unit_test_max_dsd_rel": wsd,
            "fit_error": ""}
        rows.append(row)
        if eligible or arm.reference:
            stats[arm.name] = {"nlpd": m["nlpd"], "rmse": m["rmse"],
                               "idx": arm.idx, "reference": arm.reference,
                               "converged": converged}
        lo, hi = pb.band_raw(gp, mu_t, sd_t)
        med = common.median_raw(mu_t, arm.transform)
        for q in range(len(y)):
            pred_rows.append({"config": arm.name, "i": q, "actual": y[q],
                              "loo_mu_t": mu_t[q], "loo_sd_t": sd_t[q],
                              "loo_median_raw": med[q],
                              "lo_raw": lo[q], "hi_raw": hi[q],
                              "stratum": strat[q]})
        print(f"{arm.name:16s} nlpd {m['nlpd']:8.3f}  rmse {m['rmse']:9.1f}"
              f"  cov95 {m['cov95']:2d}/32  rms_z {m['rms_z']:6.2f} "
              f" (LOW {rms_z['LOW']:.2f} MID {rms_z['MID']:.2f})"
              f"  conv {converged} ext {info['extended']}"
              f"  jitter_raw {gp.jitter_raw_mwh:.2e} MWh"
              f"  ut dmu/sy {wmu:.1e} dsd {wsd:.1e}")

    # ---- tie walks (S6): converged arms only (unconverged ineligible)
    competing = [n for n, s in stats.items()
                 if not s["reference"] and s["converged"]]
    all_conv = [n for n, s in stats.items() if s["converged"]]
    assert competing, "no converged competing arm"
    winner, order8 = tie_walk(competing, stats)
    crowned12, order12 = tie_walk(all_conv, stats)
    best = stats[order8[0]]
    within = [n for n in order8
              if stats[n]["nlpd"] <= best["nlpd"] + 0.02]
    stop_for_decision = stats[crowned12]["reference"]

    # paired per-point delta-NLPD vs the crowned competing winner
    for row in rows:
        nm = row["config"]
        if nm in nlpd_pt and winner in nlpd_pt:
            d = nlpd_pt[nm] - nlpd_pt[winner]
            row["dnlpd_vs_winner"] = float(d.mean())
            row["dnlpd_se_vs_winner"] = float(d.std(ddof=1)
                                              / np.sqrt(len(d)))

    tab = pd.DataFrame(rows).sort_values(
        ["loo_nlpd", "loo_rmse", "idx"], na_position="last")
    tab.insert(0, "rank", range(1, len(tab) + 1))
    tab["winner"] = tab["config"] == winner
    tab.to_csv(os.path.join(HERE, "loo_table.csv"), index=False)
    pd.DataFrame(pred_rows).to_csv(
        os.path.join(HERE, "loo_predictions.csv"), index=False)
    pd.DataFrame(conv_log).to_csv(
        os.path.join(HERE, "convergence_log.csv"), index=False)

    with open(os.path.join(HERE, "loo_table.csv"), "rb") as fh:
        table_hash = hashlib.sha256(fh.read()).hexdigest()

    walks = {"walk8_winner": winner,
             "walk8_order": order8,
             "walk8_within_0.02_of_best": within,
             "walk8_rmse_rule_changed_winner": winner != order8[0],
             "walk12_crowned": crowned12,
             "walk12_order": order12,
             "stop_for_decision": stop_for_decision,
             "note": "0.02-nat window is a pinned convention, not a "
                     "significance claim"}

    if stop_for_decision:
        out = {"STOP_FOR_DECISION": True,
               "reason": "the 12-arm tie walk crowned a reference "
                         "(homoscedastic 285.3) arm; spending the one "
                         "holdout scoring on the rejected scalar framing "
                         "requires Kay's sign-off",
               "walks": walks, "loo_table_sha256": table_hash,
               "committed_at_utc": datetime.now(timezone.utc).isoformat(
                   timespec="seconds")}
        with open(os.path.join(HERE, "STOP_FOR_DECISION.json"), "w") as fh:
            json.dump(out, fh, indent=2)
            fh.write("\n")
        print("\nSTOP-FOR-DECISION: 12-arm walk crowned reference arm "
              f"{crowned12}. winner_commit.json NOT written; the frozen "
              "holdout stays untouched.")
        return

    warm = next(r for r in rows if r["config"] == winner)
    commit = {"winner": {"name": winner, "kernel": warm["kernel"],
                         "transform": warm["transform"],
                         "noise_form": warm["noise_form"],
                         "idx": warm["idx"]},
              "selection": walks,
              "loo_table_sha256": table_hash,
              "committed_at_utc": datetime.now(timezone.utc).isoformat(
                  timespec="seconds")}
    with open(os.path.join(HERE, "winner_commit.json"), "w") as fh:
        json.dump(commit, fh, indent=2)
        fh.write("\n")
    print(f"\nWINNER (8-arm walk): {winner}   "
          f"(nlpd argmin {order8[0]}; within 0.02: {within}; "
          f"rmse rule changed winner: {winner != order8[0]})")
    print(f"12-arm walk crowned: {crowned12} (reference: "
          f"{stats[crowned12]['reference']})")
    print("winner_commit.json written; loo_table sha256", table_hash)


if __name__ == "__main__":
    main()
