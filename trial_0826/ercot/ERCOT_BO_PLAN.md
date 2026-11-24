# ERCOT BO campaign: plan of record (E-track station 0, prompt 51)

Status: FROZEN 2026-10-28, executor session, branch `ercot/tx123`, at
HEAD `7c5fb8d` plus this commit. Zero simulation.

The plan is **append-only**. §10 gives the amendment protocol.

- **What this plan freezes:** FORMS and RULES.
- **What later prompts do (52–56):** they fill in the NUMBERS and may
  not change a rule.

Every number quoted here comes from `analysis/bo_plan/plan51_refs.json`.
The script `analysis/bo_plan/plan51_refs.py` produced it from the
artifacts it names.

**Playbook pinned:** GP-BO 作战手册,
https://claude.ai/artifact/M58M7cShkSabFZCdFR99wT (stations 0–8). This
plan ports stations 0–6 to ERCOT. Stations 7–8, freeze-and-assert and
adversarial review, apply to every E-track deliverable without change.

**Blind-freeze statement.** No v2 solver-identity confirm run exists at
this commit, and this plan reads none.
- Origin holds one commit this checkout has not pulled: `7a511ed`
  (ercot-bot, 2026-10-13 20:40, "selection_t1_v2" extracts and
  `noise_ruler_v2_v2.json`).
- I listed its file names only. I did not read its contents before this
  freeze (§2 status).

## 0. Inputs and status at freeze (corrected)

| input | status at freeze |
|---|---|
| v2 data `data/ercot123_2019_v2/` | in force. Every v1-cost number is superseded history (`analysis/INVALID_v1_costs.md`), including the $0.29M var-cost ruler and the ±$79.5M bimodal total cost. |
| Prompt 36 waves A, B | landed (3 base + 19/19 screening). |
| Prompt 36 wave C (`selection_t1_v2`) | **landed on origin** (`7a511ed`: run dirs 3–11 extracted, FAILED marker removed). Not pulled and not read here. This corrects prompt 51 §2, which said rows 6–11 await Kay's rerun. |
| Prompt 36 wave D | not built; HOLD (PI gate, E-D0). Slate per `WAVE_D_TOPK_RULE.md`: sites 163 / 140 / 146 / 270 / 110 / 274. Smallest gen_pmax 185.4 MW. |
| Prompt 33 (TL = 360) | executed 10-11, then invalidated by E1 (header of `TL360_VERDICT.md`). Successor = the v2 solver-identity memo (G1). |
| Prompt 32 T2 | never ran; `make_selection_t2.py` not written. About 11–24k core-h; gated on PI D5/D6. |
| Prompt 37 analysis | suite landed on branch `stoprule` (~10-13); never analyzed. The "prompt 50" file does not exist. |
| v2 instrument facts (22 v2 runs: base ×3, screening ercot ×12, topup ×7) | see the list below. |

v2 instrument facts:
- 8,030 RUC solves, all OPTIMAL; max final gap 1.00 %.
- Load shed = 0 on every run.
- Nuclear units 1 and 93 have 0 starts on every run.
- Total cost = fixed + variable to within $1e-6.
- The base replicates are byte-identical.

## 1. Objective vector M_ERCOT (E-D1)

### 1.1 Members (DECISION E-D1; default recommended)

| objective | role | evidence |
|---|---|---|
| true curtailment (`true_curt`, minimize) | **objective** | location-sensitive (screening); deterministic on v2 |
| cost (minimize) | **objective**: `total_cost` if the §1.2 test passes, else `var_cost` (the D5 default) | see the cost evidence below |
| load shed | **guardrail**, not an objective | 0 on all 22 v2 runs; no variance to optimize |
| h2 volume | diagnostic only, unless the PI adopts it (D5) | quasi-deterministic in the design (ERCOT_SELECTION.md) |
| reserve shortfall | diagnostic (recorded each round) | base v2 = 445.9 MWh |

Cost evidence (16 single-site screening_v2 rows vs base):
- The fixed and variable deltas have opposite signs on 15 of 16 rows.
- Median |Δfixed| / |Δvar| is 0.42.
- Median |Δ| values: total $11.3M, fixed $13.3M, var $26.7M.
- On 4 rows, var_cost and total_cost move in opposite directions.

**Why the cost choice matters (evidence, not decision).** var_cost
alone overstates the cost effect of a PEM site by about 2.4× in the
median. It reverses the sign on 4 of 16 screened sites. Default:
`total_cost`, conditional on §1.2.

### 1.2 Total-cost readability test (FROZEN, blind)

The test uses only these artifacts, which existed at freeze:
- `extracts/base_2019_v2/run_index_{1,2,3}`
- `extracts/screening_v2/ercot/run_index_{1..12}`
- `extracts/screening_v2/topup/run_index_{1..7}`
- the reference numbers in `plan51_refs.json["readability"]`

The test is applied to the prompt-52 replicate runs, and to every
later graded run.

**SUSPECT check (prerequisite; per run).** A run is SUSPECT if any of
these fails:
- S1: |total − fixed − var| ≤ $1. (Observed max on 22 runs: $9.5e-7.)
- S2: every RUC of the run has status OPTIMAL (`ruc_quality.csv`).
  (Observed: 8,030 / 8,030.)
- S3: for designs with no nuclear retrofit, the starts of nuclear units
  1 and 93 are 0. For any design, the starts of units 1 and 93 must be
  equal across exact replicates.
  - This is the v1 bimodality mechanism: gen-1 cycling under TimeLimit
    races. Observed: 0 starts on all 22 runs.

**READABILITY rule.** total_cost is READABLE for the campaign if and
only if all of these hold:
- R1: no prompt-52 run is SUSPECT.
- R2: across the prompt-52 EXACT cross-batch replicates,
  max |Δ total_cost| ≤ 0.1 × $11.32M = **$1.13M**. ($11.32M is the
  single-site median |Δ total|.)
- R3: across the same replicates, max |Δ fixed_cost| ≤ 0.1 × $13.25M =
  **$1.33M**. ($13.25M is the single-site median |Δ fixed|.) Fixed cost
  was the v1 bimodal component.

**Outcome.**
- READABLE: the cost objective = total_cost.
- Not readable: cost = var_cost, with the D5 caveats.
- The verdict is recorded once, in the prompt-52 deliverable, and is
  final.
- Mid-campaign SUSPECT runs: a later run that is SUSPECT is excluded
  from HV and gain and flagged in the ledger. If 2 or more SUSPECT runs
  occur in one round, the campaign HALTS FOR DECISION. The cost
  objective is never switched mid-campaign.

FROZEN.

### 1.3 Guardrail acquisition treatment (DECISION E-D1)

Every guardrail gets a pinned acquisition treatment.

**Load shed.** Default: **monitored-only, with a pre-registered
violation response.** Shed is 0 on every v2 run, so a constraint model
would train on constant data:
- A GP constraint is degenerate.
- Feasibility weighting is identically 1.

Violation response:
- **Single violation:** a run with shed > 1 MWh is a VIOLATION. It stays
  in the ledger, marked infeasible-for-claims, and it is excluded from
  the reported fronts.
- **First violating round:** acquisition switches to **constrained
  qNEHVI**, with a shed GP constraint of shed ≤ 1 MWh, from the NEXT
  round on. This switch is pre-wired in the prompt-55 arm config; if it
  is missing, the build FAILS.
- **Escalation:** 2 or more violations in one round → HALT FOR DECISION.

Alternatives for the PI: constrained qNEHVI from round 1, or
feasibility-weighted acquisition.

**Reserve shortfall.** Diagnostic only, with no acquisition role. A
round flag is raised if any run exceeds 2 × the base value
(2 × 445.9 MWh). The flag is recorded and never halts.

Default above; options to the PI as E-D1.

## 2. Design space (FROZEN procedure; prompt 53 instantiates)

- **Dimensions:** the selected sites. d = site count (E-D3 slate: d = 6;
  d = 7 if the PI adopts the nuclear tier, D6).
- **Bounds per site:** x_s ∈ [0, gen_pmax_s] MW, so PEM_fraction =
  x_s / gen_pmax_s ≤ 1.
  - One shared box bound is wrong by construction: the smallest wave-D
    site is 185.4 MW and the largest is 746.4 MW.
  - The lower bound 0 means "site absent". The wave writer encodes
    x_s = 0 as an absent tier (never as ω = 0; the RTS make_row
    assertion).
- **GP input:** u_s = x_s / gen_pmax_s ∈ [0, 1]. This is a deterministic
  box normalization, applied BEFORE the GP's own data standardization.
  It is required because the MW ranges differ by about 4×.
- **No lattice:** the RTS ω-lattice code cannot be used (prompt 55 §2).
  Candidates are continuous.

FROZEN.

## 3. Noise plan (FROZEN; prompt 52 measures, after G1)

- **τ population:** EXACT cross-batch replicates only.
- **Pre-registered expectation on v2:** exact sd ≈ 0. Basis:
  byte-identical base replicates, and 0 % of RUCs at the time limit.
- **If the exact sd is 0 for an objective,** its τ contribution is 0.
  If all are 0, the stop rule is **budget-cap-only**. This is a finding
  about a deterministic instrument, not a failure.
- **Perturbed copies measure local input sensitivity.** They feed the
  rider (§7) and are never pooled with the exact replicates.
- **GP noise floor:** exact sd if > 0, else inferred-only with the 1e-9
  bound (the D-1025 pattern).

FROZEN.

## 4. Holdout random_E (FROZEN rules; prompt 53 generates)

- **Generation:** i.i.d. uniform over the frozen per-site box,
  n_E = 48.
- **cov95 bar:** [lo, hi] = `scipy.stats.binom.interval(1 − α, n_E,
  0.95)`, with **α = 0.10**. This is the central 1 − α acceptance region
  of Binomial(n_E, 0.95).
  - It reproduces [43, 48] at n_E = 48. Every α in (0.063, 0.181]
    does.
  - Other sizes: n = 32 → [28, 32]; n = 56 → [50, 56]; n = 64 →
    [58, 63].
  - **Trap for prompt 54:** `common.binom_band()` defaults to level
    0.95, which gives [42, 48]. Pass `level = 0.90`.
- **Independence disclosure (one line, required):** the 48 residuals
  share one fitted model, so the binomial region treats them as
  independent. This is an approximation.
- **Exposure budget:** at most 24 model–holdout scorings in total. One
  scoring = one committed config × one objective × one n0 tier.
- **Retirement:** after 24 scorings, or after the prompt-54
  committed-config grading, whichever comes first. After retirement,
  only deterministic replays of recorded scorings are allowed.

**E-D2 (DECISION): dual role.** random_E may also serve as the random
baseline pool (§7).
- **Statistical view:** the baseline percentile (prompt-34 formula) fits
  no model. It is model-free, so it does not leak model selection.
- **Budget view:** dual saves 48 runs, about 0.6–1.2k core-h at the v2
  per-run range (2.9–4.2k at v1 rates).
- **Pinned if dual:** baseline gradings do **NOT** count against the
  exposure budget. A model change informed by a baseline result is
  banned.
- **Recommendation:** dual.

## 5. GP arm set (FROZEN; prompt 54 fits and adds nothing)

**Default arm:** the D-1025 transfer config.
- m52 kernel, std transform.
- Noise inferred, with a lower bound of 1e-9.
- Campaign fit definition.
- u-normalized inputs (§2).
- The config is generic, not tuned on RTS. It applies to every
  objective.

Alternatives, each with a numeric inclusion rule:

| arm | include for objective j if and only if |
|---|---|
| rbf + std | always (RTS prompt 39: rbf+log1p fixed the r3 overconfidence; the kernel half enters unconditionally) |
| m52 + log1p | min y_j ≥ 0 and max y_j / max(min y_j, 1) > R* = 10 on the grading tier |
| rbf + log1p | the same condition as m52 + log1p |
| m52 + std, floor = measured | the prompt-52 exact sd_j > 0 with df ≥ 3 |

**Selection rule** (per objective, on the grading tier):
- The criterion is closed-form LOO NLPD (house `loo_t`).
- An alternative replaces the default only if its mean per-point NLPD
  is lower by more than 2 paired standard errors of the per-point
  difference.
- **Tie rule:** otherwise the default stays. Among tied alternatives,
  the order is std before log1p, then m52 before rbf.
- **Lesson behind this:** RTS Phase-B showed that LOO cannot separate
  noise treatments (a 0.017-nat gap with paired se 0.26), and that the
  LOO winner graded worst on the holdout. Ties therefore default to the
  transfer config, and the holdout is never consulted for selection.

**Holdout:** each committed config is graded ONCE against the §4 bar.

FROZEN.

## 6. Stop rule, ref point, calibration gates, cap

### 6.1 Rule form

- **The rule form** is per the prompt-37 analysis verdict.
- **Fallback (pinned):** if that analysis has not run when prompt 55
  freezes its stop-rule section, the form is the RTS two-strike rule:
  - The rule: would_stop_k = (gain_k < τ) AND (gain_{k−1} < τ).
  - It is stateless.
  - It is record-only: the machinery never halts. All rounds run to the
    cap, and only the first fire is "the stop".
  - The fallback is disclosed.
- **Rulers:** τ_joint (headline) and τ_marginal (recorded).
- **Wording:** the prompt-49 v2.1 banned-framings block applies
  verbatim.

### 6.2 τ recipe

τ = std (ddof = 0) of the exact HV over N = 1,000 MC draws, with
`default_rng(20261006)`.
- All nav-tier starts are perturbed in each draw.
- Noise vectors are drawn **jointly** from N(0, Σ), with Σ = the
  prompt-52 covariance matrix of the replicate deltas.
- If prompt 52's scalar-rejection trigger fires for an objective, that
  objective's sd is σ_j(y) per start: the prompt-52 per-level anchors,
  piecewise-linear, as in RTS form (ii).
- **Code path:** the `part_c45.py` vector path (phaseb clone,
  `noise_floor/stop_regrade45/`).
- **Fallback:** marginal sampling plus a joint-vs-marginal sensitivity
  row.
- τ is computed once at arm init, persisted, and equality-asserted
  every round.

### 6.3 HV ref-point rule

- All objectives are minimized.
- R = nadir + 0.1 × (nadir − ideal), per objective, over the GRADING
  tier.
- Prompt 53's landing report instantiates R. Prompt 55 asserts it at
  init.
- A report-only R_union (the same formula over all evaluated designs at
  the end) is added at analysis time.

### 6.4 Per-round calibration gates (numbers FROZEN)

| gate | test (q = 8 new points; pre-round GP; 95 % total band) | semantics | false-alarm P at calibration |
|---|---|---|---|
| C1 ingest | all q runs present, objectives finite, SUSPECT check (§1.2), shed check (§1.3) | **fail-stop** | — |
| C2 coverage | covered ≤ 4 of 8 for any objective | **record + REVIEW flag**; never halts | 3.7e-4 per objective |
| C3 outlier | ≥ 3 of 8 points with \|z\| > 3 for any objective | **record + REVIEW flag**; never halts | 1.1e-6 |

Kay decides the action on a REVIEW flag. The default is to continue
(record-only).

Reading note (RTS prompt 49): with the noise inferred small, |z|
inflates by construction. Judge against the committed-config cov95,
not against RTS history.

### 6.5 Cap

- The cap is a column of the §8 table. Prompt 55 asserts it at init.
- It is set by the prompt-37 verdict where that exists; otherwise the
  pinned option value.

FROZEN, with the division of labor: plan 51 freezes forms, gate
numbers and the ref rule; prompt 55 instantiates τ and R.

## 7. Baseline and robustness rider

- **Baseline:** random i.i.d. designs, with the same budget and a twin
  launch with prompt 56 — or random_E if E-D2 = dual. Grading uses the
  prompt-34 frozen percentile formula at the §6.3 refs.
- **Rider bar: 80 %, pinned.** At least 80 % of 1,000 perturbed draws
  must keep the deterministic point row.
- **Rider noise levels:** the prompt-52 MEASURED levels, from the first
  grading.
  - If an objective's exact sd is 0, its rider level is the prompt-52
    perturbed-population sd. That rider is labeled
    **"sensitivity-level rider"**, never "noise-level".
  - A 0-noise rider would pass by construction.
- **Wording:** the verdict is always quoted with its conditionality. "BO
  beats random" is banned.

FROZEN.

## 8. Budget arithmetic (printed, not implied)

**Per-run core-h on v2 is UNKNOWN.** No wall-clock exists locally:
extracts are slim, and qacct is unavailable.
- Kay extracts real wall-clock from the CRC wave `.o` files and the
  Prescient `runtimes.csv`.
- Until then, the table carries two columns: **v1 60–88 core-h/run**,
  and **v2 plausibly 12–25**.
- **Lower bound:** the measured v2 RUC solve time alone is 2.0 h/run
  (365 × 19.8 s median), which is 8 core-h at 4 slots.
- **Fixed rows:**
  - replicates (prompt 52): 12
  - n0 grading tier (nav ⊂ grading): 48 = max(8d, 48) at d = 6
  - random_E holdout: 48 (0 extra if dual)
  - baseline pool: 48
- **BO runs** = arms × seeds × cap × q, with q = 8.

| option | arms | seeds | cap | BO runs | total runs (dual / not) | core-h v2 12–25 (dual) | core-h v1 60–88 (dual) |
|---|---|---|---|---|---|---|---|
| A minimal | 1 (qNEHVI) | 1 | 4 | 32 | 140 / 188 | 1.7k–3.5k | 8.4k–12.3k |
| B pair | 2 (qNEHVI + q-ParEGO) | 2 (fixed starts, V1/N1 pattern) | 4 | 128 | 236 / 284 | 2.8k–5.9k | 14.2k–20.8k |
| C PI seeds | 1 (qNEHVI) | 5 | 4 | 160 | 268 / 316 | 3.2k–6.7k | 16.1k–23.6k |
| D full | 2 | 5 | 6 | 480 | 588 / 636 | 7.1k–14.7k | 35.3k–51.7k |

Notes on the table:
- PI directive 1014-D1 (5–10 seeds) is met only by C and D.
- 10 seeds double the BO rows of C and D.
- **Every option competes with prompt 32 T2 (about 11–24k core-h) for
  the same allocation.**
- **Wall-clock per round:**
  - Runs: v2 3–6 h at 4 slots (v1 15–22 h).
  - Acquisition: about 0.5 h.
  - Manual submission: Kay submits each round from the login node,
    because compute nodes cannot qsub.
  - The RTS experience is about 1 round per calendar day.
  - So a cap-4 arm takes about 4–5 days; seeds and arms run in
    parallel.

Recommendation: **C** if T2 is not bought, **B** if it is. This is the
DECISION E-D4 (PI budget).

## 9. Gate DAG

```
G0  E-D0: Kay recovers the UNRECORDED PI wave-D gate condition (1014-D3)  — blocks ALL E-sims
51 (this plan) ∥ prompt-37 analysis (both zero-sim; 51 blind to v2 confirms)
G1  v2 solver-identity memo (prompt-33 successor) + 36 wave C landed (MET on origin 7a511ed) → 52
G2  (32 T2 bought) OR E-D3 fallback: freeze on the wave-D slate 163/140/146/270/110/274
    (+ 51 approved: E-D1, E-D2, E-D4 answered) → 53 → 54 → 55 (needs 49's PATCH TEXT, not
    49's campaign) → G3 expectation statement → 56
```

## 10. Amendment protocol (FROZEN)

- **Append-only.** Changes go in dated `AMENDMENT YYYY-MM-DD` blocks at
  the end of this file. Each block states what changed, why, and
  whether any affected number had been seen.
- **IMMUTABLE after freeze:** the bars (§4, §6.4, §7), the selection
  rule (§5), the stop-rule form and fallback (§6.1), the readability
  test (§1.2) and the ref rule (§6.3).
- **Appendable:** budgets and actuals (prompt 52 runtimes, prompt 53
  landing numbers, prompt 55 τ and R values), plus decisions as they
  are made.

### PI decision list and drafted pi-agenda rows

| id | question | default / recommendation |
|---|---|---|
| E-D0 | What was the wave-D gate condition (1014-D3)? | Kay re-asks the PI; blocks every E-sim |
| E-D1 | M_ERCOT and guardrail treatment | curt + total_cost (if readable, else var_cost); shed = monitored-only guardrail with a pre-wired constrained-qNEHVI switch |
| E-D2 | random_E dual holdout/baseline role | dual; baseline gradings outside the exposure budget |
| E-D3 | Site slate if T2 is not bought | wave-D slate 163/140/146/270/110/274 (d = 6; +nuclear if D6) |
| E-D4 | Budget option (§8) | C if no T2; B if T2 |

Drafted rows for pi-agenda §4 (strategy session pastes them):
- `| 2026-10-28 | E-D0 | ERCOT wave-D gate | condition unrecorded — Kay re-asks; blocks all ERCOT simulation | ERCOT_BO_PLAN §9 |`
- `| 2026-10-28 | E-D1 | ERCOT objectives | curt + total_cost if the frozen readability test passes (var_cost otherwise); shed = guardrail, monitored-only + pre-wired constrained switch | ERCOT_BO_PLAN §1 |`
- `| 2026-10-28 | E-D2 | random_E role | dual holdout + baseline (saves 48 runs); baseline gradings outside exposure | ERCOT_BO_PLAN §4 |`
- `| 2026-10-28 | E-D3 | ERCOT site slate | wave-D top-6 if 32-T2 not bought | ERCOT_BO_PLAN §9 |`
- `| 2026-10-28 | E-D4 | ERCOT budget | option C (1 arm × 5 seeds × cap 4) if no T2; B if T2 | ERCOT_BO_PLAN §8 |`

## 11. Deviations (disclosed)

1. **Wave C status corrected:** it has landed on origin (`7a511ed`),
   which is not what prompt 51 §2 says. Not pulled and not read before
   the freeze.
2. **Added decision E-D4 (budget option).** Prompt 51 lists E-D0..E-D3,
   but §3.8 requires an option choice.
3. **Added C3 and the reserve-shortfall diagnostic**, beyond the
   prompt's minimum.
4. **Sensitivity-level rider rule (§7)** added for the sd = 0 case. The
   prompt does not cover it.

## AMENDMENT 2026-11-06 (prompt 57 Part A; objective pool; E-D1b)

**What changed.**
- §1.1 pool widened from five columns to the prompt-57 §2 table: V1–V3,
  E1–E9, R1–R8, N1–N5, X1, D1–D3 (28 candidates + the D3 check).
  Formulas, directions, family-internal priorities, the global order
  (priority → V < E < X < R < N → id), EF values (COAL 1.00, CT 0.55
  t/MWh, ± 20 %), the 450 $/MWh LMP threshold and the §4 ρ rules are
  FROZEN in `analysis/pool/pool_definitions.json` at commit `f76d897`.
  Candidates may not be added after Part-B data is read.
- **E-D1 stays OPEN.** The default of §1.1 (curt + total_cost if §1.2
  passes, else var_cost) is unchanged as the default.
- **§1.2 is unchanged.** It is immutable (§10) and governs E1 only. The
  SUSPECT checks S1–S3 are now computed per run in `pool_wide_v2.csv`
  (0 SUSPECT on the 31 v2 runs).
- **New decision E-D1b (PI):** which Part-B survivors (prompt 57 §4, after
  wave D) become objectives (≤ 4, at most one per family by the global
  order), guardrails, or diagnostics. Part B writes the decision table.
- Two noise-free scales join the evidence columns, never the verdict
  labels of §1.2: the MIP-gap cost bound G_run = Σ_days gap × ruc_cost
  (E1–E3 only; pair bound G_a + G_b; `GAP-READABLE` / `WITHIN GAP
  BOUND`) and the scale-free location ratio S (prompt 57 §3 A4b).
- The perturbation ruler of prompt 52 (median |Δ| over the 0.1 %
  perturbed copies) replaces the vacuous exact-replicate ruler
  (ruler = 0 on a deterministic instrument). Readability wording is
  pinned in prompt 57 §3 A4; every Part-B read carries `RULER PENDING
  (52)` until 52 lands.

**Why.** ERCOT v2 shed ≡ 0, so the RTS argument that dropped reserve
and cycling as redundant with shed does not transfer. Kay wants the
selection step to see the widest honest pool.

**What had been seen when this was written.** The 31 v2 runs' legacy 9
columns; base values of N1/N3/N4/N5/E7; the uplift zeros; the n = 16
first cut of relief/var_cost/h2/starts (`pool_correlations.csv`); the
v2 fuel prices; and, after the freeze commit, the Part-A outputs
computed on the same 31 runs (`analysis/pool/POOL_V2.md`: dead list E5,
R1, R3; first-cut clusters {E1, V2, X1} raw / {V2, X1} partialled; G
table). **No wave-D number and no prompt-52 number existed.** No
priority was changed after any number was seen.

**Finding disclosed, not acted on.** G_base = $196.7M, 17.4 × the
$11.3M median single-site |Δ total_cost| of §1.1; 0 of 16 single-site
E1 deltas exceed the pair bound. The §1.1 cost evidence must be re-read
against this bound in Part B. §1.2 is not touched.

**Storage addendum (prompt 36 §4.2, dated 11-06).** Wave D runs
`--full` on every row: 51 MB × 21 rows ≈ 1.07 GB (18 rows ≈ 0.92 GB).

Drafted pi-agenda row:
- `| 2026-11-06 | E-D1b | ERCOT pool survivors → objectives / guardrails / diagnostics | decided after wave D (prompt 57 Part B); pool frozen f76d897; ≤ 4 objectives, one per family | analysis/pool/POOL_V2.md |`

## AMENDMENT 2026-11-06b — solver identity v3 for the campaign (E-D6, decided by Kay)

**What changed.** The campaign identity for every run from wave D onward
is **identity v3: `ruc_mipgap = 0.001`, `ruc_time_limit = 1200 s`**,
recorded in `waves/GAP_DECISION.json`. All other options stay as frozen
(§2 of this plan; CONFIG_ERCOT.md table). The §1.2 readability test is
unchanged in form; its prompt-52 replicate runs are v3 runs. §3 (noise
plan) is unchanged. The 31 v2-identity runs (base, screening, selection
T1) remain slate evidence (site ranking by curtailment) and are NOT
re-run; no v2 cost value enters a v3 claim.

**Why.** Prompt 57 Part A found that under the 1 % gap the solver-hidden
cost bound (≈ $46M per run scaled to realized cost) exceeds the median
single-site PEM cost effect ($11.3M) by about 4×, so cost had no
readability evidence. The gap smoke (`extracts/smoke_gap`,
`analysis/gap_smoke/GAP_SMOKE.md`): control arm byte-identical to
smoke_v2 (plumbing clean); at 0.001 the 3-day cost falls by $89k
(linear ×365/3 ≈ $10.9M/yr ≈ 0.96 × the $11.3M median) with the
per-day RUC solve at 26 s median / 46 s max; at 0.0001 the fall is
$104k with 120 s median / 222 s max.

**Deviation from the pre-registered rule, disclosed.** Prompt 58 §2
said "adopt the tightest passing arm"; all three arms passed, which
pointed to 0.0001. Kay chose 0.001 on three grounds: (1) the smoke
covers three January days; at 0.0001 the first day already took 222 s
and summer days could reach the 1200 s limit, which would reinstate the
v1 time-limit nondeterminism — 0.001 keeps a 25× margin; (2) 0.001
recovers 86 % of the hidden cost at +18 % wall time, and G at 0.001
(≈ $12M/yr on the RUC objective, ≈ $3M realized) is already ~4× below
the median effect; (3) calendar cost: 0.0001 roughly triples core-hours
and doubles the critical path (~289 runs, 8 serial batches). The
alternative was available and is recorded.

**What had been seen.** The three smoke arms and the Part-A tables.
No wave-D number existed.

**Budget actuals (appendable row).** Smoke wall-clock at 4 slots, 3
days: 187 s (0.01), 221 s (0.001), 513 s (0.0001). Projected full-year
run at v3: ≈ 8–10 h wall / 32–40 core-h (from January days; replace
with wave-D actuals when they land).

## AMENDMENT 2026-11-14 — budget actuals from wave D (prompt 53 §2.6; appendable, §10)

**What changed.** §8's "Per-run core-h on v2 is UNKNOWN" and the
January-day projection of AMENDMENT 2026-11-06b (8–10 h wall / 32–40
core-h per full-year v3 run) are replaced by the wave-D actuals
(`analysis/pool/ERCOT_POOL_STANDINGS.md` §8, `extracts/location_oat_v2/wallclock.csv`;
4 slots per task, core-h = wall × 4). No rule, bar or option changes.

| node group | wave-D rows | wall h / run | core-h / run |
|---|---|---|---|
| fast | 15 | 5.12 – 5.48 | 20.5 – 21.9 (mean 21.1) |
| slow | 6 | 10.5 – 11.8 | 42.1 – 47.3 (mean 44.6) |

Wave D: 21 runs, 584 core-h, 11.8 h calendar. The split is node speed
(the RUC median solve time doubles with the wall time), not problem size.
Per-run core-h range for planning: **21 (fast) – 44.6 (slow)**, which
replaces "v2 plausibly 12–25" and the 32–40 projection.

**Applied to the fixed rows (prompt 53):** n0_E 48 + random_E 48 = 96
runs ≈ 2.0k (all fast) – 4.3k (all slow) core-h; 4,896 MB of `--full`
extracts in $GROUP storage. Per plan §8 option (dual random_E, totals ×
21 – 44.6): A 140 runs ≈ 2.9k – 6.2k; B 236 ≈ 5.0k – 10.5k; C 268 ≈
5.6k – 12.0k; D 588 ≈ 12.3k – 26.2k core-h.

**What had been seen.** Wave-D wall-clock and the prompt-57 standings.
No n0_E or random_E result exists at this amendment. Prompt 53's landing
report appends the n0_E / random_E actuals as a further block.

## AMENDMENT 2026-11-16 — n0_E / random_E landing actuals (prompt 53 §2.8; appendable, §10)

**What changed.** Budget actuals and the §6.3 ref point are instantiated;
no rule, bar or option changes. Source: `waves/n0_E/LANDING.md`,
`landing_rows.csv`, `landing_R.json` (`tools/land_ercot_n0.py`).

| wave | runs | SUSPECT | R1 shed | core-h (fast / slow runs) | calendar |
|---|---|---|---|---|---|
| n0_E | 48 / 48 | 0 | 0 on all | 1,566 (16 fast @ 19.1 / 32 slow @ 39.4) | 10.5 h |
| random_E | 48 / 48 | 0 | 0 on all | 1,440 (22 fast @ 18.9 / 26 slow @ 39.4) | 12.3 h |

- **Total 3,006 core-h for 96 runs (31.3 per run)**, inside the 2.0–4.3k
  bracket of AMENDMENT 2026-11-14. Per-run actuals by node: fast ≈ 19,
  slow ≈ 39.4 core-h (6-site rows; wave D 21.1 / 44.6). 58 of 96 runs
  landed on slow nodes. For the §8 BO rows plan with **≈ 31 core-h/run**
  (this mix), range 19–40: option C (160 BO runs) ≈ 3.0k–6.4k, mid ≈ 5.0k.
- 35,040 RUCs, all OPTIMAL, 0 at the time limit, max final gap 0.1 %.
  **Margin disclosed:** the longest RUC solve (incl. model build) is
  1,157 s (random_E:22, slow node) against the 1,200 s limit: ≈ 4 %
  headroom, not the ≈ 25× of the January smoke cited in AMENDMENT
  2026-11-06b. A later limit hit is caught per run by S2 (SUSPECT).
- **§6.3 R instantiated** over the 48 grading rows for all 29 pool
  candidates (`waves/n0_E/landing_R.json`; dir `max` minimized as −x, dir
  `-` computed as minimized and flagged). Seats (E-D1b provisional): V1
  3.9775e6 MWh, E1 8.1637e9 $ (E3 4.5723e9 $ if the §1.2 verdict is not
  READABLE), R4 15,279.1, N1 36,068.5. Prompt 55 asserts at init.
- R2 reserve shortfall max 199.9 MWh (flag 891.8): no flag.

**What had been seen.** The 96 landed runs' objective values (to compute
R, the ledger and this table). No GP has been fit on them and no holdout
scoring has been made: the exposure budget (§4) is untouched.

## AMENDMENT 2026-11-17 — E-D1b input widened to n0_E (pool level); new n0_E rules; Part C disclosure

**What changed.** Source: prompt 62 v1.1 §1.4 (pre-registration; this
block is committed ALONE, before `analysis/pool/pool_n0E.py` and before
any n0_E statistic is computed).

- E-D1b input = wave D (57 rules f76d897 unchanged for wave D) + n0_E
  (pool level). Candidates, directions, family priorities,
  `global_order` and the survivor rule are unchanged (f76d897).
- NEW rules for the n0_E population, stated below verbatim from prompt
  62 v1.1 §3.2–§3.4 (bar = 61 §3 B_j with D2 excluded; RESPONDS IN BOX;
  SIZE SHARE; residual-guarded REDUNDANT; TRADE-OFF; adjudication
  R-1…R-5; seat walk incl. M < 4; the E-seat clause).
- Plan §1.2 is final (READABLE → E1). No Part B or Part C read moves the
  E seat; if E1 fails RESPONDS IN BOX the E seat is HALT FOR PI, never
  passed to E3/E4. The gap read is an evidence column only.
- Objectives selected on the grading tier are then graded by 54 on the
  same tier (LOO / sufficiency); random_E stays unread; 54 adds one
  Deviations line in `ERCOT_GP_STATUS.md`.
- R2 flag re-instantiated: 2 × base_v3 reserve shortfall (2 × 156 = 312
  MWh; `design_space_E.json`'s 891.8 was 2 × the v2 base) — the strategy
  session's dated `design_space_E.json` carries it.
- Part C (16-site screening under identity v3, `waves/screening_v3`) is
  disclosure; E-D3 (the slate) is not reopened in this campaign.
- The five conditions that make post-n0 objective choice defensible
  (independent filtering, Bourgon–Gentleman–Huber 2010): rules use only
  properties of the objectives (spread, structure, concordance), never
  performance quantities (front, HV, optimum, GP fit); every statistic,
  threshold, tie band and substitution rule is committed before the
  read; random_E unread; no GP; seen-data disclosed.

**What had been seen (pre-registered, NOT blind).** Per-candidate ideal
/ nadir / R over the 48 n0_E rows for all 29 ids (`landing_R.json`,
`LANDING.md` §3, AMENDMENT 2026-11-16), read by the strategy session and
Kay; the 54 session's rerun read wave D + base_v3 only; 54's mechanism
code read n0_E X only; B_j was fixed 11-17 after `LANDING.md` existed;
no n0_E correlation, cluster, size-share or composition statistic has
been computed; no GP fitted; holdout exposure 0 of 24.

**Rules for the n0_E population (verbatim, prompt 62 v1.1 §3.2–§3.4;
numbering kept).**

2. **Bar:** `B_j` per 61 §3 from `per_candidate.<j>.perturbed_delta_signed`
   with the D2 structural-zero pairs excluded (6 values; assert input
   md5 equality for the excluded pair): `B_j = max(3·sqrt(mean δ²),
   max|δ|)`. Zero-bar set = {j : B_j == 0} (expected {E5, E9, R1, R3};
   assert): readable iff range ≥ 1 natural unit (57 A4 RULER=0 rule),
   DEAD if constant over 48. N2 (in `ruler_zero` but B_j = 2.60) is
   graded on B_j. D3 has no bar: check only. Assert `exact_pooled_sd ==
   0` for all ids. Print B_j, 57's median ruler and their ratio
   (3.5–11.5×) side by side; the two are never merged.
3. **Pre-registered statistics (per graded j):**
   - **RESPONDS IN BOX** iff ALL of: `IDR_j = Q90 − Q10 over 48 ≥ 2·B_j`;
     STRUCTURED by a Mantel permutation test (Spearman between
     |y_i − y_k| and ‖u_i − u_k‖ over the 1,128 pairs; 9,999
     permutations; `default_rng(6262)`; one-sided p ≤ 0.01); signal
     share `1 − (σ̂_j²/2)/Var(y_j) ≥ 0.5`. `IDR/B_j ∈ [2, 3)` =
     BORDERLINE (no seat may rest on it alone). STRONG iff `IDR ≥ 10·B_j`
     (descriptive). Also print range/B_j. Disclose: B_j is transferred
     from single-site off-slate designs; box chatter cannot be measured
     on n0_E (no replicates); false-RESPONDS under pure chatter ≈ 0.1 %
     per id for IDR at 1× chatter (3.5 % for the raw range).
   - **SIZE SHARE:** f̂_j = PCHIP through the medians of 6 equal-count
     bins of T; `η²_T = 1 − Var(y − f̂)/Var(y)`; adjusted `(η² −
     0.107)/(1 − 0.107)`; print the null 95th percentile 0.23. Secondary:
     isotonic regression (`scipy.optimize.isotonic_regression`, direction
     = sign of ρ(y, T)) with leave-one-out R². Descriptive only.
   - **COMPOSITION:** partial Spearman `ρ(y − f̂_y(T), s − f̂_s(T))` (both
     residualised with the same bins), Fisher-z 95 % interval.
     Descriptive only; 61 tests location directly, and this and 54's L
     flag come from the same 48 rows (never two independent pieces of
     evidence).
   - **REDUNDANT** (pairs of directed ids) iff raw `ρ_or ≥ 0.90` on the
     48 rows AND residual `ρ_or ≥ 0.50` on the T-residuals (outside the
     n = 48 null band ±0.29) AND complete linkage. A pair with raw ≥ 0.90
     but residual < 0.50 is `SIZE-CO-MONOTONE`: disclosed, not clustered
     (the n0_E analogue of 57's per-level guard). A raw ρ whose Fisher-z
     90 % interval contains 0.90 (≈ 0.86–0.93) is BORDERLINE → rule R-3.
     Orientation `ps.oriented_frame(wide, ids, defs)` (base_row=None),
     matrix `ps.spearman_matrix`, clusters `ps.clusters_from_pairs`;
     survivor = the FIRST member in `pool_definitions.json` `global_order`
     (priority first, then V<E<X<R<N, then id — e.g. E1 survives {E1,
     V2, X1}, not V2) that is directed and RESPONDS IN BOX. dir "—" ids
     shown, never clustered; dead ids = 57 A2 list. Clustermap via
     `ps.plot_cluster_panel` to `analysis/pool/figs/n0E/`.
   - **TRADE-OFF (size)** iff raw `ρ_or ≤ −0.50`; **TRADE-OFF
     (composition)** iff residual `ρ_or ≤ −0.50`; Fisher-z intervals
     printed. Multiplicity: expected false redundancy < 0.01 and false
     trade-off ≈ 0.07 over 231 pairs — printed, no correction.
   - Sampling facts to print in the md: at n = 48, P(ρ̂ ≥ 0.90 | ρ = 0.80)
     = 0.8 %, P(ρ̂ ≥ 0.90 | ρ = 0.90) = 44 %; Sobol points are not
     i.i.d. (bands mildly conservative); chatter attenuates ρ
     (permissive for R4/N1).
4. **Adjudication with wave D (pinned):**
   - R-1 (response): a seat needs RESPONDS IN BOX on n0_E. Wave-D
     readable (2·B_j at ≥ 2 of 3 levels) but n0_E not → DIAGNOSTIC,
     "readable as single sites ≤ 180 MW, chatter-level across the box".
     n0_E responds but wave D not → eligible, tagged BOX-ONLY RESPONSE.
   - R-2 (redundancy): clusters on n0_E; wave-D-redundant-only pairs
     disclosed, not clustered.
   - R-3 (borderline): a BORDERLINE n0_E pair takes wave D's frozen-rule
     verdict (57 pooled + per-level). X1–E1: X1 stays REDUNDANT→E1 unless
     raw < ≈ 0.86 or residual < 0.50.
   - R-4 (seats): walk `global_order`, fill ≤ 4 seats, ≤ 1 per family;
     skip guardrails (R1, R2; plan §1.3), dir "—", REDUNDANT, not
     RESPONDS, or BORDERLINE-only. E seat = E1 (§1.2); E1 failing →
     HALT FOR PI. A family with no eligible member leaves its seat
     empty: M < 4 is reported and the next family does not fill it until
     the PI decides; M ≠ 4 reopens plan §6.4 gate numbers for the PI.
   - R-5 (conflict): any id whose wave-D B_j verdict and n0_E verdict
     disagree gets a row printing both; never a merged label.
   - N family: report N1 and N4 both (N1 = N4 + N1_off; on wave D N4 is
     −72…−183 and N1_off is +58…+230 on 18/18 rows). If N1–N4 are
     REDUNDANT the table shows both range/B_j and flags that the 57
     priority keeps the noisier member (bar 99.5 vs 32); a PI override
     is a recorded rule change.

## AMENDMENT 2026-11-17c — location_contrast_E actuals (prompt 61; appendable, §10; analysis-only; what had been seen)

**What changed.** Nothing in the plan's rules, bars, X, HV ledger,
holdout or baseline. The 9 `location_contrast_E` rows (`tier =
"contrast"`) are analysis-only and never enter `load()`, the GP, §6.3 R
or the random baseline (55 `base_waves = ["n0_E"]` is unchanged). Source:
`analysis/location_contrast/LOCATION_CONTRAST_E.md` and
`location_contrast_E.csv` (landing commit 4b7bf85; wave commit 3b40c2d
froze the reads, prompt 61 §3, before any Y).

- **Budget actuals:** 9 / 9 runs, SUSPECT 0, R1 shed 0 on all. Wall-clock
  4.8–5.4 h per run at 4 slots, about 19–21.4 core-h per run and about
  182 core-h in total. This is inside the 170–355 core-h bracket.
- **Bars used:** B_j from the 63-re-emitted `analysis/noise_v3/ercot_noise.json`
  (D2 excluded, 6 δ): V1 16,173 MWh, E1 $2.383M, R4 146.7, N1 114.9,
  N4 37.0. `exact_pooled_sd` = 0 for all ids.
- **Interaction (V1):** g = 0.038 / 0.073 / 0.123 at 60 / 120 / 180
  MW per site (predicted 0.07 / 0.12 / 0.18). The guard passes at all
  three levels. The reads are WITHIN 10 % / WITHIN 10 % / SUB-ADDITIVE.
- **Location at fixed total:** the V1 H_C residual is +3.0 / +6.7 /
  +6.4 / +2.9 B_V1 (pairs 4–5, 7–8, 4–6, 5–6), so the §3 rule reads
  LOCATION EFFECT on all four. "Location" here means "not explained by
  H_C". The matched-u residual (6.7 rulers) is within the ≈ 9-ruler
  profile-only difference the pool model predicted in advance, so no
  network effect is claimed. N4 reads COMPOSITION for 4–5 and LOCATION
  EFFECT for the other three pairs. N1 is chatter-limited. E1 / E3 are
  NOT READABLE or WITHIN GAP BOUND (pair bounds $41.9–43.7M).
- **Saturation (row 9, 1,500 MW):** relief is 4.03 TWh, which is 83 % of
  the 4.87 TWh behind-cut pool. e = 0.730 is the lowest of the nine rows.
- **Physics prediction:** "no residual location effect" is CONTRADICTED
  under the H_C covariate. "E1 within gap bound at 800" HOLDS. "R4
  unreadable" is CONTRADICTED on the 2 pairs against row 6. Per §3 a
  contradiction is a finding.

**What had been seen.** When this block was written: the 9 contrast
runs, wave-D rows 1–18, base_v3:1 and `ercot_noise.json`. Before the
landing: everything listed in prompt 61 §3 "Seen at freeze". Not read:
`extracts/n0_E`, `extracts/random_E`, `extracts/methods_E_*`. No GP was
fit. Holdout exposure is unchanged. E-D1b, E-D4, E-D5 and E-D7 are
unaffected. This wave's Y landed before E-D1b was recorded. The E-D1b
inputs (62 Part B: wave D + n0_E) did not include it.

## AMENDMENT 2026-11-18 — noise_seed_E actuals + chatter rulers (prompt 63; appendable, §10; what had been seen)

**What changed.** Nothing in the plan's rules, X, HV ledger, holdout
or baseline. τ_exact = 0 stays the frozen stop-rule ruler (§3, §6.2).
The 18 `noise_seed_E` rows (`tier = "contrast"`) are analysis-only and
never enter `load()`, the GP, §6.3 R or the random baseline. Source:
`analysis/noise_v3/NOISE_SEED_E.md` and `ercot_noise_seed.json` (landing
commit 14378fd; wave commit 6fd3352 froze the reads, prompt 63 §3).

- **Budget actuals:** 18 / 18 runs, SUSPECT 0, time-limit hits 0, every
  run v3. About 589.5 core-h in total (Threads-4 median 38.2 core-h,
  range 19.1–42.4; Threads 8 36.6; Threads 1 6.3). This is inside the
  380–800 core-h bracket. Gurobi 13.0.2 is logged on every run.
- **Chatter sd (per run, df 16) and bars:** σ̂_c / B_j^seed vs B_j
  (perturbed, D2 excluded): V1 4,376 MWh / 18,567 vs 16,173; E1 $312.4k
  / $1.326M vs $2.383M; R4 65.1 / 276.1 vs 146.7; N1 57.1 / 242.1 vs
  114.9; N4 10.5 / 44.5 vs 37.0.
- **A3 verdict (recorded once):** σ̂_c·√2 / σ̂_pert is within 2× on 20
  of 22 gradable ids (V1 1.15, E1 0.56, R4 1.88, N4 1.20). It fails on
  N1 (2.11) and on E9 (the perturbed ruler is 0). For N1 and E9 the
  perturbed ruler is "perturbation response, not chatter" and the bar
  is B_j^seed. For the other ids both bars measure the same chatter;
  both are reported. 61 has already read; its N1 reads are reported
  against both bars.
- **Thread check:** Threads 8 and Threads 1 are NOT bit-identical to
  the Threads-4 run (304 / 364 of 365 RUC days differ). The thread rows
  ran on another node class than the anchor, so the two causes are
  confounded. Bit-identity holds only at fixed Threads on a fixed
  platform. Threads = 4 stays pinned.
- **τ_res (REPORT-ONLY):** E-D7 is not recorded, so τ_res is computed
  on the 4 anchor designs only and labelled PROVISIONAL: 1.958e18
  (0.128 × HV_0 of those 4 points). τ_exact = 0 is unchanged. 55
  Part B carries the τ_res column at the real nav starts with Σ_c from
  `ercot_noise_seed_sigma_c.csv`.
- **54 input:** σ̂_c,j with df 16 makes the measured-floor arm input
  live (54 records it as a §10-amended arm input, not a new arm). The
  54 cross-check compares the inferred noise sd against σ̂_c,j, not
  against 0.

**What had been seen.** When this block was written: the 18 noise_seed_E
runs, the 4 anchor runs n0_E:25 / 29 / 46 / 4 (Seed 0), the `R` key of
`waves/n0_E/landing_R.json`, noise_v3 and base_v3. Not read: any other
n0_E row, `extracts/random_E`, `extracts/methods_E_*`. No GP was fit.
Holdout exposure is unchanged. E-D1b, E-D4, E-D5 and E-D7 are unaffected.

## AMENDMENT 2026-11-17b — time-limit margin erratum (≈ 1.4×; per-round monitor) (prompt 63 A3; appendable, §10)

AMENDMENT 2026-11-06b states that ruc_mipgap 0.001 "keeps a 25× margin"
to the RUC TimeLimit; that figure came from January smoke days (max
46 s). Full-year v3 actuals: maximum daily RUC solve 860.7 s on
noise_v3 (`noise_v3/B:1`; 5 of 5,840 RUC days > 600 s;
`ERCOT_NOISE.md` §12), 481.1 s on base_v3, 824 s on n0_E with 11 of 48
runs having at least one day > 600 s (14 days; noise memo 2026-11-17
F7, `solve_time_s` / `status` only). Against TimeLimit = 1,200 s the
margin is ≈ 1.4×, not 25×. No time-limit hit has occurred (0 on
noise_v3 and base_v3). The identity (0.001 / 1,200 s) is unchanged. A
hit makes the incumbent depend on wall-clock speed and node load; the
S2 SUSPECT gate (every RUC OPTIMAL) catches it per run and stays the
guard. Added: a per-round monitor in 55's `grade_round` — the count of
RUC days > 600 s and the maximum daily RUC solve time of the round,
written to the round record (the strategy session edits 55's spec
text). Nothing else changes. Update 2026-11-18: noise_seed_E max
821.3 s, 3 days > 600 s over 18 runs, 0 hits.

## AMENDMENT 2026-11-18 — screening_v3 actuals + reads (prompt 62 Part C; appendable, §10; disclosure only; E-D3 not reopened)

**What changed.** Nothing in the plan's rules, bars, X, HV ledger,
holdout, baseline, seats or site slate. The 11 `screening_v3` rows are
analysis-only and never enter `load()`, the GP, §6.3 R or the random
baseline. Source: `analysis/pool/SCREENING_V3.md` and
`screening_v3_{sites,locational,covariate_rho,ranking,dominance}.csv`
(landing commit e58f4bd). The reads were frozen as prompt 62 §4.5,
verbatim in `waves/screening_v3/README.md`, in wave commit c986da0
before any Y.

- **Budget actuals:** 11 / 11 runs, SUSPECT 0, identity v3 on all.
  Wall-clock was 4.8–5.5 h per run at 4 slots, except tasks 9 and 10
  (sites 204 and 20), which took 8.9 and 9.5 h. That is about 259
  core-h in total.
- **Replicate:** `screening_v3:11` overall.csv md5 equals
  `location_oat_v2:3` (dc5b00da…), so there has been no code or data
  drift since 11-06.
- **Bars:** B_j from `ercot_noise.json` (61 §3, D2 excluded). 23
  graded ids have B_j > 0. D2 is not graded because it is 0/0 at
  base_v3. Holm is applied over the 23. `ercot_noise_seed.json` B_seed
  is reported beside B_j (N1 binding at 242.1). No verdict changes
  under B_seed.
- **LOCATIONAL** (pocket_120 ∪ wind_near, 8 sites, vs far, 5 sites;
  Holm ≤ 0.05, |HL| ≥ 2 B_j, Moses 95 % interval excludes 0):

  | id | HL / B_j | Holm p |
  |---|---|---|
  | V1 | −33.1 | 0.036 |
  | E1 | −8.7 | 0.036 |
  | N4 | −2.7 | 0.047 |
  | N5 | +4.3 | 0.036 |
  | E6 | +10.3 | 0.036 |
  | E3 | −4.6 | 0.036 |
  | V3 | −60.8 | 0.036 |

  Of the seated ids, N1 is NOT LOCATIONAL: −3.0 B_pert and −1.43
  B_seed, exact p 0.093, Holm p 0.65, and the interval contains 0. The
  other 15 ids are NOT LOCATIONAL as well. Among them, X1 (−6.1 B, Holm
  p 0.30) and V2 (+32.6 B, Holm p 0.087) fail on p. E2 and E8 are
  separated but fall below 2 B.
- **Confounds (disclosed):** the C tier holds one PV site (116); the
  WIND-only sensitivity agrees in sign and size. ω spans 0.10–0.97. 81
  % of 163's relief is own-site, which is accounting reclassification
  at saturation. E1 has ρ = −0.90 with ω.
- **Matched-MW ranking vs E-D3 slate:** the v3 top 6 are 270, 275,
  274, 110, 140 and 146, all on buses {120, 2, 75}, so the **SLATE
  BUS-SET HOLDS**. 275 enters and 163 leaves, which matches the stated
  prediction on all three counts. No site is TIED (band B_V1/180 =
  89.9 MWh/MW; 146 and 163 sit ±1.01 bands from the boundary). Kendall
  τ_b(v2, v3) = 0.667, exact p 1.3e-4. E-D3 stands.
- **Dominance:** two non-slate sites are not dominated on V1/E1/N1:
  116 (by 0.72 B, on E1) and 91 (by 0.44 B, on N1). On V1/E1/N4 only
  116 is not dominated. Both are within one bar. They are disclosed
  and flagged for the PI. E-D3 is not reopened in this campaign.
- **E1 per site:** WITHIN GAP BOUND (G_site + G_base) at 16 / 16 sites.

**What had been seen.** When this block was written:

- screening_v3 rows 1–11;
- wave D L180 rows 3/6/9/12/15/18;
- base_v3:1;
- `ercot_noise.json` and `ercot_noise_seed.json`;
- the committed 62 Part B outputs.

Not read: `extracts/random_E` and `extracts/methods_E_*`. No GP was
fit. Holdout exposure is unchanged. These Y landed after 62 Part B (the
E-D1b input). They change no seat: the Part C block is appended to §E
of `POOL_N0E_STANDINGS.md`.

## AMENDMENT 2026-11-24 — E-D1b rule v2 (disclosed post-hoc): role gate, residual-resolvability guard, confidence-bound thresholds, order-based suppression, component and conflict rules, materiality floors, one pooled bar, override protocol

Source: prompt 65 v1.1 §2 with §8 folded in (§8 overrides §2–§5 where they differ) and `debug/objective-rule-review-2026-11-24.md` §3 (rule v2, items 0–10 verbatim). Committed ALONE, before `analysis/pool/pool_n0E_v2.py` and before any rule-v2 statistic is computed; no GP fitted (`analysis/ercot_gp/committed_configs.json` absent); no acquisition; holdout exposure 0 / 24; random_E unread.

**2.1 Seen before this block.** Everything in AMENDMENT 2026-11-17's
ledger plus: the v1 Part B read (d706199: all n0_E statistics, seats
V1 · E1 · N1), the Seed-bar re-grade (baf77c3: N1 3.05, R4 1.12, N4
14.4), screening_v3 (e58f4bd: N4 LOCATIONAL, N1 not; bus set holds),
location_contrast_E (4b7bf85), the family-free strength-first trial
(V1, V2, N1), the three reviewer reports (11-24). This amendment is
NOT blind. It is justified only by §1–§5 quantities (spread, noise,
rank concordance, conflict, physical role), never by any front, HV, GP
fit or optimum (none exist). No surrogate has been fitted on n0_E for
decision purposes; holdout exposure 0 / 24; random_E unread.

Ledger additions (prompt 65 v1.1 §8.15): the 11-24 reviews computed anchor E1 / N1_off / X1 spreads from the noise_seed_E Seeds 1–4 runs (already-seen runs) and estimated residual IDR/B from printed η²_T and IDR; the floors and the §4b clause were worded after that.

**Disclosure wording for every output:** "This amendment is post hoc and not blind. It was written after the v1 read, the Seed re-grade, screening_v3 and the N4–V1 residual interval were known. We do not present it as a pre-registered selection. Every station reports three vectors from the same runs: v1 pre-registered (V1 · E1 · N1), v2 (V1 · E1 · N4), and v2 with borderline → REDUNDANT (V1 · E1). A claim about the flowgate objective is stated only as conditional on v2. Rule v2 is pre-registered unchanged for the next dataset, which is its real test."

**2.2 Role table (physics, one line each; signed by Kay as the PI's proxy; the PI may revise before the fit; corrected per prompt 65 v1.1 §8.10).** Only OUTCOME measures can be seated. Seatable OUTCOME set: {V1, E1, X1, N4}.

| id | role | reason |
|---|---|---|
| V1 | OUTCOME | wasted renewable energy; ISO/policy metric (lost PTC value) |
| V2 | PROXY(E1) | 1 − thermal share at fixed load; a reparametrisation of total PEM MW; ρ with E1 0.99 |
| V3 | DIAGNOSTIC | internal to the twin's dispatch |
| E1 | OUTCOME | production cost (efficiency); the E seat is fixed by plan §1.2 |
| E2, E3 | COMPONENT(E1) | fixed / variable parts of E1 |
| E4 | TRANSFER | generator-side settlement Σ LMP × generation + reserve + uplift (incl. the twin) |
| E5 | OUTCOME (dead) | uplift ≡ 0 |
| E6 | TRANSFER | VRE producer revenue incl. the twin's sales |
| E7 | PROXY(E4) | mean price = E4 / constant load |
| E8 | DIAGNOSTIC | price dispersion, no welfare meaning |
| E9 | DIAGNOSTIC (dead) | scarcity bus-hours; dead / not responding |
| X1 | OUTCOME | CO₂ externality (collinear with E1 here) |
| R1 | GUARD | load shed; plan §1.3 |
| R2 | GUARD | reserve shortfall; plan §1.3 |
| R3 | GUARD | over-generation slack |
| R4 | PROXY(E2 start-up cost) | thermal starts; start-up cost already in E2 and not additive in $, so not COMPONENT; wear not modelled |
| R5, R6 | DIAGNOSTIC | ramping descriptors |
| R7, R8 | DIAGNOSTIC | commitment state; undirected |
| N1 | PROXY | unweighted count over ~120 lines the design cannot reach; = N4 + N1_off |
| N2 | DIAGNOSTIC | coarse count |
| N3 | GUARD | thermal-limit slack violation |
| N4 | OUTCOME | L252 (bus-120 export limit) binding hours — the one pocket line that binds (asserted); congestion frequency the PEM relieves; L252's 29.5 GWh/yr overload is design-invariant, so no upgrade-deferral claim |
| N5 | DIAGNOSTIC | full-only; direction inverted (min of a negative spread rewards congestion); −N5 reported as depth beside N4 |
| D1 | DIAGNOSTIC (investor outcome) | H2 electricity; near-deterministic in x; used in the E1 − B·D1 lens |
| D2 | DIAGNOSTIC | utilization ratio |
| D3 | check | nuclear starts |

**2.3 Rule v2.** M_max = 4; family tiers V MAY, E MUST (fixed to E1 by §1.2), X MAY, R MAY, N MAY. The ten numbered items of the memo (§3, copied verbatim) state the rule; the instantiations that follow (prompt 65 v1.1 §8, verbatim, numbering kept) govern wherever they differ from the items. The "FLAGGED-pair exception" of prompt 65 v1 is deleted.

Rule v2 (verbatim, memo §3 items 0–10):

0. Governance: rule, value tree and thresholds committed alone with a sha256 before any statistic on the selection population; signer named; seen-data ledger; changes only via §9.
1. Value structure (signed by the PI): families = fundamental nodes with tier MUST / MAY / GUARD; every measure has one role OUTCOME / ALTERNATE / COMPONENT(of) / TRANSFER / PROXY(target) / GUARD / DIAGNOSTIC with a one-line physical reason and a written direction; PROXY, TRANSFER, DIAGNOSTIC never seated; family order is the only cross-node tie-break.
2. Noise bar: B_j = max(3·σ_j, max|δ|) with σ_j pooled over the pre-registered sources (perturbation deltas /√2, solver-seed replicates; in-box anchors preferred), df recorded; sources disagreeing by > 2× are disclosed, never switched after the read; structural-zero pairs excluded by an md5 rule.
3. Resolvable: RESOLVED iff lower 90 % bound of IDR/B ≥ 2 (χ² interval on σ at its df) and Mantel p ≤ 0.01 on the size-residuals; ADEQUATE iff point estimate ≥ 5; FLAGGED in [3, 5); not seatable below 3. Materiality floor M_j in natural units: IDR ≥ max(2·B_j, M_j). COMPOSITION-RESOLVABLE iff the same on r_j = y_j − f̂_j(T).
4. Redundant: raw oriented Spearman ≥ 0.90 AND NOT (both COMPOSITION-RESOLVABLE and upper 90 % bound of residual ρ < 0.50); SIZE-CO-MONOTONE otherwise (both kept, disclosed); borderline pairs resolve to REDUNDANT; order-based suppression (a candidate is suppressed iff REDUNDANT with any earlier eligible candidate in walk order); Kendall τ and the Brockhoff–Zitzler δ dominance-preservation share reported.
5. Conflict: TRADE-OFF(size) raw ≤ −0.50; TRADE-OFF(composition) residual ≤ −0.50 with both COMPOSITION-RESOLVABLE.
6. Seat walk (M_max = 4): families in order; within a family OUTCOMEs in PI order then ALTERNATEs; eligible iff ADEQUATE (or FLAGGED, marked) and not suppressed; a MUST family with nothing RESOLVED → HALT FOR PI (constraint / replicates / declared proxy / drop with disclosure); a MAY family → EMPTY, "not at stake in this box"; a seat with no CONFLICT partner is demoted; empty seats never back-filled; a second seat in one family only by PI decision under five conditions (disjoint component or complement, ADEQUATE, residual |ρ| < 0.5, a trade-off or a locational pass, δ ≥ 5 %); fixed seats from earlier frozen tests are honoured, failing ones HALT.
7. Components: at most one of {m, m′ = m + c}; if m is seated, c becomes a guardrail with a flag at 2·B_c worsening vs base.
8. Consequences: M ≠ planned → ref point, τ and gate numbers re-derived by pre-registered formulas before the campaign.
9. Override: amendment before any surrogate fit / acquisition / holdout read; ledger diff; general rule re-applied to all families; reason only in §1–§5 quantities; pre-registered vector co-reported; at most one per campaign.
10. Output: one table per measure (role, tier, B_j all sources, IDR/B with CI, residual IDR/B with CI, η²_T, Mantel p raw/residual, ρ raw/residual with CIs, δ, conflicts, status, why each alternative lost).

Instantiations (prompt 65 v1.1 §8.1–§8.8, §8.12; verbatim):

1. **Bar (two-run scale, pooled df 22).** Perturbation source (design-2 (site 206) structural-zero pair excluded): per design d ∈ {1, 3, 4} the three runs {reference (A ≡ B by md5, counted once), A-perturbed, B-perturbed}; s²_pert = Σ_d Σ_r (y_r − ȳ_d)² / Σ_d (n_d − 1), ν_pert = 6. Seed source: s²_seed = mean of the 4 per-design ddof-1 variances, ν_seed = 16. Pooled s_j² = (6·s²_pert + 16·s²_seed)/22, ν = 22 (equal-variance assumption; sources disagreeing > 2× disclosed: N1, E9). B_j = max(3·√2·s_j, max|δ| over the 6 perturbed and 16 Seed deltas). σ interval (two-sided 90 %): s_j·[√(22/χ²_{22,0.95}), √(22/χ²_{22,0.05})] = s_j·[0.805, 1.335]; B_j^up = max(3·√2·1.335·s_j, max|δ|). Every "90 % bound" is an end of a two-sided 90 % interval. Zero-bar set is computed, not asserted from v1 (expected {E5, R1, R3}; E9 picks up a Seed bar).
2. **Joint bootstrap for IDR/B** (b = 1…10,000, default_rng(6262)): resample the 48 designs with replacement, IDR* = Q90 − Q10 (v1 quantile method); σ*² = s_j²·22/χ²_22 drawn independently; B* = max(3√2σ*, max|δ|); lower bound = 5th percentile of IDR*/B*. Residuals: f̂_j fixed on the full data, resample r_j. Disclose that the iid bootstrap on Sobol points is conservative.
4. **Definitions.** RESOLVED iff lower-90 % joint bound of IDR/B ≥ 2 AND raw Mantel p ≤ 0.01. COMPOSITION-RESOLVABLE iff residual Mantel p ≤ 0.01 AND lower-90 % joint bound of IDR(r_j)/B_j ≥ 2 AND IDR(r_j) ≥ M_j. Seatable iff role OUTCOME AND RESOLVED AND IDR ≥ max(2·B_j, M_j) AND IDR/B (point) ≥ 3 AND not suppressed; ADEQUATE ≥ 5, FLAGGED [3, 5) marked. Mantel: Spearman between |Δy| (or |Δr|) and ‖Δu‖₂ in unit-cube design coordinates, 1,128 pairs, 9,999 label permutations, default_rng(6262), same permutation stream for every id, one-sided p = (1 + #{perm ≥ obs})/10,000.
5. **Materiality floors (disclosed: set after the relative responses were seen; compared against the point IDR):** V1 1 % of base_v3 curtailment = 58,287 MWh; E1 0.1 % of base_v3 total cost = $8.06M — the median pair gap bound G_a + G_b ($40.16M; E1 IDR 0.83×) is printed as an evidence column, NEVER a floor; X1 0.1 % of base CO₂ = 194,521 t; N4 1 % of 8,760 h = 88 h; R4 informational only (role gate excludes it): 1 % of base on/offs = 154.
6. **Redundancy (directed).** c (later in walk order) is REDUNDANT given p (earlier, already SEATED) iff oriented raw ρ(c, p) ≥ 0.90 AND NOT ESCAPE. ESCAPE iff c is COMPOSITION-RESOLVABLE AND [p is not COMPOSITION-RESOLVABLE, OR the 90 % interval of residual ρ(c, p) lies entirely below 0.50]. BORDERLINE-PAIR iff c is COMPOSITION-RESOLVABLE and the residual-ρ 90 % interval contains 0.50. A raw ρ whose 90 % interval contains 0.90 is treated as ≥ 0.90. Fisher-z se: raw √(1.06/45); residual √(1.06/39) = 0.165 (the 6-bin smoother spends ≈ 6 df). Labels: SIZE-CO-MONOTONE = raw ≥ 0.90 with ESCAPE; non-seatable ids never suppress.
   **§4b borderline resolution (inside the rule; no run-time PI exception):** a BORDERLINE-PAIR (c, p) is NOT REDUNDANT iff some s already seated before c satisfies (i) upper-90 % bound of residual ρ(c, s) ≤ −0.50 (CI-confirmed composition trade-off) AND (ii) Steiger's Z for dependent correlations sharing s (Fisher z of the residual Spearmans, n_eff = 42) gives one-sided p ≤ 0.05 that ρ_res(c, s) < ρ_res(p, s). Otherwise REDUNDANT. The δ-share is printed beside it and never decides.
7. **Walk.** Families V, E, X, R, N; within a family OUTCOME before ALTERNATE, then PI priority, then global_order id; c is suppressed iff REDUNDANT given some already-SEATED member. After the walk, a seat with no TRADE-OFF partner (raw ≤ −0.50 or residual ≤ −0.50 with both COMPOSITION-RESOLVABLE) among the other seats is DEMOTED → DIAGNOSTIC, its family EMPTY, checked once (no iteration); if E1 has no partner → HALT. Empty seats never back-filled.
8. **N1_off guardrail (monitor; never halts; no acquisition role).** Per run from line_summary.csv: N1_off = N1 − N4 (base_v3 30,750 line-h); ΔN1_off vs base; leakage ΔN1_off/(−ΔN4) when ΔN4 < 0 (a finding, not a violation). Round flag if any run has (a) ΔN1_off ≥ 2·B_N1off with B_N1off computed on N1_off from the noise_seed_E (df 16) and noise_v3 line_summary tables by the item-1 recipe (expected ≈ 390–480; printed; the 11-17 value 242.1 printed beside as the v1-memo value); or (b) a NEW bottleneck: a non-pocket line with base hours_ge_99pct = 0 reaching ≥ 88 h; or (c) N3_off = Σ sum_violation over non-pocket lines ≥ base (61,477 MWh) + 2·B_N3off. Every round prints the three non-pocket lines with the largest Δhours (expected L247, L188, L1).
12. **δ-error:** reference set F = all non-dead OUTCOME ids (V1, E1, X1, N4) oriented by dir, values in bar units ỹ_j = y_j/B_j; δ_k of dropping k from S = max over pairs (a, b) with a ⪯_{S∖k} b of (ỹ_ak − ỹ_bk)₊; share π_k = #{pairs comparable under S∖k with ỹ_ak − ỹ_bk > 2} / #{comparable pairs}; report π_k, δ_k and Kendall τ_b (raw and residual, per pair) for each seat and each single-swap alternative; bootstrap 2,000 design resamples, rng 6262, distinct-index pairs, π 2.5/97.5 %, δ point + 90th percentile. Never selecting except the second-seat condition π ≥ 5 %.

**2.4 Reporting lens (§8.11).** column only (no front): Δnet ≤ 0 by construction (replacement ≈ $24/MWh < B = $40) and falls monotonically with MW; capex excluded — one sentence in every table. Assertion of the twin's exclusion from E1: on base_v3 and n0_E:25 (one anchor, via pool_row / gen_summary — disclosed) Σ non-renewable Unit Cost == E1 == overall Total costs to $1 and Unit Cost over is_pem rows is NaN/0; the CRC Prescient source check is replaced by the citation (data_extractors.py get_fixed_costs / get_variable_costs thermal-only, checkout c453890).

**2.5 Override protocol** (rule v2 §9): this is the one override of this campaign; a second one HALTs. The pre-registered vector V1 · E1 · N1 is co-reported from the same runs at every analysis station. Governance (§8.14): §3 expected seats are a prediction, not a target. If the real walk gives anything other than V1 · E1 · N4, write the §3 outputs to the worktree UNCOMMITTED, do NOT commit (iii) or (iv), do NOT write §5, report the seat table and STOP. Any rule change after commit (ii) is a second override (§2.5) and HALTs the campaign; the PI's only lever then is to reject the whole amendment and revert to v1 (V1 · E1 · N1). The §3 sentence about a "FLAGGED-pair exception" is deleted. Commit (iii) and (iv) only on the expected result.

**2.6 Consequences (§8.9; the dated design space).** `objectives` = ONLY the v2 seats in JSON order (V1, E1, N4), each `status: "SEATED (rule v2, AMENDMENT 2026-11-24)"`; new top-level `co_reported: {"N1": {"status": "PRE-REGISTERED (v1), co-reported"}}`; `guardrails`: R1 (plan §1.3), R2 `flag_at: "2 x base_v3 = 312.2 MWh (base 156.08; plan AMENDMENT 2026-11-17)"`, R3 (over-generation, monitor, flag > 1 MWh; base 0), N3 (thermal-limit slack, monitor, flag at +2·B_N3 vs base 90,951 MWh), N1_off (item 8); `reporting`: E1 − 40·D1 column, −N5 and L252 mean flow beside N4, induced CO₂ intensity ΔX1/D1, additionality −ΔV1/D1, replacement cost ΔE1/(D1 + ΔV1); `objective_rule: "AMENDMENT 2026-11-24"`; assert every round `N4 == N4_L252` else report the pocket sum with the split. 54 Part B passes `--design-space waves/design_space_E_2026-11-24.json` (no 54 code change; 54 has no accepted-version list — that assert lives in tools/make_ercot_n0.py and keeps its default path). 55 (owner of analysis/methods_E/) updates arms_E.json in its own commit: design_space path, objectives ["V1","E1","N4"], R2 base 156.08 / flag 312.16, N1_off monitor.

## AMENDMENT 2026-11-24b — M = 2 consequences; GP fit definition v2 (MAP, L-BFGS-B, restarts); one holdout re-open round (strategy session; appendable, §10; disclosed post-hoc)

**What had been seen.** Everything in AMENDMENT 2026-11-24's ledger, the 65 real read (ae6d80a), 54 Part B's outputs (b23021c: house-fit LOO curves, holdout scorings 8/24 with results known, the exploratory 10,000-step Adam diagnostic designed AFTER the holdout was scored), and the two 54 acceptance reviews (GP statistics; PI-audience). Kay (PI's proxy, 2026-11-24 night) instructed: tune the GP hyperparameters so the GP properly describes the data set; do not stop.

**1. M = 2 consequences (rule v2 item 8).** Seated objectives V1, E1 (AMENDMENT 2026-11-24). Reference point R from `waves/n0_E/landing_R.json`: V1 3,977,491.39 MWh, E1 $8,163,727,647.92 (plan §6.3 formula over the 48 grading rows; unchanged). τ_exact = 0 (Σ_exact = 0, 5ca9650) → the stop rule is budget-cap-only; τ_res (report-only) from the Σ_c V1/E1 block (`ercot_noise_seed_sigma_c.csv`) at the navigation starts, computed by 55 Part B. §6.4 gate numbers for M = 2 ("any objective"): C2 7.4e-4 (per objective 3.7e-4), C3 2.2e-6 (per objective 1.1e-6); the gate rules themselves are unchanged. Navigation tier: E-D7 recommendation n* = 48 (54 Part B; Kay decides).

**2. 54 Part B third holdout tier.** None was scored (n* = 48 is a plan tier). Exposure 8 of 24 after the house-fit round.

**3. GP fit definition v2 (replaces the "campaign fit definition" of §5 for every fit from this block on; the arm set, the inclusion rules, the LOO NLPD selection with the > 2 paired-se rule and the tie order are UNCHANGED).** Finding (54 Part B §3, reproduced on synthetic data by the acceptance reviewer): the house fit (bogp `train_gp`: Adam, 700 steps, lr 0.01, raw lengthscale init 0) stops before convergence — raw lengthscales cannot move more than ≈ 7, inferred noise lands 3–4× above the measured chatter σ_c for V1/E1, LOO bands 1.7–2.7× wider than a converged fit, and a single-start long Adam run lands in different likelihood modes at different n (multimodal; MLE runs to infinite lengthscales on near-linear objectives). Definition v2: float64; MAP (not MLE) with BoTorch's dimension-scaled lengthscale prior LogNormal(√2 + ½·log d, √3) on inputs in [0,1]^6, a noise prior LogNormal centred on σ_c²/s_y² (log-sd 1) and a standardized noise lower bound 1e-6 (the measured-floor arm keeps its floor); optimizer L-BFGS-B (`fit_gpytorch_mll` / scipy), maxiter 1,000, ftol/gtol ≤ 1e-6; 16 seeded restarts (default init + 15 prior draws, `default_rng(5454)`), best MAP kept; converged iff ≥ 2 restarts reach the best value within 1e-3·n nats, else flagged; the convergence flag and the best-vs-second-mode gap are recorded per fit. The GP used by 55 for acquisition is fitted with the same definition as the graded one.

**4. One holdout re-open round (plan §4 retirement amended once).** Under definition v2: re-run the training-size study LOO-only (no exposure); re-select the arms at n = 48; score the holdout ONCE per seated objective at n = 48 only — 2 scorings (V1, E1), exposure 8 → 10 of 24 (N4/N1 co-reported: LOO-only, no scoring) — against the same bar [43, 48]. Pre-registered fallback: an objective whose v2 config fails the bar keeps its house-fit commit (which passed). `committed_configs.json` is rewritten LAST with `fit_definition: "v2 (AMENDMENT 2026-11-24b)"` per objective (or `"house (fallback)"`), the previous file kept as `committed_configs_housefit.json`; the holdout is retired again after this round; no further re-open without a new amendment (and this block says at most one). Disclosure: the holdout had been seen once (8 scorings, results known); the fit change was motivated by a training-side optimizer diagnosis, not by holdout residuals.

**5. Reporting fixes from the 54 reviews** (no number changes): the mechanism L flag is labelled COMPOSITION-OR-LOCATION (54 v3.2 header); the status page opens with the three PI answers (calibration, accuracy in B units and % of range, n*); the E-D7 row carries options and cost; "B_j" names only the rule-v2 bar (`pool_ed1b_v2.csv`), the v1 perturbation bar is "B_pert"; untraceable literals are computed or dropped; "n* = 48" is read as "no tier below 48 suffices; whether 48 suffices is untested (the LOO curve is still steep, slope ≈ 1.3)".
