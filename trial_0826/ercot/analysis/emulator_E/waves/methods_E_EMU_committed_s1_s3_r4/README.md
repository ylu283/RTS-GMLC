# methods_E_EMU_committed_s1_s3_r4 — methods_E acquisition round (prompt 55; NOT submitted by the writer)

Arm `qnehvi`, seed_id 3, round 4,
acq qnehvi seed 20261310; bo-gp 60e6328236e745b3d34dc8cd704bb72888ae5d15; botorch
0.16.1; guardrail_mode constrain. Created 2026-11-24T08:36:47+00:00.

Rows are `oat_site = __ALL__` multi-site designs (contract 5): `mw_<site>` /
`u_<site>` at full precision, `pem_mw = sum mw`, `tier = bo`. The retrofit dict
`retrofit_gen_dict_<i>.json` lists every site with mw > 0 (a site at exactly 0
is ABSENT). Bid 40.0 $/MWh, full year from 01-01-2019.

| row | MW 110 | MW 140 | MW 146 | MW 163 | MW 270 | MW 274 | sum MW | u 110 | u 140 | u 146 | u 163 | u 270 | u 274 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.000 | 250.600 | 215.256 | 185.400 | 579.000 | 746.400 | 1976.656 | 0.00000 | 1.00000 | 0.80319 | 1.00000 | 1.00000 | 1.00000 |
| 2 | 0.000 | 0.000 | 0.000 | 108.578 | 579.000 | 0.000 | 687.578 | 0.00000 | 0.00000 | 0.00000 | 0.58564 | 1.00000 | 0.00000 |
| 3 | 338.600 | 250.600 | 147.324 | 101.637 | 579.000 | 746.400 | 2163.561 | 1.00000 | 1.00000 | 0.54972 | 0.54820 | 1.00000 | 1.00000 |
| 4 | 0.000 | 250.600 | 115.886 | 185.400 | 579.000 | 746.400 | 1877.286 | 0.00000 | 1.00000 | 0.43241 | 1.00000 | 1.00000 | 1.00000 |
| 5 | 0.000 | 250.600 | 0.000 | 0.000 | 0.000 | 746.400 | 997.000 | 0.00000 | 1.00000 | 0.00000 | 0.00000 | 0.00000 | 1.00000 |
| 6 | 338.600 | 0.000 | 0.000 | 185.400 | 579.000 | 746.400 | 1849.400 | 1.00000 | 0.00000 | 0.00000 | 1.00000 | 1.00000 | 1.00000 |
| 7 | 338.600 | 0.000 | 197.160 | 185.400 | 579.000 | 746.400 | 2046.560 | 1.00000 | 0.00000 | 0.73567 | 1.00000 | 1.00000 | 1.00000 |
| 8 | 189.911 | 250.600 | 236.500 | 181.851 | 579.000 | 746.400 | 2184.261 | 0.56087 | 1.00000 | 0.88246 | 0.98086 | 1.00000 | 1.00000 |

Submission: Kay runs `bash analysis/methods_E/submit_ready_E.sh` on the CRC
login node (generic `methods_E_array.sh` + `methods_E_collect.sh`, `-v WAVE=methods_E_EMU_committed_s1_s3_r4`,
`-wd trial_0826/ercot/waves`, identity from `waves/GAP_DECISION.json` at run
time, every row `--full`, slim tables + `pool_full_metrics.json` + `COLLECTED`
committed, `*.csv.gz` left in storage). `predictions.csv` holds the pre-round
GP mean / total sd per objective (calibration gates C2 / C3 at grading).
