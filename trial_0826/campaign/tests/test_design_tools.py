import json
import os

import numpy as np
import pandas as pd
import pytest

import design_tools as dt
from tiers import SOBOL_SEED, TIERS

CAMPAIGN_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_sobol_continuation():
    # seed s, draw 8 then 8 more with skip=8 == draw 16 in one call
    first = dt.generate_sobol(8, SOBOL_SEED)
    second = dt.generate_sobol(8, SOBOL_SEED, skip=8)
    together = dt.generate_sobol(16, SOBOL_SEED)
    assert np.array_equal(np.vstack([first, second]), together)


def test_sobol_power_of_two_warning():
    with pytest.warns(UserWarning):
        dt.generate_sobol(3, SOBOL_SEED)


def test_sobol_uses_seed_kwarg_not_rng():
    src = open(os.path.join(CAMPAIGN_DIR, "design_tools.py")).read()
    assert "seed=seed" in src
    assert "rng=" not in src


def test_no_literal_seeds_at_call_sites():
    for module in ("design_tools.py", "make_batches.py", "submit_array.py"):
        src = open(os.path.join(CAMPAIGN_DIR, module)).read()
        assert "20260821" not in src, f"literal seed in {module}; import SOBOL_SEED from tiers"
    assert "SOBOL_SEED" in open(os.path.join(CAMPAIGN_DIR, "make_batches.py")).read()


def test_to_design_matrix_physical_bounds(tiers):
    points = dt.generate_sobol(16, SOBOL_SEED)
    df = dt.to_design_matrix(points, tiers)
    assert list(df["index"]) == list(range(1, 17))
    for name, tier in tiers.items():
        omega_lo, omega_hi = tier["omega"]
        bid_lo, bid_hi = tier["bid"]
        assert df[f"{name}_omega"].between(omega_lo, omega_hi).all()
        assert df[f"{name}_bid"].between(bid_lo, bid_hi).all()
    # d columns complete
    assert len(dt.tier_columns(tiers)) == 2 * len(TIERS) == 14
    assert all(col in df.columns for col in dt.matrix_columns(tiers))


def test_omega_zero_forbidden(tiers):
    with pytest.raises(AssertionError):
        dt.make_row(tiers, {"nuclear": (0.0, 20.0)}, index=1)
    row = dt.make_row(tiers, {"nuclear": (0.1, 20.0)}, index=1)
    row["nuclear_omega"] = 0.0
    with pytest.raises(AssertionError):
        dt.expand_to_retrofit_dict(row, tiers)
    with pytest.raises(AssertionError):
        dt.single_site_entry("121_NUCLEAR_1", 0.0, 20.0)


def test_index_is_one_based(tiers):
    with pytest.raises(AssertionError):
        dt.make_row(tiers, {"nuclear": (0.1, 20.0)}, index=0)


def test_cluster_expansion(tiers):
    row = dt.make_row(tiers, {"pv_324": (0.1234567, 20.123456)}, index=1)
    out = dt.expand_to_retrofit_dict(row, tiers)
    assert set(out) == {"324_PV_1", "324_PV_2", "324_PV_3"}
    for member, entry in out.items():
        assert entry["PEM_fraction"] == 0.1235  # rounded to 4 decimals
        assert entry["PEM_bid"] == 20.12        # rounded to 2 decimals
        assert entry["gen_pmax"] == tiers["pv_324"]["gen_pmax"][member]
        assert set(entry) == {"PEM_fraction", "PEM_bid", "gen_pmax"}
    # NaN tiers skipped; only PEM_bid key; JSON round-trips
    text = json.dumps(out)
    assert "PEM_indifference_point" not in text
    assert json.loads(text) == out


def test_thermal_expansion_has_no_gen_pmax(tiers):
    row = dt.make_row(tiers, {"nuclear": (0.5, 40.0)}, index=1)
    out = dt.expand_to_retrofit_dict(row, tiers)
    assert set(out) == {"121_NUCLEAR_1"}
    assert set(out["121_NUCLEAR_1"]) == {"PEM_fraction", "PEM_bid"}


def test_expand_refuses_oat_rows(tiers):
    row = dt.make_row(tiers, {}, index=1, oat_site="303_WIND_1")
    with pytest.raises(AssertionError):
        dt.expand_to_retrofit_dict(row, tiers)
