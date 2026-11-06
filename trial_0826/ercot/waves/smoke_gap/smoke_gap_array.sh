#!/bin/bash
#$ -N smoke_gap_array
#$ -q long
#$ -cwd
#$ -t 1-3
#$ -pe smp 4
#$ -r n
# Prompt 58 T1 gap smoke (E-D6): smoke_v2 solve (3 days from 01-01-2019, v2
# data, base) with --ruc_mipgap / --ruc_time_limit per task. Task 1 must be
# byte-identical to extracts/smoke_v2 (gap 0.01; the 120 s TL never bound
# there, so TL 1200 changes nothing). Gurobi prints
# "Optimal solution found (tolerance <gap>)" on every RUC day: the collector
# reads that line — a log showing 1.00e-02 on task 2/3 is a FAILED smoke.
set -euo pipefail
WAVE_DIR="$PWD"   # -cwd: submitted from inside the wave dir (submit_this.sh cd's there)
ERCOT_DIR="$(cd "$WAVE_DIR/../.." && pwd)"
TRIAL_DIR="$(cd "$ERCOT_DIR/.." && pwd)"
REPO_DIR="$(cd "$TRIAL_DIR/.." && pwd)"
DATA_DIR="$ERCOT_DIR/data/ercot123_2019_v2"
case "$SGE_TASK_ID" in
    1) RUC_MIPGAP=0.01; RUC_TIME_LIMIT=1200 ;;
    2) RUC_MIPGAP=0.001; RUC_TIME_LIMIT=1200 ;;
    3) RUC_MIPGAP=0.0001; RUC_TIME_LIMIT=1200 ;;
    *) echo "ABORT: unknown task $SGE_TASK_ID"; exit 1 ;;
esac
echo "SMOKE_GAP_TASK=$SGE_TASK_ID RUC_MIPGAP=$RUC_MIPGAP RUC_TIME_LIMIT=$RUC_TIME_LIMIT"
echo "SMOKE_GAP_START $(date -u +%FT%TZ) epoch=$(date +%s)"
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate PCM_ERCOT
export PYTHONNOUSERSITE=1
module load gurobi

mkdir -p "$WAVE_DIR/runs"   # prescient reporting uses os.mkdir — parent must exist
INDEX="$SGE_TASK_ID" NUM_DAYS=3 START_DATE=01-01-2019 OUT_PARENT="$WAVE_DIR/runs"
DICT="$WAVE_DIR/retrofit_gen_dict_smoke.json"
python "$ERCOT_DIR/run_ercot_pcm.py" \
    --data_dir "$DATA_DIR" \
    --index "$INDEX" \
    --num_days "$NUM_DAYS" \
    --start_date "$START_DATE" \
    --ruc_mipgap "$RUC_MIPGAP" \
    --ruc_time_limit "$RUC_TIME_LIMIT" \
    --ruc_threads 4 \
    --output_directory "$OUT_PARENT/run" \
    --retrofit_gen_dict "$(cat "$DICT")"
echo "SMOKE_GAP_END $(date -u +%FT%TZ) epoch=$(date +%s)"
