#!/bin/bash
# methods_E login-node submitter (prompt 55 section 2.8). Run on the CRC LOGIN node
# (compute nodes are not submit hosts), from anywhere:
#   bash trial_0826/ercot/analysis/methods_E/submit_ready_E.sh            # submit READY items (hold mode)
#   bash .../submit_ready_E.sh --dry-run                                  # print only
#   bash .../submit_ready_E.sh --no-hold                                  # no held next rounds
# Idempotent: re-run after any collector email; it submits only what is READY,
# keyed on the pulled clone (ledgers, wave dirs, COLLECTED and SUBMITTED markers).
# One acquisition round ~ 2 min + 8 full-year runs ~ 5.3 h wall (21 core-h) on a
# fast node, ~11 h (45 core-h) on a slow one (standings 8) -> about 1 round per
# calendar day per lane; the five lanes run in parallel (40 slots).
cd "$(dirname "${BASH_SOURCE[0]}")"
set -euo pipefail

ME_DIR="$PWD"
ERCOT="$(cd "$ME_DIR/../.." && pwd)"
REPO_DIR="$(cd "$ERCOT/../.." && pwd)"

BRANCH="$(git -C "$REPO_DIR" branch --show-current)"
[[ "$BRANCH" == "ercot/tx123" ]] || { echo "ABORT: repo on '$BRANCH', expected ercot/tx123"; exit 1; }
[[ -f "$ERCOT/waves/GAP_DECISION.json" ]] || { echo "ABORT: waves/GAP_DECISION.json absent"; exit 1; }
[[ -f "$ERCOT/waves/smoke_v2/SMOKE_PASS" ]] || { echo "ABORT: waves/smoke_v2/SMOKE_PASS absent"; exit 1; }
grep -q 'extracts/methods_E_\*/\*\*/\*.csv.gz' "$ERCOT/.gitignore" || { echo "ABORT: .gitignore gz line for methods_E_* missing"; exit 1; }
exec 9>"$REPO_DIR/.git/methods_E.flock"
flock 9
git -C "$REPO_DIR" pull --ff-only origin ercot/tx123
flock -u 9

ARGS=(--execute)
for a in "$@"; do
    case "$a" in
        --dry-run) ARGS=() ;;
        --no-hold) ARGS+=(--no-hold) ;;
        *) echo "unknown option $a"; exit 1 ;;
    esac
done
echo "--- qquota ---"; qquota -u ylu28 2>/dev/null || true
python3 "$ME_DIR/submit_state_E.py" --root "$ERCOT" ${ARGS[@]+"${ARGS[@]}"} | tee /tmp/methods_E_submit.$$

[[ " ${ARGS[*]-} " == *" --execute "* ]] || exit 0
MARKERS=$(grep '^MARKER ' /tmp/methods_E_submit.$$ | cut -d' ' -f2- || true)
rm -f /tmp/methods_E_submit.$$
if [[ -n "$MARKERS" ]]; then
    flock 9
    BOT=(-c user.name="ercot-bot" -c user.email="ercot-bot@noreply.github.com")
    # shellcheck disable=SC2086
    git -C "$REPO_DIR" add -- $MARKERS
    git -C "$REPO_DIR" "${BOT[@]}" commit -m "ercot-bot: methods_E SUBMITTED markers ($(echo "$MARKERS" | wc -l | tr -d ' '))"
    for attempt in 1 2 3 4 5; do
        git -C "$REPO_DIR" push origin ercot/tx123 && break
        echo "push rejected (attempt $attempt/5) — rebase and retry"
        sleep $((30 + RANDOM % 60))
        git -C "$REPO_DIR" pull --rebase --autostash origin ercot/tx123
        [[ "$attempt" == 5 ]] && { git -C "$REPO_DIR" push origin ercot/tx123 || exit 1; }
    done
    flock -u 9
fi
qstat -u ylu28 || true
