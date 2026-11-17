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

| perturbed key | design | ref key | PEM MW | ref PEM MW | sign | delta_rel |
|---|---|---|---|---|---|---|
| noise_v3/A:5 | D1 | noise_v3/A:1 | 520.0195 | 519.5000 | +1 | 0.001 |
| noise_v3/A:6 | D2 | noise_v3/A:2 | 900.7999 | 899.9000 | +1 | 0.001 |
| noise_v3/A:7 | D3 | noise_v3/A:3 | 133.8660 | 134.0000 | -1 | 0.001 |
| noise_v3/A:8 | D4 | noise_v3/A:4 | 2427.5700 | 2430.0000 | -1 | 0.001 |
| noise_v3/B:5 | D1 | noise_v3/B:1 | 518.9805 | 519.5000 | -1 | 0.001 |
| noise_v3/B:6 | D2 | noise_v3/B:2 | 899.0001 | 899.9000 | -1 | 0.001 |
| noise_v3/B:7 | D3 | noise_v3/B:3 | 134.1340 | 134.0000 | +1 | 0.001 |
| noise_v3/B:8 | D4 | noise_v3/B:4 | 2425.1400 | 2430.0000 | -1 | 0.002 |

| id | name | unit | n | ruler_j (median |Δ|) | min | max | status | |Δ| values |
|---|---|---|---|---|---|---|---|---|
| V1 | true curtailment | MWh | 8 | 1949 | 0 | 1.227e+04 | RULER | 1.227e+04, 0, 3072, 2266, 149.4, 0, 2574, 1632 |
| E1 | total cost | $ | 8 | 2.183e+05 | 0 | 1.862e+06 | RULER | 2.271e+05, 0, 3.911e+04, 4.085e+05, 2.367e+05, 0, 2.095e+05, 1.862e+06 |
| X1 | CO2 (fuel-factor) | t | 8 | 4359 | 0 | 2.245e+04 | RULER | 6693, 0, 2.245e+04, 4417, 1.712e+04, 0, 4302, 2490 |
| R4 | thermal starts | count | 8 | 20 | 0 | 90 | RULER | 10, 0, 37, 20, 90, 0, 20, 63 |
| N1 | congested line-hours | line-h | 8 | 15 | 0 | 65 | RULER | 9, 0, 65, 15, 55, 0, 15, 32 |
| E4 | total payments (consumer side) | $ | 8 | 1.237e+06 | 0 | 5.214e+06 | RULER | 1.310e+06, 0, 4.092e+05, 5.214e+06, 2.752e+06, 0, 1.165e+06, 3.198e+06 |
| R2 | reserve shortfall | MWh | 8 | 23.06 | 0 | 58.87 | RULER | 34.71, 0, 21.87, 28.27, 20.99, 0, 24.24, 58.87 |
| R7 | committed capacity-hours | MWh | 8 | 6.844e+04 | 0 | 1.235e+05 | RULER | 1.235e+05, 0, 6.791e+04, 1.032e+05, 1.018e+05, 0, 5.018e+04, 6.898e+04 |
| N4 | pocket-120 congested line-hours | line-h | 8 | 8.5 | 0 | 17 | RULER | 1, 0, 5, 16, 17, 0, 12, 14 |
| N5 | congestion spread | $/MWh | 8 | 0.0402 | 0 | 0.09934 | RULER | 0.0421, 0, 0.06172, 0.0285, 0.06711, 0, 0.0383, 0.09934 |
| E6 | VRE energy payments | $ | 8 | 5.521e+05 | 0 | 1.555e+06 | RULER | 3.619e+05, 0, 1.555e+06, 7.857e+05, 5.590e+05, 0, 1.365e+06, 5.452e+05 |
| R5 | start/stop ramping | MW | 8 | 2896 | 0 | 8808 | RULER | 5414, 0, 7655, 1945, 3847, 0, 297.1, 8808 |
| N3 | flow violation | MWh | 8 | 2.577 | 0 | 7.038 | RULER | 6.042, 0, 5.003, 0.8888, 0.3435, 0, 7.038, 4.265 |
| E2 | fixed (commitment) cost | $ | 8 | 6.558e+05 | 0 | 1.555e+06 | RULER | 5.780e+05, 0, 1.003e+06, 1.555e+06, 6.768e+05, 0, 9.974e+05, 6.348e+05 |
| R6 | nominal ramping | MW | 8 | 9842 | 0 | 5.681e+04 | RULER | 1.132e+04, 0, 275.5, 2.393e+04, 8361, 0, 5.681e+04, 5.583e+04 |
| N2 | congested lines | count | 8 | 0 | 0 | 2 | RULER=0 | 1, 0, 2, 0, 0, 0, 0, 1 |
| E3 | variable cost | $ | 8 | 8.507e+05 | 0 | 1.964e+06 | RULER | 3.510e+05, 0, 1.043e+06, 1.964e+06, 9.135e+05, 0, 7.879e+05, 1.227e+06 |
| R8 | committed unit-hours | unit-h | 8 | 299 | 0 | 740 | RULER | 520, 0, 740, 129, 424, 0, 174, 737 |
| E7 | mean settlement price (energy) | $/MWh | 8 | 0.002055 | 0 | 0.01083 | RULER | 0.002143, 0, 0.01083, 0.005022, 0.001968, 0, 0.005562, 0.001399 |
| E8 | LMP dispersion | $/MWh | 8 | 0.07325 | 0 | 0.1707 | RULER | 0.07843, 0, 0.1707, 0.07506, 0.06881, 0, 0.07144, 0.1009 |
| E9 | scarcity bus-hours | count | 8 | 0 | 0 | 0 | RULER=0 | 0, 0, 0, 0, 0, 0, 0, 0 |
| V2 | renewables penetration | % | 8 | 4.715e-04 | 0 | 0.003165 | RULER | 0.003165, 0, 5.180e-04, 5.900e-04, 5.760e-04, 0, 3.320e-04, 4.250e-04 |
| V3 | PEM-twin delivered share | fraction | 8 | 2.338e-06 | 0 | 2.318e-05 | RULER | 2.318e-05, 0, 4.676e-06, 0, 5.605e-06, 0, 7.145e-06, 0 |
| E5 | uplift payments | $ | 8 | 0 | 0 | 0 | RULER=0 | 0, 0, 0, 0, 0, 0, 0, 0 |
| R1 | load shed | MWh | 8 | 0 | 0 | 0 | RULER=0 | 0, 0, 0, 0, 0, 0, 0, 0 |
| R3 | over generation | MWh | 8 | 0 | 0 | 0 | RULER=0 | 0, 0, 0, 0, 0, 0, 0, 0 |
| D1 | H2 electricity | MWh | 6 | 601.2 | 0 | 2360 | RULER | 120.7, 0, 1082, 2360, 0, 1300 |
| D2 | PEM utilization | fraction | 6 | 2.821e-04 | 1.301e-04 | 6.744e-04 | RULER | 6.744e-04, 2.818e-04, 2.057e-04, 1.301e-04, 2.824e-04, 3.907e-04 |

`RULER=0` candidates (gradable): N2, E9 — readable iff |Δ| >= 1 natural unit (prompt 57 section 3 A4); continuous candidates report the raw Δ with the tag.
`RULER UNAVAILABLE` (gradable): none.
Readable means, in exactly these words: "exceeds twice the median response to a 0.1 % input perturbation at the prompt-52 designs." An effect that fails reads "not readable above the perturbation response", never "zero".

## 4. Per-level and pooled sd of the perturbed population; variance-ratio trigger

Level = design. Per-level sd = sd of {exact, perturbed copies} of that design (ddof 1, df = number of perturbed copies). Pooled sd = sqrt(Σ df_i s_i² / Σ df_i) with Satterthwaite df = (Σ df_i s_i²)² / Σ (df_i s_i²)² / df_i. CIs are chi-square 95 %. Trigger per objective: F test of max s² / min s² at alpha = 0.05 AND point ratio > 3. A non-firing trigger reads "not detectable at this df", never "homoscedastic confirmed" (prompt 52 section 3 precision budget).

**Family-wise disclosure:** 22 gradable candidates are tested at alpha = 0.05 each with no family-wise correction; a false trigger only replaces a scalar sd by per-level sds (conservative), so none is applied.

| id | per-level sd (df) [95 % CI] | pooled sd | Satterthwaite df | pooled 95 % CI | ratio | p | verdict |
|---|---|---|---|---|---|---|---|
| V1 | D1 7040 (2) [3665, 4.424e+04]; D2 0 (2) [0, 0]; D3 2826 (2) [1472, 1.776e+04]; D4 1958 (2) [1019, 1.231e+04] | 3917 | 2.97 | [2215, 1.475e+04] | inf | 0 | TRIGGER: a level has sd 0 and another sd > 0 (ratio undefined); scalar sd rejected per objective |
| E1 | D1 2.319e+05 (2) [1.207e+05, 1.458e+06]; D2 0 (2) [0, 0]; D3 1.337e+05 (2) [6.961e+04, 8.403e+05]; D4 9.786e+05 (2) [5.095e+05, 6.150e+06] | 5.073e+05 | 2.3 | [2.721e+05, 2.593e+06] | inf | 0 | TRIGGER: a level has sd 0 and another sd > 0 (ratio undefined); scalar sd rejected per objective |
| X1 | D1 1.228e+04 (2) [6394, 7.718e+04]; D2 0 (2) [0, 0]; D3 1.191e+04 (2) [6203, 7.487e+04]; D4 2215 (2) [1153, 1.392e+04] | 8626 | 4.13 | [5199, 2.419e+04] | inf | 0 | TRIGGER: a level has sd 0 and another sd > 0 (ratio undefined); scalar sd rejected per objective |
| R4 | D1 49.33 (2) [25.68, 310]; D2 0 (2) [0, 0]; D3 28.92 (2) [15.06, 181.8]; D4 32.19 (2) [16.76, 202.3] | 32.81 | 4.82 | [20.35, 82.42] | inf | 0 | TRIGGER: a level has sd 0 and another sd > 0 (ratio undefined); scalar sd rejected per objective |
| N1 | D1 34.65 (2) [18.04, 217.7]; D2 0 (2) [0, 0]; D3 34.03 (2) [17.72, 213.9]; D4 16.01 (2) [8.336, 100.6] | 25.57 | 4.8 | [15.84, 64.39] | inf | 0 | TRIGGER: a level has sd 0 and another sd > 0 (ratio undefined); scalar sd rejected per objective |
| E4 | D1 2.073e+06 (2) [1.079e+06, 1.303e+07]; D2 0 (2) [0, 0]; D3 8.166e+05 (2) [4.251e+05, 5.132e+06]; D4 2.629e+06 (2) [1.369e+06, 1.652e+07] | 1.723e+06 | 4.23 | [1.043e+06, 4.744e+06] | inf | 0 | TRIGGER: a level has sd 0 and another sd > 0 (ratio undefined); scalar sd rejected per objective |
| R2 | D1 28.13 (2) [14.64, 176.8]; D2 0 (2) [0, 0]; D3 13.36 (2) [6.958, 83.99]; D4 44.46 (2) [23.15, 279.4] | 27.14 | 3.8 | [16.11, 81.21] | inf | 0 | TRIGGER: a level has sd 0 and another sd > 0 (ratio undefined); scalar sd rejected per objective |
| R7 | D1 6.595e+04 (2) [3.434e+04, 4.145e+05]; D2 0 (2) [0, 0]; D3 3.522e+04 (2) [1.834e+04, 2.214e+05]; D4 8.664e+04 (2) [4.511e+04, 5.445e+05] | 5.722e+04 | 4.47 | [3.499e+04, 1.514e+05] | inf | 0 | TRIGGER: a level has sd 0 and another sd > 0 (ratio undefined); scalar sd rejected per objective |
| N4 | D1 10.12 (2) [5.267, 63.58]; D2 0 (2) [0, 0]; D3 6.028 (2) [3.138, 37.88]; D4 15.01 (2) [7.816, 94.34] | 9.539 | 4.24 | [5.777, 26.24] | inf | 0 | TRIGGER: a level has sd 0 and another sd > 0 (ratio undefined); scalar sd rejected per objective |
| N5 | D1 0.05508 (2) [0.02868, 0.3462]; D2 0 (2) [0, 0]; D3 0.05047 (2) [0.02628, 0.3172]; D4 0.05115 (2) [0.02663, 0.3215] | 0.04527 | 5.96 | [0.02914, 0.1] | inf | 0 | TRIGGER: a level has sd 0 and another sd > 0 (ratio undefined); scalar sd rejected per objective |
| E6 | D1 4.640e+05 (2) [2.416e+05, 2.916e+06]; D2 0 (2) [0, 0]; D3 8.482e+05 (2) [4.416e+05, 5.330e+06]; D4 4.026e+05 (2) [2.096e+05, 2.530e+06] | 5.236e+05 | 4.08 | [3.148e+05, 1.483e+06] | inf | 0 | TRIGGER: a level has sd 0 and another sd > 0 (ratio undefined); scalar sd rejected per objective |
| R5 | D1 2786 (2) [1450, 1.751e+04]; D2 0 (2) [0, 0]; D3 4336 (2) [2258, 2.725e+04]; D4 4627 (2) [2409, 2.908e+04] | 3463 | 5.28 | [2183, 8212] | inf | 0 | TRIGGER: a level has sd 0 and another sd > 0 (ratio undefined); scalar sd rejected per objective |
| N3 | D1 3.394 (2) [1.767, 21.33]; D2 0 (2) [0, 0]; D3 3.622 (2) [1.886, 22.76]; D4 2.25 (2) [1.172, 14.14] | 2.725 | 5.34 | [1.721, 6.415] | inf | 0 | TRIGGER: a level has sd 0 and another sd > 0 (ratio undefined); scalar sd rejected per objective |
| E2 | D1 3.656e+05 (2) [1.903e+05, 2.298e+06]; D2 0 (2) [0, 0]; D3 5.776e+05 (2) [3.007e+05, 3.630e+06]; D4 1.127e+06 (2) [5.866e+05, 7.081e+06] | 6.589e+05 | 3.47 | [3.841e+05, 2.137e+06] | inf | 0 | TRIGGER: a level has sd 0 and another sd > 0 (ratio undefined); scalar sd rejected per objective |
| R6 | D1 9879 (2) [5143, 6.208e+04]; D2 0 (2) [0, 0]; D3 3.288e+04 (2) [1.712e+04, 2.067e+05]; D4 2.801e+04 (2) [1.458e+04, 1.760e+05] | 2.215e+04 | 4.3 | [1.345e+04, 6.029e+04] | inf | 0 | TRIGGER: a level has sd 0 and another sd > 0 (ratio undefined); scalar sd rejected per objective |
| N2 | D1 0.5774 (2) [0.3006, 3.628]; D2 0 (2) [0, 0]; D3 1.155 (2) [0.6012, 7.257]; D4 0.5774 (2) [0.3006, 3.628] | 0.7071 | 4 | [0.4237, 2.032] | inf | 0 | TRIGGER: a level has sd 0 and another sd > 0 (ratio undefined); scalar sd rejected per objective |
| E3 | D1 4.608e+05 (2) [2.399e+05, 2.896e+06]; D2 0 (2) [0, 0]; D3 5.435e+05 (2) [2.830e+05, 3.416e+06]; D4 9.920e+05 (2) [5.165e+05, 6.234e+06] | 6.107e+05 | 4.04 | [3.666e+05, 1.740e+06] | inf | 0 | TRIGGER: a level has sd 0 and another sd > 0 (ratio undefined); scalar sd rejected per objective |
| R8 | D1 472.8 (2) [246.2, 2972]; D2 0 (2) [0, 0]; D3 386.9 (2) [201.5, 2432]; D4 393.6 (2) [204.9, 2474] | 363.4 | 5.79 | [232.7, 816.2] | inf | 0 | TRIGGER: a level has sd 0 and another sd > 0 (ratio undefined); scalar sd rejected per objective |
| E7 | D1 0.00119 (2) [6.195e-04, 0.007477]; D2 0 (2) [0, 0]; D3 0.005417 (2) [0.002821, 0.03405]; D4 0.002592 (2) [0.001349, 0.01629] | 0.003061 | 3.09 | [0.001745, 0.01106] | inf | 0 | TRIGGER: a level has sd 0 and another sd > 0 (ratio undefined); scalar sd rejected per objective |
| E8 | D1 0.07367 (2) [0.03836, 0.463]; D2 0 (2) [0, 0]; D3 0.08575 (2) [0.04465, 0.5389]; D4 0.05242 (2) [0.02729, 0.3295] | 0.06231 | 5.3 | [0.03929, 0.1474] | inf | 0 | TRIGGER: a level has sd 0 and another sd > 0 (ratio undefined); scalar sd rejected per objective |
| E9 | D1 0 (2) [0, 0]; D2 0 (2) [0, 0]; D3 0 (2) [0, 0]; D4 0 (2) [0, 0] | 0 | 8 | [0, 0] | n/a | n/a | all levels sd 0 (exact zeros): not detectable at this df |
| V2 | D1 0.002014 (2) [0.001049, 0.01266]; D2 0 (2) [0, 0]; D3 4.284e-04 (2) [2.230e-04, 0.002692]; D4 5.097e-04 (2) [2.654e-04, 0.003204] | 0.001061 | 2.45 | [5.763e-04, 0.005006] | inf | 0 | TRIGGER: a level has sd 0 and another sd > 0 (ratio undefined); scalar sd rejected per objective |
| V3 | D1 1.210e-05 (2) [6.298e-06, 7.602e-05]; D2 0 (2) [0, 0]; D3 5.953e-06 (2) [3.100e-06, 3.742e-05]; D4 0 (2) [0, 0] | 6.741e-06 | 2.92 | [3.797e-06, 2.591e-05] | inf | 0 | TRIGGER: a level has sd 0 and another sd > 0 (ratio undefined); scalar sd rejected per objective |
| E5 | D1 0 (2) [0, 0]; D2 0 (2) [0, 0]; D3 0 (2) [0, 0]; D4 0 (2) [0, 0] | 0 | 8 | [0, 0] | n/a | n/a | all levels sd 0 (exact zeros): not detectable at this df |
| R1 | D1 0 (2) [0, 0]; D2 0 (2) [0, 0]; D3 0 (2) [0, 0]; D4 0 (2) [0, 0] | 0 | 8 | [0, 0] | n/a | n/a | all levels sd 0 (exact zeros): not detectable at this df |
| R3 | D1 0 (2) [0, 0]; D2 0 (2) [0, 0]; D3 0 (2) [0, 0]; D4 0 (2) [0, 0] | 0 | 8 | [0, 0] | n/a | n/a | all levels sd 0 (exact zeros): not detectable at this df |
| D1 | D1 1329 (2) [692, 8353]; D2 0 (2) [0, 0]; D3 1192 (2) [620.7, 7493]; D4 n/a (0) [n/a, n/a] | 1031 | 3.95 | [616.2, 2989] | inf | 0 | TRIGGER: a level has sd 0 and another sd > 0 (ratio undefined); scalar sd rejected per objective |
| D2 | D1 4.318e-04 (2) [2.248e-04, 0.002714]; D2 2.821e-04 (2) [1.469e-04, 0.001773]; D3 3.030e-04 (2) [1.577e-04, 0.001904]; D4 n/a (0) [n/a, n/a] | 3.454e-04 | 5.17 | [2.169e-04, 8.293e-04] | 2.34 | 0.299 | not detectable at this df (ratio 2.34, p = 0.299; df 2/2) |

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

