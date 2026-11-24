# methods_E_EMU_house_s1_s3_r1 — methods_E acquisition round (prompt 55; NOT submitted by the writer)

Arm `qnehvi`, seed_id 3, round 1,
acq qnehvi seed 20261307; bo-gp 60e6328236e745b3d34dc8cd704bb72888ae5d15; botorch
0.16.1; guardrail_mode monitor. Created 2026-11-24T07:46:20+00:00.

Rows are `oat_site = __ALL__` multi-site designs (contract 5): `mw_<site>` /
`u_<site>` at full precision, `pem_mw = sum mw`, `tier = bo`. The retrofit dict
`retrofit_gen_dict_<i>.json` lists every site with mw > 0 (a site at exactly 0
is ABSENT). Bid 40.0 $/MWh, full year from 01-01-2019.

| row | MW 110 | MW 140 | MW 146 | MW 163 | MW 270 | MW 274 | sum MW | u 110 | u 140 | u 146 | u 163 | u 270 | u 274 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 45.641 | 0.000 | 0.000 | 185.400 | 579.000 | 0.000 | 810.041 | 0.13479 | 0.00000 | 0.00000 | 1.00000 | 1.00000 | 0.00000 |
| 2 | 0.000 | 250.600 | 161.119 | 185.400 | 579.000 | 746.400 | 1922.519 | 0.00000 | 1.00000 | 0.60119 | 1.00000 | 1.00000 | 1.00000 |
| 3 | 338.600 | 0.000 | 0.000 | 185.400 | 579.000 | 0.000 | 1103.000 | 1.00000 | 0.00000 | 0.00000 | 1.00000 | 1.00000 | 0.00000 |
| 4 | 0.000 | 0.000 | 0.000 | 185.400 | 579.000 | 746.400 | 1510.800 | 0.00000 | 0.00000 | 0.00000 | 1.00000 | 1.00000 | 1.00000 |
| 5 | 97.573 | 250.600 | 218.932 | 185.400 | 579.000 | 746.400 | 2077.905 | 0.28817 | 1.00000 | 0.81691 | 1.00000 | 1.00000 | 1.00000 |
| 6 | 0.000 | 250.600 | 0.000 | 185.400 | 579.000 | 746.400 | 1761.400 | 0.00000 | 1.00000 | 0.00000 | 1.00000 | 1.00000 | 1.00000 |
| 7 | 0.000 | 0.000 | 0.000 | 185.400 | 0.000 | 746.400 | 931.800 | 0.00000 | 0.00000 | 0.00000 | 1.00000 | 0.00000 | 1.00000 |
| 8 | 0.000 | 0.000 | 0.000 | 185.400 | 258.556 | 746.400 | 1190.356 | 0.00000 | 0.00000 | 0.00000 | 1.00000 | 0.44656 | 1.00000 |

Submission: Kay runs `bash analysis/methods_E/submit_ready_E.sh` on the CRC
login node (generic `methods_E_array.sh` + `methods_E_collect.sh`, `-v WAVE=methods_E_EMU_house_s1_s3_r1`,
`-wd trial_0826/ercot/waves`, identity from `waves/GAP_DECISION.json` at run
time, every row `--full`, slim tables + `pool_full_metrics.json` + `COLLECTED`
committed, `*.csv.gz` left in storage). `predictions.csv` holds the pre-round
GP mean / total sd per objective (calibration gates C2 / C3 at grading).
