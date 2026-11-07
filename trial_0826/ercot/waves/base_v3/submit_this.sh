#!/bin/bash
# base_v3 — run ON CRC (Kay, by hand) AFTER waves/GAP_DECISION.json exists:
#   cd trial_0826/ercot/waves/base_v3 && bash submit_this.sh
# 1 task x 4 slots = 4 slots; no -tc. Collector held on the array.
cd "$(dirname "${BASH_SOURCE[0]}")"
set -euo pipefail
W="$(cd .. && pwd)"
REPO_DIR="$(cd ../../../.. && pwd)"
BRANCH="$(git -C "$REPO_DIR" branch --show-current)"
[[ "$BRANCH" == "ercot/tx123" ]] || { echo "ABORT: on '$BRANCH', expected ercot/tx123"; exit 1; }
git -C "$REPO_DIR" pull --rebase --autostash origin ercot/tx123
[[ -f "$W/GAP_DECISION.json" ]] || { echo "ABORT: waves/GAP_DECISION.json absent — decide E-D6 first (read analysis/gap_smoke/GAP_SMOKE.md)"; exit 1; }
grep -Eq '"identity"[[:space:]]*:[[:space:]]*"v3"' "$W/GAP_DECISION.json" || { echo "ABORT: waves/GAP_DECISION.json is not identity v3 — base_v3 is the v3 base"; exit 1; }
[[ -f "$W/smoke_v2/SMOKE_PASS" ]] || { echo "ABORT: waves/smoke_v2/SMOKE_PASS absent — smoke gate not passed"; exit 1; }
[[ -f "$W/../data/ercot123_2019_v2/gen.csv" ]] || { echo "ABORT: v2 data dir missing"; exit 1; }
[[ "$(tr -d '\n ' < "$W/base_v3/retrofit_gen_dict_1.json")" == "{}" ]] || { echo "ABORT: retrofit_gen_dict_1.json is not {}"; exit 1; }
grep -q -- "--ruc_mipgap" "$W/../run_ercot_pcm.py" || { echo "ABORT: run_ercot_pcm.py has no --ruc_mipgap"; exit 1; }
grep -q "base_v3/\*\*/\*.csv.gz" "$W/../.gitignore" || { echo "ABORT: trial_0826/ercot/.gitignore gz line missing"; exit 1; }
echo "--- waves/GAP_DECISION.json (the identity base_v3 will run under; eyeball it) ---"
cat "$W/GAP_DECISION.json"
echo "-----------------------------------------------------------------------------"
echo "--- qquota (need 4 slots for 1 task x 4) ---"; qquota -u ylu28 || true
read -r -p "Submit 1 full-year base run (dict {}) under this identity? [yes/NO] " ANS
[[ "$ANS" == "yes" ]] || { echo "not submitted"; exit 1; }
J=$(qsub -terse base_v3_array.sh | cut -d. -f1)
[[ "$J" =~ ^[0-9]+$ ]] || { echo "BAD ARRAY JID: $J"; exit 1; }
C=$(qsub -terse -hold_jid "$J" -cwd -M ylu28@nd.edu -m ea collect_base_v3.sh)
[[ "$C" =~ ^[0-9]+$ ]] || { echo "BAD COLLECTOR JID: $C"; exit 1; }
echo "SUBMITTED base_v3: array=$J (1 task x 4 slots) collector=$C"
qstat -u ylu28
