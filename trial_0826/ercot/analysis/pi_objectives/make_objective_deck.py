"""Build ercot_objectives.pptx — ERCOT objective selection for E-D1b (prompt 64 v1.1), on the pi_location pattern.

Run:  /opt/anaconda3/bin/python make_objective_figs.py && /opt/anaconda3/bin/python make_objective_deck.py
Out:  ercot_objectives.pptx, OUTLINE.md, SLIDE_TEXT.md, FIGURES_USED.md

Every quoted number is read from its source file at build time by objective_facts.py (F) and asserted
there against the prompt-64 value; this script only formats F's values. Each slide carries a source
line (footer + speaker notes). Slide text follows ASD-STE100 style. Numbers not found in any source
file are not printed; README.md lists them.
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from pptx.util import Inches  # noqa: E402

import deck_lib as L  # noqa: E402
import objective_facts as F  # noqa: E402
from deck_lib import (ACCENT, INK, MUTED, WARN, card, content_slide, figure, new_deck,  # noqa: E402
                      notes, section_slide, table, text_box)

FIGS = HERE / "figs"
FIG = {
    "env": FIGS / "fig_envelope_total_mw.png",
    "hero": FIGS / "fig_hero_idr_over_bar.png",
    "relief": FIGS / "fig_relief_vs_total_mw.png",
    "eq": FIGS / "eq_seat_rules.png",
    "clust": F.POOL / "figs" / "n0E" / "n0E_clustermap_resid.png",
    "seed_a3": F.NOISE / "fig_seed_a3_ratio.png",
    "sv3_hl": F.POOL / "figs" / "screening_v3" / "sv3_hl_over_B.png",
}
DATE = "2026-11-18"
SRC_LINES: dict[int, str] = {}

n = 0


def nxt():
    global n
    n += 1
    return n


def slide(heading, src, amend):
    k = nxt()
    foot = f"Source: {src} · plan " + amend.replace("AMENDMENT ", "amendment ").replace("2026-", "")
    assert len(foot) <= 112, (len(foot), foot)   # one footer line (render check)
    SRC_LINES[k] = foot
    s = content_slide(prs, heading, k, foot)
    return s, k


def bullets(s, x, y, w, h, items, size=13, space_after=6):
    return text_box(s, x, y, w, h, items, size=size, bullets=True, space_after=space_after)


def r1(v):
    return f"{v:.1f}"


S = F.SEED_ROWS
R, RS = F.R, F.RS
n0, ed1b, sb = F.n0, F.ed1b, F.sb

prs = new_deck()

# =============================================================================
# 1. Title
# =============================================================================
k = nxt()
s = section_slide(prs, f"ERCOT TX-123BT · OBJECTIVE SELECTION (E-D1b) · {DATE}",
                  "Choosing the ERCOT objectives: three seats are firm, one is a PI choice",
                  f"identity v3 · wave D {F.N_WAVE_D} runs · n0_E {F.N_N0E} · location contrast {F.N_LC} · "
                  f"Seed replicates {F.N_SEED} · screening_v3 {F.N_SV3} (landed and read)\n"
                  f"Kay Lu · branch ercot/tx123 @ {F.TX123}", n=k)
SRC_LINES[k] = "Source: waves/{location_oat_v2,n0_E,location_contrast_E,noise_seed_E,screening_v3}/design_matrix.csv; git rev-parse ercot/tx123"
notes(s, SRC_LINES[k] + ". The screening_v3 read (analysis/pool/SCREENING_V3.md, e58f4bd) landed before the build, "
         "so the subtitle says 'landed and read' (prompt 64 fallback text 'analysis pending' replaced).")

# =============================================================================
# 2. Question
# =============================================================================
s, k = slide("The question: which three or four objectives should the ERCOT BO optimize, and is the evidence strong enough to launch?",
             "analysis/pool/pool_n0E_standings.csv, POOL_N0E_STANDINGS.md", "AMENDMENT 2026-11-06, 2026-11-17")
bullets(s, Inches(0.5), Inches(1.35), Inches(12.3), Inches(5.4), [
    ("The pool", {"bold": True, "color": ACCENT}),
    f"{F.N_GRADED} graded candidates plus the D3 check, frozen at f76d897, in five seat families:",
    ("V = curtailment · E = cost · X = CO₂ · R = reliability (starts, reserve) · N = network congestion.", {"level": 1}),
    ("The rule", {"bold": True, "color": ACCENT}),
    "At most 4 seats. At most one seat per family. Family order V < E < X < R < N.",
    "A seat needs a candidate that RESPONDS on the BO's own design space.",
    "A seat candidate must not be a copy of a higher-priority candidate.",
    ("The two questions for today", {"bold": True, "color": ACCENT}),
    "1. Which candidate takes each seat?",
    "2. Is the evidence strong enough to launch the BO?",
], size=16)
notes(s, SRC_LINES[k] + f". Pool size: {F.N_GRADED} rows in pool_n0E_standings.csv; D3 = check only (POOL_N0E_STANDINGS.md §3). "
         "Rule: plan AMENDMENT 2026-11-06 (≤ 4, one per family, V < E < X < R < N) and 2026-11-17 (RESPONDS IN BOX, REDUNDANT, seat walk R-4).")

# =============================================================================
# 3. Proposal (answer first)
# =============================================================================
s, k = slide("Proposal: optimize curtailment (V1), cost (E1) and congestion (N1 or N4); leave the reliability seat empty (M = 3)",
             "pool_ed1b_combined(_seedbar).csv, ercot_noise_seed.csv, pi-agenda", "AMENDMENT 11-17, 11-18")
rows = [["Seat", "Candidate", "IDR / perturbed bar", "IDR / Seed bar", "Read"],
        ["V", "V1 true curtailment", f"{R['V1']:.0f}×", f"{RS['V1']:.0f}×", "firm"],
        ["E", "E1 total cost", f"{R['E1']:.0f}×", f"{RS['E1']:.0f}×", "firm"],
        ["R", "R4 thermal starts", f"{R['R4']:.1f}×", f"{RS['R4']:.1f}×", "noise-level → seat EMPTY"],
        ["N", "N1 congested line-hours (system)", f"{R['N1']:.1f}×", f"{RS['N1']:.2f}× (binding)", "PI choice"],
        ["N", "N4 line-hours ≥ 99 % on L252 (pocket)", f"{R['N4']:.1f}×", f"{RS['N4']:.1f}×", "PI choice"]]
table(s, Inches(0.5), Inches(1.35), Inches(12.3), rows, col_widths=[0.7, 3.6, 2.0, 2.2, 3.0], size=13, row_h=Inches(0.42))
bullets(s, Inches(0.5), Inches(4.15), Inches(12.3), Inches(2.8), [
    "V1 and E1 are firm: their response is far above both noise bars.",
    f"R4 is at noise level ({R['R4']:.1f}× the perturbed bar, {RS['R4']:.1f}× the Seed bar). The R seat stays EMPTY.",
    f"The N seat is the choice. N1 reads all lines: {R['N1']:.1f}× perturbed, {RS['N1']:.2f}× on its binding Seed bar. "
    f"N4 reads the pocket line L252: {R['N4']:.1f}× / {RS['N4']:.1f}×.",
    "Precedent: the RTS campaign ran with M = 3 (shed, curtailment, cost-less-synthetic). Reserve and starts were dropped "
    "on 10-06 after the drop-one test (Pareto overlap 0.988; τ 0.86–0.91 vs shed).",
], size=14)
notes(s, SRC_LINES[k] + ". IDR / bar = pool_n0E_standings.csv IDR over B_j (perturbed) and over ercot_noise_seed.csv B_seed; "
         "N1's binding bar is B_seed (63 A3 DISAGREE) per pool_ed1b_combined_seedbar.csv (IDR_over_B 3.052). RTS precedent: "
         "pi-agenda row 2026-10-06 (M approved), INDEX row 28 (M = 3 APPROVED), memory project_bogp_multipem (overlap 0.988, τ 0.86–0.91).")

# =============================================================================
# 4. Why the earlier evidence was not enough
# =============================================================================
s, k = slide("Why the earlier evidence was not enough: wave D moves one site at ≤ 180 MW; the BO moves six sites at "
             f"{F.N0_MIN:,.0f}–{F.N0_MAX:,.0f} MW",
             "waves/{location_oat_v2,n0_E}/design_matrix.csv, cost_fix/wave_d_selection.json", "AMENDMENT 2026-11-06b")
figure(s, FIG["env"], Inches(0.4), Inches(1.25), Inches(12.5), Inches(4.75), k,
       caption=f"Total PEM MW per row. Wave D: {F.N_WAVE_D} rows (6 WIND sites × 60 / 120 / 180 MW + nuclear gen 1 × 3). "
               f"n0_E: {F.N_N0E} Sobol rows, six sites in every row, {F.N0_MIN:,.1f}–{F.N0_MAX:,.1f} MW.")
bullets(s, Inches(0.5), Inches(6.05), Inches(12.3), Inches(0.95), [
    "The two populations do not overlap. A read on wave D does not transfer to the BO box by itself.",
    "The slate itself was chosen on V1 alone: relief per MW at ω = 0.5 (screening_v2), under identity v2.",
], size=13, space_after=2)
notes(s, SRC_LINES[k] + ". wave_d_selection.json: the 6 chosen rows have pem_mw / gen_pmax = 0.5 and are ranked by relief_per_mw. "
         "Plan AMENDMENT 2026-11-06b: the 31 v2-identity runs remain slate evidence only.")

# =============================================================================
# 5. Math slide
# =============================================================================
s, k = slide("The seat rules were frozen before any n0_E statistic was computed (ideal, nadir and R had been seen; disclosed)",
             "POOL_N0E_STANDINGS.md (block sha256 8dd06917…)", "AMENDMENT 2026-11-17")
figure(s, FIG["eq"], Inches(0.5), Inches(1.2), Inches(8.4), Inches(4.4), k, show_path=False)
card(s, Inches(9.1), Inches(1.25), Inches(3.8), Inches(4.3))
text_box(s, Inches(9.25), Inches(1.35), Inches(3.5), Inches(4.1), [
    ("Notes", {"bold": True, "color": ACCENT}),
    "BORDERLINE: IDR / B_j in [2, 3). No seat may rest on it alone.",
    "B_j excludes the D2 structural-zero pairs.",
    f"One B:8 delta used a {100 * F.B8['delta_rel']:.1f} % step. It is kept and flagged.",
    "The seat walk allows M < 4. M ≠ 4 reopens the plan §6.4 gate numbers.",
    ("Disclosed: ideal / nadir / R over the 48 rows were seen before the rules.", {"color": WARN}),
], size=12, space_after=5)
text_box(s, Inches(0.5), Inches(5.75), Inches(12.3), Inches(1.2), [
    "A candidate responds if its middle-80 % spread over the 48 designs is at least twice the noise bar.",
    "Two candidates are copies if they rank the designs the same way both before and after the total-MW trend is removed.",
], size=15, bold=True, color=ACCENT, space_after=4)
notes(s, SRC_LINES[k] + f". Equations in math font: {FIG['eq']} (make_objective_figs.py, mathtext). Block sha256 "
         "8dd06917415c8cf6e8f7081adcee862e3d2ae6d08cf4eaa8dc0a9fa2cc8a1d1e as printed in POOL_N0E_STANDINGS.md. "
         "B:8 step: ercot_noise_daily_divergence.csv delta_rel 0.002; ERCOT_NOISE.md §10 flag.")

# =============================================================================
# 6. The ruler
# =============================================================================
dd = " / ".join(str(v) for v in F.DIV_DAYS)
s, k = slide(f"The ruler: the run repeats bit-for-bit at fixed Threads and platform, but a 0.1 % input change moves "
             f"{min(F.DIV_DAYS)}–{max(F.DIV_DAYS)} of 365 RUC days; Seed replicates agree with that ruler within 2× on "
             f"{len(F.A3_AGREE)} of {F.N_GRADABLE} candidates",
             "ERCOT_NOISE.md §10–11, ercot_noise_daily_divergence.csv, NOISE_SEED_E.md §2/§4",
             "AMENDMENT 11-18")
bullets(s, Inches(0.4), Inches(1.35), Inches(5.6), Inches(5.6), [
    ("Perturbed copies (noise_v3)", {"bold": True, "color": ACCENT}),
    f"Divergent RUC days per pair: {dd}. The 4 exact pairs: 0.",
    f"B_j is {F.SPAN_NOW[0]:.2f}–{F.SPAN_NOW[1]:.2f}× the old median ruler (current ruler); "
    f"{F.SPAN_1116[0]:.2f}–{F.SPAN_1116[1]:.2f}× vs the 11-16 ruler.",
    "The D2 pairs were structural zeros: site 206 wind max 895.48 MW < PEM 899.0 / 900.8 MW. They are excluded.",
    ("Seed replicates (noise_seed_E)", {"bold": True, "color": ACCENT}),
    f"τ_exact = {F.TAU['tau_exact']:.0f} stays. τ_res = {F.TAU['tau_res']:.2e} = {F.TAU['tau_res_over_hv0']:.3f} HV₀ "
    f"(PROVISIONAL, {F.N_TAU_STARTS} designs).",
    f"Threads 8 / 1 are not bit-identical to Threads 4 ({F.TH[8]} / {F.TH[1]} days differ). This is confounded with the node.",
], size=12, space_after=5)
rows = [["id", "σ̂_c (Seed, df 16)", "ratio σ̂_c√2 / σ̂_pert", "A3", "B^seed", "B_j (pert.)"]]
fmt = {"V1": lambda v: f"{v:,.0f} MWh", "E1": lambda v: f"${v / 1e3:,.1f}k", "R4": lambda v: f"{v:.1f}",
       "N1": lambda v: f"{v:.1f}", "N4": lambda v: f"{v:.1f}"}
fmtB = {"V1": lambda v: f"{v:,.0f}", "E1": lambda v: f"${v / 1e6:.3f}M", "R4": lambda v: f"{v:.1f}",
        "N1": lambda v: f"{v:.1f}", "N4": lambda v: f"{v:.1f}"}
for j in ["V1", "E1", "R4", "N1", "N4"]:
    r = S[j]
    rows.append([j, fmt[j](r["sigma_c"]), f"{r['ratio']:.2f}×", r["A3"], fmtB[j](r["Bs"]), fmtB[j](r["Bp"])])
table(s, Inches(6.2), Inches(1.35), Inches(6.7), rows, col_widths=[0.6, 1.7, 1.6, 1.2, 1.1, 1.1], size=12, row_h=Inches(0.42))
text_box(s, Inches(6.2), Inches(4.0), Inches(6.7), Inches(2.9), [
    ("Read", {"bold": True, "color": ACCENT}),
    "AGREE iff the ratio is in [0.5, 2]. Then both bars measure the same chatter.",
    f"N1 is {S['N1']['ratio']:.2f}× → DISAGREE. Its perturbed ruler is 'perturbation response, not chatter'. "
    f"Its bar becomes B^seed = {S['N1']['Bs']:.1f}.",
    f"The other DISAGREE id is {[j for j in F.A3_DIS if j != 'N1'][0]} (its perturbed ruler is 0).",
], size=12, space_after=5)
notes(s, SRC_LINES[k] + ". Days: ercot_noise_daily_divergence.csv n_divergent (non-structural perturbed pairs, A then B). "
         "B_j / ruler spans: computed from pool_n0E_standings.csv B_j over ercot_noise.json ruler (2.84–10.28, as POOL_N0E_STANDINGS.md §2) "
         "and over ercot_noise_2026-11-16.json ruler (3.93–13.27, as PROGRESS prompt 62). Site 206 / PEM MW: ERCOT_NOISE.md §10 table. "
         "Table: ercot_noise_seed.csv. τ: ercot_noise_seed.json tau_res. Threads: ercot_noise_seed.json thread_check.")

# =============================================================================
# 7. HERO
# =============================================================================
s, k = slide(f"On the BO's own space, V1 and E1 respond {R['V1']:.0f}× and {R['E1']:.0f}× the bar; N4 {R['N4']:.0f}× "
             f"({RS['N4']:.0f}× Seed); N1 {R['N1']:.1f}× perturbed but {RS['N1']:.2f}× on its Seed bar; R4 {R['R4']:.1f}× ({RS['R4']:.1f}× Seed)",
             "pool_n0E_standings.csv, pool_ed1b_combined_seedbar.csv, ercot_noise_seed.csv", "AMENDMENT 11-18")
figure(s, FIG["hero"], Inches(0.3), Inches(1.2), Inches(12.7), Inches(5.15), k)
text_box(s, Inches(0.5), Inches(6.38), Inches(12.3), Inches(0.6),
         f"The BORDERLINE band is [2, 3). N1's Seed value is {n0.loc['N1', 'IDR']:.1f} / {F.seed.loc['N1', 'B_seed']:.1f} = "
         f"{RS['N1']:.2f}: {RS['N1'] - 3:.2f} above the band. Open markers: the five named ids and the A3-DISAGREE ids.",
         size=13, bold=True, color=ACCENT)
notes(s, SRC_LINES[k] + f". Figure {FIG['hero']} (make_objective_figs.py fig_hero): filled = IDR / B_j (pool_n0E_standings.csv); "
         "open = IDR / B^seed (pool_ed1b_combined_seedbar.csv IDR_over_B_seed_sensitivity, asserted equal to IDR / ercot_noise_seed.csv B_seed). "
         "The formal Seed-bar re-grade landed (baf77c3, POOL_N0E_STANDINGS_seedbar.md): no seat changes; E9 becomes NOT RESPONDS (0 on the log axis).")

# =============================================================================
# 8. Redundancy
# =============================================================================
s, k = slide("Redundancy after removing the total-MW trend: CO₂ collapses into cost, penetration into consumer payments; N4 is not a copy of N1",
             "pool_spearman_n0E_{raw,resid}.csv, POOL_N0E_STANDINGS.md §3–§4", "AMENDMENT 2026-11-17")
figure(s, FIG["clust"], Inches(0.3), Inches(1.2), Inches(5.4), Inches(5.8), k,
       caption="T-residual oriented ρ (n = 48), complete linkage; green boxes = REDUNDANT pairs.")
rh = F.RHO
bullets(s, Inches(5.9), Inches(1.3), Inches(7.0), Inches(5.6), [
    ("Copies (REDUNDANT: raw ≥ 0.90 and residual ≥ 0.50)", {"bold": True, "color": ACCENT}),
    f"X1–E1: raw {rh['X1E1_raw']:.3f}, residual {rh['X1E1_res']:.3f} → X1 is a copy of E1.",
    "V2 → E4 (total payments). N5 → E4. E2 → E1. E6 → V1.",
    ("Not a copy", {"bold": True, "color": ACCENT}),
    f"N4–N1: raw {rh['N4N1_raw']:.3f}, residual {rh['N4N1_res']:.3f} → SIZE-CO-MONOTONE, not redundant.",
    ("What each N candidate carries", {"bold": True, "color": ACCENT}),
    f"N1 tracks size: raw ρ with V1 {rh['V1N1_raw']:.2f}; composition ρ {F.COMP['N1']:.2f}.",
    f"N4 carries composition (ρ {F.COMP['N4']:.2f}) and a location trade-off against cost "
    f"(residual ρ with E1 {rh['E1N4_res']:.2f}).",
], size=13, space_after=6)
notes(s, SRC_LINES[k] + f". Figure {FIG['clust']} (prompt 62 Part B, pool_n0E.py). ρ values: pool_spearman_n0E_raw.csv / _resid.csv "
         "(symmetric cells). Clusters: POOL_N0E_STANDINGS.md §4 (n0E-C1 {E6, V1} → V1; C2 {E1, E2, X1} → E1; C3 {E4, N5, V2} → E4). "
         "Composition ρ: pool_n0E_standings.csv comp_rho.")

# =============================================================================
# 9. Walk result
# =============================================================================
s, k = slide("Result of the pre-registered walk: V1, E1 and N1 seated, R seat empty (M = 3); N4 stands further above its bar but ranks behind N1 in the frozen order",
             "POOL_N0E_STANDINGS.md §E, pool_ed1b_combined.csv", "AMENDMENT 2026-11-17")
ids9 = ["V1", "E1", "X1", "R4", "R2", "R5", "R6", "R7", "N1", "N4"]
rows = [["id", "global order", "IDR / B_j", "status", "reason"]]
for j in ids9:
    r = ed1b.loc[j]
    v = r["IDR_over_B"]
    vs = f"{v:.2f}" if v == v else "n/a"
    reason = r["reason"]
    if j == "R7":
        reason = "dir '-': shown, never clustered or seated (R8 the same)"
    rows.append([j if j != "R7" else "R7 / R8", str(int(r["global_order"])), vs, r["status"], reason])
table(s, Inches(0.5), Inches(1.3), Inches(12.3), rows, col_widths=[1.0, 1.1, 1.1, 3.4, 5.7], size=11, row_h=Inches(0.38))
bullets(s, Inches(0.5), Inches(5.65), Inches(12.3), Inches(1.3), [
    "R family: R4 is BORDERLINE-only. R5 / R6 do not respond. R2 is a guardrail. R7 / R8 are undirected. No R candidate is eligible.",
    f"Disclosure: the first execution printed M = 2 from a seat-walk code defect. The fix ({F.FIX_SHA}) restored the registered rule "
    "before any output was committed.",
], size=12, space_after=4)
notes(s, SRC_LINES[k] + ". Table rows: pool_ed1b_combined.csv (global_order, IDR_over_B, status, reason). Under the Seed-bar re-grade "
         "(pool_ed1b_combined_seedbar.csv) the seats are the same: " + ", ".join(F.SB_SEATS) + ". Fix: POOL_N0E_STANDINGS.md Deviations; commit 82bb71d.")

# =============================================================================
# 10. Location contrast
# =============================================================================
rs = F.RESID
s, k = slide("Location contrast (9 runs): relief is additive within 10 % at 60 and 120 MW per site and sub-additive at 180 "
             f"(g = {F.G[180]:.2f}); at matched total MW the bus-120 sites relieve {min(rs.values()):.1f}–{max(rs.values()):.1f} bars more "
             "than host energy predicts — a size consistent with wind-profile differences, no network effect claimed (one PTDF on L252)",
             "location_contrast_E.csv, LOCATION_CONTRAST_E.md §3–§5, §7", "AMENDMENT 2026-11-17c")
figure(s, FIG["relief"], Inches(0.3), Inches(1.45), Inches(6.2), Inches(5.5), k)
rows = [["MW / site", "g", "g predicted", "read"]] + [[str(m), f"{F.G[m]:.3f}", f"{F.G_PRED[m]:.2f}", F.G_VERDICT[m]]
                                                     for m in (60, 120, 180)]
table(s, Inches(6.7), Inches(1.45), Inches(6.2), rows, col_widths=[1.2, 1.0, 1.3, 2.7], size=11, row_h=Inches(0.32))
pr = list(rs.values())
bullets(s, Inches(6.7), Inches(2.85), Inches(6.2), Inches(4.1), [
    f"Raw V1 location contrast: {F.LOC_RAW_800:.1f} B at 800 MW (b120 vs b275); {F.LOC_RAW_500:.1f} B at 500 MW (matched-u).",
    f"H_C residuals over the four pairs: {' / '.join(f'{v:+.1f}' for v in pr)} B. The pre-registered label LOCATION EFFECT "
    "means 'not explained by H_C'.",
    f"The physics prediction was contradicted on {F.N_CONTRA} of {F.N_RESID_READS} reads. 'Wind profile' is interpretation.",
    f"At 1,500 MW the retrofit relieves {100 * F.R9_SHARE:.0f} % of the {F.POOL_TWH:.2f} TWh behind-cut pool ({F.R9_TWH:.2f} TWh).",
    f"Relief per MWh of host-absorbable energy falls from {F.E_ROW6:.2f} (800 MW pro-rata) to {F.E_ROW9:.3f}. "
    f"The last 700 MW add {F.D700_TWH:.2f} TWh.",
], size=11, space_after=4)
notes(s, SRC_LINES[k] + ". g: location_contrast_E.csv kind V1_g / V1_g_pred; raw: loc_raw (ratio); residuals: loc_resid V1 (ratio) for "
         "pairs 4–5, 7–8, 4–6, 5–6; prediction row 'no residual location effect' = 7 of 8 loc_resid reads; saturation rows. "
         f"Figure {FIG['relief']} (make_objective_figs.py fig_relief; asserts ΣOAT and g against the csv). Interpretation: LOCATION_CONTRAST_E.md §7.")

# =============================================================================
# 11. DECISION
# =============================================================================
sv = F.SV3
s, k = slide("Decide today (E-D1b). Strategy recommends A′.",
             "pi-agenda E-D1b (11-17/18), NOISE_SEED_E.md §5, SCREENING_V3.md", "AMENDMENT 11-16, 11-17b, 11-18")
opts = [
    ("A — V1 · E1 · N1 (M = 3): the pre-registered walk.",
     f"N1 is {RS['N1']:.2f}× its Seed bar, {RS['N1'] - 3:.2f} above BORDERLINE. It mostly repeats the size axis that V1 already gives. "
     "Risk: BO budget spent on chatter in N1.", L.CARD),
    ("A′ — V1 · E1 · N4 (M = 3): a recorded rule change.  RECOMMENDED",
     f"N4 is {RS['N4']:.0f}–{R['N4']:.0f}× its bar and is the only N candidate with a location trade-off against cost. "
     f"Risk: N4 reads one line (L252). The 16-site screening finds N4 locational ERCOT-wide ({sv['N4'][0]:.1f} B, Holm p "
     f"{sv['N4'][1]:.3f}) and N1 not ({sv['N1'][0]:.1f} B, Holm p {sv['N1'][1]:.2f}).", L.RGBColor(0xE8, 0xF0, 0xE4)),
    ("C — add R4 (M = 4). Not recommended.",
     f"R4 is {R['R4']:.1f}× the perturbed bar and {RS['R4']:.1f}× the Seed bar.", L.CARD),
]
y = Inches(1.25)
for head, body, fill in opts:
    card(s, Inches(0.5), y, Inches(7.4), Inches(1.45), fill=fill)
    text_box(s, Inches(0.65), y + Inches(0.06), Inches(7.1), Inches(1.35),
             [(head, {"bold": True, "color": ACCENT, "size": 14}), body], size=12, space_after=3)
    y += Inches(1.55)
card(s, Inches(8.1), Inches(1.25), Inches(4.8), Inches(4.55))
text_box(s, Inches(8.25), Inches(1.32), Inches(4.5), Inches(4.45), [
    ("After either M = 3 choice", {"bold": True, "color": ACCENT}),
    "1. Re-derive the plan §6.4 C2 / C3 false-alarm numbers for M = 3 (strategy session, zero-sim).",
    "2. E-D7: nav set = the first 32 or all 48 Sobol rows.",
    "3. 54 GP fit → 55 Part B → launch.",
    ("Launch risk", {"bold": True, "color": WARN}),
    f"Longest RUC solve: {F.noisej['determinism_conditions']['noise_v3_solve']['max_solve_s']:.1f} s (noise_v3) and 1,157 s "
    "(random_E:22, incl. model build). The limit is 1,200 s: margin 1.4× / 4 %.",
], size=12, space_after=4)
text_box(s, Inches(0.5), Inches(5.95), Inches(12.4), Inches(1.0), [
    ("Cost of a wrong N choice", {"bold": True, "color": ACCENT}),
    "Before launch: no run is repeated; the objectives are re-graded from the stored runs. After launch: a new vector changes "
    "R (§6.3) and with it every HV in the ledger. Plan §10 keeps the ref rule and the gate numbers immutable.",
], size=12, space_after=2)
notes(s, SRC_LINES[k] + ". A / A′ / C: pi-agenda row 2026-11-17 E-D1b with the 11-18 update. N1 / N4 / R4 ratios: slide 3 sources. "
         "Screening line: analysis/pool/screening_v3_locational.csv (HL_over_B, p_holm; N1 NOT LOCATIONAL under both bars, Moses interval "
         "contains 0). §6.4 reopening: pi-agenda row ('M ≠ 4 reopens plan §6.4 gate numbers'). E-D7: NOISE_SEED_E.md §5. RUC solves: "
         "ercot_noise.json determinism_conditions (860.7 s), plan AMENDMENT 2026-11-16 (1,157 s, ≈ 4 %), 2026-11-17b (≈ 1.4×). "
         "Cost of a wrong choice: plan §6.3 (R over the grading tier), §10 (immutable rules). The '< 1 day' estimate in prompt 64 is not in any file (not printed).")

# =============================================================================
# 12. Discussion
# =============================================================================
s, k = slide("Discussion: what this shows and does not show; next",
             "POOL_N0E_STANDINGS, ERCOT_NOISE §12, SCREENING_V3.md, LOCATION_CONTRAST_E.md",
             "AMENDMENT 11-16…18")
bullets(s, Inches(0.5), Inches(1.3), Inches(12.3), Inches(5.65), [
    "(i) Selection used the initial design at pool level. No selection script read random_E. The strategy session saw all 96 landed "
    "values when it computed R (disclosed, plan 11-16). Holdout exposure: 0 / 24.",
    f"(ii) The bar is transferred from single-site designs. Seed chatter confirms it for {len(F.A3_AGREE)} / {F.N_GRADABLE}; N1 is the exception.",
    "(iii) N1 = system-wide line-hours (chatter-limited at single sites). N4 = the physical pocket read.",
    f"(iv) Location on this slate = composition plus a residual consistent with wind profile. ERCOT-wide, the 16-site screening "
    f"(landed) finds V1, E1 and N4 locational ({sv['V1'][0]:.1f} / {sv['E1'][0]:.1f} / {sv['N4'][0]:.1f} B) and N1 not "
    f"({sv['N1'][0]:.1f} B; {F.sv3loc.loc['N1', 'HL_over_B_seed']:.2f} B on the Seed bar).",
    "(v) Gurobi 13.0.2 is logged from noise_seed_E on. For earlier waves it is not discoverable (env records 11.0.2 vs 13.0.2).",
    "(vi) The seat-walk defect is disclosed (slide 9).",
    ("Next", {"bold": True, "color": ACCENT}),
    "Dated design_space_E.json (to do: M = 3, R2 flag 312 MWh) → 54 fit + E-D7 → 55 Part B → 56 launch (option C).",
    "Paper sentence: fixed in LOCATION_CONTRAST_E.md §8.",
], size=13, space_after=5)
notes(s, SRC_LINES[k] + ". (i) POOL_N0E_STANDINGS.md header (random_E not read; holdout 0 of 24), plan AMENDMENT 2026-11-16 "
         "('The 96 landed runs' objective values (to compute R ...)'). (ii) ercot_noise_seed.json A3. (iv) screening_v3_locational.csv. "
         "(v) ERCOT_NOISE.md §12 item 3, plan AMENDMENT 2026-11-18. Next: plan AMENDMENT 2026-11-17 (R2 flag 2 × 156 = 312 MWh). "
         "Prompt 64 also names waves/screening_v3/README.md for a paper sentence; that file holds none, so it is not cited.")

# =============================================================================
# Appendix A: process flow
# =============================================================================
s, k = slide("Appendix A: process flow — four sessions, each step committed before the next read",
             "git log (SHAs below), PROGRESS.md, ERCOT_POOL_STANDINGS.md RERUN", "AMENDMENT 2026-11-17 … 2026-11-18")
steps = [
    ("57 B", "standings on wave D rows (identity v3; the 11-07 base was v2)", None),
    ("54", "Part A rerun on base_v3 + the 52 ruler", ["bac38e7"]),
    ("62 B", "amendment → script → fix → read", ["6aa29dd", "6b5e85a", "82bb71d", "d706199"]),
    ("61", "location_contrast_E wave → landing", ["3b40c2d", "4b7bf85"]),
    ("63", "A1 bar fix → noise_seed_E wave → landing", ["d265580", "6fd3352", "14378fd"]),
    ("62 C", "screening_v3 wave → extracts → landing → amendment", ["c986da0", "1a2cde6", "e58f4bd", "1c6e73e"]),
    ("62", "Seed-bar re-grade addendum", ["baf77c3"]),
]
rows = [["session", "step", "commits", "first commit subject (git)"]]
for who, what, shas in steps:
    subj = F.git("log", "-1", "--format=%s", shas[0])[:80] + "…" if shas else "prompt 57 Part B (ERCOT_POOL_STANDINGS.md)"
    rows.append([who, what, " / ".join(shas) if shas else "—", subj])
table(s, Inches(0.5), Inches(1.3), Inches(12.3), rows, col_widths=[0.8, 3.6, 2.9, 5.0], size=10, row_h=Inches(0.55))
notes(s, SRC_LINES[k] + ". Every SHA is checked with git cat-file at build time (objective_facts.py). e58f4bd / 1c6e73e / baf77c3 "
         "landed on ercot/tx123 after prompt 64 was written and are added here.")

# =============================================================================
# Appendix B: wave D under both rulers
# =============================================================================
_o = [v for j in ("R4", "N1") for v in F.WD_OLD[j]]
_b = [v for j in ("R4", "N1") for v in F.WD_B[j]]
s, k = slide(f"Appendix B: wave D under both rulers — R4 and N1 read {min(_o):.1f}–{max(_o):.1f}× the old median ruler but ≤ {max(_b):.2f}× the bar B_j",
             "pool_standings.csv, pool_ed1b_combined.csv (waveD_range_over_B)", "AMENDMENT 2026-11-17")
rows = [["id", "range / ruler_57 at 60 / 120 / 180 MW", "range / B_j at 60 / 120 / 180 MW", "wave-D B_j verdict"]]
for j in ["R4", "N1"]:
    rows.append([j, " / ".join(f"{v:.1f}" for v in F.WD_OLD[j]), " / ".join(f"{v:.2f}" for v in F.WD_B[j]),
                 ed1b.loc[j, "waveD_B_verdict"]])
table(s, Inches(0.5), Inches(1.4), Inches(12.3), rows, col_widths=[0.8, 4.0, 4.0, 3.5], size=14, row_h=Inches(0.5))
bullets(s, Inches(0.5), Inches(3.2), Inches(12.3), Inches(3.5), [
    "The old ruler was the median |Δ| of the perturbed copies. The bar B_j is max(3σ̂, max |δ|) with the D2 zeros excluded.",
    f"B_j is {F.SPAN_NOW[0]:.2f}–{F.SPAN_NOW[1]:.2f}× the current median ruler. R4 and N1 drop below the 2× readability line on wave D.",
    "Both are BOX-ONLY candidates: unreadable as single sites at ≤ 180 MW; graded on n0_E only.",
], size=14)
notes(s, SRC_LINES[k] + ". pool_standings.csv range_over_ruler_L60/L120/L180 (RERUN, ruler = ercot_noise.json median ruler); "
         "pool_ed1b_combined.csv waveD_range_over_B_L60/L120/L180 and waveD_B_verdict; POOL_N0E_STANDINGS.md §5 (BOX-ONLY RESPONSE).")

# =============================================================================
# Appendix C: full E-D1b table (28 rows; both bars where they differ)
# =============================================================================
order = sb.sort_values("global_order").index.tolist()
for part, chunk in enumerate([order[:14], order[14:]], 1):
    s, k = slide(f"Appendix C ({part}/2): full E-D1b table — both bars side by side (binding bar per the Seed re-grade)",
                 "pool_ed1b_combined.csv, pool_ed1b_combined_seedbar.csv", "AMENDMENT 2026-11-17, 2026-11-18")
    rows = [["id", "order", "IDR / B_j", "IDR / B^seed", "binding bar", "status (re-grade)", "reason (pre-registered)"]]
    for j in chunk:
        r = sb.loc[j]
        def f2(v):
            return f"{v:.2f}" if v == v else "n/a"
        rows.append([j, str(int(r["global_order"])), f2(r["IDR_over_B_pert"]), f2(r["IDR_over_B_seed_sensitivity"]),
                     r["bar_source"], r["status"], ed1b.loc[j, "reason"][:62]])
    table(s, Inches(0.4), Inches(1.25), Inches(12.5), rows, col_widths=[0.6, 0.7, 1.0, 1.1, 2.0, 2.9, 4.2], size=9,
          row_h=Inches(0.35))
    notes(s, SRC_LINES[k] + ". Binding = IDR_over_B in the seedbar csv (Seed bar for the A3-DISAGREE ids N1, E9; B_j elsewhere).")

# =============================================================================
# Appendix D: bars for all graded ids
# =============================================================================
seed = F.seed
gr = [j for j in seed.index if seed.loc[j, "A3"] not in ("AGREE (both exactly 0)",)]
for part, chunk in enumerate([gr[:13], gr[13:]], 1):
    s, k = slide(f"Appendix D ({part}/2): bars for every graded id — perturbed B_j (D2 excluded) vs Seed B^seed; A3 verdict",
                 "ercot_noise_seed.csv, NOISE_SEED_E.md §2", "AMENDMENT 2026-11-18")
    rows = [["id", "unit", "σ̂_c (Seed)", "σ̂_pert", "ratio", "A3", "B^seed", "B_j", "B^seed / B_j"]]
    for j in chunk:
        r = seed.loc[j]
        rr = f"{r['ratio_seed_over_pert']:.2f}" if r["ratio_seed_over_pert"] == r["ratio_seed_over_pert"] else "n/a"
        bb = f"{r['B_seed'] / r['B_pert']:.2f}" if r["B_pert"] > 0 else "n/a"
        rows.append([j, r["unit"], f"{r['sigma_c']:.4g}", f"{r['sigma_hat_pert']:.4g}", rr, r["A3"],
                     f"{r['B_seed']:.4g}", f"{r['B_pert']:.4g}", bb])
    table(s, Inches(0.4), Inches(1.25), Inches(12.5), rows, col_widths=[0.6, 0.9, 1.3, 1.3, 0.8, 2.6, 1.3, 1.3, 1.2],
          size=10, row_h=Inches(0.38))
    if part == 2:
        text_box(s, Inches(0.4), Inches(6.55), Inches(12.5), Inches(0.4),
                 f"A3 verdict: AGREE on {len(F.A3_AGREE)} of {F.N_GRADABLE} gradable ids; DISAGREE on {', '.join(F.A3_DIS)}. "
                 "E5, R1, R3 are exactly 0 under both rulers (not listed).", size=12, bold=True, color=ACCENT)
    notes(s, SRC_LINES[k] + ". All cells: ercot_noise_seed.csv (sigma_c, sigma_hat_pert, ratio_seed_over_pert, A3, B_seed, B_pert).")

# =============================================================================
# Appendix E: run inventory and core-hours
# =============================================================================
inv = [("base_v3", *F.CORE["base_v3"], "extracts/base_v3/wallclock.csv × 4"),
       ("wave D (location_oat_v2)", *F.CORE["wave D (location_oat_v2)"], "extracts/location_oat_v2/wallclock.csv × 4"),
       ("noise_v3 (A + B)", *F.CORE["noise_v3 (A + B)"], "extracts/noise_v3/{A,B}/wallclock.csv × 4"),
       ("n0_E + random_E", 96, 3006.0, "plan AMENDMENT 2026-11-16 (extracts not opened)"),
       ("location_contrast_E", *F.CORE["location_contrast_E"], "extracts/location_contrast_E/wallclock.csv × 4"),
       ("noise_seed_E", F.N_SEED, F.SEED_COREH, "ercot_noise_seed.json (Threads 4 / 8 / 1 slots)"),
       ("screening_v3", *F.CORE["screening_v3"], "extracts/screening_v3/wallclock.csv × 4")]
tot = sum(c for _, _, c, _ in inv)
s, k = slide(f"Appendix E: run inventory and core-hours — {tot / 1e3:.1f}k core-h of evidence behind this selection",
             "extracts/*/wallclock.csv (× 4 slots), ercot_noise_seed.json",
             "AMENDMENT 11-14 … 11-18")
rows = [["wave", "runs", "core-h", "source"]] + [[w, str(int(nr)), f"{c:,.1f}", src] for w, nr, c, src in inv]
rows.append(["total", str(int(sum(nr for _, nr, _, _ in inv))), f"{tot:,.1f}", "sum"])
assert 5200 < tot < 5400, tot
table(s, Inches(0.5), Inches(1.3), Inches(12.3), rows, col_widths=[3.0, 1.0, 1.5, 6.8], size=13, row_h=Inches(0.45))
notes(s, SRC_LINES[k] + ". Core-h = Σ wall_s / 3600 × 4 slots (-pe smp 4 in the array scripts); noise_seed_E uses the json total "
         "because rows 17 / 18 ran on 8 / 1 slots (589.5, not 590.2 at 4 slots). n0_E + random_E: plan AMENDMENT 2026-11-16 "
         "(the extracts are never opened by this deck).")

# =============================================================================
# Appendix F: screening_v3 reads
# =============================================================================
s, k = slide(f"Appendix F: screening_v3 (16 sites, 180 MW, v3) — V1, E1 and N4 are locational ERCOT-wide; N1 is not; the slate bus set holds",
             "SCREENING_V3.md, screening_v3_{locational,ranking,dominance,sites}.csv", "AMENDMENT 11-18")
figure(s, FIG["sv3_hl"], Inches(0.3), Inches(1.2), Inches(6.6), Inches(3.4), k)
rows = [["id", "HL / B_j", "Holm p", "verdict"]]
for j in F.SV3_LOCATIONAL + ["N1", "X1", "V2"]:
    rows.append([j, f"{sv[j][0]:+.1f}", f"{sv[j][1]:.3f}", F.sv3loc.loc[j, "verdict"]])
table(s, Inches(7.1), Inches(1.2), Inches(5.8), rows, col_widths=[0.7, 1.2, 1.1, 2.8], size=10, row_h=Inches(0.3))
d1, d4 = F.DOM_N1, F.DOM_N4
bullets(s, Inches(0.4), Inches(4.75), Inches(12.5), Inches(2.25), [
    f"Contrast: pocket_120 ∪ wind_near (8 sites) vs far (5 sites); Holm over {F.N_SV3_GRADED} ids. "
    f"N1: {sv['N1'][0]:.1f} B_pert / {F.sv3loc.loc['N1', 'HL_over_B_seed']:.2f} B_seed, Holm p {sv['N1'][1]:.2f}, interval contains 0.",
    f"E1 is WITHIN GAP BOUND at {F.N_SV3_SITES} / {F.N_SV3_SITES} sites. The replicate (site 163) is md5-equal to wave D row 3.",
    f"Matched-MW top 6 = {', '.join(map(str, F.TOP6))}: bus set HOLDS; 275 in, 163 out (as predicted); τ_b 0.667. "
    f"{100 * F.OWN163:.0f} % of 163's relief is own-site.",
    f"Dominance: on V1/E1/N1 sites {' and '.join(f'{s_} ({m:.2f} B)' for s_, m in d1.items())} are not dominated; on V1/E1/N4 only "
    f"{' '.join(f'{s_} ({m:.2f} B)' for s_, m in d4.items())}. All margins < 1 B: PI flag; E-D3 stands.",
], size=12, space_after=3)
notes(s, SRC_LINES[k] + f". Figure {FIG['sv3_hl']} (screening_v3_landing.py). Table: screening_v3_locational.csv. Ranking: "
         "screening_v3_ranking.csv; τ_b and md5: SCREENING_V3.md §0. Own-site share: screening_v3_sites.csv. Dominance: "
         "screening_v3_dominance.csv (margin_bars). This replaces the prompt-64 fallback text because SCREENING_V3.md exists at build time.")

# =============================================================================
# write
# =============================================================================
out = HERE / "ercot_objectives.pptx"
prs.save(out)

with open(HERE / "FIGURES_USED.md", "w") as fh:
    fh.write("# Figures used in ercot_objectives.pptx (slide → path, origin)\n\n")
    origin = {
        str(FIG["env"]): "NEW, make_objective_figs.py fig_envelope (this commit)",
        str(FIG["hero"]): "NEW (rebuilt hero), make_objective_figs.py fig_hero (this commit)",
        str(FIG["relief"]): "NEW (rebuilt), make_objective_figs.py fig_relief (this commit)",
        str(FIG["eq"]): "NEW, make_objective_figs.py fig_equations (this commit)",
        str(FIG["clust"]): "EXISTING, prompt 62 Part B (pool_n0E.py), committed d706199",
        str(FIG["sv3_hl"]): "EXISTING, prompt 62 Part C (screening_v3_landing.py), committed e58f4bd",
    }
    for sl, p in L.FIGURES_USED:
        flag = "" if Path(p).exists() else "  **MISSING**"
        fh.write(f"- slide {sl}: `{p}` — {origin.get(p, '')}{flag}\n")
    if L.MISSING:
        fh.write("\n## Missing at build time\n\n" + "\n".join(f"- `{m}`" for m in L.MISSING) + "\n")

with open(HERE / "SLIDE_TEXT.md", "w") as fh:
    fh.write("# ercot_objectives.pptx — slide text, source line and speaker notes\n\n")
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
    fh.write(f"# ERCOT objective-selection deck — outline (prompt 64 v1.1, {DATE})\n\n")
    fh.write("Built by `make_objective_deck.py` on `deck_lib.py` (copy of pi_location's) and the ND group-meeting template. "
             "Slides 1–12 follow prompt 64 §1; appendices A–F follow (C and D take two slides each).\n\n")
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
    fh.write("# Build-time assertions (objective_facts.py; every one passed at build)\n\n")
    fh.write("\n".join(f"- {c}" for c in F.CHECKS) + "\n")

print("wrote", out, "slides:", len(prs.slides), "missing figures:", len(L.MISSING), "assertions:", len(F.CHECKS))
