#!/bin/bash
#$ -N collect_selection_t1_v2
#$ -q long
#$ -cwd
#$ -r n
# Prompt 36 collector (selection_t1_v2): gate -> extracts (--data_dir v2) -> objectives -> ercot-bot
# commit + 5-retry push. Clears a stale FAILED marker on success. Email flags
# are applied by submit_this.sh on THIS job only.
set -euo pipefail
WAVE_DIR="$PWD"   # -cwd: submitted from inside the wave dir (submit_this.sh cd's there)
ERCOT_DIR="$(cd "$WAVE_DIR/../.." && pwd)"
TRIAL_DIR="$(cd "$ERCOT_DIR/.." && pwd)"
REPO_DIR="$(cd "$TRIAL_DIR/.." && pwd)"
DATA_DIR="$ERCOT_DIR/data/ercot123_2019_v2"
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate PCM_ERCOT
export PYTHONNOUSERSITE=1

BOT=(-c user.name="ercot-bot" -c user.email="ercot-bot@noreply.github.com")
push_with_retries() {
    local attempt
    for attempt in 1 2 3 4 5; do
        if git -C "$REPO_DIR" push origin ercot/tx123; then return 0; fi
        echo "push rejected (attempt $attempt/5) — rebase and retry"
        sleep $((30 + RANDOM % 60))
        git -C "$REPO_DIR" pull --rebase --autostash origin ercot/tx123
    done
    git -C "$REPO_DIR" push origin ercot/tx123 || { git -C "$REPO_DIR" status; exit 1; }
}

missing=""
for i in $(seq 3 11); do
    [[ -f "$WAVE_DIR/runs/run_index_$i/overall_simulation_output.csv" ]] || missing="$missing $i"
done
if [[ -n "$missing" ]]; then
    marker="$WAVE_DIR/FAILED_selection_t1_v2.md"
    { echo "# FAILED — selection_t1_v2 incomplete"; echo; echo "missing:$missing";
      echo "Generated $(date -u +%FT%TZ)"; } > "$marker"
    git -C "$REPO_DIR" add -- "$marker"
    git -C "$REPO_DIR" "${BOT[@]}" commit -m "ercot-bot: FAILED marker (selection_t1_v2)"
    push_with_retries
    exit 1
fi
echo "GATE PASS: 9/9"
if [[ -f "$WAVE_DIR/FAILED_selection_t1_v2.md" ]]; then
    git -C "$REPO_DIR" rm -q -- "$WAVE_DIR/FAILED_selection_t1_v2.md" 2>/dev/null \
        || rm -f "$WAVE_DIR/FAILED_selection_t1_v2.md"
    echo "stale FAILED marker cleared"
fi

for i in $(seq 3 11); do
    JOBLOG=$(ls -t "$WAVE_DIR"/selection_t1_v2_array.o*."$i" 2>/dev/null | head -1 || true)
    python "$ERCOT_DIR/extract_ercot.py" --data_dir "$DATA_DIR" \
        "$WAVE_DIR/runs/run_index_$i" \
        "$ERCOT_DIR/extracts/selection_t1_v2/run_index_$i"  \
        ${JOBLOG:+--joblog "$JOBLOG"}
done
# objectives need A + B extracts: submit_this.sh holds this collector on
# collect_base_2019_v2 and collect_screening_v2 as well as this array.
python "$ERCOT_DIR/compute_objectives.py" --suffix _v2

git -C "$REPO_DIR" add -- "$ERCOT_DIR/extracts/selection_t1_v2" \
    "$ERCOT_DIR/analysis/selection/objectives_t1_v2.csv" \
    "$ERCOT_DIR/analysis/selection/noise_ruler_v2_v2.json"
git -C "$REPO_DIR" "${BOT[@]}" commit -m "ercot-bot: selection_t1_v2 extracts (v2 costs)"
push_with_retries
echo "collect_selection_t1_v2 done"
