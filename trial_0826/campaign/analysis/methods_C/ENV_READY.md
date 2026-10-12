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

## CRC (pending; Kay runs on bastion)

`BOGP_CRC` is py3.11, torch 2.14.1+cpu, gpytorch 1.15.2, linear_operator
0.6.1. Clone it with the same pins and the same botorch version as local:

```bash
source "$(conda info --base)/etc/profile.d/conda.sh"
conda create -y -n BOGP_CRC_botorch --clone BOGP_CRC
conda activate BOGP_CRC_botorch
export PYTHONNOUSERSITE=1
pip install --no-deps botorch==0.16.1 pyro-ppl==1.9.1 pyro-api==0.1.2 opt-einsum==3.4.0 \
    multipledispatch==1.0.0 pyre-extensions==0.0.32 typing-inspect==0.9.0 mypy-extensions==1.1.0 tqdm
python -c "import torch, gpytorch, linear_operator, botorch; \
from botorch.acquisition.multi_objective import qNoisyExpectedHypervolumeImprovement; \
print(torch.__version__, gpytorch.__version__, linear_operator.__version__, botorch.__version__)"
pip freeze > ~/BOGP_CRC_botorch_pip_freeze.txt; conda activate BOGP_CRC; pip freeze > ~/BOGP_CRC_pip_freeze_now.txt
diff ~/BOGP_CRC_pip_freeze_now.txt ~/BOGP_CRC_botorch_pip_freeze.txt
```

Kay pastes the import line and the diff. The diff must show additions
only, and `BOGP_CRC` must be unchanged against
`analysis/bo_stage2/env/BOGP_CRC_pip_freeze.txt`. The CRC side is then
recorded here.
