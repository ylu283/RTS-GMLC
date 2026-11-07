"""Prompt 57 Part B tests for pool_standings.py (synthetic 18-row fixture).

Run:  cd trial_0826/ercot && python -m pytest tests/test_pool_standings.py -q

Fixture: 6 sites x 3 levels (+ 3 nuclear rows) with planted answers:
- A: pure size effect (range 0 at every level) -> S' = 0, SIZE-DRIVEN
- B: pure site effect (same at every level)    -> S' undefined (size effect 0)
- C: site + size; C2 = 2C + tiny rank-preserving noise is the planted cluster partner
- T: planted trade-off, T = -C (oriented rho = -1 at every level)
- M: dir 'max' candidate equal to C (oriented -C: a trade-off with C, and rank-identical
  to T after orientation, so {M, T} is a second planted cluster with T surviving)
- nuclear rows carry wild values that must never enter range / S / W / rho.
Kendall W: perfect concordance -> W = 1, exact p = 1 / 518,400; the exact
distribution has mean 1/3 (n = 3 judges); mid-rank ties handled.
"""
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ERCOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ERCOT))
import pool_standings as ps  # noqa: E402

SITES = ["11", "22", "33", "44", "55", "66"]
LEVELS = ps.LEVELS
DEFS = {
    "family_order": ["V", "E", "X", "R", "N"],
    "global_order": ["A", "C", "T", "M", "C2", "B", "G", "Q"],
    "candidates": {
        "A": {"family": "V", "name": "size only", "unit": "u", "dir": "min", "priority": 1},
        "C": {"family": "E", "name": "site+size", "unit": "u", "dir": "min", "priority": 1},
        "T": {"family": "X", "name": "trade-off", "unit": "u", "dir": "min", "priority": 1},
        "M": {"family": "R", "name": "max twin of C", "unit": "u", "dir": "max", "priority": 1},
        "C2": {"family": "N", "name": "cluster partner of C", "unit": "u", "dir": "min", "priority": 1},
        "B": {"family": "N", "name": "site only", "unit": "u", "dir": "min", "priority": 2},
        "G": {"family": "R", "name": "guardrail-like", "unit": "u", "dir": "min", "priority": 3, "role": "guardrail"},
        "Q": {"family": "E", "name": "diag", "unit": "u", "dir": "-", "priority": None, "role": "diagnostic"},
    },
    "thresholds": {"redundancy": {"rule": "test"}},
}
IDS = list(DEFS["candidates"])


@pytest.fixture(scope="module")
def fixture():
    rows = []
    site_eff = {s: i * 10.0 for i, s in enumerate(SITES)}       # 0, 10, ..., 50
    rng = np.random.RandomState(57)
    k = 0
    for s in SITES:
        for l in LEVELS:
            mw = ps.LEVEL_MW[l]
            a = 100.0 + mw                                       # size only
            b = 5.0 + site_eff[s]                                # site only
            c = 100.0 + mw + site_eff[s]                         # site + size
            rows.append({"key": f"synth:{k + 1}", "index": k + 1, "site": s, "unit_type": "WIND",
                         "level_id": l, "pem_mw": mw,
                         "A": a, "B": b, "C": c, "T": -c, "M": c,
                         "C2": 2.0 * c + 1e-6 * rng.rand(),
                         "G": 1.0 + 0.001 * mw + (0.5 if s == "44" else 0.0),
                         "Q": 7.0 + mw * 0.01 + site_eff[s] * 0.001,
                         "G_run_usd": 1.0, "ruc_cost_sum_usd": 10.0, "E1": 5.0})
            k += 1
    for l in LEVELS:                                             # nuclear stratum, wild
        rows.append({"key": f"synth:{k + 1}", "index": k + 1, "site": "1", "unit_type": "NUC",
                     "level_id": l, "pem_mw": ps.LEVEL_MW[l],
                     **{c: 1e9 for c in IDS}, "G_run_usd": 1.0, "ruc_cost_sum_usd": 10.0, "E1": 5.0})
        k += 1
    wide = pd.DataFrame(rows)
    base = {c: 0.0 for c in IDS}
    base.update({"G_run_usd": 2.0, "ruc_cost_sum_usd": 10.0, "E1": 5.0})
    base["T"] = -100.0
    return wide, pd.Series(base)


def _reads(fixture, ruler=None):
    wide, base = fixture
    vre = ps.vre_rows(wide)
    assert len(vre) == 18 and len(ps.nuc_rows(wide)) == 3
    return ps.level_reads(vre, base, IDS, ruler=ruler)


# --------------------------------------------------------------------------
# step 1: range, S, S', nuclear exclusion
# --------------------------------------------------------------------------
def test_range_and_scale_free_ratios(fixture):
    reads, long = _reads(fixture)
    # A: size only -> range 0, S' = 0 at every level, mean size effect 120
    assert all(reads["A"]["range"][l] == 0.0 for l in LEVELS)
    assert reads["A"]["mean_size_effect_60_180"] == pytest.approx(120.0)
    assert all(reads["A"]["S_prime"][l] == 0.0 for l in LEVELS)
    assert reads["A"]["S_prime_verdict"].startswith("SIZE-DRIVEN")
    # A: S (v2-base delta) = 0 / mean|delta| (160, 220, 280) = 0 -> SIZE-DRIVEN as well
    assert reads["A"]["mean_abs_delta"]["L60"] == pytest.approx(160.0)
    assert reads["A"]["S_verdict"].startswith("SIZE-DRIVEN")
    # B: site only -> range 50 at every level, size effect 0 -> S' undefined, S = 50 / 30
    assert all(reads["B"]["range"][l] == pytest.approx(50.0) for l in LEVELS)
    assert reads["B"]["mean_size_effect_60_180"] == 0.0
    assert all(np.isnan(reads["B"]["S_prime"][l]) for l in LEVELS)
    assert reads["B"]["S_prime_verdict"] == "NO EFFECT AT EVERY LEVEL"
    assert reads["B"]["S"]["L60"] == pytest.approx(50.0 / 30.0)
    assert reads["B"]["S_verdict"].startswith("LOCATION-SENSITIVE")
    # C: site + size -> range 50, size effect 120 -> S' = 50/120 < 0.5 at every level
    assert all(reads["C"]["S_prime"][l] == pytest.approx(50.0 / 120.0) for l in LEVELS)
    assert reads["C"]["S_prime_verdict"].startswith("SIZE-DRIVEN")
    # nuclear exclusion: no 1e9 anywhere in the VRE reads
    for c in IDS:
        assert np.abs(reads[c]["X"].to_numpy()).max() < 1e6
    assert long["site"].isin(SITES).all() and len(long) == len(IDS) * 18


def test_ruler_pending_and_ruler_read(fixture):
    reads, _ = _reads(fixture)
    assert reads["C"]["ruler_status"] == ps.RULER_PENDING
    assert reads["C"]["ruler_verdict"] == ps.RULER_PENDING
    assert all(np.isnan(reads["C"]["range_over_ruler"][l]) for l in LEVELS)
    # with a ruler: C range 50 vs ruler 10 -> 5x at every level -> LOCATION-SENSITIVE
    reads, _ = _reads(fixture, ruler={"C": 10.0, "A": 10.0, "B": 0.0})
    assert reads["C"]["ruler_verdict"] == "LOCATION-SENSITIVE"
    assert reads["C"]["range_over_ruler"]["L60"] == pytest.approx(5.0)
    # A: range 0 < 2 x 10, per-site |delta| (160+) >= 20 on 6/6 sites -> INSENSITIVE AT THESE SIZES
    assert reads["A"]["ruler_verdict"] == "LOCATION-INSENSITIVE AT THESE SIZES"
    # B: RULER=0 -> natural-unit read (range 50 >= 1) -> LOCATION-SENSITIVE
    assert reads["B"]["ruler_status"] == "RULER=0" and reads["B"]["ruler_verdict"] == "LOCATION-SENSITIVE"
    # a candidate absent from the ruler file -> RULER UNAVAILABLE
    assert reads["T"]["ruler_status"] == "RULER UNAVAILABLE"


# --------------------------------------------------------------------------
# Kendall W exact
# --------------------------------------------------------------------------
def test_kendall_W_exact_distribution_sanity():
    dist = ps.exact_W_distribution(6, 3)
    assert len(dist) == 720 * 720
    assert dist.max() == pytest.approx(1.0) and dist.min() >= 0.0
    assert dist.mean() == pytest.approx(1.0 / 3.0, abs=1e-9)          # E[W] = 1/n under the null
    # perfect concordance -> W = 1, p = 1 / 518,400
    V = np.array([[1, 2, 3, 4, 5, 6], [10, 20, 30, 40, 50, 60], [0.1, 0.2, 0.3, 0.4, 0.5, 0.6]])
    W, p, ties, n = ps.kendall_W_exact(V)
    assert W == pytest.approx(1.0) and p == pytest.approx(1.0 / 518400) and ties == 0 and n == 518400
    # two reversed, one identity -> small W, large p
    V2 = np.array([[1, 2, 3, 4, 5, 6], [6, 5, 4, 3, 2, 1], [1, 2, 3, 4, 5, 6]])
    W2, p2, _, _ = ps.kendall_W_exact(V2)
    assert W2 < 0.2 and p2 > 0.5
    # ties: mid-ranks, counted
    V3 = np.array([[1, 1, 3, 4, 5, 6], [1, 2, 3, 4, 5, 6], [1, 2, 3, 4, 5, 6]])
    _, _, ties3, _ = ps.kendall_W_exact(V3)
    assert ties3 == 1
    # the fixture's B (site only) is perfectly concordant across levels
    assert ps.kendall_W(np.array([[1, 2, 3], [1, 2, 3]])) == pytest.approx(1.0)


# --------------------------------------------------------------------------
# step 3: oriented rho, planted cluster, planted trade-off, '-' never clusters
# --------------------------------------------------------------------------
def test_planted_cluster_and_tradeoff(fixture):
    wide, base = fixture
    vre = ps.vre_rows(wide)
    cb = ps.correlation_block(vre, IDS, DEFS, base)
    pairs = ps.pair_table(cb, IDS, DEFS)
    P = pairs.set_index("pair")
    # C2 = 2C + tiny noise: rank-identical -> redundant (pooled 1, every level 1)
    assert P.loc["C|C2", "rho_pooled_n18"] == pytest.approx(1.0) and P.loc["C|C2", "redundant_pair"]
    assert all(P.loc["C|C2", f"rho_{l}_n6"] == pytest.approx(1.0) for l in LEVELS)
    # M is dir max and equal to C: oriented -C -> rho_or = -1 -> trade-off, never a cluster
    assert P.loc["C|M", "rho_pooled_n18"] == pytest.approx(-1.0) and P.loc["C|M", "tradeoff_le_-0.90"]
    assert not P.loc["C|M", "redundant_pair"]
    # T = -C: oriented rho -1 pooled and at every level
    assert P.loc["C|T", "rho_pooled_n18"] == pytest.approx(-1.0)
    assert all(P.loc["C|T", f"rho_{l}_n6"] == pytest.approx(-1.0) for l in LEVELS)
    # A vs B: within a level A is constant -> per-level rho undefined (NaN); pooled defined
    assert np.isnan(P.loc["A|B", "rho_L60_n6"]) and np.isfinite(P.loc["A|C", "rho_pooled_n18"])
    # A vs C: pooled rho high (shared size trend) but per-level undefined -> NOT redundant (the 2-of-3 guard)
    assert P.loc["A|C", "rho_pooled_n18"] >= 0.9 and not P.loc["A|C", "redundant_pair"]
    # Q is '-' : shown, never redundant even if correlated
    assert not pairs.loc[(pairs["a"] == "Q") | (pairs["b"] == "Q"), "redundant_pair"].any()
    # clusters: {C, C2} and {M, T} (oriented M == T); survivor by global order
    members = [c for c in IDS if DEFS["candidates"][c]["dir"] in ("min", "max")]
    cl = ps.clusters_from_pairs(pairs, members)
    assert sorted(cl) == [["C", "C2"], ["M", "T"]]
    assert ps.survivor(["C", "C2"], DEFS["global_order"], {"C", "C2"}) == "C"
    assert ps.survivor(["C", "C2"], DEFS["global_order"], {"C2"}) == "C2"
    assert ps.survivor(["C", "C2"], DEFS["global_order"], set()) is None


def test_assemble_standings_and_conflicts(fixture):
    wide, base = fixture
    vre = ps.vre_rows(wide)
    reads, _ = ps.level_reads(vre, base, IDS)
    cb = ps.correlation_block(vre, IDS, DEFS, base)
    pairs = ps.pair_table(cb, IDS, DEFS)
    nuc = {c: {l: 1e9 for l in LEVELS} for c in IDS}
    shift = pd.DataFrame({"id": IDS, "identity_shift_scaled": 0.0, "scaling": "test"})
    tab, info = ps.assemble_standings(reads, nuc, cb, pairs, DEFS, dead_ids=[], ids=IDS,
                                      base_label="synth-base", shift=shift)
    t = tab.set_index("id")
    assert t.loc["C2", "status"] == "REDUNDANT->C" and t.loc["C", "cluster_id"] == t.loc["C2", "cluster_id"]
    assert t.loc["M", "status"] == "REDUNDANT->T" and t.loc["T", "is_survivor"]
    assert t.loc["Q", "status"] == "DIAGNOSTIC"
    assert t.loc["A", "status"] == "LOCATION-INSENSITIVE AT THESE SIZES"
    assert t.loc["B", "status"] == "UNREADABLE AT THIS SIZE"          # S' undefined (no size effect)
    assert t.loc["G", "status"] == "LOCATION-SENSITIVE"              # range 0.5 vs size effect 0.12
    assert all(t.loc["B", f"nuc_delta_{l}"] == 1e9 for l in LEVELS)  # overlay listed, never in range
    assert t.loc["B", "range_L60"] == pytest.approx(50.0)
    assert "C" in info["survivors"] and "C2" not in info["survivors"] and "B" not in info["survivors"]
    conf = ps.conflict_table(pairs, info["survivors"], DEFS, pinned=("C", "T"))
    c = conf.set_index("pair")
    assert c.index[0] == "C|T" and c.loc["C|T", "label"] == "TRADE-OFF (location)"
    assert "C|M" not in c.index                                      # M is REDUNDANT->T, not a survivor
    # a pinned pair whose member is not a survivor is still listed first
    conf2 = ps.conflict_table(pairs, info["survivors"], DEFS, pinned=("C", "C2"))
    assert conf2["pair"].iloc[0] == "C|C2" and not conf2["both_survivors"].iloc[0]
    ed, rec = ps.ed1b_table(tab, info, DEFS)
    assert rec == ["A", "C", "T"] and "C2" not in rec and "M" not in rec and "Q" not in rec
    assert len(rec) <= 4 and len({DEFS["candidates"][c]["family"] for c in rec}) == len(rec)
    assert "G" not in rec                                            # guardrail prior stays a guardrail
    assert ed.set_index("id").loc["G", "E_D1b_role"] == "GUARDRAIL (survivor)"


def test_gap_bound_reads(fixture):
    wide, base = fixture
    vre = ps.vre_rows(wide)
    g = ps.gap_bound_reads(vre, base, G_base=2.0, cost_ids=("A",))
    assert len(g) == 18
    assert (g["pair_bound_usd"] == 3.0).all()                        # G_base 2 + G_row 1
    assert np.allclose(g["G_base_share_of_bound"], 2.0 / 3.0)
    assert (g["gap_status_raw"] == "GAP-READABLE").all()             # |delta A| >= 160 > 3
    assert (g["v3_pair_bound_max_usd"] == 2.0).all()                 # two v3 rows: 1 + 1
    assert (g["range_vs_v3_pair_bound"] == "WITHIN GAP BOUND").all()  # range 0 < 2


def test_real_outputs_if_present():
    """Smoke on the committed outputs (skipped when absent)."""
    p = ERCOT / "analysis" / "pool" / "pool_standings.csv"
    if not p.is_file():
        pytest.skip("pool_standings.csv not on disk")
    t = pd.read_csv(p)
    allowed = {"DEAD", "DEAD ON WAVE D", "UNREADABLE AT THIS SIZE", "LOCATION-INSENSITIVE AT THESE SIZES",
               "LOCATION-SENSITIVE", "DIAGNOSTIC", "GUARDRAIL", "CANDIDATE"}
    for s in t["status"]:
        assert s in allowed or s.startswith("REDUNDANT->"), s
    assert (t["freeze_commit"] == ps.FREEZE_HASH).all()
    assert (t["ruler_status"] == ps.RULER_PENDING).all() or t["ruler_j"].notna().any()
    w = pd.read_csv(ERCOT / "analysis" / "pool" / "pool_wavedD_wide.csv")
    assert len(w) == 21 and w["full_extract"].all()
    os.path.isfile(ERCOT / "analysis" / "pool" / "pool_wide_v2.csv")
