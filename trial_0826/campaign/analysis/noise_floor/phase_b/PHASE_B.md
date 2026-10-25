# PHASE_B — heteroscedastic shed GP (prompt 43 v3 + Amendment 1)

**Status: COMPLETE 2026-10-25. Primary verdict: FAIL (c1, c2a, c2b
fail; c3 passes). The holdout is RETIRED for shed model selection.
Exposure 103 + 3 + 3 = 109.**

## 1. Run record

1. Selection ran first (12 LOO fits on train-32). The 12-arm tie walk
   crowned the reference arm rbf+log1p+285.3 — the pre-named
   STOP-FOR-DECISION. We stopped, committed, and reported
   (`STOP_FOR_DECISION.json`, kept for the record).
2. Kay resolved the STOP with **Amendment 1** (appended to the prompt,
   written BEFORE any holdout scoring existed): grade BOTH and compare
   in the results deck.
   - **PRIMARY: rbf+log1p+(ii)** — the competing-walk winner. The §7
     bar, the PASS/FAIL verdict and the CI-endpoint sensitivity attach
     to the primary ONLY.
   - **CONTROL: rbf+log1p+285.3** — identical machinery, separately
     labeled (`holdout_control.csv`), NO verdict. A criterion where
     the control grades better is a RECORDED FINDING, never a
     re-selection.
   - fig4 pinned to n0 = 32 (supersedes deviation D7).
3. `commit_amendment1.py` wrote `winner_commit.json` naming both roles
   (loo_table sha256 re-verified against the STOP record).
4. `grade_holdout.py` passed the hash gate, loaded the holdout once,
   and scored primary and control once per n0 (6 scorings).
5. `make_figs.py` built fig1, fig1c, fig2, fig3, fig4 — all
   assert-before-draw against the saved CSVs; no refit touched the
   holdout.

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
train-32 strata are 14/18/0; holdout strata are 18/27/3.)

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
- Prediction (§5 path): latent from `gp.model(xq)` (no likelihood);
  test noise from the §3 chain at the predicted raw median (one pass);
  total sd_t = sqrt(latent² + v_q·sy²); bands mapped back per
  transform. Diagnostic cov95 with sigma at OBSERVED y reported in
  parentheses (not a criterion).
- Metrics: `common.metrics(..., floor=285.3)`; the floor arg fills
  only the relabeled `rmse_over_pooled_sd` column.
- Fit boundary sentence for the paper: campaign tables use the
  700-step house fit as deployed (P17); Phase-B uses the converged
  definition because the likelihood is the object under study.

## 5. Convergence

All 18 fits (12 selection + 3 primary + 3 control holdout fits)
converged at 5,000 steps. Max dloss100 = 8.9e-4 < 2e-3. No extension
to 10,000. No jitter retry. No failure. See `convergence_log.csv`.

## 6. Unit tests

- `common.nlpd_unit_test()` PASS (< 1e-5) before any fit.
- Pinned frozen-hyperparameter LOO test, indices {0, 7, 15, 23, 31},
  re-conditioned on the other 31 points with NO retraining: run on all
  12 arms. Worst |d mu_t| / sy = 1.9e-13 (bar 1e-6); worst
  |d sd_t| / sd_t = 7.8e-14 (bar 1e-6). PASS with ~7 orders of margin.

## 7. Selection result (LOO on n0 = 32 only)

Ranked by LOO NLPD in original units (`loo_table.csv` has the full
table, per-stratum rms_z, and paired delta-NLPD columns):

| rank | config | ref | NLPD | RMSE | cov95 | rms_z (LOW/MID) | dNLPD vs primary (± paired se) |
|---|---|---|---|---|---|---|---|
| 1 | m52+log1p+ref | yes | 7.7677 | 946.5 | 30/32 | 0.96 / 1.00 | −0.0173 ± 0.2587 |
| 2 | rbf+log1p+ref | yes | 7.7682 | 894.6 | 30/32 | 1.06 / 1.09 | −0.0167 ± 0.2688 |
| 3 | rbf+log1p+ii | no | 7.7849 | 1094.5 | 30/32 | 1.07 / 0.93 | 0 (PRIMARY) |
| 4 | rbf+log1p+iii | no | 7.7852 | 1095.8 | 30/32 | 1.07 / 0.93 | +0.0002 ± 0.0001 |
| 5 | m52+log1p+ii | no | 7.9045 | 1070.4 | 32/32 | 1.16 / 0.79 | +0.1196 ± 0.0567 |
| 6 | m52+log1p+iii | no | 7.9047 | 1071.4 | 32/32 | 1.16 / 0.79 | +0.1197 ± 0.0567 |

(std-transform arms rank 7–12; NLPD 8.23–8.35.)

- 8-arm competing walk: winner rbf+log1p+ii (within 0.02 nats: only
  rbf+log1p+iii; the RMSE rule did not change the winner) -> PRIMARY
  under Amendment 1.
- 12-arm walk: crowned rbf+log1p+ref via the chained RMSE hop ->
  the pre-named STOP, resolved by Amendment 1 as CONTROL.
- The 0.02-nat window is a pinned convention, not a significance
  claim. The paired per-point delta-NLPD between the best reference
  arm and the primary is −0.017 ± 0.259 (se, n = 32): a statistical
  tie, expected ex ante given zero HIGH-stratum training points.
- Per-stratum LOO rms_z: no value >> 1 in MID for any arm (max 1.28).
  The anchors do not look too small on the training data.
- Disclosed (verbatim): selection uses the n0 = 32 arm only (part_h
  convention, comparability with prompt 42; the three arms are nested
  so they are not independent votes; no selection data exists above
  13,729 MWh under any scheme).

## 8. Holdout grading (Amendment 1: primary + control)

sd_strat recomputed from observed holdout shed with the form-(iii)
map: 130.41 MWh (pinned ~130.4, assert PASS). Holdout strata 18/27/3,
max 16,586 MWh. All six fits converged.

**PRIMARY rbf+log1p+(ii)** — the verdict attaches here:

| n0 | cov95 (sigma at obs) | RMSE | NLPD | rms_z | latent ratio | half-width latent/total |
|---|---|---|---|---|---|---|
| 16 | 41/48 (41) | 4,993 | 10.31 | 1.52 | 2.96 | 7,754 / 7,754 |
| 32 | 33/48 (33) | 3,099 | 18.93 | 2.93 | 7.26 | 2,006 / 2,006 |
| 48 | 34/48 (34) | 10,366 | 16.42 | 2.44 | 8.66 | 12,224 / 12,225 |

- c1 (cov95 in [43, 48] at every n0): **FAIL** — 41, 33, 34.
- c2a (rmse48 < rmse16 AND rmse32 <= rmse16): **FAIL** — rmse48
  10,366 > rmse16 4,993 (rmse32 3,099 <= 4,993 holds).
- c2b (RMSE <= 130.4 at every n0): **FAIL** (disclosed ex ante as
  effectively unattainable; dead as predicted).
- c3 (max/min latent sd >= 2 at every n0): **PASS** — 2.96 / 7.26 /
  8.66.
- **PASS = c1 AND (c2a OR c2b) AND c3 -> FAIL.** Pre-named next
  steps: targeted high-shed data (prompt 44 proposal) or form (i)
  amendment.
- Note (rms_z vs LOO): holdout rms_z 1.5–2.9 against LOO rms_z 0.99 —
  the measured noise is honest in-sample; the latent model is
  overconfident out-of-sample.

**CONTROL rbf+log1p+285.3** — context only, NO verdict:

| n0 | cov95 (sigma at obs) | RMSE | NLPD | rms_z | latent ratio | half-width latent/total |
|---|---|---|---|---|---|---|
| 16 | 33/48 (44) | 1,806 | 15.57 | 3.68 | 3.60 | 1,761 / 1,882 |
| 32 | 26/48 (36) | 1,456 | 17.68 | 4.46 | 4.24 | 851 / 1,041 |
| 48 | 32/48 (40) | 1,703 | 14.56 | 3.00 | 5.44 | 1,353 / 1,508 |

- Control bar ARITHMETIC (context, never a verdict): c1 false, c2a
  true, c2b false, c3 true.
- **RECORDED FINDING (never a re-selection): the control grades
  better on c2a** (its RMSE falls with n0: 1,806 / 1,456 / 1,703
  satisfies the verbatim clause). Its cov95 (33/26/32) is worse than
  the primary's at every n0. Consistent with the LOO tie: neither
  framing is calibrated on this holdout; the primary is wider and
  covers more, but its n0 = 48 fit chases the near-noiseless training
  points into large extrapolation medians (RMSE 10,366).

**CI-endpoint sensitivity (primary only, saved predictions, recorded
AFTER the verdict, cannot change it):** with the HIGH anchor at 294.6
and at 1,939 the cov95 triple is unchanged (41, 33, 34) at both
endpoints — the total band is latent-dominated (half-width latent ~=
total above). c1 stays FAIL; c2a unchanged (medians untouched); c2b
stays FAIL at sd_strat 74.3 (low endpoint) and 484.9 (high endpoint).
The verdict is insensitive to the HIGH-anchor CI.

Exposure: 103 + 3 (primary) + 3 (control) = **109** scorings, printed
by grade_holdout.py. The holdout is RETIRED for shed model selection;
no third model ever touches it.

## 9. Figures

All PROVISIONAL-watermarked, bold axis labels AND bold tick values,
assert-before-draw against the saved CSVs (no refit, no new holdout
call):
- fig1_parity_winner_3n0 — PRIMARY dual-band parity at n0 = 16/32/48
  with training points (bo_1021 conventions).
- fig1c_parity_control_3n0 — CONTROL, same layout and the same per-n0
  axes as fig1 (deck comparison).
- fig2_loo_parity_n32 — selection-side LOO parity of the primary.
- fig3_sigma_overlay — both noise forms + anchors with chi2 95% CIs.
- fig4_before_after — n0 = 32 (Amendment 1): prompt-42 converged
  winner at floor 306 redrawn from provisional/predictions_converged
  .csv (RMSE 3,060, cov95 33/48, asserted against the saved sweep row)
  beside the Phase-B primary (RMSE 3,099, cov95 33/48), same axes.

## 10. Pinned disclosures (verbatim)

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

## 11. Honesty block

No frozen file is touched; all new code lives in phase_b/. Anchors are
measurements consumed as constants; nothing in §3 is tuned on any
objective; selection never touched the holdout; the holdout calls
followed the Amendment-1 commit of both roles, written before any
scoring existed. float64 and the min_fixed_noise override are
disclosed (§4 above). Clone of the LOCAL floor40 repo at cc7647c; the
uncommitted PROVISIONAL_GP.md corrigendum edit is not in the clone
(harmless, noted). BOGP_PATH not set (common.py default
bo-gp-qparego). The §8b results deck belongs to the strategy session.

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
  script directory is on sys.path. All scripts carry a 6-line prelude
  that pre-caches the stdlib module and restores the path.
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
- **D5 (STOP interlude).** Superseded by Amendment 1. The STOP run
  wrote STOP_FOR_DECISION.json instead of winner_commit.json and
  deferred figs 1/2/4; Amendment 1 resolved it and the full outputs
  now exist. STOP_FOR_DECISION.json is kept for the record.
- **D6 (extra files).** loo_predictions.csv (feeds fig2),
  STOP_FOR_DECISION.json, commit_amendment1.py, holdout_control.csv,
  train_predictions.csv, train_predictions_control.csv,
  holdout_verdict.json, select_run.log, grade_run.log, fig1c are
  outputs beyond the original pinned list; holdout_control.csv and
  fig1c are required by Amendment 1; nothing pinned is renamed or
  dropped.
- **D7 (fig4 n0).** Superseded: Amendment 1 pins fig4 to n0 = 32;
  implemented at n0 = 32.
