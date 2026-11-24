# methods_E arm `qnehvi` — README (prompt 55 v3.1; written at init, regenerated per lane init)

Lanes: seed_ids [0, 1, 2, 3, 4] (option C: 1 arm x 5 seeds x cap 4 x q 8; plan 8, E-D4
default). Each lane `s<seed>/` has its own ledger; the start set is shared
(`['n0_E']` nav prefix, n0 = 48 — E-D7 source: PROVISIONAL arms_E n0_tier_provisional = 48 (E-D7_decided null)).

## Objectives (M = 2) and their status

- `V1`: SEATED (rule v2, AMENDMENT 2026-11-24)
- `E1`: SEATED (rule v2, AMENDMENT 2026-11-24)

R4 / N1 are PROVISIONAL (E-D1b); E1 waits for the plan 1.2 verdict (E3 if not
READABLE). The cost objective is never switched mid-campaign.

## Sources at this init (Part EMULATOR)

- loader: **real(n0_E: analysis.ercot_gp.ercot_gp_loader.load; Y replaced by the EMULATED start values)+EMULATOR wave tables** · committed configs: **real** · R: ../../waves/n0_E/landing_R.json
- Sigma for tau: ../noise_v3/ercot_noise_exact_cov.csv · form: homoscedastic (Sigma_exact for every start)
- bo-gp SHA 60e6328236e745b3d34dc8cd704bb72888ae5d15 (hypervolume_exact, M-general recursive sweep)

## tau rulers (computed ONCE at init from the 48 starts; equality-asserted every round)

| ruler | value | role |
|---|---|---|
| tau_joint | 0 | HEADLINE (plan 6.1/6.2: noise vectors drawn jointly from N(0, Sigma_exact)) |
| tau_marginal | 0 | RECORDED (independent per-objective normals, marginal sds) |
| joint / marginal | None | the plan 6.2 joint-vs-marginal sensitivity row (third ledger column) |

**The exact cross-batch replicate covariance is identically zero, so tau_joint = tau_marginal = 0: the stop rule is budget-cap-only and the cap governs (plan 3). This is a finding about a deterministic instrument, not a failure.**

Note on the Sigma convention: plan 6.2 pins Sigma = the covariance of the
replicate DELTAS (A - B). Under independent replicate noise that is 2x the
per-run covariance, so tau is larger by sqrt(2) than a per-run-noise tau. The
plan is immutable; the recipe is used as frozen and this is a disclosure, not
a change.

## The stop rule — E-D5 OPEN (both readings carried until Part B)

Per round k the ledger records gain_k = HV_k - HV_(k-1) over the accumulated
lane set (SUSPECT and R1-violating runs excluded), gain_k / tau, and the
stateless two-strike verdict would_stop_k = (gain_k < tau) AND (gain_(k-1) <
tau) under each ruler, plus first_fire_round. The machinery never halts on the
rule; every lane runs to the cap.

- **(a) plan 6.1 fallback** ("analysis not run"): the first fire is "the stop";
  later rounds are still graded and later fires are recorded as descriptive.
- **(b) E-D5 recommendation** (prompt 50: the two-strike form was NOT ACCEPTED
  truth-known — early 49.2 %, regret 1.83 tau): the budget cap is the stop; the
  first fire is DESCRIPTIVE reporting only. Lands as an append-only AMENDMENT to
  plan 6.1 before Part B.

Until E-D5 is decided and appended, both readings are reported side by side
and neither is called "the verdict".

From prompt 49 v2.1 section 2, verbatim:

**Banned framings (pinned)**: "the rule now works" · "validated live" ·
"rescued/fixed the rule" · "V1 beats / outperforms / confirms P1–N1" ·
any V1-vs-arm HV comparison not expressed as "within/outside the
prompt-35 claim-(ii) dispersion band" · describing a no-stop outcome
as "convergence not reached".

## Calibration gates (plan 6.4; per-objective numbers immutable)

C1 ingest = fail-stop (FAILED_r<k>.md, nothing proposed). C2 (covered <= 4 of 8
for any objective) and C3 (>= 3 of 8 with |z| > 3 for any objective) = record +
REVIEW flag, never a halt. The per-objective false-alarm rates are the plan's
(C2 3.7e-04, C3 1.1e-06); at M = 2 the ANY-objective rates are
C2 1 - (1 - 3.7e-04)^2 = **7.4e-04** and C3 **2.2e-06** (standings 7 raised
M = 4; the plan itself does not). Reading note: with the noise inferred small,
|z| inflates by construction — judge against the committed-config cov95.

## Guardrails and SUSPECT (plan 1.2-1.3; wiring = build requirement)

- R1 shed > 1.0 MWh: the run stays in the ledger as infeasible-for-claims,
  excluded from reported fronts and from HV/gain (kept in GP training); the
  round AFTER the first violation flips `guardrail_mode` monitor -> constrain
  (constrained qNEHVI, shed GP constraint shed <= 1.0 MWh; a constant shed
  column is degenerate -> feasibility = 1, recorded); >= 2 violations in one
  round -> `HALT_FOR_DECISION.md` (Kay decides).
- R2 reserve shortfall > 312.16 MWh (2 x base): round flag, recorded, never halts.
- SUSPECT (S1-S3, `meta.suspect`): excluded from HV, gain and (build choice)
  GP training; flagged; >= 2 in one round -> HALT FOR DECISION.

## Acquisition

botorch `qNoisyExpectedHypervolumeImprovement` (the plan's pinned form; botorch
0.16 advises `qLogNoisyExpectedHypervolumeImprovement` for numerics — NOT
adopted, a one-line config alternative), ref_point = R, alpha 0.0,
prune_baseline, SobolQMCNormalSampler(128, seed s), optimize_acqf over
[0, 1]^6, q = 8, 20 restarts x 512 raw samples, sequential.
Seed s = 20261006 + 100 x seed_id + k, `torch.manual_seed(s)` once per process;
the RTS integers are reused on a different X / Y, which is statistically
harmless (the tau RNG is numpy `default_rng(20261006)`, distinct). Proposals
u -> MW = u x gen_pmax at full precision, no snapping; exact 0 = site absent.
