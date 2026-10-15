"""Prompt 39 figures. House style: bold axis labels AND bold tick values;
PNG + PDF under figs/. No fits; reads the csv/json outputs only.
"""
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
FIGS = os.path.join(HERE, "figs")
os.makedirs(FIGS, exist_ok=True)

plt.rcParams.update({"axes.labelweight": "bold", "axes.titleweight": "bold",
                     "font.weight": "bold"})

LABEL = {"shed": "load shed", "curt": "curtailment", "cost_ls": "cost (ls)"}
ARMS = [16, 32, 48]


def boldticks(ax):
    for t in ax.get_xticklabels() + ax.get_yticklabels():
        t.set_fontweight("bold")


def save(fig, name):
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(FIGS, f"{name}.{ext}"), dpi=150,
                    bbox_inches="tight")
    plt.close(fig)
    print(f"figs/{name}.png + .pdf written")


def fig_curve():
    hold = pd.read_csv(os.path.join(HERE, "holdout_results.csv"))
    rib = pd.read_csv(os.path.join(HERE, "ribbon.csv"))
    fig, axes = plt.subplots(1, 3, figsize=(13, 4.2))
    for ax, obj in zip(axes, ["shed", "curt", "cost_ls"]):
        for role, color, mark in (("default", "tab:blue", "o"),
                                  ("winner", "tab:red", "s")):
            sub = hold[(hold.objective == obj) & (hold.role == role)]
            v = [float(sub[sub.arm == a]["rmse_over_floor"].iloc[0])
                 for a in ARMS]
            ax.plot(ARMS, v, f"-{mark}", color=color, lw=2, ms=6,
                    label="campaign default" if role == "default"
                    else "Part-H winner")
        r = rib[rib.objective == obj]["holdout_rmse_over_floor"]
        ax.errorbar([16], [r.median()],
                    yerr=[[r.median() - r.min()], [r.max() - r.median()]],
                    fmt="D", color="0.45", capsize=5, ms=5,
                    label="16-subset ribbon\n(10 random 16 of 32,\ndefault)")
        ax.axhline(1.0, color="crimson", ls="--", lw=1.2)
        ax.set_xticks(ARMS)
        ax.set_xlabel("initial-design size n0")
        ax.set_ylabel("holdout RMSE / noise floor")
        ax.set_title(LABEL[obj])
        ax.grid(alpha=0.3)
        ax.set_ylim(bottom=0)
        boldticks(ax)
    axes[1].legend(fontsize=7, prop={"weight": "bold"})
    fig.suptitle("GP holdout error vs initial-design size (random_C, 48 "
                 "designs; red dashes = noise floor)", fontweight="bold")
    fig.tight_layout()
    save(fig, "n0_curve_holdout")


def fig_e0():
    e0 = pd.read_csv(os.path.join(HERE, "e0_table.csv")).set_index(
        "objective")
    objs = ["load_shed_mwh", "true_curtailment_mwh",
            "total_cost_less_synthetic_usd"]
    names = ["load shed", "curtailment", "cost (ls)"]
    x = np.arange(3)
    width = 0.26
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.2))
    colors = {16: "tab:gray", 32: "tab:blue", 48: "tab:green"}
    ax = axes[0]
    for i, arm in enumerate(ARMS):
        v = [e0.loc[o, f"rmse_over_floor_{arm}"] for o in objs]
        ax.bar(x + (i - 1) * width, v, width, color=colors[arm],
               label=f"{arm} points")
    ax.axhline(1.0, color="crimson", ls="--", lw=1.5, label="noise floor")
    ax.set_xticks(x)
    ax.set_xticklabels(names)
    ax.set_yscale("log")
    ax.set_ylabel("LOO RMSE / noise floor")
    ax.set_title("E0: the pi_1008 LOO table extended to 48")
    ax.legend(fontsize=8, prop={"weight": "bold"})
    ax.grid(alpha=0.3, axis="y")
    boldticks(ax)
    ax = axes[1]
    for i, arm in enumerate(ARMS):
        v = [e0.loc[o, f"loo_R2_{arm}"] for o in objs]
        ax.bar(x + (i - 1) * width, v, width, color=colors[arm],
               label=f"{arm} points")
    ax.set_xticks(x)
    ax.set_xticklabels(names)
    ax.set_ylabel("LOO R$^2$")
    ax.set_ylim(0, 1.05)
    ax.set_title("Surrogate skill by objective")
    ax.grid(alpha=0.3, axis="y")
    boldticks(ax)
    fig.tight_layout()
    save(fig, "e0_loo_16_32_48")


def fig_pit():
    z = json.load(open(os.path.join(HERE, "holdout_z.json")))["z"]
    fig, axes = plt.subplots(2, 3, figsize=(13, 7))
    grid = np.linspace(-4, 4, 200)
    for row, role in enumerate(["default", "winner"]):
        for colx, obj in enumerate(["shed", "curt", "cost_ls"]):
            ax = axes[row, colx]
            zz = np.asarray(z[f"{obj}|{role}|32"])
            ax.hist(zz, bins=np.arange(-4, 4.25, 0.5), density=True,
                    color="tab:blue" if role == "default" else "tab:red",
                    alpha=0.75, edgecolor="k")
            ax.plot(grid, np.exp(-grid ** 2 / 2) / np.sqrt(2 * np.pi),
                    "k--", lw=1.5)
            ax.axvline(-1.96, color="crimson", ls=":", lw=1)
            ax.axvline(1.96, color="crimson", ls=":", lw=1)
            cov = int((np.abs(zz) <= 1.96).sum())
            rms = float(np.sqrt(np.mean(zz ** 2)))
            ax.set_title(f"{LABEL[obj]} — {role} @32\n"
                         f"cov95 {cov}/48, rms_z {rms:.2f}", fontsize=9)
            ax.set_xlabel("standardized residual z")
            ax.set_ylabel("density")
            boldticks(ax)
    fig.suptitle("Holdout z-histograms at n0 = 32 (dashed = N(0,1); dotted "
                 "= 95% bounds)", fontweight="bold")
    fig.tight_layout()
    save(fig, "z_hist_32")


if __name__ == "__main__":
    fig_curve()
    fig_e0()
    fig_pit()
