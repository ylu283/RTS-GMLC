"""Prompt 54 Part A: the ERCOT GP loader (shared contract 53-55 §6.1; zero simulation).

    from analysis.ercot_gp.ercot_gp_loader import load
    X_mw, U, Y, meta = load(["n0_E"], objectives=["V1", "E1", "R4", "N1"])

Rows = every `run_index_N` under `extracts/<wave>/` for every wave in `waves`
(batch-nested waves are addressed by their pool key prefix, e.g. "noise_v3/A").
A row is REFUSED, never silently dropped, when:
- `no_overall`      the extract dir has no overall.csv (not collected);
- `not_v3`          identity.txt is missing or does not parse to
                    ruc_mipgap = 0.001 AND ruc_time_limit = 1200
                    (`analysis/noise_v3/read_noise.read_identity`);
- `site_not_in_space` a one-site row whose oat_site is not a design-space site
                    (nuclear "1", 206, 275, the base replicate).
`meta.attrs["refused"]` = {reason: [keys]} and `meta.attrs["n_refused"]` = the
total; `meta.attrs["floors"]` = the `floors` argument, unchanged.

X_mw: one-site rows (wave D, noise_v3) put pool_row's pem_mw (omega x gen_pmax,
what the PCM ran) in their site's column and 0 elsewhere; `__ALL__` rows read
the design matrix `mw_*` columns (contract §5), asserted to sum to pool_row's
pem_mw (the retrofit-dict sum). U = X_mw / gen_pmax per column (plan §2),
before the GP's own standardization.

Y: `objectives` (default: the design-space JSON objective keys, JSON order),
values from `pool_objectives.pool_row(key)` on the committed slim tables
(never pool_full_metrics.json). Guardrails R1 / R2, G_run_usd and SUSPECT ride
in `meta`, never in Y. SUSPECT = not (S1 and S2 and S3a), S3a = nuclear units
1 and 93 have 0 starts on a non-nuclear design (plan §1.2). S3b (equal starts
across exact replicates) is a cross-run check and is not evaluated per row.

Index of all four frames = the pool key "<wave>:<index>", in wave order then
run index.
"""
import json
import os
import re
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ERCOT = os.path.abspath(os.path.join(HERE, "..", ".."))
if ERCOT not in sys.path:
    sys.path.insert(0, ERCOT)
import pool_objectives as po  # noqa: E402
from analysis.noise_v3.read_noise import read_identity  # noqa: E402

EXTR = po.EXTR
WAVES = po.WAVES
DESIGN_SPACE = os.path.join(WAVES, "design_space_E.json")
V3 = {"ruc_mipgap": 0.001, "ruc_time_limit": 1200.0}
META_COLS = ["key", "wave", "index", "tier", "sobol_index", "identity",
             "G_run_usd", "R1", "R2", "suspect"]
REFUSE_REASONS = ("no_overall", "not_v3", "site_not_in_space")
GEN_PMAX_TOL = 1e-6


def read_design_space(path=DESIGN_SPACE):
    if not os.path.isfile(path):
        raise FileNotFoundError(
            f"{path}: design_space_E.json is prompt 53's first commit "
            "(contract §3); read it with `git show ercot/53-design-space:"
            "trial_0826/ercot/waves/design_space_E.json` or pass design_space=")
    with open(path) as f:
        ds = json.load(f)
    cols = ds["x_columns"]
    assert cols == [f"mw_{s['site']}" for s in ds["sites"]], "x_columns != sites order"
    assert np.allclose(ds["bounds_mw_hi"], [s["gen_pmax"] for s in ds["sites"]],
                       rtol=0, atol=GEN_PMAX_TOL), "bounds_mw_hi != gen_pmax"
    assert all(v == 0 for v in ds["bounds_mw_lo"]), "bounds_mw_lo must be 0 (plan §2)"
    return ds


def is_v3(ident):
    if ident is None:
        return False
    return all(k in ident and abs(ident[k] - v) <= 1e-12 * max(1.0, v)
               for k, v in V3.items())


def run_indices(wave, extr=EXTR):
    """Sorted N of every run_index_N under extracts/<wave>/."""
    d = os.path.join(extr, wave)
    if not os.path.isdir(d):
        raise FileNotFoundError(f"{d}: no extracts for wave {wave!r}")
    out = []
    for name in os.listdir(d):
        m = re.fullmatch(r"run_index_(\d+)", name)
        if m and os.path.isdir(os.path.join(d, name)):
            out.append(int(m.group(1)))
    return sorted(out)


def design_matrix_exact(wave, waves_dir=WAVES):
    """pool_objectives.design_matrix with round-trip float parsing: pandas' default
    C parser can drop the last ulp, and mw_* are written at full precision."""
    return pd.read_csv(os.path.join(waves_dir, wave, "design_matrix.csv"),
                       dtype={"oat_site": str, "replicate_of": str, "unit_type": str,
                              "tier": str},
                       float_precision="round_trip", keep_default_na=True)


def _blank(v):
    return "" if v is None or (isinstance(v, float) and np.isnan(v)) else v


def _design_extras(dm, idx, cols):
    """tier / sobol_index / mw_* from the design matrix row (multi-site waves)."""
    r = dm[dm["index"].astype(int) == int(idx)]
    if len(r) != 1:
        raise KeyError(f"index {idx} not in design_matrix ({len(r)} rows)")
    r = r.iloc[0]
    tier = _blank(r["tier"]) if "tier" in r.index else ""
    sob = _blank(r["sobol_index"]) if "sobol_index" in r.index else ""
    sob = int(float(sob)) if sob != "" else ""
    mw = ({c: float(r[c]) for c in cols} if all(c in r.index for c in cols) else None)
    return str(tier), sob, mw


def suspect_flag(row):
    s3a = bool(row["is_nuclear_design"]) or (
        float(row["D3_gen1_starts"]) == 0.0 and float(row["D3_gen93_starts"]) == 0.0)
    return not (bool(row["S1_ok"]) and bool(row["S2_ok"]) and s3a)


def load(waves, objectives=None, design_space=DESIGN_SPACE, extr=EXTR, floors=None,
         waves_dir=WAVES, data_dir=po.DATA, defs=None):
    """Contract §6.1. Returns (X_mw, U, Y, meta), all indexed by pool key."""
    ds = read_design_space(design_space)
    cols = list(ds["x_columns"])
    pmax = pd.Series([float(s["gen_pmax"]) for s in ds["sites"]], index=cols)
    site_col = {str(s["site"]): f"mw_{s['site']}" for s in ds["sites"]}
    objectives = list(objectives) if objectives is not None else list(ds["objectives"])
    defs = defs or po.load_defs()

    refused = {r: [] for r in REFUSE_REASONS}
    xs, ys, ms = [], [], []
    for wave in waves:
        dm = design_matrix_exact(wave, waves_dir)
        for idx in run_indices(wave, extr):
            key = f"{wave}:{idx}"
            d = po.run_dir(key, extr)
            if not os.path.isfile(os.path.join(d, "overall.csv")):
                refused["no_overall"].append(key)
                continue
            ident = read_identity(d)
            if not is_v3(ident):
                refused["not_v3"].append(key)
                continue
            drow = po.design_row(wave, idx, waves_dir)
            site = drow["site"]
            if site != "__ALL__" and site not in site_col:
                refused["site_not_in_space"].append(key)
                continue
            row = po.pool_row(key, extr=extr, waves=waves_dir, data_dir=data_dir,
                              defs=defs, drow=drow, d=d)
            tier, sob, mw = _design_extras(dm, idx, cols)
            if site == "__ALL__":
                assert mw is not None, f"{key}: __ALL__ row without mw_* columns"
                tot = sum(mw.values())
                assert abs(tot - row["pem_mw"]) <= 1e-6 * max(1.0, tot), (
                    f"{key}: sum mw_* {tot} != retrofit-dict pem_mw {row['pem_mw']}")
                x = mw
            else:
                gp_ds = float(pmax[site_col[site]])
                assert abs(float(drow["gen_pmax"]) - gp_ds) <= GEN_PMAX_TOL, (
                    f"{key}: gen_pmax {drow['gen_pmax']} != design space {gp_ds}")
                x = {c: 0.0 for c in cols}
                x[site_col[site]] = float(row["pem_mw"])
            for c in cols:
                assert -1e-9 <= x[c] <= float(pmax[c]) + 1e-6, f"{key}: {c}={x[c]} outside box"
            xs.append({"key": key, **x})
            ys.append({"key": key, **{o: float(row[o]) for o in objectives}})
            ms.append({"key": key, "wave": wave, "index": idx, "tier": tier,
                       "sobol_index": sob, "identity": "v3",
                       "G_run_usd": float(row["G_run_usd"]), "R1": float(row["R1"]),
                       "R2": float(row["R2"]), "suspect": suspect_flag(row)})

    X_mw = pd.DataFrame(xs, columns=["key"] + cols).set_index("key")
    Y = pd.DataFrame(ys, columns=["key"] + objectives).set_index("key")
    meta = pd.DataFrame(ms, columns=META_COLS).set_index("key", drop=False)
    meta.index.name = "key"
    U = X_mw.div(pmax, axis=1)
    meta.attrs["refused"] = refused
    meta.attrs["n_refused"] = int(sum(len(v) for v in refused.values()))
    meta.attrs["floors"] = floors
    meta.attrs["design_space"] = os.path.abspath(design_space)
    meta.attrs["contract_version"] = ds.get("contract_version")
    return X_mw, U, Y, meta
