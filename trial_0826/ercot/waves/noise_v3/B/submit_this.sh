#!/bin/bash
# Prompt 52 v2.1 noise_v3 batch B — run ON CRC (Kay, by hand):
#   cd trial_0826/ercot/waves/noise_v3/B && bash submit_this.sh
# 8 tasks x 4 slots = 32 slots; no -tc. Collector held on the array.
# Batch B refuses until batch A's collector has pushed extracts/noise_v3/A/COLLECTED.
cd "$(dirname "${BASH_SOURCE[0]}")"
set -euo pipefail
E="$(cd ../../.. && pwd)"
W="$E/waves"
REPO_DIR="$(cd ../../../../.. && pwd)"
BRANCH="$(git -C "$REPO_DIR" branch --show-current)"
[[ "$BRANCH" == "ercot/tx123" ]] || { echo "ABORT: on '$BRANCH', expected ercot/tx123"; exit 1; }
git -C "$REPO_DIR" pull --rebase --autostash origin ercot/tx123
[[ -f "$W/GAP_DECISION.json" ]] || { echo "ABORT: waves/GAP_DECISION.json absent — decide E-D6 first (read analysis/gap_smoke/GAP_SMOKE.md)"; exit 1; }
[[ -f "$W/smoke_v2/SMOKE_PASS" ]] || { echo "ABORT: waves/smoke_v2/SMOKE_PASS absent — smoke gate not passed"; exit 1; }
[[ -f "$E/data/ercot123_2019_v2/gen.csv" ]] || { echo "ABORT: v2 data dir missing"; exit 1; }
git -C "$REPO_DIR" merge-base --is-ancestor 7c5fb8d HEAD || { echo "ABORT: fix 7c5fb8d not in HEAD (nuclear rows)"; exit 1; }
grep -q -- "--ruc_mipgap" "$E/run_ercot_pcm.py" || { echo "ABORT: run_ercot_pcm.py has no --ruc_mipgap"; exit 1; }
grep -q "noise_v3/\*\*/\*.csv.gz" "$E/.gitignore" || { echo "ABORT: trial_0826/ercot/.gitignore gz line missing"; exit 1; }
[[ -f design_matrix.csv && -f retrofit_gen_dict_8.json ]] || { echo "ABORT: batch B files missing"; exit 1; }
[[ -f "$E/extracts/noise_v3/A/COLLECTED" ]] || { echo "ABORT: extracts/noise_v3/A/COLLECTED absent — batch A's collector has not pushed yet (submit A first, wait for its email)"; exit 1; }
echo "--- batch A COLLECTED marker ---"; cat "$E/extracts/noise_v3/A/COLLECTED"
echo "--- waves/GAP_DECISION.json (the identity batch B will run under; eyeball it) ---"
cat "$W/GAP_DECISION.json"
echo "-----------------------------------------------------------------------------"
echo "--- qquota (need 32 slots for 8 tasks x 4) ---"; qquota -u ylu28 || true
read -r -p "Submit 8 full-year rows (noise_v3 batch B) under this identity? [yes/NO] " ANS
[[ "$ANS" == "yes" ]] || { echo "not submitted"; exit 1; }
J=$(qsub -terse noise_v3_B_array.sh | cut -d. -f1)
[[ "$J" =~ ^[0-9]+$ ]] || { echo "BAD ARRAY JID: $J"; exit 1; }
C=$(qsub -terse -hold_jid "$J" -cwd -M ylu28@nd.edu -m ea collect_noise_v3_B.sh)
[[ "$C" =~ ^[0-9]+$ ]] || { echo "BAD COLLECTOR JID: $C"; exit 1; }
echo "SUBMITTED noise_v3_B: array=$J (8 tasks x 4 slots) collector=$C"
qstat -u ylu28
