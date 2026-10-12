#!/bin/bash
#$ -N screening_v2_array
#$ -q long
#$ -cwd
#$ -t 1-19
#$ -pe smp 4
#$ -r n
# Prompt 36 wave B: v1 screening slates (12 + 7, byte-identical) on v2 costs.
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
if [[ "$SGE_TASK_ID" -le 12 ]]; then SUB=ercot; ROW=$SGE_TASK_ID
else SUB=topup; ROW=$((SGE_TASK_ID - 12)); fi
mkdir -p "$WAVE_DIR/runs/$SUB"
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate PCM_ERCOT
export PYTHONNOUSERSITE=1
module load gurobi

eval "$(python "$TRIAL_DIR/campaign/get_row.py" "$ROW" "$WAVE_DIR/$SUB/design_matrix.csv")"
OUT_PARENT="$WAVE_DIR/runs/$SUB"
DICT="$WAVE_DIR/$SUB/retrofit_gen_dict_${ROW}.json"
echo "task $SGE_TASK_ID -> $SUB row $ROW"
python "$ERCOT_DIR/run_ercot_pcm.py" \
    --data_dir "$DATA_DIR" \
    --index "$INDEX" \
    --num_days "$NUM_DAYS" \
    --start_date "$START_DATE" \
    --ruc_time_limit 120 \
    --ruc_threads 4 \
    --output_directory "$OUT_PARENT/run" \
    --retrofit_gen_dict "$(cat "$DICT")"
