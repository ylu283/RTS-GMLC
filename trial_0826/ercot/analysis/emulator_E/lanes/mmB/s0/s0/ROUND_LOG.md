# methods_E arm qnehvi seed_id 0 — ROUND_LOG (prompt 55; acq = qnehvi, base = ['n0_E'] nav prefix n0 = 48, objectives = ['V1', 'E1'])

Ledger: `lanes/mmB/s0/s0/ledger.json`. stop_rule = record_only: gain_k and
would_stop_k = (gain_k < tau) AND (gain_{k-1} < tau) are graded and logged under tau_joint
(headline) and tau_marginal (recorded) with the joint-vs-marginal sensitivity column; the
rule never halts; every lane runs to hard_cap = 4. tau_joint = 0, tau_marginal = 0 — ZERO: the stop rule is budget-cap-only and the cap governs (plan 3).
E-D5 OPEN: see README.md for the two readings of a fire. Halts ONLY per plan 1.2/1.3
(HALT_FOR_DECISION.md). Acquisition jobs never submit; Kay submits via submit_ready_E.sh.
Stop NOW: `touch lanes/mmB/s0/s0/STOP` on the CRC clone, then qdel the lane's JIDs.

<!-- BEGIN r1 -->
## Round 1 (methods_E_EMU_mmB_s0_s0_r1)
- proposed_at: "2026-11-24T08:34:50+00:00"
- wave: "methods_E_EMU_mmB_s0_s0_r1"
- acq: "qnehvi"
- acq_seed: 20261007
- guardrail_mode: "monitor"
- settings: {"mc_samples": 128, "num_restarts": 20, "raw_samples": 512, "alpha": 0.0, "prune_baseline": true, "sequential": true, "fast_mode": false, "constraint": "none", "guardrail_mode": "monitor", "seed": 20261007, "dtype": "float64", "bound_snaps": {"to_0": 0, "to_1": 0, "tol": 1e-12, "note": "bound cleanup after x * sx + mx; not lattice snapping"}}
- botorch: "0.16.1"
- bo_gp_sha: "60e6328236e745b3d34dc8cd704bb72888ae5d15"
- loo_rms_z: {"V1": 0.5942, "E1": 0.8267}
- noise_raw: {"V1": 16640.430282987367, "E1": 174965.13916944584}
- predictions: "waves/methods_E_EMU_mmB_s0_s0_r1/predictions.csv"
- graded_at: "2026-11-24T08:34:51+00:00"
- n_train: 56
- n_hv: 56
- cumulative_hv: 142254259806629.62
- gain: 41720703361466.66
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
- r2_max_mwh: 188.43390933722088
- calibration: {"V1": {"mean_z": 0.023, "rms_z": 0.863, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}, "E1": {"mean_z": 0.022, "rms_z": 0.15, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}}
- C2_review: false
- C3_review: false
- halt: null
- decision: "graded (record_only)"
- fit_info: {"V1": {"fit_definition": "house"}, "E1": {"fit_definition": "v2", "converged": true, "mode_gap_nats": 53.68406410300448, "gap_second_nats": 2.884701544303425e-07, "n_within_tol": 13, "n_failed": 0, "map_total": -19.200766147217088, "noise_sd_raw": 174965.1391694458, "noise_over_sigma_c": 0.5600269029701294}}
- qnehvi_seconds: 6.9
- r1_shared_designs_with_seed: {}
- designs (MW per site ['110', '140', '146', '163', '270', '274']):
    - [0.000, 0.000, 0.000, 185.400, 0.000, 746.400]
    - [0.000, 0.000, 0.000, 185.400, 579.000, 612.418]
    - [0.000, 0.000, 0.000, 185.400, 579.000, 0.000]
    - [0.000, 250.600, 161.819, 185.400, 579.000, 746.400]
    - [338.600, 0.000, 0.000, 185.400, 579.000, 0.000]
    - [0.000, 250.600, 0.000, 185.400, 579.000, 746.400]
    - [82.998, 250.600, 207.919, 185.400, 579.000, 746.400]
    - [0.000, 250.600, 0.000, 185.400, 579.000, 0.000]
- realized Y (['V1', 'E1']):
    - [3.0836e+06, 8.09829e+09]
    - [2.19783e+06, 8.11446e+09]
    - [3.55652e+06, 8.08474e+09]
    - [1.3823e+06, 8.13697e+09]
    - [2.75178e+06, 8.10429e+09]
    - [1.64215e+06, 8.12547e+09]
    - [1.20459e+06, 8.15007e+09]
    - [3.00999e+06, 8.09882e+09]
<!-- END r1 -->

<!-- BEGIN r2 -->
## Round 2 (methods_E_EMU_mmB_s0_s0_r2)
- proposed_at: "2026-11-24T08:34:58+00:00"
- wave: "methods_E_EMU_mmB_s0_s0_r2"
- acq: "qnehvi"
- acq_seed: 20261008
- guardrail_mode: "monitor"
- settings: {"mc_samples": 128, "num_restarts": 20, "raw_samples": 512, "alpha": 0.0, "prune_baseline": true, "sequential": true, "fast_mode": false, "constraint": "none", "guardrail_mode": "monitor", "seed": 20261008, "dtype": "float64", "bound_snaps": {"to_0": 0, "to_1": 0, "tol": 1e-12, "note": "bound cleanup after x * sx + mx; not lattice snapping"}}
- botorch: "0.16.1"
- bo_gp_sha: "60e6328236e745b3d34dc8cd704bb72888ae5d15"
- loo_rms_z: {"V1": 0.5661, "E1": 0.7851}
- noise_raw: {"V1": 16873.908096947558, "E1": 169717.38920612415}
- predictions: "waves/methods_E_EMU_mmB_s0_s0_r2/predictions.csv"
- graded_at: "2026-11-24T08:34:58+00:00"
- n_train: 64
- n_hv: 64
- cumulative_hv: 148525105494254.7
- gain: 6270845687625.0625
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
- r2_max_mwh: 178.81140332196992
- calibration: {"V1": {"mean_z": -0.008, "rms_z": 0.361, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}, "E1": {"mean_z": 0.09, "rms_z": 0.4, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}}
- C2_review: false
- C3_review: false
- halt: null
- decision: "graded (record_only)"
- fit_info: {"V1": {"fit_definition": "house"}, "E1": {"fit_definition": "v2", "converged": true, "mode_gap_nats": NaN, "gap_second_nats": 8.578076915455313e-08, "n_within_tol": 16, "n_failed": 0, "map_total": -5.385111194834494, "noise_sd_raw": 169717.38920612424, "noise_over_sigma_c": 0.5432299503116091}}
- qnehvi_seconds: 5.7
- designs (MW per site ['110', '140', '146', '163', '270', '274']):
    - [0.000, 0.000, 0.000, 27.753, 0.000, 746.400]
    - [0.000, 29.416, 0.000, 185.400, 579.000, 746.400]
    - [0.000, 250.600, 73.822, 185.400, 579.000, 746.400]
    - [0.000, 250.600, 0.000, 185.400, 0.000, 746.400]
    - [102.394, 0.000, 0.000, 185.400, 579.000, 0.000]
    - [31.525, 250.600, 198.102, 185.400, 579.000, 746.400]
    - [0.000, 0.000, 0.000, 185.400, 579.000, 476.095]
    - [148.862, 250.600, 206.048, 185.400, 579.000, 746.400]
- realized Y (['V1', 'E1']):
    - [3.43273e+06, 8.09256e+09]
    - [1.98201e+06, 8.11813e+09]
    - [1.50997e+06, 8.13129e+09]
    - [2.58768e+06, 8.10952e+09]
    - [3.28286e+06, 8.09256e+09]
    - [1.28707e+06, 8.14335e+09]
    - [2.42431e+06, 8.11216e+09]
    - [1.1268e+06, 8.15678e+09]
<!-- END r2 -->

<!-- BEGIN r3 -->
## Round 3 (methods_E_EMU_mmB_s0_s0_r3)
- proposed_at: "2026-11-24T08:35:04+00:00"
- wave: "methods_E_EMU_mmB_s0_s0_r3"
- acq: "qnehvi"
- acq_seed: 20261009
- guardrail_mode: "monitor"
- settings: {"mc_samples": 128, "num_restarts": 20, "raw_samples": 512, "alpha": 0.0, "prune_baseline": true, "sequential": true, "fast_mode": false, "constraint": "none", "guardrail_mode": "monitor", "seed": 20261009, "dtype": "float64", "bound_snaps": {"to_0": 4, "to_1": 0, "tol": 1e-12, "note": "bound cleanup after x * sx + mx; not lattice snapping"}}
- botorch: "0.16.1"
- bo_gp_sha: "60e6328236e745b3d34dc8cd704bb72888ae5d15"
- loo_rms_z: {"V1": 0.5052, "E1": 0.7998}
- noise_raw: {"V1": 17433.844418676075, "E1": 140629.99856551958}
- predictions: "waves/methods_E_EMU_mmB_s0_s0_r3/predictions.csv"
- graded_at: "2026-11-24T08:35:05+00:00"
- n_train: 72
- n_hv: 72
- cumulative_hv: 149758089459263.2
- gain: 1232983965008.5
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
- r2_max_mwh: 186.1735190668777
- calibration: {"V1": {"mean_z": 0.061, "rms_z": 0.438, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}, "E1": {"mean_z": 0.264, "rms_z": 1.176, "cov95": 6, "n_abs_z_gt3": 0, "transform": "std"}}
- C2_review: false
- C3_review: false
- halt: null
- decision: "graded (record_only)"
- fit_info: {"V1": {"fit_definition": "house"}, "E1": {"fit_definition": "v2", "converged": true, "mode_gap_nats": NaN, "gap_second_nats": 2.1603973721084913e-08, "n_within_tol": 16, "n_failed": 0, "map_total": 13.329993192727773, "noise_sd_raw": 140629.99856551958, "noise_over_sigma_c": 0.45012728212715264}}
- qnehvi_seconds: 5.1
- designs (MW per site ['110', '140', '146', '163', '270', '274']):
    - [0.000, 250.600, 0.000, 0.000, 579.000, 0.000]
    - [0.000, 250.600, 0.000, 35.980, 579.000, 746.400]
    - [0.000, 250.600, 212.178, 185.400, 579.000, 746.400]
    - [0.000, 250.600, 35.415, 185.400, 579.000, 746.400]
    - [108.134, 250.600, 217.055, 185.400, 579.000, 746.400]
    - [338.600, 250.600, 0.000, 0.000, 579.000, 0.000]
    - [267.944, 0.000, 0.000, 185.400, 579.000, 0.000]
    - [176.001, 250.600, 222.349, 185.400, 579.000, 746.400]
- realized Y (['V1', 'E1']):
    - [3.42403e+06, 8.09178e+09]
    - [1.84602e+06, 8.12367e+09]
    - [1.32144e+06, 8.13989e+09]
    - [1.57288e+06, 8.12795e+09]
    - [1.16419e+06, 8.15348e+09]
    - [2.69059e+06, 8.11132e+09]
    - [2.89819e+06, 8.1025e+09]
    - [1.08854e+06, 8.16084e+09]
<!-- END r3 -->

<!-- BEGIN r4 -->
## Round 4 (methods_E_EMU_mmB_s0_s0_r4)
- proposed_at: "2026-11-24T08:35:12+00:00"
- wave: "methods_E_EMU_mmB_s0_s0_r4"
- acq: "qnehvi"
- acq_seed: 20261010
- guardrail_mode: "monitor"
- settings: {"mc_samples": 128, "num_restarts": 20, "raw_samples": 512, "alpha": 0.0, "prune_baseline": true, "sequential": true, "fast_mode": false, "constraint": "none", "guardrail_mode": "monitor", "seed": 20261010, "dtype": "float64", "bound_snaps": {"to_0": 2, "to_1": 0, "tol": 1e-12, "note": "bound cleanup after x * sx + mx; not lattice snapping"}}
- botorch: "0.16.1"
- bo_gp_sha: "60e6328236e745b3d34dc8cd704bb72888ae5d15"
- loo_rms_z: {"V1": 0.4843, "E1": 0.8636}
- noise_raw: {"V1": 18125.330404664302, "E1": 187733.1530123761}
- predictions: "waves/methods_E_EMU_mmB_s0_s0_r4/predictions.csv"
- graded_at: "2026-11-24T08:35:13+00:00"
- n_train: 80
- n_hv: 80
- cumulative_hv: 150174617300863.5
- gain: 416527841600.3125
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
- r2_max_mwh: 182.65474901387734
- calibration: {"V1": {"mean_z": -0.566, "rms_z": 0.846, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}, "E1": {"mean_z": -0.08, "rms_z": 0.817, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}}
- C2_review: false
- C3_review: false
- halt: null
- decision: "graded (record_only)"
- fit_info: {"V1": {"fit_definition": "house"}, "E1": {"fit_definition": "v2", "converged": true, "mode_gap_nats": 7.661914657655096, "gap_second_nats": 7.887680908424954e-08, "n_within_tol": 15, "n_failed": 0, "map_total": 30.082013026480737, "noise_sd_raw": 187733.153012376, "noise_over_sigma_c": 0.6008946511597333}}
- qnehvi_seconds: 6.8
- designs (MW per site ['110', '140', '146', '163', '270', '274']):
    - [46.033, 250.600, 223.276, 185.400, 579.000, 746.400]
    - [0.000, 196.995, 0.000, 185.400, 0.000, 746.400]
    - [0.000, 0.000, 0.000, 124.186, 0.000, 746.400]
    - [338.600, 250.600, 101.758, 185.400, 579.000, 746.400]
    - [338.600, 250.600, 0.000, 185.400, 579.000, 746.400]
    - [338.600, 0.000, 0.000, 0.000, 0.000, 746.400]
    - [176.407, 247.920, 190.794, 139.159, 579.000, 746.400]
    - [324.207, 66.906, 123.441, 177.639, 566.086, 682.149]
- realized Y (['V1', 'E1']):
    - [1.23867e+06, 8.14699e+09]
    - [2.67717e+06, 8.10807e+09]
    - [3.19812e+06, 8.09697e+09]
    - [1.08504e+06, 8.15993e+09]
    - [1.23712e+06, 8.15022e+09]
    - [2.82176e+06, 8.10628e+09]
    - [1.14594e+06, 8.15838e+09]
    - [1.27912e+06, 8.1512e+09]
<!-- END r4 -->
