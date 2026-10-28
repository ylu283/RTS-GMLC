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
