# Mechanism checks (prompt 38) — FINAL (T1 complete, 2026-10-15)

**Status: T0 + T1 complete. All evidence comes from the git wave
summaries, the local no-PEM base case
(`trial_0826/base_case_pcm_test`), and the 15 run dirs Kay rsynced
into `runs/` (gitignored). 0 new Prescient runs.**

Scripts: `t0_local_checks.py`, `t0_base_evidence.py`,
`t1_hourly_analysis.py`, `fig_local_evidence.py`, `fig_t1_h1.py`.
Outputs: `t0_summary.txt`, `t0_base_evidence.txt`, `t1_summary.txt`,
`run_selection.csv`, `t1_q2_events.csv`, `t1_q2_decomposition.csv`,
`t1_h1_table.csv`, `fig_shed_shortfall_vs_mw.png`,
`fig_h1_commitment.png`.

## Plain answer — Q1 (why shed falls as PEM MW rises)

Load shed in this system is a day-ahead under-commitment problem, not
an energy shortage. On every base-case shed hour the online headroom
is 0.0 MW and the DA LMP is low (median 20 $/MWh, 25% exactly 0): the
RUC trusts cheap wind forecasts, commits little thermal, and real
time comes up short. Pricing the PEM slices at B = 40 $/MWh removes
"free" energy from the RUC's view, so the RUC commits more thermal
(+780 to +1,280 MW and +4 to +5 units vs the zero-shed designs on
the critical hours), online headroom returns (0 to 460–770 MW), and
shed collapses. Extra thermal
dispatch covers 107–171% of the shed difference, while the PEM
slices' own grid sales cover between −4% and +26%; net renewable
delivery is actually LOWER in the high-MW designs on those hours.
Reserve shortfall falls with shed, not against it.

## Plain answer — Q2 (the recurring 22.426 MWh)

The 22.425956 MWh shared by 7 designs is one event: 2020-12-18, hour
7 (a winter morning), booked at the slack bus. The no-PEM base sheds
984.425956 MWh in that hour. Every high-MW design triggers the same
commitment change (adds 221_CC_1 + 321_CC_1 + 116_STEAM_1 +
202_STEAM_3 + 202_STEAM_4 = 1,017 MW, drops 315_CT_6 = 55 MW; net
+962 MW, all dispatched at full), which removes exactly 962.000 MWh
and leaves the same 22.426 MWh residual with headroom again at 0.
The event is PEM-independent in origin and its residual is identical
across designs; "zero shed" vs "22 MWh" is not a material
reliability difference.

## Verdict table

| Hypothesis | Verdict | Deciding evidence |
|---|---|---|
| H1 commitment headroom | **SUPPORTED (dominant)** | On the 100 shed hours of the lowest-MW design: committed thermal 2,520 MW vs 3,750–3,796 MW in zero-shed designs; headroom 0 vs 737–771 MW; extra thermal dispatch = 151–171% of the shed difference (`t1_h1_table.csv`, `fig_h1_commitment.png`). Thermal starts fall with PEM MW (Spearman −0.950): units cycle less, stay online. |
| H2 PEM slice sells in scarcity | **CONTRADICTED as a main driver** | PEM grid-sales share of the shed difference is −0.04 to +0.26 across the 8 LOW-vs-HIGH pairs; parent + PEM renewable delivery is lower, not higher, in zero-shed designs on those hours (share −0.23 to −0.73). Annual PEM grid sales do not rise with PEM MW (Spearman −0.298). |
| H3 location / congestion | **CONTRADICTED as stated** | 100% of shed (base and all 15 runs) is booked at bus "Arne" = bus 113, the reference bus; booked shortfall exceeds the bus's own demand in 71% of base shed hours (max 1,024 MW vs 144 MW). RT LMP is 463–653 $/MWh at ALL buses in the worst hour. Shed is system scarcity accounted at the slack bus, not bus-local congestion. |
| H4 reserve substitution | **CONTRADICTED** | Reserve shortfall also falls with PEM MW (Spearman −0.928); shed and shortfall co-move across designs (+0.955) and on the critical hours (49,834 → 4,630 MWh alongside shed 29,182 → 0). `fig_shed_shortfall_vs_mw.png`. |
| Nuclear u ≡ 1 as varying cause | **RULED OUT** | Nuclear ω ≥ 0.05 in all 96 designs; the fixed-commitment band is present everywhere. The 7 Q2 designs span nuclear ω from 0.05 to 1.00 with identical shed. |

## Paper-ready paragraph — Q1 (STE style)

> Load shed in this system is a commitment phenomenon, not an energy
> deficit. In the no-PEM base case, all 150 shed hours have zero
> online thermal headroom, and 86% of them clear the day-ahead
> market below the PEM bid B = 40 $/MWh (25% at 0 $/MWh): the
> day-ahead unit commitment trusts low-cost renewable forecasts and
> schedules too little thermal capacity. A PEM retrofit prices its
> renewable slice at B in the day-ahead market. This raises the
> apparent cost of renewable energy, so the commitment model brings
> more thermal units online. On the 100 shed hours of the smallest
> design (407 MW of PEM, 29,182 MWh of shed), the zero-shed designs
> (≈ 2,500–2,600 MW of PEM) commit 1,230–1,276 MW more thermal
> capacity and hold 737–771 MW of online headroom where the small
> design holds none (Fig. `fig_h1_commitment`). Added thermal
> dispatch supplies 151–171% of the shed difference; the PEM slices'
> own grid sales supply at most 26% and the net renewable delivery is
> lower, not higher. Reserve shortfall falls together with load shed
> (Spearman +0.955 across the 96 designs), so the gain is not a
> transfer between penalties. The monotone shed decrease with total
> PEM MW (Spearman −0.937) is therefore an induced day-ahead
> commitment effect of priced withholding, not electrolyzer energy
> returned to the grid.

## Paper-ready paragraph — Q2 (STE style)

> Seven designs report an identical load shed of 22.426 MWh. Hourly
> output shows one shared event: 2020-12-18, hour 07, the only shed
> hour in each of these designs. The no-PEM base case sheds 984.426
> MWh in this hour with zero online headroom and a day-ahead price
> of 12.5 $/MWh. Every design with enough priced PEM capacity
> induces the same day-ahead commitment change in this hour: five
> additional thermal units (1,017 MW) come online and one 55 MW
> turbine drops, a net gain of 962 MW, dispatched in full. This
> removes exactly 962.000 MWh of the base event and leaves the same
> 22.426 MWh residual, again at zero headroom. The event is present
> without any PEM and its residual does not depend on which sites
> hold the PEM capacity (the seven designs span nuclear ω from 0.05
> to 1.00). A reliability claim should therefore read "load shed at
> or below 22.4 MWh/yr, one commitment-limited winter-morning event
> that is independent of the PEM siting", not "zero load shed".

## What this changes for the knee / S1 / recipe wording

- Replace "zero shed" for front designs with "≤ 22.4 MWh/yr, one
  PEM-independent commitment-limited event (2020-12-18 h07)". The
  difference between 0 and 22.426 MWh among front designs is one
  residual hour and is not a material reliability distinction.
- The reliability gain from PEM MW is an induced DA-commitment
  effect of priced withholding (H1). State it as such; do not imply
  the electrolyzers return energy to the grid in scarcity (H2 is
  minor) and do not attribute it to siting (H3: shed is booked at
  the slack bus; the wind-tier correlations reflect MW share, not
  location).
- No shed-to-reserve substitution exists (H4): both penalties fall
  together, so the economy–reliability front is not distorted by a
  penalty swap.
- Caveat to carry: the mechanism is a property of the RUC's
  cost-based commitment under priced withholding. A market with
  different DA bidding or reliability unit commitment practices may
  not reproduce it; flag it as model-specific in the discussion.

## Appendix — T0 evidence retained

- 96 designs, scenario C. Spearman vs total PEM MW: shed −0.937,
  reserve shortfall −0.928, true curtailment −0.914, thermal starts
  −0.950, annual PEM grid sales −0.298. Shed range 0–29,182 MWh/yr;
  base 41,500.115 MWh/yr (150 hours, all booked at Arne).
- Q2 designs: stage2_C_n0 #1 #6, stage2_C_n0b #6, bo_C_r2 #7,
  random_C #5 #14 #15 (total PEM MW 2,078–2,462). bo_C_r1 #4
  (139.6 MWh) also contains the same 22.425956 event plus one other.
- Q1 contrast set and fetch list: `run_selection.csv`,
  `fetch_runs.sh` (15 run dirs, finished waves only; data fetched
  2026-10-15).
- The base no-PEM run at scenario C exists locally:
  `trial_0826/base_case_pcm_test` (the `summarize_wave.py` delta
  baseline). DA complacency persists in retrofit runs: the Q2 hour
  clears DA at 21.47 $/MWh in stage2_C_n0 #1.
