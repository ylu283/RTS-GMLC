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
- threshold: 5.262996664950399e+16
- decision: proposed
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
<!-- END r1 -->
SUBMITTED r1: array=1516257 collector=1516258 acq=1516259
