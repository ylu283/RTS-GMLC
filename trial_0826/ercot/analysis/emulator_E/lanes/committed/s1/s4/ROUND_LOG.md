# methods_E arm qnehvi seed_id 4 — ROUND_LOG (prompt 55; acq = qnehvi, base = ['n0_E'] nav prefix n0 = 48, objectives = ['V1', 'E1'])

Ledger: `lanes/committed/s1/s4/ledger.json`. stop_rule = record_only: gain_k and
would_stop_k = (gain_k < tau) AND (gain_{k-1} < tau) are graded and logged under tau_joint
(headline) and tau_marginal (recorded) with the joint-vs-marginal sensitivity column; the
rule never halts; every lane runs to hard_cap = 4. tau_joint = 0, tau_marginal = 0 — ZERO: the stop rule is budget-cap-only and the cap governs (plan 3).
E-D5 OPEN: see README.md for the two readings of a fire. Halts ONLY per plan 1.2/1.3
(HALT_FOR_DECISION.md). Acquisition jobs never submit; Kay submits via submit_ready_E.sh.
Stop NOW: `touch lanes/committed/s1/s4/STOP` on the CRC clone, then qdel the lane's JIDs.

<!-- BEGIN r1 -->
## Round 1 (methods_E_EMU_committed_s1_s4_r1)
- proposed_at: "2026-11-24T08:36:56+00:00"
- wave: "methods_E_EMU_committed_s1_s4_r1"
- acq: "qnehvi"
- acq_seed: 20261407
- guardrail_mode: "monitor"
- settings: {"mc_samples": 128, "num_restarts": 20, "raw_samples": 512, "alpha": 0.0, "prune_baseline": true, "sequential": true, "fast_mode": false, "constraint": "none", "guardrail_mode": "monitor", "seed": 20261407, "dtype": "float64", "bound_snaps": {"to_0": 0, "to_1": 0, "tol": 1e-12, "note": "bound cleanup after x * sx + mx; not lattice snapping"}}
- botorch: "0.16.1"
- bo_gp_sha: "60e6328236e745b3d34dc8cd704bb72888ae5d15"
- loo_rms_z: {"V1": 0.4268, "E1": 0.8267}
- noise_raw: {"V1": 14949.051609849952, "E1": 174965.13916944584}
- predictions: "waves/methods_E_EMU_committed_s1_s4_r1/predictions.csv"
- graded_at: "2026-11-24T08:36:57+00:00"
- n_train: 56
- n_hv: 55
- cumulative_hv: 134675933304428.5
- gain: 34152657904208.766
- gain_tau_joint: null
- would_stop_joint: false
- gain_tau_marginal: null
- would_stop_marginal: false
- joint_vs_marginal: {"ratio_joint_over_marginal": null, "agree": true, "fires": {"joint": false, "marginal": false}}
- first_fire_round: {"tau_joint": null, "tau_marginal": null}
- n_outside_ref: 0
- violations: ["methods_E_EMU_committed_s1_s4_r1:3"]
- suspects: []
- r2_flag: false
- r2_max_mwh: 184.4956745445159
- calibration: {"V1": {"mean_z": -0.032, "rms_z": 0.161, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}, "E1": {"mean_z": 0.024, "rms_z": 0.213, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}}
- C2_review: false
- C3_review: false
- halt: null
- decision: "graded (record_only)"
- fit_info: {"V1": {"fit_definition": "house"}, "E1": {"fit_definition": "v2", "converged": true, "mode_gap_nats": 53.68406410300448, "gap_second_nats": 2.884701544303425e-07, "n_within_tol": 13, "n_failed": 0, "map_total": -19.200766147217088, "noise_sd_raw": 174965.1391694458, "noise_over_sigma_c": 0.5600269029701294}}
- qnehvi_seconds: 6.8
- r1_shared_designs_with_seed: {"0": 4, "1": 4, "2": 4, "3": 4}
- designs (MW per site ['110', '140', '146', '163', '270', '274']):
    - [0.000, 0.000, 0.000, 185.400, 0.000, 746.400]
    - [0.000, 0.000, 0.000, 185.400, 579.000, 614.486]
    - [0.000, 0.000, 0.000, 185.400, 579.000, 0.000]
    - [0.000, 250.600, 161.767, 185.400, 579.000, 746.400]
    - [338.600, 0.000, 0.000, 185.400, 579.000, 0.000]
    - [0.000, 250.600, 0.000, 185.400, 579.000, 746.400]
    - [82.524, 250.600, 209.595, 185.400, 579.000, 746.400]
    - [0.000, 250.600, 0.000, 185.400, 579.000, 0.000]
- realized Y (['V1', 'E1']):
    - [2.99585e+06, 8.09838e+09]
    - [2.1765e+06, 8.11467e+09]
    - [3.43935e+06, 8.08485e+09]
    - [1.45231e+06, 8.13665e+09]
    - [2.71285e+06, 8.10516e+09]
    - [1.71034e+06, 8.12501e+09]
    - [1.27557e+06, 8.14978e+09]
    - [2.97442e+06, 8.09862e+09]
<!-- END r1 -->

<!-- BEGIN r2 -->
## Round 2 (methods_E_EMU_committed_s1_s4_r2)
- proposed_at: "2026-11-24T08:37:05+00:00"
- wave: "methods_E_EMU_committed_s1_s4_r2"
- acq: "qnehvi"
- acq_seed: 20261408
- guardrail_mode: "constrain"
- settings: {"mc_samples": 128, "num_restarts": 20, "raw_samples": 512, "alpha": 0.0, "prune_baseline": true, "sequential": true, "fast_mode": false, "constraint": "shed <= 1.0 MWh (GP on the accumulated R1 column)", "guardrail_mode": "constrain", "seed": 20261408, "dtype": "float64", "bound_snaps": {"to_0": 0, "to_1": 0, "tol": 1e-12, "note": "bound cleanup after x * sx + mx; not lattice snapping"}}
- botorch: "0.16.1"
- bo_gp_sha: "60e6328236e745b3d34dc8cd704bb72888ae5d15"
- loo_rms_z: {"V1": 0.3677, "E1": 0.7856}
- noise_raw: {"V1": 14937.267388173072, "E1": 169791.7165069531}
- predictions: "waves/methods_E_EMU_committed_s1_s4_r2/predictions.csv"
- graded_at: "2026-11-24T08:37:06+00:00"
- n_train: 64
- n_hv: 63
- cumulative_hv: 143167934374553.84
- gain: 8492001070125.344
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
- r2_max_mwh: 169.30096456877112
- calibration: {"V1": {"mean_z": 0.045, "rms_z": 0.142, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}, "E1": {"mean_z": 0.196, "rms_z": 0.482, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}}
- C2_review: false
- C3_review: false
- halt: null
- decision: "graded (record_only)"
- fit_info: {"V1": {"fit_definition": "house"}, "E1": {"fit_definition": "v2", "converged": true, "mode_gap_nats": 72.17621948282044, "gap_second_nats": 9.007035117747364e-10, "n_within_tol": 15, "n_failed": 0, "map_total": -5.60414173909124, "noise_sd_raw": 169791.7165069531, "noise_over_sigma_c": 0.5434678564927312}}
- qnehvi_seconds: 7.3
- designs (MW per site ['110', '140', '146', '163', '270', '274']):
    - [0.000, 0.000, 0.000, 0.000, 0.000, 725.053]
    - [0.000, 23.368, 0.000, 185.400, 579.000, 746.400]
    - [0.000, 250.600, 0.000, 0.000, 579.000, 0.000]
    - [0.000, 250.600, 74.374, 185.400, 579.000, 746.400]
    - [0.000, 0.000, 0.000, 0.000, 579.000, 623.008]
    - [156.888, 250.600, 199.599, 185.400, 579.000, 746.400]
    - [27.797, 250.600, 205.194, 185.400, 579.000, 746.400]
    - [0.000, 0.000, 0.000, 185.400, 579.000, 471.642]
- realized Y (['V1', 'E1']):
    - [3.41181e+06, 8.091e+09]
    - [1.9971e+06, 8.11864e+09]
    - [3.35004e+06, 8.09256e+09]
    - [1.57243e+06, 8.13107e+09]
    - [2.51517e+06, 8.11182e+09]
    - [1.19266e+06, 8.15656e+09]
    - [1.36435e+06, 8.14288e+09]
    - [2.40534e+06, 8.11211e+09]
<!-- END r2 -->

<!-- BEGIN r3 -->
## Round 3 (methods_E_EMU_committed_s1_s4_r3)
- proposed_at: "2026-11-24T08:37:13+00:00"
- wave: "methods_E_EMU_committed_s1_s4_r3"
- acq: "qnehvi"
- acq_seed: 20261409
- guardrail_mode: "constrain"
- settings: {"mc_samples": 128, "num_restarts": 20, "raw_samples": 512, "alpha": 0.0, "prune_baseline": true, "sequential": true, "fast_mode": false, "constraint": "shed <= 1.0 MWh (GP on the accumulated R1 column)", "guardrail_mode": "constrain", "seed": 20261409, "dtype": "float64", "bound_snaps": {"to_0": 0, "to_1": 0, "tol": 1e-12, "note": "bound cleanup after x * sx + mx; not lattice snapping"}}
- botorch: "0.16.1"
- bo_gp_sha: "60e6328236e745b3d34dc8cd704bb72888ae5d15"
- loo_rms_z: {"V1": 0.3377, "E1": 0.8096}
- noise_raw: {"V1": 15508.201193656136, "E1": 152095.06982577223}
- predictions: "waves/methods_E_EMU_committed_s1_s4_r3/predictions.csv"
- graded_at: "2026-11-24T08:37:14+00:00"
- n_train: 72
- n_hv: 71
- cumulative_hv: 143735075699947.03
- gain: 567141325393.1875
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
- r2_max_mwh: 202.9264880536706
- calibration: {"V1": {"mean_z": 0.011, "rms_z": 0.17, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}, "E1": {"mean_z": 0.597, "rms_z": 1.142, "cov95": 7, "n_abs_z_gt3": 1, "transform": "std"}}
- C2_review: false
- C3_review: false
- halt: null
- decision: "graded (record_only)"
- fit_info: {"V1": {"fit_definition": "house"}, "E1": {"fit_definition": "v2", "converged": true, "mode_gap_nats": NaN, "gap_second_nats": 3.099174250564829e-08, "n_within_tol": 16, "n_failed": 0, "map_total": 11.459900251959432, "noise_sd_raw": 152095.06982577217, "noise_over_sigma_c": 0.4868245829762829}}
- qnehvi_seconds: 6.8
- designs (MW per site ['110', '140', '146', '163', '270', '274']):
    - [0.000, 250.600, 0.000, 185.400, 0.000, 746.400]
    - [0.000, 0.000, 268.000, 185.400, 0.000, 746.400]
    - [338.600, 250.600, 0.000, 185.400, 0.000, 0.000]
    - [206.543, 250.600, 195.972, 185.400, 579.000, 746.400]
    - [113.346, 250.600, 210.892, 185.400, 579.000, 746.400]
    - [338.600, 0.000, 0.000, 0.000, 579.000, 746.400]
    - [338.600, 0.000, 0.000, 0.000, 0.000, 746.400]
    - [338.600, 250.600, 0.000, 0.000, 0.842, 0.000]
- realized Y (['V1', 'E1']):
    - [2.57869e+06, 8.10932e+09]
    - [2.59087e+06, 8.11238e+09]
    - [3.57228e+06, 8.09734e+09]
    - [1.15481e+06, 8.16049e+09]
    - [1.2363e+06, 8.15378e+09]
    - [1.84426e+06, 8.12977e+09]
    - [2.77583e+06, 8.10551e+09]
    - [3.89268e+06, 8.09275e+09]
<!-- END r3 -->

<!-- BEGIN r4 -->
## Round 4 (methods_E_EMU_committed_s1_s4_r4)
- proposed_at: "2026-11-24T08:37:24+00:00"
- wave: "methods_E_EMU_committed_s1_s4_r4"
- acq: "qnehvi"
- acq_seed: 20261410
- guardrail_mode: "constrain"
- settings: {"mc_samples": 128, "num_restarts": 20, "raw_samples": 512, "alpha": 0.0, "prune_baseline": true, "sequential": true, "fast_mode": false, "constraint": "shed <= 1.0 MWh (GP on the accumulated R1 column)", "guardrail_mode": "constrain", "seed": 20261410, "dtype": "float64", "bound_snaps": {"to_0": 0, "to_1": 0, "tol": 1e-12, "note": "bound cleanup after x * sx + mx; not lattice snapping"}}
- botorch: "0.16.1"
- bo_gp_sha: "60e6328236e745b3d34dc8cd704bb72888ae5d15"
- loo_rms_z: {"V1": 0.3059, "E1": 0.8275}
- noise_raw: {"V1": 15965.018684442923, "E1": 235689.79532716656}
- predictions: "waves/methods_E_EMU_committed_s1_s4_r4/predictions.csv"
- graded_at: "2026-11-24T08:37:24+00:00"
- n_train: 80
- n_hv: 79
- cumulative_hv: 145117787578816.22
- gain: 1382711878869.1875
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
- r2_max_mwh: 181.35604561877773
- calibration: {"V1": {"mean_z": 0.036, "rms_z": 0.27, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}, "E1": {"mean_z": -0.165, "rms_z": 0.73, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}}
- C2_review: false
- C3_review: false
- halt: null
- decision: "graded (record_only)"
- fit_info: {"V1": {"fit_definition": "house"}, "E1": {"fit_definition": "v2", "converged": true, "mode_gap_nats": NaN, "gap_second_nats": 9.575160220265388e-09, "n_within_tol": 16, "n_failed": 0, "map_total": 21.228769850509572, "noise_sd_raw": 235689.7953271667, "noise_over_sigma_c": 0.7543938567722794}}
- qnehvi_seconds: 9.0
- designs (MW per site ['110', '140', '146', '163', '270', '274']):
    - [0.000, 250.600, 35.752, 185.400, 579.000, 746.400]
    - [338.600, 0.000, 14.823, 185.400, 579.000, 746.400]
    - [0.000, 250.600, 0.000, 29.527, 579.000, 746.400]
    - [0.000, 250.600, 0.000, 69.553, 579.000, 746.400]
    - [265.021, 0.000, 0.000, 185.400, 579.000, 0.000]
    - [0.000, 250.600, 0.000, 0.000, 0.000, 746.400]
    - [0.000, 0.000, 0.000, 185.400, 579.000, 421.381]
    - [0.000, 0.000, 134.925, 185.400, 579.000, 0.000]
- realized Y (['V1', 'E1']):
    - [1.6406e+06, 8.1282e+09]
    - [1.60937e+06, 8.13485e+09]
    - [1.89965e+06, 8.12322e+09]
    - [1.8184e+06, 8.12546e+09]
    - [2.85574e+06, 8.10226e+09]
    - [2.89934e+06, 8.10317e+09]
    - [2.49427e+06, 8.1101e+09]
    - [3.19457e+06, 8.09509e+09]
<!-- END r4 -->
