#!/bin/bash
#$ -N collect_selection_t1
#$ -q long
#$ -cwd
#$ -r n
# Prompt 32 T1 collector: gate -> extracts (slim 1-5, --full 6-11 for the
# thermal-h2 rule) -> compute_objectives.py (objectives_t1.csv +
# noise_ruler_v2 groups) -> ercot-bot commit + 5-RETRY randomized-backoff
# push to ercot/tx123 (prompt-30 loop; push_with_one_retry is superseded).
set -euo pipefail
WAVE_DIR="$PWD"
ERCOT_DIR="$(cd "$PWD/../.." && pwd)"
REPO_DIR="$(cd "$ERCOT_DIR/../.." && pwd)"
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
for i in $(seq 1 11); do
    [[ -f "$WAVE_DIR/runs/run_index_$i/overall_simulation_output.csv" ]] || missing="$missing $i"
done
if [[ -n "$missing" ]]; then
    marker="$WAVE_DIR/FAILED_selection_t1.md"
    { echo "# FAILED — selection_t1 incomplete"; echo; echo "missing:$missing";
      echo "Generated $(date -u +%FT%TZ)"; } > "$marker"
    git -C "$REPO_DIR" add -- "$marker"
    git -C "$REPO_DIR" "${BOT[@]}" commit -m "ercot-bot: FAILED marker (selection_t1)"
    push_with_retries
    exit 1
fi
echo "GATE PASS: 11/11"

for i in $(seq 1 11); do
    JOBLOG=$(ls -t "$WAVE_DIR"/selection_t1_array.o*."$i" 2>/dev/null | head -1 || true)
    FULL=""
    [[ "$i" -ge 6 ]] && FULL="--full"   # nuclear rows: hourly thermal dispatch needed
    python "$ERCOT_DIR/extract_ercot.py" \
        "$WAVE_DIR/runs/run_index_$i" \
        "$ERCOT_DIR/extracts/selection_t1/run_index_$i" $FULL \
        ${JOBLOG:+--joblog "$JOBLOG"}
done

python "$ERCOT_DIR/compute_objectives.py"

git -C "$REPO_DIR" add -- "$ERCOT_DIR/extracts/selection_t1" \
    "$ERCOT_DIR/analysis/selection/objectives_t1.csv" \
    "$ERCOT_DIR/analysis/selection/noise_ruler_v2.json" \
    "$ERCOT_DIR/PROGRESS.md"
git -C "$REPO_DIR" "${BOT[@]}" commit -m "ercot-bot: selection_t1 extracts + objectives + ruler v2 groups"
push_with_retries
echo "collect_selection_t1 done"
