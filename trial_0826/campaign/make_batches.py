"""Build the three campaign wave definitions (doc 14 §6): pilot, screening, n0.

Usage:  python make_batches.py <wave_name>   (one wave per invocation)

`all` is REFUSED since prompt 28: rerunning a legacy builder would overwrite
a frozen, possibly in-flight wave directory and re-insert `-tc` into its
scripts. Invoke builders per-wave by name only.

Each wave is a self-contained directory under campaign/waves/ with
design_matrix.csv, per-row retrofit JSONs, manifest.json, and the generated
SGE array script. Commit the campaign code BEFORE generating waves so the
manifest git SHA describes the generator. No job is ever submitted here.
"""

import csv
import functools
import hashlib
import json
import os
import sys

import numpy as np
import pandas as pd
import scipy

import design_tools as dt
import submit_array
from tiers import (RHO_SCENARIOS, SOBOL_SEED, STAGE2_LATTICE, TIERS,
                   build_tiers, load_gen_pmax, load_tm1_stats, stage2_tiers)

WAVES_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "waves")

FULL_YEAR = 366  # 2020 is a leap year — 366, not 365
N0_SIZE = 128    # doc 14 §2.2: 2^7, Sobol balance, ~9d at d=14

OAT_BID = 40.0            # top of bid range for every screening site (doc 14 §6 item 2)
NUCLEAR_SITE = "121_NUCLEAR_1"
NUCLEAR_OAT_OMEGA = 0.5   # parent-paper optimum; nuclear is never in 15a's CSV
BASE_CASE_SOURCE_DIR = "trial_0826/base_case_pcm_test"

HOLD_MD = """# HOLD — do not submit this wave

1. **This wave is a DRAFT — submit nothing yet.** Tier structure is FINAL
   (d = 12, screening verdict 2026-08-24); still pending: the PI decisions
   (O-M2 bid handling, O-15 constraint, f5) from doc 16.

2. **After the PI + screening decisions land, regenerate** by editing
   `campaign/tiers.py` and rerunning `python make_batches.py n0` — same
   `SOBOL_SEED`, `skip=0`. Nothing from this draft was submitted, so a full
   redraw is safe. If the tier count changes, d changes and every point
   moves — that is expected, not a bug.

3. **The continue-the-sequence rule (doc 14 §5.1) governs waves drawn AFTER
   the released n0**, within the final box: same seed, `skip` = number of
   points already drawn, never re-seed.
"""


def midpoint_design(tiers):
    return {
        name: (
            (tier["omega"][0] + tier["omega"][1]) / 2.0,
            (tier["bid"][0] + tier["bid"][1]) / 2.0,
        )
        for name, tier in tiers.items()
    }


def build_pilot(waves_root=WAVES_ROOT):
    """Engineering + noise floor: 3 identical full-year runs at the mid-box
    reference design (repeat-run noise floor) + 9 copies at num_days=7 to
    exercise concurrent submission and license load. 12 jobs.

    Deliberate deviation from doc 14 §6 item 1 ("10-20 concurrent full-year
    jobs"): sustained full-year license concurrency is demonstrated by the
    12-job screening batch instead; this buys the same engineering signal at
    ~1/10 the CPU cost (see README).
    """
    tiers, provisional = build_tiers()
    reference = midpoint_design(tiers)
    rows = [
        dt.make_row(tiers, reference, index=i, num_days=FULL_YEAR, provisional=provisional)
        for i in range(1, 4)
    ]
    rows += [
        dt.make_row(tiers, reference, index=i, num_days=7, provisional=provisional)
        for i in range(4, 13)
    ]
    wave_dir = os.path.join(waves_root, "pilot")
    dt.write_wave(dt.rows_to_matrix(rows, tiers), wave_dir, tiers, sobol=None)
    return wave_dir


def screening_sites(tiers):
    """Nuclear first, then every renewable member in tier order: one OAT run
    per SITE, not per tier — the cluster tiers are the hypothesis under test."""
    sites = [NUCLEAR_SITE]
    for tier in tiers.values():
        if tier["type"] == "renewable":
            sites.extend(tier["members"])
    return sites


def build_screening(waves_root=WAVES_ROOT):
    """T-M2: 11 single-site OAT runs (10 renewables + nuclear) + 1 all-in
    joint run = 12 full-year jobs. B=40 everywhere; omega from 15a's
    omega_oat_reference (nuclear always 0.5)."""
    tiers, provisional = build_tiers()
    stats = load_tm1_stats()
    pmax = load_gen_pmax()
    site_tier = {m: name for name, tier in tiers.items() for m in tier["members"]}

    sites = screening_sites(tiers)
    site_omega = {}
    for site in sites:
        if site == NUCLEAR_SITE:
            site_omega[site] = NUCLEAR_OAT_OMEGA
        elif stats is not None and site in stats:
            site_omega[site] = stats[site]["omega_oat_reference"]
        else:
            # fallback: half the tier's current omega upper bound
            site_omega[site] = tiers[site_tier[site]]["omega"][1] / 2.0
            provisional = True

    rows, dicts = [], {}
    for i, site in enumerate(sites, start=1):
        gen_pmax = None if site == NUCLEAR_SITE else pmax[site]
        dicts[i] = dt.single_site_entry(site, site_omega[site], OAT_BID, gen_pmax)
        rows.append(dt.make_row(tiers, {}, index=i, num_days=FULL_YEAR,
                                oat_site=site, provisional=provisional))

    # all-in row: the UNION of the 11 OAT dicts — the Sigma(OAT)-vs-joint
    # interaction test requires identical per-site settings
    all_in_index = len(sites) + 1
    all_in = {}
    for i in range(1, len(sites) + 1):
        all_in.update(dicts[i])
    dicts[all_in_index] = all_in
    rows.append(dt.make_row(tiers, {}, index=all_in_index, num_days=FULL_YEAR,
                            oat_site="__ALL__", provisional=provisional))

    wave_dir = os.path.join(waves_root, "screening")
    dt.write_wave(dt.rows_to_matrix(rows, tiers), wave_dir, tiers,
                  sobol=None, retrofit_dicts=dicts)
    return wave_dir


def build_n0(waves_root=WAVES_ROOT):
    """Initial design: 128 scrambled Sobol points (full-year) + 2 submittable
    anchors (center point, parent-paper nuclear optimum). Generated but held
    (HOLD.md) until PI + screening decisions land. The base case is NOT
    re-run: it lives in external_anchors.csv only."""
    tiers, provisional = build_tiers()

    points = dt.generate_sobol(N0_SIZE, SOBOL_SEED, skip=0)
    design = dt.to_design_matrix(points, tiers, start_index=1,
                                 num_days=FULL_YEAR, provisional=provisional)

    anchor_rows = [
        dt.make_row(tiers, midpoint_design(tiers), index=N0_SIZE + 1,
                    num_days=FULL_YEAR, anchor=True, provisional=provisional),
        dt.make_row(tiers, {"nuclear": (0.5, 40.0)}, index=N0_SIZE + 2,
                    num_days=FULL_YEAR, anchor=True, provisional=provisional),
    ]
    design = dt.rows_to_matrix(list(design.to_dict("records")) + anchor_rows, tiers)

    # non-submittable external anchor: the already-run base case
    external_row = dt.make_row(tiers, {}, index=0, num_days=FULL_YEAR, anchor=True,
                               provisional=provisional, external=True)
    external = dt.rows_to_matrix([external_row], tiers)
    external["source_dir"] = BASE_CASE_SOURCE_DIR

    wave_dir = os.path.join(waves_root, "n0")
    dt.write_wave(design, wave_dir, tiers,
                  sobol={"seed": SOBOL_SEED, "skip": 0, "n": N0_SIZE},
                  external_anchors=external)
    with open(os.path.join(wave_dir, "HOLD.md"), "w") as f:
        f.write(HOLD_MD)
    return wave_dir


def build_placebo(waves_root=WAVES_ROOT):
    """Placebo wave (screening_review.md; living report §7.2): ONE run —
    317_WIND_1 split into gen + gen_PEM at B = 0.01, an economically inert
    retrofit. At near-zero bid the PEM twin clears whenever the unsplit unit
    would have, so market outcomes should match the base case. A placebo must
    produce no effect — any residual delta IS the measurement: the pure
    split/DA-commitment artifact suspected of inflating wind-site f4 gains
    (screening saw 317 cut shedding by 22 GWh at B = 40 vs nuclear's 3.5 GWh).
    Same omega as the screening 317 OAT so the A/B pair differs only in B.
    Verdict rendered by analyze_placebo.py after summarize_wave.py runs."""
    tiers, provisional = build_tiers()
    stats = load_tm1_stats()
    pmax = load_gen_pmax()
    site = "317_WIND_1"
    omega = (stats[site]["omega_oat_reference"]
             if stats is not None and site in stats else 0.5)
    dicts = {1: dt.single_site_entry(site, omega, 0.01, pmax[site])}
    rows = [dt.make_row(tiers, {}, index=1, num_days=FULL_YEAR,
                        oat_site=site, provisional=provisional)]
    wave_dir = os.path.join(waves_root, "placebo")
    dt.write_wave(dt.rows_to_matrix(rows, tiers), wave_dir, tiers,
                  sobol=None, retrofit_dicts=dicts)
    return wave_dir


GRID_LEVELS = 9  # math-log §4.2: 9x9 direct contour grid / 9-level OAT sweeps
CONTOUR_PAIR = ("wind_303", "wind_317")  # phase-1 headline pair (two biggest)


def build_contour_303x317(scenario, waves_root=WAVES_ROOT):
    """Phase-1 contour wave (math-log §4.2): 9x9 grid over (omega_303,
    omega_317), all other tiers absent, bids derived from the batch's rho
    scenario (B = 20*rho_h2, math-log §1). 81 full-year rows, indices 1-81
    ROW-MAJOR with omega_303 as the OUTER axis:
    index = 9*i303 + i317 + 1 (i303, i317 = 0..8 into each tier's
    omega_grid). See README for the reconstruction recipe."""
    tiers, provisional = build_tiers()
    rho = RHO_SCENARIOS[scenario]
    t303, t317 = CONTOUR_PAIR
    grid_303 = dt.omega_grid(GRID_LEVELS, *tiers[t303]["omega"])
    grid_317 = dt.omega_grid(GRID_LEVELS, *tiers[t317]["omega"])
    rows = []
    for i, w303 in enumerate(grid_303):          # outer: omega_303
        for j, w317 in enumerate(grid_317):      # inner: omega_317
            rows.append(dt.make_row(
                tiers, {t303: w303, t317: w317},
                index=GRID_LEVELS * i + j + 1, num_days=FULL_YEAR,
                provisional=provisional, rho_h2=rho))
    wave_dir = os.path.join(waves_root, f"contour_303x317_{scenario}")
    dt.write_wave(dt.rows_to_matrix(rows, tiers), wave_dir, tiers, sobol=None)
    return wave_dir


def build_sweep(scenario, waves_root=WAVES_ROOT):
    """Per-tier OAT omega sweeps (math-log §4.1): for each of the 6 tiers,
    that tier alone at its 9 omega_grid levels (others absent), bids derived
    from the rho scenario. 54 full-year rows, indices 1-54 in tier order.
    The 303/317 sweep levels equal the contour grid axes (same omega_grid),
    so the §4.3 interaction index gets its f(omega, 0) margins at zero extra
    cost; f(0, 0) is the base case (external)."""
    tiers, provisional = build_tiers()
    rho = RHO_SCENARIOS[scenario]
    rows = []
    index = 1
    for tier_name, tier in tiers.items():
        for w in dt.omega_grid(GRID_LEVELS, *tier["omega"]):
            rows.append(dt.make_row(tiers, {tier_name: w}, index=index,
                                    num_days=FULL_YEAR,
                                    provisional=provisional, rho_h2=rho))
            index += 1
    wave_dir = os.path.join(waves_root, f"sweep_{scenario}")
    dt.write_wave(dt.rows_to_matrix(rows, tiers), wave_dir, tiers, sobol=None)
    return wave_dir


STAGE2_N0_SIZE = 16  # stage2_plan.md §2.1: power of 2, Sobol balance


def _snap_to_lattice(omegas):
    """Snap each omega coordinate to the nearest STAGE2_LATTICE level.
    np.argmin returns the FIRST index on an exact midpoint tie."""
    lattice = np.asarray(STAGE2_LATTICE, dtype=float)
    return np.array([lattice[np.argmin(np.abs(w - lattice))] for w in omegas])


def build_stage2_n0(scenario, waves_root=WAVES_ROOT, size=STAGE2_N0_SIZE,
                    seed=SOBOL_SEED, wave_name=None, manifest_extra=None):
    """Stage-2 batch 0 (prompt 27, PI directive 2026-09): 16 scrambled Sobol
    points on the d = 6 discrete lattice. A NEW d = 6 engine (seed
    SOBOL_SEED, skip = 0) — the never-re-seed rule applies to later Stage-2
    rows, which continue THIS sequence with skip = n_drawn_total (recorded in
    the manifest). Each point is affine-mapped into the stage-2 box and each
    coordinate snapped to the nearest lattice level; duplicate post-snap rows
    are dropped keeping the first occurrence and replaced by continuing the
    sequence in blocks (with this seed snapping produces zero collisions —
    the redraw path is correctly-specified dead code; scipy's
    non-power-of-2 UserWarning on a redraw is expected, not an error).

    `size` / `seed` / `wave_name` / `manifest_extra` (prompt 35) build ONE
    start block of any size from another engine (methods_C S2 / S3); the
    defaults reproduce stage2_C_n0 exactly."""
    tiers, provisional = stage2_tiers()
    rho = RHO_SCENARIOS[scenario]
    lo, hi = float(STAGE2_LATTICE[0]), float(STAGE2_LATTICE[-1])

    kept, seen, snap_log = [], set(), []
    n_drawn_total = 0
    while len(kept) < size:
        block = size if n_drawn_total == 0 else size - len(kept)
        points = dt.generate_sobol(block, seed, skip=n_drawn_total,
                                   d=len(tiers))
        n_drawn_total += block
        for unit in points:
            pre = lo + unit * (hi - lo)
            post = _snap_to_lattice(pre)
            key = tuple(float(w) for w in post)
            entry = {"draw": len(snap_log) + 1,
                     "pre_snap": [float(w) for w in pre],
                     "post_snap": [float(w) for w in post],
                     "kept_index": None}
            if key not in seen and len(kept) < size:
                seen.add(key)
                kept.append(post)
                entry["kept_index"] = len(kept)
            snap_log.append(entry)

    rows = [dt.make_row(tiers, dict(zip(tiers, omegas)), index=i,
                        num_days=FULL_YEAR, provisional=provisional, rho_h2=rho)
            for i, omegas in enumerate(kept, start=1)]
    wave_dir = os.path.join(waves_root, wave_name or f"stage2_{scenario}_n0")
    dt.write_wave(dt.rows_to_matrix(rows, tiers), wave_dir, tiers,
                  sobol={"seed": seed, "skip": 0, "n": size,
                         "n_drawn_total": n_drawn_total,
                         "lattice": [float(w) for w in STAGE2_LATTICE],
                         "scipy_version": scipy.__version__},
                  manifest_extra=manifest_extra)
    with open(os.path.join(wave_dir, "snap_map.json"), "w") as f:
        json.dump({"tier_order": list(tiers), "draws": snap_log}, f, indent=2)
        f.write("\n")
    return wave_dir


STAGE2_BACKFILL_README = """# stage2_backfill_C — lattice back-fill OAT rows (B = 40)

10 full-year rows riding the stage2_C_n0 submission: nuclear OAT at the 8
new-lattice levels the old [0.05, 0.5] sweep never ran (only 0.05
coincides), plus pv OAT at 0.88125 and 1.0 (the old pv box tops out at 0.8,
so those two levels are EXTRAPOLATION, not interpolation — same gap class
as nuclear). Coverage status by tier: wind lattice-matched (old box == new);
tail interpolable (old box [0.02, 1] spans the lattice); pv interpolable
below 0.8, now measured at 0.88125/1.0; nuclear measured on the full
lattice; B-scenario back-fills deferred.

Indices 1-8: nuclear at STAGE2_LATTICE[1:]; indices 9-10: pv at
STAGE2_LATTICE[7:]. Built with stage2_tiers(); bids derived (B = 20*rho,
scenario C: rho = 2.0 -> B = 40).
"""


def build_stage2_backfill(scenario, waves_root=WAVES_ROOT):
    """Stage-2 back-fill wave (prompt 27 T2): tier-level OAT rows putting
    nuclear on the full 9-level lattice and pv on the two levels above its
    old 0.8 box top. Same stage2_tiers() dict as the n0 wave so manifests
    match rows with nuclear omega > 0.5."""
    tiers, provisional = stage2_tiers()
    rho = RHO_SCENARIOS[scenario]
    rows = []
    # nuclear: the 8 levels the old [0.05, 0.5] sweep never ran
    for w in STAGE2_LATTICE[1:]:
        rows.append(dt.make_row(tiers, {"nuclear": float(w)},
                                index=len(rows) + 1, num_days=FULL_YEAR,
                                provisional=provisional, rho_h2=rho))
    # pv: extrapolation levels above the old 0.8 box top
    for w in STAGE2_LATTICE[7:]:
        rows.append(dt.make_row(tiers, {"pv": float(w)},
                                index=len(rows) + 1, num_days=FULL_YEAR,
                                provisional=provisional, rho_h2=rho))
    wave_dir = os.path.join(waves_root, f"stage2_backfill_{scenario}")
    dt.write_wave(dt.rows_to_matrix(rows, tiers), wave_dir, tiers, sobol=None)
    with open(os.path.join(wave_dir, "README.md"), "w") as f:
        f.write(STAGE2_BACKFILL_README)
    return wave_dir


STAGE2_N0B_SIZE = 16  # top-up 16 -> 32 (T4 GO recommendation, Kay 09-21)

STAGE2_N0B_README = """# stage2_C_n0b — n0 top-up 16 -> 32 (prompt 27; Kay GO 09-21)

16 more full-year rows CONTINUING the stage2_C_n0 scrambled-Sobol
sequence (TOPUP_RECOMMENDATION.md mechanics, doc 14 SS5.1): same d = 6
engine and seed, skip = n_drawn_total read from the n0 manifest (never
re-seed), global draws 17+, snapped to STAGE2_LATTICE, deduped against
ALL kept post-snap rows (the n0 16 and this wave's own) with block
redraws on collision. Wave-local indices 1-16 (SGE contract); the
manifest's sobol dict records skip, the cumulative n_drawn_total for the
NEXT continuation, and continues_wave = stage2_C_n0. snap_map.json draws
are numbered by GLOBAL sequence position.

Submission was DEFERRED behind the 3 priority pairgrid waves (Kay
09-21); those completed 09-21, so this wave is clear to submit ON CRC
from inside this directory: `bash submit_this.sh` (d6 guard + pull,
array without -tc, chained collector with email).
"""


def _write_stage2_n0b_support(wave_dir, wave_name):
    """Single-wave submit + collector, rendered from the pairgrid templates
    (same automation pattern incl. the 5-retry push loop) with the stage-2
    bot identity and task count."""
    subs = {"@WAVE@": wave_name, "@N@": str(STAGE2_N0B_SIZE)}

    def render(template):
        for key, val in subs.items():
            template = template.replace(key, val)
        return (template
                .replace("pairgrid-bot", "stage2-bot")
                .replace("(prompt 28 T1)", "(prompt 27 n0b top-up)")
                .replace("(prompt 28 T1;", "(prompt 27 n0b top-up;"))

    with open(os.path.join(wave_dir, "README.md"), "w") as f:
        f.write(STAGE2_N0B_README)
    for fname, template in (("submit_this.sh", PAIRGRID_SUBMIT),
                            (f"collect_{wave_name}.sh", PAIRGRID_COLLECTOR)):
        path = os.path.join(wave_dir, fname)
        with open(path, "w") as f:
            f.write(render(template))
        os.chmod(path, 0o755)


def build_stage2_n0b(scenario, waves_root=WAVES_ROOT):
    """Stage-2 n0 top-up (prompt 27 T4 GO, Kay 09-21): rows 17-32 of the
    SAME d = 6 sequence as stage2_C_n0 — skip = n_drawn_total from the n0
    manifest (never re-seed), snap to the lattice, dedupe against all kept
    post-snap rows across BOTH waves, block redraws on collision
    (TOPUP_RECOMMENDATION.md mechanics)."""
    tiers, provisional = stage2_tiers()
    rho = RHO_SCENARIOS[scenario]
    lo, hi = float(STAGE2_LATTICE[0]), float(STAGE2_LATTICE[-1])

    n0_dir = os.path.join(waves_root, f"stage2_{scenario}_n0")
    with open(os.path.join(n0_dir, "manifest.json")) as f:
        n0_sobol = json.load(f)["sobol"]
    assert n0_sobol["seed"] == SOBOL_SEED, "n0 manifest seed mismatch"
    start_skip = int(n0_sobol["n_drawn_total"])
    with open(os.path.join(n0_dir, "design_matrix.csv"), newline="") as f:
        # decimal-clean lattice values round-trip exactly through float()
        seen = {tuple(float(row[f"{t}_omega"]) for t in tiers)
                for row in csv.DictReader(f)}
    assert len(seen) == n0_sobol["n"], "n0 design matrix has duplicate rows?"

    kept, snap_log = [], []
    n_drawn_total = start_skip
    while len(kept) < STAGE2_N0B_SIZE:
        block = (STAGE2_N0B_SIZE if n_drawn_total == start_skip
                 else STAGE2_N0B_SIZE - len(kept))
        points = dt.generate_sobol(block, SOBOL_SEED, skip=n_drawn_total,
                                   d=len(tiers))
        n_drawn_total += block
        for offset, unit in enumerate(points):
            pre = lo + unit * (hi - lo)
            post = _snap_to_lattice(pre)
            key = tuple(float(w) for w in post)
            entry = {"draw": n_drawn_total - block + offset + 1,  # GLOBAL
                     "pre_snap": [float(w) for w in pre],
                     "post_snap": [float(w) for w in post],
                     "kept_index": None}
            if key not in seen and len(kept) < STAGE2_N0B_SIZE:
                seen.add(key)
                kept.append(post)
                entry["kept_index"] = len(kept)
            snap_log.append(entry)

    rows = [dt.make_row(tiers, dict(zip(tiers, omegas)), index=i,
                        num_days=FULL_YEAR, provisional=provisional, rho_h2=rho)
            for i, omegas in enumerate(kept, start=1)]
    wave_name = f"stage2_{scenario}_n0b"
    wave_dir = os.path.join(waves_root, wave_name)
    dt.write_wave(dt.rows_to_matrix(rows, tiers), wave_dir, tiers,
                  sobol={"seed": SOBOL_SEED, "skip": start_skip,
                         "n": STAGE2_N0B_SIZE,
                         "n_drawn_total": n_drawn_total,
                         "continues_wave": f"stage2_{scenario}_n0",
                         "lattice": [float(w) for w in STAGE2_LATTICE],
                         "scipy_version": scipy.__version__})
    with open(os.path.join(wave_dir, "snap_map.json"), "w") as f:
        json.dump({"tier_order": list(tiers), "draws": snap_log}, f, indent=2)
        f.write("\n")
    _write_stage2_n0b_support(wave_dir, wave_name)
    return wave_dir


# --- pair-grid waves (prompt 28 T1; Kay scope ruling 09-20) -------------------
# ALL 15 tier pairs get full 9x9 grids at scenario C; wind_303 x wind_317 is
# NOT built here — it already exists as contour_303x317_C (equivalence up to
# the linspace-ulp caveat is verified in the analysis provenance, never
# assumed). 14 new waves, STAGE2_LATTICE x STAGE2_LATTICE each.

PAIRGRID_SCENARIO = "C"

PAIRGRID_PAIRS = [
    (a, b)
    for i, a in enumerate(sorted(TIERS))
    for b in sorted(TIERS)[i + 1:]
    if (a, b) != ("wind_303", "wind_317")
]


def pairgrid_wave_name(tier_a, tier_b, scenario=PAIRGRID_SCENARIO):
    """Directory name only — tier keys contain underscores, so pair identity
    is READ FROM THE MANIFEST downstream, never parsed back out of this."""
    return f"pairgrid_{tier_a}_{tier_b}_{scenario}"


PAIRGRID_README = """# @WAVE@ — 9x9 pair grid at scenario @SCENARIO@ (prompt 28)

Pair: **@TIER_A@** (outer axis) x **@TIER_B@** (inner axis), sorted tier
order. 81 full-year rows, index = 9*i_a + i_b + 1 (row-major, matching
build_contour's convention). Both axes are STAGE2_LATTICE (9 decimal-clean
levels, 0.05..1.0 inclusive). The other four tiers are ABSENT (NaN in the
design matrix — absent means no PEM at those sites, never omega=0). Bids
derived: B = 20*rho_H2 = 40 at rho = 2.0 (scenario @SCENARIO@). Pair
identity and lattice are recorded in manifest.json — read them from there,
never from this directory's name (tier keys contain underscores).

Submit ON CRC from inside this directory: `bash submit_this.sh`
(d6 guard + pull, array without -tc, chained collector with email).
Nuclear omega > 0.5 rows are validated by the 09-19 omega=1.0 3-day smoke
(JID 1458448, SMOKE PASS).
"""

PAIRGRID_SUBMIT = """#!/bin/bash
# @WAVE@ — submit array + chained collector (prompt 28 T1).
# Run ON CRC from INSIDE this wave directory:  bash submit_this.sh
# Generated by campaign/make_batches.py — regenerate rather than hand-edit.

set -euo pipefail

WAVE_DIR="$PWD"
TRIAL_DIR="$(cd "$PWD/../../.." && pwd)"
REPO_DIR="$(cd "$TRIAL_DIR/.." && pwd)"

BRANCH="$(git -C "$REPO_DIR" branch --show-current)"
[[ "$BRANCH" == "d6" ]] || { echo "ABORT: repo on '$BRANCH', expected d6"; exit 1; }
git -C "$REPO_DIR" pull --rebase --autostash origin d6

J=$(qsub -terse -t 1-@N@ @WAVE@_array.sh | cut -d. -f1)
[[ "$J" =~ ^[0-9]+$ ]] || { echo "BAD JID: $J"; exit 1; }
echo "@WAVE@ array submitted: J=$J (@N@ tasks, no -tc)"
qsub -hold_jid "$J" -cwd -M ylu28@nd.edu -m ea collect_@WAVE@.sh
echo "collector submitted (holds on $J only — never on other waves)"
qstat -u ylu28
"""

PAIRGRID_COLLECTOR = """#!/bin/bash
#$ -N collect_@WAVE@
#$ -q long
#$ -cwd

# Chained collector for @WAVE@ (prompt 28 T1; single-wave adaptation of the
# prompt-27 collector spec — see stage2_backfill_C/collect_stage2.sh).
# Submitted by submit_this.sh with -hold_jid on THIS wave's array only.
# Generated by campaign/make_batches.py — regenerate rather than hand-edit.
#
# Order of operations (deliberate):
#   1. integrity gate FIRST, self-contained (never resubmit_missing.py);
#   2. on any gap: FAILED_@WAVE@.md marker, commit + push the marker ONLY;
#   3. on pass: summarize, bot-identity commit of explicit paths, commit
#      BEFORE pull --rebase, push with RETRY LOOP (up to 5 attempts,
#      randomized sleep — up to 4 concurrent bot pushers share d6, so the
#      stage2 retry-once is insufficient here).

set -euo pipefail

WAVE_DIR="$PWD"
TRIAL_DIR="$(cd "$PWD/../../.." && pwd)"

source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate PCM0826

CAMPAIGN_DIR="$(cd "$WAVE_DIR/../.." && pwd)"
REPO_DIR="$(cd "$TRIAL_DIR/.." && pwd)"

BOT=(-c user.name="pairgrid-bot" -c user.email="pairgrid-bot@noreply.github.com")

push_with_retries() {
    local attempt
    for attempt in 1 2 3 4 5; do
        if git -C "$REPO_DIR" push origin d6; then
            return 0
        fi
        echo "push rejected (attempt $attempt/5) — rebase and retry"
        sleep $((30 + RANDOM % 60))
        git -C "$REPO_DIR" pull --rebase --autostash origin d6
    done
    if git -C "$REPO_DIR" push origin d6; then
        return 0
    fi
    echo "PUSH FAILED after 5 retries — stopping with status visible:"
    git -C "$REPO_DIR" status
    git -C "$REPO_DIR" log --oneline -3
    exit 1
}

# --- 1. integrity gate: sentinel count vs the design matrix itself ----------
missing=$(python - "$WAVE_DIR" <<'EOF'
import sys, csv, os
wdir = sys.argv[1]
with open(os.path.join(wdir, "design_matrix.csv"), newline="") as f:
    idx = [int(row["index"]) for row in csv.DictReader(f)]
missing = [i for i in idx
           if not os.path.isfile(os.path.join(
               wdir, "runs", f"run_index_{i}", "overall_simulation_output.csv"))]
print(" ".join(str(i) for i in missing))
EOF
)
if [[ -n "$missing" ]]; then
    marker="$WAVE_DIR/FAILED_@WAVE@.md"
    {
        echo "# FAILED — @WAVE@ incomplete at collection"
        echo
        echo "Missing run indices (no overall_simulation_output.csv):"
        echo
        for i in $missing; do echo "- $i"; done
        echo
        echo "Recovery: Kay runs resubmit_missing.py (interactive) or a"
        echo "manual 'qsub -t a-b' per contiguous gap, then re-runs this"
        echo "collector. Generated $(date -u +%FT%TZ) by collect_@WAVE@.sh."
    } > "$marker"
    git -C "$REPO_DIR" add -- "$marker"
    git -C "$REPO_DIR" "${BOT[@]}" commit -m "pairgrid-bot: FAILED marker (@WAVE@ incomplete)"
    push_with_retries
    echo "GATE FAIL: missing indices: $missing — marker pushed, no partial CSVs."
    exit 1
fi
echo "GATE PASS: @WAVE@ complete ($(ls -d "$WAVE_DIR"/runs/run_index_* | wc -l) run dirs)"

# --- 2. summarize this wave only --------------------------------------------
python "$CAMPAIGN_DIR/summarize_wave.py" "$WAVE_DIR"

# --- 3. bot commit (explicit paths only), commit BEFORE pull --rebase, push --
git -C "$REPO_DIR" add -- "$WAVE_DIR/objectives.csv" "$WAVE_DIR/site_detail.csv"
git -C "$REPO_DIR" "${BOT[@]}" commit -m "pairgrid-bot: @WAVE@ results"
push_with_retries
echo "collect_@WAVE@ done: objectives pushed"
"""


def _write_pairgrid_support(wave_dir, wave_name, scenario, tier_a, tier_b):
    subs = {"@WAVE@": wave_name, "@SCENARIO@": scenario,
            "@TIER_A@": tier_a, "@TIER_B@": tier_b, "@N@": "81"}

    def render(template):
        for key, val in subs.items():
            template = template.replace(key, val)
        return template

    with open(os.path.join(wave_dir, "README.md"), "w") as f:
        f.write(render(PAIRGRID_README))
    for fname, template in (("submit_this.sh", PAIRGRID_SUBMIT),
                            (f"collect_{wave_name}.sh", PAIRGRID_COLLECTOR)):
        path = os.path.join(wave_dir, fname)
        with open(path, "w") as f:
            f.write(render(template))
        os.chmod(path, 0o755)


def build_pairgrid(tier_a, tier_b, scenario=PAIRGRID_SCENARIO,
                   waves_root=WAVES_ROOT):
    """One 9x9 pair-grid wave (prompt 28 T1): STAGE2_LATTICE x STAGE2_LATTICE
    directly (never omega_grid over a box), row-major with the sorted-first
    tier as the OUTER axis (build_contour's convention), other four tiers
    absent, bids derived from the scenario rho. Built with stage2_tiers()
    so manifests match rows with nuclear omega > 0.5 (validated by the
    09-19 omega=1.0 smoke, JID 1458448)."""
    assert (tier_a, tier_b) == tuple(sorted((tier_a, tier_b))), (
        f"pair must be in sorted tier order, got ({tier_a}, {tier_b})"
    )
    tiers, provisional = stage2_tiers()
    assert tier_a in tiers and tier_b in tiers and tier_a != tier_b
    rho = RHO_SCENARIOS[scenario]
    rows = []
    for i, wa in enumerate(STAGE2_LATTICE):          # outer: tier_a
        for j, wb in enumerate(STAGE2_LATTICE):      # inner: tier_b
            rows.append(dt.make_row(
                tiers, {tier_a: float(wa), tier_b: float(wb)},
                index=len(STAGE2_LATTICE) * i + j + 1, num_days=FULL_YEAR,
                provisional=provisional, rho_h2=rho))
    wave_name = pairgrid_wave_name(tier_a, tier_b, scenario)
    wave_dir = os.path.join(waves_root, wave_name)
    dt.write_wave(dt.rows_to_matrix(rows, tiers), wave_dir, tiers, sobol=None,
                  manifest_extra={"pair": [tier_a, tier_b],
                                  "lattice": [float(w) for w in STAGE2_LATTICE]})
    _write_pairgrid_support(wave_dir, wave_name, scenario, tier_a, tier_b)
    return wave_dir


WAVE_MAX_CONCURRENT = {"stage2_C_n0": 12, "stage2_backfill_C": 12}
# Pairgrid waves run with NO -tc line at all (None -> submit_array omits it;
# Kay 09-20: licenses fine). Legacy entries above and the .get(..., 20)
# fallback stay untouched — frozen waves are never regenerated.
WAVE_MAX_CONCURRENT.update({
    pairgrid_wave_name(a, b): None for a, b in PAIRGRID_PAIRS
})
WAVE_MAX_CONCURRENT["stage2_C_n0b"] = None  # top-up: no -tc (Kay 09-19 ruling)

BUILDERS = {"pilot": build_pilot, "screening": build_screening, "n0": build_n0,
            "placebo": build_placebo,
            # v3 derived-bid waves (math-log §4); contour_A first — rho = 1.0
            # is the current-market headline
            "contour_303x317_A": functools.partial(build_contour_303x317, "A"),
            "contour_303x317_B": functools.partial(build_contour_303x317, "B"),
            "contour_303x317_C": functools.partial(build_contour_303x317, "C"),
            "sweep_B": functools.partial(build_sweep, "B"),
            "sweep_C": functools.partial(build_sweep, "C"),
            # Stage-2 scenario C on the discrete lattice (prompt 27)
            "stage2_C_n0": functools.partial(build_stage2_n0, "C"),
            "stage2_backfill_C": functools.partial(build_stage2_backfill, "C"),
            # n0 top-up 16 -> 32 (prompt 27 T4 GO; Kay 09-21, deferred behind
            # the priority pairgrids — those completed 09-21)
            "stage2_C_n0b": functools.partial(build_stage2_n0b, "C")}

# 14 pair-grid waves (prompt 28). Invoke builders PER-WAVE BY NAME only —
# `make_batches.py all` (the default argv!) would regenerate legacy builders
# over frozen, in-flight wave dirs.
BUILDERS.update({
    pairgrid_wave_name(a, b): functools.partial(build_pairgrid, a, b)
    for a, b in PAIRGRID_PAIRS
})


# --- Stage-2 BO rounds (prompt 30) --------------------------------------------
# One wave per q-ParEGO round: 8 designs chosen by analysis/bo_stage2/
# acquire_next.py (which calls build_bo_round directly — these waves are
# NOT in BUILDERS: their designs come from the acquisition, not a builder).
# The automated chain per round: array (8 tasks) -> collector -> acquisition
# job, submitted as ONE triple by the wave's submit_this.sh, which itself
# appends the `SUBMITTED r<k>: array=<J> collector=<C> acq=<A>` line to
# ROUND_LOG.md and pushes it (the stop-NOW qdel targets). Headers carry
# `#$ -r n` on all three hops: a node-failed task becomes a detected gap,
# never a silent SGE rerun.

BO_SIZE = 8
BO_EMAIL = "ylu28@nd.edu"


def bo_wave_name(k):
    return f"bo_C_r{k}"


BO_ARRAY_TEMPLATE = """#!/bin/bash
#$ -N @WAVE@_array
#$ -q long
#$ -cwd
#$ -t 1-8
#$ -r n

# Generated by campaign/make_batches.py (prompt 30) — regenerate rather
# than hand-edit. Submitted by this wave's submit_this.sh (never by hand).

set -euo pipefail

GUROBI_MODULE="gurobi"

WAVE_DIR="$PWD"
TRIAL_DIR="$(cd "$PWD/../../.." && pwd)"
mkdir -p "$WAVE_DIR/runs"

source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate PCM0826
module load "$GUROBI_MODULE"

eval "$(python "$TRIAL_DIR/campaign/get_row.py" "$SGE_TASK_ID" "$WAVE_DIR/design_matrix.csv")"

python "$TRIAL_DIR/multi_pem/multi_PEM_PCM.py" \\
    --index "$INDEX" \\
    --num_days "$NUM_DAYS" \\
    --start_date "$START_DATE" \\
    --output_directory "$WAVE_DIR/runs/run" \\
    --retrofit_gen_dict "$(cat "$WAVE_DIR/retrofit_gen_dict_${INDEX}.json")"
"""

BO_COLLECTOR = """#!/bin/bash
#$ -N collect_@WAVE@
#$ -q long
#$ -cwd
#$ -r n

# Chained collector for @WAVE@ (prompt 30; single-wave, bo-bot identity,
# 5-retry randomized-backoff push). Generated by campaign/make_batches.py.
# Submitted by submit_this.sh with -hold_jid on THIS wave's array only.

set -euo pipefail

WAVE_DIR="$PWD"
TRIAL_DIR="$(cd "$PWD/../../.." && pwd)"

source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate PCM0826
export PYTHONNOUSERSITE=1  # ~/.local shadowing hazard (house-proven)

CAMPAIGN_DIR="$(cd "$WAVE_DIR/../.." && pwd)"
REPO_DIR="$(cd "$TRIAL_DIR/.." && pwd)"

BOT=(-c user.name="bo-bot" -c user.email="bo-bot@noreply.github.com")

push_with_retries() {
    local attempt
    for attempt in 1 2 3 4 5; do
        if git -C "$REPO_DIR" push origin d6; then
            return 0
        fi
        echo "push rejected (attempt $attempt/5) — rebase and retry"
        sleep $((30 + RANDOM % 60))
        git -C "$REPO_DIR" pull --rebase --autostash origin d6
    done
    git -C "$REPO_DIR" push origin d6 || {
        echo "PUSH FAILED after 5 retries:"
        git -C "$REPO_DIR" status
        exit 1
    }
}

missing=$(python - "$WAVE_DIR" <<'EOF'
import sys, csv, os
wdir = sys.argv[1]
with open(os.path.join(wdir, "design_matrix.csv"), newline="") as f:
    idx = [int(row["index"]) for row in csv.DictReader(f)]
missing = [i for i in idx
           if not os.path.isfile(os.path.join(
               wdir, "runs", f"run_index_{i}", "overall_simulation_output.csv"))]
print(" ".join(str(i) for i in missing))
EOF
)
if [[ -n "$missing" ]]; then
    marker="$WAVE_DIR/FAILED_@WAVE@.md"
    {
        echo "# FAILED — @WAVE@ incomplete at collection"
        echo
        echo "Missing run indices: $missing"
        echo
        echo "The chained acquisition job will see this marker and stop the"
        echo "round (no proposals). Recovery: Kay diagnoses, resubmits the"
        echo "gap (qsub -t a-b @WAVE@_array.sh), re-runs this collector,"
        echo "then qsubs acquire_job.sh per the WEDGED/FAILED recipe in"
        echo "ROUND_LOG.md. Generated $(date -u +%FT%TZ)."
    } > "$marker"
    git -C "$REPO_DIR" add -- "$marker"
    git -C "$REPO_DIR" "${BOT[@]}" commit -m "bo-bot: FAILED marker (@WAVE@ incomplete)"
    push_with_retries
    echo "GATE FAIL: missing indices: $missing"
    exit 1
fi
echo "GATE PASS: @WAVE@ complete"

python "$CAMPAIGN_DIR/summarize_wave.py" "$WAVE_DIR"

git -C "$REPO_DIR" add -- "$WAVE_DIR/objectives.csv" "$WAVE_DIR/site_detail.csv"
git -C "$REPO_DIR" "${BOT[@]}" commit -m "bo-bot: @WAVE@ results"
push_with_retries
echo "collect_@WAVE@ done"
"""

BO_SUBMIT = """#!/bin/bash
# @WAVE@ — submit the WHOLE round triple: array -> collector -> acquisition
# (prompt 30). Invocable from anywhere (block #1 for r1; acquire_job.sh for
# later rounds). Generated by campaign/make_batches.py.
cd "$(dirname "${BASH_SOURCE[0]}")"
set -euo pipefail

WAVE_DIR="$PWD"
TRIAL_DIR="$(cd "$PWD/../../.." && pwd)"
REPO_DIR="$(cd "$TRIAL_DIR/.." && pwd)"
BO_DIR="$TRIAL_DIR/campaign/analysis/bo_stage2"

BRANCH="$(git -C "$REPO_DIR" branch --show-current)"
[[ "$BRANCH" == "d6" ]] || { echo "ABORT: repo on '$BRANCH', expected d6"; exit 1; }
git -C "$REPO_DIR" pull --rebase --autostash origin d6

EMAIL=(-M ylu28@nd.edu -m ea)
mkdir -p "$BO_DIR/logs"

J=$(qsub -terse -t 1-8 "${EMAIL[@]}" @WAVE@_array.sh | cut -d. -f1)
[[ "$J" =~ ^[0-9]+$ ]] || { echo "BAD ARRAY JID: $J"; exit 1; }
C=$(qsub -terse -hold_jid "$J" -cwd "${EMAIL[@]}" collect_@WAVE@.sh)
[[ "$C" =~ ^[0-9]+$ ]] || { echo "BAD COLLECTOR JID: $C"; exit 1; }
A=$(qsub -terse -hold_jid "$C" -cwd -N acq_@WAVE@ -v BO_ROUND=@K@ \\
    -o "$BO_DIR/logs/" -e "$BO_DIR/logs/" "${EMAIL[@]}" \\
    "$BO_DIR/acquire_job.sh")
[[ "$A" =~ ^[0-9]+$ ]] || { echo "BAD ACQ JID: $A"; exit 1; }

echo "SUBMITTED r@K@: array=$J collector=$C acq=$A" >> "$BO_DIR/ROUND_LOG.md"
BOT=(-c user.name="bo-bot" -c user.email="bo-bot@noreply.github.com")
git -C "$REPO_DIR" add -- "$BO_DIR/ROUND_LOG.md"
git -C "$REPO_DIR" "${BOT[@]}" commit -m "bo-bot: SUBMITTED r@K@ (array=$J collector=$C acq=$A)"
for attempt in 1 2 3 4 5; do
    git -C "$REPO_DIR" push origin d6 && break
    echo "push rejected (attempt $attempt/5) — rebase and retry"
    sleep $((30 + RANDOM % 60))
    git -C "$REPO_DIR" pull --rebase --autostash origin d6
    [[ "$attempt" == 5 ]] && { git -C "$REPO_DIR" push origin d6 || exit 1; }
done
echo "SUBMITTED r@K@: array=$J collector=$C acq=$A"
qstat -u ylu28 || true
"""


def _write_bo_support(wave_dir, k):
    wave_name = bo_wave_name(k)

    def render(template):
        return template.replace("@WAVE@", wave_name).replace("@K@", str(k))

    for fname, template in ((f"{wave_name}_array.sh", BO_ARRAY_TEMPLATE),
                            (f"collect_{wave_name}.sh", BO_COLLECTOR),
                            ("submit_this.sh", BO_SUBMIT)):
        path = os.path.join(wave_dir, fname)
        with open(path, "w") as f:
            f.write(render(template))
        os.chmod(path, 0o755)


def build_bo_round(k, designs, manifest_extra=None, waves_root=WAVES_ROOT):
    """One BO round wave: 8 lattice designs from the q-ParEGO acquisition
    (prompt 30). `designs` is an (8, 6) omega array in sorted-tier order.
    REFUSES an existing wave dir (write_wave alone overwrites silently) —
    the double-spend guard at the wave level."""
    wave_name = bo_wave_name(k)
    wave_dir = os.path.join(waves_root, wave_name)
    if os.path.exists(wave_dir):
        raise RuntimeError(
            f"REFUSED: {wave_dir} already exists — a bo_C round is never "
            "regenerated (double-spend guard; see prompt 30 idempotency)")
    designs = np.asarray(designs, dtype=float)
    assert designs.shape == (BO_SIZE, 6), designs.shape
    lat = np.round(np.asarray(STAGE2_LATTICE, float), 10)
    assert all(np.isclose(lat, w, atol=1e-12).any()
               for row in designs for w in row), "off-lattice design"
    assert len({tuple(row) for row in designs.round(10).tolist()}) == BO_SIZE, \
        "duplicate designs in batch"

    tiers, provisional = stage2_tiers()
    sorted_tiers = sorted(tiers)
    rows = [dt.make_row(tiers,
                        {t: float(w) for t, w in zip(sorted_tiers, row)},
                        index=i, num_days=FULL_YEAR,
                        provisional=provisional, rho_h2=RHO_SCENARIOS["C"])
            for i, row in enumerate(designs, start=1)]
    extra = {"bo_round": k, "lattice": [float(w) for w in STAGE2_LATTICE]}
    extra.update(manifest_extra or {})
    dt.write_wave(dt.rows_to_matrix(rows, tiers), wave_dir, tiers, sobol=None,
                  manifest_extra=extra)
    _write_bo_support(wave_dir, k)
    return wave_dir


# --- Stage-2 random baseline (prompt 34) --------------------------------------
# ONE i.i.d. pool of 48 uniform lattice designs (3 provenance blocks of 16),
# evaluated once and compared with the 16 BO picks against the same 32 Sobol
# starts. Exclusion keys are lattice-INDEX tuples in sorted(TIERS) order —
# never raw floats, never CSV column order (which is TIER_ORDER).

RANDOM_SEED_BASE = 20261011
RANDOM_EXCLUDE_WAVES = ["stage2_C_n0", "stage2_C_n0b", "bo_C_r1", "bo_C_r2"]
RANDOM_EMAIL = "ylu28@nd.edu"
# §3.4 S2 recipe set, checked against the 3 BO_STAGE2 knees BEFORE submission
# and frozen in the manifest (never loosened after results)
RANDOM_RECIPE = {"nuclear_omega": 0.05, "total_gw": [1.6, 2.0],
                 "wind_303_317_share_min": 0.5, "wind_122_omega_max": 0.2875}

RANDOM_README = """# random_C — Stage-2 random baseline (prompt 34)

48 uniform random STAGE2_LATTICE designs at scenario C (rho = 2.0, B = 40),
all six tiers present, none repeating the 48 already-evaluated designs
(stage2_C_n0, stage2_C_n0b, bo_C_r1, bo_C_r2). Analyzed as ONE i.i.d. pool
against the BO campaign (analysis/random_baseline/). Draw procedure, seeds,
exclusion hash, the full draw log, the frozen recipe set and the §5
decision are in manifest.json["random_baseline"].

Indices 1..48 = 16*(arm-1) + arm_order; `arm` is provenance only.

Submit ON CRC from the login node (compute nodes are not submit hosts):
`cd trial_0826/campaign/waves/random_C && bash submit_this.sh`
(d6 guard + pull, array without -tc / without email, chained collector
with email; appends the SUBMITTED line to analysis/random_baseline/
PROGRESS.md and pushes it).
"""

RANDOM_SUBMIT = """#!/bin/bash
# @WAVE@ — submit array + chained collector (prompt 34). Run ON CRC from the
# LOGIN node (compute nodes are not submit hosts); invocable from anywhere.
# Generated by campaign/make_batches.py — regenerate rather than hand-edit.
cd "$(dirname "${BASH_SOURCE[0]}")"
set -euo pipefail

WAVE_DIR="$PWD"
TRIAL_DIR="$(cd "$PWD/../../.." && pwd)"
REPO_DIR="$(cd "$TRIAL_DIR/.." && pwd)"
PROGRESS="$TRIAL_DIR/campaign/analysis/random_baseline/PROGRESS.md"

BRANCH="$(git -C "$REPO_DIR" branch --show-current)"
[[ "$BRANCH" == "d6" ]] || { echo "ABORT: repo on '$BRANCH', expected d6"; exit 1; }
git -C "$REPO_DIR" pull --rebase --autostash origin d6

# array: NO email flags (one email per task otherwise), no -tc
J=$(qsub -terse -r n -t 1-@N@ @WAVE@_array.sh | cut -d. -f1)
[[ "$J" =~ ^[0-9]+$ ]] || { echo "BAD ARRAY JID: $J"; exit 1; }
echo "@WAVE@ array submitted: J=$J (@N@ tasks, no -tc)"
C=$(qsub -terse -r n -hold_jid "$J" -cwd -M @EMAIL@ -m ea collect_@WAVE@.sh)
[[ "$C" =~ ^[0-9]+$ ]] || { echo "BAD COLLECTOR JID: $C"; exit 1; }
echo "collector submitted: C=$C (holds on $J only)"

echo "SUBMITTED @WAVE@: array=$J collector=$C" >> "$PROGRESS"
BOT=(-c user.name="stage2-bot" -c user.email="stage2-bot@noreply.github.com")
git -C "$REPO_DIR" add -- "$PROGRESS"
git -C "$REPO_DIR" "${BOT[@]}" commit -m "stage2-bot: SUBMITTED @WAVE@ (array=$J collector=$C)"
for attempt in 1 2 3 4 5; do
    git -C "$REPO_DIR" push origin d6 && break
    echo "push rejected (attempt $attempt/5) — rebase and retry"
    sleep $((30 + RANDOM % 60))
    git -C "$REPO_DIR" pull --rebase --autostash origin d6
    [[ "$attempt" == 5 ]] && { git -C "$REPO_DIR" push origin d6 || exit 1; }
done
echo "SUBMITTED @WAVE@: array=$J collector=$C"
qstat -u ylu28 || true
"""

RANDOM_COLLECTOR_CHECK = '''
# --- 2b. objectives check: @N@ rows, finite M columns ------------------------
if ! python - "$WAVE_DIR/objectives.csv" <<'EOF'
import sys
import numpy as np, pandas as pd
ob = pd.read_csv(sys.argv[1])
M = ["load_shed_mwh", "true_curtailment_mwh", "total_cost_less_synthetic_usd"]
ok = (len(ob) == @N@ and sorted(ob["index"]) == list(range(1, @N@ + 1))
      and np.isfinite(ob[M].to_numpy(float)).all())
print(f"objectives check: rows={len(ob)} ok={ok}")
sys.exit(0 if ok else 1)
EOF
then
    marker="$WAVE_DIR/FAILED_@WAVE@.md"
    {
        echo "# FAILED — @WAVE@ objectives.csv failed the @N@-row / finite-M check"
        echo
        echo "All sentinels were present but the summary is not usable."
        echo "Generated $(date -u +%FT%TZ) by collect_@WAVE@.sh."
    } > "$marker"
    git -C "$REPO_DIR" add -- "$marker"
    git -C "$REPO_DIR" "${BOT[@]}" commit -m "stage2-bot: FAILED marker (@WAVE@ objectives check)"
    push_with_retries
    exit 1
fi
'''


def _render_random_collector(wave_name, n):
    """PAIRGRID_COLLECTOR (5-retry push, collector-only email) merged with
    BO_COLLECTOR's `-r n` header + PYTHONNOUSERSITE, plus the stale-FAILED
    cleanup after GATE PASS and the post-summarize objectives check."""
    t = PAIRGRID_COLLECTOR
    t = t.replace("#$ -cwd\n", "#$ -cwd\n#$ -r n\n", 1)
    t = t.replace("conda activate PCM0826\n",
                  "conda activate PCM0826\n"
                  "export PYTHONNOUSERSITE=1  # ~/.local shadowing hazard (house-proven)\n", 1)
    gate = 'echo "GATE PASS: @WAVE@ complete'
    i = t.index(gate)
    j = t.index("\n", i) + 1
    t = (t[:j]
         + '# a stale FAILED marker from an earlier attempt is removed in the results commit\n'
         + '[[ -f "$WAVE_DIR/FAILED_@WAVE@.md" ]] && '
           'git -C "$REPO_DIR" rm -q -- "$WAVE_DIR/FAILED_@WAVE@.md"\n'
         + t[j:])
    summ = 'python "$CAMPAIGN_DIR/summarize_wave.py" "$WAVE_DIR"\n'
    assert summ in t
    t = t.replace(summ, summ + RANDOM_COLLECTOR_CHECK, 1)
    t = (t.replace("pairgrid-bot", "stage2-bot")
          .replace("(prompt 28 T1; single-wave adaptation of the\n# prompt-27 collector spec — see stage2_backfill_C/collect_stage2.sh).",
                   "(prompt 34; PAIRGRID_COLLECTOR + BO_COLLECTOR merge)."))
    return t.replace("@WAVE@", wave_name).replace("@N@", str(n))


def _write_random_support(wave_dir, wave_name, n):
    with open(os.path.join(wave_dir, "README.md"), "w") as f:
        f.write(RANDOM_README)
    submit = (RANDOM_SUBMIT.replace("@WAVE@", wave_name)
              .replace("@N@", str(n)).replace("@EMAIL@", RANDOM_EMAIL))
    for fname, text in (("submit_this.sh", submit),
                        (f"collect_{wave_name}.sh",
                         _render_random_collector(wave_name, n))):
        path = os.path.join(wave_dir, fname)
        with open(path, "w") as f:
            f.write(text)
        os.chmod(path, 0o755)


def _lattice_index_key(omegas):
    """Lattice-index tuple for one design (omegas in sorted(TIERS) order)."""
    lat = np.asarray(STAGE2_LATTICE, dtype=float)
    key = []
    for w in omegas:
        i = int(np.argmin(np.abs(lat - w)))
        assert abs(lat[i] - w) < 1e-12, f"off-lattice omega {w!r}"
        key.append(i)
    return tuple(key)


def recipe_check(omegas_by_tier, tiers):
    """§3.4 S2 recipe membership for one design (dict tier -> omega)."""
    mw = {t: omegas_by_tier[t] * sum(tiers[t]["gen_pmax"].values())
          if "gen_pmax" in tiers[t] else None for t in tiers}
    mw["nuclear"] = omegas_by_tier["nuclear"] * NUCLEAR_PMAX_MW
    total = sum(mw.values())
    r = RANDOM_RECIPE
    return {"total_mw": total,
            "wind_share": (mw["wind_303"] + mw["wind_317"]) / total,
            "in_recipe": bool(
                abs(omegas_by_tier["nuclear"] - r["nuclear_omega"]) < 1e-12
                and r["total_gw"][0] * 1e3 <= total <= r["total_gw"][1] * 1e3
                and (mw["wind_303"] + mw["wind_317"]) / total >= r["wind_303_317_share_min"]
                and omegas_by_tier["wind_122"] <= r["wind_122_omega_max"] + 1e-12)}


NUCLEAR_PMAX_MW = 400.0  # 121_NUCLEAR_1 PMax (gen.csv); checked in the builder
RANDOM_KNEES = {"n0b#8": ("stage2_C_n0b", 8), "r1#2": ("bo_C_r1", 2),
                "r1#6": ("bo_C_r1", 6)}


def build_random_baseline(scenario, n_arms=3, n_per_arm=16,
                          seed_base=RANDOM_SEED_BASE, waves_root=WAVES_ROOT,
                          source_root=WAVES_ROOT):
    """The prompt-34 random baseline wave. Pre-registered draw: per block k,
    rng = default_rng(SeedSequence(seed_base).spawn(n_arms)[k-1]); per
    candidate idx = rng.integers(0, 9, size=6) in sorted(TIERS) order; reject
    if in the evaluated-48 set or already accepted in the same block; every
    draw logged. REFUSES an existing wave dir."""
    wave_name = f"random_{scenario}"
    wave_dir = os.path.join(waves_root, wave_name)
    if os.path.exists(wave_dir):
        raise RuntimeError(
            f"REFUSED: {wave_dir} already exists — the random baseline is "
            "never regenerated (pre-registered single draw; prompt 34)")
    tiers, provisional = stage2_tiers()
    sorted_tiers = sorted(tiers)
    assert NUCLEAR_PMAX_MW == load_gen_pmax()[NUCLEAR_SITE]
    lat = np.asarray(STAGE2_LATTICE, dtype=float)

    exclusion = set()
    knee_omegas = {}
    for w in RANDOM_EXCLUDE_WAVES:
        dm = pd.read_csv(os.path.join(source_root, w, "design_matrix.csv"))
        for _, row in dm.iterrows():
            om = [float(row[f"{t}_omega"]) for t in sorted_tiers]
            exclusion.add(_lattice_index_key(om))
            for name, (kw, ki) in RANDOM_KNEES.items():
                if kw == w and int(row["index"]) == ki:
                    knee_omegas[name] = dict(zip(sorted_tiers, om))
    assert len(exclusion) == 48, f"expected 48 distinct evaluated designs, got {len(exclusion)}"
    excl_sha = hashlib.sha256(
        json.dumps(sorted(exclusion)).encode()).hexdigest()

    knee_check = {k: recipe_check(v, tiers) for k, v in knee_omegas.items()}
    assert len(knee_check) == 3 and all(v["in_recipe"] for v in knee_check.values()), \
        f"recipe set R does not hold for the 3 knees: {knee_check}"

    children = np.random.SeedSequence(seed_base).spawn(n_arms)
    draws, accepted = [], []
    for k, child in enumerate(children, start=1):
        rng = np.random.default_rng(child)
        block, n_cand = [], 0
        while len(block) < n_per_arm:
            n_cand += 1
            idx = tuple(int(i) for i in rng.integers(0, len(lat), size=6))
            if idx in exclusion:
                reason = "in evaluated-48"
            elif idx in {b for b in block}:
                reason = "duplicate within block"
            else:
                reason = None
                block.append(idx)
            draws.append({"arm": k, "candidate": n_cand, "idx": list(idx),
                          "accepted": reason is None, "reason": reason})
        accepted.append(block)
    flat = [idx for block in accepted for idx in block]
    overlaps = sorted({idx for idx in flat if flat.count(idx) > 1})

    rows, arm, arm_order = [], [], []
    for k, block in enumerate(accepted, start=1):
        for o, idx in enumerate(block, start=1):
            rows.append(dt.make_row(
                tiers, {t: float(lat[i]) for t, i in zip(sorted_tiers, idx)},
                index=n_per_arm * (k - 1) + o, num_days=FULL_YEAR,
                provisional=provisional, rho_h2=RHO_SCENARIOS[scenario]))
            arm.append(k)
            arm_order.append(o)
    df = dt.rows_to_matrix(rows, tiers)
    df["arm"] = arm            # AFTER rows_to_matrix (it drops non-schema keys)
    df["arm_order"] = arm_order

    extra = {"lattice": [float(w) for w in STAGE2_LATTICE],
             "random_baseline": {
                 "prompt": "34 v2.1",
                 "seeds": {"seed_sequence_entropy": seed_base,
                           "spawn": n_arms,
                           "spawn_keys": [list(c.spawn_key) for c in children],
                           "generator": "numpy.random.default_rng (PCG64)",
                           "numpy_version": np.__version__},
                 "tier_order": sorted_tiers,
                 "exclusion_waves": RANDOM_EXCLUDE_WAVES,
                 "exclusion_sha256": excl_sha,
                 "draws": draws,
                 "cross_arm_overlaps": [list(i) for i in overlaps],
                 "recipe_R": RANDOM_RECIPE,
                 "recipe_knee_check": knee_check,
                 "sobol_continuation_arm": "OFF (prompt 34 §5 default; no "
                                           "explicit choice at build time)"}}
    dt.write_wave(df, wave_dir, tiers, sobol=None, manifest_extra=extra)
    _write_random_support(wave_dir, wave_name, len(df))
    submit_array.generate_script(wave_dir, max_concurrent=None)
    return wave_dir


WAVE_MAX_CONCURRENT["random_C"] = None  # no -tc (red line)
BUILDERS["random_C"] = functools.partial(build_random_baseline, "C")


# --- Stage-2 methods arms at scenario C (prompt 35) ---------------------------
# Start sets S2 / S3 (ONE 32-point block each from engines SOBOL_SEED + 1 / + 2)
# and Sobol continuations Q1-Q3 (16 each) are BUILDERS waves; the arm rounds
# (methods_C_<arm>_r<k>) are built by analysis/methods_C/acquire_arm.py through
# build_methods_round (NOT in BUILDERS). Every methods wave is submitted by
# analysis/methods_C/submit_ready.sh (bastion) through the GENERIC array and
# collector scripts there (env WAVE=<name>, -wd waves) — never a per-wave
# submit_this.sh. No -tc anywhere (red line).

METHODS_START_SIZE = 32
METHODS_SOBOL_SIZE = 16
METHODS_EMAIL = "ylu28@nd.edu"
METHODS_S1_WAVES = ["stage2_C_n0", "stage2_C_n0b"]


def methods_start_name(k):
    return f"methods_C_S{k}_n0"


def methods_sobol_name(j):
    return f"methods_C_Q{j}"


METHODS_README = """# @WAVE@ — prompt 35 methods arms (scenario C)

@WHAT@

Submit ONLY through `analysis/methods_C/submit_ready.sh` on the CRC bastion
(idempotent state machine; generic `methods_array.sh` + `methods_collect.sh`
with `-v WAVE=@WAVE@`, `-wd waves`, no -tc, collector-only email). Progress
lines go to `analysis/methods_C/PROGRESS.md`. Generated by
campaign/make_batches.py — regenerate rather than hand-edit.
"""


def _write_methods_readme(wave_dir, wave_name, what):
    with open(os.path.join(wave_dir, "README.md"), "w") as f:
        f.write(METHODS_README.replace("@WAVE@", wave_name).replace("@WHAT@", what))


def _wave_keys(wave_dir, tiers):
    with open(os.path.join(wave_dir, "design_matrix.csv"), newline="") as f:
        return [tuple(float(row[f"{t}_omega"]) for t in tiers) for row in csv.DictReader(f)]


def _overlaps(keys, waves_root, waves, tiers):
    out = []
    for w in waves:
        other = _wave_keys(os.path.join(waves_root, w), tiers)
        for i, k in enumerate(keys, start=1):
            for j, o in enumerate(other, start=1):
                if k == o:
                    out.append({"index": i, "wave": w, "wave_index": j})
    return out


def build_methods_start(k, waves_root=WAVES_ROOT, source_root=WAVES_ROOT):
    """S_k (k = 2, 3): ONE 32-point scrambled-Sobol block from engine
    SOBOL_SEED + (k - 1), same snap / dedupe / redraw as stage2_C_n0
    (build_stage2_n0 with size 32). Overlaps with S1 and the random pool are
    ALLOWED and listed in the manifest. REFUSES an existing wave dir."""
    assert k in (2, 3), k
    name = methods_start_name(k)
    wave_dir = os.path.join(waves_root, name)
    if os.path.exists(wave_dir):
        raise RuntimeError(f"REFUSED: {wave_dir} already exists")
    tiers, _ = stage2_tiers()
    build_stage2_n0("C", waves_root=waves_root, size=METHODS_START_SIZE,
                    seed=SOBOL_SEED + (k - 1), wave_name=name,
                    manifest_extra={"methods_start": k, "prompt": "35"})
    keys = _wave_keys(wave_dir, tiers)
    ov = _overlaps(keys, source_root, METHODS_S1_WAVES + ["random_C"], tiers)
    man_path = os.path.join(wave_dir, "manifest.json")
    man = json.load(open(man_path))
    man["methods_overlaps"] = ov  # allowed; listed (prompt 35 §3.3)
    with open(man_path, "w") as f:
        json.dump(man, f, indent=2)
        f.write("\n")
    _write_methods_readme(wave_dir, name,
                          f"Start set S{k}: 32 scrambled-Sobol lattice points, engine seed "
                          f"{SOBOL_SEED + k - 1}, skip 0 (n_drawn_total in the manifest). "
                          f"{len(ov)} overlap(s) with S1 / random_C (allowed, listed).")
    return wave_dir


def _sobol_continuation(seed, start_skip, size, seen, tiers):
    """build_stage2_n0b's mechanics: global draws start_skip + 1 ..., snap,
    dedupe against `seen` (mutated) and this block, block redraws."""
    lo, hi = float(STAGE2_LATTICE[0]), float(STAGE2_LATTICE[-1])
    kept, snap_log = [], []
    n_drawn_total = start_skip
    while len(kept) < size:
        block = size if n_drawn_total == start_skip else size - len(kept)
        points = dt.generate_sobol(block, seed, skip=n_drawn_total, d=len(tiers))
        n_drawn_total += block
        for offset, unit in enumerate(points):
            pre = lo + unit * (hi - lo)
            post = _snap_to_lattice(pre)
            key = tuple(float(w) for w in post)
            entry = {"draw": n_drawn_total - block + offset + 1,
                     "pre_snap": [float(w) for w in pre],
                     "post_snap": [float(w) for w in post], "kept_index": None}
            if key not in seen and len(kept) < size:
                seen.add(key)
                kept.append(post)
                entry["kept_index"] = len(kept)
            snap_log.append(entry)
    return kept, snap_log, n_drawn_total


def build_methods_sobol(j, waves_root=WAVES_ROOT, source_root=WAVES_ROOT):
    """Q_j: 16 continuation points of start set S_j's engine. Q1 continues S1
    (seed SOBOL_SEED, skip = the n0b manifest's n_drawn_total), deduped against
    S1's 32; Q2 / Q3 continue S2 / S3 (skip = their manifest n_drawn_total),
    deduped against their own 32. REFUSES an existing wave dir."""
    assert j in (1, 2, 3), j
    name = methods_sobol_name(j)
    wave_dir = os.path.join(waves_root, name)
    if os.path.exists(wave_dir):
        raise RuntimeError(f"REFUSED: {wave_dir} already exists")
    tiers, provisional = stage2_tiers()
    if j == 1:
        src = METHODS_S1_WAVES
        sob = json.load(open(os.path.join(source_root, "stage2_C_n0b", "manifest.json")))["sobol"]
    else:
        src = [methods_start_name(j)]
        sob = json.load(open(os.path.join(source_root, src[0], "manifest.json")))["sobol"]
    seed = SOBOL_SEED + (j - 1)
    assert sob["seed"] == seed, (sob["seed"], seed)
    seen = set()
    for w in src:
        seen |= set(_wave_keys(os.path.join(source_root, w), tiers))
    assert len(seen) == 32, f"start set S{j} has {len(seen)} distinct rows, expected 32"
    start_skip = int(sob["n_drawn_total"])
    kept, snap_log, n_drawn_total = _sobol_continuation(seed, start_skip, METHODS_SOBOL_SIZE, seen, tiers)
    rows = [dt.make_row(tiers, dict(zip(tiers, om)), index=i, num_days=FULL_YEAR,
                        provisional=provisional, rho_h2=RHO_SCENARIOS["C"])
            for i, om in enumerate(kept, start=1)]
    dt.write_wave(dt.rows_to_matrix(rows, tiers), wave_dir, tiers,
                  sobol={"seed": seed, "skip": start_skip, "n": METHODS_SOBOL_SIZE,
                         "n_drawn_total": n_drawn_total, "continues_waves": src,
                         "lattice": [float(w) for w in STAGE2_LATTICE],
                         "scipy_version": scipy.__version__},
                  manifest_extra={"methods_sobol": j, "prompt": "35"})
    with open(os.path.join(wave_dir, "snap_map.json"), "w") as f:
        json.dump({"tier_order": list(tiers), "draws": snap_log}, f, indent=2)
        f.write("\n")
    _write_methods_readme(wave_dir, name,
                          f"Sobol continuation Q{j}: 16 points continuing S{j}'s engine "
                          f"(seed {seed}) from global draw {start_skip + 1}, deduped against "
                          f"S{j}'s 32 ({', '.join(src)}). Descriptive arm (n = 48 vs the "
                          "same start set's q-ParEGO arm and the pool percentile).")
    return wave_dir


def build_methods_round(wave_name, designs, manifest_extra=None, waves_root=WAVES_ROOT):
    """build_bo_round generalized by name (prompt 35): one acquisition round of
    8 lattice designs for a methods arm. REFUSES an existing wave dir (the
    double-spend guard at the wave level). No submit script: submit_ready.sh
    submits it with the generic templates."""
    wave_dir = os.path.join(waves_root, wave_name)
    if os.path.exists(wave_dir):
        raise RuntimeError(f"REFUSED: {wave_dir} already exists — a methods round is never regenerated")
    designs = np.asarray(designs, dtype=float)
    assert designs.shape == (BO_SIZE, 6), designs.shape
    lat = np.round(np.asarray(STAGE2_LATTICE, float), 10)
    assert all(np.isclose(lat, w, atol=1e-12).any() for row in designs for w in row), "off-lattice design"
    assert len({tuple(r) for r in designs.round(10).tolist()}) == BO_SIZE, "duplicate designs in batch"
    tiers, provisional = stage2_tiers()
    sorted_tiers = sorted(tiers)
    rows = [dt.make_row(tiers, {t: float(w) for t, w in zip(sorted_tiers, row)}, index=i,
                        num_days=FULL_YEAR, provisional=provisional, rho_h2=RHO_SCENARIOS["C"])
            for i, row in enumerate(designs, start=1)]
    extra = {"lattice": [float(w) for w in STAGE2_LATTICE], "prompt": "35"}
    extra.update(manifest_extra or {})
    dt.write_wave(dt.rows_to_matrix(rows, tiers), wave_dir, tiers, sobol=None, manifest_extra=extra)
    _write_methods_readme(wave_dir, wave_name,
                          f"Acquisition round: {json.dumps({k: extra[k] for k in ('methods_arm', 'methods_round', 'acq', 'acq_seed') if k in extra})}.")
    return wave_dir


# Generic templates (written to analysis/methods_C/ by write_methods_templates).
# ARRAY: BO_ARRAY_TEMPLATE made generic — the wave comes from `-v WAVE=` and
# `-wd waves`; it reads the design at task START (hold mode: the held
# acquisition wrote it into this same clone) and fails loudly if absent.
METHODS_ARRAY = """#!/bin/bash
#$ -q long
#$ -r n

# Generic methods_C array task (prompt 35). Submitted ONLY by
# analysis/methods_C/submit_ready.sh:
#   qsub -wd <campaign>/waves -v WAVE=<wave> -t 1-<N> -r n -N <wave>_array methods_array.sh
# NO email flags (one email per task otherwise), no -tc.
# Generated by campaign/make_batches.py — regenerate rather than hand-edit.

set -euo pipefail
: "${WAVE:?WAVE env var required (qsub -v WAVE=<wave>)}"

GUROBI_MODULE="gurobi"
WAVES_DIR="$PWD"
WAVE_DIR="$WAVES_DIR/$WAVE"
TRIAL_DIR="$(cd "$WAVES_DIR/../.." && pwd)"

if [[ ! -f "$WAVE_DIR/design_matrix.csv" ]]; then
    echo "FATAL: $WAVE_DIR/design_matrix.csv is absent at task start — the held" >&2
    echo "acquisition did not write this round (WEDGED/FAILED/DONE?). Not running." >&2
    exit 1
fi
mkdir -p "$WAVE_DIR/runs"

# Env lines are IDENTICAL to random_C / bo_C / stage2 array scripts (the frozen
# Stage-2 stack): NO PYTHONNOUSERSITE here — PCM0826 resolves networkx (egret
# tx_calc) from ~/.local. Launch 1 (10-12) set it and every task died at import.
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate PCM0826
module load "$GUROBI_MODULE"

eval "$(python "$TRIAL_DIR/campaign/get_row.py" "$SGE_TASK_ID" "$WAVE_DIR/design_matrix.csv")"

python "$TRIAL_DIR/multi_pem/multi_PEM_PCM.py" \\
    --index "$INDEX" \\
    --num_days "$NUM_DAYS" \\
    --start_date "$START_DATE" \\
    --output_directory "$WAVE_DIR/runs/run" \\
    --retrofit_gen_dict "$(cat "$WAVE_DIR/retrofit_gen_dict_${INDEX}.json")"
"""

# COLLECTOR: _render_random_collector's features (integrity gate, FAILED
# marker, stale-FAILED cleanup, summarize, N-row finite-M check, 5-retry push,
# -r n, PYTHONNOUSERSITE) made generic, plus an flock around every git step
# (acquisition jobs and collectors share ONE CRC clone).
METHODS_COLLECTOR = r"""#!/bin/bash
#$ -q long
#$ -r n

# Generic methods_C collector (prompt 35). Submitted ONLY by submit_ready.sh:
#   qsub -wd <campaign>/waves -v WAVE=<wave> -hold_jid <array> -r n \
#        -N collect_<wave> -M ylu28@nd.edu -m ea methods_collect.sh
# Generated by campaign/make_batches.py — regenerate rather than hand-edit.

set -euo pipefail
: "${WAVE:?WAVE env var required (qsub -v WAVE=<wave>)}"

WAVES_DIR="$PWD"
WAVE_DIR="$WAVES_DIR/$WAVE"
CAMPAIGN_DIR="$(cd "$WAVES_DIR/.." && pwd)"
TRIAL_DIR="$(cd "$CAMPAIGN_DIR/.." && pwd)"
REPO_DIR="$(cd "$TRIAL_DIR/.." && pwd)"

source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate PCM0826
export PYTHONNOUSERSITE=1  # ~/.local shadowing hazard (house-proven)

BOT=(-c user.name="methods-bot" -c user.email="methods-bot@noreply.github.com")
exec 9>"$REPO_DIR/.git/methods_C.flock"

push_with_retries() {
    local attempt
    for attempt in 1 2 3 4 5; do
        if git -C "$REPO_DIR" push origin d6; then
            return 0
        fi
        echo "push rejected (attempt $attempt/5) — rebase and retry"
        sleep $((30 + RANDOM % 60))
        git -C "$REPO_DIR" pull --rebase --autostash origin d6
    done
    if git -C "$REPO_DIR" push origin d6; then
        return 0
    fi
    echo "PUSH FAILED after 5 retries — stopping with status visible:"
    git -C "$REPO_DIR" status
    git -C "$REPO_DIR" log --oneline -3
    exit 1
}

fail_marker() {  # $1 = title line, rest = body lines
    local marker="$WAVE_DIR/FAILED_${WAVE}.md"
    mkdir -p "$WAVE_DIR"
    { echo "# FAILED — $1"; echo; shift; printf '%s\n' "$@";
      echo; echo "Generated $(date -u +%FT%TZ) by methods_collect.sh (WAVE=$WAVE)."; } > "$marker"
    flock 9
    git -C "$REPO_DIR" add -- "$marker"
    git -C "$REPO_DIR" "${BOT[@]}" commit -m "methods-bot: FAILED marker ($WAVE)"
    push_with_retries
    flock -u 9
}

# --- 0. the wave must exist (hold mode: written by the held acquisition) ----
if [[ ! -f "$WAVE_DIR/design_matrix.csv" ]]; then
    fail_marker "$WAVE has no design_matrix.csv at collection" \
        "The acquisition that should have written this round did not (WEDGED/FAILED/DONE?)."
    exit 1
fi

# --- 1. integrity gate: sentinel count vs the design matrix itself ----------
read -r N missing < <(python - "$WAVE_DIR" <<'EOF'
import sys, csv, os
wdir = sys.argv[1]
with open(os.path.join(wdir, "design_matrix.csv"), newline="") as f:
    idx = [int(row["index"]) for row in csv.DictReader(f)]
missing = [i for i in idx
           if not os.path.isfile(os.path.join(
               wdir, "runs", f"run_index_{i}", "overall_simulation_output.csv"))]
print(len(idx), ",".join(str(i) for i in missing) or "-")
EOF
)
if [[ "$missing" != "-" ]]; then
    fail_marker "$WAVE incomplete at collection" \
        "Missing run indices (no overall_simulation_output.csv): $missing" \
        "Recovery (prompt 35 §5): resubmit ONCE via resubmit_missing.py / qsub -t, then re-run this collector."
    echo "GATE FAIL: missing indices: $missing"
    exit 1
fi
echo "GATE PASS: $WAVE complete ($N rows)"

# --- 2. summarize this wave only, then the N-row finite-M check -------------
python "$CAMPAIGN_DIR/summarize_wave.py" "$WAVE_DIR"
if ! python - "$WAVE_DIR/objectives.csv" "$N" <<'EOF'
import sys
import numpy as np, pandas as pd
ob = pd.read_csv(sys.argv[1]); n = int(sys.argv[2])
M = ["load_shed_mwh", "true_curtailment_mwh", "total_cost_less_synthetic_usd"]
ok = (len(ob) == n and sorted(ob["index"]) == list(range(1, n + 1))
      and np.isfinite(ob[M].to_numpy(float)).all())
print(f"objectives check: rows={len(ob)} expected={n} ok={ok}")
sys.exit(0 if ok else 1)
EOF
then
    fail_marker "$WAVE objectives.csv failed the $N-row / finite-M check" \
        "All sentinels were present but the summary is not usable."
    exit 1
fi

# --- 3. bot commit (explicit paths only) under the clone lock, push ----------
flock 9
# a stale FAILED marker from an earlier attempt is removed in the results commit
[[ -f "$WAVE_DIR/FAILED_${WAVE}.md" ]] && git -C "$REPO_DIR" rm -q -- "$WAVE_DIR/FAILED_${WAVE}.md"
git -C "$REPO_DIR" add -- "$WAVE_DIR/objectives.csv" "$WAVE_DIR/site_detail.csv"
git -C "$REPO_DIR" "${BOT[@]}" commit -m "methods-bot: $WAVE results"
push_with_retries
flock -u 9
echo "methods_collect $WAVE done: objectives pushed"
"""


def write_methods_templates(out_dir):
    for fname, text in (("methods_array.sh", METHODS_ARRAY), ("methods_collect.sh", METHODS_COLLECTOR)):
        path = os.path.join(out_dir, fname)
        with open(path, "w") as f:
            f.write(text)
        os.chmod(path, 0o755)


for _k in (2, 3):
    BUILDERS[methods_start_name(_k)] = functools.partial(build_methods_start, _k)
    WAVE_MAX_CONCURRENT[methods_start_name(_k)] = None  # no -tc (red line)
for _j in (1, 2, 3):
    BUILDERS[methods_sobol_name(_j)] = functools.partial(build_methods_sobol, _j)
    WAVE_MAX_CONCURRENT[methods_sobol_name(_j)] = None


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if not argv or argv[0] == "all":
        raise SystemExit(
            "REFUSED: build waves one at a time by name — rerunning a legacy "
            "builder overwrites a frozen (possibly in-flight) wave dir. "
            f"Choose from {list(BUILDERS)}"
        )
    names = [argv[0]]
    for name in names:
        if name not in BUILDERS:
            raise SystemExit(f"unknown wave {name!r}; choose from {list(BUILDERS)}")
        wave_dir = BUILDERS[name]()
        script = submit_array.generate_script(
            wave_dir, max_concurrent=WAVE_MAX_CONCURRENT.get(name, 20))
        print(f"built wave {name}: {wave_dir} (SGE script: {os.path.basename(script)})")


if __name__ == "__main__":
    main()
