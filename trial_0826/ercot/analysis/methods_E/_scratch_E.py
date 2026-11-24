"""Prompt 55 — build a SCRATCH ERCOT_ROOT for the offline dry round and the tests.

Zero simulation. The scratch root mirrors `trial_0826/ercot` as far as the
machinery reads it:

    <root>/waves/design_space_E.json      the contract-3 JSON verbatim (53 owns the real file)
    <root>/waves/GAP_DECISION.json        copied from the live tree (identity v3)
    <root>/waves/n0_E/                    48 scrambled-Sobol rows (sobol_index 0..47, tier nav < 32
                                          else grading) in the contract-5 schema + retrofit dicts
    <root>/waves/random_E/                48 i.i.d.-uniform rows (the holdout / baseline; must NEVER
                                          enter the training set — the assert is exercised)
    <root>/extracts/<wave>/run_index_i/identity.txt   the v3 identity line (what the loader checks)
    <root>/analysis/methods_E/            arms_E.json (+ optional overrides), the python modules
                                          (symlinked), _stub_committed_configs.json
    <root>/tools/make_v2_waves.py         the house blocks used by the templates
    <root>/.gitignore                     the three gz lines (contract 4)
    <root>/pool_objectives.py etc.        NOT needed (the stub loader never reads extracts)
    git: a repo at <root>/../.. with a bare origin, so commit + push run for real.

`fake_collect(root, wave, overrides=None)` writes identity.txt for every row
of a wave (+ `stub_pool_row.json` overrides per index: e.g. {3: {"R1": 2.5}}
for a shed violation, {5: {"suspect": True}} for a SUSPECT run) — the stand-in
for the CRC collector.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys

import numpy as np
import pandas as pd
from scipy.stats import qmc

HERE = os.path.dirname(os.path.abspath(__file__))
LIVE_ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
MODULES = ["common_E.py", "_stub_loader.py", "tau_E.py", "qnehvi_E.py", "wave_writer_E.py", "acquire_E.py",
           "_stub_committed_configs.json", "_contract_design_space_E.json", "_scratch_E.py", "dry_round_E.py"]
IDENTITY_LINE = ('IDENTITY from GAP_DECISION.json: ruc_mipgap=0.001 ruc_time_limit=1200.0 '
                 '({"ruc_mipgap": 0.001, "ruc_time_limit": 1200, "identity": "v3", "note": "scratch"})')
BASE_COLS = ["index", "oat_site", "unit_type", "bus", "omega", "bid", "gen_pmax", "start_date", "num_days",
             "replicate_of", "pem_mw", "level_id", "tier", "sobol_index"]


def _git(repo, *args):
    subprocess.run(["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@t", *args],
                   check=True, capture_output=True)


def _rows(ds, U, tier_fn, sobol):
    sites = [s["site"] for s in ds["sites"]]
    gp = np.asarray([s["gen_pmax"] for s in ds["sites"]], float)
    rows = []
    for i, u in enumerate(U, start=1):
        x = u * gp
        r = {"index": i, "oat_site": "__ALL__", "unit_type": "", "bus": "", "omega": "", "bid": 40.0, "gen_pmax": "",
             "start_date": "01-01-2019", "num_days": 365, "replicate_of": "", "pem_mw": float(x.sum()),
             "level_id": "", "tier": tier_fn(i - 1), "sobol_index": (i - 1) if sobol else ""}
        for s, v in zip(sites, x):
            r[f"mw_{s}"] = float(v)
        for s, v in zip(sites, u):
            r[f"u_{s}"] = float(v)
        rows.append(r)
    return rows, sites, gp


def write_wave(root, name, rows, sites, gp):
    d = os.path.join(root, "waves", name)
    os.makedirs(d, exist_ok=True)
    cols = BASE_COLS + [f"mw_{s}" for s in sites] + [f"u_{s}" for s in sites]
    pd.DataFrame(rows, columns=cols).to_csv(os.path.join(d, "design_matrix.csv"), index=False)
    for r in rows:
        dct = {s: {"PEM_bid": 40.0, "PEM_fraction": r[f"u_{s}"], "gen_pmax": float(p)}
               for s, p in zip(sites, gp) if r[f"mw_{s}"] > 0}
        with open(os.path.join(d, f"retrofit_gen_dict_{r['index']}.json"), "w") as f:
            json.dump(dct, f, indent=2)
    return d


def fake_collect(root, wave, overrides=None, skip=()):
    """Stand-in for the collector: identity.txt per row (+ stub overrides)."""
    dm = pd.read_csv(os.path.join(root, "waves", wave, "design_matrix.csv"))
    overrides = overrides or {}
    for i in dm["index"].astype(int):
        if i in skip:
            continue
        rd = os.path.join(root, "extracts", wave, f"run_index_{i}")
        os.makedirs(rd, exist_ok=True)
        with open(os.path.join(rd, "identity.txt"), "w") as f:
            f.write(IDENTITY_LINE + "\n")
        stale = os.path.join(rd, "stub_pool_row.json")        # a re-collect replaces earlier overrides
        if os.path.isfile(stale):
            os.remove(stale)
        if i in overrides:
            with open(os.path.join(rd, "stub_pool_row.json"), "w") as f:
                json.dump(overrides[i], f)
    with open(os.path.join(root, "extracts", wave, "COLLECTED"), "w") as f:
        f.write(f"wave={wave} rows={len(dm)} scratch\n")


def build_scratch(tmp, cfg_overrides=None, n0_seed=53, with_git=True, qsub_shim=True):
    """Returns the scratch ERCOT_ROOT path. Sets ERCOT_ROOT in os.environ."""
    repo = os.path.join(tmp, "repo")
    root = os.path.join(repo, "trial_0826", "ercot")
    me = os.path.join(root, "analysis", "methods_E")
    os.makedirs(os.path.join(root, "waves"), exist_ok=True)
    os.makedirs(os.path.join(root, "extracts"), exist_ok=True)
    os.makedirs(os.path.join(root, "tools"), exist_ok=True)
    os.makedirs(os.path.join(repo, "trial_0826", "campaign"), exist_ok=True)
    os.makedirs(me, exist_ok=True)
    for m in MODULES:
        src = os.path.join(HERE, m)
        if os.path.exists(src):
            shutil.copy(src, os.path.join(me, m))
    shutil.copy(os.path.join(LIVE_ROOT, "tools", "make_v2_waves.py"), os.path.join(root, "tools", "make_v2_waves.py"))
    shutil.copy(os.path.join(LIVE_ROOT, "..", "campaign", "get_row.py"), os.path.join(repo, "trial_0826", "campaign", "get_row.py"))
    with open(os.path.join(root, ".gitignore"), "w") as f:
        f.write("extracts/n0_E/**/*.csv.gz\nextracts/random_E/**/*.csv.gz\nextracts/methods_E_*/**/*.csv.gz\n")
    ds = json.load(open(os.path.join(HERE, "_contract_design_space_E.json")))
    with open(os.path.join(root, "waves", "design_space_E.json"), "w") as f:
        json.dump(ds, f, indent=1)
    gap = os.path.join(LIVE_ROOT, "waves", "GAP_DECISION.json")
    if os.path.isfile(gap):
        shutil.copy(gap, os.path.join(root, "waves", "GAP_DECISION.json"))
    U0 = qmc.Sobol(len(ds["sites"]), scramble=True, seed=n0_seed).random(48)
    rows, sites, gp = _rows(ds, U0, lambda i: "nav" if i < 32 else "grading", sobol=True)
    write_wave(root, "n0_E", rows, sites, gp)
    Ur = np.random.default_rng(n0_seed + 1).uniform(size=(48, len(ds["sites"])))
    rows_r, _, _ = _rows(ds, Ur, lambda i: "holdout", sobol=False)
    write_wave(root, "random_E", rows_r, sites, gp)
    fake_collect(root, "n0_E")
    fake_collect(root, "random_E")
    cfg = json.load(open(os.path.join(HERE, "arms_E.json")))
    cfg.setdefault("part_a", {})["sigma_placeholder"] = {"mode": "frac_sd", "frac": 0.02}
    for k, v in (cfg_overrides or {}).items():
        if isinstance(v, dict) and isinstance(cfg.get(k), dict):
            cfg[k].update(v)
        else:
            cfg[k] = v
    ds_cfg = os.path.join(root, cfg["design_space"])           # the dated path arms_E.json names (prompt 66 update)
    if not os.path.isfile(ds_cfg):
        shutil.copy(os.path.join(root, "waves", "design_space_E.json"), ds_cfg)
    with open(os.path.join(me, "arms_E.json"), "w") as f:
        json.dump(cfg, f, indent=1)
    if with_git:
        bare = os.path.join(tmp, "origin.git")
        subprocess.run(["git", "init", "--bare", "-q", bare], check=True)
        subprocess.run(["git", "init", "-q", "-b", cfg["repo_branch"], repo], check=True)
        subprocess.run(["git", "-C", repo, "remote", "add", "origin", bare], check=True)
        _git(repo, "add", "-A"); _git(repo, "commit", "-q", "-m", "seed"); _git(repo, "push", "-q", "origin", cfg["repo_branch"])
    if qsub_shim:
        shim = os.path.join(tmp, "shim")
        os.makedirs(shim, exist_ok=True)
        with open(os.path.join(shim, "qsub"), "w") as f:
            f.write('#!/bin/bash\necho "QSUB CALLED $@" >> "$SHIM_LOG"\nexit 1\n')
        with open(os.path.join(shim, "qstat"), "w") as f:
            f.write("#!/bin/bash\nexit 0\n")
        for n in ("qsub", "qstat"):
            os.chmod(os.path.join(shim, n), 0o755)
        os.environ["PATH"] = shim + os.pathsep + os.environ["PATH"]
        os.environ["SHIM_LOG"] = os.path.join(tmp, "qsub.log")
    os.environ["ERCOT_ROOT"] = root
    return root


def lane_modules(root):
    """Import the machinery FROM the scratch copy (so its arms_E.json is the config)."""
    me = os.path.join(root, "analysis", "methods_E")
    for m in list(sys.modules):
        if m in ("common_E", "_stub_loader", "tau_E", "qnehvi_E", "wave_writer_E", "acquire_E"):
            del sys.modules[m]
    sys.path.insert(0, me)
    import acquire_E  # noqa: E402
    return acquire_E


def cheap_propose(U, Y, ref_point, cfgs, floors, seed, q=8, qcfg=None, shed=None, shed_limit=None, fitters=None,
                  guardrail_mode="monitor", log=print):
    """Test stand-in for qnehvi_E.propose with the SAME return schema: q random
    u rows (not in U), predictions = training mean / sd. Exercises every ledger,
    guardrail and halt path without the 100-s acquisition. The constrained
    branch is reported the way qnehvi_E does (degenerate shed -> dropped)."""
    rng = np.random.default_rng(int(seed))
    U = np.asarray(U, float); Y = np.asarray(Y, float)
    ub = rng.uniform(size=(q, U.shape[1]))
    ub[0, 1] = 0.0                                             # an exact zero (site absent) every batch
    pm = np.tile(Y.mean(0), (q, 1)); ps = np.tile(np.where(Y.std(0) > 0, Y.std(0), 1.0), (q, 1))
    if guardrail_mode == "constrain" and shed is not None:
        constraint = "degenerate_constant" if np.std(shed) == 0 else f"shed <= {shed_limit} MWh (GP on the accumulated R1 column)"
    else:
        constraint = "none"
    return {"u_batch": ub, "acq_values": [0.0] * q, "pred_mean": pm, "pred_sd": ps, "seconds": 0.0, "fit": None,
            "transforms": ["std"] * Y.shape[1], "loo_rms_z": [1.0] * Y.shape[1], "noise_raw": [0.0] * Y.shape[1],
            "settings": {"cheap_stand_in": True, "constraint": constraint, "guardrail_mode": guardrail_mode,
                         "seed": int(seed), "num_restarts": 0, "raw_samples": 0, "fast_mode": False}}
