"""v3 derived-bid machinery (math-log §1-§4): scheme constants, ω-only rows,
omega_grid, contour/sweep batch builders, g4/g5 extraction, and the
pilot/screening backfill regression gate."""

import csv
import os

import numpy as np
import pandas as pd
import pytest

import design_tools as dt
import make_batches
import summarize_wave
from tiers import PSI_KG_PER_MWH, RHO_SCENARIOS, derived_bid

CAMPAIGN_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


# ---------------------------------------------------------------- Task 1

def test_derived_bid_values():
    assert derived_bid(1.0) == 20.0
    assert derived_bid(1.5) == 30.0
    assert derived_bid(2.0) == 40.0
    assert PSI_KG_PER_MWH == 20.0


def test_rho_scenarios_capped_at_pi_limit():
    assert RHO_SCENARIOS == {"A": 1.0, "B": 1.5, "C": 2.0}
    assert max(RHO_SCENARIOS.values()) <= 2.0  # PI cap (math-log §1.3)


# ---------------------------------------------------------------- Task 2

def test_v3_row_bids_all_derived(tiers):
    row = dt.make_row(tiers, {"wind_303": 0.4, "pv": 0.1}, index=1, rho_h2=1.5)
    assert row["wind_303_bid"] == 30.0
    assert row["pv_bid"] == 30.0
    assert row["wind_303_omega"] == 0.4
    assert row["rho_h2"] == 1.5
    # absent tiers stay NaN in both columns
    assert np.isnan(row["nuclear_omega"]) and np.isnan(row["nuclear_bid"])


def test_v3_row_rejects_explicit_bids(tiers):
    with pytest.raises(AssertionError):
        dt.make_row(tiers, {"wind_303": (0.4, 25.0)}, index=1, rho_h2=1.5)


def test_old_mode_rows_unchanged(tiers):
    row = dt.make_row(tiers, {"wind_303": (0.4, 25.0)}, index=1)
    assert row["wind_303_bid"] == 25.0
    assert np.isnan(row["rho_h2"])  # column present, NaN when no scenario


def test_rho_h2_column_in_matrix(tiers):
    df = dt.rows_to_matrix(
        [dt.make_row(tiers, {"wind_303": 0.4}, index=1, rho_h2=2.0)], tiers)
    assert "rho_h2" in df.columns
    assert df["rho_h2"].iloc[0] == 2.0


def test_to_design_matrix_v3_omega_only(tiers):
    pts = np.array([[0.0] * len(tiers), [1.0] * len(tiers), [0.5] * len(tiers)])
    df = dt.to_design_matrix(pts, tiers, rho_h2=1.0)
    for name, tier in tiers.items():
        lo, hi = tier["omega"]
        assert df[f"{name}_omega"].tolist() == pytest.approx([lo, hi, (lo + hi) / 2])
        assert (df[f"{name}_bid"] == 20.0).all()
    assert (df["rho_h2"] == 1.0).all()
    # v3 unit points are d = len(tiers), not 2*len(tiers)
    with pytest.raises(AssertionError):
        dt.to_design_matrix(np.zeros((2, 2 * len(tiers))), tiers, rho_h2=1.0)


def test_omega_grid():
    grid = dt.omega_grid(9, 0.05, 1.0)
    assert len(grid) == 9
    assert grid[0] == 0.05 and grid[-1] == 1.0  # endpoints exact
    assert (np.diff(grid) > 0).all()            # strictly increasing
    with pytest.raises(AssertionError):
        dt.omega_grid(1, 0.05, 1.0)
    with pytest.raises(AssertionError):
        dt.omega_grid(9, 0.0, 1.0)


# ---------------------------------------------------------------- Task 4

def active_omega_cols(df):
    return [c for c in df.columns if c.endswith("_omega")]


def test_contour_wave(contour_a_wave, tiers):
    df = pd.read_csv(os.path.join(contour_a_wave, "design_matrix.csv"))
    assert len(df) == 81
    assert list(df["index"]) == list(range(1, 82))
    assert (df["num_days"] == 366).all()
    assert (df["rho_h2"] == 1.0).all()
    # exactly two active tiers per row: 303 and 317
    act = df[active_omega_cols(df)].notna()
    assert (act.sum(axis=1) == 2).all()
    assert act["wind_303_omega"].all() and act["wind_317_omega"].all()
    # every bid == scenario A derived value
    for t in ("wind_303", "wind_317"):
        assert (df[f"{t}_bid"] == 20.0).all()
    # row-major ordering, omega_303 outer (README grid-ordering note)
    g303 = dt.omega_grid(9, *tiers["wind_303"]["omega"])
    g317 = dt.omega_grid(9, *tiers["wind_317"]["omega"])
    for idx, (i303, i317) in [(1, (0, 0)), (9, (0, 8)), (10, (1, 0)), (81, (8, 8))]:
        r = df[df["index"] == idx].iloc[0]
        assert r["wind_303_omega"] == pytest.approx(g303[i303])
        assert r["wind_317_omega"] == pytest.approx(g317[i317])


def test_contour_wave_scenario_b_bids(contour_b_wave):
    df = pd.read_csv(os.path.join(contour_b_wave, "design_matrix.csv"))
    assert (df["rho_h2"] == 1.5).all()
    assert (df["wind_303_bid"] == 30.0).all()
    assert (df["wind_317_bid"] == 30.0).all()


def test_sweep_wave(sweep_b_wave, tiers):
    df = pd.read_csv(os.path.join(sweep_b_wave, "design_matrix.csv"))
    assert len(df) == 54
    assert list(df["index"]) == list(range(1, 55))
    assert (df["rho_h2"] == 1.5).all()
    act = df[active_omega_cols(df)].notna()
    assert (act.sum(axis=1) == 1).all()  # exactly one active tier per row
    for name, tier in tiers.items():
        rows = df[df[f"{name}_omega"].notna()]
        assert len(rows) == 9
        # sweep levels == the tier's contour-grid axis (math-log §4.3: the
        # f(omega, 0) margins for the interaction index come free)
        assert rows[f"{name}_omega"].tolist() == pytest.approx(
            list(dt.omega_grid(9, *tier["omega"])))
        assert (rows[f"{name}_bid"] == 30.0).all()


def test_v3_wave_scripts(contour_a_wave, sweep_b_wave):
    for wave, n in ((contour_a_wave, 81), (sweep_b_wave, 54)):
        name = os.path.basename(wave)
        text = open(os.path.join(wave, f"{name}_array.sh")).read()
        assert f"#$ -t 1-{n}" in text
        assert "/Users/" not in text


# ---------------------------------------------------------------- Task 3

def write_thermal_detail(path, frames):
    """frames: list of (generator, [unit states in time order])."""
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Date", "Hour", "Minute", "Generator", "Dispatch",
                    "Dispatch DA", "Headroom", "Unit State", "Unit Cost",
                    "Unit Market Revenue", "Unit Uplift Payment"])
        for gen, states in frames:
            for t, u in enumerate(states):
                w.writerow([f"2020-01-{t // 24 + 1:02d}", t % 24, 0, gen,
                            0.0, 0.0, 0.0, bool(u), 0.0, 0.0, 0.0])


def test_g5_fleet_starts_synthetic(tmp_path):
    # gen A: starts at t=2 and t=5 (2 starts; first hour ON is NOT a start).
    # gen B: ON at t=0 (no start), off, one restart at t=4 -> 1 start.
    write_thermal_detail(tmp_path / "thermal_detail.csv", [
        ("A", [0, 0, 1, 1, 0, 1, 1, 1]),
        ("B", [1, 1, 0, 0, 1, 1, 0, 0]),
    ])
    assert summarize_wave.fleet_thermal_starts(tmp_path) == 3


def test_g5_unit_state_string_dtype_rejected_or_mapped(tmp_path):
    # pandas parses True/False to bool; the guard must map explicit strings
    s = pd.Series(["True", "False", "True"], dtype=object)
    assert summarize_wave._unit_state_bool(s).tolist() == [True, False, True]
    assert summarize_wave._unit_state_bool(
        pd.Series([0, 1, 1])).tolist() == [False, True, True]
    with pytest.raises(AssertionError):
        summarize_wave._unit_state_bool(pd.Series(["on", "off"], dtype=object))


def test_g4_missing_column_is_nan_not_zero(capsys):
    ov = pd.DataFrame({"Total costs": [1.0]})
    assert np.isnan(summarize_wave.reserve_shortfall_mwh(ov, "unit-test"))
    assert "WARNING" in capsys.readouterr().out
    ov = pd.DataFrame({"Total reserve shortfall": [3.0]})
    assert summarize_wave.reserve_shortfall_mwh(ov, "unit-test") == 3.0


# ------------------------------------------------- backfill regression gate

@pytest.mark.parametrize("wave", ["pilot", "screening"])
def test_backfill_old_columns_byte_identical(wave):
    """summarize_wave.py re-runs on pilot/screening must not change any
    pre-v3 column value (golden copies snapshotted before the v3 change)."""
    golden_path = os.path.join(DATA_DIR, f"pre_v3_objectives_{wave}.csv")
    current_path = os.path.join(CAMPAIGN_DIR, "waves", wave, "objectives.csv")
    if not os.path.isfile(current_path):
        pytest.skip(f"waves/{wave}/objectives.csv absent")
    with open(golden_path, newline="") as f:
        golden = list(csv.DictReader(f))
    with open(current_path, newline="") as f:
        current = list(csv.DictReader(f))
    assert len(golden) == len(current)
    old_cols = golden[0].keys()
    assert set(old_cols) <= set(current[0].keys()), "old column dropped"
    for g, c in zip(golden, current):
        for col in old_cols:
            assert c[col] == g[col], f"{wave} row {g['index']} col {col}: " \
                                     f"{c[col]!r} != golden {g[col]!r}"


@pytest.mark.parametrize("wave", ["pilot", "screening"])
def test_backfill_new_columns_present(wave):
    current_path = os.path.join(CAMPAIGN_DIR, "waves", wave, "objectives.csv")
    if not os.path.isfile(current_path):
        pytest.skip(f"waves/{wave}/objectives.csv absent")
    if not os.path.isdir(os.path.join(CAMPAIGN_DIR, "waves", wave, "runs")):
        # raw run outputs live on CRC only (untracked, .gitignore'd): the
        # g4/g5 backfill for this wave runs there — see README
        pytest.skip(f"waves/{wave}/runs absent locally; backfill happens on CRC")
    df = pd.read_csv(current_path)
    for col in ("reserve_shortfall_mwh", "thermal_starts", "rho_h2",
                "delta_reserve_shortfall_mwh", "delta_thermal_starts"):
        assert col in df.columns
    assert df["rho_h2"].isna().all()  # pre-v3 waves carry no scenario
