# methods_E_EMU_committed_s0_s3_r4 — methods_E acquisition round (prompt 55; NOT submitted by the writer)

Arm `qnehvi`, seed_id 3, round 4,
acq qnehvi seed 20261310; bo-gp 60e6328236e745b3d34dc8cd704bb72888ae5d15; botorch
0.16.1; guardrail_mode monitor. Created 2026-11-24T08:36:20+00:00.

Rows are `oat_site = __ALL__` multi-site designs (contract 5): `mw_<site>` /
`u_<site>` at full precision, `pem_mw = sum mw`, `tier = bo`. The retrofit dict
`retrofit_gen_dict_<i>.json` lists every site with mw > 0 (a site at exactly 0
is ABSENT). Bid 40.0 $/MWh, full year from 01-01-2019.

| row | MW 110 | MW 140 | MW 146 | MW 163 | MW 270 | MW 274 | sum MW | u 110 | u 140 | u 146 | u 163 | u 270 | u 274 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.000 | 79.282 | 0.000 | 185.400 | 579.000 | 746.400 | 1590.082 | 0.00000 | 0.31637 | 0.00000 | 1.00000 | 1.00000 | 1.00000 |
| 2 | 115.113 | 250.600 | 213.858 | 185.400 | 579.000 | 746.400 | 2090.372 | 0.33997 | 1.00000 | 0.79798 | 1.00000 | 1.00000 | 1.00000 |
| 3 | 0.000 | 0.000 | 0.000 | 185.400 | 579.000 | 486.558 | 1250.958 | 0.00000 | 0.00000 | 0.00000 | 1.00000 | 1.00000 | 0.65187 |
| 4 | 338.600 | 0.000 | 0.000 | 0.000 | 579.000 | 0.000 | 917.600 | 1.00000 | 0.00000 | 0.00000 | 0.00000 | 1.00000 | 0.00000 |
| 5 | 338.600 | 250.600 | 0.855 | 185.400 | 579.000 | 746.400 | 2100.855 | 1.00000 | 1.00000 | 0.00319 | 1.00000 | 1.00000 | 1.00000 |
| 6 | 0.000 | 250.600 | 115.492 | 185.400 | 579.000 | 746.400 | 1876.892 | 0.00000 | 1.00000 | 0.43094 | 1.00000 | 1.00000 | 1.00000 |
| 7 | 338.600 | 250.600 | 73.547 | 185.400 | 579.000 | 746.400 | 2173.547 | 1.00000 | 1.00000 | 0.27443 | 1.00000 | 1.00000 | 1.00000 |
| 8 | 338.600 | 250.600 | 32.457 | 185.400 | 579.000 | 746.400 | 2132.457 | 1.00000 | 1.00000 | 0.12111 | 1.00000 | 1.00000 | 1.00000 |

Submission: Kay runs `bash analysis/methods_E/submit_ready_E.sh` on the CRC
login node (generic `methods_E_array.sh` + `methods_E_collect.sh`, `-v WAVE=methods_E_EMU_committed_s0_s3_r4`,
`-wd trial_0826/ercot/waves`, identity from `waves/GAP_DECISION.json` at run
time, every row `--full`, slim tables + `pool_full_metrics.json` + `COLLECTED`
committed, `*.csv.gz` left in storage). `predictions.csv` holds the pre-round
GP mean / total sd per objective (calibration gates C2 / C3 at grading).
