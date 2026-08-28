"""Design-generation tools for the multi-PEM campaign (doc 14 §5.1).

Conventions enforced here:
- `index` starts at 1 and maps 1:1 to $SGE_TASK_ID (1-based, never 0).
- Absent tiers are encoded as NaN; omega = 0 is forbidden (it would create a
  degenerate zero-capacity PEM unit instead of omitting the site).
- Retrofit dicts use the `PEM_bid` key only — never the deprecated
  `PEM_indifference_point` alias.
"""

import hashlib
import json
import os
import subprocess
from datetime import datetime, timezone

import numpy as np
import pandas as pd
import scipy
from scipy.stats import qmc

from tiers import ENVIRONMENT_YML, REPO_DIR, TIERS, derived_bid

META_COLUMNS = ["oat_site", "anchor", "start_date", "num_days", "provisional",
                "rho_h2"]


def tier_columns(tiers):
    cols = []
    for tier_name in tiers:
        cols += [f"{tier_name}_omega", f"{tier_name}_bid"]
    return cols


def matrix_columns(tiers):
    return ["index"] + tier_columns(tiers) + META_COLUMNS


def generate_sobol(n, seed, skip=0, d=None):
    """Scrambled Sobol points in [0,1]^d.

    Uses the `seed=` kwarg verbatim: on scipy >= 1.17 the newer `rng`
    keyword produces a DIFFERENT scrambling, while `seed=` is bit-identical
    across 1.16.3 (local) and 1.18.0 (pinned on CRC). `skip` fast-forwards the engine so a
    later wave CONTINUES the same sequence (doc 14 §5.1: never re-seed).
    scipy's UserWarning when n is not a power of 2 is deliberately not
    suppressed.
    """
    if d is None:
        d = 2 * len(TIERS)
    engine = qmc.Sobol(d, scramble=True, seed=seed)
    if skip:
        engine.fast_forward(skip)
    return engine.random(n)


def make_row(tiers, tier_values, index, num_days=366, start_date="01-01-2020",
             anchor=False, provisional=False, oat_site=None, external=False,
             rho_h2=None):
    """One design-matrix row. `tier_values` maps tier -> (omega, bid) for the
    tiers present in the design; absent tiers become NaN. `external` is only
    for external-anchor rows (index outside 1..N, separate CSV).

    v3 derived-bid mode (math-log §1-2): with `rho_h2` set, `tier_values`
    maps tier -> omega ONLY — every active tier's bid is forced to
    `derived_bid(rho_h2)` and the scenario is recorded in the `rho_h2`
    column. Caller-supplied bids are an error in this mode. With
    rho_h2=None (old waves), behavior is exactly as before and the
    `rho_h2` column is NaN."""
    if not external:
        assert index >= 1, "index maps 1:1 to $SGE_TASK_ID, which is 1-based"
    row = {"index": int(index)}
    tier_values = tier_values or {}
    unknown = set(tier_values) - set(tiers)
    assert not unknown, f"unknown tiers in design row: {sorted(unknown)}"
    for tier_name in tiers:
        if tier_name in tier_values:
            if rho_h2 is not None:
                omega = tier_values[tier_name]
                assert np.isscalar(omega), (
                    f"tier {tier_name}, index {index}: with rho_h2 set, bids are "
                    "DERIVED (B = 20*rho_h2, math-log §1.2) — pass omega only, "
                    "never an (omega, bid) pair"
                )
                bid = derived_bid(rho_h2)
            else:
                omega, bid = tier_values[tier_name]
            assert omega > 0, (
                f"omega=0 is forbidden (tier {tier_name}, index {index}): encode an "
                "absent tier as NaN — omega=0 would create a degenerate zero-capacity PEM unit"
            )
            row[f"{tier_name}_omega"] = float(omega)
            row[f"{tier_name}_bid"] = float(bid)
        else:
            row[f"{tier_name}_omega"] = float("nan")
            row[f"{tier_name}_bid"] = float("nan")
    row["oat_site"] = oat_site if oat_site is not None else float("nan")
    row["anchor"] = bool(anchor)
    row["start_date"] = str(start_date)
    row["num_days"] = int(num_days)
    row["provisional"] = bool(provisional)
    row["rho_h2"] = float(rho_h2) if rho_h2 is not None else float("nan")
    return row


def rows_to_matrix(rows, tiers):
    return pd.DataFrame(rows, columns=matrix_columns(tiers))


def to_design_matrix(unit_points, tiers, start_index=1, num_days=366,
                     start_date="01-01-2020", anchor=False, provisional=False,
                     rho_h2=None):
    """Affine-map unit hypercube points to physical tier ranges.

    The scalar kwargs apply to every row of this call; multi-horizon waves
    are built from multiple calls concatenated with continued `start_index`.
    Column order per point (rho_h2=None): (omega, bid) per tier, in tier
    order. v3 derived-bid mode (rho_h2 set, math-log §2): points are omega
    ONLY — one column per tier, in tier order (d = len(tiers)) — and every
    tier's bid is filled with derived_bid(rho_h2).
    """
    unit_points = np.asarray(unit_points, dtype=float)
    d = len(tiers) if rho_h2 is not None else 2 * len(tiers)
    assert unit_points.ndim == 2 and unit_points.shape[1] == d, (
        f"expected unit points of shape (n, {d}), got {unit_points.shape}"
    )
    assert np.all((unit_points >= 0.0) & (unit_points <= 1.0)), "unit points must lie in [0,1]^d"
    rows = []
    for i, point in enumerate(unit_points):
        tier_values = {}
        for j, (tier_name, tier) in enumerate(tiers.items()):
            omega_lo, omega_hi = tier["omega"]
            if rho_h2 is not None:
                tier_values[tier_name] = omega_lo + point[j] * (omega_hi - omega_lo)
            else:
                bid_lo, bid_hi = tier["bid"]
                tier_values[tier_name] = (
                    omega_lo + point[2 * j] * (omega_hi - omega_lo),
                    bid_lo + point[2 * j + 1] * (bid_hi - bid_lo),
                )
        rows.append(make_row(tiers, tier_values, index=start_index + i,
                             num_days=num_days, start_date=start_date,
                             anchor=anchor, provisional=provisional,
                             rho_h2=rho_h2))
    return rows_to_matrix(rows, tiers)


def omega_grid(levels, lo, hi):
    """Evenly spaced omega levels over [lo, hi] INCLUDING both endpoints
    (contour grid axes and OAT sweep levels — shared so the §4.3 interaction
    index gets its f(omega, 0) margins from the sweeps at zero extra cost)."""
    assert levels >= 2, "a grid needs both endpoints: levels >= 2"
    assert lo > 0, "omega=0 is forbidden (absent tiers are NaN, never omega=0)"
    assert hi > lo, f"empty omega range: [{lo}, {hi}]"
    return np.linspace(lo, hi, levels)


def _is_oat_row(row):
    return isinstance(row["oat_site"], str) and row["oat_site"] != ""


def expand_to_retrofit_dict(row, tiers):
    """The retrofit_gen_dict for one non-OAT design row: NaN tiers are
    skipped; clusters expand to per-member entries sharing (omega, B);
    renewables carry per-member gen_pmax."""
    assert not _is_oat_row(row), (
        "OAT rows carry their dict via single_site_entry, not tier expansion"
    )
    out = {}
    for tier_name, tier in tiers.items():
        omega = row[f"{tier_name}_omega"]
        bid = row[f"{tier_name}_bid"]
        if pd.isna(omega):
            assert pd.isna(bid), f"tier {tier_name}: omega is NaN but bid is not"
            continue
        assert omega > 0, f"omega=0 is forbidden (tier {tier_name})"
        for member in tier["members"]:
            entry = {"PEM_fraction": round(float(omega), 4), "PEM_bid": round(float(bid), 2)}
            if tier["type"] == "renewable":
                entry["gen_pmax"] = float(tier["gen_pmax"][member])
            out[member] = entry
    return out


def single_site_entry(site, omega, bid, gen_pmax=None):
    """Retrofit dict for one screening (OAT) site; gen_pmax=None for thermal."""
    assert omega > 0, f"omega=0 is forbidden (site {site})"
    entry = {"PEM_fraction": round(float(omega), 4), "PEM_bid": round(float(bid), 2)}
    if gen_pmax is not None:
        entry["gen_pmax"] = float(gen_pmax)
    return {site: entry}


def _git_info():
    sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO_DIR,
                         capture_output=True, text=True, check=True).stdout.strip()
    # tracked modifications only (-uno): the wave files being written are
    # untracked at generation time and must not trip the flag
    status = subprocess.run(["git", "status", "--porcelain", "-uno"], cwd=REPO_DIR,
                            capture_output=True, text=True, check=True).stdout
    return sha, bool(status.strip())


def _sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def write_wave(design_df, wave_dir, tiers, sobol=None, retrofit_dicts=None,
               external_anchors=None):
    """Write a self-contained wave directory: design_matrix.csv, one
    retrofit_gen_dict_<index>.json per row, manifest.json, and (optionally)
    external_anchors.csv.

    `sobol` is {"seed":..., "skip":..., "n":...} or None (null in the
    manifest) for fixed-design waves that draw no Sobol points.
    `retrofit_dicts` maps index -> dict for rows whose dict is not tier
    expansion (OAT rows); required for every OAT row.
    """
    indices = [int(i) for i in design_df["index"]]
    assert len(set(indices)) == len(indices), "duplicate indices in design matrix"
    assert min(indices) >= 1, "design-matrix indices are 1-based"

    os.makedirs(wave_dir, exist_ok=True)
    design_df.to_csv(os.path.join(wave_dir, "design_matrix.csv"), index=False)

    retrofit_dicts = retrofit_dicts or {}
    for _, row in design_df.iterrows():
        idx = int(row["index"])
        if _is_oat_row(row):
            assert idx in retrofit_dicts, f"OAT row {idx} requires an explicit retrofit dict"
            gen_dict = retrofit_dicts[idx]
        else:
            gen_dict = retrofit_dicts.get(idx) or expand_to_retrofit_dict(row, tiers)
        assert gen_dict, f"row {idx}: empty retrofit dict"
        with open(os.path.join(wave_dir, f"retrofit_gen_dict_{idx}.json"), "w") as f:
            json.dump(gen_dict, f, indent=2, sort_keys=True)
            f.write("\n")

    if external_anchors is not None:
        external_anchors.to_csv(os.path.join(wave_dir, "external_anchors.csv"), index=False)

    sha, dirty = _git_info()
    manifest = {
        "git_sha": sha,
        "dirty": dirty,
        "tiers": tiers,
        "sobol": sobol,
        "scipy_version": scipy.__version__,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "environment_yml_sha256": _sha256_of(ENVIRONMENT_YML),
        "n_rows": len(indices),
    }
    with open(os.path.join(wave_dir, "manifest.json"), "w") as f:
        json.dump(manifest, f, indent=2)
        f.write("\n")
    return wave_dir
