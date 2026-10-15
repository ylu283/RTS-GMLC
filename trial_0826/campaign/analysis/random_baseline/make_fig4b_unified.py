"""fig4b: grand front of 96 designs, drawn in the style of bo_stage2 fig1_front.

Same panels, axes, markers and colours as analysis/bo_stage2/figs/fig1_front.png;
random designs get a new marker (purple triangle). Front and knee logic match
random_baseline.ipynb (cells 20-21). Writes figs/fig4b_grand_front_unified.{png,pdf}.
Run from anywhere: /opt/anaconda3/bin/python make_fig4b_unified.py
"""
import os, json
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
CAMP = os.path.abspath(os.path.join(HERE, "..", ".."))
FIG = os.path.join(HERE, "figs")

plt.rcParams.update({"font.size": 11, "axes.labelweight": "bold", "axes.titleweight": "bold",
                     "axes.linewidth": 1.6, "xtick.major.width": 1.4, "ytick.major.width": 1.4,
                     "font.weight": "bold", "axes.spines.top": False, "axes.spines.right": False,
                     "savefig.dpi": 200, "savefig.bbox": "tight"})
C_START, C_R1, C_R2, C_FRONT = "#8a8985", "#2a78d6", "#eb6834", "#1baf7a"   # fig1
C_RND = "#7b3fb5"                                                           # new: purple
M = ["load_shed_mwh", "true_curtailment_mwh", "total_cost_less_synthetic_usd"]
SHORT_K = {"load_shed_mwh": "Load shed [GWh]", "true_curtailment_mwh": "Curtailment [GWh]",
           "total_cost_less_synthetic_usd": "Cost less synthetic [$M]"}
R_FROZEN = np.asarray(json.load(open(os.path.join(CAMP, "analysis/bo_stage2/ledger.json")))["ref_point"], float)

# ---- data (labels as in the reports: n0#k, n0b#k, r1#k, r2#k, rnd#k) --------
frames = []
for w, src in [("stage2_C_n0", "start"), ("stage2_C_n0b", "start"), ("bo_C_r1", "r1"),
               ("bo_C_r2", "r2"), ("random_C", "random")]:
    dm = pd.read_csv(os.path.join(CAMP, "waves", w, "design_matrix.csv"))
    ob = pd.read_csv(os.path.join(CAMP, "waves", w, "objectives.csv"))
    d = dm.merge(ob[["index"] + M], on="index", validate="1:1")
    d["wave"], d["src"] = w, src
    frames.append(d)
D = pd.concat(frames, ignore_index=True)
D["label"] = (D["wave"].str.replace("stage2_C_", "").str.replace("bo_C_", "")
              .str.replace("random_C", "rnd") + "#" + D["index"].astype(str))
assert len(D) == 96 and D.groupby("src").size().to_dict() == {"start": 32, "r1": 8, "r2": 8, "random": 48}
Y = D[M].to_numpy(float)
assert np.isfinite(Y).all()


def nondominated(Y):
    return np.array([not np.any(np.all(Y <= y, axis=1) & np.any(Y < y, axis=1)) for y in Y])


def knees_of(F, k=3):
    Yf = F[M].to_numpy(float); lo, hi = Yf.min(0), Yf.max(0)
    F = F.assign(dist_utopia=np.linalg.norm((Yf - lo) / (hi - lo), axis=1))
    return F.nsmallest(k, "dist_utopia")


D["front"] = nondominated(Y)
D["in_ref"] = np.all(Y < R_FROZEN, axis=1)
F = D[D.front]
cnt = F.src.value_counts().to_dict()
n_r1, n_r2 = cnt.get("r1", 0), cnt.get("r2", 0)
assert len(F) == 32, len(F)
assert n_r1 + n_r2 == 13, (n_r1, n_r2)
assert cnt.get("start", 0) == 7 and cnt.get("random", 0) == 12, cnt

kfull = knees_of(F)
kclip = knees_of(D[D.front & D.in_ref])
assert len(D[D.front & D.in_ref]) == 25
assert list(kfull.label) == ["rnd#2", "n0b#8", "r1#2"], list(kfull.label)
assert list(kclip.label) == ["r2#1", "rnd#43", "r1#2"], list(kclip.label)
kclip_only = kclip[~kclip.label.isin(kfull.label)]

# check for the deck bullet: 13 starts on the 48-point front, 6 knocked off by random, all 13 BO stay
nr = (D.src != "random").to_numpy()
f48 = np.zeros(len(D), bool); f48[nr] = nondominated(Y[nr])
st48 = D[f48 & (D.src == "start")]
knocked = st48[~st48.front]
Yr = Y[(D.src == "random").to_numpy()]
assert len(st48) == 13 and len(knocked) == 6
assert all(np.any(np.all(Yr <= y, axis=1) & np.any(Yr < y, axis=1)) for y in knocked[M].to_numpy(float))
assert D[f48 & D.src.isin(["r1", "r2"])].front.all() and (f48 & D.src.isin(["r1", "r2"])).sum() == 13
print("front", len(F), cnt, "| knees full", list(kfull.label), "| clipped", list(kclip.label),
      "| starts knocked off by random:", list(knocked.label))

# ---- figure (geometry and styling copied from bo_stage2 fig1) ---------------
pairs = [(0, 1), (0, 2), (1, 2)]
scale = np.array([1e-3, 1e-3, 1e-6])
STY = [("start", C_START, "o", f"32 starting points ({cnt.get('start', 0)} on front)"),
       ("r1", C_R1, "s", f"BO round 1 ({n_r1} on front)"),
       ("r2", C_R2, "D", f"BO round 2 ({n_r2} on front)"),
       ("random", C_RND, "^", f"48 random ({cnt.get('random', 0)} on front)")]
# label offsets (points) per panel, tuned by eye against overlap; thin leader lines to the star
OFF = {
    "rnd#2":  [(55, 10), (50, -12), (-25, -60)],
    "n0b#8":  [(25, 45), (50, -62), (95, -5)],
    "r1#2":   [(-12, 55), (22, -55), (-45, -50)],
    "r2#1":   [(55, -30), (45, 38), (-30, -42)],
    "rnd#43": [(55, -8), (55, 18), (110, 25)],
}
fig, axs = plt.subplots(1, 3, figsize=(15, 4.6))
for p, (ax, (a, b)) in enumerate(zip(axs, pairs)):
    for src, col, mk, lab in STY:
        s = D[D.src == src]
        dom, fr = s[~s.front], s[s.front]
        ax.scatter(dom[M[a]] * scale[a], dom[M[b]] * scale[b], c=col, marker=mk, s=26, alpha=0.4,
                   edgecolors="white", linewidths=0.6, zorder=2)
        ax.scatter(fr[M[a]] * scale[a], fr[M[b]] * scale[b], c=col, marker=mk, s=46,
                   edgecolors="white", linewidths=1.0, label=lab, zorder=3)
    ax.scatter(F[M[a]] * scale[a], F[M[b]] * scale[b], facecolors="none", edgecolors=C_FRONT,
               s=150, linewidths=2.0, label="96-point front (n=%d)" % len(F), zorder=4)
    ax.scatter(kfull[M[a]] * scale[a], kfull[M[b]] * scale[b], marker="*", c="black", s=170,
               label="knees: full front", zorder=5)
    ax.scatter(kclip_only[M[a]] * scale[a], kclip_only[M[b]] * scale[b], marker="*", facecolors="white",
               edgecolors="black", linewidths=1.3, s=170, label="knees: clipped front", zorder=5)
    for _, r in pd.concat([kfull, kclip_only]).iterrows():
        ax.annotate(r.label, (r[M[a]] * scale[a], r[M[b]] * scale[b]), xytext=OFF[r.label][p],
                    textcoords="offset points", fontsize=9, fontweight="bold", zorder=6,
                    va="center", arrowprops=dict(arrowstyle="-", color="black", lw=0.7, shrinkA=0, shrinkB=6))
    ax.set_xlabel(SHORT_K[M[a]]); ax.set_ylabel(SHORT_K[M[b]])
    for t in ax.get_xticklabels() + ax.get_yticklabels():
        t.set_fontweight("bold")
axs[0].legend(fontsize=8.5, frameon=False, loc="upper right")
fig.suptitle("Stage-2 scenario C: 96 evaluated designs (32 starts + 16 BO + 48 random), "
             "3-objective front ringed (cost: g1-pending caveat)", fontweight="bold")
for ext in ("png", "pdf"):
    fig.savefig(os.path.join(FIG, f"fig4b_grand_front_unified.{ext}"))
print("wrote", os.path.join(FIG, "fig4b_grand_front_unified.{png,pdf}"))
