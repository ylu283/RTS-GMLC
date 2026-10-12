#!/bin/bash
#$ -N stoprule37_collect
#$ -q long
#$ -r n
#$ -cwd
#$ -o logs/
#$ -e logs/
#$ -M ylu28@nd.edu
#$ -m ea
# Prompt 37 collector (the ONLY job that emails and the only one that uses
# git): summarizes results/ -> summary/, lists missing tasks, commits
# summary/ + MISSING.txt on branch `stoprule`, pushes. Submitted by Kay with
#   qsub -hold_jid stoprule37 crc/stoprule_collect.sh
set -euo pipefail
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate BOGP_CRC
export PYTHONNOUSERSITE=1
export BOGP_PATH="${BOGP_PATH:-/groups/adowling/ylu28/bo-gp}"
python - <<'PY'
import csv, runner
from pathlib import Path
miss = [r["task"] for r in csv.DictReader(open("tasks.csv"))
        if not runner.result_path(r["problem"], r["method"], int(r["seed"]),
                                  float(r["noise"]), int(r["q"])).exists()]
Path("summary").mkdir(exist_ok=True)
Path("summary/MISSING.txt").write_text("\n".join(miss) + "\n")
print(len(miss), "missing")
PY
python collector.py
git add summary/
git -c user.name=stoprule-bot -c user.email=stoprule-bot@noreply.github.com \
    commit -m "stoprule-bot: prompt-37 CRC results summary" -- summary/ || true
git push origin stoprule
