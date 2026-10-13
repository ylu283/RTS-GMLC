# PREREG — prompt 35 methods arms at scenario C (G5)

Committed BEFORE the first new run of this prompt. §5 and §6 below are copied
VERBATIM from `admin/prompt/bogp/35-stage2-methods-arms.md` v2 (2026-10-12);
sha256 of the copied text is recorded at the end. The "Executor
clarifications" section pins details the prompt leaves open; it is part of
this pre-registration and is frozen with it. Nothing here may be edited
after the first new run lands (append-only corrections, dated, if a typo is
found — never a change of rule).

## 5. Pre-registered analysis (PREREG.md)

- **References.** Primary R_union (prompt 34, frozen). Secondary: each
  arm's R_frozen_k; R_common (nadir + 10 % span over everything in this
  prompt) post hoc only. Report points outside the primary box per arm.
- **Floor-robust HV (co-primary).** Mean over 64 uniform grid offsets
  u ∈ [0, floor)³ (fixed seed) of HV(floor·⌈(y − u)/floor⌉ + u); R not
  quantized; count points pushed outside R. A claim must hold under raw
  AND floor-robust HV.
- **Percentile vs the random pool.** Comparator for arm k = S_k ∪ random
  subset of size n − 32 (100,000 draws, seed 20261012), with a 1,000-
  resample pool bootstrap interval. n = 48 is the inferential checkpoint
  (16-of-48, the prompt-34 design). n = 56 / 64 percentiles are
  DESCRIPTIVE (24- and 32-of-48 subsets overlap heavily). The pool is
  shared by all arms, so their p̂ are correlated; say so.
- **Claim (ii) "stable across replicates (start set + acquisition seed)
  at scenario C"** holds iff ALL:
  1. P1, P2, P3 each p̂48 ≥ 0.8 at R_union under both metrics;
  2. dispersion: range of absolute HV across P1–P3 at n = 64, at R_union,
     ≤ 1 τ̄ (mean τ_k) under both metrics;
  3. each replicate's top-3 knees (both normalizations, as prompt 34
     §4.3) satisfy R′ = {nuclear ω = 0.05; (wind_303 + wind_317 MW)/total
     ≥ 0.5} at a higher rate than the base rate — the share of random-pool
     designs and of knees of random-only fronts that satisfy R′ (report
     both). P1 is in-sample for R′; P2/P3 are the out-of-sample test;
  4. curtailment extreme beyond the pool's best by > floor in ≥ 2 of 3
     replicates (cost extreme reported, not tested — guessable).
- **Interpretation table (fixed now).** All three pass → claim (ii)
  supported at C. P1 passes, P2/P3 fail → the S1 result depends on the
  start set; the headline drops to "one of three". All fail → claim (ii)
  not shown. In every case the workflow claim (audit, stop record,
  baseline) stands. A failed or missing PCM run: resubmit once; if still
  missing, the arm is reported with its last complete round. N1 gate
  failed → "not run".
- **Acquisition (N1 vs P1, paired on S1).** Report ΔHV per checkpoint in
  τ units AND as a percentile of the P1–P3 spread, under both metrics.
  Negative control: the same Δ between P1 and the median random batch. If
  the control's |Δ| is also < τ₁, write "not discriminable at this noise
  level". One seed: "consistent with" at most. Name the confound
  (acquisition + model + noise handling change together).
- **Stop rule on real data** (P1's r2 stop = live decision; all other
  stops = counterfactual, labelled): per arm τ_k/HV₀_k; round gains in τ
  units; would-stop round and whether it is the earliest possible; HV
  left on the table at n = 64 (τ units, %, both metrics); whether any
  post-stop round gained > τ (error event, k of 4); what changed after
  the stop (new front members, extremes moved > floor, knee / R′ status);
  core-h saved; stop round as a function of τ ∈ {0.25, 0.5, 1, 1.5, 2}·τ_k.
  If the rule always fires at r2, say it acts as a fixed 2-round budget.
- **Sobol (Q1–Q3):** HV at n = 48 vs the same start set's q-ParEGO arm and
  vs the pool percentile. Descriptive.
- **Wording.** Bans: "beat", "significant", "converged". Every BO-vs-
  baseline HV statement gives the difference in τ units and under
  floor-robust HV. Claim text says "scenario C only; A/B not tested".

## 6. Red lines

- Frozen: S1 waves, `bo_C_r1/r2`, `analysis/bo_stage2/*`, `random_C`,
  `ref_union.json`, the `bogp` and `BOGP_CRC` envs.
- No `-tc`; `mkdir -p` output parents; PYTHONNOUSERSITE=1; compute nodes
  never qsub; the executor never qsubs.
- No new arms after the first new run without a new pre-registration.
- **No `Co-Authored-By` line in commits.** Bold axes in every figure.
- ERCOT (prompt 36) has CRC priority until its A–C land.

## Executor clarifications (frozen with this file)

1. **N1 replay gate (§3.2).** "The q-ParEGO smoke range" = min–max of the 10
   per-seed q-ParEGO values recorded in `analysis/bo_replay/replay_results.json`
   (`qparego_smoke_C.per_seed`): n = 16 → [0.8444, 0.9295]; n = 24 →
   [0.8698, 0.9518]. N1's MEDIAN over the same 10 seeds (init =
   `default_rng(s).choice(81, 8)`, s = 0..9; q = 8; 2 rounds; candidates =
   the 81 cells; M = the 4 replay objectives; ref = the full-81 nadir + 10 %
   span, as the smoke) must lie inside the range at BOTH n = 16 and n = 24.
   Noise lower bounds = `replay.floors()` (starts = working floor 60).
   Fail → N1 "not run".
2. **qNEHVI settings.** BoTorch 0.16.1 `qNoisyExpectedHypervolumeImprovement`
   (as specified — BoTorch prints a deprecation note recommending qLogNEHVI;
   not switched), 128-sample `SobolQMCNormalSampler` seeded with the round's
   acquisition seed, `prune_baseline=True`, `cache_root=True`,
   `optimize_acqf_discrete(q=8, max_batch_size=512, unique=True)`, float64,
   model per `qnehvi.py` (differences vs q-ParEGO listed there).
3. **G4 candidate-subset rule.** Decided from the G4 measurement and
   recorded in G4_BENCHMARK.md BEFORE N1's first proposal; applies to N1 only.
4. **Floor-robust HV offsets (§5).** 64 offsets u ~ U[0, floor)³ drawn once
   from `np.random.default_rng(20261035)`; the same 64 for every arm, ref and
   checkpoint.
5. **Percentile comparator seeds.** 100,000 subsets from
   `default_rng([20261012, 0, size])` and pool bootstraps from
   `default_rng([20261012, 1, size, b])` — the prompt-34 `rb_hv.py`
   machinery, reused unchanged, with S_k in place of S1 for arm k.
6. **Acquisition seeds.** `20261006 + 100·seed_id + k`; seed_id P1 0,
   P2 2, P3 3, N1 4 (`arms.json`).
7. **Hold mode** is the default in `submit_ready.sh` (prompt §4); Kay may
   run `--no-hold` instead. Either way the analysis is unchanged.
8. **Missing runs (§5 interpretation).** "Resubmit once" = one
   `resubmit_missing.py` / `qsub -t` pass per wave, logged in PROGRESS.md.

---
sha256(verbatim §5 + §6) = `ef3b46701e44d47f954895c07d971e6806c165caa5bf0c53e7a64aa9014ddccb`

## AMENDMENT 2026-10-12 — N1 replay gate made ONE-SIDED (Kay; made AFTER the gate result)

**Disclosure: this amendment was made after the gate result was known.** It
is appended; clarification 1 above is left as originally committed.

- Original gate (clarification 1, two-sided): N1's median inside the
  q-ParEGO 10-seed min–max at both n = 16 and n = 24. Result
  (`replay_gate.json`, sha256 `f841a700…d889441`): n = 16 median 0.9166 in
  [0.8444, 0.9295]; n = 24 median **0.9534, above the max 0.9518** by
  0.0016. That failed on the HIGH side, so N1 was "not run" (commit 2596416).
- **Why it changed:** the gate only checks the implementation. A broken
  qNEHVI implementation can only score LOW, so the upper bound tested
  nothing the gate is for; prompt 35 v2 calls it a wording error. Which
  acquisition does better is answered only by N1 vs P1 on real runs (§5
  "Acquisition"), never by this gate.
- **New gate (one-sided):** N1's median ≥ the q-ParEGO smoke MIN at both
  n = 16 and n = 24. It is re-evaluated on the EXISTING `replay_gate.json`,
  with no re-run: 0.9166 ≥ 0.8444 and 0.9534 ≥ 0.8698 → **PASS**.
- **Paper text (prompt 35 §3.2):** "The pre-registered gate was two-sided;
  after the result we made it one-sided (lower bound only), because it only
  checks the implementation. qNEHVI exceeded the q-ParEGO range by 0.0016
  at n = 24."
- Nothing else in this file changes.

## NOTE 2026-10-12 (execution, not an amendment of the analysis) — launch 1 failed at import

**Launch 1 failed at import:** no run started and no output was produced.
All 7 T0 items died at task start: S2, S3, Q1–Q3, P1 r3 and N1 r1 (arrays
1533458–1533471).
- **Cause:** the generic `methods_array.sh` set `PYTHONNOUSERSITE=1`.
  PCM0826 resolves `networkx` (needed by egret's tx_calc, which Prescient
  imports) from `~/.local`, so `multi_PEM_PCM.py` raised ModuleNotFoundError.
  A smoke test of `import prescient, pyomo, egret` passes with the flag set,
  because egret's top level does not import networkx.
- **Fix:** the PRESCIENT array task now uses the **frozen Stage-2 env
  convention** byte-for-byte. Its env lines equal `random_C_array.sh` and
  the stage2 / bo_C array scripts that produced every frozen Stage-2 result:
  PCM0826, gurobi module, no PYTHONNOUSERSITE. A test enforces this.
  Collectors and acquisition jobs keep PYTHONNOUSERSITE=1. PCM0826 was not
  modified.
- **Resubmission:** each item is resubmitted once with the fixed script.
  That uses the one resubmission allowed per item (§5 "resubmit once").
  `submit_ready.sh --relaunch-failed` allows it only for FAILED items with
  zero completed runs and exactly one prior submission.
- Nothing in §5, §6 or the clarifications changes.
