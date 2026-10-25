# PHASE_B — heteroscedastic shed GP (prompt 43 v3)

**Status: STOP-FOR-DECISION (pre-named in §6 of the prompt). 2026-10-25.**
The 12-arm tie walk crowned a reference arm. The prompt names this
outcome a recorded finding and a STOP, not a winner. We committed what
exists. We did not touch the holdout. `grade_holdout.py` refuses to run:
`winner_commit.json` does not exist.

## 1. What ran and what did not

Ran:
- 12 LOO fits on the n0 = 32 training arm (8 competing + 4 reference).
- The pinned frozen-hyperparameter LOO unit test on every fitted arm.
- The tie walks: 8 competing arms, then all 12 arms.
- fig3 (sigma(y) overlay). It does not need a winner or the holdout.

Did not run (blocked by the STOP):
- The holdout grading (3 scorings). The holdout stays frozen.
- fig1, fig2, fig4. They need a committed winner and a holdout verdict.
- `winner_commit.json`. We wrote `STOP_FOR_DECISION.json` instead.

Do not run `grade_holdout.py` before Kay decides. It will refuse.

## 2. Trigger record (why Phase-B is open)

Both pre-registered triggers fired 2026-10-23 (REPLICATE_RESULT.md,
rep41 f3aad22): measured pooled sd 285.3 MWh (df 10, CI [162, 1057] via
Satterthwaite nu 3.02) inside [180, 880] where prompt 42's converged
sweep passes nothing; and the rejection trigger — per-design sd
0 / 13.34 / 520.1, variance ratio unbounded.

## 3. Noise models (pinned; as implemented)

Anchors = the pinned Population-1 per-design sd estimates
(REPLICATE_RESULT §3, cross-submission scale):

| shed level y | sigma anchor (MWh) | df | chi2 95% CI |
|---|---|---|---|
| 429.5 | 0 | 2 | [0, 0] (degenerate; "no variation observed", not "sigma known = 0") |
| 4,672 | 13.34 | 3 | [7.56, 49.7] |
| 37,834 | 520.1 | 3 | [294.6, 1,939] |

Carried caveat (verbatim from REPLICATE_RESULT): one design per
stratum — design identity and shed level are confounded.

- Form (ii): piecewise-linear through the anchors. Recomputed slopes:
  0.003144372422 on [429.5, 4,672] and 0.015281346119 on
  [4,672, 37,834]; the last slope continues above 37,834. Both round
  exactly to the pinned printed values 0.0031444 / 0.0152813 (see
  deviation D1 for the assert tolerance).
- Form (iii): sigma = 0 for y < 2,000; 13.34 for 2,000 <= y < 15,000;
  520.1 for y >= 15,000. Disclosed: the sigma-step at 15,000 is a
  cliff under the §5 plug-in rule; form (ii) has no cliff.
- Reference arms: homoscedastic sigma = 285.3 (the pooled scalar;
  "scalar framing rejected — reference only").

Unit chain for every point: v_i = (sigma(y_i) / (J_i · sy))^2 + 1e-12,
J_i = (1 + y_i) for log1p configs, J_i = 1 for std configs; jitter is
variance in standardized units. Raw-MWh equivalent of the jitter at the
largest training point: 0.0295 MWh (log1p arms), 0.0037 MWh (std arms).
Both are far below the MID anchor 13.34 MWh.

**Structural disclosure (verbatim):** no training arm has any point in
the HIGH stratum (max training shed 13,729 < 15,000 at every n0;
train-32 strata 14/18/0). The holdout has 3 points >= 15,000 (max
16,586 — 2.3x below the HIGH anchor). Consequences, stated ex ante:
selection cannot test the HIGH-stratum noise; (ii)-vs-(iii)
differences are decided mostly by the MID stratum; the final verdict is
dominated by the latent mean/kernel, and Phase-B tests "narrow AND
calibrated", not "HIGH-noise correctness". (Asserted at run time:
train-32 strata are 14/18/0; max 13,729 MWh.)

## 4. Implementation notes

- Float64 end-to-end for all Phase-B tensors. This deviates from the
  campaign float32 convention and is disclosed here: float32's
  min_fixed_noise clamp (1e-4 variance) silently flattens every noise
  design, and the LOO inverse is unstable at v_i ~ 1e-5.
- Likelihood: `FixedNoiseGaussianLikelihood(noise=v,
  learn_additional_noise=False)` built inside
  `gpytorch.settings.min_fixed_noise` overridden to 1e-14 for double,
  with a hard `torch.equal(lik.noise, v)` assert. The likelihood has
  zero trainable parameters (asserted): "no learned noise
  hyperparameters" is structural.
- Fits: new class `PhaseBExactGP` (plain ExactGP + campaign kernel
  configs) in phase_b/; direct `common.train_gp(..., n_epochs=5000,
  lr=0.01)` calls; `torch.manual_seed(0)` immediately before every
  fit; dloss100 rule (> 2e-3 at 5,000 -> refit from scratch at 10,000,
  same seed); one jitter retry (cholesky_jitter 1e-4) on failure.
- LOO: closed form, reimplemented; Kn = K + diag(lik.noise) with the
  vector AS STORED post-assert; alpha through the LEARNED constant
  mean; Cholesky solves only; no `fast_pred_var`, no `linalg.inv`
  anywhere in Phase-B.
- Selection metrics: `common.metrics(y_raw, LOO mu_t, LOO sd_t,
  transform, floor=285.3)`; the floor arg fills only the relabeled
  `rmse_over_pooled_sd` column; every other metric is
  floor-independent.
- Fit boundary sentence for the paper: campaign tables use the
  700-step house fit as deployed (P17); Phase-B uses the converged
  definition because the likelihood is the object under study.

## 5. Convergence

All 12 fits converged at 5,000 steps. Max dloss100 = 8.9e-4 < 2e-3.
No fit extended to 10,000. No jitter retry. No failure. See
`convergence_log.csv`.

## 6. Unit tests

- `common.nlpd_unit_test()` PASS (< 1e-5) before any fit.
- Pinned frozen-hyperparameter LOO test, indices {0, 7, 15, 23, 31},
  re-conditioned on the other 31 points with NO retraining: run on all
  12 arms. Worst |d mu_t| / sy = 1.9e-13 (bar 1e-6); worst
  |d sd_t| / sd_t = 7.8e-14 (bar 1e-6). PASS with ~7 orders of margin.

## 7. Selection result (LOO on n0 = 32 only)

Ranked by LOO NLPD in original units (`loo_table.csv` has the full
table, per-stratum rms_z, and paired delta-NLPD columns):

| rank | config | ref | NLPD | RMSE | cov95 | rms_z (LOW/MID) | dNLPD vs walk-8 winner (± paired se) |
|---|---|---|---|---|---|---|---|
| 1 | m52+log1p+ref | yes | 7.7677 | 946.5 | 30/32 | 0.96 / 1.00 | −0.0173 ± 0.2587 |
| 2 | rbf+log1p+ref | yes | 7.7682 | 894.6 | 30/32 | 1.06 / 1.09 | −0.0167 ± 0.2688 |
| 3 | rbf+log1p+ii | no | 7.7849 | 1094.5 | 30/32 | 1.07 / 0.93 | 0 (walk-8 winner) |
| 4 | rbf+log1p+iii | no | 7.7852 | 1095.8 | 30/32 | 1.07 / 0.93 | +0.0002 ± 0.0001 |
| 5 | m52+log1p+ii | no | 7.9045 | 1070.4 | 32/32 | 1.16 / 0.79 | +0.1196 ± 0.0567 |
| 6 | m52+log1p+iii | no | 7.9047 | 1071.4 | 32/32 | 1.16 / 0.79 | +0.1197 ± 0.0567 |

(std-transform arms rank 7–12; NLPD 8.23–8.35.)

- 8-arm competing walk: winner **rbf+log1p+ii** (NLPD argmin among the
  8; within 0.02 nats: rbf+log1p+ii, rbf+log1p+iii; the RMSE rule did
  not change the winner). This arm is NOT committed.
- 12-arm walk (part_h.py:163-169 semantics, window relative to the
  CURRENT leader, chained hops): starts at m52+log1p+ref, hops to
  **rbf+log1p+ref** (within 0.02 nats, strictly lower RMSE 894.6 <
  946.5). A reference arm is crowned -> STOP-FOR-DECISION.
- The 0.02-nat window is a pinned convention, not a significance
  claim. The paired per-point delta-NLPD between the best reference
  arm and the best competing arm is −0.017 ± 0.259 (se, n = 32): no
  statistical separation. Forms (ii) and (iii) are near-identical on
  this training set (+0.0002 ± 0.0001): the MID stratum decides, as
  disclosed ex ante.
- Per-stratum LOO rms_z (the free diagnostic): no value is >> 1 in
  MID for any arm (max 1.28, std arms). The anchors do not look too
  small on the training data.
- Disclosed (verbatim): selection uses the n0 = 32 arm only (part_h
  convention, comparability with prompt 42; the three arms are nested
  so they are not independent votes; no selection data exists above
  13,729 MWh under any scheme).

## 8. The decision Kay owns

Spending the one holdout scoring on the rejected scalar framing
requires Kay's sign-off. Options as the prompt frames them:
(a) sign off the pre-named finding and commit the competing walk-8
winner rbf+log1p+ii to the holdout (the reference arms stay reported,
not eligible); (b) spend the scoring on the crowned reference arm
rbf+log1p+ref (this reverses the "scalar framing rejected" decision
and needs an explicit sign-off); (c) amend. The LOO evidence: the
reference advantage is 0.017 nats with paired se 0.26, and the
heteroscedastic arms carry the measured noise structure that the
trigger record demands.

After the decision: write `winner_commit.json` (or re-run `select.py`
under an amended eligibility rule), then run `grade_holdout.py`, then
`make_figs.py` (figs 1, 2, 4). The pinned bar, the 3-scoring exposure
(103 + 3 = 106), and the CI-endpoint sensitivity stay as specified.

## 9. Pinned disclosures that apply to the pending grading (verbatim)

- Plug-in caveats (§5): coverage uses sigma at the predicted median,
  so bands are not conditionally calibrated where the mean errs by a
  stratum width; selection (sigma at observed y_i, LOO) and grading
  (sigma at predicted median) are different functionals — internal
  and arm-uniform, disclosed.
- c2b (§7): sd_strat = sqrt((18·0² + 27·13.34² + 3·520.1²)/48) ≈
  130.4 MWh. Disclosed ex ante: campaign-scale RMSE is ~1,000–2,000
  MWh, so c2b is effectively unattainable and the RMSE criterion is
  c2a in practice.
- Over-wide models (§7): the pinned bar cannot fail an over-wide model
  (cov95 = 48/48 passes c1); narrowness is enforced at selection
  (LOO NLPD) only — kept verbatim for comparability with prompt 42.
- Scalar control (§7): the comparison row is prompt 42's converged
  sweep at floor 306 (≈ 285.3), an interpolation, not a fresh 285.3
  run.

## 10. Honesty block

No frozen file is touched; all new code lives in phase_b/. Anchors are
measurements consumed as constants; nothing in §3 is tuned on any
objective; selection never touched the holdout; the single holdout
call follows the committed winner — no winner is committed, so no
holdout call was made. Holdout exposure stays at 103 scorings.
float64 and the min_fixed_noise override are disclosed (§4 above).
Clone of the LOCAL floor40 repo at cc7647c; the uncommitted
PROVISIONAL_GP.md corrigendum edit is not in the clone (harmless,
noted). BOGP_PATH not set (common.py default bo-gp-qparego).

## §deviations

- **D1 (slope assert tolerance).** The pinned check "recompute the
  slopes and assert agreement to 1e-6 relative" cannot pass against
  the prompt's own 7-decimal printed constants: the true relative
  gaps are 8.8e-6 (slope 1) and 3.0e-6 (slope 2) and are pure printing
  error. Implemented assert: |recomputed − pinned| <= 5e-8 (half an
  ulp of the printed precision) AND round(recomputed, 7) == pinned.
  Both pass. Any real slope error would exceed this by orders of
  magnitude. Not load-bearing; recorded, not silently patched.
- **D2 (stdlib shadow).** The pinned filename `select.py` shadows the
  Python stdlib `select` module and breaks `import numpy` when the
  script directory is on sys.path. All three scripts carry a 6-line
  prelude that pre-caches the stdlib module and restores the path.
  Mechanical; no pinned behavior changes.
- **D3 (min_variance override).** gpytorch clamps posterior variances
  at 1e-10 (double). Prediction and the unit test run under
  `min_variance` overridden to 1e-14, the same rationale as the
  pinned min_fixed_noise override: no silent flattening near zero
  noise. Without it the clamp would spuriously fail the 1e-6 unit-test
  tolerance at near-noiseless points.
- **D4 (unit-test scope).** The pinned frozen-hyperparameter test
  names the n0 = 32 arm and indices {0, 7, 15, 23, 31}. It ran on all
  12 fitted arms (every fit is an n0 = 32 arm), a superset of the
  pinned requirement.
- **D5 (deferred outputs).** figs 1, 2, 4, `winner_commit.json`,
  `holdout_final.csv`, `holdout_verdict.json`, `train_predictions.csv`
  do not exist yet: the pre-named STOP-FOR-DECISION blocks them.
  `make_figs.py` defers them automatically until the decision lands.
- **D6 (extra files).** `loo_predictions.csv` (per-point LOO, feeds
  fig2), `STOP_FOR_DECISION.json`, `select_run.log` are extra outputs
  beyond the pinned list; nothing pinned is renamed or dropped.
- **D7 (fig4 n0 choice, pending).** The prompt pins fig4 as a
  before/after "pair" but not the n0 panel. Implemented at n0 = 48
  (both sides, same axes). Change before running if Kay wants all
  three n0.
