# noise_seed_E — Gurobi-Seed replicates + thread checks at 4 n0_E designs (prompt 63 v1; NOT submitted)

Built by `tools/make_noise_seed_E.py` (zero simulation). **ANALYSIS-ONLY:**
new Y at existing n0_E X; these rows never enter the GP training set, the HV
ledger, the random baseline or any validation tier (`tier = "contrast"`,
contract 11-17 addendum). Kay submits ON CRC, after the wave commit is on
`ercot/tx123`:

    cd trial_0826/ercot/waves/noise_seed_E && bash submit_this.sh

`submit_this.sh` checks the branch, pulls, refuses without
`waves/GAP_DECISION.json`, `waves/smoke_v2/SMOKE_PASS`,
`waves/design_space_E.json`, the v2 data or the `.gitignore` gz line
(`extracts/noise_seed_E/**/*.csv.gz`, pre-seeded), prints the identity and `qquota`, and asks
for a literal `yes` before `qsub`.

## Design pick (pre-registered; X only)

The 4 rows of `waves/n0_E/design_matrix.csv` whose total T = `pem_mw` is
nearest to the 10 / 37 / 63 / 90 % quantiles of T over the 48 rows; ties →
lower `index`. Quantile = `numpy.quantile(T, q)` with the default method
"linear" (Hyndman–Fan type 7). Only `index`, `pem_mw`, `mw_*`, `u_*`
and the retrofit dicts of n0_E were read; no n0_E extract, landing file or
objective value. The Seed-0 Y of each design (the n0_E run itself) is read
only in Part C, as the replicate anchor.

| quantile | target T (MW) | n0_E index | T (MW) | distance to target (MW) | runner-up index (distance) | mw_110 | mw_140 | mw_146 | mw_163 | mw_270 | mw_274 | dict md5 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| q10 (10 %) | 796.168 | 25 | 796.994 | 0.826 | 19 (1.928) | 3.400 | 63.453 | 168.126 | 93.510 | 56.529 | 411.976 | `60f866f3` |
| q37 (37 %) | 1090.445 | 29 | 1082.929 | 7.516 | 34 (11.755) | 144.556 | 55.956 | 41.181 | 34.498 | 249.787 | 556.952 | `e6ffa509` |
| q63 (63 %) | 1298.130 | 46 | 1323.884 | 25.754 | 44 (27.883) | 229.959 | 179.421 | 99.588 | 185.030 | 509.616 | 120.270 | `cf7e803d` |
| q90 (90 %) | 1490.928 | 4 | 1463.405 | 27.523 | 11 (34.102) | 134.330 | 132.514 | 233.745 | 114.713 | 575.091 | 273.011 | `caefcf4e` |

Retrofit dicts: `retrofit_gen_dict_<row>.json` here is a byte copy of
`waves/n0_E/retrofit_gen_dict_<n0_E index>.json` (md5 asserted at build and in
the tests).

## Rows (18; `__ALL__` schema, contract section 5 + 11-17 addendum)

`design_matrix.csv` columns: `index, oat_site, unit_type, bus, omega, bid, gen_pmax, start_date, num_days, replicate_of, pem_mw, level_id, tier, sobol_index, mw_110, mw_140, mw_146, mw_163, mw_270, mw_274, u_110, u_140, u_146, u_163, u_270, u_274, seed, ruc_threads`.
`tier = "contrast"`, `sobol_index` empty, `replicate_of = n0_E:<index>`,
`level_id` = the row label, `mw_*` / `u_*` / `pem_mw` equal to the n0_E row
bit-for-bit (asserted). New columns: `seed` (Gurobi `Seed`) and `ruc_threads`
(Gurobi `Threads` = SGE slots).

| row | label | replicate_of | seed | ruc_threads | pem_mw (MW) | Seed option | qsub group |
|---|---|---|---|---|---|---|---|
| 1 | q10_seed1 | n0_E:25 | 1 | 4 | 796.994 | --ruc_solver_option Seed=1 | -t 1-16 -pe smp 4 |
| 2 | q10_seed2 | n0_E:25 | 2 | 4 | 796.994 | --ruc_solver_option Seed=2 | -t 1-16 -pe smp 4 |
| 3 | q10_seed3 | n0_E:25 | 3 | 4 | 796.994 | --ruc_solver_option Seed=3 | -t 1-16 -pe smp 4 |
| 4 | q10_seed4 | n0_E:25 | 4 | 4 | 796.994 | --ruc_solver_option Seed=4 | -t 1-16 -pe smp 4 |
| 5 | q37_seed1 | n0_E:29 | 1 | 4 | 1082.929 | --ruc_solver_option Seed=1 | -t 1-16 -pe smp 4 |
| 6 | q37_seed2 | n0_E:29 | 2 | 4 | 1082.929 | --ruc_solver_option Seed=2 | -t 1-16 -pe smp 4 |
| 7 | q37_seed3 | n0_E:29 | 3 | 4 | 1082.929 | --ruc_solver_option Seed=3 | -t 1-16 -pe smp 4 |
| 8 | q37_seed4 | n0_E:29 | 4 | 4 | 1082.929 | --ruc_solver_option Seed=4 | -t 1-16 -pe smp 4 |
| 9 | q63_seed1 | n0_E:46 | 1 | 4 | 1323.884 | --ruc_solver_option Seed=1 | -t 1-16 -pe smp 4 |
| 10 | q63_seed2 | n0_E:46 | 2 | 4 | 1323.884 | --ruc_solver_option Seed=2 | -t 1-16 -pe smp 4 |
| 11 | q63_seed3 | n0_E:46 | 3 | 4 | 1323.884 | --ruc_solver_option Seed=3 | -t 1-16 -pe smp 4 |
| 12 | q63_seed4 | n0_E:46 | 4 | 4 | 1323.884 | --ruc_solver_option Seed=4 | -t 1-16 -pe smp 4 |
| 13 | q90_seed1 | n0_E:4 | 1 | 4 | 1463.405 | --ruc_solver_option Seed=1 | -t 1-16 -pe smp 4 |
| 14 | q90_seed2 | n0_E:4 | 2 | 4 | 1463.405 | --ruc_solver_option Seed=2 | -t 1-16 -pe smp 4 |
| 15 | q90_seed3 | n0_E:4 | 3 | 4 | 1463.405 | --ruc_solver_option Seed=3 | -t 1-16 -pe smp 4 |
| 16 | q90_seed4 | n0_E:4 | 4 | 4 | 1463.405 | --ruc_solver_option Seed=4 | -t 1-16 -pe smp 4 |
| 17 | q37_threads8 | n0_E:29 | 0 | 8 | 1082.929 | (none: Gurobi default Seed 0) | -t 17-17 -pe smp 8 |
| 18 | q37_threads1 | n0_E:29 | 0 | 1 | 1082.929 | (none: Gurobi default Seed 0) | -t 18-18 -pe smp 1 |

Rows 1–16: the 4 designs × Seed ∈ {1, 2, 3, 4} at Threads 4; the default
Seed 0 is the n0_E run itself, so each design has 5 solves. Rows 17–18: the
37 %-quantile design at Threads 8 and Threads 1, Seed 0 (thread check vs the
n0_E Threads-4 run).

## How Seed and Threads reach Gurobi

- The array reads `seed` / `ruc_threads` from its own row and passes
  `--ruc_threads "$RUC_THREADS"` and, for seed > 0, `--ruc_solver_option
  Seed=$SEED` to `run_ercot_pcm.py`. The wrapper accepts any KEY=VAL except
  MIPGap / TimeLimit (refused: one source each) and casts `Seed` to int; it
  prints `ruc_solver_options={'TimeLimit': ..., 'Threads': ..., 'Seed': k}`
  in the job log (the collector copies that line to
  `run_index_N/conditions.txt`: verify the Seed echo there). A Seed-0 row passes
  no Seed option (the n0_E command line exactly, except the thread count on
  rows 17–18).
- Slots: one array script, submitted three times with command-line `-t` /
  `-pe smp` (`-t 1-16 -pe smp 4`, `-t 17-17 -pe smp 8`, `-t 18-18 -pe smp 1`);
  qsub command-line options override the embedded `#$` lines. Every task
  aborts (`FAILED_task_N_slots.md`) unless `$NSLOTS` equals its row's
  `ruc_threads`. One script keeps the job-log name `noise_seed_E_array.o<jid>.<task>`
  the collector expects.
- Identity v3 unchanged: `--ruc_mipgap` / `--ruc_time_limit` from
  `waves/GAP_DECISION.json` at run time; the task refuses without it.

## Determinism conditions logged before every run (prompt 63 A4; memo F8)

`NOISE_SEED_E_HOST` (hostname), `NOISE_SEED_E_CPU` (`lscpu` Model name),
`NOISE_SEED_E_GUROBI` (`gurobipy.gurobi.version()`), `NOISE_SEED_E_THREADS`
(ruc_threads, NSLOTS, seed), `NOISE_SEED_E_CODE` (Prescient / Egret git SHAs of the
installed packages, repo HEAD). The collector writes these lines and the
wrapper's `run_ercot_pcm: index=` line to `run_index_N/conditions.txt`.

## Part C reads (prompt 63 v1 section 3; pre-registered, FROZEN with the wave commit)

Per graded candidate j (28 ids; D3 as check):
- **Chatter sd per design:** `σ̂_c,j(d)` = sd (ddof 1) over the 5 solves
  (Seed 0–4) of design d; pooled `σ̂_c,j` over the 4 designs (df 16);
  heteroscedasticity: ratio max/min across designs and vs T (trigger
  rule of 52 §3 reused).
- **Chatter covariance Σ_c** (28 × 28, from the 16 deltas vs the Seed-0
  value) with Ledoit–Wolf shrinkage; its V1/E1/R4/N1 block feeds τ_res.
- **Assumption A3 test:** `σ̂_c,j` vs the ±0.1 % perturbed amplitude
  (D2 excluded): AGREE iff within 2×; otherwise the perturbed ruler is
  labelled "perturbation response, not chatter" and B_j is redefined on
  Seed chatter (strategy session amends 61 / 62 before their landing
  reads; if they have already read, both bars are reported).
- **Thread check:** Threads 8 / 1 vs Threads 4 — bit-identical or not;
  the conditions sentence in `ERCOT_NOISE.md` is updated either way.
- **Bars:** `B_j^seed = max(3·σ̂_c,j·√2, max|Δ_seed|)` (two-run
  contrast scale); printed beside `B_j` (perturbed, D2 excluded). Which
  bar 61 / 62 use is fixed by the A3 outcome above, recorded once.
- **τ_res:** §6.2 recipe with Σ_c at the n0_E nav starts; report-only
  next to τ_exact = 0; gain/τ_res columns for 49-style reading of the
  E campaign later.
- **54 input:** `σ̂_c,j` as the measured floor candidate (54's arm "floor
  = measured iff sd > 0 and df ≥ 3" becomes live: df = 16); 54 records
  this as a §10-amended arm input, not a new arm.
- Deliverables: `analysis/noise_v3/NOISE_SEED_E.md` + csv/json
  (`ercot_noise_seed.json`: per-candidate σ̂_c, Σ_c, A3 verdict, B_j^seed,
  τ_res); figures bold labels AND ticks, assert-before-draw; plan
  amendment (actuals + the A3 verdict) as a separate last commit.

## Budget

18 full-year runs ≈ 380–803 core-h (21.1–44.6 core-h per run at 4
slots, AMENDMENT 2026-11-16 actuals; the Threads-8 / Threads-1 rows scale
differently). 73 slots. Storage 18 × 51 MB ≈ 0.9 GB of `--full`
extracts on CRC; gz tables never in git (`extracts/noise_seed_E/**/*.csv.gz`).

## Local checks (zero simulation)

`bash -n` on the scripts; `/opt/anaconda3/bin/python -m pytest
tests/test_make_noise_seed_E.py tests/test_make_ercot_n0.py -q`.

## Deviations (disclosed)

- `tier = "contrast"` (the 11-17 addendum names prompt 61's wave; this wave
  uses the same analysis-only tier; 54 / 55 never pass it to `load()`).
- `sobol_index` is empty; the n0_E anchor is `replicate_of`.
- New columns `seed` and `ruc_threads` (read by the array, not by
  `get_row.py`, which is unchanged).
- Quantile method: the prompt names no method; numpy's default is used. The
  pick is method-sensitive at 10 % and 90 % (Hazen / Weibull would pick other
  rows); it is fixed here, before any Y of this wave exists.
- One array script with per-submission slots instead of two scripts (simplest
  form SGE accepts; NSLOTS guard).
