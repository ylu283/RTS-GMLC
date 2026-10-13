# methods_C arm N1 — ROUND_LOG (prompt 35; acq = qnehvi, base = ['stage2_C_n0', 'stage2_C_n0b'], seed_id = 4)

Ledger: `analysis/methods_C/N1/ledger.json`. stop_rule = record_only: the rule is
graded and logged (would_stop, gain in tau units) but never acted on;
every arm runs to hard_cap = 4. Acquisition jobs never
submit (--no-submit); Kay submits from bastion via submit_ready.sh.
Stop NOW: `touch analysis/methods_C/N1/STOP_N1` on the CRC clone, then qdel the
arm's JIDs from methods_C/PROGRESS.md.

<!-- BEGIN r1 -->
## Round 1 (methods_C_N1_r1)
- proposed_at: 2026-10-13T00:24:59+00:00
- acq: qnehvi
- acq_seed: 20261407
- bo_gp_sha: 60e6328236e745b3d34dc8cd704bb72888ae5d15
- botorch: 0.16.1
- predictions: waves/methods_C_N1_r1/predictions.csv
- threshold: 5.262996664950399e+16
- decision: proposed
- designs (omega, tiers ['nuclear', 'pv', 'tail', 'wind_122', 'wind_303', 'wind_317']):
    - [0.05000, 0.16875, 0.52500, 0.05000, 1.00000, 0.05000]
    - [0.05000, 1.00000, 0.52500, 0.40625, 0.64375, 1.00000]
    - [0.05000, 0.05000, 1.00000, 0.64375, 1.00000, 0.05000]
    - [0.05000, 1.00000, 1.00000, 0.64375, 1.00000, 0.88125]
    - [0.05000, 1.00000, 0.05000, 0.05000, 0.52500, 1.00000]
    - [0.05000, 1.00000, 1.00000, 1.00000, 1.00000, 0.05000]
    - [0.05000, 1.00000, 0.05000, 0.05000, 1.00000, 0.05000]
    - [0.05000, 0.05000, 1.00000, 0.52500, 1.00000, 0.88125]
<!-- END r1 -->
