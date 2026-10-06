#!/bin/bash
#$ -q long
#$ -cwd
#$ -r n

# Stage-2 BO acquisition job (prompt 30). Submitted by each wave's
# submit_this.sh with: -hold_jid <collector> -N acq_bo_C_r<k> -v BO_ROUND=<k>
# -o/-e analysis/bo_stage2/logs/ -M ylu28@nd.edu -m ea, from INSIDE the wave
# dir (so -cwd lands here and the ../.. walk below finds the campaign).
#
# Modes:
#   bash acquire_job.sh --check-env   (block #1; needs CAMPAIGN_ROOT or a
#                                      wave-dir cwd for the ledger path)
#   bash acquire_job.sh --dry-run     (block #1; REQUIRES CAMPAIGN_ROOT →
#                                      the scratch copy; PATH-shimmed qsub/git)
#   <qsub default>                    (the real unattended round)

set -euo pipefail

# Hardcoded activation — never auto-detect (prompt 30; block #1 builds this
# exact env and verifies via this script's own --check-env path).
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate BOGP_CRC
export PYTHONNOUSERSITE=1

CAMPAIGN="${CAMPAIGN_ROOT:-$(cd "$PWD/../.." && pwd)}"
BO_DIR="$CAMPAIGN/analysis/bo_stage2"
REPO_DIR="$(cd "$CAMPAIGN/../.." && pwd)"
BOGP_CLONE="${BOGP_CLONE:-/groups/adowling/ylu28/bo-gp}"

MODE="${1:-run}"

if [[ "$MODE" == "--check-env" ]]; then
    python -c "import torch, gpytorch, numpy, scipy, pandas, bogp; \
from bogp.mobo.qparego import propose_qparego_batch; \
from bogp.mobo.pareto import hypervolume_exact; \
from bogp.gp_model import GPRegressionModel, train_gp; \
print('BOGP_CRC imports OK:', torch.__version__, gpytorch.__version__)"
    SHA_EXPECT=$(python -c "import json; print(json.load(open('$BO_DIR/ledger.json'))['bo_gp_sha'])")
    SHA_HAVE=$(git -C "$BOGP_CLONE" rev-parse HEAD)
    [[ "$SHA_HAVE" == "$SHA_EXPECT" ]] || {
        echo "bo-gp SHA mismatch: clone $SHA_HAVE != ledger $SHA_EXPECT"; exit 1; }
    echo "CHECK-ENV PASS (bo-gp @ $SHA_HAVE)"
    exit 0
fi

if [[ "$MODE" == "--dry-run" ]]; then
    [[ -n "${CAMPAIGN_ROOT:-}" ]] || {
        echo "REFUSED: --dry-run without CAMPAIGN_ROOT would touch the real tree"
        exit 1
    }
fi

: "${BO_ROUND:?BO_ROUND env var required (qsub -v BO_ROUND=k)}"

on_err() {
    local rc=$?
    set +e
    marker="$BO_DIR/WEDGED_bo_r${BO_ROUND}.md"
    {
        echo "# WEDGED — acquisition job for round ${BO_ROUND} crashed (rc=$rc)"
        echo
        echo "at: $(date -u +%FT%TZ)   JOB_ID: ${JOB_ID:-n/a}"
        echo
        echo "## last step reached"
        cat "$BO_DIR/last_step.txt" 2>/dev/null || echo "(no breadcrumb)"
        echo
        echo "## any JIDs already issued"
        grep "SUBMITTED r" "$BO_DIR/ROUND_LOG.md" 2>/dev/null | tail -3 || true
        echo
        echo "## stderr tail"
        tail -40 "${SGE_STDERR_PATH:-/dev/null}" 2>/dev/null || true
        echo
        echo "Recovery (ROUND_LOG header): never qdel the running array from"
        echo "here, never resubmit automatically. Manual: push by hand + qsub"
        echo "the recorded triple — never re-run acquire_next for a round"
        echo "that already proposed."
    } > "$marker"
    git -C "$REPO_DIR" add -- "$marker" 2>/dev/null
    git -C "$REPO_DIR" -c user.name="bo-bot" -c user.email="bo-bot@noreply.github.com" \
        commit -m "bo-bot: WEDGED r${BO_ROUND}" 2>/dev/null
    git -C "$REPO_DIR" push origin d6 2>/dev/null || echo "WEDGED push failed (marker is on disk)"
    exit 1
}
trap on_err ERR

# No mid-campaign brain swap: assert the bo-gp clone is at the recorded SHA.
if [[ -d "$BOGP_CLONE" ]]; then
    SHA_EXPECT=$(python -c "import json; print(json.load(open('$BO_DIR/ledger.json'))['bo_gp_sha'])")
    SHA_HAVE=$(git -C "$BOGP_CLONE" rev-parse HEAD)
    [[ "$SHA_HAVE" == "$SHA_EXPECT" ]] || {
        echo "bo-gp SHA mismatch: $SHA_HAVE != $SHA_EXPECT"; false; }
else
    [[ "${BO_SKIP_SHA_ASSERT:-0}" == "1" ]] || {
        echo "bo-gp clone missing at $BOGP_CLONE (set BO_SKIP_SHA_ASSERT=1 only in tests)"; false; }
fi

python "$BO_DIR/acquire_next.py" run --round "$BO_ROUND"
