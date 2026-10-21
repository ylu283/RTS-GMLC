# Shed GP under the provisional floor (prompt 42): STOPPED, Kay's decision needed

Status 2026-10-21. **PROVISIONAL / DIAGNOSTIC. Stopped under §4** ("stop and
report if fits fail to converge"). The sweep ran in full with the house fit.
No figures were drawn, and no route was declared final.

## 1. Why I stopped

The house GP fit (`bogp.train_gp`: 700 Adam steps, lr 0.01, called by
`common.FlexGP`) does **not converge the noise hyperparameter**. I checked
this on training data only (n0 = 32, shed), with no holdout scoring.

| config | floor | learned noise at 700 steps | loss change, last 100 steps | learned noise at 5,000 steps | loss change, last 100 steps |
|---|---|---|---|---|---|
| default (m52+std) | 180 | 364 | 2.1e-2 | **185** | 7e-4 |
| default | 306 | 441 | 2.1e-2 | **309** | 7e-4 |
| default | 880 | 940 | 2.2e-2 | **881** | 1e-3 |
| default | 3,000 | 3,040 | 8.8e-3 | **3,001** | 3e-4 |
| rbf+log1p | 180 | 438 | 3.4e-2 | **216** | 9e-4 |
| rbf+log1p | 306 | 510 | 3.3e-2 | **308** | 8e-4 |
| rbf+log1p | 880 | 1,006 | 2.5e-2 | **881** | 7e-4 |
| rbf+log1p | 3,000 | 3,064 | 1.3e-2 | **3,001** | 4e-4 |

Noise is in raw MWh; log1p is mapped with the delta method.

- At 700 steps the loss still falls by about 0.02 per 100 steps.
- The noise parameter is `floor + softplus(raw)`, and raw has moved only
  from 0 to about −5. With lr 0.01, 700 steps cannot reach the optimum.
- The learned noise tracks √(f² + 333²) because the excess above the bound
  is the unfinished descent, not a likelihood optimum.
- With 5,000 steps the noise **goes onto the bound at every floor**. So at
  convergence the bound is ACTIVE everywhere, and the likelihood wants a
  shed noise below 180 MWh.

Consequences:

1. **The prompt's degeneracy premise is wrong.** It says that at floor 180
   the learned noise of 360–440 MWh sits above the bound, so the 180 and 306
   fits are identical. That came from the truncated optimizer. The fits
   differ at every floor; the sweep shows it.
2. **The pinned ACTIVE flag (noise ≤ 1.001 × floor_var) read INACTIVE on all
   63 fits**, even at floor 3,000 where the learned noise is 1–3 % above the
   bound. The flag is context only, so the route does not change. Under
   converged fitting it would read ACTIVE everywhere.
3. **Every frozen campaign GP uses the same 700-step fit:**
   acquire_next PredGP, the prompt 39 Part-H and holdout tables, and the
   ledgers' proposals. The sweep reproduces the frozen holdout rows exactly.
   At floor 3,000, n0 = 16, the default gives RMSE 2,264.24 / cov95 48 and
   the winner 2,292.26 / 44, the same as `holdout_results.csv`. So the
   sweep is consistent with the campaign. But "floor-dependence" in it is
   partly optimizer-budget dependence.

## 2. Sweep result with the house fit (complete, NOT final)

- **LOO winner: rbf+log1p at every floor.** No winner flip, and no tie
  within 0.02 nats at any floor.
- **F_pass = ∅ → route (ii) under the house fit.**

Joint bar per floor (✓ = criterion met at all three n0):

| floor | winner rbf+log1p: cov95 / RMSE (a) / RMSE (b) / latent ratio | default m52+std: cov95 / (a) / (b) / ratio |
|---|---|---|
| 180 | ✗ (41/40/44) / ✗ / ✗ / ✓ | ✓ / ✓ / ✗ / ✓ → **passes** |
| 306 | ✗ (41/41/44) / ✗ / ✗ / ✓ | ✓ / ✓ / ✗ / ✓ → **passes** |
| 500 | ✗ (41/42/44) / ✗ / ✗ / ✓ | ✓ / ✓ / ✗ / ✓ → **passes** |
| 880 | ✗ (41/43/44) / ✗ / ✗ / ✓ | ✓ / ✓ / ✗ / ✓ → **passes** |
| 1,500 | ✓ / ✗ / ✗ / ✓ | ✓ / ✓ / ✗ / ✗ (1.95) |
| 1,800 | ✓ / ✗ / ✗ / ✓ | ✓ / ✗ / ✗ / ✗ |
| 3,000 | ✓ / ✗ / ✓ / ✗ | ✓ / ✗ / ✓ / ✗ |

The incumbent arm equals the winner arm at every floor (same config).

- **Winner fails on:**
  - cov95: under-coverage at floors ≤ 880, 40–42 of 48 at n0 = 16 and 32;
  - RMSE: it does not fall with n0 (2,744 → 2,791 → 2,339 at floor 180);
  - the latent-sd ratio, at floor 3,000 (1.86 at n0 = 16).
- **Default (m52+std) meets the full bar at every floor in [180, 880]**:
  - cov95 45 / 45 / 48;
  - RMSE 1,745 → 1,482 → 972 at floor 180 (clause a);
  - latent ratio 2.9–4.4.
- The default is not the LOO winner, so by the pinned F_pass rule it does
  not count.
- Bar width (recorded, not a criterion), median raw half-width at n0 = 32:
  default 2,508 (floor 180) → 7,012 MWh (3,000); winner 3,958 → 23,293 MWh.

Full rows: `provisional_sweep.csv`, `joint_bar.csv`, `loo_reselection.csv`,
`provisional_summary.json`.

## 3. Decision needed (Kay)

The route depends on whether the GP is fitted to convergence. Choose one:

- **A. Keep the house 700-step fit as the campaign's GP definition.**
  - Route (ii) stands as computed: Phase-B opens.
  - Disclose that the noise hyperparameter is budget-limited.
  - The default-arm pass inside [180, 880] is a sensitivity finding that
    Phase-B should start from.
- **B. Converge the fits, then rerun the sweep** (recommended).
  - Pin, for example, 5,000 Adam steps (or a loss-change stop rule) for
    THIS diagnostic only. About 10 min locally.
  - Same 7 × 3 × 3 design; this re-scores the holdout (see the exposure
    count below).
  - Under convergence the noise sits on the bound, so the floor fully
    controls the bars. This is the object the floor question is about.
  - It needs an explicit amendment, because it leaves the frozen campaign
    GP definition for this study.
- **C. Fix the training budget campaign-wide.** This touches `bogp` or
  `common.py`, all frozen tables, and every ledger proposal's provenance.
  It is out of scope here and is a strategy decision.

My recommendation is **B**, with A's route (ii) reported alongside as the
house-fit sensitivity.

## 4. Holdout exposure (disclosed)

- This sweep: **42 distinct shed holdout scorings** on `random_C`
  (21 distinct floor-config pairs × 3 n0; repeated arms were scored once).
- Before this: prompt 39 had 6 (default + winner × 3 n0) plus 10 ribbon
  subsets. Prompt 40 had 0 (Part B skipped).
- Cumulative shed exposure: **58**.
- If B runs, add 42.
- Holdout retirement after the measured-floor scoring stands (§3
  pre-commitment).

## 5. Honesty block

- No floor value was selected from holdout performance.
- The route (i)/(ii)/(iii) is a pre-registered branch and selects no
  reported number.
- The convergence check used training data only.
- No frozen file was touched: `common.FLOORS` was mutated in place and
  restored (asserted), and `train_gp` was swapped only inside the check
  script, then restored.
