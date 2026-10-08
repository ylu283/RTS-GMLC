#!/bin/bash
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
# Prescient's reporting_manager uses os.mkdir (no parents) on the output
# dir — the PARENT must exist or the run dies in 1 s (same bug that killed
# base_2019 on 09-20; the array script already carries mkdir -p).
mkdir -p "$WAVE_DIR/smoke"
python "$ERCOT_DIR/run_ercot_pcm.py" \
    --index smoke --num_days 3 --start_date 01-01-2019 \
    --ruc_time_limit 120 --ruc_threads 4 \
    --output_directory "$WAVE_DIR/smoke/run" \
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
