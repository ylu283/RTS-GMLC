#!/bin/bash
# Prompt 36 smoke — run ON CRC (Kay, by hand):  bash submit_this.sh
cd "$(dirname "${BASH_SOURCE[0]}")"
set -euo pipefail
REPO_DIR="$(cd ../../../.. && pwd)"
BRANCH="$(git -C "$REPO_DIR" branch --show-current)"
[[ "$BRANCH" == "ercot/tx123" ]] || { echo "ABORT: on '$BRANCH', expected ercot/tx123"; exit 1; }
git -C "$REPO_DIR" pull --rebase --autostash origin ercot/tx123
[[ -f ../../data/ercot123_2019_v2/gen.csv ]] || { echo "ABORT: v2 data dir missing"; exit 1; }
J=$(qsub -terse smoke_v2_job.sh | cut -d. -f1)
[[ "$J" =~ ^[0-9]+$ ]] || { echo "BAD SMOKE JID: $J"; exit 1; }
C=$(qsub -terse -hold_jid "$J" -cwd -M ylu28@nd.edu -m ea collect_smoke_v2.sh)
[[ "$C" =~ ^[0-9]+$ ]] || { echo "BAD COLLECTOR JID: $C"; exit 1; }
echo "SUBMITTED smoke_v2: job=$J collector=$C (1 task, 4 slots)"
qstat -u ylu28
