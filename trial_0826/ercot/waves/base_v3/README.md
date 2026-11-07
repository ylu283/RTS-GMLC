# base_v3 — the full-year base run under identity v3 (built 2026-11-07, NOT submitted)

Built by `tools/make_base_v3.py`. Kay submits ON CRC:

    cd trial_0826/ercot/waves/base_v3 && bash submit_this.sh

`submit_this.sh` refuses without `waves/GAP_DECISION.json`, refuses unless
that file says identity v3, prints it, prints `qquota`, and asks for a
literal `yes` before `qsub`.

## 1. Why this run exists

Wave D (`waves/location_oat_v2`) and every later campaign run use solver
identity v3: `ruc_mipgap` 0.001, `ruc_time_limit` 1200 (`waves/GAP_DECISION.json`,
E-D6, Kay 2026-11-06). The only base run on disk (`extracts/base_2019_v2/run_index_1`) uses identity
v2: `ruc_mipgap` 0.01, `ruc_time_limit` 120.

The gap smoke (`analysis/gap_smoke/GAP_SMOKE.md`, task 2 vs task 1, 3 days
scaled by 365/3) shows that the identity change alone moves the base case:

| quantity | 3-day delta | scaled to one year |
|---|---|---|
| total cost | -89,490 $ | about -$10.9M/yr |
| true curtailment | -556.6 MWh | about -68 GWh/yr |
| on/offs (starts) | -16 | about -1,950/yr |

These shifts are the size of a single-site PEM effect ($11.3M median,
`analysis/pool/POOL_V2.md` section 6.1). A delta computed as (v3 run) minus
(v2 base) mixes the PEM effect with the identity effect. Every delta-vs-base
of a v3 run must use a v3 base. This wave makes that base.

## 2. One run suffices

The instrument is deterministic. Exact replicates are byte-identical
(`waves/base_2019_v2` rows 2 and 3 equal row 1; `extracts/smoke_v2` equals
gap-smoke task 1). A second v3 base run would add no information. Do not add
replicates to this wave.

## 3. Row (1)

| row | oat_site | dict | start | days |
|---|---|---|---|---|
| 1 | `__BASE_REPLICATE__` | `{}` | 01-01-2019 | 365 |

`design_matrix.csv` uses the `waves/base_2019_v2` schema. `retrofit_gen_dict_1.json`
is the empty dict: no PEM at any site. The array script aborts if the dict is
not `{}`.

## 4. Identity gate

The array script reads `--ruc_mipgap` / `--ruc_time_limit` from
`waves/GAP_DECISION.json` at RUN time (the wave-D block, unchanged), prints
`IDENTITY from GAP_DECISION.json: ruc_mipgap=... ruc_time_limit=...` into the
task log, and refuses (FAILED marker) if the file is missing. It is also
SMOKE_GATEd on `waves/smoke_v2/SMOKE_PASS`. The collector copies the decision
used to `extracts/base_v3/GAP_DECISION_used.json` and the identity line to
`extracts/base_v3/run_index_1/identity.txt`. Read these two files before you
use this base in any delta.

## 5. Collector and the gz policy

`collect_base_v3.sh` (held on the array; email on this job only):
`extract_ercot.py --full` -> `extracts/base_v3/run_index_1/`, Prescient
`runtimes.csv` copied, wall-clock from the `BASE_V3_START` / `BASE_V3_END`
stamps -> `extracts/base_v3/wallclock.csv`, then ON CRC
`python pool_objectives.py --run-dir <extract> --out <extract>/pool_full_metrics.json`.
Git receives the SLIM tables + `pool_full_metrics.json` + `runtimes.csv` +
`extract_manifest.json` + `identity.txt` + `GAP_DECISION_used.json`. The four
`*.csv.gz` tables stay UNCOMMITTED (`trial_0826/ercot/.gitignore`:
`extracts/base_v3/**/*.csv.gz`; the collector aborts if a gz is staged) in
`$GROUP` storage, listed by name + md5 in `extract_manifest.json`.

Storage: 1 x 51 MB = 51 MB on CRC; about 3 MB in git.

## 6. The v2 base stays

`extracts/base_2019_v2/run_index_1` remains the reference for the 31 identity-v2 runs
(screening_v2, screening_topup, selection_t1_v2, base_2019_v2). Do not
replace it. Do not compare a v2 run with the v3 base, or a v3 run with the
v2 base. Identity v3 runs are never pooled with v2 runs in any claim
(`CONFIG_ERCOT.md`, "Solver identity v3").

## 7. Expected wall-clock

One full-year row at 4 slots. Under v3 the smoke's per-day RUC solve time was
26 s median / 46 s max (`GAP_SMOKE.md`), so the year's RUC time is about 2.6 h
at the median; the v2 full-year base took about 18-27 h wall. Plan for one CRC
day. 1 task x 4 slots = 4 slots, no `-tc`.

## 8. Local checks (zero simulation)

`bash -n` on the three scripts; `tests/test_make_base_v3.py` (one row, dict
`{}`, the array reads `GAP_DECISION.json` and refuses without it, `submit_this.sh`
refuses without it, `.gitignore` line, committed wave == fresh build).
