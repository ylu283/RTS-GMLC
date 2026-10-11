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
