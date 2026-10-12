#!/bin/bash
#$ -N smoke_v2
#$ -q long
#$ -cwd
#$ -pe smp 4
#$ -r n
# Prompt 36 smoke on v2 costs: 3 days from 01-01-2019 (same window as the v1
# smoke_3d), base (no PEM), frozen solver config. SMOKE_PASS is NOT written
# here: the gate also needs the authors'-SCUC side-by-side, which runs locally
# (analysis/cost_fix/smoke_gate.py writes waves/smoke_v2/SMOKE_PASS).
set -euo pipefail
WAVE_DIR="$PWD"   # -cwd: submitted from inside the wave dir (submit_this.sh cd's there)
ERCOT_DIR="$(cd "$WAVE_DIR/../.." && pwd)"
TRIAL_DIR="$(cd "$ERCOT_DIR/.." && pwd)"
REPO_DIR="$(cd "$TRIAL_DIR/.." && pwd)"
DATA_DIR="$ERCOT_DIR/data/ercot123_2019_v2"
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate PCM_ERCOT
export PYTHONNOUSERSITE=1
module load gurobi

mkdir -p "$WAVE_DIR/runs"   # prescient reporting uses os.mkdir — parent must exist
INDEX=smoke NUM_DAYS=3 START_DATE=01-01-2019 OUT_PARENT="$WAVE_DIR/runs"
DICT="$WAVE_DIR/retrofit_gen_dict_smoke.json"
python "$ERCOT_DIR/run_ercot_pcm.py" \
    --data_dir "$DATA_DIR" \
    --index "$INDEX" \
    --num_days "$NUM_DAYS" \
    --start_date "$START_DATE" \
    --ruc_time_limit 120 \
    --ruc_threads 4 \
    --output_directory "$OUT_PARENT/run" \
    --retrofit_gen_dict "$(cat "$DICT")"
