#!/bin/bash
# Prompt 28 T1 — priority pair-grid submission (Kay paste-block).
# Run ON CRC from THIS directory in the main d6 clone:
#   bash block_1.sh 2>&1 | tee block_1.log
# Submits the 3 priority pairs (243 tasks total, no -tc — fully parallel,
# queue permitting) by invoking each wave's OWN submit_this.sh, so the
# handed-off path is exactly the tested path. Each submit_this.sh does its
# own d6 guard + pull, array qsub, and chained collector (-M/-m ea on the
# collector only). Expect overnight-to-~2 days alongside the running
# Stage-2/ERCOT arrays.
#
# Priority rationale (prompt 28 T1.3):
#   nuclear x wind_317 — max type contrast + first 2-D data at nuclear
#                        omega > 0.5;
#   pv x tail          — the two newly-full-range tiers;
#   nuclear x pv       — baseload-conventional vs solar, both newly at 1.0.

set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
CAMPAIGN_DIR="$(cd "$HERE/../.." && pwd)"
REPO_DIR="$(cd "$CAMPAIGN_DIR/../.." && pwd)"

BRANCH="$(git -C "$REPO_DIR" branch --show-current)"
[[ "$BRANCH" == "d6" ]] || { echo "ABORT: repo on '$BRANCH', expected d6"; exit 1; }
git -C "$REPO_DIR" pull --rebase --autostash origin d6

for wave in pairgrid_nuclear_wind_317_C pairgrid_pv_tail_C pairgrid_nuclear_pv_C; do
    echo "=== submitting $wave ==="
    ( cd "$CAMPAIGN_DIR/waves/$wave" && bash submit_this.sh )
done

echo "=== BLOCK 1 DONE — 3 arrays + 3 collectors queued ==="
qstat -u ylu28
