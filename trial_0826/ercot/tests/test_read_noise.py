"""Prompt 52 v2.1 tests for analysis/noise_v3/read_noise.py.

Run:  cd trial_0826/ercot && python -m pytest tests/test_read_noise.py -q

Fixture: the 16 noise_v3 rows (layout 16 = the committed wave: per design exact
A, exact B, perturbed A, antithetic perturbed B) synthesized by copying the SLIM
tables of extracts/base_2019_v2/run_index_1 (the --full reference) with tiny
controlled edits to overall.csv and a synthetic pool_full_metrics.json (E8/E9/N5,
as the CRC collector writes it), so every expected median and sd is known.
Paths tested: exact-zero (all exact pairs identical), RULER=0 (R4 untouched),
a firing and a non-firing trigger, the exact-pair-differs path, the shed assert,
the runtime table, and the chi-square / F quantiles against scipy.
"""
import json
import shutil
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ERCOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ERCOT / "analysis" / "noise_v3"))
sys.path.insert(0, str(ERCOT / "tools"))
import make_noise_v3 as mn  # noqa: E402
import read_noise as rn  # noqa: E402

pytestmark = pytest.mark.filterwarnings("ignore:Downcasting object dtype arrays:FutureWarning")

REF = ERCOT / "extracts" / "base_2019_v2" / "run_index_1"
SLIM = ["overall.csv", "daily_summary.csv", "gen_summary.csv", "committed_hourly.csv",
        "line_summary.csv", "ruc_quality.csv", "extract_manifest.json"]
HAVE = all((REF / f).is_file() for f in SLIM) and (ERCOT / mn.V2_DATA_REL / "branch.csv").is_file()

# controlled edits on the 8 perturbed rows: OFF[batch][design_no - 1]; batch A rows 5..8, batch B rows 5..8.
# Every perturbed row is read against the exact copy of its own batch, so its delta is exactly the offset.
E1_OFF = {"A": [100.0, -300.0, 200.0, 400.0], "B": [-150.0, 250.0, -350.0, 50.0]}   # Total costs
E3_OFF = {"A": [10.0] * 4, "B": [10.0] * 4}                                          # Total generation costs
E4_OFF = {"A": [1.0, 0.5, 0.7, 50.0], "B": [1.0, 0.5, 0.7, 50.0]}                    # Total payments
E8_OFF = {"A": [0.5, -0.1, 0.2, 0.3], "B": [0.4, -0.2, 0.1, 0.6]}                    # pool_full_metrics E8
E8_BASE, E9_BASE, N5_BASE = 15.0, 0, -18.4
N_RUNS = 16


def _pop(off):
    """The 8 signed perturbed deltas in read order (batch A designs 1-4, then batch B)."""
    return list(off["A"]) + list(off["B"])


def _levels(off):
    """Per design: sd of {0, delta_A, delta_B} (ddof 1, df 2) — the read_noise level definition."""
    return [float(np.std([0.0, off["A"][n], off["B"][n]], ddof=1)) for n in range(4)]


def _pooled(off):
    s = _levels(off)
    num = sum(2 * x * x for x in s)
    return np.sqrt(num / 8), (num * num / sum((2 * x * x) ** 2 / 2 for x in s) if num > 0 else 8)


# known answers (derived from the offsets, independent of read_noise)
E1_ABS_SORTED = sorted(abs(x) for x in _pop(E1_OFF))      # 50 ... 400
E1_RULER, E1_MIN, E1_MAX = 225.0, 50.0, 400.0
E8_RULER, E8_MIN, E8_MAX = 0.25, 0.1, 0.6


def _edit_overall(path, **delta):
    o = pd.read_csv(path)
    for k, v in delta.items():
        o.loc[0, k] = float(o.loc[0, k]) + v
    o.to_csv(path, index=False)


def _make_run(dst, e8=E8_BASE, e9=E9_BASE, n5=N5_BASE, wall=None):
    dst.mkdir(parents=True, exist_ok=True)
    for f in SLIM:
        shutil.copyfile(REF / f, dst / f)
    (dst / "pool_full_metrics.json").write_text(json.dumps(
        {"full_extract": True, "E8": e8, "E9": e9, "N5": n5, "N5_unweighted_check": n5 + 1.0,
         "E9_lmp_max": 446.1, "n_ruc_time_limit": 0,
         "manifest": {"gz_verified": ["bus_lmps.csv.gz", "line_flows.csv.gz", "renewables.csv.gz", "thermal.csv.gz"]}}))
    (dst / "identity.txt").write_text(
        'IDENTITY from GAP_DECISION.json: ruc_mipgap=0.001 ruc_time_limit=1200.0 ({"ruc_mipgap": 0.001})\n')


@pytest.fixture(scope="module")
def fx(tmp_path_factory):
    if not HAVE:
        pytest.skip("base_2019_v2/run_index_1 slim tables or v2 data dir not on disk")
    root = tmp_path_factory.mktemp("noise_v3")
    waves = root / "waves"
    d, rows, picked, _ = mn.build(waves=waves)
    extr = root / "extracts"
    for b in mn.BATCHES:
        bx = extr / "noise_v3" / b
        bx.mkdir(parents=True)
        (bx / "GAP_DECISION_used.json").write_text('{"ruc_mipgap": 0.001, "ruc_time_limit": 1200}\n')
        wl = ["task,start_epoch,end_epoch,wall_s"]
        assert len(rows[b]) == 8, "fixture expects the committed layout 16"
        for r in rows[b]:
            i = r["index"]
            run = bx / f"run_index_{i}"
            n = r["design_no"] - 1
            e8 = E8_BASE
            if r["copy_type"] == "perturbed":
                e8 = E8_BASE + E8_OFF[b][n]
            _make_run(run, e8=e8)
            if r["copy_type"] == "perturbed":
                _edit_overall(run / "overall.csv", **{"Total costs": E1_OFF[b][n],
                                                      "Total generation costs": E3_OFF[b][n],
                                                      "Total payments": E4_OFF[b][n]})
            wall = 30000 + 1000 * r["global_index"]
            wl.append(f"{i},1000,{1000 + wall},{wall}")
        (bx / "wallclock.csv").write_text("\n".join(wl) + "\n")
    out = root / "out"
    S, df, md = rn.read_noise(extr=str(extr), waves=str(waves), out_dir=str(out))
    return {"root": root, "waves": waves, "extr": extr, "out": out, "S": S, "df": df, "md": md, "rows": rows}


def _row(df, c):
    return df[df["id"] == c].iloc[0]


def test_exact_zero_path(fx):
    S, df = fx["S"], fx["df"]
    assert S["n_exact_pairs"] == 4 and S["n_md5_equal"] == 4 and S["all_exact_zero"]
    for c in ("V1", "E1", "E3", "E4", "R4", "N1", "X1", "E8", "E9", "N5"):
        r = _row(df, c)
        assert r["n_exact_pairs"] == 4 and r["exact_abs_delta_max"] == 0.0 and bool(r["exact_zero"])
        assert r["exact_pooled_sd"] == 0.0 and r["exact_df"] == 4
    js = json.loads((fx["out"] / "ercot_noise.json").read_text())
    assert js["noise_floor"]["all_exact_zero"] is True and js["noise_floor"]["floor"]["E1"] == 0.0
    assert js["exact_zero_finding"] == rn.EXACT_ZERO_FINDING
    assert "budget-cap-only" in fx["md"] and "exact zeros" in fx["md"]


def test_rulers_known_medians(fx):
    df = fx["df"]
    e1 = _row(df, "E1")
    assert e1["n_perturbed"] == 8 and e1["ruler"] == pytest.approx(E1_RULER) and e1["ruler_min"] == pytest.approx(E1_MIN)
    assert e1["ruler_max"] == pytest.approx(E1_MAX) and e1["ruler_status"] == "RULER"
    assert sorted(float(x) for x in e1["perturbed_abs_delta"].split("|")) == pytest.approx(E1_ABS_SORTED)
    assert E1_ABS_SORTED == [50.0, 100.0, 150.0, 200.0, 250.0, 300.0, 350.0, 400.0]
    e3 = _row(df, "E3")
    assert e3["n_perturbed"] == 8 and e3["ruler"] == pytest.approx(10.0) and e3["ruler_min"] == e3["ruler_max"] == pytest.approx(10.0)
    e8 = _row(df, "E8")
    assert e8["ruler"] == pytest.approx(E8_RULER) and e8["ruler_min"] == pytest.approx(E8_MIN) and e8["ruler_max"] == pytest.approx(E8_MAX)
    # E9 / N5 carried from pool_full_metrics (identical on every run): ruler 0
    assert _row(df, "N5")["ruler"] == 0.0 and _row(df, "E9")["ruler"] == 0.0
    # every perturbed copy is read against the exact copy of the SAME batch (A against A, B against B)
    pert = fx["S"]["perturbed"]
    assert list(pert["batch"]) == ["A"] * 4 + ["B"] * 4 and list(pert["design_no"]) == [1, 2, 3, 4] * 2
    for _, r in pert.iterrows():
        assert r["ref_key"].startswith(f"noise_v3/{r['batch']}:")
    assert list(pert["E1"]) == pytest.approx(_pop(E1_OFF))
    for n in range(1, 5):
        p = pert[pert["design_no"] == n]
        assert len(p) == 2 and len(set(p["pem_mw"])) == 2           # the two perturbed copies are distinct


def test_ruler_zero_path(fx):
    S, df = fx["S"], fx["df"]
    r4 = _row(df, "R4")
    assert r4["ruler"] == 0.0 and r4["ruler_status"] == "RULER=0"
    assert "R4" in S["ruler_zero"] and "E1" not in S["ruler_zero"] and "E8" not in S["ruler_zero"]
    assert S["ruler_unavailable"] == []           # every run carries pool_full_metrics.json
    assert "RULER=0` candidates (gradable): " in fx["md"] and "R4" in fx["md"]


def test_sd_df_and_trigger(fx):
    df, S = fx["df"], fx["S"]
    # E1: level = design, sd of {0, delta_A, delta_B} with df 2; pooled over 8 df
    e1 = S["per_candidate"]["E1"]
    sds = [lv["sd"] for lv in e1["levels"]]
    assert sds == pytest.approx(_levels(E1_OFF)) and all(lv["df"] == 2 for lv in e1["levels"])
    exp_sp, exp_df = _pooled(E1_OFF)
    assert e1["pooled_sd"] == pytest.approx(exp_sp) and e1["pooled_df_satterthwaite"] == pytest.approx(exp_df)
    assert exp_sp == pytest.approx(np.sqrt(np.mean([x * x for x in _levels(E1_OFF)])))   # equal df -> mean of variances
    t = e1["trigger"]
    var = [x * x for x in _levels(E1_OFF)]
    exp_ratio = max(var) / min(var)
    assert t["ratio"] == pytest.approx(exp_ratio) and t["df_num"] == 2 and t["df_den"] == 2
    assert exp_ratio == pytest.approx(77500.0 / 15833.3333, rel=1e-5)     # 4.89: > 3 but p = 1 / (1 + 4.89) = 0.17
    assert t["p"] == pytest.approx(1.0 / (1.0 + exp_ratio)) and 0.1 < t["p"] < 0.2 and not t["fires"]
    assert "not detectable at this df" in t["verdict"]
    # E3: equal levels -> ratio 1, Satterthwaite df = 8
    e3 = S["per_candidate"]["E3"]
    assert e3["trigger"]["ratio"] == pytest.approx(1.0) and e3["pooled_df_satterthwaite"] == pytest.approx(8.0)
    assert e3["pooled_sd"] == pytest.approx(np.std([0.0, 10.0, 10.0], ddof=1))
    # E4: level 4 var 833.3 vs level 2 var 0.0833 -> ratio 10000 with df 2/2 -> p = 1 / (1 + 10000) -> fires
    e4 = S["per_candidate"]["E4"]
    assert e4["trigger"]["ratio"] == pytest.approx(10000.0) and e4["trigger"]["p"] == pytest.approx(1.0 / 10001.0, rel=1e-6)
    assert e4["trigger"]["fires"]
    assert bool(_row(df, "E4")["trigger_fires"]) and "TRIGGER" in _row(df, "E4")["trigger_verdict"]
    # R4: all levels sd 0
    assert "exact zeros" in S["per_candidate"]["R4"]["trigger"]["verdict"] and not S["per_candidate"]["R4"]["trigger"]["fires"]
    # CI brackets the point estimate
    lo, hi = e1["pooled_sd_ci95"]
    assert lo < e1["pooled_sd"] < hi
    assert "Family-wise disclosure" in fx["md"]


def test_covariance_matrix(fx):
    cov = pd.read_csv(fx["out"] / "ercot_noise_cov.csv", index_col=0)
    assert cov.shape[0] == cov.shape[1] and {"E1", "E3", "E4", "E8", "R4", "V1"} <= set(cov.index)
    assert cov.loc["E1", "E1"] == pytest.approx(np.var(_pop(E1_OFF), ddof=1))
    assert cov.loc["E1", "E4"] == pytest.approx(np.cov(_pop(E1_OFF), _pop(E4_OFF), ddof=1)[0, 1])
    assert cov.loc["R4", "R4"] == 0.0 and cov.loc["E8", "E8"] == pytest.approx(np.var(_pop(E8_OFF), ddof=1))
    assert cov.loc["E3", "E3"] == 0.0                     # constant +10 on every perturbed run
    assert np.allclose(cov.to_numpy(), cov.to_numpy().T)


def test_shed_assert_and_runtime(fx):
    S = fx["S"]
    assert S["shed_ok"] and f"shed ≡ 0 on all {N_RUNS} runs: **PASS**" in fx["md"]
    rt = S["runtime_table"]
    assert len(rt) == N_RUNS and (rt["core_h"] == rt["wall_s"] / 3600 * 4).all()
    walls = [30000 + 1000 * g for g in range(1, N_RUNS + 1)]
    assert sorted(rt["wall_s"]) == walls
    assert S["runtime"]["core_h_median"] == pytest.approx(np.median(walls) / 3600 * 4)
    assert S["runtime"]["core_h_total"] == pytest.approx(sum(walls) / 3600 * 4)
    assert rn.PLAN_UNKNOWN in fx["md"]
    assert S["identity"]["n_with_identity_line"] == N_RUNS and S["identity"]["ruc_mipgap_values"] == [0.001]


def test_md_identity_lines_and_files(fx):
    md = fx["md"]
    assert md.startswith("# ERCOT_NOISE")
    assert "## 0. Identity (v3)" in md and "GAP_SMOKE.md" in md and "AMENDMENT 2026-11-06b" in md
    assert "ruc_mipgap 0.001, ruc_time_limit 1200 s" in md
    for f in ("ERCOT_NOISE.md", "ercot_noise.csv", "ercot_noise.json", "ercot_noise_cov.csv"):
        assert (fx["out"] / f).is_file()
    df = pd.read_csv(fx["out"] / "ercot_noise.csv")
    assert len(df) == len(rn.po.CAND_IDS) and df["gradable"].sum() == 22
    assert list(df["id"][:22]) == rn.po.load_defs()["global_order"][:22]


def test_exact_pair_differs_path(fx):
    """Edit the B exact copy of design 2: E1 exact pair |delta| = 7, floor > 0, md5 3/4.
    The B perturbed copy of design 2 is read against that edited exact, so its E1 delta shifts by -7."""
    root = fx["root"] / "differs"
    shutil.copytree(fx["extr"], root / "extracts")
    rows_b = [r for r in fx["rows"]["B"] if r["design_no"] == 2 and r["copy_type"] == "exact"]
    assert len(rows_b) == 1
    run = root / "extracts" / "noise_v3" / "B" / f"run_index_{rows_b[0]['index']}"
    _edit_overall(run / "overall.csv", **{"Total costs": 7.0})
    S, df, md = rn.read_noise(extr=str(root / "extracts"), waves=str(fx["waves"]), out_dir=str(root / "out"))
    assert not S["all_exact_zero"] and S["n_md5_equal"] == 3 and S["n_exact_pairs"] == 4
    e1 = S["per_candidate"]["E1"]
    assert not e1["exact_zero"] and e1["exact_abs_delta_max"] == pytest.approx(7.0)
    assert e1["exact_pooled_sd"] == pytest.approx(np.sqrt((49.0 / 2) / 4))
    assert S["per_candidate"]["V1"]["exact_zero"]
    assert "Exact pairs differ on 1 gradable candidates: E1" in md
    pb2 = S["perturbed"][(S["perturbed"]["batch"] == "B") & (S["perturbed"]["design_no"] == 2)]
    assert float(pb2["E1"].iloc[0]) == pytest.approx(E1_OFF["B"][1] - 7.0)
    assert S["per_candidate"]["E1"]["n_perturbed"] == 8
    js = json.loads((root / "out" / "ercot_noise.json").read_text())
    assert js["noise_floor"]["floor"]["E1"] == pytest.approx(np.sqrt((49.0 / 2) / 4)) and js["exact_zero_finding"] is None


def test_shed_failure_is_reported(fx):
    root = fx["root"] / "shed"
    shutil.copytree(fx["extr"], root / "extracts")
    _edit_overall(root / "extracts" / "noise_v3" / "A" / "run_index_1" / "overall.csv", **{"Total load shedding": 5.0})
    S, df, md = rn.read_noise(extr=str(root / "extracts"), waves=str(fx["waves"]), out_dir=str(root / "out"))
    assert not S["shed_ok"] and "FAIL: load shed is not 0" in md and "noise_v3/A:1 = 5" in md
    rc = rn.main(["--extr", str(root / "extracts"), "--waves", str(fx["waves"]), "--out-dir", str(root / "out2")])
    assert rc == 1
    rc = rn.main(["--extr", str(root / "extracts"), "--waves", str(fx["waves"]), "--out-dir", str(root / "out3"), "--no-strict"])
    assert rc == 0


def test_missing_extract_is_listed(fx):
    root = fx["root"] / "missing"
    shutil.copytree(fx["extr"], root / "extracts")
    shutil.rmtree(root / "extracts" / "noise_v3" / "B" / "run_index_3")
    S, df, md = rn.read_noise(extr=str(root / "extracts"), waves=str(fx["waves"]), out_dir=str(root / "out"))
    assert S["missing"] == ["noise_v3/B:3"] and S["n_exact_pairs"] == 3 and "WARNING: 1 extracts missing" in md
    # B:7 (perturbed, design 3) lost its B exact and falls back to the A exact: population stays 8
    assert S["per_candidate"]["E1"]["n_perturbed"] == 8
    pb3 = S["perturbed"][(S["perturbed"]["batch"] == "B") & (S["perturbed"]["design_no"] == 3)]
    assert pb3["ref_key"].iloc[0] == "noise_v3/A:3"


def test_special_functions_against_scipy():
    sp = pytest.importorskip("scipy.stats")
    for k in (1, 2, 3, 4, 7, 10, 25):
        for q in (0.025, 0.5, 0.975):
            assert rn.chi2_ppf(q, k) == pytest.approx(sp.chi2.ppf(q, k), rel=1e-7)
        assert rn.chi2_cdf(3.3, k) == pytest.approx(sp.chi2.cdf(3.3, k), rel=1e-9)
    for x, d1, d2 in ((16.0, 1, 1), (2500.0, 1, 1), (3.0, 2, 2), (9.3, 3, 3), (1.5, 4, 6), (0.2, 5, 2)):
        assert rn.f_sf(x, d1, d2) == pytest.approx(sp.f.sf(x, d1, d2), rel=1e-7, abs=1e-12)
    lo, hi = rn.sd_ci(2.0, 3)
    assert lo == pytest.approx(2.0 * np.sqrt(3 / sp.chi2.ppf(0.975, 3)), rel=1e-7)
    assert hi == pytest.approx(2.0 * np.sqrt(3 / sp.chi2.ppf(0.025, 3)), rel=1e-7)
    # the precision-budget numbers of prompt 52 section 3: ~[0.57, 3.7] x at 3 df; F(3,3) rejects at ~9.3
    assert lo / 2.0 == pytest.approx(0.566, abs=0.01) and hi / 2.0 == pytest.approx(3.73, abs=0.02)
    assert rn.f_sf(9.28, 3, 3) == pytest.approx(0.05, abs=0.002)


def test_pooled_and_level_helpers():
    assert rn.level_sd([]) == (np.nan, 0) or np.isnan(rn.level_sd([])[0])
    s, nu = rn.level_sd([3.0])
    assert s == pytest.approx(3.0 / np.sqrt(2)) and nu == 1
    sp, df = rn.pooled_sd([(1.0, 2), (1.0, 2)])
    assert sp == pytest.approx(1.0) and df == pytest.approx(4.0)
    sp, df = rn.pooled_sd([(0.0, 1), (0.0, 1)])
    assert sp == 0.0 and df == 2
    t = rn.trigger([(0.0, 1), (2.0, 1)])
    assert t["fires"] and t["ratio"] == float("inf")
    t = rn.trigger([(1.0, 1)])
    assert not t["fires"] and t["n_levels"] == 1


# --------------------------------------------------------------------------
# Part B step 0 (contract 6.3): exact-delta covariance, SUSPECT / S3b, plan 1.2 verdict
# --------------------------------------------------------------------------
def _s1_repaired(fx, name):
    """A copy of the fixture extracts whose perturbed rows satisfy the plan 1.2 S1 identity
    (the base fixture edits Total costs alone, which breaks |total - fixed - var| <= $1 and
    correctly makes those 8 rows SUSPECT): fixed += E1_OFF - E3_OFF per perturbed row."""
    root = fx["root"] / name
    shutil.copytree(fx["extr"], root / "extracts")
    for b in mn.BATCHES:
        for r in fx["rows"][b]:
            if r["copy_type"] == "perturbed":
                n = r["design_no"] - 1
                _edit_overall(root / "extracts" / "noise_v3" / b / f"run_index_{r['index']}" / "overall.csv",
                              **{"Total fixed costs": E1_OFF[b][n] - E3_OFF[b][n]})
    return root


def test_exact_cov_file_all_zero_and_shape(fx):
    exc = pd.read_csv(fx["out"] / "ercot_noise_exact_cov.csv", index_col=0)
    S = fx["S"]
    gradable = [c for c in exc.index]
    assert exc.shape[0] == exc.shape[1] == len(gradable) and "V1" in gradable and "E1" in gradable
    assert np.all(exc.to_numpy() == 0.0)                      # exact zeros, not NaN
    assert np.all(S["exact_cov"].to_numpy() == 0.0)
    js = json.loads((fx["out"] / "ercot_noise.json").read_text())
    assert js["exact_covariance"]["all_zero"] and js["exact_covariance"]["n_pairs"] == 4 and js["exact_covariance"]["ddof"] == 1
    assert "rider ONLY" in js["covariance"]["population"] and "tau" in js["exact_covariance"]["population"]
    assert "## 5b." in fx["md"] and "Identically zero" in fx["md"]
    # the perturbed covariance is NOT zero (E1 offsets) -> the two files differ
    cov = pd.read_csv(fx["out"] / "ercot_noise_cov.csv", index_col=0)
    assert float(cov.loc["E1", "E1"]) > 0.0


def test_s1_breaks_on_total_cost_only_edits(fx):
    """The base fixture's perturbed rows edit Total costs without fixed/var: S1 fails by
    exactly the offset difference, the 8 rows are SUSPECT, R1 fails, verdict NOT READABLE."""
    S = fx["S"]
    sus = [r for r in S["suspect_runs"] if r["suspect"]]
    assert len(sus) == 8 and all(r["copy_type"] == "perturbed" and not r["S1_ok"] and r["S2_ok"] for r in sus)
    assert all(r["S1_resid_usd"] == pytest.approx(abs(E1_OFF[r["key"].split("/")[1][0]][r["design_no"] - 1]
                                                       - E3_OFF[r["key"].split("/")[1][0]][r["design_no"] - 1])) for r in sus)
    rv = S["readability"]
    assert not rv["readable"] and not rv["R1"]["ok"] and rv["R2"]["ok"] and rv["R3"]["ok"] and len(rv["R1"]["suspect_keys"]) == 8
    assert "NOT READABLE" in fx["md"] and "**SUSPECT**" in fx["md"]


def test_exact_cov_nonzero_on_the_differs_fixture(fx):
    root = _s1_repaired(fx, "excov")
    rb = [r for r in fx["rows"]["B"] if r["design_no"] == 2 and r["copy_type"] == "exact"][0]
    _edit_overall(root / "extracts" / "noise_v3" / "B" / f"run_index_{rb['index']}" / "overall.csv",
                  **{"Total costs": 7.0, "Total generation costs": 7.0})           # keeps S1
    S, df, md = rn.read_noise(extr=str(root / "extracts"), waves=str(fx["waves"]), out_dir=str(root / "out"))
    exc = S["exact_cov"]
    assert float(exc.loc["E1", "E1"]) == pytest.approx(np.var([0.0, 7.0, 0.0, 0.0], ddof=1))   # 12.25
    assert float(exc.loc["E3", "E1"]) == pytest.approx(12.25) and float(exc.loc["V1", "V1"]) == 0.0 and float(exc.loc["E1", "V1"]) == 0.0
    assert "Not identically zero" in md
    # still READABLE: $7 is far inside the $1.13M bar, no SUSPECT
    assert S["readability"]["readable"] and S["readability"]["cost_objective"] == "E1"
    assert S["readability"]["R2"]["max_abs_delta_total_usd"] == pytest.approx(7.0)


def test_suspect_s3b_and_verdict_readable(fx):
    root = _s1_repaired(fx, "readable")
    S, df, md = rn.read_noise(extr=str(root / "extracts"), waves=str(fx["waves"]), out_dir=str(root / "out"))
    runs, pairs = S["suspect_runs"], S["suspect_pairs"]
    assert len(runs) == N_RUNS and not any(r["suspect"] for r in runs)
    assert all(r["S1_ok"] and r["S2_ok"] for r in runs)
    assert all(r["S3a_ok"] for r in runs if r["S3a_applicable"]) and sum(1 for r in runs if r["nuclear"]) == 4
    assert len(pairs) == 4 and all(p["S3b_ok"] for p in pairs)
    rv = S["readability"]
    assert rv["readable"] and rv["cost_objective"] == "E1"
    assert rv["R1"]["ok"] and rv["R2"]["ok"] and rv["R3"]["ok"]
    assert rv["R2"]["threshold_usd"] == pytest.approx(0.1 * 11320880.71398735) and rv["R3"]["threshold_usd"] == pytest.approx(0.1 * 13250818.77065301)
    assert rv["R2"]["max_abs_delta_total_usd"] == 0.0 and rv["R2"]["n_pairs"] == 4
    assert "READABLE -> the campaign cost objective is total_cost (E1)" in md and "## 5c." in md
    js = json.loads((root / "out" / "ercot_noise.json").read_text())
    assert js["readability"]["readable"] and js["suspect"]["n_suspect"] == 0
    # the perturbed-population rulers are unchanged by the S1 repair (fixed cost is not E1 / E3)
    assert S["per_candidate"]["E1"]["ruler"] == pytest.approx(E1_RULER)


def test_verdict_not_readable_on_R2_and_s3b_failure(fx):
    root = _s1_repaired(fx, "notread")
    rb = [r for r in fx["rows"]["B"] if r["design_no"] == 1 and r["copy_type"] == "exact"][0]
    run = root / "extracts" / "noise_v3" / "B" / f"run_index_{rb['index']}"
    _edit_overall(run / "overall.csv", **{"Total costs": 2.0e6, "Total generation costs": 2.0e6})   # > $1.13M -> R2 fails, S1 kept
    S, df, md = rn.read_noise(extr=str(root / "extracts"), waves=str(fx["waves"]), out_dir=str(root / "out"))
    rv = S["readability"]
    assert not rv["readable"] and rv["cost_objective"] == "E3" and not rv["R2"]["ok"] and rv["R3"]["ok"] and rv["R1"]["ok"]
    assert rv["R2"]["max_abs_delta_total_usd"] == pytest.approx(2.0e6)
    assert "NOT READABLE -> the campaign cost objective is var_cost (E3" in md
    # S3b: nuclear unit 1 starts differ across the exact pair of design 3 (non-nuclear) -> S3a + S3b fail, SUSPECT
    root2 = _s1_repaired(fx, "s3b")
    rb3 = [r for r in fx["rows"]["B"] if r["design_no"] == 3 and r["copy_type"] == "exact"][0]
    gs = root2 / "extracts" / "noise_v3" / "B" / f"run_index_{rb3['index']}" / "gen_summary.csv"
    g = pd.read_csv(gs, dtype={"Generator": str})
    assert (g["Generator"] == "1").sum() == 1
    g.loc[g["Generator"] == "1", "starts"] = 1.0
    g.to_csv(gs, index=False)
    S2, df2, md2 = rn.read_noise(extr=str(root2 / "extracts"), waves=str(fx["waves"]), out_dir=str(root2 / "out"))
    bad = [p for p in S2["suspect_pairs"] if not p["S3b_ok"]]
    assert [p["design_no"] for p in bad] == [3] and bad[0]["gen1_starts"] == [0.0, 1.0]
    sus = [r for r in S2["suspect_runs"] if r["suspect"]]
    assert [r["key"] for r in sus] == [f"noise_v3/B:{rb3['index']}"] and not sus[0]["S3a_ok"]
    assert not S2["readability"]["readable"] and not S2["readability"]["R1"]["ok"]
    assert S2["readability"]["R1"]["S3b_failed_designs"] == [3] and "| D3 |" in md2 and "FAIL |" in md2


# --------------------------------------------------------------------------
# Prompt 63 A1: structural-zero perturbed pairs (memo F6) leave the ruler, the
# levels, the trigger and the 61 bar B_j
# --------------------------------------------------------------------------
def _bar(d):
    d = np.asarray(d, float)
    s = float(np.sqrt(np.mean(d ** 2)))
    return s, max(3.0 * s, float(np.abs(d).max()))


def test_no_structural_zero_on_the_base_fixture(fx):
    S = fx["S"]
    assert S["structural_zero_keys"] == [] and len(S["structural_zero"]) == 8
    assert not S["structural_zero"]["structural_zero"].any()
    e1 = S["per_candidate"]["E1"]
    s, B = _bar(_pop(E1_OFF))
    assert e1["bar"]["sigma_hat"] == pytest.approx(s) and e1["bar"]["B"] == pytest.approx(B) and e1["bar"]["n"] == 8
    assert e1["with_structural_zeros"]["bar"] == e1["bar"] and e1["with_structural_zeros"]["ruler"] == e1["ruler"]
    assert e1["perturbed_delta_signed"] == e1["perturbed_delta_signed_all"]
    assert "## 10. 2026-11-17" in fx["md"] and "Excluded: none" in fx["md"]


def test_structural_zero_pairs_excluded(fx):
    """Design 2's perturbed copies get the exact copy's overall.csv + pool metrics (identical model
    output at a different design MW = the D2 / site 206 artefact): both are EXCLUDED and listed;
    ruler / levels / trigger / B_j use the 6 remaining copies; the old values are kept beside them."""
    root = fx["root"] / "structural"
    shutil.copytree(fx["extr"], root / "extracts")
    d2 = {}
    for b in mn.BATCHES:
        ex = [r for r in fx["rows"][b] if r["design_no"] == 2 and r["copy_type"] == "exact"][0]
        pt = [r for r in fx["rows"][b] if r["design_no"] == 2 and r["copy_type"] == "perturbed"][0]
        src = root / "extracts" / "noise_v3" / b / f"run_index_{ex['index']}"
        dst = root / "extracts" / "noise_v3" / b / f"run_index_{pt['index']}"
        for f in ("overall.csv", "pool_full_metrics.json"):
            shutil.copyfile(src / f, dst / f)
        d2[b] = f"noise_v3/{b}:{pt['index']}"
    S, df, md = rn.read_noise(extr=str(root / "extracts"), waves=str(fx["waves"]), out_dir=str(root / "out"))
    assert S["structural_zero_keys"] == [d2["A"], d2["B"]]
    sz = S["structural_zero"].set_index("key")
    assert sz.loc[d2["A"], "overall_md5_equal"] and sz.loc[d2["A"], "pem_mw"] != sz.loc[d2["A"], "pem_mw_ref"]
    if sz.loc[d2["A"], "site_max_availability_mw"] is not None:        # real v2 data dir: site 206 max wind 895.48 MW
        assert bool(sz.loc[d2["A"], "capped_input_identical"]) and bool(sz.loc[d2["B"], "evidence_consistent"])
    e1 = S["per_candidate"]["E1"]
    eff = [E1_OFF[b][n] for b in ("A", "B") for n in (0, 2, 3)]          # designs 1, 3, 4
    old = [0.0 if n == 1 else E1_OFF[b][n] for b in ("A", "B") for n in range(4)]
    assert e1["n_perturbed"] == 6 and sorted(e1["perturbed_delta_signed"]) == pytest.approx(sorted(eff))
    assert len(e1["perturbed_delta_signed_all"]) == 8 and e1["with_structural_zeros"]["n_perturbed"] == 8
    assert e1["ruler"] == pytest.approx(np.median(np.abs(eff))) == pytest.approx(175.0)
    assert e1["with_structural_zeros"]["ruler"] == pytest.approx(np.median(np.abs(old))) == pytest.approx(125.0)
    s, B = _bar(eff)
    so, Bo = _bar(old)
    assert e1["bar"]["sigma_hat"] == pytest.approx(s) and e1["bar"]["B"] == pytest.approx(B) and e1["bar"]["n"] == 6
    assert e1["with_structural_zeros"]["bar"]["B"] == pytest.approx(Bo) and s == pytest.approx(so * np.sqrt(8 / 6))
    # levels: design 2 is gone; the trigger runs over designs 1, 3, 4 only
    assert [lv["design_no"] for lv in e1["levels"]] == [1, 3, 4]
    assert [lv["design_no"] for lv in e1["with_structural_zeros"]["levels"]] == [1, 2, 3, 4]
    assert e1["trigger"]["n_levels"] == 3
    exp = [float(np.std([0.0, E1_OFF["A"][n], E1_OFF["B"][n]], ddof=1)) for n in (0, 2, 3)]
    assert [lv["sd"] for lv in e1["levels"]] == pytest.approx(exp)
    assert e1["trigger"]["ratio"] == pytest.approx(max(exp) ** 2 / min(exp) ** 2)
    # R4 is untouched on every copy: still all-zero (not a structural zero: its overall.csv differs)
    assert S["per_candidate"]["R4"]["ruler_status"] == "RULER=0"
    # outputs: md section 10 lists both, json carries the rule and the excluded keys
    assert "## 10. 2026-11-17" in md and f"Excluded: {d2['A']}, {d2['B']}" in md and "**no — STRUCTURAL ZERO**" in md
    js = json.loads((root / "out" / "ercot_noise.json").read_text())
    assert js["structural_zero"]["keys_excluded"] == [d2["A"], d2["B"]]
    assert len(js["per_candidate"]["E1"]["perturbed_delta_signed"]) == 6
    assert js["per_candidate"]["E1"]["bar"]["B"] == pytest.approx(B)
    # the rider covariance keeps every perturbed row (unchanged file by design)
    cov = pd.read_csv(root / "out" / "ercot_noise_cov.csv", index_col=0)
    assert float(cov.loc["E1", "E1"]) == pytest.approx(np.var(old, ddof=1))


def test_bar_B_helper():
    b = rn.bar_B([3.0, -4.0, np.nan])
    assert b["n"] == 2 and b["sigma_hat"] == pytest.approx(np.sqrt(12.5)) and b["B"] == pytest.approx(3 * np.sqrt(12.5))
    b = rn.bar_B([10.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])      # one heavy value: max term binds
    assert b["B"] == pytest.approx(10.0) and 3 * b["sigma_hat"] < 10.0
    assert rn.bar_B([])["n"] == 0


# --------------------------------------------------------------------------
# Prompt 63 A2: per-day RUC divergence table (memo F2)
# --------------------------------------------------------------------------
def test_daily_divergence_identical_tables(fx):
    """Every fixture run copies the same ruc_quality.csv: 0 divergent days on all 12 pairs."""
    dv = fx["S"]["daily_divergence"]
    assert len(dv) == 8 + 4 and set(dv["pair_type"]) == {"perturbed", "exact"}
    assert (dv["n_divergent"] == 0).all() and (dv["median_rel_all_days"] == 0.0).all()
    assert dv["first_divergent_day_no"].isna().all()
    assert (fx["out"] / "ercot_noise_daily_divergence.csv").is_file() and "## 11. 2026-11-17" in fx["md"]


def test_daily_divergence_counts_and_first_day(fx):
    root = fx["root"] / "divergence"
    shutil.copytree(fx["extr"], root / "extracts")
    pt = [r for r in fx["rows"]["A"] if r["design_no"] == 1 and r["copy_type"] == "perturbed"][0]
    p = root / "extracts" / "noise_v3" / "A" / f"run_index_{pt['index']}" / "ruc_quality.csv"
    q = pd.read_csv(p)
    n = len(q)
    base = q["ruc_cost"].to_numpy(float).copy()
    q.loc[2, "ruc_cost"] = base[2] * (1 + 2e-3)          # day 3: above the gap
    q.loc[5, "ruc_cost"] = base[5] * (1 - 1e-4)          # day 6: inside the gap
    q.to_csv(p, index=False)
    S, df, md = rn.read_noise(extr=str(root / "extracts"), waves=str(fx["waves"]), out_dir=str(root / "out"))
    dv = S["daily_divergence"]
    r = dv[dv["key"] == f"noise_v3/A:{pt['index']}"].iloc[0]
    assert r["n_days"] == n and r["n_divergent"] == 2 and r["n_rel_gt_1e-3"] == 1
    assert r["first_divergent_day_no"] == 3 and r["first_divergent_date"] == str(q.loc[2, "ruc_date"])
    assert r["max_rel"] == pytest.approx(2e-3, rel=1e-6) and r["median_rel_all_days"] == 0.0
    assert r["median_rel_divergent_days"] == pytest.approx(np.median([2e-3, 1e-4]), rel=1e-6)
    assert (dv[dv["key"] != r["key"]]["n_divergent"] == 0).all()
    # day 1 is labelled 'start_date' by the collector and reported as the calendar date
    c = rn._ruc_cost(str(p.parent))
    assert c.index[0] == (pd.Timestamp(c.index[1]) - pd.Timedelta(days=1)).strftime("%Y-%m-%d")
