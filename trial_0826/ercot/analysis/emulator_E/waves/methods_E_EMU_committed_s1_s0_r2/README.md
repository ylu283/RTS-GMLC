# methods_E_EMU_committed_s1_s0_r2 — methods_E acquisition round (prompt 55; NOT submitted by the writer)

Arm `qnehvi`, seed_id 0, round 2,
acq qnehvi seed 20261008; bo-gp 60e6328236e745b3d34dc8cd704bb72888ae5d15; botorch
0.16.1; guardrail_mode constrain. Created 2026-11-24T08:34:22+00:00.

Rows are `oat_site = __ALL__` multi-site designs (contract 5): `mw_<site>` /
`u_<site>` at full precision, `pem_mw = sum mw`, `tier = bo`. The retrofit dict
`retrofit_gen_dict_<i>.json` lists every site with mw > 0 (a site at exactly 0
is ABSENT). Bid 40.0 $/MWh, full year from 01-01-2019.

| row | MW 110 | MW 140 | MW 146 | MW 163 | MW 270 | MW 274 | sum MW | u 110 | u 140 | u 146 | u 163 | u 270 | u 274 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 8.983 | 250.600 | 107.403 | 185.400 | 579.000 | 746.400 | 1877.787 | 0.02653 | 1.00000 | 0.40076 | 1.00000 | 1.00000 | 1.00000 |
| 2 | 4.948 | 250.600 | 212.397 | 185.400 | 579.000 | 746.400 | 1978.745 | 0.01461 | 1.00000 | 0.79253 | 1.00000 | 1.00000 | 1.00000 |
| 3 | 97.699 | 0.000 | 0.000 | 185.400 | 579.000 | 0.000 | 862.099 | 0.28854 | 0.00000 | 0.00000 | 1.00000 | 1.00000 | 0.00000 |
| 4 | 0.000 | 0.000 | 0.000 | 0.000 | 579.000 | 624.936 | 1203.936 | 0.00000 | 0.00000 | 0.00000 | 0.00000 | 1.00000 | 0.83727 |
| 5 | 0.000 | 63.518 | 0.000 | 185.400 | 579.000 | 746.400 | 1574.318 | 0.00000 | 0.25346 | 0.00000 | 1.00000 | 1.00000 | 1.00000 |
| 6 | 156.927 | 250.600 | 202.618 | 185.400 | 579.000 | 746.400 | 2120.945 | 0.46346 | 1.00000 | 0.75604 | 1.00000 | 1.00000 | 1.00000 |
| 7 | 0.000 | 250.600 | 58.851 | 185.400 | 579.000 | 746.400 | 1820.251 | 0.00000 | 1.00000 | 0.21959 | 1.00000 | 1.00000 | 1.00000 |
| 8 | 0.000 | 0.000 | 0.000 | 72.867 | 579.000 | 0.000 | 651.867 | 0.00000 | 0.00000 | 0.00000 | 0.39302 | 1.00000 | 0.00000 |

Submission: Kay runs `bash analysis/methods_E/submit_ready_E.sh` on the CRC
login node (generic `methods_E_array.sh` + `methods_E_collect.sh`, `-v WAVE=methods_E_EMU_committed_s1_s0_r2`,
`-wd trial_0826/ercot/waves`, identity from `waves/GAP_DECISION.json` at run
time, every row `--full`, slim tables + `pool_full_metrics.json` + `COLLECTED`
committed, `*.csv.gz` left in storage). `predictions.csv` holds the pre-round
GP mean / total sd per objective (calibration gates C2 / C3 at grading).
