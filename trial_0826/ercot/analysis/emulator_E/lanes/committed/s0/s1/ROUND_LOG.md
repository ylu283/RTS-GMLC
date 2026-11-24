# methods_E arm qnehvi seed_id 1 — ROUND_LOG (prompt 55; acq = qnehvi, base = ['n0_E'] nav prefix n0 = 48, objectives = ['V1', 'E1'])

Ledger: `lanes/committed/s0/s1/ledger.json`. stop_rule = record_only: gain_k and
would_stop_k = (gain_k < tau) AND (gain_{k-1} < tau) are graded and logged under tau_joint
(headline) and tau_marginal (recorded) with the joint-vs-marginal sensitivity column; the
rule never halts; every lane runs to hard_cap = 4. tau_joint = 0, tau_marginal = 0 — ZERO: the stop rule is budget-cap-only and the cap governs (plan 3).
E-D5 OPEN: see README.md for the two readings of a fire. Halts ONLY per plan 1.2/1.3
(HALT_FOR_DECISION.md). Acquisition jobs never submit; Kay submits via submit_ready_E.sh.
Stop NOW: `touch lanes/committed/s0/s1/STOP` on the CRC clone, then qdel the lane's JIDs.

<!-- BEGIN r1 -->
## Round 1 (methods_E_EMU_committed_s0_s1_r1)
- proposed_at: "2026-11-24T08:34:49+00:00"
- wave: "methods_E_EMU_committed_s0_s1_r1"
- acq: "qnehvi"
- acq_seed: 20261107
- guardrail_mode: "monitor"
- settings: {"mc_samples": 128, "num_restarts": 20, "raw_samples": 512, "alpha": 0.0, "prune_baseline": true, "sequential": true, "fast_mode": false, "constraint": "none", "guardrail_mode": "monitor", "seed": 20261107, "dtype": "float64", "bound_snaps": {"to_0": 0, "to_1": 0, "tol": 1e-12, "note": "bound cleanup after x * sx + mx; not lattice snapping"}}
- botorch: "0.16.1"
- bo_gp_sha: "60e6328236e745b3d34dc8cd704bb72888ae5d15"
- loo_rms_z: {"V1": 0.4268, "E1": 0.8267}
- noise_raw: {"V1": 14949.051609849952, "E1": 174965.13916944584}
- predictions: "waves/methods_E_EMU_committed_s0_s1_r1/predictions.csv"
- graded_at: "2026-11-24T08:34:50+00:00"
- n_train: 56
- n_hv: 56
- cumulative_hv: 142766438891871.0
- gain: 42243163491651.266
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
- r2_max_mwh: 193.59315002783313
- calibration: {"V1": {"mean_z": -0.008, "rms_z": 0.158, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}, "E1": {"mean_z": 0.037, "rms_z": 0.197, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}}
- C2_review: false
- C3_review: false
- halt: null
- decision: "graded (record_only)"
- fit_info: {"V1": {"fit_definition": "house"}, "E1": {"fit_definition": "v2", "converged": true, "mode_gap_nats": 53.68406410300448, "gap_second_nats": 2.884701544303425e-07, "n_within_tol": 13, "n_failed": 0, "map_total": -19.200766147217088, "noise_sd_raw": 174965.1391694458, "noise_over_sigma_c": 0.5600269029701294}}
- qnehvi_seconds: 7.3
- r1_shared_designs_with_seed: {"0": 3}
- designs (MW per site ['110', '140', '146', '163', '270', '274']):
    - [0.000, 0.000, 0.000, 185.400, 0.000, 746.400]
    - [0.000, 0.000, 0.000, 185.400, 579.000, 615.441]
    - [0.000, 0.000, 0.000, 185.400, 579.000, 0.000]
    - [0.000, 250.600, 162.275, 185.400, 579.000, 746.400]
    - [338.600, 0.000, 0.000, 185.400, 579.000, 0.000]
    - [0.000, 250.600, 0.000, 185.400, 579.000, 746.400]
    - [82.454, 250.600, 209.293, 185.400, 579.000, 746.400]
    - [0.000, 19.759, 0.000, 185.400, 579.000, 746.400]
- realized Y (['V1', 'E1']):
    - [3.002e+06, 8.09879e+09]
    - [2.17881e+06, 8.11495e+09]
    - [3.43151e+06, 8.08461e+09]
    - [1.45303e+06, 8.1368e+09]
    - [2.71779e+06, 8.10457e+09]
    - [1.71031e+06, 8.12581e+09]
    - [1.27538e+06, 8.14947e+09]
    - [2.00367e+06, 8.1181e+09]
<!-- END r1 -->

<!-- BEGIN r2 -->
## Round 2 (methods_E_EMU_committed_s0_s1_r2)
- proposed_at: "2026-11-24T08:34:57+00:00"
- wave: "methods_E_EMU_committed_s0_s1_r2"
- acq: "qnehvi"
- acq_seed: 20261108
- guardrail_mode: "monitor"
- settings: {"mc_samples": 128, "num_restarts": 20, "raw_samples": 512, "alpha": 0.0, "prune_baseline": true, "sequential": true, "fast_mode": false, "constraint": "none", "guardrail_mode": "monitor", "seed": 20261108, "dtype": "float64", "bound_snaps": {"to_0": 0, "to_1": 0, "tol": 1e-12, "note": "bound cleanup after x * sx + mx; not lattice snapping"}}
- botorch: "0.16.1"
- bo_gp_sha: "60e6328236e745b3d34dc8cd704bb72888ae5d15"
- loo_rms_z: {"V1": 0.3736, "E1": 0.7952}
- noise_raw: {"V1": 14948.188802275903, "E1": 169369.46752006476}
- predictions: "waves/methods_E_EMU_committed_s0_s1_r2/predictions.csv"
- graded_at: "2026-11-24T08:34:58+00:00"
- n_train: 64
- n_hv: 64
- cumulative_hv: 147697738876980.34
- gain: 4931299985109.344
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
- r2_max_mwh: 192.68703367773287
- calibration: {"V1": {"mean_z": -0.015, "rms_z": 0.157, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}, "E1": {"mean_z": 0.036, "rms_z": 0.567, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}}
- C2_review: false
- C3_review: false
- halt: null
- decision: "graded (record_only)"
- fit_info: {"V1": {"fit_definition": "house"}, "E1": {"fit_definition": "v2", "converged": true, "mode_gap_nats": NaN, "gap_second_nats": 3.490686140139587e-08, "n_within_tol": 16, "n_failed": 0, "map_total": -6.402972277072696, "noise_sd_raw": 169369.46752006476, "noise_over_sigma_c": 0.5421163255904505}}
- qnehvi_seconds: 6.5
- designs (MW per site ['110', '140', '146', '163', '270', '274']):
    - [0.000, 0.000, 0.000, 185.400, 579.000, 79.739]
    - [0.000, 250.600, 74.290, 185.400, 579.000, 746.400]
    - [0.000, 0.000, 0.000, 185.400, 579.000, 438.966]
    - [0.000, 250.600, 0.000, 185.400, 579.000, 0.000]
    - [156.002, 250.600, 203.592, 185.400, 579.000, 746.400]
    - [25.049, 250.600, 211.582, 185.400, 579.000, 746.400]
    - [0.000, 250.600, 0.000, 185.400, 0.000, 746.400]
    - [0.000, 250.600, 210.261, 185.400, 579.000, 746.400]
- realized Y (['V1', 'E1']):
    - [3.25016e+06, 8.0919e+09]
    - [1.56881e+06, 8.13096e+09]
    - [2.46184e+06, 8.11047e+09]
    - [2.97278e+06, 8.09842e+09]
    - [1.1858e+06, 8.15744e+09]
    - [1.36412e+06, 8.1428e+09]
    - [2.58686e+06, 8.1093e+09]
    - [1.41006e+06, 8.13983e+09]
<!-- END r2 -->

<!-- BEGIN r3 -->
## Round 3 (methods_E_EMU_committed_s0_s1_r3)
- proposed_at: "2026-11-24T08:35:05+00:00"
- wave: "methods_E_EMU_committed_s0_s1_r3"
- acq: "qnehvi"
- acq_seed: 20261109
- guardrail_mode: "monitor"
- settings: {"mc_samples": 128, "num_restarts": 20, "raw_samples": 512, "alpha": 0.0, "prune_baseline": true, "sequential": true, "fast_mode": false, "constraint": "none", "guardrail_mode": "monitor", "seed": 20261109, "dtype": "float64", "bound_snaps": {"to_0": 0, "to_1": 0, "tol": 1e-12, "note": "bound cleanup after x * sx + mx; not lattice snapping"}}
- botorch: "0.16.1"
- bo_gp_sha: "60e6328236e745b3d34dc8cd704bb72888ae5d15"
- loo_rms_z: {"V1": 0.3419, "E1": 0.8185}
- noise_raw: {"V1": 15883.70018005054, "E1": 122881.74578602643}
- predictions: "waves/methods_E_EMU_committed_s0_s1_r3/predictions.csv"
- graded_at: "2026-11-24T08:35:06+00:00"
- n_train: 72
- n_hv: 72
- cumulative_hv: 149118220266859.44
- gain: 1420481389879.0938
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
- r2_max_mwh: 183.71625576658826
- calibration: {"V1": {"mean_z": 0.01, "rms_z": 0.258, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}, "E1": {"mean_z": -0.37, "rms_z": 1.53, "cov95": 5, "n_abs_z_gt3": 0, "transform": "std"}}
- C2_review: false
- C3_review: false
- halt: null
- decision: "graded (record_only)"
- fit_info: {"V1": {"fit_definition": "house"}, "E1": {"fit_definition": "v2", "converged": true, "mode_gap_nats": NaN, "gap_second_nats": 8.82499513465973e-08, "n_within_tol": 16, "n_failed": 0, "map_total": 12.151797188786336, "noise_sd_raw": 122881.74578602643, "noise_over_sigma_c": 0.3933188282579245}}
- qnehvi_seconds: 6.3
- designs (MW per site ['110', '140', '146', '163', '270', '274']):
    - [338.600, 0.000, 0.000, 185.400, 579.000, 746.400]
    - [0.000, 250.600, 0.000, 28.826, 579.000, 746.400]
    - [0.000, 100.941, 0.000, 185.400, 579.000, 746.400]
    - [119.806, 250.600, 202.253, 185.400, 579.000, 746.400]
    - [0.000, 0.000, 0.000, 0.000, 579.000, 746.400]
    - [0.000, 0.000, 0.000, 40.611, 579.000, 0.000]
    - [62.743, 250.600, 191.598, 185.400, 579.000, 746.400]
    - [0.000, 250.600, 35.858, 185.400, 579.000, 746.400]
- realized Y (['V1', 'E1']):
    - [1.64303e+06, 8.1343e+09]
    - [1.90471e+06, 8.12337e+09]
    - [1.86062e+06, 8.12241e+09]
    - [1.23293e+06, 8.15301e+09]
    - [2.33555e+06, 8.11462e+09]
    - [3.80246e+06, 8.08273e+09]
    - [1.31584e+06, 8.14651e+09]
    - [1.6342e+06, 8.1279e+09]
<!-- END r3 -->

<!-- BEGIN r4 -->
## Round 4 (methods_E_EMU_committed_s0_s1_r4)
- proposed_at: "2026-11-24T08:35:14+00:00"
- wave: "methods_E_EMU_committed_s0_s1_r4"
- acq: "qnehvi"
- acq_seed: 20261110
- guardrail_mode: "monitor"
- settings: {"mc_samples": 128, "num_restarts": 20, "raw_samples": 512, "alpha": 0.0, "prune_baseline": true, "sequential": true, "fast_mode": false, "constraint": "none", "guardrail_mode": "monitor", "seed": 20261110, "dtype": "float64", "bound_snaps": {"to_0": 0, "to_1": 0, "tol": 1e-12, "note": "bound cleanup after x * sx + mx; not lattice snapping"}}
- botorch: "0.16.1"
- bo_gp_sha: "60e6328236e745b3d34dc8cd704bb72888ae5d15"
- loo_rms_z: {"V1": 0.3145, "E1": 0.8809}
- noise_raw: {"V1": 16261.963535340716, "E1": 239526.9075686753}
- predictions: "waves/methods_E_EMU_committed_s0_s1_r4/predictions.csv"
- graded_at: "2026-11-24T08:35:15+00:00"
- n_train: 80
- n_hv: 80
- cumulative_hv: 149483740870087.66
- gain: 365520603228.21875
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
- r2_max_mwh: 180.46120260799304
- calibration: {"V1": {"mean_z": -0.181, "rms_z": 0.369, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}, "E1": {"mean_z": -0.527, "rms_z": 0.942, "cov95": 7, "n_abs_z_gt3": 0, "transform": "std"}}
- C2_review: false
- C3_review: false
- halt: null
- decision: "graded (record_only)"
- fit_info: {"V1": {"fit_definition": "house"}, "E1": {"fit_definition": "v2", "converged": true, "mode_gap_nats": NaN, "gap_second_nats": 1.8902102993934022e-08, "n_within_tol": 16, "n_failed": 0, "map_total": 24.03178210798622, "noise_sd_raw": 239526.90756867538, "noise_over_sigma_c": 0.7666756524211816}}
- qnehvi_seconds: 7.6
- designs (MW per site ['110', '140', '146', '163', '270', '274']):
    - [0.000, 0.000, 0.000, 185.400, 47.024, 746.400]
    - [338.600, 0.000, 99.122, 25.189, 579.000, 746.400]
    - [183.390, 250.600, 211.714, 182.922, 579.000, 746.400]
    - [0.000, 0.000, 0.000, 0.000, 579.000, 696.502]
    - [338.600, 250.600, 116.753, 121.238, 579.000, 746.400]
    - [338.600, 30.792, 268.000, 185.400, 579.000, 746.400]
    - [338.600, 0.000, 0.000, 0.000, 0.000, 746.400]
    - [338.600, 0.000, 0.000, 185.400, 0.000, 746.400]
- realized Y (['V1', 'E1']):
    - [2.89159e+06, 8.10186e+09]
    - [1.61281e+06, 8.14012e+09]
    - [1.1636e+06, 8.15945e+09]
    - [2.3931e+06, 8.11389e+09]
    - [1.18657e+06, 8.16009e+09]
    - [1.24614e+06, 8.15759e+09]
    - [2.77054e+06, 8.10542e+09]
    - [2.45318e+06, 8.11411e+09]
<!-- END r4 -->
