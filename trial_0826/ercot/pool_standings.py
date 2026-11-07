"""Prompt 57 Part B: ERCOT objective-pool standings on wave D (zero simulation).

Reads the wave-D extracts (`extracts/location_oat_v2`, 18 VRE rows = 6 sites x
3 absolute MW levels + 3 nuclear rows) through pool_objectives.pool_row, merges
the CRC-computed pool_full_metrics.json (E8/E9/N5; the gz tables are not in
git) and writes the section-4 standings under analysis/pool/.

Reads pinned in prompt 57 section 4 and the executor brief (2026-11-07):
- Every delta is value - base. The default base is base_2019_v2:1 (identity
  v2: gap 0.01 / TL 120); wave D ran under identity v3 (gap 0.001 / TL 1200).
  No v3 base exists, so every delta column is labelled
  CONTAMINATED (v2 base, v3 rows) and carries the smoke-scaled identity shift
  (extracts/smoke_gap task_2 - task_1, x 365/3 for extensive candidates) next
  to it. `--base <wave:index | extract dir>` re-runs everything against a v3
  base in one command.
- Base-free reads: range_jl and every rank statistic (rho, W, clusters,
  conflicts) do not depend on the base. The PRIMARY scale-free read is
  S'_jl = range_jl / mean_site |x_j(site, L180) - x_j(site, L60)| (spread across
  sites relative to the within-wave size effect). S_jl = range_jl / mean_site
  |delta_jl| (prompt 57 A4b) is reported as the secondary, contaminated read.
- Ruler columns (prompt 52) are RULER PENDING (52) unless --noise
  ercot_noise.json is given.
- Nuclear rows 19-21 are a separate stratum: overlay only; never in range, S,
  W, rho. Their cost-family values (E1-E4, E7) are UNCORRECTED (the thermal
  patch rewrites the nuclear cost curve; K_syn accounting pending) and are
  not overlaid on the cost heatmaps.
- pool_definitions.json is FROZEN at f76d897 and asserted against git.

pandas-3 safe (no chained assignment, explicit copies). scipy + matplotlib
only (no seaborn).
"""

import argparse
import hashlib
import itertools
import json
import os
import subprocess
import sys
import warnings

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore", message="Downcasting object dtype arrays",
                        category=FutureWarning)

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import pool_objectives as po  # noqa: E402

POOL = po.POOL
FIGS = os.path.join(POOL, "figs", "standings")
WAVE = "location_oat_v2"
FREEZE_HASH = "f76d897"
LEVELS = ["L60", "L120", "L180"]
LEVEL_MW = {"L60": 60.0, "L120": 120.0, "L180": 180.0}
SMOKE = os.path.join(po.EXTR, "smoke_gap")
SMOKE_DAYS = 3
YEAR_DAYS = 365
V2_IDENTITY = {"ruc_mipgap": 0.01, "ruc_time_limit": 120.0, "identity": "v2"}

# graded candidates (D3 is a check, split into two columns in pool_wide)
GRADED = [c for c in po.CAND_IDS]
COST_FAMILY_UNCORRECTED = ["E1", "E2", "E3", "E4", "E7"]
# extensive (annual sums; smoke 3-day shift x 365/3) vs intensive (raw difference)
EXTENSIVE = {"V1", "E1", "E2", "E3", "E4", "E5", "E6", "E9", "R1", "R2", "R3", "R4",
             "R5", "R6", "R7", "R8", "N1", "N3", "N4", "X1", "D1"}
JSON_OVERRIDE = ("E8", "E9", "N5", "N5_unweighted_check", "E9_lmp_max")
S_THRESHOLD = 0.5
RHO_CLUSTER = 0.90
RHO_CONFLICT = -0.50
NULL_BAND_N18 = 0.47
RULER_PENDING = "RULER PENDING (52)"
CONTAMINATED = "CONTAMINATED (v2 base, v3 rows)"
HONESTY = ("18-21 one-at-a-time rows, 3 levels, no interactions; the RTS verdicts rested on 15 "
           "pair grids of 81 cells. Every pooled statistic is also given per level. No multiplicity "
           "correction is applied: the verdicts are pinned threshold reads on a deterministic "
           "instrument, not tests. Of the ~22 graded candidates, about one W p-value below 0.05 is "
           "expected under exchangeable site labels, and about 0.05 false redundancy clusters among "
           "231 pairs; W does not enter any verdict. A false LOCATION-SENSITIVE call admits one more "
           "candidate to the PI table, so the error direction is permissive, not conservative; the "
           "table therefore carries range_jl / ruler_j at every level, never the label alone.")


# --------------------------------------------------------------------------
# freeze assert, identity, base
# --------------------------------------------------------------------------
def assert_frozen_defs(path=po.DEFS_PATH, freeze=FREEZE_HASH):
    """pool_definitions.json on disk == the blob at the freeze commit (md5)."""
    with open(path, "rb") as f:
        disk = hashlib.md5(f.read()).hexdigest()
    rel = os.path.relpath(path, subprocess.run(["git", "-C", HERE, "rev-parse", "--show-toplevel"],
                                               capture_output=True, text=True, check=True).stdout.strip())
    blob = subprocess.run(["git", "-C", HERE, "show", f"{freeze}:{rel}"],
                          capture_output=True, check=True).stdout
    frozen = hashlib.md5(blob).hexdigest()
    assert disk == frozen, f"pool_definitions.json differs from the freeze commit {freeze}: {disk} != {frozen}"
    return disk


def read_identity(d):
    """identity.txt -> {ruc_mipgap, ruc_time_limit, identity}; None if absent."""
    p = os.path.join(d, "identity.txt")
    if not os.path.isfile(p):
        return None
    line = open(p).read().strip()
    out = {"line": line}
    for tok in line.split():
        if tok.startswith("ruc_mipgap="):
            out["ruc_mipgap"] = float(tok.split("=", 1)[1])
        elif tok.startswith("ruc_time_limit="):
            out["ruc_time_limit"] = float(tok.split("=", 1)[1])
    gap = out.get("ruc_mipgap")
    out["identity"] = "v2" if gap == 0.01 else ("v3" if gap == 0.001 else f"gap {gap}")
    return out


def resolve_base(base, extr=po.EXTR, waves=po.WAVES, defs=None):
    """`base` = None (pool_wide_v2.csv row base_2019_v2:1), 'wave:index', or an
    extract dir named .../<wave>/run_index_<N>. Returns (row dict, identity dict, label)."""
    defs = defs or po.load_defs()
    if base is None or base == po.BASE_KEY:
        wide = pd.read_csv(os.path.join(POOL, "pool_wide_v2.csv"),
                           dtype={"replicate_of": str, "site": str, "h2_source": str})
        r = wide[wide["key"] == po.BASE_KEY]
        assert len(r) == 1
        row = r.iloc[0].to_dict()
        d = po.run_dir(po.BASE_KEY, extr)
        ident = read_identity(d) or dict(V2_IDENTITY)
        return row, ident, po.BASE_KEY
    if os.path.isdir(base):
        d = os.path.abspath(base)
        idx = os.path.basename(d).replace("run_index_", "")
        wave = os.path.relpath(os.path.dirname(d), extr).replace(os.sep, "/")
        key = f"{wave}:{idx}"
        drow = None
        if os.path.isfile(os.path.join(waves, wave, "design_matrix.csv")):
            try:
                drow = po.design_row(wave, idx, waves)
            except (KeyError, ValueError):
                drow = None
        row = po.pool_row(key, extr, waves, defs=defs, drow=drow or dict(po.BASE_DROW), d=d)
        ident = read_identity(d) or {"identity": "unknown (no identity.txt)"}
        return row, ident, key
    wave, idx = base.split(":")
    row = po.pool_row(base, extr, waves, defs=defs)
    ident = read_identity(po.run_dir(base, extr)) or dict(V2_IDENTITY)
    return row, ident, base


# --------------------------------------------------------------------------
# wave-D wide (21 rows) + pool_full_metrics merge
# --------------------------------------------------------------------------
def build_wave(wave=WAVE, extr=po.EXTR, waves=po.WAVES, defs=None, verbose=True):
    defs = defs or po.load_defs()
    dm = po.design_matrix(wave, waves)
    keys = [f"{wave}:{int(i)}" for i in dm["index"]]
    wide = po.build_pool(keys=keys, extr=extr, waves=waves, defs=defs, verbose=verbose)
    lvl = {int(i): str(l) for i, l in zip(dm["index"], dm["level_id"])}
    pmw = {int(i): float(p) for i, p in zip(dm["index"], dm["pem_mw"])}
    wide = wide.copy()
    wide["level_id"] = wide["index"].map(lvl)
    assert np.allclose(wide["pem_mw"].to_numpy(dtype=float), wide["index"].map(pmw).to_numpy(dtype=float), atol=1e-6)
    present, ident, full_src, h_mean, h_min, solve_med, solve_max, n_tl = ([] for _ in range(8))
    for i, r in wide.iterrows():
        d = po.run_dir(r["key"], extr)
        jp = os.path.join(d, "pool_full_metrics.json")
        present.append(os.path.isfile(jp))
        if present[-1]:
            with open(jp) as f:
                pm = json.load(f)
            for c in JSON_OVERRIDE:
                v = pm.get(c)
                v = np.nan if v is None else float(v)
                if np.isfinite(r.get(c, np.nan)) and np.isfinite(v):
                    assert abs(float(r[c]) - v) <= 1e-6 * max(1.0, abs(v)), (r["key"], c, r[c], v)
                wide.loc[i, c] = v
            # consistency of the CRC json with the local slim recomputation
            for c in ("R7", "R8", "G_run_usd"):
                assert abs(float(r[c]) - float(pm[c])) <= 1e-6 * max(1.0, abs(float(pm[c]))), (r["key"], c)
            assert pm["overall_md5"] == r["overall_md5"], (r["key"], "overall.csv md5 differs from pool_full_metrics.json")
            wide.loc[i, "full_extract"] = bool(pm.get("full_extract", False))
            full_src.append("pool_full_metrics.json (CRC; gz not local)" if not po.is_full(d) else "local gz")
            h_mean.append(pm.get("H_headroom_mean_mw", np.nan))
            h_min.append(pm.get("H_headroom_min_mw", np.nan))
            solve_med.append(pm.get("ruc_solve_time_median_s", np.nan))
            solve_max.append(pm.get("ruc_solve_time_max_s", np.nan))
            n_tl.append(pm.get("n_ruc_time_limit", np.nan))
        else:
            full_src.append("absent")
            for lst in (h_mean, h_min, solve_med, solve_max, n_tl):
                lst.append(np.nan)
        ident.append((read_identity(d) or {}).get("identity", "unknown"))
    wide["pool_full_metrics_present"] = present
    wide["full_source"] = full_src
    wide["identity"] = ident
    wide["H_headroom_mean_mw"] = h_mean
    wide["H_headroom_min_mw"] = h_min
    wide["ruc_solve_time_median_s"] = solve_med
    wide["ruc_solve_time_max_s"] = solve_max
    wide["n_ruc_time_limit"] = n_tl
    assert wide["full_extract"].all(), "wave D: full_extract must be True on every row (prompt 57 A5)"
    return wide


def wallclock_table(wide, extr=po.EXTR, wave=WAVE, slots=4, split_s=25000.0):
    p = os.path.join(extr, wave, "wallclock.csv")
    w = pd.read_csv(p)
    w = w.rename(columns={"task": "index"})
    w["index"] = w["index"].astype(int)
    m = wide[["index", "site", "level_id", "unit_type", "ruc_solve_time_median_s", "ruc_solve_time_max_s", "n_ruc_time_limit"]].copy()
    t = w.merge(m, on="index", how="left")
    t["wall_h"] = t["wall_s"] / 3600.0
    t["core_h"] = t["wall_h"] * slots
    t["node_group"] = np.where(t["wall_s"] < split_s, "A (fast)", "B (slow)")
    t = t.sort_values("index").reset_index(drop=True)
    return t


# --------------------------------------------------------------------------
# identity shift from the gap smoke (task_1 = 0.01, task_2 = 0.001)
# --------------------------------------------------------------------------
def smoke_identity_shift(ids, smoke=SMOKE, defs=None, days=SMOKE_DAYS):
    """Per candidate: (task_2 - task_1) over the 3 smoke days; extensive
    candidates scaled x 365/days to a year-equivalent. NaN with a note when
    the smoke extracts are absent."""
    defs = defs or po.load_defs()
    rows = []
    d1, d2 = os.path.join(smoke, "task_1"), os.path.join(smoke, "task_2")
    if not (os.path.isfile(os.path.join(d1, "overall.csv")) and os.path.isfile(os.path.join(d2, "overall.csv"))):
        for c in ids:
            rows.append({"id": c, "smoke_shift_3day": np.nan, "identity_shift_scaled": np.nan,
                         "scaling": "smoke extracts absent"})
        return pd.DataFrame(rows)
    r1 = po.pool_row("smoke_gap:task_1", defs=defs, drow=dict(po.BASE_DROW), d=d1)
    r2 = po.pool_row("smoke_gap:task_2", defs=defs, drow=dict(po.BASE_DROW), d=d2)
    for c in ids:
        a, b = r1.get(c, np.nan), r2.get(c, np.nan)
        try:
            a, b = float(a), float(b)
        except (TypeError, ValueError):
            a, b = np.nan, np.nan
        shift = b - a
        ext = c in EXTENSIVE
        rows.append({"id": c, "smoke_task1_gap001": a, "smoke_task2_gap0001": b,
                     "smoke_shift_3day": shift,
                     "identity_shift_scaled": shift * (YEAR_DAYS / days) if ext else shift,
                     "scaling": (f"x {YEAR_DAYS}/{days} (extensive)" if ext else "raw 3-day difference (intensive)")})
    return pd.DataFrame(rows)


# --------------------------------------------------------------------------
# Kendall's W with the exact permutation distribution (k = 6, n = 3)
# --------------------------------------------------------------------------
_W_CACHE = {}


def kendall_W(rank_rows):
    """rank_rows: (n_judges, k) ranks. W = 12 S / (n^2 (k^3 - k)), no tie correction."""
    R = np.asarray(rank_rows, dtype=float)
    n, k = R.shape
    tot = R.sum(axis=0)
    S = float(((tot - tot.mean()) ** 2).sum())
    return 12.0 * S / (n ** 2 * (k ** 3 - k))


def exact_W_distribution(k=6, n=3):
    """All W values over the (k!)^(n-1) relative permutations (judge 1 fixed)."""
    key = (k, n)
    if key not in _W_CACHE:
        perms = np.array(list(itertools.permutations(range(1, k + 1))), dtype=float)   # (k!, k)
        base = np.arange(1, k + 1, dtype=float)
        if n == 3:
            tot = base[None, None, :] + perms[:, None, :] + perms[None, :, :]        # (k!, k!, k)
            S = ((tot - tot.mean(axis=2, keepdims=True)) ** 2).sum(axis=2).ravel()
        elif n == 2:
            tot = base[None, :] + perms
            S = ((tot - tot.mean(axis=1, keepdims=True)) ** 2).sum(axis=1)
        else:
            raise NotImplementedError("exact W enumerated for n in {2, 3} judges")
        _W_CACHE[key] = np.sort(12.0 * S / (n ** 2 * (k ** 3 - k)))
    return _W_CACHE[key]


def kendall_W_exact(values_by_level):
    """values_by_level: (n_levels, k_sites) raw or delta values; sites are ranked
    within each level (mid-ranks on ties). Returns W, exact p = P(W_null >= W_obs),
    number of tied cells, and the enumeration size."""
    from scipy.stats import rankdata
    V = np.asarray(values_by_level, dtype=float)
    n, k = V.shape
    if not np.isfinite(V).all():
        return np.nan, np.nan, 0, 0
    R = np.vstack([rankdata(v) for v in V])
    ties = int(sum(len(v) - len(np.unique(v)) for v in V))
    W = kendall_W(R)
    dist = exact_W_distribution(k, n)
    p = float((dist >= W - 1e-12).sum()) / float(len(dist))
    return float(W), p, ties, int(len(dist))


# --------------------------------------------------------------------------
# step 1: per level, per candidate
# --------------------------------------------------------------------------
def vre_rows(wide):
    return wide[wide["unit_type"] != "NUC"].copy()


def nuc_rows(wide):
    return wide[wide["unit_type"] == "NUC"].copy()


def site_level_matrix(df, col, levels=LEVELS):
    """DataFrame sites x levels of column `col` (raw values)."""
    M = df.pivot(index="site", columns="level_id", values=col)
    return M.reindex(columns=levels)


def scale_free_verdict(S_by_level, means, thr=S_THRESHOLD):
    vals = np.array([S_by_level[l] for l in LEVELS], dtype=float)
    defined = np.isfinite(vals)
    if defined.sum() == 0:
        return "NO EFFECT AT EVERY LEVEL"
    hi = int((vals[defined] >= thr).sum())
    lo = int((vals[defined] < thr).sum())
    if hi >= 2:
        return "LOCATION-SENSITIVE (scale-free)"
    if lo >= 2:
        return "SIZE-DRIVEN (scale-free)"
    return "UNDETERMINED (scale-free; < 2 levels agree)"


def level_reads(wide_vre, base_row, ids, G_base=None, ruler=None, levels=LEVELS):
    """Per candidate: per-site delta at each level, range, mean |delta|, S (v2 base,
    contaminated), S' (base-free), W + exact p, gap-bound statuses (E1-E3),
    ruler ratios when `ruler` (dict id -> ruler_j) is given."""
    out = {}
    long = []
    sites = sorted(wide_vre["site"].unique(), key=lambda s: int(s))
    for c in ids:
        X = site_level_matrix(wide_vre, c, levels).reindex(sites)
        if not np.isfinite(X.to_numpy(dtype=float)).all():
            out[c] = {"status_data": "NaN on some wave-D rows", "X": X}
            continue
        b = float(base_row[c]) if c in base_row and pd.notna(base_row[c]) else np.nan
        D = X - b
        size_eff = (X[levels[-1]] - X[levels[0]]).abs()        # within-site 60 -> 180 effect
        mean_size_eff = float(size_eff.mean())
        rec = {"X": X, "D": D, "base": b, "mean_size_effect_60_180": mean_size_eff,
               "dead_on_wave": bool(float(X.to_numpy().max() - X.to_numpy().min()) == 0.0),
               "max_abs_wave_value": float(np.abs(X.to_numpy()).max())}
        S, Sp, rng, mabs = {}, {}, {}, {}
        for l in levels:
            rng[l] = float(X[l].max() - X[l].min())
            mabs[l] = float(D[l].abs().mean()) if np.isfinite(b) else np.nan
            S[l] = (rng[l] / mabs[l]) if (np.isfinite(mabs[l]) and mabs[l] > 0) else np.nan
            Sp[l] = (rng[l] / mean_size_eff) if mean_size_eff > 0 else np.nan
        rec.update({"range": rng, "mean_abs_delta": mabs, "S": S, "S_prime": Sp,
                    "S_verdict": scale_free_verdict(S, mabs),
                    "S_prime_verdict": scale_free_verdict(Sp, {l: mean_size_eff for l in levels})})
        # Kendall W on the site ranking across levels (base-invariant; uses raw X)
        W, p, ties, nperm = kendall_W_exact(X.to_numpy(dtype=float).T)
        rec.update({"W": W, "W_p_exact": p, "W_ties": ties, "W_n_perm": nperm})
        # response shape per site (sign on delta = contaminated; monotone on raw X = base-free)
        shape = {}
        for s in sites:
            x = X.loc[s, levels].to_numpy(dtype=float)
            d = D.loc[s, levels].to_numpy(dtype=float)
            nz = d[d != 0]
            sign = ("+" if (nz > 0).all() else "-" if (nz < 0).all() else "mixed") if len(nz) else "0"
            mono = ("increasing" if np.all(np.diff(x) > 0) else "decreasing" if np.all(np.diff(x) < 0)
                    else "flat" if np.all(np.diff(x) == 0) else "non-monotone")
            shape[s] = {"sign": sign, "n_nonzero": int(len(nz)), "monotone_raw": mono}
        rec["shape"] = shape
        rec["n_sites_monotone"] = int(sum(v["monotone_raw"] in ("increasing", "decreasing") for v in shape.values()))
        rec["n_sites_sign_consistent"] = int(sum(v["sign"] in ("+", "-") for v in shape.values()))
        rec["sign_pattern"] = "".join(shape[s]["sign"][0] for s in sites)
        # ruler read (prompt 52)
        if ruler is not None and c in ruler and np.isfinite(ruler[c]):
            rj = float(ruler[c])
            rec["ruler"] = rj
            if rj == 0.0:
                rec["ruler_status"] = "RULER=0"
                rec["range_over_ruler"] = {l: np.nan for l in levels}
                nat = 1.0
                rec["ruler_verdict"] = ("LOCATION-SENSITIVE" if sum(rng[l] >= nat for l in levels) >= 2
                                        else "UNREADABLE AT THIS SIZE")
            else:
                rec["ruler_status"] = "RULER"
                rec["range_over_ruler"] = {l: rng[l] / rj for l in levels}
                n_range_ok = sum(rng[l] >= 2 * rj for l in levels)
                n_site_ok = sum(int((D[l].abs() >= 2 * rj).sum()) >= 4 for l in levels)
                n_range_lo = sum(rng[l] < 2 * rj for l in levels)
                if n_range_ok >= 2:
                    rec["ruler_verdict"] = "LOCATION-SENSITIVE"
                elif n_site_ok >= 2 and n_range_lo >= 2:
                    rec["ruler_verdict"] = "LOCATION-INSENSITIVE AT THESE SIZES"
                else:
                    rec["ruler_verdict"] = "UNREADABLE AT THIS SIZE"
                rec["ruler_borderline"] = [l for l in levels if 2.0 <= rng[l] / rj < 3.0]
        else:
            rec["ruler"] = np.nan
            rec["ruler_status"] = RULER_PENDING if ruler is None else "RULER UNAVAILABLE"
            rec["range_over_ruler"] = {l: np.nan for l in levels}
            rec["ruler_verdict"] = rec["ruler_status"]
        out[c] = rec
        for l in levels:
            for s in sites:
                long.append({"id": c, "level_id": l, "pem_mw": LEVEL_MW[l], "site": s,
                             "value": float(X.loc[s, l]), "delta_vs_base": float(D.loc[s, l]),
                             "delta_label": CONTAMINATED})
    return out, pd.DataFrame(long)


def gap_bound_reads(wide_vre, base_row, G_base, levels=LEVELS, cost_ids=("E1", "E2", "E3")):
    """Per site x level: |delta| vs G_base + G_row (raw RUC-objective scale) and the
    realized-cost scaled version (G / (ruc_cost_sum / E1)); plus the between-site
    range at each level vs the v3-only pair bound max_(a,b) G_a + G_b (what a v3 base
    would see at most)."""
    rows = []
    sites = sorted(wide_vre["site"].unique(), key=lambda s: int(s))
    w = wide_vre.set_index(["site", "level_id"])
    ratio_base = float(base_row["ruc_cost_sum_usd"]) / float(base_row["E1"])
    for c in cost_ids:
        for l in levels:
            Gs = {s: float(w.loc[(s, l), "G_run_usd"]) for s in sites}
            vals = {s: float(w.loc[(s, l), c]) for s in sites}
            rng = max(vals.values()) - min(vals.values())
            v3_pair_max = max(Gs[a] + Gs[b] for a, b in itertools.combinations(sites, 2))
            ratios = {s: float(w.loc[(s, l), "ruc_cost_sum_usd"]) / float(w.loc[(s, l), "E1"]) for s in sites}
            v3_pair_max_scaled = max(Gs[a] / ratios[a] + Gs[b] / ratios[b] for a, b in itertools.combinations(sites, 2))
            for s in sites:
                dlt = vals[s] - float(base_row[c])
                bound = G_base + Gs[s]
                ratio_row = float(w.loc[(s, l), "ruc_cost_sum_usd"]) / float(w.loc[(s, l), "E1"])
                bound_scaled = G_base / ratio_base + Gs[s] / ratio_row
                rows.append({"id": c, "level_id": l, "site": s, "delta_vs_base_usd": dlt,
                             "G_base_usd": G_base, "G_row_usd": Gs[s], "pair_bound_usd": bound,
                             "gap_status_raw": "GAP-READABLE" if abs(dlt) >= bound else "WITHIN GAP BOUND",
                             "pair_bound_scaled_usd": bound_scaled,
                             "gap_status_scaled": "GAP-READABLE" if abs(dlt) >= bound_scaled else "WITHIN GAP BOUND",
                             "G_base_share_of_bound": G_base / bound,
                             "range_at_level_usd": rng, "v3_pair_bound_max_usd": v3_pair_max,
                             "range_vs_v3_pair_bound": "GAP-READABLE" if rng >= v3_pair_max else "WITHIN GAP BOUND",
                             "v3_pair_bound_max_scaled_usd": v3_pair_max_scaled,
                             "range_vs_v3_pair_bound_scaled": "GAP-READABLE" if rng >= v3_pair_max_scaled else "WITHIN GAP BOUND",
                             "delta_label": CONTAMINATED})
    return pd.DataFrame(rows)


# --------------------------------------------------------------------------
# step 3: oriented Spearman, pooled / per level / stratified; redundancy clusters
# --------------------------------------------------------------------------
def oriented_frame(wide_vre, ids, defs, base_row=None):
    """Oriented deltas (max x -1). Ranks are base-invariant; the base is only
    subtracted so the file shows deltas."""
    O = pd.DataFrame(index=wide_vre.index)
    for c in ids:
        sgn = -1.0 if defs["candidates"][c]["dir"] == "max" else 1.0
        b = float(base_row[c]) if base_row is not None and pd.notna(base_row.get(c, np.nan)) else 0.0
        O[c] = (wide_vre[c].astype(float) - b) * sgn
    return O


def spearman_matrix(O):
    from scipy import stats
    ids = list(O.columns)
    n = len(ids)
    M = np.full((n, n), np.nan)
    for i in range(n):
        M[i, i] = 1.0
        for j in range(i + 1, n):
            x, y = O[ids[i]].to_numpy(dtype=float), O[ids[j]].to_numpy(dtype=float)
            if np.ptp(x) == 0 or np.ptp(y) == 0:
                r = np.nan
            else:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    r = float(stats.spearmanr(x, y).statistic)
            M[i, j] = M[j, i] = r
    return pd.DataFrame(M, index=ids, columns=ids)


def stratified_matrix(O, level_ids):
    """Spearman of the within-level site ranks over all rows (level-stratified rho)."""
    from scipy.stats import rankdata
    R = O.copy()
    for c in O.columns:
        r = np.full(len(O), np.nan)
        for l in np.unique(level_ids):
            m = np.asarray(level_ids) == l
            r[m] = rankdata(O[c].to_numpy(dtype=float)[m])
        R[c] = r
    return spearman_matrix(R)


def correlation_block(wide_vre, ids, defs, base_row=None, levels=LEVELS):
    O = oriented_frame(wide_vre, ids, defs, base_row)
    lv = wide_vre["level_id"].to_numpy()
    pooled = spearman_matrix(O)
    per_level = {l: spearman_matrix(O[lv == l]) for l in levels}
    strat = stratified_matrix(O, lv)
    return {"O": O, "pooled": pooled, "per_level": per_level, "stratified": strat}


def pair_table(cb, ids, defs, levels=LEVELS, rho_min=RHO_CLUSTER):
    rows = []
    cands = defs["candidates"]
    for i, a in enumerate(ids):
        for b in ids[i + 1:]:
            pl = {l: float(cb["per_level"][l].loc[a, b]) for l in levels}
            n_hi = sum(1 for l in levels if np.isfinite(pl[l]) and pl[l] >= rho_min)
            n_neg = sum(1 for l in levels if np.isfinite(pl[l]) and pl[l] < 0)
            n_neg50 = sum(1 for l in levels if np.isfinite(pl[l]) and pl[l] <= RHO_CONFLICT)
            pooled = float(cb["pooled"].loc[a, b])
            both_dir = cands[a]["dir"] in ("min", "max") and cands[b]["dir"] in ("min", "max")
            redundant = bool(both_dir and np.isfinite(pooled) and pooled >= rho_min and n_hi >= 2)
            tradeoff90 = bool(both_dir and np.isfinite(pooled) and pooled <= -rho_min)
            rows.append({"pair": f"{a}|{b}", "a": a, "b": b, "a_dir": cands[a]["dir"], "b_dir": cands[b]["dir"],
                         "both_directed": both_dir, "rho_pooled_n18": pooled,
                         **{f"rho_{l}_n6": pl[l] for l in levels},
                         "rho_stratified": float(cb["stratified"].loc[a, b]),
                         "n_levels_ge_0.90": n_hi, "n_levels_negative": n_neg, "n_levels_le_-0.50": n_neg50,
                         "redundant_pair": redundant, "tradeoff_le_-0.90": tradeoff90})
    return pd.DataFrame(rows)


def clusters_from_pairs(pairs, members):
    """Complete linkage on the binary 'redundant' relation -> every pair inside a
    cluster is redundant (cliques)."""
    from scipy.cluster.hierarchy import fcluster, linkage
    from scipy.spatial.distance import squareform
    members = list(members)
    if len(members) < 2:
        return []
    red = {(r["a"], r["b"]) for _, r in pairs[pairs["redundant_pair"]].iterrows()}
    n = len(members)
    D = np.ones((n, n))
    np.fill_diagonal(D, 0.0)
    for i in range(n):
        for j in range(i + 1, n):
            if (members[i], members[j]) in red or (members[j], members[i]) in red:
                D[i, j] = D[j, i] = 0.0
    Z = linkage(squareform(D, checks=False), method="complete")
    lab = fcluster(Z, t=0.5, criterion="distance")
    cl = {}
    for m, l in zip(members, lab):
        cl.setdefault(int(l), []).append(m)
    return [sorted(v) for v in cl.values() if len(v) >= 2]


def survivor(cluster, global_order, eligible):
    for c in global_order:
        if c in cluster and c in eligible:
            return c
    return None


# --------------------------------------------------------------------------
# step 4: starts attribution (R4-R6)
# --------------------------------------------------------------------------
def starts_attribution(wide_vre, base_dir, extr=po.EXTR, levels=LEVELS, top=5):
    """Per site at each level: which units' starts moved vs base (gen_summary.starts),
    and base-free: L180 - L60 within site. Reports the top units by |delta starts|,
    the number of units moving, and the share of the total |delta| carried by the top 5."""
    gb = po.co.gen_summary(base_dir).set_index("Generator")["starts"].astype(float)
    rows = []
    cache = {}
    for _, r in wide_vre.iterrows():
        d = po.run_dir(r["key"], extr)
        g = po.co.gen_summary(d)
        cache[(r["site"], r["level_id"])] = g.set_index("Generator")[["starts", "unit_type"]]
    for (s, l), g in sorted(cache.items(), key=lambda kv: (int(kv[0][0]), LEVELS.index(kv[0][1]))):
        st = g["starts"].astype(float)
        for mode, ref in (("vs v2 base (contaminated)", gb), ("vs L60 same site (base-free)", cache[(s, levels[0])]["starts"].astype(float))):
            if mode.startswith("vs L60") and l == levels[0]:
                continue
            ds = (st - ref.reindex(st.index)).dropna()
            ds = ds[ds != 0]
            tot = float(ds.abs().sum())
            topu = ds.abs().sort_values(ascending=False).head(top)
            rows.append({"site": s, "level_id": l, "mode": mode, "sum_delta_starts": float(ds.sum()),
                         "n_units_moving": int(len(ds)), "n_units_up": int((ds > 0).sum()),
                         "n_units_down": int((ds < 0).sum()),
                         "top5_share_of_abs": (float(topu.sum()) / tot) if tot > 0 else np.nan,
                         "top5_units": "; ".join(f"{u}({g.loc[u, 'unit_type']}):{ds[u]:+.0f}" for u in topu.index),
                         "by_type": "; ".join(f"{t}:{ds[g.loc[ds.index, 'unit_type'] == t].sum():+.0f}"
                                              for t in sorted(g.loc[ds.index, "unit_type"].unique()))})
    return pd.DataFrame(rows)


# --------------------------------------------------------------------------
# standings assembly
# --------------------------------------------------------------------------
def assemble_standings(reads, nuc, cb, pairs, defs, dead_ids, ids, base_label, shift, gap=None, levels=LEVELS):
    cands = defs["candidates"]
    go = defs["global_order"]
    directed = [c for c in ids if cands[c]["dir"] in ("min", "max")]
    # step-1 status (ruler pending -> the scale-free S' read sets the status basis)
    status, basis = {}, {}
    for c in ids:
        rec = reads.get(c, {})
        if c in dead_ids:
            status[c], basis[c] = "DEAD", "A2 (zero variance on the 31 v2 runs)"
        elif "X" in rec and rec.get("status_data"):
            status[c], basis[c] = "UNREADABLE AT THIS SIZE", rec["status_data"]
        elif rec.get("dead_on_wave"):
            status[c], basis[c] = "DEAD ON WAVE D", f"zero variance over the 18 VRE rows; max |value| {rec['max_abs_wave_value']:.6g}"
        elif cands[c]["dir"] == "-":
            status[c], basis[c] = "DIAGNOSTIC", "dir '-' (never clusters, never survives, never an objective)"
        elif rec.get("ruler_verdict") not in (RULER_PENDING, "RULER UNAVAILABLE", None):
            status[c], basis[c] = rec["ruler_verdict"], "ruler (prompt 52) three-way read"
        else:
            v = rec.get("S_prime_verdict", "")
            if v.startswith("LOCATION-SENSITIVE"):
                status[c], basis[c] = "LOCATION-SENSITIVE", "scale-free S' (base-free) >= 0.5 at >= 2 of 3 levels; " + RULER_PENDING
            elif v.startswith("SIZE-DRIVEN"):
                status[c], basis[c] = "LOCATION-INSENSITIVE AT THESE SIZES", "scale-free S' (base-free) < 0.5 at >= 2 of 3 levels; " + RULER_PENDING
            else:
                status[c], basis[c] = "UNREADABLE AT THIS SIZE", v + "; " + RULER_PENDING
    eligible = {c for c in directed if status[c] not in ("DEAD", "DEAD ON WAVE D", "UNREADABLE AT THIS SIZE")}
    members = [c for c in directed if c not in dead_ids and not reads.get(c, {}).get("dead_on_wave")
               and "X" in reads.get(c, {}) and not reads[c].get("status_data")]
    clusters = clusters_from_pairs(pairs, members)
    cl_id, surv = {}, {}
    for k, cl in enumerate(clusters, 1):
        s = survivor(cl, go, eligible)
        for c in cl:
            cl_id[c] = f"C{k}"
            surv[c] = s
    for c in ids:
        if c in cl_id and surv[c] is not None and surv[c] != c:
            status[c] = f"REDUNDANT->{surv[c]}"
            basis[c] = f"cluster {cl_id[c]} (rho_or >= 0.90 pooled and at >= 2 of 3 levels, complete linkage); survivor by global order"
    survivors = [c for c in go if c in eligible and (c not in cl_id or surv.get(c) == c)]
    # guardrail role by prior (plan 1.3): R1 (dead), R2
    role = {}
    for c in ids:
        r = cands[c].get("role", "")
        role[c] = ("guardrail" if "guardrail" in r else "diagnostic" if "diagnostic" in r or cands[c]["dir"] == "-"
                   else "check" if "SUSPECT" in r else "objective candidate")
    rows = []
    shift_map = shift.set_index("id") if shift is not None and len(shift) else None
    for c in ids:
        rec = reads.get(c, {})
        row = {"id": c, "family": cands[c]["family"], "name": cands[c]["name"], "unit": cands[c]["unit"],
               "dir": cands[c]["dir"], "priority": cands[c]["priority"],
               "global_order_rank": go.index(c) + 1 if c in go else np.nan,
               "status": status[c], "status_basis": basis[c], "role_prior": role[c],
               "base": base_label, "delta_label": CONTAMINATED if "v2" in base_label or base_label == po.BASE_KEY else "same identity"}
        for l in levels:
            row[f"range_{l}"] = rec.get("range", {}).get(l, np.nan)
            row[f"mean_abs_delta_{l}"] = rec.get("mean_abs_delta", {}).get(l, np.nan)
            row[f"S_prime_{l}"] = rec.get("S_prime", {}).get(l, np.nan)
            row[f"S_{l}"] = rec.get("S", {}).get(l, np.nan)
        row["mean_size_effect_60_180"] = rec.get("mean_size_effect_60_180", np.nan)
        row["S_prime_verdict"] = rec.get("S_prime_verdict", "")
        row["S_verdict_contaminated"] = rec.get("S_verdict", "")
        for l in levels:
            row[f"range_over_ruler_{l}"] = rec.get("range_over_ruler", {}).get(l, np.nan)
        row["ruler_j"] = rec.get("ruler", np.nan)
        row["ruler_status"] = rec.get("ruler_status", RULER_PENDING)
        row["ruler_verdict"] = rec.get("ruler_verdict", RULER_PENDING)
        row["W"] = rec.get("W", np.nan)
        row["W_p_exact"] = rec.get("W_p_exact", np.nan)
        row["W_ties"] = rec.get("W_ties", np.nan)
        row["sign_pattern_sites"] = rec.get("sign_pattern", "")
        row["n_sites_sign_consistent"] = rec.get("n_sites_sign_consistent", np.nan)
        row["n_sites_monotone_raw"] = rec.get("n_sites_monotone", np.nan)
        if gap is not None and c in set(gap["id"]):
            for l in levels:
                gl = gap[(gap["id"] == c) & (gap["level_id"] == l)]
                row[f"gap_readable_sites_{l}"] = f"{int((gl['gap_status_raw'] == 'GAP-READABLE').sum())}/{len(gl)} raw; " \
                                                 f"{int((gl['gap_status_scaled'] == 'GAP-READABLE').sum())}/{len(gl)} scaled"
                row[f"range_vs_v3_pair_bound_{l}"] = gl["range_vs_v3_pair_bound"].iloc[0]
        row["cluster_id"] = cl_id.get(c, "")
        row["cluster_survivor"] = surv.get(c, "") or ""
        row["is_survivor"] = c in survivors
        if shift_map is not None and c in shift_map.index:
            row["identity_shift_scaled"] = float(shift_map.loc[c, "identity_shift_scaled"])
            row["identity_shift_scaling"] = shift_map.loc[c, "scaling"]
            for l in levels:
                m = rec.get("mean_abs_delta", {}).get(l, np.nan)
                row[f"identity_shift_over_mean_abs_delta_{l}"] = (abs(row["identity_shift_scaled"]) / m) if (np.isfinite(m) and m > 0) else np.nan
        for l in levels:
            row[f"nuc_delta_{l}"] = nuc.get(c, {}).get(l, np.nan)
        row["nuc_tag"] = ("UNCORRECTED (nuclear cost curve rewritten by the patch; K_syn accounting pending)"
                          if c in COST_FAMILY_UNCORRECTED else "")
        rows.append(row)
    tab = pd.DataFrame(rows)
    return tab, {"clusters": clusters, "cluster_id": cl_id, "survivor": surv, "survivors": survivors,
                 "eligible": sorted(eligible), "members": members, "status": status}


def conflict_table(pairs, survivors, defs, levels=LEVELS, pinned=("E1", "X1")):
    """Every pair of survivors; the pinned E1|X1 pair is always listed first
    with its two labels whatever they are (even when X1 is REDUNDANT->E1)."""
    rows = []
    sv = list(survivors)
    pairs_to_do = [(a, b) for i, a in enumerate(sv) for b in sv[i + 1:]]
    if pinned not in pairs_to_do and (pinned[1], pinned[0]) not in pairs_to_do:
        pairs_to_do.insert(0, pinned)
    for a, b in pairs_to_do:
        if True:
            r = pairs[(pairs["a"] == a) & (pairs["b"] == b)]
            if not len(r):
                r = pairs[(pairs["a"] == b) & (pairs["b"] == a)]
            if not len(r):
                continue
            r = r.iloc[0]
            pooled = float(r["rho_pooled_n18"])
            pl = [float(r[f"rho_{l}_n6"]) for l in levels]
            n_neg = int(r["n_levels_negative"])
            n_neg50 = int(r["n_levels_le_-0.50"])
            size = bool(np.isfinite(pooled) and pooled <= RHO_CONFLICT and n_neg >= 2)
            loc = bool(size and n_neg50 >= 2)
            label = "TRADE-OFF (location)" if loc else "TRADE-OFF (size)" if size else (
                f"sign {'+' if pooled > 0 else '-' if pooled < 0 else '0'} reported, not labelled" if np.isfinite(pooled) else "undefined")
            rows.append({"pair": f"{a}|{b}", "a": a, "b": b, "rho_pooled_n18": pooled,
                         **{f"rho_{l}_n6": v for l, v in zip(levels, pl)},
                         "n_levels_negative": n_neg, "n_levels_le_-0.50": n_neg50,
                         "trade_off_size": size, "trade_off_location": loc, "label": label,
                         "both_survivors": a in sv and b in sv,
                         "note": ("pinned pair (prompt 57 section 4 step 5); listed whatever its labels"
                                  if (a, b) in (pinned, (pinned[1], pinned[0])) else "")})
    df = pd.DataFrame(rows)
    if len(df):
        first = df["pair"].isin([f"{pinned[0]}|{pinned[1]}", f"{pinned[1]}|{pinned[0]}"])
        df = pd.concat([df[first], df[~first]]).reset_index(drop=True)
    return df


def ed1b_table(tab, info, defs, cap=4):
    """Recommended <= 4 objectives by global order, at most one per family, from
    the survivors with status LOCATION-SENSITIVE or LOCATION-INSENSITIVE AT THESE
    SIZES; guardrails; diagnostics; the full survivor list."""
    go = defs["global_order"]
    cands = defs["candidates"]
    t = tab.set_index("id")
    rec, fam_used = [], set()
    for c in go:
        if c not in t.index or not bool(t.loc[c, "is_survivor"]):
            continue
        if cands[c]["family"] in fam_used or len(rec) >= cap:
            continue
        if t.loc[c, "role_prior"] == "guardrail":
            continue
        rec.append(c)
        fam_used.add(cands[c]["family"])
    rows = []
    for c in go:
        if c not in t.index:
            continue
        st = t.loc[c, "status"]
        if c in rec:
            role = "RECOMMENDED OBJECTIVE"
        elif bool(t.loc[c, "is_survivor"]) and t.loc[c, "role_prior"] == "guardrail":
            role = "GUARDRAIL (survivor)"
        elif bool(t.loc[c, "is_survivor"]):
            role = "SURVIVOR (beyond the cap or family taken)"
        elif st.startswith("REDUNDANT"):
            role = "REDUNDANT -> " + st.split("->")[1]
        elif st == "DIAGNOSTIC":
            role = "DIAGNOSTIC"
        elif st == "DEAD":
            role = "DEAD (guardrail)" if t.loc[c, "role_prior"] == "guardrail" else "DEAD"
        else:
            role = st
        reason = f"{st}; {t.loc[c, 'status_basis']}"
        if c in rec:
            reason = f"survivor; global order {int(t.loc[c, 'global_order_rank'])}; family {cands[c]['family']}; {reason}"
        rows.append({"id": c, "name": cands[c]["name"], "family": cands[c]["family"], "dir": cands[c]["dir"],
                     "global_order_rank": int(t.loc[c, "global_order_rank"]), "E_D1b_role": role,
                     "status": st, "S_prime_verdict": t.loc[c, "S_prime_verdict"],
                     "ruler_verdict": t.loc[c, "ruler_verdict"], "cluster_id": t.loc[c, "cluster_id"],
                     "reason": reason})
    return pd.DataFrame(rows), rec


# --------------------------------------------------------------------------
# figures
# --------------------------------------------------------------------------
def _rc():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.size": 18, "font.weight": "bold", "axes.labelweight": "bold",
                         "axes.titleweight": "bold", "text.parse_math": False})
    return plt


def _fmt(v):
    if not np.isfinite(v):
        return "n/a"
    a = abs(v)
    if a >= 1e6:
        return f"{v / 1e6:+.2f}M"
    if a >= 1e3:
        return f"{v / 1e3:+.1f}k"
    if a >= 10:
        return f"{v:+.0f}"
    return f"{v:+.3g}"


def plot_heatmap(c, rec, nuc_vals, defs, path, base_label, uncorrected=False):
    plt = _rc()
    from matplotlib.patches import Rectangle
    D = rec["D"]
    sites = list(D.index)
    A = D.to_numpy(dtype=float)
    nuc_row = np.array([nuc_vals.get(l, np.nan) for l in LEVELS], dtype=float)
    show_nuc = not uncorrected and np.isfinite(nuc_row).any()
    full = np.vstack([A, nuc_row[None, :]]) if show_nuc else A
    vmax = float(np.nanmax(np.abs(full))) if np.isfinite(full).any() else 1.0
    vmax = vmax if vmax > 0 else 1.0
    fig, ax = plt.subplots(figsize=(11, 10.5))
    im = ax.imshow(np.vstack([A, np.full((1, 3), np.nan)]), cmap="RdBu_r", vmin=-vmax, vmax=vmax, aspect="auto")
    if show_nuc:
        for j, v in enumerate(nuc_row):
            if np.isfinite(v):
                ax.add_patch(Rectangle((j - 0.5, len(sites) - 0.5), 1, 1, facecolor=im.cmap(im.norm(v)),
                                       edgecolor="black", lw=2.5, ls="--"))
    else:
        for j in range(3):
            ax.add_patch(Rectangle((j - 0.5, len(sites) - 0.5), 1, 1, facecolor="0.85",
                                   edgecolor="black", lw=2.5, ls="--", hatch="//"))
    ax.axhline(len(sites) - 0.5, color="black", lw=3)
    for i in range(len(sites)):
        for j in range(3):
            v = A[i, j]
            ax.text(j, i, _fmt(v), ha="center", va="center", fontsize=18, fontweight="bold",
                    color="white" if abs(v) > 0.6 * vmax else "black")
    for j in range(3):
        if show_nuc:
            v = nuc_row[j]
            ax.text(j, len(sites), _fmt(v) if np.isfinite(v) else "n/a", ha="center", va="center",
                    fontsize=18, fontweight="bold", color="white" if np.isfinite(v) and abs(v) > 0.6 * vmax else "black")
        else:
            ax.text(j, len(sites), "UNCORRECTED" if uncorrected else "n/a", ha="center", va="center",
                    fontsize=14, fontweight="bold", color="black")
    ax.set_xticks(range(3))
    ax.set_xticklabels([f"{l} ({LEVEL_MW[l]:.0f} MW)" for l in LEVELS], fontsize=18, fontweight="bold")
    ax.set_yticks(range(len(sites) + 1))
    ax.set_yticklabels([f"site {s}" for s in sites] + ["NUC gen 1 (overlay)"], fontsize=18, fontweight="bold")
    ax.set_xlabel("PEM MW level", fontsize=18, fontweight="bold")
    ax.set_ylabel("site (6 VRE) + nuclear stratum", fontsize=18, fontweight="bold")
    cd = defs["candidates"][c]
    ax.set_title(f"{c} {cd['name']} [{cd['unit']}], dir {cd['dir']}\n"
                 f"delta vs {base_label}: {CONTAMINATED}\n"
                 f"S' = {', '.join(f'{rec['S_prime'][l]:.2f}' if np.isfinite(rec['S_prime'][l]) else 'n/a' for l in LEVELS)}"
                 f"  |  W = {rec['W']:.2f}, exact p = {rec['W_p_exact']:.3f}",
                 fontsize=16, fontweight="bold")
    from matplotlib.ticker import FuncFormatter
    cb = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.03, format=FuncFormatter(lambda v, _p: _fmt(v)))
    cb.set_label(f"delta {c} [{cd['unit']}]", fontsize=18, fontweight="bold")
    cb.ax.tick_params(labelsize=16)
    for t in cb.ax.get_yticklabels():
        t.set_fontweight("bold")
    fig.savefig(path, dpi=110, bbox_inches="tight")
    plt.close(fig)


def plot_cluster_panel(M, defs, path, title, red_pairs=None):
    plt = _rc()
    from scipy.cluster.hierarchy import dendrogram, leaves_list, linkage
    from scipy.spatial.distance import squareform
    ids = list(M.columns)
    A = M.to_numpy(dtype=float)
    Dm = np.clip(1.0 - np.nan_to_num(A, nan=0.0), 0.0, 2.0)
    np.fill_diagonal(Dm, 0.0)
    Z = linkage(squareform(Dm, checks=False), method="complete")
    order = [ids[i] for i in leaves_list(Z)]
    n = len(order)
    labels = [f"{c} ({defs['candidates'][c]['dir']})" for c in order]
    fig = plt.figure(figsize=(max(16, 0.95 * n + 4), max(18, 1.05 * n + 6)))
    gs = fig.add_gridspec(2, 2, height_ratios=[1, 6], width_ratios=[30, 1], hspace=0.08, wspace=0.05)
    axd = fig.add_subplot(gs[0, 0])
    dendrogram(Z, ax=axd, no_labels=True, color_threshold=0.10, above_threshold_color="0.4")
    axd.axhline(0.10, color="red", lw=1.5, ls="--")
    axd.set_ylabel("1 - rho", fontsize=18, fontweight="bold")
    axd.tick_params(axis="y", labelsize=16)
    for t in axd.get_yticklabels():
        t.set_fontweight("bold")
    axd.set_title(title + "  (complete linkage; red line = rho 0.90)", fontsize=18, fontweight="bold")
    axd.spines[["top", "right"]].set_visible(False)
    ax = fig.add_subplot(gs[1, 0])
    cax = fig.add_subplot(gs[1, 1])
    B = M.loc[order, order].to_numpy(dtype=float)
    im = ax.imshow(np.nan_to_num(B, nan=0.0), vmin=-1, vmax=1, cmap="RdBu_r", aspect="equal")
    ax.set_xticks(range(n))
    ax.set_yticks(range(n))
    ax.set_xticklabels(labels, rotation=90, fontsize=18, fontweight="bold")
    ax.set_yticklabels(labels, fontsize=18, fontweight="bold")
    ax.set_xlabel("candidate (oriented: smaller is better)", fontsize=18, fontweight="bold")
    ax.set_ylabel("candidate", fontsize=18, fontweight="bold")
    for i in range(n):
        for j in range(n):
            v = B[i, j]
            txt = "n/a" if not np.isfinite(v) else f"{v:+.2f}"
            ax.text(j, i, txt, ha="center", va="center", fontsize=11, fontweight="bold",
                    color="white" if np.isfinite(v) and abs(v) > 0.6 else "black")
    if red_pairs:
        from matplotlib.patches import Rectangle
        pos = {c: k for k, c in enumerate(order)}
        for a, b in red_pairs:
            if a in pos and b in pos:
                for (i, j) in ((pos[a], pos[b]), (pos[b], pos[a])):
                    ax.add_patch(Rectangle((j - 0.5, i - 0.5), 1, 1, fill=False, edgecolor="lime", lw=3))
    cb = fig.colorbar(im, cax=cax)
    cb.set_label("rho (oriented Spearman)", fontsize=18, fontweight="bold")
    cb.ax.tick_params(labelsize=16)
    for t in cb.ax.get_yticklabels():
        t.set_fontweight("bold")
    fig.savefig(path, dpi=100, bbox_inches="tight")
    plt.close(fig)


# --------------------------------------------------------------------------
# driver
# --------------------------------------------------------------------------
def load_ruler(path):
    if not path:
        return None
    with open(path) as f:
        j = json.load(f)
    pc = j.get("per_candidate", j)
    out = {}
    for c, v in pc.items():
        if isinstance(v, dict):
            r = v.get("ruler")
        else:
            r = v
        out[c] = float(r) if r is not None else np.nan
    return out


def run(base=None, noise=None, wave=WAVE, extr=po.EXTR, waves=po.WAVES, out_dir=POOL,
        figs_dir=FIGS, freeze=FREEZE_HASH, verbose=True, make_figs=True):
    defs = po.load_defs()
    defs_md5 = assert_frozen_defs(freeze=freeze)
    os.makedirs(figs_dir, exist_ok=True)
    base_row, base_ident, base_label = resolve_base(base, extr, waves, defs)
    ruler = load_ruler(noise)

    wide = build_wave(wave, extr, waves, defs, verbose)
    wide.to_csv(os.path.join(out_dir, "pool_wavedD_wide.csv"), index=False)
    row_ident = sorted(set(wide["identity"]))
    contaminated = (base_ident.get("identity") != row_ident[0]) or len(row_ident) > 1
    delta_label = CONTAMINATED if contaminated else f"same identity ({base_ident.get('identity')})"
    # deltas (all 21 rows) vs the base
    dl = wide[po.KEY_COLS + ["level_id", "identity"]].copy()
    for c in GRADED + ["D3_gen1_starts", "D3_gen93_starts", "E8_slim_daily_settle_sd"]:
        b = float(base_row[c]) if pd.notna(base_row.get(c, np.nan)) else np.nan
        dl[c] = wide[c].astype(float) - b
    dl["delta_label"] = delta_label
    dl["base"] = base_label
    dl.to_csv(os.path.join(out_dir, "pool_wavedD_delta.csv"), index=False)

    vre = vre_rows(wide)
    nuc = nuc_rows(wide)
    assert len(vre) == 18 and len(nuc) == 3, (len(vre), len(nuc))
    suspect = list(wide.loc[wide["suspect"], "key"])
    dead31 = po.dead_list(pd.read_csv(os.path.join(out_dir, "pool_wide_v2.csv"),
                                      dtype={"replicate_of": str, "site": str}))
    dead_ids = sorted(dead31.loc[dead31["status"] == "DEAD", "id"])
    ids = [c for c in GRADED if c not in dead_ids]

    G_base = float(base_row["G_run_usd"])
    reads, long = level_reads(vre, base_row, ids, G_base, ruler)
    long.to_csv(os.path.join(out_dir, "pool_standings_levels.csv"), index=False)
    gap = gap_bound_reads(vre, base_row, G_base)
    gap.to_csv(os.path.join(out_dir, "pool_gap_bound_wavedD.csv"), index=False)
    shift = smoke_identity_shift(ids, defs=defs)
    shift.to_csv(os.path.join(out_dir, "pool_identity_shift_smoke.csv"), index=False)
    nuc_d = {}
    for c in ids:
        nuc_d[c] = {}
        for _, r in nuc.iterrows():
            b = float(base_row[c]) if pd.notna(base_row.get(c, np.nan)) else np.nan
            nuc_d[c][r["level_id"]] = float(r[c]) - b if pd.notna(r[c]) else np.nan

    alive = [c for c in ids if "X" in reads.get(c, {}) and not reads[c].get("status_data") and not reads[c].get("dead_on_wave")]
    cb = correlation_block(vre, alive, defs, base_row)
    cb["pooled"].round(4).to_csv(os.path.join(out_dir, "pool_spearman_wavedD_pooled.csv"))
    for l in LEVELS:
        cb["per_level"][l].round(4).to_csv(os.path.join(out_dir, f"pool_spearman_wavedD_{l}.csv"))
    cb["stratified"].round(4).to_csv(os.path.join(out_dir, "pool_spearman_wavedD_stratified.csv"))
    pairs = pair_table(cb, alive, defs)
    pairs.to_csv(os.path.join(out_dir, "pool_spearman_wavedD_pairs.csv"), index=False)

    tab, info = assemble_standings(reads, nuc_d, cb, pairs, defs, dead_ids, ids, base_label, shift, gap)
    tab["delta_label"] = delta_label
    tab["freeze_commit"] = freeze
    tab.to_csv(os.path.join(out_dir, "pool_standings.csv"), index=False)
    conf = conflict_table(pairs, info["survivors"], defs)
    conf.to_csv(os.path.join(out_dir, "pool_conflicts_wavedD.csv"), index=False)
    ed, rec = ed1b_table(tab, info, defs)
    ed.to_csv(os.path.join(out_dir, "pool_ed1b_decision.csv"), index=False)
    wall = wallclock_table(wide, extr, wave)
    wall.to_csv(os.path.join(out_dir, "pool_wavedD_wallclock.csv"), index=False)
    starts = starts_attribution(vre, po.run_dir(po.BASE_KEY, extr) if base is None else po.run_dir(base_label, extr), extr)
    starts.to_csv(os.path.join(out_dir, "pool_starts_attribution_wavedD.csv"), index=False)
    with open(os.path.join(out_dir, "pool_clusters_wavedD.json"), "w") as f:
        json.dump(po._json_safe({"clusters": info["clusters"], "survivor": info["survivor"], "survivors": info["survivors"],
                                 "eligible": info["eligible"], "members": info["members"],
                                 "redundant_pairs": list(pairs.loc[pairs["redundant_pair"], "pair"]),
                                 "tradeoff_pairs_le_-0.90": list(pairs.loc[pairs["tradeoff_le_-0.90"], "pair"]),
                                 "rule": defs["thresholds"]["redundancy"], "freeze_commit": freeze,
                                 "defs_md5": defs_md5, "base": base_label, "base_identity": base_ident,
                                 "row_identities": row_ident, "delta_label": delta_label, "suspect_rows": suspect,
                                 "dead_ids_A2": dead_ids, "E_D1b_recommended": rec,
                                 "git_head": po.git_head()}), f, indent=1)
        f.write("\n")
    if make_figs:
        for c in ids:
            rec_c = reads.get(c, {})
            if "D" not in rec_c:
                continue
            plot_heatmap(c, rec_c, nuc_d[c], defs, os.path.join(figs_dir, f"{c}.png"), base_label,
                         uncorrected=c in COST_FAMILY_UNCORRECTED)
        red = [(r["a"], r["b"]) for _, r in pairs[pairs["redundant_pair"]].iterrows()]
        plot_cluster_panel(cb["pooled"], defs, os.path.join(figs_dir, "clustermap_pooled.png"),
                           "wave D pooled (n = 18 VRE rows; size + site variation)", red)
        for l in LEVELS:
            plot_cluster_panel(cb["per_level"][l], defs, os.path.join(figs_dir, f"clustermap_{l}.png"),
                               f"wave D level {l} ({LEVEL_MW[l]:.0f} MW; n = 6 sites)", red)
        plot_cluster_panel(cb["stratified"], defs, os.path.join(figs_dir, "clustermap_stratified.png"),
                           "wave D level-stratified (within-level site ranks, n = 18)", red)
    return {"wide": wide, "tab": tab, "info": info, "pairs": pairs, "conf": conf, "ed": ed, "rec": rec,
            "wall": wall, "gap": gap, "shift": shift, "reads": reads, "cb": cb, "starts": starts,
            "base_row": base_row, "base_ident": base_ident, "base_label": base_label,
            "delta_label": delta_label, "dead_ids": dead_ids, "suspect": suspect, "nuc": nuc, "nuc_d": nuc_d}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--base", default=None,
                    help="base run: 'wave:index' or an extract dir (default base_2019_v2:1, identity v2). "
                         "A v3 base run makes every delta column same-identity.")
    ap.add_argument("--noise", default=None, help="prompt-52 ercot_noise.json (ruler_j per candidate)")
    ap.add_argument("--wave", default=WAVE)
    ap.add_argument("--freeze-hash", default=FREEZE_HASH)
    ap.add_argument("--no-figs", action="store_true")
    args = ap.parse_args(argv)
    R = run(base=args.base, noise=args.noise, wave=args.wave, freeze=args.freeze_hash, make_figs=not args.no_figs)
    t = R["tab"]
    print(f"base {R['base_label']} identity {R['base_ident'].get('identity')}; rows identity {sorted(set(R['wide']['identity']))}; "
          f"delta label: {R['delta_label']}")
    print(f"suspect rows: {R['suspect']}; dead (A2): {R['dead_ids']}")
    print(t[["id", "status", "S_prime_L60", "S_prime_L120", "S_prime_L180", "S_L60", "S_L120", "S_L180", "W", "W_p_exact",
             "cluster_id", "cluster_survivor"]].to_string(index=False))
    print("clusters:", R["info"]["clusters"], "survivors:", R["info"]["survivors"])
    print("E-D1b recommended:", R["rec"])
    print(R["conf"][["pair", "rho_pooled_n18", "rho_L60_n6", "rho_L120_n6", "rho_L180_n6", "label"]].to_string(index=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
