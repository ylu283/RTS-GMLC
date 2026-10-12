# ercot123_2019_v2 — MANIFEST

Built 2026-10-12 by `trial_0826/ercot/tools/convert_tx123_costs.py --reading c` (prompt 36).

**v2: cost columns rebuilt; v1 mis-converted (prompt 36).** Only `gen.csv` differs from v1, and only in the cost/start columns of the 128 thermal units (`Output_pct_0`, `Output_pct_1`, `Output_pct_2`, `Output_pct_3`, `Output_pct_4`, `HR_avg_0`, `HR_incr_1`, `HR_incr_2`, `HR_incr_3`, `HR_incr_4`, `Start Heat Cold MBTU`, `Start Heat Warm MBTU`, `Start Heat Hot MBTU`, `Non Fuel Start Cost $`, `C0`, `C1`, `C2`, `Csu`). See PROVENANCE.md.

| field | value |
|---|---|
| reading | (c) — linear C0·u + C1·P, start = Csu·PMax (Kay 10-12, CONFIRMED) |
| cost factor | ×1.0 |
| breakpoints | 4 (PMin + equal thirds); 2-point fallback units: [12, 14, 28, 45, 48, 61, 66, 85, 94, 98, 107, 118, 122, 144, 148, 150, 151, 208, 213, 244, 264, 268] |
| source coefficients | `analysis/cost_fix/source_coeffs_tx123.csv` (md5 `e08fe4dd14ba2e6c54f61611932efd1e`) ← Generator_data.xlsx + 123bus_case_final.pkl (see analysis/cost_fix/T0_FACTS.md) |
| v1 gen.csv md5 | `b738d495137322223785fda7310033a1` |

## md5

| file | md5 | same as v1 |
|---|---|---|
| DAY_AHEAD_load.csv | `6053fc8869561d2c3b570bdb3c6a2200` | yes |
| DAY_AHEAD_solar.csv | `435ddf1ebbce54ce9f593fa3e000b9f5` | yes |
| DAY_AHEAD_wind.csv | `eaac5aaf43a98ba668c118dff77f34f8` | yes |
| REAL_TIME_load.csv | `6053fc8869561d2c3b570bdb3c6a2200` | yes |
| REAL_TIME_solar.csv | `435ddf1ebbce54ce9f593fa3e000b9f5` | yes |
| REAL_TIME_wind.csv | `eaac5aaf43a98ba668c118dff77f34f8` | yes |
| branch.csv | `3fe279ff4a2dfe9e9dba2cc256a2961d` | yes |
| bus.csv | `a83144a1fefeda786db842756afacd91` | yes |
| gen.csv | `42b1a09d62839d9e5a59c0625e7f1b92` | no |
| simulation_objects.csv | `8a67288cfa1569eeac3f5c67c8138267` | yes |
| timeseries_pointers.csv | `9e2ac0da1c771f9b94d9840a4586524b` | yes |
