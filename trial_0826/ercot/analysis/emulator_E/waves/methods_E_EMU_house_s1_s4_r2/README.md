# methods_E_EMU_house_s1_s4_r2 — methods_E acquisition round (prompt 55; NOT submitted by the writer)

Arm `qnehvi`, seed_id 4, round 2,
acq qnehvi seed 20261408; bo-gp 60e6328236e745b3d34dc8cd704bb72888ae5d15; botorch
0.16.1; guardrail_mode constrain. Created 2026-11-24T08:07:05+00:00.

Rows are `oat_site = __ALL__` multi-site designs (contract 5): `mw_<site>` /
`u_<site>` at full precision, `pem_mw = sum mw`, `tier = bo`. The retrofit dict
`retrofit_gen_dict_<i>.json` lists every site with mw > 0 (a site at exactly 0
is ABSENT). Bid 40.0 $/MWh, full year from 01-01-2019.

| row | MW 110 | MW 140 | MW 146 | MW 163 | MW 270 | MW 274 | sum MW | u 110 | u 140 | u 146 | u 163 | u 270 | u 274 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.000 | 250.600 | 0.000 | 185.400 | 579.000 | 65.974 | 1080.974 | 0.00000 | 1.00000 | 0.00000 | 1.00000 | 1.00000 | 0.08839 |
| 2 | 0.000 | 0.000 | 0.000 | 181.489 | 579.000 | 0.000 | 760.489 | 0.00000 | 0.00000 | 0.00000 | 0.97891 | 1.00000 | 0.00000 |
| 3 | 0.000 | 250.600 | 73.774 | 185.400 | 579.000 | 746.400 | 1835.174 | 0.00000 | 1.00000 | 0.27528 | 1.00000 | 1.00000 | 1.00000 |
| 4 | 134.488 | 0.000 | 0.000 | 185.400 | 579.000 | 0.000 | 898.888 | 0.39719 | 0.00000 | 0.00000 | 1.00000 | 1.00000 | 0.00000 |
| 5 | 0.000 | 0.000 | 0.000 | 185.400 | 154.511 | 746.400 | 1086.311 | 0.00000 | 0.00000 | 0.00000 | 1.00000 | 0.26686 | 1.00000 |
| 6 | 307.661 | 250.600 | 20.675 | 185.400 | 579.000 | 746.400 | 2089.735 | 0.90863 | 1.00000 | 0.07714 | 1.00000 | 1.00000 | 1.00000 |
| 7 | 337.777 | 250.600 | 130.128 | 185.400 | 579.000 | 746.400 | 2229.305 | 0.99757 | 1.00000 | 0.48555 | 1.00000 | 1.00000 | 1.00000 |
| 8 | 0.000 | 250.600 | 0.000 | 185.400 | 579.000 | 0.000 | 1015.000 | 0.00000 | 1.00000 | 0.00000 | 1.00000 | 1.00000 | 0.00000 |

Submission: Kay runs `bash analysis/methods_E/submit_ready_E.sh` on the CRC
login node (generic `methods_E_array.sh` + `methods_E_collect.sh`, `-v WAVE=methods_E_EMU_house_s1_s4_r2`,
`-wd trial_0826/ercot/waves`, identity from `waves/GAP_DECISION.json` at run
time, every row `--full`, slim tables + `pool_full_metrics.json` + `COLLECTED`
committed, `*.csv.gz` left in storage). `predictions.csv` holds the pre-round
GP mean / total sd per objective (calibration gates C2 / C3 at grading).
