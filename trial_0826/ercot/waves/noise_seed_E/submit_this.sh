#!/bin/bash
# Prompt 63 v1 noise_seed_E — run ON CRC (Kay, by hand):
#   cd trial_0826/ercot/waves/noise_seed_E && bash submit_this.sh
# 16 tasks x 4 slots + 1 x 8 + 1 x 1 = 73 slots (three submissions of one array
# script, -t / -pe smp on the command line); no -tc. Collector held on all three.
# Analysis-only; no dependency on n0_E / random_E / methods_E (the Seed-0 anchors are the n0_E runs).
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
grep -q "extracts/noise_seed_E/\*\*/\*.csv.gz" "$E/.gitignore" || { echo "ABORT: trial_0826/ercot/.gitignore gz line missing"; exit 1; }
[[ -f design_matrix.csv && -f retrofit_gen_dict_18.json ]] || { echo "ABORT: noise_seed_E files missing"; exit 1; }
echo "--- waves/GAP_DECISION.json (the identity noise_seed_E will run under; eyeball it) ---"
cat "$W/GAP_DECISION.json"
echo "-----------------------------------------------------------------------------"
echo "--- qquota (need 73 slots: 16 x 4 + 8 + 1) ---"; qquota -u ylu28 || true
read -r -p "Submit 18 full-year 6-site rows (noise_seed_E) under this identity? [yes/NO] " ANS
[[ "$ANS" == "yes" ]] || { echo "not submitted"; exit 1; }
J1=$(qsub -terse -t 1-16 -pe smp 4 noise_seed_E_array.sh | cut -d. -f1)
[[ "$J1" =~ ^[0-9]+$ ]] || { echo "BAD ARRAY JID (rows 1-16): $J1"; exit 1; }
J2=$(qsub -terse -t 17-17 -pe smp 8 noise_seed_E_array.sh | cut -d. -f1)
[[ "$J2" =~ ^[0-9]+$ ]] || { echo "BAD ARRAY JID (row 17, Threads 8): $J2"; exit 1; }
J3=$(qsub -terse -t 18-18 -pe smp 1 noise_seed_E_array.sh | cut -d. -f1)
[[ "$J3" =~ ^[0-9]+$ ]] || { echo "BAD ARRAY JID (row 18, Threads 1): $J3"; exit 1; }
C=$(qsub -terse -hold_jid "$J1,$J2,$J3" -cwd -M ylu28@nd.edu -m ea collect_noise_seed_E.sh)
[[ "$C" =~ ^[0-9]+$ ]] || { echo "BAD COLLECTOR JID: $C"; exit 1; }
echo "SUBMITTED noise_seed_E: rows 1-16 = $J1 (4 slots each), row 17 = $J2 (8 slots), row 18 = $J3 (1 slot); collector=$C"
qstat -u ylu28
