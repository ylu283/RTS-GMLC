#!/usr/bin/env python3
"""Prompt 53 v3.1 — build `waves/n0_E/` (Sobol initial design) and
`waves/random_E/` (holdout); NOT submitted. Zero simulation.

Design space: `waves/design_space_E.json` (the contract-2026-11-13 freeze,
first commit of ercot/53-design-space). d = 6 WIND sites, per-site box
x_s in [0, gen_pmax_s] MW, u_s = x_s / gen_pmax_s (plan section 2).
gen_pmax and bus are re-read from the wave-D design matrix
(`waves/location_oat_v2/design_matrix.csv`) and asserted equal to the JSON
to 1e-6 at every build.

  n0_E      scipy.stats.qmc.Sobol(d=6, scramble=True, seed=53).random_base2(6)
            = 64 points; rows 0-47 = the grading tier (tier "grading"),
            rows 0-31 = the nav candidates (E-D7: nav = the first 32 or all
            48, decided after prompt 54 Part B); sobol_index recorded.
            Draw-64-then-slice: the 32 / 48 prefixes equal random(32) /
            random(48) of a fresh same-seed generator (random(48) warns on
            balance).
  random_E  numpy.random.default_rng(5353).random((48, 6)), row-major;
            tier "holdout" (plan section 4).

mw_s = u_s * gen_pmax_s, full float precision, no snapping, no minimum MW.
Rows use the existing `__ALL__` multi-site convention (contract section 5):
pool_objectives.design_row()/pem_mw() read them with no change. Retrofit
dict per row: every site with mw_s > 0 -> {"PEM_bid": 40.0, "PEM_fraction":
u_s, "gen_pmax": gen_pmax_s}; mw_s == 0 exactly -> site omitted.

Scripts: the noise_v3 templates (array: -q long, -pe smp 4, -r n, no -tc,
SMOKE_GATE, identity read from waves/GAP_DECISION.json at run time and
refused without it; collector: every row --full, runtimes.csv, wall-clock
stamps, identity.txt, pool_objectives.py --run-dir on CRC, COLLECTED marker,
gz-staged abort, ercot-bot commit + 5-retry push; submit_this.sh: pre-flight,
prints the identity and qquota, literal `yes`), at one directory level
(waves/<wave>, the wave-D depth).
"""
import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import qmc

ERCOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ERCOT / "tools"))
from make_v2_waves import EMAIL, ENV, HEADER, PUSH, V2_DATA_REL, extract_cmd, write  # noqa: E402

PROMPT = "53 v3.1"
DESIGN_SPACE = ERCOT / "waves" / "design_space_E.json"
WAVE_D_DM = ERCOT / "waves" / "location_oat_v2" / "design_matrix.csv"
CONTRACT_VERSION = "2026-11-13"
SOBOL_SEED = 53
SOBOL_M = 6                      # 2**6 = 64 points drawn, then sliced
N_GRADING, N_NAV = 48, 32
RANDOM_SEED = 5353
N_HOLDOUT = 48
START_DATE, NUM_DAYS = "01-01-2019", 365
FULL_EXTRACT_MB = 51
WAVES_E = {"n0_E": "N0_E", "random_E": "RANDOM_E"}   # wave -> stamp prefix

COLS = ["index", "oat_site", "unit_type", "bus", "omega", "bid", "gen_pmax",
        "start_date", "num_days", "replicate_of", "pem_mw", "level_id", "tier",
        "sobol_index"]


# --------------------------------------------------------------------------
# design space
# --------------------------------------------------------------------------
def load_space(path=DESIGN_SPACE, wave_d_dm=WAVE_D_DM):
    """The frozen JSON, cross-checked against wave D's design matrix."""
    with open(path) as f:
        js = json.load(f)
    assert js["contract_version"] == CONTRACT_VERSION and js["identity"] == "v3", js["contract_version"]
    sites = [s["site"] for s in js["sites"]]
    pmax = np.array([float(s["gen_pmax"]) for s in js["sites"]])
    assert js["x_columns"] == [f"mw_{s}" for s in sites], js["x_columns"]
    assert js["bounds_mw_lo"] == [0] * len(sites)
    assert np.array_equal(np.array(js["bounds_mw_hi"], dtype=float), pmax)
    dm = pd.read_csv(wave_d_dm, dtype={"oat_site": str, "unit_type": str})
    for s in js["sites"]:
        r = dm[dm["oat_site"] == s["site"]]
        assert len(r) >= 1, f"site {s['site']} not in wave D"
        assert (abs(r["gen_pmax"].astype(float) - float(s["gen_pmax"])) <= 1e-6).all(), s
        assert (r["bus"].astype(int) == int(s["bus"])).all(), s
        assert (r["unit_type"] == s["unit_type"]).all() and s["unit_type"] == "WIND", s
    return {"json": js, "sites": sites, "pmax": pmax, "bid": float(js["bid"])}


def sobol_u(seed=SOBOL_SEED, d=6, m=SOBOL_M):
    """64 scrambled Sobol points in [0, 1)^d (draw the full base-2 block)."""
    return qmc.Sobol(d=d, scramble=True, seed=seed).random_base2(m)


def random_u(seed=RANDOM_SEED, n=N_HOLDOUT, d=6):
    return np.random.default_rng(seed).random((n, d))


# --------------------------------------------------------------------------
# rows
# --------------------------------------------------------------------------
def make_rows(U, space, tier, sobol_index=None):
    """One `__ALL__` row per u-vector; index = SGE task id (1-based)."""
    sites, pmax, bid = space["sites"], space["pmax"], space["bid"]
    assert U.shape[1] == len(sites) and (U >= 0).all() and (U <= 1).all()
    rows = []
    for i, u in enumerate(U):
        mw = [float(u[j]) * float(pmax[j]) for j in range(len(sites))]
        r = {"index": i + 1, "oat_site": "__ALL__", "unit_type": "", "bus": "",
             "omega": "", "bid": bid, "gen_pmax": "", "start_date": START_DATE,
             "num_days": NUM_DAYS, "replicate_of": "", "pem_mw": math.fsum(mw),   # correctly rounded: same bits on py 3.10 and >= 3.12
             "level_id": "", "tier": tier,
             "sobol_index": (int(sobol_index[i]) if sobol_index is not None else "")}
        for j, s in enumerate(sites):
            r[f"mw_{s}"] = mw[j]
        for j, s in enumerate(sites):
            r[f"u_{s}"] = float(u[j])
        rows.append(r)
    return rows


def retrofit_dict(row, space):
    """{site: {PEM_bid, PEM_fraction = u, gen_pmax}} for every site with
    mw > 0; mw == 0 exactly -> omitted (0 = absent, never omega = 0)."""
    out = {}
    for j, s in enumerate(space["sites"]):
        if row[f"mw_{s}"] > 0.0:
            out[s] = {"PEM_bid": space["bid"], "PEM_fraction": row[f"u_{s}"],
                      "gen_pmax": float(space["pmax"][j])}
    return out


def columns(space):
    return (COLS + [f"mw_{s}" for s in space["sites"]]
            + [f"u_{s}" for s in space["sites"]])


# --------------------------------------------------------------------------
# scripts (noise_v3 templates, one directory level: waves/<wave>)
# --------------------------------------------------------------------------
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
    echo "ABORT task $SGE_TASK_ID: $GAP_FILE absent — %s runs only under a decided identity"; exit 1
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


def array_script(wave, n):
    st = WAVES_E[wave]
    what = ("Sobol initial design (seed 53; grading tier rows 1-48, nav candidates 1-32)"
            if wave == "n0_E" else "random holdout (default_rng(5353); plan section 4)")
    return f"""#!/bin/bash
#$ -N {wave}_array
#$ -q long
#$ -cwd
#$ -t 1-{n}
#$ -pe smp 4
#$ -r n
# Prompt {PROMPT} {wave}: {n} full-year 6-site rows, {what}.
# Design space waves/design_space_E.json. Runs ONLY under the identity in
# waves/GAP_DECISION.json (Kay, E-D6), read at run time below.
{HEADER}{SMOKE_GATE}mkdir -p "$WAVE_DIR/runs"
{ENV}module load gurobi
{GAP_READ % wave}
eval "$(python "$TRIAL_DIR/campaign/get_row.py" "$SGE_TASK_ID" "$WAVE_DIR/design_matrix.csv")"
OUT_PARENT="$WAVE_DIR/runs"
DICT="$WAVE_DIR/retrofit_gen_dict_${{SGE_TASK_ID}}.json"
echo "{st}_TASK=$SGE_TASK_ID dict=$(tr -d '\\n ' < "$DICT")"
echo "{st}_START $(date -u +%FT%TZ) epoch=$(date +%s)"
{RUN}echo "{st}_END $(date -u +%FT%TZ) epoch=$(date +%s)"
"""


def collector_script(wave, n):
    st = WAVES_E[wave]
    check = f"""for i in $(seq 1 {n}); do
    [[ -f "$WAVE_DIR/runs/run_index_$i/overall_simulation_output.csv" ]] || missing="$missing $i"
done"""
    ext = extract_cmd('"$WAVE_DIR/runs/run_index_$i"', '"$EXTR/run_index_$i"', "--full",
                      f'"$WAVE_DIR"/{wave}_array.o*."$i"')
    return f"""#!/bin/bash
#$ -N collect_{wave}
#$ -q long
#$ -cwd
#$ -r n
# Prompt {PROMPT} collector ({wave}): gate -> --full extracts (every row) +
# runtimes.csv + wall-clock + identity.txt -> per-run pool metrics
# (pool_objectives.py --run-dir, ON CRC under PCM_ERCOT) -> COLLECTED marker ->
# ercot-bot commit of the SLIM tables + pool_full_metrics.json + runtimes.csv +
# extract_manifest.json + marker; *.csv.gz stay uncommitted
# (trial_0826/ercot/.gitignore) in $GROUP storage. Email flags are applied by
# submit_this.sh on THIS job only.
{HEADER}{ENV}
{PUSH}
missing=""
{check}
if [[ -n "$missing" ]]; then
    marker="$WAVE_DIR/FAILED_{wave}.md"
    {{ echo "# FAILED — {wave} incomplete"; echo; echo "missing:$missing";
      echo "Generated $(date -u +%FT%TZ)"; }} > "$marker"
    git -C "$REPO_DIR" add -- "$marker"
    git -C "$REPO_DIR" "${{BOT[@]}}" commit -m "ercot-bot: FAILED marker ({wave})"
    push_with_retries
    exit 1
fi
echo "GATE PASS: {n}/{n}"
if [[ -f "$WAVE_DIR/FAILED_{wave}.md" ]]; then
    git -C "$REPO_DIR" rm -q -- "$WAVE_DIR/FAILED_{wave}.md" 2>/dev/null \\
        || rm -f "$WAVE_DIR/FAILED_{wave}.md"
    echo "stale FAILED marker cleared"
fi

EXTR="$ERCOT_DIR/extracts/{wave}"
mkdir -p "$EXTR"
cp -f "$ERCOT_DIR/waves/GAP_DECISION.json" "$EXTR/GAP_DECISION_used.json"
cp -f "$WAVE_DIR/design_matrix.csv" "$EXTR/design_matrix_used.csv"
cp -f "$ERCOT_DIR/waves/design_space_E.json" "$EXTR/design_space_E_used.json"
echo "task,start_epoch,end_epoch,wall_s" > "$EXTR/wallclock.csv"
for i in $(seq 1 {n}); do
{ext}
    cp -f "$WAVE_DIR/runs/run_index_$i/run/runtimes.csv" "$EXTR/run_index_$i/runtimes.csv" \\
        || echo "WARNING: row $i has no Prescient runtimes.csv"
    if [[ -n "$JOBLOG" ]]; then
        S=$(grep -h "{st}_START" "$JOBLOG" | sed -n 's/.*epoch=\\([0-9]*\\).*/\\1/p' | head -1)
        E=$(grep -h "{st}_END" "$JOBLOG" | sed -n 's/.*epoch=\\([0-9]*\\).*/\\1/p' | tail -1)
        echo "$i,${{S:-}},${{E:-}},$(( ${{E:-0}} - ${{S:-0}} ))" >> "$EXTR/wallclock.csv"
        grep -h "IDENTITY from GAP_DECISION.json" "$JOBLOG" > "$EXTR/run_index_$i/identity.txt" || true
    fi
    python "$ERCOT_DIR/pool_objectives.py" --run-dir "$EXTR/run_index_$i" \\
        --out "$EXTR/run_index_$i/pool_full_metrics.json"
done
{{ echo "wave={wave} rows={n} collected_utc=$(date -u +%FT%TZ)";
  echo "head=$(git -C "$REPO_DIR" rev-parse --short HEAD)";
  echo "identity=$(tr -d '\\n' < "$ERCOT_DIR/waves/GAP_DECISION.json")"; }} > "$EXTR/COLLECTED"

# git policy: slim tables + pool_full_metrics.json + runtimes.csv + manifest + marker;
# *.csv.gz are ignored by trial_0826/ercot/.gitignore and asserted absent below.
git -C "$REPO_DIR" add -- "$EXTR"
if git -C "$REPO_DIR" diff --cached --name-only | grep -q '\\.csv\\.gz$'; then
    echo "ABORT: a *.csv.gz is staged — .gitignore line missing?"; git -C "$REPO_DIR" reset -q; exit 1
fi
git -C "$REPO_DIR" "${{BOT[@]}}" commit -m "ercot-bot: {wave} extracts (slim + pool_full_metrics + COLLECTED; gz left in storage)"
push_with_retries
echo "collect_{wave} done"
"""


def submit_script(wave, n):
    return f"""#!/bin/bash
# Prompt {PROMPT} {wave} — run ON CRC (Kay, by hand):
#   cd trial_0826/ercot/waves/{wave} && bash submit_this.sh
# {n} tasks x 4 slots = {4 * n} slots; no -tc. Collector held on the array.
# No dependency on the other E wave (n0_E / random_E): either order, or both.
cd "$(dirname "${{BASH_SOURCE[0]}}")"
set -euo pipefail
E="$(cd ../.. && pwd)"
W="$E/waves"
REPO_DIR="$(cd ../../../.. && pwd)"
BRANCH="$(git -C "$REPO_DIR" branch --show-current)"
[[ "$BRANCH" == "ercot/tx123" ]] || {{ echo "ABORT: on '$BRANCH', expected ercot/tx123"; exit 1; }}
git -C "$REPO_DIR" pull --rebase --autostash origin ercot/tx123
[[ -f "$W/GAP_DECISION.json" ]] || {{ echo "ABORT: waves/GAP_DECISION.json absent — decide E-D6 first (read analysis/gap_smoke/GAP_SMOKE.md)"; exit 1; }}
[[ -f "$W/smoke_v2/SMOKE_PASS" ]] || {{ echo "ABORT: waves/smoke_v2/SMOKE_PASS absent — smoke gate not passed"; exit 1; }}
[[ -f "$W/design_space_E.json" ]] || {{ echo "ABORT: waves/design_space_E.json absent — the design-space freeze is not in HEAD"; exit 1; }}
[[ -f "$E/{V2_DATA_REL}/gen.csv" ]] || {{ echo "ABORT: v2 data dir missing"; exit 1; }}
grep -q -- "--ruc_mipgap" "$E/run_ercot_pcm.py" || {{ echo "ABORT: run_ercot_pcm.py has no --ruc_mipgap"; exit 1; }}
grep -q "extracts/{wave}/\\*\\*/\\*.csv.gz" "$E/.gitignore" || {{ echo "ABORT: trial_0826/ercot/.gitignore gz line missing"; exit 1; }}
[[ -f design_matrix.csv && -f retrofit_gen_dict_{n}.json ]] || {{ echo "ABORT: {wave} files missing"; exit 1; }}
echo "--- waves/GAP_DECISION.json (the identity {wave} will run under; eyeball it) ---"
cat "$W/GAP_DECISION.json"
echo "-----------------------------------------------------------------------------"
echo "--- qquota (need {4 * n} slots for {n} tasks x 4) ---"; qquota -u ylu28 || true
read -r -p "Submit {n} full-year 6-site rows ({wave}) under this identity? [yes/NO] " ANS
[[ "$ANS" == "yes" ]] || {{ echo "not submitted"; exit 1; }}
J=$(qsub -terse {wave}_array.sh | cut -d. -f1)
[[ "$J" =~ ^[0-9]+$ ]] || {{ echo "BAD ARRAY JID: $J"; exit 1; }}
C=$(qsub -terse -hold_jid "$J" -cwd -M {EMAIL} -m ea collect_{wave}.sh)
[[ "$C" =~ ^[0-9]+$ ]] || {{ echo "BAD COLLECTOR JID: $C"; exit 1; }}
echo "SUBMITTED {wave}: array=$J ({n} tasks x 4 slots) collector=$C"
qstat -u ylu28
"""


# --------------------------------------------------------------------------
# build
# --------------------------------------------------------------------------
def wave_rows(space):
    """{wave: rows}: n0_E = Sobol rows 0-47 of the 64-point block; random_E = 48 iid."""
    S = sobol_u()
    assert S.shape == (2 ** SOBOL_M, len(space["sites"]))
    n0 = make_rows(S[:N_GRADING], space, "grading", sobol_index=range(N_GRADING))
    rnd = make_rows(random_u(d=len(space["sites"])), space, "holdout")
    return {"n0_E": n0, "random_E": rnd}


def build(waves=ERCOT / "waves", design_space=DESIGN_SPACE, wave_d_dm=WAVE_D_DM):
    space = load_space(design_space, wave_d_dm)
    rows = wave_rows(space)
    cols = columns(space)
    for wave, rs in rows.items():
        d = waves / wave
        d.mkdir(parents=True, exist_ok=True)
        pd.DataFrame(rs, columns=cols).to_csv(d / "design_matrix.csv", index=False)
        for r in rs:
            write(d / f"retrofit_gen_dict_{r['index']}.json",
                  json.dumps(retrofit_dict(r, space), indent=2) + "\n", 0o644)
        n = len(rs)
        write(d / f"{wave}_array.sh", array_script(wave, n))
        write(d / f"collect_{wave}.sh", collector_script(wave, n))
        write(d / "submit_this.sh", submit_script(wave, n))
        write(d / "README.md", readme(wave, rs, space), 0o644)
    return rows, space


def _u_table(rs, space):
    sites = space["sites"]
    head = ("| index | " + ("sobol_index | " if rs[0]["sobol_index"] != "" else "")
            + " | ".join(f"u_{s}" for s in sites) + " | pem_mw (MW) | sites present |")
    sep = "|" + "---|" * (head.count("|") - 1)
    out = [head, sep]
    for r in rs:
        present = sum(r[f"mw_{s}"] > 0 for s in sites)
        out.append(f"| {r['index']} | " + (f"{r['sobol_index']} | " if r["sobol_index"] != "" else "")
                   + " | ".join(f"{r[f'u_{s}']:.4f}" for s in sites)
                   + f" | {r['pem_mw']:.2f} | {present} |")
    return "\n".join(out)


def _min_u(rs, space):
    best = None
    for r in rs:
        for j, s in enumerate(space["sites"]):
            v = (r[f"u_{s}"], r["index"], s, r[f"mw_{s}"])
            best = v if best is None or v < best else best
    return best


BUDGET = """## Budget (wave-D actuals, `analysis/pool/ERCOT_POOL_STANDINGS.md` section 8)

Per full-year v3 run at 4 slots: fast node ≈ 5.3 h wall / 21 core-h
(15 of 21 wave-D rows); slow node 10.5–11.8 h / 44.6 core-h mean (6 rows).
The plan section 8 projection was 32–40 core-h (AMENDMENT 2026-11-06b,
January days). n0_E + random_E = 96 runs ≈ 2.0k (all fast) – 4.3k (all
slow) core-h; this wave is 48 runs ≈ 1.0k – 2.1k core-h, 192 slots, about
5–12 h calendar if the queue grants the slots at once. Both E waves can run
concurrently with each other and with noise_v3 B and base_v3.

Storage: 96 x {mb} MB ≈ 4.9 GB of `--full` extracts in $GROUP storage for the
two E waves (this wave: 48 x {mb} MB ≈ 2.4 GB; wave D was 1.07 GB). `--full`
is kept because E8 / E9 / N5 and the headroom diagnostics need `bus_lmps` /
`thermal`; `line_summary.csv` (N1) is written in slim mode too
(`extract_ercot.py:245`). About 3 MB per row in git.
""".format(mb=FULL_EXTRACT_MB)


def readme(wave, rs, space):
    n = len(rs)
    sites = space["sites"]
    mu = _min_u(rs, space)
    npres = [sum(r[f"mw_{s}"] > 0 for s in sites) for r in rs]
    bounds = "\n".join(f"| {s} | {space['json']['sites'][j]['bus']} | {space['pmax'][j]!r} |"
                       for j, s in enumerate(sites))
    if wave == "n0_E":
        draw = f"""## Draw (pinned)

    from scipy.stats import qmc
    S = qmc.Sobol(d=6, scramble=True, seed={SOBOL_SEED}).random_base2({SOBOL_M})   # 64 x 6 in [0, 1)
    U = S[:{N_GRADING}]                                                     # this wave

- Rows 1–{N_GRADING} = `sobol_index` 0–{N_GRADING - 1} = the **grading tier** (`tier =
  "grading"` on every row). Rows 1–{N_NAV} (`sobol_index` 0–{N_NAV - 1}) are the **nav
  candidates**: E-D7 (decided after prompt 54 Part B) sets nav = the first
  {N_NAV} or all {N_GRADING}. Nav ⊂ grading, so `tier` cannot carry nav without
  making a 32/48 choice early; nav membership is `sobol_index < {N_NAV}` (or
  `< {N_GRADING}`). Disclosed resolution of contract section 5 (`tier ∈ {{nav,
  grading, holdout, bo}}`).
- Draw-64-then-slice: the first-{N_NAV} / first-{N_GRADING} prefixes of `random_base2({SOBOL_M})` equal
  `random({N_NAV})` / `random({N_GRADING})` from a fresh same-seed generator (asserted in
  `tests/test_make_ercot_n0.py`); `random({N_GRADING})` alone raises scipy's balance
  warning. Rows 48–63 of the block are not used here.
- Pinned env: scipy 1.15.3 (`bogp-botorch`). The draw is bit-identical under
  scipy 1.16.3 (`/opt/anaconda3`, the test interpreter), checked 2026-11-13.
"""
        extra = ""
    else:
        draw = f"""## Draw (pinned)

    import numpy
    rng = numpy.random.default_rng({RANDOM_SEED})
    U = rng.random(({N_HOLDOUT}, 6))          # row-major: row i = site columns in JSON order

i.i.d. uniform over the frozen per-site box (plan section 4); `tier =
"holdout"`, `sobol_index` empty.
"""
        extra = f"""## Holdout rules (plan section 4; pinned AT GENERATION TIME)

- **cov95 bar:** `scipy.stats.binom.interval(0.90, {N_HOLDOUT}, 0.95)` = **[43, 48]**
  (α = 0.10). Trap: `common.binom_band()` defaults to level 0.95 → [42, 48],
  which is wrong here; pass `level = 0.90`.
- **Independence disclosure:** the {N_HOLDOUT} residuals share one fitted model,
  so the binomial region treats them as independent. This is an
  approximation.
- **Exposure budget:** at most **24** model–holdout scorings in total (one
  scoring = one committed config × one objective × one n0 tier).
- **Retirement:** after 24 scorings, or after prompt 54's committed-config
  grading (`analysis/ercot_gp/committed_configs.json` written), whichever
  comes first. After retirement only deterministic replays of recorded
  scorings are allowed.
- **E-D2 dual role:** random_E is also the random-baseline pool (plan
  section 7). Baseline gradings (model-free, prompt-34 percentile) do NOT
  count against the exposure budget. A model change informed by a baseline
  result is banned.
"""
    return f"""# {wave} — ERCOT {'Sobol initial design' if wave == 'n0_E' else 'random holdout'} (prompt {PROMPT}; built 2026-11-13, NOT submitted)

Built by `tools/make_ercot_n0.py` (zero simulation). Design space
`waves/design_space_E.json` (contract {CONTRACT_VERSION}; `waves/DESIGN_SPACE_E.md`).
Kay submits ON CRC, after the wave commit is on `ercot/tx123`:

    cd trial_0826/ercot/waves/{wave} && bash submit_this.sh

`submit_this.sh` checks the branch, pulls, refuses without
`waves/GAP_DECISION.json`, `waves/smoke_v2/SMOKE_PASS`,
`waves/design_space_E.json`, the v2 data or the `.gitignore` gz line, prints
the identity and `qquota`, and asks for a literal `yes` before `qsub`. No
dependency between n0_E and random_E.

## Space (d = 6; per-site box [0, gen_pmax] MW; bid 40 $/MWh; 2019 full year)

| site | bus | gen_pmax = upper bound (MW) |
|---|---|---|
{bounds}

`gen_pmax` / `bus` asserted equal (1e-6) to the wave-D design matrix at
build. u_s = mw_s / gen_pmax_s = `PEM_fraction`.

{draw}
## Rows ({n}; `__ALL__` multi-site schema, contract section 5)

`design_matrix.csv` columns: `{", ".join(columns(space))}`.
`oat_site = "__ALL__"`, `unit_type` / `bus` / `omega` / `gen_pmax` /
`level_id` / `replicate_of` empty, `bid = 40.0`, `pem_mw = Σ mw_s` (equals
`pool_objectives.pem_mw()` on the retrofit dict), `mw_s = u_s · gen_pmax_s` at
full float precision (17-digit reprs; read with `pd.read_csv(...,
float_precision="round_trip")` for bit-exact values, the default parser is
off by ≤ 1 ulp): no rounding, no snapping, no minimum MW. Retrofit dict
`retrofit_gen_dict_<index>.json` = `{{"<site>": {{"PEM_bid": 40.0,
"PEM_fraction": u_s, "gen_pmax": gen_pmax_s}}}}` for every site with mw_s > 0;
a site with mw_s == 0 exactly would be omitted (plan section 2: 0 = absent).
Sites present per row: min {min(npres)}, max {max(npres)} (no draw lands on 0).

**Smallest PEM disclosed:** u = {mu[0]:.4g} at row {mu[1]}, site {mu[2]} →
{mu[3]:.4f} MW. Every PEM term scales to 0 with MW; the only non-scaling
effect is the structural `_PEM` twin unit (MIP-path noise within the v3 gap):
`DESIGN_SPACE_E.md` section 5.

{_u_table(rs, space)}

{extra}## Identity (v3)

Every run reads `--ruc_mipgap` / `--ruc_time_limit` from
`waves/GAP_DECISION.json` at RUN time (0.001 / 1200; Kay, E-D6, 2026-11-06),
prints `IDENTITY from GAP_DECISION.json: ...` into the task log (the collector
copies it to `run_index_N/identity.txt`, which the prompt-54 loader requires),
and refuses without the file. SMOKE_GATE on `waves/smoke_v2/SMOKE_PASS`.

## Collector and the gz policy

`collect_{wave}.sh` (held on the array; email on this job only): every row
`extract_ercot.py --full` → `extracts/{wave}/run_index_N/`, Prescient
`runtimes.csv`, wall-clock from the `{WAVES_E[wave]}_START` / `{WAVES_E[wave]}_END` stamps →
`extracts/{wave}/wallclock.csv`, the identity line → `identity.txt`, then ON
CRC `pool_objectives.py --run-dir <extract> --out <extract>/pool_full_metrics.json`,
then `COLLECTED`. Git receives the slim tables + `pool_full_metrics.json` +
`runtimes.csv` + `extract_manifest.json` + `GAP_DECISION_used.json` +
`design_matrix_used.csv` + `design_space_E_used.json` + `COLLECTED`; the four
`*.csv.gz` tables stay uncommitted (`.gitignore`:
`extracts/{wave}/**/*.csv.gz`; the collector aborts if one is staged).
Objectives come from `pool_objectives.pool_row(key)` on the slim tables
(prompt 54 loader), never from `pool_full_metrics.json`.

{BUDGET}
## Local checks (zero simulation)

`bash -n` on the scripts; `/opt/anaconda3/bin/python -m pytest
tests/test_make_ercot_n0.py tests/test_pool_objectives.py -q`.

## Deviations

- `tier` is "grading" on all 48 n0_E rows; nav membership is carried by
  `sobol_index` until E-D7 (above).
- The scripts are the noise_v3 templates at the wave-D directory depth
  (`waves/<wave>`, `HEADER` from `make_v2_waves.py`); the nuclear T0-fix
  ancestor check is dropped (no nuclear rows) and a `design_space_E.json`
  presence check is added. The collector also copies `design_space_E.json`
  into the extract.
"""


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.parse_args(argv)
    rows, space = build()
    for wave, rs in rows.items():
        mu = _min_u(rs, space)
        print(f"built waves/{wave}: {len(rs)} rows; min u {mu[0]:.4g} (row {mu[1]}, site {mu[2]}, {mu[3]:.4f} MW)")
    n = sum(len(v) for v in rows.values())
    print(f"storage: {n} x {FULL_EXTRACT_MB} MB = {n * FULL_EXTRACT_MB} MB (~{n * FULL_EXTRACT_MB / 1000:.1f} GB) full extracts on CRC")


if __name__ == "__main__":
    main()
