# BO_STAGE2.md — Stage-2 BO campaign, scenario C (prompt 30 T2, 2026-10-10)

**Status: BO_DONE: the stopping rule fired after round 2** (gains 3.63e16 and
9.18e15, both under the pre-registered threshold 5.263e16). 48 designs were
evaluated: 32 Sobol starting points plus 2 q-ParEGO rounds of 8. Evidence:
`bo_stage2_report.ipynb` (executed). Tables: `front_designs.csv`,
`hv_counterfactual.csv`, `calibration.csv`, `edge_summary.csv`,
`t2_summary.json`. Figures: `figs/fig1–4_*.{png,pdf}`.
M = {load_shed_mwh, true_curtailment_mwh, total_cost_less_synthetic_usd},
all minimized. ρ = 2.0, B = 40. bo-gp `feat/qparego` @ `60e6328`.

> **g1 caveat:** every absolute cost below is *pending the PI's g1
> ruling*. Inside the Stage-2 box nuclear ω ≥ 0.05, so option (c) adds the
> same +$28.188M to every design. Fronts, knees and rankings are
> unaffected. Re-level the absolute costs when the PI rules.

## Audit — round 2 re-verified locally end-to-end (§1 of the notebook)

| Check | Result |
|---|---|
| Ledger HV entries 0/1/2, recomputed with the read-back ref | match, rel. diff 0.0 |
| Gains, stop decision, n_outside_ref [0, 2, 5] | match |
| Calibration z-stats from `predictions.csv` ⋈ `objectives.csv` | identical to `round_records.json` (r1, r2) |
| r2 manifest: bo_gp_sha, acq_seed 20261008, 8×3 weights | match round record |
| **r2 acquisition re-run locally** (same 40 points, seed 20261008, full 9⁶ lattice) | **weights identical; designs 8/8 identical** to what CRC proposed (384 s on the Mac) |

The unattended brain did exactly what the frozen configuration says.

## (1) Final front, knee candidates, designs

The 3-objective front of the 48 points has **26 designs: 13 from the
starts, 6 from r1 and 7 from r2**. BO points pushed 2 of the 15 starting
front points (n0b#1, n0b#9) off the front. Figure: `figs/fig1_front.png`.
The full table, with ω and MW per tier, is `front_designs.csv`.

**Knee candidates** are the designs with the smallest Euclidean distance to
the utopia point, after normalizing the front to [0, 1]³:

| Knee | Source | nuclear | pv | tail | wind_122 | wind_303 | wind_317 | total MW | shed [MWh] | curt [MWh] | cost_ls [$M]* |
|---|---|---|---|---|---|---|---|---|---|---|---|
| n0b#8 | start | 0.05 (20) | 0.05 (17) | 0.763 (192) | 0.169 (120) | 0.763 (646) | 0.881 (704) | 1,699 | 1,307 | 326,405 | 563.1 |
| r1#2 | BO r1 | 0.05 (20) | 0.288 (98) | 0.881 (222) | 0.288 (205) | 0.763 (646) | 0.644 (514) | 1,705 | 836 | 283,799 | 568.2 |
| r1#6 | BO r1 | 0.05 (20) | 0.525 (179) | 0.525 (132) | 0.169 (120) | 0.644 (545) | 0.763 (609) | 1,606 | 3,654 | 270,112 | 566.0 |

Each cell is ω (MW). *Costs are g1-pending. The three knees share one
shape: nuclear at its 0.05 floor, about 1.6–1.7 GW in total, with most of
it on wind_303/wind_317, and wind_122 kept low.

**Knee robustness (review addition):** the knee identity is sensitive to
the normalization span — the 5 outside-ref extremes stretch it. On the
front clipped to the fixed ref box (21 designs) the three smallest utopia
distances are r2#1, r1#2, r2#6; only **r1#2 is a knee under both
normalizations**. What IS robust is the recipe: every knee in either set
has nuclear at 0.05 and 1.6–2.0 GW total, wind-loaded. Quote the recipe,
not a single design. The best single-objective
designs sit at the corners of the front:

| Best in | Design |
|---|---|
| Shed | FOUR designs tie at exactly zero shed; the cheapest is **r2#6 at $582M** (curt 235 GWh), and r1#5 pairs zero shed with the lowest curtailment (48 GWh) at $668M |
| Curtailment | r1#5: 48 GWh, cost $668M (nuclear ω = 1.0) |
| Cost | r2#3: $510M. Every tier is at 0.05 except tail at 1.0, at the price of 29 GWh shed and 1.26 TWh curtailed |

## (2) HV trajectory, the counterfactual and Stage-1 context

The realized hypervolume is HV₀ = 6.606e17 at n = 32, 6.969e17 at n = 40
(**+5.5 %**) and 7.061e17 at n = 48 (**+1.4 %**). The threshold is 8.0 % of
HV₀ — **pre-declared conservative** (prompt 30: "the threshold is
shed-floor-dominated and deliberately conservative — an early stop is the
rule working, not a bug"). Sensitivity, one line: any threshold below
5.5 %/round means r1 would not have counted as low and round 3 would have
run. The stop certifies "gains below a deliberately conservative noise
bar", never "front converged". Figure: `figs/fig2_hv_trajectory.png`.

The **counterfactual is model-based** (labeled as such). The floored
prediction GPs are fit on the 32 starting points only. In each of 400
replicates, 16 random unseen lattice designs get objectives drawn jointly
from that posterior. BO's actual 16 picks are scored the same way.

| n | Realized | Random picks (model), p10 / p50 / p90 | BO's picks (model), p50 |
|---|---|---|---|
| 40 | 1.055 | 1.018 / 1.096 / 1.219 | 1.158 |
| 48 | 1.069 | 1.065 / 1.169 / 1.346 | 1.266 |

All values are HV / HV₀.

- **Inside the model world,** BO's picks beat random picks in about 70 % of
  draws. The acquisition did choose designs the model rated as better.
- **In reality,** the trajectory sits at the 30th (n = 40) and 11th (n = 48)
  percentile of the model's random-pick distribution. The 32-point model was
  optimistic about both BO and random picks.
- Real random baseline: see `../random_baseline/RANDOM_BASELINE.md` (prompt 34).

**Why the realized gain is small (report-only, §3b):** 5 of the 16 BO
evaluations fall **outside the fixed HV reference box**, and all 5 are on
the final front.

| Designs | Exceeds the ref on |
|---|---|
| r1#5, r1#7, r2#2: zero or near-zero shed, curtailment ≤ 58.4 GWh | cost > $652M |
| r2#3, r2#5: cheapest designs | curtailment (r2#3 also on shed) |

These points add no hypervolume by construction. The acquisition
normalizes over the queried min–max, so it chases front extremes the ref box
cannot credit — a mechanical contributor: 5 of 16 evaluations earn zero HV
no matter how good they are. It is NOT the main reason the gains are small:
with a wider box (nadir of all 48 plus 10 %, report-only, threshold not
recomputed) the gains are 2.6 % and 2.0 % of the corresponding HV₀ —
crediting the extremes raises r2's measured gain (1.4 → 2.0 %) but leaves
both rounds far below any plausible bar. The dominant explanation is the
dense-front regime itself (26 of 48 points non-dominated; see the Stage-1
context below): a round of 8 genuinely adds a few percent here. **The stop
is not an artifact of the box**, and the pinned ref and stop decision stand
as pre-registered.

**Stage-1 replay context** (`bo_replay/REPLAY.md` §3–4): on the 2-D,
81-cell scenario-C contour, q-ParEGO went 0.813 → 0.899 → 0.941 over two
rounds, against 0.807 → 0.885 → 0.923 for random. BO led, but only by a
small margin at C, because most cells were non-dominated and HV behaved
like a coverage count. Stage 2 repeats that picture in 6-D: the space is
large, the front is dense (26 of 48 points), and per-round gains are a few
percent.

## (3) Calibration verdict (pinned statistic)

The rule: "calibrated" requires pooled RMS(z) ∈ [0.7, 1.3] **and** pooled
95 % coverage ≥ 80 %. Figure: `figs/fig3_calibration.png`.

| Objective | r1 RMS(z) | r2 RMS(z) | Pooled RMS(z) | Pooled cov95 | Verdict |
|---|---|---|---|---|---|
| load_shed_mwh | 0.33 | 1.88 | **1.35** | 15/16 (94 %) | **not calibrated** (pooled value is a cancellation — see below) |
| true_curtailment_mwh | 0.55 | 2.49 | **1.80** | 14/16 (88 %) | **not calibrated** |
| total_cost_less_synthetic_usd | 0.91 | 1.01 | **0.96** | 16/16 (100 %) | calibrated |

**Verdict: the prediction GPs are calibrated for cost and not for shed or
curtailment.**

- Pre-registration note: calibration was REPORT-ONLY and never gated
  continuation — the in-flight "continue" decisions were HV-threshold-only
  (prompt 30 pins the pooled statistic to T2). No in-flight gate was
  violated.
- Read the per-round rows, not the pooled row: for shed and curtailment the
  GPs were outside the band in BOTH rounds — too wide in r1 (RMS 0.33/0.55,
  below the 0.7 edge: by the verdict's own band r1 alone would also fail,
  in the opposite direction), overconfident at corners in r2 (1.88/2.49).
  The pooled shed RMS of 1.35 is two opposite failures partially
  cancelling, not a near-pass.
- Coverage passes for all three objectives. The failure is RMS, and it
  comes from r2.
- The r2 misses are concentrated at the **lattice corners** BO moved into.
  r2#3 (every tier at 0.05 except tail) realized shed of 29.2k against about
  8.5k predicted, and curtailment of 1.26 TWh against 0.77 TWh predicted.
  r2#5 missed the same way.
- This is extrapolation from a 40-point Sobol-plus-r1 design that has few
  corner points. Treat corner predictions for shed and curtailment as
  under-dispersed. Candidate fixes for any restart: corner points in the
  design, a heteroscedastic noise model, or a trust-region-limited
  acquisition (log transforms stay pre-registered-forbidden). This failure
  is also why §2's model-based counterfactual cannot be quoted as
  evidence — its scoring GPs are these same models.

## (4) Interior vs edge character, tied to LOCATION v2

A tier is at an **edge** when its ω is at a lattice bound, 0.05 or 1.0
(`edge_summary.csv`, `figs/fig4_front_designs.png`):

| Set | Tiers at an edge (mean, of 6) | Share fully interior |
|---|---|---|
| Starts (Sobol) | 0.75 | 44 % |
| BO r1 | 1.9 | 0 % |
| BO r2 | 3.25 | 0 % |
| Front ∩ BO | 2.7 | 0 % |

BO moved steadily outward, and r2 was strongly edge-seeking. Read against
LOCATION v2:

- **Nuclear is bang-bang on the front.** Every BO front design has nuclear
  at a bound, mostly 0.05; the corners that minimize shed or curtailment use
  1.0. Spearman(nuclear MW, cost) = **0.89** over the 48 points. This matches
  v2's cost verdict (nuclear costs 5–7× more per MW than any partner):
  nuclear works as the switch between cost and reliability, not as a tuning
  knob. All three knees use nuclear = 0.05.
- **Wind_303 and wind_317 are loaded up on the front.** Mean ω on the front
  is 0.65 / 0.61, against 0.525 for the starts. Shed correlates most
  negatively with the wind tiers:

  | Tier | Spearman with shed |
  |---|---|
  | wind_122 | −0.58 |
  | wind_317 | −0.50 |
  | wind_303 | −0.48 |
  | nuclear | −0.31 |
  | pv | −0.19 |
  | tail | −0.16 |

  This reproduces v2's shed *ordering*: wind > nuclear > tail ≈ pv. These are
  marginal correlations over the 48 points and are confounded by total MW,
  so the order within the wind tiers is not resolved here.
- **Tail goes to 1.0 in r2** (6 of 8 picks), yet tail correlates with
  neither curtailment (−0.02) nor cost (0.03), and it is the smallest tier
  (at most 251.5 MW). Read this as EI pushing a nearly flat direction to its
  bound, **not** as evidence of a tail effect. This is consistent with tail's
  low per-MW shed value in v2. The asymmetric reading — nuclear-at-bounds
  as physics, tail-at-bounds as artifact — rests on a stated discriminator:
  nuclear carries Spearman 0.89 with cost plus v2's independent 5–7.6×
  per-MW cost tilt; tail correlates with nothing (−0.02 / 0.03).
- **PV shows no consistent push** (front mean ω 0.50), in line with its
  last place in v2's per-MW ordering.
- **Curtailment** was location-sensitive in 15/15 pairs in v2. The front's
  curtailment axis is consistent with the nuclear switch combined with how
  heavily the winds are loaded; curtailment is not a function of total MW
  alone.

Interior designs on the front come almost entirely from the Sobol starts.
Two of the three knees are BO designs, and they are interior on every tier
except nuclear.

## (5) Plain summary for Kay (≤ 6 sentences)

The automated q-ParEGO campaign ran two rounds of 8 and stopped on its
pre-registered rule. Each round added less hypervolume than the noise-based
threshold (+5.5 %, then +1.4 %, against 8 %). The final front has 26
designs, 13 of them from BO. The knee designs agree on one recipe: nuclear
at its floor and about 1.6–1.7 GW of electrolyzer, mostly on wind_303 and
wind_317. The GP's predictions were trustworthy for cost but too confident
for shed and curtailment at the extreme corner designs BO tried in round 2.
I re-ran round 2's acquisition locally and it reproduced CRC's 8 designs
exactly — though the "fully automated" chain needed one manual
resubmission, because CRC compute nodes are not allowed to submit jobs.

## Claim scope (maps to math-log §5.2)

Of the three pre-registered Stage-2 claims: **(i) "convergence within
budget" — NOT demonstrated**; say "terminated under its pre-registered
rule within budget". **(ii) "stability across ≥ 3 init seeds" — not
demonstrated for the 6-D campaign** (single seed; the replay's
seed-stability is 2-D and does not transfer). **(iii) "consistency of the
found designs with the sensitivity/interaction structure" — SUPPORTED**
(§4). Safe headline: an automated, pre-registered, interpretable MOBO
campaign on a real PCM — 13 of 16 BO picks landed on the final front
(a random 16-design batch puts 6.6 on the front of starts ∪ batch on
average, p10–p90 5–8, and 5.0 on the front of starts ∪ BO ∪ batch;
prompt 34 S2 ii) and two of three full-front knees are BO designs.
**Random baseline (prompt 34, `../random_baseline/RANDOM_BASELINE.md`):**
§3.2 row "above" at both refs — p̂48 = 0.94 [0.84, 1.00] at R_frozen,
1.00 [1.00, 1.00] at R_union — **not robust to floor-level output
perturbation** (47 % of perturbed draws keep the row); one BO
realization. Never claim: BO beat random
(single BO seed, not robust to floor perturbation; the ~70 % model figure
must not appear on a slide); convergence; surrogate accuracy beyond cost;
seed stability.

## Pain-log delta (the automation experiment's own report)

| Event (EDT) | Δ | Note |
|---|---|---|
| 10-06 15:50 → 16:31 | — | T1 machinery and artifacts pushed |
| 10-07 21:40, 22:05 | 2 fixes | block_1's dry-run harness failed on CRC twice: scratch tree was missing repo-level inputs, and a stdout-capture bug; the scratch repo also needed a local bare origin. Fixed from local before block #1 passed |
| 10-07 22:57 | — | r1 triple submitted by block #1 (chain live) |
| 10-08 15:00 | 16.1 h | r1 array + collector done; results pushed by the bot |
| 10-08 15:30 | 0.5 h | r1 acquisition graded, proposed r2, committed and pushed, then **WEDGED at qsub**: `denied: host "d12chas350.crc.nd.edu" is no submit host` |
| 10-09 11:27 | **≈20 h dead** | r2 triple submitted **by hand from the login node** (SUBMITTED line landed) |
| 10-09 17:57 | — | WEDGED marker cleared by hand |
| 10-10 09:03 / 09:05 | 21.6 h | r2 results; r2 acquisition graded → BO_DONE (stop rule), pushed |

- **Throughput:** 2 rounds in 58.1 h wall time, or **0.83 rounds/day**.
  Without the 20 h wedge it would be about 1.3 rounds/day, limited by the
  roughly 16–22 h Prescient arrays.
- **Human touches after launch:** 2, the manual r2 submission and the
  WEDGED clear. Before launch, block #1 needed 2 harness fixes.
- **Unattended hops that worked as designed:** both collectors, plus both
  acquisition jobs through grade → propose → commit → push → stop. The
  WEDGED trap fired correctly and left a diagnosable record.
- **The one structural defect:** acquisition jobs run on compute nodes, and
  CRC compute nodes cannot run `qsub`. A chain that submits round k+1 from
  inside round k's job can never work on CRC. The block #1 dry run could not
  catch this, because its PATH shim replaced `qsub`.
- **Recommended fix for any future campaign (not implemented; Kay to
  approve):** submit the whole chain from the login node at launch. Round
  k+1's array and collector are held on acq_k with `-hold_jid` and read
  their design matrix at *run start*, where acq_k has written it. Each job
  exits 0 on STOP_BO, or when the BO_DONE / FAILED marker for its round
  exists. qdel of the remaining held jobs then cleans up. The fallback is a
  login-node cron watcher that runs `submit_this.sh` when the round's
  "proposed" commit lands. Both options keep acquire_next unchanged.
- **Compute:** 16 runs at about 15 core-h each (measured: r1 + r2 mean
  14.9 h, range 11.7–21.6 h, single-slot), roughly 238 core-h, against the
  ≈ 310 core-h budget for 4 rounds.

## Open items

- g1 ruling, then re-level the absolute costs. Fronts and knees are
  invariant.
- ~~If the PI wants a stronger BO-vs-random claim: a matched real random
  batch, say 16 random lattice designs on CRC (about 155 core-h). The
  model-based counterfactual cannot substitute for it, because the models
  are not calibrated for shed and curtailment at the corners.
  **Risk to state before approving:** one batch is a single draw (n = 1
  vs n = 1) — Stage-1 showed random within 3–8 evaluations of BO at
  scenario C, so a single random batch may well match BO's realized
  trajectory. Either budget ≥ 3 batches (~465 core-h) or pre-commit to
  reporting one batch as an anecdote, not a test.~~ **DONE** (prompt 34:
  one i.i.d. pool of 48, subset-percentile statistic; see
  `../random_baseline/RANDOM_BASELINE.md`).
- Post-D3: starts, then reserve, as M additions (LOCATION v2 trigger).
  The calibration gap at the corners argues for a few corner points in any
  restart design.
