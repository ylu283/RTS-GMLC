# SLIDE_TEXT_1016 — auto-dump of bo_1016.pptx (FINAL pre-meeting, Kay-approved)

## Slide 1
  recap
  1
  BO
  •  Last meeting (10-13)
  •  whether 32 starting points is a good choice for GP & hyperparameter tuning (done)
  •  5-10 seed BO (still running)
  •  ERCOT where to build PEM and what size (not started)
  •  Other projects (no decisions needed today)
  •  GTEP. Run PCM on the 2035 fleets
  •  AIChE 2026 talk: ERCOT figures freeze next week.
  NOTES: Kay's wording 10-16. Rehearsal detail if asked: three decisions needed today = seed-study start size (NXT-D10a), tuned grading GP (NXT-D10b), seed count 5 vs 10 (1014-D1). GTEP: coal case solved on CRC 10-12 (5/6 optimal <= 1%, B1 accepted at 2.93% gap); PCM on the 2035 fleets awaits two data choices (generator parameters, load basis). Sources: pi-agenda.md §4; living-report-gtep.md. Verbal reconciliations for the recap wording (review 10-16): 'ERCOT figures freeze next week' — figure WORK starts 10-22, the freeze itself is 11-01 (slide 17); '5-10 seed BO (still running)' — 3 trajectories are live + P1 complete; the 5-vs-10 count is today's decision, the full study has not launched.

## Slide 2
  Your three asks from Tuesday — all three moved
  2
  TB| Ask (Tue 10-13) | Status | Result in one line
  TB| Evidence that n0 = 32 is a good choice | DONE — zero new PCM runs | 32 is not yet sufficient: curtailment / cost error still drops a lot at 48; calibration at 32 is sound
  TB| Would hyperparameter tuning help? | DONE — pre-registered hyperparameter study | Yes, where the pathology lives: rbf+log1p repairs the round-3 audit (coverage 5/8 to 8/8)
  TB| 5-10 random seeds behind the conclusions | RUNNING — 3 new trajectories live | P1 complete (hard cap); P2 / P3 / N1 graded r1; need your seed count to scope the rest
  •  Also closed this week:
  •  Stop rule held at both P1 overrun checkpoints (r3 = 0.62 τ, r4 = 0.30 τ — official grading).
  •  Shed mechanism identified from hourly data: day-ahead commitment, not PEM scarcity sales.
  •  ERCOT fuel-mix audit: our conversion is exact (45/45); the flagged discrepancies trace to the published dataset — AIChE figures stand.
  Needed from you today: 3 decisions — seed-study n0 · grading GP · seed count (5 vs 10) — plus the wave-D wait condition restated and the standing g1 sign-off (slide 17).
  NOTES: Sources: analysis/initial_design/N0_EVIDENCE.md; methods_C ledgers; mechanism/MECHANISM.md (261bed4); admin debug/fuelmix-check-2026-10-15.md. Dating: the meeting was Tue 10-13; the 1014-D* IDs are dated by when the decisions were recorded (10-14).

## Slide 3
  32 is not sufficient by looking at the error curve
  3
  [PICTURE 10.7x3.4 in]
  •  Holdout RMSE / noise floor (default GP)
  •  curtailment: 17.4, 9.4, 5.0
  •  cost: 15.4, 7.9, 5.3
  •  shed: below floor at every n0 (noise-limited)
  - the curve is still descending at 48.
  •  But 32 could navigate BO ok
  •  ranking Spearman ≥ 0.94; hyperparameter tunning at 32 looks good
  NOTES: criteria.json: E1 I(32to48) curt 0.470, cost 0.331 vs 1/3-rule 0.153/0.163 and 0.25 cap; E2 winner cov95 44/44/47 in [43,48]; Spearman >= 0.94 all objectives. Shed: 22/48 holdout rows below the 3,000 MWh floor. If asked why the 1/3 rule is the right bar: pre-registered geometric-convergence proxy (next 16 points should buy < 1/3 of what the last 16 bought); the 0.25 cap is a second independent bar; and at 48 the error is still ~5x the noise floor on curt/cost — the verdict survives any reasonable bar. If asked how a noise-limited shed GP drove a 3-objective BO: at explored designs shed is near-binary (the 22.4 MWh floor event vs nonzero); the GP captures that ordering, and Q2 (slide 15) shows the residual shed is PEM-independent — acquisition pressure correctly shifted to curt/cost. If asked 'your agenda said 3.0x at 48, the slide says 5.0x': the agenda quoted the in-sample LOO curve (curt 17.1-6.6-3.0); this slide is the stricter untouched-48-design holdout (17.4-9.4-5.0). The holdout is the honest number; both fail E1 the same way.

## Slide 4
  Parity plot comparison, point by point
  4
  [PICTURE 6.2x5.6 in]
  GP 95% intervals with the floor
  [PICTURE 6.2x5.6 in]
  same GPs but likelihood noise bound fixed 1e-9;
  NOTES: make_fig_parity.py: re-plot of the prompt-39 holdout scores (role=default); asserts rmse_over_floor matches holdout_results.csv to 1e-9 and cov95 exactly, per panel, before drawing. If asked why the shed bars are so wide: the predictive sd includes the floor-constrained noise (3,000 MWh) — the signal itself sits below the floor.  WHY SOME BARS ARE LARGE (STE-100, read as needed). The bar width is 1.96 x the GP's predictive standard deviation. The predictive variance is the sum of two parts: model uncertainty (distance from the training data) plus observation noise (>= floor). Three mechanisms: (1) A design far from the training data gets a long bar; a design near a training cluster gets a short bar. This is why bars differ inside one curtailment or cost panel, and why all bars shrink from 16 to 32 to 48 points. More points repair this. (2) The shed noise cannot go below the 3,000 MWh floor, so each shed bar is at least +/-6,000 MWh at every design. The full row is uniformly wide. This is our conservative assumption, not a GP failure; more points cannot repair it (the no-floor panels prove it: bars shrink 6x). (3) On the winner slide, the shed GP works on a log scale; the same log width becomes a percentage band in MWh, so bars explode for large predictions. This is a scale effect, not more noise; the coverage stays almost the same. Fast read: width varies with position = data-limited, buy points; full row wide = noise-limited, the floor speaks; bars explode with the prediction = log-scale effect, trust the coverage numbers.

## Slide 5
  Selection rule
  - LOO.
  - ranked by LOO NLPD (negative log predictive density. It penalizes both bad accuracy and bad calibration)
  Result
  Objective、
  Shed: rbf + log1p
  2. Curt: rbf + log1p
  3. cost: rbf + (std unchanged)
  Parity plot comparison, after hyperparameter tuning
  5
  [PICTURE 6.2x5.9 in]
  •  Curtailment: 17.1 / 7.3 / 4.3 × floor (default: 17.4 / 9.4 / 5.0) — better at 32 and 48; at 16 it is overconfident
  •  Cost: 10.0 / 5.0 / 3.1 × floor (default: 15.4 / 7.9 / 5.3) — accuracy ++.
  •  Load shed: 0.76 / 0.82 / 0.58 — still sub-floor everywhere; tuning neither helps nor hurts what noise already limits
  Search space:
  - Kernel: Matérn-5/2 (the campaign default) vs RBF vs Matérn-3/2.
  - Output transform: std (linear standardization) vs log1p.
  - Noise: inferred (the floor is a lower bound) vs fixed-at-floor (the noise is locked at the floor).
  - Lengthscale prior: none (the bo-gp default) vs the BoTorch default Gamma(3, 6).
  NOTES: make_fig_parity_winner.py; fits.json winners; all 9 panels assert rmse_over_floor (1e-9) + cov95 (exact) vs holdout_results.csv role=winner. Read vs the previous slide: tuning buys accuracy on curt/cost at 32/48 but NOT a replacement for more points (winner@32 curt 7.3 is still worse than default@48 5.0); shed unchanged (noise-limited); winner log1p shed upper quantiles explode (bars clipped at the data range).  PLAIN-ENGLISH REHEARSAL (STE-100). Why the shed row looks messy: The bars are not new noise. They show the same noise floor as before. The winner GP for shed works on a log scale. The default GP works on a linear scale. On a linear scale, the noise floor is a constant band (about +/-6,000 MWh per bar). On a log scale, the noise floor is a percentage. The bar grows with the predicted value. For a design with near-zero shed, the bar is small. For a design with large shed, the bar is very large; the plot cuts these bars at the frame. The model is not worse: coverage is almost the same (44/48 vs 47/48). Why we accept this configuration: We fixed the selection rule before any test. The rule used only the 32 training points; the holdout stayed untouched. The winner is more accurate on curtailment (9.4 -> 7.3 x floor) and on cost (7.9 -> 5.0 x floor). It repairs the round-3 audit (5/8 -> 8/8). Shed does not change in practice: shed error is below the noise floor for both models, and the large shed bars change no decision. We use the winner only to grade and to predict; the BO search path does not change. A percentage noise band agrees with the simulator (quiet at zero shed, noisy at large shed), but it is too wide at the top; a better noise model is future work.

## Slide 6
  GP for shed works on a log scale. The default GP works on a linear scale. On a linear scale, the noise floor is a constant band (about +/-6,000 MWh per bar).
  On a log scale, the noise floor is a percentage. The bar grows with the predicted value.
  Parity plot comparison, after hyperparameter tuning
  6
  [PICTURE 6.2x5.9 in]
  NOTES: make_fig_parity_winner.py; fits.json winners; all 9 panels assert rmse_over_floor (1e-9) + cov95 (exact) vs holdout_results.csv role=winner. Read vs the previous slide: tuning buys accuracy on curt/cost at 32/48 but NOT a replacement for more points (winner@32 curt 7.3 is still worse than default@48 5.0); shed unchanged (noise-limited); winner log1p shed upper quantiles explode (bars clipped at the data range).  PLAIN-ENGLISH REHEARSAL (STE-100). Why the shed row looks messy: The bars are not new noise. They show the same noise floor as before. The winner GP for shed works on a log scale. The default GP works on a linear scale. On a linear scale, the noise floor is a constant band (about +/-6,000 MWh per bar). On a log scale, the noise floor is a percentage. The bar grows with the predicted value. For a design with near-zero shed, the bar is small. For a design with large shed, the bar is very large; the plot cuts these bars at the frame. The model is not worse: coverage is almost the same (44/48 vs 47/48). Why we accept this configuration: We fixed the selection rule before any test. The rule used only the 32 training points; the holdout stayed untouched. The winner is more accurate on curtailment (9.4 -> 7.3 x floor) and on cost (7.9 -> 5.0 x floor). It repairs the round-3 audit (5/8 -> 8/8). Shed does not change in practice: shed error is below the noise floor for both models, and the large shed bars change no decision. We use the winner only to grade and to predict; the BO search path does not change. A percentage noise band agrees with the simulator (quiet at zero shed, noisy at large shed), but it is too wide at the top; a better noise model is future work.

## Slide 7
  Tuning helps exactly where the pathology lives
  7
  •  The start-set GP was ok
  •  32-start LOO: curtailment rms_z 0.81, coverage 31/32.
  •  Hyperparameter study (pre-registered NLPD rule)
  •  Winners: rbf + log1p (shed, curtailment), rbf (cost). Picked on the 32 starts, committed before any holdout scoring.
  TB| curtailment | default GP | rbf+log1p
  TB| coverage (of 8) | 5 / 8 | 8 / 8
  TB| rms z-score | 2.008 | 1.050
  [PICTURE 7.2x2.7 in]
  NOTES: part_h_loocv.csv (main-effects + best-combo design, 19 config-objective fits, LOO NLPD rule); hbo_cell.json; fits.json committed 07:34 UTC, first holdout call after. Proposal: adopt winner for grading/prediction only; acquisition untouched (NXT-D10b). H-BO cell mean_z: default 1.426 -> winner 0.967. If asked 'tuned-32 is still worse than default-48 — why not just use 48?': they fix different pathologies — tuning repairs late-round COVERAGE (5/8 -> 8/8), more points buy ACCURACY (winner 7.3x floor at 32 vs default 5.0x at 48); we propose both — tuned grading now, 48-point final paper surrogate (the D10a rider). Figure added 10-16 on Kay's ask: tuning before/after at n0=32 on the holdout — default (gray) vs pre-committed winner (blue). curt 9.40->7.32, cost 7.88->4.99, shed 0.76->0.82 (worse; noise-limited, hyperparameters cannot beat the floor; winner's log1p upper quantiles explode on shed - bars clipped). The parity slides earlier in the deck use the PRE-tuning campaign-default GP (m52+std) throughout - deliberately, to show the GP as deployed.  WHAT EXACTLY WAS THE TUNING STUDY (STE-100, read as needed). Search space, 4 axes: kernel Matern-5/2 (campaign default) vs RBF vs Matern-3/2; output transform std vs log1p; noise inferred (floor = lower bound) vs fixed-at-floor; lengthscale prior none (bo-gp default) vs BoTorch default Gamma(3,6). We did not run the full factorial. We used a main-effects + best-combo design: 19 config x objective fits (record: part_h_loocv.csv). Selection rule, pre-registered: leave-one-out on the 32 training points only; rank by LOO NLPD in original units (NLPD penalizes bad accuracy and bad calibration); ties within 0.02 nats break by LOO RMSE. We committed the winners to fits.json before the first holdout call (07:34 UTC). Winners: shed rbf+log1p (new kernel + new transform); curt rbf+log1p (same two changes); cost rbf (new kernel only, std unchanged).

## Slide 8
  Decision
  8
  (a) BO need study starts from 32 or 48?
  Start at 32
  Comparable to the previous running; hyperparameter tuning
  Start at 48
  More accurate surrogate, but +16 NEW PCM runs per fresh seed (≈ +25% per-seed cost) I think it – computational advantages of the paper’s claim
  NOTES: Full decision text: pi-agenda.md NXT-D10 (rigorous + plain versions). If asked 'if the curve is still descending at 48, why not 64?': the nested Sobol extends by construction — draws 49-64 are already defined, so a 64-point tier for seed 0 costs +16 runs ≈ 240 core-h and lets E1 be re-run at 48→64: if I(48→64) passes the 1/3-rule, 48 is certified as the final surrogate; if not, we learn the curve's slope. Proposed as a cheap one-seed add-on decided after the seed study launches — it does not gate anything today.

## Slide 9
  Stop rule closed at both overrun checkpoints (official)
  9
  [PICTURE 9.3x3.3 in]
  •  Live decision (10-10)
  •  STOP at r2: gains 0.69 τ, then 0.17 τ.
  •  Overrun verdict
  •  r3: 0.62 τ — below τ.
  •  r4: 0.30 τ — below τ. Hard cap; P1 complete.
  •  Cost of ignoring the rule
  •  16 extra runs bought +6.9% HV, every increment sub-threshold.
  NOTES: methods_C/P1/ledger.json; r4 graded on CRC (a8df435). τ = 5.263e16. Strategy-session preview reproduced every graded entry to relerr ≤ 2e-16 before the official grading landed; official numbers matched digit-for-digit.  TALK TRACK (60 s). The rule was fixed before the campaign: stop after two rounds in a row gain less than tau, a threshold set from the measured simulator noise. Dark line = live campaign: r1 gained 0.69 tau (strike one), r2 gained 0.17 tau (strike two) -> stop at 48 evaluations (10-10). A rule that fires once proves little, so we ran two more rounds as record-only overrun (gray tail): r3 0.62 tau, r4 0.30 tau, both below the bar, both graded officially on CRC. Right plot: all four bars sit under the red line. Ignoring the rule for 16 extra runs bought +6.9% HV, every increment sub-threshold - exactly the spend the rule exists to refuse. P1 complete at the hard cap. Q&A: 'Isn't 6.9% worth having?' - tau is the pre-registered definition of worth-it, set from noise and run cost; every post-stop increment was below it; if 6.9% feels valuable, adjust tau for the next campaign, do not override the rule after seeing the data. 'The gray line still rises?' - more runs always add some HV; the rule tests the RATE, not the direction. 'Is one trajectory enough?' - no, that is Act 2: the seed study replicates the rule across fresh starts, and the prompt-37 suite measures early/late-stop rates on truth-known problems.

## Slide 10
  How many seeds for bo
  10
  DECISION · 1014-D2 seed count: 5 or 10
  TB| Acquisition | Start set | Latest | Gain vs τ | State
  TB| q-ParEGO | the 32 (seed 0) | r4 (hard cap) (finished) | 0.30 τ | COMPLETE — stop held
  TB| q-ParEGO | fresh 32, seed 2 | r1 | 2.28 τ | r2 array running
  TB| q-ParEGO | fresh 32, seed 3 | r1 | 0.77 τ | r2 array running
  TB| qNEHVI | the 32 (seed 0) | r2 (official) | 0.61 τ | r3 array running; official r2 matched the preview
  NOTES: Ledgers: P2 r1 2.2773 τ (b46d66b), P3 r1 0.7697 τ (6fdfc93), N1 r1 1.43 τ. N1 r2 preview from the validated strategy-session HV replication (matched every graded entry to relerr <= 2e-16; P1 r4 official matched digit-for-digit) — divergence would mean a grading-infra bug, not a science change. If asked 'what if a seed never stops before the cap?': that IS the readout — the distribution of stop rounds; the hard cap bounds worst-case cost at ~1k core-h per seed. If asked 'P3 is sub-tau at r1 — will it stop at r2, and does the rule allow so short a campaign?': yes — P3 holds strike 1; a second sub-tau round stops it, and an early stop is a legitimate datum in the stop-round distribution. And r1 gain is NOT the extension-trigger input: the pre-committed trigger reads the HV-at-stop range (25% of mean gain), computed only once seeds stop.  UPDATE 10-16 PM (verified on CRC): N1 r2 graded OFFICIALLY, gain 3.1844e16 = 0.61 tau — matches the strategy-session preview digit-for-digit; strike 1 for N1. Queue check 10-16 afternoon: P2_r2 (job 1552732), P3_r2 (1552737), N1_r3 (1552743) arrays RUNNING since 10-15 23:48 — auto-submitted by the submit_ready run that night; held collectors queued behind them. No placeholder remains in the deck.

## Slide 11
  Why PEM cuts load shed — explained with hourly data (one model, one year)
  11
  PEM retrofits cut shed not by selling power in scarcity: priced PEM demand absorbs the wind forecast, so the day-ahead RUC commits ~1.2 GW more thermal and the scarce hours arrive with headroom.
  [PICTURE 7.9x3.3 in]
  •  H1 commitment headroom — supported, dominant
  •  zero-shed designs commit +1.2-1.3 GW more thermal; headroom 737-771 MW vs exactly 0; extra thermal covers 107-171% of the shed difference in all 8 pairs.
  •  H2 scarcity sales (as driver), H3 location (slack-bus accounting), H4 reserve substitution — all contradicted
  •  Q2 floor: confirmed
  •  all 7 designs: one winter-morning event (12-18 h7, 22.4 MWh), same +962 MW commitment change, decomposition residual 0.000.
  •  Caveat: a property of cost-based RUC under priced withholding — model sensitivity goes to Discussion.
  NOTES: MECHANISM.md (261bed4): verdict table + two paper-ready paragraphs. Paper wording change: 'zero shed' → '≤ 22.4 MWh/yr, one PEM-independent commitment-limited event'. Spoken framing if useful: the day-ahead commitment stops trusting free wind. If asked 'is this a Prescient / cost-based-RUC artifact?': the mechanism needs only that DA commitment responds to the net-load increase from priced PEM withholding — any RUC formulation with that coupling should reproduce it; a reliability-based-RUC sensitivity is a bounded Discussion item, not new campaign work.

## Slide 12
  ERCOT: our conversion is exact; the quirks are the dataset's
  12
  BO workflow: initial-design evidence + stop-rule closure · 2026-10-16
  ROADBLOCKER · wave D gated on 1014-D3
  TB| Flag | Finding | Action
  TB| Coal 32% of energy (real 2019: 20%) | TX-123BT's own coefficients put all 13 coal units below all 113 gas units in merit order | inherit + disclose
  TB| Gas looks like peakers | implied heat rates ~18.5 MMBtu/MWh (real CC ~7) — the paper says 'typical' coefficients | inherit + disclose
  TB| PV fleet 8.26 GW (real 2.3) | the DATASET is internally inconsistent: its paper says 2.48 GW, its published files 8.26 | inherit published files + 1 sentence
  TB| LMP $34 vs 2019 DAM $38 | right order — inflated heat rates ≈ offset missing scarcity adders | quote as 'TX-123BT prices'
  •  Our conversion: 45/45 cost coefficients exact; load side matches ERCOT 2019 actuals to the MW (383.8 TWh; preliminary peak 74,666 MW).
  •  Consequence: NO AIChE figure needs a re-run; diverted-wind ≈ $30/MWh stands as an in-model result.
  •  Wave D (location grids on ERCOT) IS the 'where to build PEM + what size' study from the recap — designed and ready; this audit was its last technical blocker. It waits only on the condition you set at the last meeting — please restate it.
  NOTES: Full audit: admin/prompt/bogp/debug/fuelmix-check-2026-10-15.md. ERCOT 2019 actuals: gas 47%, coal 20%, wind 20%, nuclear 11% (ERCOT Fact Sheet 11/2020). If asked 'coal dispatches below gas in this dataset — can any ERCOT siting conclusion transfer to the real grid?': siting signals ride on network congestion + local renewable curtailment, which the dataset's transmission topology and wind/PV placement carry; the merit-order quirk shifts WHICH thermal units back down, so we report siting as a TX-123BT in-model result and check robustness via the bid-0 placebo rows in the wave-D design.

## Slide 13
  Decisions today + the two weeks ahead
  13
  BO workflow: initial-design evidence + stop-rule closure · 2026-10-16
  TB| # | Decision | Default if you only nod
  TB| 1 | seed-study n0 = 32 or 48 | 32 (comparability); paper surrogate at 48
  TB| 2 | NXT-D10b: rbf+log1p grading layer | adopt, grading only
  TB| 3 | 1014-D1: seed count | 5 seeds now, extend to 10 if spread is wide
  TB| 4 | Wave-D condition (1014-D3) | — needs your restatement
  TB| 5 | g1 nuclear accounting (NXT-D7) | option c (+$28.188M, fronts unchanged)
  •  Next two weeks
  •  P2/P3/N1 arms run to their caps (automatic).
  •  Seed study launches at your count + n0.
  •  Stop-rule validation suite (synthetic + replay) lands.
  •  AIChE ERCOT figures 10-22 → 10-31.
  •  Figure freeze: 11-01.
  NOTES: pi-agenda.md carries the rigorous + plain text for every open decision. Scope if the PI counts rows: 1-3 are today's NEW decisions; 4 is a restatement request; 5 is the standing NXT-D7 approval. g1 rehearsal (the PI's memo mentions option (b) flipping a verdict): the base nuclear fuel curve is FLAT — $3,208.99 per committed hour, zero marginal cost above 396 MW — so (a) the old delivered-x-$8.1 framing dissolves; (b) delivered-only is ill-defined and FLIPS the location analysis's nuclear cost slope (a LOCATION.md verdict); (c) restore the deleted curve: +$28.188M/yr CONSTANT in omega — an intercept shift only, every front and slope unchanged. Full text: g1_nuclear_fuel_accounting_PROPOSAL.md + pi-agenda NXT-D7.

## Slide 14
  Backup — hyperparameter grid by-products
  14
  BO workflow: initial-design evidence + stop-rule closure · 2026-10-16
  •  Secondary findings from the Part-H study (not decision-relevant today):
  •  The BoTorch default Gamma(3, 6) lengthscale prior is harmful on every objective here (curtailment error 27× floor) — bo-gp's no-prior default is right for this problem.
  •  Matérn 3/2 never beats Matérn 5/2 on any objective.
  •  Fixing the noise at the floor (vs inferring it above the floor) changes results little.
  •  No axis interaction was triggered: each winning combination beat every single-axis change.
  NOTES: part_h_loocv.csv; selection rule: LOO NLPD in original units, ties within 0.02 nats break by LOO RMSE; winners committed to fits.json before the first holdout call.

## Slide 15
  Still need to explore the results any maybe in discussion section of the paper/talk
  15
  Why does shed fall as PEM MW rises?
  PEM adds no load. Wind priced at the bid makes thermal look cheaper in the RUC so more thermal committed and therefore more headroom
  I think checking committed MW / headroom on shed hours, low- vs high-MW design; reserve shortfall must not rise (monitor it next to shed)
  Currently what are running/want to do
  Is bo q-ParEGO stable across replicates at a fixed max budget of 64 (64 = 32+4*8)? Is one qNEHVI run consistent with it?
  I’m not sure if setting {random number = bo final + initial} is legit so I put 64
  Another bo + random
  qNEHVI which is also very standard and it can discover if the results rely on the aq function
  Running 10-12 21:00, might take 5-6 days ?
  36  ERCOT v2
  Re-run ERCOT on the corrected cost data for AIChE
  A base ×3, B screening 19, C selection 9
  A + B landed 10-13 02:30; base read done. C: 2 of 9 failed; fixed (7c5fb8d); nuclear rows 6–11 rerun
  C rerun ≈ 10-14; wave D ≈ 10-18/19
  37  Stop rule
  Does the stop rule work on problems with a known truth?
  1,540 tasks; 0 PCM runs
  Running since 10-12 evening
  ≈ 10-13 → 10-15
  NOTES: Power-systems reviewer 10-12; parameters.py (renewable split), summarize_wave.py:113-116. Hypotheses until checked. Sources: /Users/yilu/Documents/GitHub/RTS-GMLC/trial_0826/campaign/analysis/bo_stage2/BO_STAGE2.md

## Slide 16
  16
  Currently what are running
  2. ERCOT
  AI pointed that I used the wrong conversion notebook in the code and there could be an improvement for gen conversion and it might be able to change the nuclear situation back to normal.
  Job submitted
  Maybe 2-3 days (?)
  test returned on right
  TB| Quantity (2019, base) | v1 (mis-converted costs) | v2 (corrected)
  TB| Real-time LMP, mean | $14.5/MWh | $33.8/MWh
  TB| Fixed cost | $6.75 B | $3.63 B
  TB| Variable cost | $1.19 B | $4.46 B
  TB| True curtailment | 9.44 M MWh | 5.92 M MWh
  TB| Nuclear | gen-1 cycles (≈ 25 starts) | both units on all 8,760 h, 0 starts
  TB| RUC quality | TimeLimit races on capped days | 0 % capped; 1,460 / 1,460 OPTIMAL
  TB| Replicate spread (total cost) | ±$80M bimodal | 0 (4 runs byte-identical)
  The screening of one pem at one site
  the top 6 by rank: sites 163, 140, 146, 270, 110, 274 by curtailment
  •  Smallest gen_pmax of the six: 185.4 MW.
  Proposed sizes 60 / 120 / 180 MW: 6 sites × 3 + nuclear × 3 = 21 rows. On nuclear, 60 MW is ω ≈ 0.025. The nuclear rows compare against the sites; they do not sweep nuclear.
  Smallest gen_pmax of the six: 185.4 MW.
  1. top 6 sites ning (163, 140, 146, 270, 110, 274) × 3 sizes, plus nuclear × 3 sizes = 21 runs.
  - Problem: the 6 sites differ by only 9 % and sit on just 3 buses, so they cannot show a location effect.
  2. contrast sites instead, 21 runs in total:
  - the best wind site on each bus (163, 140, 146), two PV sites (116, 30) and the lowest-ranked wind site, each × 3 sizes;
  - nuclear × 2 sizes, after the nuclear cost-accounting bug is fixed.
  NOTES: Power-systems reviewer 10-12; parameters.py (renewable split), summarize_wave.py:113-116. Hypotheses until checked. Sources: /Users/yilu/Documents/GitHub/RTS-GMLC/trial_0826/campaign/analysis/bo_stage2/BO_STAGE2.md

## Slide 17
  17
  Currently what are running
  3. Does the stop rule good
  Does the stop rule work on problems with a known truth?
  Might be needed for paper discussion/methodology
  - 2-D replay grids 81 design, known true frontn.
  - 6-D emulators: a GP fit to the grid. They are cheap enough to evaluate all 531,441 designs exactly.
  Run BO (q-ParEGO and qNEHVI) and random search with 50 seeds with current stop rules
  Measure
  1. Early-stop rate: how often the rule stops while real progress is still possible. Pass: ≤ 20 %.
  2. Regret: how much HV is lost by stopping instead of continuing to round 8. Pass: median ≤ 1τ.
  3. Versus a fixed budget: is the rule better than simply "always stop after k rounds"? Pass: on or below that line
  Submitted on crc maybe 3-4 days?
  NOTES: Power-systems reviewer 10-12; parameters.py (renewable split), summarize_wave.py:113-116. Hypotheses until checked. Sources: /Users/yilu/Documents/GitHub/RTS-GMLC/trial_0826/campaign/analysis/bo_stage2/BO_STAGE2.md

## Slide 18
  Backup — where the GP is uncertain (2-D slice)
  18
  BO workflow: initial-design evidence + stop-rule closure · 2026-10-16
  [PICTURE 9.6x3.9 in]
  Predictive sd / floor on the two most active tiers (wind_303, wind_317); other 4 ω at training median; n0 = 48
  /Users/yilu/Documents/GitHub/RTS-GMLC-n0evidence/trial_0826/campaign/analysis/quality_report/bo_1016/fig_sd_heatmap.png
  •  Shed (left): sd/floor 1.07-1.20 everywhere — a featureless map pinned just above the floor; more points cannot change it (noise-limited).
  •  Curtailment (right): sd/floor 3.1-7.4 — lowest where training designs cluster, rising at the corners (data-limited; exactly what more points fix).
  NOTES: make_fig_sdheat.py. Slice axes picked by curtailment ARD lengthscales (wind_303 ls 2.0 — by far the most active; wind_317 5.4). sd is the full predictive sd incl. likelihood noise, in floor units.

