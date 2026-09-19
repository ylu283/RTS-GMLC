"""Tier configuration for the multi-PEM campaign — single source of truth.

Doc 14 §2.1: all top-10 curtailers + nuclear are retrofitted, grouped so
that only sites with learnable individual signal get independent (omega, B)
dimensions. A cluster shares one (omega, B) pair; each member still gets its
own physical PEM (omega x own nameplate).

d = 2 * len(TIERS) = 12 (d12 branch, 2026-08-24): pv_319 + pv_324 merged
into one `pv` tier per the screening verdict — both were sub-threshold
(4.2% / 3.9% effect share vs 5%), and the B-axis endpoints agree (319's
share is 4.4% in the low-B limit = base ranking, 4.2% at B = 40). See
waves/screening/screening_review.md.
"""

import copy
import csv
import os

import numpy as np

# Arbitrary but PERMANENT: the never-re-seed rule (doc 14 §5.1) makes this
# campaign state. Import it — no literal seeds at any call site.
SOBOL_SEED = 20260821

# Derived-bid scheme (math-log §1, PI-approved 2026-08-27): psi kg H2 per MWh
# diverted. The exact conversion number behind "20" (psi, and any
# site-specific m_VOM) is a recorded future-study item — do not silently
# change it.
PSI_KG_PER_MWH = 20.0

# Price scenarios (math-log §1.3). PI cap: rho_H2 <= 2.0 $/kg.
RHO_SCENARIOS = {"A": 1.0, "B": 1.5, "C": 2.0}   # $/kg


def derived_bid(rho_h2):
    """Truthful opportunity-cost offer B* = psi*rho_H2 - m_VOM (math-log
    §1.2; m_VOM = 0 in the current model), in $/MWh. Uniform across all
    sites INCLUDING nuclear (Kay 2026-08-27): psi and m_VOM are
    site-independent."""
    return round(PSI_KG_PER_MWH * rho_h2, 2)

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
TRIAL_DIR = os.path.dirname(THIS_DIR)
REPO_DIR = os.path.dirname(TRIAL_DIR)
GEN_CSV = os.path.join(REPO_DIR, "RTS_Data", "SourceData", "gen.csv")
TM1_STATS_CSV = os.path.join(TRIAL_DIR, "analysis", "tm1_per_site_stats.csv")
ENVIRONMENT_YML = os.path.join(TRIAL_DIR, "environment.yml")

TIERS = {
    "nuclear":  {"members": ["121_NUCLEAR_1"], "type": "thermal",
                 "omega": (0.05, 0.5), "bid": (15, 40)},
    "wind_303": {"members": ["303_WIND_1"], "type": "renewable",
                 # gen_pmax populated from gen.csv at build time — never hardcoded
                 "omega": (0.05, 0.5), "bid": (10, 40)},
    "wind_317": {"members": ["317_WIND_1"], "type": "renewable",
                 "omega": (0.05, 0.5), "bid": (10, 40)},
    "wind_122": {"members": ["122_WIND_1"], "type": "renewable",
                 "omega": (0.05, 0.5), "bid": (10, 40)},
    # merged pv tier (screening verdict): shared "PV policy" — near-identical
    # per-MW effect (1,269-1,590 MWh/MW) and CF (0.41-0.42) across all four
    "pv":       {"members": ["319_PV_1", "324_PV_1", "324_PV_2", "324_PV_3"],
                 "type": "renewable", "omega": (0.02, 0.3), "bid": (10, 40)},
    # tail mixes PV + wind: omega = union of member-type ranges
    # (doc 14: prefer generous bounds over truncation)
    "tail":     {"members": ["310_PV_2", "320_PV_1", "309_WIND_1"],
                 "type": "renewable", "omega": (0.02, 0.5), "bid": (10, 40)},
}

TIER_ORDER = list(TIERS)


def load_gen_pmax(gen_csv=GEN_CSV):
    """Return {GEN UID: PMax MW} from the RTS source data."""
    pmax = {}
    with open(gen_csv, newline="") as f:
        for row in csv.DictReader(f):
            pmax[row["GEN UID"]] = float(row["PMax MW"])
    return pmax


def load_tm1_stats(stats_csv=TM1_STATS_CSV):
    """Return {site: {"omega_max_recommended": float, "omega_oat_reference": float}},
    or None if the 15a stats CSV is absent (waves then run on fallback
    constants and are marked provisional)."""
    if not os.path.isfile(stats_csv):
        return None
    stats = {}
    with open(stats_csv, newline="") as f:
        for row in csv.DictReader(f):
            if not row.get("site"):
                continue
            stats[row["site"]] = {
                "omega_max_recommended": float(row["omega_max_recommended"]),
                "omega_oat_reference": float(row["omega_oat_reference"]),
            }
    return stats


def build_tiers(stats_csv=TM1_STATS_CSV, gen_csv=GEN_CSV):
    """Build the runtime tier config: per-member gen_pmax for renewables and
    omega upper bounds widened from 15a's omega_max_recommended.

    Returns (tiers, provisional): provisional is True when the 15a stats CSV
    is missing (configured fallback bounds are used).
    """
    tiers = copy.deepcopy(TIERS)
    pmax = load_gen_pmax(gen_csv)
    stats = load_tm1_stats(stats_csv)
    provisional = stats is None

    for name, tier in tiers.items():
        if tier["type"] == "renewable":
            missing = [m for m in tier["members"] if m not in pmax]
            assert not missing, f"tier {name}: members missing from gen.csv: {missing}"
            tier["gen_pmax"] = {m: pmax[m] for m in tier["members"]}
        if stats is not None:
            # a tier takes the max over members present in the CSV; tiers with
            # no member in the CSV (nuclear, always) keep configured bounds
            recs = [stats[m]["omega_max_recommended"] for m in tier["members"] if m in stats]
            if recs:
                lo, _ = tier["omega"]
                tier["omega"] = (lo, max(recs))
    return tiers, provisional


# --- Stage 2 (PI directive 2026-09 + Kay 09-19) -------------------------------
# This import sits BELOW everything design_tools needs from tiers (TIERS,
# derived_bid, ENVIRONMENT_YML, REPO_DIR); design_tools defines omega_grid
# above ITS tiers import — together the circular import is safe from either
# entry point.
from design_tools import omega_grid  # noqa: E402

# All six tiers share one 9-level discrete omega lattice: nuclear's 0.5 cap
# is lifted and the pv/tail 0.02 floors are gone (Kay 09-19: no feasibility
# check). Bids stay derived (B = 20*rho_H2), never searched.
# np.round(..., 10) makes every level the float of its short decimal string
# (linspace computes 0.05 + 3*0.11875 one ulp below the exact 0.40625 =
# 13/32, and pandas' fast CSV parser is itself 1-ulp lossy on the long
# repr) — so design_matrix.csv round-trips every omega bit-exactly.
STAGE2_LATTICE = np.round(omega_grid(9, 0.05, 1.0), 10)


def stage2_tiers():
    """Stage-2 tier config: build_tiers() output with every tier's omega box
    set to the full lattice span. Returns (tiers, provisional). Deepcopy —
    TIERS/build_tiers themselves are never mutated; use this dict for every
    Stage-2 wave so manifests match rows with nuclear omega > 0.5."""
    tiers, provisional = build_tiers()
    tiers = copy.deepcopy(tiers)
    for tier in tiers.values():
        tier["omega"] = (float(STAGE2_LATTICE[0]), float(STAGE2_LATTICE[-1]))
    return tiers, provisional
