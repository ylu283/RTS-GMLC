# methods_C arm P2 — ROUND_LOG (prompt 35; acq = qparego, base = ['methods_C_S2_n0'], seed_id = 2)

Ledger: `analysis/methods_C/P2/ledger.json`. stop_rule = record_only: the rule is
graded and logged (would_stop, gain in tau units) but never acted on;
every arm runs to hard_cap = 4. Acquisition jobs never
submit (--no-submit); Kay submits from bastion via submit_ready.sh.
Stop NOW: `touch analysis/methods_C/P2/STOP_P2` on the CRC clone, then qdel the
arm's JIDs from methods_C/PROGRESS.md.

<!-- BEGIN r1 -->
## Round 1 (methods_C_P2_r1)
- proposed_at: 2026-10-15T03:23:52+00:00
- acq: qparego
- acq_seed: 20261207
- bo_gp_sha: 60e6328236e745b3d34dc8cd704bb72888ae5d15
- predictions: waves/methods_C_P2_r1/predictions.csv
- graded_at: 2026-10-16T03:35:03+00:00
- cumulative_hv: 1.7427543049925827e+18
- gain: 1.701652109552594e+17
- gain_tau: 2.2772952648477665
- threshold: 7.47225068184712e+16
- would_stop: False
- n_outside_ref: 1
- decision: graded (record_only) -> r2
- weights (8 x M, Dirichlet(1) draws):
    - [0.1824, 0.5977, 0.2199]
    - [0.5029, 0.3297, 0.1675]
    - [0.6431, 0.2030, 0.1539]
    - [0.0351, 0.2779, 0.6871]
    - [0.4734, 0.2318, 0.2947]
    - [0.5285, 0.0630, 0.4085]
    - [0.1538, 0.6144, 0.2318]
    - [0.3774, 0.0238, 0.5987]
- designs (omega, tiers ['nuclear', 'pv', 'tail', 'wind_122', 'wind_303', 'wind_317']):
    - [0.52500, 1.00000, 0.76250, 1.00000, 0.52500, 0.28750]
    - [0.05000, 0.05000, 0.64375, 0.16875, 1.00000, 0.64375]
    - [0.05000, 0.05000, 0.05000, 0.76250, 0.05000, 1.00000]
    - [0.05000, 0.64375, 1.00000, 0.05000, 0.76250, 0.05000]
    - [0.05000, 0.05000, 0.05000, 0.05000, 0.64375, 0.76250]
    - [0.05000, 0.05000, 0.05000, 0.05000, 0.52500, 0.52500]
    - [0.05000, 1.00000, 0.40625, 0.05000, 0.88125, 1.00000]
    - [0.05000, 0.05000, 0.05000, 0.64375, 0.05000, 0.40625]
- calibration z-stats: {"load_shed_mwh": {"mean_z": 0.201, "rms_z": 0.667, "cov95": 8}, "true_curtailment_mwh": {"mean_z": 1.103, "rms_z": 1.26, "cov95": 7}, "total_cost_less_synthetic_usd": {"mean_z": -0.914, "rms_z": 0.974, "cov95": 8}}
<!-- END r1 -->

<!-- BEGIN r2 -->
## Round 2 (methods_C_P2_r2)
- proposed_at: 2026-10-16T03:48:34+00:00
- acq: qparego
- acq_seed: 20261208
- bo_gp_sha: 60e6328236e745b3d34dc8cd704bb72888ae5d15
- predictions: waves/methods_C_P2_r2/predictions.csv
- graded_at: 2026-10-17T22:37:07+00:00
- cumulative_hv: 1.7587376637431654e+18
- gain: 1.5983358750582784e+16
- gain_tau: 0.21390287118461263
- threshold: 7.47225068184712e+16
- would_stop: False
- n_outside_ref: 1
- decision: graded (record_only) -> r3
- weights (8 x M, Dirichlet(1) draws):
    - [0.7093, 0.1641, 0.1266]
    - [0.8105, 0.1262, 0.0633]
    - [0.0695, 0.3459, 0.5846]
    - [0.1882, 0.4099, 0.4019]
    - [0.6902, 0.0579, 0.2519]
    - [0.4752, 0.0564, 0.4684]
    - [0.2278, 0.4013, 0.3708]
    - [0.1118, 0.3761, 0.5121]
- designs (omega, tiers ['nuclear', 'pv', 'tail', 'wind_122', 'wind_303', 'wind_317']):
    - [0.05000, 0.05000, 0.16875, 0.40625, 1.00000, 0.88125]
    - [1.00000, 0.05000, 0.52500, 0.28750, 1.00000, 0.52500]
    - [0.05000, 0.52500, 0.52500, 0.05000, 1.00000, 0.52500]
    - [0.05000, 0.88125, 0.40625, 0.28750, 0.64375, 0.52500]
    - [0.05000, 0.05000, 1.00000, 0.05000, 1.00000, 0.88125]
    - [0.05000, 0.05000, 0.05000, 0.40625, 0.05000, 1.00000]
    - [0.05000, 0.76250, 0.40625, 0.16875, 0.64375, 0.76250]
    - [0.05000, 1.00000, 0.64375, 0.52500, 0.40625, 0.28750]
- calibration z-stats: {"load_shed_mwh": {"mean_z": -0.037, "rms_z": 0.309, "cov95": 8}, "true_curtailment_mwh": {"mean_z": 0.009, "rms_z": 0.56, "cov95": 8}, "total_cost_less_synthetic_usd": {"mean_z": -0.063, "rms_z": 0.386, "cov95": 8}}
<!-- END r2 -->

<!-- BEGIN r3 -->
## Round 3 (methods_C_P2_r3)
- proposed_at: 2026-10-17T22:42:52+00:00
- acq: qparego
- acq_seed: 20261209
- bo_gp_sha: 60e6328236e745b3d34dc8cd704bb72888ae5d15
- predictions: waves/methods_C_P2_r3/predictions.csv
- graded_at: 2026-10-21T03:41:41+00:00
- cumulative_hv: 1.788933400194263e+18
- gain: 3.01957364510976e+16
- gain_tau: 0.40410497100230175
- threshold: 7.47225068184712e+16
- would_stop: True
- n_outside_ref: 2
- decision: graded (record_only) -> r4
- weights (8 x M, Dirichlet(1) draws):
    - [0.8152, 0.0789, 0.1059]
    - [0.2915, 0.6474, 0.0611]
    - [0.4092, 0.3413, 0.2495]
    - [0.0105, 0.7010, 0.2885]
    - [0.7159, 0.2354, 0.0488]
    - [0.0701, 0.1411, 0.7888]
    - [0.6294, 0.2520, 0.1187]
    - [0.0102, 0.6152, 0.3745]
- designs (omega, tiers ['nuclear', 'pv', 'tail', 'wind_122', 'wind_303', 'wind_317']):
    - [0.05000, 0.05000, 0.05000, 1.00000, 0.40625, 0.76250]
    - [0.76250, 1.00000, 0.52500, 0.40625, 0.52500, 0.88125]
    - [0.05000, 1.00000, 0.28750, 0.28750, 0.64375, 0.88125]
    - [0.16875, 0.40625, 0.64375, 1.00000, 0.76250, 0.16875]
    - [1.00000, 0.16875, 0.64375, 0.64375, 1.00000, 0.28750]
    - [0.05000, 0.05000, 1.00000, 0.05000, 0.05000, 0.05000]
    - [0.05000, 1.00000, 0.64375, 0.28750, 0.76250, 0.88125]
    - [0.05000, 0.76250, 0.28750, 0.28750, 0.88125, 1.00000]
- calibration z-stats: {"load_shed_mwh": {"mean_z": 0.249, "rms_z": 1.189, "cov95": 7}, "true_curtailment_mwh": {"mean_z": 0.607, "rms_z": 2.078, "cov95": 7}, "total_cost_less_synthetic_usd": {"mean_z": 0.044, "rms_z": 0.49, "cov95": 8}}
<!-- END r3 -->

<!-- BEGIN r4 -->
## Round 4 (methods_C_P2_r4)
- proposed_at: 2026-10-21T03:55:37+00:00
- acq: qparego
- acq_seed: 20261210
- bo_gp_sha: 60e6328236e745b3d34dc8cd704bb72888ae5d15
- predictions: waves/methods_C_P2_r4/predictions.csv
- graded_at: 2026-10-22T03:40:22+00:00
- cumulative_hv: 1.8084153708870548e+18
- gain: 1.948197069279181e+16
- gain_tau: 0.2607242653156802
- threshold: 7.47225068184712e+16
- would_stop: True
- n_outside_ref: 4
- decision: graded (record_only)
- weights (8 x M, Dirichlet(1) draws):
    - [0.0089, 0.2913, 0.6998]
    - [0.6635, 0.2472, 0.0893]
    - [0.7793, 0.0160, 0.2047]
    - [0.2486, 0.1170, 0.6344]
    - [0.0386, 0.8306, 0.1308]
    - [0.6293, 0.3705, 0.0002]
    - [0.3419, 0.3689, 0.2892]
    - [0.4495, 0.4356, 0.1149]
- designs (omega, tiers ['nuclear', 'pv', 'tail', 'wind_122', 'wind_303', 'wind_317']):
    - [0.05000, 0.05000, 0.05000, 0.05000, 0.88125, 0.05000]
    - [0.05000, 0.05000, 0.40625, 0.76250, 0.64375, 0.64375]
    - [0.05000, 0.05000, 0.05000, 1.00000, 0.05000, 1.00000]
    - [0.05000, 0.05000, 0.05000, 0.05000, 0.05000, 0.40625]
    - [0.05000, 0.88125, 0.64375, 0.52500, 0.88125, 1.00000]
    - [0.88125, 1.00000, 0.76250, 1.00000, 0.76250, 0.76250]
    - [0.05000, 0.28750, 0.05000, 0.05000, 1.00000, 0.76250]
    - [0.05000, 0.76250, 0.05000, 1.00000, 0.64375, 0.88125]
- calibration z-stats: {"load_shed_mwh": {"mean_z": 0.283, "rms_z": 0.644, "cov95": 8}, "true_curtailment_mwh": {"mean_z": 0.372, "rms_z": 1.006, "cov95": 8}, "total_cost_less_synthetic_usd": {"mean_z": 0.075, "rms_z": 0.726, "cov95": 8}}
<!-- END r4 -->
