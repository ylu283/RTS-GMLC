# ERCOT design space E — freeze (prompt 53 §2.1; contract 2026-11-13)

Machine-readable twin: `waves/design_space_E.json`, written byte-for-byte
from `admin/prompt/bogp/53-55-shared-contract.md` §3. This file explains
it; on any disagreement the JSON wins. Plan §2 is the procedure frozen
here; this is its instantiation. Zero simulation at this commit.

## 1. Sites and bounds (d = 6)

Slate rule: E-D3 fallback = wave-D top-6 (`analysis/cost_fix/WAVE_D_TOPK_RULE.md`);
prompt 32 T2 was never bought. Nuclear is NOT in the space (D6 not
adopted; d = 6, not 7).

| column | site | type | bus | gen_pmax = upper bound (MW) | lower bound |
|---|---|---|---|---|---|
| mw_110 | 110 | WIND | 2   | 338.599998942999   | 0 |
| mw_140 | 140 | WIND | 2   | 250.5999989428539  | 0 |
| mw_146 | 146 | WIND | 75  | 267.9999991911224  | 0 |
| mw_163 | 163 | WIND | 120 | 185.3999876467921  | 0 |
| mw_270 | 270 | WIND | 120 | 578.9999877407346  | 0 |
| mw_274 | 274 | WIND | 120 | 746.3999877635443  | 0 |

`gen_pmax` and `bus` were re-read from the wave-D design matrix
(`waves/location_oat_v2/design_matrix.csv`) and asserted equal to the
JSON to 1e-6 at freeze; the generator re-asserts it at every build.
They also equal `data/ercot123_2019_v2/gen.csv` PMax. Per-site box,
never one shared bound (746.4 / 185.4 ≈ 4×; plan §2).

- **u (GP and acquisition input):** u_s = mw_s / gen_pmax_s ∈ [0, 1]
  (plan §2), a deterministic box normalization before the GP's own
  standardization. PEM_fraction = u_s.
- **0 = absent:** mw_s = 0 exactly → the site is OMITTED from the
  retrofit dict (never ω = 0; the RTS make_row assertion).
- **Bid:** 40.0 $/MWh at every site. **Period:** 2019-01-01, 365 days.
- **No lattice:** candidates are continuous (plan §2; prompt 55 §2).
- **Solver identity:** v3 (`ruc_mipgap = 0.001`, `ruc_time_limit =
  1200`; `waves/GAP_DECISION.json`, E-D6).

## 2. Tiers

| tier | rows | source |
|---|---|---|
| nav | 32 or 48 — E-D7, decided after prompt 54 Part B | the first 32 / 48 of the Sobol draw (prefix of the grading tier) |
| grading | 48 = max(8d, 48) | `waves/n0_E`, Sobol(d=6, scramble, seed 53) `random_base2(6)` rows 0–47 |
| holdout | 48 | `waves/random_E`, `default_rng(5353).random((48, 6))` |

## 3. Objectives (NOT final)

| id | seat | status |
|---|---|---|
| V1 | V | RECOMMENDED (E-D1b provisional standings, pi-agenda 11-07) |
| E1 | E | PENDING plan §1.2 verdict from prompt 52 (READABLE → E1 total_cost; else E3 var_cost) |
| R4 | R | PROVISIONAL (E-D1b, PI) |
| N1 | N | PROVISIONAL (E-D1b, PI) |

Rule: ≤ 4 objectives, one per family, frozen global order V < E < X < R
< N (plan AMENDMENT 2026-11-06). The final list is a NEW dated version
of the JSON after E-D1b and the §1.2 verdict; this version is kept. The
waves do not depend on the list: X and the `--full` extracts are the
same for any list, and the landing ref point R is computed for all 29
pool candidates (contract §6.4).

Objective source: `pool_objectives.pool_row(key)` on the committed slim
tables. The per-run `pool_full_metrics.json` carries only
E8/E9/N5/headroom/R7/R8/G_run_usd/gap/md5 and is never the Y source.

## 4. Guardrails and SUSPECT

- **R1 load shed (MWh):** monitor → constrain. Violation = shed > 1 MWh.
  The violating run stays in the ledger, infeasible-for-claims,
  excluded from reported fronts. From the round AFTER the first
  violation, acquisition = constrained qNEHVI with a shed GP constraint
  shed ≤ 1 MWh. ≥ 2 violations in one round → HALT FOR DECISION (plan §1.3).
- **R2 reserve shortfall (MWh):** monitor only; round flag at 2 × base =
  891.8 MWh; never halts; no acquisition role.
- **SUSPECT** (plan §1.2 S1–S3 per run): excluded from HV and gain and
  flagged; ≥ 2 SUSPECT in one round → HALT FOR DECISION.

## 5. Continuity at u → 0 (contract §5)

Read: `trial_0826/multi_pem/parameters.py:139 update_function_multi`
→ `_update_renewable_generator` (all six sites are WIND, so the thermal
branch never runs), applied before every RUC and every SCED by
`multi_pem/utils.py` (`_modify_DA`, `_modify_RT`). With C = u ·
gen_pmax:

| PEM term | form | at C → 0 |
|---|---|---|
| parent wind p_max(t) | max(0, avail(t) − C) | → avail(t), the base value |
| twin `<site>_PEM` p_max(t) | min(C, avail(t)) | → 0 |
| twin offer cost | p_cost = bid (40 $/MWh) × dispatched MWh ≤ 40 · C · 8760 | → 0 |
| H2 (= twin curtailment, excluded from V1 by `is_pem`) | ≤ C · 8760 MWh | → 0 |
| parent + twin capacity | = avail(t) for every C | unchanged |
| must-take check | asserts p_min = 0; all six sites have PMin 0 in gen.csv | never fires |

**Verdict: every PEM modeling term scales to 0 with MW.** There is no
fixed (MW-independent) cost, capacity or energy term. The one thing that
does not scale is **structural**: at any u > 0 the twin generator exists
as an extra unit in the RUC/SCED; at u = 0 it is absent. A
zero-capacity twin adds no energy and no cost, but it changes the MIP,
so the solver may stop at a different incumbent within the v3 gap
(0.001; G_run_usd records the bound). This is solver-path noise of the
order already measured by prompt 52, not a modeled discontinuity.
Disclosed for any reading of the response near u = 0.

Where the designs sit: Sobol never lands on 0 (min u over the 48 grading
rows = 1.044e-3 at `sobol_index` 13 = wave row 14, site 163 → 0.194 MW;
the same row is the minimum of the first 32). The random_E minimum is
u = 1.20e-4 at row 41, site 274 → 0.089 MW.
`optimize_acqf` can clamp to exactly 0, which takes the omitted (absent)
branch. No minimum MW, no snapping: full float precision.

## 6. Constraints from prompt 32's rules

None bind on this slate:
- ω lattice (`STAGE2_LATTICE`): replaced by the continuous box (plan §2).
- D6 nuclear ω cap: nuclear is not in the space.
- Shared-bus cluster pooling (bus 120: 163/270/274; bus 2: 110/140): an
  analysis rule for effect shares, not a design constraint; every site
  is an independent dimension here.
- Must-take renewables (nonzero p_min): none of the six sites.
- Hydro keep/exclude: no hydro in the slate.
- `__ALL__` naming: the multi-site rows reuse `oat_site = "__ALL__"`
  (contract §5). The label is per wave (pool key `wave:index`), so it
  cannot collide with `screening_ercot` row 10.
