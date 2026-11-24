# methods_E arm qnehvi seed_id 0 — ROUND_LOG (prompt 55; acq = qnehvi, base = ['n0_E'] nav prefix n0 = 48, objectives = ['V1', 'E1'])

Ledger: `lanes/long/s0/s0/ledger.json`. stop_rule = record_only: gain_k and
would_stop_k = (gain_k < tau) AND (gain_{k-1} < tau) are graded and logged under tau_joint
(headline) and tau_marginal (recorded) with the joint-vs-marginal sensitivity column; the
rule never halts; every lane runs to hard_cap = 4. tau_joint = 0, tau_marginal = 0 — ZERO: the stop rule is budget-cap-only and the cap governs (plan 3).
E-D5 OPEN: see README.md for the two readings of a fire. Halts ONLY per plan 1.2/1.3
(HALT_FOR_DECISION.md). Acquisition jobs never submit; Kay submits via submit_ready_E.sh.
Stop NOW: `touch lanes/long/s0/s0/STOP` on the CRC clone, then qdel the lane's JIDs.

<!-- BEGIN r1 -->
## Round 1 (methods_E_EMU_long_s0_s0_r1)
- proposed_at: "2026-11-24T08:04:49+00:00"
- wave: "methods_E_EMU_long_s0_s0_r1"
- acq: "qnehvi"
- acq_seed: 20261007
- guardrail_mode: "monitor"
- settings: {"mc_samples": 128, "num_restarts": 20, "raw_samples": 512, "alpha": 0.0, "prune_baseline": true, "sequential": true, "fast_mode": false, "constraint": "none", "guardrail_mode": "monitor", "seed": 20261007, "dtype": "float64", "bound_snaps": {"to_0": 0, "to_1": 0, "tol": 1e-12, "note": "bound cleanup after x * sx + mx; not lattice snapping"}}
- botorch: "0.16.1"
- bo_gp_sha: "60e6328236e745b3d34dc8cd704bb72888ae5d15"
- loo_rms_z: {"V1": 0.884, "E1": 0.9256}
- noise_raw: {"V1": 2688.0197417641402, "E1": 18371.00353167308}
- predictions: "waves/methods_E_EMU_long_s0_s0_r1/predictions.csv"
- graded_at: "2026-11-24T08:04:50+00:00"
- n_train: 56
- n_hv: 56
- cumulative_hv: 131252288571960.22
- gain: 31040361523428.75
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
- r2_max_mwh: 164.99459180005692
- calibration: {"V1": {"mean_z": 0.591, "rms_z": 2.677, "cov95": 5, "n_abs_z_gt3": 2, "transform": "std"}, "E1": {"mean_z": 0.649, "rms_z": 1.17, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}}
- C2_review: false
- C3_review: false
- halt: null
- decision: "graded (record_only)"
- qnehvi_seconds: 36.1
- r1_shared_designs_with_seed: {}
- designs (MW per site ['110', '140', '146', '163', '270', '274']):
    - [338.600, 0.000, 0.000, 185.400, 579.000, 0.000]
    - [19.902, 0.000, 0.000, 185.400, 579.000, 0.000]
    - [338.600, 0.000, 0.000, 185.400, 579.000, 746.400]
    - [0.000, 0.000, 0.000, 185.400, 579.000, 710.728]
    - [338.600, 250.600, 0.000, 185.400, 579.000, 736.718]
    - [0.000, 0.000, 0.000, 185.400, 0.000, 746.400]
    - [0.000, 250.600, 0.000, 185.400, 579.000, 746.400]
    - [0.000, 0.000, 0.000, 185.400, 579.000, 482.001]
- realized Y (['V1', 'E1']):
    - [2.71743e+06, 8.10887e+09]
    - [3.39519e+06, 8.09325e+09]
    - [1.64633e+06, 8.1312e+09]
    - [2.06753e+06, 8.11768e+09]
    - [1.42252e+06, 8.14369e+09]
    - [3.00051e+06, 8.10401e+09]
    - [1.7091e+06, 8.12537e+09]
    - [2.38472e+06, 8.11496e+09]
<!-- END r1 -->

<!-- BEGIN r2 -->
## Round 2 (methods_E_EMU_long_s0_s0_r2)
- proposed_at: "2026-11-24T08:05:25+00:00"
- wave: "methods_E_EMU_long_s0_s0_r2"
- acq: "qnehvi"
- acq_seed: 20261008
- guardrail_mode: "monitor"
- settings: {"mc_samples": 128, "num_restarts": 20, "raw_samples": 512, "alpha": 0.0, "prune_baseline": true, "sequential": true, "fast_mode": false, "constraint": "none", "guardrail_mode": "monitor", "seed": 20261008, "dtype": "float64", "bound_snaps": {"to_0": 2, "to_1": 0, "tol": 1e-12, "note": "bound cleanup after x * sx + mx; not lattice snapping"}}
- botorch: "0.16.1"
- bo_gp_sha: "60e6328236e745b3d34dc8cd704bb72888ae5d15"
- loo_rms_z: {"V1": 0.8905, "E1": 0.9013}
- noise_raw: {"V1": 128.72096535574946, "E1": 18309.677942305072}
- predictions: "waves/methods_E_EMU_long_s0_s0_r2/predictions.csv"
- graded_at: "2026-11-24T08:05:26+00:00"
- n_train: 64
- n_hv: 64
- cumulative_hv: 138063118761417.39
- gain: 6810830189457.172
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
- r2_max_mwh: 177.22320354771864
- calibration: {"V1": {"mean_z": 0.701, "rms_z": 1.221, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}, "E1": {"mean_z": -0.18, "rms_z": 0.749, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}}
- C2_review: false
- C3_review: false
- halt: null
- decision: "graded (record_only)"
- qnehvi_seconds: 34.4
- designs (MW per site ['110', '140', '146', '163', '270', '274']):
    - [45.326, 250.600, 268.000, 185.400, 579.000, 746.400]
    - [0.000, 250.600, 131.053, 185.400, 579.000, 746.400]
    - [109.726, 0.000, 0.000, 185.400, 579.000, 0.000]
    - [338.600, 0.000, 0.000, 0.000, 0.000, 746.400]
    - [0.000, 250.600, 0.000, 0.000, 579.000, 0.000]
    - [124.673, 250.600, 268.000, 185.400, 579.000, 746.400]
    - [0.000, 250.600, 236.776, 185.400, 579.000, 746.400]
    - [0.000, 64.151, 0.000, 185.400, 579.000, 746.400]
- realized Y (['V1', 'E1']):
    - [1.3073e+06, 8.1466e+09]
    - [1.48574e+06, 8.13526e+09]
    - [3.19564e+06, 8.09717e+09]
    - [2.77276e+06, 8.10947e+09]
    - [3.35247e+06, 8.10047e+09]
    - [1.19186e+06, 8.15364e+09]
    - [1.39011e+06, 8.14165e+09]
    - [1.92004e+06, 8.12081e+09]
<!-- END r2 -->

<!-- BEGIN r3 -->
## Round 3 (methods_E_EMU_long_s0_s0_r3)
- proposed_at: "2026-11-24T08:06:01+00:00"
- wave: "methods_E_EMU_long_s0_s0_r3"
- acq: "qnehvi"
- acq_seed: 20261009
- guardrail_mode: "monitor"
- settings: {"mc_samples": 128, "num_restarts": 20, "raw_samples": 512, "alpha": 0.0, "prune_baseline": true, "sequential": true, "fast_mode": false, "constraint": "none", "guardrail_mode": "monitor", "seed": 20261009, "dtype": "float64", "bound_snaps": {"to_0": 0, "to_1": 0, "tol": 1e-12, "note": "bound cleanup after x * sx + mx; not lattice snapping"}}
- botorch: "0.16.1"
- bo_gp_sha: "60e6328236e745b3d34dc8cd704bb72888ae5d15"
- loo_rms_z: {"V1": 0.9512, "E1": 0.9172}
- noise_raw: {"V1": 1730.513235670433, "E1": 255964.25376742566}
- predictions: "waves/methods_E_EMU_long_s0_s0_r3/predictions.csv"
- graded_at: "2026-11-24T08:06:01+00:00"
- n_train: 72
- n_hv: 72
- cumulative_hv: 140137559292477.75
- gain: 2074440531060.3594
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
- r2_max_mwh: 189.22955820006348
- calibration: {"V1": {"mean_z": -0.301, "rms_z": 0.949, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}, "E1": {"mean_z": 0.947, "rms_z": 1.379, "cov95": 7, "n_abs_z_gt3": 1, "transform": "std"}}
- C2_review: false
- C3_review: false
- halt: null
- decision: "graded (record_only)"
- qnehvi_seconds: 33.6
- designs (MW per site ['110', '140', '146', '163', '270', '274']):
    - [0.000, 0.000, 0.000, 75.407, 579.000, 0.000]
    - [233.575, 250.600, 211.290, 185.400, 579.000, 746.400]
    - [262.919, 0.000, 0.000, 185.400, 579.000, 0.000]
    - [130.696, 250.600, 184.368, 185.400, 579.000, 746.400]
    - [0.000, 250.600, 0.000, 0.000, 0.000, 746.400]
    - [191.265, 250.600, 0.000, 185.400, 579.000, 0.000]
    - [0.000, 250.600, 0.000, 185.400, 0.000, 746.400]
    - [172.209, 0.000, 0.000, 185.400, 579.000, 0.000]
- realized Y (['V1', 'E1']):
    - [3.71118e+06, 8.09088e+09]
    - [1.12269e+06, 8.15949e+09]
    - [2.86131e+06, 8.10587e+09]
    - [1.23681e+06, 8.15181e+09]
    - [2.90132e+06, 8.11109e+09]
    - [2.5915e+06, 8.11449e+09]
    - [2.58502e+06, 8.11412e+09]
    - [3.05157e+06, 8.10059e+09]
<!-- END r3 -->

<!-- BEGIN r4 -->
## Round 4 (methods_E_EMU_long_s0_s0_r4)
- proposed_at: "2026-11-24T08:06:40+00:00"
- wave: "methods_E_EMU_long_s0_s0_r4"
- acq: "qnehvi"
- acq_seed: 20261010
- guardrail_mode: "monitor"
- settings: {"mc_samples": 128, "num_restarts": 20, "raw_samples": 512, "alpha": 0.0, "prune_baseline": true, "sequential": true, "fast_mode": false, "constraint": "none", "guardrail_mode": "monitor", "seed": 20261010, "dtype": "float64", "bound_snaps": {"to_0": 0, "to_1": 0, "tol": 1e-12, "note": "bound cleanup after x * sx + mx; not lattice snapping"}}
- botorch: "0.16.1"
- bo_gp_sha: "60e6328236e745b3d34dc8cd704bb72888ae5d15"
- loo_rms_z: {"V1": 0.8705, "E1": 0.939}
- noise_raw: {"V1": 2067.8153828250315, "E1": 158754.7759629556}
- predictions: "waves/methods_E_EMU_long_s0_s0_r4/predictions.csv"
- graded_at: "2026-11-24T08:06:41+00:00"
- n_train: 80
- n_hv: 80
- cumulative_hv: 141227700821692.75
- gain: 1090141529215.0
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
- r2_max_mwh: 199.9066945586215
- calibration: {"V1": {"mean_z": 0.365, "rms_z": 0.923, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}, "E1": {"mean_z": -0.47, "rms_z": 1.264, "cov95": 7, "n_abs_z_gt3": 0, "transform": "std"}}
- C2_review: false
- C3_review: false
- halt: null
- decision: "graded (record_only)"
- qnehvi_seconds: 37.3
- designs (MW per site ['110', '140', '146', '163', '270', '274']):
    - [0.000, 0.000, 0.000, 185.400, 211.851, 746.400]
    - [0.000, 250.600, 61.696, 185.400, 579.000, 746.400]
    - [0.000, 0.000, 0.000, 0.000, 579.000, 746.400]
    - [0.000, 21.362, 0.000, 185.400, 579.000, 746.400]
    - [338.600, 0.000, 0.000, 185.400, 0.000, 746.400]
    - [7.218, 250.600, 163.363, 185.400, 579.000, 746.400]
    - [338.600, 0.000, 0.000, 185.400, 65.673, 746.400]
    - [162.864, 250.600, 268.000, 185.400, 579.000, 746.400]
- realized Y (['V1', 'E1']):
    - [2.55322e+06, 8.1129e+09]
    - [1.59476e+06, 8.12977e+09]
    - [2.33578e+06, 8.11718e+09]
    - [1.99891e+06, 8.11847e+09]
    - [2.45905e+06, 8.11574e+09]
    - [1.43511e+06, 8.13778e+09]
    - [2.33089e+06, 8.11984e+09]
    - [1.14714e+06, 8.15704e+09]
<!-- END r4 -->
