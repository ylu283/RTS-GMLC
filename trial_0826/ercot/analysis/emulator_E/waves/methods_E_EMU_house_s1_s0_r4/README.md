# methods_E_EMU_house_s1_s0_r4 — methods_E acquisition round (prompt 55; NOT submitted by the writer)

Arm `qnehvi`, seed_id 0, round 4,
acq qnehvi seed 20261010; bo-gp 60e6328236e745b3d34dc8cd704bb72888ae5d15; botorch
0.16.1; guardrail_mode constrain. Created 2026-11-24T07:45:05+00:00.

Rows are `oat_site = __ALL__` multi-site designs (contract 5): `mw_<site>` /
`u_<site>` at full precision, `pem_mw = sum mw`, `tier = bo`. The retrofit dict
`retrofit_gen_dict_<i>.json` lists every site with mw > 0 (a site at exactly 0
is ABSENT). Bid 40.0 $/MWh, full year from 01-01-2019.

| row | MW 110 | MW 140 | MW 146 | MW 163 | MW 270 | MW 274 | sum MW | u 110 | u 140 | u 146 | u 163 | u 270 | u 274 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 254.257 | 0.000 | 0.000 | 185.400 | 579.000 | 3.437 | 1022.094 | 0.75091 | 0.00000 | 0.00000 | 1.00000 | 1.00000 | 0.00460 |
| 2 | 0.000 | 250.600 | 0.000 | 185.400 | 0.000 | 746.400 | 1182.400 | 0.00000 | 1.00000 | 0.00000 | 1.00000 | 0.00000 | 1.00000 |
| 3 | 218.436 | 250.600 | 212.618 | 185.400 | 579.000 | 746.400 | 2192.453 | 0.64511 | 1.00000 | 0.79335 | 1.00000 | 1.00000 | 1.00000 |
| 4 | 338.600 | 0.000 | 0.000 | 185.400 | 579.000 | 746.400 | 1849.400 | 1.00000 | 0.00000 | 0.00000 | 1.00000 | 1.00000 | 1.00000 |
| 5 | 90.597 | 0.000 | 0.000 | 185.400 | 579.000 | 0.000 | 854.997 | 0.26756 | 0.00000 | 0.00000 | 1.00000 | 1.00000 | 0.00000 |
| 6 | 0.000 | 0.000 | 0.000 | 185.400 | 383.231 | 746.400 | 1315.031 | 0.00000 | 0.00000 | 0.00000 | 1.00000 | 0.66188 | 1.00000 |
| 7 | 0.000 | 250.600 | 113.727 | 185.400 | 579.000 | 746.400 | 1875.127 | 0.00000 | 1.00000 | 0.42436 | 1.00000 | 1.00000 | 1.00000 |
| 8 | 8.449 | 250.600 | 195.782 | 185.400 | 579.000 | 746.400 | 1965.631 | 0.02495 | 1.00000 | 0.73053 | 1.00000 | 1.00000 | 1.00000 |

Submission: Kay runs `bash analysis/methods_E/submit_ready_E.sh` on the CRC
login node (generic `methods_E_array.sh` + `methods_E_collect.sh`, `-v WAVE=methods_E_EMU_house_s1_s0_r4`,
`-wd trial_0826/ercot/waves`, identity from `waves/GAP_DECISION.json` at run
time, every row `--full`, slim tables + `pool_full_metrics.json` + `COLLECTED`
committed, `*.csv.gz` left in storage). `predictions.csv` holds the pre-round
GP mean / total sd per objective (calibration gates C2 / C3 at grading).
