#!/usr/bin/env python3
"""Prompt 55 — the login-node state machine behind submit_ready_E.sh (port of
the RTS methods_state.py, trimmed to one arm x seeds).

Idempotent: the state of a lane is read from the pulled clone only — ledger,
round_records.json, wave dirs, `extracts/<wave>/COLLECTED`, the
`waves/<wave>/SUBMITTED` marker this script writes, and the lane markers
(HALT_FOR_DECISION.md, DONE.md, FAILED_r*.md, WEDGED_r*.md) — never from
qstat job names. Each run submits everything READY and writes one SUBMITTED
marker per submission (committed + pushed by submit_ready_E.sh).

Per lane (arm, seed), with k = the first round not yet graded:
    NO_LEDGER       -> READY_ACQ0: qsub acquisition BO_ROUND=0 (init + propose r1)
                       [+ hold mode: array r1 held on it, collector held on the array]
    PROPOSED k      -> READY_ARRAY: wave k exists, no SUBMITTED marker, not COLLECTED:
                       qsub array (-t 1-q) + collector (-hold_jid array)
    SUBMITTED k     -> in flight (array/collector), wait for the collector email
    COLLECTED k     -> READY_ACQ: qsub acquisition BO_ROUND=k (grade k, propose k+1)
                       [+ hold mode: array k+1 held on it, collector held on the array]
    ACQ_SUBMITTED   -> acquisition in flight (SUBMITTED acq marker), round k+1 not proposed yet
    HALT / DONE / FAILED / WEDGED -> printed; nothing submitted (Kay acts)

Usage: submit_state_E.py [--execute] [--no-hold] [--root DIR]
Without --execute: DRY RUN (prints the qsub commands).
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import shlex
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
EMAIL = "ylu28@nd.edu"


def _lane_dir(root, cfg, arm, s):
    return os.path.join(root, cfg["arms"][arm]["lane_dir_pattern"].format(seed=s))


def _wave(cfg, arm, s, k):
    return cfg["arms"][arm]["round_wave_pattern"].format(seed=s, k=k)


def _marker(root, wave):
    return os.path.join(root, "waves", wave, "SUBMITTED")


def _acq_marker(ldir, k):
    return os.path.join(ldir, f"SUBMITTED_acq_r{k}")


def _graded(ldir):
    p = os.path.join(ldir, "ledger.json")
    if not os.path.isfile(p):
        return None
    return len(json.load(open(p))["entries"]) - 1


def _proposed(ldir):
    p = os.path.join(ldir, "round_records.json")
    if not os.path.isfile(p):
        return set()
    return {int(k) for k in json.load(open(p))}


def lane_state(root, cfg, arm, s):
    ldir = _lane_dir(root, cfg, arm, s)
    q, cap = cfg["q"], cfg["hard_cap"]
    for name in ("HALT_FOR_DECISION.md", "DONE.md"):
        if os.path.isfile(os.path.join(ldir, name)):
            return {"state": name.split(".")[0], "k": None, "note": os.path.join(ldir, name)}
    bad = sorted(glob.glob(os.path.join(ldir, "FAILED_r*.md")) + glob.glob(os.path.join(ldir, "WEDGED_r*.md")))
    if bad:
        return {"state": "FAILED/WEDGED", "k": None, "note": ", ".join(os.path.basename(b) for b in bad)}
    g = _graded(ldir)
    if g is None:
        if os.path.isfile(_acq_marker(ldir, 0)):
            return {"state": "ACQ_SUBMITTED", "k": 0, "note": "init + r1 in flight"}
        return {"state": "READY_ACQ0", "k": 0, "note": "no ledger"}
    k = g + 1
    if k > cap:
        return {"state": "DONE(cap)", "k": None, "note": f"{g} rounds graded"}
    wave = _wave(cfg, arm, s, k)
    wdir = os.path.join(root, "waves", wave)
    if k not in _proposed(ldir) or not os.path.isdir(wdir):
        if os.path.isfile(_acq_marker(ldir, g)):
            return {"state": "ACQ_SUBMITTED", "k": g, "note": f"acquisition r{g} in flight; r{k} not proposed yet"}
        return {"state": "WAIT_PROPOSE", "k": k, "note": f"round {k} not proposed (run the acquisition for round {g})"}
    if glob.glob(os.path.join(wdir, "FAILED_*")):
        return {"state": "WAVE_FAILED", "k": k, "note": wave}
    if os.path.isfile(os.path.join(root, "extracts", wave, "COLLECTED")):
        if os.path.isfile(_acq_marker(ldir, k)):
            return {"state": "ACQ_SUBMITTED", "k": k, "note": f"acquisition r{k} in flight"}
        return {"state": "READY_ACQ", "k": k, "note": f"{wave} COLLECTED, round {k} not graded"}
    if os.path.isfile(_marker(root, wave)):
        return {"state": "SUBMITTED", "k": k, "note": open(_marker(root, wave)).read().strip()}
    return {"state": "READY_ARRAY", "k": k, "note": f"{wave} proposed, not submitted"}


def _qsub(cmd, execute, out):
    out("  " + " ".join(shlex.quote(c) for c in cmd))
    if not execute:
        return "DRY"
    r = subprocess.run(cmd, capture_output=True, text=True, check=True)
    jid = r.stdout.strip().split(".")[0]
    assert jid.isdigit(), f"bad JID {r.stdout!r}"
    return jid


def run(root, execute=False, hold=True, out=print):
    cfg = json.load(open(os.path.join(HERE, "arms_E.json")))
    waves_dir = os.path.join(root, "waves")
    q = cfg["q"]
    written = []
    for arm, a in cfg["arms"].items():
        for s in a["seed_ids"]:
            st = lane_state(root, cfg, arm, s)
            ldir = _lane_dir(root, cfg, arm, s)
            out(f"{arm} s{s}: {st['state']}  {st['note']}")
            os.makedirs(os.path.join(ldir, "logs"), exist_ok=True)

            def acq(k):
                return _qsub(["qsub", "-terse", "-wd", root, "-v", f"ARM={arm},SEED={s},BO_ROUND={k}",
                              "-N", f"methods_E_{arm}_s{s}_acq_r{k + 1}", "-pe", "smp", "4", "-r", "n",
                              "-o", os.path.join(ldir, "logs"), "-e", os.path.join(ldir, "logs"),
                              os.path.join(HERE, "acquire_E_job.sh")], execute, out)

            def array(wave, hold_on=None):
                cmd = ["qsub", "-terse", "-wd", waves_dir, "-v", f"WAVE={wave}", "-t", f"1-{q}", "-r", "n",
                       "-N", f"{wave}_array"]
                if hold_on:
                    cmd += ["-hold_jid", str(hold_on)]
                return _qsub(cmd + [os.path.join(HERE, "methods_E_array.sh")], execute, out)

            def collector(wave, hold_on):
                return _qsub(["qsub", "-terse", "-wd", waves_dir, "-v", f"WAVE={wave}", "-hold_jid", str(hold_on),
                              "-r", "n", "-N", f"collect_{wave}", "-M", EMAIL, "-m", "ea",
                              os.path.join(HERE, "methods_E_collect.sh")], execute, out)

            def mark(path, text):
                if execute:
                    os.makedirs(os.path.dirname(path), exist_ok=True)
                    with open(path, "w") as f:
                        f.write(text + "\n")
                    written.append(path)

            if st["state"] in ("READY_ACQ0", "READY_ACQ"):
                k = st["k"]
                j = acq(k)
                mark(_acq_marker(ldir, k), f"acq round={k} jid={j}")
                if hold and k + 1 <= cfg["hard_cap"]:
                    nxt = _wave(cfg, arm, s, k + 1)
                    ja = array(nxt, hold_on=j)
                    jc = collector(nxt, hold_on=ja)
                    mark(_marker(root, nxt), f"wave={nxt} array={ja} collector={jc} held_on={j}")
            elif st["state"] == "READY_ARRAY":
                wave = _wave(cfg, arm, s, st["k"])
                ja = array(wave)
                jc = collector(wave, hold_on=ja)
                mark(_marker(root, wave), f"wave={wave} array={ja} collector={jc}")
    return written


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--execute", action="store_true")
    ap.add_argument("--no-hold", action="store_true")
    ap.add_argument("--root", default=os.path.abspath(os.path.join(HERE, "..", "..")))
    args = ap.parse_args(argv)
    w = run(args.root, execute=args.execute, hold=not args.no_hold)
    for p in w:
        print("MARKER", p)
    return 0


if __name__ == "__main__":
    sys.exit(main())
