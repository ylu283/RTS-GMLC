# ERCOT objective-pool standings on wave D — prompt 57 Part B

**Date:** 2026-11-07. **Branch:** `ercot/tx123` (HEAD at run time
`304335c`). **Definitions freeze commit:** `f76d897`
(`pool_definitions.json`; asserted byte-identical against that commit at
every run). **Data:** wave D `extracts/location_oat_v2` (21 rows: 6 WIND
sites × 3 absolute MW levels 60 / 120 / 180 MW + nuclear gen 1 at the same
3 levels; all `--full`; 0 SUSPECT rows; 7,665 / 7,665 RUCs OPTIMAL).
**Identity line:** wave D ran under identity **v3** (`ruc_mipgap 0.001`,
`ruc_time_limit 1200 s`; `GAP_DECISION_used.json`, E-D6). The base
`base_2019_v2:1` is an identity **v2** run (gap 0.01 / TL 120). No v3 base
exists. **No PCM simulation ran for this document.** Script:
`pool_standings.py` (one command; `--base <dir>` re-runs against a v3
base; `--noise ercot_noise.json` fills the ruler columns when prompt 52
lands).

**Honesty clause (pinned, verbatim).** 18–21 one-at-a-time rows, 3
levels, no interactions; the RTS verdicts rested on 15 pair grids of 81
cells. Every pooled statistic is also given per level. No multiplicity
correction is applied: the verdicts are pinned threshold reads on a
deterministic instrument, not tests. Of the ~22 graded candidates, about
one W p-value below 0.05 is expected under exchangeable site labels, and
about 0.05 false redundancy clusters among 231 pairs; W does not enter
any verdict. A false LOCATION-SENSITIVE call admits one more candidate to
the PI table, so the error direction is permissive, not conservative; the
table therefore carries range_jℓ / ruler_j at every level, never the
label alone.

**Ruler status: RULER PENDING (52).** Prompt 52 (`noise_v3`) has not
landed. Every ruler column is a placeholder. No readability verdict in the
sense of §3 A4 is made. The primary location read is the base-free
scale-free ratio S′ (section 0.2); the secondary read is S (§3 A4b),
which needs a base and is contaminated.

## RERUN 2026-11-17 — v3 base (`base_v3:1`) + prompt-52 ruler (`ercot_noise.json`); objective-selection study for E-D1b

**Run:** `/opt/anaconda3/bin/python pool_standings.py --base extracts/base_v3/run_index_1
--noise analysis/noise_v3/ercot_noise.json` on branch `ercot/54-gp-loader` (base
`ercot/tx123` 80e5d79), by the prompt-54 session on the strategy session's
instruction (Kay). **Data read:** wave D rows 1–21 and `base_v3:1` only —
no n0_E / random_E value was read. The 11-07 text below is kept verbatim as the
provisional record; this block states what the two new inputs change. Code
change (own commit `eb846a0`, disclosed): `pool_standings.py` hard-coded the
label `CONTAMINATED (v2 base, v3 rows)` in the per-level rows, the gap-bound
rows and the heatmap titles regardless of `--base`; the computed label is now
threaded through (`same identity (v3)`). No number changed by that edit.
Outputs refreshed in place: `pool_standings.csv`, `pool_standings_levels.csv`,
`pool_wavedD_delta.csv`, `pool_gap_bound_wavedD.csv`, `pool_ed1b_decision.csv`,
`pool_clusters_wavedD.json`, `pool_starts_attribution_wavedD.csv`, 25 heatmaps
under `figs/standings/` (clustermaps unchanged: base-free). `pool_wavedD_wide.csv`
is byte-identical (raw values are base-free).

### R.1 What changed

1. **The CONTAMINATED caveat (0.1) is LIFTED.** Base and rows are both identity
   v3 (`delta label: same identity (v3)`). Every Δ-vs-base column is now a PEM
   effect, not an identity shift. The secondary read S (0.2) is clean and
   agrees with S′ on every verdict except E3 (S′ LOCATION-SENSITIVE 0.61 / 0.88 /
   1.62; S SIZE-DRIVEN 0.47 / 0.44 / 0.71) and N4 (S′ 0.40 / 0.53 / 1.69; S
   0.28 / 0.34 / 0.70). The `identity_shift_*` columns are retained only as the
   v2→v3 size reference from the gap smoke; with a v3 base they are no longer a
   contamination read (ratios such as E2 55 / 80 compare the identity shift to
   small PEM effects and mean nothing here).
2. **The ruler columns are FILLED (prompt 52, `per_candidate.<id>.ruler` =
   median |Δ| of the 8 perturbed copies, 0.1 % MW moves).** The three-way
   verdict (`range_jℓ ≥ 2 × ruler_j` at ≥ 2 of 3 levels → LOCATION-SENSITIVE;
   < 1 at every level → INSENSITIVE AT THESE SIZES; else UNREADABLE) reads
   **LOCATION-SENSITIVE for every candidate with a ruler** (range / ruler in
   the table below), RULER=0 for E9 (dead) and N2 (no read; status by S′),
   so the 11-07 "provisional on the ruler" sentence for R4 / N1 is resolved:
   their between-site spread is 5–14 rulers at every level, far above the
   solver-indifference chatter the perturbed copies measure. Their site
   ORDER is still unstable (W p 0.79 / 0.75): a real, non-monotone location
   effect, not chatter.
3. **Sign and monotonicity on the v3 base** (`sign_pattern_sites`): V1 `------`
   (6 / 6, monotone 6 / 6); E1 `++++++` (PEM RAISES total cost vs the v3
   base, +$3.8M … +$14.1M; the 11-07 negative Δ were the v2→v3 identity
   shift); E3 `++++++`; E2 `mm----` (4 / 6, −$2.0M … +$0.7M); R4 `---mm-`
   (4 / 6; −246 … +49 starts; monotone 0 / 6); N1 `m+m-mm` (2 / 6; −63 … +102
   line-h; monotone 3 / 6); R2 `-m-mm-` (−97 … +23 MWh); N4 `------` (−183 …
   −72 h, monotone 3 / 6). E8 / N5 / D2: S undefined (no base value for E8 /
   N5 on the slim-only path of `pool_row`; D2 has no base) — S′ carries them.
4. **Cost gap bound on the v3 base (section 2 superseded):** G_base(v3) =
   **$18.7M** (was $196.7M on v2); wave-D G_row $18.4–25.1M; pair bound
   vs base $37.1–43.8M raw (G_base share 43–50 %, no longer dominated by the
   base), $8.75–10.3M scaled. **E1: 0 / 18 GAP-READABLE raw, 8 / 18 scaled**
   (L120: 110, 270, 274; L180: 110, 140, 146, 270, 274 — site 163 never);
   E3 8 / 18 scaled; E2 0 / 18. Between-site ranges ($2.2 / 5.5 / 9.2M for E1)
   stay WITHIN the v3-only pair bound at every level, raw ($41–48M) and
   scaled ($9.7–11.4M; L180 at 95 %). Plan §1.2 is settled separately
   (ERCOT_NOISE.md §5c: READABLE → E1); G stays an evidence column.
5. **Redundancy (section 4) is unchanged** (base-free): cluster C1 = {E1, V2,
   X1}, survivor E1; redundant pairs V2–E1, V2–X1, E1–X1, V2–E3; E1–X1 +0.98
   (the pinned conflict did not appear). **Conflicts (section 6) unchanged**:
   16 survivors; V1–E1 −0.70 and E1–R4 −0.53 TRADE-OFF (size); V1–E4 −0.85,
   V1–N5 −0.93, E1–R2 −0.62, E1–N4 −0.77, E4–N4, N4–N5, N4–E3, R5–E2
   TRADE-OFF (location). Among the recommended four: V1–E1 size, E1–R4 size,
   E1–N1 −0.26 (not labelled), V1–R4 +0.34, V1–N1 +0.53, R4–N1 +0.02.

### R.2 Step 1 with the ruler (18 VRE rows; `pool_standings.csv`)

| id | S′ verdict | range / ruler L60 / L120 / L180 | ruler_j | ruler verdict | W, exact p | status |
|---|---|---|---|---|---|---|
| V1 true curt | SIZE-DRIVEN (0.06 / 0.14 / 0.29) | 11.6 / 27.1 / 54.6 | 1,949 MWh | LOCATION-SENSITIVE | 0.72, 0.025 | **LOCATION-SENSITIVE** (ruler); size-driven by S′ |
| E1 total cost | LOCATION-SENSITIVE (0.39 / 0.97 / 1.62) | 10.1 / 25.2 / 42.2 | $218k | LOCATION-SENSITIVE | 0.87, 0.0018 | **LOCATION-SENSITIVE** |
| E2 fixed cost | LOCATION-SENSITIVE (1.70 / 1.12 / 2.09) | 3.0 / 2.0 / 3.7 | $656k | LOCATION-SENSITIVE | 0.47, 0.23 | LOCATION-SENSITIVE |
| E3 variable cost | LOCATION-SENSITIVE (0.61 / 0.88 / 1.62) | 3.5 / 5.0 / 9.3 | $851k | LOCATION-SENSITIVE | 0.57, 0.11 | LOCATION-SENSITIVE |
| E4 total payments | LOCATION-SENSITIVE (0.54 / 1.22 / 1.24) | 6.3 / 14.2 / 14.5 | $1.24M | LOCATION-SENSITIVE | 0.62, 0.070 | LOCATION-SENSITIVE |
| E6 VRE payments | SIZE-DRIVEN (0.18 / 0.72 / 0.39) | 1.4 / 5.6 / 3.1 | $552k | LOCATION-SENSITIVE | 0.59, 0.090 | LOCATION-SENSITIVE (ruler); size-driven by S′ |
| E8 LMP dispersion | LOCATION-SENSITIVE (1.57 / 3.27 / 2.41) | 2.9 / 6.0 / 4.4 | 0.073 $/MWh | LOCATION-SENSITIVE | 0.23, 0.70 | LOCATION-SENSITIVE |
| E9 scarcity bus-h | NO EFFECT | — | 0 (RULER=0) | UNREADABLE | — | DEAD ON WAVE D |
| R2 reserve shortfall | LOCATION-SENSITIVE (3.05 / 1.66 / 1.69) | 5.2 / 2.8 / 2.9 | 23.1 MWh | LOCATION-SENSITIVE | 0.48, 0.21 | LOCATION-SENSITIVE (guardrail) |
| R4 thermal starts | LOCATION-SENSITIVE (1.74 / 1.57 / 3.06) | 7.7 / 6.9 / 13.5 | 20 starts | LOCATION-SENSITIVE | 0.19, 0.79 | **LOCATION-SENSITIVE** (order unstable) |
| R5 on/off ramps | LOCATION-SENSITIVE (2.15 / 1.81 / 1.90) | 3.7 / 3.1 / 3.3 | 2,896 MW | LOCATION-SENSITIVE | 0.23, 0.70 | LOCATION-SENSITIVE |
| R6 nominal ramps | LOCATION-SENSITIVE (0.93 / 2.67 / 3.74) | 3.5 / 10.1 / 14.1 | 9,842 MW | LOCATION-SENSITIVE | 0.15, 0.86 | LOCATION-SENSITIVE |
| N1 congested line-h | LOCATION-SENSITIVE (1.46 / 2.83 / 2.67) | 4.9 / 9.4 / 8.9 | 15 line-h | LOCATION-SENSITIVE | 0.20, 0.75 | **LOCATION-SENSITIVE** (order unstable) |
| N2 congested lines | LOCATION-SENSITIVE (1.80 / 1.20 / 3.00) | — | 0 (RULER=0) | LOCATION-SENSITIVE (natural-unit rule) | 0.12, 0.90 | LOCATION-SENSITIVE |
| N3 flow violation | LOCATION-SENSITIVE (5.9 / 15.4 / 7.7) | 2.3 / 5.9 / 2.9 | 2.58 MWh | LOCATION-SENSITIVE | 0.37, 0.41 | LOCATION-SENSITIVE |
| N4 pocket-120 line-h | LOCATION-SENSITIVE (0.40 / 0.53 / 1.69) | 2.8 / 3.8 / 12.0 | 8.5 line-h | LOCATION-SENSITIVE | 0.37, 0.38 | LOCATION-SENSITIVE |
| N5 congestion spread | SIZE-DRIVEN (0.36 / 0.45 / 1.08) | 4.3 / 5.3 / 12.8 | 0.040 $/MWh | LOCATION-SENSITIVE | 0.54, 0.13 | LOCATION-SENSITIVE (ruler); size-driven by S′ |
| X1 CO2 | LOCATION-SENSITIVE (0.22 / 0.98 / 1.59) | 10.3 / 45.3 / 73.6 | 4,359 t | LOCATION-SENSITIVE | 0.95, 1.4e-4 | REDUNDANT→E1 |
| V2 penetration | LOCATION-SENSITIVE (0.28 / 1.04 / 1.68) | 37 / 138 / 223 | 4.7e-4 pts | LOCATION-SENSITIVE | 0.97, 3e-5 | REDUNDANT→E1 |
| V3, E7, R7, R8, D1, D2 | (rulers filled; see csv) | | | | | DIAGNOSTIC (`—`) |
| E5, R1, R3 | | | 0 | | | DEAD (0 on 31 v2 runs, wave D and base_v3) |

Reading note: the prompt-52 ruler is a SENSITIVITY ruler (median |Δ| under
0.1 % MW moves, 8 values on 4 off-slate designs), so "LOCATION-SENSITIVE by
ruler" means the between-site spread exceeds the solver's input-chatter by a
wide margin; it does not by itself say the spread is large relative to the
size effect — that is S′, which still separates the size-driven renewables
quantities (V1, E6, N5, D1) from the location-sensitive rest.

### R.3 E-D1b decision table, RERUN (one page; PI decides) — `pool_ed1b_decision.csv`

Rule (f76d897): recommended ≤ 4 objectives = the survivors in the global
order with at most one per family. Both new inputs leave the recommended
four unchanged; what changes is their qualification.

| id | role (RERUN) | 11-07 role | what the v3 base + ruler changed |
|---|---|---|---|
| **V1** true curtailment | RECOMMENDED OBJECTIVE (V) | RECOMMENDED | contamination lifted (10–20 % → 0); ruler 1,949 MWh, spread 12–55 rulers; still SIZE-DRIVEN by S′ (does not separate the six sites at 60–180 MW) |
| **E1** total cost | RECOMMENDED OBJECTIVE (E) | RECOMMENDED | plan §1.2 verdict READABLE (ERCOT_NOISE.md) → the E seat is E1; sign now + vs the v3 base (+$3.8–14.1M); 8 / 18 single-site Δ GAP-READABLE under the scaled v3 pair bound (0 / 18 on 11-07); site order stable (W p 0.002) |
| X1 CO2 | REDUNDANT → E1 | REDUNDANT → E1 | unchanged (ρ +0.98; base-free) |
| **R4** thermal starts | RECOMMENDED OBJECTIVE (R) — **no longer provisional on the ruler** | RECOMMENDED, PROVISIONAL | spread 7.7 / 6.9 / 13.5 rulers (ruler 20 starts); Δ vs v3 base −246 … +49 (the 11-07 "DOMINATED by the identity shift" read was the v2 base); site order unstable (W p 0.79), monotone 0 / 6 — a real but non-monotone location effect |
| **N1** congested line-hours | RECOMMENDED OBJECTIVE (N) — **no longer provisional on the ruler** | RECOMMENDED, PROVISIONAL | spread 4.9 / 9.4 / 8.9 rulers (ruler 15 line-h); Δ vs v3 base −63 … +102; W p 0.75, monotone 3 / 6 |
| E4 total payments | SURVIVOR (family E taken) | SURVIVOR | 6–15 rulers; sign mixed (`+mmmmm`) on the v3 base; no gap bound |
| R2 reserve shortfall | GUARDRAIL (survivor) | GUARDRAIL | 3–5 rulers; Δ −97 … +23 MWh vs the v3 base 156 MWh (plan §1.3 flag at 2 × base = 312 MWh: never approached on wave D) |
| N4 pocket-120 line-h | SURVIVOR (family N taken) | SURVIVOR | 2.8 / 3.8 / 12.0 rulers; Δ −183 … −72 h, sign-consistent 6 / 6 (PEM relieves the L252 pocket at every site) |
| N5, E6 | SURVIVOR (size-driven by S′) | SURVIVOR | ruler-readable but size-driven |
| R5, N3, E2, R6, N2, E3, E8 | SURVIVOR (family taken) | SURVIVOR | all ruler-readable; E2 / E3 within the gap bound on the v3 base (E3 8 / 18 scaled-readable) |
| R7, R8, V3, E7, D1, D2 | DIAGNOSTIC | DIAGNOSTIC | unchanged |
| E9 | DEAD ON WAVE D | DEAD ON WAVE D | unchanged (RULER=0) |
| E5, R1, R3 | DEAD | DEAD | 0 on base_v3 too; R1 stays the plan §1.3 guardrail |

What the PI should weigh now: all four recommended seats are readable above
the prompt-52 chatter and clean of identity contamination. V1 and E1 have a
stable site order; R4 and N1 have large, readable but non-monotone,
order-unstable location effects — they are legitimate objectives whose
optimum will not be a simple "more MW" or "this site" story. The honest
alternative of 11-07 (fix V1 + E1 now, fill R / N later) is no longer
forced by the ruler; it would now rest only on the order instability. The
standings do not decide. The strategy session drafts E-D1b from this table;
the GP fit (prompt 54 Part B step 1) starts after Kay's word and a dated
`design_space_E.json`.

---

## 0. Two caveats that govern every number below

### 0.1 Base contamination is MATERIAL: `CONTAMINATED (v2 base, v3 rows)`

Every Δ column is value(v3 row) − value(v2 base). The gap smoke
(`analysis/gap_smoke/GAP_SMOKE.md` §2, task 2 − task 1, 3 January days)
measured what the identity change alone does. The table scales the
3-day shift × 365/3 for extensive (annual-sum) candidates and reports the
raw 3-day difference for intensive ones. The last two columns divide the
scaled shift by the mean wave-D |Δ| at L60 and L180: a ratio near or above
1 means the identity change alone can account for the whole Δ vs base.
The scaling is a size indication from three winter days, not a year
estimate (GAP_SMOKE §6); a ratio above 1 therefore reads "the identity
shift is at least comparable to the effect", not "larger than".
File: `pool_identity_shift_smoke.csv`.

| id | 3-day shift (0.001 − 0.01) | scaled | \|shift\| / mean \|Δ\| L60 | L180 | read |
|---|---|---|---|---|---|
| V1 true curtailment | −557 MWh | −67.7 GWh/yr | 0.22 | 0.10 | 10–20 % contaminated |
| V2 penetration | +0.017 pts | raw | 0.52 | 0.18 | contaminated at L60 |
| E1 total cost | −$89.5k | −$10.9M/yr | 0.44 | 0.57 | about half identity |
| E2 fixed cost | −$547k | −$66.6M/yr | 1.03 | 1.05 | DOMINATED |
| E3 variable cost | +$458k | +$55.7M/yr | 1.40 | 1.25 | DOMINATED |
| E4 total payments | −$40.4k | −$4.9M/yr | 2.77 | 0.31 | dominated at L60 |
| E6 VRE payments | +$1.7k | +$0.2M/yr | 0.04 | 0.02 | clean |
| E7 settlement price | −0.002 $/MWh | raw | 0.04 | 0.02 | clean |
| E8 LMP dispersion | −0.77 $/MWh | raw | 1.03 | 1.03 | DOMINATED |
| R2 reserve shortfall | 0 (none in 3 days) | no smoke information | — | — | unknown |
| R4 thermal starts | −16 | −1,947/yr | 3.24 | 2.87 | DOMINATED |
| R5 on/off ramps | −751 MW | −91.4k MW/yr | 1.36 | 1.32 | DOMINATED |
| R6 nominal ramps | −5,943 MW | −723k MW/yr | 1.00 | 0.98 | DOMINATED |
| R7 committed MWh | −43.8k | −5.33M MWh/yr | 1.33 | 1.39 | DOMINATED |
| R8 committed unit-h | +3 | +365/yr | 0.05 | 0.06 | clean |
| N1 congested line-h | −8 | −973/yr | 4.85 | 3.96 | DOMINATED |
| N2 congested lines | −2 | raw | 0.75 | 0.67 | contaminated |
| N3 flow violation | 0 (none in 3 days) | no smoke information | — | — | unknown |
| N4 pocket-120 line-h | 0 (29 = 29) | no smoke information | — | — | unknown |
| N5 congestion spread | −0.67 $/MWh | raw | 1.79 | 0.79 | DOMINATED |
| X1 CO2 | −235 t | −28.5 kt/yr | 0.17 | 0.08 | clean |
| D1 H2 (twin) | 0 (no twin on base) | — | — | — | n/a |

Consequences, applied throughout: (a) every Δ-vs-base column carries the
label `CONTAMINATED (v2 base, v3 rows)`; (b) S (needs a base) is reported
and flagged; the primary scale-free read is base-free (0.2); (c)
range_jℓ, Kendall's W, every Spearman ρ, the clusters and the conflict
labels are base-invariant (a constant shift changes no rank and no
range) and are stated once here as clean; (d) the first recommendation of
this document (section 9) is to buy ONE v3 base run.

### 0.2 Scale-free reads S′ (primary, base-free) and S (secondary, contaminated)

- S′_jℓ = range_jℓ / mean_site |x_j(site, L180) − x_j(site, L60)|: the
  between-site spread at level ℓ relative to the within-wave size effect
  (60 → 180 MW at the same site). No base enters. Verdict
  `LOCATION-SENSITIVE (scale-free)` iff S′ ≥ 0.5 at ≥ 2 of 3 levels;
  `SIZE-DRIVEN (scale-free)` iff S′ < 0.5 at ≥ 2 of 3 levels; `NO
  EFFECT` when the size effect is 0.
- S_jℓ = range_jℓ / mean_site |Δ_jℓ| (§3 A4b, pinned at f76d897): same
  thresholds; the denominator is the contaminated Δ vs the v2 base. Where
  the identity shift dominates the Δ (E2, E3, R4–R7, N1, E8) S is pushed
  toward 0 and reads SIZE-DRIVEN for the wrong reason. S′ is used for the
  status column; S is shown beside it.

### 0.3 Nuclear stratum (rows 19–21): overlay only; cost family UNCORRECTED

Rows 19–21 (gen 1, formulation A thermal patch, 60 / 120 / 180 MW) never
enter range, S, S′, W, ρ, clusters or conflicts. Their Δ values are listed
as `nuc_delta_<level>` and overlaid on the heatmaps, except the cost
family: E1–E4 and E7 on nuclear rows show Δ total cost −$383M / −$366M /
−$349M vs base, which is NOT a PEM effect. The thermal patch rewrites the
nuclear cost curve (zero at p_min), so raw cost on nuclear rows is not
comparable without the synthetic-bid accounting (RTS g1 = K_raw − K_syn;
ERCOT analogue pre-registered in `analysis/selection/ERCOT_SELECTION.md`
§7). Those cells carry the tag `UNCORRECTED (nuclear cost curve rewritten
by the patch; K_syn accounting pending)` and are hatched on the heatmaps.
No correction was attempted here (what it needs: section 12, item 6).
Curtailment, congestion, reserve, starts and H2 on nuclear rows are
overlaid as they are. Nuclear D1 (thermal-rule h2) is NaN: `thermal.csv.gz`
stayed on CRC and `pool_full_metrics.json` carries no h2 (section 12,
item 4).

## 1. Step 1 — location sensitivity (18 VRE rows; ruler PENDING)

Status is set by S′ (base-free) because the ruler is pending; the ruler
three-way verdict (`LOCATION-SENSITIVE` / `LOCATION-INSENSITIVE AT THESE
SIZES` / `UNREADABLE AT THIS SIZE` on range_jℓ ≥ 2 × ruler_j) is a
separate column, `RULER PENDING (52)` on every row. Kendall's W (k = 6
sites, n = 3 level blocks) uses the raw wave-D values, exact permutation p
over all 720² relative permutations (518,400; judge 1 fixed); W is a
descriptor and enters no verdict. Full table: `pool_standings.csv`;
per-site values: `pool_standings_levels.csv`; heatmaps:
`figs/standings/<id>.png`.

| id | status | range L60 / L120 / L180 | S′ L60 / L120 / L180 | S (contam.) L60 / L120 / L180 | W, exact p |
|---|---|---|---|---|---|
| V1 true curt (MWh) | LOCATION-INSENSITIVE AT THESE SIZES | 22.5k / 52.8k / 106k | 0.06 / 0.14 / 0.29 | 0.07 / 0.11 / 0.16 | 0.72, 0.025 |
| V2 penetration (pts) | REDUNDANT→E1 | 0.018 / 0.065 / 0.105 | 0.28 / 1.04 / 1.68 | 0.53 / 0.90 / 1.10 | 0.97, 3e-5 |
| V3 twin share (—) | DIAGNOSTIC | 1.5e-4 / 3.9e-4 / 5.8e-4 | 0.54 / 1.37 / 2.04 | 0.51 / 0.81 / 0.99 | 0.94, 2e-4 |
| E1 total cost ($) | LOCATION-SENSITIVE | 2.20M / 5.51M / 9.21M | 0.39 / 0.97 / 1.62 | 0.09 / 0.26 / 0.48 | 0.87, 0.0018 |
| E2 fixed cost ($) | LOCATION-SENSITIVE | 1.99M / 1.32M / 2.45M | 1.70 / 1.12 / 2.09 | 0.03 / 0.02 / 0.04 | 0.47, 0.23 |
| E3 variable cost ($) | LOCATION-SENSITIVE | 2.97M / 4.29M / 7.88M | 0.61 / 0.88 / 1.62 | 0.07 / 0.10 / 0.18 | 0.57, 0.11 |
| E4 total payments ($) | LOCATION-SENSITIVE | 7.79M / 17.6M / 17.9M | 0.54 / 1.22 / 1.24 | 4.39 / 1.91 / 1.14 | 0.62, 0.070 |
| E6 VRE payments ($) | LOCATION-INSENSITIVE AT THESE SIZES | 0.77M / 3.11M / 1.70M | 0.18 / 0.72 / 0.39 | 0.15 / 0.46 / 0.18 | 0.59, 0.090 |
| E7 settlement price (—) | DIAGNOSTIC | 0.012 / 0.019 / 0.039 | 0.31 / 0.50 / 1.00 | 0.21 / 0.25 / 0.41 | 0.82, 0.005 |
| E8 LMP dispersion ($/MWh) | LOCATION-SENSITIVE | 0.21 / 0.44 / 0.32 | 1.57 / 3.27 / 2.41 | 0.28 / 0.66 / 0.43 | 0.23, 0.70 |
| E9 scarcity bus-h | DEAD ON WAVE D (0 on 18 / 18; max RT LMP 432 < 450) | 0 / 0 / 0 | — | — | — |
| R2 reserve shortfall (MWh) | LOCATION-SENSITIVE | 120 / 65 / 66 | 3.05 / 1.66 / 1.69 | 0.38 / 0.21 / 0.20 | 0.48, 0.21 |
| R4 thermal starts | LOCATION-SENSITIVE | 153 / 138 / 270 | 1.74 / 1.57 / 3.06 | 0.25 / 0.23 / 0.40 | 0.19, 0.79 |
| R5 on/off ramps (MW) | LOCATION-SENSITIVE | 10.7k / 9.0k / 9.4k | 2.15 / 1.81 / 1.90 | 0.16 / 0.13 / 0.14 | 0.23, 0.70 |
| R6 nominal ramps (MW) | LOCATION-SENSITIVE | 34.7k / 99.5k / 139k | 0.93 / 2.67 / 3.74 | 0.05 / 0.14 / 0.19 | 0.15, 0.86 |
| R7 committed MWh (—) | DIAGNOSTIC | 217k / 294k / 319k | 1.31 / 1.77 / 1.92 | 0.05 / 0.07 / 0.08 | 0.52, 0.17 |
| R8 committed unit-h (—) | DIAGNOSTIC | 882 / 1,388 / 1,006 | 1.80 / 2.83 / 2.05 | 0.13 / 0.21 / 0.16 | 0.53, 0.15 |
| N1 congested line-h | LOCATION-SENSITIVE | 73 / 141 / 133 | 1.46 / 2.83 / 2.67 | 0.36 / 0.62 / 0.54 | 0.20, 0.75 |
| N2 congested lines | LOCATION-SENSITIVE | 3 / 2 / 5 | 1.80 / 1.20 / 3.00 | 1.13 / 0.80 / 1.67 | 0.12, 0.90 |
| N3 flow violation (MWh) | LOCATION-SENSITIVE | 5.9 / 15.3 / 7.6 | 5.9 / 15.4 / 7.7 | 0.08 / 0.20 / 0.10 | 0.37, 0.41 |
| N4 pocket-120 line-h | LOCATION-SENSITIVE | 24 / 32 / 102 | 0.40 / 0.53 / 1.69 | 0.20 / 0.25 / 0.57 | 0.37, 0.38 |
| N5 congestion spread ($/MWh) | LOCATION-INSENSITIVE AT THESE SIZES | 0.17 / 0.21 / 0.51 | 0.36 / 0.45 / 1.08 | 0.46 / 0.35 / 0.61 | 0.54, 0.13 |
| X1 CO2 (t) | REDUNDANT→E1 | 45.1k / 197k / 321k | 0.22 / 0.98 / 1.59 | 0.27 / 0.68 / 0.87 | 0.95, 1.4e-4 |
| D1 H2 (MWh, —) | DIAGNOSTIC | 64.9k / 257k / 508k | 0.11 / 0.42 / 0.83 | 0.15 / 0.33 / 0.49 | 1.00, 2e-6 |
| D2 PEM utilization (—) | DIAGNOSTIC | 0.12 / 0.24 / 0.32 | 0.77 / 1.52 / 2.00 | n/a (no base) | 1.00, 2e-6 |
| E5, R1, R3 | DEAD (A2; 0 on 31 v2 runs and on wave D) | | | | |

Reads, in plain words:
- **The size-driven candidates are the renewables-side quantities.** V1
  (curtailment relief), D1 (twin H2), E6 (VRE payments) and N5 move with
  MW far more than with site: at matched MW the six top-relief sites
  relieve curtailment within ±5–15 % of each other. V1 stays an eligible
  objective (size-driven candidates are not dropped) but it does not
  discriminate between these six sites.
- **Cost, CO2 and penetration have a stable site order** (W p ≤ 0.002):
  site 163 (the smallest nameplate, 185 MW; ω up to 0.97) differs from the
  other five at every level (E1 −25.1M at every level vs −24.0 → −15.9M
  elsewhere, heatmap `E1.png`). S′ for E1 passes at L120 and L180 only;
  at L60 the spread is 0.39 of the size effect.
- **The operations and network candidates (R4–R6, N1–N4, E2, E8) pass S′
  with W p ≥ 0.2**: large between-site spread, but the site ORDER changes
  from level to level. For discrete candidates (starts, line-hours,
  lines) this is the pattern of solver-indifference chatter inside the
  0.1 % gap, which only the prompt-52 ruler can size. Their status is
  provisional on the ruler.
- No candidate needed the n-reduced path: 0 SUSPECT rows, 6 sites at
  every level.

## 2. Gap bound on the cost family (E1–E3; §3 A4b)

G_run = Σ_days gap × ruc_cost. G_base (v2, gap 0.01) = **$196.7M**;
wave-D G_row (v3, gap 0.001) = $18.4M – $25.1M. Pair bound vs base =
G_base + G_row = **$215M – $222M, of which the v2 base's own 1 % slack is
90 %**. Scaled to realized cost (÷ ruc_cost_sum / E1 ≈ 4.24 per run,
POOL_V2 §11): $51M. Disclosure: `ruc_cost` is the 36-hour RUC objective,
not realized cost; G is an approximate bound; E4 and E6 have no gap bound
and none is claimed. File: `pool_gap_bound_wavedD.csv`.

| read | E1 | E2 | E3 |
|---|---|---|---|
| per-site Δ vs v2 base, raw bound ($215–222M): GAP-READABLE | 0 / 18 | 0 / 18 | 0 / 18 |
| per-site Δ vs v2 base, scaled bound ($51M): GAP-READABLE | 0 / 18 (Δ −$15.9 … −26.1M) | 18 / 18 (Δ −$62.6 … −65.3M) | 0 / 18 (Δ +$38.4 … +47.8M) |
| between-site range vs the v3-only pair bound max G_a + G_b, raw ($41–48M) | WITHIN at every level ($2.2 / 5.5 / 9.2M) | WITHIN | WITHIN |
| between-site range vs the v3-only pair bound, scaled ($9.7 – 11.4M) | WITHIN at every level (L180: $9.2M vs $9.7M) | WITHIN | WITHIN |

Verdict on cost under the v2-base caveat: **every cost Δ vs the v2 base
is WITHIN GAP BOUND, and the bound is dominated by the v2 base's own
slack, so the read is uninformative about wave D.** E2's 18 / 18 under the
scaled bound is the identity shift (−$66.6M/yr fixed cost, section 0.1),
not a PEM effect. The base-free read is sharper: even against a v3 base,
the between-site cost range ($2.2–9.2M) sits inside the v3-only pair
bound ($41–48M raw; $9.7–11.4M scaled; L180 is at 95 % of the scaled
bound). The site ORDER of cost is stable (W p = 0.002), but the SIZE of
the between-site cost differences is not gap-readable at these MW levels.
Plan §1.2 is untouched; its verdict waits for prompt 52.

## 3. Step 2 — response shape per site

Sign (on Δ vs base, contaminated) and monotonicity (on raw values, base-
free; n_nonzero printed in `pool_standings.csv`):
- Sign-consistent on 6 / 6 sites: every directed candidate except E4
  (`+mm+++`: sites 140 and 146 mixed) and N2 (`-m----`). E9: 0 everywhere.
- Monotone in MW on 6 / 6 sites: V1, V2, X1, D1, D2. On 5 / 6: V3, E1,
  E3, E6, E7, N5, R7. On 4 / 6: E2, E8, R5. On ≤ 3 / 6 (flagged
  non-monotone, not dropped):
  E4 (3), R2 (3), N1 (3), N4 (3), R6 (2), R8 (2), N2 (1), R4 (0), N3 (0).
  The non-monotone set is again the discrete / commitment set.

## 4. Step 3 — redundancy (oriented Spearman; base-invariant)

Rule (f76d897): redundant iff ρ_or ≥ +0.90 pooled (n = 18) AND ≥ +0.90
at ≥ 2 of the 3 per-level matrices (n = 6); complete linkage; `—`
candidates shown, never clustered. Files: `pool_spearman_wavedD_pooled.csv`,
`_L60/_L120/_L180.csv`, `_stratified.csv`, `_pairs.csv` (300 pairs);
figures `figs/standings/clustermap_{pooled,L60,L120,L180,stratified}.png`
(green boxes = redundant pairs). Disclosure: the pooled ρ mixes size and
site variation; its null band at n = 18 is ±0.47 and the 95 % interval of
an observed 0.90 is about [0.73, 0.96]; the per-level matrices are the
location read; the pooled matrix may not form a cluster alone.

**Redundant pairs (4):** V2–E1 (0.98; 0.71 / 0.94 / 0.94), V2–X1 (0.99;
0.94 / 1.00 / 1.00), E1–X1 (0.98; 0.60 / 0.94 / 0.94), V2–E3 (0.90; 0.09 /
0.94 / 0.94).

**Cluster C1 = {E1, V2, X1}; survivor E1** (global order 2; V2 is 22, X1
is 3). E3 is redundant with V2 but not with E1 (per-level 0.60 / 1.00 /
0.83: one level ≥ 0.90) nor with X1, so complete linkage leaves E3 out.
The first cut's raw cluster {E1, V2, X1} is reproduced at matched MW.

**Pinned expectation falsified.** E1–X1 was expected to CONFLICT (cheaper
= more coal). On wave D oriented ρ is +0.98 pooled and +0.94 at L120 and
L180: with PEM at a VRE site, more PEM MW raises both total cost and CO2
(thermal backfill), and the site order of the two is the same. X1 is
REDUNDANT→E1; the question whether CO2 is an acceptable family (prompt 57
§7) is moot on this evidence.

**Trade-off pairs at ≤ −0.90 (never clusters, routed to step 5):** none
among directed pairs. Strong negatives involve `—` candidates only
(V1–N5 −0.93 is directed and goes to section 6; V1–E7 −0.91, V1–D1 −0.92
are `—`).

**Pairs above 0.90 pooled that are NOT redundant (the per-level guard):**
E1–E3 (0.92; 0.60 / 1.00 / 0.83, one level), E4–N5 (0.92; 0.77 / 1.00 /
0.89, one level), V1–E6 (0.95; 0.77 / 0.77 / 0.60, no level — the pure
size-trend case the per-level rule exists for), and pairs with a `—`
member (R7–X1 0.91, E7–N5 0.97, X1–D1 0.92, V3–E1 0.98).

Level-stratified ρ (within-level site ranks, n = 18) for the cluster:
V2–X1 0.98, V2–E1 0.87, E1–X1 0.83.

## 5. Step 4 — starts and cycling (R4–R6) on v2: per-unit attribution

File `pool_starts_attribution_wavedD.csv` (`gen_summary.starts`).
- **Vs the v2 base (contaminated):** 103–110 units move at every site;
  CT carries −261 … −393 of the −264 … −399 net; the SAME units lead at
  all six sites (unit 149 +28 … +45, unit 28 −24 … −26, unit 223 −20 …
  −23). An identical per-unit signature at six different sites is the
  signature of a base-wide change, i.e. the identity shift, not a site
  effect.
- **Base-free (L180 − L60 at the same site):** 83–98 units move, the top
  5 carry 18–27 % of the absolute change, no unit repeats across sites,
  all CT (COAL 0 to −6). Net −94 (site 270) … +15 (site 140): negative at
  5 of 6 sites. This is noise-like scatter across the CT fleet, not
  interpretable units.
- Sign consistency (≥ 2 sites): Δ vs base negative on 6 / 6 (dominated by
  the identity shift); base-free negative on 5 / 6.
Read: R4 passes S′ (large between-site spread vs a small size effect of
88 starts) but the spread has no stable site order (W p = 0.79) and no
interpretable unit. R4 is the textbook candidate for the §3 A4 ruler; its
LOCATION-SENSITIVE status is provisional.

## 6. Step 5 — conflicts among survivors

16 survivors (eligible: directed, not DEAD / DEAD ON WAVE D / UNREADABLE,
not REDUNDANT): V1, E1, R4, N1, E4, R2, N4, N5, E6, R5, N3, E2, R6, N2,
E3, E8. Labels: `TRADE-OFF (size)` iff pooled ρ_or ≤ −0.50 and negative
at ≥ 2 of 3 levels; `TRADE-OFF (location)` iff additionally ≤ −0.50 at
≥ 2 of 3 per-level matrices. File `pool_conflicts_wavedD.csv` (121
pairs; E1|X1 listed first as pinned).

| pair | pooled | L60 / L120 / L180 | label |
|---|---|---|---|
| **E1–X1 (pinned)** | +0.98 | +0.60 / +0.94 / +0.94 | not a conflict; REDUNDANT (cluster C1) |
| V1–E4 | −0.85 | −0.54 / −0.66 / −1.00 | TRADE-OFF (location) |
| V1–N5 | −0.93 | −0.31 / −0.66 / −0.89 | TRADE-OFF (location) |
| E1–R2 | −0.62 | −0.60 / −0.66 / −0.31 | TRADE-OFF (location) |
| E1–N4 | −0.77 | −0.60 / +0.06 / −0.94 | TRADE-OFF (location) |
| E4–N4 | −0.73 | +0.66 / −0.55 / −0.89 | TRADE-OFF (location) |
| N4–N5 | −0.76 | +0.31 / −0.55 / −0.83 | TRADE-OFF (location) |
| N4–E3 | −0.76 | −0.54 / +0.06 / −0.94 | TRADE-OFF (location) |
| R5–E2 | −0.59 | −0.14 / −0.77 / −0.60 | TRADE-OFF (location) |
| V1–E1 | −0.70 | +0.43 / −0.49 / −0.77 | TRADE-OFF (size) |
| V1–E3 | −0.76 | +0.54 / −0.49 / −0.77 | TRADE-OFF (size) |
| E1–R4 | −0.53 | −0.31 / +0.77 / −0.83 | TRADE-OFF (size) |
| E1–R5 | −0.51 | +0.43 / −0.83 / −0.26 | TRADE-OFF (size) |
| N1–E4, N1–N5, E4–R2, E4–E6, N4–E2, N5–E6 | −0.55 … −0.89 | | TRADE-OFF (size) |

Read: the curtailment-vs-cost axis (V1–E1 −0.70, V1–E4 −0.85) is a size
trade-off: more PEM MW relieves more curtailment and costs more. The
location trade-offs the campaign can exploit run between the pocket
(N4), the cost family (E1, E3, E4) and N5. Among the recommended four
(section 7) the pairs are V1–E1 size, E1–R4 size, E1–N1 sign − (−0.26,
not labelled), V1–R4 +0.34, V1–N1 +0.53, R4–N1 +0.02.

## 7. E-D1b decision table (one page; PI decides)

Rule (f76d897): recommended ≤ 4 objectives = the survivors in the global
order with at most one per family; the full survivor list is still shown.
M = 4 reopens the plan §6.4 gate numbers for the PI (no new simulation).
File `pool_ed1b_decision.csv`.

| id | role | reason (status; basis) |
|---|---|---|
| **V1** true curtailment | RECOMMENDED OBJECTIVE (V) | global order 1; LOCATION-INSENSITIVE AT THESE SIZES (S′ 0.06 / 0.14 / 0.29): the size axis; does not separate the six sites; 10–20 % contaminated |
| **E1** total cost | RECOMMENDED OBJECTIVE (E) | global order 2; LOCATION-SENSITIVE (S′ 0.39 / 0.97 / 1.62; W p 0.002); survivor of C1 {E1, V2, X1}; every Δ WITHIN GAP BOUND (section 2); plan §1.2 pending 52; ~half identity-contaminated |
| X1 CO2 | REDUNDANT → E1 | cluster C1 (ρ +0.98; 2 of 3 levels ≥ 0.94); the pinned conflict did not appear |
| **R4** thermal starts | RECOMMENDED OBJECTIVE (R), PROVISIONAL | global order 4; LOCATION-SENSITIVE by S′ (1.74 / 1.57 / 3.06) but W p 0.79, non-monotone 0 / 6, noise-like unit scatter (section 5); Δ vs base DOMINATED by the identity shift; waits for the ruler |
| **N1** congested line-hours | RECOMMENDED OBJECTIVE (N), PROVISIONAL | global order 5; LOCATION-SENSITIVE by S′ (1.46 / 2.83 / 2.67) but W p 0.75, monotone 3 / 6; Δ vs base DOMINATED (×4.9); waits for the ruler |
| E4 total payments | SURVIVOR (family E taken) | LOCATION-SENSITIVE (0.54 / 1.22 / 1.24); W p 0.07; sign mixed at 2 sites; no gap bound exists |
| R2 reserve shortfall | GUARDRAIL (survivor) | plan §1.3 role; LOCATION-SENSITIVE by S′ (3.05 / 1.66 / 1.69; range 120 / 65 / 66 MWh on a 446 MWh base); no smoke information on contamination |
| N4 pocket-120 line-h | SURVIVOR (family N taken) | LOCATION-SENSITIVE (0.40 / 0.53 / 1.69); the screening pocket; 4 location trade-offs |
| N5 congestion spread | SURVIVOR | LOCATION-INSENSITIVE AT THESE SIZES (0.36 / 0.45 / 1.08); DOMINATED at L60 |
| E6 VRE payments | SURVIVOR | LOCATION-INSENSITIVE AT THESE SIZES (0.18 / 0.72 / 0.39); clean of contamination |
| R5, N3, E2, R6, N2, E3, E8 | SURVIVOR (family taken) | LOCATION-SENSITIVE by S′; R5 / R6 / E2 / E3 / E8 DOMINATED by the identity shift; E3 and E2 within gap bound |
| R7, R8, V3, E7, D1, D2 | DIAGNOSTIC | dir `—`; never an objective; D1 / D2 track MW (W = 1) |
| D3 gen-1 / gen-93 starts | CHECK | 0 on 21 / 21 rows (S3 passes) |
| E9 scarcity bus-hours | DEAD ON WAVE D | 0 on 18 / 18 (max RT LMP 432 $/MWh < 450); count, not dead a priori |
| E5, R3 | DEAD | 0 on 31 + 21 runs |
| R1 load shed | DEAD (guardrail) | 0 on 31 + 21 runs; kept as guardrail (plan §1.3) |

What the PI should weigh: of the four, only V1 and E1 have a stable site
order; R4 and N1 are recommended by the global order on a scale-free
spread whose readability above solver chatter is unmeasured (RULER
PENDING). E1's between-site differences are inside the gap bound even
against a v3 base. A set that waits for prompt 52 before fixing the R and
N seats is defensible; the standings do not decide.

## 8. Wall-clock and core-hours (replaces plan §8 "UNKNOWN"; strategy session amends the plan)

`extracts/location_oat_v2/wallclock.csv`, 4 slots per task (`-pe smp 4`),
core-h = wall × 4. Two node-speed groups appear; the same designs sit in
both (site 110: L60 in A, L120 / L180 in B), and the per-day RUC median
solve time doubles with the wall time, so the split is node speed, not
problem size. File `pool_wavedD_wallclock.csv`.

| group | rows | wall h | core-h | RUC median solve s | RUC max solve s |
|---|---|---|---|---|---|
| A (fast) | 1–13, 20, 21 (15 rows) | 5.12 – 5.48 | 20.5 – 21.9 (mean 21.1) | 19.5 – 22.8 | 207 – 450 |
| B (slow) | 14–19 (6 rows) | 10.5 – 11.8 | 42.1 – 47.3 (mean 44.6) | 46.4 – 55.8 | 477 – 1,267 |

Wave D total: 21 rows, 146 h task-wall (sum), 584 core-h; the array
finished in 11.8 h of calendar time. Per full-year v3 run on a
fast node: **≈ 5.3 h wall / 21 core-h** (the plan's "v2 plausibly 12–25"
bracket holds for v3 on fast nodes; the January-day projection in
AMENDMENT 2026-11-06b, 8–10 h / 32–40 core-h, was pessimistic). Row 19
(nuclear L60, slow node) has one RUC day at 1,267 s wall with status
OPTIMAL and `n_ruc_time_limit = 0`: the solve-time column includes model
build, so a value above the 1,200 s limit does not by itself mean the
limit tripped; 0 TIME_LIMIT statuses on 7,665 RUCs.

## 9. Recommendation: buy ONE v3 base run (not decided here)

One full-year run of `base_2019_v2` data under identity v3 (`--full`,
same array block, ≈ 5.3 h wall / 21 core-h on a fast node, 11 h on a slow
one) removes the contamination from every Δ column, makes S a clean
second read, puts the E1–E3 gap bound at G_a + G_b ≈ $41–48M raw /
$10M scaled instead of $215M+, and lets the identity-shift table
(section 0.1) be replaced by a measured full-year shift. The re-run is one
command: `python pool_standings.py --base extracts/<v3 base>/run_index_1`.
Until then every Δ-vs-base number in this document is labelled
contaminated, and the base-free reads (range, S′, W, ρ, clusters,
conflicts) carry the standings. A separate agent is building that wave;
this document does not build it.

## 10. Figures

- `figs/standings/<id>.png` (25): 6 × 3 site-by-MW heatmap of Δ vs base
  (contaminated label in the title), nuclear row overlaid below a black
  rule (hatched `UNCORRECTED` for E1–E4, E7), one colorbar per candidate,
  bold axes, tick labels ≥ 18 pt, S′ and W in the title.
- `figs/standings/clustermap_pooled.png`, `_L60`, `_L120`, `_L180`,
  `_stratified`: oriented Spearman heatmaps with the complete-linkage
  dendrogram; green boxes = the 4 redundant pairs.

## 11. Files

| file | content |
|---|---|
| `pool_wavedD_wide.csv` | 21 rows: keys + level + every candidate + E8/E9/N5 from `pool_full_metrics.json` (CRC; `full_source`) + identity + G + headroom + solve times; `pool_wide_v2.csv` untouched |
| `pool_wavedD_delta.csv` | the same minus the base (label column) |
| `pool_standings.csv` | one row per candidate (26 graded + 3 dead): status, basis, range / S′ / S per level, ruler placeholders, W + exact p, gap reads, cluster, survivor, identity shift + ratios, `nuc_delta_<level>`, nuclear tag |
| `pool_standings_levels.csv` | 6 sites × 3 levels × 26 candidates: value and Δ |
| `pool_gap_bound_wavedD.csv` | E1–E3 per site × level: raw and scaled pair bounds, v3-only bounds, statuses |
| `pool_identity_shift_smoke.csv` | the section 0.1 table |
| `pool_spearman_wavedD_{pooled,L60,L120,L180,stratified}.csv`, `_pairs.csv` | step 3 |
| `pool_clusters_wavedD.json` | clusters, survivors, eligible set, redundant pairs, identities, defs md5 |
| `pool_conflicts_wavedD.csv` | step 5 |
| `pool_starts_attribution_wavedD.csv` | step 4 |
| `pool_ed1b_decision.csv` | section 7 |
| `pool_wavedD_wallclock.csv` | section 8 |
| `../../pool_standings.py`, `../../tests/test_pool_standings.py` | script (`--base`, `--noise`) + 7 tests |

Run: `python pool_standings.py` (≈ 1 min with figures). Tests:
`pytest tests/test_pool_standings.py tests/test_pool_objectives.py -q`
→ 23 passed (pandas 2.3.3 / scipy 1.16.3; not run under PCM_ERCOT).

## 12. Deviations

1. **Base identity.** No v3 base exists. Every Δ is against the v2 base
   and is labelled `CONTAMINATED (v2 base, v3 rows)`; the §3 A4b gap
   bound uses G_base(v2) + G_row(v3) and is 90 % the base's own slack;
   the smoke-scaled identity shift is printed beside every Δ (section
   0.1). The status column rests on the base-free S′ (section 0.2), an
   addition pinned by the strategy session on 11-07 after the first look
   at wave D, not in prompt 57 v2.1; S (pinned) is reported beside it.
2. **Ruler.** Prompt 52 has not landed; the ruler columns are
   placeholders (`--noise`). The three-way §4 step 1 verdict is not made;
   the status set of §4 is used with `status_basis` saying which read
   set it.
3. **Full extracts not local.** The four `*.csv.gz` tables stayed on CRC
   (`.gitignore`). E8, E9, N5 come from the CRC-computed
   `pool_full_metrics.json` per row (`full_source` column); R7, R8,
   G_run and the `overall.csv` md5 in that JSON were asserted equal to the
   local slim recomputation on all 21 rows. `full_extract = True` is
   asserted from the JSON, not from local gz presence.
4. **Nuclear h2 (D1) is NaN on rows 19–21**: `thermal_h2` needs
   `thermal.csv.gz`, which is not local, and `pool_full_metrics.json`
   carries no h2 field (`h2_source = unavailable`). D2 is NaN with it. A
   CRC per-run call of `co.thermal_h2(key, site="1", pmax=2430)` fills
   it; `pool_objectives.pool_row` already takes that path when the gz is
   present.
5. **Nuclear cost family UNCORRECTED** (section 0.3). No K_syn
   correction was attempted.
6. **What the nuclear cost correction needs:** the thermal patch's
   installed cost curve for gen 1 per row (`multi_pem/parameters.py`
   flat band + forced commitment; `retrofit_gen_dict_{19,20,21}.json`),
   the base gen-1 booked Unit Cost ($3.1849B/yr, ERCOT_SELECTION §7) and
   its fuel-curve reconciliation (open PI question), per-hour gen-1
   dispatch from `thermal.csv.gz` (CRC), and the pinned rule K_raw −
   K_syn with the synthetic-cost caveat; adjudication = PI.
7. **`pool_objectives.pool_row`** gained two optional arguments (`drow`,
   `d`) so a run without a design-matrix entry (a v3 base replicate, the
   smoke tasks) can be read; a non-integer index is tolerated. No output
   of Part A changed; `tests/test_pool_objectives.py` 16 / 16.
8. **Kendall's W exact p** by enumeration of the 720² relative
   permutations (judge 1 fixed), mid-ranks on ties without a tie
   correction (ties: N1 1 cell, N4 1, N2 8, E9 15).
9. **Clusters** are complete-linkage cliques on the binary "redundant"
   relation (both conditions of the rule), which is the rule's literal
   reading; the dendrograms in the figures use 1 − ρ of each matrix.
10. **Conflict table** lists all 120 survivor pairs plus the pinned E1|X1
    even though X1 is not a survivor (`both_survivors = False`).
11. **Wall-clock node groups** are inferred from wall time and RUC solve
    time (no host names in the extracts).
12. **Session lock** `trial_0826/campaign/.session.lock` = `57B` inside
    this worktree (it read `52` on arrival; overwritten, left untracked).
13. **Plan not amended**; the pi-agenda row and the plan §8 wall-clock
    replacement are for the strategy session.
14. **pandas 3.0.5 not tested** (local 2.3.3 only).
