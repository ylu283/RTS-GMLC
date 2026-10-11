# random_C — Stage-2 random baseline (prompt 34)

48 uniform random STAGE2_LATTICE designs at scenario C (rho = 2.0, B = 40),
all six tiers present, none repeating the 48 already-evaluated designs
(stage2_C_n0, stage2_C_n0b, bo_C_r1, bo_C_r2). Analyzed as ONE i.i.d. pool
against the BO campaign (analysis/random_baseline/). Draw procedure, seeds,
exclusion hash, the full draw log, the frozen recipe set and the §5
decision are in manifest.json["random_baseline"].

Indices 1..48 = 16*(arm-1) + arm_order; `arm` is provenance only.

Submit ON CRC from the login node (compute nodes are not submit hosts):
`cd trial_0826/campaign/waves/random_C && bash submit_this.sh`
(d6 guard + pull, array without -tc / without email, chained collector
with email; appends the SUBMITTED line to analysis/random_baseline/
PROGRESS.md and pushes it).
