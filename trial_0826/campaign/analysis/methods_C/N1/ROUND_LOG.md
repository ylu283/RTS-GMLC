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
- graded_at: 2026-10-15T03:07:04+00:00
- cumulative_hv: 7.358886164124163e+17
- gain: 7.526146478770803e+16
- gain_tau: 1.430011637455927
- threshold: 5.262996664950399e+16
- would_stop: False
- n_outside_ref: 1
- decision: graded (record_only) -> r2
- designs (omega, tiers ['nuclear', 'pv', 'tail', 'wind_122', 'wind_303', 'wind_317']):
    - [0.05000, 0.16875, 0.52500, 0.05000, 1.00000, 0.05000]
    - [0.05000, 1.00000, 0.52500, 0.40625, 0.64375, 1.00000]
    - [0.05000, 0.05000, 1.00000, 0.64375, 1.00000, 0.05000]
    - [0.05000, 1.00000, 1.00000, 0.64375, 1.00000, 0.88125]
    - [0.05000, 1.00000, 0.05000, 0.05000, 0.52500, 1.00000]
    - [0.05000, 1.00000, 1.00000, 1.00000, 1.00000, 0.05000]
    - [0.05000, 1.00000, 0.05000, 0.05000, 1.00000, 0.05000]
    - [0.05000, 0.05000, 1.00000, 0.52500, 1.00000, 0.88125]
- calibration z-stats: {"load_shed_mwh": {"mean_z": 0.619, "rms_z": 1.332, "cov95": 6}, "true_curtailment_mwh": {"mean_z": 0.829, "rms_z": 1.372, "cov95": 6}, "total_cost_less_synthetic_usd": {"mean_z": -0.697, "rms_z": 1.0, "cov95": 8}}
<!-- END r1 -->

<!-- BEGIN r2 -->
## Round 2 (methods_C_N1_r2)
- proposed_at: 2026-10-15T03:34:02+00:00
- acq: qnehvi
- acq_seed: 20261408
- bo_gp_sha: 60e6328236e745b3d34dc8cd704bb72888ae5d15
- botorch: 0.16.1
- predictions: waves/methods_C_N1_r2/predictions.csv
- threshold: 5.262996664950399e+16
- decision: proposed
- designs (omega, tiers ['nuclear', 'pv', 'tail', 'wind_122', 'wind_303', 'wind_317']):
    - [0.05000, 0.88125, 1.00000, 0.88125, 0.76250, 0.52500]
    - [0.05000, 0.05000, 1.00000, 0.52500, 0.64375, 0.05000]
    - [0.05000, 0.05000, 1.00000, 1.00000, 0.76250, 0.40625]
    - [0.05000, 0.40625, 1.00000, 1.00000, 0.88125, 0.88125]
    - [0.05000, 0.64375, 1.00000, 0.88125, 0.76250, 0.05000]
    - [0.40625, 1.00000, 1.00000, 0.76250, 0.76250, 0.52500]
    - [0.05000, 0.05000, 0.05000, 0.05000, 0.52500, 1.00000]
    - [0.05000, 1.00000, 0.05000, 0.88125, 1.00000, 1.00000]
<!-- END r2 -->
