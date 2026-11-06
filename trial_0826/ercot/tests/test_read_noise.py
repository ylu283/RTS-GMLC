"""Prompt 52 v2.1 tests for analysis/noise_v3/read_noise.py.

Run:  cd trial_0826/ercot && python -m pytest tests/test_read_noise.py -q

Fixture: the 12 noise_v3 rows synthesized by copying the SLIM tables of
extracts/base_2019_v2/run_index_1 (the --full reference) with tiny controlled
edits to overall.csv and a synthetic pool_full_metrics.json (E8/E9/N5, as the
CRC collector writes it), so every expected median is known. Paths tested:
exact-zero (all exact pairs identical), RULER=0 (R4 untouched), a firing and
a non-firing trigger, the exact-pair-differs path, the shed assert, the
runtime table, and the chi-square / F quantiles against scipy.
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

# controlled edits on the 4 perturbed rows (design 1..4), all in batch A rows 5..8
E1_OFF = [100.0, -300.0, 200.0, 400.0]        # Total costs      -> ruler 250, ratio 16 (no fire)
E3_OFF = [10.0, 10.0, 10.0, 10.0]             # Total generation costs -> ruler 10, ratio 1
E4_OFF = [1.0, 0.5, 0.7, 50.0]                # Total payments   -> ratio 2500 -> fires (df 1/1)
E8_OFF = [0.5, -0.1, 0.2, 0.3]                # pool_full_metrics E8 -> ruler 0.25
E8_BASE, E9_BASE, N5_BASE = 15.0, 0, -18.4


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
        for r in rows[b]:
            i = r["index"]
            run = bx / f"run_index_{i}"
            e8 = E8_BASE
            if r["copy_type"] == "perturbed":
                e8 = E8_BASE + E8_OFF[r["design_no"] - 1]
            _make_run(run, e8=e8)
            if r["copy_type"] == "perturbed":
                n = r["design_no"] - 1
                _edit_overall(run / "overall.csv", **{"Total costs": E1_OFF[n],
                                                      "Total generation costs": E3_OFF[n],
                                                      "Total payments": E4_OFF[n]})
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
    assert e1["n_perturbed"] == 4 and e1["ruler"] == pytest.approx(250.0) and e1["ruler_min"] == pytest.approx(100.0)
    assert e1["ruler_max"] == pytest.approx(400.0) and e1["ruler_status"] == "RULER"
    assert sorted(float(x) for x in e1["perturbed_abs_delta"].split("|")) == pytest.approx([100.0, 200.0, 300.0, 400.0])
    e3 = _row(df, "E3")
    assert e3["ruler"] == pytest.approx(10.0) and e3["ruler_min"] == e3["ruler_max"] == pytest.approx(10.0)
    e8 = _row(df, "E8")
    assert e8["ruler"] == pytest.approx(0.25) and e8["ruler_min"] == pytest.approx(0.1) and e8["ruler_max"] == pytest.approx(0.5)
    # E9 / N5 carried from pool_full_metrics (identical on every run): ruler 0
    assert _row(df, "N5")["ruler"] == 0.0 and _row(df, "E9")["ruler"] == 0.0
    # exact pairs compare perturbed to the exact copy of the SAME batch
    pert = fx["S"]["perturbed"]
    assert (pert["batch"] == "A").all() and (pert["ref_key"].str.startswith("noise_v3/A:")).all()
    assert list(pert["design_no"]) == [1, 2, 3, 4]


def test_ruler_zero_path(fx):
    S, df = fx["S"], fx["df"]
    r4 = _row(df, "R4")
    assert r4["ruler"] == 0.0 and r4["ruler_status"] == "RULER=0"
    assert "R4" in S["ruler_zero"] and "E1" not in S["ruler_zero"] and "E8" not in S["ruler_zero"]
    assert S["ruler_unavailable"] == []           # every run carries pool_full_metrics.json
    assert "RULER=0` candidates (gradable): " in fx["md"] and "R4" in fx["md"]


def test_sd_df_and_trigger(fx):
    df, S = fx["df"], fx["S"]
    # E1: levels sd = |d| / sqrt(2), df 1 each; pooled = sqrt(sum d^2 / 2 / 4)
    e1 = S["per_candidate"]["E1"]
    sds = [lv["sd"] for lv in e1["levels"]]
    assert sds == pytest.approx([abs(x) / np.sqrt(2) for x in E1_OFF]) and all(lv["df"] == 1 for lv in e1["levels"])
    assert e1["pooled_sd"] == pytest.approx(np.sqrt(sum(x * x for x in E1_OFF) / 2 / 4))
    num = sum(x * x / 2 for x in E1_OFF)
    assert e1["pooled_df_satterthwaite"] == pytest.approx(num * num / sum((x * x / 2) ** 2 for x in E1_OFF))
    t = e1["trigger"]
    assert t["ratio"] == pytest.approx(16.0) and t["df_num"] == 1 and t["df_den"] == 1
    assert t["p"] == pytest.approx(rn.f_sf(16.0, 1, 1)) and 0.1 < t["p"] < 0.2 and not t["fires"]
    assert "not detectable at this df" in t["verdict"]
    # E3: equal levels -> ratio 1, Satterthwaite df = 4
    e3 = S["per_candidate"]["E3"]
    assert e3["trigger"]["ratio"] == pytest.approx(1.0) and e3["pooled_df_satterthwaite"] == pytest.approx(4.0)
    # E4: ratio (50 / 0.5)^2 = 10000 with df 1/1 -> p ~ 0.006 -> fires
    e4 = S["per_candidate"]["E4"]
    assert e4["trigger"]["ratio"] == pytest.approx(10000.0) and e4["trigger"]["p"] < 0.05 and e4["trigger"]["fires"]
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
    assert cov.loc["E1", "E1"] == pytest.approx(np.var(E1_OFF, ddof=1))
    assert cov.loc["E1", "E4"] == pytest.approx(np.cov(E1_OFF, E4_OFF, ddof=1)[0, 1])
    assert cov.loc["R4", "R4"] == 0.0 and cov.loc["E8", "E8"] == pytest.approx(np.var(E8_OFF, ddof=1))
    assert np.allclose(cov.to_numpy(), cov.to_numpy().T)


def test_shed_assert_and_runtime(fx):
    S = fx["S"]
    assert S["shed_ok"] and "shed ≡ 0 on all 12 runs: **PASS**" in fx["md"]
    rt = S["runtime_table"]
    assert len(rt) == 12 and (rt["core_h"] == rt["wall_s"] / 3600 * 4).all()
    walls = [30000 + 1000 * g for g in range(1, 13)]
    assert sorted(rt["wall_s"]) == walls
    assert S["runtime"]["core_h_median"] == pytest.approx(np.median(walls) / 3600 * 4)
    assert S["runtime"]["core_h_total"] == pytest.approx(sum(walls) / 3600 * 4)
    assert rn.PLAN_UNKNOWN in fx["md"]
    assert S["identity"]["n_with_identity_line"] == 12 and S["identity"]["ruc_mipgap_values"] == [0.001]


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
    """Edit the B exact copy of design 2: E1 exact pair |delta| = 7, floor > 0, md5 3/4."""
    root = fx["root"] / "differs"
    shutil.copytree(fx["extr"], root / "extracts")
    rows_b = [r for r in fx["rows"]["B"] if r["design_no"] == 2]
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
    assert S["per_candidate"]["E1"]["n_perturbed"] == 4


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
