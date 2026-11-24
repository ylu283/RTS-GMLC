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


NOISE_MODE_SD_RATIO = float(np.exp(-0.5))   # LogNormal(mu, 1) on the variance: mode e^(mu - 1) -> sd ratio e^(-1/2)
REVIEWER_SYNTH = ("The acceptance reviewer reproduced the pattern with FitV2 on synthetic data (near-linear + quadratic + "
                  "six local bumps, noise 4,376; 48 scrambled-Sobol training points, 48 i.i.d. holdout points): rbf LOO "
                  "43–46 → holdout 37–48 (one replicate LOO 44 → holdout 37, rms z 1.54); m52 LOO 45–47 → holdout 41–47; "
                  "on a smooth function rbf 42–46, m52 46–48. Under misfit the rbf arm is the fragile one (acceptance "
                  "reviewer, synthetic check, 2026-11-24).")


def _arm(df, obj, n, arm):
    d = df[(df.objective == obj) & (df.n == n) & (df.arm == arm)]
    return d.iloc[0] if len(d) else None


def v2_facts(res, res2):
    """Every number the v2 text quotes, computed from the replayed results."""
    from scipy.stats import binom
    d2, ch2 = res2["study"], res2["checks"]
    seat = res2["seated"]
    f = {"mode": NOISE_MODE_SD_RATIO}
    f["noise_sel"] = {o: [float(_row(d2, o, n)["noise_over_sigma_c"]) for n in res["grid"]] for o in res2["objs"]}
    hv, hh = {}, {}
    for o in seat:
        hv[o] = res2["holdout"][o]
        hh[o] = res["holdout"][o][48]
    f["hold_v2"], f["hold_house"] = hv, hh
    f["p_le"] = {o: float(binom.cdf(hv[o]["metrics"]["cov95"], 48, 0.95)) for o in seat}
    v = "V1"
    if v in seat:
        w = res2["winners"][v][48]
        f["v1_arm48"] = w["arm"].name
        f["v1_loo_cov48"] = int(w["loo"]["metrics"]["cov95"])
        f["p_le_loo"] = float(binom.cdf(f["v1_loo_cov48"], 48, 0.95))
        rb = [(n, _arm(d2, v, n, "rbf+std")) for n in res["grid"] if 32 <= n <= 44]
        f["rbf_cov_frac"] = [float(r["loo_cov95"]) / n for n, r in rb if r is not None]
        f["rbf_noise_44"] = float(_arm(d2, v, 44, "rbf+std")["noise_over_sigma_c"])
        f["rbf_noise_48"] = float(_arm(d2, v, 48, "rbf+std")["noise_over_sigma_c"])
        r48 = _row(d2, v, 48)
        f["v1_ls48"] = [float(r48[c]) for c in r48.index if c.startswith("ls_u_")]
        f["v1_os48"] = float(r48["outputscale_sd_t"])
        f["ratio_hold_loo"] = hv[v]["metrics"]["rmse"] / float(w["loo"]["metrics"]["rmse"])
        f["band_hold"] = hv[v].get("band_sd_median", np.nan)
        f["band_loo"] = float(np.median(w["loo"]["sd_t"]))
        f["hold_range"] = hv[v].get("y_range", np.nan)
        f["grad_range"] = res["y_range"][v]
        f["top_y"], f["top_z"] = hv[v].get("y_max", np.nan), hv[v].get("z_at_ymax", np.nan)
        lc = res2.get("lc")
        if lc is not None:
            z = lc[lc.objective == v].set_index("label")["z"]
            f["lc_n_big"], f["lc_n"], f["lc_mean"] = int((np.abs(z) > 1.96).sum()), len(z), float(z.mean())
            f["lc_max_lab"], f["lc_max"] = str(z.abs().idxmax()), float(z[z.abs().idxmax()])
        ru = _arm(d2, v, 48, "m52+std")
        f["runner"] = {"arm": "m52+std", "cov": int(ru["loo_cov95"]), "rms_z": float(ru["loo_rms_z"]), "rmse": float(ru["loo_rmse"])}
        f["lfl"] = {a: float(_arm(d2, v, 44, a)["loo_rmse"]) / float(_arm(d2, v, 48, a)["loo_rmse"])
                    for a in ("m52+std", "rbf+std")}
        f["lfl_abs"] = {a: (float(_arm(d2, v, 44, a)["loo_rmse"]), float(_arm(d2, v, 48, a)["loo_rmse"]))
                        for a in ("m52+std", "rbf+std")}
        c48 = ch2[(ch2.objective == v) & (ch2.n == 48)].iloc[0]
        f["v1_ls_change48"] = float(c48["ls_rel_change_max"])
        f["v1_arm44"] = _row(d2, v, 44)["arm"]
    f["sel_ratio44"] = {o: float(ch2[(ch2.objective == o) & (ch2.n == 44)]["rmse_ratio_vs_48"].iloc[0]) for o in seat}
    if "E1" in seat:
        f["e1_cut"] = 1.0 - hv["E1"]["metrics"]["rmse"] / hh["E1"]["metrics"]["rmse"]
        hw_v1 = float(_row(res["study"], "V1", 48)["median_95_halfwidth_raw"]) / res["sigmas"]["V1"]
        hw_e1 = float(_row(d2, "E1", 48)["median_95_halfwidth_raw"]) / res2["sigmas"]["E1"]
        f["gate_ratio"] = hw_v1 / hw_e1
        ldf = res.get("long")
        if ldf is not None and len(ldf):
            f["v1_house_over_long_band"] = (float(_row(res["study"], "V1", 48)["median_95_halfwidth_raw"])
                                            / float(_row(ldf, "V1", 48)["median_95_halfwidth_raw"]))
        f["v1_house_over_v2_band"] = (float(_row(res["study"], "V1", 48)["median_95_halfwidth_raw"])
                                      / float(_row(d2, "V1", 48)["median_95_halfwidth_raw"]))
    return f


def noise_statement(f):
    return (f"The v2 noise prior is LogNormal(log(σ_c² / s_y²), 1) on the variance. Its mode is at e^(μ − 1), i.e. "
            f"{f['mode']:.2f} σ_c in sd (below the measured chatter). The fitted v2 noise of the selected arms sits there: "
            + "; ".join(f"{o} " + ", ".join(f"{x:.3f}" for x in v[:4]) + " … σ_c" for o, v in f["noise_sel"].items() if o in ("V1", "E1"))
            + ". So the likelihood is flat in the noise and the prior sets it. Observation noise is not identifiable from 48 "
            "Sobol points. The measured chatter σ_c (df 16) is the correct lower bound; any extra residual is model "
            "discrepancy, not noise. The measured-floor arm (noise lower bound 1.00 σ_c) is the design that encodes this; "
            "LOO NLPD never selected it. "
            + (f"V1 rbf+std's noise rises to {f['rbf_noise_44']:.2f} σ_c at n = 44 and {f['rbf_noise_48']:.2f} σ_c at n = 48: "
               "the data ask for more noise, a sign of misfit. " if "rbf_noise_48" in f else "")
            + "N4 and N1 fall to " + ", ".join(f"{f['noise_sel'][o][-1]:.2f}" for o in ("N4", "N1") if o in f["noise_sel"])
            + " σ_c at n = 48: the opposite direction.")


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
    if res2 is not None and {"V1", "E1"} <= set(res2["seated"]):
        f = v2_facts(res, res2)
        r_lo, r_hi = min(f["sel_ratio44"].values()), max(f["sel_ratio44"].values())
        lf = sorted(f["lfl"].values())
        row1 = (f"| {date} | E-D7 | **ERCOT navigation tier n0 (prompt 54 Part B)** | Recommend n0 = 48: no tier below 48 "
                f"meets the rule under either fit, and under the converged fit (v2) LOO RMSE still falls "
                f"{r_lo:.2f}–{r_hi:.2f}× from n = 44 to 48 (like-for-like V1 {lf[0]:.2f}–{lf[1]:.2f}). So the first BO "
                "rounds are still learning the model, not just navigating it; this costs no new simulations because all "
                "48 runs have landed. Options: **(a) 48 — recommended**; (b) 32; (c) 44 only under a 1.12 ratio bar. "
                "| analysis/ercot_gp/ERCOT_GP_STATUS.md §0, §2, §13.2 |")
        hv, hh = f["hold_v2"], f["hold_house"]
        row2 = (f"| {date} | E-D7 (fit item) | **GP fit definition for 55** | Under the pre-registered rule E1 uses fit v2 "
                f"(holdout {hv['E1']['metrics']['cov95']}/48, {100 * f['e1_cut']:.0f} % lower RMSE) and V1 keeps the house "
                f"fit. V1's v2 fit had {hh['V1']['metrics']['rmse'] / hv['V1']['metrics']['rmse']:.1f}× lower holdout error "
                f"and better NLPD, but its bands were too narrow ({hv['V1']['metrics']['cov95']}/48, P = "
                f"{f['p_le']['V1']:.0e} by chance) because a smooth stationary kernel misses location-specific effects; V1 "
                "in 55 therefore runs with conservative, wide bands and its calibration gate has little power. "
                "**Recommendation (i): the mixed commit as committed.** Alternatives considered and rejected: (ii) a V1 "
                "noise bound from the holdout residual — a second re-open, forbidden by AMENDMENT 2026-11-24b §4, and it "
                f"tunes to the holdout; (iii) V1 m52+std under v2 (the runner-up: LOO {f['runner']['cov']}/48, rms z "
                f"{f['runner']['rms_z']:.2f}, RMSE {f['runner']['rmse'] / 1e3:.1f}k, never scored) — a re-selection after "
                "scoring; (iv) both objectives on the house fit — discards E1's verified gain. "
                "| analysis/ercot_gp/ERCOT_GP_STATUS.md §13 |")
        return row1, row2
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
    if res2 is not None:
        for o in res2["seated"]:
            hv = res2["holdout"][o]
            if not hv["pass"]:
                L[L.index("| objective | role | n | LOO cov95 / n [bar] | holdout cov95 / 48 [43, 48] | holdout rms z |") - 2] += (
                    f" Under fit v2, {o}'s bands are too narrow: holdout {hv['metrics']['cov95']} / 48 (rms z "
                    f"{hv['metrics']['rms_z']:.2f}); {o} therefore keeps the house fit (§13).")
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
        f = v2_facts(res, res2)
        L += ["**Fit v2 outcome (AMENDMENT 2026-11-24b, one re-open round, 2 scorings, exposure "
              f"{res2['exposure']} / 24).** " + "; ".join(parts) + ". 55 fits each acquisition GP with the definition "
              "committed for that objective. A v2 config that fails the bar keeps the house-fit commit (pre-registered "
              "fallback); we did not re-select and did not score again.", "",
              (f"V1 in 55 still runs on the house bands. At n = 48 (median LOO 95 % half-width) they are "
               f"{f['v1_house_over_v2_band']:.1f}× wider than V1's v2 bands"
               + (f" and {f['v1_house_over_long_band']:.1f}× wider than the exploratory long fit's" if "v1_house_over_long_band" in f else "")
               + f"; relative to chatter (half-width / σ_c) they are {f['gate_ratio']:.1f}× E1's v2 bands. So V1's C2 / C3 gate "
               "has little power and E1's has more. " if "gate_ratio" in f else "") + "v2 LOO uses the fitted constant mean; house LOO used 0 after standardization. This is not "
              "strictly like-for-like; the effect is small.", "",
              "**Consequences of the mixed commit for 55.** (1) qNEHVI hypervolume gains will be driven by V1's variance: "
              "the search tilts toward V1 exploration and the V1 front is blurrier. (2) The house V1 refit cannot learn as "
              "n grows (the Adam step cap), so its drift is path-dependent; record it per round. (3) Pre-register in 55, "
              "report-only: log the V1 v2-m52 and v2-rbf posteriors beside the house fit every round, and report gate "
              "power per objective.", "",
              "**Noise.** " + noise_statement(f), ""]
    for o in bad:
        fails = [n for n in (32, 48) if not res["holdout"][o][n]["pass"]]
        L += [f"**{o} ({roles[o]}) FAILS the holdout at n = {', '.join(map(str, fails))}** ("
              + ", ".join(f"n = {n}: {res['holdout'][o][n]['metrics']['cov95']} / 48" for n in (32, 48))
              + f"; bar [43, 48]). {'It is not seated. ' if roles[o] != 'seated' else ''}We recorded the failure. "
              "We did not re-select and did not score again.", ""]
    span = raw_ls_span(res)
    L += ["**Notes.**", "",
          f"- Mechanism (descriptive): {mech_lc_sentence(res)}",
          f"- Provenance: the fit change was designed after the house holdout results were known (8 scorings; the "
          f"diagnostic {LONG_SHA} was coded 7 min later). Its stated basis is a training-side optimizer diagnosis "
          "reproduced on synthetic data. Readers should treat the v2 holdout round as a second look, not a blind test.",
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
              f"Provenance: the fit change was designed after the house holdout results were known (8 scorings; this "
              f"diagnostic, {LONG_SHA}, was coded 7 min later). Treat the v2 holdout round as a second look, not a blind test.", "",
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
         "prior LogNormal(log(σ_c² / s_y²), 1) on the standardized noise variance (its mode is at 0.61 σ_c in sd, below "
         "the measured chatter; the `fit_v2_spec` string in committed_configs.json names the same prior); standardized "
         "noise lower bound 1e-6 "
         "(the measured-floor arm keeps its σ_c floor); L-BFGS-B (`fit_gpytorch_mll_scipy`, maxiter 1,000, ftol = gtol = "
         "1e-7); 16 seeded restarts (gpytorch default init + 15 prior draws, `default_rng(5454)`); the best MAP is kept. "
         "Converged = at least 2 restarts within 1e-3·n nats of the best. Arm set, inclusion rules, LOO-NLPD selection "
         "(> 2 paired se, tie order) unchanged.", "",
         "### 13.1 Per objective at n = 48 (v2 vs house)", "",
         "| objective | role | v2 arm | lengthscales u (" + ", ".join(sites) + ") | outputscale sd (t) | noise sd / σ_c | converged (restarts within tol) | mode gap (nats) | LOO NLPD v2 / house | LOO RMSE v2 / house | LOO cov95 v2 / house [43, 48] | holdout cov95 v2 [43, 48] | holdout rms z v2 | holdout NLPD v2 / house | holdout RMSE v2 / house | committed fit |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for o in objs:
        r = _row(d2, o, 48)
        h = _row(res["study"], o, 48)
        c = com[o]
        hv = c.get("holdout_v2")
        L.append(f"| {o} | {res2['roles'][o]} | {r['arm']} | {', '.join(f'{v:.3g}' for v in r[lsc])} | {r['outputscale_sd_t']:.4g} | "
                 f"{_g(r['noise_over_sigma_c'], '{:.3g}')} | {bool(r['converged'])} ({int(r['n_within_tol'])}/16) | {_g(r['mode_gap_nats'], '{:.3g}')} | "
                 f"{r['loo_nlpd']:.3f} / {h['loo_nlpd']:.3f} | {r['loo_rmse']:.4g} / {h['loo_rmse']:.4g} | "
                 f"{int(r['loo_cov95'])} / {int(h['loo_cov95'])} | "
                 + (f"{hv['cov95']} / 48 **{_pf(hv['pass'])}** | {hv['rms_z']:.2f} | "
                    f"{res2['holdout'][o]['metrics']['nlpd']:.2f} / {res['holdout'][o][48]['metrics']['nlpd']:.2f} | "
                    f"{_nat(res2['holdout'][o]['metrics']['rmse'], o)} / {_nat(res['holdout'][o][48]['metrics']['rmse'], o)}"
                    if hv else "LOO-only (co-reported) | | | ")
                 + f" | {c['fit_definition']} |")
    f = v2_facts(res, res2)
    hv1, hh1 = f["hold_v2"].get("V1"), f["hold_house"].get("V1")
    if hv1 is not None and not hv1["pass"]:
        L += ["", f"V1's v2 fit fails only on band width: its holdout NLPD is {hv1['metrics']['nlpd']:.2f} (house "
              f"{hh1['metrics']['nlpd']:.2f}) and its holdout RMSE {_nat(hv1['metrics']['rmse'], 'V1')} (house "
              f"{_nat(hh1['metrics']['rmse'], 'V1')}, {hh1['metrics']['rmse'] / hv1['metrics']['rmse']:.1f}× worse). The "
              "fallback keeps the less accurate, wider model."]
    L += ["", f"Exposure: {res2['exposure']} of 24 after the re-open round (2 scorings: V1 and E1 at n = 48). The holdout is "
          "retired again. A seated objective whose v2 config fails [43, 48] keeps its house-fit commit (pre-registered fallback).", "",
          "**Noise under v2.** " + noise_statement(f), ""]
    if hv1 is not None and not hv1["pass"]:
        rcf = f["rbf_cov_frac"]
        L += ["### 13.1b Why V1's v2 config failed the holdout", "",
              f"(a) **Not chance.** P(≤ {hv1['metrics']['cov95']} | 48, 0.95) = {f['p_le']['V1']:.0e}. LOO "
              f"{f['v1_loo_cov48']}/48 was not a warning by itself (P(≤ {f['v1_loo_cov48']}) = {f['p_le_loo']:.2f}). But "
              f"rbf+std's LOO coverage ran at {min(rcf):.2f}–{max(rcf):.2f} for n = 32–44, and it became the selected arm "
              f"only at n = 48 (selected at n = 32–44: {', '.join(sorted(set(_row(res2['study'], 'V1', n)['arm'] for n in (32, 36, 40, 44))))}). NLPD selection rewards sharp bands, and the rule has "
              "no coverage tie-break.",
              f"(b) **Misspecification.** V1 is near-linear in the totals. The rbf lengthscales "
              f"{min(f['v1_ls48']):.1f}–{max(f['v1_ls48']):.1f} in u make it close to a low-order polynomial, with "
              f"outputscale {f['v1_os48']:.3g} smoothing over site effects. "
              + (f"The prompt-61 residual row under v2 has {f['lc_n_big']} of {f['lc_n']} |z| > 1.96, mean z "
                 f"{f['lc_mean']:+.2f}, {f['lc_max_lab']} {f['lc_max']:+.2f}." if "lc_n_big" in f else ""),
              f"(c) **LOO on the Sobol prefix is optimistic for an i.i.d. holdout.** Holdout errors are "
              f"{f['ratio_hold_loo']:.2f}× the LOO errors ({_nat(hv1['metrics']['rmse'], 'V1')} vs "
              f"{_nat(res2['winners']['V1'][48]['loo']['metrics']['rmse'], 'V1')}), while "
              f"the holdout band sd (median {_nat(f['band_hold'], 'V1')}) is narrower than the LOO band sd (median "
              f"{_nat(f['band_loo'], 'V1')}). Dropping one Sobol point opens a hole wider than a random point's "
              "nearest-neighbour gap. Winner's-curse arm selection on the same LOO adds to it.",
              f"(d) **Minor distribution shift.** The holdout V1 range is {_nat(f['hold_range'], 'V1')} against "
              f"{_nat(f['grad_range'], 'V1')} on the grading tier; the top holdout point ({_nat(f['top_y'], 'V1')}) has "
              f"z = {f['top_z']:+.2f}" + (" and lies outside its band." if abs(f["top_z"]) > 1.96 else "."),
              "", REVIEWER_SYNTH, "",
              "These holdout quantities come from the deterministic replay of the recorded scoring (no new scoring).", ""]
    L += [f"### 13.2 Training-size study under v2 (LOO only) and n\\* = {res2['n_star']}", "",
          f"Reason: n\\* = {res2['n_star']}. " + " | ".join(res2["reason_lines"]), "",
          (f"Like-for-like V1 ratios at n = 44 (same arm at 44 and 48): m52+std "
           f"{_nat(f['lfl_abs']['m52+std'][0], 'V1')} / {_nat(f['lfl_abs']['m52+std'][1], 'V1')} = {f['lfl']['m52+std']:.3f}; "
           f"rbf+std {_nat(f['lfl_abs']['rbf+std'][0], 'V1')} / {_nat(f['lfl_abs']['rbf+std'][1], 'V1')} = "
           f"{f['lfl']['rbf+std']:.3f}. The headline {f['sel_ratio44']['V1']:.2f} compares {f['v1_arm44']} at 44 with "
           f"{f['v1_arm48']} at 48. The {100 * f['v1_ls_change48']:.0f} % lengthscale change at n = 48 is an arm switch "
           f"({f['v1_arm44']} → {f['v1_arm48']}), not instability. The converged fit is still learning fast from 44 → 48; "
           "the first BO rounds are model-learning rounds." if "lfl" in f else ""), "",
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
        L += ["### 13.3 Prompt-61 residual row under the v2 configs at n = 48 (V1 v2 NOT committed; descriptive)", "",
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
