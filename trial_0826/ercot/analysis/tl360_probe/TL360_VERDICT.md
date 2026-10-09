# TL=360 probe — verdict memo (prompt 33)

**Status: v0 (2026-10-09) — T0 analysis + PRE-REGISTERED prediction,
written BEFORE any TL=360 run. T2 fills the measured column and renders
the verdict; route decision = Kay/PI.**

**The PI's question (10-08 meeting, item 1):** at RUC TimeLimit = 360 s,
does gen-1 (2,430 MW NUC @ bus 107) behave "normally" — does the 25↔26
annual-starts flip (the ±$79.5M total-cost bimodality) disappear?

## Priors (cited, not re-derived)

TL=120 base: median RUC gap 0.98%, P95 1.36%, 12% of days capped
(`extracts/base_2019/ruc_quality.csv`). Block-2 measurement
(CONFIG_ERCOT.md): TL=600 improved the gap only to ~1.0–1.4% — more time
buys almost no gap, so if TL=360 helps it is via commitment-plan
stability, not optimality. `ruc_mipgap = 0.01` is frozen config. Both
replicate pairs landed in opposite gen-1 states.

## T0 — near-tie analysis (zero simulations; `t0_neartie_days.csv`)

Method and its honest limits: the base solve is `--full` (gen-1 hourly
commitment available); the base replicate is a SLIM extract (no per-gen
hourly data), so day-level localization uses a **proxy** — hours where
system `committed_mw` differs by ≥ 2,000 MW between the two solves with
a unit-count change. This is a **superset** of gen-1 flips (the
cross-check against base gen-1 hourly states shows mixed attribution —
other large units participate in the divergence; mean step 3,070 MW).

Findings:

1. **159 divergence days**; their day-cost differences sum to **+$61.5M
   of the +$79.5M annual gap** (non-divergence days: median |Δ| $14k vs
   $150k on divergence days).
2. **124/159 divergence days sit INSIDE the day's accepted 1% RUC
   tolerance** (|Δ day cost| / (0.01 × that day's RUC objective):
   median **0.24**). At the decision points, the competing commitment
   plans are **near-ties inside the gap tolerance the solver is told to
   accept**.
3. The remaining 35 days (a September/October cluster, ratios up to
   227×, day swings ±$20–47M) are **downstream path divergence, not
   out-of-tolerance solves**: each solve stays within 1% of the optimum
   *given its own initial conditions*; once the trajectories separate,
   the 36 h RUC coupling legitimately amplifies daily differences far
   beyond any single solve's tolerance. More solve time does not
   un-couple days — it only (maybe) changes which near-tie branch is
   taken, nondeterministically.

## PRE-REGISTERED PREDICTION (recorded before T1 results)

> **TL=360 will NOT pin gen-1.** The flip is a genuine near-tie inside
> the 1% mipgap tolerance, not a time artifact: with `ruc_mipgap = 0.01`
> frozen, a longer TimeLimit still terminates on the same acceptance
> criterion, and the choice among plans that differ by less than the
> accepted gap remains machine-load-dependent. Expected T1 readout:
> gen-1 annual starts still vary across the 3 solves (or sit in one
> state by luck with total-cost pairwise |Δ| still O($10M+)); gaps
> ≈ 1%, unchanged (the TL=600 prior). Only a tighter mipgap or fixed
> commitment (formulation A/E — NXT-D6 menu) pins the state.

Refutation condition (stated now): all 3 TL=360 solves agree on gen-1
starts AND total-cost pairwise |Δ| collapses to ≪ $79.5M (toward the
var-cost scale) — then the time budget mattered and Route A gets a case.

## Verdict table (T2 fills the measured column)

| readout | TL=120 (known) | TL=360 (measured) | verdict |
|---|---|---|---|
| gen-1 annual starts across solves | 25 ↔ 26 (flips) | ? | ? |
| total-cost pairwise \|Δ\| | $79.5M bimodal | ? (3 readings, df=2) | ? |
| fixed-cost \|Δ\| | $79.5M | ? | ? |
| var-cost \|Δ\| | $0.29M | ? | ? |
| true-curt \|Δ\| | {5,479, 5,007} clean | ? | ? |
| median / P95 gap, % capped | 0.98% / 1.36% / 12% | ? | ? |
| wall per run | 15–22 h | ? | ? |

**TL=360 is a NEW solver identity** — these readings never mix with
TL=120 data, rulers, or deltas (separate wave + extract dir, config
stamped in design_matrix and manifest).

## Case-study routes (argue from the table; decide = Kay/PI)

- **Route A — rebase at TL=360:** only if the flip pins AND total-cost
  |Δ| collapses ≪ effect sizes. Cost: all rulers re-measured, screening
  comparability lost (re-run or caveat), ~20–30% longer runs campaign-wide.
- **Route B — stay at TL=120** (the T0-predicted outcome): var_cost
  stays the cost column; the NXT-D6 formulation menu carries the fix
  (A pins gen-1 by construction; E pins the schedule and makes total
  cost readable where it matters).
- **Route C — hybrid:** TL=360 only for showcase case-study runs,
  TL=120 for everything statistical; two-config bookkeeping burden,
  flagged honestly.

Record the PI's route choice in pi-agenda §4 when it lands.
