"""Prompt 45 §3: tau re-derivation + regrade under the measured shed noise.

PROVENANCE: a COPY of analysis/noise_floor/part_c.py (prompt 40 Part C, commit
4801f03, sha256 952f1a48d019c894e7eb95db9434e3d5dd0f89aa02bb6ba9c572d4cc45b30e25).
Changed ONLY:
  (a) output paths -> analysis/noise_floor/stop_regrade45/ (tau_regrade45.csv,
      tau_regrade45.json) and one sys.path line for `pool` (parent dir);
  (b) the floor/noise set: TAU_ROWS below (was BAND = (300, 3000)), plus the
      heteroscedastic form-(ii) row (per-start shed sigma; tau() takes a
      per-start shed vector — a few-line change, CRN draw order unchanged).
tau(), starts(), regrade(), the reproduce asserts (tau at 3,000 == ledger to
1e-12, hv0 == ledger, regrade == recorded would_stop incl. P1's live-stop
patch) and the break-even bisection (bracket 300-3,000) are kept as written.
Added checks (report-only, never fixes): gains == part_c_regrade.csv on the
overlapping rows; tau(300) == part_c.json; the §3.3 CONSISTENCY GATE (halts).

Original part_c.py docstring follows.

Prompt 40 Part C (report-only): per-arm tau at alternative shed floors and
a re-grade of the recorded stop decisions. Ledgers are read-only.

tau recipe = acquire_next.cmd_init / acquire_arm._mc_threshold: N = 1,000
draws, numpy default_rng(20261006), ALL 32 starts perturbed
N(0, floor^2) per objective, no clipping, exact HV, std (ddof 0) of the HV
draws. ref = the arm's ledger-frozen ref point (never recomputed). N1 shares
P1's starts and ref by design. The same seed gives common random numbers
across the floor settings.

Two-strike rule (acquire_next.run_round / acquire_arm): stop after round k
when gain_k < tau and gain_{k-1} < tau.
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
NF = os.path.abspath(os.path.join(HERE, ".."))
CAMPAIGN = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.environ.get("BOGP_PATH", "/Users/yilu/Documents/GitHub/bo-gp-qparego"))
from bogp.mobo.pareto import hypervolume_exact  # noqa: E402

sys.path.insert(0, NF)
import pool  # noqa: E402

MC_SEED, N_MC = 20261006, 1000
OTHER = (5000.0, 0.5e6)
BRACKET = (300.0, 3000.0)          # part_c's break-even bisection bracket (was BAND)
ARMS = json.load(open(os.path.join(CAMPAIGN, "analysis", "methods_C", "arms.json")))["arms"]

# (b) the noise set, prompt 45 §3.1-3.2. Label -> shed noise (MWh) or "het_ii".
TAU_ROWS = {
    "old_3000": 3000.0,         # reproduce-check (== ledger threshold)
    "scalar_285.3": 285.3,      # PRIMARY scalar (labeled: HIGH-dominated pooled, scalar framing rejected)
    "ci_lo_162": 162.0,         # measurement CI
    "ci_hi_1057": 1057.0,
    "gp_n0_32_317": 317.0,      # deployed GP inferred noise, n0 = 32
    "gp_n0_48_527": 527.0,      # deployed GP inferred noise, n0 = 48
    "het_ii": "het_ii",         # Phase-B form (ii) piecewise-linear sigma(y), per start
}
PRIMARY, OLD = "scalar_285.3", "old_3000"

# Phase-B form (ii) (PHASE_B.md §3): anchors 0 / 13.34 / 520.1 at y = 429.5 / 4,672 / 37,834.
ANCHOR_Y, ANCHOR_SD = (429.5, 4672.0, 37834.0), (0.0, 13.34, 520.1)
SLOPE1 = (ANCHOR_SD[1] - ANCHOR_SD[0]) / (ANCHOR_Y[1] - ANCHOR_Y[0])
SLOPE2 = (ANCHOR_SD[2] - ANCHOR_SD[1]) / (ANCHOR_Y[2] - ANCHOR_Y[1])
assert round(SLOPE1, 7) == 0.0031444 and round(SLOPE2, 7) == 0.0152813, (SLOPE1, SLOPE2)


def sigma_ii(y):
    y = np.asarray(y, float)
    return np.where(y <= ANCHOR_Y[0], 0.0,
                    np.where(y <= ANCHOR_Y[1], (y - ANCHOR_Y[0]) * SLOPE1,
                             ANCHOR_SD[1] + (y - ANCHOR_Y[1]) * SLOPE2))


def starts(arm):
    frames = [pool.load_wave(w) for w in ARMS[arm]["base_waves"]]
    df = pd.concat(frames, ignore_index=True)
    Y = df[pool.M_COLS].to_numpy(float)
    assert Y.shape == (32, 3), (arm, Y.shape)
    return Y


def tau(Y, ref, shed_floor):
    """shed_floor: a scalar (as in part_c) or a per-start vector of length
    len(Y) (heteroscedastic row). The scalar path is part_c's, unchanged."""
    if np.ndim(shed_floor) == 0:
        floors = np.array([shed_floor, *OTHER])
    else:
        sv = np.asarray(shed_floor, float)
        assert sv.shape == (len(Y),)
        floors = np.column_stack([sv, np.full(len(Y), OTHER[0]), np.full(len(Y), OTHER[1])])
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
    pc = json.load(open(os.path.join(NF, "part_c.json")))
    pcr = pd.read_csv(os.path.join(NF, "part_c_regrade.csv"))
    out = {"tau_rows": {k: (v if isinstance(v, str) else float(v)) for k, v in TAU_ROWS.items()},
           "primary": PRIMARY, "other_floors": list(OTHER), "sigma_ii": {
               "anchor_y": ANCHOR_Y, "anchor_sd": ANCHOR_SD, "slope1": SLOPE1, "slope2": SLOPE2},
           "arms": {}, "checks": {}}
    rows = []
    for arm in ("P1", "P2", "P3", "N1"):
        led = json.load(open(os.path.join(CAMPAIGN, ARMS[arm]["dir"], "ledger.json")))
        ref = np.asarray(led["ref_point"], float)
        tau_old = float(led["threshold"])
        Y = starts(arm)
        hv0 = float(hypervolume_exact(Y, ref))
        assert np.isclose(hv0, led["entries"][0]["hv"], rtol=1e-12), (arm, hv0)
        sig = sigma_ii(Y[:, 0])
        taus = {}
        for k, v in TAU_ROWS.items():
            taus[k] = tau(Y, ref, sig if v == "het_ii" else v)
        rel = taus[OLD] / tau_old - 1
        assert abs(rel) < 1e-12, f"{arm}: tau at 3000 does not reproduce the ledger ({rel:.3g})"
        # vector path == scalar path at a constant sigma (CRN draw order unchanged)
        assert tau(Y, ref, np.full(32, 285.3)) == taus[PRIMARY], arm
        tau300 = tau(Y, ref, 300.0)
        assert tau300 == pc["arms"][arm]["tau_300"], (arm, tau300)
        graded = [e for e in led["entries"] if e["round"] >= 1 and e.get("gain") is not None]
        gains = [float(e["gain"]) for e in graded]
        rounds = [int(e["round"]) for e in graded]
        ws = {k: regrade(gains, t) for k, t in taus.items()}
        ws_old = regrade(gains, tau_old)
        assert ws_old == ws[OLD]
        rec_ws = [e.get("would_stop") for e in graded]
        if arm == "P1":                      # r2 live 'stop'; r1 not graded in tau units
            rec_ws = [False, True] + rec_ws[2:]
        assert ws_old == [bool(x) for x in rec_ws], (arm, ws_old, rec_ws)
        cap = int(led["hard_cap"])
        assert rounds == list(range(1, cap + 1)), f"{arm}: not graded through r{cap}: {rounds}"
        # gains == part_c_regrade.csv on every overlapping row
        old = pcr[pcr.arm == arm].set_index("round")
        for r, g in zip(rounds, gains):
            if r in old.index:
                assert g == old.loc[r, "gain"], (arm, r, g, old.loc[r, "gain"])
        # CONSISTENCY GATE (§3.3): 285.3 < 300, tau monotone in the shed noise ->
        # a stop under tau(285.3) on a row part_c graded no-stop at 300 is a CONTRADICTION.
        for r, s in zip(rounds, ws[PRIMARY]):
            if r in old.index and s and not bool(old.loc[r, "would_stop_300"]):
                raise SystemExit(f"HALT: CONTRADICTION {arm} r{r} stops at 285.3 but not at 300")
        first = {k: next((r for r, s in zip(rounds, w) if s), None) for k, w in ws.items()}
        # break-even shed floor: the smallest floor at which the FIRST recorded
        # would-stop still fires (tau must exceed both strike gains)
        breakeven = None
        if first[OLD] is not None:
            k = rounds.index(first[OLD])
            need = max(gains[k], gains[k - 1])
            lo, hi = BRACKET
            assert tau(Y, ref, lo) <= need < tau(Y, ref, hi), (arm, need)
            for _ in range(30):
                mid = 0.5 * (lo + hi)
                if tau(Y, ref, mid) > need:
                    hi = mid
                else:
                    lo = mid
            breakeven = hi
        out["arms"][arm] = {
            "tau_old_ledger": tau_old, "hv0": hv0, "tau": taus,
            "tau_over_old": {k: t / tau_old for k, t in taus.items()},
            "tau_pct_hv0": {k: 100 * t / hv0 for k, t in taus.items()},
            "tau_300_part_c": tau300,
            "het_sigma_starts": {"min": float(sig.min()), "median": float(np.median(sig)),
                                 "max": float(sig.max()), "n_zero": int((sig == 0).sum()),
                                 "n_le_13.34": int((sig <= 13.34).sum())},
            "rounds_graded": rounds, "gains": gains, "first_would_stop": first,
            "would_stop": ws, "live_stop_round": led.get("live_stop_round"),
            "breakeven_shed_floor_first_stop": breakeven,
            "new_rows_not_in_part_c": [r for r in rounds if r not in old.index]}
        for i, (r, g) in enumerate(zip(rounds, gains)):
            for k, t in taus.items():
                rows.append({"arm": arm, "round": r, "gain": g, "tau_row": k,
                             "shed_noise": TAU_ROWS[k], "tau": t, "gain_over_tau": g / t,
                             "would_stop": ws[k][i], "would_stop_old": ws_old[i],
                             "in_part_c": r in old.index})
        print(f"{arm}: " + ", ".join(f"{k} {t:.4g}" for k, t in taus.items())
              + f" | first stop {first} | break-even {breakeven}")
    # monotonicity of tau in the scalar shed noise (report; the gate above assumes it)
    scal = sorted((v, k) for k, v in TAU_ROWS.items() if not isinstance(v, str))
    mono = {a: all(out["arms"][a]["tau"][k1] <= out["arms"][a]["tau"][k2]
                   for (_, k1), (_, k2) in zip(scal, scal[1:])) for a in out["arms"]}
    het_le = {a: out["arms"][a]["tau"]["het_ii"] <= out["arms"][a]["tau"][PRIMARY] for a in out["arms"]}
    out["checks"] = {"tau_monotone_in_scalar_noise": mono, "tau_het_le_tau_285.3": het_le,
                     "consistency_gate": "PASS"}
    print("checks:", out["checks"])
    pd.DataFrame(rows).to_csv(os.path.join(HERE, "tau_regrade45.csv"), index=False)
    with open(os.path.join(HERE, "tau_regrade45.json"), "w") as f:
        json.dump(out, f, indent=1, default=float)
        f.write("\n")


if __name__ == "__main__":
    main()
