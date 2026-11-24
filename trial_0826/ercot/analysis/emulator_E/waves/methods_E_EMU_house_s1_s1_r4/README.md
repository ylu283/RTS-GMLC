# methods_E_EMU_house_s1_s1_r4 — methods_E acquisition round (prompt 55; NOT submitted by the writer)

Arm `qnehvi`, seed_id 1, round 4,
acq qnehvi seed 20261110; bo-gp 60e6328236e745b3d34dc8cd704bb72888ae5d15; botorch
0.16.1; guardrail_mode constrain. Created 2026-11-24T08:05:36+00:00.

Rows are `oat_site = __ALL__` multi-site designs (contract 5): `mw_<site>` /
`u_<site>` at full precision, `pem_mw = sum mw`, `tier = bo`. The retrofit dict
`retrofit_gen_dict_<i>.json` lists every site with mw > 0 (a site at exactly 0
is ABSENT). Bid 40.0 $/MWh, full year from 01-01-2019.

| row | MW 110 | MW 140 | MW 146 | MW 163 | MW 270 | MW 274 | sum MW | u 110 | u 140 | u 146 | u 163 | u 270 | u 274 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.000 | 250.600 | 0.000 | 185.400 | 0.000 | 746.400 | 1182.400 | 0.00000 | 1.00000 | 0.00000 | 1.00000 | 0.00000 | 1.00000 |
| 2 | 0.000 | 250.600 | 35.209 | 185.400 | 579.000 | 746.400 | 1796.609 | 0.00000 | 1.00000 | 0.13138 | 1.00000 | 1.00000 | 1.00000 |
| 3 | 11.185 | 250.600 | 202.397 | 185.400 | 579.000 | 746.400 | 1974.982 | 0.03303 | 1.00000 | 0.75521 | 1.00000 | 1.00000 | 1.00000 |
| 4 | 0.000 | 0.000 | 268.000 | 185.400 | 0.000 | 746.400 | 1199.800 | 0.00000 | 0.00000 | 1.00000 | 1.00000 | 0.00000 | 1.00000 |
| 5 | 0.000 | 0.000 | 0.000 | 185.400 | 456.267 | 0.000 | 641.667 | 0.00000 | 0.00000 | 0.00000 | 1.00000 | 0.78803 | 0.00000 |
| 6 | 0.000 | 250.600 | 114.515 | 185.400 | 579.000 | 746.400 | 1875.915 | 0.00000 | 1.00000 | 0.42729 | 1.00000 | 1.00000 | 1.00000 |
| 7 | 128.363 | 250.600 | 228.055 | 185.400 | 579.000 | 746.400 | 2117.818 | 0.37910 | 1.00000 | 0.85095 | 1.00000 | 1.00000 | 1.00000 |
| 8 | 0.000 | 0.000 | 0.000 | 185.400 | 579.000 | 268.121 | 1032.521 | 0.00000 | 0.00000 | 0.00000 | 1.00000 | 1.00000 | 0.35922 |

Submission: Kay runs `bash analysis/methods_E/submit_ready_E.sh` on the CRC
login node (generic `methods_E_array.sh` + `methods_E_collect.sh`, `-v WAVE=methods_E_EMU_house_s1_s1_r4`,
`-wd trial_0826/ercot/waves`, identity from `waves/GAP_DECISION.json` at run
time, every row `--full`, slim tables + `pool_full_metrics.json` + `COLLECTED`
committed, `*.csv.gz` left in storage). `predictions.csv` holds the pre-round
GP mean / total sd per objective (calibration gates C2 / C3 at grading).
