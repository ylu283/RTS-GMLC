# ERCOT overnight deck — outline (prompt 67 v1.1, 2026-11-26)

Built by `make_overnight_deck.py` on `deck_lib.py` (byte copy of pi_objectives') and the ND group-meeting template. Slides 1–12 = main (prompt 67 §1); slide 13 = Backup divider; B1–B5; Appendices A–D (B takes three slides).

## Slide list (as built, 24 slides)

| # | Title | Figures | Source line |
|---|---|---|---|
| 1 | ERCOT BO overnight: two objectives, GPs that pass the holdout, machinery that runs end to end — four decisions before the first real round | 0 | Source: committed_configs.json (n_star), design_space_E_2026-11-24.json (M); git rev-parse ercot/tx123 |
| 2 | Is the ERCOT BO ready for its first real round, and what must be decided first? | 0 | Source: admin/prompt/bogp/ercot-station-map.md (stations 3, 4, 6); admin PROGRESS 11-24 |
| 3 | Ready after four decisions: seat V1 · E1, start at n = 48 with a mixed GP fit, set the duplicate-run and replicate rules; the emulator tests machinery, not search | 0 | Source: admin PROGRESS 11-24 (verdicts); pool_ed1b_v2.csv (eta2_T, resid_IDR_over_B); EMULATOR_BO.md §A |
| 4 | The BO problem these decisions fix, and rule v2 in three lines | 9 | Source: arms_E.json, design_space_E_2026-11-24.json, landing_R.json · plan amendment 11-24 (sha256 e3712a7f…) inst. 4–6, 11-24b §1 |
| 5 | Rule v2 seats V1 and E1; N4 clears its own bar 14× but fails the composition gate (residual Mantel p 0.025 vs 0.01), so it is co-reported, not seated | 0 | Source: POOL_N0E_STANDINGS_v2.md §7–§8, pool_ed1b_v2.csv, pool_pairs_v2.csv; GP_STATUS §6a · plan amendment 11-24 |
| 6 | The house GPs pass the holdout at n = 48 (V1 45/48, E1 48/48) and no smaller tier meets the n* rule, but the capped optimizer over-states the noise 2.7–4× | 1 | Source: ERCOT_GP_STATUS.md §0, §13.2; ercot_gp_status(_v2).csv; committed_configs.json; exposure_ledger.csv |
| 7 | Fit v2 commits E1 (48/48); V1's v2 fit is 2.3× more accurate but over-confident (37/48, P = 2e-5), so V1 keeps the house fit by the pre-registered fallback | 1 | Source: ERCOT_GP_STATUS.md §0, §13, §13.1b; ercot_gp_status_v2.csv; committed_configs(_housefit).json; exposure_ledger.csv |
| 8 | The 55 machinery runs end to end on the committed GPs (12/12 single, 15/15 multi lanes, C1 45/45) and caught a bug that wrote a PEM unit at fraction 5.6e-17 | 0 | Source: EMULATOR_BO.md §A.1, §7, §8; emulator_E_summary_committed.json; emulator_E_multi_committed.csv |
| 9 | On the emulator BO matches a plug-in of the start-set GP (HV 0.971–0.980 vs 0.966); against a mismatched V1 truth it still finds the all-PEM vertex (1 seed) | 1 | Source: emulator_E_{multi,single}_committed.csv, summary_committed, EMU_extras_committed.json; EMULATOR_BO.md §A.2–A.5 |
| 10 | The calibration gates cannot see a V1 misfit (house bands ≈ 6× too wide); the one E1 flag came at a replicated design, where fit v2 under-estimates the noise (0.31–0.99× actual) | 1 | Source: EMULATOR_BO.md §A.0, §A.3; emulator_E_single_committed.csv; emulator_E_summary_committed.json |
| 11 | Seed lanes converge on box vertices: 16 of 40 round-1 PCM runs would repeat another lane's design — reuse by design key, or run all and disclose | 0 | Source: runs_compact/EMU_extras_committed.json (seed_overlap); EMULATOR_BO.md §A.4; pi-agenda E-D4 · plan amendment 11-14 |
| 12 | Four decisions unlock round 1; the first two need no new runs, the third avoids up to ≈ 720 core-h | 0 | Source: pi-agenda 11-24 rows; pi_agenda_E-D7_draft.md; EMULATOR_BO.md §A.7, §8; PROGRESS Prompt 66 |
| 13 | Backup slides B1–B5 and Appendices A–D | 0 |  |
| 14 | Training-size study under fit v2: LOO RMSE, NLPD, coverage and inferred noise still move from 44 to 48 | 1 | Source: ercot_gp_nstar_checks_v2.csv, ercot_gp_status_v2.csv, ERCOT_GP_STATUS.md §13 |
| 15 | RTS 49 V1 arm (cap 4, 64 designs): the old-floor τ stops at rounds 3–4, the measured rulers never do, and the gains are not monotone (r4 > r3) | 0 | Source: RTS-GMLC campaign/analysis/methods_C/V1/ledger.json (d6 8ed4c01) |
| 16 | What blocks round 1: the 55 Part B checklist (13 items; blocking ones marked) | 0 | Source: EMULATOR_BO.md §8, §A.6–A.7; committed_configs.json |
| 17 | House-fit emulator block: the same machinery on the unconverged GPs — superseded items marked | 0 | Source: emulator_E_summary.json, runs_compact/EMU_extras.json, EMU_rerun_check.json (house); EMULATOR_BO.md §B |
| 18 | Figures not shown | 0 | Source: analysis/ercot_gp/figs/, analysis/emulator_E/figs/ (paths below) |
| 19 | Appendix A: process log — step · SHA · time (git log --format=%ai) · verdict | 0 | Source: git log --format=%ai on ercot/tx123 and d6; verdicts: admin PROGRESS 11-24 (acceptance reviews) |
| 20 | Appendix B (1/3): full rule-v2 standings, walk order (28 rows) | 0 | Source: analysis/pool/pool_ed1b_v2.csv · plan amendment 11-24 |
| 21 | Appendix B (2/3): full rule-v2 standings, walk order (28 rows) | 0 | Source: analysis/pool/pool_ed1b_v2.csv · plan amendment 11-24 |
| 22 | Appendix B (3/3): the bar Bj, the materiality floors, and the N4 counterfactual | 0 | Source: plan AMENDMENT 2026-11-24 inst. 1, 5, 6; pool_ed1b_v2.csv; pool_pairs_v2.csv; pool_n0E_v2.steiger · plan amendment 11-24 |
| 23 | Appendix C: emulator matched-budget baselines at r4 under three truths (committed / mismatch A / mismatch B) | 0 | Source: EMU_extras_{committed,mmA,mmB}.json (baselines, r4); emulator_E_multi_committed.csv (s0 seed 0, r4) |
| 24 | Appendix D: the two GP fit definitions in use | 0 | Source: committed_configs.json (fit_v2_spec); EMULATOR_BO.md §1; arms_E.json gp.train |
