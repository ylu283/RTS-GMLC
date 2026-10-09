#!/bin/bash
# tl360_probe — array -> collector (prompt 33). Run ON CRC from anywhere:
#   bash submit_this.sh
cd "$(dirname "${BASH_SOURCE[0]}")"
set -euo pipefail
ERCOT_DIR="$(cd "$PWD/../.." && pwd)"
REPO_DIR="$(cd "$ERCOT_DIR/../.." && pwd)"
BRANCH="$(git -C "$REPO_DIR" branch --show-current)"
[[ "$BRANCH" == "ercot/tx123" ]] || { echo "ABORT: on '$BRANCH', expected ercot/tx123"; exit 1; }
git -C "$REPO_DIR" pull --rebase --autostash origin ercot/tx123

J=$(qsub -terse -t 1-3 tl360_probe_array.sh | cut -d. -f1)
[[ "$J" =~ ^[0-9]+$ ]] || { echo "BAD ARRAY JID: $J"; exit 1; }
C=$(qsub -terse -hold_jid "$J" -cwd -M ylu28@nd.edu -m ea collect_tl360_probe.sh)
[[ "$C" =~ ^[0-9]+$ ]] || { echo "BAD COLLECTOR JID: $C"; exit 1; }
echo "SUBMITTED tl360_probe: array=$J collector=$C"
qstat -u ylu28
