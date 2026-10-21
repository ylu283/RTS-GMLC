# Prompt 42: shed GP under the provisional floor (executor PROGRESS)

Branch `floor40`, worktree `RTS-GMLC-floor40`, from `4801f03`
(prompt 40 done). Local only, zero PCM runs. Env `bogp-botorch`.

## Executor-pinned details (written BEFORE any sweep fit or holdout score)

The prompt leaves these choices to the executor. Fixed here:

- **Grid:** F = {180, 306, 500, 880, 1500, 1800, 3000} MWh.
- **Configs:** the 7 shed configs, in this order:
  1. default
  2. m32
  3. rbf
  4. log1p
  5. fixnoise
  6. gammaprior
  7. rbf+log1p
- **LOO reselection:** via `part_h.fit_and_score` on `common.arm_data(32)`,
  with `common.FLOORS["load_shed_mwh"]` mutated in place and restored in a
  `finally`.
  - Tie hierarchy: sort by (NLPD, RMSE, list index). Then run the
    part_h.main() loop: a later config replaces the incumbent if
    NLPD ≤ incumbent + 0.02 and RMSE < incumbent RMSE. Exact RMSE ties
    keep the earlier list index.
  - A "tie invoked" is recorded when ≥ 2 configs are within 0.02 nats of
    the NLPD minimum. The record also says whether the RMSE rule changed
    the winner.
- **Seeds:** `torch.manual_seed(0)` before every fit.
- **Jitter policy:** run a fit normally. If it raises, or gives non-finite
  predictions, retry ONCE inside `gpytorch.settings.cholesky_jitter(1e-4)`.
  If that also fails: record converged = False, score nothing, continue.
  Stop the study if any fit of the per-floor winner arm fails both tries.
- **Latent sd:** `gp.model(xq).stddev * gp.sy`, in a helper in this
  folder's script only.
  - Ratio = max / max(min, 1e-9·max).
  - The criterion (3) bar is ratio ≥ 2 at EVERY n0.
- **95 % band** (from `FlexGP.predict_t` μ, σ in transformed units):
  - l = back(μ − 1.96σ), u = back(μ + 1.96σ), where back = expm1 for log1p
    and identity for std.
  - Median raw half-width = median((u − l) / 2).
  - Interval score (α = 0.05) = mean[(u − l) + 40·(l − y)·1{y < l} +
    40·(y − u)·1{y > u}].
  - cov95 comes from `common.metrics` (|z_t| ≤ 1.96, identical to l ≤ y ≤ u).
- **Noise bound ACTIVE:** learned noise (`gp.lik.noise`, standardized) ≤
  1.001 × floor_var.
  - Learned noise is also logged in raw MWh: √noise·sy for std, and
    √noise·sy·(1 + y_med) for log1p (the delta method, the same mapping as
    the floor).
- **Success bar** (pinned, prompt 40 Part B):
  1. cov95 ∈ [43, 48] at every n0 (verbatim; not binom_band);
  2. either clause (a) RMSE(48) < RMSE(16) and RMSE(32) ≤ RMSE(16), or
     clause (b) RMSE ≤ f at every n0;
  3. latent ratio ≥ 2 at every n0.
- **F_pass:** a floor is in F_pass iff the per-floor WINNER arm meets the
  bar. The ACTIVE flag never deletes a pass.
- **Route:**
  - (i) F_pass ∩ [180, 880] ≠ ∅;
  - (iii) F_pass ≠ ∅ but only above 880, flagged WEAK if every such pass
    comes from clause (b) only;
  - (ii) F_pass = ∅.
- **Holdout exposure:** every distinct (floor, config, n0) scored on
  `random_C` counts once; identical (config, floor) arms are scored once.

## Run (2026-10-21) — STOPPED under §4 (fit convergence)

- The sweep ran in full with the house fit: 63 rows, 42 distinct holdout
  scorings, all fits converged by the pinned (exception) definition, no
  jitter retries.
- LOO winner: rbf+log1p at every floor, with no ties. F_pass = ∅, so route
  (ii) under the house fit.
- The default arm meets the full bar at floors 180–880; it is not the
  winner, so it does not count.
- The house `train_gp` (700 Adam steps) does not converge the noise. At
  5,000 steps the noise sits on the bound at every floor
  (`convergence_check.txt`).
  - The prompt's "identical fits at 180 / 306" premise is an optimizer
    artifact.
  - The pinned ACTIVE flag (1.001) reads inactive on all fits, even at
    3,000.
- Decision for Kay in PROVISIONAL_GP.md §3: A (house fit, route ii) or B
  (converged rerun, recommended) or C (campaign-wide fix, strategy).
- Figures are not drawn until that decision.

## Amendment 1 run (2026-10-21) — option B approved (Kay): converged rerun

### Pre-run statement (written BEFORE any converged fit or holdout score)

- **Fit, pinned (this diagnostic only):** 5,000 Adam steps, lr 0.01,
  `torch.manual_seed(0)` per fit, same optimizer (Adam, weight_decay 1e-8)
  — only the step count changes from the house 700. Per fit, the loss
  change over the last 100 steps is recorded; a fit still moving more than
  2e-3 is re-run from scratch at 10,000 steps with the same seed (a
  deterministic trajectory, so the re-run IS the extension) and recorded.
- **Mechanics:** `common.train_gp` is swapped inside `sweep_converged.py`
  only (the convergence_check.py pattern) and restored; the LOO
  reselection (`part_h.fit_and_score`) dispatches through the same wrapper,
  so selection and scoring share the fit definition.
- **Everything else identical to the house sweep:** grid F, 7 configs,
  3 arms, 3 n0, tie hierarchy, jitter policy, joint bar, F_pass rule,
  routes, verbatim cov95 band [43, 48].
- **Pre-run verify, pinned:** default at floor 306 and 5,000 steps must
  reproduce `convergence_check.txt` (learned noise ≈ 309 MWh raw) before
  the sweep proceeds; the script asserts it.
- **Expectation stated before running (Amendment 1):** at convergence the
  noise rails on the bound at every floor, so the ACTIVE flag should read
  ACTIVE everywhere and the floor genuinely controls the bars. Open
  questions: does rbf+log1p keep winning the LOO; does its holdout
  coverage recover; does the default's full-bar pass inside [180, 880]
  survive convergence.
- **Outputs (new, never overwriting the house files):**
  `provisional_sweep_converged.csv`, `joint_bar_converged.csv`,
  `loo_reselection_converged.csv`, `provisional_summary_converged.json`,
  `convergence_log_converged.csv` (per-fit log),
  `predictions_converged.csv` (holdout band per scored arm, for
  assert-before-draw figures without refitting).
- Holdout exposure of this rerun: 42 scorings (same distinct set as the
  house sweep) → cumulative 100.

### Run log (after the sweep)

- Pre-run verify passed: default, floor 306, 5,000 steps → learned noise
  309.4 MWh raw, dloss100 7.4e-4 (matches `convergence_check.txt`).
- 94 converged fits (49 LOO + 45 holdout). **No fit moved more than 2e-3
  over its last 100 steps; the 10,000-step extension never triggered**
  (max 1.8e-3, a fixnoise LOO fit at floor 500). Per-fit log:
  `convergence_log_converged.csv`. No jitter retries; all fits converged.
- LOO winner: rbf+log1p at floors 180–1,800 (no ties). At 3,000 the tie
  rule (0.018 < 0.02 nats) flips the winner to log1p via LOO RMSE
  (1,520 vs 1,716).
- **F_pass = {3,000} → route (iii), not WEAK** (clause a+b: cov95
  44/44/44; RMSE 1,946 → 1,879 → 1,258 ≤ 3,000; ratio ≥ 2.13).
- rbf+log1p coverage did NOT recover at low floors (cov95 33–41 at
  f ≤ 880, n0 = 16/32; worse than the house fit). The default's house-fit
  full-bar pass at 180/306 did not survive (cov95 38–39 at n0 = 32); the
  default now passes at 500–1,800 only (sensitivity; not the winner).
- Learned noise tracks the floor within 0.1–3 % at n0 = 16/32 everywhere;
  the pinned 1.001 ACTIVE threshold still reads INACTIVE below
  1,500–1,800 (softplus approaches the bound asymptotically) — logged as
  context. Genuinely unconstrained: n0 = 48 fits at low floors (noise
  ≈ 650 default / ≈ 1,630 rbf+log1p), floor-invariant across 180–500. No
  pass propagates via the inactive rule (winner passes only at 3,000,
  bound ACTIVE).
- Holdout exposure ACTUAL: **45** distinct scorings (not the estimated
  42) — the winner flip at 3,000 added (3,000, log1p) × 3 n0, forced by
  the pinned per-floor-winner design. Cumulative: 58 + 45 = **103**.
  Disclosed in PROVISIONAL_GP.md §4.
- Figures drawn from the converged sweep only, via
  `make_figs_converged.py`: fig1 criteria-vs-floor map + metric curves
  (CI band, break-evens 1,133/1,726/1,997, INACTIVE-flag shading), fig2
  parity 1×3 at floor 306 (winner rbf+log1p, bar not met — shown as
  measured), fig3 parity n0 = 32 floor 3,000 (log1p) vs 306 (rbf+log1p)
  with the CI text on the figure. All: PROVISIONAL watermark, bold axis
  labels and tick values, annotations asserted against the `_converged`
  CSVs (parity panels redraw `predictions_converged.csv`, no refits).
  One assert tolerance note: recomputed RMSE vs CSV agrees to ~1e-8
  relative (float32 predict_t round-trip); the figure assert uses 1e-6.
- PROVISIONAL_GP.md rewritten: converged sweep = PRIMARY (route iii),
  house sweep kept as §2 campaign-definition sensitivity, decision record
  resolved (Kay chose B), exposure and honesty block updated.
- House-fit outputs untouched: `provisional_sweep.csv`, `joint_bar.csv`,
  `loo_reselection.csv`, `provisional_summary.json`,
  `convergence_check.*`.
