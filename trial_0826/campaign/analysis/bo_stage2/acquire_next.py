"""Stage-2 BO acquisition brain (prompt 30, q-ParEGO, fully automated).

Called by acquire_job.sh on CRC after each round's collector (subcommand
`run --round k`), and by T1 locally (`init`, `propose --round 1`). All
campaign DATA paths derive from CAMPAIGN_ROOT (env override for the dry
run / tests) — code imports always come from this file's own tree.

Handled stops (gate failures, guards, STOP_BO, stopping rule, cap) write a
marker/BO_DONE and exit 0; only unhandled crashes exit nonzero, which trips
acquire_job.sh's ERR trap (WEDGED marker). Fixed configuration is pinned in
the prompt — do not re-open here.
"""

from __future__ import annotations

import argparse
import itertools
import json
import os
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone

import numpy as np
import pandas as pd

_HERE = os.path.dirname(os.path.abspath(__file__))
_OWN_CAMPAIGN = os.path.abspath(os.path.join(_HERE, "..", ".."))
sys.path.insert(0, _OWN_CAMPAIGN)  # campaign code (tiers, make_batches, ...)

_BOGP_PATH = os.environ.get("BOGP_PATH")
if _BOGP_PATH:
    sys.path.insert(0, _BOGP_PATH)

import torch  # noqa: E402
import gpytorch  # noqa: E402
from gpytorch.constraints import GreaterThan  # noqa: E402

from bogp.gp_model import GPRegressionModel, train_gp  # noqa: E402
from bogp.mobo.pareto import hypervolume_exact  # noqa: E402
from bogp.mobo.qparego import propose_qparego_batch  # noqa: E402

from tiers import TIERS, STAGE2_LATTICE  # noqa: E402
import make_batches  # noqa: E402

M_COLS = ["load_shed_mwh", "true_curtailment_mwh", "total_cost_less_synthetic_usd"]
FLOORS = np.array([3000.0, 5000.0, 0.5e6])  # pi_0911 §3.5, M order
SORTED_TIERS = sorted(TIERS)
LAT = np.round(np.asarray(STAGE2_LATTICE, float), 10)
MC_SEED = 20261006          # threshold MC: constant, no round offset
ACQ_SEED_BASE = 20261006    # acquisition seed = base + round index
HARD_CAP = 4                # refuse round 5
BASE_WAVES = ["stage2_C_n0", "stage2_C_n0b"]
BOT = ["-c", "user.name=bo-bot", "-c", "user.email=bo-bot@noreply.github.com"]


def campaign_root() -> str:
    return os.environ.get("CAMPAIGN_ROOT") or _OWN_CAMPAIGN


def bo_dir(root: str) -> str:
    return os.path.join(root, "analysis", "bo_stage2")


def repo_root(root: str) -> str:
    return os.path.abspath(os.path.join(root, "..", ".."))


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _step(root: str, msg: str) -> None:
    """Breadcrumb for the WEDGED trap; also printed."""
    print(f"STEP: {msg}", flush=True)
    with open(os.path.join(bo_dir(root), "last_step.txt"), "w") as f:
        f.write(f"{_now()} round={os.environ.get('BO_ROUND', '?')}: {msg}\n")


# --------------------------------------------------------------------------- #
# data
# --------------------------------------------------------------------------- #

def _load_wave_xy(root: str, wave: str) -> tuple[np.ndarray, np.ndarray]:
    wdir = os.path.join(root, "waves", wave)
    dm = pd.read_csv(os.path.join(wdir, "design_matrix.csv"))
    ob = pd.read_csv(os.path.join(wdir, "objectives.csv"))
    df = dm.merge(ob[["index"] + M_COLS], on="index", validate="1:1")
    X = df[[f"{t}_omega" for t in SORTED_TIERS]].to_numpy(float)
    Y = df[M_COLS].to_numpy(float)
    return X, Y


def load_training(root: str, upto_round: int) -> tuple[np.ndarray, np.ndarray]:
    """The 32 in-box points + each completed round's 8 (prompt-pinned:
    backfill/pairgrid/contour/sweep carry ABSENT tiers — never training)."""
    xs, ys = [], []
    for w in BASE_WAVES:
        X, Y = _load_wave_xy(root, w)
        xs.append(X); ys.append(Y)
    for k in range(1, upto_round + 1):
        X, Y = _load_wave_xy(root, f"bo_C_r{k}")
        xs.append(X); ys.append(Y)
    X, Y = np.vstack(xs), np.vstack(ys)
    assert np.isfinite(X).all() and np.isfinite(Y).all()
    return X, Y


def lattice_candidates() -> np.ndarray:
    """The full 9^6 product, from the same STAGE2_LATTICE floats as the
    manifests (NO snapping anywhere)."""
    return np.array(list(itertools.product(LAT, repeat=6)), dtype=float)


def assert_on_lattice(designs: np.ndarray) -> None:
    for row in np.atleast_2d(designs):
        for w in row:
            assert np.isclose(LAT, w, atol=1e-12).any(), f"off-lattice {w!r}"


# --------------------------------------------------------------------------- #
# prediction / grading GPs (layer ii — per-objective, floored likelihoods)
# --------------------------------------------------------------------------- #

class PredGP:
    def __init__(self, X: np.ndarray, y: np.ndarray, floor: float):
        self.mx = X.mean(axis=0)
        self.sx = np.where(X.std(axis=0) <= 0, 1.0, X.std(axis=0))
        self.my = float(y.mean())
        self.sy = float(np.std(y, ddof=0)) or 1.0
        floor_var = (floor / self.sy) ** 2  # gpytorch noise is a VARIANCE
        tx = torch.tensor((X - self.mx) / self.sx, dtype=torch.float32)
        ty = torch.tensor((y - self.my) / self.sy, dtype=torch.float32)
        kernel = gpytorch.kernels.ScaleKernel(
            gpytorch.kernels.MaternKernel(nu=2.5, ard_num_dims=X.shape[1]))
        self.lik = gpytorch.likelihoods.GaussianLikelihood(
            noise_constraint=GreaterThan(floor_var))
        self.model = GPRegressionModel(tx, ty, self.lik, kernel)
        train_gp(self.model, self.lik, tx, ty)
        self.model.eval(); self.lik.eval()
        self._tx, self._ty = tx, ty

    def predict(self, Xq: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """Physical-unit posterior mean and NOISE-INCLUSIVE predictive sd."""
        xq = torch.tensor((np.atleast_2d(Xq) - self.mx) / self.sx,
                          dtype=torch.float32)
        with torch.no_grad(), gpytorch.settings.fast_pred_var():
            post = self.lik(self.model(xq))
            mean = post.mean.numpy() * self.sy + self.my
            sd = post.stddev.numpy() * self.sy
        return mean, sd

    def loo_residuals(self) -> np.ndarray:
        """Closed-form LOO residuals (standardized y units)."""
        with torch.no_grad():
            K = self.model.covar_module(self._tx).evaluate()
            Kn = K + self.lik.noise * torch.eye(len(self._tx), dtype=K.dtype)
            Ki = torch.linalg.inv(Kn)
            alpha = Ki @ (self._ty - self._ty.mean())
            return (alpha / Ki.diagonal()).numpy()


def fit_prediction_gps(X: np.ndarray, Y: np.ndarray) -> list[PredGP]:
    return [PredGP(X, Y[:, j], FLOORS[j]) for j in range(len(M_COLS))]


def write_predictions(wave_dir: str, designs: np.ndarray,
                      gps: list[PredGP]) -> str:
    rows = {"index": np.arange(1, len(designs) + 1)}
    for j, col in enumerate(M_COLS):
        mean, sd = gps[j].predict(designs)
        rows[f"{col}_pred_mean"] = mean
        rows[f"{col}_pred_sd"] = sd
    path = os.path.join(wave_dir, "predictions.csv")
    pd.DataFrame(rows).to_csv(path, index=False)
    return path


# --------------------------------------------------------------------------- #
# ledger / round log (ONE writer)
# --------------------------------------------------------------------------- #

def ledger_path(root): return os.path.join(bo_dir(root), "ledger.json")
def records_path(root): return os.path.join(bo_dir(root), "round_records.json")
def round_log_path(root): return os.path.join(bo_dir(root), "ROUND_LOG.md")


def load_ledger(root: str) -> dict:
    with open(ledger_path(root)) as f:
        led = json.load(f)
    thr = led["threshold"]
    assert np.isfinite(thr) and thr > 0, f"bad stopping threshold {thr!r}"
    return led


def save_ledger(root: str, led: dict) -> None:
    hvs = [e["hv"] for e in led["entries"]]
    assert all(b >= a - 1e-9 for a, b in zip(hvs, hvs[1:])), \
        "ledger HV must be non-decreasing"
    with open(ledger_path(root), "w") as f:
        json.dump(led, f, indent=2)
        f.write("\n")


ROUND_LOG_HEADER = """# Stage-2 BO ROUND_LOG (prompt 30 — q-ParEGO, scenario C, fully automated)

**Kay's standing card** — stop NOW:
`touch /groups/adowling/ylu28/RTS-GMLC/trial_0826/campaign/analysis/bo_stage2/STOP_BO`
on the CRC clone, then `qdel <array> <collector> <acq>` from the latest
`SUBMITTED r<k>:` line below. **Silent-death watch: no email of ANY kind
for 36 h => re-invoke the session to diagnose; never resubmit by hand.**
Manual recovery after WEDGED: push by hand + qsub the recorded triple —
never re-run acquire_next for a round that already proposed.

g1 note: inside the Stage-2 box nuclear omega >= 0.05 always, so option
(c)'s add-back is the same +$28.188M constant for every design — dominance
relations and acquisition rankings are invariant. Absolute costs below
carry the "pending g1 ruling" caveat; re-level when the PI rules.
"""


def write_round_section(root: str, k: int, updates: dict) -> dict:
    """THE one writer: merge `updates` into round k's record (JSON source of
    truth) and surgically rewrite its marked section in ROUND_LOG.md."""
    recs = {}
    if os.path.isfile(records_path(root)):
        with open(records_path(root)) as f:
            recs = json.load(f)
    rec = recs.get(str(k), {"round": k})
    rec.update(updates)
    recs[str(k)] = rec
    with open(records_path(root), "w") as f:
        json.dump(recs, f, indent=2, default=float)
        f.write("\n")

    lines = [f"<!-- BEGIN r{k} -->", f"## Round {k}"]
    for key in ("proposed_at", "acq_seed", "bo_gp_sha", "predictions",
                "graded_at", "cumulative_hv", "gain", "threshold",
                "n_outside_ref", "decision"):
        if key in rec:
            lines.append(f"- {key}: {rec[key]}")
    if "weights" in rec:
        lines.append("- weights (8 x M, Dirichlet(1) draws):")
        for w in rec["weights"]:
            lines.append(f"    - [{', '.join(f'{v:.4f}' for v in w)}]")
    if "designs" in rec:
        lines.append(f"- designs (omega, tiers {SORTED_TIERS}):")
        for row in rec["designs"]:
            lines.append(f"    - [{', '.join(f'{v:.5f}' for v in row)}]")
    if "calibration" in rec:
        lines.append(f"- calibration z-stats: {json.dumps(rec['calibration'])}")
    if "notes" in rec:
        lines.append(f"- notes: {rec['notes']}")
    lines.append(f"<!-- END r{k} -->")
    block = "\n".join(lines) + "\n"

    path = round_log_path(root)
    text = open(path).read() if os.path.isfile(path) else ROUND_LOG_HEADER
    pat = re.compile(rf"<!-- BEGIN r{k} -->.*?<!-- END r{k} -->\n",
                     flags=re.DOTALL)
    text = pat.sub(block, text) if pat.search(text) else text + "\n" + block
    with open(path, "w") as f:
        f.write(text)
    return rec


def round_section_exists(root: str, k: int) -> bool:
    if not os.path.isfile(records_path(root)):
        return False
    with open(records_path(root)) as f:
        return str(k) in json.load(f)


# --------------------------------------------------------------------------- #
# git / qsub plumbing
# --------------------------------------------------------------------------- #

def _git(root: str, *args: str, bot: bool = False,
         check: bool = True) -> subprocess.CompletedProcess:
    cmd = ["git", "-C", repo_root(root)] + (BOT if bot else []) + list(args)
    return subprocess.run(cmd, capture_output=True, text=True, check=check)


def push_with_retries(root: str) -> None:
    for attempt in range(1, 6):
        if _git(root, "push", "origin", "d6", check=False).returncode == 0:
            return
        print(f"push rejected (attempt {attempt}/5) — rebase and retry")
        time.sleep(30 + np.random.default_rng().integers(60))
        _git(root, "pull", "--rebase", "--autostash", "origin", "d6",
             check=False)
    _git(root, "push", "origin", "d6")  # raises on final failure


def commit_paths(root: str, paths: list[str], msg: str) -> None:
    _git(root, "add", "--", *paths)
    r = _git(root, "commit", "-m", msg, bot=True, check=False)
    if r.returncode != 0 and "nothing to commit" not in r.stdout + r.stderr:
        raise RuntimeError(f"git commit failed: {r.stdout}{r.stderr}")


def qstat_foreign_bo_jobs() -> list[str]:
    """Names of running bo_C_r jobs excluding our own $JOB_ID."""
    if shutil.which("qstat") is None:
        return []
    out = subprocess.run(["qstat", "-u", os.environ.get("USER", "ylu28")],
                         capture_output=True, text=True).stdout
    own = os.environ.get("JOB_ID", "")
    hits = []
    for line in out.splitlines():
        if "bo_C_r" in line and (not own or not line.strip().startswith(own)):
            hits.append(line.strip())
    return hits


def write_marker(root: str, name: str, body: str, push: bool = True) -> None:
    path = os.path.join(bo_dir(root), name)
    with open(path, "w") as f:
        f.write(body)
    try:
        commit_paths(root, [path], f"bo-bot: {name}")
        if push:
            push_with_retries(root)
    except Exception as exc:  # marker must land locally even if push fails
        print(f"marker push failed (marker is on disk): {exc}")


# --------------------------------------------------------------------------- #
# T1: init (ref + threshold + ledger entry 0)
# --------------------------------------------------------------------------- #

def cmd_init(root: str, bo_gp_sha: str) -> None:
    os.makedirs(bo_dir(root), exist_ok=True)
    X, Y = load_training(root, 0)
    assert X.shape == (32, 6) and Y.shape == (32, 3)
    assert_on_lattice(X)
    ref = Y.max(axis=0) + 0.1 * (Y.max(axis=0) - Y.min(axis=0))
    hv0 = hypervolume_exact(Y, ref)

    rng = np.random.default_rng(MC_SEED)
    hvs = np.empty(1000)
    for i in range(1000):  # perturb ALL 32 points per draw, no clipping
        hvs[i] = hypervolume_exact(Y + rng.normal(0.0, FLOORS, size=Y.shape),
                                   ref)
    threshold = float(np.std(hvs, ddof=0))
    assert np.isfinite(threshold) and threshold > 0

    led = {"ref_point": [float(v) for v in ref], "threshold": threshold,
           "mc_seed": MC_SEED, "acq_seed_base": ACQ_SEED_BASE,
           "bo_gp_sha": bo_gp_sha, "m_cols": M_COLS,
           "floors": [float(v) for v in FLOORS], "hard_cap": HARD_CAP,
           "entries": [{"round": 0, "n": 32, "hv": float(hv0), "gain": None,
                        "n_outside_ref": 0, "decision": "start",
                        "at": _now()}]}
    save_ledger(root, led)
    if not os.path.isfile(round_log_path(root)):
        with open(round_log_path(root), "w") as f:
            f.write(ROUND_LOG_HEADER)
    print(f"init: hv0={hv0:.6g} ref={ref} threshold={threshold:.6g}")


# --------------------------------------------------------------------------- #
# propose round k (used by T1 for r1 and by run_round for k+1)
# --------------------------------------------------------------------------- #

def propose_round(root: str, k: int) -> str:
    led = load_ledger(root)
    _step(root, f"propose r{k}: loading training data")
    X, Y = load_training(root, k - 1)
    _step(root, f"propose r{k}: fitting prediction GPs on n={len(X)}")
    gps = fit_prediction_gps(X, Y)
    _step(root, f"propose r{k}: acquisition (q-ParEGO, candidates mode)")
    seed = led["acq_seed_base"] + k
    batch = propose_qparego_batch(X, Y, q=8, candidates=lattice_candidates(),
                                  seed=seed)
    designs = np.asarray(batch["x_batch"], float)
    assert designs.shape == (8, 6), designs.shape
    assert_on_lattice(designs)
    keys = {tuple(r) for r in designs.round(10).tolist()}
    assert len(keys) == 8, "duplicate designs in batch"
    seen = {tuple(r) for r in X.round(10).tolist()}
    assert not (keys & seen), "acquisition re-proposed an evaluated design"

    _step(root, f"propose r{k}: building wave + predictions")
    wave_dir = make_batches.build_bo_round(
        k, designs,
        manifest_extra={"weights": batch["weights"].tolist(),
                        "bo_gp_sha": led["bo_gp_sha"], "acq_seed": seed},
        waves_root=os.path.join(root, "waves"))
    pred_path = write_predictions(wave_dir, designs, gps)
    write_round_section(root, k, {
        "proposed_at": _now(), "acq_seed": seed,
        "bo_gp_sha": led["bo_gp_sha"],
        "weights": batch["weights"].tolist(),
        "designs": designs.tolist(),
        "predictions": os.path.relpath(pred_path, root),
        "threshold": led["threshold"], "decision": "proposed"})
    return wave_dir


# --------------------------------------------------------------------------- #
# the unattended round (contract steps 2-7)
# --------------------------------------------------------------------------- #

def ingest_gate(root: str, k: int) -> tuple[bool, str]:
    wdir = os.path.join(root, "waves", f"bo_C_r{k}")
    import glob as _glob
    if _glob.glob(os.path.join(wdir, "FAILED_*")):
        return False, "collector FAILED marker present"
    obj = os.path.join(wdir, "objectives.csv")
    if not os.path.isfile(obj):
        return False, "objectives.csv missing"
    ob = pd.read_csv(obj)
    if sorted(ob["index"]) != list(range(1, 9)):
        return False, f"indices {sorted(ob['index'])} != 1..8"
    if not np.isfinite(ob[M_COLS].to_numpy(float)).all():
        return False, "non-finite objective values"
    dm = pd.read_csv(os.path.join(wdir, "design_matrix.csv"))
    merged = dm.merge(ob, on="index", suffixes=("", "_ob"))
    if len(merged) != 8:
        return False, "index set mismatch vs design_matrix"
    for t in SORTED_TIERS:
        col = f"{t}_omega"
        if col + "_ob" in merged and not np.allclose(
                merged[col], merged[col + "_ob"], atol=1e-12):
            return False, f"design column {col} mismatch (wrong-wave/stale runs?)"
    return True, "ok"


def run_round(root: str, k: int) -> int:
    _step(root, f"run r{k}: git pull")
    _git(root, "pull", "--rebase", "--autostash", "origin", "d6", check=False)

    if os.path.isfile(os.path.join(bo_dir(root), "STOP_BO")):
        write_marker(root, "BO_DONE.md",
                     f"# BO_DONE\n\nreason: STOP_BO found at round {k} "
                     f"({_now()}). Graceful abort; nothing submitted.\n")
        return 0

    _step(root, f"run r{k}: ingest gate")
    ok, why = ingest_gate(root, k)
    wdir = os.path.join(root, "waves", f"bo_C_r{k}")
    if not ok:
        write_marker(root, f"FAILED_bo_r{k}.md",
                     f"# FAILED — round {k} ingest gate\n\nreason: {why}\n"
                     f"at: {_now()}\nNothing was submitted. See ROUND_LOG "
                     "header for the recovery recipe.\n")
        return 0
    # collector may have died post-write pre-push: commit objectives ourselves
    st = _git(root, "status", "--porcelain", "--",
              os.path.join(wdir, "objectives.csv")).stdout.strip()
    if st:
        commit_paths(root, [os.path.join(wdir, "objectives.csv")],
                     f"bo-bot: bo_C_r{k} objectives (collector push recovery)")

    _step(root, f"run r{k}: idempotency guards")
    guard_msgs = []
    if round_section_exists(root, k + 1):
        guard_msgs.append(f"round {k + 1} section already exists")
    if os.path.exists(os.path.join(root, "waves", f"bo_C_r{k + 1}")):
        guard_msgs.append(f"waves/bo_C_r{k + 1} already exists")
    foreign = qstat_foreign_bo_jobs()
    if foreign:
        guard_msgs.append(f"foreign bo_C jobs in qstat: {foreign}")
    if guard_msgs:
        write_marker(root, f"FAILED_bo_r{k}.md",
                     "# FAILED — double-spend guard\n\n- "
                     + "\n- ".join(guard_msgs)
                     + f"\n\nat: {_now()}\nNothing was submitted.\n")
        return 0

    _step(root, f"run r{k}: grading")
    led = load_ledger(root)
    ref = np.asarray(led["ref_point"], float)
    _, Yk = _load_wave_xy(root, f"bo_C_r{k}")
    preds = pd.read_csv(os.path.join(wdir, "predictions.csv"))
    calib = {}
    for col in M_COLS:
        z = ((Yk[:, M_COLS.index(col)] - preds[f"{col}_pred_mean"])
             / preds[f"{col}_pred_sd"]).to_numpy(float)
        calib[col] = {"mean_z": round(float(z.mean()), 3),
                      "rms_z": round(float(np.sqrt((z ** 2).mean())), 3),
                      "cov95": int((np.abs(z) <= 1.96).sum())}
    _, Ycum = load_training(root, k)
    n_out = int((~np.all(Ycum < ref, axis=1)).sum())
    hv = float(hypervolume_exact(Ycum, ref))
    prev = led["entries"][-1]
    gain = hv - prev["hv"]
    led["entries"].append({"round": k, "n": int(len(Ycum)), "hv": hv,
                           "gain": gain, "n_outside_ref": n_out,
                           "decision": "graded", "at": _now()})
    save_ledger(root, led)
    write_round_section(root, k, {
        "graded_at": _now(), "cumulative_hv": hv, "gain": gain,
        "n_outside_ref": n_out, "calibration": calib,
        "realized": Yk.tolist(), "decision": "graded"})

    _step(root, f"run r{k}: stop checks")
    gains = [e["gain"] for e in led["entries"] if e["gain"] is not None]
    thr = led["threshold"]
    low2 = len(gains) >= 2 and gains[-1] < thr and gains[-2] < thr
    if k + 1 > led["hard_cap"]:
        reason = f"hard cap: refusing round {k + 1} (cap {led['hard_cap']})"
    elif low2:
        reason = (f"stopping rule: HV gain < threshold ({thr:.6g}) for 2 "
                  f"consecutive rounds (gains {gains[-2]:.6g}, {gains[-1]:.6g})")
    else:
        reason = None
    if reason:
        led["entries"][-1]["decision"] = "stop"
        save_ledger(root, led)
        write_round_section(root, k, {"decision": f"STOP — {reason}"})
        body = (f"# BO_DONE\n\nreason: {reason}\nat: {_now()}\n\nCumulative "
                f"HV trajectory: {[round(e['hv'], 6) for e in led['entries']]}\n")
        with open(os.path.join(bo_dir(root), "BO_DONE.md"), "w") as f:
            f.write(body)
        commit_paths(root, [bo_dir(root), os.path.join(root, "waves", f"bo_C_r{k}")],
                     f"bo-bot: round {k} graded — BO_DONE ({reason.split(':')[0]})")
        push_with_retries(root)
        return 0

    _step(root, f"run r{k}: proposing round {k + 1}")
    next_wave = propose_round(root, k + 1)
    write_round_section(root, k, {"decision": f"continue -> r{k + 1}"})

    _step(root, f"run r{k}: committing full round record BEFORE submitting")
    commit_paths(root,
                 [bo_dir(root), next_wave,
                  os.path.join(root, "waves", f"bo_C_r{k}")],
                 f"bo-bot: round {k} graded (hv={hv:.6g}, gain={gain:.6g}) "
                 f"+ r{k + 1} proposed")
    push_with_retries(root)  # exhaustion raises -> ERR trap -> WEDGED

    _step(root, f"run r{k}: submitting r{k + 1} triple")
    subprocess.run(["bash", os.path.join(next_wave, "submit_this.sh")],
                   check=True)
    log_text = open(round_log_path(root)).read()
    if f"SUBMITTED r{k + 1}:" not in log_text:
        raise RuntimeError(
            f"submit_this.sh ran but no 'SUBMITTED r{k + 1}:' line landed in "
            "ROUND_LOG.md — treat as not submitted (WEDGED)")
    _step(root, f"run r{k}: done")
    return 0


# --------------------------------------------------------------------------- #
# backfill sensitivity (T1, report-only)
# --------------------------------------------------------------------------- #

def backfill_sensitivity(root: str) -> str:
    X32, Y32 = load_training(root, 0)
    Xb, Yb = _load_wave_xy(root, "stage2_backfill_C")
    Xb = np.nan_to_num(Xb, nan=0.0)  # absent tiers -> 0 MW (outside the box)
    lines = ["# Backfill sensitivity (prompt 30, round-1-only, REPORT-ONLY)",
             "", "LOO RMSE (closed form) on the 32 in-box points, prediction",
             "GPs trained on (a) the 32 alone vs (b) 32 + 10 backfill rows",
             "(absent tiers encoded 0). Never switch training sets without",
             "Kay.", ""]
    for j, col in enumerate(M_COLS):
        a = PredGP(X32, Y32[:, j], FLOORS[j])
        rms_a = float(np.sqrt((a.loo_residuals() ** 2).mean())) * a.sy
        b = PredGP(np.vstack([X32, Xb]), np.r_[Y32[:, j], Yb[:, j]], FLOORS[j])
        rms_b = float(np.sqrt((b.loo_residuals()[:32] ** 2).mean())) * b.sy
        lines.append(f"- {col}: LOO RMSE 32-only = {rms_a:,.1f}; "
                     f"with backfill = {rms_b:,.1f} "
                     f"(delta {rms_b - rms_a:+,.1f}; floor {FLOORS[j]:,.0f})")
    path = os.path.join(bo_dir(root), "backfill_sensitivity.md")
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")
    return path


# --------------------------------------------------------------------------- #

def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)
    pi = sub.add_parser("init"); pi.add_argument("--bo-gp-sha", required=True)
    pp = sub.add_parser("propose"); pp.add_argument("--round", type=int, required=True)
    pr = sub.add_parser("run"); pr.add_argument("--round", type=int, required=True)
    sub.add_parser("backfill-check")
    args = p.parse_args(argv)
    root = campaign_root()
    torch.manual_seed(0)
    if args.cmd == "init":
        cmd_init(root, args.bo_gp_sha)
    elif args.cmd == "propose":
        print("wave:", propose_round(root, args.round))
    elif args.cmd == "run":
        os.environ.setdefault("BO_ROUND", str(args.round))
        return run_round(root, args.round)
    elif args.cmd == "backfill-check":
        print("written:", backfill_sensitivity(root))
    return 0


if __name__ == "__main__":
    sys.exit(main())
