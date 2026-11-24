# methods_E_EMU_committed_s0_s4_r4 — methods_E acquisition round (prompt 55; NOT submitted by the writer)

Arm `qnehvi`, seed_id 4, round 4,
acq qnehvi seed 20261410; bo-gp 60e6328236e745b3d34dc8cd704bb72888ae5d15; botorch
0.16.1; guardrail_mode monitor. Created 2026-11-24T08:36:54+00:00.

Rows are `oat_site = __ALL__` multi-site designs (contract 5): `mw_<site>` /
`u_<site>` at full precision, `pem_mw = sum mw`, `tier = bo`. The retrofit dict
`retrofit_gen_dict_<i>.json` lists every site with mw > 0 (a site at exactly 0
is ABSENT). Bid 40.0 $/MWh, full year from 01-01-2019.

| row | MW 110 | MW 140 | MW 146 | MW 163 | MW 270 | MW 274 | sum MW | u 110 | u 140 | u 146 | u 163 | u 270 | u 274 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.000 | 250.600 | 36.429 | 185.400 | 579.000 | 746.400 | 1797.829 | 0.00000 | 1.00000 | 0.13593 | 1.00000 | 1.00000 | 1.00000 |
| 2 | 0.000 | 0.000 | 0.000 | 42.737 | 579.000 | 0.000 | 621.737 | 0.00000 | 0.00000 | 0.00000 | 0.23051 | 1.00000 | 0.00000 |
| 3 | 0.000 | 0.000 | 0.000 | 185.400 | 47.339 | 746.400 | 979.139 | 0.00000 | 0.00000 | 0.00000 | 1.00000 | 0.08176 | 1.00000 |
| 4 | 0.000 | 250.600 | 0.000 | 0.000 | 579.000 | 0.000 | 829.600 | 0.00000 | 1.00000 | 0.00000 | 0.00000 | 1.00000 | 0.00000 |
| 5 | 116.280 | 0.000 | 0.000 | 185.400 | 579.000 | 0.000 | 880.680 | 0.34341 | 0.00000 | 0.00000 | 1.00000 | 1.00000 | 0.00000 |
| 6 | 338.600 | 196.310 | 86.890 | 185.400 | 579.000 | 746.400 | 2132.600 | 1.00000 | 0.78336 | 0.32422 | 1.00000 | 1.00000 | 1.00000 |
| 7 | 338.600 | 250.600 | 138.937 | 146.951 | 579.000 | 746.400 | 2200.488 | 1.00000 | 1.00000 | 0.51842 | 0.79262 | 1.00000 | 1.00000 |
| 8 | 119.761 | 250.600 | 194.096 | 178.747 | 579.000 | 746.400 | 2068.604 | 0.35369 | 1.00000 | 0.72424 | 0.96412 | 1.00000 | 1.00000 |

Submission: Kay runs `bash analysis/methods_E/submit_ready_E.sh` on the CRC
login node (generic `methods_E_array.sh` + `methods_E_collect.sh`, `-v WAVE=methods_E_EMU_committed_s0_s4_r4`,
`-wd trial_0826/ercot/waves`, identity from `waves/GAP_DECISION.json` at run
time, every row `--full`, slim tables + `pool_full_metrics.json` + `COLLECTED`
committed, `*.csv.gz` left in storage). `predictions.csv` holds the pre-round
GP mean / total sd per objective (calibration gates C2 / C3 at grading).
