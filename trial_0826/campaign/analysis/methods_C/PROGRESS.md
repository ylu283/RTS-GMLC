# methods_C — PROGRESS (prompt 35, executor session)

Lock: `trial_0826/campaign/.session.lock` = 35 while a session works here.
Admin docs (`admin/prompt/bogp/`) are strategy-owned — outcomes are reported
HERE and in the session's final message only.

## T0 gates

- [ ] **G1 curtailment closure** — `g1_closure.py` written; local smoke PASS on
  `waves/pilot` run 1 (10 renewable PEM sites × 8,784 h, closure / split max
  error ≤ 1.4e-14 MW, non-retrofit renewables unchanged, PEM curtailment
  excluded, objectives.csv match 0.0). Stage-2 runs are CRC-only → **Kay runs
  on CRC** (random_C low-MW #42 827 MW, high-MW #39 2,590 MW, wind-heavy #2
  share 0.70):
  `python analysis/methods_C/g1_closure.py --base ../base_case_pcm_test --wave waves/random_C --index 42 --index 39 --index 2`
- [x] **G2 envs (local)** — `bogp-botorch` ready, no pin drift (ENV_READY.md, deb5f42).
  [ ] CRC `BOGP_CRC_botorch` — Kay runs the ENV_READY.md block, pastes import line + diff.
- [ ] **G3 capacity** — Kay pastes `qacct -j 1526985`, `qacct -j <acq_bo_C_r1>`, `qquota -u ylu28`.
- [x] **G4 qNEHVI benchmark** — 16.0 min wall, 2.6 GB peak (n = 40, full lattice, q = 8,
  4 threads) → no candidate-subset rule (G4_BENCHMARK.md).
- [x] **G5 PREREG.md** — §5 + §6 verbatim (sha256 ef3b4670…) + executor clarifications;
  committed with the code, before any new run.
- [x] **Regression** — generalized code reproduces bo_C_r2's 8 designs exactly (same
  order, seed 20261008, weights) from a scratch root without bo_C_r2 (326 s).

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

## Submission log
