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

---

# Prompt 41: replicate waves (executor PROGRESS)

Worktree `RTS-GMLC-rep41`, branch `rep41`, cut from `floor40` at `4801f03`.
That commit sits on origin/d6 `2a604ff`; at the 2026-10-21 fetch, d6 had
nothing newer, so the "pull d6 before selecting" step is satisfied.
Expectation statement (§0.1): verbatim in both wave READMEs.

## Build (2026-10-21), done

- [x] **Selection rule re-run** on the 304 non-grid pooled runs (P2_r4 and
  P3_r4 have no objectives yet). It reproduces the expected picks exactly:
  - LOW `methods_C_P2_r3:7`, shed 429.528861. 6-way plateau tie, broken
    by wave sort.
  - MID `methods_C_P1_r3:8` (≡ `P2_r1:5`).
  - HIGH `methods_C_P1_r3:3` (≡ `P3_r2:3`, all-0.05).
- [x] **Waves built** from clean commit `4598462`: `waves/replicate_C_noise_a` and
  `waves/replicate_C_noise_b`, 6 rows each, built with `make_row(rho_h2=2.0)` and
  `write_wave` (manifest: dirty = False, `replicate_rows`, `selection`).
  - Rows 1, 3, 5 are exact copies; rows 2, 4, 6 are perturb-1 (A) /
    perturb-2 (B).
  - Realized values: 0.999/0.998, 0.7635/0.7615, 0.051/0.052. All are
    exact at 4 decimals.
- [x] **Exact copies are byte-identical** to the parent dicts and design rows,
  and to the twins `P2_r1:5` / `P3_r2:3`.
- [x] **Array scripts:** `submit_array.generate_script(max_concurrent=None)`.
  - The diff vs `random_C_array.sh` is `-N`, `-t 1-6` and a comment only.
  - No `-tc`, no `-pe`, no PYTHONNOUSERSITE.
- [x] **Collectors:** `_render_random_collector(<wave>, 6)`.
  - The diff vs `collect_random_C.sh` is the wave name and N only.
  - `-r n`, and PYTHONNOUSERSITE=1 (deliberate).
- [x] **No pool contamination:** `pool.wave_groups()` contains no `replicate*`.
- Expected Population-1 df:
  - LOW: 3 draws (parent + 2 exact), df 2.
  - MID: parent, twin + 2 exact, df 3.
  - HIGH: the same as MID, df 3.
  - Standalone accidental pairs `bo_C_r2:3≡P2_r3:6` and
    `P1_r4:8≡P3_r3:1`: df 1 each.
  - **Total 10.**

## Submit (Kay), done 2026-10-21

- Submission JIDs: wave A array 1600195 / collector 1600196; wave B array
  1600212 / collector 1600213. The A→B gap was about 6 minutes, so the
  waves ran concurrently (disclosed in the result).

## After landing (2026-10-23), done

- 12/12 runs landed; both collectors GATE PASS and pushed to d6
  (`b455ee9`, `b0a6e1e`). rep41 fast-forwarded onto origin/d6.
- Fetched objectives cross-checked against values read directly on CRC:
  12/12 match. scp copies byte-identical to the collector commits.
- `replicate_result.py` runs the §4 pinned recipe and writes
  `REPLICATE_RESULT.md`. Headline (shed): pooled Population-1 sd
  **285.3 MWh**, df 10, Satterthwaite ν ≈ 3.0, 95% CI **[162, 1,057]**.
  Per-design sd: LOW 0 / MID 13.3 / HIGH 520 / ACC-29k 43.6 / ACC-17k 0.
  Permutation homogeneity (10k, α 0.05): shed p = 0.149 (pool not
  rejected; conditional pooled 569.6, NOT the handoff), curt p = 0.005
  and cost p = 0.001 (do not pool). **Rejection trigger FIRES** (LOW
  variance exactly 0 on all objectives → ratio infinite, test degenerate
  → rejects): scalar-floor framing REJECTED, heteroscedastic Phase-B
  route opens. Campaign floor unchanged (pinned).
- Node disclosure: only tasks 5/6 of BOTH waves have a node record
  (d12chas342, same node, live qstat); stdout has no hostname and qacct
  has no accounting file, so tasks 1–4 are unknown. The HIGH fresh exact
  pair is same-node. Runtimes from logs: HIGH 23.8–24.7 h, others
  14.9–16.5 h (a 31–33 h figure circulated during the wait does not
  match the logs).
- `replicate_run_metadata.csv` holds per-task runtime/node provenance.
