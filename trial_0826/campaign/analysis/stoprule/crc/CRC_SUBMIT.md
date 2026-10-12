# Prompt 37 — CRC array (Kay submits ONCE; the executor never runs qsub)

**Order:** prompt 36 (ERCOT) waves first, then 35's launch, then this.
37's 1,140 tasks are 4-core, mostly < 1.5 h each; they may still be queued
behind 35's acquisition jobs. That's fine; nothing here depends on them.

## 0. Gate (paste the outputs to the 37 session before step 2)

1. `BOGP_CRC_botorch` exists (35's ENV_READY commands) — paste
   `~/BOGP_CRC_botorch_pip_freeze.txt` (diffed by the session vs
   `analysis/methods_C/env/bogp-botorch_local_pip_freeze.txt`).
2. `git -C /groups/adowling/ylu28/bo-gp rev-parse HEAD` → must start `60e6328`.

If (1) never appears: use `tasks_M1.csv` (400 rows) instead of `tasks.csv`
below (PREREG §3); M3 is then "not run".

## 1. Separate checkout (never the shared /groups/adowling/ylu28/RTS-GMLC clone)

```bash
cd /groups/adowling/ylu28
git clone -b stoprule <origin-url-of-RTS-GMLC> RTS-GMLC-stoprule   # same remote as the shared clone
cd RTS-GMLC-stoprule/trial_0826/campaign/analysis/stoprule
mkdir -p logs problems
```

From the Mac (truth files are gitignored; ~130 MB):

```bash
scp ~/Documents/GitHub/RTS-GMLC-stoprule/trial_0826/campaign/analysis/stoprule/problems/*.npz \
    <crc-login>:/groups/adowling/ylu28/RTS-GMLC-stoprule/trial_0826/campaign/analysis/stoprule/problems/
```

Verify on CRC (every truth sha256 must match problems.json; prints OK):

```bash
source "$(conda info --base)/etc/profile.d/conda.sh"; conda activate BOGP_CRC
PYTHONNOUSERSITE=1 BOGP_PATH=/groups/adowling/ylu28/bo-gp python -c "
import json, problems as p
d = json.load(open('problems/problems.json'))
for k in p.PROBLEMS_6D: p.Problem(k)            # asserts sha256
import sr_common; print('OK', sr_common.assert_bogp())"
```

## 2. Submit (from analysis/stoprule of the separate checkout)

```bash
qsub -t 1-1140 crc/stoprule_array.sh       # M1-only fallback: qsub -t 1-400 -v TASKS=tasks_M1.csv crc/stoprule_array.sh
qsub -hold_jid stoprule37 crc/stoprule_collect.sh
```

`-r n`, no `-tc`, `-pe smp 4`; only the collector emails. Expected task
count **1,140** (A 500 · B 80 · C 200 · D 20 · E 340). Projected ≈ 400–800
core-h (M3 subset ≈ 0.5–1.5 core-h/run, M1 ≈ 0.2–0.5, replay M3 ≈ 0.1).
Tasks write `results/<cell>/<method>/seed<s>.npz` and checkpoint per
round. The collector writes `summary/` + `summary/MISSING.txt`, commits on
`stoprule` and pushes. Missing tasks: resubmit once with
`qsub -t <id> crc/stoprule_array.sh` (resumes from checkpoint).
