# INVALID — v1 costs (prompt 36, 2026-10-12)

**What:** `SCREENING_ERCOT.md`, `screening_noise_ruler.json` (and the screening notebook / site-effects / summary files derived from the same v1 extracts) in this directory. `analysis/cost_fix/` is NOT covered.

**Why:** these outputs were produced on `data/ercot123_2019/` (v1), whose
`gen.csv` mis-converts the TX-123BT thermal costs for all 128 units:
`HR_avg_0 = Csu·Pmax/fp` (start-up heat in the average-heat-rate slot →
nuclear no-load ≈ $2.1–2.6M/h), `HR_incr_k = ΔC_k/fp` (segment heat read as a
rate) and every start column = 1 (start-ups ≈ free; merit order inverted).
They are invalid as evidence about the system (costs, commitment, prices,
curtailment, rankings). Kept for provenance — never deleted or overwritten.

**Pointer:** v2 data `data/ercot123_2019_v2/` (MANIFEST.md, PROVENANCE.md);
facts `analysis/cost_fix/T0_FACTS.md`; re-runs `waves/{smoke_v2, base_2019_v2,
screening_v2, selection_t1_v2}`; read-outs `analysis/cost_fix/ERCOT_COST_FIX.md`.
