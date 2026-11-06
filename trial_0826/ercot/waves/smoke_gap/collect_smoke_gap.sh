#!/bin/bash
#$ -N collect_smoke_gap
#$ -q long
#$ -cwd
#$ -r n
# Prompt 58 T1 collector (smoke_gap): gate -> --full extracts + runtimes.csv +
# tolerance table + wall-clock per task -> read_smoke.py (GAP_SMOKE.md,
# gap_smoke.csv) -> ercot-bot commit + 5-retry push. Email flags are applied
# by submit_this.sh on THIS job only. Never writes waves/GAP_DECISION.json.
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
for t in 1 2 3; do
    [[ -f "$WAVE_DIR/runs/run_index_$t/overall_simulation_output.csv" ]] || missing="$missing $t"
done
if [[ -n "$missing" ]]; then
    marker="$WAVE_DIR/FAILED_smoke_gap.md"
    { echo "# FAILED — smoke_gap incomplete"; echo; echo "missing:$missing";
      echo "Generated $(date -u +%FT%TZ)"; } > "$marker"
    git -C "$REPO_DIR" add -- "$marker"
    git -C "$REPO_DIR" "${BOT[@]}" commit -m "ercot-bot: FAILED marker (smoke_gap)"
    push_with_retries
    exit 1
fi
echo "GATE PASS: 3/3"
if [[ -f "$WAVE_DIR/FAILED_smoke_gap.md" ]]; then
    git -C "$REPO_DIR" rm -q -- "$WAVE_DIR/FAILED_smoke_gap.md" 2>/dev/null \
        || rm -f "$WAVE_DIR/FAILED_smoke_gap.md"
    echo "stale FAILED marker cleared"
fi

EXTR="$ERCOT_DIR/extracts/smoke_gap"
mkdir -p "$EXTR"
for t in 1 2 3; do
    OUT="$EXTR/task_$t"
    JOBLOG=$(ls -t "$WAVE_DIR"/smoke_gap_array.o*."$t" 2>/dev/null | head -1 || true)
    python "$ERCOT_DIR/extract_ercot.py" --data_dir "$DATA_DIR" \
        "$WAVE_DIR/runs/run_index_$t" \
        "$OUT" --full \
        ${JOBLOG:+--joblog "$JOBLOG"}
    cp -f "$WAVE_DIR/runs/run_index_$t/run/runtimes.csv" "$OUT/runtimes.csv" \
        || echo "WARNING: task $t has no Prescient runtimes.csv"
    # per-RUC-day Gurobi tolerance line (the identity check) + wall-clock stamps
    if [[ -n "$JOBLOG" ]]; then
        python "$ERCOT_DIR/analysis/gap_smoke/read_smoke.py" --joblog "$JOBLOG" \
            --tolerance-out "$OUT/ruc_tolerance.csv"
        grep -h "SMOKE_GAP_TASK=\|SMOKE_GAP_START\|SMOKE_GAP_END" "$JOBLOG" > "$OUT/wallclock.txt" || true
    else
        echo "WARNING: task $t: no job log found — tolerance UNVERIFIED (read_smoke will say so)"
    fi
done
python "$ERCOT_DIR/analysis/gap_smoke/read_smoke.py" \
    --extracts "$EXTR" --ref "$ERCOT_DIR/extracts/smoke_v2" \
    --out "$ERCOT_DIR/analysis/gap_smoke"

git -C "$REPO_DIR" add -- "$EXTR" \
    "$ERCOT_DIR/analysis/gap_smoke/GAP_SMOKE.md" \
    "$ERCOT_DIR/analysis/gap_smoke/gap_smoke.csv" \
    "$ERCOT_DIR/analysis/gap_smoke/gap_smoke_days.csv"
git -C "$REPO_DIR" "${BOT[@]}" commit -m "ercot-bot: smoke_gap extracts + GAP_SMOKE.md (prompt 58 T1)"
push_with_retries
echo "collect_smoke_gap done — Kay: read analysis/gap_smoke/GAP_SMOKE.md, then write waves/GAP_DECISION.json"
