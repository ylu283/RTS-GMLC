"""Prompt 55 — wave writer for one acquisition round `methods_E_<arm>_s<seed>_r<k>`.

Writes (contract 5, the `__ALL__` convention — the reader needs no change):
  waves/<wave>/design_matrix.csv      q rows; columns = the wave-D COLS order then
                                      the extras: index, oat_site="__ALL__",
                                      unit_type="", bus="", omega="", bid=40.0,
                                      gen_pmax="", start_date=01-01-2019,
                                      num_days=365, replicate_of="", pem_mw=sum mw,
                                      level_id="", tier="bo", sobol_index="",
                                      mw_<site> x d, u_<site> x d (full precision)
  waves/<wave>/retrofit_gen_dict_<i>.json   {"<site>": {"PEM_bid": 40.0,
                                      "PEM_fraction": u_s, "gen_pmax": gen_pmax_s}}
                                      for every site with mw_s > 0; mw_s == 0
                                      exactly -> site OMITTED (plan 2: 0 = absent)
  waves/<wave>/manifest.json, README.md

The CRC job scripts are GENERIC (one array + one collector for every round,
`qsub -v WAVE=<wave> -wd <ercot>/waves`), written once into
analysis/methods_E/ by `write_templates()` with the native tools/make_noise_v3.py
blocks: identity from waves/GAP_DECISION.json at run time (refuse without it),
SMOKE_GATE, METHODS_E_START/END stamps, every row `extract_ercot.py --full`,
Prescient runtimes.csv + wallclock.csv, identity.txt per row,
`pool_objectives.py --run-dir -> pool_full_metrics.json`, the COLLECTED marker,
ercot-bot commit of the slim tables (+ json + marker) with the *.csv.gz assert
(trial_0826/ercot/.gitignore `extracts/methods_E_*/**/*.csv.gz`, owned by 53).

Collision-checked: an existing wave dir is REFUSED (a round is never regenerated).
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys

import numpy as np
import pandas as pd

from common_E import HERE, DesignSpace, now, repo_root

BID = 40.0
START_DATE, NUM_DAYS = "01-01-2019", 365
BASE_COLS = ["index", "oat_site", "unit_type", "bus", "omega", "bid", "gen_pmax",
             "start_date", "num_days", "replicate_of", "pem_mw", "level_id", "tier", "sobol_index"]
GITIGNORE_LINE = "extracts/methods_E_*/**/*.csv.gz"
EMAIL = "ylu28@nd.edu"


def _tools(root):
    t = os.path.join(root, "tools")
    if t not in sys.path:
        sys.path.insert(0, t)
    import make_v2_waves as mv  # noqa: E402  (the house blocks: ENV, PUSH, SMOKE_GATE, extract_cmd)
    return mv


def assert_gitignore(root: str) -> None:
    p = os.path.join(root, ".gitignore")
    assert os.path.isfile(p), f"{p} missing"
    lines = [ln.strip() for ln in open(p)]
    assert GITIGNORE_LINE in lines, f"{p} lacks the line {GITIGNORE_LINE!r} (contract 4; owned by 53)"


def design_rows(ds: DesignSpace, U: np.ndarray) -> list[dict]:
    U = np.asarray(U, float)
    assert U.ndim == 2 and U.shape[1] == ds.d, U.shape
    assert np.all(U >= 0.0) and np.all(U <= 1.0), "u outside [0, 1]"
    assert not np.any((U > 0) & (U < 1e-9)), "u in (0, 1e-9): a near-zero site would enter the PCM (contract 5: exact 0 = absent)"
    X = ds.u_to_mw(U)
    rows = []
    for i, (u, x) in enumerate(zip(U, X), start=1):
        r = {"index": i, "oat_site": "__ALL__", "unit_type": "", "bus": "", "omega": "", "bid": BID,
             "gen_pmax": "", "start_date": START_DATE, "num_days": NUM_DAYS, "replicate_of": "",
             "pem_mw": float(x.sum()), "level_id": "", "tier": "bo", "sobol_index": ""}
        for c, v in zip(ds.x_columns, x):
            r[c] = float(v)
        for c, v in zip(ds.u_columns, u):
            r[c] = float(v)
        rows.append(r)
    return rows


def retrofit_dict(ds: DesignSpace, row: dict) -> dict:
    out = {}
    for s, pm, xc, uc in zip(ds.sites, ds.gen_pmax, ds.x_columns, ds.u_columns):
        if float(row[xc]) > 0.0:                       # exact 0 -> omitted (plan 2; never omega = 0)
            out[s] = {"PEM_bid": BID, "PEM_fraction": float(row[uc]), "gen_pmax": float(pm)}
    return out


def _git_head(root):
    try:
        return subprocess.run(["git", "-C", repo_root(root), "rev-parse", "--short", "HEAD"],
                              capture_output=True, text=True, check=True).stdout.strip()
    except Exception:  # noqa: BLE001
        return "unknown"


def build_round_wave(root: str, ds: DesignSpace, wave: str, U, manifest_extra: dict | None = None,
                     pred_mean=None, pred_sd=None, objectives=None, transforms=None) -> str:
    """Write waves/<wave>/ for q proposals U (q, d) in u units. Returns the dir."""
    assert_gitignore(root)
    wdir = os.path.join(root, "waves", wave)
    if os.path.exists(wdir):
        raise RuntimeError(f"REFUSED: {wdir} already exists — a methods_E round is never regenerated")
    assert wave.startswith("methods_E_"), wave
    rows = design_rows(ds, U)
    q = len(rows)
    keys = {tuple(np.round(r_[c], 12) for c in ds.u_columns) for r_ in rows}
    assert len(keys) == q, "duplicate designs in batch"
    os.makedirs(wdir)
    cols = BASE_COLS + ds.x_columns + ds.u_columns
    pd.DataFrame(rows, columns=cols).to_csv(os.path.join(wdir, "design_matrix.csv"), index=False)
    for r in rows:
        with open(os.path.join(wdir, f"retrofit_gen_dict_{r['index']}.json"), "w") as f:
            json.dump(retrofit_dict(ds, r), f, indent=2)
            f.write("\n")
    if pred_mean is not None:
        pm = np.asarray(pred_mean, float); ps = np.asarray(pred_sd, float)
        pr = {"index": [r["index"] for r in rows]}
        for j, o in enumerate(objectives):
            pr[f"{o}_pred_mean"] = pm[:, j]
            pr[f"{o}_pred_sd"] = ps[:, j]
            pr[f"{o}_transform"] = [transforms[j]] * q
        pd.DataFrame(pr).to_csv(os.path.join(wdir, "predictions.csv"), index=False)
    man = {"wave": wave, "campaign": "methods_E", "prompt": "55", "q": q, "tier": "bo",
           "design_space": os.path.relpath(ds.path, root),
           "design_space_md5": hashlib.md5(open(ds.path, "rb").read()).hexdigest(),
           "contract_version": ds.raw.get("contract_version"), "identity": "v3 from waves/GAP_DECISION.json at run time",
           "sites": ds.sites, "gen_pmax": ds.gen_pmax.tolist(), "bid": BID,
           "git_head": _git_head(root), "created_at": now()}
    man.update(manifest_extra or {})
    with open(os.path.join(wdir, "manifest.json"), "w") as f:
        json.dump(man, f, indent=2, default=float)
        f.write("\n")
    with open(os.path.join(wdir, "README.md"), "w") as f:
        f.write(wave_readme(wave, rows, ds, man))
    return wdir


def wave_readme(wave, rows, ds, man):
    hdr = "| row | " + " | ".join(f"MW {s}" for s in ds.sites) + " | sum MW | " + " | ".join(f"u {s}" for s in ds.sites) + " |"
    sep = "|" + "---|" * (2 + 2 * ds.d)
    tab = [hdr, sep]
    for r in rows:
        tab.append(f"| {r['index']} | " + " | ".join(f"{r[c]:.3f}" for c in ds.x_columns)
                   + f" | {r['pem_mw']:.3f} | " + " | ".join(f"{r[c]:.5f}" for c in ds.u_columns) + " |")
    return f"""# {wave} — methods_E acquisition round (prompt 55; NOT submitted by the writer)

Arm `{man.get('methods_arm')}`, seed_id {man.get('seed_id')}, round {man.get('methods_round')},
acq {man.get('acq')} seed {man.get('acq_seed')}; bo-gp {man.get('bo_gp_sha', '?')}; botorch
{man.get('botorch', '?')}; guardrail_mode {man.get('guardrail_mode', '?')}. Created {man['created_at']}.

Rows are `oat_site = __ALL__` multi-site designs (contract 5): `mw_<site>` /
`u_<site>` at full precision, `pem_mw = sum mw`, `tier = bo`. The retrofit dict
`retrofit_gen_dict_<i>.json` lists every site with mw > 0 (a site at exactly 0
is ABSENT). Bid {BID} $/MWh, full year from {START_DATE}.

{chr(10).join(tab)}

Submission: Kay runs `bash analysis/methods_E/submit_ready_E.sh` on the CRC
login node (generic `methods_E_array.sh` + `methods_E_collect.sh`, `-v WAVE={wave}`,
`-wd trial_0826/ercot/waves`, identity from `waves/GAP_DECISION.json` at run
time, every row `--full`, slim tables + `pool_full_metrics.json` + `COLLECTED`
committed, `*.csv.gz` left in storage). `predictions.csv` holds the pre-round
GP mean / total sd per objective (calibration gates C2 / C3 at grading).
"""


# --------------------------------------------------------------------------- #
# generic CRC templates (written once into analysis/methods_E/)
# --------------------------------------------------------------------------- #

HEADER_E = """set -euo pipefail
: "${WAVE:?WAVE env var required (qsub -v WAVE=<wave>)}"
WAVES_DIR="$PWD"   # -wd trial_0826/ercot/waves
WAVE_DIR="$WAVES_DIR/$WAVE"
ERCOT_DIR="$(cd "$WAVES_DIR/.." && pwd)"
TRIAL_DIR="$(cd "$ERCOT_DIR/.." && pwd)"
REPO_DIR="$(cd "$TRIAL_DIR/.." && pwd)"
DATA_DIR="$ERCOT_DIR/%s"
"""

GAP_READ = """# --- identity from waves/GAP_DECISION.json (Kay, E-D6); refuse without it ---
GAP_FILE="$ERCOT_DIR/waves/GAP_DECISION.json"
if [[ ! -f "$GAP_FILE" ]]; then
    echo "no GAP_DECISION.json" > "$WAVE_DIR/FAILED_task_${SGE_TASK_ID}_no_gap_decision.md"
    echo "ABORT task $SGE_TASK_ID: $GAP_FILE absent — methods_E runs only under a decided identity"; exit 1
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


def array_template(mv) -> str:
    return f"""#!/bin/bash
#$ -q long
#$ -pe smp 4
#$ -r n
# Generic methods_E array task (prompt 55). Submitted ONLY by
# analysis/methods_E/submit_ready_E.sh from the CRC login node:
#   qsub -wd <ercot>/waves -v WAVE=<wave> -t 1-8 -N <wave>_array methods_E_array.sh
# NO email flags (one email per task otherwise), no -tc. Reads the design at
# task START (hold mode: a held acquisition wrote it) and fails loudly if absent.
# Identity: --ruc_mipgap / --ruc_time_limit from waves/GAP_DECISION.json at run time.
{HEADER_E % mv.V2_DATA_REL}
if [[ ! -f "$WAVE_DIR/design_matrix.csv" ]]; then
    echo "FATAL: $WAVE_DIR/design_matrix.csv absent at task start — the held acquisition" >&2
    echo "did not write this round (WEDGED/FAILED/HALT/DONE?). Not running." >&2
    exit 1
fi
{mv.SMOKE_GATE}mkdir -p "$WAVE_DIR/runs"
{mv.ENV}module load gurobi
{GAP_READ}
eval "$(python "$TRIAL_DIR/campaign/get_row.py" "$SGE_TASK_ID" "$WAVE_DIR/design_matrix.csv")"
OUT_PARENT="$WAVE_DIR/runs"
DICT="$WAVE_DIR/retrofit_gen_dict_${{SGE_TASK_ID}}.json"
echo "METHODS_E_TASK=$WAVE:$SGE_TASK_ID dict=$(tr -d '\\n ' < "$DICT")"
echo "METHODS_E_START $(date -u +%FT%TZ) epoch=$(date +%s)"
{RUN}echo "METHODS_E_END $(date -u +%FT%TZ) epoch=$(date +%s)"
"""


def collect_template(mv) -> str:
    ext = mv.extract_cmd('"$WAVE_DIR/runs/run_index_$i"', '"$EXTR/run_index_$i"', "--full",
                         '"$WAVE_DIR"/"$WAVE"_array.o*."$i"')
    return f"""#!/bin/bash
#$ -q long
#$ -r n
# Generic methods_E collector (prompt 55). Submitted ONLY by submit_ready_E.sh:
#   qsub -wd <ercot>/waves -v WAVE=<wave> -hold_jid <array> -N collect_<wave> -M {EMAIL} -m ea methods_E_collect.sh
# gate (every row's overall_simulation_output.csv) -> --full extracts (every row)
# + runtimes.csv + wall-clock + identity.txt -> pool_objectives.py --run-dir ->
# pool_full_metrics.json -> COLLECTED marker -> ercot-bot commit of the SLIM
# tables + json + marker (*.csv.gz stay in storage: trial_0826/ercot/.gitignore
# `{GITIGNORE_LINE}`), 5-retry push to ercot/tx123.
{HEADER_E % mv.V2_DATA_REL}{mv.ENV}
{mv.PUSH}
exec 9>"$REPO_DIR/.git/methods_E.flock"
if [[ ! -f "$WAVE_DIR/design_matrix.csv" ]]; then
    echo "FATAL: $WAVE_DIR has no design_matrix.csv at collection (held acquisition did not write it)"; exit 1
fi
N=$(python - "$WAVE_DIR/design_matrix.csv" <<'PY'
import csv, sys
print(sum(1 for _ in csv.DictReader(open(sys.argv[1]))))
PY
)
missing=""
for i in $(seq 1 "$N"); do
    [[ -f "$WAVE_DIR/runs/run_index_$i/overall_simulation_output.csv" ]] || missing="$missing $i"
done
if [[ -n "$missing" ]]; then
    marker="$WAVE_DIR/FAILED_$WAVE.md"
    {{ echo "# FAILED — $WAVE incomplete"; echo; echo "missing:$missing";
      echo "Recovery: resubmit the missing tasks ONCE (qsub -t <i> ...), then re-run this collector.";
      echo "Generated $(date -u +%FT%TZ)"; }} > "$marker"
    flock 9
    git -C "$REPO_DIR" add -- "$marker"
    git -C "$REPO_DIR" "${{BOT[@]}}" commit -m "ercot-bot: FAILED marker ($WAVE)"
    push_with_retries
    flock -u 9
    exit 1
fi
echo "GATE PASS: $N/$N"
if [[ -f "$WAVE_DIR/FAILED_$WAVE.md" ]]; then
    git -C "$REPO_DIR" rm -q -- "$WAVE_DIR/FAILED_$WAVE.md" 2>/dev/null || rm -f "$WAVE_DIR/FAILED_$WAVE.md"
    echo "stale FAILED marker cleared"
fi

EXTR="$ERCOT_DIR/extracts/$WAVE"
mkdir -p "$EXTR"
cp -f "$ERCOT_DIR/waves/GAP_DECISION.json" "$EXTR/GAP_DECISION_used.json"
cp -f "$WAVE_DIR/design_matrix.csv" "$EXTR/design_matrix_used.csv"
echo "task,start_epoch,end_epoch,wall_s" > "$EXTR/wallclock.csv"
for i in $(seq 1 "$N"); do
{ext}
    cp -f "$WAVE_DIR/runs/run_index_$i/run/runtimes.csv" "$EXTR/run_index_$i/runtimes.csv" \\
        || echo "WARNING: row $i has no Prescient runtimes.csv"
    if [[ -n "$JOBLOG" ]]; then
        S=$(grep -h "METHODS_E_START" "$JOBLOG" | sed -n 's/.*epoch=\\([0-9]*\\).*/\\1/p' | head -1)
        E=$(grep -h "METHODS_E_END" "$JOBLOG" | sed -n 's/.*epoch=\\([0-9]*\\).*/\\1/p' | tail -1)
        echo "$i,${{S:-}},${{E:-}},$(( ${{E:-0}} - ${{S:-0}} ))" >> "$EXTR/wallclock.csv"
        grep -h "IDENTITY from GAP_DECISION.json" "$JOBLOG" > "$EXTR/run_index_$i/identity.txt" || true
    fi
    python "$ERCOT_DIR/pool_objectives.py" --run-dir "$EXTR/run_index_$i" \\
        --out "$EXTR/run_index_$i/pool_full_metrics.json"
done
{{ echo "wave=$WAVE rows=$N collected_utc=$(date -u +%FT%TZ)";
  echo "head=$(git -C "$REPO_DIR" rev-parse --short HEAD)";
  echo "identity=$(tr -d '\\n' < "$ERCOT_DIR/waves/GAP_DECISION.json")"; }} > "$EXTR/COLLECTED"

# git policy: slim tables + pool_full_metrics.json + runtimes.csv + manifest + marker;
# *.csv.gz are ignored by trial_0826/ercot/.gitignore and asserted absent below.
flock 9
git -C "$REPO_DIR" add -- "$EXTR"
if git -C "$REPO_DIR" diff --cached --name-only | grep -q '\\.csv\\.gz$'; then
    echo "ABORT: a *.csv.gz is staged — .gitignore line missing?"; git -C "$REPO_DIR" reset -q; exit 1
fi
git -C "$REPO_DIR" "${{BOT[@]}}" commit -m "ercot-bot: $WAVE extracts (slim + pool_full_metrics + COLLECTED; gz left in storage)"
push_with_retries
flock -u 9
echo "collect $WAVE done"
"""


def write_templates(root: str, out_dir: str | None = None) -> dict:
    mv = _tools(root)
    out_dir = out_dir or os.path.join(root, "analysis", "methods_E")
    paths = {}
    for name, body in (("methods_E_array.sh", array_template(mv)), ("methods_E_collect.sh", collect_template(mv))):
        p = os.path.join(out_dir, name)
        with open(p, "w") as f:
            f.write(body)
        os.chmod(p, 0o755)
        paths[name] = p
    return paths


if __name__ == "__main__":
    from common_E import ercot_root
    print(write_templates(ercot_root()))
