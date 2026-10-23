# REPLICATE_RESULT — prompt 41 replicate waves (measured shed noise floor)

Generated 2026-10-23 by `analysis/noise_floor/replicate_result.py` (permutation seed 20261023, 10,000 permutations, alpha = 0.05).
Inputs: `waves/replicate_C_noise_a` and `waves/replicate_C_noise_b` objectives (collector commits on d6, merged at `b0a6e1e`), the frozen parent waves, `part_a_replicates.csv`, and `replicate_run_metadata.csv`. The recipe is prompt 41 section 4, applied as pinned.

## 1. Data integrity

- All 12 runs landed. Both collectors report GATE PASS (6 run dirs each).
- All 12 `load_shed_mwh` values match the values read directly on CRC (asserted to 2 decimals in this script).
- The scp copies match the collector-committed `objectives.csv` byte for byte.
- The four accidental pairs reproduce `part_a_replicates.csv` deltas to < 1e-5 on all three objectives (asserted).
- Byte-identity findings below are asserted before they are printed.

## 2. Execution environment (mandatory disclosure)

**Nodes.** The job stdout does not record the host. `qacct` is unavailable on this cluster (no accounting file). The ONLY node records are live `qstat` observations during the runs: **tasks 5 and 6 of BOTH waves ran on `d12chas342` — the same node.** The nodes of tasks 1–4 of each wave are unknown. Consequences, stated plainly:

- The HIGH fresh exact pair (a:5 x b:5) is a **same-node** pair. Its delta = 45.70 MWh measures within-node, cross-job-instance variation, not cross-node variation.
- The LOW and MID fresh exact pairs may also have shared nodes; no record exists either way. Their delta = 0 results are therefore NOT confirmed cross-node measurements.
- The wave A -> wave B submission gap was about 6 minutes (implied starts 01:17 vs 01:22 ET on 2026-10-21), so the two waves ran concurrently. The scheduler weakened the cross-environment design intent. The label 'Population 1 = cross-environment' holds with certainty only for the pairs that straddle separate submissions days apart (fresh vs parent/twin, and the 4 accidental pairs).

**Runtimes** (wallclock = `Total simulation time` from the task logs; implied start = log end mtime minus wallclock):

| wave | task | design | role | node | wallclock (h) | end (ET) |
|---|---|---|---|---|---|---|
| a | 1 | LOW | exact | unknown | 14.94 | 10-21 16:13 |
| a | 2 | LOW | perturb-1 | unknown | 14.94 | 10-21 16:13 |
| a | 3 | MID | exact | unknown | 16.51 | 10-21 17:47 |
| a | 4 | MID | perturb-1 | unknown | 16.43 | 10-21 17:42 |
| a | 5 | HIGH | exact | d12chas342 | 23.82 | 10-22 01:06 |
| a | 6 | HIGH | perturb-1 | d12chas342 | 24.67 | 10-22 01:57 |
| b | 1 | LOW | exact | unknown | 15.46 | 10-21 16:50 |
| b | 2 | LOW | perturb-2 | unknown | 15.49 | 10-21 16:52 |
| b | 3 | MID | exact | unknown | 16.52 | 10-21 17:54 |
| b | 4 | MID | perturb-2 | unknown | 16.55 | 10-21 17:55 |
| b | 5 | HIGH | exact | d12chas342 | 24.26 | 10-22 01:38 |
| b | 6 | HIGH | perturb-2 | d12chas342 | 23.95 | 10-22 01:20 |

The HIGH corner tasks took 23.8–24.7 h; every other task took 14.9–16.5 h (asserted disjoint). Solve difficulty rises with shed level (about 1.5x at the all-0.05 corner). NOTE: a 31–33 h figure was reported from memory during the wait; the logs record 23.8–24.7 h, and the log values are used here.

## 3. Population 1 (PRIMARY): cross-environment exact draws

Estimator as pinned: per-design sample variance over distinct draws, df = draws − 1 (LOW 2, MID 3, HIGH 3, two standalone accidental pairs 1 each; total df = 10, asserted). Observed zeros are legitimate draws and are never collapsed. One design per stratum: design identity and shed level are confounded, so every per-stratum number below is a per-DESIGN number.

Draws (shed, MWh): LOW = 3 x 429.528861 (parent and both fresh exacts are byte-identical on ALL THREE objectives; both perturbed LOW runs are ALSO byte-identical to the exacts — the pv 1.0 -> 0.999/0.998 perturbation changed nothing on the deterministic plateau). MID = {4645.048205 (parent); 4671.72164 x3 — both fresh exacts are byte-identical to the twin `methods_C_P2_r1:5` on all three objectives}. HIGH = {38927.225397 (parent); 38065.316271 (twin); 37810.89226 (a:5); 37856.588432 (b:5)} — four distinct values. ACC-29k = {29181.754986; 29120.116627}. ACC-17k = {16912.379196 x2 (shed and curt identical; cost differs by 1,100.07 USD)}.

### shed (MWh)

| design | draws | df | sd | 95% chi2 CI on sd |
|---|---|---|---|---|
| LOW | 3 | 2 | 0 | degenerate [0, 0] |
| MID | 4 | 3 | 13.34 | [7.555, 49.73] |
| HIGH | 4 | 3 | 520.1 | [294.6, 1,939] |
| ACC-29k | 2 | 1 | 43.58 | [19.45, 1,391] |
| ACC-17k | 2 | 1 | 0 | degenerate [0, 0] |

**Pooled (pinned formula):** sd = **285.3**, df = 10, Satterthwaite nu = 3.02, 95% CI **[161.8, 1,057]**.
Fresh-only cross-wave subpopulation (3 exact pairs, df 3; disclosure, not the estimator): sd = 18.66, 95% CI [8.323, 595.3].

### curt (MWh)

| design | draws | df | sd | 95% chi2 CI on sd |
|---|---|---|---|---|
| LOW | 3 | 2 | 0 | degenerate [0, 0] |
| MID | 4 | 3 | 565.5 | [320.3, 2,108] |
| HIGH | 4 | 3 | 2,555 | [1,447, 9,526] |
| ACC-29k | 2 | 1 | 267 | [119.1, 8,519] |
| ACC-17k | 2 | 1 | 0 | degenerate [0, 0] |

**Pooled (pinned formula):** sd = **1,436**, df = 10, Satterthwaite nu = 3.32, 95% CI **[829.7, 4,848]**.
Fresh-only cross-wave subpopulation (3 exact pairs, df 3; disclosure, not the estimator): sd = 373.7, 95% CI [166.7, 1.192e+04].

### cost (USD)

| design | draws | df | sd | 95% chi2 CI on sd |
|---|---|---|---|---|
| LOW | 3 | 2 | 0 | degenerate [0, 0] |
| MID | 4 | 3 | 8.343e+04 | [4.726e+04, 3.111e+05] |
| HIGH | 4 | 3 | 5.469e+04 | [3.098e+04, 2.039e+05] |
| ACC-29k | 2 | 1 | 1.131e+04 | [5,048, 3.61e+05] |
| ACC-17k | 2 | 1 | 777.9 | [347, 2.482e+04] |

**Pooled (pinned formula):** sd = **5.476e+04**, df = 10, Satterthwaite nu = 5.22, 95% CI **[3.444e+04, 1.307e+05]**.
Fresh-only cross-wave subpopulation (3 exact pairs, df 3; disclosure, not the estimator): sd = 4.329e+04, 95% CI [1.932e+04, 1.382e+06].

A zero sample variance gives a collapsed chi2 interval [0, 0]. Read it as 'no variation observed in these draws', not as a proof that sigma = 0.

### Cross-date side table (mandatory disclosure)

Fresh (2026-10-21/22) vs historical draws of the same design, shed MWh. These deltas ARE part of the pinned Population-1 estimator above (the prompt counts parent and twin as draws); this table separates them from the fresh cross-wave deltas to show the across-submission component. NOTE: the historical runs landed 2026-10-10 to 10-18, i.e. 3-11 days before the replicate waves, not in a prior month; the 'cross-month' label used during planning overstates the gap.

| design | pair | delta shed (MWh) |
|---|---|---|
| LOW | replicate_C_noise_a:1 vs methods_C_P2_r3:7 | 0.00 |
| LOW | replicate_C_noise_b:1 vs methods_C_P2_r3:7 | 0.00 |
| LOW | fresh a vs fresh b (concurrent waves) | 0.00 |
| MID | replicate_C_noise_a:3 vs methods_C_P1_r3:8 | 26.67 |
| MID | replicate_C_noise_a:3 vs methods_C_P2_r1:5 | 0.00 |
| MID | replicate_C_noise_b:3 vs methods_C_P1_r3:8 | 26.67 |
| MID | replicate_C_noise_b:3 vs methods_C_P2_r1:5 | 0.00 |
| MID | fresh a vs fresh b (concurrent waves) | 0.00 |
| HIGH | replicate_C_noise_a:5 vs methods_C_P1_r3:3 | 1,116.33 |
| HIGH | replicate_C_noise_a:5 vs methods_C_P3_r2:3 | 254.42 |
| HIGH | replicate_C_noise_b:5 vs methods_C_P1_r3:3 | 1,070.64 |
| HIGH | replicate_C_noise_b:5 vs methods_C_P3_r2:3 | 208.73 |
| HIGH | fresh a vs fresh b (concurrent waves) | 45.70 |

Fresh-vs-fresh deltas (0 / 0 / 45.70) are much smaller than fresh-vs-historical deltas at HIGH (209–1,116) and MID (26.67 vs parent, 0 vs twin). Noise across submissions days apart is larger than noise across these two concurrent waves. The MID fresh runs reproduced the 2026-10-15 twin exactly, so the outcome set looks quantized: runs land on a small set of discrete solutions rather than spreading continuously.

## 4. Population 2: perturbed pairs (separate population)

Pairs = each perturbed run vs its fresh exact siblings and the two perturbed runs vs each other (5 per design, 15 total; the pairs share draws, so the dfs are nominal). sigma-hat per pair = |delta|/sqrt(2). The function-term envelope is reported BESIDE the numbers, never subtracted; it biases this population's floor UPWARD, i.e. toward KEEPING the recorded stops.

| design | pair | h | delta shed (MWh) | sigma-hat (MWh) |
|---|---|---|---|---|
| LOW | replicate_C_noise_a:2 vs replicate_C_noise_a:1 | 0.00105 | 0.00 | 0.00 |
| LOW | replicate_C_noise_a:2 vs replicate_C_noise_b:1 | 0.00105 | 0.00 | 0.00 |
| LOW | replicate_C_noise_b:2 vs replicate_C_noise_a:1 | 0.00211 | 0.00 | 0.00 |
| LOW | replicate_C_noise_b:2 vs replicate_C_noise_b:1 | 0.00211 | 0.00 | 0.00 |
| LOW | replicate_C_noise_a:2 vs replicate_C_noise_b:2 | 0.00105 | 0.00 | 0.00 |
| MID | replicate_C_noise_a:4 vs replicate_C_noise_a:3 | 0.00105 | 16.84 | 11.91 |
| MID | replicate_C_noise_a:4 vs replicate_C_noise_b:3 | 0.00105 | 16.84 | 11.91 |
| MID | replicate_C_noise_b:4 vs replicate_C_noise_a:3 | 0.00105 | 151.85 | 107.37 |
| MID | replicate_C_noise_b:4 vs replicate_C_noise_b:3 | 0.00105 | 151.85 | 107.37 |
| MID | replicate_C_noise_a:4 vs replicate_C_noise_b:4 | 0.00211 | 135.01 | 95.47 |
| HIGH | replicate_C_noise_a:6 vs replicate_C_noise_a:5 | 0.00105 | 2,299.25 | 1,625.82 |
| HIGH | replicate_C_noise_a:6 vs replicate_C_noise_b:5 | 0.00105 | 2,344.95 | 1,658.13 |
| HIGH | replicate_C_noise_b:6 vs replicate_C_noise_a:5 | 0.00211 | 528.94 | 374.01 |
| HIGH | replicate_C_noise_b:6 vs replicate_C_noise_b:5 | 0.00211 | 574.63 | 406.33 |
| HIGH | replicate_C_noise_a:6 vs replicate_C_noise_b:6 | 0.00105 | 1,770.32 | 1,251.80 |

Nominal pooled Population-2 sd (shed) = 697.5 MWh over 15 non-independent pairs.
Envelope on the estimated sigma, linear anchor gamma(0.068) = 2.52e6 MWh^2: 198 MWh at h = 0.00105 and 279 MWh at h = 0.00211. Quadratic smooth-function bound: 25 and 49 MWh. Both LOW perturbed runs were byte-identical to the exacts (delta = 0), so at LOW the function term is exactly zero at these h.

## 5. Homogeneity (pinned permutation test) and pooling verdict

Pinned test: permutation on the squared deltas, 10,000 permutations, alpha = 0.05, statistic = |mean(delta^2, Pop 1) − mean(delta^2, Pop 2)| (17 vs 15 pairs). Seed 20261023 (the prompt does not pin a seed; disclosed). Power is low at these dfs — disclosed as pinned.

| objective | observed mean-diff of delta^2 | p | verdict at alpha = 0.05 |
|---|---|---|---|
| shed (MWh) | 7.817e+05 | 0.1488 | POOL (homogeneity not rejected) |
| curt (MWh) | 3.314e+07 | 0.0054 | DO NOT POOL |
| cost (USD) | 7.485e+10 | 0.0013 | DO NOT POOL |

- Conditional pooled sd (shed (MWh)), Populations 1+2, nominal df 25: 569.6. This number is CONDITIONAL on the homogeneity verdict and is NOT the handoff scalar.

Across designs (the heterogeneity question): the fresh exact-pair deltas are 0 / 0 / 45.70 MWh at shed levels 429 / 4,672 / 37,834, and the per-design sds span 0 to 520 MWh. One pooled sd is NOT defensible as a description of the per-design noise; the pinned across-design claim is the variance-ratio test below.

## 6. Level dependence and the pinned rejection trigger

Pinned: ONE pre-registered claim — a one-sided HIGH-vs-LOW per-design variance-ratio test (alpha = 0.05) plus CI. Trigger = test rejects AND the point sd ratio exceeds 3.

| objective | sd HIGH | sd LOW | sd ratio | p (one-sided F, df 3,2) |
|---|---|---|---|---|
| shed (MWh) | 520.1 | 0 | infinite | 0 (degenerate) |
| curt (MWh) | 2,555 | 0 | infinite | 0 (degenerate) |
| cost (USD) | 5.469e+04 | 0 | infinite | 0 (degenerate) |

The LOW sample variance is exactly 0 on all three objectives (five byte-identical runs across three submissions: the 2026-10-18 parent wave and waves A and B). The F statistic degenerates: under any common sigma^2 > 0 the probability of an exactly zero df-2 sample variance is 0, so the test rejects at any alpha, and the point sd ratio is infinite (> 3). The CI on the ratio is degenerate and is reported as such. The prompt anticipated a zero LOW reading ('its shed noise may read 0') and pinned the trigger anyway.

**REJECTION TRIGGER (shed): FIRES.** The scalar-floor framing is REJECTED. The heteroscedastic Phase-B route opens regardless of prompt 42's route, per prompt 41 section 0 and section 4 (pinned).

## 7. Handoff

- Paper-grade floor by the pinned formula (pooled Population-1 cross-environment sd, shed): **285.3 MWh**, df 10, Satterthwaite nu = 3.02, 95% CI **[161.8, 1,057] MWh**. This replaces the preview estimate (sd 306, CI [180, 880], n = 4).
- **But the pinned rejection trigger FIRES**, so the scalar framing is rejected: do NOT hand a single floor to prompt 42 as paper-grade. The pooled value above is dominated by the HIGH design (nu ~ 3) and understates HIGH noise while overstating LOW/MID noise.
- Cross-environment exact-pair verdict: noise at identical inputs is **NONZERO** (HIGH fresh pair delta 45.70 on one node; HIGH cross-date deltas 209–1,116; MID cross-date delta 26.67). It is zero on the LOW plateau and between the MID fresh runs and the twin. Within-wave replay determinism is prior evidence and was not retested.
- The campaign floor (3,000 MWh) does NOT change in this prompt (pinned; Kay's decision after strategy review).

## 8. tau and the recorded stops

Prompt 40's break-even table puts the first-stop break-even floors at P1 1,997 / N1 1,726 / P2 1,133 MWh. The measured pooled sd 285.3 MWh sits below all three, and the whole 95% CI [161.8, 1,057] sits below P2's 1,133 MWh as well. Taken as a scalar, the measurement would flip every recorded stop and shrink tau by roughly 7x (prompt 40: tau_300 = 0.13–0.14 tau_old). But the trigger rejected the scalar framing: at HIGH-shed designs the per-design sd (520.1 MWh, chi2 CI up to 1,939) approaches the break-even floors, while at LOW it is 0. No re-grading happens here; prompt 42's machinery consumes this result, and the Phase-B heteroscedastic prompt opens.

## 9. Deviations and unpinned choices (full disclosure)

1. Permutation-test statistic (|difference of mean delta^2|) and seed (20261023) are not pinned by the prompt; both are fixed here before looking at the test outcome, and the test itself (permutation on delta^2, 10k, alpha 0.05) is as pinned.
2. 'Exact siblings' for Population 2 = the fresh in-wave exacts only (not the historical parents), keeping Population 2 inside the replicate waves.
3. Population-1 pair list for the permutation test = all within-design pairs over the distinct draws (17 pairs). This follows section 4's enumeration with the accidental pairs entering exactly once (dedup).
4. The variance-ratio test is degenerate at s2_LOW = 0; the p-value is the limit value 0 and the ratio CI cannot be formed. Disclosed in section 6; the trigger decision does not depend on the CI.
5. Node identity for 8 of 12 tasks is unrecoverable (no hostname in stdout, no SGE accounting). Disclosed in section 2 with consequences.
6. The runtime figure quoted from memory during the wait (31–33 h for HIGH) does not match the logs (23.8–24.7 h); the log values stand.
7. No figures: the result is three small tables; a figure adds nothing. (House rule on bold axes therefore does not apply.)

Integrity checks run by this script: CRC shed cross-check (12/12), part_a delta reproduction (4 pairs x 3 objectives), byte-identity asserts (LOW x5, MID fresh = twin, ACC-17k shed), omega identity of fresh exacts across waves, single-tier perturbation check per Pop-2 pair, df total = 10, pair counts 17 and 15, HIGH/other runtime separation.
