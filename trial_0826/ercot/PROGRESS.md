# ERCOT PROGRESS (prompts 26 → 36, 52, 57, 58)

## Prompt 52 v2.1 — ERCOT noise measurement, `waves/noise_v3` BUILT (2026-11-06, zero simulation, local only)

- [x] **Pick (pre-registered)** `tools/make_noise_v3.py` writes
  `waves/noise_v3/PICK_RULE.md` BEFORE the pick, then `pick_table.csv` +
  `pick.json`: pool = 16 single-site v2 rows + 6 nuclear rows (21 distinct
  designs), objectives = the 22 gradable candidates of prompt 57 (frozen
  f76d897; E8/E9/N5 NOT USED — no v2 value on slim extracts), composition
  3 VRE + 1 NUC, score = mean achieved spread (exhaustive, 2,800 sets).
  Picked: D1 `screening_v2/ercot:1` (site 275, 519.5 MW), D2 `ercot:7`
  (206, 899.9 MW), D3 `topup:4` (146, 134.0 MW), D4 `selection_t1_v2:10`
  (nuclear gen 1, 2430 MW, ω = 1.0); mean spread 0.88 (E1 0.51, N2 0.60,
  E3 0.63 are the collapsed strata — nuclear :10 holds the max of 11
  candidates at once; visible in the README table). v2 values chose
  designs only; never data.
- [x] **Rows (layout 16 COMMITTED, 5f131f1; strategy 11-06)**: per design
  exact in A, exact in B (the cross-batch exact pair, both v3 runs), one
  perturbed copy in A and one antithetic perturbed copy in B (δ = 0.001
  relative on `pem_mw`, sign from seed 52, inward at nameplate: nuclear
  2430 → 2427.57 MW in A and 2425.14 MW in B, the antithetic copy stepping
  2δ inward at the bound). Batch A 8 rows, batch B 8 rows; ruler population
  8 (prompt 57 A4). Prompt 52 §3's "12 runs" cannot hold 4 cross-batch
  exact pairs AND 8 perturbed copies under v3 — resolved to 16, disclosed
  in README §5; `--layout 12` (A 8, B 4; ruler n = 4) stays in the builder
  as the alternative and is NOT the committed wave.
- [x] **Scripts** per batch (`waves/noise_v3/{A,B}/`): array `-t 1-n`,
  `-pe smp 4`, `-r n`, `-q long`, SMOKE_GATE, identity from
  `waves/GAP_DECISION.json` at run time (wave-D block; refuses without
  it), `NOISE_V3_START/END` stamps; collector (held; email on it only):
  every row `--full`, `runtimes.csv`, `wallclock.csv`, `identity.txt`,
  `pool_objectives.py --run-dir` → `pool_full_metrics.json`, `COLLECTED`
  marker, slim + json commit, gz asserted unstaged, 5-retry push.
  `B/submit_this.sh` refuses until `extracts/noise_v3/A/COLLECTED` is in
  the tree. `.gitignore`: `extracts/noise_v3/**/*.csv.gz`.
- [x] **`analysis/noise_v3/read_noise.py`** (pandas/numpy; reuses
  `pool_objectives.pool_row`; χ²/F quantiles from the incomplete gamma /
  beta, tested against scipy): exact-pair |Δ| (exact zeros), perturbed |Δ|
  population = `ruler_j` (median/min/max, `RULER=0` list), per-level sd +
  χ² CIs, pooled sd + Satterthwaite df, per-objective variance-ratio
  trigger (α 0.05 AND ratio > 3) with one family-wise line, covariance
  matrix of the perturbed deltas, shed ≡ 0 assert (exit 1), runtime table
  (wall → core-h; replaces plan §8 "UNKNOWN"), `ERCOT_NOISE.md` §0 = the
  three-line v3 identity statement (GAP_SMOKE.md + AMENDMENT 2026-11-06b)
  + `ercot_noise.csv/json` + `ercot_noise_cov.csv`.
- [x] **Tests** `pytest tests/test_make_noise_v3.py tests/test_read_noise.py
  tests/test_pool_objectives.py -q` green; `bash -n` on the six scripts.
  Fixture: 16 extracts from `base_2019_v2/run_index_1` slim tables with
  controlled `overall.csv` edits (known medians and sds; exact-zero,
  RULER=0, firing and non-firing trigger, exact-pair-differs, shed FAIL,
  missing-extract paths); one test keeps layout 12 buildable.
- [ ] **KAY (1):** `cd trial_0826/ercot/waves/noise_v3/A && bash submit_this.sh`
  (32 slots, 8 full-year rows, ≈ 8–10 h wall each at v3).
- [ ] **KAY (2):** after batch A's collector email:
  `cd trial_0826/ercot/waves/noise_v3/B && bash submit_this.sh` (32 slots,
  8 rows; refuses until `extracts/noise_v3/A/COLLECTED` is pushed).
- [ ] **Next session:** `python analysis/noise_v3/read_noise.py` → commit
  `ERCOT_NOISE.md`; feed `ruler_j` into prompt 57 Part B (replaces `RULER
  PENDING (52)`), the plan §8 core-h actuals, and §7 rider levels.
- Storage: 16 × 51 MB ≈ 0.80 GB on CRC; ≈ 48 MB in git. Session lock `52`
  in this worktree. No push.

## Prompt 58 — RUC-gap smoke (E-D6) + wave D build (2026-11-06, zero simulation, local only)

- [x] **Precedence settled from the source** (2026-11-06): Prescient
  `egret_plugin.py:49-53` passes `mipgap = options.ruc_mipgap` and
  `options.deterministic_ruc_solver_options` (`:358-361`) to egret;
  `solver_interface.py:145` → `_set_options`: `solver.options.MIPGap =
  mipgap` at `:44-45` FIRST, then every solver-options key at `:71-73`
  AFTER. `ruc_mipgap` is the canonical knob; a `MIPGap` solver option
  would silently override it. Pinned commits (Prescient a4c0849, egret
  e4a244d) == local HEADs on these files. Written in
  `waves/smoke_gap/README.md` §3.
- [x] **`run_ercot_pcm.py --ruc_mipgap`** (default 0.01 = inherited; every
  other default unchanged; `--ruc_solver_option MIPGap/TimeLimit` refused;
  banner prints `ruc_mipgap=`). Dry-run in the local prescient venv.
- [x] **T1 `waves/smoke_gap/`** (`tools/make_smoke_gap.py`): array `-t 1-3`
  (gap 0.01 / 0.001 / 0.0001, TL 1200, 3 days from 01-01-2019, base, 4
  slots, `-r n`, `-q long`, date stamps), held collector (`--full` extracts
  to `extracts/smoke_gap/task_N`, Prescient `runtimes.csv`,
  `ruc_tolerance.csv` from the Gurobi tolerance line, wall-clock, then
  `analysis/gap_smoke/read_smoke.py` → `GAP_SMOKE.md` + `gap_smoke.csv` +
  `gap_smoke_days.csv`), `submit_this.sh` on the smoke_v2 pattern.
  `read_smoke.py` prints the pre-registered rule's verdict and the
  ×365/3 cost shift vs the $11.3M median; it never writes
  `GAP_DECISION.json`. Fixture test (smoke_v2 × 3): all Δ = 0, identity
  PASS.
- [x] **T2 `waves/location_oat_v2/`** (`tools/make_wave_d.py`, NOT
  submitted): 21 rows (163, 140, 146, 270, 110, 274 × 60/120/180 MW;
  nuclear gen 1 × 60/120/180 MW, ω = 0.02469 / 0.04938 / 0.07407),
  `design_matrix.csv` (+ `pem_mw`, `level_id`), dicts (nuclear without
  `gen_pmax`), asserts (180 ≤ 185.4; fractions ≤ 1). Array reads
  `--ruc_mipgap/--ruc_time_limit` from `waves/GAP_DECISION.json` at run
  time (refuses without it; SMOKE_GATE; date stamps). Collector: every
  row `--full` + `runtimes.csv` + wall-clock + `pool_objectives.py
  --run-dir` on CRC; commits slim tables + `pool_full_metrics.json` +
  `runtimes.csv` + manifest; `*.csv.gz` left in storage
  (`trial_0826/ercot/.gitignore`). `submit_this.sh` refuses without
  `GAP_DECISION.json`, prints it, asks `yes`. README per prompt 58 §3.
  Storage: 21 × 51 MB ≈ 1.05 GB on CRC, ≈ 60 MB in git.
- [x] **`pool_objectives.py --run-dir/--out`** per-run mode: E8, E9, N5
  (+ checks), commitment-headroom diagnostic from `thermal.csv.gz`
  (Σ committed (PMax − Dispatch); agrees with R7 to 1e-11 MW), R7/R8, RUC
  quality, manifest md5s re-hashed. Base run 1: E8 15.483, E9 0, N5
  −18.402 (= POOL_V2 §1). Runs under pandas 2.3.3 and 3.0.6 (local
  ercot223 venv) with identical output.
- [x] **Tests** `pytest tests/test_make_wave_d.py tests/test_pool_objectives.py
  tests/test_read_smoke.py -q` green (see commit); `bash -n` on every
  shell script.
- [ ] **KAY (1):** `cd trial_0826/ercot/waves/smoke_gap && bash submit_this.sh`
  (minutes). Read `analysis/gap_smoke/GAP_SMOKE.md` when the collector
  pushes; task 1 must be byte-identical to `extracts/smoke_v2`; a task-2/3
  tolerance line reading 1.00e-02 is a FAILED smoke. Then write
  `waves/GAP_DECISION.json` (E-D6).
- [ ] **KAY (2):** `cd trial_0826/ercot/waves/location_oat_v2 && bash submit_this.sh`
  (refuses without `GAP_DECISION.json`; 84 slots; 21 full-year rows).
- [ ] **Strategy session (after E-D6):** ERCOT_BO_PLAN §2/§3 amendment +
  CONFIG_ERCOT.md row "identity v3"; Part B of prompt 57 after wave D lands.
- Pi-agenda one-liners: "E-D6 gap smoke built (3 arms, control byte-identity
  gate); wave D (21 rows, all --full) built and gated on GAP_DECISION.json".
- Session lock `58` inside this worktree. No push.

## Prompt 57 Part A — objective-pool expansion (2026-11-06, zero simulation, local only)

- [x] **Freeze** `analysis/pool/pool_definitions.json` at `f76d897` (28
  candidates + D3, dirs, priorities, global order, EF COAL 1.00 / CT 0.55
  t/MWh ± 20 %, 450 $/MWh LMP threshold, S1–S3, G, S, §4 ρ rules).
- [x] **A1/A2** `pool_objectives.py` → `pool_wide_v2.csv` (31 rows, 23
  distinct designs, 1 full extract, 0 SUSPECT); 144/144 legacy cells equal
  the frozen `objectives_t1_v2.csv` (h2 copied on the 6 slim nuclear rows).
  DEAD: E5, R1, R3 (max |value| 0). UNDETERMINED: E8, E9, N5 (one `--full`
  run). Exact replicates → exact zeros. Commit `4863973`.
- [x] **A3** first cut n = 16 (NON-USE): raw cluster {E1, V2, X1};
  gen_pmax-partialled {V2, X1}. E1–X1 +0.92 raw → +0.52 partialled (the
  pinned conflict is not visible at one size per site). V1–N3 −0.84/−0.87.
  `figs/pool_firstcut_clustermap.png`. Commit `a613507`.
- [x] **A4b** G_base = $196.7M = 17.4 × the $11.3M median single-site
  |Δ total_cost|; 0 / 16 single-site E1 deltas GAP-READABLE; the 1 % gap
  binds on every RUC day. E-D1 cost evidence must be re-read in Part B.
- [x] **A5** storage line: 51 MB × 21 rows ≈ 1.07 GB (18 rows ≈ 0.92 GB).
- [x] **A6** `ERCOT_BO_PLAN.md` AMENDMENT 2026-11-06 (E-D1b) appended.
- [x] **Tests** `pytest tests/test_pool_objectives.py -q` → 13 passed
  (pandas 2.3.3 local). **CRC run pending** under PCM_ERCOT (pandas 3.0.5).
- [ ] **Part B** waits for wave D (`location_oat_v2`, all `--full`) and
  Kay's three MW levels; ruler waits for prompt 52.
- Session lock `57` inside this worktree. No push.

## Prompt 36 — cost-data fix (2026-10-12, T0 + T1 build done locally; CRC pending)

- [x] **T0** `analysis/cost_fix/t0_verify_sources.py` → `T0_FACTS.md` 30/30 PASS
  (pkl = 0.7 × xlsx exactly on all 128 thermal; v1 HR_avg_0 = Csu·Pmax/fp;
  v1 nuclear cost at Pmin $2.13M / $2.64M/h; authors' objective linear;
  CONOPT; PV Pmax ×0.3 in pkl). `source_coeffs_tx123.csv` frozen.
  `CONVERSION_INVENTORY.md`: no other ×0.7 anywhere; live GTEP input
  `idaes-gtep/gtep/data/123_Bus_Coal/gen.csv` carries the v1 bug (B′).
- [x] **§0.2** Kay 10-12: option (c), B = 40 (prompt text). B position: 44.8 of
  75.9 GW thermal has C1 < 40 (merit order by C1).
- [x] **T1** `tools/convert_tx123_costs.py --reading c` → `data/ercot123_2019_v2/`
  (10 CSVs byte-copied, gen.csv cost cells only; 22 CT units on the 2-point
  fallback — fork 6-dp fuel rounding fails egret's convexity check on equal
  slopes; cost identical). `--data_dir` plumbed (run/extract/verify/probe/
  screening builders/make_metadata; default = v1; non-default refuses v1 wave dirs).
- [x] **Tests** `tests/` local (patched stock 0.6.2 copy, hash check skipped):
  6 pass / 1 skip; RTS round trip 73 units; campaign + multi_pem 77 pass /
  1 skip; verify_metadata v2 PASS. **CRC run pending:**
  `bash trial_0826/ercot/tests/run_cost_fix_tests.sh` in PCM_ERCOT.
- [x] Waves built (`tools/make_v2_waves.py`): smoke_v2, base_2019_v2 (A, 3),
  screening_v2 (B, 12+7 byte copies), selection_t1_v2 (C, rows 3–11),
  `waves/submit_v2/submit_this.sh` (refuses without SMOKE_PASS).
  `compute_objectives.py --suffix _v2` → objectives_t1_v2.csv, noise_ruler_v2_v2.json.
- [x] INVALID_v1_costs.md markers (9 dirs).
- [x] Authors' SCUC side-by-side (local Gurobi), days 1–3, reading (c):
  DLR system-mean LMP 4.95 / 5.68 / 5.53 (bus range −68…+79), cost $17.4M /
  $28.0M / $26.0M; static ratings: day 2 infeasible (no shed slack).
  `analysis/cost_fix/smoke_gate.py` dry-run on v1 smoke_3d → FAIL (expected).
- [x] smoke_v2 landed (1a1c628). Gate amended 10-12 (cost ±15 % vs authors
  DLR + RUC OPTIMAL/≤1 % + RT mean LMP $10–60 + zero shed; LMP side-by-side
  report-only) → **PASS** (`analysis/cost_fix/SMOKE_REPORT.md`): cost +6.0 /
  +5.6 / +3.8 %; RT mean LMP 30.0 / 40.1 / 36.9; RUC OPTIMAL, gap ≤ 1 %, ~9 s;
  nuclear on 72/72 h; no shed. Amended gate on v1 smoke_3d → FAIL (cost).
  `waves/smoke_v2/SMOKE_PASS` written.
- [ ] CRC cost-fix tests output (Kay) — not yet seen.
- [x] A + B + C submitted (Kay). A + B landed (e3082fa, 2ba803b; 3 + 19/19).
- [x] Wave-D top-k rule committed unchanged (4fb3b1f), after B landed at
  02:30 on 10-13 and before any per-site screening_v2 value was read.
- [x] T3 base read (df61ab4): `analysis/cost_fix/ERCOT_COST_FIX.md`.
  - RT LMP mean 14.5 → 33.8; fixed cost 6.75 B → 3.63 B; variable cost
    1.19 B → 4.46 B; true curtailment 9.44 M → 5.92 M MWh.
  - Nuclear: both units on 8,760 h with 0 starts.
  - Solver: 0 % of RUCs capped at the time limit; all 1,460 OPTIMAL.
  - The 4 base runs are byte-identical, so the A ruler is 0 and the rule
    falls back to the top 6 by rank: sites 163, 140, 146, 270, 110, 274.
    Smallest chosen gen_pmax 185.4 MW.
  - Screening row 10 (`__ALL__`) is an outlier and not a single-site row.
- [ ] Wave D sizes: Kay to confirm 3 absolute MW levels (≤ 185.4) before
  the build. The wave-D nuclear row needs the T0 fix below.
- [x] **Wave C T0 fix (10-13).** selection_t1_v2 tasks 6/7 FAILED (02b147d;
  CRC log o1533432.6) with "Generator 1 has less output at T0 than is
  feasible to ramp up to"; PowerGeneratedT0[1] = 7.29 p.u. = 729 MW.
  - Cause: with no initial_status.csv the parser sets a committed unit's T0
    to the ORIGINAL p_min (729 MW). The thermal patch raised p_min but did
    not touch T0.
  - Fix: `multi_pem/parameters.py` lifts `initial_p_output` to the new p_min
    when `initial_status > 0`. Prescient sets T0 (egret_plugin.py:401-403)
    before `before_ruc_solve` runs the patch.
  - Ramp numbers: gen.csv reads 121.5 MW/min, and the parser emits
    `ramp_up_60min` = 7,290 MW/h. The patch then overwrites it with the PEM
    capacity ω × 2,430 (121.5 / 698.6 / 1,275.75 / 1,852.9 / 2,430 MW/h),
    and that is the value egret's validator uses.
  - Egret requires T0 ≥ p_min − ramp. From T0 = 729 the ramp needed is
    1,579.5 at ω 0.05, 1,002.4 at 0.2875 and 425.25 at 0.525. The bracket
    "425–1002 MW/h" is only what the pass/fail pattern implies.
  - At ω 0.05 the patched ramp (121.5 MW/h) equals the gen.csv number
    121.5 MW/min only by coincidence (0.05 × 2,430).
  - Test: `multi_pem/tests/test_t0_build.py` builds the egret UC model
    (fork replica, no solve) at every ω.
    - Without the fix: ω 0.05 and 0.2875 reproduce the CRC error, and
      0.525 builds but fails the T0 ≥ p_min assertion.
    - With the fix: 6/6 pass. Locally campaign + multi_pem + ercot give
      89 passed / 2 skipped.
  - Rerun of ALL nuclear rows 6–11: `waves/selection_t1_v2/rerun_nuc_this.sh`
    (6 tasks, 24 slots). It moves the old runs to
    `runs/quarantine_T0_729/` (never deleted). Rows 3–5 keep their first
    runs. The collector then extracts all 9 rows and runs
    compute_objectives --suffix _v2. Disclosed in CARRIED_OVER.md and T3.
- [ ] Kay: `bash waves/selection_t1_v2/rerun_nuc_this.sh` on CRC.


## Prompt 33 — TL=360 probe (2026-10-09, T0 done + T1 built)

- [x] **T0 near-tie analysis (zero sims):**
  `analysis/tl360_probe/TL360_VERDICT.md` v0 + `t0_neartie_days.csv`.
  159 divergence days (≥2 GW committed-MW proxy — a SUPERSET of gen-1
  flips; replicate is slim, said so) carry +$61.5M of the +$79.5M annual
  gap; **124/159 sit inside the day's accepted 1% RUC tolerance (median
  ratio 0.24)**; the Sept/Oct tail (ratios to 227×) is downstream path
  divergence, not out-of-tolerance solves. **PRE-REGISTERED PREDICTION
  (recorded before any run): TL=360 will NOT pin gen-1** — the flip is a
  near-tie inside the frozen 1% mipgap; refutation condition stated.
- [x] **T1 built:** `waves/tl360_probe/` — 3 identical base solves at
  the frozen config with EXACTLY ONE change (`--ruc_time_limit 360`;
  threads 4 frozen; `-r n`; mkdir-p lesson applied; collector clears
  stale FAILED, 5-retry push, email on collector only; slim extracts +
  `--full` run 1). **TL=360 = NEW solver identity, quarantined** from
  all TL=120 data/rulers (manifest-stamped; `compute_tl360.py` never
  touches noise_ruler_v2.json). ~260 core-h, 18–27 h/run.
- [ ] **KAY:** `cd trial_0826/ercot/waves/tl360_probe && bash
  submit_this.sh` (may run concurrently with selection_t1 — both small).
- [ ] **T2 (re-invocation when the collector pushes):** fill the verdict
  table in TL360_VERDICT.md from `tl360_readings.json` (gen-1 starts by
  solve, pairwise |Δ| per objective, gap stats, wall time); confirm or
  refute the pre-registered prediction; argue Route A/B/C from the
  table (decide = Kay/PI); record the PI's route in pi-agenda §4.

---

# (prompt 32 and earlier below)

## Prompt 32 — selection analysis (2026-10-08, T0 + T1 build done locally)

- [x] **T0 (zero new sims):** `analysis/selection/` — executed
  `selection_t0.ipynb` + `ERCOT_SELECTION.md` **v0** with the decision
  register (D4/D5/D6). Ruler adjudication RECORDED and re-verified to the
  MWh (7,921 = clean 5,007 + PEM-twin 2,914; clean list {5,479, 5,007});
  SCREENING_ERCOT.md's inverted note corrected; `noise_ruler_v2.json`
  (list schema, v1 frozen, LOW-CONFIDENCE df rules, bimodal flags).
  T-M1 analogue: all VRE 0.875–0.979 of availability in LMP<$15 hours;
  **nuclear gen 1 only 0.360** (bus 107 clears high); **gen 93 NEVER
  COMMITS in base** (0 output/starts — stays out of T1 by design).
  Tier shares (positive-part, §4.5 rule): bus-120 cluster pools **59.5%**;
  independents at ≥5% & ≥2× (same set at ≥3×): {275, 274, 270, 110, 140,
  146, 30}; negative responder: 20 (−3.8×). Pool first-cut (n=16,
  NON-USE clause): relief↔var_cost −0.37 — the T2 contrast to prioritize.
  Fuel note pre-registered: gen-1 base booked Unit Cost **$3.1849B/yr**;
  patch takes the del-p_fuel branch (**verified locally**: egret 0.6.2
  emits p_fuel, no p_cost; thermal, p_min=729).
- [x] **T1 build (local):** `waves/selection_t1/` (11 rows; nuclear OAT on
  lattice {0,2,4,6,8}; replicate_of uses wave:index keys), smoke-gated
  chain (SMOKE_PASS file — explicit, never bare hold_jid), `-r n`
  everywhere, Threads=4 frozen, 5-retry push collector (prompt-30 loop),
  `compute_objectives.py` (thermal-h2 rule + mode-resolved base
  differencing + ruler-v2 groups), `probe_model_shape.py`,
  multi_pem ERCOT gen-1 fixture tests (16/16 pass).
- [ ] **KAY: T1 on CRC** — (i) `python probe_model_shape.py` under
  PCM_ERCOT (login node ok); (ii)
  `cd trial_0826/ercot/waves/selection_t1 && bash submit_this.sh`
  (smoke → 11-task array → collector; ~700–970 core-h; collector emails
  + bot-pushes extracts/objectives/ruler-v2).
- [ ] **PI meeting (D4/D5/D6)** with v0 + T1 nuclear evidence on screen.
- [ ] **T2 [GATED on D5/D6]:** `make_selection_t2.py` (to be written at
  T2 time with the bracket decisions: ~5 tier sweeps × 5 levels, 2–3
  pair grids on STAGE2_LATTICE², `__ALL_TIERS__` @ ω=0.525; §2
  conventions native — never d6's build_pairgrid; ~11–24k core-h).
- [ ] **T3:** ERCOT_SELECTION.md FINAL + per-stratum redundancy + RTS-vs-
  ERCOT table (basis-difference header) + artifact page.

---

# ERCOT sprint PROGRESS (prompt 26)

Updated at every block boundary; a re-invoked session resumes from here.
Workspace: local worktree `../RTS-GMLC-ercot` (branch `ercot/tx123`); CRC
worktree `$GROUP/ylu28/RTS-GMLC-ercot` (created by block #1). Prompt 27
owns the main clones on `d6` — never touch.

## State (2026-09-21, third session — base LANDED)

- [x] **T1 port (local, 09-19)** — data vendored + MD5-verified;
  metadata regenerated (`make_metadata.py`) with PROVENANCE; model-level
  VERIFY PASS; wrapper `run_ercot_pcm.py`; `CONFIG_ERCOT.md`.
- [x] **Block #1 (CRC)** — both patch HEADs asserted by hash (prescient
  h2patch-2.2.3 a4c0849…, egret ercotpatch-0.6.2 e4a244d…); diffs +
  PCM_ERCOT env export committed; PYTHONNOUSERSITE=1 everywhere.
- [x] **Block #2 (CRC)** — smoke + probes + eoy padding PASS; riders
  clear; smoke mean LMP $14.79.
- [x] **Block #3 (CRC)** — smoke extract pushed; base died (mkdir), fix
  `de4fb43`, marker cleared later by the successful collector.
- [x] **Block #5 (CRC, 09-20/21)** — base resubmitted; **collector
  succeeded end-to-end: `be5d254 ercot-bot: base_2019 extract`** (first
  fully-unattended collector run incl. marker clearing — automation
  first-pass success after one human-fixed submit bug).
- [x] **BASE QUALITY (rider (i), audited 09-21): RUN VALID.** 365/365
  days, SolCount=0 on NONE; 44/365 days (12.1%) TIME_LIMIT; final gap
  median 0.98%, P95 1.36%, max 3.23% (worst day 2019-02-22) — far under
  the 10% rider-(iii) threshold. Note on `solve_time_s` semantics: the
  per-day value sums ALL Gurobi solves in that day's log segment (RUC
  MIP + settlements/pricing under `compute_market_settlements=True`), so
  >120 s totals on OPTIMAL days are expected; the 120 s cap binds per
  MIP solve.
- [x] **Degenerate-g4 RESOLVED: NOT degenerate** — 7 hours RT reserve
  shortfall, 280.9 MWh total on the TL=120 base (TL=3600's zero did not
  carry over). CONFIG_ERCOT.md updated (row, resolution 4, decision 5).
- [x] **Base anatomy** — LMP mean $14.53 / median $10.36 over 1.08M
  bus-hours, 0 floor artifacts, 189 bus-hours ≥ $450; VRE curtailment
  10.6% of availability, zero shed; peak 74.7 GW.
  `analysis/base_anatomy.ipynb` re-executed against `extracts/base_2019`
  (PRELIMINARY banner gone), 0 errors.
- [x] **Screening slate CONFIRMED WEAK → two-arm redesign (09-21):**
  actual top-12 curtailers overlap the availability-proxy slate only
  3/9 (275, 274, 30). Curtailment is congestion-driven: **bus 120 hosts
  5 of the top-8 curtailers** (275, 274, 270, 163, 116); site 163
  (185 MW) curtails 2.5× its delivered energy. New wave
  `waves/screening_topup/` (7 rows: wind 270, 163, 110, 146, 140; PV
  116, 59) generated deterministically by `make_screening_topup.py`
  from the base extract; both arms together cover the actual top-10
  exactly. v1 = availability/contrast arm + __ALL__ + the 2 replicate
  noise-ruler rows.
- [x] **Block #4b (CRC)** — both arms ran and collected first-pass:
  `6dc533e` (topup extracts), `33a139b` (v1 extracts incl. replicate
  rows). No FAILED markers.
- [x] **SCREENING ANALYSIS (09-22, fourth session)** —
  `analysis/screening_analysis.ipynb` executed + `SCREENING_ERCOT.md`
  verdict + `screening_site_effects.csv` + `screening_noise_ruler.json`.
  Headlines: (1) relief tracks the site's own base curtailment
  (Spearman +0.89) and nothing else — availability proxy formally dead;
  (2) bus-120 pocket is the MOST efficient diversion target (0.72
  relief/H2 vs 0.37; site 275 = 2.17 TWh relief, 397× ruler); (3) big
  uncongested wind (20/204/205) = zero relief at +$13–16M var cost;
  (4) **total cost UNREADABLE: fixed cost bimodal ±$79.5M — gen 1
  (2,430 MW NUC) commitment flips under TL=120** (both replicate pairs
  landed opposite states); variable gen cost is the cost read-out
  (ruler $0.29M); (5) joint/Σ = 0.933 (mild sub-additivity);
  (6) zero load shed everywhere — shed is not an ERCOT objective.
  Proposed tier structure (pocket_120 cluster / wind_near / pv_26 /
  drop the availability giants unless an H2-volume objective enters) is
  in SCREENING_ERCOT.md, awaiting PI. Pain log compiled there
  (PENDING-KAY: qacct splits, block-log timestamps).

## Workflow-pain log inputs accumulating (directive requirement)

- Failure event #1: base died in 1 s (mkdir), marker pushed 09-20
  18:37Z, fix 18:48, recovery block same session; resubmit + clean
  collector pass by 09-21. Cause codes: submit + failure-recovery.
- First-pass automation: block #5's chain ran unattended (gate PASS,
  extract, marker clear, bot commit+push, email) — zero human touches
  after qsub.
- Ranking-gate event: block #4's slate gate is designed to trip at 3/9
  (<half) — record in the touch log whether Kay hit it or 4b's
  detection path instead (visible in whichever block log exists).
- Compile at analysis time from: block logs 1–5 + 4b, qacct on the
  JIDs, collector .o logs, ercot-bot commit log.

## Notes for the resuming session

- Local env for verify/parsing/notebook: `~/venvs/ercot223`
  (gridx-prescient 2.2.3 + egret 0.6.2 + jupyter, pip).
- Session lock: `trial_0826/campaign/.session.lock` = `26` INSIDE this
  worktree (a `27` lock in the main clone is expected, not a stop).
- Results return via bot pushes: `git pull` in the local worktree.
- `make_metadata.py` landmines (do not "clean up"): `Tr Ratio` spelling;
  branch UID `L` prefix; year-end 24 h padding.
- No `Ref` bus by design: egret picks the alphabetically-first bus name
  deterministically (params.py:153-156).
- Notebook rendering: `text.parse_math: False` required (literal "$"
  otherwise triggers mathtext and corrupts labels).
