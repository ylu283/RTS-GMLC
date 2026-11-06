#!/usr/bin/env python3
"""Prompt 52 v2.1 — build `waves/noise_v3/` (ERCOT noise measurement; NOT submitted).

Zero simulation. Kay submits batch A, then batch B, ON CRC.

Pick (pre-registered; the rule text is written to PICK_RULE.md BEFORE the
pick is computed): 4 designs from the 22-row pool (16 single-site v2 rows +
6 nuclear v2 rows; 21 distinct designs) scored on the 22 gradable candidates
of prompt 57 (analysis/pool/pool_delta_v2.csv, frozen f76d897). v2-identity
values choose designs ONLY (disclosed); they are never data.

Rows: per design one EXACT copy in batch A, one EXACT copy in batch B (the
cross-batch exact pair, both v3 runs) and one PERTURBED copy in batch A
(delta = 0.001 relative on pem_mw, inward at 0 and at nameplate; sign from
the pinned seed). Default layout = 16 rows (A: 8, B: 8; strategy 11-06: ruler population 8 per prompt 57 A4). `--layout 12` is the thinner alternative (A: 8, B: 4). `--layout 16` adds
one antithetic perturbed copy per design to batch B (A: 8, B: 8; ruler
population 8 instead of 4). The split is a resolution of prompt 52 section
3 ("4 designs x 3 copies ~ 12 runs", "TWO submission batches", exact pairs
cross-batch) and is disclosed in README.md as a deviation to confirm.

Identity: every array reads --ruc_mipgap / --ruc_time_limit from
waves/GAP_DECISION.json at run time (the wave-D block, copied) and refuses
without it; SMOKE_GATE on waves/smoke_v2/SMOKE_PASS; date stamps
NOISE_V3_START / NOISE_V3_END. Collectors (one per batch, held on the
batch's array, email on the collector only): every row --full ->
extracts/noise_v3/<batch>/run_index_N, Prescient runtimes.csv, wallclock.csv,
pool_objectives.py --run-dir -> pool_full_metrics.json, a COLLECTED marker,
ercot-bot commit of the slim tables + json + marker, 5-retry push; *.csv.gz
stay in storage (trial_0826/ercot/.gitignore). Batch B's submit_this.sh
refuses until extracts/noise_v3/A/COLLECTED is in the tree.
"""
import argparse
import itertools
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ERCOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ERCOT / "tools"))
from make_v2_waves import EMAIL, ENV, PUSH, V2_DATA_REL, extract_cmd, write  # noqa: E402

WAVE = "noise_v3"
PROMPT = "52 v2.1"
POOL_CSV = ERCOT / "analysis" / "pool" / "pool_delta_v2.csv"
DEFS_JSON = ERCOT / "analysis" / "pool" / "pool_definitions.json"
POOL_FREEZE = "f76d897"
# pinned pool order (prompt 52 v2.1: 16 single-site v2 rows + 6 nuclear rows)
POOL_KEYS = ([f"screening_v2/ercot:{i}" for i in range(1, 10)]
             + [f"screening_v2/topup:{i}" for i in range(1, 8)]
             + [f"selection_t1_v2:{i}" for i in range(6, 12)])
N_GRADABLE = 22                 # first 22 of pool_definitions global_order
COMPOSITION = {"VRE": 3, "NUC": 1}
DELTA_REL = 0.001               # prompt 52 v2.1: relative on pem_mw
SEED = 52                       # perturbation sign seed (pinned in the matrix)
BID = 40.0
START_DATE, NUM_DAYS = "01-01-2019", 365
NUC_SITE, NUC_PMAX = "1", 2430.0
T0_FIX = "7c5fb8d"
FULL_EXTRACT_MB = 51
LAYOUTS = {"12": {"A": 1, "B": 0}, "16": {"A": 1, "B": 1}}   # perturbed copies per design per batch
BATCHES = ["A", "B"]

# --------------------------------------------------------------------------
# pre-registered pick rule (written to PICK_RULE.md before the pick runs)
# --------------------------------------------------------------------------
PICK_RULE = f"""# noise_v3 pick rule (prompt {PROMPT}; pinned BEFORE the pick is computed)

Written by `tools/make_noise_v3.py` before `pick_table.csv`. The code applies
the rule; there is no manual override. Changing this text after the pick is
an amendment and must be disclosed.

## Disclosure

The v2 table was public before this rule was written (`SCREENING_ERCOT.md`,
`analysis/pool/POOL_V2.md`, `pool_delta_v2.csv`). The author had seen it.
The v2-identity values choose designs ONLY. They are never data: every
noise_v3 run is a v3 run (`waves/GAP_DECISION.json`), and no v2 value
enters `ERCOT_NOISE.md`.

## Rule

1. **Pool.** The 22 rows `{', '.join(POOL_KEYS[:9])}`,
   `{', '.join(POOL_KEYS[9:16])}`, `{', '.join(POOL_KEYS[16:])}` of
   `analysis/pool/pool_delta_v2.csv` (frozen {POOL_FREEZE}). Byte-identical
   duplicates (`selection_t1_v2:11` = `:8`, design D21) count once: 21
   distinct designs (16 VRE single-site, 5 nuclear).
2. **Objectives.** The {N_GRADABLE} gradable candidates = the first
   {N_GRADABLE} ids of `global_order` in `pool_definitions.json`. A candidate
   with no value on any pool row (E8, E9, N5: the v2 extracts are slim) is
   listed in the table as NOT USED and does not enter the score.
3. **Composition.** {COMPOSITION['VRE']} VRE single-site designs + {COMPOSITION['NUC']} nuclear
   design (proportional to the pool, 16 : 5, and to wave D, 18 : 3; the
   ruler is transferred to the wave-D sites, prompt 57 section 3 A4).
4. **Score.** For a set S of 4 designs and a used objective j,
   spread_j(S) = (max_S delta_j - min_S delta_j) / (max_pool delta_j -
   min_pool delta_j), with delta = value - base over the 21 designs.
   score(S) = mean_j spread_j(S). Exhaustive search over all
   C(16, {COMPOSITION['VRE']}) x C(5, {COMPOSITION['NUC']}) sets; the maximum wins.
5. **Tie.** The set whose tuple of pool positions (pinned order above) is
   lexicographically smallest.
6. **Table.** `pick_table.csv`: one row per gradable candidate with the
   achieved spread, the pool min/max and which design holds each, and the
   4 picked values. Correlated candidates collapse strata: they show the
   same designs at min and max. That is made visible, not hidden.

## Copies (prompt 52 section 3, v2.1)

- EXACT copy: the v2 design's `omega`, `gen_pmax`, `bid` byte-for-byte;
  one in batch A, one in batch B (the cross-batch exact pair).
- PERTURBED copy: `pem_mw' = pem_mw x (1 + s x {DELTA_REL})`, `omega' =
  pem_mw' / gen_pmax` (nuclear: `/ {NUC_PMAX}`); the sign `s` of the
  first copy of each design is drawn from `numpy.random.default_rng({SEED})`
  (recorded as `perturb_sign`, seed as `perturb_seed`); a second copy
  (layout 16) is antithetic (`-s`). Corner rule: if `pem_mw'` leaves
  `[0, gen_pmax]`, the sign is flipped inward; if that collides with the
  other copy, the inward step is `2 x {DELTA_REL}`.
"""


def load_pool(pool_csv=POOL_CSV, keys=POOL_KEYS):
    p = pd.read_csv(pool_csv, dtype={"site": str, "replicate_of": str,
                                     "distinct_design_id": str, "unit_type": str})
    p = p[p["key"].isin(keys)].copy()
    p["pos"] = p["key"].map({k: i for i, k in enumerate(keys)})
    p = p.sort_values("pos").reset_index(drop=True)
    assert len(p) == len(keys), (len(p), len(keys))
    distinct = p.drop_duplicates("distinct_design_id", keep="first").copy()
    distinct["stratum"] = np.where(distinct["unit_type"] == "NUC", "NUC", "VRE")
    return distinct.reset_index(drop=True)


def gradable_ids(defs_json=DEFS_JSON, n=N_GRADABLE):
    with open(defs_json) as f:
        d = json.load(f)
    ids = d["global_order"][:n]
    assert all(d["candidates"][i].get("priority") is not None for i in ids), ids
    return ids, d


def pick(distinct, ids, composition=COMPOSITION):
    """Exhaustive max of the mean achieved spread; returns (keys, score, table)."""
    used = [j for j in ids if distinct[j].notna().any()]
    not_used = [j for j in ids if j not in used]
    rng = {j: (float(distinct[j].max()) - float(distinct[j].min())) for j in used}
    for j in used:
        assert rng[j] > 0, f"{j}: zero range over the pool"
    vre = distinct.index[distinct["stratum"] == "VRE"].tolist()
    nuc = distinct.index[distinct["stratum"] == "NUC"].tolist()
    vals = {j: distinct[j].to_numpy(dtype=float) for j in used}
    best, best_score, best_tuple = None, -1.0, None
    for cv in itertools.combinations(vre, composition["VRE"]):
        for cn in itertools.combinations(nuc, composition["NUC"]):
            S = list(cv) + list(cn)
            sc = float(np.mean([(vals[j][S].max() - vals[j][S].min()) / rng[j] for j in used]))
            tup = tuple(sorted(int(distinct.loc[i, "pos"]) for i in S))
            if sc > best_score + 1e-12 or (abs(sc - best_score) <= 1e-12 and tup < best_tuple):
                best, best_score, best_tuple = S, sc, tup
    keys = [str(distinct.loc[i, "key"]) for i in best]
    rows = []
    for j in ids:
        r = {"id": j, "used_in_pick": j in used}
        if j in used:
            v = vals[j]
            imin, imax = int(np.argmin(v)), int(np.argmax(v))
            sel = v[best]
            r.update({"pool_min": float(v[imin]), "pool_min_design": str(distinct.loc[imin, "key"]),
                      "pool_max": float(v[imax]), "pool_max_design": str(distinct.loc[imax, "key"]),
                      "picked_min": float(sel.min()), "picked_max": float(sel.max()),
                      "achieved_spread": float((sel.max() - sel.min()) / rng[j]),
                      "picked_min_design": keys[int(np.argmin(sel))],
                      "picked_max_design": keys[int(np.argmax(sel))]})
            for k, i in zip(keys, best):
                r[f"delta_{k}"] = float(v[i])
        else:
            r.update({"pool_min": np.nan, "pool_min_design": "NOT USED (no v2 value: slim extracts)",
                      "pool_max": np.nan, "pool_max_design": "", "picked_min": np.nan,
                      "picked_max": np.nan, "achieved_spread": np.nan,
                      "picked_min_design": "", "picked_max_design": ""})
        rows.append(r)
    table = pd.DataFrame(rows)
    return keys, best_score, table, {"used": used, "not_used": not_used}


# --------------------------------------------------------------------------
# rows
# --------------------------------------------------------------------------
def perturb(pem, pmax, sign, delta=DELTA_REL, taken=()):
    """pem x (1 + sign x delta), inward at the bounds [0, pmax]; a collision
    with an already-taken value steps 2 x delta inward."""
    cand = pem * (1.0 + sign * delta)
    if cand > pmax or cand < 0.0:
        sign = -sign
        cand = pem * (1.0 + sign * delta)
    if any(abs(cand - t) < 1e-9 for t in taken):
        cand = pem * (1.0 + sign * 2.0 * delta)
        assert 0.0 <= cand <= pmax, (pem, pmax, cand)
        return cand, sign, 2.0 * delta
    assert 0.0 <= cand <= pmax, (pem, pmax, cand)
    return cand, sign, delta


def design_rows(distinct, keys, layout="12", seed=SEED, delta=DELTA_REL):
    """Rows for batches A and B. index = position inside the batch."""
    per_batch = LAYOUTS[layout]
    rng = np.random.default_rng(seed)
    signs = {k: int(rng.choice([-1, 1])) for k in keys}
    rows = {b: [] for b in BATCHES}
    base = {}
    for n, k in enumerate(keys, start=1):
        r = distinct[distinct["key"] == k].iloc[0]
        nuclear = r["unit_type"] == "NUC"
        pmax = NUC_PMAX if nuclear else float(r["gen_pmax"])
        omega = float(r["omega"])
        pem = omega * pmax
        assert abs(pem - float(r["pem_mw"])) < 1e-6, (k, pem, r["pem_mw"])
        base[k] = {"oat_site": str(r["site"]), "unit_type": str(r["unit_type"]),
                   "bus": int(float(r["bus"])), "bid": BID, "gen_pmax": pmax,
                   "start_date": START_DATE, "num_days": NUM_DAYS, "replicate_of": k,
                   "design_id": str(r["distinct_design_id"]), "design_no": n,
                   "pem_mw_origin": pem, "omega_origin": omega}
    # exact copies first (A then B), then perturbed copies
    for b in BATCHES:
        for k in keys:
            rows[b].append({**base[k], "omega": base[k]["omega_origin"], "pem_mw": base[k]["pem_mw_origin"],
                            "copy_type": "exact", "batch": b, "perturb_seed": seed,
                            "perturb_sign": 0, "delta_rel": 0.0})
    copy_no = {k: 0 for k in keys}
    taken = {k: [] for k in keys}
    for b in BATCHES:
        for _ in range(per_batch[b]):
            for k in keys:
                s = signs[k] if copy_no[k] == 0 else -signs[k]
                copy_no[k] += 1
                pem_p, s_used, d_used = perturb(base[k]["pem_mw_origin"], base[k]["gen_pmax"], s,
                                                delta, taken[k])
                taken[k].append(pem_p)
                rows[b].append({**base[k], "omega": pem_p / base[k]["gen_pmax"], "pem_mw": pem_p,
                                "copy_type": "perturbed", "batch": b, "perturb_seed": seed,
                                "perturb_sign": s_used, "delta_rel": d_used})
    gi = 0
    for b in BATCHES:
        for i, r in enumerate(rows[b], start=1):
            gi += 1
            r["index"] = i
            r["global_index"] = gi
            assert 0.0 <= r["omega"] <= 1.0, r
    n_exp = len(keys) * (2 + sum(per_batch.values()))
    assert sum(len(v) for v in rows.values()) == n_exp
    return rows


COLS = ["index", "oat_site", "unit_type", "bus", "omega", "bid", "gen_pmax",
        "start_date", "num_days", "replicate_of", "pem_mw", "copy_type", "batch",
        "perturb_seed", "perturb_sign", "delta_rel", "design_id", "design_no",
        "pem_mw_origin", "omega_origin", "global_index"]


def retrofit_dict(row):
    """Renewable: {site: {PEM_bid, PEM_fraction, gen_pmax}}; nuclear: no gen_pmax
    (waves/selection_t1_v2/retrofit_gen_dict_6.json convention)."""
    d = {"PEM_bid": BID, "PEM_fraction": row["omega"]}
    if row["unit_type"] != "NUC":
        d["gen_pmax"] = row["gen_pmax"]
    return {row["oat_site"]: d}


# --------------------------------------------------------------------------
# scripts (wave-D pattern; batch dirs sit one level deeper than waves/<wave>)
# --------------------------------------------------------------------------
HEADER3 = """set -euo pipefail
WAVE_DIR="$PWD"   # -cwd: submitted from inside waves/noise_v3/<batch> (submit_this.sh cd's there)
ERCOT_DIR="$(cd "$WAVE_DIR/../../.." && pwd)"
TRIAL_DIR="$(cd "$ERCOT_DIR/.." && pwd)"
REPO_DIR="$(cd "$TRIAL_DIR/.." && pwd)"
DATA_DIR="$ERCOT_DIR/%s"
""" % V2_DATA_REL

SMOKE_GATE = """SMOKE="$ERCOT_DIR/waves/smoke_v2/SMOKE_PASS"
if [[ ! -f "$SMOKE" ]]; then
    echo "no SMOKE_PASS" > "$WAVE_DIR/FAILED_task_${SGE_TASK_ID}_no_smoke.md"
    echo "ABORT task $SGE_TASK_ID: $SMOKE absent"; exit 1
fi
"""

GAP_READ = """# --- identity from waves/GAP_DECISION.json (Kay, E-D6); refuse without it ---
GAP_FILE="$ERCOT_DIR/waves/GAP_DECISION.json"
if [[ ! -f "$GAP_FILE" ]]; then
    echo "no GAP_DECISION.json" > "$WAVE_DIR/FAILED_task_${SGE_TASK_ID}_no_gap_decision.md"
    echo "ABORT task $SGE_TASK_ID: $GAP_FILE absent — noise_v3 runs only under a decided identity"; exit 1
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


def array_script(batch, n, layout):
    name = f"{WAVE}_{batch}"
    return f"""#!/bin/bash
#$ -N {name}_array
#$ -q long
#$ -cwd
#$ -t 1-{n}
#$ -pe smp 4
#$ -r n
# Prompt {PROMPT} noise_v3 batch {batch}: {n} full-year rows (layout {layout}; exact and
# perturbed copies of 4 pre-registered v2 designs, PICK_RULE.md). Runs ONLY under
# the identity in waves/GAP_DECISION.json (Kay, E-D6), read at run time below.
{HEADER3}{SMOKE_GATE}mkdir -p "$WAVE_DIR/runs"
{ENV}module load gurobi
{GAP_READ}
eval "$(python "$TRIAL_DIR/campaign/get_row.py" "$SGE_TASK_ID" "$WAVE_DIR/design_matrix.csv")"
OUT_PARENT="$WAVE_DIR/runs"
DICT="$WAVE_DIR/retrofit_gen_dict_${{SGE_TASK_ID}}.json"
echo "NOISE_V3_TASK={batch}:$SGE_TASK_ID dict=$(tr -d '\\n ' < "$DICT")"
echo "NOISE_V3_START $(date -u +%FT%TZ) epoch=$(date +%s)"
{RUN}echo "NOISE_V3_END $(date -u +%FT%TZ) epoch=$(date +%s)"
"""


def collector_script(batch, n):
    name = f"{WAVE}_{batch}"
    check = f"""for i in $(seq 1 {n}); do
    [[ -f "$WAVE_DIR/runs/run_index_$i/overall_simulation_output.csv" ]] || missing="$missing $i"
done"""
    ext = extract_cmd('"$WAVE_DIR/runs/run_index_$i"', '"$EXTR/run_index_$i"', "--full",
                      f'"$WAVE_DIR"/{name}_array.o*."$i"')
    return f"""#!/bin/bash
#$ -N collect_{name}
#$ -q long
#$ -cwd
#$ -r n
# Prompt {PROMPT} collector ({name}): gate -> --full extracts (every row) +
# runtimes.csv + wall-clock -> per-run pool metrics (pool_objectives.py
# --run-dir, ON CRC under PCM_ERCOT) -> COLLECTED marker -> ercot-bot commit of
# the SLIM tables + pool_full_metrics.json + runtimes.csv + extract_manifest.json
# + marker; *.csv.gz stay uncommitted (trial_0826/ercot/.gitignore) in $GROUP
# storage. Email flags are applied by submit_this.sh on THIS job only.
{HEADER3}{ENV}
{PUSH}
missing=""
{check}
if [[ -n "$missing" ]]; then
    marker="$WAVE_DIR/FAILED_{name}.md"
    {{ echo "# FAILED — {name} incomplete"; echo; echo "missing:$missing";
      echo "Generated $(date -u +%FT%TZ)"; }} > "$marker"
    git -C "$REPO_DIR" add -- "$marker"
    git -C "$REPO_DIR" "${{BOT[@]}}" commit -m "ercot-bot: FAILED marker ({name})"
    push_with_retries
    exit 1
fi
echo "GATE PASS: {n}/{n}"
if [[ -f "$WAVE_DIR/FAILED_{name}.md" ]]; then
    git -C "$REPO_DIR" rm -q -- "$WAVE_DIR/FAILED_{name}.md" 2>/dev/null \\
        || rm -f "$WAVE_DIR/FAILED_{name}.md"
    echo "stale FAILED marker cleared"
fi

EXTR="$ERCOT_DIR/extracts/{WAVE}/{batch}"
mkdir -p "$EXTR"
cp -f "$ERCOT_DIR/waves/GAP_DECISION.json" "$EXTR/GAP_DECISION_used.json"
cp -f "$WAVE_DIR/design_matrix.csv" "$EXTR/design_matrix_used.csv"
echo "task,start_epoch,end_epoch,wall_s" > "$EXTR/wallclock.csv"
for i in $(seq 1 {n}); do
{ext}
    cp -f "$WAVE_DIR/runs/run_index_$i/run/runtimes.csv" "$EXTR/run_index_$i/runtimes.csv" \\
        || echo "WARNING: row $i has no Prescient runtimes.csv"
    if [[ -n "$JOBLOG" ]]; then
        S=$(grep -h "NOISE_V3_START" "$JOBLOG" | sed -n 's/.*epoch=\\([0-9]*\\).*/\\1/p' | head -1)
        E=$(grep -h "NOISE_V3_END" "$JOBLOG" | sed -n 's/.*epoch=\\([0-9]*\\).*/\\1/p' | tail -1)
        echo "$i,${{S:-}},${{E:-}},$(( ${{E:-0}} - ${{S:-0}} ))" >> "$EXTR/wallclock.csv"
        grep -h "IDENTITY from GAP_DECISION.json" "$JOBLOG" > "$EXTR/run_index_$i/identity.txt" || true
    fi
    python "$ERCOT_DIR/pool_objectives.py" --run-dir "$EXTR/run_index_$i" \\
        --out "$EXTR/run_index_$i/pool_full_metrics.json"
done
{{ echo "batch={batch} rows={n} collected_utc=$(date -u +%FT%TZ)";
  echo "head=$(git -C "$REPO_DIR" rev-parse --short HEAD)";
  echo "identity=$(tr -d '\\n' < "$ERCOT_DIR/waves/GAP_DECISION.json")"; }} > "$EXTR/COLLECTED"

# git policy: slim tables + pool_full_metrics.json + runtimes.csv + manifest + marker;
# *.csv.gz are ignored by trial_0826/ercot/.gitignore and asserted absent below.
git -C "$REPO_DIR" add -- "$EXTR"
if git -C "$REPO_DIR" diff --cached --name-only | grep -q '\\.csv\\.gz$'; then
    echo "ABORT: a *.csv.gz is staged — .gitignore line missing?"; git -C "$REPO_DIR" reset -q; exit 1
fi
git -C "$REPO_DIR" "${{BOT[@]}}" commit -m "ercot-bot: {name} extracts (slim + pool_full_metrics + COLLECTED; gz left in storage)"
push_with_retries
echo "collect_{name} done"
"""


def submit_script(batch, n):
    name = f"{WAVE}_{batch}"
    b_gate = ""
    if batch == "B":
        b_gate = f"""[[ -f "$E/extracts/{WAVE}/A/COLLECTED" ]] || {{ echo "ABORT: extracts/{WAVE}/A/COLLECTED absent — batch A's collector has not pushed yet (submit A first, wait for its email)"; exit 1; }}
echo "--- batch A COLLECTED marker ---"; cat "$E/extracts/{WAVE}/A/COLLECTED"
"""
    return f"""#!/bin/bash
# Prompt {PROMPT} noise_v3 batch {batch} — run ON CRC (Kay, by hand):
#   cd trial_0826/ercot/waves/{WAVE}/{batch} && bash submit_this.sh
# {n} tasks x 4 slots = {4 * n} slots; no -tc. Collector held on the array.
{'# Batch B refuses until batch A' + "'s collector has pushed extracts/" + WAVE + '/A/COLLECTED.' if batch == 'B' else '# Submit this batch FIRST; batch B waits for its COLLECTED marker.'}
cd "$(dirname "${{BASH_SOURCE[0]}}")"
set -euo pipefail
E="$(cd ../../.. && pwd)"
W="$E/waves"
REPO_DIR="$(cd ../../../../.. && pwd)"
BRANCH="$(git -C "$REPO_DIR" branch --show-current)"
[[ "$BRANCH" == "ercot/tx123" ]] || {{ echo "ABORT: on '$BRANCH', expected ercot/tx123"; exit 1; }}
git -C "$REPO_DIR" pull --rebase --autostash origin ercot/tx123
[[ -f "$W/GAP_DECISION.json" ]] || {{ echo "ABORT: waves/GAP_DECISION.json absent — decide E-D6 first (read analysis/gap_smoke/GAP_SMOKE.md)"; exit 1; }}
[[ -f "$W/smoke_v2/SMOKE_PASS" ]] || {{ echo "ABORT: waves/smoke_v2/SMOKE_PASS absent — smoke gate not passed"; exit 1; }}
[[ -f "$E/{V2_DATA_REL}/gen.csv" ]] || {{ echo "ABORT: v2 data dir missing"; exit 1; }}
git -C "$REPO_DIR" merge-base --is-ancestor {T0_FIX} HEAD || {{ echo "ABORT: fix {T0_FIX} not in HEAD (nuclear rows)"; exit 1; }}
grep -q -- "--ruc_mipgap" "$E/run_ercot_pcm.py" || {{ echo "ABORT: run_ercot_pcm.py has no --ruc_mipgap"; exit 1; }}
grep -q "{WAVE}/\\*\\*/\\*.csv.gz" "$E/.gitignore" || {{ echo "ABORT: trial_0826/ercot/.gitignore gz line missing"; exit 1; }}
[[ -f design_matrix.csv && -f retrofit_gen_dict_{n}.json ]] || {{ echo "ABORT: batch {batch} files missing"; exit 1; }}
{b_gate}echo "--- waves/GAP_DECISION.json (the identity batch {batch} will run under; eyeball it) ---"
cat "$W/GAP_DECISION.json"
echo "-----------------------------------------------------------------------------"
echo "--- qquota (need {4 * n} slots for {n} tasks x 4) ---"; qquota -u ylu28 || true
read -r -p "Submit {n} full-year rows (noise_v3 batch {batch}) under this identity? [yes/NO] " ANS
[[ "$ANS" == "yes" ]] || {{ echo "not submitted"; exit 1; }}
J=$(qsub -terse {name}_array.sh | cut -d. -f1)
[[ "$J" =~ ^[0-9]+$ ]] || {{ echo "BAD ARRAY JID: $J"; exit 1; }}
C=$(qsub -terse -hold_jid "$J" -cwd -M {EMAIL} -m ea collect_{name}.sh)
[[ "$C" =~ ^[0-9]+$ ]] || {{ echo "BAD COLLECTOR JID: $C"; exit 1; }}
echo "SUBMITTED {name}: array=$J ({n} tasks x 4 slots) collector=$C"
qstat -u ylu28
"""


# --------------------------------------------------------------------------
# build
# --------------------------------------------------------------------------
def build(waves=ERCOT / "waves", pool_csv=POOL_CSV, defs_json=DEFS_JSON, layout="16",
          seed=SEED):
    d = waves / WAVE
    d.mkdir(parents=True, exist_ok=True)
    write(d / "PICK_RULE.md", PICK_RULE, 0o644)          # BEFORE the pick
    distinct = load_pool(pool_csv)
    ids, defs = gradable_ids(defs_json)
    keys, score, table, used = pick(distinct, ids)
    table.to_csv(d / "pick_table.csv", index=False)
    rows = design_rows(distinct, keys, layout, seed)
    allrows = [r for b in BATCHES for r in rows[b]]
    pd.DataFrame(allrows, columns=COLS).to_csv(d / "design_matrix.csv", index=False)
    for b in BATCHES:
        bd = d / b
        bd.mkdir(exist_ok=True)
        n = len(rows[b])
        pd.DataFrame(rows[b], columns=COLS).to_csv(bd / "design_matrix.csv", index=False)
        for r in rows[b]:
            write(bd / f"retrofit_gen_dict_{r['index']}.json",
                  json.dumps(retrofit_dict(r), indent=2) + "\n", 0o644)
        write(bd / f"{WAVE}_{b}_array.sh", array_script(b, n, layout))
        write(bd / f"collect_{WAVE}_{b}.sh", collector_script(b, n))
        write(bd / "submit_this.sh", submit_script(b, n))
    picked = []
    for k in keys:
        r = distinct[distinct["key"] == k].iloc[0]
        picked.append({"key": k, "design_id": str(r["distinct_design_id"]), "site": str(r["site"]),
                       "unit_type": str(r["unit_type"]), "bus": int(float(r["bus"])),
                       "pem_mw": float(r["pem_mw"]), "omega": float(r["omega"]),
                       "gen_pmax": float(r["gen_pmax"])})
    meta = {"prompt": PROMPT, "wave": WAVE, "layout": layout, "rows": {b: len(rows[b]) for b in BATCHES},
            "pool_csv": str(pool_csv.relative_to(ERCOT) if str(pool_csv).startswith(str(ERCOT)) else pool_csv),
            "pool_freeze": POOL_FREEZE, "pool_keys": POOL_KEYS, "n_distinct_designs": int(len(distinct)),
            "gradable_ids": ids, "objectives_used": used["used"], "objectives_not_used": used["not_used"],
            "composition": COMPOSITION, "score_mean_spread": score, "picked": picked,
            "delta_rel": DELTA_REL, "perturb_seed": seed, "identity": "v3 from waves/GAP_DECISION.json at run time"}
    write(d / "pick.json", json.dumps(meta, indent=2) + "\n", 0o644)
    write(d / "README.md", readme(rows, picked, table, score, layout, used), 0o644)
    return d, rows, picked, table


def readme(rows, picked, table, score, layout, used):
    n_a, n_b = len(rows["A"]), len(rows["B"])
    n = n_a + n_b
    tab = ["| batch | row | design | site | type | bus | copy | sign | delta_rel | PEM MW | nameplate MW | PEM_fraction |",
           "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for b in BATCHES:
        for r in rows[b]:
            tab.append(f"| {b} | {r['index']} | D{r['design_no']} ({r['replicate_of']}) | {r['oat_site']} | "
                       f"{r['unit_type']} | {r['bus']} | {r['copy_type']} | {r['perturb_sign']:+d} | "
                       f"{r['delta_rel']:.3f} | {r['pem_mw']:.4f} | {r['gen_pmax']:.1f} | {r['omega']:.6f} |")
    pk = ["| design | v2 origin | site | type | PEM MW | nameplate MW | omega |", "|---|---|---|---|---|---|---|"]
    for i, p in enumerate(picked, start=1):
        pk.append(f"| D{i} | {p['key']} ({p['design_id']}) | {p['site']} | {p['unit_type']} | "
                  f"{p['pem_mw']:.4f} | {p['gen_pmax']:.1f} | {p['omega']:.6f} |")
    sp = ["| candidate | used | achieved spread | pool min (design) | pool max (design) | picked min (design) | picked max (design) |",
          "|---|---|---|---|---|---|---|"]
    for _, r in table.iterrows():
        if r["used_in_pick"]:
            sp.append(f"| {r['id']} | yes | {r['achieved_spread']:.2f} | {r['pool_min']:.4g} ({r['pool_min_design']}) | "
                      f"{r['pool_max']:.4g} ({r['pool_max_design']}) | {r['picked_min']:.4g} ({r['picked_min_design']}) | "
                      f"{r['picked_max']:.4g} ({r['picked_max_design']}) |")
        else:
            sp.append(f"| {r['id']} | NOT USED (no v2 value: slim extracts) | | | | | |")
    nuc = [r for b in BATCHES for r in rows[b] if r["unit_type"] == "NUC"]
    nuc_line = ", ".join(f"{r['batch']}:{r['index']} {r['copy_type']} omega={r['omega']:.6f}" for r in nuc)
    return f"""# noise_v3 — ERCOT noise measurement (prompt {PROMPT}; built 2026-11-06, NOT submitted)

Built by `tools/make_noise_v3.py --layout {layout}`. Kay submits ON CRC, batch A
first, batch B after batch A's collector email:

    cd trial_0826/ercot/waves/{WAVE}/A && bash submit_this.sh
    cd trial_0826/ercot/waves/{WAVE}/B && bash submit_this.sh

Each `submit_this.sh` refuses without `waves/GAP_DECISION.json`, prints it,
prints `qquota`, and asks for a literal `yes` before `qsub`. Batch B's script
also refuses until `extracts/{WAVE}/A/COLLECTED` is in the tree (batch A's
collector writes and pushes it).

## 1. Purpose

Measure ERCOT run-to-run reproducibility per objective under the campaign
identity, and the response of each objective to a 0.1 % input move. Two
populations, never pooled (prompt 52 section 1):

- EXACT cross-batch pairs (A vs B) = the noise population (tau). Expected
  exact sd = 0 on this deterministic instrument. "If their sd is 0, τ
  collapses toward 0 and the stop rule becomes budget-cap-only — that is a
  FINDING about a deterministic instrument, stated in exactly those words,
  not a failure."
- PERTURBED copies (delta = {DELTA_REL} relative on `pem_mw`) = local input
  sensitivity: the replacement ruler `ruler_j` of prompt 57 section 3 A4 and
  the robustness rider's sensitivity level (ERCOT_BO_PLAN.md section 7).

## 2. Identity (v3)

Every run reads `--ruc_mipgap` / `--ruc_time_limit` from `waves/GAP_DECISION.json`
at RUN time (`ruc_mipgap 0.001`, `ruc_time_limit 1200`; Kay, E-D6, 2026-11-06),
prints `IDENTITY from GAP_DECISION.json: ...` into every task log, and refuses
without the file. Gate G1 of prompt 52 is MET by `analysis/gap_smoke/GAP_SMOKE.md`
(control arm byte-identical to smoke_v2; tolerance verified per RUC day; 0
time-limit hits) and ERCOT_BO_PLAN.md AMENDMENT 2026-11-06b. SMOKE_GATE on
`waves/smoke_v2/SMOKE_PASS`. Fix {T0_FIX} asserted (nuclear rows).

## 3. Pick (pre-registered rule, `PICK_RULE.md`; table `pick_table.csv`)

Rule text was written before the pick ran; v2-identity values chose designs
ONLY (disclosed in PICK_RULE.md) and never enter ERCOT_NOISE.md. Score =
mean achieved spread over the {len(used['used'])} used candidates = {score:.3f}
(E8, E9, N5 NOT USED: no v2 value on slim extracts).

{chr(10).join(pk)}

Achieved spread per candidate (1.00 = the pick holds the pool's min and max):

{chr(10).join(sp)}

Where several candidates show the same designs at min and max, they are
correlated and the strata collapse (prompt 52 section 3: made visible).

## 4. Rows ({n}: batch A {n_a}, batch B {n_b}; layout {layout})

{chr(10).join(tab)}

`PEM_fraction = pem_mw / gen_pmax` (renewable; nameplate from the v2 design
matrix) or `pem_mw / {NUC_PMAX}` (nuclear). Exact copies carry the v2 design's
`omega` byte-for-byte. Perturbed copies: `pem_mw x (1 + sign x delta_rel)`,
sign from `numpy.random.default_rng({SEED})` (column `perturb_seed`), inward
at 0 and at nameplate (PICK_RULE.md). `replicate_of` = the v2 origin row for
every copy; `copy_type` tells exact from perturbed. Bid {BID} $/MWh, full
year from {START_DATE}. Retrofit dicts: renewable `{{"<site>": {{"PEM_bid",
"PEM_fraction", "gen_pmax"}}}}`; nuclear `{{"1": {{"PEM_bid", "PEM_fraction"}}}}`
with NO `gen_pmax` key. Nuclear rows: {nuc_line}.

## 5. Batch split — resolution (DEVIATION to confirm)

Prompt 52 section 3 says "4 designs x 3 copies (1 exact + 2 perturbed) ~ 12
runs" in "TWO submission batches"; v2.1 says the exact copies "form the
cross-batch exact pairs between batch A and batch B"; ERCOT_BO_PLAN.md
section 3 pins only "tau population = EXACT cross-batch replicates" and
section 8 counts 12 replicate runs. Under v3 an exact v3 copy has no v3
partner unless a second exact copy runs, so 12 rows cannot hold both 4
cross-batch exact pairs and 8 perturbed copies. Resolution (strategy
session 11-06, layout {layout}): per design, exact in A, exact in B (the
pair), one perturbed in A and one antithetic perturbed in B — batch A {n_a}
rows, batch B {n_b} rows; the ruler population is 8 values (4 designs x 2
copies), exactly the population prompt 57 section 3 A4 pins. At a bound the
antithetic copy cannot step outward, so it steps inward by 2 x delta
(nuclear B:8, delta_rel 0.002) — disclosed in the row table. The thinner
`--layout 12` (A 8, B 4; ruler population 4) is kept in the builder as the
alternative and is NOT the committed wave. `analysis/noise_v3/read_noise.py` reads either.

## 6. Collector and the gz policy

`collect_{WAVE}_<batch>.sh` (held on the batch array; email on this job
only): every row `extract_ercot.py --full` -> `extracts/{WAVE}/<batch>/run_index_N/`,
Prescient `runtimes.csv` per row, wall-clock from the `NOISE_V3_START` /
`NOISE_V3_END` stamps -> `extracts/{WAVE}/<batch>/wallclock.csv`, the identity
line -> `run_index_N/identity.txt`, then ON CRC `python pool_objectives.py
--run-dir <extract> --out <extract>/pool_full_metrics.json` (E8, E9, N5,
headroom, R7/R8, RUC quality, manifest md5s), then the `COLLECTED` marker.
Git receives the SLIM tables + `pool_full_metrics.json` + `runtimes.csv` +
`extract_manifest.json` + `GAP_DECISION_used.json` + `design_matrix_used.csv`
+ `COLLECTED`; the four `*.csv.gz` tables stay UNCOMMITTED
(`trial_0826/ercot/.gitignore`: `extracts/{WAVE}/**/*.csv.gz`; the collector
aborts if a gz is staged).

Storage: {n} x {FULL_EXTRACT_MB} MB = {n * FULL_EXTRACT_MB / 1024:.2f} GB of full extracts on CRC;
about {n * 3} MB in git.

## 7. Expected wall-clock

Projected full-year run at v3: 8–10 h wall / 32–40 core-h at 4 slots
(ERCOT_BO_PLAN.md AMENDMENT 2026-11-06b, from the January smoke days; replace
with wave-D actuals when they land). Batch A: {n_a} x 4 = {4 * n_a} slots; batch B:
{n_b} x 4 = {4 * n_b} slots; no `-tc`. The collector's `wallclock.csv` feeds the
plan section 8 budget actuals (`read_noise.py` prints core-h per run).

## 8. After both batches land (local, zero simulation)

    cd trial_0826/ercot && python analysis/noise_v3/read_noise.py

writes `analysis/noise_v3/ERCOT_NOISE.md` + `ercot_noise.csv/json` +
`ercot_noise_cov.csv` (exact-pair |Δ|, perturbed |Δ| population = ruler_j,
pooled and per-level sd with CIs, per-objective trigger, covariance matrix,
shed ≡ 0 assert, runtime table).

## 9. Local checks (zero simulation)

`bash -n` on the six scripts; `tests/test_make_noise_v3.py` (row counts and
batches, delta inward at the bounds, nuclear dict without `gen_pmax`, pick
table spread columns, GAP_DECISION refusal, batch-B COLLECTED refusal,
`.gitignore` line, committed wave == fresh build).
"""


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--layout", choices=sorted(LAYOUTS), default="16")
    args = ap.parse_args(argv)
    d, rows, picked, table = build(layout=args.layout)
    n = sum(len(v) for v in rows.values())
    print(f"built {d}: layout {args.layout}, rows A={len(rows['A'])} B={len(rows['B'])}")
    for i, p in enumerate(picked, start=1):
        print(f"  D{i}: {p['key']} site {p['site']} {p['unit_type']} {p['pem_mw']:.4f} MW (omega {p['omega']:.6f})")
    print(f"storage: {n} x {FULL_EXTRACT_MB} MB = {n * FULL_EXTRACT_MB / 1024:.2f} GB full extracts on CRC")


if __name__ == "__main__":
    main()
