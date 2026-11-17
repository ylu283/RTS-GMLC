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
