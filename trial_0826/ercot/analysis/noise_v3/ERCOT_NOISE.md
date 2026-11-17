# ERCOT_NOISE — noise_v3 reading (prompt 52 v2.1)

Extracts: `extracts/noise_v3/A`, `extracts/noise_v3/B`. Pure pandas/numpy; every candidate value comes from `pool_objectives.pool_row`. This file decides nothing.

## 0. Identity (v3)

1. Every noise_v3 run is a v3 run: ruc_mipgap 0.001, ruc_time_limit 1200 s, read at run time from `waves/GAP_DECISION.json` (copied to `extracts/noise_v3/<batch>/GAP_DECISION_used.json`); task logs: 16 of 16 runs carry the identity line, values ruc_mipgap [0.001] / ruc_time_limit [1200.0].
2. Gate G1 is MET by `analysis/gap_smoke/GAP_SMOKE.md`: control arm byte-identical to smoke_v2, tolerance verified per RUC day, 0 time-limit hits.
3. The identity is recorded in `ERCOT_BO_PLAN.md` AMENDMENT 2026-11-06b (E-D6, Kay). No v2-identity value enters this file; the v2 table chose the designs only (`waves/noise_v3/PICK_RULE.md`).

## 1. Runs

| key | batch | design | copy | site | type | PEM MW | overall md5 | RUC optimal / TL | max gap % | wall h | core-h |
|---|---|---|---|---|---|---|---|---|---|---|---|
| noise_v3/A:1 | A | D1 | exact | 275 | WIND | 519.5000 | `fbaa386b` | 365 / 0 | 0.1 | 10.1 | 40.3 |
| noise_v3/A:2 | A | D2 | exact | 206 | WIND | 899.9000 | `6dde2591` | 365 / 0 | 0.1 | 9.79 | 39.2 |
| noise_v3/A:3 | A | D3 | exact | 146 | WIND | 134.0000 | `bdb103fb` | 365 / 0 | 0.1 | 11.2 | 44.8 |
| noise_v3/A:4 | A | D4 | exact | 1 | NUC | 2430.0000 | `1f63f9b5` | 365 / 0 | 0.1 | 9.86 | 39.4 |
| noise_v3/A:5 | A | D1 | perturbed | 275 | WIND | 520.0195 | `ae41b4df` | 365 / 0 | 0.1 | 10.8 | 43.4 |
| noise_v3/A:6 | A | D2 | perturbed | 206 | WIND | 900.7999 | `6dde2591` | 365 / 0 | 0.1 | 9.17 | 36.7 |
| noise_v3/A:7 | A | D3 | perturbed | 146 | WIND | 133.8660 | `8c9944f6` | 365 / 0 | 0.1 | 10.8 | 43.3 |
| noise_v3/A:8 | A | D4 | perturbed | 1 | NUC | 2427.5700 | `dbb4eec6` | 365 / 0 | 0.1 | 10.8 | 43.4 |
| noise_v3/B:1 | B | D1 | exact | 275 | WIND | 519.5000 | `fbaa386b` | 365 / 0 | 0.1 | 10.1 | 40.2 |
| noise_v3/B:2 | B | D2 | exact | 206 | WIND | 899.9000 | `6dde2591` | 365 / 0 | 0.1 | 9.77 | 39.1 |
| noise_v3/B:3 | B | D3 | exact | 146 | WIND | 134.0000 | `bdb103fb` | 365 / 0 | 0.1 | 11 | 43.9 |
| noise_v3/B:4 | B | D4 | exact | 1 | NUC | 2430.0000 | `1f63f9b5` | 365 / 0 | 0.1 | 9.82 | 39.3 |
| noise_v3/B:5 | B | D1 | perturbed | 275 | WIND | 518.9805 | `ddc8b669` | 365 / 0 | 0.1 | 10.8 | 43.1 |
| noise_v3/B:6 | B | D2 | perturbed | 206 | WIND | 899.0001 | `6dde2591` | 365 / 0 | 0.1 | 9.12 | 36.5 |
| noise_v3/B:7 | B | D3 | perturbed | 146 | WIND | 134.1340 | `f39f6ff0` | 365 / 0 | 0.1 | 10.6 | 42.3 |
| noise_v3/B:8 | B | D4 | perturbed | 1 | NUC | 2425.1400 | `c34c8770` | 365 / 0 | 0.1 | 9.95 | 39.8 |

## 2. Exact cross-batch pairs (the noise population tau)

4 pairs (A exact vs B exact); overall.csv byte-identical on 4 of 4.

**Every gradable candidate shows an exact-pair |Δ| of 0 — reported as exact zeros.** Finding, pre-registered (prompt 52 section 1): If their sd is 0, τ collapses toward 0 and the stop rule becomes budget-cap-only — that is a FINDING about a deterministic instrument, stated in exactly those words, not a failure.
The GP noise floor (ERCOT_BO_PLAN.md section 3): exact sd = 0, so the floor is 0 and the GP noise is INFERRED-only with the 1e-9 bound (the D-1025 pattern).

| id | name | unit | pairs | max exact pair |Δ| | exact zero | exact pooled sd (df) |
|---|---|---|---|---|---|---|
| V1 | true curtailment | MWh | 4 | 0 | yes | 0 (4) |
| E1 | total cost | $ | 4 | 0 | yes | 0 (4) |
| X1 | CO2 (fuel-factor) | t | 4 | 0 | yes | 0 (4) |
| R4 | thermal starts | count | 4 | 0 | yes | 0 (4) |
| N1 | congested line-hours | line-h | 4 | 0 | yes | 0 (4) |
| E4 | total payments (consumer side) | $ | 4 | 0 | yes | 0 (4) |
| R2 | reserve shortfall | MWh | 4 | 0 | yes | 0 (4) |
| R7 | committed capacity-hours | MWh | 4 | 0 | yes | 0 (4) |
| N4 | pocket-120 congested line-hours | line-h | 4 | 0 | yes | 0 (4) |
| N5 | congestion spread | $/MWh | 4 | 0 | yes | 0 (4) |
| E6 | VRE energy payments | $ | 4 | 0 | yes | 0 (4) |
| R5 | start/stop ramping | MW | 4 | 0 | yes | 0 (4) |
| N3 | flow violation | MWh | 4 | 0 | yes | 0 (4) |
| E2 | fixed (commitment) cost | $ | 4 | 0 | yes | 0 (4) |
| R6 | nominal ramping | MW | 4 | 0 | yes | 0 (4) |
| N2 | congested lines | count | 4 | 0 | yes | 0 (4) |
| E3 | variable cost | $ | 4 | 0 | yes | 0 (4) |
| R8 | committed unit-hours | unit-h | 4 | 0 | yes | 0 (4) |
| E7 | mean settlement price (energy) | $/MWh | 4 | 0 | yes | 0 (4) |
| E8 | LMP dispersion | $/MWh | 4 | 0 | yes | 0 (4) |
| E9 | scarcity bus-hours | count | 4 | 0 | yes | 0 (4) |
| V2 | renewables penetration | % | 4 | 0 | yes | 0 (4) |
| V3 | PEM-twin delivered share | fraction | 4 | 0 | yes | 0 (4) |
| E5 | uplift payments | $ | 4 | 0 | yes | 0 (4) |
| R1 | load shed | MWh | 4 | 0 | yes | 0 (4) |
| R3 | over generation | MWh | 4 | 0 | yes | 0 (4) |
| D1 | H2 electricity | MWh | 3 | 0 | yes | 0 (3) |
| D2 | PEM utilization | fraction | 3 | 0 | yes | 0 (3) |

## 3. Perturbed copies (local input sensitivity; the ruler)

8 perturbed runs (delta = 0.001 relative on pem_mw; sign and inward rule in `waves/noise_v3/PICK_RULE.md`), each read against the exact copy of the same design in the same batch. `ruler_j` = median |Δ_j| (prompt 57 section 3 A4). This population is never pooled with section 2.

| perturbed key | design | ref key | PEM MW | ref PEM MW | sign | delta_rel | in ruler (prompt 63 A1) |
|---|---|---|---|---|---|---|---|
| noise_v3/A:5 | D1 | noise_v3/A:1 | 520.0195 | 519.5000 | +1 | 0.001 | yes |
| noise_v3/A:6 | D2 | noise_v3/A:2 | 900.7999 | 899.9000 | +1 | 0.001 | **no — STRUCTURAL ZERO** (section 10) |
| noise_v3/A:7 | D3 | noise_v3/A:3 | 133.8660 | 134.0000 | -1 | 0.001 | yes |
| noise_v3/A:8 | D4 | noise_v3/A:4 | 2427.5700 | 2430.0000 | -1 | 0.001 | yes |
| noise_v3/B:5 | D1 | noise_v3/B:1 | 518.9805 | 519.5000 | -1 | 0.001 | yes |
| noise_v3/B:6 | D2 | noise_v3/B:2 | 899.0001 | 899.9000 | -1 | 0.001 | **no — STRUCTURAL ZERO** (section 10) |
| noise_v3/B:7 | D3 | noise_v3/B:3 | 134.1340 | 134.0000 | +1 | 0.001 | yes |
| noise_v3/B:8 | D4 | noise_v3/B:4 | 2425.1400 | 2430.0000 | -1 | 0.002 | yes |

Since 2026-11-17 (prompt 63 A1) the ruler, the levels, the trigger and B_j use the 6 non-structural copies; the 2 structural-zero copies are listed in section 10.

| id | name | unit | n | ruler_j (median |Δ|) | min | max | status | |Δ| values (structural zeros excluded) |
|---|---|---|---|---|---|---|---|---|
| V1 | true curtailment | MWh | 6 | 2420 | 149.4 | 1.227e+04 | RULER | 1.227e+04, 3072, 2266, 149.4, 2574, 1632 |
| E1 | total cost | $ | 6 | 2.319e+05 | 3.911e+04 | 1.862e+06 | RULER | 2.271e+05, 3.911e+04, 4.085e+05, 2.367e+05, 2.095e+05, 1.862e+06 |
| X1 | CO2 (fuel-factor) | t | 6 | 5555 | 2490 | 2.245e+04 | RULER | 6693, 2.245e+04, 4417, 1.712e+04, 4302, 2490 |
| R4 | thermal starts | count | 6 | 28.5 | 10 | 90 | RULER | 10, 37, 20, 90, 20, 63 |
| N1 | congested line-hours | line-h | 6 | 23.5 | 9 | 65 | RULER | 9, 65, 15, 55, 15, 32 |
| E4 | total payments (consumer side) | $ | 6 | 2.031e+06 | 4.092e+05 | 5.214e+06 | RULER | 1.310e+06, 4.092e+05, 5.214e+06, 2.752e+06, 1.165e+06, 3.198e+06 |
| R2 | reserve shortfall | MWh | 6 | 26.26 | 20.99 | 58.87 | RULER | 34.71, 21.87, 28.27, 20.99, 24.24, 58.87 |
| R7 | committed capacity-hours | MWh | 6 | 8.54e+04 | 5.018e+04 | 1.235e+05 | RULER | 1.235e+05, 6.791e+04, 1.032e+05, 1.018e+05, 5.018e+04, 6.898e+04 |
| N4 | pocket-120 congested line-hours | line-h | 6 | 13 | 1 | 17 | RULER | 1, 5, 16, 17, 12, 14 |
| N5 | congestion spread | $/MWh | 6 | 0.05191 | 0.0285 | 0.09934 | RULER | 0.0421, 0.06172, 0.0285, 0.06711, 0.0383, 0.09934 |
| E6 | VRE energy payments | $ | 6 | 6.724e+05 | 3.619e+05 | 1.555e+06 | RULER | 3.619e+05, 1.555e+06, 7.857e+05, 5.590e+05, 1.365e+06, 5.452e+05 |
| R5 | start/stop ramping | MW | 6 | 4630 | 297.1 | 8808 | RULER | 5414, 7655, 1945, 3847, 297.1, 8808 |
| N3 | flow violation | MWh | 6 | 4.634 | 0.3435 | 7.038 | RULER | 6.042, 5.003, 0.8888, 0.3435, 7.038, 4.265 |
| E2 | fixed (commitment) cost | $ | 6 | 8.371e+05 | 5.780e+05 | 1.555e+06 | RULER | 5.780e+05, 1.003e+06, 1.555e+06, 6.768e+05, 9.974e+05, 6.348e+05 |
| R6 | nominal ramping | MW | 6 | 1.762e+04 | 275.5 | 5.681e+04 | RULER | 1.132e+04, 275.5, 2.393e+04, 8361, 5.681e+04, 5.583e+04 |
| N2 | congested lines | count | 6 | 0.5 | 0 | 2 | RULER | 1, 2, 0, 0, 0, 1 |
| E3 | variable cost | $ | 6 | 9.780e+05 | 3.510e+05 | 1.964e+06 | RULER | 3.510e+05, 1.043e+06, 1.964e+06, 9.135e+05, 7.879e+05, 1.227e+06 |
| R8 | committed unit-hours | unit-h | 6 | 472 | 129 | 740 | RULER | 520, 740, 129, 424, 174, 737 |
| E7 | mean settlement price (energy) | $/MWh | 6 | 0.003582 | 0.001399 | 0.01083 | RULER | 0.002143, 0.01083, 0.005022, 0.001968, 0.005562, 0.001399 |
| E8 | LMP dispersion | $/MWh | 6 | 0.07674 | 0.06881 | 0.1707 | RULER | 0.07843, 0.1707, 0.07506, 0.06881, 0.07144, 0.1009 |
| E9 | scarcity bus-hours | count | 6 | 0 | 0 | 0 | RULER=0 | 0, 0, 0, 0, 0, 0 |
| V2 | renewables penetration | % | 6 | 5.470e-04 | 3.320e-04 | 0.003165 | RULER | 0.003165, 5.180e-04, 5.900e-04, 5.760e-04, 3.320e-04, 4.250e-04 |
| V3 | PEM-twin delivered share | fraction | 6 | 5.141e-06 | 0 | 2.318e-05 | RULER | 2.318e-05, 4.676e-06, 0, 5.605e-06, 7.145e-06, 0 |
| E5 | uplift payments | $ | 6 | 0 | 0 | 0 | RULER=0 | 0, 0, 0, 0, 0, 0 |
| R1 | load shed | MWh | 6 | 0 | 0 | 0 | RULER=0 | 0, 0, 0, 0, 0, 0 |
| R3 | over generation | MWh | 6 | 0 | 0 | 0 | RULER=0 | 0, 0, 0, 0, 0, 0 |
| D1 | H2 electricity | MWh | 4 | 1191 | 120.7 | 2360 | RULER | 120.7, 1082, 2360, 1300 |
| D2 | PEM utilization | fraction | 4 | 2.982e-04 | 1.301e-04 | 6.744e-04 | RULER | 6.744e-04, 2.057e-04, 1.301e-04, 3.907e-04 |

`RULER=0` candidates (gradable): E9 — readable iff |Δ| >= 1 natural unit (prompt 57 section 3 A4); continuous candidates report the raw Δ with the tag.
`RULER UNAVAILABLE` (gradable): none.
Readable means, in exactly these words: "exceeds twice the median response to a 0.1 % input perturbation at the prompt-52 designs." An effect that fails reads "not readable above the perturbation response", never "zero".

## 4. Per-level and pooled sd of the perturbed population; variance-ratio trigger

Level = design. Per-level sd = sd of {exact, perturbed copies} of that design (ddof 1, df = number of perturbed copies). Pooled sd = sqrt(Σ df_i s_i² / Σ df_i) with Satterthwaite df = (Σ df_i s_i²)² / Σ (df_i s_i²)² / df_i. CIs are chi-square 95 %. Trigger per objective: F test of max s² / min s² at alpha = 0.05 AND point ratio > 3. A non-firing trigger reads "not detectable at this df", never "homoscedastic confirmed" (prompt 52 section 3 precision budget).

**Family-wise disclosure:** 22 gradable candidates are tested at alpha = 0.05 each with no family-wise correction; a false trigger only replaces a scalar sd by per-level sds (conservative), so none is applied.

| id | per-level sd (df) [95 % CI] | pooled sd | Satterthwaite df | pooled 95 % CI | ratio | p | verdict |
|---|---|---|---|---|---|---|---|
| V1 | D1 7040 (2) [3665, 4.424e+04]; D3 2826 (2) [1472, 1.776e+04]; D4 1958 (2) [1019, 1.231e+04] | 4523 | 2.97 | [2558, 1.703e+04] | 12.9 | 0.0718 | not detectable at this df (ratio 12.93, p = 0.0718; df 2/2) |
| E1 | D1 2.319e+05 (2) [1.207e+05, 1.458e+06]; D3 1.337e+05 (2) [6.961e+04, 8.403e+05]; D4 9.786e+05 (2) [5.095e+05, 6.150e+06] | 5.857e+05 | 2.3 | [3.142e+05, 2.994e+06] | 53.6 | 0.0183 | TRIGGER: scalar sd rejected (ratio 53.57 > 3, p = 0.0183 < 0.05) |
| X1 | D1 1.228e+04 (2) [6394, 7.718e+04]; D3 1.191e+04 (2) [6203, 7.487e+04]; D4 2215 (2) [1153, 1.392e+04] | 9961 | 4.13 | [6004, 2.793e+04] | 30.8 | 0.0315 | TRIGGER: scalar sd rejected (ratio 30.75 > 3, p = 0.0315 < 0.05) |
| R4 | D1 49.33 (2) [25.68, 310]; D3 28.92 (2) [15.06, 181.8]; D4 32.19 (2) [16.76, 202.3] | 37.89 | 4.82 | [23.49, 95.17] | 2.91 | 0.256 | not detectable at this df (ratio 2.91, p = 0.256; df 2/2) |
| N1 | D1 34.65 (2) [18.04, 217.7]; D3 34.03 (2) [17.72, 213.9]; D4 16.01 (2) [8.336, 100.6] | 29.52 | 4.8 | [18.3, 74.35] | 4.68 | 0.176 | not detectable at this df (ratio 4.68, p = 0.176; df 2/2) |
| E4 | D1 2.073e+06 (2) [1.079e+06, 1.303e+07]; D3 8.166e+05 (2) [4.251e+05, 5.132e+06]; D4 2.629e+06 (2) [1.369e+06, 1.652e+07] | 1.990e+06 | 4.23 | [1.205e+06, 5.478e+06] | 10.4 | 0.088 | not detectable at this df (ratio 10.37, p = 0.088; df 2/2) |
| R2 | D1 28.13 (2) [14.64, 176.8]; D3 13.36 (2) [6.958, 83.99]; D4 44.46 (2) [23.15, 279.4] | 31.34 | 3.8 | [18.6, 93.78] | 11.1 | 0.0829 | not detectable at this df (ratio 11.07, p = 0.0829; df 2/2) |
| R7 | D1 6.595e+04 (2) [3.434e+04, 4.145e+05]; D3 3.522e+04 (2) [1.834e+04, 2.214e+05]; D4 8.664e+04 (2) [4.511e+04, 5.445e+05] | 6.607e+04 | 4.47 | [4.041e+04, 1.749e+05] | 6.05 | 0.142 | not detectable at this df (ratio 6.05, p = 0.142; df 2/2) |
| N4 | D1 10.12 (2) [5.267, 63.58]; D3 6.028 (2) [3.138, 37.88]; D4 15.01 (2) [7.816, 94.34] | 11.02 | 4.24 | [6.671, 30.3] | 6.2 | 0.139 | not detectable at this df (ratio 6.20, p = 0.139; df 2/2) |
| N5 | D1 0.05508 (2) [0.02868, 0.3462]; D3 0.05047 (2) [0.02628, 0.3172]; D4 0.05115 (2) [0.02663, 0.3215] | 0.05227 | 5.96 | [0.03365, 0.1155] | 1.19 | 0.456 | not detectable at this df (ratio 1.19, p = 0.456; df 2/2) |
| E6 | D1 4.640e+05 (2) [2.416e+05, 2.916e+06]; D3 8.482e+05 (2) [4.416e+05, 5.330e+06]; D4 4.026e+05 (2) [2.096e+05, 2.530e+06] | 6.046e+05 | 4.08 | [3.635e+05, 1.712e+06] | 4.44 | 0.184 | not detectable at this df (ratio 4.44, p = 0.184; df 2/2) |
| R5 | D1 2786 (2) [1450, 1.751e+04]; D3 4336 (2) [2258, 2.725e+04]; D4 4627 (2) [2409, 2.908e+04] | 3999 | 5.28 | [2520, 9483] | 2.76 | 0.266 | not detectable at this df (ratio 2.76, p = 0.266; df 2/2) |
| N3 | D1 3.394 (2) [1.767, 21.33]; D3 3.622 (2) [1.886, 22.76]; D4 2.25 (2) [1.172, 14.14] | 3.146 | 5.34 | [1.987, 7.408] | 2.59 | 0.279 | not detectable at this df (ratio 2.59, p = 0.279; df 2/2) |
| E2 | D1 3.656e+05 (2) [1.903e+05, 2.298e+06]; D3 5.776e+05 (2) [3.007e+05, 3.630e+06]; D4 1.127e+06 (2) [5.866e+05, 7.081e+06] | 7.609e+05 | 3.47 | [4.435e+05, 2.467e+06] | 9.5 | 0.0953 | not detectable at this df (ratio 9.50, p = 0.0953; df 2/2) |
| R6 | D1 9879 (2) [5143, 6.208e+04]; D3 3.288e+04 (2) [1.712e+04, 2.067e+05]; D4 2.801e+04 (2) [1.458e+04, 1.760e+05] | 2.558e+04 | 4.3 | [1.553e+04, 6.961e+04] | 11.1 | 0.0828 | not detectable at this df (ratio 11.08, p = 0.0828; df 2/2) |
| N2 | D1 0.5774 (2) [0.3006, 3.628]; D3 1.155 (2) [0.6012, 7.257]; D4 0.5774 (2) [0.3006, 3.628] | 0.8165 | 4 | [0.4892, 2.346] | 4 | 0.2 | not detectable at this df (ratio 4.00, p = 0.2; df 2/2) |
| E3 | D1 4.608e+05 (2) [2.399e+05, 2.896e+06]; D3 5.435e+05 (2) [2.830e+05, 3.416e+06]; D4 9.920e+05 (2) [5.165e+05, 6.234e+06] | 7.052e+05 | 4.04 | [4.234e+05, 2.009e+06] | 4.63 | 0.178 | not detectable at this df (ratio 4.63, p = 0.178; df 2/2) |
| R8 | D1 472.8 (2) [246.2, 2972]; D3 386.9 (2) [201.5, 2432]; D4 393.6 (2) [204.9, 2474] | 419.6 | 5.79 | [268.7, 942.5] | 1.49 | 0.401 | not detectable at this df (ratio 1.49, p = 0.401; df 2/2) |
| E7 | D1 0.00119 (2) [6.195e-04, 0.007477]; D3 0.005417 (2) [0.002821, 0.03405]; D4 0.002592 (2) [0.001349, 0.01629] | 0.003535 | 3.09 | [0.002014, 0.01277] | 20.7 | 0.046 | TRIGGER: scalar sd rejected (ratio 20.73 > 3, p = 0.046 < 0.05) |
| E8 | D1 0.07367 (2) [0.03836, 0.463]; D3 0.08575 (2) [0.04465, 0.5389]; D4 0.05242 (2) [0.02729, 0.3295] | 0.07195 | 5.3 | [0.04537, 0.1703] | 2.68 | 0.272 | not detectable at this df (ratio 2.68, p = 0.272; df 2/2) |
| E9 | D1 0 (2) [0, 0]; D3 0 (2) [0, 0]; D4 0 (2) [0, 0] | 0 | 6 | [0, 0] | n/a | n/a | all levels sd 0 (exact zeros): not detectable at this df |
| V2 | D1 0.002014 (2) [0.001049, 0.01266]; D3 4.284e-04 (2) [2.230e-04, 0.002692]; D4 5.097e-04 (2) [2.654e-04, 0.003204] | 0.001225 | 2.45 | [6.655e-04, 0.005781] | 22.1 | 0.0433 | TRIGGER: scalar sd rejected (ratio 22.11 > 3, p = 0.0433 < 0.05) |
| V3 | D1 1.210e-05 (2) [6.298e-06, 7.602e-05]; D3 5.953e-06 (2) [3.100e-06, 3.742e-05]; D4 0 (2) [0, 0] | 7.784e-06 | 2.92 | [4.384e-06, 2.991e-05] | inf | 0 | TRIGGER: a level has sd 0 and another sd > 0 (ratio undefined); scalar sd rejected per objective |
| E5 | D1 0 (2) [0, 0]; D3 0 (2) [0, 0]; D4 0 (2) [0, 0] | 0 | 6 | [0, 0] | n/a | n/a | all levels sd 0 (exact zeros): not detectable at this df |
| R1 | D1 0 (2) [0, 0]; D3 0 (2) [0, 0]; D4 0 (2) [0, 0] | 0 | 6 | [0, 0] | n/a | n/a | all levels sd 0 (exact zeros): not detectable at this df |
| R3 | D1 0 (2) [0, 0]; D3 0 (2) [0, 0]; D4 0 (2) [0, 0] | 0 | 6 | [0, 0] | n/a | n/a | all levels sd 0 (exact zeros): not detectable at this df |
| D1 | D1 1329 (2) [692, 8353]; D3 1192 (2) [620.7, 7493]; D4 n/a (0) [n/a, n/a] | 1262 | 3.95 | [754.7, 3661] | 1.24 | 0.446 | not detectable at this df (ratio 1.24, p = 0.446; df 2/2) |
| D2 | D1 4.318e-04 (2) [2.248e-04, 0.002714]; D3 3.030e-04 (2) [1.577e-04, 0.001904]; D4 n/a (0) [n/a, n/a] | 3.730e-04 | 3.58 | [2.188e-04, 0.001174] | 2.03 | 0.33 | not detectable at this df (ratio 2.03, p = 0.33; df 2/2) |

## 5. Cross-objective covariance of the perturbed deltas

`ercot_noise_cov.csv` (26 x 26; rows = perturbed runs, ddof 1; candidates with a finite delta on every perturbed run). Prompt 55 samples noise vectors JOINTLY from it, or marginal with a joint-vs-marginal sensitivity row. Candidates with an all-zero column have zero covariance with everything.

| id | variance of Δ | sd of Δ |
|---|---|---|
| V1 | 2.163e+07 | 4651 |
| E1 | 4.337e+11 | 6.586e+05 |
| X1 | 1.169e+08 | 1.081e+04 |
| R4 | 2048 | 45.26 |
| N1 | 1255 | 35.42 |
| E4 | 5.824e+12 | 2.413e+06 |
| R2 | 996.5 | 31.57 |
| R7 | 6.523e+09 | 8.076e+04 |
| N4 | 108.3 | 10.41 |
| N5 | 0.002891 | 0.05377 |
| E6 | 7.485e+11 | 8.652e+05 |
| R5 | 2.472e+07 | 4972 |
| N3 | 16.51 | 4.063 |
| E2 | 8.016e+11 | 8.953e+05 |
| R6 | 1.004e+09 | 3.169e+04 |
| N2 | 0.7857 | 0.8864 |
| E3 | 1.024e+12 | 1.012e+06 |
| R8 | 1.640e+05 | 405 |
| E7 | 2.566e-05 | 0.005066 |
| E8 | 0.005441 | 0.07376 |
| E9 | 0 | 0 |
| V2 | 1.454e-06 | 0.001206 |
| V3 | 7.932e-11 | 8.906e-06 |
| E5 | 0 | 0 |
| R1 | 0 | 0 |
| R3 | 0 | 0 |

## 5b. Covariance of the EXACT cross-batch pair deltas (the Sigma of tau; plan 3 / 6.2, contract 6.3)

`ercot_noise_exact_cov.csv` (22 x 22; rows = the 4 exact pairs, ddof 1; gradable candidates finite on every pair). THIS matrix — never the perturbed one of section 5 — feeds prompt 55's tau_joint / tau_marginal. The perturbed matrix feeds the plan-7 sensitivity-level rider only.

**Identically zero: every exact pair delta is 0, so Sigma_exact = 0 and tau_joint = tau_marginal = 0 — the stop rule is budget-cap-only and the cap governs (plan 3).**

## 5c. SUSPECT check (plan 1.2, S1-S3) and the READABILITY verdict (FINAL)

| key | design | copy | nuclear | S1 (|total-fixed-var| <= $1) | S2 (all RUC OPTIMAL) | S3a (units 1 / 93 starts = 0; n/a nuclear) | SUSPECT |
|---|---|---|---|---|---|---|---|
| noise_v3/A:1 | D1 | exact | no | ok (9.54e-07) | ok (365 / 365) | ok (0 / 0) | no |
| noise_v3/A:2 | D2 | exact | no | ok (0) | ok (365 / 365) | ok (0 / 0) | no |
| noise_v3/A:3 | D3 | exact | no | ok (0) | ok (365 / 365) | ok (0 / 0) | no |
| noise_v3/A:4 | D4 | exact | yes | ok (9.54e-07) | ok (365 / 365) | n/a (0 / 0) | no |
| noise_v3/A:5 | D1 | perturbed | no | ok (9.54e-07) | ok (365 / 365) | ok (0 / 0) | no |
| noise_v3/A:6 | D2 | perturbed | no | ok (0) | ok (365 / 365) | ok (0 / 0) | no |
| noise_v3/A:7 | D3 | perturbed | no | ok (0) | ok (365 / 365) | ok (0 / 0) | no |
| noise_v3/A:8 | D4 | perturbed | yes | ok (0) | ok (365 / 365) | n/a (0 / 0) | no |
| noise_v3/B:1 | D1 | exact | no | ok (9.54e-07) | ok (365 / 365) | ok (0 / 0) | no |
| noise_v3/B:2 | D2 | exact | no | ok (0) | ok (365 / 365) | ok (0 / 0) | no |
| noise_v3/B:3 | D3 | exact | no | ok (0) | ok (365 / 365) | ok (0 / 0) | no |
| noise_v3/B:4 | D4 | exact | yes | ok (9.54e-07) | ok (365 / 365) | n/a (0 / 0) | no |
| noise_v3/B:5 | D1 | perturbed | no | ok (0) | ok (365 / 365) | ok (0 / 0) | no |
| noise_v3/B:6 | D2 | perturbed | no | ok (0) | ok (365 / 365) | ok (0 / 0) | no |
| noise_v3/B:7 | D3 | perturbed | no | ok (0) | ok (365 / 365) | ok (0 / 0) | no |
| noise_v3/B:8 | D4 | perturbed | yes | ok (9.54e-07) | ok (365 / 365) | n/a (0 / 0) | no |

S3b (cross-run: units 1 / 93 starts equal across the exact cross-batch pair):

| design | A exact | B exact | gen-1 starts A / B | gen-93 starts A / B | S3b |
|---|---|---|---|---|---|
| D1 | noise_v3/A:1 | noise_v3/B:1 | 0 / 0 | 0 / 0 | ok |
| D2 | noise_v3/A:2 | noise_v3/B:2 | 0 / 0 | 0 / 0 | ok |
| D3 | noise_v3/A:3 | noise_v3/B:3 | 0 / 0 | 0 / 0 | ok |
| D4 | noise_v3/A:4 | noise_v3/B:4 | 0 / 0 | 0 / 0 | ok |

**Plan 1.2 verdict: total_cost is READABLE -> the campaign cost objective is total_cost (E1).** Recorded once here; final (plan 1.2, 10: immutable). The cost objective is never switched mid-campaign.

| rule | test | value | threshold | result |
|---|---|---|---|---|
| R1 | no prompt-52 run SUSPECT (S1 ∧ S2 ∧ S3a per run; S3b per exact pair) | 0 SUSPECT, 0 S3b failures over 16 runs | 0 | PASS |
| R2 | max exact-pair \|Δ total_cost\| (4 pairs) | $0 | $1,132,088 (0.1 x single-site median \|Δ total\|) | PASS |
| R3 | max exact-pair \|Δ fixed_cost\| (4 pairs) | $0 | $1,325,082 (0.1 x single-site median \|Δ fixed\|) | PASS |

Thresholds from `analysis/bo_plan/plan51_refs.json` (plan 1.2: $11.32M and $13.25M single-site medians). The gap bound of prompt 57 (G_run) is an evidence column, never a verdict label (plan AMENDMENT 2026-11-06).

## 6. Load shed assert (protects E-D1)

shed ≡ 0 on all 16 runs: **PASS**.

## 7. Runtime (wall-clock per run -> core-h at 4 slots)

16 of 16 runs carry a wall-clock stamp. core-h median 40.3, min 36.5, max 44.8, total 654.6. This replaces the line "Per-run core-h on v2 is UNKNOWN" of ERCOT_BO_PLAN.md section 8 (budget actuals).

| key | design | copy | wall h | core-h | RUC optimal | TL hits | Prescient runtimes.csv |
|---|---|---|---|---|---|---|---|
| noise_v3/A:1 | D1 | exact | 10.1 | 40.3 | 365 | 0 | no |
| noise_v3/A:2 | D2 | exact | 9.79 | 39.2 | 365 | 0 | no |
| noise_v3/A:3 | D3 | exact | 11.2 | 44.8 | 365 | 0 | no |
| noise_v3/A:4 | D4 | exact | 9.86 | 39.4 | 365 | 0 | no |
| noise_v3/A:5 | D1 | perturbed | 10.8 | 43.4 | 365 | 0 | no |
| noise_v3/A:6 | D2 | perturbed | 9.17 | 36.7 | 365 | 0 | no |
| noise_v3/A:7 | D3 | perturbed | 10.8 | 43.3 | 365 | 0 | no |
| noise_v3/A:8 | D4 | perturbed | 10.8 | 43.4 | 365 | 0 | no |
| noise_v3/B:1 | D1 | exact | 10.1 | 40.2 | 365 | 0 | no |
| noise_v3/B:2 | D2 | exact | 9.77 | 39.1 | 365 | 0 | no |
| noise_v3/B:3 | D3 | exact | 11 | 43.9 | 365 | 0 | no |
| noise_v3/B:4 | D4 | exact | 9.82 | 39.3 | 365 | 0 | no |
| noise_v3/B:5 | D1 | perturbed | 10.8 | 43.1 | 365 | 0 | no |
| noise_v3/B:6 | D2 | perturbed | 9.12 | 36.5 | 365 | 0 | no |
| noise_v3/B:7 | D3 | perturbed | 10.6 | 42.3 | 365 | 0 | no |
| noise_v3/B:8 | D4 | perturbed | 9.95 | 39.8 | 365 | 0 | no |

## 8. Free data first (prompt 52 section 2; history only)

- v2 byte-identical groups D01, D02, D09, D21: max within-group |Δ| over every candidate = 0 (`analysis/pool/pool_replicate_zero_check_v2.csv`). v2 identity; not pooled with v3.
- v1 screening ruler (SUPERSEDED, `analysis/INVALID_v1_costs.md`): var_cost 2.856e+05 $, total_cost 7.945e+07 $ (bimodal TL=120 race). Quoted as history only.
- v1 selection ruler `analysis/selection/noise_ruler_v2.json` (v1-extract based): identical inputs rerun under TL=120 (machine-load-dependent incumbents); conditional on CRC env. History only.
- The prompt-33 TL=360 base x3 is an old-identity anchor and is not read here.

## 9. Deviations and limits

- Batch split: per design exact A + exact B + one perturbed copy in A (layout 12), unless `waves/noise_v3/README.md` section 5 says layout 16. The ruler population size is the `n` column of section 3.
- With df = 1 per level the F test rejects only at observed ratios > 161 (alpha 0.05, one-sided); the trigger is an order-of-magnitude detector. Pooled sd CIs are wide at these df; read the CI, not the point.
- E8, E9, N5 use the CRC-computed `pool_full_metrics.json` (the gz tables are not in git).
- Outputs: `analysis/noise_v3/ercot_noise.csv`, `ercot_noise.json`, `ercot_noise_cov.csv` (perturbed; rider only), `ercot_noise_exact_cov.csv` (exact; tau).

## 10. 2026-11-17 — structural-zero perturbed pairs excluded (prompt 63 A1; memo F6)

Rule (generic, applied in code): a perturbed copy whose design MW differs from its exact copy's but whose `overall.csv` is byte-identical (md5) to the exact copy's has an identical effective model input. It is EXCLUDED from the ruler, the per-level sd, the pooled sd, the trigger and the 61 bar B_j. Evidence column: the PEM slice is min(PEM capacity, availability_t) (`multi_pem/parameters.py:87-91`); when both capacities are at or above the site's maximum hourly availability (REAL_TIME and DAY_AHEAD series), the capped input series is identical. The exact cross-batch pairs (section 2) and the rider covariance `ercot_noise_cov.csv` (section 5; all perturbed rows) are unchanged. The previous outputs are kept as `ercot_noise_2026-11-16.json` (5ca9650).

| perturbed key | ref key | site | PEM MW | ref PEM MW | overall md5 (pert / ref) | site max availability MW | capped input identical | evidence consistent | EXCLUDED |
|---|---|---|---|---|---|---|---|---|---|
| noise_v3/A:5 | noise_v3/A:1 | 275 | 520.0195 | 519.5000 | `ae41b4df` / `fbaa386b` | 1039.00 | no | yes | no |
| noise_v3/A:6 | noise_v3/A:2 | 206 | 900.7999 | 899.9000 | `6dde2591` / `6dde2591` | 895.48 | yes | yes | **yes** |
| noise_v3/A:7 | noise_v3/A:3 | 146 | 133.8660 | 134.0000 | `8c9944f6` / `bdb103fb` | 268.00 | no | yes | no |
| noise_v3/A:8 | noise_v3/A:4 | 1 | 2427.5700 | 2430.0000 | `dbb4eec6` / `1f63f9b5` | n/a | n/a | n/a | no |
| noise_v3/B:5 | noise_v3/B:1 | 275 | 518.9805 | 519.5000 | `ddc8b669` / `fbaa386b` | 1039.00 | no | yes | no |
| noise_v3/B:6 | noise_v3/B:2 | 206 | 899.0001 | 899.9000 | `6dde2591` / `6dde2591` | 895.48 | yes | yes | **yes** |
| noise_v3/B:7 | noise_v3/B:3 | 146 | 134.1340 | 134.0000 | `f39f6ff0` / `bdb103fb` | 268.00 | no | yes | no |
| noise_v3/B:8 | noise_v3/B:4 | 1 | 2425.1400 | 2430.0000 | `c34c8770` / `1f63f9b5` | n/a | n/a | n/a | no |

Excluded: noise_v3/A:6, noise_v3/B:6 (2 of 8 perturbed copies; 6 remain).

Flag (kept in the population, memo F9): noise_v3/B:8 used delta_rel = 0.002 — step differs from the nominal 0.001 relative (inward rule; PICK_RULE.md).

Old (all perturbed copies, 5ca9650) vs new (structural zeros excluded), gradable candidates. B_j = max(3·σ̂_j, max_i |δ_ij|), σ̂_j = sqrt(mean δ_ij²) over the signed deltas (`per_candidate.<j>.bar`; the old value is `per_candidate.<j>.with_structural_zeros.bar`). B_j is the two-run contrast bar of prompt 61 section 3 (contract addendum 2026-11-17).

| id | unit | n old / new | ruler old | ruler new | pooled sd old | pooled sd new | trigger old | trigger new | σ̂ old | σ̂ new | B_j old | B_j new |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| V1 | MWh | 8 / 6 | 1949 | 2420 | 3917 | 4523 | FIRES (sd-0 level) | no (ratio 12.9, p 0.0718) | 4669 | 5391 | 1.401e+04 | 1.617e+04 |
| E1 | $ | 8 / 6 | 2.183e+05 | 2.319e+05 | 5.073e+05 | 5.857e+05 | FIRES (sd-0 level) | FIRES (ratio 53.6) | 6.880e+05 | 7.944e+05 | 2.064e+06 | 2.383e+06 |
| X1 | t | 8 / 6 | 4359 | 5555 | 8626 | 9961 | FIRES (sd-0 level) | FIRES (ratio 30.8) | 1.052e+04 | 1.215e+04 | 3.157e+04 | 3.645e+04 |
| R4 | count | 8 / 6 | 20 | 28.5 | 32.81 | 37.89 | FIRES (sd-0 level) | no (ratio 2.91, p 0.256) | 42.33 | 48.88 | 127 | 146.7 |
| N1 | line-h | 8 / 6 | 15 | 23.5 | 25.57 | 29.52 | FIRES (sd-0 level) | no (ratio 4.68, p 0.176) | 33.18 | 38.31 | 99.53 | 114.9 |
| E4 | $ | 8 / 6 | 1.237e+06 | 2.031e+06 | 1.723e+06 | 1.990e+06 | FIRES (sd-0 level) | no (ratio 10.4, p 0.088) | 2.455e+06 | 2.835e+06 | 7.366e+06 | 8.505e+06 |
| R2 | MWh | 8 / 6 | 23.06 | 26.26 | 27.14 | 31.34 | FIRES (sd-0 level) | no (ratio 11.1, p 0.0829) | 29.53 | 34.1 | 88.59 | 102.3 |
| R7 | MWh | 8 / 6 | 6.844e+04 | 8.54e+04 | 5.722e+04 | 6.607e+04 | FIRES (sd-0 level) | no (ratio 6.05, p 0.142) | 7.759e+04 | 8.959e+04 | 2.328e+05 | 2.688e+05 |
| N4 | line-h | 8 / 6 | 8.5 | 13 | 9.539 | 11.02 | FIRES (sd-0 level) | no (ratio 6.2, p 0.139) | 10.67 | 12.32 | 32.01 | 36.97 |
| N5 | $/MWh | 8 / 6 | 0.0402 | 0.05191 | 0.04527 | 0.05227 | FIRES (sd-0 level) | no (ratio 1.19, p 0.456) | 0.05272 | 0.06087 | 0.1582 | 0.1826 |
| E6 | $ | 8 / 6 | 5.521e+05 | 6.724e+05 | 5.236e+05 | 6.046e+05 | FIRES (sd-0 level) | no (ratio 4.44, p 0.184) | 8.395e+05 | 9.694e+05 | 2.519e+06 | 2.908e+06 |
| R5 | MW | 8 / 6 | 2896 | 4630 | 3463 | 3999 | FIRES (sd-0 level) | no (ratio 2.76, p 0.266) | 4798 | 5540 | 1.439e+04 | 1.662e+04 |
| N3 | MWh | 8 / 6 | 2.577 | 4.634 | 2.725 | 3.146 | FIRES (sd-0 level) | no (ratio 2.59, p 0.279) | 4.034 | 4.658 | 12.1 | 13.97 |
| E2 | $ | 8 / 6 | 6.558e+05 | 8.371e+05 | 6.589e+05 | 7.609e+05 | FIRES (sd-0 level) | no (ratio 9.5, p 0.0953) | 8.378e+05 | 9.674e+05 | 2.513e+06 | 2.902e+06 |
| R6 | MW | 8 / 6 | 9842 | 1.762e+04 | 2.215e+04 | 2.558e+04 | FIRES (sd-0 level) | no (ratio 11.1, p 0.0828) | 2.982e+04 | 3.444e+04 | 8.947e+04 | 1.033e+05 |
| N2 | count | 8 / 6 | 0 | 0.5 | 0.7071 | 0.8165 | FIRES (sd-0 level) | no (ratio 4, p 0.2) | 0.866 | 1 | 2.598 | 3 |
| E3 | $ | 8 / 6 | 8.507e+05 | 9.780e+05 | 6.107e+05 | 7.052e+05 | FIRES (sd-0 level) | no (ratio 4.63, p 0.178) | 1.002e+06 | 1.157e+06 | 3.005e+06 | 3.470e+06 |
| R8 | unit-h | 8 / 6 | 299 | 472 | 363.4 | 419.6 | FIRES (sd-0 level) | no (ratio 1.49, p 0.401) | 445.5 | 514.4 | 1337 | 1543 |
| E7 | $/MWh | 8 / 6 | 0.002055 | 0.003582 | 0.003061 | 0.003535 | FIRES (sd-0 level) | FIRES (ratio 20.7) | 0.004795 | 0.005537 | 0.01438 | 0.01661 |
| E8 | $/MWh | 8 / 6 | 0.07325 | 0.07674 | 0.06231 | 0.07195 | FIRES (sd-0 level) | no (ratio 2.68, p 0.272) | 0.0873 | 0.1008 | 0.2619 | 0.3024 |
| E9 | count | 8 / 6 | 0 | 0 | 0 | 0 | all levels 0 | all levels 0 | 0 | 0 | 0 | 0 |
| V2 | % | 8 / 6 | 4.715e-04 | 5.470e-04 | 0.001061 | 0.001225 | FIRES (sd-0 level) | FIRES (ratio 22.1) | 0.001186 | 0.00137 | 0.003559 | 0.004109 |

Trigger fires (gradable): old 21 (V1, E1, X1, R4, N1, E4, R2, R7, N4, N5, E6, R5, N3, E2, R6, N2, E3, R8, E7, E8, V2); new 4 (E1, X1, E7, V2). The old reading fired wherever a structural level had sd 0; the new reading is the order-of-magnitude detector of section 9 (df 2 per level).
`RULER=0` (gradable, new): E9.

## 11. 2026-11-17 — per-day RUC divergence (prompt 63 A2; memo F2)

Per pair, day by day: the daily RUC objective `ruc_cost` of `ruc_quality.csv` (slim table), perturbed copy vs the exact copy of the same design in the same batch, and, as the control, exact B vs exact A. A day is divergent iff the two values differ. Relative change = |Δ| / |reference| per day; median and p90 are over ALL days of the year (and the median over divergent days only); `> 1e-3` counts the days above the v3 MIP gap. File: `ercot_noise_daily_divergence.csv`.

| pair | key vs ref | design | δ rel | structural zero | days | divergent days | median rel (all days) | p90 rel (all days) | median rel (divergent days) | days > 1e-3 | max rel | first divergent day |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| perturbed | noise_v3/A:5 vs noise_v3/A:1 | D1 | 0.001 | no | 365 | 350 | 1.333e-04 | 8.544e-04 | 1.469e-04 | 28 | 0.004323 | day 1 (2019-01-01) |
| perturbed | noise_v3/A:6 vs noise_v3/A:2 | D2 | 0.001 | yes | 365 | 0 | 0 | 0 | 0 | 0 | 0 | none |
| perturbed | noise_v3/A:7 vs noise_v3/A:3 | D3 | 0.001 | no | 365 | 357 | 1.522e-04 | 9.317e-04 | 1.567e-04 | 32 | 0.007255 | day 1 (2019-01-01) |
| perturbed | noise_v3/A:8 vs noise_v3/A:4 | D4 | 0.001 | no | 365 | 365 | 1.808e-04 | 9.088e-04 | 1.808e-04 | 32 | 0.005707 | day 1 (2019-01-01) |
| perturbed | noise_v3/B:5 vs noise_v3/B:1 | D1 | 0.001 | no | 365 | 354 | 1.383e-04 | 7.710e-04 | 1.527e-04 | 29 | 0.004246 | day 1 (2019-01-01) |
| perturbed | noise_v3/B:6 vs noise_v3/B:2 | D2 | 0.001 | yes | 365 | 0 | 0 | 0 | 0 | 0 | 0 | none |
| perturbed | noise_v3/B:7 vs noise_v3/B:3 | D3 | 0.001 | no | 365 | 358 | 1.140e-04 | 6.588e-04 | 1.225e-04 | 19 | 0.005457 | day 1 (2019-01-01) |
| perturbed | noise_v3/B:8 vs noise_v3/B:4 | D4 | 0.002 | no | 365 | 365 | 2.543e-04 | 8.063e-04 | 2.543e-04 | 26 | 0.0064 | day 1 (2019-01-01) |
| exact | noise_v3/B:1 vs noise_v3/A:1 | D1 | 0.000 | no | 365 | 0 | 0 | 0 | 0 | 0 | 0 | none |
| exact | noise_v3/B:2 vs noise_v3/A:2 | D2 | 0.000 | no | 365 | 0 | 0 | 0 | 0 | 0 | 0 | none |
| exact | noise_v3/B:3 vs noise_v3/A:3 | D3 | 0.000 | no | 365 | 0 | 0 | 0 | 0 | 0 | 0 | none |
| exact | noise_v3/B:4 vs noise_v3/A:4 | D4 | 0.000 | no | 365 | 0 | 0 | 0 | 0 | 0 | 0 | none |

Non-structural perturbed pairs (6): 350–365 of 365 days divergent; median relative change 1.140e-04–2.543e-04 (inside the 1e-3 gap); 19–32 days per pair above 1e-3. Control (exact pairs and structural-zero pairs, 6): max 0 divergent days. This is the day-level evidence that the perturbed ruler measures solver-path chatter (incumbent selection inside the gap), not a smooth slope.

## 12. 2026-11-17 — determinism conditions (prompt 63 A4; memo F1, F7, F8)

Bit-identity of the 4 of 4 exact cross-batch pairs (section 2; section 11: 0 divergent RUC days) was observed under the conditions below. Each line states its source; a condition that is not recorded is stated as such.

1. **Code.** Prescient `a4c0849`, Egret `e4a244d` (editable installs in `env/PCM_ERCOT_pip_freeze.txt`, the PCM_ERCOT env export). ERCOT PCM code path (`run_ercot_pcm.py`, `trial_0826/multi_pem/`): last commit before the first noise_v3 task start (2026-11-06T22:34Z) = `6094e82`; latest commit on these paths = `6094e82` (the same: the code path did not change across batches A, B and base_v3). Collector heads: A `304335c`, B `771aa5b`. The run-time HEAD of the CRC clone is not written per run.
2. **Data.** `data/ercot123_2019_v2` (the v2 data dir; every array script passes it).
3. **Gurobi version.** NOT DISCOVERABLE from any job log under `extracts/` or `waves/*/`: the job `.o` files stay on CRC and the collectors keep only the identity line. Env records (not per-run): `env/gurobi_version.txt` = "Gurobi Optimizer version 11.0.2 build v11.0.2rc0 (linux64 - "Red Hat Enterprise Linux 9.8 (Plow)")"; pip freeze gurobipy == 13.0.2. The two env records name different versions; which Gurobi library the RUC solves used is not resolved by local evidence. The array scripts run `module load gurobi` with no version pin.
4. **Threads.** `--ruc_threads` 4 with `-pe smp` 4 in `waves/noise_v3/A/noise_v3_A_array.sh`, `waves/noise_v3/B/noise_v3_B_array.sh`, `waves/base_v3/base_v3_array.sh`.
5. **No time-limit hit.** noise_v3: 0 RUC time-limit hits over 16 runs (`pool_full_metrics.json` n_ruc_time_limit); 5840 of 5840 RUC days OPTIMAL. Maximum daily RUC solve: noise_v3 860.7 s (noise_v3/B:1), 5 days > 600 s; base_v3 481.1 s, 0 days > 600 s; TimeLimit 1,200 s (margin 1.39× on noise_v3; from `ruc_quality.csv`).
6. **Node class, hostname, CPU model.** Not recorded (memo F8). Runs started 2026-11-06T22:34Z – 2026-11-13T23:27Z (wall-clock stamps); A and B ran a week apart and matched.

Statement: exact repeats are bit-identical under (code above, v2 data, the Gurobi build of the CRC module / env at run time, Threads = 4, MIPGap 1e-3, no time-limit hit). A change of any of these is outside the evidence. Prompt 63 Part B adds hostname, CPU model, the gurobipy version, Threads and the Prescient / Egret SHAs to the task log of `noise_seed_E` and tests Threads 8 / 1.

