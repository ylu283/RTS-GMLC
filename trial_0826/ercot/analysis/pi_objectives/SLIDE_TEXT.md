# ercot_objectives.pptx — slide text, source line and speaker notes

## Slide 1

**Source line:** Source: waves/{location_oat_v2,n0_E,location_contrast_E,noise_seed_E,screening_v3}/design_matrix.csv; git rev-parse ercot/tx123

ERCOT TX-123BT · OBJECTIVE SELECTION (E-D1b) · 2026-11-18

Choosing the ERCOT objectives: three seats are firm, one is a PI choice

identity v3 · wave D 21 runs · n0_E 48 · location contrast 9 · Seed replicates 18 · screening_v3 11 (landed and read)
Kay Lu · branch ercot/tx123 @ baf77c3

**Notes:** Source: waves/{location_oat_v2,n0_E,location_contrast_E,noise_seed_E,screening_v3}/design_matrix.csv; git rev-parse ercot/tx123. The screening_v3 read (analysis/pool/SCREENING_V3.md, e58f4bd) landed before the build, so the subtitle says 'landed and read' (prompt 64 fallback text 'analysis pending' replaced).

## Slide 2

**Source line:** Source: analysis/pool/pool_n0E_standings.csv, POOL_N0E_STANDINGS.md · plan amendment 11-06, 11-17

The question: which three or four objectives should the ERCOT BO optimize, and is the evidence strong enough to launch?


•  The pool
•  28 graded candidates plus the D3 check, frozen at f76d897, in five seat families:
–  V = curtailment · E = cost · X = CO₂ · R = reliability (starts, reserve) · N = network congestion.
•  The rule
•  At most 4 seats. At most one seat per family. Family order V < E < X < R < N.
•  A seat needs a candidate that RESPONDS on the BO's own design space.
•  A seat candidate must not be a copy of a higher-priority candidate.
•  The two questions for today
•  1. Which candidate takes each seat?
•  2. Is the evidence strong enough to launch the BO?

**Notes:** Source: analysis/pool/pool_n0E_standings.csv, POOL_N0E_STANDINGS.md · plan amendment 11-06, 11-17. Pool size: 28 rows in pool_n0E_standings.csv; D3 = check only (POOL_N0E_STANDINGS.md §3). Rule: plan AMENDMENT 2026-11-06 (≤ 4, one per family, V < E < X < R < N) and 2026-11-17 (RESPONDS IN BOX, REDUNDANT, seat walk R-4).

## Slide 3

**Source line:** Source: pool_ed1b_combined(_seedbar).csv, ercot_noise_seed.csv, pi-agenda · plan amendment 11-17, 11-18

Proposal: optimize curtailment (V1), cost (E1) and congestion (N1 or N4); leave the reliability seat empty (M = 3)


| Seat | Candidate | IDR / perturbed bar | IDR / Seed bar | Read |
| V | V1 true curtailment | 93× | 81× | firm |
| E | E1 total cost | 14× | 25× | firm |
| R | R4 thermal starts | 2.1× | 1.1× | noise-level → seat EMPTY |
| N | N1 congested line-hours (system) | 6.4× | 3.05× (binding) | PI choice |
| N | N4 line-hours ≥ 99 % on L252 (pocket) | 17.4× | 14.4× | PI choice |

•  V1 and E1 are firm: their response is far above both noise bars.
•  R4 is at noise level (2.1× the perturbed bar, 1.1× the Seed bar). The R seat stays EMPTY.
•  The N seat is the choice. N1 reads all lines: 6.4× perturbed, 3.05× on its binding Seed bar. N4 reads the pocket line L252: 17.4× / 14.4×.
•  Precedent: the RTS campaign ran with M = 3 (shed, curtailment, cost-less-synthetic). Reserve and starts were dropped on 10-06 after the drop-one test (Pareto overlap 0.988; τ 0.86–0.91 vs shed).

**Notes:** Source: pool_ed1b_combined(_seedbar).csv, ercot_noise_seed.csv, pi-agenda · plan amendment 11-17, 11-18. IDR / bar = pool_n0E_standings.csv IDR over B_j (perturbed) and over ercot_noise_seed.csv B_seed; N1's binding bar is B_seed (63 A3 DISAGREE) per pool_ed1b_combined_seedbar.csv (IDR_over_B 3.052). RTS precedent: pi-agenda row 2026-10-06 (M approved), INDEX row 28 (M = 3 APPROVED), memory project_bogp_multipem (overlap 0.988, τ 0.86–0.91).

## Slide 4

**Source line:** Source: waves/{location_oat_v2,n0_E}/design_matrix.csv, cost_fix/wave_d_selection.json · plan amendment 11-06b

Why the earlier evidence was not enough: wave D moves one site at ≤ 180 MW; the BO moves six sites at 679–1,863 MW


Total PEM MW per row. Wave D: 21 rows (6 WIND sites × 60 / 120 / 180 MW + nuclear gen 1 × 3). n0_E: 48 Sobol rows, six sites in every row, 678.8–1,862.6 MW.
/Users/yilu/Documents/GitHub/RTS-GMLC-e64/trial_0826/ercot/analysis/pi_objectives/figs/fig_envelope_total_mw.png

•  The two populations do not overlap. A read on wave D does not transfer to the BO box by itself.
•  The slate itself was chosen on V1 alone: relief per MW at ω = 0.5 (screening_v2), under identity v2.

**Notes:** Source: waves/{location_oat_v2,n0_E}/design_matrix.csv, cost_fix/wave_d_selection.json · plan amendment 11-06b. wave_d_selection.json: the 6 chosen rows have pem_mw / gen_pmax = 0.5 and are ranked by relief_per_mw. Plan AMENDMENT 2026-11-06b: the 31 v2-identity runs remain slate evidence only.

## Slide 5

**Source line:** Source: POOL_N0E_STANDINGS.md (block sha256 8dd06917…) · plan amendment 11-17

The seat rules were frozen before any n0_E statistic was computed (ideal, nadir and R had been seen; disclosed)


Notes
BORDERLINE: IDR / B_j in [2, 3). No seat may rest on it alone.
B_j excludes the D2 structural-zero pairs.
One B:8 delta used a 0.2 % step. It is kept and flagged.
The seat walk allows M < 4. M ≠ 4 reopens the plan §6.4 gate numbers.
Disclosed: ideal / nadir / R over the 48 rows were seen before the rules.

A candidate responds if its middle-80 % spread over the 48 designs is at least twice the noise bar.
Two candidates are copies if they rank the designs the same way both before and after the total-MW trend is removed.

**Notes:** Source: POOL_N0E_STANDINGS.md (block sha256 8dd06917…) · plan amendment 11-17. Equations in math font: /Users/yilu/Documents/GitHub/RTS-GMLC-e64/trial_0826/ercot/analysis/pi_objectives/figs/eq_seat_rules.png (make_objective_figs.py, mathtext). Block sha256 8dd06917415c8cf6e8f7081adcee862e3d2ae6d08cf4eaa8dc0a9fa2cc8a1d1e as printed in POOL_N0E_STANDINGS.md. B:8 step: ercot_noise_daily_divergence.csv delta_rel 0.002; ERCOT_NOISE.md §10 flag.

## Slide 6

**Source line:** Source: ERCOT_NOISE.md §10–11, ercot_noise_daily_divergence.csv, NOISE_SEED_E.md §2/§4 · plan amendment 11-18

The ruler: the run repeats bit-for-bit at fixed Threads and platform, but a 0.1 % input change moves 350–365 of 365 RUC days; Seed replicates agree with that ruler within 2× on 20 of 22 candidates


•  Perturbed copies (noise_v3)
•  Divergent RUC days per pair: 350 / 357 / 365 / 354 / 358 / 365. The 4 exact pairs: 0.
•  B_j is 2.84–10.28× the old median ruler (current ruler); 3.93–13.27× vs the 11-16 ruler.
•  The D2 pairs were structural zeros: site 206 wind max 895.48 MW < PEM 899.0 / 900.8 MW. They are excluded.
•  Seed replicates (noise_seed_E)
•  τ_exact = 0 stays. τ_res = 1.96e+18 = 0.128 HV₀ (PROVISIONAL, 4 designs).
•  Threads 8 / 1 are not bit-identical to Threads 4 (304 / 364 days differ). This is confounded with the node.

| id | σ̂_c (Seed, df 16) | ratio σ̂_c√2 / σ̂_pert | A3 | B^seed | B_j (pert.) |
| V1 | 4,376 MWh | 1.15× | AGREE | 18,567 | 16,173 |
| E1 | $312.4k | 0.56× | AGREE | $1.325M | $2.383M |
| R4 | 65.1 | 1.88× | AGREE | 276.1 | 146.7 |
| N1 | 57.1 | 2.11× | DISAGREE | 242.1 | 114.9 |
| N4 | 10.5 | 1.20× | AGREE | 44.5 | 37.0 |

Read
AGREE iff the ratio is in [0.5, 2]. Then both bars measure the same chatter.
N1 is 2.11× → DISAGREE. Its perturbed ruler is 'perturbation response, not chatter'. Its bar becomes B^seed = 242.1.
The other DISAGREE id is E9 (its perturbed ruler is 0).

**Notes:** Source: ERCOT_NOISE.md §10–11, ercot_noise_daily_divergence.csv, NOISE_SEED_E.md §2/§4 · plan amendment 11-18. Days: ercot_noise_daily_divergence.csv n_divergent (non-structural perturbed pairs, A then B). B_j / ruler spans: computed from pool_n0E_standings.csv B_j over ercot_noise.json ruler (2.84–10.28, as POOL_N0E_STANDINGS.md §2) and over ercot_noise_2026-11-16.json ruler (3.93–13.27, as PROGRESS prompt 62). Site 206 / PEM MW: ERCOT_NOISE.md §10 table. Table: ercot_noise_seed.csv. τ: ercot_noise_seed.json tau_res. Threads: ercot_noise_seed.json thread_check.

## Slide 7

**Source line:** Source: pool_n0E_standings.csv, pool_ed1b_combined_seedbar.csv, ercot_noise_seed.csv · plan amendment 11-18

On the BO's own space, V1 and E1 respond 93× and 14× the bar; N4 17× (14× Seed); N1 6.4× perturbed but 3.05× on its Seed bar; R4 2.1× (1.1× Seed)


/Users/yilu/Documents/GitHub/RTS-GMLC-e64/trial_0826/ercot/analysis/pi_objectives/figs/fig_hero_idr_over_bar.png

The BORDERLINE band is [2, 3). N1's Seed value is 738.8 / 242.1 = 3.05: 0.05 above the band. Open markers: the five named ids and the A3-DISAGREE ids.

**Notes:** Source: pool_n0E_standings.csv, pool_ed1b_combined_seedbar.csv, ercot_noise_seed.csv · plan amendment 11-18. Figure /Users/yilu/Documents/GitHub/RTS-GMLC-e64/trial_0826/ercot/analysis/pi_objectives/figs/fig_hero_idr_over_bar.png (make_objective_figs.py fig_hero): filled = IDR / B_j (pool_n0E_standings.csv); open = IDR / B^seed (pool_ed1b_combined_seedbar.csv IDR_over_B_seed_sensitivity, asserted equal to IDR / ercot_noise_seed.csv B_seed). The formal Seed-bar re-grade landed (baf77c3, POOL_N0E_STANDINGS_seedbar.md): no seat changes; E9 becomes NOT RESPONDS (0 on the log axis).

## Slide 8

**Source line:** Source: pool_spearman_n0E_{raw,resid}.csv, POOL_N0E_STANDINGS.md §3–§4 · plan amendment 11-17

Redundancy after removing the total-MW trend: CO₂ collapses into cost, penetration into consumer payments; N4 is not a copy of N1


T-residual oriented ρ (n = 48), complete linkage; green boxes = REDUNDANT pairs.
/Users/yilu/Documents/GitHub/RTS-GMLC-e64/trial_0826/ercot/analysis/pool/figs/n0E/n0E_clustermap_resid.png

•  Copies (REDUNDANT: raw ≥ 0.90 and residual ≥ 0.50)
•  X1–E1: raw 0.982, residual 0.968 → X1 is a copy of E1.
•  V2 → E4 (total payments). N5 → E4. E2 → E1. E6 → V1.
•  Not a copy
•  N4–N1: raw 0.950, residual 0.394 → SIZE-CO-MONOTONE, not redundant.
•  What each N candidate carries
•  N1 tracks size: raw ρ with V1 0.95; composition ρ -0.03.
•  N4 carries composition (ρ 0.27) and a location trade-off against cost (residual ρ with E1 -0.81).

**Notes:** Source: pool_spearman_n0E_{raw,resid}.csv, POOL_N0E_STANDINGS.md §3–§4 · plan amendment 11-17. Figure /Users/yilu/Documents/GitHub/RTS-GMLC-e64/trial_0826/ercot/analysis/pool/figs/n0E/n0E_clustermap_resid.png (prompt 62 Part B, pool_n0E.py). ρ values: pool_spearman_n0E_raw.csv / _resid.csv (symmetric cells). Clusters: POOL_N0E_STANDINGS.md §4 (n0E-C1 {E6, V1} → V1; C2 {E1, E2, X1} → E1; C3 {E4, N5, V2} → E4). Composition ρ: pool_n0E_standings.csv comp_rho.

## Slide 9

**Source line:** Source: POOL_N0E_STANDINGS.md §E, pool_ed1b_combined.csv · plan amendment 11-17

Result of the pre-registered walk: V1, E1 and N1 seated, R seat empty (M = 3); N4 stands further above its bar but ranks behind N1 in the frozen order


| id | global order | IDR / B_j | status | reason |
| V1 | 1 | 93.28 | OBJECTIVE | seat V: first eligible in global_order |
| E1 | 2 | 14.05 | OBJECTIVE | seat E: plan §1.2 final (E1) |
| X1 | 3 | 27.40 | REDUNDANT->E1 | REDUNDANT->E1 on n0_E (n0E-C2) |
| R4 | 4 | 2.11 | DIAGNOSTIC | BORDERLINE-only response (IDR/B_j in [2, 3), no wave-D backing) |
| R2 | 7 | 0.75 | GUARDRAIL | guardrail (plan §1.3); never seated |
| R5 | 12 | 0.89 | DIAGNOSTIC | NOT RESPONDS (n0_E) |
| R6 | 15 | 0.81 | DIAGNOSTIC | NOT RESPONDS (n0_E) |
| R7 / R8 | 8 | 4.40 | DIAGNOSTIC | dir '-': shown, never clustered or seated (R8 the same) |
| N1 | 5 | 6.43 | OBJECTIVE | seat N: first eligible in global_order |
| N4 | 9 | 17.38 | SIZE-CO-MONOTONE (with V1, N1) | family N seat held by N1 (earlier in global_order) |

•  R family: R4 is BORDERLINE-only. R5 / R6 do not respond. R2 is a guardrail. R7 / R8 are undirected. No R candidate is eligible.
•  Disclosure: the first execution printed M = 2 from a seat-walk code defect. The fix (82bb71d) restored the registered rule before any output was committed.

**Notes:** Source: POOL_N0E_STANDINGS.md §E, pool_ed1b_combined.csv · plan amendment 11-17. Table rows: pool_ed1b_combined.csv (global_order, IDR_over_B, status, reason). Under the Seed-bar re-grade (pool_ed1b_combined_seedbar.csv) the seats are the same: V1, E1, N1. Fix: POOL_N0E_STANDINGS.md Deviations; commit 82bb71d.

## Slide 10

**Source line:** Source: location_contrast_E.csv, LOCATION_CONTRAST_E.md §3–§5, §7 · plan amendment 11-17c

Location contrast (9 runs): relief is additive within 10 % at 60 and 120 MW per site and sub-additive at 180 (g = 0.12); at matched total MW the bus-120 sites relieve 2.9–6.7 bars more than host energy predicts — a size consistent with wind-profile differences, no network effect claimed (one PTDF on L252)


/Users/yilu/Documents/GitHub/RTS-GMLC-e64/trial_0826/ercot/analysis/pi_objectives/figs/fig_relief_vs_total_mw.png

| MW / site | g | g predicted | read |
| 60 | 0.038 | 0.07 | WITHIN 10 % |
| 120 | 0.073 | 0.12 | WITHIN 10 % |
| 180 | 0.123 | 0.18 | SUB-ADDITIVE |

•  Raw V1 location contrast: -23.0 B at 800 MW (b120 vs b275); -2.8 B at 500 MW (matched-u).
•  H_C residuals over the four pairs: +3.0 / +6.7 / +6.4 / +2.9 B. The pre-registered label LOCATION EFFECT means 'not explained by H_C'.
•  The physics prediction was contradicted on 7 of 8 reads. 'Wind profile' is interpretation.
•  At 1,500 MW the retrofit relieves 83 % of the 4.87 TWh behind-cut pool (4.03 TWh).
•  Relief per MWh of host-absorbable energy falls from 0.79 (800 MW pro-rata) to 0.730. The last 700 MW add 1.51 TWh.

**Notes:** Source: location_contrast_E.csv, LOCATION_CONTRAST_E.md §3–§5, §7 · plan amendment 11-17c. g: location_contrast_E.csv kind V1_g / V1_g_pred; raw: loc_raw (ratio); residuals: loc_resid V1 (ratio) for pairs 4–5, 7–8, 4–6, 5–6; prediction row 'no residual location effect' = 7 of 8 loc_resid reads; saturation rows. Figure /Users/yilu/Documents/GitHub/RTS-GMLC-e64/trial_0826/ercot/analysis/pi_objectives/figs/fig_relief_vs_total_mw.png (make_objective_figs.py fig_relief; asserts ΣOAT and g against the csv). Interpretation: LOCATION_CONTRAST_E.md §7.

## Slide 11

**Source line:** Source: pi-agenda E-D1b (11-17/18), NOISE_SEED_E.md §5, SCREENING_V3.md · plan amendment 11-16, 11-17b, 11-18

Decide today (E-D1b). Strategy recommends A′.


A — V1 · E1 · N1 (M = 3): the pre-registered walk.
N1 is 3.05× its Seed bar, 0.05 above BORDERLINE. It mostly repeats the size axis that V1 already gives. Risk: BO budget spent on chatter in N1.

A′ — V1 · E1 · N4 (M = 3): a recorded rule change.  RECOMMENDED
N4 is 14–17× its bar and is the only N candidate with a location trade-off against cost. Risk: N4 reads one line (L252). The 16-site screening finds N4 locational ERCOT-wide (-2.7 B, Holm p 0.047) and N1 not (-3.0 B, Holm p 0.65).

C — add R4 (M = 4). Not recommended.
R4 is 2.1× the perturbed bar and 1.1× the Seed bar.

After either M = 3 choice
1. Re-derive the plan §6.4 C2 / C3 false-alarm numbers for M = 3 (strategy session, zero-sim).
2. E-D7: nav set = the first 32 or all 48 Sobol rows.
3. 54 GP fit → 55 Part B → launch.
Launch risk
Longest RUC solve: 860.7 s (noise_v3) and 1,157 s (random_E:22, incl. model build). The limit is 1,200 s: margin 1.4× / 4 %.

Cost of a wrong N choice
Before launch: no run is repeated; the objectives are re-graded from the stored runs. After launch: a new vector changes R (§6.3) and with it every HV in the ledger. Plan §10 keeps the ref rule and the gate numbers immutable.

**Notes:** Source: pi-agenda E-D1b (11-17/18), NOISE_SEED_E.md §5, SCREENING_V3.md · plan amendment 11-16, 11-17b, 11-18. A / A′ / C: pi-agenda row 2026-11-17 E-D1b with the 11-18 update. N1 / N4 / R4 ratios: slide 3 sources. Screening line: analysis/pool/screening_v3_locational.csv (HL_over_B, p_holm; N1 NOT LOCATIONAL under both bars, Moses interval contains 0). §6.4 reopening: pi-agenda row ('M ≠ 4 reopens plan §6.4 gate numbers'). E-D7: NOISE_SEED_E.md §5. RUC solves: ercot_noise.json determinism_conditions (860.7 s), plan AMENDMENT 2026-11-16 (1,157 s, ≈ 4 %), 2026-11-17b (≈ 1.4×). Cost of a wrong choice: plan §6.3 (R over the grading tier), §10 (immutable rules). The '< 1 day' estimate in prompt 64 is not in any file (not printed).

## Slide 12

**Source line:** Source: POOL_N0E_STANDINGS, ERCOT_NOISE §12, SCREENING_V3.md, LOCATION_CONTRAST_E.md · plan amendment 11-16…18

Discussion: what this shows and does not show; next


•  (i) Selection used the initial design at pool level. No selection script read random_E. The strategy session saw all 96 landed values when it computed R (disclosed, plan 11-16). Holdout exposure: 0 / 24.
•  (ii) The bar is transferred from single-site designs. Seed chatter confirms it for 20 / 22; N1 is the exception.
•  (iii) N1 = system-wide line-hours (chatter-limited at single sites). N4 = the physical pocket read.
•  (iv) Location on this slate = composition plus a residual consistent with wind profile. ERCOT-wide, the 16-site screening (landed) finds V1, E1 and N4 locational (-33.1 / -8.7 / -2.7 B) and N1 not (-3.0 B; -1.43 B on the Seed bar).
•  (v) Gurobi 13.0.2 is logged from noise_seed_E on. For earlier waves it is not discoverable (env records 11.0.2 vs 13.0.2).
•  (vi) The seat-walk defect is disclosed (slide 9).
•  Next
•  Dated design_space_E.json (to do: M = 3, R2 flag 312 MWh) → 54 fit + E-D7 → 55 Part B → 56 launch (option C).
•  Paper sentence: fixed in LOCATION_CONTRAST_E.md §8.

**Notes:** Source: POOL_N0E_STANDINGS, ERCOT_NOISE §12, SCREENING_V3.md, LOCATION_CONTRAST_E.md · plan amendment 11-16…18. (i) POOL_N0E_STANDINGS.md header (random_E not read; holdout 0 of 24), plan AMENDMENT 2026-11-16 ('The 96 landed runs' objective values (to compute R ...)'). (ii) ercot_noise_seed.json A3. (iv) screening_v3_locational.csv. (v) ERCOT_NOISE.md §12 item 3, plan AMENDMENT 2026-11-18. Next: plan AMENDMENT 2026-11-17 (R2 flag 2 × 156 = 312 MWh). Prompt 64 also names waves/screening_v3/README.md for a paper sentence; that file holds none, so it is not cited.

## Slide 13

**Source line:** Source: git log (SHAs below), PROGRESS.md, ERCOT_POOL_STANDINGS.md RERUN · plan amendment 11-17 … 11-18

Appendix A: process flow — four sessions, each step committed before the next read


| session | step | commits | first commit subject (git) |
| 57 B | standings on wave D rows (identity v3; the 11-07 base was v2) | — | prompt 57 Part B (ERCOT_POOL_STANDINGS.md) |
| 54 | Part A rerun on base_v3 + the 52 ruler | bac38e7 | pool_standings(54B rerun, minimal): thread the computed delta_label (same identi… |
| 62 B | amendment → script → fix → read | 6aa29dd / 6b5e85a / 82bb71d / d706199 | plan(62 pre-registration): AMENDMENT 2026-11-17 — E-D1b input widened to n0_E (p… |
| 61 | location_contrast_E wave → landing | 3b40c2d / 4b7bf85 | wave(61): location_contrast_E — 9 analysis-only 6-site rows (P1 joints 60/120/18… |
| 63 | A1 bar fix → noise_seed_E wave → landing | d265580 / 6fd3352 / 14378fd | noise(63 A1): exclude structural-zero perturbed pairs (D2 / site 206: perturbed … |
| 62 C | screening_v3 wave → extracts → landing → amendment | c986da0 / 1a2cde6 / e58f4bd / 1c6e73e | wave(62 Part C): screening_v3 — 11 analysis-only single-site rows at 180 MW unde… |
| 62 | Seed-bar re-grade addendum | baf77c3 | pool(62 RE-GRADE addendum 2026-11-18): n0_E standings with B^seed for the 63-A3-… |

**Notes:** Source: git log (SHAs below), PROGRESS.md, ERCOT_POOL_STANDINGS.md RERUN · plan amendment 11-17 … 11-18. Every SHA is checked with git cat-file at build time (objective_facts.py). e58f4bd / 1c6e73e / baf77c3 landed on ercot/tx123 after prompt 64 was written and are added here.

## Slide 14

**Source line:** Source: pool_standings.csv, pool_ed1b_combined.csv (waveD_range_over_B) · plan amendment 11-17

Appendix B: wave D under both rulers — R4 and N1 read 4.9–13.5× the old median ruler but ≤ 1.84× the bar B_j


| id | range / ruler_57 at 60 / 120 / 180 MW | range / B_j at 60 / 120 / 180 MW | wave-D B_j verdict |
| R4 | 7.7 / 6.9 / 13.5 | 1.04 / 0.94 / 1.84 | UNREADABLE (B_j) |
| N1 | 4.9 / 9.4 / 8.9 | 0.64 / 1.23 / 1.16 | UNREADABLE (B_j) |

•  The old ruler was the median |Δ| of the perturbed copies. The bar B_j is max(3σ̂, max |δ|) with the D2 zeros excluded.
•  B_j is 2.84–10.28× the current median ruler. R4 and N1 drop below the 2× readability line on wave D.
•  Both are BOX-ONLY candidates: unreadable as single sites at ≤ 180 MW; graded on n0_E only.

**Notes:** Source: pool_standings.csv, pool_ed1b_combined.csv (waveD_range_over_B) · plan amendment 11-17. pool_standings.csv range_over_ruler_L60/L120/L180 (RERUN, ruler = ercot_noise.json median ruler); pool_ed1b_combined.csv waveD_range_over_B_L60/L120/L180 and waveD_B_verdict; POOL_N0E_STANDINGS.md §5 (BOX-ONLY RESPONSE).

## Slide 15

**Source line:** Source: pool_ed1b_combined.csv, pool_ed1b_combined_seedbar.csv · plan amendment 11-17, 11-18

Appendix C (1/2): full E-D1b table — both bars side by side (binding bar per the Seed re-grade)


| id | order | IDR / B_j | IDR / B^seed | binding bar | status (re-grade) | reason (pre-registered) |
| V1 | 1 | 93.28 | 81.25 | perturbed (B_j) | OBJECTIVE | seat V: first eligible in global_order |
| E1 | 2 | 14.05 | 25.27 | perturbed (B_j) | OBJECTIVE | seat E: plan §1.2 final (E1) |
| X1 | 3 | 27.40 | 25.24 | perturbed (B_j) | REDUNDANT->E1 | REDUNDANT->E1 on n0_E (n0E-C2) |
| R4 | 4 | 2.11 | 1.12 | perturbed (B_j) | DIAGNOSTIC | BORDERLINE-only response (IDR/B_j in [2, 3), no wave-D backing |
| N1 | 5 | 6.43 | 3.05 | seed (A3 DISAGREE) | OBJECTIVE | seat N: first eligible in global_order |
| E4 | 6 | 10.46 | 8.80 | perturbed (B_j) | DIAGNOSTIC | E seat is E1 only (plan §1.2 final) |
| R2 | 7 | 0.75 | 0.74 | perturbed (B_j) | GUARDRAIL | guardrail (plan §1.3); never seated |
| R7 | 8 | 4.40 | 4.16 | perturbed (B_j) | DIAGNOSTIC | dir '-': shown, never clustered or seated |
| N4 | 9 | 17.38 | 14.43 | perturbed (B_j) | SIZE-CO-MONOTONE (with V1, N1) | family N seat held by N1 (earlier in global_order) |
| N5 | 10 | 17.12 | 16.39 | perturbed (B_j) | REDUNDANT->E4 | REDUNDANT->E4 on n0_E (n0E-C3) |
| E6 | 11 | 14.57 | 24.32 | perturbed (B_j) | REDUNDANT->V1 | REDUNDANT->V1 on n0_E (n0E-C1) |
| R5 | 12 | 0.89 | 1.20 | perturbed (B_j) | DIAGNOSTIC | NOT RESPONDS (n0_E) |
| N3 | 13 | 0.66 | 0.88 | perturbed (B_j) | DIAGNOSTIC | NOT RESPONDS (n0_E) |
| E2 | 14 | 3.29 | 2.62 | perturbed (B_j) | REDUNDANT->E1 | REDUNDANT->E1 on n0_E (n0E-C2) |

**Notes:** Source: pool_ed1b_combined.csv, pool_ed1b_combined_seedbar.csv · plan amendment 11-17, 11-18. Binding = IDR_over_B in the seedbar csv (Seed bar for the A3-DISAGREE ids N1, E9; B_j elsewhere).

## Slide 16

**Source line:** Source: pool_ed1b_combined.csv, pool_ed1b_combined_seedbar.csv · plan amendment 11-17, 11-18

Appendix C (2/2): full E-D1b table — both bars side by side (binding bar per the Seed re-grade)


| id | order | IDR / B_j | IDR / B^seed | binding bar | status (re-grade) | reason (pre-registered) |
| R6 | 15 | 0.81 | 0.90 | perturbed (B_j) | DIAGNOSTIC | NOT RESPONDS (n0_E) |
| N2 | 16 | 0.43 | 0.35 | perturbed (B_j) | DIAGNOSTIC | NOT RESPONDS (n0_E) |
| E3 | 17 | 7.00 | 6.80 | perturbed (B_j) | DIAGNOSTIC | E seat is E1 only (plan §1.2 final) |
| R8 | 18 | 1.16 | 1.30 | perturbed (B_j) | DIAGNOSTIC | dir '-': shown, never clustered or seated |
| E7 | 19 | 14.09 | 16.45 | perturbed (B_j) | DIAGNOSTIC | dir '-': shown, never clustered or seated |
| E8 | 20 | 1.02 | 1.05 | perturbed (B_j) | DIAGNOSTIC | NOT RESPONDS (n0_E) |
| E9 | 21 | n/a | 0.00 | seed (A3 DISAGREE) | DIAGNOSTIC | READABLE (RULER=0) (n0_E) |
| V2 | 22 | 83.92 | 44.86 | perturbed (B_j) | REDUNDANT->E4 | REDUNDANT->E4 on n0_E (n0E-C3) |
| V3 | 23 | 67.15 | 10.83 | perturbed (B_j) | DIAGNOSTIC | dir '-': shown, never clustered or seated |
| E5 | 24 | n/a | n/a | perturbed (B_j) | DEAD | dead (57 A2 list or constant on n0_E) |
| R1 | 25 | n/a | n/a | perturbed (B_j) | DEAD | dead (57 A2 list or constant on n0_E) |
| R3 | 26 | n/a | n/a | perturbed (B_j) | DEAD | dead (57 A2 list or constant on n0_E) |
| D1 | 27 | 650.62 | 178.51 | perturbed (B_j) | DIAGNOSTIC | dir '-': shown, never clustered or seated |
| D2 | 28 | 108.68 | 80.67 | perturbed (B_j) | DIAGNOSTIC | dir '-': shown, never clustered or seated |

**Notes:** Source: pool_ed1b_combined.csv, pool_ed1b_combined_seedbar.csv · plan amendment 11-17, 11-18. Binding = IDR_over_B in the seedbar csv (Seed bar for the A3-DISAGREE ids N1, E9; B_j elsewhere).

## Slide 17

**Source line:** Source: ercot_noise_seed.csv, NOISE_SEED_E.md §2 · plan amendment 11-18

Appendix D (1/2): bars for every graded id — perturbed B_j (D2 excluded) vs Seed B^seed; A3 verdict


| id | unit | σ̂_c (Seed) | σ̂_pert | ratio | A3 | B^seed | B_j | B^seed / B_j |
| V1 | MWh | 4376 | 5391 | 1.15 | AGREE | 1.857e+04 | 1.617e+04 | 1.15 |
| V2 | % | 0.001812 | 0.00137 | 1.87 | AGREE | 0.007687 | 0.004109 | 1.87 |
| V3 | fraction | 4.536e-05 | 1.034e-05 | 6.20 | DISAGREE | 0.0001924 | 3.103e-05 | 6.20 |
| E1 | $ | 3.124e+05 | 7.944e+05 | 0.56 | AGREE | 1.325e+06 | 2.383e+06 | 0.56 |
| E2 | $ | 8.583e+05 | 9.674e+05 | 1.25 | AGREE | 3.641e+06 | 2.902e+06 | 1.25 |
| E3 | $ | 8.411e+05 | 1.157e+06 | 1.03 | AGREE | 3.569e+06 | 3.47e+06 | 1.03 |
| E4 | $ | 2.382e+06 | 2.835e+06 | 1.19 | AGREE | 1.01e+07 | 8.505e+06 | 1.19 |
| E6 | $ | 4.106e+05 | 9.694e+05 | 0.60 | AGREE | 1.742e+06 | 2.908e+06 | 0.60 |
| E7 | $/MWh | 0.003353 | 0.005537 | 0.86 | AGREE | 0.01422 | 0.01661 | 0.86 |
| E8 | $/MWh | 0.06868 | 0.1008 | 0.96 | AGREE | 0.2914 | 0.3024 | 0.96 |
| E9 | count | 0.3162 | 0 | inf | DISAGREE (one ruler is 0) | 1.342 | 0 | n/a |
| R2 | MWh | 24.22 | 34.1 | 1.00 | AGREE | 102.7 | 102.3 | 1.00 |
| R4 | count | 65.09 | 48.88 | 1.88 | AGREE | 276.1 | 146.7 | 1.88 |

**Notes:** Source: ercot_noise_seed.csv, NOISE_SEED_E.md §2 · plan amendment 11-18. All cells: ercot_noise_seed.csv (sigma_c, sigma_hat_pert, ratio_seed_over_pert, A3, B_seed, B_pert).

## Slide 18

**Source line:** Source: ercot_noise_seed.csv, NOISE_SEED_E.md §2 · plan amendment 11-18

Appendix D (2/2): bars for every graded id — perturbed B_j (D2 excluded) vs Seed B^seed; A3 verdict


| id | unit | σ̂_c (Seed) | σ̂_pert | ratio | A3 | B^seed | B_j | B^seed / B_j |
| R5 | MW | 2880 | 5540 | 0.74 | AGREE | 1.237e+04 | 1.662e+04 | 0.74 |
| R6 | MW | 2.189e+04 | 3.444e+04 | 0.90 | AGREE | 9.286e+04 | 1.033e+05 | 0.90 |
| R7 | MWh | 6.696e+04 | 8.959e+04 | 1.06 | AGREE | 2.841e+05 | 2.688e+05 | 1.06 |
| R8 | unit-h | 325 | 514.4 | 0.89 | AGREE | 1379 | 1543 | 0.89 |
| N1 | line-h | 57.06 | 38.31 | 2.11 | DISAGREE | 242.1 | 114.9 | 2.11 |
| N2 | count | 0.8803 | 1 | 1.24 | AGREE | 3.735 | 3 | 1.24 |
| N3 | MWh | 2.469 | 4.658 | 0.75 | AGREE | 10.47 | 13.97 | 0.75 |
| N4 | line-h | 10.49 | 12.32 | 1.20 | AGREE | 44.51 | 36.97 | 1.20 |
| N5 | $/MWh | 0.04495 | 0.06087 | 1.04 | AGREE | 0.1907 | 0.1826 | 1.04 |
| X1 | t | 9326 | 1.215e+04 | 1.09 | AGREE | 3.957e+04 | 3.645e+04 | 1.09 |
| D1 | MWh | 3744 | 1453 | 3.64 | DISAGREE | 1.589e+04 | 4358 | 3.64 |
| D2 | fraction | 0.0003889 | 0.0004083 | 1.35 | AGREE | 0.00165 | 0.001225 | 1.35 |

A3 verdict: AGREE on 20 of 22 gradable ids; DISAGREE on N1, E9. E5, R1, R3 are exactly 0 under both rulers (not listed).

**Notes:** Source: ercot_noise_seed.csv, NOISE_SEED_E.md §2 · plan amendment 11-18. All cells: ercot_noise_seed.csv (sigma_c, sigma_hat_pert, ratio_seed_over_pert, A3, B_seed, B_pert).

## Slide 19

**Source line:** Source: extracts/*/wallclock.csv (× 4 slots), ercot_noise_seed.json · plan amendment 11-14 … 11-18

Appendix E: run inventory and core-hours — 5.3k core-h of evidence behind this selection


| wave | runs | core-h | source |
| base_v3 | 1 | 44.1 | extracts/base_v3/wallclock.csv × 4 |
| wave D (location_oat_v2) | 21 | 584.0 | extracts/location_oat_v2/wallclock.csv × 4 |
| noise_v3 (A + B) | 16 | 654.6 | extracts/noise_v3/{A,B}/wallclock.csv × 4 |
| n0_E + random_E | 96 | 3,006.0 | plan AMENDMENT 2026-11-16 (extracts not opened) |
| location_contrast_E | 9 | 182.4 | extracts/location_contrast_E/wallclock.csv × 4 |
| noise_seed_E | 18 | 589.5 | ercot_noise_seed.json (Threads 4 / 8 / 1 slots) |
| screening_v3 | 11 | 259.3 | extracts/screening_v3/wallclock.csv × 4 |
| total | 172 | 5,319.9 | sum |

**Notes:** Source: extracts/*/wallclock.csv (× 4 slots), ercot_noise_seed.json · plan amendment 11-14 … 11-18. Core-h = Σ wall_s / 3600 × 4 slots (-pe smp 4 in the array scripts); noise_seed_E uses the json total because rows 17 / 18 ran on 8 / 1 slots (589.5, not 590.2 at 4 slots). n0_E + random_E: plan AMENDMENT 2026-11-16 (the extracts are never opened by this deck).

## Slide 20

**Source line:** Source: SCREENING_V3.md, screening_v3_{locational,ranking,dominance,sites}.csv · plan amendment 11-18

Appendix F: screening_v3 (16 sites, 180 MW, v3) — V1, E1 and N4 are locational ERCOT-wide; N1 is not; the slate bus set holds


/Users/yilu/Documents/GitHub/RTS-GMLC-e64/trial_0826/ercot/analysis/pool/figs/screening_v3/sv3_hl_over_B.png

| id | HL / B_j | Holm p | verdict |
| V1 | -33.1 | 0.036 | LOCATIONAL |
| E1 | -8.7 | 0.036 | LOCATIONAL |
| N4 | -2.7 | 0.047 | LOCATIONAL |
| N5 | +4.3 | 0.036 | LOCATIONAL |
| E6 | +10.3 | 0.036 | LOCATIONAL |
| E3 | -4.6 | 0.036 | LOCATIONAL |
| V3 | -60.8 | 0.036 | LOCATIONAL |
| N1 | -3.0 | 0.653 | NOT LOCATIONAL |
| X1 | -6.1 | 0.295 | NOT LOCATIONAL |
| V2 | +32.6 | 0.087 | NOT LOCATIONAL |

•  Contrast: pocket_120 ∪ wind_near (8 sites) vs far (5 sites); Holm over 23 ids. N1: -3.0 B_pert / -1.43 B_seed, Holm p 0.65, interval contains 0.
•  E1 is WITHIN GAP BOUND at 16 / 16 sites. The replicate (site 163) is md5-equal to wave D row 3.
•  Matched-MW top 6 = 270, 275, 274, 110, 140, 146: bus set HOLDS; 275 in, 163 out (as predicted); τ_b 0.667. 81 % of 163's relief is own-site.
•  Dominance: on V1/E1/N1 sites 116 (0.72 B) and 91 (0.44 B) are not dominated; on V1/E1/N4 only 116 (0.72 B). All margins < 1 B: PI flag; E-D3 stands.

**Notes:** Source: SCREENING_V3.md, screening_v3_{locational,ranking,dominance,sites}.csv · plan amendment 11-18. Figure /Users/yilu/Documents/GitHub/RTS-GMLC-e64/trial_0826/ercot/analysis/pool/figs/screening_v3/sv3_hl_over_B.png (screening_v3_landing.py). Table: screening_v3_locational.csv. Ranking: screening_v3_ranking.csv; τ_b and md5: SCREENING_V3.md §0. Own-site share: screening_v3_sites.csv. Dominance: screening_v3_dominance.csv (margin_bars). This replaces the prompt-64 fallback text because SCREENING_V3.md exists at build time.

