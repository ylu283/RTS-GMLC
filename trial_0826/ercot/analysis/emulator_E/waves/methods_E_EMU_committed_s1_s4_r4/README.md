# methods_E_EMU_committed_s1_s4_r4 — methods_E acquisition round (prompt 55; NOT submitted by the writer)

Arm `qnehvi`, seed_id 4, round 4,
acq qnehvi seed 20261410; bo-gp 60e6328236e745b3d34dc8cd704bb72888ae5d15; botorch
0.16.1; guardrail_mode constrain. Created 2026-11-24T08:37:24+00:00.

Rows are `oat_site = __ALL__` multi-site designs (contract 5): `mw_<site>` /
`u_<site>` at full precision, `pem_mw = sum mw`, `tier = bo`. The retrofit dict
`retrofit_gen_dict_<i>.json` lists every site with mw > 0 (a site at exactly 0
is ABSENT). Bid 40.0 $/MWh, full year from 01-01-2019.

| row | MW 110 | MW 140 | MW 146 | MW 163 | MW 270 | MW 274 | sum MW | u 110 | u 140 | u 146 | u 163 | u 270 | u 274 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.000 | 250.600 | 35.752 | 185.400 | 579.000 | 746.400 | 1797.152 | 0.00000 | 1.00000 | 0.13340 | 1.00000 | 1.00000 | 1.00000 |
| 2 | 338.600 | 0.000 | 14.823 | 185.400 | 579.000 | 746.400 | 1864.223 | 1.00000 | 0.00000 | 0.05531 | 1.00000 | 1.00000 | 1.00000 |
| 3 | 0.000 | 250.600 | 0.000 | 29.527 | 579.000 | 746.400 | 1605.527 | 0.00000 | 1.00000 | 0.00000 | 0.15926 | 1.00000 | 1.00000 |
| 4 | 0.000 | 250.600 | 0.000 | 69.553 | 579.000 | 746.400 | 1645.553 | 0.00000 | 1.00000 | 0.00000 | 0.37515 | 1.00000 | 1.00000 |
| 5 | 265.021 | 0.000 | 0.000 | 185.400 | 579.000 | 0.000 | 1029.421 | 0.78270 | 0.00000 | 0.00000 | 1.00000 | 1.00000 | 0.00000 |
| 6 | 0.000 | 250.600 | 0.000 | 0.000 | 0.000 | 746.400 | 997.000 | 0.00000 | 1.00000 | 0.00000 | 0.00000 | 0.00000 | 1.00000 |
| 7 | 0.000 | 0.000 | 0.000 | 185.400 | 579.000 | 421.381 | 1185.781 | 0.00000 | 0.00000 | 0.00000 | 1.00000 | 1.00000 | 0.56455 |
| 8 | 0.000 | 0.000 | 134.925 | 185.400 | 579.000 | 0.000 | 899.325 | 0.00000 | 0.00000 | 0.50345 | 1.00000 | 1.00000 | 0.00000 |

Submission: Kay runs `bash analysis/methods_E/submit_ready_E.sh` on the CRC
login node (generic `methods_E_array.sh` + `methods_E_collect.sh`, `-v WAVE=methods_E_EMU_committed_s1_s4_r4`,
`-wd trial_0826/ercot/waves`, identity from `waves/GAP_DECISION.json` at run
time, every row `--full`, slim tables + `pool_full_metrics.json` + `COLLECTED`
committed, `*.csv.gz` left in storage). `predictions.csv` holds the pre-round
GP mean / total sd per objective (calibration gates C2 / C3 at grading).
