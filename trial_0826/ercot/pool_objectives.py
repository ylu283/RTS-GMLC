"""Prompt 57 Part A: the ERCOT objective-pool extractor (zero simulation).

One row per v2 run -> analysis/pool/pool_wide_v2.csv (raw values) and
pool_delta_v2.csv (value - base_2019_v2:1). Every candidate of prompt 57
section 2 is computed by the exact column name pinned in
analysis/pool/pool_definitions.json (the FROZEN definitions file; this
module reads it and never writes it).

Reuses compute_objectives (co.metrics, co.thermal_h2, co.gen_summary) from
the same directory. The frozen outputs objectives_t1_v2.csv and
noise_ruler_v2_v2.json are read for the regression check and the nuclear h2
copy; they are never rewritten.

Red lines kept here:
- Prescient `Price` / `Average price` / `Cumulative average price` are
  cost-per-MWh columns. They are not read as prices anywhere in this file.
- `--full`-only candidates (E8, E9, N5) are NaN on slim extracts, never
  imputed.
- pem_mw comes from the design matrix (omega x gen_pmax) or the
  retrofit_gen_dict, never from gen_summary.
- A2 names zero-variance candidates DEAD with max |value| as the evidence.
- A3 (first cut, n = 16) names clusters and drops nothing (NON-USE clause).

pandas-3 safe: no chained assignment, explicit copies, string keys.
Tested locally under pandas 2.3.3; PCM_ERCOT (pandas 3.0.5) is the target.
"""

import hashlib
import json
import os
import sys
import warnings

import numpy as np
import pandas as pd

# compute_objectives.gen_summary fillna(False) on an object column: pandas 2.x
# warns about a future downcasting change; the result is the same bool column
# under pandas 3 (fillna keeps object, astype(bool) converts). Silence it here.
warnings.filterwarnings("ignore", message="Downcasting object dtype arrays",
                        category=FutureWarning)

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import compute_objectives as co  # noqa: E402

EXTR = os.path.join(HERE, "extracts")
WAVES = os.path.join(HERE, "waves")
DATA = os.path.join(HERE, "data", "ercot123_2019_v2")
POOL = os.path.join(HERE, "analysis", "pool")
DEFS_PATH = os.path.join(POOL, "pool_definitions.json")
FROZEN_T1 = os.path.join(HERE, "analysis", "selection", "objectives_t1_v2.csv")
BASE_KEY = "base_2019_v2:1"
HOURS = 8760

V2_RUNS = ([("base_2019_v2", i) for i in (1, 2, 3)]
           + [("screening_v2/ercot", i) for i in range(1, 13)]
           + [("screening_v2/topup", i) for i in range(1, 8)]
           + [("selection_t1_v2", i) for i in range(3, 12)])
FIRST_CUT_KEYS = ([f"screening_v2/ercot:{i}" for i in range(1, 10)]
                  + [f"screening_v2/topup:{i}" for i in range(1, 8)])

KEY_COLS = ["wave", "index", "key", "site", "unit_type", "bus", "pem_mw",
            "omega", "gen_pmax", "replicate_of", "distinct_design_id",
            "full_extract"]
# candidate id -> output column (the id itself); extra non-candidate columns
# are prefixed with the id they belong to.
CAND_IDS = ["V1", "V2", "V3", "E1", "E2", "E3", "E4", "E5", "E6", "E7", "E8",
            "E9", "R1", "R2", "R3", "R4", "R5", "R6", "R7", "R8", "N1", "N2",
            "N3", "N4", "N5", "X1", "D1", "D2"]
LEGACY = ["true_curt", "h2", "var_cost", "reserve", "onoffs", "total_cost",
          "fixed_cost", "gen1_starts", "gen1_unit_cost"]
# legacy name -> candidate id (regression + first-cut naming)
LEGACY_TO_ID = {"true_curt": "V1", "var_cost": "E3", "reserve": "R2",
                "onoffs": "R4", "total_cost": "E1", "fixed_cost": "E2",
                "h2": "D1", "gen1_starts": "D3_gen1_starts"}


# --------------------------------------------------------------------------
# definitions, paths, design matrices
# --------------------------------------------------------------------------
def load_defs(path=DEFS_PATH):
    with open(path) as f:
        return json.load(f)


def run_dir(key, extr=EXTR):
    wave, idx = key.split(":")
    return os.path.join(extr, wave, f"run_index_{idx}")


def is_full(d):
    return os.path.isfile(os.path.join(d, "bus_lmps.csv.gz"))


def design_matrix(wave, waves=WAVES):
    dm = pd.read_csv(os.path.join(waves, wave, "design_matrix.csv"),
                     dtype={"oat_site": str, "replicate_of": str,
                            "unit_type": str})
    return dm


def design_row(wave, idx, waves=WAVES):
    dm = design_matrix(wave, waves)
    r = dm[dm["index"].astype(int) == int(idx)]
    if len(r) != 1:
        raise KeyError(f"{wave}:{idx} not in design_matrix ({len(r)} rows)")
    r = r.iloc[0]

    def _f(v):
        return float(v) if pd.notna(v) else np.nan
    return {"site": str(r["oat_site"]),
            "unit_type": (str(r["unit_type"]) if pd.notna(r["unit_type"]) else ""),
            "bus": _f(r["bus"]), "omega": _f(r["omega"]),
            "gen_pmax": _f(r["gen_pmax"]),
            "replicate_of": (str(r["replicate_of"])
                             if pd.notna(r["replicate_of"]) else "")}


def pem_mw(wave, idx, drow, waves=WAVES):
    """omega x gen_pmax; __ALL__ row = sum over the retrofit dict; base = 0.
    Never gen_summary.pmax_mw."""
    site = drow["site"]
    if site == "__BASE_REPLICATE__":
        return 0.0
    if site == "__ALL__":
        with open(os.path.join(waves, wave, f"retrofit_gen_dict_{idx}.json")) as f:
            dct = json.load(f)
        return float(sum(v["PEM_fraction"] * v["gen_pmax"] for v in dct.values()))
    return float(drow["omega"] * drow["gen_pmax"])


def norm_replicate(wave, val, names):
    """v1 wave names -> v2 names; bare index -> same wave; 'base' -> base run 1."""
    if val is None or val == "" or (isinstance(val, float) and np.isnan(val)):
        return ""
    s = str(val).strip()
    if s in names and ":" in names[s]:          # 'base' -> 'base_2019_v2:1'
        return names[s]
    if ":" not in s:
        return f"{wave}:{int(float(s))}"
    w, i = s.split(":")
    return f"{names.get(w, w)}:{int(float(i))}"


# --------------------------------------------------------------------------
# network data helpers
# --------------------------------------------------------------------------
def pocket_lines(data_dir=DATA, bus=120):
    br = pd.read_csv(os.path.join(data_dir, "branch.csv"))
    m = (br["From Bus"].astype(int) == bus) | (br["To Bus"].astype(int) == bus)
    return [str(u) for u in br.loc[m, "UID"]]


def bus_name(data_dir=DATA, bus_id=120):
    b = pd.read_csv(os.path.join(data_dir, "bus.csv"))
    r = b[b["Bus ID"].astype(int) == bus_id]
    assert len(r) == 1, f"bus {bus_id}: {len(r)} rows"
    return str(r["Bus Name"].iloc[0])


def bus_id_to_name(data_dir=DATA):
    b = pd.read_csv(os.path.join(data_dir, "bus.csv"))
    return {str(int(i)): str(n) for i, n in zip(b["Bus ID"], b["Bus Name"])}


def hourly_load(data_dir=DATA):
    """REAL_TIME_load.csv -> frame indexed by (Date, Hour) with columns = bus
    ID strings. Hour = Period - 1. Year-end padding rows are kept here and
    dropped by the inner join with bus_lmps."""
    L = pd.read_csv(os.path.join(data_dir, "REAL_TIME_load.csv"))
    date = (L["Year"].astype(int).astype(str) + "-"
            + L["Month"].astype(int).map("{:02d}".format) + "-"
            + L["Day"].astype(int).map("{:02d}".format))
    hour = L["Period"].astype(int) - 1
    bus_cols = [c for c in L.columns if c not in ("Year", "Month", "Day", "Period")]
    out = L[bus_cols].copy()
    out.columns = [str(c) for c in bus_cols]
    out.index = pd.MultiIndex.from_arrays([date.to_numpy(), hour.to_numpy()],
                                          names=["Date", "Hour"])
    return out


# --------------------------------------------------------------------------
# per-run candidates
# --------------------------------------------------------------------------
def lmp_candidates(d, data_dir, defs, pocket_bus=120):
    """E8, E9, N5 (+ N5 unweighted check) from bus_lmps.csv.gz; NaN if slim."""
    out = {"E8": np.nan, "E9": np.nan, "N5": np.nan,
           "N5_unweighted_check": np.nan, "E9_lmp_max": np.nan}
    p = os.path.join(d, "bus_lmps.csv.gz")
    if not os.path.isfile(p):
        return out
    thr = float(defs["thresholds"]["lmp_scarcity_threshold_usd_per_mwh"])
    lm = pd.read_csv(p, usecols=["Date", "Hour", "Bus", "LMP"])
    lm["Bus"] = lm["Bus"].astype(str)
    lmp = lm["LMP"].astype(float)
    out["E8"] = float(lmp.std(ddof=1))
    out["E9"] = int((lmp >= thr).sum())
    out["E9_lmp_max"] = float(lmp.max())
    piv = lm.pivot(index=["Date", "Hour"], columns="Bus", values="LMP")
    knox = bus_name(data_dir, pocket_bus)
    assert knox in piv.columns, f"{knox!r} not among bus_lmps Bus names"
    id2name = bus_id_to_name(data_dir)
    load = hourly_load(data_dir)
    load = load.rename(columns=id2name)
    common_buses = [c for c in piv.columns if c in load.columns]
    assert len(common_buses) == piv.shape[1], (
        f"bus-name join: {len(common_buses)} of {piv.shape[1]} LMP buses have a load column")
    joined_idx = piv.index.intersection(load.index)
    assert len(joined_idx) == len(piv), (
        f"(Date, Hour) join: {len(joined_idx)} of {len(piv)} LMP hours matched")
    P = piv.loc[joined_idx, common_buses]
    W = load.loc[joined_idx, common_buses].astype(float)
    wmean = (P.to_numpy() * W.to_numpy()).sum(axis=1) / W.to_numpy().sum(axis=1)
    out["N5"] = float((P[knox].to_numpy() - wmean).mean())
    out["N5_unweighted_check"] = float((P[knox].to_numpy() - P.to_numpy().mean(axis=1)).mean())
    return out


def frozen_h2(key, frozen_csv=FROZEN_T1):
    wave, idx = key.split(":")
    fr = pd.read_csv(frozen_csv, dtype={"index": str, "wave": str})
    r = fr[(fr["wave"] == wave) & (fr["index"] == str(idx))]
    if len(r) != 1:
        return np.nan
    return float(r["h2"].iloc[0])


def pool_row(key, extr=EXTR, waves=WAVES, data_dir=DATA, defs=None,
             frozen_csv=FROZEN_T1, pocket_bus=120):
    """All section-2 candidates + SUSPECT inputs + G_run for one run."""
    defs = defs or load_defs()
    wave, idx = key.split(":")
    d = run_dir(key, extr)
    drow = design_row(wave, idx, waves)
    nuclear = drow["unit_type"] == "NUC"
    full = is_full(d)

    o = pd.read_csv(os.path.join(d, "overall.csv")).iloc[0]
    daily = pd.read_csv(os.path.join(d, "daily_summary.csv"))
    g = co.gen_summary(d)
    ch = pd.read_csv(os.path.join(d, "committed_hourly.csv"))
    ls = pd.read_csv(os.path.join(d, "line_summary.csv"))
    ls["Line"] = ls["Line"].astype(str)
    rq = pd.read_csv(os.path.join(d, "ruc_quality.csv"))

    # legacy 9 columns via compute_objectives (h2 for nuclear handled below)
    co_extr_saved = co.EXTR
    co.EXTR = extr
    try:
        leg = co.metrics(key, nuclear=False)
        h2_source = "twin_curtailment"
        if nuclear:
            if os.path.isfile(os.path.join(d, "thermal.csv.gz")):
                leg["h2"] = co.thermal_h2(key, site=drow["site"],
                                          pmax=float(drow["gen_pmax"]))
                h2_source = "thermal_rule"
            else:
                leg["h2"] = frozen_h2(key, frozen_csv)
                h2_source = ("frozen_t1_v2" if np.isfinite(leg["h2"])
                             else "unavailable")
    finally:
        co.EXTR = co_extr_saved

    vre = (~g["is_pem"]) & g["unit_type"].isin(["WIND", "PV"])
    twin = g["is_pem"]
    vre_avail = float((g.loc[vre, "output_mwh"] + g.loc[vre, "curtailment_mwh"]).sum())
    pmw = pem_mw(wave, idx, drow, waves)

    ef = defs["emission_factors_t_per_mwh"]
    non_pem = g.loc[~twin, ["unit_type", "output_mwh"]].copy()
    non_pem["ef"] = non_pem["unit_type"].map(
        {k: float(v) for k, v in ef.items() if isinstance(v, (int, float))})
    assert non_pem["ef"].notna().all(), (
        f"{key}: unit_type without an EF: {sorted(non_pem.loc[non_pem.ef.isna(), 'unit_type'].unique())}")
    is_gas = non_pem["unit_type"] == "CT"
    co2 = float((non_pem["output_mwh"] * non_pem["ef"]).sum())
    co2_gas = float((non_pem.loc[is_gas, "output_mwh"] * non_pem.loc[is_gas, "ef"]).sum())

    plines = pocket_lines(data_dir, pocket_bus)
    lsi = ls.set_index("Line")
    n4_split = {f"N4_{u}": (int(lsi.loc[u, "hours_ge_99pct"]) if u in lsi.index else 0)
                for u in plines}

    g1 = g[g["Generator"] == "1"]
    g93 = g[g["Generator"] == "93"]
    s1_resid = abs(float(o["Total costs"]) - float(o["Total fixed costs"])
                   - float(o["Total generation costs"]))
    status = rq["status"].astype(str)
    gap = rq["final_gap_pct"].astype(float)
    cost = rq["ruc_cost"].astype(float)

    row = {
        "wave": wave, "index": int(idx), "key": key, "site": drow["site"],
        "unit_type": drow["unit_type"], "bus": drow["bus"], "pem_mw": pmw,
        "omega": drow["omega"], "gen_pmax": drow["gen_pmax"],
        "replicate_of": norm_replicate(wave, drow["replicate_of"],
                                       defs["v1_to_v2_wave_names"]),
        "full_extract": bool(full),
        # V
        "V1": leg["true_curt"],
        "V2": float(o["Overall renewables penetration rate"]),
        "V3": float(g.loc[twin, "output_mwh"].sum()) / vre_avail if vre_avail > 0 else np.nan,
        # E
        "E1": leg["total_cost"], "E2": leg["fixed_cost"], "E3": leg["var_cost"],
        "E4": float(o["Total payments"]),
        "E5": float(o["Total uplift payments"]),
        "E6": float(daily["Renewables energy payments"].astype(float).sum()),
        "E7": float(o["Total energy payments"]) / float(o["Total demand"]),
        "E8_slim_daily_settle_sd": float((daily["Total energy payments"].astype(float)
                                          / daily["Demand"].astype(float)).std(ddof=1)),
        # R
        "R1": float(o["Total load shedding"]), "R2": leg["reserve"],
        "R3": float(o["Total over generation"]), "R4": leg["onoffs"],
        "R5": float(o["Total sum on/off ramps"]),
        "R6": float(o["Total sum nominal ramps"]),
        "R7": float(ch["committed_mw"].astype(float).sum()),
        "R8": int(ch["num_committed"].astype(int).sum()),
        # N
        "N1": int(ls["hours_ge_99pct"].astype(int).sum()),
        "N2": int((ls["hours_ge_99pct"].astype(int) > 0).sum()),
        "N3": float(ls["sum_violation"].astype(float).sum()),
        "N4": int(sum(n4_split.values())),
        **n4_split,
        # X
        "X1": co2, "X1_ef_lo": 0.8 * co2, "X1_ef_hi": 1.2 * co2,
        "X1_gas_lo": co2 - 0.2 * co2_gas, "X1_gas_hi": co2 + 0.2 * co2_gas,
        # D
        "D1": leg["h2"], "h2_source": h2_source,
        "D2": (leg["h2"] / (pmw * HOURS)) if pmw > 0 and np.isfinite(leg["h2"]) else np.nan,
        "D3_gen1_starts": float(g1["starts"].iloc[0]) if len(g1) else np.nan,
        "D3_gen93_starts": float(g93["starts"].iloc[0]) if len(g93) else np.nan,
        "gen1_unit_cost": leg["gen1_unit_cost"],
        # SUSPECT inputs (plan 1.2)
        "S1_resid_usd": s1_resid,
        "S1_ok": bool(s1_resid <= float(defs["thresholds"]["suspect_S1_abs_resid_usd"])),
        "n_ruc": int(len(rq)), "n_ruc_optimal": int((status == "OPTIMAL").sum()),
        "S2_ok": bool((status == "OPTIMAL").all()),
        "is_nuclear_design": bool(nuclear),
        # MIP-gap cost bound (A4b)
        "G_run_usd": float((gap / 100.0 * cost).sum()),
        "ruc_cost_sum_usd": float(cost.sum()),
        "max_gap_pct": float(gap.max()),
        "overall_md5": hashlib.md5(open(os.path.join(d, "overall.csv"), "rb").read()).hexdigest(),
    }
    row.update(lmp_candidates(d, data_dir, defs, pocket_bus))
    return row


def build_pool(keys=None, extr=EXTR, waves=WAVES, data_dir=DATA, defs=None,
               frozen_csv=FROZEN_T1, verbose=True):
    defs = defs or load_defs()
    keys = keys or [f"{w}:{i}" for w, i in V2_RUNS]
    rows = []
    for k in keys:
        if verbose:
            print(f"  pool_row {k}", flush=True)
        rows.append(pool_row(k, extr, waves, data_dir, defs, frozen_csv))
    wide = pd.DataFrame(rows)
    # distinct designs = byte-identical overall.csv groups, numbered by first occurrence
    ids = {}
    for h in wide["overall_md5"]:
        if h not in ids:
            ids[h] = f"D{len(ids) + 1:02d}"
    wide["distinct_design_id"] = wide["overall_md5"].map(ids)
    # S3: non-nuclear -> starts of 1 and 93 are 0; any design -> equal across exact replicates
    s3 = []
    for _, r in wide.iterrows():
        grp = wide[wide["distinct_design_id"] == r["distinct_design_id"]]
        eq = (grp["D3_gen1_starts"].nunique(dropna=False) == 1
              and grp["D3_gen93_starts"].nunique(dropna=False) == 1)
        zero = (r["D3_gen1_starts"] == 0) and (r["D3_gen93_starts"] == 0)
        s3.append(bool(eq and (zero or r["is_nuclear_design"])))
    wide["S3_ok"] = s3
    wide["suspect"] = ~(wide["S1_ok"] & wide["S2_ok"] & wide["S3_ok"])
    # replicate_of consistency with the md5 groups
    for _, r in wide.iterrows():
        if r["replicate_of"]:
            ref = wide[wide["key"] == r["replicate_of"]]
            if len(ref) and ref["distinct_design_id"].iloc[0] != r["distinct_design_id"]:
                raise AssertionError(f"{r['key']} declared replicate of {r['replicate_of']} but overall.csv differs")
    front = KEY_COLS + ["h2_source", "is_nuclear_design"]
    rest = [c for c in wide.columns if c not in front]
    return wide[front + rest]


def deltas(wide, base_key=BASE_KEY):
    """value - base for every numeric candidate column; keys kept."""
    num = [c for c in wide.columns
           if c not in KEY_COLS and pd.api.types.is_numeric_dtype(wide[c])
           and wide[c].dtype != bool and not c.startswith(("S1_", "n_ruc", "G_run", "ruc_cost", "max_gap"))]
    base = wide[wide["key"] == base_key]
    assert len(base) == 1, f"base {base_key}: {len(base)} rows"
    b = base.iloc[0]
    out = wide[KEY_COLS].copy()
    for c in num:
        out[c] = wide[c].astype(float) - float(b[c])
    return out


def regression_vs_frozen(wide, frozen_csv=FROZEN_T1, tol=1e-6):
    """All 9 legacy columns equal the frozen objectives_t1_v2.csv to tol on its
    16 rows, except h2 on the slim nuclear rows (copied, h2_source frozen)."""
    fr = pd.read_csv(frozen_csv, dtype={"index": str, "wave": str})
    col = {"true_curt": "V1", "h2": "D1", "var_cost": "E3", "reserve": "R2",
           "onoffs": "R4", "total_cost": "E1", "fixed_cost": "E2",
           "gen1_starts": "D3_gen1_starts", "gen1_unit_cost": "gen1_unit_cost"}
    w = wide.set_index("key")
    report = []
    for _, r in fr.iterrows():
        k = f"{r['wave']}:{int(r['index'])}"
        for lc, pc in col.items():
            a, b = float(r[lc]), float(w.loc[k, pc])
            copied = (lc == "h2" and w.loc[k, "h2_source"] == "frozen_t1_v2")
            report.append({"key": k, "legacy": lc, "frozen": a, "recomputed": b,
                           "abs_diff": abs(a - b), "copied_from_frozen": copied,
                           "ok": bool(abs(a - b) <= tol)})
    rep = pd.DataFrame(report)
    assert len(rep) == 16 * 9, len(rep)
    return rep


# --------------------------------------------------------------------------
# A2 dead list
# --------------------------------------------------------------------------
def dead_list(wide, cand_ids=CAND_IDS):
    rows = []
    for c in cand_ids:
        v = wide[c].astype(float)
        fin = v[np.isfinite(v)]
        n = int(len(fin))
        if n == 0:
            status = "NO VALUE"
        elif n == 1:
            status = "UNDETERMINED (1 value)"
        elif float(fin.max() - fin.min()) == 0.0:
            status = "DEAD"
        else:
            status = "ALIVE"
        rows.append({"id": c, "status": status, "n_values": n,
                     "max_abs_value": float(fin.abs().max()) if n else np.nan,
                     "min": float(fin.min()) if n else np.nan,
                     "max": float(fin.max()) if n else np.nan,
                     "range": float(fin.max() - fin.min()) if n else np.nan})
    return pd.DataFrame(rows)


def replicate_zero_check(wide, cand_ids=CAND_IDS):
    """Within byte-identical groups every candidate delta is exactly 0."""
    rows = []
    for gid, grp in wide.groupby("distinct_design_id"):
        if len(grp) < 2:
            continue
        for c in cand_ids:
            v = grp[c].astype(float).dropna()
            if len(v) >= 2:
                rows.append({"distinct_design_id": gid, "keys": "|".join(grp["key"]),
                             "id": c, "max_abs_within_delta": float(v.max() - v.min())})
    return pd.DataFrame(rows)


# --------------------------------------------------------------------------
# A3 first cut (n = 16; NON-USE)
# --------------------------------------------------------------------------
def partial_spearman(x, y, z):
    """Rank-residual partial Spearman (pool_correlations.csv convention)."""
    from scipy import stats
    rx, ry, rz = (stats.rankdata(np.asarray(v, float)) for v in (x, y, z))
    ex = rx - np.polyval(np.polyfit(rz, rx, 1), rz)
    ey = ry - np.polyval(np.polyfit(rz, ry, 1), rz)
    return float(np.corrcoef(ex, ey)[0, 1])


def first_cut_candidates(delta16, defs, dead):
    """Directed + '-' candidates with finite, non-constant deltas on the 16 rows."""
    deadset = set(dead.loc[dead["status"] != "ALIVE", "id"])
    cands = defs["candidates"]
    out = []
    for cid in CAND_IDS:
        if cid in deadset:
            continue
        v = delta16[cid].astype(float)
        if not np.isfinite(v).all() or float(v.max() - v.min()) == 0.0:
            continue
        out.append(cid)
    # D3 starts are constant 0 on the 16 rows (checked, excluded above)
    return out, cands


def oriented(delta16, ids, defs):
    """max candidates x (-1); '-' kept raw (shown, never clustered)."""
    O = pd.DataFrame(index=delta16.index)
    for cid in ids:
        sgn = -1.0 if defs["candidates"][cid]["dir"] == "max" else 1.0
        O[cid] = delta16[cid].astype(float) * sgn
    return O


def spearman_matrices(O, pmax):
    from scipy import stats
    ids = list(O.columns)
    n = len(ids)
    raw = np.eye(n)
    par = np.eye(n)
    for i in range(n):
        for j in range(i + 1, n):
            r = float(stats.spearmanr(O[ids[i]], O[ids[j]]).statistic)
            p = partial_spearman(O[ids[i]], O[ids[j]], pmax)
            raw[i, j] = raw[j, i] = r
            par[i, j] = par[j, i] = p
    return (pd.DataFrame(raw, index=ids, columns=ids),
            pd.DataFrame(par, index=ids, columns=ids))


def complete_linkage_clusters(M, directed_ids, rho_min=0.90):
    """Clusters where EVERY pair has rho_or >= rho_min (complete linkage at
    distance 1 - rho_min), on directed candidates only."""
    from scipy.cluster.hierarchy import fcluster, linkage
    from scipy.spatial.distance import squareform
    ids = [c for c in M.columns if c in directed_ids]
    if len(ids) < 2:
        return []
    sub = M.loc[ids, ids].to_numpy()
    D = np.clip(1.0 - sub, 0.0, 2.0)
    np.fill_diagonal(D, 0.0)
    Z = linkage(squareform(D, checks=False), method="complete")
    lab = fcluster(Z, t=1.0 - rho_min + 1e-12, criterion="distance")
    clusters = {}
    for cid, l in zip(ids, lab):
        clusters.setdefault(int(l), []).append(cid)
    return [sorted(v) for v in clusters.values() if len(v) >= 2]


def leaf_order(M):
    from scipy.cluster.hierarchy import leaves_list, linkage
    from scipy.spatial.distance import squareform
    D = np.clip(1.0 - M.to_numpy(), 0.0, 2.0)
    np.fill_diagonal(D, 0.0)
    Z = linkage(squareform(D, checks=False), method="complete")
    return [M.columns[i] for i in leaves_list(Z)], Z


def scale_free_S(delta16, ids):
    """S = range / mean |delta| over the 16 rows (descriptor only: one size per site)."""
    rows = []
    for cid in ids:
        v = delta16[cid].astype(float)
        m = float(v.abs().mean())
        rows.append({"id": cid, "range": float(v.max() - v.min()), "mean_abs_delta": m,
                     "S_firstcut": (float(v.max() - v.min()) / m) if m > 0 else np.nan,
                     "n_positive": int((v > 0).sum()), "n_negative": int((v < 0).sum()),
                     "n_zero": int((v == 0).sum())})
    return pd.DataFrame(rows)


def first_cut(wide, defs, dead, keys=FIRST_CUT_KEYS, base_key=BASE_KEY):
    delta = deltas(wide, base_key).set_index("key")
    d16 = delta.loc[keys].copy()
    pmax = wide.set_index("key").loc[keys, "gen_pmax"].astype(float)
    n_bus120 = int((wide.set_index("key").loc[keys, "bus"].astype(float) == 120).sum())
    ids, cands = first_cut_candidates(d16, defs, dead)
    directed = [c for c in ids if cands[c]["dir"] in ("min", "max")]
    O = oriented(d16, ids, defs)
    raw, par = spearman_matrices(O, pmax)
    long = []
    for i, a in enumerate(ids):
        for b in ids[i + 1:]:
            long.append({"pair": f"{a}|{b}", "a": a, "b": b,
                         "a_dir": cands[a]["dir"], "b_dir": cands[b]["dir"],
                         "both_directed": a in directed and b in directed,
                         "spearman_raw_oriented": round(float(raw.loc[a, b]), 4),
                         "spearman_partial_pmax_oriented": round(float(par.loc[a, b]), 4),
                         "n": len(keys), "n_bus120": n_bus120})
    long = pd.DataFrame(long)
    thr = 0.90
    clusters = {"raw": complete_linkage_clusters(raw, directed, thr),
                "partial_pmax": complete_linkage_clusters(par, directed, thr),
                "rho_min": thr, "directed_ids": directed,
                "shown_undirected": [c for c in ids if c not in directed]}
    S = scale_free_S(d16, ids)
    return {"ids": ids, "directed": directed, "raw": raw, "partial": par,
            "long": long, "clusters": clusters, "S": S, "n": len(keys),
            "n_bus120": n_bus120, "delta16": d16}


def plot_clustermap(raw, par, path, defs, title_note):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from scipy.cluster.hierarchy import dendrogram
    plt.rcParams.update({"font.size": 18, "font.weight": "bold",
                         "axes.labelweight": "bold", "axes.titleweight": "bold",
                         "text.parse_math": False})
    order, Z = leaf_order(raw)
    cands = defs["candidates"]

    def lab(c):
        d = cands[c]["dir"]
        return f"{c} ({'-' if d == '-' else d})"
    labels = [lab(c) for c in order]
    n = len(order)
    fig = plt.figure(figsize=(max(22, 1.05 * n + 6) * 1.9, max(13, 0.9 * n + 5)))
    gs = fig.add_gridspec(2, 3, height_ratios=[1, 6], width_ratios=[20, 20, 1],
                          hspace=0.12, wspace=0.25)
    axd = fig.add_subplot(gs[0, 0])
    dendrogram(Z, ax=axd, labels=None, no_labels=True, color_threshold=0.10,
               above_threshold_color="0.4")
    axd.set_ylabel("1 - rho", fontsize=18, fontweight="bold")
    axd.tick_params(axis="y", labelsize=16)
    for t in axd.get_yticklabels():
        t.set_fontweight("bold")
    axd.set_title("complete linkage (raw oriented Spearman); red line = rho 0.90",
                  fontsize=18, fontweight="bold")
    axd.axhline(0.10, color="red", lw=1.5, ls="--")
    axd.spines[["top", "right"]].set_visible(False)
    fig.add_subplot(gs[0, 1]).axis("off")
    axes = [fig.add_subplot(gs[1, 0]), fig.add_subplot(gs[1, 1])]
    cax = fig.add_subplot(gs[1, 2])
    im = None
    for ax, M, ttl in zip(axes, (raw, par),
                          ("raw oriented Spearman (n = 16)",
                           "gen_pmax-partialled (rank residual)")):
        A = M.loc[order, order].to_numpy()
        im = ax.imshow(A, vmin=-1, vmax=1, cmap="RdBu_r", aspect="equal")
        ax.set_xticks(range(n))
        ax.set_yticks(range(n))
        ax.set_xticklabels(labels, rotation=90, fontsize=18, fontweight="bold")
        ax.set_yticklabels(labels, fontsize=18, fontweight="bold")
        ax.set_title(ttl, fontsize=20, fontweight="bold")
        ax.set_xlabel("candidate (oriented: smaller is better)", fontsize=18, fontweight="bold")
        ax.set_ylabel("candidate", fontsize=18, fontweight="bold")
        for i in range(n):
            for j in range(n):
                v = A[i, j]
                ax.text(j, i, f"{v:+.2f}", ha="center", va="center", fontsize=11,
                        fontweight="bold", color="white" if abs(v) > 0.6 else "black")
    cb = fig.colorbar(im, cax=cax)
    cb.set_label("rho (oriented)", fontsize=18, fontweight="bold")
    cb.ax.tick_params(labelsize=16)
    for t in cb.ax.get_yticklabels():
        t.set_fontweight("bold")
    fig.suptitle(f"Prompt 57 A3 first cut: delta vs base over 16 single-site screening_v2 rows. "
                 f"NON-USE: names clusters, drops nothing. {title_note}",
                 fontsize=18, fontweight="bold", y=0.995)
    fig.savefig(path, dpi=110, bbox_inches="tight")
    plt.close(fig)


# --------------------------------------------------------------------------
# A4b MIP-gap bound table
# --------------------------------------------------------------------------
def gap_table(wide, base_key=BASE_KEY, ref_median=11.3e6):
    w = wide.set_index("key")
    Gb = float(w.loc[base_key, "G_run_usd"])
    rows = []
    for k, r in w.iterrows():
        bound = float(r["G_run_usd"]) + Gb
        out = {"key": k, "distinct_design_id": r["distinct_design_id"],
               "site": r["site"], "pem_mw": r["pem_mw"],
               "G_run_usd": float(r["G_run_usd"]), "ruc_cost_sum_usd": float(r["ruc_cost_sum_usd"]),
               "G_over_ruc_cost_pct": 100.0 * float(r["G_run_usd"]) / float(r["ruc_cost_sum_usd"]),
               "max_gap_pct": float(r["max_gap_pct"]), "n_ruc": int(r["n_ruc"]),
               "pair_bound_vs_base_usd": bound}
        for c in ("E1", "E2", "E3"):
            dlt = float(r[c]) - float(w.loc[base_key, c])
            out[f"delta_{c}_usd"] = dlt
            out[f"{c}_gap_status"] = ("base" if k == base_key else
                                      "GAP-READABLE" if abs(dlt) >= bound else "WITHIN GAP BOUND")
        rows.append(out)
    tab = pd.DataFrame(rows)
    summary = {"G_base_usd": Gb, "ref_single_site_median_abs_delta_total_cost_usd": ref_median,
               "G_base_over_ref": Gb / ref_median,
               "G_base_exceeds_ref": bool(Gb > ref_median),
               "G_run_min_usd": float(tab["G_run_usd"].min()),
               "G_run_max_usd": float(tab["G_run_usd"].max()),
               "n_single_site_E1_gap_readable": int(((tab["E1_gap_status"] == "GAP-READABLE")
                                                    & tab["key"].isin(FIRST_CUT_KEYS)).sum()),
               "n_single_site": int(tab["key"].isin(FIRST_CUT_KEYS).sum())}
    return tab, summary


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------
def git_head(short=True):
    import subprocess
    try:
        return subprocess.run(["git", "-C", HERE, "rev-parse", "--short" if short else "HEAD", "HEAD"],
                              capture_output=True, text=True, check=True).stdout.strip()
    except Exception:  # noqa: BLE001
        return "unknown"


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--stage", choices=["A1", "A3", "all"], default="all",
                    help="A1 = pool_wide/delta/dead/replicate/gap; A3 = first cut (after the freeze commit)")
    ap.add_argument("--freeze-hash", default="", help="freeze commit of pool_definitions.json (printed in outputs)")
    args = ap.parse_args(argv)
    defs = load_defs()
    os.makedirs(os.path.join(POOL, "figs"), exist_ok=True)
    wide_path = os.path.join(POOL, "pool_wide_v2.csv")

    if args.stage in ("A1", "all"):
        wide = build_pool(defs=defs)
        wide.to_csv(wide_path, index=False)
        deltas(wide).to_csv(os.path.join(POOL, "pool_delta_v2.csv"), index=False)
        rep = regression_vs_frozen(wide)
        rep.to_csv(os.path.join(POOL, "regression_vs_frozen_t1_v2.csv"), index=False)
        bad = rep[~rep["ok"]]
        assert bad.empty, f"regression vs frozen objectives_t1_v2.csv failed:\n{bad}"
        print(f"regression vs frozen: {len(rep)} cells OK; h2 copied on "
              f"{int(rep['copied_from_frozen'].sum()) // 1} cells")
        dead = dead_list(wide)
        dead.to_csv(os.path.join(POOL, "pool_dead_list_v2.csv"), index=False)
        print("A2 status:\n", dead[["id", "status", "n_values", "max_abs_value"]].to_string(index=False))
        rz = replicate_zero_check(wide)
        rz.to_csv(os.path.join(POOL, "pool_replicate_zero_check_v2.csv"), index=False)
        print("replicate groups max within-group |delta| over all candidates:",
              float(rz["max_abs_within_delta"].max()) if len(rz) else "n/a")
        tab, summ = gap_table(wide)
        tab.to_csv(os.path.join(POOL, "pool_gap_bound_v2.csv"), index=False)
        with open(os.path.join(POOL, "pool_gap_bound_summary.json"), "w") as f:
            json.dump(summ, f, indent=2)
            f.write("\n")
        print("A4b G_base = %.3e $, ref median |delta total_cost| = %.3e $, ratio %.2f"
              % (summ["G_base_usd"], summ["ref_single_site_median_abs_delta_total_cost_usd"],
                 summ["G_base_over_ref"]))
        print(f"31 rows: {len(wide)}; distinct designs: {wide['distinct_design_id'].nunique()}; "
              f"full extracts: {int(wide['full_extract'].sum())}; suspect: {int(wide['suspect'].sum())}")

    if args.stage in ("A3", "all"):
        wide = pd.read_csv(wide_path, dtype={"replicate_of": str, "site": str, "h2_source": str})
        wide["replicate_of"] = wide["replicate_of"].fillna("")
        dead = dead_list(wide)
        fc = first_cut(wide, defs, dead)
        fc["long"].to_csv(os.path.join(POOL, "pool_spearman_firstcut.csv"), index=False)
        fc["raw"].round(4).to_csv(os.path.join(POOL, "pool_spearman_firstcut_matrix_raw.csv"))
        fc["partial"].round(4).to_csv(os.path.join(POOL, "pool_spearman_firstcut_matrix_partial.csv"))
        fc["S"].to_csv(os.path.join(POOL, "pool_firstcut_S_descriptor.csv"), index=False)
        with open(os.path.join(POOL, "pool_firstcut_clusters.json"), "w") as f:
            json.dump({**fc["clusters"], "freeze_commit": args.freeze_hash or git_head(),
                       "n": fc["n"], "n_bus120": fc["n_bus120"], "ids": fc["ids"]}, f, indent=2)
            f.write("\n")
        plot_clustermap(fc["raw"], fc["partial"],
                        os.path.join(POOL, "figs", "pool_firstcut_clustermap.png"), defs,
                        f"definitions frozen at {args.freeze_hash or git_head()}")
        print("A3 ids:", fc["ids"])
        print("A3 clusters (rho_or >= 0.90, complete linkage, directed only):", fc["clusters"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
