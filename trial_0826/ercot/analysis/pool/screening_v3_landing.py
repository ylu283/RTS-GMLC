#!/usr/bin/env python3
"""Prompt 62 Part C §4.5 — landing analysis of `screening_v3` (zero simulation).

16 screened sites, each alone at 180 MW under identity v3, read against
`base_v3:1`: 10 new rows (`screening_v3:1-10`) + the 6 slate sites at L180
from wave D (`location_oat_v2`, rows named by `waves/screening_v3/covariates.csv`
`source_row`). Row `screening_v3:11` is the replicate of wave-D row 3 (site 163
L180): its overall.csv md5 must equal wave D's (asserted; no code/data drift).

Rules: prompt 62 v1.1 §4.5, committed verbatim in `waves/screening_v3/README.md`
with the wave, before any Y of this wave existed (asserted). B_j from
`analysis/noise_v3/ercot_noise.json` via `pool_n0E.bars` (61 §3, D2 excluded).

Reader: `pool_standings.build_wave` (pool_objectives.build_pool +
pool_full_metrics.json merge); `ercot_gp_loader.suspect_flag` cross-checks the
`suspect` column. Never reads n0_E Y beyond the committed Part B outputs, never
random_E, never methods_E.

Pinned implementation choices (the rule text leaves them open):
- Graded ids = every id with B_j > 0 and a defined delta: 23 of 28 (E5/E9/R1/R3
  have B_j = 0; D2 = D1 / (pem_mw * 8760) is 0/0 at base_v3, so Δ_D2 is
  undefined). Holm family = those 23 ids, primary contrast only.
- d_s = y_j(site s at 180 MW) - y_j(base_v3:1). HL = median of the 8 x 5 = 40
  differences d_C - d_U (C = pocket_120 + wind_near, U = far). Mann-Whitney U
  counts C > U (+1/2 per tie); p from scipy `mannwhitneyu(method="exact")`
  (its exact null assumes no ties: ties are counted and disclosed per id).
  Moses interval: k = largest integer with P0(U <= k - 1) <= 0.025 under the
  exact no-ties null (enumerated, C(13, 5) = 1,287 splits); interval =
  [D_(k), D_(41-k)] of the sorted differences; achieved coverage reported.
  Rank-biserial r = 2 U / (m n) - 1 (> 0: C sites have the larger d).
- WIND-only sensitivity drops the one PV site of C (116; 7 vs 5), raw p only.
- ΔV1 decomposition: own-site = Δ of the retrofitted unit's rows that V1
  counts (the parent `<site>` row; the `<site>_PEM` twin is is_pem = True and
  never in V1 — asserted 0); other-site = ΔV1 - own. The twin's own
  curtailment column is reported for the accounting-reclassification read.
- E1 per site: NOT READABLE if |Δ| < B_E1; GAP-READABLE if |Δ| > G_site + G_base;
  else WITHIN GAP BOUND (61's labels).
- Ranking: relief/MW = -ΔV1 / 180 (MWh/MW); tie band = B_V1 / 180. A site
  ranked 7-16 is TIED if within one band of the 6th value; a site ranked 1-6 is
  TIED if within one band of the 7th. SLATE BUS-SET HOLDS iff the top 6 lie on
  buses {120, 2, 75} (strict ranks; the TIED marks are reported beside).
  Kendall tau_b v2 rank vs v3 rank, scipy exact p.
- Dominance: seated objectives all dir = min; z_j = Δ_j / B_j. Slate site t
  dominates s iff z_t <= z_s on every seated j and < on one. Primary set
  (V1, E1, N1); alternative (V1, E1, N4). For a non-dominated site the margin
  = min over slate t of max_j (z_t,j - z_s,j) (bars by which s beats the
  closest slate site on its best objective).

Outputs (analysis/pool): SCREENING_V3.md, screening_v3_{sites,locational,
covariate_rho,ranking,dominance}.csv, figs/screening_v3/*.png; plus the Part C
block appended (idempotently) to §E of POOL_N0E_STANDINGS.md and C_* columns
of pool_ed1b_combined.csv (no seat changes).

Run: cd trial_0826/ercot && /opt/anaconda3/bin/python analysis/pool/screening_v3_landing.py
"""
import argparse
import datetime as dt
import hashlib
import itertools
import json
import os
import subprocess
import sys

import numpy as np
import pandas as pd
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
ERCOT = os.path.abspath(os.path.join(HERE, "..", ".."))
for p in (ERCOT, HERE, os.path.join(ERCOT, "tools")):
    if p not in sys.path:
        sys.path.insert(0, p)
import pool_objectives as po  # noqa: E402
import pool_standings as ps  # noqa: E402
import pool_n0E as pn  # noqa: E402
from analysis.ercot_gp.ercot_gp_loader import suspect_flag  # noqa: E402

WAVE = "screening_v3"
WAVE_D = "location_oat_v2"
BASE_DIR = os.path.join(po.EXTR, "base_v3", "run_index_1")
README = os.path.join(po.WAVES, WAVE, "README.md")
COV = os.path.join(po.WAVES, WAVE, "covariates.csv")
FIGS = os.path.join(po.POOL, "figs", "screening_v3")
MD = os.path.join(po.POOL, "SCREENING_V3.md")
STANDINGS_MD = os.path.join(po.POOL, "POOL_N0E_STANDINGS.md")
COMBINED = os.path.join(po.POOL, "pool_ed1b_combined.csv")
PEM_MW = 180.0
SEED_JSON = os.path.join(ERCOT, "analysis", "noise_v3", "ercot_noise_seed.json")
SEED_BINDING = ("N1",)               # 63: perturbation ruler DISAGREES with Seed chatter -> B_N1^seed binds
REPLICATE = (f"{WAVE}:11", f"{WAVE_D}:3")
TIERS = {"pocket_120": ("163", "270", "274", "275", "116"), "wind_near": ("110", "140", "146"),
         "pv_pocket": ("30", "59", "142"), "far": ("91", "205", "206", "204", "20")}
C_TIERS, U_TIERS = ("pocket_120", "wind_near"), ("far",)
SLATE = ("163", "140", "146", "270", "110", "274")
SLATE_BUSES = (120, 2, 75)
SEATED = ("V1", "E1", "N1")
SEATED_ALT = ("V1", "E1", "N4")
ALPHA, HL_BARS, CI_LEVEL = 0.05, 2.0, 0.95
TOP = 6
UNDEFINED_AT_BASE = ("D2",)          # PEM utilization: pem_mw = 0 at base -> no delta
PREDICTION = {"enters": "275", "leaves": "163", "bus_set_holds": True}
BEGIN, END = "<!-- PART C screening_v3 BEGIN -->", "<!-- PART C screening_v3 END -->"


# --------------------------------------------------------------------------
# guards and inputs
# --------------------------------------------------------------------------
def rules_text():
    import make_screening_v3 as ms
    t = open(README).read()
    assert ms.SECTION_4_4_4_5 in t, "README no longer carries prompt 62 §4.4-4.5 verbatim"
    return ms.SECTION_4_4_4_5


def git(*args):
    return subprocess.run(["git", *args], cwd=ERCOT, capture_output=True, text=True, check=True).stdout.strip()


def rules_commit():
    """Commit that added the README (the wave commit; before any screening_v3 Y)."""
    return git("log", "--diff-filter=A", "--format=%h", "--", os.path.relpath(README, ERCOT)).splitlines()[-1]


def md5(path):
    with open(path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()


def load_cov(path=COV):
    cov = pd.read_csv(path, dtype={"site": str}, float_precision="round_trip")
    assert len(cov) == 16 and cov["site"].is_unique
    for t, s in TIERS.items():
        assert sorted(cov.loc[cov["tier"] == t, "site"]) == sorted(s), t
    assert sorted(cov.loc[cov["slate"], "site"]) == sorted(SLATE)
    return cov.set_index("site")


def base_row(defs=None):
    row, ident, label = ps.resolve_base(BASE_DIR, defs=defs)
    assert label == "base_v3:1" and ident["identity"] == "v3", (label, ident)
    pm = json.load(open(os.path.join(BASE_DIR, "pool_full_metrics.json")))
    for c in ps.JSON_OVERRIDE:                      # same merge as build_wave
        v = pm.get(c)
        row[c] = np.nan if v is None else float(v)
    assert pm["overall_md5"] == row["overall_md5"]
    row["suspect"] = bool(suspect_flag(row))
    row["identity"] = ident["identity"]
    return row


def _seed():
    return json.load(open(SEED_JSON))


def seed_bars():
    j = _seed()
    assert sorted(j["A3"]["disagree_gradable"]) == sorted(set(SEED_BINDING) | {"E9"}), j["A3"]["disagree_gradable"]
    return {k: float(v["B_seed"]) for k, v in j["bars"].items()}


def seed_pert(j):
    return float(_seed()["bars"][j]["B_pert"])


def replicate_check():
    a, b = (os.path.join(po.run_dir(k), "overall.csv") for k in REPLICATE)
    ma, mb = md5(a), md5(b)
    assert ma == mb, f"replicate drift: {REPLICATE[0]} {ma} != {REPLICATE[1]} {mb}"
    return {"new": REPLICATE[0], "ref": REPLICATE[1], "overall_md5": ma}


def site_rows(cov, defs=None):
    """16 site rows (screening_v3 1-10 + wave D L180 slate rows) + the replicate row."""
    sv = ps.build_wave(WAVE, defs=defs, verbose=False)
    wd = ps.build_wave(WAVE_D, defs=defs, verbose=False)
    allw = pd.concat([sv, wd], ignore_index=True).set_index("key")
    keys = []
    for s, r in cov.iterrows():
        k = r["source_row"]
        assert str(allw.loc[k, "site"]) == s and abs(float(allw.loc[k, "pem_mw"]) - PEM_MW) <= 1e-6, (s, k)
        assert int(allw.loc[k, "bus"]) == int(r["bus"]) and allw.loc[k, "unit_type"] == r["unit_type"], (s, k)
        keys.append(k)
    assert sorted(set(sv["key"]) - set(keys)) == [REPLICATE[0]]
    rows = allw.loc[keys].copy()
    rows["site"] = list(cov.index)
    rep = allw.loc[REPLICATE[0]]
    for k, r in allw.loc[keys + [REPLICATE[0]]].iterrows():
        assert r["identity"] == "v3", (k, r["identity"])
        assert bool(suspect_flag(r)) == bool(r["suspect"]), (k, "suspect_flag cross-check")
    return rows.reset_index().set_index("site"), rep


def own_site(key, site, base_gs):
    gs = po.co.gen_summary(po.run_dir(key))
    v1 = gs[(~gs["is_pem"].astype(bool)) & gs["unit_type"].isin(["WIND", "PV"])]
    parent = v1[v1["Generator"].astype(str) == site]
    assert len(parent) == 1, (key, site)
    twin = gs[gs["Generator"].astype(str) == f"{site}_PEM"]
    assert len(twin) == 1 and bool(twin["is_pem"].iloc[0]), (key, site)
    assert not ((v1["Generator"].astype(str) == f"{site}_PEM").any())     # twin never in V1
    b = base_gs[(base_gs["Generator"].astype(str) == site) & (~base_gs["is_pem"].astype(bool))]
    assert len(b) == 1
    return {"own_dV1": float(parent["curtailment_mwh"].iloc[0]) - float(b["curtailment_mwh"].iloc[0]),
            "twin_curtailment_mwh": float(twin["curtailment_mwh"].iloc[0]),
            "twin_output_mwh": float(twin["output_mwh"].iloc[0]),
            "V1_from_gen_summary": float(v1["curtailment_mwh"].sum())}


# --------------------------------------------------------------------------
# statistics
# --------------------------------------------------------------------------
def exact_u_null(m, n):
    """P0(U = u) for U = #(C > U) with m C and n U values, no ties (enumerated)."""
    N = m + n
    cnt = np.zeros(m * n + 1)
    for cpos in itertools.combinations(range(N), m):     # ranks of the C values (0-based)
        u = sum(cpos) - m * (m - 1) // 2
        cnt[u] += 1
    return cnt / cnt.sum()


def moses_k(m, n, level=CI_LEVEL):
    F = np.cumsum(exact_u_null(m, n))
    a = (1 - level) / 2
    k = max(k for k in range(1, m * n + 1) if (F[k - 2] if k >= 2 else 0.0) <= a)
    cov = 1 - 2 * (F[k - 2] if k >= 2 else 0.0)
    return k, cov


def hl_read(c, u, level=CI_LEVEL):
    c, u = np.asarray(c, float), np.asarray(u, float)
    d = np.sort((c[:, None] - u[None, :]).ravel())
    m, n = len(c), len(u)
    U = float(np.sum(c[:, None] > u[None, :]) + 0.5 * np.sum(c[:, None] == u[None, :]))
    res = stats.mannwhitneyu(c, u, alternative="two-sided", method="exact")
    assert abs(res.statistic - U) < 1e-9
    k, cv = moses_k(m, n, level)
    return {"HL": float(np.median(d)), "U": U, "p": float(res.pvalue), "lo": float(d[k - 1]),
            "hi": float(d[m * n - k]), "coverage": cv, "k": k, "r_rb": 2 * U / (m * n) - 1,
            "n_tied_pairs": int(np.sum(c[:, None] == u[None, :])),
            "n_tied_values": int(len(np.concatenate([c, u])) - len(np.unique(np.concatenate([c, u]))))}


def holm(p):
    p = np.asarray(p, float)
    o = np.argsort(p, kind="stable")
    k = len(p)
    adj = np.empty(k)
    run = 0.0
    for i, j in enumerate(o):
        run = max(run, min(1.0, (k - i) * p[j]))
        adj[j] = run
    return adj


def locational_verdict(r, B, alpha=ALPHA, bars=HL_BARS):
    why = []
    if r["p_holm"] > alpha:
        why.append(f"Holm p {r['p_holm']:.3g} > {alpha:g}")
    if abs(r["HL"]) < bars * B:
        why.append(f"|HL| {abs(r['HL']) / B:.2f} B_j < {bars:g}")
    if r["lo"] <= 0 <= r["hi"]:
        why.append("interval contains 0")
    return ("LOCATIONAL" if not why else "NOT LOCATIONAL"), "; ".join(why)


def ranking(relief, cov, band, top=TOP):
    """relief: Series site -> relief/MW (v3). Returns per-site table."""
    r = relief.sort_values(ascending=False, kind="stable")
    rk = pd.Series(np.arange(1, len(r) + 1), index=r.index)
    v6, v7 = r.iloc[top - 1], r.iloc[top]
    tab = pd.DataFrame({"relief_per_mw_v3": r, "rank_v3": rk})
    tab["rank_v2"] = cov.loc[tab.index, "rank_v2"].astype(int)
    tab["relief_per_mw_v2"] = cov.loc[tab.index, "relief_per_mw_v2"]
    tab["bus"] = cov.loc[tab.index, "bus"].astype(int)
    tab["unit_type"] = cov.loc[tab.index, "unit_type"]
    tab["omega_180"] = cov.loc[tab.index, "omega_180"]
    tab["tier"] = cov.loc[tab.index, "tier"]
    tab["slate"] = cov.loc[tab.index, "slate"].astype(bool)
    tab["top6_v3"] = tab["rank_v3"] <= top
    ref = np.where(tab["top6_v3"], v7, v6)
    tab["gap_to_boundary_bands"] = (tab["relief_per_mw_v3"] - ref) / band
    tab["TIED"] = np.abs(tab["relief_per_mw_v3"] - ref) <= band
    return tab


def dominance(z, slate, others, ids):
    rows = []
    for s in others:
        by = [t for t in slate if (z.loc[t, list(ids)] <= z.loc[s, list(ids)]).all()
              and (z.loc[t, list(ids)] < z.loc[s, list(ids)]).any()]
        margin = min(float((z.loc[t, list(ids)] - z.loc[s, list(ids)]).max()) for t in slate)
        rows.append({"objectives": "/".join(ids), "site": s, "dominated": bool(by),
                     "dominated_by": ";".join(by), "margin_bars": np.nan if by else margin,
                     **{f"z_{j}": float(z.loc[s, j]) for j in ids}})
    return pd.DataFrame(rows)


# --------------------------------------------------------------------------
# compute
# --------------------------------------------------------------------------
def compute():
    rules_text()
    defs = po.load_defs()
    cov = load_cov()
    B = pn.bars()
    graded = [j for j in B.index if B.loc[j, "B_j"] > 0]
    assert sorted(set(B.index) - set(graded)) == sorted(pn.ZERO_BAR_EXPECTED), set(B.index) - set(graded)
    rep = replicate_check()
    rows, rep_row = site_rows(cov, defs)
    base = base_row(defs)
    base_gs = po.co.gen_summary(BASE_DIR)
    undefined = [j for j in graded if pd.isna(base[j])]
    assert undefined == list(UNDEFINED_AT_BASE), undefined       # D2 = D1 / (pem_mw * 8760): 0/0 at base
    graded = [j for j in graded if j not in undefined]
    for j in graded:                          # replicate = wave D row 3 on every graded id
        assert rep_row[j] == rows.loc["163", j] or (pd.isna(rep_row[j]) and pd.isna(rows.loc["163", j])), j

    # ---- per-site deltas ---------------------------------------------------
    S = rows.index
    d = pd.DataFrame({j: rows[j].astype(float) - float(base[j]) for j in graded}, index=S)
    assert not d.isna().any().any(), d.columns[d.isna().any()].tolist()
    sites = pd.DataFrame(index=S)
    sites["key"] = rows["key"]
    for c in ("tier", "slate", "bus", "unit_type", "omega_180", "gen_pmax", "rank_v2", "saturation_flag"):
        sites[c] = cov.loc[S, c]
    sites["suspect"] = rows["suspect"].astype(bool)
    sites["identity"] = rows["identity"]
    sites["G_run_usd"] = rows["G_run_usd"].astype(float)
    sites["relief_V1_mwh"] = -d["V1"]
    sites["relief_per_mw"] = -d["V1"] / PEM_MW
    dec = {s: own_site(rows.loc[s, "key"], s, base_gs) for s in S}
    for s in S:
        assert abs(dec[s]["V1_from_gen_summary"] - float(rows.loc[s, "V1"])) <= 1e-6 * float(rows.loc[s, "V1"]), s
    sites["own_dV1"] = [dec[s]["own_dV1"] for s in S]
    sites["other_dV1"] = d["V1"] - sites["own_dV1"]
    sites["own_share_of_relief"] = sites["own_dV1"] / d["V1"]
    sites["twin_curtailment_mwh"] = [dec[s]["twin_curtailment_mwh"] for s in S]
    sites["twin_output_mwh"] = [dec[s]["twin_output_mwh"] for s in S]
    BE1 = float(B.loc["E1", "B_j"])
    G_base = float(base["G_run_usd"])
    sites["E1_gap_bound"] = sites["G_run_usd"] + G_base
    sites["E1_verdict"] = ["NOT READABLE" if abs(x) < BE1 else ("GAP-READABLE" if abs(x) > g else "WITHIN GAP BOUND")
                           for x, g in zip(d["E1"], sites["E1_gap_bound"])]
    for j in graded:
        sites[f"d_{j}"] = d[j]
        sites[f"z_{j}"] = d[j] / float(B.loc[j, "B_j"])

    # ---- tiers -------------------------------------------------------------
    tier = cov.loc[S, "tier"]
    C = [s for s in S if tier[s] in C_TIERS]
    U = [s for s in S if tier[s] in U_TIERS]
    Cw = [s for s in C if cov.loc[s, "unit_type"] == "WIND"]
    assert (len(C), len(U), len(Cw)) == (8, 5, 7) and (cov.loc[U, "unit_type"] == "WIND").all()
    loc = []
    for j in graded:
        r = hl_read(d.loc[C, j], d.loc[U, j])
        w = hl_read(d.loc[Cw, j], d.loc[U, j])
        kw = stats.kruskal(*[d.loc[[s for s in S if tier[s] == t], j] for t in TIERS])
        Bj = float(B.loc[j, "B_j"])
        loc.append({"id": j, "family": defs["candidates"][j]["family"], "dir": defs["candidates"][j]["dir"],
                    "global_order": defs["global_order"].index(j) + 1, "B_j": Bj,
                    **{f"median_{t}": float(d.loc[[s for s in S if tier[s] == t], j].median()) for t in TIERS},
                    "HL": r["HL"], "HL_over_B": r["HL"] / Bj, "U": r["U"], "r_rb": r["r_rb"], "p_exact": r["p"],
                    "moses_lo": r["lo"], "moses_hi": r["hi"], "moses_coverage": r["coverage"],
                    "n_tied_pairs": r["n_tied_pairs"], "n_tied_values": r["n_tied_values"],
                    "wind_HL": w["HL"], "wind_HL_over_B": w["HL"] / Bj, "wind_p_exact": w["p"],
                    "wind_lo": w["lo"], "wind_hi": w["hi"], "kw_H": float(kw.statistic), "kw_p": float(kw.pvalue)})
    loc = pd.DataFrame(loc)
    loc["p_holm"] = holm(loc["p_exact"])
    v = [locational_verdict({"p_holm": a, "HL": h, "lo": lo, "hi": hi}, b)
         for a, h, lo, hi, b in zip(loc["p_holm"], loc["HL"], loc["moses_lo"], loc["moses_hi"], loc["B_j"])]
    loc["verdict"] = [x[0] for x in v]
    loc["why_not"] = [x[1] for x in v]
    loc["wind_2B_and_p05"] = (loc["wind_HL_over_B"].abs() >= HL_BARS) & (loc["wind_p_exact"] <= ALPHA)
    seed = seed_bars()
    loc["B_seed"] = [seed[j] for j in loc["id"]]
    for j in loc["id"]:
        assert abs(seed_pert(j) - float(B.loc[j, "B_j"])) <= 1e-9 * max(1.0, float(B.loc[j, "B_j"])), j
    loc["HL_over_B_seed"] = loc["HL"] / loc["B_seed"]
    vs = [locational_verdict({"p_holm": a, "HL": h, "lo": lo, "hi": hi}, b)
          for a, h, lo, hi, b in zip(loc["p_holm"], loc["HL"], loc["moses_lo"], loc["moses_hi"], loc["B_seed"])]
    loc["verdict_B_seed"] = [x[0] for x in vs]
    loc["seed_ruler_binding"] = loc["id"].isin(SEED_BINDING)
    loc = loc.sort_values("global_order").reset_index(drop=True)

    # ---- covariates ----------------------------------------------------------
    cov_cols = ["H_C_180_MWh", "base_v3_own_curtailment_mwh", "omega_180"] + [c for c in cov.columns if c.startswith("ptdf_")]
    pocket = [f"ptdf_{l}" for l in po.pocket_lines(po.DATA, 120)]
    crho = []
    for j in graded:
        for c in cov_cols:
            x = cov.loc[S, c].astype(float)
            if x.nunique() < 2:
                rho, p = np.nan, np.nan
            else:
                rho, p = stats.spearmanr(d[j], x)
            crho.append({"id": j, "covariate": c, "kind": ("pocket PTDF" if c in pocket else
                                                            ("PTDF" if c.startswith("ptdf_") else c)),
                         "rho": float(rho), "p_asymptotic": float(p), "n_unique": int(x.nunique())})
    crho = pd.DataFrame(crho)

    # ---- ranking ---------------------------------------------------------------
    band = float(B.loc["V1", "B_j"]) / PEM_MW
    rk = ranking(sites["relief_per_mw"], cov, band)
    tau = stats.kendalltau(rk["rank_v2"], rk["rank_v3"], method="exact")
    top = list(rk.index[rk["top6_v3"]])
    top_buses = sorted(set(rk.loc[top, "bus"]))
    holds = set(top_buses) <= set(SLATE_BUSES)
    entered = sorted(set(top) - set(SLATE), key=top.index)
    left = [s for s in SLATE if s not in top]
    rank_info = {"band": band, "top6": top, "top6_buses": top_buses, "bus_set_holds": holds,
                 "entered": entered, "left": left, "tau_b": float(tau.statistic), "tau_p_exact": float(tau.pvalue),
                 "tied_sites": list(rk.index[rk["TIED"]]),
                 "closest": ", ".join(f"{s} {g:+.3f} bands" for s, g in
                                      rk["gap_to_boundary_bands"].abs().nsmallest(2).index.map(
                                          lambda s: (s, rk.loc[s, "gap_to_boundary_bands"]))),
                 "pred_enters": PREDICTION["enters"] in entered, "pred_leaves": PREDICTION["leaves"] in left,
                 "pred_bus_set": holds == PREDICTION["bus_set_holds"]}

    # ---- dominance -------------------------------------------------------------
    z = pd.DataFrame({j: d[j] / float(B.loc[j, "B_j"]) for j in graded}, index=S)
    for j in set(SEATED) | set(SEATED_ALT):
        assert defs["candidates"][j]["dir"] == "min", j
    others = [s for s in S if s not in SLATE]
    dom = pd.concat([dominance(z, list(SLATE), others, SEATED), dominance(z, list(SLATE), others, SEATED_ALT)],
                    ignore_index=True)

    info = {"rules_commit": rules_commit(), "replicate": rep, "graded": graded, "base_key": "base_v3:1",
            "base_identity": base["identity"], "base_suspect": base["suspect"], "G_base": G_base,
            "C": C, "U": U, "C_wind": Cw, "rank": rank_info, "moses": moses_k(len(C), len(U)),
            "moses_wind": moses_k(len(Cw), len(U)), "min_p_exact": float(2 * exact_u_null(8, 5)[0]),
            "git_head": pn.git_short(), "n_suspect": int(sites["suspect"].sum())}
    return sites, loc, crho, rk, dom, info, B


# --------------------------------------------------------------------------
# figures (assert-before-draw against the written csv)
# --------------------------------------------------------------------------
def _plt():
    return ps._rc()


def _bold(ax):
    for lab in ax.get_xticklabels() + ax.get_yticklabels():
        lab.set_fontweight("bold")


def figures(out_dir, figs_dir):
    plt = _plt()
    os.makedirs(figs_dir, exist_ok=True)
    loc = pd.read_csv(os.path.join(out_dir, "screening_v3_locational.csv"))
    rk = pd.read_csv(os.path.join(out_dir, "screening_v3_ranking.csv"), dtype={"site": str}).set_index("site")
    st = pd.read_csv(os.path.join(out_dir, "screening_v3_sites.csv"), dtype={"site": str}).set_index("site")

    # 1. HL / B_j per graded id
    y = loc["HL_over_B"].to_numpy()
    assert np.allclose(y, loc["HL"] / loc["B_j"])
    fig, ax = plt.subplots(figsize=(15, 7))
    col = ["#b2182b" if v == "LOCATIONAL" else "#7f7f7f" for v in loc["verdict"]]
    ax.bar(range(len(loc)), y, color=col)
    for s in (-HL_BARS, HL_BARS):
        ax.axhline(s, color="k", ls="--", lw=1.5)
    ax.axhline(0, color="k", lw=0.8)
    ax.set_xticks(range(len(loc)))
    ax.set_xticklabels(loc["id"], rotation=90)
    ax.set_ylabel("HL shift (C - far) / B_j")
    ax.set_title("screening_v3: Hodges-Lehmann shift, pocket+near (8) vs far (5)\nred = LOCATIONAL; dashed = +/-2 B_j", fontsize=16)
    _bold(ax)
    fig.tight_layout()
    fig.savefig(os.path.join(figs_dir, "sv3_hl_over_B.png"), dpi=130)
    plt.close(fig)

    # 2. relief / MW ranking
    r = rk.sort_values("rank_v3")
    assert np.allclose(r["relief_per_mw_v3"], st.loc[r.index, "relief_per_mw"])
    fig, ax = plt.subplots(figsize=(15, 7))
    cmap = {"pocket_120": "#b2182b", "wind_near": "#ef8a62", "pv_pocket": "#67a9cf", "far": "#2166ac"}
    ax.bar(range(len(r)), r["relief_per_mw_v3"], color=[cmap[t] for t in r["tier"]],
           edgecolor=["k" if s else "none" for s in r["slate"]], linewidth=2.5)
    ax.axvline(TOP - 0.5, color="k", ls=":", lw=1.5)
    ax.set_xticks(range(len(r)))
    ax.set_xticklabels([f"{s}{'*' if t else ''} b{b}" for s, t, b in zip(r.index, r["TIED"], r["bus"])], rotation=90)
    ax.set_ylabel("V1 relief per MW at 180 MW (MWh/MW)")
    ax.set_title("screening_v3 + wave D L180: matched-MW ranking\nblack edge = E-D3 slate; * = TIED; dotted line = top-6 boundary", fontsize=16)
    from matplotlib.patches import Patch
    ax.legend(handles=[Patch(color=c, label=t) for t, c in cmap.items()], prop={"weight": "bold"})
    _bold(ax)
    fig.tight_layout()
    fig.savefig(os.path.join(figs_dir, "sv3_relief_per_mw_ranking.png"), dpi=130)
    plt.close(fig)

    # 3. seated objectives in bar units
    fig, axes = plt.subplots(1, 2, figsize=(16, 7))
    for ax, (a, b) in zip(axes, (("z_V1", "z_E1"), ("z_V1", "z_N1"))):
        assert np.allclose(st[a], st[f"d_{a[2:]}"] / loc.set_index("id").loc[a[2:], "B_j"])
        for t, c in cmap.items():
            m = st["tier"] == t
            ax.scatter(st.loc[m, a], st.loc[m, b], s=[200 if s else 80 for s in st.loc[m, "slate"]],
                       color=c, edgecolor="k", label=t)
        for s in st.index:
            ax.annotate(s, (st.loc[s, a], st.loc[s, b]), fontsize=12, fontweight="bold",
                        xytext=(4, 4), textcoords="offset points")
        ax.set_xlabel(f"Δ{a[2:]} / B_{a[2:]} (lower = better)")
        ax.set_ylabel(f"Δ{b[2:]} / B_{b[2:]} (lower = better)")
        _bold(ax)
    axes[0].legend(prop={"weight": "bold"})
    fig.suptitle("screening_v3: seated objectives at 180 MW vs base_v3 (large markers = slate)", fontweight="bold")
    fig.tight_layout()
    fig.savefig(os.path.join(figs_dir, "sv3_seated_dominance.png"), dpi=130)
    plt.close(fig)


# --------------------------------------------------------------------------
# md + Part C append
# --------------------------------------------------------------------------
def _g(v, d=3):
    if isinstance(v, (bool, np.bool_)):
        return "yes" if v else "no"
    if v is None or (isinstance(v, float) and not np.isfinite(v)):
        return "n/a"
    if isinstance(v, (int, np.integer)):
        return f"{v:,}"
    a = abs(v)
    if a != 0 and (a >= 1e5 or a < 1e-3):
        return f"{v:.{d}g}"
    return f"{v:,.{d}f}"


def _p(v):
    return _g(v) if not isinstance(v, (float, np.floating)) or not np.isfinite(v) else f"{v:.3g}"


def _tab(df, cols, fmt=None):
    fmt = fmt or {c: _p for c in cols if c.startswith(("p_", "wind_p", "kw_p", "tau_p"))}
    out = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for _, r in df.iterrows():
        out.append("| " + " | ".join(fmt.get(c, _g)(r[c]) if not isinstance(r[c], str) else r[c] for c in cols) + " |")
    return "\n".join(out)


def write_md(path, sites, loc, crho, rk, dom, info, B):
    R = info["rank"]
    n_loc = loc[loc["verdict"] == "LOCATIONAL"]
    seated = loc.set_index("id").loc[list(dict.fromkeys(SEATED + SEATED_ALT))]
    L = []
    a = L.append
    a("# SCREENING_V3 — 16-site matched-MW screening under identity v3 (prompt 62 Part C §4.5)")
    a("")
    a(f"Generated {dt.date.today().isoformat()} by `analysis/pool/screening_v3_landing.py` at `{info['git_head']}`. "
      f"Rules: prompt 62 v1.1 §4.5, committed verbatim with the wave (`waves/screening_v3/README.md`, "
      f"`{info['rules_commit']}`) before any screening_v3 Y existed. **E-D3 is not reopened; no seat changes.**")
    a("")
    a("## 0. Headline")
    a("")
    a(f"- **LOCATIONAL ids (Holm ≤ 0.05, |HL| ≥ 2 B_j, Moses interval excludes 0):** "
      + (", ".join(f"{r.id} (HL/B {r.HL_over_B:+.2f}, Holm p {r.p_holm:.3g})" for r in n_loc.itertuples()) or "none")
      + f" — of {len(loc)} graded ids.")
    a("- **Seated objectives:** " + "; ".join(
        f"{j} HL/B {seated.loc[j, 'HL_over_B']:+.2f}, exact p {seated.loc[j, 'p_exact']:.3g}, Holm p "
        f"{seated.loc[j, 'p_holm']:.3g} → {seated.loc[j, 'verdict']}" for j in seated.index) + ".")
    a(f"- **Matched-MW ranking:** v3 top 6 = {', '.join(R['top6'])} on buses {R['top6_buses']} → "
      f"**SLATE BUS-SET {'HOLDS' if R['bus_set_holds'] else 'FAILS'}**; entered {R['entered'] or 'none'}, "
      f"left {R['left'] or 'none'}; TIED (within B_V1/180 = {R['band']:.1f} MWh/MW of the boundary): "
      f"{', '.join(R['tied_sites']) or 'none'} (closest: {R['closest']}). Prediction (275 in, 163 out, bus set holds): "
      f"275 in {'✓' if R['pred_enters'] else '✗'}, 163 out {'✓' if R['pred_leaves'] else '✗'}, "
      f"bus set {'✓' if R['pred_bus_set'] else '✗'}. Kendall τ_b(v2, v3) = {R['tau_b']:.3f} (exact p {R['tau_p_exact']:.3g}).")
    for ids in (SEATED, SEATED_ALT):
        dd = dom[dom["objectives"] == "/".join(ids)]
        nd = dd[~dd["dominated"]]
        a(f"- **Dominance on {'/'.join(ids)}:** " + (
            "all 10 non-slate sites dominated by a slate site → slate exclusion justified on all seated objectives."
            if nd.empty else
            f"{len(nd)} of 10 non-slate sites NOT dominated: " + ", ".join(
                f"{r.site} (beats the closest slate site by {r.margin_bars:.2f} B on its best objective)"
                for r in nd.itertuples()) + " → disclosed, PI flag; E-D3 not reopened."))
    sl = loc.set_index("id")
    a("- **N1 against both bars** (63: perturbation ruler DISAGREES with Seed chatter, so B_N1^seed binds): "
      f"HL = {sl.loc['N1', 'HL']:+.0f} line-h → {sl.loc['N1', 'HL_over_B']:+.2f} B_pert (B = {sl.loc['N1', 'B_j']:.1f}) / "
      f"{sl.loc['N1', 'HL_over_B_seed']:+.2f} B_seed (B = {sl.loc['N1', 'B_seed']:.1f}); Holm p {sl.loc['N1', 'p_holm']:.3g} → "
      f"{sl.loc['N1', 'verdict']} under both ({sl.loc['N1', 'verdict_B_seed']} under B_seed).")
    flips = list(sl.index[sl["verdict"] != sl["verdict_B_seed"]])
    a("- **Seed-bar sensitivity (every id, `verdict_B_seed`):** " + (
        "no verdict changes." if not flips else "verdict changes for " + ", ".join(
            f"{j} ({sl.loc[j, 'verdict']} → {sl.loc[j, 'verdict_B_seed']}, {sl.loc[j, 'HL_over_B_seed']:+.2f} B_seed)"
            for j in flips) + "; the primary bar stays B_j (61 §3) except N1, whose binding bar is B_seed."))
    nE = sites["E1_verdict"].value_counts().to_dict()
    a(f"- **E1 per site vs G_site + G_base:** " + ", ".join(f"{k} {v}" for k, v in sorted(nE.items())) + ".")
    a(f"- **Replicate:** `{info['replicate']['new']}` overall.csv md5 = `{info['replicate']['ref']}` "
      f"(`{info['replicate']['overall_md5']}`) — no code/data drift since 11-06. SUSPECT rows: {info['n_suspect']} of 16 "
      f"(+ base {'SUSPECT' if info['base_suspect'] else 'ok'}); identity v3 on all 17 runs + base.")
    a("")
    a("## 1. Disclosures")
    a("")
    a("- PV/WIND confound: C holds one PV site (116); pv_pocket (30, 59, 142) is outside the primary contrast; far is all WIND. "
      "The WIND-only sensitivity (7 vs 5) is in §2.")
    a(f"- ω confound: ω = 180/gen_pmax spans {sites['omega_180'].min():.2f}–{sites['omega_180'].max():.2f}; "
      "116 (0.90) and 163 (0.97) are saturation rows; own-site relief at high ω is partly accounting reclassification (§4).")
    a(f"- Power floor: with 8 vs 5 the smallest exact two-sided p is {info['min_p_exact']:.5f} (complete separation); "
      f"Holm over {len(loc)} ids needs ≤ {ALPHA / len(loc):.5f} at its first step, so a LOCATIONAL read needs complete "
      "or near-complete separation of the 8 C sites from the 5 far sites.")
    a(f"- Moses exact interval: k = {info['moses'][0]}, achieved coverage {info['moses'][1]:.4f} (8 vs 5); "
      f"WIND-only k = {info['moses_wind'][0]}, coverage {info['moses_wind'][1]:.4f}. scipy's exact MW null assumes no "
      "ties; tied C-U pairs are counted per id (`n_tied_pairs`).")
    a("- B_j transferred from noise_v3 (61 §3, D2 structural zeros excluded); no replicate chatter is measured here. "
      "No ratio for any j is graded; V1 relief/MW is reported as a column.")
    a("- D2 (PEM utilization, a diagnostic) is not graded: base_v3 has no PEM, so D2 is 0/0 there and Δ_D2 is "
      "undefined; the Holm family is the other 23 ids with B_j > 0.")
    a("- Second bar: `analysis/noise_v3/ercot_noise_seed.json` (63, Gurobi-Seed chatter) gives B_seed per id; its "
      "B_pert is asserted equal to B_j. Dominance is invariant to per-objective bar scaling (only `margin_bars` uses B_j).")
    a("- Covariate Spearman ρ and the Kruskal–Wallis test are descriptive (no multiplicity correction).")
    a("")
    a("## 2. Tier contrast per graded id (d_s = Δ_j vs base_v3; C = pocket_120 ∪ wind_near, U = far)")
    a("")
    a(_tab(loc, ["id", "family", "B_j", "median_pocket_120", "median_wind_near", "median_pv_pocket", "median_far",
                 "HL", "HL_over_B", "moses_lo", "moses_hi", "r_rb", "p_exact", "p_holm", "n_tied_pairs", "verdict",
                 "wind_HL_over_B", "wind_p_exact", "kw_p", "B_seed", "HL_over_B_seed", "verdict_B_seed"]))
    a("")
    a("`why_not` per id is in `screening_v3_locational.csv`.")
    a("")
    a("## 3. Sites (Δ vs base_v3 at 180 MW; z = Δ/B_j)")
    a("")
    t = sites.reset_index().rename(columns={"index": "site"})
    a(_tab(t.sort_values(["tier", "site"]), ["site", "key", "tier", "unit_type", "bus", "omega_180", "relief_per_mw",
                                              "z_V1", "z_E1", "z_N1", "z_N4", "d_E1", "E1_gap_bound", "E1_verdict", "suspect"]))
    a("")
    a("## 4. ΔV1 decomposition (own-site parent row vs other sites; gen_summary)")
    a("")
    a(_tab(t.sort_values("relief_per_mw", ascending=False),
           ["site", "omega_180", "relief_V1_mwh", "own_dV1", "other_dV1", "own_share_of_relief", "twin_curtailment_mwh"]))
    a("")
    a("own_dV1 = Δ curtailment of the parent `<site>` row (its capacity shrinks by 180 MW); the `<site>_PEM` twin is "
      "is_pem = True and never in V1 (asserted). A large own share at high ω means the relief is mostly the twin's "
      "capacity leaving V1's books (accounting reclassification), not system-wide relief.")
    a("")
    a("## 5. Covariates (Spearman over the 16 sites; descriptive)")
    a("")
    keyc = crho[crho["id"].isin(list(dict.fromkeys(SEATED + SEATED_ALT)))]
    piv = keyc[keyc["covariate"].isin(["H_C_180_MWh", "base_v3_own_curtailment_mwh", "omega_180"])].pivot(
        index="id", columns="covariate", values="rho")
    pk = keyc[keyc["kind"] == "pocket PTDF"].groupby("id")["rho"].apply(lambda s: s.loc[s.abs().idxmax()] if s.notna().any() else np.nan)
    ot = keyc[keyc["kind"] == "PTDF"].groupby("id")["rho"].apply(lambda s: s.loc[s.abs().idxmax()] if s.notna().any() else np.nan)
    piv["max|rho| pocket PTDF"] = pk
    piv["max|rho| other congested PTDF"] = ot
    a(_tab(piv.reset_index(), ["id"] + list(piv.columns)))
    a("")
    a("Full table (23 ids × 47 covariates): `screening_v3_covariate_rho.csv`.")
    a("")
    a("## 6. Matched-MW ranking vs E-D3 slate")
    a("")
    a(_tab(rk.reset_index().rename(columns={"index": "site"}),
           ["site", "rank_v3", "rank_v2", "relief_per_mw_v3", "relief_per_mw_v2", "bus", "unit_type", "omega_180",
            "slate", "top6_v3", "TIED", "gap_to_boundary_bands"]))
    a("")
    a(f"v2 ranks are at ω ≈ 0.5 (pem = gen_pmax/2), v3 at a matched 180 MW, so a different order is expected from the "
      f"protocol alone. Tie band B_V1/180 = {R['band']:.1f} MWh/MW. E-D3 stands in every case.")
    a("")
    a("## 7. Dominance read (non-slate sites; z = Δ/B_j, all dir = min)")
    a("")
    a(_tab(dom, ["objectives", "site", "dominated", "dominated_by", "margin_bars", "z_V1", "z_E1"]
           + [c for c in ("z_N1", "z_N4") if c in dom.columns]))
    a("")
    a("## 8. Provenance")
    a("")
    a(f"- Rows: {', '.join(f'{s}={k}' for s, k in sites['key'].items())}; base `base_v3:1` (G_base = {_g(info['G_base'])} $).")
    a("- Seen: screening_v3 rows 1–11, wave D L180 rows 3/6/9/12/15/18, base_v3:1, ercot_noise.json, ercot_noise_seed.json, "
      "the committed Part B "
      "outputs. Not read: random_E, methods_E, any n0_E extract.")
    open(path, "w").write("\n".join(L) + "\n")


def part_c_block(loc, rk_info, dom, info):
    s = loc.set_index("id")
    nl = list(s.index[s["verdict"] == "LOCATIONAL"])
    lines = [BEGIN, "", "### Part C — screening_v3 (landed 2026-11-18; `SCREENING_V3.md`). Changes no seat.", "",
             "Seats stay V1 / E1 / R EMPTY / N1 (M = 3). Per id, columns `C_HL_over_B`, `C_holm_p`, `C_locational` "
             "in `pool_ed1b_combined.csv`.", ""]
    lines.append("- LOCATIONAL (C vs far): " + (", ".join(f"{j} ({s.loc[j, 'HL_over_B']:+.2f} B, Holm p {s.loc[j, 'p_holm']:.3g})"
                                                       for j in nl) or "none") + ".")
    lines.append("- Seated: " + "; ".join(f"{j} {s.loc[j, 'HL_over_B']:+.2f} B, Holm p {s.loc[j, 'p_holm']:.3g} → {s.loc[j, 'verdict']}"
                                         for j in dict.fromkeys(SEATED + SEATED_ALT)) + ".")
    lines.append(f"- N1 vs B_seed {s.loc['N1', 'B_seed']:.1f} (binding, 63): {s.loc['N1', 'HL_over_B_seed']:+.2f} B_seed → "
                 f"{s.loc['N1', 'verdict_B_seed']}.")
    lines.append(f"- Bus set: top 6 = {', '.join(rk_info['top6'])} → SLATE BUS-SET {'HOLDS' if rk_info['bus_set_holds'] else 'FAILS'} "
                 f"(entered {rk_info['entered'] or 'none'}, left {rk_info['left'] or 'none'}; TIED {rk_info['tied_sites'] or 'none'}).")
    for ids in (SEATED, SEATED_ALT):
        nd = dom[(dom["objectives"] == "/".join(ids)) & (~dom["dominated"])]
        lines.append(f"- Dominance {'/'.join(ids)}: " + ("all non-slate sites dominated" if nd.empty else
                                                          "not dominated: " + ", ".join(nd["site"]) + " (PI flag)") + ".")
    lines += ["", END]
    return "\n".join(lines)


def append_part_c(loc, rk_info, dom, info, md_path=STANDINGS_MD, csv_path=COMBINED):
    t = open(md_path).read()
    blk = part_c_block(loc, rk_info, dom, info)
    if BEGIN in t:
        pre, rest = t.split(BEGIN, 1)
        t = pre + blk + rest.split(END, 1)[1]
    else:
        assert t.count("\n## Deviations") == 1
        t = t.replace("\n## Deviations", "\n" + blk + "\n\n## Deviations")
    open(md_path, "w").write(t)
    comb = pd.read_csv(csv_path, dtype=str, keep_default_na=False)
    comb = comb[[c for c in comb.columns if not c.startswith("C_")]]
    s = loc.set_index("id")
    comb["C_HL_over_B"] = [f"{s.loc[j, 'HL_over_B']:.3f}" if j in s.index else "n/a (B_j = 0)" for j in comb["id"]]
    comb["C_holm_p"] = [f"{s.loc[j, 'p_holm']:.4g}" if j in s.index else "n/a" for j in comb["id"]]
    comb["C_locational"] = [s.loc[j, "verdict"] if j in s.index else "n/a" for j in comb["id"]]
    comb.to_csv(csv_path, index=False)


def run(out_dir=po.POOL, figs_dir=FIGS, make_figs=True, append=True):
    sites, loc, crho, rk, dom, info, B = compute()
    sites.index.name = "site"
    rk.index.name = "site"
    sites.to_csv(os.path.join(out_dir, "screening_v3_sites.csv"))
    loc.to_csv(os.path.join(out_dir, "screening_v3_locational.csv"), index=False)
    crho.to_csv(os.path.join(out_dir, "screening_v3_covariate_rho.csv"), index=False)
    rk.to_csv(os.path.join(out_dir, "screening_v3_ranking.csv"))
    dom.to_csv(os.path.join(out_dir, "screening_v3_dominance.csv"), index=False)
    write_md(os.path.join(out_dir, "SCREENING_V3.md"), sites, loc, crho, rk, dom, info, B)
    if make_figs:
        figures(out_dir, figs_dir)
    if append:
        append_part_c(loc, info["rank"], dom, info)
    return sites, loc, crho, rk, dom, info


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--no-figs", action="store_true")
    a = ap.parse_args(argv)
    _, loc, _, _, dom, info = run(make_figs=not a.no_figs)
    print(loc[["id", "HL_over_B", "p_exact", "p_holm", "verdict"]].to_string(index=False))
    print(json.dumps(info["rank"], indent=1, default=str))
    print(dom[~dom["dominated"]].to_string(index=False))


if __name__ == "__main__":
    main()
