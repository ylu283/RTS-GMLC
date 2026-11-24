# methods_E_EMU_house_s1_s2_r4 — methods_E acquisition round (prompt 55; NOT submitted by the writer)

Arm `qnehvi`, seed_id 2, round 4,
acq qnehvi seed 20261210; bo-gp 60e6328236e745b3d34dc8cd704bb72888ae5d15; botorch
0.16.1; guardrail_mode constrain. Created 2026-11-24T08:06:16+00:00.

Rows are `oat_site = __ALL__` multi-site designs (contract 5): `mw_<site>` /
`u_<site>` at full precision, `pem_mw = sum mw`, `tier = bo`. The retrofit dict
`retrofit_gen_dict_<i>.json` lists every site with mw > 0 (a site at exactly 0
is ABSENT). Bid 40.0 $/MWh, full year from 01-01-2019.

| row | MW 110 | MW 140 | MW 146 | MW 163 | MW 270 | MW 274 | sum MW | u 110 | u 140 | u 146 | u 163 | u 270 | u 274 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.000 | 0.000 | 0.000 | 185.400 | 267.318 | 746.400 | 1199.118 | 0.00000 | 0.00000 | 0.00000 | 1.00000 | 0.46169 | 1.00000 |
| 2 | 204.729 | 250.600 | 229.794 | 185.400 | 579.000 | 746.400 | 2195.923 | 0.60464 | 1.00000 | 0.85744 | 1.00000 | 1.00000 | 1.00000 |
| 3 | 0.000 | 0.000 | 0.000 | 185.400 | 407.401 | 746.400 | 1339.201 | 0.00000 | 0.00000 | 0.00000 | 1.00000 | 0.70363 | 1.00000 |
| 4 | 183.146 | 0.000 | 0.000 | 185.400 | 579.000 | 0.000 | 947.546 | 0.54089 | 0.00000 | 0.00000 | 1.00000 | 1.00000 | 0.00000 |
| 5 | 0.000 | 0.000 | 0.000 | 185.400 | 142.946 | 746.400 | 1074.746 | 0.00000 | 0.00000 | 0.00000 | 1.00000 | 0.24689 | 1.00000 |
| 6 | 257.237 | 0.000 | 0.000 | 185.400 | 579.000 | 0.000 | 1021.637 | 0.75971 | 0.00000 | 0.00000 | 1.00000 | 1.00000 | 0.00000 |
| 7 | 0.000 | 250.600 | 115.240 | 185.400 | 579.000 | 746.400 | 1876.640 | 0.00000 | 1.00000 | 0.43000 | 1.00000 | 1.00000 | 1.00000 |
| 8 | 60.683 | 250.600 | 219.790 | 185.400 | 579.000 | 746.400 | 2041.872 | 0.17922 | 1.00000 | 0.82011 | 1.00000 | 1.00000 | 1.00000 |

Submission: Kay runs `bash analysis/methods_E/submit_ready_E.sh` on the CRC
login node (generic `methods_E_array.sh` + `methods_E_collect.sh`, `-v WAVE=methods_E_EMU_house_s1_s2_r4`,
`-wd trial_0826/ercot/waves`, identity from `waves/GAP_DECISION.json` at run
time, every row `--full`, slim tables + `pool_full_metrics.json` + `COLLECTED`
committed, `*.csv.gz` left in storage). `predictions.csv` holds the pre-round
GP mean / total sd per objective (calibration gates C2 / C3 at grading).
