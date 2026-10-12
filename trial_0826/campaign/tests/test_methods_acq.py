"""Prompt 35 §3.1 — generalized acquisition (acquire_arm.py).

Requires torch/gpytorch + the bo-gp worktree — run under the bogp env:
  BOGP_PATH=/Users/yilu/Documents/GitHub/bo-gp-qparego \
  /opt/anaconda3/envs/bogp/bin/python -m pytest tests/test_methods_acq.py -v
The bo_C_r2 regression is the full-lattice acquisition (~6 min).
"""

import json
import os
import shutil
import stat
import subprocess
import sys

import numpy as np
import pandas as pd
import pytest

torch = pytest.importorskip("torch")
if os.environ.get("BOGP_PATH"):
    sys.path.insert(0, os.environ["BOGP_PATH"])
pytest.importorskip("bogp")

CAMPAIGN_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(CAMPAIGN_DIR, "analysis", "methods_C"))
import acquire_arm as aa  # noqa: E402

an = aa.an
SHA = "60e6328236e745b3d34dc8cd704bb72888ae5d15"
LAT = np.round(np.asarray(an.STAGE2_LATTICE, float), 10)
BOGP = os.environ.get("BOGP_PATH", "/Users/yilu/Documents/GitHub/bo-gp-qparego")

QSUB_FORBIDDEN = "#!/bin/bash\necho \"QSUB CALLED $@\" >> \"$SHIM_LOG\"\nexit 1\n"


def _git(repo, *args):
    subprocess.run(["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@t", *args],
                   check=True, capture_output=True)


def _mk_scratch(tmp_path, monkeypatch, waves, qstat_body="#!/bin/bash\nexit 0\n", test_arm=True):
    repo = tmp_path / "repo"
    camp = repo / "trial_0826" / "campaign"
    (camp / "waves").mkdir(parents=True)
    (camp / "analysis" / "bo_stage2").mkdir(parents=True)
    (camp / "analysis" / "methods_C").mkdir(parents=True)
    for w in waves:
        shutil.copytree(os.path.join(CAMPAIGN_DIR, "waves", w), camp / "waves" / w)
    for f in ("ledger.json", "round_records.json"):
        shutil.copy(os.path.join(CAMPAIGN_DIR, "analysis", "bo_stage2", f), camp / "analysis" / "bo_stage2" / f)
    cfg = json.load(open(os.path.join(CAMPAIGN_DIR, "analysis", "methods_C", "arms.json")))
    if test_arm:
        cfg["arms"]["T"] = {"dir": "analysis/methods_C/T", "base_waves": ["stage2_C_n0", "stage2_C_n0b"],
                            "round_waves": {}, "round_wave_pattern": "methods_C_T_r{k}", "env": "x",
                            "local_env": "bogp", "acq": "qparego", "seed_id": 9, "init": "mc"}
    json.dump(cfg, open(camp / "analysis" / "methods_C" / "arms.json", "w"), indent=2)
    bare = tmp_path / "origin.git"
    subprocess.run(["git", "init", "--bare", "-q", str(bare)], check=True)
    subprocess.run(["git", "init", "-q", "-b", "d6", str(repo)], check=True)
    subprocess.run(["git", "-C", str(repo), "remote", "add", "origin", str(bare)], check=True)
    _git(repo, "add", "-A"); _git(repo, "commit", "-q", "-m", "seed"); _git(repo, "push", "-q", "origin", "d6")
    shim = tmp_path / "shim"; shim.mkdir()
    for name, body in (("qsub", QSUB_FORBIDDEN), ("qstat", qstat_body)):
        p = shim / name; p.write_text(body); p.chmod(p.stat().st_mode | stat.S_IEXEC)
    monkeypatch.setenv("PATH", f"{shim}:{os.environ['PATH']}")
    monkeypatch.setenv("SHIM_LOG", str(tmp_path / "qsub.log"))
    monkeypatch.setenv("CAMPAIGN_ROOT", str(camp))
    monkeypatch.setenv("BOGP_CLONE", BOGP)
    return str(camp), cfg


@pytest.fixture()
def small_candidates(monkeypatch):
    rng = np.random.default_rng(7)
    sub = np.array([[LAT[i] for i in rng.integers(0, 9, size=6)] for _ in range(4000)])
    monkeypatch.setattr(an, "lattice_candidates", lambda: sub)


def _fake_objectives(root, cfg, arm, k, mode, seed=1):
    wdir = os.path.join(root, "waves", aa.round_wave(cfg, arm, k))
    dm = pd.read_csv(os.path.join(wdir, "design_matrix.csv"))
    _, Yb = aa.load_training(root, cfg, arm, 0)
    rng = np.random.default_rng(seed)
    Y = Yb[rng.integers(0, len(Yb), size=8)].copy()
    if mode == "strong":
        Y[0] = Yb.min(axis=0) * (0.5 - 0.08 * (seed % 5))
    out = pd.DataFrame({"index": dm["index"]})
    for j, c in enumerate(aa.M_COLS):
        out[c] = Y[:, j]
    out.to_csv(os.path.join(wdir, "objectives.csv"), index=False)
    _git(aa.repo_root(root), "add", "-A"); _git(aa.repo_root(root), "commit", "-q", "-m", f"fake {arm} r{k}")


# --------------------------------------------------------------------------- #

def test_regression_reproduces_bo_C_r2(tmp_path, monkeypatch):
    """Scratch CAMPAIGN_ROOT WITHOUT waves/bo_C_r2, torch.manual_seed(0): the
    generalized code proposes bo_C_r2's 8 designs exactly (full lattice)."""
    root, cfg = _mk_scratch(tmp_path, monkeypatch, ["stage2_C_n0", "stage2_C_n0b", "bo_C_r1"], test_arm=False)
    cfg = aa.load_config(root)
    aa.cmd_init(root, cfg, "P1", SHA)
    torch.manual_seed(0)
    wave_dir = aa.propose_round(root, cfg, "P1", 2)
    assert os.path.basename(wave_dir) == "bo_C_r2"
    got = pd.read_csv(os.path.join(wave_dir, "design_matrix.csv")).sort_values("index")[
        [f"{t}_omega" for t in aa.SORTED_TIERS]].to_numpy(float)
    want = pd.read_csv(os.path.join(CAMPAIGN_DIR, "waves", "bo_C_r2", "design_matrix.csv")).sort_values("index")[
        [f"{t}_omega" for t in aa.SORTED_TIERS]].to_numpy(float)
    np.testing.assert_array_equal(got, want)  # 8/8, same order
    man = json.load(open(os.path.join(wave_dir, "manifest.json")))
    real = json.load(open(os.path.join(CAMPAIGN_DIR, "waves", "bo_C_r2", "manifest.json")))
    assert man["acq_seed"] == 20261008 == real["acq_seed"]
    np.testing.assert_allclose(man["weights"], real["weights"])


def test_p1_init_and_seed_rule(tmp_path, monkeypatch):
    root, cfg = _mk_scratch(tmp_path, monkeypatch, ["stage2_C_n0", "stage2_C_n0b", "bo_C_r1", "bo_C_r2"])
    aa.cmd_init(root, cfg, "P1", SHA)
    led = aa.load_ledger(root, cfg, "P1")
    src = json.load(open(os.path.join(CAMPAIGN_DIR, "analysis", "bo_stage2", "ledger.json")))
    assert led["ref_point"] == src["ref_point"] and led["threshold"] == src["threshold"]
    assert [e["round"] for e in led["entries"]] == [0, 1, 2] and led["stop_rule"] == "record_only"
    assert led["live_stop_round"] == 2
    assert set(json.load(open(aa.records_path(root, cfg, "P1")))) == {"1", "2"}
    assert aa.acq_seed(cfg, "P1", 3) == 20261009  # 20261006 + k kept for P1
    assert aa.acq_seed(cfg, "P2", 1) == 20261006 + 200 + 1
    assert aa.acq_seed(cfg, "N1", 4) == 20261006 + 400 + 4
    assert aa.round_wave(cfg, "P1", 2) == "bo_C_r2" and aa.round_wave(cfg, "P1", 3) == "methods_C_P1_r3"
    with pytest.raises(RuntimeError, match="REFUSED"):
        aa.cmd_init(root, cfg, "P1", SHA)
    aa.cmd_init(root, cfg, "N1", SHA)  # copy_P1_ref
    n1 = aa.load_ledger(root, cfg, "N1")
    assert n1["ref_point"] == led["ref_point"] and n1["threshold"] == led["threshold"]
    assert n1["entries"][0]["hv"] == pytest.approx(led["entries"][0]["hv"], rel=1e-12)


def test_round0_init_reproduces_tau1_and_proposes(tmp_path, monkeypatch, small_candidates):
    """`run --round 0` on an arm whose start set IS S1 (test arm T, init mc):
    R_frozen and tau equal prompt 30's (same data, same MC), r1 proposed and
    pushed, and qsub is never called."""
    root, cfg = _mk_scratch(tmp_path, monkeypatch, ["stage2_C_n0", "stage2_C_n0b"])
    assert aa.run_round(root, cfg, "T", 0, no_submit=True) == 0
    led = aa.load_ledger(root, cfg, "T")
    src = json.load(open(os.path.join(CAMPAIGN_DIR, "analysis", "bo_stage2", "ledger.json")))
    np.testing.assert_allclose(led["ref_point"], src["ref_point"], rtol=1e-12)
    assert led["threshold"] == pytest.approx(src["threshold"], rel=1e-12)
    assert os.path.isdir(os.path.join(root, "waves", "methods_C_T_r1"))
    man = json.load(open(os.path.join(root, "waves", "methods_C_T_r1", "manifest.json")))
    assert man["acq_seed"] == 20261006 + 900 + 1 and man["methods_arm"] == "T"
    assert not os.path.exists(os.environ["SHIM_LOG"])  # no qsub, ever
    log = subprocess.run(["git", "-C", aa.repo_root(root), "log", "--oneline", "origin/d6"],
                         capture_output=True, text=True).stdout
    assert "T init + r1 proposed" in log


def test_record_only_runs_to_hard_cap(tmp_path, monkeypatch, small_candidates):
    root, cfg = _mk_scratch(tmp_path, monkeypatch, ["stage2_C_n0", "stage2_C_n0b"])
    aa.run_round(root, cfg, "T", 0, no_submit=True)
    for k in (1, 2, 3, 4):
        _fake_objectives(root, cfg, "T", k, mode="dup", seed=k)  # zero HV gain every round
        assert aa.run_round(root, cfg, "T", k, no_submit=True) == 0
        nxt = os.path.join(root, "waves", f"methods_C_T_r{k + 1}")
        assert os.path.isdir(nxt) == (k < 4)  # continues past would_stop; none beyond the cap
    led = aa.load_ledger(root, cfg, "T")
    ws = [e.get("would_stop") for e in led["entries"][1:]]
    assert ws == [False, True, True, True]  # rule fires at r2, recorded only
    assert all(e["gain_tau"] == pytest.approx(0.0, abs=1e-12) for e in led["entries"][1:])
    assert os.path.isfile(os.path.join(root, "analysis", "methods_C", "T", "DONE_T.md"))
    assert not os.path.exists(os.environ["SHIM_LOG"])


def test_run_refuses_without_no_submit(tmp_path, monkeypatch):
    root, cfg = _mk_scratch(tmp_path, monkeypatch, ["stage2_C_n0", "stage2_C_n0b"])
    with pytest.raises(SystemExit, match="--no-submit"):
        aa.run_round(root, cfg, "T", 0, no_submit=False)


QSTAT_R = """#!/bin/bash
cat <<'EOF'
job-ID  prior   name       user         state submit/start at     queue
-----------------------------------------------------------------------------
 123456 0.55500 methods_C_ ylu28        r     10/12/2026 10:00:00 long@d12chas1
       Full jobname:     methods_C_T_r2
 123457 0.55500 methods_C_ ylu28        qw    10/12/2026 10:00:00
       Full jobname:     methods_C_T_r22
EOF
"""


def test_double_spend_full_jobname(tmp_path, monkeypatch, small_candidates):
    root, cfg = _mk_scratch(tmp_path, monkeypatch, ["stage2_C_n0", "stage2_C_n0b"], qstat_body=QSTAT_R)
    assert aa.qstat_full_names() == [("123456", "methods_C_T_r2"), ("123457", "methods_C_T_r22")]
    assert aa.foreign_jobs_named("methods_C_T_r2") == ["123456"]  # r22 never matches r2
    monkeypatch.setenv("JOB_ID", "123456")
    assert aa.foreign_jobs_named("methods_C_T_r2") == []  # own job excluded
    monkeypatch.delenv("JOB_ID")
    aa.run_round(root, cfg, "T", 0, no_submit=True)  # guard is on methods_C_T_r1: clear
    _fake_objectives(root, cfg, "T", 1, mode="strong")
    aa.run_round(root, cfg, "T", 1, no_submit=True)  # methods_C_T_r2 running elsewhere -> refuse
    assert os.path.isfile(os.path.join(root, "analysis", "methods_C", "T", "FAILED_T_r1.md"))
    assert not os.path.exists(os.path.join(root, "waves", "methods_C_T_r2"))


def test_ingest_gate_and_stop_file(tmp_path, monkeypatch, small_candidates):
    root, cfg = _mk_scratch(tmp_path, monkeypatch, ["stage2_C_n0", "stage2_C_n0b"])
    aa.run_round(root, cfg, "T", 0, no_submit=True)
    aa.run_round(root, cfg, "T", 1, no_submit=True)  # no objectives yet
    assert "objectives.csv missing" in open(os.path.join(root, "analysis", "methods_C", "T", "FAILED_T_r1.md")).read()
    open(os.path.join(root, "analysis", "methods_C", "T", "STOP_T"), "w").write("")
    aa.run_round(root, cfg, "T", 1, no_submit=True)
    assert os.path.isfile(os.path.join(root, "analysis", "methods_C", "T", "DONE_T.md"))
