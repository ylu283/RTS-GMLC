# ENV_READY: `bogp-botorch` (prompt 35 G2)

**Local env `bogp-botorch` is ready** (2026-10-12). It was made with
`conda create -n bogp-botorch --clone bogp`, followed by
`pip install --no-deps`. `bogp` itself was not touched.

| Package | Version | vs `bogp` |
|---|---|---|
| python | 3.10.20 | same |
| torch | 2.12.0 (CPU) | same |
| gpytorch | 1.15.2 | same (pin kept) |
| linear_operator | 0.6.1 | same (pin kept) |
| numpy / scipy / pandas | 2.2.6 / 1.15.3 / 2.3.3 | same |
| **botorch** | **0.16.1** (PyPI upload 2025-11-21; the newest release for py3.10, well over 2 weeks old) | added |

- **The `--no-deps` install worked with no drift.** botorch 0.16.1 requires
  gpytorch ≥ 1.14.2 and linear_operator ≥ 0.6, so the existing pins
  satisfy it.
- **Added pure-Python dependencies:** pyro-ppl 1.9.1, pyro-api 0.1.2,
  opt_einsum 3.4.0, multipledispatch 1.0.0, pyre-extensions 0.0.32,
  typing-inspect 0.9.0, mypy_extensions 1.1.0, tqdm 4.70.1.
- **`pip freeze` diff vs `bogp`:** additions only, with no version
  changed. Because nothing changed, the PredGP-regrade check is not needed.
- **`pip check`:** the only complaints are the two `dispatches 1.3.dev0`
  lines (idaes-pse / pyomo). `bogp` reports the same two.
- **Import check:** `from botorch.acquisition.multi_objective import
  qNoisyExpectedHypervolumeImprovement` gives OK.
- **Freeze:** `env/bogp-botorch_local_pip_freeze.txt`, sha256
  `78aebde97c9a8670f35aa7b4808ec7636d624f4b26b6d305164fddb5377b0f8d`.

Usage (all prompts): `PYTHONNOUSERSITE=1 OMP_NUM_THREADS=4
/opt/anaconda3/envs/bogp-botorch/bin/python`, with `torch.set_num_threads(4)`.
Do not modify this env; only prompt 35 owns it.

## CRC (pending; Kay runs on bastion) — REQUIRED for N1

**Update 2026-10-12:** N1 runs again (replay gate PASS under the one-sided
amendment), so `BOGP_CRC_botorch` is needed on CRC again. Every N1
acquisition job activates it by name (`arms.json` → `env`). It must exist
and pass `ARM=N1 bash analysis/methods_C/acquire_arm_job.sh --check-env`
BEFORE N1's first acquisition (after N1 r1 lands).

**Update 2026-10-12 evening (strategy session relay): the CRC home quota is
full.**
- `conda create --clone` into `~/.conda/envs` failed with NoSpaceLeftError.
  Never write envs, caches, freezes, logs or data to `~` on CRC; use
  `/groups/adowling/ylu28/...`. Every pip call uses
  `python -m pip install --no-cache-dir`, and every conda call sets
  `CONDA_PKGS_DIRS=/groups/adowling/ylu28/conda_pkgs`.
- **The env lives at `/groups/adowling/ylu28/conda_envs/BOGP_CRC_botorch`**
  (`conda create -p … --clone BOGP_CRC`). That directory is registered in
  `~/.condarc` (`conda config --append envs_dirs
  /groups/adowling/ylu28/conda_envs`), so **`conda activate BOGP_CRC_botorch`
  by name works** on bastion and on compute nodes. `acquire_arm_job.sh`
  therefore needs no change. `BOGP_CRC` and `PCM_ERCOT` stay in
  `~/.conda/envs`, unchanged.
- **Freeze files:** `/groups/adowling/ylu28/BOGP_CRC_botorch_pip_freeze.txt`
  and `/groups/adowling/ylu28/BOGP_CRC_pip_freeze_now.txt` (not `~/…`).
- `qacct` does not work on CRC (no accounting file on bastion). G3 uses job
  logs and commit timestamps instead (PROGRESS.md).

`BOGP_CRC` is py3.11, torch 2.14.1+cpu, gpytorch 1.15.2, linear_operator
0.6.1. Clone it with the same pins and the same botorch version as local.
The strategy session is already running the build; this is the reference
recipe:

```bash
source "$(conda info --base)/etc/profile.d/conda.sh"
export CONDA_PKGS_DIRS=/groups/adowling/ylu28/conda_pkgs PYTHONNOUSERSITE=1
conda create -y -p /groups/adowling/ylu28/conda_envs/BOGP_CRC_botorch --clone BOGP_CRC
conda activate BOGP_CRC_botorch          # by name, via envs_dirs in ~/.condarc
python -m pip install --no-cache-dir --no-deps botorch==0.16.1 pyro-ppl==1.9.1 pyro-api==0.1.2 \
    opt-einsum==3.4.0 multipledispatch==1.0.0 pyre-extensions==0.0.32 typing-inspect==0.9.0 \
    mypy-extensions==1.1.0 tqdm
python -c "import torch, gpytorch, linear_operator, botorch; \
from botorch.acquisition.multi_objective import qNoisyExpectedHypervolumeImprovement; \
print(torch.__version__, gpytorch.__version__, linear_operator.__version__, botorch.__version__)"
python -m pip freeze > /groups/adowling/ylu28/BOGP_CRC_botorch_pip_freeze.txt
conda activate BOGP_CRC; python -m pip freeze > /groups/adowling/ylu28/BOGP_CRC_pip_freeze_now.txt
diff /groups/adowling/ylu28/BOGP_CRC_pip_freeze_now.txt /groups/adowling/ylu28/BOGP_CRC_botorch_pip_freeze.txt
cd /groups/adowling/ylu28/RTS-GMLC/trial_0826/campaign && ARM=N1 bash analysis/methods_C/acquire_arm_job.sh --check-env
```

Kay pastes the import line, the diff and the `--check-env` line when the
build ends. The diff must show additions only, and `BOGP_CRC` must be
unchanged against `analysis/bo_stage2/env/BOGP_CRC_pip_freeze.txt`. The CRC
side is then recorded here.
