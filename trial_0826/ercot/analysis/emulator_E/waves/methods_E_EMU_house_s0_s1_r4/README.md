# methods_E_EMU_house_s0_s1_r4 — methods_E acquisition round (prompt 55; NOT submitted by the writer)

Arm `qnehvi`, seed_id 1, round 4,
acq qnehvi seed 20261110; bo-gp 60e6328236e745b3d34dc8cd704bb72888ae5d15; botorch
0.16.1; guardrail_mode monitor. Created 2026-11-24T08:05:17+00:00.

Rows are `oat_site = __ALL__` multi-site designs (contract 5): `mw_<site>` /
`u_<site>` at full precision, `pem_mw = sum mw`, `tier = bo`. The retrofit dict
`retrofit_gen_dict_<i>.json` lists every site with mw > 0 (a site at exactly 0
is ABSENT). Bid 40.0 $/MWh, full year from 01-01-2019.

| row | MW 110 | MW 140 | MW 146 | MW 163 | MW 270 | MW 274 | sum MW | u 110 | u 140 | u 146 | u 163 | u 270 | u 274 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 338.600 | 0.000 | 0.000 | 185.400 | 579.000 | 746.400 | 1849.400 | 1.00000 | 0.00000 | 0.00000 | 1.00000 | 1.00000 | 1.00000 |
| 2 | 229.616 | 250.600 | 211.923 | 185.400 | 579.000 | 746.400 | 2202.938 | 0.67813 | 1.00000 | 0.79076 | 1.00000 | 1.00000 | 1.00000 |
| 3 | 338.600 | 79.747 | 0.000 | 185.400 | 579.000 | 746.400 | 1929.147 | 1.00000 | 0.31823 | 0.00000 | 1.00000 | 1.00000 | 1.00000 |
| 4 | 0.000 | 250.600 | 34.287 | 185.400 | 579.000 | 746.400 | 1795.687 | 0.00000 | 1.00000 | 0.12794 | 1.00000 | 1.00000 | 1.00000 |
| 5 | 0.000 | 144.868 | 0.000 | 185.400 | 579.000 | 746.400 | 1655.667 | 0.00000 | 0.57808 | 0.00000 | 1.00000 | 1.00000 | 1.00000 |
| 6 | 0.000 | 250.600 | 0.000 | 185.400 | 0.000 | 746.400 | 1182.400 | 0.00000 | 1.00000 | 0.00000 | 1.00000 | 0.00000 | 1.00000 |
| 7 | 76.399 | 250.600 | 192.888 | 185.400 | 579.000 | 746.400 | 2030.687 | 0.22563 | 1.00000 | 0.71973 | 1.00000 | 1.00000 | 1.00000 |
| 8 | 0.000 | 0.000 | 268.000 | 185.400 | 0.000 | 746.400 | 1199.800 | 0.00000 | 0.00000 | 1.00000 | 1.00000 | 0.00000 | 1.00000 |

Submission: Kay runs `bash analysis/methods_E/submit_ready_E.sh` on the CRC
login node (generic `methods_E_array.sh` + `methods_E_collect.sh`, `-v WAVE=methods_E_EMU_house_s0_s1_r4`,
`-wd trial_0826/ercot/waves`, identity from `waves/GAP_DECISION.json` at run
time, every row `--full`, slim tables + `pool_full_metrics.json` + `COLLECTED`
committed, `*.csv.gz` left in storage). `predictions.csv` holds the pre-round
GP mean / total sd per objective (calibration gates C2 / C3 at grading).
