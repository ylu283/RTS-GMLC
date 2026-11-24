# methods_E arm qnehvi seed_id 3 — ROUND_LOG (prompt 55; acq = qnehvi, base = ['n0_E'] nav prefix n0 = 48, objectives = ['V1', 'E1'])

Ledger: `lanes/house/s1/s3/ledger.json`. stop_rule = record_only: gain_k and
would_stop_k = (gain_k < tau) AND (gain_{k-1} < tau) are graded and logged under tau_joint
(headline) and tau_marginal (recorded) with the joint-vs-marginal sensitivity column; the
rule never halts; every lane runs to hard_cap = 4. tau_joint = 0, tau_marginal = 0 — ZERO: the stop rule is budget-cap-only and the cap governs (plan 3).
E-D5 OPEN: see README.md for the two readings of a fire. Halts ONLY per plan 1.2/1.3
(HALT_FOR_DECISION.md). Acquisition jobs never submit; Kay submits via submit_ready_E.sh.
Stop NOW: `touch lanes/house/s1/s3/STOP` on the CRC clone, then qdel the lane's JIDs.

<!-- BEGIN r1 -->
## Round 1 (methods_E_EMU_house_s1_s3_r1)
- proposed_at: "2026-11-24T08:06:22+00:00"
- wave: "methods_E_EMU_house_s1_s3_r1"
- acq: "qnehvi"
- acq_seed: 20261307
- guardrail_mode: "monitor"
- settings: {"mc_samples": 128, "num_restarts": 20, "raw_samples": 512, "alpha": 0.0, "prune_baseline": true, "sequential": true, "fast_mode": false, "constraint": "none", "guardrail_mode": "monitor", "seed": 20261307, "dtype": "float64", "bound_snaps": {"to_0": 0, "to_1": 0, "tol": 1e-12, "note": "bound cleanup after x * sx + mx; not lattice snapping"}}
- botorch: "0.16.1"
- bo_gp_sha: "60e6328236e745b3d34dc8cd704bb72888ae5d15"
- loo_rms_z: {"V1": 0.4268, "E1": 0.7727}
- noise_raw: {"V1": 14949.051609849952, "E1": 750721.1138779742}
- predictions: "waves/methods_E_EMU_house_s1_s3_r1/predictions.csv"
- graded_at: "2026-11-24T08:06:23+00:00"
- n_train: 56
- n_hv: 55
- cumulative_hv: 131460409299481.19
- gain: 31248482250949.72
- gain_tau_joint: null
- would_stop_joint: false
- gain_tau_marginal: null
- would_stop_marginal: false
- joint_vs_marginal: {"ratio_joint_over_marginal": null, "agree": true, "fires": {"joint": false, "marginal": false}}
- first_fire_round: {"tau_joint": null, "tau_marginal": null}
- n_outside_ref: 0
- violations: ["methods_E_EMU_house_s1_s3_r1:3"]
- suspects: []
- r2_flag: false
- r2_max_mwh: 177.5578492537288
- calibration: {"V1": {"mean_z": 0.002, "rms_z": 0.129, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}, "E1": {"mean_z": 0.025, "rms_z": 0.097, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}}
- C2_review: false
- C3_review: false
- halt: null
- decision: "graded (record_only)"
- qnehvi_seconds: 4.2
- r1_shared_designs_with_seed: {"0": 4, "1": 4, "2": 4, "4": 4}
- designs (MW per site ['110', '140', '146', '163', '270', '274']):
    - [45.641, 0.000, 0.000, 185.400, 579.000, 0.000]
    - [0.000, 250.600, 161.119, 185.400, 579.000, 746.400]
    - [338.600, 0.000, 0.000, 185.400, 579.000, 0.000]
    - [0.000, 0.000, 0.000, 185.400, 579.000, 746.400]
    - [97.573, 250.600, 218.932, 185.400, 579.000, 746.400]
    - [0.000, 250.600, 0.000, 185.400, 579.000, 746.400]
    - [0.000, 0.000, 0.000, 185.400, 0.000, 746.400]
    - [0.000, 0.000, 0.000, 185.400, 258.556, 746.400]
- realized Y (['V1', 'E1']):
    - [3.3276e+06, 8.09361e+09]
    - [1.45387e+06, 8.13762e+09]
    - [2.71507e+06, 8.10815e+09]
    - [2.03988e+06, 8.11867e+09]
    - [1.25914e+06, 8.15127e+09]
    - [1.71551e+06, 8.12632e+09]
    - [2.99108e+06, 8.10467e+09]
    - [2.47582e+06, 8.11524e+09]
<!-- END r1 -->

<!-- BEGIN r2 -->
## Round 2 (methods_E_EMU_house_s1_s3_r2)
- proposed_at: "2026-11-24T08:06:31+00:00"
- wave: "methods_E_EMU_house_s1_s3_r2"
- acq: "qnehvi"
- acq_seed: 20261308
- guardrail_mode: "constrain"
- settings: {"mc_samples": 128, "num_restarts": 20, "raw_samples": 512, "alpha": 0.0, "prune_baseline": true, "sequential": true, "fast_mode": false, "constraint": "shed <= 1.0 MWh (GP on the accumulated R1 column)", "guardrail_mode": "constrain", "seed": 20261308, "dtype": "float64", "bound_snaps": {"to_0": 0, "to_1": 0, "tol": 1e-12, "note": "bound cleanup after x * sx + mx; not lattice snapping"}}
- botorch: "0.16.1"
- bo_gp_sha: "60e6328236e745b3d34dc8cd704bb72888ae5d15"
- loo_rms_z: {"V1": 0.3862, "E1": 0.7179}
- noise_raw: {"V1": 14800.52656432767, "E1": 773637.1151495406}
- predictions: "waves/methods_E_EMU_house_s1_s3_r2/predictions.csv"
- graded_at: "2026-11-24T08:06:32+00:00"
- n_train: 64
- n_hv: 63
- cumulative_hv: 137992236354753.16
- gain: 6531827055271.969
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
- r2_max_mwh: 193.6663339410005
- calibration: {"V1": {"mean_z": 0.003, "rms_z": 0.186, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}, "E1": {"mean_z": 0.053, "rms_z": 0.205, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}}
- C2_review: false
- C3_review: false
- halt: null
- decision: "graded (record_only)"
- qnehvi_seconds: 7.0
- designs (MW per site ['110', '140', '146', '163', '270', '274']):
    - [0.000, 0.000, 0.000, 185.400, 579.000, 313.064]
    - [0.000, 250.600, 0.000, 185.400, 579.000, 0.000]
    - [134.326, 0.000, 0.000, 185.400, 579.000, 0.000]
    - [0.000, 0.000, 0.000, 167.448, 579.000, 0.000]
    - [0.000, 250.600, 73.347, 185.400, 579.000, 746.400]
    - [0.000, 0.000, 0.000, 185.400, 579.000, 506.172]
    - [39.582, 250.600, 199.780, 185.400, 579.000, 746.400]
    - [338.600, 250.600, 120.344, 185.400, 579.000, 746.400]
- realized Y (['V1', 'E1']):
    - [2.71409e+06, 8.10948e+09]
    - [2.97116e+06, 8.10341e+09]
    - [3.13377e+06, 8.09912e+09]
    - [3.47403e+06, 8.09164e+09]
    - [1.5718e+06, 8.13173e+09]
    - [2.34142e+06, 8.11545e+09]
    - [1.34873e+06, 8.14399e+09]
    - [1.19106e+06, 8.15605e+09]
<!-- END r2 -->

<!-- BEGIN r3 -->
## Round 3 (methods_E_EMU_house_s1_s3_r3)
- proposed_at: "2026-11-24T08:06:40+00:00"
- wave: "methods_E_EMU_house_s1_s3_r3"
- acq: "qnehvi"
- acq_seed: 20261309
- guardrail_mode: "constrain"
- settings: {"mc_samples": 128, "num_restarts": 20, "raw_samples": 512, "alpha": 0.0, "prune_baseline": true, "sequential": true, "fast_mode": false, "constraint": "shed <= 1.0 MWh (GP on the accumulated R1 column)", "guardrail_mode": "constrain", "seed": 20261309, "dtype": "float64", "bound_snaps": {"to_0": 8, "to_1": 1, "tol": 1e-12, "note": "bound cleanup after x * sx + mx; not lattice snapping"}}
- botorch: "0.16.1"
- bo_gp_sha: "60e6328236e745b3d34dc8cd704bb72888ae5d15"
- loo_rms_z: {"V1": 0.3543, "E1": 0.7146}
- noise_raw: {"V1": 15343.014030378476, "E1": 779142.5224514635}
- predictions: "waves/methods_E_EMU_house_s1_s3_r3/predictions.csv"
- graded_at: "2026-11-24T08:06:41+00:00"
- n_train: 72
- n_hv: 71
- cumulative_hv: 139172177720543.08
- gain: 1179941365789.9219
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
- r2_max_mwh: 173.93813536935977
- calibration: {"V1": {"mean_z": 0.005, "rms_z": 0.175, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}, "E1": {"mean_z": -0.051, "rms_z": 0.165, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}}
- C2_review: false
- C3_review: false
- halt: null
- decision: "graded (record_only)"
- qnehvi_seconds: 7.6
- designs (MW per site ['110', '140', '146', '163', '270', '274']):
    - [0.000, 87.869, 0.000, 185.400, 579.000, 746.400]
    - [338.600, 0.000, 0.000, 0.000, 0.000, 746.400]
    - [0.000, 250.600, 0.000, 185.400, 0.000, 746.400]
    - [338.600, 0.000, 0.000, 185.400, 0.000, 746.400]
    - [0.000, 0.000, 0.000, 0.000, 579.000, 746.400]
    - [0.000, 0.000, 268.000, 185.400, 0.000, 746.400]
    - [234.758, 0.000, 0.000, 185.400, 579.000, 17.100]
    - [338.600, 0.000, 0.000, 165.383, 579.000, 746.400]
- realized Y (['V1', 'E1']):
    - [1.88603e+06, 8.12211e+09]
    - [2.76922e+06, 8.1096e+09]
    - [2.58893e+06, 8.11417e+09]
    - [2.45873e+06, 8.11624e+09]
    - [2.33397e+06, 8.1175e+09]
    - [2.59342e+06, 8.1164e+09]
    - [2.87565e+06, 8.10541e+09]
    - [1.6448e+06, 8.13181e+09]
<!-- END r3 -->

<!-- BEGIN r4 -->
## Round 4 (methods_E_EMU_house_s1_s3_r4)
- proposed_at: "2026-11-24T08:06:50+00:00"
- wave: "methods_E_EMU_house_s1_s3_r4"
- acq: "qnehvi"
- acq_seed: 20261310
- guardrail_mode: "constrain"
- settings: {"mc_samples": 128, "num_restarts": 20, "raw_samples": 512, "alpha": 0.0, "prune_baseline": true, "sequential": true, "fast_mode": false, "constraint": "shed <= 1.0 MWh (GP on the accumulated R1 column)", "guardrail_mode": "constrain", "seed": 20261310, "dtype": "float64", "bound_snaps": {"to_0": 0, "to_1": 0, "tol": 1e-12, "note": "bound cleanup after x * sx + mx; not lattice snapping"}}
- botorch: "0.16.1"
- bo_gp_sha: "60e6328236e745b3d34dc8cd704bb72888ae5d15"
- loo_rms_z: {"V1": 0.3418, "E1": 0.6965}
- noise_raw: {"V1": 14545.433348316566, "E1": 757242.3766027048}
- predictions: "waves/methods_E_EMU_house_s1_s3_r4/predictions.csv"
- graded_at: "2026-11-24T08:06:51+00:00"
- n_train: 80
- n_hv: 79
- cumulative_hv: 140662726127399.22
- gain: 1490548406856.1406
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
- r2_max_mwh: 202.2689350201982
- calibration: {"V1": {"mean_z": -0.05, "rms_z": 0.179, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}, "E1": {"mean_z": -0.06, "rms_z": 0.398, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}}
- C2_review: false
- C3_review: false
- halt: null
- decision: "graded (record_only)"
- qnehvi_seconds: 7.8
- designs (MW per site ['110', '140', '146', '163', '270', '274']):
    - [338.600, 250.600, 162.239, 185.400, 579.000, 746.400]
    - [0.000, 0.000, 0.000, 185.400, 459.162, 0.000]
    - [9.152, 250.600, 197.814, 185.400, 579.000, 746.400]
    - [82.196, 0.000, 0.000, 185.400, 579.000, 6.997]
    - [0.000, 0.000, 0.000, 185.400, 179.381, 746.400]
    - [0.000, 0.000, 0.000, 185.400, 579.000, 404.618]
    - [0.000, 0.000, 0.000, 185.400, 579.000, 605.450]
    - [0.000, 150.364, 0.000, 185.400, 579.000, 746.400]
- realized Y (['V1', 'E1']):
    - [1.13962e+06, 8.1598e+09]
    - [3.67099e+06, 8.09134e+09]
    - [1.39922e+06, 8.13976e+09]
    - [3.23704e+06, 8.09683e+09]
    - [2.62355e+06, 8.11243e+09]
    - [2.52388e+06, 8.11296e+09]
    - [2.19108e+06, 8.11696e+09]
    - [1.79672e+06, 8.12449e+09]
<!-- END r4 -->
