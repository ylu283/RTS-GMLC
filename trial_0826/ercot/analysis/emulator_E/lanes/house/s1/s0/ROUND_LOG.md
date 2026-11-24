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
- proposed_at: "2026-11-24T07:44:37+00:00"
- wave: "methods_E_EMU_house_s1_s0_r1"
- acq: "qnehvi"
- acq_seed: 20261007
- guardrail_mode: "monitor"
- settings: {"mc_samples": 128, "num_restarts": 20, "raw_samples": 512, "alpha": 0.0, "prune_baseline": true, "sequential": true, "fast_mode": false, "constraint": "none", "guardrail_mode": "monitor", "seed": 20261007, "dtype": "float64"}
- botorch: "0.16.1"
- bo_gp_sha: "60e6328236e745b3d34dc8cd704bb72888ae5d15"
- loo_rms_z: {"V1": 0.4268, "E1": 0.7727}
- noise_raw: {"V1": 14949.051609849952, "E1": 750721.1138779742}
- predictions: "waves/methods_E_EMU_house_s1_s0_r1/predictions.csv"
- graded_at: "2026-11-24T07:44:38+00:00"
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
- qnehvi_seconds: 4.6
- r1_shared_designs_with_seed: {}
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
- proposed_at: "2026-11-24T07:44:46+00:00"
- wave: "methods_E_EMU_house_s1_s0_r2"
- acq: "qnehvi"
- acq_seed: 20261008
- guardrail_mode: "constrain"
- settings: {"mc_samples": 128, "num_restarts": 20, "raw_samples": 512, "alpha": 0.0, "prune_baseline": true, "sequential": true, "fast_mode": false, "constraint": "shed <= 1.0 MWh (GP on the accumulated R1 column)", "guardrail_mode": "constrain", "seed": 20261008, "dtype": "float64"}
- botorch: "0.16.1"
- bo_gp_sha: "60e6328236e745b3d34dc8cd704bb72888ae5d15"
- loo_rms_z: {"V1": 0.3719, "E1": 0.7232}
- noise_raw: {"V1": 14957.373689043627, "E1": 791678.07307028}
- predictions: "waves/methods_E_EMU_house_s1_s0_r2/predictions.csv"
- graded_at: "2026-11-24T07:44:47+00:00"
- n_train: 64
- n_hv: 63
- cumulative_hv: 138070789389625.98
- gain: 7460660105639.766
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
- calibration: {"V1": {"mean_z": 0.056, "rms_z": 0.222, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}, "E1": {"mean_z": 0.013, "rms_z": 0.154, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}}
- C2_review: false
- C3_review: false
- halt: null
- decision: "graded (record_only)"
- qnehvi_seconds: 7.6
- designs (MW per site ['110', '140', '146', '163', '270', '274']):
    - [0.000, 0.000, 0.000, 185.400, 181.107, 746.400]
    - [0.000, 0.000, 0.000, 160.093, 579.000, 0.000]
    - [0.000, 0.000, 0.000, 185.400, 579.000, 455.874]
    - [134.348, 0.000, 0.000, 185.400, 579.000, 0.000]
    - [0.000, 0.000, 0.000, 185.400, 579.000, 285.395]
    - [0.000, 250.600, 72.441, 185.400, 579.000, 746.400]
    - [333.591, 250.600, 126.232, 185.400, 579.000, 746.400]
    - [303.597, 250.600, 17.294, 185.400, 579.000, 746.400]
- realized Y (['V1', 'E1']):
    - [2.61924e+06, 8.11149e+09]
    - [3.49538e+06, 8.09193e+09]
    - [2.43375e+06, 8.11468e+09]
    - [3.13371e+06, 8.09867e+09]
    - [2.77443e+06, 8.1089e+09]
    - [1.57637e+06, 8.13096e+09]
    - [1.18528e+06, 8.15676e+09]
    - [1.38859e+06, 8.14502e+09]
<!-- END r2 -->

<!-- BEGIN r3 -->
## Round 3 (methods_E_EMU_house_s1_s0_r3)
- proposed_at: "2026-11-24T07:44:55+00:00"
- wave: "methods_E_EMU_house_s1_s0_r3"
- acq: "qnehvi"
- acq_seed: 20261009
- guardrail_mode: "constrain"
- settings: {"mc_samples": 128, "num_restarts": 20, "raw_samples": 512, "alpha": 0.0, "prune_baseline": true, "sequential": true, "fast_mode": false, "constraint": "shed <= 1.0 MWh (GP on the accumulated R1 column)", "guardrail_mode": "constrain", "seed": 20261009, "dtype": "float64"}
- botorch: "0.16.1"
- bo_gp_sha: "60e6328236e745b3d34dc8cd704bb72888ae5d15"
- loo_rms_z: {"V1": 0.3436, "E1": 0.7128}
- noise_raw: {"V1": 15209.56439638406, "E1": 801179.2881874004}
- predictions: "waves/methods_E_EMU_house_s1_s0_r3/predictions.csv"
- graded_at: "2026-11-24T07:44:56+00:00"
- n_train: 72
- n_hv: 71
- cumulative_hv: 139893310777709.5
- gain: 1822521388083.5156
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
- calibration: {"V1": {"mean_z": -0.092, "rms_z": 0.227, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}, "E1": {"mean_z": -0.104, "rms_z": 0.18, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}}
- C2_review: false
- C3_review: false
- halt: null
- decision: "graded (record_only)"
- qnehvi_seconds: 7.2
- designs (MW per site ['110', '140', '146', '163', '270', '274']):
    - [0.000, 86.439, 0.000, 185.400, 579.000, 746.400]
    - [0.000, 0.000, 0.000, 0.000, 579.000, 746.400]
    - [338.600, 0.000, 0.000, 0.000, 0.000, 746.400]
    - [38.582, 250.600, 198.419, 185.400, 579.000, 746.400]
    - [338.600, 0.000, 0.000, 185.400, 0.000, 746.400]
    - [0.000, 0.000, 0.000, 185.400, 462.240, 0.000]
    - [0.000, 0.000, 0.000, 71.236, 579.000, 0.000]
    - [180.895, 0.000, 0.000, 185.400, 579.000, 0.000]
- realized Y (['V1', 'E1']):
    - [1.88111e+06, 8.12174e+09]
    - [2.33494e+06, 8.11768e+09]
    - [2.76836e+06, 8.10956e+09]
    - [1.3527e+06, 8.1434e+09]
    - [2.46545e+06, 8.11603e+09]
    - [3.67372e+06, 8.09181e+09]
    - [3.7191e+06, 8.09021e+09]
    - [3.03234e+06, 8.10123e+09]
<!-- END r3 -->

<!-- BEGIN r4 -->
## Round 4 (methods_E_EMU_house_s1_s0_r4)
- proposed_at: "2026-11-24T07:45:05+00:00"
- wave: "methods_E_EMU_house_s1_s0_r4"
- acq: "qnehvi"
- acq_seed: 20261010
- guardrail_mode: "constrain"
- settings: {"mc_samples": 128, "num_restarts": 20, "raw_samples": 512, "alpha": 0.0, "prune_baseline": true, "sequential": true, "fast_mode": false, "constraint": "shed <= 1.0 MWh (GP on the accumulated R1 column)", "guardrail_mode": "constrain", "seed": 20261010, "dtype": "float64"}
- botorch: "0.16.1"
- bo_gp_sha: "60e6328236e745b3d34dc8cd704bb72888ae5d15"
- loo_rms_z: {"V1": 0.3249, "E1": 0.6795}
- noise_raw: {"V1": 15588.46547106437, "E1": 789045.5655083901}
- predictions: "waves/methods_E_EMU_house_s1_s0_r4/predictions.csv"
- graded_at: "2026-11-24T07:45:05+00:00"
- n_train: 80
- n_hv: 79
- cumulative_hv: 141241058310976.66
- gain: 1347747533267.1562
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
- calibration: {"V1": {"mean_z": -0.002, "rms_z": 0.18, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}, "E1": {"mean_z": -0.078, "rms_z": 0.497, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}}
- C2_review: false
- C3_review: false
- halt: null
- decision: "graded (record_only)"
- qnehvi_seconds: 7.8
- designs (MW per site ['110', '140', '146', '163', '270', '274']):
    - [254.257, 0.000, 0.000, 185.400, 579.000, 3.437]
    - [0.000, 250.600, 0.000, 185.400, 0.000, 746.400]
    - [218.436, 250.600, 212.618, 185.400, 579.000, 746.400]
    - [338.600, 0.000, 0.000, 185.400, 579.000, 746.400]
    - [90.597, 0.000, 0.000, 185.400, 579.000, 0.000]
    - [0.000, 0.000, 0.000, 185.400, 383.231, 746.400]
    - [0.000, 250.600, 113.727, 185.400, 579.000, 746.400]
    - [8.449, 250.600, 195.782, 185.400, 579.000, 746.400]
- realized Y (['V1', 'E1']):
    - [2.86614e+06, 8.10476e+09]
    - [2.5836e+06, 8.11426e+09]
    - [1.13236e+06, 8.15933e+09]
    - [1.64545e+06, 8.13133e+09]
    - [3.23667e+06, 8.09641e+09]
    - [2.26637e+06, 8.11755e+09]
    - [1.50988e+06, 8.13469e+09]
    - [1.40232e+06, 8.13922e+09]
<!-- END r4 -->
