#!/bin/bash
#$ -N base_2019_v2_array
#$ -q long
#$ -cwd
#$ -t 1-3
#$ -pe smp 4
#$ -r n
# Prompt 36 wave A: 3 full-year base solves on v2 costs (row 1 = reference,
# 2–3 replicates). Frozen solver config (TL=120, Threads=4).
set -euo pipefail
WAVE_DIR="$PWD"   # -cwd: submitted from inside the wave dir (submit_this.sh cd's there)
ERCOT_DIR="$(cd "$WAVE_DIR/../.." && pwd)"
TRIAL_DIR="$(cd "$ERCOT_DIR/.." && pwd)"
REPO_DIR="$(cd "$TRIAL_DIR/.." && pwd)"
DATA_DIR="$ERCOT_DIR/data/ercot123_2019_v2"
SMOKE="$ERCOT_DIR/waves/smoke_v2/SMOKE_PASS"
if [[ ! -f "$SMOKE" ]]; then
    echo "no SMOKE_PASS" > "$WAVE_DIR/FAILED_task_${SGE_TASK_ID}_no_smoke.md"
    echo "ABORT task $SGE_TASK_ID: $SMOKE absent"; exit 1
fi
mkdir -p "$WAVE_DIR/runs"
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate PCM_ERCOT
export PYTHONNOUSERSITE=1
module load gurobi

eval "$(python "$TRIAL_DIR/campaign/get_row.py" "$SGE_TASK_ID" "$WAVE_DIR/design_matrix.csv")"
OUT_PARENT="$WAVE_DIR/runs"
DICT="$WAVE_DIR/retrofit_gen_dict_${SGE_TASK_ID}.json"
python "$ERCOT_DIR/run_ercot_pcm.py" \
    --data_dir "$DATA_DIR" \
    --index "$INDEX" \
    --num_days "$NUM_DAYS" \
    --start_date "$START_DATE" \
    --ruc_time_limit 120 \
    --ruc_threads 4 \
    --output_directory "$OUT_PARENT/run" \
    --retrofit_gen_dict "$(cat "$DICT")"
