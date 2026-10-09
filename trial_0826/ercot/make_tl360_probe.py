"""Build waves/tl360_probe/ (prompt 33 T1): 3 identical base solves at
RUC TimeLimit = 360 s — the frozen ERCOT config with EXACTLY ONE change.

TL=360 is a NEW SOLVER IDENTITY: separate wave, separate extract dir,
config stamped in design_matrix and manifest; these runs never mix with
TL=120 data, rulers, or deltas. 3 solves -> 3 pairwise |Delta| readings
(df = 2) per objective. Refuses an existing wave dir.
"""

import csv
import json
import os
from datetime import datetime, timezone

ERCOT_DIR = os.path.dirname(os.path.abspath(__file__))
WAVE = "tl360_probe"
WAVE_DIR = os.path.join(ERCOT_DIR, "waves", WAVE)
TL = 360

HEADER = ["index", "oat_site", "unit_type", "bus", "omega", "bid",
          "gen_pmax", "start_date", "num_days", "replicate_of",
          "ruc_time_limit"]

ARRAY = """#!/bin/bash
#$ -N tl360_probe_array
#$ -q long
#$ -cwd
#$ -t 1-3
#$ -pe smp 4
#$ -r n
# Prompt 33 T1: frozen config + EXACTLY ONE change (--ruc_time_limit 360).
# Threads=4 frozen (solver provenance). Runtime est. 18-27 h/run (the 44
# TL=120-capped days may gain up to +240 s each).
set -euo pipefail
WAVE_DIR="$PWD"
ERCOT_DIR="$(cd "$PWD/../.." && pwd)"
TRIAL_DIR="$(cd "$ERCOT_DIR/.." && pwd)"
mkdir -p "$WAVE_DIR/runs"   # prescient reporting uses os.mkdir — parent must exist
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate PCM_ERCOT
export PYTHONNOUSERSITE=1
module load gurobi

eval "$(python "$TRIAL_DIR/campaign/get_row.py" "$SGE_TASK_ID" "$WAVE_DIR/design_matrix.csv")"

python "$ERCOT_DIR/run_ercot_pcm.py" \\
    --index "$INDEX" \\
    --num_days "$NUM_DAYS" \\
    --start_date "$START_DATE" \\
    --ruc_time_limit 360 \\
    --ruc_threads 4 \\
    --output_directory "$WAVE_DIR/runs/run" \\
    --retrofit_gen_dict '{}'
"""

COLLECTOR = """#!/bin/bash
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
    git -C "$REPO_DIR" rm -q -- "$WAVE_DIR/FAILED_tl360_probe.md" 2>/dev/null \\
        || rm -f "$WAVE_DIR/FAILED_tl360_probe.md"
    echo "stale FAILED marker cleared"
fi

for i in 1 2 3; do
    JOBLOG=$(ls -t "$WAVE_DIR"/tl360_probe_array.o*."$i" 2>/dev/null | head -1 || true)
    FULL=""
    [[ "$i" == 1 ]] && FULL="--full"
    python "$ERCOT_DIR/extract_ercot.py" \\
        "$WAVE_DIR/runs/run_index_$i" \\
        "$ERCOT_DIR/extracts/tl360_probe/run_index_$i" $FULL \\
        ${JOBLOG:+--joblog "$JOBLOG"}
done

python "$ERCOT_DIR/compute_tl360.py"

git -C "$REPO_DIR" add -- "$ERCOT_DIR/extracts/tl360_probe" \\
    "$ERCOT_DIR/analysis/tl360_probe"
git -C "$REPO_DIR" "${BOT[@]}" commit -m "ercot-bot: tl360_probe extracts + readings (quarantined solver identity)"
push_with_retries
echo "collect_tl360_probe done"
"""

SUBMIT = """#!/bin/bash
# tl360_probe — array -> collector (prompt 33). Run ON CRC from anywhere:
#   bash submit_this.sh
cd "$(dirname "${BASH_SOURCE[0]}")"
set -euo pipefail
ERCOT_DIR="$(cd "$PWD/../.." && pwd)"
REPO_DIR="$(cd "$ERCOT_DIR/../.." && pwd)"
BRANCH="$(git -C "$REPO_DIR" branch --show-current)"
[[ "$BRANCH" == "ercot/tx123" ]] || { echo "ABORT: on '$BRANCH', expected ercot/tx123"; exit 1; }
git -C "$REPO_DIR" pull --rebase --autostash origin ercot/tx123

J=$(qsub -terse -t 1-3 tl360_probe_array.sh | cut -d. -f1)
[[ "$J" =~ ^[0-9]+$ ]] || { echo "BAD ARRAY JID: $J"; exit 1; }
C=$(qsub -terse -hold_jid "$J" -cwd -M ylu28@nd.edu -m ea collect_tl360_probe.sh)
[[ "$C" =~ ^[0-9]+$ ]] || { echo "BAD COLLECTOR JID: $C"; exit 1; }
echo "SUBMITTED tl360_probe: array=$J collector=$C"
qstat -u ylu28
"""


def main():
    if os.path.exists(WAVE_DIR):
        raise SystemExit(f"REFUSED: {WAVE_DIR} exists")
    os.makedirs(WAVE_DIR)
    with open(os.path.join(WAVE_DIR, "design_matrix.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=HEADER)
        w.writeheader()
        for i in (1, 2, 3):
            w.writerow({"index": i, "oat_site": "__BASE_REPLICATE__",
                        "unit_type": "", "bus": "", "omega": "", "bid": "",
                        "gen_pmax": "", "start_date": "01-01-2019",
                        "num_days": 365,
                        "replicate_of": "tl360_probe:1" if i > 1 else "",
                        "ruc_time_limit": TL})
    for i in (1, 2, 3):
        with open(os.path.join(WAVE_DIR, f"retrofit_gen_dict_{i}.json"), "w") as f:
            json.dump({}, f)
            f.write("\n")
    manifest = {"wave": WAVE, "n_rows": 3,
                "solver_identity": {"ruc_time_limit": TL, "ruc_threads": 4,
                                    "ruc_mipgap": 0.01,
                                    "quarantine": "NEVER mix with TL=120 data/"
                                                  "rulers/deltas (prompt 33)"},
                "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds")}
    with open(os.path.join(WAVE_DIR, "manifest.json"), "w") as f:
        json.dump(manifest, f, indent=2)
        f.write("\n")
    for name, body in (("tl360_probe_array.sh", ARRAY),
                       ("collect_tl360_probe.sh", COLLECTOR),
                       ("submit_this.sh", SUBMIT)):
        p = os.path.join(WAVE_DIR, name)
        with open(p, "w") as f:
            f.write(body)
        os.chmod(p, 0o755)
    print(f"built {WAVE_DIR} (3 base rows @ TL={TL})")


if __name__ == "__main__":
    main()
