# LOCATION.md — v1 (pair-grid evidence; supersedes v0)

**Evidence base:** the 3 priority pair grids — **nuclear×wind_317, pv×tail,
nuclear×pv** (81/81 rows each, scenario C, collected 09-21/22 by
pairgrid-bot) — plus **wind_303×wind_317** (`contour_303x317_C`,
re-estimated under the same pinned estimators), plus the **un-truncated OAT
preliminary** (re-executed 09-22 with `stage2_backfill_C` folded in;
C-window now [42.4, 251.5] MW). Executed evidence: `pair_apparatus.ipynb`,
`oat_preliminary.ipynb`, `figs/pair_*_8c.png`, `pair_*.csv`,
`t2_summary.json`. v0's table is in the appendix with deltas marked.

**Question (PI #1):** at fixed total PEM MW, does moving capacity between
sites change each objective, or is each objective ≈ f(total) alone? →
gates the objective vector M → Stage-2 BO round 1.

**Standing caveat:** every nuclear number carries the g1 fuel-deletion
APPROX caveat (correction PROPOSED in `analysis/quality_report/`, pending
PI review — not implemented). Key robustness fact: within a pair grid all
81 rows have nuclear active, so under proposed options (a)/(c) — a
**constant** add-back — every pair-grid verdict statistic (tot/full/Δloc/
tilt/I) is **invariant**; only absolute levels shift. Under option (b) the
add-back varies with ω and the nuclear cost slopes would change. The
nuclear-pair cost verdicts below are therefore **conditional on rejecting
(b)**; cross-wave cost comparisons (nuclear-retrofit vs clean rows) wait
on the ruling entirely.

## Verdict table v1

Thresholds as pinned: *location-sensitive* = a properly-floored location
statistic (L/floor_L, extra-RMSE/floor, tilt CI excluding 1, I_raw/2×floor)
≥ 2, replicated in ≥ 2 independent pieces of evidence; *not resolvable*
includes the 1–2× band; floorless objectives use range-and-replication.

| Objective | v1 verdict | Evidence (per pair: nuc×317 / pv×tail / nuc×pv / 303×317) | Δ vs v0 |
|---|---|---|---|
| true_curtailment_mwh | **location-sensitive** | extra-RMSE gate **8.6 / 4.2 / 12.2 / 9.3×** floor; OAT L/floor 9.3×; I_raw/2floor +26 / +3.4 / +6.6 / +25 — strong sub-additivity (each site saturates its own curtailment pool); I_rel +0.22 / +0.08 / +0.08 / **+0.20** (the historical wind-pair "+16–32%" is **+20%** under the pinned estimator). GP LOOCV gate FAILS in all 4 pairs (RMSE 5.2–6.4k vs 5k floor) → along-line quantitative reads suppressed; raw-81 statistics only. | confirmed, sharpened |
| total_cost_less_synthetic_usd | **location-sensitive** *(conditional on g1 ≠ option (b))* | extra-RMSE gate **29.2 / 1.9 / 19.6 / 5.5×**; Δloc up to **0.42** (nuclear pairs — the one-knob reduction leaks 26–43% of variance there); GP gate passes everywhere → along-line reads: max−min along iso-total guides up to **21× the range floor** (nuc×317 median), 1.3× (pv×tail); nuclear per-MW cost slope ≈ **4.9×** the partner's (log₂ tilt −2.28 / −2.24, CI width ±0.02) but the *tilt reading is suppressed* per the pinned rule — quadratic-over-planar extra-RMSE exceeds the floor (curved, not straight-tilted). | confirmed; magnitude now pair-resolved |
| total_cost_raw_usd | **location-sensitive** (same pattern) | gates 30.5 / 2.0 / 21.9 / 5.9×; τ = 0.96 with cost_ls — near-duplicate (see M) | confirmed |
| load_shed_mwh | **location-sensitive (tilt only; magnitude ≤ 1× floor at matched totals)** | extra-RMSE gate **0.8 / 0.2 / 0.6 / 0.9×** — the absolute location effect at matched total is *sub-floor in all four pairs* (agrees with v0). BUT the tilt is real and replicated: log₂ tilt CI excludes 0 in 3/4 pairs — per MW, wind_317 buys ≈ **1.8×** nuclear's shed reduction (CI [1.4, 2.4]) and ≈ 1.7× wind_303's [1.5, 2.1]; nuclear ≈ 3.7× pv [1.6, 8.6]. Site ordering: **317 > nuclear > pv**. I_raw/2floor 1.6–1.8 (borderline band). | **CHANGED**: v0 "not resolvable" → direction resolved, magnitude still sub-floor |
| reserve_shortfall_mwh | **location signal (no floor; pending D3)** | Δloc 0.04–0.24 (largest on nuclear×pv); tilt point estimates sign-consistent with shed's ordering; OAT range-and-replication 9/15 pairs. No floor → no gated statistics; display contours only. | unchanged in kind |
| thermal_starts | **not resolvable (no floor; pending D3)** | Δloc 0.04–0.17; OAT 6/15 pairs; weakest floorless signal | unchanged |
| NPV | *pending extraction* (g1 ruling propagates into any NPV definition) | — | — |
| congestion | *pending extraction* (also pending NXT-D4 definition audit) | — | — |

**Data-quality note (OAT-vs-grid-edge):** 13/32 edge-consistency reads
exceed tolerance, all modestly (1.0–1.6×), concentrated where the partner
tier is large (a 0.05-ω wind partner is ~40 MW of PEM — "present at 0.05"
vs "absent" is a real difference the linear tolerance underestimates) or
where the old OAT grid required interpolation (pv/tail). nuclear×pv shows
zero flags. Flagged and characterized, not averaged away
(`pair_edge_consistency.csv`).

**26-point 6-D supplement (pre-registered EXPLORATORY, n = 26):** LOO RMSE
of GP-on-total-only vs GP-on-6-D-allocation: cost **2.5–2.6×** worse
total-only, starts 1.8×, curtailment 1.16×, shed 1.07×, reserve 1.05× —
consistent with the verdict table's ordering of where allocation matters.

## The MOBO argument, updated (from the 6-tier space)

1. **No objective is a function of the total.** The one-knob reduction
   leaks variance beyond the noise floor for curtailment and cost in all
   four sampled pairs (extra-RMSE 1.9–30.5× floor), and 26–43% of raw
   variance on the nuclear cost pairs.
2. **The objectives genuinely conflict — and the 19b prior reverses.**
   Within the old wind-pair geometry, cost and the reliability cluster
   were nearly collinear (19b: r ≥ 0.96). Across the pooled 324 6-tier
   pair-grid designs, cost is **anti-correlated** with the whole
   reliability cluster: τ(cost_ls, shed) = −0.56, τ(cost_ls, curtailment)
   = −0.63, τ(cost_ls, reserve) = −0.62, τ(cost_ls, starts) = −0.63.
   Buying reliability/curtailment relief costs money at a rate that
   depends on *which site* — cost's per-MW slope penalizes nuclear ~5×
   more than its partners (uncorrected accounting; invariant under g1
   (a)/(c)) while shed's per-MW value ranks 317 > nuclear > pv.
3. Therefore a scalarized single objective would bake in a site ranking
   that the objectives disagree on; the front must be surfaced. This
   argues from four pairs spanning thermal, PV-cluster, mixed-tail and
   wind tiers — not from any single pair.

## Draft M recommendation (RECOMMEND — decision is Kay/PI's)

**M = 3: {load_shed_mwh, true_curtailment_mwh,
total_cost_less_synthetic_usd (with the g1 add-back once ruled)}.**

- **Drop reserve_shortfall and thermal_starts:** drop-one Pareto on the
  pooled designs marks both redundant (front-overlap 0.988, HV change
  ≤ 0.01%); τ with shed 0.86–0.91 (one reliability axis suffices, and
  shed is the PI's headline); both are floorless until D3 lands, so they
  could not be noise-gated inside BO anyway. Revisit post-D3.
- **Keep exactly one cost.** cost_raw↔cost_ls τ = 0.959. Drop-one
  slightly favors keeping cost_raw (overlap 0.901 when dropped vs 0.988
  for cost_ls) but the difference between the columns *is* the synthetic
  bid-cost artifact K_syn — a design-dependent accounting term, not
  physics — so we recommend the principled **cost_less_synthetic**,
  upgraded to the corrected column when the PI rules on g1. This is a
  judgment call against the raw drop-one signal; stated openly.
- **Keep curtailment:** the least redundant objective (overlap 0.815
  when dropped, the largest HV change) and the strongest location signal.
- Small, interpretable, non-redundant: reliability, renewable
  integration, economics — one axis each. NPV/congestion join as
  post-hoc extractions if adopted later; the retained raw runs support
  both.

## What T3 needs

The same pair-generic pipeline (`pair_apparatus.ipynb` — every estimator
is a function of the wave dir + manifest pair) mapped over each remaining
`pairgrid_*/objectives.csv` as Kay's staggered submissions land
(`SUBMIT_QUEUE.md`, 11 waves). Atlas: heat-table of extra-RMSE/floor and
log₂ tilt per pair × objective; multiplicity control = the ≥ 2-evidence
replication rule; report the 2–3× band count. Never block the memo on
stragglers.

## Plain-register summary (for Kay)

Where you put the electrolyzers matters for curtailment and cost — far
above noise in all four sampled tier pairs — but for load shed only the
*direction* is resolved (wind-317 MW buys about twice the shed relief of
nuclear or wind-303 MW; the absolute difference at a fixed total stays
inside the noise floor). Cost and reliability now pull in opposite
directions across the six-tier space (they were aligned in the old
wind-only view), so a single blended objective would silently pick a side
— that is the case for keeping the multi-objective search. We recommend a
3-objective vector: load shed, curtailment, and synthetic-free cost, with
reserve/starts dropped as redundant-and-floorless and revisited after the
replicate study. The nuclear cost numbers still await Prof. Dowling's
g1 fuel-accounting ruling — the pair-grid verdicts are safe under the
recommended constant add-back but would change under the delivered-only
variant, which is one more reason to settle it before BO round 1.

---

## Appendix — v0 verdict table (OAT-only, 2026-09-20) with v1 deltas

| Objective | v0 verdict (OAT) | v1 outcome |
|---|---|---|
| true_curtailment_mwh | location-sensitive (L/floor 7.4–7.6×) | **confirmed** (4/4 pairs; saturation quantified: I_rel ≈ +0.2 on wind and nuclear×wind pairs) |
| total_cost_raw_usd | location-sensitive (8.8×) | **confirmed** (gate up to 30×) |
| total_cost_less_synthetic_usd | location-sensitive (8.5–8.7×) | **confirmed**, now conditional on g1 ≠ (b) |
| load_shed_mwh | not resolvable (1–2× band; L < 1× floor) | **CHANGED** → tilt-only location sensitivity: replicated 317-leaning direction, magnitude still ≤ 1× floor at matched totals — an interaction-free OAT could not see the tilt; the grids could |
| reserve_shortfall_mwh | location signal, no floor (9/15 pairs) | unchanged in kind (Δloc up to 0.24 added) |
| thermal_starts | not resolvable, no floor (6/15) | unchanged |
| NPV / congestion | pending extraction | unchanged |

v0's full text is preserved in git history
(`a7dfa6b:trial_0826/campaign/analysis/location_0920/LOCATION.md`); its
OAT machinery outputs were refreshed 09-22 with the back-fill folded in
(window [42.4, 251.5] MW; C-scenario medians: curtailment 9.3×, cost
7.2–7.3×, shed 0.65×).
