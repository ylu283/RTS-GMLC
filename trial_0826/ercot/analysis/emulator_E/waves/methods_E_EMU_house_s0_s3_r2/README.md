# methods_E_EMU_house_s0_s3_r2 — methods_E acquisition round (prompt 55; NOT submitted by the writer)

Arm `qnehvi`, seed_id 3, round 2,
acq qnehvi seed 20261308; bo-gp 60e6328236e745b3d34dc8cd704bb72888ae5d15; botorch
0.16.1; guardrail_mode monitor. Created 2026-11-24T07:46:00+00:00.

Rows are `oat_site = __ALL__` multi-site designs (contract 5): `mw_<site>` /
`u_<site>` at full precision, `pem_mw = sum mw`, `tier = bo`. The retrofit dict
`retrofit_gen_dict_<i>.json` lists every site with mw > 0 (a site at exactly 0
is ABSENT). Bid 40.0 $/MWh, full year from 01-01-2019.

| row | MW 110 | MW 140 | MW 146 | MW 163 | MW 270 | MW 274 | sum MW | u 110 | u 140 | u 146 | u 163 | u 270 | u 274 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.000 | 0.000 | 0.000 | 144.249 | 579.000 | 0.000 | 723.249 | 0.00000 | 0.00000 | 0.00000 | 0.77804 | 1.00000 | 0.00000 |
| 2 | 0.000 | 250.600 | 0.000 | 185.400 | 579.000 | 0.000 | 1015.000 | 0.00000 | 1.00000 | 0.00000 | 1.00000 | 1.00000 | 0.00000 |
| 3 | 0.000 | 250.600 | 73.470 | 185.400 | 579.000 | 746.400 | 1834.870 | 0.00000 | 1.00000 | 0.27414 | 1.00000 | 1.00000 | 1.00000 |
| 4 | 0.000 | 0.000 | 0.000 | 185.400 | 579.000 | 503.110 | 1267.510 | 0.00000 | 0.00000 | 0.00000 | 1.00000 | 1.00000 | 0.67405 |
| 5 | 38.546 | 250.600 | 202.425 | 185.400 | 579.000 | 746.400 | 2002.371 | 0.11384 | 1.00000 | 0.75532 | 1.00000 | 1.00000 | 1.00000 |
| 6 | 129.444 | 0.000 | 0.000 | 185.400 | 579.000 | 0.000 | 893.844 | 0.38229 | 0.00000 | 0.00000 | 1.00000 | 1.00000 | 0.00000 |
| 7 | 191.105 | 250.600 | 200.143 | 185.400 | 579.000 | 746.400 | 2152.648 | 0.56440 | 1.00000 | 0.74680 | 1.00000 | 1.00000 | 1.00000 |
| 8 | 0.000 | 89.564 | 0.000 | 185.400 | 579.000 | 746.400 | 1600.364 | 0.00000 | 0.35740 | 0.00000 | 1.00000 | 1.00000 | 1.00000 |

Submission: Kay runs `bash analysis/methods_E/submit_ready_E.sh` on the CRC
login node (generic `methods_E_array.sh` + `methods_E_collect.sh`, `-v WAVE=methods_E_EMU_house_s0_s3_r2`,
`-wd trial_0826/ercot/waves`, identity from `waves/GAP_DECISION.json` at run
time, every row `--full`, slim tables + `pool_full_metrics.json` + `COLLECTED`
committed, `*.csv.gz` left in storage). `predictions.csv` holds the pre-round
GP mean / total sd per objective (calibration gates C2 / C3 at grading).
