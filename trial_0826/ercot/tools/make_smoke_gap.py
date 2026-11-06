#!/usr/bin/env python3
"""Prompt 58 T1 — build the RUC-gap smoke `waves/smoke_gap/` (E-D6).

Three tasks, one SGE array (-t 1-3, 4 slots each, -r n, -q long). Every task
is the smoke_v2 solve (3 days from 01-01-2019, v2 data, base dict {}) with
exactly two identity parameters changed:

  task  --ruc_mipgap  --ruc_time_limit  role
  1     0.01          1200              control: BYTE-IDENTICAL to extracts/smoke_v2
  2     0.001         1200              candidate identity
  3     0.0001        1200              stretch arm

The collector (held on the array) extracts every task --full into
extracts/smoke_gap/task_N/, copies Prescient's runtimes.csv, writes the
per-RUC-day Gurobi tolerance table (analysis/gap_smoke/read_smoke.py
--joblog) and the wall-clock stamps, then runs read_smoke.py -> GAP_SMOKE.md
+ gap_smoke.csv. It never writes waves/GAP_DECISION.json (Kay does).

Conventions copied from tools/make_v2_waves.py: HEADER/ENV/PUSH blocks,
mkdir -p lesson, 5-retry push, email on the collector only, branch assert
in submit_this.sh. SMOKE_GATE is not needed (this IS a smoke).
"""
import sys
from pathlib import Path

ERCOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ERCOT / "tools"))
from make_v2_waves import EMAIL, ENV, HEADER, PUSH, V2_DATA_REL, extract_cmd, write  # noqa: E402

WAVE = "smoke_gap"
TASKS = {1: (0.01, 1200), 2: (0.001, 1200), 3: (0.0001, 1200)}
NUM_DAYS = 3
START_DATE = "01-01-2019"


def task_case():
    lines = ['case "$SGE_TASK_ID" in']
    for t, (gap, tl) in TASKS.items():
        lines.append(f"    {t}) RUC_MIPGAP={gap}; RUC_TIME_LIMIT={tl} ;;")
    lines.append('    *) echo "ABORT: unknown task $SGE_TASK_ID"; exit 1 ;;')
    lines.append("esac")
    return "\n".join(lines)


def build(waves=ERCOT / "waves"):
    d = waves / WAVE
    ntask = len(TASKS)
    write(d / "retrofit_gen_dict_smoke.json", "{}\n", 0o644)
    write(d / "design_matrix.csv",
          "task,ruc_mipgap,ruc_time_limit,role,start_date,num_days\n"
          + "\n".join(f"{t},{g},{tl},{r},{START_DATE},{NUM_DAYS}" for (t, (g, tl)), r in
                      zip(TASKS.items(), ("control_identical_to_smoke_v2",
                                          "candidate_identity", "stretch_arm")))
          + "\n", 0o644)
    write(d / f"{WAVE}_array.sh", f"""#!/bin/bash
#$ -N {WAVE}_array
#$ -q long
#$ -cwd
#$ -t 1-{ntask}
#$ -pe smp 4
#$ -r n
# Prompt 58 T1 gap smoke (E-D6): smoke_v2 solve (3 days from {START_DATE}, v2
# data, base) with --ruc_mipgap / --ruc_time_limit per task. Task 1 must be
# byte-identical to extracts/smoke_v2 (gap 0.01; the 120 s TL never bound
# there, so TL 1200 changes nothing). Gurobi prints
# "Optimal solution found (tolerance <gap>)" on every RUC day: the collector
# reads that line — a log showing 1.00e-02 on task 2/3 is a FAILED smoke.
{HEADER}{task_case()}
echo "SMOKE_GAP_TASK=$SGE_TASK_ID RUC_MIPGAP=$RUC_MIPGAP RUC_TIME_LIMIT=$RUC_TIME_LIMIT"
echo "SMOKE_GAP_START $(date -u +%FT%TZ) epoch=$(date +%s)"
{ENV}module load gurobi

mkdir -p "$WAVE_DIR/runs"   # prescient reporting uses os.mkdir — parent must exist
INDEX="$SGE_TASK_ID" NUM_DAYS={NUM_DAYS} START_DATE={START_DATE} OUT_PARENT="$WAVE_DIR/runs"
DICT="$WAVE_DIR/retrofit_gen_dict_smoke.json"
python "$ERCOT_DIR/run_ercot_pcm.py" \\
    --data_dir "$DATA_DIR" \\
    --index "$INDEX" \\
    --num_days "$NUM_DAYS" \\
    --start_date "$START_DATE" \\
    --ruc_mipgap "$RUC_MIPGAP" \\
    --ruc_time_limit "$RUC_TIME_LIMIT" \\
    --ruc_threads 4 \\
    --output_directory "$OUT_PARENT/run" \\
    --retrofit_gen_dict "$(cat "$DICT")"
echo "SMOKE_GAP_END $(date -u +%FT%TZ) epoch=$(date +%s)"
""")
    tasks = " ".join(str(t) for t in TASKS)
    write(d / f"collect_{WAVE}.sh", f"""#!/bin/bash
#$ -N collect_{WAVE}
#$ -q long
#$ -cwd
#$ -r n
# Prompt 58 T1 collector ({WAVE}): gate -> --full extracts + runtimes.csv +
# tolerance table + wall-clock per task -> read_smoke.py (GAP_SMOKE.md,
# gap_smoke.csv) -> ercot-bot commit + 5-retry push. Email flags are applied
# by submit_this.sh on THIS job only. Never writes waves/GAP_DECISION.json.
{HEADER}{ENV}
{PUSH}
missing=""
for t in {tasks}; do
    [[ -f "$WAVE_DIR/runs/run_index_$t/overall_simulation_output.csv" ]] || missing="$missing $t"
done
if [[ -n "$missing" ]]; then
    marker="$WAVE_DIR/FAILED_{WAVE}.md"
    {{ echo "# FAILED — {WAVE} incomplete"; echo; echo "missing:$missing";
      echo "Generated $(date -u +%FT%TZ)"; }} > "$marker"
    git -C "$REPO_DIR" add -- "$marker"
    git -C "$REPO_DIR" "${{BOT[@]}}" commit -m "ercot-bot: FAILED marker ({WAVE})"
    push_with_retries
    exit 1
fi
echo "GATE PASS: {ntask}/{ntask}"
if [[ -f "$WAVE_DIR/FAILED_{WAVE}.md" ]]; then
    git -C "$REPO_DIR" rm -q -- "$WAVE_DIR/FAILED_{WAVE}.md" 2>/dev/null \\
        || rm -f "$WAVE_DIR/FAILED_{WAVE}.md"
    echo "stale FAILED marker cleared"
fi

EXTR="$ERCOT_DIR/extracts/{WAVE}"
mkdir -p "$EXTR"
for t in {tasks}; do
    OUT="$EXTR/task_$t"
{extract_cmd('"$WAVE_DIR/runs/run_index_$t"', '"$OUT"', "--full",
             f'"$WAVE_DIR"/{WAVE}_array.o*."$t"')}
    cp -f "$WAVE_DIR/runs/run_index_$t/run/runtimes.csv" "$OUT/runtimes.csv" \\
        || echo "WARNING: task $t has no Prescient runtimes.csv"
    # per-RUC-day Gurobi tolerance line (the identity check) + wall-clock stamps
    if [[ -n "$JOBLOG" ]]; then
        python "$ERCOT_DIR/analysis/gap_smoke/read_smoke.py" --joblog "$JOBLOG" \\
            --tolerance-out "$OUT/ruc_tolerance.csv"
        grep -h "SMOKE_GAP_TASK=\\|SMOKE_GAP_START\\|SMOKE_GAP_END" "$JOBLOG" > "$OUT/wallclock.txt" || true
    else
        echo "WARNING: task $t: no job log found — tolerance UNVERIFIED (read_smoke will say so)"
    fi
done
python "$ERCOT_DIR/analysis/gap_smoke/read_smoke.py" \\
    --extracts "$EXTR" --ref "$ERCOT_DIR/extracts/smoke_v2" \\
    --out "$ERCOT_DIR/analysis/gap_smoke"

git -C "$REPO_DIR" add -- "$EXTR" \\
    "$ERCOT_DIR/analysis/gap_smoke/GAP_SMOKE.md" \\
    "$ERCOT_DIR/analysis/gap_smoke/gap_smoke.csv" \\
    "$ERCOT_DIR/analysis/gap_smoke/gap_smoke_days.csv"
git -C "$REPO_DIR" "${{BOT[@]}}" commit -m "ercot-bot: {WAVE} extracts + GAP_SMOKE.md (prompt 58 T1)"
push_with_retries
echo "collect_{WAVE} done — Kay: read analysis/gap_smoke/GAP_SMOKE.md, then write waves/GAP_DECISION.json"
""")
    write(d / "submit_this.sh", f"""#!/bin/bash
# Prompt 58 T1 gap smoke — run ON CRC (Kay, by hand):
#   cd trial_0826/ercot/waves/{WAVE} && bash submit_this.sh
# {ntask} tasks x 4 slots; minutes of compute. Collector held on the array.
cd "$(dirname "${{BASH_SOURCE[0]}}")"
set -euo pipefail
REPO_DIR="$(cd ../../../.. && pwd)"
BRANCH="$(git -C "$REPO_DIR" branch --show-current)"
[[ "$BRANCH" == "ercot/tx123" ]] || {{ echo "ABORT: on '$BRANCH', expected ercot/tx123"; exit 1; }}
git -C "$REPO_DIR" pull --rebase --autostash origin ercot/tx123
[[ -f ../../{V2_DATA_REL}/gen.csv ]] || {{ echo "ABORT: v2 data dir missing"; exit 1; }}
[[ -f ../../extracts/smoke_v2/overall.csv ]] || {{ echo "ABORT: extracts/smoke_v2 (byte-identity reference) missing"; exit 1; }}
grep -q -- "--ruc_mipgap" ../../run_ercot_pcm.py || {{ echo "ABORT: run_ercot_pcm.py has no --ruc_mipgap (pull the prompt-58 commits)"; exit 1; }}
J=$(qsub -terse {WAVE}_array.sh | cut -d. -f1)
[[ "$J" =~ ^[0-9]+$ ]] || {{ echo "BAD ARRAY JID: $J"; exit 1; }}
C=$(qsub -terse -hold_jid "$J" -cwd -M {EMAIL} -m ea collect_{WAVE}.sh)
[[ "$C" =~ ^[0-9]+$ ]] || {{ echo "BAD COLLECTOR JID: $C"; exit 1; }}
echo "SUBMITTED {WAVE}: array=$J ({ntask} tasks x 4 slots) collector=$C"
qstat -u ylu28
""")
    return d


def main():
    d = build()
    print(f"built {d}: {len(TASKS)} tasks {TASKS}")


if __name__ == "__main__":
    main()
