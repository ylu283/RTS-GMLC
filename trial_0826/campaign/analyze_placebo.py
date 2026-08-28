#!/usr/bin/env python3
"""Render the placebo-wave verdict on the f4 DA-commitment artifact.

Usage:  python analyze_placebo.py [wave_dir]        (default: waves/placebo)

Run AFTER the CRC run completes and `summarize_wave.py waves/placebo` has
produced waves/placebo/objectives.csv.

The placebo (317_WIND_1 split at B = 0.01) is an economically inert
retrofit: at near-zero bid the PEM twin clears whenever the unsplit unit
would have, so market outcomes should match the base case. Any residual
Δshed IS the measurement — the pure split/DA-commitment artifact suspected
of inflating wind-site f4 gains (screening_review.md; living report §7.2).

Writes the verdict + numbers to <wave_dir>/placebo_verdict.md.
"""

import os
import sys

import pandas as pd

CAMPAIGN_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_WAVE_DIR = os.path.join(CAMPAIGN_DIR, "waves", "placebo")

# --- pinned base-case constants (computed 2026-08-27; recompute nothing) ---
BASE_SHED_MWH = 41_500.115
BASE_CURT_MWH = 1_688_575.777
BASE_317_OUTPUT_MWH = 1_874_465.5
BASE_317_CURT_MWH = 427_574.7   # 100% of it in hours with Chuhsi LMP < 0.01
BASE_317_AVAILABLE_MWH = 2_302_040.2

# --- thresholds ---
SHED_FLOOR = 3_000.0     # MWh; measured perturbation floor (screening_review.md)
SHED_CONFIRM = 8_000.0   # MWh; above this the artifact is beyond floor uncertainty
# Chuhsi has 2,382 hours with LMP < 0.01; the PEM twin (399.55 MW) can only
# withhold in sub-bid-price hours, so withholding is hard-bounded:
WITHHOLD_BOUND_MWH = 951_700.0  # 399.55 MW x 2,382 h
CURT_NOTE = (
    "NOTE: Δcurt is EXPECTED nonzero and NEGATIVE even for a perfect placebo:\n"
    "curtailment-hours clear at LMP <= 1 (measured: 100% of curtailment-hours\n"
    "at every site), and in exactly-zero-price hours the twin's 0.01 bid does\n"
    "not clear — its share of own curtailment is reclassified into the H2\n"
    "column. Δcurt is NOT part of the verdict."
)

VERDICTS = {
    "SPLIT-NEUTRAL": (
        "the split itself does not distort commitment; the B=40 shed\n"
        "reductions are design-driven within the model — f4 usable for\n"
        "renewables, with the \"conservative-DA mechanism\" interpretation note."
    ),
    "INCONCLUSIVE": (
        "inside the floor's uncertainty band (the 3k floor is itself an\n"
        "estimate from 5 designs — a knife-edge verdict would rest on\n"
        "estimation noise).\n"
        "Prescribed follow-up: ONE permuted-dict repeat of the placebo (same\n"
        "design, trivially reordered dict -> different MIP path) to measure\n"
        "the perturbation floor at this exact design, ~10 h."
    ),
    "ARTIFACT CONFIRMED": (
        "the mere split distorts DA commitment; renewable f4 numbers (incl.\n"
        "the all-in -93% shed) are contaminated — f4 for renewable sites must\n"
        "carry a hard caveat and the accounting/setup needs revisiting before\n"
        "f4 drives anything."
    ),
}


def integrity_violations(row):
    """The verdict assumes the placebo behaved as designed — verify first."""
    violations = []
    h2_mwh = float(row["pem_withheld_mwh_total"])
    if h2_mwh > WITHHOLD_BOUND_MWH:
        violations.append(
            f"h2_mwh = {h2_mwh:,.1f} MWh exceeds the withholding bound "
            f"{WITHHOLD_BOUND_MWH:,.0f} MWh (399.55 MW x 2,382 sub-bid-price hours) — "
            "the twin withheld in hours it should have cleared"
        )
    delta_curt = float(row["delta_curtailment_mwh"])
    if not (-WITHHOLD_BOUND_MWH <= delta_curt <= SHED_FLOOR):
        violations.append(
            f"delta_curtailment = {delta_curt:,.1f} MWh outside "
            f"[-{WITHHOLD_BOUND_MWH:,.0f}, +{SHED_FLOOR:,.0f}] "
            "(reclassification + backfill cannot exceed total withholding; a "
            "positive delta beyond floor means the placebo premise broke)"
        )
    return violations


def verdict_for(delta_shed):
    if abs(delta_shed) <= SHED_FLOOR:
        return "SPLIT-NEUTRAL"
    if abs(delta_shed) <= SHED_CONFIRM:
        return "INCONCLUSIVE"
    return "ARTIFACT CONFIRMED"


def report_lines(row):
    delta_shed = float(row["delta_load_shed_mwh"])
    delta_curt = float(row["delta_curtailment_mwh"])
    h2_mwh = float(row["pem_withheld_mwh_total"])
    delta_cost_approx = float(row["delta_cost_less_synthetic_usd_APPROX"])
    synthetic = float(row["synthetic_bid_cost_usd"])
    # base raw cost = (raw - synthetic) - delta_APPROX, so:
    delta_cost_raw = synthetic + delta_cost_approx

    verdict = verdict_for(delta_shed)
    lines = [
        "# Placebo verdict (f4 DA-commitment artifact)",
        "",
        f"delta_shed = {delta_shed:,.1f} MWh (base {BASE_SHED_MWH:,.1f}; "
        f"floor +/-{SHED_FLOOR:,.0f}; confirm > {SHED_CONFIRM:,.0f})",
        "",
        f"**VERDICT: {verdict}** — {VERDICTS[verdict]}",
        "",
        "## Context (informational, not part of the verdict)",
        "",
        f"- delta_curt = {delta_curt:,.1f} MWh; 317's base curtailment is "
        f"{BASE_317_CURT_MWH:,.1f} MWh = {BASE_317_CURT_MWH / BASE_CURT_MWH:.1%} of system "
        f"({BASE_CURT_MWH:,.1f}).",
        CURT_NOTE,
        f"- delta_cost_raw = {delta_cost_raw:,.0f} USD (expected small — synthetic "
        f"cost = {synthetic:,.0f} USD, which is ~ grid sales x 0.01); "
        f"delta_cost APPROX column = {delta_cost_approx:,.0f} USD.",
        f"- H2: {h2_mwh:,.1f} MWh withheld = {float(row['h2_kg_total']):,.0f} kg "
        f"(bound {WITHHOLD_BOUND_MWH:,.0f} MWh).",
    ]
    return verdict, lines


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    wave_dir = argv[0] if argv else DEFAULT_WAVE_DIR
    objectives_csv = os.path.join(wave_dir, "objectives.csv")
    if not os.path.isfile(objectives_csv):
        print("run summarize_wave.py on waves/placebo first")
        return 0

    obj = pd.read_csv(objectives_csv)
    assert len(obj) == 1, f"expected exactly one placebo row, got {len(obj)}"
    row = obj.iloc[0]

    violations = integrity_violations(row)
    if violations:
        print("PLACEBO INVALID — the wave did not behave as designed; no verdict:")
        for v in violations:
            print(f"  - {v}")
        return 1

    verdict, lines = report_lines(row)
    text = "\n".join(lines) + "\n"
    print(text)
    out_path = os.path.join(wave_dir, "placebo_verdict.md")
    with open(out_path, "w") as f:
        f.write(text)
    print(f"written: {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
