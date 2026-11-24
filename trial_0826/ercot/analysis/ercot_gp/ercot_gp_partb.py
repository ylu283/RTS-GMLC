#!/usr/bin/env python3
"""Prompt 54 Part B under the v3.3 addendum (2026-11-24): training-size study,
navigation tier n*, holdout at 32 / 48 (+ n*), committed configs, noise
cross-check vs sigma_c, mechanism page with the prompt-61 residual row.

    # real (bogp-botorch; reads n0_E via the loader, random_E only in the holdout grader):
    python analysis/ercot_gp/ercot_gp_partb.py --real \
        --design-space waves/design_space_E_2026-11-24.json
    # after committed_configs.json exists: rebuild the pages from deterministic replays
    python analysis/ercot_gp/ercot_gp_partb.py --real --design-space ... --replay-only

Pinned here BEFORE any n0_E Y is read by this module (prompt 54 v3.3 §5):

- Objectives: the design-space `objectives` keys (SEATED) then the co-reported ids
  (default N4, N1): fitted and graded identically, labelled co-reported, never seated.
- Arm set per objective = plan §5 via `ercot_gp_status.arm_set`, with the
  measured-floor arm now LIVE: floor = sigma_c from analysis/noise_v3/
  ercot_noise_seed.json (prompt 63, df 16), included iff sigma_c > 0 AND df >= 3.
  log1p arms iff the plan-§5 rule holds on the grading tier (48 rows).
- Training-size study: nested Sobol prefixes N_GRID (sobol_index < n). At each n:
  every arm fitted (house fit: FlexGP / bogp.train_gp, Adam 700 epochs, lr 0.01 —
  the MLE as the house computes it), closed-form LOO NLPD / RMSE / cov95, bar
  binom.interval(0.90, n, 0.95), selection by `ercot_gp_status.select` (> 2 paired
  se, tie order), hyperparameters of every arm (ARD lengthscales in u units,
  outputscale, inferred noise sd vs sigma_c).
- n* (E-D7 recommendation; Kay decides): the smallest n < 48 in N_GRID at which, for
  EVERY SEATED objective, with the arm SELECTED at that n:
    (1) LOO cov95 in binom.interval(0.90, n, 0.95);
    (2) LOO RMSE_n / LOO RMSE_48 <= 1.1 (RMSE_48 of the arm selected at 48);
    (3) max over the 6 sites of |l_n - l_prev| / l_prev < 0.10, l = ARD lengthscale in
        u units of the arm selected at n, l_prev = of the arm selected at the
        previous grid n (the smallest grid n has no predecessor -> not stable);
  else n* = 48. The same rule is evaluated for the co-reported ids and stated, never
  binding. Descriptive alternatives (what would change the choice) are reported.
- Holdout: random_E (48, i.i.d.), bar [43, 48] = binom.interval(0.90, 48, 0.95);
  ONCE per objective at n in {32, 48} and at n* if n* not in {32, 48}, scoring the
  arm selected at that n fitted on that prefix; n* is fixed BEFORE random_E is
  loaded. Ledger append-only; the 25th scoring refused; a crash-rerun REPLAYS a
  recorded scoring deterministically (asserted equal to the ledger row, never
  appended) — plan §4 admits deterministic replays.
- committed_configs.json written LAST (retires the holdout): per objective the arm
  selected at n* (n0_tier_recommended = n*), with every tier's arm / holdout result.
- If an objective fails its holdout bar it is recorded; no re-selection, no extra
  scoring.
"""
import argparse
import datetime as _dt
import json
import os
import sys
import time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ERCOT = os.path.abspath(os.path.join(HERE, "..", ".."))
if ERCOT not in sys.path:
    sys.path.insert(0, ERCOT)
from analysis.ercot_gp import ercot_gp_status as S  # noqa: E402

import torch  # noqa: E402

N_GRID = (12, 16, 20, 24, 28, 32, 36, 40, 44, 48)
PLAN_TIERS = (32, 48)
LOO_LEVEL = 0.90
RMSE_RATIO_MAX = 1.1
LS_STAB_MAX = 0.10
MEAS_DF_MIN = S.MEAS_DF_MIN
SEED_JSON = os.path.join(ERCOT, "analysis", "noise_v3", "ercot_noise_seed.json")
NOISE_JSON = os.path.join(ERCOT, "analysis", "noise_v3", "ercot_noise.json")
LC_CSV = os.path.join(ERCOT, "analysis", "location_contrast", "location_contrast_E.csv")
LC_DM = os.path.join(ERCOT, "waves", "location_contrast_E", "design_matrix.csv")
CO_REPORTED_DEFAULT = ("N4", "N1")
FLOOR_RULE = ("measured iff sigma_c > 0 AND df >= 3 (sigma_c = prompt-63 chatter sd, "
              "analysis/noise_v3/ercot_noise_seed.json, df 16); else inferred-only 1e-9")
N_STAR_RULE = (
    "n* = the smallest n in {12, 16, ..., 44} at which, for every SEATED objective and the "
    "arm selected at that n: (1) LOO cov95 lies in binom.interval(0.90, n, 0.95); (2) LOO "
    "RMSE_n / LOO RMSE_48 <= 1.1; (3) the ARD lengthscales (u units) changed by < 10 % "
    "(max over the 6 sites, relative to the previous grid n's selected arm); if no n < 48 "
    "meets all three, n* = 48.")
EXPLORATORY = [S.Arm("m32+std", ("m32", "std", "inferred", "none"), "inferred"),
               S.Arm("m52+std+gamma", ("m52", "std", "inferred", "gamma"), "inferred"),
               S.Arm("m52+std+fixed_sigma_c", ("m52", "std", "fixed", "none"), "measured")]


# --------------------------------------------------------------------------
# measured floor (prompt 63 sigma_c) and hyperparameters
# --------------------------------------------------------------------------
def seed_floor(seed, obj):
    """(sigma_c, df, use) from ercot_noise_seed.json: use iff sigma_c > 0 AND df >= 3."""
    if seed is None or obj not in seed.get("per_candidate", {}):
        return 0.0, 0, False
    c = seed["per_candidate"][obj]
    sd, df = float(c.get("sigma_c", 0.0) or 0.0), int(c.get("df", 0) or 0)
    return sd, df, bool(sd > 0 and df >= MEAS_DF_MIN)


def hyper(gp):
    cov = gp.model.covar_module
    ls_std = cov.base_kernel.lengthscale.detach().double().numpy().reshape(-1)
    ls_u = ls_std * np.asarray(gp.sx, float)
    os_std = float(cov.outputscale.detach().double())
    s_t, s_raw = S.noise_sd(gp)
    nv = float(gp.lik.noise.detach().double())
    return {"ls_u": [float(v) for v in ls_u], "outputscale_std": os_std,
            "outputscale_sd_t": float(np.sqrt(os_std) * gp.sy), "noise_var_std": nv,
            "noise_sd_t": s_t, "noise_sd_raw": s_raw,
            "noise_at_floor": bool(nv <= 1.02 * gp.floor_var) if gp.floor_var > 0 else False,
            "mean_const_std": float(gp.model.mean_module.constant.detach().double())}


# --------------------------------------------------------------------------
# training-size study (LOO only)
# --------------------------------------------------------------------------
def _arm_row(obj, role, n, a, gp, lo_, sel_r, sigma_c, sites):
    h = hyper(gp)
    m = lo_["metrics"]
    lo, hi = S.binom_band(n, level=LOO_LEVEL)
    half = float(np.median(S.halfwidth_raw(lo_["mu_t"], lo_["sd_t"], a.transform)))
    r = {"objective": obj, "role": role, "n": n, "arm": a.name, "cfg": "/".join(a.cfg),
         "floor_mode": a.floor_mode, "floor": a.floor(sigma_c) if a.floor_mode == "measured" else S.INFERRED_FLOOR,
         "loo_nlpd": m["nlpd"], "loo_rmse": m["rmse"], "loo_rmse_pct_range": m["rmse_pct_range"],
         "loo_cov95": m["cov95"], "bar_lo": lo, "bar_hi": hi, "cov_in_bar": bool(lo <= m["cov95"] <= hi),
         "loo_rms_z": m["rms_z"], "loo_spearman": m["spearman"], "loo_r2": m["r2"],
         "median_95_halfwidth_raw": half,
         "outputscale_sd_t": h["outputscale_sd_t"], "noise_sd_raw": h["noise_sd_raw"],
         "noise_at_floor": h["noise_at_floor"], "sigma_c": sigma_c,
         "noise_over_sigma_c": h["noise_sd_raw"] / sigma_c if sigma_c > 0 else np.nan}
    for s, v in zip(sites, h["ls_u"]):
        r[f"ls_u_{s}"] = v
    if sel_r is not None:
        r.update({"diff_vs_default": sel_r["diff_vs_default"], "paired_se": sel_r["paired_se"],
                  "beats_default": sel_r["beats_default"], "selected": sel_r["selected"]})
    return r


def study(U, y, sob, arms, sigma_c, obj, role, sites, grid=N_GRID, explore=True):
    """Returns (plan-arm rows, exploratory rows, winners {n: {arm, gp, loo}})."""
    U, y = np.asarray(U, float), np.asarray(y, float)
    rows, xrows, winners = [], [], {}
    for n in grid:
        m = S.prefix_mask(sob, n)
        winner, sel_rows, fits, loos = S.select(U[m], y[m], arms, sigma_c)
        for sr in sel_rows:
            a = next(a for a in arms if a.name == sr["arm"])
            rows.append(_arm_row(obj, role, n, a, fits[a.name], loos[a.name], sr, sigma_c, sites))
        winners[n] = {"arm": winner, "gp": fits[winner.name], "loo": loos[winner.name]}
        if explore:
            base_pts = loos[winner.name]["nlpd_pts"]
            for a in EXPLORATORY:
                if a.floor_mode == "measured" and not sigma_c > 0:
                    continue
                gp = S.fit(U[m], y[m], a, sigma_c)
                lo_ = S.loo(gp, y[m], a, sigma_c)
                r = _arm_row(obj, role, n, a, gp, lo_, None, sigma_c, sites)
                dm, se = S.paired(lo_["nlpd_pts"], base_pts)
                r.update({"vs_selected_arm": winner.name, "diff_vs_selected": dm, "paired_se": se})
                xrows.append(r)
    return rows, xrows, winners


LONG_EPOCHS = 10000


class long_fit:
    """Context manager: the house fit with more Adam epochs (EXPLORATORY ONLY; plan §5 freezes
    the campaign fit definition = bogp.train_gp defaults, 700 epochs)."""

    def __init__(self, epochs=LONG_EPOCHS):
        self.epochs = epochs

    def __enter__(self):
        import functools
        self._orig = S.common.train_gp
        S.common.train_gp = functools.partial(self._orig, n_epochs=self.epochs)
        return self

    def __exit__(self, *exc):
        S.common.train_gp = self._orig
        return False


def study_long(U, y, sob, arms, sigma_c, obj, role, sites, grid=N_GRID, epochs=LONG_EPOCHS):
    """EXPLORATORY: the plan-§5 arms and selection rule re-run with `epochs` Adam epochs.
    Reported, never committed, never holdout-scored."""
    with long_fit(epochs):
        rows, _, winners = study(U, y, sob, arms, sigma_c, obj, role, sites, grid, explore=False)
    for r in rows:
        r["fit"] = f"adam{epochs}"
    return rows, winners


# --------------------------------------------------------------------------
# n*
# --------------------------------------------------------------------------
def n_star_checks(df, sites, grid=N_GRID):
    """Per (objective, n): the three n* conditions on the SELECTED arm."""
    sel = df[df["selected"]].copy()
    lsc = [f"ls_u_{s}" for s in sites]
    out = []
    for obj in sel["objective"].unique():
        d = sel[sel["objective"] == obj].set_index("n")
        r48 = float(d.loc[max(grid), "loo_rmse"])
        prev = None
        for n in grid:
            r = d.loc[n]
            ls = r[lsc].to_numpy(float)
            if prev is None:
                ch, ch_med = np.nan, np.nan
            else:
                rel = np.abs(ls - prev) / prev
                ch, ch_med = float(rel.max()), float(np.median(rel))
            ratio = float(r["loo_rmse"]) / r48
            c1 = bool(r["cov_in_bar"])
            c2 = bool(ratio <= RMSE_RATIO_MAX)
            c3 = bool(np.isfinite(ch) and ch < LS_STAB_MAX)
            out.append({"objective": obj, "role": r["role"], "n": n, "arm": r["arm"],
                        "loo_cov95": int(r["loo_cov95"]), "bar_lo": int(r["bar_lo"]), "bar_hi": int(r["bar_hi"]),
                        "c1_cov_in_bar": c1, "rmse_ratio_vs_48": ratio, "c2_rmse_ok": c2,
                        "ls_rel_change_max": ch, "ls_rel_change_median": ch_med, "c3_ls_stable": c3,
                        "all_ok": c1 and c2 and c3})
            prev = ls
    return pd.DataFrame(out)


def pick_n(checks, objs, grid=N_GRID, cond=("c1_cov_in_bar", "c2_rmse_ok", "c3_ls_stable"), ls_col=None):
    for n in grid:
        if n >= max(grid):
            break
        d = checks[(checks["n"] == n) & checks["objective"].isin(objs)]
        assert len(d) == len(objs), (n, objs)
        ok = d[list(cond)].all(axis=1)
        if ls_col is not None:
            ok &= d[ls_col] < LS_STAB_MAX
        if ok.all():
            return n
    return max(grid)


def n_star(checks, seated, co_reported, grid=N_GRID):
    ns = pick_n(checks, seated, grid)
    lines = []
    for n in grid:
        if n >= max(grid):
            break
        d = checks[(checks["n"] == n) & checks["objective"].isin(seated)]
        fails = []
        for _, r in d.iterrows():
            f = []
            if not r["c1_cov_in_bar"]:
                f.append(f"cov95 {r['loo_cov95']} outside [{r['bar_lo']}, {r['bar_hi']}]")
            if not r["c2_rmse_ok"]:
                f.append(f"RMSE ratio {r['rmse_ratio_vs_48']:.3f} > {RMSE_RATIO_MAX}")
            if not r["c3_ls_stable"]:
                f.append("no previous n" if not np.isfinite(r["ls_rel_change_max"])
                         else f"lengthscale change {100 * r['ls_rel_change_max']:.0f} % >= 10 %")
            if f:
                fails.append(f"{r['objective']} ({r['arm']}): " + ", ".join(f))
        lines.append(f"n = {n}: " + ("ALL MET" if not fails else "; ".join(fails)))
        if n == ns:
            break
    reason = (f"n* = {ns}. " + N_STAR_RULE + " Per n (seated " + ", ".join(seated) + "): "
              + " | ".join(lines) + ("" if ns < max(grid) else f" -> no n < {max(grid)} meets all three; n* = {max(grid)}."))
    alt = {
        "co_reported_included": pick_n(checks, list(seated) + list(co_reported), grid),
        "co_reported_alone": {o: pick_n(checks, [o], grid) for o in co_reported},
        "seated_each": {o: pick_n(checks, [o], grid) for o in seated},
        "without_lengthscale_condition": pick_n(checks, seated, grid, cond=("c1_cov_in_bar", "c2_rmse_ok")),
        "lengthscale_median_not_max": pick_n(checks, seated, grid, cond=("c1_cov_in_bar", "c2_rmse_ok"),
                                              ls_col="ls_rel_change_median"),
        "cov_only": pick_n(checks, seated, grid, cond=("c1_cov_in_bar",)),
    }
    return ns, reason, alt


# --------------------------------------------------------------------------
# holdout (score once, or replay a recorded scoring)
# --------------------------------------------------------------------------
def _holdout_eval(gp, arm, Uh, yh, sigma_c):
    mu, sd = gp.predict_t(Uh)
    with np.errstate(divide="ignore", invalid="ignore"):
        m, z = S.common.metrics(yh, mu, sd, arm.transform, S._report_floor(arm, sigma_c),
                                y_range=float(yh.max() - yh.min()))
    lat = S.latent_sd_t(gp, Uh)
    return {"metrics": m, "z": z, "mu_t": mu, "sd_t": sd,
            "pass": bool(S.HOLDOUT_BAR[0] <= m["cov95"] <= S.HOLDOUT_BAR[1]),
            "half_med_raw": float(np.median(S.halfwidth_raw(mu, sd, arm.transform))),
            "latent_share": float(np.median(lat / sd))}


def holdout(winners, tiers, Uh, Yh, out_dir, sigmas, allow_new=True):
    """winners[obj][n] = {arm, gp}. Scores each (obj, n) once; replays recorded ones."""
    Uh = np.asarray(Uh, float)
    led = S.read_ledger(out_dir)
    res = {}
    for obj in winners:
        yh = Yh[obj].to_numpy(float)
        res[obj] = {}
        for n in tiers:
            w = winners[obj][n]
            rec = led[(led["objective"].astype(str) == obj) & (led["n0"].astype(int) == int(n))]
            if len(rec):
                assert len(rec) == 1
                row = rec.iloc[0].to_dict()
                h = _holdout_eval(w["gp"], w["arm"], Uh, yh, sigmas[obj])
                assert row["arm"] == w["arm"].name, (obj, n, row["arm"], w["arm"].name)
                assert int(row["cov95"]) == h["metrics"]["cov95"], (
                    f"replay {obj}@{n}: cov95 {h['metrics']['cov95']} != ledger {row['cov95']} (not deterministic)")
                assert abs(float(row["rmse_raw"]) - h["metrics"]["rmse"]) <= 1e-6 * max(1.0, abs(h["metrics"]["rmse"])), (
                    f"replay {obj}@{n}: rmse differs from the ledger")
                h["ledger_row"], h["replay"] = row, True
            else:
                if not allow_new:
                    raise S.HoldoutRetired(f"{obj}@{n}: not recorded and new scorings are not allowed (replay only)")
                h = S.score_holdout(w["gp"], w["arm"], obj, n, Uh, yh, out_dir, sigmas[obj], tiers=tuple(tiers))
                h["replay"] = False
                led = S.read_ledger(out_dir)
            res[obj][n] = h
    return res


# --------------------------------------------------------------------------
# committed configs (LAST; retires the holdout)
# --------------------------------------------------------------------------
def committed_doc(winners, hres, ns, reason, alt, roles, sigmas, dfs, uses, ds_version, tiers, sites):
    objs = {}
    for obj in winners:
        w = winners[obj][ns]
        a = w["arm"]
        h = hyper(w["gp"])
        h_ns = hres[obj][ns]
        objs[obj] = {
            "cfg": list(a.cfg), "arm": a.name, "seated": roles[obj] == "seated", "role": roles[obj],
            "floor": float(sigmas[obj]) if a.floor_mode == "measured" else 0.0,
            "floor_rule": FLOOR_RULE, "measured_floor_used": a.floor_mode == "measured",
            "measured_arm_included": bool(uses[obj]), "sigma_c": float(sigmas[obj]), "sigma_c_df": int(dfs[obj]),
            "loo_nlpd_mean": float(w["loo"]["metrics"]["nlpd"]), "loo_rmse": float(w["loo"]["metrics"]["rmse"]),
            "loo_cov95": [int(w["loo"]["metrics"]["cov95"]), int(ns)],
            "holdout_cov95": [int(h_ns["metrics"]["cov95"]), S.N_HOLDOUT],
            "holdout_rmse": float(h_ns["metrics"]["rmse"]),
            "holdout_pass": bool(h_ns["pass"]),
            "holdout_cov95_by_tier": {str(n): [int(hres[obj][n]["metrics"]["cov95"]), S.N_HOLDOUT] for n in tiers},
            "holdout_pass_by_tier": {str(n): bool(hres[obj][n]["pass"]) for n in tiers},
            "exposure_rows": [int(hres[obj][n]["ledger_row"]["n_scoring"]) for n in tiers],
            "n_star": int(ns),
            "hyperparameters": {"lengthscales_u": dict(zip(sites, h["ls_u"])),
                                "outputscale_sd_t": h["outputscale_sd_t"], "noise_sd_raw": h["noise_sd_raw"],
                                "noise_at_floor": h["noise_at_floor"]},
            "by_tier": {str(n): {"arm": winners[obj][n]["arm"].name, "cfg": list(winners[obj][n]["arm"].cfg),
                                 "holdout_cov95": int(hres[obj][n]["metrics"]["cov95"]),
                                 "holdout_pass": bool(hres[obj][n]["pass"]),
                                 "holdout_rmse": float(hres[obj][n]["metrics"]["rmse"]),
                                 "hyperparameters": (lambda hh: {"lengthscales_u": dict(zip(sites, hh["ls_u"])),
                                                                 "outputscale_sd_t": hh["outputscale_sd_t"],
                                                                 "noise_sd_raw": hh["noise_sd_raw"]})(hyper(winners[obj][n]["gp"]))}
                        for n in tiers}}
    return {"identity": "v3", "design_space_version": ds_version, "n0_tier_recommended": int(ns),
            "n_star": int(ns), "n_star_reason": reason, "n_star_rule": N_STAR_RULE,
            "n_star_alternatives_descriptive": alt, "E-D7_decided": None,
            "holdout_tiers": [int(n) for n in tiers], "holdout_bar": list(S.HOLDOUT_BAR),
            "committed_cfg_is": "the arm selected (plan §5 rule) at n* on the nested Sobol prefix",
            "objectives_seated": [o for o in winners if roles[o] == "seated"],
            "co_reported": [o for o in winners if roles[o] != "seated"],
            "generated_utc": _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds"),
            "objectives": objs}


def write_committed(out_dir, doc):
    p = os.path.join(out_dir, S.COMMITTED)
    if os.path.isfile(p):
        raise S.HoldoutRetired(f"{p} exists; committed configs are written once")
    with open(p, "w") as f:
        json.dump(doc, f, indent=1)
    return p


# --------------------------------------------------------------------------
# noise cross-check vs sigma_c (descriptive)
# --------------------------------------------------------------------------
def noise_crosscheck(winners, seed, tiers, roles):
    rows = []
    for obj in winners:
        c = (seed or {}).get("per_candidate", {}).get(obj, {})
        sig = float(c.get("sigma_c", np.nan))
        ci = c.get("sigma_c_ci95", [np.nan, np.nan])
        per = [float(v) for v in c.get("sd_by_design", [])]
        ds_ = np.asarray(c.get("delta_seed", []), float)
        for n in tiers:
            w = winners[obj][n]
            h = hyper(w["gp"])
            s = h["noise_sd_raw"]
            z = ds_ / s if s > 0 and len(ds_) else np.array([])
            rows.append({"objective": obj, "role": roles[obj], "n": n, "arm": w["arm"].name,
                         "inferred_noise_sd_raw": s, "noise_at_floor": h["noise_at_floor"],
                         "sigma_c": sig, "sigma_c_ci95_lo": float(ci[0]), "sigma_c_ci95_hi": float(ci[1]),
                         "ratio_inferred_over_sigma_c": s / sig if sig > 0 else np.nan,
                         "inside_sigma_c_ci95": bool(ci[0] <= s <= ci[1]),
                         "per_level_sd": per,
                         "ratio_inferred_over_level_sd": [s / v if v > 0 else np.nan for v in per],
                         "n_seed_deltas": int(len(ds_)),
                         "seed_delta_z_mean_abs": float(np.mean(np.abs(z))) if len(z) else np.nan,
                         "seed_delta_z_max_abs": float(np.max(np.abs(z))) if len(z) else np.nan,
                         "seed_delta_frac_abs_z_gt_1p96": float(np.mean(np.abs(z) > 1.96)) if len(z) else np.nan,
                         "trigger_fires": bool(c.get("trigger", {}).get("fires", False)),
                         "trigger_verdict": c.get("trigger", {}).get("verdict", "")})
    return pd.DataFrame(rows)


# --------------------------------------------------------------------------
# figures (bold labels AND ticks; assert-before-draw)
# --------------------------------------------------------------------------
def _plt():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.size": 13, "font.weight": "bold", "axes.labelweight": "bold",
                         "axes.titleweight": "bold"})
    return plt


def _bold(ax):
    from matplotlib.ticker import FuncFormatter, LogLocator, NullFormatter
    if ax.get_yscale() == "log":
        ax.yaxis.set_major_locator(LogLocator(base=10, subs=(1.0, 2.0, 5.0)))
        ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:g}"))
        ax.yaxis.set_minor_formatter(NullFormatter())
    ax.figure.canvas.draw()
    for t in ax.get_xticklabels() + ax.get_yticklabels():
        t.set_fontweight("bold")
    ax.grid(alpha=0.3)


def fig_curves(df, objs, roles, ns, out_path, grid=N_GRID):
    plt = _plt()
    rows = ["loo_rmse_ratio", "loo_nlpd", "cov_frac", "noise_over_sigma_c"]
    ylab = {"loo_rmse_ratio": "LOO RMSE / RMSE48 (selected)", "loo_nlpd": "LOO NLPD (mean, nats)",
            "cov_frac": "LOO cov95 / n", "noise_over_sigma_c": "inferred noise sd / sigma_c"}
    fig, axes = plt.subplots(len(rows), len(objs), figsize=(5.4 * len(objs), 4.2 * len(rows)), squeeze=False)
    for j, obj in enumerate(objs):
        d = df[df["objective"] == obj]
        sel = d[d["selected"]].sort_values("n")
        r48 = float(sel.loc[sel["n"] == max(grid), "loo_rmse"].iloc[0])
        for arm in d["arm"].unique():
            a = d[d["arm"] == arm].sort_values("n")
            vals = {"loo_rmse_ratio": a["loo_rmse"].to_numpy(float) / r48, "loo_nlpd": a["loo_nlpd"].to_numpy(float),
                    "cov_frac": a["loo_cov95"].to_numpy(float) / a["n"].to_numpy(float),
                    "noise_over_sigma_c": a["noise_over_sigma_c"].to_numpy(float)}
            for i, k in enumerate(rows):
                v = vals[k]
                assert np.isfinite(v).all() or k == "noise_over_sigma_c", (obj, arm, k)
                axes[i, j].plot(a["n"], v, "o-", lw=1.2, ms=3, alpha=0.75, label=arm)
        sv = {"loo_rmse_ratio": sel["loo_rmse"].to_numpy(float) / r48, "loo_nlpd": sel["loo_nlpd"].to_numpy(float),
              "cov_frac": sel["loo_cov95"].to_numpy(float) / sel["n"].to_numpy(float),
              "noise_over_sigma_c": sel["noise_over_sigma_c"].to_numpy(float)}
        for i, k in enumerate(rows):
            ax = axes[i, j]
            assert np.isfinite(sv[k]).all() or k == "noise_over_sigma_c"
            ax.plot(sel["n"], sv[k], "s-", color="k", lw=2.6, ms=6, label="selected", zorder=5)
            ax.axvline(ns, color="C3", ls="--", lw=1.5)
            if k == "loo_rmse_ratio":
                ax.axhline(RMSE_RATIO_MAX, color="0.3", ls=":", lw=1.5)
            if k == "cov_frac":
                for n in grid:
                    lo, hi = S.binom_band(n, level=LOO_LEVEL)
                    ax.plot([n, n], [lo / n, hi / n], color="0.5", lw=7, alpha=0.35)
                ax.axhline(0.95, color="0.3", ls=":", lw=1)
            if k == "noise_over_sigma_c":
                ax.axhline(1.0, color="0.3", ls=":", lw=1.5)
                if np.isfinite(sv[k]).any():
                    ax.set_yscale("log")
                else:
                    ax.text(0.5, 0.5, "no sigma_c for this id", transform=ax.transAxes, ha="center", fontweight="bold")
            ax.set_xlabel("n (nested Sobol prefix)")
            ax.set_ylabel(ylab[k])
            if i == 0:
                ax.set_title(f"{obj} ({'seated' if roles[obj] == 'seated' else 'co-reported'})")
            _bold(ax)
            if i == 0 and j == 0:
                ax.legend(fontsize=9)
    fig.suptitle(f"Training-size study (LOO only)\nred dashed = n* = {ns}; grey bars = binom 90 % region per n",
                 fontweight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.97))
    fig.savefig(out_path, dpi=110)
    plt.close(fig)
    return out_path


def fig_lengthscales(df, objs, roles, sites, ns, out_path, grid=N_GRID):
    plt = _plt()
    fig, axes = plt.subplots(1, len(objs), figsize=(5.4 * len(objs), 4.8), squeeze=False)
    for j, obj in enumerate(objs):
        sel = df[(df["objective"] == obj) & df["selected"]].sort_values("n")
        ax = axes[0, j]
        for s in sites:
            v = sel[f"ls_u_{s}"].to_numpy(float)
            assert np.isfinite(v).all() and (v > 0).all(), (obj, s)
            ax.plot(sel["n"], v, "o-", lw=2, label=f"site {s}")
        ax.set_yscale("log")
        ax.axvline(ns, color="C3", ls="--", lw=1.5)
        ax.set_xlabel("n (nested Sobol prefix)")
        ax.set_ylabel("ARD lengthscale (u units)")
        ax.set_title(f"{obj} ({'seated' if roles[obj] == 'seated' else 'co-reported'}), selected arm")
        _bold(ax)
        if j == 0:
            ax.legend(fontsize=9)
    fig.tight_layout()
    fig.savefig(out_path, dpi=110)
    plt.close(fig)
    return out_path


def fig_house_vs_long(df, ldf, objs, roles, sites, ns, out_path, grid=N_GRID, epochs=LONG_EPOCHS):
    """EXPLORATORY: selected arm under the house fit (700 epochs) vs the long fit."""
    plt = _plt()
    fig, axes = plt.subplots(3, len(objs), figsize=(5.4 * len(objs), 12.6), squeeze=False)
    for j, obj in enumerate(objs):
        for lab, d, sty in (("house fit (700 ep)", df, "s-"), (f"long fit ({epochs} ep)", ldf, "o--")):
            sel = d[(d["objective"] == obj) & d["selected"]].sort_values("n")
            nlpd = sel["loo_nlpd"].to_numpy(float)
            rm = sel["loo_rmse"].to_numpy(float)
            ns_ = sel["noise_over_sigma_c"].to_numpy(float)
            assert np.isfinite(nlpd).all() and np.isfinite(rm).all() and (rm > 0).all(), (obj, lab)
            axes[0, j].plot(sel["n"], nlpd, sty, lw=2, label=lab)
            axes[1, j].plot(sel["n"], rm, sty, lw=2, label=lab)
            if np.isfinite(ns_).all() and (ns_ > 0).all():
                axes[2, j].plot(sel["n"], ns_, sty, lw=2, label=lab)
        axes[0, j].set_title(f"{obj} ({'seated' if roles[obj] == 'seated' else 'co-reported'}), selected arm")
        axes[0, j].set_ylabel("LOO NLPD (mean, nats)")
        axes[1, j].set_ylabel("LOO RMSE (raw units)")
        axes[2, j].set_ylabel("inferred noise sd / sigma_c")
        axes[2, j].axhline(1.0, color="0.3", ls=":", lw=1.5)
        axes[2, j].set_yscale("log")
        for i in range(3):
            axes[i, j].set_xlabel("n (nested Sobol prefix)")
            _bold(axes[i, j])
        if j == 0:
            axes[0, j].legend(fontsize=10)
    fig.suptitle("EXPLORATORY: house fit vs longer Adam fit (never committed)", fontweight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.97))
    fig.savefig(out_path, dpi=110)
    plt.close(fig)
    return out_path


def fig_parity(winners, hres, Uh, Yh, tiers, out_path):
    entries = {obj: ({n: {"gp": winners[obj][n]["gp"], "arm": winners[obj][n]["arm"], "holdout": hres[obj][n]}
                      for n in tiers},) for obj in winners}
    p = S.fig_parity(entries, np.asarray(Uh, float), Yh, os.path.dirname(out_path), tiers=tuple(tiers))
    os.replace(p, out_path)
    return out_path


# --------------------------------------------------------------------------
# mechanism page (§3 step 5; flags only) + the prompt-61 residual row
# --------------------------------------------------------------------------
def location_contrast_rows(lc_csv=LC_CSV, lc_dm=LC_DM, sites=None, objs=None):
    lc = pd.read_csv(lc_csv)
    y = lc[(lc["kind"] == "y") & lc["note"].astype(str).str.startswith("location_contrast_E:")]
    dm = pd.read_csv(lc_dm, float_precision="round_trip")
    dm["key"] = "location_contrast_E:" + dm["index"].astype(int).astype(str)
    U = dm.set_index("key")[[f"u_{s}" for s in sites]]
    Y = y.pivot(index="note", columns="objective", values="value")[objs]
    Y = Y.loc[U.index]
    labels = dm.set_index("key")["level_id"]
    assert len(U) == 9 and np.isfinite(Y.to_numpy(float)).all()
    return U, Y, labels


def lc_residuals(gps, arms, sigmas, Ulc, Ylc, labels):
    rows = []
    for obj, gp in gps.items():
        a = arms[obj]
        mu, sd = gp.predict_t(Ulc.to_numpy(float))
        y = Ylc[obj].to_numpy(float)
        t = np.log1p(y) if a.transform == "log1p" else y
        z = (t - mu) / sd
        for k, lab, zz, yy, mm, ss in zip(Ulc.index, labels.loc[Ulc.index], z, y, mu, sd):
            rows.append({"objective": obj, "key": k, "label": lab, "y": yy, "pred_mean_t": mm, "pred_sd_t": ss, "z": zz})
    return pd.DataFrame(rows)


def mechanism(winners, ns, U48, Y48, sob, sigmas, noise, hres, roles, sites, gen_pmax, out_dir, figs_dir,
              n_paths=None, log2n=None, lc=None, curves=None, base=None):
    from analysis.ercot_gp import ercot_gp_mechanism as M
    n_paths = n_paths or M.N_PATHS
    log2n = log2n or M.N_BASE_LOG2
    U48 = np.asarray(U48, float)
    m48 = S.prefix_mask(sob, 48)
    gps, arms, refit = {}, {}, {}
    for obj in winners:
        a = winners[obj][ns]["arm"]
        arms[obj] = a
        if a.name == winners[obj][48]["arm"].name:
            gps[obj], refit[obj] = winners[obj][48]["gp"], False
        else:
            gps[obj], refit[obj] = S.fit(U48[m48], Y48[obj].to_numpy(float)[m48], a, sigmas[obj]), True
    facts = M.network_facts() if curves is None else {"text": "(synthetic: no network facts)"}
    if curves is None:
        curves, base = M.wave_d_site_curves("V1")
    v1 = next(iter(winners))
    null = M.null_distributions(arms[v1], U48 * gen_pmax[None, :], U48, sites, gen_pmax, objective=v1,
                                n_paths=n_paths, log2n=log2n, curves=curves, base=base, meas_sd=sigmas[v1])
    shares = {obj: M.posterior_shares(gps[obj], gen_pmax, n_paths=n_paths, log2n=log2n) for obj in winners}
    hp = {obj: bool(hres[obj][ns]["pass"]) for obj in winners}
    bars = M.readability_bar(noise, list(winners)) if noise else {}
    yr = {obj: float(Y48[obj].max() - Y48[obj].min()) for obj in winners}
    flags = M.mechanism_flags(shares, null, holdout_pass=hp, bars=bars, y_ranges=yr)
    for obj in flags:
        flags[obj]["role"] = roles[obj]
        if roles[obj] != "seated":
            flags[obj]["suppressed"] = ((flags[obj]["suppressed"] + "; ") if flags[obj]["suppressed"] else "") + \
                "co-reported id: shares descriptive, flags not issued (v3.3 §5.4: flags for the seated ids)"
    # direction / scale facts (§3 step 5 first sentence; descriptive)
    from scipy.stats import spearmanr
    T = (U48 * gen_pmax[None, :]).sum(axis=1)
    direction = {obj: {"spearman_y_vs_T": float(spearmanr(Y48[obj].to_numpy(float), T).statistic),
                       "range": yr[obj], "B_j": bars.get(obj, {}).get("B"),
                       "range_over_B": (yr[obj] / bars[obj]["B"]) if bars.get(obj, {}).get("B") else None}
                 for obj in winners}
    lc_df = None
    if lc is not None:
        Ulc, Ylc, labels = lc
        lc_df = lc_residuals(gps, arms, sigmas, Ulc, Ylc, labels)
    figp = M.fig_null_truths(null, sites, gen_pmax, os.path.join(figs_dir, "fig_null_truths_committed.png"))
    doc = {"n_star": ns, "committed_arms": {o: a.name for o, a in arms.items()}, "refit_on_48": refit,
           "null": {k: v for k, v in null.items() if k != "curves"}, "flags": flags, "bars": bars,
           "y_ranges": yr, "holdout_pass_at_n_star": hp, "direction": direction,
           "network_facts": facts}
    with open(os.path.join(out_dir, "ercot_gp_mechanism.json"), "w") as f:
        json.dump(doc, f, indent=1, default=float)
    if lc_df is not None:
        lc_df.to_csv(os.path.join(out_dir, "ercot_gp_lc_residuals.csv"), index=False)
    return {"facts": facts, "null": null, "flags": flags, "direction": direction, "lc": lc_df,
            "fig": figp, "refit": refit, "arms": arms}


# --------------------------------------------------------------------------
# end-to-end
# --------------------------------------------------------------------------
def run(U, Y, sob, load_holdout, seed, noise, roles, sites, gen_pmax, out_dir, ds_version,
        grid=N_GRID, explore=True, replay_only=False, mech=True, mech_kw=None, lc=None, log=print,
        long_diag=False, long_epochs=LONG_EPOCHS):
    """U / Y: grading-tier rows (sobol_index aligned). `load_holdout()` -> (Uh, Yh) is
    called only AFTER n* is fixed (random_E enters only through the holdout grader)."""
    t0 = time.time()
    os.makedirs(out_dir, exist_ok=True)
    figs_dir = os.path.join(out_dir, "figs")
    os.makedirs(figs_dir, exist_ok=True)
    committed_exists = os.path.isfile(os.path.join(out_dir, S.COMMITTED))
    if committed_exists and not replay_only:
        raise S.HoldoutRetired(f"{S.COMMITTED} exists: holdout RETIRED; use --replay-only to rebuild pages")
    sob = np.asarray(sob, int)
    Uv = np.asarray(U, float)
    assert len(Uv) == len(Y) == len(sob) == 48 and sorted(sob) == list(range(48)), "grading tier = Sobol 0-47"
    objs = list(Y.columns)
    sig, dfs, uses, arms_by, rows, xrows, winners = {}, {}, {}, {}, [], [], {}
    for obj in objs:
        y = Y[obj].to_numpy(float)
        sig[obj], dfs[obj], uses[obj] = seed_floor(seed, obj)
        arms_by[obj] = S.arm_set(y, uses[obj])
        r, xr, w = study(Uv, y, sob, arms_by[obj], sig[obj], obj, roles[obj], sites, grid, explore)
        rows += r
        xrows += xr
        winners[obj] = w
        log(f"[study] {obj}: arms {[a.name for a in arms_by[obj]]}; selected "
            f"{ {n: w[n]['arm'].name for n in grid} } ({time.time() - t0:.0f} s)")
    df = pd.DataFrame(rows)
    xdf = pd.DataFrame(xrows)
    ldf, lchecks, ln = None, None, None
    if long_diag:
        lrows = []
        for obj in objs:
            lr, _ = study_long(Uv, Y[obj].to_numpy(float), sob, arms_by[obj], sig[obj], obj, roles[obj], sites, grid,
                               epochs=long_epochs)
            lrows += lr
            log(f"[long-fit diag] {obj} ({time.time() - t0:.0f} s)")
        ldf = pd.DataFrame(lrows)
        lchecks = n_star_checks(ldf, sites, grid)
    checks = n_star_checks(df, sites, grid)
    seated = [o for o in objs if roles[o] == "seated"]
    co = [o for o in objs if roles[o] != "seated"]
    ns, reason, alt = n_star(checks, seated, co, grid)
    if lchecks is not None:
        ln = n_star(lchecks, seated, co, grid)
        alt["long_fit_descriptive"] = {"epochs": long_epochs, "n_star": ln[0], "co_reported_included": ln[2]["co_reported_included"],
                                       "without_lengthscale_condition": ln[2]["without_lengthscale_condition"]}
    log(f"[n*] {reason}")
    tiers = sorted(set(PLAN_TIERS) | {ns})
    assert len(tiers) * len(objs) <= S.EXPOSURE_CAP
    # ---- holdout (random_E loaded only now) ----
    Uh, Yh = load_holdout()
    hres = holdout(winners, tiers, Uh, Yh, out_dir, sig, allow_new=not committed_exists)
    led = S.read_ledger(out_dir)
    log(f"[holdout] tiers {tiers}; ledger rows {len(led)} / {S.EXPOSURE_CAP}")
    doc = committed_doc(winners, hres, ns, reason, alt, roles, sig, dfs, uses, ds_version, tiers, sites)
    if not committed_exists:
        write_committed(out_dir, doc)                                          # LAST holdout-side write
    else:
        with open(os.path.join(out_dir, S.COMMITTED)) as f:
            old = json.load(f)
        for obj in objs:
            assert old["objectives"][obj]["arm"] == doc["objectives"][obj]["arm"], f"replay arm differs: {obj}"
            assert old["objectives"][obj]["holdout_cov95_by_tier"] == doc["objectives"][obj]["holdout_cov95_by_tier"]
        assert old["n_star"] == ns
        doc = old
    # ---- deliverables (never touch committed_configs.json) ----
    hold_rows = []
    for obj in objs:
        for n in tiers:
            h = hres[obj][n]
            m = h["metrics"]
            hold_rows.append({"objective": obj, "role": roles[obj], "n": n, "scope": "holdout",
                              "arm": winners[obj][n]["arm"].name, "cfg": "/".join(winners[obj][n]["arm"].cfg),
                              "holdout_cov95": m["cov95"], "holdout_n": m["n"], "bar_lo": S.HOLDOUT_BAR[0],
                              "bar_hi": S.HOLDOUT_BAR[1], "holdout_pass": h["pass"], "holdout_rmse": m["rmse"],
                              "holdout_rmse_pct_range": m["rmse_pct_range"], "holdout_nlpd": m["nlpd"],
                              "holdout_rms_z": m["rms_z"], "holdout_mean_z": m["mean_z"],
                              "holdout_spearman": m["spearman"], "holdout_r2": m["r2"],
                              "median_95_halfwidth_raw": h["half_med_raw"], "latent_share_median": h["latent_share"],
                              "exposure_row": int(h["ledger_row"]["n_scoring"])})
    hdf = pd.DataFrame(hold_rows)
    df_out = df.copy()
    df_out.insert(3, "scope", "loo")
    pd.concat([df_out, hdf], ignore_index=True, sort=False).to_csv(os.path.join(out_dir, "ercot_gp_status.csv"), index=False)
    xdf.to_csv(os.path.join(out_dir, "ercot_gp_exploratory.csv"), index=False)
    checks.to_csv(os.path.join(out_dir, "ercot_gp_nstar_checks.csv"), index=False)
    if ldf is not None:
        ldf.to_csv(os.path.join(out_dir, "ercot_gp_exploratory_longfit.csv"), index=False)
        lchecks.to_csv(os.path.join(out_dir, "ercot_gp_exploratory_longfit_nstar_checks.csv"), index=False)
    cross = noise_crosscheck(winners, seed, tiers, roles)
    cross.to_csv(os.path.join(out_dir, "ercot_gp_noise_crosscheck.csv"), index=False)
    figs = [fig_curves(df, objs, roles, ns, os.path.join(figs_dir, "fig_training_size_curves.png"), grid),
            fig_lengthscales(df, objs, roles, sites, ns, os.path.join(figs_dir, "fig_lengthscales_vs_n.png"), grid),
            fig_parity(winners, hres, Uh, Yh, tiers, os.path.join(figs_dir, "fig_parity_holdout.png"))]
    if ldf is not None:
        figs.append(fig_house_vs_long(df, ldf, objs, roles, sites, ns, os.path.join(figs_dir, "fig_house_vs_longfit.png"),
                                      grid, long_epochs))
    mres = None
    if mech:
        mres = mechanism(winners, ns, Uv, Y, sob, sig, noise, hres, roles, sites, np.asarray(gen_pmax, float),
                         out_dir, figs_dir, lc=lc, **(mech_kw or {}))
        figs.append(mres["fig"])
    return {"study": df, "exploratory": xdf, "long": ldf, "long_checks": lchecks, "long_n_star": ln,
            "long_epochs": long_epochs, "checks": checks, "n_star": ns, "reason": reason, "alt": alt,
            "tiers": tiers, "holdout": hres, "hold_df": hdf, "committed": doc, "cross": cross, "figs": figs,
            "mech": mres, "winners": winners, "sigmas": sig, "dfs": dfs, "uses": uses, "arms": arms_by,
            "roles": roles, "objs": objs, "ledger": S.read_ledger(out_dir), "wall_s": time.time() - t0,
            "out_dir": out_dir, "sites": sites, "grid": grid}


# --------------------------------------------------------------------------
# real inputs
# --------------------------------------------------------------------------
def real_grading(design_space, objs):
    from analysis.ercot_gp.ercot_gp_loader import load, read_design_space
    ds = read_design_space(design_space)
    _, U, Y, meta = load(["n0_E"], objs, design_space)
    g = (meta["sobol_index"].astype(str) != "") & meta["tier"].isin(["nav", "grading"])
    U, Y, meta = U[g], Y[g], meta[g]
    sob = meta["sobol_index"].astype(int).to_numpy()
    k = sob < 48
    assert k.sum() == 48 and not meta["suspect"][k].any(), "n0_E grading tier: 48 non-SUSPECT rows"
    extra = {"n_refused": meta.attrs["n_refused"], "r1_max": float(meta["R1"][k].max()),
             "r2_max": float(meta["R2"][k].max())}
    return ds, U[k], Y[k], sob[k], extra


def real_holdout_loader(design_space, objs, extra):
    def _load():
        from analysis.ercot_gp.ercot_gp_loader import load
        _, Uh, Yh, mh = load(["random_E"], objs, design_space)
        assert (mh["tier"] == "holdout").all() and len(mh) == S.N_HOLDOUT and not mh["suspect"].any()
        extra.update({"n_refused_random": mh.attrs["n_refused"], "r1_max_random": float(mh["R1"].max()),
                      "r2_max_random": float(mh["R2"].max())})
        return Uh.to_numpy(float), Yh
    return _load


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--real", action="store_true", required=True)
    ap.add_argument("--design-space", required=True)
    ap.add_argument("--co-reported", default=",".join(CO_REPORTED_DEFAULT))
    ap.add_argument("--seed-json", default=SEED_JSON)
    ap.add_argument("--noise", default=NOISE_JSON)
    ap.add_argument("--out-dir", default=HERE)
    ap.add_argument("--replay-only", action="store_true")
    ap.add_argument("--no-mechanism", action="store_true")
    ap.add_argument("--no-long-diag", action="store_true", help="skip the exploratory long-fit diagnostic")
    a = ap.parse_args(argv)
    from analysis.ercot_gp.ercot_gp_loader import read_design_space
    ds = read_design_space(a.design_space)
    seated = list(ds["objectives"])
    co = [o for o in a.co_reported.split(",") if o]
    assert set(co) <= set(ds.get("co_reported", {})), f"co-reported {co} not in the design space's co_reported"
    assert not set(co) & set(seated)
    objs = seated + co
    roles = {o: ("seated" if o in seated else "co-reported") for o in objs}
    with open(a.seed_json) as f:
        seed = json.load(f)
    with open(a.noise) as f:
        noise = json.load(f)
    ds, U, Y, sob, extra = real_grading(a.design_space, objs)
    sites = [s["site"] for s in ds["sites"]]
    gen_pmax = np.asarray([float(s["gen_pmax"]) for s in ds["sites"]], float)
    lc = location_contrast_rows(sites=sites, objs=objs)
    res = run(U, Y, sob, real_holdout_loader(a.design_space, objs, extra), seed, noise, roles, sites, gen_pmax,
              a.out_dir, ds["contract_version"], replay_only=a.replay_only, mech=not a.no_mechanism, lc=lc,
              long_diag=not a.no_long_diag)
    res["extra"] = extra
    from analysis.ercot_gp import ercot_gp_partb_report as R
    R.write_all(res, seed, ds, a)
    print(f"n* = {res['n_star']}; tiers {res['tiers']}; ledger {len(res['ledger'])}; wall {res['wall_s']:.0f} s")


if __name__ == "__main__":
    main()
