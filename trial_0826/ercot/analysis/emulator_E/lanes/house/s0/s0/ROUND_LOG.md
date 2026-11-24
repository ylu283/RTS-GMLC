# methods_E arm qnehvi seed_id 0 — ROUND_LOG (prompt 55; acq = qnehvi, base = ['n0_E'] nav prefix n0 = 48, objectives = ['V1', 'E1'])

Ledger: `lanes/house/s0/s0/ledger.json`. stop_rule = record_only: gain_k and
would_stop_k = (gain_k < tau) AND (gain_{k-1} < tau) are graded and logged under tau_joint
(headline) and tau_marginal (recorded) with the joint-vs-marginal sensitivity column; the
rule never halts; every lane runs to hard_cap = 4. tau_joint = 0, tau_marginal = 0 — ZERO: the stop rule is budget-cap-only and the cap governs (plan 3).
E-D5 OPEN: see README.md for the two readings of a fire. Halts ONLY per plan 1.2/1.3
(HALT_FOR_DECISION.md). Acquisition jobs never submit; Kay submits via submit_ready_E.sh.
Stop NOW: `touch lanes/house/s0/s0/STOP` on the CRC clone, then qdel the lane's JIDs.

<!-- BEGIN r1 -->
## Round 1 (methods_E_EMU_house_s0_s0_r1)
- proposed_at: "2026-11-24T08:04:18+00:00"
- wave: "methods_E_EMU_house_s0_s0_r1"
- acq: "qnehvi"
- acq_seed: 20261007
- guardrail_mode: "monitor"
- settings: {"mc_samples": 128, "num_restarts": 20, "raw_samples": 512, "alpha": 0.0, "prune_baseline": true, "sequential": true, "fast_mode": false, "constraint": "none", "guardrail_mode": "monitor", "seed": 20261007, "dtype": "float64", "bound_snaps": {"to_0": 0, "to_1": 1, "tol": 1e-12, "note": "bound cleanup after x * sx + mx; not lattice snapping"}}
- botorch: "0.16.1"
- bo_gp_sha: "60e6328236e745b3d34dc8cd704bb72888ae5d15"
- loo_rms_z: {"V1": 0.4268, "E1": 0.7727}
- noise_raw: {"V1": 14949.051609849952, "E1": 750721.1138779742}
- predictions: "waves/methods_E_EMU_house_s0_s0_r1/predictions.csv"
- graded_at: "2026-11-24T08:04:19+00:00"
- n_train: 56
- n_hv: 56
- cumulative_hv: 133366480777652.73
- gain: 33154553729121.266
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
- r2_max_mwh: 161.75535976993342
- calibration: {"V1": {"mean_z": -0.03, "rms_z": 0.131, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}, "E1": {"mean_z": -0.041, "rms_z": 0.105, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}}
- C2_review: false
- C3_review: false
- halt: null
- decision: "graded (record_only)"
- qnehvi_seconds: 5.4
- r1_shared_designs_with_seed: {"1": 4, "2": 5, "3": 4, "4": 4}
- designs (MW per site ['110', '140', '146', '163', '270', '274']):
    - [45.590, 0.000, 0.000, 185.400, 579.000, 0.000]
    - [0.000, 250.600, 158.408, 185.400, 579.000, 746.400]
    - [338.600, 0.000, 0.000, 185.400, 579.000, 0.000]
    - [0.000, 0.000, 0.000, 185.400, 579.000, 746.400]
    - [96.867, 250.600, 214.118, 185.400, 579.000, 746.400]
    - [0.000, 250.600, 0.000, 185.400, 579.000, 746.400]
    - [0.000, 250.600, 0.000, 185.400, 579.000, 0.000]
    - [0.000, 0.000, 0.000, 185.400, 0.000, 746.400]
- realized Y (['V1', 'E1']):
    - [3.33247e+06, 8.09368e+09]
    - [1.45098e+06, 8.13786e+09]
    - [2.71506e+06, 8.10829e+09]
    - [2.03789e+06, 8.11834e+09]
    - [1.25899e+06, 8.14897e+09]
    - [1.7183e+06, 8.12603e+09]
    - [2.97273e+06, 8.10434e+09]
    - [2.9964e+06, 8.10464e+09]
<!-- END r1 -->

<!-- BEGIN r2 -->
## Round 2 (methods_E_EMU_house_s0_s0_r2)
- proposed_at: "2026-11-24T08:04:25+00:00"
- wave: "methods_E_EMU_house_s0_s0_r2"
- acq: "qnehvi"
- acq_seed: 20261008
- guardrail_mode: "monitor"
- settings: {"mc_samples": 128, "num_restarts": 20, "raw_samples": 512, "alpha": 0.0, "prune_baseline": true, "sequential": true, "fast_mode": false, "constraint": "none", "guardrail_mode": "monitor", "seed": 20261008, "dtype": "float64", "bound_snaps": {"to_0": 0, "to_1": 0, "tol": 1e-12, "note": "bound cleanup after x * sx + mx; not lattice snapping"}}
- botorch: "0.16.1"
- bo_gp_sha: "60e6328236e745b3d34dc8cd704bb72888ae5d15"
- loo_rms_z: {"V1": 0.3742, "E1": 0.7424}
- noise_raw: {"V1": 14959.931161208044, "E1": 800227.657417711}
- predictions: "waves/methods_E_EMU_house_s0_s0_r2/predictions.csv"
- graded_at: "2026-11-24T08:04:26+00:00"
- n_train: 64
- n_hv: 64
- cumulative_hv: 138813020248573.53
- gain: 5446539470920.797
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
- r2_max_mwh: 189.97096847928813
- calibration: {"V1": {"mean_z": 0.092, "rms_z": 0.276, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}, "E1": {"mean_z": 0.142, "rms_z": 0.543, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}}
- C2_review: false
- C3_review: false
- halt: null
- decision: "graded (record_only)"
- qnehvi_seconds: 5.7
- designs (MW per site ['110', '140', '146', '163', '270', '274']):
    - [0.000, 0.000, 0.000, 167.308, 579.000, 0.000]
    - [139.839, 0.000, 0.000, 185.400, 579.000, 0.000]
    - [0.000, 0.000, 0.000, 185.400, 579.000, 465.635]
    - [0.000, 250.600, 70.673, 185.400, 579.000, 746.400]
    - [202.518, 250.600, 206.392, 185.400, 579.000, 746.400]
    - [338.600, 250.600, 6.851, 185.400, 579.000, 746.400]
    - [0.000, 86.365, 0.000, 185.400, 579.000, 746.400]
    - [0.000, 0.000, 0.000, 185.400, 353.326, 746.400]
- realized Y (['V1', 'E1']):
    - [3.48332e+06, 8.09195e+09]
    - [3.13055e+06, 8.09949e+09]
    - [2.41189e+06, 8.11483e+09]
    - [1.57731e+06, 8.13039e+09]
    - [1.15026e+06, 8.15771e+09]
    - [1.40784e+06, 8.14441e+09]
    - [1.88209e+06, 8.12204e+09]
    - [2.31147e+06, 8.11807e+09]
<!-- END r2 -->

<!-- BEGIN r3 -->
## Round 3 (methods_E_EMU_house_s0_s0_r3)
- proposed_at: "2026-11-24T08:04:34+00:00"
- wave: "methods_E_EMU_house_s0_s0_r3"
- acq: "qnehvi"
- acq_seed: 20261009
- guardrail_mode: "monitor"
- settings: {"mc_samples": 128, "num_restarts": 20, "raw_samples": 512, "alpha": 0.0, "prune_baseline": true, "sequential": true, "fast_mode": false, "constraint": "none", "guardrail_mode": "monitor", "seed": 20261009, "dtype": "float64", "bound_snaps": {"to_0": 7, "to_1": 0, "tol": 1e-12, "note": "bound cleanup after x * sx + mx; not lattice snapping"}}
- botorch: "0.16.1"
- bo_gp_sha: "60e6328236e745b3d34dc8cd704bb72888ae5d15"
- loo_rms_z: {"V1": 0.3604, "E1": 0.7633}
- noise_raw: {"V1": 15368.708137071519, "E1": 839501.1344876197}
- predictions: "waves/methods_E_EMU_house_s0_s0_r3/predictions.csv"
- graded_at: "2026-11-24T08:04:35+00:00"
- n_train: 72
- n_hv: 72
- cumulative_hv: 140391349720414.1
- gain: 1578329471840.5625
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
- r2_max_mwh: 210.53598171812786
- calibration: {"V1": {"mean_z": -0.012, "rms_z": 0.154, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}, "E1": {"mean_z": -0.035, "rms_z": 0.198, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}}
- C2_review: false
- C3_review: false
- halt: null
- decision: "graded (record_only)"
- qnehvi_seconds: 6.5
- designs (MW per site ['110', '140', '146', '163', '270', '274']):
    - [58.250, 250.600, 171.035, 185.400, 579.000, 746.400]
    - [0.000, 0.000, 0.000, 185.400, 579.000, 380.272]
    - [263.282, 0.000, 0.000, 185.400, 579.000, 0.000]
    - [338.600, 0.000, 0.000, 185.400, 0.000, 746.400]
    - [338.600, 0.000, 0.000, 0.000, 0.000, 746.400]
    - [0.000, 0.000, 0.000, 0.000, 579.000, 746.400]
    - [92.863, 0.000, 0.000, 185.400, 579.000, 0.000]
    - [0.000, 0.000, 0.000, 185.400, 462.197, 0.000]
- realized Y (['V1', 'E1']):
    - [1.34544e+06, 8.14389e+09]
    - [2.57407e+06, 8.11203e+09]
    - [2.86544e+06, 8.10532e+09]
    - [2.45702e+06, 8.11668e+09]
    - [2.77238e+06, 8.1101e+09]
    - [2.33652e+06, 8.11726e+09]
    - [3.23581e+06, 8.09654e+09]
    - [3.67059e+06, 8.09138e+09]
<!-- END r3 -->

<!-- BEGIN r4 -->
## Round 4 (methods_E_EMU_house_s0_s0_r4)
- proposed_at: "2026-11-24T08:04:44+00:00"
- wave: "methods_E_EMU_house_s0_s0_r4"
- acq: "qnehvi"
- acq_seed: 20261010
- guardrail_mode: "monitor"
- settings: {"mc_samples": 128, "num_restarts": 20, "raw_samples": 512, "alpha": 0.0, "prune_baseline": true, "sequential": true, "fast_mode": false, "constraint": "none", "guardrail_mode": "monitor", "seed": 20261010, "dtype": "float64", "bound_snaps": {"to_0": 4, "to_1": 0, "tol": 1e-12, "note": "bound cleanup after x * sx + mx; not lattice snapping"}}
- botorch: "0.16.1"
- bo_gp_sha: "60e6328236e745b3d34dc8cd704bb72888ae5d15"
- loo_rms_z: {"V1": 0.3428, "E1": 0.743}
- noise_raw: {"V1": 15403.797085569731, "E1": 815193.797729769}
- predictions: "waves/methods_E_EMU_house_s0_s0_r4/predictions.csv"
- graded_at: "2026-11-24T08:04:45+00:00"
- n_train: 80
- n_hv: 80
- cumulative_hv: 141433026348496.94
- gain: 1041676628082.8438
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
- r2_max_mwh: 191.38874043592875
- calibration: {"V1": {"mean_z": -0.012, "rms_z": 0.294, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}, "E1": {"mean_z": 0.174, "rms_z": 0.359, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}}
- C2_review: false
- C3_review: false
- halt: null
- decision: "graded (record_only)"
- qnehvi_seconds: 8.5
- designs (MW per site ['110', '140', '146', '163', '270', '274']):
    - [135.653, 250.600, 224.909, 185.400, 579.000, 746.400]
    - [0.000, 0.000, 268.000, 185.400, 0.000, 746.400]
    - [338.600, 0.000, 0.000, 185.400, 579.000, 746.400]
    - [0.000, 250.600, 33.952, 185.400, 579.000, 746.400]
    - [184.750, 0.000, 0.000, 185.400, 579.000, 0.000]
    - [0.000, 0.000, 0.000, 66.752, 579.000, 0.000]
    - [0.000, 250.600, 113.003, 185.400, 579.000, 746.400]
    - [0.000, 0.000, 0.000, 185.400, 579.000, 589.257]
- realized Y (['V1', 'E1']):
    - [1.19356e+06, 8.154e+09]
    - [2.59031e+06, 8.1163e+09]
    - [1.64645e+06, 8.1314e+09]
    - [1.64228e+06, 8.12841e+09]
    - [3.03046e+06, 8.10238e+09]
    - [3.72739e+06, 8.09107e+09]
    - [1.51104e+06, 8.13428e+09]
    - [2.22121e+06, 8.11715e+09]
<!-- END r4 -->
