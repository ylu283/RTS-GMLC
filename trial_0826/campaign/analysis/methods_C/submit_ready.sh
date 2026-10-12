#!/bin/bash
# methods_C bastion submitter (prompt 35 §4). Run on the CRC LOGIN node
# (compute nodes are not submit hosts), from anywhere:
#   bash trial_0826/campaign/analysis/methods_C/submit_ready.sh            # submit READY items (hold mode)
#   bash .../submit_ready.sh --dry-run                                    # print only
#   bash .../submit_ready.sh --no-hold                                    # no held next rounds
# Idempotent: re-run after any email; it submits only what is READY, keyed on
# the SUBMITTED lines in PROGRESS.md + the pulled clone (never on qstat names).
cd "$(dirname "${BASH_SOURCE[0]}")"
set -euo pipefail

MC_DIR="$PWD"
CAMPAIGN="$(cd "$MC_DIR/../.." && pwd)"
REPO_DIR="$(cd "$CAMPAIGN/../.." && pwd)"
PROGRESS="$MC_DIR/PROGRESS.md"

BRANCH="$(git -C "$REPO_DIR" branch --show-current)"
[[ "$BRANCH" == "d6" ]] || { echo "ABORT: repo on '$BRANCH', expected d6"; exit 1; }
exec 9>"$REPO_DIR/.git/methods_C.flock"
flock 9
git -C "$REPO_DIR" pull --ff-only origin d6
flock -u 9

source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate BOGP_CRC
export PYTHONNOUSERSITE=1

ARGS=(--execute)
for a in "$@"; do
    case "$a" in
        --dry-run) ARGS=() ;;
        --no-hold) ARGS+=(--no-hold) ;;
        *) echo "unknown option $a"; exit 1 ;;
    esac
done
python "$MC_DIR/methods_state.py" --campaign "$CAMPAIGN" "${ARGS[@]}"

[[ " ${ARGS[*]-} " == *" --execute "* ]] || exit 0
flock 9
if ! git -C "$REPO_DIR" diff --quiet -- "$PROGRESS"; then
    BOT=(-c user.name="methods-bot" -c user.email="methods-bot@noreply.github.com")
    git -C "$REPO_DIR" add -- "$PROGRESS"
    git -C "$REPO_DIR" "${BOT[@]}" commit -m "methods-bot: SUBMITTED ($(grep -c '^SUBMITTED' "$PROGRESS") lines total)"
    for attempt in 1 2 3 4 5; do
        git -C "$REPO_DIR" push origin d6 && break
        echo "push rejected (attempt $attempt/5) — rebase and retry"
        sleep $((30 + RANDOM % 60))
        git -C "$REPO_DIR" pull --rebase --autostash origin d6
        [[ "$attempt" == 5 ]] && { git -C "$REPO_DIR" push origin d6 || exit 1; }
    done
fi
flock -u 9
qstat -u ylu28 || true
