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
- BLOCKING before the first submit: **G1 on CRC** (fail → STOP) and **G3** pastes.
  ~~`BOGP_CRC_botorch` is no longer needed~~ — **needed again** (N1 runs): Kay builds it from
  the ENV_READY.md block and passes `ARM=N1 ... acquire_arm_job.sh --check-env` before N1's
  first acquisition.

## Submission log
