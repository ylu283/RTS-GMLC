# Stop-rule suite: results (prompt 37 runs, prompt 50 analysis)

Written in STE-100 style. All numbers come from `results.py` →
`tables/results_numbers.json` and `tables/*.csv`. Data: CRC bot commit
`9f45ea7` (array 1533596, re-collect after patch `b0263e2`) plus the local
Block R summaries (`stops_R-.csv.gz`, `trajectories_R-.json`).
Preregistration: `PREREG.md` §5–§6 and Amendment 1.

## 1. Verdicts (the two handoffs)

### 1.1 The rule-form verdict for prompt 55

> **S0(1·τ_j, w2, K4) NOT ACCEPTED**: early 49.2 % (CI 42.8–55.2 %) vs
> ≤ 20 %; median regret 1.83 τ (CI 1.71–1.97) vs ≤ 1 τ; S0 median regret
> at mean stop r̄ = 3.10 is 1.833 τ vs the S-fix interpolation 1.824 τ
> (above the line by 0.009 τ); Z-needle gate M1 25 % / M3 35 % →
> informative: early 10 % (CI 0–25 %) ✓, median regret 0.62 τ
> (CI 0.50–0.76) ✓, S-fix line 0.616 τ vs 0.612 τ ✗ (above by 0.004 τ).

- The primary cell fails all three criteria. The early-stop and regret
  criteria fail by a wide margin. The S-fix criterion fails by a very
  small margin.
- The Z-needle cell passes two criteria. It fails the S-fix criterion by
  a very small margin. The acceptance needs the primary cell AND Z-needle.
  Thus the rule is not accepted.
- Acceptance uses point estimates (prompt 50 §4). The CIs do not gate.
  They are reported only.

**PREREG §6 named readings (the only readings allowed):**

| reading | applies? | evidence |
|---|---|---|
| S0 ≡ S-fix-2 → report the adapting τ | no | 32.4 % of primary runs stop at r2; the stop round moves with τ at every multiplier (table §3.2) |
| trivially safe → lean on Z-needle / E-short | no | 17.6 % of primary runs have all true per-round gains < τ_j; early rate 49 % |
| ties → no method claim | partly | Z-dis, Z-needle and Z-plateau at n = 96: M1 vs M3 paired difference ≤ 0.31 τ → no method claim from these cells |
| budget-limited → report H_R − H_s | yes | at n = 96, median H/H* is 0.79 (M1). Regret vs H* at the stop is 0.29 (median). Most of that gap remains at the budget end. The stop's own regret is (H_8 − H_s)/τ_j = 1.83 τ, which is the metric above |

No other reading is made. Discussion of other rule variants is
**post-hoc exploratory** and needs fresh confirmation (§3.3).

### 1.2 The D49-4 cap input — DESCRIPTIVE (the rule was not accepted)

Primary cell exactly: E-path-1…5 × M1 × S0(1·τ_j, w2, K4), m = 1, q = 8,
R_frozen, 250 runs.

| stop round s | 1 | 2 | 3 | 4 (cap) |
|---|---|---|---|---|
| runs | 0 | 81 | 64 | 105 |
| share | 0 % | 32.4 % | 25.6 % | 42.0 % |
| evaluations s·q | 8 | 16 | 24 | 32 |

- Evaluations: mean 24.8; quantiles 10 % 16 · 25 % 16 · 50 % 24 ·
  75 % 32 · 90 % 32.
- Of the 105 cap stops, 45 (18 % of all runs) reached K = 4 without firing.
  The other 60 fired at round 4.
- S0 cannot stop at round 1 when w = 2. Thus the 0 at s = 1 is by
  construction.
- Block D (q = 4, 10 runs per method; cap = 32 evaluations), M1,
  evaluations used: τ unscaled mean 9.2 (median 8, 90 % 12); τ·q/8
  mean 12.0 (median 8, 90 % 17.6); 16-evaluation window mean 20.0
  (median 18, 90 % 28.4). This is a sensitivity check only (10 runs).
- No pooling across the B-block noise multipliers. No %H̃₀ re-expression.
  m = 1 is the measured noise scale by construction (Amendment 1 item 5).

Figure: `figs/fig_cap_input.png`. Table: `tables/cap_input_primary_hist.csv`,
`tables/cap_input_blockD_evals.csv`.

## 2. Data integrity

| check | pinned | found | result |
|---|---|---|---|
| runs (trajectories.json) | 1,540 (A 750 · B 120 · C 300 · D 30 · E 340) | same | ✓ |
| stop rows (stops.csv.gz) | 249,420 | **247,020** (A 117,000 · B 18,720 · C 46,800 · D 5,340 · E 59,160) | deviation, explained, Kay approved proceeding |
| MISSING.txt | 1 byte | 1 byte | ✓ |
| Block R files | unchanged | unchanged | ✓ |
| primary cell n | 250 | 250 | ✓ |

**Row-count deviation.** The pinned table counts six S-model rows per 6-D M3
run in BOTH boxes (166 / 188). The collector computes E[HVI] at R_frozen
only. Thus it emits S-model rows in the frozen box only (160 / 182). It has
done this since prompt 37. The gap is 400 6-D M3 runs × 6 = 2,400 rows. The
pinned 2-D M3 count (174) uses the frozen-only convention. Thus the pinned
table is not consistent with itself. No data is missing: every run has a
uniform row count.

**τ ≤ 0 (guard, `b0263e2`).** 4,158 rows have `tau_degenerate = True`. All are
Z-dis × union box, 18/20 seeds (all except 5 and 11), × 3 methods × 77 rule
rows. Every frozen-box τ is positive (minimum 2.6e16). Z-dis seeds 5 and 11
keep their union τ (3.5e14, 2.0e15) as-is. These values are 10³–10⁴× below
typical. The union-box table reports the Z-dis row as "τ degenerate (0 for
18/20 runs)". Its τ columns cover only seeds 5 and 11 and are not
interpretable.

**Exclusion.** 2,040 S-model rows on 2-D replay runs are excluded. They come
from the NaN E[HVI] array (2-D M3 does not compute E[HVI]).

**Smoke run (Amendment 1).** Every replay table is reported with R-C seed 0
included and excluded (`smoke` column). The smoke never enters a 6-D cell.

## 3. Operating characteristic

### 3.1 S0(1·τ_j, w2, K4) by cell and method (R_frozen; 20 seeds unless stated)

| cell | method | early | cap | late | late_net | mean s | median regret (τ) |
|---|---|---|---|---|---|---|---|
| E-path pooled (250) | M1 | 0.49 | 0.18 | 0.11 | 0.03 | 3.10 | 1.83 |
| E-path pooled (250) | M3 | 0.28 | 0.42 | 0.07 | 0.01 | 3.62 | 1.57 |
| E-path pooled (250) | M4 | 0.36 | 0.02 | 0.58 | 0.15 | 2.37 | 1.03 |
| Z-needle | M1 | 0.10 | 0.35 | 0.80 | 0.35 | 3.65 | 0.62 |
| Z-needle | M3 | 0.60 | 0.25 | 0.20 | 0.15 | 3.00 | 1.86 |
| Z-plateau | M1 | 0.10 | 0.30 | 0.70 | 0.50 | 3.55 | 0.48 |
| Z-dis (stress) | M1 | 0.00 | 0.80 | 0.70 | 0.25 | 4.00 | 0.47 |

All other cells and every rule variant: `tables/S0primary_by_cell_method.csv`,
`tables/oc_6d_frozen.csv`, `tables/oc_6d_union.csv` (secondary, PREREG §6).
Per path (M1): early 0.42–0.56, median regret 1.45–2.26 τ
(`tables/primary_per_path.csv`). Every path fails both thresholds.
Figure: `figs/fig_oc_rates.png`.

### 3.2 Sensitivity context (anti-forking: NOT a basis for the verdict)

- **τ multiplier** (primary cell, M1, w2 K4). Share of runs that stop at r2:
  0.25τ 0 % · 0.5τ 6 % · 1τ 32 % · 1.5τ 60 % · 2τ 78 %. The rule adapts at
  every multiplier.
- **Noise (block B, 20 pooled runs per m, M1).** m = 0.5: cap 80 %, regret
  3.1 τ. m = 2: early 30 %, regret 1.1 τ. τ_j scales with m. Thus regret in τ
  units falls as m rises.
- **q = 4 (block D, M1).** Early 70 % for the τ-unscaled and τ·q/8 variants.
  Early 40 % for the 16-evaluation window.

### 3.3 Other rules on the primary cell (post-hoc exploratory)

On the primary cell (M1), S-OCD K4, S-rel 2 % K4 and S0 have about the same
median regret (1.85–1.89 τ, mean of per-path medians). S-OCD has the highest
early rate (0.80). S-model (M3 only) w2 K4: early 0.27, regret 1.68 τ. The
oracle stops at mean round 1.6 (M1). These numbers are context only. They
make no claim. Figure: `figs/fig_frontier.png`, `figs/fig_regret_primary.png`.

## 4. PREREG §5 deliverables

**Gain-noise null.** Primary cell: 1,068 rounds have true gain < 0.1 τ_j
(17.8 % of rounds). The observed gain is ≥ τ_j in 1.2 % of them
(false-continue rate). τ_j CV across seeds is 0.24–0.29 per E-path.
Thus noise rarely makes the rule continue. The early stops come from true
gains that are small per round but large over four rounds. The median true
per-round gain (M1) is 1.02 τ at r1, 0.70 τ at r2, 0.50 τ at r3 and 0.43 τ
at r4. Table: `tables/gain_null.csv`, `tables/primary_M1_true_gain_by_round.csv`.

**Stage-2 conditional check.** 38 runs match the Stage-2 gain pattern
(g₁ 3.5–7.5 %, g₂ 0.5–2.5 % of H̃₀). The primary window gave ≥ 10 matches,
so it was not widened. True remaining gain after r2: H₄ − H₂ median 1.00 τ
(IQR 0.61–1.51) = 5.6 % of H₀; H₈ − H₂ median 2.23 τ (IQR 1.75–3.21) =
13.0 % of H₀. Table: `tables/stage2_conditional.csv`.

**Calibration audit vs error.** 8,640 audited rounds over 70 problem × round
strata. Spearman(max |log RMS|, |shortfall|): median ρ −0.006 (IQR −0.09 to
0.04). For the binary verdict, the median ρ is −0.006. 78 % of rounds fail
the audit. Rounds that fail have a lower median |shortfall| (0.87 τ) than
rounds that pass (0.95 τ). Thus the audit does not predict the HV prediction
error on these problems. This result is descriptive and has no p-values.
Table: `tables/calibration_spearman.csv`.

**Density.** Primary cell (M1), median share of non-dominated observed points
at the stop: 0.48 (s = 2), 0.46 (s = 3), 0.45 (s = 4). The PREREG "limit 3"
is read as the stop rounds of a K4, w2 rule (2–4). Table:
`tables/density_at_stop.csv`.

**Fixed-budget method comparison (6-D).** Primary cell, median H_n^true/H*:

| n | M1 | M3 | M4 |
|---|---|---|---|
| 64 | 0.735 | 0.787 | 0.672 |
| 96 | 0.785 | 0.838 | 0.694 |

At n = 96, M3 ≥ M1 on every E-path and on E-mean and E-short (paired
M3 − M1 regret −0.7 to −3.0 τ). On Z-dis, Z-needle and Z-plateau at n = 96,
M1 and M3 tie (|paired| ≤ 0.31 τ). M4 is worst in every cell. Table:
`tables/method_6d.csv`. Figure: `figs/fig_method_6d.png`.

**M2 trigger (pre-registered) — FIRES.** Pooled primary, median H_n^true/τ_j:
M1 − M3 = −1.70 (n = 64), −1.45 (n = 96). Paired medians: −1.47 and −1.54.
|Δ| > 1 at both budgets. Under PREREG §3/§4, M2 is triggered. Prompt 50 has
zero new simulation, so M2 is not run here. Running M2 is a decision for
strategy.

**Replay (17 noise-free grids, n = 35).** M1 and M4 come from Block R (local).
M3 comes from CRC block E. Median H/H*: M3 > M1 on 17/17 grids and M3 > M4 on
17/17. Paired M3 − M1 regret is −0.06 to −0.79 τ, so all differences are below
1 τ. The grids are dense, as PREREG §6 expected. Including or excluding the
smoke changes only R-C (M4 0.926 → 0.922; paired −0.51 → −0.52 τ). Table:
`tables/replay_method_M1_M3_M4.csv`. Figure:
`figs/fig_replay_methods_M1_M3_M4.png`. The quarantined local 6-D M4 runs stay
closed.

## 5. Deviations and disclosures

1. Stop-row count 247,020 vs pinned 249,420. Section 2 explains the cause.
   Kay approved proceeding with no code change.
2. Z-needle gate reading: the starts (round 0) count as queried. Seed 15 hits
   the basin at round 0 for both methods. Without round 0, the shares are
   M1 20 % and M3 30 %. The gate is still informative (via M3).
3. Z-needle S-fix line: the Z-needle cell's own S-fix medians, interpolated
   at its S0 mean stop (3.65).
4. PREREG §6 says "raw HV primary; prompt 35's floor-robust HV for
   cross-check". **The cross-check was not done.** Prompt 50 does not pin it,
   and the trajectories store raw HV only. It is open.
5. PREREG §3's "1,140 / 1,080" task counts are superseded by Amendment 1's
   1,540 / 680. This note is made here; PREREG is not rewritten.
6. Analysis code changes, all τ-guard or bookkeeping: `analysis.load`
   casts early/late/late_net to 1/0/NaN and adds `tau_degenerate = False` to
   Block R; `fixed_budget` gives NaN τ columns for τ ≤ 0; `oc_table` adds
   n_tau_degenerate, late_net and wasted_net; `_variant` names the q4 variants.
   For τ > 0, all values are unchanged.
7. The CIs are seed bootstraps with 10,000 resamples and seed 20261012. They
   are stratified by path for the primary cell and not stratified for
   Z-needle.

## 6. Files

`results.py` (driver) · `tables/*.csv` + `tables/results_numbers.json` ·
`figs/fig_oc_rates`, `fig_regret_primary`, `fig_frontier`, `fig_method_6d`,
`fig_replay_methods_M1_M3_M4`, `fig_cap_input` (png + pdf; bold labels and
ticks; drawn after a shape assert on the frozen CSVs).
