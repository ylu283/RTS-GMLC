"""Prompt 43 Amendment 1 (Kay, 2026-10-25): resolve the
STOP-FOR-DECISION. Writes winner_commit.json naming BOTH roles,
pre-declared BEFORE any holdout scoring exists:

- PRIMARY: rbf+log1p+(ii) — the competing-walk winner; the §7 bar and
  PASS/FAIL verdict attach to the primary only.
- CONTROL: rbf+log1p+285.3 (the crowned reference) — identical
  machinery, separately labeled outputs, NO verdict.

STOP_FOR_DECISION.json stays in place for the record. The stored
loo_table hash is recomputed here and must match the one recorded at
the STOP (the table has not changed since selection).

Run: /opt/anaconda3/envs/bogp-botorch/bin/python commit_amendment1.py
"""
from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))

PRIMARY = {"name": "rbf+log1p+ii", "kernel": "rbf", "transform": "log1p",
           "noise_form": "ii", "idx": 4, "role": "primary"}
CONTROL = {"name": "rbf+log1p+ref", "kernel": "rbf", "transform": "log1p",
           "noise_form": "ref", "idx": 10, "role": "control"}


def main():
    with open(os.path.join(HERE, "STOP_FOR_DECISION.json")) as fh:
        stop = json.load(fh)
    assert stop["walks"]["walk8_winner"] == PRIMARY["name"]
    assert stop["walks"]["walk12_crowned"] == CONTROL["name"]
    with open(os.path.join(HERE, "loo_table.csv"), "rb") as fh:
        table_hash = hashlib.sha256(fh.read()).hexdigest()
    assert table_hash == stop["loo_table_sha256"], \
        "loo_table.csv changed since the STOP — refuse to commit"
    commit = {
        "amendment": 1,
        "decision": "grade BOTH and compare in the results deck; the "
                    "bar and PASS/FAIL verdict attach to the PRIMARY "
                    "only; the control carries NO verdict; if the "
                    "control grades better on any criterion that is a "
                    "RECORDED FINDING, never a re-selection",
        "primary": PRIMARY,
        "control": CONTROL,
        "selection": stop["walks"],
        "loo_table_sha256": table_hash,
        "committed_at_utc": datetime.now(timezone.utc).isoformat(
            timespec="seconds")}
    with open(os.path.join(HERE, "winner_commit.json"), "w") as fh:
        json.dump(commit, fh, indent=2)
        fh.write("\n")
    print("winner_commit.json written (Amendment 1): primary",
          PRIMARY["name"], "control", CONTROL["name"], "hash", table_hash)


if __name__ == "__main__":
    main()
