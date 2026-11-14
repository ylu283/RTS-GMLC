#!/usr/bin/env python3
"""Prompt 55 Part A exit — ONE offline dry round end-to-end on a scratch
ERCOT_ROOT with the stub loader, placeholder tau and R, PINNED acquisition
settings, and the plan 1.2/1.3 halt scenarios. Zero simulation; nothing is
written into the live tree except DRY_ROUND_REPORT.md (this directory).

    /opt/anaconda3/envs/bogp-botorch/bin/python analysis/methods_E/dry_round_E.py [--scratch DIR] [--fast]

Flow (scratch A, Sigma placeholder = diag (0.02 x start-set sd)^2 so the
two-strike logic is live):
  init-all          5 lanes: init (tau rulers, R, hv0) + r1 proposal each; the
                    cross-seed assert (r1 sets differ) runs inside propose
  recompute-tau s0  independent recomputation == ledger (equality)
  s0: collect r1 -> run r1 (C1 gate, grade, C2/C3, propose r2) -> collect r2 (zero
      gain) -> run r2 (two-strike bookkeeping) -> continues; no halt
  s1: collect r1 with ONE shed violation -> run r1: guardrail_mode flips to
      constrain, r2 proposed with the shed GP constraint, violating row out of HV
  s2: collect r1 with TWO violations -> run r1: HALT_FOR_DECISION.md, no r2;
      `propose --round 2` refuses
  s3: collect r1 with TWO SUSPECT -> run r1: HALT; one more SUSPECT lane check
  s4: collect r1 with one SUSPECT + an R2 flag -> run r1: excluded from HV and
      training, R2 flag recorded, r2 proposed
Scratch B (Sigma = 0): init s0 -> tau = 0, cap-only statement; run r0/r1 ->
      would_stop False, gain_tau None.
qsub is shimmed to FAIL: the machinery must never call it.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import _scratch_E as sc  # noqa: E402


def _run(ae, argv):
    t0 = time.time()
    rc = ae.main(argv)
    assert rc == 0, (argv, rc)
    return time.time() - t0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--scratch", default=None, help="scratch dir (default: a fresh tempdir)")
    ap.add_argument("--fast", action="store_true", help="ERCOT_E_FAST=1 (fewer restarts; labelled in the report)")
    args = ap.parse_args(argv)
    if args.fast:
        os.environ["ERCOT_E_FAST"] = "1"
    tmp = args.scratch or tempfile.mkdtemp(prefix="methods_E_dry_")
    os.makedirs(tmp, exist_ok=True)
    report = [f"# methods_E Part A dry round — {time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime())}", "",
              f"scratch = `{tmp}`; fast mode = {args.fast}; python = {sys.version.split()[0]}", ""]
    T = {}

    # ---------------- scratch A: Sigma placeholder > 0 ----------------
    rootA = sc.build_scratch(os.path.join(tmp, "A"))
    ae = sc.lane_modules(rootA)
    import botorch, torch  # noqa: E402
    report += [f"botorch {botorch.__version__}, torch {torch.__version__}, bo-gp {ae.ce.bogp_sha()}", ""]
    T["init-all (5 lanes: init + r1)"] = _run(ae, ["init-all"])
    cfg = ae.load_config(rootA)
    lanes = {s: ae.Lane(rootA, cfg, "qnehvi", s) for s in range(5)}
    led0 = ae.load_ledger(lanes[0].dir)
    r1 = {s: ae.load_records(lanes[s].dir)["1"] for s in range(5)}
    sets = [frozenset(tuple(r) for r in __import__("numpy").round(r1[s]["designs_u"], 10).tolist()) for s in range(5)]
    assert all(sets[i].isdisjoint(sets[j]) for i in range(5) for j in range(i + 1, 5)), "r1 sets overlap across seeds"
    T["recompute-tau s0"] = _run(ae, ["recompute-tau", "--seed", "0"])
    report += ["## Scratch A (Sigma placeholder = diag (0.02 x sd)^2)", "",
               f"- loader = {led0['loader']}, configs = {led0['configs_source']}, n0 = {led0['n0_tier']}, R source = {led0['R_source']}",
               f"- R = {[round(v, 4) for v in led0['ref_point']]}",
               f"- tau_joint = {led0['tau']['tau_joint']:.6g}, tau_marginal = {led0['tau']['tau_marginal']:.6g}, joint/marginal = {led0['tau']['sensitivity_joint_over_marginal']:.4f} ({led0['tau']['sigma_source']})",
               f"- hv0 = {led0['entries'][0]['hv']:.6g}; recompute-tau reproduced the ledger (equality)",
               f"- r1 proposals pairwise disjoint across seed_ids 0-4 (acq seeds {[r1[s]['acq_seed'] for s in range(5)]}); settings {r1[0]['settings']}",
               f"- r1 qNEHVI seconds per lane: {[r1[s]['qnehvi_seconds'] for s in range(5)]}", ""]

    # s0: clean rounds
    sc.fake_collect(rootA, lanes[0].wave(1))
    T["s0 run r1 (grade + propose r2)"] = _run(ae, ["run", "--seed", "0", "--round", "1", "--no-submit"])
    sc.fake_collect(rootA, lanes[0].wave(2))
    T["s0 run r2"] = _run(ae, ["run", "--seed", "0", "--round", "2", "--no-submit"])
    led = ae.load_ledger(lanes[0].dir)
    e = led["entries"]
    report += ["### s0 — two clean rounds", ""]
    for x in e[1:]:
        report.append(f"- r{x['round']}: n={x['n']} n_hv={x['n_hv']} hv={x['hv']:.6g} gain={x['gain']:.6g} "
                      f"gain/tau_joint={x['gain_tau_joint']:.3f} would_stop joint/marginal={x['would_stop_joint']}/{x['would_stop_marginal']} "
                      f"C2={x['C2_review']} C3={x['C3_review']} decision={x['decision']}")
    rec1 = ae.load_records(lanes[0].dir)["1"]
    report += [f"- r1 calibration: {json.dumps(rec1['calibration'])}", f"- first_fire_round: {led['first_fire_round']}",
               f"- wave r3 proposed: {os.path.isdir(os.path.join(rootA, 'waves', lanes[0].wave(3)))}", ""]

    # s1: one violation -> constrain
    sc.fake_collect(rootA, lanes[1].wave(1), overrides={3: {"R1": 2.5}})
    T["s1 run r1 (one violation)"] = _run(ae, ["run", "--seed", "1", "--round", "1", "--no-submit"])
    led1 = ae.load_ledger(lanes[1].dir)
    rec2 = ae.load_records(lanes[1].dir)["2"]
    assert led1["guardrail_mode"] == "constrain" and led1["guardrail_flipped_at_round"] == 1
    assert "shed <=" in rec2["settings"]["constraint"], rec2["settings"]["constraint"]
    assert led1["entries"][1]["n_hv"] == 32 + 7 and led1["entries"][1]["violations"] == [f"{lanes[1].wave(1)}:3"]
    report += ["### s1 — one shed violation in r1", "",
               f"- guardrail_mode after grading r1: {led1['guardrail_mode']} (flipped at round {led1['guardrail_flipped_at_round']}); violations {led1['violations']}",
               f"- r2 proposed under constraint: `{rec2['settings']['constraint']}`; n_hv at r1 = {led1['entries'][1]['n_hv']} (violating row excluded), n_train = {rec2['n_train']} (kept in training)", ""]

    # s2: two violations -> HALT
    sc.fake_collect(rootA, lanes[2].wave(1), overrides={2: {"R1": 1.5}, 6: {"R1": 40.0}})
    T["s2 run r1 (two violations -> HALT)"] = _run(ae, ["run", "--seed", "2", "--round", "1", "--no-submit"])
    assert os.path.isfile(ae.halt_path(lanes[2].dir)) and not os.path.isdir(os.path.join(rootA, "waves", lanes[2].wave(2)))
    try:
        ae.main(["propose", "--seed", "2", "--round", "2"])
        raise AssertionError("propose did not refuse under HALT")
    except SystemExit as ex:
        assert "HALT" in str(ex)
    report += ["### s2 — two shed violations in r1", "",
               f"- `{os.path.relpath(ae.halt_path(lanes[2].dir), rootA)}` written; r2 NOT proposed; `propose --round 2` refused",
               "- " + open(ae.halt_path(lanes[2].dir)).read().splitlines()[2], ""]

    # s3: two SUSPECT -> HALT
    sc.fake_collect(rootA, lanes[3].wave(1), overrides={1: {"suspect": True}, 8: {"suspect": True}})
    T["s3 run r1 (two SUSPECT -> HALT)"] = _run(ae, ["run", "--seed", "3", "--round", "1", "--no-submit"])
    led3 = ae.load_ledger(lanes[3].dir)
    assert led3["halt"] and len(led3["entries"][1]["suspects"]) == 2 and led3["entries"][1]["n_hv"] == 32 + 6
    report += ["### s3 — two SUSPECT runs in r1", "",
               f"- HALT: {led3['halt']['reasons']}; n_hv = {led3['entries'][1]['n_hv']} (both excluded)", ""]

    # s4: one SUSPECT + R2 flag -> excluded, flagged, continues
    sc.fake_collect(rootA, lanes[4].wave(1), overrides={5: {"suspect": True}, 7: {"R2": 1000.0}})
    T["s4 run r1 (one SUSPECT + R2 flag)"] = _run(ae, ["run", "--seed", "4", "--round", "1", "--no-submit"])
    led4 = ae.load_ledger(lanes[4].dir)
    rec4 = ae.load_records(lanes[4].dir)
    assert led4["entries"][1]["n_hv"] == 32 + 7 and rec4["2"]["n_train"] == 32 + 7 and led4["r2_flag_rounds"] == [1]
    assert led4["halt"] is None and os.path.isdir(os.path.join(rootA, "waves", lanes[4].wave(2)))
    report += ["### s4 — one SUSPECT + one R2 flag in r1", "",
               f"- suspects {led4['suspects']}; n_hv = {led4['entries'][1]['n_hv']}, n_train for r2 = {rec4['2']['n_train']} (SUSPECT out of both); R2 flag rounds {led4['r2_flag_rounds']}; no halt; r2 proposed", ""]

    # never qsub; git log on origin
    assert not os.path.exists(os.environ["SHIM_LOG"]), "qsub was called"
    log = subprocess.run(["git", "-C", os.path.dirname(rootA.rstrip("/")).rsplit("/trial_0826", 1)[0], "log", "--oneline", "origin/" + cfg["repo_branch"]],
                         capture_output=True, text=True).stdout
    report += ["### Plumbing", "", "- qsub never called (shim would have logged)", "- origin git log (bot commits pushed):", "",
               "```", log.strip(), "```", ""]

    # ---------------- scratch B: Sigma = 0 ----------------
    rootB = sc.build_scratch(os.path.join(tmp, "B"), cfg_overrides={"part_a": {"sigma_placeholder": {"mode": "zero"}}})
    aeB = sc.lane_modules(rootB)
    T["B init s0 (Sigma = 0)"] = _run(aeB, ["init", "--seed", "0"])
    cfgB = aeB.load_config(rootB)
    lb = aeB.Lane(rootB, cfgB, "qnehvi", 0)
    ledB = aeB.load_ledger(lb.dir)
    assert ledB["tau"]["tau_joint"] == 0.0 and ledB["tau"]["tau_marginal"] == 0.0 and ledB["tau"]["budget_cap_only"]
    readme = open(os.path.join(rootB, cfgB["arms"]["qnehvi"]["dir"], "README.md")).read()
    assert "budget-cap-only and the cap governs" in readme
    T["B run r0 + r1"] = _run(aeB, ["run", "--seed", "0", "--round", "0", "--no-submit"])
    sc.fake_collect(rootB, lb.wave(1))
    T["B run r0 + r1"] += _run(aeB, ["run", "--seed", "0", "--round", "1", "--no-submit"])
    eB = aeB.load_ledger(lb.dir)["entries"][1]
    assert eB["gain_tau_joint"] is None and eB["would_stop_joint"] is False
    report += ["## Scratch B (Sigma = 0 -> tau = 0)", "",
               f"- tau_joint = tau_marginal = 0; README carries the plan-3 statement; r1 graded: gain = {eB['gain']:.6g}, "
               f"gain_tau = {eB['gain_tau_joint']}, would_stop = {eB['would_stop_joint']} (budget-cap-only)", ""]

    report += ["## Timings (s)", "", "| step | seconds |", "|---|---|"] + [f"| {k} | {v:.0f} |" for k, v in T.items()] + [""]
    out = os.path.join(HERE, "DRY_ROUND_REPORT.md")
    with open(out, "w") as f:
        f.write("\n".join(report))
    print("\n".join(report))
    print("report:", out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
