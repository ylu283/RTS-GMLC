# stage2_backfill_C — lattice back-fill OAT rows (B = 40)

10 full-year rows riding the stage2_C_n0 submission: nuclear OAT at the 8
new-lattice levels the old [0.05, 0.5] sweep never ran (only 0.05
coincides), plus pv OAT at 0.88125 and 1.0 (the old pv box tops out at 0.8,
so those two levels are EXTRAPOLATION, not interpolation — same gap class
as nuclear). Coverage status by tier: wind lattice-matched (old box == new);
tail interpolable (old box [0.02, 1] spans the lattice); pv interpolable
below 0.8, now measured at 0.88125/1.0; nuclear measured on the full
lattice; B-scenario back-fills deferred.

Indices 1-8: nuclear at STAGE2_LATTICE[1:]; indices 9-10: pv at
STAGE2_LATTICE[7:]. Built with stage2_tiers(); bids derived (B = 20*rho,
scenario C: rho = 2.0 -> B = 40).
