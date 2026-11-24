# methods_E_EMU_house_s1_s2_r3 — methods_E acquisition round (prompt 55; NOT submitted by the writer)

Arm `qnehvi`, seed_id 2, round 3,
acq qnehvi seed 20261209; bo-gp 60e6328236e745b3d34dc8cd704bb72888ae5d15; botorch
0.16.1; guardrail_mode constrain. Created 2026-11-24T07:46:03+00:00.

Rows are `oat_site = __ALL__` multi-site designs (contract 5): `mw_<site>` /
`u_<site>` at full precision, `pem_mw = sum mw`, `tier = bo`. The retrofit dict
`retrofit_gen_dict_<i>.json` lists every site with mw > 0 (a site at exactly 0
is ABSENT). Bid 40.0 $/MWh, full year from 01-01-2019.

| row | MW 110 | MW 140 | MW 146 | MW 163 | MW 270 | MW 274 | sum MW | u 110 | u 140 | u 146 | u 163 | u 270 | u 274 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 338.600 | 0.000 | 0.000 | 185.400 | 0.000 | 746.400 | 1270.400 | 1.00000 | 0.00000 | 0.00000 | 1.00000 | 0.00000 | 1.00000 |
| 2 | 0.000 | 88.243 | 0.000 | 185.400 | 579.000 | 746.400 | 1599.043 | 0.00000 | 0.35213 | 0.00000 | 1.00000 | 1.00000 | 1.00000 |
| 3 | 0.000 | 0.000 | 0.000 | 0.000 | 579.000 | 746.400 | 1325.400 | 0.00000 | 0.00000 | 0.00000 | 0.00000 | 1.00000 | 1.00000 |
| 4 | 338.600 | 0.000 | 0.000 | 0.000 | 0.000 | 746.400 | 1085.000 | 1.00000 | 0.00000 | 0.00000 | 0.00000 | 0.00000 | 1.00000 |
| 5 | 0.000 | 0.000 | 0.000 | 80.683 | 579.000 | 0.000 | 659.683 | 0.00000 | 0.00000 | 0.00000 | 0.43518 | 1.00000 | 0.00000 |
| 6 | 338.600 | 250.600 | 9.632 | 185.400 | 579.000 | 746.400 | 2109.632 | 1.00000 | 1.00000 | 0.03594 | 1.00000 | 1.00000 | 1.00000 |
| 7 | 93.247 | 0.000 | 0.000 | 185.400 | 579.000 | 0.000 | 857.647 | 0.27539 | 0.00000 | 0.00000 | 1.00000 | 1.00000 | 0.00000 |
| 8 | 338.600 | 250.600 | 79.117 | 185.400 | 579.000 | 746.400 | 2179.117 | 1.00000 | 1.00000 | 0.29521 | 1.00000 | 1.00000 | 1.00000 |

Submission: Kay runs `bash analysis/methods_E/submit_ready_E.sh` on the CRC
login node (generic `methods_E_array.sh` + `methods_E_collect.sh`, `-v WAVE=methods_E_EMU_house_s1_s2_r3`,
`-wd trial_0826/ercot/waves`, identity from `waves/GAP_DECISION.json` at run
time, every row `--full`, slim tables + `pool_full_metrics.json` + `COLLECTED`
committed, `*.csv.gz` left in storage). `predictions.csv` holds the pre-round
GP mean / total sd per objective (calibration gates C2 / C3 at grading).
