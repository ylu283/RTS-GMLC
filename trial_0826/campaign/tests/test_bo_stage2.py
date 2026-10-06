"""Prompt-30 BO machinery tests: r1 wave validity, build_bo_round refusal,
the fake-round dry run of acquire_next (valid r2 + ledger entry), the
2-consecutive-low stopping rule, and the double-spend guards.

Requires torch/gpytorch + the bo-gp worktree — run under the bogp env:
  BOGP_PATH=/Users/yilu/Documents/GitHub/bo-gp-qparego \
  /opt/anaconda3/envs/bogp/bin/python -m pytest tests/test_bo_stage2.py -v
Skipped automatically in the plain campaign env (no torch).
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
sys.path.insert(0, os.path.join(CAMPAIGN_DIR, "analysis", "bo_stage2"))

import acquire_next as an  # noqa: E402
import make_batches  # noqa: E402
from tiers import STAGE2_LATTICE  # noqa: E402

LAT = np.round(np.asarray(STAGE2_LATTICE, float), 10)
SHA = "60e6328236e745b3d34dc8cd704bb72888ae5d15"
FLOORS = an.FLOORS


# --------------------------------------------------------------------------- #
# fixtures
# --------------------------------------------------------------------------- #

QSUB_SHIM = """#!/bin/bash
# fake qsub: logs argv, prints a synthetic JID (array form for -t)
echo "QSUB $@" >> "$SHIM_LOG"
N=$(( $(wc -l < "$SHIM_LOG") + 9000000 ))
for a in "$@"; do
    if [[ "$a" == "-t" ]]; then echo "$N.1-8:1"; exit 0; fi
done
echo "$N"
"""

QSTAT_SHIM = "#!/bin/bash\nexit 0\n"


@pytest.fixture()
def scratch(tmp_path, monkeypatch):
    """A scratch repo/trial_0826/campaign tree seeded with the 32-point base
    waves, git-initialized on d6 with a local bare origin, and PATH shims
    for qsub/qstat. CAMPAIGN_ROOT points acquire_next at it."""
    repo = tmp_path / "repo"
    camp = repo / "trial_0826" / "campaign"
    (camp / "waves").mkdir(parents=True)
    (camp / "analysis" / "bo_stage2").mkdir(parents=True)
    for w in ("stage2_C_n0", "stage2_C_n0b", "stage2_backfill_C"):
        shutil.copytree(os.path.join(CAMPAIGN_DIR, "waves", w),
                        camp / "waves" / w)
    shutil.copy(os.path.join(CAMPAIGN_DIR, "analysis", "bo_stage2",
                             "acquire_next.py"),
                camp / "analysis" / "bo_stage2" / "acquire_next.py")

    bare = tmp_path / "origin.git"
    subprocess.run(["git", "init", "--bare", "-q", str(bare)], check=True)
    for cmd in (["git", "init", "-q", "-b", "d6", str(repo)],
                ["git", "-C", str(repo), "remote", "add", "origin", str(bare)]):
        subprocess.run(cmd, check=True)
    subprocess.run(["git", "-C", str(repo), "-c", "user.name=t",
                    "-c", "user.email=t@t", "add", "-A"], check=True)
    subprocess.run(["git", "-C", str(repo), "-c", "user.name=t",
                    "-c", "user.email=t@t", "commit", "-q", "-m", "seed"],
                   check=True)
    subprocess.run(["git", "-C", str(repo), "push", "-q", "origin", "d6"],
                   check=True)

    shim = tmp_path / "shim"
    shim.mkdir()
    for name, body in (("qsub", QSUB_SHIM), ("qstat", QSTAT_SHIM)):
        p = shim / name
        p.write_text(body)
        p.chmod(p.stat().st_mode | stat.S_IEXEC)
    monkeypatch.setenv("PATH", f"{shim}:{os.environ['PATH']}")
    monkeypatch.setenv("SHIM_LOG", str(tmp_path / "qsub.log"))
    monkeypatch.setenv("CAMPAIGN_ROOT", str(camp))

    # small candidate subsample for test speed (the acquisition contract —
    # on-lattice, distinct, unseen — is unchanged)
    rng = np.random.default_rng(7)
    sub = np.array([[LAT[i] for i in rng.integers(0, 9, size=6)]
                    for _ in range(4000)])
    monkeypatch.setattr(an, "lattice_candidates", lambda: sub)
    return str(camp)


def fake_objectives(root, k, mode="gp_noise", seed=1):
    """Write a gate-passing objectives.csv for wave k.

    gp_noise: prediction means + N(0, floor^2) per objective (the pinned
    dry-run fixture). strong: one big improver (guaranteed HV gain).
    dup: duplicates of existing Y rows (exactly zero HV gain)."""
    wdir = os.path.join(root, "waves", f"bo_C_r{k}")
    dm = pd.read_csv(os.path.join(wdir, "design_matrix.csv"))
    rng = np.random.default_rng(seed)
    _, Ybase = an.load_training(root, 0)
    if mode == "gp_noise":
        preds = pd.read_csv(os.path.join(wdir, "predictions.csv"))
        Y = np.column_stack([
            preds[f"{c}_pred_mean"] + rng.normal(0, FLOORS[j], size=8)
            for j, c in enumerate(an.M_COLS)])
        Y = np.abs(Y)  # objectives are nonnegative physical quantities
    elif mode == "strong":
        Y = Ybase[rng.integers(0, len(Ybase), size=8)].copy()
        # dominates everything seen; successive seeds push the corner further
        # so EVERY strong round has a large gain (never trips the stop rule)
        Y[0] = Ybase.min(axis=0) * (0.5 - 0.08 * (seed % 5))
    elif mode == "dup":
        Y = Ybase[rng.integers(0, len(Ybase), size=8)].copy()
    out = pd.DataFrame({"index": dm["index"]})
    for j, c in enumerate(an.M_COLS):
        out[c] = Y[:, j]
    out.to_csv(os.path.join(wdir, "objectives.csv"), index=False)
    subprocess.run(["git", "-C", an.repo_root(root), "-c", "user.name=t",
                    "-c", "user.email=t@t", "add", "-A"], check=True)
    subprocess.run(["git", "-C", an.repo_root(root), "-c", "user.name=t",
                    "-c", "user.email=t@t", "commit", "-q", "-m",
                    f"fake r{k} objectives"], check=True)


def init_and_r1(root):
    an.cmd_init(root, SHA)
    an.propose_round(root, 1)
    subprocess.run(["git", "-C", an.repo_root(root), "-c", "user.name=t",
                    "-c", "user.email=t@t", "add", "-A"], check=True)
    subprocess.run(["git", "-C", an.repo_root(root), "-c", "user.name=t",
                    "-c", "user.email=t@t", "commit", "-q", "-m", "r1"],
                   check=True)


def assert_valid_wave(root, k):
    wdir = os.path.join(root, "waves", f"bo_C_r{k}")
    dm = pd.read_csv(os.path.join(wdir, "design_matrix.csv"))
    assert list(dm["index"]) == list(range(1, 9))
    X = dm[[f"{t}_omega" for t in an.SORTED_TIERS]].to_numpy(float)
    an.assert_on_lattice(X)
    assert len({tuple(r) for r in X.round(10).tolist()}) == 8
    assert (dm[[c for c in dm.columns if c.endswith("_bid")]] == 40.0).all().all()
    man = json.load(open(os.path.join(wdir, "manifest.json")))
    assert man["bo_round"] == k and man["bo_gp_sha"] == SHA
    assert np.asarray(man["weights"]).shape == (8, 3)
    assert os.path.isfile(os.path.join(wdir, "predictions.csv"))
    for f in (f"bo_C_r{k}_array.sh", f"collect_bo_C_r{k}.sh", "submit_this.sh"):
        text = open(os.path.join(wdir, f)).read()
        assert "#$ -r n" in text or f == "submit_this.sh"
    sub = open(os.path.join(wdir, "submit_this.sh")).read()
    assert 'cd "$(dirname "${BASH_SOURCE[0]}")"' in sub
    assert "-terse -hold_jid" in sub and f"-v BO_ROUND={k}" in sub
    assert "-M ylu28@nd.edu -m ea" in sub
    return X


# --------------------------------------------------------------------------- #
# tests
# --------------------------------------------------------------------------- #

def test_build_bo_round_refuses_existing(tmp_path):
    designs = np.array([[LAT[i % 9]] * 6 for i in range(8)])
    d1 = make_batches.build_bo_round(99, designs, waves_root=str(tmp_path))
    assert os.path.isdir(d1)
    with pytest.raises(RuntimeError, match="REFUSED"):
        make_batches.build_bo_round(99, designs, waves_root=str(tmp_path))


def test_fake_round_dry_run(scratch):
    root = scratch
    init_and_r1(root)
    led0 = an.load_ledger(root)
    assert led0["entries"][0]["n"] == 32 and led0["threshold"] > 0
    X1 = assert_valid_wave(root, 1)
    # r1 designs are unseen
    Xb, _ = an.load_training(root, 0)
    seen = {tuple(r) for r in Xb.round(10).tolist()}
    assert not ({tuple(r) for r in X1.round(10).tolist()} & seen)

    fake_objectives(root, 1, mode="gp_noise")
    rc = an.run_round(root, 1)
    assert rc == 0
    # valid r2 wave + ledger entry + SUBMITTED line
    assert_valid_wave(root, 2)
    led = an.load_ledger(root)
    assert [e["round"] for e in led["entries"]] == [0, 1]
    assert led["entries"][1]["hv"] >= led["entries"][0]["hv"] - 1e-9
    assert an.round_section_exists(root, 2)
    log = open(an.round_log_path(root)).read()
    assert "SUBMITTED r2:" in log
    recs = json.load(open(an.records_path(root)))
    assert "calibration" in recs["1"] and "designs" in recs["2"]
    # qsub shim saw the triple with the pinned flags
    shim_log = open(os.environ["SHIM_LOG"]).read()
    assert "-t 1-8" in shim_log and "-hold_jid" in shim_log
    assert "-v BO_ROUND=2" in shim_log and "acq_bo_C_r2" in shim_log


def test_stop_rule_two_consecutive_low(scratch):
    root = scratch
    init_and_r1(root)
    # r1 strong gain (above threshold by construction), then two zero-gain
    # duplicate rounds: the rule must NOT fire after one low round and MUST
    # fire after two.
    fake_objectives(root, 1, mode="strong")
    assert an.run_round(root, 1) == 0
    led = an.load_ledger(root)
    assert led["entries"][1]["gain"] > led["threshold"], "fixture not strong enough"
    assert not os.path.isfile(os.path.join(an.bo_dir(root), "BO_DONE.md"))

    fake_objectives(root, 2, mode="dup", seed=2)
    assert an.run_round(root, 2) == 0
    assert not os.path.isfile(os.path.join(an.bo_dir(root), "BO_DONE.md")), \
        "stopped after ONE low round"
    assert os.path.isdir(os.path.join(root, "waves", "bo_C_r3"))

    fake_objectives(root, 3, mode="dup", seed=3)
    assert an.run_round(root, 3) == 0
    done = os.path.join(an.bo_dir(root), "BO_DONE.md")
    assert os.path.isfile(done) and "stopping rule" in open(done).read()
    assert not os.path.isdir(os.path.join(root, "waves", "bo_C_r4"))
    hvs = [e["hv"] for e in an.load_ledger(root)["entries"]]
    assert all(b >= a - 1e-9 for a, b in zip(hvs, hvs[1:]))


def test_hard_cap_refuses_round_5(scratch):
    root = scratch
    init_and_r1(root)
    for k in (1, 2, 3):
        fake_objectives(root, k, mode="strong", seed=10 + k)
        assert an.run_round(root, k) == 0
        assert not os.path.isfile(os.path.join(an.bo_dir(root), "BO_DONE.md"))
    fake_objectives(root, 4, mode="strong", seed=14)
    assert an.run_round(root, 4) == 0
    done = open(os.path.join(an.bo_dir(root), "BO_DONE.md")).read()
    assert "hard cap" in done
    assert not os.path.isdir(os.path.join(root, "waves", "bo_C_r5"))


def test_guard_existing_next_wave(scratch):
    root = scratch
    init_and_r1(root)
    fake_objectives(root, 1)
    os.makedirs(os.path.join(root, "waves", "bo_C_r2"))
    assert an.run_round(root, 1) == 0
    marker = os.path.join(an.bo_dir(root), "FAILED_bo_r1.md")
    assert os.path.isfile(marker) and "double-spend" in open(marker).read()
    assert not an.round_section_exists(root, 2)


def test_ingest_gate_design_mismatch(scratch):
    root = scratch
    init_and_r1(root)
    fake_objectives(root, 1)
    dm_path = os.path.join(root, "waves", "bo_C_r1", "design_matrix.csv")
    dm = pd.read_csv(dm_path)
    cur = dm.loc[0, "nuclear_omega"]
    dm.loc[0, "nuclear_omega"] = float(LAT[0] if cur != LAT[0] else LAT[1])
    dm.to_csv(dm_path, index=False)
    ok, why = an.ingest_gate(root, 1)
    assert not ok and "design_matrix" in why


def test_stop_bo_kill_switch(scratch):
    root = scratch
    init_and_r1(root)
    fake_objectives(root, 1)
    open(os.path.join(an.bo_dir(root), "STOP_BO"), "w").write("stop")
    assert an.run_round(root, 1) == 0
    done = open(os.path.join(an.bo_dir(root), "BO_DONE.md")).read()
    assert "STOP_BO" in done
    assert not os.path.isdir(os.path.join(root, "waves", "bo_C_r2"))


def test_real_r1_wave_committed():
    """The REAL r1 wave built at T1 passes the same validity assertions."""
    wdir = os.path.join(CAMPAIGN_DIR, "waves", "bo_C_r1")
    if not os.path.isdir(wdir):
        pytest.skip("real bo_C_r1 not built yet (pre-T1-propose)")
    dm = pd.read_csv(os.path.join(wdir, "design_matrix.csv"))
    X = dm[[f"{t}_omega" for t in an.SORTED_TIERS]].to_numpy(float)
    an.assert_on_lattice(X)
    assert len({tuple(r) for r in X.round(10).tolist()}) == 8
    man = json.load(open(os.path.join(wdir, "manifest.json")))
    assert man["bo_gp_sha"] == SHA and np.asarray(man["weights"]).shape == (8, 3)
    assert os.path.isfile(os.path.join(wdir, "predictions.csv"))
