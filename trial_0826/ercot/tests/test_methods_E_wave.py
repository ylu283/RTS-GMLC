"""Prompt 55 tests — wave writer + stub loader (analysis/methods_E/wave_writer_E.py, _stub_loader.py).

Run:  cd trial_0826/ercot && /opt/anaconda3/envs/bogp-botorch/bin/python -m pytest tests/test_methods_E_wave.py -q
"""
import json
import os
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ERCOT = Path(__file__).resolve().parents[1]
ME = ERCOT / "analysis" / "methods_E"
sys.path.insert(0, str(ME))
sys.path.insert(0, str(ERCOT))
import common_E  # noqa: E402
import wave_writer_E as ww  # noqa: E402
import _stub_loader as sl  # noqa: E402
import _scratch_E as sc  # noqa: E402

CONTRACT_COLS = ["index", "oat_site", "unit_type", "bus", "omega", "bid", "gen_pmax", "start_date", "num_days",
                 "replicate_of", "pem_mw", "level_id", "tier", "sobol_index",
                 "mw_110", "mw_140", "mw_146", "mw_163", "mw_270", "mw_274",
                 "u_110", "u_140", "u_146", "u_163", "u_270", "u_274"]


@pytest.fixture(scope="module")
def root(tmp_path_factory):
    return sc.build_scratch(str(tmp_path_factory.mktemp("scr")), with_git=False, qsub_shim=False)


@pytest.fixture(scope="module")
def ds(root):
    return common_E.DesignSpace(os.path.join(root, "waves", "design_space_E.json"))


def test_design_space_from_contract(ds):
    assert ds.sites == ["110", "140", "146", "163", "270", "274"] and ds.d == 6
    assert ds.x_columns == CONTRACT_COLS[14:20] and ds.u_columns == CONTRACT_COLS[20:]
    np.testing.assert_allclose(ds.u_to_mw(np.ones(6)), ds.gen_pmax)
    np.testing.assert_allclose(ds.mw_to_u(ds.u_to_mw(np.full(6, 0.3))), 0.3)


def test_round_wave_schema_dicts_and_precision(root, ds):
    U = np.array([[0.123456789012345, 0.0, 1.0, 0.5, 0.25, 0.75]] + [[0.1 * (i + 1)] * 6 for i in range(7)])
    wdir = ww.build_round_wave(root, ds, "methods_E_qnehvi_s9_r1", U, manifest_extra={"methods_arm": "qnehvi", "seed_id": 9,
                               "methods_round": 1, "acq": "qnehvi", "acq_seed": 1})
    dm = pd.read_csv(os.path.join(wdir, "design_matrix.csv"), dtype={"oat_site": str, "tier": str})
    assert list(dm.columns) == CONTRACT_COLS and len(dm) == 8
    assert (dm["oat_site"] == "__ALL__").all() and (dm["tier"] == "bo").all() and (dm["bid"] == 40.0).all()
    assert dm["unit_type"].isna().all() and dm["bus"].isna().all() and dm["omega"].isna().all() and dm["gen_pmax"].isna().all()
    assert dm["sobol_index"].isna().all() and (dm["num_days"] == 365).all() and (dm["start_date"] == "01-01-2019").all()
    assert dm.loc[0, "u_110"] == 0.123456789012345                       # full precision survives the CSV
    assert dm.loc[0, "mw_110"] == 0.123456789012345 * ds.gen_pmax[0]
    np.testing.assert_allclose(dm["pem_mw"], dm[ds.x_columns].sum(axis=1), rtol=0, atol=1e-9)
    d1 = json.load(open(os.path.join(wdir, "retrofit_gen_dict_1.json")))
    assert set(d1) == {"110", "146", "163", "270", "274"}                # mw_140 == 0 exactly -> OMITTED
    assert d1["146"] == {"PEM_bid": 40.0, "PEM_fraction": 1.0, "gen_pmax": ds.gen_pmax[2]}
    assert d1["110"]["PEM_fraction"] == 0.123456789012345
    # pool_objectives.pem_mw on the __ALL__ row agrees with the matrix pem_mw (reader needs no change)
    import pool_objectives as po
    drow = po.design_row("methods_E_qnehvi_s9_r1", 1, waves=os.path.join(root, "waves"))
    assert drow["site"] == "__ALL__"
    assert po.pem_mw("methods_E_qnehvi_s9_r1", 1, drow, waves=os.path.join(root, "waves")) == pytest.approx(dm.loc[0, "pem_mw"], rel=1e-12)
    man = json.load(open(os.path.join(wdir, "manifest.json")))
    assert man["q"] == 8 and man["tier"] == "bo" and man["seed_id"] == 9 and "design_space_md5" in man
    assert os.path.isfile(os.path.join(wdir, "README.md"))
    with pytest.raises(RuntimeError, match="REFUSED"):                   # collision check
        ww.build_round_wave(root, ds, "methods_E_qnehvi_s9_r1", U)
    with pytest.raises(AssertionError, match="duplicate"):
        ww.build_round_wave(root, ds, "methods_E_qnehvi_s9_r2", np.vstack([U[:7], U[6]]))


def test_gitignore_line_required(root, ds, tmp_path):
    bad = str(tmp_path / "noignore")
    os.makedirs(os.path.join(bad, "waves"))
    open(os.path.join(bad, ".gitignore"), "w").write("extracts/n0_E/**/*.csv.gz\n")
    with pytest.raises(AssertionError, match="methods_E_"):
        ww.build_round_wave(bad, ds, "methods_E_x_s0_r1", np.full((8, 6), 0.5) + np.arange(8)[:, None] * 0.01)


def test_templates_carry_the_native_blocks(root):
    paths = ww.write_templates(root, out_dir=os.path.join(root, "analysis", "methods_E"))
    arr = open(paths["methods_E_array.sh"]).read()
    col = open(paths["methods_E_collect.sh"]).read()
    for p in paths.values():
        subprocess.run(["bash", "-n", p], check=True)
    for s in ("GAP_DECISION.json", "ruc_mipgap", "ruc_time_limit", "SMOKE_PASS", "METHODS_E_START", "METHODS_E_END",
              "get_row.py", "retrofit_gen_dict_${SGE_TASK_ID}", "design_matrix.csv is absent" if False else "design_matrix.csv"):
        assert s in arr, s
    for s in ("--full", "pool_full_metrics.json", "COLLECTED", "csv\\.gz", "identity.txt", "wallclock.csv", "runtimes.csv",
              "push_with_retries", "ercot-bot", "FAILED_$WAVE.md", "methods_E.flock"):
        assert s in col, s
    assert "conda activate PCM_ERCOT" in arr and "module load gurobi" in arr


def test_stub_loader_refuses_without_v3_identity_and_applies_overrides(root):
    waves = ["n0_E"]
    X, U, Y, meta = sl.load(waves, objectives=["V1", "E1", "R4", "N1"],
                            design_space=os.path.join(root, "waves", "design_space_E.json"), extr=os.path.join(root, "extracts"))
    assert X.shape == (48, 6) and Y.shape == (48, 4) and list(meta.columns) == sl.META_COLS
    assert meta.attrs["refused"] == 0 and meta.attrs["loader"] == "stub"
    gp = np.array([s["gen_pmax"] for s in json.load(open(os.path.join(root, "waves", "design_space_E.json")))["sites"]])
    np.testing.assert_allclose(U.to_numpy(), X.to_numpy() / gp)
    assert (meta["tier"].iloc[:32] == "nav").all() and (meta["tier"].iloc[32:] == "grading").all()
    assert list(meta["sobol_index"]) == list(range(48)) and not meta["suspect"].any() and (meta["R1"] == 0).all()
    # a non-v3 identity and a missing identity are both REFUSED
    rd = os.path.join(root, "extracts", "n0_E", "run_index_5")
    open(os.path.join(rd, "identity.txt"), "w").write("IDENTITY from GAP_DECISION.json: ruc_mipgap=0.01 ruc_time_limit=120.0 (x)\n")
    os.remove(os.path.join(root, "extracts", "n0_E", "run_index_6", "identity.txt"))
    X2, _, _, m2 = sl.load(waves, design_space=os.path.join(root, "waves", "design_space_E.json"), extr=os.path.join(root, "extracts"))
    assert len(X2) == 46 and m2.attrs["refused"] == 2 and "n0_E:5" not in X2.index and "n0_E:6" not in X2.index
    sc.fake_collect(root, "n0_E")                                        # restore
    json.dump({"R1": 3.0, "suspect": True, "V1": 1.0}, open(os.path.join(root, "extracts", "n0_E", "run_index_7", "stub_pool_row.json"), "w"))
    _, _, Y3, m3 = sl.load(waves, objectives=["V1"], design_space=os.path.join(root, "waves", "design_space_E.json"), extr=os.path.join(root, "extracts"))
    assert m3.loc["n0_E:7", "R1"] == 3.0 and bool(m3.loc["n0_E:7", "suspect"]) and Y3.loc["n0_E:7", "V1"] == 1.0
    os.remove(os.path.join(root, "extracts", "n0_E", "run_index_7", "stub_pool_row.json"))


def test_design_rows_refuses_near_zero_site(ds):
    """prompt 66 (E): a u in (0, 1e-9) would put a PEM unit with fraction ~5e-17 into the PCM."""
    U = np.full((2, ds.d), 0.5)
    U[1, 0] = 5.55e-17
    with pytest.raises(AssertionError, match="near-zero"):
        ww.design_rows(ds, U)
