"""Prompt 42 convergence check (training data only, no holdout): learned shed
noise and loss slope at the house 700 Adam steps vs 5,000 steps, n0 = 32.
bogp.train_gp is swapped inside this process only and restored."""
import math
import os
import sys

import torch

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "initial_design"))
import common  # noqa: E402

X, Y = common.arm_data(32)
y = Y[:, common.M_COLS.index("load_shed_mwh")]
orig = common.train_gp
try:
    for cfg in [("m52", "std", "inferred", "none"), ("rbf", "log1p", "inferred", "none")]:
        for f in (180.0, 306.0, 880.0, 3000.0):
            cells = []
            for ep in (700, 5000):
                losses = []

                def tg(m, lik, x, yy, n_epochs=700, lr=0.01, _ep=ep):
                    r = orig(m, lik, x, yy, n_epochs=_ep, lr=lr)
                    losses.extend(r)
                    return r
                common.train_gp = tg
                torch.manual_seed(0)
                gp = common.FlexGP(X, y, f, cfg)
                sc = gp.sy * ((1 + gp.y_med) if cfg[1] == "log1p" else 1)
                cells.append(f"ep{ep}: noise {math.sqrt(float(gp.lik.noise)) * sc:7.1f} "
                             f"dloss100 {losses[-101] - losses[-1]:.2e}")
            print(f"{cfg[0]}+{cfg[1]} f={f:5.0f} | " + " | ".join(cells))
finally:
    common.train_gp = orig
