# methods_E_EMU_house_s1_s3_r2 — methods_E acquisition round (prompt 55; NOT submitted by the writer)

Arm `qnehvi`, seed_id 3, round 2,
acq qnehvi seed 20261308; bo-gp 60e6328236e745b3d34dc8cd704bb72888ae5d15; botorch
0.16.1; guardrail_mode constrain. Created 2026-11-24T07:46:28+00:00.

Rows are `oat_site = __ALL__` multi-site designs (contract 5): `mw_<site>` /
`u_<site>` at full precision, `pem_mw = sum mw`, `tier = bo`. The retrofit dict
`retrofit_gen_dict_<i>.json` lists every site with mw > 0 (a site at exactly 0
is ABSENT). Bid 40.0 $/MWh, full year from 01-01-2019.

| row | MW 110 | MW 140 | MW 146 | MW 163 | MW 270 | MW 274 | sum MW | u 110 | u 140 | u 146 | u 163 | u 270 | u 274 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.000 | 0.000 | 0.000 | 185.400 | 579.000 | 313.064 | 1077.464 | 0.00000 | 0.00000 | 0.00000 | 1.00000 | 1.00000 | 0.41943 |
| 2 | 0.000 | 250.600 | 0.000 | 185.400 | 579.000 | 0.000 | 1015.000 | 0.00000 | 1.00000 | 0.00000 | 1.00000 | 1.00000 | 0.00000 |
| 3 | 134.326 | 0.000 | 0.000 | 185.400 | 579.000 | 0.000 | 898.726 | 0.39671 | 0.00000 | 0.00000 | 1.00000 | 1.00000 | 0.00000 |
| 4 | 0.000 | 0.000 | 0.000 | 167.448 | 579.000 | 0.000 | 746.448 | 0.00000 | 0.00000 | 0.00000 | 0.90317 | 1.00000 | 0.00000 |
| 5 | 0.000 | 250.600 | 73.347 | 185.400 | 579.000 | 746.400 | 1834.747 | 0.00000 | 1.00000 | 0.27368 | 1.00000 | 1.00000 | 1.00000 |
| 6 | 0.000 | 0.000 | 0.000 | 185.400 | 579.000 | 506.172 | 1270.572 | 0.00000 | 0.00000 | 0.00000 | 1.00000 | 1.00000 | 0.67815 |
| 7 | 39.582 | 250.600 | 199.780 | 185.400 | 579.000 | 746.400 | 2000.762 | 0.11690 | 1.00000 | 0.74545 | 1.00000 | 1.00000 | 1.00000 |
| 8 | 338.600 | 250.600 | 120.344 | 185.400 | 579.000 | 746.400 | 2220.344 | 1.00000 | 1.00000 | 0.44905 | 1.00000 | 1.00000 | 1.00000 |

Submission: Kay runs `bash analysis/methods_E/submit_ready_E.sh` on the CRC
login node (generic `methods_E_array.sh` + `methods_E_collect.sh`, `-v WAVE=methods_E_EMU_house_s1_s3_r2`,
`-wd trial_0826/ercot/waves`, identity from `waves/GAP_DECISION.json` at run
time, every row `--full`, slim tables + `pool_full_metrics.json` + `COLLECTED`
committed, `*.csv.gz` left in storage). `predictions.csv` holds the pre-round
GP mean / total sd per objective (calibration gates C2 / C3 at grading).
