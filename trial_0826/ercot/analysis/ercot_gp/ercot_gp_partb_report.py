"""Prompt 54 Part B (v3.3 + plan AMENDMENT 2026-11-24b): ERCOT_GP_STATUS.md and the E-D7
decision row from an `ercot_gp_partb.run` result (house fit) and, when present, the fit-v2
result (`ercot_gp_partb.run_v2`). Never touches committed_configs.json."""
import datetime as _dt
import os

import numpy as np
import pandas as pd

from analysis.ercot_gp import ercot_gp_status as S
from analysis.ercot_gp import ercot_gp_partb as P

POOL_V2 = os.path.join(P.ERCOT, "analysis", "pool", "pool_ed1b_v2.csv")
UNIT = {"V1": "MWh", "E1": "$", "N4": "h", "N1": "line-h"}
LONG_SHA = "65179e1"


def _g(v, f="{:.4g}"):
    try:
        if v is None or (isinstance(v, float) and not np.isfinite(v)):
            return ""
    except TypeError:
        pass
    return f.format(v)


def _pf(b):
    return "PASS" if b else "FAIL"


def _nat(v, obj):
    """Natural-unit format: $ in $M, the rest with thousands separators."""
    if obj == "E1":
        return f"${v / 1e6:,.2f}M"
    return f"{v:,.0f} {UNIT.get(obj, '')}".strip() if abs(v) >= 100 else f"{v:,.1f} {UNIT.get(obj, '')}".strip()


def b_rule_v2(objs, path=POOL_V2):
    """Rule-v2 bar B_j (AMENDMENT 2026-11-24 item 1) from pool_ed1b_v2.csv."""
    d = pd.read_csv(path).set_index("id")
    return {o: float(d.loc[o, "B_j"]) for o in objs if o in d.index}


def _sel(df):
    return df[df["selected"]]


def _row(df, obj, n):
    s = _sel(df)
    return s[(s.objective == obj) & (s.n == n)].iloc[0]


def long_fit_caveat(res):
    """Two sentences computed from the house and long-fit selected arms at n = 48."""
    ldf = res.get("long")
    if ldf is None or not len(ldf):
        return ""
    seat = [o for o in res["objs"] if res["roles"][o] == "seated"]
    cut, band = {}, {}
    for o in res["objs"]:
        h, g = _row(res["study"], o, 48), _row(ldf, o, 48)
        cut[o] = 1.0 - g["loo_rmse"] / h["loo_rmse"]
        band[o] = h["median_95_halfwidth_raw"] / g["median_95_halfwidth_raw"]
    ids = [o for o in res["objs"] if o != "N1"]
    lo, hi = min(cut[o] for o in ids), max(cut[o] for o in ids)
    return (f"A {res.get('long_epochs', P.LONG_EPOCHS):,}-step fit of the same arms gives {100 * lo:.0f}–{100 * hi:.0f} % "
            f"lower LOO RMSE ({', '.join(ids)}" + (f"; N1 {100 * cut['N1']:.0f} %" if "N1" in cut else "") + ") and "
            + " to ".join(f"{band[o]:.1f}× ({o})" for o in sorted(seat, key=lambda o: band[o]))
            + " narrower LOO bands at n = 48. The house fit therefore over-states the noise and the band width. "
            "Plan AMENDMENT 2026-11-24b sets fit definition v2; an objective keeps the house fit only where its v2 "
            "config fails the holdout (§13).")


def raw_ls_span(res, n=48):
    s = _sel(res["study"])
    s = s[s.n == n]
    cols = [c for c in s.columns if c.startswith("ls_raw_")]
    if not cols:
        return None
    v = s[cols].to_numpy(float)
    return float(v.min()), float(v.max())


def mech_lc_sentence(res, obj=None):
    m = res.get("mech")
    if not m or m.get("lc") is None:
        return ""
    obj = obj or res["objs"][0]
    lc = m["lc"]
    z = lc[lc.objective == obj].set_index("label")["z"]
    big = z[np.abs(z) > 1.96]
    return (f"{obj} has |z| > 1.96 on {len(big)} of {len(z)} designs: "
            + ", ".join(f"{k} {v:+.2f}" for k, v in big.sort_values(key=np.abs, ascending=False).items())
            + f"; {int((z > 0).sum())} of {len(z)} {obj} z are positive (mean {z.mean():+.2f}).")


# --------------------------------------------------------------------------
# E-D7 decision row
# --------------------------------------------------------------------------
def pi_rows(res, res2=None, date=None):
    date = date or _dt.date.today().isoformat()
    ch = res["checks"]
    seat = [o for o in res["objs"] if res["roles"][o] == "seated"]
    r = {(o, n): ch[(ch.objective == o) & (ch.n == n)].iloc[0] for o in seat for n in (32, 40, 44)}
    hold = {o: {n: res["holdout"][o][n] for n in res["tiers"]} for o in res["objs"]}

    def rat(n):
        return " / ".join(f"{o} {r[(o, n)]['rmse_ratio_vs_48']:.3f}" for o in seat)
    v2 = ""
    if res2 is not None:
        c2 = res2["checks"]
        q = {o: float(c2[(c2.objective == o) & (c2.n == 44)]["rmse_ratio_vs_48"].iloc[0]) for o in seat}
        v2 = (f" Fit v2 (AMENDMENT 2026-11-24b): n* = {res2['n_star']}; ratios at n = 44 "
              + ", ".join(f"{o} {v:.3f}" for o, v in q.items()) + ".")
    row1 = (
        f"| {date} | E-D7 | **ERCOT navigation tier n0 (prompt 54 Part B)** | Options: **(a) n0 = 48 — recommended**; "
        f"(b) n0 = 32; (c) n0 = 44, only if the RMSE-ratio bar is relaxed to ≈ 1.12. Numbers (house fit): LOO RMSE_n / "
        f"RMSE_48 at n = 32: {rat(32)}; n = 40: {rat(40)}; n = 44: {rat(44)} (bar 1.1). Holdout [43, 48] (n = 32 / 48): "
        + ", ".join(f"{o} {hold[o][32]['metrics']['cov95']} / {hold[o][48]['metrics']['cov95']} "
                    f"{'PASS' if hold[o][32]['pass'] and hold[o][48]['pass'] else 'FAIL at a tier'}" for o in seat)
        + "." + v2 + " **Cost: no new simulations** (the 48 n0_E runs are "
        "landed; option (b) or (c) only uses fewer of them as the starting set). **What changes it:** a bar change on the "
        "RMSE ratio (1.12 → 44); a fit-definition change that moves the ratios; a decision to start the BO earlier "
        "and accept a less accurate start. Note: n0 = 48 means no tier below 48 meets the rule; whether 48 itself "
        "suffices is untested (LOO RMSE still falls by ≈ 1.3× from n = 40 to 48). | analysis/ercot_gp/ERCOT_GP_STATUS.md §0, §2 |")
    if res2 is None:
        fit = ("Fit definition v2 (plan AMENDMENT 2026-11-24b: float64 MAP, L-BFGS-B, 16 restarts) is adopted by the "
               "amendment; its results replace the house fit where the v2 config passes the holdout.")
    else:
        com = res2["committed"]["objectives"]
        fit = ("Fit definition v2 (plan AMENDMENT 2026-11-24b) — results: "
               + "; ".join(f"{o} {com[o]['fit_definition']} ({com[o]['arm']}"
                           + (f", holdout {com[o]['holdout_v2']['cov95']}/48 {_pf(com[o]['holdout_v2']['pass'])}" if com[o].get('holdout_v2') else "")
                           + ")" for o in res2["seated"])
               + f". Exposure {res2['exposure']} / 24; holdout retired again.")
    row2 = (f"| {date} | E-D7 (fit item) | **GP fit definition for 55 (separate from the tier)** | {fit} 55 fits its "
            "acquisition GP with the same definition as the committed (graded) one. Kay notes it; no decision needed "
            "unless a v2 config failed. | analysis/ercot_gp/ERCOT_GP_STATUS.md §13 |")
    return row1, row2


# --------------------------------------------------------------------------
# the page
# --------------------------------------------------------------------------
def pi_block(res, res2, B):
    objs, roles = res["objs"], res["roles"]
    ch = res["checks"]
    L = ["## 0. Answers for the PI", ""]
    ok = [o for o in objs if all(res["holdout"][o][n]["pass"] for n in (32, 48))]
    bad = [o for o in objs if o not in ok]
    L += ["**Q1 — Are the GP's 95 % bands honest (calibration)?** "
          + (f"Yes for {', '.join(ok)} (holdout inside [43, 48] at n = 32 and 48). " if ok else "")
          + " ".join(f"Not for {o}: it fails at n = "
                     + ", ".join(str(n) for n in (32, 48) if not res["holdout"][o][n]["pass"]) + "." for o in bad), "",
          "| objective | role | n | LOO cov95 / n [bar] | holdout cov95 / 48 [43, 48] | holdout rms z |", "|---|---|---|---|---|---|"]
    for o in objs:
        for n in (32, 48):
            r = _row(res["study"], o, n)
            h = res["holdout"][o][n]
            L.append(f"| {o} | {roles[o]} | {n} | {int(r['loo_cov95'])} / {n} [{int(r['bar_lo'])}, {int(r['bar_hi'])}] | "
                     f"{h['metrics']['cov95']} / 48 {_pf(h['pass'])} | {h['metrics']['rms_z']:.2f} |")
    rz = [res["holdout"][o][n]["metrics"]["rms_z"] for o in ok for n in (32, 48)]
    L += ["", "rms z < 1 means the bands are wider than the errors (conservative)."
          + (f" The house fit gives rms z {min(rz):.2f}–{max(rz):.2f} for {', '.join(ok)}." if rz else ""), ""]
    L += ["**Q2 — How accurate is it?** LOO RMSE (holdout RMSE in brackets), in natural units, in units of the rule-v2 "
          "noise bar B_j (`pool_ed1b_v2.csv`) and in % of the grading-tier range.", "",
          "| objective | B_j | n = 32: RMSE | in B_j | % range | n = 48: RMSE | in B_j | % range |", "|---|---|---|---|---|---|---|---|"]
    for o in objs:
        yr = res["y_range"][o]
        cells = []
        for n in (32, 48):
            r = _row(res["study"], o, n)
            h = res["holdout"][o][n]["metrics"]["rmse"]
            cells += [f"{_nat(r['loo_rmse'], o)} [{_nat(h, o)}]", f"{r['loo_rmse'] / B[o]:.2f} [{h / B[o]:.2f}]" if o in B else "",
                      f"{100 * r['loo_rmse'] / yr:.1f} [{100 * h / yr:.1f}]"]
        L.append(f"| {o} | {_nat(B[o], o) if o in B else ''} | " + " | ".join(cells) + " |")
    L += ["", "The % range denominator here is the 48-row grading-tier range of y for every cell (one denominator).", ""]
    seat = [o for o in objs if roles[o] == "seated"]
    r44 = {o: ch[(ch.objective == o) & (ch.n == 44)].iloc[0]["rmse_ratio_vs_48"] for o in seat}
    r40 = {o: ch[(ch.objective == o) & (ch.n == 40)].iloc[0]["rmse_ratio_vs_48"] for o in seat}
    L += [f"**Q3 — How many starting runs (n\\*, the navigation tier)?** **n\\* = {res['n_star']}.** No tier below 48 "
          f"meets the rule. The ratio LOO RMSE_n / RMSE_48 is above 1.1 at every n < 48 for the seated ids (n = 44: "
          + ", ".join(f"{o} {v:.3f}" for o, v in r44.items()) + "; n = 40: " + ", ".join(f"{o} {v:.3f}" for o, v in r40.items())
          + "). Whether 48 itself suffices is untested: "
          f"LOO RMSE still falls by ≈ {np.mean(list(r40.values())):.1f}× from n = 40 to 48."
          + (f" Under fit v2 (§13) n\\* = {res2['n_star']}." if res2 is not None else ""), ""]
    L += ["**Read this before the BO.** " + long_fit_caveat(res)
          + " The committed fit definition per objective is in §13 and `committed_configs.json` (`fit_definition`).", ""]
    if res2 is not None:
        com2 = res2["committed"]["objectives"]
        parts = []
        for o in res2["seated"]:
            hv = com2[o]["holdout_v2"]
            parts.append(f"{o}: v2 {res2['winners'][o][48]['arm'].name} holdout {hv['cov95']} / 48 (rms z {hv['rms_z']:.2f}) "
                         f"{_pf(hv['pass'])} → committed **{com2[o]['fit_definition']}**")
        L += ["**Fit v2 outcome (AMENDMENT 2026-11-24b, one re-open round, 2 scorings, exposure "
              f"{res2['exposure']} / 24).** " + "; ".join(parts) + ". 55 fits each acquisition GP with the definition "
              "committed for that objective. A v2 config that fails the bar keeps the house-fit commit (pre-registered "
              "fallback); we did not re-select and did not score again.", ""]
    for o in bad:
        fails = [n for n in (32, 48) if not res["holdout"][o][n]["pass"]]
        L += [f"**{o} ({roles[o]}) FAILS the holdout at n = {', '.join(map(str, fails))}** ("
              + ", ".join(f"n = {n}: {res['holdout'][o][n]['metrics']['cov95']} / 48" for n in (32, 48))
              + f"; bar [43, 48]). {'It is not seated. ' if roles[o] != 'seated' else ''}We recorded the failure. "
              "We did not re-select and did not score again.", ""]
    span = raw_ls_span(res)
    L += ["**Notes.**", "",
          f"- Mechanism (descriptive): {mech_lc_sentence(res)}",
          f"- Provenance: the long-fit diagnostic ({LONG_SHA}) was coded 7 minutes after the holdout was scored. It was "
          "never scored or committed. It motivates the fit change (AMENDMENT 2026-11-24b).",
          (f"- House-fit lengthscales at n = 48: raw parameter {span[0]:.1f}–{span[1]:.1f}; Adam can move it by at most "
           "≈ 7 from 0 in 700 steps at lr 0.01 (`ls_raw_*` in `ercot_gp_status.csv`)." if span else ""),
          "- The rule-v2 disclosure is in §12.", ""]
    return L


def status_md(res, seed, ds, extra, res2=None):
    objs, roles, tiers, ns = res["objs"], res["roles"], res["tiers"], res["n_star"]
    d, ch, com = res["study"], res["checks"], res["committed"]
    sites = res["sites"]
    lsc = [f"ls_u_{s}" for s in sites]
    sel = _sel(d)
    B = b_rule_v2(objs)
    L = ["# ERCOT_GP_STATUS — prompt 54 Part B (v3.3 addendum; plan AMENDMENT 2026-11-24b)", "",
         f"Design space `{os.path.basename(extra.get('design_space', ''))}` (contract_version {ds.get('contract_version')}, "
         f"objective_rule {ds.get('objective_rule')}). Seated: **{' · '.join(o for o in objs if roles[o] == 'seated')}**. "
         f"Co-reported (fitted and graded like the seated ids, never seated): {' · '.join(o for o in objs if roles[o] != 'seated')}. "
         f"Data: n0_E grading tier, 48 rows (Sobol 0–47; loader refusals {extra.get('n_refused')}; max R1 "
         f"{extra.get('r1_max')} MWh; max R2 {_g(extra.get('r2_max'), '{:.1f}')} MWh). random_E: 48 rows, read only by the "
         f"holdout grader (refusals {extra.get('n_refused_random')}; max R1 {extra.get('r1_max_random')}; max R2 "
         f"{_g(extra.get('r2_max_random'), '{:.1f}')}). Environment bogp-botorch. "
         f"House-fit page build {res['wall_s'] / 60:.1f} min"
         + (f"; fit-v2 run {res2['wall_s'] / 60:.1f} min" if res2 is not None else "") + ".", ""]
    L += pi_block(res, res2, B)
    L += ["## 1. Per-objective summary, house fit (selected arm by the plan-§5 rule at each n)", "",
          "| objective | role | n | selected arm | LOO NLPD | LOO RMSE | LOO cov95 / n [bar] | holdout cov95 / 48 [43, 48] | holdout RMSE | lengthscales u (" + ", ".join(sites) + ") | outputscale sd (t) | noise sd | noise / σ_c |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for obj in objs:
        for n in sorted(set(tiers)):
            r = _row(d, obj, n)
            h = res["holdout"][obj][n]
            L.append(f"| {obj} | {roles[obj]} | {n}{' (n*)' if n == ns else ''} | {r['arm']} | {r['loo_nlpd']:.3f} | "
                     f"{r['loo_rmse']:.4g} | {int(r['loo_cov95'])} / {n} [{int(r['bar_lo'])}, {int(r['bar_hi'])}] "
                     f"{'in' if r['cov_in_bar'] else '**out**'} | {h['metrics']['cov95']} / 48 **{_pf(h['pass'])}** | "
                     f"{h['metrics']['rmse']:.4g} | {', '.join(f'{v:.3g}' for v in r[lsc])} | {r['outputscale_sd_t']:.4g} | "
                     f"{r['noise_sd_raw']:.4g}{' (at floor)' if r['noise_at_floor'] else ''} | {_g(r['noise_over_sigma_c'], '{:.3g}')} |")
    L += ["", "σ_c = prompt-63 chatter sd (`ercot_noise_seed.json`, df 16): "
          + "; ".join(f"{o} {res['sigmas'][o]:.4g} (measured arm {'included' if res['uses'][o] else 'not included'})" for o in objs)
          + ". Arm sets: " + "; ".join(f"{o}: {', '.join(a.name for a in res['arms'][o])}" for o in objs) + ".", ""]

    L += ["## 2. Navigation tier n* (E-D7 recommendation)", "", f"**Rule (pinned in code before the fit):** {P.N_STAR_RULE}", "",
          f"**Result: n\\* = {ns}.** Per-n checks for every objective (seated ids decide):", "",
          "| objective | role | n | arm | cov95 [bar] (1) | RMSE_n / RMSE_48 (2) | max ls change (3) | median ls change (descr.) | all met |",
          "|---|---|---|---|---|---|---|---|---|"]
    for _, r in ch.iterrows():
        L.append(f"| {r['objective']} | {r['role']} | {r['n']} | {r['arm']} | {r['loo_cov95']} [{r['bar_lo']}, {r['bar_hi']}] "
                 f"{'ok' if r['c1_cov_in_bar'] else 'x'} | {r['rmse_ratio_vs_48']:.3f} {'ok' if r['c2_rmse_ok'] else 'x'} | "
                 f"{_g(r['ls_rel_change_max'], '{:.1%}')} {'ok' if r['c3_ls_stable'] else 'x'} | {_g(r['ls_rel_change_median'], '{:.1%}')} | "
                 f"{'**yes**' if r['all_ok'] else ''} |")
    alt = res["alt"]
    L += ["", "**What would change the choice (descriptive, never binding):** "
          f"with the co-reported ids included: {alt['co_reported_included']}; each seated id alone: "
          + ", ".join(f"{o} {v}" for o, v in alt["seated_each"].items())
          + "; each co-reported id alone: " + ", ".join(f"{o} {v}" for o, v in alt["co_reported_alone"].items())
          + f"; without the lengthscale condition: {alt['without_lengthscale_condition']}; with the median (not max) "
          f"lengthscale change: {alt['lengthscale_median_not_max']}; coverage alone: {alt['cov_only']}"
          + (f"; the same rule on the exploratory long fit: {alt['long_fit_descriptive']['n_star']}" if 'long_fit_descriptive' in alt else "")
          + ". n\\* = 48 means that no tier below 48 suffices. Whether 48 suffices is untested.", ""]

    L += ["## 3. Training-size study, house fit (plan-§5 arms at every n; LOO only)", "",
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
    ldf = res.get("long")
    if ldf is not None and len(ldf):
        ep = res.get("long_epochs")
        lsel = _sel(ldf)
        L += ["", f"### Exploratory: the same arms and selection rule with a longer fit (Adam {ep:,} steps; NEVER committed, never holdout-scored)", "",
              long_fit_caveat(res), "",
              f"Provenance: this diagnostic ({LONG_SHA}) was coded 7 minutes after the holdout was scored.", "",
              "| objective | n | house arm | house LOO NLPD | long arm | long LOO NLPD | house / long LOO RMSE | house / long cov95 [bar] | house / long noise / σ_c | long lengthscales u |",
              "|---|---|---|---|---|---|---|---|---|---|"]
        for obj in objs:
            for n in res["grid"]:
                h = _row(d, obj, n)
                g = lsel[(lsel.objective == obj) & (lsel.n == n)].iloc[0]
                L.append(f"| {obj} | {n} | {h['arm']} | {h['loo_nlpd']:.3f} | {g['arm']} | {g['loo_nlpd']:.3f} | "
                         f"{h['loo_rmse']:.4g} / {g['loo_rmse']:.4g} | {int(h['loo_cov95'])} / {int(g['loo_cov95'])} [{int(h['bar_lo'])}, {int(h['bar_hi'])}] | "
                         f"{_g(h['noise_over_sigma_c'], '{:.3g}')} / {_g(g['noise_over_sigma_c'], '{:.3g}')} | {', '.join(f'{v:.3g}' for v in g[lsc])} |")
        ln = res.get("long_n_star")
        if ln is not None:
            L += ["", f"The n\\* rule on the long fit (descriptive only): **{ln[0]}** (co-reported included: "
                  f"{ln[2]['co_reported_included']}; without the lengthscale condition: {ln[2]['without_lengthscale_condition']}). "
                  "Figure: `figs/fig_house_vs_longfit.png`."]
    L += ["", f"## 4. Holdout, house fit (random_E, i.i.d. 48; bar [43, 48] = binom.interval(0.90, 48, 0.95); once per objective per tier)", "",
          "| objective | role | n | arm | cov95 / 48 | pass | RMSE | RMSE % range | NLPD | rms z | mean z | Spearman | median 95 % half-width | latent share | exposure row |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for _, r in res["hold_df"].iterrows():
        L.append(f"| {r['objective']} | {r['role']} | {r['n']} | {r['arm']} | {r['holdout_cov95']} / 48 | **{_pf(r['holdout_pass'])}** | "
                 f"{r['holdout_rmse']:.4g} | {r['holdout_rmse_pct_range']:.2f} | {r['holdout_nlpd']:.3f} | {r['holdout_rms_z']:.3f} | "
                 f"{r['holdout_mean_z']:+.3f} | {r['holdout_spearman']:.3f} | {r['median_95_halfwidth_raw']:.4g} | "
                 f"{r['latent_share_median']:.3f} | {r['exposure_row']} |")
    L += ["", "RMSE % range denominators: the LOO column (§3) divides by the range of the n training rows; the holdout column "
          "divides by the range of the 48 holdout rows. §0 uses one denominator (the 48-row grading range).", "",
          "Independence disclosure (plan §4): the 48 residuals share one fitted model, so the binomial region treats them as "
          "independent. This is an approximation. We recorded a failing objective. We did not re-select and did not score again.",
          "", "Parity: `figs/fig_parity_holdout.png` (observed vs predicted, 1:1 line; wide light bar = 95 % total band with "
          "noise, narrow dark bar = 95 % latent band).", ""]

    L += ["## 5. Noise cross-check vs σ_c, house fit (descriptive only; adds no arm)", "",
          "| objective | n | arm | inferred noise sd | σ_c [95 % CI] | inferred / σ_c | inside CI | inferred / per-level sd (4 seed designs) | seed Δ: mean abs z / max abs z / frac abs z > 1.96 | 63 trigger |",
          "|---|---|---|---|---|---|---|---|---|---|"]
    for _, r in res["cross"].iterrows():
        L.append(f"| {r['objective']} | {r['n']} | {r['arm']} | {r['inferred_noise_sd_raw']:.4g}{' (at floor)' if r['noise_at_floor'] else ''} | "
                 f"{r['sigma_c']:.4g} [{r['sigma_c_ci95_lo']:.4g}, {r['sigma_c_ci95_hi']:.4g}] | {r['ratio_inferred_over_sigma_c']:.3g} | "
                 f"{'yes' if r['inside_sigma_c_ci95'] else 'no'} | {', '.join(f'{v:.3g}' for v in r['ratio_inferred_over_level_sd'])} | "
                 f"{r['seed_delta_z_mean_abs']:.3g} / {r['seed_delta_z_max_abs']:.3g} / {r['seed_delta_frac_abs_z_gt_1p96']:.2f} | "
                 f"{'FIRES — ' + str(r['trigger_verdict']) if r['trigger_fires'] else 'no'} |")
    L += ["", "Seed Δ = the 16 solver-seed deltas of prompt 63 (two-run scale, sd ≈ √2·σ_c), standardized by the inferred sd. "
          "A firing 63 trigger (level-dependent chatter) is reported. A model change needs a plan amendment.", ""]

    m = res.get("mech")
    if m:
        import re
        from analysis.ercot_gp import ercot_gp_mechanism as M
        mm = M.mechanism_md(m["facts"], m["null"], m["flags"])
        mm = mm.replace("## Mechanism sanity", "## 6. Mechanism sanity", 1)
        mm = mm.replace("The direct 8-run check is prompt 61 (`location_contrast_E`); when it lands, its standardized residuals under the "
                        "committed config are added here as one descriptive row.",
                        "The direct 8-run check is prompt 61 (`location_contrast_E`, landed 4b7bf85). Its standardized residuals "
                        "under the committed config are the descriptive row below." if m.get("lc") is not None else
                        "The direct 8-run check is prompt 61 (`location_contrast_E`); not available in this run.")
        mm = mm.replace("### (c) No-simulation null (pinned before any n0_E Y was read)",
                        "### (c) No-simulation null (machinery pinned before any n0_E Y was read; refitted here with the committed house-fit V1 config)")
        mm = re.sub(r"(?<![-\w])LOCATION(?![-\w])", "COMPOSITION-OR-LOCATION", mm)
        mm = mm.replace("| interaction flag | location flag |", "| interaction flag | composition-or-location flag |")
        L += [mm, "", "The L flag is COMPOSITION-OR-LOCATION (54 v3.2 header): the total-only null has no host-availability "
              "term, so a high L can come from the site mix (composition) as well as from location. Truth curves: "
              "`figs/fig_null_truth_curves.png` (config-independent: no GP enters it).", ""]
        L += ["### Direction and scale (descriptive)", "",
              "| objective | Spearman(y, total MW T) on 48 rows | grading range | B_pert (v1 perturbation bar) | range / B_pert | B_j (rule v2, `pool_ed1b_v2.csv`) | range / B_j | committed arm | refit on 48 |",
              "|---|---|---|---|---|---|---|---|---|"]
        for o, v in m["direction"].items():
            bj = B.get(o)
            L.append(f"| {o} | {v['spearman_y_vs_T']:+.3f} | {v['range']:.4g} | {_g(v['B_j'])} | {_g(v['range_over_B'], '{:.1f}')} | "
                     f"{_g(bj)} | {_g(v['range'] / bj if bj else None, '{:.1f}')} | {m['arms'][o].name} | {m['refit'][o]} |")
        if "N1" in B:
            L += ["", f"N1 has the smallest range in bar units ({m['direction']['N1']['range'] / B['N1']:.1f} B_j). N1 is a "
                  "PROXY under rule v2 and is co-reported only."]
        if m["lc"] is not None:
            lc = m["lc"]
            labs = list(dict.fromkeys(lc["label"]))
            L += ["", "### Prompt-61 residual row (descriptive; no bar, no pass/fail, no exposure, no input to any decision)", "",
                  "Standardized residuals z = (y − μ) / sd (predictive sd with noise) of the 9 `location_contrast_E` designs under "
                  "the committed house-fit config, fitted on the 48 grading rows. " + mech_lc_sentence(res), "",
                  "| objective | " + " | ".join(labs) + " | mean z | mean abs z | n abs z > 1.96 |", "|---|" + "---|" * (len(labs) + 3)]
            for o in lc["objective"].unique():
                z = lc[lc.objective == o].set_index("label").loc[labs, "z"].to_numpy(float)
                L.append(f"| {o} | " + " | ".join(f"{v:+.2f}" for v in z) + f" | {np.mean(z):+.2f} | {np.mean(np.abs(z)):.2f} | {int((np.abs(z) > 1.96).sum())} |")
        L += [""]

    L += ["## 7. Committed configs, house round (`committed_configs_housefit.json` after the v2 round; contract §6.2 + v3.3 keys)", "",
          "| objective | seated | arm | cfg | floor | measured floor used | LOO NLPD at n* | holdout cov95 by tier | exposure rows |",
          "|---|---|---|---|---|---|---|---|---|"]
    for o, c in com["objectives"].items():
        L.append(f"| {o} | {c['seated']} | {c['arm']} | {'/'.join(c['cfg'])} | {_g(c['floor'])} | {c['measured_floor_used']} | "
                 f"{c['loo_nlpd_mean']:.3f} | " + ", ".join(f"{n}: {v[0]}/48" for n, v in c["holdout_cov95_by_tier"].items())
                 + f" | {c['exposure_rows']} |")
    led = S.read_ledger(res["out_dir"])
    L += ["", "Floor: `floor` 0 in the json means the inferred-noise arm; the ledger shows the same arm's floor as 1e-09 "
          "(the house jitter bound in raw units). They are the same setting.", "",
          f"Exposure ledger `exposure_ledger.csv`: {len(led)} of 24 scorings in total; retired.", "",
          "## 8. E-D7 decision rows (Kay decides; 55 Part B waits on `E-D7_decided`)", "", "```", *pi_rows(res, res2), "```", "",
          "## 9. What changed vs plan", "",
          "The strategy session appended plan AMENDMENT 2026-11-24b. It records: the training-size study at n ∈ {12, …, 48}; "
          "the n\\* rule (replaces the Part A criterion); no third-tier holdout (n\\* = 48 is a plan tier; 8 house-round "
          "scorings); the measured-floor arm live with σ_c (prompt 63, df 16); fit definition v2; one holdout re-open round "
          "(2 scorings, V1 and E1 at n = 48).", "",
          "## 10. Deviations and limits", "",
          "- House fit: bogp `train_gp` (Adam, 700 steps, lr 0.01, from gpytorch's default init). It stops before convergence "
          "(§0, §3). The lengthscale-stability condition therefore also measures the optimizer's path.",
          "- Lengthscale stability compares the SELECTED arm at consecutive n. An arm switch between n − 4 and n counts as a change.",
          "- The holdout at each tier scores the arm selected at that n (the Part A semantics).",
          "- Co-reported N4 / N1: fitted, graded and exposed like the seated ids in the house round; never binding for n\\*; "
          "no mechanism flags (shares are printed). In the v2 round they are LOO-only.",
          "- The mechanism null is built on V1 (wave D). Its scale-free thresholds apply to every objective (pinned 11-17).",
          "- log1p arms: excluded for all four ids by the inclusion rule (§1).", ""]
    if res2 is not None:
        L += v2_section(res, res2, B)
    L += ["## 12. Rule-v2 disclosure (AMENDMENT 2026-11-24, with the erratum of aa98045; the fit inputs are unchanged by it)", "",
          f"> {ds.get('disclosure', '')}", "",
          "## 14. Figures", ""] + [f"- `{os.path.relpath(f, res['out_dir'])}`" for f in res["figs"] + (res2["figs"] if res2 else [])] + [""]
    return "\n".join(L)


def v2_section(res, res2, B):
    objs = res2["objs"]
    d2, ch2 = res2["study"], res2["checks"]
    com = res2["committed"]["objectives"]
    sites = res["sites"]
    lsc = [f"ls_u_{s}" for s in sites]
    L = ["## 13. Fit definition v2 (plan AMENDMENT 2026-11-24b §3–§4)", "",
         "Definition: float64; MAP with the lengthscale prior LogNormal(√2 + ½·log 6, √3) on u ∈ [0, 1]^6 and the noise "
         "prior LogNormal(log(σ_c² / s_y²), 1) on the standardized noise variance; standardized noise lower bound 1e-6 "
         "(the measured-floor arm keeps its σ_c floor); L-BFGS-B (`fit_gpytorch_mll_scipy`, maxiter 1,000, ftol = gtol = "
         "1e-7); 16 seeded restarts (gpytorch default init + 15 prior draws, `default_rng(5454)`); the best MAP is kept. "
         "Converged = at least 2 restarts within 1e-3·n nats of the best. Arm set, inclusion rules, LOO-NLPD selection "
         "(> 2 paired se, tie order) unchanged.", "",
         "### 13.1 Per objective at n = 48 (v2 vs house)", "",
         "| objective | role | v2 arm | lengthscales u (" + ", ".join(sites) + ") | outputscale sd (t) | noise sd / σ_c | converged (restarts within tol) | mode gap (nats) | LOO NLPD v2 / house | LOO RMSE v2 / house | LOO cov95 v2 / house [43, 48] | holdout cov95 v2 [43, 48] | holdout rms z v2 | committed fit |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for o in objs:
        r = _row(d2, o, 48)
        h = _row(res["study"], o, 48)
        c = com[o]
        hv = c.get("holdout_v2")
        L.append(f"| {o} | {res2['roles'][o]} | {r['arm']} | {', '.join(f'{v:.3g}' for v in r[lsc])} | {r['outputscale_sd_t']:.4g} | "
                 f"{_g(r['noise_over_sigma_c'], '{:.3g}')} | {bool(r['converged'])} ({int(r['n_within_tol'])}/16) | {_g(r['mode_gap_nats'], '{:.3g}')} | "
                 f"{r['loo_nlpd']:.3f} / {h['loo_nlpd']:.3f} | {r['loo_rmse']:.4g} / {h['loo_rmse']:.4g} | "
                 f"{int(r['loo_cov95'])} / {int(h['loo_cov95'])} | "
                 + (f"{hv['cov95']} / 48 **{_pf(hv['pass'])}** | {hv['rms_z']:.2f}" if hv else "LOO-only (co-reported) | ")
                 + f" | {c['fit_definition']} |")
    L += ["", f"Exposure: {res2['exposure']} of 24 after the re-open round (2 scorings: V1 and E1 at n = 48). The holdout is "
          "retired again. A seated objective whose v2 config fails [43, 48] keeps its house-fit commit (pre-registered fallback).", "",
          f"### 13.2 Training-size study under v2 (LOO only) and n\\* = {res2['n_star']}", "",
          f"Reason: n\\* = {res2['n_star']}. " + " | ".join(res2["reason_lines"]), "",
          "| objective | n | arm | LOO NLPD | LOO RMSE | RMSE_n / RMSE_48 | LOO cov95 [bar] | max ls change | noise / σ_c | converged | mode gap | all met |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for _, r in ch2.iterrows():
        s = _row(d2, r["objective"], r["n"])
        L.append(f"| {r['objective']} | {r['n']} | {r['arm']} | {s['loo_nlpd']:.3f} | {s['loo_rmse']:.4g} | {r['rmse_ratio_vs_48']:.3f} | "
                 f"{r['loo_cov95']} [{r['bar_lo']}, {r['bar_hi']}] | {_g(r['ls_rel_change_max'], '{:.1%}')} | "
                 f"{_g(s['noise_over_sigma_c'], '{:.3g}')} | {bool(s['converged'])} | {_g(s['mode_gap_nats'], '{:.3g}')} | "
                 f"{'**yes**' if r['all_ok'] else ''} |")
    L += ["", "All v2 arms (every n) are in `ercot_gp_status_v2.csv` with the convergence flag and the best-vs-second gap.", ""]
    if res2.get("lc") is not None:
        lc = res2["lc"]
        labs = list(dict.fromkeys(lc["label"]))
        L += ["### 13.3 Prompt-61 residual row under the committed v2 configs (descriptive)", "",
              "| objective | " + " | ".join(labs) + " | mean z | mean abs z | n abs z > 1.96 |", "|---|" + "---|" * (len(labs) + 3)]
        for o in lc["objective"].unique():
            z = lc[lc.objective == o].set_index("label").loc[labs, "z"].to_numpy(float)
            L.append(f"| {o} | " + " | ".join(f"{v:+.2f}" for v in z) + f" | {np.mean(z):+.2f} | {np.mean(np.abs(z)):.2f} | {int((np.abs(z) > 1.96).sum())} |")
        L += [""]
    return L


def write_all(res, seed, ds, args, res2=None):
    extra = dict(res.get("extra", {}))
    extra["design_space"] = args.design_space
    if "y_range" not in res:
        res["y_range"] = {o: float(res["Y48"][o].max() - res["Y48"][o].min()) for o in res["objs"]}
    md = status_md(res, seed, ds, extra, res2)
    with open(os.path.join(res["out_dir"], "ERCOT_GP_STATUS.md"), "w") as f:
        f.write(md + "\n")
    with open(os.path.join(res["out_dir"], "pi_agenda_E-D7_draft.md"), "w") as f:
        f.write("\n".join(pi_rows(res, res2)) + "\n")
    return md
