# Glossary — multi-PEM PCM campaign

Ubiquitous language for `trial_0826`. One term, one meaning. Written in
Simplified Technical English. If a document uses a term differently,
the document is wrong — fix it or flag it.

## The system under study

- **PCM** — production-cost model. A simulation that clears the power
  market hour by hour for a full year, with endogenous prices.
- **Prescient** — the PCM engine (v2.2.3, patched fork).
- **RTS-GMLC** — the 73-bus test power system. The main campaign runs here.
- **TX-123BT / ERCOT** — the 123-bus Texas system. The scaling case.
- **base case** — the system with no retrofits. All objectives are deltas
  against it. It is an external anchor and is never resubmitted.
- **PEM** — the electrolyzer type we retrofit onto a plant.
- **retrofit** — one plant gets a PEM. A renewable plant splits into
  `gen` + `gen_PEM`. A thermal plant gets a lower p_min and a flat-band
  cost, with forced commitment.

## The design space

- **tier** — a group of plants that shares one design variable. The RTS
  campaign has 6 tiers: nuclear, wind_303, wind_317, wind_122, pv, tail.
- **ω (omega)** — PEM size as a fraction of plant capacity. The only
  design variable per tier.
- **lattice / STAGE2_LATTICE** — the 9 permitted ω values, from 0.05 to
  1.0. Defined once in `campaign/tiers.py`. Never transcribe the values
  by hand.
- **design** — one ω value per tier. The space holds 9⁶ = 531,441 designs.
- **ρ_H2 (rho)** — the hydrogen price, $/kg.
- **derived bid / B** — the PEM dispatch threshold, $/MWh. It is not a
  free variable: B = 20·ρ_H2.
- **scenario A / B / C** — ρ_H2 = 1.0 / 1.5 / 2.0, so B = 20 / 30 / 40.
  Stage-2 runs scenario C only.
- **others absent** — in a pair or OAT wave, the non-studied tiers have
  NO retrofit. Absent is not ω = 0.

## The objectives

- **true curtailment** — wasted renewable energy, with all `*_PEM` units
  excluded. The raw curtailment column counts the H2 stream by mistake.
- **load shed** — unserved energy, MWh per year.
- **K_syn / cost-less-synthetic** — total cost minus the synthetic bid
  costs that the retrofit injects. The campaign's cost objective.
- **g1…g5** — the historical objective pool: cost, curtailment, shed,
  reserve shortfall, start count.
- **g1 issue** — the thermal patch deletes the real nuclear fuel cost
  (~$27.8M/yr). A fix proposal waits for the PI (option c: add back
  +$28.188M/yr, constant in ω).
- **M** — the objective vector the optimizer minimizes. Decided
  2026-10-06: M = {load shed, true curtailment, cost-less-synthetic}.
- **h2** — hydrogen production, MWh equivalent. A diagnostic, not an
  objective. For a thermal retrofit, h2 = Σ(p_max − dispatch).

## Measurement discipline

- **noise floor / ruler** — the size of solver noise per objective,
  measured from repeat runs. A delta is readable only when it is a
  multiple of the ruler. RTS floors: shed ±3,000 MWh, curtailment
  ~5,000 MWh, cost ~$0.5M.
- **replicate** — the same inputs run again. On ERCOT (TL=120) results
  are machine-dependent, so replicates measure real spread.
- **TL=120** — the 120-second cap on each daily market solve (ERCOT
  only). Results are truncated incumbents, not proven optima.
- **bimodal cost** — the ERCOT total-cost noise (±$79.5M). One nuclear
  unit flips between 25 and 26 annual starts. Total cost is unreadable
  there; variable cost is readable.
- **placebo** — a retrofit with an inert bid (B = 0.01). It proved the
  retrofit construction itself adds no artifact.
- **frozen inputs** — completed waves are read-only. No later session
  edits their design matrices, objectives, or raw runs.

## The experiments

- **wave** — one batch of runs with one design matrix, in
  `campaign/waves/<name>/`. Results distill to `objectives.csv`.
- **OAT** — one-at-a-time: sweep one tier, others absent.
- **pair grid** — a 9×9 ω grid for two tiers, others absent. All 15
  tier pairs are done.
- **8c panel** — the standard per-pair figure: iso-value contours plus
  iso-total guides in absolute MW. Spec: pi_0911 §8c, prompt 28 T2.
- **screening** — the first OAT pass that ranks sites and sets tiers.
- **Stage-1 replay** — BO run offline on already-computed grids. It
  validated the machinery: optimum found in 6 evaluations vs 26–46
  for random search.
- **Stage-2** — the live campaign on the full 9⁶ space: 42 initial
  runs + the BO rounds.
- **LOCATION.md** — the location-analysis verdict document. v2 FINAL
  answered PI question #1 and grounded the M decision.

## The optimizer

- **BO** — Bayesian optimization. A GP model proposes designs; the
  simulator answers; the model updates.
- **q-ParEGO** — the batch method: 8 random weight vectors scalarize
  the objectives; each maximizes expected improvement.
- **kriging-believer** — within a batch, the model pretends its own
  prediction is the answer, so the 8 picks do not collide.
- **round** — 8 designs, simulated in parallel (~10 h each). The chain
  submits the next round by itself. Hard cap: 4 rounds.
- **HV / hypervolume** — the volume the Pareto front dominates. The
  stopping signal: stop when HV gain < the noise threshold for 2 rounds.

## The machinery

- **chain** — array job → collector → next step, linked with
  `qsub -hold_jid`. Runs with no human in the loop.
- **collector** — the job that extracts objectives, commits them, and
  emails. Only collectors send email.
- **bot push** — a collector commits as stage2-bot / ercot-bot /
  pairgrid-bot / bo-bot, with a 5-retry backoff push.
- **markers** — `FAILED_*` (a run died), `WEDGED` (the acquisition job
  died), `SUBMITTED` (round receipt), `STOP_BO` (the kill switch),
  `BO_DONE` (campaign finished).
- **smoke** — a short (3-day) test run. A hard gate before any new code
  path burns a full-year window.
- **d6** — the active RTS branch. **ercot/tx123** — the ERCOT branch,
  in the sibling worktree `RTS-GMLC-ercot`.
- **36-hour rule** — 36 h of silence from the chain means investigate.
  Never resubmit blind.

## People and process

- **Kay** — runs the campaign; decides M and launches.
- **PI** — Prof. Dowling; decides accounting, claim scope, and design
  space (the NXT-D items in `admin/prompt/bogp/pi-agenda.md`).
- **prompt** — a numbered execution spec in `admin/prompt/bogp/`,
  written by the strategy session, run by an executor session.
- **鸭哥 review** — a parallel multi-expert review of a prompt before
  it is marked READY.
