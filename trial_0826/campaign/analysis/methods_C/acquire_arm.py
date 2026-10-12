"""Prompt 35 §3.1 — the prompt-30 acquisition brain generalized by an ARM config.

NO algorithm change: the q-ParEGO proposal, the prediction/grading GPs, the
lattice and the chunked-EI evaluation patch are IMPORTED from the frozen
`analysis/bo_stage2/acquire_next.py` (importing it applies the same
import-site EI patch). Everything campaign-specific is read from
`analysis/methods_C/arms.json` instead of being hard-coded:

    prompt-30 hard-coded item          ->  here
    bo_dir / last_step.txt / markers   ->  arm["dir"] (per arm)
    BASE_WAVES                         ->  arm["base_waves"]
    f"bo_C_r{k}" (load/ingest/guards)  ->  round_wave(cfg, arm, k)
    bo_wave_name in build_bo_round     ->  make_batches.build_methods_round(name)
    ROUND_LOG_HEADER ledger path       ->  per-arm header
    acquire_job.sh BO_DIR/env/SHA      ->  acquire_arm_job.sh reads ARM + arms.json

Differences in BEHAVIOUR (all pre-registered in prompt 35):
  * `run` REQUIRES --no-submit: grade -> propose -> commit -> push -> STOP.
    The compute node never calls a submit script (the r1 WEDGE cause).
  * stop_rule "record_only": grade, log would_stop + gain in tau units,
    continue to hard_cap (4). The prompt-30 P1 BO_DONE record stands.
  * round 0 (`run --round 0`): init the arm ledger if missing, then propose r1.
  * double-spend guard matches the FULL job name methods_C_<arm>_r{k+1} via
    `qstat -r` (plain qstat truncates names); git steps hold an flock
    (parallel acquisition jobs share one CRC clone).
"""

from __future__ import annotations

import argparse
import contextlib
import fcntl
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
sys.path.insert(0, os.path.join(_OWN_CAMPAIGN, "analysis", "bo_stage2"))
sys.path.insert(0, _OWN_CAMPAIGN)

import acquire_next as an  # noqa: E402  (frozen prompt-30 brain; applies the EI patch)
import gpytorch  # noqa: E402
import torch  # noqa: E402
import make_batches  # noqa: E402

M_COLS, FLOORS, SORTED_TIERS = an.M_COLS, an.FLOORS, an.SORTED_TIERS
hypervolume_exact = an.hypervolume_exact
BOT = ["-c", "user.name=methods-bot", "-c", "user.email=methods-bot@noreply.github.com"]
LOCK_NAME = "methods_C.flock"


def campaign_root() -> str:
    return os.environ.get("CAMPAIGN_ROOT") or _OWN_CAMPAIGN


def repo_root(root: str) -> str:
    return os.path.abspath(os.path.join(root, "..", ".."))


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


# --------------------------------------------------------------------------- #
# ARM config
# --------------------------------------------------------------------------- #

def config_path(root: str) -> str:
    return os.path.join(root, "analysis", "methods_C", "arms.json")


def load_config(root: str) -> dict:
    with open(config_path(root)) as f:
        return json.load(f)


def arm_cfg(cfg: dict, arm: str) -> dict:
    if arm not in cfg["arms"]:
        raise SystemExit(f"unknown arm {arm!r}; choose from {list(cfg['arms'])}")
    return cfg["arms"][arm]


def arm_dir(root: str, cfg: dict, arm: str) -> str:
    return os.path.join(root, arm_cfg(cfg, arm)["dir"])


def round_wave(cfg: dict, arm: str, k: int) -> str:
    a = arm_cfg(cfg, arm)
    return a["round_waves"].get(str(k)) or a["round_wave_pattern"].format(k=k)


def acq_seed(cfg: dict, arm: str, k: int) -> int:
    return int(cfg["acq_seed_base"] + 100 * arm_cfg(cfg, arm)["seed_id"] + k)


def acq_job_name(arm: str, k_next: int) -> str:
    """The acquisition job that CREATES round k_next (grades k_next - 1)."""
    return f"methods_C_{arm}_r{k_next}"


def _step(root, cfg, arm, msg):
    print(f"STEP: {msg}", flush=True)
    os.makedirs(arm_dir(root, cfg, arm), exist_ok=True)
    with open(os.path.join(arm_dir(root, cfg, arm), "last_step.txt"), "w") as f:
        f.write(f"{_now()} arm={arm} round={os.environ.get('BO_ROUND', '?')}: {msg}\n")


# --------------------------------------------------------------------------- #
# data
# --------------------------------------------------------------------------- #

def load_wave_xy(root: str, wave: str):
    return an._load_wave_xy(root, wave)


def load_training(root: str, cfg: dict, arm: str, upto_round: int):
    a = arm_cfg(cfg, arm)
    xs, ys = [], []
    for w in a["base_waves"]:
        X, Y = load_wave_xy(root, w)
        xs.append(X); ys.append(Y)
    for k in range(1, upto_round + 1):
        X, Y = load_wave_xy(root, round_wave(cfg, arm, k))
        xs.append(X); ys.append(Y)
    X, Y = np.vstack(xs), np.vstack(ys)
    assert np.isfinite(X).all() and np.isfinite(Y).all()
    return X, Y


# --------------------------------------------------------------------------- #
# ledger / round log (ONE writer per arm)
# --------------------------------------------------------------------------- #

def ledger_path(root, cfg, arm): return os.path.join(arm_dir(root, cfg, arm), "ledger.json")
def records_path(root, cfg, arm): return os.path.join(arm_dir(root, cfg, arm), "round_records.json")
def round_log_path(root, cfg, arm): return os.path.join(arm_dir(root, cfg, arm), "ROUND_LOG.md")


def load_ledger(root, cfg, arm) -> dict:
    with open(ledger_path(root, cfg, arm)) as f:
        led = json.load(f)
    thr = led["threshold"]
    assert np.isfinite(thr) and thr > 0, f"bad threshold {thr!r}"
    return led


def save_ledger(root, cfg, arm, led) -> None:
    hvs = [e["hv"] for e in led["entries"]]
    assert all(b >= a - 1e-9 for a, b in zip(hvs, hvs[1:])), "ledger HV must be non-decreasing"
    with open(ledger_path(root, cfg, arm), "w") as f:
        json.dump(led, f, indent=2)
        f.write("\n")


def round_log_header(cfg, arm) -> str:
    a = arm_cfg(cfg, arm)
    return (f"# methods_C arm {arm} — ROUND_LOG (prompt 35; acq = {a['acq']}, "
            f"base = {a['base_waves']}, seed_id = {a['seed_id']})\n\n"
            f"Ledger: `{a['dir']}/ledger.json`. stop_rule = record_only: the rule is\n"
            "graded and logged (would_stop, gain in tau units) but never acted on;\n"
            f"every arm runs to hard_cap = {cfg['hard_cap']}. Acquisition jobs never\n"
            "submit (--no-submit); Kay submits from bastion via submit_ready.sh.\n"
            f"Stop NOW: `touch {a['dir']}/STOP_{arm}` on the CRC clone, then qdel the\n"
            "arm's JIDs from methods_C/PROGRESS.md.\n")


def write_round_section(root, cfg, arm, k, updates) -> dict:
    recs = {}
    if os.path.isfile(records_path(root, cfg, arm)):
        with open(records_path(root, cfg, arm)) as f:
            recs = json.load(f)
    rec = recs.get(str(k), {"round": k})
    rec.update(updates)
    recs[str(k)] = rec
    with open(records_path(root, cfg, arm), "w") as f:
        json.dump(recs, f, indent=2, default=float)
        f.write("\n")
    lines = [f"<!-- BEGIN r{k} -->", f"## Round {k} ({round_wave(cfg, arm, k)})"]
    for key in ("proposed_at", "acq", "acq_seed", "bo_gp_sha", "botorch", "predictions",
                "graded_at", "cumulative_hv", "gain", "gain_tau", "threshold",
                "would_stop", "n_outside_ref", "decision"):
        if key in rec:
            lines.append(f"- {key}: {rec[key]}")
    if "weights" in rec:
        lines.append("- weights (8 x M, Dirichlet(1) draws):")
        lines += [f"    - [{', '.join(f'{v:.4f}' for v in w)}]" for w in rec["weights"]]
    if "designs" in rec:
        lines.append(f"- designs (omega, tiers {SORTED_TIERS}):")
        lines += [f"    - [{', '.join(f'{v:.5f}' for v in row)}]" for row in rec["designs"]]
    if "calibration" in rec:
        lines.append(f"- calibration z-stats: {json.dumps(rec['calibration'])}")
    lines.append(f"<!-- END r{k} -->")
    block = "\n".join(lines) + "\n"
    path = round_log_path(root, cfg, arm)
    text = open(path).read() if os.path.isfile(path) else round_log_header(cfg, arm)
    pat = re.compile(rf"<!-- BEGIN r{k} -->.*?<!-- END r{k} -->\n", flags=re.DOTALL)
    text = pat.sub(lambda _m: block, text) if pat.search(text) else text + "\n" + block
    with open(path, "w") as f:
        f.write(text)
    return rec


def round_record_exists(root, cfg, arm, k) -> bool:
    p = records_path(root, cfg, arm)
    if not os.path.isfile(p):
        return False
    with open(p) as f:
        return str(k) in json.load(f)


# --------------------------------------------------------------------------- #
# git / qstat plumbing (flock-serialized: parallel acq jobs share one clone)
# --------------------------------------------------------------------------- #

@contextlib.contextmanager
def repo_lock(root):
    gitdir = os.path.join(repo_root(root), ".git")
    path = os.path.join(gitdir if os.path.isdir(gitdir) else repo_root(root), LOCK_NAME)
    with open(path, "w") as fh:
        fcntl.flock(fh, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(fh, fcntl.LOCK_UN)


def _git(root, *args, bot=False, check=True):
    cmd = ["git", "-C", repo_root(root)] + (BOT if bot else []) + list(args)
    return subprocess.run(cmd, capture_output=True, text=True, check=check)


def _branch(root, cfg):
    return cfg.get("repo_branch", "d6")


def pull(root, cfg):
    with repo_lock(root):
        _git(root, "pull", "--rebase", "--autostash", "origin", _branch(root, cfg), check=False)


def commit_and_push(root, cfg, paths, msg, push=True):
    with repo_lock(root):
        _git(root, "add", "--", *paths)
        r = _git(root, "commit", "-m", msg, bot=True, check=False)
        if r.returncode != 0 and "nothing to commit" not in r.stdout + r.stderr:
            raise RuntimeError(f"git commit failed: {r.stdout}{r.stderr}")
        if not push:
            return
        br = _branch(root, cfg)
        for attempt in range(1, 6):
            if _git(root, "push", "origin", br, check=False).returncode == 0:
                return
            print(f"push rejected (attempt {attempt}/5) — rebase and retry")
            time.sleep(30 + np.random.default_rng().integers(60))
            _git(root, "pull", "--rebase", "--autostash", "origin", br, check=False)
        _git(root, "push", "origin", br)  # raises on final failure


def qstat_full_names() -> list[tuple[str, str]]:
    """(job_id, full job name) for the user's jobs, from `qstat -r`."""
    if shutil.which("qstat") is None:
        return []
    out = subprocess.run(["qstat", "-r", "-u", os.environ.get("USER", "ylu28")],
                         capture_output=True, text=True).stdout
    jobs, cur = [], None
    for line in out.splitlines():
        m = re.match(r"^\s*(\d+)\s", line)
        if m:
            cur = m.group(1)
        m = re.search(r"Full jobname:\s*(\S+)", line)
        if m and cur:
            jobs.append((cur, m.group(1)))
    return jobs


def foreign_jobs_named(name: str) -> list[str]:
    own = os.environ.get("JOB_ID", "")
    return [jid for jid, n in qstat_full_names() if n == name and jid != own]


def write_marker(root, cfg, arm, name, body, push=True):
    path = os.path.join(arm_dir(root, cfg, arm), name)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(body)
    try:
        commit_and_push(root, cfg, [path], f"methods-bot: {arm} {name}", push=push)
    except Exception as exc:  # marker must land locally even if push fails
        print(f"marker push failed (marker is on disk): {exc}")


# --------------------------------------------------------------------------- #
# init (per arm)
# --------------------------------------------------------------------------- #

def _mc_threshold(Y, ref):
    rng = np.random.default_rng(an.MC_SEED)
    hvs = np.empty(1000)
    for i in range(1000):  # identical to acquire_next.cmd_init
        hvs[i] = hypervolume_exact(Y + rng.normal(0.0, FLOORS, size=Y.shape), ref)
    return float(np.std(hvs, ddof=0))


def cmd_init(root, cfg, arm, bo_gp_sha):
    a = arm_cfg(cfg, arm)
    d = arm_dir(root, cfg, arm)
    os.makedirs(d, exist_ok=True)
    if os.path.exists(ledger_path(root, cfg, arm)):
        raise RuntimeError(f"REFUSED: {arm} ledger already exists")
    common = {"arm": arm, "acq": a["acq"], "seed_id": a["seed_id"],
              "stop_rule": cfg["stop_rule"], "hard_cap": cfg["hard_cap"],
              "acq_seed_base": cfg["acq_seed_base"], "m_cols": M_COLS,
              "floors": [float(v) for v in FLOORS], "mc_seed": an.MC_SEED,
              "init_at": _now()}
    if a["init"] == "copy_bo_stage2":
        src = os.path.join(root, "analysis", "bo_stage2")
        led = json.load(open(os.path.join(src, "ledger.json")))
        assert led["bo_gp_sha"] == bo_gp_sha, (led["bo_gp_sha"], bo_gp_sha)
        assert led["acq_seed_base"] == cfg["acq_seed_base"] and a["seed_id"] == 0
        recs = json.load(open(os.path.join(src, "round_records.json")))
        led.update(common)
        led["source"] = "copied from analysis/bo_stage2 (prompt 30); r2 'stop' = the LIVE decision (stands)"
        led["live_stop_round"] = 2
        save_ledger(root, cfg, arm, led)
        with open(records_path(root, cfg, arm), "w") as f:
            json.dump({k: v for k, v in recs.items() if k in ("1", "2")}, f, indent=2, default=float)
            f.write("\n")
        for k in (1, 2):
            write_round_section(root, cfg, arm, k, {})
        print(f"init {arm}: copied prompt-30 ledger (entries {len(led['entries'])}) + r1/r2 records")
        return
    X, Y = load_training(root, cfg, arm, 0)
    assert X.shape == (32, 6) and Y.shape == (32, 3), (X.shape, Y.shape)
    an.assert_on_lattice(X)
    if a["init"] == "copy_P1_ref":
        p1 = load_ledger(root, cfg, "P1")
        ref, thr = np.asarray(p1["ref_point"], float), float(p1["threshold"])
        source = "ref_point + threshold copied from P1 (R_frozen and tau_1 of S1)"
    elif a["init"] == "mc":
        ref = Y.max(axis=0) + 0.1 * (Y.max(axis=0) - Y.min(axis=0))
        thr = _mc_threshold(Y, ref)
        source = "R_frozen_k = nadir + 0.1 span of this arm's 32 starts; tau_k by the prompt-30 MC"
    else:
        raise ValueError(a["init"])
    hv0 = float(hypervolume_exact(Y, ref))
    led = {"ref_point": [float(v) for v in ref], "threshold": thr, "bo_gp_sha": bo_gp_sha,
           **common, "source": source,
           "entries": [{"round": 0, "n": 32, "hv": hv0, "gain": None, "n_outside_ref":
                        int((~np.all(Y < ref, axis=1)).sum()), "decision": "start", "at": _now()}]}
    save_ledger(root, cfg, arm, led)
    with open(round_log_path(root, cfg, arm), "w") as f:
        f.write(round_log_header(cfg, arm))
    print(f"init {arm}: hv0={hv0:.6g} ref={ref} threshold={thr:.6g} ({source})")


# --------------------------------------------------------------------------- #
# propose round k
# --------------------------------------------------------------------------- #

def _propose_designs(cfg, arm, X, Y, seed, led):
    a = arm_cfg(cfg, arm)
    q = cfg["q"]
    if a["acq"] == "qparego":
        with gpytorch.settings.fast_pred_var():  # exactly as acquire_next.propose_round
            batch = an.propose_qparego_batch(X, Y, q=q, candidates=an.lattice_candidates(), seed=seed)
        return np.asarray(batch["x_batch"], float), {"weights": batch["weights"].tolist()}
    if a["acq"] == "qnehvi":
        import botorch
        import qnehvi
        r = qnehvi.propose_qnehvi_batch(X, Y, an.lattice_candidates(), led["ref_point"],
                                        FLOORS, q=q, seed=seed)
        return np.asarray(r["x_batch"], float), {
            "botorch": botorch.__version__, "qnehvi_mc_samples": qnehvi.MC_SAMPLES,
            "qnehvi_seconds": round(float(r["seconds"]), 1)}
    raise ValueError(a["acq"])


def propose_round(root, cfg, arm, k) -> str:
    led = load_ledger(root, cfg, arm)
    _step(root, cfg, arm, f"propose r{k}: loading training data")
    X, Y = load_training(root, cfg, arm, k - 1)
    _step(root, cfg, arm, f"propose r{k}: fitting prediction GPs on n={len(X)}")
    gps = an.fit_prediction_gps(X, Y)
    seed = acq_seed(cfg, arm, k)
    _step(root, cfg, arm, f"propose r{k}: acquisition ({arm_cfg(cfg, arm)['acq']}, seed {seed})")
    designs, extra = _propose_designs(cfg, arm, X, Y, seed, led)
    q = cfg["q"]
    assert designs.shape == (q, 6), designs.shape
    an.assert_on_lattice(designs)
    keys = {tuple(r) for r in designs.round(10).tolist()}
    assert len(keys) == q, "duplicate designs in batch"
    assert not (keys & {tuple(r) for r in X.round(10).tolist()}), "re-proposed an evaluated design"
    _step(root, cfg, arm, f"propose r{k}: building wave + predictions")
    wave = round_wave(cfg, arm, k)
    wave_dir = make_batches.build_methods_round(
        wave, designs,
        manifest_extra={"methods_arm": arm, "methods_round": k, "acq": arm_cfg(cfg, arm)["acq"],
                        "bo_gp_sha": led["bo_gp_sha"], "acq_seed": seed, **extra},
        waves_root=os.path.join(root, "waves"))
    pred_path = an.write_predictions(wave_dir, designs, gps)
    write_round_section(root, cfg, arm, k, {
        "proposed_at": _now(), "acq": arm_cfg(cfg, arm)["acq"], "acq_seed": seed,
        "bo_gp_sha": led["bo_gp_sha"], **extra, "designs": designs.tolist(),
        "predictions": os.path.relpath(pred_path, root),
        "threshold": led["threshold"], "decision": "proposed"})
    return wave_dir


# --------------------------------------------------------------------------- #
# the round (grade k -> propose k+1 -> commit -> push -> STOP)
# --------------------------------------------------------------------------- #

def ingest_gate(root, cfg, arm, k):
    import glob
    wdir = os.path.join(root, "waves", round_wave(cfg, arm, k))
    q = cfg["q"]
    if glob.glob(os.path.join(wdir, "FAILED_*")):
        return False, "collector FAILED marker present"
    obj = os.path.join(wdir, "objectives.csv")
    if not os.path.isfile(obj):
        return False, "objectives.csv missing"
    ob = pd.read_csv(obj)
    if sorted(ob["index"]) != list(range(1, q + 1)):
        return False, f"indices {sorted(ob['index'])} != 1..{q}"
    if not np.isfinite(ob[M_COLS].to_numpy(float)).all():
        return False, "non-finite objective values"
    if not round_record_exists(root, cfg, arm, k):
        return False, f"no round-{k} record — wave of unknown provenance"
    dm = pd.read_csv(os.path.join(wdir, "design_matrix.csv"))
    proposed = np.asarray(json.load(open(records_path(root, cfg, arm)))[str(k)]["designs"], float)
    dm_x = dm.sort_values("index")[[f"{t}_omega" for t in SORTED_TIERS]].to_numpy(float)
    if not np.allclose(dm_x, proposed, atol=1e-12):
        return False, "design_matrix != proposed designs (wrong-wave/stale runs?)"
    return True, "ok"


def grade_round(root, cfg, arm, k) -> dict:
    led = load_ledger(root, cfg, arm)
    ref = np.asarray(led["ref_point"], float)
    wdir = os.path.join(root, "waves", round_wave(cfg, arm, k))
    _, Yk = load_wave_xy(root, round_wave(cfg, arm, k))
    preds = pd.read_csv(os.path.join(wdir, "predictions.csv"))
    calib = {}
    for col in M_COLS:
        z = ((Yk[:, M_COLS.index(col)] - preds[f"{col}_pred_mean"]) / preds[f"{col}_pred_sd"]).to_numpy(float)
        calib[col] = {"mean_z": round(float(z.mean()), 3), "rms_z": round(float(np.sqrt((z ** 2).mean())), 3),
                      "cov95": int((np.abs(z) <= 1.96).sum())}
    _, Ycum = load_training(root, cfg, arm, k)
    n_out = int((~np.all(Ycum < ref, axis=1)).sum())
    hv = float(hypervolume_exact(Ycum, ref))
    gain = hv - led["entries"][-1]["hv"]
    thr = led["threshold"]
    gains = [e["gain"] for e in led["entries"] if e["gain"] is not None] + [gain]
    would_stop = len(gains) >= 2 and gains[-1] < thr and gains[-2] < thr
    led["entries"].append({"round": k, "n": int(len(Ycum)), "hv": hv, "gain": gain,
                           "gain_tau": gain / thr, "would_stop": bool(would_stop),
                           "n_outside_ref": n_out, "decision": "graded (record_only)", "at": _now()})
    save_ledger(root, cfg, arm, led)
    write_round_section(root, cfg, arm, k, {
        "graded_at": _now(), "cumulative_hv": hv, "gain": gain, "gain_tau": gain / thr,
        "would_stop": bool(would_stop), "n_outside_ref": n_out, "calibration": calib,
        "realized": Yk.tolist(), "decision": "graded (record_only)"})
    return led


def run_round(root, cfg, arm, k, no_submit) -> int:
    if not no_submit:
        raise SystemExit("REFUSED: `run` requires --no-submit (compute nodes never qsub; prompt 35 §3.1)")
    d = arm_dir(root, cfg, arm)
    _step(root, cfg, arm, f"run r{k}: git pull")
    pull(root, cfg)
    if os.path.isfile(os.path.join(d, f"STOP_{arm}")):
        write_marker(root, cfg, arm, f"DONE_{arm}.md",
                     f"# DONE {arm}\n\nreason: STOP_{arm} found at round {k} ({_now()}). Nothing proposed.\n")
        return 0
    paths = [d]
    if k == 0:
        if not os.path.exists(ledger_path(root, cfg, arm)):
            _step(root, cfg, arm, "run r0: init")
            sha = subprocess.run(["git", "-C", os.environ["BOGP_CLONE"], "rev-parse", "HEAD"],
                                 capture_output=True, text=True, check=True).stdout.strip()
            cmd_init(root, cfg, arm, sha)
    else:
        _step(root, cfg, arm, f"run r{k}: ingest gate")
        ok, why = ingest_gate(root, cfg, arm, k)
        wdir = os.path.join(root, "waves", round_wave(cfg, arm, k))
        if not ok:
            write_marker(root, cfg, arm, f"FAILED_{arm}_r{k}.md",
                         f"# FAILED — {arm} round {k} ingest gate\n\nreason: {why}\nat: {_now()}\n"
                         "Nothing was proposed.\n")
            return 0
        paths.append(wdir)
    _step(root, cfg, arm, f"run r{k}: double-spend guards")
    guards = []
    if round_record_exists(root, cfg, arm, k + 1):
        guards.append(f"round {k + 1} record already exists")
    if os.path.exists(os.path.join(root, "waves", round_wave(cfg, arm, k + 1))) and k + 1 <= cfg["hard_cap"]:
        guards.append(f"waves/{round_wave(cfg, arm, k + 1)} already exists")
    foreign = foreign_jobs_named(acq_job_name(arm, k + 1))
    if foreign:
        guards.append(f"other jobs named {acq_job_name(arm, k + 1)}: {foreign}")
    if guards:
        write_marker(root, cfg, arm, f"FAILED_{arm}_r{k}.md",
                     "# FAILED — double-spend guard\n\n- " + "\n- ".join(guards)
                     + f"\n\nat: {_now()}\nNothing was proposed.\n")
        return 0
    if k >= 1:
        _step(root, cfg, arm, f"run r{k}: grading (record_only)")
        led = grade_round(root, cfg, arm, k)
        e = led["entries"][-1]
        if k >= cfg["hard_cap"]:
            body = (f"# DONE {arm}\n\nreason: hard_cap {cfg['hard_cap']} reached at round {k} ({_now()}).\n"
                    f"HV trajectory: {[round(x['hv'], 6) for x in led['entries']]}\n"
                    f"would_stop by round: {[x.get('would_stop') for x in led['entries']]}\n")
            with open(os.path.join(d, f"DONE_{arm}.md"), "w") as f:
                f.write(body)
            commit_and_push(root, cfg, paths,
                            f"methods-bot: {arm} r{k} graded (gain {e['gain_tau']:.2f} tau) — DONE (hard cap)")
            return 0
    _step(root, cfg, arm, f"run r{k}: proposing round {k + 1}")
    next_wave = propose_round(root, cfg, arm, k + 1)
    if k >= 1:
        write_round_section(root, cfg, arm, k, {"decision": f"graded (record_only) -> r{k + 1}"})
    _step(root, cfg, arm, f"run r{k}: commit + push, then STOP (--no-submit)")
    commit_and_push(root, cfg, paths + [next_wave],
                    f"methods-bot: {arm} " + (f"r{k} graded + " if k >= 1 else "init + ")
                    + f"r{k + 1} proposed ({round_wave(cfg, arm, k + 1)})")
    _step(root, cfg, arm, f"run r{k}: done (no submit — bastion submit_ready.sh picks it up)")
    return 0


# --------------------------------------------------------------------------- #

def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)
    pi = sub.add_parser("init"); pi.add_argument("--arm", required=True); pi.add_argument("--bo-gp-sha", required=True)
    pp = sub.add_parser("propose"); pp.add_argument("--arm", required=True); pp.add_argument("--round", type=int, required=True)
    pr = sub.add_parser("run"); pr.add_argument("--arm", required=True); pr.add_argument("--round", type=int, required=True)
    pr.add_argument("--no-submit", action="store_true")
    args = p.parse_args(argv)
    root = campaign_root()
    cfg = load_config(root)
    torch.manual_seed(0)
    if args.cmd == "init":
        cmd_init(root, cfg, args.arm, args.bo_gp_sha)
    elif args.cmd == "propose":
        print("wave:", propose_round(root, cfg, args.arm, args.round))
    elif args.cmd == "run":
        os.environ.setdefault("BO_ROUND", str(args.round))
        return run_round(root, cfg, args.arm, args.round, args.no_submit)
    return 0


if __name__ == "__main__":
    sys.exit(main())
