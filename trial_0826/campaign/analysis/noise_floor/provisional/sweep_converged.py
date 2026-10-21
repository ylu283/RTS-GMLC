"""Prompt 42, Amendment 1 (option B, Kay 2026-10-21): the identical
7-floor x 3-arm x 3-n0 sweep with CONVERGED fits.

Convergence budget, pinned for THIS diagnostic only: 5,000 Adam steps,
lr 0.01, same optimizer and seeds as the house fit (torch.manual_seed(0)
per fit) -- only the step count changes. Per fit, the loss change over the
final 100 steps is recorded; a fit still moving more than 2e-3 is re-run
from scratch (same seed, deterministic trajectory) at 10,000 steps and
recorded. The LOO reselection uses the SAME converged fitting.

Mechanics mirror sweep.py exactly; common.train_gp is swapped inside this
process only (the convergence_check.py pattern) and restored. Writes only
NEW files suffixed _converged; the house-fit outputs are untouched.
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

EPOCHS = 5000          # Amendment 1, pinned
EPOCHS_EXT = 10000     # extension when dloss100 > TOL at 5,000
TOL = 2e-3
LR = 0.01

_ORIG_TRAIN = common.train_gp
_STATE = {"epochs": EPOCHS, "losses": None}
CONV_LOG = []


def _train_wrapped(model, lik, tx, ty, n_epochs=700, lr=LR):
    """Same optimizer path as the house fit; only n_epochs is overridden."""
    losses = _ORIG_TRAIN(model, lik, tx, ty, n_epochs=_STATE["epochs"], lr=lr)
    _STATE["losses"] = losses
    return losses


def _dloss100():
    ls = _STATE["losses"]
    assert ls is not None and len(ls) == _STATE["epochs"]
    return ls[-101] - ls[-1]


def name(cfg):
    return part_h.cfg_name(cfg)


def log_fit(context, f, cfg, n0, extended, d5000, dfinal, gp):
    raw_scale = gp.sy * ((1.0 + gp.y_med) if cfg[1] == "log1p" else 1.0)
    CONV_LOG.append({
        "context": context, "floor": f, "config": name(cfg), "n0": n0,
        "epochs": _STATE["epochs"], "lr": LR,
        "dloss100_at_5000": d5000, "dloss100_final": dfinal,
        "extended_to_10000": extended,
        "final_loss": _STATE["losses"][-1],
        "learned_noise_raw": math.sqrt(float(gp.lik.noise)) * raw_scale,
        "noise_bound_active": float(gp.lik.noise) <= 1.001 * gp.floor_var,
    })


# ----------------------------------------------------------------- LOO select
def loo_select(f):
    """Identical to sweep.py::loo_select but every part_h.fit_and_score fit
    runs under the converged budget (5,000 steps; per-fit extension rule).
    fit_and_score itself sets torch.manual_seed(0) and builds FlexGP, which
    dispatches through the wrapped common.train_gp."""
    X, Y = common.arm_data(32)
    y = Y[:, J]
    orig = dict(common.FLOORS)
    assert part_h.FLOORS is common.FLOORS
    try:
        common.FLOORS[COL] = f                      # mutate in place, never reassign
        scored = {}
        for i, cfg in enumerate(CONFIGS):
            _STATE["epochs"] = EPOCHS
            m, hyp = part_h.fit_and_score(X, y, COL, cfg)   # manual_seed(0) inside
            d5000 = _dloss100()
            extended = d5000 > TOL
            if extended:
                _STATE["epochs"] = EPOCHS_EXT       # same seed -> deterministic extension
                m, hyp = part_h.fit_and_score(X, y, COL, cfg)
            dfinal = _dloss100()
            # fit once more just to log noise in raw units consistently
            torch.manual_seed(0)
            gp = common.FlexGP(X, y, f, cfg)
            log_fit("loo_n32", f, cfg, 32, extended, d5000, _dloss100(), gp)
            _STATE["epochs"] = EPOCHS
            scored[cfg] = {**m, "idx": i, "noise_std": hyp["noise_std"],
                           "noise_floor_std": hyp["noise_floor_std"],
                           "extended_to_10000": extended,
                           "dloss100_at_5000": d5000, "dloss100_final": dfinal}
    finally:
        common.FLOORS.update(orig)
        _STATE["epochs"] = EPOCHS
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
             "extended_to_10000": scored[c]["extended_to_10000"],
             "dloss100_at_5000": scored[c]["dloss100_at_5000"],
             "dloss100_final": scored[c]["dloss100_final"],
             "winner": c == top} for c in CONFIGS]
    return top, tie, rows


# ----------------------------------------------------------------- holdout
def latent_sd_t(gp, Xq):
    xq = torch.tensor((np.atleast_2d(Xq) - gp.mx) / gp.sx, dtype=torch.float32)
    with torch.no_grad(), gpytorch.settings.fast_pred_var():
        return gp.model(xq).stddev.numpy() * gp.sy


def fit(X, y, f, cfg, context, n0):
    """Pinned jitter policy: plain fit; on failure one retry under jitter 1e-4.
    Converged budget on top: 5,000 steps; extend THAT fit to 10,000 (same
    seed, from scratch -> deterministic) when dloss100 > 2e-3."""
    for attempt, jit in ((0, None), (1, 1e-4)):
        try:
            d5000, extended = None, False
            for epochs in (EPOCHS, EPOCHS_EXT):
                _STATE["epochs"] = epochs
                torch.manual_seed(0)
                if jit is None:
                    gp = common.FlexGP(X, y, f, cfg)
                else:
                    with gpytorch.settings.cholesky_jitter(jit):
                        gp = common.FlexGP(X, y, f, cfg)
                d = _dloss100()
                if epochs == EPOCHS:
                    d5000 = d
                    if d <= TOL:
                        break
                    extended = True
            log_fit(context, f, cfg, n0, extended, d5000, d, gp)
            _STATE["epochs"] = EPOCHS
            return gp, attempt
        except Exception as exc:  # noqa: BLE001  record, never crash
            err = repr(exc)
            _STATE["epochs"] = EPOCHS
    return None, err


def score(f, cfg, n0, Xh, yh, y_range, preds):
    X, Y = common.arm_data(n0)
    gp, info = fit(X, Y[:, J], f, cfg, "holdout", n0)
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
    pm = back(mu)
    for q in range(len(yh)):
        preds.append({"floor": f, "config": name(cfg), "n0": n0, "i": q,
                      "actual": yh[q], "pred_median_raw": pm[q],
                      "lo_raw": lo[q], "hi_raw": hi[q]})
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
    common.train_gp = _train_wrapped
    try:
        # Pinned pre-run check: default at floor 306, 5,000 steps must
        # reproduce convergence_check.txt (learned noise ~309 MWh raw).
        X32, Y32 = common.arm_data(32)
        _STATE["epochs"] = EPOCHS
        torch.manual_seed(0)
        gpv = common.FlexGP(X32, Y32[:, J], 306.0, DEFAULT)
        nv = math.sqrt(float(gpv.lik.noise)) * gpv.sy
        print(f"verify: default f=306 ep5000 learned noise {nv:.1f} MWh "
              f"(expect ~309), dloss100 {_dloss100():.2e}")
        assert abs(nv - 309.4) < 2.0, nv

        Xh, Yh = common.load_wave_xy("random_C")
        assert Xh.shape == (48, 6)
        yh = Yh[:, J]
        y_range = float(yh.max() - yh.min())

        loo_rows, sweep, path, cache, preds = [], [], [], {}, []
        for f in F:
            win, tie, lrows = loo_select(f)
            loo_rows += lrows
            path.append({"floor": f, "winner": name(win), **tie})
            print(f"floor {f:6.0f}: LOO winner {name(win):12s} tie {tie['invoked']} {tie['within_0.02']}",
                  flush=True)
            arms = [("default", DEFAULT), ("incumbent", INCUMBENT), ("winner", win)]
            for role, cfg in arms:
                for n0 in N0S:
                    key = (f, cfg, n0)
                    if key not in cache:
                        cache[key] = score(f, cfg, n0, Xh, yh, y_range, preds)
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
        df.to_csv(os.path.join(HERE, "provisional_sweep_converged.csv"), index=False)
        pd.DataFrame(loo_rows).to_csv(os.path.join(HERE, "loo_reselection_converged.csv"), index=False)
        bars.to_csv(os.path.join(HERE, "joint_bar_converged.csv"), index=False)
        pd.DataFrame(CONV_LOG).to_csv(os.path.join(HERE, "convergence_log_converged.csv"), index=False)
        pd.DataFrame(preds).to_csv(os.path.join(HERE, "predictions_converged.csv"), index=False)

        w = bars[bars.role == "winner"]
        F_pass = sorted(w[w["pass"]]["floor"].tolist())
        in_band = [f for f in F_pass if 180 <= f <= 880]
        if in_band:
            route = "(i)"
        elif F_pass:
            route = "(iii)" + (" WEAK" if all(w.set_index("floor").loc[f, "rmse_clause"] == "b" for f in F_pass) else "")
        else:
            route = "(ii)"
        n_ext = sum(1 for r in CONV_LOG if r["extended_to_10000"])
        out = {"amendment": 1, "fit": f"{EPOCHS} Adam steps, lr {LR}, seed 0 per fit; "
                                      f"extend to {EPOCHS_EXT} when dloss100 > {TOL}",
               "F": F, "F_pass": F_pass, "route": route, "winner_path": path,
               "fits_extended_to_10000": n_ext,
               "holdout_exposures_this_prompt": len(cache),
               "distinct_floor_config_scored": len({(k[0], k[1]) for k in cache})}
        with open(os.path.join(HERE, "provisional_summary_converged.json"), "w") as fh:
            json.dump(out, fh, indent=1, default=str)
            fh.write("\n")
        print(bars.to_string(index=False))
        print("F_pass", F_pass, "route", route, "holdout scorings", len(cache),
              "extended fits", n_ext)
    finally:
        common.train_gp = _ORIG_TRAIN
    assert common.train_gp is _ORIG_TRAIN


if __name__ == "__main__":
    main()
