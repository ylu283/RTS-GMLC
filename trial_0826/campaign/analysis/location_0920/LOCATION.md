# LOCATION.md — v0

> **PRELIMINARY (OAT-based; single-tier evidence, blind to interactions; pair
> grids in flight).** OAT sweeps structurally cannot see interactions — the
> wind pair's known +16–32% sub-additivity is exactly the class of effect this
> analysis is blind to. v1 (from the priority pair grids) supersedes this file;
> this table then moves to v1's appendix with deltas marked.

**Question (PI #1, directive §2.1):** at fixed total PEM MW, does moving
capacity between sites change each candidate objective, or is each objective
≈ f(total) alone? Gates the objective-vector (M) decision → Stage-2 BO round 1.

**Evidence base:** `waves/sweep_B` + `waves/sweep_C` (54 OAT rows each,
complete). `stage2_backfill_C` had **not** landed at execution time
(2026-09-20), so scenario-C nuclear (ω ≤ 0.5, ≤ 200 MW) and pv (ω ≤ 0.8,
≤ 272 MW) curves are truncated to the old level set. Executed evidence:
`oat_preliminary.ipynb` + `figs/` + `oat_*.csv` in this directory.

## Frame (pinned estimators, prompt 28 v3)

- Conversion `MW(tier, ω) = ω × Σ_members PMax` from `tiers.load_gen_pmax()`,
  implemented once in the notebook. Nameplates: nuclear 400, pv 340.5,
  tail 251.5, wind_122 713.5, wind_303 847, wind_317 799.1 MW.
- **Common window = [42.35, 200] MW** (wind_303's ω-floor × nameplate to
  nuclear's old cap), identical for B and C. In-window point counts:
  nuclear 8/9, pv 4/9, tail 5/9, wind_122 1/9, wind_303 2/9, wind_317 1/9.
  The two thin wind tiers trigger the pairwise-window matrix + matched-T
  marginal-slope supplements (`oat_pairwise_matrix.csv`,
  `oat_marginal_slopes.csv`). **The 6-way comparison cannot see T < ~42 MW or
  T > 200 MW — the deep-retrofit wind region (up to 847 MW) is invisible to
  it**; it opens only with the pair grids and the C back-fill.
- Location spread `L(T) = max_i g_i(T) − min_i g_i(T)` on a 1 MW T-grid;
  floor `floor_L` = 95th pct of the **range of 6 draws** from the per-value
  noise model (floor ≡ 1σ Gaussian; MC N = 10,000, seed 20260920). Measured
  factor: 4.04× the single-value floor (n=2 pairwise factor: 2.79×) —
  ratioing to the single-value floor would have manufactured ~2.5× fake
  signal. Primary summary = median-over-T of `L/floor_L`; max-over-T carries
  a multiplicity caveat (max of ~158 correlated reads).
- Variance decomposition = matched-basis nested ANCOVA (naive per-tier fits
  are saturated/degenerate): model 0 = natural cubic spline in T, 4 df,
  knots at pooled-in-window-T quartiles, boundary knots at the window edges;
  model 1 = + tier intercepts; model 2 = + tier×T. Fit on the full pooled 54
  points per scenario — restricting to in-window points leaves wind_122/
  wind_317 with one point each, making tier×T unidentifiable (analysis
  decision, stated here; knots remain as pinned).
- Floors per pi_0911 §3.5 (canonical): shed ±3,000 MWh, curtailment
  ~5,000 MWh, cost ~$0.5M (both cost variants). **Reserve shortfall and
  thermal starts have no floor** (replicate study D3 open): verdicts only on
  effects ≥ 10% of the objective's own range with consistent sign across the
  B and C sweeps; never shed's floor borrowed.

## Verdict table v0

Thresholds as in the prompt: *location-sensitive* = a properly-floored
location statistic ≥ 2, replicated in ≥ 2 independent pieces of evidence
(here: the B and C sweeps); *not resolvable* includes the 1–2× band —
raw ratios recorded so the PI can re-cut.

| Objective | v0 verdict | Ratios (B; C) |
|---|---|---|
| true_curtailment_mwh (g2) | **location-sensitive** | median L/floor_L **7.4; 7.6** (max 11.6; 12.1 at T=200, multiplicity caveat); ANCOVA extra-RMSE/floor ≈ 17×; site ranking stable across window (τ = 0.87; 1.0) and across B↔C (τ = 1.0) |
| total_cost_raw_usd | **location-sensitive** | median L/floor_L **8.8; 8.8** (max ~13 at T=43); ΔR²adj +0.32/+0.30 for tier intercepts; B↔C ranking τ = 1.0 |
| total_cost_less_synthetic_usd | **location-sensitive** | median L/floor_L **8.7; 8.5**; ΔR²adj +0.40/+0.37 (largest intercept increment of any objective) |
| load_shed_mwh | **not resolvable (1–2× band)** | median L/floor_L **0.53; 0.61**, max < 1 in both scenarios; ANCOVA extra-RMSE/floor 1.1×; 1.4× (F_int 13.7; 21.7 spread over 5 df). Below the 6-way range floor yet nonzero in the pooled test — borderline stays here. Ranking also unstable across the window (τ = 0.07 in B). |
| reserve_shortfall_mwh | **location signal (no floor; pending D3)** | 9/15 tier pairs show a median matched-T difference ≥ 10% of the objective's own range with consistent sign in B and C; window ranking τ(B↔C) = 0.87. Not a floored verdict — D3 replicate floor pending. |
| thermal_starts | **not resolvable (no floor; pending D3)** | only 6/15 pairs meet the range-and-replication criterion; window ranking τ as low as 0.33. Weak, patchy signal. |
| NPV | *pending extraction* | — |
| congestion | *pending extraction* (also pending its NXT-D4 definition audit) | — |

**Caveats binding on every row:** (i) OAT blindness to interactions — a pair
grid can overturn any verdict (that possibility is why the grids are in
flight); (ii) nuclear numbers carry the g1 fuel-deletion APPROX caveat (patch
pending PI review — not implemented); (iii) the nuclear B↔C comparison is
valid only ≤ 200 MW (B-scenario back-fills deferred by decision);
(iv) scenario-C nuclear/pv curves truncated to the old level set until
`stage2_backfill_C` lands.

## What v0 already suggests for M (no recommendation yet — that is T2)

Curtailment and the two cost variants separate sites far above their floors
with stable rankings, so a location decision is measurable in them. Load shed
— the headline objective of the screening sprint — is the weakest location
discriminator at matched total MW inside this window. Reserve/starts remain
floor-limited. The draft M recommendation waits for the pair grids
(Kendall-τ redundancy + drop-one Pareto sensitivity, per the prompt).

## Provenance

- Wind-pair grid equivalence: `contour_303x317_C` axes vs `STAGE2_LATTICE`
  verified `np.allclose(atol=1e-9)` = True with max |Δ| ≈ 5.6e-17; exact `==`
  fails (old CSV stores raw-linspace doubles) — **round to 10 decimals before
  any old↔new join on ω** (recorded in `oat_summary.json`).
- Machinery at commit `5012a97`; waves at `40e24c4`. Wave manifests show
  `dirty: true` solely because a concurrent session holds uncommitted
  `analysis/gm_0829/` edits in the shared checkout — the campaign generator
  code itself was fully committed (verify: `git show 5012a97 --stat`).
- MC seed 20260920, N = 10,000, pinned in the notebook.
