"""Every number the ERCOT overnight deck (prompt 67 v1.1) prints, read from its source file at build time.

Imported by make_overnight_figs.py and make_overnight_deck.py. Nothing is typed in by hand: a value is either
computed from a CSV / JSON cell, or a literal string ASSERTED to occur in the named source file (`text_has`).
The prompt-67 value is asserted against the computed one (`near`), so a drift in a source stops the build.

Sources (prompt 67 §2; read-only; under trial_0826/ercot/ unless absolute):
  analysis/pool/{POOL_N0E_STANDINGS_v2.md, pool_ed1b_v2.csv, pool_pairs_v2.csv, pool_n0E_v2.py (steiger)}
  waves/design_space_E_2026-11-24.json, waves/n0_E/landing_R.json, analysis/methods_E/arms_E.json
  analysis/ercot_gp/{ERCOT_GP_STATUS.md, ercot_gp_status.csv, ercot_gp_status_v2.csv, ercot_gp_nstar_checks_v2.csv,
                     committed_configs.json, committed_configs_housefit.json, exposure_ledger.csv,
                     ercot_gp_lc_residuals_v2.csv, pi_agenda_E-D7_draft.md}
  analysis/emulator_E/{EMULATOR_BO.md, emulator_E_single_committed.csv, emulator_E_multi_committed.csv,
                       emulator_E_summary_committed.json, runs_compact/EMU_extras_committed.json,
                       runs_compact/EMU_extras_mm{A,B}.json (Appendix C)}
  HOUSE BLOCK (backup B4 ONLY): analysis/emulator_E/{emulator_E_summary.json, runs_compact/EMU_extras.json,
                       runs_compact/EMU_rerun_check.json}
  ERCOT_BO_PLAN.md (AMENDMENT 2026-11-14, 2026-11-24, 2026-11-24b), PROGRESS.md (Prompt 54 / 65 / 66)
  RTS: /Users/yilu/Documents/GitHub/RTS-GMLC/trial_0826/campaign/analysis/methods_C/V1/ledger.json (read at d6 via git show)
  admin/prompt/bogp/{PROGRESS.md (reviewer statements ONLY), pi-agenda.md, ercot-station-map.md}
Never read: extracts/n0_E, extracts/random_E.
"""

from __future__ import annotations

import json
import math
import subprocess
import sys
from pathlib import Path

import pandas as pd
from scipy.stats import binom, norm

HERE = Path(__file__).resolve().parent              # analysis/pi_overnight_1124/
E = HERE.parent.parent                              # trial_0826/ercot/
REPO = E.parent.parent
POOL = E / "analysis" / "pool"
GP = E / "analysis" / "ercot_gp"
EMU = E / "analysis" / "emulator_E"
PLAN = E / "ERCOT_BO_PLAN.md"
EPROG = E / "PROGRESS.md"
BOGP = Path("/Users/yilu/Documents/development/nd/research/admin/prompt/bogp")
APROG = BOGP / "PROGRESS.md"           # reviewer statements only
AGENDA = BOGP / "pi-agenda.md"
STATION = BOGP / "ercot-station-map.md"
RTS_REPO = Path("/Users/yilu/Documents/GitHub/RTS-GMLC")

P = {
    "poolmd": POOL / "POOL_N0E_STANDINGS_v2.md",
    "ed1b": POOL / "pool_ed1b_v2.csv",
    "pairs": POOL / "pool_pairs_v2.csv",
    "ds": E / "waves" / "design_space_E_2026-11-24.json",
    "R": E / "waves" / "n0_E" / "landing_R.json",
    "arms": E / "analysis" / "methods_E" / "arms_E.json",
    "gpmd": GP / "ERCOT_GP_STATUS.md",
    "gph": GP / "ercot_gp_status.csv",
    "gpv2": GP / "ercot_gp_status_v2.csv",
    "nsv2": GP / "ercot_gp_nstar_checks_v2.csv",
    "cc": GP / "committed_configs.json",
    "cch": GP / "committed_configs_housefit.json",
    "exp": GP / "exposure_ledger.csv",
    "lc2": GP / "ercot_gp_lc_residuals_v2.csv",
    "ed7": GP / "pi_agenda_E-D7_draft.md",
    "emumd": EMU / "EMULATOR_BO.md",
    "sgl": EMU / "emulator_E_single_committed.csv",
    "mul": EMU / "emulator_E_multi_committed.csv",
    "sumc": EMU / "emulator_E_summary_committed.json",
    "xc": EMU / "runs_compact" / "EMU_extras_committed.json",
    "xA": EMU / "runs_compact" / "EMU_extras_mmA.json",
    "xB": EMU / "runs_compact" / "EMU_extras_mmB.json",
    "sum_house": EMU / "emulator_E_summary.json",
    "x_house": EMU / "runs_compact" / "EMU_extras.json",
    "rerun": EMU / "runs_compact" / "EMU_rerun_check.json",
}

CHECKS: list[str] = []


# ---------------------------------------------------------------- helpers (pattern of pi_objectives/objective_facts.py)
def near(value, expected, tol, what):
    if not abs(float(value) - float(expected)) <= tol:
        raise RuntimeError(f"{what}: source {value!r} vs prompt {expected!r} (tol {tol})")
    CHECKS.append(f"{what}: {float(value):.6g} ≈ {expected} (± {tol})")
    return value


FROZEN_PATH = HERE / "external_snippets.json"   # snippets asserted in files OUTSIDE the repo, frozen at first build
FROZEN = json.load(open(FROZEN_PATH)) if FROZEN_PATH.exists() else {}
_FROZEN_NEW = False
WARNINGS: list[str] = []


def text_has(path: Path, *needles: str):
    """Assert each needle occurs in the file. Files outside the repo (admin PROGRESS / pi-agenda / station map) are
    asserted against the frozen copy in external_snippets.json; a live mismatch is only listed in WARNINGS."""
    global _FROZEN_NEW
    path = Path(path)
    external = not str(path.resolve()).startswith(str(REPO.resolve()))
    live = " ".join(path.read_text().split()) if path.exists() else None   # whitespace-normalized (md line wraps)
    needles = tuple(" ".join(n.split()) for n in needles)
    for nd in needles:
        if external:
            key = str(path)
            if nd in FROZEN.get(key, []):
                if live is None or nd not in live:
                    WARNINGS.append(f"external file changed since freeze: {path.name}: '{nd[:60]}'")
            else:
                if live is None or nd not in live:
                    raise RuntimeError(f"'{nd}' not found in {path} (and not frozen)")
                FROZEN.setdefault(key, []).append(nd)
                _FROZEN_NEW = True
            CHECKS.append(f"text in {path.name} (external; frozen in external_snippets.json): '{nd}'")
        else:
            if live is None or nd not in live:
                raise RuntimeError(f"'{nd}' not found in {path}")
            CHECKS.append(f"text in {path.name}: '{nd}'")
    return needles[0] if len(needles) == 1 else needles


def save_frozen():
    if _FROZEN_NEW or not FROZEN_PATH.exists():
        json.dump(FROZEN, open(FROZEN_PATH, "w"), indent=1, ensure_ascii=False)


def git(*args, repo=REPO) -> str:
    return subprocess.check_output(["git", "-C", str(repo), *args], text=True).strip()


def jl(p):
    return json.load(open(p))


TX123 = git("rev-parse", "--short=7", "ercot/tx123")
if TX123 != "de45242":
    raise RuntimeError(f"ercot/tx123 moved: {TX123} (deck built on de45242)")
CHECKS.append(f"git rev-parse ercot/tx123 = {TX123} == de45242")

# =============================================================================
# rule v2 standings (slides 3, 4, 5, Appendix B)
# =============================================================================
ed1b = pd.read_csv(P["ed1b"]).set_index("id")
pairs = pd.read_csv(P["pairs"]).set_index("pair")
near(len(ed1b), 28, 0, "pool_ed1b_v2.csv rows")
ETA_V1 = near(ed1b.loc["V1", "eta2_T"], 0.978, 0.0005, "V1 eta2_T")
ETA_E1 = near(ed1b.loc["E1", "eta2_T"], 0.64, 0.005, "E1 eta2_T")
RESID_E1 = near(ed1b.loc["E1", "resid_IDR_over_B"], 10.1, 0.05, "E1 residual IDR/B (composition residual ≈ 10 B)")
N4_IDRB = near(ed1b.loc["N4", "IDR_over_B"], 14.24, 0.005, "N4 IDR/B")
N4_MANTEL = near(ed1b.loc["N4", "mantel_p_resid"], 0.0253, 0.00005, "N4 residual Mantel p")
N1_RESID = near(ed1b.loc["N1", "resid_IDR_over_B"], 0.94, 0.005, "N1 residual IDR/B")
assert not bool(ed1b.loc["N4", "COMP_RESOLVABLE"]); CHECKS.append("N4 COMP_RESOLVABLE False (pool_ed1b_v2.csv)")
for j in ("V1", "E1"):
    assert str(ed1b.loc[j, "status"]).startswith("SEATED"), j
CHECKS.append("pool_ed1b_v2.csv status: V1, E1 SEATED (rule v2)")
assert str(ed1b.loc["N1", "role"]) == "PROXY" and str(ed1b.loc["R4", "role"]).startswith("PROXY(E2")
CHECKS.append("roles: N1 PROXY, R4 PROXY(E2 start-up cost) (pool_ed1b_v2.csv)")
OUTCOME_R = [j for j in ed1b.index if j.startswith("R") and ed1b.loc[j, "role"] == "OUTCOME"]
assert OUTCOME_R == []; CHECKS.append("no OUTCOME role in family R (pool_ed1b_v2.csv)")
RHO = {k: pairs.loc[k] for k in ("N4|V1", "N1|V1", "X1|E1", "N4|E1", "E1|V1")}
X1E1_RAW = near(RHO["X1|E1"]["rho_raw"], 0.982, 0.0005, "X1|E1 raw ρ")
X1E1_RES = near(RHO["X1|E1"]["rho_resid"], 0.968, 0.0005, "X1|E1 residual ρ")
N4V1_RAW = near(RHO["N4|V1"]["rho_raw"], 0.966, 0.0005, "N4|V1 raw ρ")
N1V1_RAW = near(RHO["N1|V1"]["rho_raw"], 0.95, 0.001, "N1|V1 raw ρ")
assert bool(RHO["N4|V1"]["REDUNDANT_given_p"]) and not bool(RHO["N4|V1"]["BORDERLINE_PAIR"])
CHECKS.append("pool_pairs_v2.csv N4|V1: REDUNDANT_given_p True, BORDERLINE_PAIR False")
FLOORS = {j: ed1b.loc[j, "floor_M"] for j in ("V1", "E1", "X1", "N4")}
near(FLOORS["V1"], 58287, 1, "floor V1 (MWh)")
near(FLOORS["E1"] / 1e6, 8.06, 0.005, "floor E1 ($M)")
near(FLOORS["X1"], 194521, 1, "floor X1 (t)")
near(FLOORS["N4"], 87.6, 1e-9, "floor N4 (h)")
NU = {j: int(ed1b.loc[j, "nu"]) for j in ed1b.index}
assert NU["V1"] == 22 and NU["D1"] == 20 and NU["D2"] == 20
CHECKS.append("ν = 22 (D1/D2 ν 20) in pool_ed1b_v2.csv")
# B_j formula check on every graded id: B_j = max(3√2 s_j, max|δ|)
for j in ed1b.index:
    b = max(3 * math.sqrt(2) * ed1b.loc[j, "s_j"], ed1b.loc[j, "max_abs_delta"])
    assert abs(b - ed1b.loc[j, "B_j"]) <= 1e-6 * max(1.0, abs(b)), j
CHECKS.append("B_j == max(3√2·s_j, max|δ|) for all 28 ids (pool_ed1b_v2.csv)")
POOLMD = text_has(P["poolmd"],
                  "v1 pre-registered (d706199): V: V1 · E: E1 · X: EMPTY · R: EMPTY · N: N1",
                  "v1 Seed-bar re-grade (baf77c3): V: V1 · E: E1 · X: EMPTY · R: EMPTY · N: N1",
                  "v2 (this read): V: V1 · E: E1 · X: EMPTY · R: EMPTY · N: EMPTY",
                  "block sha256 `e3712a7f4d8e0542d5421ed13453fd0a722a582fa7b087b6b34d831581ac28be`",
                  "Kay overrode that clause for this read: commit the rule's actual output, never tuned")
text_has(PLAN, "Rule v2 is pre-registered unchanged for the next dataset, which is its real test.",
         "s_j² = (6·s²_pert + 16·s²_seed)/22, ν = 22",
         "B_j = max(3·√2·s_j, max|δ| over the 6 perturbed and 16 Seed deltas)",
         "Steiger's Z for dependent correlations sharing s")
# physics line: §6a + the acceptance review (reviewer statement, admin PROGRESS)
text_has(P["gpmd"], "with the same PTDF — the six sites are one electrical location")
text_has(APROG, "N4's composition signal is the cost of diverting deliverable wind, which E1 already prices")

# --- Appendix B counterfactual: Steiger recomputed at build time with pool_n0E_v2.steiger
sys.path.insert(0, str(POOL))
import pool_n0E_v2 as PV2  # noqa: E402

THR = {"RESOLVED_LO": PV2.RESOLVED_LO, "MANTEL_ALPHA": PV2.MANTEL_ALPHA, "FLOOR_BARS": PV2.FLOOR_BARS,
       "FLAGGED": PV2.FLAGGED, "RHO_RED": PV2.RHO_RED, "RHO_RESID": PV2.RHO_RESID}
for k_, v_ in zip(THR, (2.0, 0.01, 2.0, 3.0, 0.90, 0.50)):
    near(THR[k_], v_, 0, f"rule-v2 threshold pool_n0E_v2.{k_} (slide-4 equation)")
text_has(PLAN, "Seatable iff role OUTCOME AND RESOLVED AND IDR ≥ max(2·B_j, M_j) AND IDR/B (point) ≥ 3 AND not suppressed",
         "RESOLVED iff lower-90 % joint bound of IDR/B ≥ 2 AND raw Mantel p ≤ 0.01",
         "COMPOSITION-RESOLVABLE iff residual Mantel p ≤ 0.01 AND lower-90 % joint bound of IDR(r_j)/B_j ≥ 2 AND IDR(r_j) ≥ M_j",
         "oriented raw ρ(c, p) ≥ 0.90 AND NOT ESCAPE",
         "the 90 % interval of residual ρ(c, p) lies entirely below 0.50")

rcs, rps, rcp = (float(RHO["N4|E1"]["rho_resid"]), float(RHO["E1|V1"]["rho_resid"]), float(RHO["N4|V1"]["rho_resid"]))
STEIGER_Z, STEIGER_P = PV2.steiger(rcs, rps, rcp)
CHECKS.append(f"Steiger Z RECOMPUTED (pool_n0E_v2.steiger, n_eff {PV2.STEIGER_N}) for c = N4, p = V1, s = E1 from "
              f"pool_pairs_v2.csv rho_resid (N4|E1 {rcs:.4f}, E1|V1 {rps:.4f}, N4|V1 {rcp:.4f}): "
              f"Z = {STEIGER_Z:.4f}, one-sided p = {STEIGER_P:.3g}")
N4E1_UP = float(RHO["N4|E1"]["rho_resid_hi90"])
N4V1_RES_LO, N4V1_RES_HI = float(RHO["N4|V1"]["rho_resid_lo90"]), float(RHO["N4|V1"]["rho_resid_hi90"])
assert N4E1_UP <= -0.50 and STEIGER_P <= PV2.STEIGER_ALPHA and N4V1_RES_LO <= 0.50 <= N4V1_RES_HI
CHECKS.append(f"counterfactual: N4|E1 residual ρ upper-90 {N4E1_UP:.3f} ≤ −0.50; Steiger p ≤ 0.05; N4|V1 residual "
              f"90 % interval [{N4V1_RES_LO:.3f}, {N4V1_RES_HI:.3f}] contains 0.50 → §4b would resolve NOT REDUNDANT")
text_has(APROG, "Mantel p 0.023–0.027 across", "counterfactual: with that clause",
         "passed §4b would seat N4")

# =============================================================================
# the BO problem (slide 4)
# =============================================================================
ds, arms, Rj = jl(P["ds"]), jl(P["arms"]), jl(P["R"])
assert list(ds["objectives"]) == ["V1", "E1"] and ds["M"] == 2 and ds["identity"] == "v3"
CHECKS.append("design_space_E_2026-11-24.json: objectives [V1, E1], M 2, identity v3")
N_SITES = near(len(ds["sites"]), 6, 0, "design-space sites (u ∈ [0,1]^6)")
N0 = near(ds["tiers"]["grading"], 48, 0, "n0_E grading tier")
Q = near(arms["q"], 8, 0, "arms_E q")
CAP = near(arms["hard_cap"], 4, 0, "arms_E hard_cap")
LANES = near(len(arms["arms"]["qnehvi"]["seed_ids"]), 5, 0, "arms_E seed lanes")
BUDGET = near(LANES * CAP * Q, 160, 0, "BO budget lanes × cap × q (PCM runs)")
text_has(P["arms"], "1 arm x 5 seeds x cap 4 x q 8 = 160 BO runs")
assert arms["qnehvi"]["acq"] == "qNoisyExpectedHypervolumeImprovement" and arms["objectives"] == ["V1", "E1"]
CHECKS.append("arms_E.json: qNEHVI, objectives [V1, E1]")
assert arms["calibration"]["C2"]["action"].startswith("record + REVIEW flag; never halts")
assert arms["calibration"]["C3"]["action"].startswith("record + REVIEW flag; never halts")
CHECKS.append("arms_E.json: C2 / C3 action = record + REVIEW flag; never halts")
R_V1 = near(Rj["R"]["V1"], 3977491, 1, "landing_R V1 (MWh)")
R_E1 = near(Rj["R"]["E1"] / 1e6, 8163.73, 0.005, "landing_R E1 ($M)")
text_has(PLAN, "τ_exact = 0 (Σ_exact = 0, 5ca9650) → the stop rule is budget-cap-only")
text_has(P["emumd"], "eps ~ N(0, Sigma_c[V1, E1])")

# =============================================================================
# GP fits (slides 3, 6, 7, B1, Appendix D)
# =============================================================================
cc, cch = jl(P["cc"]), jl(P["cch"])
gph, gpv2 = pd.read_csv(P["gph"]), pd.read_csv(P["gpv2"])
hold_h = gph[gph.scope == "holdout"].set_index(["objective", "n"])
hold_v2 = gpv2[gpv2.scope == "holdout"].set_index("objective")
loo_h = gph[(gph.scope == "loo") & (gph.selected == True)].set_index(["objective", "n"])  # noqa: E712
loo_v2 = gpv2[gpv2.scope == "loo"].set_index(["objective", "n", "arm", "floor_mode"])

HOLD = {j: int(hold_h.loc[(j, 48), "holdout_cov95"]) for j in ("V1", "E1", "N4", "N1")}
assert HOLD == {"V1": 45, "E1": 48, "N4": 48, "N1": 41}, HOLD
CHECKS.append(f"house holdout cov95 at n = 48 (ercot_gp_status.csv): {HOLD}")
assert not bool(hold_h.loc[("N1", 48), "holdout_pass"])
HOLD_V2 = {j: int(hold_v2.loc[j, "holdout_cov95"]) for j in ("V1", "E1")}
assert HOLD_V2 == {"V1": 37, "E1": 48}; CHECKS.append(f"v2 holdout cov95 (ercot_gp_status_v2.csv): {HOLD_V2}")
assert cc["objectives"]["V1"]["fit_definition"] == "house (fallback)"
assert cc["objectives"]["E1"]["fit_definition"].startswith("v2")
CHECKS.append("committed_configs.json fit_definition: V1 house (fallback), E1 v2 (AMENDMENT 2026-11-24b)")
assert cc["n_star"] == 48 and cc["n_star_v2"] == 48 and cc["E-D7_decided"] is None
CHECKS.append("committed_configs.json: n_star 48, n_star_v2 48, E-D7_decided null")
text_has(P["cc"], "n = 44: V1 (rbf+std): RMSE ratio 1.120 > 1.1; E1 (m52+std): RMSE ratio 1.116 > 1.1")
B = {j: ed1b.loc[j, "B_j"] for j in ("V1", "E1", "N4", "N1")}
LOO_V1 = cch["objectives"]["V1"]["loo_rmse"]; LOO_E1 = cch["objectives"]["E1"]["loo_rmse"]
near(LOO_V1 / 1e3, 30.6, 0.05, "house LOO RMSE V1 (k MWh)")
near(LOO_E1 / 1e6, 3.30, 0.005, "house LOO RMSE E1 ($M)")
LOO_V1_B = near(LOO_V1 / B["V1"], 1.63, 0.01, "house LOO RMSE V1 / B_j")
LOO_E1_B = near(LOO_E1 / B["E1"], 1.77, 0.005, "house LOO RMSE E1 / B_j")
NOISE_H = {j: float(loo_h.loc[(j, 48), "noise_over_sigma_c"]) for j in ("V1", "E1")}
near(NOISE_H["V1"], 3.97, 0.005, "house inferred noise / σ_c V1"); near(NOISE_H["E1"], 2.65, 0.005, "house inferred noise / σ_c E1")
near(NOISE_H["E1"], 2.7, 0.06, "title '2.7–4×' low end = E1 2.646 (printed 2.65; the verbatim title rounds 2.65 up)")
near(round(NOISE_H["V1"]), 4, 1e-9, "title '2.7–4×' high end = V1 3.97 rounded")
# like-for-like v2 V1 ratios 44 → 48 and the cross-arm 1.46
def _v2(obj, n, arm):
    return float(loo_v2.loc[(obj, n, arm, "inferred"), "loo_rmse"])
LFL_RBF = _v2("V1", 44, "rbf+std") / _v2("V1", 48, "rbf+std")
LFL_M52 = _v2("V1", 44, "m52+std") / _v2("V1", 48, "m52+std")
CROSS = _v2("V1", 44, "m52+std") / _v2("V1", 48, "rbf+std")
near(LFL_RBF, 1.255, 0.0005, "v2 V1 LOO RMSE 44/48 rbf+std (same arm)")
near(LFL_M52, 1.285, 0.0005, "v2 V1 LOO RMSE 44/48 m52+std (same arm)")
near(CROSS, 1.46, 0.005, "v2 V1 LOO RMSE 44 m52 / 48 rbf (cross-arm)")
text_has(P["gpmd"], "m52+std 17,372 MWh / 13,520 MWh = 1.285; rbf+std 14,904 MWh / 11,880 MWh = 1.255")
text_has(P["gpmd"], "n\\* = 48 means that no tier below 48 suffices. Whether 48 suffices is untested.")
# slide 7 table
V1v2 = cc["objectives"]["V1"]["v2_result"]; E1v2 = cc["objectives"]["E1"]
LS_V1 = [V1v2["hyperparameters"]["lengthscales_u"][s] for s in ("110", "140", "146", "163", "270", "274")]
LS_E1 = [E1v2["hyperparameters"]["lengthscales_u"][s] for s in ("110", "140", "146", "163", "270", "274")]
NOISE_V2 = {"V1": V1v2["hyperparameters"]["noise_over_sigma_c"], "E1": E1v2["hyperparameters"]["noise_over_sigma_c"]}
near(NOISE_V2["V1"], 0.98, 0.005, "v2 V1 noise / σ_c (scored config)"); near(NOISE_V2["E1"], 0.61, 0.005, "v2 E1 noise / σ_c")
CONV = {"V1": int(loo_v2.loc[("V1", 48, "rbf+std", "inferred"), "n_within_tol"]),
        "E1": int(loo_v2.loc[("E1", 48, "m52+std", "inferred"), "n_within_tol"])}
assert CONV == {"V1": 14, "E1": 12}; CHECKS.append("v2 converged restarts within tol: V1 14/16, E1 12/16 (ercot_gp_status_v2.csv)")
GAP = {"V1": V1v2["mode_gap_nats"], "E1": E1v2["mode_gap_nats"]}
near(GAP["V1"], 119, 0.5, "v2 V1 mode gap (nats)"); near(GAP["E1"], 52.9, 0.05, "v2 E1 mode gap (nats)")
NLPD = {"V1": (V1v2["loo_nlpd_mean"], cch["objectives"]["V1"]["loo_nlpd_mean"]),
        "E1": (E1v2["loo_nlpd_mean"], cch["objectives"]["E1"]["loo_nlpd_mean"])}
near(NLPD["V1"][0], 10.80, 0.006, "LOO NLPD v2 V1"); near(NLPD["V1"][1], 11.73, 0.005, "LOO NLPD house V1")
near(NLPD["E1"][0], 15.81, 0.005, "LOO NLPD v2 E1"); near(NLPD["E1"][1], 16.25, 0.005, "LOO NLPD house E1")
RMSZ_V2 = {j: float(hold_v2.loc[j, "holdout_rms_z"]) for j in ("V1", "E1")}
near(RMSZ_V2["V1"], 1.64, 0.005, "v2 holdout rms z V1"); near(RMSZ_V2["E1"], 0.74, 0.005, "v2 holdout rms z E1")
HNLPD = {"V1": (float(hold_v2.loc["V1", "holdout_nlpd"]), float(hold_h.loc[("V1", 48), "holdout_nlpd"])),
         "E1": (float(hold_v2.loc["E1", "holdout_nlpd"]), float(hold_h.loc[("E1", 48), "holdout_nlpd"]))}
near(HNLPD["V1"][0], 11.31, 0.005, "v2 holdout NLPD V1"); near(HNLPD["V1"][1], 11.73, 0.005, "house holdout NLPD V1")
HRMSE = {"V1": (float(hold_v2.loc["V1", "holdout_rmse"]), float(hold_h.loc[("V1", 48), "holdout_rmse"])),
         "E1": (float(hold_v2.loc["E1", "holdout_rmse"]), float(hold_h.loc[("E1", 48), "holdout_rmse"]))}
near(HRMSE["V1"][0], 16101, 1, "v2 holdout RMSE V1"); near(HRMSE["V1"][1], 37361, 1, "house holdout RMSE V1")
RATIO_ACC = near(HRMSE["V1"][1] / HRMSE["V1"][0], 2.3, 0.05, "V1 house / v2 holdout RMSE (2.3× more accurate)")
P_CHANCE = near(binom.cdf(37, 48, 0.95), 2e-5, 0.5e-5, "P(≤ 37 | 48, 0.95)")
text_has(P["gpmd"], "P(≤ 37 | 48, 0.95) = 2e-05")
LC2 = pd.read_csv(P["lc2"])
lv1 = LC2[LC2.objective == "V1"].set_index("label")["z"]
N_OUT = near(int((lv1.abs() > 1.96).sum()), 5, 0, "prompt-61 residuals under v2: V1 |z| > 1.96 count (of 9)")
near(len(lv1), 9, 0, "prompt-61 residual designs")
Z270 = near(lv1["P2_500_270"], 5.64, 0.005, "V1 v2 z at P2_500_270")
LSR = (min(LS_V1), max(LS_V1)); near(LSR[0], 1.9, 0.05, "V1 v2 rbf lengthscale min (u)"); near(LSR[1], 5.9, 0.05, "V1 v2 rbf lengthscale max (u)")
NOISE44 = near(float(loo_v2.loc[("V1", 44, "rbf+std", "inferred"), "noise_over_sigma_c"]), 1.15, 0.005, "V1 rbf v2 noise/σ_c at n = 44")
PRIOR_MODE = near(math.exp(-0.5), 0.61, 0.005, "noise-prior MAP mode e^(−½) (σ_c units)")
text_has(P["gpmd"], "Its mode is at e^(μ − 1), i.e. 0.61 σ_c in sd")
HO_OVER_LOO = near(HRMSE["V1"][0] / V1v2["loo_rmse"], 1.36, 0.005, "V1 v2 holdout RMSE / LOO RMSE")
text_has(P["gpmd"], "holdout band sd (median 8,315 MWh) is narrower than the LOO band sd (median 12,106 MWh)")
text_has(P["gpmd"], "the fit change was designed after the house holdout results were known (8 scorings; the diagnostic 65179e1 was coded 7 min later)")
EXPL = pd.read_csv(P["exp"])
EXPO = near(len(EXPL), 10, 0, "exposure ledger scorings (of 24)")
text_has(P["gpmd"], "10 of 24 scorings in total; retired")
text_has(APROG, "V1 needs structure (linear mean / additive or site-interaction kernel), not wider bars")
FIT_V2_SPEC = cc["fit_v2_spec"]
text_has(P["arms"], "(Adam, 700 epochs, lr 0.01), float64 SingleTaskGP per objective")
text_has(P["emumd"], "`bogp.train_gp` Adam 700 steps, lr 0.01, float32")
text_has(P["emumd"], "the fit-v2 V1 truth puts f* at the all-PEM vertex")
text_has(P["emumd"], "`bogp.train_gp` Adam 700 steps, lr 0.01")
text_has(P["ed7"], "**Recommendation (i): the mixed commit as committed.**",
         "(c) 44 only under a 1.12 ratio bar", "a second re-open, forbidden by AMENDMENT 2026-11-24b §4",
         "a re-selection after scoring", "discards E1's verified gain")
NS2 = pd.read_csv(P["nsv2"])

# =============================================================================
# emulator, COMMITTED block (slides 3, 8, 9, 10, 11; Appendix C)
# =============================================================================
sumc, xc, xA, xB = jl(P["sumc"]), jl(P["xc"]), jl(P["xA"]), jl(P["xB"])
mul, sgl = pd.read_csv(P["mul"]), pd.read_csv(P["sgl"])
pf = {d["n"]: d for d in sumc["pass_fail"]}
assert pf[1]["result"] == "single 12/12, multi 15/15, ends as expected = True" and pf[1]["pass"]
assert pf[2]["result"] == "45/45" and pf[6]["result"] == "s0 True, s1 True, s2 True"
assert pf[7]["result"] == "cap-only True; monitors quiet True" and pf[8]["result"] == "multi 45/45, single 15/15"
assert "n_hv 55/63/71/79" in pf[6]["check"]
CHECKS.append("emulator_E_summary_committed.json pass_fail 1, 2, 6, 7, 8: 12/12 single, 15/15 multi, C1 45/45, "
              "branches s0/s1/s2, cap-only + monitors quiet, fit v2 converged 45/45 + 15/15 (= 60/60)")
m = mul[mul.variant == "committed"]
s0r4 = m[(m.scenario == "s0") & (m["round"] == 4)]["hv_true_frac_best"]
near(len(s0r4), 5, 0, "committed s0 lanes at r4")
HV_LO, HV_HI = near(s0r4.min(), 0.971, 0.0005, "s0 r4 HV frac min"), near(s0r4.max(), 0.980, 0.0005, "s0 r4 HV frac max")
s1 = m[(m.scenario == "s1") & (m["round"] >= 1)]
assert sorted(s1.groupby("round")["n_hv"].first().astype(int).tolist()) == [55, 63, 71, 79]
CHECKS.append("multi committed s1 n_hv per round 55/63/71/79")
_g = m[(m["round"] >= 1) & m["C2"].notna()]   # graded rows (s2 r2 = refused propose, no grade)
MULTI_C2 = int((_g["C2"].astype(str) == "True").sum()); MULTI_N = len(_g)
near(MULTI_C2, 0, 0, "multi committed C2 count"); near(MULTI_N, 45, 0, "multi committed graded (lane, round) rows")
bl = xc["baselines"]
UNI = [bl["uniform"][q][4] for q in ("p5", "p50", "p95")]
near(UNI[0], 0.667, 0.0005, "uniform r4 p5"); near(UNI[1], 0.683, 0.0005, "uniform r4 p50"); near(UNI[2], 0.712, 0.0005, "uniform r4 p95")
VERT95 = near(bl["vertices"]["p95"][4], 0.918, 0.0005, "random vertices r4 p95 (committed)")
SPREAD = near(bl["plugin_spread"]["p50"][4], 0.966, 0.0005, "r0 plug-in spread r4 (committed)")
NREP = near(bl["uniform"]["n_rep"], 1000, 0, "baseline replicates")
PLUG_V1 = near(xc["r0_plugin"]["committed"]["objectives"]["V1"]["regret_B"], 0.086, 0.0005, "r0 plug-in regret V1 (B)")
PLUG_E1 = xc["r0_plugin"]["committed"]["objectives"]["E1"]["regret_B"]
assert PLUG_E1 < 1e-9; CHECKS.append(f"r0 plug-in regret E1 = {PLUG_E1:.2g} B (≈ 0)")
smB = sgl[(sgl.variant == "mmB") & (sgl.objective == "V1")].set_index("round")
MMB_PLUG = near(smB.loc[0, "r0_plugin_regret_B"], 1.31, 0.005, "mismatch B V1 r0 plug-in regret (B)")
MMB_PM4 = near(smB.loc[4, "regret_pm_opt_B"], 0.050, 0.0005, "mismatch B V1 posterior-mean incumbent regret r4 (B)")
MMB_BO4 = near(smB.loc[4, "regret_best_obs_B"], 0.293, 0.0005, "mismatch B V1 best-observed regret r4 (B)")
text_has(P["emumd"], "BO's minimum true f among evaluated designs reaches 0.002 B by r2",
         "the best observation's noise is -0.76 and -1.40 chatter sd at r3 / r4",
         "u = 0 lies 0.34 lengthscales from the nearest start point",
         "report incumbents by posterior mean or by replicates, not by best observed")
# calibration event (slide 10)
sc = sgl[(sgl.variant == "committed") & (sgl.method == "bo")]
e1 = sc[sc.objective == "E1"].set_index(["seed_id", "round"])
EV_COV = near(e1.loc[(0, 2), "cov95"], 3, 0, "E1 single seed 0 r2 cov95 (C2 + C3 batch)")
assert bool(e1.loc[(0, 2), "C2"]) and bool(e1.loc[(0, 2), "C3"]) and int(e1.loc[(0, 2), "n_at_origin"]) == 8
CHECKS.append("E1 single seed 0 r2: C2 True, C3 True, 8 designs at the origin")
near(e1.loc[(0, 1), "n_at_origin"], 2, 0, "E1 seed 0 r1 designs at u = 0 (observed twice in r1)")
FIT_NOISE = near(e1.loc[(0, 1), "noise_over_sigma_c"], 0.676, 0.0005, "E1 r1 fit noise / σ_c (the fit used at r2)")
RHO_REP = near(e1.loc[(0, 1), "noise_over_chatter"], 0.53, 0.005, "ρ = fit noise / emulator noise")
EMU_NOISE = near(FIT_NOISE / RHO_REP, 1.274, 0.001, "emulator noise / σ_c (= 0.676 / 0.531)")
REP_COV = near(2 * norm.cdf(1.96 * RHO_REP) - 1, 0.70, 0.005, "replicate coverage 2Φ(1.96ρ) − 1")
text_has(P["emumd"], "P(C2) 0.10, P(C3) 0.018", "(the review's model gave 0.22 / 0.083 / 0.07)")
r24 = sc[(sc.objective == "E1") & (sc["round"] >= 2)]
ORIG = near(int(r24["n_at_origin"].sum()), 71, 0, "single E1 r2–r4 designs at u = 0"); near(8 * len(r24), 72, 0, "single E1 r2–r4 designs")
e1_fit = pd.concat([sc[(sc.objective == "E1") & (sc["round"] >= 0)]["noise_over_chatter"],
                    m[m["round"] >= 0]["E1_noise_over_emulator"]]).dropna()
NOE_LO, NOE_HI = near(e1_fit.min(), 0.31, 0.005, "E1 fit noise / emulator noise (min)"), near(e1_fit.max(), 0.99, 0.005, "E1 fit noise / emulator noise (max)")
pg = sumc["per_objective_gates"]
RMSZ_V1 = near(pg["V1"]["rms_z_median"], 0.17, 0.005, "V1 rms z median (committed)")
assert pg["V1"]["C2"] == 0 and pg["V1"]["C3"] == 0 and pg["V1"]["cells"] == 57
CHECKS.append("V1 C2 0, C3 0 in 57 cells (summary_committed)")
text_has(P["emumd"], "rms z median 0.17, i.e. the V1 bands are ≈ 6× too wide")
# seed overlap (slide 11)
so = xc["seed_overlap"]
UNIQ = [r["n_unique"] for r in so["per_round"]]
assert UNIQ == [24, 38, 35, 38] and all(r["n_designs"] == 40 for r in so["per_round"])
CHECKS.append("EMU_extras_committed seed_overlap unique per round 24/38/35/38 of 40")
JAC = (near(so["jaccard_range"][0], 0.10, 0.005, "Jaccard min"), near(so["jaccard_range"][1], 0.16, 0.005, "Jaccard max"))
MIND = near(min(r["min_dist_to_evaluated"] for r in so["min_dist"]), 0.067, 0.0005, "closest re-proposal distance (u)")
assert all(r["n_below_1e-6"] == 0 for r in so["min_dist"]); CHECKS.append("no proposal within 1e-6 of an evaluated design")
DUP = near(so["r1_duplicate_runs_of_40"], 16, 0, "r1 duplicate runs of 40")
text_has(PLAN, "Per-run core-h range for planning: **21 (fast) – 44.6 (slow)**")
text_has(AGENDA, "16 of 40 r1 runs would return identical outputs (≈ 340–720 core-h at 21–45 core-h/run)")
near(DUP * 21, 340, 5, "16 × 21 core-h"); near(DUP * 44.6, 720, 7, "16 × 44.6 core-h (≈ 720)")
text_has(P["emumd"], "< 1 % of a round (8 PCM runs × 5–11 h)")
# 55 changes / not-exercised (slide 8, B3)
text_has(P["emumd"], "`b2b2142` **zero-site fix (HIGH).**", "came back as 5.55e-17",
         "`c7576a6` `acquire_E.py` / `common_E.py`", "`c470d7b` hardening",
         "`0066a64` `HALT_FOR_DECISION.md` printed a literal",
         "**Code paths NOT exercised here:** `submit_state_E.py`, `acquire_E_job.sh`, the array and collector scripts, the ercot-bot commit / push, a real `__ALL__` wave ingest through `pool_objectives`, SUSPECT, a true R2 flag, resume after HALT (rename + rerun), and the Part B asserts.")
text_has(APROG, "a site proposed\n  at the lower bound comes back as 5.6e-17")
# Appendix C (matched-budget baselines per truth)
def _mm(x, var):
    b = x["baselines"]
    bo = mul[(mul.variant == var) & (mul.scenario == "s0") & (mul.seed_id == 0) & (mul["round"] == 4)]["hv_true_frac_best"].iloc[0]
    return b["vertices"]["p95"][4], b["plugin_spread"]["p50"][4], bo
APPC = {"committed": _mm(xc, "committed"), "mismatch A": _mm(xA, "mmA"), "mismatch B": _mm(xB, "mmB")}
for k, exp in {"committed": (0.918, 0.966, 0.971), "mismatch A": (0.910, 0.967, 0.977), "mismatch B": (0.940, 0.975, 0.988)}.items():
    for v, e, nm in zip(APPC[k], exp, ("vertices p95", "plug-in spread", "BO s0 seed 0")):
        near(v, e, 0.0005, f"Appendix C {k} r4 {nm}")

# =============================================================================
# emulator, HOUSE block — backup B4 ONLY
# =============================================================================
sumh, xh, rr = jl(P["sum_house"]), jl(P["x_house"]), jl(P["rerun"])
H_S0 = sumh["s0_r4_frac_best"]
H_S0R = (near(H_S0[0], 0.975, 0.0005, "HOUSE s0 r4 frac min"), near(H_S0[1], 0.979, 0.0005, "HOUSE s0 r4 frac max"))
H_PLUG = (near(xh["r0_plugin"]["house"]["objectives"]["V1"]["regret_B"], 0.086, 0.0005, "HOUSE r0 plug-in V1"),
          near(xh["r0_plugin"]["house"]["objectives"]["E1"]["regret_B"], 0.006, 0.0005, "HOUSE r0 plug-in E1"))
H_UNIQ = [r["n_unique"] for r in xh["seed_overlap"]["per_round"]]
assert H_UNIQ == [23, 36, 31, 35]; CHECKS.append("HOUSE seed overlap unique 23/36/31/35 of 40 (EMU_extras.json)")
H_DUP = near(xh["seed_overlap"]["r1_duplicate_runs_of_40"], 17, 0, "HOUSE r1 duplicate runs")
assert "C2 0, C3 0 in 114" in {d["n"]: d for d in sumh["pass_fail"]}[3]["result"]
CHECKS.append("HOUSE C2 0, C3 0 in 114 cells (emulator_E_summary.json)")
H_HV = near(rr["max_true_hv_rel_change"] * 100, 0.3, 0.05, "HOUSE path sensitivity: max true-f HV change (%)")
near(rr["max_hv_rel_change"] * 100, 0.3, 0.05, "HOUSE path sensitivity: max observed HV change (%)")
text_has(P["rerun"], "lane trajectories are not reproducible across a 1e-16 input change, only their aggregates are")

# =============================================================================
# RTS 49 V1 arm (B2) — ledger.json read at d6 8ed4c01 (git show, no checkout)
# =============================================================================
D6 = git("rev-parse", "--short=7", "d6", repo=RTS_REPO)
assert D6 == "8ed4c01", D6
LED = json.loads(git("show", "d6:trial_0826/campaign/analysis/methods_C/V1/ledger.json", repo=RTS_REPO))
CHECKS.append("RTS ledger.json read via git show d6 (8ed4c01)")
ent = {e["round"]: e for e in LED["entries"]}
near(LED["hard_cap"], 4, 0, "RTS V1 hard cap"); near(ent[4]["n"], 64, 0, "RTS V1 n at r4")
RTS = {k: ent[k] for k in (1, 2, 3, 4)}
for k, hv in zip((1, 2, 3, 4), (7.359e17, 7.664e17, 7.802e17, 7.962e17)):
    near(RTS[k]["hv"] / 1e17, hv / 1e17, 0.0005, f"RTS V1 r{k} HV (e17)")
for k, g in zip((1, 2, 3, 4), (7.53e16, 3.04e16, 1.38e16, 1.61e16)):
    near(RTS[k]["gain"] / 1e16, g / 1e16, 0.005, f"RTS V1 r{k} gain (e16)")
for k, a, b_, c in zip((1, 2, 3, 4), (1.43, 0.578, 0.262, 0.305), (11.57, 4.68, 2.12, 2.47), (24.9, 10.1, 4.56, 5.32)):
    near(RTS[k]["gain_tau"], a, 0.005, f"RTS V1 r{k} gain/τ_old")
    near(RTS[k]["gain_tau_285"], b_, 0.005, f"RTS V1 r{k} gain/τ_285")
    near(RTS[k]["gain_tau_het"], c, 0.05, f"RTS V1 r{k} gain/τ_het")
assert [RTS[k]["would_stop"] for k in (1, 2, 3, 4)] == [False, False, True, True]
assert not any(RTS[k]["would_stop_285"] or RTS[k]["would_stop_het"] for k in (1, 2, 3, 4))
CHECKS.append("RTS V1 would_stop (τ_old) r3, r4 only; τ_285 / τ_het never")
LRZ = RTS[4]["loo_rms_z"]
near(LRZ["load_shed_mwh"], 0.82, 0.005, "RTS r4 loo rms z shed"); near(LRZ["true_curtailment_mwh"], 0.76, 0.005, "RTS r4 loo rms z curt")
near(LRZ["total_cost_less_synthetic_usd"], 0.56, 0.005, "RTS r4 loo rms z cost")

# =============================================================================
# reviewer verdict lines (admin PROGRESS; cited as "acceptance review, 2026-11-24")
# =============================================================================
text_has(APROG, "**65 ACCEPTED by both reviewers (stats ACCEPT WITH\n  NOTES",
         "Power systems ACCEPT WITH NOTES: M = 2 is\n  physically right",
         "**54 B accepted (GP stats ACCEPT WITH NOTES; PI/QA FIX\n  THEN SHIP).**",
         "**54 v2 round accepted (GP stats ACCEPT WITH NOTES",
         "**66 three reviews in: BO stats ACCEPT WITH NOTES\n  (machinery check only); machinery/exec ACCEPT WITH NOTES",
         "audience FIX THEN SHIP.**",
         "**66 committed rerun accepted (ACCEPT WITH NOTES",
         "**RTS 49 V1 arm DONE at hard cap (d6 = 8ed4c01")
text_has(STATION, "| 3. Model validation |", "| 4. BO loop |", "| 6. Baseline + launch |")
text_has(AGENDA, "**UPDATE 11-24 (prompt 65, rule v2",
         "| 2026-11-24 | E-D7 | **ERCOT navigation tier n* (prompt 54 Part B",
         "| 2026-11-24 | E-D4 (part) | **Cross-lane duplicate designs under option C",
         "Strategy recommends reuse, disclosed.")
text_has(EPROG, "Accept or reject the r1 cross-seed assert change (\"sets differ\" instead of disjoint; c7576a6 + c470d7b)",
         "Meaning of a C2 REVIEW flag on a replicated design")
text_has(APROG, "make N3 / N1_off flags (b)(c) claims filters like R1")

# =============================================================================
# Appendix A — process log, times from git log --format=%ai (never PROGRESS clock times)
# =============================================================================
STEPS = [
    ("65", "plan AMENDMENT 2026-11-24 (rule v2) committed alone", "212d60d"),
    ("65", "pool_n0E_v2.py + tests", "b8a3285"),
    ("65", "real read: V1 · E1 (M = 2)", "ae6d80a"),
    ("65", "dated design space", "1f00a2d"),
    ("65", "erratum (disclosure wording)", "aa98045"),
    ("54 B", "code: training-size study", "dc316ef"),
    ("54 B", "code: exploratory long-fit diagnostic", "65179e1"),
    ("54 B", "outputs: n* = 48, holdout 8/24", "b23021c"),
    ("plan", "AMENDMENT 2026-11-24b (M = 2, fit v2, one re-open)", "93c81a4"),
    ("66", "arms_E.json as 55's proxy", "bc3168c"),
    ("66", "55 minimal changes (r1 assert 'sets differ')", "c7576a6"),
    ("66", "house-fit outputs", "76c1ae6"),
    ("66", "zero-site fix (snap_bounds + writer assert)", "b2b2142"),
    ("54 v2", "reporting fixes", "eb8c2da"),
    ("54 v2", "fit v2 round: V1 37/48 → house fallback; E1 48/48 → v2", "7bde505"),
    ("54 v2", "status page §0 / §13", "240bde1"),
    ("66 v2", "55 hook: per-objective fit definition", "36b74b7"),
    ("66 v2", "committed-fit outputs", "7457043"),
    ("54", "report-only fixes (GP-stats notes)", "81ea382"),
    ("66", "acceptance fixes, section A", "de45242"),
]
APPA = []
for step, what, sha in STEPS:
    ai = git("log", "-1", "--format=%ai", sha)
    git("merge-base", "--is-ancestor", sha, "ercot/tx123")
    APPA.append((step, what, sha, ai))
APPA.sort(key=lambda r: r[3])
EB_CI = git("log", "-1", "--format=%ci", "eb8c2da")
if not EB_CI.startswith("2026-11-24 03:22"):
    raise RuntimeError(EB_CI)
CHECKS.append(f"eb8c2da committer time {EB_CI} (rebased; author time used in Appendix A)")
near(dict((r[2], r) for r in APPA)["65179e1"][3] == "2026-11-24 01:58:15 -0500", 1, 0, "65179e1 author time 01:58:15")
CHECKS.append(f"Appendix A: {len(STEPS)} commits are ancestors of ercot/tx123; times from git log --format=%ai")
RTS_AI = git("log", "-1", "--format=%ai", "8ed4c01", repo=RTS_REPO)
CHECKS.append(f"RTS 8ed4c01 time {RTS_AI} (git log, RTS-GMLC repo)")

# B3 checklist counts (EMULATOR_BO.md §8: 13 items)
B3_DONE, B3_BLOCK, B3_OPEN_NB = (1, 3, 4), (2, 5, 6, 7, 8, 10, 11, 12, 13), (9,)
near(len(B3_DONE) + len(B3_BLOCK) + len(B3_OPEN_NB), 13, 0, "55 Part B checklist items (EMULATOR_BO.md §8)")
text_has(P["emumd"], "13. CRC: `acquire_E_job.sh --check-env`")
