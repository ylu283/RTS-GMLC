# ERCOT objective-selection deck — outline (prompt 64 v1.1, 2026-11-18)

Built by `make_objective_deck.py` on `deck_lib.py` (copy of pi_location's) and the ND group-meeting template. Slides 1–12 follow prompt 64 §1; appendices A–F follow (C and D take two slides each).

## 15-minute path

Slides 1, 2, 3, 7, 8, 11, 12, plus the N1 / N4 rows of Appendix F (slide 20). The other slides are backup.

## Slide list (as built, 20 slides)

| # | Title | Figures | Source line |
|---|---|---|---|
| 1 | Choosing the ERCOT objectives: V1 and E1 are firm, the R seat stays empty, the N seat is a PI choice (M = 3; strategy recommends N4) | 0 | Source: waves/{location_oat_v2,n0_E,location_contrast_E,noise_seed_E,screening_v3}/design_matrix.csv; git rev-parse ercot/tx123 |
| 2 | The question: which three or four objectives should the ERCOT BO optimize, and is the evidence strong enough to launch? | 0 | Source: analysis/pool/pool_n0E_standings.csv, POOL_N0E_STANDINGS.md · plan amendment 11-06, 11-17 |
| 3 | Proposal: optimize curtailment (V1), cost (E1) and pocket congestion (N4, recommended over N1); leave the reliability seat empty (M = 3) | 0 | Source: pool_ed1b_combined(_seedbar).csv, ercot_noise_seed.csv, pi-agenda · plan amendment 11-17, 11-18 |
| 4 | Why the earlier evidence was not enough: wave D moves one site at ≤ 180 MW; the BO moves six sites at 679–1,863 MW | 1 | Source: waves/{location_oat_v2,n0_E}/design_matrix.csv, cost_fix/wave_d_selection.json · plan amendment 11-06b |
| 5 | The seat rules were frozen before any grading statistic (spread, rank correlation) was computed; ideal, nadir and the reference point over the 48 rows had been seen (disclosed) | 1 | Source: POOL_N0E_STANDINGS.md (block sha256 8dd06917…) · plan amendment 11-17 |
| 6 | The ruler: the run repeats bit-for-bit at fixed Threads and platform, but a 0.1 % input change moves 350–365 of 365 RUC days; Seed replicates agree with that ruler within 2× on 20 of 22 candidates | 0 | Source: ERCOT_NOISE.md §10–11, ercot_noise_daily_divergence.csv, NOISE_SEED_E.md §2/§4 · plan amendment 11-18 |
| 7 | On the BO's own space, V1 and E1 respond 93× and 14× the bar; N4 17× (14× Seed); N1 6.4× perturbed but 3.05× on its Seed bar; R4 2.1× (1.1× Seed) | 1 | Source: pool_n0E_standings.csv, pool_ed1b_combined_seedbar.csv, ercot_noise_seed.csv · plan amendment 11-18 |
| 8 | Redundancy after removing the total-MW trend: CO₂ collapses into cost, penetration into consumer payments; N4 is not a copy of N1 | 1 | Source: pool_spearman_n0E_{raw,resid}.csv, POOL_N0E_STANDINGS.md §3–§4 · plan amendment 11-17 |
| 9 | Result of the pre-registered walk: V1, E1 and N1 seated, R seat empty (M = 3); N4 stands further above its bar but ranks behind N1 in the frozen order | 0 | Source: POOL_N0E_STANDINGS.md §E, pool_ed1b_combined.csv · plan amendment 11-17 |
| 10 | Location contrast (9 runs): relief is additive within 10 % up to 120 MW per site and sub-additive at 180; at matched total MW a residual of 2.9–6.7 bars is not explained by host-absorbable energy — no network effect is claimed | 1 | Source: location_contrast_E.csv, LOCATION_CONTRAST_E.md §3–§5, §7 · plan amendment 11-17c |
| 11 | Decide today (E-D1b): (1) N1 or N4 for the congestion seat, (2) approve M = 3. Strategy recommends A′ (N4). | 0 | Source: pi-agenda E-D1b (11-17/18), NOISE_SEED_E.md §5, SCREENING_V3.md · plan amendment 11-16, 11-17b, 11-18 |
| 12 | Discussion: what this shows and does not show; next | 0 | Source: POOL_N0E_STANDINGS, ERCOT_NOISE §12, SCREENING_V3.md, LOCATION_CONTRAST_E.md · plan amendment 11-16…18 |
| 13 | Appendix A: process flow — five sessions, each step committed before the next read | 0 | Source: git log (SHAs below), PROGRESS.md, ERCOT_POOL_STANDINGS.md RERUN · plan amendment 11-17 … 11-18 |
| 14 | Appendix B: wave D under both rulers — R4 and N1 read 4.9–13.5× the 11-16 median ruler but ≤ 1.84× the bar Bj | 0 | Source: pool_standings.csv, pool_ed1b_combined.csv (waveD_range_over_B) · plan amendment 11-17 |
| 15 | Appendix C (1/2): full E-D1b table — both bars side by side (binding bar per the Seed re-grade) | 0 | Source: pool_ed1b_combined.csv, pool_ed1b_combined_seedbar.csv · plan amendment 11-17, 11-18 |
| 16 | Appendix C (2/2): full E-D1b table — both bars side by side (binding bar per the Seed re-grade) | 0 | Source: pool_ed1b_combined.csv, pool_ed1b_combined_seedbar.csv · plan amendment 11-17, 11-18 |
| 17 | Appendix D (1/2): bars for every id — perturbed Bj (D2 excluded) vs Seed Bseed; A3 verdict | 0 | Source: ercot_noise_seed.csv, NOISE_SEED_E.md §2 · plan amendment 11-18 |
| 18 | Appendix D (2/2): bars for every id — perturbed Bj (D2 excluded) vs Seed Bseed; A3 verdict | 0 | Source: ercot_noise_seed.csv, NOISE_SEED_E.md §2 · plan amendment 11-18 |
| 19 | Appendix E: run inventory and core-hours — 5.3k core-h of evidence behind this selection | 0 | Source: extracts/*/wallclock.csv (× 4 slots), ercot_noise_seed.json · plan amendment 11-14 … 11-18 |
| 20 | Appendix F: screening_v3 (16 sites, 180 MW) — V1, E1 and N4 shift consistently with site class; N1 shifts as much but not consistently; the slate bus set holds | 1 | Source: SCREENING_V3.md, screening_v3_{locational,ranking,dominance,sites}.csv · plan amendment 11-18 |
