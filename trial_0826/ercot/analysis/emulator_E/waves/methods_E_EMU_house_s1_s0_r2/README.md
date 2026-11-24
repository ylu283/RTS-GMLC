# methods_E_EMU_house_s1_s0_r2 — methods_E acquisition round (prompt 55; NOT submitted by the writer)

Arm `qnehvi`, seed_id 0, round 2,
acq qnehvi seed 20261008; bo-gp 60e6328236e745b3d34dc8cd704bb72888ae5d15; botorch
0.16.1; guardrail_mode constrain. Created 2026-11-24T07:44:46+00:00.

Rows are `oat_site = __ALL__` multi-site designs (contract 5): `mw_<site>` /
`u_<site>` at full precision, `pem_mw = sum mw`, `tier = bo`. The retrofit dict
`retrofit_gen_dict_<i>.json` lists every site with mw > 0 (a site at exactly 0
is ABSENT). Bid 40.0 $/MWh, full year from 01-01-2019.

| row | MW 110 | MW 140 | MW 146 | MW 163 | MW 270 | MW 274 | sum MW | u 110 | u 140 | u 146 | u 163 | u 270 | u 274 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.000 | 0.000 | 0.000 | 185.400 | 181.107 | 746.400 | 1112.907 | 0.00000 | 0.00000 | 0.00000 | 1.00000 | 0.31279 | 1.00000 |
| 2 | 0.000 | 0.000 | 0.000 | 160.093 | 579.000 | 0.000 | 739.093 | 0.00000 | 0.00000 | 0.00000 | 0.86350 | 1.00000 | 0.00000 |
| 3 | 0.000 | 0.000 | 0.000 | 185.400 | 579.000 | 455.874 | 1220.274 | 0.00000 | 0.00000 | 0.00000 | 1.00000 | 1.00000 | 0.61076 |
| 4 | 134.348 | 0.000 | 0.000 | 185.400 | 579.000 | 0.000 | 898.748 | 0.39677 | 0.00000 | 0.00000 | 1.00000 | 1.00000 | 0.00000 |
| 5 | 0.000 | 0.000 | 0.000 | 185.400 | 579.000 | 285.395 | 1049.795 | 0.00000 | 0.00000 | 0.00000 | 1.00000 | 1.00000 | 0.38236 |
| 6 | 0.000 | 250.600 | 72.441 | 185.400 | 579.000 | 746.400 | 1833.841 | 0.00000 | 1.00000 | 0.27030 | 1.00000 | 1.00000 | 1.00000 |
| 7 | 333.591 | 250.600 | 126.232 | 185.400 | 579.000 | 746.400 | 2221.223 | 0.98521 | 1.00000 | 0.47102 | 1.00000 | 1.00000 | 1.00000 |
| 8 | 303.597 | 250.600 | 17.294 | 185.400 | 579.000 | 746.400 | 2082.290 | 0.89662 | 1.00000 | 0.06453 | 1.00000 | 1.00000 | 1.00000 |

Submission: Kay runs `bash analysis/methods_E/submit_ready_E.sh` on the CRC
login node (generic `methods_E_array.sh` + `methods_E_collect.sh`, `-v WAVE=methods_E_EMU_house_s1_s0_r2`,
`-wd trial_0826/ercot/waves`, identity from `waves/GAP_DECISION.json` at run
time, every row `--full`, slim tables + `pool_full_metrics.json` + `COLLECTED`
committed, `*.csv.gz` left in storage). `predictions.csv` holds the pre-round
GP mean / total sd per objective (calibration gates C2 / C3 at grading).
