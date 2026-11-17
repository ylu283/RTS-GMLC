# methods_C arm V1 — ROUND_LOG (prompt 35; acq = qnehvi, base = ['stage2_C_n0', 'stage2_C_n0b'], seed_id = 5)

Ledger: `analysis/methods_C/V1/ledger.json`. stop_rule = record_only: the rule is
graded and logged (would_stop, gain in tau units) but never acted on;
every arm runs to hard_cap = 4. Acquisition jobs never
submit (--no-submit); Kay submits from bastion via submit_ready.sh.
Stop NOW: `touch analysis/methods_C/V1/STOP_V1` on the CRC clone, then qdel the
arm's JIDs from methods_C/PROGRESS.md.

<!-- BEGIN r1 -->
## Round 1 (methods_C_V1_r1)
- proposed_at: 2026-11-14T04:37:38+00:00
- acq: qnehvi
- acq_seed: 20261507
- bo_gp_sha: 60e6328236e745b3d34dc8cd704bb72888ae5d15
- botorch: 0.16.1
- predictions: waves/methods_C_V1_r1/predictions.csv
- graded_at: 2026-11-17T04:17:19+00:00
- cumulative_hv: 7.359465729118511e+17
- gain: 7.531942128714291e+16
- gain_tau: 1.4311128446791967
- threshold: 5.262996664950399e+16
- would_stop: False
- gain_tau_het: 24.92885759299168
- would_stop_het: False
- gain_tau_285: 11.572168458621704
- would_stop_285: False
- gp_floor: 1e-09
- loo_rms_z: {'load_shed_mwh': 0.9103, 'true_curtailment_mwh': 0.7695, 'total_cost_less_synthetic_usd': 0.5743}
- n_outside_ref: 2
- decision: graded (record_only)
- designs (omega, tiers ['nuclear', 'pv', 'tail', 'wind_122', 'wind_303', 'wind_317']):
    - [0.05000, 0.16875, 0.64375, 0.05000, 1.00000, 0.05000]
    - [0.05000, 0.76250, 0.52500, 0.64375, 0.64375, 1.00000]
    - [0.05000, 1.00000, 1.00000, 0.16875, 1.00000, 0.88125]
    - [0.05000, 0.05000, 1.00000, 0.52500, 1.00000, 0.05000]
    - [0.05000, 1.00000, 0.40625, 0.05000, 0.52500, 1.00000]
    - [0.05000, 1.00000, 1.00000, 0.64375, 1.00000, 1.00000]
    - [0.05000, 0.05000, 0.05000, 0.05000, 1.00000, 0.05000]
    - [0.05000, 1.00000, 1.00000, 0.05000, 1.00000, 0.05000]
- calibration z-stats: {"load_shed_mwh": {"mean_z": 1.849, "rms_z": 2.766, "cov95": 5}, "true_curtailment_mwh": {"mean_z": 1.101, "rms_z": 1.697, "cov95": 6}, "total_cost_less_synthetic_usd": {"mean_z": -0.904, "rms_z": 1.204, "cov95": 8}}
<!-- END r1 -->
