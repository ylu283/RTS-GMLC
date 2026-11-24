# methods_E_EMU_house_s1_s2_r2 — methods_E acquisition round (prompt 55; NOT submitted by the writer)

Arm `qnehvi`, seed_id 2, round 2,
acq qnehvi seed 20261208; bo-gp 60e6328236e745b3d34dc8cd704bb72888ae5d15; botorch
0.16.1; guardrail_mode constrain. Created 2026-11-24T08:05:56+00:00.

Rows are `oat_site = __ALL__` multi-site designs (contract 5): `mw_<site>` /
`u_<site>` at full precision, `pem_mw = sum mw`, `tier = bo`. The retrofit dict
`retrofit_gen_dict_<i>.json` lists every site with mw > 0 (a site at exactly 0
is ABSENT). Bid 40.0 $/MWh, full year from 01-01-2019.

| row | MW 110 | MW 140 | MW 146 | MW 163 | MW 270 | MW 274 | sum MW | u 110 | u 140 | u 146 | u 163 | u 270 | u 274 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.000 | 0.000 | 0.000 | 185.400 | 579.000 | 371.954 | 1136.354 | 0.00000 | 0.00000 | 0.00000 | 1.00000 | 1.00000 | 0.49833 |
| 2 | 0.000 | 0.000 | 0.000 | 168.859 | 579.000 | 0.000 | 747.859 | 0.00000 | 0.00000 | 0.00000 | 0.91078 | 1.00000 | 0.00000 |
| 3 | 140.758 | 0.000 | 0.000 | 185.400 | 579.000 | 0.000 | 905.158 | 0.41571 | 0.00000 | 0.00000 | 1.00000 | 1.00000 | 0.00000 |
| 4 | 228.547 | 0.000 | 0.000 | 185.400 | 579.000 | 51.334 | 1044.281 | 0.67498 | 0.00000 | 0.00000 | 1.00000 | 1.00000 | 0.06878 |
| 5 | 0.000 | 250.600 | 73.915 | 185.400 | 579.000 | 746.400 | 1835.315 | 0.00000 | 1.00000 | 0.27580 | 1.00000 | 1.00000 | 1.00000 |
| 6 | 0.000 | 0.000 | 0.000 | 185.400 | 579.000 | 513.465 | 1277.865 | 0.00000 | 0.00000 | 0.00000 | 1.00000 | 1.00000 | 0.68792 |
| 7 | 337.375 | 250.600 | 124.762 | 185.400 | 579.000 | 746.400 | 2223.537 | 0.99638 | 1.00000 | 0.46553 | 1.00000 | 1.00000 | 1.00000 |
| 8 | 32.818 | 250.600 | 210.661 | 185.400 | 579.000 | 746.400 | 2004.879 | 0.09692 | 1.00000 | 0.78605 | 1.00000 | 1.00000 | 1.00000 |

Submission: Kay runs `bash analysis/methods_E/submit_ready_E.sh` on the CRC
login node (generic `methods_E_array.sh` + `methods_E_collect.sh`, `-v WAVE=methods_E_EMU_house_s1_s2_r2`,
`-wd trial_0826/ercot/waves`, identity from `waves/GAP_DECISION.json` at run
time, every row `--full`, slim tables + `pool_full_metrics.json` + `COLLECTED`
committed, `*.csv.gz` left in storage). `predictions.csv` holds the pre-round
GP mean / total sd per objective (calibration gates C2 / C3 at grading).
