# N1 NOT RUN — pre-registered replay gate failed (prompt 35 §3.2)

Gate (PREREG clarification 1): N1's (qNEHVI) median HV recovery over the 10
smoke seeds must lie inside q-ParEGO's 10-seed min–max at BOTH n = 16 and n = 24.

| n | N1 median | q-ParEGO range | inside? |
|---|---|---|---|
| 16 | 0.9166 | [0.8444, 0.9295] | yes |
| 24 | **0.9534** | [0.8698, 0.9518] | **no — ABOVE the max by 0.0016** |

Per §3.2 "Fail → N1 'not run' (pre-registered), report." The failure is on the
HIGH side (qNEHVI recovered more HV than every q-ParEGO seed at n = 24); the
gate was framed as an implementation sanity check, but it is pre-registered
as a two-sided range and is applied as written. Re-admitting N1 would need a
new pre-registration by the strategy session / Kay (red line: no rule change
after results). Record: `replay_gate.json` (645 s, bogp-botorch, botorch 0.16.1).
submit_ready.sh reports N1 as NOT_RUN and never submits it.
