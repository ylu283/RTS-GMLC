# methods_C — PROGRESS (prompt 35, executor session)

Lock: `trial_0826/campaign/.session.lock` = 35 while a session works here.
Admin docs (`admin/prompt/bogp/`) are strategy-owned — outcomes are reported
HERE and in the session's final message only.

## T0 gates

- [x] **G1 curtailment closure — PASS on CRC (Kay, 10-12)** on random_C #42 (827 MW), #39
  (2,590 MW), #2 (wind share 0.70): all 10 PEM sites × 8,784 h close per site-hour
  (available = dispatched + parent curtailment + PEM withheld vs base-case availability);
  PEM / parent split exact; non-retrofit renewables unchanged (≤ 1.4e-14 MW); true
  curtailment excludes `*_PEM` and equals objectives.csv (err 0 / 0 / 5.8e-11 MWh).
  Max closure error 1.0e-6 MW on three run-#42 wind sites = Prescient's 6-decimal CSV
  rounding (≈ 1e-9 relative to site availability); all others ≤ 2.3e-13. Local pilot
  smoke also PASS.
- [x] **G2 envs (local + CRC — all T0 gates G1–G5 closed)** — `bogp-botorch` ready, no pin drift (ENV_READY.md, deb5f42).
  [x] CRC `BOGP_CRC_botorch` BUILT (10-12 evening) at /groups/…/conda_envs: imports
  2.14.1+cpu / 1.15.2 / 0.6.1 / botorch 0.16.1; freeze diff vs BOGP_CRC = additions only
  (the same 9 packages as local). `ARM=N1 … --check-env` → CHECK-ENV PASS (N1)
  (bo-gp 60e6328 matches ledger); BOGP_CRC vs committed prompt-30 freeze: UNCHANGED.
  **G2 closed (local + CRC).**
- [x] **G3 capacity — recorded (10-12).** `qacct` is unavailable on CRC (no accounting file on bastion) → walls from the
  logs / bot-commit timestamps (upper bounds: include queue wait):
  - per run: random_C 48 tasks SUBMITTED→results **≤ 9.4 h** (10-11 11:00→20:22);
    bo_C_r1 16.1 h, bo_C_r2 21.6 h (prompt-30 rounds) → plan ≈ 10–22 h per round.
  - per acquisition: r1 grade + propose (q-ParEGO, full lattice) **29 min** results→push
    (10-08 15:00:49→15:30:15); grade-only 29 s. qNEHVI rounds: ≈ 30–40 min (G4 × 2).
  - capacity (`qstat -g c`, 10-12): `long` 15,515 / 25,752 slots free, CQLOAD 0.47 —
    the 128-task + 7-collector launch is not capacity-bound.
  - Optional exact per-task walls (non-blocking): `grep -h "Total simulation time"
    waves/random_C/random_C_array.o1526985.* | awk '{print $4/3600}' | sort -n`.
- [x] **G4 qNEHVI benchmark** — 16.0 min wall, 2.6 GB peak (n = 40, full lattice, q = 8,
  4 threads) → no candidate-subset rule (G4_BENCHMARK.md).
- [x] **G5 PREREG.md** — §5 + §6 verbatim (sha256 ef3b4670…) + executor clarifications;
  committed with the code, before any new run.
- [x] **Regression** — generalized code reproduces bo_C_r2's 8 designs exactly (same
  order, seed 20261008, weights) from a scratch root without bo_C_r2 (326 s).

- [x] **N1 replay gate (§3.2) — PASS under AMENDMENT 10-12 (one-sided: median ≥ q-ParEGO
  min at n = 16 and 24; Kay, made after the result, disclosed in PREREG.md).** Re-evaluated
  on the existing replay_gate.json: 0.9166 ≥ 0.8444, 0.9534 ≥ 0.8698. `N1/GATE_PASS_N1.md`
  replaces NOT_RUN_N1.md (quoted inside as history). **N1 runs again.**
  Original record:
- [x] ~~**N1 replay gate (§3.2) — FAILED (high side) → N1 NOT RUN.**~~ Median HV recovery
  n = 16: 0.9166 ∈ [0.8444, 0.9295]; n = 24: **0.9534 > max 0.9518** (by 0.0016).
  Applied as pre-registered (two-sided range); `N1/NOT_RUN_N1.md`, `replay_gate.json`.
  Re-admitting N1 needs a new pre-registration (strategy session / Kay).

## Code (§3)

- `arms.json`, `acquire_arm.py` (generalized; imports the frozen prompt-30
  brain), `acquire_arm_job.sh`, `qnehvi.py`, `replay_gate.py`,
  `methods_state.py` + `submit_ready.sh`, generic `methods_array.sh` /
  `methods_collect.sh` (from make_batches), builders in `make_batches.py`
  (`build_stage2_n0` size/seed/name params; `build_methods_start`,
  `build_methods_sobol`, `build_methods_round`).
- Tests: `tests/test_methods_C.py` (base env), `tests/test_methods_acq.py`
  (bogp; incl. the bo_C_r2 regression), `tests/test_methods_qnehvi.py`
  (bogp-botorch).

## T0 status (2026-10-12, executor)

- Built + pushed: S2, S3 (32 each), Q1–Q3 (16 each) — f82fddd, clean manifests.
- P1 initialized + r3 proposed locally (seed 20261009) — d1c2c9a.
- ~~N1 NOT RUN (replay gate failed high) — 2596416.~~ Superseded: N1 gate PASS (amendment 10-12).
- N1 initialized (P1's R_frozen + τ₁) + r1 proposed locally (qNEHVI, seed 20261407,
  678 s) — 6ab5408.
- Dry run of submit_ready (after the amendment): **7 items READY = 128 array tasks + 7
  collectors** (S2, S3, Q1–Q3, P1 r3, N1 r1); P2/P3 WAIT_BASE.
- Budget with N1: **224 runs ≈ 3.4k core-h** + ≈ 15 acquisition jobs (P1 r3–r4; P2/P3
  r0–r4; N1 r1–r4, ≈ 30–40 min each on CRC).
- ~~BLOCKING before the first submit: G1 on CRC and G3~~ — both done (d876321).
- Prompt 36 waves A+B+C SUBMITTED (SMOKE_PASS 0a2acf2, strategy relay 10-12) → CRC order
  allows the prompt-35 launch now.
  ~~`BOGP_CRC_botorch` is no longer needed~~ — **needed again** (N1 runs): Kay builds it from
  the ENV_READY.md block and passes `ARM=N1 ... acquire_arm_job.sh --check-env` before N1's
  first acquisition.

## Launch 1 (10-12) — FAILED at import → fixed → relaunch pending

- All 7 arrays (1533458–1533471) died at task start: `methods_array.sh` exported
  PYTHONNOUSERSITE=1 and PCM0826's `networkx` (egret tx_calc ← prescient) lives in
  ~/.local → ModuleNotFoundError (`methods_C_N1_r1_array.o1533471.1`). No run started; the
  7 collectors pushed FAILED markers (4290ab7…deead56).
- Fix: array env lines = random_C / stage2 / bo_C array scripts exactly (no
  PYTHONNOUSERSITE; collectors + acquisition jobs keep it); test
  `test_array_env_matches_frozen_stage2`. PCM0826 untouched. PREREG dated NOTE (not an
  analysis amendment). This is the ONE allowed resubmission per item.
- `submit_ready.sh --relaunch-failed`: FAILED + 0 completed runs + 1 prior submission →
  marker removed (committed), array + collector resubmitted once (`relaunch=1`).
  Local dry run: 7 RELAUNCH, P2/P3 WAIT_BASE.
- 37 unaffected (BOGP_CRC / BOGP_CRC_botorch only, no PCM0826).
- [x] **Provenance (Kay, bastion, 10-12; also relayed by the strategy session)** — PCM0826 = Python 3.12.13,
  `site.ENABLE_USER_SITE = True`, user site `/users/ylu28/.local/lib/python3.12/site-packages`.
  - `PYTHONNOUSERSITE=1 python -c "import networkx"` → ModuleNotFoundError (launch-1 failure reproduced).
  - Without it: `networkx 3.6.1` from `/users/ylu28/.local/lib/python3.12/site-packages/networkx/__init__.py`.
  - `prescient.__file__` = None: prescient resolves as a namespace package; a `prescient/` dir exists in ~/.local.
  - `~/.local/lib/python3.12/site-packages` (top-level, from Kay's `ls … | head -50` paste to the executor): coramin 0.1.1, gtep 0.1.dev0 (editable),
    flexcache 0.3, flexparser 0.4, iniconfig 2.3.0, networkx 3.6.1, pint 0.25.3, pluggy 1.6.0,
    prescient/, seaborn 0.13.2.
  - **Entry-path import** (trial_0826/multi_pem, flag unset): `python -c "from utils import
    parameter_sweep_runner"` → IMPORT OK (the exact import chain launch 1 died in).
  - The ~/.local user site is part of the effective frozen Stage-2 software stack (every
    Stage-2 array script ran without PYTHONNOUSERSITE).
  - **Caveat (first attempt void):** the first provenance attempt ran in a shell where the
    ENV_READY build recipe had exported PYTHONNOUSERSITE=1 (`echo` → `[1]`), so both imports
    failed. Interactive shells that ran that recipe must `unset PYTHONNOUSERSITE`. SGE jobs
    are unaffected: submit_ready.sh / qsub do not pass `-V`.

## Submission log
SUBMITTED wave=methods_C_S2_n0 array=1533458 collector=1533459
SUBMITTED wave=methods_C_S3_n0 array=1533461 collector=1533462
SUBMITTED wave=methods_C_Q1 array=1533463 collector=1533464
SUBMITTED wave=methods_C_Q2 array=1533465 collector=1533466
SUBMITTED wave=methods_C_Q3 array=1533467 collector=1533468
SUBMITTED wave=methods_C_P1_r3 array=1533469 collector=1533470
SUBMITTED wave=methods_C_N1_r1 array=1533471 collector=1533472
SUBMITTED wave=methods_C_S2_n0 array=1533551 collector=1533552 relaunch=1
SUBMITTED wave=methods_C_S3_n0 array=1533553 collector=1533554 relaunch=1
SUBMITTED wave=methods_C_Q1 array=1533555 collector=1533556 relaunch=1
SUBMITTED wave=methods_C_Q2 array=1533557 collector=1533558 relaunch=1
SUBMITTED wave=methods_C_Q3 array=1533559 collector=1533560 relaunch=1
SUBMITTED wave=methods_C_P1_r3 array=1533561 collector=1533562 relaunch=1
SUBMITTED wave=methods_C_N1_r1 array=1533563 collector=1533564 relaunch=1
SUBMITTED acq arm=P1 round=3 acq=1543622
SUBMITTED wave=methods_C_P1_r4 array=1543623 collector=1543624 held_on=1543622
SUBMITTED acq arm=P2 round=0 acq=1543625
SUBMITTED wave=methods_C_P2_r1 array=1543626 collector=1543627 held_on=1543625
SUBMITTED acq arm=P3 round=0 acq=1543628
SUBMITTED wave=methods_C_P3_r1 array=1543629 collector=1543630 held_on=1543628
SUBMITTED acq arm=N1 round=1 acq=1543631
SUBMITTED wave=methods_C_N1_r2 array=1543632 collector=1543633 held_on=1543631
SUBMITTED acq arm=P1 round=4 acq=1552728
SUBMITTED acq arm=P2 round=1 acq=1552730
SUBMITTED wave=methods_C_P2_r2 array=1552732 collector=1552734 held_on=1552730
SUBMITTED acq arm=P3 round=1 acq=1552736
SUBMITTED wave=methods_C_P3_r2 array=1552737 collector=1552739 held_on=1552736
SUBMITTED acq arm=N1 round=2 acq=1552741
SUBMITTED wave=methods_C_N1_r3 array=1552743 collector=1552745 held_on=1552741
SUBMITTED acq arm=P2 round=2 acq=1577763
SUBMITTED wave=methods_C_P2_r3 array=1577764 collector=1577765 held_on=1577763
SUBMITTED acq arm=P3 round=2 acq=1577766
SUBMITTED wave=methods_C_P3_r3 array=1577768 collector=1577769 held_on=1577766
SUBMITTED acq arm=N1 round=3 acq=1577770
SUBMITTED wave=methods_C_N1_r4 array=1577771 collector=1577772 held_on=1577770
SUBMITTED acq arm=P2 round=3 acq=1599788
SUBMITTED wave=methods_C_P2_r4 array=1599789 collector=1599791 held_on=1599788
SUBMITTED acq arm=P3 round=3 acq=1599792
SUBMITTED wave=methods_C_P3_r4 array=1599793 collector=1599794 held_on=1599792
SUBMITTED acq arm=N1 round=4 acq=1599795
SUBMITTED acq arm=P2 round=4 acq=1607939
SUBMITTED acq arm=P3 round=4 acq=1607940
