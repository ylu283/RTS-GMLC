# Mechanism checks (prompt 38) — T0 state, before the CRC rsync

**Status: T0 complete (2026-10-15). All results below come from LOCAL
data only: the git wave summaries of the five finished waves and the
local no-PEM base case (`trial_0826/base_case_pcm_test`). 0 Prescient
runs. Hourly per-run confirmation waits on `fetch_runs.sh` (Kay runs
it). Verdicts marked PRELIMINARY become final in T1.**

Scripts: `t0_local_checks.py` (96-design table, run selection),
`t0_base_evidence.py` (base-case hourly evidence),
`fig_local_evidence.py` (figure). Outputs: `t0_summary.txt`,
`t0_base_evidence.txt`, `run_selection.csv`,
`fig_shed_shortfall_vs_mw.png`.

## Q1 — why does load shed fall as PEM MW rises?

Headline correlations over the 96 designs (scenario C; shed range 0 to
29,182 MWh/yr; base case 41,500 MWh/yr):

| pair | Spearman |
|---|---|
| total PEM MW vs load shed | **−0.937** |
| total PEM MW vs reserve shortfall | **−0.928** |
| total PEM MW vs true curtailment | −0.914 |
| total PEM MW vs thermal starts | **−0.950** |
| load shed vs reserve shortfall | **+0.955** |
| total PEM MW vs annual PEM grid sales | −0.298 |

Base-case anatomy of shed (from local hourly files):

1. All 41,500 MWh of base shed is booked at ONE bus: **Arne (bus 113,
   the reference bus)**. In 71% of shed hours the booked shortfall
   exceeds the bus's own demand (max 1,024 MW shed vs 144 MW demand).
   Prescient books system-wide real-time shortfall at the slack bus.
   The "shed bus" is accounting, not geography.
2. On every shed hour the RT LMP is exactly 500 $/MWh at Arne, and
   463–653 $/MWh at ALL buses in the worst hour. This is system-wide
   scarcity, not local congestion.
3. **DA LMP on shed hours: median 20 $/MWh; 86% below B = 40; 25%
   exactly 0.** The day-ahead market saw no scarcity on the hours that
   later shed. The RUC under-commits on wind-rich forecasts; real-time
   wind under-delivers.
4. **Available headroom is 0.0 MW on all 150 shed hours** (median
   1,110 MW on non-shed hours). Shed occurs exactly when online
   headroom is exhausted.
5. 100% of base shed hours also have reserve shortfall. The two
   penalties co-bind.

Preliminary verdicts:

- **H1 (commitment headroom): SUPPORTED, preliminary.** Shed is a
  zero-headroom, DA-complacent phenomenon (facts 3–4). Pricing the
  wind slice at B = 40 removes "free" energy from the RUC's view, so
  the RUC commits more thermal. Thermal starts fall steeply with PEM
  MW (−0.950): units stay online instead of cycling. T1 confirms with
  committed-MW and headroom comparisons on the shed hours (LOW vs
  HIGH designs).
- **H2 (PEM slice sells in scarcity): PLAUSIBLE, undetermined.** The
  `_PEM` units are dispatchable at B = 40 and will sell when price
  exceeds B. But annual PEM grid sales do NOT rise with PEM MW
  (−0.298), which weakly disfavors H2 as the main driver. T1 checks
  `_PEM` dispatch on the shed hours directly.
- **H3 (location / congestion): CONTRADICTED as stated, preliminary.**
  The bus-level shed location is slack-bus accounting (facts 1–2).
  The wind-tier correlations with shed (BO_STAGE2 §4) reflect those
  tiers' MW contribution, not bus-local relief. T1 checks line
  binding if line files arrive; not required for the verdict.
- **H4 (reserve substitution): CONTRADICTED.** Reserve shortfall also
  FALLS with PEM MW (−0.928), and shed and shortfall move together
  across designs (+0.955). There is no shed-to-reserve trade. See
  `fig_shed_shortfall_vs_mw.png`.
- **Nuclear u ≡ 1:** nuclear ω ≥ 0.05 in every design (min observed
  0.05), so the fixed-commitment nuclear band is present everywhere
  and is not the varying cause. Confirmed.

## Q2 — the recurring 22.425956 MWh shed

Seven designs share load shed = 22.425956 MWh exactly:
stage2_C_n0 #1, #6; stage2_C_n0b #6; bo_C_r2 #7; random_C #5, #14,
#15 (all with total PEM MW ≥ 2,078; full list in `t0_summary.txt`).

**Local smoking gun:** the no-PEM base case sheds **984.425956 MWh on
2020-12-18, hour 7** — the only base hour whose fractional part
matches. 984.425956 − 22.425956 = **962.000000 MW exactly**. The
recurring value is the residual of this single base event after the
retrofit adds exactly 962 MW of effective real-time supply (an
integer, which points to a nameplate-quantum commitment difference).
DA LMP in that base hour was 12.54 $/MWh — again a DA-complacent
hour. The event is in the base case (at 984 MWh), so it is
PEM-independent in origin; high-MW designs shave it to a common
22.426 MWh floor. T1 confirms the bus-hour identity and the 962 MW
composition from the fetched hourly files.

Implication for wording (pending T1): "zero shed" vs "22 MWh" among
front designs is one residual hour of one winter-morning event, not a
material reliability difference. Say "≤ 22 MWh, one PEM-independent
event" instead of "zero shed".

## T1 plan (after Kay's rsync)

1. Q2: for each of the 7 designs, list shed bus-hours from
   `hourly_summary.csv` / `bus_detail.csv`. Expect exactly one:
   2020-12-18 h7, 22.425956 MWh at Arne. Identify the 962 MW from
   `thermal_detail.csv` (committed units, Unit State, Dispatch DA vs
   RT) and `renewables_detail.csv` (`_PEM` output).
2. Q1/H1: on the shed hours of bo_C_r2 #3 and random_C #42 (LOW),
   compare committed thermal MW, online headroom, and committed-unit
   count with the same hours in bo_C_r1 #5 and bo_C_r2 #2 (HIGH).
3. Q1/H2: sum `_PEM` dispatch (grid sales) on LOW-design shed hours
   in the HIGH designs; ask whether it covers the shed difference.
4. Q1/H4: reserve shortfall on the same hours (`reserves_detail.csv`)
   to close the co-binding story.
5. Write the two paper-ready paragraphs and final verdict table here.

## Run selection (15 run dirs, finished waves only)

See `run_selection.csv`. Q1 contrast set: bo_C_r2 #3 (407 MW, 29,182
MWh), random_C #42 (827 MW, 9,312 MWh), stage2_C_n0 #16 (1,763 MW,
2,516 MWh), random_C #30 (1,764 MW, 4,549 MWh), bo_C_r1 #5 (2,494
MW, 0), bo_C_r2 #2 (2,622 MW, 0). Q1 base: the local
`base_case_pcm_test` run IS the no-PEM base (full year, delta
baseline of `summarize_wave.py`); no fetch needed. Q2 set: the 7
designs above plus random_C #39 (128.17 MWh) and bo_C_r1 #4 (139.63
MWh) as different-small-shed contrasts.

**Kay: run `bash fetch_runs.sh` from this directory** (override the
host with `CRC_HOST=...` if not crcfe01). It pulls only the needed
CSVs of the 15 run dirs into `runs/` (gitignored), ≈ 1.5–1.8 GB.
