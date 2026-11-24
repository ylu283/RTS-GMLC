# methods_E_EMU_house_s0_s0_r4 — methods_E acquisition round (prompt 55; NOT submitted by the writer)

Arm `qnehvi`, seed_id 0, round 4,
acq qnehvi seed 20261010; bo-gp 60e6328236e745b3d34dc8cd704bb72888ae5d15; botorch
0.16.1; guardrail_mode monitor. Created 2026-11-24T08:04:44+00:00.

Rows are `oat_site = __ALL__` multi-site designs (contract 5): `mw_<site>` /
`u_<site>` at full precision, `pem_mw = sum mw`, `tier = bo`. The retrofit dict
`retrofit_gen_dict_<i>.json` lists every site with mw > 0 (a site at exactly 0
is ABSENT). Bid 40.0 $/MWh, full year from 01-01-2019.

| row | MW 110 | MW 140 | MW 146 | MW 163 | MW 270 | MW 274 | sum MW | u 110 | u 140 | u 146 | u 163 | u 270 | u 274 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 135.653 | 250.600 | 224.909 | 185.400 | 579.000 | 746.400 | 2121.962 | 0.40063 | 1.00000 | 0.83921 | 1.00000 | 1.00000 | 1.00000 |
| 2 | 0.000 | 0.000 | 268.000 | 185.400 | 0.000 | 746.400 | 1199.800 | 0.00000 | 0.00000 | 1.00000 | 1.00000 | 0.00000 | 1.00000 |
| 3 | 338.600 | 0.000 | 0.000 | 185.400 | 579.000 | 746.400 | 1849.400 | 1.00000 | 0.00000 | 0.00000 | 1.00000 | 1.00000 | 1.00000 |
| 4 | 0.000 | 250.600 | 33.952 | 185.400 | 579.000 | 746.400 | 1795.352 | 0.00000 | 1.00000 | 0.12669 | 1.00000 | 1.00000 | 1.00000 |
| 5 | 184.750 | 0.000 | 0.000 | 185.400 | 579.000 | 0.000 | 949.150 | 0.54563 | 0.00000 | 0.00000 | 1.00000 | 1.00000 | 0.00000 |
| 6 | 0.000 | 0.000 | 0.000 | 66.752 | 579.000 | 0.000 | 645.752 | 0.00000 | 0.00000 | 0.00000 | 0.36004 | 1.00000 | 0.00000 |
| 7 | 0.000 | 250.600 | 113.003 | 185.400 | 579.000 | 746.400 | 1874.403 | 0.00000 | 1.00000 | 0.42165 | 1.00000 | 1.00000 | 1.00000 |
| 8 | 0.000 | 0.000 | 0.000 | 185.400 | 579.000 | 589.257 | 1353.657 | 0.00000 | 0.00000 | 0.00000 | 1.00000 | 1.00000 | 0.78946 |

Submission: Kay runs `bash analysis/methods_E/submit_ready_E.sh` on the CRC
login node (generic `methods_E_array.sh` + `methods_E_collect.sh`, `-v WAVE=methods_E_EMU_house_s0_s0_r4`,
`-wd trial_0826/ercot/waves`, identity from `waves/GAP_DECISION.json` at run
time, every row `--full`, slim tables + `pool_full_metrics.json` + `COLLECTED`
committed, `*.csv.gz` left in storage). `predictions.csv` holds the pre-round
GP mean / total sd per objective (calibration gates C2 / C3 at grading).
