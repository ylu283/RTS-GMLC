# methods_E_EMU_house_s1_s3_r4 — methods_E acquisition round (prompt 55; NOT submitted by the writer)

Arm `qnehvi`, seed_id 3, round 4,
acq qnehvi seed 20261310; bo-gp 60e6328236e745b3d34dc8cd704bb72888ae5d15; botorch
0.16.1; guardrail_mode constrain. Created 2026-11-24T07:46:47+00:00.

Rows are `oat_site = __ALL__` multi-site designs (contract 5): `mw_<site>` /
`u_<site>` at full precision, `pem_mw = sum mw`, `tier = bo`. The retrofit dict
`retrofit_gen_dict_<i>.json` lists every site with mw > 0 (a site at exactly 0
is ABSENT). Bid 40.0 $/MWh, full year from 01-01-2019.

| row | MW 110 | MW 140 | MW 146 | MW 163 | MW 270 | MW 274 | sum MW | u 110 | u 140 | u 146 | u 163 | u 270 | u 274 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 338.600 | 250.600 | 162.239 | 185.400 | 579.000 | 746.400 | 2262.239 | 1.00000 | 1.00000 | 0.60537 | 1.00000 | 1.00000 | 1.00000 |
| 2 | 0.000 | 0.000 | 0.000 | 185.400 | 459.162 | 0.000 | 644.562 | 0.00000 | 0.00000 | 0.00000 | 1.00000 | 0.79303 | 0.00000 |
| 3 | 9.152 | 250.600 | 197.814 | 185.400 | 579.000 | 746.400 | 1968.367 | 0.02703 | 1.00000 | 0.73811 | 1.00000 | 1.00000 | 1.00000 |
| 4 | 82.196 | 0.000 | 0.000 | 185.400 | 579.000 | 6.997 | 853.593 | 0.24275 | 0.00000 | 0.00000 | 1.00000 | 1.00000 | 0.00937 |
| 5 | 0.000 | 0.000 | 0.000 | 185.400 | 179.381 | 746.400 | 1111.181 | 0.00000 | 0.00000 | 0.00000 | 1.00000 | 0.30981 | 1.00000 |
| 6 | 0.000 | 0.000 | 0.000 | 185.400 | 579.000 | 404.618 | 1169.018 | 0.00000 | 0.00000 | 0.00000 | 1.00000 | 1.00000 | 0.54209 |
| 7 | 0.000 | 0.000 | 0.000 | 185.400 | 579.000 | 605.450 | 1369.850 | 0.00000 | 0.00000 | 0.00000 | 1.00000 | 1.00000 | 0.81116 |
| 8 | 0.000 | 150.371 | 0.000 | 185.400 | 579.000 | 746.400 | 1661.171 | 0.00000 | 0.60005 | 0.00000 | 1.00000 | 1.00000 | 1.00000 |

Submission: Kay runs `bash analysis/methods_E/submit_ready_E.sh` on the CRC
login node (generic `methods_E_array.sh` + `methods_E_collect.sh`, `-v WAVE=methods_E_EMU_house_s1_s3_r4`,
`-wd trial_0826/ercot/waves`, identity from `waves/GAP_DECISION.json` at run
time, every row `--full`, slim tables + `pool_full_metrics.json` + `COLLECTED`
committed, `*.csv.gz` left in storage). `predictions.csv` holds the pre-round
GP mean / total sd per objective (calibration gates C2 / C3 at grading).
