# bo_1013.pptx — slide text and speaker notes

## Slide 1


PI MEETING · 2026-10-13

BO campaign + ERCOT v2: status and decisions, 2026-10-13

Stage-2 q-ParEGO on RTS-GMLC (scenario C), the methods arms now running, and the first ERCOT results on corrected data.

Three asks today
1.  Sign off the N1 gate amendment and the primary HV reference (slides 15–16).
2.  Approve the redesigned ERCOT wave D (slide 22).
3.  Decide: scenarios A/B before submission, or a scenario-C-only claim (slide 25).

**Notes:** Deck rebuilt 10-13 from bo_1012 after two expert reviews (methods review 10-13; power-systems review 10-13). Built by make_bo_1013_deck.py from OUTLINE_1013.md (content source of truth).

## Slide 2

What each claim needs, and where it stands


BO campaign + ERCOT v2 · 2026-10-13

| Claim | Evidence (experiment) | Status 10-13 | What would weaken it |
| W  Workflow: pre-registered, auditable MOBO on a real PCM stops on its rule | Stage-2 run (done) | supported; "unattended" only up to qsub | — |
| S  The stop rule has a known operating characteristic | 37 (truth-known problems); 35 P1 r3–r4 (real data) | running | S0 acts as "stop after 2 rounds" |
| ii  Results are stable across replicates (start set + seed) | 35 S2, S3 vs P1 | running | P2/P3 below 0.8 percentile, or recipe at base rate |
| iii  Found designs follow the sensitivity structure (recipe) | Stage-2 + random baseline; 35 P2/P3 out-of-sample | in-sample only | recipe fails on P2/P3 |
| A  The workflow does not depend on the acquisition | 35 N1 (qNEHVI, 1 seed); 37 | running | N1 clearly better than q-ParEGO |
| B  BO places above random; BO reaches the extremes | random baseline (done) | above at both refs, not robust; extremes clear | — |
| T  The workflow transfers to another grid | ERCOT (36: screening + OAT only, no BO) | no experiment | — |
| i  Convergence within budget | — | retired (not shown) | — |

Bottom line: Sobol continuations Q1–Q3 serve no claim (descriptive). Prompt 38 (mechanism) gates the shed axis for S, B and iii.

**Notes:** Claims W, S, ii, iii, A, B, T, i: methods review 10-13; P35 §5; P37. Sources: /Users/yilu/Documents/development/nd/research/admin/prompt/bogp/35-stage2-methods-arms.md; /Users/yilu/Documents/development/nd/research/admin/prompt/bogp/37-stop-rule-validation.md; /Users/yilu/Documents/development/nd/research/admin/prompt/bogp/math-log.md

## Slide 3

Three prompts run on CRC; prompt 38 is ready


BO campaign + ERCOT v2 · 2026-10-13

| Work | Question | CRC work | State 10-13 | Results |
| Replicates + acquisition (35) | Is q-ParEGO stable across replicates at a fixed budget of 64? Is one qNEHVI run consistent with it? | 7 arms: start sets S2, S3; Sobol continuations Q1–Q3; P1 rounds 3–4; qNEHVI N1 | running since 10-12 21:00; this is the last allowed relaunch | first round ≈ 10-13; all ≈ 10-17 → 10-19 |
| ERCOT on corrected data (36) | Re-run ERCOT for AIChE | A base ×3, B screening 19, C selection 9 | A + B landed; base read done; C nuclear rows 6–11 rerun after a T0 fix | C ≈ 10-14; wave D after redesign |
| Stop-rule validation (37) | Does the stop rule work on problems with a known truth? | 1,540 tasks, 0 PCM runs | running since 10-12 evening | ≈ 10-13 → 10-15 |
| Mechanism checks (38) | Why does shed fall as withheld MW rises? Why do 7 designs share 22.426 MWh? | 0 PCM runs (rsync of finished runs) | ready to hand off | ≈ 2 days after hand-off |

CRC order: ERCOT first. Submission stays manual from the login node.

**Notes:** Sources: admin PROGRESS.md rows 1–10; LR 10-12u, 10-12v, 10-13a, 10-13b. 35 relaunch 8308211; 37 CRC gate f5e4c14. Prompt 38 written 10-13.
Sources: /Users/yilu/Documents/development/nd/research/admin/prompt/bogp/PROGRESS.md; /Users/yilu/Documents/development/nd/research/admin/prompt/bogp/living-report-multipem.md; /Users/yilu/Documents/development/nd/research/admin/prompt/bogp/38-rts-mechanism-checks.md

## Slide 4

Reproducibility card: the campaign configuration (frozen)


BO campaign + ERCOT v2 · 2026-10-13

| Item | Setting |
| Design space | 6 tiers (nuclear, pv, tail, wind_122, wind_303, wind_317) × 9 lattice levels ω ∈ {0.05 … 1.0} = 531,441 designs |
| Scenario | C: ρ = 2.0, B = $40/MWh |
| Objectives (min) | load_shed_mwh, true_curtailment_mwh, total_cost_less_synthetic_usd |
| Starts | 32 Sobol points (shared by every comparison) |
| GP training data | the 32 starts only (10 backfill rows: report-only sensitivity) |
| Acquisition | q-ParEGO, q = 8: 8 Dirichlet weights, EI, kriging believer, discrete lattice candidates |
| HV reference (fixed before round 1) | nadir of the 32 starts + 10 % span; HV₀ = 6.606e17 |
| Stop rule | 2 consecutive rounds with gain < τ = 5.263e16 (8.0 % of HV₀; set by the shed materiality floor, conservative) |
| Software | bo-gp feat/qparego @ 60e6328; RTS runs are bit-reproducible |

**Notes:** Notes: B header; prompt 30.
Sources: /Users/yilu/Documents/GitHub/RTS-GMLC/trial_0826/campaign/analysis/bo_stage2/BO_STAGE2.md; /Users/yilu/Documents/development/nd/research/admin/prompt/bogp/30-stage2-bo-campaign.md

## Slide 5

The "PEM" is a $40 bid on renewable output, not an electrolyzer load


BO campaign + ERCOT v2 · 2026-10-13

What the model does

•  Renewable site: the unit splits. The parent keeps availability minus the PEM capacity. A _PEM unit gets the rest and offers it at B = $40/MWh. Withheld MWh count as hydrogen (20 kg/MWh).
•  Nuclear site: p_min rises to p_max − C. The band is priced at B. The unit stays committed every hour.
•  The PEM sells to the grid when the price is above B. It adds no load.

What the model omits

•  No electrolyzer efficiency curve, minimum load, ramp limit or capex.
•  No hydrogen revenue or storage.
•  Cost objective = system cost minus the synthetic bid costs. This removes the nuclear unit's real fuel cost at any ω: a constant on RTS (the g1 item), a bias against the base case on ERCOT.

Every result in this deck is about priced withholding of renewable and nuclear output. Electrolyzer physics is future work.

**Notes:** Sources: parameters.py (renewable split, thermal patch); summarize_wave.py header note on synthetic cost; power-systems review 10-13 §3.

## Slide 6

The loop runs unattended except for qsub; CRC submission stays manual


BO campaign + ERCOT v2 · 2026-10-13

ROADBLOCKER · CRC compute nodes cannot qsub

array
8 Prescient runs

collector
objectives, push

acquisition
grade, propose, push

submit next round
fails: compute nodes are not submit hosts

Chain per round; dashed = next round.

•  Unattended hops worked: both collectors, both acquisitions (grade → propose → commit → push).
•  The submit hop cannot work on CRC: compute nodes are not submit hosts.
•  The WEDGED trap fired and left a clear record. Kay submitted round 2 by hand.
•  r2 acquisition re-run on the Mac: weights and all 8 designs identical to CRC.
•  Proposed fix (not implemented): submit the whole chain from the login node with -hold_jid; or a login-node cron watcher.
•  This limits claim W: "unattended" holds up to job submission.

**Notes:** Notes: B pain log + audit table.
Sources: /Users/yilu/Documents/GitHub/RTS-GMLC/trial_0826/campaign/analysis/bo_stage2/BO_STAGE2.md; /Users/yilu/Documents/GitHub/RTS-GMLC/trial_0826/campaign/analysis/bo_stage2/ROUND_LOG.md

## Slide 7

The stop rule fired at the earliest possible round: τ (8 %) is larger than BO's whole gain (6.9 %)


BO campaign + ERCOT v2 · 2026-10-13

/Users/yilu/Documents/GitHub/RTS-GMLC/trial_0826/campaign/analysis/bo_stage2/figs/fig2_hv_trajectory.png

•  HV: 6.606e17 → 6.969e17 (+5.5 %) → 7.061e17 (+1.4 %). Both gains are under τ.
•  5 of 16 BO designs lie outside the fixed box and earn zero HV. With a wider box the gains are 2.6 % and 2.0 %.
•  The front is dense: 26 of 48 points are non-dominated.
•  The stop means "gains below a conservative materiality bar". It does not mean "converged".
•  Prompt 37 tests this directly. Its pre-registered reading: if S0 matches "stop after 2 rounds", the paper says so and reports the τ at which the rule starts to adapt.

**Notes:** Figure: /Users/yilu/Documents/GitHub/RTS-GMLC/trial_0826/campaign/analysis/bo_stage2/figs/fig2_hv_trajectory.png
Notes: B §2 (old slides 9 and 11); P37 pre-registered reading.
Sources: /Users/yilu/Documents/GitHub/RTS-GMLC/trial_0826/campaign/analysis/bo_stage2/BO_STAGE2.md; /Users/yilu/Documents/development/nd/research/admin/prompt/bogp/37-stop-rule-validation.md

## Slide 8

BO's front spans $510M with 29 GWh shed to zero shed at $582M


Costs are g1-pending (option c adds +$28.188M to every design)

/Users/yilu/Documents/GitHub/RTS-GMLC/trial_0826/campaign/analysis/bo_stage2/figs/fig1_front.png

| Best in | Design(s) |
| Shed | 4 designs tie at 0; cheapest r2#6 $582M; r1#5 = 0 shed + lowest curtailment at $668M |
| Curtailment | r1#5: 48 GWh, $668M (nuclear ω = 1.0) |
| Cost | r2#3: $510M (all tiers 0.05 except tail 1.0; 29 GWh shed, 1.26 TWh curtailed) |

**Notes:** Figure: /Users/yilu/Documents/GitHub/RTS-GMLC/trial_0826/campaign/analysis/bo_stage2/figs/fig1_front.png
Notes: B §1. Footer: costs g1-pending (+$28.188M constant under option c).
Sources: /Users/yilu/Documents/GitHub/RTS-GMLC/trial_0826/campaign/analysis/bo_stage2/BO_STAGE2.md

## Slide 9

The calibration audit failed on 2 of 3 objectives and changed nothing


BO campaign + ERCOT v2 · 2026-10-13

ROADBLOCKER · corner extrapolation

/Users/yilu/Documents/GitHub/RTS-GMLC/trial_0826/campaign/analysis/bo_stage2/figs/fig3_calibration.png

| Objective | r1 RMS(z) | r2 RMS(z) | Pooled cov95 | Verdict |
| shed | 0.33 | 1.88 | 94 % | not calibrated |
| curtailment | 0.55 | 2.49 | 88 % | not calibrated |
| cost | 0.91 | 1.01 | 100 % | calibrated |

•  r1 too wide, r2 overconfident at corners (r2#3 shed 29.2k vs 8.5k predicted).
•  The audit had no decision role.
•  Prompt 37 tests whether the audit predicts error.
•  Any restart: add corner points; consider shed as a constraint.

**Notes:** Figure: /Users/yilu/Documents/GitHub/RTS-GMLC/trial_0826/campaign/analysis/bo_stage2/figs/fig3_calibration.png
Notes: B §3; P37.
Sources: /Users/yilu/Documents/GitHub/RTS-GMLC/trial_0826/campaign/analysis/bo_stage2/BO_STAGE2.md; /Users/yilu/Documents/development/nd/research/admin/prompt/bogp/37-stop-rule-validation.md

## Slide 10

BO places at the 94th percentile of random 16-design batches; the lead is below τ


BO campaign + ERCOT v2 · 2026-10-13

Left: /Users/yilu/Documents/GitHub/RTS-GMLC/trial_0826/campaign/analysis/random_baseline/figs/fig1_hv_band.png
Right: /Users/yilu/Documents/GitHub/RTS-GMLC/trial_0826/campaign/analysis/random_baseline/figs/fig2_percentile_hist.png

Design: 48 uniform random lattice designs; 100,000 random 16-subsets; "above" needs p̂ ≥ 0.90 and p_lo ≥ 0.50 at both refs (pre-registered).

| Ref | BO HV/HV₀ | Random p10 / p50 / p90 | BO − median | p̂48 [interval] | Row |
| R_frozen | 1.0688 | 1.0158 / 1.0421 / 1.0651 | +0.027 | 0.94 [0.84, 1.00] | above |
| R_union | 1.0460 | 1.0083 / 1.0204 / 1.0311 | +0.026 | 1.00 [1.00, 1.00] | above |

R_frozen (fixed before round 1) is the honest primary. R_union credits BO's corner picks; its 1.00 restates the extremes result.

**Notes:** Figures: /Users/yilu/Documents/GitHub/RTS-GMLC/trial_0826/campaign/analysis/random_baseline/figs/fig1_hv_band.png
/Users/yilu/Documents/GitHub/RTS-GMLC/trial_0826/campaign/analysis/random_baseline/figs/fig2_percentile_hist.png
Notes: P34 §0.1, §3.1–3.2; R §2; statistics reviewer (expert review 10-12).
HOW TO READ THE TWO REFS. HV needs a reference point: the 'worst corner' of the box. A design that is worse than the ref on ANY objective earns zero HV. R_frozen = nadir of the 32 starts + 10 % span, fixed before round 1 (shed 15,102 MWh; curtailment 670,350 MWh; cost $652.0M). R_union = the same formula over all 96 designs (shed 32,100 MWh; curtailment 1,385,278 MWh; cost $684.3M); it equals BO_STAGE2's REF48. R_frozen leans toward random: 5 of BO's 16 picks are corner designs outside this box and earn zero. R_union leans toward BO: the bigger box credits those corners, so p-hat = 1.00 there mostly restates the S1 extremes result. Rule: 'above' only if above at BOTH refs. Lead with R_frozen. Each panel divides by its own HV0, so do not compare heights across the two panels (1.046 vs 1.069). Band = p10-p90 of random subsets (8-subsets at n = 40, 16-subsets at n = 48; 100,000 each).
Sources: /Users/yilu/Documents/GitHub/RTS-GMLC/trial_0826/campaign/analysis/random_baseline/RANDOM_BASELINE.md; /Users/yilu/Documents/development/nd/research/admin/prompt/bogp/34-random-baseline.md

## Slide 11

The percentile lead depends on load-shed differences smaller than the floor


BO campaign + ERCOT v2 · 2026-10-13

ROADBLOCKER · sensitivity to sub-floor shed differences

Pre-registered
1,000 perturbed draws (floors 3,000 MWh / 5,000 MWh / $0.5M).
467 above, 531 comparable, 2 matched.
0.467 < 0.8 → "not robust to floor-level output perturbation".
The flag stays.

POST-HOC (not pre-registered)
The shed floor (3,000 MWh) is 20 % of the R_frozen shed width (15,102 MWh).
Without shed noise, 0.89 of draws keep "above"; clipping shed at 0 gives 0.48.
RTS runs are deterministic, so this is a materiality stress test, not measurement noise.

Reading
"BO's percentile lead depends partly on load-shed differences smaller than 3,000 MWh." Also: p̂ = 0.94 sits only 0.04 above the 0.90 cutoff.
Shed materiality is restated after prompt 38 (22.426 MWh plateau).

**Notes:** Notes: R §3; strategy-session check 10-12; statistics reviewer (expert review 10-12); P38.
Sources: /Users/yilu/Documents/GitHub/RTS-GMLC/trial_0826/campaign/analysis/random_baseline/RANDOM_BASELINE.md; /Users/yilu/Documents/development/nd/research/admin/prompt/bogp/38-rts-mechanism-checks.md

## Slide 12

BO's clearest result: both extremes lie beyond every random design


Costs are g1-pending (option c adds +$28.188M to every design)

/Users/yilu/Documents/GitHub/RTS-GMLC/trial_0826/campaign/analysis/random_baseline/figs/fig3_s1_extremes.png

| Objective | BO best | Best of 48 random | BO ahead by > floor? |
| shed | 0 | 0 | no (tie) |
| curtailment | 48,444 MWh (r1#5) | 61,739 (rnd#15) | yes, 13.3 GWh |
| cost | $510.1M (r2#3) | $536.0M (rnd#42) | yes, $25.9M |

•  No random 16-batch came within a floor of either extreme.
•  Both extremes are corners.
•  A minimum-build heuristic would likely find the cost corner; it was not run.
•  The curtailment extreme puts the nuclear band at ω = 1.0: its hydrogen is nuclear energy, and gas replaces it.

**Notes:** Figure: /Users/yilu/Documents/GitHub/RTS-GMLC/trial_0826/campaign/analysis/random_baseline/figs/fig3_s1_extremes.png
Notes: R §4.2; power-systems reviewer (expert review 10-12); power-systems review 10-13.
Sources: /Users/yilu/Documents/GitHub/RTS-GMLC/trial_0826/campaign/analysis/random_baseline/RANDOM_BASELINE.md

## Slide 13

The recipe narrows to two rules; prompt 35 tests them out of sample


Costs are g1-pending (option c adds +$28.188M to every design)

DECISION · approve the narrowed recipe wording

| Normalization | Knee | Source | Nuclear ω | Total MW | wind_303+317 share | wind_122 ω | In old R |
| full | rnd#2 | random | 0.05 | 1,491 | 0.70 | 0.169 | no |
| full | n0b#8 | start | 0.05 | 1,699 | 0.79 | 0.169 | yes |
| full | r1#2 | BO | 0.05 | 1,705 | 0.68 | 0.288 | yes |
| clipped | r2#1 | BO | 0.05 | 1,825 | 0.58 | 0.525 | no |
| clipped | rnd#43 | random | 0.05 | 2,084 | 0.55 | 0.644 | no |
| clipped | r1#2 | BO | 0.05 | 1,705 | 0.68 | 0.288 | yes |

Holds
Nuclear at 0.05; wind_303 + wind_317 share ≥ 0.5 (0.55–0.79).
Fails
The 1.6–2.0 GW band; the wind_122 cap (drop it).

Key point
Total MW is the position along the front, not a size rule. Across 1.49 → 2.08 GW cost rises about 5 % and curtailment falls about 44 %. The size is a curtailment-vs-cost choice.
Physics: a nuclear PEM diverts cheap baseload, so it never wins on cost.

Caveats

•  Designs within 0.03 of the knee distance include some with wind share < 0.5, so the share rule describes the knees, not the whole front.
•  ω = 0.05 is the lattice floor, so "nuclear at the floor" means "no nuclear retrofit" in practice.
•  r2#1 was already outside the old R at write time (a gap in the prompt-34 pre-submission check).
•  R′ was derived from P1; P2/P3 are the out-of-sample test.

**Notes:** Notes: R §4.3 iii; power-systems reviewer (expert review 10-12); P35 (P2/P3 out-of-sample).
Proposed paper wording (power-systems reviewer, verbatim):
"Every knee design, under either normalization, places the nuclear retrofit at its lattice minimum (ω = 0.05, 20 MW) and puts most of the PEM capacity (55–79%) on the two largest wind sites (buses 303 and 317). Total PEM capacity sets the position along the front, not membership of the knee region. Knees span 1.49–2.08 GW as the normalization changes. Over that range, cost rises about 5% while curtailment falls about 44%. The total therefore expresses a choice between curtailment and cost, not a recommended size."
Sources: /Users/yilu/Documents/GitHub/RTS-GMLC/trial_0826/campaign/analysis/random_baseline/RANDOM_BASELINE.md; /Users/yilu/Documents/GitHub/RTS-GMLC/trial_0826/campaign/analysis/bo_stage2/BO_STAGE2.md; /Users/yilu/Documents/development/nd/research/admin/prompt/bogp/35-stage2-methods-arms.md

## Slide 14

Paper wording: what we can say now and what we cannot


BO campaign + ERCOT v2 · 2026-10-13

Can say

•  "An automated, pre-registered MOBO campaign on a real PCM terminated under its rule within budget."
•  "This BO run's HV exceeded 94 % of random 16-design batches (+0.027 HV₀, below our 8 % materiality bar, sensitive to sub-floor load-shed differences). Its clearer distinction is reaching the cost and curtailment extremes, $26M and 13 GWh beyond any of 48 random designs."
•  Found designs are consistent with the LOCATION sensitivity structure (claim iii: supported).
•  The narrowed recipe (slide 13).

Cannot say

•  "beat random", "significant", "robust", any p-value
•  anything about q-ParEGO in general (one seed) or seed stability (claim ii: not shown)
•  "converged" (claim i: not shown)
•  anything vs Sobol or a heuristic; the R_union [1, 1] as certainty; the ~70 % model-world figure
•  anything beyond scenario C (A/B not run)
•  reliability benefit of PEM (prompt 38 open)

**Notes:** Notes: B claim scope; ML §5.2; statistics reviewer (expert review 10-12); methods review 10-13.
Sources: /Users/yilu/Documents/GitHub/RTS-GMLC/trial_0826/campaign/analysis/bo_stage2/BO_STAGE2.md; /Users/yilu/Documents/development/nd/research/admin/prompt/bogp/math-log.md

## Slide 15

Pre-registered or post hoc: every deviation on one page


BO campaign + ERCOT v2 · 2026-10-13

| Item | Pre-registered? | What changed | When | Disclosure |
| Stop rule, τ, R_frozen | yes (prompt 30) | — | 10-06 | — |
| M = 3 objectives | decided after the 32 starts landed | — | 10-06 | state in paper |
| Random-baseline wording | yes (prompt 34) | — | 10-10 | — |
| Primary reference for 35 = R_union | frozen 10-12, after R_union gave p̂ = 1.00 | lead reference changed from R_frozen | 10-12 | justify or make R_frozen co-primary (decision) |
| Shed-noise diagnostic, recipe narrowing | post hoc | — | 10-12 | labelled post hoc |
| N1 replay gate | yes (two-sided) | made one-sided after the result | 10-12 | P13 (next slide) |
| 37 Amendment 1 | before results | 400 local 6-D random runs quarantined | 10-12 | PREREG amendment |
| ERCOT smoke gate | amended before results | cost ±15 % vs authors' SCUC | 10-12 | ERCOT_COST_FIX |
| ERCOT wave-D site rule | yes, text unchanged | committed after B landed, before any per-site value was read | 10-13 | CARRIED_OVER / T3 |
| 35 relaunch, software stack | — | ~/.local packages are part of the frozen stack | 10-12 | P14 |

**Notes:** Sources: methods review 10-13 §3.2–3.3; P30, P34, P35 §3.2, P37 Amendment 1, ERCOT_COST_FIX (df61ab4).

## Slide 16

The N1 gate was changed after its result: three items to sign off


BO campaign + ERCOT v2 · 2026-10-13

DECISION · PI sign-off

What happened

•  Pre-registered gate (35 §3.2): the qNEHVI replay median must lie INSIDE the q-ParEGO smoke range at n = 16 and 24.
•  Result: n = 16: 0.9166, inside. n = 24: 0.9534, above the q-ParEGO maximum 0.9518.
•  The gate failed HIGH.
•  Amendment 10-12, after the result: one-sided (median ≥ q-ParEGO minimum) → PASS. N1 now runs.

Sign off

•  (a) Accept the amendment and its disclosure text (P13).
•  (b) N1 vs P1 is reported as "consistent with" at most: one seed; model, acquisition and noise handling change together.
•  (c) Fix now: if qNEHVI beats q-ParEGO on real runs by more than the P1–P3 spread, the paper reports both and keeps q-ParEGO as the workflow default because ______ (agree today: cost, simplicity, or prior pre-registration).

**Notes:** Sources: P35 §3.2 AMENDMENT 10-12; replay_gate.json; methods review 10-13.
Sources: /Users/yilu/Documents/development/nd/research/admin/prompt/bogp/35-stage2-methods-arms.md

## Slide 17

Prompt 35 decides claim (ii) by a fixed four-part rule


BO campaign + ERCOT v2 · 2026-10-13

•  Claim (ii) holds only if ALL four parts pass:
–  (1) P1, P2, P3 each p̂48 ≥ 0.8 at R_union, raw and floor-robust HV.
–  (2) HV range across P1–P3 at n = 64 ≤ 1 τ̄.
–  (3) Each replicate's top-3 knees satisfy R′ above the base rate.
–  (4) Curtailment extreme beyond the pool's best by > floor in ≥ 2 of 3.
•  Reading fixed now: all pass → supported at C. P1 passes, P2/P3 fail → "one of three"; the result depends on the start set. All fail → not shown. The workflow claim stands in every case.
•  Likely outcome (methods review): the AND-rule fails on at least one part. Plan the "one of three" wording now.
•  P1 rounds 3–4 test the live stop on real data: any post-stop round > τ is an early stop.
•  Sobol Q1–Q3: descriptive only.

**Notes:** Sources: P35 §5; methods review 10-13.
Sources: /Users/yilu/Documents/development/nd/research/admin/prompt/bogp/35-stage2-methods-arms.md

## Slide 18

Prompt 37 has one confirmatory test with fixed acceptance thresholds


BO campaign + ERCOT v2 · 2026-10-13

•  Primary cell: emulator sample paths E-path-1…5 × q-ParEGO × live rule S0 (τ = 1·τ_j, w = 2, q = 8, cap 4), 50 seeds.
•  Accept only if: early-stop rate ≤ 20 % AND median regret ≤ 1 τ AND S0 on or below the fixed-budget line S-fix-k, on the primary problems AND on the needle problem.
•  Comparators: S-fix-1…8, relative-gain rule, model-based rule (qNEHVI), OCD-style test, oracle.
•  Pre-registered reading: S0 ≡ S-fix-2 almost everywhere → "the rule acts as a 2-round budget at this τ".
•  Limit: the emulators are fit on scenario-C data. They are not a second problem instance.

**Notes:** Sources: P37 §4–5.
Sources: /Users/yilu/Documents/development/nd/research/admin/prompt/bogp/37-stop-rule-validation.md

## Slide 19

Two RTS mechanism questions gate the shed axis; prompt 38 answers them


BO campaign + ERCOT v2 · 2026-10-13

| Question | Most likely answer | Check (prompt 38) |
| Why does shed fall as withheld MW rises (Spearman −0.94)? | H1: in the RUC the slice is a $40 resource, so more thermal is committed and real-time headroom grows. H2: the slice sells when the price exceeds B, so it delivers in scarcity hours. | Committed MW and headroom on shed hours, low- vs high-MW designs; shed hours vs price > B. |
| Is shed traded for reserve shortfall (H4)? | Unknown | Reserve shortfall vs total MW over 96 designs. If yes, the shed axis, τ and HV need rework. |
| Why do 7 front designs share shed = 22.426 MWh? | One PEM-independent event | Bus-hour of the shed; is it in the no-PEM base? |

Curtailment netting is closed: prompt 35 G1 closure PASS. Owner: hand off prompt 38 now (0 PCM runs).

**Notes:** Power-systems reviewer 10-12; power-systems review 10-13; parameters.py (renewable split), summarize_wave.py:113-116. Hypotheses until checked. 35 G1 closure: d876321.
Sources: /Users/yilu/Documents/GitHub/RTS-GMLC/trial_0826/campaign/analysis/bo_stage2/BO_STAGE2.md; /Users/yilu/Documents/development/nd/research/admin/prompt/bogp/38-rts-mechanism-checks.md; /Users/yilu/Documents/development/nd/research/admin/prompt/bogp/35-stage2-methods-arms.md

## Slide 20

ERCOT v2 runs clean at the system level; the fuel mix needs a check


BO campaign + ERCOT v2 · 2026-10-13

| Quantity (2019, base) | v1 (mis-converted costs) | v2 (corrected) |
| Real-time LMP, mean | $14.5/MWh | $33.8/MWh |
| Fixed cost | $6.75 B | $3.63 B |
| Variable cost | $1.19 B | $4.46 B |
| True curtailment | 9.44 M MWh | 5.92 M MWh |
| Nuclear | gen-1 cycles (≈ 25 starts) | both units on all 8,760 h, 0 starts |
| RUC quality | TimeLimit races on capped days | 0 % capped; 1,460 / 1,460 OPTIMAL |
| Replicate spread (total cost) | ±$80M bimodal | 0 (4 runs byte-identical) |
| Coal / gas share | — | 32 % / 34 % (2019 actual ≈ 20 % / 47 %, verify) |
| PV energy | — | 17.6 TWh from 8.3 GW (2019 actual ≈ 4–5 TWh, verify) |

•  v1 used mis-converted cost data (start-up energy read as a heat rate). Every v1 output is replaced.
•  Corrected costs make nuclear baseload (informs NXT-D6).
•  The coal-gas split sets the marginal unit and the cost of replacing withheld wind. Check fuel mix and fuel prices against the TX-123BT paper and 2019 data before the AIChE figures.
•  Deterministic is not exact: the RUC still stops at ≤ 1 % gap (median 0.72 %). A bid-0 placebo row gives the real ruler.

**Notes:** T3 base read: ercot df61ab4 (ERCOT_COST_FIX.md); extract base_2019_v2 (e3082fa). v1 replicate spread: screening bimodality ±$79.5M (3edd682) and TL=360 probe |Δ| $56–127M (c9d28cd). v1 mapping error: old slide 28 (backup B6). Fuel mix and PV: power-systems review 10-13.
Sources: /Users/yilu/Documents/development/nd/research/admin/prompt/bogp/living-report-multipem.md; /Users/yilu/Documents/development/nd/research/admin/prompt/bogp/PROGRESS.md

## Slide 21

ERCOT screening: relief is real, but a third of the "hydrogen" is diverted wind


BO campaign + ERCOT v2 · 2026-10-13

0 MWh

shed (4 base + 19 screening runs)

$33.8/MWh

mean RT LMP ($36.4 load-weighted)

0.61–0.67

MWh curtailment avoided per MWh H2 (top wind sites)

0.38

the same ratio at PV site 30

•  Shed is a checked constraint on ERCOT. Its span is zero, so any ERCOT BO uses two objectives: true curtailment and cost.
•  B = $40 lies above the mean price and above coal, so the PEM withholds in most hours. 33–40 % of the withheld energy would have served load; thermal replaces it.
•  Screening row 10 shows the mechanism: 15.7 TWh withheld, 3.75 TWh of it curtailment; about 12 TWh replaced by thermal → +$354M.
•  Report curtailment avoided per MWh of hydrogen next to relief per MW.

**Notes:** Sources: ERCOT extracts screening_v2 (2ba803b) and base_2019_v2 (e3082fa); power-systems review 10-13.

## Slide 22

Wave D needs contrast, a placebo and a nuclear cost fix


BO campaign + ERCOT v2 · 2026-10-13

DECISION · approve the redesigned wave D

As proposed (rule 4fb3b1f, ruler = 0 → top 6)

•  Sites 163, 140, 146, 270, 110, 274 × 60/120/180 MW + nuclear × 3 = 21 rows.
•  Problems:
–  The six differ by 9 % in relief/MW and sit on 3 buses (120 ×3, 2 ×2, 75).
–  180 MW is 97 % of site 163's nameplate but 24 % of site 274's.
–  Nuclear rows carry the cost bias (slide 5).

Redesign (21 rows)

•  163, 140, 146 (best per bus) + PV 116, PV 30 + the last-ranked wind site, each × 60/120/180 MW.
•  + one bid-0 placebo.
•  + nuclear × 2 after the cost fix.
•  Plot the nameplate fraction too.

The pre-registered rule stays on record. The redesign is a disclosed amendment: the rule selects similar sites, so it cannot show the location effect.

**Notes:** Sources: power-systems review 10-13 §3; ercot 4fb3b1f (top-k rule). The 36 session builds after Kay approves.

## Slide 23

What reviewers will require, and what is now running


BO campaign + ERCOT v2 · 2026-10-13

| # | Requirement | Why | Cost | Status 10-13 |
| 1 | Stop-rule validation: early/late-stop rates and regret at stop on truth-known problems (replay, synthetic functions, GP emulator of Stage 2); compare with existing BO stop rules | The stop rule is the most novel part of the workflow; today it has no operating characteristic | 0 PCM runs | running (37) |
| 2 | Fixed-budget comparison: every arm to 32 + 4×8; apply the stop rule post hoc to the same trajectories | BO stops on its own rule, baselines have none — budgets differ | seed 1: +16 runs | running (35) |
| 3 | q-ParEGO ≥ 3 replicates, ≥ 2 with NEW starts; qNEHVI ≥ 3 seeds paired by start set | Acquisition-only seeds share 2/3 of the data and understate variance; qNEHVI is the comparator reviewers expect | ≈ 3–4k core-h at C | partly running (2 new start sets, 1 qNEHVI seed) |
| 4 | Scenarios A and B as extra problem instances (cheapest: q-ParEGO + random) | One instance = a case study, not a methods result | ≈ 1–5k core-h each | no prompt (decision) |
| 5 | D3 noise floors + a floor-robust metric, pre-registered before new runs | Today's differences sit below the floor | spec first | spec only |
| 6 | Emulator benchmark (≥ 20 seeds per method); calibration audit with a decision role | Cheap method-level statistics; the audit failed 2 of 3 objectives with no consequence | 0 PCM runs | running (37) |

**Notes:** Contribution = the WORKFLOW (pre-registered, auditable, unattended MOBO with a materiality stop), for an applied-methods venue; not a new BO algorithm. Row 1 truth-known problems in full: replay A/B/C, synthetic functions with floor-matched noise, GP emulator of Stage 2. Downgraded: Sobol to one continuation per start set (descriptive); knee-only re-runs. Dropped: ≥ 20 real Stage-2 seeds, lower-τ continuation, 5-batch Sobol, other weather years, GP-fix restart. Total ≈ 4k (C + cheapest A/B) to ~14k core-h (full arms). Living report §9.7. Status column: PROGRESS 10-13.
Sources: /Users/yilu/Documents/development/nd/research/admin/prompt/bogp/math-log.md; /Users/yilu/Documents/development/nd/research/admin/prompt/bogp/living-report-multipem.md; /Users/yilu/Documents/development/nd/research/admin/prompt/bogp/PROGRESS.md

## Slide 24

AIChE: one message, five figures, a fallback


BO campaign + ERCOT v2 · 2026-10-13

Message
"An electrolyzer's grid value depends on where it sits: at congested wind buses it avoids about 0.6 MWh of curtailment per MWh of hydrogen; at solar or nuclear sites it avoids less at higher cost. Multi-objective BO maps these trade-offs in tens of production-cost runs."

Five figures

•  (1) PEM-model schematic (slide 5).
•  (2) RTS 96-design front (backup B3).
•  (3) RTS knee composition (slide 13).
•  (4) ERCOT relief/MW and Δcurt/H2 for all 16 sites + nuclear.
•  (5) ERCOT size response with the placebo band.

Calendar

| Dates | Work |
| 10-13 → 10-19 | 35 lands; 37 lands; ERCOT C + fuel-mix check; wave D redesign submitted. |
| 10-20 → 10-25 | Wave D lands; 38 done; figures drafted. |
| 10-26 → 11-01 | Figures frozen 11-01. |
| 11-02 → 11-08 | Talk. |

Fallback: if 35 is late, figures 2–3 use the existing single run with its stated limits. If wave D is late, figure 5 is dropped.

**Notes:** Rebuilt from old slide 26 (execution order). Message and figure list: OUTLINE_1013 §24; power-systems review 10-13. Figure freeze 11-01, talk 11-02 → 11-08 as in bo_1012.
Sources: /Users/yilu/Documents/development/nd/research/admin/prompt/bogp/living-report-multipem.md; /Users/yilu/Documents/development/nd/research/admin/prompt/bogp/PROGRESS.md

## Slide 25

Decisions today


BO campaign + ERCOT v2 · 2026-10-13

D1

Sign off the N1 amendment (a, b, c on slide 16).

D2

Primary HV reference for 35: keep R_union with a written justification, or make R_frozen co-primary.

D3

Scenarios A/B before submission, or a claim stated for scenario C only.

D4

Approve the redesigned wave D (+ placebo; nuclear after the cost fix).

D5

ERCOT fuel-mix check before the AIChE figures (owner: 36 session).

D6

Hand off prompt 38 now.

D7

g1 ruling (NXT-D7) still open; ERCOT nuclear rows have the same accounting issue.

**Notes:** D1/D2 of bo_1012 (methods design, BoTorch) were approved 10-12 (NXT-D9). D1 → slide 16; D2 → slides 15–16; D3 → slides 14, 23; D4 → slide 22; D5 → slide 20; D6 → slide 19; D7 → slide 5.

## Slide 26


BACKUP

Backup

B1–B7: supporting slides.

**Notes:** Backup slides B1–B7.

## Slide 27

B1 · Timeline 09-19 → 10-13


BO campaign + ERCOT v2 · 2026-10-13

| Date | Event |
| 09-19 → 09-22 | Stage-2 starts: 32 Sobol designs (n0 + n0b) run on CRC |
| 10-06 | M = 3 approved: load shed, true curtailment, cost less synthetic |
| 10-07 | Chain launched (block_1); 2 harness fixes first |
| 10-08 | Round 1 results; acquisition WEDGED at qsub (compute node is no submit host) |
| 10-09 | Round 2 submitted by hand from the login node (≈ 20 h lost) |
| 10-10 | Round 2 results; stop rule fires → BO_DONE; BO_STAGE2.md written and reviewed |
| 10-10 | Prompt 34 (random baseline) pre-registered, 3-agent review |
| 10-11 | 48 random designs built, run (11:00 → 20:22), analysed (23:29) |
| 10-12 | Expert review of the random-baseline result (statistics + power systems) |
| 10-12 | Prompts 35, 36, 37 written and launched |
| 10-13 | ERCOT waves A + B landed; base read done |

**Notes:** Timeline from B (status line, pain log), ROUND_LOG.md, R, P34 and LR rows 10-06 … 10-13b; PROGRESS 10-13.
Sources: /Users/yilu/Documents/GitHub/RTS-GMLC/trial_0826/campaign/analysis/bo_stage2/BO_STAGE2.md; /Users/yilu/Documents/GitHub/RTS-GMLC/trial_0826/campaign/analysis/bo_stage2/ROUND_LOG.md; /Users/yilu/Documents/GitHub/RTS-GMLC/trial_0826/campaign/analysis/random_baseline/RANDOM_BASELINE.md; /Users/yilu/Documents/development/nd/research/admin/prompt/bogp/34-random-baseline.md; /Users/yilu/Documents/development/nd/research/admin/prompt/bogp/living-report-multipem.md; /Users/yilu/Documents/development/nd/research/admin/prompt/bogp/PROGRESS.md

## Slide 28

B2 · BO moves to the lattice edges; nuclear leaves the floor only at the reliability corners


BO campaign + ERCOT v2 · 2026-10-13

/Users/yilu/Documents/GitHub/RTS-GMLC/trial_0826/campaign/analysis/bo_stage2/figs/fig4_front_designs.png

| Set | Tiers at an edge (of 6) | Fully interior |
| starts | 0.75 | 44 % |
| r1 | 1.9 | 0 % |
| r2 | 3.25 | 0 % |

•  Nuclear is bang-bang: 0.05 on the knees, 1.0 at the reliability corners. Spearman(nuclear MW, cost) = 0.89.
•  wind_303 and wind_317 are loaded up on the front (mean ω 0.65 / 0.61).
•  Tail goes to 1.0 in r2, but it correlates with nothing. Read it as EI pushing a flat direction, not a tail effect.

**Notes:** Figure: /Users/yilu/Documents/GitHub/RTS-GMLC/trial_0826/campaign/analysis/bo_stage2/figs/fig4_front_designs.png
Notes: B §4.
Sources: /Users/yilu/Documents/GitHub/RTS-GMLC/trial_0826/campaign/analysis/bo_stage2/BO_STAGE2.md

## Slide 29

B3 · Grand front of 96 designs


BO campaign + ERCOT v2 · 2026-10-13

/Users/yilu/Documents/GitHub/RTS-GMLC/trial_0826/campaign/analysis/random_baseline/figs/fig4b_grand_front_unified.png

•  Same panels and markers as slide 8. Of the 13 starts on the 48-point front, 6 are now dominated by random designs; all 13 BO front designs stay.
•  32 designs on the 96-point front: BO 13 of 16 (81 %), random 12 of 48 (25 %), starts 7 of 32.
•  A random 16-batch puts 6.6 designs (p10–p90 5–8) on the front of starts ∪ batch. BO puts 13.
•  No random design dominates any BO design (set coverage 0.00).

**Notes:** Figure: /Users/yilu/Documents/GitHub/RTS-GMLC/trial_0826/campaign/analysis/random_baseline/figs/fig4b_grand_front_unified.png
Notes: R §4.3–4.4.
Sources: /Users/yilu/Documents/GitHub/RTS-GMLC/trial_0826/campaign/analysis/random_baseline/RANDOM_BASELINE.md

## Slide 30

B4 · Status card 10-12


BO campaign + ERCOT v2 · 2026-10-13

48

designs evaluated by the campaign (32 Sobol starts + 2 BO rounds of 8)

26

designs on the final 3-objective front (13 starts, 6 r1, 7 r2)

+5.5 % → +1.4 %

HV gain per round, under the 8 % stop threshold → BO_DONE 10-10

48

uniform random designs run as the baseline (10-11, 9.4 h wall)

0.94

percentile of BO's HV among random 16-design batches (R_frozen)

0.83

rounds per day (one 20 h stall: CRC compute nodes cannot submit jobs)

**Notes:** Notes: B status line, §2, pain log; R §2; LR 10-11c.
Sources: /Users/yilu/Documents/GitHub/RTS-GMLC/trial_0826/campaign/analysis/bo_stage2/BO_STAGE2.md; /Users/yilu/Documents/GitHub/RTS-GMLC/trial_0826/campaign/analysis/random_baseline/RANDOM_BASELINE.md; /Users/yilu/Documents/development/nd/research/admin/prompt/bogp/living-report-multipem.md

## Slide 31

B5 · ERCOT wave C: nuclear rows failed on the T0 output; fixed and rerun


BO campaign + ERCOT v2 · 2026-10-13

•  Wave C: nuclear rows ω = 0.05 and 0.2875 failed at the first RUC build.
•  The PEM patch raises p_min, but the T0 output stays at the original 729 MW.
•  CRC log selection_t1_v2_array.o1533432.6: "Generator 1 has less output at T0 than is feasible to ramp up to". Same family as 1eaf05e (startup capacity).
•  The thermal patch also sets ramp_up_60min = PEM capacity (ω × 2,430 MW), so the egret T0 check depends on ω.
•  Fix (7c5fb8d): T0 output ≥ new p_min. A build-only test reproduces the error without the fix and passes 6/6 with it.
•  All nuclear rows 6–11 are rerun, so that the ω sweep shares one T0.
•  Old rows 6–11 are quarantined in runs/quarantine_T0_729, not deleted.

**Notes:** Wave C failure: 02b147d, CRC log selection_t1_v2_array.o1533432.6. Fix 7c5fb8d. From bo_1012 slide 32.
Sources: /Users/yilu/Documents/development/nd/research/admin/prompt/bogp/living-report-multipem.md; /Users/yilu/Documents/development/nd/research/admin/prompt/bogp/PROGRESS.md

## Slide 32

B6 · ERCOT v1: the cost data were mis-converted


BO campaign + ERCOT v2 · 2026-10-13

•  gen.csv HR_avg_0 = Csu · Pmax / fuel price on all 128 thermal units (checked to machine precision). It is a start-up energy in MMBTU, read by Egret as a heat rate in BTU/kWh.
•  HR_incr is a segment heat, read as a rate. Start-up heat = 1 MBTU and start cost = $1 on every unit.
•  Effect: no-load $2.1–2.6M per hour on nuclear (intended ≈ $14k); start-ups nearly free; marginal costs scaled by ΔP/1000, so the merit order is inverted (CT $2.9/MWh vs $43 intended).
•  gen-1 cycling, gen-93 never on, the ±$80M bimodality, TL=360, the rulers, screening, selection_t1: all artifacts or invalid.
•  Fix (prompt 36): find or rebuild the conversion from the TX-123BT paper; corrected data in a NEW versioned directory; regression test against Egret's parsed costs.
•  AIChE promises ERCOT results: re-run base + 2 replicates + screening on the corrected data before the 11-01 figure freeze. Old ERCOT figures are not shown.

**Notes:** Source: processing notebook gtep/123_bus_coal/ERCOT_BUS123_base_XC_editeddata/demo_processing_XC.ipynb. Correct mapping: HR_avg_0 = 1000·C(Pmin)/(fp·Pmin); HR_incr_k = 1000·(ΔC_k/ΔP_k)/fp; start cost = Csu·Pmax. Check GTEP 123-bus work from the same folder. Living report §9.8; TL360_VERDICT banner (ercot e844fa7).
Sources: /Users/yilu/Documents/development/nd/research/admin/prompt/bogp/living-report-multipem.md; /Users/yilu/Documents/development/nd/research/admin/prompt/bogp/math-log.md

## Slide 33

B7 · Operations 10-12/13: env under /groups, import failure + relaunch, 37 fingerprint, CRC lessons


BO campaign + ERCOT v2 · 2026-10-13

35  Methods arms (scenario C)

•  G1 curtailment closure: PASS. G3: runs ≤ 9.4 h (random_C), BO rounds 16–22 h, acquisition 29 min.
•  BoTorch env built on CRC under /groups (home quota is full).
•  Launch 1 failed at import (PYTHONNOUSERSITE hid packages in ~/.local). Fixed; relaunched 21:00, the last allowed relaunch.

37  Stop-rule validation (truth known)

•  PREREG + Amendment 1: 400 local 6-D random runs quarantined; all 6-D work on CRC.
•  Truth files: sha256 verified on CRC. Random-number fingerprint identical on Mac and CRC envs.
•  1,540 tasks: q-ParEGO, qNEHVI and random on 2-D replay grids (method comparison) and 6-D emulator truths (stop-rule test).

CRC lessons (10-12/13)
Envs go under /groups. Test the real entry-path import, not a shallow import. A build-only check over the whole lattice catches patch bugs before a 7 h queue.

**Notes:** 35: d876321 (G1, G3), 1b17f42 (env), 6480264 + 8308211 (import fix, relaunch). 37: 2d529ec (Amendment 1), f5e4c14 (CRC gate + fingerprint). N1 gate moved to slide 16.
Sources: /Users/yilu/Documents/development/nd/research/admin/prompt/bogp/living-report-multipem.md; /Users/yilu/Documents/development/nd/research/admin/prompt/bogp/PROGRESS.md

