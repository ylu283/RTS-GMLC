# pi_overnight_1124 — ERCOT overnight-results deck for the 1-on-1 (prompt 67 v1.1, 2026-11-26)

A 24-slide deck for Kay's 1-on-1 with the PI: what the overnight pipeline (65 → 54 → 66) produced, what it proved
and did not prove, and the four decisions for today. 12 main slides (answer first on slide 3, one decision page on
slide 12), a Backup divider, backups B1–B5 and Appendices A–D (B takes three slides). Zero simulation. Pattern =
`analysis/pi_objectives/` (prompt 64). Every quoted number is read from its source file at build time and asserted
(`overnight_facts.py`; the full log is `ASSERTIONS.md`).

## Build order

```bash
cd trial_0826/ercot/analysis/pi_overnight_1124
/opt/anaconda3/bin/python make_overnight_figs.py     # figs/: 5 byte-copied figures + 9 equation PNGs (mathtext)
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
| `make_overnight_figs.py` | copies the five committed figures byte for byte; renders the slide-4 equations with the pre_can mathtext recipe (that file is not modified); no new data figures |
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

1. Slide 11: the house-block parenthetical "(house block 23 / 36 / 31 / 35)" is moved to backup B4. The build rule
   for this deck allows house-block numbers only on B4.
2. 24 slides: Appendix B takes three slides (28 standings rows on two, the bar / floors / counterfactual on the third).
3. Verbatim titles with rounded numbers; the body prints the source value:
   - slide 6 "2.7–4×": inferred noise / σ_c is 2.646 (E1) and 3.968 (V1); the body prints 2.65 / 3.97.
   - slide 8 "5.6e-17": the source value is 5.55e-17 (EMULATOR_BO.md §7); the body prints 5.55e-17.
   - slide 12 "≈ 720 core-h": 16 runs × 45 core-h (pi-agenda E-D4 row, asserted); the plan's wave-D maximum is
     44.6 core-h per run (16 × 44.6 = 714). The n0_E landing actuals (19–39.4 core-h, plan AMENDMENT 2026-11-16)
     would give a lower range; not printed.
4. Slide 6: the like-for-like ratios are printed as 1.255–1.285 (the source text, 3 decimals), not "1.25–1.29".
5. Slide 7: LOO NLPD is printed with 3 decimals (10.795 / 11.733; 15.805 / 16.252), as in the source.
6. Slide 5 physics line uses the reviewer's wording ("the cost of diverted deliverable wind, which E1 already
   prices"), asserted in admin PROGRESS 11-24, instead of "withheld wind".
7. Slide 12, row 4 (55 Part B bundle): the "Recommend: approve all four" and "Changes it: a flag on any line" text
   is the deck's procedure for a line-by-line bundle, not a file statement (stated in the notes).
8. Backup B3: the DONE marks come from EMULATOR_BO.md §A.6–A.7 and committed_configs.json; "BLOCKS" marks every open
   item that must close before round 1 is submitted; item 9 (stale text) is marked "open".
9. Slide 4: the equations are one PNG per line at one common scale; the decision tags are text boxes beside the lines.
   ε is written as "solver seed chatter Σ_c" (EMULATOR_BO.md §1).
10. Appendix A lists 19 tx123 commits plus RTS 8ed4c01 (times from `git log --format=%ai`).
