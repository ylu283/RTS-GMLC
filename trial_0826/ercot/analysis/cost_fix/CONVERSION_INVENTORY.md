# TX-123BT cost-conversion inventory (prompt 36 T0, 2026-10-12)

Read-only sweep of `research/gtep`, every repo under `~/Documents/GitHub`
(idaes-gtep*, bo-gp*, dispatches*, RTS-GMLC*), `~/Downloads` and
`~/Documents/development`. Data facts only.

Check value: gas Gen 2 (PMax 304.6, PMin 91.38, C0 597, C1 27.85, Csu 69,
fp 2.29). **9177.9 = v1 bug** (Csu·PMax/fp); 15,014.5 = correct average
heat rate at PMin under reading (c).

**No file applies a 0.7 factor to costs.** The ×0.7 exists only inside the
authors' `123bus_case_final.pkl` (T0_FACTS.md). Every converter reads the
xlsx coefficients.

## Converter code

| id | file | modified | HR_avg_0 | HR_incr | start columns | C2 |
|---|---|---|---|---|---|---|
| A | `gtep/123_bus_coal/ERCOT_BUS123_base_XC_editeddata/demo_processing.ipynb` (Kolf original) | 2026-02-11 | `= C0` | `HR_incr_1 = C1`; Output_pct 0.6 / 1 | Non Fuel = raw Csu; Start Heat blank | — |
| B | `…/demo_processing_XC.ipynb` (v1 source) | 2026-01-22 | `Csu·PMax/fp` | `diff(C0+C1p+C2p²)/fp` (segment heat, no ×1000/ΔP) | blank | 0.0016 all |
| B′ | `…/1_demo_processing_XC.ipynb` | 2026-01-06 | as B | as B, but pct order bug → HR_incr_3 < 0 (Gen 2: −1760.99) | blank | 0.0016 all |
| B″ | `…/original_data/2_demo_processing_kay copy.ipynb` → `data_123_bus_kay/` | 2026-04-09 | as B | as B | all start columns = 1 | 0.0016 all |
| B‴ | `idaes-gtep/gtep/data/retirement_allowed_no_extreme_half_load_local/demo_processing_prescient.ipynb` | 2026-05-28 | as B | as B | = 1 | 0.0016, then map G 0.008 / C 0.02 / N 0.003 |
| C | `output_to_prescient.ipynb` — 8 identical copies (5 in `gtep/123_bus_coal/retirement_*/`, 3 in `idaes-gtep/gtep/data/retirement_*_half_load/`) | 2025-05 / 2026-05 | `= C0` (from GTEP gen.csv), fp = 1 | `= fuel_cost3` | Non Fuel = raw Csu; Start Heat 1 | — |
| D | `idaes-gtep/retirement_allowed_no_extreme_{full_load,2hr_commit,4hr_commit}/convert_to_prescient_2035.py`, `idaes-gtep/gtep/pcm_analysis/convert_gtep_to_prescient_2035{_extreme.py,.ipynb}` | 2026-05-28 | `1000·C(PMin)/(fp·PMin)` (rate — correct form) | `1000·ΔC/(fp·ΔP)`, then fp overwritten = fuel_cost3/(HR_incr_1·0.001) | inherited from B‴ (= 1): start-up cost lost | from B‴ (0.003–0.02) |
| D′ | `idaes-gtep/gtep/pcm_analysis/convert_gtep_to_prescient_2035_executed.ipynb` (pre-fix) | 2026-05-28 | v1 value kept | fp = fuel_cost3 | inherited | inherited |
| E | `RTS-GMLC-ercot/trial_0826/ercot/tools/convert_tx123_costs.py` (this prompt, v2) | 2026-10-12 | `1000·(C0+C1·PMin)/(fp·PMin)` | `1000·C1/fp` | Start Heat = Csu·PMax/fp, Non Fuel 0 | 0 (reading c) |

Authors' `Run_SCUC_annual.py` / `formpyomo_UC.py` read the pkl directly (no
conversion). dispatches (both copies), bo-gp `src/`, Downloads (incl. zips):
no TX-123 cost conversion.

## gen.csv outputs (numerically checked)

| gen.csv | rows | producer | Gen 2 HR_avg_0 | thermal rows with HR_avg_0 = Csu·PMax/fp |
|---|---|---|---|---|
| `RTS-GMLC-ercot/trial_0826/ercot/data/ercot123_2019/gen.csv` (**v1**) | 292 | B″ (md5 b738d495…) | 9177.9 | 128/128 |
| `gtep/…/original_data/data_123_bus_kay/gen.csv` | 292 | B″ (same md5) | 9177.9 | 128/128 |
| `bo-gp/raw_data/ercot123_2019/gen.csv`, `bo-gp-clean/raw_data/ercot123_2019/gen.csv` | 292 | B″ (same md5) | 9177.9 | 128/128 |
| `idaes-gtep/gtep/data/retirement_allowed_no_extreme_half_load/Prescient_2/gen.csv` | 292 | B″ (same md5) | 9177.9 | 128/128 |
| `gtep/…/ERCOT_BUS123_base_XC_editeddata/gen.csv` | 292 | B′ (HR_incr_3 < 0 on all 128) | 9177.9 | 128/128 |
| **`idaes-gtep/gtep/data/123_Bus_Coal/gen.csv` (live GTEP input; `driver_coal*.py`)** | 292 | B′ (HR_incr_3 = −1760.99) + Non Fuel = 69, capex/fuel_cost columns | 9177.9 | 128/128 |
| `idaes-gtep/gtep/data/retirement_allowed_no_extreme_half_load_local/Prescient_2/gen*.csv` | 282–292 | B‴ | 9177.9 | 128/128 |
| `idaes-gtep/gtep/data/retirement_allowed_no_extreme_half_load/Prescient_2_2035/gen.csv` | 278 | D′ (fp = 24.59) | 9177.9 | value still the bug |
| `idaes-gtep/retirement_allowed_no_extreme_{full_load,2hr_commit,4hr_commit}/Prescient_2_2035/gen.csv`, `idaes-gtep/gtep/data/retirement_allowed_{extreme,no_extreme}_half_load{,_local}/Prescient_2_2035/gen.csv` | 278–288 | D | 15,333.7 (C2 0.008), fp rescaled 1.747 | 0 (start-up = 1) |
| `gtep/123_bus_coal/retirement_*/Prescient*/gen.csv`, `gen_allowed_no_extreme.csv`, `idaes-gtep{,-eval}/gtep/data/123_Bus_Coal/Prescient/gen.csv`, `…/Prescient_2/gen_old.csv` | 278–374 | C | 597 (= C0), fp = 1 | n/a |
| `idaes-gtep{,-eval}/gtep/data/123_Bus_Resil_Week/gen*.csv`, `idaes-gtep-eval/gtep/data/123_Bus_Coal/gen.csv`, `idaes-gtep-eval/explorations/coal_upstream/output/{,crc/}_data/123_Bus_Coal/gen.csv` | 419–582 | A | 597 (= C0), fp = 0 | n/a |

## GTEP (report only — prompt 36 §5)

- The live GTEP input `idaes-gtep/gtep/data/123_Bus_Coal/gen.csv` carries the
  v1-style values (B′, incl. negative HR_incr_3). History: A-style up to
  `7988b00` (2025-04-24); replaced by the B′ output in `8606d58`
  (2026-02-11); trimmed / columns restored in `e90e8c9`, `c9e715e`,
  `b1e8268` (Apr–May 2026).
- For non-RTS-GMLC system names GTEP takes `fuelCost` from egret's
  `p_cost["values"][1]` (`gtep_model.py:2924-2931`, built from
  HR_avg_0/HR_incr) and `startupCost` from `non_fuel_startup_cost`. Not
  traced: whether `texas_case_study_updates` overrides them.
- The 2035 Prescient inputs (D) use the rate form but inherit start-up = 1
  and rescale fp. 123_Bus_Resil_Week and all of idaes-gtep-eval are A-style.
