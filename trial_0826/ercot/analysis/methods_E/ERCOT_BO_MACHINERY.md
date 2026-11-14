# ERCOT BO machinery — runbook (prompt 55 v3.1; `analysis/methods_E/`)

Every Kay-side command, in order. Zero simulation is started by any script
here except `submit_ready_E.sh` (login node, literal `yes` not required — it
prints the state table and `qquota` first; use `--dry-run` to look).

Budget per round (standings 8 actuals): 8 runs x 5.3 h wall / 21 core-h on a
fast node (group A) or 11 h / 45 core-h on a slow node (group B) = **170–360
core-h per round per lane**, ~1 round per calendar day per lane; the five
lanes run in parallel (40 slots). Option C = 5 lanes x cap 4 = 20 rounds =
160 runs = 3.4k–7.2k core-h (plan 8 table: 3.2k–6.7k at the v2 bracket).

## 0. Gates before anything runs (Part B, prompt 55 section 3)

| gate | file / decision | who |
|---|---|---|
| committed GP configs | `analysis/ercot_gp/committed_configs.json` (54 Part B) | 54 |
| 52 frozen incl. the exact covariance | `analysis/noise_v3/ercot_noise.json`, `ercot_noise_exact_cov.csv` | 52 / 54 B step 0 |
| R | `waves/n0_E/landing_R.json` (53 landing) | 53 |
| E-D7 | `committed_configs.json["E-D7_decided"]` = 32 or 48 | Kay / PI |
| E-D5 | plan 6.1 AMENDMENT appended; README wording switched | Kay |

`arms_E.json["part"] = "B"` makes `init` ASSERT all of the above (real loader,
real configs, landing_R, exact cov). Part A (`"part": "A"`) runs on the stub
loader + placeholders and is for the dry round only.

## 1. One-time environment check (login node)

    cd /groups/adowling/ylu28/RTS-GMLC-ercot          # the CRC clone (ercot/tx123)
    git pull --ff-only origin ercot/tx123
    cd trial_0826/ercot
    ARM=qnehvi SEED=0 bash analysis/methods_E/acquire_E_job.sh --check-env   # env BOGP_CRC_botorch + bo-gp SHA

The bo-gp clone (`arms_E.json["bogp_clone_crc"]`) must be at
`bogp_sha_expected` (60e6328…). A mismatch refuses: no mid-campaign brain swap.

## 2. T0 — init every lane + propose r1 (one authorized push, K6)

Locally (bogp-botorch) by the executor after Part B, OR on CRC by Kay:

    cd trial_0826/ercot
    /opt/anaconda3/envs/bogp-botorch/bin/python analysis/methods_E/acquire_E.py init-all --arm qnehvi
    /opt/anaconda3/envs/bogp-botorch/bin/python analysis/methods_E/acquire_E.py recompute-tau --seed 0
    /opt/anaconda3/envs/bogp-botorch/bin/python analysis/methods_E/acquire_E.py status

`init-all` writes, per lane `analysis/methods_E/qnehvi/s<seed>/`: `ledger.json`
(R, tau_joint / tau_marginal computed ONCE from the start set, hv0,
guardrail_mode monitor), `tau_init.json`, `ROUND_LOG.md`, `round_records.json`
(r1), and `waves/methods_E_qnehvi_s<seed>_r1/` (design_matrix.csv, 8 retrofit
dicts, predictions.csv, manifest.json, README.md). It asserts the five r1
sets are pairwise distinct (the seed reaches the sampler). The arm README
(`qnehvi/README.md`) carries the tau statement, the E-D5 readings, the banned
framings and the M = 4 note. **STOP — Kay action (K6):** commit + push
fast-forwarded into ercot/tx123 by the strategy session after a fresh rebase;
the CRC clone pulls. tau and R are appended to `ERCOT_BO_PLAN.md` as a dated
AMENDMENT.

## 3. Each round — Kay, on the CRC login node (~1 per calendar day)

    bash trial_0826/ercot/analysis/methods_E/submit_ready_E.sh --dry-run    # look
    bash trial_0826/ercot/analysis/methods_E/submit_ready_E.sh              # submit everything READY

Hold mode (default): for a lane whose round-k wave is `COLLECTED` (or has no
ledger yet), it submits the acquisition job (`acquire_E_job.sh`, grades k and
proposes k+1, `--no-submit`, commit + push), then the round-(k+1) array held
on the acquisition (`-hold_jid`) and the collector held on the array
(`-hold_jid`, `-M ylu28@nd.edu -m ea`). The array reads the design at task
start and fails loudly if the acquisition wrote none. Markers
`waves/<wave>/SUBMITTED` and `s<seed>/SUBMITTED_acq_r<k>` are committed, so a
re-run never double-submits. `--no-hold` submits only arrays whose design
exists (two visits per round).

Collector (`methods_E_collect.sh`): gate on every row's
`overall_simulation_output.csv` -> `extract_ercot.py --full` per row ->
`runtimes.csv`, `wallclock.csv`, `identity.txt` -> `pool_objectives.py
--run-dir -> pool_full_metrics.json` -> `extracts/<wave>/COLLECTED` ->
ercot-bot commit of the slim tables + json + marker (`*.csv.gz` stay in
`$GROUP` storage; `.gitignore` line `extracts/methods_E_*/**/*.csv.gz`), 5-retry
push. Identity: `--ruc_mipgap / --ruc_time_limit` from `waves/GAP_DECISION.json`
at run time (the array refuses without it); `SMOKE_GATE` on
`waves/smoke_v2/SMOKE_PASS`.

Acquisition job (`acquire_E_job.sh`): `run --round k --no-submit` = pull ->
**C1 ingest gate** (all 8 runs at the v3 identity, objectives finite, design
matrix == proposal, SUSPECT and shed checks) -> double-spend guards -> grade
k (record_only) -> propose k+1 -> commit + push -> STOP. A crash writes
`s<seed>/WEDGED_r<k>.md`; a gate refusal writes `FAILED_r<k>.md` and proposes
nothing.

## 4. Grading: what the ledger records each round

`gain_k = HV_k - HV_{k-1}` over the accumulated lane set at the frozen R
(SUSPECT and R1-violating runs excluded), `gain / tau_joint`, `gain /
tau_marginal`, `would_stop_joint`, `would_stop_marginal` (stateless two-strike:
`(gain_k < tau) AND (gain_{k-1} < tau)`), the joint-vs-marginal sensitivity
column, `first_fire_round` per ruler, `n_outside_ref`, calibration z-stats
with the **C2** (covered <= 4 of 8, any objective) and **C3** (>= 3 of 8 with
|z| > 3, any objective) REVIEW flags, R1 violations, SUSPECT keys, the R2 flag.
The rule NEVER halts and C2/C3 NEVER halt; every lane runs to `hard_cap`
(DONE.md). If tau = 0 (all exact zero): `gain_tau` is null, `would_stop` is
false — budget-cap-only, the cap governs. E-D5 OPEN: both readings of a fire
(plan 6.1 fallback: first fire = "the stop"; E-D5 recommendation: the cap is
the stop, the fire is descriptive) are in the README until Part B.

## 5. HALT FOR DECISION (plan 1.2 / 1.3) — the only machinery halts

`s<seed>/HALT_FOR_DECISION.md` is written when, in ONE round, >= 2 runs have
shed > 1 MWh or >= 2 runs are SUSPECT. The round is graded and recorded;
nothing is proposed; `propose` / `run` refuse while the file exists;
`submit_ready_E.sh` prints HALT and submits nothing for that lane. Kay
decides (continue / change the config by a dated plan amendment / stop the
lane), renames the file (e.g. `HALT_r2_DECIDED.md`), records the decision in
`PROGRESS.md`, and re-runs `submit_ready_E.sh`. The cost objective is never
switched mid-campaign.

A SINGLE shed violation does not halt: the run is marked infeasible-for-claims
and excluded from fronts/HV, and from the NEXT round the lane's acquisition is
constrained qNEHVI (shed GP, shed <= 1 MWh; `guardrail_mode: constrain` in the
ledger; `settings.constraint` in the round record). R2 > 891.8 MWh is a round
flag only.

## 6. Stop a lane now / recover

    touch analysis/methods_E/qnehvi/s<seed>/STOP      # next acquisition writes DONE.md and proposes nothing
    qdel <array/collector/acq JIDs from the SUBMITTED markers>

Never re-run an acquisition for a round that already proposed (the
double-spend guards refuse: record / wave dir / `qstat -r` full job name).
A FAILED wave (missing rows): resubmit the missing tasks ONCE by hand
(`qsub -wd waves -v WAVE=<wave> -t <i> -N <wave>_array analysis/methods_E/methods_E_array.sh`),
then the collector; remove the `FAILED_<wave>.md` marker when it lands.

## 7. Local tests (bogp-botorch, by file name)

    cd trial_0826/ercot
    /opt/anaconda3/envs/bogp-botorch/bin/python -m pytest tests/test_methods_E_tau.py tests/test_methods_E_hv.py \
        tests/test_methods_E_wave.py tests/test_methods_E_acquire.py -q -p no:cacheprovider
    /opt/anaconda3/envs/bogp-botorch/bin/python analysis/methods_E/dry_round_E.py      # pinned-settings dry round (~25 min)

The acquisition tests swap the 100-s botorch call for a cheap stand-in except
`test_real_fast_acquisition_init_and_r1`; `dry_round_E.py` runs the real
pinned settings and writes `DRY_ROUND_REPORT.md`.
