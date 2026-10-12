# PREREG — prompt 37 (v2): stop-rule validation on truth-known problems

Status: **pre-registered before any trajectory** (2026-10-12; commit = the
first commit that contains this file). Anything added after results is
labelled *post hoc*. Branch `stoprule` (worktree `RTS-GMLC-stoprule`, from
`origin/d6` @ d1e3814), dir `trial_0826/campaign/analysis/stoprule/`.

Code: `sr_common.py` (copies of the frozen Stage-2 pieces), `problems.py`
(builders), `runner.py` (trajectories), `rules.py` (rules + metrics),
`collector.py`, `make_tasks.py` → `tasks.csv` (CRC) / `local_tasks.csv`,
`crc/` (array + collector), `m3_qnehvi.py` (M3). Tests:
`tests/test_stoprule.py` (75 pass in `bogp` and in `bogp-botorch`).

## 1. Frozen inputs

- bo-gp `feat/qparego` @ `60e6328` via `BOGP_PATH`; every entry point runs
  `assert_bogp()` (path under `BOGP_PATH`, SHA `60e6328…`,
  `PYTHONNOUSERSITE=1`). CRC: `/groups/adowling/ylu28/bo-gp`, same SHA check.
- Live rule S0 constants copied from `acquire_next.cmd_init`: R = nadir of
  the starts + 10 % span; τ = std (ddof 0) of HV over 1,000 perturbations
  of ALL starts with N(0, floor²), no clipping, MC seed 20261006; gains
  strict `<`; window 2; hard cap 4. Unit test: the live Stage-2 ledger
  (τ 5.263e16; gains 3.63e16, 9.18e15) stops at r2.
- M1 call path: `propose_qparego_batch(X, Y, q, candidates=…, seed=…)` under
  `gpytorch.settings.fast_pred_var()` (LOVE cache; exact while n < 100 —
  here n ≤ 96) with the `_ei_chunked` replacement of
  `_qparego.expected_improvement` (copied, chunk 20,000). No ledger,
  marker, push or submit function is called.
- M3 = prompt 35's N1 acquirer, copied verbatim from the main clone's
  `analysis/methods_C/qnehvi.py` (uncommitted there; source sha256
  `d30ed5f89c9640fc430ea6558029873ce2584350a68e92d9653205ca1e3f080f`),
  plus `batch_ehvi` (S-model). SingleTaskGP per objective mirroring PredGP
  (z-scored X/y, Matérn-5/2 ARD, noise ≥ (floor/σ_y)², bogp `train_gp`),
  qNEHVI 128 Sobol-QMC samples, sequential greedy over the discrete
  candidates, float64, objectives and ref negated after z-scoring.
- M4 = uniform random lattice points without repeats.
- M2 (BoTorch qNParEGO) is **conditional**: run only if |median(M1) −
  median(M3)| of H_n^true/τ_j > 1 at n = 64 or n = 96 on the pooled
  primary problems; then 20 seeds × E-path-1…5, labelled "implementation
  contrast". M5 (Sobol) is cut.
- Calibration audit = PredGP (copied from `acquire_next.PredGP`, float32,
  Adam 700 epochs, noise ≥ floor²), same statistic as BO_STAGE2 §3:
  RMS(z), 95 % coverage, "calibrated" iff RMS ∈ [0.7, 1.3] and coverage ≥ 80 %.

## 2. Problems

6-D, 9⁶ = 531,441-point Stage-2 lattice; M = 3 {shed, curt, cost}, all
minimized, physical units. Truth = a deterministic function on the
lattice, its global non-dominated set precomputed (O(n log n) skyline,
`nd_mask_3d`; exact 3-D HV `hv3d`; both tested equal to bogp).

| id | definition | role |
|---|---|---|
| E-path-1…5 | GP posterior sample paths (RFF prior, 4,096 features, + exact pathwise update) on the 96 Stage-2 designs (32 starts + 16 BO + 48 random); kernel Matérn-**3/2** ARD on [0,1]-scaled inputs, Gamma(3,6) lengthscale and Gamma(2,0.15) outputscale priors, noise ≥ (floor/σ_y)², MAP by Adam (600 it, lr 0.05, float64); one path per objective | **primary** |
| E-mean | posterior mean of the same fit | secondary (smooth) |
| E-short | one sample path, every lengthscale × 0.5 | secondary (hard) |
| Z-needle | DTLZ2 (n = 6) + a Gaussian well (depth 0.5, width 0.15) at u₃..₆ = (1, .5, .5, .5) active for u₁ ≥ 0.75 — moves the f₃-heavy front corner inward | positive control (early stops) |
| Z-plateau | DTLZ2 with shed = max(0, f₁ − its 40th lattice percentile) | positive control (flat objective) |
| Z-dis | DTLZ7 (M = 3, n = 6), disconnected front | stress |
| R-A/B/C, R-PG (14 `pairgrid_*_C`; the 15th pair is contour C = R-C) | Stage-1 replay tables, 81 cells, 4 objectives (`replay.OBJECTIVES`), floors incl. the 60-start working floor | method comparison ONLY, **noise-free** |

- Z outputs: per objective, the [1 %, 99 %] lattice quantile range maps
  affinely onto the observed Stage-2 [min, max] of the 96 designs.
- Noise (6-D): N(0, (m·ρ_i·span_i)²); ρ_i = floor_i / (range of the 96
  observed Stage-2 values); span_i = range of the problem's truth at the
  96 Stage-2 designs; m ∈ {0.5, 1, 2}. The rule's τ MC uses the actual
  noise sd (the rule knows its floor, as live). Draws keyed by (problem,
  m, seed, lattice index) → common random numbers across methods.
- Start sets: 6-D: 32 points from a fresh scrambled Sobol (d = 6, seed
  per replicate, `u → min(⌊9u⌋, 8)`, duplicates skipped), identical for
  every problem/method within a seed, never the Stage-2 starts. 2-D: 5
  random cells per seed (replay convention).
- Truth files: `problems/<id>.npz` (gitignored), deterministic rebuild
  `python problems.py build`; sha256 of the float64 truth array:

| id | non-dominated lattice points | noise sd at m = 1 (shed, curt, cost) | RMSE vs Stage-2 obs at the 96 (shed, curt, cost) | Stage-2-design density (noisy / 48; real 26) | truth sha256 |
|---|---|---|---|---|---|
| E-path-1 | 1,135 | 2,254 / 4,948 / 0.50M | 2,173 / 5,193 / 0.48M | 24 | `62fc731920dd3e3c6eab983fe47b5f00f651aedc8df9405d5ec55255f6648d31` |
| E-path-2 | 1,355 | 2,421 / 4,955 / 0.50M | 1,957 / 5,530 / 0.54M | 22 | `81ba31fd226fe25b5de3b952928a47107ab6ea1d7500f33489e5c4b3c9cad2b7` |
| E-path-3 | 783 | 2,100 / 5,010 / 0.50M | 2,283 / 6,050 / 0.54M | 25 | `f0bbec491883b0d555938495839fbbb2df1968f6cc42780dd8036c5ae88468b4` |
| E-path-4 | 1,425 | 2,433 / 4,958 / 0.50M | 2,202 / 6,071 / 0.49M | 26 | `524f5a8d8fce4b8c3011cc5c0b56417a92c739616246d3e93753b2f0e888e2eb` |
| E-path-5 | 1,182 | 2,407 / 4,957 / 0.50M | 2,096 / 5,242 / 0.60M | 24 | `65ed628f4139f22ce106140fbb3a1d7e73081f5df3498a2e0293cf005279be43` |
| E-mean | 3,724 | 2,072 / 4,989 / 0.50M | 1,219 / 561 / 0.06M | 26 | `314b5199011d14fa174d1f9720cde4bac8d6be2b02b3b35191942c2400d1e95b` |
| E-short | 486 | 2,208 / 4,993 / 0.49M | 2,508 / 6,434 / 0.58M | 31 | `5dba4cf00371cd56693a8ee806d5c658d23e3ca77406d6a4916d2b31ab7a78d0` |
| Z-needle | 60 | 3,766 / 5,376 / 0.56M | 11,182 / 424,440 / 35.06M | 28 | `4d13bd555b0d439356dbd6770b48bc4048429648bb1fb172ca430bcf3331b973` |
| Z-plateau | 52 | 3,939 / 5,376 / 0.56M | 10,178 / 424,442 / 35.05M | 24 | `530eb3920774e77c59d837af50c84adecac1e0b420c30b7c8960881541bfb284` |
| Z-dis | 25 | 3,000 / 5,000 / 0.48M | 15,391 / 594,309 / 34.62M | 10 | `3ded4f5d62efdb51a3a7076fc1953155b584cf579c1636c00db7a81234e41385` |

ρ (Stage 2, floor / observed range of the 96) = 0.1028, 0.0041, 0.0032 (shed, curt, cost). Z-needle basin: 891 cells (well ≥ 10 % of depth and not weakly dominated by the base DTLZ2 front; listed in problems.json); P(random hit within 64) = 0.102; 24 of the 60 true-front points; 15 % of H* at R_union. Replay-grid table sha256s are in problems.json. Rebuild determinism checked (E-path-1 rebuilt → identical sha256).

Emulator fit (E-fit, Matérn-3/2; reported, not a gate): LOO Q² shed/curt/cost = 0.808 / 0.972 / 0.997; LOO RMSE/floor = 0.70 / 7.04 / 3.51; LOO RMS(z) = 0.53 / 0.68 / 0.49 (over-dispersed); worst design bo_C_r2#3 for all three. Holdout (32 starts + 48 random → BO's 16): E-fit RMSE 4,804 / 98,360 / 5,005,672 vs PredGP 4,122 / 78,629 / 3,393,836 (PredGP RMS(z) 1.09 / 1.69 / 0.85).

## 3. Runs

Every 6-D run executes 8 rounds of q = 8 (n = 32 → 96; q = 4: 16 rounds);
rules are applied post hoc. 2-D: n₀ = 5, q = 2, 15 rounds (n = 35).

| block | problems | methods | noise m | q | seeds | where |
|---|---|---|---|---|---|---|
| A primary | E-path-1…5 | M1, M3 (+M4) | 1 | 8 | 0–49 | CRC (M4 Mac) |
| B noise | E-path-1…5 | M1, M3 (+M4) | 0.5, 2 | 8 | 0–3 (20 pooled) | CRC (M4 Mac) |
| C secondary | E-mean, E-short, Z-needle, Z-plateau, Z-dis | M1, M3 (+M4) | 1 | 8 | 0–19 | CRC (M4 Mac) |
| D batch size | E-path-1…5 | M1, M3 (+M4) | 1 | 4 | 0–1 (10 pooled) | CRC (M4 Mac) |
| E replay | 17 grids | M3 | — | 2 | 0–19 | CRC (≈ 7 min/run here) |
| R replay | 17 grids | M1, M4 | — | 2 | 0–19 | Mac |

`tasks.csv` = 1,140 CRC tasks; `local_tasks.csv` = 1,080 Mac tasks.

**Candidate rule (M1, M3; pre-registered).** Projected full-lattice total:
M3: 35's G4 = 962 s wall × 4 threads ≈ 1.07 core-h per full-lattice
proposal at n = 40 → ≥ 8.5 core-h per 8-round run × 400 6-D M3 runs ≥
3,400 core-h > 1,500 →
**subset rule for every 6-D M1/M3 round**: 20,000 uniform unevaluated
lattice points (seed = (1005, problem, seed, round)) ∪ the unevaluated
±1-level single-coordinate lattice neighbours of the current observed
non-dominated designs. 2-D: all unevaluated cells. M4 draws from the whole
unevaluated lattice.

**Seeds.** All streams are `SeedSequence([20261012, …keys])`: starts
(1000, seed); acquisition (1001, problem, method, seed, round); M4 (1004,
problem, seed, round); candidates (1005, …); noise (problem, 0, m·100,
seed, index); `torch.manual_seed` per round from the acquisition seed;
PredGP audit `torch.manual_seed(0)`. Determinism: bitwise on one platform
(tested: resumed run = uninterrupted run); Mac vs CRC not bitwise (float
paths differ) — no cross-platform equality is claimed.

**Crash policy.** Tasks checkpoint per round and resume. Missing tasks after
the collector are listed in `summary/MISSING.txt` and resubmitted once by
Kay; still-missing runs are reported missing (no imputation); a cell with
< 80 % of its runs is flagged "incomplete" and makes no claim.

**If `BOGP_CRC_botorch` never appears:** all M3 rows are "not run"; Kay
submits the M1 rows only (`tasks_M1.csv`, same row content); every
M1-vs-M3 statement is reported as not tested; the primary cell (M1) is
unaffected.

## 4. Stopping rules (post hoc, same trajectories)

gain_k = H̃_k − H̃_{k−1} (observed, noisy, box R_j). Stop round s ∈ 1..R.
- **S0**: stop after k if the last w gains < τ (strict); τ ∈ {0.25, 0.5,
  1, 1.5, 2}·τ_j and τ ∈ {1, 2, 5, 8, 10} % of H̃₀; w ∈ {1, 2, 3}; cap
  K ∈ {4 (primary), 8}.
- **S-fix-k**, k = 1…8.
- **S-rel**: stop after k when gain_k < c·H̃_k, c ∈ {1, 2, 5} % (window 1).
- **S-model** (M3, 6-D): ehvi_k = E[HVI of batch k] at R_j under M3's
  posterior, 256 Sobol-QMC samples, computed at proposal (data ≤ k−1).
  Stop after k if ehvi of batches k−w+2 … k+1 are all < τ_j (the last one
  is then not evaluated); cannot fire at k = R. w ∈ {1, 2, 3}.
- **S-OCD-style**: Wagner, Trautmann & Naujoks (EMO 2009, "OCD") stop when
  EITHER test indicates convergence — verified against the paper's
  description; we use OR. Series = all gains so far g₁..g_k, k ≥ 3:
  (a) one-sided χ² test (k−1)s²/τ_j² < χ²_{0.05, k−1} (variance below
  τ_j²); (b) two-sided t-test on the OLS slope of g vs round, p > 0.05 (no
  trend). The prompt's "Trautmann et al. 2009" citation is the offline
  predecessor (Evol. Comput. 17(4)); OCD is the EMO 2009 paper.
- **Oracle**: s = argmin_{r∈1..R} (H* − H_r) + τ_j·r (truth known).
- Makarova 2022, Ishibashi 2023, Wilson 2024: cited, not implemented
  (scalar simple-regret bounds; no HV analogue).

## 5. Definitions and metrics (verbatim from the prompt, operationalized)

Run j: noisy observations Ỹ; box R_j = nadir of its noisy starts + 10 %
span; τ_j from the MC on its noisy starts. Truth H_k = HV(f(X_{1:k}), R_j)
with f noise-free; H* = HV(true lattice front, R_j).
- **Early stop:** the rule stops at round r < K (and r < R) and
  max_{r < m ≤ min(r+4, R)} (H_m − H_r) > τ_j (CUMULATIVE true gain).
- **Cap stop:** the rule reaches K without firing — own category.
- **Late stop:** r* = the first round r ≥ 1 with max_{r < m ≤ min(r+4, R)}
  (H_m − H_r) ≤ τ_j; the rule is late if s > r*; wasted rounds = s − r*.
  (A w-round rule's detection delay counts as wasted; reported as is.)
- **Regret at stop:** (H* − H_s)/H* and (H_R − H_s)/τ_j.
- **Compute:** s·q evaluations; saved vs S-cap = (K − s)·q.
- **Gain noise null:** rounds with true gain H_k − H_{k−1} < 0.1·τ_j:
  distribution of observed gain/τ_j; false-continue rate = P(observed gain
  ≥ τ_j | true gain < 0.1 τ_j); spread (CV) of τ_j across seeds per problem.
- **Stage-2 conditional check:** runs (M1, m = 1, q = 8, all 6-D
  problems) with observed g₁/H̃₀ ∈ [3.5, 7.5] % and g₂/H̃₀ ∈ [0.5, 2.5] %;
  report the true remaining gain H₄ − H₂ and H₈ − H₂ in τ_j and % of H₀.
  If < 10 runs match: widen to [2.5, 10] % and [0, 4] % (fallback,
  pre-registered).
- **Calibration audit vs error:** audit_k = per-objective RMS(z) of batch k
  under PredGP fit on rounds < k (all methods, 6-D). Outcome =
  shortfall_{k+1} = (Ĥ_{k+1} − H_{k+1})/τ_j, Ĥ_{k+1} = HV of the PredGP
  mean (fit on rounds ≤ k) at X_{1:k+1}. Spearman(max_i |log RMS_i|,
  |shortfall|) and the binary verdict, stratified by problem AND round;
  descriptive, no p-values.
- **Density:** share of observed points non-dominated at the stop round vs
  the stop round (limit 3).
- **Method comparison at fixed budget:** H_n^true/H* and (H*−H_n)/τ_j at
  n = 64 and 96 per seed (2-D: n = 21, 35, H/H* only); all seeds plotted,
  median + IQR; paired differences M1 − M3 in τ units. No p-values.
- Boxes: R_frozen (primary) and R_union = true-front nadir + 10 % of the
  true-front span (sensitivity; τ recomputed by the same MC in that box).

## 6. Primary cell and acceptance (the one confirmatory claim)

E-path-1…5 pooled × M1 × S0 (τ = 1·τ_j, w = 2, q = 8, K = 4, R_frozen),
m = 1, **50 seeds per path** (250 runs). Endpoints with seed-bootstrap
95 % CIs (10,000 resamples stratified by path, seed 20261012):
(i) early-stop rate; (ii) median (H_R − H_s)/τ_j.

**Acceptance:** early ≤ 20 % AND median regret ≤ 1 τ AND S0 lies on or
below the S-fix-k line — the median (H_R − H_s)/τ_j of S0 is ≤ the linear
interpolation of the S-fix-k medians at S0's mean stop round — on the
pooled primary problems AND on Z-needle (M1, 20 seeds). Every other cell:
complete heatmaps, labelled secondary, 20 seeds.

**Z-needle validity:** the control is informative only if a basin cell
(listed in `problems.json`) is queried in ≥ 25 % of M1 or M3 runs by
round 8; otherwise it is reported "positive control inconclusive (needle
not found)" and the acceptance uses the primary problems alone, said
plainly.

**Uninterpretable patterns — pre-registered reading** (prompt §5, verbatim):
S0 ≡ S-fix-2 almost everywhere → "the rule acts as a 2-round budget at
this τ", report the τ at which it starts to adapt; all true per-round
gains < τ from r1 → "trivially safe; problems too easy" → lean on
Z-needle / E-short; all methods tie on an easy problem → no method claim
from it; regret driven by H* (budget-limited) → report (H_R − H_s) as the
stop's own regret. The replay grids are dense (M = 4: 15–77 of 81 cells
non-dominated, R-C 73) — expected to tie.

**HV metric:** raw HV primary; prompt 35's floor-robust HV for cross-check.

**q = 4** (block D, `rules.apply_q4`): S0 with cap = 32 evaluations (8
rounds of 4, the live budget) and τ unscaled (w = 2) vs τ·q/8 (w = 2) vs a
16-evaluation window (w = 4 rounds of 4, τ unscaled), applied to the same
trajectories.

## 7. Emulator checks (reported, not gates)

LOO of the E-fit (RMSE, /floor, Q², RMS z, coverage); holdout (fit on 32
starts + 48 random → predict BO's 16 picks) for the E-fit and PredGP;
front density at the 48 Stage-2 designs under each problem's truth +
noise vs the real 26/48. Caveat: the emulator is smoothest where the data
are densest; the corners where the real GPs failed are where it is least
reliable.
