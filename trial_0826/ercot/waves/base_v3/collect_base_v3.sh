#!/bin/bash
#$ -N collect_base_v3
#$ -q long
#$ -cwd
#$ -r n
# Collector (base_v3): gate -> --full extract + runtimes.csv + wall-clock ->
# pool metrics (pool_objectives.py --run-dir, ON CRC under PCM_ERCOT) ->
# ercot-bot commit of the SLIM tables + pool_full_metrics.json + runtimes.csv
# + extract_manifest.json + identity.txt + GAP_DECISION_used.json; *.csv.gz
# stay uncommitted (trial_0826/ercot/.gitignore) in $GROUP storage. Email
# flags are applied by submit_this.sh on THIS job only.
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
for i in $(seq 1 1); do
    [[ -f "$WAVE_DIR/runs/run_index_$i/overall_simulation_output.csv" ]] || missing="$missing $i"
done
if [[ -n "$missing" ]]; then
    marker="$WAVE_DIR/FAILED_base_v3.md"
    { echo "# FAILED — base_v3 incomplete"; echo; echo "missing:$missing";
      echo "Generated $(date -u +%FT%TZ)"; } > "$marker"
    git -C "$REPO_DIR" add -- "$marker"
    git -C "$REPO_DIR" "${BOT[@]}" commit -m "ercot-bot: FAILED marker (base_v3)"
    push_with_retries
    exit 1
fi
echo "GATE PASS: 1/1"
if [[ -f "$WAVE_DIR/FAILED_base_v3.md" ]]; then
    git -C "$REPO_DIR" rm -q -- "$WAVE_DIR/FAILED_base_v3.md" 2>/dev/null \
        || rm -f "$WAVE_DIR/FAILED_base_v3.md"
    echo "stale FAILED marker cleared"
fi

EXTR="$ERCOT_DIR/extracts/base_v3"
mkdir -p "$EXTR"
cp -f "$ERCOT_DIR/waves/GAP_DECISION.json" "$EXTR/GAP_DECISION_used.json"
echo "task,start_epoch,end_epoch,wall_s" > "$EXTR/wallclock.csv"
for i in $(seq 1 1); do
    JOBLOG=$(ls -t "$WAVE_DIR"/base_v3_array.o*."$i" 2>/dev/null | head -1 || true)
    python "$ERCOT_DIR/extract_ercot.py" --data_dir "$DATA_DIR" \
        "$WAVE_DIR/runs/run_index_$i" \
        "$EXTR/run_index_$i" --full \
        ${JOBLOG:+--joblog "$JOBLOG"}
    cp -f "$WAVE_DIR/runs/run_index_$i/run/runtimes.csv" "$EXTR/run_index_$i/runtimes.csv" \
        || echo "WARNING: row $i has no Prescient runtimes.csv"
    if [[ -n "$JOBLOG" ]]; then
        S=$(grep -h "BASE_V3_START" "$JOBLOG" | sed -n 's/.*epoch=\([0-9]*\).*/\1/p' | head -1)
        E=$(grep -h "BASE_V3_END" "$JOBLOG" | sed -n 's/.*epoch=\([0-9]*\).*/\1/p' | tail -1)
        echo "$i,${S:-},${E:-},$(( ${E:-0} - ${S:-0} ))" >> "$EXTR/wallclock.csv"
        grep -h "IDENTITY from GAP_DECISION.json" "$JOBLOG" > "$EXTR/run_index_$i/identity.txt" || true
    fi
    python "$ERCOT_DIR/pool_objectives.py" --run-dir "$EXTR/run_index_$i" \
        --out "$EXTR/run_index_$i/pool_full_metrics.json"
done

# git policy: slim tables + pool_full_metrics.json + runtimes.csv + manifest +
# identity.txt + GAP_DECISION_used.json; *.csv.gz are ignored by
# trial_0826/ercot/.gitignore and asserted absent below.
git -C "$REPO_DIR" add -- "$EXTR"
if git -C "$REPO_DIR" diff --cached --name-only | grep -q '\.csv\.gz$'; then
    echo "ABORT: a *.csv.gz is staged — .gitignore line missing?"; git -C "$REPO_DIR" reset -q; exit 1
fi
git -C "$REPO_DIR" "${BOT[@]}" commit -m "ercot-bot: base_v3 extracts (v3 base; slim + pool_full_metrics; gz left in storage)"
push_with_retries
echo "collect_base_v3 done"
