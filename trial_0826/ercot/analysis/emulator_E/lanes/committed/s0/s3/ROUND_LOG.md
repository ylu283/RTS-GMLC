# methods_E arm qnehvi seed_id 3 — ROUND_LOG (prompt 55; acq = qnehvi, base = ['n0_E'] nav prefix n0 = 48, objectives = ['V1', 'E1'])

Ledger: `lanes/committed/s0/s3/ledger.json`. stop_rule = record_only: gain_k and
would_stop_k = (gain_k < tau) AND (gain_{k-1} < tau) are graded and logged under tau_joint
(headline) and tau_marginal (recorded) with the joint-vs-marginal sensitivity column; the
rule never halts; every lane runs to hard_cap = 4. tau_joint = 0, tau_marginal = 0 — ZERO: the stop rule is budget-cap-only and the cap governs (plan 3).
E-D5 OPEN: see README.md for the two readings of a fire. Halts ONLY per plan 1.2/1.3
(HALT_FOR_DECISION.md). Acquisition jobs never submit; Kay submits via submit_ready_E.sh.
Stop NOW: `touch lanes/committed/s0/s3/STOP` on the CRC clone, then qdel the lane's JIDs.

<!-- BEGIN r1 -->
## Round 1 (methods_E_EMU_committed_s0_s3_r1)
- proposed_at: "2026-11-24T08:35:55+00:00"
- wave: "methods_E_EMU_committed_s0_s3_r1"
- acq: "qnehvi"
- acq_seed: 20261307
- guardrail_mode: "monitor"
- settings: {"mc_samples": 128, "num_restarts": 20, "raw_samples": 512, "alpha": 0.0, "prune_baseline": true, "sequential": true, "fast_mode": false, "constraint": "none", "guardrail_mode": "monitor", "seed": 20261307, "dtype": "float64", "bound_snaps": {"to_0": 0, "to_1": 0, "tol": 1e-12, "note": "bound cleanup after x * sx + mx; not lattice snapping"}}
- botorch: "0.16.1"
- bo_gp_sha: "60e6328236e745b3d34dc8cd704bb72888ae5d15"
- loo_rms_z: {"V1": 0.4268, "E1": 0.8267}
- noise_raw: {"V1": 14949.051609849952, "E1": 174965.13916944584}
- predictions: "waves/methods_E_EMU_committed_s0_s3_r1/predictions.csv"
- graded_at: "2026-11-24T08:35:56+00:00"
- n_train: 56
- n_hv: 56
- cumulative_hv: 143312973193427.94
- gain: 42789697793208.2
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
- r2_max_mwh: 197.35545356098453
- calibration: {"V1": {"mean_z": -0.026, "rms_z": 0.167, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}, "E1": {"mean_z": 0.013, "rms_z": 0.174, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}}
- C2_review: false
- C3_review: false
- halt: null
- decision: "graded (record_only)"
- fit_info: {"V1": {"fit_definition": "house"}, "E1": {"fit_definition": "v2", "converged": true, "mode_gap_nats": 53.68406410300448, "gap_second_nats": 2.884701544303425e-07, "n_within_tol": 13, "n_failed": 0, "map_total": -19.200766147217088, "noise_sd_raw": 174965.1391694458, "noise_over_sigma_c": 0.5600269029701294}}
- qnehvi_seconds: 6.3
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
    - [2.99884e+06, 8.09812e+09]
    - [2.18097e+06, 8.11479e+09]
    - [3.43246e+06, 8.08472e+09]
    - [1.45025e+06, 8.13733e+09]
    - [2.7172e+06, 8.10436e+09]
    - [1.70644e+06, 8.1249e+09]
    - [1.27331e+06, 8.14996e+09]
    - [2.00589e+06, 8.11793e+09]
<!-- END r1 -->

<!-- BEGIN r2 -->
## Round 2 (methods_E_EMU_committed_s0_s3_r2)
- proposed_at: "2026-11-24T08:36:03+00:00"
- wave: "methods_E_EMU_committed_s0_s3_r2"
- acq: "qnehvi"
- acq_seed: 20261308
- guardrail_mode: "monitor"
- settings: {"mc_samples": 128, "num_restarts": 20, "raw_samples": 512, "alpha": 0.0, "prune_baseline": true, "sequential": true, "fast_mode": false, "constraint": "none", "guardrail_mode": "monitor", "seed": 20261308, "dtype": "float64", "bound_snaps": {"to_0": 0, "to_1": 0, "tol": 1e-12, "note": "bound cleanup after x * sx + mx; not lattice snapping"}}
- botorch: "0.16.1"
- bo_gp_sha: "60e6328236e745b3d34dc8cd704bb72888ae5d15"
- loo_rms_z: {"V1": 0.3731, "E1": 0.802}
- noise_raw: {"V1": 14958.51896973717, "E1": 169795.55902205626}
- predictions: "waves/methods_E_EMU_committed_s0_s3_r2/predictions.csv"
- graded_at: "2026-11-24T08:36:03+00:00"
- n_train: 64
- n_hv: 64
- cumulative_hv: 147379475311061.94
- gain: 4066502117634.0
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
- r2_max_mwh: 180.80328011863193
- calibration: {"V1": {"mean_z": 0.074, "rms_z": 0.148, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}, "E1": {"mean_z": 0.028, "rms_z": 1.448, "cov95": 6, "n_abs_z_gt3": 1, "transform": "std"}}
- C2_review: false
- C3_review: false
- halt: null
- decision: "graded (record_only)"
- fit_info: {"V1": {"fit_definition": "house"}, "E1": {"fit_definition": "v2", "converged": true, "mode_gap_nats": 73.13631549727427, "gap_second_nats": 8.554987829256788e-10, "n_within_tol": 14, "n_failed": 0, "map_total": -6.226799695472215, "noise_sd_raw": 169795.5590220563, "noise_over_sigma_c": 0.5434801555818131}}
- qnehvi_seconds: 6.2
- designs (MW per site ['110', '140', '146', '163', '270', '274']):
    - [88.758, 0.000, 0.000, 185.400, 579.000, 0.000]
    - [0.000, 250.600, 74.856, 185.400, 579.000, 746.400]
    - [0.000, 0.000, 0.000, 185.400, 218.404, 746.400]
    - [175.790, 250.600, 183.339, 185.400, 579.000, 746.400]
    - [40.281, 250.600, 185.018, 185.400, 579.000, 746.400]
    - [338.600, 0.000, 0.000, 185.400, 0.000, 746.400]
    - [0.000, 250.600, 0.000, 185.400, 579.000, 0.000]
    - [0.000, 0.000, 0.000, 185.400, 579.000, 709.728]
- realized Y (['V1', 'E1']):
    - [3.24152e+06, 8.09157e+09]
    - [1.57043e+06, 8.13197e+09]
    - [2.54852e+06, 8.11179e+09]
    - [1.18923e+06, 8.15708e+09]
    - [1.35792e+06, 8.14292e+09]
    - [2.46e+06, 8.11452e+09]
    - [2.97596e+06, 8.09851e+09]
    - [2.072e+06, 8.11597e+09]
<!-- END r2 -->

<!-- BEGIN r3 -->
## Round 3 (methods_E_EMU_committed_s0_s3_r3)
- proposed_at: "2026-11-24T08:36:10+00:00"
- wave: "methods_E_EMU_committed_s0_s3_r3"
- acq: "qnehvi"
- acq_seed: 20261309
- guardrail_mode: "monitor"
- settings: {"mc_samples": 128, "num_restarts": 20, "raw_samples": 512, "alpha": 0.0, "prune_baseline": true, "sequential": true, "fast_mode": false, "constraint": "none", "guardrail_mode": "monitor", "seed": 20261309, "dtype": "float64", "bound_snaps": {"to_0": 0, "to_1": 0, "tol": 1e-12, "note": "bound cleanup after x * sx + mx; not lattice snapping"}}
- botorch: "0.16.1"
- bo_gp_sha: "60e6328236e745b3d34dc8cd704bb72888ae5d15"
- loo_rms_z: {"V1": 0.3464, "E1": 0.9307}
- noise_raw: {"V1": 15548.454021274925, "E1": 301057.87260746525}
- predictions: "waves/methods_E_EMU_committed_s0_s3_r3/predictions.csv"
- graded_at: "2026-11-24T08:36:11+00:00"
- n_train: 72
- n_hv: 72
- cumulative_hv: 148731377957869.16
- gain: 1351902646807.2188
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
- r2_max_mwh: 189.27768045536857
- calibration: {"V1": {"mean_z": 0.002, "rms_z": 0.213, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}, "E1": {"mean_z": 0.125, "rms_z": 0.54, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}}
- C2_review: false
- C3_review: false
- halt: null
- decision: "graded (record_only)"
- fit_info: {"V1": {"fit_definition": "house"}, "E1": {"fit_definition": "v2", "converged": true, "mode_gap_nats": NaN, "gap_second_nats": 4.4694935752431775e-08, "n_within_tol": 16, "n_failed": 0, "map_total": 6.2697953387345144, "noise_sd_raw": 301057.87260746525, "noise_over_sigma_c": 0.9636234327105159}}
- qnehvi_seconds: 6.0
- designs (MW per site ['110', '140', '146', '163', '270', '274']):
    - [189.310, 250.600, 215.826, 185.400, 579.000, 746.400]
    - [43.893, 0.000, 0.000, 185.400, 579.000, 0.000]
    - [0.000, 0.000, 268.000, 185.400, 0.000, 746.400]
    - [0.000, 250.600, 0.000, 185.400, 579.000, 606.171]
    - [0.000, 250.600, 0.000, 18.522, 579.000, 746.400]
    - [0.000, 250.600, 0.000, 185.400, 0.000, 746.400]
    - [35.973, 250.600, 0.000, 185.400, 579.000, 0.000]
    - [0.000, 250.600, 35.499, 185.400, 579.000, 746.400]
- realized Y (['V1', 'E1']):
    - [1.15277e+06, 8.16077e+09]
    - [3.33123e+06, 8.0878e+09]
    - [2.58093e+06, 8.11216e+09]
    - [1.83207e+06, 8.12514e+09]
    - [1.91704e+06, 8.12322e+09]
    - [2.58867e+06, 8.10966e+09]
    - [2.90261e+06, 8.10162e+09]
    - [1.63817e+06, 8.12847e+09]
<!-- END r3 -->

<!-- BEGIN r4 -->
## Round 4 (methods_E_EMU_committed_s0_s3_r4)
- proposed_at: "2026-11-24T08:36:20+00:00"
- wave: "methods_E_EMU_committed_s0_s3_r4"
- acq: "qnehvi"
- acq_seed: 20261310
- guardrail_mode: "monitor"
- settings: {"mc_samples": 128, "num_restarts": 20, "raw_samples": 512, "alpha": 0.0, "prune_baseline": true, "sequential": true, "fast_mode": false, "constraint": "none", "guardrail_mode": "monitor", "seed": 20261310, "dtype": "float64", "bound_snaps": {"to_0": 0, "to_1": 0, "tol": 1e-12, "note": "bound cleanup after x * sx + mx; not lattice snapping"}}
- botorch: "0.16.1"
- bo_gp_sha: "60e6328236e745b3d34dc8cd704bb72888ae5d15"
- loo_rms_z: {"V1": 0.3318, "E1": 0.9185}
- noise_raw: {"V1": 15792.494240614553, "E1": 277539.48890816205}
- predictions: "waves/methods_E_EMU_committed_s0_s3_r4/predictions.csv"
- graded_at: "2026-11-24T08:36:21+00:00"
- n_train: 80
- n_hv: 80
- cumulative_hv: 149623766418028.12
- gain: 892388460158.9688
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
- r2_max_mwh: 177.73593630806207
- calibration: {"V1": {"mean_z": 0.193, "rms_z": 0.409, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}, "E1": {"mean_z": 0.584, "rms_z": 0.713, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}}
- C2_review: false
- C3_review: false
- halt: null
- decision: "graded (record_only)"
- fit_info: {"V1": {"fit_definition": "house"}, "E1": {"fit_definition": "v2", "converged": true, "mode_gap_nats": NaN, "gap_second_nats": 5.618524312467343e-09, "n_within_tol": 16, "n_failed": 0, "map_total": 22.534538264773914, "noise_sd_raw": 277539.48890816193, "noise_over_sigma_c": 0.8883459937389241}}
- qnehvi_seconds: 8.0
- designs (MW per site ['110', '140', '146', '163', '270', '274']):
    - [0.000, 79.282, 0.000, 185.400, 579.000, 746.400]
    - [115.113, 250.600, 213.858, 185.400, 579.000, 746.400]
    - [0.000, 0.000, 0.000, 185.400, 579.000, 486.558]
    - [338.600, 0.000, 0.000, 0.000, 579.000, 0.000]
    - [338.600, 250.600, 0.855, 185.400, 579.000, 746.400]
    - [0.000, 250.600, 115.492, 185.400, 579.000, 746.400]
    - [338.600, 250.600, 73.547, 185.400, 579.000, 746.400]
    - [338.600, 250.600, 32.457, 185.400, 579.000, 746.400]
- realized Y (['V1', 'E1']):
    - [1.89483e+06, 8.12138e+09]
    - [1.23217e+06, 8.15391e+09]
    - [2.3761e+06, 8.11265e+09]
    - [3.13424e+06, 8.1053e+09]
    - [1.41368e+06, 8.14999e+09]
    - [1.50468e+06, 8.13469e+09]
    - [1.26821e+06, 8.15702e+09]
    - [1.34833e+06, 8.15274e+09]
<!-- END r4 -->
