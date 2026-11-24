# methods_E arm qnehvi seed_id 1 — ROUND_LOG (prompt 55; acq = qnehvi, base = ['n0_E'] nav prefix n0 = 48, objectives = ['V1', 'E1'])

Ledger: `lanes/house/s1/s1/ledger.json`. stop_rule = record_only: gain_k and
would_stop_k = (gain_k < tau) AND (gain_{k-1} < tau) are graded and logged under tau_joint
(headline) and tau_marginal (recorded) with the joint-vs-marginal sensitivity column; the
rule never halts; every lane runs to hard_cap = 4. tau_joint = 0, tau_marginal = 0 — ZERO: the stop rule is budget-cap-only and the cap governs (plan 3).
E-D5 OPEN: see README.md for the two readings of a fire. Halts ONLY per plan 1.2/1.3
(HALT_FOR_DECISION.md). Acquisition jobs never submit; Kay submits via submit_ready_E.sh.
Stop NOW: `touch lanes/house/s1/s1/STOP` on the CRC clone, then qdel the lane's JIDs.

<!-- BEGIN r1 -->
## Round 1 (methods_E_EMU_house_s1_s1_r1)
- proposed_at: "2026-11-24T07:45:11+00:00"
- wave: "methods_E_EMU_house_s1_s1_r1"
- acq: "qnehvi"
- acq_seed: 20261107
- guardrail_mode: "monitor"
- settings: {"mc_samples": 128, "num_restarts": 20, "raw_samples": 512, "alpha": 0.0, "prune_baseline": true, "sequential": true, "fast_mode": false, "constraint": "none", "guardrail_mode": "monitor", "seed": 20261107, "dtype": "float64"}
- botorch: "0.16.1"
- bo_gp_sha: "60e6328236e745b3d34dc8cd704bb72888ae5d15"
- loo_rms_z: {"V1": 0.4268, "E1": 0.7727}
- noise_raw: {"V1": 14949.051609849952, "E1": 750721.1138779742}
- predictions: "waves/methods_E_EMU_house_s1_s1_r1/predictions.csv"
- graded_at: "2026-11-24T07:45:12+00:00"
- n_train: 56
- n_hv: 55
- cumulative_hv: 132416216371591.34
- gain: 32204289323059.875
- gain_tau_joint: null
- would_stop_joint: false
- gain_tau_marginal: null
- would_stop_marginal: false
- joint_vs_marginal: {"ratio_joint_over_marginal": null, "agree": true, "fires": {"joint": false, "marginal": false}}
- first_fire_round: {"tau_joint": null, "tau_marginal": null}
- n_outside_ref: 0
- violations: ["methods_E_EMU_house_s1_s1_r1:3"]
- suspects: []
- r2_flag: false
- r2_max_mwh: 172.13708904547093
- calibration: {"V1": {"mean_z": 0.01, "rms_z": 0.171, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}, "E1": {"mean_z": -0.035, "rms_z": 0.129, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}}
- C2_review: false
- C3_review: false
- halt: null
- decision: "graded (record_only)"
- qnehvi_seconds: 4.1
- r1_shared_designs_with_seed: {"0": 4}
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
    - [3.33499e+06, 8.09393e+09]
    - [1.45107e+06, 8.13778e+09]
    - [2.71444e+06, 8.10875e+09]
    - [2.04725e+06, 8.11789e+09]
    - [1.70823e+06, 8.12534e+09]
    - [1.25507e+06, 8.15013e+09]
    - [3.00075e+06, 8.10485e+09]
    - [2.48627e+06, 8.11433e+09]
<!-- END r1 -->

<!-- BEGIN r2 -->
## Round 2 (methods_E_EMU_house_s1_s1_r2)
- proposed_at: "2026-11-24T07:45:20+00:00"
- wave: "methods_E_EMU_house_s1_s1_r2"
- acq: "qnehvi"
- acq_seed: 20261108
- guardrail_mode: "constrain"
- settings: {"mc_samples": 128, "num_restarts": 20, "raw_samples": 512, "alpha": 0.0, "prune_baseline": true, "sequential": true, "fast_mode": false, "constraint": "shed <= 1.0 MWh (GP on the accumulated R1 column)", "guardrail_mode": "constrain", "seed": 20261108, "dtype": "float64"}
- botorch: "0.16.1"
- bo_gp_sha: "60e6328236e745b3d34dc8cd704bb72888ae5d15"
- loo_rms_z: {"V1": 0.3725, "E1": 0.7327}
- noise_raw: {"V1": 14787.251830337373, "E1": 779973.664660025}
- predictions: "waves/methods_E_EMU_house_s1_s1_r2/predictions.csv"
- graded_at: "2026-11-24T07:45:21+00:00"
- n_train: 64
- n_hv: 63
- cumulative_hv: 138443453313135.84
- gain: 6027236941544.5
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
- r2_max_mwh: 177.4743959808689
- calibration: {"V1": {"mean_z": 0.048, "rms_z": 0.245, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}, "E1": {"mean_z": 0.074, "rms_z": 0.212, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}}
- C2_review: false
- C3_review: false
- halt: null
- decision: "graded (record_only)"
- qnehvi_seconds: 7.2
- designs (MW per site ['110', '140', '146', '163', '270', '274']):
    - [55.407, 250.600, 0.000, 185.400, 579.000, 0.000]
    - [0.000, 0.000, 0.000, 166.750, 579.000, 0.000]
    - [0.000, 250.600, 73.509, 185.400, 579.000, 746.400]
    - [137.937, 0.000, 0.000, 185.400, 579.000, 0.000]
    - [0.000, 0.000, 0.000, 185.400, 579.000, 345.471]
    - [338.600, 250.600, 122.227, 185.400, 579.000, 746.400]
    - [338.600, 250.600, 10.974, 185.400, 579.000, 746.400]
    - [338.600, 0.000, 0.000, 0.000, 0.000, 746.400]
- realized Y (['V1', 'E1']):
    - [2.86212e+06, 8.10772e+09]
    - [3.47441e+06, 8.09108e+09]
    - [1.57293e+06, 8.13191e+09]
    - [3.13279e+06, 8.09882e+09]
    - [2.64929e+06, 8.11064e+09]
    - [1.18071e+06, 8.15662e+09]
    - [1.39897e+06, 8.14494e+09]
    - [2.76827e+06, 8.10978e+09]
<!-- END r2 -->

<!-- BEGIN r3 -->
## Round 3 (methods_E_EMU_house_s1_s1_r3)
- proposed_at: "2026-11-24T07:45:29+00:00"
- wave: "methods_E_EMU_house_s1_s1_r3"
- acq: "qnehvi"
- acq_seed: 20261109
- guardrail_mode: "constrain"
- settings: {"mc_samples": 128, "num_restarts": 20, "raw_samples": 512, "alpha": 0.0, "prune_baseline": true, "sequential": true, "fast_mode": false, "constraint": "shed <= 1.0 MWh (GP on the accumulated R1 column)", "guardrail_mode": "constrain", "seed": 20261109, "dtype": "float64"}
- botorch: "0.16.1"
- bo_gp_sha: "60e6328236e745b3d34dc8cd704bb72888ae5d15"
- loo_rms_z: {"V1": 0.3632, "E1": 0.7119}
- noise_raw: {"V1": 15233.941921317803, "E1": 809824.4206066683}
- predictions: "waves/methods_E_EMU_house_s1_s1_r3/predictions.csv"
- graded_at: "2026-11-24T07:45:30+00:00"
- n_train: 72
- n_hv: 71
- cumulative_hv: 140772149700912.72
- gain: 2328696387776.875
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
- r2_max_mwh: 173.10467818181496
- calibration: {"V1": {"mean_z": -0.042, "rms_z": 0.209, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}, "E1": {"mean_z": -0.086, "rms_z": 0.277, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}}
- C2_review: false
- C3_review: false
- halt: null
- decision: "graded (record_only)"
- qnehvi_seconds: 7.4
- designs (MW per site ['110', '140', '146', '163', '270', '274']):
    - [0.000, 88.074, 0.000, 185.400, 579.000, 746.400]
    - [0.000, 0.000, 0.000, 0.000, 579.000, 746.400]
    - [223.165, 0.000, 0.000, 185.400, 579.000, 0.000]
    - [0.000, 0.000, 0.000, 81.483, 579.000, 0.000]
    - [0.000, 0.000, 0.000, 185.400, 579.000, 558.664]
    - [45.896, 250.600, 198.553, 185.400, 579.000, 746.400]
    - [214.112, 250.600, 221.030, 185.400, 579.000, 746.400]
    - [92.023, 0.000, 0.000, 185.400, 579.000, 0.000]
- realized Y (['V1', 'E1']):
    - [1.88502e+06, 8.12161e+09]
    - [2.33169e+06, 8.11689e+09]
    - [2.94809e+06, 8.10352e+09]
    - [3.70022e+06, 8.09109e+09]
    - [2.2594e+06, 8.11634e+09]
    - [1.33861e+06, 8.14391e+09]
    - [1.12806e+06, 8.15956e+09]
    - [3.2279e+06, 8.09579e+09]
<!-- END r3 -->

<!-- BEGIN r4 -->
## Round 4 (methods_E_EMU_house_s1_s1_r4)
- proposed_at: "2026-11-24T07:45:39+00:00"
- wave: "methods_E_EMU_house_s1_s1_r4"
- acq: "qnehvi"
- acq_seed: 20261110
- guardrail_mode: "constrain"
- settings: {"mc_samples": 128, "num_restarts": 20, "raw_samples": 512, "alpha": 0.0, "prune_baseline": true, "sequential": true, "fast_mode": false, "constraint": "shed <= 1.0 MWh (GP on the accumulated R1 column)", "guardrail_mode": "constrain", "seed": 20261110, "dtype": "float64"}
- botorch: "0.16.1"
- bo_gp_sha: "60e6328236e745b3d34dc8cd704bb72888ae5d15"
- loo_rms_z: {"V1": 0.3366, "E1": 0.7044}
- noise_raw: {"V1": 15796.818947362983, "E1": 781104.773213933}
- predictions: "waves/methods_E_EMU_house_s1_s1_r4/predictions.csv"
- graded_at: "2026-11-24T07:45:40+00:00"
- n_train: 80
- n_hv: 79
- cumulative_hv: 141548664433771.7
- gain: 776514732858.9688
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
- r2_max_mwh: 179.00123003615033
- calibration: {"V1": {"mean_z": 0.094, "rms_z": 0.19, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}, "E1": {"mean_z": 0.187, "rms_z": 0.338, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}}
- C2_review: false
- C3_review: false
- halt: null
- decision: "graded (record_only)"
- qnehvi_seconds: 8.2
- designs (MW per site ['110', '140', '146', '163', '270', '274']):
    - [0.000, 250.600, 0.000, 185.400, 0.000, 746.400]
    - [0.000, 250.600, 35.209, 185.400, 579.000, 746.400]
    - [11.185, 250.600, 202.397, 185.400, 579.000, 746.400]
    - [0.000, 0.000, 268.000, 185.400, 0.000, 746.400]
    - [0.000, 0.000, 0.000, 185.400, 456.253, 0.000]
    - [0.000, 250.600, 114.515, 185.400, 579.000, 746.400]
    - [128.363, 250.600, 228.055, 185.400, 579.000, 746.400]
    - [0.000, 0.000, 0.000, 185.400, 579.000, 268.877]
- realized Y (['V1', 'E1']):
    - [2.58918e+06, 8.11394e+09]
    - [1.64736e+06, 8.12839e+09]
    - [1.39465e+06, 8.14152e+09]
    - [2.59186e+06, 8.11597e+09]
    - [3.68041e+06, 8.09122e+09]
    - [1.51172e+06, 8.13459e+09]
    - [1.21118e+06, 8.15381e+09]
    - [2.81693e+06, 8.10786e+09]
<!-- END r4 -->
