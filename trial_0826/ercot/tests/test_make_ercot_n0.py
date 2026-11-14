"""Prompt 53 v3.1 tests for tools/make_ercot_n0.py (waves/n0_E, waves/random_E).

Run:  cd trial_0826/ercot && /opt/anaconda3/bin/python -m pytest tests/test_make_ercot_n0.py -q

Checks: 48 / 48 / 32 rows, the Sobol prefix property, u = mw / pmax to
1e-9, gen_pmax and bus equal to wave D's, retrofit dicts (exact zeros
omitted, gen_pmax on every present site), the pinned draws, the holdout bar,
the scripts (bash -n, SGE flags, identity read), the GAP_DECISION refusal of
the array block and of submit_this.sh, the .gitignore lines, committed
waves == fresh build.
"""
import json
import os
import subprocess
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from scipy.stats import binom, qmc

ERCOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ERCOT / "tools"))
import make_ercot_n0 as mk  # noqa: E402

WAVES = ERCOT / "waves"
E_WAVES = ("n0_E", "random_E")


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    waves = tmp_path_factory.mktemp("waves")
    rows, space = mk.build(waves=waves)
    return waves, rows, space


def _dm(path):
    # round_trip: pandas' default C float parser is not bit-exact on 17-digit reprs
    return pd.read_csv(path, dtype={"oat_site": str, "tier": str}, float_precision="round_trip")


def test_design_space_matches_wave_d():
    space = mk.load_space()
    dm = pd.read_csv(mk.WAVE_D_DM, dtype={"oat_site": str})
    assert space["sites"] == ["110", "140", "146", "163", "270", "274"]
    for j, s in enumerate(space["sites"]):
        r = dm[dm["oat_site"] == s]
        assert len(r) == 3
        assert abs(float(r["gen_pmax"].iloc[0]) - space["pmax"][j]) <= 1e-6
        assert int(r["bus"].iloc[0]) == space["json"]["sites"][j]["bus"]
    gen = pd.read_csv(ERCOT / mk.V2_DATA_REL / "gen.csv", dtype={"GEN UID": str}).set_index("GEN UID")
    for j, s in enumerate(space["sites"]):
        assert abs(float(gen.loc[s, "PMax MW"]) - space["pmax"][j]) <= 1e-6
        assert float(gen.loc[s, "PMin MW"]) == 0.0           # no must-take site (continuity note)


def test_load_space_refuses_pmax_mismatch(tmp_path):
    js = json.loads(mk.DESIGN_SPACE.read_text())
    js["sites"][0]["gen_pmax"] += 1e-3
    js["bounds_mw_hi"][0] = js["sites"][0]["gen_pmax"]
    p = tmp_path / "ds.json"
    p.write_text(json.dumps(js))
    with pytest.raises(AssertionError):
        mk.load_space(p)


def test_row_counts_and_nav_prefix(built):
    waves, rows, _ = built
    n0 = _dm(waves / "n0_E" / "design_matrix.csv")
    rnd = _dm(waves / "random_E" / "design_matrix.csv")
    assert len(n0) == 48 and len(rnd) == 48
    assert list(n0["index"]) == list(range(1, 49)) and list(rnd["index"]) == list(range(1, 49))
    assert list(n0["sobol_index"]) == list(range(48))
    assert (n0["sobol_index"] < 32).sum() == 32               # the nav candidates
    assert set(n0["tier"]) == {"grading"} and set(rnd["tier"]) == {"holdout"}
    assert rnd["sobol_index"].isna().all()
    for dm in (n0, rnd):
        assert (dm["oat_site"] == "__ALL__").all() and (dm["bid"] == 40.0).all()
        assert (dm["start_date"] == "01-01-2019").all() and (dm["num_days"] == 365).all()
        for c in ("unit_type", "bus", "omega", "gen_pmax", "replicate_of", "level_id"):
            assert dm[c].isna().all(), c
    assert list(n0.columns) == mk.COLS + [f"mw_{s}" for s in mk.load_space()["sites"]] \
        + [f"u_{s}" for s in mk.load_space()["sites"]]


def test_sobol_prefix_property_and_pinned_draw(built):
    waves, _, space = built
    S = qmc.Sobol(d=6, scramble=True, seed=53).random_base2(6)
    assert S.shape == (64, 6)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")            # random(48) warns on balance: the reason for base2
        assert np.array_equal(S[:32], qmc.Sobol(d=6, scramble=True, seed=53).random(32))
        assert np.array_equal(S[:48], qmc.Sobol(d=6, scramble=True, seed=53).random(48))
    n0 = _dm(waves / "n0_E" / "design_matrix.csv")
    U = n0[[f"u_{s}" for s in space["sites"]]].to_numpy()
    assert np.array_equal(U, S[:48])                          # bit-exact with round_trip parsing
    R = np.random.default_rng(5353).random((48, 6))
    rnd = _dm(waves / "random_E" / "design_matrix.csv")
    assert np.array_equal(rnd[[f"u_{s}" for s in space["sites"]]].to_numpy(), R)


def test_u_equals_mw_over_pmax_and_bounds(built):
    waves, _, space = built
    for w in E_WAVES:
        dm = _dm(waves / w / "design_matrix.csv")
        mw = dm[[f"mw_{s}" for s in space["sites"]]].to_numpy()
        u = dm[[f"u_{s}" for s in space["sites"]]].to_numpy()
        assert np.abs(u - mw / space["pmax"]).max() <= 1e-9
        assert (mw >= 0).all() and (mw <= space["pmax"] + 1e-9).all()
        assert np.abs(dm["pem_mw"].to_numpy() - mw.sum(axis=1)).max() <= 1e-9
    n0 = _dm(waves / "n0_E" / "design_matrix.csv")
    assert n0[[f"u_{s}" for s in space["sites"]]].to_numpy().min() == pytest.approx(1.0441644117236137e-3)
    assert n0["mw_163"].min() == pytest.approx(0.19358806903477793)


def test_retrofit_dicts(built):
    waves, rows, space = built
    for w in E_WAVES:
        for r in rows[w]:
            d = json.loads((waves / w / f"retrofit_gen_dict_{r['index']}.json").read_text())
            assert sorted(d) == sorted(s for s in space["sites"] if r[f"mw_{s}"] > 0)
            for j, s in enumerate(space["sites"]):
                if s in d:
                    assert d[s] == {"PEM_bid": 40.0, "PEM_fraction": r[f"u_{s}"],
                                    "gen_pmax": float(space["pmax"][j])}
    # an exact zero is OMITTED (0 = absent, never omega = 0)
    space = mk.load_space()
    U = np.array([[0.0, 0.5, 0.0, 1.0, 0.25, 0.0]])
    r = mk.make_rows(U, space, "bo")[0]
    d = mk.retrofit_dict(r, space)
    assert sorted(d) == ["140", "163", "270"]
    assert d["163"]["PEM_fraction"] == 1.0 and d["163"]["gen_pmax"] == space["pmax"][3]
    assert r["pem_mw"] == pytest.approx(0.5 * space["pmax"][1] + space["pmax"][3] + 0.25 * space["pmax"][4])


def test_holdout_bar_pinned():
    assert binom.interval(0.90, 48, 0.95) == (43.0, 48.0)
    assert binom.interval(0.95, 48, 0.95) == (42.0, 48.0)      # the common.binom_band default trap
    txt = (WAVES / "random_E" / "README.md").read_text() if (WAVES / "random_E" / "README.md").is_file() else ""
    if txt:
        assert "[43, 48]" in txt and "24" in txt and "E-D2 dual role" in txt


def _bash_n(p):
    r = subprocess.run(["bash", "-n", str(p)], capture_output=True, text=True)
    assert r.returncode == 0, (p, r.stderr)


def test_scripts_parse(built):
    waves, _, _ = built
    for w in E_WAVES:
        st = mk.WAVES_E[w]
        for f in (f"{w}_array.sh", f"collect_{w}.sh", "submit_this.sh"):
            _bash_n(waves / w / f)
        arr = (waves / w / f"{w}_array.sh").read_text()
        assert "#$ -t 1-48" in arr and "#$ -pe smp 4" in arr and "#$ -r n" in arr and "#$ -q long" in arr
        assert "-tc" not in arr
        assert "SMOKE_PASS" in arr and "GAP_DECISION.json" in arr
        assert '--ruc_mipgap "$RUC_MIPGAP"' in arr and '--ruc_time_limit "$RUC_TIME_LIMIT"' in arr
        assert f"{st}_START" in arr and f"{st}_END" in arr
        assert 'ERCOT_DIR="$(cd "$WAVE_DIR/../.." && pwd)"' in arr
        coll = (waves / w / f"collect_{w}.sh").read_text()
        assert "--full" in coll and "pool_objectives.py" in coll and "--run-dir" in coll
        assert "runtimes.csv" in coll and "wallclock.csv" in coll and r"\.csv\.gz$" in coll
        assert f'extracts/{w}"' in coll and '"$EXTR/COLLECTED"' in coll and "identity.txt" in coll
        assert "push_with_retries" in coll and "1 2 3 4 5" in coll and "-M " not in coll
        sub = (waves / w / "submit_this.sh").read_text()
        assert 'cat "$W/GAP_DECISION.json"' in sub and "SMOKE_PASS" in sub and "design_space_E.json" in sub
        assert f"-M {mk.EMAIL} -m ea collect_{w}.sh" in sub and "read -r -p" in sub
        assert f"qsub -terse {w}_array.sh" in sub


def _gap_block(waves, w):
    arr = (waves / w / f"{w}_array.sh").read_text()
    return arr[arr.index("# --- identity from waves/GAP_DECISION.json"):arr.index('eval "$(python')]


@pytest.mark.parametrize("w", E_WAVES)
def test_array_refuses_without_gap_decision(built, tmp_path, w):
    waves, _, _ = built
    ercot = tmp_path / "ercot"
    (ercot / "waves").mkdir(parents=True)
    wave = tmp_path / "wave"
    wave.mkdir()
    script = (f'set -euo pipefail\nERCOT_DIR="{ercot}"\nWAVE_DIR="{wave}"\nSGE_TASK_ID=7\n'
              + _gap_block(waves, w) + 'echo "REACHED_RUN"\n')
    r = subprocess.run(["bash", "-c", script], capture_output=True, text=True)
    assert r.returncode != 0 and "ABORT task 7" in r.stdout and "REACHED_RUN" not in r.stdout
    assert (wave / "FAILED_task_7_no_gap_decision.md").is_file()
    (ercot / "waves" / "GAP_DECISION.json").write_text(json.dumps({"ruc_mipgap": 0.001, "ruc_time_limit": 1200}))
    r = subprocess.run(["bash", "-c", script + 'echo "GAP=$RUC_MIPGAP TL=$RUC_TIME_LIMIT"\n'],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "REACHED_RUN" in r.stdout and "GAP=0.001 TL=1200.0" in r.stdout
    assert "IDENTITY from GAP_DECISION.json: ruc_mipgap=0.001 ruc_time_limit=1200.0" in r.stdout


def _fake_bin(tmp_path):
    fake = tmp_path / "bin"
    fake.mkdir()
    (fake / "git").write_text('#!/bin/bash\ncase "$*" in *"branch --show-current"*) echo ercot/tx123;; *) exit 0;; esac\n')
    (fake / "qsub").write_text('#!/bin/bash\necho "qsub must not run"; exit 99\n')
    (fake / "qquota").write_text('#!/bin/bash\necho "quota ok"\n')
    for f in fake.iterdir():
        f.chmod(0o755)
    return fake


@pytest.mark.parametrize("w", E_WAVES)
def test_submit_refuses_without_gap_decision(built, tmp_path, w):
    waves, _, _ = built
    fake = _fake_bin(tmp_path)
    ercot = tmp_path / "repo" / "trial_0826" / "ercot"
    wd = ercot / "waves" / w
    wd.mkdir(parents=True)
    for f in (waves / w).iterdir():
        (wd / f.name).write_text(f.read_text())

    def run(answer="no\n"):
        return subprocess.run(["bash", str(wd / "submit_this.sh")], capture_output=True, text=True,
                              env={**os.environ, "PATH": f"{fake}:{os.environ['PATH']}"}, input=answer)
    r = run()
    assert r.returncode != 0 and "GAP_DECISION.json absent" in r.stdout, r.stdout + r.stderr
    assert "qsub must not run" not in r.stdout
    (ercot / "waves" / "GAP_DECISION.json").write_text('{"ruc_mipgap": 0.001, "ruc_time_limit": 1200}\n')
    (ercot / "waves" / "smoke_v2").mkdir()
    (ercot / "waves" / "smoke_v2" / "SMOKE_PASS").write_text("ok\n")
    r = run()
    assert r.returncode != 0 and "design_space_E.json absent" in r.stdout, r.stdout + r.stderr
    (ercot / "waves" / "design_space_E.json").write_text("{}\n")
    (ercot / mk.V2_DATA_REL).mkdir(parents=True)
    (ercot / mk.V2_DATA_REL / "gen.csv").write_text("GEN UID\n")
    (ercot / "run_ercot_pcm.py").write_text("# --ruc_mipgap\n")
    (ercot / ".gitignore").write_text(f"extracts/{w}/**/*.csv.gz\n")
    r = run()                                   # full pre-flight passes; Kay answers "no"
    assert r.returncode != 0 and "not submitted" in r.stdout and "qsub must not run" not in r.stdout, r.stdout + r.stderr
    assert "ruc_mipgap" in r.stdout


def test_gitignore_lines_present():
    gi = (ERCOT / ".gitignore").read_text()
    for w in E_WAVES:
        assert f"extracts/{w}/**/*.csv.gz" in gi


def test_committed_waves_match_builder(built):
    waves, rows, _ = built
    if not (WAVES / "n0_E" / "design_matrix.csv").is_file():
        pytest.skip("waves not built in the tree")
    for w in E_WAVES:
        names = sorted(p.name for p in (waves / w).iterdir())
        assert names == sorted(p.name for p in (WAVES / w).iterdir() if p.name != "runs"
                               and not p.name.startswith(("FAILED", "LANDING", "landing_R"))), w
        for n in names:
            assert (WAVES / w / n).read_text() == (waves / w / n).read_text(), (w, n)
