import json
import os

import pandas as pd
import pytest

import design_tools as dt
import make_batches
from tiers import TIERS


def load_wave(wave_dir):
    df = pd.read_csv(os.path.join(wave_dir, "design_matrix.csv"))
    manifest = json.load(open(os.path.join(wave_dir, "manifest.json")))
    return df, manifest


def load_json(wave_dir, index):
    return json.load(open(os.path.join(wave_dir, f"retrofit_gen_dict_{index}.json")))


def omega_cols(df):
    return [c for c in df.columns if c.endswith("_omega")]


def test_pilot_batch(pilot_wave, tiers):
    df, manifest = load_wave(pilot_wave)
    assert list(df["index"]) == list(range(1, 13))
    full_year = df[df["num_days"] == 366]
    seven_day = df[df["num_days"] == 7]
    assert list(full_year["index"]) == [1, 2, 3]
    assert list(seven_day["index"]) == list(range(4, 13))
    # all 12 rows carry the SAME mid-box reference design
    tier_vals = df[dt.tier_columns(tiers)]
    assert (tier_vals.nunique() == 1).all()
    for name, tier in tiers.items():
        lo, hi = tier["omega"]
        assert lo < df[f"{name}_omega"].iloc[0] < hi
        assert df[f"{name}_omega"].iloc[0] == pytest.approx((lo + hi) / 2.0)
    assert manifest["sobol"] is None
    # all 12 dicts identical, written per index
    dicts = [load_json(pilot_wave, i) for i in range(1, 13)]
    assert all(d == dicts[0] for d in dicts)


def test_pilot_values_in_bounds(pilot_wave, tiers):
    df, _ = load_wave(pilot_wave)
    for name, tier in tiers.items():
        assert df[f"{name}_omega"].between(*tier["omega"]).all()
        assert df[f"{name}_bid"].between(*tier["bid"]).all()


def test_screening_batch(screening_wave):
    df, manifest = load_wave(screening_wave)
    assert len(df) == 12
    assert list(df["index"]) == list(range(1, 13))
    assert (df["num_days"] == 366).all()
    assert manifest["sobol"] is None
    # all tier columns NaN on every row (everything is OAT-encoded)
    assert df[omega_cols(df)].isna().all().all()

    oat_rows = df[df["oat_site"] != "__ALL__"]
    assert len(oat_rows) == 11
    union = {}
    for _, row in oat_rows.iterrows():
        gen_dict = load_json(screening_wave, int(row["index"]))
        # each OAT JSON contains exactly its oat_site generator
        assert list(gen_dict) == [row["oat_site"]]
        assert gen_dict[row["oat_site"]]["PEM_bid"] == 40.0
        union.update(gen_dict)

    all_in_index = int(df[df["oat_site"] == "__ALL__"]["index"].iloc[0])
    assert load_json(screening_wave, all_in_index) == union


def test_screening_omega_references(screening_wave):
    df, _ = load_wave(screening_wave)
    nuclear_idx = int(df[df["oat_site"] == "121_NUCLEAR_1"]["index"].iloc[0])
    gen_dict = load_json(screening_wave, nuclear_idx)
    assert gen_dict["121_NUCLEAR_1"]["PEM_fraction"] == 0.5  # always, never from CSV
    assert "gen_pmax" not in gen_dict["121_NUCLEAR_1"]
    wind_idx = int(df[df["oat_site"] == "303_WIND_1"]["index"].iloc[0])
    wind = load_json(screening_wave, wind_idx)["303_WIND_1"]
    assert wind["gen_pmax"] == 847.0
    assert wind["PEM_fraction"] == 0.5  # omega_oat_reference from 15a's CSV


def test_n0_batch(n0_wave, tiers):
    df, manifest = load_wave(n0_wave)
    assert list(df["index"]) == list(range(1, 131))
    assert (df["num_days"] == 366).all()
    anchors = df[df["anchor"]]
    assert list(anchors["index"]) == [129, 130]
    assert len(df) - len(anchors) == 128

    assert manifest["sobol"]["n"] == 128
    assert manifest["sobol"]["skip"] == 0
    assert manifest["sobol"]["seed"] == make_batches.SOBOL_SEED

    # sobol rows: every tier present, physical values inside tier bounds
    sobol_rows = df[~df["anchor"]]
    for name, tier in tiers.items():
        assert sobol_rows[f"{name}_omega"].between(*tier["omega"]).all()
        assert sobol_rows[f"{name}_bid"].between(*tier["bid"]).all()
        assert sobol_rows[f"{name}_omega"].notna().all()

    # anchor 130 = parent-paper nuclear optimum: nuclear only, others NaN
    nuc = df[df["index"] == 130].iloc[0]
    assert nuc["nuclear_omega"] == 0.5 and nuc["nuclear_bid"] == 40.0
    other = [c for c in omega_cols(df) if c != "nuclear_omega"]
    assert nuc[other].isna().all()

    # no design-matrix row is the base case (every non-OAT row retrofits something)
    assert df[omega_cols(df)].notna().any(axis=1).all()


def test_n0_hold_md(n0_wave):
    hold = open(os.path.join(n0_wave, "HOLD.md")).read()
    assert "DRAFT" in hold and "submit" in hold.lower()          # (1) draft, submit nothing
    assert "make_batches.py n0" in hold and "SOBOL_SEED" in hold  # (2) regeneration recipe
    assert "continue-the-sequence" in hold                        # (3) rule for later waves


def test_n0_external_anchors(n0_wave):
    ext = pd.read_csv(os.path.join(n0_wave, "external_anchors.csv"))
    assert len(ext) == 1
    row = ext.iloc[0]
    assert row["source_dir"] == "trial_0826/base_case_pcm_test"
    assert int(row["index"]) == 0  # outside 1..N
    assert ext[omega_cols(ext)].isna().all().all()
    # never in the design matrix: no retrofit JSON exists for it
    assert not os.path.exists(os.path.join(n0_wave, "retrofit_gen_dict_0.json"))


def test_manifests_record_provenance(pilot_wave, screening_wave, n0_wave):
    for wave in (pilot_wave, screening_wave, n0_wave):
        manifest = json.load(open(os.path.join(wave, "manifest.json")))
        assert len(manifest["git_sha"]) == 40
        assert isinstance(manifest["dirty"], bool)
        assert manifest["scipy_version"]
        assert len(manifest["environment_yml_sha256"]) == 64
        assert set(manifest["tiers"]) == set(TIERS)


# ---- placebo wave (prompt 17 Task 4) ----

def test_placebo_builder_registered():
    assert "placebo" in make_batches.BUILDERS
    assert "control_b0" not in make_batches.BUILDERS


def test_placebo_wave(placebo_wave, screening_wave):
    df, manifest = load_wave(placebo_wave)
    assert len(df) == 1
    row = df.iloc[0]
    assert row["oat_site"] == "317_WIND_1"
    assert int(row["num_days"]) == 366
    d = load_json(placebo_wave, 1)
    assert set(d) == {"317_WIND_1"}
    assert d["317_WIND_1"]["PEM_bid"] == 0.01
    # A/B coupling: same omega as the screening 317 OAT — locate the screening
    # reference BY CONTENT, not index (content-lookup survives regeneration
    # reorder; index happens to be 3 today).
    ref = None
    for i in range(1, 13):
        try:
            cand = load_json(screening_wave, i)
        except FileNotFoundError:
            continue
        if set(cand) == {"317_WIND_1"}:
            ref = cand
            break
    assert ref is not None, "screening 317 OAT dict not found by content"
    assert d["317_WIND_1"]["PEM_fraction"] == ref["317_WIND_1"]["PEM_fraction"]


def test_analyze_placebo_verdict_bands():
    import analyze_placebo as ap
    assert ap.verdict_for(-500.0) == "SPLIT-NEUTRAL"
    assert ap.verdict_for(-5_000.0) == "INCONCLUSIVE"
    assert "permuted-dict repeat" in ap.VERDICTS["INCONCLUSIVE"]
    assert ap.verdict_for(-12_000.0) == "ARTIFACT CONFIRMED"


def test_analyze_placebo_integrity_gates():
    import analyze_placebo as ap
    ok = {"pem_withheld_mwh_total": 400_000.0, "delta_curtailment_mwh": -350_000.0}
    assert ap.integrity_violations(ok) == []
    bad_h2 = {"pem_withheld_mwh_total": 960_000.0, "delta_curtailment_mwh": -350_000.0}
    assert ap.integrity_violations(bad_h2)
    bad_curt = {"pem_withheld_mwh_total": 400_000.0, "delta_curtailment_mwh": +9_000.0}
    assert ap.integrity_violations(bad_curt)


def test_analyze_placebo_missing_objectives(tmp_path):
    import analyze_placebo as ap
    assert ap.main([str(tmp_path)]) == 0
