# Shed GP under the provisional floor (prompt 42 + Amendment 1): route (iii)

Status 2026-10-21. **PROVISIONAL / DIAGNOSTIC.** The study ran twice. The
first run used the house 700-step fit; it stopped under §4 and asked for a
decision (§3 below, kept as the record). Kay approved option B
(Amendment 1). The converged rerun is the PRIMARY answer. The house-fit
sweep stands as the campaign-definition sensitivity.

**Declared route: (iii) — F_pass = {3,000}; passes only above 880 MWh.**
No floor inside the CI band [180, 880] passes, and the grid is not empty.
Per the pre-registration: wait for the prompt 41 measurement; do not open
Phase-B yet. The pass at 3,000 holds with RMSE clause a+b, so it is NOT
flagged WEAK.

## 1. PRIMARY — Amendment 1, converged fits (5,000 Adam steps)

Fit, pinned for this diagnostic only: 5,000 Adam steps, lr 0.01,
`torch.manual_seed(0)` per fit; only the step count differs from the house
definition. Rule: a fit that still moves more than 2e-3 over its last 100
steps extends to 10,000 steps. **No fit needed the extension** (94 fits:
49 LOO, 45 holdout; max final 100-step loss change 1.8e-3, median far
lower; `convergence_log_converged.csv`). Pre-run check passed: default at
floor 306 reproduced the convergence check (learned noise 309.4 MWh).

### 1.1 LOO winner path (selection under the same converged fitting)

- Floors 180–1,800: **rbf+log1p**, no tie invoked at any of the six.
- Floor 3,000: **tie invoked, winner flips to log1p (m52+log1p).**
  rbf+log1p has the NLPD argmin (8.505 vs 8.523, gap 0.018 < 0.02 nats);
  log1p wins on the pinned LOO-RMSE tie-break (1,520 vs 1,716).
  Winner instability across floors is a recorded finding, not a stop.

### 1.2 Joint bar per floor (✓ = met at all three n0)

| floor | winner arm: cov95 / RMSE(a) / RMSE(b) / ratio → pass | default arm (sensitivity) |
|---|---|---|
| 180 | rbf+log1p: ✗ (39/33/44) / ✗ / ✗ / ✓ → fail | ✗ (43/38/45) / ✓ / ✗ / ✓ → fail |
| 306 | rbf+log1p: ✗ (39/33/44) / ✗ / ✗ / ✓ → fail | ✗ (43/39/45) / ✓ / ✗ / ✓ → fail |
| 500 | rbf+log1p: ✗ (39/37/44) / ✓ / ✗ / ✓ → fail | ✓ (43/43/45) / ✓ / ✗ / ✓ → **passes (a)** |
| 880 | rbf+log1p: ✗ (40/41/44) / ✓ / ✗ / ✓ → fail | ✓ (45/46/47) / ✓ / ✗ / ✓ → **passes (a)** |
| 1,500 | rbf+log1p: ✗ (42/42/44) / ✓ / ✗ / ✓ → fail | ✓ (48/48/48) / ✓ / ✗ / ✓ → **passes (a)** |
| 1,800 | rbf+log1p: ✓ (43/43/44) / ✗ / ✗ / ✓ → fail | ✓ / ✓ / ✓ / ✓ → **passes (a+b)** |
| 3,000 | **log1p: ✓ (44/44/44) / ✓ / ✓ / ✓ → PASSES (a+b)** | ✓ / ✓ / ✓ / ✗ (1.86–2.14) → fail |

The incumbent arm (rbf+log1p) equals the winner arm at floors ≤ 1,800. At
3,000 the incumbent also passes, but only through clause (b) (cov95
44/44/44; RMSE does not fall with n0: 1,968 → 2,123 → 1,523).

**F_pass = {3,000} → route (iii).** The winner's pass at 3,000 uses clause
a+b (RMSE 1,946 → 1,879 → 1,258, all ≤ 3,000), so the WEAK flag does not
apply.

### 1.3 Answers to the amendment's pre-stated open questions

- **Did rbf+log1p's holdout coverage recover at low floors? No — it got
  worse.** House fit at floor 306: cov95 41/41/44. Converged: 39/33/44.
  At convergence the noise sits on (0.1–3 % above) the bound, the bands
  narrow (median half-width at n0 = 32 drops from 3,958 to 1,747 MWh at
  floor 306), and the under-coverage deepens.
- **Did the default's full-bar pass inside [180, 880] survive? Only
  partly.** It survives at 500 and 880 (and extends to 1,500 and 1,800).
  It dies at 180 and 306: cov95 falls to 38–39 at n0 = 32 (house fit: 45).
  The house-fit "pass at every floor in [180, 880]" was in part an
  artifact of the truncated optimizer's inflated noise.
- **Does the noise rail on the bound everywhere? Mostly, with one real
  exception.** At n0 = 16 and 32 the learned noise tracks the floor to
  within 0.1–3 % at every floor (182 → 307 → 501 → 881 → 1,501 → 1,801 →
  3,001 MWh for the default at n0 = 16): the floor genuinely controls the
  bars. The pinned ACTIVE flag (≤ 1.001 × floor_var) still reads INACTIVE
  below 1,500–1,800 because the softplus parameterization approaches the
  bound asymptotically; treat the flag as context, as pinned. The real
  exception is n0 = 48: there the likelihood wants noise ≈ 650 MWh
  (default) and ≈ 1,630 MWh (rbf+log1p) — genuinely above the low floors,
  so the n0 = 48 fits are floor-invariant across 180–500 (identical RMSE
  965.9 / 2,202). No pass propagates through the inactive-floor rule: the
  winner arm passes only at 3,000, where the bound is ACTIVE at all n0.
- **Did rbf+log1p keep winning the LOO? Yes at 180–1,800; no at 3,000**
  (§1.1). The LOO flip at 3,000 is itself converged-fit behavior: under
  the house fit rbf+log1p won at 3,000 with no tie.

### 1.4 Bar width (recorded, not a criterion)

Median raw half-width of the 95 % band at n0 = 32: default 1,645 (floor
180) → 6,680 MWh (3,000); winner arm 1,661 (floor 180, rbf+log1p) →
19,969 MWh (3,000, log1p). The converged bands are 30–60 % narrower than
the house-fit bands at low floors (house: default 2,508, winner 3,958 at
floor 306 and n0 = 32). Calibrated-but-wide remains the PI's call.

### 1.5 What route (iii) means here

A floor near the campaign value 3,000 MWh fixes the bars with the log1p
transform; no floor in the plausible measured band [180, 880] does, for
any arm that the LOO selects. If prompt 41 measures a floor inside
[180, 880], the model itself (transform / heteroscedastic noise / hurdle)
is the problem there and Phase-B opens at the measured floor. If the
measurement lands high (prompt 40's √p90 was 1,505; the high-shed hint
1,775), the default arm's clause-a passes at 1,500–1,800 and the winner
pass at 3,000 say the existing model family may suffice. Wait for the
measurement.

Files: `provisional_sweep_converged.csv`, `joint_bar_converged.csv`,
`loo_reselection_converged.csv`, `provisional_summary_converged.json`,
`convergence_log_converged.csv`, `predictions_converged.csv`.
Figures (converged sweep, PROVISIONAL watermark, assert-before-draw):
`fig1_criteria_vs_floor_converged.png/.pdf`,
`fig2_parity_306_converged.png/.pdf` (winner rbf+log1p at 306; joint bar
not met — shown as measured),
`fig3_parity_3000_vs_306_converged.png/.pdf` (n0 = 32; CI text printed on
the figure).

## 2. SENSITIVITY — house 700-step fit (campaign GP definition)

Kept from the first run; superseded as the primary answer, retained
because every frozen campaign table uses this fit definition.

### 2.1 Why the first run stopped

The house GP fit (`bogp.train_gp`: 700 Adam steps, lr 0.01, called by
`common.FlexGP`) does **not converge the noise hyperparameter**. Checked
on training data only (n0 = 32, shed), no holdout scoring:

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

Noise in raw MWh; log1p mapped with the delta method. At 700 steps the
loss still falls about 0.02 per 100 steps; the learned noise tracks
√(f² + 333²) because the excess above the bound is unfinished descent.
Consequences, confirmed: the prompt's "identical fits at 180/306" premise
was an optimizer artifact; the pinned ACTIVE flag read INACTIVE on all 63
house fits; every frozen campaign GP (acquire_next PredGP, the Part-H and
holdout tables, the ledgers' proposals) uses this same 700-step fit — the
house sweep reproduces the frozen holdout rows exactly, so it is
consistent with the campaign, but its "floor-dependence" is partly
optimizer-budget dependence.

### 2.2 House-fit sweep result

- LOO winner: rbf+log1p at every floor, no ties.
- **F_pass = ∅ → route (ii) under the house fit.**
- The winner failed on cov95 at floors ≤ 880 (40–42 of 48 at n0 = 16 and
  32), on RMSE monotonicity, and on the latent ratio at 3,000.
- The default met the full bar at every floor in [180, 880] (cov95
  45/45/48; RMSE clause a; ratio 2.9–4.4) but was not the LOO winner.
- Bar width at n0 = 32: default 2,508 → 7,012 MWh; winner 3,958 → 23,293.

Full rows: `provisional_sweep.csv`, `joint_bar.csv`,
`loo_reselection.csv`, `provisional_summary.json`.

**Side-by-side disclosure:** the campaign definition (700 steps) routes
to (ii); the converged definition routes to (iii). The disagreement is
itself a finding: the route is sensitive to the optimizer budget, and the
converged fit is the object the floor question is about (Amendment 1).
Route (iii) is declared on the converged (primary) sweep.

## 3. Decision record (first run; resolved)

The first run stopped and offered Kay three options: A — keep the house
fit, route (ii) stands; B — converge the fits and rerun (recommended);
C — fix the budget campaign-wide (out of scope, strategy). **Kay chose B
(2026-10-21); Amendment 1 pins its terms.** Option A's result is kept in
§2 as sensitivity. Option C remains a strategy-session question; nothing
campaign-side was touched.

## 4. Holdout exposure (disclosed)

- House sweep: 42 distinct shed holdout scorings on `random_C`.
- Converged rerun: **45 distinct scorings** — the pre-registered estimate
  was +42 (same set as the house sweep), but the LOO winner flip at floor
  3,000 added the (3,000, log1p) config at three n0. The +3 follows from
  the pinned per-floor-winner design, not from a scoring choice.
- Before this prompt: 58 (prompt 39: 6 + 10 ribbon subsets; prompt 40: 0;
  house sweep: 42 of the 100 total). **Cumulative shed exposure:
  58 + 45 = 103** (the amendment's stated "cumulative 100" assumed no
  winner flip).
- Retirement pre-commitment stands: one more shed scoring at the measured
  floor, then the 48-design holdout is retired for shed model selection;
  Phase-B (if it opens) selects on LOO/training data only.

## 5. Honesty block

- No floor value was selected from holdout performance. The route
  (i)/(ii)/(iii) is a pre-registered branch and selects no reported
  number.
- The converged-fit definition (5,000 steps) was pre-registered in
  Amendment 1 BEFORE the rerun; the extension rule (10,000 steps) was
  never triggered. Selection (LOO) and scoring share the fit definition.
- The campaign GP definition is untouched everywhere else; `train_gp` was
  swapped inside the sweep scripts only and restored (asserted).
  `common.FLOORS` was mutated in place and restored (asserted). No frozen
  file was touched.
- The holdout was re-scored for this rerun (+45; §4). Both sweeps' routes
  are reported side by side; the primary/sensitivity split was fixed by
  Amendment 1 before the rerun produced numbers.
- The ACTIVE-flag threshold (1.001) under-reads bound activity for
  converged softplus fits (§1.3); it was used as context only, as pinned.
- Figures assert every annotation against the `_converged` CSVs before
  drawing; the parity figures redraw saved predictions
  (`predictions_converged.csv`), not refits.
