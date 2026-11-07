# pi_location — ERCOT wave-D location deck (prompt 59, draft v1, 2026-11-07)

A 12-slide read of "does location matter in ERCOT?" on wave D (6 WIND sites × 60 / 120 / 180 MW,
nuclear gen 1 overlay), built on the RTS `pi_1008` deck pattern (slides 8–14: design → method →
OAT curves → spread ratio → variance explained → atlas → evidence) plus two appendices. No PCM run,
no CRC access. Every number comes from `analysis/pool/` (prompt 57 Part B standings) or the files
named in each slide's speaker notes.

## Build order

```bash
cd trial_0826/ercot/analysis/pi_location
/opt/anaconda3/bin/python make_location_figs.py      # figs/oat_curves_ercot.png, sprime_bars.png, ancova_ercot.png, ancova_ercot.csv
/opt/anaconda3/bin/python make_location_deck.py      # ercot_location.pptx + OUTLINE.md, SLIDE_TEXT.md, FIGURES_USED.md
/opt/anaconda3/bin/python ~/.claude/skills/synced/*/pptx/scripts/office/validate.py ercot_location.pptx \
    --original "/Users/yilu/Documents/development/nd/research/admin/group_meeting/Sprint Week End June 6 2025.pptx"
```

python-pptx 1.0.2, pandas 2.3.3, matplotlib 3.10.6. Validator: "All validations PASSED!".

## Files

| file | content |
|---|---|
| `deck_lib.py` | COPY of `RTS-GMLC/trial_0826/campaign/analysis/pi_1008/deck_lib.py`, unchanged below a 2-line header (the source is untracked in that repo; working tree at HEAD 8a40ae8; md5 in the header) |
| `make_location_figs.py` | the three NEW figures from the pool CSVs; site colours fixed once (`SITE_COLORS`, Okabe-Ito; nuclear dashed black); bold axis + tick labels, ticks ≥ 14 pt; ANCOVA table |
| `make_location_deck.py` | the deck (24 slides: 12 main + 11 appendix A + 1 appendix B); writes the three sidecar MDs |
| `figs/` | generated figures + `ancova_ercot.csv` |
| `ercot_location.pptx` | the deck (ND group-meeting template, TITLE_ONLY layout; footer `ERCOT wave D · location read · draft v1 · 2026-11-07`) |
| `OUTLINE.md`, `SLIDE_TEXT.md`, `FIGURES_USED.md` | slide list, full slide text + notes, slide → figure path |

Template: `admin/group_meeting/Sprint Week End June 6 2025.pptx`. Source commit of the data:
`ercot/tx123` HEAD 9cb1aac (pool standings, prompt 57B); definitions frozen at f76d897.

## Sources per slide (also in the speaker notes)

| slide | source |
|---|---|
| 1 title | `ERCOT_POOL_STANDINGS.md` header, §8 |
| 2 question | RTS `pi_1008/v1/SLIDE_TEXT.md` slides 8, 9, 13 (left); standings header + honesty clause (right) |
| 3 design | `pool_wavedD_wide.csv`, `data/ercot123_2019_v2/bus.csv`, `analysis/cost_fix/wave_d_selection.json`, `WAVE_D_TOPK_RULE.md`, `waves/GAP_DECISION.json` |
| 4 method | standings §0.2, §1, §2, §4, honesty clause |
| 5 OAT curves | `figs/oat_curves_ercot.png` ← `pool_standings_levels.csv` + `pool_wavedD_wide.csv` rows 19–21 |
| 6 S′ | `figs/sprime_bars.png` + `pool_standings.csv` (16 survivors) |
| 7 ANCOVA | `figs/ancova_ercot.png`, `figs/ancova_ercot.csv` ← `pool_standings_levels.csv` |
| 8 atlas | `pool/figs/standings/{V1,E1,R4,N1}.png`, captions from `pool_standings.csv` |
| 9 redundancy | `pool/figs/standings/clustermap_L180.png`; standings §4, §6 |
| 10 gap bound | `pool_gap_bound_wavedD.csv`, `pool_gap_bound_summary.json`, standings §2 |
| 11 caveats | standings §0.1, §0.3, ruler line; `pool_standings.csv` identity-shift columns |
| 12 E-D1b | `pool_ed1b_decision.csv`, standings §7, §9 |
| A | `pool/figs/standings/<id>.png` for the 21 other graded candidates, global order |
| B | `pool_wavedD_wallclock.csv`, standings §8 |

## ANCOVA (slide 7; `figs/ancova_ercot.csv`)

On the 18 VRE rows per candidate: model 0 = 1 + MW + MW² (residual df 15); model 1 = + 5 site
intercepts (df 10); model 2 = + 5 site × MW slopes (df 5). R²adj only; NO F test (no ruler).
Reading rule (stated on the slide): `no fit` if every R²adj < 0.3; `mostly size` if both
increments < 0.10; `slopes differ` if the slope increment ≥ 0.10 and ≥ the intercept increment;
else `level shift`.

| id | R²adj quad. MW | + site intercepts | + site × MW | R²adj model 2 | reading |
|---|---|---|---|---|---|
| V1 | 0.965 | +0.013 | +0.012 | 0.990 | mostly size |
| E1 | 0.515 | +0.322 | +0.153 | 0.990 | level shift |
| R4 | 0.192 | −0.038 | −0.385 | −0.231 | no fit |
| N1 | 0.056 | −0.000 | −0.297 | −0.241 | no fit |
| R2 | −0.032 | +0.269 | +0.248 | 0.486 | level shift |
| X1 | 0.521 | +0.284 | +0.184 | 0.990 | level shift |

## Deviations from prompt 59 (disclosed)

1. **ANCOVA vocabulary.** The RTS words are `level shift` / `slopes differ` / `mostly size`. R4 and
   N1 have negative R²adj at models 1 and 2 (adding site terms costs more df than it explains), so
   `mostly size` would misread them. A fourth word, `no fit`, is used and defined on the slide.
2. **Slide 6 layout.** The S′ table sits BESIDE the figure (17 rows do not fit beneath a legible
   figure at 16:9).
3. **Slide 8 paths.** The 2 × 2 atlas prints its four paths in one line under the grid (6 pt) and in
   the notes, not under each panel (panel height).
4. **Numbers follow the data where the spec rounds differently:** G_base $196.7M (spec "$197 M");
   identity shift V1 −67.7 GWh/yr (spec "−68"), R4 −1,947 starts/yr (spec "−1,950"); E1 −$10.9M/yr.
5. **"45× contrast" (spec §0, SCREENING row)** is not quoted: no such number was found in
   `SCREENING_ERCOT.md`, and slide 3 does not need it.
6. `deck_lib.py` carries a 2-line provenance header above the unchanged copy (the spec asks for one).

## `[not in files]` markers

None. Every number on the slides is read from a CSV / JSON / MD named in the notes; the only new
statistics are the three figures of `make_location_figs.py` (prompt 59 §2 items 5–7).
