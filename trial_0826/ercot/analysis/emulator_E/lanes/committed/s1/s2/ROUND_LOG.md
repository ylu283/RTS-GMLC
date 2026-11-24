# methods_E arm qnehvi seed_id 2 — ROUND_LOG (prompt 55; acq = qnehvi, base = ['n0_E'] nav prefix n0 = 48, objectives = ['V1', 'E1'])

Ledger: `lanes/committed/s1/s2/ledger.json`. stop_rule = record_only: gain_k and
would_stop_k = (gain_k < tau) AND (gain_{k-1} < tau) are graded and logged under tau_joint
(headline) and tau_marginal (recorded) with the joint-vs-marginal sensitivity column; the
rule never halts; every lane runs to hard_cap = 4. tau_joint = 0, tau_marginal = 0 — ZERO: the stop rule is budget-cap-only and the cap governs (plan 3).
E-D5 OPEN: see README.md for the two readings of a fire. Halts ONLY per plan 1.2/1.3
(HALT_FOR_DECISION.md). Acquisition jobs never submit; Kay submits via submit_ready_E.sh.
Stop NOW: `touch lanes/committed/s1/s2/STOP` on the CRC clone, then qdel the lane's JIDs.

<!-- BEGIN r1 -->
## Round 1 (methods_E_EMU_committed_s1_s2_r1)
- proposed_at: "2026-11-24T08:35:35+00:00"
- wave: "methods_E_EMU_committed_s1_s2_r1"
- acq: "qnehvi"
- acq_seed: 20261207
- guardrail_mode: "monitor"
- settings: {"mc_samples": 128, "num_restarts": 20, "raw_samples": 512, "alpha": 0.0, "prune_baseline": true, "sequential": true, "fast_mode": false, "constraint": "none", "guardrail_mode": "monitor", "seed": 20261207, "dtype": "float64", "bound_snaps": {"to_0": 1, "to_1": 0, "tol": 1e-12, "note": "bound cleanup after x * sx + mx; not lattice snapping"}}
- botorch: "0.16.1"
- bo_gp_sha: "60e6328236e745b3d34dc8cd704bb72888ae5d15"
- loo_rms_z: {"V1": 0.4268, "E1": 0.8267}
- noise_raw: {"V1": 14949.051609849952, "E1": 174965.13916944584}
- predictions: "waves/methods_E_EMU_committed_s1_s2_r1/predictions.csv"
- graded_at: "2026-11-24T08:35:36+00:00"
- n_train: 56
- n_hv: 55
- cumulative_hv: 136393048852072.31
- gain: 35869773451852.58
- gain_tau_joint: null
- would_stop_joint: false
- gain_tau_marginal: null
- would_stop_marginal: false
- joint_vs_marginal: {"ratio_joint_over_marginal": null, "agree": true, "fires": {"joint": false, "marginal": false}}
- first_fire_round: {"tau_joint": null, "tau_marginal": null}
- n_outside_ref: 0
- violations: ["methods_E_EMU_committed_s1_s2_r1:3"]
- suspects: []
- r2_flag: false
- r2_max_mwh: 172.46910641000113
- calibration: {"V1": {"mean_z": -0.043, "rms_z": 0.161, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}, "E1": {"mean_z": -0.001, "rms_z": 0.198, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}}
- C2_review: false
- C3_review: false
- halt: null
- decision: "graded (record_only)"
- fit_info: {"V1": {"fit_definition": "house"}, "E1": {"fit_definition": "v2", "converged": true, "mode_gap_nats": 53.68406410300448, "gap_second_nats": 2.884701544303425e-07, "n_within_tol": 13, "n_failed": 0, "map_total": -19.200766147217088, "noise_sd_raw": 174965.1391694458, "noise_over_sigma_c": 0.5600269029701294}}
- qnehvi_seconds: 6.3
- r1_shared_designs_with_seed: {"0": 3, "1": 4}
- designs (MW per site ['110', '140', '146', '163', '270', '274']):
    - [0.000, 0.000, 0.000, 185.400, 0.000, 746.400]
    - [0.000, 0.000, 0.000, 185.400, 579.000, 615.439]
    - [0.000, 0.000, 0.000, 185.400, 579.000, 0.000]
    - [0.000, 250.600, 161.577, 185.400, 579.000, 746.400]
    - [338.600, 0.000, 0.000, 185.400, 579.000, 0.000]
    - [0.000, 250.600, 0.000, 185.400, 579.000, 746.400]
    - [83.530, 250.600, 207.914, 185.400, 579.000, 746.400]
    - [0.000, 24.598, 0.000, 185.400, 579.000, 746.400]
- realized Y (['V1', 'E1']):
    - [2.99373e+06, 8.09793e+09]
    - [2.179e+06, 8.11404e+09]
    - [3.432e+06, 8.08532e+09]
    - [1.45302e+06, 8.13735e+09]
    - [2.71713e+06, 8.10469e+09]
    - [1.7109e+06, 8.12511e+09]
    - [1.27649e+06, 8.1502e+09]
    - [1.98494e+06, 8.11826e+09]
<!-- END r1 -->

<!-- BEGIN r2 -->
## Round 2 (methods_E_EMU_committed_s1_s2_r2)
- proposed_at: "2026-11-24T08:35:45+00:00"
- wave: "methods_E_EMU_committed_s1_s2_r2"
- acq: "qnehvi"
- acq_seed: 20261208
- guardrail_mode: "constrain"
- settings: {"mc_samples": 128, "num_restarts": 20, "raw_samples": 512, "alpha": 0.0, "prune_baseline": true, "sequential": true, "fast_mode": false, "constraint": "shed <= 1.0 MWh (GP on the accumulated R1 column)", "guardrail_mode": "constrain", "seed": 20261208, "dtype": "float64", "bound_snaps": {"to_0": 0, "to_1": 0, "tol": 1e-12, "note": "bound cleanup after x * sx + mx; not lattice snapping"}}
- botorch: "0.16.1"
- bo_gp_sha: "60e6328236e745b3d34dc8cd704bb72888ae5d15"
- loo_rms_z: {"V1": 0.3764, "E1": 0.7961}
- noise_raw: {"V1": 14970.94454415505, "E1": 169336.6697897805}
- predictions: "waves/methods_E_EMU_committed_s1_s2_r2/predictions.csv"
- graded_at: "2026-11-24T08:35:46+00:00"
- n_train: 64
- n_hv: 63
- cumulative_hv: 145474650119220.44
- gain: 9081601267148.125
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
- r2_max_mwh: 212.6623598516753
- calibration: {"V1": {"mean_z": 0.044, "rms_z": 0.164, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}, "E1": {"mean_z": -0.31, "rms_z": 1.004, "cov95": 7, "n_abs_z_gt3": 0, "transform": "std"}}
- C2_review: false
- C3_review: false
- halt: null
- decision: "graded (record_only)"
- fit_info: {"V1": {"fit_definition": "house"}, "E1": {"fit_definition": "v2", "converged": true, "mode_gap_nats": NaN, "gap_second_nats": 3.633915568457269e-08, "n_within_tol": 16, "n_failed": 0, "map_total": -6.274446540951299, "noise_sd_raw": 169336.66978978037, "noise_over_sigma_c": 0.5420113468992507}}
- qnehvi_seconds: 8.7
- designs (MW per site ['110', '140', '146', '163', '270', '274']):
    - [74.455, 0.000, 0.000, 185.400, 579.000, 0.000]
    - [46.534, 0.000, 0.000, 31.265, 579.000, 0.000]
    - [0.000, 250.600, 74.123, 185.400, 579.000, 746.400]
    - [166.915, 250.600, 189.427, 185.400, 579.000, 746.400]
    - [0.000, 250.600, 0.000, 185.400, 0.000, 746.400]
    - [0.000, 0.000, 0.000, 0.000, 0.000, 722.988]
    - [338.600, 68.436, 66.097, 185.400, 579.000, 746.400]
    - [29.147, 250.600, 199.133, 185.400, 579.000, 746.400]
- realized Y (['V1', 'E1']):
    - [3.26644e+06, 8.09028e+09]
    - [3.71726e+06, 8.08617e+09]
    - [1.57329e+06, 8.131e+09]
    - [1.1978e+06, 8.15771e+09]
    - [2.58644e+06, 8.1094e+09]
    - [3.41901e+06, 8.09094e+09]
    - [1.40245e+06, 8.14639e+09]
    - [1.37096e+06, 8.14269e+09]
<!-- END r2 -->

<!-- BEGIN r3 -->
## Round 3 (methods_E_EMU_committed_s1_s2_r3)
- proposed_at: "2026-11-24T08:35:55+00:00"
- wave: "methods_E_EMU_committed_s1_s2_r3"
- acq: "qnehvi"
- acq_seed: 20261209
- guardrail_mode: "constrain"
- settings: {"mc_samples": 128, "num_restarts": 20, "raw_samples": 512, "alpha": 0.0, "prune_baseline": true, "sequential": true, "fast_mode": false, "constraint": "shed <= 1.0 MWh (GP on the accumulated R1 column)", "guardrail_mode": "constrain", "seed": 20261209, "dtype": "float64", "bound_snaps": {"to_0": 4, "to_1": 0, "tol": 1e-12, "note": "bound cleanup after x * sx + mx; not lattice snapping"}}
- botorch: "0.16.1"
- bo_gp_sha: "60e6328236e745b3d34dc8cd704bb72888ae5d15"
- loo_rms_z: {"V1": 0.3276, "E1": 0.8439}
- noise_raw: {"V1": 15988.693346209271, "E1": 227099.53326548624}
- predictions: "waves/methods_E_EMU_committed_s1_s2_r3/predictions.csv"
- graded_at: "2026-11-24T08:35:56+00:00"
- n_train: 72
- n_hv: 71
- cumulative_hv: 146566598150819.25
- gain: 1091948031598.8125
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
- r2_max_mwh: 170.1225079676522
- calibration: {"V1": {"mean_z": -0.05, "rms_z": 0.13, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}, "E1": {"mean_z": 0.325, "rms_z": 1.431, "cov95": 7, "n_abs_z_gt3": 1, "transform": "std"}}
- C2_review: false
- C3_review: false
- halt: null
- decision: "graded (record_only)"
- fit_info: {"V1": {"fit_definition": "house"}, "E1": {"fit_definition": "v2", "converged": true, "mode_gap_nats": NaN, "gap_second_nats": 3.148948124476192e-08, "n_within_tol": 16, "n_failed": 0, "map_total": 11.339283218919846, "noise_sd_raw": 227099.53326548618, "noise_over_sigma_c": 0.7268982203218336}}
- qnehvi_seconds: 7.9
- designs (MW per site ['110', '140', '146', '163', '270', '274']):
    - [338.600, 0.000, 0.000, 185.400, 0.000, 746.400]
    - [46.002, 250.600, 0.000, 185.400, 579.000, 0.000]
    - [0.000, 250.600, 209.749, 185.400, 579.000, 746.400]
    - [0.000, 250.600, 0.000, 25.802, 579.000, 746.400]
    - [0.000, 95.130, 0.000, 185.400, 579.000, 746.400]
    - [110.411, 250.600, 218.866, 185.400, 579.000, 746.400]
    - [0.000, 250.600, 35.662, 185.400, 579.000, 746.400]
    - [338.600, 0.000, 0.000, 0.000, 0.000, 746.400]
- realized Y (['V1', 'E1']):
    - [2.4591e+06, 8.11365e+09]
    - [2.87553e+06, 8.10251e+09]
    - [1.41083e+06, 8.14013e+09]
    - [1.90199e+06, 8.12351e+09]
    - [1.87134e+06, 8.1222e+09]
    - [1.23079e+06, 8.15321e+09]
    - [1.63969e+06, 8.12905e+09]
    - [2.76877e+06, 8.1063e+09]
<!-- END r3 -->

<!-- BEGIN r4 -->
## Round 4 (methods_E_EMU_committed_s1_s2_r4)
- proposed_at: "2026-11-24T08:36:07+00:00"
- wave: "methods_E_EMU_committed_s1_s2_r4"
- acq: "qnehvi"
- acq_seed: 20261210
- guardrail_mode: "constrain"
- settings: {"mc_samples": 128, "num_restarts": 20, "raw_samples": 512, "alpha": 0.0, "prune_baseline": true, "sequential": true, "fast_mode": false, "constraint": "shed <= 1.0 MWh (GP on the accumulated R1 column)", "guardrail_mode": "constrain", "seed": 20261210, "dtype": "float64", "bound_snaps": {"to_0": 0, "to_1": 0, "tol": 1e-12, "note": "bound cleanup after x * sx + mx; not lattice snapping"}}
- botorch: "0.16.1"
- bo_gp_sha: "60e6328236e745b3d34dc8cd704bb72888ae5d15"
- loo_rms_z: {"V1": 0.3088, "E1": 0.8911}
- noise_raw: {"V1": 16158.236249956213, "E1": 340941.94335373264}
- predictions: "waves/methods_E_EMU_committed_s1_s2_r4/predictions.csv"
- graded_at: "2026-11-24T08:36:08+00:00"
- n_train: 80
- n_hv: 79
- cumulative_hv: 147580083730830.53
- gain: 1013485580011.2812
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
- r2_max_mwh: 179.71918994062077
- calibration: {"V1": {"mean_z": -0.013, "rms_z": 0.173, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}, "E1": {"mean_z": -0.208, "rms_z": 0.638, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}}
- C2_review: false
- C3_review: false
- halt: null
- decision: "graded (record_only)"
- fit_info: {"V1": {"fit_definition": "house"}, "E1": {"fit_definition": "v2", "converged": true, "mode_gap_nats": NaN, "gap_second_nats": 6.4379293007732485e-09, "n_within_tol": 16, "n_failed": 0, "map_total": 18.86503328804521, "noise_sd_raw": 340941.9433537326, "noise_over_sigma_c": 1.0912840211220283}}
- qnehvi_seconds: 10.7
- designs (MW per site ['110', '140', '146', '163', '270', '274']):
    - [338.600, 250.600, 30.030, 126.723, 579.000, 746.400]
    - [338.600, 187.912, 143.673, 179.312, 579.000, 717.405]
    - [166.694, 250.600, 234.327, 185.400, 579.000, 746.400]
    - [46.347, 250.600, 222.575, 185.400, 579.000, 746.400]
    - [25.782, 250.600, 0.000, 0.000, 579.000, 0.000]
    - [0.000, 197.121, 0.000, 185.400, 0.000, 746.400]
    - [134.283, 0.000, 0.000, 185.400, 579.000, 0.000]
    - [0.000, 250.600, 0.000, 185.400, 28.751, 746.400]
- realized Y (['V1', 'E1']):
    - [1.34483e+06, 8.15267e+09]
    - [1.16309e+06, 8.16147e+09]
    - [1.15975e+06, 8.16046e+09]
    - [1.32136e+06, 8.1461e+09]
    - [3.29265e+06, 8.09409e+09]
    - [2.65903e+06, 8.10803e+09]
    - [3.13696e+06, 8.09469e+09]
    - [2.52079e+06, 8.11081e+09]
<!-- END r4 -->
