"""Prompt 35 §3.2 — qNEHVI acquirer + replay gate (env `bogp-botorch`):
  BOGP_PATH=/Users/yilu/Documents/GitHub/bo-gp-qparego OMP_NUM_THREADS=4 \
  /opt/anaconda3/envs/bogp-botorch/bin/python -m pytest tests/test_methods_qnehvi.py -v
Skipped where botorch is absent."""

import json
import os
import sys

import numpy as np
import pytest

pytest.importorskip("botorch")
if os.environ.get("BOGP_PATH"):
    sys.path.insert(0, os.environ["BOGP_PATH"])
CAMPAIGN = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MC = os.path.join(CAMPAIGN, "analysis", "methods_C")
sys.path.insert(0, MC)
sys.path.insert(0, os.path.join(CAMPAIGN, "analysis", "bo_stage2"))
import acquire_next as an  # noqa: E402
import qnehvi as qn  # noqa: E402
import replay_gate as rg  # noqa: E402


def test_qnehvi_contract_and_determinism():
    X, Y = an.load_training(CAMPAIGN, 0)
    ref = json.load(open(os.path.join(CAMPAIGN, "analysis", "bo_stage2", "ledger.json")))["ref_point"]
    cand = an.lattice_candidates()[np.random.default_rng(3).choice(531441, 400, replace=False)]
    cand = np.vstack([cand, X[:5]])  # evaluated rows must be excluded
    a = qn.propose_qnehvi_batch(X, Y, cand, ref, an.FLOORS, q=8, seed=5, log=lambda *_: None)
    b = qn.propose_qnehvi_batch(X, Y, cand, ref, an.FLOORS, q=8, seed=5, log=lambda *_: None)
    assert a["x_batch"].shape == (8, 6) and np.array_equal(a["cand_idx"], b["cand_idx"])
    assert len(set(a["cand_idx"].tolist())) == 8 and not (set(a["cand_idx"].tolist()) & set(range(400, 405)))
    an.assert_on_lattice(a["x_batch"])


def test_floor_lower_bounds_noise():
    X, Y = an.load_training(CAMPAIGN, 0)
    model, (_, _, _, sy) = qn.fit_model(X, Y, an.FLOORS)
    for j, m in enumerate(model.models):
        assert float(m.likelihood.noise) >= (an.FLOORS[j] / sy[j]) ** 2 * (1 - 1e-9)


def test_replay_gate_protocol_one_seed():
    out = rg.main(seeds=[0], write=False)
    assert len(out["curves_n8_n16_n24"][0]) == 3
    c = out["curves_n8_n16_n24"][0]
    assert c[0] <= c[1] <= c[2] <= 1.0 + 1e-12
    rng = rg.smoke_range()
    assert rng[16][0] == pytest.approx(0.8444332, abs=1e-6) and rng[24][1] == pytest.approx(0.9517745, abs=1e-6)


@pytest.mark.skipif(not os.path.isfile(os.path.join(MC, "replay_gate.json")), reason="gate not run yet")
def test_replay_gate_record():
    g = json.load(open(os.path.join(MC, "replay_gate.json")))
    assert g["seeds"] == list(range(10)) and len(g["curves_n8_n16_n24"]) == 10
    med16 = float(np.median([c[1] for c in g["curves_n8_n16_n24"]]))
    assert med16 == pytest.approx(g["median"]["16"])
    lo, hi = g["qparego_range"]["16"]
    assert g["PASS"] == (lo <= g["median"]["16"] <= hi and
                         g["qparego_range"]["24"][0] <= g["median"]["24"] <= g["qparego_range"]["24"][1])


@pytest.mark.skipif(not os.path.isfile(os.path.join(MC, "replay_gate.json")), reason="gate not run yet")
def test_amended_one_sided_gate():
    g = json.load(open(os.path.join(MC, "replay_gate.json")))
    assert g["PASS"] is False          # original two-sided record kept
    assert rg.amended_pass(g) is True  # AMENDMENT 2026-10-12: >= min at n = 16 and 24
    assert os.path.isfile(os.path.join(MC, "N1", "GATE_PASS_N1.md"))
    assert not os.path.exists(os.path.join(MC, "N1", "NOT_RUN_N1.md"))
