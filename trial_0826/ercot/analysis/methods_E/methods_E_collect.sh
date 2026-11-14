#!/bin/bash
#$ -q long
#$ -r n
# Generic methods_E collector (prompt 55). Submitted ONLY by submit_ready_E.sh:
#   qsub -wd <ercot>/waves -v WAVE=<wave> -hold_jid <array> -N collect_<wave> -M ylu28@nd.edu -m ea methods_E_collect.sh
# gate (every row's overall_simulation_output.csv) -> --full extracts (every row)
# + runtimes.csv + wall-clock + identity.txt -> pool_objectives.py --run-dir ->
# pool_full_metrics.json -> COLLECTED marker -> ercot-bot commit of the SLIM
# tables + json + marker (*.csv.gz stay in storage: trial_0826/ercot/.gitignore
# `extracts/methods_E_*/**/*.csv.gz`), 5-retry push to ercot/tx123.
set -euo pipefail
: "${WAVE:?WAVE env var required (qsub -v WAVE=<wave>)}"
WAVES_DIR="$PWD"   # -wd trial_0826/ercot/waves
WAVE_DIR="$WAVES_DIR/$WAVE"
ERCOT_DIR="$(cd "$WAVES_DIR/.." && pwd)"
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

exec 9>"$REPO_DIR/.git/methods_E.flock"
if [[ ! -f "$WAVE_DIR/design_matrix.csv" ]]; then
    echo "FATAL: $WAVE_DIR has no design_matrix.csv at collection (held acquisition did not write it)"; exit 1
fi
N=$(python - "$WAVE_DIR/design_matrix.csv" <<'PY'
import csv, sys
print(sum(1 for _ in csv.DictReader(open(sys.argv[1]))))
PY
)
missing=""
for i in $(seq 1 "$N"); do
    [[ -f "$WAVE_DIR/runs/run_index_$i/overall_simulation_output.csv" ]] || missing="$missing $i"
done
if [[ -n "$missing" ]]; then
    marker="$WAVE_DIR/FAILED_$WAVE.md"
    { echo "# FAILED — $WAVE incomplete"; echo; echo "missing:$missing";
      echo "Recovery: resubmit the missing tasks ONCE (qsub -t <i> ...), then re-run this collector.";
      echo "Generated $(date -u +%FT%TZ)"; } > "$marker"
    flock 9
    git -C "$REPO_DIR" add -- "$marker"
    git -C "$REPO_DIR" "${BOT[@]}" commit -m "ercot-bot: FAILED marker ($WAVE)"
    push_with_retries
    flock -u 9
    exit 1
fi
echo "GATE PASS: $N/$N"
if [[ -f "$WAVE_DIR/FAILED_$WAVE.md" ]]; then
    git -C "$REPO_DIR" rm -q -- "$WAVE_DIR/FAILED_$WAVE.md" 2>/dev/null || rm -f "$WAVE_DIR/FAILED_$WAVE.md"
    echo "stale FAILED marker cleared"
fi

EXTR="$ERCOT_DIR/extracts/$WAVE"
mkdir -p "$EXTR"
cp -f "$ERCOT_DIR/waves/GAP_DECISION.json" "$EXTR/GAP_DECISION_used.json"
cp -f "$WAVE_DIR/design_matrix.csv" "$EXTR/design_matrix_used.csv"
echo "task,start_epoch,end_epoch,wall_s" > "$EXTR/wallclock.csv"
for i in $(seq 1 "$N"); do
    JOBLOG=$(ls -t "$WAVE_DIR"/"$WAVE"_array.o*."$i" 2>/dev/null | head -1 || true)
    python "$ERCOT_DIR/extract_ercot.py" --data_dir "$DATA_DIR" \
        "$WAVE_DIR/runs/run_index_$i" \
        "$EXTR/run_index_$i" --full \
        ${JOBLOG:+--joblog "$JOBLOG"}
    cp -f "$WAVE_DIR/runs/run_index_$i/run/runtimes.csv" "$EXTR/run_index_$i/runtimes.csv" \
        || echo "WARNING: row $i has no Prescient runtimes.csv"
    if [[ -n "$JOBLOG" ]]; then
        S=$(grep -h "METHODS_E_START" "$JOBLOG" | sed -n 's/.*epoch=\([0-9]*\).*/\1/p' | head -1)
        E=$(grep -h "METHODS_E_END" "$JOBLOG" | sed -n 's/.*epoch=\([0-9]*\).*/\1/p' | tail -1)
        echo "$i,${S:-},${E:-},$(( ${E:-0} - ${S:-0} ))" >> "$EXTR/wallclock.csv"
        grep -h "IDENTITY from GAP_DECISION.json" "$JOBLOG" > "$EXTR/run_index_$i/identity.txt" || true
    fi
    python "$ERCOT_DIR/pool_objectives.py" --run-dir "$EXTR/run_index_$i" \
        --out "$EXTR/run_index_$i/pool_full_metrics.json"
done
{ echo "wave=$WAVE rows=$N collected_utc=$(date -u +%FT%TZ)";
  echo "head=$(git -C "$REPO_DIR" rev-parse --short HEAD)";
  echo "identity=$(tr -d '\n' < "$ERCOT_DIR/waves/GAP_DECISION.json")"; } > "$EXTR/COLLECTED"

# git policy: slim tables + pool_full_metrics.json + runtimes.csv + manifest + marker;
# *.csv.gz are ignored by trial_0826/ercot/.gitignore and asserted absent below.
flock 9
git -C "$REPO_DIR" add -- "$EXTR"
if git -C "$REPO_DIR" diff --cached --name-only | grep -q '\.csv\.gz$'; then
    echo "ABORT: a *.csv.gz is staged — .gitignore line missing?"; git -C "$REPO_DIR" reset -q; exit 1
fi
git -C "$REPO_DIR" "${BOT[@]}" commit -m "ercot-bot: $WAVE extracts (slim + pool_full_metrics + COLLECTED; gz left in storage)"
push_with_retries
flock -u 9
echo "collect $WAVE done"
