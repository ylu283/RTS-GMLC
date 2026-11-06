#!/bin/bash
# Prompt 58 T2 wave D — run ON CRC (Kay, by hand) AFTER waves/GAP_DECISION.json
# exists:   cd trial_0826/ercot/waves/location_oat_v2 && bash submit_this.sh
# 21 tasks x 4 slots = 84 slots; no -tc. Collector held on the array.
cd "$(dirname "${BASH_SOURCE[0]}")"
set -euo pipefail
W="$(cd .. && pwd)"
REPO_DIR="$(cd ../../../.. && pwd)"
BRANCH="$(git -C "$REPO_DIR" branch --show-current)"
[[ "$BRANCH" == "ercot/tx123" ]] || { echo "ABORT: on '$BRANCH', expected ercot/tx123"; exit 1; }
git -C "$REPO_DIR" pull --rebase --autostash origin ercot/tx123
[[ -f "$W/GAP_DECISION.json" ]] || { echo "ABORT: waves/GAP_DECISION.json absent — decide E-D6 first (read analysis/gap_smoke/GAP_SMOKE.md)"; exit 1; }
[[ -f "$W/smoke_v2/SMOKE_PASS" ]] || { echo "ABORT: waves/smoke_v2/SMOKE_PASS absent — smoke gate not passed"; exit 1; }
[[ -f "$W/../data/ercot123_2019_v2/gen.csv" ]] || { echo "ABORT: v2 data dir missing"; exit 1; }
git -C "$REPO_DIR" merge-base --is-ancestor 7c5fb8d HEAD || { echo "ABORT: fix 7c5fb8d not in HEAD (nuclear rows)"; exit 1; }
grep -q -- "--ruc_mipgap" "$W/../run_ercot_pcm.py" || { echo "ABORT: run_ercot_pcm.py has no --ruc_mipgap"; exit 1; }
grep -q "location_oat_v2/\*\*/\*.csv.gz" "$W/../.gitignore" || { echo "ABORT: trial_0826/ercot/.gitignore gz line missing"; exit 1; }
echo "--- waves/GAP_DECISION.json (the identity wave D will run under; eyeball it) ---"
cat "$W/GAP_DECISION.json"
echo "-----------------------------------------------------------------------------"
echo "--- qquota (need 84 slots for 21 tasks x 4) ---"; qquota -u ylu28 || true
read -r -p "Submit 21 full-year rows under this identity? [yes/NO] " ANS
[[ "$ANS" == "yes" ]] || { echo "not submitted"; exit 1; }
J=$(qsub -terse location_oat_v2_array.sh | cut -d. -f1)
[[ "$J" =~ ^[0-9]+$ ]] || { echo "BAD ARRAY JID: $J"; exit 1; }
C=$(qsub -terse -hold_jid "$J" -cwd -M ylu28@nd.edu -m ea collect_location_oat_v2.sh)
[[ "$C" =~ ^[0-9]+$ ]] || { echo "BAD COLLECTOR JID: $C"; exit 1; }
echo "SUBMITTED location_oat_v2: array=$J (21 tasks x 4 slots) collector=$C"
qstat -u ylu28
