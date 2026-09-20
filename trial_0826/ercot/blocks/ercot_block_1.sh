#!/bin/bash
# ERCOT paste-block #1 — CRC ercot worktree + H2-patch VERIFICATION + env
# record (prompt 26; the archaeology is done — this block verifies and
# documents). Run ON CRC from INSIDE the main RTS-GMLC clone (any subdir;
# ~5-10 min, no qsub):
#   bash ercot_block_1.sh 2>&1 | tee ercot_block_1.log
# Prereq: T1 has pushed ercot/tx123 to origin (done). Kay pre-work DONE
# (09-19): PCM_ERCOT env (clone of PCM0826) carries editable
# gridx-prescient 2.2.3 from /users/ylu28/GitHub/Prescient.

set -euo pipefail

# main clone: derive from the repo this runs inside (CRC has no $GROUP
# env var — that assumption broke on first run); $GROUP layout is the
# fallback only.
if TOP=$(git rev-parse --show-toplevel 2>/dev/null) \
   && [[ "$(basename "$TOP")" == "RTS-GMLC" ]]; then
    MAIN_CLONE="$TOP"
elif [[ -n "${TOP:-}" && "$(basename "$TOP")" == "RTS-GMLC-ercot" ]]; then
    # run from inside the ercot worktree — main clone is its sibling
    MAIN_CLONE="$(dirname "$TOP")/RTS-GMLC"
else
    MAIN_CLONE="${GROUP:?run from inside the CRC RTS-GMLC clone (or its ercot worktree), or export GROUP}/ylu28/RTS-GMLC"
fi
ERCOT_WT="$(dirname "$MAIN_CLONE")/RTS-GMLC-ercot"
echo "main clone: $MAIN_CLONE"
echo "ercot worktree target: $ERCOT_WT"
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
export PYTHONNOUSERSITE=1  # ~/.local vanilla prescient shadows the patched editable install

echo "--- (i) prescient version + editable path, HEAD equality BY HASH ---"
# NOTE: under a PEP 660 editable install the top-level package's
# __file__ is None and __path__ is a finder hook token — neither is a
# filesystem path. The reliable location probe is a SUBMODULE's
# __file__ (always a real source path); we probe the patched module
# itself, which doubles as an import check of the patch site.
python -c "import prescient.simulator, importlib.metadata as im, prescient.engine.egret.reporting as m; \
print('gridx-prescient', im.version('gridx-prescient'), 'from', m.__file__)"
PVER=$(python -c "import importlib.metadata as im; print(im.version('gridx-prescient'))")
# import simulator FIRST: egret<->simulator have an order-sensitive
# circular import; the egret-side entry alone fails
PMOD=$(python -c "import prescient.simulator, prescient.engine.egret.reporting as m; print(m.__file__)")
[[ "$PVER" == 2.2.3* ]] || { echo "ABORT: prescient version '$PVER' != 2.2.3"; exit 1; }
[[ "$PMOD" == "$PRESCIENT_DIR"/* ]] || { echo "ABORT: prescient not imported from the editable dir ($PMOD)"; exit 1; }
HEAD_SHA=$(git -C "$PRESCIENT_DIR" rev-parse HEAD)
[[ "$HEAD_SHA" == "$H2PATCH_SHA" ]] || { echo "ABORT: $PRESCIENT_DIR HEAD $HEAD_SHA != h2patch-2.2.3 $H2PATCH_SHA"; exit 1; }
echo "HEAD hash equality OK: $HEAD_SHA"

echo "--- (ii) record the single-file patch diff into the branch ---"
# the CRC clone may lack the upstream 2.2.3 TAG — but HEAD~2 IS the
# 2.2.3 commit (the patch is exactly 2 commits); assert that by hash
# and diff against it, no tag needed.
V223_SHA="97e5dcfe4cd97302baf8bba1f53f1f24ea532340"
BASE_SHA=$(git -C "$PRESCIENT_DIR" rev-parse HEAD~2)
[[ "$BASE_SHA" == "$V223_SHA" ]] || { echo "ABORT: HEAD~2 $BASE_SHA != 2.2.3 tag commit $V223_SHA"; exit 1; }
mkdir -p "$ERCOT_DIR/env"
git -C "$PRESCIENT_DIR" diff HEAD~2..HEAD > "$ERCOT_DIR/env/h2patch_2.2.3.diff"
DIFF_FILES=$(git -C "$PRESCIENT_DIR" diff --name-only HEAD~2..HEAD)
echo "patched files: $DIFF_FILES"
[[ "$DIFF_FILES" == "prescient/engine/egret/reporting.py" ]] || \
    { echo "ABORT: patch touches more than reporting.py"; exit 1; }

echo "--- (iii) egret import + model-level metadata verify under PCM_ERCOT ---"
# egret is ALSO patched (editable ercotpatch-0.6.2 from Kay's fork):
# 0.6.2 + one 2-line commit in parsers/rts_gmlc/parser.py raising the
# fuel-curve rounding precision — coarse 0.1 MW / 0.01 quantization made
# near-flat heat-rate segments non-convex and egret's UC-model convexity
# check killed every run (gen 14). Same class of fix as Kay's original
# Egret ERCOT branch (0.5.5 era); date/bus-id fixes from that branch are
# NOT needed on 0.6.2 (upstream fixed dates; metadata verify proved
# parsing). Verify by hash, record the diff.
EGRET_DIR="/users/ylu28/GitHub/Egret"
EGRETPATCH_SHA="e4a244da7a74a3258ac769c3ae8c7a15fbe639e2"
V062_SHA="ede56b8a8be333520ea04813d282a472f6342f45"
python -c "import egret, importlib.metadata as im; \
print('gridx-egret', im.version('gridx-egret'))"
EMOD=$(python -c "import egret.parsers.rts_gmlc.parser as m; print(m.__file__)")
[[ "$EMOD" == "$EGRET_DIR"/* ]] || { echo "ABORT: egret parser not from the editable dir ($EMOD)"; exit 1; }
EHEAD=$(git -C "$EGRET_DIR" rev-parse HEAD)
[[ "$EHEAD" == "$EGRETPATCH_SHA" ]] || { echo "ABORT: $EGRET_DIR HEAD $EHEAD != ercotpatch-0.6.2 $EGRETPATCH_SHA"; exit 1; }
EBASE=$(git -C "$EGRET_DIR" rev-parse HEAD~1)
[[ "$EBASE" == "$V062_SHA" ]] || { echo "ABORT: egret HEAD~1 $EBASE != 0.6.2 tag commit $V062_SHA"; exit 1; }
git -C "$EGRET_DIR" diff HEAD~1..HEAD > "$ERCOT_DIR/env/egretpatch_0.6.2.diff"
echo "egret patch verified: 0.6.2 + parser precision fix ($EGRETPATCH_SHA)"
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
