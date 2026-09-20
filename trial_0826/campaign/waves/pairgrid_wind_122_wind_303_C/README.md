# pairgrid_wind_122_wind_303_C — 9x9 pair grid at scenario C (prompt 28)

Pair: **wind_122** (outer axis) x **wind_303** (inner axis), sorted tier
order. 81 full-year rows, index = 9*i_a + i_b + 1 (row-major, matching
build_contour's convention). Both axes are STAGE2_LATTICE (9 decimal-clean
levels, 0.05..1.0 inclusive). The other four tiers are ABSENT (NaN in the
design matrix — absent means no PEM at those sites, never omega=0). Bids
derived: B = 20*rho_H2 = 40 at rho = 2.0 (scenario C). Pair
identity and lattice are recorded in manifest.json — read them from there,
never from this directory's name (tier keys contain underscores).

Submit ON CRC from inside this directory: `bash submit_this.sh`
(d6 guard + pull, array without -tc, chained collector with email).
Nuclear omega > 0.5 rows are validated by the 09-19 omega=1.0 3-day smoke
(JID 1458448, SMOKE PASS).
