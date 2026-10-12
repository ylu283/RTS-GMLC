# ercot123_2019_v2 — provenance

**What:** TX-123BT (Lu et al., arXiv:2302.13231v3) in RTS-GMLC / egret
`rts_gmlc` format, 2019 profiles. Identical to `../ercot123_2019/` (v1)
except the cost and start-up columns of the 128 thermal units (CT 113,
COAL 13, NUC 2) in `gen.csv`. The 10 other CSVs are byte copies of v1
(md5 in `MANIFEST.md`). For everything that did not change (upstream
source, metadata fixes: `Tr Ratio`, `L` branch UIDs, year-end padding,
pointers) see `../ercot123_2019/MANIFEST.md` and `../ercot123_2019/PROVENANCE.md`.

**Why v2 (prompt 36, 2026-10-12):** v1's `gen.csv` (from
`demo_processing_XC.ipynb`) set `HR_avg_0 = Csu·Pmax/fp` (start-up heat in
the average-heat-rate slot), `HR_incr_k = ΔC_k/fp` (segment heat where egret
reads a rate) and every start column to 1. Egret therefore saw nuclear
no-load ≈ $2.1–2.6M/h and near-free start-ups. Every v1 output is invalid as
system evidence (`INVALID_v1_costs.md` markers).

**Built by:** `trial_0826/ercot/tools/convert_tx123_costs.py --reading c`
from `analysis/cost_fix/source_coeffs_tx123.csv` (frozen by
`analysis/cost_fix/t0_verify_sources.py` from `Generator_data.xlsx` and the
authors' `123bus_case_final.pkl`; facts in `analysis/cost_fix/T0_FACTS.md`).

**Cost reading (c), Kay 2026-10-12:** linear C(P) = C0·u + C1·P with the
paper/xlsx coefficients (×1.0; the authors' pkl holds 0.7× these, documented
only by a code comment); start-up = Csu·PMax, Csu in $/installed MW (paper
Table III, eq. 2). C2 dropped (the paper gives 0.0016 for coal only; the XC
notebook applied it to every unit).

**Column translation (reference: `RTS_Data/SourceData/gen.csv`):**

| column | v2 value |
|---|---|
| `Output_pct_0..3` | PMin/PMax, then equal thirds to 1.0 (4 points as RTS); 22 units use 2 points (PMin, PMax) because the fork's 6-decimal fuel rounding makes their equal slopes fail egret's convexity check — list in MANIFEST |
| `HR_avg_0` | 1000·(C0 + C1·PMin)/(fp·PMin) BTU/kWh — average heat rate at PMin incl. no-load |
| `HR_incr_k` | 1000·C1/fp BTU/kWh on every segment |
| `Start Heat Cold/Warm/Hot MBTU` | Csu·PMax/fp (all tiers equal; all start times are 1 h, egret collapses them to one start cost) |
| `Non Fuel Start Cost $` | 0 |
| `Fuel Price $/MMBTU` | v1 (gas 2.29, coal 1.78, nuclear 0.81035); cancels in every cost |
| `C0`, `C1`, `C2`, `Csu` | informational (egret ignores): source C0, C1, 0, Csu |

**Prescient-required assumptions kept from v1 (not in the authors' model,
which has no min up/down):** min up/down ("ref 24" map: gas 2/1 h, coal
12/12 h, nuclear 48/48 h), ramp rates (xlsx), start times 1 h, PMin = 0.3·PMax.

**Remaining differences from the authors' SCUC** (Table VI is not a fair
validation target): CONOPT (NLP; integrality ignored) and LP-dual prices vs
Prescient MIP; daily-minimum dynamic line ratings vs static ratings; reserve
= largest unit vs `reserve_factor` 0.1 + $500 shortfall; no min up/down;
independent 24 h days vs 36 h RUC with carried state; hydro $12.3/MWh in the
paper vs 0 in code and here; PV PMax ×0.3 in the pkl vs xlsx PMax here.
