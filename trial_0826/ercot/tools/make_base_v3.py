#!/usr/bin/env python3
"""Build `waves/base_v3/` — ONE full-year base run (no PEM, dict `{}`) under
solver identity v3 (NOT submitted; Kay submits on CRC).

Why: wave D and every later campaign run read identity v3 (gap 0.001 /
TL 1200) from waves/GAP_DECISION.json, but the only base run on disk
(extracts/base_2019_v2) is identity v2 (gap 0.01 / TL 120). The gap smoke
(analysis/gap_smoke/GAP_SMOKE.md, task 2 vs task 1, x 365/3) shows the
identity change alone moves total cost by about -$10.9M/yr, true
curtailment by about -68 GWh/yr and on/offs by about -1,950/yr. Every
delta-vs-base of a v3 run therefore needs a v3 base. One run suffices: the
instrument is deterministic and exact replicates are byte-identical.

Conventions copied from tools/make_wave_d.py: HEADER / SMOKE_GATE / ENV /
PUSH from make_v2_waves, the GAP_DECISION read block (refuse without the
file), BASE_V3_START/END date stamps, held collector (--full extract to
extracts/base_v3/run_index_1, runtimes.csv, wallclock.csv, identity.txt,
GAP_DECISION_used.json, pool_objectives.py --run-dir on CRC, slim tables +
json + manifest committed, *.csv.gz left in storage, 5-retry push, email on
the collector only), submit_this.sh with the asserts + cat GAP_DECISION +
literal `yes`. 1 task x 4 slots, -r n, -q long.
"""
import json
import sys
from pathlib import Path

import pandas as pd

ERCOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ERCOT / "tools"))
from make_v2_waves import (EMAIL, ENV, HEADER, PUSH, SMOKE_GATE, V2_DATA_REL,  # noqa: E402
                           extract_cmd, write)

WAVE = "base_v3"
BASE_TOKEN = "__BASE_REPLICATE__"       # waves/base_2019_v2/design_matrix.csv convention
START_DATE, NUM_DAYS = "01-01-2019", 365
BUILT = "2026-11-07"
FULL_EXTRACT_MB = 51
V2_BASE = "extracts/base_2019_v2/run_index_1"

COLS = ["index", "oat_site", "unit_type", "bus", "omega", "bid", "gen_pmax",
        "start_date", "num_days", "replicate_of"]


def design_rows():
    """One row: the base case. Same schema as waves/base_2019_v2 (row 1)."""
    return [{"index": 1, "oat_site": BASE_TOKEN, "unit_type": "", "bus": "", "omega": "",
             "bid": "", "gen_pmax": "", "start_date": START_DATE, "num_days": NUM_DAYS,
             "replicate_of": ""}]


def retrofit_dict(row):
    """Base case: no PEM anywhere -> the empty dict."""
    assert row["oat_site"] == BASE_TOKEN
    return {}


GAP_READ = """# --- identity from waves/GAP_DECISION.json (Kay, E-D6); refuse without it ---
GAP_FILE="$ERCOT_DIR/waves/GAP_DECISION.json"
if [[ ! -f "$GAP_FILE" ]]; then
    echo "no GAP_DECISION.json" > "$WAVE_DIR/FAILED_task_${SGE_TASK_ID}_no_gap_decision.md"
    echo "ABORT task $SGE_TASK_ID: $GAP_FILE absent — base_v3 runs only under a decided identity"; exit 1
fi
read -r RUC_MIPGAP RUC_TIME_LIMIT < <(python - "$GAP_FILE" <<'PY'
import json, sys
d = json.load(open(sys.argv[1]))
g, t = float(d["ruc_mipgap"]), float(d["ruc_time_limit"])
assert 0.0 <= g < 1.0 and t > 0, (g, t)
print(g, t)
PY
)
[[ -n "$RUC_MIPGAP" && -n "$RUC_TIME_LIMIT" ]] || { echo "ABORT: GAP_DECISION.json unreadable"; exit 1; }
echo "IDENTITY from GAP_DECISION.json: ruc_mipgap=$RUC_MIPGAP ruc_time_limit=$RUC_TIME_LIMIT ($(tr -d '\\n' < "$GAP_FILE"))"
"""

RUN = """python "$ERCOT_DIR/run_ercot_pcm.py" \\
    --data_dir "$DATA_DIR" \\
    --index "$INDEX" \\
    --num_days "$NUM_DAYS" \\
    --start_date "$START_DATE" \\
    --ruc_mipgap "$RUC_MIPGAP" \\
    --ruc_time_limit "$RUC_TIME_LIMIT" \\
    --ruc_threads 4 \\
    --output_directory "$OUT_PARENT/run" \\
    --retrofit_gen_dict "$(cat "$DICT")"
"""


def build(waves=ERCOT / "waves"):
    d = waves / WAVE
    rows = design_rows()
    n = len(rows)
    assert n == 1
    dm = pd.DataFrame(rows, columns=COLS)
    d.mkdir(parents=True, exist_ok=True)
    dm.to_csv(d / "design_matrix.csv", index=False)
    for r in rows:
        dct = retrofit_dict(r)
        assert dct == {}
        write(d / f"retrofit_gen_dict_{r['index']}.json", json.dumps(dct) + "\n", 0o644)
    write(d / f"{WAVE}_array.sh", f"""#!/bin/bash
#$ -N {WAVE}_array
#$ -q long
#$ -cwd
#$ -t 1-{n}
#$ -pe smp 4
#$ -r n
# {WAVE}: ONE full-year base run (no PEM, retrofit dict {{}}) on v2 costs under
# the solver identity in waves/GAP_DECISION.json (identity v3, Kay E-D6), read
# at run time below. The v3 reference for every delta-vs-base from wave D on.
{HEADER}{SMOKE_GATE}mkdir -p "$WAVE_DIR/runs"
{ENV}module load gurobi
{GAP_READ}
eval "$(python "$TRIAL_DIR/campaign/get_row.py" "$SGE_TASK_ID" "$WAVE_DIR/design_matrix.csv")"
OUT_PARENT="$WAVE_DIR/runs"
DICT="$WAVE_DIR/retrofit_gen_dict_${{SGE_TASK_ID}}.json"
echo "BASE_V3_TASK=$SGE_TASK_ID dict=$(tr -d '\\n ' < "$DICT")"
[[ "$(tr -d '\\n ' < "$DICT")" == "{{}}" ]] || {{ echo "ABORT: base dict is not {{}}"; exit 1; }}
echo "BASE_V3_START $(date -u +%FT%TZ) epoch=$(date +%s)"
{RUN}echo "BASE_V3_END $(date -u +%FT%TZ) epoch=$(date +%s)"
""")
    check = f"""for i in $(seq 1 {n}); do
    [[ -f "$WAVE_DIR/runs/run_index_$i/overall_simulation_output.csv" ]] || missing="$missing $i"
done"""
    ext = extract_cmd('"$WAVE_DIR/runs/run_index_$i"', '"$EXTR/run_index_$i"', "--full",
                      f'"$WAVE_DIR"/{WAVE}_array.o*."$i"')
    write(d / f"collect_{WAVE}.sh", f"""#!/bin/bash
#$ -N collect_{WAVE}
#$ -q long
#$ -cwd
#$ -r n
# Collector ({WAVE}): gate -> --full extract + runtimes.csv + wall-clock ->
# pool metrics (pool_objectives.py --run-dir, ON CRC under PCM_ERCOT) ->
# ercot-bot commit of the SLIM tables + pool_full_metrics.json + runtimes.csv
# + extract_manifest.json + identity.txt + GAP_DECISION_used.json; *.csv.gz
# stay uncommitted (trial_0826/ercot/.gitignore) in $GROUP storage. Email
# flags are applied by submit_this.sh on THIS job only.
{HEADER}{ENV}
{PUSH}
missing=""
{check}
if [[ -n "$missing" ]]; then
    marker="$WAVE_DIR/FAILED_{WAVE}.md"
    {{ echo "# FAILED — {WAVE} incomplete"; echo; echo "missing:$missing";
      echo "Generated $(date -u +%FT%TZ)"; }} > "$marker"
    git -C "$REPO_DIR" add -- "$marker"
    git -C "$REPO_DIR" "${{BOT[@]}}" commit -m "ercot-bot: FAILED marker ({WAVE})"
    push_with_retries
    exit 1
fi
echo "GATE PASS: {n}/{n}"
if [[ -f "$WAVE_DIR/FAILED_{WAVE}.md" ]]; then
    git -C "$REPO_DIR" rm -q -- "$WAVE_DIR/FAILED_{WAVE}.md" 2>/dev/null \\
        || rm -f "$WAVE_DIR/FAILED_{WAVE}.md"
    echo "stale FAILED marker cleared"
fi

EXTR="$ERCOT_DIR/extracts/{WAVE}"
mkdir -p "$EXTR"
cp -f "$ERCOT_DIR/waves/GAP_DECISION.json" "$EXTR/GAP_DECISION_used.json"
echo "task,start_epoch,end_epoch,wall_s" > "$EXTR/wallclock.csv"
for i in $(seq 1 {n}); do
{ext}
    cp -f "$WAVE_DIR/runs/run_index_$i/run/runtimes.csv" "$EXTR/run_index_$i/runtimes.csv" \\
        || echo "WARNING: row $i has no Prescient runtimes.csv"
    if [[ -n "$JOBLOG" ]]; then
        S=$(grep -h "BASE_V3_START" "$JOBLOG" | sed -n 's/.*epoch=\\([0-9]*\\).*/\\1/p' | head -1)
        E=$(grep -h "BASE_V3_END" "$JOBLOG" | sed -n 's/.*epoch=\\([0-9]*\\).*/\\1/p' | tail -1)
        echo "$i,${{S:-}},${{E:-}},$(( ${{E:-0}} - ${{S:-0}} ))" >> "$EXTR/wallclock.csv"
        grep -h "IDENTITY from GAP_DECISION.json" "$JOBLOG" > "$EXTR/run_index_$i/identity.txt" || true
    fi
    python "$ERCOT_DIR/pool_objectives.py" --run-dir "$EXTR/run_index_$i" \\
        --out "$EXTR/run_index_$i/pool_full_metrics.json"
done

# git policy: slim tables + pool_full_metrics.json + runtimes.csv + manifest +
# identity.txt + GAP_DECISION_used.json; *.csv.gz are ignored by
# trial_0826/ercot/.gitignore and asserted absent below.
git -C "$REPO_DIR" add -- "$EXTR"
if git -C "$REPO_DIR" diff --cached --name-only | grep -q '\\.csv\\.gz$'; then
    echo "ABORT: a *.csv.gz is staged — .gitignore line missing?"; git -C "$REPO_DIR" reset -q; exit 1
fi
git -C "$REPO_DIR" "${{BOT[@]}}" commit -m "ercot-bot: {WAVE} extracts (v3 base; slim + pool_full_metrics; gz left in storage)"
push_with_retries
echo "collect_{WAVE} done"
""")
    write(d / "submit_this.sh", f"""#!/bin/bash
# {WAVE} — run ON CRC (Kay, by hand) AFTER waves/GAP_DECISION.json exists:
#   cd trial_0826/ercot/waves/{WAVE} && bash submit_this.sh
# {n} task x 4 slots = {4 * n} slots; no -tc. Collector held on the array.
cd "$(dirname "${{BASH_SOURCE[0]}}")"
set -euo pipefail
W="$(cd .. && pwd)"
REPO_DIR="$(cd ../../../.. && pwd)"
BRANCH="$(git -C "$REPO_DIR" branch --show-current)"
[[ "$BRANCH" == "ercot/tx123" ]] || {{ echo "ABORT: on '$BRANCH', expected ercot/tx123"; exit 1; }}
git -C "$REPO_DIR" pull --rebase --autostash origin ercot/tx123
[[ -f "$W/GAP_DECISION.json" ]] || {{ echo "ABORT: waves/GAP_DECISION.json absent — decide E-D6 first (read analysis/gap_smoke/GAP_SMOKE.md)"; exit 1; }}
grep -Eq '"identity"[[:space:]]*:[[:space:]]*"v3"' "$W/GAP_DECISION.json" || {{ echo "ABORT: waves/GAP_DECISION.json is not identity v3 — {WAVE} is the v3 base"; exit 1; }}
[[ -f "$W/smoke_v2/SMOKE_PASS" ]] || {{ echo "ABORT: waves/smoke_v2/SMOKE_PASS absent — smoke gate not passed"; exit 1; }}
[[ -f "$W/../{V2_DATA_REL}/gen.csv" ]] || {{ echo "ABORT: v2 data dir missing"; exit 1; }}
[[ "$(tr -d '\\n ' < "$W/{WAVE}/retrofit_gen_dict_1.json")" == "{{}}" ]] || {{ echo "ABORT: retrofit_gen_dict_1.json is not {{}}"; exit 1; }}
grep -q -- "--ruc_mipgap" "$W/../run_ercot_pcm.py" || {{ echo "ABORT: run_ercot_pcm.py has no --ruc_mipgap"; exit 1; }}
grep -q "{WAVE}/\\*\\*/\\*.csv.gz" "$W/../.gitignore" || {{ echo "ABORT: trial_0826/ercot/.gitignore gz line missing"; exit 1; }}
echo "--- waves/GAP_DECISION.json (the identity {WAVE} will run under; eyeball it) ---"
cat "$W/GAP_DECISION.json"
echo "-----------------------------------------------------------------------------"
echo "--- qquota (need {4 * n} slots for {n} task x 4) ---"; qquota -u ylu28 || true
read -r -p "Submit {n} full-year base run (dict {{}}) under this identity? [yes/NO] " ANS
[[ "$ANS" == "yes" ]] || {{ echo "not submitted"; exit 1; }}
J=$(qsub -terse {WAVE}_array.sh | cut -d. -f1)
[[ "$J" =~ ^[0-9]+$ ]] || {{ echo "BAD ARRAY JID: $J"; exit 1; }}
C=$(qsub -terse -hold_jid "$J" -cwd -M {EMAIL} -m ea collect_{WAVE}.sh)
[[ "$C" =~ ^[0-9]+$ ]] || {{ echo "BAD COLLECTOR JID: $C"; exit 1; }}
echo "SUBMITTED {WAVE}: array=$J ({n} task x 4 slots) collector=$C"
qstat -u ylu28
""")
    write(d / "README.md", readme(rows), 0o644)
    return d, rows


def readme(rows):
    n = len(rows)
    return f"""# base_v3 — the full-year base run under identity v3 (built {BUILT}, NOT submitted)

Built by `tools/make_base_v3.py`. Kay submits ON CRC:

    cd trial_0826/ercot/waves/{WAVE} && bash submit_this.sh

`submit_this.sh` refuses without `waves/GAP_DECISION.json`, refuses unless
that file says identity v3, prints it, prints `qquota`, and asks for a
literal `yes` before `qsub`.

## 1. Why this run exists

Wave D (`waves/location_oat_v2`) and every later campaign run use solver
identity v3: `ruc_mipgap` 0.001, `ruc_time_limit` 1200 (`waves/GAP_DECISION.json`,
E-D6, Kay 2026-11-06). The only base run on disk (`{V2_BASE}`) uses identity
v2: `ruc_mipgap` 0.01, `ruc_time_limit` 120.

The gap smoke (`analysis/gap_smoke/GAP_SMOKE.md`, task 2 vs task 1, 3 days
scaled by 365/3) shows that the identity change alone moves the base case:

| quantity | 3-day delta | scaled to one year |
|---|---|---|
| total cost | -89,490 $ | about -$10.9M/yr |
| true curtailment | -556.6 MWh | about -68 GWh/yr |
| on/offs (starts) | -16 | about -1,950/yr |

These shifts are the size of a single-site PEM effect ($11.3M median,
`analysis/pool/POOL_V2.md` section 6.1). A delta computed as (v3 run) minus
(v2 base) mixes the PEM effect with the identity effect. Every delta-vs-base
of a v3 run must use a v3 base. This wave makes that base.

## 2. One run suffices

The instrument is deterministic. Exact replicates are byte-identical
(`waves/base_2019_v2` rows 2 and 3 equal row 1; `extracts/smoke_v2` equals
gap-smoke task 1). A second v3 base run would add no information. Do not add
replicates to this wave.

## 3. Row ({n})

| row | oat_site | dict | start | days |
|---|---|---|---|---|
| 1 | `{BASE_TOKEN}` | `{{}}` | {START_DATE} | {NUM_DAYS} |

`design_matrix.csv` uses the `waves/base_2019_v2` schema. `retrofit_gen_dict_1.json`
is the empty dict: no PEM at any site. The array script aborts if the dict is
not `{{}}`.

## 4. Identity gate

The array script reads `--ruc_mipgap` / `--ruc_time_limit` from
`waves/GAP_DECISION.json` at RUN time (the wave-D block, unchanged), prints
`IDENTITY from GAP_DECISION.json: ruc_mipgap=... ruc_time_limit=...` into the
task log, and refuses (FAILED marker) if the file is missing. It is also
SMOKE_GATEd on `waves/smoke_v2/SMOKE_PASS`. The collector copies the decision
used to `extracts/{WAVE}/GAP_DECISION_used.json` and the identity line to
`extracts/{WAVE}/run_index_1/identity.txt`. Read these two files before you
use this base in any delta.

## 5. Collector and the gz policy

`collect_{WAVE}.sh` (held on the array; email on this job only):
`extract_ercot.py --full` -> `extracts/{WAVE}/run_index_1/`, Prescient
`runtimes.csv` copied, wall-clock from the `BASE_V3_START` / `BASE_V3_END`
stamps -> `extracts/{WAVE}/wallclock.csv`, then ON CRC
`python pool_objectives.py --run-dir <extract> --out <extract>/pool_full_metrics.json`.
Git receives the SLIM tables + `pool_full_metrics.json` + `runtimes.csv` +
`extract_manifest.json` + `identity.txt` + `GAP_DECISION_used.json`. The four
`*.csv.gz` tables stay UNCOMMITTED (`trial_0826/ercot/.gitignore`:
`extracts/{WAVE}/**/*.csv.gz`; the collector aborts if a gz is staged) in
`$GROUP` storage, listed by name + md5 in `extract_manifest.json`.

Storage: {n} x {FULL_EXTRACT_MB} MB = {FULL_EXTRACT_MB} MB on CRC; about 3 MB in git.

## 6. The v2 base stays

`{V2_BASE}` remains the reference for the 31 identity-v2 runs
(screening_v2, screening_topup, selection_t1_v2, base_2019_v2). Do not
replace it. Do not compare a v2 run with the v3 base, or a v3 run with the
v2 base. Identity v3 runs are never pooled with v2 runs in any claim
(`CONFIG_ERCOT.md`, "Solver identity v3").

## 7. Expected wall-clock

One full-year row at 4 slots. Under v3 the smoke's per-day RUC solve time was
26 s median / 46 s max (`GAP_SMOKE.md`), so the year's RUC time is about 2.6 h
at the median; the v2 full-year base took about 18-27 h wall. Plan for one CRC
day. {n} task x 4 slots = {4 * n} slots, no `-tc`.

## 8. Local checks (zero simulation)

`bash -n` on the three scripts; `tests/test_make_base_v3.py` (one row, dict
`{{}}`, the array reads `GAP_DECISION.json` and refuses without it, `submit_this.sh`
refuses without it, `.gitignore` line, committed wave == fresh build).
"""


def main():
    d, rows = build()
    print(f"built {d}: {len(rows)} row (base, dict {{}}); identity from waves/GAP_DECISION.json at run time")
    print(f"storage: {len(rows)} x {FULL_EXTRACT_MB} MB on CRC; about 3 MB in git (gz left in storage)")


if __name__ == "__main__":
    main()
