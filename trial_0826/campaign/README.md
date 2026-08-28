# Multi-PEM Campaign Infrastructure

Design generation, SGE array submission, and batch definitions for the
multi-PEM RTS-GMLC campaign (doc 14). Everything here is generated and
tested locally; **nothing submits jobs** — submission is done by Kay on CRC.

## Layout

| File | Role |
|---|---|
| `tiers.py` | Single source of truth: tier config (doc 14 §2.1), `SOBOL_SEED` (permanent — never re-seed), the derived-bid scheme (`derived_bid`, `RHO_SCENARIOS` — math-log §1), nameplates read from `RTS_Data/SourceData/gen.csv` at build time, ω upper bounds widened from 15a's `tm1_per_site_stats.csv` when present |
| `design_tools.py` | Sobol generation (continuation via `skip`), design-matrix construction (incl. v3 ω-only rows with derived bids + `rho_h2` column, and `omega_grid`), retrofit-dict expansion, wave writing (`manifest.json` provenance) |
| `make_batches.py` | All batch definitions → `waves/<wave>/` (see the wave inventory below) |
| `submit_array.py` | Generates one SGE array script per wave (never submits) |
| `get_row.py` | Used *by the array script* on CRC: maps `$SGE_TASK_ID` → design-matrix row, prints only scalar shell assignments |
| `resubmit_missing.py` | Lists incomplete indices, cleans partial run dirs, prints `qsub -t a-b` commands (one per contiguous range — SGE `-t` takes no comma lists) |
| `check_gurobi_license.sh` | Informational license check, run on CRC before the pilot |

Each wave dir is self-contained: `design_matrix.csv` (row `index` ==
`$SGE_TASK_ID`, both 1-based), one `retrofit_gen_dict_<index>.json` per row,
`manifest.json`, `<wave>_array.sh`.

## Wave inventory

| Wave | Rows | Design | Status |
|---|---|---|---|
| `pilot` | 12 | mid-box reference: 3 full-year repeats + 9 seven-day copies | DONE (noise floor) |
| `screening` | 12 | 11 single-site OAT + 1 all-in, B = 40 | DONE (tier verdict → d = 12 → v3 d = 6) |
| `n0` | 130 | free-B d = 12 Sobol | **SUPERSEDED — never submit** (see its `HOLD.md`) |
| `placebo` | 1 | 317 OAT at B = 0.01 (f4 split-artifact control) | pending submission |
| `contour_303x317_A` | 81 | 9×9 (ω_303, ω_317) grid, ρ = 1.0 (B = 20) | ready |
| `contour_303x317_B` | 81 | same grid, ρ = 1.5 (B = 30) | ready |
| `contour_303x317_C` | 81 | same grid, ρ = 2.0 (B = 40) | ready |
| `sweep_B` | 54 | per-tier OAT ω sweeps (6 tiers × 9 levels), ρ = 1.5 | ready |
| `sweep_C` | 54 | same sweeps, ρ = 2.0 | ready |

**Submission order suggestion:** `placebo` (1 job) and `contour_303x317_A`
first — ρ = 1.0 is the current-market headline; then `contour_303x317_B` and
`_C`; sweeps after. Each contour/sweep wave is ~81/54 full-year jobs ≈ 10 h
wall as one batch. After each batch: `summarize_wave.py` → commit CSVs →
push. Per math-log §4.2, run the 81-point LOOCV resolution gate on batch A
before firing B and C blind.

**Screening g4/g5 backfill (Kay, on CRC):** the new objective columns
(`reserve_shortfall_mwh`, `thermal_starts`, deltas) were backfilled into
`waves/pilot/objectives.csv` locally, but `waves/screening/runs/` exists
only on CRC (run outputs are untracked) — run
`python summarize_wave.py waves/screening` there once and commit the
refreshed CSVs. Old columns are regression-guarded byte-identical by
`tests/test_derived_bid.py`.

**Contour grid ordering (reconstruct the 9×9 from `index`):** row-major with
ω_303 as the OUTER axis — `index = 9*i303 + i317 + 1`, where `i303`/`i317`
index each tier's `omega_grid(9, lo, hi)` (evenly spaced, endpoints
included). So index 1 = (ω_303 lo, ω_317 lo), index 9 = (lo, hi), index 10 =
(2nd ω_303 level, lo), index 81 = (hi, hi). The sweep waves use the same
`omega_grid` levels, so the 303/317 sweeps are the contour axes' f(ω, 0)
margins for the math-log §4.3 interaction index (f(0,0) = the base case,
external).

**v3 derived-bid waves** (math-log §1–2): the design space is ω-only
(d = 6); every `<tier>_bid` column is FILLED with `derived_bid(rho_h2)` =
20·ρ_H2, never sampled, and the `rho_h2` column records the batch's price
scenario (A/B/C = 1.0/1.5/2.0 $/kg). Each ρ scenario needs its own PCM runs
(B enters the simulation).

## How Kay runs it on CRC (in order)

1. **Sync the repo** to CRC (`git pull`; the wave dirs and scripts are
   committed — submit them as-is).
2. **License check:** `bash campaign/check_gurobi_license.sh` (after
   `module load gurobi`). Full-year jobs hold a license ~40 h each; this is
   the top pre-campaign risk (doc 14 §5.2).
3. **Pilot:** `cd trial_0826/campaign/waves/pilot && qsub pilot_array.sh`.
   Submit **from inside the wave dir** — the committed script derives every
   path from `$PWD` (with `#$ -cwd`), which is what keeps it free of local
   checkout paths. Before the first submission, set the exact gurobi module
   version in the `GUROBI_MODULE` variable at the top of the script.
4. **Verify / fill gaps:**
   `python ../../campaign/resubmit_missing.py .` from the wave dir — it
   prints one `qsub -t a-b pilot_array.sh` per contiguous missing range.
5. **Noise floor** (acceptance criterion feeding tier assignment, doc 14 §6
   item 3): the std of the 3 full-year pilot repeats' objective columns —
   one line, e.g.
   `df.groupby(level=0).std()` over indices 1–3 outputs, or simply
   `pd.concat([read_objectives(i) for i in (1,2,3)]).std()`.
   This calibrates the screening threshold and the GP nugget.
6. **Screening:** `cd ../screening && qsub screening_array.sh` (12
   concurrent full-year jobs — this is also the sustained license-concurrency
   demonstration).
7. **n0 — SUPERSEDED:** `waves/n0/` is the d12-era free-B draft, replaced
   by the derived-bid ω-only scheme; see its `HOLD.md`. Never submit it.
   Submit the v3 waves per the inventory table above instead.

## Notes and deliberate deviations

- **Pilot shape** (deviation from doc 14 §6 item 1 "10–20 concurrent
  full-year jobs"): 3 identical full-year runs (noise floor) + 9 seven-day
  copies (concurrent submission + license load). Sustained full-scale
  license concurrency is instead demonstrated by the screening batch's 12
  concurrent full-year jobs; this pilot buys the same engineering signal at
  ~1/10 the CPU cost.
- **Prescient options and the gurobi module pin live in the generated,
  version-controlled SGE script — not in `manifest.json`** (deviation from
  doc 14 §5.1). The manifest records git SHA + dirty flag, tiers, Sobol
  seed/skip/n, scipy version, and the `environment.yml` sha256.
- **The n0 center anchor (index 129) duplicates the pilot reference design
  by construction** — a bonus 4th repeat for the noise floor while tiers are
  unchanged. Do **not** "deduplicate" it.
- The base case is never re-run: it appears only in `n0/external_anchors.csv`
  (`source_dir=trial_0826/base_case_pcm_test`, index 0 — outside 1..N).
- Retrofit dicts use the `PEM_bid` key only; `PEM_indifference_point` is a
  deprecated alias accepted by `parameters.py` for back-compat, never
  emitted here.
- Regenerating waves: commit code changes first — `manifest.json` records
  the git SHA + a dirty flag (`git status --porcelain -uno`, tracked
  modifications only) so the SHA describes the generator.

## Tests

`pytest trial_0826/campaign/tests/ -q` — hermetic (waves are rebuilt in a
pytest temp dir; nothing under `waves/` is touched). Conda-base python3 has
pytest/scipy/pandas.
