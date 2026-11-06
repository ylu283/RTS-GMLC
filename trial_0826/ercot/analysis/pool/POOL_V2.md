# ERCOT objective pool v2 — Part A of prompt 57 (zero simulation)

**Date:** 2026-11-06. **Branch:** `ercot/tx123`. **Definitions freeze
commit:** `f76d897` (`analysis/pool/pool_definitions.json`). Later
commits: `4863973` (extractor, pool_wide_v2, dead list, gap bound),
`a613507` (first cut). Part B (wave-D standings) has NOT run: wave D
does not exist. No PCM simulation ran for this document.

**What this document is.** The widest honest candidate pool for the
ERCOT objective vector (E-D1), computed on the 31 existing v2 runs. It
names what is dead, what is undetermined, and which candidates move
together on the 16 single-site screening rows. It drops nothing. The
NON-USE clause is in force: the first cut names clusters; Part B
decides.

**Numbers seen before the freeze.** The 31 runs' legacy 9 columns, the
base values of N1/N3/N4/N5/E7, the uplift zeros, the n = 16 first cut
of relief/var_cost/h2/starts (`pool_correlations.csv`), and the v2 fuel
prices. No prompt-52 value and no wave-D value existed. Part-A outputs
(sections 2, 4, 6) were computed AFTER the freeze commit and changed no
priority.

## 1. Pool (pinned in `pool_definitions.json` at f76d897)

Values are full-year scalars. `base` = `base_2019_v2:1`. `Δ min` /
`Δ max` = the smallest and largest (value − base) over the 31 runs
(nuclear rows included). Status is the A2 a-priori read.

| id | fam | candidate | unit | dir | prio | base | Δ min (31) | Δ max (31) | A2 status |
|---|---|---|---|---|---|---|---|---|---|
| V1 | V | true curtailment | MWh | min | 1 | 5.924e6 | −3.748e6 | 53,200 | ALIVE |
| V2 | V | renewables penetration | % | max | 9 | 22.825 | −3.125 | 0.012 | ALIVE |
| V3 | V | PEM-twin delivered share | fraction | — | — | 0.000 | 0.000 | 0.054 | ALIVE (diag) |
| E1 | E | total cost | $ | min | 1 | 8.091e9 | −345.5e6 | 358.7e6 | ALIVE |
| E2 | E | fixed (commitment) cost | $ | min | 4 | 3.631e9 | −128.2e6 | 56.9e6 | ALIVE |
| E3 | E | variable cost | $ | min | 5 | 4.460e9 | −217.3e6 | 439.9e6 | ALIVE |
| E4 | E | total payments (consumer side) | $ | min | 2 | 14.055e9 | 0.000 | 360.1e6 | ALIVE |
| E5 | E | uplift payments | $ | min | — | 0.000 | 0.000 | 0.000 | **DEAD** |
| E6 | E | VRE energy payments | $ | max | 3 | 2.610e9 | −128.6e6 | 67.4e6 | ALIVE |
| E7 | E | mean settlement price (energy) | $/MWh | — | 7 | 36.360 | 0.000 | 1.011 | ALIVE (diag) |
| E8 | E | LMP dispersion (`--full`) | $/MWh | min | 8 | 15.483 | — | — | UNDETERMINED (1 full run) |
| E9 | E | scarcity bus-hours (`--full`) | count | min | 8 | 0 | — | — | UNDETERMINED (1 full run) |
| R1 | R | load shed | MWh | min | — | 0.000 | 0.000 | 0.000 | **DEAD** (guardrail) |
| R2 | R | reserve shortfall | MWh | min | 2 | 445.934 | −328.3 | 223.6 | ALIVE |
| R3 | R | over generation | MWh | min | — | 0.000 | 0.000 | 0.000 | **DEAD** |
| R4 | R | thermal starts | count | min | 1 | 15,957 | −3,208 | 0 | ALIVE |
| R5 | R | start/stop ramping | MW | min | 3 | 1.620e6 | −269,951 | 793 | ALIVE |
| R6 | R | nominal ramping | MW | min | 4 | 16.164e6 | −1.260e6 | 571,843 | ALIVE |
| R7 | R | committed capacity-hours | MWh | — | 2 | 361.2e6 | −1.643e6 | 7.271e6 | ALIVE (diag) |
| R8 | R | committed unit-hours | unit-h | — | 5 | 443,791 | −3,959 | 9,591 | ALIVE (diag) |
| N1 | N | congested line-hours | line-h | min | 1 | 36,413 | −232 | 3,977 | ALIVE |
| N2 | N | congested lines | count | min | 4 | 39 | −4 | 1 | ALIVE |
| N3 | N | flow violation | MWh | min | 3 | 91,029 | −55.0 | 33.3 | ALIVE |
| N4 | N | pocket-120 congested line-hours | line-h | min | 2 | 5,460 | −1,074 | 297 | ALIVE |
| N5 | N | congestion spread (`--full`) | $/MWh | min | 2 | −18.402 | — | — | UNDETERMINED (1 full run) |
| X1 | X | CO2 (fuel-factor) | t | min | 1 | 194.5e6 | 0.000 | 8.002e6 | ALIVE |
| D1 | D | H2 electricity | MWh | — | — | 0.000 | 0.000 | 15.744e6 | ALIVE (diag) |
| D2 | D | PEM utilization | fraction | — | — | n/a (pem_mw = 0) | 0.288 (value) | 0.756 (value) | ALIVE (diag) |
| D3 | D | gen-1 / gen-93 starts | count | — | — | 0 / 0 | 0 | 0 | constant 0 (S3 passes on 31 runs) |

Notes on the table:
- The 31 runs are 23 distinct designs (`distinct_design_id` D01–D23,
  by byte-identical `overall.csv`). `replicate_of` is mapped to v2 wave
  names (`screening_ercot:1` → `screening_v2/ercot:1`, `selection_t1:8`
  → `selection_t1_v2:8`, `base` → `base_2019_v2:1`).
- `full_extract` is True on one run only (`base_2019_v2:1`). E8, E9 and
  N5 are NaN on the other 30 and are never imputed.
- N4 is a one-line indicator on every run: L252 carries all pocket
  line-hours; L4, L5, L100, L113, L197, L198 and L240 are 0 on all 31.
- X1 sensitivity columns: `X1_ef_lo/hi` (all EF × 0.8 / × 1.2) and
  `X1_gas_lo/hi` (CT EF only). Gas is 180.3e6 t of the 194.5e6 t base.
- SUSPECT flags S1–S3 (plan §1.2): no run is SUSPECT. S1 max residual
  is below $1; 11,315 / 11,315 RUCs are OPTIMAL (365 per run); gen-1 and
  gen-93 starts are 0 on all 31 runs.
- Legacy regression: all 144 cells (16 rows × 9 columns) of the frozen
  `objectives_t1_v2.csv` equal the recomputed values to 1e-6. `h2` on
  `selection_t1_v2:6–11` is copied from the frozen CSV
  (`h2_source = frozen_t1_v2`) because the slim extracts carry no
  `thermal.csv.gz`.

## 2. Dead list (A2; evidence = max |value| over 31 runs)

| id | candidate | max \|value\| | verdict |
|---|---|---|---|
| E5 | uplift payments | 0.0 | DEAD. Zero on every run, overall, daily and per unit. Priority vacated. |
| R1 | load shed | 0.0 | DEAD. Kept as guardrail (plan §1.3). |
| R3 | over generation | 0.0 | DEAD. |

Not dead, not alive: E8 (15.48 $/MWh), E9 (0 bus-hours; base RT LMP
max 446.1 < 450), N5 (−18.40 $/MWh) exist on one full run only. Their
status is UNDETERMINED until wave D (all `--full`). E9 = 0 on base is a
count, reported as 0, not as dead.

D3 (gen-1 / gen-93 starts) is constant 0. It is a check, not a
candidate, and does not enter the dead list.

## 3. Exact replicates give exact zeros

Byte-identical groups: {base 1, 2, 3, ercot:11} = D01; {ercot:1,
ercot:12, sel:3} = D02; {ercot:8, sel:4, sel:5} = D09; {sel:8, sel:11} =
D21. The maximum within-group |Δ| over every candidate and every group is
0.0 (`pool_replicate_zero_check_v2.csv`). The v2 instrument is
deterministic; a ruler from exact replicates is 0 and is reported as
such, never used.

## 4. First cut (A3; n = 16; NON-USE clause in force)

Rows: `screening_v2/ercot:1–9` + `screening_v2/topup:1–7` (16 single
sites; 5 share bus 120). Row 10 (`__ALL__`), 11 (base replicate) and 12
(replicate of 1) are excluded. Every candidate is oriented so that
smaller is better (`max` × −1). `—` candidates are shown and never
cluster. Spearman raw and gen_pmax-partialled (rank-residual convention
of `pool_correlations.csv`). No tie rule: the v2 ruler is 0. Files:
`pool_spearman_firstcut.csv` (210 pairs), the two matrix CSVs, and
`figs/pool_firstcut_clustermap.png` (complete linkage).

Shown: V1, V2, V3, E1, E2, E3, E4, E6, E7, R2, R4, R5, R6, R7, R8, N1,
N2, N3, N4, X1, D1 (21). Excluded: E5/R1/R3 (dead), E8/E9/N5 (NaN on
slim rows), D3 (constant).

**Clusters (ρ_or ≥ +0.90 on every pair, directed members only):**
- raw: **{E1, V2, X1}** — total cost, penetration (oriented) and CO2
  move together across sites at one size per site.
- partialled on gen_pmax: **{V2, X1}** only. E1 leaves the cluster
  (E1–X1 0.92 raw → 0.52 partialled; E1–V2 0.95 → 0.66).

These are names, not drops. One size per site confounds size and
location. Part B (wave D, matched MW) decides.

**Pairs worth watching (raw / partialled):**
- E1–X1 +0.92 / +0.52. The pinned expectation was a CONFLICT. On
  single-site rows both grow with PEM size (ΔX1 > 0 on 16 / 16, ΔE1 > 0
  on 12 / 16). The size-partialled value is +0.52, not negative. The
  conflict, if real, needs the matched-MW design to show.
- V2–X1 +0.99 / +0.95. Lower penetration ↔ more CO2. Near-affine.
- E2–R7 +0.93 / +0.94, E2–R8 +0.93 / +0.92, R7–R8 +0.92 / +0.93. Fixed
  cost tracks committed capacity-hours and unit-hours. R7/R8 are `—`,
  so no cluster forms. They explain E2.
- V1–N3 −0.84 / −0.87. Less curtailment ↔ more flow violation. A
  possible trade-off axis between the renewables and network families.
- V1–N1 +0.79 / +0.81, V1–N4 +0.74 / +0.74, V1–E6 +0.83 / +0.82.
- R4–R5–R6 (starts, start/stop ramp, nominal ramp): +0.75 to +0.84 raw;
  R4–R5 +0.64 partialled. They do not reach 0.90.
- E4–E7 +0.92 / +0.73 (E7 is `—`; E7 = E4 energy part / constant
  demand, so this is expected).
- R2 and N2 sit apart from everything (|ρ| ≤ 0.64).

**Scale-free descriptor S on the 16 rows** (S = range / mean |Δ|; one
size per site, so S is a descriptor only): V1 3.56, V2 2.37, E1 3.60, E2
2.61, E3 1.97, E4 1.77, E6 4.06, R2 3.08, R4 2.04, R5 2.33, R6 2.22, N1
5.20, N2 2.56, N3 2.84, N4 3.26, X1 2.10, D1 1.93. Sign counts: V1, V2,
R4 and N4 are negative on 16 / 16; E3, E4, E7, X1, D1 positive on 16 /
16; N1 is 7 positive / 9 negative (the most location-shaped sign
pattern); R2 4 / 12; E6 10 / 6.

## 5. Ruler (A4; pinned, not yet measurable)

`ruler_j` := the median |Δ_j| over the prompt-52 perturbed copies
(δ = 0.001 relative; 4 designs × 2 copies = 8 values). It is the response
of the deterministic solve to a 0.1 % input move, not a sampling sd.
Readable means: "exceeds twice the median response to a 0.1 % input
perturbation at the prompt-52 designs." A failing effect reads "not
readable above the perturbation response", never "zero". Ratios in
[2, 3) are BORDERLINE. `RULER=0` → readable iff |Δ| ≥ 1 natural unit.
`RULER UNAVAILABLE` for E8/E9/N5 if the 52 extracts are slim. Until 52
lands every Part-B readability statement carries `RULER PENDING (52)`.
Exact replicates and perturbed copies are never pooled.

**Status: RULER PENDING (52).** No perturbed copy exists.

## 6. Noise-free scales (A4b)

### 6.1 MIP-gap cost bound G (E1–E3 only)

G_run = Σ_days (`final_gap_pct` / 100 × `ruc_cost`) from
`ruc_quality.csv`. Pair bound = G_a + G_b. Table:
`pool_gap_bound_v2.csv` (31 rows); summary `pool_gap_bound_summary.json`.

| quantity | value |
|---|---|
| G_base (`base_2019_v2:1`) | **$196.7M** (0.573 % of the $34.3B annual RUC cost) |
| G_run range over 31 runs | $152.8M – $215.5M (0.44 – 0.63 % of RUC cost) |
| max `final_gap_pct` per run | 0.9999 – 1.0000 on every run (the 1 % gap binds every day) |
| pair bound vs base | $349.5M – $412.2M |
| single-site median \|Δ E1\| (16 rows) | $11.3M (recomputed 11.32M; range $2.0M – $66.4M) |
| **G_base / $11.3M** | **17.4** |
| single-site E1 Δ GAP-READABLE | **0 of 16** |
| any run GAP-READABLE (E1) | 1 of 31: `selection_t1_v2:10` (nuclear ω = 1.0, Δ E1 = +$358.7M vs bound $353.6M) |

**Finding.** G_base is 17.4 times the median single-site |Δ total_cost|.
Under the frozen 1 % RUC gap, every single-site cost difference seen so
far (max $66.4M; `__ALL__` row $353.6M) is WITHIN GAP BOUND. The
instrument is deterministic (section 3), so the solves are repeatable;
the bound says how much day-ahead commitment cost the solver was allowed
to leave on the table, not how much it did. E-D1's cost evidence (plan
§1.1, the $11.3M / $13.3M / $26.7M medians) must be re-read against
this bound in Part B. The §1.2 test itself is frozen and unchanged.

**Disclosure.** `ruc_cost` is the RUC objective (day-ahead commitment +
dispatch cost), not the realized total cost, so G is an approximate
bound and is stated as such. For E4 and E6 (settlement quantities) no
gap bound exists and none is claimed.

### 6.2 Scale-free location ratio S

S_jℓ = range_jℓ / mean_site |Δ_jℓ| at each wave-D MW level ℓ.
`LOCATION-SENSITIVE (scale-free)` iff S ≥ 0.5 at ≥ 2 of 3 levels;
`SIZE-DRIVEN (scale-free)` iff S < 0.5 at ≥ 2 of 3 levels with a nonzero
mean. Pinned at f76d897. On the 16-row first cut S is a descriptor only
(section 4). Wave D does not exist, so no S verdict exists.

## 7. Wave-D build requirement (A5; storage line for Kay's CRC check)

Every wave-D row runs `extract_ercot.py --full`. Measured full extract
= **51 MB** (`base_2019_v2/run_index_1`; the extractor docstring's
~40 MB is stale). **21 rows (18 VRE + 3 nuclear) ≈ 1.07 GB; 18 rows ≈
0.92 GB.** Recorded as the dated addendum to prompt 36 §4.2 (done
11-06); the pre-registered rule text stays verbatim.

## 8. Files

| file | content |
|---|---|
| `pool_definitions.json` | FROZEN at f76d897: formulas, dir, priorities, global order (29 ids), EF + source, thresholds |
| `pool_wide_v2.csv` | 31 rows: keys, every candidate, N4 per-line split, X1 sensitivities, S1–S3, G_run, `overall_md5` |
| `pool_delta_v2.csv` | the same minus `base_2019_v2:1` |
| `pool_dead_list_v2.csv` | A2 statuses with max \|value\| |
| `pool_replicate_zero_check_v2.csv` | within-group max \|Δ\| (all 0.0) |
| `regression_vs_frozen_t1_v2.csv` | 144 cells vs `objectives_t1_v2.csv` |
| `pool_gap_bound_v2.csv`, `pool_gap_bound_summary.json` | A4b |
| `pool_spearman_firstcut.csv` + `_matrix_raw/_partial.csv` | A3 (210 pairs) |
| `pool_firstcut_clusters.json`, `pool_firstcut_S_descriptor.csv` | A3 clusters and S |
| `figs/pool_firstcut_clustermap.png` | raw + partialled heatmaps, complete-linkage dendrogram |
| `../../pool_objectives.py`, `../../tests/test_pool_objectives.py` | extractor + 13 tests |

Run: `python pool_objectives.py --stage A1` then `--stage A3
--freeze-hash f76d897`. Tests: `pytest tests/test_pool_objectives.py -q`.

## 9. Open items

- Kay: the three wave-D MW levels (≤ 185.4 MW); E-D0; whether X1 is an
  acceptable objective family for the PI; confirm the family order
  V < E < X < R < N (frozen at f76d897; a change is an AMENDMENT).
- Prompt 52 (ruler) and wave D (Part B data) do not exist.
- Run the tests under PCM_ERCOT (pandas 3.0.5): not done here.
- E-D1b (plan amendment 2026-11-06): survivors → objectives /
  guardrails / diagnostics, after Part B.

## 10. Deviations

1. **Freeze order.** X1 needs the EF values before it is computed, so
   `pool_definitions.json` was written before A1 ran. It was committed
   unchanged as the first commit (f76d897), after the A1/A2 numbers were
   seen and before A3 ran. No priority, direction, threshold or EF was
   changed after any number was seen.
2. **pandas 3.0.5 not tested.** Only `/opt/anaconda3` (pandas 2.3.3,
   scipy 1.16.3, matplotlib 3.10.6, seaborn 0.13.2) was available. The
   code avoids chained assignment and uses explicit copies and string
   keys; `tests/test_pool_objectives.py` must be re-run in PCM_ERCOT.
   The FutureWarning from `compute_objectives.gen_summary` (fillna
   downcasting) is filtered, not fixed; the result is the same bool
   column under pandas 3.
3. **Clustermap drawn with scipy + matplotlib**, not seaborn, so that
   every tick label and axis label is bold and ≥ 18 pt at display size
   and the two panels (raw, partialled) share one leaf order. The
   dendrogram is the raw-matrix complete linkage.
4. **Extra non-candidate columns** in `pool_wide_v2.csv`: `N4_<UID>`
   per-line split (asked for), `X1_*` sensitivities (asked for),
   `E8_slim_daily_settle_sd` (the slim companion, asked for),
   `N5_unweighted_check` (reproduces the seen-before −17.36; a join
   check), `E9_lmp_max`, `gen1_unit_cost` (legacy regression),
   `overall_md5`, G columns. No candidate was added.
5. **`pool_delta_v2.csv`** is an extra convenience file (value − base);
   `pool_wide_v2.csv` holds raw values. D2 has no base Δ (pem_mw = 0 on
   base) and is reported as a value.
6. **EF sources are cited from the named public tables** (EPA 40 CFR 98
   Table C-1; EIA Electric Power Annual Table 8.2; EIA FAQ). They were
   not re-fetched in this session.
7. **A3 "oriented candidates"** was read as: directed candidates are
   oriented and may cluster; `—` candidates are shown unoriented and
   never cluster (§4 step 3 wording), so the first-cut figure carries 21
   ids, not 16.
8. **Session lock** `trial_0826/campaign/.session.lock` = `57` is
   written inside this worktree and left untracked.

## 11. Strategy-session note on the gap bound scale (2026-11-06, appended after 3bd4064)

`ruc_cost` is the 36-hour RUC objective (`ruc_horizon = 36`,
CONFIG_ERCOT.md) and includes penalty terms, so Σ_days `ruc_cost` =
$34.33B is 4.24 × the realized annual total cost ($8.09B). G as defined
in §6.1 therefore overstates the realized-cost artifact bound by about
that factor. Scaled to realized cost, G_base ≈ $196.7M / 4.24 ≈ **$46M**
and the pair bound vs base ≈ **$93M**. The finding does not change: the
median single-site |Δ total_cost| ($11.3M) is about 4 × below the scaled
G_base, and the largest single-site Δ ($66.4M) is below the scaled pair
bound. Both numbers (raw and scaled) are to be shown side by side in
Part B. The §6.1 definition and the frozen `pool_definitions.json` are
unchanged; this note is a scale disclosure, not a rule change. Solve
times on base: median 19 s, p95 30 s, max 51 s per RUC day — a tighter
`ruc_mipgap` is plausibly affordable and is raised as decision E-D6.
