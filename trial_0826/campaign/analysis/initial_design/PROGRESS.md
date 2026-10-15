# Prompt 39 — initial-design evidence — execution log

Executor session, separate clone `RTS-GMLC-n0evidence`, branch `d6`.
Spec: admin/prompt/bogp/39-initial-design-evidence.md (v2, 2026-10-15).
Zero PCM runs. All work is local analysis under `analysis/initial_design/`.

## 2026-10-15T07:29Z — session start, environment asserts

- Clone created at /Users/yilu/Documents/GitHub/RTS-GMLC-n0evidence (branch d6).
- BOGP_PATH = /Users/yilu/Documents/GitHub/bo-gp-qparego.
  `git rev-parse HEAD` = 60e6328236e745b3d34dc8cd704bb72888ae5d15.
  This equals `analysis/bo_stage2/ledger.json::bo_gp_sha`. PASS.
- Env `bogp` (/opt/anaconda3/envs/bogp): torch 2.12.0, gpytorch 1.15.2,
  sklearn 1.7.2, scipy 1.15.3, numpy 2.2.6. No installs needed.
- torch.set_num_threads(4) in every script; total load <= 4 threads.

## §0.1 Expectation statement (recorded BEFORE any fit; the strategy
## session relays it to Kay and the PI — this executor messages no one)

> "The most likely result: shed is already noise-limited at 32 (LOO
> 0.4 x floor — more points buy nothing), cost shows modest gains, and
> curtailment is the deciding axis: 16 -> 32 cut its LOO error from 17.1
> to 6.6 x floor. If 32 -> 48 cuts it by half again, 32 was not enough on
> that axis; if the curve flattens, 32 is vindicated. Tuning most likely
> helps the BO-augmented calibration (the observed 5/8 coverage), not
> the start-set GP, whose own audit is clean. Every outcome is
> publishable, and the whole experiment is re-analysis of runs we
> already own — zero new compute."

## 2026-10-15T07:32Z — pre-registrations the spec leaves to the executor
## (recorded BEFORE any fit, per §2 discipline)

1. **Part H winner-selection metric (LOOCV on the 32 starts only):**
   primary = LOO NLPD in ORIGINAL units (nats; change-of-variables term
   included for log1p configs). Ties within 0.02 nats break by LOO RMSE
   (original units, back-transformed median for log1p). One winner per
   objective. Rationale: NLPD scores both accuracy and calibration; the
   targeted question is calibration repair.
2. **LOO formula:** the campaign closed form (PredGP.loo_residuals
   convention): alpha = Kn^-1 (ty - mean(ty)); residual_i =
   alpha_i / (Kn^-1)_ii; LOO predictive variance = 1 / (Kn^-1)_ii
   (noise-inclusive, standardized transformed space). ty is standardized,
   so mean(ty) = 0; the learned constant mean is NOT substituted — this
   matches the campaign code exactly.
3. **Best-combination rule:** combine every axis level that beats the
   default on the primary metric in the main-effects pass; fit that
   combination. Interaction flag: if the combination is WORSE than the
   best single-change config, run the pairwise crosses of the beneficial
   axes (still LOOCV only) before naming the winner.
4. **16-end ribbon:** 10 random 16-subsets of the 32 starts, subset seed
   20261015 (numpy default_rng), campaign-default config only. Spread
   reported on holdout RMSE (the §3-named supplement cell) and LOO RMSE.
5. **Replay Spearman definition:** per arm, fit the three objective
   PredGPs (fit_prediction_gps), predict posterior means over the full
   9^6 lattice, min-max normalize each objective by the ARM'S OWN
   training ideal/nadir (library no-leakage convention), scalarize with
   the augmented Tchebycheff (rho = 0.05). Weights = the 8 Dirichlet
   vectors the real r1 drew (regenerated from acq_seed 20261007, same
   rule as propose_qparego_batch). Report the pairwise Spearman per
   weight vector: mean and range over the 8, for 16-32, 16-48, 32-48.
6. **Replay seed rule (derived, not guessed):** acquire_next.main sets
   torch.manual_seed(0) before any command; propose_round(k) uses
   seed = ledger acq_seed_base + k = 20261006 + 1 = 20261007 for r1
   (round_records.json r1 acq_seed = 20261007 confirms). Replay applies
   torch.manual_seed(0) before each arm's fits, then
   propose_qparego_batch(X, Y, q=8, candidates=lattice_candidates(),
   seed=20261007) under gpytorch.settings.fast_pred_var(), using
   acquire_next imported AS A LIBRARY (never its CLI).
7. **Holdout touch budget (per §2/§7):** per objective, exactly the
   campaign default and the pre-named LOOCV winner, each scored once per
   arm (16/32/48), plus the winner's E2 read at 32 (same fit, no refit),
   plus the §3 ribbon supplement (default config, 10 subsets). If the
   winner IS the default for an objective, only the default touches.
   Nothing else touches `waves/random_C`.
8. **E0 recipe:** the pi_1008 sklearn loo_preds function
   (analysis/stage2/n0_refresh_32.ipynb cell 3; identical in
   stage2_quicklook.ipynb cell 9), verbatim: per-fold min-max X scaling,
   ConstantKernel*Matern(nu=2.5, ls in [1e-2, 1e1]) + WhiteKernel(1e-4,
   [1e-6, 1]), normalize_y, n_restarts_optimizer=1, random_state=0,
   alpha=1e-8. 16/32 columns must reproduce n0_gp_loo.csv and
   n0_32pt_gp_loo.csv before the 48 column is added.

## 2026-10-15T07:38Z — §3 pre-flight asserts: ALL PASS

`preflight.py` run in env bogp (scipy 1.15.3):

- (i) qmc.Sobol(6, scramble=True, seed=20260821).random(48), affine-mapped
  to [0.05, 1.0]: all 48 pre-snap draws BIT-IDENTICAL to the recorded
  snap_map.json pre_snap rows of stage2_C_n0 (draws 1-16), stage2_C_n0b
  (17-32), methods_C_Q1 (33-48). Every draw kept (zero snap collisions).
- (ii) nearest-level snap of the regenerated draws equals each wave's
  design_matrix.csv AND its recorded post_snap, all 48 rows.
- (iii) skips read from manifests: n0 skip 0 (n_drawn_total 16), n0b skip
  16 (32), Q1 skip 32 (48). Chain is contiguous; no literals used.
- (iv) 48-point train set vs random_C holdout, keyed by lattice indices:
  48 unique keys each side, ZERO overlap.

scipy's power-of-2 UserWarning on .random(48) is expected (documented in
make_batches.build_stage2_n0 docstring), not an error.

Q1 is USABLE for the 48-arm. No stop condition.

## Fixed facts verified against the repo (cite-not-rederive check)

- stage2_C_n0 manifest sobol: seed 20260821, skip 0, n 16,
  n_drawn_total 16, scipy 1.16.3. PASS.
- stage2_C_n0b: skip 16, n_drawn_total 32, continues_wave stage2_C_n0. PASS.
- methods_C_Q1: skip 32, n_drawn_total 48, continues_waves [n0, n0b],
  generated 2026-10-12, 16 objective rows present. PASS.
- random_C: 48 rows, i.i.d. uniform lattice (prompt 34), sobol: null. PASS.
- P1 round_records r1 calibration: shed 0.031/0.325/8, curt
  0.285/0.554/8, cost 0.392/0.91/8; r3: shed 0.731/1.706/7, curt
  1.426/2.008/5, cost -0.751/0.829/8. Matches §1. PASS.
- pi_1008 LOO table (floors 3000/5000/0.5e6): shed 0.499 -> 0.402
  x floor, curt 17.072 -> 6.623, cost_ls 7.115 -> 4.279. Matches §1. PASS.
