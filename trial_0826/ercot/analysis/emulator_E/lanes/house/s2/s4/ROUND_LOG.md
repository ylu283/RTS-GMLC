# methods_E arm qnehvi seed_id 4 — ROUND_LOG (prompt 55; acq = qnehvi, base = ['n0_E'] nav prefix n0 = 48, objectives = ['V1', 'E1'])

Ledger: `lanes/house/s2/s4/ledger.json`. stop_rule = record_only: gain_k and
would_stop_k = (gain_k < tau) AND (gain_{k-1} < tau) are graded and logged under tau_joint
(headline) and tau_marginal (recorded) with the joint-vs-marginal sensitivity column; the
rule never halts; every lane runs to hard_cap = 4. tau_joint = 0, tau_marginal = 0 — ZERO: the stop rule is budget-cap-only and the cap governs (plan 3).
E-D5 OPEN: see README.md for the two readings of a fire. Halts ONLY per plan 1.2/1.3
(HALT_FOR_DECISION.md). Acquisition jobs never submit; Kay submits via submit_ready_E.sh.
Stop NOW: `touch lanes/house/s2/s4/STOP` on the CRC clone, then qdel the lane's JIDs.

<!-- BEGIN r1 -->
## Round 1 (methods_E_EMU_house_s2_s4_r1)
- proposed_at: "2026-11-24T07:45:03+00:00"
- wave: "methods_E_EMU_house_s2_s4_r1"
- acq: "qnehvi"
- acq_seed: 20261407
- guardrail_mode: "monitor"
- settings: {"mc_samples": 128, "num_restarts": 20, "raw_samples": 512, "alpha": 0.0, "prune_baseline": true, "sequential": true, "fast_mode": false, "constraint": "none", "guardrail_mode": "monitor", "seed": 20261407, "dtype": "float64"}
- botorch: "0.16.1"
- bo_gp_sha: "60e6328236e745b3d34dc8cd704bb72888ae5d15"
- loo_rms_z: {"V1": 0.4268, "E1": 0.7727}
- noise_raw: {"V1": 14949.051609849952, "E1": 750721.1138779742}
- predictions: "waves/methods_E_EMU_house_s2_s4_r1/predictions.csv"
- graded_at: "2026-11-24T07:45:04+00:00"
- n_train: 56
- n_hv: 54
- cumulative_hv: 126965211661861.05
- gain: 26753284613329.58
- gain_tau_joint: null
- would_stop_joint: false
- gain_tau_marginal: null
- would_stop_marginal: false
- joint_vs_marginal: {"ratio_joint_over_marginal": null, "agree": true, "fires": {"joint": false, "marginal": false}}
- first_fire_round: {"tau_joint": null, "tau_marginal": null}
- n_outside_ref: 0
- violations: ["methods_E_EMU_house_s2_s4_r1:2", "methods_E_EMU_house_s2_s4_r1:6"]
- suspects: []
- r2_flag: false
- r2_max_mwh: 174.94264755782658
- calibration: {"V1": {"mean_z": -0.028, "rms_z": 0.186, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}, "E1": {"mean_z": -0.075, "rms_z": 0.169, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}}
- C2_review: false
- C3_review: false
- halt: {"round": 1, "reasons": ["2 R1 shed violations (> 1.0 MWh) in round 1: ['methods_E_EMU_house_s2_s4_r1:2', 'methods_E_EMU_house_s2_s4_r1:6']"], "at": "2026-11-24T07:45:04+00:00"}
- decision: "graded (record_only) + HALT FOR DECISION"
- qnehvi_seconds: 4.3
- r1_shared_designs_with_seed: {"0": 4, "1": 4, "2": 4, "3": 4}
- designs (MW per site ['110', '140', '146', '163', '270', '274']):
    - [47.480, 0.000, 0.000, 185.400, 579.000, 0.000]
    - [0.000, 250.600, 162.784, 185.400, 579.000, 746.400]
    - [338.600, 0.000, 0.000, 185.400, 579.000, 0.000]
    - [0.000, 0.000, 0.000, 185.400, 579.000, 746.400]
    - [99.751, 250.600, 213.547, 185.400, 579.000, 746.400]
    - [0.000, 250.600, 0.000, 185.400, 579.000, 746.400]
    - [0.000, 0.000, 0.000, 185.400, 0.000, 746.400]
    - [0.000, 0.000, 0.000, 185.400, 579.000, 453.420]
- realized Y (['V1', 'E1']):
    - [3.32956e+06, 8.09376e+09]
    - [1.44724e+06, 8.1375e+09]
    - [2.72477e+06, 8.10845e+09]
    - [2.0408e+06, 8.11705e+09]
    - [1.2498e+06, 8.15059e+09]
    - [1.70326e+06, 8.12592e+09]
    - [2.99334e+06, 8.10445e+09]
    - [2.42837e+06, 8.11428e+09]
<!-- END r1 -->
