# methods_E arm qnehvi seed_id 0 — ROUND_LOG (prompt 55; acq = qnehvi, base = ['n0_E'] nav prefix n0 = 48, objectives = ['V1', 'E1'])

Ledger: `lanes/committed/s1/s0/ledger.json`. stop_rule = record_only: gain_k and
would_stop_k = (gain_k < tau) AND (gain_{k-1} < tau) are graded and logged under tau_joint
(headline) and tau_marginal (recorded) with the joint-vs-marginal sensitivity column; the
rule never halts; every lane runs to hard_cap = 4. tau_joint = 0, tau_marginal = 0 — ZERO: the stop rule is budget-cap-only and the cap governs (plan 3).
E-D5 OPEN: see README.md for the two readings of a fire. Halts ONLY per plan 1.2/1.3
(HALT_FOR_DECISION.md). Acquisition jobs never submit; Kay submits via submit_ready_E.sh.
Stop NOW: `touch lanes/committed/s1/s0/STOP` on the CRC clone, then qdel the lane's JIDs.

<!-- BEGIN r1 -->
## Round 1 (methods_E_EMU_committed_s1_s0_r1)
- proposed_at: "2026-11-24T08:34:11+00:00"
- wave: "methods_E_EMU_committed_s1_s0_r1"
- acq: "qnehvi"
- acq_seed: 20261007
- guardrail_mode: "monitor"
- settings: {"mc_samples": 128, "num_restarts": 20, "raw_samples": 512, "alpha": 0.0, "prune_baseline": true, "sequential": true, "fast_mode": false, "constraint": "none", "guardrail_mode": "monitor", "seed": 20261007, "dtype": "float64", "bound_snaps": {"to_0": 0, "to_1": 1, "tol": 1e-12, "note": "bound cleanup after x * sx + mx; not lattice snapping"}}
- botorch: "0.16.1"
- bo_gp_sha: "60e6328236e745b3d34dc8cd704bb72888ae5d15"
- loo_rms_z: {"V1": 0.4268, "E1": 0.8267}
- noise_raw: {"V1": 14949.051609849952, "E1": 174965.13916944584}
- predictions: "waves/methods_E_EMU_committed_s1_s0_r1/predictions.csv"
- graded_at: "2026-11-24T08:34:12+00:00"
- n_train: 56
- n_hv: 55
- cumulative_hv: 138846721737957.97
- gain: 38323446337738.234
- gain_tau_joint: null
- would_stop_joint: false
- gain_tau_marginal: null
- would_stop_marginal: false
- joint_vs_marginal: {"ratio_joint_over_marginal": null, "agree": true, "fires": {"joint": false, "marginal": false}}
- first_fire_round: {"tau_joint": null, "tau_marginal": null}
- n_outside_ref: 0
- violations: ["methods_E_EMU_committed_s1_s0_r1:3"]
- suspects: []
- r2_flag: false
- r2_max_mwh: 188.24249648827964
- calibration: {"V1": {"mean_z": -0.03, "rms_z": 0.168, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}, "E1": {"mean_z": -0.007, "rms_z": 0.253, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}}
- C2_review: false
- C3_review: false
- halt: null
- decision: "graded (record_only)"
- fit_info: {"V1": {"fit_definition": "house"}, "E1": {"fit_definition": "v2", "converged": true, "mode_gap_nats": 53.68406410300448, "gap_second_nats": 2.884701544303425e-07, "n_within_tol": 13, "n_failed": 0, "map_total": -19.200766147217088, "noise_sd_raw": 174965.1391694458, "noise_over_sigma_c": 0.5600269029701294}}
- qnehvi_seconds: 8.3
- r1_shared_designs_with_seed: {}
- designs (MW per site ['110', '140', '146', '163', '270', '274']):
    - [17.500, 0.000, 0.000, 185.400, 579.000, 0.000]
    - [338.600, 0.000, 0.000, 185.400, 579.000, 0.000]
    - [0.000, 250.600, 159.965, 185.400, 579.000, 746.400]
    - [0.000, 0.000, 0.000, 185.400, 579.000, 701.119]
    - [0.000, 250.600, 0.000, 185.400, 579.000, 0.000]
    - [0.000, 250.600, 0.000, 185.400, 579.000, 746.400]
    - [79.429, 250.600, 213.657, 185.400, 579.000, 746.400]
    - [0.000, 0.000, 0.000, 185.400, 0.000, 746.400]
- realized Y (['V1', 'E1']):
    - [3.39913e+06, 8.08567e+09]
    - [2.72108e+06, 8.10528e+09]
    - [1.44598e+06, 8.13698e+09]
    - [2.07673e+06, 8.1152e+09]
    - [2.97341e+06, 8.09963e+09]
    - [1.71549e+06, 8.12558e+09]
    - [1.27849e+06, 8.14974e+09]
    - [2.99751e+06, 8.09839e+09]
<!-- END r1 -->

<!-- BEGIN r2 -->
## Round 2 (methods_E_EMU_committed_s1_s0_r2)
- proposed_at: "2026-11-24T08:34:22+00:00"
- wave: "methods_E_EMU_committed_s1_s0_r2"
- acq: "qnehvi"
- acq_seed: 20261008
- guardrail_mode: "constrain"
- settings: {"mc_samples": 128, "num_restarts": 20, "raw_samples": 512, "alpha": 0.0, "prune_baseline": true, "sequential": true, "fast_mode": false, "constraint": "shed <= 1.0 MWh (GP on the accumulated R1 column)", "guardrail_mode": "constrain", "seed": 20261008, "dtype": "float64", "bound_snaps": {"to_0": 0, "to_1": 0, "tol": 1e-12, "note": "bound cleanup after x * sx + mx; not lattice snapping"}}
- botorch: "0.16.1"
- bo_gp_sha: "60e6328236e745b3d34dc8cd704bb72888ae5d15"
- loo_rms_z: {"V1": 0.3742, "E1": 0.7829}
- noise_raw: {"V1": 14969.759000492735, "E1": 169056.59994969668}
- predictions: "waves/methods_E_EMU_committed_s1_s0_r2/predictions.csv"
- graded_at: "2026-11-24T08:34:23+00:00"
- n_train: 64
- n_hv: 63
- cumulative_hv: 147166814043295.5
- gain: 8320092305337.531
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
- r2_max_mwh: 175.8235135844525
- calibration: {"V1": {"mean_z": 0.045, "rms_z": 0.157, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}, "E1": {"mean_z": -0.108, "rms_z": 0.501, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}}
- C2_review: false
- C3_review: false
- halt: null
- decision: "graded (record_only)"
- fit_info: {"V1": {"fit_definition": "house"}, "E1": {"fit_definition": "v2", "converged": true, "mode_gap_nats": NaN, "gap_second_nats": 5.5657475073189744e-08, "n_within_tol": 16, "n_failed": 0, "map_total": -5.880356892658121, "noise_sd_raw": 169056.5999496966, "noise_over_sigma_c": 0.5411149017793714}}
- qnehvi_seconds: 9.1
- designs (MW per site ['110', '140', '146', '163', '270', '274']):
    - [8.983, 250.600, 107.403, 185.400, 579.000, 746.400]
    - [4.948, 250.600, 212.397, 185.400, 579.000, 746.400]
    - [97.699, 0.000, 0.000, 185.400, 579.000, 0.000]
    - [0.000, 0.000, 0.000, 0.000, 579.000, 624.936]
    - [0.000, 63.518, 0.000, 185.400, 579.000, 746.400]
    - [156.927, 250.600, 202.618, 185.400, 579.000, 746.400]
    - [0.000, 250.600, 58.851, 185.400, 579.000, 746.400]
    - [0.000, 0.000, 0.000, 72.867, 579.000, 0.000]
- realized Y (['V1', 'E1']):
    - [1.50843e+06, 8.13464e+09]
    - [1.39644e+06, 8.14024e+09]
    - [3.22259e+06, 8.09241e+09]
    - [2.50851e+06, 8.1112e+09]
    - [1.92297e+06, 8.12053e+09]
    - [1.19163e+06, 8.15645e+09]
    - [1.59477e+06, 8.12991e+09]
    - [3.7182e+06, 8.08472e+09]
<!-- END r2 -->

<!-- BEGIN r3 -->
## Round 3 (methods_E_EMU_committed_s1_s0_r3)
- proposed_at: "2026-11-24T08:34:33+00:00"
- wave: "methods_E_EMU_committed_s1_s0_r3"
- acq: "qnehvi"
- acq_seed: 20261009
- guardrail_mode: "constrain"
- settings: {"mc_samples": 128, "num_restarts": 20, "raw_samples": 512, "alpha": 0.0, "prune_baseline": true, "sequential": true, "fast_mode": false, "constraint": "shed <= 1.0 MWh (GP on the accumulated R1 column)", "guardrail_mode": "constrain", "seed": 20261009, "dtype": "float64", "bound_snaps": {"to_0": 0, "to_1": 0, "tol": 1e-12, "note": "bound cleanup after x * sx + mx; not lattice snapping"}}
- botorch: "0.16.1"
- bo_gp_sha: "60e6328236e745b3d34dc8cd704bb72888ae5d15"
- loo_rms_z: {"V1": 0.3363, "E1": 0.8292}
- noise_raw: {"V1": 16207.210120149819, "E1": 171926.05593106223}
- predictions: "waves/methods_E_EMU_committed_s1_s0_r3/predictions.csv"
- graded_at: "2026-11-24T08:34:33+00:00"
- n_train: 72
- n_hv: 71
- cumulative_hv: 148197362740191.34
- gain: 1030548696895.8438
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
- r2_max_mwh: 183.88516516894077
- calibration: {"V1": {"mean_z": -0.043, "rms_z": 0.171, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}, "E1": {"mean_z": 0.302, "rms_z": 1.42, "cov95": 6, "n_abs_z_gt3": 0, "transform": "std"}}
- C2_review: false
- C3_review: false
- halt: null
- decision: "graded (record_only)"
- fit_info: {"V1": {"fit_definition": "house"}, "E1": {"fit_definition": "v2", "converged": true, "mode_gap_nats": NaN, "gap_second_nats": 2.2587257220152424e-07, "n_within_tol": 16, "n_failed": 0, "map_total": 13.90543025493077, "noise_sd_raw": 171926.05593106218, "noise_over_sigma_c": 0.5502994316467582}}
- qnehvi_seconds: 8.7
- designs (MW per site ['110', '140', '146', '163', '270', '274']):
    - [0.000, 250.600, 0.000, 0.000, 0.000, 746.400]
    - [36.881, 250.600, 221.047, 185.400, 579.000, 746.400]
    - [338.600, 0.000, 0.000, 0.000, 0.000, 746.400]
    - [0.000, 0.000, 268.000, 185.400, 0.000, 746.400]
    - [0.000, 0.000, 0.000, 185.400, 579.000, 528.411]
    - [222.411, 250.600, 188.948, 184.835, 579.000, 746.400]
    - [0.000, 250.600, 0.000, 47.427, 579.000, 746.400]
    - [338.600, 250.600, 70.704, 185.400, 579.000, 746.400]
- realized Y (['V1', 'E1']):
    - [2.90225e+06, 8.10308e+09]
    - [1.33564e+06, 8.14441e+09]
    - [2.77162e+06, 8.10555e+09]
    - [2.58992e+06, 8.11241e+09]
    - [2.30662e+06, 8.11354e+09]
    - [1.14448e+06, 8.16156e+09]
    - [1.85649e+06, 8.12387e+09]
    - [1.26409e+06, 8.15676e+09]
<!-- END r3 -->

<!-- BEGIN r4 -->
## Round 4 (methods_E_EMU_committed_s1_s0_r4)
- proposed_at: "2026-11-24T08:34:44+00:00"
- wave: "methods_E_EMU_committed_s1_s0_r4"
- acq: "qnehvi"
- acq_seed: 20261010
- guardrail_mode: "constrain"
- settings: {"mc_samples": 128, "num_restarts": 20, "raw_samples": 512, "alpha": 0.0, "prune_baseline": true, "sequential": true, "fast_mode": false, "constraint": "shed <= 1.0 MWh (GP on the accumulated R1 column)", "guardrail_mode": "constrain", "seed": 20261010, "dtype": "float64", "bound_snaps": {"to_0": 0, "to_1": 0, "tol": 1e-12, "note": "bound cleanup after x * sx + mx; not lattice snapping"}}
- botorch: "0.16.1"
- bo_gp_sha: "60e6328236e745b3d34dc8cd704bb72888ae5d15"
- loo_rms_z: {"V1": 0.3179, "E1": 0.9043}
- noise_raw: {"V1": 16166.694738602577, "E1": 261313.67501133788}
- predictions: "waves/methods_E_EMU_committed_s1_s0_r4/predictions.csv"
- graded_at: "2026-11-24T08:34:45+00:00"
- n_train: 80
- n_hv: 79
- cumulative_hv: 149343143247398.8
- gain: 1145780507207.4688
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
- r2_max_mwh: 190.72902240932652
- calibration: {"V1": {"mean_z": 0.016, "rms_z": 0.147, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}, "E1": {"mean_z": 0.587, "rms_z": 1.261, "cov95": 6, "n_abs_z_gt3": 0, "transform": "std"}}
- C2_review: false
- C3_review: false
- halt: null
- decision: "graded (record_only)"
- fit_info: {"V1": {"fit_definition": "house"}, "E1": {"fit_definition": "v2", "converged": true, "mode_gap_nats": NaN, "gap_second_nats": 7.95657228991331e-09, "n_within_tol": 16, "n_failed": 0, "map_total": 22.146093731630934, "noise_sd_raw": 261313.67501133788, "noise_over_sigma_c": 0.8364105490672412}}
- qnehvi_seconds: 10.2
- designs (MW per site ['110', '140', '146', '163', '270', '274']):
    - [107.513, 250.600, 223.402, 185.400, 579.000, 746.400]
    - [0.000, 250.600, 184.918, 185.400, 579.000, 746.400]
    - [0.000, 250.600, 0.000, 185.400, 0.000, 746.400]
    - [0.000, 250.600, 28.536, 185.400, 579.000, 746.400]
    - [165.763, 250.600, 225.488, 185.400, 579.000, 746.400]
    - [0.000, 17.605, 0.000, 185.400, 579.000, 746.400]
    - [0.000, 0.000, 0.000, 185.400, 579.000, 246.798]
    - [54.277, 250.600, 225.016, 185.400, 579.000, 746.400]
- realized Y (['V1', 'E1']):
    - [1.23365e+06, 8.15376e+09]
    - [1.42871e+06, 8.13852e+09]
    - [2.58273e+06, 8.10878e+09]
    - [1.65193e+06, 8.12745e+09]
    - [1.16385e+06, 8.15969e+09]
    - [2.00493e+06, 8.11728e+09]
    - [2.86389e+06, 8.10398e+09]
    - [1.30983e+06, 8.14741e+09]
<!-- END r4 -->
