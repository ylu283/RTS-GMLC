# ercot_overnight.pptx — slide text, source line and speaker notes

## Slide 1

**Source line:** Source: committed_configs.json (n_star), design_space_E_2026-11-24.json (M); git rev-parse ercot/tx123

ERCOT TX-123BT · OVERNIGHT RESULTS (prompts 65 → 54 → 66) · 1-ON-1 · 2026-11-26

ERCOT BO overnight: two objectives, GPs that pass the holdout, machinery that runs end to end — four decisions before the first real round

rule v2 (M = 2) · n* = 48 · mixed GP fit · emulator dry run · 2026-11-24
Kay Lu · branch ercot/tx123 @ de45242


**Notes:** Source: committed_configs.json (n_star), design_space_E_2026-11-24.json (M); git rev-parse ercot/tx123. Say: Last night the pipeline ran three steps: the objective rule (65), the GP fits (54) and an emulator test of the BO machinery (66). Today: what it proved, what it did not, and four decisions.

## Slide 2

**Source line:** Source: admin/prompt/bogp/ercot-station-map.md (stations 3, 4, 6); admin PROGRESS 11-24

Is the ERCOT BO ready for its first real round, and what must be decided first?


65

rule v2

objectives V1 · E1

DONE

→

54

GP fit + holdout

n* = 48; V1 house, E1 v2

DONE

→

66

emulator BO

55 machinery, no PCM

DONE

→

55 B

Part B

13 open items (backup B3)

OPEN

→

56

launch

Kay submits round 1

OPEN

The four decisions for today (slide 12)

•  E-D1b: the objectives. Accept M = 2 (V1 · E1) under rule v2, or revert to the v1 vector.
•  E-D7 + the fit item: start at n = 48 with the mixed GP fit (V1 house, E1 fit v2).
•  E-D4 (part): duplicate PCM runs across the seed lanes. Reuse by design key, or run all.
•  55 Part B rules: the duplicate-slot rule, the meaning of a C2 flag on a replicate, the r1 assert change, claims filters.

**Notes:** Source: admin/prompt/bogp/ercot-station-map.md (stations 3, 4, 6); admin PROGRESS 11-24. Station rows: ercot-station-map.md §2 (3. Model validation, 4. BO loop, 6. Baseline + launch). States: admin PROGRESS 11-24 entries (65 executed, 54 B done, 66 done; 'Overnight pipeline COMPLETE').

## Slide 3

**Source line:** Source: admin PROGRESS 11-24 (verdicts); pool_ed1b_v2.csv (eta2_T, resid_IDR_over_B); EMULATOR_BO.md §A

Ready after four decisions: seat V1 · E1, start at n = 48 with a mixed GP fit, set the duplicate-run and replicate rules; the emulator tests machinery, not search


ACCEPT WITH NOTES ×2

Objectives: rule v2 seats V1 · E1 (M = 2).

ACCEPT WITH NOTES · PI/QA FIX THEN SHIP (applied)

GPs pass the random_E holdout at n = 48: V1 house fit 45/48, E1 fit v2 48/48.

ACCEPT WITH NOTES ×2 · FIX THEN SHIP; rerun ACCEPT WITH NOTES

The 55 machinery runs end to end on the committed GPs. It found one bug. We fixed it.

DONE

RTS 49 V1 arm: DONE at cap 4 (backup B2).

SCIENTIFIC RISK

V1 is 98 % total PEM MW (η²T 0.978). Location enters the front through E1 (η²T 0.64, composition residual IDR 10 B). Both ends of the emulator front are box vertices outside the start data. Round 1 tests them.

Verdict chips: acceptance review, 2026-11-24 (independent reviewers per step).

**Notes:** Source: admin PROGRESS 11-24 (verdicts); pool_ed1b_v2.csv (eta2_T, resid_IDR_over_B); EMULATOR_BO.md §A. (i) 65: stats + power systems ACCEPT WITH NOTES. (ii) 54 B: GP stats ACCEPT WITH NOTES, PI/QA FIX THEN SHIP (fixes applied 9a357ea/eb8c2da); 54 v2 round GP stats ACCEPT WITH NOTES. (iii) 66: BO stats + machinery ACCEPT WITH NOTES, audience FIX THEN SHIP; committed rerun ACCEPT WITH NOTES. (iv) RTS 49 V1 DONE d6 8ed4c01. Holdout: ercot_gp_status.csv / _v2.csv holdout rows. Risk: pool_ed1b_v2.csv eta2_T V1/E1, resid_IDR_over_B E1; EMULATOR_BO.md §A.0 item 1.

## Slide 4

**Source line:** Source: arms_E.json, design_space_E_2026-11-24.json, landing_R.json · plan amendment 11-24 (sha256 e3712a7f…) inst. 4–6, 11-24b §1

The BO problem these decisions fix, and rule v2 in three lines


The BO problem

→ E-D1b (objectives)

→ E-D7 (n₀ and the fit)

→ E-D4 (lanes) · 55 B (proposal rule)

Rule v2 (objective seats), three lines

In words: a measure takes a seat only if it is a physical outcome, it moves clearly above the noise bar, and no earlier seat already carries it. Bj formula and the full table: Appendix B.

**Notes:** Source: arms_E.json, design_space_E_2026-11-24.json, landing_R.json · plan amendment 11-24 (sha256 e3712a7f…) inst. 4–6, 11-24b §1. Equations in math font: figs/eq_bo_1..5.png, figs/eq_rule_1..4.png (make_overnight_figs.py, pre_can mathtext recipe). u ∈ [0,1]^6: design_space_E_2026-11-24.json sites; n0 = 48: tiers.grading; q, cap, 5 seed lanes, qNEHVI: arms_E.json; R: landing_R.json R (V1 3,977,491.39 MWh, E1 $8,163.73M); τ_exact = 0: plan AMENDMENT 2026-11-24b §1; C2/C3 REVIEW only: arms_E.json calibration.action; rule lines: plan AMENDMENT 2026-11-24 instantiations 4 and 6 (block sha256 e3712a7f…). ε: Σ_c = prompt-63 solver-seed chatter (EMULATOR_BO.md §1).

## Slide 5

**Source line:** Source: POOL_N0E_STANDINGS_v2.md §7–§8, pool_ed1b_v2.csv, pool_pairs_v2.csv; GP_STATUS §6a · plan amendment 11-24

Rule v2 seats V1 and E1; N4 clears its own bar 14× but fails the composition gate (residual Mantel p 0.025 vs 0.01), so it is co-reported, not seated


| Family | v1 walk | v1 Seed re-grade | v2 (this read) | Reason (v2) |
| V | V1 | V1 | V1 | OUTCOME, RESOLVED, ADEQUATE |
| E | E1 | E1 | E1 | OUTCOME, RESOLVED, ADEQUATE |
| X | — | — | — | X1 REDUNDANT given E1 (raw ρ 0.982 / residual ρ 0.968) |
| R | — | — | — | no OUTCOME candidate; R4 is a PROXY of E2 (start-up cost) |
| N | N1 | N1 | — | N4: IDR/B 14.24, residual Mantel p 0.0253 > 0.01 → raw ρ with V1 0.966 → REDUNDANT; N1 is a PROXY |

•  Disclosure (once): rule v2 was written after the v1 read (post hoc, disclosed). We expected it to seat V1 · E1 · N4. It returned V1 · E1. We committed what it returned, without tuning (§8.14 departure, disclosed). Rule v2 is pre-committed unchanged for the next dataset.
•  Physics: the six slate sites share one PTDF on L252. N4's composition signal is the cost of diverted deliverable wind, and E1 already prices it (acceptance review, 2026-11-24).
•  Pushback: the 0.01 threshold was fixed before the read. N4 is still fitted and graded (holdout 48/48) and co-reported in every result. The next dataset is the real test of rule v2.
•  What N4 would need to be seated: Appendix B (counterfactual).

**Notes:** Source: POOL_N0E_STANDINGS_v2.md §7–§8, pool_ed1b_v2.csv, pool_pairs_v2.csv; GP_STATUS §6a · plan amendment 11-24. Vectors: POOL_N0E_STANDINGS_v2.md §8 (v1 d706199, Seed re-grade baf77c3, v2). N4 / N1 / R4 roles, IDR_over_B, mantel_p_resid: pool_ed1b_v2.csv. ρ values: pool_pairs_v2.csv (X1|E1, N4|V1). Physics: ERCOT_GP_STATUS.md §6a (same PTDF) + power-systems acceptance review (admin PROGRESS 11-24 ~03:30). §8.14 and Kay's override: governance note in POOL_N0E_STANDINGS_v2.md. N4 holdout 48/48: ercot_gp_status.csv.

## Slide 6

**Source line:** Source: ERCOT_GP_STATUS.md §0, §13.2; ercot_gp_status(_v2).csv; committed_configs.json; exposure_ledger.csv

The house GPs pass the holdout at n = 48 (V1 45/48, E1 48/48) and no smaller tier meets the n* rule, but the capped optimizer over-states the noise 2.7–4×


Holdout parity, house fit, n = 32 (top) and 48 (bottom); red = outside the 95 % band.

•  LOO RMSE at n = 48: V1 30.6k MWh (1.63 Bj); E1 $3.30M (1.77 Bj).
•  Co-reported: N4 48/48; N1 41/48 FAIL (recorded, not re-selected).
•  Inferred noise / σc: V1 3.97, E1 2.65. Adam stops at 700 steps.
•  LOO RMSE ratio n = 44 / 48: V1 1.120, E1 1.116 (> 1.1). No tier below 48 qualifies.
•  Under the converged fit, LOO RMSE still falls 1.255–1.285× from 44 to 48 (same arm; 1.46 is the cross-arm figure). The first BO rounds are model-learning rounds.
•  n* = 48 means that no smaller tier suffices. We did not test whether 48 suffices. The early front is not a claim.

**Notes:** Source: ERCOT_GP_STATUS.md §0, §13.2; ercot_gp_status(_v2).csv; committed_configs.json; exposure_ledger.csv. Holdout: ercot_gp_status.csv holdout rows (exposure rows 2, 4, 6, 8 of exposure_ledger.csv). LOO RMSE: committed_configs_housefit.json loo_rmse / pool_ed1b_v2.csv B_j. Noise: ercot_gp_status.csv noise_over_sigma_c (selected arm, n = 48). Ratios at 44: committed_configs.json n_star_reason. Like-for-like v2 ratios: ercot_gp_status_v2.csv loo_rmse (rbf+std 14,904/11,880; m52+std 17,372/13,520; cross-arm 17,372/11,880) = ERCOT_GP_STATUS.md §13.2. Figure: analysis/ercot_gp/figs/fig_parity_holdout.png (81ea382), copied.

## Slide 7

**Source line:** Source: ERCOT_GP_STATUS.md §0, §13, §13.1b; ercot_gp_status_v2.csv; committed_configs(_housefit).json; exposure_ledger.csv

Fit v2 commits E1 (48/48); V1's v2 fit is 2.3× more accurate but over-confident (37/48, P = 2e-5), so V1 keeps the house fit by the pre-registered fallback


Fit v2 holdout parity + residual row (V1 left, E1 right).

| fit v2 at n = 48 | V1 (rbf+std) | E1 (m52+std) |
| lengthscales in u | 4.66 / 5.85 / 5.63 / 5.60 / 2.41 / 1.86 | 2.75 / 3.59 / 4.31 / 4.33 / 2.09 / 1.41 |
| noise / σc | 0.98 | 0.61 |
| converged restarts · mode gap | 14/16 · 119 nats | 12/16 · 52.9 nats |
| LOO NLPD v2 / house | 10.795 / 11.733 | 15.805 / 16.252 |
| holdout cov95 · rms z | 37/48 FAIL · 1.64 | 48/48 PASS · 0.74 |
| holdout NLPD · RMSE, v2 vs house | 11.31 · 16,101 vs 11.73 · 37,361 MWh | 15.39 · $1.17M vs 15.84 · $1.76M |
| committed definition | house (fallback) | v2 (AMENDMENT 11-24b) |

•  Why V1 v2 fails: (a) not chance, P(≤ 37 | 48) = 2e-05. (b) Smooth-kernel misfit: rbf lengthscales 1.9–5.9 in u; prompt-61 residuals 5 of 9 |z| > 1.96, P2_500_270 +5.64. The data ask for more noise (V1 rbf 1.15 σc at n = 44, 0.98 at 48); the prior sets most other fits at its mode 0.61 σc.
•  (c) LOO on a Sobol prefix is optimistic for an i.i.d. holdout: holdout error 1.36× LOO (16,101 vs 11,880 MWh) with narrower bands (sd 8,315 vs 12,106).
•  Provenance (once): we designed fit v2 after we saw the house holdout (8 scorings; the diagnostic was coded 7 min later). It is a second look, not a blind test. Exposure 10 of 24.
•  Pushback: we launch with one GP too wide (V1; gates blind) and one too narrow at replicates (E1). Report-only, pre-registered for 55: log V1's v2 posteriors beside the house fit every round, and gate power per objective. The fallback was pre-registered; re-selection after scoring was not allowed.
•  Paper lesson: V1 needs structure (linear mean, additive or site-interaction kernel), not wider bars (acceptance review, 2026-11-24).

**Notes:** Source: ERCOT_GP_STATUS.md §0, §13, §13.1b; ercot_gp_status_v2.csv; committed_configs(_housefit).json; exposure_ledger.csv. Table: committed_configs.json (V1 v2_result; E1 hyperparameters, mode_gap_nats, loo_nlpd_mean), committed_configs_housefit.json (house LOO NLPD), ercot_gp_status_v2.csv (n_within_tol; holdout rows: cov95, rms z, NLPD, RMSE), ercot_gp_status.csv (house holdout NLPD/RMSE). P = binom.cdf(37, 48, 0.95). Residuals: ercot_gp_lc_residuals_v2.csv. Noise 1.15 at 44: ercot_gp_status_v2.csv. Band sd 8,315 / 12,106 and provenance: ERCOT_GP_STATUS.md §13.1b / §0. Paper lesson: GP-stats acceptance review (admin PROGRESS 11-24 ~09:00). Figure: analysis/ercot_gp/figs/fig_parity_holdout_v2.png (81ea382), copied.

## Slide 8

**Source line:** Source: EMULATOR_BO.md §A.1, §7, §8; emulator_E_summary_committed.json; emulator_E_multi_committed.csv

The 55 machinery runs end to end on the committed GPs (12/12 single, 15/15 multi lanes, C1 45/45) and caught a bug that wrote a PEM unit at fraction 5.6e-17


| check (committed block) | result |  |
| runs finish; each lane ends where its scenario says | single 12/12, multi 15/15 | PASS |
| C1 ingest on every emulated round | 45/45 | PASS |
| branches: s0 to the cap; s1 constrained from r2; s2 HALT | s1 n_hv 55/63/71/79; s2 propose refused | PASS |
| fit v2 (E1) converged at every round fit | multi 45/45, single 15/15 (60/60) | PASS |
| τexact = 0 → cap only; R2 / N1_off monitors | cap only; monitors quiet | PASS |

Three changes to 55 (disclosed)

•  b2b2142 zero-site fix (HIGH): a lower-bound optimum came back as 5.55e-17, so the writer built a <site>_PEM unit. snap_bounds sets it to 0; the writer refuses u in (0, 1e-9).
•  c7576a6 + c470d7b: the r1 cross-seed assert checks "sets differ" (prompt 55 §2.1), hardened by a second assert.
•  0066a64: the HALT file printed a literal name; fixed.

NOT exercised here
•  submit_state_E.py
•  acquire_E_job.sh
•  CRC array and collector scripts
•  ercot-bot commit / push
•  a real __ALL__ wave ingest
•  SUSPECT runs
•  resume after HALT
These run first on CRC, one lane first (backup B3).

**Notes:** Source: EMULATOR_BO.md §A.1, §7, §8; emulator_E_summary_committed.json; emulator_E_multi_committed.csv. Pass/fail: emulator_E_summary_committed.json pass_fail 1, 2, 6, 7, 8; n_hv per round: emulator_E_multi_committed.csv (s1). Changes: EMULATOR_BO.md §7 items 2–5. NOT exercised: §8 'Code paths NOT exercised here' (a true R2 flag and the Part B asserts also not exercised). Title value 5.6e-17 = the reviewer's rounding of 5.55e-17 (admin PROGRESS 11-24 ~07:00).

## Slide 9

**Source line:** Source: emulator_E_{multi,single}_committed.csv, summary_committed, EMU_extras_committed.json; EMULATOR_BO.md §A.2–A.5

On the emulator BO matches a plug-in of the start-set GP (HV 0.971–0.980 vs 0.966); against a mismatched V1 truth it still finds the all-PEM vertex (1 seed)


True-f HV / best-known front, committed truth; bands = matched-budget baselines.

•  Baselines at r4 (1,000 reps): uniform p5/p50/p95 0.667/0.683/0.712; random vertices p95 0.918; r0 plug-in spread 0.966.
•  Circularity (once): the truth is the GP's own posterior mean through the same 48 points. So the r0 GP already knows the optimum (plug-in regret V1 0.086 B, E1 ≈ 0).
•  Mismatch B (V1 truth = v2 fit): plug-in error 1.31 B. The best evaluated design's true f is 0.002 B by r2. The posterior-mean incumbent is 0.050 B at r4; the best observation is 0.293 B.
•  Winner's curse: the best observation carries −0.76 / −1.40 sd of noise (r3 / r4). Report incumbents by posterior mean.
•  f*(E1) at the no-PEM vertex is a smooth-trend claim (0.34 lengthscales from the data), not data.

**Notes:** Source: emulator_E_{multi,single}_committed.csv, summary_committed, EMU_extras_committed.json; EMULATOR_BO.md §A.2–A.5. HV: emulator_E_multi_committed.csv hv_true_frac_best, s0, round 4 (5 lanes). Baselines and plug-in: EMU_extras_committed.json baselines[*][4], r0_plugin.committed. Mismatch B: emulator_E_single_committed.csv variant mmB (r0_plugin_regret_B, regret_pm_opt_B, regret_best_obs_B); 0.002 B, −0.76 / −1.40 and 0.34 lengthscales: EMULATOR_BO.md §A.5 / §A.0. Figure: analysis/emulator_E/figs/fig_EMU_multi_hv_committed.png (de45242), copied.

## Slide 10

**Source line:** Source: EMULATOR_BO.md §A.0, §A.3; emulator_E_single_committed.csv; emulator_E_summary_committed.json

The calibration gates cannot see a V1 misfit (house bands ≈ 6× too wide); the one E1 flag came at a replicated design, where fit v2 under-estimates the noise (0.31–0.99× actual)


cov95 of each round's 8 new points; C2 fires at ≤ 4 (red line).

•  V1: rms z median 0.17; C2 0, C3 0. The house bands are ≈ 6× too wide.
•  The E1 C2 + C3 event: 8 identical designs at u = 0 (observed twice in r1). Fit noise 0.676 σc vs emulator 1.274 σc, ρ 0.53 → coverage 0.70. P(C2) per such batch 0.10 (executor) / 0.22 (reviewer).
•  Multi path: 0/45. Single-objective E1 replicates u = 0 in 71 of 72 r2–r4 designs.
•  C2 and C3 are REVIEW flags. They never halt.

What tells us a GP is wrong in round 1?
Today: the report-only V1 v2 posterior log and E1's REVIEW flags.
Proposed trigger (for 55 B): a REVIEW flag on a non-replicated batch, or |posterior mean − PCM| > 2 Bj on any design, opens a model review before round 2.

**Notes:** Source: EMULATOR_BO.md §A.0, §A.3; emulator_E_single_committed.csv; emulator_E_summary_committed.json. V1: summary_committed per_objective_gates.V1. Event: emulator_E_single_committed.csv E1 bo seed 0 (r1 n_at_origin 2; r2 cov95 3, C2, C3; r1 noise_over_sigma_c 0.676, noise_over_chatter 0.531); emulator noise = 0.676 / 0.531 = 1.274 σ_c; coverage 2Φ(1.96ρ) − 1. P(C2) 0.10 / 0.22: EMULATOR_BO.md §A.0 item 3. Multi C2: emulator_E_multi_committed.csv (45 graded rows). 71/72: n_at_origin r2–r4. Noise range: noise_over_chatter (single E1) ∪ E1_noise_over_emulator (multi). The proposed trigger is a proposal for 55 Part B, not a rule. Figure: analysis/emulator_E/figs/fig_EMU_calibration_committed.png (de45242), copied.

## Slide 11

**Source line:** Source: runs_compact/EMU_extras_committed.json (seed_overlap); EMULATOR_BO.md §A.4; pi-agenda E-D4 · plan amendment 11-14

Seed lanes converge on box vertices: 16 of 40 round-1 PCM runs would repeat another lane's design — reuse by design key, or run all and disclose


| committed block, 5 lanes | r1 | r2 | r3 | r4 |
| unique designs of 40 | 24 | 38 | 35 | 38 |

•  Lane-set Jaccard 0.10–0.16. Closest re-proposal of an evaluated design: 0.067 in u (none within 1e-6).
•  Cost of running all: 16 runs × 21–45 core-h ≈ 340–720 core-h (wave-D actuals 21–44.6 core-h per run).
•  The PCM is deterministic (τexact = 0). A repeat run returns the same y, so reuse changes no posterior.
•  The five lanes are correlated either way. They cannot support a seed-dispersion claim.
•  Reuse needs one 55 B item: the HV ledger must count a shared design once.

**Notes:** Source: runs_compact/EMU_extras_committed.json (seed_overlap); EMULATOR_BO.md §A.4; pi-agenda E-D4 · plan amendment 11-14. unique per round, jaccard_range, min_dist, r1_duplicate_runs_of_40: EMU_extras_committed.json seed_overlap. Core-h: plan AMENDMENT 2026-11-14 (21 fast – 44.6 slow per run) and pi-agenda E-D4 row (≈ 340–720 at 21–45). The house block's overlap (first run) is on backup B4 only.

## Slide 12

**Source line:** Source: pi-agenda 11-24 rows; pi_agenda_E-D7_draft.md; EMULATOR_BO.md §A.7, §8; PROGRESS Prompt 66

Four decisions unlock round 1; the first two need no new runs, the third avoids up to ≈ 720 core-h


E-D1b · objectives
Options: (a) accept M = 2 (V1 · E1) under rule v2; ratify the §8.14 departure and the one holdout re-open (24b §4). (b) reject the amendment → v1 vector V1 · E1 · N1 (N1 PROXY, raw ρ with V1 0.95, residual IDR/B 0.94); M = 3 re-derives R, τ and the gate numbers. Cost: no new runs.

Recommend: accept M = 2.
Changes it: a PI view that location must be its own objective. Even then N4 cannot be seated: no further rule override is allowed this campaign.

E-D7 + fit item · n₀ and the GP fit
Options: n₀ = 48 / 32 / 44 (44 only under a 1.12 bar). Cost: no new runs. Rejected: a second re-open (forbidden), V1 m52 v2 (re-selection after scoring), both house (discards E1's gain).

Recommend: 48 with the mixed commit (V1 house, E1 v2), as the pre-registered fallback produced it.
Changes it: nothing without new data.

E-D4 (part) · duplicate runs
Options: run all (16 extra r1 runs, ≈ 340–720 core-h), or reuse by design key (HV ledger de-dup, built in 55 B).

Recommend: reuse by design key, disclosed (deterministic PCM).
Changes it: a decision to claim seed dispersion (then run all, and the claim is still weak).

55 Part B rules · one bundle
Approve or flag line by line: (1) duplicate slot → re-optimize the slot without the evaluated designs (default), or a disclosed replicate; (2) a C2 REVIEW on a replicated design = review, no halt; (3) accept the r1 cross-seed assert change (c7576a6 + c470d7b); (4) claims filters for N3 / N1_off (b)(c), as for R1.

Recommend: approve all four.
Changes it: a flag on any line; that line then waits, the others proceed.

Round 1 = 8 PCM runs × 5–11 h wall per lane; acquisition < 1 % of a round. Open 55 B items that block round 1: backup B3.
Next dataset: V1 structure in the GP; a continuous congestion metric; the fit definition pre-registered.

**Notes:** Source: pi-agenda 11-24 rows; pi_agenda_E-D7_draft.md; EMULATOR_BO.md §A.7, §8; PROGRESS Prompt 66. E-D1b: pi-agenda E-D1b UPDATE 11-24; N1 values pool_pairs_v2.csv / pool_ed1b_v2.csv; one override per campaign: plan AMENDMENT 2026-11-24 §2.5. E-D7: pi-agenda E-D7 row + pi_agenda_E-D7_draft.md (alternatives ii–iv). E-D4: pi-agenda E-D4 (part) row (strategy recommends reuse, disclosed). 55 B bundle: pi-agenda E-D4 row + ERCOT PROGRESS Prompt 66 'Decisions for Kay' + admin PROGRESS 11-24 ~03:30 (claims filters). Round wall: EMULATOR_BO.md §8 runtime note. The 4th-row 'Changes it' line is the deck's procedure (each line approved separately), not a file number.

## Slide 13

**Source line:** 

BACKUP

Backup slides B1–B5 and Appendices A–D

B1 training-size study under fit v2 · B2 RTS 49 V1 arm · B3 the 55 Part B checklist · B4 house-fit emulator block · B5 figures not shown · A process log · B rule-v2 standings · C matched-budget baselines · D fit definitions

## Slide 14

**Source line:** Source: ercot_gp_nstar_checks_v2.csv, ercot_gp_status_v2.csv, ERCOT_GP_STATUS.md §13

Training-size study under fit v2: LOO RMSE, NLPD, coverage and inferred noise still move from 44 to 48


The inferred-noise plateau at 0.61 σc is the prior's MAP mode (e^(−½)·σc). V1 rbf leaves it at 44–48 (1.15, 0.98 σc).

**Notes:** Source: ercot_gp_nstar_checks_v2.csv, ercot_gp_status_v2.csv, ERCOT_GP_STATUS.md §13. Figure: analysis/ercot_gp/figs/fig_training_size_curves_v2.png (81ea382), copied.

## Slide 15

**Source line:** Source: RTS-GMLC campaign/analysis/methods_C/V1/ledger.json (d6 8ed4c01)

RTS 49 V1 arm (cap 4, 64 designs): the old-floor τ stops at rounds 3–4, the measured rulers never do, and the gains are not monotone (r4 > r3)


| round | HV | gain | gain / τold | gain / τ285 | gain / τhet |
| r1 | 7.359e+17 | 7.53e+16 | 1.43 | 11.6 | 24.9 |
| r2 | 7.664e+17 | 3.04e+16 | 0.578 | 4.68 | 10.1 |
| r3 | 7.802e+17 | 1.38e+16 | 0.262 (would stop) | 2.12 | 4.56 |
| r4 | 7.962e+17 | 1.61e+16 | 0.305 (would stop) | 2.47 | 5.32 |

•  r4 LOO rms z: shed 0.82, curtailment 0.76, cost 0.56.
•  The old-floor ruler would stop at r3 and r4. The measured rulers (τ285, τhet) never stop.
•  The r4 gain is larger than the r3 gain. Gains are not monotone.

**Notes:** Source: RTS-GMLC campaign/analysis/methods_C/V1/ledger.json (d6 8ed4c01). entries[1..4]: hv, gain, gain_tau (τ_old), gain_tau_285, gain_tau_het, would_stop*, loo_rms_z; read with git show d6:… (no checkout).

## Slide 16

**Source line:** Source: EMULATOR_BO.md §8, §A.6–A.7; committed_configs.json

What blocks round 1: the 55 Part B checklist (13 items; blocking ones marked)


DONE

1. Zero-site fix (b2b2142); add a real-loader ingest test.

BLOCKS

2. Duplicate-proposal rule; idempotent grade_round; commit before propose.

DONE

3. Fit v2 in qnehvi_E per fit_definition (36b74b7 hook); convergence flag recorded.

DONE

4. New committed_configs.json (240bde1); dry run rerun on it.

BLOCKS

5. E-D7 decided in committed_configs.json (Part B guard: DONE).

BLOCKS

6. E-D5 amendment appended; README wording.

BLOCKS

7. arms_E.json complete: gp.train = fit v2, part = B; R3 / N3 / N1_off wired.

BLOCKS

8. τres written into the ledger.

open

9. Stale README / runbook text (M = 4, 'pairwise distinct').

BLOCKS

10. dry_round_E.py aligned with the r1 change; tests for the c7576a6 branches.

BLOCKS

11. Real-loader ingest test on a fake __ALL__ methods_E wave.

BLOCKS

12. Kay's duplicate-run decision (slide 11).

BLOCKS

13. CRC: --check-env, GAP_DECISION.json, --dry-run; then one lane first.

**Notes:** Source: EMULATOR_BO.md §8, §A.6–A.7; committed_configs.json. Items verbatim in substance from EMULATOR_BO.md §8; DONE marks from §A.6 / §A.7 (hook 36b74b7, configs 240bde1, Part B guard 4aad620). 'BLOCKS' = must be done before round 1 is submitted (prompt 67 B3 marking); item 9 is text only.

## Slide 17

**Source line:** Source: emulator_E_summary.json, runs_compact/EMU_extras.json, EMU_rerun_check.json (house); EMULATOR_BO.md §B

House-fit emulator block: the same machinery on the unconverged GPs — superseded items marked


•  s0 r4 HV fraction of the best-known front: 0.975–0.979 (committed block: 0.971–0.980).
•  r0 plug-in regret V1 / E1: 0.086 / 0.006 B. SUPERSEDED for E1 (committed block: E1 ≈ 0).
•  Seed overlap, unique designs of 40 per round r1–r4: 23 / 36 / 31 / 35; 17 duplicate r1 runs. SUPERSEDED by the committed block (slide 11).
•  C2 / C3: 0 in 114 cells. This is no power, not a pass: the house bands are too wide. SUPERSEDED (slide 10).
•  Path sensitivity (still valid): a 1e-16 input change (5.55e-17 → 0) re-routes lanes from r2. Aggregates move ≤ 0.3 % in HV. Lane trajectories do not reproduce; aggregates do.

**Notes:** Source: emulator_E_summary.json, runs_compact/EMU_extras.json, EMU_rerun_check.json (house); EMULATOR_BO.md §B. House block = first run, kept as run (EMULATOR_BO.md §B). s0_r4_frac_best, pass_fail[3]: emulator_E_summary.json; r0_plugin.house, seed_overlap: EMU_extras.json; max_true_hv_rel_change: EMU_rerun_check.json.

## Slide 18

**Source line:** Source: analysis/ercot_gp/figs/, analysis/emulator_E/figs/ (paths below)

Figures not shown


•  ercot_gp/figs/fig_lengthscales_vs_n_v2.png
–  The 55 % lengthscale change at n = 48 is an arm switch (m52+std → rbf+std), not instability.
•  ercot_gp/figs/fig_house_vs_longfit.png
–  The diagnostic that triggered AMENDMENT 2026-11-24b (house fit vs 10,000-step fit).
•  emulator_E/figs/fig_EMU_front_committed.png
–  Both front ends lie outside the R box; V1 below the lowest observed value (1.409 TWh) is extrapolation.
•  emulator_E/figs/fig_EMU_single_regret_committed.png
–  Single-objective regret; the E1 replicate collapse at u = 0 is marked.

**Notes:** Source: analysis/ercot_gp/figs/, analysis/emulator_E/figs/ (paths below). Lines: ERCOT_GP_STATUS.md §13.2 (arm switch); plan AMENDMENT 2026-11-24b (diagnostic); EMULATOR_BO.md §1 caution + 'Limits of this test' (front ends, 1.409 TWh); §A.3 (replicate collapse).

## Slide 19

**Source line:** Source: git log --format=%ai on ercot/tx123 and d6; verdicts: admin PROGRESS 11-24 (acceptance reviews)

Appendix A: process log — step · SHA · time (git log --format=%ai) · verdict


| step | what | SHA | time (git) | review |
| 65 | plan AMENDMENT 2026-11-24 (rule v2) committed alone | 212d60d | 2026-11-24 00:50:42 -0500 |  |
| 65 | pool_n0E_v2.py + tests | b8a3285 | 2026-11-24 01:24:50 -0500 |  |
| 65 | real read: V1 · E1 (M = 2) | ae6d80a | 2026-11-24 01:31:28 -0500 |  |
| 65 | dated design space | 1f00a2d | 2026-11-24 01:32:12 -0500 |  |
| 65 | erratum (disclosure wording) | aa98045 | 2026-11-24 01:41:12 -0500 | 65: ACCEPT WITH NOTES ×2 |
| 54 B | code: training-size study, long-fit diagnostic | dc316ef | 2026-11-24 01:48:22 -0500 |  |
| 54 B | outputs: n* = 48, holdout 8/24 | b23021c | 2026-11-24 02:19:30 -0500 | 54 B: ACCEPT W. NOTES · FIX THEN SHIP |
| plan | AMENDMENT 2026-11-24b (M = 2, fit v2, one re-open) | 93c81a4 | 2026-11-24 02:31:19 -0500 |  |
| 66 | arms_E.json as 55's proxy | bc3168c | 2026-11-24 02:34:53 -0500 |  |
| 66 | 55 minimal changes (r1 assert 'sets differ') | c7576a6 | 2026-11-24 02:46:46 -0500 |  |
| 66 | house-fit outputs | 76c1ae6 | 2026-11-24 02:52:11 -0500 | 66: ACCEPT W. NOTES ×2 · FIX THEN SHIP |
| 66 | zero-site fix (snap_bounds + writer assert) | b2b2142 | 2026-11-24 03:01:54 -0500 |  |
| 54 v2 | reporting fixes | eb8c2da | 2026-11-24 02:48:44 -0500 |  |
| 54 v2 | fit v2 round: V1 37/48 → house fallback; E1 48/48 → v2 | 7bde505 | 2026-11-24 03:14:16 -0500 |  |
| 54 v2 | status page §0 / §13 | 240bde1 | 2026-11-24 03:22:40 -0500 | 54 v2: ACCEPT WITH NOTES |
| 66 v2 | 55 hook: per-objective fit definition | 36b74b7 | 2026-11-24 03:31:23 -0500 |  |
| 66 v2 | committed-fit outputs | 7457043 | 2026-11-24 03:45:57 -0500 | 66 v2: ACCEPT WITH NOTES |
| 54 | report-only fixes (GP-stats notes) | 81ea382 | 2026-11-24 03:58:05 -0500 |  |
| 66 | acceptance fixes, section A | de45242 | 2026-11-24 03:59:00 -0500 |  |
| RTS 49 | V1 arm r4 graded — DONE (hard cap) | 8ed4c01 | 2026-11-24 01:16:14 -0500 |  |

**Notes:** Source: git log --format=%ai on ercot/tx123 and d6; verdicts: admin PROGRESS 11-24 (acceptance reviews). Times are commit times from git, not the clock times in PROGRESS. All SHAs asserted as ancestors of ercot/tx123 (RTS: d6).

## Slide 20

**Source line:** Source: analysis/pool/pool_ed1b_v2.csv · plan amendment 11-24

Appendix B (1/3): full rule-v2 standings, walk order (28 rows)


| id | role | Bj | IDR/B [lo90] | resid IDR/B | η²T | Mantel p raw / resid | status |
| V1 | OUTCOME | 1.87e+04 | 80.50 [58.78] | 8.83 | 0.978 | 0.0001 / 0.0016 | SEATED (rule v2) |
| E1 | OUTCOME | 1.86e+06 | 17.99 [13.32] | 10.11 | 0.641 | 0.0003 / 0.0002 | SEATED (rule v2) |
| X1 | OUTCOME | 4.03e+04 | 24.77 [16.99] | 11.29 | 0.741 | 0.0004 / 0.0002 | SUPPRESSED (REDUNDANT given E1 |
| R4 | PROXY(E2 start-up cost) | 250 | 1.24 [0.82] | 0.80 | 0.514 | 0.0009 / 0.0290 | PROXY |
| N1 | PROXY | 217 | 3.41 [2.34] | 0.94 | 0.891 | 0.0001 / 0.0042 | PROXY (REDUNDANT given V1, E6, |
| E4 | TRANSFER | 9.68e+06 | 9.19 [6.52] | 2.88 | 0.873 | 0.0001 / 0.0050 | TRANSFER (REDUNDANT given V2,  |
| R2 | GUARD | 112 | 0.68 [0.46] | 0.66 | 0.067 | 0.1728 / 0.5489 | GUARDRAIL |
| R7 | DIAGNOSTIC | 2.83e+05 | 4.18 [2.76] | 2.27 | 0.689 | 0.0001 / 0.0020 | DIAGNOSTIC |
| N4 | OUTCOME | 45.1 | 14.24 [10.01] | 4.34 | 0.925 | 0.0001 / 0.0253 | SUPPRESSED (REDUNDANT given V1 |
| N5 | DIAGNOSTIC | 0.2 | 15.66 [11.30] | 4.30 | 0.926 | 0.0001 / 0.0019 | DIAGNOSTIC (REDUNDANT given V2 |
| E6 | TRANSFER | 2e+06 | 21.18 [14.94] | 4.70 | 0.697 | 0.0001 / 0.0133 | TRANSFER (REDUNDANT given V1) |
| R5 | DIAGNOSTIC | 1.37e+04 | 1.08 [0.76] | 0.91 | -0.715 | 0.1093 / 0.2172 | DIAGNOSTIC |
| N3 | GUARD | 11.3 | 0.81 [0.55] | 0.83 | -1.720 | 0.1118 / 0.0513 | GUARDRAIL |
| E2 | COMPONENT(E1) | 3.53e+06 | 2.70 [1.88] | 1.77 | 0.557 | 0.0006 / 0.0013 | COMPONENT (REDUNDANT given V2, |

**Notes:** Source: analysis/pool/pool_ed1b_v2.csv · plan amendment 11-24. Columns: B_j, IDR_over_B, IDR_over_B_lo90, resid_IDR_over_B, eta2_T, mantel_p_raw, mantel_p_resid, status (role / status strings truncated to fit; full strings in the csv).

## Slide 21

**Source line:** Source: analysis/pool/pool_ed1b_v2.csv · plan amendment 11-24

Appendix B (2/3): full rule-v2 standings, walk order (28 rows)


| id | role | Bj | IDR/B [lo90] | resid IDR/B | η²T | Mantel p raw / resid | status |
| R6 | DIAGNOSTIC | 9.74e+04 | 0.86 [0.63] | 1.09 | -2.974 | 0.6759 / 0.0109 | DIAGNOSTIC |
| N2 | DIAGNOSTIC | 3.66 | 0.35 [0.23] | 0.45 | -0.040 | 0.5561 / 0.4135 | DIAGNOSTIC |
| E3 | COMPONENT(E1) | 3.42e+06 | 7.10 [4.98] | 4.01 | 0.674 | 0.0004 / 0.0002 | COMPONENT (REDUNDANT given V2, |
| R8 | DIAGNOSTIC | 1.5e+03 | 1.20 [0.80] | 0.85 | 0.523 | 0.0032 / 0.0661 | DIAGNOSTIC |
| E7 | PROXY(E4) | 0.0144 | 16.21 [11.73] | 5.11 | 0.891 | 0.0001 / 0.0094 | PROXY |
| E8 | DIAGNOSTIC | 0.295 | 1.04 [0.69] | 0.77 | 0.355 | 0.0267 / 0.4307 | DIAGNOSTIC |
| E9 | DIAGNOSTIC (dead) | 1.14 | 0.00 [0.00] | 0.00 | 0.000 | 0.8332 / 0.8332 | DIAGNOSTIC |
| V2 | PROXY(E1) | 0.00709 | 48.60 [34.09] | 23.14 | 0.714 | 0.0002 / 0.0002 | PROXY |
| V3 | DIAGNOSTIC | 0.000165 | 12.63 [9.29] | 10.16 | 0.416 | 0.0003 / 0.0002 | DIAGNOSTIC |
| E5 | OUTCOME (dead) | 0 | — | — | — | — | DEAD / constant / not computed |
| R1 | GUARD | 0 | — | — | — | — | GUARDRAIL |
| R3 | GUARD | 0 | — | — | — | — | GUARDRAIL |
| D1 | DIAGNOSTIC (investor out | 1.44e+04 | 196.80 [137.08] | 48.38 | 0.899 | 0.0001 / 0.0016 | DIAGNOSTIC |
| D2 | DIAGNOSTIC | 0.00164 | 81.33 [54.46] | 39.77 | 0.696 | 0.0001 / 0.0172 | DIAGNOSTIC |

**Notes:** Source: analysis/pool/pool_ed1b_v2.csv · plan amendment 11-24. Columns: B_j, IDR_over_B, IDR_over_B_lo90, resid_IDR_over_B, eta2_T, mantel_p_raw, mantel_p_resid, status (role / status strings truncated to fit; full strings in the csv).

## Slide 22

**Source line:** Source: plan AMENDMENT 2026-11-24 inst. 1, 5, 6; pool_ed1b_v2.csv; pool_pairs_v2.csv; pool_n0E_v2.steiger · plan amendment 11-24

Appendix B (3/3): the bar Bj, the materiality floors, and the N4 counterfactual


•  Bar
•  Bj = max(3√2·s_j, max|δ|);  s_j² = (6 s²_pert + 16 s²_seed)/22,  ν = 22 (D1, D2: ν 20).
•  Materiality floors (set after the relative responses were seen; disclosed)
•  V1 58,287 MWh · E1 $8.06M · X1 194,521 t · N4 87.6 h.
•  N4 counterfactual (not a result; the rule allows no second override)
•  If N4 had passed the composition gate (residual Mantel p ≤ 0.01; it read 0.0253), the N4–V1 pair would be a BORDERLINE-PAIR: residual ρ 0.421, 90 % interval [0.176, 0.617] contains 0.50.
•  §4b via the seated E1: residual ρ(N4, E1) -0.805, upper-90 -0.687 ≤ −0.50; Steiger Z -5.74 (one-sided p 4.8e-09, n_eff 42; recomputed at build) → NOT REDUNDANT → N4 seated → M = 3.
•  Reviewer items (acceptance review, 2026-11-24): the residual Mantel p reads 0.023–0.027 across permutation seeds; with that clause passed, §4b would seat N4.

**Notes:** Source: plan AMENDMENT 2026-11-24 inst. 1, 5, 6; pool_ed1b_v2.csv; pool_pairs_v2.csv; pool_n0E_v2.steiger · plan amendment 11-24. Steiger: pool_n0E_v2.steiger(ρ_res(N4,E1), ρ_res(E1,V1), ρ_res(N4,V1)) on pool_pairs_v2.csv rho_resid (logged in ASSERTIONS.md). Floors: pool_ed1b_v2.csv floor_M. Bin sensitivity is not printed (no file).

## Slide 23

**Source line:** Source: EMU_extras_{committed,mmA,mmB}.json (baselines, r4); emulator_E_multi_committed.csv (s0 seed 0, r4)

Appendix C: emulator matched-budget baselines at r4 under three truths (committed / mismatch A / mismatch B)


| truth (V1 / E1) | random vertices p95 | r0 plug-in spread | BO s0 seed 0 |
| committed (house / v2) | 0.918 | 0.966 | 0.971 |
| mismatch A (house / house) | 0.910 | 0.967 | 0.977 |
| mismatch B (v2 / v2) | 0.940 | 0.975 | 0.988 |

•  Each truth is scored against the best-known front of its own truth.
•  BO ends above the plug-in spread under every truth, by a small margin. One seed per mismatch.

**Notes:** Source: EMU_extras_{committed,mmA,mmB}.json (baselines, r4); emulator_E_multi_committed.csv (s0 seed 0, r4). baselines.vertices.p95[4], baselines.plugin_spread.p50[4]; BO = hv_true_frac_best, variant committed / mmA / mmB, s0, seed 0, round 4.

## Slide 24

**Source line:** Source: committed_configs.json (fit_v2_spec); EMULATOR_BO.md §1; arms_E.json gp.train

Appendix D: the two GP fit definitions in use


•  Fit v2 (E1; AMENDMENT 2026-11-24b) — fit_v2_spec, verbatim
•  float64; MAP; lengthscale prior LogNormal(sqrt(2) + 0.5 log d, sqrt(3)) on u in [0,1]^d (no input standardization); noise prior LogNormal(log(sigma_c^2 / s_y^2), 1) on the standardized noise variance; standardized noise lower bound 1e-6 (measured-floor arm: max(1e-6, (sigma_c / s_y)^2)); L-BFGS-B via botorch fit_gpytorch_mll_scipy (maxiter 1000, ftol = gtol = 1e-7); 16 restarts (gpytorch default init + 15 prior draws, numpy default_rng(5454)); best MAP kept; converged iff >= 2 restarts within 1e-3 n nats of the best
•  House fit (V1, fallback)
•  bogp.train_gp: Adam, 700 steps, lr 0.01, float32, torch.manual_seed(0); refit each round.

**Notes:** Source: committed_configs.json (fit_v2_spec); EMULATOR_BO.md §1; arms_E.json gp.train. fit_v2_spec printed verbatim from committed_configs.json.

