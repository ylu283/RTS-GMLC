# methods_E_EMU_house_s0_s4_r4 — methods_E acquisition round (prompt 55; NOT submitted by the writer)

Arm `qnehvi`, seed_id 4, round 4,
acq qnehvi seed 20261410; bo-gp 60e6328236e745b3d34dc8cd704bb72888ae5d15; botorch
0.16.1; guardrail_mode monitor. Created 2026-11-24T08:06:45+00:00.

Rows are `oat_site = __ALL__` multi-site designs (contract 5): `mw_<site>` /
`u_<site>` at full precision, `pem_mw = sum mw`, `tier = bo`. The retrofit dict
`retrofit_gen_dict_<i>.json` lists every site with mw > 0 (a site at exactly 0
is ABSENT). Bid 40.0 $/MWh, full year from 01-01-2019.

| row | MW 110 | MW 140 | MW 146 | MW 163 | MW 270 | MW 274 | sum MW | u 110 | u 140 | u 146 | u 163 | u 270 | u 274 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 338.600 | 0.000 | 0.000 | 0.000 | 0.000 | 746.400 | 1085.000 | 1.00000 | 0.00000 | 0.00000 | 0.00000 | 0.00000 | 1.00000 |
| 2 | 0.000 | 250.600 | 115.488 | 185.400 | 579.000 | 746.400 | 1876.888 | 0.00000 | 1.00000 | 0.43092 | 1.00000 | 1.00000 | 1.00000 |
| 3 | 0.000 | 0.000 | 268.000 | 185.400 | 0.000 | 746.400 | 1199.800 | 0.00000 | 0.00000 | 1.00000 | 1.00000 | 0.00000 | 1.00000 |
| 4 | 338.600 | 250.600 | 35.119 | 185.400 | 579.000 | 746.400 | 2135.119 | 1.00000 | 1.00000 | 0.13104 | 1.00000 | 1.00000 | 1.00000 |
| 5 | 338.600 | 0.000 | 0.000 | 185.400 | 579.000 | 43.497 | 1146.497 | 1.00000 | 0.00000 | 0.00000 | 1.00000 | 1.00000 | 0.05828 |
| 6 | 338.600 | 250.600 | 168.715 | 185.400 | 579.000 | 746.400 | 2268.715 | 1.00000 | 1.00000 | 0.62953 | 1.00000 | 1.00000 | 1.00000 |
| 7 | 188.372 | 0.000 | 0.000 | 185.400 | 579.000 | 0.000 | 952.772 | 0.55633 | 0.00000 | 0.00000 | 1.00000 | 1.00000 | 0.00000 |
| 8 | 338.600 | 250.600 | 0.000 | 185.400 | 579.000 | 746.400 | 2100.000 | 1.00000 | 1.00000 | 0.00000 | 1.00000 | 1.00000 | 1.00000 |

Submission: Kay runs `bash analysis/methods_E/submit_ready_E.sh` on the CRC
login node (generic `methods_E_array.sh` + `methods_E_collect.sh`, `-v WAVE=methods_E_EMU_house_s0_s4_r4`,
`-wd trial_0826/ercot/waves`, identity from `waves/GAP_DECISION.json` at run
time, every row `--full`, slim tables + `pool_full_metrics.json` + `COLLECTED`
committed, `*.csv.gz` left in storage). `predictions.csv` holds the pre-round
GP mean / total sd per objective (calibration gates C2 / C3 at grading).
