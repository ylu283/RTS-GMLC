# methods_E arm qnehvi seed_id 1 — ROUND_LOG (prompt 55; acq = qnehvi, base = ['n0_E'] nav prefix n0 = 48, objectives = ['V1', 'E1'])

Ledger: `lanes/house/s0/s1/ledger.json`. stop_rule = record_only: gain_k and
would_stop_k = (gain_k < tau) AND (gain_{k-1} < tau) are graded and logged under tau_joint
(headline) and tau_marginal (recorded) with the joint-vs-marginal sensitivity column; the
rule never halts; every lane runs to hard_cap = 4. tau_joint = 0, tau_marginal = 0 — ZERO: the stop rule is budget-cap-only and the cap governs (plan 3).
E-D5 OPEN: see README.md for the two readings of a fire. Halts ONLY per plan 1.2/1.3
(HALT_FOR_DECISION.md). Acquisition jobs never submit; Kay submits via submit_ready_E.sh.
Stop NOW: `touch lanes/house/s0/s1/STOP` on the CRC clone, then qdel the lane's JIDs.

<!-- BEGIN r1 -->
## Round 1 (methods_E_EMU_house_s0_s1_r1)
- proposed_at: "2026-11-24T08:04:53+00:00"
- wave: "methods_E_EMU_house_s0_s1_r1"
- acq: "qnehvi"
- acq_seed: 20261107
- guardrail_mode: "monitor"
- settings: {"mc_samples": 128, "num_restarts": 20, "raw_samples": 512, "alpha": 0.0, "prune_baseline": true, "sequential": true, "fast_mode": false, "constraint": "none", "guardrail_mode": "monitor", "seed": 20261107, "dtype": "float64", "bound_snaps": {"to_0": 0, "to_1": 0, "tol": 1e-12, "note": "bound cleanup after x * sx + mx; not lattice snapping"}}
- botorch: "0.16.1"
- bo_gp_sha: "60e6328236e745b3d34dc8cd704bb72888ae5d15"
- loo_rms_z: {"V1": 0.4268, "E1": 0.7727}
- noise_raw: {"V1": 14949.051609849952, "E1": 750721.1138779742}
- predictions: "waves/methods_E_EMU_house_s0_s1_r1/predictions.csv"
- graded_at: "2026-11-24T08:04:54+00:00"
- n_train: 56
- n_hv: 56
- cumulative_hv: 134098591145598.9
- gain: 33886664097067.438
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
- r2_max_mwh: 167.82846488137113
- calibration: {"V1": {"mean_z": -0.035, "rms_z": 0.173, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}, "E1": {"mean_z": -0.034, "rms_z": 0.156, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}}
- C2_review: false
- C3_review: false
- halt: null
- decision: "graded (record_only)"
- qnehvi_seconds: 5.6
- r1_shared_designs_with_seed: {"0": 4, "2": 4, "3": 4, "4": 4}
- designs (MW per site ['110', '140', '146', '163', '270', '274']):
    - [45.589, 0.000, 0.000, 185.400, 579.000, 0.000]
    - [0.000, 250.600, 163.837, 185.400, 579.000, 746.400]
    - [338.600, 0.000, 0.000, 185.400, 579.000, 0.000]
    - [0.000, 0.000, 0.000, 185.400, 579.000, 746.400]
    - [0.000, 250.600, 0.000, 185.400, 579.000, 746.400]
    - [99.775, 250.600, 211.964, 185.400, 579.000, 746.400]
    - [0.000, 0.000, 0.000, 185.400, 0.000, 746.400]
    - [0.000, 0.000, 0.000, 185.400, 248.353, 746.400]
- realized Y (['V1', 'E1']):
    - [3.33679e+06, 8.0941e+09]
    - [1.44613e+06, 8.13765e+09]
    - [2.71366e+06, 8.10916e+09]
    - [2.03187e+06, 8.11751e+09]
    - [1.70969e+06, 8.12551e+09]
    - [1.25306e+06, 8.15016e+09]
    - [2.99252e+06, 8.10492e+09]
    - [2.49236e+06, 8.11432e+09]
<!-- END r1 -->

<!-- BEGIN r2 -->
## Round 2 (methods_E_EMU_house_s0_s1_r2)
- proposed_at: "2026-11-24T08:05:01+00:00"
- wave: "methods_E_EMU_house_s0_s1_r2"
- acq: "qnehvi"
- acq_seed: 20261108
- guardrail_mode: "monitor"
- settings: {"mc_samples": 128, "num_restarts": 20, "raw_samples": 512, "alpha": 0.0, "prune_baseline": true, "sequential": true, "fast_mode": false, "constraint": "none", "guardrail_mode": "monitor", "seed": 20261108, "dtype": "float64", "bound_snaps": {"to_0": 8, "to_1": 0, "tol": 1e-12, "note": "bound cleanup after x * sx + mx; not lattice snapping"}}
- botorch: "0.16.1"
- bo_gp_sha: "60e6328236e745b3d34dc8cd704bb72888ae5d15"
- loo_rms_z: {"V1": 0.3846, "E1": 0.7334}
- noise_raw: {"V1": 14839.262067586, "E1": 781072.751025736}
- predictions: "waves/methods_E_EMU_house_s0_s1_r2/predictions.csv"
- graded_at: "2026-11-24T08:05:02+00:00"
- n_train: 64
- n_hv: 64
- cumulative_hv: 139043516667630.36
- gain: 4944925522031.453
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
- r2_max_mwh: 171.02808890292454
- calibration: {"V1": {"mean_z": -0.016, "rms_z": 0.147, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}, "E1": {"mean_z": 0.104, "rms_z": 0.235, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}}
- C2_review: false
- C3_review: false
- halt: null
- decision: "graded (record_only)"
- qnehvi_seconds: 5.2
- designs (MW per site ['110', '140', '146', '163', '270', '274']):
    - [0.000, 250.600, 0.000, 185.400, 579.000, 0.000]
    - [0.000, 250.600, 73.607, 185.400, 579.000, 746.400]
    - [0.000, 0.000, 0.000, 165.237, 579.000, 0.000]
    - [0.000, 0.000, 0.000, 185.400, 579.000, 122.587]
    - [338.600, 250.600, 125.118, 185.400, 579.000, 746.400]
    - [42.063, 250.600, 194.593, 185.400, 579.000, 746.400]
    - [0.000, 0.000, 0.000, 0.000, 579.000, 746.400]
    - [0.000, 87.427, 0.000, 185.400, 579.000, 746.400]
- realized Y (['V1', 'E1']):
    - [2.97467e+06, 8.10437e+09]
    - [1.57276e+06, 8.13124e+09]
    - [3.48991e+06, 8.09193e+09]
    - [3.14355e+06, 8.09892e+09]
    - [1.18331e+06, 8.15623e+09]
    - [1.34466e+06, 8.14428e+09]
    - [2.33692e+06, 8.11772e+09]
    - [1.88223e+06, 8.12173e+09]
<!-- END r2 -->

<!-- BEGIN r3 -->
## Round 3 (methods_E_EMU_house_s0_s1_r3)
- proposed_at: "2026-11-24T08:05:08+00:00"
- wave: "methods_E_EMU_house_s0_s1_r3"
- acq: "qnehvi"
- acq_seed: 20261109
- guardrail_mode: "monitor"
- settings: {"mc_samples": 128, "num_restarts": 20, "raw_samples": 512, "alpha": 0.0, "prune_baseline": true, "sequential": true, "fast_mode": false, "constraint": "none", "guardrail_mode": "monitor", "seed": 20261109, "dtype": "float64", "bound_snaps": {"to_0": 0, "to_1": 0, "tol": 1e-12, "note": "bound cleanup after x * sx + mx; not lattice snapping"}}
- botorch: "0.16.1"
- bo_gp_sha: "60e6328236e745b3d34dc8cd704bb72888ae5d15"
- loo_rms_z: {"V1": 0.3448, "E1": 0.7284}
- noise_raw: {"V1": 15621.947770660838, "E1": 789273.4597603735}
- predictions: "waves/methods_E_EMU_house_s0_s1_r3/predictions.csv"
- graded_at: "2026-11-24T08:05:09+00:00"
- n_train: 72
- n_hv: 72
- cumulative_hv: 140438806102391.73
- gain: 1395289434761.375
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
- r2_max_mwh: 165.25908729926874
- calibration: {"V1": {"mean_z": 0.065, "rms_z": 0.198, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}, "E1": {"mean_z": 0.087, "rms_z": 0.329, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}}
- C2_review: false
- C3_review: false
- halt: null
- decision: "graded (record_only)"
- qnehvi_seconds: 5.7
- designs (MW per site ['110', '140', '146', '163', '270', '274']):
    - [0.000, 0.000, 0.000, 185.400, 579.000, 489.362]
    - [0.000, 0.000, 0.000, 76.753, 579.000, 0.000]
    - [338.600, 0.000, 0.000, 0.000, 0.000, 746.400]
    - [0.000, 0.000, 0.000, 185.400, 579.000, 246.916]
    - [0.000, 0.000, 0.000, 185.400, 579.000, 373.368]
    - [173.734, 0.000, 0.000, 185.400, 579.000, 0.000]
    - [0.000, 0.000, 0.000, 185.400, 472.337, 0.000]
    - [338.600, 0.000, 0.000, 185.400, 0.000, 746.400]
- realized Y (['V1', 'E1']):
    - [2.37303e+06, 8.11514e+09]
    - [3.71365e+06, 8.09114e+09]
    - [2.77408e+06, 8.10975e+09]
    - [2.86129e+06, 8.10648e+09]
    - [2.58574e+06, 8.11256e+09]
    - [3.04921e+06, 8.10087e+09]
    - [3.64722e+06, 8.09128e+09]
    - [2.46231e+06, 8.11574e+09]
<!-- END r3 -->

<!-- BEGIN r4 -->
## Round 4 (methods_E_EMU_house_s0_s1_r4)
- proposed_at: "2026-11-24T08:05:17+00:00"
- wave: "methods_E_EMU_house_s0_s1_r4"
- acq: "qnehvi"
- acq_seed: 20261110
- guardrail_mode: "monitor"
- settings: {"mc_samples": 128, "num_restarts": 20, "raw_samples": 512, "alpha": 0.0, "prune_baseline": true, "sequential": true, "fast_mode": false, "constraint": "none", "guardrail_mode": "monitor", "seed": 20261110, "dtype": "float64", "bound_snaps": {"to_0": 0, "to_1": 0, "tol": 1e-12, "note": "bound cleanup after x * sx + mx; not lattice snapping"}}
- botorch: "0.16.1"
- bo_gp_sha: "60e6328236e745b3d34dc8cd704bb72888ae5d15"
- loo_rms_z: {"V1": 0.3306, "E1": 0.7091}
- noise_raw: {"V1": 15258.827396446426, "E1": 798276.3164090121}
- predictions: "waves/methods_E_EMU_house_s0_s1_r4/predictions.csv"
- graded_at: "2026-11-24T08:05:18+00:00"
- n_train: 80
- n_hv: 80
- cumulative_hv: 141159354161405.5
- gain: 720548059013.7656
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
- r2_max_mwh: 186.73979502963584
- calibration: {"V1": {"mean_z": 0.08, "rms_z": 0.33, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}, "E1": {"mean_z": 0.072, "rms_z": 0.289, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}}
- C2_review: false
- C3_review: false
- halt: null
- decision: "graded (record_only)"
- qnehvi_seconds: 6.4
- designs (MW per site ['110', '140', '146', '163', '270', '274']):
    - [338.600, 0.000, 0.000, 185.400, 579.000, 746.400]
    - [229.616, 250.600, 211.923, 185.400, 579.000, 746.400]
    - [338.600, 79.747, 0.000, 185.400, 579.000, 746.400]
    - [0.000, 250.600, 34.287, 185.400, 579.000, 746.400]
    - [0.000, 144.868, 0.000, 185.400, 579.000, 746.400]
    - [0.000, 250.600, 0.000, 185.400, 0.000, 746.400]
    - [76.399, 250.600, 192.888, 185.400, 579.000, 746.400]
    - [0.000, 0.000, 268.000, 185.400, 0.000, 746.400]
- realized Y (['V1', 'E1']):
    - [1.64405e+06, 8.1322e+09]
    - [1.12052e+06, 8.1595e+09]
    - [1.52359e+06, 8.13729e+09]
    - [1.64926e+06, 8.12896e+09]
    - [1.80153e+06, 8.12376e+09]
    - [2.58726e+06, 8.11447e+09]
    - [1.29703e+06, 8.14681e+09]
    - [2.59181e+06, 8.11597e+09]
<!-- END r4 -->
