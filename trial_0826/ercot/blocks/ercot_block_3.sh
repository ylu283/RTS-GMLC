#!/bin/bash
# ERCOT paste-block #3 — BASE SUBMISSION + smoke extract (prompt 26 T3).
# Run ON CRC after ercot_block_2.sh printed BLOCK 2 DONE (and any rider
# banner was acted on):
#   bash ercot_block_3.sh 2>&1 | tee ercot_block_3.log
# Submits the full-year base (TL=120, ~15-22 h; 'long' queue carried the
# prior 113 h base, so wall headroom >> the required 48-72 h) + ONE
# chained collector (hold_jid; -M/-m ea on the COLLECTOR only). Also
# extracts + pushes the 3-day smoke so the anatomy notebook can be drafted
# locally against it while the base queues.

set -euo pipefail

ERCOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
REPO_DIR="$(cd "$ERCOT_DIR/../.." && pwd)"

BRANCH="$(git -C "$REPO_DIR" branch --show-current)"
[[ "$BRANCH" == "ercot/tx123" ]] || { echo "ABORT: worktree on '$BRANCH', expected ercot/tx123"; exit 1; }
git -C "$REPO_DIR" pull --rebase --autostash origin ercot/tx123

if [[ "${SKIP_SMOKE_CHECK:-0}" != "1" ]] && \
   [[ ! -f "$ERCOT_DIR/smoke/run_index_smoke_3d/overall_simulation_output.csv" ]]; then
    echo "ABORT: no smoke sentinel — run ercot_block_2.sh first (or SKIP_SMOKE_CHECK=1)."
    exit 1
fi

# --- smoke extract -> committed, so local anatomy drafting can start -------
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate PCM_ERCOT
export PYTHONNOUSERSITE=1  # ~/.local vanilla prescient shadows the patched editable install
JOBLOG=$(ls -t "$ERCOT_DIR"/smoke/ercot_smoke_3d.o* 2>/dev/null | head -1 || true)
python "$ERCOT_DIR/extract_ercot.py" \
    "$ERCOT_DIR/smoke/run_index_smoke_3d" \
    "$ERCOT_DIR/extracts/smoke_3d" --full \
    ${JOBLOG:+--joblog "$JOBLOG"}
git -C "$REPO_DIR" add -- "$ERCOT_DIR/extracts/smoke_3d"
git -C "$REPO_DIR" -c user.name="ercot-bot" -c user.email="ercot-bot@noreply.github.com" \
    commit -m "ercot-bot: smoke_3d extract (anatomy drafting input)"
git -C "$REPO_DIR" push origin ercot/tx123 || {
    git -C "$REPO_DIR" pull --rebase --autostash origin ercot/tx123
    git -C "$REPO_DIR" push origin ercot/tx123
}

# --- base + chained collector ----------------------------------------------
cd "$ERCOT_DIR/waves/base_2019"
J=$(qsub -terse base_job.sh)
[[ "$J" =~ ^[0-9]+$ ]] || { echo "BAD JID: $J"; exit 1; }
echo "base submitted: J=$J (ETA ~15-22 h)"
qsub -hold_jid "$J" -cwd -M ylu28@nd.edu -m ea collect_base_2019.sh
echo "collector submitted (holds on $J); it gates, extracts (incl. ruc_quality.csv) and bot-pushes to ercot/tx123."

qstat -u ylu28
echo "BLOCK 3 DONE — run ercot_block_4.sh (screening) any time; it confirms the site ranking against the base extract if it has landed, else submits on the proxy ranking (Sep-30 protection)."
