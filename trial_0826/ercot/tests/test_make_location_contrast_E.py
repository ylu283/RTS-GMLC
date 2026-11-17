"""Prompt 61 v1.1 tests for tools/make_location_contrast_E.py (waves/location_contrast_E).

Run:  cd trial_0826/ercot && /opt/anaconda3/bin/python -m pytest \
          tests/test_make_location_contrast_E.py tests/test_make_ercot_n0.py -q

Checks: 9 rows in the pinned order; P1 rows at 60 / 120 / 180 MW on every
site; P2/P3 group sums = T, off-group sites exactly 0, mw <= gen_pmax, the
matched-u pair; pem_mw == pool_objectives.pem_mw(); retrofit dicts; the
scripts (bash -n, SGE flags, GAP_DECISION refusal, no "Sobol" / "holdout");
H_C (4,410 hours, per-site sums, the predicted 800-MW ratio); 53's module
globals untouched; committed wave == fresh build. Running together with
tests/test_make_ercot_n0.py guards the runtime WAVES_E key.
"""
import json
import math
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ERCOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ERCOT / "tools"))
sys.path.insert(0, str(ERCOT))
import make_ercot_n0 as mk  # noqa: E402
import make_location_contrast_E as lc  # noqa: E402
import pool_objectives as po  # noqa: E402

WAVES = ERCOT / "waves"
W = lc.WAVE
LABELS = ["P1_60", "P1_120", "P1_180", "P2_800_b120", "P2_800_b275", "P2_800_all",
          "P2_500_270", "P2_500_110_140", "P3_1500_all"]
GROUPS = {"P2_800_b120": (800.0, {"163", "270", "274"}),
          "P2_800_b275": (800.0, {"110", "140", "146"}),
          "P2_800_all": (800.0, set(lc.ALL6)),
          "P2_500_270": (500.0, {"270"}),
          "P2_500_110_140": (500.0, {"110", "140"}),
          "P3_1500_all": (1500.0, set(lc.ALL6))}
# prompt 61 section 2.2 table (rounded to 0.01)
TABLE = {"P2_800_b120": [0, 0, 0, 98.17, 306.59, 395.23],
         "P2_800_b275": [316.01, 233.88, 250.12, 0, 0, 0],
         "P2_800_all": [114.39, 84.66, 90.54, 62.64, 195.61, 252.16],
         "P2_500_270": [0, 0, 0, 0, 500, 0],
         "P2_500_110_140": [287.34, 212.66, 0, 0, 0, 0],
         "P3_1500_all": [214.48, 158.74, 169.76, 117.44, 366.77, 472.80]}
PINNED_PHRASE = "never in GP X / HV / holdout / baseline"


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    globals_before = (mk.PROMPT, mk.DESIGN_SPACE, mk.CONTRACT_VERSION)
    waves = tmp_path_factory.mktemp("waves")
    rows, hc, space = lc.build(waves=waves)
    assert (mk.PROMPT, mk.DESIGN_SPACE, mk.CONTRACT_VERSION) == globals_before
    return waves, rows, hc, space


def _dm(path):
    return pd.read_csv(path, dtype={"oat_site": str, "tier": str, "level_id": str},
                       float_precision="round_trip")


def test_rows_in_pinned_order(built):
    waves, _, _, space = built
    dm = _dm(waves / W / "design_matrix.csv")
    assert len(dm) == 9 and list(dm["index"]) == list(range(1, 10))
    assert list(dm["level_id"]) == LABELS
    assert set(dm["tier"]) == {"contrast"} and dm["sobol_index"].isna().all()
    assert (dm["oat_site"] == "__ALL__").all() and (dm["bid"] == 40.0).all()
    assert (dm["start_date"] == "01-01-2019").all() and (dm["num_days"] == 365).all()
    for c in ("unit_type", "bus", "omega", "gen_pmax", "replicate_of"):
        assert dm[c].isna().all(), c
    assert list(dm.columns) == mk.columns(space)


def test_p1_rows_exact(built):
    waves, _, _, space = built
    dm = _dm(waves / W / "design_matrix.csv").set_index("level_id")
    for lab, m in (("P1_60", 60.0), ("P1_120", 120.0), ("P1_180", 180.0)):
        for j, s in enumerate(space["sites"]):
            assert abs(dm.loc[lab, f"mw_{s}"] - m) <= 1e-9
            assert abs(dm.loc[lab, f"u_{s}"] - m / space["pmax"][j]) <= 1e-12
        assert abs(dm.loc[lab, "pem_mw"] - 6 * m) <= 1e-9


def test_prorata_rows(built):
    waves, _, _, space = built
    dm = _dm(waves / W / "design_matrix.csv").set_index("level_id")
    for lab, (T, grp) in GROUPS.items():
        mw = np.array([dm.loc[lab, f"mw_{s}"] for s in space["sites"]])
        assert abs(math.fsum(mw) - T) <= 1e-6, lab
        assert (mw <= space["pmax"]).all(), lab
        for j, s in enumerate(space["sites"]):
            if s not in grp:
                assert dm.loc[lab, f"mw_{s}"] == 0.0 and dm.loc[lab, f"u_{s}"] == 0.0, (lab, s)
            else:
                assert dm.loc[lab, f"mw_{s}"] > 0.0
        u = {dm.loc[lab, f"u_{s}"] for s in grp}
        assert max(u) - min(u) <= 1e-12, lab                    # one u on the group
        assert np.round(mw, 2).tolist() == pytest.approx(TABLE[lab], abs=1e-9), lab
    u7 = dm.loc["P2_500_270", "u_270"]
    u8 = dm.loc["P2_500_110_140", "u_110"]
    assert abs(u7 - u8) <= 0.02                                  # the matched-u pair
    assert round(u7, 3) == 0.864 and round(u8, 3) == 0.849


def test_pem_mw_matches_pool_objectives(built):
    waves, rows, _, _ = built
    dm = _dm(waves / W / "design_matrix.csv")
    for r in rows:
        drow = po.design_row(W, r["index"], waves=str(waves))
        assert drow["site"] == "__ALL__"
        v = po.pem_mw(W, r["index"], drow, waves=str(waves))
        assert abs(v - dm.loc[dm["index"] == r["index"], "pem_mw"].iloc[0]) <= 1e-9


def test_retrofit_dicts(built):
    waves, rows, _, space = built
    for r in rows:
        d = json.loads((waves / W / f"retrofit_gen_dict_{r['index']}.json").read_text())
        assert sorted(d) == sorted(s for s in space["sites"] if r[f"mw_{s}"] > 0)
        for j, s in enumerate(space["sites"]):
            if s in d:
                assert d[s] == {"PEM_bid": 40.0, "PEM_fraction": r[f"u_{s}"],
                                "gen_pmax": float(space["pmax"][j])}
    assert sorted(json.loads((waves / W / "retrofit_gen_dict_7.json").read_text())) == ["270"]


def _bash_n(p):
    r = subprocess.run(["bash", "-n", str(p)], capture_output=True, text=True)
    assert r.returncode == 0, (p, r.stderr)


def test_scripts(built):
    waves, _, _, _ = built
    names = (f"{W}_array.sh", f"collect_{W}.sh", "submit_this.sh")
    for f in names:
        _bash_n(waves / W / f)
        t = (waves / W / f).read_text()
        assert "Sobol" not in t, f
        assert "holdout" not in t.replace(PINNED_PHRASE, ""), f
        assert "Prompt 61 v1.1" in t and "Prompt 53" not in t, f
    arr = (waves / W / names[0]).read_text()
    assert "#$ -t 1-9" in arr and "#$ -pe smp 4" in arr and "#$ -r n" in arr and "#$ -q long" in arr
    assert "-tc" not in arr and "default_rng" not in arr
    assert "analysis-only location contrast (prompt 61;" in arr
    assert "LOC_CONTRAST_E_START" in arr and "LOC_CONTRAST_E_END" in arr
    coll = (waves / W / names[1]).read_text()
    assert "--full" in coll and f'extracts/{W}"' in coll and '"$EXTR/COLLECTED"' in coll
    assert "LOC_CONTRAST_E_START" in coll and "identity.txt" in coll
    sub = (waves / W / names[2]).read_text()
    assert "Analysis-only; no dependency on n0_E / random_E / methods_E." in sub
    assert f"qsub -terse {W}_array.sh" in sub and "read -r -p" in sub and '"$ANS" == "yes"' in sub
    assert f"extracts/{W}/" in sub and "retrofit_gen_dict_9.json" in sub


def test_array_refuses_without_gap_decision(built, tmp_path):
    waves, _, _, _ = built
    arr = (waves / W / f"{W}_array.sh").read_text()
    block = arr[arr.index("# --- identity from waves/GAP_DECISION.json"):arr.index('eval "$(python')]
    ercot = tmp_path / "ercot"
    (ercot / "waves").mkdir(parents=True)
    wave = tmp_path / "wave"
    wave.mkdir()
    script = (f'set -euo pipefail\nERCOT_DIR="{ercot}"\nWAVE_DIR="{wave}"\nSGE_TASK_ID=7\n'
              + block + 'echo "REACHED_RUN"\n')
    r = subprocess.run(["bash", "-c", script], capture_output=True, text=True)
    assert r.returncode != 0 and "ABORT task 7" in r.stdout and "REACHED_RUN" not in r.stdout
    assert (wave / "FAILED_task_7_no_gap_decision.md").is_file()
    (ercot / "waves" / "GAP_DECISION.json").write_text(json.dumps({"ruc_mipgap": 0.001, "ruc_time_limit": 1200}))
    r = subprocess.run(["bash", "-c", script + 'echo "GAP=$RUC_MIPGAP TL=$RUC_TIME_LIMIT"\n'],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "REACHED_RUN" in r.stdout and "GAP=0.001 TL=1200.0" in r.stdout


def test_h_c(built):
    waves, rows, hc, space = built
    t = pd.read_csv(waves / W / "H_C.csv", dtype={"level_id": str}, float_precision="round_trip")
    assert list(t["level_id"]) == LABELS and (t["n_hours_C"] == 4410).all()
    per = t[[f"H_C_{s}" for s in space["sites"]]].to_numpy()
    assert np.abs(per.sum(axis=1) - t["H_C_MWh"].to_numpy()).max() <= 1e-6
    for r, (_, h) in zip(rows, t.iterrows()):
        for s in space["sites"]:
            assert (h[f"H_C_{s}"] == 0.0) == (r[f"mw_{s}"] == 0.0)
            assert h[f"H_C_{s}"] <= 4410 * r[f"mw_{s}"] + 1e-6
    # independent recompute of one row from the raw files
    ren = pd.read_csv(lc.BASE_RENEW)
    c = ren[(ren["unit_type"] == "WIND") & (~ren["is_pem"]) & (ren["Curtailment"] > 1.0)]
    wind = pd.read_csv(lc.WIND_RT)
    wind = wind[wind["Year"] == 2019].reset_index(drop=True)
    wind["key"] = (wind["Year"].astype(str) + "-" + wind["Month"].map("{:02d}".format) + "-"
                   + wind["Day"].map("{:02d}".format) + "/" + wind["Period"].astype(str))
    keys = set(c["Date"] + "/" + (c["Hour"] + 1).astype(str))
    wc = wind[wind["key"].isin(keys)]
    assert len(wc) == 4410
    exp = np.minimum(500.0, wc["270"].to_numpy()).sum()
    assert t.set_index("level_id").loc["P2_500_270", "H_C_MWh"] == pytest.approx(exp, rel=1e-12)
    hcd = t.set_index("level_id")["H_C_MWh"]
    assert hcd["P2_800_b120"] / hcd["P2_800_b275"] == pytest.approx(1.149, abs=0.005)   # section 3 prediction


def test_waves_e_key_only():
    lc.scripts(9)
    assert mk.WAVES_E[W] == "LOC_CONTRAST_E"
    assert mk.WAVES_E["n0_E"] == "N0_E" and mk.WAVES_E["random_E"] == "RANDOM_E"
    assert mk.PROMPT == "53 v3.1"


def test_readme_carries_prereg_and_is_deterministic(built, tmp_path):
    waves, _, _, _ = built
    txt = (waves / W / "README.md").read_text()
    assert lc.PREREG in txt and txt.endswith(lc.PREREG)
    assert lc.PREREG.startswith("## 3. Pre-registered reads (FROZEN with the wave commit")
    assert "**Scope sentence for the paper (conditional, fixed now):**" in lc.PREREG
    assert "857.2" in txt and "97.1%" in txt and "0.933" in txt and 'tier = "contrast"' in txt
    lc.build(waves=tmp_path)
    assert (tmp_path / W / "README.md").read_text() == txt


def test_gitignore_line_present():
    assert f"extracts/{W}/**/*.csv.gz" in (ERCOT / ".gitignore").read_text()


def test_committed_wave_matches_builder(built):
    waves, _, _, _ = built
    if not (WAVES / W / "design_matrix.csv").is_file():
        pytest.skip("wave not built in the tree")
    names = sorted(p.name for p in (waves / W).iterdir())
    assert names == sorted(p.name for p in (WAVES / W).iterdir()
                           if p.name != "runs" and not p.name.startswith("FAILED"))
    for n in names:
        assert (WAVES / W / n).read_text() == (waves / W / n).read_text(), n
