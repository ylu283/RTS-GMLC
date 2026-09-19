#!/bin/bash
# Stage-2 paste-block #2 — SUBMISSION (prompt 27 T3). Run on CRC AFTER
# block_1.sh printed SMOKE PASS:
#   bash block_2.sh 2>&1 | tee block_2.log
# Submits both Stage-2 arrays plus ONE chained collector (SGE dependency
# chain per the PI directive: hold_jid + bot commit/push completes the
# automation). No concurrency cap (Kay 09-19: Gurobi licenses are not a
# constraint) — all 16 n0 tasks may run at once; the backfill array still
# holds until n0 finishes so its manifests see completed n0 state.

set -euo pipefail

CAMPAIGN_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
REPO_DIR="$(cd "$CAMPAIGN_DIR/../.." && pwd)"

BRANCH="$(git -C "$REPO_DIR" branch --show-current)"
if [[ "$BRANCH" != "d6" ]]; then
    echo "ABORT: main clone is on '$BRANCH', expected d6 — never switch branches here."
    exit 1
fi
git -C "$REPO_DIR" pull --rebase --autostash

# gate on block 1's evidence unless Kay explicitly overrides
if [[ "${SKIP_SMOKE_CHECK:-0}" != "1" ]] && \
   [[ ! -f "$CAMPAIGN_DIR/smoke_stage2/run_index_smoke_nuc_w1/overall_simulation_output.csv" ]]; then
    echo "ABORT: no smoke sentinel — run block_1.sh first (or SKIP_SMOKE_CHECK=1 if it passed elsewhere)."
    exit 1
fi

cd "$CAMPAIGN_DIR/waves/stage2_C_n0"
# no -tc cap: Kay 09-19 — license is not a constraint, let all tasks run
J1=$(qsub -terse -t 1-16 stage2_C_n0_array.sh | cut -d. -f1)
[[ "$J1" =~ ^[0-9]+$ ]] || { echo "BAD JID: $J1"; exit 1; }
echo "stage2_C_n0 array submitted: J1=$J1"

cd ../stage2_backfill_C
J2=$(qsub -terse -t 1-10 -hold_jid "$J1" stage2_backfill_C_array.sh | cut -d. -f1)
[[ "$J2" =~ ^[0-9]+$ ]] || { echo "BAD JID: $J2"; exit 1; }
echo "stage2_backfill_C array submitted (holds on J1): J2=$J2"

# -M/-m ea on the COLLECTOR only (not the arrays: -m e on an array job
# emails once PER TASK = 26 emails). One email when everything incl. the
# summarize+push is done ('e'), plus one if the collector itself aborts ('a').
qsub -hold_jid "$J1,$J2" -cwd -M ylu28@nd.edu -m ea collect_stage2.sh   # ONE collector, both waves
echo "collector submitted (holds on J1,J2); it summarizes both waves and bot-pushes objectives to d6."
echo "JIDs: J1=$J1 J2=$J2"

qstat -u ylu28
