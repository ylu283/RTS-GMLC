"""Stage-2 discrete-lattice waves (prompt 27): lattice membership, row
distinctness, derived bids, back-fill structure, snap_map/manifest records."""

import json
import os

import numpy as np
import pandas as pd

import make_batches
from tiers import SOBOL_SEED, STAGE2_LATTICE, TIERS, build_tiers, stage2_tiers

LATTICE = [float(w) for w in STAGE2_LATTICE]


def load_wave(wave_dir):
    df = pd.read_csv(os.path.join(wave_dir, "design_matrix.csv"))
    manifest = json.load(open(os.path.join(wave_dir, "manifest.json")))
    return df, manifest


def omega_cols(df):
    return [c for c in df.columns if c.endswith("_omega")]


def bid_cols(df):
    return [c for c in df.columns if c.endswith("_bid")]


def test_lattice_definition():
    # 9 evenly spaced levels over [0.05, 1.0], endpoints included
    assert len(STAGE2_LATTICE) == 9
    assert STAGE2_LATTICE[0] == 0.05 and STAGE2_LATTICE[-1] == 1.0
    steps = np.diff(STAGE2_LATTICE)
    assert np.allclose(steps, steps[0])


def test_stage2_tiers_full_span_and_no_mutation():
    before = json.dumps(build_tiers()[0], sort_keys=True, default=str)
    tiers, provisional = stage2_tiers()
    assert provisional is False
    for tier in tiers.values():
        assert tier["omega"] == (0.05, 1.0)  # nuclear cap and pv/tail floors gone
    # neither TIERS nor build_tiers() output changed
    assert json.dumps(build_tiers()[0], sort_keys=True, default=str) == before
    assert TIERS["nuclear"]["omega"] == (0.05, 0.5)
    assert TIERS["pv"]["omega"] == (0.02, 0.3)


def test_snap_to_lattice_midpoint_first_index_wins():
    mid = (LATTICE[0] + LATTICE[1]) / 2.0
    snapped = make_batches._snap_to_lattice(np.array([mid]))
    assert snapped[0] == LATTICE[0]


def test_stage2_n0_lattice_membership_and_distinct(stage2_n0_wave):
    df, manifest = load_wave(stage2_n0_wave)
    assert list(df["index"]) == list(range(1, 17))
    assert (df["num_days"] == 366).all()
    om = df[omega_cols(df)]
    assert om.notna().all().all()  # every tier active on every row
    for col in om.columns:
        assert om[col].isin(LATTICE).all(), f"{col} has off-lattice values"
    # 16 distinct rows
    assert len(om.drop_duplicates()) == 16


def test_stage2_n0_bids_all_40(stage2_n0_wave):
    df, _ = load_wave(stage2_n0_wave)
    assert (df[bid_cols(df)] == 40.0).all().all()
    assert (df["rho_h2"] == 2.0).all()
    for i in range(1, 17):
        d = json.load(open(os.path.join(stage2_n0_wave, f"retrofit_gen_dict_{i}.json")))
        assert all(entry["PEM_bid"] == 40.0 for entry in d.values())


def test_stage2_n0_manifest_and_snap_map(stage2_n0_wave):
    df, manifest = load_wave(stage2_n0_wave)
    sobol = manifest["sobol"]
    assert sobol["seed"] == SOBOL_SEED and sobol["skip"] == 0 and sobol["n"] == 16
    assert sobol["lattice"] == LATTICE
    assert sobol["n_drawn_total"] >= 16
    assert sobol["scipy_version"]
    # manifest tiers carry the full-span box (rows with nuclear omega > 0.5 match)
    assert list(manifest["tiers"]["nuclear"]["omega"]) == [0.05, 1.0]

    snap = json.load(open(os.path.join(stage2_n0_wave, "snap_map.json")))
    assert snap["tier_order"] == list(TIERS)
    draws = snap["draws"]
    assert len(draws) == sobol["n_drawn_total"]
    kept = [d for d in draws if d["kept_index"] is not None]
    assert [d["kept_index"] for d in kept] == list(range(1, 17))
    # snap correctness: post is the nearest lattice level of pre
    for d in draws:
        for pre, post in zip(d["pre_snap"], d["post_snap"]):
            nearest = LATTICE[int(np.argmin([abs(pre - lv) for lv in LATTICE]))]
            assert post == nearest
    # design matrix rows == kept snapped points, in draw order
    om = df[omega_cols(df)].to_numpy()
    assert np.array_equal(om, np.array([d["post_snap"] for d in kept]))


def test_stage2_backfill_structure(stage2_backfill_wave):
    df, manifest = load_wave(stage2_backfill_wave)
    assert list(df["index"]) == list(range(1, 11))
    assert (df["num_days"] == 366).all()
    assert manifest["sobol"] is None
    assert (df[bid_cols(df)].fillna(40.0) == 40.0).all().all()

    # rows 1-8: nuclear OAT at the 8 levels the old [0.05, 0.5] sweep never ran
    nuc = df.iloc[:8]
    assert list(nuc["nuclear_omega"]) == LATTICE[1:]
    assert nuc[[c for c in omega_cols(df) if c != "nuclear_omega"]].isna().all().all()
    # rows 9-10: pv extrapolation above the old 0.8 box top
    pv = df.iloc[8:]
    assert list(pv["pv_omega"]) == LATTICE[7:]
    assert pv[[c for c in omega_cols(df) if c != "pv_omega"]].isna().all().all()

    readme = " ".join(open(os.path.join(stage2_backfill_wave, "README.md")).read().split())
    for phrase in ("wind lattice-matched", "tail interpolable",
                   "pv interpolable below 0.8", "nuclear measured on the full lattice",
                   "B-scenario back-fills deferred"):
        assert phrase in readme

    # nuclear rows above the old 0.5 cap really exist (the new-regime data)
    assert (nuc["nuclear_omega"] > 0.5).sum() == 5


def test_stage2_arrays_use_tc_12(stage2_n0_wave, stage2_backfill_wave):
    for wave in (stage2_n0_wave, stage2_backfill_wave):
        name = os.path.basename(os.path.normpath(wave))
        script = open(os.path.join(wave, f"{name}_array.sh")).read()
        assert "#$ -tc 12" in script


# --- n0b top-up: continuation of the n0 sequence (Kay GO 09-21) --------------

def test_stage2_n0b_continues_the_sequence(stage2_n0_wave, stage2_n0b_wave):
    import design_tools as dt
    from tiers import SOBOL_SEED
    _, n0_manifest = load_wave(stage2_n0_wave)
    df, manifest = load_wave(stage2_n0b_wave)
    sobol = manifest["sobol"]
    assert sobol["seed"] == SOBOL_SEED
    assert sobol["skip"] == n0_manifest["sobol"]["n_drawn_total"]
    assert sobol["n"] == 16
    assert sobol["n_drawn_total"] >= sobol["skip"] + 16
    assert sobol["continues_wave"] == "stage2_C_n0"
    assert sobol["lattice"] == LATTICE
    # the first redrawn block really is draws skip+1..skip+16 of the SAME
    # engine: pre_snap of the first 16 snap_map draws must match an
    # independent generate_sobol call with skip = n_drawn_total(n0)
    snap = json.load(open(os.path.join(stage2_n0b_wave, "snap_map.json")))
    pts = dt.generate_sobol(16, SOBOL_SEED, skip=sobol["skip"], d=len(TIERS))
    lo, hi = LATTICE[0], LATTICE[-1]
    expect = lo + pts * (hi - lo)
    got = np.array([d["pre_snap"] for d in snap["draws"][:16]])
    assert np.allclose(got, expect, rtol=0, atol=0)
    assert [d["draw"] for d in snap["draws"][:16]] == list(
        range(sobol["skip"] + 1, sobol["skip"] + 17))


def test_stage2_n0b_no_overlap_and_lattice(stage2_n0_wave, stage2_n0b_wave):
    df0, _ = load_wave(stage2_n0_wave)
    df, _ = load_wave(stage2_n0b_wave)
    assert list(df["index"]) == list(range(1, 17))
    assert (df["num_days"] == 366).all()
    om = df[omega_cols(df)]
    assert om.notna().all().all()
    for col in om.columns:
        assert om[col].isin(LATTICE).all(), f"{col} has off-lattice values"
    combined = pd.concat([df0[omega_cols(df0)], om])
    assert len(combined.drop_duplicates()) == 32  # 32 distinct across BOTH waves
    assert (df[bid_cols(df)] == 40.0).all().all()
    assert (df["rho_h2"] == 2.0).all()


def test_stage2_n0b_snap_map_matches_matrix(stage2_n0b_wave):
    df, manifest = load_wave(stage2_n0b_wave)
    snap = json.load(open(os.path.join(stage2_n0b_wave, "snap_map.json")))
    assert snap["tier_order"] == list(TIERS)
    draws = snap["draws"]
    assert len(draws) == manifest["sobol"]["n_drawn_total"] - manifest["sobol"]["skip"]
    kept = [d for d in draws if d["kept_index"] is not None]
    assert [d["kept_index"] for d in kept] == list(range(1, 17))
    for d in draws:
        for pre, post in zip(d["pre_snap"], d["post_snap"]):
            nearest = LATTICE[int(np.argmin([abs(pre - lv) for lv in LATTICE]))]
            assert post == nearest
    om = df[omega_cols(df)].to_numpy()
    assert np.array_equal(om, np.array([d["post_snap"] for d in kept]))


def test_stage2_n0b_support_scripts(stage2_n0b_wave):
    array = open(os.path.join(stage2_n0b_wave, "stage2_C_n0b_array.sh")).read()
    assert "#$ -tc" not in array  # no concurrency cap (Kay 09-19)
    submit = open(os.path.join(stage2_n0b_wave, "submit_this.sh")).read()
    assert "-t 1-16" in submit
    assert 'BRANCH" == "d6"' in submit.replace("$", "")
    collector = open(os.path.join(stage2_n0b_wave, "collect_stage2_C_n0b.sh")).read()
    assert 'user.name="stage2-bot"' in collector
    assert "push_with_retries" in collector
    # the collector never INVOKES resubmit_missing.py (Kay-run recovery only)
    for line in collector.splitlines():
        if "resubmit_missing.py" in line:
            assert line.lstrip().startswith(("#", "echo")), line
