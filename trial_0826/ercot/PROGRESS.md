# ERCOT PROGRESS (prompts 26 → 36, 52, 53–55, 57, 58)

## Prompt 65 — E-D1b rule v2: disclosed post-hoc amendment + re-walk + dated design space (v1.1, 2026-11-24; executor writes here only)

### 2026-11-24 — executor (worktree `RTS-GMLC-e65`, branch `ercot/65-objective-rule-v2`)

- (i) 212d60d: AMENDMENT 2026-11-24 committed alone. It is the v1.1 block with §8 folded in, sha256 `e3712a7f…`.
- (ii) b8a3285: `analysis/pool/pool_n0E_v2.py` + `tests/test_pool_n0E_v2.py` (26 tests on synthetic Y at the real X).
- (iii) real read. Seats **V1 · E1 (M = 2)**: X1 suppressed by E1, R EMPTY, N EMPTY.
  - N4 is REDUNDANT given V1: raw ρ 0.966; residual ρ 0.421 [90 % 0.176, 0.617]; residual Mantel p 0.0253 > 0.01, so N4 is not COMPOSITION-RESOLVABLE; residual IDR/B 4.34 (joint lower-90 2.31).
  - §4b was not reached.
  - This differs from the §3 prediction V1 · E1 · N4. It was committed per Kay's override of §8.14: never tuned, never re-run.
  - v1 and the Seed-bar re-grade (V1 · E1 · N1) are co-reported.
- (iv) `waves/design_space_E_2026-11-24.json` with the actual seats, plus the `DESIGN_SPACE_E.md` addendum.
- Not done: no push, no qsub. random_E unread; no GP (`committed_configs.json` absent).

## Prompt 64 — ERCOT objective-selection deck (v1.1, 2026-11-18; executor writes here only)

### 2026-11-18 — deck build (executor; worktree `RTS-GMLC-e64`, branch `ercot/64-objective-deck`)

- Worktree from `ercot/tx123` 11e9ddf, at baf77c3 by build time (the 62 session's screening_v3 landing e58f4bd / 1c6e73e and the Seed-bar re-grade baf77c3 landed during the build; both optional sources used). Zero simulation; nothing pushed, nothing submitted; `extracts/n0_E` and `extracts/random_E` never opened.
- `analysis/pi_objectives/`: `ercot_objectives.pptx` (20 slides = 12 main + A, B, C×2, D×2, E, F), `objective_facts.py` (every printed number read from its source and asserted; 198 assertions → `ASSERTIONS.md`), `make_objective_figs.py` (envelope, hero IDR/bar, relief vs total MW, equations; bold labels and ticks; assert-before-draw), `make_objective_deck.py`, `deck_lib.py` (copy of pi_location @ 771aa5b), `OUTLINE.md`, `SLIDE_TEXT.md` (source line per slide), `FIGURES_USED.md`, `README.md` (not-printed list, deviations).
- Validator: All validations PASSED. Render check (Codex runtime): 20 / 20 slides looked at; overlap and footer fixes applied.
- Not printed (not in files): the "< 1 day" re-derivation estimate; a paper sentence in `waves/screening_v3/README.md` (none there); "voids the HV ledger" (reworded to plan §6.3 / §10).
- **Review round (second commit):** three reviews (fact-check, PI / audience, consistency) → B1–B8 and S1–S12 all applied (README "Review round"). Key changes: Appendix B column = "range / 11-16 median ruler" (pool_standings.csv ruler_j asserted equal to the 11-16 json); slide 1 / 3 / 11 titles name N4 as the recommendation and A′ as a disclosed post-hoc PI override; "shifts consistently with site class" replaces "locational ERCOT-wide"; one A3 sentence (22 gradable; V3 / D1 / D2 not gradable); slide 8 = 5 × 5 raw / residual matrix; sites 116 (on E1) / 91 (on N1) printed from plan AMENDMENT 2026-11-18; external snippets frozen in `external_snippets.json`. 214 assertions; validator PASSED; 20 / 20 slides re-rendered and looked at.

## Prompt 63 — ERCOT noise follow-up: zero-run corrections + wave `noise_seed_E` (v1, 2026-11-17; executor writes here only)

(pre-seeded by the strategy session; 16 Gurobi-Seed replicates at 4 n0_E designs + 2 thread checks; analysis-only, never in GP X / HV / holdout / baseline)

### 2026-11-17 — Part A (zero runs) + Part B build (executor)

Worktree `RTS-GMLC-e63`, branch `ercot/63-noise-followup`, created by the executor from `ercot/tx123` 849fdcf (the worktree did not exist yet). Rebased onto `ercot/tx123` 074c65d (61's wave) before reporting; SHAs below are post-rebase. Nothing pushed, nothing submitted. Read for n0_E: `waves/n0_E/design_matrix.csv` (X columns) and the 4 picked `retrofit_gen_dict_<idx>.json` only; no `extracts/n0_E`, no `extracts/random_E`, no landing file.

- **A1 (d265580)** `read_noise.py` excludes structural-zero perturbed copies: rule = perturbed design MW ≠ exact MW but `overall.csv` md5 equal; evidence = both capacities ≥ the site's max hourly availability. Excluded: `noise_v3/A:6`, `noise_v3/B:6` (D2, site 206, max wind 895.48 MW < 899.0 / 900.8 MW; md5 `6dde2591`). `per_candidate.<j>` ruler / levels / pooled sd / trigger / `bar` / `perturbed_delta_signed` now over 6 copies; `*_all` and `with_structural_zeros` keep the old values; rider `ercot_noise_cov.csv` unchanged (all 8). Old json kept as `ercot_noise_2026-11-16.json`; `ERCOT_NOISE.md` §10. B_j old → new: V1 14,006 → 16,173 MWh; E1 $2.064M → $2.383M; E3 $3.005M → $3.470M; R4 127.0 → 146.7; N1 99.5 → 114.9; N4 32.0 → 37.0. Trigger fires on 21 → 4 gradable ids (E1, X1, E7, V2). `RULER=0`: N2, E9 → E9 (N2 ruler 0 → 0.5). D4 B (2δ step) flagged, kept.
- **A2 (33ec7b7)** per-day RUC divergence (`ruc_quality.csv` ruc_cost), `ERCOT_NOISE.md` §11 + `ercot_noise_daily_divergence.csv`: the 6 non-structural perturbed pairs diverge on 350–365 of 365 days, all from day 1; median relative daily change 1.14e-4 – 2.54e-4; p90 6.6e-4 – 9.3e-4; 19–32 days per pair > 1e-3. D2 pairs and the 4 exact pairs: 0 divergent days.
- **A4 (0e7f880)** determinism conditions, `ERCOT_NOISE.md` §12 (read from the repo in code): Prescient a4c0849, Egret e4a244d; PCM code path last changed 6094e82 (before the first noise_v3 start; unchanged since); data `data/ercot123_2019_v2`; Gurobi version NOT discoverable from any job log under `extracts/` or `waves/*/` (env records disagree: `env/gurobi_version.txt` 11.0.2 module vs pip gurobipy 13.0.2; `module load gurobi` unpinned); Threads 4 / `-pe smp 4`; 0 TL hits, 5,840 / 5,840 RUC days OPTIMAL; max daily RUC solve noise_v3 860.7 s (B:1; 5 days > 600 s), base_v3 481.1 s (0 days > 600 s); host / CPU / node class not recorded. The array of `noise_seed_E` logs them (Part B).
- **A5 (154a854)** `tau_E.tau_res(Y, ref, Sigma_c)` = the tau_joint code path (bit-for-bit) with Σ_c, labelled REPORT-ONLY, τ_exact carried beside it; `sigma_c_from_deltas` (per-run = two-run second moment / 2; Ledoit–Wolf toward diag); `sigma_c_provisional` asserts the structural zeros are out. `analysis/noise_v3/ercot_noise_sigma_c_provisional.csv` (26 × 26, 6 pairs, LW shrinkage 0.709; per-run sd V1 3,812 MWh, E1 $561.7k, R4 34.6, N1 27.1). tau_joint / tau_marginal / rulers_from_files unchanged. No τ_res value computed here (needs the nav-start Y; 55 Part B carries the column).
- **A6 pointer** (strategy session edits 54): 54 §3 step 3 should compare the inferred GP noise against the chatter sd σ̂_c,j, not against the exact sd 0. Until Part C lands, the provisional per-run σ̂_c,j = sqrt(diag) of `ercot_noise_sigma_c_provisional.csv` (= `per_candidate.<j>.bar.sigma_hat / √2`).
- **A3 — DRAFT ONLY, not in `ERCOT_BO_PLAN.md`** (the plan EOF is serialized; the strategy session places it after a fresh rebase, 62 §6):

  > **AMENDMENT 2026-11-17b — time-limit margin erratum (≈ 1.4×; per-round monitor)** (prompt 63 A3; appendable, §10). AMENDMENT 2026-11-06b states that ruc_mipgap 0.001 "keeps a 25× margin" to the RUC TimeLimit; that figure came from January smoke days (max 46 s). Full-year v3 actuals: maximum daily RUC solve 860.7 s on noise_v3 (`noise_v3/B:1`; 5 of 5,840 RUC days > 600 s; `ERCOT_NOISE.md` §12), 481.1 s on base_v3, 824 s on n0_E with 11 of 48 runs having at least one day > 600 s (14 days; noise memo 2026-11-17 F7, `solve_time_s` / `status` only). Against TimeLimit = 1,200 s the margin is ≈ 1.4×, not 25×. No time-limit hit has occurred (0 on noise_v3 and base_v3). The identity (0.001 / 1,200 s) is unchanged. A hit makes the incumbent depend on wall-clock speed and node load; the S2 SUSPECT gate (every RUC OPTIMAL) catches it per run and stays the guard. Added: a per-round monitor in 55's `grade_round` — the count of RUC days > 600 s and the maximum daily RUC solve time of the round, written to the round record (the strategy session edits 55's spec text). Nothing else changes.

- **Part B (wave commit follows this one; nothing submitted)** `tools/make_noise_seed_E.py` + `waves/noise_seed_E/` + `tests/test_make_noise_seed_E.py`. Picks (numpy `quantile`, default "linear"; ties → lower index): q10 → n0_E:25 (T 796.994), q37 → n0_E:29 (1,082.929), q63 → n0_E:46 (1,323.884), q90 → n0_E:4 (1,463.405). 18 rows: 1–16 = 4 designs × Seed 1–4 at Threads 4; 17 / 18 = n0_E:29 at Threads 8 / 1, Seed 0. One array script, three `qsub` groups (`-t 1-16 -pe smp 4`, `-t 17-17 -pe smp 8`, `-t 18-18 -pe smp 1`), NSLOTS guard; Seed via `--ruc_solver_option Seed=k` (wrapper refuses only MIPGap / TimeLimit; verified by a test that runs the wrapper's own `build_options`); determinism lines logged before each run, collected to `conditions.txt`. Dict md5 == n0_E's (asserted). Tests: `test_make_noise_seed_E.py` 17 + `test_make_ercot_n0.py` 16 green in one process.
- **Deviations:** (1) quantile method not named by the prompt → numpy default, disclosed (Hazen / Weibull would pick 19 at 10 % and 17 at 90 %); (2) `sobol_index` empty, `tier = "contrast"` (addendum names 61's wave); (3) one array + three submissions instead of two arrays; (4) `ercot_noise_cov.csv` (rider) keeps D2; (5) Σ_c shrinkage over all 26 finite ids (Part C form), not over the 4 HV objectives only (memo A6 form); the V1/E1/R4/N1 block is read from it.

### 2026-11-18 — Part C landing (noise_seed_E COLLECTED, ercot-bot ad87c80; executor)

Read: the 18 noise_seed_E runs + ONLY the 4 n0_E anchors (n0_E:25 / 29 / 46 / 4, Seed 0, Threads 4) via `pool_row`; `waves/n0_E/landing_R.json` key `R` only (τ_res ref); nothing else of n0_E; no random_E. 22 / 22 runs v3, 0 SUSPECT, 0 time-limit hits; max daily RUC solve 821.3 s (noise_seed_E:3), 3 days > 600 s over the 18 runs; Gurobi 13.0.2 on every wave run (conditions.txt), Seed echoed in `ruc_solver_options` on rows 1–16; core-h total 589.5 (Threads-4 median 38.2, range 19.1–42.4; Threads 8 36.6; Threads 1 6.3).

- `analysis/noise_v3/read_noise_seed.py` → `NOISE_SEED_E.md`, `ercot_noise_seed.json`, `ercot_noise_seed.csv`, `ercot_noise_seed_runs.csv`, `ercot_noise_seed_sigma_c.csv` (28 × 28, LW 0.448), `fig_seed_chatter_sd.png`, `fig_seed_a3_ratio.png`; `tests/test_read_noise_seed.py` (3 green, bogp-botorch).
- σ̂_c (per run, df 16) / B_j^seed vs B_j: V1 4,376 MWh / 18,567 vs 16,173; E1 $312.4k / $1.326M vs $2.383M; R4 65.1 / 276.1 vs 146.7; N1 57.1 / 242.1 vs 114.9; N4 10.5 / 44.5 vs 37.0.
- **A3 (final):** ratio σ̂_c√2 / σ̂_pert — V1 1.15, E1 0.556, R4 1.88, N1 2.11, N4 1.20. AGREE on 20 of 22 gradable ids; DISAGREE on N1 (2.11) and E9 (perturbed ruler 0, Seed 0.32). For N1 and E9 the perturbed ruler is "perturbation response, not chatter" and B_j^seed is the bar; elsewhere both bars are reported.
- Heteroscedasticity: the 52 trigger fires on 9 of 22 gradable ids (X1, N1, N4, E6, R5, E2, R6, E3, E9); V1, E1 and R4 do not fire.
- **Thread check:** Threads 8 and Threads 1 are NOT bit-identical to the Threads-4 anchor n0_E:29 (304 / 364 divergent RUC days, from day 1; 23 / 24 ids differ; Δ 0.5–4.6 σ̂_c). Confounded with node class (thread rows on d32cepyc128; anchor host not recorded). Determinism holds only at fixed Threads and platform.
- **τ_res (REPORT-ONLY, PROVISIONAL):** E-D7 not recorded, so computed on the 4 anchor designs only: τ_res = 1.958e18 (HV_0 1.536e19; ratio 0.128) next to τ_exact = 0; with the A5 perturbed Σ_c 9.65e17.
- **54 input:** σ̂_c,j with df 16 makes the measured-floor arm live (V1 4,376; E1 $312.4k; R4 65.1; N1 57.1; N4 10.5).
- Commits: landing (this one), then the plan AMENDMENT 2026-11-18 (+ the 63 A3 time-limit erratum block) as a separate last commit after a fresh rebase.

## Prompt 62 — ERCOT objective-selection study v3: standings rerun (A) · n0_E population (B) · 16-site v3 screening `screening_v3` (C) (v1, 2026-11-17; executor writes here only)

(pre-seeded by the strategy session; Part C = 10 single-site runs at 180 MW for the non-slate screened sites; analysis-only, never in GP X / HV / holdout / baseline)

### 2026-11-17 — gates, pre-registration (i)/(ii), Part A verify (executor e62; worktree `RTS-GMLC-e62`, branch `ercot/62-objective-study`)

- **Gates (§1.1).** Worktree from `ercot/tx123` 30c7877; `merge-base --is-ancestor 62afe9e` OK; `.gitignore` carries
  `extracts/screening_v3/**/*.csv.gz` (not edited); this section exists. Interpreter `/opt/anaconda3/bin/python`
  (py3.13, scipy 1.16.3, sklearn 1.7.2). Branch rebased onto tx123 074c65d (61's wave) before (ii), then onto 6fd3352 (63 A + B) before the Part C wave commit; SHAs below are post-rebase.
- **(i) Plan AMENDMENT 2026-11-17 committed alone** (6aa29dd after the rebase onto tx123 6fd3352; block sha256 `8dd06917…a1d1e`,
  asserted by the script). Rules = prompt 62 v1.1 §3.2–§3.4 verbatim.
- **(ii) `analysis/pool/pool_n0E.py` + `tests/test_pool_n0E.py`** (6b5e85a): 11 tests green on SYNTHETIC Y at the
  real n0_E X (`waves/n0_E/design_matrix.csv` sha256 `87ee148e…b19a049`); with `test_pool_standings.py` +
  `test_pool_objectives.py` 37 green. **No n0_E Y read; no GP; random_E never read.** STOP for the strategy
  fast-forward before the Part B read.
- **Bar B_j (D2 excluded) — deviation from the prompt's quoted numbers:** V1 16,173 MWh, E1 $2.383M (as quoted),
  but N2 3.0 / N1 114.9 / N4 37.0, where prompt 62 quotes 2.60 / 99.5 / 32 (those are the 8-value, D2-included
  numbers). The pinned definition (61 §3, contract addendum) is applied; zero-bar set {E5, E9, R1, R3} as expected.
  B_j / 57-ruler spans 3.93–13.27× (prompt text 3.5–11.5×; V3's 2.3e-6 ruler sets the top). Note for 54: its
  `ercot_gp_mechanism.readability_bar` averages all 8 deltas (D2 included) — not edited here.
- **Part A (§2) — the 54 rerun reproduces.** One `RERUN 2026-11-17` block in `ERCOT_POOL_STANDINGS.md`.
  `ps.run(base='extracts/base_v3/run_index_1', noise='analysis/noise_v3/ercot_noise.json', make_figs=False)` into a
  scratch dir (with `pool_wide_v2.csv` copied in): **17 of 17 csv byte-identical** to `analysis/pool/` (16 written by
  `run` + the copied input); `pool_clusters_wavedD.json` differs only in `git_head` (scratch HEAD vs committed
  eb846a0 — the pre-rebase SHA; cosmetic, not cited further). Nothing written under `analysis/pool/` for Part A.
  Part A decides nothing; its labels enter §5 as the wave-D column.
- **(ii) follow-ups (strategy review).** e09193b: `--synthetic` mode (planted Y at the real X; refuses output under
  `analysis/pool/`; an injected `wide` requires `synthetic=True`); amendment cited via `git log -S <title>`;
  `landing_rows.csv` cross-check (suspect, G_run_usd, R1, R2; its random_E rows dropped on load); E1 failing ->
  status HALT FOR PI; combined table gains the wave-D cost-gap column, the n0_E gap read for E1/E2/E3 and a per-id
  reason; `waveD_B_readable` False for ids not graded on wave D. f7ef2d3: `bars()` reads 63 A1's re-emitted
  `ercot_noise.json` (D2 already dropped; `bar.B` asserted equal to the own computation). 15 tests green; still
  **no n0_E Y read**.
- **Part C wave built (§4.1–4.4), NOT submitted.** eae9574 = the one `make_wave_d.py` refactor commit
  (default build == committed wave D, all 26 files byte-identical; `test_make_wave_d.py` 9 green). c986da0 =
  wave commit: `waves/screening_v3/` 11 rows (ranks 7–16 read from `wave_d_selection.json` + the replicate of
  `location_oat_v2:3`), omega 0.100 (206) – 0.971 (163); `covariates.csv` pre-registered before any Y (16 sites;
  H_C(s, 180) over 4,410 h, PV on the solar profile; base_v3 own-site curtailment; DC PTDF with a load-weighted
  distributed slack — `bus.csv` has no Ref bus — on 8 pocket + 36 congested lines; buses 120/2/75 share
  L252 PTDF −0.346). README carries §4.4–§4.5 verbatim. Tests: `test_make_screening_v3.py` 11 green with
  `test_make_wave_d.py` in the same process. 11 tasks × 4 slots = 44; ≈ 232–491 core-h.
- **STOP.** Strategy: fast-forward tx123 to this branch. Kay: push, then on CRC `cd
  trial_0826/ercot/waves/screening_v3 && bash submit_this.sh` (literal `yes`). The real Part B read
  (`pool_n0E.py`, writes `analysis/pool/`) runs only after the strategy session says so.

### 2026-11-17 — Part B read (n0_E pool level; GO from the strategy session after tx123 = 6b6e178)

- Read date 2026-11-17T09:27Z; pre-registration (i) 6aa29dd, (ii) 6b5e85a + follow-ups e09193b, f7ef2d3,
  143b6a3 (citation only), 82bb71d (FIX, below). 48 rows, SUSPECT 0, landing_rows cross-check OK, D3 starts 0,
  N1_off cross-checked on 48 runs. No GP; random_E Y not read (landing_rows' random_E rows dropped on load).
- **DEVIATION — implementation fix after the first real execution.** The seat walk treated a cluster SURVIVOR as
  "absorbed": family V (V1 = survivor of {E6, V1}; V2 REDUNDANT->E4) took no seat and the first run printed M = 2.
  That contradicted the registered R-4 (skip REDUNDANT members only). 82bb71d restores R-4 (regression test added);
  nothing from the first execution was committed. Disclosed in POOL_N0E_STANDINGS.md Deviations.
- **Seats (R-4): V1 / E1 / R EMPTY / N1 → M = 3** (M != 4 reopens plan §6.4 for the PI). R family: R4 RESPONDS only
  BORDERLINE (IDR/B_j 2.11) with wave-D B_j UNREADABLE → not seat-eligible; R5/R6 NOT RESPONDS; R2 guardrail;
  R7/R8 dir '-'. X1 REDUNDANT->E1 (raw 0.982, resid 0.968). E1 RESPONDS STRONG (14.1); no HALT FOR PI.
- Clusters: {V1, E6} -> V1; {E1, E2, X1} -> E1; {E4, N5, V2} -> E4. N1–N4 SIZE-CO-MONOTONE (raw 0.950, resid 0.394),
  not redundant; N4 is the quieter member (IDR/B_j 17.4 vs 6.4). R-5 conflicts (wave-D B_j UNREADABLE, n0_E
  RESPONDS = BOX-ONLY RESPONSE): E2, E3, E6, E7, R4, R7, N1, N4, N5. Cost gap (evidence only): E1 IDR 0.83 x the
  median pair bound G_a+G_b.
- Outputs: POOL_N0E_STANDINGS.md, pool_n0E_standings.csv, pool_spearman_n0E_{raw,resid}.csv,
  pool_ed1b_combined.csv, figs/n0E/ (3 PNG; tick-label fix = plotting only). **STOP for E-D1b (PI).**

### 2026-11-18 — Part C landing (§4.5; screening_v3 COLLECTED, ercot-bot 1a2cde6; rebased on tx123 11e9ddf)

- Script `analysis/pool/screening_v3_landing.py` + `tests/test_screening_v3_landing.py` (10 green; with
  test_pool_n0E / test_make_screening_v3 / test_make_wave_d: 46 green). Rules = §4.5 verbatim in
  `waves/screening_v3/README.md` (wave commit c986da0, before any Y; asserted). Reader `ps.build_wave`; suspect_flag
  cross-check on 17 runs + base: SUSPECT 0; identity v3 everywhere. **Replicate:** screening_v3:11 overall.csv md5 ==
  location_oat_v2:3 (dc5b00da…) → no drift since 11-06.
- Pinned: graded = 23 ids (B_j > 0; **D2 dropped: 0/0 at base_v3, Δ undefined**, disclosed); Holm over 23. Moses
  exact k = 8 (coverage 0.955). TIED = within B_V1/180 = 89.9 MWh/MW of the 6th/7th value.
- **LOCATIONAL (C 8 vs far 5):** V1 −33.1 B, E1 −8.7 B, N4 −2.7 B (Holm 0.047), N5 +4.3 B, E6 +10.3 B, E3 −4.6 B,
  V3 −60.8 B (Holm 0.036 each, complete separation). Not: N1 −3.0 B_pert / −1.43 B_seed (exact p 0.093, Holm 0.65,
  interval contains 0) — NOT LOCATIONAL under both bars (63's B_N1^seed = 242.1 binding); X1 −6.1 B (Holm 0.30);
  V2 +32.6 B (Holm 0.087); E2 −1.6 B, E8 +1.0 B (separated but < 2 B). Seed-bar sensitivity: no verdict changes.
- **Bus set:** v3 top 6 = 270, 275, 274, 110, 140, 146 → SLATE BUS-SET HOLDS; 275 in, 163 out (ω 0.97 saturation;
  81 % of its relief is own-site) — prediction 3/3. No TIED site (146 / 163 at ±1.01 bands). Kendall τ_b(v2, v3)
  0.667, exact p 1.3e-4. E-D3 stands.
- **Dominance:** V1/E1/N1 — 116 (margin 0.72 B, via lower E1) and 91 (0.44 B, via lower N1) not dominated → PI flag,
  both within one bar; V1/E1/N4 — 116 only (0.72 B). E-D3 not reopened.
- E1 per site: WITHIN GAP BOUND 16/16. Covariates (descriptive): V1 ρ −0.88 with base own curtailment, +0.88 with
  pocket PTDF L252; E1 ρ −0.90 with ω (confound disclosed).
- Appended (no seat change): Part C block in §E of POOL_N0E_STANDINGS.md; C_HL_over_B / C_holm_p / C_locational columns
  in pool_ed1b_combined.csv (existing cells byte-identical). Outputs: SCREENING_V3.md, screening_v3_{sites,locational,
  covariate_rho,ranking,dominance}.csv, figs/screening_v3/ (3 PNG, bold labels + ticks, assert-before-draw).
- Code fix found at this landing (no output change): `pool_n0E.amendment_block` included the blank line before the
  next appended plan block once 61/63 appended after it, so the pinned sha no longer matched; it now strips trailing
  newlines (sha 8dd06917… reproduced on both the d706199 and the current plan).
- Seen: screening_v3 1–11, wave D L180 rows, base_v3:1, ercot_noise.json, ercot_noise_seed.json. random_E not read.

### 2026-11-18 — Part C amendment + RE-GRADE addendum (B^seed for 63-A3-DISAGREE ids)

- Plan AMENDMENT 2026-11-18 — screening_v3 actuals + reads: 1c6e73e (after a fresh rebase on tx123 11e9ddf).
- RE-GRADE (strategy request after 63 A3): `pool_n0E.py --bars seed-adjusted` substitutes the binding bar B^seed
  for N1 (114.9 → 242.1) and E9 (0 → 1.342 = json `bars.E9.B_seed`; the request quoted 0.32, which is E9's sigma_c)
  and nothing else (sigma_hat / signal share unchanged). Writes only POOL_N0E_STANDINGS_seedbar.md +
  pool_ed1b_combined_seedbar.csv; pre-registered outputs untouched.
- Result: **seats unchanged, V1 / E1 / R EMPTY / N1 (M = 3) under both bars.** N1 IDR/B 6.43 → 3.05, RESPONDS IN BOX
  (0.05 above the [2, 3) BORDERLINE band — fragile). E9 → NOT RESPONDS (was READABLE (RULER=0)), still DIAGNOSTIC.
  Sensitivity (A3 AGREE, bar not binding): R4 IDR/B_seed 1.12 (B_j 2.11), N4 14.43 (B_j 17.38).
  Descriptive: raw rho with V1 N1 0.950 / N4 0.966; composition rho N1 −0.027 / N4 0.268; N4 residual rho with E1 −0.805.

## Prompt 61 — ERCOT location-contrast wave `location_contrast_E` (v1, 2026-11-17; executor writes here only)

(pre-seeded by the strategy session; 8 analysis-only runs: P1 all-six at 60/120/180, P2 matched-total 800/1,500 MW reallocations; never in GP X / HV / holdout / baseline)

### Build the wave (v1.1 §2.1–2.5; 2026-11-17, zero simulation, worktree `../RTS-GMLC-e61`, branch `ercot/61-location-contrast` from tx123 849fdcf; 80e5d79 ancestor asserted; `.gitignore` gz line asserted, not edited)

- [x] **Wave commit `3b40c2d`** — `tools/make_location_contrast_E.py`, `tests/test_make_location_contrast_E.py`, `waves/location_contrast_E/` (9 rows, `tier = "contrast"`, `level_id` = label; dicts, array 1-9 × 4 slots, collector `--full`, submit literal `yes`; README = disclosures + §3 VERBATIM; `H_C.csv`). v1.1 has 9 rows (the pre-seed line above says 8: v1).
- [x] Table as built (MW 110/140/146/163/270/274 · total · u): P1_60/120/180 all six at 60/120/180 (u 0.08–0.32 / 0.16–0.65 / 0.24–0.97); P2_800_b120 0/0/0/98.17/306.59/395.23 · 800 · 0.530; P2_800_b275 316.01/233.88/250.12/0/0/0 · 800 · 0.933; P2_800_all 114.39/84.66/90.54/62.64/195.61/252.16 · 800 · 0.338; P2_500_270 site 270 at 500 · 0.864; P2_500_110_140 287.34/212.66 · 500 · 0.849; P3_1500_all 214.48/158.74/169.76/117.44/366.77/472.80 · 1,500 · 0.633. Matches §2.2.
- [x] H_C (MWh, 4,410 h, inputs only, no Y existed): 1,488,501 / 2,831,797 / 4,000,863 / 3,092,965 / 2,691,591 / 3,208,407 / 1,655,333 / 1,729,211 / 5,529,516. H_C(b120)/H_C(b275) = 1.1491 (predicted ≈ 1.149); H_C(270)/H_C(110+140) = 0.9573.
- [x] Tests: `pytest tests/test_make_location_contrast_E.py tests/test_make_ercot_n0.py -q` → 28 passed (12 + 16); `bash -n` clean on the three scripts.
- Deviation (README): §2.3 pins a replacement text containing "holdout" and also asks for no "holdout" in the scripts; the pinned text is kept and the check excludes that one phrase.
- **STOP — Kay action:** strategy FF tx123 → push → on CRC `cd trial_0826/ercot/waves/location_contrast_E && bash submit_this.sh`. Landing (§2.6) waits for COLLECTED.

### Landing (v1.1 §2.6; 2026-11-17, on tx123 465f99a = ercot-bot COLLECTED)

- [x] Guards: COLLECTED; 9/9 identity 0.001/1200 (+ 18 wave-D singles + base_v3:1); 9/9 `pool_full_metrics.json`; SUSPECT 0/28; `exact_pooled_sd` = 0 all ids; B_j recomputed from the 63-re-emitted `ercot_noise.json` (D2 excluded, 6 δ) = json (V1 16,173 MWh; E1 $2.38M; E3 $3.47M; R2 102.3; R4 146.7; N1 114.9; N4 37.0; R1 0). N4 = N4_L252 asserted on all 28 runs.
- [x] `analysis/location_contrast/` — `location_contrast_E.py`, `location_contrast_E.csv` (702 rows; md rendered from it only; deterministic), `LOCATION_CONTRAST_E.md`, 3 figures (bold labels + ticks; csv round-trip asserted before drawing).
- Interaction V1: g = 0.038 / 0.073 / 0.123 at 60 / 120 / 180 (predicted 0.07 / 0.12 / 0.18); guard PASS at all three; reads WITHIN 10 % / WITHIN 10 % / SUB-ADDITIVE (ΣR − R_J = 2.2 / 7.7 / 17.7 r_I) → not "ADDITIVE WITHIN 10 %" overall.
- Location: V1 raw 4–5 −23.0 B, 7–8 −2.8 B; H_C residual +3.0 / +6.7 / +6.4 / +2.9 B (4–5, 7–8, 4–6, 5–6) → LOCATION EFFECT on all four under the §3 rule (residual = "not explained by H_C"; magnitude ≤ the pre-stated ≈ 9-ruler profile-only prediction for 7–8; no network claim). N4 residual: 4–5 COMPOSITION (+0.5 B), the other three LOCATION EFFECT (−2.3 / −3.6 / −3.5 B). N1 not readable (chatter-limited). E1/E3 NOT READABLE or WITHIN GAP BOUND everywhere.
- Saturation (row 9): R = 4.03 TWh = 82.9 % of the 4.87 TWh behind-cut pool (computed 4,865,415 MWh); H_C = 1.14 × pool; e = 0.730 (lowest; row 6 0.787).
- Physics check: no-residual-location CONTRADICTED (7/8 reads); E1 within gap bound at 800 HOLDS (bounds $41.9–43.7M); R4 unreadable CONTRADICTED (2/4 pairs, both vs row 6).

## Prompt 55 — ERCOT BO machinery build (v3.1, 2026-11-13; executor writes here only)

### Part A — BUILD (2026-11-14, zero simulation, worktree `../RTS-GMLC-e55`, branch `ercot/55-machinery`, rebased on `ercot/tx123` 03eca72)

- [x] **Build commit `9dc177e`** — `analysis/methods_E/` (22 files, 3,956 lines): `arms_E.json`
  (option C = arm `qnehvi` x seed_ids 0–4 x cap 4 x q 8; B/D one edit; pinned qNEHVI block;
  guardrail / SUSPECT / calibration blocks), `common_E.py` (paths, design space, committed-config
  + loader fallbacks, `pin_bogp`, exact HV import), `_stub_loader.py` (contract 6.1 signature,
  synthetic Y, v3-identity refusal, per-run overrides), `tau_E.py` (M-general `tau_joint` /
  `tau_marginal` / sensitivity row; explicit Sigma = 0 branch; heteroscedastic D·C·D; rider levels),
  `qnehvi_E.py` (float64 SingleTaskGP per objective with the D-1025 cfg axes + floor, `optimize_acqf`
  over [0,1]^6, q 8 sequential 20 x 512, SobolQMC 128, alpha 0, prune_baseline; constrained branch =
  shed GP as the last output + botorch constraint, degenerate-constant -> dropped and recorded),
  `wave_writer_E.py` (contract-5 `__ALL__` rows mw_*/u_* full precision, retrofit dicts with mw = 0
  omitted, collision check, `.gitignore` assert; generic `methods_E_array.sh` / `methods_E_collect.sh`
  with the noise_v3 blocks), `acquire_E.py` (lanes, init, propose, C1 gate, form-agnostic
  `grade_round`, HALT files, run), `submit_state_E.py` + `submit_ready_E.sh` (login-node state
  machine, hold mode with `-hold_jid` chains, SUBMITTED markers), `acquire_E_job.sh`, runbook
  `ERCOT_BO_MACHINERY.md`, `_scratch_E.py` + `dry_round_E.py`, `DRY_ROUND_REPORT.md`.
- [x] **Donor port, lattice-free**: `assert_on_lattice` / `lattice_candidates` / `build_methods_round` /
  the omega parse are gone; `optimize_acqf_discrete` -> `optimize_acqf`; `tau45` generalised to M = 4
  and a covariance sample — `tau_marginal` with the donor floors reproduces `tau_regrade45.json`
  arms.P1 (old_3000 / scalar_285.3 / het_ii) **bit-for-bit** on the RTS 32 S1 starts (test);
  `hypervolume_exact` M = 4 three-point toy = 86.0 = botorch `Hypervolume` (test); `pareto.hypervolume`
  never imported. `write_round_section` prints every record key (the donor's silent skip is gone).
- [x] **Guardrails + SUSPECT wired (plan 1.2–1.3)**: R1 > 1 MWh -> ledger-marked, out of HV/fronts,
  kept in GP training; the round after the first violation flips `guardrail_mode` monitor -> constrain
  (constrained qNEHVI, shed <= 1 MWh); >= 2 violations in a round -> `HALT_FOR_DECISION.md`
  (propose/run/submit refuse while it exists). R2 > 891.8 MWh -> round flag only. SUSPECT -> out of HV,
  gain and (build choice, disclosed in the arm README) GP training; >= 2 -> HALT.
- [x] **Stop rule, form-agnostic, record_only**: gain_k, gain/tau and the stateless two-strike
  `would_stop_k` under tau_joint (headline) and tau_marginal (recorded) + the joint-vs-marginal
  sensitivity column, `first_fire_round` per ruler, runs to the cap; never halts on the rule or on
  C2/C3. tau = 0 -> `gain_tau` null, `would_stop` false, README states "budget-cap-only and the cap
  governs" in the plan-3 words. Arm README carries BOTH E-D5 readings labelled OPEN, the 49 v2.1
  banned-framings block verbatim, and the M = 4 any-objective false-alarm note (C2 1.5e-3, C3 4.4e-6).
- [x] **Tests green in bogp-botorch by file name** (31 passed, 23:50 wall):
  `tests/test_methods_E_tau.py` (7), `tests/test_methods_E_hv.py` (6), `tests/test_methods_E_wave.py`
  (5), `tests/test_methods_E_acquire.py` (13: init/readback, seed rule, random_E assert, record-only to
  cap + DONE, Sigma = 0, one-violation flip, two-violation HALT, SUSPECT + two-SUSPECT HALT, C1 gate
  incl. tampered mw_*/u_*/retrofit-dict refusal, C2/C3 flags never halt, STOP + double-spend, wave
  files, one REAL botorch acquisition in ERCOT_E_FAST). The other 12 acquisition tests swap the
  botorch call for `_scratch_E.cheap_propose` (same schema).
- [x] **Pinned-settings dry round** (`dry_round_E.py`, scratch root, stub loader, placeholder
  R = nadir + 0.1 span of the 48 stub n0_E rows, placeholder Sigma = diag(0.02 sd)^2):
  `init-all` 5 lanes (r1 sets pairwise disjoint; acq seeds 20261007 / 107 / 207 / 307 / 407),
  `recompute-tau` equality, s0 r1 -> r2 -> r3 (gain 47 / 22 tau; C2/C3 clean), s1 one violation ->
  constrain + r2 under the shed constraint, s2 two violations -> HALT, s3 two SUSPECT -> HALT,
  s4 one SUSPECT + R2 flag -> excluded + flagged + r2; scratch B Sigma = 0 -> tau 0, cap-only.
  qsub shim never called; six bot commits reached the scratch origin. `DRY_ROUND_REPORT.md`.
- **Timing (this Mac, M = 4, n = 32–48)**: one pinned proposal ~100 s alone (GP fit 14 s), 140–410 s
  under CPU contention; `ERCOT_E_FAST` does not help (the cost is the sequential q = 8 optimisation).
  Budget per round (standings 8): 170–360 core-h per lane; ~1 round per calendar day per lane.
- **Disclosures / build choices**: (1) SUSPECT runs are excluded from GP training as well as from HV
  (plan 1.2 names HV and gain only). (2) botorch 0.16 advises `qLogNoisyExpectedHypervolumeImprovement`;
  the plan's pinned qNEHVI is kept (one-line alternative, not adopted). (3) Plan 6.2's Sigma is the
  DELTA covariance (2x per-run under independence; tau larger by sqrt 2) — used as frozen, noted in the
  README. (4) The heteroscedastic anchor key in `ercot_noise.json.levels[]` is read defensively
  (`y` / `mean` / …); Part B pins it against the real file. (5) 54 Part A landed during the build
  (`analysis/ercot_gp/ercot_gp_loader.py`, extra `waves_dir` kwarg): `common_E.get_loader` now imports
  it in the live tree (and refuses a loader resolved outside the root, so scratch roots stay on the
  stub); Part B asserts it. (6) Tests live in `tests/test_methods_E_*.py` (own `sys.path.insert`;
  `conftest.py` untouched); `import common_E` must precede any `bogp` import (the editable
  feat/pt-system install has no `hypervolume_exact`).
### Part B step 0 — noise_v3 A + B read, exact covariance, §1.2 verdict (2026-11-16, zero simulation; run by 55 on Kay's instruction — contract 6.3 names 54 B step 0; disclosed)

- [x] **`read_noise.py` on A + B** (`analysis/noise_v3/`, commit `02d9ba0`): 16 / 16 runs at the v3
  identity, 4 / 4 exact cross-batch pairs byte-identical (`overall.csv` md5), every gradable
  candidate exact-zero → `all_exact_zero: true`, GP noise floor 0 (inferred-only 1e-9). RULER=0:
  N2, E9. Shed ≡ 0 on 16 / 16. Wall-clock (4 slots): 36.5–44.8 core-h per run,
  median 40.3, 655 total (all 16 on slow-group nodes; standings 8 group B).
- [x] **NEW `ercot_noise_exact_cov.csv`** (contract 6.3): covariance (ddof 1) of the EXACT pair
  deltas over the 22 gradable ids, rows = the 4 pairs — **identically 0 → Σ_exact = 0 → τ_joint =
  τ_marginal = 0: the stop rule is budget-cap-only and the cap governs (plan 3).** `ercot_noise_cov.csv`
  (perturbed) is labelled rider-only in the md / json. md §5b, json `exact_covariance`.
- [x] **SUSPECT + S3b + plan 1.2 verdict (md §5c, json `suspect` / `readability`, FINAL)**: per run
  S1 (max residual 9.5e-7 $), S2 (365 / 365 OPTIMAL), S3a (units 1 / 93 starts 0 on the 12 non-nuclear
  runs; n/a on the 4 nuclear); S3b per exact pair (starts equal, 4 / 4) → 0 SUSPECT. R1 PASS;
  R2 max |Δ total_cost| = $0 ≤ $1,132,088; R3 max |Δ fixed_cost| = $0 ≤ $1,325,082 (thresholds from
  `plan51_refs.json`) → **total_cost READABLE → the campaign cost objective is E1 (total_cost)**.
  Recorded once; never switched mid-campaign.
- [x] **Tests**: `tests/test_read_noise.py` 17 passed (`/opt/anaconda3/bin/python`; 5 new: exact-cov
  file zero / shape / rider labels, non-zero exact cov on an edited pair (12.25 = var ddof 1 of
  [0, 7, 0, 0]), S1 flags the fixture's total-only edits (8 SUSPECT, R1 FAIL), READABLE on an
  S1-consistent copy, NOT READABLE on a $2M pair delta (R2) and on a gen-1 starts mismatch (S3a +
  S3b)). `tests/test_methods_E_tau.py` 7 passed (bogp-botorch).
- [x] **tau_E gate (methods_E, disclosed)**: the heteroscedastic branch now applies only where the
  exact sd_j > 0 (plan 3: an exact-zero objective contributes 0 to τ; the 52 trigger fires on the
  PERTURBED levels for almost every candidate, and those anchors must never enter τ). With
  `all_exact_zero` the Part B init will compute τ = 0 regardless of the triggers.
- **Gates now**: 52 frozen incl. the exact cov ✔, §1.2 verdict ✔ (E1). Still open: 54 B
  `committed_configs.json` + E-D7, 53 `landing_R.json`, E-D5 amendment, E-D1b final objective list
  (new dated `design_space_E.json`). STOP.

- **STOP — Part A exit.** Part B waits for the five header gates: 54 B `committed_configs.json`
  (+ `E-D7_decided`), 52 frozen incl. `ercot_noise_exact_cov.csv`, 53 `landing_R.json`, E-D5 plan
  AMENDMENT (README wording), then `arms_E.json["part"] = "B"`, rerun the dry round, K6 push.
  No push by the executor; integration per contract 2 (rebase onto `ercot/tx123`, FF, Kay pushes).

## Prompt 54 — ERCOT GP loader + fit/validation pack (v3.1, 2026-11-13; executor writes here only)

### Part A — build (2026-11-14, zero data; branch `ercot/54-gp-loader`, worktree `RTS-GMLC-e54`; 0807c52)

- [x] **Loader** `analysis/ercot_gp/ercot_gp_loader.py` per contract §6.1:
  `load(waves, objectives=None, design_space, extr, floors) -> (X_mw, U, Y, meta)`,
  index = pool key. Refusals in `meta.attrs["refused"]` = {`no_overall`,
  `not_v3` (identity.txt missing / not gap 0.001 + TL 1200, via
  `read_noise.read_identity`), `site_not_in_space`: [keys]}, total in
  `meta.attrs["n_refused"]`; `floors` passed through in `meta.attrs["floors"]`.
  One-site rows → pool_row `pem_mw` (ω × gen_pmax) in the site column;
  `__ALL__` rows → design-matrix `mw_*` (round-trip float parse; asserted to
  sum to the retrofit-dict pem_mw). Y from `pool_row` only; R1 / R2 /
  G_run_usd / suspect in meta. SUSPECT = not (S1 ∧ S2 ∧ S3a); S3b (equal
  nuclear starts across exact replicates) is cross-run, not evaluated per row.
- [x] **Harness** `analysis/ercot_gp/ercot_gp_status.py`: D-1025 `FlexGP` /
  `metrics` / `binom_band` imported from the n0evidence clone (I/O
  re-implemented; RTS campaign dir removed from sys.path after import). Plan §5
  arms in tie-priority order m52+std (default, floor 1e-9) · m52+std+meas
  (iff exact sd > 0 AND df ≥ 3) · rbf+std · m52+log1p · rbf+log1p (iff
  min y ≥ 0 and max / max(min, 1) > 10); LOO-NLPD selection (> 2 paired se);
  holdout once per committed config at n0 = 32 / 48 vs [43, 48]
  (`binom_band(48, level=0.90)`); `exposure_ledger.csv` append-only; refuses
  the 25th scoring, a repeat (objective, n0), a non-plan tier, and any scoring
  after `committed_configs.json` exists; sufficiency curves LOO-only at Sobol
  prefixes 16/24/32/40/48 (config committed at 48); `committed_configs.json`
  written LAST (contract §6.2 keys + `arm`, `by_tier`, `exact_sd/df`).
- [x] **Sufficiency criterion, pinned before data** (E-D7 cites it verbatim):
  "32 is sufficient iff, for every objective, LOO cov95 at 32 is inside [28, 32]
  (binom.interval(0.90, 32, 0.95)) and LOO RMSE_32 / LOO RMSE_48 <= 1.1 and the
  committed config at 32 passes the holdout bar [43, 48]; otherwise the
  recommendation is 48."
- [x] **Smoke on committed data**: wave D → 18 WIND rows, rows 19–21 (NUC)
  refused; noise_v3 A → rows 3, 7 (site 146), rows 1/2/4/5/6/8 (sites
  275/206/1) refused; 0 SUSPECT. 53's `design_space_E.json` (99ca929) equals
  the contract and loads. Synthetic 6-D end-to-end: 4 scorings, committed
  written, re-run refused (holdout retired).
- [x] **Tests** (bogp-botorch, by file name):
  `python -m pytest tests/test_ercot_gp_loader.py tests/test_ercot_gp_status.py -q`
  → 28 passed, 1 skipped (the committed-JSON check skips until 53's freeze is
  on this branch).
- [x] **Part A STOP** (gates (i)–(iii) met 11-16/17; (iv) OPEN) — Part B waits on its four gates: (i) n0_E + random_E landed;
  (ii) noise_v3 B + base_v3 landed and `read_noise.py` run (Part B step 0,
  owned here); (iii) §1.2 verdict in `ERCOT_NOISE.md`; (iv) E-D1b → new dated
  `design_space_E.json` (`--real` refuses PENDING / PROVISIONAL objectives).

### Part B — pre-fit work (2026-11-17, zero simulation, NO n0_E Y read; HEAD after this section's commit)

- [x] **Gates**: (i) n0_E + random_E landed (53 landing a023215 / 1695153: 96 / 96 v3, 0 SUSPECT,
  `landing_R.json`); (ii) step 0 run by 55 on Kay's instruction (5ca9650: `ercot_noise_exact_cov.csv`
  identically 0 → τ = 0; S3b per pair); (iii) §1.2 verdict READABLE → cost seat E1 (`ERCOT_NOISE.md` §5c);
  **(iv) OPEN** — `design_space_E.json` is still 2026-11-13 with PENDING / PROVISIONAL seats; no n0_E Y
  has been read by this prompt. Branch fast-forwarded to `ercot/tx123` 80e5d79 (a stale no-op
  cherry-pick state was cleared with `--quit`).
- [x] **§3.5 v3.2 mechanism machinery, pinned before Y — commit `d9355f7`**
  (`analysis/ercot_gp/ercot_gp_mechanism.py`): (a) network facts computed and ASSERTED from
  `branch.csv` + base_v3 `line_summary.csv` — buses 2 / 75 / 121 exit only via bus 120 (L4, L5, L240);
  L252 700 MW, 5,426 h/yr ≥ 99 %; (b) location share L_j = 1 − Var(E[f|T])/Var(f) (40 T-quantile bins)
  and interaction share I_j = 1 − Σ first-order Sobol (Jansen) over 256 posterior sample paths on a
  Sobol base of 2^13 (seed 5454) — paths by decoupled sampling (RFF prior, 8192 features, Matern /
  RBF spectral t-draws + canonical update), verified against the exact gpytorch posterior (mean within
  0.1 sd, sd ratio 0.91–1.06); (c) the null: additive PCHIP truth through wave D's per-site V1 at
  0 / 60 / 120 / 180 MW (0 = base_v3 5.8287e6; last segment extrapolated to nameplate, floored at 0)
  and a total-only concave truth base − a(1 − e^{−T/b}) (a = 2.52e6, b = 689 MW), evaluated at the
  n0_E X (design matrix only) and refitted with the default config: **additive null I 0.0097
  [0.0050, 0.0144], L 0.026; total-only null L 0.024 [0.019, 0.031], I 0.047** → thresholds
  INTERACTION if I_p05 > 0.0144, LOCATION if L_p05 > 0.0314 (`ercot_gp_null.json`,
  `fig_null_truths.png`, `ERCOT_GP_MECHANISM_NULL.md`; recomputed with the committed config at fit
  time). Finding visible already: the wave-D site curves are so alike that the additive null's L
  (0.026) sits inside the total-only null band — L can separate the two only above ≈ 0.03.
  R4 / N1 flag suppression pinned to the contract addendum 2026-11-17 bar B_j = max(3σ̂_j, max|δ_ij|)
  with "chatter readable" ⇔ grading-tier range ≥ 2 B_j and the [43, 48] pass.
- [x] **Part B deliverables code — commit `184779e`** (`ercot_gp_status.py`): §3.3 noise cross-check
  table (inferred vs 52 exact / perturbed pooled and per-level, standardized residuals of the perturbed
  deltas, trigger reported — descriptive, adds no arm); holdout parity figures (dual latent / total
  95 % bands, bold labels + ticks, assert-before-draw); LOO sufficiency figure with per-n binomial
  90 % bands; `ERCOT_GP_STATUS.md` writer (selection, gp_status_47 grading columns, cross-check,
  sufficiency + the pinned criterion verbatim, committed configs, mechanism page, deviations); drafted
  pi-agenda E-D7 row (`pi_agenda_E-D7_draft.md`); `deliverables()` runs AFTER `committed_configs.json`
  and never touches it. `--real` now runs fit → committed → deliverables → mechanism in one command.
- [x] **Tests** (bogp-botorch, by file name): `tests/test_ercot_gp_loader.py` (13),
  `tests/test_ercot_gp_status.py` (18; +2 deliverables), `tests/test_ercot_gp_mechanism.py` (7: network
  facts from data, sampler vs exact posterior, estimators on known truths, PCHIP / concave nulls, flag
  logic + B_j suppression, a small real null run) → **38 passed**. Synthetic end-to-end with
  `--synthetic --mechanism` produces every Part B file.
- **Disclosures**: the L / I null is built on V1 and its scale-free thresholds are applied to every
  objective; the additive-null PCHIP curves are extrapolated linearly beyond 180 MW (no wave-D data
  there); the RFF path sampler is an approximation of the exact posterior (sd within ±10 % at 8192
  features, tested).
- [x] **E-D1b objective-selection study (strategy session's instruction, 2026-11-17; before any GP
  fit)** — prompt 57 Part B standings rerun on the v3 base + the 52 ruler:
  `pool_standings.py --base extracts/base_v3/run_index_1 --noise analysis/noise_v3/ercot_noise.json`
  (py 3.13; wave D + base_v3 only, no n0_E / random_E Y). Code change in its own commit `bac38e7` (pre-rebase id eb846a0)
  (minimal, disclosed): the per-level rows, gap-bound rows and heatmap titles hard-coded
  `CONTAMINATED (v2 base, v3 rows)` regardless of `--base`; the computed label is now threaded through
  (7 standings tests green; no number changed). Outputs + dated RERUN block in
  `analysis/pool/ERCOT_POOL_STANDINGS.md` (11-07 text kept): commit `d6a8933` (pre-rebase id a74a77b). **Result:** CONTAMINATED
  caveat lifted (same identity v3); ruler columns filled — every candidate with a ruler is
  LOCATION-SENSITIVE (range ≥ 2 rulers at ≥ 2 levels); **R4 (7.7 / 6.9 / 13.5 rulers) and N1 (4.9 / 9.4 /
  8.9) are no longer provisional on the ruler** (site order still unstable, W p 0.79 / 0.75; a real
  non-monotone location effect, not chatter); cost gap bound on the v3 base G_base $18.7M (was $196.7M),
  E1 8 / 18 single-site Δ GAP-READABLE under the scaled v3 pair bound, between-site ranges WITHIN; E1
  sign + vs the v3 base (+$3.8–14.1M); redundancy (C1 = {E1, V2, X1} → E1) and conflicts unchanged.
  **E-D1b table (RERUN): RECOMMENDED V1 (V), E1 (E; §1.2 READABLE), R4 (R), N1 (N) — membership
  unchanged, qualification changed; REDUNDANT→E1: X1, V2; GUARDRAIL: R2 (+ R1 dead); SURVIVORS: E4, N4,
  N5, E6, R5, N3, E2, R6, N2, E3, E8; DIAGNOSTIC: R7, R8, V3, E7, D1, D2; DEAD: E9 (wave D), E5, R1, R3.**
  The strategy session drafts E-D1b from this table.
- [ ] **STOP — waiting on gate (iv) (E-D1b → dated `design_space_E.json`, or Kay's word to fit the four
  provisional seats V1 / E1 / R4 / N1).** Then ONE command: `python analysis/ercot_gp/ercot_gp_status.py
  --real` (fits plan-5 arms at 32 / 48, LOO selection, holdout once per config per tier, exposure ≤ 8 of
  24, `committed_configs.json` LAST, cross-check, figures, mechanism flags, `ERCOT_GP_STATUS.md`,
  E-D7 draft row); then E-D7 to Kay; 55 Part B waits on `E-D7_decided`.

## Prompt 53 — ERCOT design-space freeze + n0_E / random_E waves (v3.1, 2026-11-13; executor writes here only)

(pre-seeded section)

- [x] **Freeze (§2.1)** — first commit on `ercot/53-design-space`:
  **99ca929**. `waves/design_space_E.json` byte-for-byte from contract §3
  (pmax/bus asserted = wave D to 1e-6, = gen.csv); `waves/DESIGN_SPACE_E.md`
  (bounds, u, tiers, objective statuses, guardrails). Continuity at u → 0
  (`parameters.py:139` → `_update_renewable_generator`): every PEM term
  scales to 0 with MW; the only non-scaling effect is the structural
  `<site>_PEM` twin (MIP-path noise within the v3 gap), disclosed. No
  prompt-32 constraint binds (all six WIND, PMin 0, no nuclear/hydro).
- [x] **Generator** `tools/make_ercot_n0.py` → `waves/n0_E/` (Sobol seed 53,
  `random_base2(6)`, rows 0–47; nav = first 32 per E-D7) and
  `waves/random_E/` (`default_rng(5353).random((48, 6))`; bar [43, 48],
  exposure 24, retirement, E-D2 dual pinned in its README). `__ALL__`
  schema of contract §5; `pem_mw` by `math.fsum` (bit-equal on py 3.10 /
  3.13). Min u: n0_E 1.04e-3 (row 14, site 163, 0.19 MW); random_E 1.2e-4
  (row 41, site 274, 0.09 MW). Draws bit-identical under scipy 1.15.3 and
  1.16.3. Disclosed: `tier = "grading"` on all 48 n0_E rows (nav carried by
  `sobol_index` until E-D7).
- [x] **Reader regression (§2.5, reader unchanged)**: 3 tests in
  `tests/test_pool_objectives.py` (6-site `design_row`/`pem_mw`;
  `pool_row` on a copied wave-D slim extract: V1/E1/E3/R1/R2/R4/N1 finite,
  not nuclear; generator `pem_mw` = reader on all 96 rows to 1e-9).
- [x] **Verification (§3)**: `bash -n` on 6 scripts; `/opt/anaconda3/bin/python
  -m pytest tests/test_make_ercot_n0.py tests/test_pool_objectives.py -q`
  → 33 passed (generator tests also pass in bogp-botorch).
- [x] **Budget (§2.6)**: README lines + plan AMENDMENT 2026-11-14 (wave-D
  actuals 21 / 44.6 core-h per run; 96 runs ≈ 2.0–4.3k core-h; 4.9 GB).
- [x] **K2/K3 done**: both waves submitted and collected (n0_E COLLECTED
  2026-11-15T05:53Z, 3ad3c1d; random_E 07:02Z, 4254166).
- [x] **Landing (§2.8)** `tools/land_ercot_n0.py` → `waves/n0_E/LANDING.md`,
  `landing_R.json` (contract §6.4; R over the 48 grading rows for all 29
  candidates), `landing_rows.csv` (96 rows). 96 / 96 landed, all v3, **0
  SUSPECT, R1 shed 0 on every run**, R2 max 199.9 MWh (no flag), 35,040
  RUCs OPTIMAL, 0 time limit. **3,006 core-h** (31.3 / run; 58 slow-node
  runs). Disclosed: longest RUC solve 1,157 s vs 1,200 s limit (slow node).
  Plan AMENDMENT 2026-11-16. Tests: 35 passed (`test_make_ercot_n0.py` +
  `test_pool_objectives.py`, /opt/anaconda3).

## Prompt 57 Part B — wave-D standings (2026-11-07, zero simulation, local only)

- [x] **Wave D landed** (`extracts/location_oat_v2`, 304335c; 21 rows, all
  `--full`, identity v3 = gap 0.001 / TL 1200; 7,665 / 7,665 RUCs
  OPTIMAL; 0 SUSPECT). gz tables on CRC only; E8/E9/N5 from the per-row
  `pool_full_metrics.json` (R7/R8/G/md5 asserted equal to the local slim
  recomputation on 21 / 21).
- [x] **`pool_standings.py`** (one command; `--base <wave:index | dir>`,
  `--noise ercot_noise.json`, `--no-figs`): `pool_wavedD_wide.csv` (21
  rows; `pool_wide_v2.csv` untouched), `pool_standings.csv`, per-level /
  pooled / stratified oriented Spearman CSVs + pairs, clusters JSON,
  conflicts, starts attribution, E-D1b table, gap-bound table, smoke
  identity-shift table, wall-clock table; 25 heatmaps + 5 clustermaps
  under `analysis/pool/figs/standings/`. Freeze f76d897 asserted against
  git at every run.
- [x] **Reads** (`analysis/pool/ERCOT_POOL_STANDINGS.md`): base is v2,
  rows are v3 → every Δ `CONTAMINATED (v2 base, v3 rows)` with the
  smoke-scaled identity shift beside it (R4 / N1 / E2 / E3 / R5–R7 / E8
  DOMINATED; E1 ≈ half; V1 10–20 %; X1 / E6 clean). Status by the
  base-free S′ = range / within-site 60→180 effect (S pinned, reported,
  contaminated). RULER PENDING (52) on every row. Cluster {E1, V2, X1} →
  E1 (E1–X1 +0.98: the pinned conflict did not appear). 16 survivors;
  E-D1b ≤ 4 by global order: **V1, E1, R4, N1** (R4, N1 provisional: S′
  passes, W p ≥ 0.75, discrete → ruler). Cost: every E1–E3 Δ WITHIN GAP
  BOUND; bound is 90 % the v2 base's own slack; even the v3-only between-
  site range is inside the v3 pair bound. E9 DEAD ON WAVE D. Nuclear
  rows overlay only; E1–E4 / E7 UNCORRECTED (patch cost curve); D1 NaN
  (thermal.csv.gz on CRC).
- [x] **Wall-clock** (replaces plan §8 UNKNOWN; strategy amends the plan):
  two node groups — A (15 rows) 5.1–5.5 h wall / 20.5–21.9 core-h at 4
  slots, RUC median 20–23 s; B (rows 14–19) 10.5–11.8 h / 42–47 core-h,
  RUC median 46–56 s. 584 core-h total; array 11.8 h calendar.
- [x] **Tests** `pytest tests/test_pool_standings.py tests/test_pool_objectives.py -q`
  → 23 passed (synthetic 18-row fixture: range, S / S′, planted cluster
  and trade-off, nuclear exclusion, exact W distribution mean 1/3 and
  p = 1/518,400 at W = 1). `pool_row` gained `drow` / `d` overrides.
- [ ] **Recommended, not decided:** buy ONE v3 base run (≈ 5.3 h wall /
  21 core-h on a fast node; `waves/base_v3` below), then
  `python pool_standings.py --base extracts/base_v3/run_index_1`. Re-run
  with `--noise` when 52 lands.
- Session lock `57B` inside this worktree. No push; plan not amended.

## base_v3 — the identity-v3 base run, `waves/base_v3` BUILT (2026-11-07, zero simulation, local only)

- [x] **Why**: wave D and every later campaign run are identity v3 (gap
  0.001 / TL 1200); the only base on disk (`extracts/base_2019_v2`) is
  identity v2 (gap 0.01 / TL 120). The gap smoke (task 2 vs 1, × 365/3)
  shows the identity change alone moves cost ≈ −$10.9M/yr, true
  curtailment ≈ −68 GWh/yr and starts ≈ −1,950/yr — the size of a
  single-site PEM effect — so every Δ-vs-base of a v3 run needs a v3 base.
  One run (deterministic instrument; exact replicates byte-identical). The
  v2 base stays the reference for the 31 v2 runs; never mixed (README §6).
- [x] **Build** `tools/make_base_v3.py` (wave-D conventions): one row
  (`__BASE_REPLICATE__`, full year, `design_matrix.csv` == base_2019_v2
  row 1), `retrofit_gen_dict_1.json` = `{}` (array aborts otherwise);
  array `-t 1-1`, `-pe smp 4`, `-r n`, `-q long`, SMOKE_GATE, identity
  from `waves/GAP_DECISION.json` at run time (wave-D block verbatim;
  refuses without it), `BASE_V3_START/END` stamps; collector (held; email
  on it only): `--full` → `extracts/base_v3/run_index_1`, `runtimes.csv`,
  `wallclock.csv`, `identity.txt`, `GAP_DECISION_used.json`,
  `pool_objectives.py --run-dir` → `pool_full_metrics.json`, slim + json +
  manifest committed, gz asserted unstaged, 5-retry push.
  `submit_this.sh`: branch / pull / GAP_DECISION present AND `"identity":
  "v3"` / SMOKE_PASS / data dir / dict `{}` / `--ruc_mipgap` / gitignore
  asserts, prints GAP_DECISION + `qquota`, literal `yes`. `.gitignore`:
  `extracts/base_v3/**/*.csv.gz`.
- [x] **Tests** `pytest tests/test_make_base_v3.py -q` (10 passed); `bash -n`
  on the three scripts.
- [ ] **KAY:** `cd trial_0826/ercot/waves/base_v3 && bash submit_this.sh`
  (4 slots, one full-year row, ≈ one CRC day). Can run alongside wave D.
- [ ] **Next session:** after the collector pushes, read
  `extracts/base_v3/run_index_1/identity.txt` + `GAP_DECISION_used.json`;
  point every wave-D / noise_v3 Δ-vs-base at `extracts/base_v3`, never at
  `base_2019_v2`.
- Storage: 51 MB on CRC; ≈ 3 MB in git. No push.

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
