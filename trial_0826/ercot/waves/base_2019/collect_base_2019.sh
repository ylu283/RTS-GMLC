#!/bin/bash
#$ -N collect_base_2019
#$ -q long
#$ -cwd

# Chained collector for the ERCOT base case (prompt 26 T3; same pattern as
# prompt 27 T3's collector, two deltas: PCM_ERCOT env, ercot/tx123 push).
# Submitted from INSIDE waves/base_2019 by ercot_block_3.sh:
#   qsub -hold_jid "$JID" -cwd -M ylu28@nd.edu -m ea collect_base_2019.sh
# Order: integrity gate FIRST (self-contained sentinel check, never
# resubmit_missing.py); on gap: FAILED marker committed+pushed, exit; on
# pass: slimmed extract (incl. rider-(i) ruc_quality.csv from this job
# dir's newest base .o log), bot-identity commit of explicit paths, commit
# BEFORE rebase, push origin ercot/tx123, one retry on race.

set -euo pipefail

WAVE_DIR="$PWD"
ERCOT_DIR="$(cd "$PWD/../.." && pwd)"
REPO_DIR="$(cd "$ERCOT_DIR/../.." && pwd)"

source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate PCM_ERCOT
export PYTHONNOUSERSITE=1  # ~/.local vanilla prescient shadows the patched editable install

BOT=(-c user.name="ercot-bot" -c user.email="ercot-bot@noreply.github.com")

push_with_one_retry() {
    if ! git -C "$REPO_DIR" push origin ercot/tx123; then
        echo "push rejected — one rebase retry"
        git -C "$REPO_DIR" pull --rebase --autostash origin ercot/tx123
        git -C "$REPO_DIR" push origin ercot/tx123 || {
            echo "PUSH FAILED after retry — stopping with status visible:"
            git -C "$REPO_DIR" status
            git -C "$REPO_DIR" log --oneline -3
            exit 1
        }
    fi
}

RUN_DIR="$WAVE_DIR/runs/run_index_base"
if [[ ! -f "$RUN_DIR/overall_simulation_output.csv" ]]; then
    marker="$WAVE_DIR/FAILED_base_2019.md"
    {
        echo "# FAILED — base_2019 incomplete at collection"
        echo
        echo "No overall_simulation_output.csv in runs/run_index_base."
        echo "Check the newest ercot_base_2019.o* log in this dir; recovery"
        echo "is a fresh qsub base_job.sh after diagnosis (full-year runs"
        echo "have no mid-year restart). Generated $(date -u +%FT%TZ)."
    } > "$marker"
    git -C "$REPO_DIR" add -- "$marker"
    git -C "$REPO_DIR" "${BOT[@]}" commit -m "ercot-bot: FAILED marker (base_2019 incomplete)"
    push_with_one_retry
    echo "GATE FAIL: FAILED marker pushed; exiting without extract."
    exit 1
fi
echo "GATE PASS: base run complete"

JOBLOG=$(ls -t "$WAVE_DIR"/ercot_base_2019.o* 2>/dev/null | head -1 || true)
OUT_DIR="$ERCOT_DIR/extracts/base_2019"
python "$ERCOT_DIR/extract_ercot.py" "$RUN_DIR" "$OUT_DIR" --full \
    ${JOBLOG:+--joblog "$JOBLOG"}

git -C "$REPO_DIR" add -- "$OUT_DIR"
git -C "$REPO_DIR" "${BOT[@]}" commit -m "ercot-bot: base_2019 extract"
push_with_one_retry
echo "collect_base_2019 done: extract pushed to ercot/tx123"
