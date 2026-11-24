# methods_E arm qnehvi seed_id 3 — ROUND_LOG (prompt 55; acq = qnehvi, base = ['n0_E'] nav prefix n0 = 48, objectives = ['V1', 'E1'])

Ledger: `lanes/house/s0/s3/ledger.json`. stop_rule = record_only: gain_k and
would_stop_k = (gain_k < tau) AND (gain_{k-1} < tau) are graded and logged under tau_joint
(headline) and tau_marginal (recorded) with the joint-vs-marginal sensitivity column; the
rule never halts; every lane runs to hard_cap = 4. tau_joint = 0, tau_marginal = 0 — ZERO: the stop rule is budget-cap-only and the cap governs (plan 3).
E-D5 OPEN: see README.md for the two readings of a fire. Halts ONLY per plan 1.2/1.3
(HALT_FOR_DECISION.md). Acquisition jobs never submit; Kay submits via submit_ready_E.sh.
Stop NOW: `touch lanes/house/s0/s3/STOP` on the CRC clone, then qdel the lane's JIDs.

<!-- BEGIN r1 -->
## Round 1 (methods_E_EMU_house_s0_s3_r1)
- proposed_at: "2026-11-24T07:45:55+00:00"
- wave: "methods_E_EMU_house_s0_s3_r1"
- acq: "qnehvi"
- acq_seed: 20261307
- guardrail_mode: "monitor"
- settings: {"mc_samples": 128, "num_restarts": 20, "raw_samples": 512, "alpha": 0.0, "prune_baseline": true, "sequential": true, "fast_mode": false, "constraint": "none", "guardrail_mode": "monitor", "seed": 20261307, "dtype": "float64"}
- botorch: "0.16.1"
- bo_gp_sha: "60e6328236e745b3d34dc8cd704bb72888ae5d15"
- loo_rms_z: {"V1": 0.4268, "E1": 0.7727}
- noise_raw: {"V1": 14949.051609849952, "E1": 750721.1138779742}
- predictions: "waves/methods_E_EMU_house_s0_s3_r1/predictions.csv"
- graded_at: "2026-11-24T07:45:56+00:00"
- n_train: 56
- n_hv: 56
- cumulative_hv: 134179610644479.03
- gain: 33967683595947.562
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
- r2_max_mwh: 195.4514598148051
- calibration: {"V1": {"mean_z": -0.025, "rms_z": 0.202, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}, "E1": {"mean_z": -0.035, "rms_z": 0.138, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}}
- C2_review: false
- C3_review: false
- halt: null
- decision: "graded (record_only)"
- qnehvi_seconds: 4.1
- r1_shared_designs_with_seed: {"0": 4, "1": 4, "2": 4}
- designs (MW per site ['110', '140', '146', '163', '270', '274']):
    - [45.641, 0.000, 0.000, 185.400, 579.000, 0.000]
    - [0.000, 250.600, 161.119, 185.400, 579.000, 746.400]
    - [338.600, 0.000, 0.000, 185.400, 579.000, 0.000]
    - [0.000, 0.000, 0.000, 185.400, 579.000, 746.400]
    - [97.573, 250.600, 218.932, 185.400, 579.000, 746.400]
    - [0.000, 250.600, 0.000, 185.400, 579.000, 746.400]
    - [0.000, 0.000, 0.000, 185.400, 0.000, 746.400]
    - [0.000, 0.000, 0.000, 185.400, 258.556, 746.400]
- realized Y (['V1', 'E1']):
    - [3.33777e+06, 8.09448e+09]
    - [1.44814e+06, 8.13644e+09]
    - [2.71787e+06, 8.10849e+09]
    - [2.04019e+06, 8.11837e+09]
    - [1.24318e+06, 8.14993e+09]
    - [1.70406e+06, 8.12569e+09]
    - [2.99486e+06, 8.10398e+09]
    - [2.47304e+06, 8.11528e+09]
<!-- END r1 -->

<!-- BEGIN r2 -->
## Round 2 (methods_E_EMU_house_s0_s3_r2)
- proposed_at: "2026-11-24T07:46:00+00:00"
- wave: "methods_E_EMU_house_s0_s3_r2"
- acq: "qnehvi"
- acq_seed: 20261308
- guardrail_mode: "monitor"
- settings: {"mc_samples": 128, "num_restarts": 20, "raw_samples": 512, "alpha": 0.0, "prune_baseline": true, "sequential": true, "fast_mode": false, "constraint": "none", "guardrail_mode": "monitor", "seed": 20261308, "dtype": "float64"}
- botorch: "0.16.1"
- bo_gp_sha: "60e6328236e745b3d34dc8cd704bb72888ae5d15"
- loo_rms_z: {"V1": 0.3805, "E1": 0.7213}
- noise_raw: {"V1": 14807.868853924807, "E1": 773465.2375813284}
- predictions: "waves/methods_E_EMU_house_s0_s3_r2/predictions.csv"
- graded_at: "2026-11-24T07:46:01+00:00"
- n_train: 64
- n_hv: 64
- cumulative_hv: 139678525640060.44
- gain: 5498914995581.406
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
- r2_max_mwh: 172.38147470764264
- calibration: {"V1": {"mean_z": 0.096, "rms_z": 0.254, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}, "E1": {"mean_z": 0.163, "rms_z": 0.425, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}}
- C2_review: false
- C3_review: false
- halt: null
- decision: "graded (record_only)"
- qnehvi_seconds: 4.1
- designs (MW per site ['110', '140', '146', '163', '270', '274']):
    - [0.000, 0.000, 0.000, 144.249, 579.000, 0.000]
    - [0.000, 250.600, 0.000, 185.400, 579.000, 0.000]
    - [0.000, 250.600, 73.470, 185.400, 579.000, 746.400]
    - [0.000, 0.000, 0.000, 185.400, 579.000, 503.110]
    - [38.546, 250.600, 202.425, 185.400, 579.000, 746.400]
    - [129.444, 0.000, 0.000, 185.400, 579.000, 0.000]
    - [191.105, 250.600, 200.143, 185.400, 579.000, 746.400]
    - [0.000, 89.564, 0.000, 185.400, 579.000, 746.400]
- realized Y (['V1', 'E1']):
    - [3.53736e+06, 8.09091e+09]
    - [2.97522e+06, 8.1048e+09]
    - [1.57357e+06, 8.13175e+09]
    - [2.3427e+06, 8.11471e+09]
    - [1.35166e+06, 8.1437e+09]
    - [3.15108e+06, 8.09854e+09]
    - [1.16497e+06, 8.15761e+09]
    - [1.87923e+06, 8.1224e+09]
<!-- END r2 -->

<!-- BEGIN r3 -->
## Round 3 (methods_E_EMU_house_s0_s3_r3)
- proposed_at: "2026-11-24T07:46:07+00:00"
- wave: "methods_E_EMU_house_s0_s3_r3"
- acq: "qnehvi"
- acq_seed: 20261309
- guardrail_mode: "monitor"
- settings: {"mc_samples": 128, "num_restarts": 20, "raw_samples": 512, "alpha": 0.0, "prune_baseline": true, "sequential": true, "fast_mode": false, "constraint": "none", "guardrail_mode": "monitor", "seed": 20261309, "dtype": "float64"}
- botorch: "0.16.1"
- bo_gp_sha: "60e6328236e745b3d34dc8cd704bb72888ae5d15"
- loo_rms_z: {"V1": 0.3548, "E1": 0.7201}
- noise_raw: {"V1": 15883.502732954597, "E1": 791524.055886899}
- predictions: "waves/methods_E_EMU_house_s0_s3_r3/predictions.csv"
- graded_at: "2026-11-24T07:46:07+00:00"
- n_train: 72
- n_hv: 72
- cumulative_hv: 140370174447475.39
- gain: 691648807414.9531
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
- r2_max_mwh: 180.03284113391294
- calibration: {"V1": {"mean_z": -0.02, "rms_z": 0.168, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}, "E1": {"mean_z": -0.004, "rms_z": 0.212, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}}
- C2_review: false
- C3_review: false
- halt: null
- decision: "graded (record_only)"
- qnehvi_seconds: 4.4
- designs (MW per site ['110', '140', '146', '163', '270', '274']):
    - [0.000, 250.600, 0.000, 185.400, 0.000, 746.400]
    - [0.000, 0.000, 0.000, 66.110, 579.000, 0.000]
    - [0.000, 0.000, 0.000, 0.000, 579.000, 746.400]
    - [338.600, 0.000, 0.000, 0.000, 0.000, 746.400]
    - [338.600, 0.000, 0.000, 185.400, 0.000, 746.400]
    - [177.935, 0.000, 0.000, 185.400, 579.000, 0.000]
    - [338.600, 0.000, 0.000, 185.400, 579.000, 746.400]
    - [0.000, 0.000, 0.000, 185.400, 579.000, 0.000]
- realized Y (['V1', 'E1']):
    - [2.57694e+06, 8.11381e+09]
    - [3.73089e+06, 8.09079e+09]
    - [2.33669e+06, 8.11693e+09]
    - [2.77114e+06, 8.11002e+09]
    - [2.45812e+06, 8.11668e+09]
    - [3.04415e+06, 8.10099e+09]
    - [1.64012e+06, 8.13167e+09]
    - [3.43747e+06, 8.09245e+09]
<!-- END r3 -->

<!-- BEGIN r4 -->
## Round 4 (methods_E_EMU_house_s0_s3_r4)
- proposed_at: "2026-11-24T07:46:14+00:00"
- wave: "methods_E_EMU_house_s0_s3_r4"
- acq: "qnehvi"
- acq_seed: 20261310
- guardrail_mode: "monitor"
- settings: {"mc_samples": 128, "num_restarts": 20, "raw_samples": 512, "alpha": 0.0, "prune_baseline": true, "sequential": true, "fast_mode": false, "constraint": "none", "guardrail_mode": "monitor", "seed": 20261310, "dtype": "float64"}
- botorch: "0.16.1"
- bo_gp_sha: "60e6328236e745b3d34dc8cd704bb72888ae5d15"
- loo_rms_z: {"V1": 0.3311, "E1": 0.7051}
- noise_raw: {"V1": 15629.87949617628, "E1": 806421.2722282995}
- predictions: "waves/methods_E_EMU_house_s0_s3_r4/predictions.csv"
- graded_at: "2026-11-24T07:46:14+00:00"
- n_train: 80
- n_hv: 80
- cumulative_hv: 141968352238822.38
- gain: 1598177791346.9844
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
- r2_max_mwh: 176.4462510126214
- calibration: {"V1": {"mean_z": 0.005, "rms_z": 0.121, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}, "E1": {"mean_z": -0.033, "rms_z": 0.434, "cov95": 8, "n_abs_z_gt3": 0, "transform": "std"}}
- C2_review: false
- C3_review: false
- halt: null
- decision: "graded (record_only)"
- qnehvi_seconds: 5.4
- designs (MW per site ['110', '140', '146', '163', '270', '274']):
    - [267.497, 0.000, 0.000, 185.400, 579.000, 0.000]
    - [338.600, 0.000, 0.000, 185.400, 579.000, 39.371]
    - [0.000, 0.000, 0.000, 185.400, 579.000, 603.127]
    - [0.000, 250.600, 222.264, 185.400, 579.000, 746.400]
    - [0.000, 147.458, 0.000, 185.400, 579.000, 746.400]
    - [0.000, 0.000, 268.000, 185.400, 0.000, 746.400]
    - [0.000, 0.000, 0.000, 185.400, 579.000, 418.068]
    - [0.000, 250.600, 114.063, 185.400, 579.000, 746.400]
- realized Y (['V1', 'E1']):
    - [2.85176e+06, 8.10514e+09]
    - [2.63217e+06, 8.11134e+09]
    - [2.19061e+06, 8.11661e+09]
    - [1.39766e+06, 8.14007e+09]
    - [1.80196e+06, 8.12304e+09]
    - [2.58928e+06, 8.11666e+09]
    - [2.50135e+06, 8.11292e+09]
    - [1.50726e+06, 8.13432e+09]
<!-- END r4 -->
