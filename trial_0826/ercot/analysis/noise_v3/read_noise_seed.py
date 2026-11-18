#!/usr/bin/env python3
"""Prompt 63 v1 section 3 (Part C) — read waves/noise_seed_E and write NOISE_SEED_E.md (zero simulation).

    cd trial_0826/ercot && BOGP_PATH=/Users/yilu/Documents/GitHub/bo-gp-qparego \\
        /opt/anaconda3/envs/bogp-botorch/bin/python analysis/noise_v3/read_noise_seed.py

Inputs (blind discipline, prompt 63 section 4): the 18 noise_seed_E runs and ONLY the 4 n0_E
anchor runs named in `replicate_of` (n0_E:25 / 29 / 46 / 4 = the Seed-0, Threads-4 solve of
each design), via pool_objectives.pool_row; nothing else from n0_E; never random_E. The
perturbed ruler and B_j come from analysis/noise_v3/ercot_noise.json (D2 excluded, 63 A1).
The tau_res ref point is the frozen plan 6.3 R (waves/n0_E/landing_R.json key "R" only).

Reads (pre-registered, wave README / prompt 63 section 3), per candidate j (28 pool ids;
D3 = the S3a nuclear-starts check inside SUSPECT):
  - chatter sd per design sigma_c,j(d) = sd (ddof 1) over the 5 solves (Seed 0-4); pooled
    sigma_c,j = sqrt(mean of the 4 variances), df 16; heteroscedasticity: the 52 section 3
    trigger (F test max/min variance, alpha 0.05 AND ratio > 3) across designs, plus the
    sd-vs-T rank correlation (descriptive);
  - Sigma_c from the 16 deltas y_seed_k - y_seed_0 (tau_E.sigma_c_from_deltas: second
    moment / 2, Ledoit-Wolf toward diag) over every id finite on all 16;
  - A3: ratio = sigma_c,j * sqrt 2 / sigma_hat_pert,j (both two-run scales); AGREE iff
    1/2 <= ratio <= 2 (both 0 -> AGREE); else the perturbed ruler is labelled
    "perturbation response, not chatter";
  - thread check: rows 17 / 18 (Threads 8 / 1, Seed 0) vs the anchor n0_E:29 (Threads 4):
    overall.csv md5, per-candidate delta, divergent RUC days; conditions.txt lines;
  - B_j^seed = max(3 sigma_c,j sqrt 2, max |delta_seed|) beside B_j (perturbed, D2 excluded);
  - tau_res (tau_E.tau_res, REPORT-ONLY): E-D7 (nav = 32 or 48) is not recorded, so the
    nav-start set is not defined without reading n0_E rows beyond the anchors -> computed
    on the 4 anchor designs' Y only, labelled PROVISIONAL;
  - 54 input: sigma_c,j (df 16) as the measured-floor candidate.
"""
import argparse
import json
import math
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ERCOT = os.path.abspath(os.path.join(HERE, "..", ".."))
for p in (ERCOT, HERE, os.path.join(ERCOT, "analysis", "methods_E")):
    if p not in sys.path:
        sys.path.insert(0, p)
import pool_objectives as po  # noqa: E402
import read_noise as rn  # noqa: E402

WAVE = "noise_seed_E"
N_ROWS = 18
SEEDS = (1, 2, 3, 4)
AGREE_FACTOR = 2.0
HV_OBJ = ["V1", "E1", "R4", "N1"]
HEAD = ["V1", "E1", "R4", "N1", "N4"]
PERTURBED_LABEL = "perturbation response, not chatter"


# --------------------------------------------------------------------------
# inputs
# --------------------------------------------------------------------------
def _conditions(run_dir):
    p = os.path.join(run_dir, "conditions.txt")
    out = {}
    if not os.path.isfile(p):
        return out
    for line in open(p):
        line = line.rstrip("\n")
        for k in ("HOST", "CPU", "GUROBI", "THREADS", "CODE"):
            tag = f"NOISE_SEED_E_{k} "
            if line.startswith(tag):
                out[k.lower()] = line[len(tag):]
        if line.startswith("run_ercot_pcm: index="):
            i = line.find("ruc_solver_options=")
            j = line.find(" PEM_data=")
            out["ruc_solver_options"] = line[i + len("ruc_solver_options="):j] if i >= 0 else None
    return out


def _solve(run_dir):
    p = os.path.join(run_dir, "ruc_quality.csv")
    if not os.path.isfile(p):
        return {}
    q = pd.read_csv(p, usecols=["solve_time_s", "status"])
    t = q["solve_time_s"].to_numpy(float)
    return {"max_solve_s": float(t.max()), "n_days_gt_600s": int((t > 600.0).sum()),
            "n_ruc": int(len(t)), "n_optimal": int((q["status"].astype(str) == "OPTIMAL").sum())}


def read_run(key, extr, waves, defs):
    d = po.run_dir(key, extr)
    row = po.pool_row(key, extr=extr, waves=waves, defs=defs)
    jp = os.path.join(d, "pool_full_metrics.json")
    if os.path.isfile(jp):
        with open(jp) as f:
            pm = json.load(f)
        for c in rn.JSON_OVERRIDE:
            v = pm.get(c)
            v = np.nan if v is None else float(v)
            if np.isfinite(row.get(c, np.nan)) and np.isfinite(v):
                assert abs(row[c] - v) <= 1e-6 * max(1.0, abs(v)), (key, c, row[c], v)
            row[c] = v if np.isfinite(v) else row.get(c, np.nan)
        row["n_ruc_time_limit"] = pm.get("n_ruc_time_limit")
    from analysis.ercot_gp.ercot_gp_loader import suspect_flag
    row["suspect"] = bool(suspect_flag(row))
    row["identity"] = rn.read_identity(d)
    row["conditions"] = _conditions(d)
    row.update(_solve(d))
    return row


def load(extr=po.EXTR, waves=po.WAVES, defs=None):
    defs = defs or po.load_defs()
    dm = pd.read_csv(os.path.join(waves, WAVE, "design_matrix.csv"),
                     dtype={"replicate_of": str, "level_id": str}, float_precision="round_trip")
    assert len(dm) == N_ROWS and list(dm["index"]) == list(range(1, N_ROWS + 1))
    wall = rn.read_wallclock(os.path.join(extr, WAVE, "wallclock.csv"))
    rows = {}
    for _, r in dm.iterrows():
        i = int(r["index"])
        rec = read_run(f"{WAVE}:{i}", extr, waves, defs)
        rec.update({"seed": int(r["seed"]), "ruc_threads": int(r["ruc_threads"]), "anchor": str(r["replicate_of"]),
                    "level_id": str(r["level_id"]), "T": float(r["pem_mw"]), "wall_s": wall.get(i, np.nan)})
        rec["core_h"] = rec["wall_s"] / 3600.0 * rec["ruc_threads"] if np.isfinite(rec["wall_s"]) else np.nan
        rows[i] = rec
    anchors = {}
    for a in sorted({r["anchor"] for r in rows.values()}, key=lambda s: int(s.split(":")[1])):
        assert a.startswith("n0_E:"), a
        rec = read_run(a, extr, waves, defs)                     # ONLY the 4 anchor runs of n0_E
        rec.update({"seed": 0, "ruc_threads": 4, "anchor": a, "level_id": "anchor (n0_E Seed 0, Threads 4)"})
        anchors[a] = rec
    assert len(anchors) == 4, sorted(anchors)
    return dm, rows, anchors


# --------------------------------------------------------------------------
# statistics
# --------------------------------------------------------------------------
def designs(dm, rows, anchors):
    """[(anchor key, label, T, [y-records Seed 0..4])] in quantile order (row order of dm)."""
    out = []
    for a in dict.fromkeys(dm.loc[dm["seed"] > 0, "replicate_of"]):
        seeds = {rows[i]["seed"]: rows[i] for i in rows if rows[i]["anchor"] == a and rows[i]["ruc_threads"] == 4}
        assert sorted(seeds) == list(SEEDS), (a, sorted(seeds))
        lab = rows[min(i for i in rows if rows[i]["anchor"] == a)]["level_id"].split("_")[0]
        out.append((a, lab, float(dm.loc[dm["replicate_of"] == a, "pem_mw"].iloc[0]),
                    [anchors[a]] + [seeds[k] for k in SEEDS]))
    return out


def _v(rec, c):
    try:
        return float(rec.get(c, np.nan))
    except (TypeError, ValueError):
        return np.nan


def _rank_corr(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float)
    if len(x) < 3 or np.all(y == y[0]):
        return np.nan
    rx, ry = pd.Series(x).rank().to_numpy(), pd.Series(y).rank().to_numpy()
    return float(np.corrcoef(rx, ry)[0, 1])


def candidate_stats(D, ids, noise_json):
    """D = designs(); per candidate: per-design sd, pooled sd (df 16), trigger, deltas, bars, A3."""
    out = {}
    for c in ids:
        Y = np.array([[_v(r, c) for r in recs] for _, _, _, recs in D])          # 4 x 5
        finite = bool(np.isfinite(Y).all())
        sds = [float(np.std(y, ddof=1)) if np.isfinite(y).all() else np.nan for y in Y]
        lv = [(s, len(y) - 1) for s, y in zip(sds, Y) if np.isfinite(s)]
        pooled = float(math.sqrt(np.mean([s * s for s, _ in lv]))) if lv else np.nan
        df = int(sum(nu for _, nu in lv))
        lo, hi = rn.sd_ci(pooled, df) if lv and pooled > 0 else (np.nan, np.nan)
        tr = rn.trigger(lv)
        delta = (Y[:, 1:] - Y[:, [0]]).ravel()                                     # 16 deltas vs Seed 0
        dfin = delta[np.isfinite(delta)]
        maxd = float(np.abs(dfin).max()) if len(dfin) else np.nan
        b_seed = float(max(3.0 * pooled * math.sqrt(2.0), maxd)) if np.isfinite(pooled) and np.isfinite(maxd) else np.nan
        pc = noise_json["per_candidate"].get(c, {})
        bar = pc.get("bar", {}) or {}
        sp = float(bar.get("sigma_hat", np.nan)) if bar.get("sigma_hat") is not None else np.nan
        bj = float(bar.get("B", np.nan)) if bar.get("B") is not None else np.nan
        two = pooled * math.sqrt(2.0) if np.isfinite(pooled) else np.nan
        if not (np.isfinite(two) and np.isfinite(sp)):
            ratio, verdict = np.nan, "n/a"
        elif two == 0.0 and sp == 0.0:
            ratio, verdict = np.nan, "AGREE (both exactly 0)"
        elif two == 0.0 or sp == 0.0:
            ratio, verdict = (0.0 if two == 0.0 else float("inf")), "DISAGREE (one ruler is 0)"
        else:
            ratio = float(two / sp)
            verdict = "AGREE" if 1.0 / AGREE_FACTOR <= ratio <= AGREE_FACTOR else "DISAGREE"
        out[c] = {"id": c, "finite_all": finite, "y": Y.tolist(), "sd_by_design": sds, "df_by_design": [len(y) - 1 for y in Y],
                  "sigma_c": pooled, "df": df, "sigma_c_ci95": [lo, hi], "trigger": tr,
                  "sd_vs_T_rank_corr": _rank_corr([t for _, _, t, _ in D], sds) if all(np.isfinite(sds)) else np.nan,
                  "max_over_min_sd": (float(max(sds) / min(sds)) if all(np.isfinite(sds)) and min(sds) > 0 else
                                      (np.nan if all(np.isfinite(sds)) and max(sds) == 0 else float("inf"))),
                  "delta_seed": delta.tolist(), "max_abs_delta_seed": maxd, "B_seed": b_seed,
                  "sigma_hat_pert": sp, "B_pert": bj, "B_pert_n": bar.get("n"),
                  "ratio_seed_over_pert": ratio, "A3": verdict,
                  "perturbed_ruler_label": (None if verdict.startswith("AGREE") or verdict == "n/a" else PERTURBED_LABEL)}
    return out


def thread_check(rows, anchors, ids, extr):
    th = [r for r in rows.values() if r["seed"] == 0]
    out = []
    for r in sorted(th, key=lambda r: -r["ruc_threads"]):
        a = anchors[r["anchor"]]
        c1, c0 = rn._ruc_cost(po.run_dir(r["key"], extr)), rn._ruc_cost(po.run_dir(a["key"], extr))
        dv = rn.divergence_row(c1, c0) if c1 is not None and c0 is not None else {}
        nz = {c: _v(r, c) - _v(a, c) for c in ids if np.isfinite(_v(r, c) - _v(a, c)) and _v(r, c) != _v(a, c)}
        out.append({"key": r["key"], "anchor": a["key"], "threads": r["ruc_threads"],
                    "overall_md5": r["overall_md5"], "anchor_md5": a["overall_md5"],
                    "bit_identical": bool(r["overall_md5"] == a["overall_md5"]),
                    "n_candidates_differing": len(nz), "delta": nz,
                    "n_divergent_days": dv.get("n_divergent"), "first_divergent_day_no": dv.get("first_divergent_day_no"),
                    "median_rel_all_days": dv.get("median_rel_all_days"), "conditions": r["conditions"]})
    return out


def seed_day_divergence(D, extr):
    out = []
    for a, lab, T, recs in D:
        c0 = rn._ruc_cost(po.run_dir(recs[0]["key"], extr))
        for r in recs[1:]:
            c1 = rn._ruc_cost(po.run_dir(r["key"], extr))
            dv = rn.divergence_row(c1, c0)
            out.append({"key": r["key"], "anchor": a, "label": lab, "seed": r["seed"],
                        "md5_equal_anchor": bool(r["overall_md5"] == recs[0]["overall_md5"]), **dv})
    return pd.DataFrame(out)


def sigma_c_matrix(D, ids):
    import tau_E
    cols = []
    for c in ids:
        Y = np.array([[_v(r, c) for r in recs] for _, _, _, recs in D])
        d = (Y[:, 1:] - Y[:, [0]]).ravel()
        if np.isfinite(d).all():
            cols.append((c, d))
    M = np.column_stack([d for _, d in cols])
    S, info = tau_E.sigma_c_from_deltas(M)
    ids_ok = [c for c, _ in cols]
    info["ids"] = ids_ok
    info["note"] = ("16 deltas vs the Seed-0 solve of the same design; the 4 deltas of one design share their "
                    "Seed-0 value (not independent) — the estimator treats them as 16 pairs (disclosed)")
    return pd.DataFrame(S, index=ids_ok, columns=ids_ok), info


def tau_res_provisional(D, Sc, ref_path, objectives=HV_OBJ, pert_sigma_csv=None):
    import tau_E
    with open(ref_path) as f:
        R = json.load(f)["R"]                                    # ONLY the frozen plan 6.3 ref point
    ref = np.array([float(R[o]) for o in objectives])
    Y = np.array([[_v(recs[0], o) for o in objectives] for _, _, _, recs in D])
    S4 = Sc.loc[objectives, objectives].to_numpy(float)
    out = tau_E.tau_res(Y, ref, S4)
    import common_E
    out.update({"status": "PROVISIONAL (4 anchor designs only; E-D7 nav set not recorded)",
                "objectives": objectives, "ref": ref.tolist(), "ref_source": "waves/n0_E/landing_R.json key R (plan 6.3, AMENDMENT 2026-11-16)",
                "starts": [a for a, _, _, _ in D], "hv0": common_E.hv_exact(Y, ref),
                "n_starts_on_front_below_ref": int(np.all(Y < ref, axis=1).sum())})
    out["tau_res_over_hv0"] = (out["tau_res"] / out["hv0"]) if out["hv0"] > 0 else None
    if pert_sigma_csv and os.path.isfile(pert_sigma_csv):
        Sp = tau_E.read_cov_csv(pert_sigma_csv, objectives)
        out["tau_res_with_perturbed_provisional_sigma_c"] = tau_E.tau_res(Y, ref, Sp)["tau_res"]
    return out


# --------------------------------------------------------------------------
# figures (bold labels AND ticks; assert-before-draw)
# --------------------------------------------------------------------------
def _bold(ax):
    for t in ax.get_xticklabels() + ax.get_yticklabels():
        t.set_fontweight("bold")
    ax.xaxis.label.set_fontweight("bold")
    ax.yaxis.label.set_fontweight("bold")
    ax.title.set_fontweight("bold")


def figures(cs, D, defs, out_dir, csv_df):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    Ts = [t for _, _, t, _ in D]
    labs = [lab for _, lab, _, _ in D]
    # fig 1: per-design chatter sd vs T, pooled line
    fig, axs = plt.subplots(1, len(HEAD), figsize=(4.0 * len(HEAD), 3.6))
    for ax, c in zip(axs, HEAD):
        sds = cs[c]["sd_by_design"]
        row = csv_df[csv_df["id"] == c].iloc[0]
        assert np.allclose(sds, [row[f"sd_{lb}"] for lb in labs]) and np.isclose(cs[c]["sigma_c"], row["sigma_c"])
        ax.plot(Ts, sds, "o-", color="#1f5f99")
        for t, s, lb in zip(Ts, sds, labs):
            ax.annotate(lb, (t, s), textcoords="offset points", xytext=(4, 4), fontsize=8, fontweight="bold")
        ax.axhline(cs[c]["sigma_c"], color="#b03a2e", ls="--", label=f"pooled σ̂_c (df {cs[c]['df']})")
        ax.set_xlabel("total PEM T (MW)")
        ax.set_ylabel(f"{c} chatter sd ({defs['candidates'].get(c, {}).get('unit', '')})")
        ax.set_title(f"{c}: sd over Seed 0–4")
        ax.set_ylim(bottom=0)
        ax.legend(fontsize=8, prop={"weight": "bold", "size": 8})
        _bold(ax)
    fig.tight_layout()
    p1 = os.path.join(out_dir, "fig_seed_chatter_sd.png")
    fig.savefig(p1, dpi=150)
    plt.close(fig)
    # fig 2: A3 ratio per gradable id with the [1/2, 2] band
    g = [c for c in defs["global_order"][:22] if np.isfinite(cs[c]["ratio_seed_over_pert"]) and cs[c]["ratio_seed_over_pert"] > 0
         and np.isfinite(np.log(cs[c]["ratio_seed_over_pert"]))]
    r = [cs[c]["ratio_seed_over_pert"] for c in g]
    for c, v in zip(g, r):
        assert np.isclose(v, csv_df.loc[csv_df["id"] == c, "ratio_seed_over_pert"].iloc[0])
    fig, ax = plt.subplots(figsize=(10, 3.8))
    cols = ["#1e8449" if 0.5 <= v <= 2.0 else "#b03a2e" for v in r]
    ax.bar(range(len(g)), r, color=cols)
    ax.axhspan(0.5, 2.0, color="#d5f5e3", alpha=0.5, zorder=0)
    ax.axhline(1.0, color="k", lw=0.8)
    ax.set_yscale("log")
    from matplotlib.ticker import FixedLocator, FormatStrFormatter, NullFormatter, NullLocator
    yt = [0.4, 0.5, 0.7, 1.0, 1.4, 2.0, 3.0]
    assert min(r) >= yt[0] and max(r) <= yt[-1], (min(r), max(r))
    ax.set_ylim(yt[0], yt[-1])
    ax.yaxis.set_major_locator(FixedLocator(yt))
    ax.yaxis.set_major_formatter(FormatStrFormatter("%g"))
    ax.yaxis.set_minor_locator(NullLocator())
    ax.yaxis.set_minor_formatter(NullFormatter())
    ax.set_xticks(range(len(g)))
    ax.set_xticklabels(g)
    ax.set_ylabel("σ̂_c·√2 / σ̂_pert (two-run scales)")
    ax.set_xlabel("candidate (gradable)")
    ax.set_title("A3: Seed chatter vs ±0.1 % perturbed amplitude (green band = AGREE, within 2×)")
    _bold(ax)
    fig.tight_layout()
    p2 = os.path.join(out_dir, "fig_seed_a3_ratio.png")
    fig.savefig(p2, dpi=150)
    plt.close(fig)
    return [p1, p2]


# --------------------------------------------------------------------------
# outputs
# --------------------------------------------------------------------------
_f = rn._f


def to_frame(cs, D, defs, ids):
    labs = [lab for _, lab, _, _ in D]
    rows = []
    for c in ids:
        p = cs[c]
        d = {"id": c, "unit": defs["candidates"].get(c, {}).get("unit"), "gradable": c in defs["global_order"][:22],
             "sigma_c": p["sigma_c"], "df": p["df"], "sigma_c_ci95_lo": p["sigma_c_ci95"][0], "sigma_c_ci95_hi": p["sigma_c_ci95"][1]}
        for lb, s in zip(labs, p["sd_by_design"]):
            d[f"sd_{lb}"] = s
        d.update({"max_over_min_sd": p["max_over_min_sd"], "trigger_fires": p["trigger"]["fires"],
                  "trigger_verdict": p["trigger"]["verdict"], "sd_vs_T_rank_corr": p["sd_vs_T_rank_corr"],
                  "max_abs_delta_seed": p["max_abs_delta_seed"], "B_seed": p["B_seed"],
                  "sigma_hat_pert": p["sigma_hat_pert"], "B_pert": p["B_pert"],
                  "ratio_seed_over_pert": p["ratio_seed_over_pert"], "A3": p["A3"],
                  "perturbed_ruler_label": p["perturbed_ruler_label"] or ""})
        rows.append(d)
    return pd.DataFrame(rows)


def fmt_md(S):
    cs, D, defs = S["cand"], S["designs"], S["defs"]
    ids, grad = S["ids"], S["defs"]["global_order"][:22]
    labs = [lab for _, lab, _, _ in D]
    L = ["# NOISE_SEED_E — Gurobi-Seed chatter rulers (prompt 63 v1 Part C; landed 2026-11-18)", "",
         f"Wave `waves/{WAVE}` (18 runs, analysis-only) + the 4 n0_E anchor runs "
         f"({', '.join(a for a, _, _, _ in D)}: Seed 0, Threads 4). Every value from `pool_objectives.pool_row` "
         "(E8 / E9 / N5 from `pool_full_metrics.json`). Reads pre-registered in `waves/noise_seed_E/README.md` "
         "(prompt 63 section 3). Nothing else of n0_E and nothing of random_E was read. This file decides nothing; "
         "the A3 outcome is recorded once below.", ""]
    # 0 runs
    sus = [r["key"] for r in S["runs"] if r["suspect"]]
    idv = sorted({(r["identity"] or {}).get("ruc_mipgap") for r in S["runs"]} | set())
    L += ["## 0. Runs, identity, SUSPECT", "",
          f"{len(S['runs'])} runs read (18 wave + 4 anchors). Identity: ruc_mipgap {idv}, ruc_time_limit "
          f"{sorted({(r['identity'] or {}).get('ruc_time_limit') for r in S['runs']})}. SUSPECT (S1 ∧ S2 ∧ S3a; S3a = the "
          f"D3 nuclear-starts check): {', '.join(sus) if sus else 'none'}. Time-limit hits: "
          f"{sum(int(r.get('n_ruc_time_limit') or 0) for r in S['runs'])}. Max daily RUC solve over the 22 runs: "
          f"{_f(max(r.get('max_solve_s', 0) for r in S['runs']), 4)} s; days > 600 s: "
          f"{sum(int(r.get('n_days_gt_600s', 0)) for r in S['runs'] if r['key'].startswith(WAVE))} on the 18 wave runs.", "",
          "| key | label | anchor | seed | threads | T (MW) | overall md5 | host | Gurobi | Seed echo (ruc_solver_options) | max RUC solve s | days > 600 s | wall h | core-h | SUSPECT |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in S["runs"]:
        cd = r.get("conditions", {})
        w = r.get("wall_s", np.nan)
        L.append(f"| {r['key']} | {r['level_id']} | {r['anchor']} | {r['seed']} | {r['ruc_threads']} | "
                 f"{_f(r.get('T', r.get('pem_mw', np.nan)), 6)} | `{r['overall_md5'][:8]}` | {cd.get('host', '—')} | "
                 f"{cd.get('gurobi', '—')} | {cd.get('ruc_solver_options', '—')} | {_f(r.get('max_solve_s', np.nan), 4)} | "
                 f"{r.get('n_days_gt_600s', '—')} | {_f(w / 3600.0 if np.isfinite(w) else np.nan, 3)} | "
                 f"{_f(r.get('core_h', np.nan), 3)} | {'**yes**' if r['suspect'] else 'no'} |")
    rt = S["runtime"]
    L += ["", f"Core-h (wall × slots): total {_f(rt['total'], 4)}, median per Threads-4 run {_f(rt['median_t4'], 3)} "
          f"(min {_f(rt['min_t4'], 3)}, max {_f(rt['max_t4'], 3)}); Threads 8 run {_f(rt['t8'], 3)}, Threads 1 run {_f(rt['t1'], 3)}.", ""]
    # 1 chatter sd
    L += ["## 1. Chatter sd per design and pooled (Seed 0–4; df 4 per design, pooled df 16)", "",
          "Per design: sd (ddof 1) over the 5 solves. Pooled σ̂_c = sqrt(mean of the 4 variances), df 16, chi-square 95 % CI. "
          "Heteroscedasticity: the 52 section 3 trigger (F test of max / min variance, df 4 / 4, alpha 0.05 AND ratio > 3; "
          "with df 4 / 4 it rejects only above ratio 6.39) and the rank correlation of the 4 design sds with T "
          "(descriptive; n = 4). A non-firing trigger reads \"not detectable at this df\".", "",
          "| id | unit | " + " | ".join(f"sd {lb} (T {t:.0f})" for _, lb, t, _ in D)
          + " | pooled σ̂_c (df 16) | 95 % CI | max/min sd | trigger | rank corr(sd, T) |",
          "|---|---|" + "---|" * len(D) + "---|---|---|---|---|"]
    for c in ids:
        p = cs[c]
        L.append(f"| {c} | {defs['candidates'].get(c, {}).get('unit', '')} | " + " | ".join(_f(s) for s in p["sd_by_design"])
                 + f" | {_f(p['sigma_c'])} | [{_f(p['sigma_c_ci95'][0])}, {_f(p['sigma_c_ci95'][1])}] | {_f(p['max_over_min_sd'], 3)} | "
                 f"{rn._trig_short(p['trigger'])} | {_f(p['sd_vs_T_rank_corr'], 2)} |")
    fires = [c for c in grad if cs[c]["trigger"].get("fires")]
    L += ["", f"Trigger fires (gradable): {len(fires)} of {len(grad)} ({', '.join(fires) or 'none'}). "
          "Figure: `fig_seed_chatter_sd.png` (V1, E1, R4, N1, N4: sd per design vs T, pooled line).", ""]
    # 2 A3 + bars
    L += ["## 2. A3 test and the bars (FINAL, recorded once)", "",
          "A3 compares like with like on the two-run scale: ratio = σ̂_c·√2 / σ̂_pert, with σ̂_pert = sqrt(mean δ²) over the "
          "6 non-structural ±0.1 % perturbed deltas (`ercot_noise.json` `per_candidate.<j>.bar`, D2 excluded). AGREE iff "
          "1/2 ≤ ratio ≤ 2. B_j^seed = max(3·σ̂_c·√2, max |Δ_seed|) over the 16 deltas vs Seed 0; B_j = the perturbed bar "
          "(prompt 61 section 3, D2 excluded).", "",
          "| id | unit | σ̂_c (per run) | σ̂_c·√2 | σ̂_pert | ratio | A3 | max |Δ_seed| | B_j^seed | B_j (perturbed) | B_j^seed / B_j |",
          "|---|---|---|---|---|---|---|---|---|---|---|"]
    for c in ids:
        p = cs[c]
        rb = (p["B_seed"] / p["B_pert"]) if np.isfinite(p["B_seed"]) and np.isfinite(p["B_pert"]) and p["B_pert"] > 0 else np.nan
        L.append(f"| {c} | {defs['candidates'].get(c, {}).get('unit', '')} | {_f(p['sigma_c'])} | "
                 f"{_f(p['sigma_c'] * math.sqrt(2) if np.isfinite(p['sigma_c']) else np.nan)} | {_f(p['sigma_hat_pert'])} | "
                 f"{_f(p['ratio_seed_over_pert'], 3)} | {p['A3']} | {_f(p['max_abs_delta_seed'])} | {_f(p['B_seed'])} | "
                 f"{_f(p['B_pert'])} | {_f(rb, 3)} |")
    ag = [c for c in grad if cs[c]["A3"].startswith("AGREE")]
    dis = [c for c in grad if cs[c]["A3"].startswith("DISAGREE")]
    hv = {c: cs[c]["A3"] for c in HEAD}
    L += ["", f"**A3 verdict (gradable, {len(grad)} ids): AGREE on {len(ag)} ({', '.join(ag) or 'none'}); DISAGREE on "
          f"{len(dis)} ({', '.join(dis) or 'none'}).** Headline objectives: "
          + "; ".join(f"{c} {v}" for c, v in hv.items()) + ".",
          "For every DISAGREE id the perturbed ruler is labelled \"" + PERTURBED_LABEL + "\" and B_j is redefined on "
          "Seed chatter (B_j^seed); for every AGREE id both bars measure the same chatter and both are reported "
          "(prompt 63 section 3; the strategy session amends 61 / 62; 61 has already read, so both bars are reported there). "
          "Figure: `fig_seed_a3_ratio.png`.", ""]
    # 3 Sigma_c
    sc, sci = S["sigma_c"], S["sigma_c_info"]
    blk = [c for c in HEAD if c in sc.index]
    L += ["## 3. Chatter covariance Σ_c", "",
          f"`ercot_noise_seed_sigma_c.csv` ({sc.shape[0]} × {sc.shape[1]}; ids finite on all 16 deltas). Estimator "
          "`tau_E.sigma_c_from_deltas`: per-run Σ_c = (second moment of the 16 deltas about 0) / 2, Ledoit–Wolf shrinkage "
          f"of the RMS-scaled matrix toward I (= toward the diagonal); shrinkage {sci['lw_shrinkage']:.3f}; "
          f"{sci['zero_columns']} zero columns. {sci['note']}.", "",
          "Headline block (covariance; diagonal sqrt = per-run sd from the deltas; off-diagonal as correlation in brackets):", "",
          "| | " + " | ".join(blk) + " |", "|---|" + "---|" * len(blk)]
    for a in blk:
        cells = []
        for b in blk:
            v = float(sc.loc[a, b])
            if a == b:
                cells.append(f"{_f(v)} (sd {_f(math.sqrt(v))})")
            else:
                den = math.sqrt(float(sc.loc[a, a]) * float(sc.loc[b, b]))
                cells.append(f"{_f(v)} ({_f(v / den, 2) if den > 0 else 'n/a'})")
        L.append(f"| {a} | " + " | ".join(cells) + " |")
    L += [""]
    # 4 thread check
    L += ["## 4. Thread check (Threads 8 / 1 vs the Threads-4 anchor n0_E:29; Seed 0)", "",
          "| key | threads | overall md5 vs anchor | bit-identical | candidates differing | divergent RUC days | first divergent day | median rel day change | host | Gurobi | echo |",
          "|---|---|---|---|---|---|---|---|---|---|---|"]
    for t in S["threads"]:
        cd = t["conditions"]
        L.append(f"| {t['key']} | {t['threads']} | `{t['overall_md5'][:8]}` vs `{t['anchor_md5'][:8]}` | "
                 f"{'**yes**' if t['bit_identical'] else '**no**'} | {t['n_candidates_differing']} | {t['n_divergent_days']} | "
                 f"{t['first_divergent_day_no'] if t['first_divergent_day_no'] is not None else 'none'} | {_f(t['median_rel_all_days'])} | "
                 f"{cd.get('host', '—')} | {cd.get('gurobi', '—')} | {cd.get('ruc_solver_options', '—')} |")
    allid = all(t["bit_identical"] for t in S["threads"])
    L += ["", ("**Threads 8 and Threads 1 reproduce the Threads-4 run bit-for-bit.** The determinism statement extends to "
               "Threads ∈ {1, 4, 8} on this node class." if allid else
               "**The Threads-8 / Threads-1 runs are NOT bit-identical to the Threads-4 anchor** (every RUC day from day 1 "
               "can differ). Caveat: the anchor ran in the n0_E wave on a node that was not recorded, while both thread rows "
               f"ran on {', '.join(sorted({t['conditions'].get('host', '?') for t in S['threads']}))}; the thread count and "
               "the node class are therefore confounded in this check. Either way, bit-identity is established only at "
               "fixed Threads on a fixed platform class (the noise_v3 conditions, `ERCOT_NOISE.md` §12); a thread or node "
               "change acts like a Seed change (Δ in σ̂_c units below)."), ""]
    if not allid:
        L += ["| key | " + " | ".join(HEAD) + " |", "|---|" + "---|" * len(HEAD)]
        for t in S["threads"]:
            L.append(f"| {t['key']} | " + " | ".join(
                f"{_f(t['delta'].get(c, 0.0))} ({_f(abs(t['delta'].get(c, 0.0)) / cs[c]['sigma_c'], 2) if cs[c]['sigma_c'] > 0 else 'n/a'} σ̂_c)"
                for c in HEAD) + " |")
        L += ["", "Cells: Δ vs the anchor (and |Δ| in units of the per-run σ̂_c).", ""]
    sd = S["seed_days"]
    L += ["Seed rows vs their Seed-0 anchor, day level: "
          f"{int(sd['n_divergent'].min())}–{int(sd['n_divergent'].max())} of {int(sd['n_days'].max())} RUC days divergent; "
          f"first divergent day {int(sd['first_divergent_day_no'].min())}–{int(sd['first_divergent_day_no'].max())}; median relative "
          f"day change {_f(sd['median_rel_all_days'].min())}–{_f(sd['median_rel_all_days'].max())}; overall md5 equal to the anchor on "
          f"{int(sd['md5_equal_anchor'].sum())} of {len(sd)}.", ""]
    # 5 tau_res
    tr = S["tau_res"]
    L += ["## 5. τ_res (REPORT-ONLY; PROVISIONAL)", "",
          "E-D7 (nav = the first 32 or all 48 Sobol rows) is not recorded, so the nav-start set is not defined without "
          "reading n0_E rows beyond the 4 anchors. τ_res is therefore computed on the 4 anchor designs' Y only and labelled "
          f"PROVISIONAL. Recipe: `tau_E.tau_res` (the tau_joint code path; N = {tr['n_draws']}, default_rng({tr['seed']})), "
          f"Σ_c = the V1/E1/R4/N1 block of section 3, ref = the frozen plan 6.3 R ({tr['ref_source']}).", "",
          "| quantity | value |", "|---|---|",
          f"| τ_exact (frozen rule) | {_f(tr['tau_exact'])} |",
          f"| HV_0 of the 4 anchors | {_f(tr['hv0'])} |",
          f"| **τ_res (Seed Σ_c), PROVISIONAL** | **{_f(tr['tau_res'])}** |",
          f"| τ_res / HV_0 | {_f(tr['tau_res_over_hv0'])} |",
          f"| τ_res with the 63 A5 perturbed PROVISIONAL Σ_c (same 4 starts) | {_f(tr.get('tau_res_with_perturbed_provisional_sigma_c', np.nan))} |",
          f"| anchors strictly below R | {tr['n_starts_on_front_below_ref']} of 4 |",
          "", "τ_exact = 0 stays the rule (plan 3 / 6.2; frozen). τ_res is printed beside it and decides nothing. The value at the "
          "real nav starts is 55 Part B's column (Σ_c from this file).", ""]
    # 6 54 input
    L += ["## 6. Input to prompt 54 (measured-floor candidate; §10-amended arm input, not a new arm)", "",
          "54's arm rule \"floor = measured iff sd > 0 and df ≥ 3\" becomes live: σ̂_c,j below, df 16. The 54 cross-check "
          "(63 A6 pointer) compares the inferred GP noise sd against σ̂_c,j, not against the exact sd 0.", "",
          "| id | σ̂_c,j (per run) | df | 95 % CI | measured arm live (sd > 0, df ≥ 3) |", "|---|---|---|---|---|"]
    for c in HEAD:
        p = cs[c]
        L.append(f"| {c} | {_f(p['sigma_c'])} | {p['df']} | [{_f(p['sigma_c_ci95'][0])}, {_f(p['sigma_c_ci95'][1])}] | "
                 f"{'yes' if p['sigma_c'] > 0 and p['df'] >= 3 else 'no'} |")
    L += ["", "## 7. Deviations and limits", "",
          "- The 4 deltas of one design share their Seed-0 value; Σ_c and max |Δ_seed| treat the 16 as pairs. σ̂_c (section 1) is "
          "the within-design sd and does not have this dependence.",
          "- n = 4 designs, all inside the BO box (T 797–1,463 MW); the trigger has df 4 / 4 and is an order-of-magnitude detector.",
          "- τ_res is PROVISIONAL on 4 anchor starts (E-D7 not recorded); `landing_R.json` was loaded for its `R` key only.",
          "- The anchors ran in the n0_E wave (other nodes / dates); host and Gurobi version of the anchor runs are not recorded "
          "(n0_E predates the conditions lines). The Seed rows' conditions are in section 0.",
          "- Outputs: `NOISE_SEED_E.md`, `ercot_noise_seed.json`, `ercot_noise_seed.csv` (per candidate), "
          "`ercot_noise_seed_runs.csv`, `ercot_noise_seed_sigma_c.csv`, `fig_seed_chatter_sd.png`, `fig_seed_a3_ratio.png`.", ""]
    return "\n".join(L)


def run(extr=po.EXTR, waves=po.WAVES, out_dir=HERE, noise_json=os.path.join(HERE, "ercot_noise.json"), figs=True):
    defs = po.load_defs()
    ids = list(po.CAND_IDS)
    dm, rows, anchors = load(extr, waves, defs)
    with open(noise_json) as f:
        nj = json.load(f)
    assert nj.get("structural_zero", {}).get("keys_excluded"), "ercot_noise.json must be the 63 A1 version (D2 excluded)"
    D = designs(dm, rows, anchors)
    runs = [rows[i] for i in sorted(rows)] + [anchors[a] for a, _, _, _ in D]
    sus = [r["key"] for r in runs if r["suspect"]]
    assert not sus, f"SUSPECT runs present — the pre-registered reads exclude them; handle before reading: {sus}"
    for r in runs:
        idn = r["identity"] or {}
        assert idn.get("ruc_mipgap") == 0.001 and idn.get("ruc_time_limit") == 1200.0, (r["key"], idn)
    cs = candidate_stats(D, ids, nj)
    Sc, sci = sigma_c_matrix(D, ids)
    t4 = [r["core_h"] for r in rows.values() if r["ruc_threads"] == 4 and np.isfinite(r["core_h"])]
    S = {"defs": defs, "ids": ids, "designs": D, "cand": cs, "runs": runs, "sigma_c": Sc, "sigma_c_info": sci,
         "threads": thread_check(rows, anchors, ids, extr), "seed_days": seed_day_divergence(D, extr),
         "tau_res": tau_res_provisional(D, Sc, os.path.join(waves, "n0_E", "landing_R.json"),
                                        pert_sigma_csv=os.path.join(HERE, "ercot_noise_sigma_c_provisional.csv")),
         "runtime": {"total": float(np.nansum([r["core_h"] for r in rows.values()])), "median_t4": float(np.median(t4)),
                     "min_t4": float(np.min(t4)), "max_t4": float(np.max(t4)),
                     "t8": float(next(r["core_h"] for r in rows.values() if r["ruc_threads"] == 8)),
                     "t1": float(next(r["core_h"] for r in rows.values() if r["ruc_threads"] == 1))}}
    os.makedirs(out_dir, exist_ok=True)
    df = to_frame(cs, D, defs, ids)
    df.to_csv(os.path.join(out_dir, "ercot_noise_seed.csv"), index=False)
    Sc.to_csv(os.path.join(out_dir, "ercot_noise_seed_sigma_c.csv"))
    rcols = ["key", "level_id", "anchor", "seed", "ruc_threads", "overall_md5", "suspect", "max_solve_s", "n_days_gt_600s",
             "n_ruc", "n_optimal", "n_ruc_time_limit", "wall_s", "core_h"]
    pd.DataFrame([{k: r.get(k) for k in rcols} for r in runs]).to_csv(os.path.join(out_dir, "ercot_noise_seed_runs.csv"), index=False)
    if figs:
        S["figures"] = [os.path.relpath(p, ERCOT) for p in figures(cs, D, defs, out_dir, df)]
    md = fmt_md(S)
    with open(os.path.join(out_dir, "NOISE_SEED_E.md"), "w") as f:
        f.write(md + "\n")
    js = {"prompt": "63 v1 Part C", "wave": WAVE, "anchors": [a for a, _, _, _ in D],
          "designs": [{"anchor": a, "label": lab, "T": t, "keys": [r["key"] for r in recs]} for a, lab, t, recs in D],
          "per_candidate": cs, "sigma_c": {"ids": list(Sc.index), "matrix": Sc.to_numpy().tolist(), "info": sci,
                                           "file": "ercot_noise_seed_sigma_c.csv"},
          "A3": {"rule": "AGREE iff 1/2 <= sigma_c*sqrt2 / sigma_hat_pert <= 2 (two-run scales; perturbed D2 excluded)",
                 "per_candidate": {c: cs[c]["A3"] for c in ids},
                 "agree_gradable": [c for c in defs["global_order"][:22] if cs[c]["A3"].startswith("AGREE")],
                 "disagree_gradable": [c for c in defs["global_order"][:22] if cs[c]["A3"].startswith("DISAGREE")],
                 "perturbed_ruler_label_if_disagree": PERTURBED_LABEL},
          "bars": {c: {"B_seed": cs[c]["B_seed"], "B_pert": cs[c]["B_pert"]} for c in ids},
          "thread_check": S["threads"], "seed_day_divergence": S["seed_days"].to_dict(orient="records"),
          "tau_res": S["tau_res"], "runtime_core_h": S["runtime"],
          "floor_candidate_54": {c: {"sigma_c": cs[c]["sigma_c"], "df": cs[c]["df"]} for c in ids},
          "runs": [{k: r.get(k) for k in rcols + ["conditions"]} for r in runs],
          "generated_utc": pd.Timestamp.now(tz="UTC").strftime("%Y-%m-%dT%H:%M:%SZ"), "git_head": po.git_head()}
    with open(os.path.join(out_dir, "ercot_noise_seed.json"), "w") as f:
        json.dump(po._json_safe(js), f, indent=1, default=str)
        f.write("\n")
    return S, df, md


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out-dir", default=HERE)
    ap.add_argument("--no-figs", action="store_true")
    a = ap.parse_args(argv)
    S, df, md = run(out_dir=a.out_dir, figs=not a.no_figs)
    cs = S["cand"]
    print("id  sigma_c(df16)  sigma_c*sqrt2  sigma_pert  ratio  A3  B_seed  B_pert")
    for c in HEAD:
        p = cs[c]
        print(f"{c:3s} {p['sigma_c']:.6g} {p['sigma_c'] * math.sqrt(2):.6g} {p['sigma_hat_pert']:.6g} "
              f"{p['ratio_seed_over_pert']:.3g} {p['A3']} {p['B_seed']:.6g} {p['B_pert']:.6g}")
    for t in S["threads"]:
        print(f"thread {t['threads']}: bit-identical {t['bit_identical']} ({t['n_candidates_differing']} ids differ, "
              f"{t['n_divergent_days']} divergent days)")
    tr = S["tau_res"]
    print(f"tau_res PROVISIONAL {tr['tau_res']:.6g} (hv0 {tr['hv0']:.6g}; ratio {tr['tau_res_over_hv0']}); "
          f"with perturbed Sigma_c {tr.get('tau_res_with_perturbed_provisional_sigma_c')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
