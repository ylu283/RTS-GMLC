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
                        r"\mathrm{C2,\ C3\ gates} = \mathrm{REVIEW\ only\ (never\ halt)}$"),
    ]
    rule = [
        ("eq_rule_1.png", r"$\mathrm{seat}\ j\ \Leftrightarrow\ \mathrm{OUTCOME}\ \wedge\ \mathrm{lo}_{90}(\mathrm{IDR}_j/B_j) \geq 2"
                          r"\ \wedge\ p^{\,\mathrm{raw}}_{\mathrm{Mantel}} \leq 0.01\ \wedge\ \mathrm{IDR}_j \geq \max(2B_j,\,M_j)"
                          r"\ \wedge\ \mathrm{IDR}_j/B_j \geq 3\ \wedge\ \neg\,\mathrm{suppressed}$"),
        ("eq_rule_2.png", r"$\mathrm{REDUNDANT}(c\,|\,p)\ \Leftrightarrow\ \rho_{\mathrm{raw}}(c,p) \geq 0.90\ \wedge\ \neg\,\mathrm{ESCAPE}$"),
        ("eq_rule_3.png", r"$\mathrm{ESCAPE}\ \Leftrightarrow\ c\ \mathrm{COMP\!-\!RES}\ \wedge\ "
                          r"[\ \neg\,(p\ \mathrm{COMP\!-\!RES})\ \vee\ \mathrm{up}_{90}\,\rho_{\mathrm{res}}(c,p) < 0.50\ ]$"),
        ("eq_rule_4.png", r"$\mathrm{COMP\!-\!RES}\ \Leftrightarrow\ p^{\,\mathrm{res}}_{\mathrm{Mantel}} \leq 0.01\ \wedge\ "
                          r"\mathrm{lo}_{90}(\mathrm{IDR}(r_j)/B_j) \geq 2\ \wedge\ \mathrm{IDR}(r_j) \geq M_j$"),
    ]
    return [render_eq(n, t) for n, t in bo], [render_eq(n, t) for n, t in rule]


if __name__ == "__main__":
    c = copy_figs()
    bo, rule = equations()
    for k, v in c.items():
        print(k, v[1], v[2])
    print("equations:", [p.name for p in bo + rule])
