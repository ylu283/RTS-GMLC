"""Prompt 34 — Stage-2 random baseline wave (random_C)."""

import json
import os
import re

import numpy as np
import pandas as pd
import pytest

import make_batches
from tiers import STAGE2_LATTICE, TIERS

SORTED_TIERS = sorted(TIERS)
OM = [f"{t}_omega" for t in SORTED_TIERS]


@pytest.fixture(scope="module")
def random_wave(tmp_path_factory):
    root = str(tmp_path_factory.mktemp("random_waves"))
    return make_batches.build_random_baseline("C", waves_root=root)


def _evaluated_48():
    keys = set()
    for w in make_batches.RANDOM_EXCLUDE_WAVES:
        dm = pd.read_csv(os.path.join(make_batches.WAVES_ROOT, w, "design_matrix.csv"))
        keys |= {make_batches._lattice_index_key(r) for r in dm[OM].to_numpy(float)}
    return keys


def test_determinism(random_wave, tmp_path):
    again = make_batches.build_random_baseline("C", waves_root=str(tmp_path))
    a = pd.read_csv(os.path.join(random_wave, "design_matrix.csv"))
    b = pd.read_csv(os.path.join(again, "design_matrix.csv"))
    pd.testing.assert_frame_equal(a, b)


def test_refuses_existing_dir(random_wave):
    with pytest.raises(RuntimeError, match="REFUSED"):
        make_batches.build_random_baseline(
            "C", waves_root=os.path.dirname(random_wave))


def test_zero_overlap_with_evaluated_48(random_wave):
    ev = _evaluated_48()
    assert len(ev) == 48
    dm = pd.read_csv(os.path.join(random_wave, "design_matrix.csv"))
    keys = [make_batches._lattice_index_key(r) for r in dm[OM].to_numpy(float)]
    assert not (set(keys) & ev)
    for k in (1, 2, 3):  # within-block distinctness
        blk = [kk for kk, a in zip(keys, dm["arm"]) if a == k]
        assert len(set(blk)) == 16


def test_on_lattice_all_six_tiers(random_wave):
    dm = pd.read_csv(os.path.join(random_wave, "design_matrix.csv"))
    lat = np.asarray(STAGE2_LATTICE, float)
    vals = dm[OM].to_numpy(float)
    assert np.isfinite(vals).all() and (vals >= 0.05 - 1e-12).all()
    assert all(np.isclose(lat, w, atol=1e-12).any() for w in vals.ravel())


def test_bids_and_rho(random_wave):
    dm = pd.read_csv(os.path.join(random_wave, "design_matrix.csv"))
    assert (dm[[f"{t}_bid" for t in SORTED_TIERS]] == 40.0).all().all()
    assert (dm["rho_h2"] == 2.0).all()


def test_indices_and_arms(random_wave):
    dm = pd.read_csv(os.path.join(random_wave, "design_matrix.csv"))
    assert list(dm["index"]) == list(range(1, 49))
    assert list(dm["index"]) == list(16 * (dm["arm"] - 1) + dm["arm_order"])


def test_manifest_draw_log(random_wave):
    m = json.load(open(os.path.join(random_wave, "manifest.json")))
    rb = m["random_baseline"]
    assert m["sobol"] is None
    assert rb["tier_order"] == SORTED_TIERS
    acc = [d for d in rb["draws"] if d["accepted"]]
    assert len(acc) == 48
    dm = pd.read_csv(os.path.join(random_wave, "design_matrix.csv"))
    keys = [list(make_batches._lattice_index_key(r)) for r in dm[OM].to_numpy(float)]
    assert [d["idx"] for d in acc] == keys
    assert all(v["in_recipe"] for v in rb["recipe_knee_check"].values())
    assert rb["sobol_continuation_arm"].startswith("OFF")


def test_scripts_no_tc_r_n(random_wave):
    array = open(os.path.join(random_wave, "random_C_array.sh")).read()
    submit = open(os.path.join(random_wave, "submit_this.sh")).read()
    assert "#$ -tc" not in array
    assert "-r n -t 1-48 random_C_array.sh" in submit
    assert re.search(r"qsub -terse -r n -hold_jid", submit)


def test_scripts_bot_and_email(random_wave):
    submit = open(os.path.join(random_wave, "submit_this.sh")).read()
    coll = open(os.path.join(random_wave, "collect_random_C.sh")).read()
    assert "stage2-bot" in submit and "stage2-bot" in coll
    assert "pairgrid-bot" not in submit + coll
    array_line = next(l for l in submit.splitlines() if "random_C_array.sh" in l and "qsub" in l)
    coll_line = next(l for l in submit.splitlines() if "collect_random_C.sh" in l and "qsub" in l)
    assert "-M" not in array_line and "-m " not in array_line
    assert "-M ylu28@nd.edu -m ea" in coll_line
    assert "#$ -r n" in coll and "PYTHONNOUSERSITE=1" in coll
    assert 'git -C "$REPO_DIR" rm -q -- "$WAVE_DIR/FAILED_random_C.md"' in coll
    assert "len(ob) == 48" in coll
    assert 'cd "$(dirname "${BASH_SOURCE[0]}")"' in submit
    assert "SUBMITTED random_C: array=$J collector=$C" in submit


def test_registered_without_tc():
    assert "random_C" in make_batches.BUILDERS
    assert "random_C" in make_batches.WAVE_MAX_CONCURRENT
    assert make_batches.WAVE_MAX_CONCURRENT["random_C"] is None


REAL = os.path.join(make_batches.WAVES_ROOT, "random_C")


@pytest.mark.skipif(not os.path.isdir(REAL), reason="real random_C wave not built yet")
def test_real_wave_manifest_clean():
    m = json.load(open(os.path.join(REAL, "manifest.json")))
    assert m["dirty"] is False
    assert m["n_rows"] == 48


# ---- T2: the primary statistic treats the 48 as ONE pool (prompt 34 §3.1) --

RB_DIR = os.path.join(os.path.dirname(make_batches.WAVES_ROOT), "analysis", "random_baseline")


@pytest.mark.skipif(not os.path.exists(os.path.join(REAL, "objectives.csv")),
                    reason="random_C results not collected yet")
def test_primary_ignores_arm():
    import inspect
    import sys
    sys.path.insert(0, RB_DIR)
    import rb_hv

    dm = pd.read_csv(os.path.join(REAL, "design_matrix.csv"))
    ob = pd.read_csv(os.path.join(REAL, "objectives.csv"))
    df = dm.merge(ob[["index"] + rb_hv.M_COLS], on="index", validate="1:1")
    shuffled = df.assign(arm=np.random.default_rng(0).permutation(df["arm"].to_numpy()),
                         arm_order=0).sample(frac=1, random_state=1)
    Y, Ys = rb_hv.pool_matrix(df), rb_hv.pool_matrix(shuffled)
    np.testing.assert_array_equal(Y, Ys)
    for fn in (rb_hv.p_hat, rb_hv.subset_hvs, rb_hv.boot_task, rb_hv.perturb_task):
        assert "arm" not in inspect.signature(fn).parameters
    toy_hv = lambda P, ref: float(np.prod(np.clip(ref - P.min(0), 0, None)))
    starts, ref = Y[:4] * 1.5, Y.max(0) * 2
    args = (starts, Y, toy_hv(starts, ref) * 1.1, ref, 16, 500)
    p1, h1 = rb_hv.p_hat(*args, np.random.default_rng(7), toy_hv)
    p2, h2 = rb_hv.p_hat(starts, Ys, *args[2:], np.random.default_rng(7), toy_hv)
    assert p1 == p2 and np.array_equal(h1, h2)


def test_percentile_ties_count_half():
    import sys
    sys.path.insert(0, RB_DIR)
    import rb_hv
    assert rb_hv.percentile_of(1.0, np.array([0.5, 1.0, 1.0 + 1e-13, 2.0])) == pytest.approx(0.25 + 0.5 * 0.5)
    assert rb_hv.verdict_row(0.95, 0.6, 0.99) == "above"
    assert rb_hv.verdict_row(0.95, 0.4, 0.99) == "comparable"
    assert rb_hv.verdict_row(0.05, 0.0, 0.3) == "matched"
    assert rb_hv.verdict_row(0.5) == "comparable"
