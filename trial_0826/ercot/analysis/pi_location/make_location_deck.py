"""Build ercot_location.pptx — ERCOT wave-D location read (prompt 59), on the RTS pi_1008 pattern.

Run:  /opt/anaconda3/bin/python make_location_deck.py        (from analysis/pi_location/)
Out:  ercot_location.pptx, OUTLINE.md, SLIDE_TEXT.md, FIGURES_USED.md   (figures in figs/ and ../pool/figs/standings/)

Every figure slide prints the absolute source path under the image and in the speaker notes.
To swap a figure, edit the path constant or the call. Slide text follows ASD-STE100 style:
short sentences, active voice, one idea per sentence. Numbers are quoted from the files named
in the notes; nothing is recomputed here except the three figures of make_location_figs.py.

Sources (all read-only):
  analysis/pool/ERCOT_POOL_STANDINGS.md (prose numbers), pool_standings.csv, pool_standings_levels.csv,
  pool_wavedD_wide.csv, pool_ed1b_decision.csv, pool_wavedD_wallclock.csv, pool_identity_shift_smoke.csv,
  pool_gap_bound_wavedD.csv, pool_definitions.json, analysis/cost_fix/wave_d_selection.json,
  waves/location_oat_v2/README.md, data/ercot123_2019_v2/bus.csv, figs/ancova_ercot.csv.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent            # analysis/pi_location/
sys.path.insert(0, str(HERE))

import pandas as pd  # noqa: E402
from pptx.util import Inches  # noqa: E402

import deck_lib as L  # noqa: E402
from deck_lib import (ACCENT, INK, MUTED, WARN, card, content_slide, figure, new_deck,  # noqa: E402
                      notes, section_slide, stat, table, text_box)

E = HERE.parent.parent                              # trial_0826/ercot/
POOL = E / "analysis" / "pool"
STD = POOL / "figs" / "standings"
FIGS = HERE / "figs"

F = {
    "oat": FIGS / "oat_curves_ercot.png",
    "sprime": FIGS / "sprime_bars.png",
    "ancova": FIGS / "ancova_ercot.png",
    "clustermap": STD / "clustermap_L180.png",
}
STANDINGS_MD = POOL / "ERCOT_POOL_STANDINGS.md"
FOOT = "ERCOT wave D · location read · draft v1 · 2026-11-07"

# ---- data ---------------------------------------------------------------------------------
stand = pd.read_csv(POOL / "pool_standings.csv")
ed1b = pd.read_csv(POOL / "pool_ed1b_decision.csv")
wide = pd.read_csv(POOL / "pool_wavedD_wide.csv")
wall = pd.read_csv(POOL / "pool_wavedD_wallclock.csv")
gapb = pd.read_csv(POOL / "pool_gap_bound_wavedD.csv")
anc = pd.read_csv(FIGS / "ancova_ercot.csv")
defs = json.load(open(POOL / "pool_definitions.json"))["candidates"]
sel = json.load(open(E / "analysis" / "cost_fix" / "wave_d_selection.json"))
bus = pd.read_csv(E / "data" / "ercot123_2019_v2" / "bus.csv").set_index("Bus ID")
S = stand.set_index("id")
SITE_ORDER = [163, 140, 146, 270, 110, 274]
RANK = {int(r["site"]): r["rank"] for r in sel["ranked"]}

n = 0


def nxt():
    global n
    n += 1
    return n


def bullets(slide, x, y, w, h, items, size=13):
    return text_box(slide, x, y, w, h, items, size=size, bullets=True, space_after=5)


def f3(cid, col="S_prime"):
    r = S.loc[cid]
    return f"{r[col + '_L60']:.2f} / {r[col + '_L120']:.2f} / {r[col + '_L180']:.2f}"


def wp(cid):
    p = S.loc[cid, "W_p_exact"]
    return f"{p:.0e}" if p < 1e-3 else f"{p:.3f}"


def rng(cid):
    r = S.loc[cid]
    d = defs[cid]

    def fmt(v):
        a = abs(v)
        if a >= 1e6:
            return f"{v / 1e6:.2f}M"
        if a >= 1e3:
            return f"{v / 1e3:.1f}k"
        if a >= 10:
            return f"{v:.0f}"
        return f"{v:.2g}"
    return f"{fmt(r['range_L60'])} / {fmt(r['range_L120'])} / {fmt(r['range_L180'])} {d['unit']}"


def caption_short(cid):
    r = S.loc[cid]
    st = r["status"].replace("LOCATION-INSENSITIVE AT THESE SIZES", "LOC-INSENSITIVE (these sizes)").replace("LOCATION-SENSITIVE", "LOC-SENSITIVE")
    return f"{cid}: {st} · S′ {f3(cid)} · W p {wp(cid)} · Δ CONTAMINATED"


def caption_for(cid):
    r = S.loc[cid]
    tag = "; nuclear cost UNCORRECTED (hatched)" if isinstance(r["nuc_tag"], str) and "UNCORRECTED" in r["nuc_tag"] else ""
    return (f"{cid} {defs[cid]['name']}: {r['status']}. S′ {f3(cid)}; W {r['W']:.2f}, p {wp(cid)}. "
            f"Δ vs v2 base CONTAMINATED{tag}.")


prs = new_deck()

# =============================================================================
# 1. Title
# =============================================================================
s = section_slide(prs, "ERCOT TX-123BT · WAVE D · 2026-11-07",
                  "Does location matter in ERCOT? Wave D, six sites × three sizes",
                  "Identity v3 · 21 full-year runs · 584 core-h · 0 SUSPECT rows\n"
                  "Kay Lu · draft v1 (figure paths printed on each slide)", n=nxt())
notes(s, f"Deck source: analysis/pi_location/make_location_deck.py. Numbers: {STANDINGS_MD} (header: 21 rows, 0 SUSPECT, "
         "7,665 / 7,665 RUCs OPTIMAL; §8: 584 core-h). Mirrors RTS pi_1008 slides 8–14 (location section).")

# =============================================================================
# 2. The question and the RTS answer it mirrors
# =============================================================================
s = content_slide(prs, "The question: at a fixed PEM size, does the site change the objective?", nxt(), FOOT)
card(s, Inches(0.5), Inches(1.35), Inches(6.0), Inches(4.7))
text_box(s, Inches(0.7), Inches(1.45), Inches(5.6), Inches(4.5), [
    ("RTS-GMLC (pi_1008, slides 8–14)", {"bold": True, "color": ACCENT, "size": 15}),
    "6 tiers. 15 pair grids, 9 × 9 cells each. 1,215 full-year runs.",
    "Curtailment: location-sensitive in 15 / 15 pairs (gate 4.2–12.6× floor).",
    "Cost: two regimes. Nuclear pairs 16.5–32.9× floor; renewable-only pairs 1.6–5.6×.",
    "Load shed: direction only. Tilt replicates in 11 / 15 pairs; absolute effect ≤ 1.4× floor.",
    "Instrument: 1 % RUC gap with Monte-Carlo range floors; F tests against the floor.",
], size=13, bullets=True, space_after=6)
card(s, Inches(6.8), Inches(1.35), Inches(6.0), Inches(4.7))
text_box(s, Inches(7.0), Inches(1.45), Inches(5.6), Inches(4.5), [
    ("ERCOT today (wave D, prompt 57 Part B)", {"bold": True, "color": ACCENT, "size": 15}),
    "One site at a time. 6 WIND sites × 60 / 120 / 180 MW = 18 VRE rows.",
    "Plus nuclear gen 1 × 3 levels = 3 overlay rows (never in the statistics).",
    "No pairs. No interactions. No mixed designs.",
    "Instrument: identity v3 (gap 0.001, TL 1,200 s). Deterministic: exact replicate ruler = 0.",
    "Noise ruler PENDING (prompt 52). Base is a v2 run: every Δ vs base is CONTAMINATED.",
], size=13, bullets=True, space_after=6)
text_box(s, Inches(0.5), Inches(6.25), Inches(12.3), Inches(0.6),
         "The ERCOT read is weaker by design: 18 points, 3 levels. It reads the ORDER of sites and a base-free spread ratio. "
         "It does not read significance.", size=14, bold=True, color=WARN)
notes(s, "Left column: RTS pi_1008 v1/SLIDE_TEXT.md slides 8, 9, 13 (verbatim numbers). Right column: "
         f"{STANDINGS_MD} header + honesty clause (18–21 rows, 3 levels, no interactions; no multiplicity correction).")

# =============================================================================
# 3. Design
# =============================================================================
s = content_slide(prs, "Design: the top-6 curtailment-relief WIND sites, each alone, at 60 / 120 / 180 MW", nxt(), FOOT)
rows = [["Site", "Bus (name)", "Nameplate MW", "ω at 60 / 120 / 180 MW", "Slate rank (relief per MW)"]]
for site in SITE_ORDER:
    w = wide[(wide["site"] == site) & (wide["unit_type"] == "WIND")].sort_values("pem_mw")
    b = int(w["bus"].iloc[0])
    om = " / ".join(f"{v:.3f}" for v in w["omega"])
    rows.append([str(site), f"{b} ({bus.loc[b, 'Bus Name']})", f"{w['gen_pmax'].iloc[0]:.1f}", om, str(RANK[site])])
wn = wide[wide["unit_type"] == "NUC"].sort_values("pem_mw")
rows.append(["1 (nuclear)", f"107 ({bus.loc[107, 'Bus Name']})", f"{wn['gen_pmax'].iloc[0]:.0f}",
             " / ".join(f"{v:.4f}" for v in wn["omega"]), "overlay (formulation A)"])
table(s, Inches(0.5), Inches(1.3), Inches(8.0), rows, col_widths=[1.1, 2.3, 1.3, 2.0, 1.6], size=11, row_h=Inches(0.36))
text_box(s, Inches(0.5), Inches(4.45), Inches(8.0), Inches(2.5), [
    ("Why these six", {"bold": True, "color": ACCENT}),
    "The pre-registered rule (analysis/cost_fix/WAVE_D_TOPK_RULE.md, commit 4fb3b1f) ranks screening_v2 sites by "
    "Δ true curtailment per MW and keeps the top 6. The A ruler is 0, so every site qualified and the rule reduced to the top 6 by rank.",
    "Result: a homogeneous congested slate. Sites 163, 270, 274 sit on bus 120 (Knox City). Sites 110, 140 sit on bus 2 (Wheeler). "
    "Site 146 sits on bus 75 (Panhandle 3). The location read below is a read INSIDE congested sites.",
    "Size is absolute MW, not ω. Site 163 (185 MW nameplate) reaches ω 0.97 at 180 MW.",
], size=12, space_after=5)
x0, y0, w, h = Inches(8.8), Inches(1.3), Inches(4.0), Inches(1.25)
card(s, x0, y0, w, h)
text_box(s, x0 + Inches(0.15), y0 + Inches(0.08), w - Inches(0.3), h - Inches(0.15), [
    ("Identity v3", {"bold": True, "color": ACCENT}),
    "ruc_mipgap 0.001, ruc_time_limit 1,200 s (GAP_DECISION.json, E-D6). 0 TIME_LIMIT on 7,665 RUCs.",
], size=11)
card(s, x0, y0 + Inches(1.4), w, h)
text_box(s, x0 + Inches(0.15), y0 + Inches(1.48), w - Inches(0.3), h - Inches(0.15), [
    ("--full extracts", {"bold": True, "color": ACCENT}),
    "Every row --full: E8, E9, N5 from pool_full_metrics.json. 0 SUSPECT rows (S1–S3 pass).",
], size=11)
card(s, x0, y0 + Inches(2.8), w, h)
text_box(s, x0 + Inches(0.15), y0 + Inches(2.88), w - Inches(0.3), h - Inches(0.15), [
    ("Deterministic instrument", {"bold": True, "color": ACCENT}),
    "Exact replicates are byte-identical (A ruler = 0). Noise ruler = prompt 52, PENDING.",
], size=11)
card(s, x0, y0 + Inches(4.2), w, h, fill=L.RGBColor(0xFB, 0xEC, 0xE9))
text_box(s, x0 + Inches(0.15), y0 + Inches(4.28), w - Inches(0.3), h - Inches(0.15), [
    ("Base = v2 run", {"bold": True, "color": WARN}),
    "base_2019_v2:1 ran at gap 0.01 / TL 120. Every Δ vs base is CONTAMINATED until base_v3 lands.",
], size=11)
notes(s, "Table: pool_wavedD_wide.csv (site, bus, pem_mw, omega, gen_pmax), data/ercot123_2019_v2/bus.csv (Bus Name), "
         "analysis/cost_fix/wave_d_selection.json (rank by relief_per_mw: 163 3,841; 140 3,630; 146 3,587; 270 3,568; 110 3,502; 274 3,501). "
         "Rule file: analysis/cost_fix/WAVE_D_TOPK_RULE.md (prompt 36 §4.2). Cards: waves/GAP_DECISION.json; "
         f"{STANDINGS_MD} header and §0.1. Nuclear ω = 60/120/180 MW over 2,430 MW (waves/location_oat_v2/README.md §2).")

# =============================================================================
# 4. Method
# =============================================================================
s = content_slide(prs, "Method: pinned statistics, one base-free rule, no test", nxt(), FOOT)
rows = [
    ["Statistic", "What it measures", "Decision use"],
    ["range_jℓ", "max − min over the 6 sites at level ℓ (60 / 120 / 180 MW); base-invariant", "Printed at every level; the ruler read divides it by ruler_j (PENDING)"],
    ["S′_jℓ (primary)", "range_jℓ / mean_site |x(site, 180) − x(site, 60)|: between-site spread over the within-site size effect; base-free", "LOCATION-SENSITIVE iff S′ ≥ 0.5 at 2 of 3 levels; SIZE-DRIVEN iff S′ < 0.5 at 2 of 3"],
    ["S_jℓ (secondary)", "range_jℓ / mean_site |Δ_jℓ vs base|; same thresholds (pinned f76d897)", "Shown beside S′; CONTAMINATED where the identity shift dominates the Δ"],
    ["Kendall W, exact p", "Agreement of the 3 level-rankings of the 6 sites; exact p over 518,400 permutations", "Descriptor only; enters no verdict"],
    ["Oriented Spearman ρ", "Rank agreement of two candidates, oriented by direction; pooled n = 18 and per level n = 6", "REDUNDANT iff ρ ≥ +0.90 pooled AND at 2 of 3 levels; complete linkage"],
    ["Gap bound G", "Σ_days gap × ruc_cost; pair bound G_a + G_b (E1–E3 only)", "GAP-READABLE iff |Δ| > bound; approximate (RUC objective, not realized cost)"],
    ["Ruler_j", "Replicate noise under identity v3 (prompt 52 noise_v3)", "RULER PENDING (52): every ruler column is a placeholder"],
]
table(s, Inches(0.5), Inches(1.3), Inches(12.3), rows, col_widths=[1.7, 6.0, 4.6], size=11, row_h=Inches(0.56))
text_box(s, Inches(0.5), Inches(6.0), Inches(12.3), Inches(0.9), [
    "No multiplicity correction. The verdicts are threshold reads on a deterministic instrument, not tests. "
    "Among ~22 graded candidates about one W p < 0.05 is expected under exchangeable site labels.",
    "The error direction is permissive: a false LOCATION-SENSITIVE call admits one more candidate to the PI table.",
], size=12, color=INK, space_after=3)
notes(s, f"Source: {STANDINGS_MD} §0.2 (S′, S), §1 (W), §2 (G), §4 (ρ rule), honesty clause (no multiplicity correction; "
         "permissive error direction), ruler status line. Mirrors RTS pi_1008 slide 9 (statistic / what / decision use).")

# =============================================================================
# 5. OAT curves (NEW FIG)
# =============================================================================
s = content_slide(prs, "OAT view: curtailment curves overlap; cost curves fan out; starts and congestion scatter", nxt(), FOOT)
figure(s, F["oat"], Inches(0.4), Inches(1.25), Inches(8.6), Inches(5.7), n,
       caption="Raw value vs PEM MW, one line per site (fixed colours across the deck). Nuclear gen 1 dashed black; "
               "omitted on E1 because its cost is UNCORRECTED.")
card(s, Inches(9.2), Inches(1.25), Inches(3.7), Inches(5.7))
text_box(s, Inches(9.35), Inches(1.35), Inches(3.4), Inches(5.5), [
    ("Takeaway", {"bold": True, "color": ACCENT}),
    "V1 curtailment: the six curves overlap. Size drives it. S′ " + f3("V1") + ".",
    "E1 cost: the curves fan out with MW. Site 163 is flat: ω 0.97 on a 185 MW nameplate saturates. S′ " + f3("E1") + "; W p " + wp("E1") + ".",
    "X1 CO₂ moves with E1 (same fan, same flat site 163).",
    "R4 starts, N1 line-hours, R2 shortfall: the lines cross. No stable site order (W p " + wp("R4") + " / " + wp("N1") + " / " + wp("R2") + ").",
    ("Data", {"bold": True, "color": ACCENT}),
    "pool_standings_levels.csv (18 VRE rows per candidate) + pool_wavedD_wide.csv rows 19–21 (nuclear).",
], size=11, space_after=4)
notes(s, f"Figure: {F['oat']} (make_location_figs.py, fig_oat). Values: {POOL / 'pool_standings_levels.csv'}; nuclear rows from "
         f"{POOL / 'pool_wavedD_wide.csv'}. S′ and W p: {POOL / 'pool_standings.csv'}. Reads: {STANDINGS_MD} §1 'Reads, in plain words'. "
         "RTS analogue: pi_1008 slide 10 (oat_curves_C.png).")

# =============================================================================
# 6. Spread ratio S′ (NEW FIG)
# =============================================================================
_surv = stand[stand["is_survivor"] == True]  # noqa: E712
_n_sens = int((_surv["status"] == "LOCATION-SENSITIVE").sum())
s = content_slide(prs, f"Spread ratio S′: {_n_sens} of {len(_surv)} survivors pass 0.5 at 2 of 3 levels; V1 does not", nxt(), FOOT)
figure(s, F["sprime"], Inches(0.3), Inches(1.25), Inches(7.6), Inches(4.0), n,
       caption="S′ at L60 / L120 / L180 (log scale), 16 survivors in global order, colour by family; dashed = 0.5 rule.")
surv = stand[stand["is_survivor"] == True].sort_values("global_order_rank")  # noqa: E712
rows = [["id", "S′ L60", "L120", "L180", "W p", "Status"]]
for r in surv.itertuples():
    rows.append([r.id, f"{r.S_prime_L60:.2f}", f"{r.S_prime_L120:.2f}", f"{r.S_prime_L180:.2f}", wp(r.id),
                 r.status.replace("LOCATION-INSENSITIVE AT THESE SIZES", "LOC-INSENSITIVE (these sizes)").replace("LOCATION-SENSITIVE", "LOC-SENSITIVE")])
table(s, Inches(8.1), Inches(1.25), Inches(4.8), rows, col_widths=[0.6, 0.8, 0.7, 0.7, 0.8, 2.4], size=8, row_h=Inches(0.3))
text_box(s, Inches(0.3), Inches(5.35), Inches(7.6), Inches(1.6), [
    ("Read", {"bold": True, "color": ACCENT}),
    "V1, N5, E6 are SIZE-DRIVEN: the six top-relief sites relieve curtailment within ±5–15 % of each other at matched MW.",
    "E1 passes at L120 and L180 only; at L60 the spread is 0.39 of the size effect.",
    "R4–R6, N1–N4, E2, E8 pass S′ with W p ≥ 0.2: a large spread with a site order that changes from level to level. "
    "Only the prompt-52 ruler can size that chatter. Their status is provisional.",
], size=11, space_after=3)
notes(s, f"Figure: {F['sprime']} (make_location_figs.py, fig_sprime). Table: {POOL / 'pool_standings.csv'} "
         "(S_prime_L60/L120/L180, W_p_exact, status; is_survivor = True, sorted by global_order_rank). "
         f"Reads: {STANDINGS_MD} §1. Deviation from the spec layout: the table sits beside the figure, not beneath it (17 rows do not fit under a legible figure). "
         "RTS analogue: pi_1008 slide 11 (oat_spread_ratio.png).")

# =============================================================================
# 7. Variance explained (NEW FIG + table)
# =============================================================================
s = content_slide(prs, "Variance explained: site identity adds 32 points for cost; nothing fits starts or line-hours", nxt(), FOOT)
figure(s, F["ancova"], Inches(0.3), Inches(1.25), Inches(7.2), Inches(4.6), n,
       caption="R²adj of model 0 (quadratic in MW) and ΔR²adj for + site intercepts, then + site × MW. 18 VRE rows per candidate.")
rows = [["Candidate", "R²adj quad. MW", "+ site intercepts", "+ site × MW", "Reading"]]
for r in anc.itertuples():
    rows.append([f"{r.id} {r.name}", f"{r.R2adj_m0_quadratic_MW:.3f}", f"{r.dR2adj_m1_site_intercepts:+.3f}",
                 f"{r.dR2adj_m2_site_x_MW:+.3f}", r.reading])
table(s, Inches(7.7), Inches(1.25), Inches(5.2), rows, col_widths=[1.9, 1.0, 1.1, 1.0, 1.0], size=9, row_h=Inches(0.36))
text_box(s, Inches(7.7), Inches(4.0), Inches(5.2), Inches(2.0), [
    ("Takeaway", {"bold": True, "color": ACCENT}),
    "V1: MW alone explains 97 %. Site adds 1 point. Mostly size.",
    "E1 and X1: MW explains 52 %; site intercepts add 32 / 28 points; slopes add 15 / 18. Level shift first, then slope.",
    "R4, N1: no model exceeds R²adj 0.2. Neither MW nor site explains the 18 rows. The spread is unstructured.",
    "R2: a weak fit (0.49) with equal site and slope shares.",
], size=11, space_after=3)
text_box(s, Inches(0.3), Inches(5.95), Inches(7.2), Inches(1.0), [
    "Method. Model 0: 1 + MW + MW² (2 df; residual df 15). Model 1: + 5 site intercepts (residual df 10). Model 2: + 5 site × MW slopes "
    "(residual df 5). R²adj = 1 − (RSS/(n−p)) / (TSS/(n−1)). Reading rule: 'no fit' if every R²adj < 0.3; 'mostly size' if both increments < 0.10; "
    "'slopes differ' if the slope increment ≥ 0.10 and ≥ the intercept increment; else 'level shift'. No ruler, no F.",
], size=9, color=MUTED, space_after=0)
notes(s, f"Figure: {F['ancova']}; table: {FIGS / 'ancova_ercot.csv'} (make_location_figs.py, ancova_table). Data: "
         f"{POOL / 'pool_standings_levels.csv'}, 18 VRE rows per candidate. NO F test (no ruler). 'no fit' is added to the RTS vocabulary "
         "because R4 and N1 have negative R²adj at models 1 and 2. RTS analogue: pi_1008 slide 12 (oat_ancova_increments.png).")

# =============================================================================
# 8. Atlas: existing heatmaps for the four recommended candidates
# =============================================================================
s = content_slide(prs, "Atlas: Δ vs base, 6 sites × 3 MW, for the four recommended candidates (Δ CONTAMINATED)", nxt(), FOOT)
atlas = ["V1", "E1", "R4", "N1"]
cw, ch = Inches(6.1), Inches(2.85)
for i, cid in enumerate(atlas):
    x = Inches(0.4) + (i % 2) * (cw + Inches(0.3))
    y = Inches(1.2) + (i // 2) * ch
    figure(s, STD / f"{cid}.png", x, y, cw, ch, n, caption=caption_short(cid), show_path=False)
text_box(s, Inches(0.4), Inches(6.85), Inches(12.5), Inches(0.25),
         "Paths: " + "  ·  ".join(str(STD / f"{c}.png") for c in atlas), size=6, color=L.PATH_GREY, space_after=0)
notes(s, "Figures: " + "\n".join(str(STD / f"{c}.png") for c in atlas) +
         f"\nCaptions: {POOL / 'pool_standings.csv'} (status, S_prime, W, W_p_exact, nuc_tag). The heatmaps come from pool_standings.py "
         "(6 × 3 Δ vs v2 base, nuclear row overlaid below a black rule, hatched = UNCORRECTED on E1). RTS analogue: pi_1008 slide 13 (atlas_heattables.png).")

# =============================================================================
# 9. Redundancy and the falsified conflict
# =============================================================================
s = content_slide(prs, "Redundancy: cluster {E1, V2, X1} → E1. The pinned cost-vs-CO₂ conflict did not appear", nxt(), FOOT)
figure(s, F["clustermap"], Inches(0.3), Inches(1.2), Inches(5.2), Inches(5.8), n,
       caption="Oriented Spearman ρ at L180 (n = 6 sites) with complete-linkage dendrogram; green boxes = redundant pairs.")
text_box(s, Inches(5.8), Inches(1.25), Inches(7.0), Inches(5.7), [
    ("Rule (f76d897)", {"bold": True, "color": ACCENT}),
    "REDUNDANT iff ρ_or ≥ +0.90 pooled (n = 18) AND ≥ +0.90 at 2 of 3 levels (n = 6). Complete linkage. Base-invariant.",
    ("Result", {"bold": True, "color": ACCENT}),
    "4 redundant pairs: V2–E1 0.98, V2–X1 0.99, E1–X1 0.98, V2–E3 0.90. One cluster C1 = {E1, V2, X1}; survivor E1 (global order 2).",
    "E3 is redundant with V2 only, so complete linkage leaves it out.",
    ("Pinned expectation falsified", {"bold": True, "color": WARN}),
    "E1–X1 was expected to CONFLICT ('cheaper = more coal'). On wave D ρ = +0.98 pooled, +0.94 at L120 and L180.",
    "Mechanism: PEM at a VRE site raises day-ahead thermal commitment. Cost and CO₂ rise together, in the same site order. X1 is REDUNDANT → E1.",
    ("The real axes", {"bold": True, "color": ACCENT}),
    "V1–E1 ρ = −0.70: a SIZE trade-off. More PEM MW relieves more curtailment and costs more.",
    "LOCATION trade-offs run between the pocket N4 and the cost family (E1 −0.77, E3 −0.76, E4 −0.73) and N5 (−0.76).",
    "Among the recommended four: V1–R4 +0.34, V1–N1 +0.53, R4–N1 +0.02, E1–N1 −0.26 (not labelled).",
], size=11, space_after=3)
notes(s, f"Figure: {F['clustermap']} (pool_standings.py). Alternative: {STD / 'clustermap_stratified.png'}. "
         f"Numbers: {STANDINGS_MD} §4 (redundant pairs, cluster C1, falsified expectation) and §6 (conflict table; "
         f"{POOL / 'pool_conflicts_wavedD.csv'}, {POOL / 'pool_spearman_wavedD_pairs.csv'}).")

# =============================================================================
# 10. Cost under the gap bound
# =============================================================================
s = content_slide(prs, "Cost under the gap bound: the site ORDER is stable, the SIZE of the difference is not readable", nxt(), FOOT)
e1 = gapb[gapb["id"] == "E1"]
rr = {lv: e1[e1["level_id"] == lv].iloc[0] for lv in ["L60", "L120", "L180"]}
x0, y0, w, h, gap = Inches(0.5), Inches(1.3), Inches(2.95), Inches(2.0), Inches(0.17)
stat(s, x0, y0, w, h, "$2.2 / 5.5 / 9.2M",
     "E1 between-site range at 60 / 120 / 180 MW (base-free).", num_size=24)
stat(s, x0 + (w + gap), y0, w, h, "$41–48M raw",
     "v3-only pair bound max G_a + G_b. Scaled to realized cost: $9.7–11.4M. L180 range is 95 % of the scaled bound.", num_size=24)
stat(s, x0 + 2 * (w + gap), y0, w, h, f"${rr['L60']['G_base_usd'] / 1e6:.1f}M",
     "G_base of the v2 base (gap 0.01). It is 90 % of every Δ-vs-base pair bound ($215–222M).", num_size=24)
stat(s, x0 + 3 * (w + gap), y0, w, h, "0 / 18",
     "E1 per-site Δ vs base GAP-READABLE (raw or scaled bound). E2 18 / 18 scaled = the identity shift, not PEM.", num_size=24)
rows = [["Level", "E1 range", "v3 pair bound, raw", "status", "v3 pair bound, scaled", "status"]]
for lv, r in rr.items():
    rows.append([lv, f"${r['range_at_level_usd'] / 1e6:.2f}M", f"${r['v3_pair_bound_max_usd'] / 1e6:.1f}M", r["range_vs_v3_pair_bound"],
                 f"${r['v3_pair_bound_max_scaled_usd'] / 1e6:.1f}M", r["range_vs_v3_pair_bound_scaled"]])
table(s, Inches(0.5), Inches(3.55), Inches(12.3), rows, col_widths=[0.8, 1.2, 1.8, 1.8, 1.8, 1.8], size=11, row_h=Inches(0.34))
bullets(s, Inches(0.5), Inches(5.05), Inches(12.3), Inches(1.9), [
    "Read: the cost site order is stable (W p 0.002; site 163 cheapest at every level). The between-site cost difference sits inside the "
    "v3-only pair bound at every level. Size is not gap-readable at ≤ 180 MW.",
    "Every Δ vs the v2 base is WITHIN GAP BOUND, and that bound is dominated by the base's own 1 % slack. The Δ-vs-base read is uninformative about wave D.",
    "Disclosure: ruc_cost is the 36-hour RUC objective, not realized cost; G is an approximate bound. Scale factor ruc_cost_sum / E1 ≈ 4.24. "
    "E4 and E6 have no gap bound. Plan §1.2 is untouched and waits for prompt 52.",
], size=12)
notes(s, f"Source: {POOL / 'pool_gap_bound_wavedD.csv'} (E1 rows: range_at_level_usd, v3_pair_bound_max_usd, "
         f"v3_pair_bound_max_scaled_usd, G_base_usd, G_base_share_of_bound), {STANDINGS_MD} §2 (table and verdict), "
         f"{POOL / 'pool_gap_bound_summary.json'} (G_base 196.7M). W p from pool_standings.csv (E1 0.0018).")

# =============================================================================
# 11. Caveats
# =============================================================================
s = content_slide(prs, "Caveats: four things that govern every number in this deck", nxt(), FOOT)
rows = [
    ["#", "Caveat", "What it does to the read"],
    ["a", "Δ vs v2 base is CONTAMINATED (v2 base, v3 rows). Smoke identity shift (3 January days × 365/3): "
          f"V1 {S.loc['V1', 'identity_shift_scaled'] / 1e3:,.1f} GWh/yr, E1 ${S.loc['E1', 'identity_shift_scaled'] / 1e6:.1f}M/yr, "
          f"R4 {S.loc['R4', 'identity_shift_scaled']:,.0f} starts/yr, N1 {S.loc['N1', 'identity_shift_scaled']:,.0f} line-h/yr.",
     "S (needs a base) reads SIZE-DRIVEN for the wrong reason on E2, E3, R4–R7, N1, E8. S′, range, W, ρ, clusters are base-free and clean."],
    ["b", "RULER PENDING (52). No replicate noise under identity v3 exists.",
     "No readability verdict. R4, N1 and the other S′-passers with W p ≥ 0.2 are provisional."],
    ["c", "Nuclear cost UNCORRECTED. The thermal patch rewrites the gen-1 cost curve (zero at p_min); K_syn accounting pending.",
     "E1–E4, E7 on nuclear rows show Δ −$383M / −$366M / −$349M. Not a PEM effect. Hatched on the heatmaps; omitted on the OAT cost panel."],
    ["d", "Homogeneous slate: six top-relief WIND sites on three congested buses.",
     "The location effect here is INSIDE congested sites. The caps (163: 185 MW; 274: 746 MW) are where the BO space will see location."],
]
table(s, Inches(0.5), Inches(1.3), Inches(12.3), rows, col_widths=[0.4, 6.4, 5.5], size=10, row_h=Inches(0.62))
rows = [["id", "scaled identity shift", "|shift| / mean |Δ| at L60", "at L180", "read"]]
reads = {"V1": "10–20 % contaminated", "E1": "about half identity", "R4": "DOMINATED", "N1": "DOMINATED"}
units = {"V1": "MWh/yr", "E1": "$/yr", "R4": "starts/yr", "N1": "line-h/yr"}
for cid in ["V1", "E1", "R4", "N1"]:
    r = S.loc[cid]
    rows.append([cid, f"{r['identity_shift_scaled']:,.0f} {units[cid]}", f"{r['identity_shift_over_mean_abs_delta_L60']:.2f}",
                 f"{r['identity_shift_over_mean_abs_delta_L180']:.2f}", reads[cid]])
table(s, Inches(0.5), Inches(4.75), Inches(8.5), rows, col_widths=[0.6, 2.2, 1.9, 1.2, 2.2], size=10, row_h=Inches(0.32))
text_box(s, Inches(9.2), Inches(4.75), Inches(3.6), Inches(1.7),
         "A ratio near or above 1 means the identity change alone can account for the whole Δ vs base. "
         "The scaling is a size indication from three winter days, not a year estimate.", size=10, color=MUTED)
notes(s, f"Source: {STANDINGS_MD} §0.1 (contamination table and reads), §0.3 (nuclear UNCORRECTED), ruler status line, §7 last paragraph; "
         f"{POOL / 'pool_standings.csv'} (identity_shift_scaled, identity_shift_over_mean_abs_delta_L60/L180); "
         f"{POOL / 'pool_identity_shift_smoke.csv'}. Caps: pool_wavedD_wide.csv gen_pmax (163: 185.4; 274: 746.4).")

# =============================================================================
# 12. E-D1b table + what happens next
# =============================================================================
s = content_slide(prs, "E-D1b: fix V1 + E1 now; fill the R and N seats after prompt 52", nxt(), FOOT)
ed = ed1b.set_index("id")
rows = [["id", "Role", "Reason (status; basis)"],
        ["V1 true curtailment", "RECOMMENDED OBJECTIVE (V)",
         f"Global order 1. LOCATION-INSENSITIVE AT THESE SIZES (S′ {f3('V1')}). The size axis; does not separate the six sites; 10–20 % contaminated."],
        ["E1 total cost", "RECOMMENDED OBJECTIVE (E)",
         f"Global order 2. LOCATION-SENSITIVE (S′ {f3('E1')}; W p {wp('E1')}). Survivor of C1. Every Δ WITHIN GAP BOUND. Plan §1.2 pending 52; ~half identity-contaminated."],
        ["R4 thermal starts", "RECOMMENDED (R), PROVISIONAL",
         f"Global order 4. LOCATION-SENSITIVE by S′ ({f3('R4')}) but W p {wp('R4')}, monotone 0 / 6, noise-like unit scatter. Δ vs base DOMINATED. Waits for the ruler."],
        ["N1 congested line-hours", "RECOMMENDED (N), PROVISIONAL",
         f"Global order 5. LOCATION-SENSITIVE by S′ ({f3('N1')}) but W p {wp('N1')}, monotone 3 / 6. Δ vs base DOMINATED (×4.9). Waits for the ruler."],
        ["R2 reserve shortfall", "GUARDRAIL (survivor)",
         f"Plan §1.3 role. LOCATION-SENSITIVE by S′ ({f3('R2')}; range 120 / 65 / 66 MWh on a 446 MWh base). No smoke information on contamination."],
        ["X1 CO₂", "REDUNDANT → E1", "Cluster C1 (ρ +0.98; 2 of 3 levels ≥ 0.94). The pinned conflict did not appear."],
        ["E9 scarcity bus-hours", "DEAD ON WAVE D", "0 on 18 / 18 rows (max RT LMP 432 $/MWh < 450). Count, not dead a priori."],
        ]
table(s, Inches(0.5), Inches(1.3), Inches(12.3), rows, col_widths=[2.0, 2.4, 7.9], size=10, row_h=Inches(0.5))
card(s, Inches(0.5), Inches(5.45), Inches(12.3), Inches(1.5))
text_box(s, Inches(0.7), Inches(5.52), Inches(12.0), Inches(1.4), [
    ("What happens next (no decision here; the PI decides M)", {"bold": True, "color": ACCENT}),
    "1. base_v3: one full-year run of base_2019_v2 data under identity v3 (≈ 5.3 h wall / 21 core-h on a fast node). It removes the contamination from every Δ column.",
    "2. noise_v3 arm A, then arm B (prompt 52): the ruler. It sizes the chatter behind R4 and N1 and makes the plan §1.2 verdict.",
    "3. One rerun: python pool_standings.py --base extracts/<base_v3>/run_index_1 --noise ercot_noise.json. No other code changes.",
], size=11, space_after=3)
notes(s, f"Source: {POOL / 'pool_ed1b_decision.csv'} (E_D1b_role) and {STANDINGS_MD} §7 (reason column, verbatim numbers), §9 (base_v3), "
         "ruler status line (prompt 52). The 'fix V1 + E1 now, fill R / N after 52' line is the strategy-session read of §7's last paragraph.")

# =============================================================================
# Appendix A: remaining graded candidates, 2 heatmaps per slide
# =============================================================================
rest = stand[~stand["id"].isin(atlas)].sort_values("global_order_rank")["id"].tolist()
rest = [c for c in rest if (STD / f"{c}.png").exists()]
for i in range(0, len(rest), 2):
    pair = rest[i:i + 2]
    s = content_slide(prs, "Appendix A: Δ-vs-base heatmaps, " + " and ".join(f"{c} {defs[c]['name']}" for c in pair), nxt(), FOOT)
    for j, cid in enumerate(pair):
        figure(s, STD / f"{cid}.png", Inches(0.4) + j * Inches(6.35), Inches(1.25), Inches(6.1), Inches(5.7), n, caption=caption_for(cid))
    notes(s, "Figures: " + "\n".join(str(STD / f"{c}.png") for c in pair) +
             f"\nCaptions: {POOL / 'pool_standings.csv'}. Δ vs v2 base is CONTAMINATED on every panel (title label).")

# =============================================================================
# Appendix B: wall-clock
# =============================================================================
s = content_slide(prs, "Appendix B: wall-clock and core-hours, two node-speed groups", nxt(), FOOT)
rows = [["Group", "Rows", "n", "Wall h", "Core-h (4 slots)", "RUC median solve s", "RUC max solve s"]]
for g, sub in wall.groupby("node_group"):
    idx = sorted(sub["index"].tolist())
    rows.append([g, ", ".join(str(i) for i in idx), str(len(sub)),
                 f"{sub['wall_h'].min():.2f} – {sub['wall_h'].max():.2f}",
                 f"{sub['core_h'].min():.1f} – {sub['core_h'].max():.1f} (mean {sub['core_h'].mean():.1f})",
                 f"{sub['ruc_solve_time_median_s'].min():.1f} – {sub['ruc_solve_time_median_s'].max():.1f}",
                 f"{sub['ruc_solve_time_max_s'].min():.0f} – {sub['ruc_solve_time_max_s'].max():,.0f}"])
rows.append(["Total", "1–21", "21", f"{wall['wall_h'].sum():.0f} (sum)", f"{wall['core_h'].sum():.0f}", "", ""])
table(s, Inches(0.5), Inches(1.3), Inches(12.3), rows, col_widths=[1.2, 3.0, 0.6, 1.5, 2.4, 1.8, 1.8], size=11, row_h=Inches(0.5))
bullets(s, Inches(0.5), Inches(3.6), Inches(12.3), Inches(3.3), [
    "The same designs sit in both groups (site 110: L60 in A, L120 / L180 in B) and the per-day RUC median solve time doubles with the wall time. "
    "The split is node speed, not problem size. Node groups are inferred: the extracts carry no host names.",
    "The array finished in 11.8 h of calendar time. Per full-year v3 run on a fast node: ≈ 5.3 h wall / 21 core-h.",
    "Row 19 (nuclear L60, slow node) has one RUC day at 1,267 s with status OPTIMAL and n_ruc_time_limit = 0: the solve-time column includes model build. "
    "0 TIME_LIMIT statuses on 7,665 RUCs.",
    "The plan's 'v2 plausibly 12–25 core-h' bracket holds for v3 on fast nodes; the January-day projection (8–10 h / 32–40 core-h) was pessimistic.",
], size=12)
notes(s, f"Source: {POOL / 'pool_wavedD_wallclock.csv'} (wall_h, core_h, node_group, RUC solve times) and {STANDINGS_MD} §8. "
         f"Raw stamps: {E / 'extracts' / 'location_oat_v2' / 'wallclock.csv'}.")

# =============================================================================
# write
# =============================================================================
out = HERE / "ercot_location.pptx"
prs.save(out)

with open(HERE / "FIGURES_USED.md", "w") as fh:
    fh.write("# Figures used in ercot_location.pptx (slide → path)\n\n")
    for sl, p in L.FIGURES_USED:
        flag = "" if Path(p).exists() else "  **MISSING**"
        fh.write(f"- slide {sl}: `{p}`{flag}\n")
    if L.MISSING:
        fh.write("\n## Missing at build time\n\n" + "\n".join(f"- `{m}`" for m in L.MISSING) + "\n")

with open(HERE / "SLIDE_TEXT.md", "w") as fh:
    fh.write("# ercot_location.pptx — slide text and speaker notes\n\n")
    for i, sl in enumerate(prs.slides, 1):
        fh.write(f"## Slide {i}\n\n")
        for sh in sl.shapes:
            if sh.has_text_frame and sh.text_frame.text.strip():
                for para in sh.text_frame.paragraphs:
                    t = "".join(r.text for r in para.runs).strip()
                    if t:
                        fh.write(t + "\n")
                fh.write("\n")
            if sh.has_table:
                for r in sh.table.rows:
                    fh.write("| " + " | ".join(c.text_frame.text.replace("\n", " ") for c in r.cells) + " |\n")
                fh.write("\n")
        if sl.has_notes_slide and sl.notes_slide.notes_text_frame.text.strip():
            fh.write("**Notes:** " + sl.notes_slide.notes_text_frame.text.strip() + "\n\n")

with open(HERE / "OUTLINE.md", "w") as fh:
    fh.write("# ERCOT wave-D location deck — outline (draft v1, 2026-11-07)\n\n")
    fh.write("Built by `make_location_deck.py` on `deck_lib.py` (copied from RTS pi_1008) and the ND group-meeting template. "
             "Figures are embedded AND their source path is printed under each image and in the speaker notes. "
             "Slides 1–12 follow prompt 59 §2; appendix A = one Δ heatmap per remaining graded candidate (2 per slide); appendix B = wall-clock.\n\n")
    fh.write(f"## Slide list (as built, {len(prs.slides)} slides)\n\n| # | Slide | Figures |\n|---|---|---|\n")
    counts = {}
    for sl, _ in L.FIGURES_USED:
        counts[sl] = counts.get(sl, 0) + 1
    for i, sl in enumerate(prs.slides, 1):
        t = sl.shapes.title.text_frame.text if sl.shapes.title is not None else ""
        if not t:
            for sh in sl.shapes:
                if sh.has_text_frame and sh.text_frame.text.strip() and sh.text_frame.text.strip() != "#":
                    t = sh.text_frame.text.strip().split("\n")[0]
                    break
        fh.write(f"| {i} | {t} | {counts.get(i, 0)} |\n")

print("wrote", out, "slides:", len(prs.slides), "missing figures:", len(L.MISSING))
