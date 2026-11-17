# location_contrast_E — ERCOT location contrast (prompt 61 v1.1; analysis-only; NOT submitted)

Built by `tools/make_location_contrast_E.py` (zero simulation; reuses the
prompt-53 helpers in `tools/make_ercot_n0.py`). Design space
`waves/design_space_E.json` (contract 2026-11-13, passed explicitly).
Kay submits ON CRC, after the wave commit is on `ercot/tx123`:

    cd trial_0826/ercot/waves/location_contrast_E && bash submit_this.sh

`submit_this.sh` checks the branch, pulls, refuses without
`waves/GAP_DECISION.json`, `waves/smoke_v2/SMOKE_PASS`,
`waves/design_space_E.json`, the v2 data or the `.gitignore` gz line
(`extracts/location_contrast_E/**/*.csv.gz`), prints the identity and `qquota`, and asks
for a literal `yes` before `qsub`. Analysis-only; no dependency on n0_E /
random_E / methods_E.

**Analysis-only.** These 9 rows never enter the GP's X, the HV ledger, the
holdout or the random baseline (prompt 61 section 4; plan sections 4, 5,
6.3, 7; 55 `base_waves = ["n0_E"]`). `tier = "contrast"`, `sobol_index` empty,
`level_id` = the row label.

## Design (9 rows; `__ALL__` multi-site schema, contract section 5)

Computed in code from `design_space_E.json`: flat rows put every site at m
MW; pro-rata rows put `mw_s = T · gen_pmax_s / Σ_group gen_pmax` on the group
(`u = T / Σ_group` on the group) and exactly 0.0 elsewhere. Asserted:
`mw_s ≤ gen_pmax_s`, `Σ mw = T` to 1e-6, the group's buses. Table rounded to
0.01 MW; `design_matrix.csv` carries full float precision (read with
`float_precision="round_trip"`). The `mw_*` columns hold the exact MW (P1
rows carry 60 / 120 / 180 exactly); `u_* = PEM_fraction`; `pem_mw = Σ mw_s`
(equals `pool_objectives.pem_mw()` on the retrofit dict to 1e-9). Retrofit
dict `retrofit_gen_dict_<index>.json` = `{"<site>": {"PEM_bid": 40.0,
"PEM_fraction": u_s, "gen_pmax": gen_pmax_s}}` for every site with mw_s > 0;
exact zeros are omitted (plan section 2: 0 = absent).

| # | label | rule | mw_110 | mw_140 | mw_146 | mw_163 | mw_270 | mw_274 | total | u |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | P1_60 | all six at 60 | 60.00 | 60.00 | 60.00 | 60.00 | 60.00 | 60.00 | 360 | 0.08–0.32 |
| 2 | P1_120 | all six at 120 | 120.00 | 120.00 | 120.00 | 120.00 | 120.00 | 120.00 | 720 | 0.16–0.65 |
| 3 | P1_180 | all six at 180 | 180.00 | 180.00 | 180.00 | 180.00 | 180.00 | 180.00 | 1,080 | 0.24–0.97 |
| 4 | P2_800_b120 | T 800, bus-120 only, pro rata to gen_pmax | 0.00 | 0.00 | 0.00 | 98.17 | 306.59 | 395.23 | 800 | 0.530 |
| 5 | P2_800_b275 | T 800, bus-2/75 only, pro rata | 316.01 | 233.88 | 250.12 | 0.00 | 0.00 | 0.00 | 800 | 0.933 |
| 6 | P2_800_all | T 800, six pro rata | 114.39 | 84.66 | 90.54 | 62.64 | 195.61 | 252.16 | 800 | 0.338 |
| 7 | P2_500_270 | T 500, site 270 alone (bus 120) | 0.00 | 0.00 | 0.00 | 0.00 | 500.00 | 0.00 | 500 | 0.864 |
| 8 | P2_500_110_140 | T 500, sites 110 + 140 (bus 2), pro rata | 287.34 | 212.66 | 0.00 | 0.00 | 0.00 | 0.00 | 500 | 0.849 |
| 9 | P3_1500_all | T 1,500, six pro rata — saturation probe | 214.48 | 158.74 | 169.76 | 117.44 | 366.77 | 472.80 | 1,500 | 0.633 |

Rows 7–8 are the **matched-u pair** (same total, same share of nameplate,
different bus): the design-side control for the u confound. Row 9 is the
saturation probe (Kay may drop it; default IN).

### Disclosures (prompt 61 section 2.2)

- Row 3 (P1_180) puts site 163 at 97.1% of nameplate (u = 0.9709).
- Row 5 (P2_800_b275) puts the bus-2/75 sites at u = 0.933.
- A bus-2/75-only row at 1,500 MW is infeasible: the group cap is
  857.2 MW.
- The v1 1,500-MW bus-120-only row (u 0.993 on three sites, a box corner)
  was dropped in review.

## Covariate H_C (pre-registered; computed at build, before any Y of this wave existed)

`H_C(x) = Σ_{h∈C} Σ_s min(mw_s, W_s,h)`, W = `data/ercot123_2019_v2/REAL_TIME_wind.csv`
(the 8,760 rows of 2019; the file's 24 rows of 2020-01-01 are not used;
`Period = Hour + 1`), C = hours with base_v3 non-PEM WIND curtailment
> 1 MWh (`extracts/base_v3/run_index_1/renewables_hourly.csv`;
4,410 h, asserted). Per-site terms and full precision in `H_C.csv`.

| # | label | total MW | H_C (MWh) | H_C / total MW (h) |
|---|---|---|---|---|
| 1 | P1_60 | 360.00 | 1,488,501.0 | 4,134.7 |
| 2 | P1_120 | 720.00 | 2,831,797.0 | 3,933.1 |
| 3 | P1_180 | 1,080.00 | 4,000,863.0 | 3,704.5 |
| 4 | P2_800_b120 | 800.00 | 3,092,965.4 | 3,866.2 |
| 5 | P2_800_b275 | 800.00 | 2,691,591.1 | 3,364.5 |
| 6 | P2_800_all | 800.00 | 3,208,406.6 | 4,010.5 |
| 7 | P2_500_270 | 500.00 | 1,655,333.3 | 3,310.7 |
| 8 | P2_500_110_140 | 500.00 | 1,729,210.8 | 3,458.4 |
| 9 | P3_1500_all | 1,500.00 | 5,529,516.4 | 3,686.3 |

Ratios: H_C(P2_800_b120) / H_C(P2_800_b275) = 1.1491
(section 3 predicted ≈ 1.149); H_C(P2_500_270) / H_C(P2_500_110_140) =
0.9573.

## Identity (v3)

Every run reads `--ruc_mipgap` / `--ruc_time_limit` from
`waves/GAP_DECISION.json` at RUN time (0.001 / 1200; Kay, E-D6, 2026-11-06),
prints `IDENTITY from GAP_DECISION.json: ...` into the task log (the collector
copies it to `run_index_N/identity.txt`), and refuses without the file.
SMOKE_GATE on `waves/smoke_v2/SMOKE_PASS`.

## Collector and the gz policy

`collect_location_contrast_E.sh` (held on the array; email on this job only): every row
`extract_ercot.py --full` → `extracts/location_contrast_E/run_index_N/` (`--full` kept:
same template, nothing in git, keeps N5 / E8 available; the section 3 reads
need only the slim tables), Prescient `runtimes.csv`, wall-clock from the
`LOC_CONTRAST_E_START` / `LOC_CONTRAST_E_END` stamps, the identity line → `identity.txt`,
then ON CRC `pool_objectives.py --run-dir`, then `COLLECTED`. The
`*.csv.gz` tables stay uncommitted (`.gitignore`:
`extracts/location_contrast_E/**/*.csv.gz`; the collector aborts if one is staged).

## Budget

9 full-year runs × 4 slots = 36 slots; ≈ 170–355 core-h (6-site landing
actuals 19–39.4 core-h/run, plan AMENDMENT 2026-11-16). Storage: 9 ×
51 MB ≈ 459 MB of `--full` extracts in $GROUP storage.

## Local checks (zero simulation)

`bash -n` on the scripts; `/opt/anaconda3/bin/python -m pytest
tests/test_make_location_contrast_E.py tests/test_make_ercot_n0.py -q`.

## Deviations

- `tier = "contrast"` is outside contract section 5's `{nav, grading,
  holdout, bo}`; admitted by the contract addendum 2026-11-17.
- The scripts are the prompt-53 templates (`make_ercot_n0.array_script` /
  `collector_script` / `submit_script`) with a `WAVES_E` key added at
  runtime and three asserted string replacements (prompt label, row
  description, dependency line). The collector copies `design_space_E.json`
  into the extract, as 53's does.
- Prompt 61 section 2.3 pins the row-description replacement text
  "... never in GP X / HV / holdout / baseline)" AND asks that the final
  script texts contain no "holdout". The two cannot both hold. The pinned
  replacement is kept; the "no holdout" check (generator and test) is
  applied to the script texts with that one pinned phrase removed, so the
  53 holdout label ("random holdout (default_rng(5353) ...)") is proven
  gone. "Sobol" is checked on the full texts.
- The array-script comment keeps the template wording "full-year 6-site
  rows"; rows 4, 5, 7 and 8 have 3, 3, 1 and 2 sites present (absent sites are
  omitted from the retrofit dict, plan section 2).

---

The section below is prompt 61 v1.1 section 3, copied VERBATIM; it is the
frozen pre-registration of this wave.

## 3. Pre-registered reads (FROZEN with the wave commit; copied verbatim into the wave README)

**Seen at freeze (11-17):** wave-D rows 1–18 and base_v3 (all pool ids);
`analysis/noise_v3/ercot_noise.json` (rulers; `all_exact_zero = True`;
plan §1.2 READABLE → cost seat E1, E3 secondary); `waves/n0_E/LANDING.md`
and plan AMENDMENT 2026-11-16 (R values). No `location_contrast_E`
value existed. The bar form below is justified by the 52 null
population, not by any contrast value.

**Notation.** b = `base_v3:1`; singles s(m) = `location_oat_v2` row with
`oat_site = s, level_id = L<m>`; J(m) = P1 row at m; all objectives
minimized; Δ_j(x) = y_j(x) − y_j(b) (signed, objective units); relief
R(x) = −Δ_V1(x).

**Bar per objective j** (from `per_candidate.<j>.perturbed_delta_signed`,
EXCLUDING structural-zero pairs: a perturbed copy whose model input is
identical to its exact copy — design D2, site 206, where the wind
availability never exceeds the 899.9 MW PEM capacity (max 895.48 MW in
`REAL_TIME_wind.csv`), so ±0.1 % on the capacity changes nothing; assert
by comparing the two runs' input md5, and exclude; 6 values δ_ij remain
at 5ca9650 — noise memo `debug/noise-assessment-2026-11-17.md` finding
2): `σ̂_j = sqrt(mean δ_ij²)`, `B_j = max(3·σ̂_j, max_i |δ_ij|)` (with
D2 excluded V1 ≈ 16.2k MWh; E1 ≈ $2.38M; recompute R4 / N1 in code and
print them). A two-run contrast
is READABLE iff `|Δ| ≥ B_j`; for E1/E3 it must also exceed `G_a + G_b`
(`G_run_usd` of the two runs; label GAP-READABLE / WITHIN GAP BOUND —
G_run is an evidence column, never a verdict). If `B_j = 0` (R1; any id
in `ruler_zero`) the objective is reported as an exact value with no
read. `exact_pooled_sd` is a guard: if > 0 for any objective, STOP and
report. No multiplicity correction; the reads are descriptive and no
campaign decision depends on them. The ruler is transferred from the
52 designs (off-slate + nuclear, n = 8, heteroscedastic) — disclosed.

**Interaction (all objectives):** `A_j(m) = Σ_s Δ_j(s(m))`, `I_j(m) =
Δ_j(J(m)) − A_j(m) = y_J − Σ_s y_s + 5·y_b`, ruler `r_I,j = 4·σ̂_j`
(weights 1 + 6 + 25 on per-run chatter σ̂²/2); for E1/E3 the gap bound
is `G_J + Σ_s G_s + 5·G_b` (expected unreadable; stated in advance).
Report I_j in units and as I_j / r_I,j; never a ratio for j ≠ V1.

**Interaction, V1 only:** headline `g(m) = (Σ_s R(s(m)) − R(J(m))) /
R(J(m))` (RTS-screening convention) and secondary `I_rel(m) = (Σ_s R −
R_J) / Σ_s R` (RTS pair-grid convention, ≤ +0.22 there). Positive =
sub-additive. Guard: `R(J) ≥ 3·r_I,V1`, else UNRESOLVED. Reads at each
m: SUB-ADDITIVE iff `g ≥ 0.10` and `(ΣR − R_J) ≥ 2·r_I`;
SUPER-ADDITIVE iff `g ≤ −0.10` and `(ΣR − R_J) ≤ −2·r_I`; ADDITIVE
WITHIN 10 % iff `|g| < 0.10` at all three levels with the guard passed;
UNRESOLVED otherwise. Prediction stated in advance (offline pool model):
g ≈ 0.07 / 0.12 / 0.18 at 60 / 120 / 180.

**Covariate H_C (pre-registered, computed before any Y):** `H_C(x) =
Σ_{h∈C} Σ_s min(mw_s, W_s,h)` with W = `REAL_TIME_wind.csv` (2019) and
C = hours with base_v3 non-PEM WIND curtailment > 1 MWh
(`renewables_hourly.csv`; 4,410 h). Predicted ratios: H_C(b120)/H_C(b275)
at 800 ≈ 1.149; H_C(all)/H_C(b120) — not used (row dropped).

**Location at fixed total (V1, N4; N1 chatter-limited):** raw
`Δ_loc,j = y_j(row 4) − y_j(row 5)` and `y_j(row 7) − y_j(row 8)` and
each 800 row vs row 6. Efficiency `e(x) = R(x)/H_C(x)`. LOCATION EFFECT
iff `|R_a − R_b · H_C,a / H_C,b| ≥ B_V1`; a raw `|Δ_loc| ≥ B_V1` that the
H_C scaling explains is a COMPOSITION effect (host availability /
saturation), not location. The matched-u pair (rows 7–8) is the
design-side check: predicted profile-only difference ≈ 9 rulers in
the pool model; if `|R_7 − R_8 · H_C,7/H_C,8| < B_V1` the one-location
reading stands directly. Same reads for N4 (L252 hours ≥ 99 %, ruler
8.5) as the pocket-congestion read; N1 (all 255 lines, ruler 15, max
perturbed |Δ| 65, wave-D range −63…+102 with no trend) is reported
against `B_N1` and labelled chatter-limited. **Physics prediction:** no
residual location effect for V1 / N4 after H_C scaling; E1 contrasts
WITHIN GAP BOUND at 800 (pair bound ≈ $37–50M); R4 unreadable. A
contradiction is a finding, not an error.

**Saturation probe (row 9):** relief and e(x) at 1,500 MW vs the 4.87
TWh behind-cut pool; descriptive only.

**Scope sentence for the paper (conditional, fixed now):** "On ERCOT we
did not run pair grids. We screened location one site at a time (six
slate wind sites × 60/120/180 MW, identity v3) and tested it directly
with nine runs at 360–1,500 MW total: three all-six joint runs, five
matched-total reallocations (one pair matched on share of nameplate)
and one saturation probe. Network data place all six sites behind one
cut (L252), so differences at matched total are read as [composition
effects explained by host-absorbable energy | a residual location
effect of X × the ruler] (chosen per the §3 read). Per-site
curtailment inside the pocket is an LP tie (identical PTDFs; bus-120
sites 39–58 % curtailed, bus-2/75 sites 4–10 %), so only pocket and
system totals are read. ERCOT-wide location sensitivity rests on the
v1-identity 16-site screening (curtailment relief 25–397 × the v1
replicate ruler of 5,479 MWh; its cost numbers are void,
`INVALID_v1_costs.md`); site 275 (1,039 MW, 1.48 TWh curtailed) is in
the pocket but not in the slate."
