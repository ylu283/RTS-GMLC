# methods_E arm qnehvi seed_id 2 — ROUND_LOG (prompt 55; acq = qnehvi, base = ['n0_E'] nav prefix n0 = 48, objectives = ['V1', 'E1'])

Ledger: `lanes/house/s0/s2/ledger.json`. stop_rule = record_only: gain_k and
would_stop_k = (gain_k < tau) AND (gain_{k-1} < tau) are graded and logged under tau_joint
(headline) and tau_marginal (recorded) with the joint-vs-marginal sensitivity column; the
rule never halts; every lane runs to hard_cap = 4. tau_joint = 0, tau_marginal = 0 — ZERO: the stop rule is budget-cap-only and the cap governs (plan 3).
E-D5 OPEN: see README.md for the two readings of a fire. Halts ONLY per plan 1.2/1.3
(HALT_FOR_DECISION.md). Acquisition jobs never submit; Kay submits via submit_ready_E.sh.
Stop NOW: `touch lanes/house/s0/s2/STOP` on the CRC clone, then qdel the lane's JIDs.

<!-- BEGIN r1 -->
## Round 1 (methods_E_EMU_house_s0_s2_r1)
- proposed_at: "2026-11-24T07:45:29+00:00"
- wave: "methods_E_EMU_house_s0_s2_r1"
- acq: "qnehvi"
- acq_seed: 20261207
- guardrail_mode: "monitor"
- settings: {"mc_samples": 128, "num_restarts": 20, "raw_samples": 512, "alpha": 0.0, "prune_baseline": true, "sequential": true, "fast_mode": false, "constraint": "none", "guardrail_mode": "monitor", "seed": 20261207, "dtype": "float64"}
- botorch: "0.16.1"
- bo_gp_sha: "60e6328236e745b3d34dc8cd704bb72888ae5d15"
- loo_rms_z: {"V1": 0.4268, "E1": 0.7727}
- noise_raw: {"V1": 14949.051609849952, "E1": 750721.1138779742}
- predictions: "waves/methods_E_EMU_house_s0_s2_r1/predictions.csv"
- graded_at: "2026-11-24T07:45:30+00:00"
- n_train: 56
- n_hv: 56
- cumulative_hv: 133346707244674.03
- gain: 33134780196142.562
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
- r2_max_mwh: 188.22465971122725
- calibration: {"V1": {"mean_z": -0.01, "rms_z": 0.159, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}, "E1": {"mean_z": -0.033, "rms_z": 0.118, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}}
- C2_review: false
- C3_review: false
- halt: null
- decision: "graded (record_only)"
- qnehvi_seconds: 4.2
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
    - [3.33685e+06, 8.09423e+09]
    - [1.44942e+06, 8.1374e+09]
    - [2.71926e+06, 8.10867e+09]
    - [2.037e+06, 8.1181e+09]
    - [1.71558e+06, 8.12562e+09]
    - [1.24985e+06, 8.15002e+09]
    - [3.00419e+06, 8.10522e+09]
    - [2.97681e+06, 8.10396e+09]
<!-- END r1 -->

<!-- BEGIN r2 -->
## Round 2 (methods_E_EMU_house_s0_s2_r2)
- proposed_at: "2026-11-24T07:45:35+00:00"
- wave: "methods_E_EMU_house_s0_s2_r2"
- acq: "qnehvi"
- acq_seed: 20261208
- guardrail_mode: "monitor"
- settings: {"mc_samples": 128, "num_restarts": 20, "raw_samples": 512, "alpha": 0.0, "prune_baseline": true, "sequential": true, "fast_mode": false, "constraint": "none", "guardrail_mode": "monitor", "seed": 20261208, "dtype": "float64"}
- botorch: "0.16.1"
- bo_gp_sha: "60e6328236e745b3d34dc8cd704bb72888ae5d15"
- loo_rms_z: {"V1": 0.3689, "E1": 0.7297}
- noise_raw: {"V1": 14959.191137099295, "E1": 794596.4930475922}
- predictions: "waves/methods_E_EMU_house_s0_s2_r2/predictions.csv"
- graded_at: "2026-11-24T07:45:36+00:00"
- n_train: 64
- n_hv: 64
- cumulative_hv: 138693080902387.89
- gain: 5346373657713.859
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
- r2_max_mwh: 193.98792337606304
- calibration: {"V1": {"mean_z": 0.056, "rms_z": 0.185, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}, "E1": {"mean_z": 0.091, "rms_z": 0.223, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}}
- C2_review: false
- C3_review: false
- halt: null
- decision: "graded (record_only)"
- qnehvi_seconds: 4.3
- designs (MW per site ['110', '140', '146', '163', '270', '274']):
    - [0.000, 0.000, 0.000, 159.156, 579.000, 0.000]
    - [135.025, 0.000, 0.000, 185.400, 579.000, 0.000]
    - [0.000, 0.000, 0.000, 185.400, 579.000, 462.130]
    - [338.600, 0.000, 0.000, 185.400, 579.000, 746.400]
    - [39.722, 250.600, 199.459, 185.400, 579.000, 746.400]
    - [188.618, 250.600, 205.743, 185.400, 579.000, 746.400]
    - [0.000, 250.600, 79.659, 185.400, 579.000, 746.400]
    - [0.000, 0.000, 0.000, 0.000, 579.000, 746.400]
- realized Y (['V1', 'E1']):
    - [3.49536e+06, 8.09216e+09]
    - [3.14248e+06, 8.09943e+09]
    - [2.41579e+06, 8.11371e+09]
    - [1.64047e+06, 8.13188e+09]
    - [1.35125e+06, 8.14399e+09]
    - [1.15663e+06, 8.15673e+09]
    - [1.56382e+06, 8.13187e+09]
    - [2.33921e+06, 8.11742e+09]
<!-- END r2 -->

<!-- BEGIN r3 -->
## Round 3 (methods_E_EMU_house_s0_s2_r3)
- proposed_at: "2026-11-24T07:45:41+00:00"
- wave: "methods_E_EMU_house_s0_s2_r3"
- acq: "qnehvi"
- acq_seed: 20261209
- guardrail_mode: "monitor"
- settings: {"mc_samples": 128, "num_restarts": 20, "raw_samples": 512, "alpha": 0.0, "prune_baseline": true, "sequential": true, "fast_mode": false, "constraint": "none", "guardrail_mode": "monitor", "seed": 20261209, "dtype": "float64"}
- botorch: "0.16.1"
- bo_gp_sha: "60e6328236e745b3d34dc8cd704bb72888ae5d15"
- loo_rms_z: {"V1": 0.3437, "E1": 0.7207}
- noise_raw: {"V1": 15772.706496176606, "E1": 781184.4533058059}
- predictions: "waves/methods_E_EMU_house_s0_s2_r3/predictions.csv"
- graded_at: "2026-11-24T07:45:42+00:00"
- n_train: 72
- n_hv: 72
- cumulative_hv: 140240211290045.88
- gain: 1547130387657.9844
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
- r2_max_mwh: 177.00596574759172
- calibration: {"V1": {"mean_z": 0.03, "rms_z": 0.308, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}, "E1": {"mean_z": 0.273, "rms_z": 0.414, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}}
- C2_review: false
- C3_review: false
- halt: null
- decision: "graded (record_only)"
- qnehvi_seconds: 4.7
- designs (MW per site ['110', '140', '146', '163', '270', '274']):
    - [338.600, 0.000, 0.000, 0.000, 0.000, 746.400]
    - [0.000, 85.079, 0.000, 185.400, 579.000, 746.400]
    - [0.000, 0.000, 0.000, 185.400, 461.161, 0.000]
    - [0.000, 0.000, 0.000, 185.400, 579.000, 377.398]
    - [338.600, 250.600, 0.000, 185.400, 579.000, 746.400]
    - [0.000, 0.000, 0.000, 185.400, 579.000, 579.096]
    - [0.000, 0.000, 0.000, 185.400, 579.000, 239.307]
    - [0.000, 250.600, 37.364, 185.400, 579.000, 746.400]
- realized Y (['V1', 'E1']):
    - [2.76894e+06, 8.11017e+09]
    - [1.89305e+06, 8.12203e+09]
    - [3.67189e+06, 8.09176e+09]
    - [2.58403e+06, 8.11243e+09]
    - [1.42037e+06, 8.14341e+09]
    - [2.23256e+06, 8.11654e+09]
    - [2.87656e+06, 8.10595e+09]
    - [1.63058e+06, 8.12935e+09]
<!-- END r3 -->

<!-- BEGIN r4 -->
## Round 4 (methods_E_EMU_house_s0_s2_r4)
- proposed_at: "2026-11-24T07:45:48+00:00"
- wave: "methods_E_EMU_house_s0_s2_r4"
- acq: "qnehvi"
- acq_seed: 20261210
- guardrail_mode: "monitor"
- settings: {"mc_samples": 128, "num_restarts": 20, "raw_samples": 512, "alpha": 0.0, "prune_baseline": true, "sequential": true, "fast_mode": false, "constraint": "none", "guardrail_mode": "monitor", "seed": 20261210, "dtype": "float64"}
- botorch: "0.16.1"
- bo_gp_sha: "60e6328236e745b3d34dc8cd704bb72888ae5d15"
- loo_rms_z: {"V1": 0.3412, "E1": 0.7352}
- noise_raw: {"V1": 15549.756929468394, "E1": 771036.0785508457}
- predictions: "waves/methods_E_EMU_house_s0_s2_r4/predictions.csv"
- graded_at: "2026-11-24T07:45:49+00:00"
- n_train: 80
- n_hv: 80
- cumulative_hv: 141455502079209.0
- gain: 1215290789163.125
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
- r2_max_mwh: 170.5738297809268
- calibration: {"V1": {"mean_z": 0.057, "rms_z": 0.231, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}, "E1": {"mean_z": -0.201, "rms_z": 0.36, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}}
- C2_review: false
- C3_review: false
- halt: null
- decision: "graded (record_only)"
- qnehvi_seconds: 5.3
- designs (MW per site ['110', '140', '146', '163', '270', '274']):
    - [177.609, 0.000, 0.000, 185.400, 579.000, 0.000]
    - [90.824, 0.000, 0.000, 185.400, 579.000, 0.000]
    - [0.000, 0.000, 0.000, 60.776, 579.000, 0.000]
    - [76.001, 250.600, 193.157, 185.400, 579.000, 746.400]
    - [141.750, 250.600, 206.582, 185.400, 579.000, 746.400]
    - [0.000, 250.600, 118.311, 185.400, 579.000, 746.400]
    - [0.000, 250.600, 0.000, 185.400, 0.000, 746.400]
    - [338.600, 0.000, 0.000, 185.400, 0.000, 746.400]
- realized Y (['V1', 'E1']):
    - [3.04423e+06, 8.10182e+09]
    - [3.23831e+06, 8.09603e+09]
    - [3.74707e+06, 8.09081e+09]
    - [1.30351e+06, 8.14671e+09]
    - [1.20303e+06, 8.15344e+09]
    - [1.51234e+06, 8.13472e+09]
    - [2.57908e+06, 8.11328e+09]
    - [2.45849e+06, 8.11609e+09]
<!-- END r4 -->
