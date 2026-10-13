# selection_t1_v2 — rows carried over from v1 selection

`waves/selection_t1` rows 3–11 (rows 1–2 were base replicates; on v2 they are
wave A `base_2019_v2`). Matrix lines and retrofit dicts are byte-identical to v1;
the array runs `-t 3-11` so indices keep their v1 meaning. Carried over from v1
selection, NOT v2 choices.

Rows 6–11 (site 1, NUC) measure FORMULATION A: the multi_pem thermal patch
replaces gen-1's p_cost with the PEM bid and forces u ≡ 1 (needs fix `1eaf05e`).
gen-1's own v2 behaviour comes ONLY from wave A and non-retrofit rows.

**Rerun after the T0 fix (2026-10-13).** All v2 nuclear rows (6–11) were rerun
after the multi_pem thermal patch was fixed to lift gen 1's `initial_p_output`
to the raised p_min. Before the fix, T0 was the parser default (the original
p_min, 729 MW).

- Rows 6–7 (ω 0.05 / 0.2875) died at the first RUC build: "Generator 1 has
  less output at T0 than is feasible to ramp up to".
- Rows 8–11 finished, but started day 1 at T0 = 729 MW.
- Those first-run dirs are kept in `runs/quarantine_T0_729/` and are not used.
- Rows 3–5 (renewable sites) keep their first runs.
- Regression test: `multi_pem/tests/test_t0_build.py`.
