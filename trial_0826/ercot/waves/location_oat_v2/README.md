# location_oat_v2 — wave D (prompt 58 T2; built 2026-11-06, NOT submitted)

Built by `tools/make_wave_d.py`. Kay submits ON CRC, AFTER `waves/GAP_DECISION.json`
exists (decision E-D6 from `analysis/gap_smoke/GAP_SMOKE.md`):

    cd trial_0826/ercot/waves/location_oat_v2 && bash submit_this.sh

`submit_this.sh` refuses without `GAP_DECISION.json`, prints it, prints
`qquota`, and asks for a literal `yes` before `qsub`.

## 1. Rule (pre-registered; text untouched)

Prompt 36 section 4.2, copied verbatim in `analysis/cost_fix/WAVE_D_TOPK_RULE.md`
(commit 4fb3b1f, before wave B landed). Selection recorded in
`analysis/cost_fix/wave_d_selection.json`: A ruler = 0 (byte-identical
replicates) so the rule reduces to the top 6 by relief per MW: sites
163, 140, 146, 270, 110, 274 (all WIND). Plus nuclear gen 1 (formulation A:
thermal patch, cost-curve band, forced commitment; T0 fix 7c5fb8d is in the
tree and `submit_this.sh` asserts it). Each site alone, other sites absent.
Three ABSOLUTE MW levels, Kay 11-06: 60 / 120 / 180 MW. Every row `--full`
(prompt 36 section 4.2 addendum 11-06; prompt 57 A5).

## 2. Rows (21; order fixed by prompt 58 section 3)

| row | site | type | bus | level | PEM MW | nameplate MW | PEM_fraction |
|---|---|---|---|---|---|---|---|
| 1 | 163 | WIND | 120 | L60 | 60 | 185.4 | 0.32362 |
| 2 | 163 | WIND | 120 | L120 | 120 | 185.4 | 0.64725 |
| 3 | 163 | WIND | 120 | L180 | 180 | 185.4 | 0.97087 |
| 4 | 140 | WIND | 2 | L60 | 60 | 250.6 | 0.23943 |
| 5 | 140 | WIND | 2 | L120 | 120 | 250.6 | 0.47885 |
| 6 | 140 | WIND | 2 | L180 | 180 | 250.6 | 0.71828 |
| 7 | 146 | WIND | 75 | L60 | 60 | 268.0 | 0.22388 |
| 8 | 146 | WIND | 75 | L120 | 120 | 268.0 | 0.44776 |
| 9 | 146 | WIND | 75 | L180 | 180 | 268.0 | 0.67164 |
| 10 | 270 | WIND | 120 | L60 | 60 | 579.0 | 0.10363 |
| 11 | 270 | WIND | 120 | L120 | 120 | 579.0 | 0.20725 |
| 12 | 270 | WIND | 120 | L180 | 180 | 579.0 | 0.31088 |
| 13 | 110 | WIND | 2 | L60 | 60 | 338.6 | 0.17720 |
| 14 | 110 | WIND | 2 | L120 | 120 | 338.6 | 0.35440 |
| 15 | 110 | WIND | 2 | L180 | 180 | 338.6 | 0.53160 |
| 16 | 274 | WIND | 120 | L60 | 60 | 746.4 | 0.08039 |
| 17 | 274 | WIND | 120 | L120 | 120 | 746.4 | 0.16077 |
| 18 | 274 | WIND | 120 | L180 | 180 | 746.4 | 0.24116 |
| 19 | 1 | NUC | 107 | L60 | 60 | 2430.0 | 0.02469 |
| 20 | 1 | NUC | 107 | L120 | 120 | 2430.0 | 0.04938 |
| 21 | 1 | NUC | 107 | L180 | 180 | 2430.0 | 0.07407 |

`PEM_fraction = pem_mw / gen_pmax` (renewable; nameplate from
`data/ercot123_2019_v2/gen.csv`) or `pem_mw / 2430.0` (nuclear). Builder asserts:
max level (180 MW) <= min chosen nameplate (185.4 MW, site 163; the egret
renewable patch clamps silently above nameplate), every fraction <= 1.
Bid 40.0 $/MWh, full year from 01-01-2019, `replicate_of` empty.
`design_matrix.csv` = the screening schema + `pem_mw` + `level_id`.
Retrofit dicts: renewable `{"<site>": {"PEM_bid", "PEM_fraction", "gen_pmax"}}`;
nuclear `{"1": {"PEM_bid", "PEM_fraction"}}` with NO `gen_pmax` key
(`waves/selection_t1_v2/retrofit_gen_dict_6.json` convention).

**Nuclear omega note.** omega = 0.02469 / 0.04938 / 0.07407 for 60 / 120 / 180 MW. These sit below
the Stage-1 0.05 lattice floor. That floor is an RTS convention, not an ERCOT
constraint; the T0 fix 7c5fb8d covers any omega (committed initial output lifted
to the raised p_min). Rows 19-21 are labelled formulation A.

## 3. Identity gate (GP training data runs under the FINAL identity only)

Prompt 53 rule: wave D onward runs under the final solver identity. The array
script reads `--ruc_mipgap` / `--ruc_time_limit` from `waves/GAP_DECISION.json`
at RUN time (python one-liner after `conda activate`), prints
`IDENTITY from GAP_DECISION.json: ruc_mipgap=... ruc_time_limit=...` into every
task log, and refuses (FAILED marker) if the file is missing. It is also
SMOKE_GATEd on `waves/smoke_v2/SMOKE_PASS` like the v2 waves. The collector
copies the decision used to `extracts/location_oat_v2/GAP_DECISION_used.json`
and each task's identity line to `run_index_N/identity.txt`.

## 4. Collector and the gz policy

`collect_location_oat_v2.sh` (held on the array, email on this job only):
every row `extract_ercot.py --full` -> `extracts/location_oat_v2/run_index_N/`,
Prescient `runtimes.csv` copied per row, wall-clock from the `WAVE_D_START` /
`WAVE_D_END` stamps -> `extracts/location_oat_v2/wallclock.csv`, then ON CRC
`python pool_objectives.py --run-dir <extract> --out <extract>/pool_full_metrics.json`
(E8, E9, N5, the commitment-headroom diagnostic, R7/R8, RUC quality, manifest
md5s). Git receives the SLIM tables + `pool_full_metrics.json` + `runtimes.csv`
+ `extract_manifest.json`; the four `*.csv.gz` tables stay UNCOMMITTED
(`trial_0826/ercot/.gitignore`: `extracts/location_oat_v2/**/*.csv.gz`; the
collector aborts if a gz is staged). The gz files stay in `$GROUP` storage and
are listed by name + md5 in each `extract_manifest.json`
(`pool_full_metrics.json` re-hashes them: `manifest.gz_verified`).

Storage: 21 x 51 MB = 1.05 GB of full
extracts on CRC; about 60 MB in git.

## 5. Expected wall-clock

Per row = 365 RUC solves + SCEDs + pricing + overhead. Under the frozen identity
(0.01 / 120) the v2 base RUC solve time was median 19.2 s, max 50.7 s per day
(2.0 h/yr RUC time at the median); the measured v2 full-year runs took about
18-27 h wall each at 4 slots. Under the adopted identity: year RUC time =
365 x the smoke's median (and max) per-day solve time, printed in
`GAP_SMOKE.md` (rule (iii) caps the max-projection at 61 h, about +2.5 CRC
days on a 4-slot run). 21 tasks x 4 slots = 84 slots, no `-tc`.

## 6. Local checks (zero simulation)

`bash -n` on the three scripts; `tests/test_make_wave_d.py` (row count and
order, fractions, the <= 185.4 assert fires at 186, nuclear dict without
`gen_pmax`, the GAP_DECISION refusal of the array block and of
`submit_this.sh`, `.gitignore` line, committed wave == fresh build).
