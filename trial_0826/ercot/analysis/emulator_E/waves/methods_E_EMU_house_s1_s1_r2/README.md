# methods_E_EMU_house_s1_s1_r2 — methods_E acquisition round (prompt 55; NOT submitted by the writer)

Arm `qnehvi`, seed_id 1, round 2,
acq qnehvi seed 20261108; bo-gp 60e6328236e745b3d34dc8cd704bb72888ae5d15; botorch
0.16.1; guardrail_mode constrain. Created 2026-11-24T08:05:13+00:00.

Rows are `oat_site = __ALL__` multi-site designs (contract 5): `mw_<site>` /
`u_<site>` at full precision, `pem_mw = sum mw`, `tier = bo`. The retrofit dict
`retrofit_gen_dict_<i>.json` lists every site with mw > 0 (a site at exactly 0
is ABSENT). Bid 40.0 $/MWh, full year from 01-01-2019.

| row | MW 110 | MW 140 | MW 146 | MW 163 | MW 270 | MW 274 | sum MW | u 110 | u 140 | u 146 | u 163 | u 270 | u 274 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 55.407 | 250.600 | 0.000 | 185.400 | 579.000 | 0.000 | 1070.407 | 0.16363 | 1.00000 | 0.00000 | 1.00000 | 1.00000 | 0.00000 |
| 2 | 0.000 | 0.000 | 0.000 | 166.750 | 579.000 | 0.000 | 745.750 | 0.00000 | 0.00000 | 0.00000 | 0.89941 | 1.00000 | 0.00000 |
| 3 | 0.000 | 250.600 | 73.509 | 185.400 | 579.000 | 746.400 | 1834.909 | 0.00000 | 1.00000 | 0.27429 | 1.00000 | 1.00000 | 1.00000 |
| 4 | 137.937 | 0.000 | 0.000 | 185.400 | 579.000 | 0.000 | 902.337 | 0.40738 | 0.00000 | 0.00000 | 1.00000 | 1.00000 | 0.00000 |
| 5 | 0.000 | 0.000 | 0.000 | 185.400 | 579.000 | 345.471 | 1109.871 | 0.00000 | 0.00000 | 0.00000 | 1.00000 | 1.00000 | 0.46285 |
| 6 | 338.600 | 250.600 | 122.227 | 185.400 | 579.000 | 746.400 | 2222.227 | 1.00000 | 1.00000 | 0.45607 | 1.00000 | 1.00000 | 1.00000 |
| 7 | 338.600 | 250.600 | 10.974 | 185.400 | 579.000 | 746.400 | 2110.974 | 1.00000 | 1.00000 | 0.04095 | 1.00000 | 1.00000 | 1.00000 |
| 8 | 338.600 | 0.000 | 0.000 | 0.000 | 0.000 | 746.400 | 1085.000 | 1.00000 | 0.00000 | 0.00000 | 0.00000 | 0.00000 | 1.00000 |

Submission: Kay runs `bash analysis/methods_E/submit_ready_E.sh` on the CRC
login node (generic `methods_E_array.sh` + `methods_E_collect.sh`, `-v WAVE=methods_E_EMU_house_s1_s1_r2`,
`-wd trial_0826/ercot/waves`, identity from `waves/GAP_DECISION.json` at run
time, every row `--full`, slim tables + `pool_full_metrics.json` + `COLLECTED`
committed, `*.csv.gz` left in storage). `predictions.csv` holds the pre-round
GP mean / total sd per objective (calibration gates C2 / C3 at grading).
