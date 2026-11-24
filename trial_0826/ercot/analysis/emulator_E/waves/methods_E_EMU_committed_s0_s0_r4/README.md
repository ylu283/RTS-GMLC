# methods_E_EMU_committed_s0_s0_r4 — methods_E acquisition round (prompt 55; NOT submitted by the writer)

Arm `qnehvi`, seed_id 0, round 4,
acq qnehvi seed 20261010; bo-gp 60e6328236e745b3d34dc8cd704bb72888ae5d15; botorch
0.16.1; guardrail_mode monitor. Created 2026-11-24T08:34:39+00:00.

Rows are `oat_site = __ALL__` multi-site designs (contract 5): `mw_<site>` /
`u_<site>` at full precision, `pem_mw = sum mw`, `tier = bo`. The retrofit dict
`retrofit_gen_dict_<i>.json` lists every site with mw > 0 (a site at exactly 0
is ABSENT). Bid 40.0 $/MWh, full year from 01-01-2019.

| row | MW 110 | MW 140 | MW 146 | MW 163 | MW 270 | MW 274 | sum MW | u 110 | u 140 | u 146 | u 163 | u 270 | u 274 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 201.000 | 250.600 | 202.250 | 180.463 | 579.000 | 746.400 | 2159.712 | 0.59362 | 1.00000 | 0.75466 | 0.97337 | 1.00000 | 1.00000 |
| 2 | 66.247 | 250.600 | 186.121 | 185.400 | 579.000 | 746.400 | 2013.768 | 0.19565 | 1.00000 | 0.69448 | 1.00000 | 1.00000 | 1.00000 |
| 3 | 0.000 | 56.194 | 0.000 | 185.400 | 0.000 | 746.400 | 987.994 | 0.00000 | 0.22424 | 0.00000 | 1.00000 | 0.00000 | 1.00000 |
| 4 | 338.600 | 250.600 | 137.486 | 137.612 | 579.000 | 746.400 | 2189.698 | 1.00000 | 1.00000 | 0.51301 | 0.74225 | 1.00000 | 1.00000 |
| 5 | 338.600 | 0.000 | 0.000 | 185.400 | 0.000 | 746.400 | 1270.400 | 1.00000 | 0.00000 | 0.00000 | 1.00000 | 0.00000 | 1.00000 |
| 6 | 338.600 | 250.600 | 80.209 | 127.633 | 579.000 | 746.400 | 2122.442 | 1.00000 | 1.00000 | 0.29929 | 0.68842 | 1.00000 | 1.00000 |
| 7 | 0.000 | 250.600 | 35.605 | 185.400 | 579.000 | 746.400 | 1797.005 | 0.00000 | 1.00000 | 0.13285 | 1.00000 | 1.00000 | 1.00000 |
| 8 | 13.630 | 250.600 | 180.719 | 185.400 | 579.000 | 746.400 | 1955.749 | 0.04025 | 1.00000 | 0.67433 | 1.00000 | 1.00000 | 1.00000 |

Submission: Kay runs `bash analysis/methods_E/submit_ready_E.sh` on the CRC
login node (generic `methods_E_array.sh` + `methods_E_collect.sh`, `-v WAVE=methods_E_EMU_committed_s0_s0_r4`,
`-wd trial_0826/ercot/waves`, identity from `waves/GAP_DECISION.json` at run
time, every row `--full`, slim tables + `pool_full_metrics.json` + `COLLECTED`
committed, `*.csv.gz` left in storage). `predictions.csv` holds the pre-round
GP mean / total sd per objective (calibration gates C2 / C3 at grading).
