# methods_E arm qnehvi seed_id 4 — ROUND_LOG (prompt 55; acq = qnehvi, base = ['n0_E'] nav prefix n0 = 48, objectives = ['V1', 'E1'])

Ledger: `lanes/house/s1/s4/ledger.json`. stop_rule = record_only: gain_k and
would_stop_k = (gain_k < tau) AND (gain_{k-1} < tau) are graded and logged under tau_joint
(headline) and tau_marginal (recorded) with the joint-vs-marginal sensitivity column; the
rule never halts; every lane runs to hard_cap = 4. tau_joint = 0, tau_marginal = 0 — ZERO: the stop rule is budget-cap-only and the cap governs (plan 3).
E-D5 OPEN: see README.md for the two readings of a fire. Halts ONLY per plan 1.2/1.3
(HALT_FOR_DECISION.md). Acquisition jobs never submit; Kay submits via submit_ready_E.sh.
Stop NOW: `touch lanes/house/s1/s4/STOP` on the CRC clone, then qdel the lane's JIDs.

<!-- BEGIN r1 -->
## Round 1 (methods_E_EMU_house_s1_s4_r1)
- proposed_at: "2026-11-24T08:06:56+00:00"
- wave: "methods_E_EMU_house_s1_s4_r1"
- acq: "qnehvi"
- acq_seed: 20261407
- guardrail_mode: "monitor"
- settings: {"mc_samples": 128, "num_restarts": 20, "raw_samples": 512, "alpha": 0.0, "prune_baseline": true, "sequential": true, "fast_mode": false, "constraint": "none", "guardrail_mode": "monitor", "seed": 20261407, "dtype": "float64", "bound_snaps": {"to_0": 0, "to_1": 0, "tol": 1e-12, "note": "bound cleanup after x * sx + mx; not lattice snapping"}}
- botorch: "0.16.1"
- bo_gp_sha: "60e6328236e745b3d34dc8cd704bb72888ae5d15"
- loo_rms_z: {"V1": 0.4268, "E1": 0.7727}
- noise_raw: {"V1": 14949.051609849952, "E1": 750721.1138779742}
- predictions: "waves/methods_E_EMU_house_s1_s4_r1/predictions.csv"
- graded_at: "2026-11-24T08:06:57+00:00"
- n_train: 56
- n_hv: 55
- cumulative_hv: 132820832401166.19
- gain: 32608905352634.72
- gain_tau_joint: null
- would_stop_joint: false
- gain_tau_marginal: null
- would_stop_marginal: false
- joint_vs_marginal: {"ratio_joint_over_marginal": null, "agree": true, "fires": {"joint": false, "marginal": false}}
- first_fire_round: {"tau_joint": null, "tau_marginal": null}
- n_outside_ref: 0
- violations: ["methods_E_EMU_house_s1_s4_r1:3"]
- suspects: []
- r2_flag: false
- r2_max_mwh: 177.94500644458446
- calibration: {"V1": {"mean_z": 0.013, "rms_z": 0.179, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}, "E1": {"mean_z": -0.022, "rms_z": 0.109, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}}
- C2_review: false
- C3_review: false
- halt: null
- decision: "graded (record_only)"
- qnehvi_seconds: 3.8
- r1_shared_designs_with_seed: {"0": 4, "1": 4, "2": 4, "3": 4}
- designs (MW per site ['110', '140', '146', '163', '270', '274']):
    - [47.480, 0.000, 0.000, 185.400, 579.000, 0.000]
    - [0.000, 250.600, 162.784, 185.400, 579.000, 746.400]
    - [338.600, 0.000, 0.000, 185.400, 579.000, 0.000]
    - [0.000, 0.000, 0.000, 185.400, 579.000, 746.400]
    - [99.751, 250.600, 213.547, 185.400, 579.000, 746.400]
    - [0.000, 250.600, 0.000, 185.400, 579.000, 746.400]
    - [0.000, 0.000, 0.000, 185.400, 0.000, 746.400]
    - [0.000, 0.000, 0.000, 185.400, 579.000, 453.420]
- realized Y (['V1', 'E1']):
    - [3.33206e+06, 8.09352e+09]
    - [1.45314e+06, 8.13766e+09]
    - [2.72225e+06, 8.10904e+09]
    - [2.04066e+06, 8.11858e+09]
    - [1.24838e+06, 8.15074e+09]
    - [1.70977e+06, 8.1256e+09]
    - [2.99607e+06, 8.10398e+09]
    - [2.43711e+06, 8.11441e+09]
<!-- END r1 -->

<!-- BEGIN r2 -->
## Round 2 (methods_E_EMU_house_s1_s4_r2)
- proposed_at: "2026-11-24T08:07:05+00:00"
- wave: "methods_E_EMU_house_s1_s4_r2"
- acq: "qnehvi"
- acq_seed: 20261408
- guardrail_mode: "constrain"
- settings: {"mc_samples": 128, "num_restarts": 20, "raw_samples": 512, "alpha": 0.0, "prune_baseline": true, "sequential": true, "fast_mode": false, "constraint": "shed <= 1.0 MWh (GP on the accumulated R1 column)", "guardrail_mode": "constrain", "seed": 20261408, "dtype": "float64", "bound_snaps": {"to_0": 0, "to_1": 0, "tol": 1e-12, "note": "bound cleanup after x * sx + mx; not lattice snapping"}}
- botorch: "0.16.1"
- bo_gp_sha: "60e6328236e745b3d34dc8cd704bb72888ae5d15"
- loo_rms_z: {"V1": 0.3772, "E1": 0.7296}
- noise_raw: {"V1": 14852.939759178093, "E1": 783052.6636612387}
- predictions: "waves/methods_E_EMU_house_s1_s4_r2/predictions.csv"
- graded_at: "2026-11-24T08:07:05+00:00"
- n_train: 64
- n_hv: 63
- cumulative_hv: 138326698748103.86
- gain: 5505866346937.672
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
- r2_max_mwh: 175.36432923692678
- calibration: {"V1": {"mean_z": 0.071, "rms_z": 0.289, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}, "E1": {"mean_z": 0.157, "rms_z": 0.202, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}}
- C2_review: false
- C3_review: false
- halt: null
- decision: "graded (record_only)"
- qnehvi_seconds: 7.1
- designs (MW per site ['110', '140', '146', '163', '270', '274']):
    - [0.000, 250.600, 0.000, 185.400, 579.000, 65.974]
    - [0.000, 0.000, 0.000, 181.489, 579.000, 0.000]
    - [0.000, 250.600, 73.774, 185.400, 579.000, 746.400]
    - [134.488, 0.000, 0.000, 185.400, 579.000, 0.000]
    - [0.000, 0.000, 0.000, 185.400, 154.511, 746.400]
    - [307.661, 250.600, 20.675, 185.400, 579.000, 746.400]
    - [337.777, 250.600, 130.128, 185.400, 579.000, 746.400]
    - [0.000, 250.600, 0.000, 185.400, 579.000, 0.000]
- realized Y (['V1', 'E1']):
    - [2.81913e+06, 8.10807e+09]
    - [3.44647e+06, 8.09142e+09]
    - [1.56806e+06, 8.13163e+09]
    - [3.13739e+06, 8.09889e+09]
    - [2.67605e+06, 8.11115e+09]
    - [1.3747e+06, 8.14534e+09]
    - [1.17754e+06, 8.15724e+09]
    - [2.97078e+06, 8.10517e+09]
<!-- END r2 -->

<!-- BEGIN r3 -->
## Round 3 (methods_E_EMU_house_s1_s4_r3)
- proposed_at: "2026-11-24T08:07:13+00:00"
- wave: "methods_E_EMU_house_s1_s4_r3"
- acq: "qnehvi"
- acq_seed: 20261409
- guardrail_mode: "constrain"
- settings: {"mc_samples": 128, "num_restarts": 20, "raw_samples": 512, "alpha": 0.0, "prune_baseline": true, "sequential": true, "fast_mode": false, "constraint": "shed <= 1.0 MWh (GP on the accumulated R1 column)", "guardrail_mode": "constrain", "seed": 20261409, "dtype": "float64", "bound_snaps": {"to_0": 0, "to_1": 0, "tol": 1e-12, "note": "bound cleanup after x * sx + mx; not lattice snapping"}}
- botorch: "0.16.1"
- bo_gp_sha: "60e6328236e745b3d34dc8cd704bb72888ae5d15"
- loo_rms_z: {"V1": 0.3541, "E1": 0.7369}
- noise_raw: {"V1": 15301.363900461187, "E1": 815478.2148006173}
- predictions: "waves/methods_E_EMU_house_s1_s4_r3/predictions.csv"
- graded_at: "2026-11-24T08:07:14+00:00"
- n_train: 72
- n_hv: 71
- cumulative_hv: 139984956576918.83
- gain: 1658257828814.9688
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
- r2_max_mwh: 171.0933064129256
- calibration: {"V1": {"mean_z": -0.139, "rms_z": 0.185, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}, "E1": {"mean_z": -0.148, "rms_z": 0.418, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}}
- C2_review: false
- C3_review: false
- halt: null
- decision: "graded (record_only)"
- qnehvi_seconds: 7.3
- designs (MW per site ['110', '140', '146', '163', '270', '274']):
    - [0.000, 83.736, 0.000, 185.400, 579.000, 746.400]
    - [0.000, 0.000, 0.000, 0.000, 579.000, 746.400]
    - [0.000, 0.000, 0.000, 95.080, 579.000, 0.000]
    - [338.600, 0.000, 0.000, 0.000, 0.000, 746.400]
    - [0.000, 0.000, 268.000, 185.400, 0.000, 746.400]
    - [47.978, 250.600, 189.179, 185.400, 579.000, 746.400]
    - [0.000, 250.600, 0.000, 185.400, 0.000, 746.400]
    - [338.600, 0.000, 0.000, 185.400, 0.000, 746.400]
- realized Y (['V1', 'E1']):
    - [1.88556e+06, 8.1216e+09]
    - [2.33272e+06, 8.1174e+09]
    - [3.66021e+06, 8.09031e+09]
    - [2.77262e+06, 8.10934e+09]
    - [2.58998e+06, 8.11747e+09]
    - [1.34095e+06, 8.14325e+09]
    - [2.58023e+06, 8.11378e+09]
    - [2.45941e+06, 8.11673e+09]
<!-- END r3 -->

<!-- BEGIN r4 -->
## Round 4 (methods_E_EMU_house_s1_s4_r4)
- proposed_at: "2026-11-24T08:07:23+00:00"
- wave: "methods_E_EMU_house_s1_s4_r4"
- acq: "qnehvi"
- acq_seed: 20261410
- guardrail_mode: "constrain"
- settings: {"mc_samples": 128, "num_restarts": 20, "raw_samples": 512, "alpha": 0.0, "prune_baseline": true, "sequential": true, "fast_mode": false, "constraint": "shed <= 1.0 MWh (GP on the accumulated R1 column)", "guardrail_mode": "constrain", "seed": 20261410, "dtype": "float64", "bound_snaps": {"to_0": 0, "to_1": 0, "tol": 1e-12, "note": "bound cleanup after x * sx + mx; not lattice snapping"}}
- botorch: "0.16.1"
- bo_gp_sha: "60e6328236e745b3d34dc8cd704bb72888ae5d15"
- loo_rms_z: {"V1": 0.3264, "E1": 0.7307}
- noise_raw: {"V1": 15287.822954172841, "E1": 817483.633484924}
- predictions: "waves/methods_E_EMU_house_s1_s4_r4/predictions.csv"
- graded_at: "2026-11-24T08:07:23+00:00"
- n_train: 80
- n_hv: 79
- cumulative_hv: 141327750202078.44
- gain: 1342793625159.6094
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
- r2_max_mwh: 187.16141491448113
- calibration: {"V1": {"mean_z": 0.015, "rms_z": 0.178, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}, "E1": {"mean_z": 0.098, "rms_z": 0.276, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}}
- C2_review: false
- C3_review: false
- halt: null
- decision: "graded (record_only)"
- qnehvi_seconds: 7.6
- designs (MW per site ['110', '140', '146', '163', '270', '274']):
    - [0.000, 0.000, 0.000, 185.400, 579.000, 237.199]
    - [0.000, 0.000, 0.000, 185.400, 579.000, 167.049]
    - [338.600, 0.000, 0.000, 185.400, 579.000, 746.400]
    - [205.419, 250.600, 229.152, 185.400, 579.000, 746.400]
    - [0.000, 250.600, 116.044, 185.400, 579.000, 746.400]
    - [0.000, 0.000, 0.000, 185.400, 579.000, 370.036]
    - [0.000, 250.600, 34.959, 185.400, 579.000, 746.400]
    - [0.000, 0.000, 0.000, 185.400, 579.000, 572.905]
- realized Y (['V1', 'E1']):
    - [2.88274e+06, 8.10578e+09]
    - [3.04265e+06, 8.10185e+09]
    - [1.63963e+06, 8.13102e+09]
    - [1.12986e+06, 8.15972e+09]
    - [1.5104e+06, 8.13509e+09]
    - [2.60046e+06, 8.11173e+09]
    - [1.64256e+06, 8.12848e+09]
    - [2.23458e+06, 8.11683e+09]
<!-- END r4 -->
