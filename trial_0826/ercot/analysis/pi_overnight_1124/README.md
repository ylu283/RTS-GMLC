# pi_overnight_1124 — ERCOT overnight-results deck for the 1-on-1 (prompt 67 v1.1, 2026-11-26)

A 25-slide deck for Kay's 1-on-1 with the PI: what the overnight pipeline (65 → 54 → 66) produced, what it proved
and did not prove, and the four decisions for today. 11 main slides (answer first on slide 2, one decision page on
slide 11), a Backup divider, backups B0 (station map), B1 (two slides), B2–B5 and Appendices A–D (B takes three
slides). Titles: prompt 67 v1.1, superseded on slides 2, 3, 5, 7, 8, 9, 11 by the review round (coordinator, 2026-11-26). Zero simulation. Pattern =
`analysis/pi_objectives/` (prompt 64). Every quoted number is read from its source file at build time and asserted
(`overnight_facts.py`; the full log is `ASSERTIONS.md`).

## Build order

```bash
cd trial_0826/ercot/analysis/pi_overnight_1124
/opt/anaconda3/bin/python make_overnight_figs.py     # figs/: 5 byte copies, 3 crops of them, 1 re-rendered HV figure, 9 equation PNGs
/opt/anaconda3/bin/python make_overnight_deck.py     # ercot_overnight.pptx + OUTLINE.md, SLIDE_TEXT.md, FIGURES_USED.md, ASSERTIONS.md
/opt/anaconda3/bin/python ~/.claude/skills/synced/*/pptx/scripts/office/validate.py ercot_overnight.pptx \
    --original "/Users/yilu/Documents/development/nd/research/admin/group_meeting/Sprint Week End June 6 2025.pptx"
```

python-pptx 1.0.2 (/opt/anaconda3). Validator: "All validations PASSED!". Render check: Codex runtime
(`render.mjs` + node + `@oai/artifact-tool`), all slides rendered and looked at once.

## Files

| file | content |
|---|---|
| `deck_lib.py` | byte copy of `analysis/pi_objectives/deck_lib.py` @ 170cf86 below a 1-line header (md5 of the body = source md5 6c6b8b60…) |
| `overnight_facts.py` | reads every source (prompt 67 §2), computes every printed number, asserts it against the prompt value or a text match in the source; recomputes the Appendix B Steiger Z with `analysis/pool/pool_n0E_v2.py`'s `steiger` (imported, the walk is not re-run) |
| `external_snippets.json` | asserted text snippets of the files OUTSIDE the repo (admin `PROGRESS.md` — reviewer statements only —, `pi-agenda.md`, `ercot-station-map.md`), frozen at the first build; a later edit of those files cannot break the rebuild |
| `make_overnight_figs.py` | copies five committed figures byte for byte; crops three panels from them (parity V1/E1; training-size curves split in two); re-renders the slide-8 HV figure from the committed csv/json with 5 legend entries (bold labels and ticks, assert-before-draw); renders the slide-3 equations with the pre_can mathtext recipe (that file is not modified) |
| `make_overnight_deck.py` | the deck and the sidecar MDs; one source line per slide (footer + notes) |
| `ercot_overnight.pptx` | the deck (ND group-meeting template, TITLE_ONLY layout) |
| `OUTLINE.md`, `SLIDE_TEXT.md`, `FIGURES_USED.md`, `ASSERTIONS.md` | slide list with source lines; full text + notes; slide → figure + source commit; assertion log |

Data state at build: `ercot/tx123` de45242; RTS `d6` 8ed4c01 (ledger read with `git show`). Never opened:
`extracts/n0_E`, `extracts/random_E`. No PCM, no qsub, no push.

## Block discipline

Slides 8–11 and Appendix C read only the committed emulator block (`*_committed.csv/json`,
`runs_compact/EMU_extras_committed.json`; Appendix C adds `EMU_extras_mmA/mmB.json`). The house block
(`emulator_E_summary.json`, `runs_compact/EMU_extras.json`, `EMU_rerun_check.json`) is read only for backup B4.

## Numbers NOT printed (not found in any source file)

1. Appendix B: the bin-sensitivity line of the N4 counterfactual (no file holds it; dropped as prompt 67 says).

Nothing else was dropped. Every other prompt-67 number was found and asserted (see the rounding notes below).

## Deviations from prompt 67 v1.1 (disclosed)

Slide numbers below refer to the review-round deck (main = 11 slides).

1. Slide 10: the house-block parenthetical "(house block 23 / 36 / 31 / 35)" is moved to backup B4. The build rule
   for this deck allows house-block numbers only on B4.
2. 25 slides: B1 takes two slides; Appendix B takes three slides (28 standings rows on two, the bar / floors / counterfactual on the third).
3. Verbatim titles with rounded numbers; the body prints the source value:
   - slide 5 bullet "2.7–4×": inferred noise / σ_c is 2.646 (E1) and 3.968 (V1); the bullet prints 2.65 / 3.97.
   - slide 11 "≈ 720 core-h": 16 runs × 45 core-h (pi-agenda E-D4 row, asserted); the plan's wave-D maximum is
     44.6 core-h per run (16 × 44.6 = 714). The n0_E landing actuals (19–39.4 core-h, plan AMENDMENT 2026-11-16)
     would give a lower range; not printed.
4. Slide 5: the like-for-like ratios are printed as 1.255–1.285 (the source text, 3 decimals), not "1.25–1.29".
5. Slide 6: LOO NLPD is printed with 3 decimals (10.795 / 11.733; 15.805 / 16.252), as in the source.
6. Slide 4 physics line uses the reviewer's wording ("the cost of diverted deliverable wind, which E1 already
   prices"), asserted in admin PROGRESS 11-24, instead of "withheld wind".
7. Slide 11: every "Recommend" line is Kay's recommendation (no file holds it as a decision; the notes say so).
   Row 4 adds line (5), the round-1 model-review trigger of slide 9 (a proposal, not a file rule). Slide 6
   "Proposal" line (linear mean for V1) is Kay's recommendation, not a file statement.
8. Backup B3: 13 items of EMULATOR_BO.md §8 (3 done, 10 open, 9 blocking) plus one report-only item from
   ERCOT_GP_STATUS.md §0 (open, non-blocking). The DONE marks come from EMULATOR_BO.md §A.6–A.7 and committed_configs.json; "BLOCKS" marks every open
   item that must close before round 1 is submitted; item 9 (stale text) is marked "open".
9. Slide 3: the equations are one PNG per line at one common scale; the decision tags are text boxes beside the lines.
   ε is written as "solver seed chatter Σ_c" (EMULATOR_BO.md §1).
10. Appendix A lists 20 tx123 commits plus RTS 8ed4c01, sorted by author time (`git log --format=%ai`);
    eb8c2da was rebased (committed 03:22).
11. Slide 8 shows a re-render of the committed HV figure with 5 legend entries (committed truth only: uniform and
    vertex bands, the r0 plug-in front, s0 and s1 lanes); the full figure is listed on B5.
12. Slide 3 "ACCEPT WITH NOTES ×3" chip for 66 = BO stats + machinery + the committed rerun (audience: FIX THEN SHIP).

## Render round (second commit)

All 24 slides rendered with the Codex runtime and looked at once. Fixes: slide 6 figure full width with the bullets in
two columns below; slide 4 rule block moved up (clear of the footer); slides 8 and 10 side cards shortened; B1
figure enlarged; B2 HV / gain in × 10ⁿ form and gain/τ_285 with 2 decimals; B3 item 1 wording (its open test is item
11); Appendix B full role / status strings (no truncation), B_j in k / M form, unbulleted headings, true minus signs;
Appendix D unbulleted. No number changed.

## Review round (third commit; coordinator's consolidated list from three reviews, 2026-11-26)

Applied in one round: four corrections (Appendix B "global order"; Appendix A adds 65179e1 and sorts by author time;
"13 items: 3 done, 10 open (9 blocking)"; house fit = float32 in 54, float64 SingleTaskGP in 55); new verbatim
titles on slides 2, 3, 5, 7, 8, 9, 11; the station map moved to backup B0 (main deck = 11 slides); slide-by-slide
layout and wording (larger fonts, slide 5 crop, slide 6 table to 5 rows, slide 8 re-render, slide 11 boxes, B1
split); QA asserts (rule thresholds from `pool_n0E_v2` constants + plan text; tx123 == de45242; budget 160 from
arms_E.json; RuntimeError instead of assert in `near` / `text_has`). No other number changed. The QA reviewer's
sentence-level STE-100 rewrite list was not in the message; an own STE-100 pass was applied to slides 7, 8, 9,
11 and Appendix B.
