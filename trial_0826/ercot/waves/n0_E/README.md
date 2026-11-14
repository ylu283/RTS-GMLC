# n0_E — ERCOT Sobol initial design (prompt 53 v3.1; built 2026-11-13, NOT submitted)

Built by `tools/make_ercot_n0.py` (zero simulation). Design space
`waves/design_space_E.json` (contract 2026-11-13; `waves/DESIGN_SPACE_E.md`).
Kay submits ON CRC, after the wave commit is on `ercot/tx123`:

    cd trial_0826/ercot/waves/n0_E && bash submit_this.sh

`submit_this.sh` checks the branch, pulls, refuses without
`waves/GAP_DECISION.json`, `waves/smoke_v2/SMOKE_PASS`,
`waves/design_space_E.json`, the v2 data or the `.gitignore` gz line, prints
the identity and `qquota`, and asks for a literal `yes` before `qsub`. No
dependency between n0_E and random_E.

## Space (d = 6; per-site box [0, gen_pmax] MW; bid 40 $/MWh; 2019 full year)

| site | bus | gen_pmax = upper bound (MW) |
|---|---|---|
| 110 | 2 | np.float64(338.599998942999) |
| 140 | 2 | np.float64(250.5999989428539) |
| 146 | 75 | np.float64(267.9999991911224) |
| 163 | 120 | np.float64(185.3999876467921) |
| 270 | 120 | np.float64(578.9999877407346) |
| 274 | 120 | np.float64(746.3999877635443) |

`gen_pmax` / `bus` asserted equal (1e-6) to the wave-D design matrix at
build. u_s = mw_s / gen_pmax_s = `PEM_fraction`.

## Draw (pinned)

    from scipy.stats import qmc
    S = qmc.Sobol(d=6, scramble=True, seed=53).random_base2(6)   # 64 x 6 in [0, 1)
    U = S[:48]                                                     # this wave

- Rows 1–48 = `sobol_index` 0–47 = the **grading tier** (`tier =
  "grading"` on every row). Rows 1–32 (`sobol_index` 0–31) are the **nav
  candidates**: E-D7 (decided after prompt 54 Part B) sets nav = the first
  32 or all 48. Nav ⊂ grading, so `tier` cannot carry nav without
  making a 32/48 choice early; nav membership is `sobol_index < 32` (or
  `< 48`). Disclosed resolution of contract section 5 (`tier ∈ {nav,
  grading, holdout, bo}`).
- Draw-64-then-slice: the first-32 / first-48 prefixes of `random_base2(6)` equal
  `random(32)` / `random(48)` from a fresh same-seed generator (asserted in
  `tests/test_make_ercot_n0.py`); `random(48)` alone raises scipy's balance
  warning. Rows 48–63 of the block are not used here.
- Pinned env: scipy 1.15.3 (`bogp-botorch`). The draw is bit-identical under
  scipy 1.16.3 (`/opt/anaconda3`, the test interpreter), checked 2026-11-13.

## Rows (48; `__ALL__` multi-site schema, contract section 5)

`design_matrix.csv` columns: `index, oat_site, unit_type, bus, omega, bid, gen_pmax, start_date, num_days, replicate_of, pem_mw, level_id, tier, sobol_index, mw_110, mw_140, mw_146, mw_163, mw_270, mw_274, u_110, u_140, u_146, u_163, u_270, u_274`.
`oat_site = "__ALL__"`, `unit_type` / `bus` / `omega` / `gen_pmax` /
`level_id` / `replicate_of` empty, `bid = 40.0`, `pem_mw = Σ mw_s` (equals
`pool_objectives.pem_mw()` on the retrofit dict), `mw_s = u_s · gen_pmax_s` at
full float precision (17-digit reprs; read with `pd.read_csv(...,
float_precision="round_trip")` for bit-exact values, the default parser is
off by ≤ 1 ulp): no rounding, no snapping, no minimum MW. Retrofit dict
`retrofit_gen_dict_<index>.json` = `{"<site>": {"PEM_bid": 40.0,
"PEM_fraction": u_s, "gen_pmax": gen_pmax_s}}` for every site with mw_s > 0;
a site with mw_s == 0 exactly would be omitted (plan section 2: 0 = absent).
Sites present per row: min 6, max 6 (no draw lands on 0).

**Smallest PEM disclosed:** u = 0.001044 at row 14, site 163 →
0.1936 MW. Every PEM term scales to 0 with MW; the only non-scaling
effect is the structural `_PEM` twin unit (MIP-path noise within the v3 gap):
`DESIGN_SPACE_E.md` section 5.

| index | sobol_index | u_110 | u_140 | u_146 | u_163 | u_270 | u_274 | pem_mw (MW) | sites present |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 0 | 0.1621 | 0.4216 | 0.0767 | 0.0888 | 0.6335 | 0.1875 | 704.35 | 6 |
| 2 | 1 | 0.9901 | 0.8596 | 0.6646 | 0.8927 | 0.3165 | 0.6912 | 1593.40 | 6 |
| 3 | 2 | 0.6935 | 0.1904 | 0.4015 | 0.4232 | 0.0525 | 0.8645 | 1144.23 | 6 |
| 4 | 3 | 0.3967 | 0.5288 | 0.8722 | 0.6187 | 0.9932 | 0.3658 | 1463.40 | 6 |
| 5 | 4 | 0.2760 | 0.0706 | 0.5798 | 0.7188 | 0.8310 | 0.0090 | 887.66 | 6 |
| 6 | 5 | 0.5728 | 0.6483 | 0.1794 | 0.2899 | 0.1545 | 0.5104 | 928.61 | 6 |
| 7 | 6 | 0.8684 | 0.2862 | 0.8791 | 0.7613 | 0.4844 | 0.9337 | 1719.87 | 6 |
| 8 | 7 | 0.0404 | 0.9947 | 0.3458 | 0.1908 | 0.5343 | 0.4372 | 1026.71 | 6 |
| 9 | 8 | 0.1043 | 0.1419 | 0.9427 | 0.3624 | 0.2858 | 0.3103 | 787.82 | 6 |
| 10 | 9 | 0.8074 | 0.5770 | 0.2845 | 0.6835 | 0.7270 | 0.8110 | 1647.26 | 6 |
| 11 | 10 | 0.5089 | 0.4962 | 0.5164 | 0.1490 | 0.9001 | 0.6337 | 1456.83 | 6 |
| 12 | 11 | 0.3370 | 0.7848 | 0.2410 | 0.8285 | 0.0835 | 0.1360 | 678.79 | 6 |
| 13 | 12 | 0.4587 | 0.3659 | 0.4633 | 0.9472 | 0.2486 | 0.4892 | 1055.84 | 6 |
| 14 | 13 | 0.6306 | 0.9153 | 0.8090 | 0.0010 | 0.7991 | 0.9915 | 1862.63 | 6 |
| 15 | 14 | 0.9282 | 0.0273 | 0.0156 | 0.5336 | 0.5660 | 0.5643 | 1173.12 | 6 |
| 16 | 15 | 0.2250 | 0.6919 | 0.7285 | 0.4791 | 0.3899 | 0.0648 | 807.77 | 6 |
| 17 | 16 | 0.1929 | 0.0602 | 0.2595 | 0.7945 | 0.9527 | 0.9463 | 1555.15 | 6 |
| 18 | 17 | 0.8959 | 0.7209 | 0.9841 | 0.2241 | 0.0032 | 0.4485 | 1125.92 | 6 |
| 19 | 18 | 0.6628 | 0.3290 | 0.2150 | 0.6934 | 0.3619 | 0.1228 | 794.24 | 6 |
| 20 | 19 | 0.4909 | 0.8901 | 0.5568 | 0.2646 | 0.6858 | 0.6235 | 1450.04 | 6 |
| 21 | 20 | 0.3693 | 0.4631 | 0.7720 | 0.3979 | 0.5212 | 0.7518 | 1384.69 | 6 |
| 22 | 21 | 0.5410 | 0.7556 | 0.4849 | 0.5933 | 0.4624 | 0.2524 | 1068.60 | 6 |
| 23 | 22 | 0.7752 | 0.1787 | 0.6905 | 0.1221 | 0.1647 | 0.1767 | 742.19 | 6 |
| 24 | 23 | 0.0721 | 0.6021 | 0.0362 | 0.9258 | 0.8481 | 0.6791 | 1354.56 | 6 |
| 25 | 24 | 0.0100 | 0.2532 | 0.6273 | 0.5044 | 0.0976 | 0.5520 | 796.99 | 6 |
| 26 | 25 | 0.8382 | 0.9656 | 0.0981 | 0.4498 | 0.9211 | 0.0533 | 1208.52 | 6 |
| 27 | 26 | 0.6031 | 0.1074 | 0.8359 | 0.9844 | 0.7178 | 0.3750 | 1333.15 | 6 |
| 28 | 27 | 0.3062 | 0.6734 | 0.4238 | 0.0381 | 0.2678 | 0.8786 | 1203.92 | 6 |
| 29 | 28 | 0.4269 | 0.2233 | 0.1537 | 0.1861 | 0.4314 | 0.7462 | 1082.93 | 6 |
| 30 | 29 | 0.7238 | 0.5578 | 0.6204 | 0.8657 | 0.6143 | 0.2496 | 1253.68 | 6 |
| 31 | 30 | 0.9599 | 0.3847 | 0.3210 | 0.3331 | 0.7547 | 0.3214 | 1246.07 | 6 |
| 32 | 31 | 0.1318 | 0.8344 | 0.9207 | 0.6543 | 0.1954 | 0.8228 | 1349.06 | 6 |
| 33 | 32 | 0.1477 | 0.2145 | 0.5141 | 0.9121 | 0.5623 | 0.8929 | 1402.69 | 6 |
| 34 | 33 | 0.9445 | 0.5040 | 0.2269 | 0.1084 | 0.4874 | 0.3925 | 1102.20 | 6 |
| 35 | 34 | 0.7391 | 0.4286 | 0.9648 | 0.5757 | 0.1277 | 0.0385 | 825.67 | 6 |
| 36 | 35 | 0.4111 | 0.8529 | 0.3105 | 0.3803 | 0.8263 | 0.5360 | 1385.17 | 6 |
| 37 | 36 | 0.2894 | 0.3089 | 0.0169 | 0.2783 | 0.9746 | 0.8393 | 1422.29 | 6 |
| 38 | 37 | 0.6175 | 0.9724 | 0.7416 | 0.7070 | 0.0402 | 0.3367 | 1057.17 | 6 |
| 39 | 38 | 0.8237 | 0.0791 | 0.4422 | 0.2417 | 0.3369 | 0.2327 | 830.80 | 6 |
| 40 | 39 | 0.0270 | 0.6392 | 0.7840 | 0.8120 | 0.6447 | 0.7324 | 1449.88 | 6 |
| 41 | 40 | 0.0860 | 0.4739 | 0.3806 | 0.6406 | 0.3942 | 0.6089 | 1051.38 | 6 |
| 42 | 41 | 0.7579 | 0.8074 | 0.8474 | 0.3194 | 0.5932 | 0.1056 | 1167.55 | 6 |
| 43 | 42 | 0.5584 | 0.1329 | 0.0783 | 0.8481 | 0.7956 | 0.4635 | 1207.20 | 6 |
| 44 | 43 | 0.3553 | 0.5855 | 0.6779 | 0.1685 | 0.2212 | 0.9620 | 1326.01 | 6 |
| 45 | 44 | 0.4760 | 0.0026 | 0.9009 | 0.0518 | 0.0719 | 0.6628 | 949.21 | 6 |
| 46 | 45 | 0.6791 | 0.7160 | 0.3716 | 0.9980 | 0.8802 | 0.1611 | 1323.88 | 6 |
| 47 | 46 | 0.8796 | 0.3593 | 0.5772 | 0.4673 | 0.7389 | 0.2691 | 1257.85 | 6 |
| 48 | 47 | 0.2077 | 0.9223 | 0.1651 | 0.5219 | 0.3050 | 0.7658 | 1190.66 | 6 |

## Identity (v3)

Every run reads `--ruc_mipgap` / `--ruc_time_limit` from
`waves/GAP_DECISION.json` at RUN time (0.001 / 1200; Kay, E-D6, 2026-11-06),
prints `IDENTITY from GAP_DECISION.json: ...` into the task log (the collector
copies it to `run_index_N/identity.txt`, which the prompt-54 loader requires),
and refuses without the file. SMOKE_GATE on `waves/smoke_v2/SMOKE_PASS`.

## Collector and the gz policy

`collect_n0_E.sh` (held on the array; email on this job only): every row
`extract_ercot.py --full` → `extracts/n0_E/run_index_N/`, Prescient
`runtimes.csv`, wall-clock from the `N0_E_START` / `N0_E_END` stamps →
`extracts/n0_E/wallclock.csv`, the identity line → `identity.txt`, then ON
CRC `pool_objectives.py --run-dir <extract> --out <extract>/pool_full_metrics.json`,
then `COLLECTED`. Git receives the slim tables + `pool_full_metrics.json` +
`runtimes.csv` + `extract_manifest.json` + `GAP_DECISION_used.json` +
`design_matrix_used.csv` + `design_space_E_used.json` + `COLLECTED`; the four
`*.csv.gz` tables stay uncommitted (`.gitignore`:
`extracts/n0_E/**/*.csv.gz`; the collector aborts if one is staged).
Objectives come from `pool_objectives.pool_row(key)` on the slim tables
(prompt 54 loader), never from `pool_full_metrics.json`.

## Budget (wave-D actuals, `analysis/pool/ERCOT_POOL_STANDINGS.md` section 8)

Per full-year v3 run at 4 slots: fast node ≈ 5.3 h wall / 21 core-h
(15 of 21 wave-D rows); slow node 10.5–11.8 h / 44.6 core-h mean (6 rows).
The plan section 8 projection was 32–40 core-h (AMENDMENT 2026-11-06b,
January days). n0_E + random_E = 96 runs ≈ 2.0k (all fast) – 4.3k (all
slow) core-h; this wave is 48 runs ≈ 1.0k – 2.1k core-h, 192 slots, about
5–12 h calendar if the queue grants the slots at once. Both E waves can run
concurrently with each other and with noise_v3 B and base_v3.

Storage: 96 x 51 MB ≈ 4.9 GB of `--full` extracts in $GROUP storage for the
two E waves (this wave: 48 x 51 MB ≈ 2.4 GB; wave D was 1.07 GB). `--full`
is kept because E8 / E9 / N5 and the headroom diagnostics need `bus_lmps` /
`thermal`; `line_summary.csv` (N1) is written in slim mode too
(`extract_ercot.py:245`). About 3 MB per row in git.

## Local checks (zero simulation)

`bash -n` on the scripts; `/opt/anaconda3/bin/python -m pytest
tests/test_make_ercot_n0.py tests/test_pool_objectives.py -q`.

## Deviations

- `tier` is "grading" on all 48 n0_E rows; nav membership is carried by
  `sobol_index` until E-D7 (above).
- The scripts are the noise_v3 templates at the wave-D directory depth
  (`waves/<wave>`, `HEADER` from `make_v2_waves.py`); the nuclear T0-fix
  ancestor check is dropped (no nuclear rows) and a `design_space_E.json`
  presence check is added. The collector also copies `design_space_E.json`
  into the extract.
