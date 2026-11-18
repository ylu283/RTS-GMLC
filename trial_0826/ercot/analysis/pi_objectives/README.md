# pi_objectives — ERCOT objective-selection deck (prompt 64 v1.1, 2026-11-18)

A 12-slide deck plus appendices A–F (20 slides) for the PI decision E-D1b: N1 or N4 for the N seat,
M = 3. Answer first (slide 3), evidence after, decision page on one screen (slide 11). Zero simulation.
Pattern = `analysis/pi_location/` (prompt 59). Every quoted number is read from its source file at build
time and asserted (`objective_facts.py`; 214 assertions, listed in `ASSERTIONS.md`).

15-minute path: slides 1, 2, 3, 7, 8, 11, 12 plus the N1 / N4 rows of Appendix F (slide 20). The rest is backup.

## Build order

```bash
cd trial_0826/ercot/analysis/pi_objectives
/opt/anaconda3/bin/python make_objective_figs.py     # figs/: envelope, hero, relief-vs-MW, equations, 5x5 rho, screening HL
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
| `external_snippets.json` | the asserted text snippets of the three files OUTSIDE the repo (`admin/prompt/bogp/pi-agenda.md`, `INDEX.md`, the memory file `project_bogp_multipem.md`), frozen at the first build. The build asserts against this frozen copy, so a later edit of those files cannot break the rebuild; a live mismatch is only listed in `objective_facts.WARNINGS` |
| `make_objective_figs.py` | the 6 new figures; bold axis labels AND bold tick values; assert-before-draw on every plotted array |
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
3. Slide 11: "changing the vector after launch voids the HV ledger (plan §6, §10)". The plan has no such
   sentence. Printed instead: a new vector changes R (§6.3) and every HV in the ledger; §10 keeps the
   ref rule and gate numbers immutable.

Removed from this list in the review round: "116 on E1 / 91 on N1" is in plan AMENDMENT 2026-11-18
(screening_v3) and is now printed on Appendix F with that source.

## Ruler names (one term per concept)

- "median ruler" = `ercot_noise.json` `per_candidate.<j>.ruler` (D2 excluded; R4 28.5, N1 23.5).
- "11-16 median ruler" = `ercot_noise_2026-11-16.json` ruler (all 8 copies; R4 20, N1 15). `pool_standings.csv`
  (written at d6a8933) uses this one; asserted. Appendix B's first column is therefore "range / 11-16 median ruler".

## Review round (second commit): three reviews, all items applied

B1 ruler names (Appendix B column and bullet, slide 6); B2 slide 10 title / bullets / 0.787; B3 slide 1 title + footer;
B4 slide 3 title, "spread" header + footnote, R4 cell / bullet, launch-readiness bullet; B5 slide 11 title, A′ as a
disclosed post-hoc PI override (no new threshold rule), A′ body, A risk (N1 bar = 33 % of its spread), headroom sentence;
B6 "shifts consistently with site class" wording (slides 11, 12, 20), 3 sites in neither class, site-mix wording on
slides 8 and 12; B7 one A3 sentence (slides 6, 12, 18), "gradable" column on Appendix D, hero caption; B8 "option C"
disambiguated. S1 slide 5 title; S2 R7 / R8 row and N1 reason; S3 R4 reason untruncated, engineering units on slides
17–18 and τ_res, real sub/superscript runs for B_j, B^seed, σ̂_c, τ_res, H_C (post-pass `scripts_pass`; footers and notes
untouched), slide 6 header on one line; S4 five sessions, d6a8933; S5 hero legend swatches neutral (family X recoloured
orange), labels 2 decimals, N4 Seed label moved; S6 slide 8 = one 5 × 5 matrix (upper raw, lower residual, 18 pt cells,
N1–N4 boxed), full clustermap path in the notes; S7 relief figure: own markers for the 500 MW rows, 800 MW markers offset,
larger legend; S8 screening bar chart rebuilt here with N1 / N4 annotated; S9 figure paths in the notes only; S10 printed;
S11 15-minute path + 7 listener sentences in the notes ("Say: …"); S12 `external_snippets.json`.

## Deviations from prompt 64 (disclosed)

1. 20 slides, not 18: Appendix C (28 rows) and Appendix D (25 ids) take two slides each.
2. Slide 9: R7 and R8 share one row so the table holds 10 rows (both: dir '-', DIAGNOSTIC).
3. Hero (slide 7): open (Seed) markers for the five named ids, the gradable A3-DISAGREE ids N1 and E9,
   and the non-gradable V3 and D1. E9's Seed value is 0 and is printed as "0 (Seed)" on the log axis.
4. Slide 6: "3.93–13.27× vs the 11-16 ruler" is computed from `analysis/noise_v3/ercot_noise_2026-11-16.json`
   (the pre-A1 json kept by 63) and matches PROGRESS (prompt 62). This file is not in the §2 list by name.
5. Slide 3 RTS precedent (overlap 0.988, τ 0.86–0.91) is asserted against the memory file
   `project_bogp_multipem.md` that prompt 64 names; INDEX row 28 and pi-agenda 10-06 carry the M = 3 decision only.
6. Appendix E: noise_seed_E core-h = 589.5 (json total; rows 17 / 18 ran on 8 / 1 slots), not 590.
   Total over the inventory: 5,319.9 core-h.
7. Footers abbreviate "plan AMENDMENT 2026-MM-DD" to "plan amendment MM-DD" to stay on one line; the
   speaker notes carry the full source line.
8. Slide 1 subtitle: "screening_v3 11 (landed and read)" instead of "(landed, analysis pending)".
9. Appendix A adds e58f4bd, 1c6e73e and baf77c3 (landed after prompt 64 was written) and d6a8933 (the 54 outputs).
11. Slide 8 shows a 5 × 5 subset instead of the full clustermap (review S6); slide 20's bar chart is rebuilt from
    `screening_v3_locational.csv` instead of reusing the 62 session's PNG (review S8).
10. `ASSERTIONS.md` is an extra output (the assertion log of the build).
