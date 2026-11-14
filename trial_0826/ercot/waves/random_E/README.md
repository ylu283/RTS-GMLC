# random_E — ERCOT random holdout (prompt 53 v3.1; built 2026-11-13, NOT submitted)

Built by `tools/make_ercot_n0.py` (zero simulation). Design space
`waves/design_space_E.json` (contract 2026-11-13; `waves/DESIGN_SPACE_E.md`).
Kay submits ON CRC, after the wave commit is on `ercot/tx123`:

    cd trial_0826/ercot/waves/random_E && bash submit_this.sh

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

    import numpy
    rng = numpy.random.default_rng(5353)
    U = rng.random((48, 6))          # row-major: row i = site columns in JSON order

i.i.d. uniform over the frozen per-site box (plan section 4); `tier =
"holdout"`, `sobol_index` empty.

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

**Smallest PEM disclosed:** u = 0.0001199 at row 41, site 274 →
0.0895 MW. Every PEM term scales to 0 with MW; the only non-scaling
effect is the structural `_PEM` twin unit (MIP-path noise within the v3 gap):
`DESIGN_SPACE_E.md` section 5.

| index | u_110 | u_140 | u_146 | u_163 | u_270 | u_274 | pem_mw (MW) | sites present |
|---|---|---|---|---|---|---|---|---|
| 1 | 0.3705 | 0.4681 | 0.6577 | 0.7663 | 0.3105 | 0.1078 | 821.27 | 6 |
| 2 | 0.2528 | 0.5346 | 0.7524 | 0.0391 | 0.4633 | 0.7959 | 1290.77 | 6 |
| 3 | 0.8621 | 0.4132 | 0.2398 | 0.0966 | 0.3717 | 0.9789 | 1423.48 | 6 |
| 4 | 0.5118 | 0.5945 | 0.7469 | 0.6439 | 0.2682 | 0.0726 | 851.31 | 6 |
| 5 | 0.4106 | 0.0278 | 0.5545 | 0.0478 | 0.3221 | 0.8342 | 1112.61 | 6 |
| 6 | 0.1959 | 0.6178 | 0.4091 | 0.0572 | 0.2867 | 0.2701 | 709.04 | 6 |
| 7 | 0.1553 | 0.4073 | 0.0090 | 0.0459 | 0.3131 | 0.9589 | 1062.56 | 6 |
| 8 | 0.7693 | 0.0692 | 0.2105 | 0.1403 | 0.9933 | 0.8233 | 1549.88 | 6 |
| 9 | 0.0766 | 0.1386 | 0.0376 | 0.0939 | 0.2291 | 0.6530 | 708.15 | 6 |
| 10 | 0.6274 | 0.6391 | 0.4845 | 0.4512 | 0.5030 | 0.5770 | 1308.01 | 6 |
| 11 | 0.2188 | 0.2018 | 0.2053 | 0.6211 | 0.8048 | 0.7778 | 1341.36 | 6 |
| 12 | 0.6110 | 0.1330 | 0.0418 | 0.2841 | 0.1549 | 0.1788 | 527.30 | 6 |
| 13 | 0.7305 | 0.6591 | 0.7122 | 0.8435 | 0.8591 | 0.3853 | 1544.72 | 6 |
| 14 | 0.3736 | 0.3179 | 0.8210 | 0.8580 | 0.8628 | 0.6571 | 1575.33 | 6 |
| 15 | 0.5439 | 0.7320 | 0.7566 | 0.9465 | 0.9555 | 0.2688 | 1499.66 | 6 |
| 16 | 0.3333 | 0.5285 | 0.2216 | 0.1826 | 0.8555 | 0.1297 | 930.64 | 6 |
| 17 | 0.3416 | 0.8470 | 0.1940 | 0.1731 | 0.4257 | 0.8857 | 1319.56 | 6 |
| 18 | 0.6349 | 0.2716 | 0.7933 | 0.2930 | 0.3127 | 0.1363 | 832.78 | 6 |
| 19 | 0.8117 | 0.2544 | 0.0636 | 0.0024 | 0.1512 | 0.2282 | 614.00 | 6 |
| 20 | 0.8771 | 0.6202 | 0.1825 | 0.9505 | 0.6156 | 0.9067 | 1710.77 | 6 |
| 21 | 0.6643 | 0.7359 | 0.9432 | 0.8813 | 0.8967 | 0.3466 | 1603.42 | 6 |
| 22 | 0.2773 | 0.9128 | 0.8113 | 0.5209 | 0.7605 | 0.5052 | 1454.03 | 6 |
| 23 | 0.0150 | 0.2382 | 0.6318 | 0.5050 | 0.5781 | 0.0822 | 723.82 | 6 |
| 24 | 0.7232 | 0.5671 | 0.6752 | 0.3799 | 0.2713 | 0.8600 | 1437.39 | 6 |
| 25 | 0.6014 | 0.3096 | 0.2828 | 0.3869 | 0.9627 | 0.2862 | 1199.82 | 6 |
| 26 | 0.9411 | 0.8748 | 0.1637 | 0.9008 | 0.7139 | 0.4244 | 1478.86 | 6 |
| 27 | 0.0300 | 0.4706 | 0.3450 | 0.1995 | 0.9189 | 0.5382 | 1191.35 | 6 |
| 28 | 0.6824 | 0.4507 | 0.4343 | 0.6043 | 0.3192 | 0.5130 | 1140.18 | 6 |
| 29 | 0.8700 | 0.1899 | 0.1741 | 0.7795 | 0.2942 | 0.1415 | 809.29 | 6 |
| 30 | 0.4707 | 0.4806 | 0.4689 | 0.8236 | 0.4357 | 0.4494 | 1145.92 | 6 |
| 31 | 0.6598 | 0.9905 | 0.2315 | 0.7238 | 0.6354 | 0.0472 | 1070.97 | 6 |
| 32 | 0.8430 | 0.2534 | 0.7266 | 0.2476 | 0.2661 | 0.5257 | 1136.08 | 6 |
| 33 | 0.4868 | 0.5550 | 0.3749 | 0.9202 | 0.6263 | 0.6239 | 1403.26 | 6 |
| 34 | 0.6938 | 0.7847 | 0.8353 | 0.4557 | 0.7714 | 0.5013 | 1560.69 | 6 |
| 35 | 0.7845 | 0.6349 | 0.2963 | 0.3285 | 0.1709 | 0.7951 | 1257.48 | 6 |
| 36 | 0.6873 | 0.6871 | 0.8018 | 0.9842 | 0.3811 | 0.4189 | 1335.54 | 6 |
| 37 | 0.1190 | 0.3903 | 0.3494 | 0.0261 | 0.8022 | 0.6241 | 1166.90 | 6 |
| 38 | 0.8821 | 0.6087 | 0.4936 | 0.8087 | 0.2535 | 0.5065 | 1258.30 | 6 |
| 39 | 0.9861 | 0.8917 | 0.2107 | 0.2616 | 0.8247 | 0.1883 | 1280.35 | 6 |
| 40 | 0.3735 | 0.9934 | 0.5468 | 0.9842 | 0.2106 | 0.6815 | 1335.08 | 6 |
| 41 | 0.2621 | 0.3472 | 0.5951 | 0.5754 | 0.2865 | 0.0001 | 607.86 | 6 |
| 42 | 0.6509 | 0.7246 | 0.3469 | 0.3342 | 0.5073 | 0.5049 | 1227.48 | 6 |
| 43 | 0.4305 | 0.5433 | 0.0458 | 0.5765 | 0.2496 | 0.6412 | 1024.18 | 6 |
| 44 | 0.0524 | 0.8817 | 0.1231 | 0.1379 | 0.3875 | 0.1257 | 615.40 | 6 |
| 45 | 0.7185 | 0.3896 | 0.2930 | 0.7537 | 0.7272 | 0.5311 | 1376.64 | 6 |
| 46 | 0.7430 | 0.9837 | 0.7965 | 0.2591 | 0.8851 | 0.2578 | 1464.47 | 6 |
| 47 | 0.5985 | 0.3917 | 0.8656 | 0.6912 | 0.6374 | 0.8580 | 1670.40 | 6 |
| 48 | 0.2561 | 0.5411 | 0.8225 | 0.9293 | 0.2468 | 0.4713 | 1109.70 | 6 |

## Holdout rules (plan section 4; pinned AT GENERATION TIME)

- **cov95 bar:** `scipy.stats.binom.interval(0.90, 48, 0.95)` = **[43, 48]**
  (α = 0.10). Trap: `common.binom_band()` defaults to level 0.95 → [42, 48],
  which is wrong here; pass `level = 0.90`.
- **Independence disclosure:** the 48 residuals share one fitted model,
  so the binomial region treats them as independent. This is an
  approximation.
- **Exposure budget:** at most **24** model–holdout scorings in total (one
  scoring = one committed config × one objective × one n0 tier).
- **Retirement:** after 24 scorings, or after prompt 54's committed-config
  grading (`analysis/ercot_gp/committed_configs.json` written), whichever
  comes first. After retirement only deterministic replays of recorded
  scorings are allowed.
- **E-D2 dual role:** random_E is also the random-baseline pool (plan
  section 7). Baseline gradings (model-free, prompt-34 percentile) do NOT
  count against the exposure budget. A model change informed by a baseline
  result is banned.
## Identity (v3)

Every run reads `--ruc_mipgap` / `--ruc_time_limit` from
`waves/GAP_DECISION.json` at RUN time (0.001 / 1200; Kay, E-D6, 2026-11-06),
prints `IDENTITY from GAP_DECISION.json: ...` into the task log (the collector
copies it to `run_index_N/identity.txt`, which the prompt-54 loader requires),
and refuses without the file. SMOKE_GATE on `waves/smoke_v2/SMOKE_PASS`.

## Collector and the gz policy

`collect_random_E.sh` (held on the array; email on this job only): every row
`extract_ercot.py --full` → `extracts/random_E/run_index_N/`, Prescient
`runtimes.csv`, wall-clock from the `RANDOM_E_START` / `RANDOM_E_END` stamps →
`extracts/random_E/wallclock.csv`, the identity line → `identity.txt`, then ON
CRC `pool_objectives.py --run-dir <extract> --out <extract>/pool_full_metrics.json`,
then `COLLECTED`. Git receives the slim tables + `pool_full_metrics.json` +
`runtimes.csv` + `extract_manifest.json` + `GAP_DECISION_used.json` +
`design_matrix_used.csv` + `design_space_E_used.json` + `COLLECTED`; the four
`*.csv.gz` tables stay uncommitted (`.gitignore`:
`extracts/random_E/**/*.csv.gz`; the collector aborts if one is staged).
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
