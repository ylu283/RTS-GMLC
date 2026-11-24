# methods_E_EMU_committed_s1_s3_r2 — methods_E acquisition round (prompt 55; NOT submitted by the writer)

Arm `qnehvi`, seed_id 3, round 2,
acq qnehvi seed 20261308; bo-gp 60e6328236e745b3d34dc8cd704bb72888ae5d15; botorch
0.16.1; guardrail_mode constrain. Created 2026-11-24T08:36:26+00:00.

Rows are `oat_site = __ALL__` multi-site designs (contract 5): `mw_<site>` /
`u_<site>` at full precision, `pem_mw = sum mw`, `tier = bo`. The retrofit dict
`retrofit_gen_dict_<i>.json` lists every site with mw > 0 (a site at exactly 0
is ABSENT). Bid 40.0 $/MWh, full year from 01-01-2019.

| row | MW 110 | MW 140 | MW 146 | MW 163 | MW 270 | MW 274 | sum MW | u 110 | u 140 | u 146 | u 163 | u 270 | u 274 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 73.300 | 0.000 | 0.000 | 185.400 | 579.000 | 0.000 | 837.700 | 0.21648 | 0.00000 | 0.00000 | 1.00000 | 1.00000 | 0.00000 |
| 2 | 46.266 | 0.000 | 0.000 | 35.595 | 579.000 | 0.000 | 660.861 | 0.13664 | 0.00000 | 0.00000 | 0.19199 | 1.00000 | 0.00000 |
| 3 | 0.000 | 250.600 | 74.823 | 185.400 | 579.000 | 746.400 | 1836.223 | 0.00000 | 1.00000 | 0.27919 | 1.00000 | 1.00000 | 1.00000 |
| 4 | 0.000 | 0.000 | 0.000 | 185.400 | 579.000 | 436.170 | 1200.570 | 0.00000 | 0.00000 | 0.00000 | 1.00000 | 1.00000 | 0.58436 |
| 5 | 167.340 | 250.600 | 196.738 | 185.400 | 579.000 | 746.400 | 2125.478 | 0.49421 | 1.00000 | 0.73410 | 1.00000 | 1.00000 | 1.00000 |
| 6 | 33.830 | 250.600 | 195.947 | 185.400 | 579.000 | 746.400 | 1991.178 | 0.09991 | 1.00000 | 0.73115 | 1.00000 | 1.00000 | 1.00000 |
| 7 | 0.000 | 0.000 | 0.000 | 185.400 | 56.199 | 746.400 | 987.999 | 0.00000 | 0.00000 | 0.00000 | 1.00000 | 0.09706 | 1.00000 |
| 8 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 746.400 | 746.400 | 0.00000 | 0.00000 | 0.00000 | 0.00000 | 0.00000 | 1.00000 |

Submission: Kay runs `bash analysis/methods_E/submit_ready_E.sh` on the CRC
login node (generic `methods_E_array.sh` + `methods_E_collect.sh`, `-v WAVE=methods_E_EMU_committed_s1_s3_r2`,
`-wd trial_0826/ercot/waves`, identity from `waves/GAP_DECISION.json` at run
time, every row `--full`, slim tables + `pool_full_metrics.json` + `COLLECTED`
committed, `*.csv.gz` left in storage). `predictions.csv` holds the pre-round
GP mean / total sd per objective (calibration gates C2 / C3 at grading).
