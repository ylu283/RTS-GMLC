# g1 nuclear fuel-accounting patch — PROPOSAL (writing only; nothing implemented)

**Status: awaiting PI review (pi-directive-2026-09 §1, g1 row: "Propose the
math patch first … do NOT implement before PI review").** This document
proposes the correction; no extraction code, objectives.csv, or figure has
been touched. Prepared 2026-09-20, branch d6.

---

## Memo to Prof. Dowling (plain language, one page)

**What is wrong today.** Our nuclear PEM retrofit works by re-pricing the
plant's top band: the model raises the unit's minimum output and replaces
its *entire* cost curve with the synthetic H2-bid curve. That deletes the
plant's real fuel bill from the simulation's ledger. The bill is large and
simple: the RTS nuclear unit's cost curve is **flat — $3,208.99 for every
committed hour, with zero marginal cost** — so the deleted amount is about
**$28.2M per year, ~56× our $0.5M cost noise floor**. Every cost number we
have published for a nuclear-retrofit run carries this hole (flagged
APPROX since 08-28); everything wind/solar-only is clean.

**Why it is now urgent.** The location analysis (prompt 28) compares tiers
on cost. Uncorrected, nuclear looks like the *cheapest* retrofit site at
every capacity level — an artifact of the missing $28M. Corrected, it
becomes the *most expensive*, and the cost-vs-location picture inverts
(details in §3). Five nuclear pair-grid waves are in flight and the
objective-vector (M) decision consumes these cost verdicts, so the
accounting must be settled first.

**What we propose.** An extraction-side **add-back** — a corrected-cost
column computed from existing outputs; no simulation is re-run. Because
the real curve is flat, the correct add-back is simply the flat rate times
the forced-committed hours:

> **corrected cost = raw cost − synthetic bid cost + $3,208.99 × 8,784
> = raw − K_syn + $28,187,733 per nuclear-retrofit full-year row,
> constant in ω.**

The once-discussed "delivered × $8.1/MWh" form (pi-agenda §5) predates
our audit of the curve shape: $8.1035/MWh is only the *average* rate at
minimum output. Pricing delivered MWh would make deep retrofits look up
to ~$14M/yr cheaper purely by bookkeeping, and would *flip the sign* of
cost-vs-ω for nuclear. §2 adjudicates the three candidate rules.

**What we need from you.** One decision: **approve option (c) (faithful
restoration of the flat curve, constant add-back), or amend** to (a)
average-rate × gross MWh (differs by +$0.28M ≈ 0.6× floor) or (b)
delivered-only (we recommend against; §2 documents why it is ill-defined
here). Everything downstream — corrected sweep curves, the pair-grid
analysis, the M decision, any NPV objective — applies mechanically once
the rule is fixed.

---

# Technical appendix

## 1. The mechanism, stated exactly (from code)

`trial_0826/multi_pem/parameters.py`, `_update_thermal_generator`
(lines 27–43), applied to `121_NUCLEAR_1` in every nuclear-retrofit run
(single unit — thermal retrofits get **no** twin split):

- `PEM_capacity = ω · p_max`; `p_min ← p_max − PEM_capacity` (line 28–29);
- the **entire** cost curve is replaced (line 38):
  `p_cost.values = [[p_min, 0.], [p_max, PEM_capacity·B]]`
  — zero cost at the new p_min, slope exactly B across the band;
- ramps set to the band width (41–42); **commitment forced all hours**
  (line 43: `fixed_commitment = 1` for all time keys).

What leaves the ledger: the unit's real fuel cost function, in full. What
enters: a synthetic band cost equal to B per MWh dispatched above p_min.
Under forced commitment the unit also incurs **no startup cost** (base ran
4 starts).

### The real curve is FLAT (derived numerically, not from HR arithmetic)

`RTS_Data/SourceData/gen.csv` row 75 (`121_NUCLEAR_1`): PMax 400, PMin
396, Fuel Price $0.81035/MMBTU, HR_avg_0 = 10,000 BTU/kWh at
Output_pct_0 = 0.99, **HR_incr_1..3 = 0** → zero marginal cost above
PMin = 396 MW. Verified hourly in
`trial_0826/base_case_pcm_test/thermal_detail.csv`: over the full year the
unit takes exactly two on-hour Unit Cost values —
**$3,208.986** (8,585 plain on-hours, dispatch 396–400 MW) and
**$67,208.8083** (4 start hours = 3,208.986 + **$63,999.822** startup-fuel
adder; cross-check 78,978 MMBTU × $0.81035 = $63,999.82). Base-year total:

> **$27,817,980.04 = 8,589 on-hours × $3,208.986 + 4 starts × $63,999.82.**

The familiar "$8.1/MWh" is the *average* rate at PMin
($3,208.986 / 396 = $8.1035) and matches spend only because the unit sits
at 396–400 MW all year. The deleted object is **per committed hour**, not
per MWh.

Note the retrofit deletes slightly *more* than the base total: forced
commitment runs 8,784 h vs the base's 8,589 (structural gap
**+$625,752** vs base running cost, **+$369,753** vs base total including
its 4 starts — the +$0.37–0.66M band used in §4's check).

### Tie-in to the existing three-way accounting

`summarize_wave.py` reports, per row: `total_cost_raw_usd` (Prescient's
objective, containing the synthetic band cost), `synthetic_bid_cost_usd`
(K_syn — for the thermal site this is the unit's **entire** booked Unit
Cost, line 161: "real fuel cost deleted by the patch → all synthetic"),
and `total_cost_less_synthetic_usd = raw − K_syn`. The APPROX caveat is
precisely that raw − K_syn removes the synthetic cost but restores
nothing real.

## 2. The proposed correction — three options adjudicated

The patch is an **extraction-side add-back**: a corrected column computed
from existing outputs. Raw runs are never re-run; frozen files never
edited. The old delivered-vs-generated dichotomy dissolves once the curve
shape is seen — the deleted object is per-committed-hour:

| | Rule | Full-year value | Assessment |
|---|---|---|---|
| **(c)** | **Faithful restoration: re-price the deleted curve.** Flat rate × forced-committed hours: $3,208.986 × 8,784 | **$28,187,733.02, constant in ω** (no MWh series needed — marginal cost is zero over the curve's whole domain) | **RECOMMENDED.** Restores exactly what line 38 deleted; needs no bridging assumption; exact from base data. |
| (a) | Average-rate × gross MWh: $8.1035 × 400 MW × 8,784 h | $28,472,457.60 (+$284,725 over (c) ≈ 0.57× floor) | Numerically close but requires the always-committed-at-p_max bridging assumption and imports a fake per-MWh framing. Acceptable fallback. |
| (b) | Delivered-only (pi-agenda §5's older "delivered × $8.1/MWh") | ω-dependent; e.g. ≈ $14.8M at ω = 0.5 | **Ill-defined and rejected.** For ω > 0.01 dispatch drops below 396 MW, where the base curve has no definition; and it zeroes the fuel attributable to the H2 stream — an artificial ~$13–14M/yr "saving" at ω = 0.5 that scales with retrofit depth (≈ −$25M per unit ω). It flips the cost-vs-ω slope (§3). |

**Interaction with K_syn — no double count.** Because line 38 replaces the
*whole* curve, the run's booked nuclear cost is 100% synthetic and K_syn
subtracts 100% of it; the add-back restores the real curve into the
resulting vacuum. `corrected = raw − K_syn + add-back` has no residue
term. (Startup fuel needs no add-back: forced commitment means no starts
occurred in-run, so none was deleted from any *incurred* hour; the
base-vs-retrofit start difference lives in the §4 structural-gap budget,
not in the row correction.)

**Thermal "grid sales", defined.** The §1 identity "K_syn = grid sales ×
B" was coined for the renewable twin; `site_detail.csv` carries
`pem_grid_sales_mwh = NaN` for thermal rows. For the thermal site define
**band sales ≡ pem_capacity_mw × 8,784 − h2_mwh**, using site_detail's
*recorded* `pem_capacity_mw` and `h2_mwh` (`h2_mwh` is p_max·hours −
ΣDispatch per `summarize_wave.py:160`). Then K_syn = B × band sales,
exactly. **Precision trap found while verifying:** the retrofit JSONs
round PEM_fraction to 4 decimals (e.g. ω = 0.10625 → 0.1063 → capacity
42.52 MW, not 42.50), so computing the band from the *design-matrix* ω
leaves ±B × 175.68 MWh ≈ ±$7,027.20 (scenario C) discrepancies on the
half-precision levels. With the recorded `pem_capacity_mw` the identity
closes to ≤ $0.002 on all 18 sweep rows. Any implementation must use the
recorded capacity.

### Identity shown end-to-end, twice

**(i) Cent-exact on real raw CSVs — `waves/pilot/runs/run_index_1/`**
(the one wave with local raw runs; nuclear ω = 0.275, legacy bid
B = 27.5, so p_min = 290 MW, band 110 MW):

```
hours = 8,784; min hourly dispatch = 290.0 = p_min  (forced commitment holds)
Σ Unit Cost                      = $537,996.344284
B · (ΣDispatch − p_min · hours)  = $537,996.344380   → difference $0.000096
h2_mwh      = 400·8,784 − ΣDispatch = 946,676.497 MWh
band sales  = 110·8,784 − h2_mwh    =  19,563.503 MWh ;  B · band = $537,996.34 ✓
corrected   = raw − 537,996.34 + 28,187,733.02   (add-back (c))
```

**(ii) On a mid-ω sweep row from its EXTRACT records** — `sweep_C`
index 5 (nuclear OAT, ω = 0.275, B = 40; objectives.csv +
site_detail.csv only):

```
K_syn (objectives.csv)                       = $1,585,951.98
band  = pem_capacity_mw·8,784 − h2_mwh       = 110·8,784 − 926,591.20 = 39,648.80 MWh
B · band = 40 × 39,648.80                    = $1,585,951.98   (closes to $0.001)
corrected = 508.86M (less-synthetic) + 28.19M = $537.05M
```

Gross generation under forced commitment is 400 × 8,784 = 3,513,600 MWh
on every nuclear-retrofit row; the add-back (c) never needs it, which is
part of its appeal.

## 3. Blast radius — what moves, and by how much

Add-back (c) is **+$28.1877M (56.4× floor), constant in ω**, on every
full-year row with nuclear retrofitted; wind/PV-only rows move $0.
"Preview" numbers below are arithmetic on existing outputs, labeled
**preview under proposed correction, pending PI approval** — nothing is
written into objectives.csv.

| Artifact | Moves? | Magnitude (preview under (c)) |
|---|---|---|
| `sweep_C` nuclear OAT (9 rows) | yes | less-synthetic $496.16→521.89M becomes **$524.34→550.08M** (each +28.19M = 56.4× floor; ω-slope unchanged) |
| `sweep_B` nuclear OAT (9 rows) | yes | $496.15→521.28M becomes **$524.34→549.47M** (same shift) |
| `stage2_backfill_C` nuclear rows 1–8 | yes | $502.7–552.6M → **$530.9–580.8M** |
| `stage2_C_n0` (extracts synced 09-20) | yes — **all 16 rows** (every row has nuclear ω ≥ 0.05) | $539.3–641.2M → **$567.4–669.4M** |
| 5 `pairgrid_nuclear_*_C` waves (in flight) | yes | correction applied at analysis time in prompt 28 T2/T3 **if approved** — the collectors publish uncorrected extracts; the pair pipeline adds the column |
| `pilot` wave (12 runs, ω = 0.275, legacy B = 27.5; unpublished) | yes if ever summarized | +28.19M per row; raw-CSV demo ground for §2(i) |
| **LOCATION.md v0 cost rows** | **yes — the single strongest reason to rule now** | see below |
| `pi_0911.md` §4.4 (nuclear tier cost panel, annotated "APPROX excludes ~$27.8M/yr") | yes | annotation replaced by corrected values; the living report's "nuclear OAT Δcost −$0.56M" becomes ≈ **+$27.6M real**. §8b/8c are wind-only — unaffected. |
| Living-report cost narrative (`living-report-multipem.md`, 08-28/09-10 entries) | yes | same re-statement; the "understated $14–28M" range collapses to the single constant under (c) |
| NPV candidate objective | yes | any NPV definition carries nuclear fuel as an operating cost — the adjudicated rule propagates into it verbatim |

**The LOCATION.md v0 cost verdict, quantified.** Interpolating the
sweep_C per-tier cost curves at matched total-PEM MW (floor_L = $2.02M,
the 6-draw range floor):

| T (MW) | L(T) uncorrected | cheapest tier | L(T) corrected (c) | cheapest tier |
|---|---|---|---|---|
| 50 | $25.1M (12.4×) | **nuclear** | $3.8M (1.9×) | tail |
| 100 | $19.6M (9.7×) | **nuclear** | $9.8M (4.8×) | tail |
| 150 | $14.3M (7.1×) | **nuclear** | $16.3M (8.1×) | tail |
| 200 | $8.2M (4.0×) | **nuclear** | $23.1M (11.5×) | tail |

Uncorrected, nuclear is the cheapest tier everywhere and the spread
*shrinks* with T; corrected, nuclear is the **most expensive** tier
everywhere and the spread *grows* with T. The "cost is
location-sensitive" verdict survives, but its magnitude profile and the
site ranking that the M decision would consume are artifacts until the
rule is fixed. And the *choice* decides the slope verdict: under (a)/(c)
the add-back is constant in ω (slope preserved, intercept +$28M); under
(b) it falls ≈ $25M per unit ω (slope flips). **This is why the PI must
rule before the M decision.**

## 4. Verification plan (post-approval; for the implementer)

Three checks, all must pass:

1. **Identity, exact:** `corrected = total_cost_raw_usd −
   synthetic_bid_cost_usd + 28,187,733.02` on every nuclear-retrofit
   full-year row (equivalently `total_cost_less_synthetic_usd +
   add-back`). PLUS the extrapolated ω → 0 comparison against base: no
   true ω = 0 row exists (minimum is 0.05), so extrapolate the corrected
   nuclear OAT curve to ω = 0 and compare to the base $522.48M with the
   forced-commitment gap **explicitly budgeted (+$0.37–0.66M)**.
   Reference point: corrected sweep_C ω = 0.05 sits +$1.86M above base =
   structural gap + real displacement cost of the 167.7 GWh H2 diversion.
2. **Both §2 hand-computations reproduced by code to the cent** — the
   pilot raw-CSV check (i) and the sweep_C index-5 extract check (ii),
   with the printed intermediate quantities matching this document.
3. **K_syn identity preserved with the DEFINED thermal band-sales
   expression:** `K_syn = B × (pem_capacity_mw × 8,784 − h2_mwh)` using
   site_detail's recorded capacity — **never** the NaN
   `pem_grid_sales_mwh` column and never design-matrix ω × p_max (the
   ±$7,027 rounding trap in §2).

**Where the implementation lands — recommendation:** add the columns
(`nuclear_fuel_addback_usd`, `total_cost_corrected_usd`) to
`summarize_wave.py` so every *future* collection (including the five
in-flight pair grids at their collection time) emits them at the source.
For the **already-summarized waves** (sweep_B/C, stage2_C_n0,
stage2_backfill_C): their raw runs live only on CRC, so local
re-summarization is impossible — bridge with a small **analysis-side
helper** (the constant + the row mask "nuclear ω not NaN") used by
prompt 28's T2/T3 until Kay re-runs `summarize_wave.py` on CRC and the
bot pushes regenerated objectives.csv (a sanctioned pipeline
regeneration, not a hand edit; one commit, labeled). The helper and the
column must agree to the cent (check 2 covers this).

---

*Prepared under prompt 29. Sources: `multi_pem/parameters.py` (read at
d6 `ea247fa`), `RTS_Data/SourceData/gen.csv` row 75,
`base_case_pcm_test/thermal_detail.csv`, `waves/pilot/runs/run_index_1/`,
`waves/sweep_{B,C}/` + `waves/stage2_*/` extracts,
`analysis/location_0920/LOCATION.md` v0, `analysis/pi_0911/pi_0911.md`
§4.4, pi-agenda.md §5, living-report-multipem.md. All preview arithmetic
ran in the session scratchpad; this file is the only repo change.*
