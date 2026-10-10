# Stage-2 BO ROUND_LOG (prompt 30 — q-ParEGO, scenario C, fully automated)

**Kay's standing card** — stop NOW:
`touch /groups/adowling/ylu28/RTS-GMLC/trial_0826/campaign/analysis/bo_stage2/STOP_BO`
on the CRC clone, then `qdel <array> <collector> <acq>` from the latest
`SUBMITTED r<k>:` line below. **Silent-death watch: no email of ANY kind
for 36 h => re-invoke the session to diagnose; never resubmit by hand.**
Manual recovery after WEDGED: push by hand + qsub the recorded triple —
never re-run acquire_next for a round that already proposed.

g1 note: inside the Stage-2 box nuclear omega >= 0.05 always, so option
(c)'s add-back is the same +$28.188M constant for every design — dominance
relations and acquisition rankings are invariant. Absolute costs below
carry the "pending g1 ruling" caveat; re-level when the PI rules.

<!-- BEGIN r1 -->
## Round 1
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
SUBMITTED r1: array=1516257 collector=1516258 acq=1516259

<!-- BEGIN r2 -->
## Round 2
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
SUBMITTED r2: array=1519934 collector=1519935 acq=1519936
