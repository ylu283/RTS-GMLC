#!/bin/bash
# Stage-2 paste-block #1 — SMOKE (prompt 27 T3). Run on CRC:
#   bash block_1.sh 2>&1 | tee block_1.log
# ONE 3-day nuclear omega = 1.0 job before burning an overnight window on the
# first-ever thermal omega > 0.5: verifies Prescient accepts p_min = 0 on the
# fixed-committed unit (outputs present, no solver complaints). Expected
# wall: queue wait + ~15-30 min run; the block polls until the job leaves
# the queue (timeout 3 h). Only on SMOKE PASS proceed to block_2.sh.

set -euo pipefail

CAMPAIGN_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
TRIAL_DIR="$(cd "$CAMPAIGN_DIR/.." && pwd)"
REPO_DIR="$(cd "$TRIAL_DIR/.." && pwd)"

# main CRC clone must be on d6 (prompt 26's ERCOT worktree is separate and
# NOT our concern)
BRANCH="$(git -C "$REPO_DIR" branch --show-current)"
if [[ "$BRANCH" != "d6" ]]; then
    echo "ABORT: main clone is on '$BRANCH', expected d6 — never switch branches here."
    exit 1
fi
git -C "$REPO_DIR" pull --rebase --autostash

SMOKE_DIR="$CAMPAIGN_DIR/smoke_stage2"   # untracked scratch, CRC only
mkdir -p "$SMOKE_DIR"
cd "$SMOKE_DIR"

cat > retrofit_smoke.json <<'EOF'
{"121_NUCLEAR_1": {"PEM_fraction": 1.0, "PEM_bid": 40.0}}
EOF

cat > smoke_job.sh <<EOF
#!/bin/bash
#$ -N stage2_smoke_nuc_w1
#$ -q long
#$ -cwd
set -euo pipefail
GUROBI_MODULE="gurobi"
source "\$(conda info --base)/etc/profile.d/conda.sh"
conda activate PCM0826
module load "\$GUROBI_MODULE"
python "$TRIAL_DIR/multi_pem/multi_PEM_PCM.py" \\
    --index smoke_nuc_w1 \\
    --num_days 3 \\
    --start_date 01-01-2020 \\
    --output_directory "$SMOKE_DIR/run" \\
    --retrofit_gen_dict "\$(cat "$SMOKE_DIR/retrofit_smoke.json")"
EOF

JID=$(qsub -terse smoke_job.sh)
[[ "$JID" =~ ^[0-9]+$ ]] || { echo "BAD JID: $JID"; exit 1; }
echo "smoke job submitted: JID=$JID ($(date))"

waited=0
while qstat -j "$JID" >/dev/null 2>&1; do
    sleep 60
    waited=$((waited + 60))
    if (( waited >= 10800 )); then
        echo "SMOKE FAIL: job $JID still queued/running after 3 h — investigate."
        qstat -u ylu28
        exit 1
    fi
done
echo "smoke job left the queue after ~${waited}s ($(date))"

RUN_DIR="$SMOKE_DIR/run_index_smoke_nuc_w1"
FAIL=0
if [[ ! -f "$RUN_DIR/overall_simulation_output.csv" ]]; then
    echo "SMOKE FAIL: sentinel overall_simulation_output.csv missing in $RUN_DIR"
    FAIL=1
fi
JOBLOG=$(ls -t "$SMOKE_DIR"/stage2_smoke_nuc_w1.o* 2>/dev/null | head -1 || true)
if [[ -n "$JOBLOG" ]]; then
    echo "--- solver-complaint scan of $(basename "$JOBLOG") ---"
    n_bad=$(grep -ciE "infeasib|traceback" "$JOBLOG" || true)
    echo "infeasible/traceback matches: $n_bad"
    if (( n_bad > 0 )); then
        grep -iE "infeasib|traceback" "$JOBLOG" | head -20
        FAIL=1
    fi
else
    echo "SMOKE FAIL: no job log stage2_smoke_nuc_w1.o* found"
    FAIL=1
fi

if (( FAIL == 0 )); then
    # p_min = 0 acceptance evidence: the unit stays committed while dispatch
    # dips below the old p_min (was p_max before the retrofit patch)
    source "$(conda info --base)/etc/profile.d/conda.sh"
    conda activate PCM0826
    python - "$RUN_DIR" <<'EOF'
import sys
import pandas as pd
td = pd.read_csv(sys.argv[1] + "/thermal_detail.csv")
nuc = td[td["Generator"] == "121_NUCLEAR_1"]
print(f"121_NUCLEAR_1 hours={len(nuc)} dispatch min={nuc['Dispatch'].min():.1f} "
      f"max={nuc['Dispatch'].max():.1f} mean={nuc['Dispatch'].mean():.1f} "
      f"always committed={bool(nuc['Unit State'].all())}")
EOF
    echo "SMOKE PASS — Prescient accepted p_min = 0 on the fixed-committed unit. Proceed to block_2.sh."
else
    echo "SMOKE FAIL — do NOT run block_2.sh; paste this log back."
fi

qstat -u ylu28
exit "$FAIL"
