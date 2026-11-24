# POOL_N0E_STANDINGS_v2 — E-D1b rule v2 re-walk on n0_E (prompt 65 v1.1; disclosed post-hoc amendment)

**This amendment is post hoc and not blind. It was written after the v1 read, the Seed re-grade, screening_v3 and the N4–V1 residual interval were known. We do not present it as a pre-registered selection. Every station reports three vectors from the same runs: v1 pre-registered (V1 · E1 · N1), v2 (V1 · E1 · N4), and v2 with borderline → REDUNDANT (V1 · E1). A claim about the flowgate objective is stated only as conditional on v2. Rule v2 is pre-registered unchanged for the next dataset, which is its real test. [ERRATUM 2026-11-24, strategy session, after the read: this verbatim disclosure predates the real walk; the walk itself gives v2 = V1 · E1 (M = 2) — N4 is suppressed by a failed composition-resolvability test (residual Mantel p 0.025 > 0.01), not by a borderline pair; the vectors reported are v1 V1 · E1 · N1, v2 V1 · E1, and the pre-read prediction V1 · E1 · N4 as a conditional reading.]**

Read date (UTC): 2026-11-24T06:31:03+00:00. Rules: plan AMENDMENT 2026-11-24 (commit (i) 212d60d, block sha256 `e3712a7f4d8e0542d5421ed13453fd0a722a582fa7b087b6b34d831581ac28be`); script + tests commit (ii) b8a3285; git HEAD at the read b8a3285. `waves/n0_E/design_matrix.csv` sha256 `87ee148e8d9237c23957f6b9999d70c1bef5dba47a622cdf9e2017394b19a049`.

Input: 48 n0_E grading rows (`pool_standings.build_wave("n0_E")`); no GP fitted (`analysis/ercot_gp/committed_configs.json` absent, asserted); random_E not read; holdout exposure 0 / 24.

## 1. Ledger

Everything in AMENDMENT 2026-11-17's ledger plus the v1 Part B read (d706199), the Seed-bar re-grade (baf77c3), screening_v3 (e58f4bd), location_contrast_E (4b7bf85), the family-free strength-first trial, the three 11-24 reviewer reports and the §8.15 additions (anchor spreads from noise_seed_E Seeds 1–4; residual IDR/B estimated from printed η²_T and IDR). Implementation pins: module docstring of `pool_n0E_v2.py`.

## 2. Bars (§8.1: two-run scale, pooled ν; design-2 (site 206) structural-zero pair excluded) and floors

| id | s_pert | nu_pert | s_seed | nu_seed | sources_ratio | sources_disagree_2x | A3_63 | s_j | nu | max_abs_delta | B_j | B_lo | B_up | B_binding_term | B_pert_v1 | B_seed_63 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| V1 | 4523.397 | 6 | 4376.236 | 16 | 0.967 | False | AGREE | 4416.857 | 22 | 1.227e+04 | 1.874e+04 | 1.509e+04 | 2.502e+04 | 3*sqrt2*s_j | 1.617e+04 | 1.857e+04 |
| V2 | 0.001225 | 6 | 0.001812 | 16 | 1.479 | False | AGREE | 0.001672 | 22 | 0.005119 | 0.007095 | 0.005713 | 0.009474 | 3*sqrt2*s_j | 0.004109 | 0.007687 |
| V3 | 7.784e-06 | 6 | 4.536e-05 | 16 | 5.827 | True | DISAGREE | 3.89e-05 | 22 | 0.0001315 | 0.000165 | 0.0001329 | 0.0002204 | 3*sqrt2*s_j | 3.103e-05 | 0.0001924 |
| E1 | 5.857e+05 | 6 | 3.124e+05 | 16 | 0.533 | False | AGREE | 4.057e+05 | 22 | 1.862e+06 | 1.862e+06 | 1.862e+06 | 2.298e+06 | max|delta| | 2.383e+06 | 1.325e+06 |
| E2 | 7.609e+05 | 6 | 8.583e+05 | 16 | 1.128 | False | AGREE | 8.328e+05 | 22 | 2.931e+06 | 3.533e+06 | 2.931e+06 | 4.718e+06 | 3*sqrt2*s_j | 2.902e+06 | 3.641e+06 |
| E3 | 7.052e+05 | 6 | 8.411e+05 | 16 | 1.193 | False | AGREE | 8.063e+05 | 22 | 3.137e+06 | 3.421e+06 | 3.137e+06 | 4.568e+06 | 3*sqrt2*s_j | 3.47e+06 | 3.569e+06 |
| E4 | 1.99e+06 | 6 | 2.382e+06 | 16 | 1.197 | False | AGREE | 2.281e+06 | 22 | 7.881e+06 | 9.679e+06 | 7.881e+06 | 1.292e+07 | 3*sqrt2*s_j | 8.505e+06 | 1.01e+07 |
| E5 | 0.000 | 6 | 0.000 | 16 | n/a | False | AGREE (both exactly 0) | 0.000 | 22 | 0.000 | 0.000 | 0.000 | 0.000 | 3*sqrt2*s_j | 0.000 | 0.000 |
| E6 | 6.046e+05 | 6 | 4.106e+05 | 16 | 0.679 | False | AGREE | 4.715e+05 | 22 | 1.555e+06 | 2.001e+06 | 1.611e+06 | 2.671e+06 | 3*sqrt2*s_j | 2.908e+06 | 1.742e+06 |
| E7 | 0.003535 | 6 | 0.003353 | 16 | 0.949 | False | AGREE | 0.003403 | 22 | 0.012 | 0.014 | 0.012 | 0.019 | 3*sqrt2*s_j | 0.017 | 0.014 |
| E8 | 0.072 | 6 | 0.069 | 16 | 0.955 | False | AGREE | 0.070 | 22 | 0.200 | 0.295 | 0.238 | 0.394 | 3*sqrt2*s_j | 0.302 | 0.291 |
| E9 | 0.000 | 6 | 0.316 | 16 | n/a | True | DISAGREE (one ruler is 0) | 0.270 | 22 | 1.000 | 1.144 | 1.000 | 1.528 | 3*sqrt2*s_j | 0.000 | 1.342 |
| R1 | 0.000 | 6 | 0.000 | 16 | n/a | False | AGREE (both exactly 0) | 0.000 | 22 | 0.000 | 0.000 | 0.000 | 0.000 | 3*sqrt2*s_j | 0.000 | 0.000 |
| R2 | 31.338 | 6 | 24.215 | 16 | 0.773 | False | AGREE | 26.349 | 22 | 59.895 | 111.791 | 90.025 | 149.278 | 3*sqrt2*s_j | 102.295 | 102.736 |
| R3 | 0.000 | 6 | 0.000 | 16 | n/a | False | AGREE (both exactly 0) | 0.000 | 22 | 0.000 | 0.000 | 0.000 | 0.000 | 3*sqrt2*s_j | 0.000 | 0.000 |
| R4 | 37.886 | 6 | 65.087 | 16 | 1.718 | False | AGREE | 58.927 | 22 | 161.000 | 250.006 | 201.329 | 333.841 | 3*sqrt2*s_j | 146.653 | 276.140 |
| R5 | 3999.025 | 6 | 2879.606 | 16 | 0.720 | False | AGREE | 3223.686 | 22 | 1.237e+04 | 1.368e+04 | 1.237e+04 | 1.826e+04 | 3*sqrt2*s_j | 1.662e+04 | 1.237e+04 |
| R6 | 2.558e+04 | 6 | 2.189e+04 | 16 | 0.856 | False | AGREE | 2.295e+04 | 22 | 6.197e+04 | 9.738e+04 | 7.842e+04 | 1.3e+05 | 3*sqrt2*s_j | 1.033e+05 | 9.286e+04 |
| R7 | 6.607e+04 | 6 | 6.696e+04 | 16 | 1.013 | False | AGREE | 6.672e+04 | 22 | 2.333e+05 | 2.831e+05 | 2.333e+05 | 3.78e+05 | 3*sqrt2*s_j | 2.688e+05 | 2.841e+05 |
| R8 | 419.591 | 6 | 325.011 | 16 | 0.775 | False | AGREE | 353.325 | 22 | 800.000 | 1499.032 | 1207.163 | 2001.703 | 3*sqrt2*s_j | 1543.306 | 1378.905 |
| N1 | 29.524 | 6 | 57.060 | 16 | 1.933 | False | DISAGREE | 51.045 | 22 | 177.000 | 216.565 | 177.000 | 289.186 | 3*sqrt2*s_j | 114.924 | 242.083 |
| N2 | 0.816 | 6 | 0.880 | 16 | 1.078 | False | AGREE | 0.863 | 22 | 2.000 | 3.663 | 2.950 | 4.891 | 3*sqrt2*s_j | 3.000 | 3.735 |
| N3 | 3.146 | 6 | 2.469 | 16 | 0.785 | False | AGREE | 2.671 | 22 | 7.038 | 11.330 | 9.124 | 15.130 | 3*sqrt2*s_j | 13.974 | 10.474 |
| N4 | 11.015 | 6 | 10.492 | 16 | 0.952 | False | AGREE | 10.637 | 22 | 37.000 | 45.129 | 37.000 | 60.262 | 3*sqrt2*s_j | 36.966 | 44.512 |
| N5 | 0.052 | 6 | 0.045 | 16 | 0.860 | False | AGREE | 0.047 | 22 | 0.148 | 0.200 | 0.161 | 0.267 | 3*sqrt2*s_j | 0.183 | 0.191 |
| X1 | 9960.898 | 6 | 9326.155 | 16 | 0.936 | False | AGREE | 9503.472 | 22 | 3.071e+04 | 4.032e+04 | 3.247e+04 | 5.384e+04 | 3*sqrt2*s_j | 3.645e+04 | 3.957e+04 |
| D1 | 1262.488 | 4 | 3744.166 | 16 | 2.966 | True | DISAGREE | 3396.145 | 20 | 1.069e+04 | 1.441e+04 | 1.15e+04 | 1.956e+04 | 3*sqrt2*s_j | 4358.402 | 1.589e+04 |
| D2 | 0.000373 | 4 | 0.0003889 | 16 | 1.043 | False | AGREE | 0.0003858 | 20 | 0.001143 | 0.001637 | 0.001306 | 0.002222 | 3*sqrt2*s_j | 0.001225 | 0.00165 |

Floors (§8.5; disclosed: set after the relative responses were seen; point IDR compared): V1 58287.3; E1 8.06138e+06; X1 194521; N4 87.6; R4 (informational; role gate excludes it) 154.09. E1 median pair gap bound G_a + G_b = 4.016e+07 (evidence only, never a floor; E1 IDR / gap bound = 0.83).

$40-offer exclusion (§8.11): base_v3:1 E1 8.06138e+09 = Σ non-renewable Unit Cost 8.06138e+09 (PEM twins 0, Unit Cost NaN/0); n0_E:25 E1 8.11351e+09 = Σ non-renewable Unit Cost 8.11351e+09 (PEM twins 6, Unit Cost NaN/0). Source: data_extractors.py get_fixed_costs / get_variable_costs sum thermal units only (Prescient checkout c453890).

## 3. Per measure (item 10; §8.4)

| id | role | tier | B_j | IDR | IDR_over_B | IDR_over_B_lo90 | IDR_over_B_hi90 | resid_IDR_over_B | resid_IDR_over_B_lo90 | resid_IDR_over_B_hi90 | eta2_T | mantel_p_raw | mantel_p_resid | floor_M | floor_pass | RESOLVED | COMP_RESOLVABLE | sufficiency | trade_offs | status | why |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| V1 | OUTCOME | MAY | 1.874e+04 | 1.509e+06 | 80.502 | 58.784 | 107.135 | 8.829 | 5.697 | 12.527 | 0.978 | 0.0001 | 0.0016 | 5.829e+04 | True | True | True | ADEQUATE | size:V2; size:E1; size:E4; size:E2; size:E3; size:X1; size:N5 | SEATED (rule v2) | SEATED |
| V2 | PROXY(E1) | MAY | 0.007095 | 0.345 | 48.605 | 34.095 | 67.604 | 23.136 | 15.216 | 32.967 | 0.714 | 0.0002 | 0.0002 | n/a | True | True | True | ADEQUATE | size:V1; size:E6; size:E8; size:R4; size:R5; size:N4; size:N1 | PROXY | role PROXY never seated |
| V3 | DIAGNOSTIC | MAY | 0.000165 | 0.002084 | 12.626 | 9.287 | 18.103 | 10.164 | 6.948 | 13.112 | 0.416 | 0.0003 | 0.0002 | n/a | True | True | True | ADEQUATE |  | DIAGNOSTIC | role DIAGNOSTIC never seated |
| E1 | OUTCOME | MUST | 1.862e+06 | 3.35e+07 | 17.990 | 13.317 | 22.364 | 10.109 | 6.885 | 12.245 | 0.641 | 0.0003 | 0.0002 | 8.061e+06 | True | True | True | ADEQUATE | size:V1; size:E6; size:E8; size:R4; size:R5; size:N4; size:N1 | SEATED (rule v2) | SEATED |
| E4 | TRANSFER | MUST | 9.679e+06 | 8.896e+07 | 9.191 | 6.522 | 13.214 | 2.880 | 1.825 | 3.920 | 0.873 | 0.0001 | 0.005 | n/a | True | True | False | ADEQUATE | size:V1; size:E6; size:E8; size:R4; size:R5; size:N4; size:N1 | TRANSFER (REDUNDANT given V2, E1) | role TRANSFER never seated |
| E6 | TRANSFER | MUST | 2.001e+06 | 4.238e+07 | 21.183 | 14.943 | 28.369 | 4.704 | 3.276 | 8.947 | 0.697 | 0.0001 | 0.013 | n/a | True | True | False | ADEQUATE | size:V2; size:E1; size:E4; size:E2; size:E3; size:X1; size:N5 | TRANSFER (REDUNDANT given V1) | role TRANSFER never seated |
| E2 | COMPONENT(E1) | MUST | 3.533e+06 | 9.557e+06 | 2.705 | 1.878 | 3.556 | 1.767 | 1.217 | 2.346 | 0.557 | 0.0006 | 0.0013 | n/a | True | False | False | NOT SEATABLE (< 3) | size:V1; size:E6; size:E8; size:R4; size:R5; size:N4; size:N1 | COMPONENT (REDUNDANT given V2, E1, E4) | role COMPONENT never seated |
| E3 | COMPONENT(E1) | MUST | 3.421e+06 | 2.427e+07 | 7.095 | 4.979 | 9.156 | 4.011 | 2.511 | 4.968 | 0.674 | 0.0004 | 0.0002 | n/a | True | True | True | ADEQUATE | size:V1; size:E6; size:E8; size:R4; size:R5; size:N4; size:N1 | COMPONENT (REDUNDANT given V2, E1) | role COMPONENT never seated |
| E7 | PROXY(E4) | MUST | 0.014 | 0.234 | 16.209 | 11.735 | 23.245 | 5.113 | 3.116 | 7.042 | 0.891 | 0.0001 | 0.0094 | n/a | True | True | True | ADEQUATE |  | PROXY | role PROXY never seated |
| E8 | DIAGNOSTIC | MUST | 0.295 | 0.307 | 1.040 | 0.692 | 1.421 | 0.767 | 0.533 | 1.137 | 0.355 | 0.027 | 0.431 | n/a | False | False | False | NOT SEATABLE (< 3) | size:V2; size:E1; size:E4; size:E2; size:E3; size:X1; size:N5 | DIAGNOSTIC | role DIAGNOSTIC never seated |
| E9 | DIAGNOSTIC (dead) | MUST | 1.144 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.833 | 0.833 | n/a | False | False | False | NOT SEATABLE (< 3) |  | DIAGNOSTIC | role DIAGNOSTIC never seated |
| X1 | OUTCOME | MAY | 4.032e+04 | 9.988e+05 | 24.772 | 16.988 | 33.751 | 11.287 | 7.025 | 15.366 | 0.741 | 0.0004 | 0.0002 | 1.945e+05 | True | True | True | ADEQUATE | size:V1; size:E6; size:E8; size:R4; size:R5; size:N4; size:N1 | SUPPRESSED (REDUNDANT given E1) | suppressed: REDUNDANT given seated E1 |
| R4 | PROXY(E2 start-up cost) | MAY | 250.006 | 310.100 | 1.240 | 0.822 | 1.607 | 0.798 | 0.573 | 1.076 | 0.514 | 0.0009 | 0.029 | n/a | False | False | False | NOT SEATABLE (< 3) | size:V2; size:E1; size:E4; size:E2; size:E3; size:X1; size:N5 | PROXY | role PROXY never seated |
| R2 | GUARD | MAY | 111.791 | 76.423 | 0.684 | 0.462 | 0.906 | 0.664 | 0.441 | 0.925 | 0.067 | 0.173 | 0.549 | n/a | False | False | False | NOT SEATABLE (< 3) |  | GUARDRAIL | role GUARD never seated |
| R7 | DIAGNOSTIC | MAY | 2.831e+05 | 1.183e+06 | 4.179 | 2.763 | 5.428 | 2.266 | 1.409 | 2.861 | 0.689 | 0.0001 | 0.002 | n/a | True | True | False | FLAGGED |  | DIAGNOSTIC | role DIAGNOSTIC never seated |
| R5 | DIAGNOSTIC | MAY | 1.368e+04 | 1.48e+04 | 1.082 | 0.762 | 1.341 | 0.906 | 0.619 | 1.222 | -0.715 | 0.109 | 0.217 | n/a | False | False | False | NOT SEATABLE (< 3) | size:V2; size:E1; size:E4; size:E2; size:E3; size:X1; size:N5 | DIAGNOSTIC | role DIAGNOSTIC never seated |
| R6 | DIAGNOSTIC | MAY | 9.738e+04 | 8.389e+04 | 0.861 | 0.627 | 1.134 | 1.090 | 0.694 | 1.663 | -2.974 | 0.676 | 0.011 | n/a | False | False | False | NOT SEATABLE (< 3) |  | DIAGNOSTIC | role DIAGNOSTIC never seated |
| R8 | DIAGNOSTIC | MAY | 1499.032 | 1793.100 | 1.196 | 0.802 | 1.727 | 0.849 | 0.556 | 1.135 | 0.523 | 0.0032 | 0.066 | n/a | False | False | False | NOT SEATABLE (< 3) |  | DIAGNOSTIC | role DIAGNOSTIC never seated |
| N4 | OUTCOME | MAY | 45.129 | 642.500 | 14.237 | 10.008 | 18.875 | 4.337 | 2.311 | 5.512 | 0.925 | 0.0001 | 0.025 | 87.600 | True | True | False | ADEQUATE | size:V2; size:E1; size:E4; size:E2; size:E3; size:X1; size:N5 | SUPPRESSED (REDUNDANT given V1) | suppressed: REDUNDANT given seated V1 |
| N1 | PROXY | MAY | 216.565 | 738.800 | 3.411 | 2.340 | 4.637 | 0.943 | 0.697 | 1.236 | 0.891 | 0.0001 | 0.0042 | n/a | True | True | False | FLAGGED | size:V2; size:E1; size:E4; size:E2; size:E3; size:X1; size:N5 | PROXY (REDUNDANT given V1, E6, N4) | role PROXY never seated |
| N5 | DIAGNOSTIC | MAY | 0.200 | 3.126 | 15.657 | 11.301 | 22.851 | 4.295 | 2.561 | 6.133 | 0.926 | 0.0001 | 0.0019 | n/a | True | True | True | ADEQUATE | size:V1; size:E6; size:E8; size:R4; size:R5; size:N4; size:N1 | DIAGNOSTIC (REDUNDANT given V2, E1, E3, X1) | role DIAGNOSTIC never seated |
| N3 | GUARD | MAY | 11.330 | 9.208 | 0.813 | 0.550 | 0.979 | 0.832 | 0.500 | 1.234 | -1.720 | 0.112 | 0.051 | n/a | False | False | False | NOT SEATABLE (< 3) |  | GUARDRAIL | role GUARD never seated |
| N2 | DIAGNOSTIC | MAY | 3.663 | 1.300 | 0.355 | 0.233 | 0.806 | 0.450 | 0.316 | 0.838 | -0.040 | 0.556 | 0.413 | n/a | False | False | False | NOT SEATABLE (< 3) |  | DIAGNOSTIC | role DIAGNOSTIC never seated |
| D1 | DIAGNOSTIC (investor outcome) | — | 1.441e+04 | 2.836e+06 | 196.804 | 137.082 | 263.747 | 48.380 | 31.038 | 71.233 | 0.899 | 0.0001 | 0.0016 | n/a | True | True | True | ADEQUATE |  | DIAGNOSTIC | role DIAGNOSTIC never seated |
| D2 | DIAGNOSTIC | — | 0.001637 | 0.133 | 81.327 | 54.459 | 102.800 | 39.768 | 27.022 | 57.382 | 0.696 | 0.0001 | 0.017 | n/a | True | True | False | ADEQUATE |  | DIAGNOSTIC | role DIAGNOSTIC never seated |
| E5 | OUTCOME (dead) | MUST | 0.000 | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | False | False | False | NOT GRADED |  | DEAD / constant / not computed | role OUTCOME (dead) never seated |
| R1 | GUARD | MAY | 0.000 | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | False | False | False | NOT GRADED |  | GUARDRAIL | role GUARD never seated |
| R3 | GUARD | MAY | 0.000 | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | False | False | False | NOT GRADED |  | GUARDRAIL | role GUARD never seated |

## 4. Pairs (directed; c later, p earlier in walk order; §8.6)

| pair | rho_raw | rho_raw_lo90 | rho_raw_hi90 | rho_resid | rho_resid_lo90 | rho_resid_hi90 | kendall_tau_b_raw | kendall_tau_b_resid | c_comp_resolvable | p_comp_resolvable | ESCAPE | BORDERLINE_PAIR | REDUNDANT_given_p | TRADE_OFF_size | TRADE_OFF_comp |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| V2|V1 | -0.867 | -0.918 | -0.790 | -0.115 | -0.368 | 0.155 | -0.700 | -0.064 | True | True | False | False | False | True | False |
| E1|V1 | -0.819 | -0.886 | -0.716 | -0.054 | -0.314 | 0.214 | -0.645 | -0.030 | True | True | False | False | False | True | False |
| E4|V1 | -0.965 | -0.979 | -0.942 | -0.240 | -0.474 | 0.027 | -0.849 | -0.135 | False | True | False | False | False | True | False |
| E6|V1 | 0.982 | 0.970 | 0.989 | 0.551 | 0.335 | 0.712 | 0.897 | 0.411 | False | True | False | False | True | False | False |
| E2|V1 | -0.773 | -0.857 | -0.650 | -0.046 | -0.307 | 0.221 | -0.587 | -0.025 | False | True | False | False | False | True | False |
| E3|V1 | -0.838 | -0.899 | -0.745 | -0.075 | -0.333 | 0.194 | -0.670 | -0.053 | True | True | False | False | False | True | False |
| X1|V1 | -0.896 | -0.936 | -0.834 | -0.137 | -0.387 | 0.133 | -0.738 | -0.082 | True | True | False | False | False | True | False |
| N4|V1 | 0.966 | 0.945 | 0.979 | 0.421 | 0.176 | 0.617 | 0.858 | 0.229 | False | True | False | False | True | False | False |
| N1|V1 | 0.950 | 0.919 | 0.970 | 0.253 | -0.012 | 0.485 | 0.817 | 0.200 | False | True | False | False | True | False | False |
| N5|V1 | -0.969 | -0.981 | -0.950 | -0.319 | -0.538 | -0.059 | -0.862 | -0.174 | True | True | False | False | False | True | False |
| E1|V2 | 0.992 | 0.987 | 0.995 | 0.988 | 0.979 | 0.993 | 0.941 | 0.924 | True | True | False | False | True | False | False |
| E4|V2 | 0.945 | 0.911 | 0.967 | 0.866 | 0.780 | 0.920 | 0.830 | 0.699 | False | True | False | False | True | False | False |
| E6|V2 | -0.789 | -0.867 | -0.673 | 0.603 | 0.403 | 0.748 | -0.605 | 0.426 | False | True | False | False | False | True | False |
| E2|V2 | 0.956 | 0.929 | 0.973 | 0.909 | 0.848 | 0.946 | 0.840 | 0.759 | False | True | False | False | True | False | False |
| E3|V2 | 0.987 | 0.979 | 0.992 | 0.976 | 0.960 | 0.986 | 0.927 | 0.883 | True | True | False | False | True | False | False |
| E8|V2 | -0.549 | -0.701 | -0.349 | -0.022 | -0.285 | 0.244 | -0.392 | -0.007092 | False | True | False | False | False | True | False |
| X1|V2 | 0.995 | 0.992 | 0.997 | 0.988 | 0.980 | 0.993 | 0.963 | 0.926 | True | True | False | False | True | False | False |
| R4|V2 | -0.789 | -0.867 | -0.673 | -0.335 | -0.551 | -0.077 | -0.597 | -0.223 | False | True | False | False | False | True | False |
| R5|V2 | -0.661 | -0.780 | -0.494 | -0.516 | -0.687 | -0.291 | -0.468 | -0.372 | False | True | False | False | False | True | False |
| N4|V2 | -0.944 | -0.966 | -0.908 | -0.841 | -0.905 | -0.742 | -0.828 | -0.651 | False | True | False | False | False | True | False |
| N1|V2 | -0.833 | -0.896 | -0.737 | -0.307 | -0.529 | -0.046 | -0.677 | -0.211 | False | True | False | False | False | True | False |
| N5|V2 | 0.948 | 0.916 | 0.969 | 0.874 | 0.792 | 0.925 | 0.832 | 0.706 | True | True | False | False | True | False | False |
| E4|E1 | 0.911 | 0.857 | 0.946 | 0.837 | 0.735 | 0.902 | 0.775 | 0.665 | False | True | False | False | True | False | False |
| E6|E1 | -0.732 | -0.829 | -0.592 | 0.656 | 0.473 | 0.784 | -0.550 | 0.459 | False | True | False | False | False | True | False |
| E2|E1 | 0.962 | 0.937 | 0.977 | 0.924 | 0.873 | 0.955 | 0.853 | 0.782 | False | True | False | False | True | False | False |
| E3|E1 | 0.991 | 0.985 | 0.995 | 0.972 | 0.953 | 0.984 | 0.940 | 0.871 | True | True | False | False | True | False | False |
| E8|E1 | -0.505 | -0.668 | -0.294 | 0.00152 | -0.263 | 0.266 | -0.362 | 0.012 | False | True | False | False | False | True | False |
| X1|E1 | 0.982 | 0.970 | 0.989 | 0.968 | 0.945 | 0.981 | 0.904 | 0.860 | True | True | False | False | True | False | False |
| R4|E1 | -0.761 | -0.849 | -0.633 | -0.335 | -0.551 | -0.077 | -0.577 | -0.229 | False | True | False | False | False | True | False |
| R5|E1 | -0.682 | -0.795 | -0.523 | -0.523 | -0.692 | -0.300 | -0.491 | -0.378 | False | True | False | False | False | True | False |
| N4|E1 | -0.909 | -0.944 | -0.854 | -0.805 | -0.882 | -0.687 | -0.770 | -0.610 | False | True | False | False | False | True | False |
| N1|E1 | -0.787 | -0.866 | -0.670 | -0.262 | -0.493 | 0.002633 | -0.626 | -0.170 | False | True | False | False | False | True | False |
| N5|E1 | 0.913 | 0.860 | 0.947 | 0.829 | 0.723 | 0.897 | 0.773 | 0.658 | True | True | False | False | True | False | False |
| E6|E4 | -0.928 | -0.956 | -0.883 | 0.358 | 0.103 | 0.569 | -0.764 | 0.266 | False | False | False | False | False | True | False |
| E2|E4 | 0.863 | 0.783 | 0.915 | 0.760 | 0.621 | 0.853 | 0.695 | 0.582 | False | False | False | False | True | False | False |
| E3|E4 | 0.927 | 0.881 | 0.955 | 0.852 | 0.758 | 0.911 | 0.803 | 0.681 | True | False | True | False | False | False | False |
| E8|E4 | -0.642 | -0.768 | -0.470 | -0.278 | -0.505 | -0.014 | -0.459 | -0.199 | False | False | False | False | False | True | False |
| X1|E4 | 0.965 | 0.943 | 0.979 | 0.888 | 0.814 | 0.933 | 0.867 | 0.730 | True | False | True | False | False | False | False |
| R4|E4 | -0.770 | -0.855 | -0.646 | -0.201 | -0.442 | 0.067 | -0.574 | -0.131 | False | False | False | False | False | True | False |
| R5|E4 | -0.528 | -0.686 | -0.323 | -0.309 | -0.530 | -0.048 | -0.358 | -0.220 | False | False | False | False | False | True | False |
| N4|E4 | -0.993 | -0.996 | -0.988 | -0.824 | -0.894 | -0.716 | -0.941 | -0.658 | False | False | False | False | False | True | False |
| N1|E4 | -0.936 | -0.961 | -0.896 | -0.393 | -0.596 | -0.144 | -0.791 | -0.236 | False | False | False | False | False | True | False |
| N5|E4 | 0.993 | 0.989 | 0.996 | 0.918 | 0.863 | 0.951 | 0.941 | 0.780 | True | False | True | False | False | False | False |
| E2|E6 | -0.681 | -0.794 | -0.522 | 0.604 | 0.403 | 0.749 | -0.498 | 0.411 | False | False | False | False | False | True | False |
| E3|E6 | -0.759 | -0.847 | -0.630 | 0.660 | 0.479 | 0.787 | -0.574 | 0.450 | True | False | False | False | False | True | False |
| X1|E6 | -0.825 | -0.891 | -0.726 | 0.559 | 0.346 | 0.718 | -0.642 | 0.401 | True | False | False | False | False | True | False |
| N4|E6 | 0.931 | 0.888 | 0.958 | -0.239 | -0.474 | 0.027 | 0.770 | -0.183 | False | False | False | False | True | False | False |
| N1|E6 | 0.957 | 0.929 | 0.974 | 0.064 | -0.205 | 0.323 | 0.824 | 0.051 | False | False | False | False | True | False | False |
| N5|E6 | -0.931 | -0.958 | -0.889 | 0.353 | 0.097 | 0.565 | -0.770 | 0.273 | True | False | False | False | False | True | False |
| E3|E2 | 0.926 | 0.880 | 0.955 | 0.842 | 0.743 | 0.905 | 0.793 | 0.670 | True | False | True | False | False | False | False |
| E8|E2 | -0.503 | -0.667 | -0.292 | -0.016 | -0.279 | 0.250 | -0.363 | -0.003546 | False | False | False | False | False | True | False |
| X1|E2 | 0.939 | 0.900 | 0.962 | 0.906 | 0.844 | 0.944 | 0.810 | 0.755 | True | False | True | False | False | False | False |
| R4|E2 | -0.780 | -0.861 | -0.660 | -0.366 | -0.575 | -0.112 | -0.569 | -0.252 | False | False | False | False | False | True | False |
| R5|E2 | -0.753 | -0.843 | -0.622 | -0.616 | -0.757 | -0.420 | -0.564 | -0.454 | False | False | False | False | False | True | False |
| N4|E2 | -0.864 | -0.916 | -0.785 | -0.722 | -0.828 | -0.565 | -0.697 | -0.544 | False | False | False | False | False | True | False |
| N1|E2 | -0.751 | -0.842 | -0.618 | -0.303 | -0.525 | -0.041 | -0.574 | -0.207 | False | False | False | False | False | True | False |
| N5|E2 | 0.867 | 0.789 | 0.918 | 0.770 | 0.634 | 0.859 | 0.707 | 0.592 | True | False | True | False | False | False | False |
| E8|E3 | -0.516 | -0.677 | -0.308 | -0.010 | -0.274 | 0.255 | -0.365 | 0.000 | False | True | False | False | False | True | False |
| X1|E3 | 0.985 | 0.975 | 0.991 | 0.957 | 0.928 | 0.975 | 0.918 | 0.840 | True | True | False | False | True | False | False |
| R4|E3 | -0.742 | -0.836 | -0.606 | -0.271 | -0.500 | -0.007302 | -0.563 | -0.184 | False | True | False | False | False | True | False |
| R5|E3 | -0.631 | -0.760 | -0.455 | -0.440 | -0.631 | -0.198 | -0.438 | -0.316 | False | True | False | False | False | True | False |
| N4|E3 | -0.921 | -0.951 | -0.872 | -0.814 | -0.888 | -0.700 | -0.791 | -0.612 | False | True | False | False | False | True | False |
| N1|E3 | -0.800 | -0.874 | -0.689 | -0.222 | -0.460 | 0.045 | -0.644 | -0.147 | False | True | False | False | False | True | False |
| N5|E3 | 0.925 | 0.878 | 0.954 | 0.856 | 0.764 | 0.913 | 0.794 | 0.677 | True | True | False | False | True | False | False |
| X1|E8 | -0.552 | -0.703 | -0.353 | -0.053 | -0.313 | 0.215 | -0.387 | -0.035 | True | False | False | False | False | True | False |
| N5|E8 | -0.616 | -0.749 | -0.435 | -0.214 | -0.453 | 0.053 | -0.447 | -0.138 | True | False | False | False | False | True | False |
| R4|X1 | -0.790 | -0.868 | -0.675 | -0.310 | -0.531 | -0.049 | -0.600 | -0.206 | False | True | False | False | False | True | False |
| R5|X1 | -0.636 | -0.763 | -0.461 | -0.505 | -0.679 | -0.277 | -0.445 | -0.379 | False | True | False | False | False | True | False |
| N4|X1 | -0.962 | -0.977 | -0.938 | -0.854 | -0.912 | -0.761 | -0.862 | -0.679 | False | True | False | False | False | True | False |
| N1|X1 | -0.858 | -0.912 | -0.776 | -0.347 | -0.560 | -0.091 | -0.707 | -0.250 | False | True | False | False | False | True | False |
| N5|X1 | 0.966 | 0.944 | 0.979 | 0.892 | 0.821 | 0.936 | 0.869 | 0.723 | True | True | False | False | True | False | False |
| N5|R4 | -0.789 | -0.867 | -0.673 | -0.286 | -0.512 | -0.023 | -0.597 | -0.202 | True | False | False | False | False | True | False |
| N5|R5 | -0.556 | -0.706 | -0.357 | -0.450 | -0.638 | -0.210 | -0.388 | -0.333 | True | False | False | False | False | True | False |
| N1|N4 | 0.950 | 0.918 | 0.969 | 0.394 | 0.144 | 0.597 | 0.821 | 0.248 | False | False | False | False | True | False | False |
| N5|N4 | -0.995 | -0.997 | -0.991 | -0.910 | -0.947 | -0.850 | -0.954 | -0.757 | True | False | False | False | False | True | False |
| N5|N1 | -0.938 | -0.962 | -0.899 | -0.397 | -0.599 | -0.148 | -0.803 | -0.232 | True | False | False | False | False | True | False |

Key pairs (90 % intervals):

- N4|V1: raw 0.966 [0.945, 0.979]; residual 0.421 [0.176, 0.617]; τ_b raw 0.858 / resid 0.229; ESCAPE False; BORDERLINE-PAIR False; REDUNDANT given p True; TRADE-OFF False
- N1|V1: raw 0.950 [0.919, 0.970]; residual 0.253 [-0.012, 0.485]; τ_b raw 0.817 / resid 0.200; ESCAPE False; BORDERLINE-PAIR False; REDUNDANT given p True; TRADE-OFF False
- N1|N4: raw 0.950 [0.918, 0.969]; residual 0.394 [0.144, 0.597]; τ_b raw 0.821 / resid 0.248; ESCAPE False; BORDERLINE-PAIR False; REDUNDANT given p True; TRADE-OFF False
- N4|E1: raw -0.909 [-0.944, -0.854]; residual -0.805 [-0.882, -0.687]; τ_b raw -0.770 / resid -0.610; ESCAPE False; BORDERLINE-PAIR False; REDUNDANT given p False; TRADE-OFF True
- X1|E1: raw 0.982 [0.970, 0.989]; residual 0.968 [0.945, 0.981]; τ_b raw 0.904 / resid 0.860; ESCAPE False; BORDERLINE-PAIR False; REDUNDANT given p True; TRADE-OFF False
- E1|V1: raw -0.819 [-0.886, -0.716]; residual -0.054 [-0.314, 0.214]; τ_b raw -0.645 / resid -0.030; ESCAPE False; BORDERLINE-PAIR False; REDUNDANT given p False; TRADE-OFF True

§4b evaluations:

- none evaluated

## 5. Trade-offs (item 5)

- V1: size:V2; size:E1; size:E4; size:E2; size:E3; size:X1; size:N5
- E1: size:V1; size:E6; size:E8; size:R4; size:R5; size:N4; size:N1
- X1: size:V1; size:E6; size:E8; size:R4; size:R5; size:N4; size:N1
- N4: size:V2; size:E1; size:E4; size:E2; size:E3; size:X1; size:N5

## 6. δ-error (§8.12; F = {V1, E1, X1, N4}, bar units; reported, never selecting)

- v2 V1·E1: V1: π 0.808 [0.752, 0.860], δ 124.60 (p90 124.60), comparable 1128; E1: π 0.744 [0.679, 0.800], δ 27.39 (p90 27.39), comparable 1128
- v1 pre-registered V1·E1·N1: V1: π 0.246 [0.141, 0.358], δ 29.58 (p90 29.58), comparable 211; E1: π 0.775 [0.707, 0.834], δ 27.39 (p90 27.39), comparable 1025; N1: π 0.000 [0.000, 0.000], δ 0.68 (p90 0.68), comparable 200
- swap V1->X1: X1·E1: X1: π 0.008 [0.002, 0.015], δ 3.48 (p90 3.48), comparable 1128; E1: π 0.004 [0.000, 0.008], δ 3.01 (p90 3.01), comparable 1128
- swap V1->N4: N4·E1: N4: π 0.762 [0.694, 0.817], δ 25.68 (p90 25.68), comparable 1128; E1: π 0.801 [0.746, 0.849], δ 27.39 (p90 27.39), comparable 1128
- swap E1->X1: V1·X1: V1: π 0.853 [0.810, 0.892], δ 124.60 (p90 124.60), comparable 1128; X1: π 0.804 [0.746, 0.856], δ 39.96 (p90 39.96), comparable 1128
- swap E1->N4: V1·N4: V1: π 0.060 [0.037, 0.083], δ 20.96 (p90 20.96), comparable 1128; N4: π 0.020 [0.005, 0.034], δ 4.25 (p90 4.25), comparable 1128

## 7. The walk (§8.7)

- V (MAY): **V1** — SEATED
- E (MUST): **E1** — SEATED
- X (MAY): **EMPTY** — not at stake in this box
- R (MAY): **EMPTY** — not at stake in this box
- N (MAY): **EMPTY** — not at stake in this box

M = 2 — M != 4: ref point, τ and gate numbers re-derived (item 8).

Matches the §3 prediction V1 · E1 · N4: **False** — §8.14: outputs stay UNCOMMITTED; STOP.

## 8. Three vectors from the same runs (+ v1 seat lines)

- v1 pre-registered (d706199): V: V1 · E: E1 · X: EMPTY · R: EMPTY · N: N1
- v1 Seed-bar re-grade (baf77c3): V: V1 · E: E1 · X: EMPTY · R: EMPTY · N: N1
- v2 (this read): V: V1 · E: E1 · X: EMPTY · R: EMPTY · N: EMPTY
- v2 with borderline → REDUNDANT (no §4b): V: V1 · E: E1 · X: EMPTY · R: EMPTY · N: EMPTY
- pre-registered vector V1 · E1 · N1 co-reported at every station (§2.5).

## 9. N1_off guardrail (§8.8; monitor, never halts)

- B_N1off = 231.3 line-h (s 54.5, ν 22; 2·B = 462.7; v1-memo value 242.1); B_N3off = 42.1 MWh (anchor + 4 Seeds (nu 16)); base N1_off 30750, base N3_off 61477.
- ΔN1_off range -49 … 378; leakage median 0.279 (finding, not a violation).
- Flags: {'a_dN1off_ge_2B': False, 'b_new_bottleneck': False, 'c_N3off_ge_base_plus_2B': False}.
- Top-3 non-pocket lines by max Δhours (max, median): L247 (603, 342); L188 (408, 338); L1 (314, 245)
- N4 == N4_L252 on every row: True.

## 10. Reporting lens

E1 − 40·D1 is a reporting column only: Δnet ≤ 0 by construction (replacement ≈ $24/MWh < B = $40) and it falls monotonically with MW; capex excluded. Lens IDR 7.835e+07 $; Spearman with E1 -0.850. Per design: `pool_lens_v2.csv`.

## Deviations

- Zero-bar set (computed, not asserted): ['E5', 'R1', 'R3'].
- Sources disagreeing > 2x under the §8.1 recipe (disclosed, never switched): V3 (5.83), E9 (nan), D1 (2.97); N1 ratio 1.93 (63 A3, on its sigma_pert estimator: DISAGREE).
- §8.11: the $40-offer assert reads n0_E:25 gen_summary directly (real run only; disclosed); synthetic runs assert on base_v3 only.
- N4 floor = 1 % of 8,760 h = 87.6 h (rule text rounds to 88 h).
- B_N3off Seed source: anchor + 4 Seeds (nu 16).
- IDR / Mantel statistics computed for all non-constant ids.

## Governance note (added by hand at commit; Kay, 2026-11-24)

The walk gave V1 · E1 (M = 2), not the §3 prediction V1 · E1 · N4. §8.14 says the outputs stay uncommitted in that case. Kay overrode that clause for this read: commit the rule's actual output, never tuned and never re-run with other thresholds, and write the dated design space with the actual seats. The rule, thresholds and code are unchanged since commit (ii) b8a3285. Why N4 is not seated: its residual Mantel p is 0.0253 > 0.01, so it is not COMPOSITION-RESOLVABLE. It therefore has no ESCAPE from REDUNDANT given the seated V1 (raw ρ 0.966). The pair is not a BORDERLINE-PAIR, so §4b was never evaluated.
