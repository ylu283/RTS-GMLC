"""Prompt 35 — methods_C builders, generic templates and the bastion state
machine (base env; no torch needed)."""

import json
import os
import shutil
import stat
import subprocess
import sys

import numpy as np
import pandas as pd
import pytest

import make_batches
from tiers import STAGE2_LATTICE, SOBOL_SEED, TIERS

CAMPAIGN = os.path.dirname(make_batches.WAVES_ROOT)
MC = os.path.join(CAMPAIGN, "analysis", "methods_C")
sys.path.insert(0, MC)
import methods_state  # noqa: E402

LAT = np.asarray(STAGE2_LATTICE, float)
OM = [f"{t}_omega" for t in sorted(TIERS)]


def _x(wave_dir):
    return pd.read_csv(os.path.join(wave_dir, "design_matrix.csv"))[OM].to_numpy(float)


def _on_lattice(X):
    return all(np.isclose(LAT, w, atol=1e-12).any() for w in X.ravel())


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    root = str(tmp_path_factory.mktemp("methods_waves"))
    out = {k: make_batches.build_methods_start(k, waves_root=root) for k in (2, 3)}
    for j in (1, 2, 3):
        out[f"Q{j}"] = make_batches.build_methods_sobol(j, waves_root=root, source_root=(
            make_batches.WAVES_ROOT if j == 1 else root))
    out["root"] = root
    return out


def test_n0_defaults_reproduce_frozen_stage2_C_n0(tmp_path):
    d = make_batches.build_stage2_n0("C", waves_root=str(tmp_path))
    a = pd.read_csv(os.path.join(d, "design_matrix.csv"))
    b = pd.read_csv(os.path.join(make_batches.WAVES_ROOT, "stage2_C_n0", "design_matrix.csv"))
    pd.testing.assert_frame_equal(a, b)


@pytest.mark.parametrize("k", [2, 3])
def test_start_sets(built, k):
    d = built[k]
    X = _x(d)
    assert X.shape == (32, 6) and _on_lattice(X)
    assert len({tuple(r) for r in X.tolist()}) == 32
    m = json.load(open(os.path.join(d, "manifest.json")))
    assert m["sobol"]["seed"] == SOBOL_SEED + k - 1 and m["sobol"]["n"] == 32
    assert m["sobol"]["n_drawn_total"] >= 32 and "scipy_version" in m["sobol"]
    assert isinstance(m["methods_overlaps"], list)
    dm = pd.read_csv(os.path.join(d, "design_matrix.csv"))
    assert (dm[[f"{t}_bid" for t in sorted(TIERS)]] == 40.0).all().all() and (dm.rho_h2 == 2.0).all()


def test_start_sets_differ_and_deterministic(built, tmp_path):
    assert not np.array_equal(_x(built[2]), _x(built[3]))
    again = make_batches.build_methods_start(2, waves_root=str(tmp_path))
    np.testing.assert_array_equal(_x(again), _x(built[2]))


@pytest.mark.parametrize("j", [1, 2, 3])
def test_sobol_continuations(built, j):
    d = built[f"Q{j}"]
    X = _x(d)
    assert X.shape == (16, 6) and _on_lattice(X)
    m = json.load(open(os.path.join(d, "manifest.json")))
    src_root = make_batches.WAVES_ROOT if j == 1 else built["root"]
    src = ["stage2_C_n0", "stage2_C_n0b"] if j == 1 else [f"methods_C_S{j}_n0"]
    start = set()
    for w in src:
        start |= {tuple(r) for r in _x(os.path.join(src_root, w)).tolist()}
    assert len(start) == 32
    keys = {tuple(r) for r in X.tolist()}
    assert len(keys) == 16 and not (keys & start)  # deduped against its start set
    s = m["sobol"]
    assert s["seed"] == SOBOL_SEED + j - 1 and s["continues_waves"] == src
    if j == 1:
        assert s["skip"] == 32  # the n0b manifest's n_drawn_total
    snap = json.load(open(os.path.join(d, "snap_map.json")))
    assert snap["draws"][0]["draw"] == s["skip"] + 1  # GLOBAL numbering


def test_q1_deterministic(tmp_path):
    a = make_batches.build_methods_sobol(1, waves_root=str(tmp_path / "a"))
    b = make_batches.build_methods_sobol(1, waves_root=str(tmp_path / "b"))
    np.testing.assert_array_equal(_x(a), _x(b))


def test_refuse_existing(built):
    with pytest.raises(RuntimeError, match="REFUSED"):
        make_batches.build_methods_start(2, waves_root=built["root"])
    with pytest.raises(RuntimeError, match="REFUSED"):
        make_batches.build_methods_sobol(2, waves_root=built["root"], source_root=built["root"])
    designs = np.array([[LAT[i]] * 6 for i in range(8)])
    make_batches.build_methods_round("methods_C_T_r1", designs, waves_root=built["root"])
    with pytest.raises(RuntimeError, match="REFUSED"):
        make_batches.build_methods_round("methods_C_T_r1", designs, waves_root=built["root"])


def test_registered_without_tc():
    for name in ("methods_C_S2_n0", "methods_C_S3_n0", "methods_C_Q1", "methods_C_Q2", "methods_C_Q3"):
        assert name in make_batches.BUILDERS and make_batches.WAVE_MAX_CONCURRENT[name] is None
    assert not any(k.startswith("methods_C_P") or k.startswith("methods_C_N") for k in make_batches.BUILDERS)


def test_generic_templates(tmp_path):
    make_batches.write_methods_templates(str(tmp_path))
    arr = open(tmp_path / "methods_array.sh").read()
    col = open(tmp_path / "methods_collect.sh").read()
    for t in (arr, col):
        assert "#$ -tc" not in t and "#$ -r n" in t
        assert ': "${WAVE:?' in t
    assert "PYTHONNOUSERSITE=1" in col  # collector (pandas only) keeps it
    assert "-M " not in arr.split("set -euo")[1] and "FATAL" in arr and 'mkdir -p "$WAVE_DIR/runs"' in arr
    assert "flock 9" in col and "methods-bot" in col and "pairgrid-bot" not in col
    assert 'git -C "$REPO_DIR" rm -q -- "$WAVE_DIR/FAILED_${WAVE}.md"' in col
    assert "objectives check" in col
    # the committed copies are current
    for f in ("methods_array.sh", "methods_collect.sh"):
        assert open(os.path.join(MC, f)).read() == open(tmp_path / f).read()


def test_job_script_never_submits():
    job = open(os.path.join(MC, "acquire_arm_job.sh")).read()
    assert "--no-submit" in job and "submit_this.sh" not in job
    assert "OMP_NUM_THREADS=4" in job and "set_num_threads(4)" in job
    assert "qsub " not in job.split("trap on_err ERR")[1]


# ---- submit_ready state machine on a fake tree ----------------------------- #

def _wave(root, name, n, landed=False, failed=False):
    d = os.path.join(root, "waves", name)
    os.makedirs(d, exist_ok=True)
    pd.DataFrame({"index": range(1, n + 1)}).to_csv(os.path.join(d, "design_matrix.csv"), index=False)
    if landed:
        pd.DataFrame({"index": range(1, n + 1)}).to_csv(os.path.join(d, "objectives.csv"), index=False)
    if failed:
        open(os.path.join(d, f"FAILED_{name}.md"), "w").write("x")


def _ledger(root, arm, graded):
    d = os.path.join(root, "analysis", "methods_C", arm)
    os.makedirs(d, exist_ok=True)
    ent = [{"round": 0, "hv": 1.0, "gain": None}] + [{"round": k, "hv": 1.0, "gain": 0.0} for k in graded]
    json.dump({"entries": ent, "threshold": 1.0}, open(os.path.join(d, "ledger.json"), "w"))


@pytest.fixture()
def fake_tree(tmp_path):
    root = str(tmp_path / "campaign")
    os.makedirs(os.path.join(root, "analysis", "methods_C"))
    shutil.copy(os.path.join(MC, "arms.json"), os.path.join(root, "analysis", "methods_C"))
    _wave(root, "methods_C_S2_n0", 32)                      # BUILT -> submit
    _wave(root, "methods_C_S3_n0", 32, landed=True)          # LANDED
    _wave(root, "methods_C_Q1", 16, failed=True)            # FAILED
    _wave(root, "methods_C_Q2", 16)
    _wave(root, "methods_C_Q3", 16)
    _ledger(root, "P1", [1, 2]); _wave(root, "methods_C_P1_r3", 8)   # READY_ARRAY
    _ledger(root, "N1", []); _wave(root, "methods_C_N1_r1", 8, landed=True)  # READY_ACQ
    return root


def test_state_machine_dry_run(fake_tree):
    lines, table = methods_state.run(fake_tree, execute=False, hold=True, out=lambda *_: None)
    st = {n: s for n, s, _ in table}
    assert st["methods_C_S2_n0"] == "SUBMITTED (now)" and st["methods_C_S3_n0"] == "LANDED"
    assert st["methods_C_Q1"] == "FAILED"
    assert st["P1"] == "SUBMITTED (now)" and st["P2"] == "WAIT_BASE"
    assert st["P3"] == "ACQ_SUBMITTED (now)" and st["N1"] == "ACQ_SUBMITTED (now)"
    joined = "\n".join(lines)
    assert "SUBMITTED wave=methods_C_P1_r3 " in joined
    assert "SUBMITTED acq arm=P3 round=0" in joined and "SUBMITTED wave=methods_C_P3_r1" in joined and "held_on=" in joined
    assert "SUBMITTED acq arm=N1 round=1" in joined and "SUBMITTED wave=methods_C_N1_r2" in joined
    assert not os.path.exists(os.path.join(fake_tree, "analysis", "methods_C", "PROGRESS.md"))


QSUB_SHIM = """#!/bin/bash
echo "QSUB $@" >> "$SHIM_LOG"
N=$(( $(wc -l < "$SHIM_LOG") + 7000000 ))
for a in "$@"; do [[ "$a" == "-t" ]] && { echo "$N.1-8:1"; exit 0; }; done
echo "$N"
"""


def test_state_machine_execute_idempotent(fake_tree, tmp_path, monkeypatch):
    shim = tmp_path / "shim"; shim.mkdir()
    (shim / "qsub").write_text(QSUB_SHIM)
    (shim / "qsub").chmod(0o755)
    monkeypatch.setenv("PATH", f"{shim}:{os.environ['PATH']}")
    monkeypatch.setenv("SHIM_LOG", str(tmp_path / "qsub.log"))
    lines1, _ = methods_state.run(fake_tree, execute=True, hold=True, out=lambda *_: None)
    log = open(tmp_path / "qsub.log").read()
    assert "-tc" not in log and log.count("-r n") == log.count("QSUB")
    assert "-pe smp 4" in log and "-v ARM=N1,BO_ROUND=1" in log and "-N methods_C_N1_r2" in log
    for line in log.splitlines():  # email on collectors + acquisitions only, never arrays
        if "methods_array.sh" in line:
            assert "-M" not in line and "-m " not in line
    prog = open(os.path.join(fake_tree, "analysis", "methods_C", "PROGRESS.md")).read()
    assert prog.count("SUBMITTED") == len(lines1)
    lines2, table2 = methods_state.run(fake_tree, execute=True, hold=True, out=lambda *_: None)
    assert lines2 == []  # nothing READY twice
    st = {n: s for n, s, _ in table2}
    assert st["P1"] == "SUBMITTED" and st["N1"] == "ACQ_SUBMITTED" and st["P3"] == "ACQ_SUBMITTED"


def test_state_machine_no_hold(fake_tree):
    lines, _ = methods_state.run(fake_tree, execute=False, hold=False, out=lambda *_: None)
    assert not any("held_on" in l for l in lines)
    assert not any("methods_C_N1_r2" in l for l in lines)


def test_progress_parser():
    w, a = methods_state.parse_progress(
        "SUBMITTED wave=methods_C_Q1 array=11 collector=12\n"
        "SUBMITTED acq arm=P2 round=0 acq=13\n"
        "SUBMITTED wave=methods_C_P2_r1 array=14 collector=15 held_on=13\nnoise\n")
    assert w["methods_C_P2_r1"]["held_on"] == "13" and a[("P2", 0)] == "13"


# ---- real waves (skip until built at T0) ----------------------------------- #

REAL = [n for n in ("methods_C_S2_n0", "methods_C_S3_n0", "methods_C_Q1", "methods_C_Q2", "methods_C_Q3")
        if os.path.isdir(os.path.join(make_batches.WAVES_ROOT, n))]


@pytest.mark.skipif(not REAL, reason="methods_C waves not built yet")
@pytest.mark.parametrize("name", REAL)
def test_real_wave_manifest_clean(name):
    m = json.load(open(os.path.join(make_batches.WAVES_ROOT, name, "manifest.json")))
    assert m["dirty"] is False and m["n_rows"] == (32 if name.endswith("_n0") else 16)


def test_not_run_marker_blocks_arm(fake_tree):
    d = os.path.join(fake_tree, "analysis", "methods_C", "N1")
    open(os.path.join(d, "NOT_RUN_N1.md"), "w").write("gate failed")
    lines, table = methods_state.run(fake_tree, execute=False, hold=True, out=lambda *_: None)
    assert {n: s for n, s, _ in table}["N1"] == "NOT_RUN"
    assert not any("N1" in l for l in lines)


def _env_lines(text):
    keys = ("conda activate", "module load", "PYTHONNOUSERSITE", "GUROBI_MODULE=", "profile.d/conda.sh")
    return [l.strip() for l in text.splitlines()
            if any(k in l for k in keys) and not l.lstrip().startswith("#")]


def test_array_env_matches_frozen_stage2():
    """Launch-1 lesson (10-12): the PRESCIENT array task must use the frozen
    Stage-2 env convention exactly — PCM0826, gurobi module, and NO
    PYTHONNOUSERSITE (networkx for egret lives in ~/.local)."""
    arr = open(os.path.join(MC, "methods_array.sh")).read()
    ref = open(os.path.join(make_batches.WAVES_ROOT, "random_C", "random_C_array.sh")).read()
    assert _env_lines(arr) == _env_lines(ref)
    code = lambda t: "\n".join(l for l in t.splitlines() if not l.lstrip().startswith("#"))
    assert "PYTHONNOUSERSITE" not in code(make_batches.METHODS_ARRAY)
    for w in ("bo_C_r2", "stage2_C_n0b"):
        other = [f for f in os.listdir(os.path.join(make_batches.WAVES_ROOT, w)) if f.endswith("_array.sh")]
        for f in other:
            assert _env_lines(open(os.path.join(make_batches.WAVES_ROOT, w, f)).read()) == _env_lines(ref)


# ---- launch-1 relaunch rule (FAILED + 0 completed runs -> resubmit ONCE) -----

def _launch1_tree(root):
    """All 7 T0 items submitted once, all FAILED at import (no run completed)."""
    prog = os.path.join(root, "analysis", "methods_C", "PROGRESS.md")
    items = ["methods_C_S2_n0", "methods_C_S3_n0", "methods_C_Q1", "methods_C_Q2", "methods_C_Q3",
             "methods_C_P1_r3", "methods_C_N1_r1"]
    lines = []
    for i, w in enumerate(items):
        n = 32 if w.endswith("_n0") else (16 if "_Q" in w else 8)
        _wave(root, w, n, failed=True)
        ob = os.path.join(root, "waves", w, "objectives.csv")
        if os.path.exists(ob):
            os.remove(ob)  # launch 1: no wave produced objectives
        os.makedirs(os.path.join(root, "waves", w, "runs"), exist_ok=True)  # mkdir -p ran, nothing inside
        lines.append(f"SUBMITTED wave={w} array={100 + 2 * i} collector={101 + 2 * i}")
    open(prog, "w").write("\n".join(lines) + "\n")
    return items


def test_relaunch_failed_once(fake_tree, tmp_path, monkeypatch):
    shutil.rmtree(os.path.join(fake_tree, "waves", "methods_C_S3_n0"))
    items = _launch1_tree(fake_tree)
    # without the flag: reported, nothing submitted
    lines, table = methods_state.run(fake_tree, execute=False, out=lambda *_: None)
    assert lines == [] and all("relaunchable" in s for n, s, _ in table if n in
                               ("methods_C_S2_n0", "methods_C_Q1", "P1", "N1"))
    # with the flag (fake qsub): 7 relaunches, markers removed, lines tagged
    shim = tmp_path / "shim"; shim.mkdir()
    (shim / "qsub").write_text(QSUB_SHIM); (shim / "qsub").chmod(0o755)
    monkeypatch.setenv("PATH", f"{shim}:{os.environ['PATH']}")
    monkeypatch.setenv("SHIM_LOG", str(tmp_path / "qsub.log"))
    lines, table = methods_state.run(fake_tree, execute=True, out=lambda *_: None, relaunch_failed=True)
    assert len(lines) == 7 and all(l.endswith("relaunch=1") for l in lines)
    assert not any(os.path.exists(os.path.join(fake_tree, "waves", w, f"FAILED_{w}.md")) for w in items)
    assert sum(1 for l in open(tmp_path / "qsub.log") if "methods_array.sh" in l) == 7
    # idempotent: now SUBMITTED, nothing new
    lines2, table2 = methods_state.run(fake_tree, execute=True, out=lambda *_: None, relaunch_failed=True)
    assert lines2 == [] and {n: s for n, s, _ in table2}["P1"] == "SUBMITTED"
    # fails again -> NOT relaunchable a second time
    _wave(fake_tree, "methods_C_Q1", 16, failed=True)
    lines3, table3 = methods_state.run(fake_tree, execute=False, out=lambda *_: None, relaunch_failed=True)
    assert lines3 == [] and {n: s for n, s, _ in table3}["methods_C_Q1"] == "FAILED"


def test_relaunch_refused_when_a_run_completed(fake_tree):
    _launch1_tree(fake_tree)
    d = os.path.join(fake_tree, "waves", "methods_C_Q2", "runs", "run_index_3")
    os.makedirs(d); open(os.path.join(d, "overall_simulation_output.csv"), "w").write("x")
    lines, table = methods_state.run(fake_tree, execute=False, out=lambda *_: None, relaunch_failed=True)
    assert {n: s for n, s, _ in table}["methods_C_Q2"] == "FAILED"
    assert not any("methods_C_Q2" in l for l in lines)
