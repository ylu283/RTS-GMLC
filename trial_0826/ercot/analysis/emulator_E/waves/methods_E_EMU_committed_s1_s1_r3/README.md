# methods_E_EMU_committed_s1_s1_r3 — methods_E acquisition round (prompt 55; NOT submitted by the writer)

Arm `qnehvi`, seed_id 1, round 3,
acq qnehvi seed 20261109; bo-gp 60e6328236e745b3d34dc8cd704bb72888ae5d15; botorch
0.16.1; guardrail_mode constrain. Created 2026-11-24T08:35:15+00:00.

Rows are `oat_site = __ALL__` multi-site designs (contract 5): `mw_<site>` /
`u_<site>` at full precision, `pem_mw = sum mw`, `tier = bo`. The retrofit dict
`retrofit_gen_dict_<i>.json` lists every site with mw > 0 (a site at exactly 0
is ABSENT). Bid 40.0 $/MWh, full year from 01-01-2019.

| row | MW 110 | MW 140 | MW 146 | MW 163 | MW 270 | MW 274 | sum MW | u 110 | u 140 | u 146 | u 163 | u 270 | u 274 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.000 | 0.000 | 0.000 | 185.400 | 579.000 | 479.236 | 1243.636 | 0.00000 | 0.00000 | 0.00000 | 1.00000 | 1.00000 | 0.64206 |
| 2 | 0.000 | 250.600 | 0.000 | 33.233 | 579.000 | 746.400 | 1609.233 | 0.00000 | 1.00000 | 0.00000 | 0.17925 | 1.00000 | 1.00000 |
| 3 | 260.049 | 0.000 | 0.000 | 185.400 | 579.000 | 0.000 | 1024.449 | 0.76801 | 0.00000 | 0.00000 | 1.00000 | 1.00000 | 0.00000 |
| 4 | 0.000 | 105.385 | 0.000 | 185.400 | 579.000 | 746.400 | 1616.185 | 0.00000 | 0.42053 | 0.00000 | 1.00000 | 1.00000 | 1.00000 |
| 5 | 51.957 | 250.600 | 211.061 | 185.400 | 579.000 | 746.400 | 2024.419 | 0.15345 | 1.00000 | 0.78754 | 1.00000 | 1.00000 | 1.00000 |
| 6 | 338.600 | 0.000 | 0.000 | 0.000 | 0.000 | 746.400 | 1085.000 | 1.00000 | 0.00000 | 0.00000 | 0.00000 | 0.00000 | 1.00000 |
| 7 | 196.035 | 250.600 | 198.783 | 184.458 | 579.000 | 746.400 | 2155.276 | 0.57896 | 1.00000 | 0.74173 | 0.99492 | 1.00000 | 1.00000 |
| 8 | 0.000 | 250.600 | 211.167 | 185.400 | 579.000 | 746.400 | 1972.567 | 0.00000 | 1.00000 | 0.78794 | 1.00000 | 1.00000 | 1.00000 |

Submission: Kay runs `bash analysis/methods_E/submit_ready_E.sh` on the CRC
login node (generic `methods_E_array.sh` + `methods_E_collect.sh`, `-v WAVE=methods_E_EMU_committed_s1_s1_r3`,
`-wd trial_0826/ercot/waves`, identity from `waves/GAP_DECISION.json` at run
time, every row `--full`, slim tables + `pool_full_metrics.json` + `COLLECTED`
committed, `*.csv.gz` left in storage). `predictions.csv` holds the pre-round
GP mean / total sd per objective (calibration gates C2 / C3 at grading).
