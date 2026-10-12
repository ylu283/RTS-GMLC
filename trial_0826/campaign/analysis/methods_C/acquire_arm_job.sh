#!/bin/bash
#$ -q long
#$ -r n

# methods_C acquisition job (prompt 35): grade round BO_ROUND of arm ARM,
# propose BO_ROUND + 1, commit + push, STOP (--no-submit: compute nodes never
# qsub). Submitted ONLY by submit_ready.sh from the bastion:
#   qsub -wd <campaign> -v ARM=<arm>,BO_ROUND=<k> -N methods_C_<arm>_r<k+1> \
#        -pe smp 4 -r n -o/-e analysis/methods_C/<arm>/logs/ acquire_arm_job.sh
# BO_ROUND=0 = init the arm ledger (if missing) + propose r1 (P2/P3).
#
# Modes:
#   bash acquire_arm_job.sh --check-env   (needs ARM; prints versions + SHA check)
#   <qsub default>                        (the round)

set -euo pipefail
: "${ARM:?ARM env var required (qsub -v ARM=<arm>,BO_ROUND=<k>)}"

CAMPAIGN="${CAMPAIGN_ROOT:-$PWD}"
MC_DIR="$CAMPAIGN/analysis/methods_C"
ARM_DIR="$MC_DIR/$ARM"
REPO_DIR="$(cd "$CAMPAIGN/../.." && pwd)"
export BOGP_CLONE="${BOGP_CLONE:-/groups/adowling/ylu28/bo-gp}"
export BOGP_PATH="$BOGP_CLONE"
mkdir -p "$ARM_DIR/logs"

# env from arms.json (hardcoded per arm there — never auto-detected)
ENV_NAME=$(python3 -c "import json,sys; print(json.load(open('$MC_DIR/arms.json'))['arms']['$ARM']['env'])")
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate "$ENV_NAME"
export PYTHONNOUSERSITE=1
export OMP_NUM_THREADS=4 MKL_NUM_THREADS=4  # -pe smp 4; torch.set_num_threads(4) below

sha_check() {
    local expect have
    expect=$(python -c "import json; print(json.load(open('$MC_DIR/P1/ledger.json'))['bo_gp_sha'])")
    have=$(git -C "$BOGP_CLONE" rev-parse HEAD)
    [[ "$have" == "$expect" ]] || { echo "bo-gp SHA mismatch: clone $have != ledger $expect"; return 1; }
    echo "bo-gp @ $have (matches ledger)"
}

if [[ "${1:-run}" == "--check-env" ]]; then
    python -c "import torch, gpytorch, numpy, scipy, pandas, bogp; \
print('$ENV_NAME:', torch.__version__, gpytorch.__version__)"
    [[ "$ENV_NAME" == *botorch* ]] && python -c "import botorch; \
from botorch.acquisition.multi_objective import qNoisyExpectedHypervolumeImprovement; \
print('botorch', botorch.__version__)"
    sha_check
    echo "CHECK-ENV PASS ($ARM)"
    exit 0
fi

: "${BO_ROUND:?BO_ROUND env var required}"

on_err() {
    local rc=$?
    set +e
    marker="$ARM_DIR/WEDGED_${ARM}_r${BO_ROUND}.md"
    {
        echo "# WEDGED — $ARM acquisition for round ${BO_ROUND} crashed (rc=$rc)"
        echo
        echo "at: $(date -u +%FT%TZ)   JOB_ID: ${JOB_ID:-n/a}"
        echo
        echo "## last step reached"
        cat "$ARM_DIR/last_step.txt" 2>/dev/null || echo "(no breadcrumb)"
        echo
        echo "## stderr tail"
        tail -40 "${SGE_STDERR_PATH:-/dev/null}" 2>/dev/null || true
        echo
        echo "Recovery: never re-run an acquisition for a round that already proposed;"
        echo "held next-round jobs will fail loudly (no design_matrix) — qdel them."
    } > "$marker"
    exec 9>"$REPO_DIR/.git/methods_C.flock"; flock 9
    git -C "$REPO_DIR" add -- "$marker" 2>/dev/null
    git -C "$REPO_DIR" -c user.name="methods-bot" -c user.email="methods-bot@noreply.github.com" \
        commit -m "methods-bot: WEDGED $ARM r${BO_ROUND}" 2>/dev/null
    git -C "$REPO_DIR" push origin d6 2>/dev/null || echo "WEDGED push failed (marker is on disk)"
    exit 1
}
trap on_err ERR

# No mid-campaign brain swap: the bo-gp clone must be at the ledger SHA.
sha_check

python -c "import torch; torch.set_num_threads(4)"  # fail fast if torch is broken
python - <<EOF
import os, sys, torch
torch.set_num_threads(4)
sys.argv = ["acquire_arm.py", "run", "--arm", "$ARM", "--round", "$BO_ROUND", "--no-submit"]
sys.path.insert(0, "$MC_DIR")
import acquire_arm
sys.exit(acquire_arm.main(sys.argv[1:]))
EOF
