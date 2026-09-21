#!/bin/bash
# ERCOT paste-block #4b — SCREENING, both arms (prompt 26 T4, 2026-09-21).
# SUPERSEDES ercot_block_4.sh — run THIS one:
#   bash ercot_block_4b.sh 2>&1 | tee ercot_block_4b.log
#
# Why: the base_2019 extract confirmed the availability proxy is a poor
# curtailment predictor (only 275/274/30 of the drafted 9 are in the
# actual top-12; curtailment concentrates at congestion-trapped sites —
# bus 120 alone hosts 5 of the top-8). Resolution is a TWO-ARM design:
#   arm 1 = screening_ercot (v1, 12 rows): availability/contrast arm +
#           __ALL__ + the 2 replicate noise-ruler rows;
#   arm 2 = screening_topup (7 rows): the actual top curtailers missing
#           from v1. Both arms together cover the actual top-10 exactly.
# This block is safe in BOTH histories:
#   - if block #4 was never run (or its ranking gate stopped it), this
#     submits BOTH arms;
#   - if block #4 proxy-submitted v1 before the base landed, this detects
#     v1 (queue or run dirs) and submits ONLY the top-up arm.

set -euo pipefail

ERCOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
REPO_DIR="$(cd "$ERCOT_DIR/../.." && pwd)"

BRANCH="$(git -C "$REPO_DIR" branch --show-current)"
[[ "$BRANCH" == "ercot/tx123" ]] || { echo "ABORT: worktree on '$BRANCH', expected ercot/tx123"; exit 1; }
git -C "$REPO_DIR" pull --rebase --autostash origin ercot/tx123

[[ -f "$ERCOT_DIR/waves/screening_topup/design_matrix.csv" ]] \
    || { echo "ABORT: screening_topup wave missing after pull"; exit 1; }

# --- arm 1 (v1): submit only if not already in flight/ran -------------------
V1_DIR="$ERCOT_DIR/waves/screening_ercot"
v1_state="not submitted"
if qstat -j screening_ercot_array >/dev/null 2>&1; then
    v1_state="in queue"
elif compgen -G "$V1_DIR/runs/run_index_*" >/dev/null; then
    v1_state="has run dirs (submitted earlier)"
fi
echo "v1 (screening_ercot) state: $v1_state"

if [[ "$v1_state" == "not submitted" ]]; then
    cd "$V1_DIR"
    J1=$(qsub -terse -t 1-12 screening_ercot_array.sh | cut -d. -f1)
    [[ "$J1" =~ ^[0-9]+$ ]] || { echo "BAD JID: $J1"; exit 1; }
    echo "arm 1 (v1, 12 tasks incl. __ALL__ + 2 replicates) submitted: J1=$J1"
    qsub -hold_jid "$J1" -cwd -M ylu28@nd.edu -m ea collect_screening_ercot.sh
    echo "arm-1 collector submitted (holds on $J1)"
else
    echo "arm 1 already in flight — leaving it alone (its own collector handles it)."
fi

# --- arm 2 (top-up): always submitted by this block -------------------------
cd "$ERCOT_DIR/waves/screening_topup"
if compgen -G "runs/run_index_*" >/dev/null || qstat -j screening_topup_array >/dev/null 2>&1; then
    echo "ABORT: screening_topup already submitted — this block already ran?"
    exit 1
fi
J2=$(qsub -terse -t 1-7 screening_topup_array.sh | cut -d. -f1)
[[ "$J2" =~ ^[0-9]+$ ]] || { echo "BAD JID: $J2"; exit 1; }
echo "arm 2 (top-up, 7 curtailment-arm tasks) submitted: J2=$J2"
qsub -hold_jid "$J2" -cwd -M ylu28@nd.edu -m ea collect_screening_topup.sh
echo "arm-2 collector submitted (holds on $J2); each arm bot-pushes its own extracts."

qstat -u ylu28
echo "BLOCK 4b DONE — qstat above is the submission evidence."
