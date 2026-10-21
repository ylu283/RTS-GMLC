"""Prompt 42: shed GP under PROVISIONAL floors (diagnostic sweep).

For each floor f in F: LOO-select the shed winner over the 7 pinned configs
(n0 = 32 training set only), then fit THREE arms (default, incumbent
rbf+log1p, per-floor winner) at n0 = 16/32/48 and score them on the frozen
random_C holdout. Executor details pinned in PROGRESS.md (3731f49).

Imports common / part_h only (never runs their main()). Mutates
common.FLOORS IN PLACE for the LOO reselection and restores it. Writes only
under analysis/noise_floor/provisional/.
"""
from __future__ import annotations

import json
import math
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..", "initial_design")))

import common  # noqa: E402
import part_h  # noqa: E402
import gpytorch  # noqa: E402
import torch  # noqa: E402

COL = "load_shed_mwh"
J = common.M_COLS.index(COL)
F = [180.0, 306.0, 500.0, 880.0, 1500.0, 1800.0, 3000.0]
CONFIGS = [("m52", "std", "inferred", "none"), ("m32", "std", "inferred", "none"),
           ("rbf", "std", "inferred", "none"), ("m52", "log1p", "inferred", "none"),
           ("m52", "std", "fixed", "none"), ("m52", "std", "inferred", "gamma"),
           ("rbf", "log1p", "inferred", "none")]
DEFAULT = CONFIGS[0]
INCUMBENT = ("rbf", "log1p", "inferred", "none")
COV_BAND = (43, 48)
N0S = (16, 32, 48)
ALPHA = 0.05


def name(cfg):
    return part_h.cfg_name(cfg)


# ----------------------------------------------------------------- LOO select
def loo_select(f):
    X, Y = common.arm_data(32)
    y = Y[:, J]
    orig = dict(common.FLOORS)
    assert part_h.FLOORS is common.FLOORS
    try:
        common.FLOORS[COL] = f                      # mutate in place, never reassign
        scored = {}
        for i, cfg in enumerate(CONFIGS):
            m, hyp = part_h.fit_and_score(X, y, COL, cfg)   # manual_seed(0) inside
            scored[cfg] = {**m, "idx": i, "noise_std": hyp["noise_std"],
                           "noise_floor_std": hyp["noise_floor_std"]}
    finally:
        common.FLOORS.update(orig)
    assert common.FLOORS == orig
    order = sorted(scored, key=lambda c: (scored[c]["nlpd"], scored[c]["rmse"], scored[c]["idx"]))
    top = order[0]
    for c in order[1:]:                             # part_h.main() lines 163-169
        if scored[c]["nlpd"] <= scored[top]["nlpd"] + 0.02 and scored[c]["rmse"] < scored[top]["rmse"]:
            top = c
    best = scored[order[0]]["nlpd"]
    within = [name(c) for c in order if scored[c]["nlpd"] <= best + 0.02]
    tie = {"invoked": len(within) >= 2, "within_0.02": within,
           "rmse_rule_changed_winner": top != order[0], "nlpd_argmin": name(order[0])}
    rows = [{"floor": f, "config": name(c), "loo_nlpd": scored[c]["nlpd"],
             "loo_rmse": scored[c]["rmse"], "loo_cov95": scored[c]["cov95"],
             "noise_std_standardized": scored[c]["noise_std"],
             "floor_std_standardized": scored[c]["noise_floor_std"],
             "winner": c == top} for c in CONFIGS]
    return top, tie, rows


# ----------------------------------------------------------------- holdout
def latent_sd_t(gp, Xq):
    xq = torch.tensor((np.atleast_2d(Xq) - gp.mx) / gp.sx, dtype=torch.float32)
    with torch.no_grad(), gpytorch.settings.fast_pred_var():
        return gp.model(xq).stddev.numpy() * gp.sy


def fit(X, y, f, cfg):
    """Pinned jitter policy: plain fit; on failure one retry under jitter 1e-4."""
    for attempt, jit in ((0, None), (1, 1e-4)):
        try:
            torch.manual_seed(0)
            if jit is None:
                gp = common.FlexGP(X, y, f, cfg)
                return gp, attempt
            with gpytorch.settings.cholesky_jitter(jit):
                gp = common.FlexGP(X, y, f, cfg)
                return gp, attempt
        except Exception as exc:  # noqa: BLE001  record, never crash
            err = repr(exc)
    return None, err


def score(f, cfg, n0, Xh, yh, y_range):
    X, Y = common.arm_data(n0)
    gp, info = fit(X, Y[:, J], f, cfg)
    base = {"floor": f, "config": name(cfg), "n0": n0}
    if gp is None:
        return {**base, "converged": False, "fit_error": info}
    mu, sd = gp.predict_t(Xh)
    if not (np.isfinite(mu).all() and np.isfinite(sd).all()):
        return {**base, "converged": False, "fit_error": "non-finite prediction"}
    m, z = common.metrics(yh, mu, sd, cfg[1], f, y_range=y_range)
    back = np.expm1 if cfg[1] == "log1p" else (lambda v: v)
    lo, hi = back(mu - 1.96 * sd), back(mu + 1.96 * sd)
    assert int(((yh >= lo) & (yh <= hi)).sum()) == m["cov95"]
    isc = (hi - lo) + (2 / ALPHA) * (lo - yh) * (yh < lo) + (2 / ALPHA) * (yh - hi) * (yh > hi)
    lat = latent_sd_t(gp, Xh)
    ratio = float(lat.max() / max(lat.min(), 1e-9 * lat.max()))
    noise = float(gp.lik.noise)
    raw_scale = gp.sy * ((1.0 + gp.y_med) if cfg[1] == "log1p" else 1.0)
    return {**base, "converged": True, "jitter_retry": bool(info),
            "cov95": m["cov95"], "rmse": m["rmse"], "rmse_le_floor": m["rmse"] <= f,
            "nlpd": m["nlpd"], "rms_z": m["rms_z"], "spearman": m["spearman"], "r2": m["r2"],
            "latent_sd_ratio": ratio,
            "median_halfwidth_raw": float(np.median((hi - lo) / 2)),
            "interval_score": float(isc.mean()),
            "noise_bound_active": noise <= 1.001 * gp.floor_var,
            "learned_noise_raw": math.sqrt(noise) * raw_scale,
            "floor_raw": f}


def joint_bar(rows):
    """rows: the three n0 rows of one (floor, config)."""
    r = {x["n0"]: x for x in rows}
    if not all(x.get("converged") for x in rows):
        return {"pass": False, "c1": False, "c2a": False, "c2b": False, "c3": False, "note": "not converged"}
    c1 = all(COV_BAND[0] <= r[n]["cov95"] <= COV_BAND[1] for n in N0S)
    c2a = r[48]["rmse"] < r[16]["rmse"] and r[32]["rmse"] <= r[16]["rmse"]
    c2b = all(r[n]["rmse"] <= r[n]["floor_raw"] for n in N0S)
    c3 = all(r[n]["latent_sd_ratio"] >= 2 for n in N0S)
    clause = "a+b" if (c2a and c2b) else ("a" if c2a else ("b" if c2b else "-"))
    return {"pass": c1 and (c2a or c2b) and c3, "c1": c1, "c2a": c2a, "c2b": c2b, "c3": c3,
            "rmse_clause": clause}


def main():
    assert common.nlpd_unit_test() < 1e-5
    Xh, Yh = common.load_wave_xy("random_C")
    assert Xh.shape == (48, 6)
    yh = Yh[:, J]
    y_range = float(yh.max() - yh.min())

    loo_rows, sweep, path, cache = [], [], [], {}
    for f in F:
        win, tie, lrows = loo_select(f)
        loo_rows += lrows
        path.append({"floor": f, "winner": name(win), **tie})
        print(f"floor {f:6.0f}: LOO winner {name(win):12s} tie {tie['invoked']} {tie['within_0.02']}")
        arms = [("default", DEFAULT), ("incumbent", INCUMBENT), ("winner", win)]
        for role, cfg in arms:
            for n0 in N0S:
                key = (f, cfg, n0)
                if key not in cache:
                    cache[key] = score(f, cfg, n0, Xh, yh, y_range)
                sweep.append({"role": role, **cache[key]})
        if any(not r.get("converged") for r in sweep if r["floor"] == f and r["role"] == "winner"):
            raise SystemExit(f"STOP: winner arm failed to converge at floor {f} (pinned policy)")

    df = pd.DataFrame(sweep)
    bars = []
    for (f, role), g in df.groupby(["floor", "role"], sort=False):
        b = joint_bar(g.to_dict("records"))
        bars.append({"floor": f, "role": role, "config": g["config"].iloc[0], **b,
                     "bound_active_n0": "".join("A" if x else "i" for x in g["noise_bound_active"])})
    bars = pd.DataFrame(bars)
    df = df.merge(bars[["floor", "role", "pass", "rmse_clause"]], on=["floor", "role"])
    df.to_csv(os.path.join(HERE, "provisional_sweep.csv"), index=False)
    pd.DataFrame(loo_rows).to_csv(os.path.join(HERE, "loo_reselection.csv"), index=False)
    bars.to_csv(os.path.join(HERE, "joint_bar.csv"), index=False)

    w = bars[bars.role == "winner"]
    F_pass = sorted(w[w["pass"]]["floor"].tolist())
    in_band = [f for f in F_pass if 180 <= f <= 880]
    if in_band:
        route = "(i)"
    elif F_pass:
        route = "(iii)" + (" WEAK" if all(w.set_index("floor").loc[f, "rmse_clause"] == "b" for f in F_pass) else "")
    else:
        route = "(ii)"
    out = {"F": F, "F_pass": F_pass, "route": route, "winner_path": path,
           "holdout_exposures_this_prompt": len(cache),
           "distinct_floor_config_scored": len({(k[0], k[1]) for k in cache})}
    with open(os.path.join(HERE, "provisional_summary.json"), "w") as fh:
        json.dump(out, fh, indent=1, default=str)
        fh.write("\n")
    print(bars.to_string(index=False))
    print("F_pass", F_pass, "route", route, "holdout scorings", len(cache))


if __name__ == "__main__":
    main()
