# bo_1012 — BO campaign quality report deck (2026-10-12)

**What:** `bo_1012.pptx` is a 34-slide deck in PI-meeting style on the ND group-meeting template. It covers the Stage-2 q-ParEGO campaign result, the random baseline, the design recipe, claim scope, open questions and decisions. The deck is organised in four blocks (progress / technical update / roadblockers / decisions), plus block 5 (slides 30–34, added 2026-10-13: status of prompts 35, 36 and 37), with RED and GREEN badges on technical slides, as in pi_1008 v2.

**Build:**

```
/opt/anaconda3/bin/python make_bo_1012_deck.py
```

This writes `bo_1012.pptx`, `SLIDE_TEXT.md` (all slide text and speaker notes) and `FIGURES_USED.md` (slide → figure path).

**Sources:**
- Content: `OUTLINE.md` (the source of truth; the builder only renders it).
- Helpers: `../../pi_1008/deck_lib.py`. The badge helper is copied from `../../pi_1008/v2/make_pi_1008_v2.py`.
- Figures: `../../bo_stage2/figs/fig1–4*.png`, `../../random_baseline/figs/fig1–4*.png`. Slide 8's chain flow is drawn with shapes.
- Numbers: `bo_stage2/BO_STAGE2.md`, `random_baseline/RANDOM_BASELINE.md`, `admin/prompt/bogp/{30,34,math-log,living-report-multipem}.md`. Each slide's speaker notes name its source.

Costs are g1-pending: slides 10, 17 and 19 carry the footer. To change content, edit `OUTLINE.md` first, then the builder.
