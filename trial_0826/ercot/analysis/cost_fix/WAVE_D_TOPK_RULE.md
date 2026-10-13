# Wave D `location_oat_v2`: pre-registered top-k rule (prompt 36 §4.2, unchanged)

Committed after wave B (screening_v2) landed at 02:30 on 10-13, before any
per-site screening_v2 value was read. The rule text below is copied verbatim
from prompt 36 §4.2:

> - Pre-registered top-k rule (commit before B lands): rank sites by
>   screening_v2 Δtrue_curtailment per MW; keep sites with |Δ| > 2× the
>   A ruler; k = 6 if ≥ 6 qualify, else all qualifying (min 4, fill by
>   rank). Plus nuclear (formulation A; label it).
> - Sizes: 3 ABSOLUTE MW levels (PI 10-08). `PEM_fraction = MW / p_max`
>   (thermal) or `MW / gen_pmax` (renewable). Builder ASSERTS the largest
>   size ≤ the smallest qualifying site's `gen_pmax` (`_update_renewable_generator`
>   clamps silently above nameplate). Kay confirms the sizes before build.
> - Each site alone, other sites absent. 15–21 rows, ≈ 1.0–1.6k core-h.

Operational definitions. These carry over the v1 screening conventions in
`analysis/SCREENING_ERCOT.md`; none of them is new.

- **true_curtailment:** curtailment from `compute_objectives.py`, taken from
  the non-PEM WIND + PV rows of `gen_summary`. It is not the `overall.csv`
  curtailment, which is PEM-contaminated.
- **Δ:** the screening_v2 row's value minus the base_2019_v2 value. Ranking
  is by relief per MW of the screened PEM size, where relief = −Δ, largest
  first.
- **A ruler:** the replicate pairwise |Δ| in true_curtailment over the three
  base_2019_v2 rows.

Fallback stated in advance: if the A ruler is 0 (byte-identical replicates),
the threshold 2 × ruler is 0. Every site with a nonzero Δ then qualifies, so
the rule reduces to the top 6 by rank.
