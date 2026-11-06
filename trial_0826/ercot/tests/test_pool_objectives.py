"""Prompt 57 Part A tests for pool_objectives.py.

Run only this file:  cd trial_0826/ercot && python -m pytest tests/test_pool_objectives.py -q
(tests/test_cost_fix_v2.py needs the egret fork on CRC.)

Blocks: (1) synthetic 2-run fixture -> every section-2 formula by hand;
(2) N5 bus-name join + padding drop; (3) X1 EF sensitivity columns;
(4) real-extract regression against the FROZEN objectives_t1_v2.csv
(skipped when the extracts are not on disk); (5) helpers.
"""
import gzip
import json
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ERCOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ERCOT))
import pool_objectives as po  # noqa: E402

# compute_objectives.gen_summary fillna(False): pandas 2.x future-downcasting notice
pytestmark = pytest.mark.filterwarnings("ignore:Downcasting object dtype arrays:FutureWarning")

DEFS = po.load_defs(str(ERCOT / "analysis" / "pool" / "pool_definitions.json"))
HAVE_EXTRACTS = (ERCOT / "extracts" / "base_2019_v2" / "run_index_1" / "bus_lmps.csv.gz").is_file()


# --------------------------------------------------------------------------
# synthetic fixture
# --------------------------------------------------------------------------
OVERALL_COLS = ["Total demand", "Total fixed costs", "Total generation costs", "Total costs",
                "Total load shedding", "Total over generation", "Total reserve shortfall",
                "Total renewables curtailment", "Total on/offs", "Total sum on/off ramps",
                "Total sum nominal ramps", "Maximum observed demand",
                "Overall renewables penetration rate", "Cumulative average price",
                "Total energy payments", "Total reserve payments", "Total uplift payments",
                "Total payments", "Cumulative average payments"]
GEN_COLS = ["Generator", "unit_type", "is_pem", "output_mwh", "curtailment_mwh",
            "Unit Market Revenue", "Unit Uplift Payment", "Unit Cost", "starts", "pmax_mw"]


def _w(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


def _overall(total_demand, fixed, var, total, reserve, onoffs, ramps, nramps, pen,
             energy_pay, uplift, total_pay):
    vals = [total_demand, fixed, var, total, 0.0, 0.0, reserve, 170.0, onoffs, ramps, nramps,
            600.0, pen, total / total_demand, energy_pay, 10.0, uplift, total_pay,
            total_pay / total_demand]
    return ",".join(OVERALL_COLS) + "\n" + ",".join(str(v) for v in vals) + "\n"


def _daily(ren_pay, energy_pay, demand):
    cols = ["Date", "Demand", "Renewables available", "Renewables used",
            "Renewables penetration rate", "Average price", "Fixed costs", "Generation costs",
            "Load shedding", "Over generation", "Reserve shortfall", "Renewables curtailment",
            "Number on/offs", "Sum on/off ramps", "Sum nominal ramps",
            "Renewables energy payments", "Renewables uplift payments",
            "Thermal energy payments", "Thermal uplift payments", "Total energy payments",
            "Total uplift payments", "Total reserve payments", "Total payments",
            "Average payments"]
    rows = []
    for i, (rp, ep, dm) in enumerate(zip(ren_pay, energy_pay, demand)):
        r = {c: 0.0 for c in cols}
        r.update({"Date": f"2019-01-0{i + 1}", "Demand": dm,
                  "Renewables energy payments": rp, "Total energy payments": ep})
        rows.append(",".join(str(r[c]) for c in cols))
    return ",".join(cols) + "\n" + "\n".join(rows) + "\n"


def _gen(with_twin, wind_curt):
    rows = [
        "1,NUC,,1000,,0,0,0,0.0,2430.0",
        "93,NUC,,0,,0,0,0,0.0,2708.6",
        "5,COAL,,2000,,0,0,0,3.0,500.0",
        "7,CT,,1000,,0,0,0,5.0,200.0",
        f"275,WIND,False,300,{wind_curt},0,0,,,400.0",
        "101,PV,False,100,50,0,0,,,50.0",
        "8,HYDRO,False,10,0,0,0,,,10.0",
    ]
    if with_twin:
        rows.append("275_PEM,WIND,True,50,20,0,0,,,400.0")
    return ",".join(GEN_COLS) + "\n" + "\n".join(rows) + "\n"


@pytest.fixture(scope="module")
def synth(tmp_path_factory):
    root = tmp_path_factory.mktemp("synth")
    extr, waves, data = root / "extracts", root / "waves", root / "data"
    # --- data dir ---------------------------------------------------------
    _w(data / "bus.csv",
       "Bus ID,Bus Name,BaseKV,Bus Type,MW Load,MVAR Load,V Mag,V Angle,Area,Zone,Bus Lat,Bus Long\n"
       "1,A 345,345,PV,1,0,1,0,1,EAST,0,0\n"
       "120,Knox City 345,345,PV,1,0,1,0,120,NORTH,0,0\n"
       "2,B 345,345,PV,1,0,1,0,2,WEST,0,0\n")
    _w(data / "branch.csv",
       "UID,From Bus,To Bus,R,X,B,Cont Rating,LTE Rating,STE Rating,Tr Ratio\n"
       "L4,120,2,0,0,0,100,100,100,0\n"
       "L9,1,2,0,0,0,100,100,100,0\n"
       "L252,2,120,0,0,0,100,100,100,0\n")
    _w(data / "REAL_TIME_load.csv",
       "Year,Month,Day,Period,1,2,120\n"
       "2019,1,1,1,100,300,600\n"
       "2019,1,1,2,200,200,600\n"
       "2020,1,1,1,999,999,999\n")          # year-end padding: must be dropped by the join
    # --- wave --------------------------------------------------------------
    _w(waves / "synth" / "design_matrix.csv",
       "index,oat_site,unit_type,bus,omega,bid,gen_pmax,start_date,num_days,replicate_of\n"
       "1,__BASE_REPLICATE__,,,,,,01-01-2019,365,\n"
       "2,275,WIND,120,0.5,40.0,400.0,01-01-2019,365,\n"
       "3,__ALL__,,,,40.0,,01-01-2019,365,\n")
    _w(waves / "synth" / "retrofit_gen_dict_3.json",
       json.dumps({"275": {"PEM_bid": 40.0, "PEM_fraction": 0.5, "gen_pmax": 400.0},
                   "30": {"PEM_bid": 40.0, "PEM_fraction": 0.4, "gen_pmax": 1000.0}}))
    # --- run 1: base, slim, one RUC not OPTIMAL (S2 trip) ---------------------
    r1 = extr / "synth" / "run_index_1"
    _w(r1 / "overall.csv", _overall(1000.0, 100.0, 200.0, 300.5, 7.0, 10, 13.0, 25.0, 40.0,
                                     4000.0, 0.0, 4010.0))
    _w(r1 / "daily_summary.csv", _daily([50.0, 50.0], [1000.0, 3000.0], [400.0, 500.0]))
    _w(r1 / "gen_summary.csv", _gen(with_twin=False, wind_curt=120))
    _w(r1 / "committed_hourly.csv", "Date,Hour,committed_mw,num_committed\n"
       "2019-01-01,0,150.0,3\n2019-01-01,1,250.0,5\n")
    _w(r1 / "line_summary.csv",
       "Line,cont_rating,max_abs_flow,p99_abs_flow,mean_abs_flow,sum_violation,hours_ge_99pct\n"
       "L4,100,100,100,50,0.0,12\nL9,100,50,40,20,0.0,0\nL252,100,100,90,60,1.0,8\n")
    _w(r1 / "ruc_quality.csv", "ruc_date,final_gap_pct,sol_count,status,solve_time_s,ruc_cost\n"
       "start_date,1.0,1,OPTIMAL,1.0,100.0\n2019-01-02,0.5,1,TIME_LIMIT,1.0,200.0\n")
    # --- run 2: WIND site 275 at bus 120, --full ----------------------------
    r2 = extr / "synth" / "run_index_2"
    _w(r2 / "overall.csv", _overall(1000.0, 100.0, 200.0, 300.0, 5.0, 8, 11.0, 22.0, 45.0,
                                     5000.0, 0.0, 5010.0))
    _w(r2 / "daily_summary.csv", _daily([100.0, 200.0], [2000.0, 3000.0], [400.0, 500.0]))
    _w(r2 / "gen_summary.csv", _gen(with_twin=True, wind_curt=100))
    _w(r2 / "committed_hourly.csv", "Date,Hour,committed_mw,num_committed\n"
       "2019-01-01,0,100.0,3\n2019-01-01,1,200.0,4\n")
    _w(r2 / "line_summary.csv",
       "Line,cont_rating,max_abs_flow,p99_abs_flow,mean_abs_flow,sum_violation,hours_ge_99pct\n"
       "L4,100,100,100,50,1.5,10\nL9,100,50,40,20,0.0,0\nL252,100,100,90,60,2.0,7\n")
    _w(r2 / "ruc_quality.csv", "ruc_date,final_gap_pct,sol_count,status,solve_time_s,ruc_cost\n"
       "start_date,1.0,1,OPTIMAL,1.0,100.0\n2019-01-02,0.5,1,OPTIMAL,1.0,200.0\n")
    lm = ("Date,Hour,Bus,LMP,LMP DA\n"
          "2019-01-01,0,A 345,10,10\n2019-01-01,0,B 345,30,30\n2019-01-01,0,Knox City 345,40,40\n"
          "2019-01-01,1,A 345,20,20\n2019-01-01,1,B 345,20,20\n2019-01-01,1,Knox City 345,500,500\n")
    with gzip.open(r2 / "bus_lmps.csv.gz", "wt") as f:
        f.write(lm)
    return {"extr": str(extr), "waves": str(waves), "data": str(data)}


def _row(synth, idx):
    return po.pool_row(f"synth:{idx}", extr=synth["extr"], waves=synth["waves"],
                       data_dir=synth["data"], defs=DEFS)


# --------------------------------------------------------------------------
# (1) every formula on the synthetic run
# --------------------------------------------------------------------------
def test_synthetic_every_formula(synth):
    r = _row(synth, 2)
    assert r["site"] == "275" and r["unit_type"] == "WIND" and r["bus"] == 120.0
    assert r["pem_mw"] == pytest.approx(200.0)            # omega x gen_pmax, not gen_summary
    assert r["full_extract"] is True
    # V
    assert r["V1"] == pytest.approx(150.0)                # non-PEM WIND+PV curtailment
    assert r["V2"] == pytest.approx(45.0)
    assert r["V3"] == pytest.approx(50.0 / 550.0)         # twin output / non-PEM VRE available
    # E
    assert r["E1"] == 300.0 and r["E2"] == 100.0 and r["E3"] == 200.0
    assert r["E4"] == 5010.0 and r["E5"] == 0.0
    assert r["E6"] == pytest.approx(300.0)                # sum daily Renewables energy payments
    assert r["E7"] == pytest.approx(5.0)                  # energy payments / demand
    assert r["E8_slim_daily_settle_sd"] == pytest.approx(np.std([5.0, 6.0], ddof=1))
    # R
    assert r["R1"] == 0.0 and r["R2"] == 5.0 and r["R3"] == 0.0
    assert r["R4"] == 8.0 and r["R5"] == 11.0 and r["R6"] == 22.0
    assert r["R7"] == pytest.approx(300.0) and r["R8"] == 7
    # N
    assert r["N1"] == 17 and r["N2"] == 2 and r["N3"] == pytest.approx(3.5)
    assert r["N4"] == 17 and r["N4_L4"] == 10 and r["N4_L252"] == 7 and "N4_L9" not in r
    # D
    assert r["D1"] == pytest.approx(20.0) and r["h2_source"] == "twin_curtailment"
    assert r["D2"] == pytest.approx(20.0 / (200.0 * 8760))
    assert r["D3_gen1_starts"] == 0.0 and r["D3_gen93_starts"] == 0.0
    # SUSPECT inputs + gap
    assert r["S1_ok"] and r["S2_ok"] and r["n_ruc"] == 2 and r["n_ruc_optimal"] == 2
    assert r["G_run_usd"] == pytest.approx(1.0 * 100 / 100 + 0.5 * 200 / 100)
    assert r["max_gap_pct"] == 1.0


def test_synthetic_base_slim_and_suspect(synth):
    r = _row(synth, 1)
    assert r["pem_mw"] == 0.0 and r["full_extract"] is False
    assert r["V1"] == pytest.approx(170.0) and r["V3"] == 0.0 and r["D1"] == 0.0
    for c in ("E8", "E9", "N5", "N5_unweighted_check"):
        assert np.isnan(r[c]), c                            # never imputed on slim
    assert r["S1_resid_usd"] == pytest.approx(0.5) and r["S1_ok"]
    assert r["S2_ok"] is False and r["n_ruc_optimal"] == 1


def test_build_pool_flags_deltas_dead(synth):
    wide = po.build_pool(keys=["synth:1", "synth:2"], extr=synth["extr"], waves=synth["waves"],
                         data_dir=synth["data"], defs=DEFS, verbose=False)
    assert list(wide["distinct_design_id"]) == ["D01", "D02"]
    assert list(wide["suspect"]) == [True, False]           # run 1 trips S2
    assert list(wide["S3_ok"]) == [True, True]
    d = po.deltas(wide, base_key="synth:1").set_index("key")
    assert d.loc["synth:2", "V1"] == pytest.approx(-20.0)
    assert d.loc["synth:2", "E1"] == pytest.approx(-0.5)
    assert d.loc["synth:1", "N1"] == 0.0
    dead = po.dead_list(wide).set_index("id")
    assert dead.loc["E5", "status"] == "DEAD" and dead.loc["E5", "max_abs_value"] == 0.0
    assert dead.loc["R1", "status"] == "DEAD" and dead.loc["R3", "status"] == "DEAD"
    assert dead.loc["E8", "status"] == "UNDETERMINED (1 value)"
    assert dead.loc["V1", "status"] == "ALIVE"


# --------------------------------------------------------------------------
# (2) N5 bus-name join
# --------------------------------------------------------------------------
def test_n5_bus_name_join_and_padding(synth):
    r = _row(synth, 2)
    # hour 0: Knox 40, load-weighted mean (10*100 + 30*300 + 40*600)/1000 = 34 -> +6
    # hour 1: Knox 500, (20*200 + 20*200 + 500*600)/1000 = 308 -> +192
    assert r["N5"] == pytest.approx((6.0 + 192.0) / 2)
    assert r["N5_unweighted_check"] == pytest.approx(((40 - 80 / 3) + (500 - 180)) / 2)
    assert r["E9"] == 1 and r["E9_lmp_max"] == 500.0      # one bus-hour at LMP >= 450
    assert r["E8"] == pytest.approx(np.std([10, 30, 40, 20, 20, 500], ddof=1))
    assert po.bus_name(synth["data"], 120) == "Knox City 345"
    assert po.pocket_lines(synth["data"], 120) == ["L4", "L252"]


def test_n5_refuses_unmatched_bus_name(synth, tmp_path):
    bad = tmp_path / "data_bad"
    bad.mkdir()
    for f in ("branch.csv", "REAL_TIME_load.csv"):
        (bad / f).write_text((Path(synth["data"]) / f).read_text())
    (bad / "bus.csv").write_text((Path(synth["data"]) / "bus.csv").read_text()
                                 .replace("Knox City 345", "Knox City 138"))
    with pytest.raises(AssertionError):
        po.lmp_candidates(po.run_dir("synth:2", synth["extr"]), str(bad), DEFS)


# --------------------------------------------------------------------------
# (3) X1 EF sensitivity columns
# --------------------------------------------------------------------------
def test_x1_emission_factor_sensitivity(synth):
    ef = DEFS["emission_factors_t_per_mwh"]
    assert ef["COAL"] == 1.00 and ef["CT"] == 0.55
    assert all(ef[k] == 0.0 for k in ("NUC", "HYDRO", "WIND", "PV"))
    r = _row(synth, 2)
    x1 = 2000 * 1.00 + 1000 * 0.55                       # twin + VRE + NUC + HYDRO contribute 0
    assert r["X1"] == pytest.approx(x1)
    assert r["X1_ef_lo"] == pytest.approx(0.8 * x1) and r["X1_ef_hi"] == pytest.approx(1.2 * x1)
    assert r["X1_gas_lo"] == pytest.approx(x1 - 0.2 * 550) and r["X1_gas_hi"] == pytest.approx(x1 + 0.2 * 550)


# --------------------------------------------------------------------------
# (4) real extracts: regression against the FROZEN objectives_t1_v2.csv
# --------------------------------------------------------------------------
@pytest.fixture(scope="module")
def wide_real():
    if not HAVE_EXTRACTS:
        pytest.skip("v2 extracts not on disk")
    fr = pd.read_csv(po.FROZEN_T1, dtype={"index": str})
    keys = sorted({f"{w}:{int(i)}" for w, i in zip(fr["wave"], fr["index"])})
    return po.build_pool(keys=keys, defs=DEFS, verbose=False)


def test_regression_vs_frozen_t1_v2(wide_real):
    rep = po.regression_vs_frozen(wide_real)
    assert len(rep) == 144 and rep["ok"].all(), rep[~rep["ok"]]
    copied = rep[rep["copied_from_frozen"]]
    assert sorted(copied["key"], key=lambda k: int(k.split(":")[1])) == [
        f"selection_t1_v2:{i}" for i in range(6, 12)]
    w = wide_real.set_index("key")
    assert (w.loc[[f"selection_t1_v2:{i}" for i in range(6, 12)], "h2_source"] == "frozen_t1_v2").all()
    assert (w.loc[[f"selection_t1_v2:{i}" for i in (3, 4, 5)], "h2_source"] == "twin_curtailment").all()


def test_base_run_reference_values(wide_real):
    b = wide_real.set_index("key").loc["base_2019_v2:1"]
    assert b["full_extract"]
    assert b["N1"] == 36413 and b["N2"] == 39 and b["N4"] == 5460 and b["N4_L252"] == 5460
    assert b["N3"] == pytest.approx(91029, abs=1.0)
    assert b["N5_unweighted_check"] == pytest.approx(-17.36, abs=0.01)   # seen-before reference
    assert b["E9"] == 0 and b["E9_lmp_max"] == pytest.approx(446.1, abs=0.1)
    assert b["E5"] == 0.0 and b["R1"] == 0.0 and b["R3"] == 0.0
    assert b["n_ruc"] == 365 and b["S2_ok"] and b["S1_ok"] and b["S3_ok"]
    assert b["replicate_of"] == ""
    w = wide_real.set_index("key")
    assert w.loc["selection_t1_v2:3", "replicate_of"] == "screening_v2/ercot:1"
    assert w.loc["selection_t1_v2:11", "replicate_of"] == "selection_t1_v2:8"
    assert w.loc["screening_v2/ercot:11", "replicate_of"] == "base_2019_v2:1"
    assert w.loc["screening_v2/ercot:12", "replicate_of"] == "screening_v2/ercot:1"
    assert (w.loc["screening_v2/ercot:12", "distinct_design_id"]
            == w.loc["screening_v2/ercot:1", "distinct_design_id"])


# --------------------------------------------------------------------------
# (4b) per-run mode (prompt 58 T2): --run-dir / --out
# --------------------------------------------------------------------------
def test_per_run_mode_synthetic(synth, tmp_path):
    """Design-matrix independent; E8/E9/N5 equal pool_row; headroom NaN without thermal.csv.gz."""
    d = po.run_dir("synth:2", synth["extr"])
    m = po.per_run_metrics(d, data_dir=synth["data"], defs=DEFS)
    r = _row(synth, 2)
    for c in ("E8", "E9", "N5", "N5_unweighted_check", "E9_lmp_max"):
        assert m[c] == pytest.approx(r[c]), c
    assert m["full_extract"] is True and m["R7"] == pytest.approx(300.0) and m["R8"] == 7
    assert np.isnan(m["H_headroom_mwh"])                 # no thermal.csv.gz in the fixture
    assert m["manifest"]["manifest_present"] is False
    assert m["n_ruc"] == 2 and m["n_ruc_optimal"] == 2 and m["G_run_usd"] == pytest.approx(2.0)
    out = tmp_path / "x" / "pool_full_metrics.json"
    assert po.main(["--run-dir", d, "--out", str(out), "--data_dir", synth["data"]]) == 0
    back = json.loads(out.read_text())
    assert back["E9"] == 1 and back["H_headroom_mwh"] is None    # NaN -> null, never imputed
    # slim run: E8/E9/N5 NaN
    m1 = po.per_run_metrics(po.run_dir("synth:1", synth["extr"]), data_dir=synth["data"], defs=DEFS)
    assert m1["full_extract"] is False and all(np.isnan(m1[c]) for c in ("E8", "E9", "N5"))


def test_headroom_diagnostic_synthetic(tmp_path):
    data = tmp_path / "data"
    data.mkdir()
    (data / "gen.csv").write_text("GEN UID,Bus ID,Unit Type,PMax MW,PMin MW\n"
                                  "1,107,NUC,2430.0,729.0\n5,3,COAL,500.0,100.0\n7,4,CT,200.0,50.0\n")
    run = tmp_path / "run"
    run.mkdir()
    rows = ["Date,Hour,Generator,Dispatch,Unit State,Unit Cost,Unit Market Revenue,unit_type",
            "2019-01-01,0,1,2430.0,True,1,1,NUC", "2019-01-01,0,5,400.0,True,1,1,COAL",
            "2019-01-01,0,7,0.0,False,0,0,CT",
            "2019-01-01,1,1,2430.0,True,1,1,NUC", "2019-01-01,1,5,500.0,True,1,1,COAL",
            "2019-01-01,1,7,150.0,True,1,1,CT"]
    with gzip.open(run / "thermal.csv.gz", "wt") as f:
        f.write("\n".join(rows) + "\n")
    (run / "committed_hourly.csv").write_text("Date,Hour,committed_mw,num_committed\n"
                                              "2019-01-01,0,2930.0,2\n2019-01-01,1,3130.0,3\n")
    h = po.headroom_diagnostic(str(run), str(data))
    # hour 0: (2430-2430) + (500-400) = 100; hour 1: 0 + 0 + (200-150) = 50
    assert h["H_headroom_mwh"] == pytest.approx(150.0) and h["H_headroom_mean_mw"] == pytest.approx(75.0)
    assert h["H_headroom_min_mw"] == pytest.approx(50.0) and h["H_hours"] == 2
    assert h["H_committed_cap_mwh"] == pytest.approx(2930.0 + 3130.0)
    assert h["H_committed_cap_minus_R7_max_abs_mw"] == pytest.approx(0.0)
    assert h["H_n_thermal_units"] == 3
    # an unknown generator is refused, never silently dropped
    (data / "gen.csv").write_text("GEN UID,Bus ID,Unit Type,PMax MW,PMin MW\n1,107,NUC,2430.0,729.0\n")
    with pytest.raises(AssertionError):
        po.headroom_diagnostic(str(run), str(data))


@pytest.mark.skipif(not HAVE_EXTRACTS, reason="v2 extracts not on disk")
def test_per_run_mode_base_run_index_1(tmp_path):
    """The only local --full run; POOL_V2.md section 1 values: N5 -18.40
    (load-weighted), E9 = 0, E8 = 15.48. Manifest md5s of the 4 gz tables verified."""
    d = str(ERCOT / "extracts" / "base_2019_v2" / "run_index_1")
    out = tmp_path / "pool_full_metrics.json"
    m = po.write_per_run(d, str(out), defs=DEFS)
    assert m["full_extract"] is True
    assert m["N5"] == pytest.approx(-18.40, abs=0.01)
    assert m["N5_unweighted_check"] == pytest.approx(-17.36, abs=0.01)
    assert m["E9"] == 0 and m["E9_lmp_max"] == pytest.approx(446.1, abs=0.1)
    assert m["E8"] == pytest.approx(15.48, abs=0.01)
    assert m["R7"] == pytest.approx(361173142.3, rel=1e-9) and m["R8"] == 443791
    assert m["H_hours"] == 8760 and m["H_headroom_mwh"] > 0 and m["H_headroom_min_mw"] >= 0
    assert m["H_committed_cap_minus_R7_max_abs_mw"] < 1.0      # thermal.csv.gz agrees with committed_hourly
    assert m["n_ruc"] == 365 and m["n_ruc_optimal"] == 365
    assert sorted(m["manifest"]["gz_verified"]) == ["bus_lmps.csv.gz", "line_flows.csv.gz",
                                                    "renewables.csv.gz", "thermal.csv.gz"]
    assert m["manifest"]["gz_missing"] == []
    back = json.loads(out.read_text())
    assert back["N5"] == pytest.approx(m["N5"]) and back["manifest"]["md5"]["overall.csv"] == m["overall_md5"]


# --------------------------------------------------------------------------
# (5) helpers
# --------------------------------------------------------------------------
def test_norm_replicate_mapping():
    names = DEFS["v1_to_v2_wave_names"]
    assert po.norm_replicate("selection_t1_v2", "screening_ercot:1", names) == "screening_v2/ercot:1"
    assert po.norm_replicate("selection_t1_v2", "selection_t1:8", names) == "selection_t1_v2:8"
    assert po.norm_replicate("screening_v2/ercot", "base", names) == "base_2019_v2:1"
    assert po.norm_replicate("screening_v2/ercot", "1", names) == "screening_v2/ercot:1"
    assert po.norm_replicate("screening_v2/ercot", "1.0", names) == "screening_v2/ercot:1"
    assert po.norm_replicate("x", "", names) == "" and po.norm_replicate("x", np.nan, names) == ""


def test_pem_mw_all_row_from_retrofit_dict(synth):
    drow = po.design_row("synth", 3, synth["waves"])
    assert drow["site"] == "__ALL__"
    assert po.pem_mw("synth", 3, drow, synth["waves"]) == pytest.approx(0.5 * 400 + 0.4 * 1000)


def test_oriented_and_clusters():
    d = pd.DataFrame({"A": [1, 2, 3, 4, 5], "B": [2, 3, 5, 7, 11], "C": [5, 4, 3, 2, 1]}, dtype=float)
    defs = {"candidates": {"A": {"dir": "min"}, "B": {"dir": "max"}, "C": {"dir": "min"}}}
    O = po.oriented(d, ["A", "B", "C"], defs)
    assert (O["B"] == -d["B"]).all() and (O["A"] == d["A"]).all()
    raw, par = po.spearman_matrices(O, pd.Series([1.0, 2.0, 3.0, 4.0, 5.0]))
    assert raw.loc["A", "C"] == pytest.approx(-1.0) and raw.loc["A", "B"] == pytest.approx(-1.0)
    assert raw.loc["B", "C"] == pytest.approx(1.0)       # oriented -B and C both decrease
    # anti-correlated pairs never cluster; the +1 pair does
    assert po.complete_linkage_clusters(raw, ["A", "B", "C"], 0.90) == [["B", "C"]]
    assert po.complete_linkage_clusters(raw, ["A", "C"], 0.90) == []
    M = pd.DataFrame([[1, .95, .2], [.95, 1, .3], [.2, .3, 1]], index=list("XYZ"), columns=list("XYZ"))
    assert po.complete_linkage_clusters(M, ["X", "Y", "Z"], 0.90) == [["X", "Y"]]
    assert po.complete_linkage_clusters(M, ["X", "Z"], 0.90) == []           # undirected Y cannot cluster


def test_partial_spearman_removes_common_cause():
    z = np.arange(1, 17, dtype=float)
    rng = np.random.default_rng(0)
    x = z + 3.0 * rng.normal(size=16)
    y = z + 3.0 * rng.normal(size=16)
    from scipy import stats
    raw = float(stats.spearmanr(x, y).statistic)
    assert raw > 0.5
    assert abs(po.partial_spearman(x, y, z)) < raw          # the common cause z is removed


def test_definitions_global_order_complete():
    cands = set(DEFS["candidates"]) | {"D3"}
    go = DEFS["global_order"]
    assert len(go) == len(set(go)) and set(go) == cands
    fam = {f: i for i, f in enumerate(DEFS["family_order"])}
    ranked = [c for c in go if DEFS["candidates"].get(c, {}).get("priority") is not None]
    keyf = lambda c: (DEFS["candidates"][c]["priority"], fam[DEFS["candidates"][c]["family"]],  # noqa: E731
                      int(c[1:]))
    assert ranked == sorted(ranked, key=keyf)
    assert DEFS["thresholds"]["lmp_scarcity_threshold_usd_per_mwh"] == 450.0
