#!/usr/bin/env python3
"""Prompt 36 T1/T2 — build the v2 (cost-fixed) CRC waves.

  waves/smoke_v2/         3-day smoke (01-01-2019 ×3, same window as v1 smoke_3d)
  waves/base_2019_v2/     A: 3 base solves (row 1 --full extract; 2–3 replicates)
  waves/screening_v2/     B: ercot/ (12 rows) + topup/ (7 rows), design matrices
                          and retrofit dicts copied BYTE-FOR-BYTE from v1;
                          one 19-task array (task 1–12 → ercot/, 13–19 → topup/)
  waves/selection_t1_v2/  C: selection_t1 rows 3–11 (rows 1–2 = base replicates,
                          now in A); matrix lines + dicts byte-identical; -t 3-11
  waves/submit_v2/submit_this.sh   ONE submission of A + B + C, gated on SMOKE_PASS

Every job: --data_dir data/ercot123_2019_v2, TL=120, Threads=4, -pe smp 4,
-r n, no -tc, PYTHONNOUSERSITE=1, mkdir -p of every output parent.
B and C rows are "carried over from v1 selection" — not v2 choices
(make_screening_topup.py is NOT re-run: it ranks from v1 extracts).
"""
import hashlib
import shutil
from pathlib import Path

ERCOT = Path(__file__).resolve().parents[1]
WAVES = ERCOT / "waves"
V2_DATA_REL = "data/ercot123_2019_v2"
EMAIL = "ylu28@nd.edu"

HEADER = """set -euo pipefail
WAVE_DIR="$PWD"   # -cwd: submitted from inside the wave dir (submit_this.sh cd's there)
ERCOT_DIR="$(cd "$WAVE_DIR/../.." && pwd)"
TRIAL_DIR="$(cd "$ERCOT_DIR/.." && pwd)"
REPO_DIR="$(cd "$TRIAL_DIR/.." && pwd)"
DATA_DIR="$ERCOT_DIR/%s"
""" % V2_DATA_REL

ENV = """source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate PCM_ERCOT
export PYTHONNOUSERSITE=1
"""

PUSH = """BOT=(-c user.name="ercot-bot" -c user.email="ercot-bot@noreply.github.com")
push_with_retries() {
    local attempt
    for attempt in 1 2 3 4 5; do
        if git -C "$REPO_DIR" push origin ercot/tx123; then return 0; fi
        echo "push rejected (attempt $attempt/5) — rebase and retry"
        sleep $((30 + RANDOM % 60))
        git -C "$REPO_DIR" pull --rebase --autostash origin ercot/tx123
    done
    git -C "$REPO_DIR" push origin ercot/tx123 || { git -C "$REPO_DIR" status; exit 1; }
}
"""

SMOKE_GATE = """SMOKE="$ERCOT_DIR/waves/smoke_v2/SMOKE_PASS"
if [[ ! -f "$SMOKE" ]]; then
    echo "no SMOKE_PASS" > "$WAVE_DIR/FAILED_task_${SGE_TASK_ID}_no_smoke.md"
    echo "ABORT task $SGE_TASK_ID: $SMOKE absent"; exit 1
fi
"""

RUN = """python "$ERCOT_DIR/run_ercot_pcm.py" \\
    --data_dir "$DATA_DIR" \\
    --index "$INDEX" \\
    --num_days "$NUM_DAYS" \\
    --start_date "$START_DATE" \\
    --ruc_time_limit 120 \\
    --ruc_threads 4 \\
    --output_directory "$OUT_PARENT/run" \\
    --retrofit_gen_dict "$(cat "$DICT")"
"""


def write(path, text, mode=0o755):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    path.chmod(mode)


def copy_exact(src, dst):
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dst)
    assert hashlib.md5(src.read_bytes()).digest() == hashlib.md5(dst.read_bytes()).digest()


def collector(name, n_label, check_loop, extract_loop, extra="", add_paths=""):
    return f"""#!/bin/bash
#$ -N collect_{name}
#$ -q long
#$ -cwd
#$ -r n
# Prompt 36 collector ({name}): gate -> extracts (--data_dir v2) -> {('objectives -> ' if extra else '')}ercot-bot
# commit + 5-retry push. Clears a stale FAILED marker on success. Email flags
# are applied by submit_this.sh on THIS job only.
{HEADER}{ENV}
{PUSH}
missing=""
{check_loop}
if [[ -n "$missing" ]]; then
    marker="$WAVE_DIR/FAILED_{name}.md"
    {{ echo "# FAILED — {name} incomplete"; echo; echo "missing:$missing";
      echo "Generated $(date -u +%FT%TZ)"; }} > "$marker"
    git -C "$REPO_DIR" add -- "$marker"
    git -C "$REPO_DIR" "${{BOT[@]}}" commit -m "ercot-bot: FAILED marker ({name})"
    push_with_retries
    exit 1
fi
echo "GATE PASS: {n_label}"
if [[ -f "$WAVE_DIR/FAILED_{name}.md" ]]; then
    git -C "$REPO_DIR" rm -q -- "$WAVE_DIR/FAILED_{name}.md" 2>/dev/null \\
        || rm -f "$WAVE_DIR/FAILED_{name}.md"
    echo "stale FAILED marker cleared"
fi

{extract_loop}
{extra}
git -C "$REPO_DIR" add -- "$ERCOT_DIR/extracts/{name}"{add_paths}
git -C "$REPO_DIR" "${{BOT[@]}}" commit -m "ercot-bot: {name} extracts (v2 costs)"
push_with_retries
echo "collect_{name} done"
"""


def extract_cmd(run_dir, out_dir, full, joblog_glob):
    return f"""    JOBLOG=$(ls -t {joblog_glob} 2>/dev/null | head -1 || true)
    python "$ERCOT_DIR/extract_ercot.py" --data_dir "$DATA_DIR" \\
        {run_dir} \\
        {out_dir} {full} \\
        ${{JOBLOG:+--joblog "$JOBLOG"}}"""


def build_smoke():
    d = WAVES / "smoke_v2"
    write(d / "smoke_v2_job.sh", f"""#!/bin/bash
#$ -N smoke_v2
#$ -q long
#$ -cwd
#$ -pe smp 4
#$ -r n
# Prompt 36 smoke on v2 costs: 3 days from 01-01-2019 (same window as the v1
# smoke_3d), base (no PEM), frozen solver config. SMOKE_PASS is NOT written
# here: the gate also needs the authors'-SCUC side-by-side, which runs locally
# (analysis/cost_fix/smoke_gate.py writes waves/smoke_v2/SMOKE_PASS).
{HEADER}{ENV}module load gurobi

mkdir -p "$WAVE_DIR/runs"   # prescient reporting uses os.mkdir — parent must exist
INDEX=smoke NUM_DAYS=3 START_DATE=01-01-2019 OUT_PARENT="$WAVE_DIR/runs"
DICT="$WAVE_DIR/retrofit_gen_dict_smoke.json"
{RUN}""")
    write(d / "retrofit_gen_dict_smoke.json", "{}\n", 0o644)
    check = """[[ -f "$WAVE_DIR/runs/run_index_smoke/overall_simulation_output.csv" ]] || missing=" smoke\""""
    ext = extract_cmd('"$WAVE_DIR/runs/run_index_smoke"', '"$ERCOT_DIR/extracts/smoke_v2"',
                      "--full", '"$WAVE_DIR"/smoke_v2.o*').replace("    ", "", 1)
    write(d / "collect_smoke_v2.sh", collector("smoke_v2", "1/1", check, ext))
    write(d / "submit_this.sh", f"""#!/bin/bash
# Prompt 36 smoke — run ON CRC (Kay, by hand):  bash submit_this.sh
cd "$(dirname "${{BASH_SOURCE[0]}}")"
set -euo pipefail
REPO_DIR="$(cd ../../../.. && pwd)"
BRANCH="$(git -C "$REPO_DIR" branch --show-current)"
[[ "$BRANCH" == "ercot/tx123" ]] || {{ echo "ABORT: on '$BRANCH', expected ercot/tx123"; exit 1; }}
git -C "$REPO_DIR" pull --rebase --autostash origin ercot/tx123
[[ -f ../../{V2_DATA_REL}/gen.csv ]] || {{ echo "ABORT: v2 data dir missing"; exit 1; }}
J=$(qsub -terse smoke_v2_job.sh | cut -d. -f1)
[[ "$J" =~ ^[0-9]+$ ]] || {{ echo "BAD SMOKE JID: $J"; exit 1; }}
C=$(qsub -terse -hold_jid "$J" -cwd -M {EMAIL} -m ea collect_smoke_v2.sh)
[[ "$C" =~ ^[0-9]+$ ]] || {{ echo "BAD COLLECTOR JID: $C"; exit 1; }}
echo "SUBMITTED smoke_v2: job=$J collector=$C (1 task, 4 slots)"
qstat -u ylu28
""")


def build_base():
    d = WAVES / "base_2019_v2"
    lines = ["index,oat_site,unit_type,bus,omega,bid,gen_pmax,start_date,num_days,replicate_of",
             "1,__BASE_REPLICATE__,,,,,,01-01-2019,365,",
             "2,__BASE_REPLICATE__,,,,,,01-01-2019,365,base_2019_v2:1",
             "3,__BASE_REPLICATE__,,,,,,01-01-2019,365,base_2019_v2:1"]
    write(d / "design_matrix.csv", "\n".join(lines) + "\n", 0o644)
    for i in (1, 2, 3):
        write(d / f"retrofit_gen_dict_{i}.json", "{}\n", 0o644)
    write(d / "base_2019_v2_array.sh", f"""#!/bin/bash
#$ -N base_2019_v2_array
#$ -q long
#$ -cwd
#$ -t 1-3
#$ -pe smp 4
#$ -r n
# Prompt 36 wave A: 3 full-year base solves on v2 costs (row 1 = reference,
# 2–3 replicates). Frozen solver config (TL=120, Threads=4).
{HEADER}{SMOKE_GATE}mkdir -p "$WAVE_DIR/runs"
{ENV}module load gurobi

eval "$(python "$TRIAL_DIR/campaign/get_row.py" "$SGE_TASK_ID" "$WAVE_DIR/design_matrix.csv")"
OUT_PARENT="$WAVE_DIR/runs"
DICT="$WAVE_DIR/retrofit_gen_dict_${{SGE_TASK_ID}}.json"
{RUN}""")
    check = """for i in 1 2 3; do
    [[ -f "$WAVE_DIR/runs/run_index_$i/overall_simulation_output.csv" ]] || missing="$missing $i"
done"""
    ext = ("for i in 1 2 3; do\n    FULL=\"\"\n    [[ \"$i\" == 1 ]] && FULL=\"--full\"   # only row 1's full extract is committed\n"
           + extract_cmd('"$WAVE_DIR/runs/run_index_$i"', '"$ERCOT_DIR/extracts/base_2019_v2/run_index_$i"',
                         "$FULL", '"$WAVE_DIR"/base_2019_v2_array.o*."$i"') + "\ndone")
    write(d / "collect_base_2019_v2.sh", collector("base_2019_v2", "3/3", check, ext))


def build_screening():
    d = WAVES / "screening_v2"
    for sub, src in (("ercot", "screening_ercot"), ("topup", "screening_topup")):
        s = WAVES / src
        copy_exact(s / "design_matrix.csv", d / sub / "design_matrix.csv")
        for f in sorted(s.glob("retrofit_gen_dict_*.json")):
            copy_exact(f, d / sub / f.name)
    (d / "CARRIED_OVER.md").write_text(
        "# screening_v2 — rows carried over from v1 selection\n\n"
        "`ercot/` = `waves/screening_ercot` (12 rows) and `topup/` = `waves/screening_topup`\n"
        "(7 rows), design matrices and retrofit dicts copied BYTE-FOR-BYTE (md5-asserted by\n"
        "`tools/make_v2_waves.py`). The slate was chosen from v1 (mis-costed) extracts; these\n"
        "rows are carried over from v1 selection, NOT v2 choices. `make_screening_topup.py`\n"
        "was not re-run. `replicate_of` values refer to rows of the same sub-matrix\n"
        "(`ercot/` row 11 = base replicate, row 12 = replicate of row 1).\n\n"
        "Task map: SGE task 1–12 → `ercot/` row = task; 13–19 → `topup/` row = task − 12.\n"
        "Runs: `runs/<sub>/run_index_<row>`; extracts: `extracts/screening_v2/<sub>/run_index_<row>`.\n")
    write(d / "screening_v2_array.sh", f"""#!/bin/bash
#$ -N screening_v2_array
#$ -q long
#$ -cwd
#$ -t 1-19
#$ -pe smp 4
#$ -r n
# Prompt 36 wave B: v1 screening slates (12 + 7, byte-identical) on v2 costs.
{HEADER}{SMOKE_GATE}if [[ "$SGE_TASK_ID" -le 12 ]]; then SUB=ercot; ROW=$SGE_TASK_ID
else SUB=topup; ROW=$((SGE_TASK_ID - 12)); fi
mkdir -p "$WAVE_DIR/runs/$SUB"
{ENV}module load gurobi

eval "$(python "$TRIAL_DIR/campaign/get_row.py" "$ROW" "$WAVE_DIR/$SUB/design_matrix.csv")"
OUT_PARENT="$WAVE_DIR/runs/$SUB"
DICT="$WAVE_DIR/$SUB/retrofit_gen_dict_${{ROW}}.json"
echo "task $SGE_TASK_ID -> $SUB row $ROW"
{RUN}""")
    check = """for t in $(seq 1 19); do
    if [[ "$t" -le 12 ]]; then SUB=ercot; ROW=$t; else SUB=topup; ROW=$((t - 12)); fi
    [[ -f "$WAVE_DIR/runs/$SUB/run_index_$ROW/overall_simulation_output.csv" ]] || missing="$missing $SUB:$ROW"
done"""
    ext = ("for t in $(seq 1 19); do\n"
           "    if [[ \"$t\" -le 12 ]]; then SUB=ercot; ROW=$t; else SUB=topup; ROW=$((t - 12)); fi\n"
           + extract_cmd('"$WAVE_DIR/runs/$SUB/run_index_$ROW"',
                         '"$ERCOT_DIR/extracts/screening_v2/$SUB/run_index_$ROW"', "",
                         '"$WAVE_DIR"/screening_v2_array.o*."$t"') + "\ndone")
    write(d / "collect_screening_v2.sh", collector("screening_v2", "19/19", check, ext))


def build_selection():
    d = WAVES / "selection_t1_v2"
    s = WAVES / "selection_t1"
    src_lines = (s / "design_matrix.csv").read_text().split("\n")
    kept = [src_lines[0]] + [l for l in src_lines[1:] if l and int(l.split(",")[0]) >= 3]
    assert len(kept) == 10 and all(l in src_lines for l in kept)
    write(d / "design_matrix.csv", "\n".join(kept) + "\n", 0o644)
    for i in range(3, 12):
        copy_exact(s / f"retrofit_gen_dict_{i}.json", d / f"retrofit_gen_dict_{i}.json")
    (d / "CARRIED_OVER.md").write_text(
        "# selection_t1_v2 — rows carried over from v1 selection\n\n"
        "`waves/selection_t1` rows 3–11 (rows 1–2 were base replicates; on v2 they are\n"
        "wave A `base_2019_v2`). Matrix lines and retrofit dicts are byte-identical to v1;\n"
        "the array runs `-t 3-11` so indices keep their v1 meaning. Carried over from v1\n"
        "selection, NOT v2 choices.\n\n"
        "Rows 6–11 (site 1, NUC) measure FORMULATION A: the multi_pem thermal patch\n"
        "replaces gen-1's p_cost with the PEM bid and forces u ≡ 1 (needs fix `1eaf05e`).\n"
        "gen-1's own v2 behaviour comes ONLY from wave A and non-retrofit rows.\n")
    write(d / "selection_t1_v2_array.sh", f"""#!/bin/bash
#$ -N selection_t1_v2_array
#$ -q long
#$ -cwd
#$ -t 3-11
#$ -pe smp 4
#$ -r n
# Prompt 36 wave C: selection_t1 rows 3–11 on v2 costs (needs fix 1eaf05e).
{HEADER}{SMOKE_GATE}mkdir -p "$WAVE_DIR/runs"
{ENV}module load gurobi

eval "$(python "$TRIAL_DIR/campaign/get_row.py" "$SGE_TASK_ID" "$WAVE_DIR/design_matrix.csv")"
OUT_PARENT="$WAVE_DIR/runs"
DICT="$WAVE_DIR/retrofit_gen_dict_${{SGE_TASK_ID}}.json"
{RUN}""")
    check = """for i in $(seq 3 11); do
    [[ -f "$WAVE_DIR/runs/run_index_$i/overall_simulation_output.csv" ]] || missing="$missing $i"
done"""
    ext = ("for i in $(seq 3 11); do\n"
           + extract_cmd('"$WAVE_DIR/runs/run_index_$i"',
                         '"$ERCOT_DIR/extracts/selection_t1_v2/run_index_$i"', "",
                         '"$WAVE_DIR"/selection_t1_v2_array.o*."$i"') + "\ndone")
    extra = ('# objectives need A + B extracts: submit_this.sh holds this collector on\n'
             '# collect_base_2019_v2 and collect_screening_v2 as well as this array.\n'
             'python "$ERCOT_DIR/compute_objectives.py" --suffix _v2\n')
    add = (' \\\n    "$ERCOT_DIR/analysis/selection/objectives_t1_v2.csv" \\\n'
           '    "$ERCOT_DIR/analysis/selection/noise_ruler_v2_v2.json"')
    write(d / "collect_selection_t1_v2.sh",
          collector("selection_t1_v2", "9/9", check, ext, extra=extra, add_paths=add))


def build_submit():
    write(WAVES / "submit_v2" / "submit_this.sh", f"""#!/bin/bash
# Prompt 36 T2 — ONE submission of waves A + B + C on v2 costs.
# Run ON CRC (Kay, by hand) after SMOKE_PASS is committed:  bash submit_this.sh
# 31 tasks × 4 slots = 124 slots; no -tc.
cd "$(dirname "${{BASH_SOURCE[0]}}")"
set -euo pipefail
W="$(cd .. && pwd)"
REPO_DIR="$(cd ../../../.. && pwd)"
BRANCH="$(git -C "$REPO_DIR" branch --show-current)"
[[ "$BRANCH" == "ercot/tx123" ]] || {{ echo "ABORT: on '$BRANCH', expected ercot/tx123"; exit 1; }}
git -C "$REPO_DIR" pull --rebase --autostash origin ercot/tx123
[[ -f "$W/smoke_v2/SMOKE_PASS" ]] || {{ echo "ABORT: waves/smoke_v2/SMOKE_PASS absent — smoke gate not passed"; exit 1; }}
[[ -f "$W/../data/ercot123_2019_v2/gen.csv" ]] || {{ echo "ABORT: v2 data dir missing"; exit 1; }}
git -C "$REPO_DIR" merge-base --is-ancestor 1eaf05e HEAD || {{ echo "ABORT: fix 1eaf05e not in HEAD (wave C)"; exit 1; }}
echo "--- qquota (need 124 slots for 31 tasks x 4) ---"; qquota -u ylu28 || true

sub() {{ local d=$1; shift; (cd "$W/$d" && qsub -terse "$@" | cut -d. -f1); }}
chk() {{ [[ "$2" =~ ^[0-9]+$ ]] || {{ echo "BAD JID for $1: $2"; exit 1; }}; }}

JA=$(sub base_2019_v2 base_2019_v2_array.sh);              chk A_array "$JA"
JB=$(sub screening_v2 screening_v2_array.sh);              chk B_array "$JB"
JC=$(sub selection_t1_v2 selection_t1_v2_array.sh);        chk C_array "$JC"
CA=$(sub base_2019_v2 -hold_jid "$JA" -cwd -M {EMAIL} -m ea collect_base_2019_v2.sh);   chk A_coll "$CA"
CB=$(sub screening_v2 -hold_jid "$JB" -cwd -M {EMAIL} -m ea collect_screening_v2.sh);   chk B_coll "$CB"
CC=$(sub selection_t1_v2 -hold_jid "$JC,$CA,$CB" -cwd -M {EMAIL} -m ea collect_selection_t1_v2.sh); chk C_coll "$CC"
echo "SUBMITTED v2 A+B+C: A array=$JA (3) B array=$JB (19) C array=$JC (9) | collectors A=$CA B=$CB C=$CC"
qstat -u ylu28
""")


def main():
    build_smoke()
    build_base()
    build_screening()
    build_selection()
    build_submit()
    print("built waves: smoke_v2, base_2019_v2 (3), screening_v2 (12+7), "
          "selection_t1_v2 (rows 3-11), submit_v2/submit_this.sh")


if __name__ == "__main__":
    main()
