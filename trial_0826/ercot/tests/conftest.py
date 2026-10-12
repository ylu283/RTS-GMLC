"""Fixtures for the prompt-36 cost-fix tests.

Run in PCM_ERCOT on the CRC front-end (the egret fork ylu283/Egret@e4a244d):
    cd trial_0826/ercot && PYTHONNOUSERSITE=1 python -m pytest tests -s -q
Locally, only with a patched copy of stock egret 0.6.2 on PYTHONPATH and
ERCOT_LOCAL_PATCHED_EGRET=1 (the git-hash check is then reported, not enforced).

Env overrides: ERCOT_V2_DIR (default data/ercot123_2019_v2), ERCOT_READING (c).
"""
import os
import subprocess
import sys
from pathlib import Path

import pandas as pd
import pytest

ERCOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ERCOT / "tools"))

FORK_SHA = "e4a244d"


@pytest.fixture(scope="session")
def v1_dir():
    return ERCOT / "data" / "ercot123_2019"


@pytest.fixture(scope="session")
def v2_dir():
    return Path(os.environ.get("ERCOT_V2_DIR", ERCOT / "data" / "ercot123_2019_v2"))


@pytest.fixture(scope="session")
def reading():
    return os.environ.get("ERCOT_READING", "c")


@pytest.fixture(scope="session")
def source():
    return pd.read_csv(ERCOT / "analysis" / "cost_fix" / "source_coeffs_tx123.csv")


@pytest.fixture(scope="session")
def rts_dir():
    return ERCOT.parents[1] / "RTS_Data" / "SourceData"


def egret_identity():
    """(source carries the fork rounding, git HEAD of the egret checkout or None)."""
    import inspect

    import egret
    from egret.parsers.rts_gmlc import parser
    src = inspect.getsource(parser._read_generators)
    fork_src = "round(val*pmax, 4)" in src and "round(f[i],6)" in src
    sha = None
    try:
        sha = subprocess.run(["git", "-C", str(Path(egret.__file__).resolve().parents[1]),
                              "rev-parse", "HEAD"], capture_output=True, text=True,
                             check=True).stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    return fork_src, sha, egret.__file__


@pytest.fixture(scope="session")
def skeleton():
    """Parse a data dir's bus/branch/gen exactly as egret does (fork)."""
    from egret.parsers.rts_gmlc.parser import _create_rtsgmlc_skeleton

    cache = {}

    def _parse(d):
        d = str(d)
        if d not in cache:
            cache[d] = _create_rtsgmlc_skeleton(d)["elements"]["generator"]
        return cache[d]
    return _parse
