"""Build ercot_overnight.pptx — ERCOT overnight results (65 → 54 → 66) for the 1-on-1 (prompt 67 v1.1).

Run:  /opt/anaconda3/bin/python make_overnight_figs.py && /opt/anaconda3/bin/python make_overnight_deck.py
Out:  ercot_overnight.pptx, OUTLINE.md, SLIDE_TEXT.md, FIGURES_USED.md, ASSERTIONS.md, external_snippets.json

Every quoted number is read from its source file at build time by overnight_facts.py (F) and asserted there; this
script only formats F's values. Slide titles: prompt 67 v1.1, with the review-round titles (coordinator, 2026-11-26)
superseding slides 2, 3, 5, 7, 8, 9, 11. Body text follows ASD-STE100 style.
Each slide carries a source line (footer + speaker notes). Numbers not in any source file are not printed (README).
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from lxml import etree  # noqa: E402
from pptx.dml.color import RGBColor  # noqa: E402
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN  # noqa: E402
from pptx.oxml.ns import qn  # noqa: E402
from pptx.util import Inches, Pt  # noqa: E402

import deck_lib as L  # noqa: E402
import overnight_facts as F  # noqa: E402
import make_overnight_figs as MF  # noqa: E402
from deck_lib import (ACCENT, ACCENT2, INK, MUTED, WARN, card, content_slide, figure, new_deck,  # noqa: E402
                      notes, section_slide, table, text_box)

FIGS = HERE / "figs"
DATE = "2026-11-26"
SRC_LINES: dict[int, str] = {}
GREEN = RGBColor(0x2E, 0x7D, 0x32)
AMBER = RGBColor(0xB2, 0x6A, 0x00)
n = 0


def nxt():
    global n
    n += 1
    return n


def slide(heading, src, amend=None):
    k = nxt()
    foot = f"Source: {src}" + (f" · plan amendment {amend}" if amend else "")
    assert len(foot) <= 135, (len(foot), foot)   # one footer line (render check)
    SRC_LINES[k] = foot
    s = content_slide(prs, heading, k, foot)
    tsize = 22 if len(heading) <= 90 else (20 if len(heading) <= 125 else 18)
    for r_ in s.shapes.title.text_frame.paragraphs[0].runs:
        r_.font.size = Pt(tsize)
    return s, k


def bullets(s, x, y, w, h, items, size=13, space_after=5):
    return text_box(s, x, y, w, h, items, size=size, bullets=True, space_after=space_after)


def headed(s, x, y, w, h, items, size=13, space_after=6):
    """List with unbulleted bold headings: items = [("H", heading) | str]."""
    out = []
    for it in items:
        if isinstance(it, tuple) and it[0] == "H":
            out.append((it[1], {"bold": True, "color": ACCENT}))
        elif isinstance(it, tuple):
            out.append(("•  " + it[0], it[1]))
        else:
            out.append("•  " + it)
    return text_box(s, x, y, w, h, out, size=size, space_after=space_after)


def chip(s, x, y, w, h, text, fill, size=10):
    card(s, x, y, w, h, fill=fill)
    text_box(s, x, y, w, h, text, size=size, bold=True, color=L.WHITE, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)


def eq(s, path, x, y, scale_in_per_px):
    from PIL import Image
    with Image.open(path) as im:
        w, h = im.size
    s.shapes.add_picture(str(path), x, y, int(Inches(w * scale_in_per_px)), int(Inches(h * scale_in_per_px)))
    L.FIGURES_USED.append((n, str(path)))
    return h * scale_in_per_px


def MINUS(v, d):
    return f"{v:.{d}f}".replace("-", "−")


def f2(v):
    return f"{v:.2f}"


def f3(v):
    return f"{v:.3f}"


# --------------------------------------------------------------- real sub/superscripts (pi_objectives scripts_pass)
_TOK = re.compile(r"(?<![A-Za-z_])(B|σ|τ|η²|M|ρ|s|u|r|GP)(_(?:i|j|c|exact|old|285|het|T|raw|res))(?![A-Za-z0-9])")


def _split_run(r):
    t_el = r.find(qn("a:t"))
    if t_el is None or not t_el.text or not _TOK.search(t_el.text):
        return
    text = t_el.text
    parts, pos = [], 0
    for m in _TOK.finditer(text):
        parts.append((text[pos:m.start()] + m.group(1), 0))
        parts.append((m.group(2)[1:], -25000))
        pos = m.end()
    parts.append((text[pos:], 0))
    parent = r.getparent()
    idx = parent.index(r)
    for k_, (txt, base) in enumerate([p_ for p_ in parts if p_[0]]):
        nr = etree.fromstring(etree.tostring(r))
        nr.find(qn("a:t")).text = txt
        if base:
            rpr = nr.find(qn("a:rPr"))
            rpr.set("baseline", str(base))
        parent.insert(idx + k_, nr)
    parent.remove(r)


def scripts_pass(prs_):
    for sl in prs_.slides:
        for sh in sl.shapes:
            frames = []
            if sh.has_text_frame and not sh.text_frame.text.startswith("Source: "):
                frames.append(sh.text_frame)
            if sh.has_table:
                frames += [c.text_frame for row in sh.table.rows for c in row.cells]
            for tf in frames:
                for r in list(tf._txBody.iter(qn("a:r"))):
                    _split_run(r)


prs = new_deck()
ed1b = F.ed1b

P_STR = f"{F.P_CHANCE:.0e}".replace("e-05", "e-5")          # "2e-5"
assert P_STR == "2e-5"
SL = {"answer": 2, "math": 3, "rule": 4, "house": 5, "v2": 6, "mach": 7, "emu": 8, "calib": 9, "lanes": 10,
      "decision": 11}                                      # main-deck slide numbers (used in cross-references)

# =============================================================================
# 1. Title
# =============================================================================
k = nxt()
s = section_slide(prs, f"ERCOT TX-123BT · OVERNIGHT RESULTS (prompts 65 → 54 → 66) · 1-ON-1 · {DATE}",
                  "ERCOT BO overnight: two objectives, GPs that pass the holdout, machinery that runs end to end — "
                  "four decisions before the first real round",
                  f"rule v2 (M = 2) · n* = {F.N0} · mixed GP fit · emulator dry run · 2026-11-24\n"
                  f"Kay Lu · branch ercot/tx123 @ {F.TX123}", n=k)
for sh in s.shapes:   # three-line heading: shrink it and move the subtitle below it (deck_lib unchanged)
    if sh.has_text_frame and sh.text_frame.text.startswith("ERCOT BO overnight"):
        for r_ in sh.text_frame.paragraphs[0].runs:
            r_.font.size = Pt(32)
        sh.height = Inches(2.0)
    elif sh.has_text_frame and sh.text_frame.text.startswith("rule v2"):
        sh.top = Inches(4.45)
SRC_LINES[k] = "Source: committed_configs.json (n_star), design_space_E_2026-11-24.json (M); git rev-parse ercot/tx123"
L.footer(s, SRC_LINES[k])
notes(s, SRC_LINES[k] + ". Say: Last night the pipeline ran three steps: the objective rule (65), the GP fits (54) "
         "and an emulator test of the BO machinery (66). Today: what it proved, what it did not, and four decisions.")

# =============================================================================
# 2. ANSWER
# =============================================================================
n_done, n_open, n_block = len(F.B3_DONE), len(F.B3_BLOCK) + len(F.B3_OPEN_NB), len(F.B3_BLOCK)
s, k = slide(f"Round 1 can launch after four decisions today and nine Part B items (B3); the emulator tests the "
             "machinery, not the search",
             "admin PROGRESS 11-24 (verdicts); pool_ed1b_v2.csv (eta2_T, resid_IDR_over_B); EMULATOR_BO.md §A, §8")
assert n_block == 9
text_box(s, Inches(0.45), Inches(1.02), Inches(12.4), Inches(0.32),
         f"65 ✓  →  54 ✓  →  66 ✓  →  55 B {n_done}/13 done  →  56 launch", size=12, bold=True, color=ACCENT2)
rows3 = [
    ("ACCEPT WITH NOTES ×2", GREEN, "Objectives: rule v2 seats V1 · E1 (M = 2)."),
    ("ACCEPT WITH NOTES · PI/QA FIX THEN SHIP (applied)", GREEN,
     f"GPs pass the random_E holdout at n = {F.N0}: V1 house fit {F.HOLD['V1']}/48, E1 fit v2 {F.HOLD_V2['E1']}/48."),
    ("ACCEPT WITH NOTES ×3 · FIX THEN SHIP", GREEN,
     "The 55 machinery runs end to end on the committed GPs. It found one serious bug (fixed) and two minor fixes."),
    ("DONE", GREEN, f"RTS 49 V1 arm: DONE at cap {int(F.LED['hard_cap'])} (backup B2)."),
    ("SCIENTIFIC RISK", WARN,
     f"{100 * F.ETA_V1:.0f} % of V1's spread is explained by total PEM MW (η²_T {F.ETA_V1:.3f}). Location enters only "
     f"through E1 (η²_T {F.ETA_E1:.2f}, composition residual IDR {F.RESID_E1:.0f} B_j). Both ends of the emulator "
     "front are box vertices outside the start data. Round 1 tests them."),
]
y = 1.42
for lab, col, txt in rows3:
    hh = 1.15 if lab == "SCIENTIFIC RISK" else 0.86
    chip(s, Inches(0.45), Inches(y + 0.04), Inches(1.6), Inches(hh - 0.08), lab, col, size=11)
    text_box(s, Inches(2.2), Inches(y), Inches(10.75), Inches(hh), txt, size=16, anchor=MSO_ANCHOR.MIDDLE)
    y += hh + 0.06
text_box(s, Inches(0.45), Inches(y), Inches(12.4), Inches(0.3),
         "Verdict chips: acceptance review, 2026-11-24. B_j = the objective's own noise bar.", size=11, color=MUTED)
card(s, Inches(0.35), Inches(6.38), Inches(12.65), Inches(0.6), fill=L.HEADER_BG)
text_box(s, Inches(0.45), Inches(6.38), Inches(12.45), Inches(0.6),
         f"Asks today: accept M = 2 · n₀ = {F.N0}, mixed fit · reuse by design key · approve the 55 B bundle",
         size=14, bold=True, color=ACCENT, anchor=MSO_ANCHOR.MIDDLE)
F.text_has(F.P["emumd"], "Both optima are still box vertices outside the data.")
notes(s, SRC_LINES[k] + ". (i) 65: stats + power systems ACCEPT WITH NOTES. (ii) 54 B: GP stats ACCEPT WITH NOTES, PI/QA "
         "FIX THEN SHIP (fixes applied eb8c2da); 54 v2 round GP stats ACCEPT WITH NOTES. (iii) 66: BO stats + "
         "machinery ACCEPT WITH NOTES, audience FIX THEN SHIP; committed rerun ACCEPT WITH NOTES (chip: ACCEPT WITH NOTES ×3 = BO stats + machinery + rerun). Serious bug = b2b2142 "
         "zero-site fix (HIGH); minor = c7576a6/c470d7b r1 assert, 0066a64 HALT name. (iv) RTS 49 V1 DONE d6 8ed4c01. "
         "Holdout: ercot_gp_status.csv / _v2.csv holdout rows. Risk: pool_ed1b_v2.csv eta2_T V1/E1, resid_IDR_over_B E1; "
         f"EMULATOR_BO.md §A.0 item 1. Station strip: 55 B checklist {n_done} of 13 done (EMULATOR_BO.md §8, backup B3).")

# =============================================================================
# 3. Math slide
# =============================================================================
s, k = slide("The BO problem has two objectives, six design fractions and a 4-round cap; four decisions fix its symbols",
             "arms_E.json, design_space_E_2026-11-24.json, landing_R.json", "11-24 (sha256 e3712a7f…) inst. 4–6, 11-24b §1")
assert F.N_SITES == 6 and F.CAP == 4
SC = 12.3 / 4347 * 0.98       # one scale for every equation PNG → one math font size on the slide
text_box(s, Inches(0.45), Inches(1.12), Inches(8), Inches(0.35), "The BO problem", size=14, bold=True, color=ACCENT)
tags = ["V₁, E₁  →  E-D1b", "", "n₀, GP_j fit  →  E-D7", "5 seed lanes  →  E-D4;  q, qNEHVI  →  55 B", ""]
y = 1.47
for i in range(5):
    eq(s, FIGS / f"eq_bo_{i + 1}.png", Inches(0.45), Inches(y), SC)
    if tags[i]:
        text_box(s, Inches(9.2), Inches(y + 0.08), Inches(3.8), Inches(0.35), tags[i], size=12, bold=True, color=ACCENT2)
    y += 0.44
text_box(s, Inches(0.45), Inches(3.72), Inches(8), Inches(0.35), "Rule v2 (objective seats), four lines",
         size=14, bold=True, color=ACCENT)
y = 4.07
for i in range(4):
    eq(s, FIGS / f"eq_rule_{i + 1}.png", Inches(0.45), Inches(y), SC)
    y += 0.42
text_box(s, Inches(0.45), Inches(5.83), Inches(12.4), Inches(0.5),
         f"u_i = PEM fraction at site i · IDR = inter-decile range (Q90 − Q10 over the {F.N0} designs) · B_j = noise bar "
         "(App. B) · r_j = residual after total PEM MW · lo₉₀ / up₉₀ = 90 % bounds", size=12, color=MUTED)
text_box(s, Inches(0.45), Inches(6.42), Inches(12.4), Inches(0.55),
         "In words: a seat needs a physical outcome that moves clearly above its noise bar and that no earlier seat "
         "already carries.", size=13, bold=True, color=ACCENT)
F.text_has(F.PLAN, "IDR* = Q90 − Q10")
notes(s, SRC_LINES[k] + f". Equations in math font: figs/eq_bo_1..5.png, figs/eq_rule_1..4.png (make_overnight_figs.py, "
         f"pre_can mathtext recipe). u ∈ [0,1]^{F.N_SITES}: design_space_E_2026-11-24.json sites; n0 = {F.N0}: tiers.grading; "
         f"q, cap, 5 seed lanes, qNEHVI: arms_E.json; budget {F.LANES} × {F.CAP} × {F.Q} = {F.BUDGET}: arms_E.json "
         f"budget_option C; R: landing_R.json R (V1 {F.R_V1:,.2f} MWh, E1 ${F.R_E1:,.2f}M); τ_exact = 0: plan "
         "AMENDMENT 2026-11-24b §1; C2/C3 REVIEW only: arms_E.json calibration.action; rule lines: plan AMENDMENT "
         "2026-11-24 instantiations 4 and 6 (block sha256 e3712a7f…); thresholds 2, 0.01, 2·B_j, 3, 0.90, 0.50 asserted "
         "against pool_n0E_v2 constants. ε: Σ_c = prompt-63 solver-seed chatter (EMULATOR_BO.md §1).")

# =============================================================================
# 4. Rule v2 seats
# =============================================================================
s, k = slide(f"Rule v2 seats V1 and E1; N4 clears its own bar 14× but fails the composition gate (residual Mantel p 0.025 "
             "vs 0.01), so it is co-reported, not seated",
             "POOL_N0E_STANDINGS_v2.md §7–§8, pool_ed1b_v2.csv, pool_pairs_v2.csv; GP_STATUS §6a", "11-24")
rows = [["Family", "v1 walk", "v1 Seed re-grade", "v2 (this read)", "Reason (v2)"],
        ["V", "V1", "V1", "V1", "OUTCOME, RESOLVED, ADEQUATE"],
        ["E", "E1", "E1", "E1", "OUTCOME, RESOLVED, ADEQUATE"],
        ["X", "—", "—", "—", f"X1 REDUNDANT given E1 (raw ρ {F.X1E1_RAW:.3f} / residual ρ {F.X1E1_RES:.3f})"],
        ["R", "—", "—", "—", "no OUTCOME candidate; R4 is a PROXY of E2 (start-up cost)"],
        ["N", "N1", "N1", "—", f"N4: IDR/B_j {F.N4_IDRB:.2f}, residual Mantel p {F.N4_MANTEL:.4f} > 0.01 → raw ρ with V1 "
                               f"{F.N4V1_RAW:.3f} → REDUNDANT; N1 is a PROXY"]]
table(s, Inches(0.45), Inches(1.3), Inches(12.4), rows, col_widths=[0.8, 1.1, 1.6, 1.4, 7.5], size=13, row_h=Inches(0.38))
bullets(s, Inches(0.45), Inches(3.75), Inches(12.4), Inches(3.25), [
    "Rule v2 was written after the v1 read (post hoc, disclosed). We expected V1 · E1 · N4; it returned V1 · E1, and we "
    "committed that without tuning. Rule v2 stays unchanged for the next dataset.",
    "Physics: the six slate sites share one PTDF on L252. N4's composition signal is the cost of diverted deliverable "
    "wind, and E1 already prices it (acceptance review, 2026-11-24).",
    "N4 stays in view: the 0.01 threshold was fixed before the read. N4 is still fitted and graded (holdout 48/48) and "
    "co-reported in every result. The next dataset is the real test of rule v2.",
    ("What N4 would need to take a seat: Appendix B (counterfactual).", {"color": MUTED, "size": 13}),
], size=15, space_after=8)
assert F.HOLD["N4"] == 48
notes(s, SRC_LINES[k] + ". Vectors: POOL_N0E_STANDINGS_v2.md §8 (v1 d706199, Seed re-grade baf77c3, v2). N4 / N1 / R4 "
         "roles, IDR_over_B, mantel_p_resid: pool_ed1b_v2.csv. ρ values: pool_pairs_v2.csv (X1|E1, N4|V1). Physics: "
         "ERCOT_GP_STATUS.md §6a (same PTDF) + power-systems acceptance review (admin PROGRESS 11-24). §8.14 departure and "
         "Kay's override: governance note in POOL_N0E_STANDINGS_v2.md. N4 holdout 48/48: ercot_gp_status.csv.")

# =============================================================================
# 5. House GPs
# =============================================================================
s, k = slide("The house GPs pass the holdout at n = 48 (V1 45/48, E1 48/48), and no smaller tier meets the n* rule",
             "ERCOT_GP_STATUS.md §0, §13.2; ercot_gp_status(_v2).csv; committed_configs.json; exposure_ledger.csv")
figure(s, FIGS / "fig_parity_holdout_V1E1.png", Inches(0.3), Inches(1.15), Inches(6.1), Inches(5.85), k, show_path=False,
       caption="Holdout parity, house fit, V1 and E1, n = 32 (top) and 48 (bottom); red = outside the 95 % band.")
bullets(s, Inches(6.55), Inches(1.2), Inches(6.45), Inches(5.8), [
    f"LOO RMSE at n = {F.N0}: V1 {F.LOO_V1 / 1e3:.1f}k MWh ({F.LOO_V1_B:.2f} B_j); E1 ${F.LOO_E1 / 1e6:.2f}M ({F.LOO_E1_B:.2f} B_j).",
    f"Co-reported: N4 {F.HOLD['N4']}/48; N1 {F.HOLD['N1']}/48 FAIL (recorded, not re-selected).",
    f"The capped optimizer (Adam, 700 steps) over-states the noise 2.7–4×: inferred noise / σ_c is "
    f"{F.NOISE_H['E1']:.2f} (E1) and {F.NOISE_H['V1']:.2f} (V1).",
    "LOO RMSE ratio n = 44 / 48: V1 1.120, E1 1.116 (> 1.1). No tier below 48 meets the rule.",
    f"Under the converged fit, LOO RMSE still falls {F.LFL_RBF:.3f}–{F.LFL_M52:.3f}× from 44 to 48 (same arm). "
    "The first BO rounds are model-learning rounds.",
    ("n* = 48 means that no smaller tier suffices. We did not test whether 48 suffices. The early front is not a claim.",
     {"bold": True, "color": ACCENT}),
], size=14, space_after=8)
notes(s, SRC_LINES[k] + ". Holdout: ercot_gp_status.csv holdout rows (exposure rows 2, 4, 6, 8 of exposure_ledger.csv). "
         "LOO RMSE: committed_configs_housefit.json loo_rmse / pool_ed1b_v2.csv B_j. Noise: ercot_gp_status.csv "
         "noise_over_sigma_c (selected arm, n = 48). Ratios at 44: committed_configs.json n_star_reason. Like-for-like "
         f"v2 ratios: ercot_gp_status_v2.csv loo_rmse (rbf+std 14,904/11,880; m52+std 17,372/13,520); {F.CROSS:.2f} is the "
         "cross-arm figure (m52+std at 44 / rbf+std at 48) = ERCOT_GP_STATUS.md §13.2. Figure: cropped (V1, E1 columns) "
         "from analysis/ercot_gp/figs/fig_parity_holdout.png (81ea382); the N4 / N1 columns are in the source figure.")

# =============================================================================
# 6. Fit v2
# =============================================================================
s, k = slide("Fit v2 commits E1 (48/48); V1's v2 fit is 2.3× more accurate but over-confident (37/48, P = 2e-5), "
             "so V1 keeps the house fit by the pre-registered fallback",
             "ERCOT_GP_STATUS.md §0, §13, §13.1b; ercot_gp_status_v2.csv; committed_configs(_housefit).json; exposure_ledger.csv")
figure(s, FIGS / "fig_parity_holdout_v2.png", Inches(0.3), Inches(1.2), Inches(5.6), Inches(5.8), k, show_path=False,
       caption="Fit v2 holdout parity + residual row (V1 left, E1 right).")
rows = [["fit v2 at n = 48", "V1 (rbf+std)", "E1 (m52+std)"],
        ["noise / σ_c", f"{F.NOISE_V2['V1']:.2f}", f"{F.NOISE_V2['E1']:.2f}"],
        ["LOO NLPD v2 / house", f"{F.NLPD['V1'][0]:.3f} / {F.NLPD['V1'][1]:.3f}", f"{F.NLPD['E1'][0]:.3f} / {F.NLPD['E1'][1]:.3f}"],
        ["holdout cov95 · rms z", f"{F.HOLD_V2['V1']}/48 FAIL · {F.RMSZ_V2['V1']:.2f}", f"{F.HOLD_V2['E1']}/48 PASS · {F.RMSZ_V2['E1']:.2f}"],
        ["holdout NLPD · RMSE, v2 vs house", f"{F.HNLPD['V1'][0]:.2f} · {F.HRMSE['V1'][0]:,.0f} vs {F.HNLPD['V1'][1]:.2f} · {F.HRMSE['V1'][1]:,.0f} MWh",
         f"{F.HNLPD['E1'][0]:.2f} · ${F.HRMSE['E1'][0] / 1e6:.2f}M vs {F.HNLPD['E1'][1]:.2f} · ${F.HRMSE['E1'][1] / 1e6:.2f}M"],
        ["committed definition", "house (fallback)", "fit v2 (AMENDMENT 11-24b)"]]
table(s, Inches(6.05), Inches(1.2), Inches(6.95), rows, col_widths=[2.3, 2.6, 2.05], size=11, row_h=Inches(0.3))
bullets(s, Inches(6.05), Inches(3.3), Inches(6.95), Inches(3.7), [
    f"Why V1 fit v2 fails: not chance (P = {P_STR}); a smooth-kernel misfit ({F.N_OUT} of 9 prompt-61 residuals "
    f"|z| > 1.96); LOO on a Sobol prefix is optimistic (holdout error {F.HO_OVER_LOO:.2f}× LOO).",
    "We designed fit v2 after we saw the house holdout (8 scorings; the diagnostic was coded 7 min later). It is a "
    f"second look, not a blind test. Exposure: {F.EXPO} of 24.",
    ("To pre-register in 55 B (report-only): V1's fit v2 posteriors logged beside the house fit every round; gate "
     "power per objective.", {"bold": True, "color": ACCENT}),
    "Proposal: a linear mean in total PEM MW for V1 before round 1 is a new fit definition. It needs a new amendment, "
    "and no holdout is left to test it (retired, 10 of 24). Run it report-only beside the house fit in rounds 1–4, and "
    "pre-register it for the next dataset.",
    ("Paper lesson: V1 needs structure (linear mean, additive or site-interaction kernel), not wider bars "
     "(acceptance review, 2026-11-24).", {"color": MUTED}),
], size=13, space_after=5)
assert F.EXPO == 10
notes(s, SRC_LINES[k] + ". Table: committed_configs.json (V1 v2_result; E1 hyperparameters, loo_nlpd_mean), "
         "committed_configs_housefit.json (house LOO NLPD), ercot_gp_status_v2.csv (holdout rows: cov95, rms z, NLPD, "
         "RMSE), ercot_gp_status.csv (house holdout NLPD/RMSE). Lengthscales, converged restarts and mode gaps: "
         f"Appendix D. P = binom.cdf(37, 48, 0.95). Residuals: ercot_gp_lc_residuals_v2.csv (P2_500_270 +{F.Z270:.2f}). "
         f"Holdout {F.HRMSE['V1'][0]:,.0f} vs LOO {F.V1v2['loo_rmse']:,.0f} MWh; bands narrower (sd 8,315 vs 12,106; "
         f"§13.1b). The data ask for more noise: V1 rbf {F.NOISE44:.2f} σ_c at n = 44, {F.NOISE_V2['V1']:.2f} at 48; the "
         f"prior mode is {F.PRIOR_MODE:.2f} σ_c. Provenance: ERCOT_GP_STATUS.md §0. Report-only item: ERCOT_GP_STATUS.md §0 "
         "'Consequences of the mixed commit' (3). The 'Proposal' line is Kay's recommendation, not a file statement. "
         "Paper lesson: GP-stats acceptance review (admin PROGRESS 11-24). Figure: analysis/ercot_gp/figs/"
         "fig_parity_holdout_v2.png (81ea382), copied.")
F.text_has(F.P["gpmd"], "Pre-register in 55, report-only: log the V1 v2-m52 and v2-rbf posteriors beside the house fit every round, and report gate power per objective.")

# =============================================================================
# 7. Machinery
# =============================================================================
s, k = slide("The 55 machinery runs end to end on the committed GPs (12/12 single, 15/15 multi lanes, C1 45/45) and "
             "caught a bug that wrote a PEM unit at fraction 5.55e-17",
             "EMULATOR_BO.md §A.1, §7, §8; emulator_E_summary_committed.json; emulator_E_multi_committed.csv")
rows = [["check (committed block)", "result", ""],
        ["runs finish; each lane ends where its scenario says", "single 12/12, multi 15/15", "PASS"],
        ["C1 ingest on every emulated round", "45/45", "PASS"],
        ["branches: s0 to the cap; s1 constrained from r2; s2 HALT", "s1 n_hv 55/63/71/79; s2 propose refused", "PASS"],
        ["fit v2 (E1) converged at every round fit", "multi 45/45, single 15/15 (60/60)", "PASS"],
        ["τ_exact = 0 → cap only; R2 / N1_off monitors", "cap only; monitors quiet", "PASS"]]
table(s, Inches(0.45), Inches(1.25), Inches(7.7), rows, col_widths=[3.6, 3.2, 0.9], size=13, row_h=Inches(0.5))
text_box(s, Inches(0.45), Inches(4.45), Inches(7.7), Inches(0.35), "Three changes to 55", size=15, bold=True, color=ACCENT)
bullets(s, Inches(0.45), Inches(4.82), Inches(7.7), Inches(2.2), [
    "b2b2142, zero-site fix (HIGH): a lower-bound optimum came back as 5.55e-17, and the writer built a <site>_PEM unit. "
    "Now snap_bounds sets the value to 0, and the writer refuses u in (0, 1e-9).",
    "c7576a6 + c470d7b: the r1 cross-seed assert checks that the seed sets differ (prompt 55 §2.1). A second assert "
    "hardens it.",
    "0066a64: the HALT file printed a literal file name. We fixed the f-string.",
], size=13, space_after=5)
card(s, Inches(8.4), Inches(1.25), Inches(4.55), Inches(3.75))
text_box(s, Inches(8.55), Inches(1.33), Inches(4.3), Inches(3.6), [
    ("NOT exercised here", {"bold": True, "color": WARN, "size": 15}),
    "•  submit_state_E.py",
    "•  acquire_E_job.sh",
    "•  CRC array and collector scripts",
    "•  ercot-bot commit / push",
    "•  a real __ALL__ wave ingest",
    "•  SUSPECT runs",
    "•  resume after HALT",
    ("These run first on CRC, one lane first (backup B3).", {"color": MUTED, "size": 13}),
], size=14, space_after=4)
notes(s, SRC_LINES[k] + ". Pass/fail: emulator_E_summary_committed.json pass_fail 1, 2, 6, 7, 8; n_hv per round: "
         "emulator_E_multi_committed.csv (s1). Changes: EMULATOR_BO.md §7 items 2–5 (5.55e-17: item 4). NOT exercised: "
         "§8 'Code paths NOT exercised here' (a true R2 flag and the Part B asserts are also not exercised).")

# =============================================================================
# 8. Emulator search
# =============================================================================
s, k = slide(f"On the emulator, BO ends just above a no-search plug-in (HV {F.HV_LO:.3f}–{F.HV_HI:.3f} vs {F.SPREAD:.3f}): "
             "the dry run tests the machinery, not the search",
             "emulator_E_{multi,single}_committed.csv, summary_committed, EMU_extras_committed.json; EMULATOR_BO.md §A.2–A.5")
figure(s, FIGS / "fig_hv_committed_5series.png", Inches(0.25), Inches(1.15), Inches(7.6), Inches(5.85), k, show_path=False)
bullets(s, Inches(7.95), Inches(1.2), Inches(5.05), Inches(5.8), [
    f"Baselines at r4 ({F.NREP:,} reps): uniform p5/p50/p95 {F.UNI[0]:.3f}/{F.UNI[1]:.3f}/{F.UNI[2]:.3f}; random "
    f"vertices p95 {F.VERT95:.3f}; r0 plug-in front, no search, {F.SPREAD:.3f}.",
    (f"Circularity: the truth is the GP's own posterior mean through the same {F.N0} points. So the r0 GP already "
     f"knows the optimum (plug-in regret V1 {F.PLUG_V1:.3f} B_j, E1 ≈ 0).", {"bold": True}),
    f"Mismatch B (V1 truth = fit v2 mean; 1 seed): the optimum is the all-PEM vertex. The plug-in error is "
    f"{F.MMB_PLUG:.2f} B_j. BO reaches regret 0.002 B_j (best evaluated design, r2). At r4 the posterior-mean incumbent "
    f"is at {F.MMB_PM4:.3f} B_j and the best observation at {F.MMB_BO4:.3f} B_j.",
    "Winner's curse: the best observation carries −0.76 / −1.40 sd of noise (r3 / r4). Report incumbents by "
    "posterior mean.",
    "f*(E1) at the no-PEM vertex is a smooth-trend claim (0.34 lengthscales from the data), not data.",
], size=12, space_after=6)
notes(s, SRC_LINES[k] + ". HV: emulator_E_multi_committed.csv hv_true_frac_best, s0, round 4 (5 lanes). Baselines and "
         "plug-in: EMU_extras_committed.json baselines[*][4], r0_plugin.committed. Mismatch B: "
         "emulator_E_single_committed.csv variant mmB (r0_plugin_regret_B, regret_pm_opt_B, regret_best_obs_B); all-PEM "
         "vertex, 0.002 B, −0.76 / −1.40 and 0.34 lengthscales: EMULATOR_BO.md §A.5 / §A.0. Figure: "
         "figs/fig_hv_committed_5series.png, re-rendered here from emulator_E_multi_committed.csv + "
         "EMU_extras_committed.json (committed truth only; 5 legend entries; assert-before-draw); the full source "
         "figure is analysis/emulator_E/figs/fig_EMU_multi_hv_committed.png (de45242).")

# =============================================================================
# 9. Calibration
# =============================================================================
s, k = slide("The calibration gates cannot see a V1 misfit (house bands ≈ 6× too wide); the one E1 flag came at a "
             f"replicated design, where fit v2 set the noise at about half the actual ({F.RHO_REP:.2f}×)",
             "EMULATOR_BO.md §A.0, §A.3; emulator_E_single_committed.csv; emulator_E_summary_committed.json")
figure(s, FIGS / "fig_EMU_calibration_committed.png", Inches(0.3), Inches(1.2), Inches(12.7), Inches(3.5), k,
       show_path=False)
bullets(s, Inches(0.45), Inches(4.75), Inches(7.35), Inches(2.25), [
    f"V1: rms z median {F.RMSZ_V1:.2f}; C2 0, C3 0. The house bands are ≈ 6× too wide.",
    f"The E1 C2 + C3 event: 8 identical designs at u = 0, observed twice in r1. The fit noise ({F.FIT_NOISE:.3f} σ_c) is "
    f"below the emulator noise ({F.EMU_NOISE:.3f} σ_c; ρ {F.RHO_REP:.2f}), so coverage is {F.REP_COV:.2f}. P(C2) per "
    "such batch: 0.10 (executor), 0.22 (reviewer).",
    f"Across all E1 fits: {F.NOE_LO:.2f}–{F.NOE_HI:.2f}× the emulator noise.",
    f"Multi path: {F.MULTI_C2}/{F.MULTI_N} flags. Single-objective E1 replicates u = 0 in {F.ORIG} of 72 r2–r4 designs.",
    "C2 and C3 are REVIEW flags. They never halt.",
], size=12, space_after=3)
card(s, Inches(7.95), Inches(4.8), Inches(4.95), Inches(1.75))
text_box(s, Inches(8.05), Inches(4.85), Inches(4.75), Inches(1.65), [
    ("What tells us a GP is wrong in round 1?", {"bold": True, "color": ACCENT}),
    "Today: the report-only V1 fit v2 posterior log and E1's REVIEW flags.",
    "Proposed trigger (for 55 B): a REVIEW flag on a non-replicated batch, or |posterior mean − PCM| > 2 B_j on any "
    "design, opens a model review before round 2.",
], size=12, space_after=3)
notes(s, SRC_LINES[k] + ". V1: summary_committed per_objective_gates.V1. Event: emulator_E_single_committed.csv E1 bo seed 0 "
         "(r1 n_at_origin 2; r2 cov95 3, C2, C3; r1 noise_over_sigma_c 0.676, noise_over_chatter 0.531); emulator noise "
         "= 0.676 / 0.531 = 1.274 σ_c; coverage 2Φ(1.96ρ) − 1. P(C2) 0.10 / 0.22: EMULATOR_BO.md §A.0 item 3. Multi C2: "
         "emulator_E_multi_committed.csv (45 graded rows). 71/72: n_at_origin r2–r4. Noise range: noise_over_chatter "
         "(single E1) ∪ E1_noise_over_emulator (multi). The proposed trigger is Kay's proposal for 55 Part B, not a "
         "file rule. Figure: analysis/emulator_E/figs/fig_EMU_calibration_committed.png (de45242), copied.")

# =============================================================================
# 10. Seed lanes
# =============================================================================
s, k = slide(f"Seed lanes converge on box vertices: {F.DUP} of 40 round-1 PCM runs would repeat another lane's design — "
             "reuse by design key, or run all and disclose",
             "runs_compact/EMU_extras_committed.json (seed_overlap); EMULATOR_BO.md §A.4; pi-agenda E-D4", "11-14")
rows = [["committed block, 5 lanes", "r1", "r2", "r3", "r4"],
        ["unique designs of 40", *[str(u) for u in F.UNIQ]]]
table(s, Inches(0.45), Inches(1.35), Inches(8.0), rows, col_widths=[3.2, 1.2, 1.2, 1.2, 1.2], size=15, row_h=Inches(0.48))
bullets(s, Inches(0.45), Inches(2.55), Inches(12.4), Inches(4.4), [
    f"Lane-set Jaccard {F.JAC[0]:.2f}–{F.JAC[1]:.2f}. Closest re-proposal of an evaluated design: {F.MIND:.3f} in u (none "
    "within 1e-6).",
    f"Cost of running all: {F.DUP} runs × 21–45 core-h ≈ 340–720 core-h.",
    "The PCM is deterministic (τ_exact = 0). A repeat run returns the same y, so reuse changes no posterior.",
    ("The five lanes are correlated either way. They cannot support a seed-dispersion claim.", {"bold": True, "color": ACCENT}),
    ("Reuse needs one 55 B item: the HV ledger must count a shared design once.", {"color": MUTED}),
], size=16, space_after=10)
notes(s, SRC_LINES[k] + ". unique per round, jaccard_range, min_dist, r1_duplicate_runs_of_40: EMU_extras_committed.json "
         "seed_overlap. Core-h: plan AMENDMENT 2026-11-14 (wave-D actuals 21 fast – 44.6 slow per run) and pi-agenda E-D4 "
         "row (≈ 340–720 at 21–45). The house block's overlap (first run) is on backup B4 only.")

# =============================================================================
# 11. DECISION
# =============================================================================
s, k = slide("Four decisions today, then nine Part B items, unlock round 1; the first two need no new runs, the third "
             "avoids up to ≈ 720 core-h",
             "pi-agenda 11-24 rows; pi_agenda_E-D7_draft.md; EMULATOR_BO.md §A.7, §8; PROGRESS Prompt 66")
dec = [
    (1.38, "E-D1b · objectives",
     ["(a) Accept M = 2 (V1 · E1), and ratify the rule-v2 departure and the one holdout re-open.",
      f"(b) Revert to v1: V1 · E1 · N1, where N1 is a proxy (ρ {F.N1V1_RAW:.2f} with V1); M = 3 re-derives R, τ and the gates.",
      "Cost: no new runs."],
     "Recommend: accept M = 2.",
     "Changes it: if location must be its own objective, neither option gives it; that needs a new rule for the next "
     "dataset."),
    (1.02, "E-D7 + fit item (ratify) · n₀ and the GP fit",
     [f"{F.N0}, mixed fit (the only tier that meets the n* rule); 32 / 44 fail the rule. Cost: no new runs."],
     f"Recommend: {F.N0} with the mixed commit (V1 house, E1 fit v2), as the pre-registered fallback produced it.",
     "Changes it: nothing without new data."),
    (1.15, "E-D4 (part) · duplicate runs",
     [f"Run all ({F.DUP} extra r1 runs, ≈ 340–720 core-h), or reuse by design key (HV ledger de-dup, built in 55 B)."],
     "Recommend: reuse by design key (the PCM is deterministic).",
     "Changes it: a decision to claim seed dispersion. Then run all; the claim is still weak."),
    (1.78, "55 Part B rules · one bundle, line by line",
     ["(1) Duplicate slot → re-optimize the slot without the evaluated designs (default), or a replicate.",
      "(2) A C2 REVIEW on a replicated design = review, no halt.",
      "(3) Accept the r1 cross-seed assert change (c7576a6 + c470d7b).",
      "(4) The R1 claims filter also applies to N3 and N1_off.",
      f"(5) Round-1 model-review trigger (slide {SL['calib']}): approve now, or defer to 55 B."],
     "Recommend: approve (1)–(4); (5) is your choice.",
     "Changes it: a flag on any line. That line waits; the others go ahead."),
]
y = 1.2
for hh, name, opts, rec, chg in dec:
    card(s, Inches(0.35), Inches(y), Inches(12.65), Inches(hh - 0.06), line=ACCENT)
    text_box(s, Inches(0.45), Inches(y + 0.02), Inches(7.75), Inches(hh - 0.08),
             [(name, {"bold": True, "color": ACCENT, "size": 14})] + [(o, {}) for o in opts], size=13, space_after=1)
    text_box(s, Inches(8.3), Inches(y + 0.02), Inches(4.65), Inches(hh - 0.08),
             [(rec, {"bold": True, "color": GREEN}), (chg, {"color": INK})], size=13, space_after=2)
    y += hh
text_box(s, Inches(0.45), Inches(y + 0.01), Inches(12.5), Inches(0.42),
         f"Launch: after the {n_block} blocking items (B3); date to be set by Kay. Round 1 = 8 PCM runs × 5–11 h wall per "
         "lane; acquisition < 1 % of a round.", size=12, bold=True)
F.text_has(F.AGENDA, "Options: (a) 48 recommended; (b) 32 (already scored, PASS, 1.5–1.9× RMSE); (c) 44 only under a 1.12 bar.")
F.text_has(F.PLAN, "this is the one override of this campaign; a second one HALTs")
notes(s, SRC_LINES[k] + ". The 'Recommend' lines are Kay's recommendations (no file holds them as decisions; the strategy "
         "rows in pi-agenda carry the same E-D4 and E-D7 recommendation). E-D1b: pi-agenda E-D1b UPDATE 11-24; option (a) "
         "ratifies the §8.14 departure and the 24b §4 holdout re-open; N1 residual IDR/B_j "
         f"{F.N1_RESID:.2f} (pool_ed1b_v2.csv), raw ρ with V1 (pool_pairs_v2.csv); one override per campaign: plan "
         "AMENDMENT 2026-11-24 §2.5. E-D7: pi-agenda E-D7 row + pi_agenda_E-D7_draft.md; rejected alternatives: a second "
         "re-open (forbidden), V1 m52 fit v2 (re-selection after scoring), both house (discards E1's gain). E-D4: "
         "pi-agenda E-D4 (part) row. 55 B bundle: pi-agenda E-D4 row + ERCOT PROGRESS Prompt 66 'Decisions for Kay' + "
         "admin PROGRESS 11-24 (claims filters); line (5) = the proposal on slide 9. Round wall: EMULATOR_BO.md §8 "
         "runtime note. Next dataset: V1 structure in the GP; a continuous congestion metric; the fit definition "
         "pre-registered.")

# =============================================================================
# Backup
# =============================================================================
k = nxt()
section_slide(prs, "BACKUP", "Backup slides B0–B5 and Appendices A–D",
              "B0 station map · B1 training-size study under fit v2 · B2 RTS 49 V1 arm · B3 the 55 Part B checklist · "
              "B4 house-fit emulator block · B5 figures not shown · A process log · B rule-v2 standings · "
              "C matched-budget baselines · D fit definitions", n=k)
SRC_LINES[k] = ""

# B0 station map
s, k = slide("Is the ERCOT BO ready for its first real round, and what must be decided first?",
             "admin/prompt/bogp/ercot-station-map.md (stations 3, 4, 6); admin PROGRESS 11-24; EMULATOR_BO.md §8")
steps = [("65", "rule v2", "objectives V1 · E1", "DONE", GREEN),
         ("54", "GP fit + holdout", f"n₀ = {F.N0}; V1 house, E1 fit v2", "DONE", GREEN),
         ("66", "emulator BO", "55 machinery, no PCM", "DONE", GREEN),
         ("55 B", "Part B", f"13 items: {n_done} done, {n_open} open ({n_block} blocking)", "OPEN", AMBER),
         ("56", "launch", "Kay submits round 1", "OPEN", AMBER)]
x0, wbox, gap = 0.45, 2.25, 0.27
for i, (num, name, sub, st, col) in enumerate(steps):
    x = Inches(x0 + i * (wbox + gap))
    card(s, x, Inches(1.45), Inches(wbox), Inches(1.75), line=ACCENT)
    text_box(s, x, Inches(1.52), Inches(wbox), Inches(0.5), num, size=20, bold=True, color=ACCENT, align=PP_ALIGN.CENTER)
    text_box(s, x, Inches(1.98), Inches(wbox), Inches(0.4), name, size=14, bold=True, align=PP_ALIGN.CENTER)
    text_box(s, x, Inches(2.33), Inches(wbox), Inches(0.45), sub, size=11, color=MUTED, align=PP_ALIGN.CENTER)
    chip(s, x + Inches(0.6), Inches(2.8), Inches(wbox - 1.2), Inches(0.32), st, col, size=11)
    if i < len(steps) - 1:
        text_box(s, x + Inches(wbox - 0.02), Inches(2.05), Inches(gap + 0.05), Inches(0.4), "→", size=18,
                 bold=True, color=ACCENT2, align=PP_ALIGN.CENTER)
text_box(s, Inches(0.5), Inches(3.5), Inches(12.3), Inches(0.4), f"The four decisions for today (slide {SL['decision']})",
         size=16, bold=True, color=ACCENT)
bullets(s, Inches(0.5), Inches(3.95), Inches(12.3), Inches(2.9), [
    "E-D1b: the objectives. Accept M = 2 (V1 · E1) under rule v2, or revert to the v1 vector.",
    f"E-D7 + the fit item: start at n₀ = {F.N0} with the mixed GP fit (V1 house, E1 fit v2).",
    "E-D4 (part): duplicate PCM runs across the seed lanes. Reuse by design key, or run all.",
    "55 Part B rules: the duplicate-slot rule, the meaning of a C2 flag on a replicate, the r1 assert change, "
    "the claims filters, the round-1 review trigger.",
], size=15, space_after=8)
notes(s, SRC_LINES[k] + ". Station rows: ercot-station-map.md §2 (3. Model validation, 4. BO loop, 6. Baseline + "
         "launch). States: admin PROGRESS 11-24 entries. 55 B counts: EMULATOR_BO.md §8 with the DONE marks of §A.6–A.7 "
         "(backup B3).")

# B1 (two slides)
for part, (fname, who) in enumerate((("fig_training_size_curves_v2_V1E1.png", "seated V1, E1"),
                                     ("fig_training_size_curves_v2_N4N1.png", "co-reported N4, N1")), 1):
    s, k = slide(f"Training-size study under fit v2 ({part}/2, {who}): LOO RMSE, NLPD, coverage and inferred noise "
                 "still move from 44 to 48",
                 "ercot_gp_nstar_checks_v2.csv, ercot_gp_status_v2.csv, ERCOT_GP_STATUS.md §13")
    figure(s, FIGS / fname, Inches(0.3), Inches(1.1), Inches(6.6), Inches(5.9), k, show_path=False)
    rows_lines = ["Rows, top to bottom: LOO RMSE / RMSE₄₈; LOO NLPD; LOO cov95 / n (grey = binomial 90 % region); "
                  "inferred noise / σ_c. Red dashed line: n* = 48. Black: the selected arm."]
    if part == 1:
        rows_lines.append((f"The inferred-noise plateau at {F.PRIOR_MODE:.2f} σ_c is the prior's MAP mode (e^(−½)·σ_c). "
                           f"V1 rbf leaves it at 44–48 ({F.NOISE44:.2f}, {F.NOISE_V2['V1']:.2f} σ_c).",
                           {"bold": True, "color": ACCENT}))
    else:
        rows_lines.append(("N4 and N1 are co-reported only. They never decide n*.", {"bold": True, "color": ACCENT}))
    text_box(s, Inches(7.1), Inches(1.4), Inches(5.9), Inches(5.4), rows_lines, size=15, space_after=12)
    notes(s, SRC_LINES[k] + f". Figure: cropped ({who}) from analysis/ercot_gp/figs/fig_training_size_curves_v2.png "
             "(81ea382); no pixel redrawn.")

# B2
s, k = slide("RTS 49 V1 arm (cap 4, 64 designs): the old-floor τ stops at rounds 3–4, the measured rulers never do, "
             "and the gains are not monotone (r4 > r3)",
             "RTS-GMLC campaign/analysis/methods_C/V1/ledger.json (d6 8ed4c01)")
R = F.RTS
rows = [["round", "HV", "gain", "gain / τ_old", "gain / τ_285", "gain / τ_het"]]
for kk in (1, 2, 3, 4):
    e = R[kk]
    rows.append([f"r{kk}", f"{e['hv'] / 1e17:.3f} × 10¹⁷", f"{e['gain'] / 1e16:.2f} × 10¹⁶",
                 f"{e['gain_tau']:.3g}" + (" (would stop)" if e["would_stop"] else ""),
                 f"{e['gain_tau_285']:.2f}", f"{e['gain_tau_het']:.3g}"])
table(s, Inches(0.45), Inches(1.35), Inches(12.4), rows, col_widths=[1, 2, 2, 2.6, 2, 2], size=15, row_h=Inches(0.5))
lz = F.LRZ
bullets(s, Inches(0.45), Inches(4.1), Inches(12.4), Inches(2.9), [
    f"r4 LOO rms z: shed {lz['load_shed_mwh']:.2f}, curtailment {lz['true_curtailment_mwh']:.2f}, cost {lz['total_cost_less_synthetic_usd']:.2f}.",
    "The old-floor ruler would stop at r3 and r4. The measured rulers (τ_285, τ_het) never stop.",
    "The r4 gain is larger than the r3 gain. Gains are not monotone.",
], size=16, space_after=8)
notes(s, SRC_LINES[k] + ". entries[1..4]: hv, gain, gain_tau (τ_old), gain_tau_285, gain_tau_het, would_stop*, "
         "loo_rms_z; read with git show d6:… (no checkout).")

# B3
s, k = slide(f"What blocks round 1: the 55 Part B checklist (13 items: {n_done} done, {n_open} open, {n_block} blocking) "
             "plus one report-only item",
             "EMULATOR_BO.md §8, §A.6–A.7; committed_configs.json; ERCOT_GP_STATUS.md §0")
chk = [
    ("DONE", "1. Zero-site fix (b2b2142) and its two tests (the real-loader ingest test is item 11)."),
    ("BLOCKS", "2. Duplicate-proposal rule; idempotent grade_round; commit before propose."),
    ("DONE", "3. Fit v2 in qnehvi_E per fit_definition (36b74b7 hook); convergence flag recorded."),
    ("DONE", "4. New committed_configs.json (240bde1); dry run rerun on it."),
    ("BLOCKS", "5. E-D7 decided in committed_configs.json (the Part B guard is done)."),
    ("BLOCKS", "6. E-D5 amendment appended; README wording."),
    ("BLOCKS", "7. arms_E.json complete: gp.train = fit v2, part = B; R3 / N3 / N1_off wired."),
    ("BLOCKS", "8. τ_res written into the ledger."),
    ("OPEN (non-blocking)", "9. Stale README / runbook text (M = 4, 'pairwise distinct')."),
    ("BLOCKS", "10. dry_round_E.py aligned with the r1 change; tests for the c7576a6 branches."),
    ("BLOCKS", "11. Real-loader ingest test on a fake __ALL__ methods_E wave."),
    ("BLOCKS", f"12. Kay's duplicate-run decision (slide {SL['lanes']})."),
    ("BLOCKS", "13. CRC: --check-env, GAP_DECISION.json, --dry-run; then one lane first."),
    ("OPEN (non-blocking)", "+ Report-only, to pre-register in 55 B: V1's fit v2 posteriors beside the house fit every "
                            "round; gate power per objective."),
]
assert sum(1 for c_, _ in chk[:13] if c_ == "DONE") == n_done and sum(1 for c_, _ in chk[:13] if c_ == "BLOCKS") == n_block
assert F.cc["E-D7_decided"] is None
y = 1.2
for st, txt in chk:
    col = GREEN if st == "DONE" else (WARN if st == "BLOCKS" else MUTED)
    chip(s, Inches(0.45), Inches(y + 0.04), Inches(2.0), Inches(0.33), st, col, size=10)
    text_box(s, Inches(2.6), Inches(y), Inches(10.4), Inches(0.41), txt, size=13, anchor=MSO_ANCHOR.MIDDLE)
    y += 0.415
notes(s, SRC_LINES[k] + ". Items 1–13 from EMULATOR_BO.md §8; DONE marks from §A.6 / §A.7 (hook 36b74b7, configs 240bde1, "
         "Part B guard 4aad620). 'BLOCKS' = must close before round 1 is submitted (deck marking); item 9 is text only. "
         "The report-only item comes from ERCOT_GP_STATUS.md §0 ('Consequences of the mixed commit' (3)); it is not in §8.")

# B4 (HOUSE block — the only slide with house-block numbers)
s, k = slide("House-fit emulator block: the same machinery on the unconverged GPs — superseded items marked",
             "emulator_E_summary.json, runs_compact/EMU_extras.json, EMU_rerun_check.json (house); EMULATOR_BO.md §B")
bullets(s, Inches(0.45), Inches(1.35), Inches(12.4), Inches(5.6), [
    f"s0 r4 HV fraction of the best-known front: {F.H_S0R[0]:.3f}–{F.H_S0R[1]:.3f} (committed block: {F.HV_LO:.3f}–{F.HV_HI:.3f}).",
    f"r0 plug-in regret V1 / E1: {F.H_PLUG[0]:.3f} / {F.H_PLUG[1]:.3f} B_j. SUPERSEDED for E1 (committed block: E1 ≈ 0).",
    "Seed overlap, unique designs of 40 per round r1–r4: " + " / ".join(str(u) for u in F.H_UNIQ)
    + f"; {F.H_DUP} duplicate r1 runs. SUPERSEDED by the committed block (slide {SL['lanes']}).",
    f"C2 / C3: 0 in 114 cells. This shows no power, not a pass: the house bands are too wide. SUPERSEDED (slide {SL['calib']}).",
    f"Path sensitivity (still valid): a 1e-16 input change (5.55e-17 → 0) re-routes lanes from r2. Aggregates move "
    f"≤ {F.H_HV:.1f} % in HV. Lane trajectories do not reproduce; aggregates do.",
], size=16, space_after=10)
notes(s, SRC_LINES[k] + ". House block = first run, kept as run (EMULATOR_BO.md §B). s0_r4_frac_best, pass_fail[3]: "
         "emulator_E_summary.json; r0_plugin.house, seed_overlap: EMU_extras.json; max_true_hv_rel_change: EMU_rerun_check.json.")

# B5
s, k = slide("Figures not shown", "analysis/ercot_gp/figs/, analysis/emulator_E/figs/ (paths below)")
bullets(s, Inches(0.45), Inches(1.35), Inches(12.4), Inches(5.6), [
    ("ercot_gp/figs/fig_lengthscales_vs_n_v2.png", {"bold": True}),
    ("The 55 % lengthscale change at n = 48 is an arm switch (m52+std → rbf+std), not instability.", {"level": 1}),
    ("ercot_gp/figs/fig_house_vs_longfit.png", {"bold": True}),
    ("The diagnostic that triggered AMENDMENT 2026-11-24b (house fit vs 10,000-step fit).", {"level": 1}),
    ("emulator_E/figs/fig_EMU_front_committed.png", {"bold": True}),
    ("Both front ends lie outside the R box; V1 below the lowest observed value (1.409 TWh) is extrapolation.", {"level": 1}),
    ("emulator_E/figs/fig_EMU_single_regret_committed.png", {"bold": True}),
    ("Single-objective regret; the E1 replicate collapse at u = 0 is marked.", {"level": 1}),
    ("emulator_E/figs/fig_EMU_multi_hv_committed.png", {"bold": True}),
    (f"The full HV figure (also s2 and the mismatch lanes); slide {SL['emu']} shows a 5-series re-render.", {"level": 1}),
], size=15, space_after=6)
F.text_has(F.P["gpmd"], "The 55 % lengthscale change at n = 48 is an arm switch (m52+std → rbf+std), not instability.")
F.text_has(F.P["emumd"], "below the lowest observed V1 (1.409 TWh)", "Both front end points lie outside the R box")
notes(s, SRC_LINES[k] + ". Lines: ERCOT_GP_STATUS.md §13.2 (arm switch); plan AMENDMENT 2026-11-24b (diagnostic); "
         "EMULATOR_BO.md §1 caution + 'Limits of this test' (front ends, 1.409 TWh); §A.3 (replicate collapse).")

# =============================================================================
# Appendix A — process log
# =============================================================================
s, k = slide("Appendix A: process log — step · SHA · author time (git log --format=%ai) · review",
             "git log --format=%ai on ercot/tx123 and d6; reviews: admin PROGRESS 11-24 (acceptance reviews)")
verdict = {"aa98045": "65: ACCEPT WITH NOTES ×2", "b23021c": "54 B: ACCEPT WITH NOTES · FIX THEN SHIP",
           "240bde1": "54 v2: ACCEPT WITH NOTES", "76c1ae6": "66: ACCEPT WITH NOTES ×2 · FIX THEN SHIP",
           "7457043": "66 v2: ACCEPT WITH NOTES"}
rowsA = [(step, what, sha, ai, verdict.get(sha, "")) for step, what, sha, ai in F.APPA]
rowsA.append(("RTS 49", "V1 arm r4 graded — DONE (hard cap)", "8ed4c01", F.RTS_AI, ""))
rowsA.sort(key=lambda r: r[3])
table(s, Inches(0.35), Inches(1.15), Inches(12.65), [["step", "what", "SHA", "author time (git)", "review"]] + [list(r) for r in rowsA],
      col_widths=[0.85, 4.6, 0.95, 2.5, 3.75], size=9, row_h=Inches(0.245))
text_box(s, Inches(0.35), Inches(6.72), Inches(12.6), Inches(0.3),
         "Author time; eb8c2da rebased, committed 03:22. Times are git times, not PROGRESS clock times.", size=10, color=MUTED)
notes(s, SRC_LINES[k] + f". All SHAs asserted as ancestors of ercot/tx123 (RTS: d6). eb8c2da committer time {F.EB_CI}.")

# =============================================================================
# Appendix B — standings (two slides) + formula / floors / counterfactual
# =============================================================================
cols = ["id", "role", "B_j", "IDR/B_j [lo90]", "resid IDR/B_j", "η²_T", "Mantel p raw / resid", "status"]
order = ed1b.sort_values("global_order").index.tolist()


def gnum(v):
    if v != v:
        return "—"
    a = abs(v)
    return f"{v / 1e6:.3g}M" if a >= 1e6 else (f"{v / 1e3:.3g}k" if a >= 1e3 else f"{v:.3g}")


rowsB = []
for j in order:
    r = ed1b.loc[j]
    rowsB.append([j, str(r["role"]), gnum(r["B_j"]),
                  "—" if r["IDR_over_B"] != r["IDR_over_B"] else f"{r['IDR_over_B']:.2f} [{r['IDR_over_B_lo90']:.2f}]",
                  "—" if r["resid_IDR_over_B"] != r["resid_IDR_over_B"] else f"{r['resid_IDR_over_B']:.2f}",
                  "—" if r["eta2_T"] != r["eta2_T"] else MINUS(r["eta2_T"], 3),
                  "—" if r["mantel_p_raw"] != r["mantel_p_raw"] else f"{r['mantel_p_raw']:.4f} / {r['mantel_p_resid']:.4f}",
                  str(r["status"])])
assert len(rowsB) == 28
for part, chunk in ((1, rowsB[:14]), (2, rowsB[14:])):
    s, k = slide(f"Appendix B ({part}/3): full rule-v2 standings, global order ({len(rowsB)} rows)",
                 "analysis/pool/pool_ed1b_v2.csv", "11-24")
    table(s, Inches(0.35), Inches(1.2), Inches(12.65), [cols] + chunk,
          col_widths=[0.5, 2.35, 0.85, 1.4, 0.95, 0.7, 1.6, 3.6], size=10, row_h=Inches(0.36))
    notes(s, SRC_LINES[k] + ". Sorted by global_order. Columns: B_j, IDR_over_B, IDR_over_B_lo90, resid_IDR_over_B, "
             "eta2_T, mantel_p_raw, mantel_p_resid, status (full strings).")

s, k = slide("Appendix B (3/3): the bar B_j, the materiality floors, and the N4 counterfactual",
             "plan AMENDMENT 2026-11-24 inst. 1, 5, 6; pool_ed1b_v2.csv; pool_pairs_v2.csv; pool_n0E_v2.steiger", "11-24")
headed(s, Inches(0.45), Inches(1.3), Inches(12.4), Inches(5.7), [
    ("H", "Bar"),
    "B_j = max(3√2·s_j, max|δ|);  s_j² = (6·s²(pert) + 16·s²(seed)) / 22;  degrees of freedom 22 (D1, D2: 20).",
    ("H", "Materiality floors (set after the relative responses were seen)"),
    f"V1 {F.FLOORS['V1']:,.0f} MWh · E1 ${F.FLOORS['E1'] / 1e6:.2f}M · X1 {F.FLOORS['X1']:,.0f} t · N4 {F.FLOORS['N4']:.1f} h.",
    ("H", "N4 counterfactual (not a result; the rule allows no second override)"),
    f"Suppose N4 had passed the composition gate (residual Mantel p ≤ 0.01; it read {F.N4_MANTEL:.4f}). Then the N4–V1 "
    f"pair is a BORDERLINE-PAIR: residual ρ {F.RHO['N4|V1']['rho_resid']:.3f}, and its 90 % interval "
    f"[{F.N4V1_RES_LO:.3f}, {F.N4V1_RES_HI:.3f}] contains 0.50.",
    f"§4b via the seated E1: residual ρ(N4, E1) {MINUS(F.rcs, 3)}, upper-90 {MINUS(F.N4E1_UP, 3)} ≤ −0.50; Steiger Z "
    f"{MINUS(F.STEIGER_Z, 2)} (one-sided p {F.STEIGER_P:.1e}, n_eff {F.PV2.STEIGER_N}; recomputed at build). The pair is "
    "then NOT REDUNDANT, N4 takes a seat, and M = 3.",
    "Reviewer items (acceptance review, 2026-11-24): the residual Mantel p reads 0.023–0.027 across permutation seeds; "
    "with that clause passed, §4b would seat N4.",
], size=14, space_after=6)
notes(s, SRC_LINES[k] + ". Steiger: pool_n0E_v2.steiger(ρ_res(N4,E1), ρ_res(E1,V1), ρ_res(N4,V1)) on pool_pairs_v2.csv "
         "rho_resid (logged in ASSERTIONS.md). Floors: pool_ed1b_v2.csv floor_M (disclosed as post hoc in plan "
         "AMENDMENT 2026-11-24 inst. 5). Bin sensitivity is not printed (no file).")

# =============================================================================
# Appendix C — matched-budget baselines per truth
# =============================================================================
s, k = slide("Appendix C: emulator matched-budget baselines at r4 under three truths (committed / mismatch A / mismatch B)",
             "EMU_extras_{committed,mmA,mmB}.json (baselines, r4); emulator_E_multi_committed.csv (s0 seed 0, r4)")
rows = [["truth (V1 / E1)", "random vertices p95", "r0 plug-in spread", "BO s0 seed 0"]]
lab = {"committed": "committed (house / fit v2)", "mismatch A": "mismatch A (house / house)",
       "mismatch B": "mismatch B (fit v2 / fit v2)"}
for kk, v in F.APPC.items():
    rows.append([lab[kk], f"{v[0]:.3f}", f"{v[1]:.3f}", f"{v[2]:.3f}"])
table(s, Inches(0.45), Inches(1.4), Inches(12.4), rows, col_widths=[4, 2.8, 2.8, 2.8], size=16, row_h=Inches(0.55))
bullets(s, Inches(0.45), Inches(4.0), Inches(12.4), Inches(2.8), [
    "Each truth is scored against the best-known front of its own truth.",
    "BO ends above the plug-in spread under every truth, by a small margin. One seed per mismatch.",
], size=16, space_after=8)
notes(s, SRC_LINES[k] + ". baselines.vertices.p95[4], baselines.plugin_spread.p50[4]; BO = hv_true_frac_best, variant "
         "committed / mmA / mmB, s0, seed 0, round 4.")

# =============================================================================
# Appendix D — fit definitions
# =============================================================================
s, k = slide("Appendix D: the two GP fit definitions in use", "committed_configs.json (fit_v2_spec); EMULATOR_BO.md §1; arms_E.json gp.train")
ls = lambda v: " / ".join(f"{x:.2f}" for x in v)  # noqa: E731
text_box(s, Inches(0.45), Inches(1.3), Inches(12.4), Inches(5.7), [
    ("Fit v2 (E1; AMENDMENT 2026-11-24b): fit_v2_spec, verbatim", {"bold": True, "color": ACCENT}),
    (F.FIT_V2_SPEC, {"size": 13}),
    (f"At n = {F.N0}: lengthscales in u (sites 110 / 140 / 146 / 163 / 270 / 274) — V1 fit v2 {ls(F.LS_V1)}; "
     f"E1 fit v2 {ls(F.LS_E1)}. Converged restarts: V1 {F.CONV['V1']}/16, E1 {F.CONV['E1']}/16. Mode gap: "
     f"V1 {F.GAP['V1']:.0f} nats, E1 {F.GAP['E1']:.1f} nats.", {"size": 13}),
    ("", {}),
    ("House fit (V1, fallback)", {"bold": True, "color": ACCENT}),
    ("Adam, 700 steps, lr 0.01; float32 in 54, float64 SingleTaskGP refit each round in 55.", {"size": 13}),
], size=14, space_after=8)
assert "Adam, 700 epochs, lr 0.01" in F.arms["gp"]["train"]
F.CHECKS.append("arms_E.json gp.train contains 'Adam, 700 epochs, lr 0.01' and 'float64 SingleTaskGP'")
notes(s, SRC_LINES[k] + ". fit_v2_spec printed verbatim from committed_configs.json. Lengthscales, n_within_tol, "
         "mode_gap_nats: committed_configs.json / ercot_gp_status_v2.csv. House fit: EMULATOR_BO.md §1 (54 path, float32) "
         "and arms_E.json gp.train (55, float64 SingleTaskGP).")

# =============================================================================
# write
# =============================================================================
scripts_pass(prs)
out = HERE / "ercot_overnight.pptx"
prs.save(out)
F.save_frozen()

copies = MF.copy_figs()
MF.crops()
with open(HERE / "FIGURES_USED.md", "w") as fh:
    fh.write("# Figures used in ercot_overnight.pptx (slide → path, origin)\n\n")
    for sl, p in L.FIGURES_USED:
        name = Path(p).name
        if name in MF.CROPS:
            srcname, what = MF.CROPS[name]
            src, com, h = copies[srcname]
            origin = f"CROPPED from `{src.relative_to(F.REPO)}` @ {com} ({what}); no pixel redrawn"
        elif name == "fig_hv_committed_5series.png":
            origin = ("NEW, make_overnight_figs.py fig_hv5 (re-rendered from emulator_E_multi_committed.csv + "
                      "EMU_extras_committed.json; committed truth only; 5 legend entries; bold labels and ticks; "
                      "assert-before-draw). Full figure: analysis/emulator_E/figs/fig_EMU_multi_hv_committed.png @ de45242")
        elif name in copies:
            src, com, h = copies[name]
            origin = f"COPIED byte for byte from `{src.relative_to(F.REPO)}` @ {com} (md5 {h})"
        else:
            origin = "NEW, make_overnight_figs.py equations() (pre_can mathtext recipe; this commit)"
        flag = "" if Path(p).exists() else "  **MISSING**"
        fh.write(f"- slide {sl}: `figs/{name}` — {origin}{flag}\n")
    if L.MISSING:
        fh.write("\n## Missing at build time\n\n" + "\n".join(f"- `{m}`" for m in L.MISSING) + "\n")

with open(HERE / "SLIDE_TEXT.md", "w") as fh:
    fh.write("# ercot_overnight.pptx — slide text, source line and speaker notes\n\n")
    for i, sl in enumerate(prs.slides, 1):
        fh.write(f"## Slide {i}\n\n**Source line:** {SRC_LINES.get(i, '')}\n\n")
        for sh in sl.shapes:
            if sh.has_text_frame and sh.text_frame.text.strip() and sh.text_frame.text.strip() != "#":
                for para in sh.text_frame.paragraphs:
                    t = "".join(r.text for r in para.runs).strip()
                    if t and not t.startswith("Source: "):
                        fh.write(t + "\n")
                fh.write("\n")
            if sh.has_table:
                for r in sh.table.rows:
                    fh.write("| " + " | ".join(c.text_frame.text.replace("\n", " ") for c in r.cells) + " |\n")
                fh.write("\n")
        if sl.has_notes_slide and sl.notes_slide.notes_text_frame.text.strip():
            fh.write("**Notes:** " + sl.notes_slide.notes_text_frame.text.strip() + "\n\n")

with open(HERE / "OUTLINE.md", "w") as fh:
    fh.write(f"# ERCOT overnight deck — outline (prompt 67 v1.1, {DATE})\n\n")
    fh.write("Built by `make_overnight_deck.py` on `deck_lib.py` (byte copy of pi_objectives') and the ND group-meeting "
             "template. Slides 1–11 = main (prompt 67 §1 without the station map); slide 12 = Backup divider; "
             "B0 (station map), B1 (two slides), B2–B5; Appendices A–D (B takes three slides).\n\n")
    fh.write(f"## Slide list (as built, {len(prs.slides)} slides)\n\n| # | Title | Figures | Source line |\n|---|---|---|---|\n")
    counts = {}
    for sl_, _ in L.FIGURES_USED:
        counts[sl_] = counts.get(sl_, 0) + 1
    for i, sl in enumerate(prs.slides, 1):
        t = sl.shapes.title.text_frame.text if sl.shapes.title is not None else ""
        if not t:
            texts = [sh.text_frame.text.strip() for sh in sl.shapes if sh.has_text_frame and sh.text_frame.text.strip() not in ("", "#")]
            t = texts[1] if len(texts) > 1 else texts[0]
        fh.write(f"| {i} | {t} | {counts.get(i, 0)} | {SRC_LINES.get(i, '')} |\n")

with open(HERE / "ASSERTIONS.md", "w") as fh:
    fh.write("# Build-time assertions (overnight_facts.py + make_overnight_deck.py; every one passed at build)\n\n")
    fh.write(f"Data state: ercot/tx123 {F.TX123}; RTS d6 {F.D6}. Steiger Z recomputed with "
             f"analysis/pool/pool_n0E_v2.py `steiger` (imported): Z = {F.STEIGER_Z:.4f}, p = {F.STEIGER_P:.3g}.\n\n")
    fh.write("\n".join(f"- {c}" for c in F.CHECKS) + "\n")
    if F.WARNINGS:
        fh.write("\n## Warnings\n\n" + "\n".join(f"- {w}" for w in F.WARNINGS) + "\n")

print("wrote", out, "slides:", len(prs.slides), "missing figures:", len(L.MISSING), "assertions:", len(F.CHECKS))
