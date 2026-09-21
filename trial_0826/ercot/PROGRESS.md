# ERCOT sprint PROGRESS (prompt 26)

Updated at every block boundary; a re-invoked session resumes from here.
Workspace: local worktree `../RTS-GMLC-ercot` (branch `ercot/tx123`); CRC
worktree `$GROUP/ylu28/RTS-GMLC-ercot` (created by block #1). Prompt 27
owns the main clones on `d6` — never touch.

## State (2026-09-21, third session — base LANDED)

- [x] **T1 port (local, 09-19)** — data vendored + MD5-verified;
  metadata regenerated (`make_metadata.py`) with PROVENANCE; model-level
  VERIFY PASS; wrapper `run_ercot_pcm.py`; `CONFIG_ERCOT.md`.
- [x] **Block #1 (CRC)** — both patch HEADs asserted by hash (prescient
  h2patch-2.2.3 a4c0849…, egret ercotpatch-0.6.2 e4a244d…); diffs +
  PCM_ERCOT env export committed; PYTHONNOUSERSITE=1 everywhere.
- [x] **Block #2 (CRC)** — smoke + probes + eoy padding PASS; riders
  clear; smoke mean LMP $14.79.
- [x] **Block #3 (CRC)** — smoke extract pushed; base died (mkdir), fix
  `de4fb43`, marker cleared later by the successful collector.
- [x] **Block #5 (CRC, 09-20/21)** — base resubmitted; **collector
  succeeded end-to-end: `be5d254 ercot-bot: base_2019 extract`** (first
  fully-unattended collector run incl. marker clearing — automation
  first-pass success after one human-fixed submit bug).
- [x] **BASE QUALITY (rider (i), audited 09-21): RUN VALID.** 365/365
  days, SolCount=0 on NONE; 44/365 days (12.1%) TIME_LIMIT; final gap
  median 0.98%, P95 1.36%, max 3.23% (worst day 2019-02-22) — far under
  the 10% rider-(iii) threshold. Note on `solve_time_s` semantics: the
  per-day value sums ALL Gurobi solves in that day's log segment (RUC
  MIP + settlements/pricing under `compute_market_settlements=True`), so
  >120 s totals on OPTIMAL days are expected; the 120 s cap binds per
  MIP solve.
- [x] **Degenerate-g4 RESOLVED: NOT degenerate** — 7 hours RT reserve
  shortfall, 280.9 MWh total on the TL=120 base (TL=3600's zero did not
  carry over). CONFIG_ERCOT.md updated (row, resolution 4, decision 5).
- [x] **Base anatomy** — LMP mean $14.53 / median $10.36 over 1.08M
  bus-hours, 0 floor artifacts, 189 bus-hours ≥ $450; VRE curtailment
  10.6% of availability, zero shed; peak 74.7 GW.
  `analysis/base_anatomy.ipynb` re-executed against `extracts/base_2019`
  (PRELIMINARY banner gone), 0 errors.
- [x] **Screening slate CONFIRMED WEAK → two-arm redesign (09-21):**
  actual top-12 curtailers overlap the availability-proxy slate only
  3/9 (275, 274, 30). Curtailment is congestion-driven: **bus 120 hosts
  5 of the top-8 curtailers** (275, 274, 270, 163, 116); site 163
  (185 MW) curtails 2.5× its delivered energy. New wave
  `waves/screening_topup/` (7 rows: wind 270, 163, 110, 146, 140; PV
  116, 59) generated deterministically by `make_screening_topup.py`
  from the base extract; both arms together cover the actual top-10
  exactly. v1 = availability/contrast arm + __ALL__ + the 2 replicate
  noise-ruler rows.
- [ ] **Block #4b (CRC, NEXT KAY ACTION — supersedes block #4):**
  `bash ercot_block_4b.sh 2>&1 | tee ercot_block_4b.log`. Handles both
  histories: if v1 was never submitted (or block #4's ranking gate
  stopped it — it fires at 3/9), submits BOTH arms (12 + 7 tasks); if
  v1 was proxy-submitted before the base landed, detects it (qstat -j /
  run dirs) and submits only the top-up. Each arm has its own chained
  collector (-M/-m ea). **Do not run ercot_block_4.sh anymore.**
- [ ] Screening analysis when the arm extracts land: retrofit deltas
  gated by the replicate-spread noise ruler (|Δ| ≫ spread or "within
  solver noise"); check whether retrofit value tracks curtailment
  (top-up arm) or size/availability (v1 arm); bus-120 congestion-pocket
  story vs line_flows.

## Workflow-pain log inputs accumulating (directive requirement)

- Failure event #1: base died in 1 s (mkdir), marker pushed 09-20
  18:37Z, fix 18:48, recovery block same session; resubmit + clean
  collector pass by 09-21. Cause codes: submit + failure-recovery.
- First-pass automation: block #5's chain ran unattended (gate PASS,
  extract, marker clear, bot commit+push, email) — zero human touches
  after qsub.
- Ranking-gate event: block #4's slate gate is designed to trip at 3/9
  (<half) — record in the touch log whether Kay hit it or 4b's
  detection path instead (visible in whichever block log exists).
- Compile at analysis time from: block logs 1–5 + 4b, qacct on the
  JIDs, collector .o logs, ercot-bot commit log.

## Notes for the resuming session

- Local env for verify/parsing/notebook: `~/venvs/ercot223`
  (gridx-prescient 2.2.3 + egret 0.6.2 + jupyter, pip).
- Session lock: `trial_0826/campaign/.session.lock` = `26` INSIDE this
  worktree (a `27` lock in the main clone is expected, not a stop).
- Results return via bot pushes: `git pull` in the local worktree.
- `make_metadata.py` landmines (do not "clean up"): `Tr Ratio` spelling;
  branch UID `L` prefix; year-end 24 h padding.
- No `Ref` bus by design: egret picks the alphabetically-first bus name
  deterministically (params.py:153-156).
- Notebook rendering: `text.parse_math: False` required (literal "$"
  otherwise triggers mathtext and corrupts labels).
