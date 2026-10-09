#!/bin/bash
#$ -N collect_tl360_probe
#$ -q long
#$ -cwd
#$ -r n
# Prompt 33 collector: gate -> extracts (slim; --full on run 1 only, the
# hourly reference) -> compute_tl360.py -> ercot-bot 5-retry push.
# Clears a stale FAILED marker on success (09-20 lesson). Email flags are
# applied by submit_this.sh on THIS job only.
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
for i in 1 2 3; do
    [[ -f "$WAVE_DIR/runs/run_index_$i/overall_simulation_output.csv" ]] || missing="$missing $i"
done
if [[ -n "$missing" ]]; then
    marker="$WAVE_DIR/FAILED_tl360_probe.md"
    { echo "# FAILED — tl360_probe incomplete"; echo; echo "missing:$missing";
      echo "Generated $(date -u +%FT%TZ)"; } > "$marker"
    git -C "$REPO_DIR" add -- "$marker"
    git -C "$REPO_DIR" "${BOT[@]}" commit -m "ercot-bot: FAILED marker (tl360_probe)"
    push_with_retries
    exit 1
fi
echo "GATE PASS: 3/3"
if [[ -f "$WAVE_DIR/FAILED_tl360_probe.md" ]]; then
    git -C "$REPO_DIR" rm -q -- "$WAVE_DIR/FAILED_tl360_probe.md" 2>/dev/null \
        || rm -f "$WAVE_DIR/FAILED_tl360_probe.md"
    echo "stale FAILED marker cleared"
fi

for i in 1 2 3; do
    JOBLOG=$(ls -t "$WAVE_DIR"/tl360_probe_array.o*."$i" 2>/dev/null | head -1 || true)
    FULL=""
    [[ "$i" == 1 ]] && FULL="--full"
    python "$ERCOT_DIR/extract_ercot.py" \
        "$WAVE_DIR/runs/run_index_$i" \
        "$ERCOT_DIR/extracts/tl360_probe/run_index_$i" $FULL \
        ${JOBLOG:+--joblog "$JOBLOG"}
done

python "$ERCOT_DIR/compute_tl360.py"

git -C "$REPO_DIR" add -- "$ERCOT_DIR/extracts/tl360_probe" \
    "$ERCOT_DIR/analysis/tl360_probe"
git -C "$REPO_DIR" "${BOT[@]}" commit -m "ercot-bot: tl360_probe extracts + readings (quarantined solver identity)"
push_with_retries
echo "collect_tl360_probe done"
