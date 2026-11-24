# methods_E_EMU_committed_s1_s3_r3 — methods_E acquisition round (prompt 55; NOT submitted by the writer)

Arm `qnehvi`, seed_id 3, round 3,
acq qnehvi seed 20261309; bo-gp 60e6328236e745b3d34dc8cd704bb72888ae5d15; botorch
0.16.1; guardrail_mode constrain. Created 2026-11-24T08:36:36+00:00.

Rows are `oat_site = __ALL__` multi-site designs (contract 5): `mw_<site>` /
`u_<site>` at full precision, `pem_mw = sum mw`, `tier = bo`. The retrofit dict
`retrofit_gen_dict_<i>.json` lists every site with mw > 0 (a site at exactly 0
is ABSENT). Bid 40.0 $/MWh, full year from 01-01-2019.

| row | MW 110 | MW 140 | MW 146 | MW 163 | MW 270 | MW 274 | sum MW | u 110 | u 140 | u 146 | u 163 | u 270 | u 274 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 116.741 | 250.600 | 214.475 | 185.400 | 579.000 | 746.400 | 2092.616 | 0.34478 | 1.00000 | 0.80028 | 1.00000 | 1.00000 | 1.00000 |
| 2 | 0.000 | 250.600 | 0.000 | 19.769 | 579.000 | 746.400 | 1595.769 | 0.00000 | 1.00000 | 0.00000 | 0.10663 | 1.00000 | 1.00000 |
| 3 | 0.000 | 250.600 | 0.000 | 185.400 | 0.000 | 746.400 | 1182.400 | 0.00000 | 1.00000 | 0.00000 | 1.00000 | 0.00000 | 1.00000 |
| 4 | 180.588 | 250.600 | 220.445 | 181.455 | 579.000 | 746.400 | 2158.488 | 0.53334 | 1.00000 | 0.82256 | 0.97872 | 1.00000 | 1.00000 |
| 5 | 0.000 | 95.935 | 0.000 | 185.400 | 579.000 | 746.400 | 1606.735 | 0.00000 | 0.38282 | 0.00000 | 1.00000 | 1.00000 | 1.00000 |
| 6 | 127.949 | 0.000 | 0.000 | 185.400 | 579.000 | 0.000 | 892.349 | 0.37788 | 0.00000 | 0.00000 | 1.00000 | 1.00000 | 0.00000 |
| 7 | 338.600 | 250.600 | 0.000 | 185.400 | 579.000 | 746.400 | 2100.000 | 1.00000 | 1.00000 | 0.00000 | 1.00000 | 1.00000 | 1.00000 |
| 8 | 22.559 | 250.600 | 0.000 | 95.368 | 579.000 | 0.000 | 947.527 | 0.06662 | 1.00000 | 0.00000 | 0.51439 | 1.00000 | 0.00000 |

Submission: Kay runs `bash analysis/methods_E/submit_ready_E.sh` on the CRC
login node (generic `methods_E_array.sh` + `methods_E_collect.sh`, `-v WAVE=methods_E_EMU_committed_s1_s3_r3`,
`-wd trial_0826/ercot/waves`, identity from `waves/GAP_DECISION.json` at run
time, every row `--full`, slim tables + `pool_full_metrics.json` + `COLLECTED`
committed, `*.csv.gz` left in storage). `predictions.csv` holds the pre-round
GP mean / total sd per objective (calibration gates C2 / C3 at grading).
