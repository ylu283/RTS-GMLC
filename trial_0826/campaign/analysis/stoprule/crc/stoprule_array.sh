#!/bin/bash
#$ -N stoprule37
#$ -q long
#$ -pe smp 4
#$ -r n
#$ -cwd
#$ -o logs/
#$ -e logs/
# Prompt 37 CRC array: one task = one trajectory = row $SGE_TASK_ID of
# tasks.csv. Submitted ONCE by Kay from INSIDE analysis/stoprule of the
# SEPARATE CRC checkout of branch `stoprule` (never the shared RTS-GMLC clone):
#   qsub -t 1-<N> crc/stoprule_array.sh
# Checkpoint per round (resume on restart). NO git here; the collector job
# merges and commits. No -tc. No email from tasks.
set -euo pipefail
source "$(conda info --base)/etc/profile.d/conda.sh"
export PYTHONNOUSERSITE=1
export BOGP_PATH="${BOGP_PATH:-/groups/adowling/ylu28/bo-gp}"
export OMP_NUM_THREADS="$NSLOTS" MKL_NUM_THREADS="$NSLOTS" OPENBLAS_NUM_THREADS="$NSLOTS"
TASKS="${TASKS:-tasks.csv}"
METHOD=$(awk -F, -v t="$SGE_TASK_ID" 'NR>1 && $1==t {print $4}' "$TASKS")
[[ -n "$METHOD" ]] || { echo "no task $SGE_TASK_ID in $TASKS"; exit 1; }
if [[ "$METHOD" == "M3" ]]; then conda activate BOGP_CRC_botorch; else conda activate BOGP_CRC; fi
[[ "$(git -C "$BOGP_PATH" rev-parse HEAD)" == 60e6328* ]] || { echo "bo-gp SHA mismatch"; exit 1; }
python -u runner.py task --tasks "$TASKS" --row "$SGE_TASK_ID"
