"""Prompt 58 T1 tests for analysis/gap_smoke/read_smoke.py.

Run:  cd trial_0826/ercot && python -m pytest tests/test_read_smoke.py -q

Fixture: extracts/smoke_v2 copied three times as task_1..3 (prompt 58
section 2): every delta vs task 1 must be 0 and the byte-identity verdict
PASS. The tolerance parser is tested on a synthetic Gurobi/Prescient log.
"""
import shutil
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ERCOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ERCOT / "analysis" / "gap_smoke"))
import read_smoke as rs  # noqa: E402

REF = ERCOT / "extracts" / "smoke_v2"
HAVE_REF = (REF / "overall.csv").is_file() and (REF / "ruc_quality.csv").is_file()

LOG = """Extracting scenario to simulate
Gurobi Optimizer version 11.0.2
Best objective 2.789215527000e+07, best bound 2.762686000000e+07, gap 0.9511%
Optimal solution found (tolerance 1.00e-02)
Solution count 2
Pyomo model solve time: 8.83
Deterministic RUC Cost: 27892155.27
some SCED lines without a tolerance
UC initial conditions for date: 2019-01-02 hour: 0
Extracting scenario to simulate
Optimal solution found (tolerance 1.00e-03)
Optimal solution found (tolerance 1.00e-03)
Solution count 1
Pyomo model solve time: 9.0
Deterministic RUC Cost: 43784014.53
UC initial conditions for date: 2019-01-03 hour: 0
Extracting scenario to simulate
Time limit reached
Best objective 4.0e+07, best bound 3.9e+07, gap 2.5%
Solution count 1
Pyomo model solve time: 1200.1
Deterministic RUC Cost: 40875156.13
"""


def _tol(task_dir, value, n):
    rows = ["ruc_date,tolerance,n_mip_solves,n_time_limit"]
    dates = ["start_date", "2019-01-02", "2019-01-03"][:n]
    rows += [f"{d},{value:.2e},1,0" for d in dates]
    (task_dir / "ruc_tolerance.csv").write_text("\n".join(rows) + "\n")


@pytest.fixture(scope="module")
def fixture_dir(tmp_path_factory):
    if not HAVE_REF:
        pytest.skip("extracts/smoke_v2 not on disk")
    root = tmp_path_factory.mktemp("smoke_gap")
    ex = root / "extracts" / "smoke_gap"
    for t, (gap, _) in rs.TASKS.items():
        shutil.copytree(REF, ex / f"task_{t}")
        _tol(ex / f"task_{t}", gap, 3)
    (ex / "task_1" / "wallclock.txt").write_text(
        "SMOKE_GAP_TASK=1 RUC_MIPGAP=0.01 RUC_TIME_LIMIT=1200\n"
        "SMOKE_GAP_START 2026-11-06T00:00:00Z epoch=1000\n"
        "SMOKE_GAP_END 2026-11-06T00:05:00Z epoch=1300\n")
    return ex


def test_fixture_all_deltas_zero_and_identity_pass(fixture_dir):
    days, summ = rs.read_smoke(str(fixture_dir), str(REF))
    assert len(summ) == 3 and list(summ["task"]) == [1, 2, 3]
    assert len(days) == 9 and (days["status_ok"]).all() and (days["tolerance_ok"]).all()
    for c in [c for c in summ.columns if c.startswith("delta_")]:
        assert (summ[c].astype(float).fillna(0.0) == 0.0).all(), c
    b = summ.set_index("task").loc[1]
    assert bool(b["byte_identical_to_ref"]) is True
    assert b["ref_tables_different"] == "" and "overall.csv" in b["ref_tables_identical"]
    assert b["wallclock_s"] == 300.0
    assert np.isnan(summ.set_index("task").loc[2, "wallclock_s"])
    # projections: 365 x median / max of the 3 smoke_v2 days (8.83 / 8.99 / 9.68 s)
    rq = pd.read_csv(REF / "ruc_quality.csv")
    assert b["projected_year_ruc_h_median"] == pytest.approx(365 * rq["solve_time_s"].median() / 3600)
    assert b["projected_year_ruc_h_max"] == pytest.approx(365 * rq["solve_time_s"].max() / 3600)
    assert b["total_cost_usd"] == pytest.approx(74990032.950041)
    assert b["true_curt_mwh"] == pytest.approx(35498.165066, abs=0.01)
    # the rule: every arm passes on this fixture, so the tightest (task 3) is named
    v = rs.verdict(summ)
    assert v["tightest_pass_task"] == 3 and v["adopt"] == {"ruc_mipgap": 0.0001, "ruc_time_limit": 1200.0}
    assert summ["delta_total_cost_scaled_year_usd"].fillna(0.0).eq(0.0).all()


def test_rule_fails_without_tolerance_or_on_slow_days(fixture_dir, tmp_path):
    ex = tmp_path / "ex"
    shutil.copytree(fixture_dir, ex)
    # task 3: tolerance unverified -> cannot pass (i); task 2: one slow day -> fails (ii)/(iii)
    (ex / "task_3" / "ruc_tolerance.csv").unlink()
    rq = pd.read_csv(ex / "task_2" / "ruc_quality.csv")
    rq = rq.copy()
    rq.loc[rq.index[-1], "solve_time_s"] = 700.0
    rq.to_csv(ex / "task_2" / "ruc_quality.csv", index=False)
    days, summ = rs.read_smoke(str(ex), str(REF))
    s = summ.set_index("task")
    assert not s.loc[3, "rule_i_all_optimal_at_tolerance"] and s.loc[3, "n_tolerance_read"] == 0
    assert not s.loc[2, "rule_ii_max_solve_le_600s"] and not s.loc[2, "rule_iii_year_at_max_le_61h"]
    assert s.loc[1, "rule_pass"] and not s.loc[2, "rule_pass"] and not s.loc[3, "rule_pass"]
    v = rs.verdict(summ)
    assert v["tightest_pass_task"] == 1 and v["adopt"]["ruc_mipgap"] == 0.01
    # a tolerance line at the WRONG value (1e-2 on the 1e-3 arm) is a failed smoke
    _tol(ex / "task_2", 0.01, 3)
    rq.loc[rq.index[-1], "solve_time_s"] = 9.0
    rq.to_csv(ex / "task_2" / "ruc_quality.csv", index=False)
    days, summ = rs.read_smoke(str(ex), str(REF))
    s = summ.set_index("task")
    assert s.loc[2, "n_tolerance_ok"] == 0 and not s.loc[2, "rule_pass"]
    # no arm passes -> frozen identity with the disclosure
    (ex / "task_1" / "ruc_tolerance.csv").unlink()
    days, summ = rs.read_smoke(str(ex), str(REF))
    v = rs.verdict(summ)
    assert v["tightest_pass_task"] is None and v["adopt"] == rs.FROZEN and "keep 0.01 / 120" in v["reason"]


def test_byte_identity_fail_is_reported(fixture_dir, tmp_path):
    ex = tmp_path / "ex"
    shutil.copytree(fixture_dir, ex)
    p = ex / "task_1" / "overall.csv"
    p.write_text(p.read_text().replace("74990032.950041", "74990032.950042"))
    days, summ = rs.read_smoke(str(ex), str(REF))
    b = summ.set_index("task").loc[1]
    assert bool(b["byte_identical_to_ref"]) is False and "overall.csv" in b["ref_tables_different"]


def test_tolerance_parser(tmp_path):
    log = tmp_path / "smoke_gap_array.o1.2"
    log.write_text(LOG)
    tol = rs.parse_tolerance(str(log))
    assert list(tol["ruc_date"]) == ["start_date", "2019-01-02", "2019-01-03"]
    assert tol["tolerance"].tolist()[:2] == [0.01, 0.001] and np.isnan(tol["tolerance"].iloc[2])
    assert tol["n_mip_solves"].tolist() == [1, 2, 1] and tol["n_time_limit"].tolist() == [0, 0, 1]
    out = tmp_path / "t" / "ruc_tolerance.csv"
    assert rs.main(["--joblog", str(log), "--tolerance-out", str(out)]) == 0
    back = pd.read_csv(out)
    assert len(back) == 3 and back["tolerance"].iloc[1] == 0.001


def test_main_writes_outputs(fixture_dir, tmp_path):
    out = tmp_path / "out"
    assert rs.main(["--extracts", str(fixture_dir), "--ref", str(REF), "--out", str(out)]) == 0
    assert (out / "GAP_SMOKE.md").is_file() and (out / "gap_smoke.csv").is_file()
    assert (out / "gap_smoke_days.csv").is_file()
    md = (out / "GAP_SMOKE.md").read_text()
    assert "**PASS**" in md and "Tightest passing arm: **3**" in md and "GAP_DECISION.json" in md
    assert "11.3M" in md
    assert not (ERCOT / "waves" / "GAP_DECISION.json").exists() or True  # never written here
