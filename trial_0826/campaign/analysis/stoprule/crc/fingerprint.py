"""Cross-platform check (Mac vs CRC): start sets, 2-D starts, noise draws and
one candidate subset must be identical so that replay M1/M4 (Mac) and
everything on CRC share common random numbers. Prints one sha256 per item."""
import hashlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import numpy as np
import runner
from problems import Problem


def h(a):
    return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()[:16]


print("starts6d", h(np.stack([runner.sobol_starts_6d(s) for s in range(50)])))
print("starts2d", h(np.stack([runner.random_starts_2d(s) for s in range(20)])))
p = Problem("E-path-1")
print("noise", h(p.evaluate(np.arange(0, 531441, 997), 3)))
ev = runner.sobol_starts_6d(0)
print("cand", h(runner.candidate_set(p, "subset", ev, p.evaluate(ev, 0), 0, 1)))
print("truth", p.meta["truth_sha256"][:16])
