# methods_E_EMU_committed_s0_s1_r4 — methods_E acquisition round (prompt 55; NOT submitted by the writer)

Arm `qnehvi`, seed_id 1, round 4,
acq qnehvi seed 20261110; bo-gp 60e6328236e745b3d34dc8cd704bb72888ae5d15; botorch
0.16.1; guardrail_mode monitor. Created 2026-11-24T08:35:14+00:00.

Rows are `oat_site = __ALL__` multi-site designs (contract 5): `mw_<site>` /
`u_<site>` at full precision, `pem_mw = sum mw`, `tier = bo`. The retrofit dict
`retrofit_gen_dict_<i>.json` lists every site with mw > 0 (a site at exactly 0
is ABSENT). Bid 40.0 $/MWh, full year from 01-01-2019.

| row | MW 110 | MW 140 | MW 146 | MW 163 | MW 270 | MW 274 | sum MW | u 110 | u 140 | u 146 | u 163 | u 270 | u 274 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.000 | 0.000 | 0.000 | 185.400 | 47.024 | 746.400 | 978.824 | 0.00000 | 0.00000 | 0.00000 | 1.00000 | 0.08122 | 1.00000 |
| 2 | 338.600 | 0.000 | 99.122 | 25.189 | 579.000 | 746.400 | 1788.312 | 1.00000 | 0.00000 | 0.36986 | 0.13586 | 1.00000 | 1.00000 |
| 3 | 183.390 | 250.600 | 211.714 | 182.922 | 579.000 | 746.400 | 2154.026 | 0.54161 | 1.00000 | 0.78998 | 0.98663 | 1.00000 | 1.00000 |
| 4 | 0.000 | 0.000 | 0.000 | 0.000 | 579.000 | 696.502 | 1275.502 | 0.00000 | 0.00000 | 0.00000 | 0.00000 | 1.00000 | 0.93315 |
| 5 | 338.600 | 250.600 | 116.753 | 121.238 | 579.000 | 746.400 | 2152.591 | 1.00000 | 1.00000 | 0.43565 | 0.65393 | 1.00000 | 1.00000 |
| 6 | 338.600 | 30.792 | 268.000 | 185.400 | 579.000 | 746.400 | 2148.192 | 1.00000 | 0.12287 | 1.00000 | 1.00000 | 1.00000 | 1.00000 |
| 7 | 338.600 | 0.000 | 0.000 | 0.000 | 0.000 | 746.400 | 1085.000 | 1.00000 | 0.00000 | 0.00000 | 0.00000 | 0.00000 | 1.00000 |
| 8 | 338.600 | 0.000 | 0.000 | 185.400 | 0.000 | 746.400 | 1270.400 | 1.00000 | 0.00000 | 0.00000 | 1.00000 | 0.00000 | 1.00000 |

Submission: Kay runs `bash analysis/methods_E/submit_ready_E.sh` on the CRC
login node (generic `methods_E_array.sh` + `methods_E_collect.sh`, `-v WAVE=methods_E_EMU_committed_s0_s1_r4`,
`-wd trial_0826/ercot/waves`, identity from `waves/GAP_DECISION.json` at run
time, every row `--full`, slim tables + `pool_full_metrics.json` + `COLLECTED`
committed, `*.csv.gz` left in storage). `predictions.csv` holds the pre-round
GP mean / total sd per objective (calibration gates C2 / C3 at grading).
