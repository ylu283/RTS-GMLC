# screening_v3 — 16-site screening under identity v3 (prompt 62 Part C; NOT submitted)

Built by `tools/make_screening_v3.py` (zero simulation). Kay submits ON CRC after
the wave commit is fast-forwarded and pushed:

    cd trial_0826/ercot/waves/screening_v3 && bash submit_this.sh

`submit_this.sh` refuses without `waves/GAP_DECISION.json`, prints it, prints
`qquota`, and asks for a literal `yes` before `qsub`. 11 tasks x 4 slots =
44 slots (`-q long -pe smp 4 -r n`); collector `--full` on every row
(11 x 51 MB = 561 MB on CRC; gz stay out of git).

Analysis-only: these rows never enter the GP's X, the HV ledger, the holdout or
the random baseline. Part C is disclosure; E-D3 (the slate) is not reopened.

## 1. Rows (11)

Rows 1-10 = ranks 7-16 of `analysis/cost_fix/wave_d_selection.json` (read from
the file), each site alone at 180 MW (`omega = 180 / gen_pmax`, bid 40.0, full
year from 01-01-2019, `level_id = L180`). The six slate sites already have L180
rows in wave D (`location_oat_v2` rows 3, 6, 9, 12, 15, 18). Row 11 replicates
wave-D row 3 (site 163 L180): its `overall.csv` md5 must equal wave D's at
landing (no code or data drift since 11-06; also the within-wave anchor for the
saturation row). No L60 level.

| row | site | type | bus | level | PEM MW | nameplate MW | PEM_fraction | replicate_of | flag |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 275 | WIND | 120 | L180 | 180 | 1039.0 | 0.17324 | - |  |
| 2 | 116 | PV | 120 | L180 | 180 | 199.3 | 0.90301 | - | saturation (omega >= 0.9) |
| 3 | 59 | PV | 26 | L180 | 180 | 491.7 | 0.36610 | - |  |
| 4 | 30 | PV | 26 | L180 | 180 | 926.7 | 0.19424 | - |  |
| 5 | 142 | PV | 14 | L180 | 180 | 703.3 | 0.25592 | - |  |
| 6 | 91 | WIND | 94 | L180 | 180 | 785.5 | 0.22915 | - |  |
| 7 | 205 | WIND | 77 | L180 | 180 | 1058.0 | 0.17013 | - |  |
| 8 | 206 | WIND | 22 | L180 | 180 | 1799.8 | 0.10001 | - |  |
| 9 | 204 | WIND | 28 | L180 | 180 | 857.0 | 0.21004 | - |  |
| 10 | 20 | WIND | 32 | L180 | 180 | 780.2 | 0.23071 | - |  |
| 11 | 163 | WIND | 120 | L180 | 180 | 185.4 | 0.97087 | location_oat_v2:3 | saturation (omega >= 0.9) |

Retrofit dicts: `{"<site>": {"PEM_bid", "PEM_fraction", "gen_pmax"}}` for WIND
and PV alike (`parameters.py::_update_renewable_generator` needs gen_pmax and
p_min = 0; every screened site has PMin 0).

## 2. Pre-registered covariates (`covariates.csv`; computed at build from inputs only)

Per site, all 16 screened sites: tier (pocket_120 / wind_near / pv_pocket /
far), slate flag, the row that carries its L180 value, `H_C(s, 180)` = sum over
the 4,410 base_v3 WIND-curtailment hours (> 1 MWh) of
`min(180, W_s,h)` (W = `REAL_TIME_wind.csv` for WIND, `REAL_TIME_solar.csv` for
PV — prompt 61 defined W for wind only; the PV substitution is disclosed),
base_v3 own-site curtailment (`gen_summary.csv`), and the DC PTDF of the site
bus on the pocket lines (`pocket_lines(120)`) and on every base_v3 line with
`hours_ge_99pct > 0`. `bus.csv` has no Ref bus, so the PTDF uses a
load-weighted distributed slack (mean 2019 hourly load per bus,
`REAL_TIME_load.csv`); B from branch reactance X; positive = From -> To.

## 3. Prompt 62 §4.4–§4.5 (verbatim)

4. **Wave commit — STOP — Kay action:** `git rebase ercot/tx123`,
   report the SHA; strategy fast-forwards; Kay pushes and on CRC `cd
   trial_0826/ercot/waves/screening_v3 && bash submit_this.sh` (may go
   up together with 61's wave; 44 + 36 slots). **Pre-computed BEFORE any
   Y, committed with the wave as `waves/screening_v3/covariates.csv`:**
   per site `H_C(s, 180)` (61 §3 definition), base_v3 own-site
   curtailment, DC PTDF of the site bus on the pocket lines
   (`pocket_lines(120)`) and on every base_v3 line with
   `hours_ge_99pct > 0` (from `branch.csv`/`bus.csv`).
5. **Landing analysis `analysis/pool/SCREENING_V3.md` + csv (after
   COLLECTED and the strategy session's tx123 update; reader
   `ps.build_wave("screening_v3")`; `ercot_gp_loader.suspect_flag` as
   cross-check):** for each graded j (B_j > 0) with d_s = Δ_j(s, 180) vs
   base_v3 over 16 sites:
   - **Tiers (pre-registered from SCREENING_ERCOT.md, no Y):** pocket_120
     {163, 270, 274, 275, 116}, wind_near {110, 140, 146} (buses 2/75),
     pv_pocket {30, 59, 142} (buses 26/14), far {91, 205, 206, 204, 20}.
     Primary contrast: C = pocket_120 ∪ wind_near (8) vs U = far (5);
     Hodges–Lehmann shift HL (median of the 40 differences), exact
     two-sided Mann–Whitney p (`mannwhitneyu(method="exact")`), exact 95 %
     Moses interval. **LOCATIONAL** iff Holm-adjusted p ≤ 0.05 across the
     graded ids AND `|HL| ≥ 2·B_j` AND the interval excludes 0; two-sided
     (far sites may cost more for less relief). Also: HL/B_j,
     rank-biserial r, WIND-only sensitivity (7 vs 5), Kruskal–Wallis over
     the four tiers (descriptive). Disclose the PV/WIND and ω (0.10–0.97)
     confounds. No ratio for any j; V1 relief/MW is reported as a column.
   - **Covariates:** Spearman of d_s with H_C, own-site base
     curtailment and the PTDF columns; ΔV1 decomposed per run into
     own-site (parent + twin of the retrofitted unit) and other-site
     components from `gen_summary` (own-site relief at high ω is partly
     accounting reclassification).
   - **E1 per site:** GAP-READABLE vs `G_site + G_base`.
   - **MATCHED-MW RANKING vs E-D3 SLATE** (renamed; v2 ranked at ω ≈
     0.5 so a different order is expected from the protocol alone):
     tie band `B_V1/180 ≈ 90 MWh/MW`; **SLATE BUS-SET HOLDS** iff the v3
     top-6 by relief/MW at 180 MW lie on buses {120, 2, 75}; site
     membership reported with TIED marks. **Prediction stated now:** 275
     enters and 163 leaves (ω saturation); the bus set holds. Kendall
     τ_b between v2 and v3 ranks on the 16 sites with exact p
     (descriptive). E-D3 stands in every case.
   - **Dominance read:** a non-slate site is BO-relevant only if its
     L180 Δ vector on the seated objectives (B_j units) is not dominated
     by some slate site's; all dominated → "slate exclusion justified on
     all seated objectives"; any non-dominated → disclosed + PI flag;
     E-D3 not reopened in this campaign.

## 4. Identity gate and collector

Same machinery as wave D (`tools/make_wave_d.py`): the array reads
`--ruc_mipgap` / `--ruc_time_limit` from `waves/GAP_DECISION.json` at RUN time
and refuses without it; SMOKE_GATEd on `waves/smoke_v2/SMOKE_PASS`; task stamps
`SCREENING_V3_START` / `SCREENING_V3_END`. Collector: every row `--full` ->
`extracts/screening_v3/run_index_N/`, `runtimes.csv`, wall-clock, per-run
`pool_full_metrics.json` on CRC; git receives the slim tables only
(`trial_0826/ercot/.gitignore`: `extracts/screening_v3/**/*.csv.gz`).
