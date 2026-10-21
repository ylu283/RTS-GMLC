"""Prompt 40 Part C (report-only): per-arm tau at alternative shed floors and
a re-grade of the recorded stop decisions. Ledgers are read-only.

Part A returned ABSTAIN, so per §2 A3 Part C runs as a SENSITIVITY BAND:
shed floor in {300, 3000} MWh (curt / cost floors unchanged 5000 / 0.5e6).
The 3000 row must reproduce each ledger's tau_old exactly (recipe check).

tau recipe = acquire_next.cmd_init / acquire_arm._mc_threshold: N = 1,000
draws, numpy default_rng(20261006), ALL 32 starts perturbed
N(0, floor^2) per objective, no clipping, exact HV, std (ddof 0) of the HV
draws. ref = the arm's ledger-frozen ref point (never recomputed). N1 shares
P1's starts and ref by design. The same seed gives common random numbers
across the two floor settings.

Two-strike rule (acquire_next.run_round / acquire_arm): stop after round k
when gain_k < tau and gain_{k-1} < tau.

Writes ONLY analysis/noise_floor/part_c.json and part_c_regrade.csv.
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
CAMPAIGN = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.environ.get("BOGP_PATH", "/Users/yilu/Documents/GitHub/bo-gp-qparego"))
from bogp.mobo.pareto import hypervolume_exact  # noqa: E402

import pool  # noqa: E402

MC_SEED, N_MC = 20261006, 1000
OTHER = (5000.0, 0.5e6)
BAND = (300.0, 3000.0)
ARMS = json.load(open(os.path.join(CAMPAIGN, "analysis", "methods_C", "arms.json")))["arms"]


def starts(arm):
    frames = [pool.load_wave(w) for w in ARMS[arm]["base_waves"]]
    df = pd.concat(frames, ignore_index=True)
    Y = df[pool.M_COLS].to_numpy(float)
    assert Y.shape == (32, 3), (arm, Y.shape)
    return Y


def tau(Y, ref, shed_floor):
    floors = np.array([shed_floor, *OTHER])
    rng = np.random.default_rng(MC_SEED)
    hvs = np.empty(N_MC)
    for i in range(N_MC):
        hvs[i] = hypervolume_exact(Y + rng.normal(0.0, floors, size=Y.shape), ref)
    return float(np.std(hvs, ddof=0))


def regrade(gains, thr):
    """would_stop after each graded round under the two-strike rule."""
    ws = []
    for k in range(len(gains)):
        ws.append(k >= 1 and gains[k] < thr and gains[k - 1] < thr)
    return ws


def main():
    out, rows = {"band": list(BAND), "other_floors": list(OTHER), "arms": {}}, []
    for arm in ("P1", "P2", "P3", "N1"):
        led = json.load(open(os.path.join(CAMPAIGN, ARMS[arm]["dir"], "ledger.json")))
        ref = np.asarray(led["ref_point"], float)
        tau_old = float(led["threshold"])
        Y = starts(arm)
        hv0 = float(hypervolume_exact(Y, ref))
        assert np.isclose(hv0, led["entries"][0]["hv"], rtol=1e-12), (arm, hv0)
        taus = {f: tau(Y, ref, f) for f in BAND}
        rel = taus[3000.0] / tau_old - 1
        assert abs(rel) < 1e-12, f"{arm}: tau at 3000 does not reproduce the ledger ({rel:.3g})"
        graded = [e for e in led["entries"] if e["round"] >= 1 and e.get("gain") is not None]
        gains = [float(e["gain"]) for e in graded]
        rounds = [int(e["round"]) for e in graded]
        ws_old = regrade(gains, tau_old)
        ws_new = regrade(gains, taus[300.0])
        rec_ws = [e.get("would_stop") for e in graded]
        if arm == "P1":                      # r2 live 'stop'; r1 not graded in tau units
            rec_ws = [False, True] + rec_ws[2:]
        assert ws_old == [bool(x) for x in rec_ws], (arm, ws_old, rec_ws)
        cap = int(led["hard_cap"])
        pending = len(rounds) < cap
        first_old = next((r for r, s in zip(rounds, ws_old) if s), None)
        first_new = next((r for r, s in zip(rounds, ws_new) if s), None)
        flips = []
        for r, so, sn in zip(rounds, ws_old, ws_new):
            if so != sn:
                if r < rounds[-1]:
                    status = "VERIFIABLE"
                elif r < cap:
                    status = f"PENDING (r{r + 1} not yet graded)"
                else:
                    status = "CENSORED"
                flips.append({"round": r, "old": "stop" if so else "continue",
                              "new_300": "stop" if sn else "continue",
                              "status": status,
                              "rounds_observed_after": [x for x in rounds if x > r]})
        # break-even shed floor: the smallest floor at which the FIRST recorded
        # would-stop still fires (tau must exceed both strike gains)
        breakeven = None
        if first_old is not None:
            k = rounds.index(first_old)
            need = max(gains[k], gains[k - 1])
            lo, hi = BAND
            for _ in range(30):
                mid = 0.5 * (lo + hi)
                if tau(Y, ref, mid) > need:
                    hi = mid
                else:
                    lo = mid
            breakeven = hi
        out["arms"][arm] = {
            "tau_old_ledger": tau_old, "tau_3000_recomputed": taus[3000.0],
            "tau_300": taus[300.0], "hv0": hv0,
            "tau_old_pct_hv0": 100 * tau_old / hv0, "tau_300_pct_hv0": 100 * taus[300.0] / hv0,
            "tau_300_over_old": taus[300.0] / tau_old,
            "rounds_graded": rounds, "pending_final_grade": pending,
            "first_would_stop_old": first_old, "first_would_stop_300": first_new,
            "live_stop_round": led.get("live_stop_round"), "flips": flips,
            "breakeven_shed_floor_first_stop": breakeven}
        for r, g, so, sn in zip(rounds, gains, ws_old, ws_new):
            rows.append({"arm": arm, "round": r, "gain": g,
                         "gain_over_tau_old": g / tau_old, "gain_over_tau_300": g / taus[300.0],
                         "would_stop_old": so, "would_stop_300": sn,
                         "flip": so != sn})
        print(f"{arm}: tau_old {tau_old:.4g} (recomputed {taus[3000.0]:.4g}), tau_300 {taus[300.0]:.4g} "
              f"(x{taus[300.0] / tau_old:.3f}; {100 * tau_old / hv0:.2f}% -> "
              f"{100 * taus[300.0] / hv0:.2f}% of HV0); first stop old r{first_old} / 300 r{first_new}"
              f"{' [PENDING FINAL GRADE]' if pending else ''}; break-even floor {breakeven}; "
              f"flips {[(x['round'], x['status']) for x in flips]}")
    pd.DataFrame(rows).to_csv(os.path.join(HERE, "part_c_regrade.csv"), index=False)
    with open(os.path.join(HERE, "part_c.json"), "w") as f:
        json.dump(out, f, indent=1, default=float)
        f.write("\n")


if __name__ == "__main__":
    main()
