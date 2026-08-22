#!/bin/bash
# Informational Gurobi license check — run on CRC BEFORE the pilot batch
# (doc 14 §5.2: license concurrency is the top pre-campaign check; full-year
# jobs hold a license ~40 h each). Does not submit or change anything.

echo "GRB_LICENSE_FILE=${GRB_LICENSE_FILE:-<unset>}"

if [ -n "${GRB_LICENSE_FILE:-}" ] && [ -f "$GRB_LICENSE_FILE" ]; then
    echo "--- token/limit lines in license file ---"
    grep -E "TOKENSERVER|LIMIT" "$GRB_LICENSE_FILE" || echo "(no TOKENSERVER/LIMIT lines found)"
else
    echo "(license file not set or not readable from this shell)"
fi

if command -v gurobi_cl >/dev/null 2>&1; then
    echo "--- gurobi_cl --license ---"
    gurobi_cl --license
else
    echo "gurobi_cl not on PATH — run 'module load gurobi' first"
fi
