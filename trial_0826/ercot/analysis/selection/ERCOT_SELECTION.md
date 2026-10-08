# ERCOT_SELECTION.md — v0 (T0, 2026-10-08; zero new simulations)

**Mission:** the RTS-standard *presented* selection analysis for TX-123BT —
which sites/tiers, which objectives (M_ERCOT), what design space — every
verdict a multiple of a measured noise ruler. v0 = T0 evidence + the
decision register for the PI meeting. FINAL lands at T3 after the gated
T2 wave.

**Caveat rider on every number:** TL=120 ⇒ time-truncated MILP incumbents;
deltas only with ×-ruler; no cross-system cost-level comparisons vs RTS
(NXT-D5 rules); var_cost readings between designs whose truncated-day
fractions differ by > 5 pp carry a differential-bias caveat. Rulers are
IDENTICAL-INPUT rerun spreads conditional on the CRC execution environment
— a different phenomenon from RTS's perturbed-input mipgap-path floors,
playing the same ≈1σ role. The source-paper price mechanism is never
speculated on ("mechanism explanation pending (Kay)"; $17.98 is context,
never a target).

**Honesty clause (pinned for T3):** the RTS M-selection rested on the full
15-pair atlas; ERCOT T2 samples ~5 sweeps + 2–3 *selected* pairs. The
final RTS-vs-ERCOT table states this basis difference in its header, and
every pooled statistic is also reported per stratum.

Executed evidence: `selection_t0.ipynb` + `figs/` + `tm1_availability.csv`,
`tier_shares.csv`, `pool_correlations.csv`, `noise_ruler_v2.json`,
`fuel_note.json`, `t0_summary.json`.

## §1 Ruler bookkeeping (adjudication recorded; v2 list schema emitted)

The curtailment-ruler conflict is resolved as adjudicated 2026-10-07 and
re-verified here from the committed extracts, to the MWh:

> contaminated `overall.csv` 275-pair |Δ| **7,921.1** = clean non-PEM
> recompute **5,007.0** + PEM-twin |Δ| **2,914.1** (= the h2 ruler).

SCREENING_ERCOT.md's ruler table carried 7,921 with an inverted provenance
note — corrected in this commit. **Clean true_curt reading list =
{5,479.1 (base pair), 5,007.0 (275 pair)}**; the 397× site-275 headline
stands (2.17 TWh / 5,479). `noise_ruler_v2.json` stores per-pair reading
lists (never a bare scalar), keeps v1 frozen as provenance, tags every
df < 3 floor LOW-CONFIDENCE (verdicts against them need ≥ 3× not ≥ 2×),
and lists total_cost/fixed_cost as bimodal — no Gaussian machinery ever.

## §2 Objective-pool standings (restated with evidence pointers)

| Objective | Standing | Evidence |
|---|---|---|
| shed | **DEAD** | ≡ 0 fleet-wide, all 20 runs (SCREENING_ERCOT.md) |
| total_cost / fixed_cost | **DEAD campaign-wide** | ±$79.5M bimodal; gen-1 flips 25↔26 starts between replicate solves. *Possible nuclear-tier resurrection: T1's nuclear replicate tests whether forced commitment u≡1 pins gen-1's state (df = 1 ⇒ qualitative mode-pinning answer only).* |
| reserve | **guardrail only** | feasible improvement range [−280.9, 0] MWh < 1× the 554 ruler ⇒ no reduction can resolve; an INCREASE ≥ 2× (≥ 1,108 MWh) is readable and is flagged in every verdict table (GW-baseload withdrawal = plausible trigger). Not an M_ERCOT candidate. |
| starts (onoffs) | **SUSPECT class** | the 258 ruler IS commitment churn — the mechanism that killed total_cost. Verdict requires ≥ 3× AND per-unit decomposition concentrating on interpretable units AND sign consistency across ≥ 2 independent designs. |
| h2 | **DIAGNOSTIC by default** | quasi-deterministic in the design (noise ≤ 1% of effect — the readability ruler is vacuous). Enters M_ERCOT only by explicit PI adoption → D5. |
| **true_curtailment, var_cost (+ gated starts)** | **surviving grid-response candidates** | ERCOT's var_cost ≠ RTS's g1 column (total_cost_less_synthetic) — different quantities, never one column. |

## §3 T-M1 analogue — availability in cheap-LMP hours

`tm1_availability.csv`, `figs/tm1_curves.png`. Fraction of each site's
available energy in hours with own-bus LMP < τ (τ = 15 = the RTS T-M1
threshold; τ = 40 ≈ total availability on this price distribution — as
expected with mean LMP $14.53, and said so; the spread across τ is the
exhibit):

- Every VRE candidate sits at 0.875–0.979 at τ = 15 — cheap-hour-dominated
  everywhere, with the bus-120 pocket (0.967) and the PV@26 pair (0.979)
  at the top.
- **Nuclear gen 1 (bus 107): 0.360 at τ = 15** — by far the lowest; its
  bus clears well above the VRE buses, so band diversion there forgoes the
  most market value per MWh. **Gen 93 (bus 111): 0.814 — but it NEVER
  COMMITS in the base year** (0 output, 0 starts, 0 cost): a retrofit
  there is a commitment experiment, not a diversion experiment.
- D6 evidence only — the design-space default remains the full RTS lattice
  (Kay 09-19 no-feasibility-check precedent).

## §4 Tier proposal — quantitative (math-log §4.5 rule)

Effect shares s_i = max(Δtrue_curt_i, 0)/Σ max(Δ_j, 0) over the 16
distinct OAT designs; independent iff s_i ≥ 5% AND Δ ≥ 2× ruler (the
LOW-CONFIDENCE ≥ 3× variant gives the SAME set — robust). `tier_shares.csv`:

| candidate tier | members (share) | pooled share | status |
|---|---|---|---|
| **pocket_120** (cluster, pv_324 precedent) | 275 (.229) 274 (.165) 270 (.139) 163 (.045) 116 (.017) | **0.595** | independent, dominant |
| **wind_near** | 110 (.072, bus 2) 140 (.056, bus 2) 146 (.058, bus 75) | 0.186 | 110/140 share bus 2 → pool; 146 separate or pooled (judgment) |
| **pv_26** | 30 (.071) 59 (.038) | 0.109 | 30 independent; 59 sub-threshold → pool |
| big independents | 206 (.024) 205 (.014) 204 (.003) 91 (.029) | 0.069 | all sub-5%; **re-enter ONLY if D5 adopts h2 volume** (they divert 2.6–2.9 TWh each) |
| negative responder | 20 (−3.8× ruler) | — | listed separately, never pooled |
| **nuclear** (gen 1) | [GATED: D6] | — | T1 produces the OAT evidence; gen 93 stays out by design (never commits in base) |
| hydro | keep + exclude-from-curtailment | — | D6 confirm |

## §5 Objective-pool first cut (n = 16; NON-USE clause in force)

`pool_correlations.csv` — raw and gen_pmax-partialled Spearman side by
side; |Δ| < 2× ruler entered as ties; 5 of 16 designs share bus 120:

- relief↔var_cost **−0.37 / −0.36**: mild site-level conflict (the best
  relief sites are not the cheapest) — the T2 contrast to prioritize.
- relief↔starts +0.57 / +0.69; var_cost↔h2 +0.78 raw collapses to +0.41
  partialled (size is the common cause — the guard worked).
- **These prioritize T2 contrasts only; they may not add/drop pool
  members** (cross-site agreement at fixed ω ≠ design-space redundancy —
  that is T3's pooled job).

## §6 Congestion case study (NXT-D4 exhibit)

`figs/bus120_case_study.png`: bus-120 LMP CDF vs the median candidate
bus, relief/H2 bars (pocket 0.72–0.79 vs fleet 0.37), and the base-year
loading of the lines touching bus 120. Offered as the D4 exhibit;
half a page, no mechanism speculation.

## §7 Fuel-accounting note (g1-analogue; pre-registered BEFORE T1 runs)

`fuel_note.json`. The thermal patch (`multi_pem/parameters.py:27-43`) on
the ERCOT gen-1 dict takes the `del p_fuel` branch — **verified locally
2026-10-08: egret 0.6.2 parses gen 1 as `generator_type="thermal"`,
`p_min=729` present, emits `p_fuel` (4-point fuel_curve) and no
`p_cost`** — and installs the flat band + forced commitment. What leaves
the ledger, by the OBSERVED base year: **gen-1 booked Unit Cost
$3.1849B/yr** (3.30 TWh output, 25 starts). The parser-level fuel-curve
magnitudes do not reconcile with that booked figure at face value
(recorded open question for the PI meeting; observed number is
authoritative). Rule: **T1 nuclear var_cost readings are reported raw AND
fuel-cost-adjusted, each with the synthetic-cost caveat; adjudication =
PI. RTS g1 (NXT-D7) is never imported silently.**

## §8 Decision register (for the PI meeting; v0 + T1 nuclear evidence on screen)

| ID | Decision | Default / options | Evidence |
|---|---|---|---|
| **D4** | congestion-objective owner + definition | bus-120 exhibit offered | §6 |
| **D5** | claim scope; **var_cost as the cost objective** (vs waiting on a fuel-adjusted column); **adopt h2 volume as an objective?** — decides whether big independents 205/206 re-enter site selection | defaults: var_cost with caveats; h2 stays diagnostic | §2, §4, §7 |
| **D6** | **nuclear tier yes/no** (gen 1 only); **ω cap** (default = full RTS lattice); hydro keep+exclude confirm | T1 delivers: 5-level on-lattice nuclear OAT + mode-pinning replicate + T-M1's 0.360 cheap-hour fraction + gen-93 never-commits fact | §3, T1 |

## §9 T1 plan (no PI gate; smoke-gated)

11 full-year runs (~700–970 core-h), wave `waves/selection_t1/`:
2 more base (→ df = 3 base rulers) · 1 more wind-275 (→ df = 2) ·
2 PV-30 replicates (new stratum, → df = 2) · 5-level nuclear gen-1 OAT on
lattice indices {0,2,4,6,8} · 1 nuclear ω = 0.525 replicate (df = 1,
mode-pinning qualitative only — no quantitative nuclear floor at df = 1).
Gating: `SMOKE_PASS` file written by the 3-day nuclear ω = 1.0 smoke
after ALL gates pass (hold_jid alone releases on completion, not
success); every array task exits with a FAILED marker if it is absent.
Extraction rules pinned: **thermal h2 = Σ(p_max − Dispatch) over
committed hours** (never the is_pem pipeline, which returns 0 for
thermal); **mode-resolved base differencing** (classify every base solve
by gen-1 starts; never difference against the pooled base mean).
T2 (sweeps + 2–3 pairs + `__ALL_TIERS__` @ ω = 0.525) stays GATED on
D5/D6; budget ≈ 11,000–24,000 core-h.
