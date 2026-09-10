# Stage-2 BO plan — d = 6 continuous q-ParEGO per scenario (build-only, NOT launched)

Status (2026-09-10): **prepared, not submitted.** Scenario scope and budget are
the pending PI decision **pi-agenda 0911-D2** (recommended there: full
q-ParEGO at B and C; at A only the n₀ = 16 Sobol batch as an alignment check).
No wave directories or design CSVs have been generated — wave generation
touches `make_batches.py` / `design_tools.py` (campaign builders) and waits for
D2. Everything below is the exact recipe so launch is one command per batch
once decided.

Stage 1 (this directory, `REPLAY.md`) validated the machinery on the 81-cell
pair grids; Stage 2 carries the claim (math-log §5.2): (i) convergence within
budget, (ii) stability across init seeds, (iii) consistency with the
sensitivity/interaction structure (§4.1/4.3). Beating the pair-grid optimum is
near-guaranteed (d = 6 adds four tiers) and is a garnish, not the claim.

## 1. Design space (identical for every scenario)

d = 6, ω-only, one coordinate per tier in `tiers.TIER_ORDER`; every tier's bid
is `derived_bid(rho_h2)` = 20·ρ (never sampled). **Bounds = `tiers.build_tiers()`
output** (the 15a-widened box; the raw `TIERS` dict holds narrower fallback
bounds and must not be used — `build_tiers()` returns `provisional=False`
locally, confirming the stats CSV is present):

| tier | ω lo | ω hi | members |
|---|---|---|---|
| nuclear | 0.05 | 0.5 | 121_NUCLEAR_1 |
| wind_303 | 0.05 | 1.0 | 303_WIND_1 |
| wind_317 | 0.05 | 1.0 | 317_WIND_1 |
| wind_122 | 0.05 | 1.0 | 122_WIND_1 |
| pv | 0.02 | 0.8 | 319_PV_1, 324_PV_{1,2,3} |
| tail | 0.02 | 1.0 | 310_PV_2, 320_PV_1, 309_WIND_1 |

Scenarios: A ρ = 1.0 (B = $20), B ρ = 1.5 ($30), C ρ = 2.0 ($40) — each needs
its own PCM runs (B enters the simulation). Objectives (M = 4, all minimized,
Δ vs base): `delta_cost_less_synthetic_usd_APPROX`, `delta_curtailment_mwh`,
`delta_load_shed_mwh`, `delta_thermal_starts`; reserve shortfall stays a
diagnostic column. Floors: cost $0.5M, curtailment 5,000 MWh, shed 3,000 MWh
(established); starts has no established floor (Stage-1 working value 60 is a
replay stopping criterion only).

## 2. Per-scenario recipe

### 2.1 Batch 0 — n₀ = 16 scrambled Sobol points

**A NEW d = 6 Sobol engine: seed `tiers.SOBOL_SEED` = 20260821, skip = 0.**
The campaign's never-re-seed / `fast_forward` convention applies to later
Stage-2 rounds that continue *this* d = 6 sequence (e.g. extra space-filling
rows would use `skip = 16`); it does not mean continuing the retired d = 12
`n0` sequence — different dimension, nothing to continue. 16 is a power of
two (Sobol balance; no scipy warning).

Builder (to be added to `make_batches.py` as `build_stage2_n0(scenario)` once
D2 lands — the code is the existing `build_n0` / `build_contour_303x317`
pattern in v3 derived-bid mode):

```python
tiers, provisional = build_tiers()                     # widened box, d = 6
rho = RHO_SCENARIOS[scenario]
points = dt.generate_sobol(16, SOBOL_SEED, skip=0, d=len(tiers))   # fresh d=6 engine
design = dt.to_design_matrix(points, tiers, start_index=1, num_days=FULL_YEAR,
                             provisional=provisional, rho_h2=rho)  # omega-only rows, bids = 20*rho
wave_dir = os.path.join(waves_root, f"stage2_{scenario}_n0")
dt.write_wave(design, wave_dir, tiers, sobol={"seed": SOBOL_SEED, "skip": 0, "n": 16})
```

Then `python submit_array.py waves/stage2_<S>_n0 --max-concurrent 16`, commit,
and on CRC `cd waves/stage2_<S>_n0 && qsub stage2_<S>_n0_array.sh`; after the
batch, `python summarize_wave.py waves/stage2_<S>_n0` → `objectives.csv`,
commit CSVs, push (same loop as the contour waves).

### 2.2 Rounds k = 1..R — q = 8 from bo-gp q-ParEGO

Inputs: every completed Stage-2 row of the scenario so far (n₀ + 8(k−1)),
`design_matrix.csv` ⋈ `objectives.csv` on `index`, X = the six `<tier>_omega`
columns in `TIER_ORDER`, Y = the four objective columns.

```python
from bogp.mobo.qparego import propose_qparego_batch     # bo-gp feat/qparego
bounds = np.array([tiers[t]["omega"] for t in TIER_ORDER])          # (6, 2)
batch = propose_qparego_batch(X_obs, Y_obs, q=8, bounds=bounds,
                              seed=<round seed>, rho=0.05,           # augmented Tchebycheff
                              kernel_nu=2.5, n_epochs=300, lr=0.05)  # Matern-2.5 ARD, one GP per member
rows = [dt.make_row(tiers, dict(zip(TIER_ORDER, x)), index=i, num_days=FULL_YEAR,
                    provisional=provisional, rho_h2=rho)
        for i, x in enumerate(batch["x_batch"], start=1)]
dt.write_wave(dt.rows_to_matrix(rows, tiers), f"waves/stage2_{S}_r{k}", tiers, sobol=None)
```

Round waves are fixed-design (`sobol=None` in the manifest); alongside the
manifest write a `qparego_round.json` sidecar recording the bo-gp commit SHA,
round seed, the 8 weight vectors, the queried-only ideal/nadir used for
normalization, and the indices of the observations used. Objective
normalization to [0,1] inside q-ParEGO uses the ideal/nadir of the observed
Stage-2 rows only (no-leakage rule; there is no table to leak from here, but
the code path is the same as the Stage-1 replay).

Design-space handling: continuous acquisition optimization inside the box
(random restarts + Powell, the repo's `_propose_with_restarts`); no snapping.
Round seed convention: `seed = 1000·k + <init seed>` so seeds are recorded
and reproducible per round.

**Stopping / reporting (§5.2 claims):** exact hypervolume (`hypervolume_exact`)
after every round against a reference frozen after batch 0 as
nadir(n₀) + 0.1·(nadir(n₀) − ideal(n₀)) per objective (frozen so rounds are
comparable; the sequential ParEGO in bo-gp freezes its box the same way);
stop at the planned R or when the HV gain over the last two rounds is
< 1 % of the current HV, whichever first. Report the M = 4 front and the
cost–shed 2-D front (as in Stage 1), and the found designs against the
sweep/interaction structure (SWEEP.md).

### 2.3 Where files land

```
waves/stage2_<S>_n0/    design_matrix.csv (16 rows), retrofit_gen_dict_<i>.json, manifest.json,
                        stage2_<S>_n0_array.sh, objectives.csv (after summarize_wave)
waves/stage2_<S>_r<k>/  same layout, 8 rows, + qparego_round.json
analysis/stage2/        HV-per-round table, front plots, seed-stability summary (new analysis dir)
```

## 3. Run-count and wall-clock estimates (~10 h/run, full year)

Per scenario, one init seed:

| through round | runs | core-h (10 h/run) | wall (batches × ~10 h) |
|---|---|---|---|
| n₀ only | 16 | 160 | ~10 h |
| R = 2 | 32 | 320 | ~30 h |
| R = 3 | 40 | 400 | ~40 h |
| R = 5 | 56 | 560 | ~60 h |

D2's recommended scope (A: n₀ only; B and C: n₀ + 5 rounds) = 16 + 56 + 56 =
**128 runs ≈ 1,280 core-h** (D2 quotes ≈ 1,245 at 9.7 h/run). B and C can run
concurrently (16 concurrent full-year jobs each = 32 licenses; the screening
batch demonstrated 12 sustained — re-check the Gurobi license ceiling before
submitting both at once, else stagger). Rounds are strictly sequential within
a scenario (each round's proposals need the previous batch's objectives), so
the ~60 h per scenario is a floor, plus minutes per round for proposal +
commit + submit.

## 4. Open items for the PI (blockers before launch)

1. **0911-D2 scope + budget** — which scenarios get rounds, and how many.
2. **Seed stability (§5.2 ii) vs the D2 budget.** §5.2 asks for stability
   across ≥ 3 init seeds; D2 budgets one Sobol sequence per scenario. Options:
   (a) 3 independent n₀ + rounds per scenario (≈ 3× budget); (b) share n₀ and
   vary only the round seeds (weight draws + acquisition restarts) — cheaper,
   tests optimizer stability but not init stability; (c) one seed now, seeds
   2–3 after the first sequence converges. Needs a decision; the plan above
   is written for (c).
3. **Reference-point freeze rule** (nadir of n₀ + 10 %) — confirm, since it
   fixes what "HV plateau" means for the stopping rule.
4. Stage-1 evidence that bears on Stage 2: 4-D non-domination inflates fronts
   (71–73/81 on the pair grids), so track the cost–shed 2-D front alongside
   M = 4 HV in Stage 2 as well.
