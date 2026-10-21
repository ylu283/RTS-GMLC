# Prompt 40: shed noise-floor re-estimate (executor PROGRESS)

Worktree `RTS-GMLC-floor40`, branch `floor40`, from origin/d6 at `2a604ff`
(2026-10-20). Zero PCM runs. Env: `/opt/anaconda3/envs/bogp-botorch/bin/python`.

## 0. Before computation

- [x] §0.1 expectation statement sent to Kay (in the session reply, before
  any computation), verbatim from the prompt.
- [x] Ledger state at start:
  - P1: r1–r4 graded, DONE.
  - N1: r1–r4 graded, DONE.
  - P2 and P3: r1–r3 graded; r4 is proposed with no objectives
    (`methods_C_P2_r4`, `methods_C_P3_r4`).
  - Part C therefore marks P2/P3 r4 as PENDING FINAL GRADE.
- [x] Solver comparability. Every pooled wave runs
  `multi_pem/multi_PEM_PCM.py` with no solver flags; the methods_C waves go
  through `analysis/methods_C/methods_array.sh`. The fixed options are
  `ruc_mipgap` 0.01, Gurobi, SCED threads 1, RUC horizon 36.
  - On d6, `multi_PEM_PCM.py` was last changed on 2026-08-22, and
    `multi_pem/parameters.py` and `utils.py` were also last changed on
    2026-08-22.
  - The first pooled C objectives landed on 2026-09-06
    (`contour_303x317_C`).
  - So every pooled wave ran the same driver, patch and solver options.

## 1. G0 (2026-10-21) — PASS

Pool: 1,573 runs.

| group | runs | waves |
|---|---|---|
| space-filling | 192 | n0, n0b, Q1–Q3, random_C, S2, S3 |
| BO rounds | 112 | bo_C_r1/r2, P1 r3–r4, P2 r1–r3, P3 r1–r3, N1 r1–r4 |
| grid | 1,269 | sweep_C, contour_303x317_C, 14 pairgrid_*_C |

- Pairs: 1,236,378 in total. 4 pairs have h = 0 (identical designs).
- **4,630 pairs have 0 < h < 0.15**, against the G0 threshold of 20.
- Smallest nonzero h = 0.0298.
- By origin, the h < 0.15 pairs are 4,530 grid–grid, 95 BO–grid, 4 BO–BO
  and 1 space-filling–space-filling. The small-h mass is almost entirely
  grid (sparse-retrofit axis and plane subspaces), as the prompt warned.

Difference from the prompt's measured expectation (about 4,758 pairs,
smallest h about 0.0066):

| convention | pairs < 0.15 | smallest h |
|---|---|---|
| pinned (blank = 0.0, lattice range 0.05–1.0) | 4,630 | 0.0298 |
| raw ω | 4,658 | 0.0283 |
| blank = 0.05 | 5,788 | 0.0039 |

- No tested convention gives 0.0066.
- The pair count under the pinned convention is within 3 % of the
  expectation, so I continue with the pinned convention.
- Disclosed in the report.

## 2. Pre-registration of the bins (written BEFORE any γ value is computed)

The prompt pins the estimator (Cressie–Hawkins, WLS line over the k = 4
smallest populated bins, weights = pair counts, intercept at h = 0). It does
not give bin edges, so they are fixed here:

- **Bins:** equal width 0.025 on (0, 0.15), giving 6 bins, and edges
  identical in every resample.
  - Pair counts (distances only): 0, 1, 817, 110, 1,057, 2,645.
  - So the pinned fit uses bins 2–5, centred at about 0.03, 0.06, 0.09 and
    0.11. Bin 2 holds one pair and gets weight 1.
- **Fit x value:** the pair-count-weighted mean h of the bin.
- **Populated:** at least 1 pair (resample weight > 0).
- **Bootstrap:** 2,000 resamples of the pooled DESIGN POINTS, numpy
  default_rng(20261021).
  - Pairs are rebuilt by multiplicity: an original pair (i, j) counts
    m_i·m_j times.
  - Copies of the same point form h = 0 pairs and are excluded.
- **Sensitivity rows (reported only, never used as floor_new):**
  - bin widths 0.0125 and 0.05;
  - k = 3 and k = 5 smallest bins;
  - the classical estimator;
  - a power-law fit.

## 3. Part A (2026-10-21) — ABSTAIN

- Point nugget 6.05e5 MWh² (sd 778).
- Bootstrap p5 / p50 / p90: −7.14e5 / 8.83e5 / 2.27e6. 18.9 % of resamples
  are ≤ 0, so p5 < 0 and the branch is **ABSTAIN**. √p90 = 1,505 MWh.
- Robustness rows (a) 1,631 and (b) 1,495 MWh: both ABSTAIN. The branch is
  unchanged.
- Resolution check: pure noise is recovered within 4 %. A smooth shed-scale
  function biases the pinned intercept by −3.9e6 MWh², so the method cannot
  resolve a floor of about 2,000 MWh or less.
- Four h = 0 cross-wave replicates; pooled sd 306 MWh (n = 4).
- log1p nugget < 0; only the high-shed stratum gives a positive nugget.
  Flag: level-dependent noise.
- Curt √p90 28.1k (×5.6) and cost √p90 $8.2M (×16.4): function variation,
  not noise. No change.

## 4. Part B — skipped (ABSTAIN branch)

## 5. Part C — band {300, 3000}

- The 3,000 row reproduces all four ledger τ values exactly.
- τ₃₀₀ = 0.13–0.14 × τ_old.
- At 300 MWh no arm stops. Flips:
  - P1 r2 (live): VERIFIABLE
  - P1 r3: VERIFIABLE
  - P1 r4: CENSORED
  - N1 r3: VERIFIABLE
  - N1 r4: CENSORED
  - P2 r3: PENDING (r4 not yet graded)
- Break-even shed floor for the first stop: P1 1,997, N1 1,726, P2 1,133 MWh.

## 6. Open

- [ ] P2/P3 r4 grade (10-21 arrays). Rerun `part_c.py` (read-only) and
  update the Part C table.
- [ ] Strategy session: consolidate. 1016-D2 → NXT-D3 replicate study.
  1016-D3 → stop rule provisional. Heteroscedastic model = Phase-B prompt.
