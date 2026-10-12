"""Prompt 36 T1 tests (a)–(e) + the RTS-GMLC round-trip (§3.0).

(f) — the campaign / multi_pem suites — is run by tests/run_cost_fix_tests.sh.
"""
import hashlib
import math
import os

import numpy as np
import pandas as pd
import pytest

from conftest import FORK_SHA, egret_identity
import convert_tx123_costs as cv

THERMAL = cv.THERMAL
FACTOR = cv.FACTOR


def chosen(source, reading):
    """{uid: (C0, C1, C2, start $, fp, pmin, pmax)} for the chosen reading."""
    out = {}
    for _, s in source.iterrows():
        if reading in ("c", "a"):
            C0, C1, Csu = s["C0_xlsx"], s["C1_xlsx"], s["Csu_xlsx"]
        else:
            C0, C1, Csu = s["c0_pkl"], s["c1_pkl"], s["csu_pkl"]
        C2 = cv.C2_COAL if (reading == "a" and s["Unit Type"] == "COAL") else 0.0
        out[str(int(s["GEN UID"]))] = (C0, C1, C2, Csu * s["PMax MW"],
                                       s["Fuel Price $/MMBTU"], s["PMin MW"], s["PMax MW"])
    return out


def egret_start_costs(g):
    """params.startup_costs_init_rule for a startup_fuel list."""
    nf = g.get("non_fuel_startup_cost") or 0.0
    return [nf + g["fuel_cost"] * h for _, h in g["startup_fuel"]]


# ---------------------------------------------------------------- (a) ------
def test_a_egret_is_the_fork():
    fork_src, sha, path = egret_identity()
    print(f"\negret: {path}\n  fork rounding in source: {fork_src}; git HEAD: {sha}")
    assert fork_src, "loaded egret lacks the fork rounding (round(.,4) / round(.,6)) — stock egret?"
    if sha is None or not sha.startswith(FORK_SHA):
        if os.environ.get("ERCOT_LOCAL_PATCHED_EGRET") == "1":
            pytest.skip(f"local patched copy (HEAD {sha}); fork hash enforced on CRC only")
        pytest.fail(f"egret checkout HEAD {sha} is not {FORK_SHA}")


def test_a_breakpoints_and_cost(v2_dir, skeleton, source, reading):
    gens = skeleton(v2_dir)
    want = chosen(source, reading)
    assert len(want) == 128
    worst = 0.0
    for uid, (C0, C1, C2, _, fp, pmin, pmax) in want.items():
        pts = gens[uid]["p_fuel"]["values"]
        assert abs(pts[0][0] - pmin) < 1e-4 and abs(pts[-1][0] - pmax) < 1e-4, (uid, pts)
        assert gens[uid]["fuel_cost"] == fp
        for x, f in pts:
            err = abs(fp * f - (C0 + C1 * x + C2 * x * x))
            worst = max(worst, err / fp)
            assert err < 1e-5 * fp, (uid, x, fp * f, C0 + C1 * x + C2 * x * x)
    print(f"\nmax |parsed cost − C(x)|/fp over all breakpoints: {worst:.2e}")


# ---------------------------------------------------------------- (b) ------
def test_b_convexity_all_128(v2_dir, skeleton):
    from egret.model_library.transmission.tx_utils import validate_and_clean_cost_curve
    gens = skeleton(v2_dir)
    n = 0
    for uid, g in gens.items():
        if g.get("generator_type") != "thermal":
            continue
        validate_and_clean_cost_curve(g["p_fuel"], "fuel_curve", g["p_min"], g["p_max"], uid)
        n += 1
    assert n == 128


# ---------------------------------------------------------------- (c) ------
def test_c_start_cost(v2_dir, skeleton, source, reading):
    gens = skeleton(v2_dir)
    for uid, (*_, start, fp, pmin, pmax) in chosen(source, reading).items():
        costs = egret_start_costs(gens[uid])
        assert len(costs) == 1, (uid, gens[uid]["startup_fuel"])  # 1 h start times collapse
        assert math.isclose(costs[0], start, rel_tol=1e-12), (uid, costs, start)


# ---------------------------------------------------------------- (d) ------
def test_d_non_cost_bytes_identical(v1_dir, v2_dir):
    md5 = lambda p: hashlib.md5(p.read_bytes()).hexdigest()
    for f in cv.V1_CSVS:
        if f != "gen.csv":
            assert md5(v1_dir / f) == md5(v2_dir / f), f
    l1 = (v1_dir / "gen.csv").read_text().split("\n")
    l2 = (v2_dir / "gen.csv").read_text().split("\n")
    assert l1[0] == l2[0] and len(l1) == len(l2)
    hdr = l1[0].split(",")
    ut = hdr.index("Unit Type")
    n_th = 0
    for a, b in zip(l1[1:], l2[1:]):
        ca, cb = a.split(","), b.split(",")
        if ca and len(ca) > ut and ca[ut] in THERMAL:
            n_th += 1
            for i, c in enumerate(hdr):
                if c not in cv.COST_COLS:
                    assert ca[i] == cb[i], (ca[0], c)
        else:
            assert a == b, ca[:3]
    assert n_th == 128


# ---------------------------------------------------------------- (e) ------
def test_e_csv_coefficients_and_report(v2_dir, source, reading):
    g = pd.read_csv(v2_dir / "gen.csv")
    g = g[g["Unit Type"].isin(THERMAL)].set_index(g["GEN UID"].astype(str)[g["Unit Type"].isin(THERMAL)])
    want = chosen(source, reading)
    for uid, (C0, C1, C2, start, fp, pmin, pmax) in want.items():
        r = g.loc[uid]
        if C2 == 0:
            C1b = fp * r["HR_incr_1"] / 1000
            C0b = fp * r["HR_avg_0"] * pmin / 1000 - C1b * pmin
            assert math.isclose(C1b, C1, rel_tol=1e-9), (uid, C1b, C1)
            assert abs(C0b - C0) <= 1e-9 * max(abs(C0), C1 * pmin), (uid, C0b, C0)
        heat = r["Start Heat Cold MBTU"] * fp + r["Non Fuel Start Cost $"]
        assert math.isclose(heat, start, rel_tol=1e-9), (uid, heat, start)

    # report (no gates)
    df = pd.DataFrame([{"uid": u, "type": g.loc[u, "Unit Type"], "C0": v[0], "C1": v[1],
                        "start": v[3], "pmax": v[6]} for u, v in want.items()])
    print(f"\nreading ({reading}) ×{FACTOR[reading]} — by type:")
    print(df.groupby("type").agg(n=("uid", "size"), noload_med=("C0", "median"),
                                 mc_min=("C1", "min"), mc_max=("C1", "max"),
                                 start_med=("start", "median")).to_string())
    m = df.sort_values("C1").assign(cum_gw=lambda d: d["pmax"].cumsum() / 1e3)
    print("merit order (first 5 / last 3):")
    print(m[["uid", "type", "C1", "cum_gw"]].head(5).to_string(index=False))
    print(m[["uid", "type", "C1", "cum_gw"]].tail(3).to_string(index=False))
    for B in (40.0, 28.0):
        below = m[m["C1"] < B]
        print(f"B = {B}: {below['pmax'].sum()/1e3:.1f} GW of {m['pmax'].sum()/1e3:.1f} GW "
              f"thermal has C1 < B")


# ------------------------------------------------------- RTS round trip ----
RTS_THERMAL = ("CT", "CC", "STEAM", "NUCLEAR")


def test_rts_round_trip(rts_dir, skeleton, tmp_path):
    """Linearize RTS-GMLC thermal rows, feed them through the TX converter,
    parse both with the fork: cost at PMin / PMax and start cost must match."""
    import shutil
    orig = skeleton(rts_dir)
    rts = pd.read_csv(rts_dir / "gen.csv")
    th = rts[rts["Unit Type"].isin(RTS_THERMAL) & (rts["PMin MW"] > 0)
             & (rts["Fuel Price $/MMBTU"] > 0)]
    assert len(th) > 50
    new = rts.copy()
    want = {}
    for i, row in th.iterrows():
        uid = str(row["GEN UID"])
        o = orig[uid]
        pts = o["p_fuel"]["values"]
        fp = o["fuel_cost"]
        pmin, pmax = o["p_min"], o["p_max"]
        assert abs(pts[0][0] - pmin) < 1e-4 and abs(pts[-1][0] - pmax) < 1e-4, uid
        c_min, c_max = fp * pts[0][1], fp * pts[-1][1]
        C1 = (c_max - c_min) / (pmax - pmin)
        C0 = c_min - C1 * pmin
        start = egret_start_costs(o)[-1]                       # coldest tier
        cols, _, _ = cv.convert_unit(row.to_dict(), C0, C1, start / pmax)
        for c, v in cols.items():
            if c in new.columns:
                new.at[i, c] = np.nan if v is None else float(cv._fmt(v))
        want[uid] = (c_min, c_max, start, fp)
    for f in ("bus.csv", "branch.csv"):
        shutil.copyfile(rts_dir / f, tmp_path / f)
    new.to_csv(tmp_path / "gen.csv", index=False)
    conv = skeleton(tmp_path)
    for uid, (c_min, c_max, start, fp) in want.items():
        p = conv[uid]["p_fuel"]["values"]
        assert abs(fp * p[0][1] - c_min) < 1e-5 * fp, (uid, fp * p[0][1], c_min)
        assert abs(fp * p[-1][1] - c_max) < 1e-5 * fp, (uid, fp * p[-1][1], c_max)
        assert math.isclose(egret_start_costs(conv[uid])[-1], start, rel_tol=1e-9), uid
    print(f"\nRTS round trip: {len(want)} thermal units reproduce C(PMin), C(PMax), cold start")
