# bo_1013 — BO campaign + ERCOT v2 status deck (PI meeting, 2026-10-13)

Authored 2026-10-13 in the strategy session after two expert reviews
(methods referee + PI view; power systems). This file is the CONTENT
source of truth for `bo_1013.pptx`. `bo_1012.pptx` stays as the 10-12
record. Builder: `make_bo_1013_deck.py` (derived from
`make_bo_1012_deck.py`; same helpers, badges, footer style). ASD-STE100
prose. Every slide title is a claim sentence unless marked [TOPIC].
No section-divider slides. Footer: "BO campaign + ERCOT v2 · 2026-10-13".

Sources (shorthand as in OUTLINE.md): B, R, P34, ML, LR; plus
P35 = admin/prompt/bogp/35-stage2-methods-arms.md, P37 = 37-stop-rule-
validation.md, P38 = 38-rts-mechanism-checks.md, PROG = admin PROGRESS.md,
ERC = ercot repo origin/ercot/tx123 (ERCOT_COST_FIX.md df61ab4; extracts
base_2019_v2 e3082fa, screening_v2 2ba803b), RVM / RVP = expert reviews
10-13 (scratchpad review_methods.md / review_power.md; summarise in
notes, do not cite paths).

Slide numbers in [old N] point to bo_1012 slides whose code is reused.

---

## MAIN DECK

## 1 [TITLE] BO campaign + ERCOT v2: status and decisions, 2026-10-13
Sub: Stage-2 q-ParEGO on RTS-GMLC (scenario C), the methods arms now
running, and the first ERCOT results on corrected data.
Boxed "Three asks today":
1. Sign off the N1 gate amendment and the primary HV reference (slides 15–16).
2. Approve the redesigned ERCOT wave D (slide 22).
3. Decide: scenarios A/B before submission, or a scenario-C-only claim (slide 26).
Notes: deck rebuilt 10-13 from bo_1012 after two expert reviews.

## 2 What each claim needs, and where it stands
Table: Claim | Evidence (experiment) | Status 10-13 | What would weaken it
- W  Workflow: pre-registered, auditable MOBO on a real PCM stops on its rule | Stage-2 run (done) | supported; "unattended" only up to qsub | —
- S  The stop rule has a known operating characteristic | 37 (truth-known problems); 35 P1 r3–r4 (real data) | running | S0 acts as "stop after 2 rounds"
- ii Results are stable across replicates (start set + seed) | 35 S2, S3 vs P1 | running | P2/P3 below 0.8 percentile, or recipe at base rate
- iii Found designs follow the sensitivity structure (recipe) | Stage-2 + random baseline; 35 P2/P3 out-of-sample | in-sample only | recipe fails on P2/P3
- A  The workflow does not depend on the acquisition | 35 N1 (qNEHVI, 1 seed); 37 | running | N1 clearly better than q-ParEGO
- B  BO places above random; BO reaches the extremes | random baseline (done) | above at both refs, not robust; extremes clear | —
- T  The workflow transfers to another grid | ERCOT (36: screening + OAT only, no BO) | no experiment | —
- i  Convergence within budget | — | retired (not shown) | —
Bottom line (muted): Sobol continuations Q1–Q3 serve no claim (descriptive). Prompt 38 (mechanism) gates the shed axis for S, B and iii.

## 3 Three prompts run on CRC; prompt 38 is ready  [old 31, updated]
Table: Work | Question | CRC work | State 10-13 | Results
- Replicates + acquisition (35) | Is q-ParEGO stable across replicates at a fixed budget of 64? Is one qNEHVI run consistent with it? | 7 arms: start sets S2, S3; Sobol continuations Q1–Q3; P1 rounds 3–4; qNEHVI N1 | running since 10-12 21:00; this is the last allowed relaunch | first round ≈ 10-13; all ≈ 10-17 → 10-19
- ERCOT on corrected data (36) | Re-run ERCOT for AIChE | A base ×3, B screening 19, C selection 9 | A + B landed; base read done; C nuclear rows 6–11 rerun after a T0 fix | C ≈ 10-14; wave D after redesign
- Stop-rule validation (37) | Does the stop rule work on problems with a known truth? | 1,540 tasks, 0 PCM runs | running since 10-12 evening | ≈ 10-13 → 10-15
- Mechanism checks (38) | Why does shed fall as withheld MW rises? Why do 7 designs share 22.426 MWh? | 0 PCM runs (rsync of finished runs) | ready to hand off | ≈ 2 days after hand-off
Muted line: CRC order: ERCOT first. Submission stays manual from the login node.

## 4 Reproducibility card: the campaign configuration (frozen)  [old 7]
Same table. Add row: "GP training data | the 32 starts only (10 backfill rows: report-only sensitivity)".
Rename "Stop rule" row text: "… (8.0 % of HV₀; set by the shed materiality floor, conservative)".

## 5 The "PEM" is a $40 bid on renewable output, not an electrolyzer load  [NEW]
Left column "What the model does":
- Renewable site: the unit splits. The parent keeps availability minus the PEM capacity. A `_PEM` unit gets the rest and offers it at B = $40/MWh. Withheld MWh count as hydrogen (20 kg/MWh).
- Nuclear site: p_min rises to p_max − C; the band is priced at B; the unit stays committed every hour.
- The PEM sells to the grid when the price is above B. It adds no load.
Right column "What the model omits":
- No electrolyzer efficiency curve, minimum load, ramp limit or capex.
- No hydrogen revenue or storage.
- Cost objective = system cost minus the synthetic bid costs. This removes the nuclear unit's real fuel cost at any ω: a constant on RTS (the g1 item), a bias against the base case on ERCOT.
Boxed: "Every result in this deck is about priced withholding of renewable and nuclear output. Electrolyzer physics is future work."
Notes: parameters.py (renewable split, thermal patch), summarize_wave.py header note on synthetic cost; RVP §3.

## 6 The loop runs unattended except for qsub; CRC submission stays manual  [old 8]  [RED: CRC compute nodes cannot qsub]
Keep the chain drawing and bullets. Add bullet: "This limits claim W: 'unattended' holds up to job submission."

## 7 The stop rule fired at the earliest possible round: τ (8 %) is larger than BO's whole gain (6.9 %)  [old 9 + old 11]
Figure: hv_traj (left). Bullets (right):
- HV: 6.606e17 → 6.969e17 (+5.5 %) → 7.061e17 (+1.4 %). Both gains are under τ.
- 5 of 16 BO designs lie outside the fixed box and earn zero HV. With a wider box the gains are 2.6 % and 2.0 %.
- The front is dense: 26 of 48 points are non-dominated.
- The stop means "gains below a conservative materiality bar". It does not mean "converged".
- Prompt 37 tests this directly. Its pre-registered reading: if S0 matches "stop after 2 rounds", the paper says so and reports the τ at which the rule starts to adapt.

## 8 BO's front spans $510M with 29 GWh shed to zero shed at $582M  [old 10]
Same figure + table. Footer G1.

## 9 The calibration audit failed on 2 of 3 objectives and changed nothing  [old 12]  [RED: corner extrapolation]
Same table. Bullets: r1 too wide, r2 overconfident at corners (r2#3 shed 29.2k vs 8.5k predicted). The audit had no decision role. Prompt 37 tests whether the audit predicts error. Any restart: add corner points; consider shed as a constraint.

## 10 BO places at the 94th percentile of random 16-design batches; the lead is below τ  [old 14 + old 15]
Figures hv_band + pct_hist; table as old 15.
One line: "Design: 48 uniform random lattice designs; 100,000 random 16-subsets; 'above' needs p̂ ≥ 0.90 and p_lo ≥ 0.50 at both refs (pre-registered)."
Box: "R_frozen (fixed before round 1) is the honest primary. R_union credits BO's corner picks; its 1.00 restates the extremes result."
Notes: old 15 notes (two-ref reading).

## 11 The percentile lead depends on load-shed differences smaller than the floor  [old 16]  [RED]
Same. Change "materiality stress test" wording kept. Add one line: "Shed materiality is restated after prompt 38 (22.426 MWh plateau)."

## 12 BO's clearest result: both extremes lie beyond every random design  [old 17]
Same table. Bullets: no random 16-batch came within a floor of either extreme. Both extremes are corners. A minimum-build heuristic would likely find the cost corner; it was not run. The curtailment extreme puts the nuclear band at ω = 1.0: its hydrogen is nuclear energy, and gas replaces it.

## 13 The recipe narrows to two rules; prompt 35 tests them out of sample  [old 19]  [GREEN: approve the narrowed recipe wording]
Same table + boxes. Add to Caveats: "R′ was derived from P1; P2/P3 are the out-of-sample test."
Physics line: "A nuclear PEM diverts cheap baseload, so it never wins on cost."

## 14 Paper wording: what we can say now and what we cannot  [old 20]
Same two columns. Changes: "noise bar" → "materiality bar" everywhere. Add to Cannot say: "anything beyond scenario C (A/B not run)"; "reliability benefit of PEM (prompt 38 open)".

## 15 Pre-registered or post hoc: every deviation on one page  [NEW]
Table: Item | Pre-registered? | What changed | When | Disclosure
- Stop rule, τ, R_frozen | yes (prompt 30) | — | 10-06 | —
- M = 3 objectives | decided after the 32 starts landed | — | 10-06 | state in paper
- Random-baseline wording | yes (prompt 34) | — | 10-10 | —
- Primary reference for 35 = R_union | frozen 10-12, after R_union gave p̂ = 1.00 | lead reference changed from R_frozen | 10-12 | justify or make R_frozen co-primary (decision)
- Shed-noise diagnostic, recipe narrowing | post hoc | — | 10-12 | labelled post hoc
- N1 replay gate | yes (two-sided) | made one-sided after the result | 10-12 | P13 (next slide)
- 37 Amendment 1 | before results | 400 local 6-D random runs quarantined | 10-12 | PREREG amendment
- ERCOT smoke gate | amended before results | cost ±15 % vs authors' SCUC | 10-12 | ERCOT_COST_FIX
- ERCOT wave-D site rule | yes, text unchanged | committed after B landed, before any per-site value was read | 10-13 | CARRIED_OVER / T3
- 35 relaunch, software stack | — | ~/.local packages are part of the frozen stack | 10-12 | P14
Notes: RVM §3.2–3.3.

## 16 The N1 gate was changed after its result: three items to sign off  [NEW]  [GREEN: PI sign-off]
Left "What happened":
- Pre-registered gate (35 §3.2): qNEHVI replay median must lie INSIDE the q-ParEGO smoke range at n = 16 and 24.
- Result: n = 16: 0.9166, inside. n = 24: 0.9534, above the q-ParEGO maximum 0.9518. The gate failed HIGH.
- Amendment 10-12, after the result: one-sided (median ≥ q-ParEGO minimum) → PASS. N1 now runs.
Right "Sign off":
(a) Accept the amendment and its disclosure text (P13).
(b) N1 vs P1 is reported as "consistent with" at most: one seed; model, acquisition and noise handling change together.
(c) Fix now: if qNEHVI beats q-ParEGO on real runs by more than the P1–P3 spread, the paper reports both and keeps q-ParEGO as the workflow default because [reason to agree today: cost / simplicity / prior pre-registration].
Notes: P35 §3.2 AMENDMENT 10-12; replay_gate.json.

## 17 Prompt 35 decides claim (ii) by a fixed four-part rule  [NEW]
Bullets (from P35 §5):
- Claim (ii) holds only if ALL: (1) P1, P2, P3 each p̂48 ≥ 0.8 at R_union, raw and floor-robust HV; (2) HV range across P1–P3 at n = 64 ≤ 1 τ̄; (3) each replicate's top-3 knees satisfy R′ above the base rate; (4) curtailment extreme beyond the pool's best by > floor in ≥ 2 of 3.
- Reading fixed now: all pass → supported at C. P1 passes, P2/P3 fail → "one of three"; the result depends on the start set. All fail → not shown. The workflow claim stands in every case.
- Likely outcome (RVM): the AND-rule fails on at least one part. Plan the "one of three" wording now.
- P1 rounds 3–4 test the live stop on real data: any post-stop round > τ is an early stop.
- Sobol Q1–Q3: descriptive only.

## 18 Prompt 37 has one confirmatory test with fixed acceptance thresholds  [NEW]
Bullets (from P37 §4–5):
- Primary cell: emulator sample paths E-path-1…5 × q-ParEGO × live rule S0 (τ = 1·τ_j, w = 2, q = 8, cap 4), 50 seeds.
- Accept only if: early-stop rate ≤ 20 % AND median regret ≤ 1 τ AND S0 on or below the fixed-budget line S-fix-k, on the primary problems AND on the needle problem.
- Comparators: S-fix-1…8, relative-gain rule, model-based rule (qNEHVI), OCD-style test, oracle.
- Pre-registered reading: S0 ≡ S-fix-2 almost everywhere → "the rule acts as a 2-round budget at this τ".
- Limit: the emulators are fit on scenario-C data. They are not a second problem instance.

## 19 Two RTS mechanism questions gate the shed axis; prompt 38 answers them  [old 22 + old 27]
Table: Question | Most likely answer | Check (prompt 38)
- Why does shed fall as withheld MW rises (Spearman −0.94)? | H1: in the RUC the slice is a $40 resource, so more thermal is committed and real-time headroom grows. H2: the slice sells when the price exceeds B, so it delivers in scarcity hours. | Committed MW and headroom on shed hours, low- vs high-MW designs; shed hours vs price > B.
- Is shed traded for reserve shortfall (H4)? | Unknown | Reserve shortfall vs total MW over 96 designs. If yes, the shed axis, τ and HV need rework.
- Why do 7 front designs share shed = 22.426 MWh? | One PEM-independent event | Bus-hour of the shed; is it in the no-PEM base?
Muted line: Curtailment netting is closed: prompt 35 G1 closure PASS. Owner: hand off prompt 38 now (0 PCM runs).

## 20 ERCOT v2 runs clean at the system level; the fuel mix needs a check  [old 28 + old 33]
Table v1 → v2 (as bo_1012 slide 33) PLUS rows:
- Coal / gas share | — | 32 % / 34 % (2019 actual ≈ 20 % / 47 %, verify) |
- PV energy | — | 17.6 TWh from 8.3 GW (2019 actual ≈ 4–5 TWh, verify) |
Bullets (right):
- v1 used mis-converted cost data (start-up energy read as a heat rate); every v1 output is replaced.
- Corrected costs make nuclear baseload (informs NXT-D6).
- The coal-gas split sets the marginal unit and the cost of replacing withheld wind. Check fuel mix and fuel prices against the TX-123BT paper and 2019 data before the AIChE figures.
- Deterministic is not exact: the RUC still stops at ≤ 1 % gap (median 0.72 %). A bid-0 placebo row gives the real ruler.

## 21 ERCOT screening: relief is real, but a third of the "hydrogen" is diverted wind  [NEW]
Cards: "0 MWh shed (4 base + 19 screening runs)" · "$33.8/MWh mean RT LMP ($36.4 load-weighted)" · "0.61–0.67 MWh curtailment avoided per MWh H2 (top wind sites)" · "0.38 (PV site 30)".
Bullets:
- Shed is a checked constraint on ERCOT. Its span is zero, so any ERCOT BO uses two objectives: true curtailment and cost.
- B = $40 lies above the mean price and above coal, so the PEM withholds in most hours. 33–40 % of the withheld energy would have served load; thermal replaces it.
- Screening row 10 shows the mechanism: 15.7 TWh withheld, 3.75 TWh of it curtailment; about 12 TWh replaced by thermal → +$354M.
- Report curtailment avoided per MWh of hydrogen next to relief per MW.

## 22 Wave D needs contrast, a placebo and a nuclear cost fix  [NEW]  [GREEN: approve the redesigned wave D]
Left "As proposed (rule 4fb3b1f, ruler = 0 → top 6)": sites 163, 140, 146, 270, 110, 274 × 60/120/180 MW + nuclear × 3 = 21 rows. Problems: the six differ by 9 % in relief/MW and sit on 3 buses (120 ×3, 2 ×2, 75); 180 MW is 97 % of site 163's nameplate but 24 % of site 274's; nuclear rows carry the cost bias (slide 5).
Right "Redesign (21 rows)": 163, 140, 146 (best per bus) + PV 116, PV 30 + the last-ranked wind site, each × 60/120/180 MW; + one bid-0 placebo; + nuclear × 2 after the cost fix. Plot the nameplate fraction too.
Box: "The pre-registered rule stays on record. The redesign is a disclosed amendment: the rule selects similar sites, so it cannot show the location effect."
Notes: RVP §3. The 36 session builds after Kay approves.

## 23 What reviewers will require, and what is now running  [old 25 + status column]
Same table + column Status: 1 stop-rule validation → running (37); 2 fixed budget → running (35); 3 replicates + qNEHVI → partly running (2 new start sets, 1 qNEHVI seed); 4 scenarios A/B → no prompt (decision); 5 D3 floors → spec only; 6 emulator benchmark → running (37).

## 24 AIChE: one message, five figures, a fallback  [old 26 rebuilt]
Message (box): "An electrolyzer's grid value depends on where it sits: at congested wind buses it avoids about 0.6 MWh of curtailment per MWh of hydrogen; at solar or nuclear sites it avoids less at higher cost. Multi-objective BO maps these trade-offs in tens of production-cost runs."
Figures: (1) PEM-model schematic (slide 5); (2) RTS 96-design front (backup B3); (3) RTS knee composition (slide 13); (4) ERCOT relief/MW and Δcurt/H2 for all 16 sites + nuclear; (5) ERCOT size response with the placebo band.
Calendar table: 10-13 → 10-19: 35 lands; 37 lands; ERCOT C + fuel-mix check; wave D redesign submitted. 10-20 → 10-25: wave D lands; 38 done; figures drafted. 10-26 → 11-01: figures frozen 11-01. 11-02 → 11-08: talk.
Fallback: if 35 is late, figures 2–3 use the existing single run with its stated limits; if wave D is late, figure 5 is dropped.

## 25 (folded) — none

## 26 Decisions today
D1 Sign off the N1 amendment (a, b, c on slide 16).
D2 Primary HV reference for 35: keep R_union with a written justification, or make R_frozen co-primary.
D3 Scenarios A/B before submission, or a claim stated for scenario C only.
D4 Approve the redesigned wave D (+ placebo; nuclear after the cost fix).
D5 ERCOT fuel-mix check before the AIChE figures (owner: 36 session).
D6 Hand off prompt 38 now.
D7 g1 ruling (NXT-D7) still open; ERCOT nuclear rows have the same accounting issue.
Notes: D1/D2 of bo_1012 (methods design, BoTorch) were approved 10-12 (NXT-D9).

---

## BACKUP (header slide "Backup" allowed: one divider only)

B1 Timeline 09-19 → 10-13 [old 5 + rows: 10-12 prompts 35/36/37 written, launched; 10-13 ERCOT A+B landed, base read]
B2 BO moves to the lattice edges; nuclear leaves the floor only at the reliability corners [old 13]
B3 Grand front of 96 designs [old 18]
B4 Status card 10-12 [old 4]
B5 ERCOT wave C: nuclear rows failed on the T0 output; fixed and rerun [from bo_1012 slide 32 wave-C bullet + notes]
B6 ERCOT v1: the cost data were mis-converted [old 28 bullets]
B7 Operations 10-12/13: env under /groups, import failure + relaunch, 37 fingerprint, CRC lessons [bo_1012 slide 34 minus the N1 bullet]
