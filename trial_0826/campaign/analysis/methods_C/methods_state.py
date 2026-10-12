#!/usr/bin/env python3
"""Prompt 35 §4 — the bastion state machine behind submit_ready.sh.

Idempotent: state is keyed on the SUBMITTED lines (+ JIDs) appended to
analysis/methods_C/PROGRESS.md and on what the clone holds after
`git pull --ff-only` (wave dirs, objectives.csv, ledgers, markers) — never
on qstat job names. Each run submits everything READY, appends one
SUBMITTED line per submission, and prints a state table.

Per standalone wave (S2, S3, Q1-Q3): BUILT -> SUBMITTED -> LANDED | FAILED.
Per arm (P1, P2, P3, N1), for the first round k that is not yet graded:
    WAIT_BASE        P2/P3 start set not landed yet
    READY_ACQ0       start set landed, no ledger: submit acquisition round 0
    READY_ARRAY      wave k proposed, not submitted: submit array + collector
    SUBMITTED        wave k array/collector in flight (incl. held)
    FAILED           FAILED marker in wave k (resubmit once by hand, §5)
    READY_ACQ        wave k landed: submit acquisition k (+ held k+1 in hold mode)
    ACQ_SUBMITTED    acquisition submitted, round k+1 not proposed yet
    WEDGED           WEDGED_/FAILED_ marker from the acquisition
    DONE             all rounds to hard_cap graded (or DONE_<arm>.md)

Hold mode (default): together with acquisition k, submit round k+1's array
(held on the acquisition) and collector (held on that array); the array task
reads its design at start and fails loudly if the acquisition wrote none.

Usage: methods_state.py [--execute] [--no-hold] [--campaign DIR]
Without --execute: DRY RUN (prints the qsub commands it would run).
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import re
import shlex
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
EMAIL = "ylu28@nd.edu"
STANDALONE = ["methods_C_S2_n0", "methods_C_S3_n0", "methods_C_Q1", "methods_C_Q2", "methods_C_Q3"]
BASE_OF = {"P2": "methods_C_S2_n0", "P3": "methods_C_S3_n0"}

RE_WAVE = re.compile(r"^SUBMITTED wave=(\S+) array=(\d+) collector=(\d+)(?: held_on=(\d+))?\s*$")
RE_ACQ = re.compile(r"^SUBMITTED acq arm=(\S+) round=(\d+) acq=(\d+)\s*$")


def parse_progress(text):
    waves, acqs = {}, {}
    for line in text.splitlines():
        m = RE_WAVE.match(line.strip())
        if m:
            waves[m.group(1)] = {"array": m.group(2), "collector": m.group(3), "held_on": m.group(4)}
        m = RE_ACQ.match(line.strip())
        if m:
            acqs[(m.group(1), int(m.group(2)))] = m.group(3)
    return waves, acqs


def _rows(path):
    try:
        with open(path) as f:
            return max(0, sum(1 for _ in f) - 1)
    except FileNotFoundError:
        return None


def wave_status(waves_root, wave):
    d = os.path.join(waves_root, wave)
    if not os.path.isfile(os.path.join(d, "design_matrix.csv")):
        return "ABSENT", 0
    n = _rows(os.path.join(d, "design_matrix.csv"))
    if glob.glob(os.path.join(d, "FAILED_*")):
        return "FAILED", n
    ob = _rows(os.path.join(d, "objectives.csv"))
    if ob is not None and ob == n:
        return "LANDED", n
    return "PROPOSED", n


def _graded_rounds(arm_dir):
    p = os.path.join(arm_dir, "ledger.json")
    if not os.path.isfile(p):
        return None
    return {int(e["round"]) for e in json.load(open(p))["entries"] if e.get("gain") is not None}


def arm_state(campaign, cfg, arm, waves, acqs):
    """(state, round, detail) for the first un-graded round of `arm`."""
    sys.path.insert(0, HERE)
    a = cfg["arms"][arm]
    adir = os.path.join(campaign, a["dir"])
    wroot = os.path.join(campaign, "waves")
    rwave = lambda k: a["round_waves"].get(str(k)) or a["round_wave_pattern"].format(k=k)
    if glob.glob(os.path.join(adir, f"DONE_{arm}.md")):
        return "DONE", None, "DONE marker"
    graded = _graded_rounds(adir)
    if graded is None:
        base = BASE_OF.get(arm)
        if base is None:
            return "NEEDS_LOCAL_INIT", 0, "P1/N1 are initialized locally at T0"
        st, _ = wave_status(wroot, base)
        if st != "LANDED":
            return "WAIT_BASE", 0, f"{base}: {st}"
        if (arm, 0) in acqs:
            return _acq_wait(adir, arm, 0, acqs[(arm, 0)])
        return "READY_ACQ0", 0, f"{base} landed"
    for k in range(1, cfg["hard_cap"] + 1):
        if k in graded:
            continue
        w = rwave(k)
        st, n = wave_status(wroot, w)
        if st == "ABSENT":
            if (arm, k - 1) in acqs:
                return _acq_wait(adir, arm, k - 1, acqs[(arm, k - 1)])
            return "STALLED", k, f"{w} not proposed and no acquisition {k - 1} logged — inspect"
        if st == "FAILED":
            return "FAILED", k, f"{w}: FAILED marker"
        if st == "LANDED":
            if (arm, k) in acqs:
                return _acq_wait(adir, arm, k, acqs[(arm, k)])
            return "READY_ACQ", k, f"{w} landed"
        if w in waves:
            return "SUBMITTED", k, f"{w}: array={waves[w]['array']} collector={waves[w]['collector']}"
        return "READY_ARRAY", k, f"{w} proposed ({n} rows)"
    return "DONE", None, "all rounds graded"


def _acq_wait(adir, arm, k, jid):
    bad = glob.glob(os.path.join(adir, f"WEDGED_{arm}_r{k}.md")) + glob.glob(os.path.join(adir, f"FAILED_{arm}_r{k}.md"))
    if bad:
        return "WEDGED", k, f"{os.path.basename(bad[0])} (acq {jid})"
    return "ACQ_SUBMITTED", k, f"acq {jid} grading r{k} / proposing r{k + 1}"


class Submitter:
    def __init__(self, campaign, execute, log_lines):
        self.c = campaign
        self.execute = execute
        self.lines = log_lines
        self.mc = os.path.join(campaign, "analysis", "methods_C")
        self.waves = os.path.join(campaign, "waves")
        self._fake = 900000

    def qsub(self, args):
        cmd = ["qsub", "-terse"] + args
        print("  $", " ".join(shlex.quote(x) for x in cmd))
        if not self.execute:
            self._fake += 1
            return str(self._fake)
        out = subprocess.run(cmd, capture_output=True, text=True, check=True).stdout.strip()
        jid = out.split(".")[0]
        if not re.fullmatch(r"\d+", jid):
            raise RuntimeError(f"BAD JID from qsub: {out!r}")
        return jid

    def wave(self, wave, n, hold=None):
        logs = os.path.join(self.waves, "methods_C_logs")  # gitignored; exists before any hold
        if self.execute:
            os.makedirs(logs, exist_ok=True)
        out = ["-o", logs + "/", "-e", logs + "/"]
        array = self.qsub(["-r", "n", "-wd", self.waves, "-v", f"WAVE={wave}", "-t", f"1-{n}",
                           "-N", f"{wave}_array"] + out + (["-hold_jid", hold] if hold else [])
                          + [os.path.join(self.mc, "methods_array.sh")])
        coll = self.qsub(["-r", "n", "-wd", self.waves, "-v", f"WAVE={wave}", "-hold_jid", array,
                          "-N", f"collect_{wave}"] + out + ["-M", EMAIL, "-m", "ea",
                          os.path.join(self.mc, "methods_collect.sh")])
        self.lines.append(f"SUBMITTED wave={wave} array={array} collector={coll}"
                          + (f" held_on={hold}" if hold else ""))
        return array, coll

    def acq(self, arm, k):
        logs = os.path.join(self.mc, arm, "logs")
        if self.execute:
            os.makedirs(logs, exist_ok=True)
        jid = self.qsub(["-wd", self.c, "-v", f"ARM={arm},BO_ROUND={k}", "-N", f"methods_C_{arm}_r{k + 1}",
                         "-pe", "smp", "4", "-r", "n", "-o", logs + "/", "-e", logs + "/",
                         "-M", EMAIL, "-m", "ea", os.path.join(self.mc, "acquire_arm_job.sh")])
        self.lines.append(f"SUBMITTED acq arm={arm} round={k} acq={jid}")
        return jid


def run(campaign, execute=False, hold=True, out=print):
    cfg = json.load(open(os.path.join(campaign, "analysis", "methods_C", "arms.json")))
    prog = os.path.join(campaign, "analysis", "methods_C", "PROGRESS.md")
    waves, acqs = parse_progress(open(prog).read() if os.path.isfile(prog) else "")
    new_lines = []
    sub = Submitter(campaign, execute, new_lines)
    table = []
    wroot = os.path.join(campaign, "waves")
    for w in STANDALONE:
        st, n = wave_status(wroot, w)
        if st == "PROPOSED" and w not in waves:
            out(f"[{w}] BUILT -> submitting array ({n}) + collector")
            sub.wave(w, n)
            st = "SUBMITTED (now)"
        elif st == "PROPOSED":
            st = "SUBMITTED"
        table.append((w, st, ""))
    for arm in cfg["arms"]:
        st, k, detail = arm_state(campaign, cfg, arm, waves, acqs)
        a = cfg["arms"][arm]
        rwave = lambda kk: a["round_waves"].get(str(kk)) or a["round_wave_pattern"].format(k=kk)
        if st == "READY_ARRAY":
            out(f"[{arm}] r{k} READY_ARRAY -> submitting {rwave(k)}")
            sub.wave(rwave(k), cfg["q"])
            st = "SUBMITTED (now)"
        elif st in ("READY_ACQ", "READY_ACQ0"):
            out(f"[{arm}] {st} r{k} -> submitting acquisition {k}"
                + (f" + held {rwave(k + 1)}" if hold and k + 1 <= cfg["hard_cap"] else ""))
            jid = sub.acq(arm, k)
            if hold and k + 1 <= cfg["hard_cap"]:
                sub.wave(rwave(k + 1), cfg["q"], hold=jid)
            st = "ACQ_SUBMITTED (now)"
        table.append((arm, st, f"r{k} {detail}" if k is not None else detail))
    out("\nmethods_C state" + ("" if execute else " (DRY RUN — nothing submitted)"))
    for name, st, detail in table:
        out(f"  {name:18s} {st:22s} {detail}")
    if execute and new_lines:
        with open(prog, "a") as f:
            f.write("\n".join(new_lines) + "\n")
    return new_lines, table


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--campaign", default=os.path.abspath(os.path.join(HERE, "..", "..")))
    ap.add_argument("--execute", action="store_true")
    ap.add_argument("--no-hold", action="store_true")
    a = ap.parse_args(argv)
    lines, _ = run(a.campaign, execute=a.execute, hold=not a.no_hold)
    print(f"\n{len(lines)} SUBMITTED line(s)" + ("" if a.execute else " would be") + " appended")
    return 0


if __name__ == "__main__":
    sys.exit(main())
