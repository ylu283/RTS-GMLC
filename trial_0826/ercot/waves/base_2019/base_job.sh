#!/bin/bash
#$ -N ercot_base_2019
#$ -q long
#$ -cwd
#$ -pe smp 4

# ERCOT full-year base case (prompt 26 T3). Submit from INSIDE this wave
# dir of the CRC ERCOT WORKTREE:
#   cd <worktree>/trial_0826/ercot/waves/base_2019 && qsub base_job.sh
# Decided config: gurobi_persistent + TimeLimit=120 (Kay 09-19), threads=4
# (explicit, = slot count; drop '-pe smp 4' AND set --ruc_threads 1
# together if the cluster rejects the pe), output_solver_logs=True (rider
# (i): the collector parses this job's .o file into ruc_quality.csv).
# Runtime estimate ~15-22 h. Wall-clock headroom: the 'long' queue already
# carried the prior 113 h full-year base (job 2318970) — comfortably above
# the required >=48-72 h; house scripts request no h_rt.
# FULL YEAR — never cut num_days (Sep-30 has float).

set -euo pipefail

GUROBI_MODULE="gurobi"

WAVE_DIR="$PWD"
ERCOT_DIR="$(cd "$PWD/../.." && pwd)"

source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate PCM_ERCOT
export PYTHONNOUSERSITE=1  # ~/.local vanilla prescient shadows the patched editable install
module load "$GUROBI_MODULE"

python "$ERCOT_DIR/run_ercot_pcm.py" \
    --index base \
    --num_days 365 \
    --start_date 01-01-2019 \
    --ruc_time_limit 120 \
    --ruc_threads 4 \
    --output_directory "$WAVE_DIR/runs/run" \
    --retrofit_gen_dict '{}'
