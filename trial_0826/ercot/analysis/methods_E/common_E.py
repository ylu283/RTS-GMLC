"""Prompt 55 — shared plumbing for analysis/methods_E (paths, config, design space,
objective loader, exact hypervolume).

Root = `trial_0826/ercot` (holds waves/, extracts/, analysis/). Override with
`ERCOT_ROOT` (the tests and the dry round point it at a scratch copy).

Imports, in this order of preference, each recorded in the ledger:
  * objectives loader: `analysis.ercot_gp.ercot_gp_loader.load` (prompt 54,
    contract 6.1) behind try/except ImportError -> `_stub_loader.load` (same
    signature, synthetic Y). Part B asserts the real one (`assert_real_loader`).
  * committed configs: `analysis/ercot_gp/committed_configs.json` (54 Part B)
    else `_stub_committed_configs.json`. Part B asserts the real one.
  * exact HV: `bogp.mobo.pareto.hypervolume_exact` (M-general recursive sweep);
    `bogp.mobo.pareto.hypervolume` (Monte-Carlo at M >= 3) is NEVER imported.
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
_OWN_ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))        # trial_0826/ercot
_BOGP_DEFAULT = "/Users/yilu/Documents/GitHub/bo-gp-qparego"


def bogp_path() -> str:
    return os.environ.get("BOGP_PATH") or os.environ.get("BOGP_CLONE") or _BOGP_DEFAULT


def pin_bogp() -> str:
    """Put the bo-gp-qparego worktree FIRST on sys.path and refuse a `bogp` that
    was already imported from anywhere else (the editable feat/pt-system install
    has no hypervolume_exact / qparego — contract 1)."""
    p = bogp_path()
    if p not in sys.path or sys.path[0] != p:
        if p in sys.path:
            sys.path.remove(p)
        sys.path.insert(0, p)
    m = sys.modules.get("bogp")
    if m is not None and not os.path.abspath(m.__file__).startswith(os.path.abspath(p)):
        raise ImportError(f"a foreign bogp is already imported from {m.__file__}; expected {p} "
                          "(never import from the editable bo-gp install — set BOGP_PATH / import common_E first)")
    return p


pin_bogp()


def ercot_root() -> str:
    return os.environ.get("ERCOT_ROOT") or _OWN_ROOT


def repo_root(root: str) -> str:
    return os.path.abspath(os.path.join(root, "..", ".."))


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


# --------------------------------------------------------------------------- #
# config
# --------------------------------------------------------------------------- #

def config_path(root: str | None = None) -> str:
    return os.path.join(root or ercot_root(), "analysis", "methods_E", "arms_E.json")


def load_config(root: str | None = None) -> dict:
    with open(config_path(root)) as f:
        cfg = json.load(f)
    assert cfg["campaign"] == "methods_E" and cfg["q"] == 8 and cfg["stop_rule"] == "record_only", cfg["campaign"]
    return cfg


def arm_cfg(cfg: dict, arm: str) -> dict:
    if arm not in cfg["arms"]:
        raise SystemExit(f"unknown arm {arm!r}; choose from {list(cfg['arms'])}")
    return cfg["arms"][arm]


def lane_dir(root: str, cfg: dict, arm: str, seed: int) -> str:
    a = arm_cfg(cfg, arm)
    assert seed in a["seed_ids"], f"seed_id {seed} not in {a['seed_ids']} (arm {arm})"
    return os.path.join(root, a["lane_dir_pattern"].format(seed=seed))


def round_wave(cfg: dict, arm: str, seed: int, k: int) -> str:
    return arm_cfg(cfg, arm)["round_wave_pattern"].format(seed=seed, k=k)


def acq_seed(cfg: dict, seed_id: int, k: int) -> int:
    return int(cfg["acq_seed_base"] + 100 * seed_id + k)


# --------------------------------------------------------------------------- #
# design space (53 owns the file; we only read it)
# --------------------------------------------------------------------------- #

class DesignSpace:
    def __init__(self, path: str):
        with open(path) as f:
            d = json.load(f)
        self.raw = d
        self.path = path
        self.sites = [s["site"] for s in d["sites"]]
        self.gen_pmax = np.asarray([float(s["gen_pmax"]) for s in d["sites"]], float)
        self.bus = [s["bus"] for s in d["sites"]]
        self.unit_type = [s["unit_type"] for s in d["sites"]]
        self.x_columns = list(d["x_columns"])
        self.u_columns = [c.replace("mw_", "u_") for c in self.x_columns]
        self.lo = np.asarray(d["bounds_mw_lo"], float)
        self.hi = np.asarray(d["bounds_mw_hi"], float)
        self.bid = float(d["bid"])
        self.objectives_json = list(d["objectives"].keys())
        self.d = len(self.sites)
        assert self.x_columns == [f"mw_{s}" for s in self.sites], (self.x_columns, self.sites)
        assert np.allclose(self.hi, self.gen_pmax, rtol=0, atol=1e-9) and np.all(self.lo == 0)

    def u_to_mw(self, U):
        U = np.asarray(U, float)
        assert U.shape[-1] == self.d and np.all(U >= 0) and np.all(U <= 1 + 1e-12), "u outside [0, 1]"
        return np.clip(U, 0.0, 1.0) * self.gen_pmax

    def mw_to_u(self, X):
        X = np.asarray(X, float)
        assert X.shape[-1] == self.d
        return X / self.gen_pmax


def design_space_path(root: str, cfg: dict) -> str:
    return os.path.join(root, cfg["design_space"])


def load_design_space(root: str, cfg: dict) -> DesignSpace:
    return DesignSpace(design_space_path(root, cfg))


# --------------------------------------------------------------------------- #
# committed configs (54 Part B) with the Part A stub
# --------------------------------------------------------------------------- #

def committed_configs(root: str, cfg: dict) -> tuple[dict, str]:
    """(configs dict, source) with source in {'real', 'stub'}."""
    p = os.path.join(root, cfg["committed_configs"])
    if os.path.isfile(p):
        with open(p) as f:
            return json.load(f), "real"
    with open(os.path.join(HERE, "_stub_committed_configs.json")) as f:
        return json.load(f), "stub"


def n0_tier(configs: dict, provisional: int | None = None) -> int:
    """E-D7 nav tier. `provisional` (arms_E.json "n0_tier_provisional", prompt 66 emulator
    only) is used ONLY while E-D7_decided is null; a decided E-D7 always wins."""
    t = configs.get("E-D7_decided")
    if t is None and provisional is not None:
        t = provisional
    assert t in (32, 48), f"E-D7_decided must be 32 or 48 (got {t!r}); the nav tier is undecided"
    return int(t)


def gp_cfg_and_floor(configs: dict, objectives: list[str]) -> tuple[list[tuple], np.ndarray]:
    cfgs, floors = [], []
    for o in objectives:
        c = configs["objectives"][o]
        cfgs.append(tuple(c["cfg"]))
        f = float(c["floor"])
        floors.append(f if f > 0 else 1e-9)      # plan 3: exact sd if > 0 else inferred-only 1e-9
    return cfgs, np.asarray(floors, float)


def gp_fitters(configs: dict, objectives: list[str]) -> list[dict]:
    """Per objective, the fit definition from committed_configs (prompt 54 AMENDMENT 2026-11-24b): a value starting
    with "v2" -> {"def": "v2", "sigma_c": <committed sigma_c>}; anything else or missing -> {"def": "house"}."""
    out = []
    for o in objectives:
        c = configs["objectives"][o]
        fd = str(c.get("fit_definition") or "house")
        out.append({"def": "v2", "sigma_c": float(c.get("sigma_c", 0.0)), "source": fd} if fd.startswith("v2")
                   else {"def": "house", "source": fd})
    return out


# --------------------------------------------------------------------------- #
# objectives loader (contract 6.1) with the Part A stub
# --------------------------------------------------------------------------- #

def _import_loader(root: str):
    if root not in sys.path:
        sys.path.insert(0, root)
    try:
        from analysis.ercot_gp import ercot_gp_loader as _mod  # type: ignore
        if not os.path.abspath(_mod.__file__).startswith(os.path.abspath(root)):
            raise ImportError(f"ercot_gp_loader resolved outside root ({_mod.__file__}); a scratch root uses the stub")
        return _mod.load, "real"
    except ImportError:
        if HERE not in sys.path:
            sys.path.insert(0, HERE)
        from _stub_loader import load as _load  # type: ignore
        return _load, "stub"


def get_loader(root: str | None = None):
    """(load callable, source) — source in {'real', 'stub'}."""
    return _import_loader(root or ercot_root())


def assert_real_loader(root: str | None = None) -> None:
    _, src = get_loader(root)
    assert src == "real", "Part B requires analysis.ercot_gp.ercot_gp_loader (54); the stub is active"


# --------------------------------------------------------------------------- #
# exact hypervolume (bogp.mobo.pareto.hypervolume_exact; M-general)
# --------------------------------------------------------------------------- #

def _import_hv():
    pin_bogp()
    from bogp.mobo.pareto import hypervolume_exact as _hv  # the exact one; never `hypervolume`
    return _hv


hypervolume_exact = None


def hv_exact(Y, ref) -> float:
    """Exact HV (minimisation) of the rows of Y strictly below ref, any M."""
    global hypervolume_exact
    if hypervolume_exact is None:
        hypervolume_exact = _import_hv()
    Y = np.atleast_2d(np.asarray(Y, float))
    if len(Y) == 0:
        return 0.0
    return float(hypervolume_exact(Y, np.asarray(ref, float)))


def bogp_sha() -> str:
    import subprocess
    p = bogp_path()
    try:
        return subprocess.run(["git", "-C", p, "rev-parse", "HEAD"], capture_output=True, text=True,
                              check=True).stdout.strip()
    except Exception:  # noqa: BLE001
        return "unknown"
