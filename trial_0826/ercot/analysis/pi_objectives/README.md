# pi_objectives — ERCOT objective-selection deck (prompt 64 v1.1, 2026-11-18)

A 12-slide deck plus appendices A–F (20 slides) for the PI decision E-D1b: N1 or N4 for the N seat,
M = 3. Answer first (slide 3), evidence after, decision page on one screen (slide 11). Zero simulation.
Pattern = `analysis/pi_location/` (prompt 59). Every quoted number is read from its source file at build
time and asserted (`objective_facts.py`; 198 assertions, listed in `ASSERTIONS.md`).

## Build order

```bash
cd trial_0826/ercot/analysis/pi_objectives
/opt/anaconda3/bin/python make_objective_figs.py     # figs/: envelope, hero, relief-vs-MW, equations
/opt/anaconda3/bin/python make_objective_deck.py     # ercot_objectives.pptx + OUTLINE.md, SLIDE_TEXT.md, FIGURES_USED.md, ASSERTIONS.md
/opt/anaconda3/bin/python ~/.claude/skills/synced/*/pptx/scripts/office/validate.py ercot_objectives.pptx \
    --original "/Users/yilu/Documents/development/nd/research/admin/group_meeting/Sprint Week End June 6 2025.pptx"
```

python-pptx 1.0.2, pandas 2.3.3, matplotlib 3.10.6. Validator: "All validations PASSED!". Render check:
Codex runtime (`render.mjs`, node + `@oai/artifact-tool`), all 20 slides rendered and looked at once;
fixes applied (hero label overlaps, relief-figure annotation, footer length ≤ 112 characters asserted,
Appendix C row height, slide-7 caption spacing).

## Files

| file | content |
|---|---|
| `deck_lib.py` | byte copy of `analysis/pi_location/deck_lib.py` @ 771aa5b below a 1-line header (md5 of the copied body = source md5 850caa63…) |
| `objective_facts.py` | reads every source (prompt 64 §2), computes every printed number, asserts it against the prompt value or a text match in the source file |
| `make_objective_figs.py` | the 4 new figures; bold axis labels AND bold tick values; assert-before-draw on every plotted array |
| `make_objective_deck.py` | the deck; writes the sidecar MDs; one source line per slide (footer + notes) |
| `ercot_objectives.pptx` | the deck (ND group-meeting template, TITLE_ONLY layout) |
| `OUTLINE.md`, `SLIDE_TEXT.md`, `FIGURES_USED.md`, `ASSERTIONS.md` | slide list with source lines; full text + notes; slide → figure path + origin; assertion log |

Data state at build: `ercot/tx123` baf77c3 (includes the 62 session's screening_v3 landing e58f4bd /
1c6e73e and the Seed-bar re-grade baf77c3). Never opened: `extracts/n0_E`, `extracts/random_E`.

## Optional sources (prompt 64 §1): both present at build

- `analysis/pool/POOL_N0E_STANDINGS_seedbar.md` + `pool_ed1b_combined_seedbar.csv` (baf77c3): used for
  the hero's Seed values (N1 3.05, E9 → NOT RESPONDS), slide 3 "binding" bar, Appendix C two-bar table.
  No seat changes (asserted).
- `analysis/pool/SCREENING_V3.md` + `screening_v3_*.csv` (e58f4bd): Appendix F carries the §4.5 reads;
  one line on slide 11 (A′) and slide 12 (iv). The fallback text "analysis pending" is not used.

## Numbers NOT printed (not found in any source file)

1. Slide 11: the "< 1 day" duration of the §6.4 C2 / C3 re-derivation. Printed without a duration.
2. Slide 12: "paper sentences fixed in `waves/screening_v3/README.md`". That README holds no paper
   sentence; only `LOCATION_CONTRAST_E.md` §8 is cited.
3. Appendix F / coordinator note: the objective through which sites 116 ("via E1") and 91 ("via N1") are
   not dominated. `screening_v3_dominance.csv` gives only `margin_bars`; the margins (0.72 / 0.44 B) are printed.
4. Slide 11: "changing the vector after launch voids the HV ledger (plan §6, §10)". The plan has no such
   sentence. Printed instead: a new vector changes R (§6.3) and every HV in the ledger; §10 keeps the
   ref rule and gate numbers immutable.

## Deviations from prompt 64 (disclosed)

1. 20 slides, not 18: Appendix C (28 rows) and Appendix D (25 ids) take two slides each.
2. Slide 9: R7 and R8 share one row so the table holds 10 rows (both: dir '-', DIAGNOSTIC).
3. Hero (slide 7): open (Seed) markers for the five named ids and every id the 63 A3 table marks
   DISAGREE (N1, E9, and the undirected diagnostics V3, D1). E9's Seed value is 0 and is printed as
   "0 (Seed)" on the log axis.
4. Slide 6: "3.93–13.27× vs the 11-16 ruler" is computed from `analysis/noise_v3/ercot_noise_2026-11-16.json`
   (the pre-A1 json kept by 63) and matches PROGRESS (prompt 62). This file is not in the §2 list by name.
5. Slide 3 RTS precedent (overlap 0.988, τ 0.86–0.91) is asserted against the memory file
   `project_bogp_multipem.md` that prompt 64 names; INDEX row 28 and pi-agenda 10-06 carry the M = 3 decision only.
6. Appendix E: noise_seed_E core-h = 589.5 (json total; rows 17 / 18 ran on 8 / 1 slots), not 590.
   Total over the inventory: 5,319.9 core-h.
7. Footers abbreviate "plan AMENDMENT 2026-MM-DD" to "plan amendment MM-DD" to stay on one line; the
   speaker notes carry the full source line.
8. Slide 1 subtitle: "screening_v3 11 (landed and read)" instead of "(landed, analysis pending)".
9. Appendix A adds e58f4bd, 1c6e73e and baf77c3 (landed after prompt 64 was written).
10. `ASSERTIONS.md` is an extra output (the assertion log of the build).
