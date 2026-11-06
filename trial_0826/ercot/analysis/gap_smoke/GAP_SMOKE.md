# GAP_SMOKE — RUC-gap smoke reading (prompt 58 T1, E-D6)

Extracts: `extracts/smoke_gap`; byte-identity reference: `extracts/smoke_v2`. Pure pandas; this file decides nothing. Kay writes `waves/GAP_DECISION.json`.

## 1. Per task

| task | role | gap | TL s | days | OPTIMAL | tol OK | tol read | max solve s | median solve s | max gap % | year RUC h (365 x median) | year RUC h (365 x max) | wall s | rule (i) | (ii) | (iii) | PASS |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | control (identical to smoke_v2) | 0.01 | 1200 | 3 | 3 | 3 | 3 | 23.0 | 19.6 | 0.9997 | 1.99 | 2.33 | 187 | Y | Y | Y | PASS |
| 2 | candidate | 0.001 | 1200 | 3 | 3 | 3 | 3 | 46.1 | 26.3 | 0.0997 | 2.67 | 4.67 | 221 | Y | Y | Y | PASS |
| 3 | stretch | 0.0001 | 1200 | 3 | 3 | 3 | 3 | 222.3 | 120.4 | 0.0100 | 12.21 | 22.54 | 513 | Y | Y | Y | PASS |

A task whose `tol read` < `days` has an UNVERIFIED tolerance (no job log or no Gurobi tolerance line) and cannot pass rule (i). A tolerance line that reads 1.00e-02 on task 2 or 3 is a FAILED smoke, not a result.

## 2. 3-day totals and delta vs task 1

| task | total cost $ | fixed $ | variable $ | true curt MWh | committed MWh | on/offs | G_run $ | d total cost vs 1 | d fixed | d variable | d true curt | d committed | d on/offs |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 74,990,033 | 32,575,910 | 42,414,123 | 35,498.2 | 3,204,491 | 187 | 1,107,533 | +0 | +0 | +0 | +0.0 | +0 | +0 |
| 2 | 74,900,543 | 32,028,576 | 42,871,967 | 34,941.6 | 3,160,713 | 171 | 101,131 | -89,490 | -547,334 | +457,844 | -556.6 | -43,778 | -16 |
| 3 | 74,885,864 | 32,270,281 | 42,615,583 | 34,913.2 | 3,180,881 | 175 | 9,833 | -104,169 | -305,629 | +201,461 | -585.0 | -23,611 | -12 |

## 3. Per task x day

| task | gap | day | status | tolerance read | tol OK | final gap % | solve s | MIP solves | RUC cost $ |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.01 | start_date | OPTIMAL | 1.00e-02 | Y | 0.9511 | 19.1 | 2 | 27,892,155 |
| 1 | 0.01 | 2019-01-02 | OPTIMAL | 1.00e-02 | Y | 0.9997 | 19.6 | 2 | 43,784,015 |
| 1 | 0.01 | 2019-01-03 | OPTIMAL | 1.00e-02 | Y | 0.9897 | 23.0 | 2 | 40,875,156 |
| 2 | 0.001 | start_date | OPTIMAL | 1.00e-03 | Y | 0.0985 | 46.1 | 2 | 27,865,302 |
| 2 | 0.001 | 2019-01-02 | OPTIMAL | 1.00e-03 | Y | 0.0997 | 21.2 | 2 | 43,784,015 |
| 2 | 0.001 | 2019-01-03 | OPTIMAL | 1.00e-03 | Y | 0.0736 | 26.3 | 1 | 40,802,748 |
| 3 | 0.0001 | start_date | OPTIMAL | 1.00e-04 | Y | 0.0086 | 222.3 | 2 | 27,862,504 |
| 3 | 0.0001 | 2019-01-02 | OPTIMAL | 1.00e-04 | Y | 0.0100 | 120.4 | 1 | 43,770,637 |
| 3 | 0.0001 | 2019-01-03 | OPTIMAL | 1.00e-04 | Y | 0.0075 | 55.7 | 1 | 40,793,453 |

## 4. Byte identity of the control arm (task 1 vs smoke_v2)

- `overall.csv` md5 task 1 `8b2b0575bde1c2487141dfee86b6bc7c` vs reference `8b2b0575bde1c2487141dfee86b6bc7c` → **PASS**.
- Tables identical to the reference manifest: `committed_hourly.csv;daily_summary.csv;gen_summary.csv;hourly_summary.csv;line_summary.csv;overall.csv;renewables_hourly.csv;reserves.csv`.
- Tables different: `bus_lmps.csv.gz;line_flows.csv.gz;renewables.csv.gz;ruc_quality.csv;thermal.csv.gz`.
- FAIL means the `--ruc_mipgap` plumbing changed something besides the gap (or the 120 s TL bound in smoke_v2 after all): stop, do not decide.

## 5. Pre-registered rule (prompt 58 section 2) — printed, not decided

- Tightest passing arm: **3** → adopt `ruc_mipgap = 0.0001`, `ruc_time_limit = 1200`.
- Reason: tightest arm with (i) all days OPTIMAL at the requested tolerance, (ii) max solve <= 600 s, (iii) 365 x max <= 61 h.
- Rule: (i) every day OPTIMAL with tolerance line == requested gap; (ii) max per-day solve <= 600 s; (iii) 365 x max solve <= 61 h. Otherwise keep 0.01 / 120 and disclose.
- Kay writes `waves/GAP_DECISION.json` `{"ruc_mipgap": …, "ruc_time_limit": …, "decided_by": "Kay", "date": …, "evidence": "extracts/smoke_gap"}`. Wave D refuses to start without it.

## 6. Was tightening worth it? (cost shift vs the $11.3M single-site median)

- task 2 (gap 0.001) vs task 1: 3-day d total cost -89,490 $ → x 365/3 = **-10,887,945 $/yr** = 0.96 x the $11.3M median single-site |d total cost| (POOL_V2 section 6.1). G_run at this gap: 101,131 $ over 3 days.
- task 3 (gap 0.0001) vs task 1: 3-day d total cost -104,169 $ → x 365/3 = **-12,673,871 $/yr** = 1.12 x the $11.3M median single-site |d total cost| (POOL_V2 section 6.1). G_run at this gap: 9,833 $ over 3 days.

The scaled shift is the solver-hidden cost the 1 % gap left on the table on these 3 days, extrapolated linearly; it is a size indication, not a year estimate.

