# Smoke gate — Prescient v2 vs authors' SCUC (reading c)

Prescient extract: `extracts/smoke_v2`. Authors: `authors_scuc_sidebyside.py` (Gurobi MIP 1 %, LP re-solve for prices). Gate per prompt 36 §3 AMENDMENT 10-12: cost ±15 % vs the authors' code as shipped (daily-minimum DLR) + RUC solves + LMP sanity band + shed. Static-rating rows and the LMP side-by-side are reported, not gated.

## Gate

| check | result |
|---|---|
| cost within ±15% of authors (DLR), 3 day(s) | PASS |
| every RUC OPTIMAL or gap <= 1 % | PASS |
| RT system-mean LMP in $10–60/MWh every day | PASS |
| zero load shed (known pattern) | PASS |

**Gate: PASS**

## Daily production cost (gated vs DLR) and LMP side-by-side (reported only)

| day | authors ratings | Prescient prod. cost $ | authors cost $ | Δ cost | cost gate | Prescient RT mean LMP | authors mean LMP | Δ LMP |
|---|---|---|---|---|---|---|---|---|
| 2019-01-01 | dlr | 18,438,989 | 17,397,413 | +6.0% | PASS | 30.02 | 4.95 | +25.06 |
| 2019-01-01 | static | 18,438,989 | 18,504,955 | -0.4% | PASS (context) | 30.02 | 9.42 | +20.60 |
| 2019-01-02 | dlr | 29,550,436 | 27,987,563 | +5.6% | PASS | 40.14 | 5.68 | +34.46 |
| 2019-01-02 | static | 29,550,436 | — (infeasibleOrUnbounded) | — | n/a | 40.14 | — | — |
| 2019-01-03 | dlr | 27,000,608 | 26,015,976 | +3.8% | PASS | 36.86 | 5.53 | +31.33 |
| 2019-01-03 | static | 27,000,608 | 26,784,312 | +0.8% | PASS (context) | 36.86 | 5.76 | +31.09 |

## Prescient per day

| day | RT mean LMP | in band | DA mean LMP | hourly Price mean | RT LMP range | load shed MWh | reserve shortfall MWh | fixed $ | generation $ |
|---|---|---|---|---|---|---|---|---|---|
| 2019-01-01 | 30.02 | yes | 32.47 | 18.67 | 0.00 – 65.20 | 0.0 | 0.0 | 8,419,371 | 10,019,618 |
| 2019-01-02 | 40.14 | yes | 42.76 | 25.76 | 17.44 – 79.00 | 0.0 | 0.0 | 12,521,728 | 17,028,708 |
| 2019-01-03 | 36.86 | yes | 39.00 | 24.53 | -5.21 – 101.70 | 0.0 | 0.0 | 11,634,812 | 15,365,797 |

Shortfall hours (shed or reserve shortfall) are excluded from the LMP means.

RUC quality (TL = 120 s): {'n': 3, 'all_ok': True, 'statuses': ['OPTIMAL', 'OPTIMAL', 'OPTIMAL'], 'gaps_pct': [0.9511, 0.9997, 0.9897], 'gap_pct_median': 0.9897, 'gap_pct_max': 0.9997, 'solve_s_median': 8.986762285232544, 'solve_s_max': 9.675623893737791, 'capped_share': 0.0}

Nuclear committed hours (gen 1, 93): {'1': 72, '93': 72}; authors (DLR): day 1: [24, 24], day 2: [24, 24], day 3: [24, 24]
