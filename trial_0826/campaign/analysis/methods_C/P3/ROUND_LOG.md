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
- threshold: 7.123010611496081e+16
- decision: proposed
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
<!-- END r1 -->
