#!/bin/bash
# selection_t1 — smoke -> array -> collector (prompt 32 T1).
# Run ON CRC from anywhere:  bash submit_this.sh
cd "$(dirname "${BASH_SOURCE[0]}")"
set -euo pipefail
WAVE_DIR="$PWD"
ERCOT_DIR="$(cd "$PWD/../.." && pwd)"
REPO_DIR="$(cd "$ERCOT_DIR/../.." && pwd)"

BRANCH="$(git -C "$REPO_DIR" branch --show-current)"
[[ "$BRANCH" == "ercot/tx123" ]] || { echo "ABORT: on '$BRANCH', expected ercot/tx123"; exit 1; }
git -C "$REPO_DIR" pull --rebase --autostash origin ercot/tx123

S=$(qsub -terse selection_t1_smoke.sh | cut -d. -f1)
[[ "$S" =~ ^[0-9]+$ ]] || { echo "BAD SMOKE JID: $S"; exit 1; }
J=$(qsub -terse -hold_jid "$S" -t 1-11 selection_t1_array.sh | cut -d. -f1)
[[ "$J" =~ ^[0-9]+$ ]] || { echo "BAD ARRAY JID: $J"; exit 1; }
C=$(qsub -terse -hold_jid "$J" -cwd -M ylu28@nd.edu -m ea collect_selection_t1.sh)
[[ "$C" =~ ^[0-9]+$ ]] || { echo "BAD COLLECTOR JID: $C"; exit 1; }
echo "SUBMITTED selection_t1: smoke=$S array=$J collector=$C"
qstat -u ylu28
