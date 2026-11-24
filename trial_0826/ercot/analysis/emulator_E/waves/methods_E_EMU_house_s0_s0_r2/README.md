# methods_E_EMU_house_s0_s0_r2 — methods_E acquisition round (prompt 55; NOT submitted by the writer)

Arm `qnehvi`, seed_id 0, round 2,
acq qnehvi seed 20261008; bo-gp 60e6328236e745b3d34dc8cd704bb72888ae5d15; botorch
0.16.1; guardrail_mode monitor. Created 2026-11-24T08:04:25+00:00.

Rows are `oat_site = __ALL__` multi-site designs (contract 5): `mw_<site>` /
`u_<site>` at full precision, `pem_mw = sum mw`, `tier = bo`. The retrofit dict
`retrofit_gen_dict_<i>.json` lists every site with mw > 0 (a site at exactly 0
is ABSENT). Bid 40.0 $/MWh, full year from 01-01-2019.

| row | MW 110 | MW 140 | MW 146 | MW 163 | MW 270 | MW 274 | sum MW | u 110 | u 140 | u 146 | u 163 | u 270 | u 274 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.000 | 0.000 | 0.000 | 167.308 | 579.000 | 0.000 | 746.308 | 0.00000 | 0.00000 | 0.00000 | 0.90242 | 1.00000 | 0.00000 |
| 2 | 139.839 | 0.000 | 0.000 | 185.400 | 579.000 | 0.000 | 904.239 | 0.41299 | 0.00000 | 0.00000 | 1.00000 | 1.00000 | 0.00000 |
| 3 | 0.000 | 0.000 | 0.000 | 185.400 | 579.000 | 465.635 | 1230.035 | 0.00000 | 0.00000 | 0.00000 | 1.00000 | 1.00000 | 0.62384 |
| 4 | 0.000 | 250.600 | 70.673 | 185.400 | 579.000 | 746.400 | 1832.073 | 0.00000 | 1.00000 | 0.26370 | 1.00000 | 1.00000 | 1.00000 |
| 5 | 202.518 | 250.600 | 206.392 | 185.400 | 579.000 | 746.400 | 2170.309 | 0.59810 | 1.00000 | 0.77012 | 1.00000 | 1.00000 | 1.00000 |
| 6 | 338.600 | 250.600 | 6.851 | 185.400 | 579.000 | 746.400 | 2106.851 | 1.00000 | 1.00000 | 0.02556 | 1.00000 | 1.00000 | 1.00000 |
| 7 | 0.000 | 86.365 | 0.000 | 185.400 | 579.000 | 746.400 | 1597.165 | 0.00000 | 0.34463 | 0.00000 | 1.00000 | 1.00000 | 1.00000 |
| 8 | 0.000 | 0.000 | 0.000 | 185.400 | 353.326 | 746.400 | 1285.126 | 0.00000 | 0.00000 | 0.00000 | 1.00000 | 0.61023 | 1.00000 |

Submission: Kay runs `bash analysis/methods_E/submit_ready_E.sh` on the CRC
login node (generic `methods_E_array.sh` + `methods_E_collect.sh`, `-v WAVE=methods_E_EMU_house_s0_s0_r2`,
`-wd trial_0826/ercot/waves`, identity from `waves/GAP_DECISION.json` at run
time, every row `--full`, slim tables + `pool_full_metrics.json` + `COLLECTED`
committed, `*.csv.gz` left in storage). `predictions.csv` holds the pre-round
GP mean / total sd per objective (calibration gates C2 / C3 at grading).
