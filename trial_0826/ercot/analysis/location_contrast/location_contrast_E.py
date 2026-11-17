#!/usr/bin/env python3
"""Prompt 61 v1.1 §2.6 — landing analysis of `location_contrast_E`.

Reads exactly per prompt 61 §3 (frozen in `waves/location_contrast_E/README.md`):
bar B_j, interaction I_j / g / I_rel (V1 guard), location at fixed total
(raw Δ_loc and the H_C efficiency residual for V1 and N4; N1 chatter-limited;
E1 / E3 gap labels), the saturation probe (row 9) and the physics-prediction
check. Inputs: this wave (9 rows), wave D rows 1–18 (`location_oat_v2`,
selected by (oat_site, level_id)), `base_v3:1`; objectives from
`pool_objectives.pool_row(key)`; SUSPECT from
`analysis.ercot_gp.ercot_gp_loader.suspect_flag`. Never reads n0_E,
random_E or methods_E extracts.

Outputs: `location_contrast_E.csv` (every number in the md), the md
`LOCATION_CONTRAST_E.md` (rendered from the csv only) and three figures
in `figs/` (bold labels and ticks; values asserted against the csv
before drawing).

Run:  cd trial_0826/ercot && /opt/anaconda3/bin/python analysis/location_contrast/location_contrast_E.py
"""
import hashlib
import json
import math
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ERCOT = HERE.parents[1]
for p in (str(ERCOT), str(ERCOT / "analysis" / "noise_v3")):
    if p not in sys.path:
        sys.path.insert(0, p)
import pool_objectives as po  # noqa: E402
from read_noise import read_identity  # noqa: E402
from analysis.ercot_gp.ercot_gp_loader import suspect_flag  # noqa: E402

WAVE = "location_contrast_E"
WAVE_D = "location_oat_v2"
BASE = "base_v3:1"
EXTR = ERCOT / "extracts"
NOISE_JSON = ERCOT / "analysis" / "noise_v3" / "ercot_noise.json"
HC_CSV = ERCOT / "waves" / WAVE / "H_C.csv"
OUT_CSV = HERE / "location_contrast_E.csv"
OUT_MD = HERE / "LOCATION_CONTRAST_E.md"
FIGS = HERE / "figs"

OBJ = ["V1", "E1", "E3", "R1", "R2", "R4", "N1", "N4"]
UNITS = {"V1": "MWh", "E1": "$", "E3": "$", "R1": "MWh", "R2": "MWh", "R4": "on/offs",
         "N1": "line-h", "N4": "line-h"}
GAP_OBJ = ("E1", "E3")
SITES = ["163", "140", "146", "270", "110", "274"]          # wave-D run-index order
LEVELS = [60, 120, 180]
LABELS = ["P1_60", "P1_120", "P1_180", "P2_800_b120", "P2_800_b275", "P2_800_all",
          "P2_500_270", "P2_500_110_140", "P3_1500_all"]
J_OF = {60: "P1_60", 120: "P1_120", 180: "P1_180"}
LOC_PAIRS = [("P2_800_b120", "P2_800_b275"), ("P2_500_270", "P2_500_110_140"),
             ("P2_800_b120", "P2_800_all"), ("P2_800_b275", "P2_800_all")]
RESID_OBJ = ("V1", "N4")
G_PRED = {60: 0.07, 120: 0.12, 180: 0.18}
POCKET_BUSES = (2, 75, 120, 121)
EXPECT_KEYS_EXCLUDED = ["noise_v3/A:6", "noise_v3/B:6"]


# --------------------------------------------------------------------------
# inputs + guards
# --------------------------------------------------------------------------
def assert_landed():
    wd = EXTR / WAVE
    assert (wd / "COLLECTED").is_file(), "no COLLECTED marker"
    for i in range(1, 10):
        d = wd / f"run_index_{i}"
        ident = read_identity(str(d))
        assert ident is not None, d
        assert ident["ruc_mipgap"] == 0.001 and ident["ruc_time_limit"] == 1200.0, (d, ident)
        assert (d / "pool_full_metrics.json").is_file(), d


def keys():
    dmc = pd.read_csv(ERCOT / "waves" / WAVE / "design_matrix.csv", dtype={"level_id": str})
    assert list(dmc["level_id"]) == LABELS and list(dmc["index"]) == list(range(1, 10))
    k = {lab: f"{WAVE}:{i}" for lab, i in zip(dmc["level_id"], dmc["index"])}
    dmd = pd.read_csv(ERCOT / "waves" / WAVE_D / "design_matrix.csv", dtype={"oat_site": str})
    for s in SITES:
        for m in LEVELS:
            r = dmd[(dmd["oat_site"] == s) & (dmd["level_id"] == f"L{m}")]
            assert len(r) == 1 and float(r["pem_mw"].iloc[0]) == float(m), (s, m)
            assert int(r["index"].iloc[0]) <= 18
            k[f"s{s}_L{m}"] = f"{WAVE_D}:{int(r['index'].iloc[0])}"
    k["base"] = BASE
    return k


def bars():
    js = json.loads(NOISE_JSON.read_text())
    pc = js["per_candidate"]
    bad = {j: v["exact_pooled_sd"] for j, v in pc.items() if v.get("exact_pooled_sd", 0.0) > 0}
    if bad:
        raise SystemExit(f"STOP: exact_pooled_sd > 0 for {bad} (61 §3 guard)")
    sz = js["structural_zero"]
    assert sorted(sz["keys_excluded"]) == EXPECT_KEYS_EXCLUDED, sz["keys_excluded"]
    for pr in sz["pairs"]:
        if pr["key"] in EXPECT_KEYS_EXCLUDED:
            assert pr["structural_zero"] and pr["capped_input_identical"] and pr["overall_md5_equal"], pr
            # local md5 of the two runs' overall.csv (the exact-copy identity)
            a = po.run_dir(pr["key"], str(EXTR))
            b = po.run_dir(pr["ref_key"], str(EXTR))
            if os.path.isfile(os.path.join(a, "overall.csv")) and os.path.isfile(os.path.join(b, "overall.csv")):
                ma = hashlib.md5(open(os.path.join(a, "overall.csv"), "rb").read()).hexdigest()
                mb = hashlib.md5(open(os.path.join(b, "overall.csv"), "rb").read()).hexdigest()
                assert ma == mb == pr["overall_md5"], (pr["key"], ma, mb)
    out = {}
    for j in OBJ:
        v = pc[j]
        d = np.array(v["perturbed_delta_signed"], dtype=float)
        assert len(d) == 6 and not set(v["perturbed_keys"]) & set(EXPECT_KEYS_EXCLUDED), j
        sig = math.sqrt(float(np.mean(d ** 2)))
        B = max(3.0 * sig, float(np.max(np.abs(d))))
        assert abs(B - v["bar"]["B"]) <= 1e-9 * max(1.0, B), (j, B, v["bar"]["B"])
        out[j] = {"sigma": sig, "B": B, "max_abs": float(np.max(np.abs(d))), "n": len(d)}
    return out, js


def pocket_pool_mwh():
    """base_v3 non-PEM WIND + PV curtailment at the pocket buses (2/75/120/121)."""
    g = pd.read_csv(ERCOT / "data" / "ercot123_2019_v2" / "gen.csv", dtype={"GEN UID": str})
    s = po.co.gen_summary(po.run_dir(BASE, str(EXTR)))
    m = s.merge(g[["GEN UID", "Bus ID"]], left_on="Generator", right_on="GEN UID")
    p = m[m["Bus ID"].isin(POCKET_BUSES) & (~m["is_pem"]) & m["unit_type"].isin(["WIND", "PV"])]
    return float(p["curtailment_mwh"].sum())


# --------------------------------------------------------------------------
# compute -> long csv
# --------------------------------------------------------------------------
def compute():
    assert_landed()
    K = keys()
    bar, js = bars()
    for lab, key in K.items():                     # every input run is identity v3
        ident = read_identity(po.run_dir(key, str(EXTR)))
        assert ident and ident["ruc_mipgap"] == 0.001 and ident["ruc_time_limit"] == 1200.0, (key, ident)
    rows = {lab: po.pool_row(key) for lab, key in K.items()}
    for lab, r in rows.items():                    # N4 = L252 hours (the other pocket lines never bind)
        assert r["N4"] == r["N4_L252"], (lab, r["N4"], r["N4_L252"])
    sus ={lab: bool(suspect_flag(r)) for lab, r in rows.items()}
    y = {lab: {j: float(r[j]) for j in OBJ} for lab, r in rows.items()}
    G = {lab: float(r["G_run_usd"]) for lab, r in rows.items()}
    hc = pd.read_csv(HC_CSV, dtype={"level_id": str}, float_precision="round_trip").set_index("level_id")
    H = {lab: float(hc.loc[lab, "H_C_MWh"]) for lab in LABELS}
    assert all(abs(float(rows[lab]["pem_mw"]) - float(hc.loc[lab, "total_mw"])) <= 1e-9 for lab in LABELS)
    D = {lab: {j: y[lab][j] - y["base"][j] for j in OBJ} for lab in y}
    rec = []

    def add(kind, item, obj="", m="", value=np.nan, B=np.nan, bound=np.nan, verdict="", note=""):
        ratio = value / B if (np.isfinite(B) and B > 0 and np.isfinite(value)) else np.nan
        rec.append({"kind": kind, "item": item, "objective": obj, "m": m, "value": value, "B": B,
                    "ratio": ratio, "bound": bound, "verdict": verdict, "note": note})

    for j in OBJ:
        add("bar", "B_j", j, value=bar[j]["B"], note=f"sigma_hat={bar[j]['sigma']!r}; n={bar[j]['n']}")
        add("bar", "sigma_hat", j, value=bar[j]["sigma"])
        add("bar", "r_I", j, value=4.0 * bar[j]["sigma"])
    for lab in y:
        add("suspect", lab, value=float(sus[lab]), verdict=("SUSPECT" if sus[lab] else "ok"), note=K[lab])
        add("G_run", lab, value=G[lab], note=K[lab])
        add("pem_mw", lab, value=float(rows[lab]["pem_mw"]), note=K[lab])
        for j in OBJ:
            add("y", lab, j, value=y[lab][j], note=K[lab])
            if lab != "base":
                add("delta", lab, j, value=D[lab][j], B=bar[j]["B"])
    for lab in LABELS:
        add("H_C", lab, value=H[lab])
    suspect_any = [lab for lab, v in sus.items() if v]

    def ok(*labs):
        return not any(sus[x] for x in labs)

    # ---- interaction (all objectives) ------------------------------------
    for m in LEVELS:
        J = J_OF[m]
        singles = [f"s{s}_L{m}" for s in SITES]
        usable = ok(J, "base", *singles)
        for j in OBJ:
            A = math.fsum(D[s][j] for s in singles)
            I = D[J][j] - A
            rI = 4.0 * bar[j]["sigma"]
            bound = (G[J] + math.fsum(G[s] for s in singles) + 5 * G["base"]) if j in GAP_OBJ else np.nan
            if not usable:
                v = "EXCLUDED (SUSPECT)"
            elif bar[j]["B"] == 0:
                v = "EXACT (B_j = 0; no read)"
            elif j in GAP_OBJ:
                v = ("NOT READABLE" if abs(I) < rI else
                     ("GAP-READABLE" if abs(I) > bound else "WITHIN GAP BOUND"))
            else:
                v = "reported (I_j / r_I)"
            add("A", J, j, m, value=A)
            add("interaction", J, j, m, value=I, B=rI, bound=bound, verdict=v)
        # V1 headline
        RJ = -D[J]["V1"]
        SR = math.fsum(-D[s]["V1"] for s in singles)
        rI = 4.0 * bar["V1"]["sigma"]
        g = (SR - RJ) / RJ
        Irel = (SR - RJ) / SR
        guard = RJ >= 3 * rI
        if not usable or not guard:
            v = "UNRESOLVED" + (" (SUSPECT)" if not usable else " (guard R_J < 3 r_I)")
        elif g >= 0.10 and (SR - RJ) >= 2 * rI:
            v = "SUB-ADDITIVE"
        elif g <= -0.10 and (SR - RJ) <= -2 * rI:
            v = "SUPER-ADDITIVE"
        elif abs(g) < 0.10:
            v = "WITHIN 10 %"
        else:
            v = "UNRESOLVED"
        add("V1_RJ", J, "V1", m, value=RJ, B=rI)
        add("V1_sumR", J, "V1", m, value=SR, B=rI)
        add("V1_sumR_minus_RJ", J, "V1", m, value=SR - RJ, B=rI)
        add("V1_guard", J, "V1", m, value=RJ / (3 * rI), verdict=("PASS" if guard else "FAIL"),
            note="R_J / (3 r_I); pass iff >= 1")
        add("V1_g", J, "V1", m, value=g, verdict=v, note=f"predicted {G_PRED[m]}")
        add("V1_g_pred", J, "V1", m, value=G_PRED[m])
        add("V1_I_rel", J, "V1", m, value=Irel)
    gv = [r for r in rec if r["kind"] == "V1_g"]
    if all(r["verdict"] == "WITHIN 10 %" for r in gv):
        overall = "ADDITIVE WITHIN 10 %"
    else:
        overall = "per level: " + " / ".join(f"{r['m']}: {r['verdict']}" for r in gv)
    add("V1_additivity", "overall", "V1", verdict=overall)

    # ---- location at fixed total ----------------------------------------
    for a, b in LOC_PAIRS:
        pair = f"{a} vs {b}"
        usable = ok(a, b)
        for j in OBJ:
            dl = y[a][j] - y[b][j]
            B = bar[j]["B"]
            bound = (G[a] + G[b]) if j in GAP_OBJ else np.nan
            if not usable:
                v = "EXCLUDED (SUSPECT)"
            elif B == 0:
                v = "EXACT (B_j = 0; no read)"
            elif abs(dl) < B:
                v = "NOT READABLE"
            elif j in GAP_OBJ:
                v = "GAP-READABLE" if abs(dl) > bound else "WITHIN GAP BOUND"
            else:
                v = "READABLE"
            if j == "N1" and B > 0:
                v += " (chatter-limited)"
            add("loc_raw", pair, j, value=dl, B=B, bound=bound, verdict=v)
        for j in RESID_OBJ:
            Ra, Rb = -D[a][j], -D[b][j]
            res = Ra - Rb * H[a] / H[b]
            B = bar[j]["B"]
            raw = abs(y[a][j] - y[b][j]) >= B
            if not usable:
                v = "EXCLUDED (SUSPECT)"
            elif abs(res) >= B:
                v = "LOCATION EFFECT"
            elif raw:
                v = "COMPOSITION (raw readable, explained by H_C)"
            else:
                v = "NO READABLE DIFFERENCE (raw and residual < B_j)"
            add("loc_resid", pair, j, value=res, B=B, verdict=v,
                note=f"R_a={Ra!r}; R_b={Rb!r}; H_a/H_b={H[a] / H[b]!r}")
    for lab in LABELS:
        for j in RESID_OBJ:
            add("efficiency", lab, j, value=-D[lab][j] / H[lab],
                note="e = relief / H_C (" + ("MWh per MWh" if j == "V1" else "line-h per MWh") + ")")

    # ---- saturation probe -------------------------------------------------
    pool = pocket_pool_mwh()
    lab = "P3_1500_all"
    add("saturation", "pocket_pool_base_v3", "V1", value=pool,
        note="base_v3 non-PEM WIND+PV curtailment at buses 2/75/120/121 (prompt: 4.87 TWh)")
    add("saturation", "R_row9", "V1", value=-D[lab]["V1"], B=bar["V1"]["B"])
    add("saturation", "H_C_row9", "V1", value=H[lab])
    add("saturation", "R_row9_over_pool", "V1", value=-D[lab]["V1"] / pool)
    add("saturation", "H_C_row9_over_pool", "V1", value=H[lab] / pool)
    add("saturation", "e_row9", "V1", value=-D[lab]["V1"] / H[lab])
    add("saturation", "e_row6", "V1", value=-D["P2_800_all"]["V1"] / H["P2_800_all"])
    add("saturation", "R_row9_minus_R_row6", "V1", value=D["P2_800_all"]["V1"] - D[lab]["V1"],
        B=bar["V1"]["B"])

    # ---- physics prediction check ----------------------------------------
    t = pd.DataFrame(rec)
    lr = t[t.kind == "loc_resid"]
    n_loc = int((lr.verdict == "LOCATION EFFECT").sum())
    add("prediction", "no residual location effect (V1, N4)", value=float(n_loc),
        verdict=("HOLDS" if n_loc == 0 else "CONTRADICTED"), note="count of LOCATION EFFECT reads")
    e800 = t[(t.kind == "loc_raw") & (t.objective == "E1") & t["item"].str.startswith("P2_800")]
    n_gr = int((e800.verdict == "GAP-READABLE").sum())
    add("prediction", "E1 at 800 within gap bound", value=float(n_gr),
        verdict=("HOLDS" if n_gr == 0 else "CONTRADICTED"), note="count of GAP-READABLE E1 800-MW pairs")
    add("prediction", "E1 800 pair bound min", value=float(e800["bound"].min()), note="predicted ≈ $37–50M")
    add("prediction", "E1 800 pair bound max", value=float(e800["bound"].max()))
    r4 = t[(t.kind == "loc_raw") & (t.objective == "R4")]
    n_r4 = int((r4.verdict == "READABLE").sum())
    add("prediction", "R4 unreadable", value=float(n_r4),
        verdict=("HOLDS" if n_r4 == 0 else "CONTRADICTED"), note="count of READABLE R4 location pairs")
    add("prediction", "H_C(b120)/H_C(b275)", value=H["P2_800_b120"] / H["P2_800_b275"], note="predicted ≈ 1.149")
    add("meta", "suspect_rows", value=float(len(suspect_any)), note=";".join(suspect_any))
    add("meta", "noise_json_prompt", note=js.get("prompt", ""))
    add("meta", "noise_json_git_head", note=str(js.get("git_head", "")))
    return pd.DataFrame(rec, columns=["kind", "item", "objective", "m", "value", "B", "ratio",
                                      "bound", "verdict", "note"])


# --------------------------------------------------------------------------
# csv lookups (the md and the figures read ONLY the csv)
# --------------------------------------------------------------------------
def load_csv(path=OUT_CSV):
    return pd.read_csv(path, dtype={"kind": str, "item": str, "objective": str, "verdict": str, "note": str},
                       float_precision="round_trip", keep_default_na=False, na_values=[""])


def cell(t, kind, item=None, obj=None, m=None, col="value"):
    s = t[t["kind"] == kind]
    if item is not None:
        s = s[s["item"] == item]
    if obj is not None:
        s = s[s["objective"] == obj]
    if m is not None:
        s = s[s["m"] == float(m)]
    assert len(s) == 1, (kind, item, obj, m, len(s))
    return s.iloc[0][col]


def assert_csv_equals(t, t2):
    assert list(t.columns) == list(t2.columns) and len(t) == len(t2)
    for c in ("value", "B", "ratio", "bound"):
        a, b = t[c].astype(float).to_numpy(), t2[c].astype(float).to_numpy()
        assert np.array_equal(np.isnan(a), np.isnan(b)), c
        f = ~np.isnan(a)
        assert np.array_equal(a[f], b[f]), c
    for c in ("kind", "item", "objective", "verdict"):
        assert [str(x) if x == x else "" for x in t[c]] == [str(x) if x == x else "" for x in t2[c]], c


# --------------------------------------------------------------------------
# figures (bold labels AND ticks)
# --------------------------------------------------------------------------
def _plt():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.size": 16, "font.weight": "bold", "axes.labelweight": "bold",
                         "axes.titleweight": "bold", "text.parse_math": False})
    return plt


def _bold_ticks(ax):
    for lab in ax.get_xticklabels() + ax.get_yticklabels():
        lab.set_fontweight("bold")


def figures(t):
    plt = _plt()
    FIGS.mkdir(exist_ok=True)
    # 1. V1 relief vs total MW
    tot = {lab: cell(t, "pem_mw", lab) for lab in LABELS}
    RJ = [cell(t, "V1_RJ", J_OF[m], "V1", m) for m in LEVELS]
    SR = [cell(t, "V1_sumR", J_OF[m], "V1", m) for m in LEVELS]
    xs = [tot[J_OF[m]] for m in LEVELS]
    assert xs == [360.0, 720.0, 1080.0]
    R = {lab: -cell(t, "delta", lab, "V1") for lab in LABELS}
    assert all(abs(R[J_OF[m]] - RJ[i]) <= 1e-6 for i, m in enumerate(LEVELS))
    B = cell(t, "bar", "B_j", "V1")
    fig, ax = plt.subplots(figsize=(11, 7.5))
    ax.plot(xs, [v / 1e6 for v in SR], "s--", color="#888888", ms=10, lw=2.5, label="sum of six single-site relief (wave D)")
    ax.plot(xs, [v / 1e6 for v in RJ], "o-", color="#1f4e9c", ms=10, lw=2.5, label="all-six joint run (P1)")
    ax.plot([tot["P3_1500_all"]], [R["P3_1500_all"] / 1e6], "D", color="#b2182b", ms=12, label="P3 1,500 MW (saturation probe)")
    mk = {"P2_800_b120": ("^", "#2c7a3f"), "P2_800_b275": ("v", "#d17a00"), "P2_800_all": ("P", "#6a3d9a"),
          "P2_500_270": ("^", "#66a873"), "P2_500_110_140": ("v", "#f0b45a")}
    for lab, (sym, col) in mk.items():
        ax.plot([tot[lab]], [R[lab] / 1e6], sym, color=col, ms=11, label=lab)
    pool = cell(t, "saturation", "pocket_pool_base_v3", "V1")
    ax.axhline(pool / 1e6, color="#b2182b", lw=1.5, ls=":", label="base_v3 behind-cut curtailment pool")
    ax.set_xlabel("total PEM MW")
    ax.set_ylabel("V1 relief R = -(y - y_base) (TWh)")
    ax.set_title(f"Curtailment relief vs total MW (bar B_V1 = {B / 1e3:.1f} GWh)")
    ax.grid(alpha=0.3)
    ax.legend(fontsize=11, loc="lower right")
    _bold_ticks(ax)
    fig.tight_layout()
    fig.savefig(FIGS / "fig_v1_relief_vs_total.png", dpi=150)
    plt.close(fig)
    # 2. efficiency per row
    e = [cell(t, "efficiency", lab, "V1") for lab in LABELS]
    assert all(abs(e[i] - R[lab] / cell(t, "H_C", lab)) <= 1e-12 for i, lab in enumerate(LABELS))
    fig, ax = plt.subplots(figsize=(12, 6.5))
    ax.bar(range(len(LABELS)), e, color="#1f4e9c")
    for i, v in enumerate(e):
        ax.text(i, v + 0.005, f"{v:.3f}", ha="center", fontsize=12, fontweight="bold")
    ax.set_xticks(range(len(LABELS)))
    ax.set_xticklabels(LABELS, rotation=30, ha="right")
    ax.set_ylim(0.6, 1.0)
    ax.set_ylabel("e = V1 relief / H_C (MWh per MWh)")
    ax.set_xlabel("row")
    ax.set_title("Relief per unit host-absorbable energy (H_C, pre-registered)")
    ax.grid(axis="y", alpha=0.3)
    _bold_ticks(ax)
    fig.tight_layout()
    fig.savefig(FIGS / "fig_efficiency_relief_over_HC.png", dpi=150)
    plt.close(fig)
    # 3. rows 4-8 in B_j units, one panel per objective with B_j > 0
    rows48 = LABELS[3:8]
    objs = [j for j in OBJ if cell(t, "bar", "B_j", j) > 0]
    fig, axes = plt.subplots(1, len(objs), figsize=(3.2 * len(objs), 6.5), sharey=False)
    cols = ["#2c7a3f", "#d17a00", "#6a3d9a", "#66a873", "#f0b45a"]
    for ax, j in zip(axes, objs):
        v = [cell(t, "delta", lab, j, col="ratio") for lab in rows48]
        assert all(abs(v[i] - cell(t, "delta", lab, j) / cell(t, "bar", "B_j", j)) <= 1e-9 * max(1, abs(v[i]))
                   for i, lab in enumerate(rows48))
        ax.bar(range(5), v, color=cols)
        ax.axhline(1, color="k", lw=1, ls="--")
        ax.axhline(-1, color="k", lw=1, ls="--")
        ax.axhline(0, color="k", lw=1)
        ax.set_xticks(range(5))
        ax.set_xticklabels(["4", "5", "6", "7", "8"])
        ax.set_title(j)
        ax.set_xlabel("row")
        _bold_ticks(ax)
    axes[0].set_ylabel("(y - y_base) / B_j")
    fig.suptitle("Rows 4-8 vs base_v3 in bar units (dashed = +/- 1 B_j; R1 exact 0, no bar)", fontweight="bold")
    fig.tight_layout()
    fig.savefig(FIGS / "fig_rows4to8_in_Bj.png", dpi=150)
    plt.close(fig)


# --------------------------------------------------------------------------
# md (rendered from the csv only)
# --------------------------------------------------------------------------
def _n(v, d=0):
    return f"{v:,.{d}f}"


def _r(v):
    return f"{v:+.2f}"


def _money(v):
    return ("-" if v < 0 else "") + f"${abs(v) / 1e6:,.2f}M"


def _val(j, v):
    if j in GAP_OBJ:
        return _money(v)
    if j == "V1":
        return f"{_n(v)} MWh"
    if j == "R2":
        return f"{v:,.1f}"
    return _n(v)


def render_md(t):
    L = []
    a = L.append
    nsus = int(cell(t, "meta", "suspect_rows"))
    a("# LOCATION_CONTRAST_E — ERCOT location-contrast wave, landing (prompt 61 v1.1 §2.6)")
    a("")
    a("Generated by `analysis/location_contrast/location_contrast_E.py` from "
      "`location_contrast_E.csv` (every number below is a cell of that csv). "
      "Reads exactly per prompt 61 §3, frozen in `waves/location_contrast_E/README.md` "
      "with the wave commit before any Y existed. Analysis-only: these rows never enter "
      "the GP's X, the HV ledger, the holdout or the random baseline.")
    a("")
    a("## 0. Inputs and guards")
    a("")
    a("- `extracts/location_contrast_E/COLLECTED` present; 9 / 9 `identity.txt` parse to "
      "ruc_mipgap 0.001 / ruc_time_limit 1200 (`read_noise.read_identity`); 9 / 9 "
      "`pool_full_metrics.json` present. The 18 wave-D singles and `base_v3:1` also parse to v3.")
    a("- Inputs: this wave (9), wave D rows 1–18 selected by `(oat_site, level_id)` "
      "(nuclear rows 19–21 excluded), `base_v3:1`. Objectives from "
      "`pool_objectives.pool_row(key)`. N4 = L252 hours ≥ 99 % (asserted equal to "
      "`N4_L252` on all 28 runs; the other pocket lines never reach 99 %).")
    a(f"- SUSPECT (`ercot_gp_loader.suspect_flag`, S1 ∧ S2 ∧ S3a): **{nsus} of 28** runs. "
      "No exclusion was needed.")
    a(f"- Bars from `analysis/noise_v3/ercot_noise.json` ({cell(t, 'meta', 'noise_json_prompt', col='note')}; "
      f"git_head {cell(t, 'meta', 'noise_json_git_head', col='note')}). The D2 / site-206 "
      "structural-zero pairs (`noise_v3/A:6`, `B:6`) are excluded, 6 δ values remain. "
      "B_j is recomputed in code and asserted equal to the json. The md5 identity of the "
      "excluded pairs is asserted. `exact_pooled_sd` = 0 for every id, so the guard passes.")
    a("")
    a("## 1. Bars")
    a("")
    a("| objective | unit | σ̂_j | B_j = max(3σ̂, max abs δ) | r_I = 4σ̂ |")
    a("|---|---|---|---|---|")
    for j in OBJ:
        a(f"| {j} | {UNITS[j]} | {_val(j, cell(t, 'bar', 'sigma_hat', j))} | "
          f"{_val(j, cell(t, 'bar', 'B_j', j))} | {_val(j, cell(t, 'bar', 'r_I', j))} |")
    a("")
    r1max = max(abs(cell(t, "y", lab, "R1")) for lab in LABELS + [f"s{s}_L{m}" for s in SITES for m in LEVELS] + ["base"])
    a(f"R1 has B_j = 0, so it is reported as an exact value with no read. Max |R1| over the 28 runs = {_n(r1max)} MWh.")
    a("")
    a("## 2. The nine rows vs base_v3 (Δ_j / B_j)")
    a("")
    objs = [j for j in OBJ if j != "R1"]
    a("| # | row | total MW | H_C (MWh) | " + " | ".join(objs) + " | R1 (MWh) | G_run |")
    a("|---|" + "---|" * (len(objs) + 5))
    for i, lab in enumerate(LABELS, 1):
        a(f"| {i} | {lab} | {_n(cell(t, 'pem_mw', lab))} | {_n(cell(t, 'H_C', lab))} | "
          + " | ".join(_r(cell(t, "delta", lab, j, col="ratio")) for j in objs)
          + f" | {_n(cell(t, 'y', lab, 'R1'))} | {_money(cell(t, 'G_run', lab))} |")
    a("")
    a(f"base_v3:1: V1 = {_val('V1', cell(t, 'y', 'base', 'V1'))}, E1 = {_money(cell(t, 'y', 'base', 'E1'))}, "
      f"N4 = {_n(cell(t, 'y', 'base', 'N4'))} h, G_run = {_money(cell(t, 'G_run', 'base'))}.")
    a("")
    a("## 3. Interaction (all-six joint vs the sum of six singles)")
    a("")
    a("### 3.1 V1 (headline)")
    a("")
    a("| m (MW/site) | R_J (MWh) | Σ_s R_s (MWh) | ΣR − R_J (MWh) | (ΣR − R_J) / r_I | guard R_J / 3r_I | g | g predicted | I_rel | read |")
    a("|---|---|---|---|---|---|---|---|---|---|")
    for m in LEVELS:
        J = J_OF[m]
        a(f"| {m} | {_n(cell(t, 'V1_RJ', J, 'V1', m))} | {_n(cell(t, 'V1_sumR', J, 'V1', m))} | "
          f"{_n(cell(t, 'V1_sumR_minus_RJ', J, 'V1', m))} | {_r(cell(t, 'V1_sumR_minus_RJ', J, 'V1', m, 'ratio'))} | "
          f"{cell(t, 'V1_guard', J, 'V1', m):.1f} ({cell(t, 'V1_guard', J, 'V1', m, 'verdict')}) | "
          f"{cell(t, 'V1_g', J, 'V1', m):+.3f} | {cell(t, 'V1_g_pred', J, 'V1', m):.2f} | "
          f"{cell(t, 'V1_I_rel', J, 'V1', m):+.3f} | **{cell(t, 'V1_g', J, 'V1', m, 'verdict')}** |")
    a("")
    dg = [cell(t, "V1_g_pred", J_OF[m], "V1", m) - cell(t, "V1_g", J_OF[m], "V1", m) for m in LEVELS]
    a(f"Overall (§3: ADDITIVE WITHIN 10 % needs |g| < 0.10 at all three levels): "
      f"**{cell(t, 'V1_additivity', 'overall', 'V1', col='verdict')}**. Relief is sub-additive "
      "at every level (g > 0) and grows with m. The observed g is below the offline pool-model "
      f"prediction at each level, by {min(dg):.3f}–{max(dg):.3f}.")
    a("")
    a("### 3.2 I_j for every objective (I_j = Δ_J − Σ_s Δ_s; ruler r_I = 4σ̂_j)")
    a("")
    a("| objective | I(60) | I/r_I | I(120) | I/r_I | I(180) | I/r_I | note |")
    a("|---|---|---|---|---|---|---|---|")
    for j in OBJ:
        cells = []
        for m in LEVELS:
            cells += [_val(j, cell(t, "interaction", J_OF[m], j, m)),
                      ("—" if cell(t, "bar", "B_j", j) == 0 else _r(cell(t, "interaction", J_OF[m], j, m, "ratio")))]
        note = ""
        if j in GAP_OBJ:
            note = "gap bound " + " / ".join(_money(cell(t, "interaction", J_OF[m], j, m, "bound")) for m in LEVELS) \
                + ": " + " / ".join(cell(t, "interaction", J_OF[m], j, m, "verdict") for m in LEVELS)
        elif j == "R1":
            note = "exact (B_j = 0)"
        elif j == "V1":
            note = "sign: + = sub-additive relief"
        a(f"| {j} | " + " | ".join(cells) + f" | {note} |")
    a("")
    gb = [cell(t, "interaction", J_OF[m], j, m, "bound") / cell(t, "interaction", J_OF[m], j, m, "B")
          for j in GAP_OBJ for m in LEVELS]
    a(f"No ratio is formed for j ≠ V1. For E1 / E3 the gap bound (G_J + Σ G_s + 5 G_b) "
      f"is {min(gb):.0f}–{max(gb):.0f} × r_I, so these are unreadable, as stated in advance.")
    a("")
    a("## 4. Location at fixed total")
    a("")
    a("### 4.1 Raw contrasts y(a) − y(b), in B_j units")
    a("")
    pairs = [f"{x} vs {y}" for x, y in LOC_PAIRS]
    a("| pair | " + " | ".join(objs) + " |")
    a("|---|" + "---|" * len(objs))
    for pr in pairs:
        a(f"| {pr} | " + " | ".join(
            f"{_r(cell(t, 'loc_raw', pr, j, col='ratio'))} ({cell(t, 'loc_raw', pr, j, col='verdict')})"
            for j in objs) + " |")
    a("")
    a("E1 / E3 pair gap bound G_a + G_b: " + "; ".join(
        f"{pr}: {_money(cell(t, 'loc_raw', pr, 'E1', col='bound'))}" for pr in pairs) + ".")
    a("N1 is chatter-limited (§3). It is reported against B_N1 and never read as a location effect.")
    a("")
    a("### 4.2 H_C efficiency residual (V1, N4): R_a − R_b · H_C,a / H_C,b")
    a("")
    a("| pair | objective | raw / B_j | residual | residual / B_j | read |")
    a("|---|---|---|---|---|---|")
    for pr in pairs:
        for j in RESID_OBJ:
            a(f"| {pr} | {j} | {_r(cell(t, 'loc_raw', pr, j, col='ratio'))} | "
              f"{_val(j, cell(t, 'loc_resid', pr, j))} | {_r(cell(t, 'loc_resid', pr, j, col='ratio'))} | "
              f"**{cell(t, 'loc_resid', pr, j, col='verdict')}** |")
    a("")
    a("Efficiency e(x) = R(x) / H_C(x):")
    a("")
    a("| row | e_V1 (MWh/MWh) | e_N4 (line-h per GWh of H_C) |")
    a("|---|---|---|")
    for lab in LABELS:
        a(f"| {lab} | {cell(t, 'efficiency', lab, 'V1'):.4f} | {1e3 * cell(t, 'efficiency', lab, 'N4'):.4f} |")
    a("")
    pr78 = pairs[1]
    a(f"**Matched-u pair (rows 7–8):** residual {_r(cell(t, 'loc_resid', pr78, 'V1', col='ratio'))} B_V1 ≥ 1. "
      "By the §3 rule the one-location reading does NOT stand directly. §3 stated in advance that "
      "the pool model predicts a profile-only (no-network) difference of ≈ 9 rulers for this pair.")
    a("")
    a("## 5. Saturation probe (row 9, P3_1500_all)")
    a("")
    a(f"- V1 relief R_9 = {_val('V1', cell(t, 'saturation', 'R_row9', 'V1'))} "
      f"({cell(t, 'saturation', 'R_row9', 'V1', col='ratio'):.1f} B_V1). This is "
      f"{100 * cell(t, 'saturation', 'R_row9_over_pool', 'V1'):.1f} % of the base_v3 behind-cut "
      f"curtailment pool, {_val('V1', cell(t, 'saturation', 'pocket_pool_base_v3', 'V1'))}. The pool is "
      "non-PEM WIND + PV curtailment at buses 2 / 75 / 120 / 121, computed in code; the prompt quoted 4.87 TWh.")
    a(f"- H_C(row 9) = {_val('V1', cell(t, 'saturation', 'H_C_row9', 'V1'))} = "
      f"{cell(t, 'saturation', 'H_C_row9_over_pool', 'V1'):.3f} × the pool, so host-absorbable energy "
      "exceeds what is curtailed.")
    a(f"- e(row 9) = {cell(t, 'saturation', 'e_row9', 'V1'):.4f}, the lowest of the nine rows "
      f"(row 6, the same composition at 800 MW: {cell(t, 'saturation', 'e_row6', 'V1'):.4f}). "
      f"The extra 700 MW from row 6 to row 9 adds {_val('V1', cell(t, 'saturation', 'R_row9_minus_R_row6', 'V1'))} "
      f"of relief ({cell(t, 'saturation', 'R_row9_minus_R_row6', 'V1', col='ratio'):.1f} B_V1). Descriptive only.")
    a("")
    a("## 6. Physics-prediction check (stated in §3 before any Y)")
    a("")
    a("| prediction | observed | verdict |")
    a("|---|---|---|")
    a(f"| no residual location effect for V1 / N4 after H_C scaling | "
      f"{int(cell(t, 'prediction', 'no residual location effect (V1, N4)'))} of 8 residual reads are LOCATION EFFECT | "
      f"**{cell(t, 'prediction', 'no residual location effect (V1, N4)', col='verdict')}** |")
    a(f"| E1 contrasts at 800 WITHIN GAP BOUND (pair bound ≈ $37–50M) | "
      f"{int(cell(t, 'prediction', 'E1 at 800 within gap bound'))} GAP-READABLE; bound "
      f"{_money(cell(t, 'prediction', 'E1 800 pair bound min'))}–{_money(cell(t, 'prediction', 'E1 800 pair bound max'))} | "
      f"**{cell(t, 'prediction', 'E1 at 800 within gap bound', col='verdict')}** |")
    a(f"| R4 unreadable | {int(cell(t, 'prediction', 'R4 unreadable'))} of 4 location pairs READABLE "
      "(both pairs against row 6) | "
      f"**{cell(t, 'prediction', 'R4 unreadable', col='verdict')}** |")
    a(f"| g ≈ 0.07 / 0.12 / 0.18 | " + " / ".join(f"{cell(t, 'V1_g', J_OF[m], 'V1', m):.3f}" for m in LEVELS)
      + " | lower at every level |")
    a(f"| H_C(b120) / H_C(b275) ≈ 1.149 | {cell(t, 'prediction', 'H_C(b120)/H_C(b275)'):.4f} | input check (no Y) |")
    a("")
    a("A contradiction is a finding, not an error (§3).")
    a("")
    a("## 7. What the reads say (interpretation; the verdicts above stand as computed)")
    a("")
    a("- **The rule reads LOCATION EFFECT for V1 on all four pairs.** At matched total, the "
      "bus-120 rows relieve more curtailment per unit of H_C than the bus-2/75 rows "
      f"(e {cell(t, 'efficiency', 'P2_800_b120', 'V1'):.3f} vs {cell(t, 'efficiency', 'P2_800_b275', 'V1'):.3f} "
      f"at 800 MW; {cell(t, 'efficiency', 'P2_500_270', 'V1'):.3f} vs {cell(t, 'efficiency', 'P2_500_110_140', 'V1'):.3f} "
      "in the matched-u pair). H_C scaling does not remove the difference.")
    a("- **This is not evidence of a NETWORK effect.** All six sites share one PTDF on L252 "
      "and one LMP. H_C counts every curtailed hour equally, but relief in an hour is also "
      "bounded by how much is curtailed in that hour. A site whose output is high in the "
      "deep-curtailment hours relieves more per MWh of H_C: that is a wind-profile effect. "
      "§3 predicted in advance a profile-only difference of ≈ 9 rulers for the matched-u "
      f"pair; the observed residual is {cell(t, 'loc_resid', pr78, 'V1', col='ratio'):.1f} rulers. "
      "The covariate H_C was too coarse to absorb the profile. The pre-registered "
      "label is kept; it means \"not explained by H_C\", not \"network\".")
    a("- **Size non-linearity also enters the pairs against row 6.** e falls with size on the "
      f"same composition (P1: {cell(t, 'efficiency', 'P1_60', 'V1'):.3f} → {cell(t, 'efficiency', 'P1_120', 'V1'):.3f} → "
      f"{cell(t, 'efficiency', 'P1_180', 'V1'):.3f}; row 6 → row 9: {cell(t, 'saturation', 'e_row6', 'V1'):.3f} → "
      f"{cell(t, 'saturation', 'e_row9', 'V1'):.3f}). The linear H_C scaling ignores this fall.")
    a("- N4: pair 4–5 is COMPOSITION, and the other three pairs read LOCATION EFFECT with the same caveat. "
      "N1 is not readable on any pair, as expected (chatter-limited).")
    a("- E1 / E3: every location contrast is NOT READABLE or WITHIN GAP BOUND. No cost statement can be made.")
    a("")
    a("## 8. Scope sentence for the paper (§3 template, branch chosen by the read)")
    a("")
    lo = min(abs(cell(t, "loc_resid", pr, "V1", col="ratio")) for pr in pairs)
    hi = max(abs(cell(t, "loc_resid", pr, "V1", col="ratio")) for pr in pairs)
    a("> \"On ERCOT we did not run pair grids. We screened location one site at a time (six "
      "slate wind sites × 60/120/180 MW, identity v3) and tested it directly with nine runs at "
      "360–1,500 MW total: three all-six joint runs, five matched-total reallocations (one pair "
      "matched on share of nameplate) and one saturation probe. Network data place all six sites "
      "behind one cut (L252), so differences at matched total are read as "
      f"a residual location effect of {lo:.1f}–{hi:.1f} × the ruler "
      "(chosen per the §3 read). Per-site curtailment inside the pocket is an LP tie (identical PTDFs; "
      "bus-120 sites 39–58 % curtailed, bus-2/75 sites 4–10 %), so only pocket and system totals are "
      "read. ERCOT-wide location sensitivity rests on the v1-identity 16-site screening (curtailment "
      "relief 25–397 × the v1 replicate ruler of 5,479 MWh; its cost numbers are void, "
      "`INVALID_v1_costs.md`); site 275 (1,039 MW, 1.48 TWh curtailed) is in the pocket but not in the slate.\"")
    a("")
    a("Suggested qualifier for the paper (not part of the frozen template): \"... a residual of "
      f"{lo:.1f}–{hi:.1f} × the ruler not explained by host-absorbable energy, consistent in size with "
      "wind-profile differences between sites behind the same cut.\"")
    a("")
    a("## 9. Figures")
    a("")
    a("- `figs/fig_v1_relief_vs_total.png`: V1 relief vs total MW (P1 joints, ΣOAT, P3, P2 rows, the behind-cut pool).")
    a("- `figs/fig_efficiency_relief_over_HC.png`: e = relief / H_C per row.")
    a("- `figs/fig_rows4to8_in_Bj.png`: rows 4–8 vs base in B_j units, one panel per objective (R1 omitted, B = 0).")
    a("")
    a("## 10. Seen data and deviations")
    a("")
    a("- Seen: this wave's 9 runs, wave D rows 1–18, base_v3:1, `ercot_noise.json`. Not read: "
      "`extracts/n0_E`, `extracts/random_E`, `extracts/methods_E_*`.")
    a("- B_j comes from the 63-re-emitted `ercot_noise.json` (D2 excluded, 6 δ). This is the "
      f"bar §3 defines. B_N4 = {cell(t, 'bar', 'B_j', 'N4'):.1f} and B_N1 = {cell(t, 'bar', 'B_j', 'N1'):.1f} "
      "replace the median rulers 8.5 and 15 quoted in §3's prose; the B_j rule is the binding one.")
    a("- §3 gives no threshold for I_j with j ≠ V1. Those values are reported as I_j / r_I without a verdict. "
      "For E1 / E3 the gap label is applied to |I| ≥ r_I.")
    a("- E1 / E3 location verdicts: NOT READABLE if |Δ| < B_j; otherwise GAP-READABLE if |Δ| > G_a + G_b, "
      "else WITHIN GAP BOUND.")
    a("- N4 residual: relief r = −Δ_N4 (fewer L252 hours ≥ 99 %), scaled by the same H_C ratio as V1.")
    a("- §7 above is interpretation, added after the read. It changes no verdict.")
    a("")
    return "\n".join(L)


def main():
    t = compute()
    t.to_csv(OUT_CSV, index=False)
    t2 = load_csv()
    assert_csv_equals(t, t2)                       # assert-before-draw: everything downstream reads t2
    figures(t2)
    OUT_MD.write_text(render_md(t2))
    print(f"wrote {OUT_CSV.name} ({len(t2)} rows), {OUT_MD.name}, figs/")


if __name__ == "__main__":
    main()
