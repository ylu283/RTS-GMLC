# ERCOT / Texas 123-bus Raw Data — Provenance

**Added to repository:** 2026-08-03 by Kay (commit `c1d639a`, "Upload ERCOT raw data")
**Provenance documented:** 2026-08-03
**Status:** ⚠️ Provenance is **partially** established. Verified facts are in
§1–§4. Items only Kay or Alex can supply are in §6 and are required to close
step S1 of `quality_reports/living_report/main.tex` §8.

---

## 1. Upstream source

This is **not** an ERCOT-published dataset. It is a *synthetic* Texas
transmission system, referred to upstream as **TX-123BT**.

| Field | Value |
|---|---|
| Dataset name | Texas Synthetic Power System Test Case (**TX-123BT**), 5-year profiles |
| Distribution | <https://rpglab.github.io/resources/TX-123BT/> (RPGLab) |
| Describing publication | J. Lu, X. Li, H. Li, T. Chegini, C. Gamarra, Y. C. E. Yang, M. Cook, G. Dillingham, "A Synthetic Texas Power System with Time-Series Weather-Dependent Spatiotemporal Profiles," **arXiv:2302.13231v3** |
| Upstream scope | 123-bus backbone transmission system with spatio-temporally correlated solar, wind, dynamic line rating, and load profiles at 1-hour resolution for **five continuous years** |

The paper's own headline numbers, useful as a sanity check on our runs: hourly
dynamic line ratings cut operating cost from \$8.09M to \$7.95M (−1.7%), raise
renewable dispatch 1.3%, and lower average LMPs from \$18.66 to \$17.98/MWh.
Note those LMPs are well below RTS-GMLC's ~\$30/MWh mean — do not expect
cross-network comparability of absolute economics.

**Terminology note.** We have been calling this "ERCOT 123-bus" throughout the
living report and refactor notes. It is a *synthetic Texas* system, not an ERCOT
model. Keep the informal name if convenient, but write-ups should say
"TX-123BT synthetic Texas 123-bus system" and cite arXiv:2302.13231.

## 2. Transformation chain

The committed CSVs are a **processed derivative** of the upstream release, not a
verbatim copy. The conversion to Prescient/Egret input format was done by
`demo_processing_XC.ipynb`, currently living outside this repository in the shared
Google Drive at `Kay_Lu_research/RTS-GMLC_NEPEM_base_case/data_123_bus_XC/`.

That notebook reads from an upstream folder named
`Texas Synthetic Power System Test Case (TX-123BT) 5year profiles/Data_public_5year`
(files `Bus_data.csv`, `Line_data.csv`, …) and writes `bus.csv`, `branch.csv`,
`gen.csv`, and the load/renewable timeseries in the shapes committed here.

> **Recommendation:** commit `demo_processing_XC.ipynb` to this repository.
> Without it the derivation from TX-123BT is not reproducible, and the notebook is
> currently single-copy in a cloud-synced folder.

The committed files are **byte-identical** (all nine MD5s verified 2026-08-03) to
`Kay_Lu_research/RTS-GMLC_NEPEM_base_case/data_123_bus_2019/`, which is the
immediate source of this commit.

## 3. File inventory

| File | Rows (excl. header) | MD5 (first 12) |
|---|---|---|
| `bus.csv` | 123 | `a83144a1fefe…` |
| `branch.csv` | 255 | `df72b63b4f21…` |
| `gen.csv` | 292 | `b738d4951373…` |
| `DAY_AHEAD_load.csv` | 8,760 | `96b78d9d755e…` |
| `REAL_TIME_load.csv` | 8,760 | `96b78d9d755e…` |
| `DAY_AHEAD_solar.csv` | 8,760 | `20d799754349…` |
| `REAL_TIME_solar.csv` | 8,760 | `20d799754349…` |
| `DAY_AHEAD_wind.csv` | 8,760 | `b0eb20289f9b…` |
| `REAL_TIME_wind.csv` | 8,760 | `b0eb20289f9b…` |

Timeseries are keyed `Year,Month,Day,Period` with `Period` = 1–24 (hourly), and
span **2019-01-01 through 2019-12-31** (8,760 rows = non-leap year). Load columns
are numbered bus IDs.

There is **no `reserves.csv`**, consistent with the prior CRC run logs which
report "did not find reserves.csv; assuming no reserves."

## 4. System composition (verified by inspection)

- **123 buses, 255 branches, 292 generators.**
- Fuel mix by unit count: 113 gas (`G`), 82 wind (`W`), 72 solar (`S`),
  13 coal (`C`), 10 hydro (`H`), **2 nuclear (`N`)**.
- Nuclear units: `GEN UID 1` at bus **107**, PMax **2430.0 MW**; `GEN UID 93` at
  bus **111**, PMax **2708.6 MW**.

The two nuclear units are the retrofit sites for case study CS3a; the 82 wind
units are the candidate pool screened in step S7.

## 5. ⚠️ Two properties that affect the study design

**5.1 Day-ahead and real-time profiles are identical.** `DAY_AHEAD_load.csv` and
`REAL_TIME_load.csv` have the *same MD5*, and likewise for solar and wind. There
is therefore **zero forecast error** between the day-ahead and real-time stages.

This matters for objective $f_4$ (unserved energy). In
APEN-D-26-14824 §2.3, shortfall and over-generation events arise substantially
*because* Prescient's day-ahead commitment uses forecasts that the real-time
dispatch then corrects. With DA ≡ RT, that mechanism is absent: any unserved
energy reflects genuine capacity or transmission limits, not mis-forecasting.
Either accept and document this, or construct a forecast-error variant. Tracked as
part of open item O12 (network comparability).

**5.2 The committed year is 2019; the prior CRC runs are dated 2035.** The two
completed annual base-case runs in
`Kay_Lu_research/ERCOT_Bus123_basecase/results_timelimit3600_{Kay,Xinhe}/` report
"Dates to simulate: 2035-01-01 to 2035-12-31" and 8,760 SCED solves. The data
committed here is stamped 2019.

Since TX-123BT provides five continuous years of *weather-dependent historical*
profiles, the most likely explanations are (a) the dates were remapped to 2035 to
place the study in a future year, or (b) those runs used a different profile year
or a different processed folder. This is **unresolved** and matters because the
measured 113 h and 132 h runtimes, and the "2035" framing in the living report,
are attached to those runs rather than demonstrably to this data. See §6.

## 6. TODO — required to close step S1

Only Kay or Alex can supply these; do not guess.

- [ ] **Download date** of the TX-123BT release, and its version/release identifier
      if the distribution provides one. If the site is unversioned, record the
      retrieval date and archive a checksum of the downloaded archive.
- [ ] **License / redistribution terms** for TX-123BT, confirming this data may be
      committed to a repository that may become public.
- [ ] **Which of the five profile years** this is, confirmed against the upstream
      release rather than inferred from the folder name.
- [ ] **Resolve the 2019 vs 2035 discrepancy** in §5.2: were the prior runs a date
      remap of this data, or a different input set?
- [ ] **Commit `demo_processing_XC.ipynb`** (§2), or record where it is archived.
- [ ] Confirm whether a `reserves.csv` should exist and was intentionally omitted
      (§3), since this differs from the RTS-GMLC configuration.

## 7. Still outstanding: RTS-GMLC

RTS-GMLC data is **not yet in this repository**. It is currently only available on
Alex's machine via the pip package `dispatches-rts-gmlc-data` 23.6.30 inside the
`dispatches-fe-testing` conda environment. Vendoring it here — with the upstream
`GridMod/RTS-GMLC` commit hash that package builds from — is the remaining half of
step S1. See `quality_reports/refactor_notes.md` §4c.
