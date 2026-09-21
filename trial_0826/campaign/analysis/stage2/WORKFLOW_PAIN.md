# Workflow-pain log — Stage-2 C launch (prompt 27 T4; directive requirement)

First production use of the chained-collector automation pattern
(`qsub -hold_jid` arrays → `collect_stage2.sh` → stage2-bot push). Three
metrics as required. Sources: git history of d6, wave manifests, the
09-19/09-20 session records. Items only visible on CRC (block logs,
collector `.o` log, `qacct`) are marked PENDING-KAY — fill in from
`block_1.log` / `block_2.log` and `qacct -j <J1>,<J2>`.

## (i) Cause-coded touch log

| # | When (approx) | Actor | Code | What |
|---|---|---|---|---|
| 1 | 09-19 (T1–T3 session) | session | submit-prep | waves generated + pushed (manifests clean, `74cd5520`, dirty=false) |
| 2 | 09-19 | Kay | submit | block_1.sh — 3-day nuclear ω=1.0 smoke (JID 1458448, SMOKE PASS) |
| 3 | 09-19/20 | Kay | submit | block_2.sh — J1 (n₀ ×16) + J2 (backfill ×10, holds J1) + single collector (holds J1,J2) |
| 4 | 09-20 22:01 EDT | **bot** | — | collector: gate PASS both waves → summarize → commit `fc98902` → push. **Zero human touches.** |

Failure-recovery touches: **0** (no FAILED markers ever appeared; no
resubmissions in git history). Git/race touches: **0 observed** (see iii).
Data-wrangling touches: **0** (CSVs landed via bot; local session only ran
`git pull`). Monitor touches: PENDING-KAY (how often did you check qstat
between blocks?). Human-gated dead time between smoke pass and block_2:
PENDING-KAY (block log timestamps).

## (ii) End-to-end latency decomposition

wave-generated → CSVs-on-d6: **2026-09-19T10:23:08Z → 2026-09-21T02:01:46Z
≈ 39.6 h**, decomposed as:

| Segment | Duration | Evidence |
|---|---|---|
| generation → smoke submitted | human-gated (block_1 handoff) | PENDING-KAY (block_1.log) |
| smoke run + verdict | ~1–2 h by design | SMOKE PASS 09-19, JID 1458448 |
| smoke pass → block_2 submitted | human-gated dead time | PENDING-KAY (block_2.log timestamp) |
| queue + run (J1 16 tasks ∥, then J2 10 tasks) | expected ~2 × ~10 h at ~9.7 h/run with no `-tc` | PENDING-KAY (`qacct -j`: qsub_time/start_time/end_time per task) |
| collector + push | minutes | fc98902 single commit at 22:01:46 EDT |
| results-on-d6 → noticed locally | **~40 min** (bot push → this session's pull at ~22:40 EDT) | pull log |
| time-to-notice of FAILED marker | n/a — none occurred | — |

The dominant segments are queue/run (irreducible) and the two human-gated
handoffs (the paste-block protocol's price). The automation removed the
*post-run* human segment entirely — under the old manual pattern,
results-on-d6 would have waited for the next Kay session.

## (iii) First-pass automation success

**PASS on every locally-observable criterion:**

- Integrity gate: PASS on both waves (26/26 sentinels), no FAILED markers.
- Collector + bot push unattended: **yes** — one commit (`fc98902`),
  bot identity, explicit paths only (2 objectives.csv + 2 site_detail.csv,
  222 insertions), no partial CSVs, no stray files.
- Rebase retries: **no rewrite occurred** — AuthorDate == CommitDate
  (22:01:46-04:00), so the commit was never rebased and the *first* push
  succeeded. Note: the commit's parent is `a7dfa6b` (pushed by the
  prompt-28 session earlier the same evening), so the CRC clone was
  already at origin tip when the collector committed. Whether that is
  because block_2's pull happened late, Kay pulled manually, or simply
  no one pushed between the CRC clone's last pull and 22:01 cannot be
  distinguished locally — the collector `.o` log in
  `waves/stage2_backfill_C/` on CRC settles it. PENDING-KAY.
- Gate resubmissions: 0.

**Verdict:** the pattern worked first time, end to end. The two known
sharp edges for the *next* users (already addressed in prompt 28's
pairgrid collectors): (a) retry-once is thin once several bot pushers
share d6 concurrently — pairgrid collectors use a ×5 retry loop with
randomized backoff; (b) hand-edits to generated array scripts (the `-tc`
strip on 09-20) drift them from their generator — `submit_array.py` now
supports `max_concurrent=None` natively, and `make_batches.py all` is
refused, so regeneration can't clobber frozen waves.
