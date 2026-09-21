# ERCOT sprint PROGRESS (prompt 26)

Updated at every block boundary; a re-invoked session resumes from here.
Workspace: local worktree `../RTS-GMLC-ercot` (branch `ercot/tx123`); CRC
worktree `$GROUP/ylu28/RTS-GMLC-ercot` (created by block #1). Prompt 27
owns the main clones on `d6` — never touch.

## State (2026-09-20, second session)

- [x] **T1 port (local, 2026-09-19)** — data vendored + MD5-verified
  (`data/ercot123_2019/`, commit-pinned `MD5SUMS.vendored`); metadata
  regenerated (`make_metadata.py`: pointers, year-end padding, branch.csv
  header + UID fixes) with `PROVENANCE.md`; **model-level VERIFY PASS**
  locally (`verify_metadata.py` under gridx-prescient 2.2.3 / egret
  0.6.2: 8,772 h coverage both sims, 154 renewable time-series p_max,
  exactly 10 scalar hydro, 123 loads); wrapper `run_ercot_pcm.py`;
  `CONFIG_ERCOT.md` complete; `.gitignore` runs/`*.o*`/smoke.
- [x] **T4 pre-draft (local)** — screening wave drafted
  (`waves/screening_ercot/`: 12 rows = 9 OAT B=40 + `__ALL__` + 2
  replicate noise rows) from the availability proxy (GTEP results have
  zero curtailment — see CONFIG "Pre-ranking deviation"); extract tooling
  (`extract_ercot.py`, RUC-quality parser).
- [x] **Block #1 (CRC, 09-19/20)** — worktree created; BOTH patch HEADs
  asserted by hash (prescient h2patch-2.2.3 = a4c0849…, egret
  ercotpatch-0.6.2 = e4a244d…); diffs archived + PCM_ERCOT env export
  committed (`5816f30`); PYTHONNOUSERSITE=1 everywhere.
- [x] **Block #2 (CRC, 09-20)** — smoke_3d PASS after the egret
  fuel-curve precision patch (TL=600 characterization: all 3 days
  OPTIMAL at 1% mipgap in 305–510 s, SolCount ≥ 10, smoke mean LMP
  $14.79); probes + eoy padding check passed; riders (iii)/(iv) clear.
- [x] **Block #3 (CRC, 09-20)** — smoke_3d extract pushed (`23b9c08`);
  base submitted… **but the base DIED at t≈1 s**: prescient creates the
  run dir with `os.mkdir` and `waves/base_2019/runs/` did not exist. The
  collector's gate worked as designed → `FAILED_base_2019.md` pushed
  (`4bf58e6`). Fix committed+pushed (`de4fb43`): `mkdir -p` in
  base_job.sh + collector clears the stale marker on success.
- [ ] **Block #5 (CRC, NEXT KAY ACTION)** — recovery per the contingency
  rule: `bash ercot_block_5.sh 2>&1 | tee ercot_block_5.log` from
  `trial_0826/ercot/blocks/` in the CRC ercot worktree. Pulls + verifies
  the fix, resubmits base + chained collector (-M/-m ea). ETA ~15–22 h
  after it starts.
- [ ] **Block #4** (CRC, independent — run any time): screening array
  (12 tasks, no -tc) + chained collector; confirms the slate against the
  base extract if landed, else proxy-submits (Sep-30 protection).
- [x] **Anatomy notebook** (`analysis/base_anatomy.ipynb`, 09-20) —
  EXECUTED against `extracts/smoke_3d` with the PRELIMINARY banner
  (auto-upgrades: it prefers `extracts/base_2019` when that exists —
  after the base collector lands, `git pull` + re-run all cells, nothing
  else changes). Contains: curtailment duration + top-15 site
  concentration (hydro excluded), LMP distribution (mean $14.79
  reproduced; pricing-history caption incl. "mechanism explanation
  pending (Kay)"; 0 floor artifacts), load/net-load anatomy, RTS-vs-ERCOT
  structural panel (full-year shapes from source profiles even in prelim
  mode; peak 74.7 GW = 9.4× RTS; nuclear 6.1–6.8× per unit), standing
  DA≡RT/TL footer + gap stamp on run-derived figures.
- Block #5 written (was contingency; the FAILED marker activated it).

## Workflow-pain log inputs accumulating (directive requirement)

- Failure event #1: base died in 1 s (mkdir), collector pushed FAILED
  marker 2026-09-20T18:37Z, fix pushed 18:48 local same day, recovery
  block written same session. Cause code: failure-recovery + submit.
- Cause-coded touch log, latency decomposition, and first-pass
  automation success get compiled at analysis time from: block logs
  1–5, qacct on the JIDs, collector .o logs, ercot-bot commit log.

## Notes for the resuming session

- Local prescient env for verify/parsing/notebook: `~/venvs/ercot223`
  (gridx-prescient 2.2.3 + egret 0.6.2 + jupyter, pip).
- Session lock: `trial_0826/campaign/.session.lock` = `26` INSIDE this
  worktree (a `27` lock in the main clone is expected, not a stop).
- Results return via bot pushes: `git pull` in the local worktree.
- Known landmines already fixed in `make_metadata.py` (do not "clean up"):
  branch.csv `Tr Ratio` spelling; branch UID `L` prefix (float-coercion
  of all-numeric rows mangles bus-id lookups); year-end 24 h padding.
- No `Ref` bus by design: egret picks the alphabetically-first bus name
  deterministically (params.py:153-156).
- Notebook rendering: `text.parse_math: False` is required (literal "$"
  in captions otherwise triggers mathtext and corrupts labels).
