#!/bin/bash
#$ -N collect_screening_ercot
#$ -q long
#$ -cwd

# Chained collector for the ERCOT screening wave (prompt 26 T4; prompt-27
# collector pattern, deltas: PCM_ERCOT env, ercot/tx123 push). Submitted
# from INSIDE waves/screening_ercot by ercot_block_4.sh:
#   qsub -hold_jid "$JID" -cwd -M ylu28@nd.edu -m ea collect_screening_ercot.sh
# Integrity gate FIRST (sentinel count vs design_matrix, self-contained,
# never resubmit_missing.py); on any gap: FAILED marker committed+pushed
# (no partial extracts), exit; on pass: per-run slimmed extracts incl.
# rider-(i) ruc_quality.csv (array task logs screening_ercot_array.o*.N),
# bot commit of explicit paths, commit BEFORE rebase, push, one retry.

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

# --- 1. integrity gate ------------------------------------------------------
missing=$(python - "$WAVE_DIR" <<'EOF'
import sys, csv, os
wdir = sys.argv[1]
with open(os.path.join(wdir, "design_matrix.csv"), newline="") as f:
    idx = [int(row["index"]) for row in csv.DictReader(f)]
missing = [i for i in idx
           if not os.path.isfile(os.path.join(
               wdir, "runs", f"run_index_{i}", "overall_simulation_output.csv"))]
print(" ".join(str(i) for i in missing))
EOF
)
if [[ -n "$missing" ]]; then
    marker="$WAVE_DIR/FAILED_screening_ercot.md"
    {
        echo "# FAILED — screening_ercot incomplete at collection"
        echo
        echo "Missing run indices (no overall_simulation_output.csv):"
        echo
        for i in $missing; do echo "- $i"; done
        echo
        echo "Recovery: manual 'qsub -t a-b screening_ercot_array.sh' per"
        echo "contiguous gap, then re-run this collector. Generated"
        echo "$(date -u +%FT%TZ) by collect_screening_ercot.sh."
    } > "$marker"
    echo "GATE FAIL: missing indices: $missing"
    git -C "$REPO_DIR" add -- "$marker"
    git -C "$REPO_DIR" "${BOT[@]}" commit -m "ercot-bot: FAILED marker (screening_ercot incomplete)"
    push_with_one_retry
    exit 1
fi
echo "GATE PASS: all 12 runs complete"

# --- 2. per-run slimmed extracts -------------------------------------------
paths=()
while IFS=, read -r i _; do
    [[ "$i" == "index" ]] && continue
    RUN_DIR="$WAVE_DIR/runs/run_index_$i"
    OUT_DIR="$ERCOT_DIR/extracts/screening_ercot/run_index_$i"
    JOBLOG=$(ls -t "$WAVE_DIR"/screening_ercot_array.o*."$i" 2>/dev/null | head -1 || true)
    python "$ERCOT_DIR/extract_ercot.py" "$RUN_DIR" "$OUT_DIR" \
        ${JOBLOG:+--joblog "$JOBLOG"}
    paths+=("$OUT_DIR")
done < "$WAVE_DIR/design_matrix.csv"

# --- 3. bot commit + push ---------------------------------------------------
git -C "$REPO_DIR" add -- "${paths[@]}"
git -C "$REPO_DIR" "${BOT[@]}" commit -m "ercot-bot: screening_ercot results (extracts incl. replicate noise rows)"
push_with_one_retry
echo "collect_screening_ercot done: extracts pushed to ercot/tx123"
