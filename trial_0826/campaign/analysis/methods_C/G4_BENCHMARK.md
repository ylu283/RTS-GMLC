# G4 — qNEHVI full-lattice benchmark (prompt 35)

**Result: 16.0 min wall, 2.6 GB peak RSS** — within the expected
15–90 min / 1.5–3 GB, far below the 3 h / 8 GB trigger. **No candidate-subset
rule:** N1 uses the full lattice (531,441 minus evaluated) every round
(PREREG clarification 3, decided here before N1's first proposal).

| Item | Value |
|---|---|
| Data | n = 40 (S1 32 + bo_C_r1 8), M = 3, P1's R_frozen |
| Proposal | q = 8 sequential greedy, `optimize_acqf_discrete(max_batch_size=512)`, float64 |
| Sampler | 128-sample SobolQMCNormalSampler, seed 20261407 |
| Candidates | 531,401 (531,441 − 40 evaluated) |
| Wall | 961.9 s (python) / 966.7 s (`/usr/bin/time -l`) |
| Peak memory | 2.40 GB (`getrusage`) / 2.61 GB max RSS (`time -l`) |
| Threads | 4 (OMP_NUM_THREADS=4, torch.set_num_threads(4)) |
| Machine | local arm64 (macOS), botorch 0.16.1, torch 2.12.0 |

CRC expectation: the acquisition job runs with `-pe smp 4`; allow ~2× local
wall for slower cores → ≈ 30–40 min per N1 round, well inside `long`.
Raw record: `g4_benchmark.json`.
