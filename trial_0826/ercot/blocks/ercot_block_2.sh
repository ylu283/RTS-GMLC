#!/bin/bash
# ERCOT paste-block #2 — SMOKE + HARD-DAY PROBES (prompt 26 T2). Run ON CRC
# after ercot_block_1.sh printed BLOCK 1 PASS:
#   bash ercot_block_2.sh 2>&1 | tee ercot_block_2.log
# Submits 4 jobs (all PCM_ERCOT, no -tc):
#   smoke_3d   01-01-2019 x3d, RUC TL=600  — gap-vs-time at 60/120/300/600 s
#              per day CHARACTERIZES what TL=120 buys (decision already
#              made; nothing here holds the base submit)
#   probe_jul  07-16-2019 x1d, TL=120 — worst July day of the prior log
#   probe_sep  09-28-2019 x1d, TL=120 — worst September day (both capped
#              at 3600 s in the TL=3600 run)
#   eoy_3d     12-29-2019 x3d, TL=120 — Dec-31 RUC must run onto the padded
#              1/1/2020 rows, not off the data (verifies T1.2 padding)
# Riders: probe gap >= 10% -> REPORT to Kay (decision stands unless he
# reverses); any SolCount=0 -> add MIPFocus=1 (rider (iv)) BEFORE the base.
# Expected wall: queue wait + ~30-60 min run; polls up to 4 h.

set -euo pipefail

ERCOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
SMOKE_DIR="$ERCOT_DIR/smoke"          # untracked scratch (gitignored)
mkdir -p "$SMOKE_DIR"
cd "$SMOKE_DIR"

declare -A START=([smoke_3d]=01-01-2019 [probe_jul]=07-16-2019 [probe_sep]=09-28-2019 [eoy_3d]=12-29-2019)
declare -A DAYS=([smoke_3d]=3 [probe_jul]=1 [probe_sep]=1 [eoy_3d]=3)
declare -A TL=([smoke_3d]=600 [probe_jul]=120 [probe_sep]=120 [eoy_3d]=120)

JIDS=()
for name in smoke_3d probe_jul probe_sep eoy_3d; do
    cat > "job_${name}.sh" <<EOF
#!/bin/bash
#$ -N ercot_${name}
#$ -q long
#$ -cwd
#$ -pe smp 4
set -euo pipefail
source "\$(conda info --base)/etc/profile.d/conda.sh"
conda activate PCM_ERCOT
export PYTHONNOUSERSITE=1  # ~/.local vanilla prescient shadows the patched editable install
module load gurobi
python "$ERCOT_DIR/run_ercot_pcm.py" \\
    --index "${name}" \\
    --num_days "${DAYS[$name]}" \\
    --start_date "${START[$name]}" \\
    --ruc_time_limit "${TL[$name]}" \\
    --ruc_threads 4 \\
    --output_directory "$SMOKE_DIR/run" \\
    --retrofit_gen_dict '{}'
EOF
    JID=$(qsub -terse "job_${name}.sh")
    [[ "$JID" =~ ^[0-9]+$ ]] || { echo "BAD JID for $name: $JID"; exit 1; }
    echo "$name submitted: JID=$JID"
    JIDS+=("$JID")
done

waited=0
for JID in "${JIDS[@]}"; do
    while qstat -j "$JID" >/dev/null 2>&1; do
        sleep 60; waited=$((waited + 60))
        if (( waited >= 14400 )); then
            echo "BLOCK 2 FAIL: job $JID still in queue after 4 h"; qstat -u ylu28; exit 1
        fi
    done
done
echo "all 4 jobs left the queue after ~${waited}s ($(date))"

FAIL=0
for name in smoke_3d probe_jul probe_sep eoy_3d; do
    if [[ ! -f "$SMOKE_DIR/run_index_${name}/overall_simulation_output.csv" ]]; then
        echo "FAIL: $name has no overall_simulation_output.csv (eoy_3d failing here = padding broken)"
        FAIL=1
    fi
done
(( FAIL == 0 )) || { echo "BLOCK 2 FAIL — paste this log back."; exit 1; }
echo "all 4 runs completed (eoy_3d completing IS the padding evidence: the 12-31 RUC ran onto the padded 1/1/2020 rows)"

echo "--- warning whitelist scan (known cosmetics: piecewise gen 2; startup/shutdown-curve 26/165/175/177/269; no reserves.csv; default t0) ---"
for name in smoke_3d probe_jul probe_sep eoy_3d; do
    LOG=$(ls -t "$SMOKE_DIR"/ercot_${name}.o* | head -1)
    n_unexpected=$(grep -iE "warn" "$LOG" | grep -vcE \
      "Extending piecewise linear cost curve .* generator 2 |Truncating (startup|shutdown)_curve .* generator (26|165|175|177|269)|Did not find reserves.csv|Setting default t0" \
      || true)
    echo "$name: $n_unexpected non-whitelisted warning lines"
    if (( n_unexpected > 0 )); then
        grep -iE "warn" "$LOG" | grep -vE \
          "Extending piecewise linear cost curve .* generator 2 |Truncating (startup|shutdown)_curve .* generator (26|165|175|177|269)|Did not find reserves.csv|Setting default t0" | head -10
    fi
done

echo "--- RUC quality + gap-vs-time + LMP/reserves checks ---"
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate PCM_ERCOT
export PYTHONNOUSERSITE=1  # ~/.local vanilla prescient shadows the patched editable install
python - "$SMOKE_DIR" "$ERCOT_DIR" <<'EOF'
import re, sys
from pathlib import Path
import pandas as pd
smoke, ercot = Path(sys.argv[1]), Path(sys.argv[2])
sys.path.insert(0, str(ercot))
from extract_ercot import parse_ruc_quality, OPEN_RE, CLOSE_RE, DATE_RE

NODE = re.compile(r"\s(\d+(?:\.\d+)?)%.*?\s(\d+)s\s*$")
def gap_vs_time(log):
    segs, cur, date = [], None, "day1"
    for line in log.open(errors="replace"):
        m = DATE_RE.search(line)
        if m: date = m.group(1); continue
        if OPEN_RE.search(line): cur = (date, []); continue
        if cur is None: continue
        m = NODE.search(line)
        if m: cur[1].append((int(m.group(2)), float(m.group(1))))
        if CLOSE_RE.search(line): segs.append(cur); cur = None
    return segs

def newest(pat):
    files = sorted(smoke.glob(pat), key=lambda p: p.stat().st_mtime)
    return files[-1] if files else None

print("smoke_3d gap-vs-time (TL=600 characterization of what TL=120 buys):")
for date, pts in gap_vs_time(newest("ercot_smoke_3d.o*")):
    row = {}
    for t in (60, 120, 300, 600):
        seen = [g for (s, g) in pts if s <= t]
        row[t] = f"{seen[-1]:.2f}%" if seen else "-"
    print(f"  {date}: gap@60s {row[60]}  @120s {row[120]}  @300s {row[300]}  @600s {row[600]}")

worst_gap, solzero = 0.0, []
for name in ("probe_jul", "probe_sep", "eoy_3d", "smoke_3d"):
    log = newest(f"ercot_{name}.o*")
    rq = parse_ruc_quality(log)
    print(f"{name}: " + "; ".join(
        f"{r.ruc_date}: gap {r.final_gap_pct}% sol_count {r.sol_count} {r.status}"
        for r in rq.itertuples()))
    if name.startswith("probe"):
        worst_gap = max(worst_gap, rq["final_gap_pct"].fillna(0).max())
    z = rq[rq["sol_count"].fillna(1) == 0]
    solzero += [(name, d) for d in z["ruc_date"]]

if solzero:
    print(f"*** RIDER (iv): SolCount=0 at TL=120 on {solzero} — add "
          "--ruc_solver_option MIPFocus=1 to base_job.sh + arrays BEFORE the base submit. ***")
else:
    print("rider (iv) clear: no SolCount=0 day")
if worst_gap >= 10:
    print(f"*** RIDER (iii): worst probe gap {worst_gap:.1f}% >= 10% — REPORT to Kay "
          "with these numbers before the base submit (decision stands unless reversed). ***")
else:
    print(f"rider (iii) clear: worst probe gap {worst_gap:.2f}% < 10%")

for name in ("smoke_3d",):
    run = smoke / f"run_index_{name}"
    bd = pd.read_csv(run / "bus_detail.csv", usecols=["LMP"])
    print(f"{name} LMPs: mean {bd.LMP.mean():.2f} p1 {bd.LMP.quantile(.01):.1f} "
          f"p99 {bd.LMP.quantile(.99):.1f} max {bd.LMP.max():.1f} "
          f"(<= price_threshold 500; ORDER-OF-MAGNITUDE check only — the "
          f"paper's $17.98 mean was LMP+5000, ours is aCHP+500); "
          f"floor artifacts <= -900: {(bd.LMP <= -900).sum()}")
    rs = pd.read_csv(run / "reserves_detail.csv")
    print(f"{name} reserves_detail cols: {list(rs.columns)}; "
          f"shortfall nonzero hours: {(rs['Shortfall'] != 0).sum()}/{len(rs)} "
          "(degenerate-g4 verdict waits for the full TL=120 base)")
EOF

echo "BLOCK 2 DONE — paste this log back; base submit (block 3) proceeds unless a rider banner printed above."
