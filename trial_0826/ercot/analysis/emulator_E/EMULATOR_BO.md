# EMULATOR BO dry run on the committed GPs (prompt 66, 2026-11-24)

**EMULATOR. This is a machinery check, not a result.** No PCM ran. No CRC job ran. Nothing here enters a ledger, the plan, a decision row or the paper's claims. "Truth" means the emulator's truth (the posterior mean of the committed GPs), not the ERCOT system.

## Answer in two minutes

1. **Did the BO machinery run end to end on ERCOT?** Yes, after one change to 55. As built, the multi-seed init crashed at seed 1. qNEHVI puts 4–5 of the 8 r1 designs on the same box vertices in every seed lane, and 55 asserted disjoint r1 sets. I relaxed the assert to the prompt-55 text ("sets differ"). After that change, 12/12 single-objective runs and 15/15 multi-objective lanes finished. Each scenario took its expected branch: s0 monitor to the cap, s1 constrained from r2, s2 HALT at r1. **Kay: accept or reject this change (section 7, change 2c).**
2. **Are the committed GPs good enough to drive it?** They are good enough to steer, but not to check themselves. On this emulator, BO gets to 0.18 B (V1) and 0.011 B (E1) of the emulator optimum by round 4 on 3/3 seeds — but the r0 start-set GP's own optimum already has regret 0.09 / 0.006 B, so this measures optimize_acqf and bound handling, not search. The front reaches 0.975–0.979 of the best-known emulator front. The house fit sets the noise sd at 6× (V1) and 2.3× (E1) the emulated chatter. Every 95 % band is too wide (rms z 0.07–0.59), so C2 and C3 cannot fire. Do not read "C2/C3 = 0" as evidence of calibration.
3. **What changes with a converged fit?** The nearest proxy for fit v2 is the long fit (exploratory, 10,000 steps) (it is NOT v2 — no priors, single start). It gives the same search result (V1 ≤ 0.09 B, E1 0.028 B, HV 0.973). The gates get power: C2 fires at E1 r1 on 3 of 3 seeds. Two causes: all 8 r1 designs lie outside the start set's hull, and the r0 long fit sets the E1 noise at $18k, 0.05× the chatter (noise collapse). Expect C2 REVIEW flags at r1 under fit v2 unless v2 gives a stable noise estimate.
4. **What remains before a real launch?** Land fit v2, then rerun this dry run (truth and BO GP both change; add the v2 convergence flag per round fit). Decide the 55 r1-assert change (item 1) and E-D7. Decide what a C2 flag at r1 on an out-of-hull batch means (review, not halt; report hull distance). Replace the repeat-design assert in propose_round with a declared rule. Align dry_round_E.py. Decide the cross-lane duplicate-vertex runs (≈ 17 of 40 r1 runs under option C). The full checklist is section 8.

**Limits of this test.** Both emulator optima sit on box vertices outside the data. f*(V1) is 19 B below the lowest observed V1. f*(E1) is 12.7 B below the lowest observed E1. The regrets measure how well the machinery finds a vertex. They do not measure the ERCOT optimum. Both front end points lie outside the R box (V1-corner E1 $8,166.9M > R_E1; E1-corner V1 5.21 TWh > R_V1), so the extrapolated V1 corner adds zero HV.

## 0. Verdict

| # | check (prompt 66 pass criteria) | result | verdict |
|---|---|---|---|
| 1 | No crash: 12 single-objective house runs and 15 multi-objective house lanes finish; each lane ends where its scenario says | 12/12, 15/15, ends as expected | PASS after a 55 fix. As built, the multi-seed init CRASHED at seed 1 (section 7, change 2c) |
| 2 | C1 ingest passes on every emulated round (55 `ingest_gate`) | 49/49 rounds | PASS |
| 3 | C2/C3 flag counts at or below nominal (Poisson 95 % limit of the expected count) | C2 0, C3 0 in 114 (round, objective) cells; expected C2 0.042 | PASS — NO POWER. The Poisson limit is 0 flags, and the house-fit bands are 2–6× too wide (§4.3). With a converged-fit proxy, C2 fires 3 times (§5). |
| 4 | Single-objective BO within 2 B_j of the emulator optimum by round 4 on >= 2 of 3 seeds | V1 3/3; E1 3/3 | PASS (easy case: both optima are box vertices, and optimize_acqf goes to vertices) |
| 5 | Single-objective BO beats random-8 at matched budget (round 4, 80 evaluations) on every objective | On this emulator, where both optima are box vertices outside the data hull: V1 0.18 B vs 18.7 B; E1 0.011 B vs 12.3 B; every seed. Uniform draws in [0,1]^6 almost never reach a vertex, so this gap does not predict the gap on PCM. | PASS |
| 6 | Multi s0 (clean): 4 rounds, monitor mode, no halt, 5 lanes | yes | PASS |
| 7 | Multi s1 (one shed violation in r1): mode flips at r1; r2–r4 constrained qNEHVI with the shed GP; the violating run is out of HV (n_hv 55/63/71/79); 5 lanes | yes | PASS |
| 8 | Multi s2 (two violations in r1): `HALT_FOR_DECISION.md` written; `propose --round 2` refused; 5 lanes | yes | PASS |
| 9 | tau_exact = 0 -> budget-cap-only: gain/tau_exact null, would_stop never fires, every lane runs to the cap | yes | PASS |
| 10 | R2 and N1_off monitors at base + chatter raise no flag | R2 max 210.5 MWh (< 312.16); N1_off max 30,954 (dN1_off < 462.7) | PASS |
| 11 | HV fraction of the best-known emulator front reported (no threshold) | s0 round 4, true f: 0.975–0.979 of the best-known front. The reference is a lower bound on the true front, so these fractions are upper bounds | reported |

p_random = 1 [1, 1] in every lane has no power. All 48 random designs together reach only 0.714 of the front, and BO's r1 already reaches 0.92–0.93. The matched-budget baselines in §3.2 give the effect size instead.

## 1. Emulator (prompt 66 §1)

- Training rows: the n* = 48 grading rows of `n0_E` (Sobol 0–47), read by the real 54 loader `analysis.ercot_gp.ercot_gp_loader.load` with `waves/design_space_E_2026-11-24.json`. 0 refused, 0 SUSPECT, R1 max 0.
- Fit: `ercot_gp_status.fit` (D-1025 FlexGP, `bogp.train_gp` Adam 700 steps, lr 0.01, float32, `torch.manual_seed(0)`), floor 0 → inferred-only 1e-9. This is the house fit, the code path 54 used for `committed_configs.json`.
- f_j(u) = the posterior mean, frozen in a float64 closed form (`emulator_E_params.json`). It matches FlexGP's mean on 1,024 Sobol points to 17 MWh (V1), $403 (E1) and 0.003 (N4). The refit reproduces the committed hyperparameters to ≤ 3.1e-06 relative.

| id | role | arm | ARD lengthscales (u; 110 / 140 / 146 / 163 / 270 / 274) | outputscale sd | noise sd | f* at u* | f* (Sobol 2^14) |
|---|---|---|---|---|---|---|---|
| V1 | seated | rbf+std | 1.8501 / 1.9054 / 1.8491 / 1.9502 / 1.4780 / 1.2010 | 7.5901e+05 | 17,368 | 1.04734e+06 at [1.00, 0.98, 1.00, 0.76, 1.00, 0.97] | 1.0985e+06 |
| E1 | seated | m52+std | 1.6064 / 1.8450 / 1.7461 / 1.8987 / 1.2859 / 0.9575 | 1.8343e+07 | 8.2675e+05 | 8.08405e+09 at [0.00, 0.00, 0.00, 0.15, 0.00, 0.00] | 8.08826e+09 |
| N4 | co-reported | m52+std | 1.7693 / 1.9323 / 1.7497 / 1.9444 / 1.2956 / 1.1264 | 322.99 | 14.35 | 3,574.15 at [1.00, 0.95, 1.00, 0.37, 1.00, 1.00] | 3,635.98 |

Caution: both emulator optima are extrapolations to box vertices. f*(V1) = 1.047 TWh at the all-PEM corner is 0.36 TWh (19 B) below the lowest observed V1 (1.409 TWh). f*(E1) = $8,084.05M near the no-PEM corner is $23.6M (12.7 B) below the lowest observed E1 ($8,107.63M). The regrets below are measured against these extrapolations. They test the machinery, not the ERCOT optimum.

- Observation: y = f(u) + eps, eps ~ N(0, Sigma_c[V1, E1]) from `analysis/noise_v3/ercot_noise_seed_sigma_c.csv` (prompt-63 Seed chatter, LW-shrunk): sd V1 3,275 MWh, sd E1 $0.398M, corr 0.205.
- Streams: numpy `default_rng([6666, family, seed_id, scenario, variant])`. BO and its random baseline share one stream (common random numbers).
- Start set: the 48 n0_E designs with EMULATED values f(u_i) + eps_i (`default_rng(6666)`, first 48 × 2 draw). One generating process makes every Y the BO sees.
- Guardrails: R1 = 0 (except injected rows), R2 = 156.08 + N(0, 18.8²) MWh, N1_off = 30,750 + N(0, 52.3²) line-h, N4 = f_N4 + N(0, 10.9²) on an independent monitor stream.
- R (`waves/n0_E/landing_R.json`): V1 3,977,491 MWh, E1 $8,163.73M. B_V1 18,739 MWh, B_E1 $1.862M.

## 2. Single-objective BO (prompt 66 §2)

Settings: botorch `qLogNoisyExpectedImprovement`, `SobolQMCNormalSampler(128, seed s)`, `prune_baseline`, `cache_root`, `optimize_acqf` over [0, 1]^6, q 8, 20 restarts × 512 raw samples, sequential. s = 20261007 + 100 seed_id + k. GP = 55's `qnehvi_E.ObjGP` (float64, house fit) with the committed kernel and transform, floor 1e-9, refitted each round. Proposals get the same bound cleanup as 55 (`snap_bounds`). Random baseline = 8 i.i.d. uniform u per round from `default_rng(s)`, same s, same noise stream. Regret = f(best-observed design) − f*, in B_j.

**r0 plug-in.** The start-set GP (house fit, round 0) already puts its posterior-mean optimum at regret 0.086 B (V1) and 0.006 B (E1). Criteria 4 and 5 therefore validate optimize_acqf and bound handling, not search: the GP that BO starts from already knows where the optimum is.

| obj | fit | method | seed | r0 plug-in | r0 | r1 | r2 | r3 | r4 | posterior-mean optimum r4 | cov95 r1–r4 | rms z r1–r4 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| E1 | house | bo | 0 | 0.006 | 12.803 | 0.004 | 0.004 | 0.004 | 0.004 | 0.011 | 8/8/8/8 | 0.11/0.33/0.26/0.30 |
| E1 | house | bo | 1 | 0.006 | 12.803 | 0.016 | 0.016 | 0.000 | 0.000 | 0.016 | 8/8/8/8 | 0.11/0.24/0.22/0.30 |
| E1 | house | bo | 2 | 0.006 | 12.803 | 0.016 | 0.151 | 0.030 | 0.030 | 0.013 | 8/8/8/8 | 0.09/0.17/0.32/0.25 |
| E1 | house | random | 0 | 0.006 | 12.803 | 12.660 | 12.660 | 12.660 | 12.660 | - | - | - |
| E1 | house | random | 1 | 0.006 | 12.803 | 12.803 | 12.803 | 11.906 | 11.906 | - | - | - |
| E1 | house | random | 2 | 0.006 | 12.803 | 12.803 | 12.803 | 12.309 | 12.309 | - | - | - |
| E1 | long (expl.) | bo | 0 | 0.016 | 12.803 | 0.016 | 0.016 | 0.016 | 0.016 | 0.016 | 0/8/8/8 | 2.30/0.62/0.38/1.01 |
| E1 | long (expl.) | bo | 1 | 0.016 | 12.803 | 0.016 | 0.016 | 0.016 | 0.016 | 0.016 | 1/8/8/7 | 2.21/0.87/0.38/1.00 |
| E1 | long (expl.) | bo | 2 | 0.016 | 12.803 | 0.016 | 0.016 | 0.016 | 0.028 | 0.009 | 2/8/7/8 | 2.26/0.78/0.96/0.94 |
| V1 | house | bo | 0 | 0.086 | 19.582 | 0.086 | 0.081 | 0.081 | 0.081 | 0.027 | 8/8/8/8 | 0.13/0.16/0.16/0.12 |
| V1 | house | bo | 1 | 0.086 | 19.582 | 0.086 | 0.086 | 0.360 | 0.360 | 0.014 | 8/8/8/8 | 0.13/0.15/0.20/0.07 |
| V1 | house | bo | 2 | 0.086 | 19.582 | 0.086 | 0.086 | 0.086 | 0.086 | 0.026 | 8/8/8/8 | 0.14/0.19/0.20/0.16 |
| V1 | house | random | 0 | 0.086 | 19.582 | 19.582 | 19.582 | 20.045 | 20.045 | - | - | - |
| V1 | house | random | 1 | 0.086 | 19.582 | 19.582 | 19.582 | 19.582 | 18.196 | - | - | - |
| V1 | house | random | 2 | 0.086 | 19.582 | 17.820 | 17.820 | 17.820 | 17.820 | - | - | - |
| V1 | long (expl.) | bo | 0 | 0.882 | 19.582 | 0.327 | 0.008 | 0.008 | 0.063 | 0.016 | 5/8/7/6 | 1.88/1.05/1.50/1.73 |
| V1 | long (expl.) | bo | 1 | 0.882 | 19.582 | 0.311 | 0.029 | 0.087 | 0.087 | 0.027 | 5/8/8/8 | 1.87/0.72/0.92/0.63 |
| V1 | long (expl.) | bo | 2 | 0.882 | 19.582 | 0.417 | 0.011 | 0.007 | 0.007 | 0.006 | 6/7/8/7 | 1.84/1.37/1.15/0.95 |

The best observed can get worse when a noisy low observation at a slightly worse design replaces the best. The posterior-mean optimum stays at 0.01–0.03 B.

![single](figs/fig_EMU_single_regret.png)

## 3. Multi-objective, 55 machinery (prompt 66 §3)

`acquire_E.Lane` + `cmd_init` + `propose_round` + `ingest_gate` (C1) + `grade_round`, with the section-7 changes. Root = `analysis/emulator_E/`: waves `waves/methods_E_EMU_<fit>_<scen>_s<seed>_r<k>/` (55 wave writer output + `objectives_EMULATOR.csv`); ledgers `lanes/<fit>/<scen>/s<seed>/`. Config = `arms_E.json` with absolute paths, `part = "EMULATOR"`, `n0_tier_provisional = 48`. Loader = the real 54 loader for n0_E (keys, U, meta, identity gate) with Y replaced by the emulated start values, plus the emulated wave tables. qNEHVI block as pinned, acq seed 20261006 + 100 seed_id + k, cap 4. Seed lane 0 ran first (s0), then seeds 1–4.

- tau_exact: `ercot_noise_exact_cov.csv` is identically 0 for V1 and E1, so tau_joint = tau_marginal = 0 and `budget_cap_only = true`. The ledger records gain/tau = null and would_stop = false in every round.
- tau_res (REPORT-ONLY, `tau_E.tau_res`, Sigma_c[V1, E1], 1,000 draws, `default_rng(20261006)`): 4.398e+11 (HV units, MWh × $).
- **Best-known front** (the reference): non-dominated set (true f) of Sobol 2^14 + 64 vertices + 98 scalarizations + every design evaluated by any lane, single run, random pool or matched-budget baseline; a LOWER bound on the true front. HV = 1.4489e+14 = 1.0176 × the polished front (Sobol + vertices + scalarizations); polished ∪ the lane designs alone = 1.0160 × polished. Sobol reference = 0.893 of best-known; not a front.
- prompt-34 p (one 48-pool, 8k-subsets, ties ½, seed 20261012, interval from 1,000 × 2,000 pool resamples) is kept as specified in `emulator_E_multi.csv` (`p_random_prompt34_saturated`): saturated; see effect size.

### 3.1 Lanes

| scen | fit | seed | graded | true-f HV / best-known, r0–r4 | effect vs vertices p95, r4 | gain / tau_res, r1–r4 | C2/C3 | wall s per round |
|---|---|---|---|---|---|---|---|---|
| s0 | house | 0 | 4 | 0.694/0.921/0.961/0.971/0.979 | +0.070 | 75.4/12.4/3.6/2.4 | 0/0 | 7.6/7.6/8.5/10.5 |
| s0 | house | 1 | 4 | 0.694/0.925/0.960/0.970/0.975 | +0.065 | 77.0/11.2/3.2/1.6 | 0/0 | 7.9/7.2/7.7/8.3 |
| s0 | house | 2 | 4 | 0.694/0.921/0.960/0.971/0.979 | +0.070 | 75.3/12.2/3.5/3.0 | 0/0 | 7.1/7.6/8.2/9.0 |
| s0 | house | 3 | 4 | 0.694/0.925/0.964/0.969/0.979 | +0.070 | 77.2/12.5/1.6/3.6 | 0/0 | 6.4/6.5/6.8/7.6 |
| s0 | house | 4 | 4 | 0.694/0.927/0.964/0.971/0.976 | +0.067 | 77.6/11.6/2.3/1.5 | 0/0 | 6.1/6.3/6.6/7.4 |
| s0 | long (expl.) | 0 | 4 | 0.694/0.907/0.953/0.967/0.973 | +0.063 | 70.6/15.5/4.7/2.5 | 0/0 | 38.5/36.3/35.4/39.1 |
| s1 | house | 0 | 4 | 0.694/0.905/0.958/0.970/0.976 | +0.067 | 69.1/17.5/4.5/2.5 | 0/0 | 7.5/11.3/13.3/12.5 |
| s1 | house | 1 | 4 | 0.694/0.913/0.954/0.971/0.977 | +0.067 | 73.2/13.7/5.3/1.8 | 0/0 | 7.1/10.5/10.4/11.8 |
| s1 | house | 2 | 4 | 0.694/0.904/0.960/0.968/0.976 | +0.067 | 70.7/17.6/3.0/2.7 | 0/0 | 7.3/11.8/9.9/9.9 |
| s1 | house | 3 | 4 | 0.694/0.912/0.957/0.964/0.974 | +0.064 | 71.0/14.9/2.7/3.4 | 0/0 | 5.9/8.7/9.2/9.4 |
| s1 | house | 4 | 4 | 0.694/0.916/0.955/0.965/0.974 | +0.065 | 74.1/12.5/3.8/3.1 | 0/0 | 5.3/8.6/8.9/9.1 |
| s2 | house | 0 | 1 (HALT) | 0.694/0.869 | - | 58.7 | 0/0 | 7.5 |
| s2 | house | 1 | 1 (HALT) | 0.694/0.875 | - | 60.4 | 0/0 | 7.3 |
| s2 | house | 2 | 1 (HALT) | 0.694/0.872 | - | 58.4 | 0/0 | 7.5 |
| s2 | house | 3 | 1 (HALT) | 0.694/0.872 | - | 58.9 | 0/0 | 8.8 |
| s2 | house | 4 | 1 (HALT) | 0.694/0.874 | - | 60.8 | 0/0 | 7.6 |

### 3.2 Matched-budget baselines (true-f HV / best-known front; same 48 starts; 8 per round × 4)

Rule: matched budget: same 48 starts (true f), 8 designs per round x 4, true-f HV / best-known HV per round; uniform = i.i.d. u; vertices = 32 of the 64 box vertices without replacement; plugin_random = 32 random designs of the r0 plug-in front; plugin_spread = 32 designs at quantiles of the plug-in front (1 replicate, no exploration); 1000 replicates, default_rng(20261166).

| baseline | reps | r1 p5/p50/p95 | r2 p50 | r3 p50 | r4 p5/p50/p95 | r4 max |
|---|---|---|---|---|---|---|
| i.i.d. uniform | 1000 | 0.694/0.699/0.718 | 0.705 | 0.711 | 0.701/0.716/0.740 | 0.770 |
| random box vertices | 1000 | 0.725/0.770/0.824 | 0.819 | 0.851 | 0.838/0.875/0.910 | 0.921 |
| r0 plug-in front, random 32 | 1000 | 0.782/0.833/0.883 | 0.894 | 0.930 | 0.915/0.948/0.958 | 0.964 |
| r0 plug-in front, spread (no exploration) | 1 | 0.866/0.866/0.866 | 0.931 | 0.944 | 0.955/0.955/0.955 | 0.955 |
| qNEHVI s0 (5 lanes) | 5 | 0.921–0.927 | 0.960–0.964 | 0.969–0.971 | 0.975–0.979 | 0.979 |

Effect size at r4 (s0, house fit): BO − vertices p95 = +0.065–+0.070; BO − plug-in random p95 = +0.017–+0.021; BO − plug-in spread = +0.020–+0.024.
BO ends above the plug-in exploit in every lane, but by little; the emulator separates acquisition from a plug-in exploit only weakly.

![multi](figs/fig_EMU_multi_hv.png)

### 3.3 Seed overlap (input to E-D4)

| round | designs (5 lanes) | unique | exact vertices |
|---|---|---|---|
| r1 | 40 | 23 | 55% |
| r2 | 40 | 36 | 18% |
| r3 | 40 | 31 | 40% |
| r4 | 40 | 35 | 28% |

Pairwise Jaccard of the 32-design lane sets: 0.19–0.21. Final true-f HV spread across the 5 lanes: 0.975–0.979. Minimum distance (u, Euclidean) of a proposal to the lane's already-evaluated set: 0.0527; proposals within 1e-6: 0; within 0.05: 0 (re-proposal risk, F6). **Under option C, 17 of the 40 r1 PCM runs would duplicate another lane's design (exact match to 1e-10 in u). Shared replicates vs run all is a decision for Kay.**

- s1: r1 is unconstrained (the violation is not yet known). From r2 the round record says `constraint: shed <= 1.0 MWh (GP on the accumulated R1 column)`. The violating run stays in GP training and is out of HV.
- s2: grade r1 writes `HALT_FOR_DECISION.md`; the next `propose_round` raises the REFUSED SystemExit.
- Wall time per round (house fit, s0): 7.6 s mean (propose + emulate + C1 + grade); qNEHVI fit + optimize 6.5 s mean at 2 threads.
- botorch emits ~199 warnings per propose (restart retries, numerics); counts are in `emulator_E_multi.csv`. None stopped a round.

![front](figs/fig_EMU_front.png)

## 4. Calibration and lengthscales

### 4.1 Counts

C2 (covered ≤ 4 of 8) and C3 (≥ 3 of 8 with |z| > 3), computed exactly as 55 (`acquire_E._calibration`; `emulator_E.calib` is tested equal). House fit: 0 C2, 0 C3 in 24 single-objective rounds; 0 C2, 0 C3 in 90 multi-objective (round, objective) cells. Expected under the nominal rates: 0.042 (C2), 1.3e-04 (C3).

### 4.2 Start-set hull split

A design is inside the hull when it is a convex combination of the 48 start designs (LP feasibility in u).

**Every proposed design in every batch (146 (batch, objective) rows, both fits) lies outside the start set's convex hull.** The inside/outside split is therefore degenerate: all calibration here is extrapolation. The 48 Sobol starts fill the interior; BO goes to faces and vertices.

| kind | fit | round | (batch, objective) rows | mean fraction outside hull | exact vertices / batch | cov95 inside (pooled) | cov95 outside (pooled) | rms z inside | rms z outside | C2 batches |
|---|---|---|---|---|---|---|---|---|---|---|
| multi | house | r1 | 30 | 1.00 | 4.4 | 0/0 | 240/240 | - | 0.14 | 0 |
| multi | house | r2 | 20 | 1.00 | 1.0 | 0/0 | 160/160 | - | 0.24 | 0 |
| multi | house | r3 | 20 | 1.00 | 3.5 | 0/0 | 160/160 | - | 0.23 | 0 |
| multi | house | r4 | 20 | 1.00 | 1.6 | 0/0 | 160/160 | - | 0.31 | 0 |
| multi | long (expl.) | r1 | 2 | 1.00 | 4.0 | 0/0 | 13/16 | - | 1.92 | 0 |
| multi | long (expl.) | r2 | 2 | 1.00 | 2.0 | 0/0 | 16/16 | - | 0.99 | 0 |
| multi | long (expl.) | r3 | 2 | 1.00 | 2.0 | 0/0 | 15/16 | - | 1.16 | 0 |
| multi | long (expl.) | r4 | 2 | 1.00 | 2.0 | 0/0 | 15/16 | - | 1.09 | 0 |
| single | house | r1 | 6 | 1.00 | 2.8 | 0/0 | 48/48 | - | 0.12 | 0 |
| single | house | r2 | 6 | 1.00 | 0.8 | 0/0 | 48/48 | - | 0.21 | 0 |
| single | house | r3 | 6 | 1.00 | 0.3 | 0/0 | 48/48 | - | 0.23 | 0 |
| single | house | r4 | 6 | 1.00 | 0.0 | 0/0 | 48/48 | - | 0.20 | 0 |
| single | long (expl.) | r1 | 6 | 1.00 | 3.7 | 0/0 | 19/48 | - | 2.06 | 3 |
| single | long (expl.) | r2 | 6 | 1.00 | 2.0 | 0/0 | 47/48 | - | 0.90 | 0 |
| single | long (expl.) | r3 | 6 | 1.00 | 0.3 | 0/0 | 46/48 | - | 0.88 | 0 |
| single | long (expl.) | r4 | 6 | 1.00 | 0.7 | 0/0 | 44/48 | - | 1.04 | 0 |

### 4.3 Lengthscale drift (house fit)

Max relative change of the BO GP's ARD lengthscales (u) from r0 to r4: 0.05–0.10. Distance from the emulator's lengthscales: ≤ 0.11. The refit is stable.

### 4.4 Power caveat

The house-fit BO GP infers noise sd 19,742 MWh (V1) and $0.93M (E1) on average, 6× and 2.3× the emulated chatter. Its 95 % bands are too wide, rms z is 0.07–0.59, and C2/C3 cannot fire on an under-covering model. The zero flag count is weak evidence. (54's ERCOT_GP_STATUS reports 3.97× / 2.65× against the df-16 σ_c; this file uses the LW-shrunk Σ_c sd 3,275 MWh / $0.398M.)

![calibration](figs/fig_EMU_calibration.png)

## 5. EXPLORATORY — long fit (exploratory, 10,000 steps) of the BO's internal GP (nothing committed)

Same emulator truth (the committed house-fit f). Only the BO's own GP fit changes: `qnehvi_E.train_gp` → `bogp.train_gp(n_epochs=10000)`. This is NOT fit v2 (no priors, single start).

| item | house fit (700 steps) | long fit (exploratory, 10,000 steps) |
|---|---|---|
| single V1 regret r4, seeds 0/1/2 (B) | 0.081 / 0.360 / 0.086 | 0.063 / 0.087 / 0.007 |
| single E1 regret r4, seeds 0/1/2 (B) | 0.004 / 0.000 / 0.030 | 0.016 / 0.016 / 0.028 |
| inferred noise sd V1 / E1 | mean 19.7k MWh / $0.93M | mean 3.2k MWh / $0.30M; range 2.3k–4.3k MWh / $18k–$527k; r0 (start set) 2.7k MWh / $18k (E1 0.05× chatter) |
| rms z of new batches (single and multi) | 0.07–0.59 | 0.38–2.68 |
| C2 flags (single, 24 rounds) | 0 | 3 (E1 r1 cov95 0, 1, 2 of 8) |
| C3 flags (single) | 0 | 0 |
| lengthscale distance to the emulator (max over sites) | ≤ 0.11 | 0.86–2.12 (86%–212%) |
| multi s0 seed 0: true-f HV / best-known r4 | 0.979 | 0.973 |
| multi s0 seed 0: C2/C3 | 0/0 | 0/0 |
| wall s per round, mean over r1–r4 (single / multi) | 2.7 / 7.6 | 14.7 / 37.3 |

Reading: the optimizer-limited house fit does not hurt the BO's search on this emulator. Both fits reach the same regret and front fraction. The long fit is better calibrated after round 1. In round 1 it under-covers the E1 vertex batch (cov95 0, 1, 2 of 8), so C2 fires. Two causes act together. First, all 8 designs are outside the start set's hull. Second, the r0 long fit sets the E1 noise at $18k, 0.05× the chatter. The long fit's noise is unstable (54 Part B saw the same multimodal likelihood). Fit v2 must show a stable noise estimate before C2 means anything. This emulator's truth is itself a house-fit posterior mean; a converged-fit truth could change the comparison.

## 6. Every parameter, environment and file

- Branch `ercot/66-emulator-bo`, worktree `RTS-GMLC-e66`, based on `ercot/tx123`. Environment bogp-botorch (botorch 0.16.1, torch 2.12.0, gpytorch 1.15.2). bo-gp-qparego 60e6328 (= `bogp_sha_expected`).
- Plan AMENDMENT 2026-11-24b (ERCOT_BO_PLAN.md, 93c81a4) replaces the house fit with fit definition v2 (MAP, L-BFGS-B, 16 restarts) for every fit from that block on. This run uses the committed configs as they stand (house fit) for both the emulator truth and the BO GP. Mode-gap columns (`mode_gap_v2`) are empty and wait for the v2 rerun.
- n* = 48 (54, provisional; E-D7 null). q 8, cap 4, rounds 4.
- Seeds: emulator 6666; single acq 20261007 + 100 seed_id + k (seed_ids 0–2); multi acq 20261006 + 100 seed_id + k (seed_ids 0–4); tau 20261006; prompt-34 subsets 20261012; pool `default_rng([6666, 4, 1])`; Sobol front 6614; plug-in front Sobol 6615; matched-budget baselines `default_rng(20261166)`, 1000 replicates.
- MC 128 Sobol QMC, 20 restarts, 512 raw, sequential greedy, float64. Bound cleanup `snap_bounds` (tol 1e-12).
- Scenarios: s1 injects R1 = 2.5 MWh on r1 run 3; s2 injects R1 = 1.5 and 40.0 MWh on r1 runs 2 and 6.
- Files: `emulator_E_params.json` (emulator, hyperparameters, start set); `emulator_E_single.csv`, `emulator_E_multi.csv`, `emulator_E_calib_hull.csv`, `emulator_E_summary.json` (pass/fail); `runs_compact/` (single and multi run records with every design u, `EMU_front.json`, `EMU_random_pool.json`, `EMU_extras.json`: plug-in, best-known front, baselines, seed overlap); `lanes/`, `waves/`, `figs/`. `runs/` is gitignored (trial_0826/ercot/**/runs/) and holds only logs and the prompt-34 subset-HV npz; the report and figures read only committed files, so a clean checkout reproduces them (assert-before-draw recomputes every plotted value).
- Code: `emulator_E.py`, `emulator_E_report.py`, `test_emulator_E.py` (toy 2-D function).

Reproduce (bogp-botorch, from `trial_0826/ercot`):

    PY=/opt/anaconda3/envs/bogp-botorch/bin/python
    $PY analysis/emulator_E/emulator_E.py fit-emulator && $PY analysis/emulator_E/emulator_E.py front && $PY analysis/emulator_E/emulator_E.py random-pool
    for o in V1 E1; do for s in 0 1 2; do for m in bo random; do $PY analysis/emulator_E/emulator_E.py single --obj $o --seed $s --method $m; done; $PY analysis/emulator_E/emulator_E.py single --obj $o --seed $s --variant long; done; done
    for sc in s0 s1 s2; do $PY analysis/emulator_E/emulator_E.py multi --scenario $sc --seeds 0,1,2,3,4; done
    $PY analysis/emulator_E/emulator_E.py multi --scenario s0 --seeds 0 --variant long && $PY analysis/emulator_E/emulator_E.py extras
    $PY analysis/emulator_E/emulator_E_report.py collect && $PY analysis/emulator_E/emulator_E_report.py figs && $PY analysis/emulator_E/emulator_E_report.py report

## 7. Changes to 55 code and config (as 55's proxy) and deviations

1. `bc3168c` `arms_E.json`: dated design space; objectives [V1, E1]; R2 base 156.08 / flag 312.16 MWh; N1_off monitor. `_scratch_E.py` writes the design space at the configured path; three M = 4 test asserts read the config.
2. `c7576a6` `acquire_E.py` / `common_E.py`: (a) `Lane(loader=...)` takes an injected loader; (b) `n0_tier` uses `n0_tier_provisional` ONLY while `E-D7_decided` is null; (c) **the r1 cross-seed assert checks "sets differ" (prompt 55 §2.1 text) instead of "pairwise disjoint" and records the shared count. Kay: accept or reject.**
3. `c470d7b` hardening: (a) a second r1 cross-seed assert — at least one design per seed pair differs by > 1e-6 in u; (b) the provisional-n* fallback REFUSES when `part == "B"`; (c) a comment at the re-proposal assert (rule unchanged; a 55 Part B decision).
4. `b2b2142` **zero-site fix (HIGH).** `qnehvi_E.propose` mapped x·sx + mx back to u and clipped, so a lower-bound optimum came back as 5.55e-17. The wave writer then wrote a `<site>_PEM` unit with PEM_fraction ~5e-17, a different model instance from "site absent" (contract §5). The first emulated waves had 57 of 2,352 u cells in (0, 1e-9); `ingest_gate` did not see them. Now `snap_bounds` sets u < 1e-12 to 0 and u > 1 − 1e-12 to 1 (`settings.bound_snaps`; bound cleanup, not lattice snapping), predictions use the snapped design, and `wave_writer_E.design_rows` refuses u in (0, 1e-9). Two tests added. I regenerated every wave and result after the fix.
   Rerun check: Not bit-identical, but no conclusion moves. Every r1 proposal is identical to the pre-fix run once the pre-fix 5.55e-17 values are read as 0 (16/16 lane r1 batches, all single-objective r1 batches). From r2 on, the training inputs differ by ~5e-17, and the Adam fit + multi-start optimizer then take a different path in some lanes (multi: 7/11 r2, 7/11 r3, 3/11 r4 batches identical; some designs move to another vertex). Aggregates: max change in single-objective regret 0.012 B; in observed HV 0.3% and in true-f HV 0.3% relative; cov95 unchanged in every single-objective round. The fix snapped 56 u cells to 0 and 7 to 1 across the regenerated multi lanes. This path sensitivity is itself a finding: lane trajectories are not reproducible across a 1e-16 input change, only their aggregates are.
5. `0066a64` `HALT_FOR_DECISION.md` printed a literal `HALT_r{k}_DECIDED.md`; fixed (f-string).
6. `3d57f8c` `arms_E.json` carries the R3 and N3 monitors from the design space as config text only.
7. `dry_round_E.py` still asserts DISJOINT r1 sets on stub data. This is inconsistent with change 2c; left for 55 Part B.
8. Interpretation: start-set observations are emulated (f + eps), not the real n0_E Y (section 1).
9. The headline HV fraction uses the best-known front (true f); the spec's Sobol 2^14 figure is reported as a reference.
10. The exploratory long fit repeat covers all 3 single-objective seeds; multi is s0 seed 0 only, as asked.
11. The audience review named three STE-100 sentence rewrites that were not in the message I received; I applied the given texts and the one-name-per-fit rule.

## 8. What remains before a real launch (pre-launch checklist, 55 Part B)

1. Zero-site fix landed (change 4) — keep the test; add a real-loader ingest test on a fake methods_E wave copied from one n0_E run.
2. Duplicate-proposal path: replace the re-proposal assert with a declared rule (re-optimize the duplicate slot or allow a replicate); make grade_round idempotent; commit before propose.
3. Fit v2 in `qnehvi_E` per `committed_configs.json` `fit_definition` (MAP, L-BFGS-B, 16 restarts); add a per-round convergence flag.
4. New `committed_configs.json` under fit v2 (54 re-open round), then rerun this dry run.
5. E-D7 decided in `committed_configs.json`; the Part B guard (change 3b) then never sees the provisional tier.
6. E-D5 amendment appended; README wording switched.
7. `arms_E.json` complete: `gp.train` = fit v2, `part = "B"`; R3 / N3 / N1_off wired into grading (today config text only).
8. τ_res written into the ledger (today report-only, computed here outside the machinery).
9. Stale text: README / runbook M = 4 and "pairwise distinct" wording; the HALT placeholder (fixed, change 5).
10. `dry_round_E.py` aligned with change 2c; tests for the c7576a6 branches (injected loader, provisional tier, Part B refusal).
11. Real-loader ingest test on a fake `__ALL__` methods_E wave copied from one n0_E run.
12. Kay's decision on cross-lane duplicate runs (≈ 17 of 40 r1 runs under option C): shared replicates vs run all.
13. CRC: `acquire_E_job.sh --check-env`, `GAP_DECISION.json` present, `submit_ready_E.sh --dry-run`, then one lane first.

**Code paths NOT exercised here:** `submit_state_E.py`, `acquire_E_job.sh`, the array and collector scripts, the ercot-bot commit / push, a real `__ALL__` wave ingest through `pool_objectives`, SUSPECT, a true R2 flag, resume after HALT (rename + rerun), and the Part B asserts.

**Runtime note.** qNEHVI took 3.8–11.1 s per propose at 2 threads here. Expect 10–30 s plus the fit v2 restarts on CRC; that is < 1 % of a round (8 PCM runs × 5–11 h).
