# noise_v3 pick rule (prompt 52 v2.1; pinned BEFORE the pick is computed)

Written by `tools/make_noise_v3.py` before `pick_table.csv`. The code applies
the rule; there is no manual override. Changing this text after the pick is
an amendment and must be disclosed.

## Disclosure

The v2 table was public before this rule was written (`SCREENING_ERCOT.md`,
`analysis/pool/POOL_V2.md`, `pool_delta_v2.csv`). The author had seen it.
The v2-identity values choose designs ONLY. They are never data: every
noise_v3 run is a v3 run (`waves/GAP_DECISION.json`), and no v2 value
enters `ERCOT_NOISE.md`.

## Rule

1. **Pool.** The 22 rows `screening_v2/ercot:1, screening_v2/ercot:2, screening_v2/ercot:3, screening_v2/ercot:4, screening_v2/ercot:5, screening_v2/ercot:6, screening_v2/ercot:7, screening_v2/ercot:8, screening_v2/ercot:9`,
   `screening_v2/topup:1, screening_v2/topup:2, screening_v2/topup:3, screening_v2/topup:4, screening_v2/topup:5, screening_v2/topup:6, screening_v2/topup:7`, `selection_t1_v2:6, selection_t1_v2:7, selection_t1_v2:8, selection_t1_v2:9, selection_t1_v2:10, selection_t1_v2:11` of
   `analysis/pool/pool_delta_v2.csv` (frozen f76d897). Byte-identical
   duplicates (`selection_t1_v2:11` = `:8`, design D21) count once: 21
   distinct designs (16 VRE single-site, 5 nuclear).
2. **Objectives.** The 22 gradable candidates = the first
   22 ids of `global_order` in `pool_definitions.json`. A candidate
   with no value on any pool row (E8, E9, N5: the v2 extracts are slim) is
   listed in the table as NOT USED and does not enter the score.
3. **Composition.** 3 VRE single-site designs + 1 nuclear
   design (proportional to the pool, 16 : 5, and to wave D, 18 : 3; the
   ruler is transferred to the wave-D sites, prompt 57 section 3 A4).
4. **Score.** For a set S of 4 designs and a used objective j,
   spread_j(S) = (max_S delta_j - min_S delta_j) / (max_pool delta_j -
   min_pool delta_j), with delta = value - base over the 21 designs.
   score(S) = mean_j spread_j(S). Exhaustive search over all
   C(16, 3) x C(5, 1) sets; the maximum wins.
5. **Tie.** The set whose tuple of pool positions (pinned order above) is
   lexicographically smallest.
6. **Table.** `pick_table.csv`: one row per gradable candidate with the
   achieved spread, the pool min/max and which design holds each, and the
   4 picked values. Correlated candidates collapse strata: they show the
   same designs at min and max. That is made visible, not hidden.

## Copies (prompt 52 section 3, v2.1)

- EXACT copy: the v2 design's `omega`, `gen_pmax`, `bid` byte-for-byte;
  one in batch A, one in batch B (the cross-batch exact pair).
- PERTURBED copy: `pem_mw' = pem_mw x (1 + s x 0.001)`, `omega' =
  pem_mw' / gen_pmax` (nuclear: `/ 2430.0`); the sign `s` of the
  first copy of each design is drawn from `numpy.random.default_rng(52)`
  (recorded as `perturb_sign`, seed as `perturb_seed`); a second copy
  (layout 16) is antithetic (`-s`). Corner rule: if `pem_mw'` leaves
  `[0, gen_pmax]`, the sign is flipped inward; if that collides with the
  other copy, the inward step is `2 x 0.001`.
