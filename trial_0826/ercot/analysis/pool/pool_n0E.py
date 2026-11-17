"""Prompt 62 Part B: ERCOT objective pool on the n0_E population (zero simulation).

Reads the 48 n0_E grading rows at POOL level only (per-run candidate values via
`pool_standings.build_wave("n0_E")`: pool_objectives.build_pool + the
pool_full_metrics.json merge for E8/E9/N5). Fits no GP. Never reads random_E
(no `land_ercot_n0.load`, no `ercot_gp_loader.load`).

Rules: plan ERCOT_BO_PLAN.md AMENDMENT 2026-11-17 (verbatim prompt 62 v1.1
§3.2-§3.4); the sha256 of that block is asserted before anything is read.
Candidates, directions, priorities and global_order: pool_definitions.json at
f76d897 (asserted).

Pinned implementation choices (stated here because the rule text leaves them open):
- B_j (61 §3): the 8 perturbed deltas minus the two design-2 copies (site 206,
  structural zeros); NaN deltas (D1/D2 at the nuclear design) dropped.
  No input md5 is recorded for the noise runs, so the "input md5" of the
  excluded pair is the md5 of the effective PEM slice
  (min(cap, wind_t), max(0, wind_t - cap)) over RT + DA wind for site 206
  (multi_pem/parameters.py `_update_renewable_generator`); the output
  overall.csv md5 equality is asserted as well.
- Mantel: a FRESH default_rng(6262) per id (results do not depend on id order);
  permutation of the y labels; p = (1 + #{r_perm >= r_obs}) / (1 + 9,999).
- Var(y_j) for the signal share uses ddof = 1.
- f_hat(T): PCHIP through (median T, median y) of 6 equal-count bins (8 rows
  each, by rank of T), extrapolate=True outside the outer bin medians.
- Isotonic LOO prediction at T_i: linear interpolation of the 47-row fit,
  clamped at the ends (np.interp). R^2 = 1 - SSE / sum (y - mean y)^2.
- Fisher-z intervals use se = 1 / sqrt(n - 3) for every Spearman rho.
- R-3: BORDERLINE pair = raw rho in the exact band where its 90 % Fisher-z
  interval contains 0.90; it takes wave D's frozen-rule verdict
  (pool_spearman_wavedD_pairs.csv `redundant_pair`) AND needs residual
  rho >= 0.50 (the X1-E1 sentence applied to every borderline pair).
- Zero-bar ids (B_j = 0): READABLE (RULER=0) iff range >= 1 natural unit,
  DEAD ON n0_E if constant; they never carry RESPONDS IN BOX and are not
  seat-eligible.
- R-4: a BORDERLINE responder (IDR/B_j in [2, 3)) is seat-eligible only when
  its wave-D B_j verdict is readable (a second piece of evidence).
  Families are walked in the order of their first directed non-guardrail
  member in global_order. A family whose directed non-guardrail members ALL
  sit in n0_E clusters with another family consumes no seat (the 57
  mechanism, e.g. X1 -> E1); a family
  with NO responder holds an EMPTY seat (M < 4; never refilled by the next
  family); the E seat is E1 or HALT FOR PI.

Run: cd trial_0826/ercot && /opt/anaconda3/bin/python analysis/pool/pool_n0E.py
"""

import argparse
import datetime as dt
import hashlib
import json
import os
import subprocess
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ERCOT = os.path.abspath(os.path.join(HERE, "..", ".."))
if ERCOT not in sys.path:
    sys.path.insert(0, ERCOT)
import pool_objectives as po  # noqa: E402
import pool_standings as ps  # noqa: E402

WAVE = "n0_E"
N_ROWS = 48
FREEZE = "f76d897"
PLAN = os.path.join(ERCOT, "ERCOT_BO_PLAN.md")
AMEND_TITLE = ("## AMENDMENT 2026-11-17 — E-D1b input widened to n0_E (pool level); "
               "new n0_E rules; Part C disclosure")
AMEND_SHA256 = "8dd06917415c8cf6e8f7081adcee862e3d2ae6d08cf4eaa8dc0a9fa2cc8a1d1e"
NOISE = os.path.join(ERCOT, "analysis", "noise_v3", "ercot_noise.json")
FIGS = os.path.join(po.POOL, "figs", "n0E")

STRUCTURAL_ZERO_DESIGN = 2          # noise_v3 design D2 = site 206 (noise memo F6)
STRUCTURAL_ZERO_SITE = "206"
ZERO_BAR_EXPECTED = {"E5", "E9", "R1", "R3"}
GUARDRAILS = ("R1", "R2")           # plan §1.3
E_SEAT = "E1"                       # plan §1.2 final (READABLE -> E1)
POCKET_SITES = ("mw_163", "mw_270", "mw_274")   # bus 120
D3_COLS = ("D3_gen1_starts", "D3_gen93_starts")

IDR_BARS, BORDER_BARS, STRONG_BARS = 2.0, 3.0, 10.0
MANTEL_SEED, N_PERM, MANTEL_ALPHA = 6262, 9999, 0.01
SIGNAL_SHARE_MIN = 0.5
N_BINS = 6
ETA_NULL_MEAN, ETA_NULL_95 = 0.107, 0.23
RHO_RED, RHO_RESID, RHO_TRADE = 0.90, 0.50, -0.50
CI_BORDER = 0.90                    # two-sided 90 % Fisher-z interval for R-3
MAX_SEATS = 4

SAMPLING_FACTS = [
    "At n = 48, P(rho_hat >= 0.90 | rho = 0.80) = 0.8 %; P(rho_hat >= 0.90 | rho = 0.90) = 44 %.",
    "Sobol points are not i.i.d.; the null bands are mildly conservative.",
    "Solver chatter attenuates rho (permissive for R4 / N1).",
    "Multiplicity over 231 pairs: expected false redundancy < 0.01, false trade-off about 0.07; no correction.",
    "False RESPONDS under pure chatter: about 0.1 % per id for IDR at 1x chatter (3.5 % for the raw range).",
]
DISCLOSURES = [
    "B_j is transferred from single-site off-slate designs (noise_v3, n = 6 deltas after the D2 exclusion); "
    "box chatter cannot be measured on n0_E (no replicates).",
    "rho(T, s) = +0.39 in this design (s = bus-120 share): size and composition are not orthogonal.",
    "COMPOSITION and 54's L flag come from the same 48 rows: never two independent pieces of evidence; "
    "61 tests location directly.",
    "SIZE SHARE, COMPOSITION and the isotonic LOO R^2 are descriptive only.",
    "Not blind: per-candidate ideal / nadir / R over these 48 rows were seen before the rules "
    "(plan AMENDMENT 2026-11-16 / 2026-11-17).",
]


# --------------------------------------------------------------------------
# pre-registration guards
# --------------------------------------------------------------------------
def amendment_block(plan_path=PLAN):
    text = open(plan_path, encoding="utf-8").read()
    assert text.count(AMEND_TITLE) == 1, "plan must carry exactly one AMENDMENT 2026-11-17 block"
    blk = text[text.index(AMEND_TITLE):]
    nxt = blk.find("\n## AMENDMENT ", len(AMEND_TITLE))
    return blk if nxt < 0 else blk[:nxt + 1]


def assert_amendment(plan_path=PLAN, expect=AMEND_SHA256):
    h = hashlib.sha256(amendment_block(plan_path).encode("utf-8")).hexdigest()
    assert h == expect, f"amendment block sha256 {h} != pinned {expect}"
    return h


def sha256_file(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def git_short(path=None, ref="HEAD"):
    cmd = ["git", "-C", ERCOT, "log", "-1", "--format=%h", ref] + (["--", path] if path else [])
    return subprocess.run(cmd, capture_output=True, text=True).stdout.strip() or "uncommitted"


# --------------------------------------------------------------------------
# X (design only) and the bar B_j
# --------------------------------------------------------------------------
def load_X(waves=po.WAVES):
    p = os.path.join(waves, WAVE, "design_matrix.csv")
    dm = pd.read_csv(p)
    assert len(dm) == N_ROWS and (dm["tier"] == "grading").all()
    mw = [c for c in dm.columns if c.startswith("mw_")]
    u = [c for c in dm.columns if c.startswith("u_")]
    assert len(mw) == 6 and len(u) == 6
    T = dm[mw].sum(axis=1).to_numpy(dtype=float)
    assert np.allclose(T, dm["pem_mw"].to_numpy(dtype=float), atol=1e-6)
    X = pd.DataFrame({"index": dm["index"].astype(int), "T": T,
                      "s": dm[list(POCKET_SITES)].sum(axis=1).to_numpy(dtype=float) / T})
    for c in u:
        X[c] = dm[c].to_numpy(dtype=float)
    X.attrs["u_cols"] = u
    X.attrs["design_sha256"] = sha256_file(p)
    return X.set_index("index", drop=False)


def pem_slice_md5(site, cap, data_dir=po.DATA):
    h = hashlib.md5()
    for f in ("REAL_TIME_wind.csv", "DAY_AHEAD_wind.csv"):
        w = pd.read_csv(os.path.join(data_dir, f), usecols=[site])[site].to_numpy(dtype=float)
        h.update(np.minimum(cap, w).tobytes())
        h.update(np.maximum(0.0, w - cap).tobytes())
    return h.hexdigest()


def bars(noise_path=NOISE, data_dir=po.DATA, ids=None):
    """B_j = max(3 sigma_hat_j, max |delta_ij|), D2 structural zeros excluded (61 §3)."""
    j = json.load(open(noise_path))
    pdl = j["perturbed_deltas"]
    dn = np.array([d["design_no"] for d in pdl])
    runs = {r["key"]: r for r in j["runs"]}
    excl = []
    for d in pdl:
        if d["design_no"] != STRUCTURAL_ZERO_DESIGN:
            continue
        a, b = runs[d["key"]], runs[d["ref_key"]]
        assert a["site"] == b["site"] == STRUCTURAL_ZERO_SITE
        assert a["overall_md5"] == b["overall_md5"], (d["key"], "outputs differ: not a structural zero")
        ma, mb = pem_slice_md5(a["site"], d["pem_mw"], data_dir), pem_slice_md5(b["site"], d["pem_mw_ref"], data_dir)
        assert ma == mb, (d["key"], "effective PEM input differs: not a structural zero")
        excl.append({"key": d["key"], "ref_key": d["ref_key"], "input_md5": ma, "overall_md5": a["overall_md5"]})
    assert len(excl) == 2
    rows = []
    for c in ids or list(j["per_candidate"]):
        v = j["per_candidate"][c]
        assert float(v["exact_pooled_sd"]) == 0.0, f"{c}: exact_pooled_sd > 0 -> STOP (61 §3 guard)"
        sig = np.array([np.nan if x is None else x for x in v["perturbed_delta_signed"]], float)
        chk = np.array([np.nan if d.get(c) is None else d[c] for d in pdl], float)
        assert np.allclose(sig, chk, equal_nan=True), c
        k = sig[(dn != STRUCTURAL_ZERO_DESIGN) & np.isfinite(sig)]
        s = float(np.sqrt(np.mean(k ** 2)))
        B = float(max(3.0 * s, np.abs(k).max()))
        r = v.get("ruler")
        r = np.nan if r is None else float(r)
        rows.append({"id": c, "n_delta": len(k), "sigma_hat": s, "B_j": B, "ruler_57": r,
                     "B_over_ruler": B / r if r and np.isfinite(r) and r > 0 else np.nan,
                     "in_ruler_zero": c in j.get("ruler_zero", [])})
    out = pd.DataFrame(rows).set_index("id")
    out.attrs["excluded"] = excl
    return out


# --------------------------------------------------------------------------
# Y (pool level)
# --------------------------------------------------------------------------
def load_wide(verbose=False):
    return ps.build_wave(wave=WAVE, verbose=verbose)


def check_wide(wide, X):
    assert len(wide) == N_ROWS, len(wide)
    assert int(wide["suspect"].sum()) == 0, "SUSPECT rows on n0_E"
    nan = [c for c in po.CAND_IDS if wide[c].isna().any()]
    assert not nan, f"NaN in graded ids {nan}"
    w = wide.copy()
    w["index"] = w["index"].astype(int)
    w = w.set_index("index", drop=False).loc[X.index]
    return w


def line_summary_reader(key, extr=po.EXTR):
    return pd.read_csv(os.path.join(po.run_dir(key, extr), "line_summary.csv"))


def n1_off(wide, reader=line_summary_reader, data_dir=po.DATA):
    """N1_off = N1 - N4 (non-pocket congested line-hours), cross-checked per run."""
    pl = set(po.pocket_lines(data_dir, 120))
    off = (wide["N1"] - wide["N4"]).astype(float)
    for key, v in zip(wide["key"], off):
        ls = reader(key)
        got = float(ls.loc[~ls["Line"].astype(str).isin(pl), "hours_ge_99pct"].sum())
        assert got == v, (key, got, v)
    return off


# --------------------------------------------------------------------------
# statistics
# --------------------------------------------------------------------------
def _pairs(n):
    return np.triu_indices(n, k=1)


def _spearman(a, b):
    from scipy.stats import spearmanr
    a, b = np.asarray(a, float), np.asarray(b, float)
    if np.ptp(a) == 0 or np.ptp(b) == 0:
        return np.nan
    return float(spearmanr(a, b).statistic)


def fisher_ci(r, n, level=0.95):
    from scipy.stats import norm
    if not np.isfinite(r) or abs(r) >= 1:
        return (r, r)
    z, h = np.arctanh(r), norm.ppf(0.5 + level / 2) / np.sqrt(n - 3)
    return (float(np.tanh(z - h)), float(np.tanh(z + h)))


def border_band(n=N_ROWS, rho=RHO_RED, level=CI_BORDER):
    """raw rho values whose `level` Fisher-z interval contains `rho`."""
    return fisher_ci(rho, n, level)


def mantel(y, U, seed=MANTEL_SEED, n_perm=N_PERM, chunk=1000):
    """One-sided Mantel: Spearman between |y_i - y_k| and ||u_i - u_k|| (fresh rng per call)."""
    from scipy.stats import rankdata
    y = np.asarray(y, float)
    if np.ptp(y) == 0:
        return np.nan, np.nan
    I, K = _pairs(len(y))
    du = np.sqrt(((U[I] - U[K]) ** 2).sum(axis=1))
    ru = rankdata(du)
    ru = (ru - ru.mean()) / ru.std()

    def stat(Yp):
        r = rankdata(np.abs(Yp[:, I] - Yp[:, K]), axis=1)
        r = (r - r.mean(axis=1, keepdims=True)) / r.std(axis=1, keepdims=True)
        return (r * ru).mean(axis=1)

    obs = float(stat(y[None, :])[0])
    rng = np.random.default_rng(seed)
    ge, done = 0, 0
    while done < n_perm:
        m = min(chunk, n_perm - done)
        P = np.argsort(rng.random((m, len(y))), axis=1)
        ge += int((stat(y[P]) >= obs - 1e-12).sum())
        done += m
    return obs, (1 + ge) / (1 + n_perm)


def bin_pchip(T, y, n_bins=N_BINS):
    from scipy.interpolate import PchipInterpolator
    T, y = np.asarray(T, float), np.asarray(y, float)
    bins = np.array_split(np.argsort(T, kind="stable"), n_bins)
    xk = np.array([np.median(T[b]) for b in bins])
    yk = np.array([np.median(y[b]) for b in bins])
    assert np.all(np.diff(xk) > 0)
    return PchipInterpolator(xk, yk, extrapolate=True)(T)


def size_share(T, y):
    y = np.asarray(y, float)
    vy = np.var(y)
    if vy == 0:
        return np.nan, np.nan
    eta = 1.0 - np.var(y - bin_pchip(T, y)) / vy
    return float(eta), float((eta - ETA_NULL_MEAN) / (1 - ETA_NULL_MEAN))


def iso_loo_r2(T, y):
    from scipy.optimize import isotonic_regression
    T, y = np.asarray(T, float), np.asarray(y, float)
    if np.ptp(y) == 0:
        return np.nan
    inc = not (_spearman(y, T) < 0)
    pred = np.empty_like(y)
    for i in range(len(y)):
        m = np.arange(len(y)) != i
        o = np.argsort(T[m], kind="stable")
        fit = isotonic_regression(y[m][o], increasing=inc).x
        pred[i] = np.interp(T[i], T[m][o], fit)
    return float(1.0 - ((y - pred) ** 2).sum() / ((y - y.mean()) ** 2).sum())


def oriented(wide, ids, defs):
    return ps.oriented_frame(wide, ids, defs, base_row=None)


def residualise(O, T):
    return pd.DataFrame({c: O[c].to_numpy(dtype=float) - bin_pchip(T, O[c]) for c in O.columns}, index=O.index)


# --------------------------------------------------------------------------
# per-id table (§3.3 RESPONDS / SIZE / COMPOSITION)
# --------------------------------------------------------------------------
def per_id(wide, X, B, ids):
    U = X[X.attrs["u_cols"]].to_numpy(dtype=float)
    T, s = X["T"].to_numpy(dtype=float), X["s"].to_numpy(dtype=float)
    rs = s - bin_pchip(T, s)
    rows = []
    for c in ids:
        y = wide[c].to_numpy(dtype=float)
        b = float(B.loc[c, "B_j"])
        q10, q90 = np.quantile(y, [0.10, 0.90])
        idr, rng_ = float(q90 - q10), float(np.ptp(y))
        r_m, p_m = mantel(y, U)
        vy = float(np.var(y, ddof=1))
        share = 1.0 - (B.loc[c, "sigma_hat"] ** 2 / 2.0) / vy if vy > 0 else np.nan
        eta, eta_adj = size_share(T, y)
        rc = _spearman(y - bin_pchip(T, y), rs)
        lo, hi = fisher_ci(rc, len(y))
        rec = {"id": c, "B_j": b, "IDR": idr, "range": rng_, "mantel_r": r_m, "mantel_p": p_m,
               "signal_share": share, "eta2_T": eta, "eta2_T_adj": eta_adj, "iso_loo_R2": iso_loo_r2(T, y),
               "comp_rho": rc, "comp_ci_lo": lo, "comp_ci_hi": hi}
        if b > 0:
            rec["IDR_over_B"], rec["range_over_B"] = idr / b, rng_ / b
            ok = (idr >= IDR_BARS * b and np.isfinite(p_m) and p_m <= MANTEL_ALPHA
                  and np.isfinite(share) and share >= SIGNAL_SHARE_MIN)
            rec["responds"] = bool(ok)
            rec["respond_label"] = ("RESPONDS IN BOX" + (" (STRONG)" if idr >= STRONG_BARS * b else "")
                                    + (" (BORDERLINE)" if idr < BORDER_BARS * b else "")) if ok else "NOT RESPONDS"
            rec["borderline"] = bool(ok and idr < BORDER_BARS * b)
        else:
            rec["IDR_over_B"] = rec["range_over_B"] = np.nan
            rec["responds"], rec["borderline"] = False, False
            rec["respond_label"] = ("DEAD ON n0_E (constant)" if rng_ == 0 else
                                    ("READABLE (RULER=0)" if rng_ >= 1.0 else "UNREADABLE (RULER=0, range < 1 unit)"))
        rows.append(rec)
    return pd.DataFrame(rows).set_index("id")


# --------------------------------------------------------------------------
# pairs (§3.3 REDUNDANT / SIZE-CO-MONOTONE / TRADE-OFF, R-3)
# --------------------------------------------------------------------------
def wave_d_pairs(path=os.path.join(po.POOL, "pool_spearman_wavedD_pairs.csv")):
    p = pd.read_csv(path)
    return {frozenset((a, b)): bool(r) for a, b, r in zip(p["a"], p["b"], p["redundant_pair"])}


def pair_reads(raw, resid, ids, defs, wd_red):
    lo, hi = border_band()
    rows = []
    for i, a in enumerate(ids):
        for b in ids[i + 1:]:
            r, e = float(raw.loc[a, b]), float(resid.loc[a, b])
            both = defs["candidates"][a]["dir"] in ("min", "max") and defs["candidates"][b]["dir"] in ("min", "max")
            border = bool(np.isfinite(r) and lo <= r <= hi)
            wd = wd_red.get(frozenset((a, b)))
            if border:
                red = bool(wd) and np.isfinite(e) and e >= RHO_RESID
                basis = f"R-3 BORDERLINE: wave-D verdict {wd} + residual"
            else:
                red = bool(np.isfinite(r) and r >= RHO_RED and np.isfinite(e) and e >= RHO_RESID)
                basis = "n0_E rule"
            cmono = bool(np.isfinite(r) and r >= RHO_RED and not (np.isfinite(e) and e >= RHO_RESID))
            rl, rh = fisher_ci(r, N_ROWS)
            el, eh = fisher_ci(e, N_ROWS)
            rows.append({"pair": f"{a}|{b}", "a": a, "b": b, "both_directed": both,
                         "rho_raw": r, "rho_raw_lo95": rl, "rho_raw_hi95": rh,
                         "rho_resid": e, "rho_resid_lo95": el, "rho_resid_hi95": eh,
                         "borderline_R3": border, "wave_d_redundant": wd,
                         "redundant_pair": bool(both and red), "redundant_basis": basis if both else "",
                         "size_co_monotone": bool(both and cmono and not red),
                         "tradeoff_size": bool(both and np.isfinite(r) and r <= RHO_TRADE),
                         "tradeoff_composition": bool(both and np.isfinite(e) and e <= RHO_TRADE),
                         "wave_d_redundant_only": bool(both and wd and not red)})
    return pd.DataFrame(rows)


# --------------------------------------------------------------------------
# wave-D columns (committed 54 rerun outputs; read only)
# --------------------------------------------------------------------------
def wave_d_columns(B, path=os.path.join(po.POOL, "pool_standings.csv")):
    st = pd.read_csv(path).set_index("id")
    out = pd.DataFrame(index=st.index)
    out["waveD_label_57"] = st["status"]
    for l in ps.LEVELS:
        out[f"waveD_range_over_B_{l}"] = st[f"range_{l}"] / B["B_j"].reindex(st.index).replace(0, np.nan)
    rb = out[[f"waveD_range_over_B_{l}" for l in ps.LEVELS]]
    out["waveD_B_readable"] = (rb >= IDR_BARS).sum(axis=1) >= 2
    out["waveD_B_verdict"] = np.where(out["waveD_B_readable"], "READABLE (2 of 3)", "UNREADABLE (B_j)")
    for l in ps.LEVELS:
        c = f"gap_readable_sites_{l}"
        if c in st.columns:
            out[f"waveD_{c}"] = st[c]
    return out


# --------------------------------------------------------------------------
# adjudication (§3.4) and the E-D1b table (§5)
# --------------------------------------------------------------------------
def survivors(pairs, tab, defs, directed_alive):
    cl = ps.clusters_from_pairs(pairs, directed_alive)
    elig = {c for c in directed_alive if bool(tab.loc[c, "responds"])}
    out = []
    for k, m in enumerate(sorted(cl, key=lambda m: min(defs["global_order"].index(x) for x in m)), 1):
        out.append({"cluster": f"n0E-C{k}", "members": m, "survivor": ps.survivor(m, defs["global_order"], elig)})
    return out


def seat_walk(tab, defs, red_to, clusters=()):
    cands = defs["candidates"]
    go = defs["global_order"]
    fam_first = {}
    for c in go:
        f = cands[c]["family"]
        if f != "D" and cands[c]["dir"] in ("min", "max") and c not in GUARDRAILS:
            fam_first.setdefault(f, go.index(c))
    seats, log = [], []
    for fam in sorted(fam_first, key=fam_first.get):
        if len(seats) >= MAX_SEATS:
            log.append(f"family {fam}: not reached (cap {MAX_SEATS})")
            continue
        mem = [c for c in go if cands[c]["family"] == fam and cands[c]["dir"] in ("min", "max")
               and c not in GUARDRAILS]
        if fam == "E":
            e = tab.loc[E_SEAT]
            ok = bool(e["responds"]) and E_SEAT not in red_to and (not e["borderline"] or bool(e["waveD_B_readable"]))
            seats.append({"family": "E", "seat": E_SEAT if ok else "HALT FOR PI",
                          "reason": "plan §1.2 final (E1)" if ok else
                          "E1 fails R-1/R-4 -> HALT FOR PI (never passed to E3/E4)"})
            continue
        in_cl = {m: set(cl["members"]) for cl in clusters for m in cl["members"]}
        absorbed = all(m in in_cl and any(cands[o]["family"] != fam for o in in_cl[m]) for m in mem)
        if absorbed:
            log.append(f"family {fam}: every member is in a cluster with another family "
                       + ", ".join(f"{c}->{red_to.get(c, 'no survivor')}" for c in mem) + " (no seat consumed)")
            continue
        resp = [c for c in mem if bool(tab.loc[c, "responds"])
                and (not tab.loc[c, "borderline"] or bool(tab.loc[c, "waveD_B_readable"]))]
        if not resp:
            seats.append({"family": fam, "seat": "EMPTY",
                          "reason": "no member RESPONDS IN BOX (non-borderline or wave-D-backed) -> M < 4; "
                                    "the next family does not fill it until the PI decides"})
            continue
        elig = [c for c in resp if c not in red_to]
        if not elig:
            log.append(f"family {fam}: every responder REDUNDANT -> "
                       + ", ".join(f"{c}->{red_to[c]}" for c in resp) + " (no seat consumed)")
            continue
        lost = [f"{c} ({'REDUNDANT->' + red_to[c] if c in red_to else tab.loc[c, 'respond_label']})"
                for c in mem if c != elig[0] and go.index(c) < go.index(elig[0])]
        seats.append({"family": fam, "seat": elig[0], "reason": "first eligible in global_order"
                      + (f"; ahead of it: {'; '.join(lost)}" if lost else "")})
    M = sum(1 for s in seats if s["seat"] not in ("EMPTY", "HALT FOR PI"))
    return seats, M, log


def status_column(tab, defs, dead57, red_to, seated, cmono_with):
    out = {}
    for c in tab.index:
        if c in dead57 or tab.loc[c, "respond_label"].startswith("DEAD"):
            out[c] = "DEAD"
        elif c in GUARDRAILS:
            out[c] = "GUARDRAIL"
        elif c in red_to:
            out[c] = f"REDUNDANT->{red_to[c]}"
        elif c in seated:
            out[c] = "OBJECTIVE"
        elif c in cmono_with:
            out[c] = f"SIZE-CO-MONOTONE (with {', '.join(cmono_with[c])})"
        else:
            out[c] = "DIAGNOSTIC"
    return pd.Series(out)


def r5_conflicts(tab):
    rows = []
    for c in tab.index:
        if not (tab.loc[c, "B_j"] > 0):
            continue
        wd, nb = bool(tab.loc[c, "waveD_B_readable"]), bool(tab.loc[c, "responds"])
        if wd != nb:
            rows.append({"id": c, "waveD_B_verdict": tab.loc[c, "waveD_B_verdict"],
                         "n0E_verdict": tab.loc[c, "respond_label"],
                         "R1_label": ("DIAGNOSTIC: readable as single sites <= 180 MW, chatter-level across the box"
                                      if wd else "BOX-ONLY RESPONSE (eligible)")})
    return pd.DataFrame(rows, columns=["id", "waveD_B_verdict", "n0E_verdict", "R1_label"])


# --------------------------------------------------------------------------
# figures (assert-before-draw)
# --------------------------------------------------------------------------
def plot_idr(tab, path):
    plt = ps._rc()
    t = tab[tab["B_j"] > 0].sort_values("IDR_over_B")
    v = t["IDR_over_B"].to_numpy(dtype=float)
    assert np.allclose(v, (t["IDR"] / t["B_j"]).to_numpy(dtype=float))
    fig, ax = plt.subplots(figsize=(14, max(8, 0.45 * len(t) + 2)))
    col = ["tab:blue" if r else "0.6" for r in t["responds"]]
    ax.barh(range(len(t)), np.maximum(v, 1e-3), color=col)
    for x, ls in ((IDR_BARS, "--"), (BORDER_BARS, ":"), (STRONG_BARS, "-.")):
        ax.axvline(x, color="red", ls=ls, lw=2)
    ax.set_xscale("log")
    ax.set_yticks(range(len(t)))
    ax.set_yticklabels(list(t.index), fontsize=16, fontweight="bold")
    ax.set_xlabel("IDR / B_j on n0_E (Q90 - Q10 over 48 rows; lines 2, 3, 10)", fontsize=18, fontweight="bold")
    ax.set_ylabel("candidate", fontsize=18, fontweight="bold")
    ax.set_title("n0_E response in the box (blue = RESPONDS IN BOX)", fontsize=18, fontweight="bold")
    for lab in ax.get_xticklabels() + ax.get_yticklabels():
        lab.set_fontweight("bold")
    ax.tick_params(labelsize=16)
    fig.savefig(path, dpi=100, bbox_inches="tight")
    plt.close(fig)


# --------------------------------------------------------------------------
# writer
# --------------------------------------------------------------------------
def _f(v, d=3):
    if isinstance(v, (bool, np.bool_)):
        return str(bool(v))
    if v is None or (isinstance(v, float) and not np.isfinite(v)):
        return "n/a"
    if isinstance(v, (int, np.integer)):
        return str(v)
    if isinstance(v, (float, np.floating)):
        a = abs(v)
        return f"{v:.4g}" if (a >= 1e4 or (a and a < 1e-2)) else f"{v:.{d}f}"
    return str(v)


def _md_table(df, cols):
    lines = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for _, r in df.iterrows():
        lines.append("| " + " | ".join(_f(r[c]) for c in cols) + " |")
    return "\n".join(lines)


def write_md(path, info, B, tab, pairs, clusters, seats, M, walk_log, conf, nfam, comb):
    lo, hi = border_band()
    L = [f"# POOL_N0E_STANDINGS — objective pool on the n0_E population (prompt 62 Part B)", "",
         f"Read date (UTC): {info['read_utc']}. Rules: plan AMENDMENT 2026-11-17 (commit (i) "
         f"{info['sha_i']}, block sha256 `{info['amend_sha256']}`); script + tests commit (ii) {info['sha_ii']}. "
         f"Definitions frozen at {FREEZE}. `waves/n0_E/design_matrix.csv` sha256 `{info['design_sha256']}`. "
         f"git HEAD at the read {info['git_head']}.", "",
         "Input: 48 n0_E grading rows at pool level (`pool_standings.build_wave(\"n0_E\")`); no GP fitted; "
         "random_E not read; holdout exposure 0 of 24.", "",
         "## 1. Disclosures", ""] + [f"- {d}" for d in DISCLOSURES] + [
         "", "Sampling facts:", ""] + [f"- {d}" for d in SAMPLING_FACTS] + [
         "", f"R-3 BORDERLINE band (raw rho whose 90 % Fisher-z interval contains 0.90, n = 48): "
         f"[{lo:.3f}, {hi:.3f}] (prompt text: about 0.86-0.93).", "",
         "## 2. Bar B_j (61 §3, D2 structural zeros excluded) beside 57's median ruler (never merged)", "",
         "Excluded pair(s): " + "; ".join(f"{e['key']} vs {e['ref_key']} (effective-input md5 {e['input_md5'][:8]}, "
                                          f"overall md5 {e['overall_md5'][:8]})" for e in B.attrs["excluded"]), "",
         _md_table(B.reset_index(), ["id", "n_delta", "sigma_hat", "B_j", "ruler_57", "B_over_ruler", "in_ruler_zero"]),
         "", f"B_j / ruler range over ids with both > 0: {np.nanmin(B['B_over_ruler']):.2f}-"
             f"{np.nanmax(B['B_over_ruler']):.2f}x.", "",
         "## 3. Per candidate (RESPONDS IN BOX, SIZE SHARE, COMPOSITION)", "",
         f"RESPONDS IN BOX iff IDR >= {IDR_BARS:g} B_j AND Mantel one-sided p <= {MANTEL_ALPHA} "
         f"(9,999 permutations, default_rng({MANTEL_SEED}) per id) AND signal share >= {SIGNAL_SHARE_MIN}; "
         f"BORDERLINE iff IDR/B_j in [2, 3); STRONG iff IDR >= 10 B_j. eta2_T null mean {ETA_NULL_MEAN}, "
         f"null 95th percentile {ETA_NULL_95}.", "",
         _md_table(tab.reset_index(), ["id", "B_j", "IDR", "IDR_over_B", "range_over_B", "mantel_p", "signal_share",
                                       "respond_label", "eta2_T", "eta2_T_adj", "iso_loo_R2", "comp_rho",
                                       "comp_ci_lo", "comp_ci_hi"]), "",
         f"D3 check (no bar): {info['d3']}.", "",
         f"N1_off = N1 - N4 cross-checked against line_summary.csv on all 48 runs: range "
         f"{info['n1off_min']:.0f}-{info['n1off_max']:.0f} line-hours.", "",
         "## 4. Pairs (directed ids; oriented Spearman, raw and T-residual)", ""]
    sel = pairs[pairs["both_directed"] & (pairs["redundant_pair"] | pairs["size_co_monotone"] | pairs["borderline_R3"]
                                          | pairs["tradeoff_size"] | pairs["tradeoff_composition"]
                                          | pairs["wave_d_redundant_only"])]
    L += [_md_table(sel, ["pair", "rho_raw", "rho_raw_lo95", "rho_raw_hi95", "rho_resid", "rho_resid_lo95",
                          "rho_resid_hi95", "borderline_R3", "wave_d_redundant", "redundant_pair", "size_co_monotone",
                          "tradeoff_size", "tradeoff_composition", "wave_d_redundant_only"]) if len(sel) else
          "No pair meets any pair rule.", "", "Clusters (complete linkage on the REDUNDANT relation):", ""]
    L += [f"- {c['cluster']}: {', '.join(c['members'])} -> survivor {c['survivor']}" for c in clusters] or ["- none"]
    L += ["", "## 5. Adjudication with wave D (R-1 ... R-5)", "", "R-5 conflict rows (both verdicts printed):", "",
          _md_table(conf, list(conf.columns)) if len(conf) else "none", "",
          "N family (N1 = N4 + N1_off):", ""] + [f"- {x}" for x in nfam] + ["",
          "## E. E-D1b decision table (Parts A + B; Part C appended when it lands)", "",
          f"Seat walk (R-4): M = {M}" + (" — M != 4 reopens plan §6.4 gate numbers for the PI." if M != 4 else "."), ""]
    L += [f"- {s['family']}: **{s['seat']}** — {s['reason']}" for s in seats] + [f"- {x}" for x in walk_log]
    L += ["", _md_table(comb.reset_index(), list(comb.reset_index().columns)), "",
          "## Deviations", ""] + [f"- {d}" for d in info["deviations"]] + [""]
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(L))


# --------------------------------------------------------------------------
# driver
# --------------------------------------------------------------------------
def run(wide=None, out_dir=po.POOL, figs_dir=FIGS, line_reader=line_summary_reader, make_figs=True,
        noise=NOISE, waves=po.WAVES, data_dir=po.DATA, wave_d_dir=po.POOL, plan=PLAN, verbose=True):
    amend = assert_amendment(plan)
    ps.assert_frozen_defs()
    defs = po.load_defs()
    X = load_X(waves)
    assert abs(_spearman(X["T"], X["s"]) - 0.39) < 0.01, "rho(T, s) != +0.39"
    ids = list(po.CAND_IDS)
    B = bars(noise, data_dir, ids)
    zero = set(B.index[B["B_j"] == 0])
    assert zero == ZERO_BAR_EXPECTED, f"zero-bar set {sorted(zero)} != {sorted(ZERO_BAR_EXPECTED)}"
    if wide is None:
        wide = load_wide()
    wide = check_wide(wide, X)
    off = n1_off(wide, line_reader, data_dir)
    d3 = {c: sorted(set(wide[c].astype(float))) for c in D3_COLS}

    tab = per_id(wide, X, B, ids)
    wd = wave_d_columns(B, os.path.join(wave_d_dir, "pool_standings.csv"))
    tab = tab.join(wd, how="left")
    tab["family"] = [defs["candidates"][c]["family"] for c in tab.index]
    tab["dir"] = [defs["candidates"][c]["dir"] for c in tab.index]
    tab["global_order"] = [defs["global_order"].index(c) + 1 for c in tab.index]

    dead57 = set(pd.read_csv(os.path.join(wave_d_dir, "pool_dead_list_v2.csv"))
                 .query("status == 'DEAD'")["id"])
    alive = [c for c in defs["global_order"] if c in ids and c not in dead57 and np.ptp(wide[c].astype(float)) > 0]
    O = oriented(wide, alive, defs)
    raw = ps.spearman_matrix(O)
    resid = ps.spearman_matrix(residualise(O, X["T"].to_numpy(dtype=float)))
    pairs = pair_reads(raw, resid, alive, defs, wave_d_pairs(os.path.join(wave_d_dir, "pool_spearman_wavedD_pairs.csv")))
    directed = [c for c in alive if defs["candidates"][c]["dir"] in ("min", "max")]
    clusters = survivors(pairs, tab, defs, directed)
    red_to = {}
    for cl in clusters:
        for m in cl["members"]:
            if cl["survivor"] is not None and m != cl["survivor"]:
                red_to[m] = cl["survivor"]
    tab["cluster"] = pd.Series({m: cl["cluster"] for cl in clusters for m in cl["members"]})
    tab["survivor"] = pd.Series({m: cl["survivor"] for cl in clusters for m in cl["members"]})
    seats, M, walk_log = seat_walk(tab, defs, red_to, clusters)
    seated = {s["seat"] for s in seats}
    go = [c for c in defs["global_order"] if c in tab.index]
    cmono_with = {}
    for _, p in pairs[pairs["size_co_monotone"]].iterrows():
        a, b = sorted((p["a"], p["b"]), key=go.index)
        cmono_with.setdefault(b, []).append(a)
    tab["status"] = status_column(tab, defs, dead57, red_to, seated, cmono_with)
    tr = {c: [] for c in tab.index}
    for _, p in pairs.iterrows():
        for lab in ("tradeoff_size", "tradeoff_composition"):
            if p[lab]:
                tr[p["a"]].append(f"{lab.split('_')[1]}:{p['b']}")
                tr[p["b"]].append(f"{lab.split('_')[1]}:{p['a']}")
    tab["tradeoffs"] = pd.Series({c: "; ".join(v) for c, v in tr.items()})
    conf = r5_conflicts(tab)

    nfam = []
    for c in ("N1", "N4"):
        nfam.append(f"{c}: B_j {tab.loc[c, 'B_j']:.4g}, IDR/B_j {_f(tab.loc[c, 'IDR_over_B'])}, "
                    f"range/B_j {_f(tab.loc[c, 'range_over_B'])}, {tab.loc[c, 'respond_label']}, status {tab.loc[c, 'status']}")
    nfam.append(f"N1_off (diagnostic, not a pool id): range {off.min():.0f}-{off.max():.0f}, "
                f"IDR {np.quantile(off, 0.9) - np.quantile(off, 0.1):.0f}")
    if "N4" in red_to and red_to["N4"] == "N1" or "N1" in red_to and red_to["N1"] == "N4":
        nfam.append(f"N1-N4 REDUNDANT: the 57 priority keeps N1, the noisier member (bar {tab.loc['N1', 'B_j']:.4g} "
                    f"vs {tab.loc['N4', 'B_j']:.4g}); a PI override is a recorded rule change.")

    g = wide["G_run_usd"].astype(float).to_numpy()
    pair_g = float(np.median((g[:, None] + g[None, :])[np.triu_indices(len(g), 1)]))
    tab["n0E_cost_gap_read"] = ""
    tab.loc[E_SEAT, "n0E_cost_gap_read"] = (f"IDR {tab.loc[E_SEAT, 'IDR']:.4g} vs median pair bound "
                                            f"G_a+G_b {pair_g:.4g} ({tab.loc[E_SEAT, 'IDR'] / pair_g:.2f}x; evidence only)")
    comb_cols = (["family", "global_order", "waveD_label_57"] + [f"waveD_range_over_B_{l}" for l in ps.LEVELS]
                 + ["waveD_B_verdict", "IDR_over_B", "mantel_p", "signal_share", "eta2_T", "comp_rho", "cluster",
                    "survivor", "tradeoffs", "n0E_cost_gap_read", "status"])
    comb = tab.reindex(go)[comb_cols]
    comb.index.name = "id"

    deviations = [
        "B_j with D2 excluded gives N2 3.0, N1 114.9, N4 37.0; prompt 62 v1.1 quotes 2.60 / 99.5 / 32, which are "
        "the 8-value (D2-included) numbers. The pinned definition (61 §3 / contract addendum) is applied; "
        "54's `ercot_gp_mechanism.readability_bar` uses all 8 values (not edited here; reported).",
        f"B_j / ruler spans {np.nanmin(B['B_over_ruler']):.2f}-{np.nanmax(B['B_over_ruler']):.2f}x "
        "(prompt text 3.5-11.5x); V3's tiny ruler sets the top.",
        "No input md5 exists for the noise runs; the D2 exclusion asserts the md5 of the effective PEM slice "
        "(RT + DA wind, site 206) plus equal overall.csv md5.",
        f"R-3 band computed exactly ([{border_band()[0]:.3f}, {border_band()[1]:.3f}]); prompt text says about 0.86-0.93.",
    ]
    info = {"read_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
            "sha_i": git_short(PLAN), "sha_ii": git_short(os.path.abspath(__file__)),
            "git_head": git_short(), "amend_sha256": amend, "design_sha256": X.attrs["design_sha256"],
            "d3": d3, "n1off_min": float(off.min()), "n1off_max": float(off.max()), "deviations": deviations}

    os.makedirs(out_dir, exist_ok=True)
    std_cols = ["family", "dir", "global_order", "B_j", "IDR", "IDR_over_B", "range_over_B", "mantel_r", "mantel_p",
                "signal_share", "respond_label", "eta2_T", "eta2_T_adj", "iso_loo_R2", "comp_rho", "comp_ci_lo",
                "comp_ci_hi", "cluster", "survivor", "tradeoffs", "status"]
    tab.reindex(go)[[c for c in std_cols]].rename_axis("id").to_csv(os.path.join(out_dir, "pool_n0E_standings.csv"))
    raw.to_csv(os.path.join(out_dir, "pool_spearman_n0E_raw.csv"))
    resid.to_csv(os.path.join(out_dir, "pool_spearman_n0E_resid.csv"))
    comb.to_csv(os.path.join(out_dir, "pool_ed1b_combined.csv"))
    write_md(os.path.join(out_dir, "POOL_N0E_STANDINGS.md"), info, B, tab.reindex(go), pairs, clusters, seats, M,
             walk_log, conf, nfam, comb)
    if make_figs:
        os.makedirs(figs_dir, exist_ok=True)
        dl = [c for c in directed]
        red_pairs = [(p["a"], p["b"]) for _, p in pairs[pairs["redundant_pair"]].iterrows()]
        ps.plot_cluster_panel(raw.loc[dl, dl], defs, os.path.join(figs_dir, "n0E_clustermap_raw.png"),
                              "n0_E raw oriented rho (n = 48)", red_pairs=red_pairs)
        ps.plot_cluster_panel(resid.loc[dl, dl], defs, os.path.join(figs_dir, "n0E_clustermap_resid.png"),
                              "n0_E T-residual oriented rho (n = 48)", red_pairs=red_pairs)
        plot_idr(tab, os.path.join(figs_dir, "n0E_idr_over_B.png"))
    if verbose:
        print(B[["B_j", "ruler_57", "B_over_ruler"]].to_string())
        print(tab.reindex(go)[["IDR_over_B", "mantel_p", "signal_share", "respond_label", "status"]].to_string())
        for s in seats:
            print(f"seat {s['family']}: {s['seat']} — {s['reason']}")
        print(f"M = {M}")
    return {"B": B, "tab": tab, "pairs": pairs, "clusters": clusters, "seats": seats, "M": M,
            "conflicts": conf, "comb": comb, "info": info}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--no-figs", action="store_true")
    a = ap.parse_args(argv)
    run(make_figs=not a.no_figs)
    return 0


if __name__ == "__main__":
    sys.exit(main())
