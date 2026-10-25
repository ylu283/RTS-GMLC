# BO performance table — prompt 46 (n0 = 32)

Source: `analysis/methods_C/{P1,P2,P3,N1}/ledger.json` (synced from d6 b0a6e1e). HV units: MWh·MWh·$. Every HV carries its arm's frozen ref; HV values across different refs are NOT comparable — compare HV/HV₀ only. gain/τ is relative to τ_old (prompt-30 MC, assumed floors 3,000 / 5,000 / $0.5M); the measured-noise re-grade is prompt 45's.

| arm | acq | starts | ref | rounds | evals (BO) | gain/τ_old r1 · r2 · r3 · r4 | stop | overrun checkpoints | HV₀ | HV at stop | HV at cap | HV/HV₀ stop · cap |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| P1 | qparego | S1 | R_S1 | 4 | 64 (32) | 0.69 · 0.17 · 0.62 · 0.30 | r2 live | r3 0.62 sub-tau_old; r4 0.30 sub-tau_old | 6.606e+17 (R_S1) | 7.061e+17 (R_S1) | 7.547e+17 (R_S1) | 1.069 · 1.142 |
| P2 | qparego | S2 | R_S2 | 4 | 64 (32) | 2.28 · 0.21 · 0.40 · 0.26 | r3 rule stop, record-only | r4 0.26 sub-tau_old | 1.573e+18 (R_S2) | 1.789e+18 (R_S2) | 1.808e+18 (R_S2) | 1.138 · 1.150 |
| P3 | qparego | S3 | R_S3 | 4 | 64 (32) | 0.77 · 1.28 · 0.29 · 0.30 | r4 rule stop, record-only | none (stop at cap) | 1.562e+18 (R_S3) | 1.750e+18 (R_S3) | 1.750e+18 (R_S3) | 1.120 · 1.120 |
| N1 | qnehvi | S1 | R_S1 | 4 | 64 (32) | 1.43 · 0.61 · 0.19 · 0.22 | r3 rule stop, record-only | r4 0.22 sub-tau_old | 6.606e+17 (R_S1) | 7.777e+17 (R_S1) | 7.892e+17 (R_S1) | 1.177 · 1.195 |

Stop rule: two consecutive rounds with gain < τ_old. Stops (arm-labeled): P1 r2 (live) · P2 r3 · P3 r4 (second strike AT the cap) · N1 r3. Overrun = record-only rounds after the stop; all are sub-τ_old, so no overrun reverses its stop.

**Refs (ledger-frozen):**

- **R_S1** (arms P1, N1): shed 15,102 MWh · curt 670,350 MWh · cost $652.0M; τ_old = 5.2630e+16
- **R_S2** (arms P2): shed 25,392 MWh · curt 794,884 MWh · cost $659.6M; τ_old = 7.4723e+16
- **R_S3** (arms P3): shed 25,641 MWh · curt 751,852 MWh · cost $663.2M; τ_old = 7.1230e+16

**Economics (BO_STAGE2.md §front, two distinct designs; values re-checked against waves/bo_C_r1, bo_C_r2):** cost endpoint r2#3 $510M (29 GWh shed, 1.26 TWh curt) vs reliability endpoint r1#5 (zero shed, 48 GWh curt, $668M); cheapest zero-shed design $582M.
