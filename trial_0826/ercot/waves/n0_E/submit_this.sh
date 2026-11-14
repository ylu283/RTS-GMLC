#!/bin/bash
# Prompt 53 v3.1 n0_E — run ON CRC (Kay, by hand):
#   cd trial_0826/ercot/waves/n0_E && bash submit_this.sh
# 48 tasks x 4 slots = 192 slots; no -tc. Collector held on the array.
# No dependency on the other E wave (n0_E / random_E): either order, or both.
cd "$(dirname "${BASH_SOURCE[0]}")"
set -euo pipefail
E="$(cd ../.. && pwd)"
W="$E/waves"
REPO_DIR="$(cd ../../../.. && pwd)"
BRANCH="$(git -C "$REPO_DIR" branch --show-current)"
[[ "$BRANCH" == "ercot/tx123" ]] || { echo "ABORT: on '$BRANCH', expected ercot/tx123"; exit 1; }
git -C "$REPO_DIR" pull --rebase --autostash origin ercot/tx123
[[ -f "$W/GAP_DECISION.json" ]] || { echo "ABORT: waves/GAP_DECISION.json absent — decide E-D6 first (read analysis/gap_smoke/GAP_SMOKE.md)"; exit 1; }
[[ -f "$W/smoke_v2/SMOKE_PASS" ]] || { echo "ABORT: waves/smoke_v2/SMOKE_PASS absent — smoke gate not passed"; exit 1; }
[[ -f "$W/design_space_E.json" ]] || { echo "ABORT: waves/design_space_E.json absent — the design-space freeze is not in HEAD"; exit 1; }
[[ -f "$E/data/ercot123_2019_v2/gen.csv" ]] || { echo "ABORT: v2 data dir missing"; exit 1; }
grep -q -- "--ruc_mipgap" "$E/run_ercot_pcm.py" || { echo "ABORT: run_ercot_pcm.py has no --ruc_mipgap"; exit 1; }
grep -q "extracts/n0_E/\*\*/\*.csv.gz" "$E/.gitignore" || { echo "ABORT: trial_0826/ercot/.gitignore gz line missing"; exit 1; }
[[ -f design_matrix.csv && -f retrofit_gen_dict_48.json ]] || { echo "ABORT: n0_E files missing"; exit 1; }
echo "--- waves/GAP_DECISION.json (the identity n0_E will run under; eyeball it) ---"
cat "$W/GAP_DECISION.json"
echo "-----------------------------------------------------------------------------"
echo "--- qquota (need 192 slots for 48 tasks x 4) ---"; qquota -u ylu28 || true
read -r -p "Submit 48 full-year 6-site rows (n0_E) under this identity? [yes/NO] " ANS
[[ "$ANS" == "yes" ]] || { echo "not submitted"; exit 1; }
J=$(qsub -terse n0_E_array.sh | cut -d. -f1)
[[ "$J" =~ ^[0-9]+$ ]] || { echo "BAD ARRAY JID: $J"; exit 1; }
C=$(qsub -terse -hold_jid "$J" -cwd -M ylu28@nd.edu -m ea collect_n0_E.sh)
[[ "$C" =~ ^[0-9]+$ ]] || { echo "BAD COLLECTOR JID: $C"; exit 1; }
echo "SUBMITTED n0_E: array=$J (48 tasks x 4 slots) collector=$C"
qstat -u ylu28
