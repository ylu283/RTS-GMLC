# TL=360 probe — verdict memo (prompt 33)

**Status: v1.1 (2026-10-11) — T2 filled from the 3 TL=360 solves
(ercot-bot 1a3a89e), then corrected after a two-agent review (numbers
audit + skeptical referee). The T0 analysis and the prediction below are
unchanged from v0 (committed 10-09 in 2c11e7e, before any TL=360 run).
Route decision = Kay/PI.**

## Verdict (10-11)

**gen-1 is not pinned at TL=360, and total cost is not readable. The
outcome is consistent with the prediction. The prediction's stated
mechanism is NOT what the data show. Two new findings matter more than
the route question.**

### Finding 1 — the trigger is the TimeLimit, not a near-tie

- The three solves are bit-identical through 2019-01-08: same gap, same
  RUC cost, every day (`ruc_quality.csv`).
- They first diverge on 2019-01-09. Solve 1 finishes OPTIMAL (661 s, gap
  0.9954%). Solves 2 and 3 stop at TIME_LIMIT (731 s, gap 1.2205%) with a
  different incumbent. Solves 2 and 3 then split on 01-18.
- Gurobi is deterministic at fixed Threads. A wall-clock TimeLimit is
  the one thing that breaks this: where the search is when the clock
  fires depends on machine load. The 36 h RUC coupling then carries the
  difference forward (the T0 "path divergence").
- TL=360 still caps on 15 / 22 / 28 days (4.1 / 6.0 / 7.7%), so the
  race still happens. The T0 near-tie analysis explains why the branches
  are close in cost. It does not explain why they differ.
- **Implication:** the fix is a deterministic stop, not more seconds.
  Gurobi's `WorkLimit` (deterministic work units) instead of TimeLimit
  could make reruns bit-identical at about TL=120 cost. This is an
  untested option (Route D below).

### Finding 2 — gen-1's cost data look wrong (gates every route)

- gen-1 costs ≈ $2.13M per committed hour. That is its no-load cost:
  `PMin 729 MW × HR_avg_0 3,598,445 × $0.81035/MMBTU ÷ 1000`
  (`data/ercot123_2019/gen.csv`). gen-93 is the same order: $2.64M/h.
- For comparison, the same row's own `C0/C1/C2` give ≈ $14k/h at
  p_min. Coal no-load is $0.15–0.33M/h.
- Consequence: gen-1's Unit Cost is ≈ $3.2B of the $8.0B system total.
  The unit is OFF 83% of hours (run 1: 1,501 on-hours, measured from
  `thermal.csv.gz`). gen-93 never commits. The ±$56–133M spread is
  ≈ 26 on-hours × $2.13M.
- With a realistic nuclear no-load cost, the "bimodality" would likely
  shrink to the $1M scale. It would also change why gen-1 cycles and
  why gen-93 is idle. This finding concerns this dataset's input
  values; it says nothing about the source paper's price mechanism.
- `gen.csv` is a frozen vendored input (`0e1d68a`, MD5-verified against
  bo-gp-clean). Do not edit it. Kay must confirm the HR_avg_0 units /
  conversion before any route or NXT-D6 choice.

### Decomposition (valid accounting; not causation)

- Σ `Unit Cost` over the 128 thermal units equals overall Total costs
  to within $0.02 in each solve.
- Net Δ by pair: gen-1 −$77.4M of −$71.6M (1–2), −$55.6M of −$55.7M
  (1–3), −$133.0M of −$127.4M (2–3). The other units net +$5.8M / −$0.1M
  / +$5.7M, with gross Σ|Δ| $45–82M. Netting to ≈ 0 is expected:
  cheap units replace gen-1's MWh.
- Solves 1 and 3 have equal gen-1 starts (25) but differ by 47.6k MWh
  of gen-1 output. That is ≈ 20 h at Pmax, or ≈ 26 on-hours at the
  no-load rate. **This is INFERRED.** Solves 2 and 3 are slim extracts;
  only a `--full` re-extract can count their on-hours.
- Option A/E would remove gen-1's term only. The other-unit residual
  (±$5.8M net here) stays.

### Table (pairs in the order 1–2 / 1–3 / 2–3 in every TL=360 cell)

| readout | TL=120 (known) | TL=360 (measured) | verdict |
|---|---|---|---|
| gen-1 annual starts | 25 ↔ 26 (flips) | 25 / 26 / 25 | still flips |
| total-cost \|Δ\| | $79.5M bimodal | $71.6M / $55.7M / $127.4M | not readable |
| fixed-cost \|Δ\| | $79.2M | $70.0M / $56.1M / $126.1M | ≈ all gen-1 |
| var-cost \|Δ\| | $0.29M | $1.57M / $0.37M / $1.20M | looser (df = 2 vs 1) |
| true-curt \|Δ\| | {5,479, 5,007} clean | 13,854 / 30,896 / 17,042 MWh | looser (df = 2) |
| median / P95 gap | 0.98% / 1.36% | 0.97–0.98% / 1.00–1.25% | 1% mipgap is the binding stop |
| % days capped (status TIME_LIMIT) | 12% | 4.1 / 6.0 / 7.7% (per solve) | fewer caps, not zero |
| annual RUC solve time | 14.0 h | 29.3 / 31.5 / 37.0 h (2.1–2.6×) | see note |
| wall per run | 15–22 h | not measured (no job logs in repo) | — |

- Note on solve time: `solve_time_s` is Prescient's "Pyomo model solve
  time". It wraps several Gurobi solves per RUC (lazy-PTDF LP + MIP
  re-solves) plus Pyomo I/O, so it can exceed the TimeLimit. It is
  RUC-only and load-sensitive, not wall per run. Prompt 33 §3's
  "+20–30%" was a per-run estimate, so it is not directly comparable.
- TL=360 readings stay quarantined. "Looser" compares scales only; the
  "var_cost is the readable cost column" claim rests on TL=120 evidence
  alone.
- Test strength: the prediction passed unless all 3 solves agreed AND
  |Δ| collapsed. With n = 3 the probe supports "not pinned"; it does not
  establish a mechanism. Finding 1 comes from the day-level logs, not
  from the n = 3 readings.

**Route recommendation (provisional):** do NOT rebase at TL=360 (Route
A fails both conditions and costs ≥ 2× RUC time). Before choosing
between B, C and D, (1) audit gen-1's cost data (Finding 2), and (2)
consider a small deterministic-stop probe (Route D). Under B, var_cost
stays the cost column; NXT-D6 A/E then removes gen-1's term, with the
other-unit residual stated.

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

- **Route D — deterministic stop (added 10-11, untested):** replace
  TimeLimit with Gurobi `WorkLimit` (and/or a tighter mipgap such as
  0.25% on a probe) so reruns are bit-identical. Probe cost ≈ 2–3 base
  solves. Must first check that Prescient/egret passes the option
  through (`--ruc-solver-options` or equivalent).

Record the PI's route choice in pi-agenda §4 when it lands.
