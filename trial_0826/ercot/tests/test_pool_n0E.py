"""Prompt 62 Part B tests for analysis/pool/pool_n0E.py — SYNTHETIC Y at the real n0_E X.

Run:  cd trial_0826/ercot && /opt/anaconda3/bin/python -m pytest tests/test_pool_n0E.py -q

No n0_E Y is read: `wide` is synthetic (planted answers in units of the real
B_j), N1_off's line_summary reader is synthetic, outputs go to tmp_path.
Real inputs used: the plan amendment (sha256), pool_definitions.json (f76d897),
waves/n0_E/design_matrix.csv (X only), analysis/noise_v3/ercot_noise.json (bars),
the committed wave-D standings csvs (54 rerun).

Planted (base case):
- V1 = -8 z_T - 3 z_s (STRONG response); V2 (max) = 3 V1 -> oriented rank-identical -> REDUNDANT->V1
- E1 = 5 z_T + 4 z_s (size + composition); X1 = 2 E1 -> REDUNDANT->E1 (X family consumes no seat)
- E4, E2 = 6 z_T + independent 0.3 noise -> SIZE-CO-MONOTONE (raw >= 0.90, residual < 0.50)
- V1 vs E4: TRADE-OFF (size)
- R4 = 0.3 chatter -> NOT RESPONDS; R5 = 4 z_T + 0.2 noise -> R seat
- N1 = 5 z_s + 2 z_T; N4 = 0.3 N1 -> REDUNDANT->N1 (N priority keeps the noisier N1)
- E6 = 6 B unstructured noise -> IDR large but Mantel fails -> NOT RESPONDS
- E5, E9, R1, R3 constant 0 -> DEAD
Seats V1 / E1 / R5 / N1, M = 4.
"""
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ERCOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ERCOT))
sys.path.insert(0, str(ERCOT / "analysis" / "pool"))
import pool_objectives as po  # noqa: E402
import pool_n0E as pn  # noqa: E402

SRC = (ERCOT / "analysis" / "pool" / "pool_n0E.py").read_text()


@pytest.fixture(scope="module")
def X():
    return pn.load_X()


@pytest.fixture(scope="module")
def B():
    return pn.bars(ids=list(po.CAND_IDS))


def _z(v):
    v = np.asarray(v, float)
    return (v - v.mean()) / v.std()


def synth(X, B, variant="base", seed=62):
    rng = np.random.default_rng(seed)
    zT = _z(X["T"])
    zs = _z(X["s"] - pn.bin_pchip(X["T"], X["s"]))
    n = len(X)
    b = B["B_j"]
    noise = lambda k=1.0: k * rng.standard_normal(n)  # noqa: E731
    Y = {c: b[c] * noise(6.0) + 1e6 for c in po.CAND_IDS}
    Y["V1"] = b["V1"] * (-8 * zT - 3 * zs) + 4e6
    Y["V2"] = -3 * Y["V1"] / 1e6
    Y["E1"] = b["E1"] * (5 * zT + 4 * zs) + 8e9
    Y["X1"] = 2 * Y["E1"]
    Y["E4"] = b["E4"] * (6 * zT + noise(0.3))
    Y["E2"] = b["E2"] * (6 * zT + noise(0.3))
    Y["R4"] = b["R4"] * noise(0.3) + 15000
    Y["R5"] = b["R5"] * (4 * zT + noise(0.2))
    Y["N1"] = np.round(b["N1"] * (5 * zs + 2 * zT)) + 36000
    Y["N4"] = 0.3 * Y["N1"]
    for c in ("E5", "E9", "R1", "R3"):
        Y[c] = np.zeros(n)
    if variant == "e_fails":       # E-seat clause: E1 chatter -> HALT FOR PI, never E3/E4
        Y["E1"] = b["E1"] * noise(0.2) + 8e9
        Y["X1"] = 2 * Y["E1"]
        Y["E4"] = b["E4"] * (6 * zs + noise(0.2))     # a strong E responder that must NOT take the seat
    if variant == "r_empty":       # M < 4: R family has no responder, X1 independent -> X seats, N not filled
        for c in ("R4", "R5", "R6", "R8"):
            Y[c] = b[c] * noise(0.3) + 1e5
        Y["X1"] = b["X1"] * (7 * zs - 2 * zT) + 2e8
    w = pd.DataFrame(Y)
    w.insert(0, "index", X.index.to_numpy())
    w.insert(0, "key", [f"n0_E:{i}" for i in X.index])
    w["suspect"] = False
    w["G_run_usd"] = 1.5e6
    for c in pn.D3_COLS:
        w[c] = 0.0
    return w.sample(frac=1.0, random_state=1).reset_index(drop=True)   # row order must not matter


def reader_for(wide):
    pl = po.pocket_lines()
    by = {k: (n1, n4) for k, n1, n4 in zip(wide["key"], wide["N1"], wide["N4"])}

    def read(key):
        n1, n4 = by[key]
        return pd.DataFrame({"Line": [pl[0], "LX_off"], "hours_ge_99pct": [n4, n1 - n4]})
    return read


def _run(X, B, tmp_path, variant="base", figs=False):
    w = synth(X, B, variant)
    return pn.run(wide=w, out_dir=str(tmp_path), figs_dir=str(tmp_path / "figs"),
                  line_reader=reader_for(w), make_figs=figs, verbose=False, synthetic=True)


# --------------------------------------------------------------------------- guards
def test_amendment_and_freeze_asserted():
    assert pn.assert_amendment() == pn.AMEND_SHA256
    blk = pn.amendment_block()
    assert "RESPONDS IN BOX" in blk and "HALT FOR PI" in blk and blk.rstrip().endswith("is a recorded rule change.")
    bad = blk.replace("0.90", "0.85", 1)
    assert pn.hashlib.sha256(bad.encode()).hexdigest() != pn.AMEND_SHA256


def test_no_random_E_no_gp_loader():
    import ast
    tree = ast.parse(SRC)
    mods = {a.name for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names}
    mods |= {n.module for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)}
    assert not mods & {"land_ercot_n0", "ercot_gp_loader"}
    names = {n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)}
    assert "land_ercot_n0" not in names and "ercot_gp_loader" not in names
    for n in ast.walk(tree):            # "random_E" may appear only in a statement that it is not read
        if isinstance(n, ast.Constant) and isinstance(n.value, str) and "random_E" in n.value:
            assert any(w in n.value for w in ("not read", "Never reads", "unread")), n.value[:80]
    assert "build_wave(wave=WAVE" in SRC and pn.WAVE == "n0_E"


def test_X_and_design_sha(X):
    assert len(X) == 48 and 678 < X["T"].min() < 679 and 1862 < X["T"].max() < 1863
    assert abs(pn._spearman(X["T"], X["s"]) - 0.39) < 0.01
    assert len(X.attrs["design_sha256"]) == 64


def test_bars_D2_excluded(B):
    assert set(B.index[B["B_j"] == 0]) == pn.ZERO_BAR_EXPECTED
    assert B.loc[B["B_j"] > 0, "n_delta"].to_dict() == {c: (4 if c in ("D1", "D2") else 6) for c in B.index[B["B_j"] > 0]}  # D1/D2: nuclear design NaN
    assert B.loc["V1", "B_j"] == pytest.approx(16173.06, rel=1e-5)
    assert B.loc["E1", "B_j"] == pytest.approx(2.38324e6, rel=1e-5)
    assert B.loc["N2", "B_j"] == 3.0 and B.loc["N2", "in_ruler_zero"]
    assert [e["key"] for e in B.attrs["excluded"]] == ["noise_v3/A:6", "noise_v3/B:6"]


# --------------------------------------------------------------------------- statistics
def test_mantel_detects_structure_not_noise(X):
    U = X[X.attrs["u_cols"]].to_numpy(dtype=float)
    r, p = pn.mantel(X["T"].to_numpy(), U, n_perm=999)
    assert r > 0 and p <= 0.01
    r2, p2 = pn.mantel(np.random.default_rng(3).standard_normal(48), U, n_perm=999)
    assert p2 > 0.01
    assert pn.mantel(X["T"].to_numpy(), U, n_perm=999) == (r, p)      # fresh rng per call


def test_size_share_and_iso(X):
    T = X["T"].to_numpy()
    eta, adj = pn.size_share(T, 3 * T + 1)
    assert eta > 0.95 and adj == pytest.approx((eta - 0.107) / 0.893)
    assert pn.iso_loo_r2(T, -T) > 0.95
    noise = np.random.default_rng(5).standard_normal(48)
    assert pn.iso_loo_r2(T, noise) < 0.3


def test_border_band():
    lo, hi = pn.border_band()
    assert 0.83 < lo < 0.87 and 0.92 < hi < 0.95
    assert pn.fisher_ci(0.9, 48, 0.90)[0] == pytest.approx(lo)


# --------------------------------------------------------------------------- end to end
def test_base_case(X, B, tmp_path):
    out = _run(X, B, tmp_path, figs=True)
    t = out["tab"]
    assert t.loc["V1", "respond_label"].startswith("RESPONDS IN BOX (STRONG)")
    assert not t.loc["R4", "responds"] and not t.loc["E6", "responds"] and t.loc["E6", "IDR_over_B"] > 2
    assert t.loc["V2", "status"] == "REDUNDANT->V1" and t.loc["X1", "status"] == "REDUNDANT->E1"
    assert t.loc["N4", "status"] == "REDUNDANT->N1"
    assert t.loc["E4", "status"].startswith("SIZE-CO-MONOTONE") or t.loc["E2", "status"].startswith("SIZE-CO-MONOTONE")
    for c in ("E5", "E9", "R1", "R3"):
        assert t.loc[c, "status"] == "DEAD"
    assert t.loc["R2", "status"] == "GUARDRAIL"
    p = out["pairs"].set_index("pair")
    assert p.loc["V1|E4", "tradeoff_size"]
    assert [s["seat"] for s in out["seats"]] == ["V1", "E1", "R5", "N1"] and out["M"] == 4
    for f in ("POOL_N0E_STANDINGS.md", "pool_n0E_standings.csv", "pool_spearman_n0E_raw.csv",
              "pool_spearman_n0E_resid.csv", "pool_ed1b_combined.csv"):
        assert (tmp_path / f).is_file()
    for f in ("n0E_clustermap_raw.png", "n0E_clustermap_resid.png", "n0E_idr_over_B.png"):
        assert (tmp_path / "figs" / f).is_file()
    md = (tmp_path / "POOL_N0E_STANDINGS.md").read_text()
    assert "## E. E-D1b decision table" in md and "N1-N4 REDUNDANT" in md and pn.AMEND_SHA256 in md
    comb = pd.read_csv(tmp_path / "pool_ed1b_combined.csv")
    assert list(comb["id"])[:5] == ["V1", "E1", "X1", "R4", "N1"]


def test_E_seat_halts_never_passes(X, B, tmp_path):
    out = _run(X, B, tmp_path, "e_fails")
    seats = {s["family"]: s["seat"] for s in out["seats"]}
    assert seats["E"] == "HALT FOR PI"
    assert out["tab"].loc["E4", "responds"] and "E4" not in seats.values()
    assert out["M"] == 3
    assert out["tab"].loc["E1", "status"].startswith("HALT FOR PI")
    assert "never passed to E3/E4" in out["tab"].loc["E1", "reason"]


def test_empty_family_not_refilled(X, B, tmp_path):
    out = _run(X, B, tmp_path, "r_empty")
    seats = [(s["family"], s["seat"]) for s in out["seats"]]
    assert seats == [("V", "V1"), ("E", "E1"), ("X", "X1"), ("R", "EMPTY")]
    assert out["tab"].loc["N1", "responds"] and out["M"] == 3


def test_outputs_never_overwrite_57():
    assert "pool_ed1b_decision.csv" not in SRC and "ERCOT_POOL_STANDINGS.md" not in SRC
    assert "to_csv(os.path.join(out_dir, \"pool_standings" not in SRC
    assert '"figs", "n0E"' in SRC


def test_synthetic_guards(X, B, tmp_path):
    w = synth(X, B)
    with pytest.raises(AssertionError, match="REFUSED: synthetic output under analysis/pool"):
        pn.run(wide=w, out_dir=os.path.join(po.POOL, "x"), make_figs=False, verbose=False, synthetic=True)
    with pytest.raises(AssertionError, match="REFUSED: an injected wide is synthetic"):
        pn.run(wide=w, out_dir=str(tmp_path), make_figs=False, verbose=False)
    out = pn.run(out_dir=str(tmp_path / "planted"), figs_dir=str(tmp_path / "planted" / "figs"),
                 make_figs=False, verbose=False, synthetic=True)     # built-in planted Y
    assert out["info"]["landing"] == {"skipped": "synthetic run"}
    assert "SYNTHETIC DRY RUN" in (tmp_path / "planted" / "POOL_N0E_STANDINGS.md").read_text()
    assert not any(os.path.getmtime(os.path.join(po.POOL, f)) > os.path.getmtime(tmp_path / "planted")
                   for f in os.listdir(po.POOL) if f.startswith(("pool_n0E", "POOL_N0E", "pool_ed1b_combined")))


def test_combined_table_columns(X, B, tmp_path):
    out = _run(X, B, tmp_path)
    t, comb = out["tab"], out["comb"]
    for c in ("E5", "R1", "R3"):
        assert t.loc[c, "waveD_B_readable"] is False or t.loc[c, "waveD_B_readable"] == False  # noqa: E712
    assert {"waveD_cost_gap_read", "n0E_cost_gap_read", "reason"} <= set(comb.columns)
    for c in ("E1", "E2", "E3"):
        assert comb.loc[c, "n0E_cost_gap_read"].startswith("IDR ")
    assert comb["reason"].fillna("").ne("").sum() >= len(t) - 1
    assert comb.loc["R4", "reason"].startswith("NOT RESPONDS")
    assert comb.loc["X1", "reason"].startswith("REDUNDANT->E1")
    assert comb.loc["E4", "reason"] in ("E seat is E1 only (plan §1.2 final)",) or "REDUNDANT" in comb.loc["E4", "reason"]


def test_amendment_cited_by_log_S():
    sha = pn.amendment_commit()
    msg = pn.subprocess.run(["git", "-C", pn.ERCOT, "log", "-1", "--format=%s", sha],
                            capture_output=True, text=True).stdout
    assert msg.startswith("plan(62 pre-registration)")


def test_landing_crosscheck(X, B, tmp_path):
    w = synth(X, B)
    lr = pd.DataFrame({"key": w["key"], "wave": "n0_E", "index": w["index"], "suspect": False,
                       "G_run_usd": w["G_run_usd"], "R1_shed_mwh": w["R1"], "R2_reserve_shortfall_mwh": w["R2"]})
    other = lr.assign(wave="random_E", R2_reserve_shortfall_mwh=-1.0)
    p = tmp_path / "landing_rows.csv"
    pd.concat([lr, other]).to_csv(p, index=False)
    assert pn.landing_crosscheck(w, p)["rows"] == 48
    lr.assign(R2_reserve_shortfall_mwh=lr["R2_reserve_shortfall_mwh"] + 1).to_csv(p, index=False)
    with pytest.raises(AssertionError):
        pn.landing_crosscheck(w, p)
