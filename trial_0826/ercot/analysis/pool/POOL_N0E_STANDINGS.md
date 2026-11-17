# POOL_N0E_STANDINGS — objective pool on the n0_E population (prompt 62 Part B)

Read date (UTC): 2026-11-17T09:27:34+00:00. Rules: plan AMENDMENT 2026-11-17 (commit (i) 6aa29dd, block sha256 `8dd06917415c8cf6e8f7081adcee862e3d2ae6d08cf4eaa8dc0a9fa2cc8a1d1e`); script + tests commit (ii) 6b5e85a (+ follow-ups e09193b, f7ef2d3, 143b6a3, 82bb71d). Definitions frozen at f76d897. `waves/n0_E/design_matrix.csv` sha256 `87ee148e8d9237c23957f6b9999d70c1bef5dba47a622cdf9e2017394b19a049`. git HEAD at the read 82bb71d.

Input: 48 n0_E grading rows at pool level (`pool_standings.build_wave("n0_E")`); no GP fitted; random_E not read; holdout exposure 0 of 24.

## 1. Disclosures

- B_j is transferred from single-site off-slate designs (noise_v3, n = 6 deltas after the D2 exclusion); box chatter cannot be measured on n0_E (no replicates).
- rho(T, s) = +0.39 in this design (s = bus-120 share): size and composition are not orthogonal.
- COMPOSITION and 54's L flag come from the same 48 rows: never two independent pieces of evidence; 61 tests location directly.
- SIZE SHARE, COMPOSITION and the isotonic LOO R^2 are descriptive only.
- Not blind: per-candidate ideal / nadir / R over these 48 rows were seen before the rules (plan AMENDMENT 2026-11-16 / 2026-11-17).

Sampling facts:

- At n = 48, P(rho_hat >= 0.90 | rho = 0.80) = 0.8 %; P(rho_hat >= 0.90 | rho = 0.90) = 44 %.
- Sobol points are not i.i.d.; the null bands are mildly conservative.
- Solver chatter attenuates rho (permissive for R4 / N1).
- Multiplicity over 231 pairs: expected false redundancy < 0.01, false trade-off about 0.07; no correction.
- False RESPONDS under pure chatter: about 0.1 % per id for IDR at 1x chatter (3.5 % for the raw range).

R-3 BORDERLINE band (raw rho whose 90 % Fisher-z interval contains 0.90, n = 48): [0.842, 0.938] (prompt text: about 0.86-0.93).

## 2. Bar B_j (61 §3, D2 structural zeros excluded) beside 57's median ruler (never merged)

Excluded pair(s): noise_v3/A:6 vs noise_v3/A:2 (effective-input md5 8141c960, overall md5 6dde2591); noise_v3/B:6 vs noise_v3/B:2 (effective-input md5 8141c960, overall md5 6dde2591)

| id | n_delta | sigma_hat | B_j | ruler_57 | B_over_ruler | in_ruler_zero |
|---|---|---|---|---|---|---|
| V1 | 6 | 5391.019 | 1.617e+04 | 2420.009 | 6.683 | False |
| V2 | 6 | 0.00137 | 0.004109 | 0.000547 | 7.512 | False |
| V3 | 6 | 1.034e-05 | 3.103e-05 | 5.141e-06 | 6.036 | False |
| E1 | 6 | 7.944e+05 | 2.383e+06 | 2.319e+05 | 10.277 | False |
| E2 | 6 | 9.674e+05 | 2.902e+06 | 8.371e+05 | 3.467 | False |
| E3 | 6 | 1.157e+06 | 3.47e+06 | 9.78e+05 | 3.548 | False |
| E4 | 6 | 2.835e+06 | 8.505e+06 | 2.031e+06 | 4.188 | False |
| E5 | 6 | 0.000 | 0.000 | 0.000 | n/a | False |
| E6 | 6 | 9.694e+05 | 2.908e+06 | 6.724e+05 | 4.325 | False |
| E7 | 6 | 0.005537 | 0.017 | 0.003582 | 4.637 | False |
| E8 | 6 | 0.101 | 0.302 | 0.077 | 3.941 | False |
| E9 | 6 | 0.000 | 0.000 | 0.000 | n/a | True |
| R1 | 6 | 0.000 | 0.000 | 0.000 | n/a | False |
| R2 | 6 | 34.098 | 102.295 | 26.255 | 3.896 | False |
| R3 | 6 | 0.000 | 0.000 | 0.000 | n/a | False |
| R4 | 6 | 48.884 | 146.653 | 28.500 | 5.146 | False |
| R5 | 6 | 5540.210 | 1.662e+04 | 4630.305 | 3.590 | False |
| R6 | 6 | 3.444e+04 | 1.033e+05 | 1.762e+04 | 5.862 | False |
| R7 | 6 | 8.959e+04 | 2.688e+05 | 8.54e+04 | 3.147 | False |
| R8 | 6 | 514.435 | 1543.306 | 472.000 | 3.270 | False |
| N1 | 6 | 38.308 | 114.924 | 23.500 | 4.890 | False |
| N2 | 6 | 1.000 | 3.000 | 0.500 | 6.000 | False |
| N3 | 6 | 4.658 | 13.974 | 4.634 | 3.015 | False |
| N4 | 6 | 12.322 | 36.966 | 13.000 | 2.844 | False |
| N5 | 6 | 0.061 | 0.183 | 0.052 | 3.518 | False |
| X1 | 6 | 1.215e+04 | 3.645e+04 | 5555.275 | 6.562 | False |
| D1 | 4 | 1452.801 | 4358.402 | 1190.566 | 3.661 | False |
| D2 | 4 | 0.0004083 | 0.001225 | 0.0002982 | 4.107 | False |

B_j / ruler range over ids with both > 0: 2.84-10.28x.

## 3. Per candidate (RESPONDS IN BOX, SIZE SHARE, COMPOSITION)

RESPONDS IN BOX iff IDR >= 2 B_j AND Mantel one-sided p <= 0.01 (9,999 permutations, default_rng(6262) per id) AND signal share >= 0.5; BORDERLINE iff IDR/B_j in [2, 3); STRONG iff IDR >= 10 B_j. eta2_T null mean 0.107, null 95th percentile 0.23.

| id | B_j | IDR | IDR_over_B | range_over_B | mantel_p | signal_share | respond_label | eta2_T | eta2_T_adj | iso_loo_R2 | comp_rho | comp_ci_lo | comp_ci_hi |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| V1 | 1.617e+04 | 1.509e+06 | 93.275 | 144.367 | 0.0001 | 1.000 | RESPONDS IN BOX (STRONG) | 0.978 | 0.975 | 0.987 | -0.469 | -0.664 | -0.213 |
| E1 | 2.383e+06 | 3.35e+07 | 14.055 | 21.397 | 0.0003 | 0.998 | RESPONDS IN BOX (STRONG) | 0.641 | 0.598 | 0.670 | -0.608 | -0.761 | -0.391 |
| X1 | 3.645e+04 | 9.988e+05 | 27.399 | 44.200 | 0.0004 | 1.000 | RESPONDS IN BOX (STRONG) | 0.741 | 0.710 | 0.788 | -0.508 | -0.692 | -0.261 |
| R4 | 146.653 | 310.100 | 2.115 | 3.689 | 0.0009 | 0.916 | RESPONDS IN BOX (BORDERLINE) | 0.514 | 0.456 | 0.379 | 0.073 | -0.215 | 0.350 |
| N1 | 114.924 | 738.800 | 6.429 | 11.094 | 0.0001 | 0.992 | RESPONDS IN BOX | 0.891 | 0.877 | 0.910 | -0.027 | -0.308 | 0.259 |
| E4 | 8.505e+06 | 8.896e+07 | 10.460 | 18.292 | 0.0001 | 0.997 | RESPONDS IN BOX (STRONG) | 0.873 | 0.857 | 0.893 | -0.375 | -0.595 | -0.101 |
| R2 | 102.295 | 76.423 | 0.747 | 1.246 | 0.173 | 0.381 | NOT RESPONDS | 0.067 | -0.045 | -0.090 | 0.093 | -0.196 | 0.368 |
| R7 | 2.688e+05 | 1.183e+06 | 4.401 | 7.351 | 0.0001 | 0.980 | RESPONDS IN BOX | 0.689 | 0.651 | 0.773 | -0.446 | -0.648 | -0.185 |
| N4 | 36.966 | 642.500 | 17.381 | 31.353 | 0.0001 | 0.999 | RESPONDS IN BOX (STRONG) | 0.925 | 0.916 | 0.899 | 0.268 | -0.018 | 0.513 |
| N5 | 0.183 | 3.126 | 17.117 | 32.065 | 0.0001 | 0.999 | RESPONDS IN BOX (STRONG) | 0.926 | 0.917 | 0.917 | -0.393 | -0.609 | -0.123 |
| E6 | 2.908e+06 | 4.238e+07 | 14.572 | 27.220 | 0.0001 | 0.998 | RESPONDS IN BOX (STRONG) | 0.697 | 0.660 | 0.931 | 0.740 | 0.578 | 0.846 |
| R5 | 1.662e+04 | 1.48e+04 | 0.891 | 1.579 | 0.109 | 0.564 | NOT RESPONDS | -0.715 | -0.920 | 0.311 | 0.321 | 0.040 | 0.554 |
| N3 | 13.974 | 9.208 | 0.659 | 0.951 | 0.112 | 0.033 | NOT RESPONDS | -1.720 | -2.046 | -0.201 | 0.046 | -0.241 | 0.326 |
| E2 | 2.902e+06 | 9.557e+06 | 3.293 | 5.284 | 0.0006 | 0.967 | RESPONDS IN BOX | 0.557 | 0.504 | 0.572 | -0.568 | -0.734 | -0.339 |
| R6 | 1.033e+05 | 8.389e+04 | 0.812 | 1.665 | 0.676 | 0.546 | NOT RESPONDS | -2.974 | -3.450 | 0.015 | 0.142 | -0.148 | 0.410 |
| N2 | 3.000 | 1.300 | 0.433 | 1.333 | 0.556 | 0.376 | NOT RESPONDS | -0.040 | -0.165 | -0.029 | -0.112 | -0.384 | 0.178 |
| E3 | 3.47e+06 | 2.427e+07 | 6.995 | 11.053 | 0.0004 | 0.993 | RESPONDS IN BOX | 0.674 | 0.635 | 0.677 | -0.592 | -0.750 | -0.370 |
| R8 | 1543.306 | 1793.100 | 1.162 | 2.021 | 0.0032 | 0.755 | NOT RESPONDS | 0.523 | 0.466 | 0.473 | -0.153 | -0.419 | 0.137 |
| E7 | 0.017 | 0.234 | 14.090 | 25.669 | 0.0001 | 0.998 | RESPONDS IN BOX (STRONG) | 0.891 | 0.878 | 0.901 | -0.438 | -0.642 | -0.176 |
| E8 | 0.302 | 0.307 | 1.016 | 1.995 | 0.027 | 0.696 | NOT RESPONDS | 0.355 | 0.277 | 0.120 | -0.140 | -0.408 | 0.150 |
| E9 | 0.000 | 0.000 | n/a | n/a | 0.833 | 1.000 | READABLE (RULER=0) | 0.000 | -0.120 | -0.098 | -0.143 | -0.410 | 0.147 |
| V2 | 0.004109 | 0.345 | 83.923 | 134.649 | 0.0002 | 1.000 | RESPONDS IN BOX (STRONG) | 0.714 | 0.680 | 0.752 | 0.560 | 0.328 | 0.728 |
| V3 | 3.103e-05 | 0.002084 | 67.149 | 125.963 | 0.0003 | 1.000 | RESPONDS IN BOX (STRONG) | 0.416 | 0.346 | 0.503 | -0.715 | -0.830 | -0.540 |
| E5 | 0.000 | 0.000 | n/a | n/a | n/a | n/a | DEAD ON n0_E (constant) | n/a | n/a | n/a | n/a | n/a | n/a |
| R1 | 0.000 | 0.000 | n/a | n/a | n/a | n/a | DEAD ON n0_E (constant) | n/a | n/a | n/a | n/a | n/a | n/a |
| R3 | 0.000 | 0.000 | n/a | n/a | n/a | n/a | DEAD ON n0_E (constant) | n/a | n/a | n/a | n/a | n/a | n/a |
| D1 | 4358.402 | 2.836e+06 | 650.623 | 1019.728 | 0.0001 | 1.000 | RESPONDS IN BOX (STRONG) | 0.899 | 0.886 | 0.927 | -0.421 | -0.630 | -0.155 |
| D2 | 0.001225 | 0.133 | 108.682 | 159.557 | 0.0001 | 1.000 | RESPONDS IN BOX (STRONG) | 0.696 | 0.659 | 0.654 | -0.450 | -0.651 | -0.190 |

D3 check (no bar): {'D3_gen1_starts': [0.0], 'D3_gen93_starts': [0.0]}. landing_rows.csv cross-check: {'rows': 48, 'checked': ['suspect', 'G_run_usd', 'R1', 'R2']}.

N1_off = N1 - N4 cross-checked against line_summary.csv on all 48 runs: range 30701-31128 line-hours.

## 4. Pairs (directed ids; oriented Spearman, raw and T-residual)

| pair | rho_raw | rho_raw_lo95 | rho_raw_hi95 | rho_resid | rho_resid_lo95 | rho_resid_hi95 | borderline_R3 | wave_d_redundant | redundant_pair | size_co_monotone | tradeoff_size | tradeoff_composition | wave_d_redundant_only |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| V1|E1 | -0.819 | -0.895 | -0.696 | -0.054 | -0.333 | 0.233 | False | False | False | False | True | False | False |
| V1|X1 | -0.896 | -0.941 | -0.821 | -0.137 | -0.405 | 0.153 | False | False | False | False | True | False | False |
| V1|N1 | 0.950 | 0.913 | 0.972 | 0.253 | -0.033 | 0.501 | False | False | False | True | False | False | False |
| V1|E4 | -0.965 | -0.980 | -0.938 | -0.240 | -0.490 | 0.048 | False | False | False | False | True | False | False |
| V1|N4 | 0.966 | 0.940 | 0.981 | 0.421 | 0.155 | 0.630 | False | False | False | True | False | False | False |
| V1|N5 | -0.969 | -0.983 | -0.946 | -0.319 | -0.553 | -0.038 | False | False | False | False | True | False | False |
| V1|E6 | 0.982 | 0.967 | 0.990 | 0.551 | 0.317 | 0.722 | False | False | True | False | False | False | False |
| V1|E2 | -0.773 | -0.867 | -0.626 | -0.046 | -0.326 | 0.241 | False | False | False | False | True | False | False |
| V1|E3 | -0.838 | -0.906 | -0.727 | -0.075 | -0.351 | 0.214 | False | False | False | False | True | False | False |
| V1|V2 | -0.867 | -0.924 | -0.774 | -0.115 | -0.386 | 0.175 | False | False | False | False | True | False | False |
| E1|X1 | 0.982 | 0.967 | 0.990 | 0.968 | 0.943 | 0.982 | False | True | True | False | False | False | False |
| E1|R4 | -0.761 | -0.859 | -0.609 | -0.335 | -0.565 | -0.056 | False | False | False | False | True | False | False |
| E1|N1 | -0.787 | -0.875 | -0.648 | -0.262 | -0.509 | 0.024 | False | False | False | False | True | False | False |
| E1|E4 | 0.911 | 0.846 | 0.950 | 0.837 | 0.725 | 0.906 | True | False | False | False | False | False | False |
| E1|N4 | -0.909 | -0.948 | -0.843 | -0.805 | -0.886 | -0.675 | False | False | False | False | True | True | False |
| E1|N5 | 0.913 | 0.850 | 0.951 | 0.829 | 0.713 | 0.901 | True | False | False | False | False | False | False |
| E1|E6 | -0.732 | -0.841 | -0.565 | 0.656 | 0.456 | 0.792 | False | False | False | False | True | False | False |
| E1|R5 | -0.682 | -0.809 | -0.494 | -0.523 | -0.703 | -0.281 | False | False | False | False | True | True | False |
| E1|E2 | 0.962 | 0.932 | 0.979 | 0.924 | 0.868 | 0.957 | False | False | True | False | False | False | False |
| E1|E3 | 0.991 | 0.984 | 0.995 | 0.972 | 0.951 | 0.984 | False | False | True | False | False | False | False |
| E1|E8 | -0.505 | -0.690 | -0.257 | 0.00152 | -0.283 | 0.286 | False | False | False | False | True | False | False |
| E1|V2 | 0.992 | 0.986 | 0.996 | 0.988 | 0.978 | 0.993 | False | True | True | False | False | False | False |
| X1|R4 | -0.790 | -0.877 | -0.652 | -0.310 | -0.546 | -0.028 | False | False | False | False | True | False | False |
| X1|N1 | -0.858 | -0.919 | -0.760 | -0.347 | -0.575 | -0.070 | False | False | False | False | True | False | False |
| X1|E4 | 0.965 | 0.938 | 0.980 | 0.888 | 0.807 | 0.936 | False | False | True | False | False | False | False |
| X1|N4 | -0.962 | -0.979 | -0.933 | -0.854 | -0.916 | -0.752 | False | False | False | False | True | True | False |
| X1|N5 | 0.966 | 0.939 | 0.981 | 0.892 | 0.814 | 0.938 | False | False | True | False | False | False | False |
| X1|E6 | -0.825 | -0.899 | -0.706 | 0.559 | 0.327 | 0.728 | False | False | False | False | True | False | False |
| X1|R5 | -0.636 | -0.779 | -0.429 | -0.505 | -0.690 | -0.258 | False | False | False | False | True | True | False |
| X1|E2 | 0.939 | 0.892 | 0.965 | 0.906 | 0.838 | 0.947 | False | False | True | False | False | False | False |
| X1|E3 | 0.985 | 0.973 | 0.991 | 0.957 | 0.925 | 0.976 | False | False | True | False | False | False | False |
| X1|E8 | -0.552 | -0.723 | -0.318 | -0.053 | -0.332 | 0.235 | False | False | False | False | True | False | False |
| X1|V2 | 0.995 | 0.991 | 0.997 | 0.988 | 0.979 | 0.993 | False | True | True | False | False | False | False |
| R4|E4 | -0.770 | -0.865 | -0.622 | -0.201 | -0.459 | 0.088 | False | False | False | False | True | False | False |
| R4|N5 | -0.789 | -0.877 | -0.650 | -0.286 | -0.528 | -0.002429 | False | False | False | False | True | False | False |
| R4|E2 | -0.780 | -0.871 | -0.637 | -0.366 | -0.589 | -0.091 | False | False | False | False | True | False | False |
| R4|E3 | -0.742 | -0.847 | -0.580 | -0.271 | -0.516 | 0.014 | False | False | False | False | True | False | False |
| R4|V2 | -0.789 | -0.877 | -0.650 | -0.335 | -0.565 | -0.056 | False | False | False | False | True | False | False |
| N1|E4 | -0.936 | -0.964 | -0.888 | -0.393 | -0.609 | -0.123 | False | False | False | False | True | False | False |
| N1|N4 | 0.950 | 0.911 | 0.972 | 0.394 | 0.124 | 0.610 | False | False | False | True | False | False | False |
| N1|N5 | -0.938 | -0.965 | -0.891 | -0.397 | -0.612 | -0.128 | False | False | False | False | True | False | False |
| N1|E6 | 0.957 | 0.924 | 0.976 | 0.064 | -0.225 | 0.342 | False | False | False | True | False | False | False |
| N1|E2 | -0.751 | -0.853 | -0.593 | -0.303 | -0.540 | -0.020 | False | False | False | False | True | False | False |
| N1|E3 | -0.800 | -0.883 | -0.667 | -0.222 | -0.476 | 0.066 | False | False | False | False | True | False | False |
| N1|V2 | -0.833 | -0.903 | -0.719 | -0.307 | -0.544 | -0.025 | False | False | False | False | True | False | False |
| E4|N4 | -0.993 | -0.996 | -0.987 | -0.824 | -0.898 | -0.705 | False | False | False | False | True | True | False |
| E4|N5 | 0.993 | 0.988 | 0.996 | 0.918 | 0.857 | 0.953 | False | False | True | False | False | False | False |
| E4|E6 | -0.928 | -0.959 | -0.874 | 0.358 | 0.082 | 0.583 | False | False | False | False | True | False | False |
| E4|R5 | -0.528 | -0.706 | -0.287 | -0.309 | -0.545 | -0.027 | False | False | False | False | True | False | False |
| E4|E2 | 0.863 | 0.767 | 0.921 | 0.760 | 0.608 | 0.859 | True | False | False | False | False | False | False |
| E4|E3 | 0.927 | 0.872 | 0.958 | 0.852 | 0.749 | 0.915 | True | False | False | False | False | False | False |
| E4|E8 | -0.642 | -0.784 | -0.438 | -0.278 | -0.521 | 0.006889 | False | False | False | False | True | False | False |
| E4|V2 | 0.945 | 0.904 | 0.969 | 0.866 | 0.771 | 0.923 | False | False | True | False | False | False | False |
| N4|N5 | -0.995 | -0.997 | -0.990 | -0.910 | -0.949 | -0.844 | False | False | False | False | True | True | False |
| N4|E6 | 0.931 | 0.880 | 0.961 | -0.239 | -0.490 | 0.048 | True | False | False | True | False | False | False |
| N4|E2 | -0.864 | -0.922 | -0.769 | -0.722 | -0.835 | -0.550 | False | False | False | False | True | True | False |
| N4|E3 | -0.921 | -0.955 | -0.862 | -0.814 | -0.892 | -0.690 | False | False | False | False | True | True | False |
| N4|V2 | -0.944 | -0.968 | -0.901 | -0.841 | -0.908 | -0.732 | False | False | False | False | True | True | False |
| N5|E6 | -0.931 | -0.961 | -0.880 | 0.353 | 0.076 | 0.579 | False | False | False | False | True | False | False |
| N5|R5 | -0.556 | -0.725 | -0.322 | -0.450 | -0.651 | -0.190 | False | False | False | False | True | False | False |
| N5|E2 | 0.867 | 0.774 | 0.924 | 0.770 | 0.622 | 0.865 | True | False | False | False | False | False | False |
| N5|E3 | 0.925 | 0.869 | 0.957 | 0.856 | 0.755 | 0.917 | True | False | False | False | False | False | False |
| N5|E8 | -0.616 | -0.766 | -0.402 | -0.214 | -0.470 | 0.074 | False | False | False | False | True | False | False |
| N5|V2 | 0.948 | 0.909 | 0.971 | 0.874 | 0.784 | 0.928 | False | False | True | False | False | False | False |
| E6|E2 | -0.681 | -0.809 | -0.492 | 0.604 | 0.386 | 0.758 | False | False | False | False | True | False | False |
| E6|E3 | -0.759 | -0.858 | -0.605 | 0.660 | 0.462 | 0.795 | False | False | False | False | True | False | False |
| E6|V2 | -0.789 | -0.877 | -0.651 | 0.603 | 0.385 | 0.757 | False | False | False | False | True | False | False |
| R5|E2 | -0.753 | -0.855 | -0.597 | -0.616 | -0.766 | -0.402 | False | False | False | False | True | True | False |
| R5|E3 | -0.631 | -0.776 | -0.423 | -0.440 | -0.644 | -0.178 | False | False | False | False | True | False | False |
| R5|V2 | -0.661 | -0.796 | -0.464 | -0.516 | -0.698 | -0.271 | False | False | False | False | True | True | False |
| E2|E3 | 0.926 | 0.871 | 0.958 | 0.842 | 0.734 | 0.909 | True | False | False | False | False | False | False |
| E2|E8 | -0.503 | -0.689 | -0.255 | -0.016 | -0.298 | 0.270 | False | False | False | False | True | False | False |
| E2|V2 | 0.956 | 0.923 | 0.975 | 0.909 | 0.842 | 0.948 | False | False | True | False | False | False | False |
| E3|E8 | -0.516 | -0.698 | -0.272 | -0.010 | -0.293 | 0.275 | False | False | False | False | True | False | False |
| E3|V2 | 0.987 | 0.977 | 0.993 | 0.976 | 0.958 | 0.987 | False | True | True | False | False | False | False |
| E8|V2 | -0.549 | -0.721 | -0.314 | -0.022 | -0.304 | 0.264 | False | False | False | False | True | False | False |

Clusters (complete linkage on the REDUNDANT relation):

- n0E-C1: E6, V1 -> survivor V1
- n0E-C2: E1, E2, X1 -> survivor E1
- n0E-C3: E4, N5, V2 -> survivor E4

## 5. Adjudication with wave D (R-1 ... R-5)

R-5 conflict rows (both verdicts printed):

| id | waveD_B_verdict | n0E_verdict | R1_label |
|---|---|---|---|
| E2 | UNREADABLE (B_j) | RESPONDS IN BOX | BOX-ONLY RESPONSE (eligible) |
| E3 | UNREADABLE (B_j) | RESPONDS IN BOX | BOX-ONLY RESPONSE (eligible) |
| E6 | UNREADABLE (B_j) | RESPONDS IN BOX (STRONG) | BOX-ONLY RESPONSE (eligible) |
| E7 | UNREADABLE (B_j) | RESPONDS IN BOX (STRONG) | BOX-ONLY RESPONSE (eligible) |
| R4 | UNREADABLE (B_j) | RESPONDS IN BOX (BORDERLINE) | BOX-ONLY RESPONSE (eligible) |
| R7 | UNREADABLE (B_j) | RESPONDS IN BOX | BOX-ONLY RESPONSE (eligible) |
| N1 | UNREADABLE (B_j) | RESPONDS IN BOX | BOX-ONLY RESPONSE (eligible) |
| N4 | UNREADABLE (B_j) | RESPONDS IN BOX (STRONG) | BOX-ONLY RESPONSE (eligible) |
| N5 | UNREADABLE (B_j) | RESPONDS IN BOX (STRONG) | BOX-ONLY RESPONSE (eligible) |

N family (N1 = N4 + N1_off):

- N1: B_j 114.9, IDR/B_j 6.429, range/B_j 11.094, RESPONDS IN BOX, status OBJECTIVE
- N4: B_j 36.97, IDR/B_j 17.381, range/B_j 31.353, RESPONDS IN BOX (STRONG), status SIZE-CO-MONOTONE (with V1, N1)
- N1_off (diagnostic, not a pool id): range 30701-31128, IDR 213

## E. E-D1b decision table (Parts A + B; Part C appended when it lands)

Seat walk (R-4): M = 3 — M != 4 reopens plan §6.4 gate numbers for the PI.

- V: **V1** — first eligible in global_order
- E: **E1** — plan §1.2 final (E1)
- R: **EMPTY** — no member RESPONDS IN BOX (non-borderline or wave-D-backed) -> M < 4; the next family does not fill it until the PI decides
- N: **N1** — first eligible in global_order
- family X: every member is in a cluster with another family X1->E1 (no seat consumed)

| id | family | global_order | waveD_label_57 | waveD_range_over_B_L60 | waveD_range_over_B_L120 | waveD_range_over_B_L180 | waveD_B_verdict | IDR_over_B | mantel_p | signal_share | eta2_T | comp_rho | cluster | survivor | tradeoffs | waveD_cost_gap_read | n0E_cost_gap_read | status | reason |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| V1 | V | 1 | LOCATION-SENSITIVE | 1.392 | 3.266 | 6.576 | READABLE (2 of 3) | 93.275 | 0.0001 | 1.000 | 0.978 | -0.469 | n0E-C1 | V1 | size:E1; size:X1; size:E4; size:N5; size:E2; size:E3; size:V2 |  |  | OBJECTIVE | seat V: first eligible in global_order |
| E1 | E | 2 | LOCATION-SENSITIVE | 0.922 | 2.312 | 3.865 | READABLE (2 of 3) | 14.055 | 0.0003 | 0.998 | 0.641 | -0.608 | n0E-C2 | E1 | size:V1; size:R4; size:N1; size:N4; composition:N4; size:E6; size:R5; composition:R5; size:E8 | L60 0/6 raw; 0/6 scaled; L120 0/6 raw; 3/6 scaled; L180 0/6 raw; 5/6 scaled | IDR 3.35e+07 vs median pair bound G_a+G_b 4.016e+07 (0.83x; evidence only) | OBJECTIVE | seat E: plan §1.2 final (E1) |
| X1 | X | 3 | REDUNDANT->E1 | 1.237 | 5.416 | 8.805 | READABLE (2 of 3) | 27.399 | 0.0004 | 1.000 | 0.741 | -0.508 | n0E-C2 | E1 | size:V1; size:R4; size:N1; size:N4; composition:N4; size:E6; size:R5; composition:R5; size:E8 |  |  | REDUNDANT->E1 | REDUNDANT->E1 on n0_E (n0E-C2) |
| R4 | R | 4 | LOCATION-SENSITIVE | 1.043 | 0.941 | 1.841 | UNREADABLE (B_j) | 2.115 | 0.0009 | 0.916 | 0.514 | 0.073 | n/a | n/a | size:E1; size:X1; size:E4; size:N5; size:E2; size:E3; size:V2 |  |  | DIAGNOSTIC | BORDERLINE-only response (IDR/B_j in [2, 3), no wave-D backing) |
| N1 | N | 5 | LOCATION-SENSITIVE | 0.635 | 1.227 | 1.157 | UNREADABLE (B_j) | 6.429 | 0.0001 | 0.992 | 0.891 | -0.027 | n/a | n/a | size:E1; size:X1; size:E4; size:N5; size:E2; size:E3; size:V2 |  |  | OBJECTIVE | seat N: first eligible in global_order |
| E4 | E | 6 | LOCATION-SENSITIVE | 0.916 | 2.065 | 2.102 | READABLE (2 of 3) | 10.460 | 0.0001 | 0.997 | 0.873 | -0.375 | n0E-C3 | E4 | size:V1; size:R4; size:N1; size:N4; composition:N4; size:E6; size:R5; size:E8 |  |  | DIAGNOSTIC | E seat is E1 only (plan §1.2 final) |
| R2 | R | 7 | LOCATION-SENSITIVE | 1.172 | 0.638 | 0.649 | UNREADABLE (B_j) | 0.747 | 0.173 | 0.381 | 0.067 | 0.093 | n/a | n/a |  |  |  | GUARDRAIL | guardrail (plan §1.3); never seated |
| R7 | R | 8 | DIAGNOSTIC | 0.807 | 1.095 | 1.187 | UNREADABLE (B_j) | 4.401 | 0.0001 | 0.980 | 0.689 | -0.446 | n/a | n/a |  |  |  | DIAGNOSTIC | dir '-': shown, never clustered or seated |
| N4 | N | 9 | LOCATION-SENSITIVE | 0.649 | 0.866 | 2.759 | UNREADABLE (B_j) | 17.381 | 0.0001 | 0.999 | 0.925 | 0.268 | n/a | n/a | size:E1; composition:E1; size:X1; composition:X1; size:E4; composition:E4; size:N5; composition:N5; size:E2; composition:E2; size:E3; composition:E3; size:V2; composition:V2 |  |  | SIZE-CO-MONOTONE (with V1, N1) | family N seat held by N1 (earlier in global_order) |
| N5 | N | 10 | LOCATION-SENSITIVE | 0.939 | 1.163 | 2.816 | UNREADABLE (B_j) | 17.117 | 0.0001 | 0.999 | 0.926 | -0.393 | n0E-C3 | E4 | size:V1; size:R4; size:N1; size:N4; composition:N4; size:E6; size:R5; size:E8 |  |  | REDUNDANT->E4 | REDUNDANT->E4 on n0_E (n0E-C3) |
| E6 | E | 11 | LOCATION-SENSITIVE | 0.266 | 1.071 | 0.585 | UNREADABLE (B_j) | 14.572 | 0.0001 | 0.998 | 0.697 | 0.740 | n0E-C1 | V1 | size:E1; size:X1; size:E4; size:N5; size:E2; size:E3; size:V2 |  |  | REDUNDANT->V1 | REDUNDANT->V1 on n0_E (n0E-C1) |
| R5 | R | 12 | LOCATION-SENSITIVE | 0.643 | 0.541 | 0.568 | UNREADABLE (B_j) | 0.891 | 0.109 | 0.564 | -0.715 | 0.321 | n/a | n/a | size:E1; composition:E1; size:X1; composition:X1; size:E4; size:N5; size:E2; composition:E2; size:E3; size:V2; composition:V2 |  |  | DIAGNOSTIC | NOT RESPONDS (n0_E) |
| N3 | N | 13 | LOCATION-SENSITIVE | 0.421 | 1.096 | 0.544 | UNREADABLE (B_j) | 0.659 | 0.112 | 0.033 | -1.720 | 0.046 | n/a | n/a |  |  |  | DIAGNOSTIC | NOT RESPONDS (n0_E) |
| E2 | E | 14 | LOCATION-SENSITIVE | 0.687 | 0.454 | 0.844 | UNREADABLE (B_j) | 3.293 | 0.0006 | 0.967 | 0.557 | -0.568 | n0E-C2 | E1 | size:V1; size:R4; size:N1; size:N4; composition:N4; size:E6; size:R5; composition:R5; size:E8 | L60 0/6 raw; 0/6 scaled; L120 0/6 raw; 0/6 scaled; L180 0/6 raw; 0/6 scaled | IDR 9.557e+06 vs median pair bound G_a+G_b 4.016e+07 (0.24x; evidence only) | REDUNDANT->E1 | REDUNDANT->E1 on n0_E (n0E-C2) |
| R6 | R | 15 | LOCATION-SENSITIVE | 0.336 | 0.964 | 1.348 | UNREADABLE (B_j) | 0.812 | 0.676 | 0.546 | -2.974 | 0.142 | n/a | n/a |  |  |  | DIAGNOSTIC | NOT RESPONDS (n0_E) |
| N2 | N | 16 | LOCATION-SENSITIVE | 1.000 | 0.667 | 1.667 | UNREADABLE (B_j) | 0.433 | 0.556 | 0.376 | -0.040 | -0.112 | n/a | n/a |  |  |  | DIAGNOSTIC | NOT RESPONDS (n0_E) |
| E3 | E | 17 | LOCATION-SENSITIVE | 0.855 | 1.236 | 2.272 | UNREADABLE (B_j) | 6.995 | 0.0004 | 0.993 | 0.674 | -0.592 | n/a | n/a | size:V1; size:R4; size:N1; size:N4; composition:N4; size:E6; size:R5; size:E8 | L60 0/6 raw; 0/6 scaled; L120 0/6 raw; 4/6 scaled; L180 0/6 raw; 4/6 scaled | IDR 2.427e+07 vs median pair bound G_a+G_b 4.016e+07 (0.60x; evidence only) | DIAGNOSTIC | E seat is E1 only (plan §1.2 final) |
| R8 | R | 18 | DIAGNOSTIC | 0.572 | 0.899 | 0.652 | UNREADABLE (B_j) | 1.162 | 0.0032 | 0.755 | 0.523 | -0.153 | n/a | n/a |  |  |  | DIAGNOSTIC | dir '-': shown, never clustered or seated |
| E7 | E | 19 | DIAGNOSTIC | 0.717 | 1.171 | 2.338 | UNREADABLE (B_j) | 14.090 | 0.0001 | 0.998 | 0.891 | -0.438 | n/a | n/a |  |  |  | DIAGNOSTIC | dir '-': shown, never clustered or seated |
| E8 | E | 20 | LOCATION-SENSITIVE | 0.695 | 1.446 | 1.066 | UNREADABLE (B_j) | 1.016 | 0.027 | 0.696 | 0.355 | -0.140 | n/a | n/a | size:E1; size:X1; size:E4; size:N5; size:E2; size:E3; size:V2 |  |  | DIAGNOSTIC | NOT RESPONDS (n0_E) |
| E9 | E | 21 | DEAD ON WAVE D | n/a | n/a | n/a | UNREADABLE (B_j) | n/a | 0.833 | 1.000 | 0.000 | -0.143 | n/a | n/a |  |  |  | DIAGNOSTIC | READABLE (RULER=0) (n0_E) |
| V2 | V | 22 | REDUNDANT->E1 | 4.275 | 15.850 | 25.615 | READABLE (2 of 3) | 83.923 | 0.0002 | 1.000 | 0.714 | 0.560 | n0E-C3 | E4 | size:V1; size:R4; size:N1; size:N4; composition:N4; size:E6; size:R5; composition:R5; size:E8 |  |  | REDUNDANT->E4 | REDUNDANT->E4 on n0_E (n0E-C3) |
| V3 | V | 23 | DIAGNOSTIC | 4.928 | 12.426 | 18.554 | READABLE (2 of 3) | 67.149 | 0.0003 | 1.000 | 0.416 | -0.715 | n/a | n/a |  |  |  | DIAGNOSTIC | dir '-': shown, never clustered or seated |
| E5 | E | 24 | n/a | n/a | n/a | n/a | n/a (not graded on wave D) | n/a | n/a | n/a | n/a | n/a | n/a | n/a |  |  |  | DEAD | dead (57 A2 list or constant on n0_E) |
| R1 | R | 25 | n/a | n/a | n/a | n/a | n/a (not graded on wave D) | n/a | n/a | n/a | n/a | n/a | n/a | n/a |  |  |  | DEAD | dead (57 A2 list or constant on n0_E) |
| R3 | R | 26 | n/a | n/a | n/a | n/a | n/a (not graded on wave D) | n/a | n/a | n/a | n/a | n/a | n/a | n/a |  |  |  | DEAD | dead (57 A2 list or constant on n0_E) |
| D1 | D | 27 | DIAGNOSTIC | 14.894 | 59.003 | 116.647 | READABLE (2 of 3) | 650.623 | 0.0001 | 1.000 | 0.899 | -0.421 | n/a | n/a |  |  |  | DIAGNOSTIC | dir '-': shown, never clustered or seated |
| D2 | D | 28 | DIAGNOSTIC | 100.837 | 199.739 | 263.249 | READABLE (2 of 3) | 108.682 | 0.0001 | 1.000 | 0.696 | -0.450 | n/a | n/a |  |  |  | DIAGNOSTIC | dir '-': shown, never clustered or seated |

## Deviations

- B_j with D2 excluded gives N2 3.0, N1 114.9, N4 37.0; prompt 62 v1.1 quotes 2.60 / 99.5 / 32, which are the 8-value (D2-included) numbers. The pinned definition (61 §3 / contract addendum) is applied and equals 63's re-emitted `per_candidate.<j>.bar.B` (asserted).
- B_j / ruler spans 2.84-10.28x (prompt text 3.5-11.5x). The ruler column is the current ercot_noise.json `ruler` (re-emitted by 63 A1 d265580 with the D2 pair excluded; ruler_zero now {E9} only, N2 left it).
- No input md5 exists for the noise runs; the D2 exclusion asserts the md5 of the effective PEM slice (RT + DA wind, site 206) plus equal overall.csv md5.
- Implementation fix after the first real execution (same day, before any output was committed): the seat walk's 'absorbed family' test treated a cluster SURVIVOR as absorbed, so family V (V1 = survivor of {E6, V1}; V2 REDUNDANT->E4) consumed no seat and the first run reported M = 2 (E1 / R EMPTY / N1). That contradicted the pinned R-4 (skip REDUNDANT members only). The fix restores R-4 as registered; no threshold, statistic or order changed. Fix commit: see PROGRESS (prompt 62).
- R-3 band computed exactly ([0.842, 0.938]); prompt text says about 0.86-0.93.
