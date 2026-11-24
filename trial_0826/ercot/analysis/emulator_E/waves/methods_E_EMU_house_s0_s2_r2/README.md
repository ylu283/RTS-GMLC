# methods_E_EMU_house_s0_s2_r2 — methods_E acquisition round (prompt 55; NOT submitted by the writer)

Arm `qnehvi`, seed_id 2, round 2,
acq qnehvi seed 20261208; bo-gp 60e6328236e745b3d34dc8cd704bb72888ae5d15; botorch
0.16.1; guardrail_mode monitor. Created 2026-11-24T07:45:35+00:00.

Rows are `oat_site = __ALL__` multi-site designs (contract 5): `mw_<site>` /
`u_<site>` at full precision, `pem_mw = sum mw`, `tier = bo`. The retrofit dict
`retrofit_gen_dict_<i>.json` lists every site with mw > 0 (a site at exactly 0
is ABSENT). Bid 40.0 $/MWh, full year from 01-01-2019.

| row | MW 110 | MW 140 | MW 146 | MW 163 | MW 270 | MW 274 | sum MW | u 110 | u 140 | u 146 | u 163 | u 270 | u 274 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.000 | 0.000 | 0.000 | 159.156 | 579.000 | 0.000 | 738.156 | 0.00000 | 0.00000 | 0.00000 | 0.85845 | 1.00000 | 0.00000 |
| 2 | 135.025 | 0.000 | 0.000 | 185.400 | 579.000 | 0.000 | 899.425 | 0.39877 | 0.00000 | 0.00000 | 1.00000 | 1.00000 | 0.00000 |
| 3 | 0.000 | 0.000 | 0.000 | 185.400 | 579.000 | 462.130 | 1226.530 | 0.00000 | 0.00000 | 0.00000 | 1.00000 | 1.00000 | 0.61915 |
| 4 | 338.600 | 0.000 | 0.000 | 185.400 | 579.000 | 746.400 | 1849.400 | 1.00000 | 0.00000 | 0.00000 | 1.00000 | 1.00000 | 1.00000 |
| 5 | 39.722 | 250.600 | 199.459 | 185.400 | 579.000 | 746.400 | 2000.581 | 0.11731 | 1.00000 | 0.74425 | 1.00000 | 1.00000 | 1.00000 |
| 6 | 188.618 | 250.600 | 205.743 | 185.400 | 579.000 | 746.400 | 2155.761 | 0.55705 | 1.00000 | 0.76770 | 1.00000 | 1.00000 | 1.00000 |
| 7 | 0.000 | 250.600 | 79.659 | 185.400 | 579.000 | 746.400 | 1841.059 | 0.00000 | 1.00000 | 0.29724 | 1.00000 | 1.00000 | 1.00000 |
| 8 | 0.000 | 0.000 | 0.000 | 0.000 | 579.000 | 746.400 | 1325.400 | 0.00000 | 0.00000 | 0.00000 | 0.00000 | 1.00000 | 1.00000 |

Submission: Kay runs `bash analysis/methods_E/submit_ready_E.sh` on the CRC
login node (generic `methods_E_array.sh` + `methods_E_collect.sh`, `-v WAVE=methods_E_EMU_house_s0_s2_r2`,
`-wd trial_0826/ercot/waves`, identity from `waves/GAP_DECISION.json` at run
time, every row `--full`, slim tables + `pool_full_metrics.json` + `COLLECTED`
committed, `*.csv.gz` left in storage). `predictions.csv` holds the pre-round
GP mean / total sd per objective (calibration gates C2 / C3 at grading).
