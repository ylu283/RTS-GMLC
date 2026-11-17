"""Prompt 63 v1 Part B tests for tools/make_noise_seed_E.py (waves/noise_seed_E).

Run:  cd trial_0826/ercot && /opt/anaconda3/bin/python -m pytest \
          tests/test_make_noise_seed_E.py tests/test_make_ercot_n0.py -q
(the second file in the same process guards the runtime WAVES_E key, prompt 61 section 2.3).

Checks: the X-only quantile pick (recomputed independently), 18 rows in the pinned
order, X and pem_mw equal to n0_E bit-for-bit and to pool_objectives.pem_mw(), dict md5
== n0_E's, the seed / ruc_threads columns, the Seed / Threads / NSLOTS block of the array
(run in bash), the wrapper accepting Seed and refusing MIPGap / TimeLimit (its own
build_options, executed with a stub multi_PEM_PCM), the GAP_DECISION refusal of the array
and of submit_this.sh, the three qsub groups, no "Sobol" / "holdout" text, the .gitignore
line, committed wave == fresh build.
"""
import ast
import hashlib
import json
import os
import subprocess
import sys
import types
from argparse import ArgumentParser
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ERCOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ERCOT / "tools"))
sys.path.insert(0, str(ERCOT))
import make_noise_seed_E as ns  # noqa: E402
import make_ercot_n0 as mk  # noqa: E402
import pool_objectives as po  # noqa: E402

WAVES = ERCOT / "waves"
W = ns.WAVE
SCRIPTS = (f"{W}_array.sh", f"collect_{W}.sh", "submit_this.sh")


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    waves = tmp_path_factory.mktemp("waves")
    rows, picks, space = ns.build(waves=waves)
    return waves, rows, picks, space


def _dm(path):
    return pd.read_csv(path, dtype={"oat_site": str, "tier": str, "replicate_of": str, "level_id": str},
                       float_precision="round_trip")


def _md5(p):
    return hashlib.md5(Path(p).read_bytes()).hexdigest()


def test_pick_is_the_x_only_quantile_rule():
    n0 = _dm(WAVES / "n0_E" / "design_matrix.csv")
    T = n0["pem_mw"].to_numpy(float)
    want = []
    for q in (0.10, 0.37, 0.63, 0.90):
        t = np.quantile(T, q)                                  # numpy default = "linear"
        d = np.abs(T - t)
        best = min(range(48), key=lambda i: (d[i], int(n0["index"][i])))
        want.append(int(n0["index"][best]))
    picks = ns.pick_designs(ns.read_n0_x())
    assert [p["index"] for p in picks] == want == [25, 29, 46, 4]
    assert [p["label"] for p in picks] == ["q10", "q37", "q63", "q90"]
    # ties -> lower index
    dm = pd.DataFrame({"index": [1, 2, 3], "pem_mw": [10.0, 30.0, 50.0]})
    p = ns.pick_designs(dm, quantiles=(0.25,))                  # target 20: rows 1 and 2 tie at 10
    assert p[0]["index"] == 1 and p[0]["abs_dist"] == p[0]["runner_up_dist"]


def test_eighteen_rows_pinned_order_and_columns(built):
    waves, rows, picks, space = built
    dm = _dm(waves / W / "design_matrix.csv")
    assert len(dm) == 18 and list(dm["index"]) == list(range(1, 19))
    assert list(dm.columns) == mk.columns(space) + ["seed", "ruc_threads"]
    assert list(dm["seed"]) == [1, 2, 3, 4] * 4 + [0, 0]
    assert list(dm["ruc_threads"]) == [4] * 16 + [8, 1]
    assert list(dm["replicate_of"]) == [f"n0_E:{k}" for k in (25, 29, 46, 4) for _ in range(4)] + ["n0_E:29"] * 2
    assert list(dm["level_id"][:4]) == ["q10_seed1", "q10_seed2", "q10_seed3", "q10_seed4"]
    assert list(dm["level_id"][16:]) == ["q37_threads8", "q37_threads1"]
    assert set(dm["tier"]) == {"contrast"} and dm["sobol_index"].isna().all()
    assert (dm["oat_site"] == "__ALL__").all() and (dm["bid"] == 40.0).all()
    assert (dm["start_date"] == "01-01-2019").all() and (dm["num_days"] == 365).all()
    for c in ("unit_type", "bus", "omega", "gen_pmax"):
        assert dm[c].isna().all(), c


def test_x_equals_n0_bit_for_bit_and_pem_mw(built):
    waves, rows, picks, space = built
    dm = _dm(waves / W / "design_matrix.csv")
    n0 = _dm(WAVES / "n0_E" / "design_matrix.csv").set_index("index")
    xcols = [f"mw_{s}" for s in space["sites"]] + [f"u_{s}" for s in space["sites"]] + ["pem_mw"]
    for _, r in dm.iterrows():
        k = int(r["replicate_of"].split(":")[1])
        assert np.array_equal(r[xcols].to_numpy(float), n0.loc[k, xcols].to_numpy(float)), (r["index"], k)
        drow = {"site": "__ALL__"}
        assert abs(po.pem_mw(W, int(r["index"]), drow, waves=str(waves)) - r["pem_mw"]) <= 1e-9
        assert (r[[f"mw_{s}" for s in space["sites"]]].to_numpy(float) <= space["pmax"] + 1e-9).all()


def test_retrofit_dicts_are_n0_byte_copies(built):
    waves, rows, picks, space = built
    for r in rows:
        k = int(r["replicate_of"].split(":")[1])
        here, src = waves / W / f"retrofit_gen_dict_{r['index']}.json", WAVES / "n0_E" / f"retrofit_gen_dict_{k}.json"
        assert _md5(here) == _md5(src), (r["index"], k)
        assert json.loads(here.read_text()) == mk.retrofit_dict(r, space)
    assert sorted(p.name for p in (waves / W).glob("retrofit_gen_dict_*.json")) == \
        sorted(f"retrofit_gen_dict_{i}.json" for i in range(1, 19))


def _bash_n(p):
    r = subprocess.run(["bash", "-n", str(p)], capture_output=True, text=True)
    assert r.returncode == 0, (p, r.stderr)


def test_scripts_parse_and_text(built):
    waves, *_ = built
    for f in SCRIPTS:
        _bash_n(waves / W / f)
        t = (waves / W / f).read_text()
        assert "Sobol" not in t and "holdout" not in t, f
        assert "Prompt 63 v1" in t and "53 v3.1" not in t, f
    arr = (waves / W / f"{W}_array.sh").read_text()
    assert "#$ -t 1-16" in arr and "#$ -pe smp 4" in arr and "#$ -r n" in arr and "#$ -q long" in arr and "-tc" not in arr
    assert '--ruc_threads "$RUC_THREADS"' in arr and "--ruc_threads 4" not in arr
    assert '${SEED_OPT[@]+"${SEED_OPT[@]}"}' in arr and '--ruc_solver_option "Seed=$SEED"' in arr
    assert '--ruc_mipgap "$RUC_MIPGAP"' in arr and '--ruc_time_limit "$RUC_TIME_LIMIT"' in arr
    for st in ("HOST", "CPU", "GUROBI", "THREADS", "CODE", "START", "END"):
        assert f"{ns.STAMP}_{st}" in arr, st
    assert "lscpu" in arr and "gurobipy.gurobi.version()" in arr and "hostname" in arr
    coll = (waves / W / f"collect_{W}.sh").read_text()
    assert "--full" in coll and "conditions.txt" in coll and "run_ercot_pcm: index=" in coll
    assert f'extracts/{W}"' in coll and "for i in $(seq 1 18)" in coll
    sub = (waves / W / "submit_this.sh").read_text()
    for g in ("-t 1-16 -pe smp 4", "-t 17-17 -pe smp 8", "-t 18-18 -pe smp 1"):
        assert f"qsub -terse {g} {W}_array.sh" in sub, g
    assert '-hold_jid "$J1,$J2,$J3"' in sub and f"-M {mk.EMAIL} -m ea collect_{W}.sh" in sub
    assert sub.count("qsub -terse") == 4 and "read -r -p" in sub and "73 slots" in sub


def _fake_python(tmp_path):
    b = tmp_path / "pybin"
    b.mkdir(exist_ok=True)
    (b / "python").symlink_to(sys.executable)
    return b


def _row_block(waves):
    arr = (waves / W / f"{W}_array.sh").read_text()
    return arr[arr.index("# --- prompt 63: Gurobi Seed"):arr.index("# --- determinism conditions")]


@pytest.mark.parametrize("task,nslots,ok,opt", [(3, "4", True, "--ruc_solver_option Seed=3"), (17, "8", True, ""),
                                                (18, "1", True, ""), (17, "4", False, None), (5, "", False, None)])
def test_array_seed_threads_and_slot_guard(built, tmp_path, task, nslots, ok, opt):
    waves, *_ = built
    pyb = _fake_python(tmp_path)
    wd = tmp_path / f"w{task}_{nslots}"
    wd.mkdir()
    env_n = f'NSLOTS="{nslots}"\n' if nslots else "unset NSLOTS\n"
    script = (f'set -euo pipefail\nWAVE_DIR="{wd}"\nSGE_TASK_ID={task}\n{env_n}'
              f'cp "{waves / W / "design_matrix.csv"}" "$WAVE_DIR/design_matrix.csv"\n'
              + _row_block(waves) + 'echo "OPT=[${SEED_OPT[@]+${SEED_OPT[@]}}] TH=$RUC_THREADS"\n')
    r = subprocess.run(["bash", "-c", script], capture_output=True, text=True,
                       env={**os.environ, "PATH": f"{pyb}:{os.environ['PATH']}"})
    if ok:
        assert r.returncode == 0, r.stdout + r.stderr
        th = {17: "8", 18: "1"}.get(task, "4")
        assert f"OPT=[{opt}] TH={th}" in r.stdout
    else:
        assert r.returncode != 0 and f"ABORT task {task}" in r.stdout and "OPT=" not in r.stdout
        assert (wd / f"FAILED_task_{task}_slots.md").is_file()


def _gap_block(waves):
    arr = (waves / W / f"{W}_array.sh").read_text()
    return arr[arr.index("# --- identity from waves/GAP_DECISION.json"):arr.index('eval "$(python')]


def test_array_refuses_without_gap_decision(built, tmp_path):
    waves, *_ = built
    ercot = tmp_path / "ercot"
    (ercot / "waves").mkdir(parents=True)
    wave = tmp_path / "wave"
    wave.mkdir()
    pyb = _fake_python(tmp_path)
    env = {**os.environ, "PATH": f"{pyb}:{os.environ['PATH']}"}
    script = (f'set -euo pipefail\nERCOT_DIR="{ercot}"\nWAVE_DIR="{wave}"\nSGE_TASK_ID=7\n'
              + _gap_block(waves) + 'echo "REACHED_RUN"\n')
    r = subprocess.run(["bash", "-c", script], capture_output=True, text=True, env=env)
    assert r.returncode != 0 and "ABORT task 7" in r.stdout and "REACHED_RUN" not in r.stdout
    assert (wave / "FAILED_task_7_no_gap_decision.md").is_file()
    (ercot / "waves" / "GAP_DECISION.json").write_text(json.dumps({"ruc_mipgap": 0.001, "ruc_time_limit": 1200}))
    r = subprocess.run(["bash", "-c", script], capture_output=True, text=True, env=env)
    assert r.returncode == 0 and "REACHED_RUN" in r.stdout
    assert "IDENTITY from GAP_DECISION.json: ruc_mipgap=0.001 ruc_time_limit=1200.0" in r.stdout


def _fake_bin(tmp_path):
    fake = tmp_path / "bin"
    fake.mkdir()
    (fake / "git").write_text('#!/bin/bash\ncase "$*" in *"branch --show-current"*) echo ercot/tx123;; *) exit 0;; esac\n')
    (fake / "qsub").write_text('#!/bin/bash\necho "qsub must not run"; exit 99\n')
    (fake / "qquota").write_text('#!/bin/bash\necho "quota ok"\n')
    for f in fake.iterdir():
        f.chmod(0o755)
    return fake


def test_submit_refuses_without_gap_decision(built, tmp_path):
    waves, *_ = built
    fake = _fake_bin(tmp_path)
    ercot = tmp_path / "repo" / "trial_0826" / "ercot"
    wd = ercot / "waves" / W
    wd.mkdir(parents=True)
    for f in (waves / W).iterdir():
        (wd / f.name).write_text(f.read_text())

    def run(answer="no\n"):
        return subprocess.run(["bash", str(wd / "submit_this.sh")], capture_output=True, text=True,
                              env={**os.environ, "PATH": f"{fake}:{os.environ['PATH']}"}, input=answer)
    r = run()
    assert r.returncode != 0 and "GAP_DECISION.json absent" in r.stdout and "qsub must not run" not in r.stdout
    (ercot / "waves" / "GAP_DECISION.json").write_text('{"ruc_mipgap": 0.001, "ruc_time_limit": 1200}\n')
    (ercot / "waves" / "smoke_v2").mkdir()
    (ercot / "waves" / "smoke_v2" / "SMOKE_PASS").write_text("ok\n")
    (ercot / "waves" / "design_space_E.json").write_text("{}\n")
    (ercot / mk.V2_DATA_REL).mkdir(parents=True)
    (ercot / mk.V2_DATA_REL / "gen.csv").write_text("GEN UID\n")
    (ercot / "run_ercot_pcm.py").write_text("# --ruc_mipgap\n")
    r = run()
    assert r.returncode != 0 and ".gitignore gz line missing" in r.stdout, r.stdout + r.stderr
    (ercot / ".gitignore").write_text(f"{ns.GITIGNORE_LINE}\n")
    r = run()                                     # full pre-flight passes; Kay answers "no"
    assert r.returncode != 0 and "not submitted" in r.stdout and "qsub must not run" not in r.stdout, r.stdout + r.stderr
    assert "need 73 slots" in r.stdout


def _wrapper_ns(tmp_path):
    """run_ercot_pcm.parse_args / build_options executed from the file's own source with a stub
    multi_PEM_PCM (the real module imports Prescient, absent here)."""
    src = (ERCOT / "run_ercot_pcm.py").read_text()
    tree = ast.parse(src)
    fns = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in ("parse_args", "build_options")]
    assert len(fns) == 2
    g = {"os": os, "ArgumentParser": ArgumentParser, "DEFAULT_DATA_DIR": str(tmp_path), "__doc__": "x",
         "multi_PEM_PCM": types.SimpleNamespace(prescient_options={})}
    exec(compile(ast.Module(body=fns, type_ignores=[]), "run_ercot_pcm.py", "exec"), g)
    (tmp_path / "gen.csv").write_text("GEN UID\n")
    return g


def test_wrapper_accepts_seed_and_refuses_only_gap_and_time_limit(tmp_path):
    g = _wrapper_ns(tmp_path)
    base = ["--data_dir", str(tmp_path), "--ruc_threads", "4", "--ruc_time_limit", "1200", "--ruc_mipgap", "0.001"]
    o = g["build_options"](g["parse_args"](base + ["--ruc_solver_option", "Seed=3"]))
    assert o["deterministic_ruc_solver_options"] == {"TimeLimit": 1200.0, "Threads": 4, "Seed": 3}
    assert isinstance(o["deterministic_ruc_solver_options"]["Seed"], int) and o["ruc_mipgap"] == 0.001
    o = g["build_options"](g["parse_args"](base))
    assert "Seed" not in o["deterministic_ruc_solver_options"]          # Seed-0 rows: the n0_E options exactly
    for bad in ("MIPGap=0.01", "mipgap=0.01", "TimeLimit=60", "timelimit=60"):
        with pytest.raises(SystemExit, match="refused"):
            g["build_options"](g["parse_args"](base + ["--ruc_solver_option", bad]))
    src = (ERCOT / "run_ercot_pcm.py").read_text()
    assert 'if k.lower() in ("mipgap", "timelimit"):' in src and "ruc_solver_options={opts['deterministic_ruc_solver_options']}" in src


def test_gitignore_line_present_and_asserted(tmp_path):
    assert ns.GITIGNORE_LINE in (ERCOT / ".gitignore").read_text().splitlines()
    gi = tmp_path / ".gitignore"
    gi.write_text("extracts/n0_E/**/*.csv.gz\n")
    with pytest.raises(AssertionError, match="gitignore"):
        ns.build(waves=tmp_path / "w", gitignore=gi)


def test_readme_carries_part_c_verbatim_and_disclosures(built):
    waves, *_ = built
    txt = (waves / W / "README.md").read_text()
    assert ns.PART_C in txt and "B_j^seed = max(3·σ̂_c,j·√2, max|Δ_seed|)" in txt
    assert "ANALYSIS-ONLY" in txt and 'tier = "contrast"' in txt and "Hyndman–Fan type 7" in txt
    assert "| q10 (10 %)" in txt and "| 25 |" in txt and "--ruc_solver_option Seed=4" in txt
    assert "Sobol" not in txt and "holdout" not in txt
    import re
    assert not re.search(r"\d{4}-\d{2}-\d{2}T\d{2}", txt)          # no timestamp: README is deterministic


def test_waves_e_key_is_runtime_only():
    assert mk.WAVES_E.get(W) in (None, ns.STAMP)
    assert mk.PROMPT == "53 v3.1"
    assert {"n0_E": "N0_E", "random_E": "RANDOM_E"}.items() <= mk.WAVES_E.items()


def test_committed_wave_matches_builder(built):
    waves, *_ = built
    if not (WAVES / W / "design_matrix.csv").is_file():
        pytest.skip("wave not built in the tree")
    names = sorted(p.name for p in (waves / W).iterdir())
    assert names == sorted(p.name for p in (WAVES / W).iterdir() if p.name != "runs"
                           and not p.name.startswith(("FAILED", "LANDING", "landing_")))
    for n in names:
        assert (WAVES / W / n).read_text() == (waves / W / n).read_text(), n
