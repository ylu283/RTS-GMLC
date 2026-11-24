"""Prompt 54 Part B v3.3: ERCOT_GP_STATUS.md + the drafted E-D7 row from an
`ercot_gp_partb.run` result. Never touches committed_configs.json."""
import datetime as _dt
import os

import numpy as np

from analysis.ercot_gp import ercot_gp_status as S
from analysis.ercot_gp import ercot_gp_partb as P


def _g(v, f="{:.4g}"):
    try:
        if v is None or (isinstance(v, float) and not np.isfinite(v)):
            return ""
    except TypeError:
        pass
    return f.format(v)


def _pf(b):
    return "PASS" if b else "FAIL"


def part_a_criterion(res):
    """The Part A pinned criterion, evaluated for continuity (v3.3 replaces it with n*)."""
    out = {}
    for obj in res["objs"]:
        c = res["checks"]
        r32 = c[(c.objective == obj) & (c.n == 32)].iloc[0]
        out[obj] = {"loo_cov95_32": int(r32["loo_cov95"]), "ratio": float(r32["rmse_ratio_vs_48"]),
                    "holdout_pass_32": bool(res["holdout"][obj][32]["pass"])}
    seated = [o for o in res["objs"] if res["roles"][o] == "seated"]
    ok = all(28 <= out[o]["loo_cov95_32"] <= 32 and out[o]["ratio"] <= 1.1 and out[o]["holdout_pass_32"] for o in seated)
    return out, (32 if ok else 48)


def pi_row(res, date=None):
    date = date or _dt.date.today().isoformat()
    com = res["committed"]["objectives"]
    seat = [o for o in res["objs"] if res["roles"][o] == "seated"]
    hold = "; ".join(f"{o} " + ", ".join(f"n={n}: {com[o]['holdout_cov95_by_tier'][str(n)][0]}/48 "
                                         f"{_pf(com[o]['holdout_pass_by_tier'][str(n)])}" for n in res["tiers"])
                     for o in res["objs"])
    return (f"| {date} | E-D7 | **ERCOT navigation tier (prompt 54 Part B v3.3)** | Recommendation **n0 = {res['n_star']}** "
            f"(n*, training-size study, seated {' · '.join(seat)}; rule: {P.N_STAR_RULE}) Holdout [43, 48]: {hold}. "
            f"Committed configs: " + "; ".join(f"{o} {com[o]['arm']}" for o in res["objs"])
            + f". Exposure {len(res['ledger'])} / 24; holdout RETIRED. Kay decides; 55 Part B waits on "
            "`committed_configs.json[\"E-D7_decided\"]`. | analysis/ercot_gp/ERCOT_GP_STATUS.md |")


def amendment_text(res):
    ns = res["n_star"]
    third = ns not in P.PLAN_TIERS
    return (
        "## AMENDMENT 2026-11-24b — prompt 54 Part B v3.3: training-size study and a holdout at a third tier n* "
        "(appendable, §10; DRAFT — the strategy session places it)\n\n"
        "**What changed.** (1) The LOO sufficiency curve at 16 / 24 / 32 / 40 / 48 (prompt 54 v3.1 §2.2) is replaced by a "
        f"training-size study at nested Sobol prefixes n ∈ {{{', '.join(str(n) for n in res['grid'])}}}, with the full plan-§5 "
        "arm set and selection rule at every n (LOO only). (2) The navigation-tier recommendation E-D7 is n*, the smallest n "
        "at which every seated objective has LOO cov95 inside binom.interval(0.90, n, 0.95), LOO RMSE_n / RMSE_48 ≤ 1.1 and "
        "ARD lengthscales stable to < 10 % between consecutive n (else 48); it replaces the Part A criterion (which also "
        "required the holdout pass at 32). (3) " + (
            f"**Holdout at a third tier n* = {ns}**: plan §4 / §5 grade each committed config once at the plan tiers 32 and "
            f"48; this run also graded once at n* = {ns}. " if third else
            f"n* = {ns} is a plan tier, so **no third-tier holdout was scored**; the admission of a third tier was not used. ")
        + f"Scorings {len(res['ledger'])} of 24 (4 objectives × {len(res['tiers'])} tiers; co-reported N4 / N1 graded like the "
        "seated V1 / E1). (4) The measured-floor arm is live with σ_c from prompt 63 (`ercot_noise_seed.json`, df 16) instead "
        "of the prompt-52 exact sd (identically 0). (5) n* was fixed before random_E was loaded; the holdout was never "
        "consulted for selection or for n*. committed_configs.json was written after the last scoring and retires the "
        "holdout.\n\n**What had been seen.** The n0_E objective values (E-D1b, rule v2, prompt 65) and the noise_seed_E "
        "chatter; no GP had been fitted on n0_E and random_E had not been read by any model before this run.")


def status_md(res, seed, ds, extra):
    objs, roles, tiers, ns = res["objs"], res["roles"], res["tiers"], res["n_star"]
    d, ch, com = res["study"], res["checks"], res["committed"]
    sites = res["sites"]
    lsc = [f"ls_u_{s}" for s in sites]
    sel = d[d["selected"]]
    L = ["# ERCOT_GP_STATUS — prompt 54 Part B (v3.3 addendum, 2026-11-24)", "",
         f"Design space `{os.path.basename(extra.get('design_space', ''))}` (contract_version {ds.get('contract_version')}, "
         f"objective_rule {ds.get('objective_rule')}). Seated: **{' · '.join(o for o in objs if roles[o] == 'seated')}**; "
         f"co-reported (fitted and graded identically, never seated): {' · '.join(o for o in objs if roles[o] != 'seated')}. "
         f"Data: n0_E grading tier 48 rows (Sobol 0–47, loader refusals {extra.get('n_refused')}, max R1 "
         f"{extra.get('r1_max')} MWh, max R2 {_g(extra.get('r2_max'), '{:.1f}')} MWh); random_E 48 rows, read only by the "
         f"holdout grader (refusals {extra.get('n_refused_random')}, max R1 {extra.get('r1_max_random')}, max R2 "
         f"{_g(extra.get('r2_max_random'), '{:.1f}')}). Environment bogp-botorch; wall {res['wall_s'] / 60:.1f} min.", "",
         f"> Disclosure (AMENDMENT 2026-11-24): {ds.get('disclosure', '')}", "",
         f"**E-D7 recommendation: n\\* = {ns}** (Kay decides). Holdout tiers {tiers}; exposure {len(res['ledger'])} / 24; "
         "`committed_configs.json` written after the last scoring — the holdout is RETIRED.", "",
         "## 1. Per-objective summary (selected arm by the plan-§5 rule at each n)", "",
         "| objective | role | n | selected arm | LOO NLPD | LOO RMSE | LOO cov95 / n [bar] | holdout cov95 / 48 [43, 48] | holdout RMSE | lengthscales u (" + ", ".join(sites) + ") | outputscale sd (t) | noise sd | noise / σ_c |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    show = sorted(set(tiers))
    for obj in objs:
        for n in show:
            r = sel[(sel.objective == obj) & (sel.n == n)].iloc[0]
            h = res["holdout"][obj][n]
            L.append(f"| {obj} | {roles[obj]} | {n}{' (n*)' if n == ns else ''} | {r['arm']} | {r['loo_nlpd']:.3f} | "
                     f"{r['loo_rmse']:.4g} | {int(r['loo_cov95'])} / {n} [{int(r['bar_lo'])}, {int(r['bar_hi'])}] "
                     f"{'in' if r['cov_in_bar'] else '**out**'} | {h['metrics']['cov95']} / 48 **{_pf(h['pass'])}** | "
                     f"{h['metrics']['rmse']:.4g} | {', '.join(f'{v:.3g}' for v in r[lsc])} | {r['outputscale_sd_t']:.4g} | "
                     f"{r['noise_sd_raw']:.4g}{' (at floor)' if r['noise_at_floor'] else ''} | {_g(r['noise_over_sigma_c'], '{:.3g}')} |")
    L += ["", "σ_c = prompt-63 chatter sd (`ercot_noise_seed.json`, df 16): "
          + "; ".join(f"{o} {res['sigmas'][o]:.4g} (measured arm {'included' if res['uses'][o] else 'not included'})" for o in objs)
          + ". Arm sets: " + "; ".join(f"{o}: {', '.join(a.name for a in res['arms'][o])}" for o in objs)
          + " (log1p arms enter iff min y ≥ 0 and max / max(min, 1) > 10 on the 48 grading rows).", ""]

    L += ["## 2. Navigation tier n* (E-D7 recommendation)", "", f"**Rule (pinned in code before the fit):** {P.N_STAR_RULE}", "",
          f"**Reason:** {res['reason']}", "",
          "| objective | role | n | arm | cov95 [bar] (1) | RMSE_n / RMSE_48 (2) | max ls change (3) | median ls change (descr.) | all met |",
          "|---|---|---|---|---|---|---|---|---|"]
    for _, r in ch.iterrows():
        L.append(f"| {r['objective']} | {r['role']} | {r['n']} | {r['arm']} | {r['loo_cov95']} [{r['bar_lo']}, {r['bar_hi']}] "
                 f"{'ok' if r['c1_cov_in_bar'] else 'x'} | {r['rmse_ratio_vs_48']:.3f} {'ok' if r['c2_rmse_ok'] else 'x'} | "
                 f"{_g(r['ls_rel_change_max'], '{:.1%}')} {'ok' if r['c3_ls_stable'] else 'x'} | {_g(r['ls_rel_change_median'], '{:.1%}')} | "
                 f"{'**yes**' if r['all_ok'] else ''} |")
    alt = res["alt"]
    L += ["", "**What would change the choice (descriptive, never binding):** "
          f"with the co-reported ids included n would be {alt['co_reported_included']}; each seated id alone: "
          + ", ".join(f"{o} {v}" for o, v in alt["seated_each"].items())
          + "; each co-reported id alone: " + ", ".join(f"{o} {v}" for o, v in alt["co_reported_alone"].items())
          + f"; without the lengthscale condition {alt['without_lengthscale_condition']}; with the median (not max) "
          f"lengthscale change {alt['lengthscale_median_not_max']}; coverage alone {alt['cov_only']}.", ""]
    pa, pa_n = part_a_criterion(res)
    L += [f"Part A criterion (pinned 11-14, verbatim, evaluated for continuity; v3.3 replaces it): \"{S.SUFFICIENCY_CRITERION}\" "
          "→ seated: " + "; ".join(f"{o} cov95@32 {pa[o]['loo_cov95_32']}, ratio {pa[o]['ratio']:.3f}, holdout@32 "
                                   f"{_pf(pa[o]['holdout_pass_32'])}" for o in objs if roles[o] == "seated")
          + f" → it would recommend **{pa_n}**.", ""]

    L += ["## 3. Training-size study (plan-§5 arms at every n; LOO only)", "",
          "| objective | n | arm | LOO NLPD | Δ vs default (paired se) | beats default | LOO cov95 [bar] | LOO RMSE | RMSE % range | outputscale sd (t) | noise sd | noise / σ_c | selected |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for _, r in d.iterrows():
        L.append(f"| {r['objective']} | {r['n']} | {r['arm']} | {r['loo_nlpd']:.3f} | {r['diff_vs_default']:+.3f} ({r['paired_se']:.3f}) | "
                 f"{'yes' if r['beats_default'] else ''} | {int(r['loo_cov95'])} [{int(r['bar_lo'])}, {int(r['bar_hi'])}] | "
                 f"{r['loo_rmse']:.4g} | {r['loo_rmse_pct_range']:.2f} | {r['outputscale_sd_t']:.4g} | "
                 f"{r['noise_sd_raw']:.4g}{' (floor)' if r['noise_at_floor'] else ''} | {_g(r['noise_over_sigma_c'], '{:.3g}')} | "
                 f"{'**yes**' if r['selected'] else ''} |")
    L += ["", "ARD lengthscales (u units) of the SELECTED arm vs n (descriptive; in u-space they scale with 1 / gen_pmax):", "",
          "| objective | n | arm | " + " | ".join(f"site {s}" for s in sites) + " |", "|---|---|---|" + "---|" * len(sites)]
    for _, r in sel.iterrows():
        L.append(f"| {r['objective']} | {r['n']} | {r['arm']} | " + " | ".join(f"{v:.3g}" for v in r[lsc]) + " |")
    x = res["exploratory"]
    if len(x):
        L += ["", "### Exploratory diagnostic arms (reported, NEVER committed; not part of selection)", "",
              "| objective | n | arm | LOO NLPD | Δ vs selected plan arm (paired se) | LOO cov95 [bar] | LOO RMSE | noise sd | lengthscales u |",
              "|---|---|---|---|---|---|---|---|---|"]
        for _, r in x.iterrows():
            L.append(f"| {r['objective']} | {r['n']} | {r['arm']} | {r['loo_nlpd']:.3f} | {r['diff_vs_selected']:+.3f} ({r['paired_se']:.3f}) "
                     f"vs {r['vs_selected_arm']} | {int(r['loo_cov95'])} [{int(r['bar_lo'])}, {int(r['bar_hi'])}] | {r['loo_rmse']:.4g} | "
                     f"{r['noise_sd_raw']:.4g} | {', '.join(f'{v:.3g}' for v in r[lsc])} |")

    L += ["", f"## 4. Holdout (random_E, i.i.d. 48; bar [43, 48] = binom.interval(0.90, 48, 0.95); once per objective per tier)", "",
          "| objective | role | n | arm | cov95 / 48 | pass | RMSE | RMSE % range | NLPD | rms z | mean z | Spearman | median 95 % half-width | latent share | exposure row |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for _, r in res["hold_df"].iterrows():
        L.append(f"| {r['objective']} | {r['role']} | {r['n']} | {r['arm']} | {r['holdout_cov95']} / 48 | **{_pf(r['holdout_pass'])}** | "
                 f"{r['holdout_rmse']:.4g} | {r['holdout_rmse_pct_range']:.2f} | {r['holdout_nlpd']:.3f} | {r['holdout_rms_z']:.3f} | "
                 f"{r['holdout_mean_z']:+.3f} | {r['holdout_spearman']:.3f} | {r['median_95_halfwidth_raw']:.4g} | "
                 f"{r['latent_share_median']:.3f} | {r['exposure_row']} |")
    L += ["", "Independence disclosure (plan §4): the 48 residuals share one fitted model, so the binomial region treats them as "
          "independent. This is an approximation. A failing objective is recorded; no re-selection and no extra scoring "
          "followed.", "", "Parity: `figs/fig_parity_holdout.png` (dual band: total 95 % incl. noise, latent 95 %).", ""]

    L += ["## 5. Noise cross-check vs σ_c (descriptive only; adds no arm)", "",
          "| objective | n | arm | inferred noise sd | σ_c [95 % CI] | inferred / σ_c | inside CI | inferred / per-level sd (4 seed designs) | seed Δ: mean abs z / max abs z / frac abs z > 1.96 | 63 trigger |",
          "|---|---|---|---|---|---|---|---|---|---|"]
    for _, r in res["cross"].iterrows():
        L.append(f"| {r['objective']} | {r['n']} | {r['arm']} | {r['inferred_noise_sd_raw']:.4g}{' (at floor)' if r['noise_at_floor'] else ''} | "
                 f"{r['sigma_c']:.4g} [{r['sigma_c_ci95_lo']:.4g}, {r['sigma_c_ci95_hi']:.4g}] | {r['ratio_inferred_over_sigma_c']:.3g} | "
                 f"{'yes' if r['inside_sigma_c_ci95'] else 'no'} | {', '.join(f'{v:.3g}' for v in r['ratio_inferred_over_level_sd'])} | "
                 f"{r['seed_delta_z_mean_abs']:.3g} / {r['seed_delta_z_max_abs']:.3g} / {r['seed_delta_frac_abs_z_gt_1p96']:.2f} | "
                 f"{'FIRES — ' + str(r['trigger_verdict']) if r['trigger_fires'] else 'no'} |")
    L += ["", "Seed Δ = the 16 solver-seed deltas of prompt 63 (two-run scale, sd ≈ √2·σ_c), standardized by the inferred sd. "
          "A firing 63 trigger (level-dependent chatter) is reported; any model change needs a plan amendment.", ""]

    m = res.get("mech")
    if m:
        from analysis.ercot_gp import ercot_gp_mechanism as M
        L += [M.mechanism_md(m["facts"], m["null"], m["flags"]), ""]
        L += ["### Direction and scale (descriptive)", "", "| objective | Spearman(y, total MW T) on 48 rows | grading range | B_j (contract addendum bar) | range / B_j | committed arm | refit on 48 |",
              "|---|---|---|---|---|---|---|"]
        for o, v in m["direction"].items():
            L.append(f"| {o} | {v['spearman_y_vs_T']:+.3f} | {v['range']:.4g} | {_g(v['B_j'])} | {_g(v['range_over_B'], '{:.1f}')} | "
                     f"{m['arms'][o].name} | {m['refit'][o]} |")
        if m["lc"] is not None:
            lc = m["lc"]
            labs = list(dict.fromkeys(lc["label"]))
            L += ["", "### Prompt-61 residual row (descriptive; no bar, no pass/fail, no exposure, no input to any decision)", "",
                  "Standardized residuals z = (y − μ) / sd (predictive sd incl. noise) of the 9 `location_contrast_E` designs under "
                  "the committed config fitted on the 48 grading rows.", "",
                  "| objective | " + " | ".join(labs) + " | mean abs z | n abs z > 1.96 |", "|---|" + "---|" * (len(labs) + 2)]
            for o in lc["objective"].unique():
                z = lc[lc.objective == o].set_index("label").loc[labs, "z"].to_numpy(float)
                L.append(f"| {o} | " + " | ".join(f"{v:+.2f}" for v in z) + f" | {np.mean(np.abs(z)):.2f} | {int((np.abs(z) > 1.96).sum())} |")
        L += [""]

    L += ["## 7. Committed configs (`committed_configs.json`, contract §6.2 + v3.3 keys)", "",
          "| objective | seated | arm | cfg | floor | measured floor used | LOO NLPD at n* | holdout cov95 by tier | exposure rows |",
          "|---|---|---|---|---|---|---|---|---|"]
    for o, c in com["objectives"].items():
        L.append(f"| {o} | {c['seated']} | {c['arm']} | {'/'.join(c['cfg'])} | {_g(c['floor'])} | {c['measured_floor_used']} | "
                 f"{c['loo_nlpd_mean']:.3f} | " + ", ".join(f"{n}: {v[0]}/48" for n, v in c["holdout_cov95_by_tier"].items())
                 + f" | {c['exposure_rows']} |")
    L += ["", f"Exposure ledger `exposure_ledger.csv`: {len(res['ledger'])} of 24 scorings; retired.", "",
          "## 8. Drafted pi-agenda row E-D7 (Kay decides; 55 Part B waits on it)", "", "```", pi_row(res), "```", "",
          "## 9. What changed vs plan (draft §10 amendment text — NOT appended to the plan; the strategy session places it)", "",
          "```", amendment_text(res), "```", "",
          "## 10. Deviations and limits", "",
          "- Hyperparameters are the house fit (bogp `train_gp`: Adam, 700 epochs, lr 0.01, from gpytorch's default init), "
          "i.e. the MLE as the house computes it; it is not a converged multi-start optimum. The lengthscale-stability "
          "condition therefore also measures optimizer path-dependence.",
          "- Lengthscale stability compares the SELECTED arm at consecutive n; an arm switch between n − 4 and n counts as a change.",
          "- The holdout at each tier scores the arm selected at that n (the Part A semantics); committed_configs.json "
          "carries the arm selected at n* and lists every tier.",
          "- Co-reported N4 / N1: fitted, graded and exposed like the seated ids (4 objectives × tiers); never binding for n*; "
          "mechanism flags issued for the seated ids only (their shares are printed).",
          "- The mechanism null is built on V1 (wave D) and its scale-free thresholds are applied to every objective (pinned 11-17).",
          "- log1p arms: none or some may be absent by the plan inclusion rule (see §1).", "",
          "## 11. Figures", ""] + [f"- `{os.path.relpath(f, res['out_dir'])}`" for f in res["figs"]] + [""]
    return "\n".join(L)


def write_all(res, seed, ds, args):
    extra = dict(res.get("extra", {}))
    extra["design_space"] = args.design_space
    md = status_md(res, seed, ds, extra)
    with open(os.path.join(res["out_dir"], "ERCOT_GP_STATUS.md"), "w") as f:
        f.write(md + "\n")
    with open(os.path.join(res["out_dir"], "pi_agenda_E-D7_draft.md"), "w") as f:
        f.write(pi_row(res) + "\n")
    return md
