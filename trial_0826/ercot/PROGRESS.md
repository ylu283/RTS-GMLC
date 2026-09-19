# ERCOT sprint PROGRESS (prompt 26)

Updated at every block boundary; a re-invoked session resumes from here.
Workspace: local worktree `../RTS-GMLC-ercot` (branch `ercot/tx123`); CRC
worktree `$GROUP/ylu28/RTS-GMLC-ercot` (created by block #1). Prompt 27
owns the main clones on `d6` — never touch.

## State

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
  (`extract_ercot.py`, RUC-quality parser validated against the prior
  113 h log: 365 segments, median 730 s, 21 capped days).
- [ ] **Block #1** (CRC): ercot worktree via fetch; H2-patch verification
  (2.2.3 editable, HEAD == a4c0849…, reporting.py-only diff recorded);
  PCM_ERCOT env export committed; CRC-side verify_metadata PASS.
- [ ] **Block #2** (CRC): smoke_3d (TL=600 gap-vs-time characterization),
  probe_jul 07-16 + probe_sep 09-28 (TL=120 worst-case gap/SolCount),
  eoy_3d 12-29 (padding evidence). Riders (iii)/(iv) checked in-log.
- [ ] **Block #3** (CRC): smoke extract pushed; full-year base submitted
  (TL=120, ~15–22 h ETA) + chained collector (-M/-m ea).
- [ ] **Block #4** (CRC): slate confirmed vs base curtailers (or
  proxy-submit if base slipped); screening array (12 tasks, no -tc) +
  chained collector submitted — qstat in the block log is the evidence.
- [ ] **Anatomy notebook** (`analysis/base_anatomy.ipynb`): build locally
  against `extracts/smoke_3d` with a PRELIMINARY banner once block #3
  pushes it (git pull); re-execute against `extracts/base_2019` when the
  base collector lands. Figure-side truncation rules in prompt 26 T4.
- [ ] Block #5 exists only as contingency (written on a FAILED marker).

## Notes for the resuming session

- Local prescient env for verify/parsing: `~/venvs/ercot223`
  (gridx-prescient 2.2.3 + egret 0.6.2, pip).
- Session lock: `trial_0826/campaign/.session.lock` = `26` INSIDE this
  worktree (a `27` lock in the main clone is expected, not a stop).
- Results return via bot pushes: `git pull` in the local worktree.
- Known landmines already fixed in `make_metadata.py` (do not "clean up"):
  branch.csv `Tr Ratio` spelling; branch UID `L` prefix (float-coercion
  of all-numeric rows mangles bus-id lookups); year-end 24 h padding.
- No `Ref` bus by design: egret picks the alphabetically-first bus name
  deterministically (params.py:153-156).
