# methods_E arm qnehvi seed_id 4 — ROUND_LOG (prompt 55; acq = qnehvi, base = ['n0_E'] nav prefix n0 = 48, objectives = ['V1', 'E1'])

Ledger: `lanes/house/s0/s4/ledger.json`. stop_rule = record_only: gain_k and
would_stop_k = (gain_k < tau) AND (gain_{k-1} < tau) are graded and logged under tau_joint
(headline) and tau_marginal (recorded) with the joint-vs-marginal sensitivity column; the
rule never halts; every lane runs to hard_cap = 4. tau_joint = 0, tau_marginal = 0 — ZERO: the stop rule is budget-cap-only and the cap governs (plan 3).
E-D5 OPEN: see README.md for the two readings of a fire. Halts ONLY per plan 1.2/1.3
(HALT_FOR_DECISION.md). Acquisition jobs never submit; Kay submits via submit_ready_E.sh.
Stop NOW: `touch lanes/house/s0/s4/STOP` on the CRC clone, then qdel the lane's JIDs.

<!-- BEGIN r1 -->
## Round 1 (methods_E_EMU_house_s0_s4_r1)
- proposed_at: "2026-11-24T07:46:20+00:00"
- wave: "methods_E_EMU_house_s0_s4_r1"
- acq: "qnehvi"
- acq_seed: 20261407
- guardrail_mode: "monitor"
- settings: {"mc_samples": 128, "num_restarts": 20, "raw_samples": 512, "alpha": 0.0, "prune_baseline": true, "sequential": true, "fast_mode": false, "constraint": "none", "guardrail_mode": "monitor", "seed": 20261407, "dtype": "float64"}
- botorch: "0.16.1"
- bo_gp_sha: "60e6328236e745b3d34dc8cd704bb72888ae5d15"
- loo_rms_z: {"V1": 0.4268, "E1": 0.7727}
- noise_raw: {"V1": 14949.051609849952, "E1": 750721.1138779742}
- predictions: "waves/methods_E_EMU_house_s0_s4_r1/predictions.csv"
- graded_at: "2026-11-24T07:46:21+00:00"
- n_train: 56
- n_hv: 56
- cumulative_hv: 134359831075259.12
- gain: 34147904026727.656
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
- r2_max_mwh: 195.49448005452177
- calibration: {"V1": {"mean_z": 0.003, "rms_z": 0.174, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}, "E1": {"mean_z": -0.034, "rms_z": 0.11, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}}
- C2_review: false
- C3_review: false
- halt: null
- decision: "graded (record_only)"
- qnehvi_seconds: 4.1
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
    - [3.33276e+06, 8.0936e+09]
    - [1.44904e+06, 8.13706e+09]
    - [2.71171e+06, 8.10815e+09]
    - [2.0389e+06, 8.11823e+09]
    - [1.2517e+06, 8.15015e+09]
    - [1.71316e+06, 8.12619e+09]
    - [2.99472e+06, 8.10475e+09]
    - [2.43959e+06, 8.11487e+09]
<!-- END r1 -->

<!-- BEGIN r2 -->
## Round 2 (methods_E_EMU_house_s0_s4_r2)
- proposed_at: "2026-11-24T07:46:26+00:00"
- wave: "methods_E_EMU_house_s0_s4_r2"
- acq: "qnehvi"
- acq_seed: 20261408
- guardrail_mode: "monitor"
- settings: {"mc_samples": 128, "num_restarts": 20, "raw_samples": 512, "alpha": 0.0, "prune_baseline": true, "sequential": true, "fast_mode": false, "constraint": "none", "guardrail_mode": "monitor", "seed": 20261408, "dtype": "float64"}
- botorch: "0.16.1"
- bo_gp_sha: "60e6328236e745b3d34dc8cd704bb72888ae5d15"
- loo_rms_z: {"V1": 0.3699, "E1": 0.7301}
- noise_raw: {"V1": 14832.928227677354, "E1": 782218.7006817211}
- predictions: "waves/methods_E_EMU_house_s0_s4_r2/predictions.csv"
- graded_at: "2026-11-24T07:46:27+00:00"
- n_train: 64
- n_hv: 64
- cumulative_hv: 139442954410916.8
- gain: 5083123335657.672
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
- r2_max_mwh: 186.4591402417671
- calibration: {"V1": {"mean_z": 0.042, "rms_z": 0.128, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}, "E1": {"mean_z": 0.12, "rms_z": 0.19, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}}
- C2_review: false
- C3_review: false
- halt: null
- decision: "graded (record_only)"
- qnehvi_seconds: 4.4
- designs (MW per site ['110', '140', '146', '163', '270', '274']):
    - [149.410, 0.000, 0.000, 185.400, 579.000, 0.000]
    - [0.000, 0.000, 0.000, 175.637, 579.000, 0.000]
    - [0.000, 250.600, 73.804, 185.400, 579.000, 746.400]
    - [33.659, 250.600, 212.233, 185.400, 579.000, 746.400]
    - [175.204, 250.600, 217.528, 185.400, 579.000, 746.400]
    - [0.000, 250.600, 0.000, 185.400, 579.000, 0.000]
    - [0.000, 90.395, 0.000, 185.400, 579.000, 746.400]
    - [0.000, 0.000, 0.000, 0.000, 579.000, 746.400]
- realized Y (['V1', 'E1']):
    - [3.10296e+06, 8.09923e+09]
    - [3.46184e+06, 8.09169e+09]
    - [1.57592e+06, 8.13153e+09]
    - [1.35103e+06, 8.14382e+09]
    - [1.17046e+06, 8.15678e+09]
    - [2.97541e+06, 8.10385e+09]
    - [1.88391e+06, 8.12248e+09]
    - [2.32878e+06, 8.11701e+09]
<!-- END r2 -->

<!-- BEGIN r3 -->
## Round 3 (methods_E_EMU_house_s0_s4_r3)
- proposed_at: "2026-11-24T07:46:32+00:00"
- wave: "methods_E_EMU_house_s0_s4_r3"
- acq: "qnehvi"
- acq_seed: 20261409
- guardrail_mode: "monitor"
- settings: {"mc_samples": 128, "num_restarts": 20, "raw_samples": 512, "alpha": 0.0, "prune_baseline": true, "sequential": true, "fast_mode": false, "constraint": "none", "guardrail_mode": "monitor", "seed": 20261409, "dtype": "float64"}
- botorch: "0.16.1"
- bo_gp_sha: "60e6328236e745b3d34dc8cd704bb72888ae5d15"
- loo_rms_z: {"V1": 0.3359, "E1": 0.7122}
- noise_raw: {"V1": 15761.005962495006, "E1": 763046.5799541242}
- predictions: "waves/methods_E_EMU_house_s0_s4_r3/predictions.csv"
- graded_at: "2026-11-24T07:46:33+00:00"
- n_train: 72
- n_hv: 72
- cumulative_hv: 140473882771993.97
- gain: 1030928361077.1719
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
- r2_max_mwh: 174.52308757916006
- calibration: {"V1": {"mean_z": 0.099, "rms_z": 0.26, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}, "E1": {"mean_z": -0.021, "rms_z": 0.208, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}}
- C2_review: false
- C3_review: false
- halt: null
- decision: "graded (record_only)"
- qnehvi_seconds: 4.7
- designs (MW per site ['110', '140', '146', '163', '270', '274']):
    - [338.600, 0.000, 0.000, 185.400, 0.000, 746.400]
    - [0.000, 0.000, 0.000, 82.109, 579.000, 0.000]
    - [263.751, 0.000, 0.000, 185.400, 579.000, 0.000]
    - [0.000, 250.600, 0.000, 185.400, 0.000, 746.400]
    - [338.600, 0.000, 0.000, 185.400, 579.000, 746.400]
    - [0.000, 0.000, 0.000, 185.400, 470.019, 0.000]
    - [99.027, 0.000, 0.000, 185.400, 579.000, 0.000]
    - [0.000, 0.000, 0.000, 185.400, 378.415, 746.400]
- realized Y (['V1', 'E1']):
    - [2.4525e+06, 8.11607e+09]
    - [3.69123e+06, 8.09074e+09]
    - [2.86647e+06, 8.10558e+09]
    - [2.58125e+06, 8.11436e+09]
    - [1.63764e+06, 8.13161e+09]
    - [3.651e+06, 8.09072e+09]
    - [3.21722e+06, 8.09651e+09]
    - [2.27128e+06, 8.1173e+09]
<!-- END r3 -->

<!-- BEGIN r4 -->
## Round 4 (methods_E_EMU_house_s0_s4_r4)
- proposed_at: "2026-11-24T07:46:40+00:00"
- wave: "methods_E_EMU_house_s0_s4_r4"
- acq: "qnehvi"
- acq_seed: 20261410
- guardrail_mode: "monitor"
- settings: {"mc_samples": 128, "num_restarts": 20, "raw_samples": 512, "alpha": 0.0, "prune_baseline": true, "sequential": true, "fast_mode": false, "constraint": "none", "guardrail_mode": "monitor", "seed": 20261410, "dtype": "float64"}
- botorch: "0.16.1"
- bo_gp_sha: "60e6328236e745b3d34dc8cd704bb72888ae5d15"
- loo_rms_z: {"V1": 0.3259, "E1": 0.6789}
- noise_raw: {"V1": 15648.140441304635, "E1": 787320.977433018}
- predictions: "waves/methods_E_EMU_house_s0_s4_r4/predictions.csv"
- graded_at: "2026-11-24T07:46:40+00:00"
- n_train: 80
- n_hv: 80
- cumulative_hv: 141150939676226.62
- gain: 677056904232.6562
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
- r2_max_mwh: 173.40632202506313
- calibration: {"V1": {"mean_z": 0.036, "rms_z": 0.276, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}, "E1": {"mean_z": 0.295, "rms_z": 0.422, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}}
- C2_review: false
- C3_review: false
- halt: null
- decision: "graded (record_only)"
- qnehvi_seconds: 5.5
- designs (MW per site ['110', '140', '146', '163', '270', '274']):
    - [338.600, 0.000, 0.000, 0.000, 0.000, 746.400]
    - [0.000, 250.600, 115.488, 185.400, 579.000, 746.400]
    - [0.000, 0.000, 268.000, 185.400, 0.000, 746.400]
    - [338.600, 250.600, 35.119, 185.400, 579.000, 746.400]
    - [338.600, 0.000, 0.000, 185.400, 579.000, 43.497]
    - [338.600, 250.600, 168.715, 185.400, 579.000, 746.400]
    - [188.372, 0.000, 0.000, 185.400, 579.000, 0.000]
    - [338.600, 250.600, 0.000, 185.400, 579.000, 746.400]
- realized Y (['V1', 'E1']):
    - [2.76865e+06, 8.11009e+09]
    - [1.50619e+06, 8.1349e+09]
    - [2.58795e+06, 8.11655e+09]
    - [1.34162e+06, 8.14708e+09]
    - [2.61888e+06, 8.11185e+09]
    - [1.12929e+06, 8.16046e+09]
    - [3.01886e+06, 8.10231e+09]
    - [1.42714e+06, 8.144e+09]
<!-- END r4 -->
