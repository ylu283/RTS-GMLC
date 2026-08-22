import os
import sys

CAMPAIGN_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, CAMPAIGN_DIR)

import pytest  # noqa: E402

import make_batches  # noqa: E402
import submit_array  # noqa: E402
from tiers import build_tiers  # noqa: E402


@pytest.fixture(scope="session")
def tiers():
    tiers, _ = build_tiers()
    return tiers


@pytest.fixture(scope="session")
def waves_root(tmp_path_factory):
    return str(tmp_path_factory.mktemp("waves"))


@pytest.fixture(scope="session")
def pilot_wave(waves_root):
    wave_dir = make_batches.build_pilot(waves_root)
    submit_array.generate_script(wave_dir)
    return wave_dir


@pytest.fixture(scope="session")
def screening_wave(waves_root):
    wave_dir = make_batches.build_screening(waves_root)
    submit_array.generate_script(wave_dir)
    return wave_dir


@pytest.fixture(scope="session")
def n0_wave(waves_root):
    wave_dir = make_batches.build_n0(waves_root)
    submit_array.generate_script(wave_dir)
    return wave_dir
