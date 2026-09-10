# Stage-1 BO replay on the 303×317 contour grids (prompt 21, data 2026-09-10)

**Stage 1 validates the BO machinery on a smooth 2-D, 81-candidate problem
where the truth is known; the difficulty claim lives in Stage 2** (math-log
§5.1/§5.2). Nothing below is the headline's difficulty — the surfaces are
quadratic to R² 0.99–0.998 for cost/curtailment (table §1) and BO's job here
is to *recover* a known optimum, not to find a hard one.

Data: `waves/contour_303x317_{A,B,C}` — `design_matrix.csv` ⋈ `objectives.csv`
on `index`, 81 rows each, inputs (ω_303, ω_317), M = 4 objectives all
minimized (Δ vs base): cost APPROX, curtailment, load shed, thermal starts.
Code: `replay.py` (harness), `bo_replay.ipynb` (executed, 212 s wall on 14
cores), CSV tables + `replay_results.json` next to it, figures in `figs/`.

## 0. Rules followed (math-log §5.1 — hard requirements)

- **No leakage.** Inside every replay loop the GP, its hyperparameters and the
  input/output scalers are fit ONLY on the points queried so far. `QueriedGP`
  (`replay.py`) is the single fit path; it min-max scales inputs on the
  queried rows, standardizes outputs on the queried rows (`normalize_y`),
  and re-optimizes the Matérn-2.5 ARD hyperparameters on the queried rows at
  every iteration. The notebook's last cell greps the file: the three `.fit(`
  calls all receive `X[q]`/`y[q]` (queried rows). The only full-table
  quantities are metric *definitions*: grid-min + floor ("optimum found") and
  the HV ideal/nadir/reference (§3).
- **"Optimum found"** = best-so-far ≤ grid-min + the metric's noise floor, not
  exact argmin (A-shed has a 20-cell tie set within its floor).
- **Seeds recorded.** BO: 20 init seeds (0–19), init = 5 random cells
  (`rng.choice(81, 5)` per seed — a stated choice: for d = 2 over 81
  candidates a seed-randomized init supplies the seed-variance distribution
  §5.1 requires; Stage 2 uses Sobol n₀ = 16 per §5.2). Random search: 100
  seeds (0–99), full permutations. Sobol ordering: one, from `tiers.SOBOL_SEED`
  = 20260821 — scrambled Sobol in [0,1]², fresh d = 2 engine, mapped onto the
  design box and snapped to the nearest lattice cell, visited cells skipped,
  drawn until all 81 are ordered. The design matrices are raster-ordered
  factorials; row order is never used.
- GP: sklearn `GaussianProcessRegressor`, `ConstantKernel × Matern(ν = 2.5,
  per-dim length scales) + WhiteKernel`, one restart, warm-started from the
  previous iteration's hyperparameters (queried-data information only).
  Acquisition: analytic EI for minimization, argmax over the unqueried cells,
  ties broken at random.

**Noise floors.** Established (campaign noise model): shed 3,000 MWh,
curtailment 5,000 MWh, cost $0.5M. **Starts has NO established floor** (prompt
20's docs are right). For this replay only, a **WORKING ASSUMPTION floor of
60 starts** is used as the stopping criterion, derived as the quadratic-
surface residual RMSE of the starts surfaces — 54.6 / 56.2 / 50.1 (dof n−6)
or 52.5 / 54.1 / 48.2 (÷n) for A / B / C — rounded up; sensitivity at
{30, 60, 120} is in §2b. It is not a claim about starts noise.

## 1. Surfaces, fronts, degeneracy (honesty exhibit)

Full-quadratic (6-term) least-squares fit per surface, on the full 81 (this
is a *description* of the surfaces, not part of any loop):

| scen | metric | quad R² | resid RMSE (n−6) | grid min | floor | cells within floor of min |
|---|---|---|---|---|---|---|
| A | cost | 0.998 | $0.34M | −$32.2M | $0.5M | 1 |
| A | curt | 0.992 | 23.8 GWh | −1,351 GWh | 5 GWh | 2 |
| A | shed | **0.627** | 1.7 GWh | −12.1 GWh | 3 GWh | **20** |
| A | starts | 0.874 | 54.6 | −706 | 60 (working) | 8 |
| B | cost | 0.998 | $0.42M | +$4.45M | $0.5M | 1 |
| B | curt | 0.988 | 26.3 GWh | −1,244 GWh | 5 GWh | 2 |
| B | shed | 0.976 | 1.2 GWh | −33.9 GWh | 3 GWh | 12 |
| B | starts | 0.973 | 56.2 | −1,712 | 60 (working) | 3 |
| C | cost | 0.998 | $0.60M | +$4.00M | $0.5M | 1 |
| C | curt | 0.990 | 23.6 GWh | −1,218 GWh | 5 GWh | 2 |
| C | shed | 0.984 | 1.1 GWh | −38.6 GWh | 3 GWh | 14 |
| C | starts | 0.988 | 50.1 | −2,245 | 60 (working) | 4 |

A-shed's R² = 0.63 is the noise-floor plateau, not a rough surface (its
residual RMSE 1.7 GWh is below the 3 GWh floor; 19b §B.4, LOOCV Q² 0.59). The
"cells within floor" column is the size of the target set each replay must
hit — it is why shed and A-starts are found in 2–8 evaluations by *any*
ordering (§2).

**Front cardinalities** (both reported, as required):

| scen | cost–shed 2-D front | M = 4 front | (1,1) corner weakly dominates |
|---|---|---|---|
| A | 4 | 15 | 54 / 81 cells (incl. itself) |
| B | 23 | 71 | 1 / 81 (itself) |
| C | 24 | 73 | 1 / 81 (itself) |

Matches 19b (≈ 4 / 23 / 24) and the expected 4-D inflation (≈ 15 / 71 / 73;
with four objectives 88–90 % of the B/C cells are non-dominated — this is a
property of 4-D non-domination, not a bug, and was not "fixed"). **A's
degeneracy is the aligned-objective structure:** the all-in corner (1,1)
weakly dominates 54 of 81 cells on the M = 4 vector (19b §C: 54/81 on the
five-objective set), and the A cost–shed front is 4 near-coincident cells
(all within one cell's floors of the best one in cost; the front is a
plateau). The M = 4 cardinality of 15 says nothing about that.

## 2. Single-objective replay: evals-to-optimum (median, IQR over seeds)

BO = 20 seeds; random = 100 seeds; Sobol = one ordering. n counts every
queried cell including the 5 init cells.

| scen | metric | BO median (IQR) | random median (IQR) | Sobol |
|---|---|---|---|---|
| A | cost | **6** (6–7) | 46 (20–60) | 76 |
| A | curt | **6** (6–7) | 26 (15–45) | 66 |
| A | shed | 3 (1–6) | 3 (2–5) | 2 |
| A | starts* | 7.5 (5–11) | 6.5 (2–12) | 11 |
| B | cost | **6** (6–7) | 37.5 (20–61) | 77 |
| B | curt | **6** (6–7) | 26 (15–45) | 66 |
| B | shed | 5.5 (3–6) | 5 (3–9) | 2 |
| B | starts* | **6** (6–7) | 17 (10–26) | 48 |
| C | cost | **6** (6–7) | 37.5 (20–61) | 77 |
| C | curt | **6** (6–7) | 26 (15–45) | 66 |
| C | shed | 3.5 (2–6) | 4 (2–7) | 2 |
| C | starts* | **6** (4–6) | 14.5 (7–20) | 16 |

\* working floor 60. Figure: `figs/fig1_best_so_far.pdf` (median + 20–80 %
band, per metric × scenario).

Reading: where the target set is a single corner cell (cost, curtailment,
B/C starts) BO reaches it on its **first model-guided pick** (n = 6 = 5 init
+ 1) in ≥ 75 % of seeds, worst seed 15; random needs 26–46, Sobol 48–77 (the
scrambled sequence reaches the (1,1) corner cell late). Where the target set
is a floor-wide plateau (shed: 12–20 cells; A-starts: 8 cells) every
ordering hits it in 2–8 evaluations and BO has no room to beat random — the
honest statement is "trivial for all methods", not "BO wins". This is
exactly the §5.1 claim scope: the machinery converges where truth is known.

### 2b. Starts working-floor sensitivity (evals-to-optimum, median (IQR))

| scen | floor | BO | random | Sobol |
|---|---|---|---|---|
| A | 30 | 9 (6–15) | 12 (4–22) | 11 |
| A | 60 | 7.5 (5–11) | 6.5 (2–12) | 11 |
| A | 120 | 1.5 (1–3) | 2 (1–3) | 2 |
| B | 30 | 7 (6–7) | 46 (20–60) | 76 |
| B | 60 | 6 (6–7) | 17 (10–26) | 48 |
| B | 120 | 6 (4–6) | 11 (4–18) | 16 |
| C | 30 | 6 (6–8) | 22.5 (12–40) | 48 |
| C | 60 | 6 (4–6) | 14.5 (7–20) | 16 |
| C | 120 | 6 (4–6) | 8 (4–15) | 2 |

BO's answer is insensitive to the floor at B/C (6–7 evals at every floor);
the baselines' numbers are what move. At A the starts surface is a plateau
(8 cells within 60; LOOCV Q² 0.86) and the comparison is uninformative at
any floor. Conclusion: the working floor only changes how good the
*baselines* look, not the BO result — safe as a stopping criterion.

## 3. Multi-objective replay (M = 4): HV recovery n ↦ HV(first n) / HV(all 81)

Loop: sequential (q = 1) ParEGO — per iteration a weight vector uniform on
the simplex (Dirichlet(1,1,1,1)), the QUERIED objectives normalized to [0,1]
by their own ideal/nadir (recomputed each iteration), augmented Tchebycheff
scalarization (ρ = 0.05), GP + EI on the scalarized value over the unqueried
cells. Scalarization and weights are imported from `bogp.mobo.qparego`, so
the replay and the bo-gp T-M8 implementation share one code path.

**Reference points** (per scenario, on the full 81; the reference defines the
metric, not the optimizer's information — an exact-nadir reference would
zero out the extreme trade-off cells): reference = nadir + 0.1 (nadir − ideal).

| scen | metric | ideal | nadir | reference |
|---|---|---|---|---|
| A | cost [$] | −3.217e7 | −3.324e6 | −4.399e5 |
| A | curt [MWh] | −1.351e6 | −1.888e5 | −7.262e4 |
| A | shed [MWh] | −1.211e4 | +6.195e2 | +1.892e3 |
| A | starts | −706 | −4 | +66.2 |
| B | cost [$] | +4.451e6 | +4.014e7 | +4.371e7 |
| B | curt [MWh] | −1.244e6 | −1.891e5 | −8.366e4 |
| B | shed [MWh] | −3.387e4 | −2.326e2 | +3.131e3 |
| B | starts | −1,712 | −262 | −117 |
| C | cost [$] | +4.004e6 | +4.957e7 | +5.412e7 |
| C | curt [MWh] | −1.218e6 | −1.943e5 | −9.194e4 |
| C | shed [MWh] | −3.858e4 | −1.398e3 | +2.321e3 |
| C | starts | −2,245 | −183 | +23.2 |

HV(all 81), exact: A 4.085e20, B 1.250e21, C 2.772e21 (raw objective units;
normalized to the ideal–reference box: 0.9315 / 0.4650 / 0.5296, which the
bo-gp Monte-Carlo estimator reproduces to ±0.0004 — sanity only, all
headline numbers are exact). HV is computed with `hypervolume_exact`
(exact any-M dimension sweep, new in bo-gp) — **never** the Monte-Carlo
`bogp.mobo.pareto.hypervolume` (exact only for M = 2).

**n at 90 / 95 / 99 % recovery** (median (IQR); BO 20 seeds, random 100, Sobol 1):

| scen | level | BO | random | Sobol |
|---|---|---|---|---|
| A | 90 % | **13** (10–16) | 31.5 (20–44) | 41 |
| A | 95 % | **22** (20–24) | 47 (31–60) | 76 |
| A | 99 % | **37** (31–41) | 63.5 (52–72) | 76 |
| B | 90 % | 19.5 (18–22) | 22.5 (20–25) | 23 |
| B | 95 % | 33.5 (30–37) | 38 (35–41) | 48 |
| B | 99 % | 61 (58–66) | 68.5 (65–72) | 76 |
| C | 90 % | 16.5 (15–20) | 19 (17–22) | 21 |
| C | 95 % | 29 (28–32) | 33 (31–37) | 32 |
| C | 99 % | 61.5 (57–64) | 66 (63–69) | 68 |

Figure: `figs/fig2_hv_recovery_M4.pdf`. At A (15-cell front, aligned
objectives) BO recovers 95 % of the hypervolume in 22 evaluations against
47 random / 76 Sobol. At B and C BO is ahead at every level but only by 3–8
evaluations: with 71–73 of 81 cells non-dominated, the M = 4 hypervolume is
essentially a *coverage count* — nearly every cell contributes its own sliver
and no ordering can recover the last 10 % without visiting most cells. That
is the 4-D non-domination inflation of §1, and it is why the M = 4 HV ratio
is a weak discriminator on this grid.

### 3b. Supplementary: cost–shed (M = 2) recovery — where the trade-off lives

Same loop restricted to {cost, shed} (the 19b comparison front), reference
built the same way on those two columns (`hv_reference_costshed.csv`):

| scen | level | BO | random | Sobol |
|---|---|---|---|---|
| A | 90 % | **8** (7–10) | 24 (16–32) | 31 |
| A | 95 % | **8** (7–10) | 45.5 (20–59) | 76 |
| A | 99 % | **28.5** (22–31) | 50 (38–67) | 76 |
| B | 90 % | 14 (11–15) | 16 (14–20) | 16 |
| B | 95 % | **21** (19–25) | 31 (28–37) | 36 |
| B | 99 % | **43.5** (38–48) | 62 (57–69) | 77 |
| C | 90 % | 13 (12–15) | 15 (12–18) | 14 |
| C | 95 % | **19.5** (17–23) | 29 (26–33) | 28 |
| C | 99 % | **38.5** (33–44) | 61 (56–66) | 73 |

Figure: `figs/fig3_hv_recovery_costshed.pdf`; the fronts themselves in
`figs/fig4_fronts.pdf`. On the 23–24-cell B/C cost–shed fronts BO reaches
99 % in 39–44 evaluations vs 61–62 random / 73–77 Sobol. This — not the
M = 4 ratio — is the exhibit that shows trade-off *recovery*; Stage 2 should
track both.

## 4. q-ParEGO (bo-gp T-M8) smoke on scenario C, replay mode

`bogp.mobo.qparego.run_mobo_qparego` (branch `feat/qparego`) in candidates
mode: n₀ = 8 random cells (seeds 0–9), q = 8, 2 rounds → 24 evaluations,
`MultiGridEvaluator` lookups, same no-leakage rules (its [0,1] normalization
uses the queried ideal/nadir only). Architecture: classic ParEGO — one GP
(gpytorch, Matérn-2.5 ARD) per batch member on that member's scalarization,
greedy fill with kriging-believer fantasies (pending points get the current
GP's posterior mean; documented in the module). Every batch member was a
distinct, previously unqueried cell in all 10 seeds (asserted).

HV recovery (M = 4, same reference as §3), median (IQR):

| n | q-ParEGO q = 8 | sequential ParEGO (§3, 20 seeds) | random (100 seeds) |
|---|---|---|---|
| 8 (init) | 0.813 (0.783–0.820) | 0.824 (0.780–0.842) | 0.807 (0.784–0.827) |
| 16 | 0.899 (0.886–0.915) | 0.900 (0.872–0.913) | 0.885 (0.873–0.896) |
| 24 | **0.941** (0.923–0.947) | 0.936 (0.921–0.940) | 0.923 (0.914–0.932) |

Two batched rounds of 8 recover as much hypervolume as 16 sequential picks
(0.941 vs 0.936 at n = 24) and beat random (0.923); the batch machinery
costs nothing measurable here relative to the sequential loop. 48 s for
10 seeds. This is a smoke test of the implementation, not a Stage-2 claim.

## 5. File inventory

```
analysis/bo_replay/
  replay.py                     harness (loaders, orderings, QueriedGP, EI, ParEGO loop, HV curves)
  bo_replay.ipynb               executed notebook (all tables/figures; 212 s)
  REPLAY.md                     this summary
  stage2_plan.md                Stage-2 recipe (build-only; PI decision 0911-D2 pending)
  surface_stats.csv             quadratic R² / RMSE / grid min / floor / tie-set size
  front_stats.csv               front cardinalities + corner dominance
  evals_to_optimum.csv          §2 table (all seeds summarized)
  starts_floor_sensitivity.csv  §2b
  hv_reference.csv              §3 ideal / nadir / reference (M = 4)
  hv_recovery_M4.csv            §3 table
  hv_reference_costshed.csv     §3b reference (M = 2)
  hv_recovery_costshed.csv      §3b table
  qparego_smoke_C.csv           §4 table
  replay_results.json           every number above, machine-readable
  figs/fig1_best_so_far.{pdf,png}         best-so-far bands, 3 × 4 panels
  figs/fig2_hv_recovery_M4.{pdf,png}      M = 4 HV recovery bands
  figs/fig3_hv_recovery_costshed.{pdf,png} cost–shed HV recovery bands
  figs/fig4_fronts.{pdf,png}              cost–shed vs M = 4 fronts on the 81 cells
```

bo-gp (`feat/qparego`): `bogp/mobo/qparego.py` (new: `propose_qparego_batch`,
`run_mobo_qparego`, `scalarize_tchebycheff`, `normalize_objectives`,
`sample_simplex_weights`), `bogp/mobo/pareto.py` (+ `hypervolume_exact`),
`tests/test_qparego.py` (27 tests: scalarization fixture + reconciliation with
the sequential `parego.scalarize` maximization form, simplex-uniform weights,
q distinct points in both modes, NaN handling, seed reproducibility, loop;
exact HV vs 2-D exact, 3-D hand fixture (19), 3-D/4-D lattice brute force,
Monte-Carlo agreement). Suite: 73 passed, nothing deselected.

Reproduce: `PYTHONPATH=<bo-gp checkout on feat/qparego> /opt/anaconda3/envs/bogp/bin/jupyter nbconvert --to notebook --execute --inplace bo_replay.ipynb`
from this directory.

## 6. Blockers / caveats

- Stage-2 scope + budget = PI decision 0911-D2 (see `stage2_plan.md` §4,
  incl. the §5.2 ≥ 3-seed stability requirement vs the single-sequence budget).
- Starts floor 60 is a working assumption (this document and the notebook
  say so); it is not to be quoted as a noise floor elsewhere.
- Sobol baseline is a single deterministic ordering (as specified); its
  poor evals-to-optimum on corner optima is a property of where the
  scrambled sequence places the corner cell, not a general statement about
  Sobol designs.
