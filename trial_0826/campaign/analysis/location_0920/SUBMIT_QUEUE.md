# Pair-grid submit queue — Kay's staggered handoff (prompt 28 T1)

The 3 priority pairs go via `block_1.sh` in this directory. The **11
remaining waves below are built, tested, and pushed** — each is
fire-and-forget: its `submit_this.sh` does the d6 guard + pull, submits
its own 81-task array (no `-tc`) and its own chained collector
(`-M ylu28@nd.edu -m ea` on the collector only, one email per wave).
Stagger at your discretion; there are no cross-wave dependencies.

**Honest budget:** ~9.7 h wall per run, single slot (pi_0911 §3.2) →
~790 core-h per 81-run wave. All 14 waves = 1,134 runs ≈ **11k core-h**
(the 3 priority waves are 243 runs ≈ 2.4k core-h of that).

Run each from the CRC main d6 clone:

| ✓ | Wave | Command | Cost |
|---|------|---------|------|
| ☐ | pairgrid_nuclear_tail_C | `cd trial_0826/campaign/waves/pairgrid_nuclear_tail_C && bash submit_this.sh` | ~790 core-h |
| ☐ | pairgrid_nuclear_wind_122_C | `cd trial_0826/campaign/waves/pairgrid_nuclear_wind_122_C && bash submit_this.sh` | ~790 core-h |
| ☐ | pairgrid_nuclear_wind_303_C | `cd trial_0826/campaign/waves/pairgrid_nuclear_wind_303_C && bash submit_this.sh` | ~790 core-h |
| ☐ | pairgrid_pv_wind_122_C | `cd trial_0826/campaign/waves/pairgrid_pv_wind_122_C && bash submit_this.sh` | ~790 core-h |
| ☐ | pairgrid_pv_wind_303_C | `cd trial_0826/campaign/waves/pairgrid_pv_wind_303_C && bash submit_this.sh` | ~790 core-h |
| ☐ | pairgrid_pv_wind_317_C | `cd trial_0826/campaign/waves/pairgrid_pv_wind_317_C && bash submit_this.sh` | ~790 core-h |
| ☐ | pairgrid_tail_wind_122_C | `cd trial_0826/campaign/waves/pairgrid_tail_wind_122_C && bash submit_this.sh` | ~790 core-h |
| ☐ | pairgrid_tail_wind_303_C | `cd trial_0826/campaign/waves/pairgrid_tail_wind_303_C && bash submit_this.sh` | ~790 core-h |
| ☐ | pairgrid_tail_wind_317_C | `cd trial_0826/campaign/waves/pairgrid_tail_wind_317_C && bash submit_this.sh` | ~790 core-h |
| ☐ | pairgrid_wind_122_wind_303_C | `cd trial_0826/campaign/waves/pairgrid_wind_122_wind_303_C && bash submit_this.sh` | ~790 core-h |
| ☐ | pairgrid_wind_122_wind_317_C | `cd trial_0826/campaign/waves/pairgrid_wind_122_wind_317_C && bash submit_this.sh` | ~790 core-h |

`pairgrid_wind_303_wind_317_C` does **not** exist by design — the
existing `contour_303x317_C` (81/81 complete) IS that pair; level
equivalence to STAGE2_LATTICE is verified with `np.allclose(atol=1e-9)`
in the analysis provenance (the old CSV stores raw-linspace doubles, so
exact `==` fails at one level).

Results return via each collector's `pairgrid-bot` push to d6 (push
retry loop ×5 with randomized backoff — up to 4 bot pushers share the
branch). A `FAILED_<wave>.md` marker in a wave dir means the integrity
gate found missing runs; recovery is `resubmit_missing.py` (interactive)
or a manual `qsub -t a-b`, then re-running the collector.
