# bo_1012.pptx — slide text and speaker notes

## Slide 1


BO CAMPAIGN QUALITY REPORT · 2026-10-12

BO campaign quality report

Stage-2 q-ParEGO on RTS-GMLC, scenario C — what ran, what it found, what it does not show, and what comes next.

**Notes:** Deck built by make_bo_1012_deck.py from OUTLINE.md (content source of truth). Sources: /Users/yilu/Documents/GitHub/RTS-GMLC/trial_0826/campaign/analysis/bo_stage2/BO_STAGE2.md; /Users/yilu/Documents/GitHub/RTS-GMLC/trial_0826/campaign/analysis/bo_stage2/ROUND_LOG.md; /Users/yilu/Documents/GitHub/RTS-GMLC/trial_0826/campaign/analysis/random_baseline/RANDOM_BASELINE.md; /Users/yilu/Documents/development/nd/research/admin/prompt/bogp/34-random-baseline.md; /Users/yilu/Documents/development/nd/research/admin/prompt/bogp/math-log.md; /Users/yilu/Documents/development/nd/research/admin/prompt/bogp/living-report-multipem.md

## Slide 2

How this deck is organised


BO campaign quality report · 2026-10-12

1  Progress

Status and timeline.

2  Technical update

A setup, B BO result, C random baseline, D design recipe, E claim scope.

3  Roadblockers

Roadblockers and open questions.

4  Decision points

Decision points and TODO.

Red badge (top-right) = the slide touches a roadblocker. Green badge = the slide touches a decision. Block 5 (added 10-13, slides 30–34): status of prompts 35, 36, 37.

One-line takeaway
The automated campaign ran and stopped on its rule. This run's HV is above 94 % of random 16-design batches, but the lead is small and sensitive to load-shed differences. BO's clear advantage is the cost and curtailment extremes. The design recipe must narrow.

**Notes:** Organisation follows pi_1008 v2: four blocks. Technical slides that touch a roadblocker get a RED badge, a decision a GREEN badge. Sources: /Users/yilu/Documents/GitHub/RTS-GMLC/trial_0826/campaign/analysis/bo_stage2/BO_STAGE2.md; /Users/yilu/Documents/GitHub/RTS-GMLC/trial_0826/campaign/analysis/random_baseline/RANDOM_BASELINE.md

## Slide 3


BLOCK 1

Progress

Status and timeline.

**Notes:** Block 1: status and timeline.

## Slide 4

Status: BO campaign complete, random baseline complete


BO campaign quality report · 2026-10-12

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

## Slide 5

Timeline 09-19 → 10-12


BO campaign quality report · 2026-10-12

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

**Notes:** Timeline from B (status line, pain log), ROUND_LOG.md, R, P34 and LR rows 10-06 … 10-11c.
Sources: /Users/yilu/Documents/GitHub/RTS-GMLC/trial_0826/campaign/analysis/bo_stage2/BO_STAGE2.md; /Users/yilu/Documents/GitHub/RTS-GMLC/trial_0826/campaign/analysis/bo_stage2/ROUND_LOG.md; /Users/yilu/Documents/GitHub/RTS-GMLC/trial_0826/campaign/analysis/random_baseline/RANDOM_BASELINE.md; /Users/yilu/Documents/development/nd/research/admin/prompt/bogp/34-random-baseline.md; /Users/yilu/Documents/development/nd/research/admin/prompt/bogp/living-report-multipem.md

## Slide 6


BLOCK 2

Technical update

A setup → B BO result → C random baseline → D design recipe → E claim scope.
Red badge = roadblocker, green badge = decision point.

**Notes:** Block 2: technical update.

## Slide 7

Reproducibility card: the campaign configuration (frozen)


BO campaign quality report · 2026-10-12

| Item | Setting |
| Design space | 6 tiers (nuclear, pv, tail, wind_122, wind_303, wind_317) × 9 lattice levels ω ∈ {0.05 … 1.0} = 531,441 designs |
| Scenario | C: ρ = 2.0, B = $40/MWh |
| Objectives (min) | load_shed_mwh, true_curtailment_mwh, total_cost_less_synthetic_usd |
| Starts | 32 Sobol points (shared by every comparison) |
| Acquisition | q-ParEGO, q = 8: 8 Dirichlet weights, EI, kriging believer, discrete lattice candidates |
| HV reference (fixed before round 1) | nadir of the 32 starts + 10 % span; HV₀ = 6.606e17 |
| Stop rule | 2 consecutive rounds with gain < τ = 5.263e16 (8.0 % of HV₀; shed-floor-dominated, conservative) |
| Software | bo-gp feat/qparego @ 60e6328; RTS runs are bit-reproducible |

**Notes:** Notes: B header; prompt 30.
Sources: /Users/yilu/Documents/GitHub/RTS-GMLC/trial_0826/campaign/analysis/bo_stage2/BO_STAGE2.md; /Users/yilu/Documents/development/nd/research/admin/prompt/bogp/30-stage2-bo-campaign.md

## Slide 8

How the loop ran, and the one structural defect


BO campaign quality report · 2026-10-12

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

**Notes:** Notes: B pain log + audit table.
Sources: /Users/yilu/Documents/GitHub/RTS-GMLC/trial_0826/campaign/analysis/bo_stage2/BO_STAGE2.md; /Users/yilu/Documents/GitHub/RTS-GMLC/trial_0826/campaign/analysis/bo_stage2/ROUND_LOG.md

## Slide 9

BO result: HV trajectory and the stop rule


BO campaign quality report · 2026-10-12

/Users/yilu/Documents/GitHub/RTS-GMLC/trial_0826/campaign/analysis/bo_stage2/figs/fig2_hv_trajectory.png

•  HV: 6.606e17 → 6.969e17 (+5.5 %) → 7.061e17 (+1.4 %).
•  Both gains are under the 8 % bar → stop after round 2.
•  The stop means "gains below a conservative noise bar". It does not mean "front converged".
•  Sensitivity: with any bar below 5.5 %, round 3 would have run.

**Notes:** Figure: /Users/yilu/Documents/GitHub/RTS-GMLC/trial_0826/campaign/analysis/bo_stage2/figs/fig2_hv_trajectory.png
Notes: B §2.
Sources: /Users/yilu/Documents/GitHub/RTS-GMLC/trial_0826/campaign/analysis/bo_stage2/BO_STAGE2.md

## Slide 10

BO result: the final front and its corners


Costs are g1-pending (option c adds +$28.188M to every design)

/Users/yilu/Documents/GitHub/RTS-GMLC/trial_0826/campaign/analysis/bo_stage2/figs/fig1_front.png

| Best in | Design(s) |
| Shed | 4 designs tie at 0; cheapest r2#6 $582M; r1#5 = 0 shed + lowest curtailment at $668M |
| Curtailment | r1#5: 48 GWh, $668M (nuclear ω = 1.0) |
| Cost | r2#3: $510M (all tiers 0.05 except tail 1.0; 29 GWh shed, 1.26 TWh curtailed) |

**Notes:** Figure: /Users/yilu/Documents/GitHub/RTS-GMLC/trial_0826/campaign/analysis/bo_stage2/figs/fig1_front.png
Notes: B §1. Footer: costs g1-pending (+$28.188M constant under option c).
Sources: /Users/yilu/Documents/GitHub/RTS-GMLC/trial_0826/campaign/analysis/bo_stage2/BO_STAGE2.md

## Slide 11

Why the gains are small: dense front, not a box artifact


BO campaign quality report · 2026-10-12

•  5 of 16 BO designs lie outside the fixed HV box. They earn zero HV by construction.
•  With a wider box (nadir of all 48 + 10 %), the gains are 2.6 % and 2.0 %. Still small.
•  The main cause is the dense front: 26 of 48 points are non-dominated.
•  Stage-1 replay (2-D, scenario C): BO 0.813 → 0.899 → 0.941 vs random 0.807 → 0.885 → 0.923. BO led by a small margin. Stage 2 repeats that picture in 6-D.

**Notes:** Notes: B §2.
Sources: /Users/yilu/Documents/GitHub/RTS-GMLC/trial_0826/campaign/analysis/bo_stage2/BO_STAGE2.md

## Slide 12

Calibration: the GPs are right for cost, not for shed and curtailment at corners


BO campaign quality report · 2026-10-12

ROADBLOCKER · corner extrapolation

/Users/yilu/Documents/GitHub/RTS-GMLC/trial_0826/campaign/analysis/bo_stage2/figs/fig3_calibration.png

| Objective | r1 RMS(z) | r2 RMS(z) | Pooled cov95 | Verdict |
| shed | 0.33 | 1.88 | 94 % | not calibrated |
| curtailment | 0.55 | 2.49 | 88 % | not calibrated |
| cost | 0.91 | 1.01 | 100 % | calibrated |

•  r1 too wide, r2 overconfident at corners (r2#3 shed 29.2k vs 8.5k predicted).
•  Calibration was report-only; no gate was violated.
•  Any restart: add corner points.

**Notes:** Figure: /Users/yilu/Documents/GitHub/RTS-GMLC/trial_0826/campaign/analysis/bo_stage2/figs/fig3_calibration.png
Notes: B §3.
Sources: /Users/yilu/Documents/GitHub/RTS-GMLC/trial_0826/campaign/analysis/bo_stage2/BO_STAGE2.md

## Slide 13

Where BO went: outward to the edges


BO campaign quality report · 2026-10-12

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

## Slide 14

Random baseline: why, and how it was pre-registered


BO campaign quality report · 2026-10-12

DECISION · Kay chose option (c), 10-10

•  Question: is this BO run better than random 16-design batches at the same budget?
•  48 uniform random lattice designs, never repeating the evaluated 48. One i.i.d. pool.
•  Statistic: draw 100,000 random 16-subsets of the pool; p̂48 = fraction with HV below BO's.
•  Interval: 1,000 pool bootstraps. Two refs: R_frozen (ledger) and R_union (all 96 points).
•  Wording fixed before results: "above" needs p̂ ≥ 0.90 and p_lo ≥ 0.50 at BOTH refs. "Beat random" is banned.
•  Expectation written before submission: "comparable" is most likely; the extremes test (S1) can separate the methods.

**Notes:** Notes: P34 §0.1, §3.1–3.2; Sobol arm OFF (Kay 10-11; future TODO).
Sources: /Users/yilu/Documents/development/nd/research/admin/prompt/bogp/34-random-baseline.md; /Users/yilu/Documents/GitHub/RTS-GMLC/trial_0826/campaign/analysis/random_baseline/RANDOM_BASELINE.md

## Slide 15

Random baseline: primary result


BO campaign quality report · 2026-10-12

Left: /Users/yilu/Documents/GitHub/RTS-GMLC/trial_0826/campaign/analysis/random_baseline/figs/fig1_hv_band.png
Right: /Users/yilu/Documents/GitHub/RTS-GMLC/trial_0826/campaign/analysis/random_baseline/figs/fig2_percentile_hist.png

| Ref | BO HV/HV₀ | Random p10 / p50 / p90 | BO − median | p̂48 [interval] | Row |
| R_frozen | 1.0688 | 1.0158 / 1.0421 / 1.0651 | +0.027 | 0.94 [0.84, 1.00] | above |
| R_union | 1.0460 | 1.0083 / 1.0204 / 1.0311 | +0.026 | 1.00 [1.00, 1.00] | above |

BO's total HV gain (6.9 % of HV₀) is below the campaign's per-round noise bar (8 %). No HV result in this experiment can show BO ahead by more than that bar.

Expert review
R_union equals REF48 and mainly credits BO's corner picks. Its 1.00 restates the extremes result; do not count it as separate evidence. Lead with R_frozen.

**Notes:** Figures: /Users/yilu/Documents/GitHub/RTS-GMLC/trial_0826/campaign/analysis/random_baseline/figs/fig1_hv_band.png
/Users/yilu/Documents/GitHub/RTS-GMLC/trial_0826/campaign/analysis/random_baseline/figs/fig2_percentile_hist.png
Notes: R §2; statistics reviewer (expert review 10-12).
HOW TO READ THE TWO REFS. HV needs a reference point: the 'worst corner' of the box. A design that is worse than the ref on ANY objective earns zero HV. R_frozen = nadir of the 32 starts + 10 % span, fixed before round 1 (shed 15,102 MWh; curtailment 670,350 MWh; cost $652.0M). R_union = the same formula over all 96 designs (shed 32,100 MWh; curtailment 1,385,278 MWh; cost $684.3M); it equals BO_STAGE2's REF48. R_frozen leans toward random: 5 of BO's 16 picks are corner designs outside this box and earn zero. R_union leans toward BO: the bigger box credits those corners, so p-hat = 1.00 there mostly restates the S1 extremes result. Rule: 'above' only if above at BOTH refs. Lead with R_frozen. Each panel divides by its own HV0, so do not compare heights across the two panels (1.046 vs 1.069). Band = p10-p90 of random subsets (8-subsets at n = 40, 16-subsets at n = 48; 100,000 each).
Sources: /Users/yilu/Documents/GitHub/RTS-GMLC/trial_0826/campaign/analysis/random_baseline/RANDOM_BASELINE.md

## Slide 16

Robustness: the verdict is not robust, and the reason is the shed axis


BO campaign quality report · 2026-10-12

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

**Notes:** Notes: R §3; strategy-session check 10-12; statistics reviewer (expert review 10-12).
Sources: /Users/yilu/Documents/GitHub/RTS-GMLC/trial_0826/campaign/analysis/random_baseline/RANDOM_BASELINE.md

## Slide 17

Extremes (S1): BO's clearest advantage


Costs are g1-pending (option c adds +$28.188M to every design)

/Users/yilu/Documents/GitHub/RTS-GMLC/trial_0826/campaign/analysis/random_baseline/figs/fig3_s1_extremes.png

| Objective | BO best | Best of 48 random | BO ahead by > floor? |
| shed | 0 | 0 | no (tie) |
| curtailment | 48,444 MWh (r1#5) | 61,739 (rnd#15) | yes, 13.3 GWh |
| cost | $510.1M (r2#3) | $536.0M (rnd#42) | yes, $25.9M |

•  No random 16-batch came within a floor of either extreme.
•  Caveat: the cost extreme is a minimum-build corner, guessable from physics; S1 compares BO with uniform random, not with a heuristic.

**Notes:** Figure: /Users/yilu/Documents/GitHub/RTS-GMLC/trial_0826/campaign/analysis/random_baseline/figs/fig3_s1_extremes.png
Notes: R §4.2; power-systems reviewer (expert review 10-12).
Sources: /Users/yilu/Documents/GitHub/RTS-GMLC/trial_0826/campaign/analysis/random_baseline/RANDOM_BASELINE.md

## Slide 18

Grand front of 96 designs


BO campaign quality report · 2026-10-12

/Users/yilu/Documents/GitHub/RTS-GMLC/trial_0826/campaign/analysis/random_baseline/figs/fig4b_grand_front_unified.png

•  Same panels and markers as slide 10. Of the 13 starts on the 48-point front, 6 are now dominated by random designs; all 13 BO front designs stay.
•  32 designs on the 96-point front: BO 13 of 16 (81 %), random 12 of 48 (25 %), starts 7 of 32.
•  A random 16-batch puts 6.6 designs (p10–p90 5–8) on the front of starts ∪ batch. BO puts 13.
•  No random design dominates any BO design (set coverage 0.00).

**Notes:** Figure: /Users/yilu/Documents/GitHub/RTS-GMLC/trial_0826/campaign/analysis/random_baseline/figs/fig4b_grand_front_unified.png
Notes: R §4.3–4.4.
Sources: /Users/yilu/Documents/GitHub/RTS-GMLC/trial_0826/campaign/analysis/random_baseline/RANDOM_BASELINE.md

## Slide 19

The design recipe, revisited: two rules hold, two fail


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

Caveats

•  Designs within 0.03 of the knee distance include some with wind share < 0.5, so the share rule describes the knees, not the whole front.
•  ω = 0.05 is the lattice floor, so "nuclear at the floor" means "no nuclear retrofit" in practice.
•  r2#1 was already outside the old R at write time (a gap in the prompt-34 pre-submission check).

**Notes:** Notes: R §4.3 iii; power-systems reviewer (expert review 10-12).
Proposed paper wording (power-systems reviewer, verbatim):
"Every knee design, under either normalization, places the nuclear retrofit at its lattice minimum (ω = 0.05, 20 MW) and puts most of the PEM capacity (55–79%) on the two largest wind sites (buses 303 and 317). Total PEM capacity sets the position along the front, not membership of the knee region. Knees span 1.49–2.08 GW as the normalization changes. Over that range, cost rises about 5% while curtailment falls about 44%. The total therefore expresses a choice between curtailment and cost, not a recommended size."
Sources: /Users/yilu/Documents/GitHub/RTS-GMLC/trial_0826/campaign/analysis/random_baseline/RANDOM_BASELINE.md; /Users/yilu/Documents/GitHub/RTS-GMLC/trial_0826/campaign/analysis/bo_stage2/BO_STAGE2.md

## Slide 20

Claim scope: what the paper can and cannot say


BO campaign quality report · 2026-10-12

Can say

•  "An automated, pre-registered MOBO campaign on a real PCM terminated under its rule within budget."
•  "This BO run's HV exceeded 94 % of random 16-design batches (+0.027 HV₀, below our 8 % noise bar, sensitive to sub-floor load-shed differences). Its clearer distinction is reaching the cost and curtailment extremes, $26M and 13 GWh beyond any of 48 random designs."
•  Found designs are consistent with the LOCATION sensitivity structure (claim iii: supported).
•  The narrowed recipe (slide 19).

Cannot say

•  "beat random", "significant", "robust", any p-value
•  anything about q-ParEGO in general (one seed) or seed stability (claim ii: not shown)
•  "converged" (claim i: not shown)
•  anything vs Sobol or a heuristic; the R_union [1, 1] as certainty; the ~70 % model-world figure

**Notes:** Notes: B claim scope; ML §5.2; statistics reviewer (expert review 10-12).
Sources: /Users/yilu/Documents/GitHub/RTS-GMLC/trial_0826/campaign/analysis/bo_stage2/BO_STAGE2.md; /Users/yilu/Documents/development/nd/research/admin/prompt/bogp/math-log.md

## Slide 21


BLOCK 3

Roadblockers and open questions

Each open question needs an owner.

**Notes:** Block 3: roadblockers and open questions.

## Slide 22

Open questions (each needs an owner)


BO campaign quality report · 2026-10-12

| Item | Why it matters | Owner |
| Shed falls as PEM MW rises (Spearman −0.94) | Adding load should not reduce shed; reviewers will ask for the mechanism | Kay |
| Does true_curtailment net out PEM-absorbed energy at every site? | Otherwise wind-sited PEMs are credited twice | Kay (check the accounting) |
| 7 front designs share shed = 22.426 MWh | Likely one unavoidable event; "0 vs 22 MWh" is not a material difference | Kay |
| g1 ruling (NXT-D7) | Absolute costs shift by +$28.188M; rankings unchanged | PI |
| CRC chain submit defect | A future multi-round campaign needs the login-node fix | Kay approves |

**Notes:** Notes: power-systems reviewer (expert review 10-12); B open items.
Sources: /Users/yilu/Documents/GitHub/RTS-GMLC/trial_0826/campaign/analysis/bo_stage2/BO_STAGE2.md

## Slide 23


BLOCK 4

Decision points and TODO

Why a second BO seed is next, the the reviewed methods plan, the ERCOT data finding, and what I need today.

**Notes:** Block 4: decision points and TODO.

## Slide 24

Why a second BO seed is the next experiment


BO campaign quality report · 2026-10-12

•  The random baseline places THIS one BO run. It cannot tell if 0.94 was a good or a lucky run.
•  One acquisition seed controls the 8 Dirichlet weights per round, so a new seed sends BO to different designs from the same 32 starts.
•  A second seed tests: does p̂ stay high? Do the knees keep the same shape? Does BO reach the same extremes?
•  Cost: 16 runs ≈ 240 core-h, ≈ 2–3 days. The 48 random designs are reused as the reference; no new random runs.
•  Scope note: a new ACQUISITION seed keeps the 32 starts. Pre-registered claim (ii) says "≥ 3 init seeds"; a full init-seed replicate also needs new starts (+32 runs ≈ 480 core-h). Recommend: acquisition seeds first.
•  Optional add-on: one minimum-build heuristic design (1 run) to answer "the cost extreme is guessable".

**Notes:** Notes: statistics reviewer (expert review 10-12); ML §5.2.
Sources: /Users/yilu/Documents/development/nd/research/admin/prompt/bogp/math-log.md; /Users/yilu/Documents/GitHub/RTS-GMLC/trial_0826/campaign/analysis/random_baseline/RANDOM_BASELINE.md

## Slide 25

The methods claim: what reviewers will require (3-agent review, 10-12)


BO campaign quality report · 2026-10-12

| # | Requirement | Why | Cost |
| 1 | Stop-rule validation: early/late-stop rates and regret at stop on truth-known problems (replay A/B/C, synthetic functions with floor-matched noise, GP emulator of Stage 2); compare with existing BO stop rules | The stop rule is the most novel part of the workflow; today it has no operating characteristic | 0 PCM runs |
| 2 | Fixed-budget comparison: every arm to 32 + 4×8; apply the stop rule post hoc to the same trajectories | BO stops on its own rule, baselines have none — budgets differ | seed 1: +16 runs |
| 3 | q-ParEGO ≥ 3 replicates, ≥ 2 with NEW starts; qNEHVI ≥ 3 seeds paired by start set | Acquisition-only seeds share 2/3 of the data and understate variance; qNEHVI is the comparator reviewers expect | ≈ 3–4k core-h at C |
| 4 | Scenarios A and B as extra problem instances (cheapest: q-ParEGO + random) | One instance = a case study, not a methods result | ≈ 1–5k core-h each |
| 5 | D3 noise floors + a floor-robust metric, pre-registered before new runs | Today's differences sit below the floor | spec first |
| 6 | Emulator benchmark (≥ 20 seeds per method); calibration audit with a decision role | Cheap method-level statistics; the audit failed 2 of 3 objectives with no consequence | 0 PCM runs |

**Notes:** Contribution = the WORKFLOW (pre-registered, auditable, unattended MOBO with a noise-floor stop), for an applied-methods venue; not a new BO algorithm. Downgraded: Sobol to one continuation per start set (descriptive); knee-only re-runs. Dropped: ≥ 20 real Stage-2 seeds, lower-τ continuation, 5-batch Sobol, other weather years, GP-fix restart. Total ≈ 4k (C + cheapest A/B) to ~14k core-h (full arms). Living report §9.7.
Sources: /Users/yilu/Documents/development/nd/research/admin/prompt/bogp/math-log.md; /Users/yilu/Documents/development/nd/research/admin/prompt/bogp/living-report-multipem.md

## Slide 26

Execution order and calendar to AIChE (Nov 8)


BO campaign quality report · 2026-10-12

| Week | Work |
| W1 10-12 → 10-18 | ERCOT data fix (prompt 36 T0–T1) + base/replicate re-run; curtailment-netting check; qacct for the real per-run rate; qquota; ONE combined pre-registration (prompt 35); PI decisions incl. BoTorch install. Launch C replicates. |
| W2 10-19 → 10-25 | ERCOT screening_v2 on CRC; qNEHVI code + replay validation; stop-rule validation (0 PCM runs); D3 spec; AIChE workbook (prompt 31). |
| W3 10-26 → 11-01 | Analyse C replicates; ERCOT v2 figures. Freeze AIChE figures 11-01. |
| W4 11-02 → 11-08 | Talk only. |
| After AIChE | qNEHVI arms; scenarios A/B; emulator benchmark; D3 study; ERCOT BO on v2 data (paper placement decided after v2). |

•  CRC submission stays manual. One submit_ready.sh submits every ready round across all campaigns; Kay runs it once or twice a day.

**Notes:** Planner review 10-12. Shed-vs-PEM and the 22.4 MWh check gate the write-up, not compute. g1 does not gate compute (constant shift).
Sources: /Users/yilu/Documents/development/nd/research/admin/prompt/bogp/living-report-multipem.md; /Users/yilu/Documents/GitHub/RTS-GMLC/trial_0826/campaign/analysis/bo_stage2/BO_STAGE2.md

## Slide 27

Open questions: likely answers and cheap checks (domain review)


BO campaign quality report · 2026-10-12

| Question | Most likely answer | Cheap check |
| Does true_curtailment double-count PEM energy? | No — summarize_wave excludes *_PEM rows. But the withheld slice counts as H2 with no electrolyzer minimum load or efficiency | Per site-hour closure: available = dispatched + parent curtailment + withheld |
| Why does shed fall as PEM MW rises? | PEM adds no load. Wind priced at the bid makes thermal look cheaper in the RUC → more thermal committed → more headroom | Committed MW / headroom on shed hours, low- vs high-MW design; reserve shortfall must not rise (monitor it next to shed) |
| Why do 7 designs share shed = 22.426 MWh? | One PEM-independent shed event | Bus and hour of that shed |

**Notes:** Power-systems reviewer 10-12; parameters.py (renewable split), summarize_wave.py:113-116. Hypotheses until checked.
Sources: /Users/yilu/Documents/GitHub/RTS-GMLC/trial_0826/campaign/analysis/bo_stage2/BO_STAGE2.md

## Slide 28

ERCOT: the cost data are mis-converted. Every ERCOT output so far is invalid


BO campaign quality report · 2026-10-12

•  gen.csv HR_avg_0 = Csu · Pmax / fuel price on all 128 thermal units (checked to machine precision). It is a start-up energy in MMBTU, read by Egret as a heat rate in BTU/kWh.
•  HR_incr is a segment heat, read as a rate. Start-up heat = 1 MBTU and start cost = $1 on every unit.
•  Effect: no-load $2.1–2.6M per hour on nuclear (intended ≈ $14k); start-ups nearly free; marginal costs scaled by ΔP/1000, so the merit order is inverted (CT $2.9/MWh vs $43 intended).
•  gen-1 cycling, gen-93 never on, the ±$80M bimodality, TL=360, the rulers, screening, selection_t1: all artifacts or invalid.
•  Fix (prompt 36): find or rebuild the conversion from the TX-123BT paper; corrected data in a NEW versioned directory; regression test against Egret's parsed costs.
•  AIChE promises ERCOT results: re-run base + 2 replicates + screening on the corrected data before the 11-01 figure freeze. Old ERCOT figures are not shown.

**Notes:** Source: processing notebook gtep/123_bus_coal/ERCOT_BUS123_base_XC_editeddata/demo_processing_XC.ipynb. Correct mapping: HR_avg_0 = 1000·C(Pmin)/(fp·Pmin); HR_incr_k = 1000·(ΔC_k/ΔP_k)/fp; start cost = Csu·Pmax. Check GTEP 123-bus work from the same folder. Living report §9.8; TL360_VERDICT banner (ercot e844fa7).
Sources: /Users/yilu/Documents/development/nd/research/admin/prompt/bogp/living-report-multipem.md; /Users/yilu/Documents/development/nd/research/admin/prompt/bogp/math-log.md

## Slide 29

Decision points: what I need today


BO campaign quality report · 2026-10-12

D1

Approve the methods design (slide 25): fixed budget, ≥ 2 init-seed replicates, qNEHVI, scenarios A/B, stop-rule validation.

D2

Approve the BoTorch install for qNEHVI. CRC submission stays manual (batched submit_ready.sh).

D3

Approve the narrowed recipe (slide 19) and the claim-scope sentences (slide 20).

D4

ERCOT: fix the cost data (prompt 36) and re-run for AIChE; decide paper placement after the v2 results.

D5

g1 ruling (NXT-D7) — still open; it does not gate compute.

**Notes:** Decisions D1–D5 from OUTLINE.md slide 26. D1 → slide 24/25; D2 → slide 19; D3 → slide 20; D4 → slide 8; D5 → NXT-D7 (slide 22).
Sources: /Users/yilu/Documents/GitHub/RTS-GMLC/trial_0826/campaign/analysis/random_baseline/RANDOM_BASELINE.md; /Users/yilu/Documents/GitHub/RTS-GMLC/trial_0826/campaign/analysis/bo_stage2/BO_STAGE2.md; /Users/yilu/Documents/development/nd/research/admin/prompt/bogp/34-random-baseline.md

## Slide 30


BLOCK 5 · UPDATE 2026-10-13

Since 10-12: prompts 35, 36, 37

All three are on CRC. First ERCOT v2 results.

**Notes:** Block 5 was appended on 10-13. OUTLINE.md slides 30–33. Sources: /Users/yilu/Documents/development/nd/research/admin/prompt/bogp/living-report-multipem.md; /Users/yilu/Documents/development/nd/research/admin/prompt/bogp/PROGRESS.md

## Slide 31

Three prompts on CRC (status 10-13)


BO campaign quality report · update 2026-10-13

| Prompt | Question | CRC work | State 10-13 | Results |
| 35  Methods arms | Is q-ParEGO stable across replicates at a fixed budget of 64? Is one qNEHVI run consistent with it? | 7 arms: start sets S2, S3; Sobol continuations Q1–Q3; P1 rounds 3–4; qNEHVI N1 | Running since 10-12 21:00 (relaunch after an import failure) | First round ≈ 10-13; all ≈ 5 days |
| 36  ERCOT v2 | Re-run ERCOT on the corrected cost data for AIChE | A base ×3, B screening 19, C selection 9 | A + B landed 10-13 02:30; base read done. C: 2 of 9 failed; fixed (7c5fb8d); nuclear rows 6–11 rerun | C rerun ≈ 10-14; wave D ≈ 10-18/19 |
| 37  Stop rule | Does the stop rule work on problems with a known truth? | 1,540 tasks; 0 PCM runs | Running since 10-12 evening | ≈ 10-13 → 10-15 |

CRC order: 36 first (AIChE), then 35 and 37. Submission stays manual from the login node.

**Notes:** Sources: admin PROGRESS.md rows 1–10; LR 10-12u, 10-12v, 10-13a, 10-13b. 35 relaunch 8308211; 37 CRC gate f5e4c14.
Sources: /Users/yilu/Documents/development/nd/research/admin/prompt/bogp/PROGRESS.md; /Users/yilu/Documents/development/nd/research/admin/prompt/bogp/living-report-multipem.md

## Slide 32

ERCOT v2: first results (waves A and B)


BO campaign quality report · update 2026-10-13

ROADBLOCKER · wave C nuclear rows failed

DECISION · Kay: rerun nuclear rows 6–11

$8.09 B

base total cost, 2019 (raw Prescient)

0 MWh

load shed: base + all 19 screening rows

$21.08

mean price per MWh (base)

0

spread between the 3 base replicates

•  smoke_v2 matched the authors' SCUC within +6 % on 3 days (SMOKE_PASS 0a2acf2).
•  The 3 base replicates are byte-identical: the v1 replicate divergence (TL=360 Finding 1) does not occur on v2.
•  Load shed is 0 everywhere so far. On ERCOT the shed objective carries no signal.
•  Screening row 10 is an outlier (+$354M). Prescient's curtailment total counts PEM-withheld MWh; the analysis uses true curtailment.
•  Wave C: nuclear rows ω = 0.05 and 0.2875 failed at the first RUC build. The PEM patch raises p_min, but the T0 output stays at the original 729 MW. Fix (7c5fb8d): T0 output ≥ new p_min. A build-only test reproduces the error without the fix and passes 6/6 with it. All nuclear rows 6–11 are rerun, so that the ω sweep shares one T0.
•  Process: the wave-D site rule was committed after B landed, before any per-site value was read. Disclosed.

**Notes:** Numbers: ercot extracts base_2019_v2 (e3082fa) and screening_v2 (2ba803b), overall.csv; raw Prescient totals, objectives (true curtailment, cost less synthetic) not yet computed. Wave C failure: 02b147d, CRC log selection_t1_v2_array.o1533432.6 ('Generator 1 has less output at T0 than is feasible to ramp up to'). Same family as 1eaf05e (startup capacity). The thermal patch also sets ramp_up_60min = PEM capacity (ω × 2,430 MW), so the egret T0 check depends on ω. Old rows 6–11 are quarantined in runs/quarantine_T0_729, not deleted.
Sources: /Users/yilu/Documents/development/nd/research/admin/prompt/bogp/living-report-multipem.md; /Users/yilu/Documents/development/nd/research/admin/prompt/bogp/PROGRESS.md

## Slide 33

ERCOT v2 base read: what changed from v1


BO campaign quality report · update 2026-10-13

DECISION · confirm wave-D sizes 60/120/180 MW

| Quantity (2019, base) | v1 (mis-converted costs) | v2 (corrected) |
| Real-time LMP, mean | $14.5/MWh | $33.8/MWh |
| Fixed cost | $6.75 B | $3.63 B |
| Variable cost | $1.19 B | $4.46 B |
| True curtailment | 9.44 M MWh | 5.92 M MWh |
| Nuclear | gen-1 cycles (≈ 25 starts) | both units on all 8,760 h, 0 starts |
| RUC quality | TimeLimit races on capped days | 0 % capped; 1,460 / 1,460 OPTIMAL |
| Replicate spread (total cost) | ±$80M bimodal | 0 (4 runs byte-identical) |

•  Nuclear is baseload on v2. This informs NXT-D6.
•  Wave-D site rule (4fb3b1f, text unchanged): ruler = 0, so the top 6 by rank: sites 163, 140, 146, 270, 110, 274.
•  Smallest gen_pmax of the six: 185.4 MW.
•  Proposed sizes 60 / 120 / 180 MW (absolute, PI 10-08): 6 sites × 3 + nuclear × 3 = 21 rows.
•  On nuclear, 60 MW is ω ≈ 0.025. The nuclear rows compare against the sites; they do not sweep nuclear.

Next: Kay confirms the sizes → 36 builds wave D (21 full-year runs, ≈ 1–2 days on CRC) → AIChE figures 10-22 → 10-31.

**Notes:** T3 base read: ercot df61ab4 (ERCOT_COST_FIX.md). v1 replicate spread: screening bimodality ±$79.5M (3edd682) and TL=360 probe |Δ| $56–127M (c9d28cd). Top-k: 4fb3b1f (committed after B landed, before any per-site value was read; disclosed). Sizes are a proposal by the 36 session; pending Kay.
Sources: /Users/yilu/Documents/development/nd/research/admin/prompt/bogp/living-report-multipem.md; /Users/yilu/Documents/development/nd/research/admin/prompt/bogp/PROGRESS.md

## Slide 34

Methods track: prompts 35 and 37


BO campaign quality report · update 2026-10-13

35  Methods arms (scenario C)

•  G1 curtailment closure: PASS. G3: runs ≤ 9.4 h (random_C), BO rounds 16–22 h, acquisition 29 min.
•  BoTorch env built on CRC under /groups (home quota is full).
•  N1 replay gate: the two-sided test failed HIGH (qNEHVI median 0.9534 > q-ParEGO max 0.9518 at n = 24). Amended to one-sided (≥ q-ParEGO min) → PASS. Disclosed in the paper.
•  Launch 1 failed at import (PYTHONNOUSERSITE hid packages in ~/.local). Fixed; relaunched 21:00, the last allowed relaunch.

37  Stop-rule validation (truth known)

•  PREREG + Amendment 1: 400 local 6-D random runs quarantined; all 6-D work on CRC.
•  Truth files: sha256 verified on CRC. Random-number fingerprint identical on Mac and CRC envs.
•  1,540 tasks: q-ParEGO, qNEHVI and random on 2-D replay grids (method comparison) and 6-D emulator truths (stop-rule test).

CRC lessons (10-12/13)
Envs go under /groups. Test the real entry-path import, not a shallow import. A build-only check over the whole lattice catches patch bugs before a 7 h queue.

**Notes:** 35: d876321 (G1, G3), 1b17f42 (env), 35 §3.2 AMENDMENT 10-12 (N1 gate; paper register P13), 6480264 + 8308211 (import fix, relaunch). 37: 2d529ec (Amendment 1), f5e4c14 (CRC gate + fingerprint).
Sources: /Users/yilu/Documents/development/nd/research/admin/prompt/bogp/living-report-multipem.md; /Users/yilu/Documents/development/nd/research/admin/prompt/bogp/PROGRESS.md

