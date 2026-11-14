#!/usr/bin/env python3
"""Prompt 54: ERCOT GP fit / grade harness (plan §4, §5; contract 53-55 §6.2).

    # Part A smoke (synthetic 6-D function on a scratch Sobol set; no data):
    python analysis/ercot_gp/ercot_gp_status.py --synthetic --out-dir <scratch>
    # Part B (after the four gates; reads n0_E, random_E, ercot_noise.json):
    python analysis/ercot_gp/ercot_gp_status.py --real

Run in bogp-botorch (contract §1). The GP is the D-1025 `FlexGP`, imported
from the n0evidence clone's `initial_design/common.py` (generic parts only:
`FlexGP`, `metrics`, `binom_band`, `DEFAULT_CFG`); the I/O is ercot_gp_loader.

Pinned here, before any n0_E number (prompt 54 §2.2-§2.3):
- Arm set per objective j (plan §5), in tie-priority order (std before log1p,
  then m52 before rbf):
    default      m52+std, noise inferred, floor 1e-9 (house "inferred-only")
    m52+std+meas m52+std, floor = exact sd_j   iff sd_j > 0 AND df_j >= 3
    rbf+std      always
    m52+log1p    iff min y >= 0 and max y / max(min y, 1) > 10 (grading tier)
    rbf+log1p    same condition
- Selection: closed-form LOO NLPD in original units (`FlexGP.loo_t`, log1p
  change-of-variables term included). An alternative replaces the default
  only if its mean per-point NLPD is lower by > 2 paired se of the per-point
  difference; among alternatives that pass, those within 2 paired se of the
  best are tied and the first in priority order wins.
- Holdout: each committed config is scored ONCE per plan tier (n0 = 32, 48)
  against binom_band(48, level=0.90) = [43, 48]; every scoring is appended to
  exposure_ledger.csv; the 25th scoring, a repeat scoring, and any scoring
  after committed_configs.json exists are REFUSED (plan §4 retirement).
  Independence disclosure: the 48 residuals share one fitted model, so the
  binomial region treats them as independent; this is an approximation.
- Sufficiency curves: LOO only (LOO RMSE, LOO cov95) at nested Sobol prefixes
  16 / 24 / 32 / 40 / 48 with the config committed at n0 = 48.
- SUFFICIENCY_CRITERION (below) decides the E-D7 recommendation.
"""
import argparse
import csv
import datetime as _dt
import importlib.util
import json
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ERCOT = os.path.abspath(os.path.join(HERE, "..", ".."))
if ERCOT not in sys.path:
    sys.path.insert(0, ERCOT)

COMMON_PATH = os.environ.get(
    "D1025_COMMON",
    "/Users/yilu/Documents/GitHub/RTS-GMLC-n0evidence/trial_0826/campaign/"
    "analysis/initial_design/common.py")


def _import_common(path=COMMON_PATH):
    """Load D-1025 common.py under a private name; drop the RTS campaign dir it
    puts on sys.path so ERCOT's `analysis` namespace stays ERCOT's."""
    saved = list(sys.path)
    spec = importlib.util.spec_from_file_location("d1025_common", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    campaign = os.path.abspath(os.path.join(os.path.dirname(path), "..", ".."))
    sys.path[:] = [p for p in sys.path if os.path.abspath(p) != campaign] or saved
    return mod


common = _import_common()
FlexGP, DEFAULT_CFG, binom_band = common.FlexGP, common.DEFAULT_CFG, common.binom_band

import torch  # noqa: E402  (after common: same torch, threads set there)
import gpytorch  # noqa: E402

OUT = HERE
INFERRED_FLOOR = 1e-9            # house "inferred-only" floor (gp_status_47 pattern)
R_STAR = 10.0                    # plan §5 log1p inclusion ratio
MEAS_DF_MIN = 3                  # plan §5 measured-floor df rule
N_HOLDOUT = 48
HOLDOUT_LEVEL = 0.90             # plan §4 alpha = 0.10; NOT common's 0.95 default
HOLDOUT_BAR = binom_band(N_HOLDOUT, level=HOLDOUT_LEVEL)    # (43, 48)
EXPOSURE_CAP = 24                # plan §4
TIERS = (32, 48)                 # plan tiers: the only n0 the holdout is touched at
PREFIXES = (16, 24, 32, 40, 48)  # LOO sufficiency curve
SE_MULT = 2.0
SEED = 0
LEDGER = "exposure_ledger.csv"
COMMITTED = "committed_configs.json"
LEDGER_COLS = ["n_scoring", "utc", "objective", "n0", "arm", "cfg", "floor",
               "cov95", "n", "bar_lo", "bar_hi", "pass", "rmse_raw"]

SUFFICIENCY_CRITERION = (
    "32 is sufficient iff, for every objective, LOO cov95 at 32 is inside [28, 32] "
    "(binom.interval(0.90, 32, 0.95)) and LOO RMSE_32 / LOO RMSE_48 <= 1.1 and the "
    "committed config at 32 passes the holdout bar [43, 48]; otherwise the "
    "recommendation is 48.")
LOO_BAR_32 = binom_band(32, level=HOLDOUT_LEVEL)             # (28, 32)
RMSE_RATIO_MAX = 1.1


# --------------------------------------------------------------------------
# arms
# --------------------------------------------------------------------------
class Arm:
    def __init__(self, name, cfg, floor_mode):
        self.name, self.cfg, self.floor_mode = name, tuple(cfg), floor_mode

    @property
    def transform(self):
        return self.cfg[1]

    def floor(self, meas_sd):
        return float(meas_sd) if self.floor_mode == "measured" else INFERRED_FLOOR

    def __repr__(self):
        return f"Arm({self.name})"


DEFAULT_ARM = Arm("m52+std", DEFAULT_CFG, "inferred")
ARM_PRIORITY = ["m52+std", "m52+std+meas", "rbf+std", "m52+log1p", "rbf+log1p"]


def measured_floor(noise, obj):
    """(sd, df, use) from ercot_noise.json: use iff exact sd > 0 AND df >= 3."""
    if noise is None:
        return 0.0, 0, False
    sd = float(noise["noise_floor"]["floor"].get(obj, 0.0) or 0.0)
    df = int(noise["per_candidate"].get(obj, {}).get("exact_df", 0) or 0)
    return sd, df, bool(sd > 0 and df >= MEAS_DF_MIN)


def log1p_eligible(y):
    y = np.asarray(y, float)
    return bool(y.min() >= 0 and y.max() / max(y.min(), 1.0) > R_STAR)


def arm_set(y_grading, meas_use):
    """Plan §5 arms for one objective, in ARM_PRIORITY order (default first)."""
    arms = [DEFAULT_ARM]
    if meas_use:
        arms.append(Arm("m52+std+meas", DEFAULT_CFG, "measured"))
    arms.append(Arm("rbf+std", ("rbf", "std", "inferred", "none"), "inferred"))
    if log1p_eligible(y_grading):
        arms.append(Arm("m52+log1p", ("m52", "log1p", "inferred", "none"), "inferred"))
        arms.append(Arm("rbf+log1p", ("rbf", "log1p", "inferred", "none"), "inferred"))
    return arms


# --------------------------------------------------------------------------
# fit / LOO / predict
# --------------------------------------------------------------------------
def fit(U, y, arm, meas_sd=0.0):
    torch.manual_seed(SEED)
    return FlexGP(np.asarray(U, float), np.asarray(y, float), arm.floor(meas_sd), arm.cfg)


def nlpd_points(y, mu_t, sd_t, transform):
    """Per-point NLPD in ORIGINAL units (common.metrics convention)."""
    y = np.asarray(y, float)
    t = np.log1p(y) if transform == "log1p" else y
    z = (t - mu_t) / sd_t
    out = 0.5 * np.log(2 * np.pi * sd_t ** 2) + 0.5 * z ** 2
    if transform == "log1p":
        out = out + np.log1p(y)
    return out


def _report_floor(arm, meas_sd):
    return float(meas_sd) if arm.floor_mode == "measured" and meas_sd > 0 else np.nan


def loo(gp, y, arm, meas_sd=0.0):
    mu, sd, _ = gp.loo_t()
    pts = nlpd_points(y, mu, sd, arm.transform)
    with np.errstate(divide="ignore", invalid="ignore"):
        m, z = common.metrics(y, mu, sd, arm.transform, _report_floor(arm, meas_sd))
    assert abs(m["nlpd"] - float(pts.mean())) <= 1e-6 * max(1.0, abs(m["nlpd"]))
    return {"mu_t": mu, "sd_t": sd, "nlpd_pts": pts, "metrics": m, "z": z}


def noise_sd(gp):
    """Inferred noise sd in t units and in raw units (log1p: delta method at the
    training median, flagged approximate)."""
    s_t = float(np.sqrt(float(gp.lik.noise.detach())) * gp.sy)
    s_raw = s_t * (1.0 + gp.y_med) if gp.transform == "log1p" else s_t
    return s_t, s_raw


def latent_sd_t(gp, Uq):
    """Latent (noise-free) posterior sd, t units (gp_status_47 / bo_1021 convention)."""
    xq = torch.tensor((np.atleast_2d(Uq) - gp.mx) / gp.sx, dtype=torch.float32)
    with torch.no_grad(), gpytorch.settings.fast_pred_var():
        return gp.model(xq).stddev.numpy() * gp.sy


def halfwidth_raw(mu_t, sd_t, transform):
    if transform == "log1p":
        return 0.5 * (np.expm1(mu_t + 1.96 * sd_t) - np.expm1(mu_t - 1.96 * sd_t))
    return 1.96 * sd_t


# --------------------------------------------------------------------------
# selection
# --------------------------------------------------------------------------
def paired(a, b):
    """mean and se of the per-point difference a - b."""
    d = np.asarray(a, float) - np.asarray(b, float)
    return float(d.mean()), float(d.std(ddof=1) / np.sqrt(len(d)))


def select(U, y, arms, meas_sd=0.0):
    """Plan §5 LOO-NLPD selection. Returns (winner Arm, table rows, fits)."""
    assert arms[0].name == DEFAULT_ARM.name
    fits = {a.name: fit(U, y, a, meas_sd) for a in arms}
    loos = {a.name: loo(fits[a.name], y, a, meas_sd) for a in arms}
    base = loos[DEFAULT_ARM.name]["nlpd_pts"]
    rows, passing = [], []
    for a in arms:
        dm, se = paired(loos[a.name]["nlpd_pts"], base) if a is not arms[0] else (0.0, 0.0)
        beats = a is not arms[0] and dm < -SE_MULT * se
        if beats:
            passing.append(a)
        rows.append({"arm": a.name, "cfg": "/".join(a.cfg), "floor_mode": a.floor_mode,
                     "loo_nlpd_mean": float(loos[a.name]["nlpd_pts"].mean()),
                     "diff_vs_default": dm, "paired_se": se, "beats_default": bool(beats),
                     "loo_cov95": loos[a.name]["metrics"]["cov95"],
                     "loo_rmse": loos[a.name]["metrics"]["rmse"]})
    winner = arms[0]
    if passing:
        best = min(passing, key=lambda a: loos[a.name]["nlpd_pts"].mean())
        tied = [a for a in passing if a is best or
                paired(loos[a.name]["nlpd_pts"], loos[best.name]["nlpd_pts"])[0]
                < SE_MULT * paired(loos[a.name]["nlpd_pts"], loos[best.name]["nlpd_pts"])[1]]
        winner = min(tied, key=lambda a: ARM_PRIORITY.index(a.name))
    for r in rows:
        r["selected"] = r["arm"] == winner.name
    return winner, rows, fits, loos


# --------------------------------------------------------------------------
# holdout: exposure ledger + retirement
# --------------------------------------------------------------------------
class HoldoutRetired(RuntimeError):
    pass


def read_ledger(out_dir):
    p = os.path.join(out_dir, LEDGER)
    if not os.path.isfile(p):
        return pd.DataFrame(columns=LEDGER_COLS)
    return pd.read_csv(p)


def score_holdout(gp, arm, objective, n0, Uh, yh, out_dir, meas_sd=0.0):
    """ONE holdout scoring, appended to the ledger. Refuses after retirement
    (committed_configs.json exists), at the 25th scoring, on a repeat
    (objective, n0) scoring, and at a non-plan tier."""
    if os.path.isfile(os.path.join(out_dir, COMMITTED)):
        raise HoldoutRetired(f"{COMMITTED} exists: holdout RETIRED (plan §4)")
    if n0 not in TIERS:
        raise HoldoutRetired(f"n0 = {n0} is not a plan tier {TIERS}")
    led = read_ledger(out_dir)
    if len(led) >= EXPOSURE_CAP:
        raise HoldoutRetired(f"exposure budget spent ({len(led)} >= {EXPOSURE_CAP})")
    if ((led["objective"].astype(str) == objective)
            & (led["n0"].astype(int) == int(n0))).any():
        raise HoldoutRetired(f"{objective} at n0 = {n0} already scored once")
    yh = np.asarray(yh, float)
    assert len(yh) == N_HOLDOUT, f"holdout has {len(yh)} rows, plan §4 n_E = {N_HOLDOUT}"
    mu, sd = gp.predict_t(Uh)
    with np.errstate(divide="ignore", invalid="ignore"):
        m, z = common.metrics(yh, mu, sd, arm.transform, _report_floor(arm, meas_sd),
                              y_range=float(yh.max() - yh.min()))
    lo, hi = HOLDOUT_BAR
    ok = bool(lo <= m["cov95"] <= hi)
    row = {"n_scoring": len(led) + 1,
           "utc": _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds"),
           "objective": objective, "n0": int(n0), "arm": arm.name, "cfg": "/".join(arm.cfg),
           "floor": arm.floor(meas_sd), "cov95": m["cov95"], "n": m["n"], "bar_lo": lo,
           "bar_hi": hi, "pass": ok, "rmse_raw": m["rmse"]}
    p = os.path.join(out_dir, LEDGER)
    new = not os.path.isfile(p)
    with open(p, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=LEDGER_COLS)
        if new:
            w.writeheader()
        w.writerow(row)
    lat = latent_sd_t(gp, Uh)
    return {"metrics": m, "z": z, "mu_t": mu, "sd_t": sd, "pass": ok,
            "half_med_raw": float(np.median(halfwidth_raw(mu, sd, arm.transform))),
            "latent_share": float(np.median(lat / sd)), "ledger_row": row}


# --------------------------------------------------------------------------
# sufficiency
# --------------------------------------------------------------------------
def prefix_mask(sobol_index, n):
    s = np.asarray(sobol_index, int)
    m = s < n
    assert m.sum() == n, f"prefix {n}: {m.sum()} rows with sobol_index < {n}"
    return m


def sufficiency_curve(U, y, sobol_index, arm, meas_sd=0.0, prefixes=PREFIXES):
    out = []
    for n in prefixes:
        m = prefix_mask(sobol_index, n)
        gp = fit(U[m], y[m], arm, meas_sd)
        lm = loo(gp, y[m], arm, meas_sd)["metrics"]
        out.append({"n": n, "arm": arm.name, "loo_rmse": lm["rmse"],
                    "loo_cov95": lm["cov95"], "loo_nlpd": lm["nlpd"]})
    return out


def recommend(per_obj):
    """per_obj[obj] = {"loo_cov95_32", "loo_rmse_32", "loo_rmse_48", "holdout_pass_32"}.
    Returns (32 | 48, reasons) under SUFFICIENCY_CRITERION."""
    lo, hi = LOO_BAR_32
    reasons = []
    for obj, r in per_obj.items():
        if not lo <= r["loo_cov95_32"] <= hi:
            reasons.append(f"{obj}: LOO cov95 at 32 = {r['loo_cov95_32']} outside [{lo}, {hi}]")
        ratio = r["loo_rmse_32"] / r["loo_rmse_48"]
        if not ratio <= RMSE_RATIO_MAX:
            reasons.append(f"{obj}: LOO RMSE_32 / RMSE_48 = {ratio:.3f} > {RMSE_RATIO_MAX}")
        if not r["holdout_pass_32"]:
            reasons.append(f"{obj}: committed config at 32 fails the holdout bar {list(HOLDOUT_BAR)}")
    return (32 if not reasons else 48), reasons


# --------------------------------------------------------------------------
# committed configs (writing it retires the holdout)
# --------------------------------------------------------------------------
def write_committed(out_dir, entries, n0_rec, design_space_version):
    p = os.path.join(out_dir, COMMITTED)
    if os.path.isfile(p):
        raise HoldoutRetired(f"{p} exists; committed configs are written once")
    doc = {"identity": "v3", "design_space_version": design_space_version,
           "n0_tier_recommended": int(n0_rec), "E-D7_decided": None,
           "objectives": entries}
    with open(p, "w") as f:
        json.dump(doc, f, indent=1)
    return p


# --------------------------------------------------------------------------
# end-to-end
# --------------------------------------------------------------------------
def run(U, Y, sobol_index, Uh, Yh, noise, out_dir, design_space_version):
    """U / Y: the 48 grading rows (U, Y frames; sobol_index aligned); Uh / Yh: the
    48 holdout rows. Writes ercot_gp_status.csv, ercot_gp_selection.csv,
    ercot_gp_sufficiency.csv, exposure_ledger.csv, committed_configs.json (LAST)."""
    os.makedirs(out_dir, exist_ok=True)
    if os.path.isfile(os.path.join(out_dir, COMMITTED)):
        raise HoldoutRetired(f"{COMMITTED} exists in {out_dir}: holdout RETIRED")
    sob = np.asarray(sobol_index, int)
    assert len(U) == len(Y) == len(sob) == 48 and sorted(sob) == list(range(48)), (
        "grading tier = Sobol rows 0-47")
    Uv, Uhv = np.asarray(U, float), np.asarray(Uh, float)
    status, sel_rows, suff_rows, entries, per_obj = [], [], [], {}, {}
    for obj in Y.columns:
        y, yh = Y[obj].to_numpy(float), Yh[obj].to_numpy(float)
        sd_meas, df_meas, use_meas = measured_floor(noise, obj)
        arms = arm_set(y, use_meas)
        res = {}
        for n0 in TIERS:
            m = prefix_mask(sob, n0)
            winner, rows, fits, loos = select(Uv[m], y[m], arms, sd_meas)
            for r in rows:
                sel_rows.append({"objective": obj, "n0": n0, **r})
            gp = fits[winner.name]
            lm = loos[winner.name]["metrics"]
            h = score_holdout(gp, winner, obj, n0, Uhv, yh, out_dir, sd_meas)
            s_t, s_raw = noise_sd(gp)
            for scope, mm, half, lat in (
                    ("loo", lm, float(np.median(halfwidth_raw(
                        loos[winner.name]["mu_t"], loos[winner.name]["sd_t"],
                        winner.transform))), np.nan),
                    ("holdout", h["metrics"], h["half_med_raw"], h["latent_share"])):
                status.append({"objective": obj, "n0": n0, "scope": scope, "arm": winner.name,
                               "rmse_raw": mm["rmse"], "cov95": mm["cov95"], "n": mm["n"],
                               "nlpd": mm["nlpd"], "inferred_noise_sd_t": s_t,
                               "inferred_noise_sd_raw": s_raw,
                               "noise_raw_is_delta_method": winner.transform == "log1p",
                               "median_95_halfwidth_raw": half, "latent_share_median": lat,
                               "holdout_pass": h["pass"] if scope == "holdout" else np.nan})
            res[n0] = {"arm": winner, "loo": lm, "holdout": h}
        curve = sufficiency_curve(Uv, y, sob, res[48]["arm"], sd_meas)
        for c in curve:
            suff_rows.append({"objective": obj, **c})
        per_obj[obj] = {"loo_cov95_32": res[32]["loo"]["cov95"],
                        "loo_rmse_32": res[32]["loo"]["rmse"],
                        "loo_rmse_48": res[48]["loo"]["rmse"],
                        "holdout_pass_32": res[32]["holdout"]["pass"]}
        res_obj = (res, sd_meas, df_meas, use_meas)
        entries[obj] = res_obj
    n0_rec, reasons = recommend(per_obj)
    committed = {}
    for obj, (res, sd_meas, df_meas, use_meas) in entries.items():
        r = res[n0_rec]
        a = r["arm"]
        committed[obj] = {
            "cfg": list(a.cfg), "arm": a.name,
            "floor": float(a.floor(sd_meas)) if a.floor_mode == "measured" else 0.0,
            "floor_rule": "exact sd_j > 0 AND df_j >= 3 else inferred-only 1e-9",
            "exact_sd": sd_meas, "exact_df": df_meas, "measured_arm_included": use_meas,
            "loo_nlpd_mean": r["loo"]["nlpd"],
            "holdout_cov95": [int(r["holdout"]["metrics"]["cov95"]), N_HOLDOUT],
            "holdout_rmse": r["holdout"]["metrics"]["rmse"],
            "exposure_rows": [int(res[n]["holdout"]["ledger_row"]["n_scoring"]) for n in TIERS],
            "by_tier": {str(n): {"arm": res[n]["arm"].name, "cfg": list(res[n]["arm"].cfg),
                                 "holdout_cov95": int(res[n]["holdout"]["metrics"]["cov95"]),
                                 "holdout_pass": bool(res[n]["holdout"]["pass"])}
                        for n in TIERS}}
    pd.DataFrame(status).to_csv(os.path.join(out_dir, "ercot_gp_status.csv"), index=False)
    pd.DataFrame(sel_rows).to_csv(os.path.join(out_dir, "ercot_gp_selection.csv"), index=False)
    pd.DataFrame(suff_rows).to_csv(os.path.join(out_dir, "ercot_gp_sufficiency.csv"), index=False)
    with open(os.path.join(out_dir, "ercot_gp_recommendation.json"), "w") as f:
        json.dump({"E-D7_recommendation": n0_rec, "criterion": SUFFICIENCY_CRITERION,
                   "reasons_for_48": reasons, "per_objective": per_obj}, f, indent=1)
    path = write_committed(out_dir, committed, n0_rec, design_space_version)   # LAST
    return {"recommendation": n0_rec, "reasons": reasons, "committed": path,
            "status": pd.DataFrame(status), "selection": pd.DataFrame(sel_rows),
            "sufficiency": pd.DataFrame(suff_rows)}


# --------------------------------------------------------------------------
# synthetic (Part A smoke) and real (Part B) inputs
# --------------------------------------------------------------------------
def synthetic_inputs(seed=54):
    """6-D test functions on a scratch Sobol set (64 -> first 48) and a uniform
    holdout of 48. 'pos' is positive with max/min > 10 (exercises log1p arms)."""
    from scipy.stats import qmc
    U = qmc.Sobol(d=6, scramble=True, seed=seed).random_base2(6)[:48]
    Uh = np.random.default_rng(seed + 1).random((48, 6))

    def f(u):
        u = np.atleast_2d(u)
        smooth = 1e6 * (2.0 - u[:, 0] ** 2 + 0.6 * np.sin(3 * u[:, 1]) - 0.4 * u[:, 2] * u[:, 3]
                        + 0.2 * u[:, 4] - 0.1 * u[:, 5])
        pos = 50.0 * np.exp(2.5 * u[:, 0] + 1.5 * u[:, 3] * u[:, 4])
        return pd.DataFrame({"S1": smooth, "S2": pos})
    rng = np.random.default_rng(seed + 2)
    Y = f(U)
    Y["S1"] += rng.normal(0, 2e3, len(Y))
    Yh = f(Uh)
    Yh["S1"] += rng.normal(0, 2e3, len(Yh))
    sob = np.arange(48)
    cols = [f"u_{i}" for i in range(6)]
    return (pd.DataFrame(U, columns=cols), Y, sob, pd.DataFrame(Uh, columns=cols), Yh)


def real_inputs(design_space, noise_path, objectives=None):
    from analysis.ercot_gp.ercot_gp_loader import load, read_design_space
    ds = read_design_space(design_space)
    bad = {k: v["status"] for k, v in ds["objectives"].items()
           if any(w in v.get("status", "") for w in ("PENDING", "PROVISIONAL"))}
    if bad and objectives is None:
        raise SystemExit(f"Part B gate (iv): objective list not final in {design_space}: {bad}")
    if not os.path.isfile(noise_path):
        raise SystemExit(f"Part B gate (ii): {noise_path} missing (run read_noise.py first)")
    with open(noise_path) as f:
        noise = json.load(f)
    floors = {k: float(v) for k, v in noise["noise_floor"]["floor"].items()}
    _, U, Y, meta = load(["n0_E"], objectives, design_space, floors=floors)
    g = meta["sobol_index"].astype(str) != ""
    g &= meta["tier"].isin(["nav", "grading"])
    U, Y, meta_g = U[g], Y[g], meta[g]
    sob = meta_g["sobol_index"].astype(int).to_numpy()
    keep = sob < 48
    _, Uh, Yh, meta_h = load(["random_E"], objectives, design_space, floors=floors)
    assert (meta_h["tier"] == "holdout").all() and len(meta_h) == N_HOLDOUT
    for m, name in ((meta_g, "n0_E"), (meta_h, "random_E")):
        assert not m["suspect"].any(), f"{name}: SUSPECT rows {list(m.index[m['suspect']])}"
    return (U[keep], Y[keep], sob[keep], Uh, Yh, noise, ds["contract_version"])


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--synthetic", action="store_true")
    g.add_argument("--real", action="store_true")
    ap.add_argument("--out-dir", default=OUT)
    ap.add_argument("--design-space", default=os.path.join(ERCOT, "waves", "design_space_E.json"))
    ap.add_argument("--noise", default=os.path.join(ERCOT, "analysis", "noise_v3", "ercot_noise.json"))
    a = ap.parse_args(argv)
    if a.synthetic:
        if os.path.abspath(a.out_dir) == os.path.abspath(OUT):
            raise SystemExit("--synthetic writes a ledger: pass a scratch --out-dir")
        U, Y, sob, Uh, Yh = synthetic_inputs()
        res = run(U, Y, sob, Uh, Yh, None, a.out_dir, "synthetic")
    else:
        U, Y, sob, Uh, Yh, noise, ver = real_inputs(a.design_space, a.noise)
        res = run(U, Y, sob, Uh, Yh, noise, a.out_dir, ver)
    print(res["status"].to_string(index=False))
    print(f"E-D7 recommendation: n0 = {res['recommendation']}; reasons for 48: {res['reasons']}")
    print(f"wrote {res['committed']} (holdout RETIRED)")


if __name__ == "__main__":
    main()
