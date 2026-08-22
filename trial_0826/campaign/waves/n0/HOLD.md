# HOLD — do not submit this wave

1. **This wave is a DRAFT generated from provisional tiers/bounds — submit
   nothing.** Pending decisions: O-M2 bid handling and the final tier
   assignment from the screening batch's noise criterion.

2. **After the PI + screening decisions land, regenerate** by editing
   `campaign/tiers.py` and rerunning `python make_batches.py n0` — same
   `SOBOL_SEED`, `skip=0`. Nothing from this draft was submitted, so a full
   redraw is safe. If the tier count changes, d changes and every point
   moves — that is expected, not a bug.

3. **The continue-the-sequence rule (doc 14 §5.1) governs waves drawn AFTER
   the released n0**, within the final box: same seed, `skip` = number of
   points already drawn, never re-seed.
