#!/bin/bash
# Prompt 30 block #1 — BOGP_CRC env + dry runs + LAUNCH ROUND 1 (Kay paste-block).
# Run ON CRC from this directory in the main d6 clone:
#   bash block_1.sh 2>&1 | tee block_1.log
set -euo pipefail

BO_DIR="$(cd "$(dirname "$0")" && pwd)"
CAMPAIGN="$(cd "$BO_DIR/../.." && pwd)"
REPO_DIR="$(cd "$CAMPAIGN/../.." && pwd)"
BOGP_CLONE="/groups/adowling/ylu28/bo-gp"
BOGP_SHA="60e6328236e745b3d34dc8cd704bb72888ae5d15"

[[ "$(git -C "$REPO_DIR" branch --show-current)" == "d6" ]] || { echo "ABORT: not on d6"; exit 1; }
git -C "$REPO_DIR" pull --rebase --autostash origin d6

# --- 1. bo-gp clone, DETACHED at the pinned SHA (never track the branch) -----
if [[ ! -d "$BOGP_CLONE" ]]; then
    git clone git@github.com:ylu283/bo-gp.git "$BOGP_CLONE"
fi
git -C "$BOGP_CLONE" fetch origin
git -C "$BOGP_CLONE" checkout --detach "$BOGP_SHA"
[[ "$(git -C "$BOGP_CLONE" rev-parse HEAD)" == "$BOGP_SHA" ]] || { echo "SHA checkout failed"; exit 1; }
echo "bo-gp detached @ $BOGP_SHA"

# --- 2. BOGP_CRC env (dedicated; PCM0826 lacks torch) ------------------------
source "$(conda info --base)/etc/profile.d/conda.sh"
if ! conda env list | grep -q "^BOGP_CRC "; then
    conda create -y -n BOGP_CRC python=3.11
    conda activate BOGP_CRC
    pip install torch --index-url https://download.pytorch.org/whl/cpu
    pip install gpytorch numpy scipy pandas
    pip install -e "$BOGP_CLONE"
    conda deactivate
fi
conda activate BOGP_CRC
mkdir -p "$BO_DIR/env" "$BO_DIR/logs"
conda env export > "$BO_DIR/env/BOGP_CRC.yml"
pip freeze > "$BO_DIR/env/BOGP_CRC_pip_freeze.txt"
conda deactivate

# --- 3. env verification via the wrapper's OWN activation path ---------------
( cd "$CAMPAIGN/waves/bo_C_r1" && bash "$BO_DIR/acquire_job.sh" --check-env )

# --- 4. dry runs against a SCRATCH COPY (never the real tree) ----------------
make_scratch() {
    local scr="$1"
    mkdir -p "$scr/trial_0826"
    rsync -a --exclude "runs" --exclude "*.o*" --exclude "smoke*" \
        "$CAMPAIGN/" "$scr/trial_0826/campaign/"
    git init -q -b d6 "$scr"
    git -C "$scr" -c user.name=dry -c user.email=dry@dry add -A
    git -C "$scr" -c user.name=dry -c user.email=dry@dry commit -q -m seed
    # seed the committed fake-round fixture into the scratch r1 wave
    cp "$BO_DIR/dryrun_fixture/objectives_r1.csv" \
       "$scr/trial_0826/campaign/waves/bo_C_r1/objectives.csv"
    git -C "$scr" -c user.name=dry -c user.email=dry@dry add -A
    git -C "$scr" -c user.name=dry -c user.email=dry@dry commit -q -m fixture
}

SHIM="$(mktemp -d)/shim"
mkdir -p "$SHIM"
REAL_GIT="$(command -v git)"
cat > "$SHIM/qsub" <<'SHIMEOF'
#!/bin/bash
echo "QSUB $@" >> "$SHIM_LOG"
if [[ "${QSUB_FAIL:-0}" == "1" ]]; then echo "forced qsub failure" >&2; exit 1; fi
N=$(( $(wc -l < "$SHIM_LOG") + 9000000 ))
for a in "$@"; do if [[ "$a" == "-t" ]]; then echo "$N.1-8:1"; exit 0; fi; done
echo "$N"
SHIMEOF
cat > "$SHIM/qstat" <<'SHIMEOF'
#!/bin/bash
exit 0
SHIMEOF
cat > "$SHIM/git" <<SHIMEOF
#!/bin/bash
for a in "\$@"; do
    if [[ "\$a" == "push" ]]; then echo "GIT-PUSH-INTERCEPTED \$@" >> "\$SHIM_LOG"; exit 0; fi
done
exec "$REAL_GIT" "\$@"
SHIMEOF
chmod +x "$SHIM"/qsub "$SHIM"/qstat "$SHIM"/git
REAL_PATH="$PATH"

REAL_STATE_BEFORE=$(git -C "$REPO_DIR" status --porcelain | sort | md5sum)

run_dry() {  # $1 = label, extra env via caller
    local scr; scr="$(mktemp -d)/repo"
    make_scratch "$scr"
    export SHIM_LOG="$scr/shim.log"; : > "$SHIM_LOG"
    export CAMPAIGN_ROOT="$scr/trial_0826/campaign"
    ( cd "$CAMPAIGN_ROOT/waves/bo_C_r1" && \
      PATH="$SHIM:$REAL_PATH" BO_ROUND=1 bash "$CAMPAIGN_ROOT/analysis/bo_stage2/acquire_job.sh" --dry-run ) \
      || true
    echo "$scr"
}

echo "=== DRY RUN (a): full round ==="
SCR_A=$(run_dry a)
LOG_A="$SCR_A/shim.log"
grep -q -- "-t 1-8" "$LOG_A" || { echo "FAIL: array qsub flags"; exit 1; }
grep -E -- "-hold_jid [0-9]+ .*collect_bo_C_r2" "$LOG_A" >/dev/null || { echo "FAIL: collector hold"; exit 1; }
grep -q -- "-terse" "$LOG_A" || { echo "FAIL: -terse"; exit 1; }
grep -E -- "-hold_jid [0-9]+ .*acq" "$LOG_A" >/dev/null || { echo "FAIL: acq hold"; exit 1; }
grep -q -- "-M ylu28@nd.edu" "$LOG_A" && grep -q -- "-m ea" "$LOG_A" || { echo "FAIL: email flags"; exit 1; }
grep -q -- "-v BO_ROUND=2" "$LOG_A" || { echo "FAIL: BO_ROUND env"; exit 1; }
grep -q "GIT-PUSH-INTERCEPTED" "$LOG_A" || { echo "FAIL: push not intercepted"; exit 1; }
[[ -d "$SCR_A/trial_0826/campaign/waves/bo_C_r2" ]] || { echo "FAIL: no r2 wave"; exit 1; }
grep -q "SUBMITTED r2:" "$SCR_A/trial_0826/campaign/analysis/bo_stage2/ROUND_LOG.md" || { echo "FAIL: no SUBMITTED line"; exit 1; }
grep -q -- "-r n" "$SCR_A/trial_0826/campaign/waves/bo_C_r2/bo_C_r2_array.sh" || { echo "FAIL: -r n header"; exit 1; }
echo "DRY RUN (a) PASS"

echo "=== DRY RUN (b): STOP_BO honored ==="
SCR_B="$(mktemp -d)/repo"
make_scratch "$SCR_B"
touch "$SCR_B/trial_0826/campaign/analysis/bo_stage2/STOP_BO"
export SHIM_LOG="$SCR_B/shim.log"; : > "$SHIM_LOG"
export CAMPAIGN_ROOT="$SCR_B/trial_0826/campaign"
( cd "$CAMPAIGN_ROOT/waves/bo_C_r1" && \
  PATH="$SHIM:$REAL_PATH" BO_ROUND=1 bash "$CAMPAIGN_ROOT/analysis/bo_stage2/acquire_job.sh" --dry-run )
[[ -f "$CAMPAIGN_ROOT/analysis/bo_stage2/BO_DONE.md" ]] || { echo "FAIL: no BO_DONE"; exit 1; }
! grep -q "QSUB" "$SHIM_LOG" || { echo "FAIL: STOP_BO still submitted"; exit 1; }
echo "DRY RUN (b) PASS"

echo "=== DRY RUN (c): forced qsub failure -> WEDGED via ERR trap ==="
SCR_C="$(mktemp -d)/repo"
make_scratch "$SCR_C"
export SHIM_LOG="$SCR_C/shim.log"; : > "$SHIM_LOG"
export CAMPAIGN_ROOT="$SCR_C/trial_0826/campaign"
set +e
( cd "$CAMPAIGN_ROOT/waves/bo_C_r1" && \
  PATH="$SHIM:$REAL_PATH" BO_ROUND=1 QSUB_FAIL=1 bash "$CAMPAIGN_ROOT/analysis/bo_stage2/acquire_job.sh" --dry-run )
RC=$?
set -e
[[ "$RC" -ne 0 ]] || { echo "FAIL: forced failure exited 0"; exit 1; }
[[ -f "$CAMPAIGN_ROOT/analysis/bo_stage2/WEDGED_bo_r1.md" ]] || { echo "FAIL: no WEDGED marker"; exit 1; }
grep -q "last step" "$CAMPAIGN_ROOT/analysis/bo_stage2/WEDGED_bo_r1.md" || { echo "FAIL: WEDGED lacks step"; exit 1; }
echo "DRY RUN (c) PASS"

unset CAMPAIGN_ROOT SHIM_LOG

# --- 5. ZERO files created under the real tree -------------------------------
REAL_STATE_AFTER=$(git -C "$REPO_DIR" status --porcelain | sort | md5sum)
[[ "$REAL_STATE_BEFORE" == "$REAL_STATE_AFTER" ]] || {
    echo "FAIL: dry runs touched the real tree:"; git -C "$REPO_DIR" status --porcelain; exit 1; }
[[ ! -d "$CAMPAIGN/waves/bo_C_r2" ]] || { echo "FAIL: real bo_C_r2 appeared"; exit 1; }
echo "real tree untouched: PASS"

# --- 6. shim PATH dropped, launch the REAL round 1 ---------------------------
[[ "$(command -v qsub)" != "$SHIM/qsub" ]] || { echo "FAIL: shim still on PATH"; exit 1; }
echo "qsub = $(command -v qsub) (system binary)"
bash "$CAMPAIGN/waves/bo_C_r1/submit_this.sh"

echo
echo "=== BLOCK 1 DONE — the chain is live ==="
qstat -u ylu28
echo
echo "KAY'S STANDING CARD:"
echo "  stop NOW:  touch $BO_DIR/STOP_BO   then qdel the three JIDs from the"
echo "             latest 'SUBMITTED r<k>:' line in ROUND_LOG.md"
echo "  silent-death watch: no email of ANY kind for 36 h => re-invoke the"
echo "  session to diagnose; never resubmit by hand."
