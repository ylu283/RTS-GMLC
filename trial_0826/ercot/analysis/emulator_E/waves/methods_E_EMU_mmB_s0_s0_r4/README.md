# methods_E_EMU_mmB_s0_s0_r4 — methods_E acquisition round (prompt 55; NOT submitted by the writer)

Arm `qnehvi`, seed_id 0, round 4,
acq qnehvi seed 20261010; bo-gp 60e6328236e745b3d34dc8cd704bb72888ae5d15; botorch
0.16.1; guardrail_mode monitor. Created 2026-11-24T08:35:12+00:00.

Rows are `oat_site = __ALL__` multi-site designs (contract 5): `mw_<site>` /
`u_<site>` at full precision, `pem_mw = sum mw`, `tier = bo`. The retrofit dict
`retrofit_gen_dict_<i>.json` lists every site with mw > 0 (a site at exactly 0
is ABSENT). Bid 40.0 $/MWh, full year from 01-01-2019.

| row | MW 110 | MW 140 | MW 146 | MW 163 | MW 270 | MW 274 | sum MW | u 110 | u 140 | u 146 | u 163 | u 270 | u 274 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 46.033 | 250.600 | 223.276 | 185.400 | 579.000 | 746.400 | 2030.709 | 0.13595 | 1.00000 | 0.83312 | 1.00000 | 1.00000 | 1.00000 |
| 2 | 0.000 | 196.995 | 0.000 | 185.400 | 0.000 | 746.400 | 1128.795 | 0.00000 | 0.78610 | 0.00000 | 1.00000 | 0.00000 | 1.00000 |
| 3 | 0.000 | 0.000 | 0.000 | 124.186 | 0.000 | 746.400 | 870.586 | 0.00000 | 0.00000 | 0.00000 | 0.66983 | 0.00000 | 1.00000 |
| 4 | 338.600 | 250.600 | 101.758 | 185.400 | 579.000 | 746.400 | 2201.758 | 1.00000 | 1.00000 | 0.37969 | 1.00000 | 1.00000 | 1.00000 |
| 5 | 338.600 | 250.600 | 0.000 | 185.400 | 579.000 | 746.400 | 2100.000 | 1.00000 | 1.00000 | 0.00000 | 1.00000 | 1.00000 | 1.00000 |
| 6 | 338.600 | 0.000 | 0.000 | 0.000 | 0.000 | 746.400 | 1085.000 | 1.00000 | 0.00000 | 0.00000 | 0.00000 | 0.00000 | 1.00000 |
| 7 | 176.407 | 247.920 | 190.794 | 139.159 | 579.000 | 746.400 | 2079.681 | 0.52099 | 0.98931 | 0.71192 | 0.75059 | 1.00000 | 1.00000 |
| 8 | 324.207 | 66.906 | 123.441 | 177.639 | 566.086 | 682.149 | 1940.429 | 0.95749 | 0.26698 | 0.46060 | 0.95814 | 0.97770 | 0.91392 |

Submission: Kay runs `bash analysis/methods_E/submit_ready_E.sh` on the CRC
login node (generic `methods_E_array.sh` + `methods_E_collect.sh`, `-v WAVE=methods_E_EMU_mmB_s0_s0_r4`,
`-wd trial_0826/ercot/waves`, identity from `waves/GAP_DECISION.json` at run
time, every row `--full`, slim tables + `pool_full_metrics.json` + `COLLECTED`
committed, `*.csv.gz` left in storage). `predictions.csv` holds the pre-round
GP mean / total sd per objective (calibration gates C2 / C3 at grading).
