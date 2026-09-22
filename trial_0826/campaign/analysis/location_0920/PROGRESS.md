# Location analysis PROGRESS (prompt 28)

Updated at session boundaries; a re-invoked session resumes from here.
Workspace: main clone, branch `d6` (never switch). Session lock protocol:
`trial_0826/campaign/.session.lock` = `28` per invocation, removed on close
including error paths.

## State

- [x] **T1 machinery (2026-09-20, commit `5012a97`)** — `build_pairgrid`
  over `STAGE2_LATTICE × STAGE2_LATTICE` (sorted-first tier outer,
  others-absent, ρ=2.0 → derived bids 40); `write_wave(manifest_extra=…)`
  carries `pair` + `lattice` in the manifest (pair identity is read from
  the manifest, never the dir name); `submit_array.generate_script(
  max_concurrent=None)` omits `-tc`; `make_batches.py all` now REFUSED;
  per-wave `submit_this.sh` + single-wave collector (pairgrid-bot, push
  retry loop ×5 with randomized backoff) generated with each wave.
  Tests: `tests/test_pairgrid.py`, suite green (70 passed, 1 pre-existing
  skip).
- [x] **T1 waves (commit `40e24c4`)** — all 14 `pairgrid_*_C` dirs
  (81 rows each; wind_303×wind_317 NOT built — `contour_303x317_C` is that
  pair, allclose-equivalence recorded in LOCATION.md provenance).
  Manifests show `dirty: true` only because of a concurrent session's
  uncommitted `gm_0829` edits in the shared checkout; generator code was
  fully committed.
- [x] **T1.5 OAT preliminary** — `oat_preliminary.ipynb` executed +
  `LOCATION.md` v0 + `figs/` + `oat_*.csv`. Headline: curtailment/cost
  location-sensitive (L/floor_L median 7–9×), load shed below its 6-draw
  range floor (0.5–0.6×, borderline band), reserve 9/15 pairs by
  range-and-replication, starts 6/15. `stage2_backfill_C` had NOT landed
  → C nuclear/pv curves truncated (old level set); fold in on re-run when
  it lands.
- [x] **Priority submission + returns (09-21/22).** All 3 priority pair
  grids ran and collected clean: pairgrid-bot pushes `8579cc5`
  (nuclear_wind_317), `5bfd4a6` (nuclear_pv), `738b201` (pv_tail) —
  81/81 each, no FAILED markers, collectors first-pass.
- [x] **T2 (2026-09-22)** — `pair_apparatus.ipynb` executed on the 3 new
  pairs + `contour_303x317_C` (pinned estimators; wind-pair ω rounded to
  10 decimals before the join). Outputs: `pair_verdict_stats.csv`,
  `pair_gp_gate.csv`, `pair_isototal_reads.csv`,
  `pair_edge_consistency.csv`, `pool26_total_vs_allocation.csv`,
  `pooled_kendall_tau.csv`, `drop_one_pareto.csv`, `t2_summary.json`,
  `figs/pair_*_8c.png`. **LOCATION.md v1** shipped (v0 in appendix with
  deltas) + **draft M = {shed, curtailment, cost_less_synthetic}** +
  plain summary. Headlines: curtailment/cost location-sensitive in all
  4 pairs (gates 1.9–30.5× floor); shed verdict CHANGED to tilt-only
  (317 ≈ 1.8× nuclear per MW, replicated; magnitude sub-floor); GP gate
  fails for curtailment everywhere (along-line reads suppressed); cost
  vs reliability τ flips to −0.6 pooled (19b prior reverses — MOBO
  necessity); 13/32 edge flags, characterized benign. OAT preliminary
  re-executed with backfill folded (window [42.4, 251.5]).
- [ ] Remaining 11 waves: Kay staggers per `SUBMIT_QUEUE.md` (fire-and-
  forget; ~790 core-h each). **Kay 09-21: n0b top-up build is GO but
  submits only AFTER these 3 priority pairs — that condition is now MET;
  n0b build/submission is queued work for a stage2 session (skip =
  n_drawn_total = 16, new wave dir).**

## Re-invocation routing

1. `git pull` first. Then check `waves/pairgrid_*/objectives.csv`:
   - any of the 3 priority pairs present → **T2**: pair-generic apparatus
     (8c panels, pinned interaction index I_raw/I_rel, tilt with CI,
     GP along-line reads gated by LOOCV RMSE ≤ floor — floorless
     objectives get raw-81-point statistics only) on the landed pairs +
     `contour_303x317_C` (remember the round-to-10-decimals ω join rule)
     → LOCATION.md v1 + draft M recommendation. M does NOT wait for all 15.
   - additional non-priority pairs present → **T3**: same pipeline mapped
     over each, append to the atlas; final 15-pair atlas + final verdict
     table + M memo revision when the last pair lands. Never block on
     stragglers — report which are outstanding and proceed.
2. Any `FAILED_pairgrid_*.md` in a wave dir → report it and stop that
   wave's analysis (Kay recovers via resubmit_missing.py / manual qsub).
3. If `stage2_backfill_C/objectives.csv` has landed → re-execute
   `oat_preliminary.ipynb` (it folds the rows in automatically and the
   truncation flags clear; window widens to ~[42.4, 251.5] MW).
4. If `stage2_C_n0/objectives.csv` exists at T2 time → run the
   pre-registered EXPLORATORY pooled 26-point f(total)-vs-f(allocation)
   LOO check (small-n caveat); skip with a note if absent.

## Key facts for the resuming session

- Priority pairs + rationale: nuclear×wind_317 (max type contrast, first
  2-D nuclear ω>0.5 data), pv×tail (two newly-full-range tiers),
  nuclear×pv (both newly at ω=1.0).
- Noise floors (pi_0911 §3.5 canonical): shed 3,000 / curtailment 5,000
  MWh / cost $0.5M; reserve + starts have NO floor (D3 open). Range-floor
  MC factors (seed 20260920): n=6 → 4.04σ, n=2 → 2.79σ.
- Nuclear rows carry the g1 fuel-deletion APPROX caveat in every caption
  (patch pending PI review — do NOT implement).
- GP reference: `analysis/bo_replay/replay.py:182-199` (Matérn-2.5 ARD,
  per-fold standardization). House style: bold axes.
- Frozen: existing `waves/*/design_matrix.csv`, `objectives.csv`, raw
  runs; stage2 scripts (hand-stripped `-tc` — never regenerate them).
