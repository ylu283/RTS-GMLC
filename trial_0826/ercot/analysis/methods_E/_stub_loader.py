"""Prompt 55 Part A — STUB objectives loader with the contract 6.1 signature.

    load(waves, objectives=None, design_space=<waves/design_space_E.json>,
         extr=<extracts>, floors=None) -> (X_mw, U, Y, meta)

Same frames, same index (= key "<wave>:<index>"), same meta columns as
`analysis.ercot_gp.ercot_gp_loader.load` (prompt 54), but Y is SYNTHETIC: a
deterministic smooth function of U (curtailment falls with total PEM MW, cost
and starts rise, line-hours mix sites), so the machinery can run a dry round
with zero simulation. Rows are accepted only if
`extracts/<wave>/run_index_<i>/identity.txt` parses to the v3 identity
(ruc_mipgap 0.001, ruc_time_limit 1200), exactly like the real loader; a
missing file = REFUSED and counted in `meta.attrs["refused"]`.

Per-run overrides for the dry-round scenarios: an optional
`extracts/<wave>/run_index_<i>/stub_pool_row.json` with any of the keys
V1 E1 E3 R4 N1 R1 R2 suspect G_run_usd replaces the synthetic value.

This module is imported ONLY when `analysis.ercot_gp.ercot_gp_loader` is not
importable (common_E.get_loader); Part B asserts the real loader.
"""

from __future__ import annotations

import json
import os

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
EXTR = os.path.join(ROOT, "extracts")
DESIGN_SPACE = os.path.join(ROOT, "waves", "design_space_E.json")
V3 = {"ruc_mipgap": 0.001, "ruc_time_limit": 1200.0}
META_COLS = ["key", "wave", "index", "tier", "sobol_index", "identity", "G_run_usd", "R1", "R2", "suspect"]
STUB_IDS = ["V1", "E1", "E3", "R4", "N1"]


def read_identity(run_dir):
    """read_noise.read_identity verbatim (kept local: the stub must import alone)."""
    p = os.path.join(run_dir, "identity.txt")
    if not os.path.isfile(p):
        return None
    line = open(p).read().strip()
    out = {"line": line}
    for tok in line.split():
        if tok.startswith("ruc_mipgap="):
            out["ruc_mipgap"] = float(tok.split("=", 1)[1])
        elif tok.startswith("ruc_time_limit="):
            out["ruc_time_limit"] = float(tok.split("=", 1)[1])
    return out


def is_v3(ident) -> bool:
    return bool(ident and ident.get("ruc_mipgap") == V3["ruc_mipgap"]
                and ident.get("ruc_time_limit") == V3["ruc_time_limit"])


def synthetic_objectives(u: np.ndarray, gen_pmax: np.ndarray) -> dict:
    """Deterministic, smooth, with real trade-offs (curtailment vs cost/starts)."""
    u = np.asarray(u, float)
    T = float((u * gen_pmax).sum()) / 1000.0            # total PEM GW
    w = np.array([1.0, 0.8, 1.2, 0.6, 1.5, 1.8])
    v1 = 7.0e5 * np.exp(-1.2 * T) + 2.0e4 * float((u ** 2).sum())
    e1 = 2.0e9 + 2.5e7 * T + 6.0e6 * float((w * u).sum()) + 4.0e6 * float(u[0] * u[5])
    r4 = 9000.0 + 1500.0 * T + 800.0 * float(((u - 0.5) ** 2).sum())
    n1 = 1200.0 + 600.0 * float(u[3] + u[4] + u[5]) - 300.0 * float(u[0] + u[1]) + 200.0 * float(np.sin(3.0 * u[2]))
    return {"V1": v1, "E1": e1, "E3": 0.6 * e1 - 1.0e8, "R4": r4, "N1": n1,
            "R1": 0.0, "R2": 445.9 + 50.0 * T, "suspect": False, "G_run_usd": 1.2e7}


def load(waves, objectives=None, design_space=DESIGN_SPACE, extr=EXTR, floors=None, waves_dir=None):
    with open(design_space) as f:
        ds = json.load(f)
    sites = [s["site"] for s in ds["sites"]]
    gen_pmax = np.asarray([float(s["gen_pmax"]) for s in ds["sites"]], float)
    x_cols = list(ds["x_columns"])
    objectives = list(objectives) if objectives is not None else list(ds["objectives"].keys())
    waves_dir = waves_dir or os.path.join(os.path.dirname(os.path.abspath(extr)), "waves")
    rows_x, rows_y, rows_m, keys, refused = [], [], [], [], 0
    for wave in waves:
        dm = pd.read_csv(os.path.join(waves_dir, wave, "design_matrix.csv"),
                         dtype={"oat_site": str, "tier": str, "sobol_index": str})
        for _, r in dm.iterrows():
            idx = int(r["index"])
            rdir = os.path.join(extr, wave, f"run_index_{idx}")
            ident = read_identity(rdir)
            if not is_v3(ident):
                refused += 1
                continue
            if str(r["oat_site"]) == "__ALL__":
                x = np.asarray([float(r[c]) for c in x_cols], float)
            elif str(r["oat_site"]) in sites:
                x = np.zeros(len(sites))
                x[sites.index(str(r["oat_site"]))] = float(r["omega"]) * float(r["gen_pmax"])
            else:
                refused += 1
                continue
            u = x / gen_pmax
            syn = synthetic_objectives(u, gen_pmax)
            op = os.path.join(rdir, "stub_pool_row.json")
            if os.path.isfile(op):
                with open(op) as f:
                    syn.update(json.load(f))
            keys.append(f"{wave}:{idx}")
            rows_x.append(x)
            rows_y.append([float(syn[o]) for o in objectives])
            sob = r.get("sobol_index", "")
            rows_m.append({"key": keys[-1], "wave": wave, "index": idx,
                           "tier": (str(r["tier"]) if "tier" in dm.columns and pd.notna(r["tier"]) else ""),
                           "sobol_index": (int(float(sob)) if isinstance(sob, str) and sob.strip() != "" and sob != "nan"
                                           else (int(sob) if isinstance(sob, (int, np.integer)) else "")),
                           "identity": ident["line"], "G_run_usd": float(syn["G_run_usd"]),
                           "R1": float(syn["R1"]), "R2": float(syn["R2"]), "suspect": bool(syn["suspect"])})
    X = pd.DataFrame(np.asarray(rows_x, float).reshape(-1, len(sites)), columns=x_cols, index=pd.Index(keys, name="key"))
    U = X / gen_pmax
    U.columns = [c.replace("mw_", "u_") for c in x_cols]
    Y = pd.DataFrame(np.asarray(rows_y, float).reshape(-1, len(objectives)), columns=objectives, index=X.index)
    meta = pd.DataFrame(rows_m, columns=META_COLS)
    meta.index = X.index
    meta.attrs["refused"] = int(refused)
    meta.attrs["floors"] = floors
    meta.attrs["loader"] = "stub"
    return X, U, Y, meta
