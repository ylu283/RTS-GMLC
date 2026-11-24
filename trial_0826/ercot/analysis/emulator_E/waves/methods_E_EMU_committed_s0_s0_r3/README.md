# methods_E_EMU_committed_s0_s0_r3 — methods_E acquisition round (prompt 55; NOT submitted by the writer)

Arm `qnehvi`, seed_id 0, round 3,
acq qnehvi seed 20261009; bo-gp 60e6328236e745b3d34dc8cd704bb72888ae5d15; botorch
0.16.1; guardrail_mode monitor. Created 2026-11-24T08:34:29+00:00.

Rows are `oat_site = __ALL__` multi-site designs (contract 5): `mw_<site>` /
`u_<site>` at full precision, `pem_mw = sum mw`, `tier = bo`. The retrofit dict
`retrofit_gen_dict_<i>.json` lists every site with mw > 0 (a site at exactly 0
is ABSENT). Bid 40.0 $/MWh, full year from 01-01-2019.

| row | MW 110 | MW 140 | MW 146 | MW 163 | MW 270 | MW 274 | sum MW | u 110 | u 140 | u 146 | u 163 | u 270 | u 274 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.000 | 250.600 | 0.000 | 0.000 | 579.000 | 0.000 | 829.600 | 0.00000 | 1.00000 | 0.00000 | 0.00000 | 1.00000 | 0.00000 |
| 2 | 0.000 | 250.600 | 0.000 | 185.400 | 0.000 | 746.400 | 1182.400 | 0.00000 | 1.00000 | 0.00000 | 1.00000 | 0.00000 | 1.00000 |
| 3 | 0.000 | 250.600 | 114.134 | 185.400 | 579.000 | 746.400 | 1875.534 | 0.00000 | 1.00000 | 0.42587 | 1.00000 | 1.00000 | 1.00000 |
| 4 | 0.000 | 250.600 | 0.000 | 55.739 | 579.000 | 746.400 | 1631.739 | 0.00000 | 1.00000 | 0.00000 | 0.30064 | 1.00000 | 1.00000 |
| 5 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 746.400 | 746.400 | 0.00000 | 0.00000 | 0.00000 | 0.00000 | 0.00000 | 1.00000 |
| 6 | 0.000 | 0.000 | 268.000 | 185.400 | 0.000 | 746.400 | 1199.800 | 0.00000 | 0.00000 | 1.00000 | 1.00000 | 0.00000 | 1.00000 |
| 7 | 338.600 | 0.000 | 0.000 | 185.400 | 579.000 | 746.400 | 1849.400 | 1.00000 | 0.00000 | 0.00000 | 1.00000 | 1.00000 | 1.00000 |
| 8 | 128.419 | 250.600 | 193.055 | 185.400 | 579.000 | 746.400 | 2082.874 | 0.37927 | 1.00000 | 0.72035 | 1.00000 | 1.00000 | 1.00000 |

Submission: Kay runs `bash analysis/methods_E/submit_ready_E.sh` on the CRC
login node (generic `methods_E_array.sh` + `methods_E_collect.sh`, `-v WAVE=methods_E_EMU_committed_s0_s0_r3`,
`-wd trial_0826/ercot/waves`, identity from `waves/GAP_DECISION.json` at run
time, every row `--full`, slim tables + `pool_full_metrics.json` + `COLLECTED`
committed, `*.csv.gz` left in storage). `predictions.csv` holds the pre-round
GP mean / total sd per objective (calibration gates C2 / C3 at grading).
