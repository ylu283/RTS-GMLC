# replicate_C_noise_b — prompt 41 replicate wave B (shed noise floor)

6 PCM runs at scenario C (ρ = 2.0, B = 40), 1 slot per task, production
solver config unchanged. This is the SECOND of two waves. Its sibling
`replicate_C_noise_a` holds the other copies, so that each exact×exact pair is a
CROSS-environment pair. The selection, rows and recipe are pre-registered
in prompt 41 §2–§3. The builder is
`analysis/noise_floor/build_replicate_waves.py` (manifest `git_sha`
4598462, dirty = False).

## Expectation (prompt 41 §0.1, written before submission)

> "Preview from 4 accidental cross-wave replicates: sd ≈ 306 MWh,
> 95% CI ≈ [180, 880]. Expected: the measured floor lands well below
> every recorded stop's break-even (1,133–1,997 MWh), flipping the
> stop decisions and shrinking τ ~7×. The cross-wave exact pairs are
> the primary measurement; if they all come back byte-identical, the
> production noise is zero at identical inputs and the GP floor
> question moves entirely to the perturbed population — which the
> function-term envelope biases UPWARD, i.e. toward KEEPING the
> recorded stops, against our expected conclusion. The high-shed
> design tests the level-dependence hint (per-design sd ~1,775 vs
> ~306). The LOW pick sits on a deterministic 6-design shed plateau
> (429.528861 MWh exactly), so its shed noise may read 0 — curt/cost
> still informative there. Every outcome is informative."

## Rows (tier order nuclear, pv, tail, wind_122, wind_303, wind_317)

| index | design | role | parent | ω | perturbed tier | h to parent |
|---|---|---|---|---|---|---|
| 1 | LOW | exact | `methods_C_P2_r3:7` | 0.05, 1, 0.64375, 0.2875, 0.7625, 0.88125 | — | 0.00000 |
| 2 | LOW | perturb-2 | `methods_C_P2_r3:7` | 0.05, 0.998, 0.64375, 0.2875, 0.7625, 0.88125 | pv | 0.00211 |
| 3 | MID | exact | `methods_C_P1_r3:8` (≡ `methods_C_P2_r1:5`) | 0.05, 0.05, 0.05, 0.05, 0.64375, 0.7625 | — | 0.00000 |
| 4 | MID | perturb-2 | `methods_C_P1_r3:8` (≡ `methods_C_P2_r1:5`) | 0.05, 0.05, 0.05, 0.05, 0.64375, 0.7615 | wind_317 | 0.00105 |
| 5 | HIGH | exact | `methods_C_P1_r3:3` (≡ `methods_C_P3_r2:3`) | 0.05, 0.05, 0.05, 0.05, 0.05, 0.05 | — | 0.00000 |
| 6 | HIGH | perturb-2 | `methods_C_P1_r3:3` (≡ `methods_C_P3_r2:3`) | 0.052, 0.05, 0.05, 0.05, 0.05, 0.05 | nuclear | 0.00211 |

- **Selection** (304 non-grid pooled C runs; strata by shed LOW ≤ 3,000 /
  MID 3,000–25,000 / HIGH ≥ 35,000 MWh):
  - LOW `methods_C_P2_r3:7`, shed 429.53. 176 in stratum; no accidental
    pair. Closest to the median, 6-way tie, broken by (wave, index).
  - MID `methods_C_P1_r3:8`, shed 4,645. 124 in stratum; first of the
    accidental-pair designs by (wave, index).
  - HIGH `methods_C_P1_r3:3`, shed 38,927. 2 in stratum; the all-0.05
    accidental pair.
- **Perturbation:** δ = 0.001 on the largest-ω tier, with ties broken by
  sorted tier order.
  - Wave A takes perturb-1 and wave B takes perturb-2.
  - LOW, pv = 1.0: 0.999 / 0.998.
  - MID, wind_317: 0.7635 / 0.7615.
  - HIGH, 6-way tie → nuclear: 0.051 / 0.052.
  - No value clips onto a bound. All realized PEM_fraction values are
    exact at 4 decimals (design_tools.py:183).
- **Normalized distances** (raw δ / 0.95):
  - MID: exact–perturb 0.00105, perturb–perturb 0.0021.
  - LOW/HIGH: exact–perturb-1 0.00105, exact–perturb-2 0.0021,
    perturb–perturb 0.00105.
- **Exact copies are verified byte-identical** to the parent's
  `retrofit_gen_dict` and design row. The MID and HIGH exact copies are
  also verified against the accidental twins (`methods_C_P2_r1:5`,
  `methods_C_P3_r2:3`).
- **No contamination of the pool:** the wave name matches none of
  pool.py's wave lists or globs (checked: `wave_groups()` contains no
  `replicate*`).

## Solver path untouched: generated array script vs `random_C_array.sh`

```diff
2c2
< #$ -N random_C_array
---
> #$ -N replicate_C_noise_b_array
5c5
< #$ -t 1-48
---
> #$ -t 1-6
9c9
< #   cd <wave_dir> && qsub random_C_array.sh
---
> #   cd <wave_dir> && qsub replicate_C_noise_b_array.sh
```

These differences are the name and the task count only. The array has no
`-tc` and no `-pe`, and it does not set PYTHONNOUSERSITE (PCM0826 needs
the networkx in ~/.local). The collector
(`make_batches._render_random_collector("replicate_C_noise_b", 6)`) differs from
`collect_random_C.sh` only in the wave name and the 6-row check. It DOES
export PYTHONNOUSERSITE=1. This asymmetry is deliberate.

## Submit (Kay, CRC login node; do not chain)

Submit wave A first. Confirm that its tasks are RUNNING (`qstat`). Then
submit wave B. The time gap between the two is the environment split.

```bash
cd /groups/adowling/ylu28/RTS-GMLC && git checkout d6 && git pull origin d6
cd trial_0826/campaign/waves/replicate_C_noise_b
J=$(qsub -terse -r n replicate_C_noise_b_array.sh | cut -d. -f1); echo "$J"
qsub -r n -hold_jid "$J" -M ylu28@nd.edu -m ea collect_replicate_C_noise_b.sh
```
