# Random baseline PROGRESS (prompt 34 v2.1)

Lock protocol: each local invocation writes `34` to
`trial_0826/campaign/.session.lock` and deletes it on close. Routing on
every invocation after `git pull` (d6): FAILED marker → report + stop;
`waves/random_C/objectives.csv` with 48 rows → T2; wave dir without
results → "awaiting collector"; else T1.

## T1 (2026-10-11)

- [x] Builder `make_batches.build_random_baseline` + support templates
  (PAIRGRID collector/submit merged with BO `-r n`, PYTHONNOUSERSITE,
  `cd dirname`, `-terse` collector JID validation; stale-FAILED cleanup;
  48-row finite-M objectives check) + `tests/test_random_baseline.py`.
  Registered `random_C` in BUILDERS with `WAVE_MAX_CONCURRENT = None`.
- [x] Tests: base suite 84 passed / 3 skipped (74 + 10 new; the real-wave
  manifest test skips until the build); BO suite 8/8 (bogp env).
- [x] Recipe set R checked against the 3 BO_STAGE2 knees BEFORE submission
  — all three in R unchanged (n0b#8 1,699 MW / wind share 0.79; r1#2
  1,705 / 0.68; r1#6 1,606 / 0.72 — r1#6 sits 6 MW above the 1.6 GW
  floor). R frozen in the manifest as written in the prompt (no loosening).
- [x] §5 Sobol-continuation arm: **OFF** (prompt default; no explicit
  choice from Kay at build time) — recorded in the manifest.
- [x] Wave built from a clean tree (`make_batches.py random_C`, base env,
  scipy 1.16.3): manifest git_sha a368668, dirty False, 48 rows, 48 draws /
  0 rejections, 0 cross-arm overlaps, exclusion sha256 a2bd9df34210…;
  real-wave test green (11/11).
- [ ] **Kay:** send the §0.1 expectation statement to the PI, THEN on CRC
  bastion/login node: `cd trial_0826/campaign/waves/random_C && bash submit_this.sh`
- [ ] Collector lands → T2 (re-invoke the prompt).

Budget: ~15 core-h/run × 48 ≈ 715 core-h; wall ≈ 1 day if all 48 dispatch
at once, plan ≈ 2 days with queue holds.

## Submission log
SUBMITTED random_C: array=1526985 collector=1526986

## T2 — analysis (2026-10-11, routed (b): objectives.csv 48 rows, collector ce16936)

- [x] Lock 34 taken (no prior lock). No FAILED marker.
- [x] R_union computed once before any HV → `ref_union.json` (equals BO_STAGE2 REF48 exactly).
- [x] Gates: bo-gp HEAD == ledger sha 60e6328; BO HV n=32/40/48 rel err 0.0 (gate 1e-9).
- [x] HV rate logged: 0.454 ms/call (48 points), 12 spawn workers; full T2 ≈ 10 min.
- [x] Primary (§3.1): row "above" at both refs — p̂48 0.942 [0.836, 1.000] R_frozen; 1.000 [1.000, 1.000] R_union. p̂40 0.962 / 0.959.
- [x] §3.3 robustness: 0.467 of draws keep "above" → headline carries "not robust to floor-level output perturbation".
- [x] §3.4 secondaries in order; S2(iii) recipe counter-examples reported (rnd#2, r2#1, rnd#43).
- [x] `random_baseline.ipynb` executed; `RANDOM_BASELINE.md`; `t2_summary.json`; figs 1–4.
- [x] BO_STAGE2.md edits (1)–(4) only.
- [x] Tests: `test_primary_ignores_arm`, `test_percentile_ties_count_half` (base suite 87 pass / 2 skip).
- [x] Living-report row 2026-10-11c + math-log §5.2 log line (admin repo; `prompt/bogp/` is untracked there — NOT committed).
- No further random or BO runs in this prompt (red line). Next: second BO seed (new prompt).
