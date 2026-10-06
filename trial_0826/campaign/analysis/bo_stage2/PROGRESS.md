# Stage-2 BO campaign PROGRESS (prompt 30)

Lock protocol: T1 took `30`, released on close; T2 re-takes `30`. The CRC
bot jobs NEVER touch the lock. Other local sessions mid-campaign: `git
pull` first; `analysis/bo_stage2/` and `waves/bo_C_*/` are bot-owned
read-only (STOP_BO excepted).

## State (2026-10-06, T1)

- [x] **Decisions in force:** M = {load_shed_mwh, true_curtailment_mwh,
  total_cost_less_synthetic_usd} (Kay 10-06, LOCATION.md v2 adopted);
  scenario C; fully automated rounds; g1 invariance argument recorded in
  ROUND_LOG header (constant add-back ⇒ rankings invariant; costs carry
  the pending-g1 caveat).
- [x] **Init:** 32 in-box points (n0 + n0b) ingested; **HV ref fixed
  BEFORE round-1 proposals** = nadir + 0.1·span =
  [1.51022e4, 6.70350e5, 6.52035e8]; ledger entry 0: HV₀ =
  6.606272e17; **MC stopping threshold = 5.263e16** (1,000 perturbed-HV
  draws, floors 3000/5000/0.5e6, seed 20261006, ddof=0) — shed-floor-
  dominated and deliberately conservative: an early stop is the rule
  working.
- [x] **Machinery** (`7df9213` + artifacts commit): `build_bo_round` +
  bo_C triple templates (array/collector/submit_this; `-r n` all hops,
  `-terse` collector, `-M/-m ea` every hop, SUBMITTED append + bot
  push); `acquire_next.py` (ingest gate incl. designs-vs-round-record
  check, double-spend guards, floored prediction GPs, q-ParEGO
  candidates mode over the full 9⁶ lattice, one-writer
  ROUND_LOG/ledger, stop rules); `acquire_job.sh` (BOGP_CRC hardcoded
  activation, bo-gp SHA assert, ERR→WEDGED trap).
- [x] **OOM fix (documented in code):** gpytorch 1.15's exact-GP
  posterior OOMs on the full 531,441-candidate EI (>39 GB at 50k).
  Fixes are EVALUATION-CONTEXT only, library file untouched at SHA
  60e6328: (i) `fast_pred_var` around the propose call (LOVE cache —
  numerically exact for train n ≤ 64 < root size 100; verified
  2.4e-7 max dev); (ii) chunked evaluation of the library's own
  pointwise EI (bit-identical per point; import-site redirect).
- [x] **Round 1 proposed** (acq_seed 20261007, 8 designs on-lattice,
  distinct, unseen; weights 8×3 in manifest; predictions.csv written by
  the same function later rounds use). Backfill sensitivity (REPORT-
  ONLY): LOO RMSE deltas −180 shed / −5.6k curt / −72k cost — mild,
  no training-set switch proposed.
- [x] Dry-run fixture committed (`dryrun_fixture/objectives_r1.csv`,
  pinned recipe, seed 20261006).
- [x] **Tests green:** campaign suite 74 passed + 2 skipped (system env);
  BO suite 8/8 under bogp env (fake-round dry run, stop rule fires only
  on 2 consecutive lows, hard cap refuses r5, double-spend guard,
  ingest-gate design mismatch, STOP_BO, real-r1 validity).
- [ ] **KAY: run block #1** — `cd trial_0826/campaign/analysis/bo_stage2
  && bash block_1.sh 2>&1 | tee block_1.log` on the CRC d6 clone:
  bo-gp clone detached @ 60e6328, BOGP_CRC env build + export,
  `--check-env`, THREE dry runs on a scratch copy (full round / STOP_BO
  / forced-WEDGED) with qsub+git shims and a zero-real-files assert,
  then the REAL `waves/bo_C_r1/submit_this.sh` → the chain is live.
- [ ] Rounds 2–4 run unattended (array → collector → acquisition).
  Stop: threshold rule (2 consecutive low gains), hard cap (refuses
  round 5), or STOP_BO.

## T2 (one re-invocation after BO_DONE / FAILED / WEDGED email)

Re-take lock 30; `git pull`. BO_DONE → BO_STAGE2.md + executed notebook
+ figs (front + knees, HV trajectory vs random-lattice counterfactual +
Stage-1 replay context, calibration verdict [pooled RMS(z) ∈ [0.7,1.3]
AND 95% coverage ≥ 80%], interior-vs-edge vs LOCATION v2, plain summary
≤6 sentences, pain-log delta). Audit one unattended round end-to-end:
recompute its HV locally, match the ledger. FAILED/WEDGED/silent >36 h →
diagnose from markers + logs/ + ROUND_LOG + SUBMITTED lines; propose
manual recovery; never auto-resubmit.

## Kay's standing card

Stop NOW: `touch .../analysis/bo_stage2/STOP_BO` on CRC, then
`qdel <array> <collector> <acq>` from the latest SUBMITTED line in
ROUND_LOG.md. Silent-death watch: no email of ANY kind for 36 h ⇒
re-invoke the session; never resubmit by hand.
