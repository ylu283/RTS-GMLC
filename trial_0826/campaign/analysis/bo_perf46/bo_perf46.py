"""Prompt 46 — BO performance pack at n0 = 32 (existing data only).

Zero simulation, no GP fits, no holdout. Reads the four methods_C ledgers
(per-round hv / threshold), arms.json + wave objectives (fronts), and the
prompt-34 random-baseline figures (copied, not recomputed).

HV is recomputed per round ONLY as a data check (bogp.mobo.pareto.
hypervolume_exact @ 60e6328, the ledgers' bo_gp_sha) and asserted equal
to the ledger value; every HV reported comes from the ledger.

Run:  BOGP_PATH=/Users/yilu/Documents/GitHub/bo-gp-qparego \
      /opt/anaconda3/envs/bogp-botorch/bin/python bo_perf46.py
"""
from __future__ import annotations

import json
import os
import shutil
import sys

import numpy as np
import pandas as pd

_BOGP_PATH = os.environ.get("BOGP_PATH", "/Users/yilu/Documents/GitHub/bo-gp-qparego")
sys.path.insert(0, _BOGP_PATH)
from bogp.mobo.pareto import hypervolume_exact  # noqa: E402

import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
CAMPAIGN = os.path.abspath(os.path.join(HERE, "..", ".."))
ANALYSIS = os.path.join(CAMPAIGN, "analysis")
FIGS = os.path.join(HERE, "figs")
os.makedirs(FIGS, exist_ok=True)

ARMS = ["P1", "P2", "P3", "N1"]
M_COLS = ["load_shed_mwh", "true_curtailment_mwh", "total_cost_less_synthetic_usd"]
SORTED_TIERS = None  # design columns not needed (objectives only)

# §1 pinned, ARM-LABELED stops (asserted against the ledgers below)
PINNED_STOP = {"P1": 2, "P2": 3, "P3": 4, "N1": 3}
PINNED_OVERRUN = {("P1", 3): 0.62, ("P1", 4): 0.30, ("P2", 4): 0.26, ("N1", 4): 0.22}
# ref labels: P1 and N1 share S1's frozen ref (N1 copied P1's ref + tau)
REF_LABEL = {"P1": "R_S1", "N1": "R_S1", "P2": "R_S2", "P3": "R_S3"}
START_SET = {"P1": "S1", "N1": "S1", "P2": "S2", "P3": "S3"}

RB_VERDICT = ("above at both refs; NOT robust to floor-level output perturbation "
              "(47% of 1,000 draws keep 'above'; threshold 80%)")
RB_CONDITIONAL = ("The perturbation jointly used the ASSUMED floors 3,000 MWh / "
                  "5,000 MWh / $0.5M, so this rider is conditional on the rejected "
                  "old floor.")
RB_POINTER = ("Measured-shed re-run of the prompt-34 rider (shed level 285.3 MWh; "
              "curt/cost at assumed floors): prompt 45 deliverable 4 — NOT yet "
              "available on phaseb at the time of this pack (prompt 45 in flight); "
              "slot left open, quote side by side once it lands.")
ECON = ("cost endpoint r2#3 $510M (29 GWh shed, 1.26 TWh curt) vs reliability "
        "endpoint r1#5 (zero shed, 48 GWh curt, $668M); cheapest zero-shed design $582M")


def load_wave_y(wave: str) -> pd.DataFrame:
    ob = pd.read_csv(os.path.join(CAMPAIGN, "waves", wave, "objectives.csv"))
    df = ob[["index"] + M_COLS].copy()
    df["wave"] = wave
    assert np.isfinite(df[M_COLS].to_numpy(float)).all(), wave
    return df


def arm_points(cfg: dict, arm: str) -> pd.DataFrame:
    a = cfg["arms"][arm]
    parts = []
    for w in a["base_waves"]:
        d = load_wave_y(w); d["round"] = 0; parts.append(d)
    for k in range(1, cfg["hard_cap"] + 1):
        w = a["round_waves"].get(str(k)) or a["round_wave_pattern"].format(k=k)
        d = load_wave_y(w); d["round"] = k; parts.append(d)
        assert len(d) == cfg["q"], (arm, k, len(d))
    df = pd.concat(parts, ignore_index=True)
    assert (df["round"] == 0).sum() == 32, arm
    return df


def stop_round(entries: list[dict]) -> int:
    """First round the ledger records a stop (live 'stop' or record-only would_stop)."""
    for e in entries[1:]:
        if e.get("decision") == "stop" or e.get("would_stop"):
            return int(e["round"])
    raise AssertionError("no stop")


def nd_mask_min(Y: np.ndarray) -> np.ndarray:
    n = len(Y)
    m = np.ones(n, bool)
    for i in range(n):
        dom = np.all(Y <= Y[i], axis=1) & np.any(Y < Y[i], axis=1)
        if dom.any():
            m[i] = False
    return m


# --------------------------------------------------------------------------- #
# 1. table
# --------------------------------------------------------------------------- #
cfg = json.load(open(os.path.join(ANALYSIS, "methods_C", "arms.json")))
regrade = pd.read_csv(os.path.join(ANALYSIS, "noise_floor", "part_c_regrade.csv"))

rows, traj, pts = [], [], {}
for arm in ARMS:
    L = json.load(open(os.path.join(ANALYSIS, "methods_C", arm, "ledger.json")))
    ent = L["entries"]
    assert [e["round"] for e in ent] == [0, 1, 2, 3, 4], arm
    ref, tau = np.array(L["ref_point"]), float(L["threshold"])
    P = arm_points(cfg, arm)
    pts[arm] = P
    # data check: cumulative HV recomputed == ledger hv
    for e in ent:
        Y = P.loc[P["round"] <= e["round"], M_COLS].to_numpy(float)
        assert len(Y) == e["n"], (arm, e["round"])
        hv = hypervolume_exact(Y, ref)
        assert np.isclose(hv, e["hv"], rtol=1e-9, atol=0), (arm, e["round"], hv, e["hv"])
    s = stop_round(ent)
    assert s == PINNED_STOP[arm], (arm, s)
    hv0 = ent[0]["hv"]
    r = {"arm": arm, "acq": L["acq"], "start_set": START_SET[arm],
         "ref_label": REF_LABEL[arm],
         "ref_shed_mwh": ref[0], "ref_curt_mwh": ref[1], "ref_cost_usd": ref[2],
         "tau_old": tau, "rounds_graded": ent[-1]["round"],
         "evals_total": ent[-1]["n"], "evals_bo": ent[-1]["n"] - 32,
         "stop_round": s,
         "stop_kind": "live" if L.get("live_stop_round") == s else "rule stop, record-only",
         "evals_at_stop": ent[s]["n"]}
    over = []
    for e in ent[1:]:
        k = e["round"]
        g_tau = e["gain"] / tau
        if "gain_tau" in e:
            assert np.isclose(g_tau, e["gain_tau"], rtol=1e-12), (arm, k)
        rc = regrade[(regrade.arm == arm) & (regrade["round"] == k)]
        if len(rc):
            assert np.isclose(rc.gain.iloc[0], e["gain"], rtol=1e-12), (arm, k)
            assert np.isclose(rc.gain_over_tau_old.iloc[0], g_tau, rtol=1e-12), (arm, k)
        r[f"gain_tau_r{k}"] = g_tau
        r[f"hv_r{k}"] = e["hv"]
        traj.append({"arm": arm, "round": k, "hv": e["hv"], "gain_tau": g_tau,
                     "hv_over_hv0": e["hv"] / hv0})
        if k > s:
            assert round(g_tau, 2) == PINNED_OVERRUN[(arm, k)], (arm, k, g_tau)
            assert g_tau < 1.0
            over.append(f"r{k} {g_tau:.2f} sub-tau_old")
    traj.append({"arm": arm, "round": 0, "hv": hv0, "gain_tau": np.nan, "hv_over_hv0": 1.0})
    assert set(k for (a, k) in PINNED_OVERRUN if a == arm) == {k for k in range(s + 1, 5)}
    r["overrun"] = "; ".join(over) if over else "none (stop at cap)"
    r["hv0"] = hv0
    r["hv_stop"] = ent[s]["hv"]
    r["hv_cap"] = ent[-1]["hv"]
    r["hv_stop_over_hv0"] = ent[s]["hv"] / hv0
    r["hv_cap_over_hv0"] = ent[-1]["hv"] / hv0
    rows.append(r)

T = pd.DataFrame(rows)
T.to_csv(os.path.join(HERE, "bo_perf_table.csv"), index=False)
pd.DataFrame(traj).sort_values(["arm", "round"]).to_csv(
    os.path.join(HERE, "bo_perf_trajectory.csv"), index=False)

# economics: verify the pinned BO_STAGE2 numbers against P1 (= campaign) waves
P1 = pts["P1"]
def _pt(wave, idx):
    q = P1[(P1.wave == wave) & (P1["index"] == idx)]
    assert len(q) == 1
    return q[M_COLS].iloc[0].to_numpy(float)
c = _pt("bo_C_r2", 3); rel = _pt("bo_C_r1", 5)
assert round(c[2] / 1e6) == 510 and round(c[0] / 1e3) == 29 and round(c[1] / 1e6, 2) == 1.26, c
assert rel[0] == 0 and round(rel[1] / 1e3) == 48 and round(rel[2] / 1e6) == 668, rel
live = P1[P1["round"] <= 2]
zs = live[live.load_shed_mwh == 0]
assert round(zs.total_cost_less_synthetic_usd.min() / 1e6) == 582, zs
ECON_PTS = {"r2#3 (cost endpoint)": c, "r1#5 (reliability endpoint)": rel}


def _md_table(T: pd.DataFrame) -> str:
    hdr = ("| arm | acq | starts | ref | rounds | evals (BO) | gain/τ_old r1 · r2 · r3 · r4 "
           "| stop | overrun checkpoints | HV₀ | HV at stop | HV at cap | HV/HV₀ stop · cap |\n"
           "|---|---|---|---|---|---|---|---|---|---|---|---|---|\n")
    out = hdr
    for _, r in T.iterrows():
        g = " · ".join(f"{r[f'gain_tau_r{k}']:.2f}" for k in range(1, 5))
        out += (f"| {r.arm} | {r.acq} | {r.start_set} | {r.ref_label} | {r.rounds_graded} "
                f"| {r.evals_total} ({r.evals_bo}) | {g} | r{r.stop_round} {r.stop_kind} "
                f"| {r.overrun} | {r.hv0:.3e} ({r.ref_label}) | {r.hv_stop:.3e} ({r.ref_label}) "
                f"| {r.hv_cap:.3e} ({r.ref_label}) | {r.hv_stop_over_hv0:.3f} · {r.hv_cap_over_hv0:.3f} |\n")
    return out


refs = "\n".join(
    f"- **{lab}** (arms {', '.join(T[T.ref_label == lab].arm)}): shed "
    f"{g.ref_shed_mwh.iloc[0]:,.0f} MWh · curt {g.ref_curt_mwh.iloc[0]:,.0f} MWh · cost "
    f"${g.ref_cost_usd.iloc[0] / 1e6:,.1f}M; τ_old = {g.tau_old.iloc[0]:.4e}"
    for lab, g in T.groupby("ref_label", sort=False))

with open(os.path.join(HERE, "bo_perf_table.md"), "w") as f:
    f.write("# BO performance table — prompt 46 (n0 = 32)\n\n"
            "Source: `analysis/methods_C/{P1,P2,P3,N1}/ledger.json` (synced from d6 "
            "b0a6e1e). HV units: MWh·MWh·$. Every HV carries its arm's frozen ref; "
            "HV values across different refs are NOT comparable — compare HV/HV₀ only. "
            "gain/τ is relative to τ_old (prompt-30 MC, assumed floors 3,000 / 5,000 / "
            "$0.5M); the measured-noise re-grade is prompt 45's.\n\n")
    f.write(_md_table(T))
    f.write("\nStop rule: two consecutive rounds with gain < τ_old. Stops (arm-labeled): "
            "P1 r2 (live) · P2 r3 · P3 r4 (second strike AT the cap) · N1 r3. "
            "Overrun = record-only rounds after the stop; all are sub-τ_old, so no "
            "overrun reverses its stop.\n\n**Refs (ledger-frozen):**\n\n" + refs + "\n\n"
            "**Economics (BO_STAGE2.md §front, two distinct designs; values re-checked "
            "against waves/bo_C_r1, bo_C_r2):** " + ECON + ".\n")

# --------------------------------------------------------------------------- #
# 2. figures (assert-before-draw vs bo_perf_table.csv)
# --------------------------------------------------------------------------- #
plt.rcParams.update({"font.weight": "bold", "axes.labelweight": "bold",
                     "axes.titleweight": "bold", "font.size": 10})
TC = pd.read_csv(os.path.join(HERE, "bo_perf_table.csv")).set_index("arm")
TR = pd.read_csv(os.path.join(HERE, "bo_perf_trajectory.csv"))
C_LIVE, C_TAIL, C_START = "#1f77b4", "#d62728", "#9a9a9a"


def _save(fig, name):
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(FIGS, f"{name}.{ext}"), dpi=200, bbox_inches="tight")
    plt.close(fig)


# fig1: per-arm HV (own ref) + gain/τ_arm subpanel
fig = plt.figure(figsize=(11, 8.2))
outer = fig.add_gridspec(2, 2, hspace=0.42, wspace=0.28)
for i, arm in enumerate(ARMS):
    tr = TR[TR.arm == arm].sort_values("round")
    t = TC.loc[arm]
    s = int(t.stop_round)
    # assert-before-draw
    assert np.allclose(tr.hv.to_numpy()[[0, s, 4]], [t.hv0, t.hv_stop, t.hv_cap], rtol=1e-12)
    for k in range(1, 5):
        assert np.isclose(tr[tr["round"] == k].gain_tau.iloc[0], t[f"gain_tau_r{k}"], rtol=1e-12)
    g = outer[i // 2, i % 2].subgridspec(2, 1, height_ratios=[2, 1], hspace=0.08)
    ax, bx = fig.add_subplot(g[0]), fig.add_subplot(g[1])
    x, hv = tr["round"].to_numpy(), tr.hv.to_numpy() / 1e17
    live = x <= s
    ax.plot(x[live], hv[live], "-o", color=C_LIVE, lw=2, label="live phase")
    ax.plot(x[s:], hv[s:], "--s", color=C_TAIL, lw=2, label="record-only tail")
    ax.axvline(s, color="k", ls=":", lw=1.2)
    ax.axvspan(s, 4.4, color=C_TAIL, alpha=0.07)
    ax.set_xlim(-0.3, 4.4); ax.set_xticks(range(5)); ax.tick_params(labelbottom=False)
    ax.set_ylabel("HV (×1e17)")
    ax.set_title(f"{arm} ({t.acq}, starts {t.start_set}) — ref {t.ref_label}", fontsize=10)
    ax.text(0.02, 0.95, f"stop r{s} ({t.stop_kind})\nHV/HV₀ cap = {t.hv_cap_over_hv0:.3f}",
            transform=ax.transAxes, va="top", fontsize=8.5)
    if i == 0:
        ax.legend(loc="lower right", fontsize=8)
    gt = tr[tr["round"] >= 1]
    cols = [C_LIVE if k <= s else C_TAIL for k in gt["round"]]
    bx.bar(gt["round"], gt.gain_tau, color=cols, width=0.6)
    bx.axhline(1.0, color="k", lw=1)  # gain/τ_arm = 1 on a ratio axis
    bx.axvline(s, color="k", ls=":", lw=1.2)
    bx.set_xlim(-0.3, 4.4); bx.set_xticks(range(5))
    bx.set_ylabel("gain/τ_old"); bx.set_xlabel("round")
    for k, v in zip(gt["round"], gt.gain_tau):
        bx.text(k, v, f"{v:.2f}", ha="center", va="bottom", fontsize=7.5)
    bx.set_ylim(0, max(2.6, gt.gain_tau.max() * 1.25))
_save(fig, "fig1_hv_trajectories")

# fig1b: normalized combined view HV/HV₀ (ref-free ratio within each arm's own ref)
fig, ax = plt.subplots(figsize=(6.2, 4.2))
mk = {"P1": "o", "P2": "s", "P3": "^", "N1": "D"}
for arm in ARMS:
    tr = TR[TR.arm == arm].sort_values("round")
    t = TC.loc[arm]; s = int(t.stop_round)
    assert np.isclose(tr.hv_over_hv0.iloc[-1], t.hv_cap_over_hv0, rtol=1e-12)
    ln, = ax.plot(tr["round"], tr.hv_over_hv0, "-" + mk[arm], lw=1.8,
                  label=f"{arm} ({t.ref_label}; stop r{s})")
    ax.plot(s, tr.hv_over_hv0.iloc[s], marker="*", ms=16, color=ln.get_color(),
            mec="k", ls="none")
ax.set_xticks(range(5)); ax.set_xlabel("round"); ax.set_ylabel("HV / HV₀ (own ref)")
ax.legend(fontsize=8, title="★ = stop round", title_fontsize=8)
_save(fig, "fig1b_hv_normalized")

# fig2: fronts, 3 projections × 4 arms
PROJ = [(0, 1), (0, 2), (1, 2)]
SC = np.array([1e3, 1e3, 1e6])
LAB = ["shed (GWh)", "curtailment (GWh)", "cost_ls ($M)"]


def stair(Y2):
    m = nd_mask_min(Y2)
    F = Y2[m]; F = F[np.argsort(F[:, 0])]
    return F


fig, axes = plt.subplots(4, 3, figsize=(13, 15))
for i, arm in enumerate(ARMS):
    P = pts[arm]; t = TC.loc[arm]; s = int(t.stop_round)
    assert len(P) == t.evals_total and (P["round"] > 0).sum() == t.evals_bo
    Y = P[M_COLS].to_numpy(float) / SC
    rd = P["round"].to_numpy()
    start, livebo, tail = rd == 0, (rd >= 1) & (rd <= s), rd > s
    capF = nd_mask_min(Y); stopF = nd_mask_min(np.where((rd <= s)[:, None], Y, np.inf))
    stopF &= rd <= s
    for j, (a, b) in enumerate(PROJ):
        ax = axes[i, j]
        ax.scatter(Y[start, a], Y[start, b], s=22, c=C_START, label="Sobol starts (32)")
        ax.scatter(Y[livebo, a], Y[livebo, b], s=34, c=C_LIVE, label=f"BO live r1–r{s}")
        if tail.any():
            ax.scatter(Y[tail, a], Y[tail, b], s=40, c=C_TAIL, marker="^",
                       label=f"record-only r{s + 1}–r4")
        ax.scatter(Y[capF, a], Y[capF, b], s=95, facecolors="none", edgecolors="k",
                   lw=1.1, label="cap-front member (3-D nondominated of 64)")
        Fs = stair(Y[rd <= s][:, [a, b]]); Fc = stair(Y[:, [a, b]])
        ax.step(Fc[:, 0], Fc[:, 1], where="post", color="k", lw=1.4, label="cap 2-D front")
        ax.step(Fs[:, 0], Fs[:, 1], where="post", color=C_LIVE, ls="--", lw=1.4,
                label=f"live-stop 2-D front (≤ stop round; r{s} here)")
        ax.set_xlabel(LAB[a]); ax.set_ylabel(LAB[b])
        if j == 0:
            ax.set_title(f"{arm} ({t.acq}, starts {t.start_set}) — stop r{s} {t.stop_kind}",
                         loc="left", fontsize=10)
        if arm == "P1":
            for nm, v in ECON_PTS.items():
                v = v / SC
                ax.annotate(nm.split()[0], (v[a], v[b]), xytext=(6, 6),
                            textcoords="offset points", fontsize=8)
        if i == 0 and j == 2:
            ax.legend(fontsize=7.5, loc="upper right")
fig.tight_layout()
_save(fig, "fig2_fronts")

# fig3: copy the prompt-34 figures (no recompute)
RB = os.path.join(ANALYSIS, "random_baseline", "figs")
for src, dst in [("fig1_hv_band", "fig3a_random_baseline_hv_band"),
                 ("fig4b_grand_front_unified", "fig3b_random_baseline_grand_front_unified")]:
    for ext in ("png", "pdf"):
        shutil.copyfile(os.path.join(RB, f"{src}.{ext}"), os.path.join(FIGS, f"{dst}.{ext}"))

print(T[["arm", "stop_round", "stop_kind", "overrun", "hv_stop_over_hv0", "hv_cap_over_hv0"]]
      .to_string(index=False))
print("cap-front sizes:", {a: int(nd_mask_min(pts[a][M_COLS].to_numpy(float)).sum()) for a in ARMS})
print("econ:", {k: (v / SC).round(2).tolist() for k, v in ECON_PTS.items()})
