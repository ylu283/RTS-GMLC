#!/bin/bash
# Prompt 36 wave C rerun — ALL nuclear rows 6–11 after the T0 fix in
# multi_pem/parameters.py (initial_p_output lifted to the raised p_min).
# Run ON CRC (Kay, by hand, from bastion):  bash rerun_nuc_this.sh
# 6 tasks × 4 slots = 24 slots; no -tc. Rows 3–5 keep their first runs.
cd "$(dirname "${BASH_SOURCE[0]}")"
set -euo pipefail
WAVE_DIR="$PWD"
REPO_DIR="$(cd ../../../.. && pwd)"
TRIAL_DIR="$REPO_DIR/trial_0826"
BRANCH="$(git -C "$REPO_DIR" branch --show-current)"
[[ "$BRANCH" == "ercot/tx123" ]] || { echo "ABORT: on '$BRANCH', expected ercot/tx123"; exit 1; }
git -C "$REPO_DIR" pull --rebase --autostash origin ercot/tx123
grep -q 'gen\["initial_p_output"\] = gen\["p_min"\]' "$TRIAL_DIR/multi_pem/parameters.py" \
    || { echo "ABORT: T0 fix not in multi_pem/parameters.py"; exit 1; }
for i in 3 4 5; do
    [[ -f "runs/run_index_$i/overall_simulation_output.csv" ]] || { echo "ABORT: kept row $i has no finished run"; exit 1; }
done

# preflight: build-only regression on the real fork egret (no solve)
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate PCM_ERCOT
PYTHONNOUSERSITE=1 OMP_NUM_THREADS=4 python -m pytest -q -p no:cacheprovider \
    "$TRIAL_DIR/multi_pem/tests/test_t0_build.py" || { echo "ABORT: T0 build test failed"; exit 1; }

# quarantine the first-run dirs (T0 = 729 MW); never delete
Q="runs/quarantine_T0_729"
mkdir -p "$Q"
for i in 6 7 8 9 10 11; do
    if [[ -e "runs/run_index_$i" ]]; then
        [[ -e "$Q/run_index_$i" ]] && { echo "ABORT: $Q/run_index_$i already exists"; exit 1; }
        mv "runs/run_index_$i" "$Q/run_index_$i"
        echo "quarantined runs/run_index_$i -> $Q/run_index_$i"
    fi
done

echo "--- qquota (need 24 slots for 6 tasks x 4) ---"; qquota -u ylu28 || true
JC=$(qsub -terse -t 6-11 selection_t1_v2_array.sh | cut -d. -f1)
[[ "$JC" =~ ^[0-9]+$ ]] || { echo "BAD JID for array: $JC"; exit 1; }
CC=$(qsub -terse -hold_jid "$JC" -cwd -M ylu28@nd.edu -m ea collect_selection_t1_v2.sh | cut -d. -f1)
[[ "$CC" =~ ^[0-9]+$ ]] || { echo "BAD JID for collector: $CC"; exit 1; }
echo "SUBMITTED selection_t1_v2 nuclear rerun: array=$JC (-t 6-11) collector=$CC (holds on $JC)"
qstat -u ylu28
