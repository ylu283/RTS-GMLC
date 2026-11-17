#!/usr/bin/env python3
"""Prompt 61 v1.1 — build `waves/location_contrast_E/` (9 analysis-only
6-site rows: all-six joints, matched-total reallocations, one saturation
probe) and its pre-registered covariate `H_C.csv`; NOT submitted. Zero
simulation.

Analysis-only: these rows never enter the GP's X, the HV ledger, the
holdout or the random baseline (prompt 61 section 4). `tier = "contrast"`
(contract 53-55 addendum 2026-11-17), `sobol_index` empty, `level_id` = the
row label.

Reuses `tools/make_ercot_n0.py` (prompt 53) for `load_space`, `make_rows`,
`retrofit_dict`, `columns` and the three script templates. It does NOT use
53's `build` / `readme` (hardwired to n0_E / random_E). The only runtime
change to the 53 module is a new KEY in `mk.WAVES_E` (setdefault); no module
global is assigned. The template texts are post-processed with asserted
one-hit string replacements.

Design space: the contract-2026-11-13 file `waves/design_space_E.json`,
passed explicitly so a later dated successor does not change this wave.

H_C (prompt 61 section 3): H_C(x) = sum over h in C of sum_s min(mw_s,
W_s,h), W = `data/ercot123_2019_v2/REAL_TIME_wind.csv` (2019 rows), C = the
hours where base_v3 non-PEM WIND curtailment > 1 MWh
(`extracts/base_v3/run_index_1/renewables_hourly.csv`; 4,410 h). Computed
from inputs only; no Y of this wave exists at build time.
"""
import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ERCOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ERCOT / "tools"))
import make_ercot_n0 as mk  # noqa: E402
from make_v2_waves import write  # noqa: E402

PROMPT = "61 v1.1"
WAVE = "location_contrast_E"
STAMP = "LOC_CONTRAST_E"
TIER = "contrast"
DESIGN_SPACE_1113 = ERCOT / "waves" / "design_space_E.json"   # contract 2026-11-13 (explicit)
WIND_RT = ERCOT / "data" / "ercot123_2019_v2" / "REAL_TIME_wind.csv"
BASE_RENEW = ERCOT / "extracts" / "base_v3" / "run_index_1" / "renewables_hourly.csv"
CURT_MIN_MWH = 1.0
N_C_HOURS = 4410
TOL_SUM = 1e-6

ALL6 = ("110", "140", "146", "163", "270", "274")
B120 = ("163", "270", "274")
B275 = ("110", "140", "146")

# (label, rule, kind, value, group); kind "flat" = every site at value MW,
# kind "prorata" = total value MW over the group, mw_s = T * pmax_s / sum_group pmax.
DESIGN = [
    ("P1_60", "all six at 60", "flat", 60.0, ALL6),
    ("P1_120", "all six at 120", "flat", 120.0, ALL6),
    ("P1_180", "all six at 180", "flat", 180.0, ALL6),
    ("P2_800_b120", "T 800, bus-120 only, pro rata to gen_pmax", "prorata", 800.0, B120),
    ("P2_800_b275", "T 800, bus-2/75 only, pro rata", "prorata", 800.0, B275),
    ("P2_800_all", "T 800, six pro rata", "prorata", 800.0, ALL6),
    ("P2_500_270", "T 500, site 270 alone (bus 120)", "prorata", 500.0, ("270",)),
    ("P2_500_110_140", "T 500, sites 110 + 140 (bus 2), pro rata", "prorata", 500.0, ("110", "140")),
    ("P3_1500_all", "T 1,500, six pro rata — saturation probe", "prorata", 1500.0, ALL6),
]
GROUP_BUSES = {B120: {120}, B275: {2, 75}, ("270",): {120}, ("110", "140"): {2}}

# asserted one-hit replacements on the 53 templates: (old, new, scripts it must hit)
REPLACE = [
    ("Prompt 53 v3.1", f"Prompt {PROMPT}", ("array", "collect", "submit")),
    ("random holdout (default_rng(5353); plan section 4)",
     "analysis-only location contrast (prompt 61; never in GP X / HV / holdout / baseline)",
     ("array",)),
    ("No dependency on the other E wave (n0_E / random_E): either order, or both.",
     "Analysis-only; no dependency on n0_E / random_E / methods_E.", ("submit",)),
]


# --------------------------------------------------------------------------
# design
# --------------------------------------------------------------------------
def design(space):
    """[(label, rule, total, mw[6], u[6])] in the pinned order, computed from the JSON."""
    sites, pmax = space["sites"], space["pmax"]
    assert tuple(sites) == ALL6, sites
    bus = {s["site"]: int(s["bus"]) for s in space["json"]["sites"]}
    out = []
    for label, rule, kind, val, group in DESIGN:
        if group in GROUP_BUSES:
            assert {bus[s] for s in group} == GROUP_BUSES[group], (label, group)
        mw = np.zeros(len(sites))
        u = np.zeros(len(sites))
        idx = [sites.index(s) for s in group]
        if kind == "flat":
            for j in idx:
                mw[j] = val
                u[j] = val / pmax[j]
            total = val * len(idx)
        else:
            sig = math.fsum(pmax[j] for j in idx)
            for j in idx:
                mw[j] = val * pmax[j] / sig
                u[j] = val / sig
            total = val
        assert (mw <= pmax).all() and (u <= 1.0).all(), (label, mw, pmax)
        assert abs(math.fsum(mw) - total) <= TOL_SUM, (label, math.fsum(mw), total)
        assert all(mw[j] == 0.0 for j in range(len(sites)) if j not in idx), label
        out.append((label, rule, total, mw, u))
    return out


def wave_rows(space):
    d = design(space)
    U = np.array([u for (_, _, _, _, u) in d])
    rows = mk.make_rows(U, space, TIER)
    for r, (label, _, _, mw, _) in zip(rows, d):
        r["level_id"] = label
        for j, s in enumerate(space["sites"]):
            r[f"mw_{s}"] = float(mw[j])           # exact MW (P1 rows carry 60 / 120 / 180 exactly)
        r["pem_mw"] = math.fsum(r[f"mw_{s}"] for s in space["sites"])
    return rows, d


# --------------------------------------------------------------------------
# H_C (pre-registered covariate; inputs only)
# --------------------------------------------------------------------------
def curtailed_hours(renew=BASE_RENEW):
    """[(date 'YYYY-MM-DD', period 1-24)] with base_v3 non-PEM WIND curtailment > 1 MWh."""
    r = pd.read_csv(renew)
    assert r["is_pem"].dtype == bool, r["is_pem"].dtype
    w = r[(r["unit_type"] == "WIND") & (~r["is_pem"])]
    assert len(w) == 8760 and not w.duplicated(["Date", "Hour"]).any()
    c = w[w["Curtailment"] > CURT_MIN_MWH]
    assert len(c) == N_C_HOURS, len(c)
    return list(zip(c["Date"], c["Hour"].astype(int) + 1))


def wind_on(hours, sites, wind=WIND_RT):
    """W[h, s] for the given (date, period) hours, from the 2019 rows of REAL_TIME_wind.csv."""
    w = pd.read_csv(wind, dtype={s: float for s in sites})
    w = w[w["Year"] == 2019].copy()
    assert len(w) == 8760
    w["Date"] = [f"{y:04d}-{m:02d}-{d:02d}" for y, m, d in zip(w["Year"], w["Month"], w["Day"])]
    w = w.set_index(["Date", "Period"])
    assert w.index.is_unique
    W = w.loc[hours, list(sites)].to_numpy(dtype=float)
    assert W.shape == (len(hours), len(sites)) and np.isfinite(W).all()
    return W


def h_c_table(rows, space, renew=BASE_RENEW, wind=WIND_RT):
    sites = space["sites"]
    hours = curtailed_hours(renew)
    W = wind_on(hours, sites, wind)
    out = []
    for r in rows:
        per = [math.fsum(np.minimum(r[f"mw_{s}"], W[:, j])) for j, s in enumerate(sites)]
        rec = {"index": r["index"], "level_id": r["level_id"], "total_mw": r["pem_mw"],
               "n_hours_C": len(hours), "H_C_MWh": math.fsum(per)}
        for j, s in enumerate(sites):
            rec[f"H_C_{s}"] = per[j]
        out.append(rec)
    return out


def h_c_columns(space):
    return ["index", "level_id", "total_mw", "n_hours_C", "H_C_MWh"] + [f"H_C_{s}" for s in space["sites"]]


# --------------------------------------------------------------------------
# scripts (53 templates + asserted replacements)
# --------------------------------------------------------------------------
def _post(text, kind):
    for old, new, kinds in REPLACE:
        if kind in kinds:
            assert text.count(old) == 1, (kind, old, text.count(old))
            text = text.replace(old, new)
    assert "Sobol" not in text and "holdout" not in text.replace(
        "never in GP X / HV / holdout / baseline", ""), kind
    return text


def scripts(n):
    mk.WAVES_E.setdefault(WAVE, STAMP)            # a key only; no module global is assigned
    assert mk.WAVES_E[WAVE] == STAMP
    return {f"{WAVE}_array.sh": _post(mk.array_script(WAVE, n), "array"),
            f"collect_{WAVE}.sh": _post(mk.collector_script(WAVE, n), "collect"),
            "submit_this.sh": _post(mk.submit_script(WAVE, n), "submit")}


# --------------------------------------------------------------------------
# build
# --------------------------------------------------------------------------
def build(waves=ERCOT / "waves", design_space=DESIGN_SPACE_1113, wave_d_dm=mk.WAVE_D_DM,
          renew=BASE_RENEW, wind=WIND_RT):
    space = mk.load_space(design_space, wave_d_dm)
    rows, d = wave_rows(space)
    hc = h_c_table(rows, space, renew, wind)
    wd = Path(waves) / WAVE
    wd.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows, columns=mk.columns(space)).to_csv(wd / "design_matrix.csv", index=False)
    for r in rows:
        write(wd / f"retrofit_gen_dict_{r['index']}.json",
              json.dumps(mk.retrofit_dict(r, space), indent=2) + "\n", 0o644)
    for name, text in scripts(len(rows)).items():
        write(wd / name, text)
    pd.DataFrame(hc, columns=h_c_columns(space)).to_csv(wd / "H_C.csv", index=False)
    write(wd / "README.md", readme(rows, d, hc, space), 0o644)
    return rows, hc, space


def _design_table(d, space):
    sites = space["sites"]
    head = "| # | label | rule | " + " | ".join(f"mw_{s}" for s in sites) + " | total | u |"
    out = [head, "|" + "---|" * (head.count("|") - 1)]
    for i, (label, rule, total, mw, u) in enumerate(d, 1):
        nz = sorted({round(float(x), 3) for x in u if x > 0})
        us = (f"{nz[0]:.3f}" if len(nz) == 1 else f"{min(nz):.2f}–{max(nz):.2f}")
        out.append(f"| {i} | {label} | {rule} | " + " | ".join(f"{x:.2f}" for x in mw)
                   + f" | {total:,.0f} | {us} |")
    return "\n".join(out)


def _hc_table(hc):
    out = ["| # | label | total MW | H_C (MWh) | H_C / total MW (h) |", "|---|---|---|---|---|"]
    for r in hc:
        out.append(f"| {r['index']} | {r['level_id']} | {r['total_mw']:,.2f} | {r['H_C_MWh']:,.1f} "
                   f"| {r['H_C_MWh'] / r['total_mw']:,.1f} |")
    return "\n".join(out)


def readme(rows, d, hc, space):
    n = len(rows)
    hcd = {r["level_id"]: r["H_C_MWh"] for r in hc}
    pm = dict(zip(space["sites"], space["pmax"]))
    u163 = 180.0 / pm["163"]
    cap275 = math.fsum(pm[s] for s in B275)
    u5 = [u for (lab, _, _, _, u) in d if lab == "P2_800_b275"][0].max()
    return f"""# {WAVE} — ERCOT location contrast (prompt {PROMPT}; analysis-only; NOT submitted)

Built by `tools/make_location_contrast_E.py` (zero simulation; reuses the
prompt-53 helpers in `tools/make_ercot_n0.py`). Design space
`waves/design_space_E.json` (contract {mk.CONTRACT_VERSION}, passed explicitly).
Kay submits ON CRC, after the wave commit is on `ercot/tx123`:

    cd trial_0826/ercot/waves/{WAVE} && bash submit_this.sh

`submit_this.sh` checks the branch, pulls, refuses without
`waves/GAP_DECISION.json`, `waves/smoke_v2/SMOKE_PASS`,
`waves/design_space_E.json`, the v2 data or the `.gitignore` gz line
(`extracts/{WAVE}/**/*.csv.gz`), prints the identity and `qquota`, and asks
for a literal `yes` before `qsub`. Analysis-only; no dependency on n0_E /
random_E / methods_E.

**Analysis-only.** These {n} rows never enter the GP's X, the HV ledger, the
holdout or the random baseline (prompt 61 section 4; plan sections 4, 5,
6.3, 7; 55 `base_waves = ["n0_E"]`). `tier = "{TIER}"`, `sobol_index` empty,
`level_id` = the row label.

## Design ({n} rows; `__ALL__` multi-site schema, contract section 5)

Computed in code from `design_space_E.json`: flat rows put every site at m
MW; pro-rata rows put `mw_s = T · gen_pmax_s / Σ_group gen_pmax` on the group
(`u = T / Σ_group` on the group) and exactly 0.0 elsewhere. Asserted:
`mw_s ≤ gen_pmax_s`, `Σ mw = T` to 1e-6, the group's buses. Table rounded to
0.01 MW; `design_matrix.csv` carries full float precision (read with
`float_precision="round_trip"`). The `mw_*` columns hold the exact MW (P1
rows carry 60 / 120 / 180 exactly); `u_* = PEM_fraction`; `pem_mw = Σ mw_s`
(equals `pool_objectives.pem_mw()` on the retrofit dict to 1e-9). Retrofit
dict `retrofit_gen_dict_<index>.json` = `{{"<site>": {{"PEM_bid": 40.0,
"PEM_fraction": u_s, "gen_pmax": gen_pmax_s}}}}` for every site with mw_s > 0;
exact zeros are omitted (plan section 2: 0 = absent).

{_design_table(d, space)}

Rows 7–8 are the **matched-u pair** (same total, same share of nameplate,
different bus): the design-side control for the u confound. Row 9 is the
saturation probe (Kay may drop it; default IN).

### Disclosures (prompt 61 section 2.2)

- Row 3 (P1_180) puts site 163 at {u163:.1%} of nameplate (u = {u163:.4f}).
- Row 5 (P2_800_b275) puts the bus-2/75 sites at u = {u5:.3f}.
- A bus-2/75-only row at 1,500 MW is infeasible: the group cap is
  {cap275:,.1f} MW.
- The v1 1,500-MW bus-120-only row (u 0.993 on three sites, a box corner)
  was dropped in review.

## Covariate H_C (pre-registered; computed at build, before any Y of this wave existed)

`H_C(x) = Σ_{{h∈C}} Σ_s min(mw_s, W_s,h)`, W = `data/ercot123_2019_v2/REAL_TIME_wind.csv`
(the 8,760 rows of 2019; the file's 24 rows of 2020-01-01 are not used;
`Period = Hour + 1`), C = hours with base_v3 non-PEM WIND curtailment
> {CURT_MIN_MWH:g} MWh (`extracts/base_v3/run_index_1/renewables_hourly.csv`;
{N_C_HOURS:,} h, asserted). Per-site terms and full precision in `H_C.csv`.

{_hc_table(hc)}

Ratios: H_C(P2_800_b120) / H_C(P2_800_b275) = {hcd['P2_800_b120'] / hcd['P2_800_b275']:.4f}
(section 3 predicted ≈ 1.149); H_C(P2_500_270) / H_C(P2_500_110_140) =
{hcd['P2_500_270'] / hcd['P2_500_110_140']:.4f}.

## Identity (v3)

Every run reads `--ruc_mipgap` / `--ruc_time_limit` from
`waves/GAP_DECISION.json` at RUN time (0.001 / 1200; Kay, E-D6, 2026-11-06),
prints `IDENTITY from GAP_DECISION.json: ...` into the task log (the collector
copies it to `run_index_N/identity.txt`), and refuses without the file.
SMOKE_GATE on `waves/smoke_v2/SMOKE_PASS`.

## Collector and the gz policy

`collect_{WAVE}.sh` (held on the array; email on this job only): every row
`extract_ercot.py --full` → `extracts/{WAVE}/run_index_N/` (`--full` kept:
same template, nothing in git, keeps N5 / E8 available; the section 3 reads
need only the slim tables), Prescient `runtimes.csv`, wall-clock from the
`{STAMP}_START` / `{STAMP}_END` stamps, the identity line → `identity.txt`,
then ON CRC `pool_objectives.py --run-dir`, then `COLLECTED`. The
`*.csv.gz` tables stay uncommitted (`.gitignore`:
`extracts/{WAVE}/**/*.csv.gz`; the collector aborts if one is staged).

## Budget

{n} full-year runs × 4 slots = {4 * n} slots; ≈ 170–355 core-h (6-site landing
actuals 19–39.4 core-h/run, plan AMENDMENT 2026-11-16). Storage: {n} ×
{mk.FULL_EXTRACT_MB} MB ≈ {n * mk.FULL_EXTRACT_MB} MB of `--full` extracts in $GROUP storage.

## Local checks (zero simulation)

`bash -n` on the scripts; `/opt/anaconda3/bin/python -m pytest
tests/test_make_location_contrast_E.py tests/test_make_ercot_n0.py -q`.

## Deviations

- `tier = "{TIER}"` is outside contract section 5's `{{nav, grading,
  holdout, bo}}`; admitted by the contract addendum 2026-11-17.
- The scripts are the prompt-53 templates (`make_ercot_n0.array_script` /
  `collector_script` / `submit_script`) with a `WAVES_E` key added at
  runtime and three asserted string replacements (prompt label, row
  description, dependency line). The collector copies `design_space_E.json`
  into the extract, as 53's does.
- Prompt 61 section 2.3 pins the row-description replacement text
  "... never in GP X / HV / holdout / baseline)" AND asks that the final
  script texts contain no "holdout". The two cannot both hold. The pinned
  replacement is kept; the "no holdout" check (generator and test) is
  applied to the script texts with that one pinned phrase removed, so the
  53 holdout label ("random holdout (default_rng(5353) ...)") is proven
  gone. "Sobol" is checked on the full texts.
- The array-script comment keeps the template wording "full-year 6-site
  rows"; rows 4, 5, 7 and 8 have 3, 3, 1 and 2 sites present (absent sites are
  omitted from the retrofit dict, plan section 2).

---

The section below is prompt 61 v1.1 section 3, copied VERBATIM; it is the
frozen pre-registration of this wave.

{PREREG}"""


PREREG = r"""## 3. Pre-registered reads (FROZEN with the wave commit; copied verbatim into the wave README)

**Seen at freeze (11-17):** wave-D rows 1–18 and base_v3 (all pool ids);
`analysis/noise_v3/ercot_noise.json` (rulers; `all_exact_zero = True`;
plan §1.2 READABLE → cost seat E1, E3 secondary); `waves/n0_E/LANDING.md`
and plan AMENDMENT 2026-11-16 (R values). No `location_contrast_E`
value existed. The bar form below is justified by the 52 null
population, not by any contrast value.

**Notation.** b = `base_v3:1`; singles s(m) = `location_oat_v2` row with
`oat_site = s, level_id = L<m>`; J(m) = P1 row at m; all objectives
minimized; Δ_j(x) = y_j(x) − y_j(b) (signed, objective units); relief
R(x) = −Δ_V1(x).

**Bar per objective j** (from `per_candidate.<j>.perturbed_delta_signed`,
EXCLUDING structural-zero pairs: a perturbed copy whose model input is
identical to its exact copy — design D2, site 206, where the wind
availability never exceeds the 899.9 MW PEM capacity (max 895.48 MW in
`REAL_TIME_wind.csv`), so ±0.1 % on the capacity changes nothing; assert
by comparing the two runs' input md5, and exclude; 6 values δ_ij remain
at 5ca9650 — noise memo `debug/noise-assessment-2026-11-17.md` finding
2): `σ̂_j = sqrt(mean δ_ij²)`, `B_j = max(3·σ̂_j, max_i |δ_ij|)` (with
D2 excluded V1 ≈ 16.2k MWh; E1 ≈ $2.38M; recompute R4 / N1 in code and
print them). A two-run contrast
is READABLE iff `|Δ| ≥ B_j`; for E1/E3 it must also exceed `G_a + G_b`
(`G_run_usd` of the two runs; label GAP-READABLE / WITHIN GAP BOUND —
G_run is an evidence column, never a verdict). If `B_j = 0` (R1; any id
in `ruler_zero`) the objective is reported as an exact value with no
read. `exact_pooled_sd` is a guard: if > 0 for any objective, STOP and
report. No multiplicity correction; the reads are descriptive and no
campaign decision depends on them. The ruler is transferred from the
52 designs (off-slate + nuclear, n = 8, heteroscedastic) — disclosed.

**Interaction (all objectives):** `A_j(m) = Σ_s Δ_j(s(m))`, `I_j(m) =
Δ_j(J(m)) − A_j(m) = y_J − Σ_s y_s + 5·y_b`, ruler `r_I,j = 4·σ̂_j`
(weights 1 + 6 + 25 on per-run chatter σ̂²/2); for E1/E3 the gap bound
is `G_J + Σ_s G_s + 5·G_b` (expected unreadable; stated in advance).
Report I_j in units and as I_j / r_I,j; never a ratio for j ≠ V1.

**Interaction, V1 only:** headline `g(m) = (Σ_s R(s(m)) − R(J(m))) /
R(J(m))` (RTS-screening convention) and secondary `I_rel(m) = (Σ_s R −
R_J) / Σ_s R` (RTS pair-grid convention, ≤ +0.22 there). Positive =
sub-additive. Guard: `R(J) ≥ 3·r_I,V1`, else UNRESOLVED. Reads at each
m: SUB-ADDITIVE iff `g ≥ 0.10` and `(ΣR − R_J) ≥ 2·r_I`;
SUPER-ADDITIVE iff `g ≤ −0.10` and `(ΣR − R_J) ≤ −2·r_I`; ADDITIVE
WITHIN 10 % iff `|g| < 0.10` at all three levels with the guard passed;
UNRESOLVED otherwise. Prediction stated in advance (offline pool model):
g ≈ 0.07 / 0.12 / 0.18 at 60 / 120 / 180.

**Covariate H_C (pre-registered, computed before any Y):** `H_C(x) =
Σ_{h∈C} Σ_s min(mw_s, W_s,h)` with W = `REAL_TIME_wind.csv` (2019) and
C = hours with base_v3 non-PEM WIND curtailment > 1 MWh
(`renewables_hourly.csv`; 4,410 h). Predicted ratios: H_C(b120)/H_C(b275)
at 800 ≈ 1.149; H_C(all)/H_C(b120) — not used (row dropped).

**Location at fixed total (V1, N4; N1 chatter-limited):** raw
`Δ_loc,j = y_j(row 4) − y_j(row 5)` and `y_j(row 7) − y_j(row 8)` and
each 800 row vs row 6. Efficiency `e(x) = R(x)/H_C(x)`. LOCATION EFFECT
iff `|R_a − R_b · H_C,a / H_C,b| ≥ B_V1`; a raw `|Δ_loc| ≥ B_V1` that the
H_C scaling explains is a COMPOSITION effect (host availability /
saturation), not location. The matched-u pair (rows 7–8) is the
design-side check: predicted profile-only difference ≈ 9 rulers in
the pool model; if `|R_7 − R_8 · H_C,7/H_C,8| < B_V1` the one-location
reading stands directly. Same reads for N4 (L252 hours ≥ 99 %, ruler
8.5) as the pocket-congestion read; N1 (all 255 lines, ruler 15, max
perturbed |Δ| 65, wave-D range −63…+102 with no trend) is reported
against `B_N1` and labelled chatter-limited. **Physics prediction:** no
residual location effect for V1 / N4 after H_C scaling; E1 contrasts
WITHIN GAP BOUND at 800 (pair bound ≈ $37–50M); R4 unreadable. A
contradiction is a finding, not an error.

**Saturation probe (row 9):** relief and e(x) at 1,500 MW vs the 4.87
TWh behind-cut pool; descriptive only.

**Scope sentence for the paper (conditional, fixed now):** "On ERCOT we
did not run pair grids. We screened location one site at a time (six
slate wind sites × 60/120/180 MW, identity v3) and tested it directly
with nine runs at 360–1,500 MW total: three all-six joint runs, five
matched-total reallocations (one pair matched on share of nameplate)
and one saturation probe. Network data place all six sites behind one
cut (L252), so differences at matched total are read as [composition
effects explained by host-absorbable energy | a residual location
effect of X × the ruler] (chosen per the §3 read). Per-site
curtailment inside the pocket is an LP tie (identical PTDFs; bus-120
sites 39–58 % curtailed, bus-2/75 sites 4–10 %), so only pocket and
system totals are read. ERCOT-wide location sensitivity rests on the
v1-identity 16-site screening (curtailment relief 25–397 × the v1
replicate ruler of 5,479 MWh; its cost numbers are void,
`INVALID_v1_costs.md`); site 275 (1,039 MW, 1.48 TWh curtailed) is in
the pocket but not in the slate."
"""


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.parse_args(argv)
    rows, hc, space = build()
    for r, h in zip(rows, hc):
        print(f"{r['index']} {r['level_id']:<15} " + " ".join(f"{r[f'mw_{s}']:8.2f}" for s in space["sites"])
              + f"  total {r['pem_mw']:8.2f}  H_C {h['H_C_MWh']:12.1f} MWh")


if __name__ == "__main__":
    main()
