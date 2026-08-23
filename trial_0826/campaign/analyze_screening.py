#!/usr/bin/env python3
"""Analyze the screening wave: per-site effects, interaction, tier verdict.

Usage:
    python analyze_screening.py [wave_dir]        # default waves/screening

Prereq: summarize_wave.py has produced objectives.csv + site_detail.csv in
the wave dir.

Method note: the pilot measured a ZERO solver-noise floor (identical runs →
bit-identical objectives), so the tier criterion cannot be "effect exceeds
repeat noise". We use an EFFECT-SHARE criterion instead: a site earns
independent design dimensions iff its single-site (OAT) curtailment
reduction is at least SHARE_INDEP of the summed OAT reductions. Thresholds
are parameters, printed with the result; the output is a recommendation
table, not an automatic decision.

Also reports the interaction (substitution) measure the campaign design
needs: sum(OAT effects) vs the all-in joint run. A large positive gap means
sites compete for the same surplus and OAT overstates marginal sites
(doc 14 / 14b B3); it also calibrates how non-additive the GP landscape is.
"""
import sys
from pathlib import Path

import pandas as pd

SHARE_INDEP = 0.05   # OAT curtailment-reduction share needed for independent dims
HOURS = 8784

CAMPAIGN_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(CAMPAIGN_DIR))


def site_to_tier():
    import tiers
    t = tiers.build_tiers() if hasattr(tiers, "build_tiers") else tiers.TIERS
    if isinstance(t, tuple):  # build_tiers() may return (tiers, provisional)
        t = t[0]
    return {m: name for name, cfg in t.items() for m in cfg["members"]}


def main():
    wave = Path(sys.argv[1]) if len(sys.argv) > 1 else CAMPAIGN_DIR / "waves" / "screening"
    obj_path = wave / "objectives.csv"
    if not obj_path.is_file():
        print(f"{obj_path} not found — run summarize_wave.py on this wave first.")
        return 0

    obj = pd.read_csv(obj_path)
    site = pd.read_csv(wave / "site_detail.csv")
    tier_of = site_to_tier()

    oat = obj[obj["oat_site"].notna() & (obj["oat_site"] != "__ALL__")].copy()
    allin = obj[obj["oat_site"] == "__ALL__"]
    n_expected = 12
    if len(obj) < n_expected:
        print(f"WARNING: only {len(obj)}/{n_expected} screening runs summarized — "
              "results below are partial.")

    rows = []
    for _, r in oat.iterrows():
        s = r["oat_site"]
        sd = site[(site["index"] == r["index"]) & (site["site"] == s)]
        cap = float(sd["pem_capacity_mw"].iloc[0]) if len(sd) else float("nan")
        h2 = float(sd["h2_mwh"].iloc[0]) if len(sd) else float("nan")
        curt_red = -r["delta_curtailment_mwh"]          # positive = good
        shed_red = -r["delta_load_shed_mwh"]
        rows.append({
            "site": s, "tier_now": tier_of.get(s, "?"),
            "pem_mw": cap,
            "curt_reduction_mwh": curt_red,
            "curt_red_per_mw": curt_red / cap if cap else float("nan"),
            "shed_reduction_mwh": shed_red,
            "pem_cf": h2 / (cap * HOURS) if cap else float("nan"),
        })
    df = pd.DataFrame(rows)
    total_oat = df["curt_reduction_mwh"].sum()
    df["share_of_oat_total"] = df["curt_reduction_mwh"] / total_oat
    df["verdict"] = df["share_of_oat_total"].apply(
        lambda x: "independent" if x >= SHARE_INDEP else "cluster")
    df = df.sort_values("curt_reduction_mwh", ascending=False)

    lines = ["# Screening analysis", "",
             f"Effect-share criterion: independent iff OAT curtailment-reduction "
             f"share >= {SHARE_INDEP:.0%} (noise floor is zero; see docstring).", ""]
    lines.append(df.to_string(index=False,
                              float_format=lambda v: f"{v:,.3f}"))
    lines.append("")

    if len(allin):
        a = allin.iloc[0]
        joint = -a["delta_curtailment_mwh"]
        gap = (total_oat - joint) / joint if joint else float("nan")
        lines += [
            f"Sum of OAT curtailment reductions: {total_oat:,.0f} MWh",
            f"All-in joint reduction:            {joint:,.0f} MWh",
            f"Interaction gap (sum-OAT vs joint): {gap:+.1%}",
            "  > 0: sites are substitutes — OAT overstates marginal sites;",
            "  the larger the gap, the less additive the landscape (GP kernel note).",
            "",
            f"All-in load-shed reduction: {-a['delta_load_shed_mwh']:,.0f} MWh",
        ]
    else:
        lines.append("All-in run not yet summarized — interaction gap unavailable.")

    changes = df[df["verdict"].ne(df["tier_now"].map(
        lambda t: "independent" if df[df.tier_now == t].shape[0] == 1 else "cluster"))]
    lines += ["", "Tier-change candidates (verdict differs from current tier "
              "structure — final call is Kay's, edit tiers.py accordingly):"]
    lines.append(changes[["site", "tier_now", "share_of_oat_total", "verdict"]]
                 .to_string(index=False) if len(changes) else "  none")

    report = "\n".join(lines)
    print(report)
    (wave / "screening_analysis.md").write_text(report + "\n")
    print(f"\nwritten: {wave / 'screening_analysis.md'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
