#!/bin/bash
#$ -N screening_ercot_array
#$ -q long
#$ -cwd
#$ -t 1-12
#$ -pe smp 4

# ERCOT screening array (prompt 26 T4). Submit from INSIDE the wave dir of
# the CRC ERCOT WORKTREE ($GROUP/ylu28/RTS-GMLC-ercot):
#   cd <worktree>/trial_0826/ercot/waves/screening_ercot && qsub screening_ercot_array.sh
# No -tc cap (Kay 09-19: Gurobi licenses are not a constraint).
# -pe smp 4 + --ruc_threads 4: RUC threads explicitly = slot count
# (solver-provenance row; under TimeLimit=120 threads shape the incumbent).
# If this cluster rejects '-pe smp', drop that line AND change
# --ruc_threads to 1 — the two must stay equal.
# Env: PCM_ERCOT (editable h2patch-2.2.3), NEVER PCM0826.

set -euo pipefail

GUROBI_MODULE="gurobi"

WAVE_DIR="$PWD"
ERCOT_DIR="$(cd "$PWD/../.." && pwd)"
TRIAL_DIR="$(cd "$ERCOT_DIR/.." && pwd)"
mkdir -p "$WAVE_DIR/runs"

source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate PCM_ERCOT
module load "$GUROBI_MODULE"

eval "$(python "$TRIAL_DIR/campaign/get_row.py" "$SGE_TASK_ID" "$WAVE_DIR/design_matrix.csv")"

python "$ERCOT_DIR/run_ercot_pcm.py" \
    --index "$INDEX" \
    --num_days "$NUM_DAYS" \
    --start_date "$START_DATE" \
    --ruc_time_limit 120 \
    --ruc_threads 4 \
    --output_directory "$WAVE_DIR/runs/run" \
    --retrofit_gen_dict "$(cat "$WAVE_DIR/retrofit_gen_dict_${INDEX}.json")"
