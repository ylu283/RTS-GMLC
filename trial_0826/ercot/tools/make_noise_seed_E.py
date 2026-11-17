#!/usr/bin/env python3
"""Prompt 63 v1 Part B — build `waves/noise_seed_E/` (18 analysis-only runs); NOT submitted.

Gurobi-Seed replicates at 4 n0_E designs + 2 thread checks. Zero simulation.

Design pick (pre-registered, X ONLY): the 4 rows of `waves/n0_E/design_matrix.csv`
whose total T = `pem_mw` is nearest to the 10 / 37 / 63 / 90 % quantiles of T over
the 48 rows (`numpy.quantile`, default method "linear" = Hyndman-Fan type 7; ties
-> lower `index`). Nothing else of n0_E is read: no extract, no landing file, no Y.
Their retrofit dicts are copied verbatim from `waves/n0_E/retrofit_gen_dict_<idx>.json`
(md5 asserted equal).

Rows (18; `__ALL__` schema, contract section 5 + 11-17 addendum: `tier =
"contrast"`, `sobol_index` empty, `replicate_of = n0_E:<idx>`, `level_id` = the row
label; new columns `seed`, `ruc_threads`):
  1-16  the 4 designs x Gurobi Seed in {1, 2, 3, 4}, Threads 4 (Seed 0 = the n0_E run)
  17    the 37 %-quantile design, Threads 8, Seed 0
  18    the 37 %-quantile design, Threads 1, Seed 0

Seed reaches Gurobi as `--ruc_solver_option Seed=<k>` (run_ercot_pcm.py refuses only
MIPGap / TimeLimit keys; the wrapper prints `ruc_solver_options=` in the job log). A
Seed-0 row passes no Seed option (the n0_E path exactly).

Slots: ONE array script, submitted three times by submit_this.sh with command-line
`-t` / `-pe smp` (qsub command-line options override the embedded `#$` lines):
`-t 1-16 -pe smp 4`, `-t 17-17 -pe smp 8`, `-t 18-18 -pe smp 1`. The task refuses to
run if `$NSLOTS` differs from its row's `ruc_threads`.

Reuses `tools/make_ercot_n0.py` per prompt 61 section 2.3: `load_space, make_rows,
retrofit_dict, columns, array_script, collector_script, submit_script`; a runtime
`mk.WAVES_E.setdefault(...)` key only (never `mk.PROMPT` or any other global); every
template change is a `str.replace` asserted to hit exactly once; own `build` / `readme`.
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ERCOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ERCOT / "tools"))
import make_ercot_n0 as mk  # noqa: E402
from make_v2_waves import write  # noqa: E402

WAVE = "noise_seed_E"
STAMP = "NOISE_SEED_E"
PROMPT_TAG = "63 v1"
N0_DIR = ERCOT / "waves" / "n0_E"
DESIGN_SPACE_1113 = ERCOT / "waves" / "design_space_E.json"     # the 2026-11-13 freeze (load_space asserts it)
GITIGNORE_LINE = "extracts/noise_seed_E/**/*.csv.gz"
QUANTILES = (0.10, 0.37, 0.63, 0.90)
QUANTILE_METHOD = "linear"
SEEDS = (1, 2, 3, 4)
BASE_THREADS = 4
THREAD_ROWS = (8, 1)
THREAD_Q = 0.37
EXTRA_COLS = ["seed", "ruc_threads"]
CORE_H_RUN = (21.1, 44.6)                                       # fast / slow node per run at 4 slots (AMENDMENT 2026-11-16)

# Part C reads — prompt 63 v1 section 3, copied VERBATIM (frozen with the wave commit)
PART_C = """Per graded candidate j (28 ids; D3 as check):
- **Chatter sd per design:** `σ̂_c,j(d)` = sd (ddof 1) over the 5 solves
  (Seed 0–4) of design d; pooled `σ̂_c,j` over the 4 designs (df 16);
  heteroscedasticity: ratio max/min across designs and vs T (trigger
  rule of 52 §3 reused).
- **Chatter covariance Σ_c** (28 × 28, from the 16 deltas vs the Seed-0
  value) with Ledoit–Wolf shrinkage; its V1/E1/R4/N1 block feeds τ_res.
- **Assumption A3 test:** `σ̂_c,j` vs the ±0.1 % perturbed amplitude
  (D2 excluded): AGREE iff within 2×; otherwise the perturbed ruler is
  labelled "perturbation response, not chatter" and B_j is redefined on
  Seed chatter (strategy session amends 61 / 62 before their landing
  reads; if they have already read, both bars are reported).
- **Thread check:** Threads 8 / 1 vs Threads 4 — bit-identical or not;
  the conditions sentence in `ERCOT_NOISE.md` is updated either way.
- **Bars:** `B_j^seed = max(3·σ̂_c,j·√2, max|Δ_seed|)` (two-run
  contrast scale); printed beside `B_j` (perturbed, D2 excluded). Which
  bar 61 / 62 use is fixed by the A3 outcome above, recorded once.
- **τ_res:** §6.2 recipe with Σ_c at the n0_E nav starts; report-only
  next to τ_exact = 0; gain/τ_res columns for 49-style reading of the
  E campaign later.
- **54 input:** `σ̂_c,j` as the measured floor candidate (54's arm "floor
  = measured iff sd > 0 and df ≥ 3" becomes live: df = 16); 54 records
  this as a §10-amended arm input, not a new arm.
- Deliverables: `analysis/noise_v3/NOISE_SEED_E.md` + csv/json
  (`ercot_noise_seed.json`: per-candidate σ̂_c, Σ_c, A3 verdict, B_j^seed,
  τ_res); figures bold labels AND ticks, assert-before-draw; plan
  amendment (actuals + the A3 verdict) as a separate last commit."""


# --------------------------------------------------------------------------
# pick + rows
# --------------------------------------------------------------------------
def read_n0_x(n0_dir=N0_DIR):
    """The n0_E design matrix: X columns only (index, pem_mw, mw_*, u_*)."""
    dm = pd.read_csv(n0_dir / "design_matrix.csv", dtype={"oat_site": str, "tier": str},
                     float_precision="round_trip")
    assert len(dm) == 48 and list(dm["index"]) == list(range(1, 49)), "n0_E must be the 48-row grading tier"
    return dm


def pick_designs(dm, quantiles=QUANTILES, method=QUANTILE_METHOD):
    """Nearest row to each quantile of T = pem_mw (ties -> lower index); distinct rows asserted."""
    T = dm["pem_mw"].to_numpy(float)
    idx = dm["index"].to_numpy(int)
    out = []
    for q in quantiles:
        t = float(np.quantile(T, q, method=method))
        d = np.abs(T - t)
        order = sorted(range(len(T)), key=lambda i: (d[i], idx[i]))
        i = order[0]
        out.append({"q": q, "label": f"q{int(round(q * 100)):02d}", "target_T": t, "index": int(idx[i]),
                    "T": float(T[i]), "abs_dist": float(d[i]), "runner_up_index": int(idx[order[1]]),
                    "runner_up_dist": float(d[order[1]])})
    assert len({p["index"] for p in out}) == len(out), f"two quantiles picked the same row: {out}"
    return out


def make_wave_rows(dm, picks, space):
    """18 rows: picks x SEEDS at BASE_THREADS, then the THREAD_Q design at THREAD_ROWS (Seed 0)."""
    sites = space["sites"]
    by = {int(r["index"]): r for _, r in dm.iterrows()}
    plan = [(p, k, BASE_THREADS, f"{p['label']}_seed{k}") for p in picks for k in SEEDS]
    pt = [p for p in picks if p["q"] == THREAD_Q]
    assert len(pt) == 1
    plan += [(pt[0], 0, th, f"{pt[0]['label']}_threads{th}") for th in THREAD_ROWS]
    U = np.array([[float(by[p["index"]][f"u_{s}"]) for s in sites] for p, _, _, _ in plan])
    rows = mk.make_rows(U, space, "contrast")
    for r, (p, k, th, lab) in zip(rows, plan):
        src = by[p["index"]]
        for s in sites:                                   # u * pmax reproduces n0_E's mw bit-for-bit
            assert r[f"mw_{s}"] == float(src[f"mw_{s}"]), (lab, s, r[f"mw_{s}"], src[f"mw_{s}"])
        assert r["pem_mw"] == float(src["pem_mw"]), (lab, r["pem_mw"], src["pem_mw"])
        r["replicate_of"] = f"n0_E:{p['index']}"
        r["level_id"] = lab
        r["sobol_index"] = ""
        r["seed"] = int(k)
        r["ruc_threads"] = int(th)
    return rows


def md5(p):
    return hashlib.md5(Path(p).read_bytes()).hexdigest()


# --------------------------------------------------------------------------
# scripts (make_ercot_n0 templates + asserted replacements)
# --------------------------------------------------------------------------
def _rep(text, old, new):
    assert text.count(old) == 1, (old, text.count(old))
    return text.replace(old, new)


ROW_READ = """eval "$(python "$TRIAL_DIR/campaign/get_row.py" "$SGE_TASK_ID" "$WAVE_DIR/design_matrix.csv")"
# --- prompt 63: Gurobi Seed + Threads from this row; the slot count must match ---
read -r SEED RUC_THREADS < <(python - "$SGE_TASK_ID" "$WAVE_DIR/design_matrix.csv" <<'PY'
import csv, sys
t = int(sys.argv[1])
rows = [r for r in csv.DictReader(open(sys.argv[2])) if int(float(r["index"])) == t]
assert len(rows) == 1, (t, len(rows))
s, th = int(rows[0]["seed"]), int(rows[0]["ruc_threads"])
assert 0 <= s <= 2000000000 and th in (1, 4, 8), (s, th)
print(s, th)
PY
)
[[ -n "$SEED" && -n "$RUC_THREADS" ]] || { echo "ABORT: seed / ruc_threads unreadable"; exit 1; }
if [[ "${NSLOTS:-}" != "$RUC_THREADS" ]]; then
    echo "slots ${NSLOTS:-unset} != ruc_threads $RUC_THREADS" > "$WAVE_DIR/FAILED_task_${SGE_TASK_ID}_slots.md"
    echo "ABORT task $SGE_TASK_ID: NSLOTS=${NSLOTS:-unset} but the row asks ruc_threads=$RUC_THREADS (submit_this.sh sets -pe smp per row group)"; exit 1
fi
SEED_OPT=()
if [[ "$SEED" != "0" ]]; then SEED_OPT=(--ruc_solver_option "Seed=$SEED"); fi
# --- determinism conditions (prompt 63 A4; memo F8), logged before the run ---
echo "%(st)s_HOST $(hostname)"
echo "%(st)s_CPU $(lscpu 2>/dev/null | grep 'Model name' | sed 's/  */ /g' || true)"
GRB_VERSION=$(python -c 'import gurobipy; print(gurobipy.gurobi.version())' 2>&1 || true)
echo "%(st)s_GUROBI $GRB_VERSION"
echo "%(st)s_THREADS ruc_threads=$RUC_THREADS nslots=${NSLOTS:-unset} seed=$SEED"
CODE_SHAS=$(python - 2>&1 <<'PY' || true
import os, subprocess
out = []
for m in ("prescient", "egret"):
    try:
        mod = __import__(m)
        d = os.path.dirname(os.path.realpath(mod.__file__))
        sha = subprocess.run(["git", "-C", d, "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()
        out.append(f"{m}={sha or 'unknown'}")
    except Exception as e:  # noqa: BLE001
        out.append(f"{m}=unknown({type(e).__name__})")
print(" ".join(out))
PY
)
echo "%(st)s_CODE $CODE_SHAS repo=$(git -C "$REPO_DIR" rev-parse --short HEAD 2>/dev/null || echo unknown)"
""" % {"st": STAMP}

GAP_LINE = 'echo "IDENTITY from GAP_DECISION.json:'


def array_text():
    t = mk.array_script(WAVE, 18)
    t = _rep(t, "Prompt 53 v3.1", f"Prompt {PROMPT_TAG}")
    t = _rep(t, "random holdout (default_rng(5353); plan section 4)",
             "analysis-only Gurobi-Seed / thread replicates at 4 n0_E designs (prompt 63; new Y at existing n0_E X; "
             "never in the GP training set, the HV ledger or the baseline)")
    t = _rep(t, "#$ -t 1-18\n", "#$ -t 1-16\n")
    t = _rep(t, "# Design space waves/design_space_E.json.",
             "# Rows 17-18 (Threads 8 / 1) are submitted by submit_this.sh with -t 17-17 -pe smp 8 and\n"
             "# -t 18-18 -pe smp 1 (command-line options override the #$ lines above); every task\n"
             "# refuses to run unless NSLOTS equals its row's ruc_threads.\n"
             "# Design space waves/design_space_E.json.")
    t = _rep(t, 'eval "$(python "$TRIAL_DIR/campaign/get_row.py" "$SGE_TASK_ID" "$WAVE_DIR/design_matrix.csv")"\n',
             ROW_READ)
    t = _rep(t, "    --ruc_threads 4 \\\n",
             '    --ruc_threads "$RUC_THREADS" \\\n    ${SEED_OPT[@]+"${SEED_OPT[@]}"} \\\n')
    t = _rep(t, f'echo "{STAMP}_TASK=$SGE_TASK_ID dict=',
             f'echo "{STAMP}_TASK=$SGE_TASK_ID seed=$SEED ruc_threads=$RUC_THREADS dict=')
    for bad in ("Sobol", "holdout", "--ruc_threads 4"):
        assert bad not in t, bad
    return t


def collector_text():
    t = mk.collector_script(WAVE, 18)
    t = _rep(t, "Prompt 53 v3.1", f"Prompt {PROMPT_TAG}")
    t = _rep(t, '        grep -h "IDENTITY from GAP_DECISION.json" "$JOBLOG" > "$EXTR/run_index_$i/identity.txt" || true\n',
             '        grep -h "IDENTITY from GAP_DECISION.json" "$JOBLOG" > "$EXTR/run_index_$i/identity.txt" || true\n'
             f'        grep -h -e "^{STAMP}_" -e "^run_ercot_pcm: index=" "$JOBLOG" > "$EXTR/run_index_$i/conditions.txt" || true\n')
    for bad in ("Sobol", "holdout"):
        assert bad not in t, bad
    return t


SUBMIT_OLD = """J=$(qsub -terse {w}_array.sh | cut -d. -f1)
[[ "$J" =~ ^[0-9]+$ ]] || {{ echo "BAD ARRAY JID: $J"; exit 1; }}
C=$(qsub -terse -hold_jid "$J" -cwd -M {e} -m ea collect_{w}.sh)
[[ "$C" =~ ^[0-9]+$ ]] || {{ echo "BAD COLLECTOR JID: $C"; exit 1; }}
echo "SUBMITTED {w}: array=$J (18 tasks x 4 slots) collector=$C"
"""
SUBMIT_NEW = """J1=$(qsub -terse -t 1-16 -pe smp 4 {w}_array.sh | cut -d. -f1)
[[ "$J1" =~ ^[0-9]+$ ]] || {{ echo "BAD ARRAY JID (rows 1-16): $J1"; exit 1; }}
J2=$(qsub -terse -t 17-17 -pe smp 8 {w}_array.sh | cut -d. -f1)
[[ "$J2" =~ ^[0-9]+$ ]] || {{ echo "BAD ARRAY JID (row 17, Threads 8): $J2"; exit 1; }}
J3=$(qsub -terse -t 18-18 -pe smp 1 {w}_array.sh | cut -d. -f1)
[[ "$J3" =~ ^[0-9]+$ ]] || {{ echo "BAD ARRAY JID (row 18, Threads 1): $J3"; exit 1; }}
C=$(qsub -terse -hold_jid "$J1,$J2,$J3" -cwd -M {e} -m ea collect_{w}.sh)
[[ "$C" =~ ^[0-9]+$ ]] || {{ echo "BAD COLLECTOR JID: $C"; exit 1; }}
echo "SUBMITTED {w}: rows 1-16 = $J1 (4 slots each), row 17 = $J2 (8 slots), row 18 = $J3 (1 slot); collector=$C"
"""


def submit_text():
    t = mk.submit_script(WAVE, 18)
    t = _rep(t, "Prompt 53 v3.1", f"Prompt {PROMPT_TAG}")
    t = _rep(t, "# No dependency on the other E wave (n0_E / random_E): either order, or both.",
             "# Analysis-only; no dependency on n0_E / random_E / methods_E (the Seed-0 anchors are the n0_E runs).")
    t = _rep(t, "# 18 tasks x 4 slots = 72 slots; no -tc. Collector held on the array.",
             "# 16 tasks x 4 slots + 1 x 8 + 1 x 1 = 73 slots (three submissions of one array\n"
             "# script, -t / -pe smp on the command line); no -tc. Collector held on all three.")
    t = _rep(t, "need 72 slots for 18 tasks x 4", "need 73 slots: 16 x 4 + 8 + 1")
    t = _rep(t, SUBMIT_OLD.format(w=WAVE, e=mk.EMAIL), SUBMIT_NEW.format(w=WAVE, e=mk.EMAIL))
    for bad in ("Sobol", "holdout"):
        assert bad not in t, bad
    return t


# --------------------------------------------------------------------------
# README + build
# --------------------------------------------------------------------------
def readme(picks, rows, space, n0_md5):
    sites = space["sites"]
    pk = "\n".join(
        f"| {p['label']} ({int(p['q'] * 100)} %) | {p['target_T']:.3f} | {p['index']} | {p['T']:.3f} | {p['abs_dist']:.3f} | "
        f"{p['runner_up_index']} ({p['runner_up_dist']:.3f}) | " + " | ".join(
            f"{float(r[f'mw_{s}']):.3f}" for s in sites for r in [next(x for x in rows if x['replicate_of'] == f"n0_E:{p['index']}")])
        + f" | `{n0_md5[p['index']][:8]}` |"
        for p in picks)
    rt = "\n".join(f"| {r['index']} | {r['level_id']} | {r['replicate_of']} | {r['seed']} | {r['ruc_threads']} | "
                   f"{r['pem_mw']:.3f} | {'--ruc_solver_option Seed=' + str(r['seed']) if r['seed'] else '(none: Gurobi default Seed 0)'} | "
                   f"{'-t 1-16 -pe smp 4' if r['index'] <= 16 else ('-t 17-17 -pe smp 8' if r['ruc_threads'] == 8 else '-t 18-18 -pe smp 1')} |"
                   for r in rows)
    lo, hi = CORE_H_RUN
    return f"""# noise_seed_E — Gurobi-Seed replicates + thread checks at 4 n0_E designs (prompt {PROMPT_TAG}; NOT submitted)

Built by `tools/make_noise_seed_E.py` (zero simulation). **ANALYSIS-ONLY:**
new Y at existing n0_E X; these rows never enter the GP training set, the HV
ledger, the random baseline or any validation tier (`tier = "contrast"`,
contract 11-17 addendum). Kay submits ON CRC, after the wave commit is on
`ercot/tx123`:

    cd trial_0826/ercot/waves/{WAVE} && bash submit_this.sh

`submit_this.sh` checks the branch, pulls, refuses without
`waves/GAP_DECISION.json`, `waves/smoke_v2/SMOKE_PASS`,
`waves/design_space_E.json`, the v2 data or the `.gitignore` gz line
(`{GITIGNORE_LINE}`, pre-seeded), prints the identity and `qquota`, and asks
for a literal `yes` before `qsub`.

## Design pick (pre-registered; X only)

The 4 rows of `waves/n0_E/design_matrix.csv` whose total T = `pem_mw` is
nearest to the 10 / 37 / 63 / 90 % quantiles of T over the 48 rows; ties →
lower `index`. Quantile = `numpy.quantile(T, q)` with the default method
"{QUANTILE_METHOD}" (Hyndman–Fan type 7). Only `index`, `pem_mw`, `mw_*`, `u_*`
and the retrofit dicts of n0_E were read; no n0_E extract, landing file or
objective value. The Seed-0 Y of each design (the n0_E run itself) is read
only in Part C, as the replicate anchor.

| quantile | target T (MW) | n0_E index | T (MW) | distance to target (MW) | runner-up index (distance) | {" | ".join(f"mw_{s}" for s in sites)} | dict md5 |
|---|---|---|---|---|---|{"---|" * len(sites)}---|
{pk}

Retrofit dicts: `retrofit_gen_dict_<row>.json` here is a byte copy of
`waves/n0_E/retrofit_gen_dict_<n0_E index>.json` (md5 asserted at build and in
the tests).

## Rows (18; `__ALL__` schema, contract section 5 + 11-17 addendum)

`design_matrix.csv` columns: `{", ".join(mk.columns(space) + EXTRA_COLS)}`.
`tier = "contrast"`, `sobol_index` empty, `replicate_of = n0_E:<index>`,
`level_id` = the row label, `mw_*` / `u_*` / `pem_mw` equal to the n0_E row
bit-for-bit (asserted). New columns: `seed` (Gurobi `Seed`) and `ruc_threads`
(Gurobi `Threads` = SGE slots).

| row | label | replicate_of | seed | ruc_threads | pem_mw (MW) | Seed option | qsub group |
|---|---|---|---|---|---|---|---|
{rt}

Rows 1–16: the 4 designs × Seed ∈ {{1, 2, 3, 4}} at Threads 4; the default
Seed 0 is the n0_E run itself, so each design has 5 solves. Rows 17–18: the
37 %-quantile design at Threads 8 and Threads 1, Seed 0 (thread check vs the
n0_E Threads-4 run).

## How Seed and Threads reach Gurobi

- The array reads `seed` / `ruc_threads` from its own row and passes
  `--ruc_threads "$RUC_THREADS"` and, for seed > 0, `--ruc_solver_option
  Seed=$SEED` to `run_ercot_pcm.py`. The wrapper accepts any KEY=VAL except
  MIPGap / TimeLimit (refused: one source each) and casts `Seed` to int; it
  prints `ruc_solver_options={{'TimeLimit': ..., 'Threads': ..., 'Seed': k}}`
  in the job log (the collector copies that line to
  `run_index_N/conditions.txt`: verify the Seed echo there). A Seed-0 row passes
  no Seed option (the n0_E command line exactly, except the thread count on
  rows 17–18).
- Slots: one array script, submitted three times with command-line `-t` /
  `-pe smp` (`-t 1-16 -pe smp 4`, `-t 17-17 -pe smp 8`, `-t 18-18 -pe smp 1`);
  qsub command-line options override the embedded `#$` lines. Every task
  aborts (`FAILED_task_N_slots.md`) unless `$NSLOTS` equals its row's
  `ruc_threads`. One script keeps the job-log name `{WAVE}_array.o<jid>.<task>`
  the collector expects.
- Identity v3 unchanged: `--ruc_mipgap` / `--ruc_time_limit` from
  `waves/GAP_DECISION.json` at run time; the task refuses without it.

## Determinism conditions logged before every run (prompt 63 A4; memo F8)

`{STAMP}_HOST` (hostname), `{STAMP}_CPU` (`lscpu` Model name),
`{STAMP}_GUROBI` (`gurobipy.gurobi.version()`), `{STAMP}_THREADS`
(ruc_threads, NSLOTS, seed), `{STAMP}_CODE` (Prescient / Egret git SHAs of the
installed packages, repo HEAD). The collector writes these lines and the
wrapper's `run_ercot_pcm: index=` line to `run_index_N/conditions.txt`.

## Part C reads (prompt 63 v1 section 3; pre-registered, FROZEN with the wave commit)

{PART_C}

## Budget

18 full-year runs ≈ {18 * lo:.0f}–{18 * hi:.0f} core-h ({lo}–{hi} core-h per run at 4
slots, AMENDMENT 2026-11-16 actuals; the Threads-8 / Threads-1 rows scale
differently). 73 slots. Storage 18 × {mk.FULL_EXTRACT_MB} MB ≈ {18 * mk.FULL_EXTRACT_MB / 1000:.1f} GB of `--full`
extracts on CRC; gz tables never in git (`{GITIGNORE_LINE}`).

## Local checks (zero simulation)

`bash -n` on the scripts; `/opt/anaconda3/bin/python -m pytest
tests/test_make_noise_seed_E.py tests/test_make_ercot_n0.py -q`.

## Deviations (disclosed)

- `tier = "contrast"` (the 11-17 addendum names prompt 61's wave; this wave
  uses the same analysis-only tier; 54 / 55 never pass it to `load()`).
- `sobol_index` is empty; the n0_E anchor is `replicate_of`.
- New columns `seed` and `ruc_threads` (read by the array, not by
  `get_row.py`, which is unchanged).
- Quantile method: the prompt names no method; numpy's default is used. The
  pick is method-sensitive at 10 % and 90 % (Hazen / Weibull would pick other
  rows); it is fixed here, before any Y of this wave exists.
- One array script with per-submission slots instead of two scripts (simplest
  form SGE accepts; NSLOTS guard).
"""


def build(waves=ERCOT / "waves", design_space=DESIGN_SPACE_1113, wave_d_dm=mk.WAVE_D_DM, n0_dir=N0_DIR,
          gitignore=ERCOT / ".gitignore"):
    assert GITIGNORE_LINE in Path(gitignore).read_text().splitlines(), f".gitignore lacks {GITIGNORE_LINE}"
    mk.WAVES_E.setdefault(WAVE, STAMP)                    # a runtime key only (prompt 61 section 2.3)
    space = mk.load_space(design_space, wave_d_dm)
    dm = read_n0_x(n0_dir)
    picks = pick_designs(dm)
    rows = make_wave_rows(dm, picks, space)
    assert len(rows) == 18 and [r["index"] for r in rows] == list(range(1, 19))
    d = Path(waves) / WAVE
    d.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows, columns=mk.columns(space) + EXTRA_COLS).to_csv(d / "design_matrix.csv", index=False)
    n0_md5 = {}
    for r in rows:
        k = int(r["replicate_of"].split(":")[1])
        src = Path(n0_dir) / f"retrofit_gen_dict_{k}.json"
        dst = d / f"retrofit_gen_dict_{r['index']}.json"
        write(dst, src.read_text(), 0o644)
        n0_md5[k] = md5(src)
        assert md5(dst) == n0_md5[k], (dst, src)
        assert json.loads(src.read_text()) == mk.retrofit_dict(r, space), f"n0_E dict {k} != retrofit_dict(row)"
    write(d / f"{WAVE}_array.sh", array_text())
    write(d / f"collect_{WAVE}.sh", collector_text())
    write(d / "submit_this.sh", submit_text())
    write(d / "README.md", readme(picks, rows, space, n0_md5), 0o644)
    return rows, picks, space


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.parse_args(argv)
    rows, picks, space = build()
    for p in picks:
        print(f"{p['label']}: target T {p['target_T']:.3f} -> n0_E:{p['index']} T {p['T']:.3f} "
              f"(dist {p['abs_dist']:.3f}; runner-up {p['runner_up_index']} at {p['runner_up_dist']:.3f})")
    print(f"built waves/{WAVE}: {len(rows)} rows")


if __name__ == "__main__":
    main()
