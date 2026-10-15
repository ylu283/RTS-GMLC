#!/bin/bash
# fetch_runs.sh — prompt 38 (mechanism checks). KAY RUNS THIS on the Mac.
#
# Pulls the per-run Prescient CSVs for the 15 selected runs (see
# run_selection.csv, picked by t0_local_checks.py) from the CRC clone
# into analysis/mechanism/runs/ (gitignored). One rsync per run dir.
# Only FINISHED waves: stage2_C_n0, stage2_C_n0b, bo_C_r1, bo_C_r2,
# random_C. Estimated size: about 1.5-1.8 GB total.
#
# Usage:
#   bash fetch_runs.sh
# Override the host if needed:
#   CRC_HOST=ylu28@crcfe02.crc.nd.edu bash fetch_runs.sh

set -euo pipefail

CRC_HOST="${CRC_HOST:-ylu28@crcfe01.crc.nd.edu}"
REMOTE_WAVES="/groups/adowling/ylu28/RTS-GMLC/trial_0826/campaign/waves"
HERE="$(cd "$(dirname "$0")" && pwd)"
DEST="$HERE/runs"

# wave:index — Q1 contrast set (6), Q2 22.426 set (7), Q2 contrast (2).
RUNS=(
    # Q1 LOW total PEM MW, high shed
    "bo_C_r2:3"        # 407 MW, 29182 MWh shed (spec)
    "random_C:42"      # 827 MW,  9312 MWh shed
    # Q1 MID
    "stage2_C_n0:16"   # 1763 MW, 2516 MWh shed
    "random_C:30"      # 1764 MW, 4549 MWh shed
    # Q1 HIGH, zero shed
    "bo_C_r1:5"        # 2494 MW, 0 shed (spec)
    "bo_C_r2:2"        # 2622 MW, 0 shed
    # Q2: every design with shed == 22.425956 MWh
    "stage2_C_n0:1"
    "stage2_C_n0:6"
    "stage2_C_n0b:6"
    "bo_C_r2:7"
    "random_C:5"
    "random_C:14"
    "random_C:15"
    # Q2 contrast: different small shed
    "random_C:39"      # 128.17 MWh
    "bo_C_r1:4"        # 139.63 MWh
)

# Only these CSVs (plus any RUC/DA commitment file, if one exists).
INCLUDES=(
    --include='overall_simulation_output.csv'
    --include='hourly_summary.csv'
    --include='hourly_gen_summary.csv'
    --include='bus_detail.csv'
    --include='thermal_detail.csv'
    --include='renewables_detail.csv'
    --include='reserves_detail.csv'
    --include='*ruc*' --include='*RUC*'
    --include='*commit*'
    --exclude='*'
)

for run in "${RUNS[@]}"; do
    wave="${run%%:*}"
    idx="${run##*:}"
    src="$REMOTE_WAVES/$wave/runs/run_index_$idx/"
    dst="$DEST/$wave/run_index_$idx/"
    mkdir -p "$dst"
    echo "== $wave run_index_$idx =="
    rsync -az --progress "${INCLUDES[@]}" "$CRC_HOST:$src" "$dst"
done

echo
echo "Done. Fetched files:"
find "$DEST" -name '*.csv' | sort
echo
echo "Run dirs fetched: $(find "$DEST" -name 'overall_simulation_output.csv' | wc -l) of ${#RUNS[@]} expected"
