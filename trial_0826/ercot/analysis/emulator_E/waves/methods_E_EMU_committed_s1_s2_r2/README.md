# methods_E_EMU_committed_s1_s2_r2 — methods_E acquisition round (prompt 55; NOT submitted by the writer)

Arm `qnehvi`, seed_id 2, round 2,
acq qnehvi seed 20261208; bo-gp 60e6328236e745b3d34dc8cd704bb72888ae5d15; botorch
0.16.1; guardrail_mode constrain. Created 2026-11-24T08:35:45+00:00.

Rows are `oat_site = __ALL__` multi-site designs (contract 5): `mw_<site>` /
`u_<site>` at full precision, `pem_mw = sum mw`, `tier = bo`. The retrofit dict
`retrofit_gen_dict_<i>.json` lists every site with mw > 0 (a site at exactly 0
is ABSENT). Bid 40.0 $/MWh, full year from 01-01-2019.

| row | MW 110 | MW 140 | MW 146 | MW 163 | MW 270 | MW 274 | sum MW | u 110 | u 140 | u 146 | u 163 | u 270 | u 274 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 74.455 | 0.000 | 0.000 | 185.400 | 579.000 | 0.000 | 838.855 | 0.21989 | 0.00000 | 0.00000 | 1.00000 | 1.00000 | 0.00000 |
| 2 | 46.534 | 0.000 | 0.000 | 31.265 | 579.000 | 0.000 | 656.800 | 0.13743 | 0.00000 | 0.00000 | 0.16864 | 1.00000 | 0.00000 |
| 3 | 0.000 | 250.600 | 74.123 | 185.400 | 579.000 | 746.400 | 1835.523 | 0.00000 | 1.00000 | 0.27658 | 1.00000 | 1.00000 | 1.00000 |
| 4 | 166.915 | 250.600 | 189.427 | 185.400 | 579.000 | 746.400 | 2117.743 | 0.49296 | 1.00000 | 0.70682 | 1.00000 | 1.00000 | 1.00000 |
| 5 | 0.000 | 250.600 | 0.000 | 185.400 | 0.000 | 746.400 | 1182.400 | 0.00000 | 1.00000 | 0.00000 | 1.00000 | 0.00000 | 1.00000 |
| 6 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 722.988 | 722.988 | 0.00000 | 0.00000 | 0.00000 | 0.00000 | 0.00000 | 0.96863 |
| 7 | 338.600 | 68.436 | 66.097 | 185.400 | 579.000 | 746.400 | 1983.933 | 1.00000 | 0.27309 | 0.24663 | 1.00000 | 1.00000 | 1.00000 |
| 8 | 29.147 | 250.600 | 199.133 | 185.400 | 579.000 | 746.400 | 1989.679 | 0.08608 | 1.00000 | 0.74303 | 1.00000 | 1.00000 | 1.00000 |

Submission: Kay runs `bash analysis/methods_E/submit_ready_E.sh` on the CRC
login node (generic `methods_E_array.sh` + `methods_E_collect.sh`, `-v WAVE=methods_E_EMU_committed_s1_s2_r2`,
`-wd trial_0826/ercot/waves`, identity from `waves/GAP_DECISION.json` at run
time, every row `--full`, slim tables + `pool_full_metrics.json` + `COLLECTED`
committed, `*.csv.gz` left in storage). `predictions.csv` holds the pre-round
GP mean / total sd per objective (calibration gates C2 / C3 at grading).
