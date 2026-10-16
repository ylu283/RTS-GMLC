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
- threshold: 7.47225068184712e+16
- decision: proposed
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
<!-- END r2 -->
