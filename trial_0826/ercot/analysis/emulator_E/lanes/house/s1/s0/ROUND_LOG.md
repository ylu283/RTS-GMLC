# methods_E arm qnehvi seed_id 0 — ROUND_LOG (prompt 55; acq = qnehvi, base = ['n0_E'] nav prefix n0 = 48, objectives = ['V1', 'E1'])

Ledger: `lanes/house/s1/s0/ledger.json`. stop_rule = record_only: gain_k and
would_stop_k = (gain_k < tau) AND (gain_{k-1} < tau) are graded and logged under tau_joint
(headline) and tau_marginal (recorded) with the joint-vs-marginal sensitivity column; the
rule never halts; every lane runs to hard_cap = 4. tau_joint = 0, tau_marginal = 0 — ZERO: the stop rule is budget-cap-only and the cap governs (plan 3).
E-D5 OPEN: see README.md for the two readings of a fire. Halts ONLY per plan 1.2/1.3
(HALT_FOR_DECISION.md). Acquisition jobs never submit; Kay submits via submit_ready_E.sh.
Stop NOW: `touch lanes/house/s1/s0/STOP` on the CRC clone, then qdel the lane's JIDs.

<!-- BEGIN r1 -->
## Round 1 (methods_E_EMU_house_s1_s0_r1)
- proposed_at: "2026-11-24T08:04:18+00:00"
- wave: "methods_E_EMU_house_s1_s0_r1"
- acq: "qnehvi"
- acq_seed: 20261007
- guardrail_mode: "monitor"
- settings: {"mc_samples": 128, "num_restarts": 20, "raw_samples": 512, "alpha": 0.0, "prune_baseline": true, "sequential": true, "fast_mode": false, "constraint": "none", "guardrail_mode": "monitor", "seed": 20261007, "dtype": "float64", "bound_snaps": {"to_0": 0, "to_1": 1, "tol": 1e-12, "note": "bound cleanup after x * sx + mx; not lattice snapping"}}
- botorch: "0.16.1"
- bo_gp_sha: "60e6328236e745b3d34dc8cd704bb72888ae5d15"
- loo_rms_z: {"V1": 0.4268, "E1": 0.7727}
- noise_raw: {"V1": 14949.051609849952, "E1": 750721.1138779742}
- predictions: "waves/methods_E_EMU_house_s1_s0_r1/predictions.csv"
- graded_at: "2026-11-24T08:04:19+00:00"
- n_train: 56
- n_hv: 55
- cumulative_hv: 130610129283986.22
- gain: 30398202235454.75
- gain_tau_joint: null
- would_stop_joint: false
- gain_tau_marginal: null
- would_stop_marginal: false
- joint_vs_marginal: {"ratio_joint_over_marginal": null, "agree": true, "fires": {"joint": false, "marginal": false}}
- first_fire_round: {"tau_joint": null, "tau_marginal": null}
- n_outside_ref: 0
- violations: ["methods_E_EMU_house_s1_s0_r1:3"]
- suspects: []
- r2_flag: false
- r2_max_mwh: 168.68108920895827
- calibration: {"V1": {"mean_z": -0.001, "rms_z": 0.18, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}, "E1": {"mean_z": -0.021, "rms_z": 0.111, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}}
- C2_review: false
- C3_review: false
- halt: null
- decision: "graded (record_only)"
- qnehvi_seconds: 5.3
- r1_shared_designs_with_seed: {"1": 4, "2": 5, "3": 4, "4": 4}
- designs (MW per site ['110', '140', '146', '163', '270', '274']):
    - [45.590, 0.000, 0.000, 185.400, 579.000, 0.000]
    - [0.000, 250.600, 158.408, 185.400, 579.000, 746.400]
    - [338.600, 0.000, 0.000, 185.400, 579.000, 0.000]
    - [0.000, 0.000, 0.000, 185.400, 579.000, 746.400]
    - [96.867, 250.600, 214.118, 185.400, 579.000, 746.400]
    - [0.000, 250.600, 0.000, 185.400, 579.000, 746.400]
    - [0.000, 250.600, 0.000, 185.400, 579.000, 0.000]
    - [0.000, 0.000, 0.000, 185.400, 0.000, 746.400]
- realized Y (['V1', 'E1']):
    - [3.33878e+06, 8.09407e+09]
    - [1.45146e+06, 8.13688e+09]
    - [2.72074e+06, 8.109e+09]
    - [2.04565e+06, 8.11835e+09]
    - [1.2558e+06, 8.15046e+09]
    - [1.71109e+06, 8.12556e+09]
    - [2.97506e+06, 8.10449e+09]
    - [2.99795e+06, 8.1043e+09]
<!-- END r1 -->

<!-- BEGIN r2 -->
## Round 2 (methods_E_EMU_house_s1_s0_r2)
- proposed_at: "2026-11-24T08:04:29+00:00"
- wave: "methods_E_EMU_house_s1_s0_r2"
- acq: "qnehvi"
- acq_seed: 20261008
- guardrail_mode: "constrain"
- settings: {"mc_samples": 128, "num_restarts": 20, "raw_samples": 512, "alpha": 0.0, "prune_baseline": true, "sequential": true, "fast_mode": false, "constraint": "shed <= 1.0 MWh (GP on the accumulated R1 column)", "guardrail_mode": "constrain", "seed": 20261008, "dtype": "float64", "bound_snaps": {"to_0": 0, "to_1": 0, "tol": 1e-12, "note": "bound cleanup after x * sx + mx; not lattice snapping"}}
- botorch: "0.16.1"
- bo_gp_sha: "60e6328236e745b3d34dc8cd704bb72888ae5d15"
- loo_rms_z: {"V1": 0.3719, "E1": 0.7232}
- noise_raw: {"V1": 14957.373689043648, "E1": 791678.0730702803}
- predictions: "waves/methods_E_EMU_house_s1_s0_r2/predictions.csv"
- graded_at: "2026-11-24T08:04:30+00:00"
- n_train: 64
- n_hv: 63
- cumulative_hv: 138318905839906.2
- gain: 7708776555919.984
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
- r2_max_mwh: 174.13268022130015
- calibration: {"V1": {"mean_z": -0.031, "rms_z": 0.17, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}, "E1": {"mean_z": -0.0, "rms_z": 0.163, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}}
- C2_review: false
- C3_review: false
- halt: null
- decision: "graded (record_only)"
- qnehvi_seconds: 9.5
- designs (MW per site ['110', '140', '146', '163', '270', '274']):
    - [0.000, 0.000, 0.000, 185.400, 181.107, 746.400]
    - [0.000, 0.000, 0.000, 160.093, 579.000, 0.000]
    - [0.000, 0.000, 0.000, 185.400, 579.000, 455.874]
    - [134.348, 0.000, 0.000, 185.400, 579.000, 0.000]
    - [0.000, 0.000, 0.000, 185.400, 579.000, 285.395]
    - [0.000, 250.600, 72.441, 185.400, 579.000, 746.400]
    - [333.591, 250.600, 126.232, 185.400, 579.000, 746.400]
    - [0.000, 85.943, 0.000, 185.400, 579.000, 746.400]
- realized Y (['V1', 'E1']):
    - [2.61924e+06, 8.11149e+09]
    - [3.49538e+06, 8.09193e+09]
    - [2.43375e+06, 8.11468e+09]
    - [3.13371e+06, 8.09867e+09]
    - [2.77443e+06, 8.1089e+09]
    - [1.57637e+06, 8.13096e+09]
    - [1.18528e+06, 8.15676e+09]
    - [1.88827e+06, 8.12181e+09]
<!-- END r2 -->

<!-- BEGIN r3 -->
## Round 3 (methods_E_EMU_house_s1_s0_r3)
- proposed_at: "2026-11-24T08:04:42+00:00"
- wave: "methods_E_EMU_house_s1_s0_r3"
- acq: "qnehvi"
- acq_seed: 20261009
- guardrail_mode: "constrain"
- settings: {"mc_samples": 128, "num_restarts": 20, "raw_samples": 512, "alpha": 0.0, "prune_baseline": true, "sequential": true, "fast_mode": false, "constraint": "shed <= 1.0 MWh (GP on the accumulated R1 column)", "guardrail_mode": "constrain", "seed": 20261009, "dtype": "float64", "bound_snaps": {"to_0": 0, "to_1": 0, "tol": 1e-12, "note": "bound cleanup after x * sx + mx; not lattice snapping"}}
- botorch: "0.16.1"
- bo_gp_sha: "60e6328236e745b3d34dc8cd704bb72888ae5d15"
- loo_rms_z: {"V1": 0.3477, "E1": 0.7145}
- noise_raw: {"V1": 14914.127772584543, "E1": 787265.490971865}
- predictions: "waves/methods_E_EMU_house_s1_s0_r3/predictions.csv"
- graded_at: "2026-11-24T08:04:43+00:00"
- n_train: 72
- n_hv: 71
- cumulative_hv: 140305098748282.62
- gain: 1986192908376.4219
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
- r2_max_mwh: 200.99543643060215
- calibration: {"V1": {"mean_z": -0.024, "rms_z": 0.155, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}, "E1": {"mean_z": -0.044, "rms_z": 0.229, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}}
- C2_review: false
- C3_review: false
- halt: null
- decision: "graded (record_only)"
- qnehvi_seconds: 11.1
- designs (MW per site ['110', '140', '146', '163', '270', '274']):
    - [36.297, 250.600, 200.712, 185.400, 579.000, 746.400]
    - [338.600, 0.000, 0.000, 0.000, 0.000, 746.400]
    - [338.600, 0.000, 0.000, 185.400, 0.000, 746.400]
    - [0.000, 0.000, 0.000, 72.990, 579.000, 0.000]
    - [0.000, 0.000, 0.000, 0.000, 579.000, 746.400]
    - [241.833, 0.000, 0.000, 185.400, 579.000, 0.000]
    - [179.736, 0.000, 0.000, 185.400, 579.000, 0.000]
    - [0.000, 250.600, 35.234, 185.400, 579.000, 746.400]
- realized Y (['V1', 'E1']):
    - [1.34961e+06, 8.14326e+09]
    - [2.77072e+06, 8.11025e+09]
    - [2.45712e+06, 8.11585e+09]
    - [3.71692e+06, 8.09053e+09]
    - [2.34089e+06, 8.11717e+09]
    - [2.91025e+06, 8.10499e+09]
    - [3.03552e+06, 8.10086e+09]
    - [1.63859e+06, 8.12844e+09]
<!-- END r3 -->

<!-- BEGIN r4 -->
## Round 4 (methods_E_EMU_house_s1_s0_r4)
- proposed_at: "2026-11-24T08:04:55+00:00"
- wave: "methods_E_EMU_house_s1_s0_r4"
- acq: "qnehvi"
- acq_seed: 20261010
- guardrail_mode: "constrain"
- settings: {"mc_samples": 128, "num_restarts": 20, "raw_samples": 512, "alpha": 0.0, "prune_baseline": true, "sequential": true, "fast_mode": false, "constraint": "shed <= 1.0 MWh (GP on the accumulated R1 column)", "guardrail_mode": "constrain", "seed": 20261010, "dtype": "float64", "bound_snaps": {"to_0": 0, "to_1": 0, "tol": 1e-12, "note": "bound cleanup after x * sx + mx; not lattice snapping"}}
- botorch: "0.16.1"
- bo_gp_sha: "60e6328236e745b3d34dc8cd704bb72888ae5d15"
- loo_rms_z: {"V1": 0.3234, "E1": 0.6894}
- noise_raw: {"V1": 15172.60498994087, "E1": 746044.0483627566}
- predictions: "waves/methods_E_EMU_house_s1_s0_r4/predictions.csv"
- graded_at: "2026-11-24T08:04:56+00:00"
- n_train: 80
- n_hv: 79
- cumulative_hv: 141399654406471.38
- gain: 1094555658188.75
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
- r2_max_mwh: 178.02997345896534
- calibration: {"V1": {"mean_z": -0.041, "rms_z": 0.248, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}, "E1": {"mean_z": -0.064, "rms_z": 0.591, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}}
- C2_review: false
- C3_review: false
- halt: null
- decision: "graded (record_only)"
- qnehvi_seconds: 10.4
- designs (MW per site ['110', '140', '146', '163', '270', '274']):
    - [219.124, 250.600, 212.202, 185.400, 579.000, 746.400]
    - [0.000, 250.600, 0.000, 185.400, 0.000, 746.400]
    - [2.656, 250.600, 206.100, 185.400, 579.000, 746.400]
    - [0.000, 0.000, 268.000, 185.400, 0.000, 746.400]
    - [0.000, 0.000, 0.000, 185.400, 391.564, 746.400]
    - [277.496, 0.000, 0.000, 185.400, 579.000, 0.774]
    - [0.000, 250.600, 112.719, 185.400, 579.000, 746.400]
    - [60.773, 250.600, 216.144, 185.400, 579.000, 746.400]
- realized Y (['V1', 'E1']):
    - [1.12529e+06, 8.15877e+09]
    - [2.5836e+06, 8.11426e+09]
    - [1.40773e+06, 8.1402e+09]
    - [2.59263e+06, 8.11622e+09]
    - [2.25452e+06, 8.11751e+09]
    - [2.83179e+06, 8.1063e+09]
    - [1.51131e+06, 8.13462e+09]
    - [1.30295e+06, 8.14566e+09]
<!-- END r4 -->
