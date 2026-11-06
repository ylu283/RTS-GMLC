# noise_v3 — ERCOT noise measurement (prompt 52 v2.1; built 2026-11-06, NOT submitted)

Built by `tools/make_noise_v3.py --layout 12`. Kay submits ON CRC, batch A
first, batch B after batch A's collector email:

    cd trial_0826/ercot/waves/noise_v3/A && bash submit_this.sh
    cd trial_0826/ercot/waves/noise_v3/B && bash submit_this.sh

Each `submit_this.sh` refuses without `waves/GAP_DECISION.json`, prints it,
prints `qquota`, and asks for a literal `yes` before `qsub`. Batch B's script
also refuses until `extracts/noise_v3/A/COLLECTED` is in the tree (batch A's
collector writes and pushes it).

## 1. Purpose

Measure ERCOT run-to-run reproducibility per objective under the campaign
identity, and the response of each objective to a 0.1 % input move. Two
populations, never pooled (prompt 52 section 1):

- EXACT cross-batch pairs (A vs B) = the noise population (tau). Expected
  exact sd = 0 on this deterministic instrument. "If their sd is 0, τ
  collapses toward 0 and the stop rule becomes budget-cap-only — that is a
  FINDING about a deterministic instrument, stated in exactly those words,
  not a failure."
- PERTURBED copies (delta = 0.001 relative on `pem_mw`) = local input
  sensitivity: the replacement ruler `ruler_j` of prompt 57 section 3 A4 and
  the robustness rider's sensitivity level (ERCOT_BO_PLAN.md section 7).

## 2. Identity (v3)

Every run reads `--ruc_mipgap` / `--ruc_time_limit` from `waves/GAP_DECISION.json`
at RUN time (`ruc_mipgap 0.001`, `ruc_time_limit 1200`; Kay, E-D6, 2026-11-06),
prints `IDENTITY from GAP_DECISION.json: ...` into every task log, and refuses
without the file. Gate G1 of prompt 52 is MET by `analysis/gap_smoke/GAP_SMOKE.md`
(control arm byte-identical to smoke_v2; tolerance verified per RUC day; 0
time-limit hits) and ERCOT_BO_PLAN.md AMENDMENT 2026-11-06b. SMOKE_GATE on
`waves/smoke_v2/SMOKE_PASS`. Fix 7c5fb8d asserted (nuclear rows).

## 3. Pick (pre-registered rule, `PICK_RULE.md`; table `pick_table.csv`)

Rule text was written before the pick ran; v2-identity values chose designs
ONLY (disclosed in PICK_RULE.md) and never enter ERCOT_NOISE.md. Score =
mean achieved spread over the 19 used candidates = 0.879
(E8, E9, N5 NOT USED: no v2 value on slim extracts).

| design | v2 origin | site | type | PEM MW | nameplate MW | omega |
|---|---|---|---|---|---|---|
| D1 | screening_v2/ercot:1 (D02) | 275 | WIND | 519.5000 | 1039.0 | 0.500000 |
| D2 | screening_v2/ercot:7 (D08) | 206 | WIND | 899.9000 | 1799.8 | 0.500000 |
| D3 | screening_v2/topup:4 (D15) | 146 | WIND | 134.0000 | 268.0 | 0.500000 |
| D4 | selection_t1_v2:10 (D23) | 1 | NUC | 2430.0000 | 2430.0 | 1.000000 |

Achieved spread per candidate (1.00 = the pick holds the pool's min and max):

| candidate | used | achieved spread | pool min (design) | pool max (design) | picked min (design) | picked max (design) |
|---|---|---|---|---|---|---|
| V1 | yes | 1.00 | -1.774e+06 (screening_v2/ercot:1) | 5.32e+04 (selection_t1_v2:9) | -1.774e+06 (screening_v2/ercot:1) | 5.225e+04 (selection_t1_v2:10) |
| E1 | yes | 0.51 | -3.455e+08 (selection_t1_v2:6) | 3.587e+08 (selection_t1_v2:10) | -3.594e+06 (screening_v2/topup:4) | 3.587e+08 (selection_t1_v2:10) |
| X1 | yes | 0.97 | 6.186e+04 (screening_v2/topup:6) | 8.002e+06 (selection_t1_v2:10) | 2.721e+05 (screening_v2/topup:4) | 8.002e+06 (selection_t1_v2:10) |
| R4 | yes | 0.83 | -1420 (selection_t1_v2:10) | -86 (screening_v2/topup:6) | -1420 (selection_t1_v2:10) | -308 (screening_v2/topup:4) |
| N1 | yes | 1.00 | -232 (screening_v2/ercot:1) | 3977 (selection_t1_v2:10) | -232 (screening_v2/ercot:1) | 3977 (selection_t1_v2:10) |
| E4 | yes | 0.95 | 3.99e+06 (screening_v2/topup:2) | 2.491e+08 (selection_t1_v2:10) | 1.578e+07 (screening_v2/topup:4) | 2.491e+08 (selection_t1_v2:10) |
| R2 | yes | 1.00 | -328.3 (screening_v2/ercot:1) | 223.6 (screening_v2/topup:4) | -328.3 (screening_v2/ercot:1) | 223.6 (screening_v2/topup:4) |
| R7 | yes | 1.00 | -1.643e+06 (screening_v2/topup:4) | 3.719e+06 (selection_t1_v2:10) | -1.643e+06 (screening_v2/topup:4) | 3.719e+06 (selection_t1_v2:10) |
| N4 | yes | 1.00 | -413 (screening_v2/ercot:1) | 297 (selection_t1_v2:9) | -413 (screening_v2/ercot:1) | 296 (selection_t1_v2:10) |
| N5 | NOT USED (no v2 value: slim extracts) | | | | | |
| E6 | yes | 0.97 | -5.281e+07 (screening_v2/ercot:2) | 6.736e+07 (selection_t1_v2:10) | -4.875e+07 (screening_v2/ercot:7) | 6.736e+07 (selection_t1_v2:10) |
| R5 | yes | 1.00 | -1.55e+05 (selection_t1_v2:10) | 793 (screening_v2/topup:4) | -1.55e+05 (selection_t1_v2:10) | 793 (screening_v2/topup:4) |
| N3 | yes | 0.89 | -54.97 (selection_t1_v2:10) | 33.34 (selection_t1_v2:6) | -54.97 (selection_t1_v2:10) | 23.84 (screening_v2/ercot:1) |
| E2 | yes | 0.66 | -1.281e+08 (selection_t1_v2:6) | 8.17e+06 (screening_v2/ercot:7) | -8.127e+07 (selection_t1_v2:10) | 8.17e+06 (screening_v2/ercot:7) |
| R6 | yes | 1.00 | -3.064e+05 (screening_v2/ercot:7) | 5.718e+05 (selection_t1_v2:10) | -3.064e+05 (screening_v2/ercot:7) | 5.718e+05 (selection_t1_v2:10) |
| N2 | yes | 0.60 | -4 (screening_v2/ercot:5) | 1 (selection_t1_v2:6) | -3 (screening_v2/ercot:1) | 0 (screening_v2/topup:4) |
| E3 | yes | 0.63 | -2.173e+08 (selection_t1_v2:6) | 4.399e+08 (selection_t1_v2:10) | 2.61e+07 (screening_v2/topup:4) | 4.399e+08 (selection_t1_v2:10) |
| R8 | yes | 0.83 | -3959 (screening_v2/topup:4) | 7077 (selection_t1_v2:9) | -3959 (screening_v2/topup:4) | 5192 (selection_t1_v2:10) |
| E7 | yes | 0.93 | 0.02177 (screening_v2/topup:2) | 0.6982 (selection_t1_v2:10) | 0.069 (screening_v2/topup:4) | 0.6982 (selection_t1_v2:10) |
| E8 | NOT USED (no v2 value: slim extracts) | | | | | |
| E9 | NOT USED (no v2 value: slim extracts) | | | | | |
| V2 | yes | 0.93 | -0.5808 (screening_v2/ercot:2) | 0.01174 (selection_t1_v2:7) | -0.5638 (screening_v2/ercot:7) | -0.01361 (selection_t1_v2:10) |

Where several candidates show the same designs at min and max, they are
correlated and the strata collapse (prompt 52 section 3: made visible).

## 4. Rows (12: batch A 8, batch B 4; layout 12)

| batch | row | design | site | type | bus | copy | sign | delta_rel | PEM MW | nameplate MW | PEM_fraction |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A | 1 | D1 (screening_v2/ercot:1) | 275 | WIND | 120 | exact | +0 | 0.000 | 519.5000 | 1039.0 | 0.500000 |
| A | 2 | D2 (screening_v2/ercot:7) | 206 | WIND | 22 | exact | +0 | 0.000 | 899.9000 | 1799.8 | 0.500000 |
| A | 3 | D3 (screening_v2/topup:4) | 146 | WIND | 75 | exact | +0 | 0.000 | 134.0000 | 268.0 | 0.500000 |
| A | 4 | D4 (selection_t1_v2:10) | 1 | NUC | 107 | exact | +0 | 0.000 | 2430.0000 | 2430.0 | 1.000000 |
| A | 5 | D1 (screening_v2/ercot:1) | 275 | WIND | 120 | perturbed | +1 | 0.001 | 520.0195 | 1039.0 | 0.500500 |
| A | 6 | D2 (screening_v2/ercot:7) | 206 | WIND | 22 | perturbed | +1 | 0.001 | 900.7999 | 1799.8 | 0.500500 |
| A | 7 | D3 (screening_v2/topup:4) | 146 | WIND | 75 | perturbed | -1 | 0.001 | 133.8660 | 268.0 | 0.499500 |
| A | 8 | D4 (selection_t1_v2:10) | 1 | NUC | 107 | perturbed | -1 | 0.001 | 2427.5700 | 2430.0 | 0.999000 |
| B | 1 | D1 (screening_v2/ercot:1) | 275 | WIND | 120 | exact | +0 | 0.000 | 519.5000 | 1039.0 | 0.500000 |
| B | 2 | D2 (screening_v2/ercot:7) | 206 | WIND | 22 | exact | +0 | 0.000 | 899.9000 | 1799.8 | 0.500000 |
| B | 3 | D3 (screening_v2/topup:4) | 146 | WIND | 75 | exact | +0 | 0.000 | 134.0000 | 268.0 | 0.500000 |
| B | 4 | D4 (selection_t1_v2:10) | 1 | NUC | 107 | exact | +0 | 0.000 | 2430.0000 | 2430.0 | 1.000000 |

`PEM_fraction = pem_mw / gen_pmax` (renewable; nameplate from the v2 design
matrix) or `pem_mw / 2430.0` (nuclear). Exact copies carry the v2 design's
`omega` byte-for-byte. Perturbed copies: `pem_mw x (1 + sign x delta_rel)`,
sign from `numpy.random.default_rng(52)` (column `perturb_seed`), inward
at 0 and at nameplate (PICK_RULE.md). `replicate_of` = the v2 origin row for
every copy; `copy_type` tells exact from perturbed. Bid 40.0 $/MWh, full
year from 01-01-2019. Retrofit dicts: renewable `{"<site>": {"PEM_bid",
"PEM_fraction", "gen_pmax"}}`; nuclear `{"1": {"PEM_bid", "PEM_fraction"}}`
with NO `gen_pmax` key. Nuclear rows: A:4 exact omega=1.000000, A:8 perturbed omega=0.999000, B:4 exact omega=1.000000.

## 5. Batch split — resolution (DEVIATION to confirm)

Prompt 52 section 3 says "4 designs x 3 copies (1 exact + 2 perturbed) ~ 12
runs" in "TWO submission batches"; v2.1 says the exact copies "form the
cross-batch exact pairs between batch A and batch B"; ERCOT_BO_PLAN.md
section 3 pins only "tau population = EXACT cross-batch replicates" and
section 8 counts 12 replicate runs. Under v3 an exact v3 copy has no v3
partner unless a second exact copy runs, so 12 rows cannot hold both 4
cross-batch exact pairs and 8 perturbed copies. Resolution built here
(layout 12): per design, exact in A, exact in B (the pair), one perturbed in
A — batch A 8 rows, batch B 4 rows; the ruler population is 4 values
(one per design), not the 8 of prompt 57 A4, and per-level sd has 1 df.
Alternative kept in the builder: `python tools/make_noise_v3.py --layout 16`
adds one antithetic perturbed copy per design to batch B (8 + 8 rows; ruler
population 8; 16 x 36 core-h). Kay confirms the layout before submitting A;
`analysis/noise_v3/read_noise.py` reads either.

## 6. Collector and the gz policy

`collect_noise_v3_<batch>.sh` (held on the batch array; email on this job
only): every row `extract_ercot.py --full` -> `extracts/noise_v3/<batch>/run_index_N/`,
Prescient `runtimes.csv` per row, wall-clock from the `NOISE_V3_START` /
`NOISE_V3_END` stamps -> `extracts/noise_v3/<batch>/wallclock.csv`, the identity
line -> `run_index_N/identity.txt`, then ON CRC `python pool_objectives.py
--run-dir <extract> --out <extract>/pool_full_metrics.json` (E8, E9, N5,
headroom, R7/R8, RUC quality, manifest md5s), then the `COLLECTED` marker.
Git receives the SLIM tables + `pool_full_metrics.json` + `runtimes.csv` +
`extract_manifest.json` + `GAP_DECISION_used.json` + `design_matrix_used.csv`
+ `COLLECTED`; the four `*.csv.gz` tables stay UNCOMMITTED
(`trial_0826/ercot/.gitignore`: `extracts/noise_v3/**/*.csv.gz`; the collector
aborts if a gz is staged).

Storage: 12 x 51 MB = 0.60 GB of full extracts on CRC;
about 36 MB in git.

## 7. Expected wall-clock

Projected full-year run at v3: 8–10 h wall / 32–40 core-h at 4 slots
(ERCOT_BO_PLAN.md AMENDMENT 2026-11-06b, from the January smoke days; replace
with wave-D actuals when they land). Batch A: 8 x 4 = 32 slots; batch B:
4 x 4 = 16 slots; no `-tc`. The collector's `wallclock.csv` feeds the
plan section 8 budget actuals (`read_noise.py` prints core-h per run).

## 8. After both batches land (local, zero simulation)

    cd trial_0826/ercot && python analysis/noise_v3/read_noise.py

writes `analysis/noise_v3/ERCOT_NOISE.md` + `ercot_noise.csv/json` +
`ercot_noise_cov.csv` (exact-pair |Δ|, perturbed |Δ| population = ruler_j,
pooled and per-level sd with CIs, per-objective trigger, covariance matrix,
shed ≡ 0 assert, runtime table).

## 9. Local checks (zero simulation)

`bash -n` on the six scripts; `tests/test_make_noise_v3.py` (row counts and
batches, delta inward at the bounds, nuclear dict without `gen_pmax`, pick
table spread columns, GAP_DECISION refusal, batch-B COLLECTED refusal,
`.gitignore` line, committed wave == fresh build).
