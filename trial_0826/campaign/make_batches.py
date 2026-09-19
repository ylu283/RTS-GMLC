"""Build the three campaign wave definitions (doc 14 §6): pilot, screening, n0.

Usage:  python make_batches.py [pilot|screening|n0|all]

Each wave is a self-contained directory under campaign/waves/ with
design_matrix.csv, per-row retrofit JSONs, manifest.json, and the generated
SGE array script. Commit the campaign code BEFORE generating waves so the
manifest git SHA describes the generator. No job is ever submitted here.
"""

import functools
import json
import os
import sys

import numpy as np
import scipy

import design_tools as dt
import submit_array
from tiers import (RHO_SCENARIOS, SOBOL_SEED, STAGE2_LATTICE, build_tiers,
                   load_gen_pmax, load_tm1_stats, stage2_tiers)

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


def build_stage2_n0(scenario, waves_root=WAVES_ROOT):
    """Stage-2 batch 0 (prompt 27, PI directive 2026-09): 16 scrambled Sobol
    points on the d = 6 discrete lattice. A NEW d = 6 engine (seed
    SOBOL_SEED, skip = 0) — the never-re-seed rule applies to later Stage-2
    rows, which continue THIS sequence with skip = n_drawn_total (recorded in
    the manifest). Each point is affine-mapped into the stage-2 box and each
    coordinate snapped to the nearest lattice level; duplicate post-snap rows
    are dropped keeping the first occurrence and replaced by continuing the
    sequence in blocks (with this seed snapping produces zero collisions —
    the redraw path is correctly-specified dead code; scipy's
    non-power-of-2 UserWarning on a redraw is expected, not an error)."""
    tiers, provisional = stage2_tiers()
    rho = RHO_SCENARIOS[scenario]
    lo, hi = float(STAGE2_LATTICE[0]), float(STAGE2_LATTICE[-1])

    kept, seen, snap_log = [], set(), []
    n_drawn_total = 0
    while len(kept) < STAGE2_N0_SIZE:
        block = STAGE2_N0_SIZE if n_drawn_total == 0 else STAGE2_N0_SIZE - len(kept)
        points = dt.generate_sobol(block, SOBOL_SEED, skip=n_drawn_total,
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
            if key not in seen and len(kept) < STAGE2_N0_SIZE:
                seen.add(key)
                kept.append(post)
                entry["kept_index"] = len(kept)
            snap_log.append(entry)

    rows = [dt.make_row(tiers, dict(zip(tiers, omegas)), index=i,
                        num_days=FULL_YEAR, provisional=provisional, rho_h2=rho)
            for i, omegas in enumerate(kept, start=1)]
    wave_dir = os.path.join(waves_root, f"stage2_{scenario}_n0")
    dt.write_wave(dt.rows_to_matrix(rows, tiers), wave_dir, tiers,
                  sobol={"seed": SOBOL_SEED, "skip": 0, "n": STAGE2_N0_SIZE,
                         "n_drawn_total": n_drawn_total,
                         "lattice": [float(w) for w in STAGE2_LATTICE],
                         "scipy_version": scipy.__version__})
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


# License budget (prompt 27 T3): total concurrent Stage-2 tasks <= 12
# (prompt 26's ERCOT job shares the Gurobi pool).
WAVE_MAX_CONCURRENT = {"stage2_C_n0": 12, "stage2_backfill_C": 12}

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
            "stage2_backfill_C": functools.partial(build_stage2_backfill, "C")}


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    which = argv[0] if argv else "all"
    names = list(BUILDERS) if which == "all" else [which]
    for name in names:
        if name not in BUILDERS:
            raise SystemExit(f"unknown wave {name!r}; choose from {list(BUILDERS)} or 'all'")
        wave_dir = BUILDERS[name]()
        script = submit_array.generate_script(
            wave_dir, max_concurrent=WAVE_MAX_CONCURRENT.get(name, 20))
        print(f"built wave {name}: {wave_dir} (SGE script: {os.path.basename(script)})")


if __name__ == "__main__":
    main()
