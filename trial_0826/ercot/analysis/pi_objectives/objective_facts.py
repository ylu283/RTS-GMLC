"""Every number the ERCOT objective deck (prompt 64) prints, read from its source file at build time.

Import from make_objective_figs.py and make_objective_deck.py. Nothing here is typed in by hand:
a value is either computed from a CSV / JSON cell, or a literal string that is ASSERTED to occur in
the named source file (`text_has`). The expected values of prompt 64 v1.1 are asserted against the
computed ones (`near`), so a drift in a source file stops the build.

Sources (prompt 64 §2 only; all read-only, under trial_0826/ercot/ unless absolute):
  analysis/pool/{POOL_N0E_STANDINGS.md, pool_n0E_standings.csv, pool_ed1b_combined.csv,
                 pool_spearman_n0E_raw.csv, pool_spearman_n0E_resid.csv, pool_standings.csv,
                 ERCOT_POOL_STANDINGS.md}
  analysis/noise_v3/{ERCOT_NOISE.md, ercot_noise.json, ercot_noise_2026-11-16.json (the 11-16 ruler,
                 kept by 63 A1), ercot_noise_daily_divergence.csv, NOISE_SEED_E.md,
                 ercot_noise_seed.json, ercot_noise_seed.csv}
  analysis/location_contrast/{LOCATION_CONTRAST_E.md, location_contrast_E.csv}
  analysis/cost_fix/wave_d_selection.json
  waves/{location_oat_v2,n0_E,location_contrast_E,noise_seed_E,screening_v3}/design_matrix.csv
  extracts/{base_v3,location_oat_v2,noise_v3/A,noise_v3/B,location_contrast_E,screening_v3}/wallclock.csv
  ERCOT_BO_PLAN.md, PROGRESS.md, admin/prompt/bogp/{pi-agenda.md, INDEX.md}
  memory project_bogp_multipem.md (RTS M = 3 drop-one numbers; named by prompt 64 slide 3)
Never read: extracts/n0_E, extracts/random_E.
"""

from __future__ import annotations

import json
import math
import subprocess
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent              # analysis/pi_objectives/
E = HERE.parent.parent                              # trial_0826/ercot/
REPO = E.parent.parent
POOL = E / "analysis" / "pool"
NOISE = E / "analysis" / "noise_v3"
LOC = E / "analysis" / "location_contrast"
PLAN = E / "ERCOT_BO_PLAN.md"
PROGRESS = E / "PROGRESS.md"
BOGP = Path("/Users/yilu/Documents/development/nd/research/admin/prompt/bogp")
PI_AGENDA = BOGP / "pi-agenda.md"
INDEX = BOGP / "INDEX.md"
MEMORY_MULTIPEM = Path("/Users/yilu/.claude/projects/-Users-yilu-Documents-life-and-random-context-infrastructure/"
                       "memory/project_bogp_multipem.md")

P = {  # short names used in the slide source lines
    "n0md": POOL / "POOL_N0E_STANDINGS.md",
    "n0csv": POOL / "pool_n0E_standings.csv",
    "ed1b": POOL / "pool_ed1b_combined.csv",
    "raw": POOL / "pool_spearman_n0E_raw.csv",
    "resid": POOL / "pool_spearman_n0E_resid.csv",
    "std": POOL / "pool_standings.csv",
    "stdmd": POOL / "ERCOT_POOL_STANDINGS.md",
    "noisemd": NOISE / "ERCOT_NOISE.md",
    "noisejson": NOISE / "ercot_noise.json",
    "noise1116": NOISE / "ercot_noise_2026-11-16.json",
    "div": NOISE / "ercot_noise_daily_divergence.csv",
    "seedmd": NOISE / "NOISE_SEED_E.md",
    "seedjson": NOISE / "ercot_noise_seed.json",
    "seedcsv": NOISE / "ercot_noise_seed.csv",
    "locmd": LOC / "LOCATION_CONTRAST_E.md",
    "loccsv": LOC / "location_contrast_E.csv",
    "sel": E / "analysis" / "cost_fix" / "wave_d_selection.json",
    "dm_D": E / "waves" / "location_oat_v2" / "design_matrix.csv",
    "dm_n0": E / "waves" / "n0_E" / "design_matrix.csv",
    "dm_lc": E / "waves" / "location_contrast_E" / "design_matrix.csv",
    "dm_seed": E / "waves" / "noise_seed_E" / "design_matrix.csv",
    "dm_sv3": E / "waves" / "screening_v3" / "design_matrix.csv",
}

CHECKS: list[str] = []          # every assertion made, written to README by the deck builder


# ---------------------------------------------------------------- assertion helpers
def near(value, expected, tol, what):
    assert abs(float(value) - float(expected)) <= tol, f"{what}: source {value!r} vs prompt {expected!r} (tol {tol})"
    CHECKS.append(f"{what}: {value:.6g} ≈ {expected} (± {tol})")
    return value


def text_has(path: Path, *needles: str):
    txt = Path(path).read_text()
    for nd in needles:
        assert nd in txt, f"'{nd}' not found in {path}"
        CHECKS.append(f"text in {Path(path).name}: '{nd}'")
    return needles[0] if len(needles) == 1 else needles


def git(*args) -> str:
    return subprocess.check_output(["git", "-C", str(REPO), *args], text=True).strip()


def commit_exists(sha):
    git("cat-file", "-e", sha + "^{commit}")
    CHECKS.append(f"commit {sha} exists in git")
    return sha


# ---------------------------------------------------------------- tables
n0 = pd.read_csv(P["n0csv"]).set_index("id")
ed1b = pd.read_csv(P["ed1b"]).set_index("id")
raw = pd.read_csv(P["raw"], index_col=0)
resid = pd.read_csv(P["resid"], index_col=0)
std = pd.read_csv(P["std"]).set_index("id")
seed = pd.read_csv(P["seedcsv"]).set_index("id")
seedj = json.load(open(P["seedjson"]))
noisej = json.load(open(P["noisejson"]))
noise1116 = json.load(open(P["noise1116"]))
div = pd.read_csv(P["div"])
loc = pd.read_csv(P["loccsv"])
sel = json.load(open(P["sel"]))
dmD = pd.read_csv(P["dm_D"])
dm0 = pd.read_csv(P["dm_n0"])
dmLC = pd.read_csv(P["dm_lc"])
dmS = pd.read_csv(P["dm_seed"])
dmV3 = pd.read_csv(P["dm_sv3"])

# ---------------------------------------------------------------- slide 1: run counts
N_WAVE_D = near(len(dmD), 21, 0, "wave D rows")
N_N0E = near(len(dm0), 48, 0, "n0_E rows")
N_LC = near(len(dmLC), 9, 0, "location_contrast_E rows")
N_SEED = near(len(dmS), 18, 0, "noise_seed_E rows")
N_SV3 = near(len(dmV3), 11, 0, "screening_v3 rows")
N_SV3_REP = int(dmV3["replicate_of"].notna().sum())
near(N_SV3_REP, 1, 0, "screening_v3 replicate rows")
SV3_WALL = pd.read_csv(E / "extracts" / "screening_v3" / "wallclock.csv")
near(len(SV3_WALL), 11, 0, "screening_v3 wall-clock rows (landed)")
TX123 = git("rev-parse", "--short=7", "ercot/tx123")
SCREENING_V3_MD = POOL / "SCREENING_V3.md"
SEEDBAR_MD = POOL / "POOL_N0E_STANDINGS_seedbar.md"
SEEDBAR_CSV = POOL / "pool_ed1b_combined_seedbar.csv"
HAVE_SCREENING_V3 = SCREENING_V3_MD.exists()
HAVE_SEEDBAR = SEEDBAR_MD.exists() and SEEDBAR_CSV.exists()

# ---------------------------------------------------------------- slide 2: pool
N_GRADED = near(len(n0), 28, 0, "pool candidates graded on n0_E")
text_has(P["n0md"], "D3 check (no bar)")
FAMILIES = sorted(n0["family"].unique())
text_has(PLAN, "≤ 4 objectives, one per family", "V < E < X < R < N")

# ---------------------------------------------------------------- per-candidate ratios
def idr_over(j, bar="pert"):
    idr = n0.loc[j, "IDR"]
    b = n0.loc[j, "B_j"] if bar == "pert" else seed.loc[j, "B_seed"]
    return idr / b if b > 0 else float("nan")


R = {j: idr_over(j) for j in n0.index}
RS = {j: idr_over(j, "seed") for j in n0.index}
near(R["V1"], 93.3, 0.05, "V1 IDR/B_j")
near(R["E1"], 14.05, 0.01, "E1 IDR/B_j")
near(R["R4"], 2.1, 0.05, "R4 IDR/B_j")
near(RS["R4"], 1.1, 0.05, "R4 IDR/B_seed")
near(R["N1"], 6.4, 0.05, "N1 IDR/B_j")
near(RS["N1"], 3.05, 0.005, "N1 IDR/B_seed")
near(R["N4"], 17.4, 0.05, "N4 IDR/B_j")
near(RS["N4"], 14.4, 0.05, "N4 IDR/B_seed")
near(n0.loc["N1", "IDR"], 738.8, 0.05, "N1 IDR")
near(seed.loc["N1", "B_seed"], 242.1, 0.05, "N1 B_seed")
for j, v in R.items():  # the csv ratio column equals IDR / B_j
    if not math.isnan(v):
        assert abs(v - n0.loc[j, "IDR_over_B"]) < 1e-9, j
for j in ["V1", "E1", "R4", "N1", "N4"]:
    assert abs(n0.loc[j, "B_j"] - seed.loc[j, "B_pert"]) < 1e-6 * max(1, n0.loc[j, "B_j"]), j
CHECKS.append("pool_n0E_standings B_j == ercot_noise_seed B_pert for V1, E1, R4, N1, N4")


def x(v, d=1):
    return f"{v:.{d}f}×"


# RTS precedent (memory file named in prompt 64 slide 3) + pi-agenda / INDEX rows
text_has(MEMORY_MULTIPEM, "overlap 0.988, τ 0.86–0.91 vs shed", "M = 3 FINAL (Kay 10-06)")
text_has(PI_AGENDA, "| 2026-10-06 | — | **Objective vector M** | **APPROVED (Kay): M = {load_shed, true_curtailment, cost_less_synthetic}**")
text_has(INDEX, "M = 3 APPROVED (Kay 10-06): shed + curtailment + cost-less-synthetic")
text_has(PI_AGENDA, "Strategy recommendation shifts to A′: V1 · E1 · N4 (M = 3), a recorded rule change")

# ---------------------------------------------------------------- slide 4: envelopes
D_PEM = dmD["pem_mw"].astype(float)
near(int((dmD["unit_type"] == "WIND").sum()), 18, 0, "wave D WIND rows")
near(int((dmD["unit_type"] == "NUC").sum()), 3, 0, "wave D nuclear rows")
near(dmD.loc[dmD.unit_type == "WIND", "oat_site"].nunique(), 6, 0, "wave D WIND sites")
D_LEVELS = sorted(D_PEM.unique())
assert D_LEVELS == [60.0, 120.0, 180.0], D_LEVELS
N0_MW_COLS = [c for c in dm0.columns if c.startswith("mw_")]
N0_PEM = dm0["pem_mw"].astype(float)
assert (dm0[N0_MW_COLS].sum(axis=1) - N0_PEM).abs().max() < 1e-6
N0_NSITES = int((dm0[N0_MW_COLS] > 0).sum(axis=1).min())
near(N0_NSITES, 6, 0, "n0_E sites per row (min)")
N0_MIN = near(N0_PEM.min(), 678.8, 0.05, "n0_E total MW min")
N0_MAX = near(N0_PEM.max(), 1862.6, 0.05, "n0_E total MW max")
SLATE_OMEGA = [r["pem_mw"] / r["gen_pmax"] for r in sel["ranked"] if r["row"] in sel["chosen"]]
assert all(abs(o - 0.5) < 1e-6 for o in SLATE_OMEGA)
CHECKS.append("wave_d_selection.json: chosen 6 rows at pem_mw / gen_pmax = 0.5")
SLATE_SITES = [int(r["site"]) for r in sel["ranked"] if r["row"] in sel["chosen"]]
text_has(PLAN, "The 31 v2-identity runs (base, screening, selection", "remain slate evidence (site ranking by curtailment)")

# ---------------------------------------------------------------- slide 5: rules
SHA_BLOCK = text_has(P["n0md"], "block sha256 `8dd06917415c8cf6e8f7081adcee862e3d2ae6d08cf4eaa8dc0a9fa2cc8a1d1e`")
text_has(PLAN, "9,999", "permutations; `default_rng(6262)`", "≥ 0.5", "residual `ρ_or ≥ 0.50`")
B8 = div[div["key"] == "noise_v3/B:8"].iloc[0]
near(B8["delta_rel"], 0.002, 1e-12, "noise_v3/B:8 delta_rel")
text_has(P["noisemd"], "noise_v3/B:8 used delta_rel = 0.002")

# ---------------------------------------------------------------- slide 6: the ruler
PERT = div[(div.pair_type == "perturbed")]
PERT_NS = PERT[~PERT["structural_zero"]]
DIV_DAYS = [int(v) for v in PERT_NS["n_divergent"]]
assert DIV_DAYS == [350, 357, 365, 354, 358, 365], DIV_DAYS
EXACT = div[div.pair_type == "exact"]
assert len(EXACT) == 4 and int(EXACT["n_divergent"].max()) == 0
CHECKS.append("divergent days per non-structural perturbed pair 350/357/365/354/358/365; 4 exact pairs 0")
# B_j / current ruler and / the 11-16 ruler (ids with both > 0)
def _ratio_span(ruler_json):
    rs = []
    for j in n0.index:
        b = n0.loc[j, "B_j"]
        pc = ruler_json["per_candidate"].get(j)
        if pc is None:
            continue
        r = pc.get("ruler")
        if b > 0 and r:
            rs.append(b / r)
    return min(rs), max(rs)


SPAN_NOW = _ratio_span(noisej)
SPAN_1116 = _ratio_span(noise1116)
near(SPAN_NOW[0], 2.84, 0.005, "B_j / current ruler min")
near(SPAN_NOW[1], 10.28, 0.005, "B_j / current ruler max")
near(SPAN_1116[0], 3.93, 0.005, "B_j / 11-16 ruler min")
near(SPAN_1116[1], 13.27, 0.005, "B_j / 11-16 ruler max")
text_has(P["n0md"], "B_j / ruler range over ids with both > 0: 2.84-10.28x.")
text_has(PROGRESS, "B_j / 57-ruler spans 3.93–13.27×")
text_has(P["noisemd"], "| noise_v3/A:6 | noise_v3/A:2 | 206 | 900.7999 | 899.9000 |", "| 895.48 |",
         "| noise_v3/B:6 | noise_v3/B:2 | 206 | 899.0001 | 899.9000 |")
SEED_ROWS = {}
for j in ["V1", "E1", "R4", "N1", "N4"]:
    r = seed.loc[j]
    SEED_ROWS[j] = dict(sigma_c=r["sigma_c"], sig2=r["sigma_c"] * math.sqrt(2), pert=r["sigma_hat_pert"],
                        ratio=r["ratio_seed_over_pert"], A3=r["A3"], Bs=r["B_seed"], Bp=r["B_pert"])
near(SEED_ROWS["V1"]["sigma_c"], 4376, 0.5, "V1 sigma_c")
near(SEED_ROWS["E1"]["sigma_c"], 312.4e3, 50, "E1 sigma_c")
near(SEED_ROWS["R4"]["sigma_c"], 65.1, 0.05, "R4 sigma_c")
near(SEED_ROWS["R4"]["ratio"], 1.88, 0.005, "R4 A3 ratio")
near(SEED_ROWS["N1"]["sigma_c"], 57.1, 0.05, "N1 sigma_c")
near(SEED_ROWS["N1"]["ratio"], 2.11, 0.005, "N1 A3 ratio")
near(SEED_ROWS["N4"]["sigma_c"], 10.5, 0.05, "N4 sigma_c")
assert SEED_ROWS["N1"]["A3"] == "DISAGREE"
A3_AGREE = seedj["A3"]["agree_gradable"]
A3_DIS = seedj["A3"]["disagree_gradable"]
N_GRADABLE = len(A3_AGREE) + len(A3_DIS)
near(len(A3_AGREE), 20, 0, "A3 AGREE count")
near(N_GRADABLE, 22, 0, "A3 gradable count")
TAU = seedj["tau_res"]
near(TAU["tau_exact"], 0, 0, "tau_exact")
near(TAU["tau_res"] / 1e18, 1.96, 0.005, "tau_res / 1e18")
near(TAU["tau_res_over_hv0"], 0.128, 0.0005, "tau_res / HV0")
N_TAU_STARTS = len(TAU["starts"])
TH = {t["threads"]: t["n_divergent_days"] for t in seedj["thread_check"]}
near(TH[8], 304, 0, "Threads 8 divergent days")
near(TH[1], 364, 0, "Threads 1 divergent days")
assert not any(t["bit_identical"] for t in seedj["thread_check"])

# ---------------------------------------------------------------- slide 8: redundancy
def rr(a, b, m):
    v = m.loc[a, b]
    assert abs(v - m.loc[b, a]) < 1e-12
    return v


RHO = {
    "X1E1_raw": rr("X1", "E1", raw), "X1E1_res": rr("X1", "E1", resid),
    "N4N1_raw": rr("N4", "N1", raw), "N4N1_res": rr("N4", "N1", resid),
    "V1N1_raw": rr("V1", "N1", raw), "E1N4_res": rr("E1", "N4", resid),
}
near(RHO["X1E1_raw"], 0.982, 0.0005, "rho raw X1-E1")
near(RHO["X1E1_res"], 0.968, 0.0005, "rho resid X1-E1")
near(RHO["N4N1_raw"], 0.950, 0.0005, "rho raw N4-N1")
near(RHO["N4N1_res"], 0.394, 0.0005, "rho resid N4-N1")
near(RHO["V1N1_raw"], 0.95, 0.005, "rho raw V1-N1")
near(RHO["E1N4_res"], -0.81, 0.005, "rho resid E1-N4")
COMP = {j: n0.loc[j, "comp_rho"] for j in ["N1", "N4"]}
near(COMP["N1"], -0.03, 0.005, "composition rho N1")
near(COMP["N4"], 0.27, 0.005, "composition rho N4")
STATUS = n0["status"].to_dict()
for j, s in {"X1": "REDUNDANT->E1", "V2": "REDUNDANT->E4", "N5": "REDUNDANT->E4", "E2": "REDUNDANT->E1",
             "E6": "REDUNDANT->V1"}.items():
    assert STATUS[j] == s, (j, STATUS[j])
assert STATUS["N4"].startswith("SIZE-CO-MONOTONE")
CHECKS.append("statuses X1/E2 → E1, V2/N5 → E4, E6 → V1, N4 SIZE-CO-MONOTONE (pool_n0E_standings.csv)")
text_has(P["n0md"], "- n0E-C1: E6, V1 -> survivor V1", "- n0E-C2: E1, E2, X1 -> survivor E1",
         "- n0E-C3: E4, N5, V2 -> survivor E4")

# ---------------------------------------------------------------- slide 9: walk
SEATS = {"V": "V1", "E": "E1", "N": "N1"}
for fam, j in SEATS.items():
    assert ed1b.loc[j, "status"] == "OBJECTIVE", j
assert (ed1b["status"] == "OBJECTIVE").sum() == 3
text_has(P["n0md"], "Seat walk (R-4): M = 3", "- R: **EMPTY**")
FIX_SHA = commit_exists("82bb71d")
text_has(P["n0md"], "82bb71d", "the first run reported M = 2")
for j, s in {"R4": "DIAGNOSTIC", "R5": "DIAGNOSTIC", "R6": "DIAGNOSTIC", "R2": "GUARDRAIL",
             "R7": "DIAGNOSTIC", "R8": "DIAGNOSTIC"}.items():
    assert ed1b.loc[j, "status"] == s, j
assert ed1b.loc["R4", "reason"].startswith("BORDERLINE-only")
assert ed1b.loc["R5", "reason"] == "NOT RESPONDS (n0_E)" and ed1b.loc["R6", "reason"] == "NOT RESPONDS (n0_E)"
assert ed1b.loc["R7", "reason"].startswith("dir '-'") and ed1b.loc["R8", "reason"].startswith("dir '-'")
CHECKS.append("E-D1b reasons R4 BORDERLINE-only, R5/R6 NOT RESPONDS, R2 guardrail, R7/R8 dir '-'")

# ---------------------------------------------------------------- slide 10: location contrast
def lc(kind, item, obj=None, col="value"):
    q = (loc["kind"] == kind) & (loc["item"] == item)
    if obj is not None:
        q &= loc["objective"] == obj
    s = loc[q]
    assert len(s) == 1, (kind, item, obj, len(s))
    return s.iloc[0][col]


G = {m: lc("V1_g", f"P1_{m}", "V1") for m in (60, 120, 180)}
G_PRED = {m: lc("V1_g_pred", f"P1_{m}", "V1") for m in (60, 120, 180)}
G_VERDICT = {m: lc("V1_g", f"P1_{m}", "V1", "verdict") for m in (60, 120, 180)}
near(G[60], 0.038, 0.0005, "g 60"); near(G[120], 0.073, 0.0005, "g 120"); near(G[180], 0.123, 0.0005, "g 180")
LOC_RAW_800 = lc("loc_raw", "P2_800_b120 vs P2_800_b275", "V1", "ratio")
LOC_RAW_500 = lc("loc_raw", "P2_500_270 vs P2_500_110_140", "V1", "ratio")
near(LOC_RAW_800, -23.0, 0.05, "raw loc V1 800"); near(LOC_RAW_500, -2.8, 0.05, "raw loc V1 500")
PAIRS = ["P2_800_b120 vs P2_800_b275", "P2_500_270 vs P2_500_110_140", "P2_800_b120 vs P2_800_all",
         "P2_800_b275 vs P2_800_all"]
RESID = {p: lc("loc_resid", p, "V1", "ratio") for p in PAIRS}
for p, e in zip(PAIRS, [3.0, 6.7, 6.4, 2.9]):
    near(RESID[p], e, 0.05, f"H_C residual {p}")
N_CONTRA = int(lc("prediction", "no residual location effect (V1, N4)"))
N_RESID_READS = int((loc["kind"] == "loc_resid").sum())
near(N_CONTRA, 7, 0, "LOCATION EFFECT reads"); near(N_RESID_READS, 8, 0, "residual reads")
POOL_TWH = lc("saturation", "pocket_pool_base_v3", "V1") / 1e6
R9_TWH = lc("saturation", "R_row9", "V1") / 1e6
R9_SHARE = lc("saturation", "R_row9_over_pool", "V1")
E_ROW6 = lc("saturation", "e_row6", "V1")
E_ROW9 = lc("saturation", "e_row9", "V1")
D700_TWH = lc("saturation", "R_row9_minus_R_row6", "V1") / 1e6
near(POOL_TWH, 4.87, 0.005, "pocket pool TWh"); near(R9_TWH, 4.03, 0.005, "row 9 relief TWh")
near(R9_SHARE, 0.83, 0.005, "row 9 share"); near(E_ROW6, 0.79, 0.005, "e row 6")
near(E_ROW9, 0.730, 0.0005, "e row 9"); near(D700_TWH, 1.51, 0.005, "last 700 MW TWh")
LC_PEM = {it: lc("pem_mw", it) for it in loc.loc[loc.kind == "pem_mw", "item"] if it.startswith("P")}
assert abs(LC_PEM["P3_1500_all"] - 1500) < 1e-6 and abs(LC_PEM["P2_800_all"] - 800) < 1e-6
text_has(P["locmd"], "All six sites share one PTDF on L252", "it means \"not explained by H_C\", not \"network\"")

# ---------------------------------------------------------------- slide 11 / 12: plan + agenda facts
text_has(P["noisemd"], "noise_v3 860.7 s (noise_v3/B:1")
near(noisej["determinism_conditions"]["noise_v3_solve"]["max_solve_s"], 860.7, 0.05, "noise_v3 max RUC solve s")
text_has(PLAN, "1,157 s (random_E:22, slow node) against the 1,200 s limit: ≈ 4 %",
         "the\nmargin is ≈ 1.4×, not 25×")
near(1200 / 860.7, 1.4, 0.05, "1,200 / 860.7")
near((1200 - 1157) / 1200, 0.04, 0.005, "(1,200 - 1,157) / 1,200")
text_has(PI_AGENDA, "M ≠ 4 reopens plan §6.4 gate numbers (C2/C3 false-alarm rates were set for M = 4)")
text_has(P["seedmd"], "nav = the first 32 or all 48 Sobol rows")
text_has(PLAN, "C2 coverage", "C3 outlier", "IMMUTABLE after freeze", "R = nadir + 0.1 × (nadir − ideal)")
text_has(P["n0md"], "random_E not read; holdout exposure 0 of 24")
text_has(PLAN, "The 96 landed runs' objective values (to compute\nR, the ledger and this table)")
text_has(PLAN, "2 × 156 = 312\n  MWh", "the strategy\n  session's dated `design_space_E.json` carries it")
text_has(P["noisemd"], "11.0.2", "gurobipy == 13.0.2", "NOT DISCOVERABLE")
text_has(P["seedmd"], "Gurobi 13.0.2" if "Gurobi 13.0.2" in P["seedmd"].read_text() else "(13, 0, 2)")
text_has(PLAN, "Gurobi 13.0.2 is logged on every run")
text_has(P["locmd"], "## 8. Scope sentence for the paper")
text_has(P["n0md"], "B_j is transferred from single-site off-slate designs")

# ---------------------------------------------------------------- appendix A: SHAs (git)
APPX_A_SHAS = ["bac38e7", "6aa29dd", "6b5e85a", "82bb71d", "d706199", "3b40c2d", "4b7bf85", "d265580",
               "6fd3352", "14378fd", "c986da0", "1a2cde6"]
SHA_SUBJ = {s: (commit_exists(s), git("log", "-1", "--format=%s", s))[1] for s in APPX_A_SHAS}

# ---------------------------------------------------------------- appendix B: wave D under both rulers
WD_OLD = {j: [std.loc[j, f"range_over_ruler_L{m}"] for m in (60, 120, 180)] for j in ["R4", "N1"]}
WD_B = {j: [ed1b.loc[j, f"waveD_range_over_B_L{m}"] for m in (60, 120, 180)] for j in ["R4", "N1"]}
for j, exp in {"R4": [7.7, 6.9, 13.5], "N1": [4.9, 9.4, 8.9]}.items():
    for v, e in zip(WD_OLD[j], exp):
        near(v, e, 0.05, f"{j} wave D range/ruler_57")
for j, exp in {"R4": [1.04, 0.94, 1.84], "N1": [0.64, 1.23, 1.16]}.items():
    for v, e in zip(WD_B[j], exp):
        near(v, e, 0.005, f"{j} wave D range/B_j")

# ---------------------------------------------------------------- appendix E: core-h
def _coreh(rel, slots=4):
    w = pd.read_csv(E / "extracts" / rel / "wallclock.csv")
    return len(w), w["wall_s"].sum() / 3600 * slots


CORE = {
    "base_v3": _coreh("base_v3"),
    "wave D (location_oat_v2)": _coreh("location_oat_v2"),
    "noise_v3 (A + B)": tuple(a + b for a, b in zip(_coreh("noise_v3/A"), _coreh("noise_v3/B"))),
    "location_contrast_E": _coreh("location_contrast_E"),
    "screening_v3": _coreh("screening_v3"),
}
near(CORE["base_v3"][1], 44.1, 0.05, "base_v3 core-h")
near(CORE["wave D (location_oat_v2)"][1], 584.0, 0.05, "wave D core-h")
near(CORE["noise_v3 (A + B)"][1], 654.6, 0.05, "noise_v3 core-h")
near(CORE["location_contrast_E"][1], 182, 0.5, "location_contrast core-h")
near(CORE["screening_v3"][1], 259, 0.5, "screening_v3 core-h")
text_has(E / "waves" / "screening_v3" / "screening_v3_array.sh", "-pe smp 4")
text_has(E / "waves" / "location_contrast_E" / "location_contrast_E_array.sh", "-pe smp 4")
text_has(PLAN, "**Total 3,006 core-h for 96 runs (31.3 per run)**")
SEED_COREH = seedj["runtime_core_h"]["total"]
near(SEED_COREH, 590, 0.5, "noise_seed_E core-h (json; mixed 4 / 8 / 1 slots)")

# ---------------------------------------------------------------- landed 11-18 (62 session): Seed-bar re-grade
P["seedbar_md"] = SEEDBAR_MD
P["seedbar"] = SEEDBAR_CSV
assert HAVE_SEEDBAR, "POOL_N0E_STANDINGS_seedbar.md / pool_ed1b_combined_seedbar.csv must exist (landed baf77c3)"
sb = pd.read_csv(SEEDBAR_CSV).set_index("id")
near(len(sb), 28, 0, "seedbar rows")
near(sb.loc["N1", "IDR_over_B"], 3.05, 0.005, "seedbar N1 IDR/B (binding)")
assert sb.loc["N1", "bar_source"].startswith("seed")
for j in ["V1", "E1", "R4", "N1", "N4"]:
    assert abs(sb.loc[j, "IDR_over_B_seed_sensitivity"] - RS[j]) < 1e-9, j   # same number, two files
CHECKS.append("seedbar IDR_over_B_seed_sensitivity == IDR / B_seed (ercot_noise_seed.csv) for V1, E1, R4, N1, N4")
SB_SEATS = sb[sb["status"] == "OBJECTIVE"].index.tolist()
assert sorted(SB_SEATS) == ["E1", "N1", "V1"], SB_SEATS
text_has(SEEDBAR_MD, "→ **no seat changes**", "E9: B 0 → 1.342", "NOT RESPONDS (was READABLE (RULER=0))")
commit_exists("baf77c3")

# ---------------------------------------------------------------- landed 11-18 (62 session): screening_v3
assert HAVE_SCREENING_V3
P["sv3md"] = SCREENING_V3_MD
sv3loc = pd.read_csv(POOL / "screening_v3_locational.csv").set_index("id")
sv3dom = pd.read_csv(POOL / "screening_v3_dominance.csv")
sv3rank = pd.read_csv(POOL / "screening_v3_ranking.csv")
sv3sites = pd.read_csv(POOL / "screening_v3_sites.csv").set_index("site")
P["sv3loc"] = POOL / "screening_v3_locational.csv"
P["sv3dom"] = POOL / "screening_v3_dominance.csv"
P["sv3rank"] = POOL / "screening_v3_ranking.csv"
P["sv3sites"] = POOL / "screening_v3_sites.csv"
N_SV3_GRADED = near(len(sv3loc), 23, 0, "screening_v3 graded ids (Holm family)")
SV3_LOCATIONAL = sv3loc[sv3loc["verdict"] == "LOCATIONAL"].index.tolist()
assert SV3_LOCATIONAL == ["V1", "E1", "N4", "N5", "E6", "E3", "V3"], SV3_LOCATIONAL
SV3 = {j: (sv3loc.loc[j, "HL_over_B"], sv3loc.loc[j, "p_holm"]) for j in sv3loc.index}
for j, (hl, ph) in {"V1": (-33.1, 0.036), "E1": (-8.7, 0.036), "N4": (-2.7, 0.047), "N5": (4.3, 0.036),
                    "E6": (10.3, 0.036), "E3": (-4.6, 0.036), "V3": (-60.8, 0.036)}.items():
    near(SV3[j][0], hl, 0.05, f"screening_v3 {j} HL/B"); near(SV3[j][1], ph, 0.0005, f"screening_v3 {j} Holm p")
assert sv3loc.loc["N1", "verdict"] == "NOT LOCATIONAL" and sv3loc.loc["N1", "verdict_B_seed"] == "NOT LOCATIONAL"
near(sv3loc.loc["N1", "HL_over_B"], -3.0, 0.005, "screening_v3 N1 HL/B_pert")
near(sv3loc.loc["N1", "HL_over_B_seed"], -1.43, 0.005, "screening_v3 N1 HL/B_seed")
near(sv3loc.loc["N1", "p_holm"], 0.65, 0.005, "screening_v3 N1 Holm p")
assert sv3loc.loc["N1", "moses_lo"] < 0 < sv3loc.loc["N1", "moses_hi"]
for j in ["X1", "V2"]:
    assert sv3loc.loc[j, "verdict"] == "NOT LOCATIONAL" and sv3loc.loc[j, "p_holm"] > 0.05
N_SV3_SITES = len(sv3sites)
near(N_SV3_SITES, 16, 0, "screening_v3 sites")
near(int((sv3sites["E1_verdict"] == "WITHIN GAP BOUND").sum()), 16, 0, "E1 WITHIN GAP BOUND sites")
TOP6 = sv3rank.sort_values("rank_v3").head(6)["site"].astype(int).tolist()
assert TOP6 == [270, 275, 274, 110, 140, 146], TOP6
assert set(sv3rank[sv3rank.top6_v3].bus) <= {120, 2, 75}
text_has(SCREENING_V3_MD, "**SLATE BUS-SET HOLDS**", "entered ['275'], left ['163']",
         "Kendall τ_b(v2, v3) = 0.667 (exact p 0.000135)",
         "`screening_v3:11` overall.csv md5 = `location_oat_v2:3`")
OWN163 = near(sv3sites.loc[163, "own_share_of_relief"], 0.81, 0.005, "site 163 own-site share of relief")
def _undominated(obj):
    s = sv3dom[(sv3dom.objectives == obj) & (~sv3dom.dominated)]
    return {int(r.site): r.margin_bars for r in s.itertuples()}
DOM_N1 = _undominated("V1/E1/N1")
DOM_N4 = _undominated("V1/E1/N4")
assert set(DOM_N1) == {116, 91} and set(DOM_N4) == {116}
near(DOM_N1[116], 0.72, 0.005, "116 margin (V1/E1/N1)"); near(DOM_N1[91], 0.44, 0.005, "91 margin (V1/E1/N1)")
assert max(list(DOM_N1.values()) + list(DOM_N4.values())) < 1
for s in ["e58f4bd", "1c6e73e"]:
    commit_exists(s)
text_has(PLAN, "AMENDMENT 2026-11-18 — screening_v3 actuals + reads", "That is about 259\n  core-h in total.")
