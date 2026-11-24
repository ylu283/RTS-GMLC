# methods_E_EMU_mmB_s0_s0_r2 — methods_E acquisition round (prompt 55; NOT submitted by the writer)

Arm `qnehvi`, seed_id 0, round 2,
acq qnehvi seed 20261008; bo-gp 60e6328236e745b3d34dc8cd704bb72888ae5d15; botorch
0.16.1; guardrail_mode monitor. Created 2026-11-24T08:34:58+00:00.

Rows are `oat_site = __ALL__` multi-site designs (contract 5): `mw_<site>` /
`u_<site>` at full precision, `pem_mw = sum mw`, `tier = bo`. The retrofit dict
`retrofit_gen_dict_<i>.json` lists every site with mw > 0 (a site at exactly 0
is ABSENT). Bid 40.0 $/MWh, full year from 01-01-2019.

| row | MW 110 | MW 140 | MW 146 | MW 163 | MW 270 | MW 274 | sum MW | u 110 | u 140 | u 146 | u 163 | u 270 | u 274 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.000 | 0.000 | 0.000 | 27.753 | 0.000 | 746.400 | 774.153 | 0.00000 | 0.00000 | 0.00000 | 0.14969 | 0.00000 | 1.00000 |
| 2 | 0.000 | 29.416 | 0.000 | 185.400 | 579.000 | 746.400 | 1540.216 | 0.00000 | 0.11738 | 0.00000 | 1.00000 | 1.00000 | 1.00000 |
| 3 | 0.000 | 250.600 | 73.822 | 185.400 | 579.000 | 746.400 | 1835.222 | 0.00000 | 1.00000 | 0.27545 | 1.00000 | 1.00000 | 1.00000 |
| 4 | 0.000 | 250.600 | 0.000 | 185.400 | 0.000 | 746.400 | 1182.400 | 0.00000 | 1.00000 | 0.00000 | 1.00000 | 0.00000 | 1.00000 |
| 5 | 102.394 | 0.000 | 0.000 | 185.400 | 579.000 | 0.000 | 866.794 | 0.30240 | 0.00000 | 0.00000 | 1.00000 | 1.00000 | 0.00000 |
| 6 | 31.525 | 250.600 | 198.102 | 185.400 | 579.000 | 746.400 | 1991.027 | 0.09310 | 1.00000 | 0.73919 | 1.00000 | 1.00000 | 1.00000 |
| 7 | 0.000 | 0.000 | 0.000 | 185.400 | 579.000 | 476.095 | 1240.495 | 0.00000 | 0.00000 | 0.00000 | 1.00000 | 1.00000 | 0.63786 |
| 8 | 148.862 | 250.600 | 206.048 | 185.400 | 579.000 | 746.400 | 2116.310 | 0.43964 | 1.00000 | 0.76884 | 1.00000 | 1.00000 | 1.00000 |

Submission: Kay runs `bash analysis/methods_E/submit_ready_E.sh` on the CRC
login node (generic `methods_E_array.sh` + `methods_E_collect.sh`, `-v WAVE=methods_E_EMU_mmB_s0_s0_r2`,
`-wd trial_0826/ercot/waves`, identity from `waves/GAP_DECISION.json` at run
time, every row `--full`, slim tables + `pool_full_metrics.json` + `COLLECTED`
committed, `*.csv.gz` left in storage). `predictions.csv` holds the pre-round
GP mean / total sd per objective (calibration gates C2 / C3 at grading).
