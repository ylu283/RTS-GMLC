"""Prompt 65 (v1.1): E-D1b rule v2 re-walk on the n0_E population (zero simulation; disclosed post-hoc amendment).

Rules: plan ERCOT_BO_PLAN.md AMENDMENT 2026-11-24 (rule v2: memo §3 items 0-10 + the prompt-65 v1.1 §8
instantiations, which govern where they differ). The sha256 of that block is asserted before anything is
read; the v1 block (AMENDMENT 2026-11-17) is asserted unchanged. Candidates, directions, priorities and
global_order: pool_definitions.json at f76d897 (asserted). Roles: parsed from the committed role table.

Reads: the 48 n0_E rows ONLY through `pool_standings.build_wave("n0_E")` (pool_n0E.load_wide) and only in
the real run, plus (real run only, disclosed) the n0_E line_summary tables for N1_off / new-bottleneck /
N3_off (pool_n0E.line_summary_reader, as v1) and gen_summary of anchor n0_E:25 for the $40-offer assert
(§8.11). X = waves/n0_E/design_matrix.csv. The two noise jsons; noise_v3 / noise_seed_E line_summary
(N3_off bar); extracts/base_v3 (floors, base N1_off / N3_off). Never reads random_E; never calls
land_ercot_n0.load / ercot_gp_loader.load; fits no GP; refuses to run if
analysis/ercot_gp/committed_configs.json exists. pool_n0E.py (v1, frozen) is imported for helpers only.

Implementation pins (where §8 leaves a mechanical choice open; fixed in commit (ii), before the read):
- Bar (§8.1): perturbed run values per design are {0 (reference), delta_A, delta_B} (each delta is
  perturbed - reference; the A and B references are md5-equal, asserted); a design whose two deltas are
  NaN (D1 / D2 at the nuclear design) is dropped (nu_pert = 4 for D1 / D2; nu = 20 there).
- Joint bootstrap (§8.2): a fresh default_rng(6262) per id draws, in this order, the (10,000 x 48) row
  indices and then the 10,000 chi-square(nu) variates; the same draws serve IDR and IDR(r_j).
  The 90 % interval is the [5th, 95th] percentile of IDR*/B*.
- Mantel: pool_n0E.mantel (fresh default_rng(6262) per call = the same permutation stream for every id),
  u = the six unit-cube Sobol coordinates u_*.
- Fisher-z (§8.6): se raw sqrt(1.06/45), residual sqrt(1.06/39); "90 % interval" = two-sided.
- Walk order (§8.7): families V, E, X, R, N, D; within a family OUTCOME before ALTERNATE before every
  other role, then pool_definitions priority (None last), then global_order position. The same order
  defines c (later) / p (earlier) for the directed pair labels of non-walk ids.
- §4b: s ranges over the seats taken before c, s != p; Steiger (1980) Z for dependent correlations
  sharing s on Fisher z of the residual Spearmans, n_eff = 42, pooled r-bar covariance term; one-sided
  p = Phi(Z) for H1: rho_res(c, s) < rho_res(p, s).
- HALT (E1 not seatable or suppressed, or E1 without a trade-off partner after the walk): the E seat
  prints HALT FOR PI; the other families are still walked (suppression only by actual seats) and printed.
- N4 floor = 0.01 x 8,760 = 87.6 h (the rule text rounds to 88 h).
- N3_off bar: perturbed source from the noise_v3 line_summary tables, Seed source from the
  noise_seed_E line_summary tables with the anchors read through the n0_E line_summary reader (real run
  only); without an anchor reader (tests) the Seed source is the 4 replicates per design (nu 12, no Seed
  deltas) and is labelled so.
- delta (§8.12): a pair is comparable under S\\k iff one design weakly dominates the other (all <=) on
  S\\k; for a comparable pair the gap is y~_ak - y~_bk taken from the dominating member a (both
  orientations when equal); k outside F (e.g. N1) is allowed. Bootstrap pairs = pairs of distinct
  resampled designs (unique indices of each resample).
- Lens: E1 - 40 D1 per design (column only, pool_lens_v2.csv).

Run (real read, only after the strategy fast-forward):
    cd trial_0826/ercot && /opt/anaconda3/bin/python analysis/pool/pool_n0E_v2.py
Synthetic dry run:  ... pool_n0E_v2.py --synthetic additive --out <scratch dir>
"""

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import subprocess
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ERCOT = os.path.abspath(os.path.join(HERE, "..", ".."))
for _p in (ERCOT, HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import pool_objectives as po  # noqa: E402
import pool_standings as ps  # noqa: E402
import pool_n0E as pn  # noqa: E402  (v1, frozen: helpers only)

WAVE = pn.WAVE
N_ROWS = pn.N_ROWS
PLAN = pn.PLAN
AMEND_TITLE = ("## AMENDMENT 2026-11-24 — E-D1b rule v2 (disclosed post-hoc): role gate, residual-resolvability "
               "guard, confidence-bound thresholds, order-based suppression, component and conflict rules, "
               "materiality floors, one pooled bar, override protocol")
AMEND_SHA256 = "e3712a7f4d8e0542d5421ed13453fd0a722a582fa7b087b6b34d831581ac28be"
NOISE, NOISE_SEED = pn.NOISE, pn.NOISE_SEED
GP_CONFIGS = os.path.join(ERCOT, "analysis", "ercot_gp", "committed_configs.json")
FIGS = os.path.join(po.POOL, "figs", "n0E_v2")
BASE_DIR = os.path.join(po.EXTR, "base_v3", "run_index_1")
OFFER_ANCHOR = "n0_E:25"
V1_CSV = os.path.join(po.POOL, "pool_ed1b_combined.csv")
SEEDBAR_CSV = os.path.join(po.POOL, "pool_ed1b_combined_seedbar.csv")
CITATION = "data_extractors.py get_fixed_costs / get_variable_costs sum thermal units only (Prescient checkout c453890)"

FAMILIES = ("V", "E", "X", "R", "N", "D")
TIER = {"V": "MAY", "E": "MUST", "X": "MAY", "R": "MAY", "N": "MAY", "D": "—"}
E_SEAT = "E1"
GUARDRAILS = ("R1", "R2", "R3", "N3")
PRE_REGISTERED = ("V1", "E1", "N1")
EXPECTED_V2 = ("V1", "E1", "N4")
M_MAX = 4
RESOLVED_LO, ADEQUATE, FLAGGED, FLOOR_BARS = 2.0, 5.0, 3.0, 2.0
MANTEL_ALPHA = 0.01
RHO_RED, RHO_RESID, RHO_CONF = 0.90, 0.50, -0.50
SE_RAW, SE_RESID = float(np.sqrt(1.06 / 45)), float(np.sqrt(1.06 / 39))
Z90 = 1.6448536269514722
STEIGER_N, STEIGER_ALPHA = 42, 0.05
N_BOOT, BOOT_SEED = 10_000, 6262
N_BOOT_DELTA = 2_000
LENS_B = 40.0
N4_FLOOR_H = 0.01 * 8760
NEW_BOTTLENECK_H = 88
BASE_N1OFF, BASE_N3OFF = 30750.0, 61477.25216900001
L252 = "L252"
F_SET = ("V1", "E1", "X1", "N4")
LENS_SENTENCE = ("E1 − 40·D1 is a reporting column only: Δnet ≤ 0 by construction (replacement ≈ $24/MWh < B = $40) "
                 "and it falls monotonically with MW; capex excluded.")
DISCLOSURE = ("This amendment is post hoc and not blind. It was written after the v1 read, the Seed re-grade, "
              "screening_v3 and the N4–V1 residual interval were known. We do not present it as a pre-registered "
              "selection. Every station reports three vectors from the same runs: v1 pre-registered (V1 · E1 · N1), "
              "v2 (V1 · E1 · N4), and v2 with borderline → REDUNDANT (V1 · E1). A claim about the flowgate objective "
              "is stated only as conditional on v2. Rule v2 is pre-registered unchanged for the next dataset, which "
              "is its real test.")

ROLE_EXPECTED = {
    "V1": "OUTCOME", "V2": "PROXY", "V3": "DIAGNOSTIC", "E1": "OUTCOME", "E2": "COMPONENT", "E3": "COMPONENT",
    "E4": "TRANSFER", "E5": "OUTCOME (dead)", "E6": "TRANSFER", "E7": "PROXY", "E8": "DIAGNOSTIC",
    "E9": "DIAGNOSTIC", "X1": "OUTCOME", "R1": "GUARD", "R2": "GUARD", "R3": "GUARD", "R4": "PROXY",
    "R5": "DIAGNOSTIC", "R6": "DIAGNOSTIC", "R7": "DIAGNOSTIC", "R8": "DIAGNOSTIC", "N1": "PROXY",
    "N2": "DIAGNOSTIC", "N3": "GUARD", "N4": "OUTCOME", "N5": "DIAGNOSTIC", "D1": "DIAGNOSTIC",
    "D2": "DIAGNOSTIC", "D3": "check"}
ROLE_RANK = {"OUTCOME": 0, "ALTERNATE": 1}


# --------------------------------------------------------------------------
# pre-registration guards (parametrized by title)
# --------------------------------------------------------------------------
def amendment_block(plan_path=PLAN, title=AMEND_TITLE):
    text = open(plan_path, encoding="utf-8").read()
    assert text.count(title) == 1, f"plan must carry exactly one block titled {title[:40]!r}"
    blk = text[text.index(title):]
    nxt = blk.find("\n## AMENDMENT ", len(title))
    blk = blk if nxt < 0 else blk[:nxt + 1]
    return blk.rstrip("\n") + "\n"


def amendment_sha(plan_path=PLAN, title=AMEND_TITLE):
    return hashlib.sha256(amendment_block(plan_path, title).encode("utf-8")).hexdigest()


def assert_amendment(plan_path=PLAN, title=AMEND_TITLE, expect=AMEND_SHA256):
    h = amendment_sha(plan_path, title)
    assert h == expect, f"amendment block sha256 {h} != pinned {expect}"
    pn.assert_amendment(plan_path)           # the v1 block (2026-11-17) is unchanged
    return h


def assert_no_gp(path=GP_CONFIGS):
    assert not os.path.exists(path), f"REFUSED: {path} exists (rule v2 must precede any GP fit)"


def _git(*args):
    return subprocess.run(["git", "-C", ERCOT, *args], capture_output=True, text=True).stdout.split()


def amendment_commit(plan_path=PLAN, title=AMEND_TITLE):
    out = _git("log", "--format=%h", "-S", title, "--", plan_path)
    return out[-1] if out else "uncommitted"


def script_commits():
    out = _git("log", "--reverse", "--format=%h", "--", os.path.abspath(__file__),
               os.path.join(ERCOT, "tests", "test_pool_n0E_v2.py"))
    return (out[0] + (f" (+ follow-ups {', '.join(out[1:])})" if out[1:] else "")) if out else "uncommitted"


def roles(plan_path=PLAN):
    """Role table parsed from the committed amendment block: id -> role_base / role / reason."""
    blk = amendment_block(plan_path)
    sec = blk[blk.index("**2.2 Role table"):blk.index("**2.3 Rule v2")]
    out = {}
    for line in sec.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) != 3 or cells[0] == "id" or set(cells[0]) <= {"-"}:
            continue
        ids, role, reason = cells
        base = "OUTCOME (dead)" if role.startswith("OUTCOME (dead)") else re.split(r"[ (]", role)[0]
        for i in (x.strip() for x in ids.split(",")):
            out[i] = {"role_base": base, "role": role, "role_reason": reason}
    got = {k: v["role_base"] for k, v in out.items()}
    assert got == ROLE_EXPECTED, f"role table differs: {set(got.items()) ^ set(ROLE_EXPECTED.items())}"
    return out


def seatable_role(role_base):
    return role_base == "OUTCOME"


# --------------------------------------------------------------------------
# the bar (§8.1)
# --------------------------------------------------------------------------
def chi2_factors(nu, level=0.90):
    from scipy.stats import chi2
    a = (1 - level) / 2
    return float(np.sqrt(nu / chi2.ppf(1 - a, nu))), float(np.sqrt(nu / chi2.ppf(a, nu)))


def bar_from_sources(pert_designs, seed_designs, seed_deltas):
    """pert_designs: per-design run values with the reference first; seed_designs: per-design run values;
    seed_deltas: the Seed deltas. Returns the §8.1 bar (two-run scale) from the pooled per-run s_j."""
    pert_designs = [np.asarray(v, float) for v in pert_designs if len(v) >= 2]
    seed_designs = [np.asarray(v, float) for v in seed_designs if len(v) >= 2]
    nu_p = sum(len(v) - 1 for v in pert_designs)
    nu_s = sum(len(v) - 1 for v in seed_designs)
    s2_p = sum(float(((v - v.mean()) ** 2).sum()) for v in pert_designs) / nu_p if nu_p else np.nan
    s2_s = float(np.mean([np.var(v, ddof=1) for v in seed_designs])) if nu_s else np.nan
    nu = nu_p + nu_s
    s = float(np.sqrt(((nu_p * s2_p) if nu_p else 0.0) / nu + ((nu_s * s2_s) if nu_s else 0.0) / nu))
    md = [float(np.abs(v - v[0]).max()) for v in pert_designs]
    if len(seed_deltas):
        md.append(float(np.max(np.abs(seed_deltas))))
    mx = max(md) if md else 0.0
    flo, fhi = chi2_factors(nu)
    k = 3.0 * np.sqrt(2.0)
    return {"s_pert": float(np.sqrt(s2_p)) if nu_p else np.nan, "nu_pert": nu_p,
            "s_seed": float(np.sqrt(s2_s)) if nu_s else np.nan, "nu_seed": nu_s, "s_j": s, "nu": nu,
            "chi_lo": flo, "chi_hi": fhi, "max_abs_delta": mx, "B_j": max(k * s, mx),
            "B_lo": max(k * flo * s, mx), "B_up": max(k * fhi * s, mx),
            "B_binding_term": "3*sqrt2*s_j" if k * s >= mx else "max|delta|"}


def _by_design(j):
    by = {}
    for d in j["perturbed_deltas"]:
        if d["design_no"] != pn.STRUCTURAL_ZERO_DESIGN:
            by.setdefault(d["design_no"], []).append(d)
    runs = {r["key"]: r for r in j["runs"]}
    for dno, ds in by.items():
        assert len(ds) == 2, dno
        assert runs[ds[0]["ref_key"]]["overall_md5"] == runs[ds[1]["ref_key"]]["overall_md5"], (dno, "A/B refs differ")
    return by


def _pert_designs(j, getter):
    """Per kept design: [0, delta_A, delta_B] (design-2 (site 206) structural-zero pair excluded)."""
    out = []
    for dno, ds in sorted(_by_design(j).items()):
        v = [getter(d) for d in ds]
        if all(x is None or not np.isfinite(x) for x in v):
            continue
        assert all(x is not None and np.isfinite(x) for x in v), (dno, v)
        out.append(np.array([0.0] + [float(x) for x in v]))
    return out


def assert_structural_zero(j, data_dir=po.DATA):
    runs = {r["key"]: r for r in j["runs"]}
    excl = []
    for d in j["perturbed_deltas"]:
        if d["design_no"] != pn.STRUCTURAL_ZERO_DESIGN:
            continue
        a, b = runs[d["key"]], runs[d["ref_key"]]
        assert a["site"] == b["site"] == pn.STRUCTURAL_ZERO_SITE
        assert a["overall_md5"] == b["overall_md5"], (d["key"], "outputs differ: not a structural zero")
        ma = pn.pem_slice_md5(a["site"], d["pem_mw"], data_dir)
        assert ma == pn.pem_slice_md5(b["site"], d["pem_mw_ref"], data_dir), (d["key"], "effective input differs")
        excl.append({"key": d["key"], "ref_key": d["ref_key"], "input_md5": ma, "overall_md5": a["overall_md5"]})
    assert len(excl) == 2
    return excl


def pooled_bars(noise=NOISE, noise_seed=NOISE_SEED, data_dir=po.DATA, ids=None):
    ids = list(ids or po.CAND_IDS)
    j = json.load(open(noise))
    s = json.load(open(noise_seed))
    excl = assert_structural_zero(j, data_dir)
    rows = []
    for c in ids:
        pert = _pert_designs(j, lambda d, c=c: d.get(c))
        sc = s["per_candidate"][c]
        seed = [np.asarray(y, float) for y in sc["y"]]
        assert len(seed) == 4 and all(len(y) == 5 for y in seed), c
        dseed = np.array(sc["delta_seed"], float)
        assert np.allclose(dseed, np.concatenate([y[1:] - y[0] for y in seed])), c
        b = bar_from_sources(pert, seed, dseed)
        assert abs(b["s_seed"] - float(sc["sigma_c"])) <= 1e-9 * max(1.0, b["s_seed"]), c
        bar = j["per_candidate"][c].get("bar")
        b.update({"id": c, "B_pert_v1": float(bar["B"]) if isinstance(bar, dict) and bar.get("B") is not None else np.nan,
                  "B_seed_63": float(s["bars"][c]["B_seed"])})
        b["sources_ratio"] = b["s_seed"] / b["s_pert"] if b["s_pert"] and b["s_pert"] > 0 else np.nan
        sp, ss = b["s_pert"], b["s_seed"]
        b["sources_disagree_2x"] = bool((sp == 0) != (ss == 0) if (sp == 0 or ss == 0)
                                        else not 0.5 <= ss / sp <= 2.0)
        b["A3_63"] = s["A3"]["per_candidate"].get(c, "")
        rows.append(b)
    out = pd.DataFrame(rows).set_index("id")
    out.attrs["excluded"] = excl
    return out


def n1off_bar(noise=NOISE, noise_seed=NOISE_SEED):
    """§8.8 (a): B_N1off from the per-run json values (N1 - N4 per run; linear in the deltas)."""
    j, s = json.load(open(noise)), json.load(open(noise_seed))
    pert = _pert_designs(j, lambda d: (d["N1"] - d["N4"]) if d.get("N1") is not None else None)
    y = [np.asarray(a, float) - np.asarray(b, float)
         for a, b in zip(s["per_candidate"]["N1"]["y"], s["per_candidate"]["N4"]["y"])]
    b = bar_from_sources(pert, y, np.concatenate([v[1:] - v[0] for v in y]))
    b["seed_runs"] = {k: float(v) for des, yy in zip(s["designs"], y) for k, v in zip(des["keys"], yy)}
    return b


def _offsum(ls, col, data_dir=po.DATA):
    pl = set(po.pocket_lines(data_dir, 120))
    return float(ls.loc[~ls["Line"].astype(str).isin(pl), col].astype(float).sum())


def _ls(key):
    return pd.read_csv(os.path.join(po.run_dir(key), "line_summary.csv"))


def n3off_bar(noise=NOISE, noise_seed=NOISE_SEED, anchor_reader=None, data_dir=po.DATA):
    """§8.8 (c): B_N3off from line_summary tables (noise_v3; noise_seed_E with anchors iff anchor_reader)."""
    j, s = json.load(open(noise)), json.load(open(noise_seed))
    off = lambda key: _offsum(_ls(key), "sum_violation", data_dir)  # noqa: E731
    pert = []
    for dno, ds in sorted(_by_design(j).items()):
        ref = off(ds[0]["ref_key"])
        pert.append(np.array([0.0] + [off(d["key"]) - ref for d in ds]))
    seed, deltas = [], []
    for des in s["designs"]:
        reps = np.array([off(k) for k in des["keys"][1:]])
        if anchor_reader is not None:
            a = _offsum(anchor_reader(des["keys"][0]), "sum_violation", data_dir)
            seed.append(np.concatenate([[a], reps]))
            deltas.extend(list(reps - a))
        else:
            seed.append(reps)
    b = bar_from_sources(pert, seed, np.array(deltas))
    b["seed_source"] = "anchor + 4 Seeds (nu 16)" if anchor_reader is not None else "4 Seeds only (nu 12; no anchor read)"
    return b


# --------------------------------------------------------------------------
# base_v3 floors (§8.5), offer exclusion (§8.11)
# --------------------------------------------------------------------------
def base_row(base_dir=BASE_DIR):
    return po.pool_row("base_v3:1", drow=po.BASE_DROW, d=base_dir)


def floors(base):
    f = {"V1": 0.01 * float(base["V1"]), "E1": 0.001 * float(base["E1"]), "X1": 0.001 * float(base["X1"]),
         "N4": N4_FLOOR_H}
    assert abs(f["V1"] - 58287) < 1 and abs(f["E1"] - 8.06e6) < 0.01e6 and abs(f["X1"] - 194521) < 1, f
    return f, {"R4 (informational; role gate excludes it)": 0.01 * float(base["R4"])}


def assert_offer_excluded(dirs, tol=1.0):
    """E1 == overall Total costs == Σ non-renewable Unit Cost (to $1); is_pem Unit Cost NaN/0."""
    out = []
    for key, d in dirs:
        o = pd.read_csv(os.path.join(d, "overall.csv")).iloc[0]
        g = pd.read_csv(os.path.join(d, "gen_summary.csv"))
        pem = g["is_pem"].astype("boolean").fillna(False).astype(bool)
        th = ~g["unit_type"].isin(["WIND", "PV"]) & ~pem
        s_th = float(g.loc[th, "Unit Cost"].sum())
        pem_cost = float(g.loc[pem, "Unit Cost"].fillna(0.0).abs().sum())
        E1 = float(o["Total costs"])
        assert abs(E1 - s_th) <= tol and pem_cost == 0.0, (key, E1, s_th, pem_cost)
        out.append({"key": key, "E1": E1, "sum_non_renewable_unit_cost": s_th, "n_pem_twins": int(pem.sum())})
    return out


# --------------------------------------------------------------------------
# per-id statistics (§8.2, §8.4)
# --------------------------------------------------------------------------
def _idr(y, axis=None):
    q = np.quantile(np.asarray(y, float), [0.10, 0.90], axis=axis)
    return q[1] - q[0]


def joint_bootstrap(y, r, s, nu, mx, n_boot=N_BOOT, seed=BOOT_SEED):
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(y), (n_boot, len(y)))
    chi = rng.chisquare(nu, n_boot)
    Bs = np.maximum(3.0 * np.sqrt(2.0) * s * np.sqrt(nu / chi), mx)
    a = _idr(np.asarray(y, float)[idx], axis=1) / Bs
    b = _idr(np.asarray(r, float)[idx], axis=1) / Bs
    return (float(np.quantile(a, 0.05)), float(np.quantile(a, 0.95)),
            float(np.quantile(b, 0.05)), float(np.quantile(b, 0.95)))


STAT_COLS = ("IDR", "resid_IDR", "IDR_over_B", "IDR_over_B_lo90", "IDR_over_B_hi90", "IDR_over_B_up_analytic",
             "resid_IDR_over_B", "resid_IDR_over_B_lo90", "resid_IDR_over_B_hi90", "mantel_p_raw", "mantel_p_resid",
             "eta2_T", "iso_loo_R2", "comp_rho")


def per_id(wide, X, B, ids, role, fl, stat_ids=None):
    U = X[X.attrs["u_cols"]].to_numpy(dtype=float)
    T = X["T"].to_numpy(dtype=float)
    rs = X["s"].to_numpy(float) - pn.bin_pchip(T, X["s"].to_numpy(float))
    rows = []
    for c in ids:
        y = wide[c].to_numpy(dtype=float)
        rb = role[c]["role_base"]
        rec = {"id": c, "role": role[c]["role"], "role_base": rb, "seatable_role": seatable_role(rb),
               "floor_M": fl.get(c, np.nan), "computed": False}
        b = float(B.loc[c, "B_j"])
        if (stat_ids is not None and c not in stat_ids) or np.ptp(y) == 0:
            rows.append(rec)
            continue
        r = y - pn.bin_pchip(T, y)
        _, p_raw = pn.mantel(y, U)
        _, p_res = pn.mantel(r, U) if np.ptp(r) > 0 else (np.nan, np.nan)
        eta, _ = pn.size_share(T, y)
        rec.update({"computed": True, "IDR": float(_idr(y)), "resid_IDR": float(_idr(r)), "eta2_T": eta,
                    "iso_loo_R2": pn.iso_loo_r2(T, y), "comp_rho": pn._spearman(r, rs),
                    "mantel_p_raw": p_raw, "mantel_p_resid": p_res})
        if b > 0:
            lo, hi, rlo, rhi = joint_bootstrap(y, r, float(B.loc[c, "s_j"]), int(B.loc[c, "nu"]),
                                               float(B.loc[c, "max_abs_delta"]))
            rec.update({"IDR_over_B": rec["IDR"] / b, "IDR_over_B_lo90": lo, "IDR_over_B_hi90": hi,
                        "IDR_over_B_up_analytic": rec["IDR"] / float(B.loc[c, "B_up"]),
                        "resid_IDR_over_B": rec["resid_IDR"] / b, "resid_IDR_over_B_lo90": rlo,
                        "resid_IDR_over_B_hi90": rhi})
        rows.append(rec)
    t = pd.DataFrame(rows).set_index("id")
    for k in STAT_COLS:
        if k not in t.columns:
            t[k] = np.nan
    return t


def classify(t, B):
    """§8.4 definitions (point IDR against the floors)."""
    t = t.copy()
    graded = (B.loc[t.index, "B_j"] > 0) & t["computed"].astype(bool)
    M = t["floor_M"].astype(float).fillna(0.0)
    t["RESOLVED"] = graded & (t["IDR_over_B_lo90"] >= RESOLVED_LO) & (t["mantel_p_raw"] <= MANTEL_ALPHA)
    t["COMP_RESOLVABLE"] = (graded & (t["mantel_p_resid"] <= MANTEL_ALPHA)
                            & (t["resid_IDR_over_B_lo90"] >= RESOLVED_LO) & (t["resid_IDR"] >= M))
    t["floor_need"] = np.maximum(FLOOR_BARS * B.loc[t.index, "B_j"].to_numpy(float), M.to_numpy(float))
    t["floor_pass"] = graded & (t["IDR"] >= t["floor_need"])
    t["sufficiency"] = np.where(~graded, "NOT GRADED", np.where(t["IDR_over_B"] >= ADEQUATE, "ADEQUATE",
                                np.where(t["IDR_over_B"] >= FLAGGED, "FLAGGED", "NOT SEATABLE (< 3)")))
    t["seatable_pre"] = (t["seatable_role"] & t["RESOLVED"] & t["floor_pass"]
                         & t["sufficiency"].isin(["ADEQUATE", "FLAGGED"]))
    return t


# --------------------------------------------------------------------------
# order, pairs (§8.6, §8.7)
# --------------------------------------------------------------------------
def walk_order(ids, defs, role):
    go = defs["global_order"]

    def key(c):
        cd = defs["candidates"][c]
        pr = cd.get("priority")
        return (FAMILIES.index(cd["family"]), ROLE_RANK.get(role[c]["role_base"], 2),
                pr if pr is not None else 99, go.index(c))
    return sorted(ids, key=key)


def fisher90(r, se):
    if not np.isfinite(r) or abs(r) >= 1:
        return (r, r)
    z = np.arctanh(r)
    return (float(np.tanh(z - Z90 * se)), float(np.tanh(z + Z90 * se)))


def steiger(r_cs, r_ps, r_cp, n=STEIGER_N):
    """Steiger (1980) Z for H1: rho(c, s) < rho(p, s) (dependent, sharing s); one-sided p = Phi(Z)."""
    from scipy.stats import norm
    rb = (r_cs + r_ps) / 2.0
    psi = r_cp * (1 - 2 * rb ** 2) - 0.5 * rb ** 2 * (1 - 2 * rb ** 2 - r_cp ** 2)
    cbar = psi / (1 - rb ** 2) ** 2
    Z = (np.arctanh(r_cs) - np.arctanh(r_ps)) * np.sqrt(n - 3) / np.sqrt(2 - 2 * cbar)
    return float(Z), float(norm.cdf(Z))


def pair_table(raw, resid, O, R, order, defs, comp):
    from scipy.stats import kendalltau
    ids = [c for c in order if c in raw.index]
    rows = []
    for i, p in enumerate(ids):
        for c in ids[i + 1:]:                       # p earlier, c later
            r, e = float(raw.loc[c, p]), float(resid.loc[c, p])
            both = all(defs["candidates"][x]["dir"] in ("min", "max") for x in (c, p))
            r90, e90 = fisher90(r, SE_RAW), fisher90(e, SE_RESID)
            tr = float(kendalltau(O[c], O[p], variant="b").statistic)
            te = float(kendalltau(R[c], R[p], variant="b").statistic)
            cc, cp = bool(comp.get(c, False)), bool(comp.get(p, False))
            raw_ge = bool(np.isfinite(r) and (r >= RHO_RED or r90[0] <= RHO_RED <= r90[1]))
            escape = cc and (not cp or (np.isfinite(e) and e90[1] < RHO_RESID))
            border = bool(raw_ge and not escape and cc and np.isfinite(e) and e90[0] <= RHO_RESID <= e90[1])
            rows.append({"pair": f"{c}|{p}", "c_later": c, "p_earlier": p, "both_directed": both,
                         "rho_raw": r, "rho_raw_lo90": r90[0], "rho_raw_hi90": r90[1],
                         "rho_resid": e, "rho_resid_lo90": e90[0], "rho_resid_hi90": e90[1],
                         "kendall_tau_b_raw": tr, "kendall_tau_b_resid": te,
                         "c_comp_resolvable": cc, "p_comp_resolvable": cp, "raw_ge_090": raw_ge,
                         "ESCAPE": bool(both and raw_ge and escape),
                         "SIZE_CO_MONOTONE": bool(both and raw_ge and escape),
                         "BORDERLINE_PAIR": bool(both and border),
                         "REDUNDANT_given_p": bool(both and raw_ge and not escape),
                         "TRADE_OFF_size": bool(both and np.isfinite(r) and r <= RHO_CONF),
                         "TRADE_OFF_comp": bool(both and cc and cp and np.isfinite(e) and e <= RHO_CONF)})
    pt = pd.DataFrame(rows)
    pt["TRADE_OFF"] = pt["TRADE_OFF_size"] | pt["TRADE_OFF_comp"]
    return pt


class Pairs:
    def __init__(self, pt):
        self.pt = pt.set_index(["c_later", "p_earlier"])

    def get(self, a, b):
        return self.pt.loc[(a, b)] if (a, b) in self.pt.index else self.pt.loc[(b, a)]

    def trade_off(self, a, b):
        return bool(self.get(a, b)["TRADE_OFF"])


# --------------------------------------------------------------------------
# the walk (§8.6 §4b, §8.7)
# --------------------------------------------------------------------------
def resolve_4b(c, p, seated, P):
    """§4b: a BORDERLINE-PAIR (c, p) is NOT REDUNDANT iff some earlier seat s != p gives a CI-confirmed
    composition trade-off with c that is significantly stronger than p's (Steiger)."""
    tried = []
    for s in seated:
        if s == p:
            continue
        rcs = float(P.get(c, s)["rho_resid"])
        up = fisher90(rcs, SE_RESID)[1]
        rps, rcp = float(P.get(p, s)["rho_resid"]), float(P.get(c, p)["rho_resid"])
        Z, pv = steiger(rcs, rps, rcp)
        ok = bool(up <= RHO_CONF and pv <= STEIGER_ALPHA)
        tried.append({"s": s, "rho_res_cs": rcs, "rho_res_cs_up90": up, "rho_res_ps": rps, "rho_res_cp": rcp,
                      "steiger_Z": Z, "steiger_p": pv, "resolves": ok})
        if ok:
            return True, tried
    return False, tried


def walk(t, P, order, use_4b=True):
    seats, log, sup, b4 = {}, {}, {}, {}
    seated, halt = [], None
    fam = {c: c[0] for c in order}
    for c in [c for c in order if bool(t.loc[c, "seatable_role"])]:
        f = fam[c]
        if not bool(t.loc[c, "seatable_pre"]):
            log[c] = _not_seatable_reason(t, c)
            if c == E_SEAT:
                halt = f"E1 not seatable: {log[c]}"
            continue
        red_by = None
        for p in seated:
            row = P.get(c, p)
            if not bool(row["REDUNDANT_given_p"]):
                continue
            if bool(row["BORDERLINE_PAIR"]) and use_4b:
                ok, tried = resolve_4b(c, p, seated, P)
                b4[(c, p)] = tried
                if ok:
                    continue
            red_by = p
            break
        if red_by is not None:
            sup[c] = red_by
            log[c] = f"suppressed: REDUNDANT given seated {red_by}" + (
                " (BORDERLINE-PAIR, §4b not met)" if bool(P.get(c, red_by)["BORDERLINE_PAIR"]) else "")
            if c == E_SEAT:
                halt = f"E1 suppressed by {red_by}"
            continue
        if f in seats:
            log[c] = f"family {f} seat held by {seats[f]}; a second seat only by PI decision"
            continue
        seats[f] = c
        seated.append(c)
        log[c] = "SEATED"
    demoted = [s for s in seats.values() if not any(P.trade_off(s, o) for o in seats.values() if o != s)]
    for s in demoted:                                       # one pass, simultaneous, no iteration
        if s == E_SEAT:
            halt = "E1 has no TRADE-OFF partner among the seats"
            log[s] = "no TRADE-OFF partner -> HALT"
        else:
            log[s] = "DEMOTED -> DIAGNOSTIC (no TRADE-OFF partner among the seats); family EMPTY"
        del seats[fam[s]]
    out = []
    for f in FAMILIES[:5]:
        if f == "E" and halt:
            out.append({"family": f, "seat": "HALT FOR PI", "note": halt})
        elif f in seats:
            fl = " (FLAGGED)" if t.loc[seats[f], "sufficiency"] == "FLAGGED" else ""
            out.append({"family": f, "seat": seats[f], "note": "SEATED" + fl})
        else:
            dem = [s for s in demoted if fam[s] == f]
            out.append({"family": f, "seat": "EMPTY", "note": f"{dem[0]} demoted; never back-filled" if dem
                        else ("not at stake in this box" if TIER[f] == "MAY" else "")})
    M = None if halt else sum(1 for s in out if s["note"].startswith("SEATED"))
    return {"seats": out, "M": M, "halt": halt, "log": log, "suppressed": sup, "demoted": demoted, "b4": b4}


def _not_seatable_reason(t, c):
    r = t.loc[c]
    if not r["seatable_role"]:
        return f"role {r['role_base']} never seated"
    if not bool(r["computed"]):
        return "constant / not computed"
    bits = []
    if not r["RESOLVED"]:
        bits.append(f"not RESOLVED (joint lower-90 IDR/B {pn._f(r['IDR_over_B_lo90'])}, raw Mantel p "
                    f"{pn._f(r['mantel_p_raw'])})")
    if not r["floor_pass"]:
        bits.append(f"materiality: IDR {r['IDR']:.4g} < max(2 B, M) = {r['floor_need']:.4g}")
    if r["sufficiency"] not in ("ADEQUATE", "FLAGGED"):
        bits.append(str(r["sufficiency"]))
    return "; ".join(bits) or "seatable"


def seat_line(res):
    return " · ".join(f"{s['family']}: {s['seat']}" for s in res["seats"])


def seat_vector(res):
    return tuple(s["seat"] for s in res["seats"] if s["note"].startswith("SEATED"))


# --------------------------------------------------------------------------
# δ-error (§8.12)
# --------------------------------------------------------------------------
def _delta_k(Yt, S, k):
    """Yt: bar-unit oriented values. Returns (δ_k, π_k, n_comparable) for dropping k from S."""
    rest = [c for c in S if c != k]
    V = Yt[rest].to_numpy(float) if rest else np.zeros((len(Yt), 0))
    yk = Yt[k].to_numpy(float)
    I, K = np.triu_indices(len(Yt), 1)
    a_le = (V[I] <= V[K]).all(axis=1)
    b_le = (V[K] <= V[I]).all(axis=1)
    gap = np.maximum(np.where(a_le, yk[I] - yk[K], -np.inf), np.where(b_le, yk[K] - yk[I], -np.inf))
    comp = a_le | b_le
    if not comp.any():
        return 0.0, 0.0, 0
    return float(max(0.0, gap[comp].max())), float(np.mean(gap[comp] > 2.0)), int(comp.sum())


def delta_report(Yt, S, n_boot=N_BOOT_DELTA, seed=BOOT_SEED):
    pts = {k: _delta_k(Yt, S, k) for k in S}
    rng = np.random.default_rng(seed)
    bs = {k: ([], []) for k in S}
    for _ in range(n_boot):
        sub = Yt.iloc[np.unique(rng.integers(0, len(Yt), len(Yt)))]
        for k in S:
            d, p, _ = _delta_k(sub, S, k)
            bs[k][0].append(d)
            bs[k][1].append(p)
    return {k: {"delta": pts[k][0], "delta_p90": float(np.quantile(bs[k][0], 0.90)), "pi": pts[k][1],
                "pi_lo": float(np.quantile(bs[k][1], 0.025)), "pi_hi": float(np.quantile(bs[k][1], 0.975)),
                "n_comparable": pts[k][2]} for k in S}


# --------------------------------------------------------------------------
# N1_off guardrail (§8.8)
# --------------------------------------------------------------------------
def n1off_guard(wide, reader, base_dir=BASE_DIR, data_dir=po.DATA, B_n1off=None, B_n3off=None):
    pl = set(po.pocket_lines(data_dir, 120))
    base = pd.read_csv(os.path.join(base_dir, "line_summary.csv"))
    base["Line"] = base["Line"].astype(str)
    bo = base[~base["Line"].isin(pl)].set_index("Line")
    zero = set(bo.index[bo["hours_ge_99pct"] == 0])
    off = pn.n1_off(wide, reader)
    dN1off = off.to_numpy(float) - BASE_N1OFF
    dN4 = wide["N4"].to_numpy(float) - float(base.loc[base["Line"] == L252, "hours_ge_99pct"].iloc[0])
    with np.errstate(divide="ignore", invalid="ignore"):
        leak = np.where(dN4 < 0, dN1off / (-dN4), np.nan)
    new_b, n3, dh = [], [], []
    for key in wide["key"]:
        ls = reader(key)
        ls = ls.assign(Line=ls["Line"].astype(str))
        lo = ls[~ls["Line"].isin(pl)].set_index("Line")
        new_b.append(";".join(ln for ln in lo.index if ln in zero and float(lo.loc[ln, "hours_ge_99pct"]) >= NEW_BOTTLENECK_H))
        n3.append(float(lo["sum_violation"].sum()) if "sum_violation" in lo.columns else np.nan)
        dh.append(lo["hours_ge_99pct"].astype(float) - bo["hours_ge_99pct"].reindex(lo.index).fillna(0.0))
    D = pd.concat(dh, axis=1).fillna(0.0)
    top = D.max(axis=1).sort_values(ascending=False).head(3)
    g = pd.DataFrame({"key": wide["key"].to_numpy(), "N1_off": off.to_numpy(float), "dN1_off": dN1off, "dN4": dN4,
                      "leakage": leak, "new_bottleneck": new_b, "N3_off": n3})
    flags = {"a_dN1off_ge_2B": bool(B_n1off is not None and (g["dN1_off"] >= 2 * B_n1off).any()),
             "b_new_bottleneck": bool((g["new_bottleneck"] != "").any()),
             "c_N3off_ge_base_plus_2B": bool(B_n3off is not None and (g["N3_off"] >= BASE_N3OFF + 2 * B_n3off).any())}
    return g, flags, [(ln, float(v), float(D.loc[ln].median())) for ln, v in top.items()]


# --------------------------------------------------------------------------
# figures (assert-before-draw; bold labels and ticks)
# --------------------------------------------------------------------------
def plot_idr_ci(t, path):
    plt = ps._rc()
    import matplotlib.ticker as mt
    s = t[np.isfinite(t["IDR_over_B"].astype(float))].sort_values("IDR_over_B")
    v, lo, hi = (s[k].to_numpy(float) for k in ("IDR_over_B", "IDR_over_B_lo90", "IDR_over_B_hi90"))
    assert np.all(np.isfinite(lo)) and np.all(lo <= hi)
    fig, ax = plt.subplots(figsize=(14, max(8, 0.45 * len(s) + 2)))
    y = np.arange(len(s))
    vv = np.maximum(v, 1e-3)
    ax.errorbar(vv, y, xerr=[np.maximum(vv - np.maximum(lo, 1e-4), 0), np.maximum(np.maximum(hi, 1e-3) - vv, 0)],
                fmt="none", ecolor="k", lw=2, capsize=4)
    ax.scatter(vv, y, c=["tab:blue" if bool(x) else "0.6" for x in s["seatable_role"]], s=90, zorder=3)
    for x, ls in ((RESOLVED_LO, "--"), (FLAGGED, ":"), (ADEQUATE, "-.")):
        ax.axvline(x, color="red", ls=ls, lw=2)
    ax.set_xscale("log")
    tk = [q for q in (0.1, 0.3, 1, 2, 3, 5, 10, 30, 100, 300, 1000) if q <= max(10.0, 1.5 * float(np.nanmax(hi)))]
    ax.xaxis.set_major_locator(mt.FixedLocator(tk))
    ax.xaxis.set_minor_locator(mt.NullLocator())
    ax.set_xticklabels([f"{q:g}" for q in tk])
    ax.set_yticks(y)
    ax.set_yticklabels([f"{c} ({s.loc[c, 'role_base']})" for c in s.index])
    ax.set_xlabel("IDR / B_j with joint-bootstrap 90 % interval (lines 2, 3, 5)", fontsize=18, fontweight="bold")
    ax.set_ylabel("candidate (role)", fontsize=18, fontweight="bold")
    ax.set_title("n0_E rule v2: IDR / B_j (blue = OUTCOME role)", fontsize=18, fontweight="bold")
    ax.tick_params(labelsize=16)
    for lab in ax.get_xticklabels() + ax.get_yticklabels():
        lab.set_fontweight("bold")
    fig.savefig(path, dpi=100, bbox_inches="tight")
    plt.close(fig)


def plot_rho5(P, ids, path):
    plt = ps._rc()
    fig, axes = plt.subplots(1, 2, figsize=(26, 11))
    im = None
    for ax, k, ttl in ((axes[0], "rho_raw", "raw oriented Spearman"), (axes[1], "rho_resid", "T-residual oriented Spearman")):
        M = np.eye(len(ids))
        txt = [["1"] * len(ids) for _ in ids]
        for i, a in enumerate(ids):
            for j, b in enumerate(ids):
                if i != j:
                    r = P.get(a, b)
                    M[i, j] = r[k]
                    txt[i][j] = f"{r[k]:.2f}\n[{r[k + '_lo90']:.2f}, {r[k + '_hi90']:.2f}]"
        assert np.allclose(M, M.T)
        im = ax.imshow(M, cmap="RdBu_r", vmin=-1, vmax=1)
        for i in range(len(ids)):
            for j in range(len(ids)):
                ax.text(j, i, txt[i][j], ha="center", va="center", fontsize=11, fontweight="bold")
        ax.set_xticks(range(len(ids)))
        ax.set_yticks(range(len(ids)))
        ax.set_xticklabels(ids)
        ax.set_yticklabels(ids)
        ax.tick_params(labelsize=16)
        for lab in ax.get_xticklabels() + ax.get_yticklabels():
            lab.set_fontweight("bold")
        ax.set_title(f"{ttl} (90 % Fisher-z interval), n = 48", fontsize=16, fontweight="bold")
        ax.set_xlabel("candidate", fontsize=16, fontweight="bold")
        ax.set_ylabel("candidate", fontsize=16, fontweight="bold")
    fig.colorbar(im, ax=axes, shrink=0.8)
    fig.savefig(path, dpi=100, bbox_inches="tight")
    plt.close(fig)


# --------------------------------------------------------------------------
# writer
# --------------------------------------------------------------------------
def _v1_seats(path):
    if not os.path.isfile(path):
        return "n/a"
    c = pd.read_csv(path)
    sel = c["status"] == "OBJECTIVE"
    fam = dict(zip(c.loc[sel, "family"], c.loc[sel, "id"]))
    return " · ".join(f"{f}: {fam.get(f, 'EMPTY')}" for f in FAMILIES[:5])


def write_md(path, o):
    info, B, t, pt, res = o["info"], o["B"], o["tab"], o["pairs"], o["res"]
    L = ["# POOL_N0E_STANDINGS_v2 — E-D1b rule v2 re-walk on n0_E (prompt 65 v1.1; disclosed post-hoc amendment)", "",
         f"**{DISCLOSURE}**", "",
         f"Read date (UTC): {info['read_utc']}. Rules: plan AMENDMENT 2026-11-24 (commit (i) {info['sha_i']}, block "
         f"sha256 `{info['amend_sha256']}`); script + tests commit (ii) {info['sha_ii']}; git HEAD at the read "
         f"{info['git_head']}. `waves/n0_E/design_matrix.csv` sha256 `{info['design_sha256']}`.", "",
         ("**SYNTHETIC DRY RUN — planted Y, not n0_E data.**\n\n" if info["synthetic"] else "")
         + "Input: 48 n0_E grading rows (`pool_standings.build_wave(\"n0_E\")`); no GP fitted "
         "(`analysis/ercot_gp/committed_configs.json` absent, asserted); random_E not read; holdout exposure 0 / 24.", "",
         "## 1. Ledger", "",
         "Everything in AMENDMENT 2026-11-17's ledger plus the v1 Part B read (d706199), the Seed-bar re-grade "
         "(baf77c3), screening_v3 (e58f4bd), location_contrast_E (4b7bf85), the family-free strength-first trial, the "
         "three 11-24 reviewer reports and the §8.15 additions (anchor spreads from noise_seed_E Seeds 1–4; residual "
         "IDR/B estimated from printed η²_T and IDR). Implementation pins: module docstring of `pool_n0E_v2.py`.", "",
         "## 2. Bars (§8.1: two-run scale, pooled ν; design-2 (site 206) structural-zero pair excluded) and floors", ""]
    bc = ["id", "s_pert", "nu_pert", "s_seed", "nu_seed", "sources_ratio", "sources_disagree_2x", "A3_63", "s_j", "nu",
          "max_abs_delta", "B_j", "B_lo", "B_up", "B_binding_term", "B_pert_v1", "B_seed_63"]
    L += [pn._md_table(B.reset_index(), bc), "",
          "Floors (§8.5; disclosed: set after the relative responses were seen; point IDR compared): "
          + "; ".join(f"{k} {v:.6g}" for k, v in info["floors"].items())
          + "; " + "; ".join(f"{k} {v:.6g}" for k, v in info["floors_info"].items())
          + f". E1 median pair gap bound G_a + G_b = {info['G_pair_median']:.4g} (evidence only, never a floor; "
          f"E1 IDR / gap bound = {info['E1_over_gap']:.2f}).", "",
          "$40-offer exclusion (§8.11): " + "; ".join(
              f"{x['key']} E1 {x['E1']:.6g} = Σ non-renewable Unit Cost {x['sum_non_renewable_unit_cost']:.6g} "
              f"(PEM twins {x['n_pem_twins']}, Unit Cost NaN/0)" for x in info["offer"]) + f". Source: {CITATION}.", "",
          "## 3. Per measure (item 10; §8.4)", ""]
    pc = ["id", "role", "tier", "B_j", "IDR", "IDR_over_B", "IDR_over_B_lo90", "IDR_over_B_hi90", "resid_IDR_over_B",
          "resid_IDR_over_B_lo90", "resid_IDR_over_B_hi90", "eta2_T", "mantel_p_raw", "mantel_p_resid", "floor_M",
          "floor_pass", "RESOLVED", "COMP_RESOLVABLE", "sufficiency", "trade_offs", "status", "why"]
    L += [pn._md_table(t.reset_index(), pc), "", "## 4. Pairs (directed; c later, p earlier in walk order; §8.6)", ""]
    sel = pt[pt["both_directed"] & (pt["REDUNDANT_given_p"] | pt["SIZE_CO_MONOTONE"] | pt["BORDERLINE_PAIR"]
                                    | pt["TRADE_OFF"])]
    qc = ["pair", "rho_raw", "rho_raw_lo90", "rho_raw_hi90", "rho_resid", "rho_resid_lo90", "rho_resid_hi90",
          "kendall_tau_b_raw", "kendall_tau_b_resid", "c_comp_resolvable", "p_comp_resolvable", "ESCAPE",
          "BORDERLINE_PAIR", "REDUNDANT_given_p", "TRADE_OFF_size", "TRADE_OFF_comp"]
    L += [pn._md_table(sel, qc) if len(sel) else "none", "", "Key pairs (90 % intervals):", ""]
    for a, b in (("N4", "V1"), ("N1", "V1"), ("N4", "N1"), ("N4", "E1"), ("X1", "E1"), ("E1", "V1")):
        try:
            r = o["P"].get(a, b)
        except KeyError:
            continue
        L.append(f"- {r['pair']}: raw {r['rho_raw']:.3f} [{r['rho_raw_lo90']:.3f}, {r['rho_raw_hi90']:.3f}]; residual "
                 f"{r['rho_resid']:.3f} [{r['rho_resid_lo90']:.3f}, {r['rho_resid_hi90']:.3f}]; τ_b raw "
                 f"{r['kendall_tau_b_raw']:.3f} / resid {r['kendall_tau_b_resid']:.3f}; ESCAPE {r['ESCAPE']}; "
                 f"BORDERLINE-PAIR {r['BORDERLINE_PAIR']}; REDUNDANT given p {r['REDUNDANT_given_p']}; TRADE-OFF {r['TRADE_OFF']}")
    L += ["", "§4b evaluations:", ""]
    for (c, p), tried in res["b4"].items():
        for x in tried:
            L.append(f"- ({c}, {p}) via s = {x['s']}: ρ_res(c,s) {x['rho_res_cs']:.3f} (upper-90 {x['rho_res_cs_up90']:.3f}), "
                     f"ρ_res(p,s) {x['rho_res_ps']:.3f}, ρ_res(c,p) {x['rho_res_cp']:.3f}; Steiger Z {x['steiger_Z']:.3f}, "
                     f"one-sided p {x['steiger_p']:.4g} → {'NOT REDUNDANT' if x['resolves'] else 'not resolved'}")
    if not res["b4"]:
        L.append("- none evaluated")
    L += ["", "## 5. Trade-offs (item 5)", ""]
    L += [f"- {c}: {t.loc[c, 'trade_offs'] or 'none'}" for c in t.index if t.loc[c, "seatable_role"]]
    L += ["", "## 6. δ-error (§8.12; F = {" + ", ".join(F_SET) + "}, bar units; reported, never selecting)", ""]
    for name, d in o["deltas"].items():
        L.append(f"- {name}: " + "; ".join(
            f"{k}: π {v['pi']:.3f} [{v['pi_lo']:.3f}, {v['pi_hi']:.3f}], δ {v['delta']:.2f} (p90 {v['delta_p90']:.2f}), "
            f"comparable {v['n_comparable']}" for k, v in d.items()))
    L += ["", "## 7. The walk (§8.7)", ""]
    L += [f"- {s['family']} ({TIER[s['family']]}): **{s['seat']}** — {s['note']}" for s in res["seats"]]
    L += ["", f"M = {res['M'] if res['M'] is not None else 'HALT'}" + (
        " — M != 4: ref point, τ and gate numbers re-derived (item 8)." if res["M"] not in (None, M_MAX) else ""), "",
          f"Matches the §3 prediction V1 · E1 · N4: **{info['expected_match']}**"
          + ("" if info["expected_match"] else " — §8.14: outputs stay UNCOMMITTED; STOP."), "",
          "## 8. Three vectors from the same runs (+ v1 seat lines)", "",
          f"- v1 pre-registered (d706199): {info['v1_seats']}",
          f"- v1 Seed-bar re-grade (baf77c3): {info['seedbar_seats']}",
          f"- v2 (this read): {seat_line(res)}",
          f"- v2 with borderline → REDUNDANT (no §4b): {seat_line(o['res_no4b'])}",
          f"- pre-registered vector {' · '.join(PRE_REGISTERED)} co-reported at every station (§2.5).", "",
          "## 9. N1_off guardrail (§8.8; monitor, never halts)", ""]
    g = o["guard"]
    L += [f"- B_N1off = {info['B_n1off']['B_j']:.1f} line-h (s {info['B_n1off']['s_j']:.1f}, ν {info['B_n1off']['nu']}; "
          f"2·B = {2 * info['B_n1off']['B_j']:.1f}; v1-memo value 242.1); B_N3off = {info['B_n3off']['B_j']:.1f} MWh "
          f"({info['B_n3off']['seed_source']}); base N1_off {BASE_N1OFF:.0f}, base N3_off {BASE_N3OFF:.0f}.",
          f"- ΔN1_off range {g['table']['dN1_off'].min():.0f} … {g['table']['dN1_off'].max():.0f}; leakage median "
          f"{np.nanmedian(g['table']['leakage']) if np.isfinite(g['table']['leakage']).any() else float('nan'):.3f} "
          "(finding, not a violation).",
          f"- Flags: {g['flags']}.",
          "- Top-3 non-pocket lines by max Δhours (max, median): " + "; ".join(f"{a} ({b:.0f}, {c:.0f})" for a, b, c in g['top3']),
          f"- N4 == N4_L252 on every row: {info['n4_is_l252']}.", "",
          "## 10. Reporting lens", "", LENS_SENTENCE + f" Lens IDR {info['lens']['IDR']:.4g} $; Spearman with E1 "
          f"{info['lens']['rho_E1']:.3f}. Per design: `pool_lens_v2.csv`.", "",
          "## Deviations", ""] + [f"- {d}" for d in info["deviations"]] + [""]
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(L))


# --------------------------------------------------------------------------
# driver
# --------------------------------------------------------------------------
def run(wide=None, out_dir=po.POOL, figs_dir=FIGS, make_figs=True, synthetic=False, write=True, verbose=True,
        line_reader=None, plan=PLAN, gp_configs=GP_CONFIGS, stat_ids=None, n_boot_delta=N_BOOT_DELTA, X=None, B=None):
    if synthetic:
        assert wide is not None, "synthetic run needs an injected wide"
        if write:
            for d in (out_dir, figs_dir):
                assert not pn._under(d, po.POOL), f"REFUSED: synthetic output under analysis/pool/ ({d})"
    else:
        assert wide is None, "REFUSED: an injected wide is synthetic — pass synthetic=True"
        assert X is None and B is None and stat_ids is None
    assert_no_gp(gp_configs)
    amend = assert_amendment(plan)
    ps.assert_frozen_defs()
    defs = po.load_defs()
    role = roles(plan)
    X = pn.load_X() if X is None else X
    ids = list(po.CAND_IDS)
    B = pooled_bars(ids=ids) if B is None else B
    zero = sorted(B.index[B["B_j"] == 0])
    base = base_row()
    fl, fl_info = floors(base)
    if synthetic:
        reader, anchor_reader, landing = line_reader, None, {"skipped": "synthetic run"}
        offer = assert_offer_excluded([("base_v3:1", BASE_DIR)])
    else:
        wide = pn.load_wide()                                # pool_standings.build_wave("n0_E")
        landing = pn.landing_crosscheck(wide)
        reader = anchor_reader = pn.line_summary_reader
        offer = assert_offer_excluded([("base_v3:1", BASE_DIR), (OFFER_ANCHOR, po.run_dir(OFFER_ANCHOR))])
    wide = pn.check_wide(wide, X)
    col = f"N4_{L252}"
    n4_is_l252 = bool((wide["N4"].astype(float) == wide[col].astype(float)).all()) if col in wide.columns else "n/a"
    g = wide["G_run_usd"].astype(float).to_numpy()
    G_pair = float(np.median((g[:, None] + g[None, :])[np.triu_indices(len(g), 1)]))

    t = classify(per_id(wide, X, B, ids, role, fl, stat_ids), B)
    dead57 = set(pd.read_csv(os.path.join(po.POOL, "pool_dead_list_v2.csv")).query("status == 'DEAD'")["id"])
    alive = [c for c in ids if c not in dead57 and bool(t.loc[c, "computed"])]
    order = walk_order(alive, defs, role)
    O = pn.oriented(wide, order, defs)
    Tn = X["T"].to_numpy(dtype=float)
    R = pn.residualise(O, Tn)
    raw, resid = ps.spearman_matrix(O), ps.spearman_matrix(R)
    pt = pair_table(raw, resid, O, R, order, defs, {c: bool(t.loc[c, "COMP_RESOLVABLE"]) for c in alive})
    P = Pairs(pt)
    res = walk(t, P, order, use_4b=True)
    res_no4b = walk(t, P, order, use_4b=False)

    tr = {c: [] for c in t.index}
    for _, p in pt[pt["TRADE_OFF"]].iterrows():
        lab = "size" if p["TRADE_OFF_size"] else "comp"
        tr[p["c_later"]].append(f"{lab}:{p['p_earlier']}")
        tr[p["p_earlier"]].append(f"{lab}:{p['c_later']}")
    t["trade_offs"] = pd.Series({c: "; ".join(v) for c, v in tr.items()})
    t["family"] = [defs["candidates"][c]["family"] for c in t.index]
    t["tier"] = [TIER[f] for f in t["family"]]
    t["global_order"] = [defs["global_order"].index(c) + 1 for c in t.index]
    seated = set(seat_vector(res))
    st, why = {}, {}
    for c in t.index:
        rb = t.loc[c, "role_base"]
        if c in seated:
            st[c] = "SEATED (rule v2)"
        elif c == E_SEAT and res["halt"]:
            st[c] = "HALT FOR PI (E seat)"
        elif c in GUARDRAILS:
            st[c] = "GUARDRAIL"
        elif c in dead57 or not bool(t.loc[c, "computed"]):
            st[c] = "DEAD / constant / not computed"
        elif c in res["suppressed"]:
            st[c] = f"SUPPRESSED (REDUNDANT given {res['suppressed'][c]})"
        elif c in res["demoted"]:
            st[c] = "DEMOTED -> DIAGNOSTIC"
        else:
            red = list(pt.loc[(pt["c_later"] == c) & pt["REDUNDANT_given_p"], "p_earlier"])
            st[c] = rb + (f" (REDUNDANT given {', '.join(red)})" if red else "")
        why[c] = res["log"].get(c, f"role {rb} never seated" if not seatable_role(rb) else "")
    t["status"], t["why"] = pd.Series(st), pd.Series(why)

    Yt = pd.DataFrame({c: O[c].to_numpy(float) / float(B.loc[c, "B_j"]) for c in O.columns
                       if float(B.loc[c, "B_j"]) > 0}, index=O.index)
    S2 = [s for s in seat_vector(res) if s in Yt.columns] or [c for c in EXPECTED_V2 if c in Yt.columns]
    sets = {"v2 " + "·".join(S2): S2}
    if all(c in Yt.columns for c in PRE_REGISTERED):
        sets["v1 pre-registered V1·E1·N1"] = list(PRE_REGISTERED)
    for i, k in enumerate(S2):
        for alt in F_SET:
            if alt not in S2 and alt in Yt.columns:
                s_ = S2[:i] + [alt] + S2[i + 1:]
                sets[f"swap {k}->{alt}: " + "·".join(s_)] = s_
    deltas = {k: delta_report(Yt, v, n_boot=n_boot_delta) for k, v in sets.items()}

    b1 = n1off_bar()
    b3 = n3off_bar(anchor_reader=anchor_reader)
    gt, gflags, top3 = n1off_guard(wide, reader, B_n1off=b1["B_j"], B_n3off=b3["B_j"])
    lens_v = wide["E1"].astype(float) - LENS_B * wide["D1"].astype(float)
    lens = {"IDR": float(_idr(lens_v)), "rho_E1": pn._spearman(lens_v, wide["E1"])}
    exp = (not res["halt"]) and seat_vector(res) == EXPECTED_V2
    deviations = [
        f"Zero-bar set (computed, not asserted): {zero}.",
        "Sources disagreeing > 2x under the §8.1 recipe (disclosed, never switched): "
        + ", ".join(f"{c} ({B.loc[c, 'sources_ratio']:.2f})" for c in B.index[B["sources_disagree_2x"]])
        + f"; N1 ratio {B.loc['N1', 'sources_ratio']:.2f} (63 A3, on its sigma_pert estimator: "
        f"{B.loc['N1', 'A3_63']}).",
        "§8.11: the $40-offer assert reads n0_E:25 gen_summary directly (real run only; disclosed); synthetic runs "
        "assert on base_v3 only.",
        f"N4 floor = 1 % of 8,760 h = {N4_FLOOR_H:g} h (rule text rounds to 88 h).",
        f"B_N3off Seed source: {b3['seed_source']}.",
        "IDR / Mantel statistics computed for " + ("all non-constant ids" if stat_ids is None else
                                                   f"the subset {sorted(stat_ids)} (test speed)") + ".",
    ]
    E1_idr = float(t.loc["E1", "IDR"])
    info = {"read_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
            "sha_i": amendment_commit(plan), "sha_ii": script_commits(), "git_head": pn.git_short(),
            "amend_sha256": amend, "design_sha256": X.attrs["design_sha256"], "synthetic": synthetic,
            "floors": fl, "floors_info": fl_info, "G_pair_median": G_pair,
            "E1_over_gap": E1_idr / G_pair if np.isfinite(E1_idr) else np.nan,
            "offer": offer, "landing": landing, "B_n1off": b1, "B_n3off": b3, "n4_is_l252": n4_is_l252,
            "lens": lens, "expected_match": exp, "deviations": deviations, "zero_bar": zero,
            "v1_seats": _v1_seats(V1_CSV), "seedbar_seats": _v1_seats(SEEDBAR_CSV)}
    go = list(order) + [c for c in defs["global_order"] if c in t.index and c not in order]
    ed = t.join(B[["s_j", "nu", "max_abs_delta", "B_j", "B_lo", "B_up", "B_pert_v1", "B_seed_63"]].rename(
        columns={"B_lo": "B_j_lo90", "B_up": "B_j_up90"})).reindex(go)
    out = {"B": B, "tab": ed, "pairs": pt, "P": P, "res": res, "res_no4b": res_no4b, "deltas": deltas,
           "guard": {"table": gt, "flags": gflags, "top3": top3}, "info": info, "O": O, "order": order}
    if not write:
        return out
    os.makedirs(out_dir, exist_ok=True)
    ecols = ["family", "tier", "global_order", "role", "B_j", "B_j_lo90", "B_j_up90", "s_j", "nu", "max_abs_delta",
             "B_pert_v1", "B_seed_63", "IDR", "IDR_over_B", "IDR_over_B_lo90", "IDR_over_B_hi90", "IDR_over_B_up_analytic",
             "resid_IDR", "resid_IDR_over_B", "resid_IDR_over_B_lo90", "resid_IDR_over_B_hi90", "eta2_T", "iso_loo_R2",
             "comp_rho", "mantel_p_raw", "mantel_p_resid", "floor_M", "floor_need", "floor_pass", "RESOLVED",
             "COMP_RESOLVABLE", "sufficiency", "trade_offs", "status", "why"]
    ed[ecols].rename_axis("id").to_csv(os.path.join(out_dir, "pool_ed1b_v2.csv"))
    pt.to_csv(os.path.join(out_dir, "pool_pairs_v2.csv"), index=False)
    pd.DataFrame({"index": X.index.to_numpy(), "T": Tn, "E1": wide["E1"].to_numpy(float),
                  "D1": wide["D1"].to_numpy(float), "E1_minus_40_D1": lens_v.to_numpy(float)}).to_csv(
        os.path.join(out_dir, "pool_lens_v2.csv"), index=False)
    write_md(os.path.join(out_dir, "POOL_N0E_STANDINGS_v2.md"), out)
    if make_figs:
        os.makedirs(figs_dir, exist_ok=True)
        plot_idr_ci(ed, os.path.join(figs_dir, "n0E_v2_idr_over_B_ci.png"))
        plot_rho5(P, [c for c in ("V1", "E1", "X1", "N1", "N4") if c in order],
                  os.path.join(figs_dir, "n0E_v2_rho5x5.png"))
        dl = [c for c in order if defs["candidates"][c]["dir"] in ("min", "max")]
        rp = [(p["c_later"], p["p_earlier"]) for _, p in pt[pt["REDUNDANT_given_p"]].iterrows()]
        ps.plot_cluster_panel(raw.loc[dl, dl], defs, os.path.join(figs_dir, "n0E_v2_clustermap_raw.png"),
                              "n0_E raw oriented rho (n = 48)", red_pairs=rp)
    if verbose:
        print(ed[["role_base", "B_j", "IDR_over_B", "IDR_over_B_lo90", "resid_IDR_over_B_lo90", "mantel_p_raw",
                  "mantel_p_resid", "floor_pass", "RESOLVED", "COMP_RESOLVABLE", "status"]].to_string())
        print("v2:", seat_line(res), "| M =", res["M"], "| no-4b:", seat_line(res_no4b), "| expected match:", exp)
    return out


# --------------------------------------------------------------------------
# synthetic Y at the real X (dry runs and tests only)
# --------------------------------------------------------------------------
def _z(v):
    v = np.asarray(v, float)
    return (v - v.mean()) / v.std()


def composition_axes(X):
    """Three mutually orthogonal unit-variance composition directions (T-residualised design columns)."""
    T = X["T"].to_numpy(float)
    cols = [X["s"].to_numpy(float)] + [X[c].to_numpy(float) for c in X.attrs["u_cols"][:3]]
    Z = []
    for v in cols:
        r = _z(v - pn.bin_pchip(T, v))
        for q in Z:
            r = r - np.dot(r, q) / np.dot(q, q) * q
        Z.append(_z(r))
    return Z[0], Z[1], Z[2]


SCENARIOS = ("additive", "total_only", "one_proxy", "size_copy", "asymmetric", "borderline_tradeoff",
             "borderline_no_tradeoff", "binding_floor", "noise_E1", "strong_proxy", "conflict_demotion")


def synthetic_wide(scenario, X=None, B=None, seed=65):
    """Planted Y in units of the pooled B_j (hand-built seats: tests/test_pool_n0E_v2.py docstring)."""
    X = pn.load_X() if X is None else X
    B = pooled_bars() if B is None else B
    assert scenario in SCENARIOS, scenario
    rng = np.random.default_rng(seed)
    n = len(X)
    zT = _z(X["T"].to_numpy(float))
    zs, zq, zw = composition_axes(X)
    b = B["B_j"]
    ch = lambda k=0.3: k * rng.standard_normal(n)  # noqa: E731
    Y = {c: (b[c] if b[c] > 0 else 1.0) * ch() + 1e6 for c in po.CAND_IDS}
    for c in ("E5", "R1", "R3"):
        Y[c] = np.zeros(n)
    V1 = lambda a: b["V1"] * a + 4e6  # noqa: E731
    E1 = lambda a: b["E1"] * a + 8e9  # noqa: E731
    N4 = lambda a: np.round(b["N4"] * a) + 5000  # noqa: E731
    Y["V1"], Y["E1"], Y["N4"] = V1(-8 * zT - 3 * zs), E1(6 * zT + 4 * zw), N4(5 * zT + 6 * zq)
    if scenario == "total_only":
        Y["V1"], Y["E1"], Y["N4"] = V1(-8 * zT + ch()), E1(6 * zT + ch()), N4(-5 * zT + ch())
    elif scenario == "one_proxy":
        Y["V2"] = -3.0 * (Y["V1"] - 4e6) / b["V1"] * b["V2"] + 22.0
    elif scenario == "size_copy":
        Y["N4"] = N4(-8 * zT - 3 * zs + ch(0.4))                    # V1 copy + chatter (the N1 loophole)
    elif scenario == "asymmetric":
        Y["V1"] = V1(-8 * zT + ch(0.2))                             # partner pure size
        Y["N4"] = N4(-30 * zT + 2.0 * zq)                           # candidate ~5 B composition
    elif scenario in ("borderline_tradeoff", "borderline_no_tradeoff"):
        mix = (-0.45 * zs - 0.89 * zw) if scenario == "borderline_tradeoff" else (-0.30 * zs - 0.95 * zq)
        Y["N4"] = N4(-30 * zT + 6 * mix)
    elif scenario == "binding_floor":
        Y["X1"] = b["X1"] * 1.5 * zq + 2e8                          # resolvable, IDR ≈ 4 B < 0.1 % of base CO2
    elif scenario == "noise_E1":
        Y["E1"] = E1(ch())
    elif scenario == "strong_proxy":
        Y["E4"] = b["E4"] * (-40 * zT + 10 * zq) + 1e10             # TRANSFER, strongest responder
        Y["V2"] = -3.0 * (Y["V1"] - 4e6) / b["V1"] * b["V2"] + 22.0
    elif scenario == "conflict_demotion":
        Y["N4"] = N4(6 * zw)                                        # pure composition, no trade-off with V1 / E1
    if scenario != "binding_floor":
        Y["X1"] = Y["E1"] / 10.0
    Y["N1"] = Y["N4"] + np.round(b["N1"] * ch()) + 30750
    Y["D1"] = b["D1"] * 10 * zT + 1e6
    w = pd.DataFrame(Y)
    w["N4_L252"] = w["N4"]
    w.insert(0, "index", X.index.to_numpy())
    w.insert(0, "key", [f"{WAVE}:{i}" for i in X.index])
    w["suspect"], w["G_run_usd"] = False, 1.0e6
    for c in pn.D3_COLS:
        w[c] = 0.0
    return w


def synthetic_reader(wide, base_dir=BASE_DIR, data_dir=po.DATA):
    """base_v3 line_summary with L252 hours = N4 and the largest non-pocket line absorbing N1_off - base."""
    base = pd.read_csv(os.path.join(base_dir, "line_summary.csv"))
    base["Line"] = base["Line"].astype(str)
    pl = set(po.pocket_lines(data_dir, 120))
    off = base[~base["Line"].isin(pl)]
    big = off.loc[off["hours_ge_99pct"].idxmax(), "Line"]
    by = {k: (n1, n4) for k, n1, n4 in zip(wide["key"], wide["N1"], wide["N4"])}

    def read(key):
        n1, n4 = by[key]
        ls = base.copy()
        ls.loc[ls["Line"].isin(pl), "hours_ge_99pct"] = 0
        ls.loc[ls["Line"] == L252, "hours_ge_99pct"] = n4
        ls.loc[ls["Line"] == big, "hours_ge_99pct"] += (n1 - n4) - BASE_N1OFF
        return ls
    return read


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--no-figs", action="store_true")
    ap.add_argument("--synthetic", choices=SCENARIOS, default=None)
    ap.add_argument("--out", default=None)
    a = ap.parse_args(argv)
    if a.synthetic:
        assert a.out, "--synthetic needs --out <scratch dir>"
        w = synthetic_wide(a.synthetic)
        run(wide=w, out_dir=a.out, figs_dir=os.path.join(a.out, "figs"), make_figs=not a.no_figs, synthetic=True,
            line_reader=synthetic_reader(w))
    else:
        assert a.out is None, "the real read writes analysis/pool/ only"
        run(make_figs=not a.no_figs)
    return 0


if __name__ == "__main__":
    sys.exit(main())
