# methods_E_EMU_committed_s1_s1_r4 — methods_E acquisition round (prompt 55; NOT submitted by the writer)

Arm `qnehvi`, seed_id 1, round 4,
acq qnehvi seed 20261110; bo-gp 60e6328236e745b3d34dc8cd704bb72888ae5d15; botorch
0.16.1; guardrail_mode constrain. Created 2026-11-24T08:35:26+00:00.

Rows are `oat_site = __ALL__` multi-site designs (contract 5): `mw_<site>` /
`u_<site>` at full precision, `pem_mw = sum mw`, `tier = bo`. The retrofit dict
`retrofit_gen_dict_<i>.json` lists every site with mw > 0 (a site at exactly 0
is ABSENT). Bid 40.0 $/MWh, full year from 01-01-2019.

| row | MW 110 | MW 140 | MW 146 | MW 163 | MW 270 | MW 274 | sum MW | u 110 | u 140 | u 146 | u 163 | u 270 | u 274 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 117.118 | 250.600 | 200.839 | 185.400 | 579.000 | 746.400 | 2079.356 | 0.34589 | 1.00000 | 0.74940 | 1.00000 | 1.00000 | 1.00000 |
| 2 | 338.600 | 159.927 | 141.654 | 185.400 | 579.000 | 746.400 | 2150.981 | 1.00000 | 0.63818 | 0.52856 | 1.00000 | 1.00000 | 1.00000 |
| 3 | 338.600 | 250.600 | 74.350 | 185.400 | 579.000 | 746.400 | 2174.350 | 1.00000 | 1.00000 | 0.27743 | 1.00000 | 1.00000 | 1.00000 |
| 4 | 338.600 | 0.000 | 0.000 | 185.400 | 579.000 | 746.400 | 1849.400 | 1.00000 | 0.00000 | 0.00000 | 1.00000 | 1.00000 | 1.00000 |
| 5 | 129.296 | 0.000 | 0.000 | 185.400 | 579.000 | 0.000 | 893.696 | 0.38185 | 0.00000 | 0.00000 | 1.00000 | 1.00000 | 0.00000 |
| 6 | 338.600 | 0.000 | 41.693 | 71.845 | 579.000 | 746.400 | 1777.538 | 1.00000 | 0.00000 | 0.15557 | 0.38751 | 1.00000 | 1.00000 |
| 7 | 166.517 | 250.600 | 206.173 | 185.400 | 579.000 | 746.400 | 2134.089 | 0.49178 | 1.00000 | 0.76930 | 1.00000 | 1.00000 | 1.00000 |
| 8 | 0.000 | 250.600 | 117.049 | 185.400 | 579.000 | 746.400 | 1878.449 | 0.00000 | 1.00000 | 0.43675 | 1.00000 | 1.00000 | 1.00000 |

Submission: Kay runs `bash analysis/methods_E/submit_ready_E.sh` on the CRC
login node (generic `methods_E_array.sh` + `methods_E_collect.sh`, `-v WAVE=methods_E_EMU_committed_s1_s1_r4`,
`-wd trial_0826/ercot/waves`, identity from `waves/GAP_DECISION.json` at run
time, every row `--full`, slim tables + `pool_full_metrics.json` + `COLLECTED`
committed, `*.csv.gz` left in storage). `predictions.csv` holds the pre-round
GP mean / total sd per objective (calibration gates C2 / C3 at grading).
