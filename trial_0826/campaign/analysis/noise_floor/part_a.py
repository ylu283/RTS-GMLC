"""Prompt 40 Part A: variogram-nugget estimate of the noise floors.

Estimator (pinned, PROGRESS.md §2, committed 45562e0 before any gamma value):
Cressie-Hawkins semivariance in 6 equal bins of width 0.025 on (0, 0.15);
WLS straight line in h over the k = 4 smallest populated bins (weights =
pair counts, x = count-weighted mean h of the bin); nugget variance = the
intercept at h = 0. h = 0 pairs are excluded from the fit and reported as
replicate observations. Uncertainty: 2,000 bootstrap resamples of the pooled
DESIGN points (seed 20261021). floor_new = sqrt(p90 of the nugget-variance
bootstrap distribution).

Writes ONLY under analysis/noise_floor/: part_a.json, part_a_bins.csv,
part_a_replicates.csv.
"""
from __future__ import annotations

import json
import os

import numpy as np
import pandas as pd
from scipy.optimize import curve_fit

import pool

HERE = os.path.dirname(os.path.abspath(__file__))
OLD = {"load_shed_mwh": 3000.0, "true_curtailment_mwh": 5000.0,
       "total_cost_less_synthetic_usd": 0.5e6}
WIDTH, H_MAX, K = 0.025, 0.15, 4
N_BOOT, SEED = 2000, 20261021
EPS0 = 1e-12


def bin_stats(h, d, w, width=WIDTH, h_max=H_MAX, estimator="ch"):
    """Per-bin (N, mean h, gamma) with pair weights w."""
    nb = int(round(h_max / width))
    b = np.minimum((h / width).astype(int), nb - 1)
    N = np.bincount(b, weights=w, minlength=nb)
    Hs = np.bincount(b, weights=w * h, minlength=nb)
    with np.errstate(invalid="ignore", divide="ignore"):
        hbar = Hs / N
        if estimator == "ch":
            s = np.bincount(b, weights=w * np.sqrt(np.abs(d)), minlength=nb) / N
            g = s ** 4 / (2.0 * (0.457 + 0.494 / N + 0.045 / N ** 2))
        else:  # classical
            g = np.bincount(b, weights=w * d ** 2, minlength=nb) / (2.0 * N)
    return N, hbar, g


def wls_intercept(N, hbar, g, k=K):
    pop = np.nonzero(N > 0)[0][:k]
    if len(pop) < 2:
        return np.nan
    x, y, wt = hbar[pop], g[pop], N[pop]
    W = wt.sum()
    xm, ym = (wt * x).sum() / W, (wt * y).sum() / W
    sxx = (wt * (x - xm) ** 2).sum()
    slope = (wt * (x - xm) * (y - ym)).sum() / sxx if sxx > 0 else 0.0
    return float(ym - slope * xm)


def power_intercept(N, hbar, g, k=6):
    pop = np.nonzero(N > 0)[0][:k]
    f = lambda h, a, b, c: a + b * h ** c  # noqa: E731
    try:
        p, _ = curve_fit(f, hbar[pop], g[pop], p0=[g[pop].min(), g[pop].max(), 1.0],
                         sigma=1 / np.sqrt(N[pop]), maxfev=20000,
                         bounds=([-np.inf, 0, 0.1], [np.inf, np.inf, 4]))
        return float(p[0])
    except RuntimeError:
        return np.nan


class Variogram:
    """Pairs below H_MAX for one pool; y per objective; bootstrap by design."""

    def __init__(self, df):
        self.df = df
        Xn = pool.normalized_X(df)
        I, J, H = pool.pairs_below(Xn, H_MAX)
        self.zero = H <= EPS0
        self.I0, self.J0 = I[self.zero], J[self.zero]
        keep = ~self.zero
        self.I, self.J, self.H = I[keep], J[keep], H[keep]
        self.n = len(df)

    def diffs(self, y):
        return y[self.I] - y[self.J]

    def point(self, y, **kw):
        w = np.ones(len(self.H))
        est = kw.pop("estimator", "ch")
        N, hb, g = bin_stats(self.H, self.diffs(y), w, estimator=est, **kw)
        return N, hb, g

    def boot(self, y, n_boot=N_BOOT, seed=SEED, k=K):
        rng = np.random.default_rng(seed)
        d = self.diffs(y)
        out = np.empty(n_boot)
        for r in range(n_boot):
            m = np.bincount(rng.integers(0, self.n, self.n), minlength=self.n)
            w = (m[self.I] * m[self.J]).astype(float)
            sel = w > 0
            N, hb, g = bin_stats(self.H[sel], d[sel], w[sel])
            out[r] = wls_intercept(N, hb, g, k=k)
        return out


def branch(floor_new, p5_var, old=3000.0):
    if not (100.0 <= floor_new <= 30000.0):
        return "BROKEN (outside [100, 30000] MWh sanity band)"
    if p5_var <= 0 or floor_new < 300.0:
        return "ABSTAIN"
    if 0.8 * old <= floor_new <= 1.25 * old:
        return "VINDICATED"
    if floor_new > 1.25 * old:
        return "UNDERSTATED"
    return "LOWERED"


def estimate(vg, y, label, boot=True):
    N, hb, g = vg.point(y)
    nug = wls_intercept(N, hb, g)
    rec = {"label": label, "nugget_var_point": nug,
           "nugget_sd_point": float(np.sqrt(nug)) if nug > 0 else None,
           "bins": {"N": N.tolist(), "hbar": hb.tolist(), "gamma_ch": g.tolist()}}
    if boot:
        bs = vg.boot(y)
        ok = np.isfinite(bs)
        p5, p50, p90 = np.quantile(bs[ok], [0.05, 0.5, 0.9])
        rec.update({"boot_n": int(ok.sum()), "boot_var_p5": float(p5),
                    "boot_var_p50": float(p50), "boot_var_p90": float(p90),
                    "boot_frac_nonpositive": float(np.mean(bs[ok] <= 0)),
                    "floor_new": float(np.sqrt(p90)) if p90 > 0 else 0.0})
    return rec


def main():
    res = {"pinned": {"width": WIDTH, "h_max": H_MAX, "k": K, "n_boot": N_BOOT,
                      "seed": SEED, "estimator": "cressie_hawkins",
                      "prereg_commit": "45562e0"}}
    df, missing = pool.load_pool()
    res["pool"] = {"n": len(df), "missing_objectives": missing,
                   "by_group": df.groupby("group").size().to_dict()}
    vg = Variogram(df)
    res["pairs"] = {"h_lt_0.15_nonzero": int(len(vg.H)), "h_zero": int(vg.zero.sum()),
                    "min_h": float(vg.H.min())}

    # replicate observations (h = 0)
    reps = []
    for i, j in zip(vg.I0, vg.J0):
        a, b = df.iloc[i], df.iloc[j]
        reps.append({"a": f"{a.wave}:{a['index']}", "b": f"{b.wave}:{b['index']}",
                     **{f"abs_d_{pool.M_COLS[c][:4]}": abs(float(a[col] - b[col]))
                        for c, col in enumerate(pool.M_COLS)},
                     "same_wave": a.wave == b.wave})
    pd.DataFrame(reps).to_csv(os.path.join(HERE, "part_a_replicates.csv"), index=False)
    res["replicates_h0"] = reps

    shed = df["load_shed_mwh"].to_numpy(float)
    head = estimate(vg, shed, "shed raw, full pool")
    head["branch"] = branch(head["floor_new"], head["boot_var_p5"])
    res["shed"] = head
    print(f"SHED floor_new {head['floor_new']:.1f} MWh "
          f"(point sd {head['nugget_sd_point']}, p5/p50/p90 var "
          f"{head['boot_var_p5']:.4g}/{head['boot_var_p50']:.4g}/{head['boot_var_p90']:.4g}, "
          f"frac<=0 {head['boot_frac_nonpositive']:.3f}) -> {head['branch']}")

    # pre-registered robustness rows
    rob = {}
    for name, kw in {"a_space_filling_plus_grid": {"groups": ("space_filling", "grid")},
                     "b_leave_holdout_out": {"drop_waves": ("random_C",)}}.items():
        d2, _ = pool.load_pool(**kw)
        v2 = Variogram(d2)
        r = estimate(v2, d2["load_shed_mwh"].to_numpy(float), name)
        r["n"] = len(d2)
        r["pairs"] = int(len(v2.H))
        r["branch"] = branch(r["floor_new"], r["boot_var_p5"])
        rob[name] = r
        print(f"  {name}: n {len(d2)}, pairs {len(v2.H)}, floor_new {r['floor_new']:.1f} -> {r['branch']}")
    res["robustness"] = rob
    res["robust_branch_unchanged"] = all(r["branch"] == head["branch"] for r in rob.values())

    # reported-only sensitivity (never floor_new)
    sens = {}
    for wdt in (0.0125, 0.05):
        N, hb, g = vg.point(shed, width=wdt)
        sens[f"width_{wdt}"] = wls_intercept(N, hb, g)
    N, hb, g = vg.point(shed)
    for k in (3, 5):
        sens[f"k_{k}"] = wls_intercept(N, hb, g, k=k)
    Nc, hbc, gc = vg.point(shed, estimator="classical")
    sens["classical"] = wls_intercept(Nc, hbc, gc)
    sens["power_law_all_bins"] = power_intercept(N, hb, g)
    res["shed_sensitivity_nugget_var"] = sens
    res["shed_sensitivity_sd"] = {k: (float(np.sqrt(v)) if v and v > 0 else None)
                                  for k, v in sens.items()}

    # heteroscedasticity: strata by pair-mean shed level, and log1p reconciliation
    pm = 0.5 * (shed[vg.I] + shed[vg.J])
    edges = np.quantile(pm, [0, 1 / 3, 2 / 3, 1])
    strata = []
    for s in range(3):
        m = (pm >= edges[s]) & (pm <= edges[s + 1]) if s == 2 else (pm >= edges[s]) & (pm < edges[s + 1])
        N, hb, g = bin_stats(vg.H[m], vg.diffs(shed)[m], np.ones(m.sum()))
        nv = wls_intercept(N, hb, g)
        strata.append({"stratum": s + 1, "pair_mean_shed_range": [float(edges[s]), float(edges[s + 1])],
                       "pairs": int(m.sum()), "nugget_var": nv,
                       "nugget_sd": float(np.sqrt(nv)) if nv > 0 else None})
    res["shed_strata"] = strata
    lt = estimate(vg, np.log1p(shed), "shed log1p, full pool")
    y_med = float(np.median(shed))
    recon = float(np.sqrt(lt["boot_var_p90"]) * (1 + y_med)) if lt["boot_var_p90"] > 0 else None
    res["shed_log1p"] = {**lt, "y_med": y_med, "floor_new_reconciled_raw": recon,
                         "ratio_to_floor_new": recon / head["floor_new"] if recon and head["floor_new"] else None}

    # cross-check objectives (report only; campaign floors do not change)
    for col in pool.M_COLS[1:]:
        r = estimate(vg, df[col].to_numpy(float), f"{col}, full pool")
        r["old_floor"] = OLD[col]
        r["ratio_new_old"] = r["floor_new"] / OLD[col]
        res[col] = r
        print(f"{col}: floor_new {r['floor_new']:.4g} vs old {OLD[col]:.4g} (x{r['ratio_new_old']:.2f})")

    rows = []
    for key in ["shed", "shed_log1p", "true_curtailment_mwh", "total_cost_less_synthetic_usd"]:
        b = res[key]["bins"]
        for i in range(len(b["N"])):
            rows.append({"objective": key, "bin": i + 1, "h_lo": i * WIDTH, "h_hi": (i + 1) * WIDTH,
                         "pairs": b["N"][i], "hbar": b["hbar"][i], "gamma_ch": b["gamma_ch"][i]})
    pd.DataFrame(rows).to_csv(os.path.join(HERE, "part_a_bins.csv"), index=False)
    with open(os.path.join(HERE, "part_a.json"), "w") as f:
        json.dump(res, f, indent=1, default=float)
        f.write("\n")
    print("robust branch unchanged:", res["robust_branch_unchanged"])
    print("wrote part_a.json, part_a_bins.csv, part_a_replicates.csv")


if __name__ == "__main__":
    main()
