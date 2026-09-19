#!/bin/bash
# ERCOT paste-block #4 — SCREENING WAVE SUBMISSION + collector (prompt 26
# T4). Run ON CRC after ercot_block_3.sh:
#   bash ercot_block_4.sh 2>&1 | tee ercot_block_4.log
# 12 runs (9 OAT B=40 + __ALL__ + 2 replicate noise rows), no -tc cap, ONE
# chained collector with -M/-m ea. If the base extract has landed, the
# drafted availability-proxy site slate is CONFIRMED against the actual
# top curtailers first (hydro excluded); if not, the wave submits on the
# proxy ranking (protects "screening submitted by Sep 30") and the check
# runs at analysis time instead.

set -euo pipefail

ERCOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
REPO_DIR="$(cd "$ERCOT_DIR/../.." && pwd)"

BRANCH="$(git -C "$REPO_DIR" branch --show-current)"
[[ "$BRANCH" == "ercot/tx123" ]] || { echo "ABORT: worktree on '$BRANCH', expected ercot/tx123"; exit 1; }
git -C "$REPO_DIR" pull --rebase --autostash origin ercot/tx123

source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate PCM_ERCOT

if [[ -f "$ERCOT_DIR/extracts/base_2019/gen_summary.csv" ]]; then
    echo "--- confirming drafted slate vs base-case top curtailers (hydro excluded) ---"
    python - "$ERCOT_DIR" <<'EOF'
import sys
from pathlib import Path
import pandas as pd
ercot = Path(sys.argv[1])
gs = pd.read_csv(ercot / "extracts/base_2019/gen_summary.csv")
ren = gs[gs.unit_type.isin(["WIND", "PV"])].copy()   # HYDRO excluded: fake curtailment
top = (ren.sort_values("curtailment_mwh", ascending=False)
       .head(12)["Generator"].astype(str).tolist())
dm = pd.read_csv(ercot / "waves/screening_ercot/design_matrix.csv")
drafted = [s for s in dm["oat_site"].astype(str) if not s.startswith("__")]
overlap = [s for s in drafted if s in top]
print(f"base top-12 curtailers: {top}")
print(f"drafted OAT slate:      {drafted}")
print(f"overlap: {len(overlap)}/{len(drafted)} ({overlap})")
if len(overlap) < max(1, len(drafted) // 2):
    print("*** RANKING MISMATCH: <half the drafted slate is in the base's "
          "top curtailers. STOP — paste this log back so the wave is "
          "regenerated from the base ranking before submission. ***")
    sys.exit(1)
print("ranking CONFIRMED — proceeding to submit")
EOF
else
    echo "base extract not landed yet — submitting on the availability-proxy ranking (Sep-30 protection); ranking check moves to analysis time."
fi

cd "$ERCOT_DIR/waves/screening_ercot"
# no -tc cap: all 12 tasks may run at once (queue slots are the limiter)
J=$(qsub -terse -t 1-12 screening_ercot_array.sh | cut -d. -f1)
[[ "$J" =~ ^[0-9]+$ ]] || { echo "BAD JID: $J"; exit 1; }
echo "screening_ercot array submitted: J=$J (12 tasks, each ~15-22 h wall; no -tc)"
qsub -hold_jid "$J" -cwd -M ylu28@nd.edu -m ea collect_screening_ercot.sh
echo "collector submitted (holds on $J); it gates, extracts all 12 (incl. ruc_quality + replicate noise rows) and bot-pushes to ercot/tx123."

qstat -u ylu28
echo "BLOCK 4 DONE — qstat above is the submission evidence."
