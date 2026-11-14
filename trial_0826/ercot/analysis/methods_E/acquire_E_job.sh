#!/bin/bash
#$ -q long
#$ -r n

# methods_E acquisition job (prompt 55): grade round BO_ROUND of lane (ARM, SEED),
# propose BO_ROUND + 1, commit + push, STOP (--no-submit: compute nodes never
# qsub). Submitted ONLY by submit_ready_E.sh from the CRC login node:
#   qsub -wd <ercot> -v ARM=qnehvi,SEED=<s>,BO_ROUND=<k> -N methods_E_<arm>_s<s>_acq_r<k+1> \
#        -pe smp 4 -r n -o/-e analysis/methods_E/<arm>/s<s>/logs/ acquire_E_job.sh
# BO_ROUND=0 = init the lane ledger (if missing) + propose r1.
#
# Modes:
#   bash acquire_E_job.sh --check-env      (needs ARM; prints versions + bo-gp SHA check)
#   <qsub default>                         (the round)

set -euo pipefail
: "${ARM:=qnehvi}"
: "${SEED:?SEED env var required (qsub -v ARM=<arm>,SEED=<s>,BO_ROUND=<k>)}"

ERCOT="${ERCOT_ROOT:-$PWD}"
ME_DIR="$ERCOT/analysis/methods_E"
LANE_DIR="$ME_DIR/$ARM/s$SEED"
REPO_DIR="$(cd "$ERCOT/../.." && pwd)"
export BOGP_CLONE="${BOGP_CLONE:-$(python3 -c "import json; print(json.load(open('$ME_DIR/arms_E.json'))['bogp_clone_crc'])")}"
export BOGP_PATH="$BOGP_CLONE"
mkdir -p "$LANE_DIR/logs"

ENV_NAME=$(python3 -c "import json; print(json.load(open('$ME_DIR/arms_E.json'))['arms']['$ARM']['env'])")
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate "$ENV_NAME"
export PYTHONNOUSERSITE=1
export OMP_NUM_THREADS=4 MKL_NUM_THREADS=4

sha_check() {
    local expect have
    expect=$(python -c "import json; print(json.load(open('$ME_DIR/arms_E.json'))['bogp_sha_expected'])")
    have=$(git -C "$BOGP_CLONE" rev-parse HEAD)
    [[ "$have" == "$expect" ]] || { echo "bo-gp SHA mismatch: clone $have != arms_E.json $expect"; return 1; }
    echo "bo-gp @ $have (matches arms_E.json)"
}

if [[ "${1:-run}" == "--check-env" ]]; then
    python -c "import torch, gpytorch, numpy, scipy, pandas, botorch, bogp; \
from botorch.acquisition.multi_objective import qNoisyExpectedHypervolumeImprovement; \
print('$ENV_NAME:', torch.__version__, gpytorch.__version__, 'botorch', botorch.__version__, 'pandas', pandas.__version__)"
    sha_check
    echo "CHECK-ENV PASS ($ARM s$SEED)"
    exit 0
fi

: "${BO_ROUND:?BO_ROUND env var required}"

on_err() {
    local rc=$?
    set +e
    marker="$LANE_DIR/WEDGED_r${BO_ROUND}.md"
    {
        echo "# WEDGED — $ARM s$SEED acquisition for round ${BO_ROUND} crashed (rc=$rc)"
        echo
        echo "at: $(date -u +%FT%TZ)   JOB_ID: ${JOB_ID:-n/a}"
        echo
        echo "## last step reached"
        cat "$LANE_DIR/last_step.txt" 2>/dev/null || echo "(no breadcrumb)"
        echo
        echo "## stderr tail"
        tail -40 "${SGE_STDERR_PATH:-/dev/null}" 2>/dev/null || true
        echo
        echo "Recovery: never re-run an acquisition for a round that already proposed;"
        echo "held next-round jobs will fail loudly (no design_matrix) — qdel them."
    } > "$marker"
    exec 9>"$REPO_DIR/.git/methods_E.flock"; flock 9
    git -C "$REPO_DIR" add -- "$marker" 2>/dev/null
    git -C "$REPO_DIR" -c user.name="ercot-bot" -c user.email="ercot-bot@noreply.github.com" \
        commit -m "ercot-bot: WEDGED methods_E $ARM s$SEED r${BO_ROUND}" 2>/dev/null
    git -C "$REPO_DIR" push origin ercot/tx123 2>/dev/null || echo "WEDGED push failed (marker is on disk)"
    exit 1
}
trap on_err ERR

sha_check
python -c "import torch; torch.set_num_threads(4)"
python - <<EOF2
import os, sys, torch
torch.set_num_threads(4)
os.environ["ERCOT_ROOT"] = "$ERCOT"
sys.path.insert(0, "$ME_DIR")
import acquire_E
sys.exit(acquire_E.main(["run", "--arm", "$ARM", "--seed", "$SEED", "--round", "$BO_ROUND", "--no-submit"]))
EOF2
