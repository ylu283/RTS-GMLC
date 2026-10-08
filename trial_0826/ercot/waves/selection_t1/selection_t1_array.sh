#!/bin/bash
#$ -N selection_t1_array
#$ -q long
#$ -cwd
#$ -t 1-11
#$ -pe smp 4
#$ -r n
# Prompt 32 T1 array. -pe smp 4 + --ruc_threads 4 is FROZEN solver
# provenance (shapes the TL=120 incumbent and the rulers) — never retune.
# Explicit smoke gating: exits with a FAILED marker if SMOKE_PASS absent.
set -euo pipefail
WAVE_DIR="$PWD"
ERCOT_DIR="$(cd "$PWD/../.." && pwd)"
TRIAL_DIR="$(cd "$ERCOT_DIR/.." && pwd)"
if [[ ! -f "$WAVE_DIR/SMOKE_PASS" ]]; then
    echo "no SMOKE_PASS" > "$WAVE_DIR/FAILED_task_${SGE_TASK_ID}_no_smoke.md"
    echo "ABORT task $SGE_TASK_ID: SMOKE_PASS absent"; exit 1
fi
mkdir -p "$WAVE_DIR/runs"
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate PCM_ERCOT
export PYTHONNOUSERSITE=1
module load gurobi

eval "$(python "$TRIAL_DIR/campaign/get_row.py" "$SGE_TASK_ID" "$WAVE_DIR/design_matrix.csv")"

python "$ERCOT_DIR/run_ercot_pcm.py" \
    --index "$INDEX" \
    --num_days "$NUM_DAYS" \
    --start_date "$START_DATE" \
    --ruc_time_limit 120 \
    --ruc_threads 4 \
    --output_directory "$WAVE_DIR/runs/run" \
    --retrofit_gen_dict "$(cat "$WAVE_DIR/retrofit_gen_dict_${SGE_TASK_ID}.json")"
