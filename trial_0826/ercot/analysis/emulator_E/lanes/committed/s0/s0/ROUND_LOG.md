# methods_E arm qnehvi seed_id 0 — ROUND_LOG (prompt 55; acq = qnehvi, base = ['n0_E'] nav prefix n0 = 48, objectives = ['V1', 'E1'])

Ledger: `lanes/committed/s0/s0/ledger.json`. stop_rule = record_only: gain_k and
would_stop_k = (gain_k < tau) AND (gain_{k-1} < tau) are graded and logged under tau_joint
(headline) and tau_marginal (recorded) with the joint-vs-marginal sensitivity column; the
rule never halts; every lane runs to hard_cap = 4. tau_joint = 0, tau_marginal = 0 — ZERO: the stop rule is budget-cap-only and the cap governs (plan 3).
E-D5 OPEN: see README.md for the two readings of a fire. Halts ONLY per plan 1.2/1.3
(HALT_FOR_DECISION.md). Acquisition jobs never submit; Kay submits via submit_ready_E.sh.
Stop NOW: `touch lanes/committed/s0/s0/STOP` on the CRC clone, then qdel the lane's JIDs.

<!-- BEGIN r1 -->
## Round 1 (methods_E_EMU_committed_s0_s0_r1)
- proposed_at: "2026-11-24T08:34:12+00:00"
- wave: "methods_E_EMU_committed_s0_s0_r1"
- acq: "qnehvi"
- acq_seed: 20261007
- guardrail_mode: "monitor"
- settings: {"mc_samples": 128, "num_restarts": 20, "raw_samples": 512, "alpha": 0.0, "prune_baseline": true, "sequential": true, "fast_mode": false, "constraint": "none", "guardrail_mode": "monitor", "seed": 20261007, "dtype": "float64", "bound_snaps": {"to_0": 0, "to_1": 1, "tol": 1e-12, "note": "bound cleanup after x * sx + mx; not lattice snapping"}}
- botorch: "0.16.1"
- bo_gp_sha: "60e6328236e745b3d34dc8cd704bb72888ae5d15"
- loo_rms_z: {"V1": 0.4268, "E1": 0.8267}
- noise_raw: {"V1": 14949.051609849952, "E1": 174965.13916944584}
- predictions: "waves/methods_E_EMU_committed_s0_s0_r1/predictions.csv"
- graded_at: "2026-11-24T08:34:12+00:00"
- n_train: 56
- n_hv: 56
- cumulative_hv: 141566211779269.44
- gain: 41042936379049.7
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
- r2_max_mwh: 182.33594411604116
- calibration: {"V1": {"mean_z": -0.017, "rms_z": 0.134, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}, "E1": {"mean_z": 0.055, "rms_z": 0.137, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}}
- C2_review: false
- C3_review: false
- halt: null
- decision: "graded (record_only)"
- fit_info: {"V1": {"fit_definition": "house"}, "E1": {"fit_definition": "v2", "converged": true, "mode_gap_nats": 53.68406410300448, "gap_second_nats": 2.884701544303425e-07, "n_within_tol": 13, "n_failed": 0, "map_total": -19.200766147217088, "noise_sd_raw": 174965.1391694458, "noise_over_sigma_c": 0.5600269029701294}}
- qnehvi_seconds: 8.6
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
    - [3.39186e+06, 8.08561e+09]
    - [2.71515e+06, 8.10427e+09]
    - [1.45446e+06, 8.13778e+09]
    - [2.08346e+06, 8.11674e+09]
    - [2.97143e+06, 8.09919e+09]
    - [1.71743e+06, 8.12593e+09]
    - [1.27857e+06, 8.14976e+09]
    - [2.99826e+06, 8.09755e+09]
<!-- END r1 -->

<!-- BEGIN r2 -->
## Round 2 (methods_E_EMU_committed_s0_s0_r2)
- proposed_at: "2026-11-24T08:34:20+00:00"
- wave: "methods_E_EMU_committed_s0_s0_r2"
- acq: "qnehvi"
- acq_seed: 20261008
- guardrail_mode: "monitor"
- settings: {"mc_samples": 128, "num_restarts": 20, "raw_samples": 512, "alpha": 0.0, "prune_baseline": true, "sequential": true, "fast_mode": false, "constraint": "none", "guardrail_mode": "monitor", "seed": 20261008, "dtype": "float64", "bound_snaps": {"to_0": 0, "to_1": 0, "tol": 1e-12, "note": "bound cleanup after x * sx + mx; not lattice snapping"}}
- botorch: "0.16.1"
- bo_gp_sha: "60e6328236e745b3d34dc8cd704bb72888ae5d15"
- loo_rms_z: {"V1": 0.3717, "E1": 0.8003}
- noise_raw: {"V1": 14943.094567015372, "E1": 170348.06342908216}
- predictions: "waves/methods_E_EMU_committed_s0_s0_r2/predictions.csv"
- graded_at: "2026-11-24T08:34:21+00:00"
- n_train: 64
- n_hv: 64
- cumulative_hv: 146840624433540.3
- gain: 5274412654270.875
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
- r2_max_mwh: 187.3381143887112
- calibration: {"V1": {"mean_z": -0.089, "rms_z": 0.206, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}, "E1": {"mean_z": 0.238, "rms_z": 0.915, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}}
- C2_review: false
- C3_review: false
- halt: null
- decision: "graded (record_only)"
- fit_info: {"V1": {"fit_definition": "house"}, "E1": {"fit_definition": "v2", "converged": true, "mode_gap_nats": NaN, "gap_second_nats": 4.162112787753358e-08, "n_within_tol": 16, "n_failed": 0, "map_total": -5.615621172943836, "noise_sd_raw": 170348.0634290822, "noise_over_sigma_c": 0.5452486069053902}}
- qnehvi_seconds: 7.0
- designs (MW per site ['110', '140', '146', '163', '270', '274']):
    - [0.000, 0.000, 0.000, 185.400, 241.525, 746.400]
    - [0.000, 250.600, 73.222, 185.400, 579.000, 746.400]
    - [174.275, 250.600, 189.168, 185.400, 579.000, 746.400]
    - [0.000, 0.000, 0.000, 185.400, 579.000, 520.116]
    - [36.206, 250.600, 188.386, 185.400, 579.000, 746.400]
    - [338.600, 0.000, 0.000, 0.000, 0.000, 746.400]
    - [94.880, 0.000, 0.000, 185.400, 579.000, 0.000]
    - [0.000, 61.036, 0.000, 185.400, 579.000, 746.400]
- realized Y (['V1', 'E1']):
    - [2.50147e+06, 8.11254e+09]
    - [1.57174e+06, 8.13123e+09]
    - [1.18135e+06, 8.15747e+09]
    - [2.31684e+06, 8.1136e+09]
    - [1.36273e+06, 8.14403e+09]
    - [2.76818e+06, 8.10652e+09]
    - [3.22644e+06, 8.09252e+09]
    - [1.92949e+06, 8.12022e+09]
<!-- END r2 -->

<!-- BEGIN r3 -->
## Round 3 (methods_E_EMU_committed_s0_s0_r3)
- proposed_at: "2026-11-24T08:34:29+00:00"
- wave: "methods_E_EMU_committed_s0_s0_r3"
- acq: "qnehvi"
- acq_seed: 20261009
- guardrail_mode: "monitor"
- settings: {"mc_samples": 128, "num_restarts": 20, "raw_samples": 512, "alpha": 0.0, "prune_baseline": true, "sequential": true, "fast_mode": false, "constraint": "none", "guardrail_mode": "monitor", "seed": 20261009, "dtype": "float64", "bound_snaps": {"to_0": 0, "to_1": 0, "tol": 1e-12, "note": "bound cleanup after x * sx + mx; not lattice snapping"}}
- botorch: "0.16.1"
- bo_gp_sha: "60e6328236e745b3d34dc8cd704bb72888ae5d15"
- loo_rms_z: {"V1": 0.3586, "E1": 0.887}
- noise_raw: {"V1": 15529.611707423834, "E1": 240192.53829242103}
- predictions: "waves/methods_E_EMU_committed_s0_s0_r3/predictions.csv"
- graded_at: "2026-11-24T08:34:30+00:00"
- n_train: 72
- n_hv: 72
- cumulative_hv: 147875680994631.25
- gain: 1035056561090.9375
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
- r2_max_mwh: 175.8050521752434
- calibration: {"V1": {"mean_z": -0.009, "rms_z": 0.187, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}, "E1": {"mean_z": -0.085, "rms_z": 0.766, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}}
- C2_review: false
- C3_review: false
- halt: null
- decision: "graded (record_only)"
- fit_info: {"V1": {"fit_definition": "house"}, "E1": {"fit_definition": "v2", "converged": true, "mode_gap_nats": 83.95963282519688, "gap_second_nats": 8.128317574573884e-09, "n_within_tol": 15, "n_failed": 0, "map_total": 8.202590172518342, "noise_sd_raw": 240192.53829242085, "noise_over_sigma_c": 0.7688061974801029}}
- qnehvi_seconds: 6.7
- designs (MW per site ['110', '140', '146', '163', '270', '274']):
    - [0.000, 250.600, 0.000, 0.000, 579.000, 0.000]
    - [0.000, 250.600, 0.000, 185.400, 0.000, 746.400]
    - [0.000, 250.600, 114.134, 185.400, 579.000, 746.400]
    - [0.000, 250.600, 0.000, 55.739, 579.000, 746.400]
    - [0.000, 0.000, 0.000, 0.000, 0.000, 746.400]
    - [0.000, 0.000, 268.000, 185.400, 0.000, 746.400]
    - [338.600, 0.000, 0.000, 185.400, 579.000, 746.400]
    - [128.419, 250.600, 193.055, 185.400, 579.000, 746.400]
- realized Y (['V1', 'E1']):
    - [3.34672e+06, 8.09172e+09]
    - [2.58805e+06, 8.10939e+09]
    - [1.50946e+06, 8.13395e+09]
    - [1.84368e+06, 8.12391e+09]
    - [3.37359e+06, 8.09274e+09]
    - [2.59539e+06, 8.11278e+09]
    - [1.64282e+06, 8.13476e+09]
    - [1.22654e+06, 8.15388e+09]
<!-- END r3 -->

<!-- BEGIN r4 -->
## Round 4 (methods_E_EMU_committed_s0_s0_r4)
- proposed_at: "2026-11-24T08:34:39+00:00"
- wave: "methods_E_EMU_committed_s0_s0_r4"
- acq: "qnehvi"
- acq_seed: 20261010
- guardrail_mode: "monitor"
- settings: {"mc_samples": 128, "num_restarts": 20, "raw_samples": 512, "alpha": 0.0, "prune_baseline": true, "sequential": true, "fast_mode": false, "constraint": "none", "guardrail_mode": "monitor", "seed": 20261010, "dtype": "float64", "bound_snaps": {"to_0": 2, "to_1": 0, "tol": 1e-12, "note": "bound cleanup after x * sx + mx; not lattice snapping"}}
- botorch: "0.16.1"
- bo_gp_sha: "60e6328236e745b3d34dc8cd704bb72888ae5d15"
- loo_rms_z: {"V1": 0.3303, "E1": 0.865}
- noise_raw: {"V1": 15599.33842487317, "E1": 271157.33148708235}
- predictions: "waves/methods_E_EMU_committed_s0_s0_r4/predictions.csv"
- graded_at: "2026-11-24T08:34:40+00:00"
- n_train: 80
- n_hv: 80
- cumulative_hv: 148589644761117.22
- gain: 713963766485.9688
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
- r2_max_mwh: 217.68759433136017
- calibration: {"V1": {"mean_z": 0.063, "rms_z": 0.194, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}, "E1": {"mean_z": 0.271, "rms_z": 1.215, "cov95": 7, "n_abs_z_gt3": 0, "transform": "std"}}
- C2_review: false
- C3_review: false
- halt: null
- decision: "graded (record_only)"
- fit_info: {"V1": {"fit_definition": "house"}, "E1": {"fit_definition": "v2", "converged": true, "mode_gap_nats": 18.542908268128304, "gap_second_nats": 3.1689950219515595e-08, "n_within_tol": 15, "n_failed": 0, "map_total": 18.94435381484359, "noise_sd_raw": 271157.33148708235, "noise_over_sigma_c": 0.867918039508947}}
- qnehvi_seconds: 8.6
- designs (MW per site ['110', '140', '146', '163', '270', '274']):
    - [201.000, 250.600, 202.250, 180.463, 579.000, 746.400]
    - [66.247, 250.600, 186.121, 185.400, 579.000, 746.400]
    - [0.000, 56.194, 0.000, 185.400, 0.000, 746.400]
    - [338.600, 250.600, 137.486, 137.612, 579.000, 746.400]
    - [338.600, 0.000, 0.000, 185.400, 0.000, 746.400]
    - [338.600, 250.600, 80.209, 127.633, 579.000, 746.400]
    - [0.000, 250.600, 35.605, 185.400, 579.000, 746.400]
    - [13.630, 250.600, 180.719, 185.400, 579.000, 746.400]
- realized Y (['V1', 'E1']):
    - [1.15277e+06, 8.16172e+09]
    - [1.3154e+06, 8.14685e+09]
    - [2.89576e+06, 8.10225e+09]
    - [1.1495e+06, 8.16233e+09]
    - [2.46079e+06, 8.11354e+09]
    - [1.24474e+06, 8.15805e+09]
    - [1.64008e+06, 8.12895e+09]
    - [1.41004e+06, 8.13994e+09]
<!-- END r4 -->
