# screening_v2 — rows carried over from v1 selection

`ercot/` = `waves/screening_ercot` (12 rows) and `topup/` = `waves/screening_topup`
(7 rows), design matrices and retrofit dicts copied BYTE-FOR-BYTE (md5-asserted by
`tools/make_v2_waves.py`). The slate was chosen from v1 (mis-costed) extracts; these
rows are carried over from v1 selection, NOT v2 choices. `make_screening_topup.py`
was not re-run. `replicate_of` values refer to rows of the same sub-matrix
(`ercot/` row 11 = base replicate, row 12 = replicate of row 1).

Task map: SGE task 1–12 → `ercot/` row = task; 13–19 → `topup/` row = task − 12.
Runs: `runs/<sub>/run_index_<row>`; extracts: `extracts/screening_v2/<sub>/run_index_<row>`.
