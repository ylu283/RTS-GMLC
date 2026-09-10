"""extract_mediation.py (prompt 20 Task 4): synthetic fixture run-dirs."""

import csv
import json

import numpy as np
import pandas as pd
import pytest

import extract_mediation as em


def write_csv(path, header, rows):
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)


def make_run_dir(tmp_path, hours=20, with_hourly=True, hourly_cols=None):
    """A tiny synthetic Prescient output dir.

    - 303_WIND_1 + twin: twin sells 10 MWh and withholds 5 MWh per hour.
    - Two thermal gens: T1 (pmax 100) ON in hours 0..9, T2 (pmax 50) always ON.
    - Net load = Demand - available renewables ramps upward with hour, so the
      top-5% net-load hours are exactly the last ceil(0.05*hours) hours.
    """
    run = tmp_path / "runs" / "run_index_1"
    run.mkdir(parents=True)
    (run / em.SENTINEL).write_text("ok\n")

    ren_rows = []
    for h in range(hours):
        ren_rows += [
            ["2020-01-01", h, 0, "303_WIND_1", 40.0, 0.0],
            ["2020-01-01", h, 0, "303_WIND_1_PEM", 10.0, 5.0],
        ]
    write_csv(run / "renewables_detail.csv",
              ["Date", "Hour", "Minute", "Generator", "Output", "Curtailment"],
              ren_rows)

    th_rows = []
    for h in range(hours):
        th_rows += [
            ["2020-01-01", h, 0, "T1", 0.0, h < 10, 0.0],
            ["2020-01-01", h, 0, "T2", 0.0, True, 0.0],
        ]
    write_csv(run / "thermal_detail.csv",
              ["Date", "Hour", "Minute", "Generator", "Dispatch", "Unit State",
               "Unit Cost"],
              th_rows)

    if with_hourly:
        cols = hourly_cols or ["Date", "Hour", "Demand", "RenewablesUsed",
                               "RenewablesCurtailment"]
        hs_rows = []
        for h in range(hours):
            base = {"Date": "2020-01-01", "Hour": h, "Demand": 1000.0 + 10 * h,
                    "RenewablesUsed": 50.0, "RenewablesCurtailment": 5.0}
            hs_rows.append([base.get(c, 0.0) for c in cols])
        write_csv(run / "hourly_summary.csv", cols, hs_rows)
    return run


PMAX = {"T1": 100.0, "T2": 50.0}
RETROFIT = {"303_WIND_1": {"PEM_bid": 30.0, "PEM_fraction": 0.5,
                           "gen_pmax": 847.0}}


def test_extract_run_known_values(tmp_path):
    run = make_run_dir(tmp_path, hours=20)
    rows = em.extract_run(run, RETROFIT, PMAX)
    assert len(rows) == 1
    r = rows[0]
    assert r["site"] == "303_WIND_1"
    assert r["pem_bid"] == 30.0
    assert r["pem_sales_mwh"] == pytest.approx(200.0)      # 10 x 20 h
    assert r["pem_withheld_mwh"] == pytest.approx(100.0)   # 5 x 20 h
    # T1 on 10 h x 100 MW + T2 on 20 h x 50 MW = 2,000 MWh
    assert r["fleet_committed_mwh"] == pytest.approx(2000.0)
    # net load ramps with hour -> the 95th-percentile threshold (1180.5)
    # keeps exactly the top hour h=19 (5% of 20 h = 1 h); T1 is OFF there,
    # so committed = 1 x 50 MW
    assert r["committed_mwh_top5"] == pytest.approx(50.0)


def test_thermal_only_retrofit_is_skipped(tmp_path, capsys):
    run = make_run_dir(tmp_path)
    rows = em.extract_run(run, {"121_NUCLEAR_1": {"PEM_bid": 30.0,
                                                  "PEM_fraction": 0.5}}, PMAX)
    assert rows == []  # no gen_PEM twin -> no per-site mediation row


def test_missing_hourly_summary_degrades_to_nan(tmp_path, capsys):
    run = make_run_dir(tmp_path, with_hourly=False)
    r = em.extract_run(run, RETROFIT, PMAX)[0]
    assert np.isnan(r["committed_mwh_top5"])
    assert not np.isnan(r["fleet_committed_mwh"])
    assert "WARNING" in capsys.readouterr().out


def test_missing_netload_columns_degrade_to_nan(tmp_path, capsys):
    run = make_run_dir(tmp_path, hourly_cols=["Date", "Hour", "Demand"])
    r = em.extract_run(run, RETROFIT, PMAX)[0]
    assert np.isnan(r["committed_mwh_top5"])
    out = capsys.readouterr().out
    assert "WARNING" in out and "RenewablesUsed" in out


def test_unknown_thermal_generator_warns_and_excludes(tmp_path, capsys):
    run = make_run_dir(tmp_path)
    r = em.extract_run(run, RETROFIT, {"T1": 100.0})[0]  # T2 not in lookup
    assert r["fleet_committed_mwh"] == pytest.approx(1000.0)  # T1 only
    assert "T2" in capsys.readouterr().out


def test_main_end_to_end(tmp_path, capsys):
    wave = tmp_path
    make_run_dir(wave)
    pd.DataFrame({"index": [1, 2], "num_days": [366, 366]}).to_csv(
        wave / "design_matrix.csv", index=False)
    with open(wave / "retrofit_gen_dict_1.json", "w") as f:
        json.dump(RETROFIT, f)
    # site_detail cross-check fixture: matches extract_run's sales exactly
    pd.DataFrame({"index": [1], "site": ["303_WIND_1"],
                  "pem_grid_sales_mwh": [200.0]}).to_csv(
        wave / "site_detail.csv", index=False)
    rc = em.main([str(wave)])
    assert rc == 0
    med = pd.read_csv(wave / "mediation.csv")
    assert len(med) == 1 and med.loc[0, "pem_sales_mwh"] == pytest.approx(200.0)
    out = capsys.readouterr().out
    assert "MISSING (not extracted): indices [2]" in out
    assert "[OK]" in out  # cross-check passed
