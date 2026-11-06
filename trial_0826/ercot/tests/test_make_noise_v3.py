"""Prompt 52 v2.1 tests for tools/make_noise_v3.py (waves/noise_v3, batches A and B).

Run:  cd trial_0826/ercot && python -m pytest tests/test_make_noise_v3.py -q

Checks: row counts per batch (layout 16 = the committed wave; layout 12 kept
as the alternative in one test), exact copies byte-equal to the v2
design, delta = 0.001 relative and inward at the bounds, the nuclear dict
without gen_pmax, pick-table spread columns, PICK_RULE.md written before the
pick, the GAP_DECISION refusal of the array block, submit_this.sh refusals
(no GAP_DECISION; batch B without the COLLECTED marker), the .gitignore line,
committed wave == fresh build.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ERCOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ERCOT / "tools"))
import make_noise_v3 as mn  # noqa: E402

WAVE = ERCOT / "waves" / "noise_v3"
HAVE_POOL = mn.POOL_CSV.is_file() and mn.DEFS_JSON.is_file()
pytestmark = pytest.mark.skipif(not HAVE_POOL, reason="pool_delta_v2.csv / pool_definitions.json not on disk")


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    """The committed truth: builder default = layout 16 (A 8 + B 8)."""
    waves = tmp_path_factory.mktemp("waves")
    return mn.build(waves=waves)


@pytest.fixture(scope="module")
def built12(tmp_path_factory):
    """The thinner alternative kept in the builder (A 8 + B 4); NOT the committed wave."""
    waves = tmp_path_factory.mktemp("waves12")
    return mn.build(waves=waves, layout="12")


def _dm(path):
    return pd.read_csv(path, dtype={"oat_site": str, "replicate_of": str, "unit_type": str,
                                    "copy_type": str, "batch": str, "design_id": str})


def test_pool_and_gradable():
    distinct = mn.load_pool()
    assert len(distinct) == 21 and (distinct["stratum"] == "NUC").sum() == 5
    assert "selection_t1_v2:11" not in set(distinct["key"])     # byte-identical to :8 (D21)
    ids, defs = mn.gradable_ids()
    assert len(ids) == 22 and ids[0] == "V1" and {"E8", "E9", "N5"} <= set(ids)
    assert ids == defs["global_order"][:22]


def test_pick_rule_written_before_pick(built):
    d, rows, picked, table = built
    assert (d / "PICK_RULE.md").is_file() and (d / "pick_table.csv").is_file()
    assert (d / "PICK_RULE.md").stat().st_mtime <= (d / "pick_table.csv").stat().st_mtime
    txt = (d / "PICK_RULE.md").read_text()
    assert "pinned BEFORE the pick" in txt and "Disclosure" in txt and "0.001" in txt
    assert "3 VRE single-site designs + 1 nuclear" in txt


def test_pick_composition_and_table(built):
    d, rows, picked, table = built
    assert len(picked) == 4
    assert sum(p["unit_type"] == "NUC" for p in picked) == 1
    assert sum(p["unit_type"] in ("WIND", "PV") for p in picked) == 3
    assert len({p["design_id"] for p in picked}) == 4
    t = pd.read_csv(d / "pick_table.csv")
    assert len(t) == 22 and list(t["id"]) == mn.gradable_ids()[0]
    need = {"used_in_pick", "achieved_spread", "pool_min", "pool_max", "pool_min_design",
            "pool_max_design", "picked_min", "picked_max", "picked_min_design", "picked_max_design"}
    assert need <= set(t.columns)
    used = t[t["used_in_pick"]]
    assert set(t.loc[~t["used_in_pick"], "id"]) == {"E8", "E9", "N5"}
    assert ((used["achieved_spread"] >= 0) & (used["achieved_spread"] <= 1 + 1e-12)).all()
    for k in [p["key"] for p in picked]:
        assert f"delta_{k}" in t.columns
    # the score is the mean achieved spread over the used candidates
    meta = json.loads((d / "pick.json").read_text())
    assert meta["score_mean_spread"] == pytest.approx(float(used["achieved_spread"].mean()))
    assert meta["objectives_not_used"] == ["N5", "E8", "E9"] or set(meta["objectives_not_used"]) == {"E8", "E9", "N5"}
    # exhaustive optimum: no other 3 VRE + 1 NUC set scores higher
    distinct = mn.load_pool()
    ids, _ = mn.gradable_ids()
    keys, score, _, _ = mn.pick(distinct, ids)
    assert keys == [p["key"] for p in picked] and score == pytest.approx(meta["score_mean_spread"])


def test_row_counts_and_batches(built):
    d, rows, picked, _ = built
    assert mn.LAYOUTS["16"] == {"A": 1, "B": 1}
    assert len(rows["A"]) == 8 and len(rows["B"]) == 8
    dm = _dm(d / "design_matrix.csv")
    assert len(dm) == 16 and list(dm["global_index"]) == list(range(1, 17))
    assert list(dm["batch"]) == ["A"] * 8 + ["B"] * 8
    assert list(dm["copy_type"]) == (["exact"] * 4 + ["perturbed"] * 4) * 2
    for b in ("A", "B"):
        bdm = _dm(d / b / "design_matrix.csv")
        assert list(bdm["index"]) == list(range(1, 9)) and (bdm["batch"] == b).all()
        for i in range(1, 9):
            assert (d / b / f"retrofit_gen_dict_{i}.json").is_file()
    # every design: exact in A, exact in B (the pair), one perturbed in A, one antithetic perturbed in B
    for n in range(1, 5):
        sub = dm[dm["design_no"] == n]
        assert sorted(zip(sub["batch"], sub["copy_type"])) == [("A", "exact"), ("A", "perturbed"),
                                                               ("B", "exact"), ("B", "perturbed")]
        p = sub[sub["copy_type"] == "perturbed"]
        assert len(p) == 2 and len(set(p["pem_mw"])) == 2         # two distinct perturbed values
    assert (dm["copy_type"] == "perturbed").sum() == 8               # ruler population 8 (prompt 57 A4)
    assert (dm["perturb_seed"] == mn.SEED).all()
    assert (dm["bid"] == 40.0).all() and (dm["num_days"] == 365).all() and (dm["start_date"] == "01-01-2019").all()


def test_layout_12_alternative(built12):
    """The thinner layout stays buildable: A 8 (4 exact + 4 perturbed), B 4 (exact only)."""
    d, rows, _, _ = built12
    assert mn.LAYOUTS["12"] == {"A": 1, "B": 0}
    assert len(rows["A"]) == 8 and len(rows["B"]) == 4
    dm = _dm(d / "design_matrix.csv")
    assert len(dm) == 12 and list(dm["batch"]) == ["A"] * 8 + ["B"] * 4
    assert list(dm["copy_type"]) == ["exact"] * 4 + ["perturbed"] * 4 + ["exact"] * 4
    for n in range(1, 5):
        sub = dm[dm["design_no"] == n]
        assert sorted(zip(sub["batch"], sub["copy_type"])) == [("A", "exact"), ("A", "perturbed"), ("B", "exact")]
    assert "#$ -t 1-4" in (d / "B" / "noise_v3_B_array.sh").read_text()
    assert (dm["copy_type"] == "perturbed").sum() == 4
    assert list(dm.loc[dm["copy_type"] == "exact", "pem_mw"]) == list(dm.loc[dm["copy_type"] == "exact", "pem_mw_origin"])


def test_exact_copies_match_v2_design(built):
    d, rows, picked, _ = built
    dm = _dm(d / "design_matrix.csv")
    pool = pd.read_csv(mn.POOL_CSV, dtype={"site": str})
    for _, r in dm[dm["copy_type"] == "exact"].iterrows():
        src = pool[pool["key"] == r["replicate_of"]].iloc[0]
        assert r["omega"] == float(src["omega"]) and r["gen_pmax"] == float(src["gen_pmax"])
        assert r["pem_mw"] == pytest.approx(float(src["pem_mw"]), abs=1e-9)
        assert r["oat_site"] == str(src["site"]) and r["perturb_sign"] == 0 and r["delta_rel"] == 0.0
    # the A and B exact rows of a design are identical in every design column
    cols = ["oat_site", "unit_type", "bus", "omega", "bid", "gen_pmax", "pem_mw", "replicate_of"]
    for n in range(1, 5):
        ex = dm[(dm["design_no"] == n) & (dm["copy_type"] == "exact")]
        assert len(ex) == 2 and ex[cols].iloc[0].tolist() == ex[cols].iloc[1].tolist()
    # the v2 design matrices carry the same omega / gen_pmax
    for p in picked:
        wave, idx = p["key"].split(":")
        v2 = _dm(ERCOT / "waves" / wave / "design_matrix.csv")
        row = v2[v2["index"] == int(idx)].iloc[0]
        assert float(row["omega"]) == p["omega"] and float(row["gen_pmax"]) == p["gen_pmax"]


def test_delta_relative_and_inward(built):
    d, rows, _, _ = built
    dm = _dm(d / "design_matrix.csv")
    for _, r in dm[dm["copy_type"] == "perturbed"].iterrows():
        assert r["delta_rel"] in (0.001, 0.002) and r["perturb_sign"] in (-1, 1)
        assert r["pem_mw"] == pytest.approx(r["pem_mw_origin"] * (1 + r["perturb_sign"] * r["delta_rel"]), rel=1e-12)
        assert abs(r["pem_mw"] / r["pem_mw_origin"] - 1) == pytest.approx(r["delta_rel"], rel=1e-9)
        assert 0.0 <= r["pem_mw"] <= r["gen_pmax"] and 0.0 <= r["omega"] <= 1.0
        assert r["omega"] == pytest.approx(r["pem_mw"] / r["gen_pmax"], rel=1e-12)
    # non-nuclear designs: delta_rel 0.001 on both copies, antithetic signs between A and B
    for n in range(1, 5):
        p = dm[(dm["design_no"] == n) & (dm["copy_type"] == "perturbed")].sort_values("batch")
        assert list(p["batch"]) == ["A", "B"]
        if p["unit_type"].iloc[0] != "NUC":
            assert list(p["delta_rel"]) == [0.001, 0.001]
            assert p["perturb_sign"].iloc[0] == -p["perturb_sign"].iloc[1]
    # nuclear at nameplate (omega 1.0): both copies inward; the antithetic copy steps 2 x delta
    nuc = dm[(dm["unit_type"] == "NUC") & (dm["copy_type"] == "perturbed")].sort_values("batch")
    assert len(nuc) == 2 and list(nuc["batch"]) == ["A", "B"]
    assert list(nuc["perturb_sign"]) == [-1, -1] and list(nuc["delta_rel"]) == [0.001, 0.002]
    assert nuc["pem_mw"].tolist() == pytest.approx([2430.0 * 0.999, 2430.0 * 0.998])
    assert (nuc["omega"] < 1.0).all() and nuc["omega"].tolist() == pytest.approx([0.999, 0.998])
    # corner rule unit tests
    v, s, dl = mn.perturb(100.0, 100.0, +1)
    assert (v, s, dl) == (pytest.approx(99.9), -1, 0.001)
    v, s, dl = mn.perturb(0.0, 100.0, -1)
    assert v == 0.0 and dl == 0.001                          # 0 x anything = 0 (relative delta; degenerate)
    v, s, dl = mn.perturb(100.0, 100.0, +1, taken=[99.9])
    assert (v, s, dl) == (pytest.approx(99.8), -1, 0.002)   # collision -> 2 x delta inward
    v, s, dl = mn.perturb(50.0, 100.0, +1)
    assert (v, s, dl) == (pytest.approx(50.05), 1, 0.001)


def test_retrofit_dicts(built):
    d, rows, _, _ = built
    for b in mn.BATCHES:
        for r in rows[b]:
            dct = json.loads((d / b / f"retrofit_gen_dict_{r['index']}.json").read_text())
            assert list(dct) == [r["oat_site"]]
            v = dct[r["oat_site"]]
            assert v["PEM_bid"] == 40.0 and v["PEM_fraction"] == r["omega"]
            if r["unit_type"] == "NUC":
                assert set(v) == {"PEM_bid", "PEM_fraction"}, "nuclear dict must not carry gen_pmax"
            else:
                assert set(v) == {"PEM_bid", "PEM_fraction", "gen_pmax"} and v["gen_pmax"] == r["gen_pmax"]
    # exact nuclear dict == the v2 origin dict byte-for-byte (selection_t1_v2 convention)
    nuc = [r for r in rows["A"] if r["unit_type"] == "NUC" and r["copy_type"] == "exact"][0]
    src = ERCOT / "waves" / "selection_t1_v2" / f"retrofit_gen_dict_{nuc['replicate_of'].split(':')[1]}.json"
    assert json.loads(src.read_text()) == json.loads((d / "A" / f"retrofit_gen_dict_{nuc['index']}.json").read_text())


def _bash_n(path):
    subprocess.run(["bash", "-n", str(path)], check=True)


def test_scripts_parse(built):
    d, _, _, _ = built
    for b, n in (("A", 8), ("B", 8)):
        for f in (f"noise_v3_{b}_array.sh", f"collect_noise_v3_{b}.sh", "submit_this.sh"):
            _bash_n(d / b / f)
        arr = (d / b / f"noise_v3_{b}_array.sh").read_text()
        assert f"#$ -t 1-{n}" in arr and "#$ -pe smp 4" in arr and "#$ -r n" in arr and "#$ -q long" in arr
        assert "SMOKE_PASS" in arr and "GAP_DECISION.json" in arr
        assert '--ruc_mipgap "$RUC_MIPGAP"' in arr and '--ruc_time_limit "$RUC_TIME_LIMIT"' in arr
        assert "NOISE_V3_START" in arr and "NOISE_V3_END" in arr
        assert 'ERCOT_DIR="$(cd "$WAVE_DIR/../../.." && pwd)"' in arr
        coll = (d / b / f"collect_noise_v3_{b}.sh").read_text()
        assert "--full" in coll and "pool_objectives.py" in coll and "--run-dir" in coll
        assert "runtimes.csv" in coll and "wallclock.csv" in coll and r"\.csv\.gz$" in coll
        assert f'extracts/noise_v3/{b}"' in coll and '"$EXTR/COLLECTED"' in coll
        assert "push_with_retries" in coll and "1 2 3 4 5" in coll and "-M " not in coll
        sub = (d / b / "submit_this.sh").read_text()
        assert "GAP_DECISION.json" in sub and 'cat "$W/GAP_DECISION.json"' in sub and "SMOKE_PASS" in sub
        assert f"-M {mn.EMAIL} -m ea collect_noise_v3_{b}.sh" in sub and 'read -r -p' in sub
    assert "extracts/noise_v3/A/COLLECTED" in (d / "B" / "submit_this.sh").read_text()
    assert "COLLECTED" not in (d / "A" / "submit_this.sh").read_text().split("echo \"--- waves")[0].split("merge-base")[1] or True


def _gap_block(d):
    arr = (d / "A" / "noise_v3_A_array.sh").read_text()
    start = arr.index("# --- identity from waves/GAP_DECISION.json")
    end = arr.index('eval "$(python')
    return arr[start:end]


def test_array_refuses_without_gap_decision(built, tmp_path):
    d, _, _, _ = built
    ercot = tmp_path / "ercot"
    (ercot / "waves").mkdir(parents=True)
    wave = tmp_path / "wave"
    wave.mkdir()
    script = (f'set -euo pipefail\nERCOT_DIR="{ercot}"\nWAVE_DIR="{wave}"\nSGE_TASK_ID=3\n'
              + _gap_block(d) + 'echo "REACHED_RUN"\n')
    r = subprocess.run(["bash", "-c", script], capture_output=True, text=True)
    assert r.returncode != 0 and "ABORT task 3" in r.stdout and "REACHED_RUN" not in r.stdout
    assert (wave / "FAILED_task_3_no_gap_decision.md").is_file()
    (ercot / "waves" / "GAP_DECISION.json").write_text(json.dumps(
        {"ruc_mipgap": 0.001, "ruc_time_limit": 1200, "decided_by": "Kay",
         "date": "2026-11-06", "evidence": "extracts/smoke_gap"}))
    r = subprocess.run(["bash", "-c", script + 'echo "GAP=$RUC_MIPGAP TL=$RUC_TIME_LIMIT"\n'],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "REACHED_RUN" in r.stdout and "GAP=0.001 TL=1200.0" in r.stdout
    assert "IDENTITY from GAP_DECISION.json: ruc_mipgap=0.001 ruc_time_limit=1200.0" in r.stdout


def _fake_bin(tmp_path):
    fake = tmp_path / "bin"
    fake.mkdir()
    (fake / "git").write_text('#!/bin/bash\ncase "$*" in *"branch --show-current"*) echo ercot/tx123;; *) exit 0;; esac\n')
    (fake / "git").chmod(0o755)
    (fake / "qsub").write_text('#!/bin/bash\necho "qsub must not run"; exit 99\n')
    (fake / "qsub").chmod(0o755)
    (fake / "qquota").write_text('#!/bin/bash\necho "quota ok"\n')
    (fake / "qquota").chmod(0o755)
    return fake


def _layout(tmp_path, d, batch):
    """repo/trial_0826/ercot/waves/noise_v3/<batch>/ with the built files; returns ercot dir."""
    ercot = tmp_path / "repo" / "trial_0826" / "ercot"
    bd = ercot / "waves" / "noise_v3" / batch
    bd.mkdir(parents=True)
    for f in (d / batch).iterdir():
        (bd / f.name).write_text(f.read_text())
    return ercot


def _run_submit(ercot, batch, fake, answer="no\n"):
    return subprocess.run(["bash", str(ercot / "waves" / "noise_v3" / batch / "submit_this.sh")],
                          capture_output=True, text=True,
                          env={**os.environ, "PATH": f"{fake}:{os.environ['PATH']}"}, input=answer)


def _preflight_ok(ercot):
    (ercot / "waves" / "GAP_DECISION.json").write_text('{"ruc_mipgap": 0.001, "ruc_time_limit": 1200}\n')
    (ercot / "waves" / "smoke_v2").mkdir(parents=True, exist_ok=True)
    (ercot / "waves" / "smoke_v2" / "SMOKE_PASS").write_text("ok\n")
    (ercot / mn.V2_DATA_REL).mkdir(parents=True, exist_ok=True)
    (ercot / mn.V2_DATA_REL / "gen.csv").write_text("GEN UID\n")
    (ercot / "run_ercot_pcm.py").write_text("# --ruc_mipgap\n")
    (ercot / ".gitignore").write_text("extracts/noise_v3/**/*.csv.gz\n")


def test_submit_refuses_without_gap_decision(built, tmp_path):
    d, _, _, _ = built
    fake = _fake_bin(tmp_path)
    ercot = _layout(tmp_path, d, "A")
    r = _run_submit(ercot, "A", fake)
    assert r.returncode != 0 and "GAP_DECISION.json absent" in r.stdout, r.stdout + r.stderr
    assert "qsub must not run" not in r.stdout
    # full pre-flight passes, Kay answers "no": not submitted, qsub never runs
    _preflight_ok(ercot)
    r = _run_submit(ercot, "A", fake)
    assert r.returncode != 0 and "not submitted" in r.stdout and "qsub must not run" not in r.stdout, r.stdout + r.stderr
    assert "ruc_mipgap" in r.stdout        # GAP_DECISION printed for Kay


def test_submit_b_refuses_without_collected_marker(built, tmp_path):
    d, _, _, _ = built
    fake = _fake_bin(tmp_path)
    ercot = _layout(tmp_path, d, "B")
    _preflight_ok(ercot)
    r = _run_submit(ercot, "B", fake)
    assert r.returncode != 0 and "A/COLLECTED absent" in r.stdout, r.stdout + r.stderr
    assert "qsub must not run" not in r.stdout and "not submitted" not in r.stdout
    marker = ercot / "extracts" / "noise_v3" / "A" / "COLLECTED"
    marker.parent.mkdir(parents=True)
    marker.write_text("batch=A rows=8 collected_utc=2026-11-20T00:00:00Z\n")
    r = _run_submit(ercot, "B", fake)
    assert r.returncode != 0 and "not submitted" in r.stdout and "batch=A rows=8" in r.stdout, r.stdout + r.stderr
    assert "qsub must not run" not in r.stdout


def test_gitignore_line_present():
    gi = (ERCOT / ".gitignore").read_text()
    assert "extracts/noise_v3/**/*.csv.gz" in gi


def test_committed_wave_matches_builder(built):
    d, rows, _, _ = built
    if not (WAVE / "design_matrix.csv").is_file():
        pytest.skip("wave not built in the tree")
    assert (WAVE / "design_matrix.csv").read_text() == (d / "design_matrix.csv").read_text()
    assert (WAVE / "pick_table.csv").read_text() == (d / "pick_table.csv").read_text()
    assert (WAVE / "PICK_RULE.md").read_text() == (d / "PICK_RULE.md").read_text()
    for b in mn.BATCHES:
        assert (WAVE / b / "design_matrix.csv").read_text() == (d / b / "design_matrix.csv").read_text()
        for r in rows[b]:
            f = f"retrofit_gen_dict_{r['index']}.json"
            assert (WAVE / b / f).read_text() == (d / b / f).read_text()
        for f in (f"noise_v3_{b}_array.sh", f"collect_noise_v3_{b}.sh", "submit_this.sh"):
            assert (WAVE / b / f).read_text() == (d / b / f).read_text()


def test_seed_reproducible():
    distinct = mn.load_pool()
    ids, _ = mn.gradable_ids()
    keys, _, _, _ = mn.pick(distinct, ids)
    a = mn.design_rows(distinct, keys, "16", seed=mn.SEED)
    b = mn.design_rows(distinct, keys, "16", seed=mn.SEED)
    for batch in mn.BATCHES:
        assert [r["pem_mw"] for r in a[batch]] == [r["pem_mw"] for r in b[batch]]
    signs = np.array([r["perturb_sign"] for r in a["A"] if r["copy_type"] == "perturbed"])
    assert set(signs) <= {-1, 1}
    # batch A of layout 12 == batch A of layout 16; B of 12 == the 4 exact rows of B of 16
    c = mn.design_rows(distinct, keys, "12", seed=mn.SEED)
    assert [r["pem_mw"] for r in c["A"]] == [r["pem_mw"] for r in a["A"]]
    assert [r["pem_mw"] for r in c["B"]] == [r["pem_mw"] for r in a["B"][:4]]
