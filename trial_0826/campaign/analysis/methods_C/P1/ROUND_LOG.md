# methods_C arm P1 — ROUND_LOG (prompt 35; acq = qparego, base = ['stage2_C_n0', 'stage2_C_n0b'], seed_id = 0)

Ledger: `analysis/methods_C/P1/ledger.json`. stop_rule = record_only: the rule is
graded and logged (would_stop, gain in tau units) but never acted on;
every arm runs to hard_cap = 4. Acquisition jobs never
submit (--no-submit); Kay submits from bastion via submit_ready.sh.
Stop NOW: `touch analysis/methods_C/P1/STOP_P1` on the CRC clone, then qdel the
arm's JIDs from methods_C/PROGRESS.md.

<!-- BEGIN r1 -->
## Round 1 (bo_C_r1)
- proposed_at: 2026-10-06T20:28:58+00:00
- acq_seed: 20261007
- bo_gp_sha: 60e6328236e745b3d34dc8cd704bb72888ae5d15
- predictions: waves/bo_C_r1/predictions.csv
- graded_at: 2026-10-08T19:01:17+00:00
- cumulative_hv: 6.969242093952338e+17
- gain: 3.629705777052557e+16
- threshold: 5.262996664950399e+16
- n_outside_ref: 2
- decision: continue -> r2
- weights (8 x M, Dirichlet(1) draws):
    - [0.0668, 0.5906, 0.3426]
    - [0.5457, 0.0762, 0.3781]
    - [0.4472, 0.3438, 0.2090]
    - [0.4773, 0.3696, 0.1531]
    - [0.1098, 0.8071, 0.0830]
    - [0.5556, 0.1075, 0.3369]
    - [0.0434, 0.7953, 0.1613]
    - [0.4468, 0.0061, 0.5471]
- designs (omega, tiers ['nuclear', 'pv', 'tail', 'wind_122', 'wind_303', 'wind_317']):
    - [0.05000, 0.64375, 0.05000, 0.05000, 0.88125, 0.52500]
    - [0.05000, 0.28750, 0.88125, 0.28750, 0.76250, 0.64375]
    - [0.05000, 0.52500, 0.05000, 0.76250, 0.64375, 0.40625]
    - [0.76250, 1.00000, 0.52500, 0.88125, 0.40625, 0.64375]
    - [1.00000, 0.76250, 0.64375, 1.00000, 0.52500, 0.64375]
    - [0.05000, 0.52500, 0.52500, 0.16875, 0.64375, 0.76250]
    - [1.00000, 0.76250, 1.00000, 1.00000, 0.52500, 0.40625]
    - [0.05000, 0.40625, 0.76250, 0.05000, 0.64375, 0.52500]
- calibration z-stats: {"load_shed_mwh": {"mean_z": 0.031, "rms_z": 0.325, "cov95": 8}, "true_curtailment_mwh": {"mean_z": 0.285, "rms_z": 0.554, "cov95": 8}, "total_cost_less_synthetic_usd": {"mean_z": 0.392, "rms_z": 0.91, "cov95": 8}}
<!-- END r1 -->

<!-- BEGIN r2 -->
## Round 2 (bo_C_r2)
- proposed_at: 2026-10-08T19:30:14+00:00
- acq_seed: 20261008
- bo_gp_sha: 60e6328236e745b3d34dc8cd704bb72888ae5d15
- predictions: waves/bo_C_r2/predictions.csv
- graded_at: 2026-10-10T13:05:19+00:00
- cumulative_hv: 7.06104917466881e+17
- gain: 9180708071647232.0
- threshold: 5.262996664950399e+16
- n_outside_ref: 5
- decision: STOP — stopping rule: HV gain < threshold (5.263e+16) for 2 consecutive rounds (gains 3.62971e+16, 9.18071e+15)
- weights (8 x M, Dirichlet(1) draws):
    - [0.0300, 0.4085, 0.5615]
    - [0.6340, 0.3359, 0.0301]
    - [0.1662, 0.0765, 0.7572]
    - [0.5038, 0.3788, 0.1174]
    - [0.2215, 0.0615, 0.7169]
    - [0.6439, 0.2271, 0.1290]
    - [0.3527, 0.5201, 0.1272]
    - [0.6644, 0.0958, 0.2398]
- designs (omega, tiers ['nuclear', 'pv', 'tail', 'wind_122', 'wind_303', 'wind_317']):
    - [0.05000, 0.52500, 0.76250, 0.52500, 0.64375, 0.64375]
    - [1.00000, 0.76250, 0.16875, 0.52500, 0.88125, 1.00000]
    - [0.05000, 0.05000, 1.00000, 0.05000, 0.05000, 0.05000]
    - [1.00000, 0.88125, 1.00000, 0.64375, 1.00000, 0.16875]
    - [0.05000, 0.05000, 1.00000, 0.05000, 0.05000, 0.88125]
    - [0.05000, 0.28750, 1.00000, 0.52500, 0.52500, 1.00000]
    - [1.00000, 0.88125, 1.00000, 0.16875, 1.00000, 0.64375]
    - [0.05000, 0.05000, 1.00000, 0.40625, 0.88125, 0.88125]
- calibration z-stats: {"load_shed_mwh": {"mean_z": 0.475, "rms_z": 1.88, "cov95": 7}, "true_curtailment_mwh": {"mean_z": 0.924, "rms_z": 2.485, "cov95": 6}, "total_cost_less_synthetic_usd": {"mean_z": 0.051, "rms_z": 1.01, "cov95": 8}}
<!-- END r2 -->

<!-- BEGIN r3 -->
## Round 3 (methods_C_P1_r3)
- proposed_at: 2026-10-12T23:19:09+00:00
- acq: qparego
- acq_seed: 20261009
- bo_gp_sha: 60e6328236e745b3d34dc8cd704bb72888ae5d15
- predictions: waves/methods_C_P1_r3/predictions.csv
- graded_at: 2026-10-15T03:06:51+00:00
- cumulative_hv: 7.389927937274784e+17
- gain: 3.2887876260597376e+16
- gain_tau: 0.6248887915817695
- threshold: 5.262996664950399e+16
- would_stop: True
- n_outside_ref: 7
- decision: graded (record_only) -> r4
- weights (8 x M, Dirichlet(1) draws):
    - [0.6159, 0.2073, 0.1768]
    - [0.3697, 0.4499, 0.1805]
    - [0.0866, 0.1209, 0.7926]
    - [0.2955, 0.3348, 0.3697]
    - [0.6395, 0.1374, 0.2231]
    - [0.5805, 0.1383, 0.2812]
    - [0.0779, 0.2412, 0.6809]
    - [0.5406, 0.0896, 0.3698]
- designs (omega, tiers ['nuclear', 'pv', 'tail', 'wind_122', 'wind_303', 'wind_317']):
    - [0.05000, 0.76250, 0.28750, 0.76250, 1.00000, 0.05000]
    - [0.05000, 0.52500, 1.00000, 0.88125, 0.76250, 0.05000]
    - [0.05000, 0.05000, 0.05000, 0.05000, 0.05000, 0.05000]
    - [0.05000, 0.40625, 0.05000, 0.05000, 0.64375, 0.28750]
    - [0.05000, 0.28750, 0.40625, 0.64375, 1.00000, 0.05000]
    - [0.05000, 0.88125, 0.28750, 0.64375, 0.88125, 0.16875]
    - [0.05000, 0.05000, 0.05000, 0.05000, 0.05000, 0.40625]
    - [0.05000, 0.05000, 0.05000, 0.05000, 0.64375, 0.76250]
- calibration z-stats: {"load_shed_mwh": {"mean_z": 0.731, "rms_z": 1.706, "cov95": 7}, "true_curtailment_mwh": {"mean_z": 1.426, "rms_z": 2.008, "cov95": 5}, "total_cost_less_synthetic_usd": {"mean_z": -0.751, "rms_z": 0.829, "cov95": 8}}
<!-- END r3 -->

<!-- BEGIN r4 -->
## Round 4 (methods_C_P1_r4)
- proposed_at: 2026-10-15T03:21:07+00:00
- acq: qparego
- acq_seed: 20261010
- bo_gp_sha: 60e6328236e745b3d34dc8cd704bb72888ae5d15
- predictions: waves/methods_C_P1_r4/predictions.csv
- threshold: 5.262996664950399e+16
- decision: proposed
- weights (8 x M, Dirichlet(1) draws):
    - [0.8624, 0.1071, 0.0305]
    - [0.3642, 0.4985, 0.1373]
    - [0.2420, 0.2204, 0.5376]
    - [0.7040, 0.0772, 0.2188]
    - [0.0099, 0.3842, 0.6059]
    - [0.5934, 0.2423, 0.1643]
    - [0.5540, 0.2400, 0.2060]
    - [0.1085, 0.1760, 0.7155]
- designs (omega, tiers ['nuclear', 'pv', 'tail', 'wind_122', 'wind_303', 'wind_317']):
    - [1.00000, 0.05000, 0.28750, 0.28750, 1.00000, 0.40625]
    - [0.05000, 1.00000, 1.00000, 0.05000, 1.00000, 1.00000]
    - [0.05000, 0.05000, 0.05000, 0.05000, 0.88125, 0.05000]
    - [0.05000, 0.52500, 1.00000, 0.52500, 1.00000, 0.05000]
    - [0.05000, 0.05000, 0.05000, 1.00000, 0.28750, 0.05000]
    - [0.05000, 0.05000, 0.05000, 0.40625, 0.64375, 0.88125]
    - [0.05000, 1.00000, 1.00000, 1.00000, 0.05000, 0.28750]
    - [0.05000, 0.05000, 0.05000, 0.05000, 1.00000, 0.05000]
<!-- END r4 -->
