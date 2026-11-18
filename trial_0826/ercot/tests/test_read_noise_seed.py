"""Prompt 63 Part C tests for analysis/noise_v3/read_noise_seed.py.

Run:  cd trial_0826/ercot && /opt/anaconda3/envs/bogp-botorch/bin/python -m pytest tests/test_read_noise_seed.py -q
"""
import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ERCOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ERCOT / "analysis" / "methods_E"))
sys.path.insert(0, str(ERCOT / "analysis" / "noise_v3"))
import common_E  # noqa: E402,F401  (pins bo-gp-qparego)
import read_noise_seed as rs  # noqa: E402

OUT = ERCOT / "analysis" / "noise_v3"


def _D(vals):
    """vals: 4 x 5 values of one candidate 'Q' -> designs() structure."""
    return [(f"n0_E:{k}", f"q{k}", float(100 * k), [{"Q": v, "key": f"x{k}_{s}"} for s, v in enumerate(row)])
            for k, row in zip((1, 2, 3, 4), vals)]


def test_candidate_stats_known_answers():
    rng = np.random.default_rng(1)
    vals = rng.normal(size=(4, 5)) * 10 + 100
    noise = {"per_candidate": {"Q": {"bar": {"sigma_hat": 10.0 * math.sqrt(2), "B": 50.0, "n": 6}}}}
    cs = rs.candidate_stats(_D(vals), ["Q"], noise)["Q"]
    sds = [np.std(v, ddof=1) for v in vals]
    assert cs["sd_by_design"] == pytest.approx(sds) and cs["df"] == 16
    assert cs["sigma_c"] == pytest.approx(np.sqrt(np.mean(np.square(sds))))
    d = (vals[:, 1:] - vals[:, [0]]).ravel()
    assert cs["max_abs_delta_seed"] == pytest.approx(np.abs(d).max())
    assert cs["B_seed"] == pytest.approx(max(3 * cs["sigma_c"] * math.sqrt(2), np.abs(d).max()))
    r = cs["sigma_c"] * math.sqrt(2) / (10.0 * math.sqrt(2))
    assert cs["ratio_seed_over_pert"] == pytest.approx(r)
    assert cs["A3"] == ("AGREE" if 0.5 <= r <= 2 else "DISAGREE")


def test_a3_rule_edges():
    base = np.array([[0, 1, -1, 1, -1]] * 4, float)              # sd = 1 per design
    s = np.std(base[0], ddof=1)
    for sp, want in ((s * math.sqrt(2) / 2.0, "AGREE"), (s * math.sqrt(2) / 2.01, "DISAGREE"),
                     (s * math.sqrt(2) * 2.0, "AGREE"), (s * math.sqrt(2) * 2.01, "DISAGREE"), (0.0, "DISAGREE (one ruler is 0)")):
        cs = rs.candidate_stats(_D(base), ["Q"], {"per_candidate": {"Q": {"bar": {"sigma_hat": sp, "B": 1.0}}}})["Q"]
        assert cs["A3"] == want, (sp, cs["A3"])
    z = rs.candidate_stats(_D(np.zeros((4, 5))), ["Q"], {"per_candidate": {"Q": {"bar": {"sigma_hat": 0.0, "B": 0.0}}}})["Q"]
    assert z["A3"].startswith("AGREE (both") and z["sigma_c"] == 0.0 and z["B_seed"] == 0.0


def test_committed_outputs_consistent():
    p = OUT / "ercot_noise_seed.json"
    if not p.is_file():
        pytest.skip("Part C not landed")
    js = json.loads(p.read_text())
    df = pd.read_csv(OUT / "ercot_noise_seed.csv")
    assert len(df) == 28 and js["anchors"] == ["n0_E:25", "n0_E:29", "n0_E:46", "n0_E:4"]
    nj = json.loads((OUT / "ercot_noise.json").read_text())
    for c in ("V1", "E1", "R4", "N1", "N4"):
        p_ = js["per_candidate"][c]
        assert p_["df"] == 16 and p_["B_pert"] == pytest.approx(nj["per_candidate"][c]["bar"]["B"])
        assert p_["B_seed"] == pytest.approx(max(3 * p_["sigma_c"] * math.sqrt(2), p_["max_abs_delta_seed"]))
        assert float(df.loc[df["id"] == c, "sigma_c"].iloc[0]) == pytest.approx(p_["sigma_c"])
    Sc = pd.read_csv(OUT / "ercot_noise_seed_sigma_c.csv", index_col=0)
    assert np.allclose(Sc.to_numpy(), Sc.to_numpy().T) and np.linalg.eigvalsh(Sc.to_numpy()).min() > -1e-6 * np.abs(Sc.to_numpy()).max()
    assert js["tau_res"]["status"].startswith("PROVISIONAL") and js["tau_res"]["tau_exact"] == 0.0
    assert {t["threads"] for t in js["thread_check"]} == {8, 1}
    # every run's key is the wave or one of the 4 anchors (blind discipline)
    assert all(r["key"].startswith("noise_seed_E:") or r["key"] in js["anchors"] for r in js["runs"])
