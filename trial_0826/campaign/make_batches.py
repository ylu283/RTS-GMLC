"""Build the three campaign wave definitions (doc 14 §6): pilot, screening, n0.

Usage:  python make_batches.py [pilot|screening|n0|all]

Each wave is a self-contained directory under campaign/waves/ with
design_matrix.csv, per-row retrofit JSONs, manifest.json, and the generated
SGE array script. Commit the campaign code BEFORE generating waves so the
manifest git SHA describes the generator. No job is ever submitted here.
"""

import os
import sys

import design_tools as dt
import submit_array
from tiers import SOBOL_SEED, build_tiers, load_gen_pmax, load_tm1_stats

WAVES_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "waves")

FULL_YEAR = 366  # 2020 is a leap year — 366, not 365
N0_SIZE = 128    # doc 14 §2.2: 2^7, Sobol balance, ~9d at d=14

OAT_BID = 40.0            # top of bid range for every screening site (doc 14 §6 item 2)
NUCLEAR_SITE = "121_NUCLEAR_1"
NUCLEAR_OAT_OMEGA = 0.5   # parent-paper optimum; nuclear is never in 15a's CSV
BASE_CASE_SOURCE_DIR = "trial_0826/base_case_pcm_test"

HOLD_MD = """# HOLD — do not submit this wave

1. **This wave is a DRAFT generated from provisional tiers/bounds — submit
   nothing.** Pending decisions: O-M2 bid handling and the final tier
   assignment from the screening batch's noise criterion.

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


BUILDERS = {"pilot": build_pilot, "screening": build_screening, "n0": build_n0}


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    which = argv[0] if argv else "all"
    names = list(BUILDERS) if which == "all" else [which]
    for name in names:
        if name not in BUILDERS:
            raise SystemExit(f"unknown wave {name!r}; choose from {list(BUILDERS)} or 'all'")
        wave_dir = BUILDERS[name]()
        script = submit_array.generate_script(wave_dir)
        print(f"built wave {name}: {wave_dir} (SGE script: {os.path.basename(script)})")


if __name__ == "__main__":
    main()
