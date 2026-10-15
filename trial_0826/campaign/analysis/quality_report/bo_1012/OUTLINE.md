# bo_1012 — BO campaign quality report deck (PI-meeting style)

Authored 2026-10-12 in the strategy session. This file is the CONTENT
source of truth. The builder (`make_bo_1012_deck.py`) renders it with
`../../pi_1008/deck_lib.py` (ND template). Slide prose follows
ASD-STE100: short sentences, active voice, one idea per sentence. Every
number below is quoted from the source named in the slide's notes. Do
not add numbers that are not here or in those sources.

Organisation (same as pi_1008 v2): four blocks — PROGRESS / TECHNICAL
UPDATE / ROADBLOCKERS / DECISION POINTS + TODO. Technical slides that
touch a roadblocker get a RED badge, a decision a GREEN badge
(top-right), as in `pi_1008/v2/make_pi_1008_v2.py::add_badges`.

Sources (read-only):
- B = `campaign/analysis/bo_stage2/BO_STAGE2.md` (+ figs/, ROUND_LOG.md, t2_summary.json)
- R = `campaign/analysis/random_baseline/RANDOM_BASELINE.md` (+ figs/, t2_summary.json)
- P34 = `admin/prompt/bogp/34-random-baseline.md`; ML = `admin/prompt/bogp/math-log.md` §5
- LR = `admin/prompt/bogp/living-report-multipem.md` (rows 10-06 … 10-11c)
- Expert review 10-12 (strategy session; summarised in slide notes of 15, 18, 20)

Costs are g1-pending everywhere: footer on every cost slide.

---

## 1 [DIV] BO CAMPAIGN QUALITY REPORT · 2026-10-12
Sub: Stage-2 q-ParEGO on RTS-GMLC, scenario C — what ran, what it found,
what it does not show, and what comes next.

## 2 How this deck is organised
- Block 1 Progress: status and timeline.
- Block 2 Technical update: A setup, B BO result, C random baseline,
  D design recipe, E claim scope.
- Block 3 Roadblockers and open questions.
- Block 4 Decision points and TODO.
- One-line takeaway (boxed): "The automated campaign ran and stopped on
  its rule. This run's HV is above 94 % of random 16-design batches, but
  the lead is small and sensitive to load-shed differences. BO's clear
  advantage is the cost and curtailment extremes. The design recipe must
  narrow."

## 3 [DIV] BLOCK 1 · PROGRESS

## 4 Status: BO campaign complete, random baseline complete
Stat cards (number / label):
- 48 / designs evaluated by the campaign (32 Sobol starts + 2 BO rounds of 8)
- 26 / designs on the final 3-objective front (13 starts, 6 r1, 7 r2)
- +5.5 % → +1.4 % / HV gain per round, under the 8 % stop threshold → BO_DONE 10-10
- 48 / uniform random designs run as the baseline (10-11, 9.4 h wall)
- 0.94 / percentile of BO's HV among random 16-design batches (R_frozen)
- 0.83 / rounds per day (one 20 h stall: CRC compute nodes cannot submit jobs)
Notes: B status line, §2, pain log; R §2; LR 10-11c.

## 5 Timeline 09-19 → 10-12
Table (date | event):
- 09-19 → 09-22 | Stage-2 starts: 32 Sobol designs (n0 + n0b) run on CRC
- 10-06 | M = 3 approved: load shed, true curtailment, cost less synthetic
- 10-07 | Chain launched (block_1); 2 harness fixes first
- 10-08 | Round 1 results; acquisition WEDGED at qsub (compute node is no submit host)
- 10-09 | Round 2 submitted by hand from the login node (≈ 20 h lost)
- 10-10 | Round 2 results; stop rule fires → BO_DONE; BO_STAGE2.md written and reviewed
- 10-10 | Prompt 34 (random baseline) pre-registered, 3-agent review
- 10-11 | 48 random designs built, run (11:00 → 20:22), analysed (23:29)
- 10-12 | Expert review of the random-baseline result (statistics + power systems)

## 6 [DIV] BLOCK 2 · TECHNICAL UPDATE

## 7 Reproducibility card: the campaign configuration (frozen)
Two-column table:
- Design space | 6 tiers (nuclear, pv, tail, wind_122, wind_303, wind_317) × 9 lattice levels ω ∈ {0.05 … 1.0} = 531,441 designs
- Scenario | C: ρ = 2.0, B = $40/MWh
- Objectives (min) | load_shed_mwh, true_curtailment_mwh, total_cost_less_synthetic_usd
- Starts | 32 Sobol points (shared by every comparison)
- Acquisition | q-ParEGO, q = 8: 8 Dirichlet weights, EI, kriging believer, discrete lattice candidates
- HV reference (fixed before round 1) | nadir of the 32 starts + 10 % span; HV₀ = 6.606e17
- Stop rule | 2 consecutive rounds with gain < τ = 5.263e16 (8.0 % of HV₀; shed-floor-dominated, conservative)
- Software | bo-gp feat/qparego @ 60e6328; RTS runs are bit-reproducible
Notes: B header; prompt 30.

## 8 How the loop ran, and the one structural defect   [RED: CRC compute nodes cannot qsub]
Left: chain as a 4-box flow: array (8 Prescient runs) → collector (objectives, push) → acquisition (grade, propose, push) → submit next round.
Right bullets:
- Unattended hops worked: both collectors, both acquisitions (grade → propose → commit → push).
- The submit hop cannot work on CRC: compute nodes are not submit hosts.
- The WEDGED trap fired and left a clear record. Kay submitted round 2 by hand.
- r2 acquisition re-run on the Mac: weights and all 8 designs identical to CRC.
- Proposed fix (not implemented): submit the whole chain from the login node with -hold_jid; or a login-node cron watcher.
Notes: B pain log + audit table.

## 9 BO result: HV trajectory and the stop rule
Figure: bo_stage2/figs/fig2_hv_trajectory.png
Bullets:
- HV: 6.606e17 → 6.969e17 (+5.5 %) → 7.061e17 (+1.4 %).
- Both gains are under the 8 % bar → stop after round 2.
- The stop means "gains below a conservative noise bar". It does not mean "front converged".
- Sensitivity: with any bar below 5.5 %, round 3 would have run.
Notes: B §2.

## 10 BO result: the final front and its corners
Figure: bo_stage2/figs/fig1_front.png
Table "best in":
- Shed | 4 designs tie at 0; cheapest r2#6 $582M; r1#5 = 0 shed + lowest curtailment at $668M
- Curtailment | r1#5: 48 GWh, $668M (nuclear ω = 1.0)
- Cost | r2#3: $510M (all tiers 0.05 except tail 1.0; 29 GWh shed, 1.26 TWh curtailed)
Footer: costs g1-pending (+$28.188M constant under option c).
Notes: B §1.

## 11 Why the gains are small: dense front, not a box artifact
Bullets:
- 5 of 16 BO designs lie outside the fixed HV box. They earn zero HV by construction.
- With a wider box (nadir of all 48 + 10 %), the gains are 2.6 % and 2.0 %. Still small.
- The main cause is the dense front: 26 of 48 points are non-dominated.
- Stage-1 replay (2-D, scenario C): BO 0.813 → 0.899 → 0.941 vs random 0.807 → 0.885 → 0.923. BO led by a small margin. Stage 2 repeats that picture in 6-D.
Notes: B §2.

## 12 Calibration: the GPs are right for cost, not for shed and curtailment at corners   [RED: corner extrapolation]
Figure: bo_stage2/figs/fig3_calibration.png
Table: objective | r1 RMS(z) | r2 RMS(z) | pooled cov95 | verdict
- shed | 0.33 | 1.88 | 94 % | not calibrated
- curtailment | 0.55 | 2.49 | 88 % | not calibrated
- cost | 0.91 | 1.01 | 100 % | calibrated
Bullets: r1 too wide, r2 overconfident at corners (r2#3 shed 29.2k vs 8.5k predicted). Calibration was report-only; no gate was violated. Any restart: add corner points.
Notes: B §3.

## 13 Where BO went: outward to the edges
Figure: bo_stage2/figs/fig4_front_designs.png
Table: set | tiers at an edge (of 6) | fully interior: starts 0.75 / 44 %; r1 1.9 / 0 %; r2 3.25 / 0 %.
Bullets:
- Nuclear is bang-bang: 0.05 on the knees, 1.0 at the reliability corners. Spearman(nuclear MW, cost) = 0.89.
- wind_303 and wind_317 are loaded up on the front (mean ω 0.65 / 0.61).
- Tail goes to 1.0 in r2, but it correlates with nothing. Read it as EI pushing a flat direction, not a tail effect.
Notes: B §4.

## 14 Random baseline: why, and how it was pre-registered   [GREEN: Kay chose option (c), 10-10]
Bullets:
- Question: is this BO run better than random 16-design batches at the same budget?
- 48 uniform random lattice designs, never repeating the evaluated 48. One i.i.d. pool.
- Statistic: draw 100,000 random 16-subsets of the pool; p̂48 = fraction with HV below BO's.
- Interval: 1,000 pool bootstraps. Two refs: R_frozen (ledger) and R_union (all 96 points).
- Wording fixed before results: "above" needs p̂ ≥ 0.90 and p_lo ≥ 0.50 at BOTH refs. "Beat random" is banned.
- Expectation written before submission: "comparable" is most likely; the extremes test (S1) can separate the methods.
Notes: P34 §0.1, §3.1–3.2; Sobol arm OFF (Kay 10-11; future TODO).

## 15 Random baseline: primary result
Figures: random_baseline/figs/fig1_hv_band.png and fig2_percentile_hist.png (side by side)
Table: ref | BO HV/HV₀ | random p10 / p50 / p90 | BO − median | p̂48 [interval] | row
- R_frozen | 1.0688 | 1.0158 / 1.0421 / 1.0651 | +0.027 | 0.94 [0.84, 1.00] | above
- R_union | 1.0460 | 1.0083 / 1.0204 / 1.0311 | +0.026 | 1.00 [1.00, 1.00] | above
Boxed mandatory sentence: "BO's total HV gain (6.9 % of HV₀) is below the campaign's per-round noise bar (8 %). No HV result in this experiment can show BO ahead by more than that bar."
Bullet (expert review): R_union equals REF48 and mainly credits BO's corner picks. Its 1.00 restates the extremes result; do not count it as separate evidence. Lead with R_frozen.
Notes: R §2; statistics reviewer. Plus a "how to read the two refs" paragraph (box definitions, which way each ref leans, both-refs rule, separate HV₀ per panel).

## 16 Robustness: the verdict is not robust, and the reason is the shed axis   [RED: sensitivity to sub-floor shed differences]
Left (pre-registered): 1,000 perturbed draws (floors 3,000 MWh / 5,000 MWh / $0.5M). 467 above, 531 comparable, 2 matched. 0.467 < 0.8 → "not robust to floor-level output perturbation". The flag stays.
Right (POST-HOC, labelled): the shed floor (3,000 MWh) is 20 % of the R_frozen shed width (15,102 MWh). Without shed noise, 0.89 of draws keep "above"; clipping shed at 0 gives 0.48. RTS runs are deterministic, so this is a materiality stress test, not measurement noise.
Reading (box): "BO's percentile lead depends partly on load-shed differences smaller than 3,000 MWh." Also: p̂ = 0.94 sits only 0.04 above the 0.90 cutoff.
Notes: R §3; strategy-session check 10-12; statistics reviewer.

## 17 Extremes (S1): BO's clearest advantage
Figure: random_baseline/figs/fig3_s1_extremes.png
Table: objective | BO best | best of 48 random | BO ahead by > floor?
- shed | 0 | 0 | no (tie)
- curtailment | 48,444 MWh (r1#5) | 61,739 (rnd#15) | yes, 13.3 GWh
- cost | $510.1M (r2#3) | $536.0M (rnd#42) | yes, $25.9M
Bullets: no random 16-batch came within a floor of either extreme. Caveat: the cost extreme is a minimum-build corner, guessable from physics; S1 compares BO with uniform random, not with a heuristic.
Notes: R §4.2; power-systems reviewer.

## 18 Grand front of 96 designs
Figure: random_baseline/figs/fig4b_grand_front_unified.png
Bullets:
- Same panels and markers as slide 10. Of the 13 starts on the 48-point front, 6 are now dominated by random designs; all 13 BO front designs stay.
- 32 designs on the 96-point front: BO 13 of 16 (81 %), random 12 of 48 (25 %), starts 7 of 32.
- A random 16-batch puts 6.6 designs (p10–p90 5–8) on the front of starts ∪ batch. BO puts 13.
- No random design dominates any BO design (set coverage 0.00).
Notes: R §4.3–4.4.

## 19 The design recipe, revisited: two rules hold, two fail   [GREEN: approve the narrowed recipe wording]
Table of the six knees (normalization | knee | source | nuclear ω | total MW | wind_303+317 share | wind_122 ω | in old R):
- full | rnd#2 | random | 0.05 | 1,491 | 0.70 | 0.169 | no
- full | n0b#8 | start | 0.05 | 1,699 | 0.79 | 0.169 | yes
- full | r1#2 | BO | 0.05 | 1,705 | 0.68 | 0.288 | yes
- clipped | r2#1 | BO | 0.05 | 1,825 | 0.58 | 0.525 | no
- clipped | rnd#43 | random | 0.05 | 2,084 | 0.55 | 0.644 | no
- clipped | r1#2 | BO | 0.05 | 1,705 | 0.68 | 0.288 | yes
Holds: nuclear at 0.05; wind_303 + wind_317 share ≥ 0.5 (0.55–0.79).
Fails: the 1.6–2.0 GW band; the wind_122 cap (drop it).
Key point (box): total MW is the position along the front, not a size rule. Across 1.49 → 2.08 GW cost rises about 5 % and curtailment falls about 44 %. The size is a curtailment-vs-cost choice.
Caveats: designs within 0.03 of the knee distance include some with wind share < 0.5, so the share rule describes the knees, not the whole front. ω = 0.05 is the lattice floor, so "nuclear at the floor" means "no nuclear retrofit" in practice. r2#1 was already outside the old R at write time (a gap in the prompt-34 pre-submission check).
Notes: R §4.3 iii; power-systems reviewer (proposed paper wording in notes, verbatim).

## 20 Claim scope: what the paper can and cannot say
Two columns.
Can say:
- "An automated, pre-registered MOBO campaign on a real PCM terminated under its rule within budget."
- "This BO run's HV exceeded 94 % of random 16-design batches (+0.027 HV₀, below our 8 % noise bar, sensitive to sub-floor load-shed differences). Its clearer distinction is reaching the cost and curtailment extremes, $26M and 13 GWh beyond any of 48 random designs."
- Found designs are consistent with the LOCATION sensitivity structure (claim iii: supported).
- The narrowed recipe (slide 19).
Cannot say:
- "beat random", "significant", "robust", any p-value
- anything about q-ParEGO in general (one seed) or seed stability (claim ii: not shown)
- "converged" (claim i: not shown)
- anything vs Sobol or a heuristic; the R_union [1, 1] as certainty; the ~70 % model-world figure
Notes: B claim scope; ML §5.2; statistics reviewer.

## 21 [DIV] BLOCK 3 · ROADBLOCKERS AND OPEN QUESTIONS

## 22 Open questions (each needs an owner)
Table: item | why it matters | owner
- Shed falls as PEM MW rises (Spearman −0.94) | adding load should not reduce shed; reviewers will ask for the mechanism | Kay
- Does true_curtailment net out PEM-absorbed energy at every site? | otherwise wind-sited PEMs are credited twice | Kay (check the accounting)
- 7 front designs share shed = 22.426 MWh | likely one unavoidable event; "0 vs 22 MWh" is not a material difference | Kay
- g1 ruling (NXT-D7) | absolute costs shift by +$28.188M; rankings unchanged | PI
- CRC chain submit defect | a future multi-round campaign needs the login-node fix | Kay approves
Notes: power-systems reviewer; B open items.

## 23 [DIV] BLOCK 4 · DECISION POINTS AND TODO

## 24 Why a second BO seed is the next experiment
Bullets:
- The random baseline places THIS one BO run. It cannot tell if 0.94 was a good or a lucky run.
- One acquisition seed controls the 8 Dirichlet weights per round, so a new seed sends BO to different designs from the same 32 starts.
- A second seed tests: does p̂ stay high? Do the knees keep the same shape? Does BO reach the same extremes?
- Cost: 16 runs ≈ 240 core-h, ≈ 2–3 days. The 48 random designs are reused as the reference; no new random runs.
- Scope note: a new ACQUISITION seed keeps the 32 starts. Pre-registered claim (ii) says "≥ 3 init seeds"; a full init-seed replicate also needs new starts (+32 runs ≈ 480 core-h). Recommend: acquisition seeds first.
- Optional add-on: one minimum-build heuristic design (1 run) to answer "the cost extreme is guessable".
Notes: statistics reviewer; ML §5.2.

## 25 The methods claim: what reviewers will require   [GREEN]
## 26 Execution order and calendar to AIChE
## 27 Open questions: likely answers and cheap checks
## 28 ERCOT: the cost data are mis-converted; every ERCOT output is invalid   [RED]
(Rewritten 10-12 after the 3-agent review; text in make_bo_1012_deck.py and
SLIDE_TEXT.md; same content as living report §9.7–9.8.)

## 29 Decision points: what I need today
- D1: Approve prompt 35 — acquisition seeds (1 or 2 extra) and whether to add the minimum-build design.
- D2: Approve the narrowed recipe wording (slide 19).
- D3: Approve the claim-scope sentences (slide 20) for AIChE and the paper.
- D4: Approve the CRC chain fix design (slide 8).
- D5: g1 ruling (NXT-D7) — still open.
- D6: Approve the Stage-2 comparison design (q-ParEGO seeds, Sobol batches, second acquisition).

---

# BLOCK 5 · UPDATE 2026-10-13 (added after the deck; prompts 35 / 36 / 37)

Appended at the end so that slides 1–29 and their cross-references keep
their numbers. Sources: LR rows 10-12s … 10-13b; admin PROGRESS.md;
ercot commits e3082fa, 2ba803b, 02b147d; d6 commits d876321, 6480264,
8308211; stoprule commits 2d529ec, f5e4c14.

## 30 [DIV] BLOCK 5 · UPDATE 10-13
Sub: Since 10-12: prompts 35, 36 and 37 are on CRC. First ERCOT v2 results.

## 31 Three prompts on CRC (status 10-13)
Table: prompt | question | CRC work | state 10-13 | results expected
- 35 methods arms | Is q-ParEGO stable across replicates at a fixed budget of 64 designs? Is one qNEHVI run consistent with it? | 7 arms: new start sets S2, S3; Sobol continuations Q1–Q3; P1 rounds 3–4; qNEHVI N1 | running since 10-12 21:00 (relaunch after an import failure) | first round ≈ 10-13; all ≈ 5 days
- 36 ERCOT v2 | Re-run ERCOT on the corrected cost data for AIChE | A base ×3, B screening 19, C selection 9 | A + B landed 10-13 02:30; base read done; C: 2 of 9 failed, fixed (7c5fb8d), nuclear rows 6–11 rerun | C rerun ≈ 10-14; wave D ≈ 10-18/19
- 37 stop rule | Does the stop rule work on problems with a known truth? | 1,540 tasks, 0 PCM runs | running since 10-12 evening | ≈ 10-13 → 10-15

## 32 ERCOT v2: first results (waves A and B)   [RED: wave C nuclear rows failed] [GREEN: Kay chose rerun rows 6–11]
Cards: $8.09 B base total cost (2019, raw Prescient) · 0 MWh load shed (base + all 19 screening rows) · $21.08/MWh mean price · 0 spread between base replicates.
- smoke_v2 matched the authors' SCUC within +6 % (3 days); SMOKE_PASS 0a2acf2.
- The 3 base replicates are byte-identical. The v1 replicate divergence (TL=360 Finding 1) does not occur on v2 (to confirm from RUC logs).
- Load shed is 0 everywhere so far: on ERCOT the shed objective carries no signal.
- Screening row 10 is an outlier (+$354M). Prescient's curtailment total counts PEM-withheld MWh; use the true curtailment from compute_objectives.
- Wave C: nuclear rows ω = 0.05, 0.2875 failed at the first RUC build. The PEM patch raises p_min but leaves the T0 output at the original 729 MW (the patch also sets the ramp to the PEM capacity, so the check depends on ω). Fix 7c5fb8d: T0 output ≥ new p_min; a build-only test reproduces the error without the fix and passes 6/6 with it. All nuclear rows 6–11 are rerun so the ω sweep shares one T0.
- Process: the wave-D top-k rule was committed after B landed (before any per-site value was read); disclosed.

## 33 ERCOT v2 base read: what changed from v1   [GREEN: confirm wave-D sizes 60 / 120 / 180 MW]
Table v1 → v2 (df61ab4): RT LMP mean $14.5 → $33.8/MWh; fixed cost $6.75B → $3.63B; variable cost $1.19B → $4.46B; true curtailment 9.44M → 5.92M MWh; nuclear: gen-1 cycles (≈ 25 starts) → both units on 8,760 h, 0 starts; RUC: TimeLimit races → 0 % capped, 1,460/1,460 OPTIMAL; replicate spread: ±$80M bimodal → 0 (4 runs byte-identical).
- Nuclear is baseload on v2. This informs NXT-D6.
- Wave-D site rule (4fb3b1f, text unchanged): ruler = 0 → top 6 by rank: sites 163, 140, 146, 270, 110, 274. Smallest gen_pmax 185.4 MW.
- Proposed sizes 60 / 120 / 180 MW (absolute, PI 10-08): 6 sites × 3 + nuclear × 3 = 21 rows. On nuclear, 60 MW is ω ≈ 0.025 (below the lattice minimum); the nuclear rows compare against the sites, they do not sweep nuclear.

## 34 Methods track: prompts 35 and 37
Left (35):
- G1 curtailment closure PASS. G3: runs ≤ 9.4 h (random_C), BO rounds 16–22 h, acquisition 29 min.
- BoTorch env built on CRC under /groups (home quota is full).
- N1 replay gate: the two-sided test failed HIGH (qNEHVI median 0.9534 > q-ParEGO max 0.9518 at n = 24). Amended to one-sided (≥ q-ParEGO min) → PASS. Disclose in the paper (P13).
- Launch 1 failed at import (PYTHONNOUSERSITE hid packages in ~/.local). Fixed; relaunched 21:00 (the last allowed relaunch).
Right (37):
- PREREG + Amendment 1: 400 local 6-D random runs quarantined; 6-D work on CRC only.
- Truth files sha256 verified on CRC; random-number fingerprint identical on Mac and CRC envs.
- 1,540 tasks: q-ParEGO, qNEHVI, random on 2-D replay grids (method comparison) and 6-D emulator truths (stop-rule test).
Box: CRC lessons — envs go under /groups; test the real entry-path import; a build-only check over the whole lattice catches patch bugs before a 7 h queue.
