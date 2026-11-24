"""Prompt 55 tests — the acquisition brain (analysis/methods_E/acquire_E.py) on a
scratch ERCOT_ROOT: init (tau once, R, hv0), record-only two-strike grading
under tau_joint / tau_marginal to the cap, the Sigma = 0 cap-only branch, the
C1 ingest gate, the plan 1.3 guardrail flip + HALT rules, SUSPECT exclusion +
HALT, the random_E assert, qsub never called, commits land on origin.

Run:  cd trial_0826/ercot && /opt/anaconda3/envs/bogp-botorch/bin/python -m pytest tests/test_methods_E_acquire.py -q

Most tests swap qnehvi_E.propose for the cheap stand-in in _scratch_E (same
return schema); `test_real_fast_acquisition_init_and_r1` runs the real
botorch path once in ERCOT_E_FAST mode (~2 min). The pinned-settings dry round
is `python analysis/methods_E/dry_round_E.py` (DRY_ROUND_REPORT.md).
"""
import json
import os
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

ERCOT = Path(__file__).resolve().parents[1]
ME = ERCOT / "analysis" / "methods_E"
sys.path.insert(0, str(ME))
import common_E  # noqa: E402,F401  (pins bo-gp-qparego first)
pytest.importorskip("botorch")
import _scratch_E as sc  # noqa: E402


@pytest.fixture()
def scratch(tmp_path, monkeypatch):
    def _make(cheap=True, **overrides):
        root = sc.build_scratch(str(tmp_path), cfg_overrides=overrides or None)
        ae = sc.lane_modules(root)
        if cheap:
            import qnehvi_E
            monkeypatch.setattr(qnehvi_E, "propose", sc.cheap_propose)
        cfg = ae.load_config(root)
        return root, ae, cfg
    return _make


def _lane(ae, root, cfg, s=0):
    return ae.Lane(root, cfg, "qnehvi", s)


def _origin_log(root, cfg):
    repo = os.path.abspath(os.path.join(root, "..", ".."))
    return subprocess.run(["git", "-C", repo, "log", "--oneline", "origin/" + cfg["repo_branch"]],
                          capture_output=True, text=True).stdout


# --------------------------------------------------------------------------- #

def test_init_tau_once_R_hv0_and_readback(scratch):
    root, ae, cfg = scratch()
    lane = _lane(ae, root, cfg)
    led = ae.cmd_init(lane)
    assert led["n0_tier"] == 32 and led["entries"][0]["n"] == 32 and led["loader"] == "stub" and led["configs_source"] == "stub"
    assert led["objectives"] == cfg["objectives"] == ["V1", "E1"] and len(led["ref_point"]) == 2   # arms_E.json, design space 2026-11-24
    assert led["tau"]["tau_joint"] > 0 and led["tau"]["tau_marginal"] > 0 and not led["tau"]["budget_cap_only"]
    assert led["guardrail_mode"] == "monitor" and led["first_fire_round"] == {"tau_joint": None, "tau_marginal": None}
    assert "PLACEHOLDER" in led["R_source"] and "PLACEHOLDER" in led["tau"]["sigma_source"]
    ti = json.load(open(ae.tau_init_path(lane.dir)))
    assert ti["n_starts"] == 32 and ti["M"] == 2 and ti["n_draws"] == 1000 and ti["seed"] == 20261006
    assert len(ti["start_set_keys"]) == 32 and all(k.startswith("n0_E:") for k in ti["start_set_keys"])
    rul = ae.recompute_rulers(lane)                       # independent recomputation == ledger
    assert rul["tau_joint"] == led["tau"]["tau_joint"] and rul["tau_marginal"] == led["tau"]["tau_marginal"]
    readme = open(os.path.join(root, cfg["arms"]["qnehvi"]["dir"], "README.md")).read()
    for s in ("E-D5 OPEN", "Banned framings", "the rule now works", f"1 - (1 - 3.7e-04)^{len(cfg['objectives'])}", "PROVISIONAL", "sensitivity"):
        assert s in readme, s
    with pytest.raises(RuntimeError, match="REFUSED"):
        ae.cmd_init(lane)
    ti["tau_joint"] *= 1.0000001                          # a tau edited after init is caught
    json.dump(ti, open(ae.tau_init_path(lane.dir), "w"))
    with pytest.raises(AssertionError, match="tau_init"):
        ae.check_rulers(lane, ae.load_ledger(lane.dir))


def test_seed_rule_wave_names_and_lane_dirs(scratch):
    root, ae, cfg = scratch()
    assert ae.acq_seed(cfg, 0, 1) == 20261007 and ae.acq_seed(cfg, 4, 3) == 20261006 + 400 + 3
    assert ae.round_wave(cfg, "qnehvi", 2, 3) == "methods_E_qnehvi_s2_r3"
    assert ae.lane_dir(root, cfg, "qnehvi", 4).endswith("analysis/methods_E/qnehvi/s4")
    with pytest.raises(AssertionError):
        ae.lane_dir(root, cfg, "qnehvi", 7)


def test_random_E_never_in_training(scratch):
    root, ae, cfg = scratch(base_waves=["n0_E", "random_E"])
    lane = _lane(ae, root, cfg)
    with pytest.raises(AssertionError, match="forbidden wave random_E"):
        lane.start_set()


def test_record_only_two_strike_to_cap_and_done(scratch):
    """Zero HV gain every round (duplicate-like designs with stub Y above R? no:
    we force gain = 0 by making every new row dominated): would_stop fires at r2
    under both rulers, first_fire_round = 2, lane continues to hard_cap, DONE."""
    root, ae, cfg = scratch()
    lane = _lane(ae, root, cfg)
    assert ae.run_round(lane, 0, no_submit=True) == 0
    assert os.path.isdir(os.path.join(root, "waves", lane.wave(1)))
    led = ae.load_ledger(lane.dir)
    nadir = {o: 2.0 * v for o, v in zip(lane.objectives, led["ref_point"])}  # outside R -> contributes nothing
    for k in (1, 2, 3, 4):
        sc.fake_collect(root, lane.wave(k), overrides={i: dict(nadir) for i in range(1, 9)})
        assert ae.run_round(lane, k, no_submit=True) == 0
        assert os.path.isdir(os.path.join(root, "waves", lane.wave(k + 1))) == (k < 4)
    led = ae.load_ledger(lane.dir)
    e = led["entries"][1:]
    assert [x["gain"] for x in e] == [0.0] * 4
    assert [x["would_stop_joint"] for x in e] == [False, True, True, True]
    assert [x["would_stop_marginal"] for x in e] == [False, True, True, True]
    assert led["first_fire_round"] == {"tau_joint": 2, "tau_marginal": 2}
    assert all(x["gain_tau_joint"] == 0.0 and x["joint_vs_marginal"]["agree"] for x in e)
    assert all(x["n_outside_ref"] == 8 * x["round"] for x in e)
    done = open(ae.done_path(lane.dir)).read()
    assert "hard_cap 4 reached" in done and "first_fire_round: {'tau_joint': 2, 'tau_marginal': 2}" in done and "E-D5 OPEN" in done
    assert not os.path.exists(os.environ["SHIM_LOG"])                  # qsub never called
    log = _origin_log(root, cfg)
    assert "s0 init + r1 proposed" in log and "DONE (hard cap)" in log
    rl = open(ae.round_log_path(lane.dir)).read()
    assert "would_stop_joint: true" in rl and "first_fire_round" in rl and "calibration" in rl
    with pytest.raises(SystemExit, match="--no-submit"):
        ae.run_round(lane, 0, no_submit=False)


def test_sigma_zero_is_budget_cap_only(scratch):
    root, ae, cfg = scratch(part_a={"sigma_placeholder": {"mode": "zero"}})
    lane = _lane(ae, root, cfg)
    led = ae.cmd_init(lane)
    assert led["tau"] == {**led["tau"], "tau_joint": 0.0, "tau_marginal": 0.0, "budget_cap_only": True}
    readme = open(os.path.join(root, cfg["arms"]["qnehvi"]["dir"], "README.md")).read()
    assert "budget-cap-only and the cap governs" in readme
    assert "ZERO" in open(ae.round_log_path(lane.dir)).read()
    ae.propose_round(lane, 1)
    sc.fake_collect(root, lane.wave(1), overrides={i: {"V1": 1e12, "E1": 1e12, "R4": 1e12, "N1": 1e12} for i in range(1, 9)})
    led, halted = ae.grade_round(lane, 1)
    e = led["entries"][1]
    assert not halted and e["gain"] == 0.0 and e["gain_tau_joint"] is None and e["would_stop_joint"] is False
    assert led["first_fire_round"]["tau_joint"] is None


def test_guardrail_one_violation_flips_to_constrain_and_excludes_from_hv(scratch):
    root, ae, cfg = scratch()
    lane = _lane(ae, root, cfg)
    ae.run_round(lane, 0, no_submit=True)
    sc.fake_collect(root, lane.wave(1), overrides={3: {"R1": 2.5, "V1": 1.0, "E1": 1.0, "R4": 1.0, "N1": 1.0}})
    ae.run_round(lane, 1, no_submit=True)
    led = ae.load_ledger(lane.dir)
    e = led["entries"][1]
    assert led["guardrail_mode"] == "constrain" and led["guardrail_flipped_at_round"] == 1
    assert e["violations"] == [f"{lane.wave(1)}:3"] and e["n_hv"] == 39 and e["n"] == 40 and led["halt"] is None
    rec2 = ae.load_records(lane.dir)["2"]
    assert rec2["guardrail_mode"] == "constrain" and rec2["settings"]["constraint"].startswith("shed <= 1.0")
    assert rec2["n_train"] == 40                                           # violating run stays in GP training
    # the (very good) violating row did NOT raise HV: its values are excluded
    acc = lane.accumulated(1)
    hv_with = ae.ce.hv_exact(acc["Y"].to_numpy(float), np.asarray(led["ref_point"]))
    assert hv_with > e["hv"]
    assert os.path.isdir(os.path.join(root, "waves", lane.wave(2)))


def test_two_violations_halt(scratch):
    root, ae, cfg = scratch()
    lane = _lane(ae, root, cfg)
    ae.run_round(lane, 0, no_submit=True)
    sc.fake_collect(root, lane.wave(1), overrides={2: {"R1": 1.01}, 7: {"R1": 300.0}})
    assert ae.run_round(lane, 1, no_submit=True) == 0
    led = ae.load_ledger(lane.dir)
    assert led["halt"]["round"] == 1 and "2 R1 shed violations" in led["halt"]["reasons"][0]
    assert os.path.isfile(ae.halt_path(lane.dir)) and not os.path.isdir(os.path.join(root, "waves", lane.wave(2)))
    assert led["entries"][1]["decision"].endswith("HALT FOR DECISION") and led["guardrail_mode"] == "constrain"
    with pytest.raises(SystemExit, match="HALT"):
        ae.propose_round(lane, 2)
    assert ae.run_round(lane, 1, no_submit=True) == 0                     # refuses quietly; nothing new
    assert len(ae.load_ledger(lane.dir)["entries"]) == 2
    assert "HALT FOR DECISION" in _origin_log(root, cfg)
    st = ae.status(root, cfg)
    assert [r for r in st if r["seed"] == 0][0]["files"] == ["HALT_FOR_DECISION.md"]


def test_suspect_exclusion_and_two_suspect_halt(scratch):
    root, ae, cfg = scratch()
    lane = _lane(ae, root, cfg)
    ae.run_round(lane, 0, no_submit=True)
    sc.fake_collect(root, lane.wave(1), overrides={5: {"suspect": True, "V1": 1.0, "E1": 1.0, "R4": 1.0, "N1": 1.0},
                                                  7: {"R2": 1000.0}})
    ae.run_round(lane, 1, no_submit=True)
    led = ae.load_ledger(lane.dir)
    e = led["entries"][1]
    assert e["suspects"] == [f"{lane.wave(1)}:5"] and e["n_hv"] == 39 and led["halt"] is None
    assert e["r2_flag"] is True and led["r2_flag_rounds"] == [1]
    assert ae.load_records(lane.dir)["2"]["n_train"] == 39                # SUSPECT out of training (build choice)
    assert led["guardrail_mode"] == "monitor"                             # R2 has no acquisition role
    # second lane: two SUSPECT -> HALT
    lane1 = _lane(ae, root, cfg, 1)
    ae.run_round(lane1, 0, no_submit=True)
    sc.fake_collect(root, lane1.wave(1), overrides={1: {"suspect": True}, 2: {"suspect": True}})
    ae.run_round(lane1, 1, no_submit=True)
    led1 = ae.load_ledger(lane1.dir)
    assert led1["halt"] and "2 SUSPECT runs" in led1["halt"]["reasons"][0] and os.path.isfile(ae.halt_path(lane1.dir))
    assert not os.path.isdir(os.path.join(root, "waves", lane1.wave(2)))


def test_c1_ingest_gate_failures(scratch):
    root, ae, cfg = scratch()
    lane = _lane(ae, root, cfg)
    ae.run_round(lane, 0, no_submit=True)
    ae.run_round(lane, 1, no_submit=True)                                 # nothing collected
    f = open(os.path.join(lane.dir, "FAILED_r1.md")).read()
    assert "0 of 8 runs present" in f and not os.path.isdir(os.path.join(root, "waves", lane.wave(2)))
    os.remove(os.path.join(lane.dir, "FAILED_r1.md"))
    sc.fake_collect(root, lane.wave(1), skip=(4,))                        # one row missing its identity
    ok, why, _ = ae.ingest_gate(lane, 1)
    assert not ok and "7 of 8" in why
    sc.fake_collect(root, lane.wave(1), overrides={2: {"V1": float("nan")}})
    ok, why, _ = ae.ingest_gate(lane, 1)
    assert not ok and "non-finite" in why
    sc.fake_collect(root, lane.wave(1))
    ok, why, info = ae.ingest_gate(lane, 1)
    assert ok and info == {"n_suspect": 0, "n_violation": 0, "r2_max": pytest.approx(info["r2_max"])}
    # tampered wave files -> refused: u_* column, mw_* column, a retrofit dict (each alone)
    import pandas as pd
    import shutil
    wdir = os.path.join(root, "waves", lane.wave(1))
    p = os.path.join(wdir, "design_matrix.csv")
    shutil.copy(p, p + ".bak")
    dm = pd.read_csv(p); dm.loc[0, "u_110"] = 0.4242; dm.to_csv(p, index=False)
    ok, why, _ = ae.ingest_gate(lane, 1)
    assert not ok and "u_* columns" in why
    shutil.copy(p + ".bak", p)
    dm = pd.read_csv(p); dm.loc[1, "mw_274"] += 0.01; dm.to_csv(p, index=False)
    ok, why, _ = ae.ingest_gate(lane, 1)
    assert not ok and ("mw_* columns" in why or "proposed designs" in why)
    shutil.copy(p + ".bak", p)
    assert ae.ingest_gate(lane, 1)[0]
    dp = os.path.join(wdir, "retrofit_gen_dict_2.json")
    d2 = json.load(open(dp)); shutil.copy(dp, dp + ".bak")
    site = next(iter(d2)); d2[site]["PEM_fraction"] += 1e-6; json.dump(d2, open(dp, "w"))
    ok, why, _ = ae.ingest_gate(lane, 1)
    assert not ok and "retrofit_gen_dict_2.json entry" in why
    d2 = json.load(open(dp + ".bak")); d2["999"] = {"PEM_bid": 40.0, "PEM_fraction": 0.1, "gen_pmax": 1.0}; json.dump(d2, open(dp, "w"))
    ok, why, _ = ae.ingest_gate(lane, 1)
    assert not ok and "sites" in why
    os.remove(dp)
    ok, why, _ = ae.ingest_gate(lane, 1)
    assert not ok and "missing" in why
    shutil.copy(dp + ".bak", dp)
    assert ae.ingest_gate(lane, 1)[0]


def test_calibration_c2_c3_flags_recorded_never_halt(scratch):
    root, ae, cfg = scratch()
    lane = _lane(ae, root, cfg)
    ae.run_round(lane, 0, no_submit=True)
    far = {"V1": 1e9, "E1": 1e13, "R4": 1e8, "N1": 1e7}                   # far outside the predictive band
    sc.fake_collect(root, lane.wave(1), overrides={i: dict(far) for i in range(1, 9)})
    assert ae.run_round(lane, 1, no_submit=True) == 0
    led = ae.load_ledger(lane.dir)
    e = led["entries"][1]
    assert e["C2_review"] and e["C3_review"] and led["C2_review_rounds"] == [1] and led["C3_review_rounds"] == [1]
    assert led["halt"] is None and os.path.isdir(os.path.join(root, "waves", lane.wave(2)))
    cal = ae.load_records(lane.dir)["1"]["calibration"]
    assert all(cal[o]["cov95"] == 0 and cal[o]["n_abs_z_gt3"] == 8 for o in lane.objectives)


def test_stop_file_and_double_spend_guard(scratch):
    root, ae, cfg = scratch()
    lane = _lane(ae, root, cfg)
    ae.run_round(lane, 0, no_submit=True)
    sc.fake_collect(root, lane.wave(1))
    os.makedirs(os.path.join(root, "waves", lane.wave(2)))                 # someone already made r2
    ae.run_round(lane, 1, no_submit=True)
    assert "already exists" in open(os.path.join(lane.dir, "FAILED_r1.md")).read()
    os.remove(os.path.join(lane.dir, "FAILED_r1.md")); os.rmdir(os.path.join(root, "waves", lane.wave(2)))
    open(ae.stop_path(lane.dir), "w").close()
    ae.run_round(lane, 1, no_submit=True)
    assert "STOP found" in open(ae.done_path(lane.dir)).read()


def test_wave_files_from_the_brain(scratch):
    import pandas as pd
    root, ae, cfg = scratch()
    lane = _lane(ae, root, cfg)
    ae.run_round(lane, 0, no_submit=True)
    wdir = os.path.join(root, "waves", lane.wave(1))
    dm = pd.read_csv(os.path.join(wdir, "design_matrix.csv"), dtype={"oat_site": str})
    assert len(dm) == 8 and (dm["oat_site"] == "__ALL__").all() and dm.loc[0, "mw_140"] == 0.0
    d1 = json.load(open(os.path.join(wdir, "retrofit_gen_dict_1.json")))
    assert "140" not in d1 and len(d1) == 5
    pr = pd.read_csv(os.path.join(wdir, "predictions.csv"))
    assert set(pr.columns) >= {"index", "V1_pred_mean", "V1_pred_sd", "V1_transform", "E1_pred_sd"}
    man = json.load(open(os.path.join(wdir, "manifest.json")))
    assert man["acq_seed"] == 20261007 and man["seed_id"] == 0 and man["methods_round"] == 1 and man["guardrail_mode"] == "monitor"


@pytest.mark.slow
def test_real_fast_acquisition_init_and_r1(scratch, monkeypatch):
    """The real botorch path once (ERCOT_E_FAST): init + r1 for seeds 0 and 1,
    r1 sets differ (the seed reaches the sampler), predictions / loo recorded."""
    monkeypatch.setenv("ERCOT_E_FAST", "1")
    root, ae, cfg = scratch(cheap=False)
    import qnehvi_E
    assert qnehvi_E.FAST is True or os.environ["ERCOT_E_FAST"] == "1"
    qnehvi_E.FAST = True
    l0, l1 = _lane(ae, root, cfg, 0), _lane(ae, root, cfg, 1)
    ae.cmd_init(l0); ae.propose_round(l0, 1)
    ae.cmd_init(l1); ae.propose_round(l1, 1)
    r0, r1 = ae.load_records(l0.dir)["1"], ae.load_records(l1.dir)["1"]
    assert r0["settings"]["fast_mode"] and r0["settings"]["mc_samples"] == 128 and r0["settings"]["alpha"] == 0.0
    assert r0["acq_seed"] == 20261007 and r1["acq_seed"] == 20261107
    u0, u1 = np.asarray(r0["designs_u"]), np.asarray(r1["designs_u"])
    assert u0.shape == (8, 6) and np.all(u0 >= 0) and np.all(u0 <= 1) and not np.allclose(u0, u1)
    assert set(r0["loo_rms_z"]) == set(l0.objectives) and all(v > 0 for v in r0["noise_raw"].values())


def test_lower_bound_optimum_returns_exact_zero():
    """prompt 66 (E): a lower-bound optimum comes back as exact 0.0 (not 5.55e-17); bound_snaps recorded."""
    import qnehvi_E
    rng = np.random.default_rng(0)
    U = rng.uniform(0.2, 1.0, size=(12, 3))
    Y = np.column_stack([U.sum(1), (1 - U).sum(1) + 0.3 * U[:, 0]])      # site 0 at 0 helps both objectives
    res = qnehvi_E.propose(U, Y, Y.max(0) + 0.5, [("m52", "std", "inferred", "none")] * 2, [1e-9, 1e-9], seed=5,
                           q=2, qcfg={"num_restarts": 2, "raw_samples": 32, "mc_samples": 16}, log=lambda *_: None)
    ub = res["u_batch"]
    assert not np.any((ub > 0) & (ub < 1e-9)) and not np.any((ub < 1) & (ub > 1 - 1e-9))
    assert (ub == 0.0).any(), ub
    bs = res["settings"]["bound_snaps"]
    assert set(bs) >= {"to_0", "to_1", "tol"}
    u = np.array([[5.55e-17, 1 - 1e-15, 0.5, 0.0]])
    s = qnehvi_E.snap_bounds(u)
    assert (s["to_0"], s["to_1"]) == (1, 1) and u.tolist() == [[0.0, 1.0, 0.5, 0.0]]
