#!/usr/bin/env python3
"""Prompt 62 Part C — build `waves/screening_v3/` (11 single-site rows at 180 MW
under identity v3) and its pre-registered `covariates.csv`; NOT submitted.
Zero simulation.

Rows 1-10 = ranks 7-16 of `analysis/cost_fix/wave_d_selection.json` (read from
the file, not literals), each site alone at pem_mw = 180, omega = 180 /
gen_pmax, bid 40, level_id L180. Row 11 = replicate of wave-D row 3 (site 163
L180; `replicate_of = location_oat_v2:3`): its overall.csv md5 must equal wave
D's at landing (no code/data drift since 11-06). No L60 level. Analysis-only:
never in GP X / HV / holdout / baseline.

Builder: `tools/make_wave_d.build(wave="screening_v3", sites=ranks 7-16,
levels=[180.0], include_nuclear=False, unit_types=("WIND", "PV"),
readme_fn=readme, extra_rows=[replicate])` (the default-preserving refactor
dac93e3; the replicate row is passed as `extra_rows` so the array/collector
ranges cover it).

covariates.csv (per site, all 16 screened sites; computed from INPUTS only,
before any Y of this wave exists):
- tier (pre-registered, SCREENING_ERCOT.md / prompt 62 §4.5) and slate flag;
- H_C(s, 180) (prompt 61 §3): sum over h in C of min(180, W_s,h), C = hours with
  base_v3 non-PEM WIND curtailment > 1 MWh (4,410 h); W = REAL_TIME_wind.csv for
  WIND sites and REAL_TIME_solar.csv for PV sites (61 defined W for wind only;
  the PV substitution is disclosed);
- base_v3 own-site curtailment (gen_summary.csv, non-PEM row);
- DC PTDF of the site bus on the pocket lines (`pocket_lines(120)`) and on every
  base_v3 line with hours_ge_99pct > 0. bus.csv has no Ref bus, so the PTDF uses
  a load-weighted DISTRIBUTED slack (weights = mean 2019 hourly load per bus,
  REAL_TIME_load.csv); B from branch.csv reactance X; flow sign From -> To.
"""
import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ERCOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ERCOT / "tools"))
sys.path.insert(0, str(ERCOT))
import make_wave_d as mw  # noqa: E402
import pool_objectives as po  # noqa: E402

WAVE = "screening_v3"
PROMPT_TAG = "Prompt 62 Part C"
LEVEL = 180.0
RANKS = range(7, 17)
SELECTION = ERCOT / "analysis" / "cost_fix" / "wave_d_selection.json"
WAVE_D_DM = ERCOT / "waves" / mw.WAVE / "design_matrix.csv"
REPLICATE_OF = (mw.WAVE, 3)
DATA = ERCOT / mw.V2_DATA_REL
WIND_RT, SOLAR_RT, LOAD_RT = DATA / "REAL_TIME_wind.csv", DATA / "REAL_TIME_solar.csv", DATA / "REAL_TIME_load.csv"
BASE = ERCOT / "extracts" / "base_v3" / "run_index_1"
CURT_MIN_MWH, N_C_HOURS = 1.0, 4410
SATURATION_OMEGA = 0.9
TIERS = {"pocket_120": ("163", "270", "274", "275", "116"), "wind_near": ("110", "140", "146"),
         "pv_pocket": ("30", "59", "142"), "far": ("91", "205", "206", "204", "20")}
SLATE = ("163", "140", "146", "270", "110", "274")

SECTION_4_4_4_5 = """4. **Wave commit — STOP — Kay action:** `git rebase ercot/tx123`,
   report the SHA; strategy fast-forwards; Kay pushes and on CRC `cd
   trial_0826/ercot/waves/screening_v3 && bash submit_this.sh` (may go
   up together with 61's wave; 44 + 36 slots). **Pre-computed BEFORE any
   Y, committed with the wave as `waves/screening_v3/covariates.csv`:**
   per site `H_C(s, 180)` (61 §3 definition), base_v3 own-site
   curtailment, DC PTDF of the site bus on the pocket lines
   (`pocket_lines(120)`) and on every base_v3 line with
   `hours_ge_99pct > 0` (from `branch.csv`/`bus.csv`).
5. **Landing analysis `analysis/pool/SCREENING_V3.md` + csv (after
   COLLECTED and the strategy session's tx123 update; reader
   `ps.build_wave("screening_v3")`; `ercot_gp_loader.suspect_flag` as
   cross-check):** for each graded j (B_j > 0) with d_s = Δ_j(s, 180) vs
   base_v3 over 16 sites:
   - **Tiers (pre-registered from SCREENING_ERCOT.md, no Y):** pocket_120
     {163, 270, 274, 275, 116}, wind_near {110, 140, 146} (buses 2/75),
     pv_pocket {30, 59, 142} (buses 26/14), far {91, 205, 206, 204, 20}.
     Primary contrast: C = pocket_120 ∪ wind_near (8) vs U = far (5);
     Hodges–Lehmann shift HL (median of the 40 differences), exact
     two-sided Mann–Whitney p (`mannwhitneyu(method="exact")`), exact 95 %
     Moses interval. **LOCATIONAL** iff Holm-adjusted p ≤ 0.05 across the
     graded ids AND `|HL| ≥ 2·B_j` AND the interval excludes 0; two-sided
     (far sites may cost more for less relief). Also: HL/B_j,
     rank-biserial r, WIND-only sensitivity (7 vs 5), Kruskal–Wallis over
     the four tiers (descriptive). Disclose the PV/WIND and ω (0.10–0.97)
     confounds. No ratio for any j; V1 relief/MW is reported as a column.
   - **Covariates:** Spearman of d_s with H_C, own-site base
     curtailment and the PTDF columns; ΔV1 decomposed per run into
     own-site (parent + twin of the retrofitted unit) and other-site
     components from `gen_summary` (own-site relief at high ω is partly
     accounting reclassification).
   - **E1 per site:** GAP-READABLE vs `G_site + G_base`.
   - **MATCHED-MW RANKING vs E-D3 SLATE** (renamed; v2 ranked at ω ≈
     0.5 so a different order is expected from the protocol alone):
     tie band `B_V1/180 ≈ 90 MWh/MW`; **SLATE BUS-SET HOLDS** iff the v3
     top-6 by relief/MW at 180 MW lie on buses {120, 2, 75}; site
     membership reported with TIED marks. **Prediction stated now:** 275
     enters and 163 leaves (ω saturation); the bus set holds. Kendall
     τ_b between v2 and v3 ranks on the 16 sites with exact p
     (descriptive). E-D3 stands in every case.
   - **Dominance read:** a non-slate site is BO-relevant only if its
     L180 Δ vector on the seated objectives (B_j units) is not dominated
     by some slate site's; all dominated → "slate exclusion justified on
     all seated objectives"; any non-dominated → disclosed + PI flag;
     E-D3 not reopened in this campaign."""


# --------------------------------------------------------------------------
# rows
# --------------------------------------------------------------------------
def selection(path=SELECTION):
    ranked = json.load(open(path))["ranked"]
    by = {int(r["rank"]): r for r in ranked}
    assert sorted(by) == list(range(1, 17)), sorted(by)
    assert [by[k]["site"] for k in range(1, 7)] == list(SLATE)
    return by


def sites_7_16(path=SELECTION):
    by = selection(path)
    return [str(by[k]["site"]) for k in RANKS]


def replicate_row(index, wave_d_dm=WAVE_D_DM):
    dm = pd.read_csv(wave_d_dm, dtype={"oat_site": str, "replicate_of": str}, float_precision="round_trip")
    r = dm[dm["index"] == REPLICATE_OF[1]].iloc[0].to_dict()
    assert r["oat_site"] == "163" and r["level_id"] == "L180" and r["pem_mw"] == LEVEL, r
    assert r["omega"] == LEVEL / r["gen_pmax"], (r["omega"], LEVEL / r["gen_pmax"])
    r = {c: r[c] for c in mw.COLS}
    r["index"] = index
    r["replicate_of"] = f"{REPLICATE_OF[0]}:{REPLICATE_OF[1]}"
    r["bus"] = int(r["bus"])
    return r


# --------------------------------------------------------------------------
# covariates (inputs only)
# --------------------------------------------------------------------------
def curtailed_hours(renew=BASE / "renewables_hourly.csv"):
    r = pd.read_csv(renew)
    assert r["is_pem"].dtype == bool, r["is_pem"].dtype
    w = r[(r["unit_type"] == "WIND") & (~r["is_pem"])]
    assert len(w) == 8760 and not w.duplicated(["Date", "Hour"]).any()
    c = w[w["Curtailment"] > CURT_MIN_MWH]
    assert len(c) == N_C_HOURS, len(c)
    return list(zip(c["Date"], c["Hour"].astype(int) + 1))


def profile_on(hours, site, path):
    w = pd.read_csv(path, dtype={site: float})
    w = w[w["Year"] == 2019].copy()
    assert len(w) == 8760
    w["Date"] = [f"{y:04d}-{m:02d}-{d:02d}" for y, m, d in zip(w["Year"], w["Month"], w["Day"])]
    w = w.set_index(["Date", "Period"])
    assert w.index.is_unique
    v = w.loc[hours, site].to_numpy(dtype=float)
    assert len(v) == len(hours) and np.isfinite(v).all()
    return v


def ptdf_distributed(data_dir=DATA, load=LOAD_RT):
    """(PTDF DataFrame lines x bus ids, weights). Distributed slack over mean 2019 hourly load."""
    br = pd.read_csv(data_dir / "branch.csv")
    bus = pd.read_csv(data_dir / "bus.csv")
    ids = [int(b) for b in bus["Bus ID"]]
    pos = {b: i for i, b in enumerate(ids)}
    x = br["X"].to_numpy(dtype=float)
    assert (x > 0).all()
    A = np.zeros((len(br), len(ids)))
    for k, (f, t) in enumerate(zip(br["From Bus"].astype(int), br["To Bus"].astype(int))):
        A[k, pos[f]], A[k, pos[t]] = 1.0, -1.0
    Bbus = A.T @ np.diag(1 / x) @ A
    r = 0                                            # any reference: removed by the distributed slack
    keep = [i for i in range(len(ids)) if i != r]
    theta = np.zeros((len(ids), len(ids)))
    theta[np.ix_(keep, keep)] = np.linalg.inv(Bbus[np.ix_(keep, keep)])
    P_ref = np.diag(1 / x) @ A @ theta              # injection at bus j, withdrawal at r
    ld = pd.read_csv(load)
    ld = ld[ld["Year"] == 2019]
    assert len(ld) == 8760
    w = np.array([ld[str(b)].astype(float).mean() for b in ids])
    w = w / w.sum()
    P = P_ref - (P_ref @ w)[:, None]
    return pd.DataFrame(P, index=br["UID"].astype(str), columns=ids), w


def covariates(data_dir=DATA, base=BASE, selection_path=SELECTION):
    by = selection(selection_path)
    tier_of = {s: t for t, ss in TIERS.items() for s in ss}
    sites = [str(by[k]["site"]) for k in range(1, 17)]
    assert sorted(tier_of) == sorted(sites), (sorted(tier_of), sorted(sites))
    hours = curtailed_hours(base / "renewables_hourly.csv")
    gs = pd.read_csv(base / "gen_summary.csv", dtype={"Generator": str})
    gs = gs[gs["is_pem"].astype(str).str.lower() != "true"].set_index("Generator")
    ls = pd.read_csv(base / "line_summary.csv")
    pocket = po.pocket_lines(str(data_dir), 120)
    cong = [str(l) for l in ls.loc[ls["hours_ge_99pct"] > 0, "Line"]]
    lines = pocket + [l for l in cong if l not in pocket]
    P, _ = ptdf_distributed(data_dir)
    npl = mw.nameplates(sites, data_dir)
    wave_d_row = {s: 3 * (SLATE.index(s) + 1) for s in SLATE}
    v3 = {s: i + 1 for i, s in enumerate(sites_7_16(selection_path))}
    rows = []
    for k in range(1, 17):
        s = sites[k - 1]
        pmax, b, ut = npl[s]
        assert b == int(by[k]["bus"]) and ut == by[k]["unit_type"] and abs(pmax - by[k]["gen_pmax"]) < 1e-6
        W = profile_on(hours, s, WIND_RT if ut == "WIND" else SOLAR_RT)
        rec = {"site": s, "rank_v2": k, "unit_type": ut, "bus": b, "gen_pmax": pmax, "omega_180": LEVEL / pmax,
               "tier": tier_of[s], "slate": s in SLATE,
               "source_row": (f"{mw.WAVE}:{wave_d_row[s]}" if s in SLATE else f"{WAVE}:{v3[s]}"),
               "relief_per_mw_v2": float(by[k]["relief_per_mw"]),
               "H_C_180_MWh": math.fsum(np.minimum(LEVEL, W)), "H_C_profile": "wind" if ut == "WIND" else "solar",
               "n_hours_C": len(hours), "base_v3_own_curtailment_mwh": float(gs.loc[s, "curtailment_mwh"]),
               "saturation_flag": bool(LEVEL / pmax >= SATURATION_OMEGA)}
        for l in lines:
            rec[f"ptdf_{l}"] = float(P.loc[l, b])
        rows.append(rec)
    df = pd.DataFrame(rows)
    df.attrs["pocket_lines"], df.attrs["congested_lines"] = pocket, cong
    return df


# --------------------------------------------------------------------------
# README + build
# --------------------------------------------------------------------------
def readme(rows):
    n = len(rows)
    tab = ["| row | site | type | bus | level | PEM MW | nameplate MW | PEM_fraction | replicate_of | flag |",
           "|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        flag = "saturation (omega >= 0.9)" if r["omega"] >= SATURATION_OMEGA else ""
        tab.append(f"| {r['index']} | {r['oat_site']} | {r['unit_type']} | {r['bus']} | {r['level_id']} | "
                   f"{r['pem_mw']:.0f} | {r['gen_pmax']:.1f} | {r['omega']:.5f} | {r['replicate_of'] or '-'} | {flag} |")
    return f"""# {WAVE} — 16-site screening under identity v3 (prompt 62 Part C; NOT submitted)

Built by `tools/make_screening_v3.py` (zero simulation). Kay submits ON CRC after
the wave commit is fast-forwarded and pushed:

    cd trial_0826/ercot/waves/{WAVE} && bash submit_this.sh

`submit_this.sh` refuses without `waves/GAP_DECISION.json`, prints it, prints
`qquota`, and asks for a literal `yes` before `qsub`. {n} tasks x 4 slots =
{4 * n} slots (`-q long -pe smp 4 -r n`); collector `--full` on every row
({n} x {mw.FULL_EXTRACT_MB} MB = {n * mw.FULL_EXTRACT_MB} MB on CRC; gz stay out of git).

Analysis-only: these rows never enter the GP's X, the HV ledger, the holdout or
the random baseline. Part C is disclosure; E-D3 (the slate) is not reopened.

## 1. Rows ({n})

Rows 1-10 = ranks 7-16 of `analysis/cost_fix/wave_d_selection.json` (read from
the file), each site alone at 180 MW (`omega = 180 / gen_pmax`, bid 40.0, full
year from 01-01-2019, `level_id = L180`). The six slate sites already have L180
rows in wave D (`location_oat_v2` rows 3, 6, 9, 12, 15, 18). Row {n} replicates
wave-D row 3 (site 163 L180): its `overall.csv` md5 must equal wave D's at
landing (no code or data drift since 11-06; also the within-wave anchor for the
saturation row). No L60 level.

{chr(10).join(tab)}

Retrofit dicts: `{{"<site>": {{"PEM_bid", "PEM_fraction", "gen_pmax"}}}}` for WIND
and PV alike (`parameters.py::_update_renewable_generator` needs gen_pmax and
p_min = 0; every screened site has PMin 0).

## 2. Pre-registered covariates (`covariates.csv`; computed at build from inputs only)

Per site, all 16 screened sites: tier (pocket_120 / wind_near / pv_pocket /
far), slate flag, the row that carries its L180 value, `H_C(s, 180)` = sum over
the {N_C_HOURS:,} base_v3 WIND-curtailment hours (> {CURT_MIN_MWH:g} MWh) of
`min(180, W_s,h)` (W = `REAL_TIME_wind.csv` for WIND, `REAL_TIME_solar.csv` for
PV — prompt 61 defined W for wind only; the PV substitution is disclosed),
base_v3 own-site curtailment (`gen_summary.csv`), and the DC PTDF of the site
bus on the pocket lines (`pocket_lines(120)`) and on every base_v3 line with
`hours_ge_99pct > 0`. `bus.csv` has no Ref bus, so the PTDF uses a
load-weighted distributed slack (mean 2019 hourly load per bus,
`REAL_TIME_load.csv`); B from branch reactance X; positive = From -> To.

## 3. Prompt 62 §4.4–§4.5 (verbatim)

{SECTION_4_4_4_5}

## 4. Identity gate and collector

Same machinery as wave D (`tools/make_wave_d.py`): the array reads
`--ruc_mipgap` / `--ruc_time_limit` from `waves/GAP_DECISION.json` at RUN time
and refuses without it; SMOKE_GATEd on `waves/smoke_v2/SMOKE_PASS`; task stamps
`{WAVE.upper()}_START` / `{WAVE.upper()}_END`. Collector: every row `--full` ->
`extracts/{WAVE}/run_index_N/`, `runtimes.csv`, wall-clock, per-run
`pool_full_metrics.json` on CRC; git receives the slim tables only
(`trial_0826/ercot/.gitignore`: `extracts/{WAVE}/**/*.csv.gz`).
"""


def build(waves=ERCOT / "waves", data_dir=DATA, selection_path=SELECTION, wave_d_dm=WAVE_D_DM, base=BASE):
    sites = sites_7_16(selection_path)
    rep = replicate_row(len(sites) + 1, wave_d_dm)
    d, rows = mw.build(waves=waves, data_dir=data_dir, levels=[LEVEL], wave=WAVE, sites=sites,
                       include_nuclear=False, readme_fn=readme, unit_types=("WIND", "PV"),
                       extra_rows=[rep], prompt_tag=PROMPT_TAG)
    cov = covariates(data_dir, base, selection_path)
    cov.to_csv(d / "covariates.csv", index=False)
    return d, rows, cov


def main():
    d, rows, cov = build()
    print(f"built {d}: {len(rows)} rows; sites {[r['oat_site'] for r in rows]}")
    print(f"omega: " + ", ".join(f"{r['oat_site']} {r['omega']:.3f}" for r in rows))
    print(f"covariates: {len(cov)} sites x {cov.shape[1]} columns; pocket lines {cov.attrs['pocket_lines']}; "
          f"{len(cov.attrs['congested_lines'])} base_v3 congested lines")


if __name__ == "__main__":
    main()
