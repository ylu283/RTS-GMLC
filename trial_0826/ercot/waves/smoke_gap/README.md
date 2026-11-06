# smoke_gap — RUC-gap smoke (prompt 58 T1, decision E-D6)

Built 2026-11-06 by `tools/make_smoke_gap.py`. NOT submitted by the executor.
Kay submits ON CRC:

    cd trial_0826/ercot/waves/smoke_gap && bash submit_this.sh

## 1. What it does

Three tasks, one SGE array (`-t 1-3`, 4 slots each, `-r n`, `-q long`).
Each task is the `smoke_v2` solve (3 days from 01-01-2019, v2 data, base
dict `{}`) with exactly two identity parameters changed:

| task | `--ruc_mipgap` | `--ruc_time_limit` | role |
|---|---|---|---|
| 1 | 0.01 | 1200 | control: must be BYTE-IDENTICAL to `extracts/smoke_v2` (the 120 s TL never bound there; raising it changes nothing — this asserts the new flag plumbing changed nothing else) |
| 2 | 0.001 | 1200 | candidate identity |
| 3 | 0.0001 | 1200 | stretch arm (where the cost curve flattens) |

The array prints `SMOKE_GAP_START` / `SMOKE_GAP_END` date stamps (with
epoch seconds). The collector (held on the array, email on this job only)
extracts every task `--full` into `extracts/smoke_gap/task_N/`, copies
Prescient's `runtimes.csv` (SCED solve times), writes `ruc_tolerance.csv`
(per-RUC-day Gurobi tolerance line) and `wallclock.txt`, then runs
`analysis/gap_smoke/read_smoke.py` -> `analysis/gap_smoke/GAP_SMOKE.md` +
`gap_smoke.csv` (per task) + `gap_smoke_days.csv` (per task x day), and
commits + pushes (ercot-bot, 5 retries).

## 2. Why: the gap binds everywhere at 1 %

`analysis/pool/POOL_V2.md` section 6.1 / 11: under `ruc_mipgap = 0.01` the gap
binds on every RUC day of all 31 v2 runs. The solver-hidden cost bound is
about $46M per run (about $93M per pair) against a median single-site PEM cost
effect of $11.3M: 0 of 16 single-site cost deltas are gap-readable. v2 RUCs are
cheap (base solve time median 19.2 s, p95 29.9 s, max 50.7 s per day at 4
threads), so a tighter gap is plausibly affordable. Any new identity sets BOTH
the gap and a time limit the gap never reaches (a binding TL brings back the
v1 nondeterminism).

## 3. Prescient precedence finding (settled 2026-11-06 from the source)

Question (prompt 58 section 1): does Prescient's `ruc_mipgap` option set the
Gurobi `MIPGap` BEFORE or AFTER `deterministic_ruc_solver_options` are applied?

Answer: BEFORE. `ruc_mipgap` is written first; every key of
`deterministic_ruc_solver_options` is written after it, so a `MIPGap` key
there would silently OVERRIDE `ruc_mipgap`. The chain (local checkouts;
the CRC env pins Prescient `ylu283/Prescient@a4c0849` and the egret fork
`ylu283/Egret@e4a244d`; `git diff` of these files between the pinned commits
and the local HEADs is empty):

- `Prescient/prescient/simulator/config.py:459-463` declares `ruc_mipgap`
  (default 0.01, "the mipgap for all deterministic RUC solves") and
  `:435-439` declares `deterministic_ruc_solver_options`.
- `Prescient/prescient/engine/egret/egret_plugin.py:358-361`:
  `_solve_deterministic_ruc` calls
  `call_solver(solver, pyo_model, options, options.deterministic_ruc_solver_options)`.
- `Prescient/prescient/engine/egret/egret_plugin.py:49-53`: `call_solver`
  reads `mipgap = options.ruc_mipgap` and calls
  `_solve_unit_commitment(instance, solver, mipgap, None, tee, symbolic_solver_labels, solver_options, None, relaxed, ...)`
  — note `timelimit=None`: the TimeLimit reaches Gurobi ONLY through the
  solver-options dict (= `--ruc_time_limit`).
- `Egret/egret/models/unit_commitment.py:1605-1612`:
  `_solve_unit_commitment` -> `_solve_model(m, solver, mipgap, timelimit, ..., solver_options, ...)`
  (via `_outer_lazy_ptdf_solve_loop` `:875/:917/:951` on the lazy-PTDF path,
  same arguments).
- `Egret/egret/common/solver_interface.py:145`:
  `_set_options(solver, mipgap, timelimit, solver_options)`.
- `Egret/egret/common/solver_interface.py:44-45`:
  `if 'gurobi' in solver_name: if mipgap is not None: solver.options.MIPGap = mipgap` — FIRST.
- `Egret/egret/common/solver_interface.py:71-73`:
  `if other_options is not None: for key, opt in other_options.items(): solver.options[key] = opt` — AFTER.

Implementation (`run_ercot_pcm.py`, prompt 58): new `--ruc_mipgap` (default
0.01 = the value inherited from `multi_PEM_PCM.prescient_options`, so every
existing wave is unchanged) written to `opts["ruc_mipgap"]`; every other
default untouched. Because of the precedence above the wrapper REFUSES
`--ruc_solver_option MIPGap=...` (and `TimeLimit=...`): the gap has exactly
one source. The wrapper banner prints `ruc_mipgap=<value>`.

Note on the h2patch (`env/h2patch_2.2.3.diff`): it touches only
`prescient/engine/egret/reporting.py`; the solve path above is stock.

## 4. Verification: the tolerance line

Gurobi prints, on every RUC day that reaches the gap,

    Optimal solution found (tolerance 1.00e-03)

The collector greps this line per RUC segment (segment = the
`Extracting scenario to simulate` ... `Deterministic RUC Cost:` block, the
same boundaries `extract_ercot.parse_ruc_quality` uses) with
`read_smoke.py --joblog <array .o file> --tolerance-out task_N/ruc_tolerance.csv`
(regex `Optimal solution found \(tolerance ([\d.eE+-]+)\)`; a lazy-PTDF day
can hold several MIP solves — the last tolerance of the segment is kept and
the count reported). `read_smoke.py` then checks tolerance == requested gap
on every day. **A task-2/3 log whose tolerance reads 1.00e-02 is a FAILED
smoke, not a result.** `Time limit reached` days have no tolerance line and
fail rule (i).

## 5. Pre-registered reading (decision = Kay, E-D6)

`read_smoke.py` prints the table and the rule's verdict; it does not choose
and never writes `waves/GAP_DECISION.json`. Adopt the TIGHTEST arm for which
(i) every day is OPTIMAL with the tolerance line == the requested gap,
(ii) max per-day solve time <= 600 s, (iii) projected full-year RUC time at
the max (365 x max) <= 61 h; otherwise keep 0.01 / 120 and disclose. The
report also shows the 3-day cost shift of task 2 (and 3) vs task 1 scaled
x 365/3 next to the $11.3M single-site median, and the byte-identity verdict
of task 1 vs `extracts/smoke_v2` (md5 of `overall.csv`, plus every table of
the reference manifest).

Kay then writes `waves/GAP_DECISION.json`:

    {"ruc_mipgap": 0.001, "ruc_time_limit": 1200, "decided_by": "Kay",
     "date": "2026-11-xx", "evidence": "extracts/smoke_gap"}

Wave D (`waves/location_oat_v2/`) refuses to start without it. The adopted
pair is an AMENDMENT to `ERCOT_BO_PLAN.md` section 2/3 (strategy session) and a
new `CONFIG_ERCOT.md` row marked "identity v3".

## 6. Local checks done (zero simulation)

- `bash -n` on the three scripts.
- `run_ercot_pcm.build_options` dry-run in the local prescient venv: default
  `ruc_mipgap = 0.01`, `--ruc_mipgap 0.001 --ruc_time_limit 1200` lands in
  `opts["ruc_mipgap"]` / `deterministic_ruc_solver_options["TimeLimit"]`;
  `--ruc_solver_option MIPGap=...` refused.
- `tests/test_read_smoke.py`: `extracts/smoke_v2` copied three times as
  task_1..3 -> every delta vs task 1 = 0, byte identity PASS; the tolerance
  parser on a synthetic log; the rule's failure branches.
