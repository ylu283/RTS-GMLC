#!/bin/bash
# Prompt 58 T1 gap smoke — run ON CRC (Kay, by hand):
#   cd trial_0826/ercot/waves/smoke_gap && bash submit_this.sh
# 3 tasks x 4 slots; minutes of compute. Collector held on the array.
cd "$(dirname "${BASH_SOURCE[0]}")"
set -euo pipefail
REPO_DIR="$(cd ../../../.. && pwd)"
BRANCH="$(git -C "$REPO_DIR" branch --show-current)"
[[ "$BRANCH" == "ercot/tx123" ]] || { echo "ABORT: on '$BRANCH', expected ercot/tx123"; exit 1; }
git -C "$REPO_DIR" pull --rebase --autostash origin ercot/tx123
[[ -f ../../data/ercot123_2019_v2/gen.csv ]] || { echo "ABORT: v2 data dir missing"; exit 1; }
[[ -f ../../extracts/smoke_v2/overall.csv ]] || { echo "ABORT: extracts/smoke_v2 (byte-identity reference) missing"; exit 1; }
grep -q -- "--ruc_mipgap" ../../run_ercot_pcm.py || { echo "ABORT: run_ercot_pcm.py has no --ruc_mipgap (pull the prompt-58 commits)"; exit 1; }
J=$(qsub -terse smoke_gap_array.sh | cut -d. -f1)
[[ "$J" =~ ^[0-9]+$ ]] || { echo "BAD ARRAY JID: $J"; exit 1; }
C=$(qsub -terse -hold_jid "$J" -cwd -M ylu28@nd.edu -m ea collect_smoke_gap.sh)
[[ "$C" =~ ^[0-9]+$ ]] || { echo "BAD COLLECTOR JID: $C"; exit 1; }
echo "SUBMITTED smoke_gap: array=$J (3 tasks x 4 slots) collector=$C"
qstat -u ylu28
