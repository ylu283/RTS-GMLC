"""Prompt 65 v1.1 tests for analysis/pool/pool_n0E_v2.py — SYNTHETIC Y at the real n0_E X (no n0_E Y is read).

Run:  cd trial_0826/ercot && /opt/anaconda3/bin/python -m pytest tests/test_pool_n0E_v2.py -q

Real inputs: the plan (AMENDMENT 2026-11-24 sha256 + the 2026-11-17 block), pool_definitions.json (f76d897),
waves/n0_E/design_matrix.csv (X only), the two noise jsons (real bars), extracts/base_v3 (floors),
noise_v3 / noise_seed_E line_summary (N3_off bar), the committed v1 / seedbar csvs (seat lines).
Outputs go to tmp_path. Synthetic Y planted in units of the pooled B_j (§8.13 scenarios):

| scenario | planted | hand-built seats |
|---|---|---|
| additive | V1 = -size - comp_s; E1 = +size + comp_w; N4 = +size + comp_q; X1 = E1/10 | V1 · E1 · N4 (X1 suppressed by E1) |
| total_only | every id = f(T) + chatter | V1 · E1, N EMPTY (N4 REDUNDANT given V1) |
| one_proxy | V2 = rank copy of V1, strongest | V1 · E1 · N4; V2 never seated |
| size_copy | N4 = V1 copy + chatter (the N1 loophole) | V1 · E1, N4 REDUNDANT given V1 |
| asymmetric | V1 pure size; N4 = size + ~5 B composition | ESCAPE -> V1 · E1 · N4 |
| borderline_tradeoff | N4|V1 residual CI straddles 0.50; N4 trades off with E1 | §4b resolves -> V1 · E1 · N4; no-§4b -> N EMPTY |
| borderline_no_tradeoff | same, no differential trade-off | REDUNDANT -> N EMPTY |
| binding_floor | X1 resolvable, IDR < 0.1 % base CO2 | X1 not seatable (materiality) |
| noise_E1 | E1 pure chatter | E: HALT FOR PI |
| strong_proxy | E4 (TRANSFER) and V2 (PROXY) strongest | never seated |
| conflict_demotion | N4 pure composition, no trade-off with V1 / E1 | N4 DEMOTED, N EMPTY |
plus the bar-scale unit test and row-shuffle invariance.
"""
import ast
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
import pool_n0E_v2 as p2  # noqa: E402

SRC = (ERCOT / "analysis" / "pool" / "pool_n0E_v2.py").read_text()
SUB = {"V1", "E1", "X1", "N4", "N1", "V2", "E4"}


@pytest.fixture(scope="module")
def X():
    return p2.pn.load_X()


@pytest.fixture(scope="module")
def B():
    return p2.pooled_bars()


def _run(sc, X, B, wide=None, **kw):
    w = p2.synthetic_wide(sc, X, B) if wide is None else wide
    kw.setdefault("write", False)
    return p2.run(wide=w, synthetic=True, verbose=False, line_reader=p2.synthetic_reader(w), stat_ids=SUB,
                  n_boot_delta=50, X=X, B=B, **kw)


@pytest.fixture(scope="module")
def runs(X, B):
    return {sc: _run(sc, X, B) for sc in p2.SCENARIOS}


def _seats(res):
    return {s["family"]: s["seat"] for s in res["seats"]}


# --------------------------------------------------------------------------- guards
def test_amendment_sha_parametrized_and_v1_block(tmp_path):
    assert p2.assert_amendment() == p2.AMEND_SHA256
    assert p2.amendment_sha(title=p2.AMEND_TITLE) == p2.AMEND_SHA256
    blk = p2.amendment_block()
    assert "Rule v2 (verbatim, memo §3 items 0–10)" in blk and "**§4b borderline resolution" in blk
    assert "FLAGGED-pair" in blk and "R4 | PROXY(E2 start-up cost)" in blk and "X1 0.1 % of base CO₂" in blk
    bad = tmp_path / "plan.md"
    bad.write_text(open(p2.PLAN, encoding="utf-8").read().replace("Steiger's Z", "Steigers Z"), encoding="utf-8")
    with pytest.raises(AssertionError, match="sha256"):
        p2.assert_amendment(str(bad))
    with pytest.raises(AssertionError, match="exactly one block"):
        p2.amendment_block(title="## AMENDMENT 2099-01-01 — none")


def test_no_random_E_no_gp_loader_build_wave_only():
    tree = ast.parse(SRC)
    mods = {a.name for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names}
    mods |= {n.module for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)}
    assert not mods & {"land_ercot_n0", "ercot_gp_loader"}
    names = {n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)}
    assert not names & {"land_ercot_n0", "ercot_gp_loader", "build_pool"}
    for n in ast.walk(tree):
        if isinstance(n, ast.Constant) and isinstance(n.value, str) and "random_E" in n.value:
            assert any(w in n.value for w in ("not read", "Never reads", "unread")), n.value[:80]
    assert "pn.load_wide()" in SRC and "build_wave(wave=WAVE" in (ERCOT / "analysis" / "pool" / "pool_n0E.py").read_text()
    assert "extracts/n0_E" not in SRC and '"n0_E", "run_index' not in SRC
    assert "ZERO_BAR_EXPECTED" not in SRC


def test_gp_config_refusal(tmp_path):
    p2.assert_no_gp()
    f = tmp_path / "committed_configs.json"
    f.write_text("{}")
    with pytest.raises(AssertionError, match="REFUSED"):
        p2.assert_no_gp(str(f))


def test_roles_from_committed_table():
    r = p2.roles()
    assert sorted(c for c, v in r.items() if p2.seatable_role(v["role_base"])) == ["E1", "N4", "V1", "X1"]
    assert r["R4"]["role"] == "PROXY(E2 start-up cost)" and r["N5"]["role_base"] == "DIAGNOSTIC"
    assert r["E9"]["role"] == "DIAGNOSTIC (dead)" and r["E5"]["role_base"] == "OUTCOME (dead)"
    assert "no upgrade-deferral claim" in r["N4"]["role_reason"]


# --------------------------------------------------------------------------- bar (§8.1, bar-scale unit test)
def test_bar_scale_unit():
    rng = np.random.default_rng(0)
    pert = [np.array([0.0, 1.0, -2.0]), np.array([0.0, 3.0, 1.0]), np.array([0.0, -1.0, 0.5])]
    seed = [rng.normal(0, 2, 5) for _ in range(4)]
    b = p2.bar_from_sources(pert, seed, np.concatenate([v[1:] - v[0] for v in seed]))
    s2p = sum(((v - v.mean()) ** 2).sum() for v in pert) / 6
    s2s = np.mean([np.var(v, ddof=1) for v in seed])
    s = np.sqrt((6 * s2p + 16 * s2s) / 22)
    assert b["nu"] == 22 and b["nu_pert"] == 6 and b["nu_seed"] == 16 and abs(b["s_j"] - s) < 1e-12
    assert abs(b["B_j"] - max(3 * np.sqrt(2) * s, b["max_abs_delta"])) < 1e-12
    assert abs(b["chi_lo"] - 0.805) < 0.001 and abs(b["chi_hi"] - 1.335) < 0.001
    big = p2.bar_from_sources([np.array([0.0, 100.0, 0.0])], seed, np.array([]))
    assert big["B_j"] == 100.0 and big["B_binding_term"] == "max|delta|"


def test_pooled_bars_real(B):
    assert (B.loc[[c for c in B.index if c not in ("D1", "D2")], "nu"] == 22).all()
    assert (B.loc[["D1", "D2"], "nu_pert"] == 4).all()
    assert set(B.index[B["B_j"] == 0]) == {"E5", "R1", "R3"} and B.loc["E9", "B_j"] > 0
    assert "E9" in set(B.index[B["sources_disagree_2x"]])             # one source exactly 0
    assert 1.8 < B.loc["N1", "sources_ratio"] < 2.2 and B.loc["N1", "A3_63"] == "DISAGREE"
    n1 = B.loc["N1"]
    assert abs(n1["s_seed"] - 57.0596) < 1e-3 and n1["max_abs_delta"] == 177.0
    assert abs(n1["B_up"] / (3 * np.sqrt(2) * n1["s_j"]) - 1.335) < 0.001
    assert (B["B_lo"] <= B["B_j"]).all() and (B["B_j"] <= B["B_up"]).all()


def test_n1off_and_n3off_bars():
    b1 = p2.n1off_bar()
    assert b1["nu"] == 22 and 150 < b1["B_j"] < 500
    for k, v in b1["seed_runs"].items():                     # json N1 - N4 == line_summary non-pocket sum
        if k.startswith("noise_seed_E"):
            assert p2._offsum(p2._ls(k), "hours_ge_99pct") == v, k
    b3 = p2.n3off_bar()
    assert b3["nu"] == 18 and b3["seed_source"].startswith("4 Seeds only") and b3["B_j"] > 0


def test_floors_offer_base():
    base = p2.base_row()
    fl, info = p2.floors(base)
    assert abs(fl["V1"] - 58287.26) < 0.01 and abs(fl["E1"] - 8.0614e6) < 1e3 and abs(fl["X1"] - 194520.6) < 0.1
    assert fl["N4"] == pytest.approx(87.6) and list(info.values()) == [pytest.approx(154.09)]
    assert p2._offsum(pd.read_csv(os.path.join(p2.BASE_DIR, "line_summary.csv")), "hours_ge_99pct") == p2.BASE_N1OFF
    assert p2._offsum(pd.read_csv(os.path.join(p2.BASE_DIR, "line_summary.csv")), "sum_violation") == pytest.approx(p2.BASE_N3OFF)
    out = p2.assert_offer_excluded([("base_v3:1", p2.BASE_DIR), ("noise_seed_E:1", po.run_dir("noise_seed_E:1"))])
    assert out[1]["n_pem_twins"] > 0


def test_offer_tamper(tmp_path):
    src = Path(po.run_dir("noise_seed_E:1"))
    (tmp_path / "overall.csv").write_text((src / "overall.csv").read_text())
    g = pd.read_csv(src / "gen_summary.csv")
    g.loc[g["is_pem"].astype("boolean").fillna(False).astype(bool), "Unit Cost"] = 40.0
    g.to_csv(tmp_path / "gen_summary.csv", index=False)
    with pytest.raises(AssertionError):
        p2.assert_offer_excluded([("bad", str(tmp_path))])


# --------------------------------------------------------------------------- pair rules + Steiger
def _pair(r, e, cc=True, cp=True):
    ids = ["P", "C"]
    raw = pd.DataFrame([[1, r], [r, 1]], index=ids, columns=ids, dtype=float)
    res = pd.DataFrame([[1, e], [e, 1]], index=ids, columns=ids, dtype=float)
    O = pd.DataFrame({"P": np.arange(48.0), "C": np.arange(48.0)})
    defs = {"candidates": {"P": {"dir": "min"}, "C": {"dir": "max"}}}
    return p2.pair_table(raw, res, O, O, ids, defs, {"C": cc, "P": cp}).iloc[0]


def test_pair_rules():
    assert _pair(0.97, 0.10)["SIZE_CO_MONOTONE"]
    assert _pair(0.97, 0.10, cc=False)["REDUNDANT_given_p"]            # the N1 loophole closed
    assert _pair(0.97, 0.90, cp=False)["ESCAPE"]                        # partner not composition-resolvable
    r = _pair(0.97, 0.42)
    assert r["BORDERLINE_PAIR"] and r["REDUNDANT_given_p"] and r["rho_resid_lo90"] < 0.5 < r["rho_resid_hi90"]
    assert _pair(0.88, 0.95)["raw_ge_090"]                              # raw CI contains 0.90
    assert not _pair(0.80, 0.95)["REDUNDANT_given_p"]
    assert _pair(-0.6, 0.0)["TRADE_OFF_size"] and _pair(0.2, -0.6)["TRADE_OFF_comp"]
    assert not _pair(0.2, -0.6, cc=False)["TRADE_OFF"]
    lo, hi = p2.fisher90(0.42, p2.SE_RESID)
    assert abs(p2.SE_RESID - 0.1649) < 1e-3 and lo < 0.5 < hi


def test_steiger():
    Z, p = p2.steiger(-0.8, 0.0, 0.4)
    assert Z < 0 and p < 0.001
    Z, p = p2.steiger(0.3, 0.3, 0.5)
    assert abs(Z) < 1e-12 and abs(p - 0.5) < 1e-12


def test_delta_error():
    rng = np.random.default_rng(1)
    Yt = pd.DataFrame(rng.standard_normal((48, 4)) * 3, columns=list(p2.F_SET))
    d = p2.delta_report(Yt, list(p2.F_SET), n_boot=30)
    for v in d.values():
        assert 0 <= v["pi_lo"] <= v["pi_hi"] <= 1 and v["delta"] >= 0
    Yt["N4"] = Yt["V1"]                                                 # dropping a copy loses nothing
    assert p2._delta_k(Yt, ["V1", "E1", "N4"], "N4")[0] == 0.0


# --------------------------------------------------------------------------- scenarios (§8.13)
def test_additive(runs):
    r = runs["additive"]
    assert p2.seat_vector(r["res"]) == ("V1", "E1", "N4") and r["res"]["M"] == 3 and r["info"]["expected_match"]
    assert r["res"]["suppressed"] == {"X1": "E1"}
    assert r["info"]["n4_is_l252"] is True and not any(r["guard"]["flags"].values())


def test_total_only(runs):
    r = runs["total_only"]
    assert p2.seat_vector(r["res"]) == ("V1", "E1") and r["res"]["suppressed"]["N4"] == "V1"
    assert not r["tab"].loc["N4", "COMP_RESOLVABLE"]


def test_one_proxy(runs):
    r = runs["one_proxy"]
    assert p2.seat_vector(r["res"]) == ("V1", "E1", "N4")
    assert r["tab"].loc["V2", "IDR_over_B"] > 5 and r["tab"].loc["V2", "status"].startswith("PROXY")


def test_size_copy_loophole(runs):
    r = runs["size_copy"]
    assert p2.seat_vector(r["res"]) == ("V1", "E1") and r["res"]["suppressed"]["N4"] == "V1"
    assert r["P"].get("N4", "V1")["REDUNDANT_given_p"]


def test_asymmetric_escape(runs):
    r = runs["asymmetric"]
    assert not r["tab"].loc["V1", "COMP_RESOLVABLE"] and r["tab"].loc["N4", "COMP_RESOLVABLE"]
    assert r["P"].get("N4", "V1")["ESCAPE"] and p2.seat_vector(r["res"]) == ("V1", "E1", "N4")


def test_borderline_with_and_without_tradeoff(runs):
    a, b = runs["borderline_tradeoff"], runs["borderline_no_tradeoff"]
    assert a["P"].get("N4", "V1")["BORDERLINE_PAIR"] and b["P"].get("N4", "V1")["BORDERLINE_PAIR"]
    assert p2.seat_vector(a["res"]) == ("V1", "E1", "N4") and a["res"]["b4"][("N4", "V1")][-1]["resolves"]
    assert p2.seat_vector(a["res_no4b"]) == ("V1", "E1")
    assert p2.seat_vector(b["res"]) == ("V1", "E1") and not b["res"]["b4"][("N4", "V1")][-1]["resolves"]


def test_binding_floor(runs):
    t = runs["binding_floor"]["tab"]
    assert t.loc["X1", "RESOLVED"] and not t.loc["X1", "floor_pass"] and t.loc["X1", "IDR_over_B"] >= 2
    assert "materiality" in t.loc["X1", "why"] and _seats(runs["binding_floor"]["res"])["X"] == "EMPTY"


def test_noise_E1_halts(runs):
    r = runs["noise_E1"]["res"]
    assert r["halt"] and _seats(r)["E"] == "HALT FOR PI" and r["M"] is None
    assert runs["noise_E1"]["tab"].loc["E1", "status"].startswith("HALT")


def test_strong_proxy_never_seated(runs):
    r = runs["strong_proxy"]
    assert r["tab"].loc["E4", "IDR_over_B"] > r["tab"].loc["E1", "IDR_over_B"]
    assert not {"E4", "V2"} & set(p2.seat_vector(r["res"]))


def test_conflict_demotion(runs):
    r = runs["conflict_demotion"]["res"]
    assert r["demoted"] == ["N4"] and _seats(r)["N"] == "EMPTY" and p2.seat_vector(r) == ("V1", "E1")


def test_row_shuffle_invariance(X, B, runs):
    w = p2.synthetic_wide("borderline_tradeoff", X, B).sample(frac=1.0, random_state=3)
    r = _run("borderline_tradeoff", X, B, wide=w)
    a = runs["borderline_tradeoff"]
    cols = ["IDR_over_B", "IDR_over_B_lo90", "resid_IDR_over_B_lo90", "mantel_p_raw", "mantel_p_resid"]
    pd.testing.assert_frame_equal(r["tab"][cols], a["tab"][cols])
    assert p2.seat_line(r["res"]) == p2.seat_line(a["res"])


# --------------------------------------------------------------------------- outputs + guards
def test_written_outputs(X, B, tmp_path):
    out = _run("additive", X, B, write=True, out_dir=str(tmp_path), figs_dir=str(tmp_path / "figs"), make_figs=True)
    md = (tmp_path / "POOL_N0E_STANDINGS_v2.md").read_text()
    assert "SYNTHETIC DRY RUN" in md and p2.DISCLOSURE in md and p2.LENS_SENTENCE in md
    assert "v2 with borderline → REDUNDANT" in md and "## 9. N1_off guardrail" in md
    for f in ("pool_ed1b_v2.csv", "pool_pairs_v2.csv", "pool_lens_v2.csv"):
        assert (tmp_path / f).exists()
    for f in ("n0E_v2_idr_over_B_ci.png", "n0E_v2_rho5x5.png", "n0E_v2_clustermap_raw.png"):
        assert (tmp_path / "figs" / f).exists()
    assert out["info"]["landing"] == {"skipped": "synthetic run"}


def test_synthetic_guards(X, B, tmp_path):
    w = p2.synthetic_wide("additive", X, B)
    with pytest.raises(AssertionError, match="REFUSED: synthetic output under analysis/pool"):
        p2.run(wide=w, out_dir=os.path.join(po.POOL, "x"), make_figs=False, verbose=False, synthetic=True,
               line_reader=p2.synthetic_reader(w))
    with pytest.raises(AssertionError, match="REFUSED: an injected wide is synthetic"):
        p2.run(wide=w, out_dir=str(tmp_path), make_figs=False, verbose=False)


def test_outputs_are_v2_only():
    for f in ('"POOL_N0E_STANDINGS.md"', 'out_dir, "pool_ed1b_combined', '"pool_n0E_standings.csv"',
              "pool_ed1b_decision.csv", '"figs", "n0E")'):
        assert f not in SRC, f
    assert '"figs", "n0E_v2"' in SRC and "POOL_N0E_STANDINGS_v2.md" in SRC
