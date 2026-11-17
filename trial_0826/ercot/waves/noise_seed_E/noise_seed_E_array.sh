#!/bin/bash
#$ -N noise_seed_E_array
#$ -q long
#$ -cwd
#$ -t 1-16
#$ -pe smp 4
#$ -r n
# Prompt 63 v1 noise_seed_E: 18 full-year 6-site rows, analysis-only Gurobi-Seed / thread replicates at 4 n0_E designs (prompt 63; new Y at existing n0_E X; never in the GP training set, the HV ledger or the baseline).
# Rows 17-18 (Threads 8 / 1) are submitted by submit_this.sh with -t 17-17 -pe smp 8 and
# -t 18-18 -pe smp 1 (command-line options override the #$ lines above); every task
# refuses to run unless NSLOTS equals its row's ruc_threads.
# Design space waves/design_space_E.json. Runs ONLY under the identity in
# waves/GAP_DECISION.json (Kay, E-D6), read at run time below.
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
# --- identity from waves/GAP_DECISION.json (Kay, E-D6); refuse without it ---
GAP_FILE="$ERCOT_DIR/waves/GAP_DECISION.json"
if [[ ! -f "$GAP_FILE" ]]; then
    echo "no GAP_DECISION.json" > "$WAVE_DIR/FAILED_task_${SGE_TASK_ID}_no_gap_decision.md"
    echo "ABORT task $SGE_TASK_ID: $GAP_FILE absent — noise_seed_E runs only under a decided identity"; exit 1
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
# --- prompt 63: Gurobi Seed + Threads from this row; the slot count must match ---
read -r SEED RUC_THREADS < <(python - "$SGE_TASK_ID" "$WAVE_DIR/design_matrix.csv" <<'PY'
import csv, sys
t = int(sys.argv[1])
rows = [r for r in csv.DictReader(open(sys.argv[2])) if int(float(r["index"])) == t]
assert len(rows) == 1, (t, len(rows))
s, th = int(rows[0]["seed"]), int(rows[0]["ruc_threads"])
assert 0 <= s <= 2000000000 and th in (1, 4, 8), (s, th)
print(s, th)
PY
)
[[ -n "$SEED" && -n "$RUC_THREADS" ]] || { echo "ABORT: seed / ruc_threads unreadable"; exit 1; }
if [[ "${NSLOTS:-}" != "$RUC_THREADS" ]]; then
    echo "slots ${NSLOTS:-unset} != ruc_threads $RUC_THREADS" > "$WAVE_DIR/FAILED_task_${SGE_TASK_ID}_slots.md"
    echo "ABORT task $SGE_TASK_ID: NSLOTS=${NSLOTS:-unset} but the row asks ruc_threads=$RUC_THREADS (submit_this.sh sets -pe smp per row group)"; exit 1
fi
SEED_OPT=()
if [[ "$SEED" != "0" ]]; then SEED_OPT=(--ruc_solver_option "Seed=$SEED"); fi
# --- determinism conditions (prompt 63 A4; memo F8), logged before the run ---
echo "NOISE_SEED_E_HOST $(hostname)"
echo "NOISE_SEED_E_CPU $(lscpu 2>/dev/null | grep 'Model name' | sed 's/  */ /g' || true)"
GRB_VERSION=$(python -c 'import gurobipy; print(gurobipy.gurobi.version())' 2>&1 || true)
echo "NOISE_SEED_E_GUROBI $GRB_VERSION"
echo "NOISE_SEED_E_THREADS ruc_threads=$RUC_THREADS nslots=${NSLOTS:-unset} seed=$SEED"
CODE_SHAS=$(python - 2>&1 <<'PY' || true
import os, subprocess
out = []
for m in ("prescient", "egret"):
    try:
        mod = __import__(m)
        d = os.path.dirname(os.path.realpath(mod.__file__))
        sha = subprocess.run(["git", "-C", d, "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()
        out.append(f"{m}={sha or 'unknown'}")
    except Exception as e:  # noqa: BLE001
        out.append(f"{m}=unknown({type(e).__name__})")
print(" ".join(out))
PY
)
echo "NOISE_SEED_E_CODE $CODE_SHAS repo=$(git -C "$REPO_DIR" rev-parse --short HEAD 2>/dev/null || echo unknown)"
OUT_PARENT="$WAVE_DIR/runs"
DICT="$WAVE_DIR/retrofit_gen_dict_${SGE_TASK_ID}.json"
echo "NOISE_SEED_E_TASK=$SGE_TASK_ID seed=$SEED ruc_threads=$RUC_THREADS dict=$(tr -d '\n ' < "$DICT")"
echo "NOISE_SEED_E_START $(date -u +%FT%TZ) epoch=$(date +%s)"
python "$ERCOT_DIR/run_ercot_pcm.py" \
    --data_dir "$DATA_DIR" \
    --index "$INDEX" \
    --num_days "$NUM_DAYS" \
    --start_date "$START_DATE" \
    --ruc_mipgap "$RUC_MIPGAP" \
    --ruc_time_limit "$RUC_TIME_LIMIT" \
    --ruc_threads "$RUC_THREADS" \
    ${SEED_OPT[@]+"${SEED_OPT[@]}"} \
    --output_directory "$OUT_PARENT/run" \
    --retrofit_gen_dict "$(cat "$DICT")"
echo "NOISE_SEED_E_END $(date -u +%FT%TZ) epoch=$(date +%s)"
