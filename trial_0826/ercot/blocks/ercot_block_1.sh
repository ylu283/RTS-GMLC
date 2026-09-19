#!/bin/bash
# ERCOT paste-block #1 — CRC ercot worktree + H2-patch VERIFICATION + env
# record (prompt 26; the archaeology is done — this block verifies and
# documents). Run ON CRC from anywhere (self-contained; ~5-10 min, no qsub):
#   bash ercot_block_1.sh 2>&1 | tee ercot_block_1.log
# Prereq: T1 has pushed ercot/tx123 to origin (done). Kay pre-work DONE
# (09-19): PCM_ERCOT env (clone of PCM0826) carries editable
# gridx-prescient 2.2.3 from /users/ylu28/GitHub/Prescient.

set -euo pipefail

MAIN_CLONE="$GROUP/ylu28/RTS-GMLC"
ERCOT_WT="$GROUP/ylu28/RTS-GMLC-ercot"
PRESCIENT_DIR="/users/ylu28/GitHub/Prescient"
H2PATCH_SHA="a4c0849aff17bc98314b3f8319582c310c89773e"

# --- 1. second checkout: fetch-only worktree (NEVER pull the main clone) ---
git -C "$MAIN_CLONE" fetch origin
if [[ -d "$ERCOT_WT" ]]; then
    echo "ercot worktree already exists — skipping creation"
    git -C "$ERCOT_WT" pull --rebase --autostash origin ercot/tx123
else
    # explicit remote ref: no local branch exists on CRC yet, and
    # 'git worktree add' does not DWIM from a remote
    git -C "$MAIN_CLONE" worktree add ../RTS-GMLC-ercot -b ercot/tx123 origin/ercot/tx123
fi
ERCOT_DIR="$ERCOT_WT/trial_0826/ercot"
[[ -f "$ERCOT_DIR/run_ercot_pcm.py" ]] || { echo "ABORT: worktree lacks trial_0826/ercot"; exit 1; }

# --- 2. H2-patch verification (settled-facts checklist) --------------------
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate PCM_ERCOT

echo "--- (i) prescient version + editable path, HEAD equality BY HASH ---"
python -c "import prescient, importlib.metadata as im; \
print('gridx-prescient', im.version('gridx-prescient'), 'from', prescient.__file__)"
PVER=$(python -c "import importlib.metadata as im; print(im.version('gridx-prescient'))")
PFILE=$(python -c "import prescient; print(prescient.__file__)")
[[ "$PVER" == 2.2.3* ]] || { echo "ABORT: prescient version '$PVER' != 2.2.3"; exit 1; }
[[ "$PFILE" == "$PRESCIENT_DIR"/* ]] || { echo "ABORT: prescient not imported from the editable dir ($PFILE)"; exit 1; }
HEAD_SHA=$(git -C "$PRESCIENT_DIR" rev-parse HEAD)
[[ "$HEAD_SHA" == "$H2PATCH_SHA" ]] || { echo "ABORT: $PRESCIENT_DIR HEAD $HEAD_SHA != h2patch-2.2.3 $H2PATCH_SHA"; exit 1; }
echo "HEAD hash equality OK: $HEAD_SHA"

echo "--- (ii) record the single-file patch diff into the branch ---"
mkdir -p "$ERCOT_DIR/env"
git -C "$PRESCIENT_DIR" diff 2.2.3..h2patch-2.2.3 > "$ERCOT_DIR/env/h2patch_2.2.3.diff"
DIFF_FILES=$(git -C "$PRESCIENT_DIR" diff --name-only 2.2.3..h2patch-2.2.3)
echo "patched files: $DIFF_FILES"
[[ "$DIFF_FILES" == "prescient/engine/egret/reporting.py" ]] || \
    { echo "ABORT: patch touches more than reporting.py"; exit 1; }

echo "--- (iii) egret import + model-level metadata verify under PCM_ERCOT ---"
python -c "import egret, importlib.metadata as im; \
print('gridx-egret', im.version('gridx-egret'))"
python "$ERCOT_DIR/verify_metadata.py"

echo "--- env exports (solver-provenance companion record) ---"
pip freeze > "$ERCOT_DIR/env/PCM_ERCOT_pip_freeze.txt"
conda env export > "$ERCOT_DIR/env/PCM_ERCOT_conda_env.yml"
module load gurobi 2>/dev/null || true
{ gurobi_cl --version 2>/dev/null || echo "gurobi_cl not on PATH (record from a job log)"; } \
    | tee "$ERCOT_DIR/env/gurobi_version.txt"

# --- 3. commit the records (explicit paths, per-invocation bot identity) ---
git -C "$ERCOT_WT" add -- "$ERCOT_DIR/env"
git -C "$ERCOT_WT" -c user.name="ercot-bot" -c user.email="ercot-bot@noreply.github.com" \
    commit -m "ercot-bot: block1 H2-patch verification record + PCM_ERCOT env export"
git -C "$ERCOT_WT" push origin ercot/tx123 || {
    git -C "$ERCOT_WT" pull --rebase --autostash origin ercot/tx123
    git -C "$ERCOT_WT" push origin ercot/tx123
}

echo "BLOCK 1 PASS — worktree ready, patch verified (2.2.3 + reporting.py only, HEAD $H2PATCH_SHA), env recorded. Next: ercot_block_2.sh"
