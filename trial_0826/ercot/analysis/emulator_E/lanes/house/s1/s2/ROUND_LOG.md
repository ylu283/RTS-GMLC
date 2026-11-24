# methods_E arm qnehvi seed_id 2 — ROUND_LOG (prompt 55; acq = qnehvi, base = ['n0_E'] nav prefix n0 = 48, objectives = ['V1', 'E1'])

Ledger: `lanes/house/s1/s2/ledger.json`. stop_rule = record_only: gain_k and
would_stop_k = (gain_k < tau) AND (gain_{k-1} < tau) are graded and logged under tau_joint
(headline) and tau_marginal (recorded) with the joint-vs-marginal sensitivity column; the
rule never halts; every lane runs to hard_cap = 4. tau_joint = 0, tau_marginal = 0 — ZERO: the stop rule is budget-cap-only and the cap governs (plan 3).
E-D5 OPEN: see README.md for the two readings of a fire. Halts ONLY per plan 1.2/1.3
(HALT_FOR_DECISION.md). Acquisition jobs never submit; Kay submits via submit_ready_E.sh.
Stop NOW: `touch lanes/house/s1/s2/STOP` on the CRC clone, then qdel the lane's JIDs.

<!-- BEGIN r1 -->
## Round 1 (methods_E_EMU_house_s1_s2_r1)
- proposed_at: "2026-11-24T07:45:45+00:00"
- wave: "methods_E_EMU_house_s1_s2_r1"
- acq: "qnehvi"
- acq_seed: 20261207
- guardrail_mode: "monitor"
- settings: {"mc_samples": 128, "num_restarts": 20, "raw_samples": 512, "alpha": 0.0, "prune_baseline": true, "sequential": true, "fast_mode": false, "constraint": "none", "guardrail_mode": "monitor", "seed": 20261207, "dtype": "float64"}
- botorch: "0.16.1"
- bo_gp_sha: "60e6328236e745b3d34dc8cd704bb72888ae5d15"
- loo_rms_z: {"V1": 0.4268, "E1": 0.7727}
- noise_raw: {"V1": 14949.051609849952, "E1": 750721.1138779742}
- predictions: "waves/methods_E_EMU_house_s1_s2_r1/predictions.csv"
- graded_at: "2026-11-24T07:45:46+00:00"
- n_train: 56
- n_hv: 55
- cumulative_hv: 131326614676903.28
- gain: 31114687628371.812
- gain_tau_joint: null
- would_stop_joint: false
- gain_tau_marginal: null
- would_stop_marginal: false
- joint_vs_marginal: {"ratio_joint_over_marginal": null, "agree": true, "fires": {"joint": false, "marginal": false}}
- first_fire_round: {"tau_joint": null, "tau_marginal": null}
- n_outside_ref: 0
- violations: ["methods_E_EMU_house_s1_s2_r1:3"]
- suspects: []
- r2_flag: false
- r2_max_mwh: 170.3617003061376
- calibration: {"V1": {"mean_z": -0.045, "rms_z": 0.152, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}, "E1": {"mean_z": -0.065, "rms_z": 0.107, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}}
- C2_review: false
- C3_review: false
- halt: null
- decision: "graded (record_only)"
- qnehvi_seconds: 4.1
- r1_shared_designs_with_seed: {"0": 5, "1": 4}
- designs (MW per site ['110', '140', '146', '163', '270', '274']):
    - [46.199, 0.000, 0.000, 185.400, 579.000, 0.000]
    - [0.000, 250.600, 162.825, 185.400, 579.000, 746.400]
    - [338.600, 0.000, 0.000, 185.400, 579.000, 0.000]
    - [0.000, 0.000, 0.000, 185.400, 579.000, 746.400]
    - [0.000, 250.600, 0.000, 185.400, 579.000, 746.400]
    - [98.238, 250.600, 215.289, 185.400, 579.000, 746.400]
    - [0.000, 0.000, 0.000, 185.400, 0.000, 746.400]
    - [0.000, 250.600, 0.000, 185.400, 579.000, 0.000]
- realized Y (['V1', 'E1']):
    - [3.33127e+06, 8.09376e+09]
    - [1.4423e+06, 8.13709e+09]
    - [2.70861e+06, 8.1079e+09]
    - [2.04082e+06, 8.11814e+09]
    - [1.71427e+06, 8.12554e+09]
    - [1.25571e+06, 8.15044e+09]
    - [2.99664e+06, 8.10394e+09]
    - [2.9713e+06, 8.10464e+09]
<!-- END r1 -->

<!-- BEGIN r2 -->
## Round 2 (methods_E_EMU_house_s1_s2_r2)
- proposed_at: "2026-11-24T07:45:55+00:00"
- wave: "methods_E_EMU_house_s1_s2_r2"
- acq: "qnehvi"
- acq_seed: 20261208
- guardrail_mode: "constrain"
- settings: {"mc_samples": 128, "num_restarts": 20, "raw_samples": 512, "alpha": 0.0, "prune_baseline": true, "sequential": true, "fast_mode": false, "constraint": "shed <= 1.0 MWh (GP on the accumulated R1 column)", "guardrail_mode": "constrain", "seed": 20261208, "dtype": "float64"}
- botorch: "0.16.1"
- bo_gp_sha: "60e6328236e745b3d34dc8cd704bb72888ae5d15"
- loo_rms_z: {"V1": 0.3746, "E1": 0.7199}
- noise_raw: {"V1": 14980.676891602821, "E1": 789802.9475287931}
- predictions: "waves/methods_E_EMU_house_s1_s2_r2/predictions.csv"
- graded_at: "2026-11-24T07:45:56+00:00"
- n_train: 64
- n_hv: 63
- cumulative_hv: 139240326947547.58
- gain: 7913712270644.297
- gain_tau_joint: null
- would_stop_joint: false
- gain_tau_marginal: null
- would_stop_marginal: false
- joint_vs_marginal: {"ratio_joint_over_marginal": null, "agree": true, "fires": {"joint": false, "marginal": false}}
- first_fire_round: {"tau_joint": null, "tau_marginal": null}
- n_outside_ref: 0
- violations: []
- suspects: []
- r2_flag: false
- r2_max_mwh: 201.95908064732572
- calibration: {"V1": {"mean_z": 0.109, "rms_z": 0.282, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}, "E1": {"mean_z": 0.17, "rms_z": 0.278, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}}
- C2_review: false
- C3_review: false
- halt: null
- decision: "graded (record_only)"
- qnehvi_seconds: 7.9
- designs (MW per site ['110', '140', '146', '163', '270', '274']):
    - [0.000, 0.000, 0.000, 185.400, 579.000, 371.954]
    - [0.000, 0.000, 0.000, 168.859, 579.000, 0.000]
    - [140.758, 0.000, 0.000, 185.400, 579.000, 0.000]
    - [237.640, 0.000, 0.000, 185.400, 579.000, 43.806]
    - [0.000, 250.600, 73.915, 185.400, 579.000, 746.400]
    - [0.000, 0.000, 0.000, 185.400, 579.000, 513.392]
    - [33.265, 250.600, 211.042, 185.400, 579.000, 746.400]
    - [188.903, 250.600, 198.543, 185.400, 579.000, 746.400]
- realized Y (['V1', 'E1']):
    - [2.58849e+06, 8.11176e+09]
    - [3.47617e+06, 8.09124e+09]
    - [3.12238e+06, 8.0997e+09]
    - [2.81686e+06, 8.1071e+09]
    - [1.57338e+06, 8.13177e+09]
    - [2.33507e+06, 8.11583e+09]
    - [1.35419e+06, 8.14348e+09]
    - [1.15734e+06, 8.15708e+09]
<!-- END r2 -->

<!-- BEGIN r3 -->
## Round 3 (methods_E_EMU_house_s1_s2_r3)
- proposed_at: "2026-11-24T07:46:03+00:00"
- wave: "methods_E_EMU_house_s1_s2_r3"
- acq: "qnehvi"
- acq_seed: 20261209
- guardrail_mode: "constrain"
- settings: {"mc_samples": 128, "num_restarts": 20, "raw_samples": 512, "alpha": 0.0, "prune_baseline": true, "sequential": true, "fast_mode": false, "constraint": "shed <= 1.0 MWh (GP on the accumulated R1 column)", "guardrail_mode": "constrain", "seed": 20261209, "dtype": "float64"}
- botorch: "0.16.1"
- bo_gp_sha: "60e6328236e745b3d34dc8cd704bb72888ae5d15"
- loo_rms_z: {"V1": 0.3744, "E1": 0.7241}
- noise_raw: {"V1": 15769.573851638066, "E1": 768227.4965114703}
- predictions: "waves/methods_E_EMU_house_s1_s2_r3/predictions.csv"
- graded_at: "2026-11-24T07:46:04+00:00"
- n_train: 72
- n_hv: 71
- cumulative_hv: 140563157034222.86
- gain: 1322830086675.2812
- gain_tau_joint: null
- would_stop_joint: false
- gain_tau_marginal: null
- would_stop_marginal: false
- joint_vs_marginal: {"ratio_joint_over_marginal": null, "agree": true, "fires": {"joint": false, "marginal": false}}
- first_fire_round: {"tau_joint": null, "tau_marginal": null}
- n_outside_ref: 0
- violations: []
- suspects: []
- r2_flag: false
- r2_max_mwh: 189.61748966198473
- calibration: {"V1": {"mean_z": 0.113, "rms_z": 0.335, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}, "E1": {"mean_z": -0.11, "rms_z": 0.262, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}}
- C2_review: false
- C3_review: false
- halt: null
- decision: "graded (record_only)"
- qnehvi_seconds: 6.7
- designs (MW per site ['110', '140', '146', '163', '270', '274']):
    - [338.600, 0.000, 0.000, 185.400, 0.000, 746.400]
    - [0.000, 88.243, 0.000, 185.400, 579.000, 746.400]
    - [0.000, 0.000, 0.000, 0.000, 579.000, 746.400]
    - [338.600, 0.000, 0.000, 0.000, 0.000, 746.400]
    - [0.000, 0.000, 0.000, 80.683, 579.000, 0.000]
    - [338.600, 250.600, 9.632, 185.400, 579.000, 746.400]
    - [93.247, 0.000, 0.000, 185.400, 579.000, 0.000]
    - [338.600, 250.600, 79.117, 185.400, 579.000, 746.400]
- realized Y (['V1', 'E1']):
    - [2.46351e+06, 8.11704e+09]
    - [1.88269e+06, 8.12177e+09]
    - [2.33807e+06, 8.11803e+09]
    - [2.77273e+06, 8.11002e+09]
    - [3.69328e+06, 8.09026e+09]
    - [1.39571e+06, 8.14406e+09]
    - [3.22994e+06, 8.09606e+09]
    - [1.26027e+06, 8.15187e+09]
<!-- END r3 -->

<!-- BEGIN r4 -->
## Round 4 (methods_E_EMU_house_s1_s2_r4)
- proposed_at: "2026-11-24T07:46:13+00:00"
- wave: "methods_E_EMU_house_s1_s2_r4"
- acq: "qnehvi"
- acq_seed: 20261210
- guardrail_mode: "constrain"
- settings: {"mc_samples": 128, "num_restarts": 20, "raw_samples": 512, "alpha": 0.0, "prune_baseline": true, "sequential": true, "fast_mode": false, "constraint": "shed <= 1.0 MWh (GP on the accumulated R1 column)", "guardrail_mode": "constrain", "seed": 20261210, "dtype": "float64"}
- botorch: "0.16.1"
- bo_gp_sha: "60e6328236e745b3d34dc8cd704bb72888ae5d15"
- loo_rms_z: {"V1": 0.3493, "E1": 0.6956}
- noise_raw: {"V1": 15896.908239817883, "E1": 775674.7444316687}
- predictions: "waves/methods_E_EMU_house_s1_s2_r4/predictions.csv"
- graded_at: "2026-11-24T07:46:14+00:00"
- n_train: 80
- n_hv: 79
- cumulative_hv: 141087850890662.88
- gain: 524693856440.0156
- gain_tau_joint: null
- would_stop_joint: false
- gain_tau_marginal: null
- would_stop_marginal: false
- joint_vs_marginal: {"ratio_joint_over_marginal": null, "agree": true, "fires": {"joint": false, "marginal": false}}
- first_fire_round: {"tau_joint": null, "tau_marginal": null}
- n_outside_ref: 0
- violations: []
- suspects: []
- r2_flag: false
- r2_max_mwh: 169.71330725003827
- calibration: {"V1": {"mean_z": 0.137, "rms_z": 0.267, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}, "E1": {"mean_z": 0.143, "rms_z": 0.26, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}}
- C2_review: false
- C3_review: false
- halt: null
- decision: "graded (record_only)"
- qnehvi_seconds: 8.4
- designs (MW per site ['110', '140', '146', '163', '270', '274']):
    - [0.000, 250.600, 0.000, 185.400, 0.000, 746.400]
    - [338.600, 0.000, 0.000, 185.400, 579.000, 746.400]
    - [0.000, 0.000, 0.000, 185.400, 579.000, 168.077]
    - [0.000, 0.000, 268.000, 185.400, 0.000, 746.400]
    - [0.000, 0.000, 0.000, 185.400, 274.841, 746.400]
    - [6.728, 250.600, 203.946, 185.400, 579.000, 746.400]
    - [0.000, 250.600, 116.202, 185.400, 579.000, 746.400]
    - [0.000, 0.000, 0.000, 185.400, 407.830, 746.400]
- realized Y (['V1', 'E1']):
    - [2.5873e+06, 8.11418e+09]
    - [1.64435e+06, 8.13142e+09]
    - [3.04345e+06, 8.10217e+09]
    - [2.58638e+06, 8.11652e+09]
    - [2.4501e+06, 8.1155e+09]
    - [1.40423e+06, 8.13998e+09]
    - [1.50765e+06, 8.13468e+09]
    - [2.23297e+06, 8.11792e+09]
<!-- END r4 -->
