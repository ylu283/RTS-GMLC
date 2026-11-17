## Mechanism sanity (prompt 54 §3.5 v3.2; read-only flags — nothing here changes committed_configs.json, E-D7 or 55)

### (a) Network facts (computed from branch.csv and base_v3 line_summary.csv, asserted)

Buses [2, 75, 121] (sites 110 / 140 on bus 2, 146 on bus 75) drain only through bus 120 (sites 163 / 270 / 274) via ['L240', 'L4', 'L5']; every MW injected at any of the six sites therefore reaches the binding line L252 (700 MW, 5,426 h/yr >= 99 % of rating in base_v3) with the same PTDF — the six sites are one electrical location; location effects can come only from resource profiles and nameplate caps.

### (c) No-simulation null (pinned before any n0_E Y was read)

Objective V1; GP config ['m52', 'std', 'inferred', 'none'] (m52+std); 256 posterior paths on a Sobol base of 2^13 points (seed 5454); base_v3 = 5.82873e+06; total-only fit a = 2.524e+06, b = 689.1 MW.

| null truth | truth L | truth I | posterior L median [5, 95] | posterior I median [5, 95] |
|---|---|---|---|---|
| additive | 0.0183 | -0.0000 | 0.0261 [0.0210, 0.0326] | 0.0097 [0.0050, 0.0144] |
| total_only | 0.0117 | 0.0610 | 0.0241 [0.0188, 0.0314] | 0.0470 [0.0330, 0.0659] |

Thresholds: INTERACTION if I_p05 > 0.0144 (additive null 95th); ADDITIVE if I_p95 < 0.0097 (its median); LOCATION if L_p05 > 0.0314 (total-only null 95th); TOTAL-ONLY-COMPATIBLE if L_p95 < 0.0241; otherwise UNRESOLVED. L and I are scale-free shares, so the V1-built null thresholds are applied to every objective.

The direct 8-run check is prompt 61 (`location_contrast_E`); when it lands, its standardized residuals under the committed config are added here as one descriptive row.

