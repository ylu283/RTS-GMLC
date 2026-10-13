# ERCOT PROGRESS (prompts 26 → 36)

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
- [ ] Kay: `bash waves/submit_v2/submit_this.sh` (31 tasks, 124 slots).
- [ ] T3 read-outs `analysis/cost_fix/ERCOT_COST_FIX.md`; wave D after B.


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
