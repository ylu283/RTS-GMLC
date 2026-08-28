# Screening Review — 3-Expert Quality Guard Synthesis (2026-08-24)

Three independent expert reviews (numerics audit, power-systems physics,
BO/campaign design) of `screening_analysis.md` and the underlying data.
Full analysis stands numerically; interpretation amended as below.

## Verified clean

- Every number in `screening_analysis.md` independently reproduced from the
  CSVs — zero discrepancies. Deltas exact vs base (float precision); H2
  accounting exact; PEM capacities exact; **all-in dict = exact union of the
  11 OAT dicts**; all 12 logs completed cleanly (8.3–22.9 h); shed column
  independently confirmed against per-hour log lines.

## Verdicts (final)

### Tier structure: merge to 6 tiers, d = 12  ✅ recommended

`pv = {319_PV_1, 324_PV_1/2/3}` replaces pv_319 + pv_324. Rationale:

1. 319_PV_1 = 4.2% < 5%, **and pv_324 as a tier is itself only 3.9% < 5%**
   — one merge resolves both sub-threshold flags. Merged shares: wind
   29.5/21.9/18.3, nuclear 16.3, pv 8.1, tail 5.7 — every tier ≥ 5.7%.
2. **The B-axis endpoints agree.** The physics review worried B=40
   compresses shares toward capacity ratios and 319 might cross 5% at low
   B. But the low-B limit is already measured: as B→0 the PEM reduces to a
   pure curtailment mop, so effect shares approach own-curtailment shares —
   319 = 74.5k/1,689k = **4.4%**, also below 5%. Both ends of the B axis
   (4.4% and 4.2%) say demote; no extra run needed for the tier call.
3. Share semantics are sound: under proportional attribution, "share of
   Σ-OAT" ≡ "share of joint effect" (the +54.6% inflation cancels), and
   substitution plausibly cannibalizes small overlapping pools hardest, so
   4.2% is an upper bound on 319's joint share.
4. All four PVs: near-identical per-MW effect (1,269–1,590 MWh/MW) and CF
   (0.41–0.42) — a shared "PV policy" (ω, B) is coherent; type homogeneity
   beats bus homogeneity (tail already mixes buses).
5. d = 14 → 12: n₀ = 128 becomes 10.7d (crosses the 10d guideline); free to
   change now — n₀ is held, redraw at same seed costs nothing.

Top-4 independence (303/317/122/nuclear, shares 16–30%) is robust at any B
and any attribution reading.

### Noise model: "zero floor" amended to a two-regime statement

- **Identical inputs → zero noise** (pilot repeats bit-identical) — stands.
- **Perturbed inputs → nonzero floor**: the near-identical pv_324 triplet
  spans +2,193 to −2,293 MWh in Δshed (sign flip); mipgap-1% on a
  ~$1.43M/day RUC objective admits ~500–700 MWh/day of commitment reshuffle
  cashed out through the zero-lookahead SCED. **Interpretability floors:
  |Δshed| ≲ 3k MWh/yr = zero within noise; |Δcurt| ≳ 5k MWh trustworthy.**
  GP nuggets: f4 scale ≈ 2.5k MWh; f3 ≈ 3k MWh; f1 ≈ $0.5M (observed
  small-PV cost chatter).
- All curtailment-based shares/verdicts and the +54.6% gap are far above
  floor — unaffected. Small-site shed and cost deltas are below floor —
  report as "0 within noise", never as findings.

### f4 (unserved energy): contaminated for renewable sites — placebo run needed  ⚠

Wind OAT shed reductions (317: −22.0k, 122: −21.4k = half of base shedding)
are physically inverted vs nuclear's −3.5k (whose band actually adds zero
scarcity-hour supply — base nuclear already runs at P_max when LMP > 40).
Likely mechanism: **DA-commitment artifact** — pricing wind at $40 makes the
RUC treat forecast output as withheld → commits more thermal → the extra
iron serves load when wind underperforms in RT. "Withholding makes DA
conservative," not "the PEM firms supply."

**Action: add ONE placebo run (`waves/placebo`) to the next CRC batch** — 317 OAT with B ≈ 0
(gen_PEM at cost ~0 is economically identical to the unsplit base; any
residual Δshed isolates the pure split/commitment artifact). Until it runs:
wind f4 gains and the all-in −93% shed carry an explicit caveat; f4 drives
no tier or acquisition decision.

### Kernel: additive candidate REJECTED (recorded)

g = +54.6%, of which ≥ ~35% is arithmetically forced (Σ-OAT 2,273k exceeds
total base surplus 1,689k — cannot remove more surplus than exists).
Interactions are dense and global (wind OAT reductions exceed own-site base
curtailment: 122 by 1.8×, via cross-site transfer of withheld cheap energy).
Use vanilla full-ARD Matérn-2.5 per objective; lengthscale inspection is the
structure diagnostic.

### Also recorded

- The "reduction > own curtailment" magnitudes lean on cross-site transfer;
  a per-generator curtailment cross-check of run 4 (122) vs base on CRC
  (raw data lives there) would close the remaining [MEDIUM] accounting concern —
  cheap, optional, uses existing outputs.
- ~45–52% of days terminate transmission-infeasible (lazy-PTDF iteration
  cap) — common-mode across all runs incl. base; largely differences out,
  but adds the path-dependence behind the shed chatter.
- Screening was measured at B = 40 (the aggressive envelope): shares are an
  ω,B-envelope decision basis, not B-averaged sensitivities.

## Actions

1. [Kay approves] Edit `tiers.py`: merge to 6 tiers → redraw n₀ = 128 at
   seed 20260821 (held anyway pending PI decisions — free).
2. Add the B≈0 317 placebo run (`waves/placebo`) to the next submission batch (~10 h, 1 job).
3. Living report updated: §3.3 (d=12), §4.3 (kernel closed), §4.5/§5
   (two-regime noise), §7.2 (results + verdict), f4 caveat.

(2026-08-27: the B≈0 control wave was renamed to "placebo".)
