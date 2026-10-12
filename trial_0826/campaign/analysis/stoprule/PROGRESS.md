# Prompt 37 — execution PROGRESS (executor-owned; strategy consolidates)

## 2026-10-12

- STEP 0: worktree `~/Documents/GitHub/RTS-GMLC-stoprule`, branch `stoprule`
  from `origin/d6` @ d1e3814. No d6 merges/pulls after STEP 0.
- Started on v1.1; the prompt was revised to **v2** mid-session. The v1.1
  build (emulator posterior mean + Z-1/Z-2) was killed before it wrote
  anything (G4 was running → v2 forbids 6-D truth builds then). Kept and
  reworked to v2: sr_common, problems, runner, rules, collector, tests.
- `ENV_READY.md` (bogp-botorch, botorch 0.16.1) landed on origin/d6 @ deb5f42
  during the session → M3 enabled locally (2-D only).
- M3 = verbatim copy of 35's local `methods_C/qnehvi.py` (not yet committed
  by 35; sha256 in PREREG) + `batch_ehvi`. If 35 changes that file before
  CRC submission, diff and record here.
- 35's **G4**: one full-lattice qNEHVI proposal at n = 40 = 962 s wall on 4
  threads (≈ 1.07 core-h), peak RSS 2.4 GB → full-lattice M3 ≈ 9+ core-h
  per 8-round run, 400 runs ≥ 3,600 core-h > 1,500 → the pre-registered
  candidate-subset rule applies to all 6-D M1/M3 rounds.
- Local timing (Mac, 4 threads): 2-D M3 run (15 rounds, R-C) ≈ 420 s
  (13→44 s/round); 2-D M1 run ≈ 10 s. 340 replay M3 runs ≈ 40 h locally →
  moved to the CRC array (block E); replay M1/M4 stay local.
- OCD logic verified: Wagner, Trautmann & Naujoks (EMO 2009) stop when
  EITHER the χ² variance test or the trend t-test indicates convergence.
- Z problems built (fronts: needle 60, plateau 52, dis 25 lattice points;
  Stage-2-design density 28/24/10 of 48 noisy vs real 26). Z-needle basin:
  891 cells (well ≥ 10 % of depth, not dominated by the base front),
  random-hit probability within 64 draws 10 %, 24 of 60 true-front points,
  15 % of H* (union box).
- Note: the replay grids are dense at M = 4 (15–77 of 81 non-dominated;
  R-C 73) — expected to tie across methods (PREREG §6).
