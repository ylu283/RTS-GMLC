# methods_E arm qnehvi seed_id 1 — ROUND_LOG (prompt 55; acq = qnehvi, base = ['n0_E'] nav prefix n0 = 48, objectives = ['V1', 'E1'])

Ledger: `lanes/committed/s1/s1/ledger.json`. stop_rule = record_only: gain_k and
would_stop_k = (gain_k < tau) AND (gain_{k-1} < tau) are graded and logged under tau_joint
(headline) and tau_marginal (recorded) with the joint-vs-marginal sensitivity column; the
rule never halts; every lane runs to hard_cap = 4. tau_joint = 0, tau_marginal = 0 — ZERO: the stop rule is budget-cap-only and the cap governs (plan 3).
E-D5 OPEN: see README.md for the two readings of a fire. Halts ONLY per plan 1.2/1.3
(HALT_FOR_DECISION.md). Acquisition jobs never submit; Kay submits via submit_ready_E.sh.
Stop NOW: `touch lanes/committed/s1/s1/STOP` on the CRC clone, then qdel the lane's JIDs.

<!-- BEGIN r1 -->
## Round 1 (methods_E_EMU_committed_s1_s1_r1)
- proposed_at: "2026-11-24T08:34:54+00:00"
- wave: "methods_E_EMU_committed_s1_s1_r1"
- acq: "qnehvi"
- acq_seed: 20261107
- guardrail_mode: "monitor"
- settings: {"mc_samples": 128, "num_restarts": 20, "raw_samples": 512, "alpha": 0.0, "prune_baseline": true, "sequential": true, "fast_mode": false, "constraint": "none", "guardrail_mode": "monitor", "seed": 20261107, "dtype": "float64", "bound_snaps": {"to_0": 0, "to_1": 0, "tol": 1e-12, "note": "bound cleanup after x * sx + mx; not lattice snapping"}}
- botorch: "0.16.1"
- bo_gp_sha: "60e6328236e745b3d34dc8cd704bb72888ae5d15"
- loo_rms_z: {"V1": 0.4268, "E1": 0.8267}
- noise_raw: {"V1": 14949.051609849952, "E1": 174965.13916944584}
- predictions: "waves/methods_E_EMU_committed_s1_s1_r1/predictions.csv"
- graded_at: "2026-11-24T08:34:55+00:00"
- n_train: 56
- n_hv: 55
- cumulative_hv: 135107835533212.0
- gain: 34584560132992.266
- gain_tau_joint: null
- would_stop_joint: false
- gain_tau_marginal: null
- would_stop_marginal: false
- joint_vs_marginal: {"ratio_joint_over_marginal": null, "agree": true, "fires": {"joint": false, "marginal": false}}
- first_fire_round: {"tau_joint": null, "tau_marginal": null}
- n_outside_ref: 0
- violations: ["methods_E_EMU_committed_s1_s1_r1:3"]
- suspects: []
- r2_flag: false
- r2_max_mwh: 195.90573971251314
- calibration: {"V1": {"mean_z": -0.008, "rms_z": 0.169, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}, "E1": {"mean_z": 0.054, "rms_z": 0.209, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}}
- C2_review: false
- C3_review: false
- halt: null
- decision: "graded (record_only)"
- fit_info: {"V1": {"fit_definition": "house"}, "E1": {"fit_definition": "v2", "converged": true, "mode_gap_nats": 53.68406410300448, "gap_second_nats": 2.884701544303425e-07, "n_within_tol": 13, "n_failed": 0, "map_total": -19.200766147217088, "noise_sd_raw": 174965.1391694458, "noise_over_sigma_c": 0.5600269029701294}}
- qnehvi_seconds: 7.2
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
    - [3.0008e+06, 8.09841e+09]
    - [2.17548e+06, 8.11484e+09]
    - [3.43881e+06, 8.08482e+09]
    - [1.45055e+06, 8.13681e+09]
    - [2.71836e+06, 8.10517e+09]
    - [1.71386e+06, 8.1264e+09]
    - [1.27174e+06, 8.15006e+09]
    - [2.0046e+06, 8.11779e+09]
<!-- END r1 -->

<!-- BEGIN r2 -->
## Round 2 (methods_E_EMU_committed_s1_s1_r2)
- proposed_at: "2026-11-24T08:35:05+00:00"
- wave: "methods_E_EMU_committed_s1_s1_r2"
- acq: "qnehvi"
- acq_seed: 20261108
- guardrail_mode: "constrain"
- settings: {"mc_samples": 128, "num_restarts": 20, "raw_samples": 512, "alpha": 0.0, "prune_baseline": true, "sequential": true, "fast_mode": false, "constraint": "shed <= 1.0 MWh (GP on the accumulated R1 column)", "guardrail_mode": "constrain", "seed": 20261108, "dtype": "float64", "bound_snaps": {"to_0": 0, "to_1": 0, "tol": 1e-12, "note": "bound cleanup after x * sx + mx; not lattice snapping"}}
- botorch: "0.16.1"
- bo_gp_sha: "60e6328236e745b3d34dc8cd704bb72888ae5d15"
- loo_rms_z: {"V1": 0.3734, "E1": 0.8009}
- noise_raw: {"V1": 14954.94152135701, "E1": 169813.88764063036}
- predictions: "waves/methods_E_EMU_committed_s1_s1_r2/predictions.csv"
- graded_at: "2026-11-24T08:35:06+00:00"
- n_train: 64
- n_hv: 63
- cumulative_hv: 144608413447957.62
- gain: 9500577914745.625
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
- r2_max_mwh: 202.34039146795152
- calibration: {"V1": {"mean_z": -0.054, "rms_z": 0.303, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}, "E1": {"mean_z": -0.336, "rms_z": 0.525, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}}
- C2_review: false
- C3_review: false
- halt: null
- decision: "graded (record_only)"
- fit_info: {"V1": {"fit_definition": "house"}, "E1": {"fit_definition": "v2", "converged": true, "mode_gap_nats": NaN, "gap_second_nats": 4.927945695953895e-08, "n_within_tol": 16, "n_failed": 0, "map_total": -6.665370919133149, "noise_sd_raw": 169813.88764063042, "noise_over_sigma_c": 0.5435388216654942}}
- qnehvi_seconds: 9.3
- designs (MW per site ['110', '140', '146', '163', '270', '274']):
    - [0.000, 0.000, 0.000, 0.000, 0.000, 730.967]
    - [47.080, 0.000, 0.000, 56.312, 579.000, 0.000]
    - [28.089, 250.600, 0.000, 0.000, 579.000, 0.000]
    - [0.000, 250.600, 74.374, 185.400, 579.000, 746.400]
    - [67.126, 0.000, 0.000, 185.400, 579.000, 0.000]
    - [0.000, 250.600, 0.000, 185.400, 0.000, 746.400]
    - [18.141, 250.600, 227.762, 185.400, 579.000, 746.400]
    - [138.656, 250.600, 219.152, 185.400, 579.000, 746.400]
- realized Y (['V1', 'E1']):
    - [3.40092e+06, 8.09102e+09]
    - [3.6523e+06, 8.08728e+09]
    - [3.28734e+06, 8.09447e+09]
    - [1.56485e+06, 8.13101e+09]
    - [3.28695e+06, 8.08977e+09]
    - [2.57953e+06, 8.1094e+09]
    - [1.36634e+06, 8.14277e+09]
    - [1.20484e+06, 8.1564e+09]
<!-- END r2 -->

<!-- BEGIN r3 -->
## Round 3 (methods_E_EMU_committed_s1_s1_r3)
- proposed_at: "2026-11-24T08:35:15+00:00"
- wave: "methods_E_EMU_committed_s1_s1_r3"
- acq: "qnehvi"
- acq_seed: 20261109
- guardrail_mode: "constrain"
- settings: {"mc_samples": 128, "num_restarts": 20, "raw_samples": 512, "alpha": 0.0, "prune_baseline": true, "sequential": true, "fast_mode": false, "constraint": "shed <= 1.0 MWh (GP on the accumulated R1 column)", "guardrail_mode": "constrain", "seed": 20261109, "dtype": "float64", "bound_snaps": {"to_0": 9, "to_1": 0, "tol": 1e-12, "note": "bound cleanup after x * sx + mx; not lattice snapping"}}
- botorch: "0.16.1"
- bo_gp_sha: "60e6328236e745b3d34dc8cd704bb72888ae5d15"
- loo_rms_z: {"V1": 0.3507, "E1": 0.8362}
- noise_raw: {"V1": 16174.353354879186, "E1": 193457.32298956977}
- predictions: "waves/methods_E_EMU_committed_s1_s1_r3/predictions.csv"
- graded_at: "2026-11-24T08:35:16+00:00"
- n_train: 72
- n_hv: 71
- cumulative_hv: 146411038329552.2
- gain: 1802624881594.5625
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
- r2_max_mwh: 178.29063267172268
- calibration: {"V1": {"mean_z": 0.028, "rms_z": 0.157, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}, "E1": {"mean_z": 0.475, "rms_z": 0.942, "cov95": 7, "n_abs_z_gt3": 0, "transform": "std"}}
- C2_review: false
- C3_review: false
- halt: null
- decision: "graded (record_only)"
- fit_info: {"V1": {"fit_definition": "house"}, "E1": {"fit_definition": "v2", "converged": true, "mode_gap_nats": NaN, "gap_second_nats": 5.748951537043467e-09, "n_within_tol": 16, "n_failed": 0, "map_total": 13.525526333905255, "noise_sd_raw": 193457.3229895698, "noise_over_sigma_c": 0.6192165248748046}}
- qnehvi_seconds: 8.2
- designs (MW per site ['110', '140', '146', '163', '270', '274']):
    - [0.000, 0.000, 0.000, 185.400, 579.000, 479.236]
    - [0.000, 250.600, 0.000, 33.233, 579.000, 746.400]
    - [260.049, 0.000, 0.000, 185.400, 579.000, 0.000]
    - [0.000, 105.385, 0.000, 185.400, 579.000, 746.400]
    - [51.957, 250.600, 211.061, 185.400, 579.000, 746.400]
    - [338.600, 0.000, 0.000, 0.000, 0.000, 746.400]
    - [196.035, 250.600, 198.783, 184.458, 579.000, 746.400]
    - [0.000, 250.600, 211.167, 185.400, 579.000, 746.400]
- realized Y (['V1', 'E1']):
    - [2.39349e+06, 8.11274e+09]
    - [1.88275e+06, 8.12374e+09]
    - [2.86565e+06, 8.10205e+09]
    - [1.85961e+06, 8.12259e+09]
    - [1.32028e+06, 8.14661e+09]
    - [2.77448e+06, 8.10567e+09]
    - [1.16025e+06, 8.15996e+09]
    - [1.40911e+06, 8.14012e+09]
<!-- END r3 -->

<!-- BEGIN r4 -->
## Round 4 (methods_E_EMU_committed_s1_s1_r4)
- proposed_at: "2026-11-24T08:35:26+00:00"
- wave: "methods_E_EMU_committed_s1_s1_r4"
- acq: "qnehvi"
- acq_seed: 20261110
- guardrail_mode: "constrain"
- settings: {"mc_samples": 128, "num_restarts": 20, "raw_samples": 512, "alpha": 0.0, "prune_baseline": true, "sequential": true, "fast_mode": false, "constraint": "shed <= 1.0 MWh (GP on the accumulated R1 column)", "guardrail_mode": "constrain", "seed": 20261110, "dtype": "float64", "bound_snaps": {"to_0": 0, "to_1": 0, "tol": 1e-12, "note": "bound cleanup after x * sx + mx; not lattice snapping"}}
- botorch: "0.16.1"
- bo_gp_sha: "60e6328236e745b3d34dc8cd704bb72888ae5d15"
- loo_rms_z: {"V1": 0.3271, "E1": 0.8379}
- noise_raw: {"V1": 16398.599538934985, "E1": 231109.7746861824}
- predictions: "waves/methods_E_EMU_committed_s1_s1_r4/predictions.csv"
- graded_at: "2026-11-24T08:35:27+00:00"
- n_train: 80
- n_hv: 79
- cumulative_hv: 147323880310954.84
- gain: 912841981402.6562
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
- r2_max_mwh: 168.2000801723814
- calibration: {"V1": {"mean_z": 0.111, "rms_z": 0.277, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}, "E1": {"mean_z": 0.297, "rms_z": 1.172, "cov95": 7, "n_abs_z_gt3": 0, "transform": "std"}}
- C2_review: false
- C3_review: false
- halt: null
- decision: "graded (record_only)"
- fit_info: {"V1": {"fit_definition": "house"}, "E1": {"fit_definition": "v2", "converged": true, "mode_gap_nats": 19.63356894780179, "gap_second_nats": 7.271711766065891e-08, "n_within_tol": 15, "n_failed": 0, "map_total": 28.230434049435093, "noise_sd_raw": 231109.77468618235, "noise_over_sigma_c": 0.7397341663488877}}
- qnehvi_seconds: 10.1
- designs (MW per site ['110', '140', '146', '163', '270', '274']):
    - [117.118, 250.600, 200.839, 185.400, 579.000, 746.400]
    - [338.600, 159.927, 141.654, 185.400, 579.000, 746.400]
    - [338.600, 250.600, 74.350, 185.400, 579.000, 746.400]
    - [338.600, 0.000, 0.000, 185.400, 579.000, 746.400]
    - [129.296, 0.000, 0.000, 185.400, 579.000, 0.000]
    - [338.600, 0.000, 41.693, 71.845, 579.000, 746.400]
    - [166.517, 250.600, 206.173, 185.400, 579.000, 746.400]
    - [0.000, 250.600, 117.049, 185.400, 579.000, 746.400]
- realized Y (['V1', 'E1']):
    - [1.23624e+06, 8.15373e+09]
    - [1.18439e+06, 8.15923e+09]
    - [1.26948e+06, 8.15667e+09]
    - [1.64457e+06, 8.13382e+09]
    - [3.14651e+06, 8.09395e+09]
    - [1.63029e+06, 8.1367e+09]
    - [1.18325e+06, 8.15883e+09]
    - [1.50586e+06, 8.13398e+09]
<!-- END r4 -->
