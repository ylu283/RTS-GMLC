# methods_E_EMU_committed_s0_s2_r3 — methods_E acquisition round (prompt 55; NOT submitted by the writer)

Arm `qnehvi`, seed_id 2, round 3,
acq qnehvi seed 20261209; bo-gp 60e6328236e745b3d34dc8cd704bb72888ae5d15; botorch
0.16.1; guardrail_mode monitor. Created 2026-11-24T08:35:38+00:00.

Rows are `oat_site = __ALL__` multi-site designs (contract 5): `mw_<site>` /
`u_<site>` at full precision, `pem_mw = sum mw`, `tier = bo`. The retrofit dict
`retrofit_gen_dict_<i>.json` lists every site with mw > 0 (a site at exactly 0
is ABSENT). Bid 40.0 $/MWh, full year from 01-01-2019.

| row | MW 110 | MW 140 | MW 146 | MW 163 | MW 270 | MW 274 | sum MW | u 110 | u 140 | u 146 | u 163 | u 270 | u 274 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.000 | 0.000 | 0.000 | 0.000 | 579.000 | 746.400 | 1325.400 | 0.00000 | 0.00000 | 0.00000 | 0.00000 | 1.00000 | 1.00000 |
| 2 | 0.000 | 250.600 | 115.917 | 185.400 | 579.000 | 746.400 | 1877.317 | 0.00000 | 1.00000 | 0.43253 | 1.00000 | 1.00000 | 1.00000 |
| 3 | 0.000 | 162.395 | 0.000 | 185.400 | 579.000 | 0.000 | 926.795 | 0.00000 | 0.64802 | 0.00000 | 1.00000 | 1.00000 | 0.00000 |
| 4 | 67.795 | 250.600 | 184.565 | 185.400 | 579.000 | 746.400 | 2013.759 | 0.20022 | 1.00000 | 0.68867 | 1.00000 | 1.00000 | 1.00000 |
| 5 | 203.487 | 250.600 | 189.547 | 184.799 | 579.000 | 746.400 | 2153.833 | 0.60097 | 1.00000 | 0.70726 | 0.99676 | 1.00000 | 1.00000 |
| 6 | 0.000 | 250.600 | 36.146 | 185.400 | 579.000 | 746.400 | 1797.546 | 0.00000 | 1.00000 | 0.13487 | 1.00000 | 1.00000 | 1.00000 |
| 7 | 338.600 | 0.000 | 0.000 | 185.400 | 0.000 | 746.400 | 1270.400 | 1.00000 | 0.00000 | 0.00000 | 1.00000 | 0.00000 | 1.00000 |
| 8 | 12.115 | 250.600 | 185.888 | 185.400 | 579.000 | 746.400 | 1959.403 | 0.03578 | 1.00000 | 0.69361 | 1.00000 | 1.00000 | 1.00000 |

Submission: Kay runs `bash analysis/methods_E/submit_ready_E.sh` on the CRC
login node (generic `methods_E_array.sh` + `methods_E_collect.sh`, `-v WAVE=methods_E_EMU_committed_s0_s2_r3`,
`-wd trial_0826/ercot/waves`, identity from `waves/GAP_DECISION.json` at run
time, every row `--full`, slim tables + `pool_full_metrics.json` + `COLLECTED`
committed, `*.csv.gz` left in storage). `predictions.csv` holds the pre-round
GP mean / total sd per objective (calibration gates C2 / C3 at grading).
