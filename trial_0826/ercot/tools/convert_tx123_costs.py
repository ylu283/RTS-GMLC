#!/usr/bin/env python3
"""Prompt 36 T1 — rebuild the TX-123BT thermal cost/start columns in
RTS-GMLC `gen.csv` convention and write `data/ercot123_2019_v2/`.

v1 (`data/ercot123_2019/gen.csv`, from demo_processing_XC.ipynb) put the
start-up heat Csu·Pmax/fp into HR_avg_0 (egret reads an average heat RATE at
Pmin), wrote segment HEAT ΔC/fp into HR_incr_k (egret reads a RATE, BTU/kWh)
and set every start column to 1. This script translates the authors' C0/C1/Csu
into what each column means in RTS_Data/SourceData/gen.csv (prompt 36 §3.0):

  Output_pct_0          = PMin/PMax
  Output_pct_1..3       = (PMin + k·(PMax−PMin)/3)/PMax       (4 points, as RTS)
  HR_avg_0  [BTU/kWh]   = 1000·C(PMin)/(fp·PMin)   — includes the no-load C0
  HR_incr_k [BTU/kWh]   = 1000·ΔC_k/(fp·ΔP_k)       (linear: 1000·C1/fp, all k)
  Start Heat Cold/Warm/Hot MBTU = Csu·PMax/fp        (Csu in $/installed MW)
  Non Fuel Start Cost $ = 0

Readings (prompt 36 §0.2; Kay 10-12 chose c):
  c       linear C0 + C1·P, xlsx coefficients (= pkl ÷ 0.7), start Csu·PMax
  b, bp   linear, pkl coefficients (×0.7); bp differs from b only in the PEM
          bid B, which lives in the wave retrofit dicts, not here
  a       quadratic C0 + C1·P + C2·P² (C2 = 0.0016 COAL only; nuclear flat),
          Non Fuel Start Cost $ = Csu·PMax, Start Heat * = 0

The cost a unit actually gets is what the CRC egret fork (ylu283/Egret@e4a244d,
env/egretpatch_0.6.2.diff) parses: breakpoints round(pct·PMax, 4), fuel
round(f, 6). `fork_fuel_curve` replays that parser and `egret_convex_ok`
replays egret's convexity check (tx_utils.validate_and_clean_cost_curve);
a unit whose 4-point curve fails falls back to 2 points (PMin, PMax), logged.

Only gen.csv changes; every other v1 CSV is copied byte-for-byte, and inside
gen.csv only the COST_COLS cells of the 128 thermal rows are rewritten (all
other cells keep v1's exact text).

Usage (repo root or anywhere):
  python trial_0826/ercot/tools/convert_tx123_costs.py --reading c
"""
import argparse
import csv
import hashlib
import io
import json
import math
import shutil
import sys
from datetime import date
from pathlib import Path

import pandas as pd

ERCOT = Path(__file__).resolve().parents[1]
V1_DIR = ERCOT / "data" / "ercot123_2019"
V2_DIR = ERCOT / "data" / "ercot123_2019_v2"
SOURCE = ERCOT / "analysis" / "cost_fix" / "source_coeffs_tx123.csv"
REPORT_DIR = ERCOT / "analysis" / "cost_fix"

THERMAL = ("CT", "COAL", "NUC")
FACTOR = {"c": 1.0, "a": 1.0, "b": 0.7, "bp": 0.7}
C2_COAL = 0.0016
NPTS = 4
V1_CSVS = ("bus.csv", "branch.csv", "gen.csv", "simulation_objects.csv",
           "timeseries_pointers.csv", "DAY_AHEAD_load.csv", "DAY_AHEAD_solar.csv",
           "DAY_AHEAD_wind.csv", "REAL_TIME_load.csv", "REAL_TIME_solar.csv",
           "REAL_TIME_wind.csv")
START_HEAT = ("Start Heat Cold MBTU", "Start Heat Warm MBTU", "Start Heat Hot MBTU")
COST_COLS = (tuple(f"Output_pct_{i}" for i in range(5)) + ("HR_avg_0",)
             + tuple(f"HR_incr_{i}" for i in range(1, 5)) + START_HEAT
             + ("Non Fuel Start Cost $", "C0", "C1", "C2", "Csu"))


# --------------------------------------------------------------------------
# egret-fork replays
# --------------------------------------------------------------------------
def _num(v):
    try:
        v = float(v)
    except (TypeError, ValueError):
        return math.nan
    return v


def fork_fuel_curve(row):
    """Replay egret parser._read_generators (fork rounding) → [(MW, MMBTU/h)].

    `row` maps column → value as pandas.read_csv returns it (same as egret)."""
    pmax = float(row["PMax MW"])
    pcts = []
    for i in range(50):
        v = _num(row.get(f"Output_pct_{i}"))
        if math.isnan(v):
            break
        pcts.append(v)
    x = {i: round(v * pmax, 4) for i, v in enumerate(pcts)}
    n = len(x)
    if n == 0:
        return [(pmax, 0.0)]
    f = {0: (float(row["HR_avg_0"]) * 1000. / 1000000.) * x[0]}
    for i in range(1, n):
        f[i] = (((x[i] - x[i - 1]) * (float(row[f"HR_incr_{i}"]) * 1000. / 1000000.))) + f[i - 1]
    pts = [(x[i], round(f[i], 6)) for i in range(n)
           if (((i == 0) or (x[i - 1], f[i - 1]) != (x[i], f[i])) and (x[i], f[i]) != (0., 0.))]
    return pts or [(pmax, 0.0)]


def egret_convex_ok(points, p_min, p_max):
    """Replay the piecewise branch of tx_utils.validate_and_clean_cost_curve:
    False where egret would raise ValueError (non-convex / infinite slope)."""
    if len(points) == 1:
        o1, _ = points[0]
        return math.isclose(p_min, p_max) and (math.isclose(p_min, o1) or math.isclose(p_max, o1))
    last = None
    for (o1, c1), (o2, c2) in zip(points, points[1:]):
        if o2 <= p_min or math.isclose(p_min, o2):
            continue
        if p_max <= o1 or math.isclose(p_max, o1):
            continue
        if math.isclose(o2, o1):
            if math.isclose(c2, c1):
                continue
            return False
        s = (c2 - c1) / (o2 - o1)
        if last is None:
            last = s
            continue
        if s < last and not math.isclose(s, last):
            return False
        if not math.isclose(s, last):
            last = s
    return True


def fork_start_costs(row):
    """Replay parser start-up tiers + params.startup_costs_init_rule → [$] hot→cold."""
    mdt = float(row["Min Down Time Hr"])
    heat = tuple(_num(row[c]) for c in ("Start Heat Hot MBTU", "Start Heat Warm MBTU",
                                        "Start Heat Cold MBTU"))
    tim = tuple(_num(row[c]) for c in ("Start Time Hot Hr", "Start Time Warm Hr",
                                       "Start Time Cold Hr"))
    fuel = []
    for i in range(3):
        if math.isnan(tim[i]) or math.isnan(heat[i]):
            continue
        t = max(tim[i], mdt)
        if fuel and fuel[-1][0] == t:
            fuel[-1] = (t, heat[i])
        else:
            fuel.append((t, heat[i]))
    nf = _num(row["Non Fuel Start Cost $"])
    nf = 0.0 if math.isnan(nf) else nf
    fp = float(row["Fuel Price $/MMBTU"])
    return [nf + fp * h for _, h in fuel] if fuel else [nf]


# --------------------------------------------------------------------------
# translation
# --------------------------------------------------------------------------
def cost_columns(pmin, pmax, fp, C0, C1, Csu, C2=0.0, npts=NPTS, start="heat"):
    """Return {column: float | None} in RTS-GMLC convention for C(P) = C0 + C1 P + C2 P²."""
    def C(p):
        return C0 + C1 * p + C2 * p * p
    ps = [pmin + k * (pmax - pmin) / (npts - 1) for k in range(npts)]
    ps[-1] = pmax
    out = {f"Output_pct_{i}": None for i in range(5)}
    out.update({f"HR_incr_{i}": None for i in range(1, 5)})
    for k, p in enumerate(ps):
        out[f"Output_pct_{k}"] = p / pmax
    out["HR_avg_0"] = 1000. * C(pmin) / (fp * pmin)
    for k in range(1, npts):
        if C2:
            out[f"HR_incr_{k}"] = 1000. * (C(ps[k]) - C(ps[k - 1])) / (fp * (ps[k] - ps[k - 1]))
        else:                 # linear: one exact value on every segment
            out[f"HR_incr_{k}"] = 1000. * C1 / fp
    s = Csu * pmax
    if start == "heat":       # RTS convention: start fuel × fp, non-fuel 0
        for c in START_HEAT:
            out[c] = s / fp
        out["Non Fuel Start Cost $"] = 0.0
    else:                     # reading (a): all-$ start
        for c in START_HEAT:
            out[c] = 0.0
        out["Non Fuel Start Cost $"] = s
    out.update({"C0": C0, "C1": C1, "C2": C2, "Csu": Csu})
    return out


def _fmt(v):
    return "" if v is None else repr(float(v))


def _row_with(base, cols):
    r = dict(base)
    for k, v in cols.items():
        r[k] = math.nan if v is None else float(_fmt(v))   # value as egret reads the text
    return r


def convert_unit(base_row, C0, C1, Csu, C2=0.0, start="heat"):
    """Translate one unit; returns (cols, npts_used, parsed_points)."""
    pmin, pmax = float(base_row["PMin MW"]), float(base_row["PMax MW"])
    fp = float(base_row["Fuel Price $/MMBTU"])
    assert pmin > 0, f"Pmin must be > 0 (gen {base_row.get('GEN UID')})"
    for n in (NPTS, 2):
        if n == 2 and C2:
            raise ValueError(f"quadratic unit {base_row.get('GEN UID')} cannot fall back to 2 points")
        cols = cost_columns(pmin, pmax, fp, C0, C1, Csu, C2=C2, npts=n, start=start)
        pts = fork_fuel_curve(_row_with(base_row, cols))
        if egret_convex_ok(pts, pmin, pmax):
            return cols, n, pts
    raise ValueError(f"gen {base_row.get('GEN UID')}: 2-point curve fails convexity replay")


def md5(p):
    return hashlib.md5(Path(p).read_bytes()).hexdigest()


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--reading", choices=sorted(FACTOR), default="c")
    ap.add_argument("--v1_dir", type=Path, default=V1_DIR)
    ap.add_argument("--out_dir", type=Path, default=V2_DIR)
    ap.add_argument("--source", type=Path, default=SOURCE)
    ap.add_argument("--force", action="store_true", help="overwrite an existing out_dir gen.csv")
    a = ap.parse_args(argv)

    fac = FACTOR[a.reading]
    src = pd.read_csv(a.source).set_index("GEN UID")
    # (c)/(a): xlsx; (b)/(bp): pkl. Both must agree up to the 0.7 factor.
    for x, p in (("C0_xlsx", "c0_pkl"), ("C1_xlsx", "c1_pkl"), ("Csu_xlsx", "csu_pkl")):
        assert ((src[p] - 0.7 * src[x]).abs() <= 1e-12 * src[x].abs().clip(lower=1)).all(), x

    text = (a.v1_dir / "gen.csv").read_text()
    assert "\r" not in text and '"' not in text, "v1 gen.csv format changed"
    lines = text.split("\n")
    header = lines[0].split(",")
    col = {c: i for i, c in enumerate(header)}
    v1 = pd.read_csv(a.v1_dir / "gen.csv")          # values exactly as egret reads them
    assert len(v1) == len(lines) - 2 and lines[-1] == ""

    log, out_lines = [], [lines[0]]
    for i, line in enumerate(lines[1:-1]):
        cells = line.split(",")
        row = v1.iloc[i].to_dict()
        uid = int(row["GEN UID"])
        if row["Unit Type"] in THERMAL:
            s = src.loc[uid]
            assert s["Unit Type"] == row["Unit Type"] and s["PMax MW"] == row["PMax MW"]
            if a.reading in ("c", "a"):
                C0, C1, Csu = s["C0_xlsx"], s["C1_xlsx"], s["Csu_xlsx"]
            else:
                C0, C1, Csu = s["c0_pkl"], s["c1_pkl"], s["csu_pkl"]
            C2 = C2_COAL if (a.reading == "a" and row["Unit Type"] == "COAL") else 0.0
            cols, n, pts = convert_unit(row, C0, C1, Csu, C2=C2,
                                        start="nonfuel" if a.reading == "a" else "heat")
            for c, v in cols.items():
                cells[col[c]] = _fmt(v)
            fp = row["Fuel Price $/MMBTU"]
            log.append({"GEN UID": uid, "type": row["Unit Type"], "npts": n,
                        "PMin": row["PMin MW"], "PMax": row["PMax MW"], "fp": fp,
                        "C0": C0, "C1": C1, "C2": C2, "Csu": Csu,
                        "cost_at_pmin": fp * pts[0][1], "cost_at_pmax": fp * pts[-1][1],
                        "start_$": fork_start_costs(_row_with(row, cols))[-1]})
        out_lines.append(",".join(cells))
    out_lines.append("")

    a.out_dir.mkdir(parents=True, exist_ok=True)
    gen_out = a.out_dir / "gen.csv"
    if gen_out.exists() and not a.force:
        sys.exit(f"{gen_out} exists; pass --force to rebuild")
    for f in V1_CSVS:
        if f != "gen.csv":
            shutil.copyfile(a.v1_dir / f, a.out_dir / f)
    gen_out.write_text("\n".join(out_lines))

    # re-read exactly as egret does (pandas.read_csv) and replay every unit again
    v2 = pd.read_csv(gen_out)
    for rec in log:
        r = v2[v2["GEN UID"] == rec["GEN UID"]].iloc[0].to_dict()
        pts = fork_fuel_curve(r)
        assert egret_convex_ok(pts, r["PMin MW"], r["PMax MW"]), rec["GEN UID"]
        assert len(pts) == rec["npts"], rec["GEN UID"]
        assert pts[0][1] * r["Fuel Price $/MMBTU"] == rec["cost_at_pmin"], rec["GEN UID"]
        assert pts[-1][1] * r["Fuel Price $/MMBTU"] == rec["cost_at_pmax"], rec["GEN UID"]

    lg = pd.DataFrame(log)
    fallback = lg.loc[lg["npts"] == 2, "GEN UID"].tolist()
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    (REPORT_DIR / f"convert_log_{a.reading}.json").write_text(json.dumps({
        "reading": a.reading, "factor": fac, "n_thermal": len(lg),
        "fallback_2pt": fallback, "units": log}, indent=1, default=float))

    # MANIFEST
    files = sorted(V1_CSVS)
    with open(a.out_dir / "MANIFEST.md", "w") as fh:
        fh.write(f"# ercot123_2019_v2 — MANIFEST\n\n"
                 f"Built {date.today().isoformat()} by `trial_0826/ercot/tools/convert_tx123_costs.py "
                 f"--reading {a.reading}` (prompt 36).\n\n"
                 f"**v2: cost columns rebuilt; v1 mis-converted (prompt 36).** Only `gen.csv` "
                 f"differs from v1, and only in the cost/start columns of the 128 thermal "
                 f"units ({', '.join(f'`{c}`' for c in COST_COLS)}). See PROVENANCE.md.\n\n"
                 f"| field | value |\n|---|---|\n"
                 f"| reading | ({a.reading}) — "
                 + {"c": "linear C0·u + C1·P, start = Csu·PMax (Kay 10-12, CONFIRMED)",
                    "a": "quadratic, C2 = 0.0016 COAL only, start = Csu·PMax non-fuel",
                    "b": "linear, authors' pkl ×0.7", "bp": "linear, authors' pkl ×0.7 (B = 28)"}[a.reading]
                 + f" |\n| cost factor | ×{fac} |\n"
                 f"| breakpoints | {NPTS} (PMin + equal thirds); 2-point fallback units: "
                 f"{fallback if fallback else 'none'} |\n"
                 f"| source coefficients | `analysis/cost_fix/source_coeffs_tx123.csv` "
                 f"(md5 `{md5(a.source)}`) ← Generator_data.xlsx + 123bus_case_final.pkl "
                 f"(see analysis/cost_fix/T0_FACTS.md) |\n"
                 f"| v1 gen.csv md5 | `{md5(a.v1_dir / 'gen.csv')}` |\n\n"
                 f"## md5\n\n| file | md5 | same as v1 |\n|---|---|---|\n")
        for f in files:
            fh.write(f"| {f} | `{md5(a.out_dir / f)}` | "
                     f"{'yes' if md5(a.out_dir / f) == md5(a.v1_dir / f) else 'no'} |\n")

    print(f"reading ({a.reading}) ×{fac}: {len(lg)} thermal units rewritten; "
          f"{len(fallback)} fell back to 2 points {fallback}")
    print(f"wrote {a.out_dir} ({len(V1_CSVS)} CSVs + MANIFEST.md)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
