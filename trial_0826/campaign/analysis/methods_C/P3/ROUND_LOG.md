# methods_C arm P3 — ROUND_LOG (prompt 35; acq = qparego, base = ['methods_C_S3_n0'], seed_id = 3)

Ledger: `analysis/methods_C/P3/ledger.json`. stop_rule = record_only: the rule is
graded and logged (would_stop, gain in tau units) but never acted on;
every arm runs to hard_cap = 4. Acquisition jobs never
submit (--no-submit); Kay submits from bastion via submit_ready.sh.
Stop NOW: `touch analysis/methods_C/P3/STOP_P3` on the CRC clone, then qdel the
arm's JIDs from methods_C/PROGRESS.md.

<!-- BEGIN r1 -->
## Round 1 (methods_C_P3_r1)
- proposed_at: 2026-10-15T03:22:27+00:00
- acq: qparego
- acq_seed: 20261307
- bo_gp_sha: 60e6328236e745b3d34dc8cd704bb72888ae5d15
- predictions: waves/methods_C_P3_r1/predictions.csv
- graded_at: 2026-10-16T03:35:06+00:00
- cumulative_hv: 1.6166270068560238e+18
- gain: 5.482280395382323e+16
- gain_tau: 0.769657760516919
- threshold: 7.123010611496081e+16
- would_stop: False
- n_outside_ref: 3
- decision: graded (record_only) -> r2
- weights (8 x M, Dirichlet(1) draws):
    - [0.2949, 0.1264, 0.5787]
    - [0.1125, 0.5186, 0.3689]
    - [0.6594, 0.2028, 0.1378]
    - [0.4276, 0.4433, 0.1291]
    - [0.1332, 0.8474, 0.0194]
    - [0.3740, 0.4937, 0.1323]
    - [0.8382, 0.0061, 0.1557]
    - [0.1500, 0.8045, 0.0456]
- designs (omega, tiers ['nuclear', 'pv', 'tail', 'wind_122', 'wind_303', 'wind_317']):
    - [0.05000, 0.05000, 0.88125, 0.05000, 0.05000, 0.40625]
    - [0.05000, 0.40625, 1.00000, 0.52500, 0.52500, 0.52500]
    - [0.05000, 1.00000, 0.05000, 0.88125, 1.00000, 0.05000]
    - [0.28750, 1.00000, 1.00000, 0.40625, 0.64375, 0.76250]
    - [1.00000, 1.00000, 0.76250, 0.88125, 0.64375, 0.76250]
    - [0.52500, 0.16875, 1.00000, 0.28750, 0.64375, 1.00000]
    - [0.05000, 1.00000, 0.05000, 0.76250, 0.28750, 0.76250]
    - [1.00000, 1.00000, 1.00000, 0.52500, 0.88125, 1.00000]
- calibration z-stats: {"load_shed_mwh": {"mean_z": -0.029, "rms_z": 0.475, "cov95": 8}, "true_curtailment_mwh": {"mean_z": 0.659, "rms_z": 1.661, "cov95": 7}, "total_cost_less_synthetic_usd": {"mean_z": -0.069, "rms_z": 0.984, "cov95": 8}}
<!-- END r1 -->

<!-- BEGIN r2 -->
## Round 2 (methods_C_P3_r2)
- proposed_at: 2026-10-16T03:48:36+00:00
- acq: qparego
- acq_seed: 20261308
- bo_gp_sha: 60e6328236e745b3d34dc8cd704bb72888ae5d15
- predictions: waves/methods_C_P3_r2/predictions.csv
- graded_at: 2026-10-17T22:37:09+00:00
- cumulative_hv: 1.7078245879188093e+18
- gain: 9.119758106278554e+16
- gain_tau: 1.2803235322378785
- threshold: 7.123010611496081e+16
- would_stop: False
- n_outside_ref: 5
- decision: graded (record_only) -> r3
- weights (8 x M, Dirichlet(1) draws):
    - [0.2241, 0.6053, 0.1706]
    - [0.5306, 0.4546, 0.0148]
    - [0.0862, 0.0292, 0.8846]
    - [0.3030, 0.4689, 0.2281]
    - [0.0473, 0.8954, 0.0573]
    - [0.6142, 0.1658, 0.2200]
    - [0.3895, 0.2249, 0.3856]
    - [0.5308, 0.1738, 0.2954]
- designs (omega, tiers ['nuclear', 'pv', 'tail', 'wind_122', 'wind_303', 'wind_317']):
    - [0.05000, 1.00000, 0.76250, 0.88125, 0.52500, 0.88125]
    - [0.76250, 1.00000, 0.28750, 0.88125, 0.88125, 1.00000]
    - [0.05000, 0.05000, 0.05000, 0.05000, 0.05000, 0.05000]
    - [0.05000, 1.00000, 0.52500, 0.64375, 0.40625, 1.00000]
    - [1.00000, 0.76250, 0.52500, 0.64375, 0.76250, 0.76250]
    - [0.05000, 1.00000, 0.64375, 0.52500, 1.00000, 0.28750]
    - [0.05000, 0.28750, 0.88125, 0.40625, 1.00000, 0.28750]
    - [0.05000, 0.05000, 0.05000, 0.64375, 1.00000, 0.05000]
- calibration z-stats: {"load_shed_mwh": {"mean_z": 0.545, "rms_z": 1.88, "cov95": 7}, "true_curtailment_mwh": {"mean_z": 0.98, "rms_z": 1.75, "cov95": 7}, "total_cost_less_synthetic_usd": {"mean_z": -0.163, "rms_z": 0.352, "cov95": 8}}
<!-- END r2 -->

<!-- BEGIN r3 -->
## Round 3 (methods_C_P3_r3)
- proposed_at: 2026-10-17T22:42:53+00:00
- acq: qparego
- acq_seed: 20261309
- bo_gp_sha: 60e6328236e745b3d34dc8cd704bb72888ae5d15
- predictions: waves/methods_C_P3_r3/predictions.csv
- graded_at: 2026-10-21T03:41:42+00:00
- cumulative_hv: 1.728579873429406e+18
- gain: 2.075528551059661e+16
- gain_tau: 0.2913836107038632
- threshold: 7.123010611496081e+16
- would_stop: False
- n_outside_ref: 5
- decision: graded (record_only) -> r4
- weights (8 x M, Dirichlet(1) draws):
    - [0.1605, 0.3139, 0.5256]
    - [0.0977, 0.6352, 0.2672]
    - [0.7478, 0.1602, 0.0921]
    - [0.3691, 0.5512, 0.0797]
    - [0.5402, 0.2615, 0.1983]
    - [0.8335, 0.1546, 0.0119]
    - [0.0679, 0.6433, 0.2889]
    - [0.0594, 0.7058, 0.2348]
- designs (omega, tiers ['nuclear', 'pv', 'tail', 'wind_122', 'wind_303', 'wind_317']):
    - [0.05000, 0.05000, 0.05000, 0.05000, 1.00000, 0.05000]
    - [0.05000, 1.00000, 1.00000, 0.76250, 0.88125, 0.05000]
    - [0.05000, 0.52500, 1.00000, 0.88125, 1.00000, 0.16875]
    - [0.40625, 1.00000, 1.00000, 0.05000, 1.00000, 1.00000]
    - [0.05000, 0.16875, 0.88125, 1.00000, 1.00000, 0.05000]
    - [0.05000, 1.00000, 1.00000, 1.00000, 1.00000, 0.28750]
    - [0.28750, 1.00000, 1.00000, 0.16875, 1.00000, 0.05000]
    - [0.28750, 1.00000, 1.00000, 0.76250, 1.00000, 0.05000]
- calibration z-stats: {"load_shed_mwh": {"mean_z": 0.009, "rms_z": 0.365, "cov95": 8}, "true_curtailment_mwh": {"mean_z": 0.288, "rms_z": 0.975, "cov95": 7}, "total_cost_less_synthetic_usd": {"mean_z": -0.829, "rms_z": 0.89, "cov95": 8}}
<!-- END r3 -->

<!-- BEGIN r4 -->
## Round 4 (methods_C_P3_r4)
- proposed_at: 2026-10-21T03:55:40+00:00
- acq: qparego
- acq_seed: 20261310
- bo_gp_sha: 60e6328236e745b3d34dc8cd704bb72888ae5d15
- predictions: waves/methods_C_P3_r4/predictions.csv
- graded_at: 2026-10-22T03:40:23+00:00
- cumulative_hv: 1.7499769887755884e+18
- gain: 2.13971153461824e+16
- gain_tau: 0.3003942646336766
- threshold: 7.123010611496081e+16
- would_stop: True
- n_outside_ref: 6
- decision: graded (record_only)
- weights (8 x M, Dirichlet(1) draws):
    - [0.0419, 0.5484, 0.4097]
    - [0.3320, 0.3824, 0.2856]
    - [0.3942, 0.4788, 0.1271]
    - [0.3612, 0.2882, 0.3506]
    - [0.3975, 0.5759, 0.0265]
    - [0.1146, 0.2491, 0.6363]
    - [0.0528, 0.8640, 0.0833]
    - [0.6604, 0.0046, 0.3350]
- designs (omega, tiers ['nuclear', 'pv', 'tail', 'wind_122', 'wind_303', 'wind_317']):
    - [0.05000, 0.52500, 0.76250, 0.05000, 1.00000, 0.64375]
    - [0.05000, 0.05000, 0.05000, 0.05000, 1.00000, 1.00000]
    - [0.05000, 1.00000, 0.05000, 0.40625, 1.00000, 1.00000]
    - [0.05000, 0.05000, 0.05000, 1.00000, 1.00000, 0.05000]
    - [0.64375, 0.64375, 1.00000, 1.00000, 1.00000, 1.00000]
    - [0.05000, 1.00000, 0.05000, 0.05000, 0.52500, 0.05000]
    - [0.28750, 0.88125, 0.64375, 0.52500, 1.00000, 1.00000]
    - [0.05000, 0.05000, 1.00000, 0.05000, 0.05000, 1.00000]
- calibration z-stats: {"load_shed_mwh": {"mean_z": 0.015, "rms_z": 0.406, "cov95": 8}, "true_curtailment_mwh": {"mean_z": 0.438, "rms_z": 0.624, "cov95": 8}, "total_cost_less_synthetic_usd": {"mean_z": -0.334, "rms_z": 0.511, "cov95": 8}}
<!-- END r4 -->
