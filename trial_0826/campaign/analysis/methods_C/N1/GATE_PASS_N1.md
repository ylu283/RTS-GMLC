# N1 GATE PASS — replay gate re-evaluated under AMENDMENT 2026-10-12 (one-sided)

The gate is now one-sided (Kay, 10-12, made AFTER the result; see the
PREREG.md amendment): N1's median must be ≥ the q-ParEGO smoke MIN at both
n = 16 and n = 24. It was re-evaluated on the EXISTING `replay_gate.json`
(sha256 f841a700650721aea72a01747a8354cd03af9fd90667732c67740b9d7d889441),
with no re-run.

| n | N1 median | q-ParEGO min | ≥ min? |
|---|---|---|---|
| 16 | 0.9166 | 0.8444 | yes |
| 24 | 0.9534 | 0.8698 | yes |

**PASS. N1 runs.** Which acquisition does better is answered by N1 vs P1 on
real runs only (§5).

## History: the superseded NOT_RUN record (commit 2596416)

> # N1 NOT RUN — pre-registered replay gate failed (prompt 35 §3.2)
>
> Gate (PREREG clarification 1): N1's (qNEHVI) median HV recovery over the 10
> smoke seeds must lie inside q-ParEGO's 10-seed min–max at BOTH n = 16 and n = 24.
>
> | n | N1 median | q-ParEGO range | inside? |
> |---|---|---|---|
> | 16 | 0.9166 | [0.8444, 0.9295] | yes |
> | 24 | **0.9534** | [0.8698, 0.9518] | **no — ABOVE the max by 0.0016** |
>
> Per §3.2 "Fail → N1 'not run' (pre-registered), report." The failure is on the
> HIGH side (qNEHVI recovered more HV than every q-ParEGO seed at n = 24); the
> gate was framed as an implementation sanity check, but it is pre-registered
> as a two-sided range and is applied as written. Re-admitting N1 would need a
> new pre-registration by the strategy session / Kay (red line: no rule change
> after results). Record: `replay_gate.json` (645 s, bogp-botorch, botorch 0.16.1).
> submit_ready.sh reports N1 as NOT_RUN and never submits it.
