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


def score_holdout(gp, arm, objective, n0, Uh, yh, out_dir, meas_sd=0.0, tiers=TIERS):
    """ONE holdout scoring, appended to the ledger. Refuses after retirement
    (committed_configs.json exists), at the 25th scoring, on a repeat
    (objective, n0) scoring, and at a tier not in `tiers` (default: the plan
    tiers 32 / 48; prompt 54 v3.3 §5.3 adds n* as a third tier, disclosed as a
    plan §10 amendment)."""
    if os.path.isfile(os.path.join(out_dir, COMMITTED)):
        raise HoldoutRetired(f"{COMMITTED} exists: holdout RETIRED (plan §4)")
    if n0 not in tiers:
        raise HoldoutRetired(f"n0 = {n0} is not a plan tier (admitted {tuple(tiers)})")
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
            res[n0] = {"arm": winner, "loo": lm, "holdout": h, "gp": gp, "loo_full": loos[winner.name]}
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
    return {"recommendation": n0_rec, "reasons": reasons, "committed": path, "committed_doc": committed,
            "status": pd.DataFrame(status), "selection": pd.DataFrame(sel_rows),
            "sufficiency": pd.DataFrame(suff_rows), "per_obj": per_obj, "entries": entries,
            "inputs": {"U": Uv, "Y": Y, "sob": sob, "Uh": Uhv, "Yh": Yh}, "out_dir": out_dir,
            "design_space_version": design_space_version}


# --------------------------------------------------------------------------
# Part B deliverables (prompt 54 §3.3-§3.6): noise cross-check, figures, status page,
# E-D7 pi-agenda draft, mechanism page. Written AFTER committed_configs.json; none of
# them changes it.
# --------------------------------------------------------------------------
def noise_crosscheck(noise, entries, n0=48):
    """Descriptive only (§3.3; adds no arm): inferred GP noise (committed config at n0)
    vs the 52 measured values — exact pooled sd (the floor), perturbed pooled sd, and a
    per-level standardized-residual table (perturbed signed deltas / inferred sd)."""
    rows = []
    for obj, (res, sd_meas, df_meas, use_meas) in entries.items():
        gp = res[n0]["gp"]
        s_t, s_raw = noise_sd(gp)
        pc = (noise or {}).get("per_candidate", {}).get(obj, {})
        pert_sd = float(pc.get("pooled_sd", np.nan)) if pc else np.nan
        levels = pc.get("levels", []) if pc else []
        deltas = np.asarray(pc.get("perturbed_delta_signed", []), float) if pc else np.array([])
        z = deltas / s_raw if s_raw > 0 and len(deltas) else np.array([])
        trig = pc.get("trigger", {}) if pc else {}
        rows.append({"objective": obj, "arm": res[n0]["arm"].name, "n0": n0,
                     "inferred_noise_sd_raw": s_raw, "inferred_is_delta_method": gp.transform == "log1p",
                     "exact_sd_floor": float(sd_meas), "exact_df": int(df_meas), "measured_arm_included": bool(use_meas),
                     "perturbed_pooled_sd": pert_sd,
                     "ratio_inferred_over_perturbed": (s_raw / pert_sd if np.isfinite(pert_sd) and pert_sd > 0 else np.nan),
                     "per_level_sd": [float(lv.get("sd", np.nan)) for lv in levels],
                     "n_perturbed": int(len(deltas)), "z_mean_abs": (float(np.mean(np.abs(z))) if len(z) else np.nan),
                     "z_max_abs": (float(np.max(np.abs(z))) if len(z) else np.nan),
                     "trigger_fires": bool(trig.get("fires", False)), "trigger_verdict": trig.get("verdict", ""),
                     "note": ("52 trigger fired: reported only; any model change needs a plan amendment (plan 5 / 10)"
                              if trig.get("fires") else "")})
    return pd.DataFrame(rows)


def _fmt3(v):
    return "" if not np.isfinite(v) else f"{v:.3f}"


def _bold(ax):
    for t in ax.get_xticklabels() + ax.get_yticklabels():
        t.set_fontweight("bold")
    ax.grid(alpha=0.3)


def fig_parity(entries, Uh, Yh, out_dir, tiers=TIERS):
    """Holdout parity per objective x tier: y vs predictive median with the TOTAL 95 %
    band (noise included) and the LATENT band (dual band). Big figure, bold labels
    and ticks, assert-before-draw."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.size": 13, "font.weight": "bold", "axes.labelweight": "bold", "axes.titleweight": "bold"})
    objs = list(entries)
    fig, axes = plt.subplots(len(tiers), len(objs), figsize=(5.2 * len(objs), 4.6 * len(tiers)), squeeze=False)
    for i, n0 in enumerate(tiers):
        for j, obj in enumerate(objs):
            res = entries[obj][0][n0]
            gp, arm, h = res["gp"], res["arm"], res["holdout"]
            yh = Yh[obj].to_numpy(float)
            mu_t, sd_t = h["mu_t"], h["sd_t"]
            lat = latent_sd_t(gp, Uh)
            med = common.median_raw(mu_t, arm.transform)
            lo_t, hi_t = mu_t - 1.96 * sd_t, mu_t + 1.96 * sd_t
            lo_l, hi_l = mu_t - 1.96 * lat, mu_t + 1.96 * lat
            if arm.transform == "log1p":
                lo_t, hi_t, lo_l, hi_l = (np.expm1(v) for v in (lo_t, hi_t, lo_l, hi_l))
            for v in (med, lo_t, hi_t, lo_l, hi_l):
                assert np.isfinite(v).all(), (obj, n0)
            o = np.argsort(med)
            ax = axes[i, j]
            ax.fill_between(np.arange(len(o)), lo_t[o], hi_t[o], color="C0", alpha=0.18, label="95 % total band")
            ax.fill_between(np.arange(len(o)), lo_l[o], hi_l[o], color="C0", alpha=0.35, label="95 % latent band")
            ax.plot(np.arange(len(o)), med[o], color="C0", lw=2, label="predictive median")
            ax.plot(np.arange(len(o)), yh[o], "o", color="C3", ms=4, label="holdout y")
            m = h["metrics"]
            ax.set_title(f"{obj} n0={n0} {arm.name}\ncov95 {m['cov95']}/{m['n']} {'PASS' if h['pass'] else 'FAIL'} "
                         f"[{HOLDOUT_BAR[0]}, {HOLDOUT_BAR[1]}]; RMSE {m['rmse']:.3g}", fontsize=11)
            ax.set_xlabel("holdout row (sorted by prediction)")
            ax.set_ylabel(obj)
            _bold(ax)
            if i == 0 and j == 0:
                ax.legend(fontsize=9)
    fig.tight_layout()
    path = os.path.join(out_dir, "fig_parity_holdout.png")
    fig.savefig(path, dpi=120)
    plt.close(fig)
    return path


def fig_sufficiency(suff, out_dir, prefixes=PREFIXES):
    """LOO sufficiency curves per objective: LOO RMSE (relative to n = 48) and LOO cov95
    with the per-n binomial 90 % bands."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.size": 13, "font.weight": "bold", "axes.labelweight": "bold", "axes.titleweight": "bold"})
    objs = list(suff["objective"].unique())
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.2))
    for obj in objs:
        d = suff[suff["objective"] == obj].sort_values("n")
        r48 = float(d.loc[d["n"] == max(prefixes), "loo_rmse"].iloc[0])
        assert np.isfinite(d["loo_rmse"]).all() and r48 > 0
        axes[0].plot(d["n"], d["loo_rmse"] / r48, "o-", lw=2, label=obj)
        axes[1].plot(d["n"], d["loo_cov95"] / d["n"], "o-", lw=2, label=obj)
    axes[0].axhline(RMSE_RATIO_MAX, color="k", ls="--", lw=1.5, label=f"ratio {RMSE_RATIO_MAX} (criterion at 32)")
    axes[0].set_xlabel("n (Sobol prefix)"); axes[0].set_ylabel("LOO RMSE / LOO RMSE at 48"); axes[0].set_title("LOO RMSE (nested prefixes)")
    for n in prefixes:
        lo, hi = binom_band(n, level=HOLDOUT_LEVEL)
        axes[1].plot([n, n], [lo / n, hi / n], color="0.4", lw=6, alpha=0.4)
    axes[1].axhline(0.95, color="k", ls=":", lw=1)
    axes[1].set_xlabel("n (Sobol prefix)"); axes[1].set_ylabel("LOO cov95 / n"); axes[1].set_title("LOO coverage (grey = binom 90 % band per n)")
    for ax in axes:
        _bold(ax); ax.legend(fontsize=9)
    fig.tight_layout()
    path = os.path.join(out_dir, "fig_sufficiency_loo.png")
    fig.savefig(path, dpi=120)
    plt.close(fig)
    return path


def pi_agenda_row(n0_rec, reasons, date=None):
    date = date or _dt.date.today().isoformat()
    why = ("criterion met for every objective" if not reasons else "; ".join(reasons))
    return (f"| {date} | E-D7 | **ERCOT navigation tier (prompt 54 Part B)** | Recommendation **n0 = {n0_rec}** under the "
            f"pinned criterion: \"{SUFFICIENCY_CRITERION}\" — {why}. Kay decides; 55 Part B waits on it "
            f"(`committed_configs.json[\"E-D7_decided\"]`). | analysis/ercot_gp/ERCOT_GP_STATUS.md |")


def mechanism_shares(res_entries, n0, gen_pmax):
    from analysis.ercot_gp import ercot_gp_mechanism as M
    return {obj: M.posterior_shares(res[n0]["gp"], gen_pmax) for obj, (res, *_rest) in res_entries.items()}


def status_md(res, noise, cross, figs, mech_md, pi_row, extra):
    st, sel, suff = res["status"], res["selection"], res["sufficiency"]
    com = res["committed_doc"]
    L = ["# ERCOT_GP_STATUS — prompt 54 Part B (plan 4 / 5; contract 6.2)", "",
         f"Design space {res['design_space_version']}; committed configs `committed_configs.json` (written LAST; the holdout is "
         f"RETIRED); E-D7 recommendation **n0 = {res['recommendation']}**. "
         + ("Synthetic smoke (no campaign data)." if extra.get("synthetic") else
            f"Data: n0_E grading tier 48 rows (refused {extra.get('n_refused_n0')}), random_E holdout 48 rows (refused "
            f"{extra.get('n_refused_random')}); max R1 shed {extra.get('r1_max')} MWh, max R2 {extra.get('r2_max')} MWh."), "",
         "## 1. Arms and LOO selection (plan 5; LOO NLPD, > 2 paired se, tie order std < log1p, m52 < rbf)", "",
         "| objective | n0 | arm | cfg | floor | LOO NLPD mean | diff vs default | paired se | beats default | LOO cov95 | LOO RMSE | selected |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for _, r in sel.iterrows():
        L.append(f"| {r['objective']} | {r['n0']} | {r['arm']} | {r['cfg']} | {r['floor_mode']} | {r['loo_nlpd_mean']:.4f} | "
                 f"{r['diff_vs_default']:+.4f} | {r['paired_se']:.4f} | {r['beats_default']} | {r['loo_cov95']} | {r['loo_rmse']:.4g} | "
                 f"{'**yes**' if r['selected'] else ''} |")
    L += ["", f"## 2. Grading (gp_status_47 column set; holdout ONCE per committed config per tier vs [{HOLDOUT_BAR[0]}, {HOLDOUT_BAR[1]}] = binom_band(48, level 0.90))", "",
          "| objective | n0 | scope | arm | RMSE raw | cov95 / n | NLPD | inferred noise sd (raw) | median 95 % half-width | latent share | holdout pass |",
          "|---|---|---|---|---|---|---|---|---|---|---|"]
    for _, r in st.iterrows():
        L.append(f"| {r['objective']} | {r['n0']} | {r['scope']} | {r['arm']} | {r['rmse_raw']:.4g} | {r['cov95']} / {r['n']} | {r['nlpd']:.3f} | "
                 f"{r['inferred_noise_sd_raw']:.4g}{' (delta method)' if r['noise_raw_is_delta_method'] else ''} | {r['median_95_halfwidth_raw']:.4g} | "
                 f"{_fmt3(r['latent_share_median'])} | "
                 f"{'' if not isinstance(r['holdout_pass'], (bool, np.bool_)) else ('PASS' if r['holdout_pass'] else 'FAIL')} |")
    L += ["", "Independence disclosure (plan 4): the 48 holdout residuals share one fitted model, so the binomial region treats them as independent; this is an approximation.", "",
          "## 3. Noise cross-check (descriptive only; adds no arm — plan 5 / 10)", "",
          "| objective | arm | inferred noise sd (raw) | exact sd (floor) | exact df | measured arm included | 52 perturbed pooled sd | inferred / perturbed | per-level sd | mean abs z (perturbed deltas / inferred sd) | max abs z | 52 trigger |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for _, r in cross.iterrows():
        L.append(f"| {r['objective']} | {r['arm']} | {r['inferred_noise_sd_raw']:.4g}{' (delta)' if r['inferred_is_delta_method'] else ''} | {r['exact_sd_floor']:.4g} | "
                 f"{r['exact_df']} | {r['measured_arm_included']} | {r['perturbed_pooled_sd']:.4g} | {r['ratio_inferred_over_perturbed']:.3g} | "
                 f"{', '.join(f'{v:.3g}' for v in r['per_level_sd'])} | {r['z_mean_abs']:.3g} | {r['z_max_abs']:.3g} | "
                 f"{'FIRES — ' + r['trigger_verdict'] if r['trigger_fires'] else 'no'} |")
    L += ["", "Reading: the exact replicate sd is 0 on this deterministic instrument (ERCOT_NOISE.md), so the GP noise is inferred-only; "
          "the perturbed-copy sd is a LOCAL INPUT SENSITIVITY (0.1 % MW moves), not noise — the ratio is descriptive. A firing 52 trigger is "
          "reported; any model change needs a plan amendment.", "",
          f"## 4. Sufficiency (LOO only; nested Sobol prefixes {list(PREFIXES)}; config committed at 48) and E-D7", "",
          "| objective | n | arm | LOO RMSE | LOO cov95 | LOO NLPD |", "|---|---|---|---|---|---|"]
    for _, r in suff.iterrows():
        L.append(f"| {r['objective']} | {r['n']} | {r['arm']} | {r['loo_rmse']:.4g} | {r['loo_cov95']} | {r['loo_nlpd']:.3f} |")
    L += ["", f"**Criterion (pinned in Part A, verbatim):** {SUFFICIENCY_CRITERION}", "",
          "| objective | LOO cov95 at 32 (bar [28, 32]) | LOO RMSE 32 / 48 (<= 1.1) | committed config at 32 passes holdout |", "|---|---|---|---|"]
    for obj, r in res["per_obj"].items():
        L.append(f"| {obj} | {r['loo_cov95_32']} | {r['loo_rmse_32'] / r['loo_rmse_48']:.3f} | {r['holdout_pass_32']} |")
    L += ["", f"**E-D7 recommendation: n0 = {res['recommendation']}.** " + ("Every objective meets the criterion at 32." if not res["reasons"]
          else "Reasons for 48: " + "; ".join(res["reasons"]) + "."), "",
          "Drafted pi-agenda row (Kay decides; 55 Part B waits on `E-D7_decided`):", "", "```", pi_row, "```", "",
          "## 5. Committed configs (contract 6.2)", "", "| objective | arm | cfg | floor | exact sd / df | holdout cov95 (at the recommended tier) | holdout RMSE | exposure rows |", "|---|---|---|---|---|---|---|---|"]
    for obj, c in com.items():
        L.append(f"| {obj} | {c['arm']} | {'/'.join(c['cfg'])} | {c['floor']} | {c['exact_sd']} / {c['exact_df']} | {c['holdout_cov95'][0]} / {c['holdout_cov95'][1]} | "
                 f"{c['holdout_rmse']:.4g} | {c['exposure_rows']} |")
    L += ["", f"Exposure ledger: `exposure_ledger.csv` ({len(read_ledger(res['out_dir']))} of {EXPOSURE_CAP} scorings used; retired by committed_configs.json).", ""]
    L += ["## 6. Figures", ""] + [f"- `{os.path.basename(f)}`" for f in figs] + [""]
    if mech_md:
        L += [mech_md, ""]
    L += ["## 7. Deviations and limits", "",
          "- Holdout touched only at the two plan tiers (32, 48), once per committed config; sufficiency curves are LOO-only (prompt 54 v3.1).",
          "- The mechanism page is read-only (flags); R4 / N1 flags need the [43, 48] pass AND readable chatter (contract addendum 2026-11-17 bar).",
          "- log1p arms: the inferred noise in raw units is a delta-method value at the training median (flagged).", ""]
    return "\n".join(L)


def deliverables(res, noise, mechanism=None, extra=None, n_paths=None):
    """Write the figures, the noise cross-check CSV, the mechanism page and ERCOT_GP_STATUS.md
    into res['out_dir']. Never touches committed_configs.json."""
    from analysis.ercot_gp import ercot_gp_mechanism as M
    extra = extra or {}
    out = res["out_dir"]
    entries = res["entries"]
    inp = res["inputs"]
    figs = [fig_parity(entries, inp["Uh"], inp["Yh"], out), fig_sufficiency(res["sufficiency"], out)]
    cross = noise_crosscheck(noise, entries, n0=48)
    cross.to_csv(os.path.join(out, "ercot_gp_noise_crosscheck.csv"), index=False)
    pi_row = pi_agenda_row(res["recommendation"], res["reasons"])
    with open(os.path.join(out, "pi_agenda_E-D7_draft.md"), "w") as f:
        f.write(pi_row + "\n")
    mech_md = None
    if mechanism is not None:
        facts = M.network_facts() if not extra.get("synthetic") else {"text": "(synthetic smoke: no network facts)"}
        gen_pmax = np.asarray(mechanism["gen_pmax"], float)
        sites = list(mechanism["sites"])
        v1 = next(iter(entries))                                   # the null uses the FIRST objective's committed arm
        arm_v1 = entries[v1][0][48]["arm"]
        null = M.null_distributions(arm_v1, inp["U"] * gen_pmax[None, :], inp["U"], sites, gen_pmax, objective=v1,
                                    n_paths=n_paths or M.N_PATHS, curves=mechanism["curves"], base=mechanism["base"],
                                    meas_sd=entries[v1][1])
        shares = {obj: M.posterior_shares(res_[48]["gp"], gen_pmax, n_paths=n_paths or M.N_PATHS)
                  for obj, (res_, *_r) in entries.items()}
        holdout_pass = {obj: bool(res_[res["recommendation"]]["holdout"]["pass"]) for obj, (res_, *_r) in entries.items()}
        bars = M.readability_bar(noise, list(entries)) if noise else {}
        y_ranges = {obj: float(inp["Y"][obj].max() - inp["Y"][obj].min()) for obj in entries}
        flags = M.mechanism_flags(shares, null, holdout_pass=holdout_pass, bars=bars, y_ranges=y_ranges)
        with open(os.path.join(out, "ercot_gp_mechanism.json"), "w") as f:
            json.dump({"null": {k: v for k, v in null.items() if k != "curves"}, "flags": flags,
                       "bars": bars, "y_ranges": y_ranges, "holdout_pass": holdout_pass}, f, indent=1, default=float)
        figs.append(M.fig_null_truths(null, sites, gen_pmax, os.path.join(out, "fig_null_truths.png")))
        mech_md = M.mechanism_md(facts, null, flags)
    md = status_md(res, noise, cross, figs, mech_md, pi_row, extra)
    with open(os.path.join(out, "ERCOT_GP_STATUS.md"), "w") as f:
        f.write(md + "\n")
    return {"figs": figs, "cross": cross, "pi_row": pi_row, "md": md}


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
    extra = {"sites": [s_["site"] for s_ in ds["sites"]],
             "gen_pmax": np.asarray([float(s_["gen_pmax"]) for s_ in ds["sites"]], float),
             "n_refused_n0": meta.attrs["n_refused"], "n_refused_random": meta_h.attrs["n_refused"],
             "refused_n0": meta.attrs["refused"], "refused_random": meta_h.attrs["refused"],
             "r2_max": float(max(meta_g["R2"].max(), meta_h["R2"].max())),
             "r1_max": float(max(meta_g["R1"].max(), meta_h["R1"].max()))}
    return (U[keep], Y[keep], sob[keep], Uh, Yh, noise, ds["contract_version"], extra)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--synthetic", action="store_true")
    g.add_argument("--real", action="store_true")
    ap.add_argument("--out-dir", default=OUT)
    ap.add_argument("--design-space", default=os.path.join(ERCOT, "waves", "design_space_E.json"))
    ap.add_argument("--noise", default=os.path.join(ERCOT, "analysis", "noise_v3", "ercot_noise.json"))
    ap.add_argument("--mechanism", action="store_true", help="synthetic: also run the mechanism page on synthetic curves")
    a = ap.parse_args(argv)
    if a.synthetic:
        if os.path.abspath(a.out_dir) == os.path.abspath(OUT):
            raise SystemExit("--synthetic writes a ledger: pass a scratch --out-dir")
        U, Y, sob, Uh, Yh = synthetic_inputs()
        res = run(U, Y, sob, Uh, Yh, None, a.out_dir, "synthetic")
        from analysis.ercot_gp import ercot_gp_mechanism as M
        mech = {"curves": M.wave_d_site_curves_synthetic(), "base": 1.0, "sites": [f"s{i}" for i in range(6)],
                "gen_pmax": np.array([338.6, 250.6, 268.0, 185.4, 579.0, 746.4])} if a.mechanism else None
        deliverables(res, None, mechanism=mech, extra={"synthetic": True})
    else:
        U, Y, sob, Uh, Yh, noise, ver, extra = real_inputs(a.design_space, a.noise)
        res = run(U, Y, sob, Uh, Yh, noise, a.out_dir, ver)
        from analysis.ercot_gp import ercot_gp_mechanism as M
        curves, base = M.wave_d_site_curves("V1")
        mech = {"curves": curves, "base": base, "sites": extra["sites"], "gen_pmax": extra["gen_pmax"]}
        deliverables(res, noise, mechanism=mech, extra=extra)
    print(res["status"].to_string(index=False))
    print(f"E-D7 recommendation: n0 = {res['recommendation']}; reasons for 48: {res['reasons']}")
    print(f"wrote {res['committed']} (holdout RETIRED); ERCOT_GP_STATUS.md + figures in {res['out_dir']}")


if __name__ == "__main__":
    main()
