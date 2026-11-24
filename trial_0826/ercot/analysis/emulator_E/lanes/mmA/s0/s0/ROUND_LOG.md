# methods_E arm qnehvi seed_id 0 — ROUND_LOG (prompt 55; acq = qnehvi, base = ['n0_E'] nav prefix n0 = 48, objectives = ['V1', 'E1'])

Ledger: `lanes/mmA/s0/s0/ledger.json`. stop_rule = record_only: gain_k and
would_stop_k = (gain_k < tau) AND (gain_{k-1} < tau) are graded and logged under tau_joint
(headline) and tau_marginal (recorded) with the joint-vs-marginal sensitivity column; the
rule never halts; every lane runs to hard_cap = 4. tau_joint = 0, tau_marginal = 0 — ZERO: the stop rule is budget-cap-only and the cap governs (plan 3).
E-D5 OPEN: see README.md for the two readings of a fire. Halts ONLY per plan 1.2/1.3
(HALT_FOR_DECISION.md). Acquisition jobs never submit; Kay submits via submit_ready_E.sh.
Stop NOW: `touch lanes/mmA/s0/s0/STOP` on the CRC clone, then qdel the lane's JIDs.

<!-- BEGIN r1 -->
## Round 1 (methods_E_EMU_mmA_s0_s0_r1)
- proposed_at: "2026-11-24T08:34:11+00:00"
- wave: "methods_E_EMU_mmA_s0_s0_r1"
- acq: "qnehvi"
- acq_seed: 20261007
- guardrail_mode: "monitor"
- settings: {"mc_samples": 128, "num_restarts": 20, "raw_samples": 512, "alpha": 0.0, "prune_baseline": true, "sequential": true, "fast_mode": false, "constraint": "none", "guardrail_mode": "monitor", "seed": 20261007, "dtype": "float64", "bound_snaps": {"to_0": 0, "to_1": 0, "tol": 1e-12, "note": "bound cleanup after x * sx + mx; not lattice snapping"}}
- botorch: "0.16.1"
- bo_gp_sha: "60e6328236e745b3d34dc8cd704bb72888ae5d15"
- loo_rms_z: {"V1": 0.4268, "E1": 0.868}
- noise_raw: {"V1": 14949.051609849952, "E1": 178124.16366543318}
- predictions: "waves/methods_E_EMU_mmA_s0_s0_r1/predictions.csv"
- graded_at: "2026-11-24T08:34:12+00:00"
- n_train: 56
- n_hv: 56
- cumulative_hv: 134163383190115.84
- gain: 33951456141584.375
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
- r2_max_mwh: 173.89881120608132
- calibration: {"V1": {"mean_z": 0.002, "rms_z": 0.166, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}, "E1": {"mean_z": 0.543, "rms_z": 0.907, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}}
- C2_review: false
- C3_review: false
- halt: null
- decision: "graded (record_only)"
- fit_info: {"V1": {"fit_definition": "house"}, "E1": {"fit_definition": "v2", "converged": true, "mode_gap_nats": 54.871620355150625, "gap_second_nats": 1.22345330311191e-07, "n_within_tol": 11, "n_failed": 0, "map_total": -17.358398993603036, "noise_sd_raw": 178124.1636654332, "noise_over_sigma_c": 0.5701382812326372}}
- qnehvi_seconds: 8.3
- r1_shared_designs_with_seed: {}
- designs (MW per site ['110', '140', '146', '163', '270', '274']):
    - [0.000, 0.000, 0.000, 185.400, 0.000, 746.400]
    - [0.000, 0.000, 0.000, 185.400, 579.000, 0.000]
    - [0.000, 0.000, 0.000, 185.400, 579.000, 618.943]
    - [0.000, 250.600, 162.026, 185.400, 579.000, 746.400]
    - [338.600, 0.000, 0.000, 185.400, 579.000, 0.000]
    - [0.000, 250.600, 0.000, 185.400, 579.000, 746.400]
    - [88.715, 250.600, 202.460, 185.400, 579.000, 746.400]
    - [0.000, 16.521, 0.000, 185.400, 579.000, 746.400]
- realized Y (['V1', 'E1']):
    - [2.99815e+06, 8.10464e+09]
    - [3.43176e+06, 8.09126e+09]
    - [2.17668e+06, 8.11692e+09]
    - [1.45362e+06, 8.13706e+09]
    - [2.71933e+06, 8.10913e+09]
    - [1.70536e+06, 8.12568e+09]
    - [1.28074e+06, 8.14858e+09]
    - [2.00936e+06, 8.11905e+09]
<!-- END r1 -->

<!-- BEGIN r2 -->
## Round 2 (methods_E_EMU_mmA_s0_s0_r2)
- proposed_at: "2026-11-24T08:34:20+00:00"
- wave: "methods_E_EMU_mmA_s0_s0_r2"
- acq: "qnehvi"
- acq_seed: 20261008
- guardrail_mode: "monitor"
- settings: {"mc_samples": 128, "num_restarts": 20, "raw_samples": 512, "alpha": 0.0, "prune_baseline": true, "sequential": true, "fast_mode": false, "constraint": "none", "guardrail_mode": "monitor", "seed": 20261008, "dtype": "float64", "bound_snaps": {"to_0": 4, "to_1": 0, "tol": 1e-12, "note": "bound cleanup after x * sx + mx; not lattice snapping"}}
- botorch: "0.16.1"
- bo_gp_sha: "60e6328236e745b3d34dc8cd704bb72888ae5d15"
- loo_rms_z: {"V1": 0.371, "E1": 0.8715}
- noise_raw: {"V1": 14950.703342010018, "E1": 175890.42495046317}
- predictions: "waves/methods_E_EMU_mmA_s0_s0_r2/predictions.csv"
- graded_at: "2026-11-24T08:34:21+00:00"
- n_train: 64
- n_hv: 64
- cumulative_hv: 138866894874037.78
- gain: 4703511683921.9375
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
- r2_max_mwh: 193.33466091459928
- calibration: {"V1": {"mean_z": -0.019, "rms_z": 0.221, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}, "E1": {"mean_z": 0.23, "rms_z": 0.649, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}}
- C2_review: false
- C3_review: false
- halt: null
- decision: "graded (record_only)"
- fit_info: {"V1": {"fit_definition": "house"}, "E1": {"fit_definition": "v2", "converged": true, "mode_gap_nats": NaN, "gap_second_nats": 7.355783893103762e-08, "n_within_tol": 16, "n_failed": 0, "map_total": -9.40280398974468, "noise_sd_raw": 175890.4249504632, "noise_over_sigma_c": 0.5629885496888144}}
- qnehvi_seconds: 6.7
- designs (MW per site ['110', '140', '146', '163', '270', '274']):
    - [0.000, 250.600, 0.000, 185.400, 579.000, 0.000]
    - [0.000, 0.000, 0.000, 185.400, 579.000, 77.111]
    - [0.000, 250.600, 74.176, 185.400, 579.000, 746.400]
    - [183.542, 250.600, 189.495, 185.400, 579.000, 746.400]
    - [0.000, 0.000, 0.000, 185.400, 579.000, 435.732]
    - [46.499, 250.600, 175.267, 185.400, 579.000, 746.400]
    - [0.000, 0.000, 0.000, 185.400, 455.547, 0.000]
    - [338.600, 0.000, 0.000, 0.000, 0.000, 746.400]
- realized Y (['V1', 'E1']):
    - [2.97907e+06, 8.10491e+09]
    - [3.26109e+06, 8.09643e+09]
    - [1.57133e+06, 8.13101e+09]
    - [1.16869e+06, 8.15595e+09]
    - [2.46668e+06, 8.11336e+09]
    - [1.36523e+06, 8.14313e+09]
    - [3.68375e+06, 8.09073e+09]
    - [2.77437e+06, 8.11002e+09]
<!-- END r2 -->

<!-- BEGIN r3 -->
## Round 3 (methods_E_EMU_mmA_s0_s0_r3)
- proposed_at: "2026-11-24T08:34:29+00:00"
- wave: "methods_E_EMU_mmA_s0_s0_r3"
- acq: "qnehvi"
- acq_seed: 20261009
- guardrail_mode: "monitor"
- settings: {"mc_samples": 128, "num_restarts": 20, "raw_samples": 512, "alpha": 0.0, "prune_baseline": true, "sequential": true, "fast_mode": false, "constraint": "none", "guardrail_mode": "monitor", "seed": 20261009, "dtype": "float64", "bound_snaps": {"to_0": 6, "to_1": 0, "tol": 1e-12, "note": "bound cleanup after x * sx + mx; not lattice snapping"}}
- botorch: "0.16.1"
- bo_gp_sha: "60e6328236e745b3d34dc8cd704bb72888ae5d15"
- loo_rms_z: {"V1": 0.3506, "E1": 0.896}
- noise_raw: {"V1": 16083.466622797057, "E1": 201298.83664586776}
- predictions: "waves/methods_E_EMU_mmA_s0_s0_r3/predictions.csv"
- graded_at: "2026-11-24T08:34:29+00:00"
- n_train: 72
- n_hv: 72
- cumulative_hv: 140959455926546.8
- gain: 2092561052509.0312
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
- r2_max_mwh: 166.0360887064597
- calibration: {"V1": {"mean_z": 0.069, "rms_z": 0.204, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}, "E1": {"mean_z": -0.121, "rms_z": 0.79, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}}
- C2_review: false
- C3_review: false
- halt: null
- decision: "graded (record_only)"
- fit_info: {"V1": {"fit_definition": "house"}, "E1": {"fit_definition": "v2", "converged": true, "mode_gap_nats": NaN, "gap_second_nats": 1.0193907939992641e-09, "n_within_tol": 16, "n_failed": 0, "map_total": 7.81953143448882, "noise_sd_raw": 201298.8366458678, "noise_over_sigma_c": 0.6443155739104048}}
- qnehvi_seconds: 7.1
- designs (MW per site ['110', '140', '146', '163', '270', '274']):
    - [0.000, 0.000, 0.000, 55.538, 579.000, 0.000]
    - [104.213, 250.600, 0.000, 0.000, 579.000, 0.000]
    - [154.785, 0.000, 0.000, 185.400, 579.000, 0.000]
    - [265.211, 0.000, 0.000, 185.400, 579.000, 0.000]
    - [0.000, 97.043, 0.000, 185.400, 579.000, 746.400]
    - [0.000, 0.000, 0.000, 0.000, 579.000, 746.400]
    - [236.647, 250.600, 194.587, 185.400, 579.000, 746.400]
    - [144.502, 250.600, 178.609, 185.400, 579.000, 746.400]
- realized Y (['V1', 'E1']):
    - [3.75897e+06, 8.0911e+09]
    - [3.12996e+06, 8.10515e+09]
    - [3.09167e+06, 8.10013e+09]
    - [2.85546e+06, 8.10523e+09]
    - [1.87094e+06, 8.1221e+09]
    - [2.33258e+06, 8.11706e+09]
    - [1.13565e+06, 8.15896e+09]
    - [1.22875e+06, 8.15226e+09]
<!-- END r3 -->

<!-- BEGIN r4 -->
## Round 4 (methods_E_EMU_mmA_s0_s0_r4)
- proposed_at: "2026-11-24T08:34:39+00:00"
- wave: "methods_E_EMU_mmA_s0_s0_r4"
- acq: "qnehvi"
- acq_seed: 20261010
- guardrail_mode: "monitor"
- settings: {"mc_samples": 128, "num_restarts": 20, "raw_samples": 512, "alpha": 0.0, "prune_baseline": true, "sequential": true, "fast_mode": false, "constraint": "none", "guardrail_mode": "monitor", "seed": 20261010, "dtype": "float64", "bound_snaps": {"to_0": 0, "to_1": 0, "tol": 1e-12, "note": "bound cleanup after x * sx + mx; not lattice snapping"}}
- botorch: "0.16.1"
- bo_gp_sha: "60e6328236e745b3d34dc8cd704bb72888ae5d15"
- loo_rms_z: {"V1": 0.3177, "E1": 0.9625}
- noise_raw: {"V1": 16550.111513537755, "E1": 207651.10806271687}
- predictions: "waves/methods_E_EMU_mmA_s0_s0_r4/predictions.csv"
- graded_at: "2026-11-24T08:34:39+00:00"
- n_train: 80
- n_hv: 80
- cumulative_hv: 141612439681831.8
- gain: 652983755285.0
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
- r2_max_mwh: 175.74413915446718
- calibration: {"V1": {"mean_z": -0.111, "rms_z": 0.23, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}, "E1": {"mean_z": 0.089, "rms_z": 0.797, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}}
- C2_review: false
- C3_review: false
- halt: null
- decision: "graded (record_only)"
- fit_info: {"V1": {"fit_definition": "house"}, "E1": {"fit_definition": "v2", "converged": true, "mode_gap_nats": 88.98890296110872, "gap_second_nats": 1.6764008847758305e-08, "n_within_tol": 15, "n_failed": 0, "map_total": 23.754691765679876, "noise_sd_raw": 207651.1080627169, "noise_over_sigma_c": 0.6646478692767318}}
- qnehvi_seconds: 8.1
- designs (MW per site ['110', '140', '146', '163', '270', '274']):
    - [157.260, 250.600, 191.095, 185.400, 579.000, 746.400]
    - [14.412, 250.600, 183.289, 185.400, 579.000, 746.400]
    - [0.000, 250.600, 0.000, 0.000, 0.000, 746.400]
    - [0.000, 0.000, 268.000, 185.400, 0.000, 746.400]
    - [0.000, 250.600, 0.000, 185.400, 0.000, 746.400]
    - [0.000, 250.600, 0.000, 76.300, 0.000, 746.400]
    - [0.000, 250.600, 36.028, 185.400, 579.000, 746.400]
    - [0.000, 0.000, 0.000, 185.400, 579.000, 515.640]
- realized Y (['V1', 'E1']):
    - [1.20008e+06, 8.15417e+09]
    - [1.40338e+06, 8.13961e+09]
    - [2.90571e+06, 8.11172e+09]
    - [2.59191e+06, 8.11617e+09]
    - [2.58756e+06, 8.11471e+09]
    - [2.74792e+06, 8.11324e+09]
    - [1.64429e+06, 8.12805e+09]
    - [2.32635e+06, 8.11518e+09]
<!-- END r4 -->
