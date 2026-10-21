# OUTLINE_1016 — PI meeting deck, 2026-10-16

Audience: Prof. Dowling. Goal: answer the three 10-14 asks with evidence,
get three decisions. Style: one message per slide; evidence on the slide,
derivation in the notes. Placeholders marked [PH] for results that land
overnight (N1 r2 official grading only — 38 T1 landed 10-15 night).

Number sources (all verified in repo on 10-15/10-16):
- N0 = `analysis/initial_design/N0_EVIDENCE.md` + `criteria.json` (commit 2bb6e73)
- Ledgers = `analysis/methods_C/{P1,P2,P3,N1}/ledger.json` (P1 r4 official a8df435;
  P2 r1 2.2773 tau b46d66b; P3 r1 0.7697 tau 6fdfc93; N1 r1 1.43 tau; N1 r2
  PREVIEW 0.61 tau — strategy-session HV replication, validated to relerr <= 2e-16
  on every graded entry)
- Mechanism = `RTS-GMLC-mechanism:analysis/mechanism/MECHANISM.md` (T1 final, 261bed4)
- Fuel mix = `admin/prompt/bogp/debug/fuelmix-check-2026-10-15.md`
- Meeting directives = `admin/prompt/bogp/pi-agenda.md` §4 (1014-D1..D3)

## Slides

1. **[SUPERSEDED by Kay's 10-16 PM edit — see the PM note at the bottom; the
   deck now opens with ONE short "recap" slide in Kay's wording, entries 1 and
   1b below describe the pre-merge versions]** **Title.** "Initial-design
   evidence + stop-rule closure" — BO workflow status,
   PI meeting 2026-10-16. Sub: answers to the three 10-14 asks; 3 decisions needed.
1b. **[SUPERSEDED — merged into Kay's "recap" slide, 10-16 PM]** **Where we
   stand — 60-second recap** (added 10-16 morning on Kay's request;
   text-only context slide, deck slide 2). Three groups: (a) campaign status —
   BO complete 10-10, random baseline 10-11, $510M economy vs zero-shed/48k-curt
   reliability front, methods-paper scope, no new runs this week; (b) last
   meeting 10-14 — the three directives 1014-D1..D3 mapped to Acts 2/1/3 (D3's
   wait condition was not recorded, re-asked today); (c) other projects —
   GTEP rebuilt on Sandia upstream (tutorials 10-08; coal case on CRC 10-12,
   5/6 optimal <= 1%, B1 accepted 2.9% gap; next = PCM on 2035 fleets, two data
   choices pending) and AIChE timeline (figures 10-22 -> 10-31, freeze 11-01).
   Notes carry GTEP rehearsal detail (B1 definition, 71-81 CTs, 0 retirements).
2. **Your three asks from Tuesday — all moved.** Table: ask -> status -> where.
   (a) evidence for n0=32 -> DONE, zero new PCM runs -> verdict: 32 not sufficient,
   48 measurably better; (b) would tuning help -> YES where the pathology is
   (grading layer), repairs r3 curtailment coverage 5/8 -> 8/8; (c) 5-10 seeds ->
   3 fresh trajectories already running + P1 complete -> need your count.
   Bonus rows: stop rule closed at both overrun checkpoints; shed mechanism
   identified from hourly data (T1); ERCOT fuel-mix audit clean (figures stand).
3. **Divider Act 1.** Is 32 initial points enough? (1014-D2)
4. **The test cost zero new runs.** One nested scrambled Sobol sequence
   (seed 20260821): draws 1-16 = n0, 17-32 = n0b, 33-48 = Q1 (landed 10-13) ->
   16 ⊂ 32 ⊂ 48 by construction. Holdout = 48 i.i.d. random designs
   (`waves/random_C`), zero overlap (asserted), never used to train or tune.
   Pre-flight: regeneration bit-identical; all 4 asserts pass. Criteria
   pre-registered before any fit.
5. **Verdict: 32 is not sufficient — the error curve has not bent.**
   Figure `n0_curve_holdout.png`. Holdout RMSE/floor (default GP):
   curt 17.4 -> 9.4 -> 5.0; cost 15.4 -> 7.9 -> 5.3; shed noise-limited
   (0.75/0.76/0.59, below floor at every n0). E1 fails on curt + cost
   (I(32->48) = 0.47 / 0.33 vs 1/3-rule 0.15 / 0.16 and 0.25 cap). BUT:
   ranking at 32 is fine (holdout Spearman >= 0.94) and calibration at 32
   PASSES (E2: cov95 44/44/47 in [43,48]) — 32 was good enough to drive BO,
   not good enough as a final surrogate.
5b. **The same verdict, point by point** (added 10-16 morning on Kay's request;
   deck slides after this shift +1, 17 slides total). Figure
   `fig_parity_holdout.png`: 3x3 parity grid (objective x n0), predicted vs
   actual on the 48 unseen holdout designs, 95% error bars, campaign-default
   GP. Curtailment/cost rows collapse onto the 45-degree line and tighten
   16 -> 32 -> 48; shed row scattered + wide bars at every n0 (noise-limited,
   coverage honest 47-48/48). NOT a new holdout touch: deterministic refit,
   script asserts every panel's rmse_over_floor (to 1e-9) and cov95 (exact)
   match holdout_results.csv before drawing.
6. **Tuning: yes — where the pathology actually lives.** Part-H LOOCV grid
   (pre-registered NLPD rule, winners committed before holdout): shed/curt
   rbf+log1p, cost rbf. The start-set GP was never miscalibrated; the weak
   r3 audit belongs to the BO-augmented GP. H-BO cell table (rms_z/cov95 on
   the slide; mean_z 1.426 -> 0.967 carried in the notes,
   curt): default 1.426/2.008/5-8 -> winner 0.967/1.050/8-8. Default cell
   reproduces the recorded r3 audit EXACTLY. Also: BoTorch Gamma lengthscale
   prior is harmful on every objective (curt 27x floor); Matern 3/2 never beats 5/2.
7. **Why a seed study is the right next instrument.** Acquisition replay of r1
   (library import, frozen machinery): 32-start GP reproduces the deployed r1
   batch 8/8; 16- and 48-start pick DISJOINT batches (0/8 on every pair) while
   the scalarized posterior landscape stays rank-stable (Spearman 0.94/0.95
   vs the 32-start landscape; min across the 8 weights 0.892).
   Read: n0 moves WHICH points BO probes, barely moves the fitted landscape.
   Whether that changes the final front = an outcome question = seeds (37 + 1014-D1).
8. **DECISION NXT-D10.** (a) seed-study n0: 32 (comparable to the live campaign;
   calibration sound; known ~2x curtailment accuracy cost) vs 48 (accurate;
   +16 NEW runs per fresh seed = ~+25% per-seed cost; only seed 0's 48 points
   exist today). Default recommendation: 32 for the seed
   study (comparability), 48 for the final paper surrogate. (b) adopt rbf+log1p
   for the grading/prediction layer only — acquisition path untouched. Badges.
9. **Divider Act 2.** The stop rule held — and the seed study is running.
10. **Stop rule closed at both overrun checkpoints.** Figure
    `fig_stoprule_closed.png`. Live stop at r2 (gains 0.69 tau, 0.17 tau).
    Overrun (record only): r3 0.62 tau, r4 0.30 tau — both sub-threshold,
    official CRC grading (a8df435). The 16 overrun runs bought +6.9% HV at
    sub-threshold rates — exactly what the rule is built to refuse.
11. **Seed trajectories: 3 new arms live.** Table: arm / acq / start set /
    latest round / gain vs tau / state. P1 qparego seed-0 COMPLETE (hard cap);
    P2 qparego fresh-32 seed-2 r1 2.28 tau (official) -> r2 running;
    P3 seed-3 r1 0.77 tau (official) -> r2 running; N1 qNEHVI r1 1.43 tau
    official, r2 0.61 tau [PH: official grading tonight]. Cost ~1k core-h per
    seed. DECISION (1014-D1): 5 seeds (~5k core-h) or 10 (~10k)?
12. **Divider Act 3.** Mechanism + ERCOT — both unblocked this week.
13. **Why does PEM cut load shed? Explained with hourly data — one model, one
    year (T1, 261bed4). Caveat on-slide: cost-based RUC under priced
    withholding.** Headline:
    "PEM retrofits cut shed not by selling power in scarcity but by making the
    day-ahead commitment stop trusting free wind — the RUC brings ~1.2 GW more
    thermal online." Figure `fig_h1_commitment.png`. Verdicts: H1 commitment
    headroom SUPPORTED-DOMINANT (zero-shed designs commit +1,230-1,276 MW more
    thermal on the low design's 100 shed hours; headroom 737-771 MW vs exactly
    0; extra thermal covers 107-171% of the shed difference in all 8 pairs);
    H2 PEM-sells-in-scarcity CONTRADICTED as driver (grid-sales share
    -0.04..+0.26); H3 location CONTRADICTED as stated (all shed booked at the
    slack bus 113 = reference bus); H4 reserve substitution CONTRADICTED
    (shortfall co-falls, rho -0.93). Q2 CONFIRMED end-to-end: all 7 designs
    shed once — 2020-12-18 h7, 22.425956 MWh — via the SAME +962 MW net
    commitment change (2 CCs + 3 STEAMs on, 1 CT off) in all 7; decomposition
    residual 0.000. Paper wording: "zero shed" -> "<= 22.4 MWh/yr, one
    PEM-independent commitment-limited winter-morning event". Caveat: property
    of cost-based RUC under priced withholding — may be model-specific.
14. **ERCOT: the conversion is clean; the quirks are the dataset's.** 45/45
    coefficients exact. Coal-heavy dispatch = authors' coefficients put all 13
    coal units below all 113 gas units in merit order; PV = dataset's own
    2.48-vs-8.26 GW inconsistency (we inherit published files + one disclosure
    sentence); load side matches ERCOT 2019 actuals to the MW (383.8 TWh /
    preliminary peak 74,666 MW). AIChE figures need no re-run. Wave D still gated on the
    condition from 1014-D3 — please restate it.
15. **Decisions + near-term plan.** (1) NXT-D10a seed-study n0; (2) NXT-D10b
    tuned grading layer; (3) seed count 5 vs 10; (4) wave-D condition;
    (5) g1 accounting (NXT-D7, still open). Timeline: seeds + 37 stop-rule
    validation -> late Oct; AIChE ERCOT figures 10-22 -> 10-31; figure freeze
    11-01.

16. **Backup — hyperparameter grid by-products** (moved off slide 6 per review):
    Gamma(3,6) lengthscale prior harmful everywhere (curt 27x floor); Matern 3/2
    never beats 5/2; fixed-at-floor noise changes little; no axis interaction.

## Review round (10-16, three parallel agents)
- Fact-check: 3 blockers found and fixed (unsupported "2,160-fit grid" claim;
  part_h described as a 72-config factorial — it is a 19-fit main-effects +
  best-combo design; "+50% per-seed cost" for 48-start — deck's own numbers give
  ~+25%). 4 minors fixed (headroom 737-771; H2 "as driver" qualifier; "all
  quirks" overstated vs the audit's 6 verdicts; "preliminary" peak). 16 groups
  of load-bearing numbers verified against primary sources.
- Storytelling (PI's chair): slide-5/8 "48 already paid for" trap defused
  (scoped to seed 0); "SOLVED"/"vindicated" toned to "explained"/"held";
  RUC-artifact caveat moved on-slide; 5->10 extension trigger pre-committed
  (25% range of HV-at-stop, threshold PI-adjustable); grid by-products moved
  to backup; rehearsal answers for 5 hard questions added to notes.
- Layout QA: no must-fix; slide-7 box height trimmed, slide-14 badge shortened.

## 10-16 morning additions (post-review, on Kay's request)
- Parity slide 5b (fig_parity_holdout.png + make_fig_parity.py; reproduction
  asserts vs holdout_results.csv all pass 9/9).
- Ablation slide 5c, v2 on Kay's ask: full 3x3 no-floor grid
  (fig_parity_nofloor.png + make_fig_parity_nofloor.py) mirroring slide 5b
  panel-for-panel (flip to compare); shed-only 2x3 variant kept on disk
  (fig_shed_nofloor.png, no longer in the deck). Finding: THE FLOOR ONLY
  BINDS ON SHED. Free-noise inferred sd: shed 317-527 MWh vs floor 3,000
  (bars ~6x tighter, cov95 45-48/48, RMSE 0.32-0.58x floor); curt 8.5-12.5k
  vs floor 5,000 and cost $1.1-1.9M vs $0.5M — already above floor, so the
  six curt/cost panels barely move (RMSE changes in the 3rd digit).
  ILLUSTRATION ONLY, outside pre-registered axes; hints heteroscedastic shed
  noise -> Discussion. Sub-floor shed RMSE verdict unchanged either way.
- Backup slide (last): uncertainty heatmaps fig_sd_heatmap.png +
  make_fig_sdheat.py — predictive sd/floor on wind_303 x wind_317 (curt's two
  smallest ARD lengthscales), other 4 omegas at training median, n0=48. Shed
  map flat 1.07-1.20 (floor-pinned, noise-limited); curt map 3.1-7.4,
  structured by data density (data-limited).
- Context slide 1b "Where we stand — 60-second recap" (text only, deck
  slide 2): campaign status + 10-14 directives mapped to acts + other
  projects (GTEP next steps, AIChE timeline).
- Deck was briefly 20 slides; Kay's 10-16 PM edit (backed up as
  bo_1016_kay_edit_1016pm.pptx) merged the title slide + recap into ONE
  short slide 1 titled "recap" (Kay's wording, verbatim in the script now):
  BO / last meeting (10-13 — Kay's date; the Tuesday meeting; 1014-D* IDs
  are recording-dated) / 32-points+tuning done / 5-10 seed BO running /
  ERCOT siting+size not started / other projects: GTEP PCM on 2035 fleets,
  AIChE figure freeze next week. Deck now 19 slides (recap=1,
  three-asks=2, ...; decisions=17, backups 18-19).
- Slide-8 notes: rehearsal answer for "why not 64?" — nested Sobol extends by
  construction (draws 49-64 defined); +16 runs ~ 240 core-h for seed 0 re-runs
  E1 at 48->64 to certify 48 as the final surrogate; decide after seed launch.

## Review round 2 (10-16 PM, three parallel agents, post-Kay-edit)
Fact-check: every load-bearing number traced clean to primary sources; 2
on-slide fixes applied — no-floor slide's "1.7-2.7x" contradicted its own cost
numbers (1.9/0.5 = 3.8x) -> "1.7-3.8x"; parity slide said "red line" but the
identity line is black dashed -> "dashed line". Stale notes ref "Q2 (slide
13)" -> 15 after the renumber (only stale ref found).
PI-chair: announce-the-asks line added to slide 2 (3 decisions + 2 carried
items, keybox); wave-D bullet on the ERCOT slide now names it as the recap's
"where + what size" study; seeds slide proposal now points at the visible r1
spread (2.28 vs 0.77 tau); parity slide got a forward kicker to the no-floor
slide; "(default GP)" qualifier on slide 5; "Rider" label on the D10a 48-point
add-on; "Ask (Tue 10-13)" header matches Kay's recap date. Notes rehearsals
added: LOO-vs-holdout number clash (agenda 3.0x vs slide 5.0x), tuned-32 vs
default-48, three-Spearman disambiguation, P3-early-stop/strike logic, g1
option a/b/c walk-through (slide 17 row 5 was unsupported), TX-123BT siting
transferability, recap verbal reconciliations (AIChE "freeze next week" =
work starts 10-22 / freeze 11-01; "5-10 seed BO still running" = 3 arms live,
count is today's decision — Kay's slide-1 wording left untouched).
QA: structure/placeholders/figures/notes clean; OUTLINE digit drifts fixed
here (shed 0.75, Spearman 0.892 min, 2 CCs + 3 STEAMs, mean_z in notes);
script docstring corrected (no SLIDE_TEXT writer; overflow check warns, not
asserts). Known residual: fig_h1_commitment.png title/label collision at top
center (mechanism repo owns the figure; cosmetic, not fixed today).

## Kay's 10-16 PM restructure (LIVE PPTX IS NOW THE SOURCE OF TRUTH)
Kay hand-edited bo_1016.pptx down to 16 slides: Act-1 divider + zero-new-runs
slide DELETED; verdict slide retitled "32 is not sufficient by looking at the
error curve" and trimmed (keybox removed); BOTH parity grids merged onto one
slide 4 ("Parity plot comparison, point by point", two 3x3 figures side by
side); decision slide retitled "Decision", badges + Rider line removed, Kay's
own phrasing; footers removed on several slides. New order: 1 recap, 2 three-
asks, 3 verdict curve, 4 parity floored+no-floor, 5 tuning, 6 replay,
7 decision, 8 Act-2 divider, 9 stop rule, 10 seeds, 11 Act-3 divider,
12 mechanism, 13 ERCOT, 14 decisions, 15-16 backups. Backups of Kay's
versions: bo_1016_kay_edit2_1016.pptx (pre-figure). make_bo_1016_deck.py is
STALE (guard added — refuses to run); edits now go directly into the pptx
via python-pptx.
- Added on Kay's ask (15:03): fig_parity_tune32.png on slide 5 (tuning
  before/after at n0=32, default m52 gray vs pre-committed winner blue, same
  holdout, both roles asserted against holdout_results.csv: curt 9.40->7.32,
  cost 7.88->4.99, shed 0.76->0.82 worse + winner log1p upper quantiles
  explode on shed, bars clipped — honesty kept on-slide). Out-of-sample
  bullets moved to bottom-right. Script: make_fig_parity_tune32.py.
- Clarified (notes, slide 5): the parity grids on slide 4 are the PRE-tuning
  campaign-default GP (m52+std) — deliberate, the GP as deployed.
- Added on Kay's ask (15:20): NEW slide 5 "Parity plot comparison, after
  hyperparameter tuning" — fig_parity_winner.png, the full 3x3 grid refit
  with the Part-H winners (floors ON), all 9 panels asserted vs
  holdout_results.csv role=winner. Winner numbers: curt 17.07/7.32/4.31
  (cov 38/44/46 — overconfident at 16), cost 10.05/4.99/3.14 (cov 48/47/48),
  shed 0.76/0.82/0.58 (cov 44/44/44, sub-floor throughout). Deck now
  17 slides (tuning=6, replay=7, decision=8, Act-2=9, stop=10, seeds=11,
  Act-3=12, mechanism=13, ERCOT=14, decisions=15, backups 16-17).
  Script: make_fig_parity_winner.py.
