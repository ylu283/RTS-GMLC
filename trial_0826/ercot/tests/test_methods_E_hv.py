"""Prompt 55 tests — exact hypervolume (common_E.hv_exact -> bogp.mobo.pareto.hypervolume_exact).

Run:  cd trial_0826/ercot && /opt/anaconda3/envs/bogp-botorch/bin/python -m pytest tests/test_methods_E_hv.py -q

The M = 4 three-point toy equals 86.0 and botorch's Hypervolume; M = 2/3 random
sets agree with botorch; the Monte-Carlo `pareto.hypervolume` is never imported.
"""
import sys
from pathlib import Path

import numpy as np
import pytest

ERCOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ERCOT / "analysis" / "methods_E"))
import common_E  # noqa: E402  (pins the bo-gp-qparego worktree BEFORE any bogp import)
pytest.importorskip("bogp")
torch = pytest.importorskip("torch")

TOY86 = np.array([[1.0, 2.0, 4.0, 0.0], [1.0, 4.0, 3.0, 0.0], [0.0, 3.0, 4.0, 2.0]])
REF4 = np.array([5.0, 5.0, 5.0, 5.0])


def _botorch_hv(Y, ref):
    from botorch.utils.multi_objective.hypervolume import Hypervolume
    return float(Hypervolume(ref_point=torch.tensor(-ref, dtype=torch.float64)).compute(torch.tensor(-Y, dtype=torch.float64)))


def test_m4_three_point_toy_is_86_and_matches_botorch():
    assert common_E.hv_exact(TOY86, REF4) == 86.0
    assert _botorch_hv(TOY86, REF4) == pytest.approx(86.0)


@pytest.mark.parametrize("M,n", [(2, 15), (3, 25), (4, 20)])
def test_random_sets_match_botorch(M, n):
    rng = np.random.default_rng(M * 11 + n)
    Y = rng.uniform(size=(n, M)) * np.array([1e5, 1e9, 1e4, 1e3][:M])
    ref = Y.max(0) + 0.1 * (Y.max(0) - Y.min(0))
    assert common_E.hv_exact(Y, ref) == pytest.approx(_botorch_hv(Y, ref), rel=1e-10)


def test_dominated_duplicates_and_outside_ref_contribute_nothing():
    Y = np.vstack([TOY86, TOY86[0], [4.9, 4.9, 4.9, 4.9], [6.0, 0.0, 0.0, 0.0]])
    assert common_E.hv_exact(Y, REF4) == 86.0
    assert common_E.hv_exact(np.zeros((0, 4)), REF4) == 0.0


def test_only_the_exact_routine_is_imported():
    import inspect
    src = inspect.getsource(common_E)
    assert "hypervolume_exact" in src and "import hypervolume\n" not in src and "pareto.hypervolume(" not in src
    assert common_E.hv_exact(TOY86, REF4) == 86.0 and common_E.hypervolume_exact.__name__ == "hypervolume_exact"
