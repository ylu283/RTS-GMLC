# ercot_location.pptx — slide text and speaker notes

## Slide 1


ERCOT TX-123BT · WAVE D · 2026-11-07

Does location matter in ERCOT? Wave D, six sites × three sizes

Identity v3 · 21 full-year runs · 584 core-h · 0 SUSPECT rows
Kay Lu · draft v1 (figure paths printed on each slide)

**Notes:** Deck source: analysis/pi_location/make_location_deck.py. Numbers: /Users/yilu/Documents/GitHub/RTS-GMLC-ercot/trial_0826/ercot/analysis/pool/ERCOT_POOL_STANDINGS.md (header: 21 rows, 0 SUSPECT, 7,665 / 7,665 RUCs OPTIMAL; §8: 584 core-h). Mirrors RTS pi_1008 slides 8–14 (location section).

## Slide 2

The question: at a fixed PEM size, does the site change the objective?


ERCOT wave D · location read · draft v1 · 2026-11-07

•  RTS-GMLC (pi_1008, slides 8–14)
•  6 tiers. 15 pair grids, 9 × 9 cells each. 1,215 full-year runs.
•  Curtailment: location-sensitive in 15 / 15 pairs (gate 4.2–12.6× floor).
•  Cost: two regimes. Nuclear pairs 16.5–32.9× floor; renewable-only pairs 1.6–5.6×.
•  Load shed: direction only. Tilt replicates in 11 / 15 pairs; absolute effect ≤ 1.4× floor.
•  Instrument: 1 % RUC gap with Monte-Carlo range floors; F tests against the floor.

•  ERCOT today (wave D, prompt 57 Part B)
•  One site at a time. 6 WIND sites × 60 / 120 / 180 MW = 18 VRE rows.
•  Plus nuclear gen 1 × 3 levels = 3 overlay rows (never in the statistics).
•  No pairs. No interactions. No mixed designs.
•  Instrument: identity v3 (gap 0.001, TL 1,200 s). Deterministic: exact replicate ruler = 0.
•  Noise ruler PENDING (prompt 52). Base is a v2 run: every Δ vs base is CONTAMINATED.

The ERCOT read is weaker by design: 18 points, 3 levels. It reads the ORDER of sites and a base-free spread ratio. It does not read significance.

**Notes:** Left column: RTS pi_1008 v1/SLIDE_TEXT.md slides 8, 9, 13 (verbatim numbers). Right column: /Users/yilu/Documents/GitHub/RTS-GMLC-ercot/trial_0826/ercot/analysis/pool/ERCOT_POOL_STANDINGS.md header + honesty clause (18–21 rows, 3 levels, no interactions; no multiplicity correction).

## Slide 3

Design: the top-6 curtailment-relief WIND sites, each alone, at 60 / 120 / 180 MW


ERCOT wave D · location read · draft v1 · 2026-11-07

| Site | Bus (name) | Nameplate MW | ω at 60 / 120 / 180 MW | Slate rank (relief per MW) |
| 163 | 120 (Knox City 345) | 185.4 | 0.324 / 0.647 / 0.971 | 1 |
| 140 | 2 (Wheeler 345) | 250.6 | 0.239 / 0.479 / 0.718 | 2 |
| 146 | 75 (Panhandle 3 345) | 268.0 | 0.224 / 0.448 / 0.672 | 3 |
| 270 | 120 (Knox City 345) | 579.0 | 0.104 / 0.207 / 0.311 | 4 |
| 110 | 2 (Wheeler 345) | 338.6 | 0.177 / 0.354 / 0.532 | 5 |
| 274 | 120 (Knox City 345) | 746.4 | 0.080 / 0.161 / 0.241 | 6 |
| 1 (nuclear) | 107 (Glen Rose 2 345) | 2430 | 0.0247 / 0.0494 / 0.0741 | overlay (formulation A) |

Why these six
The pre-registered rule (analysis/cost_fix/WAVE_D_TOPK_RULE.md, commit 4fb3b1f) ranks screening_v2 sites by Δ true curtailment per MW and keeps the top 6. The A ruler is 0, so every site qualified and the rule reduced to the top 6 by rank.
Result: a homogeneous congested slate. Sites 163, 270, 274 sit on bus 120 (Knox City). Sites 110, 140 sit on bus 2 (Wheeler). Site 146 sits on bus 75 (Panhandle 3). The location read below is a read INSIDE congested sites.
Size is absolute MW, not ω. Site 163 (185 MW nameplate) reaches ω 0.97 at 180 MW.

Identity v3
ruc_mipgap 0.001, ruc_time_limit 1,200 s (GAP_DECISION.json, E-D6). 0 TIME_LIMIT on 7,665 RUCs.

--full extracts
Every row --full: E8, E9, N5 from pool_full_metrics.json. 0 SUSPECT rows (S1–S3 pass).

Deterministic instrument
Exact replicates are byte-identical (A ruler = 0). Noise ruler = prompt 52, PENDING.

Base = v2 run
base_2019_v2:1 ran at gap 0.01 / TL 120. Every Δ vs base is CONTAMINATED until base_v3 lands.

**Notes:** Table: pool_wavedD_wide.csv (site, bus, pem_mw, omega, gen_pmax), data/ercot123_2019_v2/bus.csv (Bus Name), analysis/cost_fix/wave_d_selection.json (rank by relief_per_mw: 163 3,841; 140 3,630; 146 3,587; 270 3,568; 110 3,502; 274 3,501). Rule file: analysis/cost_fix/WAVE_D_TOPK_RULE.md (prompt 36 §4.2). Cards: waves/GAP_DECISION.json; /Users/yilu/Documents/GitHub/RTS-GMLC-ercot/trial_0826/ercot/analysis/pool/ERCOT_POOL_STANDINGS.md header and §0.1. Nuclear ω = 60/120/180 MW over 2,430 MW (waves/location_oat_v2/README.md §2).

## Slide 4

Method: pinned statistics, one base-free rule, no test


ERCOT wave D · location read · draft v1 · 2026-11-07

| Statistic | What it measures | Decision use |
| range_jℓ | max − min over the 6 sites at level ℓ (60 / 120 / 180 MW); base-invariant | Printed at every level; the ruler read divides it by ruler_j (PENDING) |
| S′_jℓ (primary) | range_jℓ / mean_site |x(site, 180) − x(site, 60)|: between-site spread over the within-site size effect; base-free | LOCATION-SENSITIVE iff S′ ≥ 0.5 at 2 of 3 levels; SIZE-DRIVEN iff S′ < 0.5 at 2 of 3 |
| S_jℓ (secondary) | range_jℓ / mean_site |Δ_jℓ vs base|; same thresholds (pinned f76d897) | Shown beside S′; CONTAMINATED where the identity shift dominates the Δ |
| Kendall W, exact p | Agreement of the 3 level-rankings of the 6 sites; exact p over 518,400 permutations | Descriptor only; enters no verdict |
| Oriented Spearman ρ | Rank agreement of two candidates, oriented by direction; pooled n = 18 and per level n = 6 | REDUNDANT iff ρ ≥ +0.90 pooled AND at 2 of 3 levels; complete linkage |
| Gap bound G | Σ_days gap × ruc_cost; pair bound G_a + G_b (E1–E3 only) | GAP-READABLE iff |Δ| > bound; approximate (RUC objective, not realized cost) |
| Ruler_j | Replicate noise under identity v3 (prompt 52 noise_v3) | RULER PENDING (52): every ruler column is a placeholder |

No multiplicity correction. The verdicts are threshold reads on a deterministic instrument, not tests. Among ~22 graded candidates about one W p < 0.05 is expected under exchangeable site labels.
The error direction is permissive: a false LOCATION-SENSITIVE call admits one more candidate to the PI table.

**Notes:** Source: /Users/yilu/Documents/GitHub/RTS-GMLC-ercot/trial_0826/ercot/analysis/pool/ERCOT_POOL_STANDINGS.md §0.2 (S′, S), §1 (W), §2 (G), §4 (ρ rule), honesty clause (no multiplicity correction; permissive error direction), ruler status line. Mirrors RTS pi_1008 slide 9 (statistic / what / decision use).

## Slide 5

OAT view: curtailment curves overlap; cost curves fan out; starts and congestion scatter


ERCOT wave D · location read · draft v1 · 2026-11-07

Raw value vs PEM MW, one line per site (fixed colours across the deck). Nuclear gen 1 dashed black; omitted on E1 because its cost is UNCORRECTED.
/Users/yilu/Documents/GitHub/RTS-GMLC-ercot/trial_0826/ercot/analysis/pi_location/figs/oat_curves_ercot.png

Takeaway
V1 curtailment: the six curves overlap. Size drives it. S′ 0.06 / 0.14 / 0.29.
E1 cost: the curves fan out with MW. Site 163 is flat: ω 0.97 on a 185 MW nameplate saturates. S′ 0.39 / 0.97 / 1.62; W p 0.002.
X1 CO₂ moves with E1 (same fan, same flat site 163).
R4 starts, N1 line-hours, R2 shortfall: the lines cross. No stable site order (W p 0.792 / 0.754 / 0.214).
Data
pool_standings_levels.csv (18 VRE rows per candidate) + pool_wavedD_wide.csv rows 19–21 (nuclear).

**Notes:** Figure: /Users/yilu/Documents/GitHub/RTS-GMLC-ercot/trial_0826/ercot/analysis/pi_location/figs/oat_curves_ercot.png (make_location_figs.py, fig_oat). Values: /Users/yilu/Documents/GitHub/RTS-GMLC-ercot/trial_0826/ercot/analysis/pool/pool_standings_levels.csv; nuclear rows from /Users/yilu/Documents/GitHub/RTS-GMLC-ercot/trial_0826/ercot/analysis/pool/pool_wavedD_wide.csv. S′ and W p: /Users/yilu/Documents/GitHub/RTS-GMLC-ercot/trial_0826/ercot/analysis/pool/pool_standings.csv. Reads: /Users/yilu/Documents/GitHub/RTS-GMLC-ercot/trial_0826/ercot/analysis/pool/ERCOT_POOL_STANDINGS.md §1 'Reads, in plain words'. RTS analogue: pi_1008 slide 10 (oat_curves_C.png).

## Slide 6

Spread ratio S′: 13 of 16 survivors pass 0.5 at 2 of 3 levels; V1 does not


ERCOT wave D · location read · draft v1 · 2026-11-07

S′ at L60 / L120 / L180 (log scale), 16 survivors in global order, colour by family; dashed = 0.5 rule.
/Users/yilu/Documents/GitHub/RTS-GMLC-ercot/trial_0826/ercot/analysis/pi_location/figs/sprime_bars.png

| id | S′ L60 | L120 | L180 | W p | Status |
| V1 | 0.06 | 0.14 | 0.29 | 0.025 | LOC-INSENSITIVE (these sizes) |
| E1 | 0.39 | 0.97 | 1.62 | 0.002 | LOC-SENSITIVE |
| R4 | 1.74 | 1.57 | 3.06 | 0.792 | LOC-SENSITIVE |
| N1 | 1.46 | 2.83 | 2.67 | 0.754 | LOC-SENSITIVE |
| E4 | 0.54 | 1.22 | 1.24 | 0.070 | LOC-SENSITIVE |
| R2 | 3.05 | 1.66 | 1.69 | 0.214 | LOC-SENSITIVE |
| N4 | 0.40 | 0.53 | 1.69 | 0.379 | LOC-SENSITIVE |
| N5 | 0.36 | 0.45 | 1.08 | 0.134 | LOC-INSENSITIVE (these sizes) |
| E6 | 0.18 | 0.72 | 0.39 | 0.090 | LOC-INSENSITIVE (these sizes) |
| R5 | 2.15 | 1.81 | 1.90 | 0.699 | LOC-SENSITIVE |
| N3 | 5.92 | 15.44 | 7.66 | 0.414 | LOC-SENSITIVE |
| E2 | 1.70 | 1.12 | 2.09 | 0.232 | LOC-SENSITIVE |
| R6 | 0.93 | 2.67 | 3.74 | 0.858 | LOC-SENSITIVE |
| N2 | 1.80 | 1.20 | 3.00 | 0.901 | LOC-SENSITIVE |
| E3 | 0.61 | 0.88 | 1.62 | 0.112 | LOC-SENSITIVE |
| E8 | 1.57 | 3.27 | 2.41 | 0.699 | LOC-SENSITIVE |

Read
V1, N5, E6 are SIZE-DRIVEN: the six top-relief sites relieve curtailment within ±5–15 % of each other at matched MW.
E1 passes at L120 and L180 only; at L60 the spread is 0.39 of the size effect.
R4–R6, N1–N4, E2, E8 pass S′ with W p ≥ 0.2: a large spread with a site order that changes from level to level. Only the prompt-52 ruler can size that chatter. Their status is provisional.

**Notes:** Figure: /Users/yilu/Documents/GitHub/RTS-GMLC-ercot/trial_0826/ercot/analysis/pi_location/figs/sprime_bars.png (make_location_figs.py, fig_sprime). Table: /Users/yilu/Documents/GitHub/RTS-GMLC-ercot/trial_0826/ercot/analysis/pool/pool_standings.csv (S_prime_L60/L120/L180, W_p_exact, status; is_survivor = True, sorted by global_order_rank). Reads: /Users/yilu/Documents/GitHub/RTS-GMLC-ercot/trial_0826/ercot/analysis/pool/ERCOT_POOL_STANDINGS.md §1. Deviation from the spec layout: the table sits beside the figure, not beneath it (17 rows do not fit under a legible figure). RTS analogue: pi_1008 slide 11 (oat_spread_ratio.png).

## Slide 7

Variance explained: site identity adds 32 points for cost; nothing fits starts or line-hours


ERCOT wave D · location read · draft v1 · 2026-11-07

R²adj of model 0 (quadratic in MW) and ΔR²adj for + site intercepts, then + site × MW. 18 VRE rows per candidate.
/Users/yilu/Documents/GitHub/RTS-GMLC-ercot/trial_0826/ercot/analysis/pi_location/figs/ancova_ercot.png

| Candidate | R²adj quad. MW | + site intercepts | + site × MW | Reading |
| V1 true curtailment | 0.965 | +0.013 | +0.012 | mostly size |
| E1 total cost | 0.515 | +0.322 | +0.153 | level shift |
| R4 thermal starts | 0.192 | -0.038 | -0.385 | no fit |
| N1 congested line-hours | 0.056 | -0.000 | -0.297 | no fit |
| R2 reserve shortfall | -0.032 | +0.269 | +0.248 | level shift |
| X1 CO2 (fuel-factor) | 0.521 | +0.284 | +0.184 | level shift |

Takeaway
V1: MW alone explains 97 %. Site adds 1 point. Mostly size.
E1 and X1: MW explains 52 %; site intercepts add 32 / 28 points; slopes add 15 / 18. Level shift first, then slope.
R4, N1: no model exceeds R²adj 0.2. Neither MW nor site explains the 18 rows. The spread is unstructured.
R2: a weak fit (0.49) with equal site and slope shares.

Method. Model 0: 1 + MW + MW² (2 df; residual df 15). Model 1: + 5 site intercepts (residual df 10). Model 2: + 5 site × MW slopes (residual df 5). R²adj = 1 − (RSS/(n−p)) / (TSS/(n−1)). Reading rule: 'no fit' if every R²adj < 0.3; 'mostly size' if both increments < 0.10; 'slopes differ' if the slope increment ≥ 0.10 and ≥ the intercept increment; else 'level shift'. No ruler, no F.

**Notes:** Figure: /Users/yilu/Documents/GitHub/RTS-GMLC-ercot/trial_0826/ercot/analysis/pi_location/figs/ancova_ercot.png; table: /Users/yilu/Documents/GitHub/RTS-GMLC-ercot/trial_0826/ercot/analysis/pi_location/figs/ancova_ercot.csv (make_location_figs.py, ancova_table). Data: /Users/yilu/Documents/GitHub/RTS-GMLC-ercot/trial_0826/ercot/analysis/pool/pool_standings_levels.csv, 18 VRE rows per candidate. NO F test (no ruler). 'no fit' is added to the RTS vocabulary because R4 and N1 have negative R²adj at models 1 and 2. RTS analogue: pi_1008 slide 12 (oat_ancova_increments.png).

## Slide 8

Atlas: Δ vs base, 6 sites × 3 MW, for the four recommended candidates (Δ CONTAMINATED)


ERCOT wave D · location read · draft v1 · 2026-11-07

V1: LOC-INSENSITIVE (these sizes) · S′ 0.06 / 0.14 / 0.29 · W p 0.025 · Δ CONTAMINATED

E1: LOC-SENSITIVE · S′ 0.39 / 0.97 / 1.62 · W p 0.002 · Δ CONTAMINATED

R4: LOC-SENSITIVE · S′ 1.74 / 1.57 / 3.06 · W p 0.792 · Δ CONTAMINATED

N1: LOC-SENSITIVE · S′ 1.46 / 2.83 / 2.67 · W p 0.754 · Δ CONTAMINATED

Paths: /Users/yilu/Documents/GitHub/RTS-GMLC-ercot/trial_0826/ercot/analysis/pool/figs/standings/V1.png  ·  /Users/yilu/Documents/GitHub/RTS-GMLC-ercot/trial_0826/ercot/analysis/pool/figs/standings/E1.png  ·  /Users/yilu/Documents/GitHub/RTS-GMLC-ercot/trial_0826/ercot/analysis/pool/figs/standings/R4.png  ·  /Users/yilu/Documents/GitHub/RTS-GMLC-ercot/trial_0826/ercot/analysis/pool/figs/standings/N1.png

**Notes:** Figures: /Users/yilu/Documents/GitHub/RTS-GMLC-ercot/trial_0826/ercot/analysis/pool/figs/standings/V1.png
/Users/yilu/Documents/GitHub/RTS-GMLC-ercot/trial_0826/ercot/analysis/pool/figs/standings/E1.png
/Users/yilu/Documents/GitHub/RTS-GMLC-ercot/trial_0826/ercot/analysis/pool/figs/standings/R4.png
/Users/yilu/Documents/GitHub/RTS-GMLC-ercot/trial_0826/ercot/analysis/pool/figs/standings/N1.png
Captions: /Users/yilu/Documents/GitHub/RTS-GMLC-ercot/trial_0826/ercot/analysis/pool/pool_standings.csv (status, S_prime, W, W_p_exact, nuc_tag). The heatmaps come from pool_standings.py (6 × 3 Δ vs v2 base, nuclear row overlaid below a black rule, hatched = UNCORRECTED on E1). RTS analogue: pi_1008 slide 13 (atlas_heattables.png).

## Slide 9

Redundancy: cluster {E1, V2, X1} → E1. The pinned cost-vs-CO₂ conflict did not appear


ERCOT wave D · location read · draft v1 · 2026-11-07

Oriented Spearman ρ at L180 (n = 6 sites) with complete-linkage dendrogram; green boxes = redundant pairs.
/Users/yilu/Documents/GitHub/RTS-GMLC-ercot/trial_0826/ercot/analysis/pool/figs/standings/clustermap_L180.png

Rule (f76d897)
REDUNDANT iff ρ_or ≥ +0.90 pooled (n = 18) AND ≥ +0.90 at 2 of 3 levels (n = 6). Complete linkage. Base-invariant.
Result
4 redundant pairs: V2–E1 0.98, V2–X1 0.99, E1–X1 0.98, V2–E3 0.90. One cluster C1 = {E1, V2, X1}; survivor E1 (global order 2).
E3 is redundant with V2 only, so complete linkage leaves it out.
Pinned expectation falsified
E1–X1 was expected to CONFLICT ('cheaper = more coal'). On wave D ρ = +0.98 pooled, +0.94 at L120 and L180.
Mechanism: PEM at a VRE site raises day-ahead thermal commitment. Cost and CO₂ rise together, in the same site order. X1 is REDUNDANT → E1.
The real axes
V1–E1 ρ = −0.70: a SIZE trade-off. More PEM MW relieves more curtailment and costs more.
LOCATION trade-offs run between the pocket N4 and the cost family (E1 −0.77, E3 −0.76, E4 −0.73) and N5 (−0.76).
Among the recommended four: V1–R4 +0.34, V1–N1 +0.53, R4–N1 +0.02, E1–N1 −0.26 (not labelled).

**Notes:** Figure: /Users/yilu/Documents/GitHub/RTS-GMLC-ercot/trial_0826/ercot/analysis/pool/figs/standings/clustermap_L180.png (pool_standings.py). Alternative: /Users/yilu/Documents/GitHub/RTS-GMLC-ercot/trial_0826/ercot/analysis/pool/figs/standings/clustermap_stratified.png. Numbers: /Users/yilu/Documents/GitHub/RTS-GMLC-ercot/trial_0826/ercot/analysis/pool/ERCOT_POOL_STANDINGS.md §4 (redundant pairs, cluster C1, falsified expectation) and §6 (conflict table; /Users/yilu/Documents/GitHub/RTS-GMLC-ercot/trial_0826/ercot/analysis/pool/pool_conflicts_wavedD.csv, /Users/yilu/Documents/GitHub/RTS-GMLC-ercot/trial_0826/ercot/analysis/pool/pool_spearman_wavedD_pairs.csv).

## Slide 10

Cost under the gap bound: the site ORDER is stable, the SIZE of the difference is not readable


ERCOT wave D · location read · draft v1 · 2026-11-07

$2.2 / 5.5 / 9.2M

E1 between-site range at 60 / 120 / 180 MW (base-free).

$41–48M raw

v3-only pair bound max G_a + G_b. Scaled to realized cost: $9.7–11.4M. L180 range is 95 % of the scaled bound.

$196.7M

G_base of the v2 base (gap 0.01). It is 90 % of every Δ-vs-base pair bound ($215–222M).

0 / 18

E1 per-site Δ vs base GAP-READABLE (raw or scaled bound). E2 18 / 18 scaled = the identity shift, not PEM.

| Level | E1 range | v3 pair bound, raw | status | v3 pair bound, scaled | status |
| L60 | $2.20M | $47.7M | WITHIN GAP BOUND | $11.2M | WITHIN GAP BOUND |
| L120 | $5.51M | $48.2M | WITHIN GAP BOUND | $11.4M | WITHIN GAP BOUND |
| L180 | $9.21M | $41.0M | WITHIN GAP BOUND | $9.7M | WITHIN GAP BOUND |

•  Read: the cost site order is stable (W p 0.002; site 163 cheapest at every level). The between-site cost difference sits inside the v3-only pair bound at every level. Size is not gap-readable at ≤ 180 MW.
•  Every Δ vs the v2 base is WITHIN GAP BOUND, and that bound is dominated by the base's own 1 % slack. The Δ-vs-base read is uninformative about wave D.
•  Disclosure: ruc_cost is the 36-hour RUC objective, not realized cost; G is an approximate bound. Scale factor ruc_cost_sum / E1 ≈ 4.24. E4 and E6 have no gap bound. Plan §1.2 is untouched and waits for prompt 52.

**Notes:** Source: /Users/yilu/Documents/GitHub/RTS-GMLC-ercot/trial_0826/ercot/analysis/pool/pool_gap_bound_wavedD.csv (E1 rows: range_at_level_usd, v3_pair_bound_max_usd, v3_pair_bound_max_scaled_usd, G_base_usd, G_base_share_of_bound), /Users/yilu/Documents/GitHub/RTS-GMLC-ercot/trial_0826/ercot/analysis/pool/ERCOT_POOL_STANDINGS.md §2 (table and verdict), /Users/yilu/Documents/GitHub/RTS-GMLC-ercot/trial_0826/ercot/analysis/pool/pool_gap_bound_summary.json (G_base 196.7M). W p from pool_standings.csv (E1 0.0018).

## Slide 11

Caveats: four things that govern every number in this deck


ERCOT wave D · location read · draft v1 · 2026-11-07

| # | Caveat | What it does to the read |
| a | Δ vs v2 base is CONTAMINATED (v2 base, v3 rows). Smoke identity shift (3 January days × 365/3): V1 -67.7 GWh/yr, E1 $-10.9M/yr, R4 -1,947 starts/yr, N1 -973 line-h/yr. | S (needs a base) reads SIZE-DRIVEN for the wrong reason on E2, E3, R4–R7, N1, E8. S′, range, W, ρ, clusters are base-free and clean. |
| b | RULER PENDING (52). No replicate noise under identity v3 exists. | No readability verdict. R4, N1 and the other S′-passers with W p ≥ 0.2 are provisional. |
| c | Nuclear cost UNCORRECTED. The thermal patch rewrites the gen-1 cost curve (zero at p_min); K_syn accounting pending. | E1–E4, E7 on nuclear rows show Δ −$383M / −$366M / −$349M. Not a PEM effect. Hatched on the heatmaps; omitted on the OAT cost panel. |
| d | Homogeneous slate: six top-relief WIND sites on three congested buses. | The location effect here is INSIDE congested sites. The caps (163: 185 MW; 274: 746 MW) are where the BO space will see location. |

| id | scaled identity shift | |shift| / mean |Δ| at L60 | at L180 | read |
| V1 | -67,714 MWh/yr | 0.22 | 0.10 | 10–20 % contaminated |
| E1 | -10,887,945 $/yr | 0.44 | 0.57 | about half identity |
| R4 | -1,947 starts/yr | 3.24 | 2.87 | DOMINATED |
| N1 | -973 line-h/yr | 4.85 | 3.96 | DOMINATED |

A ratio near or above 1 means the identity change alone can account for the whole Δ vs base. The scaling is a size indication from three winter days, not a year estimate.

**Notes:** Source: /Users/yilu/Documents/GitHub/RTS-GMLC-ercot/trial_0826/ercot/analysis/pool/ERCOT_POOL_STANDINGS.md §0.1 (contamination table and reads), §0.3 (nuclear UNCORRECTED), ruler status line, §7 last paragraph; /Users/yilu/Documents/GitHub/RTS-GMLC-ercot/trial_0826/ercot/analysis/pool/pool_standings.csv (identity_shift_scaled, identity_shift_over_mean_abs_delta_L60/L180); /Users/yilu/Documents/GitHub/RTS-GMLC-ercot/trial_0826/ercot/analysis/pool/pool_identity_shift_smoke.csv. Caps: pool_wavedD_wide.csv gen_pmax (163: 185.4; 274: 746.4).

## Slide 12

E-D1b: fix V1 + E1 now; fill the R and N seats after prompt 52


ERCOT wave D · location read · draft v1 · 2026-11-07

| id | Role | Reason (status; basis) |
| V1 true curtailment | RECOMMENDED OBJECTIVE (V) | Global order 1. LOCATION-INSENSITIVE AT THESE SIZES (S′ 0.06 / 0.14 / 0.29). The size axis; does not separate the six sites; 10–20 % contaminated. |
| E1 total cost | RECOMMENDED OBJECTIVE (E) | Global order 2. LOCATION-SENSITIVE (S′ 0.39 / 0.97 / 1.62; W p 0.002). Survivor of C1. Every Δ WITHIN GAP BOUND. Plan §1.2 pending 52; ~half identity-contaminated. |
| R4 thermal starts | RECOMMENDED (R), PROVISIONAL | Global order 4. LOCATION-SENSITIVE by S′ (1.74 / 1.57 / 3.06) but W p 0.792, monotone 0 / 6, noise-like unit scatter. Δ vs base DOMINATED. Waits for the ruler. |
| N1 congested line-hours | RECOMMENDED (N), PROVISIONAL | Global order 5. LOCATION-SENSITIVE by S′ (1.46 / 2.83 / 2.67) but W p 0.754, monotone 3 / 6. Δ vs base DOMINATED (×4.9). Waits for the ruler. |
| R2 reserve shortfall | GUARDRAIL (survivor) | Plan §1.3 role. LOCATION-SENSITIVE by S′ (3.05 / 1.66 / 1.69; range 120 / 65 / 66 MWh on a 446 MWh base). No smoke information on contamination. |
| X1 CO₂ | REDUNDANT → E1 | Cluster C1 (ρ +0.98; 2 of 3 levels ≥ 0.94). The pinned conflict did not appear. |
| E9 scarcity bus-hours | DEAD ON WAVE D | 0 on 18 / 18 rows (max RT LMP 432 $/MWh < 450). Count, not dead a priori. |

What happens next (no decision here; the PI decides M)
1. base_v3: one full-year run of base_2019_v2 data under identity v3 (≈ 5.3 h wall / 21 core-h on a fast node). It removes the contamination from every Δ column.
2. noise_v3 arm A, then arm B (prompt 52): the ruler. It sizes the chatter behind R4 and N1 and makes the plan §1.2 verdict.
3. One rerun: python pool_standings.py --base extracts/<base_v3>/run_index_1 --noise ercot_noise.json. No other code changes.

**Notes:** Source: /Users/yilu/Documents/GitHub/RTS-GMLC-ercot/trial_0826/ercot/analysis/pool/pool_ed1b_decision.csv (E_D1b_role) and /Users/yilu/Documents/GitHub/RTS-GMLC-ercot/trial_0826/ercot/analysis/pool/ERCOT_POOL_STANDINGS.md §7 (reason column, verbatim numbers), §9 (base_v3), ruler status line (prompt 52). The 'fix V1 + E1 now, fill R / N after 52' line is the strategy-session read of §7's last paragraph.

## Slide 13

Appendix A: Δ-vs-base heatmaps, X1 CO2 (fuel-factor) and E4 total payments (consumer side)


ERCOT wave D · location read · draft v1 · 2026-11-07

X1 CO2 (fuel-factor): REDUNDANT->E1. S′ 0.22 / 0.98 / 1.59; W 0.95, p 1e-04. Δ vs v2 base CONTAMINATED.
/Users/yilu/Documents/GitHub/RTS-GMLC-ercot/trial_0826/ercot/analysis/pool/figs/standings/X1.png

E4 total payments (consumer side): LOCATION-SENSITIVE. S′ 0.54 / 1.22 / 1.24; W 0.62, p 0.070. Δ vs v2 base CONTAMINATED; nuclear cost UNCORRECTED (hatched).
/Users/yilu/Documents/GitHub/RTS-GMLC-ercot/trial_0826/ercot/analysis/pool/figs/standings/E4.png

**Notes:** Figures: /Users/yilu/Documents/GitHub/RTS-GMLC-ercot/trial_0826/ercot/analysis/pool/figs/standings/X1.png
/Users/yilu/Documents/GitHub/RTS-GMLC-ercot/trial_0826/ercot/analysis/pool/figs/standings/E4.png
Captions: /Users/yilu/Documents/GitHub/RTS-GMLC-ercot/trial_0826/ercot/analysis/pool/pool_standings.csv. Δ vs v2 base is CONTAMINATED on every panel (title label).

## Slide 14

Appendix A: Δ-vs-base heatmaps, R2 reserve shortfall and R7 committed capacity-hours


ERCOT wave D · location read · draft v1 · 2026-11-07

R2 reserve shortfall: LOCATION-SENSITIVE. S′ 3.05 / 1.66 / 1.69; W 0.48, p 0.214. Δ vs v2 base CONTAMINATED.
/Users/yilu/Documents/GitHub/RTS-GMLC-ercot/trial_0826/ercot/analysis/pool/figs/standings/R2.png

R7 committed capacity-hours: DIAGNOSTIC. S′ 1.31 / 1.77 / 1.92; W 0.52, p 0.168. Δ vs v2 base CONTAMINATED.
/Users/yilu/Documents/GitHub/RTS-GMLC-ercot/trial_0826/ercot/analysis/pool/figs/standings/R7.png

**Notes:** Figures: /Users/yilu/Documents/GitHub/RTS-GMLC-ercot/trial_0826/ercot/analysis/pool/figs/standings/R2.png
/Users/yilu/Documents/GitHub/RTS-GMLC-ercot/trial_0826/ercot/analysis/pool/figs/standings/R7.png
Captions: /Users/yilu/Documents/GitHub/RTS-GMLC-ercot/trial_0826/ercot/analysis/pool/pool_standings.csv. Δ vs v2 base is CONTAMINATED on every panel (title label).

## Slide 15

Appendix A: Δ-vs-base heatmaps, N4 pocket-120 congested line-hours and N5 congestion spread


ERCOT wave D · location read · draft v1 · 2026-11-07

N4 pocket-120 congested line-hours: LOCATION-SENSITIVE. S′ 0.40 / 0.53 / 1.69; W 0.37, p 0.379. Δ vs v2 base CONTAMINATED.
/Users/yilu/Documents/GitHub/RTS-GMLC-ercot/trial_0826/ercot/analysis/pool/figs/standings/N4.png

N5 congestion spread: LOCATION-INSENSITIVE AT THESE SIZES. S′ 0.36 / 0.45 / 1.08; W 0.54, p 0.134. Δ vs v2 base CONTAMINATED.
/Users/yilu/Documents/GitHub/RTS-GMLC-ercot/trial_0826/ercot/analysis/pool/figs/standings/N5.png

**Notes:** Figures: /Users/yilu/Documents/GitHub/RTS-GMLC-ercot/trial_0826/ercot/analysis/pool/figs/standings/N4.png
/Users/yilu/Documents/GitHub/RTS-GMLC-ercot/trial_0826/ercot/analysis/pool/figs/standings/N5.png
Captions: /Users/yilu/Documents/GitHub/RTS-GMLC-ercot/trial_0826/ercot/analysis/pool/pool_standings.csv. Δ vs v2 base is CONTAMINATED on every panel (title label).

## Slide 16

Appendix A: Δ-vs-base heatmaps, E6 VRE energy payments and R5 start/stop ramping


ERCOT wave D · location read · draft v1 · 2026-11-07

E6 VRE energy payments: LOCATION-INSENSITIVE AT THESE SIZES. S′ 0.18 / 0.72 / 0.39; W 0.59, p 0.090. Δ vs v2 base CONTAMINATED.
/Users/yilu/Documents/GitHub/RTS-GMLC-ercot/trial_0826/ercot/analysis/pool/figs/standings/E6.png

R5 start/stop ramping: LOCATION-SENSITIVE. S′ 2.15 / 1.81 / 1.90; W 0.23, p 0.699. Δ vs v2 base CONTAMINATED.
/Users/yilu/Documents/GitHub/RTS-GMLC-ercot/trial_0826/ercot/analysis/pool/figs/standings/R5.png

**Notes:** Figures: /Users/yilu/Documents/GitHub/RTS-GMLC-ercot/trial_0826/ercot/analysis/pool/figs/standings/E6.png
/Users/yilu/Documents/GitHub/RTS-GMLC-ercot/trial_0826/ercot/analysis/pool/figs/standings/R5.png
Captions: /Users/yilu/Documents/GitHub/RTS-GMLC-ercot/trial_0826/ercot/analysis/pool/pool_standings.csv. Δ vs v2 base is CONTAMINATED on every panel (title label).

## Slide 17

Appendix A: Δ-vs-base heatmaps, N3 flow violation and E2 fixed (commitment) cost


ERCOT wave D · location read · draft v1 · 2026-11-07

N3 flow violation: LOCATION-SENSITIVE. S′ 5.92 / 15.44 / 7.66; W 0.37, p 0.414. Δ vs v2 base CONTAMINATED.
/Users/yilu/Documents/GitHub/RTS-GMLC-ercot/trial_0826/ercot/analysis/pool/figs/standings/N3.png

E2 fixed (commitment) cost: LOCATION-SENSITIVE. S′ 1.70 / 1.12 / 2.09; W 0.47, p 0.232. Δ vs v2 base CONTAMINATED; nuclear cost UNCORRECTED (hatched).
/Users/yilu/Documents/GitHub/RTS-GMLC-ercot/trial_0826/ercot/analysis/pool/figs/standings/E2.png

**Notes:** Figures: /Users/yilu/Documents/GitHub/RTS-GMLC-ercot/trial_0826/ercot/analysis/pool/figs/standings/N3.png
/Users/yilu/Documents/GitHub/RTS-GMLC-ercot/trial_0826/ercot/analysis/pool/figs/standings/E2.png
Captions: /Users/yilu/Documents/GitHub/RTS-GMLC-ercot/trial_0826/ercot/analysis/pool/pool_standings.csv. Δ vs v2 base is CONTAMINATED on every panel (title label).

## Slide 18

Appendix A: Δ-vs-base heatmaps, R6 nominal ramping and N2 congested lines


ERCOT wave D · location read · draft v1 · 2026-11-07

R6 nominal ramping: LOCATION-SENSITIVE. S′ 0.93 / 2.67 / 3.74; W 0.15, p 0.858. Δ vs v2 base CONTAMINATED.
/Users/yilu/Documents/GitHub/RTS-GMLC-ercot/trial_0826/ercot/analysis/pool/figs/standings/R6.png

N2 congested lines: LOCATION-SENSITIVE. S′ 1.80 / 1.20 / 3.00; W 0.12, p 0.901. Δ vs v2 base CONTAMINATED.
/Users/yilu/Documents/GitHub/RTS-GMLC-ercot/trial_0826/ercot/analysis/pool/figs/standings/N2.png

**Notes:** Figures: /Users/yilu/Documents/GitHub/RTS-GMLC-ercot/trial_0826/ercot/analysis/pool/figs/standings/R6.png
/Users/yilu/Documents/GitHub/RTS-GMLC-ercot/trial_0826/ercot/analysis/pool/figs/standings/N2.png
Captions: /Users/yilu/Documents/GitHub/RTS-GMLC-ercot/trial_0826/ercot/analysis/pool/pool_standings.csv. Δ vs v2 base is CONTAMINATED on every panel (title label).

## Slide 19

Appendix A: Δ-vs-base heatmaps, E3 variable cost and R8 committed unit-hours


ERCOT wave D · location read · draft v1 · 2026-11-07

E3 variable cost: LOCATION-SENSITIVE. S′ 0.61 / 0.88 / 1.62; W 0.57, p 0.112. Δ vs v2 base CONTAMINATED; nuclear cost UNCORRECTED (hatched).
/Users/yilu/Documents/GitHub/RTS-GMLC-ercot/trial_0826/ercot/analysis/pool/figs/standings/E3.png

R8 committed unit-hours: DIAGNOSTIC. S′ 1.80 / 2.83 / 2.05; W 0.53, p 0.146. Δ vs v2 base CONTAMINATED.
/Users/yilu/Documents/GitHub/RTS-GMLC-ercot/trial_0826/ercot/analysis/pool/figs/standings/R8.png

**Notes:** Figures: /Users/yilu/Documents/GitHub/RTS-GMLC-ercot/trial_0826/ercot/analysis/pool/figs/standings/E3.png
/Users/yilu/Documents/GitHub/RTS-GMLC-ercot/trial_0826/ercot/analysis/pool/figs/standings/R8.png
Captions: /Users/yilu/Documents/GitHub/RTS-GMLC-ercot/trial_0826/ercot/analysis/pool/pool_standings.csv. Δ vs v2 base is CONTAMINATED on every panel (title label).

## Slide 20

Appendix A: Δ-vs-base heatmaps, E7 mean settlement price (energy) and E8 LMP dispersion


ERCOT wave D · location read · draft v1 · 2026-11-07

E7 mean settlement price (energy): DIAGNOSTIC. S′ 0.31 / 0.50 / 1.00; W 0.82, p 0.005. Δ vs v2 base CONTAMINATED; nuclear cost UNCORRECTED (hatched).
/Users/yilu/Documents/GitHub/RTS-GMLC-ercot/trial_0826/ercot/analysis/pool/figs/standings/E7.png

E8 LMP dispersion: LOCATION-SENSITIVE. S′ 1.57 / 3.27 / 2.41; W 0.23, p 0.699. Δ vs v2 base CONTAMINATED.
/Users/yilu/Documents/GitHub/RTS-GMLC-ercot/trial_0826/ercot/analysis/pool/figs/standings/E8.png

**Notes:** Figures: /Users/yilu/Documents/GitHub/RTS-GMLC-ercot/trial_0826/ercot/analysis/pool/figs/standings/E7.png
/Users/yilu/Documents/GitHub/RTS-GMLC-ercot/trial_0826/ercot/analysis/pool/figs/standings/E8.png
Captions: /Users/yilu/Documents/GitHub/RTS-GMLC-ercot/trial_0826/ercot/analysis/pool/pool_standings.csv. Δ vs v2 base is CONTAMINATED on every panel (title label).

## Slide 21

Appendix A: Δ-vs-base heatmaps, E9 scarcity bus-hours and V2 renewables penetration


ERCOT wave D · location read · draft v1 · 2026-11-07

E9 scarcity bus-hours: DEAD ON WAVE D. S′ nan / nan / nan; W 0.00, p 1.000. Δ vs v2 base CONTAMINATED.
/Users/yilu/Documents/GitHub/RTS-GMLC-ercot/trial_0826/ercot/analysis/pool/figs/standings/E9.png

V2 renewables penetration: REDUNDANT->E1. S′ 0.28 / 1.04 / 1.68; W 0.97, p 3e-05. Δ vs v2 base CONTAMINATED.
/Users/yilu/Documents/GitHub/RTS-GMLC-ercot/trial_0826/ercot/analysis/pool/figs/standings/V2.png

**Notes:** Figures: /Users/yilu/Documents/GitHub/RTS-GMLC-ercot/trial_0826/ercot/analysis/pool/figs/standings/E9.png
/Users/yilu/Documents/GitHub/RTS-GMLC-ercot/trial_0826/ercot/analysis/pool/figs/standings/V2.png
Captions: /Users/yilu/Documents/GitHub/RTS-GMLC-ercot/trial_0826/ercot/analysis/pool/pool_standings.csv. Δ vs v2 base is CONTAMINATED on every panel (title label).

## Slide 22

Appendix A: Δ-vs-base heatmaps, V3 PEM-twin delivered share and D1 H2 electricity


ERCOT wave D · location read · draft v1 · 2026-11-07

V3 PEM-twin delivered share: DIAGNOSTIC. S′ 0.54 / 1.37 / 2.04; W 0.94, p 2e-04. Δ vs v2 base CONTAMINATED.
/Users/yilu/Documents/GitHub/RTS-GMLC-ercot/trial_0826/ercot/analysis/pool/figs/standings/V3.png

D1 H2 electricity: DIAGNOSTIC. S′ 0.11 / 0.42 / 0.83; W 1.00, p 2e-06. Δ vs v2 base CONTAMINATED.
/Users/yilu/Documents/GitHub/RTS-GMLC-ercot/trial_0826/ercot/analysis/pool/figs/standings/D1.png

**Notes:** Figures: /Users/yilu/Documents/GitHub/RTS-GMLC-ercot/trial_0826/ercot/analysis/pool/figs/standings/V3.png
/Users/yilu/Documents/GitHub/RTS-GMLC-ercot/trial_0826/ercot/analysis/pool/figs/standings/D1.png
Captions: /Users/yilu/Documents/GitHub/RTS-GMLC-ercot/trial_0826/ercot/analysis/pool/pool_standings.csv. Δ vs v2 base is CONTAMINATED on every panel (title label).

## Slide 23

Appendix A: Δ-vs-base heatmaps, D2 PEM utilization


ERCOT wave D · location read · draft v1 · 2026-11-07

D2 PEM utilization: DIAGNOSTIC. S′ 0.77 / 1.52 / 2.00; W 1.00, p 2e-06. Δ vs v2 base CONTAMINATED.
/Users/yilu/Documents/GitHub/RTS-GMLC-ercot/trial_0826/ercot/analysis/pool/figs/standings/D2.png

**Notes:** Figures: /Users/yilu/Documents/GitHub/RTS-GMLC-ercot/trial_0826/ercot/analysis/pool/figs/standings/D2.png
Captions: /Users/yilu/Documents/GitHub/RTS-GMLC-ercot/trial_0826/ercot/analysis/pool/pool_standings.csv. Δ vs v2 base is CONTAMINATED on every panel (title label).

## Slide 24

Appendix B: wall-clock and core-hours, two node-speed groups


ERCOT wave D · location read · draft v1 · 2026-11-07

| Group | Rows | n | Wall h | Core-h (4 slots) | RUC median solve s | RUC max solve s |
| A (fast) | 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 20, 21 | 15 | 5.12 – 5.48 | 20.5 – 21.9 (mean 21.1) | 19.5 – 22.8 | 207 – 450 |
| B (slow) | 14, 15, 16, 17, 18, 19 | 6 | 10.52 – 11.84 | 42.1 – 47.3 (mean 44.6) | 46.4 – 55.8 | 477 – 1,267 |
| Total | 1–21 | 21 | 146 (sum) | 584 |  |  |

•  The same designs sit in both groups (site 110: L60 in A, L120 / L180 in B) and the per-day RUC median solve time doubles with the wall time. The split is node speed, not problem size. Node groups are inferred: the extracts carry no host names.
•  The array finished in 11.8 h of calendar time. Per full-year v3 run on a fast node: ≈ 5.3 h wall / 21 core-h.
•  Row 19 (nuclear L60, slow node) has one RUC day at 1,267 s with status OPTIMAL and n_ruc_time_limit = 0: the solve-time column includes model build. 0 TIME_LIMIT statuses on 7,665 RUCs.
•  The plan's 'v2 plausibly 12–25 core-h' bracket holds for v3 on fast nodes; the January-day projection (8–10 h / 32–40 core-h) was pessimistic.

**Notes:** Source: /Users/yilu/Documents/GitHub/RTS-GMLC-ercot/trial_0826/ercot/analysis/pool/pool_wavedD_wallclock.csv (wall_h, core_h, node_group, RUC solve times) and /Users/yilu/Documents/GitHub/RTS-GMLC-ercot/trial_0826/ercot/analysis/pool/ERCOT_POOL_STANDINGS.md §8. Raw stamps: /Users/yilu/Documents/GitHub/RTS-GMLC-ercot/trial_0826/ercot/extracts/location_oat_v2/wallclock.csv.

