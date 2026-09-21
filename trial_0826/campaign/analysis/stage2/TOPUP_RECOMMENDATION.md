# Pre-registered top-up decision: extend n₀ 16 → 32 — **GO**

Recommendation to Kay (prompt 27 T4; decision is yours/PI's). Evidence in
`stage2_quicklook.ipynb` + `n0_gp_loo.csv`.

## Why GO

1. **The GP is model-limited, not noise-limited, exactly where it matters.**
   LOO RMSE over the 16 points (Matérn-2.5 ARD per the bo_replay reference,
   per-fold standardization): curtailment **17.1× floor**, cost raw
   **7.2×**, cost-less-synthetic **7.1×**. Errors that size are sparse-
   coverage error, so additional design points buy real information. (Load
   shed is the exception — LOO RMSE 0.50× floor, already noise-limited;
   more points won't sharpen it.)
2. **The new regimes are genuinely nonlinear.** The back-fill shows the
   ω ≤ 0.5 linear trend breaking past 0.5 for nuclear (curtailment +147 GWh
   above the extrapolation at ω = 1.0, 29× floor; cost +$1.8–2.7M, 4–5×)
   and past 0.8 for pv (curtailment 20× floor; cost 6–7× *below* the
   line). A 6-D surrogate headed into BO round 1 needs interior coverage
   of that curvature; 16 points give it ~2–3 per octant of nothing.
3. **It is schedule-free.** ~160 core-h during the M-decision dead time;
   the automation pattern just demonstrated a zero-touch 39.6 h
   turnaround, and no `-tc` applies.

## Mechanics (continue-the-sequence rule, doc 14 §5.1)

Draw rows 17–32 with `generate_sobol(16, SOBOL_SEED, skip=16, d=6)` —
`skip = n_drawn_total = 16` from the n₀ manifest (never re-seed), snap to
`STAGE2_LATTICE`, dedupe against **all 32** post-snap rows, redraw in
blocks on collision, update `n_drawn_total` in the new wave's manifest.
Build as a NEW wave dir (e.g. `stage2_C_n0b`) with its own array script
(no `-tc`) + collector — never regenerate `stage2_C_n0`.

## Caveats

- Nuclear numbers carry the g1 fuel-deletion APPROX caveat (patch pending
  PI review).
- LOO R² on 16 points is fragile (leave-one-out of a 6-D design of 16);
  the ratios to floor, not the R² values, carry the decision.
- This extends the *objective-agnostic* n₀ only; BO round 1 still waits
  on M from the location analysis.
