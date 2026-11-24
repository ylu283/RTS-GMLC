# methods_E arm qnehvi seed_id 3 — ROUND_LOG (prompt 55; acq = qnehvi, base = ['n0_E'] nav prefix n0 = 48, objectives = ['V1', 'E1'])

Ledger: `lanes/committed/s1/s3/ledger.json`. stop_rule = record_only: gain_k and
would_stop_k = (gain_k < tau) AND (gain_{k-1} < tau) are graded and logged under tau_joint
(headline) and tau_marginal (recorded) with the joint-vs-marginal sensitivity column; the
rule never halts; every lane runs to hard_cap = 4. tau_joint = 0, tau_marginal = 0 — ZERO: the stop rule is budget-cap-only and the cap governs (plan 3).
E-D5 OPEN: see README.md for the two readings of a fire. Halts ONLY per plan 1.2/1.3
(HALT_FOR_DECISION.md). Acquisition jobs never submit; Kay submits via submit_ready_E.sh.
Stop NOW: `touch lanes/committed/s1/s3/STOP` on the CRC clone, then qdel the lane's JIDs.

<!-- BEGIN r1 -->
## Round 1 (methods_E_EMU_committed_s1_s3_r1)
- proposed_at: "2026-11-24T08:36:16+00:00"
- wave: "methods_E_EMU_committed_s1_s3_r1"
- acq: "qnehvi"
- acq_seed: 20261307
- guardrail_mode: "monitor"
- settings: {"mc_samples": 128, "num_restarts": 20, "raw_samples": 512, "alpha": 0.0, "prune_baseline": true, "sequential": true, "fast_mode": false, "constraint": "none", "guardrail_mode": "monitor", "seed": 20261307, "dtype": "float64", "bound_snaps": {"to_0": 0, "to_1": 0, "tol": 1e-12, "note": "bound cleanup after x * sx + mx; not lattice snapping"}}
- botorch: "0.16.1"
- bo_gp_sha: "60e6328236e745b3d34dc8cd704bb72888ae5d15"
- loo_rms_z: {"V1": 0.4268, "E1": 0.8267}
- noise_raw: {"V1": 14949.051609849952, "E1": 174965.13916944584}
- predictions: "waves/methods_E_EMU_committed_s1_s3_r1/predictions.csv"
- graded_at: "2026-11-24T08:36:17+00:00"
- n_train: 56
- n_hv: 55
- cumulative_hv: 135667627327373.94
- gain: 35144351927154.203
- gain_tau_joint: null
- would_stop_joint: false
- gain_tau_marginal: null
- would_stop_marginal: false
- joint_vs_marginal: {"ratio_joint_over_marginal": null, "agree": true, "fires": {"joint": false, "marginal": false}}
- first_fire_round: {"tau_joint": null, "tau_marginal": null}
- n_outside_ref: 0
- violations: ["methods_E_EMU_committed_s1_s3_r1:3"]
- suspects: []
- r2_flag: false
- r2_max_mwh: 179.42857303569212
- calibration: {"V1": {"mean_z": -0.005, "rms_z": 0.201, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}, "E1": {"mean_z": 0.055, "rms_z": 0.291, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}}
- C2_review: false
- C3_review: false
- halt: null
- decision: "graded (record_only)"
- fit_info: {"V1": {"fit_definition": "house"}, "E1": {"fit_definition": "v2", "converged": true, "mode_gap_nats": 53.68406410300448, "gap_second_nats": 2.884701544303425e-07, "n_within_tol": 13, "n_failed": 0, "map_total": -19.200766147217088, "noise_sd_raw": 174965.1391694458, "noise_over_sigma_c": 0.5600269029701294}}
- qnehvi_seconds: 6.5
- r1_shared_designs_with_seed: {"0": 3, "1": 4, "2": 4}
- designs (MW per site ['110', '140', '146', '163', '270', '274']):
    - [0.000, 0.000, 0.000, 185.400, 0.000, 746.400]
    - [0.000, 0.000, 0.000, 185.400, 579.000, 613.472]
    - [0.000, 0.000, 0.000, 185.400, 579.000, 0.000]
    - [0.000, 250.600, 163.694, 185.400, 579.000, 746.400]
    - [338.600, 0.000, 0.000, 185.400, 579.000, 0.000]
    - [0.000, 250.600, 0.000, 185.400, 579.000, 746.400]
    - [85.024, 250.600, 207.040, 185.400, 579.000, 746.400]
    - [0.000, 17.346, 0.000, 185.400, 579.000, 746.400]
- realized Y (['V1', 'E1']):
    - [2.99896e+06, 8.09806e+09]
    - [2.18745e+06, 8.11512e+09]
    - [3.43805e+06, 8.08578e+09]
    - [1.44851e+06, 8.13689e+09]
    - [2.72362e+06, 8.10595e+09]
    - [1.70964e+06, 8.12493e+09]
    - [1.27235e+06, 8.14932e+09]
    - [2.00013e+06, 8.11769e+09]
<!-- END r1 -->

<!-- BEGIN r2 -->
## Round 2 (methods_E_EMU_committed_s1_s3_r2)
- proposed_at: "2026-11-24T08:36:26+00:00"
- wave: "methods_E_EMU_committed_s1_s3_r2"
- acq: "qnehvi"
- acq_seed: 20261308
- guardrail_mode: "constrain"
- settings: {"mc_samples": 128, "num_restarts": 20, "raw_samples": 512, "alpha": 0.0, "prune_baseline": true, "sequential": true, "fast_mode": false, "constraint": "shed <= 1.0 MWh (GP on the accumulated R1 column)", "guardrail_mode": "constrain", "seed": 20261308, "dtype": "float64", "bound_snaps": {"to_0": 0, "to_1": 0, "tol": 1e-12, "note": "bound cleanup after x * sx + mx; not lattice snapping"}}
- botorch: "0.16.1"
- bo_gp_sha: "60e6328236e745b3d34dc8cd704bb72888ae5d15"
- loo_rms_z: {"V1": 0.3823, "E1": 0.8047}
- noise_raw: {"V1": 14994.71692233187, "E1": 169956.34592185513}
- predictions: "waves/methods_E_EMU_committed_s1_s3_r2/predictions.csv"
- graded_at: "2026-11-24T08:36:27+00:00"
- n_train: 64
- n_hv: 63
- cumulative_hv: 145091648593682.16
- gain: 9424021266308.219
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
- r2_max_mwh: 171.04159683009783
- calibration: {"V1": {"mean_z": -0.055, "rms_z": 0.186, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}, "E1": {"mean_z": 0.489, "rms_z": 1.036, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}}
- C2_review: false
- C3_review: false
- halt: null
- decision: "graded (record_only)"
- fit_info: {"V1": {"fit_definition": "house"}, "E1": {"fit_definition": "v2", "converged": true, "mode_gap_nats": NaN, "gap_second_nats": 3.401427051130668e-08, "n_within_tol": 16, "n_failed": 0, "map_total": -6.912374630144079, "noise_sd_raw": 169956.3459218552, "noise_over_sigma_c": 0.5439948008989316}}
- qnehvi_seconds: 8.7
- designs (MW per site ['110', '140', '146', '163', '270', '274']):
    - [73.300, 0.000, 0.000, 185.400, 579.000, 0.000]
    - [46.266, 0.000, 0.000, 35.595, 579.000, 0.000]
    - [0.000, 250.600, 74.823, 185.400, 579.000, 746.400]
    - [0.000, 0.000, 0.000, 185.400, 579.000, 436.170]
    - [167.340, 250.600, 196.738, 185.400, 579.000, 746.400]
    - [33.830, 250.600, 195.947, 185.400, 579.000, 746.400]
    - [0.000, 0.000, 0.000, 185.400, 56.199, 746.400]
    - [0.000, 0.000, 0.000, 0.000, 0.000, 746.400]
- realized Y (['V1', 'E1']):
    - [3.2776e+06, 8.09075e+09]
    - [3.70983e+06, 8.08722e+09]
    - [1.56321e+06, 8.13112e+09]
    - [2.46842e+06, 8.11105e+09]
    - [1.18394e+06, 8.15797e+09]
    - [1.35996e+06, 8.1434e+09]
    - [2.87663e+06, 8.10227e+09]
    - [3.37223e+06, 8.0919e+09]
<!-- END r2 -->

<!-- BEGIN r3 -->
## Round 3 (methods_E_EMU_committed_s1_s3_r3)
- proposed_at: "2026-11-24T08:36:36+00:00"
- wave: "methods_E_EMU_committed_s1_s3_r3"
- acq: "qnehvi"
- acq_seed: 20261309
- guardrail_mode: "constrain"
- settings: {"mc_samples": 128, "num_restarts": 20, "raw_samples": 512, "alpha": 0.0, "prune_baseline": true, "sequential": true, "fast_mode": false, "constraint": "shed <= 1.0 MWh (GP on the accumulated R1 column)", "guardrail_mode": "constrain", "seed": 20261309, "dtype": "float64", "bound_snaps": {"to_0": 0, "to_1": 0, "tol": 1e-12, "note": "bound cleanup after x * sx + mx; not lattice snapping"}}
- botorch: "0.16.1"
- bo_gp_sha: "60e6328236e745b3d34dc8cd704bb72888ae5d15"
- loo_rms_z: {"V1": 0.3458, "E1": 0.9272}
- noise_raw: {"V1": 15922.16986237063, "E1": 269107.0686401754}
- predictions: "waves/methods_E_EMU_committed_s1_s3_r3/predictions.csv"
- graded_at: "2026-11-24T08:36:36+00:00"
- n_train: 72
- n_hv: 71
- cumulative_hv: 146452398234737.97
- gain: 1360749641055.8125
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
- r2_max_mwh: 169.75801624489216
- calibration: {"V1": {"mean_z": 0.056, "rms_z": 0.234, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}, "E1": {"mean_z": -0.12, "rms_z": 0.641, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}}
- C2_review: false
- C3_review: false
- halt: null
- decision: "graded (record_only)"
- fit_info: {"V1": {"fit_definition": "house"}, "E1": {"fit_definition": "v2", "converged": true, "mode_gap_nats": 91.72524591216612, "gap_second_nats": 4.250722085430425e-08, "n_within_tol": 15, "n_failed": 0, "map_total": 12.13931546885842, "noise_sd_raw": 269107.0686401754, "noise_over_sigma_c": 0.8613555759354687}}
- qnehvi_seconds: 7.7
- designs (MW per site ['110', '140', '146', '163', '270', '274']):
    - [116.741, 250.600, 214.475, 185.400, 579.000, 746.400]
    - [0.000, 250.600, 0.000, 19.769, 579.000, 746.400]
    - [0.000, 250.600, 0.000, 185.400, 0.000, 746.400]
    - [180.588, 250.600, 220.445, 181.455, 579.000, 746.400]
    - [0.000, 95.935, 0.000, 185.400, 579.000, 746.400]
    - [127.949, 0.000, 0.000, 185.400, 579.000, 0.000]
    - [338.600, 250.600, 0.000, 185.400, 579.000, 746.400]
    - [22.559, 250.600, 0.000, 95.368, 579.000, 0.000]
- realized Y (['V1', 'E1']):
    - [1.22771e+06, 8.15407e+09]
    - [1.91352e+06, 8.12263e+09]
    - [2.5887e+06, 8.10927e+09]
    - [1.15461e+06, 8.16004e+09]
    - [1.8672e+06, 8.12207e+09]
    - [3.15602e+06, 8.0943e+09]
    - [1.41955e+06, 8.14937e+09]
    - [3.08802e+06, 8.09862e+09]
<!-- END r3 -->

<!-- BEGIN r4 -->
## Round 4 (methods_E_EMU_committed_s1_s3_r4)
- proposed_at: "2026-11-24T08:36:47+00:00"
- wave: "methods_E_EMU_committed_s1_s3_r4"
- acq: "qnehvi"
- acq_seed: 20261310
- guardrail_mode: "constrain"
- settings: {"mc_samples": 128, "num_restarts": 20, "raw_samples": 512, "alpha": 0.0, "prune_baseline": true, "sequential": true, "fast_mode": false, "constraint": "shed <= 1.0 MWh (GP on the accumulated R1 column)", "guardrail_mode": "constrain", "seed": 20261310, "dtype": "float64", "bound_snaps": {"to_0": 0, "to_1": 0, "tol": 1e-12, "note": "bound cleanup after x * sx + mx; not lattice snapping"}}
- botorch: "0.16.1"
- bo_gp_sha: "60e6328236e745b3d34dc8cd704bb72888ae5d15"
- loo_rms_z: {"V1": 0.3221, "E1": 0.8923}
- noise_raw: {"V1": 16238.613213446593, "E1": 288469.8784732396}
- predictions: "waves/methods_E_EMU_committed_s1_s3_r4/predictions.csv"
- graded_at: "2026-11-24T08:36:48+00:00"
- n_train: 80
- n_hv: 79
- cumulative_hv: 148141091663286.56
- gain: 1688693428548.5938
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
- r2_max_mwh: 175.46736855026214
- calibration: {"V1": {"mean_z": -0.097, "rms_z": 0.234, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}, "E1": {"mean_z": 0.168, "rms_z": 0.989, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}}
- C2_review: false
- C3_review: false
- halt: null
- decision: "graded (record_only)"
- fit_info: {"V1": {"fit_definition": "house"}, "E1": {"fit_definition": "v2", "converged": true, "mode_gap_nats": NaN, "gap_second_nats": 1.2604324695075775e-08, "n_within_tol": 16, "n_failed": 0, "map_total": 26.662942368576097, "noise_sd_raw": 288469.8784732396, "noise_over_sigma_c": 0.923331890046298}}
- qnehvi_seconds: 9.6
- designs (MW per site ['110', '140', '146', '163', '270', '274']):
    - [0.000, 250.600, 215.256, 185.400, 579.000, 746.400]
    - [0.000, 0.000, 0.000, 108.578, 579.000, 0.000]
    - [338.600, 250.600, 147.324, 101.637, 579.000, 746.400]
    - [0.000, 250.600, 115.886, 185.400, 579.000, 746.400]
    - [0.000, 250.600, 0.000, 0.000, 0.000, 746.400]
    - [338.600, 0.000, 0.000, 185.400, 579.000, 746.400]
    - [338.600, 0.000, 197.160, 185.400, 579.000, 746.400]
    - [189.911, 250.600, 236.500, 181.851, 579.000, 746.400]
- realized Y (['V1', 'E1']):
    - [1.40119e+06, 8.14023e+09]
    - [3.62236e+06, 8.0842e+09]
    - [1.15518e+06, 8.16277e+09]
    - [1.50748e+06, 8.1346e+09]
    - [2.89951e+06, 8.10314e+09]
    - [1.6407e+06, 8.13376e+09]
    - [1.34304e+06, 8.15082e+09]
    - [1.13676e+06, 8.16221e+09]
<!-- END r4 -->
