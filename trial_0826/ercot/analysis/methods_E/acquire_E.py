"""Prompt 55 — the ERCOT BO machinery: config-driven arms x seeds ("lanes"),
qNEHVI over the continuous per-site MW box, wave writer, ledger with the tau
rulers, calibration records, guardrail + SUSPECT handling, HALT files.

Ported from the RTS donor `trial_0826/campaign/analysis/methods_C/acquire_arm.py`
(prompt 35/49) with every lattice-bound line dropped (no `assert_on_lattice`,
no `lattice_candidates`, no `build_methods_round`, no omega-column parse) and
the data path replaced by the contract-6.1 loader. One lane = (arm, seed_id);
its files live in `analysis/methods_E/<arm>/s<seed>/`:

    ledger.json           R, tau rulers, guardrail_mode, violations, suspects, entries
    tau_init.json         the rulers as computed ONCE at init (equality-asserted every round)
    round_records.json    per-round proposal + grading record (one writer per lane)
    ROUND_LOG.md          human view of the records
    last_step.txt         breadcrumb
    HALT_FOR_DECISION.md  written by grade_round on >= 2 violations or >= 2 SUSPECT in one round;
                          propose/run REFUSE while it exists (Kay decides, then renames it)
    FAILED_r<k>.md        ingest gate (C1) or double-spend guard refusal; nothing proposed
    DONE.md               hard_cap reached (or STOP file found)
    STOP                  touch to stop the lane at its next run

Stop rule (form-agnostic, record_only): per round gain_k = HV_k - HV_{k-1}
over the accumulated lane set (SUSPECT and R1-violating runs EXCLUDED from HV
and gain), would_stop_k = (gain_k < tau) AND (gain_{k-1} < tau) under
tau_joint (headline) and tau_marginal (recorded), the joint-vs-marginal
sensitivity as a third column, first_fire_round per ruler. The machinery never
halts on the rule or on C2/C3; it halts ONLY per plan 1.2/1.3 (HALT FOR
DECISION) and stops at hard_cap. tau = 0 (all exact zero) -> would_stop never
fires: budget-cap-only, the cap governs.

Guardrails (plan 1.3): R1 shed > 1 MWh = VIOLATION (ledger-marked, excluded
from fronts/HV, kept in GP training); the round AFTER the first violation
flips guardrail_mode monitor -> constrain (constrained qNEHVI, shed GP
constraint shed <= 1 MWh); >= 2 violations in one round -> HALT. R2 reserve
shortfall > 2 x base = round flag, recorded, never halts, no acquisition role.
SUSPECT (S1-S3 via meta.suspect): excluded from HV, gain and (build choice,
disclosed) GP training; >= 2 in one round -> HALT.

Calibration (plan 6.4): C1 ingest fail-stop (all q runs present at the v3
identity, objectives finite, SUSPECT and shed checks run); C2 covered <= 4 of
8 for any objective; C3 >= 3 of 8 with |z| > 3 for any objective -> REVIEW
flags, record-only.

`run --round k --no-submit`: pull -> ingest gate -> guards -> grade k ->
propose k+1 -> commit (+ push) -> STOP. Compute nodes never qsub; Kay submits
with submit_ready_E.sh from the login node.
"""

from __future__ import annotations

import argparse
import contextlib
import fcntl
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import common_E as ce  # noqa: E402
import tau_E  # noqa: E402
import wave_writer_E as ww  # noqa: E402
from common_E import (acq_seed, arm_cfg, lane_dir, load_config, now, repo_root,  # noqa: E402
                      round_wave)

BOT = ["-c", "user.name=ercot-bot", "-c", "user.email=ercot-bot@noreply.github.com"]
LOCK_NAME = "methods_E.flock"
BANNED_FRAMINGS = (
    'From prompt 49 v2.1 section 2, verbatim:\n\n'
    '**Banned framings (pinned)**: "the rule now works" · "validated live" ·\n'
    '"rescued/fixed the rule" · "V1 beats / outperforms / confirms P1–N1" ·\n'
    'any V1-vs-arm HV comparison not expressed as "within/outside the\n'
    'prompt-35 claim-(ii) dispersion band" · describing a no-stop outcome\n'
    'as "convergence not reached".')


def _step(ldir, msg):
    print(f"STEP: {msg}", flush=True)
    os.makedirs(ldir, exist_ok=True)
    with open(os.path.join(ldir, "last_step.txt"), "w") as f:
        f.write(f"{now()} {msg}\n")


# --------------------------------------------------------------------------- #
# lane paths
# --------------------------------------------------------------------------- #

def ledger_path(ldir): return os.path.join(ldir, "ledger.json")
def records_path(ldir): return os.path.join(ldir, "round_records.json")
def round_log_path(ldir): return os.path.join(ldir, "ROUND_LOG.md")
def tau_init_path(ldir): return os.path.join(ldir, "tau_init.json")
def halt_path(ldir): return os.path.join(ldir, "HALT_FOR_DECISION.md")
def stop_path(ldir): return os.path.join(ldir, "STOP")
def done_path(ldir): return os.path.join(ldir, "DONE.md")


def load_ledger(ldir) -> dict:
    with open(ledger_path(ldir)) as f:
        led = json.load(f)
    for k in ("tau_joint", "tau_marginal"):
        assert np.isfinite(led["tau"][k]) and led["tau"][k] >= 0, (k, led["tau"][k])
    return led


def save_ledger(ldir, led) -> None:
    hvs = [e["hv"] for e in led["entries"]]
    assert all(b >= a - 1e-9 * max(1.0, abs(a)) for a, b in zip(hvs, hvs[1:])), "ledger HV must be non-decreasing"
    with open(ledger_path(ldir), "w") as f:
        json.dump(led, f, indent=2, default=float)
        f.write("\n")


def load_records(ldir) -> dict:
    p = records_path(ldir)
    if not os.path.isfile(p):
        return {}
    with open(p) as f:
        return json.load(f)


def round_record_exists(ldir, k) -> bool:
    return str(k) in load_records(ldir)


# --------------------------------------------------------------------------- #
# data (contract 6.1 loader; stub in Part A)
# --------------------------------------------------------------------------- #

class Lane:
    """Everything the lane needs that is derived from files: config, design
    space, committed configs, loader, start-set selection."""

    def __init__(self, root, cfg, arm, seed, loader=None):
        """`loader` = optional (load callable, source label) injected by a caller (prompt 66
        emulator: the real 54 loader for n0_E + emulated wave tables); default = common_E.get_loader."""
        self.root, self.cfg, self.arm, self.seed = root, cfg, arm, int(seed)
        self.a = arm_cfg(cfg, arm)
        self.dir = lane_dir(root, cfg, arm, seed)
        self.ds = ce.load_design_space(root, cfg)
        self.configs, self.configs_source = ce.committed_configs(root, cfg)
        if self.configs.get("E-D7_decided") is None and cfg.get("n0_tier_provisional") is not None:
            assert cfg.get("part") != "B", ("Part B: a provisional n0 tier is REFUSED — E-D7 must be decided in "
                                            "committed_configs.json (a real lane never runs on a provisional tier)")
        self.n0_tier = ce.n0_tier(self.configs, cfg.get("n0_tier_provisional"))
        self.n0_source = (f"committed_configs ({self.configs_source}) E-D7_decided"
                          if self.configs.get("E-D7_decided") is not None
                          else f"PROVISIONAL arms_E n0_tier_provisional = {self.n0_tier} (E-D7_decided null)")
        self.objectives = list(cfg["objectives"])
        for o in self.objectives:
            assert o in self.ds.objectives_json, f"objective {o} not in design_space_E.json objectives"
        self.gp_cfgs, self.gp_floors = ce.gp_cfg_and_floor(self.configs, self.objectives)
        self.load, self.loader_source = loader if loader is not None else ce.get_loader(root)
        if cfg.get("part") == "B":
            assert self.loader_source == "real", "Part B: the real loader (54) must be importable"
            assert self.configs_source == "real", "Part B: analysis/ercot_gp/committed_configs.json (54 B) required"
        self.violation_mwh = float(cfg["guardrails"]["R1"]["violation_mwh"])
        self.r2_flag_at = float(cfg["guardrails"]["R2"]["flag_at_mwh"])

    def wave(self, k):
        return round_wave(self.cfg, self.arm, self.seed, k)

    def _load(self, waves):
        X, U, Y, meta = self.load(waves, objectives=self.objectives,
                                  design_space=ce.design_space_path(self.root, self.cfg),
                                  extr=os.path.join(self.root, "extracts"),
                                  waves_dir=os.path.join(self.root, "waves"),
                                  floors={o: float(f) for o, f in zip(self.objectives, self.gp_floors)})
        for w in self.cfg.get("forbidden_training_waves", []):
            bad = [k for k in X.index if str(k).split(":")[0] == w or str(k).startswith(w + ":")]
            assert not bad, f"forbidden wave {w} in the training set (plan 4/7 baseline independence): {bad[:3]}"
        return X, U, Y, meta

    def start_set(self):
        """The nav prefix of base_waves (E-D7 tier): rows with sobol_index < n0_tier."""
        X, U, Y, meta = self._load(list(self.cfg["base_waves"]))
        sob = pd.to_numeric(meta["sobol_index"], errors="coerce")
        keep = sob.notna() & (sob < self.n0_tier)
        assert int(keep.sum()) == self.n0_tier, (
            f"start set: {int(keep.sum())} rows with sobol_index < {self.n0_tier} (need exactly {self.n0_tier}; "
            f"loaded {len(X)}, refused {meta.attrs.get('refused')})")
        order = np.argsort(sob[keep].to_numpy())
        idx = X.index[keep][order]
        return X.loc[idx], U.loc[idx], Y.loc[idx], meta.loc[idx], (X, U, Y, meta)

    def accumulated(self, upto_round):
        """Start set + rounds 1..upto_round. Returns dict with the masks."""
        X0, U0, Y0, m0, _ = self.start_set()
        parts = [(X0, U0, Y0, m0)]
        for k in range(1, upto_round + 1):
            Xk, Uk, Yk, mk = self._load([self.wave(k)])
            assert len(Xk) == self.cfg["q"], f"{self.wave(k)}: {len(Xk)} rows loaded (q = {self.cfg['q']})"
            parts.append((Xk, Uk, Yk, mk))
        X = pd.concat([p[0] for p in parts]); U = pd.concat([p[1] for p in parts])
        Y = pd.concat([p[2] for p in parts]); meta = pd.concat([p[3] for p in parts])
        assert X.index.is_unique, "duplicate keys in the accumulated set"
        assert np.isfinite(U.to_numpy(float)).all() and np.isfinite(Y.to_numpy(float)).all()
        suspect = meta["suspect"].astype(bool).to_numpy()
        viol = meta["R1"].astype(float).to_numpy() > self.violation_mwh
        train = ~suspect if not self.cfg["gp"].get("suspect_in_training", False) else np.ones(len(X), bool)
        if not self.cfg["gp"].get("violation_in_training", True):
            train &= ~viol
        return {"X": X, "U": U, "Y": Y, "meta": meta, "train": train, "hv": ~suspect & ~viol,
                "suspect": suspect, "violation": viol, "n0": len(X0)}


# --------------------------------------------------------------------------- #
# round log (ONE writer per lane; every record key is printed — nothing skipped)
# --------------------------------------------------------------------------- #

KEY_ORDER = ["proposed_at", "wave", "acq", "acq_seed", "guardrail_mode", "settings", "botorch", "bo_gp_sha",
             "loo_rms_z", "noise_raw", "predictions", "graded_at", "n_train", "n_hv", "cumulative_hv", "gain",
             "gain_tau_joint", "would_stop_joint", "gain_tau_marginal", "would_stop_marginal",
             "joint_vs_marginal", "first_fire_round", "n_outside_ref", "violations", "suspects", "r2_flag",
             "r2_max_mwh", "calibration", "C2_review", "C3_review", "halt", "decision"]


def round_log_header(lane: Lane, led: dict) -> str:
    t = led["tau"]
    cap_only = led["tau"].get("budget_cap_only", False)
    return (f"# methods_E arm {lane.arm} seed_id {lane.seed} — ROUND_LOG (prompt 55; acq = {lane.a['acq']}, "
            f"base = {lane.cfg['base_waves']} nav prefix n0 = {led['n0_tier']}, objectives = {led['objectives']})\n\n"
            f"Ledger: `{os.path.relpath(ledger_path(lane.dir), lane.root)}`. stop_rule = record_only: gain_k and\n"
            "would_stop_k = (gain_k < tau) AND (gain_{k-1} < tau) are graded and logged under tau_joint\n"
            "(headline) and tau_marginal (recorded) with the joint-vs-marginal sensitivity column; the\n"
            f"rule never halts; every lane runs to hard_cap = {led['hard_cap']}. tau_joint = {t['tau_joint']:.6g}, "
            f"tau_marginal = {t['tau_marginal']:.6g}"
            + (" — ZERO: the stop rule is budget-cap-only and the cap governs (plan 3).\n" if cap_only else ".\n")
            + "E-D5 OPEN: see README.md for the two readings of a fire. Halts ONLY per plan 1.2/1.3\n"
            "(HALT_FOR_DECISION.md). Acquisition jobs never submit; Kay submits via submit_ready_E.sh.\n"
            f"Stop NOW: `touch {os.path.relpath(stop_path(lane.dir), lane.root)}` on the CRC clone, then qdel the lane's JIDs.\n")


def write_round_section(lane: Lane, k: int, updates: dict, led: dict | None = None) -> dict:
    recs = load_records(lane.dir)
    rec = recs.get(str(k), {"round": k})
    rec.update(updates)
    recs[str(k)] = rec
    with open(records_path(lane.dir), "w") as f:
        json.dump(recs, f, indent=2, default=float)
        f.write("\n")
    lines = [f"<!-- BEGIN r{k} -->", f"## Round {k} ({lane.wave(k)})"]
    printed = set()
    for key in KEY_ORDER:
        if key in rec:
            lines.append(f"- {key}: {json.dumps(rec[key], default=float)}")
            printed.add(key)
    for key in rec:                                   # the donor skipped unknown keys silently; we never do
        if key not in printed and key not in ("round", "designs_u", "designs_mw", "realized"):
            lines.append(f"- {key}: {json.dumps(rec[key], default=float)}")
    if "designs_mw" in rec:
        lines.append(f"- designs (MW per site {lane.ds.sites}):")
        lines += [f"    - [{', '.join(f'{v:.3f}' for v in row)}]" for row in rec["designs_mw"]]
    if "realized" in rec:
        lines.append(f"- realized Y ({lane.objectives}):")
        lines += [f"    - [{', '.join(f'{v:.6g}' for v in row)}]" for row in rec["realized"]]
    lines.append(f"<!-- END r{k} -->")
    block = "\n".join(lines) + "\n"
    path = round_log_path(lane.dir)
    if os.path.isfile(path):
        text = open(path).read()
    else:
        text = round_log_header(lane, led or load_ledger(lane.dir))
    pat = re.compile(rf"<!-- BEGIN r{k} -->.*?<!-- END r{k} -->\n", flags=re.DOTALL)
    text = pat.sub(lambda _m: block, text) if pat.search(text) else text + "\n" + block
    with open(path, "w") as f:
        f.write(text)
    return rec


# --------------------------------------------------------------------------- #
# git / qstat plumbing (flock-serialised; parallel lanes share one clone)
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


def _has_remote(root) -> bool:
    return _git(root, "remote", check=False).stdout.strip() != ""


def pull(root, cfg):
    if not _has_remote(root):
        return
    with repo_lock(root):
        _git(root, "pull", "--rebase", "--autostash", "origin", cfg["repo_branch"], check=False)


def commit_and_push(root, cfg, paths, msg, push=True):
    with repo_lock(root):
        _git(root, "add", "--", *paths)
        r = _git(root, "commit", "-m", msg, bot=True, check=False)
        if r.returncode != 0 and "nothing to commit" not in r.stdout + r.stderr:
            raise RuntimeError(f"git commit failed: {r.stdout}{r.stderr}")
        if not push or not _has_remote(root):
            return
        br = cfg["repo_branch"]
        for attempt in range(1, 6):
            if _git(root, "push", "origin", br, check=False).returncode == 0:
                return
            print(f"push rejected (attempt {attempt}/5) — rebase and retry")
            time.sleep(30 + np.random.default_rng().integers(60))
            _git(root, "pull", "--rebase", "--autostash", "origin", br, check=False)
        _git(root, "push", "origin", br)


def qstat_full_names() -> list[tuple[str, str]]:
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


def acq_job_name(lane: Lane, k_next: int) -> str:
    return f"methods_E_{lane.arm}_s{lane.seed}_acq_r{k_next}"


def write_marker(lane: Lane, name, body, push=True):
    path = os.path.join(lane.dir, name)
    os.makedirs(lane.dir, exist_ok=True)
    with open(path, "w") as f:
        f.write(body)
    try:
        commit_and_push(lane.root, lane.cfg, [path], f"ercot-bot: methods_E {lane.arm} s{lane.seed} {name}", push=push)
    except Exception as exc:  # noqa: BLE001
        print(f"marker commit failed (marker is on disk): {exc}")


# --------------------------------------------------------------------------- #
# R and Sigma sources (Part B asserts the real files)
# --------------------------------------------------------------------------- #

def ref_point(lane: Lane, grading_Y: pd.DataFrame) -> tuple[np.ndarray, dict]:
    p = os.path.join(lane.root, lane.cfg["landing_R"])
    if os.path.isfile(p):
        with open(p) as f:
            land = json.load(f)
        assert land.get("identity") == "v3", land.get("identity")
        R = np.asarray([float(land["R"][o]) for o in lane.objectives], float)
        return R, {"R_source": os.path.relpath(p, lane.root), "R_rule": land.get("rule"), "R_n_rows": land.get("n_rows")}
    assert lane.cfg.get("part") != "B", "Part B: waves/n0_E/landing_R.json (53) is required"
    Yg = grading_Y.to_numpy(float)
    nadir, ideal = Yg.max(0), Yg.min(0)
    R = nadir + 0.1 * (nadir - ideal)
    return R, {"R_source": f"PLACEHOLDER (Part A): nadir + 0.1 (nadir - ideal) over the {len(Yg)} loaded n0_E rows",
               "R_rule": "plan 6.3 (placeholder data)", "R_n_rows": int(len(Yg))}


def sigma_and_noise(lane: Lane, Y0: np.ndarray) -> tuple[np.ndarray | None, str | None, dict | None, str]:
    """(Sigma or None, exact_cov_csv path or None, noise_json or None, source)."""
    cov = os.path.join(lane.root, lane.cfg["noise_exact_cov"])
    nj = os.path.join(lane.root, lane.cfg["noise_json"])
    noise = json.load(open(nj)) if os.path.isfile(nj) else None
    if os.path.isfile(cov):
        return None, cov, noise, os.path.relpath(cov, lane.root)
    assert lane.cfg.get("part") != "B", "Part B: analysis/noise_v3/ercot_noise_exact_cov.csv (52 / 54 B step 0) is required"
    ph = lane.cfg.get("part_a", {}).get("sigma_placeholder", {"mode": "zero"})
    M = Y0.shape[1]
    if ph.get("mode") == "zero":
        return np.zeros((M, M)), None, None, "PLACEHOLDER (Part A): Sigma = 0 (all exact zero)"
    if ph.get("mode") == "frac_sd":
        sd = float(ph["frac"]) * Y0.std(0, ddof=0)
        return np.diag(sd ** 2), None, None, f"PLACEHOLDER (Part A): diag ({ph['frac']} x start-set sd)^2"
    raise ValueError(ph)


# --------------------------------------------------------------------------- #
# init
# --------------------------------------------------------------------------- #

def cmd_init(lane: Lane, bo_gp_sha: str | None = None) -> dict:
    os.makedirs(lane.dir, exist_ok=True)
    if os.path.exists(ledger_path(lane.dir)):
        raise RuntimeError(f"REFUSED: lane {lane.arm} s{lane.seed} ledger already exists")
    _step(lane.dir, "init: loading the start set")
    X0, U0, Y0, m0, (Xall, Uall, Yall, mall) = lane.start_set()
    assert len(X0) == lane.n0_tier and Y0.shape[1] == len(lane.objectives), (X0.shape, Y0.shape)
    assert not m0["suspect"].astype(bool).any(), "SUSPECT run in the start set"
    Yn = Y0.to_numpy(float)
    R, rinfo = ref_point(lane, Yall)
    assert np.all(np.isfinite(R))
    Sigma, cov_csv, noise, sigma_source = sigma_and_noise(lane, Yn)
    _step(lane.dir, "init: tau rulers (N = 1000 draws, exact HV)")
    rul = tau_E.rulers_from_files(Yn, R, lane.objectives, exact_cov_csv=cov_csv, noise_json=noise, Sigma=Sigma,
                                  n_draws=int(lane.cfg.get("tau_n_draws", 1000)), seed=int(lane.cfg.get("tau_seed", 20261006)))
    rul["sigma_source"] = sigma_source
    rul["computed_at"] = now()
    rul["start_set_keys"] = [str(k) for k in X0.index]
    rider = tau_E.rider_levels(noise, lane.objectives) if noise else None
    with open(tau_init_path(lane.dir), "w") as f:
        json.dump(rul, f, indent=2, default=float)
        f.write("\n")
    hv0 = ce.hv_exact(Yn, R)
    sha = bo_gp_sha or ce.bogp_sha()
    led = {
        "campaign": "methods_E", "prompt": "55", "part": lane.cfg.get("part", "A"),
        "arm": lane.arm, "seed_id": lane.seed, "acq": lane.a["acq"],
        "objectives": lane.objectives,
        "objective_status": {o: lane.ds.raw["objectives"][o]["status"] for o in lane.objectives},
        "ref_point": R.tolist(), **rinfo,
        "tau": {"tau_joint": rul["tau_joint"], "tau_marginal": rul["tau_marginal"],
                "sensitivity_joint_over_marginal": rul["sensitivity_joint_over_marginal"],
                "budget_cap_only": rul["budget_cap_only"], "form": rul["form"], "sigma_source": sigma_source},
        "tau_headline": "tau_joint", "tau_recipe": rul["recipe"],
        "rider_levels": rider,
        "n0_tier": lane.n0_tier, "n0_source": lane.n0_source,
        "base_waves": lane.cfg["base_waves"], "loader": lane.loader_source, "configs_source": lane.configs_source,
        "gp": {o: {"cfg": list(c), "floor": float(f)} for o, c, f in zip(lane.objectives, lane.gp_cfgs, lane.gp_floors)},
        "qnehvi": lane.cfg["qnehvi"], "q": lane.cfg["q"], "hard_cap": lane.cfg["hard_cap"],
        "stop_rule": lane.cfg["stop_rule"], "acq_seed_base": lane.cfg["acq_seed_base"],
        "guardrails": lane.cfg["guardrails"], "guardrail_mode": "monitor", "guardrail_flipped_at_round": None,
        "violations": [], "suspects": [], "r2_flag_rounds": [],
        "first_fire_round": {"tau_joint": None, "tau_marginal": None},
        "C2_review_rounds": [], "C3_review_rounds": [], "halt": None,
        "bo_gp_sha": sha, "design_space_version": lane.ds.raw.get("contract_version"),
        "init_at": now(),
        "entries": [{"round": 0, "n": int(len(X0)), "n_hv": int(len(X0)), "hv": hv0, "gain": None,
                     "n_outside_ref": int((~np.all(Yn < R, axis=1)).sum()), "decision": "start", "at": now()}],
    }
    save_ledger(lane.dir, led)
    with open(round_log_path(lane.dir), "w") as f:
        f.write(round_log_header(lane, led))
    write_arm_readme(lane, led, rul)
    print(f"init {lane.arm} s{lane.seed}: n0={len(X0)} hv0={hv0:.6g} R={R.round(4).tolist()} "
          f"tau_joint={rul['tau_joint']:.6g} tau_marginal={rul['tau_marginal']:.6g} "
          f"[{sigma_source}; R {rinfo['R_source']}; loader {lane.loader_source}; configs {lane.configs_source}]")
    return led


def check_rulers(lane: Lane, led: dict) -> dict:
    """Read back tau_init.json; equality-asserted every round."""
    t = json.load(open(tau_init_path(lane.dir)))
    for k in ("tau_joint", "tau_marginal"):
        assert led["tau"][k] == t[k], (f"ledger {k} != tau_init.json", led["tau"][k], t[k])
    return t


def recompute_rulers(lane: Lane) -> dict:
    """Independent recomputation of the init rulers from the files; equality-asserted."""
    led = load_ledger(lane.dir)
    X0, U0, Y0, m0, _ = lane.start_set()
    Sigma, cov_csv, noise, _ = sigma_and_noise(lane, Y0.to_numpy(float))
    rul = tau_E.rulers_from_files(Y0.to_numpy(float), np.asarray(led["ref_point"]), lane.objectives,
                                  exact_cov_csv=cov_csv, noise_json=noise, Sigma=Sigma,
                                  n_draws=int(lane.cfg.get("tau_n_draws", 1000)), seed=int(lane.cfg.get("tau_seed", 20261006)))
    for k in ("tau_joint", "tau_marginal"):
        assert rul[k] == led["tau"][k], (k, rul[k], led["tau"][k])
    return rul


# --------------------------------------------------------------------------- #
# arm README (E-D5 OPEN: both readings; banned framings verbatim; M = 4 note)
# --------------------------------------------------------------------------- #

def write_arm_readme(lane: Lane, led: dict, rul: dict) -> str:
    M = len(lane.objectives)
    c2, c3 = 3.7e-4, 1.1e-6
    any_c2 = 1 - (1 - c2) ** M
    any_c3 = 1 - (1 - c3) ** M
    cap_only = led["tau"]["budget_cap_only"]
    body = f"""# methods_E arm `{lane.arm}` — README (prompt 55 v3.1; written at init, regenerated per lane init)

Lanes: seed_ids {lane.a['seed_ids']} (option C: 1 arm x 5 seeds x cap {led['hard_cap']} x q {led['q']}; plan 8, E-D4
default). Each lane `s<seed>/` has its own ledger; the start set is shared
(`{led['base_waves']}` nav prefix, n0 = {led['n0_tier']} — E-D7 source: {led['n0_source']}).

## Objectives (M = {M}) and their status

{chr(10).join(f'- `{o}`: {led["objective_status"][o]}' for o in lane.objectives)}

R4 / N1 are PROVISIONAL (E-D1b); E1 waits for the plan 1.2 verdict (E3 if not
READABLE). The cost objective is never switched mid-campaign.

## Sources at this init (Part {led['part']})

- loader: **{led['loader']}** · committed configs: **{led['configs_source']}** · R: {led['R_source']}
- Sigma for tau: {led['tau']['sigma_source']} · form: {led['tau']['form']}
- bo-gp SHA {led['bo_gp_sha']} (hypervolume_exact, M-general recursive sweep)

## tau rulers (computed ONCE at init from the {led['n0_tier']} starts; equality-asserted every round)

| ruler | value | role |
|---|---|---|
| tau_joint | {led['tau']['tau_joint']:.6g} | HEADLINE (plan 6.1/6.2: noise vectors drawn jointly from N(0, Sigma_exact)) |
| tau_marginal | {led['tau']['tau_marginal']:.6g} | RECORDED (independent per-objective normals, marginal sds) |
| joint / marginal | {led['tau']['sensitivity_joint_over_marginal']} | the plan 6.2 joint-vs-marginal sensitivity row (third ledger column) |

{'**The exact cross-batch replicate covariance is identically zero, so tau_joint = tau_marginal = 0: the stop rule is budget-cap-only and the cap governs (plan 3). This is a finding about a deterministic instrument, not a failure.**' if cap_only else 'Sigma_exact is NOT identically zero: the two-strike readings below are live.'}

Note on the Sigma convention: plan 6.2 pins Sigma = the covariance of the
replicate DELTAS (A - B). Under independent replicate noise that is 2x the
per-run covariance, so tau is larger by sqrt(2) than a per-run-noise tau. The
plan is immutable; the recipe is used as frozen and this is a disclosure, not
a change.

## The stop rule — E-D5 OPEN (both readings carried until Part B)

Per round k the ledger records gain_k = HV_k - HV_(k-1) over the accumulated
lane set (SUSPECT and R1-violating runs excluded), gain_k / tau, and the
stateless two-strike verdict would_stop_k = (gain_k < tau) AND (gain_(k-1) <
tau) under each ruler, plus first_fire_round. The machinery never halts on the
rule; every lane runs to the cap.

- **(a) plan 6.1 fallback** ("analysis not run"): the first fire is "the stop";
  later rounds are still graded and later fires are recorded as descriptive.
- **(b) E-D5 recommendation** (prompt 50: the two-strike form was NOT ACCEPTED
  truth-known — early 49.2 %, regret 1.83 tau): the budget cap is the stop; the
  first fire is DESCRIPTIVE reporting only. Lands as an append-only AMENDMENT to
  plan 6.1 before Part B.

Until E-D5 is decided and appended, both readings are reported side by side
and neither is called "the verdict".

{BANNED_FRAMINGS}

## Calibration gates (plan 6.4; per-objective numbers immutable)

C1 ingest = fail-stop (FAILED_r<k>.md, nothing proposed). C2 (covered <= 4 of 8
for any objective) and C3 (>= 3 of 8 with |z| > 3 for any objective) = record +
REVIEW flag, never a halt. The per-objective false-alarm rates are the plan's
(C2 {c2:.1e}, C3 {c3:.1e}); at M = {M} the ANY-objective rates are
C2 1 - (1 - {c2:.1e})^{M} = **{any_c2:.1e}** and C3 **{any_c3:.1e}** (standings 7 raised
M = 4; the plan itself does not). Reading note: with the noise inferred small,
|z| inflates by construction — judge against the committed-config cov95.

## Guardrails and SUSPECT (plan 1.2-1.3; wiring = build requirement)

- R1 shed > {lane.violation_mwh} MWh: the run stays in the ledger as infeasible-for-claims,
  excluded from reported fronts and from HV/gain (kept in GP training); the
  round AFTER the first violation flips `guardrail_mode` monitor -> constrain
  (constrained qNEHVI, shed GP constraint shed <= {lane.violation_mwh} MWh; a constant shed
  column is degenerate -> feasibility = 1, recorded); >= 2 violations in one
  round -> `HALT_FOR_DECISION.md` (Kay decides).
- R2 reserve shortfall > {lane.r2_flag_at} MWh (2 x base): round flag, recorded, never halts.
- SUSPECT (S1-S3, `meta.suspect`): excluded from HV, gain and (build choice)
  GP training; flagged; >= 2 in one round -> HALT FOR DECISION.

## Acquisition

botorch `qNoisyExpectedHypervolumeImprovement` (the plan's pinned form; botorch
0.16 advises `qLogNoisyExpectedHypervolumeImprovement` for numerics — NOT
adopted, a one-line config alternative), ref_point = R, alpha 0.0,
prune_baseline, SobolQMCNormalSampler(128, seed s), optimize_acqf over
[0, 1]^{lane.ds.d}, q = {led['q']}, 20 restarts x 512 raw samples, sequential.
Seed s = {led['acq_seed_base']} + 100 x seed_id + k, `torch.manual_seed(s)` once per process;
the RTS integers are reused on a different X / Y, which is statistically
harmless (the tau RNG is numpy `default_rng(20261006)`, distinct). Proposals
u -> MW = u x gen_pmax at full precision, no snapping; exact 0 = site absent.
"""
    p = os.path.join(lane.root, lane.a["dir"], "README.md")
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w") as f:
        f.write(body)
    return p


# --------------------------------------------------------------------------- #
# propose round k
# --------------------------------------------------------------------------- #

def _refuse_if_halted(lane: Lane):
    if os.path.isfile(halt_path(lane.dir)):
        raise SystemExit(f"REFUSED: {halt_path(lane.dir)} exists — HALT FOR DECISION (Kay decides, then renames it)")


def propose_round(lane: Lane, k: int) -> str:
    import qnehvi_E
    import botorch
    led = load_ledger(lane.dir)
    _refuse_if_halted(lane)
    assert 1 <= k <= led["hard_cap"], f"round {k} outside 1..{led['hard_cap']}"
    check_rulers(lane, led)
    _step(lane.dir, f"propose r{k}: loading the accumulated set (rounds 1..{k - 1})")
    acc = lane.accumulated(k - 1)
    U = acc["U"].to_numpy(float)[acc["train"]]
    Y = acc["Y"].to_numpy(float)[acc["train"]]
    shed = acc["meta"]["R1"].astype(float).to_numpy()[acc["train"]]
    R = np.asarray(led["ref_point"], float)
    seed = acq_seed(lane.cfg, lane.seed, k)
    mode = led["guardrail_mode"]
    _step(lane.dir, f"propose r{k}: qNEHVI on n={len(U)} (seed {seed}, guardrail_mode {mode})")
    res = qnehvi_E.propose(U, Y, R, lane.gp_cfgs, lane.gp_floors, seed=seed, q=lane.cfg["q"],
                           qcfg=lane.cfg["qnehvi"], shed=shed, shed_limit=lane.violation_mwh, guardrail_mode=mode)
    ub = res["u_batch"]
    assert ub.shape == (lane.cfg["q"], lane.ds.d), ub.shape
    keys = {tuple(r) for r in ub.round(10).tolist()}
    assert len(keys) == lane.cfg["q"], "duplicate designs in batch"
    # RISK (prompt 66 F6): qNEHVI proposes box vertices; a later round can re-propose an evaluated vertex and this assert
    # then stops the lane. The replacement (declared re-proposal rule) is a 55 Part B decision — unchanged here.
    assert not (keys & {tuple(r) for r in acc["U"].to_numpy(float).round(10).tolist()}), "re-proposed an evaluated design"
    overlap = {}
    if k == 1:
        for s in lane.a["seed_ids"]:          # init assert: r1 proposals differ across seeds (the seed reaches the sampler)
            if s == lane.seed:
                continue
            other = load_records(lane_dir(lane.root, lane.cfg, lane.arm, s)).get("1")
            if other:
                okeys = {tuple(r) for r in np.asarray(other["designs_u"], float).round(10).tolist()}
                # prompt 55 §2.1 pins "r1 proposals DIFFER across seed_ids"; pairwise disjointness was stricter and
                # fails legitimately when the acquisition optimum sits on a box vertex (prompt 66 emulator, real n0_E):
                # assert the sets differ, RECORD the shared designs.
                assert keys != okeys, f"r1 proposals of s{lane.seed} identical to s{s} (the seed does not reach the sampler)"
                ob = np.asarray(other["designs_u"], float)
                dmin = np.abs(ub[:, None, :] - ob[None, :, :]).max(-1).min(1)     # per design: nearest design of seed s
                assert (dmin > 1e-6).any(), (f"r1 proposals of s{lane.seed} and s{s} differ only by round-off "
                                             "(< 1e-6 in u): the seed does not reach the sampler")
                overlap[str(s)] = len(keys & okeys)
    _step(lane.dir, f"propose r{k}: writing wave {lane.wave(k)}")
    extra = {"methods_arm": lane.arm, "seed_id": lane.seed, "methods_round": k, "acq": lane.a["acq"],
             "acq_seed": seed, "bo_gp_sha": led["bo_gp_sha"], "botorch": botorch.__version__,
             "guardrail_mode": mode, "settings": res["settings"], "objectives": lane.objectives,
             "n_train": int(len(U)), "loader": lane.loader_source}
    wdir = ww.build_round_wave(lane.root, lane.ds, lane.wave(k), ub, manifest_extra=extra,
                               pred_mean=res["pred_mean"], pred_sd=res["pred_sd"], objectives=lane.objectives,
                               transforms=res["transforms"])
    write_round_section(lane, k, {
        "proposed_at": now(), "wave": lane.wave(k), "acq": lane.a["acq"], "acq_seed": seed,
        "guardrail_mode": mode, "settings": res["settings"], "botorch": botorch.__version__,
        "bo_gp_sha": led["bo_gp_sha"], "n_train": int(len(U)),
        "loo_rms_z": dict(zip(lane.objectives, res["loo_rms_z"])),
        "noise_raw": dict(zip(lane.objectives, [float(v) for v in res["noise_raw"]])),
        "qnehvi_seconds": round(float(res["seconds"]), 1),
        "designs_u": ub.tolist(), "designs_mw": lane.ds.u_to_mw(ub).tolist(),
        "predictions": os.path.relpath(os.path.join(wdir, "predictions.csv"), lane.root),
        **({"r1_shared_designs_with_seed": overlap} if k == 1 else {}),
        "decision": "proposed"}, led=led)
    return wdir


# --------------------------------------------------------------------------- #
# C1 ingest gate
# --------------------------------------------------------------------------- #

def ingest_gate(lane: Lane, k: int):
    wdir = os.path.join(lane.root, "waves", lane.wave(k))
    q = lane.cfg["q"]
    if not os.path.isdir(wdir):
        return False, f"waves/{lane.wave(k)} missing", {}
    if glob.glob(os.path.join(wdir, "FAILED_*")):
        return False, "collector FAILED marker present", {}
    if not round_record_exists(lane.dir, k):
        return False, f"no round-{k} record — wave of unknown provenance", {}
    try:
        X, U, Y, meta = lane._load([lane.wave(k)])
    except Exception as exc:  # noqa: BLE001
        return False, f"loader failed on {lane.wave(k)}: {exc}", {}
    if len(X) != q:
        return False, f"{len(X)} of {q} runs present at the v3 identity (refused {meta.attrs.get('refused')})", {}
    idx = sorted(int(i) for i in meta["index"])
    if idx != list(range(1, q + 1)):
        return False, f"indices {idx} != 1..{q}", {}
    if not np.isfinite(Y.to_numpy(float)).all():
        return False, "non-finite objective values", {}
    rec = load_records(lane.dir)[str(k)]
    proposed_u = np.asarray(rec["designs_u"], float)
    proposed_mw = np.asarray(rec["designs_mw"], float)
    got = U.loc[[f"{lane.wave(k)}:{i}" for i in range(1, q + 1)]].to_numpy(float)
    if not np.allclose(got, proposed_u, atol=1e-9, rtol=0):
        return False, "loaded u != proposed designs (wrong-wave/stale runs?)", {}
    # the landed wave files themselves: design_matrix mw_* AND u_* columns, and every retrofit dict
    dm = pd.read_csv(os.path.join(wdir, "design_matrix.csv"), dtype={"oat_site": str}).sort_values("index")
    if list(dm["index"].astype(int)) != list(range(1, q + 1)) or not (dm["oat_site"] == "__ALL__").all():
        return False, "design_matrix rows/oat_site do not match a methods_E round", {}
    if not np.allclose(dm[lane.ds.x_columns].to_numpy(float), proposed_mw, atol=1e-6, rtol=0):
        return False, "design_matrix mw_* columns != proposed designs (tampered or wrong wave)", {}
    if not np.allclose(dm[lane.ds.u_columns].to_numpy(float), proposed_u, atol=1e-9, rtol=0):
        return False, "design_matrix u_* columns != proposed designs (tampered or wrong wave)", {}
    if not np.allclose(dm["pem_mw"].to_numpy(float), proposed_mw.sum(axis=1), atol=1e-6, rtol=0):
        return False, "design_matrix pem_mw != sum of the proposed MW", {}
    for i, u in enumerate(proposed_u, start=1):
        dp = os.path.join(wdir, f"retrofit_gen_dict_{i}.json")
        if not os.path.isfile(dp):
            return False, f"retrofit_gen_dict_{i}.json missing", {}
        with open(dp) as f:
            dct = json.load(f)
        want = {s: {"PEM_bid": lane.ds.bid, "PEM_fraction": float(uu), "gen_pmax": float(pm)}
                for s, uu, pm in zip(lane.ds.sites, u, lane.ds.gen_pmax) if float(uu) * float(pm) > 0.0}
        if set(dct) != set(want):
            return False, f"retrofit_gen_dict_{i}.json sites {sorted(dct)} != proposed {sorted(want)}", {}
        for s_, w in want.items():
            g = dct[s_]
            if (abs(float(g.get("PEM_fraction", np.nan)) - w["PEM_fraction"]) > 1e-9
                    or abs(float(g.get("gen_pmax", np.nan)) - w["gen_pmax"]) > 1e-6
                    or float(g.get("PEM_bid", np.nan)) != w["PEM_bid"]):
                return False, f"retrofit_gen_dict_{i}.json entry {s_} != proposed design", {}
    info = {"n_suspect": int(meta["suspect"].astype(bool).sum()),
            "n_violation": int((meta["R1"].astype(float) > lane.violation_mwh).sum()),
            "r2_max": float(meta["R2"].astype(float).max())}
    return True, "ok", info


# --------------------------------------------------------------------------- #
# grade round k (form-agnostic; record_only; halts only per plan 1.2/1.3)
# --------------------------------------------------------------------------- #

def _calibration(lane: Lane, k: int, Yk: pd.DataFrame) -> tuple[dict, bool, bool]:
    wdir = os.path.join(lane.root, "waves", lane.wave(k))
    preds = pd.read_csv(os.path.join(wdir, "predictions.csv")).sort_values("index")
    calib, c2, c3 = {}, False, False
    q = len(Yk)
    for o in lane.objectives:
        tr = str(preds[f"{o}_transform"].iloc[0])
        y = Yk[o].to_numpy(float)
        t = np.log1p(y) if tr == "log1p" else y
        z = (t - preds[f"{o}_pred_mean"].to_numpy(float)) / preds[f"{o}_pred_sd"].to_numpy(float)
        cov = int((np.abs(z) <= 1.96).sum())
        n3 = int((np.abs(z) > 3.0).sum())
        calib[o] = {"mean_z": round(float(z.mean()), 3), "rms_z": round(float(np.sqrt((z ** 2).mean())), 3),
                    "cov95": cov, "n_abs_z_gt3": n3, "transform": tr}
        c2 |= cov <= 4
        c3 |= n3 >= 3
    assert q == lane.cfg["q"]
    return calib, c2, c3


def grade_round(lane: Lane, k: int) -> tuple[dict, bool]:
    led = load_ledger(lane.dir)
    tau = check_rulers(lane, led)
    R = np.asarray(led["ref_point"], float)
    _step(lane.dir, f"grade r{k}: loading rounds 0..{k}")
    acc = lane.accumulated(k)
    meta = acc["meta"]
    wave = lane.wave(k)
    in_k = meta["wave"].astype(str).to_numpy() == wave
    order = np.argsort(meta[in_k]["index"].astype(int).to_numpy(), kind="stable")   # align with predictions.csv
    Yk = acc["Y"][in_k].iloc[order]
    mk = meta[in_k].iloc[order]
    calib, c2, c3 = _calibration(lane, k, Yk)
    viol_k = [str(x) for x in mk.index[mk["R1"].astype(float) > lane.violation_mwh]]
    susp_k = [str(x) for x in mk.index[mk["suspect"].astype(bool)]]
    r2_max = float(mk["R2"].astype(float).max())
    r2_flag = bool(r2_max > lane.r2_flag_at)
    # guardrail bookkeeping (plan 1.3)
    led["violations"] = sorted(set(led["violations"]) | set(viol_k))
    led["suspects"] = sorted(set(led["suspects"]) | set(susp_k))
    if viol_k and led["guardrail_mode"] == "monitor":
        led["guardrail_mode"] = "constrain"                   # applies from the NEXT round's proposal
        led["guardrail_flipped_at_round"] = k
    if r2_flag:
        led["r2_flag_rounds"].append(k)
    halt_reasons = []
    if len(viol_k) >= 2:
        halt_reasons.append(f"{len(viol_k)} R1 shed violations (> {lane.violation_mwh} MWh) in round {k}: {viol_k}")
    if len(susp_k) >= 2:
        halt_reasons.append(f"{len(susp_k)} SUSPECT runs in round {k}: {susp_k}")
    # HV / gain over the accumulated set WITHOUT suspect / violating rows
    Yhv = acc["Y"].to_numpy(float)[acc["hv"]]
    hv = ce.hv_exact(Yhv, R)
    prev = led["entries"][-1]["hv"]
    gain = hv - prev
    gains = [e["gain"] for e in led["entries"] if e["gain"] is not None] + [gain]
    rulers, ws = {}, {}
    for name in ("tau_joint", "tau_marginal"):
        t = float(tau[name])
        if t > 0:
            rulers[f"gain_{name}"] = gain / t
            ws[name] = bool(len(gains) >= 2 and gains[-1] < t and gains[-2] < t)
        else:
            rulers[f"gain_{name}"] = None                      # budget-cap-only: no ruler to divide by
            ws[name] = False
        rulers[f"would_stop_{name}"] = ws[name]
        if ws[name] and led["first_fire_round"][name] is None:
            led["first_fire_round"][name] = k
    sens = {"ratio_joint_over_marginal": led["tau"]["sensitivity_joint_over_marginal"],
            "agree": ws["tau_joint"] == ws["tau_marginal"],
            "fires": {"joint": ws["tau_joint"], "marginal": ws["tau_marginal"]}}
    if c2:
        led["C2_review_rounds"].append(k)
    if c3:
        led["C3_review_rounds"].append(k)
    decision = "graded (record_only)"
    if halt_reasons:
        decision += " + HALT FOR DECISION"
        led["halt"] = {"round": k, "reasons": halt_reasons, "at": now()}
    n_out = int((~np.all(Yhv < R, axis=1)).sum())
    entry = {"round": k, "n": int(len(acc["X"])), "n_hv": int(acc["hv"].sum()), "hv": hv, "gain": gain,
             "gain_tau_joint": rulers["gain_tau_joint"], "would_stop_joint": ws["tau_joint"],
             "gain_tau_marginal": rulers["gain_tau_marginal"], "would_stop_marginal": ws["tau_marginal"],
             "joint_vs_marginal": sens, "n_outside_ref": n_out, "violations": viol_k, "suspects": susp_k,
             "r2_flag": r2_flag, "C2_review": c2, "C3_review": c3, "decision": decision, "at": now()}
    led["entries"].append(entry)
    save_ledger(lane.dir, led)
    write_round_section(lane, k, {
        "graded_at": now(), "n_train": int(acc["train"].sum()), "n_hv": int(acc["hv"].sum()),
        "cumulative_hv": hv, "gain": gain,
        "gain_tau_joint": rulers["gain_tau_joint"], "would_stop_joint": ws["tau_joint"],
        "gain_tau_marginal": rulers["gain_tau_marginal"], "would_stop_marginal": ws["tau_marginal"],
        "joint_vs_marginal": sens, "first_fire_round": led["first_fire_round"], "n_outside_ref": n_out,
        "violations": viol_k, "suspects": susp_k, "r2_flag": r2_flag, "r2_max_mwh": r2_max,
        "calibration": calib, "C2_review": c2, "C3_review": c3,
        "halt": led["halt"] if halt_reasons else None,
        "realized": Yk.to_numpy(float).tolist(), "decision": decision}, led=led)
    if halt_reasons:
        with open(halt_path(lane.dir), "w") as f:
            f.write(f"# HALT FOR DECISION — methods_E {lane.arm} s{lane.seed}, round {k} ({now()})\n\n"
                    + "".join(f"- {r}\n" for r in halt_reasons)
                    + "\nThe machinery has STOPPED proposing for this lane (plan 1.2 / 1.3). Round "
                    f"{k} is graded and recorded above; nothing was proposed. Kay decides; to resume, rename "
                    f"this file (e.g. HALT_FOR_DECISION.md -> HALT_r{k}_DECIDED.md) and record the decision in "
                    "PROGRESS.md. The cost objective is never switched mid-campaign.\n")
    return led, bool(halt_reasons)


# --------------------------------------------------------------------------- #
# the round (grade k -> propose k+1 -> commit -> push -> STOP)
# --------------------------------------------------------------------------- #

def run_round(lane: Lane, k: int, no_submit: bool, push: bool = True) -> int:
    if not no_submit:
        raise SystemExit("REFUSED: `run` requires --no-submit (compute nodes never qsub; prompt 35 3.1 / 55 2.8)")
    d = lane.dir
    _step(d, f"run r{k}: git pull")
    pull(lane.root, lane.cfg)
    if os.path.isfile(stop_path(d)):
        write_marker(lane, "DONE.md", f"# DONE {lane.arm} s{lane.seed}\n\nreason: STOP found at round {k} ({now()}). Nothing proposed.\n", push)
        return 0
    if os.path.isfile(halt_path(d)):
        print(f"HALT FOR DECISION present at {halt_path(d)} — nothing graded or proposed")
        return 0
    paths = [d, os.path.join(lane.root, lane.a["dir"], "README.md")]
    if k == 0:
        if not os.path.exists(ledger_path(d)):
            _step(d, "run r0: init")
            cmd_init(lane)
    else:
        _step(d, f"run r{k}: ingest gate (C1)")
        ok, why, info = ingest_gate(lane, k)
        if not ok:
            write_marker(lane, f"FAILED_r{k}.md",
                         f"# FAILED — {lane.arm} s{lane.seed} round {k} ingest gate (C1)\n\nreason: {why}\nat: {now()}\n"
                         "Nothing was proposed.\n", push)
            return 0
        paths.append(os.path.join(lane.root, "waves", lane.wave(k)))
    _step(d, f"run r{k}: double-spend guards")
    guards = []
    if round_record_exists(d, k + 1):
        guards.append(f"round {k + 1} record already exists")
    if k + 1 <= lane.cfg["hard_cap"] and os.path.exists(os.path.join(lane.root, "waves", lane.wave(k + 1))):
        guards.append(f"waves/{lane.wave(k + 1)} already exists")
    foreign = foreign_jobs_named(acq_job_name(lane, k + 1))
    if foreign:
        guards.append(f"other jobs named {acq_job_name(lane, k + 1)}: {foreign}")
    if guards:
        write_marker(lane, f"FAILED_r{k}.md", "# FAILED — double-spend guard\n\n- " + "\n- ".join(guards)
                     + f"\n\nat: {now()}\nNothing was proposed.\n", push)
        return 0
    if k >= 1:
        _step(d, f"run r{k}: grading (record_only)")
        led, halted = grade_round(lane, k)
        e = led["entries"][-1]
        gt = e["gain_tau_joint"]
        gtxt = f"{gt:.2f} tau_joint" if gt is not None else "cap-only (tau = 0)"
        if halted:
            commit_and_push(lane.root, lane.cfg, paths, f"ercot-bot: methods_E {lane.arm} s{lane.seed} r{k} graded ({gtxt}) — HALT FOR DECISION", push)
            return 0
        if k >= lane.cfg["hard_cap"]:
            body = (f"# DONE {lane.arm} s{lane.seed}\n\nreason: hard_cap {lane.cfg['hard_cap']} reached at round {k} ({now()}).\n"
                    f"HV trajectory: {[round(x['hv'], 6) for x in led['entries']]}\n"
                    f"would_stop_joint by round: {[x.get('would_stop_joint') for x in led['entries'][1:]]}\n"
                    f"would_stop_marginal by round: {[x.get('would_stop_marginal') for x in led['entries'][1:]]}\n"
                    f"first_fire_round: {led['first_fire_round']}  (E-D5 OPEN: reading (a) first fire = the stop; "
                    "reading (b) the cap is the stop, the fire is descriptive)\n"
                    f"violations: {led['violations']}  suspects: {led['suspects']}  C2 review rounds: {led['C2_review_rounds']}  "
                    f"C3 review rounds: {led['C3_review_rounds']}\n")
            with open(done_path(d), "w") as f:
                f.write(body)
            commit_and_push(lane.root, lane.cfg, paths, f"ercot-bot: methods_E {lane.arm} s{lane.seed} r{k} graded ({gtxt}) — DONE (hard cap)", push)
            return 0
    _step(d, f"run r{k}: proposing round {k + 1}")
    next_wave = propose_round(lane, k + 1)
    if k >= 1:
        write_round_section(lane, k, {"decision": f"graded (record_only) -> r{k + 1}"})
    _step(d, f"run r{k}: commit{' + push' if push else ''}, then STOP (--no-submit)")
    commit_and_push(lane.root, lane.cfg, paths + [next_wave],
                    f"ercot-bot: methods_E {lane.arm} s{lane.seed} " + (f"r{k} graded + " if k >= 1 else "init + ")
                    + f"r{k + 1} proposed ({lane.wave(k + 1)})", push)
    _step(d, f"run r{k}: done (no submit — submit_ready_E.sh picks it up)")
    return 0


def status(root, cfg) -> list[dict]:
    rows = []
    for arm, a in cfg["arms"].items():
        for s in a["seed_ids"]:
            d = lane_dir(root, cfg, arm, s)
            st = {"arm": arm, "seed": s, "ledger": os.path.isfile(ledger_path(d))}
            if st["ledger"]:
                led = load_ledger(d)
                st.update({"rounds_graded": len(led["entries"]) - 1, "guardrail_mode": led["guardrail_mode"],
                           "halt": bool(led.get("halt")), "first_fire_round": led["first_fire_round"],
                           "proposed": sorted(int(k) for k in load_records(d))})
            st["files"] = [f for f in ("HALT_FOR_DECISION.md", "DONE.md", "STOP") if os.path.exists(os.path.join(d, f))]
            st["files"] += sorted(os.path.basename(p) for p in glob.glob(os.path.join(d, "FAILED_r*.md")))
            rows.append(st)
    return rows


# --------------------------------------------------------------------------- #

def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)
    for name in ("init", "propose", "grade", "run", "recompute-tau"):
        sp = sub.add_parser(name)
        sp.add_argument("--arm", default="qnehvi")
        sp.add_argument("--seed", type=int, required=True)
        if name in ("propose", "grade", "run"):
            sp.add_argument("--round", type=int, required=True)
        if name == "run":
            sp.add_argument("--no-submit", action="store_true")
            sp.add_argument("--no-push", action="store_true")
    sa = sub.add_parser("init-all", help="init every seed of an arm + propose r1 each; asserts the r1 sets differ")
    sa.add_argument("--arm", default="qnehvi")
    sub.add_parser("status")
    args = p.parse_args(argv)
    root = ce.ercot_root()
    cfg = load_config(root)
    if args.cmd == "status":
        for r in status(root, cfg):
            print(json.dumps(r))
        return 0
    if args.cmd == "init-all":
        for s in arm_cfg(cfg, args.arm)["seed_ids"]:
            lane = Lane(root, cfg, args.arm, s)
            if not os.path.exists(ledger_path(lane.dir)):
                cmd_init(lane)
            if not round_record_exists(lane.dir, 1):
                print("wave:", propose_round(lane, 1))
        return 0
    lane = Lane(root, cfg, args.arm, args.seed)
    if args.cmd == "init":
        cmd_init(lane)
    elif args.cmd == "propose":
        print("wave:", propose_round(lane, args.round))
    elif args.cmd == "grade":
        led, halted = grade_round(lane, args.round)
        print(json.dumps(led["entries"][-1], default=float), "HALT" if halted else "")
    elif args.cmd == "recompute-tau":
        print(json.dumps({k: v for k, v in recompute_rulers(lane).items() if k.startswith("tau")}))
    elif args.cmd == "run":
        return run_round(lane, args.round, args.no_submit, push=not args.no_push)
    return 0


if __name__ == "__main__":
    sys.exit(main())
