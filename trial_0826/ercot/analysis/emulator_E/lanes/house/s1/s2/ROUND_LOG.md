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
- proposed_at: "2026-11-24T08:05:44+00:00"
- wave: "methods_E_EMU_house_s1_s2_r1"
- acq: "qnehvi"
- acq_seed: 20261207
- guardrail_mode: "monitor"
- settings: {"mc_samples": 128, "num_restarts": 20, "raw_samples": 512, "alpha": 0.0, "prune_baseline": true, "sequential": true, "fast_mode": false, "constraint": "none", "guardrail_mode": "monitor", "seed": 20261207, "dtype": "float64", "bound_snaps": {"to_0": 0, "to_1": 1, "tol": 1e-12, "note": "bound cleanup after x * sx + mx; not lattice snapping"}}
- botorch: "0.16.1"
- bo_gp_sha: "60e6328236e745b3d34dc8cd704bb72888ae5d15"
- loo_rms_z: {"V1": 0.4268, "E1": 0.7727}
- noise_raw: {"V1": 14949.051609849952, "E1": 750721.1138779742}
- predictions: "waves/methods_E_EMU_house_s1_s2_r1/predictions.csv"
- graded_at: "2026-11-24T08:05:45+00:00"
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
- qnehvi_seconds: 5.3
- r1_shared_designs_with_seed: {"0": 5, "1": 4, "3": 4, "4": 4}
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
- proposed_at: "2026-11-24T08:05:56+00:00"
- wave: "methods_E_EMU_house_s1_s2_r2"
- acq: "qnehvi"
- acq_seed: 20261208
- guardrail_mode: "constrain"
- settings: {"mc_samples": 128, "num_restarts": 20, "raw_samples": 512, "alpha": 0.0, "prune_baseline": true, "sequential": true, "fast_mode": false, "constraint": "shed <= 1.0 MWh (GP on the accumulated R1 column)", "guardrail_mode": "constrain", "seed": 20261208, "dtype": "float64", "bound_snaps": {"to_0": 0, "to_1": 0, "tol": 1e-12, "note": "bound cleanup after x * sx + mx; not lattice snapping"}}
- botorch: "0.16.1"
- bo_gp_sha: "60e6328236e745b3d34dc8cd704bb72888ae5d15"
- loo_rms_z: {"V1": 0.3746, "E1": 0.7199}
- noise_raw: {"V1": 14980.676891602794, "E1": 789802.9475287931}
- predictions: "waves/methods_E_EMU_house_s1_s2_r2/predictions.csv"
- graded_at: "2026-11-24T08:05:57+00:00"
- n_train: 64
- n_hv: 63
- cumulative_hv: 139088769343941.48
- gain: 7762154667038.203
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
- calibration: {"V1": {"mean_z": 0.116, "rms_z": 0.216, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}, "E1": {"mean_z": 0.206, "rms_z": 0.312, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}}
- C2_review: false
- C3_review: false
- halt: null
- decision: "graded (record_only)"
- qnehvi_seconds: 10.0
- designs (MW per site ['110', '140', '146', '163', '270', '274']):
    - [0.000, 0.000, 0.000, 185.400, 579.000, 371.954]
    - [0.000, 0.000, 0.000, 168.859, 579.000, 0.000]
    - [140.758, 0.000, 0.000, 185.400, 579.000, 0.000]
    - [228.547, 0.000, 0.000, 185.400, 579.000, 51.334]
    - [0.000, 250.600, 73.915, 185.400, 579.000, 746.400]
    - [0.000, 0.000, 0.000, 185.400, 579.000, 513.465]
    - [337.375, 250.600, 124.762, 185.400, 579.000, 746.400]
    - [32.818, 250.600, 210.661, 185.400, 579.000, 746.400]
- realized Y (['V1', 'E1']):
    - [2.58849e+06, 8.11176e+09]
    - [3.47617e+06, 8.09124e+09]
    - [3.12238e+06, 8.0997e+09]
    - [2.81828e+06, 8.10721e+09]
    - [1.57338e+06, 8.13177e+09]
    - [2.33495e+06, 8.11583e+09]
    - [1.18627e+06, 8.15649e+09]
    - [1.34503e+06, 8.1439e+09]
<!-- END r2 -->

<!-- BEGIN r3 -->
## Round 3 (methods_E_EMU_house_s1_s2_r3)
- proposed_at: "2026-11-24T08:06:06+00:00"
- wave: "methods_E_EMU_house_s1_s2_r3"
- acq: "qnehvi"
- acq_seed: 20261209
- guardrail_mode: "constrain"
- settings: {"mc_samples": 128, "num_restarts": 20, "raw_samples": 512, "alpha": 0.0, "prune_baseline": true, "sequential": true, "fast_mode": false, "constraint": "shed <= 1.0 MWh (GP on the accumulated R1 column)", "guardrail_mode": "constrain", "seed": 20261209, "dtype": "float64", "bound_snaps": {"to_0": 0, "to_1": 0, "tol": 1e-12, "note": "bound cleanup after x * sx + mx; not lattice snapping"}}
- botorch: "0.16.1"
- bo_gp_sha: "60e6328236e745b3d34dc8cd704bb72888ae5d15"
- loo_rms_z: {"V1": 0.3536, "E1": 0.733}
- noise_raw: {"V1": 15404.283088295848, "E1": 781689.0595474755}
- predictions: "waves/methods_E_EMU_house_s1_s2_r3/predictions.csv"
- graded_at: "2026-11-24T08:06:07+00:00"
- n_train: 72
- n_hv: 71
- cumulative_hv: 140388846379217.48
- gain: 1300077035276.0
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
- calibration: {"V1": {"mean_z": -0.001, "rms_z": 0.201, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}, "E1": {"mean_z": -0.038, "rms_z": 0.139, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}}
- C2_review: false
- C3_review: false
- halt: null
- decision: "graded (record_only)"
- qnehvi_seconds: 8.1
- designs (MW per site ['110', '140', '146', '163', '270', '274']):
    - [338.600, 0.000, 0.000, 185.400, 0.000, 746.400]
    - [0.000, 87.929, 0.000, 185.400, 579.000, 746.400]
    - [0.000, 0.000, 0.000, 0.000, 579.000, 746.400]
    - [338.600, 0.000, 0.000, 0.000, 0.000, 746.400]
    - [338.600, 0.000, 0.000, 185.400, 579.000, 746.400]
    - [0.000, 250.600, 0.000, 185.400, 0.000, 746.400]
    - [0.000, 0.000, 0.000, 185.400, 579.000, 87.436]
    - [0.000, 0.000, 0.000, 81.816, 579.000, 0.000]
- realized Y (['V1', 'E1']):
    - [2.46351e+06, 8.11704e+09]
    - [1.88318e+06, 8.12175e+09]
    - [2.33807e+06, 8.11803e+09]
    - [2.77273e+06, 8.11002e+09]
    - [1.63876e+06, 8.13115e+09]
    - [2.58051e+06, 8.11352e+09]
    - [3.23208e+06, 8.09678e+09]
    - [3.69627e+06, 8.09029e+09]
<!-- END r3 -->

<!-- BEGIN r4 -->
## Round 4 (methods_E_EMU_house_s1_s2_r4)
- proposed_at: "2026-11-24T08:06:16+00:00"
- wave: "methods_E_EMU_house_s1_s2_r4"
- acq: "qnehvi"
- acq_seed: 20261210
- guardrail_mode: "constrain"
- settings: {"mc_samples": 128, "num_restarts": 20, "raw_samples": 512, "alpha": 0.0, "prune_baseline": true, "sequential": true, "fast_mode": false, "constraint": "shed <= 1.0 MWh (GP on the accumulated R1 column)", "guardrail_mode": "constrain", "seed": 20261210, "dtype": "float64", "bound_snaps": {"to_0": 0, "to_1": 0, "tol": 1e-12, "note": "bound cleanup after x * sx + mx; not lattice snapping"}}
- botorch: "0.16.1"
- bo_gp_sha: "60e6328236e745b3d34dc8cd704bb72888ae5d15"
- loo_rms_z: {"V1": 0.3314, "E1": 0.7067}
- noise_raw: {"V1": 15144.257121948944, "E1": 787099.4512792546}
- predictions: "waves/methods_E_EMU_house_s1_s2_r4/predictions.csv"
- graded_at: "2026-11-24T08:06:16+00:00"
- n_train: 80
- n_hv: 79
- cumulative_hv: 141564603385665.97
- gain: 1175757006448.4844
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
- calibration: {"V1": {"mean_z": 0.188, "rms_z": 0.293, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}, "E1": {"mean_z": 0.06, "rms_z": 0.263, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}}
- C2_review: false
- C3_review: false
- halt: null
- decision: "graded (record_only)"
- qnehvi_seconds: 8.1
- designs (MW per site ['110', '140', '146', '163', '270', '274']):
    - [0.000, 0.000, 0.000, 185.400, 267.318, 746.400]
    - [204.729, 250.600, 229.794, 185.400, 579.000, 746.400]
    - [0.000, 0.000, 0.000, 185.400, 407.401, 746.400]
    - [183.146, 0.000, 0.000, 185.400, 579.000, 0.000]
    - [0.000, 0.000, 0.000, 185.400, 142.946, 746.400]
    - [257.237, 0.000, 0.000, 185.400, 579.000, 0.000]
    - [0.000, 250.600, 115.240, 185.400, 579.000, 746.400]
    - [60.683, 250.600, 219.790, 185.400, 579.000, 746.400]
- realized Y (['V1', 'E1']):
    - [2.45939e+06, 8.1152e+09]
    - [1.13275e+06, 8.1592e+09]
    - [2.2315e+06, 8.11766e+09]
    - [3.02706e+06, 8.10152e+09]
    - [2.70277e+06, 8.11111e+09]
    - [2.87677e+06, 8.1047e+09]
    - [1.509e+06, 8.13461e+09]
    - [1.30553e+06, 8.14707e+09]
<!-- END r4 -->
