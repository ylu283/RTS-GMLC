# n0_E / random_E — landing report (prompt 53 v3.1 §2.8)

Zero simulation. Built by `tools/land_ercot_n0.py` from the collector
commits (`extracts/n0_E/COLLECTED`: 48 rows, 2026-11-15T05:53Z;
`extracts/random_E/COLLECTED`: 48 rows, 2026-11-15T07:02Z) through the
unchanged reader (`pool_standings.build_wave` → `pool_objectives.build_pool`;
`pool_definitions.json` asserted equal to freeze f76d897; E8 / E9 / N5 from the
CRC `pool_full_metrics.json`, R7 / R8 / G_run / overall md5 asserted equal to
the local slim recomputation on every row). Per-run table:
`landing_rows.csv` (96 rows). Ref point: `landing_R.json` (contract §6.4).

## 1. Success, identity, SUSPECT, guardrails (per run in `landing_rows.csv`)

| wave | rows landed | identity v3 | SUSPECT | S1 / S2 / S3 fails | max S1 resid $ | RUCs OPTIMAL | RUCs at time limit | max final gap % | R1 shed max MWh (violations > 1) | R2 max MWh (flags > 891.8) |
|---|---|---|---|---|---|---|---|---|---|---|
| n0_E | 48 / 48 | 48 | 0 | 0 / 0 / 0 | 9.54e-07 | 17,520 / 17,520 | 0 | 0.100 | 0 (0) | 170.2 (0) |
| random_E | 48 / 48 | 48 | 0 | 0 / 0 / 0 | 1.91e-06 | 17,520 / 17,520 | 0 | 0.100 | 0 (0) | 199.9 (0) |

- **SUSPECT (plan §1.2 S1–S3): 0 of 96.** S3 here = gen-1 and gen-93 starts
  are 0 on every run (no nuclear retrofit; no exact replicates in these
  waves); every row is a distinct design (96 distinct `overall.csv` md5s over the 96).
- **R1 load shed: 0 MWh on every one of the 96 runs** (expected 0; plan §1.3
  violation = shed > 1 MWh: none). R1 is DEAD on the
  grading tier, as on every earlier wave; the constrained-qNEHVI switch is
  not triggered.
- **R2 reserve shortfall:** max 199.9 MWh, far below the round
  flag 2 × base = 891.8 MWh; no flag.
- `full_extract` true on all 96 (`--full`; gz tables in $GROUP storage).

## 2. Wall-clock (`extracts/<wave>/wallclock.csv`; 4 slots, core-h = wall × 4)

Node groups split at 25,000 s wall (the wave-D split).

| wave | group | runs | wall h | core-h | RUC median solve s (median) | RUC max solve s |
|---|---|---|---|---|---|---|
| n0_E | A (fast) | 16 | 4.62 – 4.97 | 18.5 – 19.9 (mean 19.1) | 17.9 | 416 |
| n0_E | B (slow) | 32 | 9.38 – 10.46 | 37.5 – 41.9 (mean 39.4) | 42.3 | 824 |
| n0_E | **all** | 48 | 4.62 – 10.46 | **1,566 total** (mean 32.6) | 40.4 | 824 |
| n0_E | calendar | | 10.5 h (11-14 17:29 → 11-15 03:57 UTC) | | | |
| random_E | A (fast) | 22 | 4.51 – 5.10 | 18.0 – 20.4 (mean 18.9) | 17.6 | 403 |
| random_E | B (slow) | 26 | 9.00 – 10.66 | 36.0 – 42.6 (mean 39.4) | 41.8 | 1157 |
| random_E | **all** | 48 | 4.51 – 10.66 | **1,440 total** (mean 30.0) | 38.8 | 1157 |
| random_E | calendar | | 12.3 h (11-14 17:30 → 11-15 05:47 UTC) | | | |

**Total: 3,006 core-h for 96 runs (31.3 per run)**, inside the
2.0–4.3k bracket that AMENDMENT 2026-11-14 projected from wave D. The 6-site rows
run at about the wave-D per-node speeds (fast 4.5–5.1 h, slow
9.0–10.7 h; wave D 5.1–5.5 / 10.5–11.8 h); 58 of 96 landed on slow nodes
(wave D: 6 of 21), which is why the mean per run sits above wave D's fast 21.

**RUC solve-time margin (disclosed).** The longest RUC solve is
1157 s (random_E:22, slow node) against `ruc_time_limit` = 1200 s,
status OPTIMAL, 0 time-limit statuses on all 35,040 RUCs. The solve-time
column includes model build (standings §8), so this is not a limit hit, but
the margin on a slow node is ≈ 4 %, not the ≈ 25× of the January smoke cited
in AMENDMENT 2026-11-06b. Any later TIME_LIMIT status is caught by S2
(SUSPECT) per run.

## 3. HV reference point R (plan §6.3; `landing_R.json`)

Over the **48 grading rows** (`n0_E`, `sobol_index` 0–47), for **all 29 pool
candidates** (contract §6.4: a later objective-list version never reopens
§6.3). R = nadir + 0.1 (nadir - ideal) per objective over the 48 grading rows (plan §6.3). All objectives minimized: dir `max` candidates are minimized
as −x and reported in raw units (ideal = max, nadir = min, R = min −
0.1 (max − min)); dir `-` candidates have no direction in
`pool_definitions.json` and are computed as if minimized (flagged). D3 =
gen-1 + gen-93 starts. Prompt 55 Part B asserts these values at init.
E3 is listed too: the cost seat is E1 if prompt 52's §1.2 verdict is READABLE, else E3 (both R values are pinned here, so either verdict reads R from this file).

| id | dir | unit | ideal | nadir | R | note |
|---|---|---|---|---|---|---|
| V1 | min | MWh | 1.4091e+06 | 3.7440e+06 | **3.9775e+06** | seat (E-D1b)  |
| E1 | min | $ | 8.1076e+09 | 8.1586e+09 | **8.1637e+09** | seat (E-D1b)  |
| X1 | min | t | 1.9605e+08 | 1.9766e+08 | **1.9782e+08** |   |
| R4 | min | count | 14,684 | 15,225 | **15,279.1** | seat (E-D1b)  |
| N1 | min | line-h | 34,666 | 35,941 | **36,068.5** | seat (E-D1b)  |
| E4 | min | $ | 1.4128e+10 | 1.4283e+10 | **1.4299e+10** |   |
| R2 | min | MWh | 42.6912 | 170.1577 | **182.9043** |   |
| R7 | - | MWh | 3.5846e+08 | 3.6044e+08 | **3.6063e+08** |  dir '-' in pool_definitions.json: computed as minimized; a seat needs a direction first |
| N4 | min | line-h | 3,777 | 4,936 | **5,051.9** |   |
| N5 | min | $/MWh | -15.4759 | -9.6201 | **-9.0346** |   |
| E6 | max | $ | 2.7055e+09 | 2.6264e+09 | **2.6184e+09** |   |
| R5 | min | MW | 1.4982e+06 | 1.5245e+06 | **1.5271e+06** |   |
| N3 | min | MWh | 90,947.6036 | 90,960.8866 | **90,962.2149** |   |
| E2 | min | $ | 3.5761e+09 | 3.5915e+09 | **3.5930e+09** |   |
| R6 | min | MW | 1.5248e+07 | 1.5420e+07 | **1.5437e+07** |   |
| N2 | min | count | 34 | 38 | **38.4** |   |
| E3 | min | $ | 4.5301e+09 | 4.5684e+09 | **4.5723e+09** |   |
| R8 | - | unit-h | 4.3918e+05 | 4.4230e+05 | **4.4261e+05** |  dir '-' in pool_definitions.json: computed as minimized; a seat needs a direction first |
| E7 | - | $/MWh | 36.6299 | 37.0563 | **37.0989** |  dir '-' in pool_definitions.json: computed as minimized; a seat needs a direction first |
| E8 | min | $/MWh | 14.3971 | 15.0003 | **15.0606** |   |
| E9 | min | count | 0 | 1 | **1.1** |   |
| V2 | max | % | 22.3511 | 21.7978 | **21.7425** |   |
| V3 | - | fraction | 0.0027 | 0.0066 | **0.007** |  dir '-' in pool_definitions.json: computed as minimized; a seat needs a direction first |
| E5 | min | $ | 0 | 0 | **0** |  zero range on the 48 grading rows (value 0): R = nadir |
| R1 | min | MWh | 0 | 0 | **0** |  zero range on the 48 grading rows (value 0): R = nadir |
| R3 | min | MWh | 0 | 0 | **0** |  zero range on the 48 grading rows (value 0): R = nadir |
| D1 | - | MWh | 4.0147e+06 | 8.4591e+06 | **8.9036e+06** |  dir '-' in pool_definitions.json: computed as minimized; a seat needs a direction first |
| D2 | - | fraction | 0.5036 | 0.699 | **0.7185** |  dir '-' in pool_definitions.json: computed as minimized; a seat needs a direction first |
| D3 | - | count | 0 | 0 | **0** |  dir '-' in pool_definitions.json: computed as minimized; a seat needs a direction first; zero range on the 48 grading rows (value 0): R = nadir |

The R values use the grading tier only; R does not depend on E-D7 (nav 32
or 48). The holdout rows (random_E) are NOT used for R. They are model-free
here: no model has been scored against them, so this report spends none of
the 24-scoring exposure budget.

## 4. Budget actuals

Appended to the plan as AMENDMENT 2026-11-16 (n0_E + random_E actuals).
