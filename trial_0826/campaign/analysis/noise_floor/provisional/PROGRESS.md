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
