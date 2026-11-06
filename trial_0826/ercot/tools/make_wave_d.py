#!/usr/bin/env python3
"""Prompt 58 T2 — build wave D `waves/location_oat_v2/` (21 rows; NOT submitted).

Rows (pinned order, prompt 58 section 3 / WAVE_D_TOPK_RULE.md): VRE sites
163, 140, 146, 270, 110, 274 (all WIND) x levels 60 / 120 / 180 MW -> rows
1-18; nuclear gen 1 (formulation A: thermal patch, fix 7c5fb8d) x 60 / 120 /
180 MW -> rows 19-21. PEM_fraction = pem_mw / gen_pmax (renewable, nameplate
from data/ercot123_2019_v2/gen.csv) or pem_mw / 2430.0 (nuclear). Builder
asserts: max level <= min chosen nameplate (185.4, site 163; the egret
renewable patch clamps silently above nameplate) and every fraction <= 1.

The array script reads --ruc_mipgap / --ruc_time_limit from
waves/GAP_DECISION.json at RUN time and refuses if it is missing; it is also
SMOKE_GATEd on waves/smoke_v2/SMOKE_PASS. submit_this.sh refuses without
GAP_DECISION.json and prints it for Kay to eyeball before qsub.

Collector: every row --full -> extracts/location_oat_v2/run_index_N/, plus
Prescient runtimes.csv and the wall-clock stamps; per-run pool metrics
(pool_objectives.py --run-dir) on CRC; git adds the slim tables +
pool_full_metrics.json + runtimes.csv + extract_manifest.json and leaves
*.csv.gz uncommitted (trial_0826/ercot/.gitignore; the gz files stay in
$GROUP storage, listed by name + md5 in each extract_manifest.json).
"""
import json
import sys
from pathlib import Path

import pandas as pd

ERCOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ERCOT / "tools"))
from make_v2_waves import (EMAIL, ENV, HEADER, PUSH, SMOKE_GATE, V2_DATA_REL,  # noqa: E402
                           extract_cmd, write)

WAVE = "location_oat_v2"
SITES = ["163", "140", "146", "270", "110", "274"]      # pinned order
LEVELS_MW = [60.0, 120.0, 180.0]
NUC_SITE, NUC_BUS, NUC_PMAX = "1", 107, 2430.0
BID = 40.0
START_DATE, NUM_DAYS = "01-01-2019", 365
T0_FIX = "7c5fb8d"
FULL_EXTRACT_MB = 51


def nameplates(data_dir=ERCOT / V2_DATA_REL):
    g = pd.read_csv(data_dir / "gen.csv", dtype={"GEN UID": str})
    g = g.set_index("GEN UID")
    return {s: (float(g.loc[s, "PMax MW"]), int(g.loc[s, "Bus ID"]), str(g.loc[s, "Unit Type"]))
            for s in SITES}


def design_rows(levels=LEVELS_MW, sites=SITES, data_dir=ERCOT / V2_DATA_REL):
    """21 dict rows in the pinned order; asserts of prompt 58 section 3."""
    npl = nameplates(data_dir)
    min_npl = min(v[0] for v in npl.values())
    assert max(levels) <= min_npl, (
        f"max level {max(levels)} MW > min chosen nameplate {min_npl:.1f} MW "
        f"(the renewable patch clamps silently above nameplate)")
    rows = []
    idx = 0
    for s in sites:
        pmax, bus, ut = npl[s]
        assert ut == "WIND", (s, ut)
        for lv in levels:
            idx += 1
            omega = lv / pmax
            assert omega <= 1.0, (s, lv, omega)
            rows.append({"index": idx, "oat_site": s, "unit_type": ut, "bus": bus,
                         "omega": omega, "bid": BID, "gen_pmax": pmax,
                         "start_date": START_DATE, "num_days": NUM_DAYS, "replicate_of": "",
                         "pem_mw": lv, "level_id": f"L{int(lv)}"})
    for lv in levels:
        idx += 1
        omega = lv / NUC_PMAX
        assert omega <= 1.0
        rows.append({"index": idx, "oat_site": NUC_SITE, "unit_type": "NUC", "bus": NUC_BUS,
                     "omega": omega, "bid": BID, "gen_pmax": NUC_PMAX,
                     "start_date": START_DATE, "num_days": NUM_DAYS, "replicate_of": "",
                     "pem_mw": lv, "level_id": f"L{int(lv)}"})
    assert len(rows) == len(sites) * len(levels) + len(levels)
    return rows


def retrofit_dict(row):
    """Renewable: {site: {PEM_bid, PEM_fraction, gen_pmax}}; nuclear: no gen_pmax
    (waves/selection_t1_v2/retrofit_gen_dict_6.json convention)."""
    d = {"PEM_bid": BID, "PEM_fraction": row["omega"]}
    if row["unit_type"] != "NUC":
        d["gen_pmax"] = row["gen_pmax"]
    return {row["oat_site"]: d}


COLS = ["index", "oat_site", "unit_type", "bus", "omega", "bid", "gen_pmax",
        "start_date", "num_days", "replicate_of", "pem_mw", "level_id"]

GAP_READ = """# --- identity from waves/GAP_DECISION.json (Kay, E-D6); refuse without it ---
GAP_FILE="$ERCOT_DIR/waves/GAP_DECISION.json"
if [[ ! -f "$GAP_FILE" ]]; then
    echo "no GAP_DECISION.json" > "$WAVE_DIR/FAILED_task_${SGE_TASK_ID}_no_gap_decision.md"
    echo "ABORT task $SGE_TASK_ID: $GAP_FILE absent — wave D runs only under a decided identity"; exit 1
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

RUN_D = """python "$ERCOT_DIR/run_ercot_pcm.py" \\
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


def build(waves=ERCOT / "waves", data_dir=ERCOT / V2_DATA_REL, levels=LEVELS_MW):
    d = waves / WAVE
    rows = design_rows(levels, data_dir=data_dir)
    n = len(rows)
    dm = pd.DataFrame(rows, columns=COLS)
    d.mkdir(parents=True, exist_ok=True)
    dm.to_csv(d / "design_matrix.csv", index=False)   # repr floats: 40.0, 2430.0, full omega
    for r in rows:
        write(d / f"retrofit_gen_dict_{r['index']}.json",
              json.dumps(retrofit_dict(r), indent=2) + "\n", 0o644)
    write(d / f"{WAVE}_array.sh", f"""#!/bin/bash
#$ -N {WAVE}_array
#$ -q long
#$ -cwd
#$ -t 1-{n}
#$ -pe smp 4
#$ -r n
# Prompt 58 T2 wave D ({WAVE}): {n} full-year rows on v2 costs
# (6 WIND sites x 60/120/180 MW + nuclear gen 1 x 60/120/180 MW, formulation A,
# fix {T0_FIX}). GP training data (prompt 53): runs ONLY under the identity in
# waves/GAP_DECISION.json (Kay, E-D6), read at run time below.
{HEADER}{SMOKE_GATE}mkdir -p "$WAVE_DIR/runs"
{ENV}module load gurobi
{GAP_READ}
eval "$(python "$TRIAL_DIR/campaign/get_row.py" "$SGE_TASK_ID" "$WAVE_DIR/design_matrix.csv")"
OUT_PARENT="$WAVE_DIR/runs"
DICT="$WAVE_DIR/retrofit_gen_dict_${{SGE_TASK_ID}}.json"
echo "WAVE_D_TASK=$SGE_TASK_ID dict=$(tr -d '\\n ' < "$DICT")"
echo "WAVE_D_START $(date -u +%FT%TZ) epoch=$(date +%s)"
{RUN_D}echo "WAVE_D_END $(date -u +%FT%TZ) epoch=$(date +%s)"
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
# Prompt 58 T2 collector ({WAVE}): gate -> --full extracts (every row) +
# runtimes.csv + wall-clock -> per-run pool metrics (pool_objectives.py
# --run-dir, ON CRC under PCM_ERCOT) -> ercot-bot commit of the SLIM tables +
# pool_full_metrics.json + runtimes.csv + extract_manifest.json; *.csv.gz
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
        S=$(grep -h "WAVE_D_START" "$JOBLOG" | sed -n 's/.*epoch=\\([0-9]*\\).*/\\1/p' | head -1)
        E=$(grep -h "WAVE_D_END" "$JOBLOG" | sed -n 's/.*epoch=\\([0-9]*\\).*/\\1/p' | tail -1)
        echo "$i,${{S:-}},${{E:-}},$(( ${{E:-0}} - ${{S:-0}} ))" >> "$EXTR/wallclock.csv"
        grep -h "IDENTITY from GAP_DECISION.json" "$JOBLOG" > "$EXTR/run_index_$i/identity.txt" || true
    fi
    python "$ERCOT_DIR/pool_objectives.py" --run-dir "$EXTR/run_index_$i" \\
        --out "$EXTR/run_index_$i/pool_full_metrics.json"
done

# git policy: slim tables + pool_full_metrics.json + runtimes.csv + manifest;
# *.csv.gz are ignored by trial_0826/ercot/.gitignore and asserted absent below.
git -C "$REPO_DIR" add -- "$EXTR"
if git -C "$REPO_DIR" diff --cached --name-only | grep -q '\\.csv\\.gz$'; then
    echo "ABORT: a *.csv.gz is staged — .gitignore line missing?"; git -C "$REPO_DIR" reset -q; exit 1
fi
git -C "$REPO_DIR" "${{BOT[@]}}" commit -m "ercot-bot: {WAVE} extracts (slim + pool_full_metrics; gz left in storage)"
push_with_retries
echo "collect_{WAVE} done"
""")
    write(d / "submit_this.sh", f"""#!/bin/bash
# Prompt 58 T2 wave D — run ON CRC (Kay, by hand) AFTER waves/GAP_DECISION.json
# exists:   cd trial_0826/ercot/waves/{WAVE} && bash submit_this.sh
# {n} tasks x 4 slots = {4 * n} slots; no -tc. Collector held on the array.
cd "$(dirname "${{BASH_SOURCE[0]}}")"
set -euo pipefail
W="$(cd .. && pwd)"
REPO_DIR="$(cd ../../../.. && pwd)"
BRANCH="$(git -C "$REPO_DIR" branch --show-current)"
[[ "$BRANCH" == "ercot/tx123" ]] || {{ echo "ABORT: on '$BRANCH', expected ercot/tx123"; exit 1; }}
git -C "$REPO_DIR" pull --rebase --autostash origin ercot/tx123
[[ -f "$W/GAP_DECISION.json" ]] || {{ echo "ABORT: waves/GAP_DECISION.json absent — decide E-D6 first (read analysis/gap_smoke/GAP_SMOKE.md)"; exit 1; }}
[[ -f "$W/smoke_v2/SMOKE_PASS" ]] || {{ echo "ABORT: waves/smoke_v2/SMOKE_PASS absent — smoke gate not passed"; exit 1; }}
[[ -f "$W/../{V2_DATA_REL}/gen.csv" ]] || {{ echo "ABORT: v2 data dir missing"; exit 1; }}
git -C "$REPO_DIR" merge-base --is-ancestor {T0_FIX} HEAD || {{ echo "ABORT: fix {T0_FIX} not in HEAD (nuclear rows)"; exit 1; }}
grep -q -- "--ruc_mipgap" "$W/../run_ercot_pcm.py" || {{ echo "ABORT: run_ercot_pcm.py has no --ruc_mipgap"; exit 1; }}
grep -q "location_oat_v2/\\*\\*/\\*.csv.gz" "$W/../.gitignore" || {{ echo "ABORT: trial_0826/ercot/.gitignore gz line missing"; exit 1; }}
echo "--- waves/GAP_DECISION.json (the identity wave D will run under; eyeball it) ---"
cat "$W/GAP_DECISION.json"
echo "-----------------------------------------------------------------------------"
echo "--- qquota (need {4 * n} slots for {n} tasks x 4) ---"; qquota -u ylu28 || true
read -r -p "Submit {n} full-year rows under this identity? [yes/NO] " ANS
[[ "$ANS" == "yes" ]] || {{ echo "not submitted"; exit 1; }}
J=$(qsub -terse {WAVE}_array.sh | cut -d. -f1)
[[ "$J" =~ ^[0-9]+$ ]] || {{ echo "BAD ARRAY JID: $J"; exit 1; }}
C=$(qsub -terse -hold_jid "$J" -cwd -M {EMAIL} -m ea collect_{WAVE}.sh)
[[ "$C" =~ ^[0-9]+$ ]] || {{ echo "BAD COLLECTOR JID: $C"; exit 1; }}
echo "SUBMITTED {WAVE}: array=$J ({n} tasks x 4 slots) collector=$C"
qstat -u ylu28
""")
    write(d / "README.md", readme(rows), 0o644)
    return d, rows


def readme(rows):
    n = len(rows)
    tab = ["| row | site | type | bus | level | PEM MW | nameplate MW | PEM_fraction |",
           "|---|---|---|---|---|---|---|---|"]
    for r in rows:
        tab.append(f"| {r['index']} | {r['oat_site']} | {r['unit_type']} | {r['bus']} | {r['level_id']} | "
                   f"{r['pem_mw']:.0f} | {r['gen_pmax']:.1f} | {r['omega']:.5f} |")
    nuc = [r for r in rows if r["unit_type"] == "NUC"]
    nuc_w = " / ".join(f"{r['omega']:.5f}" for r in nuc)
    return f"""# location_oat_v2 — wave D (prompt 58 T2; built 2026-11-06, NOT submitted)

Built by `tools/make_wave_d.py`. Kay submits ON CRC, AFTER `waves/GAP_DECISION.json`
exists (decision E-D6 from `analysis/gap_smoke/GAP_SMOKE.md`):

    cd trial_0826/ercot/waves/location_oat_v2 && bash submit_this.sh

`submit_this.sh` refuses without `GAP_DECISION.json`, prints it, prints
`qquota`, and asks for a literal `yes` before `qsub`.

## 1. Rule (pre-registered; text untouched)

Prompt 36 section 4.2, copied verbatim in `analysis/cost_fix/WAVE_D_TOPK_RULE.md`
(commit 4fb3b1f, before wave B landed). Selection recorded in
`analysis/cost_fix/wave_d_selection.json`: A ruler = 0 (byte-identical
replicates) so the rule reduces to the top 6 by relief per MW: sites
163, 140, 146, 270, 110, 274 (all WIND). Plus nuclear gen 1 (formulation A:
thermal patch, cost-curve band, forced commitment; T0 fix {T0_FIX} is in the
tree and `submit_this.sh` asserts it). Each site alone, other sites absent.
Three ABSOLUTE MW levels, Kay 11-06: 60 / 120 / 180 MW. Every row `--full`
(prompt 36 section 4.2 addendum 11-06; prompt 57 A5).

## 2. Rows ({n}; order fixed by prompt 58 section 3)

{chr(10).join(tab)}

`PEM_fraction = pem_mw / gen_pmax` (renewable; nameplate from
`data/ercot123_2019_v2/gen.csv`) or `pem_mw / 2430.0` (nuclear). Builder asserts:
max level (180 MW) <= min chosen nameplate (185.4 MW, site 163; the egret
renewable patch clamps silently above nameplate), every fraction <= 1.
Bid 40.0 $/MWh, full year from 01-01-2019, `replicate_of` empty.
`design_matrix.csv` = the screening schema + `pem_mw` + `level_id`.
Retrofit dicts: renewable `{{"<site>": {{"PEM_bid", "PEM_fraction", "gen_pmax"}}}}`;
nuclear `{{"1": {{"PEM_bid", "PEM_fraction"}}}}` with NO `gen_pmax` key
(`waves/selection_t1_v2/retrofit_gen_dict_6.json` convention).

**Nuclear omega note.** omega = {nuc_w} for 60 / 120 / 180 MW. These sit below
the Stage-1 0.05 lattice floor. That floor is an RTS convention, not an ERCOT
constraint; the T0 fix {T0_FIX} covers any omega (committed initial output lifted
to the raised p_min). Rows 19-21 are labelled formulation A.

## 3. Identity gate (GP training data runs under the FINAL identity only)

Prompt 53 rule: wave D onward runs under the final solver identity. The array
script reads `--ruc_mipgap` / `--ruc_time_limit` from `waves/GAP_DECISION.json`
at RUN time (python one-liner after `conda activate`), prints
`IDENTITY from GAP_DECISION.json: ruc_mipgap=... ruc_time_limit=...` into every
task log, and refuses (FAILED marker) if the file is missing. It is also
SMOKE_GATEd on `waves/smoke_v2/SMOKE_PASS` like the v2 waves. The collector
copies the decision used to `extracts/location_oat_v2/GAP_DECISION_used.json`
and each task's identity line to `run_index_N/identity.txt`.

## 4. Collector and the gz policy

`collect_location_oat_v2.sh` (held on the array, email on this job only):
every row `extract_ercot.py --full` -> `extracts/location_oat_v2/run_index_N/`,
Prescient `runtimes.csv` copied per row, wall-clock from the `WAVE_D_START` /
`WAVE_D_END` stamps -> `extracts/location_oat_v2/wallclock.csv`, then ON CRC
`python pool_objectives.py --run-dir <extract> --out <extract>/pool_full_metrics.json`
(E8, E9, N5, the commitment-headroom diagnostic, R7/R8, RUC quality, manifest
md5s). Git receives the SLIM tables + `pool_full_metrics.json` + `runtimes.csv`
+ `extract_manifest.json`; the four `*.csv.gz` tables stay UNCOMMITTED
(`trial_0826/ercot/.gitignore`: `extracts/location_oat_v2/**/*.csv.gz`; the
collector aborts if a gz is staged). The gz files stay in `$GROUP` storage and
are listed by name + md5 in each `extract_manifest.json`
(`pool_full_metrics.json` re-hashes them: `manifest.gz_verified`).

Storage: {n} x {FULL_EXTRACT_MB} MB = {n * FULL_EXTRACT_MB / 1024:.2f} GB of full
extracts on CRC; about 60 MB in git.

## 5. Expected wall-clock

Per row = 365 RUC solves + SCEDs + pricing + overhead. Under the frozen identity
(0.01 / 120) the v2 base RUC solve time was median 19.2 s, max 50.7 s per day
(2.0 h/yr RUC time at the median); the measured v2 full-year runs took about
18-27 h wall each at 4 slots. Under the adopted identity: year RUC time =
365 x the smoke's median (and max) per-day solve time, printed in
`GAP_SMOKE.md` (rule (iii) caps the max-projection at 61 h, about +2.5 CRC
days on a 4-slot run). {n} tasks x 4 slots = {4 * n} slots, no `-tc`.

## 6. Local checks (zero simulation)

`bash -n` on the three scripts; `tests/test_make_wave_d.py` (row count and
order, fractions, the <= 185.4 assert fires at 186, nuclear dict without
`gen_pmax`, the GAP_DECISION refusal of the array block and of
`submit_this.sh`, `.gitignore` line, committed wave == fresh build).
"""


def main():
    d, rows = build()
    nuc = [r for r in rows if r["unit_type"] == "NUC"]
    print(f"built {d}: {len(rows)} rows; nuclear omega = "
          + " / ".join(f"{r['omega']:.5f}" for r in nuc))
    print(f"storage: {len(rows)} x {FULL_EXTRACT_MB} MB = {len(rows) * FULL_EXTRACT_MB / 1024:.2f} GB "
          f"full extracts on CRC; about 60 MB in git (gz left in storage)")


if __name__ == "__main__":
    main()
