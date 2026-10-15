# N0_EVIDENCE — is n0 = 32 a good choice? (prompt 39, 2026-10-15)

## Verdict

**n0 = 32 is not a sufficient initial design for Stage-2 GP accuracy on a
uniform holdout: E1 fails on curtailment and cost_ls (I(32→48) = 0.47 and
0.33 against the ⅓ × I(16→32) rule and the 0.25 cap), while E2
calibration at 32 passes on all three objectives (winner cov95 44/44/47
in [43, 48]) and shed is noise-limited at 32; tuning needed: no for
start-set calibration, yes for the BO-augmented GP — the Part-H winner
repairs the r3 overconfidence (curtailment cov95 5/8 → 8/8); acquisition-
replay agreement: the 32-start replay reproduces the real r1 batch 8/8,
but 16- and 48-start GPs select disjoint batches (0/8 overlap on every
pair) even though the scalarized posterior landscapes stay
rank-correlated (Spearman 0.91–0.95) — batch choice is n0-sensitive,
landscape ranking is not; BO-outcome sensitivity to n0 is prompt 37's
scope.**

Scope. This verdict covers GP prediction quality on the uniform random_C
holdout. It does not measure BO outcome quality. Accuracy at 32 is good
enough to rank designs (holdout Spearman ≥ 0.94 on every objective).
Calibration at 32 is sound. The accuracy curve still descends at 48 on
curtailment and cost, so more start points keep buying real information.

## E0 — the PI's LOO table extended to 48

Recipe: the exact pi_1008 sklearn LOO (n0_refresh_32.ipynb cell 3).
The 16 and 32 columns reproduce the recorded tables to a worst relative
deviation of 3.9e-7 before the 48 column was added. Floors: shed
3,000 MWh; curtailment 5,000 MWh; cost $0.5M (D3 provisional).

| Objective | LOO RMSE/floor 16 | 32 | 48 | LOO R² 16 | 32 | 48 |
|---|---|---|---|---|---|---|
| load_shed_mwh | 0.50 | 0.40 | 0.44 | 0.876 | 0.894 | 0.890 |
| true_curtailment_mwh | 17.07 | 6.62 | **3.03** | 0.675 | 0.940 | 0.990 |
| total_cost_less_synthetic_usd | 7.12 | 4.28 | **2.25** | 0.985 | 0.994 | 0.998 |

Supplement (no floor defined): reserve_shortfall R² 0.83 → 0.89 → 0.95;
thermal_starts R² 0.68 → 0.92 → 0.97; total_cost_raw RMSE/floor 7.24 →
2.88 → 2.31. Full table: `e0_table.csv`. Figure:
`figs/e0_loo_16_32_48.png`.

Read against the §0.1 expectation: 32 → 48 cuts the curtailment LOO
error by MORE than half again (6.62 → 3.03). By the pre-stated test,
32 was not enough on that axis. Shed is flat at ~0.4–0.5 × floor
(noise-limited). Cost halves again (4.28 → 2.25).

## The holdout curve (the stricter, new evidence layer)

Holdout = `waves/random_C`: 48 i.i.d. uniform lattice designs, zero
overlap with the 48 training designs (pre-flight assert iv), never used
for training or tuning. Metrics in original units; log1p configs scored
through back-transformed quantiles/median and change-of-variables NLPD
(formula unit-tested before any holdout call). Figure:
`figs/n0_curve_holdout.png`; full table: `holdout_results.csv`.

Holdout RMSE/floor:

| Objective | Config | n0=16 | n0=32 | n0=48 |
|---|---|---|---|---|
| shed | default | 0.755 | 0.763 | 0.590 |
| shed | winner (rbf+log1p) | 0.764 | 0.822 | 0.579 |
| curt | default | 17.37 | 9.40 | 4.98 |
| curt | winner (rbf+log1p) | 17.07 | 7.32 | 4.31 |
| cost_ls | default | 15.38 | 7.88 | 5.28 |
| cost_ls | winner (rbf) | 10.05 | 4.99 | 3.14 |

cov95/48 (band [43, 48]) by arm — default: shed 48/47/48, curt 44/45/47,
cost 48/48/48; winner: shed 44/44/44, curt 38/44/46, cost 48/47/48.
Holdout Spearman at 32: 0.94–0.99 on all objectives, both configs.

16-end ribbon (10 random 16-subsets of the 32, default config, subset
seed 20261015; a random subset of a Sobol design is NOT itself
low-discrepancy — the designed prefix arm is the anchor): holdout
RMSE/floor min–median–max: shed 0.88–1.16–1.42; curt 15.0–20.5–30.8;
cost 8.4–16.1–18.7. The designed 16-prefix sits at or below the ribbon
median on every objective.

## Pre-registered criteria (constants ⅓ / 0.25 / 0.05 / 0.10 are
## conventions fixed in the spec before any fit)

**E1 — diminishing returns: FAIL** (default config; winner agrees).
- shed: PASS by the noise-limited escape (32-pt LOO 0.40 ≤ 1 × floor).
  Raw holdout deltas are sub-floor at every step (|ΔRMSE| < 3,000 MWh
  from 16→32 and 32→48), so I counts 0 throughout.
- curtailment: I(16→32) = 0.459, I(32→48) = 0.470 > ⅓ × 0.459 = 0.153
  and > 0.25. FAIL — the curve has not bent.
- cost_ls: I(16→32) = 0.488, I(32→48) = 0.331 > 0.163 and > 0.25. FAIL.
- Overall: 1 of 3 pass and the 0.25 cap is violated → E1 FAILS. The
  data say: at 48 the returns are not yet diminishing on 2 of 3 axes.

**E2 — calibration at 32: PASS** (judged on the pre-named winner;
default alongside, no post-hoc swap). Winner cov95: shed 44, curt 44,
cost 47 — all three inside [43, 48] → joint rule passes. Default: 47,
45, 48 — also passes. Caveat: holdout hits share hyperparameters, so
the binomial band is approximate.

**E3 — tuning verdict: tuning helps, calibration never needed it at 32.**
At n0 = 32, winner vs default: ΔNLPD = −0.41 (shed), −0.24 (curt),
−0.48 (cost) nats — all improve; cov95 stays in band (no degradation by
the pre-registered test). Winner's-curse check (LOOCV → holdout at 32):
curt 4.79 → 7.32 × floor, shed 0.58 → 0.82, cost 7.21 → 4.99 — the LOO
advantage shrinks but does not vanish.

**H-BO cell — where the pathology lives.** Both configs refit on the
BO-augmented set (32 + bo_C_r1 + bo_C_r2, n = 48), scored on the 8
BO-selected `methods_C_P1_r3` designs (mean_z / rms_z / cov95):

| Objective | default | winner |
|---|---|---|
| shed | 0.731 / 1.706 / 7-8 | 0.133 / 0.280 / 8-8 |
| curt | 1.426 / 2.008 / 5-8 | 0.967 / 1.050 / 8-8 |
| cost_ls | −0.751 / 0.829 / 8-8 | −0.946 / 1.059 / 8-8 |

The default cell reproduces the recorded r3 audit EXACTLY — the
replication is faithful. **Answer to the targeted question: yes.
rbf+log1p restores curtailment coverage (5/8 → 8/8) and brings rms_z
from 2.008 to 1.050.** The start-set GP's own LOO calibration was never
broken (curt rms_z 0.81, cov 31/32, band [28, 32]); the repair matters
where the pathology was observed — after BO rounds enter training.

## Part H — hyperparameter study (LOOCV on the 32 starts; ledger
## `fits.json`, grid results `part_h_loocv.csv`)

Selection rule (pre-registered before fitting): LOO NLPD in original
units; ties within 0.02 nats break by LOO RMSE. Winners committed to
`fits.json` at 2026-10-15T07:34:02+00:00, before the first holdout call.

- shed: winner **rbf+log1p** (NLPD 8.61 vs default 9.24).
- curtailment: winner **rbf+log1p** (NLPD 11.11 vs 11.88; LOO RMSE
  4.79 vs 8.12 × floor).
- cost_ls: winner **rbf** (NLPD 16.24 vs 16.53; log1p not in the grid
  for cost per §2).
- The BoTorch Gamma(3, 6) lengthscale prior hurts badly on every
  objective (curt 27 × floor) — the bo-gp default (no prior) is right
  for this problem. Fixed-at-floor noise changes little. Matérn 3/2
  never beats 5/2. No axis interaction was triggered (each combo beat
  every single change).

## Acquisition replay (descriptive; `refit_r1.py`, library import only)

Seed rule derived from `acquire_next.py`: torch.manual_seed(0) at entry;
proposal seed = acq_seed_base + round = 20261006 + 1 = 20261007
(round_records r1 confirms). Record-only q-ParEGO r1 batches proposed
from the 16-, 32- and 48-start GPs over the full 9^6 lattice.

Results (`replay_r1.json`):

- Overlap with the frozen `waves/bo_C_r1` batch: 16-start 0/8;
  **32-start 8/8** (the replay reproduces the deployed round-1 batch
  exactly, on local hardware); 48-start 0/8.
- Pairwise batch overlap between arms: 16–32 0/8, 16–48 0/8, 32–48 0/8.
- Spearman of the scalarized posterior mean over all 531,441 lattice
  points (augmented Tchebycheff, the 8 real r1 weight vectors;
  mean [min, max]): 16–32 0.942 [0.912, 0.987]; 16–48 0.907
  [0.892, 0.932]; 32–48 0.947 [0.895, 0.991].

Read: the GPs agree on the global landscape ranking at every n0
(ρ ≥ 0.89 on every weight), but the EI argmax is a knife-edge — a
different start set moves every batch member. The decision-relevant
message: n0 changes WHICH points BO probes next, even when it barely
changes the fitted landscape. Only prompt 37's outcome study can say
whether those different probes change the final front.

## Shed supplement (pre-registered; Gaussian GP is misspecified at the
## floor plateau)

The holdout has 4 exact zeros, a repeated 22.4 MWh plateau and 22/48
rows below the 3,000 MWh floor. (a) RMSE restricted to the 26 rows
above the floor (default / winner, MWh): 16: 2,845 / 3,066; 32:
2,985 / 3,264; 48: 2,203 / 2,248. (b) Floor-exceedance classification
accuracy: default 0.96 / 0.96 / 0.94; winner 0.73 / 0.85 / 0.96.
Do not interpret sub-floor differences.

## Disclosure (required)

The random pool's summary statistics were published (RANDOM_BASELINE.md,
PI decks) before these thresholds were frozen, and prompt 35 reuses the
same pool for HV percentiles — correlated evidence across the paper's
claims; no GP was ever trained or tuned on the pool.

## Paper-ready paragraph (STE-100)

We test the initial-design size with data we already own. We train the
Stage-2 surrogate on nested Sobol designs of 16, 32 and 48 points. We
score each model once on a held-out pool of 48 uniform random designs.
The pool never trains or tunes any model. Load-shed error stays below
the simulator noise floor at 32 points. Curtailment error falls from
17.4 to 9.4 to 5.0 times the noise floor as the design grows; cost
error falls from 15.4 to 7.9 to 5.3. The error curve does not flatten
at 32 on these two objectives, so 32 points do not exhaust the value of
space-filling data. Calibration at 32 is sound: 95 % intervals cover
44–48 of 48 holdout points for all objectives. A pre-registered
hyperparameter study selects an RBF kernel with a log1p output
transform by leave-one-out likelihood. The tuned model repairs the
over-confidence that appears after BO points enter training: coverage
on the round-3 audit points rises from 5/8 to 8/8. Rank quality is
high at every size (holdout Spearman ≥ 0.94 at 32). A replay of the
first acquisition round shows the same split: the 32-point model
reproduces the deployed batch exactly, but the 16-point and 48-point
models each select a fully different batch (0/8 overlap), while the
scalarized posterior landscapes stay rank-correlated (Spearman
0.91–0.95). Warning: these results measure surrogate quality, not BO
outcomes. Prompt 37 owns the BO-outcome question.

## Summary block for the strategy session (living report + 1014-D1)

- **E0 extended:** curt LOO 17.1 → 6.6 → 3.0 × floor, cost 7.1 → 4.3 →
  2.3 (16/32/48); shed flat at 0.4–0.5. The PI's 16/32 columns
  reproduced to 4e-7 first.
- **Holdout (new, stricter):** same shape. E1 diminishing-returns FAILS
  on curt (I(32→48) = 0.47) and cost (0.33); shed passes by the
  noise-limited escape. E2 calibration at 32 PASSES on all three
  (winner 44/44/47 in [43, 48]). Spearman ≥ 0.94 at 32.
- **Tuning (Part H):** winners rbf+log1p (shed, curt), rbf (cost);
  NLPD improves ~0.2–0.5 nats; the Gamma lengthscale prior is harmful.
  H-BO cell: tuning REPAIRS the r3 overconfidence (curt 5/8 → 8/8,
  rms_z 2.008 → 1.05); the default cell reproduced the r3 audit exactly.
- **Replay:** 32-start reproduces the real r1 batch 8/8; 16/48 pick
  disjoint batches (0/8 everywhere) with landscape Spearman 0.91–0.95.
- **1014-D1 scoping (does the seed study keep n0 = 32?):** for GP
  quality alone, 32 is defensible on ranking + calibration but leaves
  ~2 × accuracy on the table on curt/cost vs 48. The seed study should
  keep n0 = 32 for comparability with the live campaign, cite this
  curve as the known accuracy cost, and consider the rbf+log1p
  prediction-layer tuning for BO-augmented rounds (acquisition layer
  untouched). Zero new compute was spent here.

## Files

- `PROGRESS.md` — execution log with the §3 pre-flight asserts.
- `fits.json` — every fit: config, LOOCV metrics, hyperparameters;
  winner commitment timestamp.
- `part_h_loocv.csv`, `holdout_results.csv`, `arm_loo_flexgp.csv`,
  `ribbon.csv`, `e0_table.csv`, `criteria.json`, `hbo_cell.json`,
  `replay_r1.json`, `holdout_z.json`.
- Figures (PNG + PDF): `figs/n0_curve_holdout`, `figs/e0_loo_16_32_48`,
  `figs/z_hist_32`.
