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
- threshold: 7.123010611496081e+16
- decision: proposed
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
<!-- END r2 -->
