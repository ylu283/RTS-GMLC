#!/bin/bash
#$ -N tl360_probe_array
#$ -q long
#$ -cwd
#$ -t 1-3
#$ -pe smp 4
#$ -r n
# Prompt 33 T1: frozen config + EXACTLY ONE change (--ruc_time_limit 360).
# Threads=4 frozen (solver provenance). Runtime est. 18-27 h/run (the 44
# TL=120-capped days may gain up to +240 s each).
set -euo pipefail
WAVE_DIR="$PWD"
ERCOT_DIR="$(cd "$PWD/../.." && pwd)"
TRIAL_DIR="$(cd "$ERCOT_DIR/.." && pwd)"
mkdir -p "$WAVE_DIR/runs"   # prescient reporting uses os.mkdir — parent must exist
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate PCM_ERCOT
export PYTHONNOUSERSITE=1
module load gurobi

eval "$(python "$TRIAL_DIR/campaign/get_row.py" "$SGE_TASK_ID" "$WAVE_DIR/design_matrix.csv")"

python "$ERCOT_DIR/run_ercot_pcm.py" \
    --index "$INDEX" \
    --num_days "$NUM_DAYS" \
    --start_date "$START_DATE" \
    --ruc_time_limit 360 \
    --ruc_threads 4 \
    --output_directory "$WAVE_DIR/runs/run" \
    --retrofit_gen_dict '{}'
