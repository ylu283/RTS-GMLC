# methods_E_EMU_house_s1_s4_r4 — methods_E acquisition round (prompt 55; NOT submitted by the writer)

Arm `qnehvi`, seed_id 4, round 4,
acq qnehvi seed 20261410; bo-gp 60e6328236e745b3d34dc8cd704bb72888ae5d15; botorch
0.16.1; guardrail_mode constrain. Created 2026-11-24T08:07:23+00:00.

Rows are `oat_site = __ALL__` multi-site designs (contract 5): `mw_<site>` /
`u_<site>` at full precision, `pem_mw = sum mw`, `tier = bo`. The retrofit dict
`retrofit_gen_dict_<i>.json` lists every site with mw > 0 (a site at exactly 0
is ABSENT). Bid 40.0 $/MWh, full year from 01-01-2019.

| row | MW 110 | MW 140 | MW 146 | MW 163 | MW 270 | MW 274 | sum MW | u 110 | u 140 | u 146 | u 163 | u 270 | u 274 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.000 | 0.000 | 0.000 | 185.400 | 579.000 | 237.199 | 1001.599 | 0.00000 | 0.00000 | 0.00000 | 1.00000 | 1.00000 | 0.31779 |
| 2 | 0.000 | 0.000 | 0.000 | 185.400 | 579.000 | 167.049 | 931.449 | 0.00000 | 0.00000 | 0.00000 | 1.00000 | 1.00000 | 0.22381 |
| 3 | 338.600 | 0.000 | 0.000 | 185.400 | 579.000 | 746.400 | 1849.400 | 1.00000 | 0.00000 | 0.00000 | 1.00000 | 1.00000 | 1.00000 |
| 4 | 205.419 | 250.600 | 229.152 | 185.400 | 579.000 | 746.400 | 2195.971 | 0.60667 | 1.00000 | 0.85505 | 1.00000 | 1.00000 | 1.00000 |
| 5 | 0.000 | 250.600 | 116.044 | 185.400 | 579.000 | 746.400 | 1877.444 | 0.00000 | 1.00000 | 0.43300 | 1.00000 | 1.00000 | 1.00000 |
| 6 | 0.000 | 0.000 | 0.000 | 185.400 | 579.000 | 370.036 | 1134.436 | 0.00000 | 0.00000 | 0.00000 | 1.00000 | 1.00000 | 0.49576 |
| 7 | 0.000 | 250.600 | 34.959 | 185.400 | 579.000 | 746.400 | 1796.359 | 0.00000 | 1.00000 | 0.13045 | 1.00000 | 1.00000 | 1.00000 |
| 8 | 0.000 | 0.000 | 0.000 | 185.400 | 579.000 | 572.905 | 1337.305 | 0.00000 | 0.00000 | 0.00000 | 1.00000 | 1.00000 | 0.76756 |

Submission: Kay runs `bash analysis/methods_E/submit_ready_E.sh` on the CRC
login node (generic `methods_E_array.sh` + `methods_E_collect.sh`, `-v WAVE=methods_E_EMU_house_s1_s4_r4`,
`-wd trial_0826/ercot/waves`, identity from `waves/GAP_DECISION.json` at run
time, every row `--full`, slim tables + `pool_full_metrics.json` + `COLLECTED`
committed, `*.csv.gz` left in storage). `predictions.csv` holds the pre-round
GP mean / total sd per objective (calibration gates C2 / C3 at grading).
