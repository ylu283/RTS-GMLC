"""Build bo_1016.pptx — initial-design evidence + stop-rule closure (PI meeting 2026-10-16).

!!! STALE AS OF 10-16 PM — DO NOT REBUILD OVER bo_1016.pptx !!!
Kay hand-restructured the live deck in PowerPoint (16 slides: Act-1 divider +
zero-new-runs slide deleted, both parity grids merged onto one slide, verdict/
decision slides reworded, footers removed) and the tune32 figure was inserted
directly into the pptx with python-pptx. This script still renders the OLD
19-slide version and would clobber all of that. Backups of Kay's versions:
bo_1016_kay_edit_1016pm.pptx (opener rewrite), bo_1016_kay_edit2_1016.pptx
(16-slide restructure, pre-figure). Back-port before any rebuild.
"""
import sys as _sys
if "--force-stale-rebuild" not in _sys.argv:
    _sys.exit("REFUSING to rebuild: bo_1016.pptx is hand-edited (see docstring). "
              "Pass --force-stale-rebuild to override.")
_OLD_DOC = """

Run:  /opt/anaconda3/bin/python make_bo_1016_deck.py
Out:  bo_1016.pptx, FIGURES_USED_1016.md  (next to this script).
      SLIDE_TEXT_1016.md is regenerated separately (python-pptx dump) after
      every rebuild — it is NOT written by this script.

Content source of truth: OUTLINE_1016.md in this folder. This script only
renders it. Style follows make_bo_1013_deck.py (deck_lib copied locally from
pi_1008 — the main clone is not touched). After the build an overflow check
WARNS (no assert) for shapes with top < 6.8 in and bottom > 7.2 in; text
overflowing INSIDE a fixed-height box is not caught — eyeball dense slides.
"""

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent                      # quality_report/bo_1016/
sys.path.insert(0, str(HERE))

from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt

import deck_lib as L
from deck_lib import (ACCENT, INK, MUTED, card, content_slide, figure, new_deck,
                      notes, section_slide, table, text_box)

AN = HERE.parent.parent                                      # campaign/analysis
MECH = Path("/Users/yilu/Documents/GitHub/RTS-GMLC-mechanism/trial_0826/campaign/analysis/mechanism")
ADMIN = Path("/Users/yilu/Documents/development/nd/research/admin/prompt/bogp")

RED = RGBColor(0xC0, 0x39, 0x2B)
GREEN = RGBColor(0x1E, 0x84, 0x49)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
BOX = RGBColor(0xFD, 0xF6, 0xE3)       # pale gold for boxed key sentences
PHBG = RGBColor(0xED, 0xED, 0xED)      # placeholder gray

FOOT = "BO workflow: initial-design evidence + stop-rule closure · 2026-10-16"

F = {
    "n0_curve": AN / "initial_design/figs/n0_curve_holdout.png",
    "parity": HERE / "fig_parity_holdout.png",
    "nofloor": HERE / "fig_parity_nofloor.png",
    "sdheat": HERE / "fig_sd_heatmap.png",
    "stoprule": HERE / "fig_stoprule_closed.png",
    "h1": MECH / "fig_h1_commitment.png",
}

n = 0


def nxt():
    global n
    n += 1
    return n


def bullets(slide, x, y, w, h, items, size=14, space_after=6):
    return text_box(slide, x, y, w, h, items, size=size, bullets=True,
                    space_after=space_after)


def keybox(slide, x, y, w, h, lines, size=14):
    card(slide, x, y, w, h, fill=BOX)
    text_box(slide, x + Inches(0.12), y + Inches(0.07), w - Inches(0.24),
             h - Inches(0.14), lines, size=size)


def add_badges(slide, items):
    ph = slide.shapes.title
    if ph is not None:
        ph.left, ph.top, ph.width, ph.height = (Inches(0.14), Inches(0.14),
                                                Inches(9.8), Inches(0.86))
        for p in ph.text_frame.paragraphs:
            for r in p.runs:
                r.font.size = Pt(18 if len(ph.text_frame.text) > 60 else 21)
    y = Inches(0.16)
    for kind, text in items:
        color = RED if kind == "R" else GREEN
        label = ("ROADBLOCKER · " if kind == "R" else "DECISION · ") + text
        shp = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(10.05), y,
                                     Inches(3.15), Inches(0.36))
        shp.adjustments[0] = 0.3
        shp.fill.solid(); shp.fill.fore_color.rgb = color
        shp.line.fill.background(); shp.shadow.inherit = False
        tf = shp.text_frame; tf.word_wrap = True
        tf.margin_left = tf.margin_right = Inches(0.06)
        tf.margin_top = tf.margin_bottom = Inches(0.01)
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
        r = p.add_run(); r.text = label
        r.font.name = L.FONT; r.font.size = Pt(8.5); r.font.bold = True
        r.font.color.rgb = WHITE
        y += Inches(0.40)


prs = new_deck()

# --------------------------- 1 · recap (Kay's 10-16 PM edit, verbatim; it
# replaces the original title slide + the 60-second-recap slide)
s = content_slide(prs, "recap", n=nxt())
text_box(s, Inches(0.5), Inches(1.2), Inches(12.3), Inches(2.67), [
    ("BO", {"bold": True}),
    ("•  Last meeting (10-13)", {"bold": True}),
    "•  whether 32 starting points is a good choice for GP & hyperparameter tuning (done)",
    "•  5-10 seed BO (still running)",
    "•  ERCOT where to build PEM and what size (not started)",
    ("•  Other projects (no decisions needed today)", {"bold": True}),
    "•  GTEP. Run PCM on the 2035 fleets",
    "•  AIChE 2026 talk: ERCOT figures freeze next week.",
], size=13, space_after=8)
notes(s, "Kay's wording 10-16. Rehearsal detail if asked: three decisions "
         "needed today = seed-study start size (NXT-D10a), tuned grading GP "
         "(NXT-D10b), seed count 5 vs 10 (1014-D1). GTEP: coal case solved on "
         "CRC 10-12 (5/6 optimal <= 1%, B1 accepted at 2.93% gap); PCM on the "
         "2035 fleets awaits two data choices (generator parameters, load "
         "basis). Sources: pi-agenda.md §4; living-report-gtep.md. "
         "Verbal reconciliations for the recap wording (review 10-16): "
         "'ERCOT figures freeze next week' — figure WORK starts 10-22, the "
         "freeze itself is 11-01 (slide 17); '5-10 seed BO (still running)' — "
         "3 trajectories are live + P1 complete; the 5-vs-10 count is today's "
         "decision, the full study has not launched.")

# ------------------------------------------------- 2 · three asks status map
s = content_slide(prs, "Your three asks from Tuesday — all three moved", n=nxt(), foot=FOOT)
table(s, Inches(0.5), Inches(1.25), Inches(12.3), [
    ["Ask (Tue 10-13)", "Status", "Result in one line"],
    ["Evidence that n0 = 32 is a good choice",
     "DONE — zero new PCM runs",
     "32 is not yet sufficient: curtailment / cost error still drops a lot at 48; calibration at 32 is sound"],
    ["Would hyperparameter tuning help?",
     "DONE — pre-registered hyperparameter study",
     "Yes, where the pathology lives: rbf+log1p repairs the round-3 audit (coverage 5/8 to 8/8)"],
    ["5-10 random seeds behind the conclusions",
     "RUNNING — 3 new trajectories live",
     "P1 complete (hard cap); P2 / P3 / N1 graded r1; need your seed count to scope the rest"],
], col_widths=[3.4, 2.6, 6.3], size=12, row_h=Inches(0.62))
bullets(s, Inches(0.5), Inches(4.05), Inches(12.3), Inches(2.4), [
    ("Also closed this week:", {"bold": True}),
    "Stop rule held at both P1 overrun checkpoints (r3 = 0.62 τ, r4 = 0.30 τ — official grading).",
    "Shed mechanism identified from hourly data: day-ahead commitment, not PEM scarcity sales.",
    "ERCOT fuel-mix audit: our conversion is exact (45/45); the flagged discrepancies trace to the published dataset — AIChE figures stand.",
], size=13)
keybox(s, Inches(0.5), Inches(6.35), Inches(12.3), Inches(0.62), [
    ("Needed from you today: 3 decisions — seed-study n0 · grading GP · "
     "seed count (5 vs 10) — plus the wave-D wait condition restated and the "
     "standing g1 sign-off (slide 17).", {"bold": True})], size=12.5)
notes(s, "Sources: analysis/initial_design/N0_EVIDENCE.md; methods_C ledgers; "
         "mechanism/MECHANISM.md (261bed4); admin debug/fuelmix-check-2026-10-15.md. "
         "Dating: the meeting was Tue 10-13; the 1014-D* IDs are dated by when "
         "the decisions were recorded (10-14).")

# ---------------------------------------------------------- 3 · divider act 1
s = section_slide(prs, "ACT 1 · THE GP QUESTION (1014-D2)",
                  "Is 32 starting points enough?",
                  "Test: refit the same GP on 16 / 32 / 48 starts; score every fit on an\n"
                  "untouched 48-run random holdout; judge by pre-registered criteria.",
                  n=nxt())

# ------------------------------------------------------- 4 · zero new runs
s = content_slide(prs, "The test cost zero new PCM runs", n=nxt(), foot=FOOT)
bullets(s, Inches(0.5), Inches(1.3), Inches(6.4), Inches(5.4), [
    ("One nested Sobol sequence, by construction", {"bold": True}),
    "Draws 1-16 = the original 16 starts; 17-32 = the 32-point refresh; 33-48 = wave Q1 (already landed 10-13).",
    "So 16 ⊂ 32 ⊂ 48 — the 48-point design existed before the question was asked.",
    ("Holdout nobody trained on", {"bold": True}),
    "waves/random_C: 48 i.i.d. uniform designs; zero overlap with the 48 training designs (asserted); never used to fit or tune.",
    ("Pre-registered, then executed", {"bold": True}),
    "Acceptance criteria (E1 diminishing returns, E2 calibration, E3 tuning) fixed in the prompt BEFORE any fit.",
    "Pre-flight: Sobol regeneration bit-identical; 16/32 LOO tables reproduce the 10-08 deck to 4e-7.",
], size=13.5)
card(s, Inches(7.2), Inches(1.4), Inches(5.6), Inches(3.1))
text_box(s, Inches(7.45), Inches(1.6), Inches(5.1), Inches(2.8), [
    ("Budget", {"bold": True, "size": 14}),
    ("0 new PCM runs", {"bold": True, "size": 26, "color": ACCENT}),
    "Every fit, audit and the frozen-machinery replay ran locally — no cluster time.",
], size=13)
notes(s, "Provenance: tiers.py SOBOL_SEED 20260821, scipy 1.16.3; Q1 manifest "
         "continues_waves [n0, n0b]. Asserts: initial_design/preflight.py (all pass).")

# --------------------------------------------------- 5 · main evidence curve
s = content_slide(prs, "Verdict: 32 is not sufficient — the error curve has not bent", n=nxt(), foot=FOOT)
figure(s, F["n0_curve"], Inches(0.4), Inches(1.25), Inches(8.6), Inches(4.4),
       slide_no=n, caption="GP accuracy on the untouched holdout vs number of starting points")
bullets(s, Inches(9.2), Inches(1.3), Inches(3.9), Inches(5.6), [
    ("Holdout RMSE / noise floor (default GP)", {"bold": True}),
    "curtailment: 17.4 → 9.4 → 5.0",
    "cost: 15.4 → 7.9 → 5.3",
    "shed: below floor at every n0 (noise-limited)",
    ("E1 (returns diminishing?) fails", {"bold": True, "color": RED}),
    "32→48 cuts error almost as much as 16→32 — the curve is still descending at 48.",
    ("But 32 steered BO soundly", {"bold": True, "color": GREEN}),
    "ranking Spearman ≥ 0.94; calibration at 32 passes (E2).",
], size=12.5)
keybox(s, Inches(0.4), Inches(5.95), Inches(8.6), Inches(1.0), [
    ("32 was good enough to steer the campaign; it is not good enough as the final "
     "reported surrogate. 48 is measurably better — and for THIS design (seed 0) the "
     "extra 16 runs already exist.", {"bold": True})],
    size=13.5)
notes(s, "criteria.json: E1 I(32to48) curt 0.470, cost 0.331 vs 1/3-rule 0.153/0.163 "
         "and 0.25 cap; E2 winner cov95 44/44/47 in [43,48]; Spearman >= 0.94 all "
         "objectives. Shed: 22/48 holdout rows below the 3,000 MWh floor. "
         "If asked why the 1/3 rule is the right bar: pre-registered geometric-"
         "convergence proxy (next 16 points should buy < 1/3 of what the last 16 "
         "bought); the 0.25 cap is a second independent bar; and at 48 the error is "
         "still ~5x the noise floor on curt/cost — the verdict survives any reasonable "
         "bar. If asked how a noise-limited shed GP drove a 3-objective BO: at "
         "explored designs shed is near-binary (the 22.4 MWh floor event vs nonzero); "
         "the GP captures that ordering, and Q2 (slide 15) shows the residual shed is "
         "PEM-independent — acquisition pressure correctly shifted to curt/cost. "
         "If asked 'your agenda said 3.0x at 48, the slide says 5.0x': the agenda "
         "quoted the in-sample LOO curve (curt 17.1-6.6-3.0); this slide is the "
         "stricter untouched-48-design holdout (17.4-9.4-5.0). The holdout is the "
         "honest number; both fail E1 the same way.")

# ------------------------------------------------- 5b · parity (point-by-point)
s = content_slide(prs, "The same verdict, point by point", n=nxt(), foot=FOOT)
figure(s, F["parity"], Inches(0.3), Inches(1.2), Inches(6.3), Inches(5.8),
       slide_no=n, caption="Predicted vs actual on the 48 unseen designs; bars = GP 95% intervals")
bullets(s, Inches(6.9), Inches(1.3), Inches(6.2), Inches(5.4), [
    ("How to read", {"bold": True}),
    "Each dot = one unseen random design; bar = the GP's 95% interval; dashed line = perfect prediction.",
    ("Curtailment and cost (rows 2-3)", {"bold": True, "color": GREEN}),
    "Dots collapse onto the line and the bars tighten 16 → 32 → 48 — the same ~2× error cut per +16 points as the curve, now visible per design.",
    ("Load shed (row 1)", {"bold": True}),
    "Scattered with wide bars at every n0 — noise-limited, as the floor analysis says. The GP stays honest about it: coverage 47-48/48.",
    ("No new holdout touch", {"bold": True}),
    "Deterministic refit of the same campaign-default GPs; the script asserts every panel's RMSE and coverage match the official holdout table exactly.",
    ("Are the wide shed bars the GP, or the floor? Next slide removes the floors to find out.", {"bold": True}),
], size=13)
notes(s, "make_fig_parity.py: re-plot of the prompt-39 holdout scores (role="
         "default); asserts rmse_over_floor matches holdout_results.csv to 1e-9 "
         "and cov95 exactly, per panel, before drawing. If asked why the shed "
         "bars are so wide: the predictive sd includes the floor-constrained "
         "noise (3,000 MWh) — the signal itself sits below the floor.")

# --------------------------------------------- 5c · shed bars = floor ablation
s = content_slide(prs, "Same nine panels without the noise floors — only the shed row changes", n=nxt(), foot=FOOT)
figure(s, F["nofloor"], Inches(0.3), Inches(1.2), Inches(6.3), Inches(5.8),
       slide_no=n, caption="Identical GPs, likelihood noise bound (floor/σ)² → 1e-9; scored against the REAL floors")
bullets(s, Inches(6.9), Inches(1.25), Inches(6.2), Inches(5.6), [
    ("One change vs the previous slide", {"bold": True}),
    "The GP's noise lower bound is dropped; data, seed, kernel, metrics identical — flip back and forth to compare.",
    ("The floor only ever binds on shed", {"bold": True, "color": GREEN}),
    "Shed: free-noise GP infers 317-527 MWh vs the 3,000 MWh floor — bars shrink ~6×, coverage stays 45-48/48, RMSE 0.32-0.58× floor.",
    "Curtailment / cost: inferred noise already sits 1.7-3.8× ABOVE the floor (curt 8.5-12.5k vs 5k MWh; cost $1.1-1.9M vs $0.5M), so those six panels barely move.",
    ("Read", {"bold": True}),
    "Point predictions were never the problem — the wide shed bars are the pre-registered replicate-variability floor, conservative on unseen designs (the safe side for BO).",
    ("Post-hoc illustration, outside the pre-registered axes — hints shed noise is design-dependent; a Discussion item, no decision today.", {"italic": True}),
], size=12)
notes(s, "make_fig_parity_nofloor.py (full 3x3; shed-only 2x3 variant in "
         "make_fig_nofloor.py). FlexGP with floor=1e-9 = unconstrained noise; "
         "metrics still scored against the real 3,000 MWh floor. If asked 'so "
         "is the floor wrong?': the floor encodes measured PCM replicate "
         "spread; holdout residuals below it suggest the replicate noise is "
         "heteroscedastic (large at shedding designs, small near zero shed, "
         "and random_C concentrates at low shed). A conservative homoscedastic "
         "floor costs nothing for BO — shed ordering is preserved — and a "
         "heteroscedastic noise model is future work for the final surrogate, "
         "not a campaign change.")

# ------------------------------------------------------------- 6 · tuning
s = content_slide(prs, "Tuning helps exactly where the pathology lives", n=nxt(), foot=FOOT)
bullets(s, Inches(0.5), Inches(1.25), Inches(6.6), Inches(3.0), [
    ("The start-set GP was never miscalibrated", {"bold": True}),
    "32-start LOO: curtailment rms_z 0.81, coverage 31/32. The weak audit you saw (r3) belongs to the BO-augmented GP.",
    ("Hyperparameter study (pre-registered NLPD rule)", {"bold": True}),
    "Winners: rbf + log1p (shed, curtailment), rbf (cost). Picked on the 32 starts, committed before any holdout scoring.",
], size=13)
text_box(s, Inches(7.4), Inches(1.3), Inches(5.5), Inches(0.35),
         "Round-3 audit cell (the PI's observation), refit + rescored:",
         size=12.5, bold=True)
table(s, Inches(7.4), Inches(1.7), Inches(5.5), [
    ["curtailment", "default GP", "rbf+log1p"],
    ["coverage (of 8)", "5 / 8", "8 / 8"],
    ["rms z-score", "2.008", "1.050"],
    ["reproduces recorded audit", "exact", "—"],
], col_widths=[2.2, 1.65, 1.65], size=12, row_h=Inches(0.42))
bullets(s, Inches(0.5), Inches(4.35), Inches(12.3), Inches(2.1), [
    ("Out-of-sample check:", {"bold": True}),
    "the winner's curtailment error rises from 4.8× (LOO) to 7.3× floor on the holdout — still better than the default; the advantage shrinks but holds.",
    "Secondary grid findings (BoTorch prior, kernels) → backup slide.",
], size=12.5)
notes(s, "part_h_loocv.csv (main-effects + best-combo design, 19 config-objective fits, LOO NLPD rule); hbo_cell.json; "
         "fits.json committed 07:34 UTC, first holdout call after. "
         "Proposal: adopt winner for grading/prediction only; acquisition untouched (NXT-D10b). "
         "H-BO cell mean_z: default 1.426 -> winner 0.967. "
         "If asked 'tuned-32 is still worse than default-48 — why not just use 48?': "
         "they fix different pathologies — tuning repairs late-round COVERAGE "
         "(5/8 -> 8/8), more points buy ACCURACY (winner 7.3x floor at 32 vs "
         "default 5.0x at 48); we propose both — tuned grading now, 48-point "
         "final paper surrogate (the D10a rider).")

# --------------------------------------------------------------- 7 · replay
s = content_slide(prs, "Same landscape, different probes — why seeds are the next instrument", n=nxt(), foot=FOOT)
table(s, Inches(0.5), Inches(1.3), Inches(7.2), [
    ["Round-1 replay from...", "Batch overlap with deployed r1", "Landscape rank corr. (Spearman)"],
    ["32 starts (the real campaign)", "8 / 8 — reproduces it exactly", "—"],
    ["16 starts", "0 / 8", "0.94 vs 32-start"],
    ["48 starts", "0 / 8", "0.95 vs 32-start"],
], col_widths=[2.6, 2.4, 2.2], size=12, row_h=Inches(0.5))
bullets(s, Inches(8.0), Inches(1.3), Inches(5.0), Inches(2.9), [
    ("How to read this", {"bold": True}),
    "The GPs agree on where is good (ρ ≥ 0.89 on every weight) …",
    "… but the acquisition argmax is a knife-edge: a different start set moves every batch member.",
    "A knife-edge argmax is expected for batch acquisition — which is exactly why one replay cannot answer the front question.",
], size=12.5)
keybox(s, Inches(0.5), Inches(4.3), Inches(12.3), Inches(1.5), [
    ("n0 changes which points BO probes next, even when it barely changes the fitted "
     "landscape.", {"bold": True}),
    "Whether that changes the final front is an outcome question — answered by running "
    "the workflow from several seeds (your 1014-D1 directive), not by more GP diagnostics.",
], size=13.5)
notes(s, "replay_r1.json; frozen bo-gp 60e6328; proposal seed 20261007 re-derived "
         "and confirmed against round_records r1. Library import only — the frozen "
         "campaign state was never written. Three different Spearmans in this deck, "
         "if the PI probes: slide 5's >= 0.94 = GP-prediction vs truth RANKING on the "
         "holdout; this table's 0.94/0.95 = 16/48-start posterior LANDSCAPE vs the "
         "32-start landscape; 'rho >= 0.89 on every weight' = the minimum of that "
         "landscape correlation across the 8 scalarization weights (min 0.892).")

# ------------------------------------------------------------ 8 · NXT-D10
s = content_slide(prs, "Decision NXT-D10 — two choices from Act 1", n=nxt(), foot=FOOT)
add_badges(s, [("D", "NXT-D10a seed-study n0"), ("D", "NXT-D10b tuned grading GP")])
card(s, Inches(0.5), Inches(1.35), Inches(6.1), Inches(4.6))
text_box(s, Inches(0.75), Inches(1.5), Inches(5.6), Inches(4.3), [
    ("(a) Seed study starts from 32 or 48?", {"bold": True, "size": 15}),
    ("Start at 32 — RECOMMENDED", {"bold": True, "color": GREEN}),
    "Comparable to the live campaign; calibration sound; replay reproduces the real r1; known cost: ~2× curtailment error vs 48.",
    ("Start at 48", {"bold": True}),
    "More accurate surrogate, but +16 NEW PCM runs per fresh seed (≈ +25% per-seed cost) — only seed 0's 48 points exist today.",
    ("Rider (folds into D10a): the final paper surrogate is reported at 48.", {"italic": True}),
], size=13)
card(s, Inches(6.9), Inches(1.35), Inches(6.1), Inches(4.6))
text_box(s, Inches(7.15), Inches(1.5), Inches(5.6), Inches(4.3), [
    ("(b) Adopt rbf+log1p for grading only?", {"bold": True, "size": 15}),
    ("Yes — RECOMMENDED", {"bold": True, "color": GREEN}),
    "Repairs the r3 overconfidence (5/8 → 8/8) with zero new runs.",
    "Scope: grading / prediction / audit layer ONLY.",
    ("The acquisition path stays frozen", {"bold": True}),
    "so every completed and running arm stays comparable; a tuned-acquisition arm can be a separate seed later if wanted.",
], size=13)
notes(s, "Full decision text: pi-agenda.md NXT-D10 (rigorous + plain versions). "
         "If asked 'if the curve is still descending at 48, why not 64?': the "
         "nested Sobol extends by construction — draws 49-64 are already defined, "
         "so a 64-point tier for seed 0 costs +16 runs ≈ 240 core-h and lets E1 "
         "be re-run at 48→64: if I(48→64) passes the 1/3-rule, 48 is certified "
         "as the final surrogate; if not, we learn the curve's slope. Proposed "
         "as a cheap one-seed add-on decided after the seed study launches — "
         "it does not gate anything today.")

# ---------------------------------------------------------- 9 · divider act 2
s = section_slide(prs, "ACT 2 · THE STOP RULE + SEEDS (1014-D1)",
                  "The stop rule held — twice",
                  "P1 ran past its own stop to the hard cap, as a record-only overrun.\n"
                  "Three new trajectories are live.",
                  n=nxt())

# ------------------------------------------------------------ 10 · stop rule
s = content_slide(prs, "Stop rule closed at both overrun checkpoints (official)", n=nxt(), foot=FOOT)
figure(s, F["stoprule"], Inches(0.4), Inches(1.25), Inches(9.3), Inches(4.7),
       slide_no=n, caption="P1: live stop at r2; overrun rounds r3 / r4 graded on CRC (record only)")
bullets(s, Inches(9.9), Inches(1.3), Inches(3.2), Inches(5.0), [
    ("Live decision (10-10)", {"bold": True}),
    "STOP at r2: gains 0.69 τ, then 0.17 τ.",
    ("Overrun verdict", {"bold": True}),
    "r3: 0.62 τ — below τ.",
    "r4: 0.30 τ — below τ. Hard cap; P1 complete.",
    ("Cost of ignoring the rule", {"bold": True}),
    "16 extra runs bought +6.9% HV, every increment sub-threshold.",
], size=12.5)
notes(s, "methods_C/P1/ledger.json; r4 graded on CRC (a8df435). τ = 5.263e16. "
         "Strategy-session preview reproduced every graded entry to relerr ≤ 2e-16 "
         "before the official grading landed; official numbers matched digit-for-digit.")

# ------------------------------------------------------------- 11 · seeds
s = content_slide(prs, "Seed support is building — need your count", n=nxt(), foot=FOOT)
add_badges(s, [("D", "1014-D1 seed count: 5 or 10")])
table(s, Inches(0.5), Inches(1.35), Inches(12.3), [
    ["Arm", "Acquisition", "Start set", "Latest graded", "Gain vs τ", "State"],
    ["P1 (the campaign)", "q-ParEGO", "the 32 (seed 0)", "r4 (hard cap)", "0.30 τ", "COMPLETE — stop held"],
    ["P2", "q-ParEGO", "fresh 32, seed 2", "r1", "2.28 τ", "r2 array running"],
    ["P3", "q-ParEGO", "fresh 32, seed 3", "r1", "0.77 τ", "r2 array running"],
    ["N1", "qNEHVI", "the 32 (seed 0)", "r1", "1.43 τ", "r2 ran; grading lands tonight (preview 0.61 τ)"],
], col_widths=[2.1, 1.5, 1.9, 1.7, 1.3, 3.8], size=12, row_h=Inches(0.46))
bullets(s, Inches(0.5), Inches(4.2), Inches(12.3), Inches(2.2), [
    ("What a 'seed' buys:", {"bold": True}),
    "One full workflow replicate — fresh Sobol init + BO rounds + stop rule — ≈ 1,000 core-h. Readout: the distribution of stop round and HV-at-stop across seeds.",
    "5 seeds ≈ 5k core-h (fits this month); 10 seeds ≈ 10k core-h (stronger claim, ~2× queue time).",
    ("The r1 spread above (2.28 τ vs 0.77 τ) is exactly what the trigger adjudicates. Proposal: start with 5 and pre-commit the extension — extend to 10 if the seed-to-seed range of HV-at-stop exceeds 25% of the mean BO gain (threshold yours to set). NXT-D10a fixes the start size.", {"bold": True}),
], size=13)
notes(s, "Ledgers: P2 r1 2.2773 τ (b46d66b), P3 r1 0.7697 τ (6fdfc93), N1 r1 1.43 τ. "
         "N1 r2 preview from the validated strategy-session HV replication (matched "
         "every graded entry to relerr <= 2e-16; P1 r4 official matched digit-for-"
         "digit) — divergence would mean a grading-infra bug, not a science change. "
         "If asked 'what if a seed never stops before the cap?': that IS the readout "
         "— the distribution of stop rounds; the hard cap bounds worst-case cost at "
         "~1k core-h per seed. If asked 'P3 is sub-tau at r1 — will it stop at r2, "
         "and does the rule allow so short a campaign?': yes — P3 holds strike 1; a "
         "second sub-tau round stops it, and an early stop is a legitimate datum in "
         "the stop-round distribution. And r1 gain is NOT the extension-trigger "
         "input: the pre-committed trigger reads the HV-at-stop range (25% of mean "
         "gain), computed only once seeds stop.")

# ---------------------------------------------------------- 12 · divider act 3
s = section_slide(prs, "ACT 3 · IN ONE WEEK, UNBLOCKED",
                  "The mechanism, and ERCOT",
                  "Two standing worries closed with zero new simulation:\n"
                  "why PEM cuts load shed, and whether the ERCOT conversion is sound.",
                  n=nxt())

# ---------------------------------------------------------- 13 · mechanism
s = content_slide(prs, "Why PEM cuts load shed — explained with hourly data (one model, one year)", n=nxt(), foot=FOOT)
keybox(s, Inches(0.4), Inches(1.2), Inches(12.5), Inches(0.95), [
    ("PEM retrofits cut shed not by selling power in scarcity: priced PEM demand "
     "absorbs the wind forecast, so the day-ahead RUC commits ~1.2 GW more thermal "
     "and the scarce hours arrive with headroom.", {"bold": True, "size": 14})])
figure(s, F["h1"], Inches(0.4), Inches(2.25), Inches(7.9), Inches(4.2),
       slide_no=n, caption="Committed thermal + headroom on the low design's 100 shed hours; shed-difference decomposition")
bullets(s, Inches(8.5), Inches(2.3), Inches(4.6), Inches(4.4), [
    ("H1 commitment headroom — supported, dominant", {"bold": True, "color": GREEN}),
    "zero-shed designs commit +1.2-1.3 GW more thermal; headroom 737-771 MW vs exactly 0; extra thermal covers 107-171% of the shed difference in all 8 pairs.",
    ("H2 scarcity sales (as driver), H3 location (slack-bus accounting), H4 reserve substitution — all contradicted", {"bold": True, "color": RED}),
    ("Q2 floor: confirmed", {"bold": True}),
    "all 7 designs: one winter-morning event (12-18 h7, 22.4 MWh), same +962 MW commitment change, decomposition residual 0.000.",
    ("Caveat: a property of cost-based RUC under priced withholding — model sensitivity goes to Discussion.", {"italic": True}),
], size=11.5)
notes(s, "MECHANISM.md (261bed4): verdict table + two paper-ready paragraphs. "
         "Paper wording change: 'zero shed' → '≤ 22.4 MWh/yr, one PEM-independent "
         "commitment-limited event'. Spoken framing if useful: the day-ahead "
         "commitment stops trusting free wind. If asked 'is this a Prescient / "
         "cost-based-RUC artifact?': the mechanism needs only that DA commitment "
         "responds to the net-load increase from priced PEM withholding — any RUC "
         "formulation with that coupling should reproduce it; a reliability-based-RUC "
         "sensitivity is a bounded Discussion item, not new campaign work.")

# -------------------------------------------------------------- 14 · ERCOT
s = content_slide(prs, "ERCOT: our conversion is exact; the quirks are the dataset's", n=nxt(), foot=FOOT)
add_badges(s, [("R", "wave D gated on 1014-D3")])
table(s, Inches(0.5), Inches(1.35), Inches(12.3), [
    ["Flag", "Finding", "Action"],
    ["Coal 32% of energy (real 2019: 20%)", "TX-123BT's own coefficients put all 13 coal units below all 113 gas units in merit order", "inherit + disclose"],
    ["Gas looks like peakers", "implied heat rates ~18.5 MMBtu/MWh (real CC ~7) — the paper says 'typical' coefficients", "inherit + disclose"],
    ["PV fleet 8.26 GW (real 2.3)", "the DATASET is internally inconsistent: its paper says 2.48 GW, its published files 8.26", "inherit published files + 1 sentence"],
    ["LMP $34 vs 2019 DAM $38", "right order — inflated heat rates ≈ offset missing scarcity adders", "quote as 'TX-123BT prices'"],
], col_widths=[3.1, 6.2, 3.0], size=11.5, row_h=Inches(0.56))
bullets(s, Inches(0.5), Inches(4.5), Inches(12.3), Inches(1.9), [
    ("Our conversion: 45/45 cost coefficients exact; load side matches ERCOT 2019 actuals to the MW (383.8 TWh; preliminary peak 74,666 MW).", {"bold": True}),
    "Consequence: NO AIChE figure needs a re-run; diverted-wind ≈ $30/MWh stands as an in-model result.",
    ("Wave D (location grids on ERCOT) IS the 'where to build PEM + what size' study from the recap — designed and ready; "
     "this audit was its last technical blocker. It waits only on the condition you set at the last meeting — please restate it.", {"bold": True}),
], size=12.5)
notes(s, "Full audit: admin/prompt/bogp/debug/fuelmix-check-2026-10-15.md. "
         "ERCOT 2019 actuals: gas 47%, coal 20%, wind 20%, nuclear 11% (ERCOT Fact Sheet 11/2020). "
         "If asked 'coal dispatches below gas in this dataset — can any ERCOT "
         "siting conclusion transfer to the real grid?': siting signals ride on "
         "network congestion + local renewable curtailment, which the dataset's "
         "transmission topology and wind/PV placement carry; the merit-order quirk "
         "shifts WHICH thermal units back down, so we report siting as a TX-123BT "
         "in-model result and check robustness via the bid-0 placebo rows in the "
         "wave-D design.")

# ----------------------------------------------------------- 15 · decisions
s = content_slide(prs, "Decisions today + the two weeks ahead", n=nxt(), foot=FOOT)
table(s, Inches(0.5), Inches(1.3), Inches(7.6), [
    ["#", "Decision", "Default if you only nod"],
    ["1", "NXT-D10a: seed-study n0 = 32 or 48", "32 (comparability); paper surrogate at 48"],
    ["2", "NXT-D10b: rbf+log1p grading layer", "adopt, grading only"],
    ["3", "1014-D1: seed count", "5 seeds now, extend to 10 if spread is wide"],
    ["4", "Wave-D condition (1014-D3)", "— needs your restatement"],
    ["5", "g1 nuclear accounting (NXT-D7)", "option c (+$28.188M, fronts unchanged)"],
], col_widths=[0.5, 3.6, 3.5], size=12, row_h=Inches(0.48))
bullets(s, Inches(8.4), Inches(1.3), Inches(4.6), Inches(4.8), [
    ("Next two weeks", {"bold": True}),
    "P2/P3/N1 arms run to their caps (automatic).",
    "Seed study launches at your count + n0.",
    "Stop-rule validation suite (synthetic + replay) lands.",
    "AIChE ERCOT figures 10-22 → 10-31.",
    ("Figure freeze: 11-01.", {"bold": True}),
], size=13)
notes(s, "pi-agenda.md carries the rigorous + plain text for every open decision. "
         "Scope if the PI counts rows: 1-3 are today's NEW decisions; 4 is a "
         "restatement request; 5 is the standing NXT-D7 approval. g1 rehearsal "
         "(the PI's memo mentions option (b) flipping a verdict): the base "
         "nuclear fuel curve is FLAT — $3,208.99 per committed hour, zero "
         "marginal cost above 396 MW — so (a) the old delivered-x-$8.1 framing "
         "dissolves; (b) delivered-only is ill-defined and FLIPS the location "
         "analysis's nuclear cost slope (a LOCATION.md verdict); (c) restore "
         "the deleted curve: +$28.188M/yr CONSTANT in omega — an intercept "
         "shift only, every front and slope unchanged. Full text: "
         "g1_nuclear_fuel_accounting_PROPOSAL.md + pi-agenda NXT-D7.")

# ------------------------------------------------------- 16 · backup
s = content_slide(prs, "Backup — hyperparameter grid by-products", n=nxt(), foot=FOOT)
bullets(s, Inches(0.5), Inches(1.4), Inches(12.3), Inches(4.6), [
    ("Secondary findings from the Part-H study (not decision-relevant today):", {"bold": True}),
    "The BoTorch default Gamma(3, 6) lengthscale prior is harmful on every objective here (curtailment error 27× floor) — bo-gp's no-prior default is right for this problem.",
    "Matérn 3/2 never beats Matérn 5/2 on any objective.",
    "Fixing the noise at the floor (vs inferring it above the floor) changes results little.",
    "No axis interaction was triggered: each winning combination beat every single-axis change.",
], size=14)
notes(s, "part_h_loocv.csv; selection rule: LOO NLPD in original units, ties within "
         "0.02 nats break by LOO RMSE; winners committed to fits.json before the "
         "first holdout call.")

# ------------------------------------------- backup 2 · uncertainty heatmaps
s = content_slide(prs, "Backup — where the GP is uncertain (2-D slice)", n=nxt(), foot=FOOT)
figure(s, F["sdheat"], Inches(0.4), Inches(1.3), Inches(12.5), Inches(4.6),
       slide_no=n, caption="Predictive sd / floor on the two most active tiers (wind_303, wind_317); other 4 ω at training median; n0 = 48")
bullets(s, Inches(0.5), Inches(6.0), Inches(12.3), Inches(1.0), [
    "Shed (left): sd/floor 1.07-1.20 everywhere — a featureless map pinned just above the floor; more points cannot change it (noise-limited).",
    "Curtailment (right): sd/floor 3.1-7.4 — lowest where training designs cluster, rising at the corners (data-limited; exactly what more points fix).",
], size=12)
notes(s, "make_fig_sdheat.py. Slice axes picked by curtailment ARD lengthscales "
         "(wind_303 ls 2.0 — by far the most active; wind_317 5.4). sd is the "
         "full predictive sd incl. likelihood noise, in floor units.")

# ------------------------------------------------------------------ outputs
out = HERE / "bo_1016.pptx"
prs.save(out)
print(f"saved {out} ({n} slides)")

# overflow check (same spirit as bo_1013): every shape bottom <= 7.2 in
EMU = 914400
bad = []
for i, slide in enumerate(prs.slides, 1):
    for shp in slide.shapes:
        try:
            bottom = (shp.top + shp.height) / EMU
        except TypeError:
            continue
        top = shp.top / EMU
        if bottom > 7.2 and top < 6.8:   # content spilling into the footer strip
            bad.append((i, shp.shape_type, round(top, 2), round(bottom, 2)))
if bad:
    print("OVERFLOW WARNINGS:", bad)
else:
    print("overflow check: all shape bottoms <= 7.2 in")

with open(HERE / "FIGURES_USED_1016.md", "w") as fh:
    fh.write("# Figures used in bo_1016.pptx\n\n")
    for slide_no, p in L.FIGURES_USED:
        fh.write(f"- slide {slide_no}: `{p}`\n")
    if L.MISSING:
        fh.write("\n## MISSING at build time\n\n")
        for p in L.MISSING:
            fh.write(f"- {p}\n")
print("missing figures:", L.MISSING or "none")
