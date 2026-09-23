# ERCOT screening verdict (prompt 26; both arms analyzed 2026-09-22)

Evidence: `screening_analysis.ipynb` (executed) + `screening_site_effects.csv`
+ `screening_noise_ruler.json` + `figs/screening_value_tracking.png`.
16 OAT retrofits (ω = 0.5 wind / 0.4 PV, B = 40) + `__ALL__` + 2 replicate
noise-ruler rows. Standing footer: **DA≡RT (no forecast error); RUC
TimeLimit 120 s (12.1% days truncated); never compare cost levels to RTS.**

## Noise rulers (replicate pairs; the gate for every read)

| Objective | Ruler | Note |
|---|---|---|
| true curtailment (non-PEM WIND+PV) | **7,921 MWh** | `overall.csv`'s "renewables curtailment" counts the PEM twin's H2 as curtailment — always recompute from gen_summary |
| variable generation cost | **$0.29M** | the cost read-out |
| **total cost** | **UNREADABLE (±$79.5M bimodal)** | fixed-cost component flips between two commitment states; per-generator attribution: **gen 1, the 2,430 MW nuclear** (25↔26 starts, ±104 GWh, ±$79.6M). TL=120 toggles it nondeterministically — both replicate pairs landed in opposite states. |
| reserve shortfall | 554 MWh | small system total (281 MWh base) — near-degenerate |
| on/offs | 258 | |
| load shed | ≡ 0 everywhere | not an objective on TX-123BT (no shed in base or any retrofit run) |

## The screening verdict

1. **Retrofit value is congestion-locational, full stop.** System
   curtailment relief tracks the site's own base-case curtailment at
   Spearman **+0.89** — and tracks nothing else (availability −0.03,
   nameplate −0.17, H2 volume −0.04). The availability proxy that seeded
   v1 is formally dead (it already overlapped the true top curtailers
   only 3/9); the two-arm redesign was necessary and sufficient — both
   arms together cover the actual top-10 curtailers exactly.
2. **The bus-120 congestion pocket is the best place to divert, not a
   trap.** The pre-analysis worry was own-site reclassification; the
   data says the opposite: pocket sites convert H2 diversion into system
   relief at **0.72 MWh/MWh** (median; 275/274/270/163 at 0.72–0.79) vs
   **0.37** elsewhere. Site 275 alone: **2.17 TWh relief (397× ruler)**
   at +$6.2M variable cost.
3. **Big-availability sites without congestion are useless for relief
   and expensive.** Sites 20/204/205 (780–1,058 MW, uncongested buses):
   relief −21k/+25k/+137k MWh (−3.8×/4.5×/25× ruler — the first is
   *negative*) while variable cost rises **+$13.0–15.8M (46–55×)**:
   diverting sellable wind forces expensive replacement generation.
   (They do produce the most H2 — sites 205/206 divert 2.6–2.9 TWh — so
   they stay relevant *only* if an H2-volume objective enters M; for
   curtailment/cost they are pure loss.)
4. **Interactions are mild at screening depth:** joint `__ALL__` relief
   = 0.933 × Σ(OAT) over the v1 nine — 6.7% sub-additive (RTS showed
   ~20% on its headline pair).
5. **All retrofits raise variable cost** (+$0.9M to +$15.8M): with zero
   load shed and cheap fuel, curtailed energy is free but its diversion
   partner (B = 40 clearing + replacement energy) is not. The
   cost-vs-relief frontier is carried by the pocket sites.

## Proposed ERCOT tier structure (for the PI — decision required)

- **Tier `pocket_120`** (cluster, one shared (ω, B)): 275, 274, 270,
  163, 116 — 2,749 MW, 5 of the top-8 curtailers, one electrical
  location. The screening cannot separate members at one bus (shared
  congestion driver); a cluster is the honest granularity.
- **Tier `wind_near`** (cluster): 110, 140 (bus 2) + 146 (bus 75) —
  secondary pockets, relief 96–125× ruler at 0.63–0.67 relief/H2.
- **Tier `pv_26`**: 30 + 59 (bus 26; PV pocket, 0.52–0.54) — plus 142
  (bus 14) if a third PV lever is wanted (0.37, weakest keeper).
- **Drop**: 20, 204, 205, 206, 91 — no learnable curtailment signal
  (relief ≤ 25× ruler but per-H2 efficiency ≤ 0.14 and var-cost 25–55×
  against), unless an H2-volume objective is adopted (then 206/205 are
  the volume levers and re-enter as their own tier).
- **Nuclear (2 units, 2,430/2,708.6 MW): still the open PI question**,
  now with hard evidence attached — unit 1's commitment is degenerate at
  ±$79M under TL=120. Note a nuclear retrofit's forced commitment would
  *pin* that state (removing the bimodality) — an argument for including
  one nuclear tier if only to stabilize the cost objective; ω at RTS-like
  levels implies a GW-scale electrolyzer at one bus.
- Hydro stays excluded from curtailment accounting (constant-PMax
  caveat; 09-19 decision) — unchanged.

## Workflow-pain log (prompt-26 sprint, compiled at analysis time)

- **Touch log:** block #1 (submit; +2 patch verifications), block #2
  (submit; riders clear), block #3 (submit; base died in 1 s — mkdir),
  fix `de4fb43` + block #5 resubmit (failure-recovery), block #4b
  (submit; two arms). Failure events: 1 (mkdir; marker pushed 09-20
  18:37Z, fix 11 min later, recovery same session).
- **Automation:** base collector ran unattended end-to-end incl. clearing
  the stale FAILED marker (`be5d254`); both screening collectors
  first-pass (`6dc533e`, `33a139b`). Post-submission human touches after
  the mkdir fix: **zero**.
- **Latency:** base wave submitted (block #5, 09-20/21) → extract on
  branch 09-21; screening arms submitted (block #4b) → both extracts on
  branch 09-22 (≈ 1 day/wave at 12–19 concurrent full-year tasks, no
  `-tc`). PENDING-KAY: per-task queue/run split (`qacct`), block-log
  timestamps for the human-gated gaps.
- **The ranking-gate design worked:** block #4's 3/9 slate gate tripped
  as designed → two-arm redesign instead of burning 12 runs on the weak
  proxy slate.

## Carried PI questions (unchanged wording, new evidence)

1. **Tier structure incl. GW-scale nuclear** — see proposal above; new
   evidence: the ±$79M unit-1 commitment degeneracy.
2. **Hydro treatment** — excluded from curtailment accounting; keep-with-
   caveat unchanged.
