# ERCOT cost fix: T3 read-outs (prompt 36 §5)

Report only; data facts. Status 10-13: **base read done**. The B (screening)
read is limited to the wave-D input below. The C (selection) read is pending
the nuclear-row rerun (§C).

Sources: `t3_base_read.py` → `t3_base_read.json`; `wave_d_select.py` →
`wave_d_selection.json`.

- v1 = `extracts/base_2019` (cost-INVALID, kept for comparison).
- v2 = `extracts/base_2019_v2/run_index_1` (`--full`), plus replicates
  `base_2019_v2` rows 2–3 and `screening_v2/ercot` row 11.
- Curtailment is the `compute_objectives.py` true curtailment (non-PEM
  WIND + PV rows of `gen_summary`), not the `overall.csv` column. For these
  base runs, which have no PEM, the two agree to < 1e-4 MWh.

## A. Base year 2019, v1 vs v2

| quantity | v1 | v2 |
|---|---|---|
| RT LMP, bus-hour mean / median $/MWh (shortfall hours excluded) | 14.49 / 10.36 | **33.82 / 32.82** |
| DA LMP mean / median | 27.15 / 18.52 | 35.88 / 34.66 |
| system-mean hourly RT LMP p05 / p50 / p95 | 7.77 / 11.10 / 35.90 | 21.21 / 33.54 / 46.46 |
| RT bus LMP min / max | −48.0 / 682.7 | −7.6 / 446.1 |
| hourly `Price` mean; cumulative average price | 18.49; 20.68 | 20.49; 21.08 |
| total cost $ | 7.939 B | 8.091 B |
| fixed cost $ | 6.752 B | **3.631 B** |
| variable (generation) cost $ | 1.187 B | **4.460 B** |
| true curtailment MWh | 9,444,258 | **5,923,688** |
| load shed MWh | 0 | 0 |
| reserve shortfall MWh (hours) | 280.9 (7 h) | 445.9 (38 h) |
| on/offs | 17,689 | 15,957 |
| gen 1 (2,430 MW) on-hours / starts | 1,485 / 25 | **8,760 / 0** |
| gen 93 (2,708.6 MW) on-hours / starts | 0 / 0 | **8,760 / 0** |
| cost share, unit `Unit Cost` (CT / COAL / NUC) | 46.4 / 13.4 / 40.1 % | 58.4 / 32.2 / 9.4 % |

Paper Table VI: the gate's sanity envelope is $10–60/MWh. The v2 RT mean
(33.8) and median (32.8) fall inside it, and the v1 median (10.4) sits at
its floor. Table VI is not a like-for-like target; see
`data/ercot123_2019_v2/PROVENANCE.md`.

## A. Nuclear on v2 (reopens NXT-D6)

- Both nuclear units are committed for all 8,760 h with 0 starts.
- Gen 1 runs at Pmax in 8,712 h; its mean dispatch is 2,429.3 MW.
- Gen 93 runs at Pmax in 3,534 h; its mean dispatch is 2,544.9 of 2,708.6 MW.
- In v1, gen 1 cycled 25 times (1,485 h on) and gen 93 never committed.
- On v2 the nuclear units are baseload. That is the u ≡ 1 premise behind
  formulation A.

## A. Solver quality and replicates

| | v1 base | v2 (4 base runs, 1,460 RUCs) |
|---|---|---|
| RUC status | OPTIMAL 321 / TIME_LIMIT 44 | OPTIMAL 1,460 |
| final gap % p50 / p90 / max | 0.98 / 1.12 / 3.23 | 0.72 / 1.00 / 1.00 |
| recorded solve_time_s p50 / p90 / max | 107.7 / 289.4 / 605.7 | 19.8 / 27.7 / 53.4 |
| share of solves ≥ 0.98 × TL | 47.1 % | **0 %** |

- **Replicates (df = 3):** `overall.csv`, `gen_summary.csv`,
  `daily_summary.csv`, `hourly_summary.csv` and `committed_hourly.csv` are
  byte-identical across the 4 v2 base runs. The per-RUC gaps are identical
  too; only the solve times differ.
- Pairwise |Δ| is 0 for every objective (true_curt, h2, var_cost, reserve,
  onoffs, total_cost, fixed_cost). **The A ruler is 0.**
- Screening row 12 (replicate of row 1) also matches row 1 exactly
  (Δ true_curt = 0).
- TL360 Finding 1 (replicates diverging through TimeLimit races) is not
  reproduced on v2, because no RUC reaches the TimeLimit.

## Wave-D top-k rule application (§4.2)

The rule was committed in `WAVE_D_TOPK_RULE.md` (`4fb3b1f`) after B landed
at 02:30 on 10-13, before any per-site screening_v2 value was read.

**The base replicates are byte-identical, so the A ruler is 0.** The
threshold 2 × ruler is then 0, all 16 single-site rows qualify (every Δ is
nonzero), and the rule falls back to **the top 6 by rank** (relief per MW
of the screened PEM size).

| rank | row | site | type | bus | gen_pmax MW | screened PEM MW | Δ true_curt MWh | relief / MW |
|---|---|---|---|---|---|---|---|---|
| 1 | topup:2 | 163 | WIND | 120 | 185.4 | 92.7 | −356,076 | 3,841 |
| 2 | topup:5 | 140 | WIND | 2 | 250.6 | 125.3 | −454,899 | 3,631 |
| 3 | topup:4 | 146 | WIND | 75 | 268.0 | 134.0 | −480,679 | 3,587 |
| 4 | topup:1 | 270 | WIND | 120 | 579.0 | 289.5 | −1,032,882 | 3,568 |
| 5 | topup:3 | 110 | WIND | 2 | 338.6 | 169.3 | −592,888 | 3,502 |
| 6 | ercot:4 | 274 | WIND | 120 | 746.4 | 373.2 | −1,306,528 | 3,501 |
| 7 | ercot:1 | 275 | WIND | 120 | 1,039.0 | 519.5 | −1,773,674 | 3,414 |
| 8–16 | PV 116, 59, 30, 142; WIND 91, 205, 206, 204, 20 | | | | | | | 2,418 → 83 |

The full table is in `wave_d_selection.json`.

- Screening row 10 (`__ALL__`: every screened site retrofitted at once) is
  an outlier. It shows Δ true_curt = −3.75 M MWh and PEM h2 = 15.7 M MWh.
  It is not a single-site row, so it takes no part in the ranking.
- The smallest chosen `gen_pmax` is 185.4 MW (site 163), which caps the
  largest wave-D size. Sizes await Kay's confirmation; nothing is built yet.

## C. Selection (pending)

v2 nuclear rows (6–11) are being rerun after the T0 fix to the thermal
patch (initial output raised to the new p_min). The first run of rows 8–11
used T0 = 729 MW (gen 1's original p_min) and is quarantined. Rows 6–7
failed at the first RUC build on that same T0 condition. Rows 3–5 keep
their first runs.
