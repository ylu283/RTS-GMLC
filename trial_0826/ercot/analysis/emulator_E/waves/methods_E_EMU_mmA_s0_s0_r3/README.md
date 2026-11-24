# methods_E_EMU_mmA_s0_s0_r3 — methods_E acquisition round (prompt 55; NOT submitted by the writer)

Arm `qnehvi`, seed_id 0, round 3,
acq qnehvi seed 20261009; bo-gp 60e6328236e745b3d34dc8cd704bb72888ae5d15; botorch
0.16.1; guardrail_mode monitor. Created 2026-11-24T08:34:29+00:00.

Rows are `oat_site = __ALL__` multi-site designs (contract 5): `mw_<site>` /
`u_<site>` at full precision, `pem_mw = sum mw`, `tier = bo`. The retrofit dict
`retrofit_gen_dict_<i>.json` lists every site with mw > 0 (a site at exactly 0
is ABSENT). Bid 40.0 $/MWh, full year from 01-01-2019.

| row | MW 110 | MW 140 | MW 146 | MW 163 | MW 270 | MW 274 | sum MW | u 110 | u 140 | u 146 | u 163 | u 270 | u 274 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.000 | 0.000 | 0.000 | 55.538 | 579.000 | 0.000 | 634.538 | 0.00000 | 0.00000 | 0.00000 | 0.29956 | 1.00000 | 0.00000 |
| 2 | 104.213 | 250.600 | 0.000 | 0.000 | 579.000 | 0.000 | 933.813 | 0.30778 | 1.00000 | 0.00000 | 0.00000 | 1.00000 | 0.00000 |
| 3 | 154.785 | 0.000 | 0.000 | 185.400 | 579.000 | 0.000 | 919.184 | 0.45713 | 0.00000 | 0.00000 | 1.00000 | 1.00000 | 0.00000 |
| 4 | 265.211 | 0.000 | 0.000 | 185.400 | 579.000 | 0.000 | 1029.611 | 0.78326 | 0.00000 | 0.00000 | 1.00000 | 1.00000 | 0.00000 |
| 5 | 0.000 | 97.043 | 0.000 | 185.400 | 579.000 | 746.400 | 1607.843 | 0.00000 | 0.38724 | 0.00000 | 1.00000 | 1.00000 | 1.00000 |
| 6 | 0.000 | 0.000 | 0.000 | 0.000 | 579.000 | 746.400 | 1325.400 | 0.00000 | 0.00000 | 0.00000 | 0.00000 | 1.00000 | 1.00000 |
| 7 | 236.647 | 250.600 | 194.587 | 185.400 | 579.000 | 746.400 | 2192.635 | 0.69890 | 1.00000 | 0.72607 | 1.00000 | 1.00000 | 1.00000 |
| 8 | 144.502 | 250.600 | 178.609 | 185.400 | 579.000 | 746.400 | 2084.511 | 0.42676 | 1.00000 | 0.66645 | 1.00000 | 1.00000 | 1.00000 |

Submission: Kay runs `bash analysis/methods_E/submit_ready_E.sh` on the CRC
login node (generic `methods_E_array.sh` + `methods_E_collect.sh`, `-v WAVE=methods_E_EMU_mmA_s0_s0_r3`,
`-wd trial_0826/ercot/waves`, identity from `waves/GAP_DECISION.json` at run
time, every row `--full`, slim tables + `pool_full_metrics.json` + `COLLECTED`
committed, `*.csv.gz` left in storage). `predictions.csv` holds the pre-round
GP mean / total sd per objective (calibration gates C2 / C3 at grading).
