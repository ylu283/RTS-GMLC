"""Build waves/selection_t1/ (prompt 32 T1): replicate hardening + nuclear OAT.

11 full-year rows: 2 more base solves (base group -> df=3), 1 more wind-275
(pocket group -> df=2), 2 PV-30 replicates (NEW stratum -> df=2), 5-level
on-lattice nuclear gen-1 OAT (lattice indices {0,2,4,6,8}), 1 nuclear
omega=0.525 replicate (df=1, mode-pinning qualitative only).

Run LOCALLY (needs campaign/tiers.py for STAGE2_LATTICE — never transcribe
the lattice); the wave is committed and submitted on CRC via its own
submit_this.sh (smoke-gated: see selection_t1_smoke.sh — hold_jid releases
on COMPLETION not success, so every array task re-checks SMOKE_PASS).
Deterministic and idempotent EXCEPT it refuses an existing wave dir.
"""

import csv
import json
import os
import sys

ERCOT_DIR = os.path.dirname(os.path.abspath(__file__))
TRIAL_DIR = os.path.dirname(ERCOT_DIR)
sys.path.insert(0, os.path.join(TRIAL_DIR, "campaign"))
from tiers import STAGE2_LATTICE  # noqa: E402  (never transcribe literals)

WAVE = "selection_t1"
WAVE_DIR = os.path.join(ERCOT_DIR, "waves", WAVE)
BID = 40.0
NUC_LEVELS = [float(STAGE2_LATTICE[i]) for i in (0, 2, 4, 6, 8)]  # 5-level subset
# site facts from the screening design matrices / data gen.csv (audited)
W275 = {"site": "275", "unit_type": "WIND", "bus": 120, "omega": 0.5,
        "gen_pmax": 1038.999987796685, "replicate_of": "screening_ercot:1"}
PV30 = {"site": "30", "unit_type": "PV", "bus": 26, "omega": 0.4,
        "gen_pmax": 926.6666666666669, "replicate_of": "screening_ercot:8"}
NUC1 = {"site": "1", "unit_type": "NUC", "bus": 107, "gen_pmax": 2430.0}

HEADER = ["index", "oat_site", "unit_type", "bus", "omega", "bid",
          "gen_pmax", "start_date", "num_days", "replicate_of"]


def rows_and_dicts():
    rows, dicts = [], {}
    idx = 0

    def add(site, ut, bus, omega, pmax, rep, gdict):
        nonlocal idx
        idx += 1
        rows.append({"index": idx, "oat_site": site, "unit_type": ut,
                     "bus": bus, "omega": omega, "bid": BID if gdict else "",
                     "gen_pmax": pmax, "start_date": "01-01-2019",
                     "num_days": 365, "replicate_of": rep})
        dicts[idx] = gdict

    for _ in range(2):  # base group -> 4 solves total, df = 3
        add("__BASE_REPLICATE__", "", "", "", "", "base_2019:base", {})
    add(W275["site"], W275["unit_type"], W275["bus"], W275["omega"],
        W275["gen_pmax"], W275["replicate_of"],
        {"275": {"PEM_bid": BID, "PEM_fraction": W275["omega"],
                 "gen_pmax": W275["gen_pmax"]}})
    for _ in range(2):  # PV stratum (site 30 = screening_ercot ROW 8)
        add(PV30["site"], PV30["unit_type"], PV30["bus"], PV30["omega"],
            PV30["gen_pmax"], PV30["replicate_of"],
            {"30": {"PEM_bid": BID, "PEM_fraction": PV30["omega"],
                    "gen_pmax": PV30["gen_pmax"]}})
    for w in NUC_LEVELS:  # indices 6-10; omega=0.525 lands at index 8
        add(NUC1["site"], NUC1["unit_type"], NUC1["bus"], w, NUC1["gen_pmax"],
            "", {"1": {"PEM_bid": BID, "PEM_fraction": w}})  # thermal: no gen_pmax
    add(NUC1["site"], NUC1["unit_type"], NUC1["bus"], 0.525, NUC1["gen_pmax"],
        f"{WAVE}:8", {"1": {"PEM_bid": BID, "PEM_fraction": 0.525}})
    assert idx == 11 and rows[7]["omega"] == 0.525  # replicate_of target check
    return rows, dicts


SMOKE = """#!/bin/bash
#$ -N selection_t1_smoke
#$ -q long
#$ -cwd
#$ -pe smp 4
#$ -r n
# 3-day nuclear omega=1.0 smoke (prompt 32 T1.0 gate iii). Writes SMOKE_PASS
# into the wave dir ONLY if every gate passes — the array tasks hold on this
# job's COMPLETION and then check for the file themselves (explicit gating;
# -hold_jid releases on completion, not success).
set -euo pipefail
WAVE_DIR="$PWD"
ERCOT_DIR="$(cd "$PWD/../.." && pwd)"
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate PCM_ERCOT
export PYTHONNOUSERSITE=1
module load gurobi

rm -f "$WAVE_DIR/SMOKE_PASS"
python "$ERCOT_DIR/run_ercot_pcm.py" \\
    --index smoke --num_days 3 --start_date 01-01-2019 \\
    --ruc_time_limit 120 --ruc_threads 4 \\
    --output_directory "$WAVE_DIR/smoke/run" \\
    --retrofit_gen_dict '{"1": {"PEM_bid": 40.0, "PEM_fraction": 1.0}}'

python - "$WAVE_DIR/smoke/run_index_smoke" <<'EOF'
import sys, os
import pandas as pd
d = sys.argv[1]
assert os.path.isfile(os.path.join(d, "overall_simulation_output.csv")), "no overall output"
td = pd.read_csv(os.path.join(d, "thermal_detail.csv"))
td["Generator"] = td["Generator"].astype(str)
g1 = td[td.Generator == "1"]
assert len(g1) == 72, f"expected 72 gen-1 hours, got {len(g1)}"
on = g1[g1["Unit State"].astype(float) > 0]
assert len(on) == 72, "p_min=0 fixed-committed unit not committed all hours"
h2 = float((2430.0 - on["Dispatch"].astype(float)).sum())
assert h2 > 0, "thermal h2 == 0 (prompt-32 gate)"
print(f"smoke gates: committed 72/72, dispatch min {on['Dispatch'].min():.1f}, h2 {h2:,.1f} MWh")
EOF

LOG=$(ls -t "$WAVE_DIR"/selection_t1_smoke.o* 2>/dev/null | head -1 || true)
if [[ -n "$LOG" ]] && grep -q "Solution count 0" "$LOG"; then
    echo "GATE FAIL: SolCount=0 day in smoke"; exit 1
fi
echo "SMOKE PASS $(date -u +%FT%TZ)" > "$WAVE_DIR/SMOKE_PASS"
echo "SMOKE_PASS written"
"""

ARRAY = """#!/bin/bash
#$ -N selection_t1_array
#$ -q long
#$ -cwd
#$ -t 1-11
#$ -pe smp 4
#$ -r n
# Prompt 32 T1 array. -pe smp 4 + --ruc_threads 4 is FROZEN solver
# provenance (shapes the TL=120 incumbent and the rulers) — never retune.
# Explicit smoke gating: exits with a FAILED marker if SMOKE_PASS absent.
set -euo pipefail
WAVE_DIR="$PWD"
ERCOT_DIR="$(cd "$PWD/../.." && pwd)"
TRIAL_DIR="$(cd "$ERCOT_DIR/.." && pwd)"
if [[ ! -f "$WAVE_DIR/SMOKE_PASS" ]]; then
    echo "no SMOKE_PASS" > "$WAVE_DIR/FAILED_task_${SGE_TASK_ID}_no_smoke.md"
    echo "ABORT task $SGE_TASK_ID: SMOKE_PASS absent"; exit 1
fi
mkdir -p "$WAVE_DIR/runs"
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate PCM_ERCOT
export PYTHONNOUSERSITE=1
module load gurobi

eval "$(python "$TRIAL_DIR/campaign/get_row.py" "$SGE_TASK_ID" "$WAVE_DIR/design_matrix.csv")"

python "$ERCOT_DIR/run_ercot_pcm.py" \\
    --index "$INDEX" \\
    --num_days "$NUM_DAYS" \\
    --start_date "$START_DATE" \\
    --ruc_time_limit 120 \\
    --ruc_threads 4 \\
    --output_directory "$WAVE_DIR/runs/run" \\
    --retrofit_gen_dict "$(cat "$WAVE_DIR/retrofit_gen_dict_${SGE_TASK_ID}.json")"
"""

COLLECTOR = """#!/bin/bash
#$ -N collect_selection_t1
#$ -q long
#$ -cwd
#$ -r n
# Prompt 32 T1 collector: gate -> extracts (slim 1-5, --full 6-11 for the
# thermal-h2 rule) -> compute_objectives.py (objectives_t1.csv +
# noise_ruler_v2 groups) -> ercot-bot commit + 5-RETRY randomized-backoff
# push to ercot/tx123 (prompt-30 loop; push_with_one_retry is superseded).
set -euo pipefail
WAVE_DIR="$PWD"
ERCOT_DIR="$(cd "$PWD/../.." && pwd)"
REPO_DIR="$(cd "$ERCOT_DIR/../.." && pwd)"
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate PCM_ERCOT
export PYTHONNOUSERSITE=1

BOT=(-c user.name="ercot-bot" -c user.email="ercot-bot@noreply.github.com")
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

missing=""
for i in $(seq 1 11); do
    [[ -f "$WAVE_DIR/runs/run_index_$i/overall_simulation_output.csv" ]] || missing="$missing $i"
done
if [[ -n "$missing" ]]; then
    marker="$WAVE_DIR/FAILED_selection_t1.md"
    { echo "# FAILED — selection_t1 incomplete"; echo; echo "missing:$missing";
      echo "Generated $(date -u +%FT%TZ)"; } > "$marker"
    git -C "$REPO_DIR" add -- "$marker"
    git -C "$REPO_DIR" "${BOT[@]}" commit -m "ercot-bot: FAILED marker (selection_t1)"
    push_with_retries
    exit 1
fi
echo "GATE PASS: 11/11"

for i in $(seq 1 11); do
    JOBLOG=$(ls -t "$WAVE_DIR"/selection_t1_array.o*."$i" 2>/dev/null | head -1 || true)
    FULL=""
    [[ "$i" -ge 6 ]] && FULL="--full"   # nuclear rows: hourly thermal dispatch needed
    python "$ERCOT_DIR/extract_ercot.py" \\
        "$WAVE_DIR/runs/run_index_$i" \\
        "$ERCOT_DIR/extracts/selection_t1/run_index_$i" $FULL \\
        ${JOBLOG:+--joblog "$JOBLOG"}
done

python "$ERCOT_DIR/compute_objectives.py"

git -C "$REPO_DIR" add -- "$ERCOT_DIR/extracts/selection_t1" \\
    "$ERCOT_DIR/analysis/selection/objectives_t1.csv" \\
    "$ERCOT_DIR/analysis/selection/noise_ruler_v2.json" \\
    "$ERCOT_DIR/PROGRESS.md"
git -C "$REPO_DIR" "${BOT[@]}" commit -m "ercot-bot: selection_t1 extracts + objectives + ruler v2 groups"
push_with_retries
echo "collect_selection_t1 done"
"""

SUBMIT = """#!/bin/bash
# selection_t1 — smoke -> array -> collector (prompt 32 T1).
# Run ON CRC from anywhere:  bash submit_this.sh
cd "$(dirname "${BASH_SOURCE[0]}")"
set -euo pipefail
WAVE_DIR="$PWD"
ERCOT_DIR="$(cd "$PWD/../.." && pwd)"
REPO_DIR="$(cd "$ERCOT_DIR/../.." && pwd)"

BRANCH="$(git -C "$REPO_DIR" branch --show-current)"
[[ "$BRANCH" == "ercot/tx123" ]] || { echo "ABORT: on '$BRANCH', expected ercot/tx123"; exit 1; }
git -C "$REPO_DIR" pull --rebase --autostash origin ercot/tx123

S=$(qsub -terse selection_t1_smoke.sh | cut -d. -f1)
[[ "$S" =~ ^[0-9]+$ ]] || { echo "BAD SMOKE JID: $S"; exit 1; }
J=$(qsub -terse -hold_jid "$S" -t 1-11 selection_t1_array.sh | cut -d. -f1)
[[ "$J" =~ ^[0-9]+$ ]] || { echo "BAD ARRAY JID: $J"; exit 1; }
C=$(qsub -terse -hold_jid "$J" -cwd -M ylu28@nd.edu -m ea collect_selection_t1.sh)
[[ "$C" =~ ^[0-9]+$ ]] || { echo "BAD COLLECTOR JID: $C"; exit 1; }
echo "SUBMITTED selection_t1: smoke=$S array=$J collector=$C"
qstat -u ylu28
"""


def main():
    if os.path.exists(WAVE_DIR):
        raise SystemExit(f"REFUSED: {WAVE_DIR} exists (never regenerate a wave)")
    os.makedirs(WAVE_DIR)
    rows, dicts = rows_and_dicts()
    with open(os.path.join(WAVE_DIR, "design_matrix.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=HEADER)
        w.writeheader()
        w.writerows(rows)
    for i, d in dicts.items():
        with open(os.path.join(WAVE_DIR, f"retrofit_gen_dict_{i}.json"), "w") as f:
            json.dump(d, f, indent=2, sort_keys=True)
            f.write("\n")
    for name, body in (("selection_t1_smoke.sh", SMOKE),
                       ("selection_t1_array.sh", ARRAY),
                       ("collect_selection_t1.sh", COLLECTOR),
                       ("submit_this.sh", SUBMIT)):
        p = os.path.join(WAVE_DIR, name)
        with open(p, "w") as f:
            f.write(body)
        os.chmod(p, 0o755)
    print(f"built {WAVE_DIR}: 11 rows, nuclear levels {NUC_LEVELS}")


if __name__ == "__main__":
    main()
