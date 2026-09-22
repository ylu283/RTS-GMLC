# stage2_C_n0b — n0 top-up 16 -> 32 (prompt 27; Kay GO 09-21)

16 more full-year rows CONTINUING the stage2_C_n0 scrambled-Sobol
sequence (TOPUP_RECOMMENDATION.md mechanics, doc 14 SS5.1): same d = 6
engine and seed, skip = n_drawn_total read from the n0 manifest (never
re-seed), global draws 17+, snapped to STAGE2_LATTICE, deduped against
ALL kept post-snap rows (the n0 16 and this wave's own) with block
redraws on collision. Wave-local indices 1-16 (SGE contract); the
manifest's sobol dict records skip, the cumulative n_drawn_total for the
NEXT continuation, and continues_wave = stage2_C_n0. snap_map.json draws
are numbered by GLOBAL sequence position.

Submission was DEFERRED behind the 3 priority pairgrid waves (Kay
09-21); those completed 09-21, so this wave is clear to submit ON CRC
from inside this directory: `bash submit_this.sh` (d6 guard + pull,
array without -tc, chained collector with email).
