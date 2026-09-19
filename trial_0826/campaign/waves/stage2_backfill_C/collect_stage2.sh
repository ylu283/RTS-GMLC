#!/bin/bash
#$ -N collect_stage2
#$ -q long
#$ -cwd

# Chained collector for BOTH Stage-2 waves (prompt 27 T3; PI directive:
# hold_jid chain + bot commit/push completes the automation).
# Submitted from INSIDE waves/stage2_backfill_C with
#   qsub -hold_jid "$J1,$J2" -cwd collect_stage2.sh
# so it starts only after both arrays finish. First production use of the
# automation pattern — its .o log is part of the workflow-pain record (T4).
#
# Order of operations (deliberate):
#   1. integrity gate FIRST, self-contained (never resubmit_missing.py — that
#      is a Kay-run recovery tool: interactive prompt, deletes partials under
#      --yes, exits 0 regardless);
#   2. on any gap: FAILED_<wave>.md marker, commit + push the marker ONLY
#      (no partial CSVs), exit — the failure must be visible locally on pull;
#   3. on pass: summarize both waves, bot-identity commit of explicit paths,
#      commit BEFORE pull --rebase, push, ONE retry on race, then stop with
#      status visible.

set -euo pipefail

# --- env preamble: copied verbatim from the array template ------------------
WAVE_DIR="$PWD"
TRIAL_DIR="$(cd "$PWD/../../.." && pwd)"

source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate PCM0826

WAVES_DIR="$(cd "$WAVE_DIR/.." && pwd)"
CAMPAIGN_DIR="$(cd "$WAVE_DIR/../.." && pwd)"
REPO_DIR="$(cd "$TRIAL_DIR/.." && pwd)"
WAVES=("stage2_C_n0" "stage2_backfill_C")

BOT=(-c user.name="stage2-bot" -c user.email="stage2-bot@noreply.github.com")

# --- 1. integrity gate: sentinel count vs each design matrix itself ---------
declare -a MARKERS=()
for wave in "${WAVES[@]}"; do
    wdir="$WAVES_DIR/$wave"
    missing=$(python - "$wdir" <<'EOF'
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
        marker="$wdir/FAILED_${wave}.md"
        {
            echo "# FAILED — $wave incomplete at collection"
            echo
            echo "Missing run indices (no overall_simulation_output.csv):"
            echo
            for i in $missing; do echo "- $i"; done
            echo
            echo "Recovery: Kay runs resubmit_missing.py (interactive) or a"
            echo "manual 'qsub -t a-b' per contiguous gap, then re-runs this"
            echo "collector. Generated $(date -u +%FT%TZ) by collect_stage2.sh."
        } > "$marker"
        MARKERS+=("$marker")
        echo "GATE FAIL: $wave missing indices: $missing"
    else
        echo "GATE PASS: $wave complete ($(ls -d "$wdir"/runs/run_index_* | wc -l) run dirs)"
    fi
done

push_with_one_retry() {
    if ! git -C "$REPO_DIR" push origin d6; then
        echo "push rejected — one rebase retry"
        git -C "$REPO_DIR" pull --rebase --autostash origin d6
        git -C "$REPO_DIR" push origin d6 || {
            echo "PUSH FAILED after retry — stopping with status visible:"
            git -C "$REPO_DIR" status
            git -C "$REPO_DIR" log --oneline -3
            exit 1
        }
    fi
}

if [[ ${#MARKERS[@]} -gt 0 ]]; then
    git -C "$REPO_DIR" add -- "${MARKERS[@]}"
    git -C "$REPO_DIR" "${BOT[@]}" commit -m "stage2-bot: FAILED markers (incomplete stage2 wave(s))"
    push_with_one_retry
    echo "FAILED markers committed and pushed; exiting without summarize."
    exit 1
fi

# --- 2. summarize both waves -------------------------------------------------
for wave in "${WAVES[@]}"; do
    python "$CAMPAIGN_DIR/summarize_wave.py" "$WAVES_DIR/$wave"
done

# --- 3. bot commit (explicit paths only), commit BEFORE pull --rebase, push --
paths=()
for wave in "${WAVES[@]}"; do
    paths+=("$WAVES_DIR/$wave/objectives.csv" "$WAVES_DIR/$wave/site_detail.csv")
done
git -C "$REPO_DIR" add -- "${paths[@]}"
git -C "$REPO_DIR" "${BOT[@]}" commit -m "stage2-bot: stage2_C_n0 + stage2_backfill_C results"
push_with_one_retry
echo "collect_stage2 done: objectives pushed for ${WAVES[*]}"
