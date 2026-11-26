"""Build figs/ for the ERCOT overnight deck (prompt 67 v1.1). Zero simulation. No new data figures.

Run:  /opt/anaconda3/bin/python make_overnight_figs.py        (from analysis/pi_overnight_1124/)
Out:  figs/<copied PNG>          byte copies of the committed figures named per slide (FIGURES_USED.md: source + commit)
      figs/eq_bo_*.png           slide 4 top: the BO problem, one PNG per line (math font)
      figs/eq_rule_*.png         slide 4 bottom: rule v2 in three lines (+ the COMPOSITION-RESOLVABLE line)

Equation recipe copied from admin/pre_can/misc/generate_equation_pngs.py (matplotlib mathtext, math_fontfamily 'cm',
dpi 300, transparent, bbox tight); that file is not modified. The equation PNGs have no axes; text is bold where
mathtext allows (rcParams font.weight bold). Every number in an equation comes from overnight_facts.py.
"""

from __future__ import annotations

import hashlib
import shutil
import subprocess

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

import overnight_facts as F  # noqa: E402

FIGS = F.HERE / "figs"
FIGS.mkdir(exist_ok=True)
plt.rcParams.update({"font.weight": "bold", "axes.labelweight": "bold", "axes.titleweight": "bold",
                     "mathtext.fontset": "cm"})

# slide → (source, short name); copied byte for byte
COPIES = {
    "fig_parity_holdout.png": F.GP / "figs" / "fig_parity_holdout.png",                    # slide 6
    "fig_parity_holdout_v2.png": F.GP / "figs" / "fig_parity_holdout_v2.png",              # slide 7
    "fig_EMU_multi_hv_committed.png": F.EMU / "figs" / "fig_EMU_multi_hv_committed.png",   # slide 9
    "fig_EMU_calibration_committed.png": F.EMU / "figs" / "fig_EMU_calibration_committed.png",  # slide 10
    "fig_training_size_curves_v2.png": F.GP / "figs" / "fig_training_size_curves_v2.png",  # B1
}


def src_commit(p):
    return subprocess.check_output(["git", "-C", str(F.REPO), "log", "-1", "--format=%h", "ercot/tx123", "--",
                                    str(p.relative_to(F.REPO))], text=True).strip()


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


def copy_figs():
    out = {}
    for name, src in COPIES.items():
        dst = FIGS / name
        shutil.copyfile(src, dst)
        assert md5(src) == md5(dst)
        out[name] = (src, src_commit(src), md5(src))
    return out


def render_eq(filename, latex, fontsize=20, figwidth=12, figheight=0.7):
    """pre_can recipe: one mathtext line, centred, cm math font, 300 dpi, transparent."""
    fig, ax = plt.subplots(figsize=(figwidth, figheight))
    ax.text(0.0, 0.5, latex, fontsize=fontsize, ha="left", va="center", transform=ax.transAxes, math_fontfamily="cm")
    ax.axis("off")
    path = FIGS / filename
    fig.savefig(path, dpi=300, bbox_inches="tight", transparent=True, pad_inches=0.06)
    plt.close(fig)
    return path


def equations():
    Rv1 = f"{F.R_V1:,.0f}".replace(",", "{,}")
    Re1 = f"{F.R_E1:,.2f}".replace(",", "{,}")
    bo = [
        ("eq_bo_1.png", r"$\min_{u\,\in\,[0,1]^{%d}}\ \ (V_1(u),\ E_1(u))\ \ =\ \ "
                        r"(\mathrm{curtailment\ MWh},\ \mathrm{total\ system\ cost\ \$})$" % F.N_SITES),
        ("eq_bo_2.png", r"$y = f(u) + \varepsilon,\quad f = \mathrm{PCM\ (Prescient,\ identity\ v3)},\quad "
                        r"\varepsilon\ :\ \mathrm{solver\ seed\ chatter}\ \Sigma_c$"),
        ("eq_bo_3.png", r"$n_0 = %d\ \mathrm{Sobol\ designs};\quad \hat f_j \sim \mathcal{GP}_j\ \ "
                        r"(V_1{:}\ \mathrm{house\ fit},\ \ E_1{:}\ \mathrm{fit\ v2})$" % F.N0),
        ("eq_bo_4.png", r"$\mathrm{qNEHVI},\ q = %d\ \mathrm{per\ round},\ %d\ \mathrm{seed\ lanes},\ \mathrm{cap}\ %d;"
                        r"\quad R = (%s\ \mathrm{MWh};\ \$%s\mathrm{M})$" % (F.Q, F.LANES, F.CAP, Rv1, Re1)),
        ("eq_bo_5.png", r"$\tau_{\mathrm{exact}} = 0\ \Rightarrow\ \mathrm{budget\ cap\ only};\quad "
                        r"\mathrm{budget}\ %d \times %d \times %d = %d\ \mathrm{PCM\ runs};\quad \mathrm{C2,\ C3} = \mathrm{REVIEW\ only}$"
                        % (F.LANES, F.CAP, F.Q, F.BUDGET)),
    ]
    rule = [
        ("eq_rule_1.png", r"$\mathrm{seat}\ j\ \Leftrightarrow\ \mathrm{OUTCOME}\ \wedge\ \mathrm{lo}_{90}(\mathrm{IDR}_j/B_j) \geq 2"
                          r"\ \wedge\ p^{\,\mathrm{raw}}_{\mathrm{Mantel}} \leq 0.01\ \wedge\ \mathrm{IDR}_j \geq \max(2B_j,\,M_j)"
                          r"\ \wedge\ \mathrm{IDR}_j/B_j \geq 3\ \wedge\ \neg\,\mathrm{suppressed}$"),
        ("eq_rule_2.png", r"$\mathrm{REDUNDANT}(c\,|\,p)\ \Leftrightarrow\ \rho_{\mathrm{raw}}(c,p) \geq 0.90\ \wedge\ \neg\,\mathrm{ESCAPE}$"),
        ("eq_rule_3.png", r"$\mathrm{ESCAPE}\ \Leftrightarrow\ c\ \mathrm{COMP}\text{-}\mathrm{RES}\ \wedge\ "
                          r"[\ \neg\,(p\ \mathrm{COMP}\text{-}\mathrm{RES})\ \vee\ \mathrm{up}_{90}\,\rho_{\mathrm{res}}(c,p) < 0.50\ ]$"),
        ("eq_rule_4.png", r"$\mathrm{COMP}\text{-}\mathrm{RES}\ \Leftrightarrow\ p^{\,\mathrm{res}}_{\mathrm{Mantel}} \leq 0.01\ \wedge\ "
                          r"\mathrm{lo}_{90}(\mathrm{IDR}(r_j)/B_j) \geq 2\ \wedge\ \mathrm{IDR}(r_j) \geq M_j$"),
    ]
    return [render_eq(n, t) for n, t in bo], [render_eq(n, t) for n, t in rule]


CROPS = {}   # derived PNG name -> (source PNG, description)


def crops():
    """Crops of the byte-copied figures (no pixel is redrawn): slide 5 parity V1/E1 columns; B1 split in two."""
    from PIL import Image
    par = Image.open(FIGS / "fig_parity_holdout.png")
    W, H = par.size
    assert (W, H) == (2464, 1078)
    par.crop((0, 0, 1232, H)).save(FIGS / "fig_parity_holdout_V1E1.png")
    CROPS["fig_parity_holdout_V1E1.png"] = ("fig_parity_holdout.png", "cropped: left two columns (V1, E1), x 0–1232 px")
    tr = Image.open(FIGS / "fig_training_size_curves_v2.png")
    W, H = tr.size
    assert (W, H) == (2376, 1848)
    leg = tr.crop((820, 1800, 1550, 1848))
    for name, box, what in (("fig_training_size_curves_v2_V1E1.png", (0, 115, 1178, 1795), "V1, E1 columns"),
                            ("fig_training_size_curves_v2_N4N1.png", (1178, 115, 2376, 1795), "N4, N1 columns")):
        pan = tr.crop(box)
        out = Image.new("RGB", (pan.width, pan.height + leg.height + 10), "white")
        out.paste(pan, (0, 0))
        out.paste(leg, ((pan.width - leg.width) // 2, pan.height + 5))
        out.save(FIGS / name)
        CROPS[name] = ("fig_training_size_curves_v2.png", f"cropped: {what} + the arm legend strip")


def fig_hv5():
    """Slide 8: true-f HV / best-known front, committed truth only, 5 legend entries (re-rendered from the csv/json)."""
    import numpy as np
    m = F.mul[(F.mul.variant == "committed")]
    bl = F.xc["baselines"]
    r = np.arange(5)
    s0 = {sd: g.sort_values("round")["hv_true_frac_best"].to_numpy() for sd, g in m[m.scenario == "s0"].groupby("seed_id")}
    s1 = {sd: g.sort_values("round")["hv_true_frac_best"].to_numpy() for sd, g in m[m.scenario == "s1"].groupby("seed_id")}
    # assert before draw
    assert len(s0) == 5 and all(len(v) == 5 for v in s0.values()) and len(s1) == 5
    assert abs(min(v[4] for v in s0.values()) - F.HV_LO) < 1e-12 and abs(max(v[4] for v in s0.values()) - F.HV_HI) < 1e-12
    assert abs(bl["uniform"]["p95"][4] - F.UNI[2]) < 1e-12 and abs(bl["vertices"]["p95"][4] - F.VERT95) < 1e-12
    assert abs(bl["plugin_spread"]["p50"][4] - F.SPREAD) < 1e-12
    TICK = 15
    fig, ax = plt.subplots(figsize=(8.4, 6.0))
    ax.fill_between(r, bl["uniform"]["p5"], bl["uniform"]["p95"], color="#BBBBBB", alpha=0.6, label="i.i.d. uniform, 5–95 %")
    ax.fill_between(r, bl["vertices"]["p5"], bl["vertices"]["p95"], color="#B39DDB", alpha=0.5, label="random box vertices, 5–95 %")
    ax.plot(r, bl["plugin_spread"]["p50"], "D--", color="#E66100", lw=2.5, ms=7, label="r0 plug-in front, no search")
    for i, v in enumerate(s1.values()):
        ax.plot(r, v, "o--", color="#00A6B7", lw=1.6, ms=5, label="qNEHVI s1 (shed-constrained), 5 lanes" if i == 0 else None)
    for i, v in enumerate(s0.values()):
        ax.plot(r, v, "o-", color="#0C2340", lw=2.6, ms=6, label="qNEHVI s0, 5 lanes" if i == 0 else None)
    ax.set_xlabel("Round", fontsize=17, fontweight="bold")
    ax.set_ylabel("true-f HV / best-known front", fontsize=17, fontweight="bold")
    ax.set_xticks(r)
    for lab in ax.get_xticklabels() + ax.get_yticklabels():
        lab.set_fontweight("bold"); lab.set_fontsize(TICK)
    ax.grid(alpha=0.3)
    ax.legend(loc="upper center", bbox_to_anchor=(0.45, -0.13), ncol=2, prop={"weight": "bold", "size": 12}, frameon=False)
    out = FIGS / "fig_hv_committed_5series.png"
    fig.savefig(out, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return out


if __name__ == "__main__":
    c = copy_figs()
    crops()
    fig_hv5()
    bo, rule = equations()
    for k, v in c.items():
        print(k, v[1], v[2])
    print("equations:", [p.name for p in bo + rule])
