# Stage-2 scenario C — session bridge (prompt 27)

**State (2026-09-20, end of T4 session): COMPLETE through T4.** Smoke
passed 09-19 (JID 1458448); both arrays + single chained collector ran;
results landed on d6 as `fc98902` (stage2-bot, first-pass push success,
zero human touches post-submission — end-to-end 39.6 h). T4 delivered in
this directory: `stage2_quicklook.ipynb` (executed) + `figs/` +
`n0_gp_loo.csv`/`nuclear_break_test.csv`/`pv_topup_test.csv`/
`t4_summary.json`, `WORKFLOW_PAIN.md` (three metrics; PENDING-KAY items
need block logs + qacct), `TOPUP_RECOMMENDATION.md` (**GO** on 16 → 32,
`skip = n_drawn_total = 16`, new wave dir — decision is Kay/PI's).
**KAY DECIDED (09-21): GO, but submission DEFERRED — build the n0b
wave whenever convenient, submit only AFTER the 3 priority pairgrid
waves (nuclear_wind_317 / pv_tail / nuclear_pv) have completed on CRC
(queue-priority: pair grids are the critical path gating M).**
T4 headlines: n₀ escapes the wind-pair hull on every objective (shed down
to 22 MWh, cost up to $648M); nuclear trend breaks past ω = 0.5
(curtailment 29× floor above the ≤ 0.5 extrapolation at ω = 1.0); pv
breaks past 0.8 (20× floor); GP LOO: curtailment/cost model-limited
(7–17× floor), shed already noise-limited (0.5×). Remaining for a later
session: fill the PENDING-KAY pain-log cells; build n0b if Kay approves
the top-up; BO round 1 waits on M from the location analysis (prompt 28).

---
Historical bridge below (T1–T3 session, 2026-09-19):

## Done this session (T1–T3)

- `tiers.py`: `STAGE2_LATTICE` (9 levels, decimal-clean) + `stage2_tiers()`
  (full-span [0.05, 1.0] box, deepcopy; TIERS/build_tiers untouched).
- `make_batches.py`: `build_stage2_n0("C")` (16-row snapped-Sobol wave,
  d = 6, seed 20260821, skip 0, n_drawn_total = 16 — zero snap collisions)
  and `build_stage2_backfill("C")` (10 rows: nuclear × 8 new lattice
  levels, pv × {0.88125, 1.0}).
- Waves generated with clean manifests (git_sha 74cd5520, dirty false):
  `waves/stage2_C_n0/` (+ `snap_map.json`), `waves/stage2_backfill_C/`
  (+ README, `collect_stage2.sh` chained collector).
- Tests green: campaign 60 passed + 1 skipped (incl. new
  `tests/test_stage2.py`), multi_pem 14 passed (incl. the two new thermal
  ω > 0.5 regime cases: PEM_fraction 1.0 → p_min = 0, cost curve
  [[0,0],[p_max, p_max·B]], ramps = p_max; and 0.7625).
- Congestion pre-check: hourly bus LMPs live in each run's
  `bus_detail.csv` (`LMP`, `LMP DA`), hourly line flows in
  `line_detail.csv` (`Flow`, `Violation`); nothing in the driver's
  prescient options suppresses them → any congestion definition stays
  post-hoc extractable.
- `analysis/bo_replay/stage2_plan.md`: AMENDMENTS section appended — that
  append is the update of record (prompt 24's session must not redo it).

## JIDs

Pending — assigned when Kay runs the blocks. J1 (n0 array, 16 tasks, no
-tc cap — Kay 09-19: licenses not a constraint), J2 (backfill array, 10
tasks, holds on J1), collector (holds on J1,J2; emails ylu28@nd.edu on
finish/abort). Recorded in `block_2.log`.

## T4 (next session) needs

1. At session start: `git pull`; if `waves/stage2_C_n0/objectives.csv`
   exists → T4; if any `FAILED_*.md` marker exists → report and stop.
2. Notebook (bold-axes rcParams house style): n₀ objective ranges vs the
   wind-pair grid hull; nuclear back-fill curve ω ∈ [0.05, 1] appended to
   the sweep figure (does the linear trend break past 0.5?); pv top-up
   points (0.88125, 1.0) vs the old curve.
3. Pre-registered top-up decision: GP LOO diagnostics on the 16 → go/no-go
   recommendation to Kay on extending n₀ 16 → 32 via
   `skip = n_drawn_total` (= 16, from the wave manifest), ~160 core-h.
4. Workflow-pain log (directive requirement), three metrics:
   (i) cause-coded touch log {submit, monitor, failure-recovery, git/race,
   data-wrangling}; (ii) latency decomposition wave-generated → CSVs-on-d6
   (queue / run / collector / human-gated dead time, esp. time-to-notice
   of any FAILED marker); (iii) first-pass automation success (collector +
   bot push unattended? rebase retries? gate resubmissions?). Inputs:
   block_1.log / block_2.log timestamps, qacct on the JIDs, collector .o
   log in `waves/stage2_backfill_C/`, git log of stage2-bot commits.
5. Delete `campaign/.session.lock` ownership passes to the T4 session
   (this session deletes its lock on close; T4 writes its own).
