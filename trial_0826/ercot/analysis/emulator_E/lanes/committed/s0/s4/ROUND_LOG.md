# methods_E arm qnehvi seed_id 4 — ROUND_LOG (prompt 55; acq = qnehvi, base = ['n0_E'] nav prefix n0 = 48, objectives = ['V1', 'E1'])

Ledger: `lanes/committed/s0/s4/ledger.json`. stop_rule = record_only: gain_k and
would_stop_k = (gain_k < tau) AND (gain_{k-1} < tau) are graded and logged under tau_joint
(headline) and tau_marginal (recorded) with the joint-vs-marginal sensitivity column; the
rule never halts; every lane runs to hard_cap = 4. tau_joint = 0, tau_marginal = 0 — ZERO: the stop rule is budget-cap-only and the cap governs (plan 3).
E-D5 OPEN: see README.md for the two readings of a fire. Halts ONLY per plan 1.2/1.3
(HALT_FOR_DECISION.md). Acquisition jobs never submit; Kay submits via submit_ready_E.sh.
Stop NOW: `touch lanes/committed/s0/s4/STOP` on the CRC clone, then qdel the lane's JIDs.

<!-- BEGIN r1 -->
## Round 1 (methods_E_EMU_committed_s0_s4_r1)
- proposed_at: "2026-11-24T08:36:29+00:00"
- wave: "methods_E_EMU_committed_s0_s4_r1"
- acq: "qnehvi"
- acq_seed: 20261407
- guardrail_mode: "monitor"
- settings: {"mc_samples": 128, "num_restarts": 20, "raw_samples": 512, "alpha": 0.0, "prune_baseline": true, "sequential": true, "fast_mode": false, "constraint": "none", "guardrail_mode": "monitor", "seed": 20261407, "dtype": "float64", "bound_snaps": {"to_0": 0, "to_1": 0, "tol": 1e-12, "note": "bound cleanup after x * sx + mx; not lattice snapping"}}
- botorch: "0.16.1"
- bo_gp_sha: "60e6328236e745b3d34dc8cd704bb72888ae5d15"
- loo_rms_z: {"V1": 0.4268, "E1": 0.8267}
- noise_raw: {"V1": 14949.051609849952, "E1": 174965.13916944584}
- predictions: "waves/methods_E_EMU_committed_s0_s4_r1/predictions.csv"
- graded_at: "2026-11-24T08:36:29+00:00"
- n_train: 56
- n_hv: 56
- cumulative_hv: 141005103627547.0
- gain: 40481828227327.266
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
- r2_max_mwh: 181.65062769595872
- calibration: {"V1": {"mean_z": -0.004, "rms_z": 0.146, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}, "E1": {"mean_z": 0.082, "rms_z": 0.192, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}}
- C2_review: false
- C3_review: false
- halt: null
- decision: "graded (record_only)"
- fit_info: {"V1": {"fit_definition": "house"}, "E1": {"fit_definition": "v2", "converged": true, "mode_gap_nats": 53.68406410300448, "gap_second_nats": 2.884701544303425e-07, "n_within_tol": 13, "n_failed": 0, "map_total": -19.200766147217088, "noise_sd_raw": 174965.1391694458, "noise_over_sigma_c": 0.5600269029701294}}
- qnehvi_seconds: 6.6
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
    - [3.0005e+06, 8.09864e+09]
    - [2.17351e+06, 8.11474e+09]
    - [3.43905e+06, 8.08535e+09]
    - [1.4536e+06, 8.13683e+09]
    - [2.71723e+06, 8.10476e+09]
    - [1.71383e+06, 8.12561e+09]
    - [1.28377e+06, 8.15027e+09]
    - [2.9795e+06, 8.09932e+09]
<!-- END r1 -->

<!-- BEGIN r2 -->
## Round 2 (methods_E_EMU_committed_s0_s4_r2)
- proposed_at: "2026-11-24T08:36:37+00:00"
- wave: "methods_E_EMU_committed_s0_s4_r2"
- acq: "qnehvi"
- acq_seed: 20261408
- guardrail_mode: "monitor"
- settings: {"mc_samples": 128, "num_restarts": 20, "raw_samples": 512, "alpha": 0.0, "prune_baseline": true, "sequential": true, "fast_mode": false, "constraint": "none", "guardrail_mode": "monitor", "seed": 20261408, "dtype": "float64", "bound_snaps": {"to_0": 0, "to_1": 0, "tol": 1e-12, "note": "bound cleanup after x * sx + mx; not lattice snapping"}}
- botorch: "0.16.1"
- bo_gp_sha: "60e6328236e745b3d34dc8cd704bb72888ae5d15"
- loo_rms_z: {"V1": 0.3638, "E1": 0.7837}
- noise_raw: {"V1": 14914.996861570015, "E1": 169778.3795008826}
- predictions: "waves/methods_E_EMU_committed_s0_s4_r2/predictions.csv"
- graded_at: "2026-11-24T08:36:37+00:00"
- n_train: 64
- n_hv: 64
- cumulative_hv: 146786354084192.62
- gain: 5781250456645.625
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
- r2_max_mwh: 177.7528268523339
- calibration: {"V1": {"mean_z": 0.029, "rms_z": 0.244, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}, "E1": {"mean_z": -0.108, "rms_z": 0.755, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}}
- C2_review: false
- C3_review: false
- halt: null
- decision: "graded (record_only)"
- fit_info: {"V1": {"fit_definition": "house"}, "E1": {"fit_definition": "v2", "converged": true, "mode_gap_nats": NaN, "gap_second_nats": 8.523636907398213e-09, "n_within_tol": 16, "n_failed": 0, "map_total": -5.782368947496829, "noise_sd_raw": 169778.37950088258, "noise_over_sigma_c": 0.5434251675191448}}
- qnehvi_seconds: 6.4
- designs (MW per site ['110', '140', '146', '163', '270', '274']):
    - [0.000, 250.600, 0.000, 0.000, 579.000, 746.400]
    - [0.000, 0.000, 0.000, 185.400, 579.000, 444.516]
    - [0.000, 92.557, 0.000, 185.400, 579.000, 0.000]
    - [0.000, 0.000, 0.000, 185.400, 579.000, 746.400]
    - [0.000, 250.600, 74.412, 185.400, 579.000, 746.400]
    - [23.998, 250.600, 212.941, 185.400, 579.000, 746.400]
    - [149.301, 250.600, 203.244, 184.602, 579.000, 746.400]
    - [0.000, 0.000, 0.000, 185.400, 579.000, 524.291]
- realized Y (['V1', 'E1']):
    - [1.96016e+06, 8.12189e+09]
    - [2.44845e+06, 8.11171e+09]
    - [3.26115e+06, 8.0915e+09]
    - [2.04359e+06, 8.11708e+09]
    - [1.57829e+06, 8.13047e+09]
    - [1.36165e+06, 8.14353e+09]
    - [1.19785e+06, 8.15726e+09]
    - [2.31448e+06, 8.11294e+09]
<!-- END r2 -->

<!-- BEGIN r3 -->
## Round 3 (methods_E_EMU_committed_s0_s4_r3)
- proposed_at: "2026-11-24T08:36:44+00:00"
- wave: "methods_E_EMU_committed_s0_s4_r3"
- acq: "qnehvi"
- acq_seed: 20261409
- guardrail_mode: "monitor"
- settings: {"mc_samples": 128, "num_restarts": 20, "raw_samples": 512, "alpha": 0.0, "prune_baseline": true, "sequential": true, "fast_mode": false, "constraint": "none", "guardrail_mode": "monitor", "seed": 20261409, "dtype": "float64", "bound_snaps": {"to_0": 0, "to_1": 0, "tol": 1e-12, "note": "bound cleanup after x * sx + mx; not lattice snapping"}}
- botorch: "0.16.1"
- bo_gp_sha: "60e6328236e745b3d34dc8cd704bb72888ae5d15"
- loo_rms_z: {"V1": 0.3533, "E1": 0.8494}
- noise_raw: {"V1": 15493.884597915983, "E1": 158912.24820112297}
- predictions: "waves/methods_E_EMU_committed_s0_s4_r3/predictions.csv"
- graded_at: "2026-11-24T08:36:45+00:00"
- n_train: 72
- n_hv: 72
- cumulative_hv: 148141758016877.2
- gain: 1355403932684.5625
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
- r2_max_mwh: 221.42421155113038
- calibration: {"V1": {"mean_z": -0.186, "rms_z": 0.216, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}, "E1": {"mean_z": -0.54, "rms_z": 1.249, "cov95": 7, "n_abs_z_gt3": 1, "transform": "std"}}
- C2_review: false
- C3_review: false
- halt: null
- decision: "graded (record_only)"
- fit_info: {"V1": {"fit_definition": "house"}, "E1": {"fit_definition": "v2", "converged": true, "mode_gap_nats": NaN, "gap_second_nats": 4.1839165021428926e-08, "n_within_tol": 16, "n_failed": 0, "map_total": 10.549841586384769, "noise_sd_raw": 158912.248201123, "noise_over_sigma_c": 0.5086449485111869}}
- qnehvi_seconds: 6.2
- designs (MW per site ['110', '140', '146', '163', '270', '274']):
    - [338.600, 0.000, 0.000, 0.000, 0.000, 746.400]
    - [338.600, 0.000, 0.000, 92.899, 0.000, 746.400]
    - [0.000, 0.000, 0.000, 106.898, 0.000, 746.400]
    - [0.000, 105.264, 0.000, 185.400, 579.000, 746.400]
    - [64.986, 250.600, 189.404, 185.400, 579.000, 746.400]
    - [0.000, 250.600, 0.000, 185.400, 0.000, 746.400]
    - [0.000, 159.223, 0.000, 185.400, 579.000, 746.400]
    - [183.122, 250.600, 201.274, 177.908, 579.000, 746.400]
- realized Y (['V1', 'E1']):
    - [2.77045e+06, 8.10581e+09]
    - [2.59019e+06, 8.11118e+09]
    - [3.14383e+06, 8.09635e+09]
    - [1.85525e+06, 8.12247e+09]
    - [1.31694e+06, 8.1468e+09]
    - [2.58535e+06, 8.10887e+09]
    - [1.78923e+06, 8.12436e+09]
    - [1.16608e+06, 8.15916e+09]
<!-- END r3 -->

<!-- BEGIN r4 -->
## Round 4 (methods_E_EMU_committed_s0_s4_r4)
- proposed_at: "2026-11-24T08:36:54+00:00"
- wave: "methods_E_EMU_committed_s0_s4_r4"
- acq: "qnehvi"
- acq_seed: 20261410
- guardrail_mode: "monitor"
- settings: {"mc_samples": 128, "num_restarts": 20, "raw_samples": 512, "alpha": 0.0, "prune_baseline": true, "sequential": true, "fast_mode": false, "constraint": "none", "guardrail_mode": "monitor", "seed": 20261410, "dtype": "float64", "bound_snaps": {"to_0": 0, "to_1": 0, "tol": 1e-12, "note": "bound cleanup after x * sx + mx; not lattice snapping"}}
- botorch: "0.16.1"
- bo_gp_sha: "60e6328236e745b3d34dc8cd704bb72888ae5d15"
- loo_rms_z: {"V1": 0.3395, "E1": 0.8755}
- noise_raw: {"V1": 15742.614330138955, "E1": 246692.0630070503}
- predictions: "waves/methods_E_EMU_committed_s0_s4_r4/predictions.csv"
- graded_at: "2026-11-24T08:36:55+00:00"
- n_train: 80
- n_hv: 80
- cumulative_hv: 149618078968402.2
- gain: 1476320951525.0
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
- r2_max_mwh: 190.12407324796757
- calibration: {"V1": {"mean_z": 0.047, "rms_z": 0.218, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}, "E1": {"mean_z": -0.418, "rms_z": 1.228, "cov95": 7, "n_abs_z_gt3": 1, "transform": "std"}}
- C2_review: false
- C3_review: false
- halt: null
- decision: "graded (record_only)"
- fit_info: {"V1": {"fit_definition": "house"}, "E1": {"fit_definition": "v2", "converged": true, "mode_gap_nats": NaN, "gap_second_nats": 2.0894844965368975e-08, "n_within_tol": 16, "n_failed": 0, "map_total": 22.977044245834012, "noise_sd_raw": 246692.0630070503, "noise_over_sigma_c": 0.7896098199273532}}
- qnehvi_seconds: 8.3
- designs (MW per site ['110', '140', '146', '163', '270', '274']):
    - [0.000, 250.600, 36.429, 185.400, 579.000, 746.400]
    - [0.000, 0.000, 0.000, 42.737, 579.000, 0.000]
    - [0.000, 0.000, 0.000, 185.400, 47.339, 746.400]
    - [0.000, 250.600, 0.000, 0.000, 579.000, 0.000]
    - [116.280, 0.000, 0.000, 185.400, 579.000, 0.000]
    - [338.600, 196.310, 86.890, 185.400, 579.000, 746.400]
    - [338.600, 250.600, 138.937, 146.951, 579.000, 746.400]
    - [119.761, 250.600, 194.096, 178.747, 579.000, 746.400]
- realized Y (['V1', 'E1']):
    - [1.63983e+06, 8.12785e+09]
    - [3.79614e+06, 8.08234e+09]
    - [2.89509e+06, 8.1023e+09]
    - [3.34748e+06, 8.09228e+09]
    - [3.17532e+06, 8.09295e+09]
    - [1.25366e+06, 8.15695e+09]
    - [1.15482e+06, 8.16236e+09]
    - [1.23856e+06, 8.15238e+09]
<!-- END r4 -->
