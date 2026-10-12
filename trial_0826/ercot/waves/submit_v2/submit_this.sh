#!/bin/bash
# Prompt 36 T2 — ONE submission of waves A + B + C on v2 costs.
# Run ON CRC (Kay, by hand) after SMOKE_PASS is committed:  bash submit_this.sh
# 31 tasks × 4 slots = 124 slots; no -tc.
cd "$(dirname "${BASH_SOURCE[0]}")"
set -euo pipefail
W="$(cd .. && pwd)"
REPO_DIR="$(cd ../../../.. && pwd)"
BRANCH="$(git -C "$REPO_DIR" branch --show-current)"
[[ "$BRANCH" == "ercot/tx123" ]] || { echo "ABORT: on '$BRANCH', expected ercot/tx123"; exit 1; }
git -C "$REPO_DIR" pull --rebase --autostash origin ercot/tx123
[[ -f "$W/smoke_v2/SMOKE_PASS" ]] || { echo "ABORT: waves/smoke_v2/SMOKE_PASS absent — smoke gate not passed"; exit 1; }
[[ -f "$W/../data/ercot123_2019_v2/gen.csv" ]] || { echo "ABORT: v2 data dir missing"; exit 1; }
git -C "$REPO_DIR" merge-base --is-ancestor 1eaf05e HEAD || { echo "ABORT: fix 1eaf05e not in HEAD (wave C)"; exit 1; }
echo "--- qquota (need 124 slots for 31 tasks x 4) ---"; qquota -u ylu28 || true

sub() { local d=$1; shift; (cd "$W/$d" && qsub -terse "$@" | cut -d. -f1); }
chk() { [[ "$2" =~ ^[0-9]+$ ]] || { echo "BAD JID for $1: $2"; exit 1; }; }

JA=$(sub base_2019_v2 base_2019_v2_array.sh);              chk A_array "$JA"
JB=$(sub screening_v2 screening_v2_array.sh);              chk B_array "$JB"
JC=$(sub selection_t1_v2 selection_t1_v2_array.sh);        chk C_array "$JC"
CA=$(sub base_2019_v2 -hold_jid "$JA" -cwd -M ylu28@nd.edu -m ea collect_base_2019_v2.sh);   chk A_coll "$CA"
CB=$(sub screening_v2 -hold_jid "$JB" -cwd -M ylu28@nd.edu -m ea collect_screening_v2.sh);   chk B_coll "$CB"
CC=$(sub selection_t1_v2 -hold_jid "$JC,$CA,$CB" -cwd -M ylu28@nd.edu -m ea collect_selection_t1_v2.sh); chk C_coll "$CC"
echo "SUBMITTED v2 A+B+C: A array=$JA (3) B array=$JB (19) C array=$JC (9) | collectors A=$CA B=$CB C=$CC"
qstat -u ylu28
