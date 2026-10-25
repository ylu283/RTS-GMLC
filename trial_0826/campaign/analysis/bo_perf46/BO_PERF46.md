# BO_PERF46 — BO performance at n0 = 32 (prompt 46)

Existing data only. No simulation. No GP fit. No holdout. Script:
`bo_perf46.py`. Data: four `methods_C` ledgers (d6 b0a6e1e, sync commit
4908ae9), arm waves, prompt-34 figures. All HV values come from the
ledgers. The script recomputes each round's HV
(`hypervolume_exact`, bo-gp 60e6328) and asserts that it equals the ledger value.
All asserts pass.

## 1. Per-arm result (τ-relative columns use τ_old)

| arm | starts / ref | stop | gain/τ_old r1 · r2 · r3 · r4 | overrun (post-stop) | HV/HV₀ at stop · at cap |
|---|---|---|---|---|---|
| P1 (q-ParEGO) | S1 / R_S1 | r2 (live) | 0.69 · 0.17 · 0.62 · 0.30 | r3 0.62 · r4 0.30 | 1.069 · 1.142 |
| P2 (q-ParEGO) | S2 / R_S2 | r3 | 2.28 · 0.21 · 0.40 · 0.26 | r4 0.26 | 1.138 · 1.150 |
| P3 (q-ParEGO) | S3 / R_S3 | r4 (second strike AT the cap) | 0.77 · 1.28 · 0.29 · 0.30 | none | 1.120 · 1.120 |
| N1 (qNEHVI) | S1 / R_S1 | r3 | 1.43 · 0.61 · 0.19 · 0.22 | r4 0.22 | 1.177 · 1.195 |

- Each arm: 32 starts + 4 × 8 BO = 64 evaluations at the cap.
  Evaluations at stop: P1 48 · P2 56 · P3 64 · N1 56.
- All overrun checkpoints are below τ_old. No overrun reverses its stop.
- Raw HV, with the ref label: P1 6.606e17 → 7.061e17 (stop) → 7.547e17 (cap), R_S1 ·
  N1 6.606e17 → 7.777e17 → 7.892e17, R_S1 · P2 1.573e18 → 1.789e18 →
  1.808e18, R_S2 · P3 1.562e18 → 1.750e18 (stop = cap), R_S3. Raw HV is
  comparable only within one ref (P1 vs N1). Use HV/HV₀ to compare across refs.
- Full table: `bo_perf_table.md` / `.csv`. Per-round series: `bo_perf_trajectory.csv`.

## 2. Economics (BO_STAGE2.md §front; two distinct designs)

cost endpoint r2#3 $510M (29 GWh shed, 1.26 TWh curt) vs reliability
endpoint r1#5 (zero shed, 48 GWh curt, $668M); cheapest zero-shed design
$582M.

## 3. Random baseline (prompt 34)

- Old-floor rider (verbatim): "above at both refs; NOT robust to
  floor-level output perturbation (47% of 1,000 draws keep 'above';
  threshold 80%)".
- The perturbation jointly used the ASSUMED floors 3,000 MWh / 5,000 MWh /
  $0.5M. Thus this rider is conditional on the rejected old floor.
- Measured-shed re-run (shed 285.3 MWh): prompt 45 deliverable 4.
  **NOT AVAILABLE when this pack was made.** Put it beside the old-floor
  rider when it is available.

## 4. Figures (`figs/`, .png + .pdf)

- `fig1_hv_trajectories`: 2 × 2, one panel per arm, each on its own ref.
  Top: HV. Blue = live phase. Red dashed and shaded = record-only tail.
  Dotted line = stop round. Bottom: gain/τ_old per round, with a line at
  1. The HV axis has no τ line.
- `fig1b_hv_normalized`: all arms. HV/HV₀, where each arm uses its own ref
  and HV₀ is its 32-start HV. ★ = stop round.
- `fig2_fronts`: rows P1 · P2 · P3 · N1. Columns shed–curt · shed–cost_ls ·
  curt–cost_ls. Grey = starts. Blue = live BO (≤ stop). Red ▲ =
  record-only (post-stop). Ring = member of the 3-D cap front.
  Black step = 2-D cap front. Blue dashed step = 2-D live-stop front.
  The fronts use no ref. P1 row: r2#3 and r1#5 are labeled.
- `fig3a_random_baseline_hv_band`, `fig3b_random_baseline_grand_front_unified`:
  copies of the prompt-34 `fig1_hv_band` and `fig4b_grand_front_unified`,
  not recomputed. Caption: the §3 rider, the conditionality sentence and
  the prompt-45 pointer.

## 5. Measured-noise re-grade

This pack uses τ_old only. Prompt 45 supplies the re-grade at measured noise.
This pack does not repeat it.

## 6. Deviations

1. Data sync: not run again. Commit 4908ae9 (prompt 45 §2, b0a6e1e) was
   already on `phaseb`.
2. BOGP_PATH: the default `bo-gp` checkout is on `feat/pt-system`, which
   has no `hypervolume_exact`. The script uses `bo-gp-qparego` at
   60e6328, which is the ledgers' `bo_gp_sha`. The HV is a data check only.
3. fig3 is two copied figures (3a, 3b), not one combined figure.
4. Additions: `fig1b_hv_normalized` (allowed by §3.1) and
   `bo_perf_trajectory.csv` (the per-round data for fig1).
5. Prompt-45 D4 result: open slot (§3).
