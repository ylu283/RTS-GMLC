# HOLD — do not submit this wave

1. **This wave is a DRAFT — submit nothing yet.** Tier structure is FINAL
   (d = 12, screening verdict 2026-08-24); still pending: the PI decisions
   (O-M2 bid handling, O-15 constraint, f5) from doc 16.

2. **After the PI + screening decisions land, regenerate** by editing
   `campaign/tiers.py` and rerunning `python make_batches.py n0` — same
   `SOBOL_SEED`, `skip=0`. Nothing from this draft was submitted, so a full
   redraw is safe. If the tier count changes, d changes and every point
   moves — that is expected, not a bug.

3. **The continue-the-sequence rule (doc 14 §5.1) governs waves drawn AFTER
   the released n0**, within the final box: same seed, `skip` = number of
   points already drawn, never re-seed.
