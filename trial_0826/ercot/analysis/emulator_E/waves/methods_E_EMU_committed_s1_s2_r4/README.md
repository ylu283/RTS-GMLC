# methods_E_EMU_committed_s1_s2_r4 — methods_E acquisition round (prompt 55; NOT submitted by the writer)

Arm `qnehvi`, seed_id 2, round 4,
acq qnehvi seed 20261210; bo-gp 60e6328236e745b3d34dc8cd704bb72888ae5d15; botorch
0.16.1; guardrail_mode constrain. Created 2026-11-24T08:36:07+00:00.

Rows are `oat_site = __ALL__` multi-site designs (contract 5): `mw_<site>` /
`u_<site>` at full precision, `pem_mw = sum mw`, `tier = bo`. The retrofit dict
`retrofit_gen_dict_<i>.json` lists every site with mw > 0 (a site at exactly 0
is ABSENT). Bid 40.0 $/MWh, full year from 01-01-2019.

| row | MW 110 | MW 140 | MW 146 | MW 163 | MW 270 | MW 274 | sum MW | u 110 | u 140 | u 146 | u 163 | u 270 | u 274 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 338.600 | 250.600 | 30.030 | 126.723 | 579.000 | 746.400 | 2071.354 | 1.00000 | 1.00000 | 0.11205 | 0.68351 | 1.00000 | 1.00000 |
| 2 | 338.600 | 187.912 | 143.673 | 179.312 | 579.000 | 717.405 | 2145.901 | 1.00000 | 0.74985 | 0.53609 | 0.96716 | 1.00000 | 0.96115 |
| 3 | 166.694 | 250.600 | 234.327 | 185.400 | 579.000 | 746.400 | 2162.422 | 0.49230 | 1.00000 | 0.87436 | 1.00000 | 1.00000 | 1.00000 |
| 4 | 46.347 | 250.600 | 222.575 | 185.400 | 579.000 | 746.400 | 2030.322 | 0.13688 | 1.00000 | 0.83050 | 1.00000 | 1.00000 | 1.00000 |
| 5 | 25.782 | 250.600 | 0.000 | 0.000 | 579.000 | 0.000 | 855.382 | 0.07614 | 1.00000 | 0.00000 | 0.00000 | 1.00000 | 0.00000 |
| 6 | 0.000 | 197.121 | 0.000 | 185.400 | 0.000 | 746.400 | 1128.921 | 0.00000 | 0.78660 | 0.00000 | 1.00000 | 0.00000 | 1.00000 |
| 7 | 134.283 | 0.000 | 0.000 | 185.400 | 579.000 | 0.000 | 898.682 | 0.39658 | 0.00000 | 0.00000 | 1.00000 | 1.00000 | 0.00000 |
| 8 | 0.000 | 250.600 | 0.000 | 185.400 | 28.751 | 746.400 | 1211.151 | 0.00000 | 1.00000 | 0.00000 | 1.00000 | 0.04966 | 1.00000 |

Submission: Kay runs `bash analysis/methods_E/submit_ready_E.sh` on the CRC
login node (generic `methods_E_array.sh` + `methods_E_collect.sh`, `-v WAVE=methods_E_EMU_committed_s1_s2_r4`,
`-wd trial_0826/ercot/waves`, identity from `waves/GAP_DECISION.json` at run
time, every row `--full`, slim tables + `pool_full_metrics.json` + `COLLECTED`
committed, `*.csv.gz` left in storage). `predictions.csv` holds the pre-round
GP mean / total sd per objective (calibration gates C2 / C3 at grading).
