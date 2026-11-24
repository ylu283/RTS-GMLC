# methods_E_EMU_committed_s1_s1_r2 — methods_E acquisition round (prompt 55; NOT submitted by the writer)

Arm `qnehvi`, seed_id 1, round 2,
acq qnehvi seed 20261108; bo-gp 60e6328236e745b3d34dc8cd704bb72888ae5d15; botorch
0.16.1; guardrail_mode constrain. Created 2026-11-24T08:35:05+00:00.

Rows are `oat_site = __ALL__` multi-site designs (contract 5): `mw_<site>` /
`u_<site>` at full precision, `pem_mw = sum mw`, `tier = bo`. The retrofit dict
`retrofit_gen_dict_<i>.json` lists every site with mw > 0 (a site at exactly 0
is ABSENT). Bid 40.0 $/MWh, full year from 01-01-2019.

| row | MW 110 | MW 140 | MW 146 | MW 163 | MW 270 | MW 274 | sum MW | u 110 | u 140 | u 146 | u 163 | u 270 | u 274 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 730.967 | 730.967 | 0.00000 | 0.00000 | 0.00000 | 0.00000 | 0.00000 | 0.97932 |
| 2 | 47.080 | 0.000 | 0.000 | 56.312 | 579.000 | 0.000 | 682.392 | 0.13904 | 0.00000 | 0.00000 | 0.30373 | 1.00000 | 0.00000 |
| 3 | 28.089 | 250.600 | 0.000 | 0.000 | 579.000 | 0.000 | 857.689 | 0.08296 | 1.00000 | 0.00000 | 0.00000 | 1.00000 | 0.00000 |
| 4 | 0.000 | 250.600 | 74.374 | 185.400 | 579.000 | 746.400 | 1835.774 | 0.00000 | 1.00000 | 0.27752 | 1.00000 | 1.00000 | 1.00000 |
| 5 | 67.126 | 0.000 | 0.000 | 185.400 | 579.000 | 0.000 | 831.526 | 0.19824 | 0.00000 | 0.00000 | 1.00000 | 1.00000 | 0.00000 |
| 6 | 0.000 | 250.600 | 0.000 | 185.400 | 0.000 | 746.400 | 1182.400 | 0.00000 | 1.00000 | 0.00000 | 1.00000 | 0.00000 | 1.00000 |
| 7 | 18.141 | 250.600 | 227.762 | 185.400 | 579.000 | 746.400 | 2007.303 | 0.05358 | 1.00000 | 0.84986 | 1.00000 | 1.00000 | 1.00000 |
| 8 | 138.656 | 250.600 | 219.152 | 185.400 | 579.000 | 746.400 | 2119.208 | 0.40950 | 1.00000 | 0.81773 | 1.00000 | 1.00000 | 1.00000 |

Submission: Kay runs `bash analysis/methods_E/submit_ready_E.sh` on the CRC
login node (generic `methods_E_array.sh` + `methods_E_collect.sh`, `-v WAVE=methods_E_EMU_committed_s1_s1_r2`,
`-wd trial_0826/ercot/waves`, identity from `waves/GAP_DECISION.json` at run
time, every row `--full`, slim tables + `pool_full_metrics.json` + `COLLECTED`
committed, `*.csv.gz` left in storage). `predictions.csv` holds the pre-round
GP mean / total sd per objective (calibration gates C2 / C3 at grading).
