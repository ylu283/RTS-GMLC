# Sweep + interaction findings (prompt 20, data 2026-09-10)

Data: `waves/sweep_B` (ρ=1.5), `waves/sweep_C` (ρ=2.0) — 6 tiers × 9 ω
levels, full-year OAT — and `waves/contour_303x317_B/C` for the pair
surfaces. All Δ vs base year; negative = improvement. Reserve shortfall is
a **diagnostic** (no stated floor), never a headline metric.

## Tier × metric summary (total effect at box top / saturation ω)

Cells: `total / ω_sat`. Units: cost M$ (APPROX), curtailment GWh, shed
GWh, starts count, reserve GWh. ω_sat = first ω where the remaining
improvement is < 10% of the tier's total; "—" = total below noise floor
(saturation undefined).

### Scenario B (ρ = 1.5 $/kg, B = $30)

| tier | Δcost APPROX | Δcurt | Δshed | Δstarts | Δreserve (diag) |
|---|---|---|---|---|---|
| nuclear | -1.2 / 0.50 | -370.1 / 0.44 | 0.0 / — | -394.0 / 0.50 | -19.3 / 0.39 |
| wind_303 | 13.0 / 0.76 | -853.5 / 0.76 | -16.0 / 0.76 | -894.0 / 0.76 | -70.0 / 0.64 |
| wind_317 | 20.4 / 0.88 | -714.7 / 0.76 | -25.7 / 0.76 | -1,197.0 / 1.00 | -102.8 / 0.76 |
| wind_122 | 17.3 / 0.88 | -612.8 / 0.76 | -23.4 / 0.76 | -1,043.0 / 0.76 | -98.2 / 0.76 |
| pv | 9.4 / 0.70 | -269.4 / 0.70 | -0.1 / — | -289.0 / 0.80 | -11.7 / 0.51 |
| tail | 2.2 / 0.63 | -197.4 / 0.63 | 0.7 / — | -262.0 / 0.63 | -19.0 / 0.76 |

### Scenario C (ρ = 2.0 $/kg, B = $40)

| tier | Δcost APPROX | Δcurt | Δshed | Δstarts | Δreserve (diag) |
|---|---|---|---|---|---|
| nuclear | -0.6 / 0.50 | -377.5 / 0.50 | -1.5 / — | -345.0 / 0.50 | -21.5 / 0.50 |
| wind_303 | 14.6 / 0.88 | -828.9 / 0.76 | -19.0 / 1.00 | -1,214.0 / 0.88 | -83.3 / 0.76 |
| wind_317 | 22.9 / 0.88 | -699.4 / 0.76 | -29.3 / 0.64 | -1,468.0 / 0.76 | -110.7 / 0.64 |
| wind_122 | 19.9 / 0.88 | -590.3 / 0.88 | -28.2 / 0.76 | -1,556.0 / 0.88 | -113.3 / 0.64 |
| pv | 8.9 / 0.70 | -284.2 / 0.70 | -1.8 / — | -246.0 / 0.60 | -13.7 / 0.41 |
| tail | 4.9 / 0.88 | -170.4 / 0.76 | -2.9 / — | -372.0 / 1.00 | -28.3 / 1.00 |

**Nuclear cost caveat (mandatory):** nuclear Δcost is an APPROX-column
value that EXCLUDES the ~$27.8M/yr base-nuclear fuel asymmetry (living
report §3.4) — do not read nuclear's negative Δcost as a cost-negative
retrofit; its true position is ≈ +$13–27M/yr.

## Findings

1. **The wind curtailment ranking is screening's, at both prices:**
   wind_303 > wind_317 > wind_122 > nuclear > pv > tail — the same top-heavy order screening measured at B=$40
   (303: 671.6 > 317: 498.7 > 122: 416.6 GWh solo), now traced over the
   whole ω box.
2. **The reliability cluster is led by 317/122, not by curtailment-leader
   303.** Shed ranking wind_317 > wind_122 > wind_303 at both prices; starts and the
   reserve diagnostic follow the same 317/122-first pattern, with 122
   pulling ahead of 317 on starts and reserve at C. Consistent with 19b's
   committed-capacity reading: withheld *capacity*, not energy, drives
   the cluster, and 303's energy lead does not carry over.
3. **Curtailment is first-order price-invariant; cost is not.** B→C moves
   per-tier Δcurt by ≲5% but adds $1.5–2.6M to every wind tier's Δcost —
   the price scenario prices the same physical diversion differently.
4. **Small tiers are shed-inert:** pv and tail Δshed sit inside the
   ±3 GWh floor at both prices (report as "0 within noise"); their
   curtailment effects (170–284 GWh) are real but 2–5× smaller than any
   single big wind tier.
5. **Wind curtailment shows diminishing returns inside the box:** each
   wind tier reaches 90% of its total effect by ω_sat ≈ 0.76–0.88 (see
   tables) while remaining monotone to ω = 1.0 — the last ~120 MW-scale
   increments of PEM buy the final ~10%. Nuclear and pv saturate earlier
   relative to their (smaller) boxes.
6. **Interactions (§4.3): sub-additive (substitutes) across the
   measurable plane, with one caveated edge.** For curtailment and cost
   the interaction is significant almost everywhere (79/81 and 52–71/81
   cells) and I > 0 in every significant cell, from the smallest ω up.
   Shed interaction only *turns on* at mid-size (first significant cells
   ω ≈ 0.41/0.53 at B; 13–22 cells; all but one I > 0). At (1,1) the
   additive OAT sum overpromises the pair improvement by
   21% (curtailment, B; 325 GWh) —
   the two-site share of screening's +54.6% eleven-site gap. Caveat:
   thermal starts shows a band of *negative* I (apparent complementarity,
   −100…−340 starts) along the ω ≈ 0.05 edges in both scenarios; it sits
   just above the *working* floor (quadratic-residual RMSE ≈ 50, no
   established floor), so we flag it as tentative rather than a finding.
   No A-scenario map exists (no sweep_A wave).

## Files

- `sweep_curves.ipynb` (this notebook, executed) — asserts
  6×9×2 + bitwise lattice equality, curves grid, quantification tables,
  interaction maps.
- `figs/sweep_curves_grid.png|pdf`, `figs/interaction_maps_B|C.png|pdf`.
