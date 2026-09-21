#!/bin/bash
# ERCOT paste-block #5 — BASE RECOVERY (contingency block, activated by the
# FAILED_base_2019.md marker of 2026-09-20). Run ON CRC:
#   bash ercot_block_5.sh 2>&1 | tee ercot_block_5.log
# Diagnosis (done locally, fix pushed as de4fb43): the base died at t~1 s
# because prescient creates the run dir with os.mkdir and the parent
# waves/base_2019/runs/ did not exist. base_job.sh now does
# `mkdir -p "$WAVE_DIR/runs"` before the run, and the collector clears the
# stale FAILED marker on success. This block pulls the fix, verifies it is
# actually present, and resubmits base + chained collector (same shape as
# block #3's submission tail). Block #4 (screening) is independent — run it
# whenever; it proxy-submits if the base extract has not landed.

set -euo pipefail

ERCOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
REPO_DIR="$(cd "$ERCOT_DIR/../.." && pwd)"

BRANCH="$(git -C "$REPO_DIR" branch --show-current)"
[[ "$BRANCH" == "ercot/tx123" ]] || { echo "ABORT: worktree on '$BRANCH', expected ercot/tx123"; exit 1; }
git -C "$REPO_DIR" pull --rebase --autostash origin ercot/tx123

# --- verify the fix is really in the tree we are about to qsub -------------
git -C "$REPO_DIR" merge-base --is-ancestor de4fb4328ad8788a771fe1b7efd8b75fbed58ab7 HEAD \
    || { echo "ABORT: fix commit de4fb43 not an ancestor of HEAD — pull failed?"; exit 1; }
grep -q 'mkdir -p "$WAVE_DIR/runs"' "$ERCOT_DIR/waves/base_2019/base_job.sh" \
    || { echo "ABORT: mkdir fix missing from base_job.sh"; exit 1; }
echo "fix verified: de4fb43 in HEAD, mkdir -p present in base_job.sh"

cd "$ERCOT_DIR/waves/base_2019"

# --- failure-evidence record for the block log (workflow-pain input) -------
OLDLOG=$(ls -t ercot_base_2019.o* 2>/dev/null | head -1 || true)
if [[ -n "$OLDLOG" ]]; then
    echo "--- tail of failed attempt log $OLDLOG ---"
    tail -15 "$OLDLOG"
    echo "-------------------------------------------"
fi

# clear any partial run dir from the failed attempt (prescient's os.mkdir
# also dies on an EXISTING dir; the failed attempt produced at most an
# empty/1-second partial — full-year runs have no mid-year restart anyway)
if [[ -d runs/run_index_base ]]; then
    echo "removing partial run dir runs/run_index_base ($(du -sh runs/run_index_base | cut -f1))"
    rm -rf runs/run_index_base
fi

# --- resubmit: base + ONE chained collector (identical to block #3 tail) ---
J=$(qsub -terse base_job.sh)
[[ "$J" =~ ^[0-9]+$ ]] || { echo "BAD JID: $J"; exit 1; }
echo "base resubmitted: J=$J (ETA ~15-22 h)"
qsub -hold_jid "$J" -cwd -M ylu28@nd.edu -m ea collect_base_2019.sh
echo "collector submitted (holds on $J); on success it clears the FAILED marker and bot-pushes extracts/base_2019 to ercot/tx123."

qstat -u ylu28
echo "BLOCK 5 DONE — nothing else changes: block #4 runs independently whenever you want the screening in the queue."
