# SCREENING_V3 — 16-site matched-MW screening under identity v3 (prompt 62 Part C §4.5)

Generated 2026-11-18 by `analysis/pool/screening_v3_landing.py` at `11e9ddf`. Rules: prompt 62 v1.1 §4.5, committed verbatim with the wave (`waves/screening_v3/README.md`, `c986da0`) before any screening_v3 Y existed. **E-D3 is not reopened; no seat changes.**

## 0. Headline

- **LOCATIONAL ids (Holm ≤ 0.05, |HL| ≥ 2 B_j, Moses interval excludes 0):** V1 (HL/B -33.12, Holm p 0.0357), E1 (HL/B -8.73, Holm p 0.0357), N4 (HL/B -2.69, Holm p 0.0466), N5 (HL/B +4.33, Holm p 0.0357), E6 (HL/B +10.31, Holm p 0.0357), E3 (HL/B -4.59, Holm p 0.0357), V3 (HL/B -60.82, Holm p 0.0357) — of 23 graded ids.
- **Seated objectives:** V1 HL/B -33.12, exact p 0.00155, Holm p 0.0357 → LOCATIONAL; E1 HL/B -8.73, exact p 0.00155, Holm p 0.0357 → LOCATIONAL; N1 HL/B -3.00, exact p 0.0932, Holm p 0.653 → NOT LOCATIONAL; N4 HL/B -2.69, exact p 0.00311, Holm p 0.0466 → LOCATIONAL.
- **Matched-MW ranking:** v3 top 6 = 270, 275, 274, 110, 140, 146 on buses [2, 75, 120] → **SLATE BUS-SET HOLDS**; entered ['275'], left ['163']; TIED (within B_V1/180 = 89.9 MWh/MW of the boundary): none (closest: 146 +1.011 bands, 163 -1.011 bands). Prediction (275 in, 163 out, bus set holds): 275 in ✓, 163 out ✓, bus set ✓. Kendall τ_b(v2, v3) = 0.667 (exact p 0.000135).
- **Dominance on V1/E1/N1:** 2 of 10 non-slate sites NOT dominated: 116 (beats the closest slate site by 0.72 B on its best objective), 91 (beats the closest slate site by 0.44 B on its best objective) → disclosed, PI flag; E-D3 not reopened.
- **Dominance on V1/E1/N4:** 1 of 10 non-slate sites NOT dominated: 116 (beats the closest slate site by 0.72 B on its best objective) → disclosed, PI flag; E-D3 not reopened.
- **N1 against both bars** (63: perturbation ruler DISAGREES with Seed chatter, so B_N1^seed binds): HL = -345 line-h → -3.00 B_pert (B = 114.9) / -1.43 B_seed (B = 242.1); Holm p 0.653 → NOT LOCATIONAL under both (NOT LOCATIONAL under B_seed).
- **Seed-bar sensitivity (every id, `verdict_B_seed`):** no verdict changes.
- **E1 per site vs G_site + G_base:** WITHIN GAP BOUND 16.
- **Replicate:** `screening_v3:11` overall.csv md5 = `location_oat_v2:3` (`dc5b00da713b1c09efe8f65b3728aa34`) — no code/data drift since 11-06. SUSPECT rows: 0 of 16 (+ base ok); identity v3 on all 17 runs + base.

## 1. Disclosures

- PV/WIND confound: C holds one PV site (116); pv_pocket (30, 59, 142) is outside the primary contrast; far is all WIND. The WIND-only sensitivity (7 vs 5) is in §2.
- ω confound: ω = 180/gen_pmax spans 0.10–0.97; 116 (0.90) and 163 (0.97) are saturation rows; own-site relief at high ω is partly accounting reclassification (§4).
- Power floor: with 8 vs 5 the smallest exact two-sided p is 0.00155 (complete separation); Holm over 23 ids needs ≤ 0.00217 at its first step, so a LOCATIONAL read needs complete or near-complete separation of the 8 C sites from the 5 far sites.
- Moses exact interval: k = 8, achieved coverage 0.9549 (8 vs 5); WIND-only k = 7, coverage 0.9520. scipy's exact MW null assumes no ties; tied C-U pairs are counted per id (`n_tied_pairs`).
- B_j transferred from noise_v3 (61 §3, D2 structural zeros excluded); no replicate chatter is measured here. No ratio for any j is graded; V1 relief/MW is reported as a column.
- D2 (PEM utilization, a diagnostic) is not graded: base_v3 has no PEM, so D2 is 0/0 there and Δ_D2 is undefined; the Holm family is the other 23 ids with B_j > 0.
- Second bar: `analysis/noise_v3/ercot_noise_seed.json` (63, Gurobi-Seed chatter) gives B_seed per id; its B_pert is asserted equal to B_j. Dominance is invariant to per-objective bar scaling (only `margin_bars` uses B_j).
- Covariate Spearman ρ and the Kruskal–Wallis test are descriptive (no multiplicity correction).

## 2. Tier contrast per graded id (d_s = Δ_j vs base_v3; C = pocket_120 ∪ wind_near, U = far)

| id | family | B_j | median_pocket_120 | median_wind_near | median_pv_pocket | median_far | HL | HL_over_B | moses_lo | moses_hi | r_rb | p_exact | p_holm | n_tied_pairs | verdict | wind_HL_over_B | wind_p_exact | kw_p | B_seed | HL_over_B_seed | verdict_B_seed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| V1 | V | 16,173.058 | -6.34e+05 | -5.54e+05 | -2.41e+05 | -18,307.330 | -5.36e+05 | -33.117 | -6.17e+05 | -4.24e+05 | -1.000 | 0.00155 | 0.0357 | 0 | LOCATIONAL | -33.587 | 0.00253 | 0.00541 | 18,566.797 | -28.847 | LOCATIONAL |
| E1 | E | 2.38e+06 | 1.2e+07 | 1.15e+07 | 1.35e+07 | 3.29e+07 | -2.08e+07 | -8.726 | -2.58e+07 | -1.57e+07 | -1.000 | 0.00155 | 0.0357 | 0 | LOCATIONAL | -8.638 | 0.00253 | 0.0127 | 1.33e+06 | -15.688 | LOCATIONAL |
| X1 | X | 36,454.153 | 4.49e+05 | 3.95e+05 | 2.47e+05 | 6.29e+05 | -2.22e+05 | -6.084 | -4.47e+05 | -1.01e+05 | -0.750 | 0.0295 | 0.295 | 0 | NOT LOCATIONAL | -5.471 | 0.048 | 0.0548 | 39,567.526 | -5.606 | NOT LOCATIONAL |
| R4 | R | 146.653 | -184.000 | -132.000 | -122.000 | -290.000 | 136.500 | 0.931 | 28.000 | 314.000 | 0.700 | 0.0451 | 0.406 | 0 | NOT LOCATIONAL | 0.805 | 0.0732 | 0.16 | 276.140 | 0.494 | NOT LOCATIONAL |
| N1 | N | 114.924 | -43.000 | 19.000 | -28.000 | 308.000 | -345.000 | -3.002 | -552.000 | 50.000 | -0.600 | 0.0932 | 0.653 | 0 | NOT LOCATIONAL | -3.019 | 0.106 | 0.2 | 242.083 | -1.425 | NOT LOCATIONAL |
| E4 | E | 8.51e+06 | 1.67e+07 | 9.95e+06 | 1.62e+07 | 8.74e+06 | -1.03e+06 | -0.121 | -8.07e+06 | 8.03e+06 | -0.050 | 0.943 | 1 | 0 | NOT LOCATIONAL | 0.153 | 0.876 | 0.971 | 1.01e+07 | -0.102 | NOT LOCATIONAL |
| R2 | R | 102.295 | -40.072 | -52.176 | -7.741 | 15.675 | -62.442 | -0.610 | -122.987 | -17.076 | -0.800 | 0.0186 | 0.224 | 0 | NOT LOCATIONAL | -0.664 | 0.0101 | 0.132 | 102.736 | -0.608 | NOT LOCATIONAL |
| R7 | R | 2.69e+05 | 1.69e+05 | 1.99e+05 | 93,618.200 | 4.51e+05 | -2.55e+05 | -0.949 | -4.61e+05 | -90,794.800 | -0.700 | 0.0451 | 0.406 | 0 | NOT LOCATIONAL | -0.915 | 0.0732 | 0.123 | 2.84e+05 | -0.898 | NOT LOCATIONAL |
| N4 | N | 36.966 | -145.000 | -160.000 | -27.000 | -44.000 | -99.500 | -2.692 | -128.000 | -37.000 | -0.950 | 0.00311 | 0.0466 | 0 | LOCATIONAL | -3.003 | 0.00253 | 0.00713 | 44.512 | -2.235 | LOCATIONAL |
| N5 | N | 0.183 | 0.818 | 0.646 | -0.052 | -0.135 | 0.791 | 4.330 | 0.492 | 0.954 | 1.000 | 0.00155 | 0.0357 | 0 | LOCATIONAL | 4.533 | 0.00253 | 0.00718 | 0.191 | 4.146 | LOCATIONAL |
| E6 | E | 2.91e+06 | 5.88e+06 | 5.48e+06 | 8.28e+06 | -2.45e+07 | 3e+07 | 10.305 | 1.62e+07 | 3.15e+07 | 1.000 | 0.00155 | 0.0357 | 0 | LOCATIONAL | 10.295 | 0.00253 | 0.0183 | 1.74e+06 | 17.202 | LOCATIONAL |
| R5 | R | 16,620.630 | 5,984.520 | 2,786.280 | 3,439.050 | -6,296.970 | 9,710.590 | 0.584 | 4,375.590 | 14,674.320 | 0.900 | 0.00622 | 0.087 | 0 | NOT LOCATIONAL | 0.557 | 0.0101 | 0.02 | 12,365.100 | 0.785 | NOT LOCATIONAL |
| N3 | N | 13.974 | -0.440 | 0.202 | 2.519 | 1.640 | -0.892 | -0.064 | -2.503 | 2.843 | -0.050 | 0.943 | 1 | 0 | NOT LOCATIONAL | -0.104 | 0.755 | 0.231 | 10.474 | -0.085 | NOT LOCATIONAL |
| E2 | E | 2.9e+06 | -4.09e+05 | 6.77e+05 | 7.48e+05 | 4.54e+06 | -4.56e+06 | -1.572 | -5.56e+06 | -3.56e+06 | -1.000 | 0.00155 | 0.0357 | 0 | NOT LOCATIONAL | -1.566 | 0.00253 | 0.0107 | 3.64e+06 | -1.253 | NOT LOCATIONAL |
| R6 | R | 1.03e+05 | -55,991.780 | -8,647.315 | -81,442.860 | -95,794.857 | 78,653.228 | 0.761 | 24,243.888 | 1.58e+05 | 0.800 | 0.0186 | 0.224 | 0 | NOT LOCATIONAL | 0.827 | 0.0303 | 0.1 | 92,856.632 | 0.847 | NOT LOCATIONAL |
| N2 | N | 3.000 | -1.000 | 0.000 | 1.000 | 1.000 | -1.000 | -0.333 | -2.000 | 1.000 | -0.400 | 0.284 | 1 | 6 | NOT LOCATIONAL | -0.333 | 0.432 | 0.243 | 3.735 | -0.268 | NOT LOCATIONAL |
| E3 | E | 3.47e+06 | 1.3e+07 | 1.16e+07 | 1.25e+07 | 2.83e+07 | -1.59e+07 | -4.587 | -2.05e+07 | -1.19e+07 | -1.000 | 0.00155 | 0.0357 | 0 | LOCATIONAL | -4.412 | 0.00253 | 0.0183 | 3.57e+06 | -4.461 | LOCATIONAL |
| R8 | R | 1,543.306 | 1,007.000 | 848.000 | 1,051.000 | 1,604.000 | -613.000 | -0.397 | -1,144.000 | 2.000 | -0.600 | 0.0932 | 0.653 | 0 | NOT LOCATIONAL | -0.391 | 0.149 | 0.264 | 1,378.905 | -0.445 | NOT LOCATIONAL |
| E7 | E | 0.017 | 0.070 | 0.060 | 0.051 | 0.047 | 0.014 | 0.826 | -0.022 | 0.026 | 0.200 | 0.622 | 1 | 0 | NOT LOCATIONAL | 0.972 | 0.343 | 0.695 | 0.014 | 0.965 | NOT LOCATIONAL |
| E8 | E | 0.302 | 0.108 | 0.214 | -0.213 | -0.157 | 0.311 | 1.029 | 0.194 | 0.397 | 1.000 | 0.00155 | 0.0357 | 0 | NOT LOCATIONAL | 1.059 | 0.00253 | 0.0377 | 0.291 | 1.068 | NOT LOCATIONAL |
| V2 | V | 0.004 | -0.143 | -0.129 | -0.106 | -0.266 | 0.134 | 32.611 | 0.095 | 0.211 | 0.900 | 0.00622 | 0.087 | 0 | NOT LOCATIONAL | 31.779 | 0.0101 | 0.0296 | 0.008 | 17.432 | NOT LOCATIONAL |
| V3 | V | 3.1e-05 | 0.000625 | 0.000661 | 0.000693 | 0.002 | -0.002 | -60.816 | -0.007 | -0.001 | -1.000 | 0.00155 | 0.0357 | 0 | LOCATIONAL | -58.153 | 0.00253 | 0.0195 | 0.000192 | -9.805 | LOCATIONAL |
| D1 | D | 4,358.402 | 1.19e+06 | 1.04e+06 | 6.2e+05 | 1.06e+06 | 27,735.619 | 6.364 | -3.13e+05 | 2.33e+05 | 0.050 | 0.943 | 1 | 0 | NOT LOCATIONAL | 21.651 | 0.639 | 0.309 | 15,885.151 | 1.746 | NOT LOCATIONAL |

`why_not` per id is in `screening_v3_locational.csv`.

## 3. Sites (Δ vs base_v3 at 180 MW; z = Δ/B_j)

| site | key | tier | unit_type | bus | omega_180 | relief_per_mw | z_V1 | z_E1 | z_N1 | z_N4 | d_E1 | E1_gap_bound | E1_verdict | suspect |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 20 | screening_v3:10 | far | WIND | 32 | 0.231 | 60.435 | -0.673 | 8.243 | 5.412 | -0.893 | 1.96e+07 | 3.95e+07 | WITHIN GAP BOUND | no |
| 204 | screening_v3:9 | far | WIND | 28 | 0.210 | 60.124 | -0.669 | 14.307 | 2.680 | -0.866 | 3.41e+07 | 3.92e+07 | WITHIN GAP BOUND | no |
| 205 | screening_v3:7 | far | WIND | 77 | 0.170 | 101.707 | -1.132 | 14.674 | 4.081 | -1.190 | 3.5e+07 | 4e+07 | WITHIN GAP BOUND | no |
| 206 | screening_v3:8 | far | WIND | 22 | 0.100 | 127.543 | -1.420 | 13.793 | 2.471 | -1.353 | 3.29e+07 | 4.13e+07 | WITHIN GAP BOUND | no |
| 91 | screening_v3:6 | far | WIND | 94 | 0.229 | 721.625 | -8.031 | 12.865 | -0.983 | -1.731 | 3.07e+07 | 3.99e+07 | WITHIN GAP BOUND | no |
| 116 | screening_v3:2 | pocket_120 | PV | 120 | 0.903 | 1,479.575 | -16.467 | 1.309 | 0.479 | -1.623 | 3.12e+06 | 3.91e+07 | WITHIN GAP BOUND | no |
| 163 | location_oat_v2:3 | pocket_120 | WIND | 120 | 0.971 | 2,945.043 | -32.777 | 2.034 | 0.000 | -2.191 | 4.85e+06 | 3.87e+07 | WITHIN GAP BOUND | no |
| 270 | location_oat_v2:12 | pocket_120 | WIND | 120 | 0.311 | 3,535.924 | -39.353 | 5.042 | -0.548 | -4.382 | 1.2e+07 | 3.85e+07 | WITHIN GAP BOUND | no |
| 274 | location_oat_v2:18 | pocket_120 | WIND | 120 | 0.241 | 3,524.930 | -39.231 | 5.899 | -0.513 | -4.950 | 1.41e+07 | 3.93e+07 | WITHIN GAP BOUND | no |
| 275 | screening_v3:1 | pocket_120 | WIND | 120 | 0.173 | 3,529.999 | -39.288 | 6.297 | -0.374 | -3.923 | 1.5e+07 | 3.96e+07 | WITHIN GAP BOUND | no |
| 142 | screening_v3:5 | pv_pocket | PV | 14 | 0.256 | 960.615 | -10.691 | 6.111 | 0.183 | -0.757 | 1.46e+07 | 4.1e+07 | WITHIN GAP BOUND | no |
| 30 | screening_v3:4 | pv_pocket | PV | 26 | 0.194 | 1,358.803 | -15.123 | 5.670 | -0.322 | -0.730 | 1.35e+07 | 4.03e+07 | WITHIN GAP BOUND | no |
| 59 | screening_v3:3 | pv_pocket | PV | 26 | 0.366 | 1,339.459 | -14.908 | 5.193 | -0.244 | -0.406 | 1.24e+07 | 4.17e+07 | WITHIN GAP BOUND | no |
| 110 | location_oat_v2:15 | wind_near | WIND | 2 | 0.532 | 3,221.095 | -35.850 | 5.155 | -0.165 | -4.355 | 1.23e+07 | 3.88e+07 | WITHIN GAP BOUND | no |
| 140 | location_oat_v2:6 | wind_near | WIND | 2 | 0.718 | 3,078.263 | -34.260 | 4.164 | 0.165 | -3.300 | 9.92e+06 | 3.92e+07 | WITHIN GAP BOUND | no |
| 146 | location_oat_v2:9 | wind_near | WIND | 75 | 0.672 | 3,035.840 | -33.788 | 4.822 | 0.609 | -4.328 | 1.15e+07 | 3.71e+07 | WITHIN GAP BOUND | no |

## 4. ΔV1 decomposition (own-site parent row vs other sites; gen_summary)

| site | omega_180 | relief_V1_mwh | own_dV1 | other_dV1 | own_share_of_relief | twin_curtailment_mwh |
|---|---|---|---|---|---|---|
| 270 | 0.311 | 6.36e+05 | -3.8e+05 | -2.57e+05 | 0.597 | 1.19e+06 |
| 275 | 0.173 | 6.35e+05 | -4.23e+05 | -2.12e+05 | 0.666 | 1.29e+06 |
| 274 | 0.241 | 6.34e+05 | -2.61e+05 | -3.73e+05 | 0.412 | 1.24e+06 |
| 110 | 0.532 | 5.8e+05 | 99,680.816 | -6.79e+05 | -0.172 | 1.08e+06 |
| 140 | 0.718 | 5.54e+05 | -12,990.365 | -5.41e+05 | 0.023 | 9.78e+05 |
| 146 | 0.672 | 5.46e+05 | 71,730.931 | -6.18e+05 | -0.131 | 1.04e+06 |
| 163 | 0.971 | 5.3e+05 | -4.32e+05 | -98,570.373 | 0.814 | 7.33e+05 |
| 116 | 0.903 | 2.66e+05 | -1.95e+05 | -71,024.256 | 0.733 | 4.04e+05 |
| 30 | 0.194 | 2.45e+05 | 30,623.011 | -2.75e+05 | -0.125 | 6.51e+05 |
| 59 | 0.366 | 2.41e+05 | -63,751.160 | -1.77e+05 | 0.264 | 6.06e+05 |
| 142 | 0.256 | 1.73e+05 | 0.000 | -1.73e+05 | -0.000 | 6.2e+05 |
| 91 | 0.229 | 1.3e+05 | 139.678 | -1.3e+05 | -0.001 | 1.14e+06 |
| 206 | 0.100 | 22,957.764 | 386.225 | -23,343.988 | -0.017 | 1.05e+06 |
| 205 | 0.170 | 18,307.330 | 0.000 | -18,307.330 | -0.000 | 1.09e+06 |
| 20 | 0.231 | 10,878.250 | 0.000 | -10,878.250 | -0.000 | 5.84e+05 |
| 204 | 0.210 | 10,822.363 | 0.000 | -10,822.363 | -0.000 | 1.06e+06 |

own_dV1 = Δ curtailment of the parent `<site>` row (its capacity shrinks by 180 MW); the `<site>_PEM` twin is is_pem = True and never in V1 (asserted). A large own share at high ω means the relief is mostly the twin's capacity leaving V1's books (accounting reclassification), not system-wide relief.

## 5. Covariates (Spearman over the 16 sites; descriptive)

| id | H_C_180_MWh | base_v3_own_curtailment_mwh | omega_180 | max|rho| pocket PTDF | max|rho| other congested PTDF |
|---|---|---|---|---|---|
| E1 | 0.494 | -0.597 | -0.900 | 0.729 | -0.729 |
| N1 | -0.224 | -0.689 | -0.100 | 0.483 | 0.586 |
| N4 | -0.553 | -0.640 | -0.303 | 0.817 | -0.805 |
| V1 | -0.232 | -0.883 | -0.426 | 0.879 | 0.879 |

Full table (23 ids × 47 covariates): `screening_v3_covariate_rho.csv`.

## 6. Matched-MW ranking vs E-D3 slate

| site | rank_v3 | rank_v2 | relief_per_mw_v3 | relief_per_mw_v2 | bus | unit_type | omega_180 | slate | top6_v3 | TIED | gap_to_boundary_bands |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 270 | 1 | 4 | 3,535.924 | 3,567.814 | 120 | WIND | 0.311 | yes | yes | no | 6.576 |
| 275 | 2 | 7 | 3,529.999 | 3,414.195 | 120 | WIND | 0.173 | no | yes | no | 6.510 |
| 274 | 3 | 6 | 3,524.930 | 3,500.878 | 120 | WIND | 0.241 | yes | yes | no | 6.454 |
| 110 | 4 | 5 | 3,221.095 | 3,501.994 | 2 | WIND | 0.532 | yes | yes | no | 3.072 |
| 140 | 5 | 2 | 3,078.263 | 3,630.479 | 2 | WIND | 0.718 | yes | yes | no | 1.483 |
| 146 | 6 | 3 | 3,035.840 | 3,587.156 | 75 | WIND | 0.672 | yes | yes | no | 1.011 |
| 163 | 7 | 1 | 2,945.043 | 3,841.170 | 120 | WIND | 0.971 | yes | no | no | -1.011 |
| 116 | 8 | 8 | 1,479.575 | 2,418.168 | 120 | PV | 0.903 | no | no | no | -17.321 |
| 30 | 9 | 10 | 1,358.803 | 1,274.456 | 26 | PV | 0.194 | no | no | no | -18.665 |
| 59 | 10 | 9 | 1,339.459 | 1,591.034 | 26 | PV | 0.366 | no | no | no | -18.880 |
| 142 | 11 | 11 | 960.615 | 1,126.761 | 14 | PV | 0.256 | no | no | no | -23.096 |
| 91 | 12 | 12 | 721.625 | 713.121 | 94 | WIND | 0.229 | no | no | no | -25.756 |
| 206 | 13 | 14 | 127.543 | 118.960 | 22 | WIND | 0.100 | no | no | no | -32.368 |
| 205 | 14 | 13 | 101.707 | 124.154 | 77 | WIND | 0.170 | no | no | no | -32.656 |
| 20 | 15 | 16 | 60.435 | 82.946 | 32 | WIND | 0.231 | no | no | no | -33.115 |
| 204 | 16 | 15 | 60.124 | 105.499 | 28 | WIND | 0.210 | no | no | no | -33.119 |

v2 ranks are at ω ≈ 0.5 (pem = gen_pmax/2), v3 at a matched 180 MW, so a different order is expected from the protocol alone. Tie band B_V1/180 = 89.9 MWh/MW. E-D3 stands in every case.

## 7. Dominance read (non-slate sites; z = Δ/B_j, all dir = min)

| objectives | site | dominated | dominated_by | margin_bars | z_V1 | z_E1 | z_N1 | z_N4 |
|---|---|---|---|---|---|---|---|---|
| V1/E1/N1 | 275 | yes | 270 | n/a | -39.288 | 6.297 | -0.374 | n/a |
| V1/E1/N1 | 116 | no |  | 0.725 | -16.467 | 1.309 | 0.479 | n/a |
| V1/E1/N1 | 59 | yes | 270 | n/a | -14.908 | 5.193 | -0.244 | n/a |
| V1/E1/N1 | 30 | yes | 270 | n/a | -15.123 | 5.670 | -0.322 | n/a |
| V1/E1/N1 | 142 | yes | 163;140;270;110;274 | n/a | -10.691 | 6.111 | 0.183 | n/a |
| V1/E1/N1 | 91 | no |  | 0.435 | -8.031 | 12.865 | -0.983 | n/a |
| V1/E1/N1 | 205 | yes | 163;140;146;270;110;274 | n/a | -1.132 | 14.674 | 4.081 | n/a |
| V1/E1/N1 | 206 | yes | 163;140;146;270;110;274 | n/a | -1.420 | 13.793 | 2.471 | n/a |
| V1/E1/N1 | 204 | yes | 163;140;146;270;110;274 | n/a | -0.669 | 14.307 | 2.680 | n/a |
| V1/E1/N1 | 20 | yes | 163;140;146;270;110;274 | n/a | -0.673 | 8.243 | 5.412 | n/a |
| V1/E1/N4 | 275 | yes | 270 | n/a | -39.288 | 6.297 | n/a | -3.923 |
| V1/E1/N4 | 116 | no |  | 0.725 | -16.467 | 1.309 | n/a | -1.623 |
| V1/E1/N4 | 59 | yes | 163;140;146;270;110 | n/a | -14.908 | 5.193 | n/a | -0.406 |
| V1/E1/N4 | 30 | yes | 163;140;146;270;110 | n/a | -15.123 | 5.670 | n/a | -0.730 |
| V1/E1/N4 | 142 | yes | 163;140;146;270;110;274 | n/a | -10.691 | 6.111 | n/a | -0.757 |
| V1/E1/N4 | 91 | yes | 163;140;146;270;110;274 | n/a | -8.031 | 12.865 | n/a | -1.731 |
| V1/E1/N4 | 205 | yes | 163;140;146;270;110;274 | n/a | -1.132 | 14.674 | n/a | -1.190 |
| V1/E1/N4 | 206 | yes | 163;140;146;270;110;274 | n/a | -1.420 | 13.793 | n/a | -1.353 |
| V1/E1/N4 | 204 | yes | 163;140;146;270;110;274 | n/a | -0.669 | 14.307 | n/a | -0.866 |
| V1/E1/N4 | 20 | yes | 163;140;146;270;110;274 | n/a | -0.673 | 8.243 | n/a | -0.893 |

## 8. Provenance

- Rows: 163=location_oat_v2:3, 140=location_oat_v2:6, 146=location_oat_v2:9, 270=location_oat_v2:12, 110=location_oat_v2:15, 274=location_oat_v2:18, 275=screening_v3:1, 116=screening_v3:2, 59=screening_v3:3, 30=screening_v3:4, 142=screening_v3:5, 91=screening_v3:6, 205=screening_v3:7, 206=screening_v3:8, 204=screening_v3:9, 20=screening_v3:10; base `base_v3:1` (G_base = 1.87e+07 $).
- Seen: screening_v3 rows 1–11, wave D L180 rows 3/6/9/12/15/18, base_v3:1, ercot_noise.json, ercot_noise_seed.json, the committed Part B outputs. Not read: random_E, methods_E, any n0_E extract.
