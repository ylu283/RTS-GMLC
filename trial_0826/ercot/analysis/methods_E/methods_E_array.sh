#!/bin/bash
#$ -q long
#$ -pe smp 4
#$ -r n
# Generic methods_E array task (prompt 55). Submitted ONLY by
# analysis/methods_E/submit_ready_E.sh from the CRC login node:
#   qsub -wd <ercot>/waves -v WAVE=<wave> -t 1-8 -N <wave>_array methods_E_array.sh
# NO email flags (one email per task otherwise), no -tc. Reads the design at
# task START (hold mode: a held acquisition wrote it) and fails loudly if absent.
# Identity: --ruc_mipgap / --ruc_time_limit from waves/GAP_DECISION.json at run time.
set -euo pipefail
: "${WAVE:?WAVE env var required (qsub -v WAVE=<wave>)}"
WAVES_DIR="$PWD"   # -wd trial_0826/ercot/waves
WAVE_DIR="$WAVES_DIR/$WAVE"
ERCOT_DIR="$(cd "$WAVES_DIR/.." && pwd)"
TRIAL_DIR="$(cd "$ERCOT_DIR/.." && pwd)"
REPO_DIR="$(cd "$TRIAL_DIR/.." && pwd)"
DATA_DIR="$ERCOT_DIR/data/ercot123_2019_v2"

if [[ ! -f "$WAVE_DIR/design_matrix.csv" ]]; then
    echo "FATAL: $WAVE_DIR/design_matrix.csv absent at task start — the held acquisition" >&2
    echo "did not write this round (WEDGED/FAILED/HALT/DONE?). Not running." >&2
    exit 1
fi
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
# --- identity from waves/GAP_DECISION.json (Kay, E-D6); refuse without it ---
GAP_FILE="$ERCOT_DIR/waves/GAP_DECISION.json"
if [[ ! -f "$GAP_FILE" ]]; then
    echo "no GAP_DECISION.json" > "$WAVE_DIR/FAILED_task_${SGE_TASK_ID}_no_gap_decision.md"
    echo "ABORT task $SGE_TASK_ID: $GAP_FILE absent — methods_E runs only under a decided identity"; exit 1
fi
read -r RUC_MIPGAP RUC_TIME_LIMIT < <(python - "$GAP_FILE" <<'PY'
import json, sys
d = json.load(open(sys.argv[1]))
g, t = float(d["ruc_mipgap"]), float(d["ruc_time_limit"])
assert 0.0 <= g < 1.0 and t > 0, (g, t)
print(g, t)
PY
)
[[ -n "$RUC_MIPGAP" && -n "$RUC_TIME_LIMIT" ]] || { echo "ABORT: GAP_DECISION.json unreadable"; exit 1; }
echo "IDENTITY from GAP_DECISION.json: ruc_mipgap=$RUC_MIPGAP ruc_time_limit=$RUC_TIME_LIMIT ($(tr -d '\n' < "$GAP_FILE"))"

eval "$(python "$TRIAL_DIR/campaign/get_row.py" "$SGE_TASK_ID" "$WAVE_DIR/design_matrix.csv")"
OUT_PARENT="$WAVE_DIR/runs"
DICT="$WAVE_DIR/retrofit_gen_dict_${SGE_TASK_ID}.json"
echo "METHODS_E_TASK=$WAVE:$SGE_TASK_ID dict=$(tr -d '\n ' < "$DICT")"
echo "METHODS_E_START $(date -u +%FT%TZ) epoch=$(date +%s)"
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
echo "METHODS_E_END $(date -u +%FT%TZ) epoch=$(date +%s)"
