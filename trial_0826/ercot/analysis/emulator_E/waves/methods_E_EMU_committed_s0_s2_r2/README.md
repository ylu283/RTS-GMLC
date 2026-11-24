# methods_E_EMU_committed_s0_s2_r2 — methods_E acquisition round (prompt 55; NOT submitted by the writer)

Arm `qnehvi`, seed_id 2, round 2,
acq qnehvi seed 20261208; bo-gp 60e6328236e745b3d34dc8cd704bb72888ae5d15; botorch
0.16.1; guardrail_mode monitor. Created 2026-11-24T08:35:30+00:00.

Rows are `oat_site = __ALL__` multi-site designs (contract 5): `mw_<site>` /
`u_<site>` at full precision, `pem_mw = sum mw`, `tier = bo`. The retrofit dict
`retrofit_gen_dict_<i>.json` lists every site with mw > 0 (a site at exactly 0
is ABSENT). Bid 40.0 $/MWh, full year from 01-01-2019.

| row | MW 110 | MW 140 | MW 146 | MW 163 | MW 270 | MW 274 | sum MW | u 110 | u 140 | u 146 | u 163 | u 270 | u 274 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.000 | 96.692 | 0.000 | 185.400 | 579.000 | 0.000 | 861.092 | 0.00000 | 0.38584 | 0.00000 | 1.00000 | 1.00000 | 0.00000 |
| 2 | 0.000 | 250.600 | 74.049 | 185.400 | 579.000 | 746.400 | 1835.449 | 0.00000 | 1.00000 | 0.27630 | 1.00000 | 1.00000 | 1.00000 |
| 3 | 338.600 | 77.588 | 0.000 | 185.400 | 579.000 | 0.000 | 1180.588 | 1.00000 | 0.30961 | 0.00000 | 1.00000 | 1.00000 | 0.00000 |
| 4 | 0.000 | 250.600 | 0.000 | 185.400 | 579.000 | 0.000 | 1015.000 | 0.00000 | 1.00000 | 0.00000 | 1.00000 | 1.00000 | 0.00000 |
| 5 | 24.754 | 250.600 | 211.954 | 185.400 | 579.000 | 746.400 | 1998.109 | 0.07311 | 1.00000 | 0.79087 | 1.00000 | 1.00000 | 1.00000 |
| 6 | 148.593 | 250.600 | 204.614 | 185.400 | 579.000 | 746.400 | 2114.607 | 0.43884 | 1.00000 | 0.76349 | 1.00000 | 1.00000 | 1.00000 |
| 7 | 0.000 | 101.027 | 0.000 | 185.400 | 579.000 | 746.400 | 1611.827 | 0.00000 | 0.40314 | 0.00000 | 1.00000 | 1.00000 | 1.00000 |
| 8 | 0.000 | 0.000 | 0.000 | 185.400 | 266.944 | 746.400 | 1198.744 | 0.00000 | 0.00000 | 0.00000 | 1.00000 | 0.46104 | 1.00000 |

Submission: Kay runs `bash analysis/methods_E/submit_ready_E.sh` on the CRC
login node (generic `methods_E_array.sh` + `methods_E_collect.sh`, `-v WAVE=methods_E_EMU_committed_s0_s2_r2`,
`-wd trial_0826/ercot/waves`, identity from `waves/GAP_DECISION.json` at run
time, every row `--full`, slim tables + `pool_full_metrics.json` + `COLLECTED`
committed, `*.csv.gz` left in storage). `predictions.csv` holds the pre-round
GP mean / total sd per objective (calibration gates C2 / C3 at grading).
