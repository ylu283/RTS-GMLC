# methods_E arm qnehvi seed_id 2 — ROUND_LOG (prompt 55; acq = qnehvi, base = ['n0_E'] nav prefix n0 = 48, objectives = ['V1', 'E1'])

Ledger: `lanes/committed/s0/s2/ledger.json`. stop_rule = record_only: gain_k and
would_stop_k = (gain_k < tau) AND (gain_{k-1} < tau) are graded and logged under tau_joint
(headline) and tau_marginal (recorded) with the joint-vs-marginal sensitivity column; the
rule never halts; every lane runs to hard_cap = 4. tau_joint = 0, tau_marginal = 0 — ZERO: the stop rule is budget-cap-only and the cap governs (plan 3).
E-D5 OPEN: see README.md for the two readings of a fire. Halts ONLY per plan 1.2/1.3
(HALT_FOR_DECISION.md). Acquisition jobs never submit; Kay submits via submit_ready_E.sh.
Stop NOW: `touch lanes/committed/s0/s2/STOP` on the CRC clone, then qdel the lane's JIDs.

<!-- BEGIN r1 -->
## Round 1 (methods_E_EMU_committed_s0_s2_r1)
- proposed_at: "2026-11-24T08:35:23+00:00"
- wave: "methods_E_EMU_committed_s0_s2_r1"
- acq: "qnehvi"
- acq_seed: 20261207
- guardrail_mode: "monitor"
- settings: {"mc_samples": 128, "num_restarts": 20, "raw_samples": 512, "alpha": 0.0, "prune_baseline": true, "sequential": true, "fast_mode": false, "constraint": "none", "guardrail_mode": "monitor", "seed": 20261207, "dtype": "float64", "bound_snaps": {"to_0": 1, "to_1": 0, "tol": 1e-12, "note": "bound cleanup after x * sx + mx; not lattice snapping"}}
- botorch: "0.16.1"
- bo_gp_sha: "60e6328236e745b3d34dc8cd704bb72888ae5d15"
- loo_rms_z: {"V1": 0.4268, "E1": 0.8267}
- noise_raw: {"V1": 14949.051609849952, "E1": 174965.13916944584}
- predictions: "waves/methods_E_EMU_committed_s0_s2_r1/predictions.csv"
- graded_at: "2026-11-24T08:35:23+00:00"
- n_train: 56
- n_hv: 56
- cumulative_hv: 142037590196040.38
- gain: 41514314795820.64
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
- r2_max_mwh: 194.78626280162212
- calibration: {"V1": {"mean_z": 0.015, "rms_z": 0.177, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}, "E1": {"mean_z": 0.086, "rms_z": 0.2, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}}
- C2_review: false
- C3_review: false
- halt: null
- decision: "graded (record_only)"
- fit_info: {"V1": {"fit_definition": "house"}, "E1": {"fit_definition": "v2", "converged": true, "mode_gap_nats": 53.68406410300448, "gap_second_nats": 2.884701544303425e-07, "n_within_tol": 13, "n_failed": 0, "map_total": -19.200766147217088, "noise_sd_raw": 174965.1391694458, "noise_over_sigma_c": 0.5600269029701294}}
- qnehvi_seconds: 6.4
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
    - [2.99999e+06, 8.09863e+09]
    - [2.17819e+06, 8.11527e+09]
    - [3.44041e+06, 8.08515e+09]
    - [1.4503e+06, 8.13692e+09]
    - [2.72074e+06, 8.10435e+09]
    - [1.71001e+06, 8.12593e+09]
    - [1.28077e+06, 8.15024e+09]
    - [1.99768e+06, 8.11846e+09]
<!-- END r1 -->

<!-- BEGIN r2 -->
## Round 2 (methods_E_EMU_committed_s0_s2_r2)
- proposed_at: "2026-11-24T08:35:30+00:00"
- wave: "methods_E_EMU_committed_s0_s2_r2"
- acq: "qnehvi"
- acq_seed: 20261208
- guardrail_mode: "monitor"
- settings: {"mc_samples": 128, "num_restarts": 20, "raw_samples": 512, "alpha": 0.0, "prune_baseline": true, "sequential": true, "fast_mode": false, "constraint": "none", "guardrail_mode": "monitor", "seed": 20261208, "dtype": "float64", "bound_snaps": {"to_0": 0, "to_1": 0, "tol": 1e-12, "note": "bound cleanup after x * sx + mx; not lattice snapping"}}
- botorch: "0.16.1"
- bo_gp_sha: "60e6328236e745b3d34dc8cd704bb72888ae5d15"
- loo_rms_z: {"V1": 0.3691, "E1": 0.7987}
- noise_raw: {"V1": 14946.422801841847, "E1": 169757.98967704465}
- predictions: "waves/methods_E_EMU_committed_s0_s2_r2/predictions.csv"
- graded_at: "2026-11-24T08:35:31+00:00"
- n_train: 64
- n_hv: 64
- cumulative_hv: 146786655821532.72
- gain: 4749065625492.344
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
- r2_max_mwh: 154.62622659857303
- calibration: {"V1": {"mean_z": -0.06, "rms_z": 0.186, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}, "E1": {"mean_z": 0.11, "rms_z": 0.631, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}}
- C2_review: false
- C3_review: false
- halt: null
- decision: "graded (record_only)"
- fit_info: {"V1": {"fit_definition": "house"}, "E1": {"fit_definition": "v2", "converged": true, "mode_gap_nats": NaN, "gap_second_nats": 9.426677038959497e-08, "n_within_tol": 16, "n_failed": 0, "map_total": -6.54358118605948, "noise_sd_raw": 169757.9896770447, "noise_over_sigma_c": 0.5433599039474971}}
- qnehvi_seconds: 6.0
- designs (MW per site ['110', '140', '146', '163', '270', '274']):
    - [0.000, 96.692, 0.000, 185.400, 579.000, 0.000]
    - [0.000, 250.600, 74.049, 185.400, 579.000, 746.400]
    - [338.600, 77.588, 0.000, 185.400, 579.000, 0.000]
    - [0.000, 250.600, 0.000, 185.400, 579.000, 0.000]
    - [24.754, 250.600, 211.954, 185.400, 579.000, 746.400]
    - [148.593, 250.600, 204.614, 185.400, 579.000, 746.400]
    - [0.000, 101.027, 0.000, 185.400, 579.000, 746.400]
    - [0.000, 0.000, 0.000, 185.400, 266.944, 746.400]
- realized Y (['V1', 'E1']):
    - [3.25242e+06, 8.09167e+09]
    - [1.57706e+06, 8.13108e+09]
    - [2.57919e+06, 8.11018e+09]
    - [2.97075e+06, 8.09868e+09]
    - [1.36482e+06, 8.1438e+09]
    - [1.1951e+06, 8.15668e+09]
    - [1.86463e+06, 8.12241e+09]
    - [2.45917e+06, 8.11399e+09]
<!-- END r2 -->

<!-- BEGIN r3 -->
## Round 3 (methods_E_EMU_committed_s0_s2_r3)
- proposed_at: "2026-11-24T08:35:38+00:00"
- wave: "methods_E_EMU_committed_s0_s2_r3"
- acq: "qnehvi"
- acq_seed: 20261209
- guardrail_mode: "monitor"
- settings: {"mc_samples": 128, "num_restarts": 20, "raw_samples": 512, "alpha": 0.0, "prune_baseline": true, "sequential": true, "fast_mode": false, "constraint": "none", "guardrail_mode": "monitor", "seed": 20261209, "dtype": "float64", "bound_snaps": {"to_0": 0, "to_1": 0, "tol": 1e-12, "note": "bound cleanup after x * sx + mx; not lattice snapping"}}
- botorch: "0.16.1"
- bo_gp_sha: "60e6328236e745b3d34dc8cd704bb72888ae5d15"
- loo_rms_z: {"V1": 0.3541, "E1": 0.8263}
- noise_raw: {"V1": 15536.010841456684, "E1": 167641.716419502}
- predictions: "waves/methods_E_EMU_committed_s0_s2_r3/predictions.csv"
- graded_at: "2026-11-24T08:35:38+00:00"
- n_train: 72
- n_hv: 72
- cumulative_hv: 148266806762754.1
- gain: 1480150941221.375
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
- r2_max_mwh: 175.51600963130812
- calibration: {"V1": {"mean_z": -0.069, "rms_z": 0.239, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}, "E1": {"mean_z": -0.818, "rms_z": 1.512, "cov95": 7, "n_abs_z_gt3": 0, "transform": "std"}}
- C2_review: false
- C3_review: false
- halt: null
- decision: "graded (record_only)"
- fit_info: {"V1": {"fit_definition": "house"}, "E1": {"fit_definition": "v2", "converged": true, "mode_gap_nats": NaN, "gap_second_nats": 5.13710070038087e-08, "n_within_tol": 16, "n_failed": 0, "map_total": 11.512751659412785, "noise_sd_raw": 167641.716419502, "noise_over_sigma_c": 0.5365861548230365}}
- qnehvi_seconds: 5.9
- designs (MW per site ['110', '140', '146', '163', '270', '274']):
    - [0.000, 0.000, 0.000, 0.000, 579.000, 746.400]
    - [0.000, 250.600, 115.917, 185.400, 579.000, 746.400]
    - [0.000, 162.395, 0.000, 185.400, 579.000, 0.000]
    - [67.795, 250.600, 184.565, 185.400, 579.000, 746.400]
    - [203.487, 250.600, 189.547, 184.799, 579.000, 746.400]
    - [0.000, 250.600, 36.146, 185.400, 579.000, 746.400]
    - [338.600, 0.000, 0.000, 185.400, 0.000, 746.400]
    - [12.115, 250.600, 185.888, 185.400, 579.000, 746.400]
- realized Y (['V1', 'E1']):
    - [2.3372e+06, 8.11494e+09]
    - [1.5059e+06, 8.13432e+09]
    - [3.12636e+06, 8.09491e+09]
    - [1.31723e+06, 8.14649e+09]
    - [1.16722e+06, 8.15949e+09]
    - [1.63489e+06, 8.12785e+09]
    - [2.46008e+06, 8.11342e+09]
    - [1.40365e+06, 8.13996e+09]
<!-- END r3 -->

<!-- BEGIN r4 -->
## Round 4 (methods_E_EMU_committed_s0_s2_r4)
- proposed_at: "2026-11-24T08:35:46+00:00"
- wave: "methods_E_EMU_committed_s0_s2_r4"
- acq: "qnehvi"
- acq_seed: 20261210
- guardrail_mode: "monitor"
- settings: {"mc_samples": 128, "num_restarts": 20, "raw_samples": 512, "alpha": 0.0, "prune_baseline": true, "sequential": true, "fast_mode": false, "constraint": "none", "guardrail_mode": "monitor", "seed": 20261210, "dtype": "float64", "bound_snaps": {"to_0": 2, "to_1": 0, "tol": 1e-12, "note": "bound cleanup after x * sx + mx; not lattice snapping"}}
- botorch: "0.16.1"
- bo_gp_sha: "60e6328236e745b3d34dc8cd704bb72888ae5d15"
- loo_rms_z: {"V1": 0.3316, "E1": 0.8865}
- noise_raw: {"V1": 16255.99471110412, "E1": 270440.079889606}
- predictions: "waves/methods_E_EMU_committed_s0_s2_r4/predictions.csv"
- graded_at: "2026-11-24T08:35:47+00:00"
- n_train: 80
- n_hv: 80
- cumulative_hv: 148892529027128.3
- gain: 625722264374.2188
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
- r2_max_mwh: 189.3167035357051
- calibration: {"V1": {"mean_z": 0.032, "rms_z": 0.29, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}, "E1": {"mean_z": 0.516, "rms_z": 0.932, "cov95": 7, "n_abs_z_gt3": 0, "transform": "std"}}
- C2_review: false
- C3_review: false
- halt: null
- decision: "graded (record_only)"
- fit_info: {"V1": {"fit_definition": "house"}, "E1": {"fit_definition": "v2", "converged": true, "mode_gap_nats": NaN, "gap_second_nats": 1.3641496821037435e-09, "n_within_tol": 16, "n_failed": 0, "map_total": 25.20283448196558, "noise_sd_raw": 270440.0798896059, "noise_over_sigma_c": 0.8656222668042135}}
- qnehvi_seconds: 7.3
- designs (MW per site ['110', '140', '146', '163', '270', '274']):
    - [338.600, 250.600, 68.564, 185.400, 579.000, 746.400]
    - [128.452, 250.600, 184.540, 185.400, 579.000, 746.400]
    - [0.000, 250.600, 0.000, 185.400, 0.000, 746.400]
    - [0.000, 250.600, 0.000, 0.000, 0.000, 746.400]
    - [338.600, 250.600, 1.768, 185.400, 579.000, 746.400]
    - [338.600, 93.127, 164.889, 185.400, 579.000, 746.400]
    - [41.412, 0.000, 0.000, 185.400, 579.000, 0.000]
    - [338.600, 0.000, 0.000, 0.000, 0.000, 746.400]
- realized Y (['V1', 'E1']):
    - [1.27523e+06, 8.1564e+09]
    - [1.24239e+06, 8.15389e+09]
    - [2.58502e+06, 8.10942e+09]
    - [2.90201e+06, 8.10255e+09]
    - [1.41787e+06, 8.15041e+09]
    - [1.22471e+06, 8.15711e+09]
    - [3.35028e+06, 8.08844e+09]
    - [2.77066e+06, 8.10603e+09]
<!-- END r4 -->
