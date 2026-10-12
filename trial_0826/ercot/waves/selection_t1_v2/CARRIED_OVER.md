# selection_t1_v2 — rows carried over from v1 selection

`waves/selection_t1` rows 3–11 (rows 1–2 were base replicates; on v2 they are
wave A `base_2019_v2`). Matrix lines and retrofit dicts are byte-identical to v1;
the array runs `-t 3-11` so indices keep their v1 meaning. Carried over from v1
selection, NOT v2 choices.

Rows 6–11 (site 1, NUC) measure FORMULATION A: the multi_pem thermal patch
replaces gen-1's p_cost with the PEM bid and forces u ≡ 1 (needs fix `1eaf05e`).
gen-1's own v2 behaviour comes ONLY from wave A and non-retrofit rows.
