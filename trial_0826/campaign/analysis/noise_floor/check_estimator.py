"""Prompt 40 Part A self-check: the pinned estimator (CH, WLS over the k = 4
smallest populated bins) recovers a KNOWN nugget on the real pooled design
geometry. y = smooth f(x) + N(0, sigma^2), sigma known. Writes nothing."""
import numpy as np

import part_a
import pool

df, _ = pool.load_pool()
vg = part_a.Variogram(df)
Xn = pool.normalized_X(df)
rng = np.random.default_rng(7)
for label, f in {"linear": lambda X: 20000 * X.sum(1),
                 "quadratic": lambda X: 30000 * ((X - 0.5) ** 2).sum(1)}.items():
    for sigma in (300.0, 1000.0, 3000.0):
        est = []
        for _ in range(50):
            y = f(Xn) + rng.normal(0, sigma, len(Xn))
            N, hb, g = vg.point(y)
            est.append(part_a.wls_intercept(N, hb, g))
        est = np.array(est)
        print(f"{label:9s} sigma {sigma:6.0f}: median nugget sd "
              f"{np.sqrt(max(np.median(est), 0)):7.1f}  "
              f"(var ratio median {np.median(est) / sigma ** 2:5.2f}, "
              f"frac<=0 {np.mean(est <= 0):.2f})")
