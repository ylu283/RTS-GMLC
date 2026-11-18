# NOISE_SEED_E — Gurobi-Seed chatter rulers (prompt 63 v1 Part C; landed 2026-11-18)

Wave `waves/noise_seed_E` (18 runs, analysis-only) + the 4 n0_E anchor runs (n0_E:25, n0_E:29, n0_E:46, n0_E:4: Seed 0, Threads 4). Every value from `pool_objectives.pool_row` (E8 / E9 / N5 from `pool_full_metrics.json`). Reads pre-registered in `waves/noise_seed_E/README.md` (prompt 63 section 3). Nothing else of n0_E and nothing of random_E was read. This file decides nothing; the A3 outcome is recorded once below.

## 0. Runs, identity, SUSPECT

22 runs read (18 wave + 4 anchors). Identity: ruc_mipgap [0.001], ruc_time_limit [1200.0]. SUSPECT (S1 ∧ S2 ∧ S3a; S3a = the D3 nuclear-starts check): none. Time-limit hits: 0. Max daily RUC solve over the 22 runs: 821.3 s; days > 600 s: 3 on the 18 wave runs.

| key | label | anchor | seed | threads | T (MW) | overall md5 | host | Gurobi | Seed echo (ruc_solver_options) | max RUC solve s | days > 600 s | wall h | core-h | SUSPECT |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| noise_seed_E:1 | q10_seed1 | n0_E:25 | 1 | 4 | 796.994 | `3aa80d06` | d32cepyc127.crc.nd.edu | (13, 0, 2) | {'TimeLimit': 1200.0, 'Threads': 4, 'Seed': 1} | 291.4 | 0 | 4.96 | 19.8 | no |
| noise_seed_E:2 | q10_seed2 | n0_E:25 | 2 | 4 | 796.994 | `412b7317` | d12chas350.crc.nd.edu | (13, 0, 2) | {'TimeLimit': 1200.0, 'Threads': 4, 'Seed': 2} | 503.7 | 0 | 9.77 | 39.1 | no |
| noise_seed_E:3 | q10_seed3 | n0_E:25 | 3 | 4 | 796.994 | `eef9c5db` | d12chas350.crc.nd.edu | (13, 0, 2) | {'TimeLimit': 1200.0, 'Threads': 4, 'Seed': 3} | 821.3 | 2 | 10.6 | 42.4 | no |
| noise_seed_E:4 | q10_seed4 | n0_E:25 | 4 | 4 | 796.994 | `19259f44` | d12chas350.crc.nd.edu | (13, 0, 2) | {'TimeLimit': 1200.0, 'Threads': 4, 'Seed': 4} | 535.8 | 0 | 9.86 | 39.4 | no |
| noise_seed_E:5 | q37_seed1 | n0_E:29 | 1 | 4 | 1082.93 | `b7daa2a3` | d12chas350.crc.nd.edu | (13, 0, 2) | {'TimeLimit': 1200.0, 'Threads': 4, 'Seed': 1} | 443 | 0 | 9.56 | 38.2 | no |
| noise_seed_E:6 | q37_seed2 | n0_E:29 | 2 | 4 | 1082.93 | `f877a430` | d12chas350.crc.nd.edu | (13, 0, 2) | {'TimeLimit': 1200.0, 'Threads': 4, 'Seed': 2} | 509.2 | 0 | 10.1 | 40.5 | no |
| noise_seed_E:7 | q37_seed3 | n0_E:29 | 3 | 4 | 1082.93 | `de600a07` | d12chas350.crc.nd.edu | (13, 0, 2) | {'TimeLimit': 1200.0, 'Threads': 4, 'Seed': 3} | 592.9 | 0 | 9.4 | 37.6 | no |
| noise_seed_E:8 | q37_seed4 | n0_E:29 | 4 | 4 | 1082.93 | `caee3f42` | d12chas346.crc.nd.edu | (13, 0, 2) | {'TimeLimit': 1200.0, 'Threads': 4, 'Seed': 4} | 455.5 | 0 | 9.36 | 37.4 | no |
| noise_seed_E:9 | q63_seed1 | n0_E:46 | 1 | 4 | 1323.88 | `88b90957` | d12chas346.crc.nd.edu | (13, 0, 2) | {'TimeLimit': 1200.0, 'Threads': 4, 'Seed': 1} | 439.4 | 0 | 10 | 40 | no |
| noise_seed_E:10 | q63_seed2 | n0_E:46 | 2 | 4 | 1323.88 | `5e9554e8` | d12chas346.crc.nd.edu | (13, 0, 2) | {'TimeLimit': 1200.0, 'Threads': 4, 'Seed': 2} | 436.9 | 0 | 9.6 | 38.4 | no |
| noise_seed_E:11 | q63_seed3 | n0_E:46 | 3 | 4 | 1323.88 | `12fe8869` | d12chas346.crc.nd.edu | (13, 0, 2) | {'TimeLimit': 1200.0, 'Threads': 4, 'Seed': 3} | 415.6 | 0 | 9.55 | 38.2 | no |
| noise_seed_E:12 | q63_seed4 | n0_E:46 | 4 | 4 | 1323.88 | `1b0d4321` | d12chas346.crc.nd.edu | (13, 0, 2) | {'TimeLimit': 1200.0, 'Threads': 4, 'Seed': 4} | 485.2 | 0 | 10 | 40.1 | no |
| noise_seed_E:13 | q90_seed1 | n0_E:4 | 1 | 4 | 1463.4 | `6c5d9711` | d12chas346.crc.nd.edu | (13, 0, 2) | {'TimeLimit': 1200.0, 'Threads': 4, 'Seed': 1} | 576.5 | 0 | 9.48 | 37.9 | no |
| noise_seed_E:14 | q90_seed2 | n0_E:4 | 2 | 4 | 1463.4 | `2bd89502` | d32cepyc128.crc.nd.edu | (13, 0, 2) | {'TimeLimit': 1200.0, 'Threads': 4, 'Seed': 2} | 209.7 | 0 | 4.76 | 19.1 | no |
| noise_seed_E:15 | q90_seed3 | n0_E:4 | 3 | 4 | 1463.4 | `844dce54` | d32cepyc128.crc.nd.edu | (13, 0, 2) | {'TimeLimit': 1200.0, 'Threads': 4, 'Seed': 3} | 290.9 | 0 | 4.81 | 19.2 | no |
| noise_seed_E:16 | q90_seed4 | n0_E:4 | 4 | 4 | 1463.4 | `a59f6208` | d32cepyc128.crc.nd.edu | (13, 0, 2) | {'TimeLimit': 1200.0, 'Threads': 4, 'Seed': 4} | 310 | 0 | 4.79 | 19.1 | no |
| noise_seed_E:17 | q37_threads8 | n0_E:29 | 0 | 8 | 1082.93 | `e8d6189f` | d32cepyc128.crc.nd.edu | (13, 0, 2) | {'TimeLimit': 1200.0, 'Threads': 8} | 239.5 | 0 | 4.57 | 36.6 | no |
| noise_seed_E:18 | q37_threads1 | n0_E:29 | 0 | 1 | 1082.93 | `6d988d94` | d32cepyc128.crc.nd.edu | (13, 0, 2) | {'TimeLimit': 1200.0, 'Threads': 1} | 634.8 | 1 | 6.32 | 6.32 | no |
| n0_E:25 | anchor (n0_E Seed 0, Threads 4) | n0_E:25 | 0 | 4 | 796.994 | `08e890f1` | — | — | — | 242.9 | 0 | n/a | n/a | no |
| n0_E:29 | anchor (n0_E Seed 0, Threads 4) | n0_E:29 | 0 | 4 | 1082.93 | `f71ea2e1` | — | — | — | 271.4 | 0 | n/a | n/a | no |
| n0_E:46 | anchor (n0_E Seed 0, Threads 4) | n0_E:46 | 0 | 4 | 1323.88 | `56541ea6` | — | — | — | 545.4 | 0 | n/a | n/a | no |
| n0_E:4 | anchor (n0_E Seed 0, Threads 4) | n0_E:4 | 0 | 4 | 1463.4 | `692ab5e3` | — | — | — | 438.8 | 0 | n/a | n/a | no |

Core-h (wall × slots): total 589.5, median per Threads-4 run 38.2 (min 19.1, max 42.4); Threads 8 run 36.6, Threads 1 run 6.32.

## 1. Chatter sd per design and pooled (Seed 0–4; df 4 per design, pooled df 16)

Per design: sd (ddof 1) over the 5 solves. Pooled σ̂_c = sqrt(mean of the 4 variances), df 16, chi-square 95 % CI. Heteroscedasticity: the 52 section 3 trigger (F test of max / min variance, df 4 / 4, alpha 0.05 AND ratio > 3; with df 4 / 4 it rejects only above ratio 6.39) and the rank correlation of the 4 design sds with T (descriptive; n = 4). A non-firing trigger reads "not detectable at this df".

| id | unit | sd q10 (T 797) | sd q37 (T 1083) | sd q63 (T 1324) | sd q90 (T 1463) | pooled σ̂_c (df 16) | 95 % CI | max/min sd | trigger | rank corr(sd, T) |
|---|---|---|---|---|---|---|---|---|---|---|
| V1 | MWh | 5259 | 4399 | 3174 | 4418 | 4376 | [3259, 6660] | 1.66 | no (ratio 2.75, p 0.176) | -0.4 |
| V2 | % | 0.001985 | 0.002071 | 0.001035 | 0.001957 | 0.001812 | [0.001349, 0.002757] | 2 | no (ratio 4.01, p 0.104) | -0.6 |
| V3 | fraction | 3.790e-05 | 5.557e-05 | 3.290e-05 | 5.121e-05 | 4.536e-05 | [3.378e-05, 6.903e-05] | 1.69 | no (ratio 2.85, p 0.167) | 0 |
| E1 | $ | 2.348e+05 | 2.081e+05 | 3.676e+05 | 3.961e+05 | 3.124e+05 | [2.327e+05, 4.755e+05] | 1.9 | no (ratio 3.62, p 0.12) | 0.8 |
| E2 | $ | 4.259e+05 | 6.075e+05 | 1.277e+06 | 8.753e+05 | 8.583e+05 | [6.392e+05, 1.306e+06] | 3 | FIRES (ratio 8.98) | 0.8 |
| E3 | $ | 4.363e+05 | 5.378e+05 | 9.535e+05 | 1.200e+06 | 8.411e+05 | [6.264e+05, 1.280e+06] | 2.75 | FIRES (ratio 7.57) | 1 |
| E4 | $ | 3.057e+06 | 2.963e+06 | 1.259e+06 | 1.724e+06 | 2.382e+06 | [1.774e+06, 3.625e+06] | 2.43 | no (ratio 5.89, p 0.057) | -0.8 |
| E5 | $ | 0 | 0 | 0 | 0 | 0 | [n/a, n/a] | n/a | all levels 0 | n/a |
| E6 | $ | 6.112e+05 | 4.687e+05 | 1.525e+05 | 2.408e+05 | 4.106e+05 | [3.058e+05, 6.250e+05] | 4.01 | FIRES (ratio 16.1) | -0.8 |
| E7 | $/MWh | 0.00459 | 0.002483 | 0.002977 | 0.002978 | 0.003353 | [0.002497, 0.005103] | 1.85 | no (ratio 3.42, p 0.131) | -0.2 |
| E8 | $/MWh | 0.057 | 0.09143 | 0.05981 | 0.06069 | 0.06868 | [0.05115, 0.1045] | 1.6 | no (ratio 2.57, p 0.191) | 0.4 |
| E9 | count | 0.4472 | 0 | 0 | 0.4472 | 0.3162 | [0.2355, 0.4813] | inf | FIRES (sd-0 level) | 0.32 |
| R1 | MWh | 0 | 0 | 0 | 0 | 0 | [n/a, n/a] | n/a | all levels 0 | n/a |
| R2 | MWh | 24.73 | 14.55 | 24.06 | 30.71 | 24.22 | [18.03, 36.85] | 2.11 | no (ratio 4.45, p 0.0885) | 0.4 |
| R3 | MWh | 0 | 0 | 0 | 0 | 0 | [n/a, n/a] | n/a | all levels 0 | n/a |
| R4 | count | 56 | 66.36 | 69.35 | 67.8 | 65.09 | [48.47, 99.06] | 1.24 | no (ratio 1.53, p 0.344) | 0.8 |
| R5 | MW | 2429 | 1363 | 2101 | 4583 | 2880 | [2145, 4383] | 3.36 | FIRES (ratio 11.3) | 0.4 |
| R6 | MW | 1.031e+04 | 2.626e+04 | 2.604e+04 | 2.102e+04 | 2.189e+04 | [1.63e+04, 3.331e+04] | 2.55 | FIRES (ratio 6.48) | 0.2 |
| R7 | MWh | 5.402e+04 | 4.994e+04 | 7.032e+04 | 8.704e+04 | 6.696e+04 | [4.987e+04, 1.019e+05] | 1.74 | no (ratio 3.04, p 0.154) | 0.8 |
| R8 | unit-h | 237.5 | 475.1 | 223.1 | 301.1 | 325 | [242.1, 494.6] | 2.13 | no (ratio 4.54, p 0.0861) | 0 |
| N1 | line-h | 33.04 | 25.01 | 77.46 | 72.84 | 57.06 | [42.5, 86.84] | 3.1 | FIRES (ratio 9.59) | 0.6 |
| N2 | count | 0.8367 | 0.4472 | 1 | 1.095 | 0.8803 | [0.6557, 1.34] | 2.45 | no (ratio 6, p 0.0554) | 0.8 |
| N3 | MWh | 1.533 | 2.347 | 2.501 | 3.204 | 2.469 | [1.839, 3.757] | 2.09 | no (ratio 4.37, p 0.0911) | 1 |
| N4 | line-h | 9.524 | 10.13 | 15.67 | 1.095 | 10.49 | [7.814, 15.97] | 14.3 | FIRES (ratio 205) | -0.2 |
| N5 | $/MWh | 0.03617 | 0.02918 | 0.04518 | 0.06229 | 0.04495 | [0.03347, 0.0684] | 2.13 | no (ratio 4.56, p 0.0855) | 0.8 |
| X1 | t | 3729 | 9892 | 1.339e+04 | 7541 | 9326 | [6946, 1.419e+04] | 3.59 | FIRES (ratio 12.9) | 0.4 |
| D1 | MWh | 3194 | 4607 | 2703 | 4164 | 3744 | [2789, 5698] | 1.7 | no (ratio 2.9, p 0.163) | 0 |
| D2 | fraction | 4.575e-04 | 4.856e-04 | 2.331e-04 | 3.248e-04 | 3.889e-04 | [2.896e-04, 5.919e-04] | 2.08 | no (ratio 4.34, p 0.092) | -0.6 |

Trigger fires (gradable): 9 of 22 (X1, N1, N4, E6, R5, E2, R6, E3, E9). Figure: `fig_seed_chatter_sd.png` (V1, E1, R4, N1, N4: sd per design vs T, pooled line).

## 2. A3 test and the bars (FINAL, recorded once)

A3 compares like with like on the two-run scale: ratio = σ̂_c·√2 / σ̂_pert, with σ̂_pert = sqrt(mean δ²) over the 6 non-structural ±0.1 % perturbed deltas (`ercot_noise.json` `per_candidate.<j>.bar`, D2 excluded). AGREE iff 1/2 ≤ ratio ≤ 2. B_j^seed = max(3·σ̂_c·√2, max |Δ_seed|) over the 16 deltas vs Seed 0; B_j = the perturbed bar (prompt 61 section 3, D2 excluded).

| id | unit | σ̂_c (per run) | σ̂_c·√2 | σ̂_pert | ratio | A3 | max |Δ_seed| | B_j^seed | B_j (perturbed) | B_j^seed / B_j |
|---|---|---|---|---|---|---|---|---|---|---|
| V1 | MWh | 4376 | 6189 | 5391 | 1.15 | AGREE | 9661 | 1.857e+04 | 1.617e+04 | 1.15 |
| V2 | % | 0.001812 | 0.002562 | 0.00137 | 1.87 | AGREE | 0.005119 | 0.007687 | 0.004109 | 1.87 |
| V3 | fraction | 4.536e-05 | 6.415e-05 | 1.034e-05 | 6.2 | DISAGREE | 1.315e-04 | 1.924e-04 | 3.103e-05 | 6.2 |
| E1 | $ | 3.124e+05 | 4.418e+05 | 7.944e+05 | 0.556 | AGREE | 1.052e+06 | 1.325e+06 | 2.383e+06 | 0.556 |
| E2 | $ | 8.583e+05 | 1.214e+06 | 9.674e+05 | 1.25 | AGREE | 2.931e+06 | 3.641e+06 | 2.902e+06 | 1.25 |
| E3 | $ | 8.411e+05 | 1.190e+06 | 1.157e+06 | 1.03 | AGREE | 3.137e+06 | 3.569e+06 | 3.470e+06 | 1.03 |
| E4 | $ | 2.382e+06 | 3.368e+06 | 2.835e+06 | 1.19 | AGREE | 7.881e+06 | 1.010e+07 | 8.505e+06 | 1.19 |
| E5 | $ | 0 | 0 | 0 | n/a | AGREE (both exactly 0) | 0 | 0 | 0 | n/a |
| E6 | $ | 4.106e+05 | 5.807e+05 | 9.694e+05 | 0.599 | AGREE | 1.271e+06 | 1.742e+06 | 2.908e+06 | 0.599 |
| E7 | $/MWh | 0.003353 | 0.004741 | 0.005537 | 0.856 | AGREE | 0.01188 | 0.01422 | 0.01661 | 0.856 |
| E8 | $/MWh | 0.06868 | 0.09713 | 0.1008 | 0.964 | AGREE | 0.1998 | 0.2914 | 0.3024 | 0.964 |
| E9 | count | 0.3162 | 0.4472 | 0 | inf | DISAGREE (one ruler is 0) | 1 | 1.342 | 0 | n/a |
| R1 | MWh | 0 | 0 | 0 | n/a | AGREE (both exactly 0) | 0 | 0 | 0 | n/a |
| R2 | MWh | 24.22 | 34.25 | 34.1 | 1 | AGREE | 59.9 | 102.7 | 102.3 | 1 |
| R3 | MWh | 0 | 0 | 0 | n/a | AGREE (both exactly 0) | 0 | 0 | 0 | n/a |
| R4 | count | 65.09 | 92.05 | 48.88 | 1.88 | AGREE | 161 | 276.1 | 146.7 | 1.88 |
| R5 | MW | 2880 | 4072 | 5540 | 0.735 | AGREE | 1.237e+04 | 1.237e+04 | 1.662e+04 | 0.744 |
| R6 | MW | 2.189e+04 | 3.095e+04 | 3.444e+04 | 0.899 | AGREE | 6.197e+04 | 9.286e+04 | 1.033e+05 | 0.899 |
| R7 | MWh | 6.696e+04 | 9.469e+04 | 8.959e+04 | 1.06 | AGREE | 2.333e+05 | 2.841e+05 | 2.688e+05 | 1.06 |
| R8 | unit-h | 325 | 459.6 | 514.4 | 0.893 | AGREE | 800 | 1379 | 1543 | 0.893 |
| N1 | line-h | 57.06 | 80.69 | 38.31 | 2.11 | DISAGREE | 177 | 242.1 | 114.9 | 2.11 |
| N2 | count | 0.8803 | 1.245 | 1 | 1.24 | AGREE | 2 | 3.735 | 3 | 1.24 |
| N3 | MWh | 2.469 | 3.491 | 4.658 | 0.75 | AGREE | 6.743 | 10.47 | 13.97 | 0.75 |
| N4 | line-h | 10.49 | 14.84 | 12.32 | 1.2 | AGREE | 37 | 44.51 | 36.97 | 1.2 |
| N5 | $/MWh | 0.04495 | 0.06356 | 0.06087 | 1.04 | AGREE | 0.1477 | 0.1907 | 0.1826 | 1.04 |
| X1 | t | 9326 | 1.319e+04 | 1.215e+04 | 1.09 | AGREE | 3.071e+04 | 3.957e+04 | 3.645e+04 | 1.09 |
| D1 | MWh | 3744 | 5295 | 1453 | 3.64 | DISAGREE | 1.069e+04 | 1.589e+04 | 4358 | 3.64 |
| D2 | fraction | 3.889e-04 | 5.500e-04 | 4.083e-04 | 1.35 | AGREE | 0.001143 | 0.00165 | 0.001225 | 1.35 |

**A3 verdict (gradable, 22 ids): AGREE on 20 (V1, E1, X1, R4, E4, R2, R7, N4, N5, E6, R5, N3, E2, R6, N2, E3, R8, E7, E8, V2); DISAGREE on 2 (N1, E9).** Headline objectives: V1 AGREE; E1 AGREE; R4 AGREE; N1 DISAGREE; N4 AGREE.
For every DISAGREE id the perturbed ruler is labelled "perturbation response, not chatter" and B_j is redefined on Seed chatter (B_j^seed); for every AGREE id both bars measure the same chatter and both are reported (prompt 63 section 3; the strategy session amends 61 / 62; 61 has already read, so both bars are reported there). Figure: `fig_seed_a3_ratio.png`.

## 3. Chatter covariance Σ_c

`ercot_noise_seed_sigma_c.csv` (28 × 28; ids finite on all 16 deltas). Estimator `tau_E.sigma_c_from_deltas`: per-run Σ_c = (second moment of the 16 deltas about 0) / 2, Ledoit–Wolf shrinkage of the RMS-scaled matrix toward I (= toward the diagonal); shrinkage 0.448; 3 zero columns. 16 deltas vs the Seed-0 solve of the same design; the 4 deltas of one design share their Seed-0 value (not independent) — the estimator treats them as 16 pairs (disclosed).

Headline block (covariance; diagonal sqrt = per-run sd from the deltas; off-diagonal as correlation in brackets):

| | V1 | E1 | R4 | N1 | N4 |
|---|---|---|---|---|---|
| V1 | 1.073e+07 (sd 3275) | 2.676e+08 (0.21) | -2.246e+04 (-0.11) | 1.985e+04 (0.12) | 2006 (0.056) |
| E1 | 2.676e+08 (0.21) | 1.585e+11 (sd 3.981e+05) | 8.287e+06 (0.33) | 5.471e+06 (0.28) | 4.143e+05 (0.095) |
| R4 | -2.246e+04 (-0.11) | 8.287e+06 (0.33) | 3975 (sd 63.05) | 652.4 (0.21) | -10.24 (-0.015) |
| N1 | 1.985e+04 (0.12) | 5.471e+06 (0.28) | 652.4 (0.21) | 2454 (sd 49.54) | -79.3 (-0.15) |
| N4 | 2006 (0.056) | 4.143e+05 (0.095) | -10.24 (-0.015) | -79.3 (-0.15) | 119.8 (sd 10.95) |

## 4. Thread check (Threads 8 / 1 vs the Threads-4 anchor n0_E:29; Seed 0)

| key | threads | overall md5 vs anchor | bit-identical | candidates differing | divergent RUC days | first divergent day | median rel day change | host | Gurobi | echo |
|---|---|---|---|---|---|---|---|---|---|---|
| noise_seed_E:17 | 8 | `e8d6189f` vs `f71ea2e1` | **no** | 23 | 304 | 1 | 1.057e-04 | d32cepyc128.crc.nd.edu | (13, 0, 2) | {'TimeLimit': 1200.0, 'Threads': 8} |
| noise_seed_E:18 | 1 | `6d988d94` vs `f71ea2e1` | **no** | 24 | 364 | 1 | 1.722e-04 | d32cepyc128.crc.nd.edu | (13, 0, 2) | {'TimeLimit': 1200.0, 'Threads': 1} |

**The Threads-8 / Threads-1 runs are NOT bit-identical to the Threads-4 anchor** (every RUC day from day 1 can differ). Caveat: the anchor ran in the n0_E wave on a node that was not recorded, while both thread rows ran on d32cepyc128.crc.nd.edu; the thread count and the node class are therefore confounded in this check. Either way, bit-identity is established only at fixed Threads on a fixed platform class (the noise_v3 conditions, `ERCOT_NOISE.md` §12); a thread or node change acts like a Seed change (Δ in σ̂_c units below).

| key | V1 | E1 | R4 | N1 | N4 |
|---|---|---|---|---|---|
| noise_seed_E:17 | 6043 (1.4 σ̂_c) | 2.173e+05 (0.7 σ̂_c) | 31 (0.48 σ̂_c) | -135 (2.4 σ̂_c) | 19 (1.8 σ̂_c) |
| noise_seed_E:18 | -2525 (0.58 σ̂_c) | 4.568e+05 (1.5 σ̂_c) | 125 (1.9 σ̂_c) | -265 (4.6 σ̂_c) | 16 (1.5 σ̂_c) |

Cells: Δ vs the anchor (and |Δ| in units of the per-run σ̂_c).

Seed rows vs their Seed-0 anchor, day level: 363–365 of 365 RUC days divergent; first divergent day 1–1; median relative day change 1.306e-04–1.747e-04; overall md5 equal to the anchor on 0 of 16.

## 5. τ_res (REPORT-ONLY; PROVISIONAL)

E-D7 (nav = the first 32 or all 48 Sobol rows) is not recorded, so the nav-start set is not defined without reading n0_E rows beyond the 4 anchors. τ_res is therefore computed on the 4 anchor designs' Y only and labelled PROVISIONAL. Recipe: `tau_E.tau_res` (the tau_joint code path; N = 1000, default_rng(20261006)), Σ_c = the V1/E1/R4/N1 block of section 3, ref = the frozen plan 6.3 R (waves/n0_E/landing_R.json key R (plan 6.3, AMENDMENT 2026-11-16)).

| quantity | value |
|---|---|
| τ_exact (frozen rule) | 0 |
| HV_0 of the 4 anchors | 1.536e+19 |
| **τ_res (Seed Σ_c), PROVISIONAL** | **1.958e+18** |
| τ_res / HV_0 | 0.1275 |
| τ_res with the 63 A5 perturbed PROVISIONAL Σ_c (same 4 starts) | 9.651e+17 |
| anchors strictly below R | 4 of 4 |

τ_exact = 0 stays the rule (plan 3 / 6.2; frozen). τ_res is printed beside it and decides nothing. The value at the real nav starts is 55 Part B's column (Σ_c from this file).

## 6. Input to prompt 54 (measured-floor candidate; §10-amended arm input, not a new arm)

54's arm rule "floor = measured iff sd > 0 and df ≥ 3" becomes live: σ̂_c,j below, df 16. The 54 cross-check (63 A6 pointer) compares the inferred GP noise sd against σ̂_c,j, not against the exact sd 0.

| id | σ̂_c,j (per run) | df | 95 % CI | measured arm live (sd > 0, df ≥ 3) |
|---|---|---|---|---|
| V1 | 4376 | 16 | [3259, 6660] | yes |
| E1 | 3.124e+05 | 16 | [2.327e+05, 4.755e+05] | yes |
| R4 | 65.09 | 16 | [48.47, 99.06] | yes |
| N1 | 57.06 | 16 | [42.5, 86.84] | yes |
| N4 | 10.49 | 16 | [7.814, 15.97] | yes |

## 7. Deviations and limits

- The 4 deltas of one design share their Seed-0 value; Σ_c and max |Δ_seed| treat the 16 as pairs. σ̂_c (section 1) is the within-design sd and does not have this dependence.
- n = 4 designs, all inside the BO box (T 797–1,463 MW); the trigger has df 4 / 4 and is an order-of-magnitude detector.
- τ_res is PROVISIONAL on 4 anchor starts (E-D7 not recorded); `landing_R.json` was loaded for its `R` key only.
- The anchors ran in the n0_E wave (other nodes / dates); host and Gurobi version of the anchor runs are not recorded (n0_E predates the conditions lines). The Seed rows' conditions are in section 0.
- Outputs: `NOISE_SEED_E.md`, `ercot_noise_seed.json`, `ercot_noise_seed.csv` (per candidate), `ercot_noise_seed_runs.csv`, `ercot_noise_seed_sigma_c.csv`, `fig_seed_chatter_sd.png`, `fig_seed_a3_ratio.png`.

