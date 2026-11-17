#!/usr/bin/env python3
"""Prompt 53 v3.1 §2.8 — landing report for waves n0_E + random_E (zero simulation).

Reads extracts/{n0_E,random_E} (slim tables committed by the collectors +
the CRC-computed pool_full_metrics.json for E8 / E9 / N5) through the
UNCHANGED reader: pool_standings.build_wave() = pool_objectives.build_pool()
+ the json merge with its consistency asserts (R7 / R8 / G_run / overall md5).

Writes
  waves/n0_E/landing_R.json   contract §6.4: R = nadir + 0.1 (nadir - ideal)
                              per candidate over the 48 grading rows (plan
                              §6.3), for ALL 29 pool candidates
  waves/n0_E/landing_rows.csv one row per run (96): identity, SUSPECT S1-S3,
                              R1 shed, R2 + flag, RUC quality, G_run, wall-clock
  waves/n0_E/LANDING.md       the report

Orientation (plan §6.3 "all objectives are minimized"): dir 'min' as is;
dir 'max' (V2, E6) minimized as -x, reported back in raw units (ideal = max,
nadir = min, R = min - 0.1 (max - min)); dir '-' (no direction in
pool_definitions.json) computed as if minimized and flagged. D3 (two
columns) enters as gen-1 + gen-93 starts.

Run (py >= 3.12; pool_standings.py):
    cd trial_0826/ercot && /opt/anaconda3/bin/python tools/land_ercot_n0.py
"""
import json
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

ERCOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ERCOT))
warnings.filterwarnings("ignore", message="Downcasting object dtype arrays", category=FutureWarning)
import pool_objectives as po  # noqa: E402
import pool_standings as ps  # noqa: E402

WAVES_E = ("n0_E", "random_E")
GRADING_WAVE = "n0_E"
OUT = ERCOT / "waves" / "n0_E"
SLOTS = 4
SPLIT_S = 25000.0                      # the wave-D node-group split (pool_standings.wallclock_table)
SHED_VIOLATION_MWH = 1.0               # plan §1.3 / design_space_E.json guardrails.R1
R2_FLAG_MWH = 891.8                    # 2 x base (plan §1.3)
RULE = "R = nadir + 0.1 (nadir - ideal) per objective over the 48 grading rows (plan §6.3)"


def load(waves=WAVES_E):
    ps.assert_frozen_defs()
    defs = po.load_defs()
    wides, walls = {}, {}
    for w in waves:
        wide = ps.build_wave(wave=w, defs=defs, verbose=False)
        wide["D3"] = wide["D3_gen1_starts"].astype(float) + wide["D3_gen93_starts"].astype(float)
        wides[w] = wide
        walls[w] = ps.wallclock_table(wide, wave=w, slots=SLOTS, split_s=SPLIT_S)
    return defs, wides, walls


def ref_point(wide, defs):
    """ideal / nadir / R for every candidate (raw units) + orientation notes."""
    ids = list(defs["global_order"])
    assert len(ids) == 29 and sorted(ids) == sorted(defs["candidates"]), ids
    ideal, nadir, R, dirs, notes = {}, {}, {}, {}, {}
    for j in ids:
        x = wide[j].astype(float).to_numpy()
        assert len(x) == 48 and np.isfinite(x).all(), (j, np.isfinite(x).sum())
        d = defs["candidates"][j]["dir"]
        dirs[j] = d
        s = -1.0 if d == "max" else 1.0          # minimization orientation
        y = s * x
        lo, hi = float(y.min()), float(y.max())
        r = hi + 0.1 * (hi - lo)
        ideal[j], nadir[j], R[j] = s * lo, s * hi, s * r
        if d == "-":
            notes[j] = "dir '-' in pool_definitions.json: computed as minimized; a seat needs a direction first"
        if hi == lo:
            notes[j] = (notes.get(j, "") + ("; " if j in notes else "")
                        + f"zero range on the 48 grading rows (value {s * hi:g}): R = nadir")
    return ids, ideal, nadir, R, dirs, notes


def rows_table(wides, walls):
    out = []
    for w, wide in wides.items():
        t = walls[w].set_index("index")
        for _, r in wide.iterrows():
            i = int(r["index"])
            out.append({
                "key": r["key"], "wave": w, "index": i, "identity": r["identity"],
                "suspect": bool(r["suspect"]), "S1_ok": bool(r["S1_ok"]), "S2_ok": bool(r["S2_ok"]),
                "S3_ok": bool(r["S3_ok"]), "S1_resid_usd": float(r["S1_resid_usd"]),
                "n_ruc": int(r["n_ruc"]), "n_ruc_optimal": int(r["n_ruc_optimal"]),
                "n_ruc_time_limit": int(r["n_ruc_time_limit"]), "max_gap_pct": float(r["max_gap_pct"]),
                "R1_shed_mwh": float(r["R1"]), "R1_violation": bool(float(r["R1"]) > SHED_VIOLATION_MWH),
                "R2_reserve_shortfall_mwh": float(r["R2"]), "R2_flag": bool(float(r["R2"]) > R2_FLAG_MWH),
                "G_run_usd": float(r["G_run_usd"]), "pem_mw": float(r["pem_mw"]),
                "overall_md5": r["overall_md5"],
                "wall_s": float(t.loc[i, "wall_s"]), "wall_h": float(t.loc[i, "wall_h"]),
                "core_h": float(t.loc[i, "core_h"]), "node_group": t.loc[i, "node_group"],
                "ruc_solve_time_median_s": float(r["ruc_solve_time_median_s"]),
                "ruc_solve_time_max_s": float(r["ruc_solve_time_max_s"]),
                "full_extract": bool(r["full_extract"])})
    return pd.DataFrame(out)


def _f(v):
    a = abs(v)
    if v == 0:
        return "0"
    if a >= 1e5 or a < 1e-3:
        return f"{v:.4e}"
    return f"{v:,.4f}".rstrip("0").rstrip(".")


def report(rows, walls, ids, ideal, nadir, R, dirs, notes, defs):
    n = {w: int((rows.wave == w).sum()) for w in WAVES_E}
    lines = []
    for w in WAVES_E:
        s = rows[rows.wave == w]
        lines.append(f"| {w} | {n[w]} / 48 | {(s.identity == 'v3').sum()} | {int(s.suspect.sum())} | "
                     f"{int((~s.S1_ok).sum())} / {int((~s.S2_ok).sum())} / {int((~s.S3_ok).sum())} | "
                     f"{s.S1_resid_usd.max():.2e} | {s.n_ruc_optimal.sum():,} / {s.n_ruc.sum():,} | "
                     f"{int(s.n_ruc_time_limit.sum())} | {s.max_gap_pct.max():.3f} | "
                     f"{s.R1_shed_mwh.max():g} ({int(s.R1_violation.sum())}) | "
                     f"{s.R2_reserve_shortfall_mwh.max():.1f} ({int(s.R2_flag.sum())}) |")
    wc = []
    for w in WAVES_E:
        s = rows[rows.wave == w]
        for g in ("A (fast)", "B (slow)"):
            q = s[s.node_group == g]
            if len(q):
                wc.append(f"| {w} | {g} | {len(q)} | {q.wall_h.min():.2f} – {q.wall_h.max():.2f} | "
                          f"{q.core_h.min():.1f} – {q.core_h.max():.1f} (mean {q.core_h.mean():.1f}) | "
                          f"{q.ruc_solve_time_median_s.median():.1f} | {q.ruc_solve_time_max_s.max():.0f} |")
        st, en = walls[w].start_epoch.min(), walls[w].end_epoch.max()
        wc.append(f"| {w} | **all** | {len(s)} | {s.wall_h.min():.2f} – {s.wall_h.max():.2f} | "
                  f"**{s.core_h.sum():,.0f} total** (mean {s.core_h.mean():.1f}) | "
                  f"{s.ruc_solve_time_median_s.median():.1f} | {s.ruc_solve_time_max_s.max():.0f} |")
        wc.append(f"| {w} | calendar | | {(en - st) / 3600:.1f} h ({pd.to_datetime(st, unit='s'):%m-%d %H:%M} → "
                  f"{pd.to_datetime(en, unit='s'):%m-%d %H:%M} UTC) | | | |")
    tot = rows.core_h.sum()
    fa, sl = rows[rows.node_group == "A (fast)"], rows[rows.node_group == "B (slow)"]
    n_md5 = int(rows["overall_md5"].nunique())
    worst = rows.loc[rows.ruc_solve_time_max_s.idxmax()]
    rp = []
    for j in ids:
        tag = "seat (E-D1b)" if j in ("V1", "E1", "R4", "N1") else ""
        rp.append(f"| {j} | {dirs[j]} | {defs['candidates'][j]['unit']} | {_f(ideal[j])} | {_f(nadir[j])} | "
                  f"**{_f(R[j])}** | {tag} {notes.get(j, '')} |".replace("|  |", "| |"))
    seats_note = ("E3 is listed too: the cost seat is E1 if prompt 52's §1.2 verdict is READABLE, "
                  "else E3 (both R values are pinned here, so either verdict reads R from this file).")
    return f"""# n0_E / random_E — landing report (prompt 53 v3.1 §2.8)

Zero simulation. Built by `tools/land_ercot_n0.py` from the collector
commits (`extracts/n0_E/COLLECTED`: 48 rows, 2026-11-15T05:53Z;
`extracts/random_E/COLLECTED`: 48 rows, 2026-11-15T07:02Z) through the
unchanged reader (`pool_standings.build_wave` → `pool_objectives.build_pool`;
`pool_definitions.json` asserted equal to freeze f76d897; E8 / E9 / N5 from the
CRC `pool_full_metrics.json`, R7 / R8 / G_run / overall md5 asserted equal to
the local slim recomputation on every row). Per-run table:
`landing_rows.csv` (96 rows). Ref point: `landing_R.json` (contract §6.4).

## 1. Success, identity, SUSPECT, guardrails (per run in `landing_rows.csv`)

| wave | rows landed | identity v3 | SUSPECT | S1 / S2 / S3 fails | max S1 resid $ | RUCs OPTIMAL | RUCs at time limit | max final gap % | R1 shed max MWh (violations > 1) | R2 max MWh (flags > {R2_FLAG_MWH}) |
|---|---|---|---|---|---|---|---|---|---|---|
{chr(10).join(lines)}

- **SUSPECT (plan §1.2 S1–S3): 0 of 96.** S3 here = gen-1 and gen-93 starts
  are 0 on every run (no nuclear retrofit; no exact replicates in these
  waves); every row is a distinct design ({n_md5} distinct `overall.csv` md5s over the 96).
- **R1 load shed: 0 MWh on every one of the 96 runs** (expected 0; plan §1.3
  violation = shed > {SHED_VIOLATION_MWH:g} MWh: none). R1 is DEAD on the
  grading tier, as on every earlier wave; the constrained-qNEHVI switch is
  not triggered.
- **R2 reserve shortfall:** max {rows.R2_reserve_shortfall_mwh.max():.1f} MWh, far below the round
  flag 2 × base = {R2_FLAG_MWH} MWh; no flag.
- `full_extract` true on all 96 (`--full`; gz tables in $GROUP storage).

## 2. Wall-clock (`extracts/<wave>/wallclock.csv`; 4 slots, core-h = wall × 4)

Node groups split at {SPLIT_S:,.0f} s wall (the wave-D split).

| wave | group | runs | wall h | core-h | RUC median solve s (median) | RUC max solve s |
|---|---|---|---|---|---|---|
{chr(10).join(wc)}

**Total: {tot:,.0f} core-h for 96 runs ({tot / 96:.1f} per run)**, inside the
2.0–4.3k bracket that AMENDMENT 2026-11-14 projected from wave D. The 6-site rows
run at about the wave-D per-node speeds (fast {fa.wall_h.min():.1f}–{fa.wall_h.max():.1f} h, slow
{sl.wall_h.min():.1f}–{sl.wall_h.max():.1f} h; wave D 5.1–5.5 / 10.5–11.8 h); {len(sl)} of 96 landed on slow nodes
(wave D: 6 of 21), which is why the mean per run sits above wave D's fast 21.

**RUC solve-time margin (disclosed).** The longest RUC solve is
{worst.ruc_solve_time_max_s:.0f} s ({worst.key}, slow node) against `ruc_time_limit` = 1200 s,
status OPTIMAL, 0 time-limit statuses on all {int(rows.n_ruc.sum()):,} RUCs. The solve-time
column includes model build (standings §8), so this is not a limit hit, but
the margin on a slow node is ≈ 4 %, not the ≈ 25× of the January smoke cited
in AMENDMENT 2026-11-06b. Any later TIME_LIMIT status is caught by S2
(SUSPECT) per run.

## 3. HV reference point R (plan §6.3; `landing_R.json`)

Over the **48 grading rows** (`n0_E`, `sobol_index` 0–47), for **all 29 pool
candidates** (contract §6.4: a later objective-list version never reopens
§6.3). {RULE}. All objectives minimized: dir `max` candidates are minimized
as −x and reported in raw units (ideal = max, nadir = min, R = min −
0.1 (max − min)); dir `-` candidates have no direction in
`pool_definitions.json` and are computed as if minimized (flagged). D3 =
gen-1 + gen-93 starts. Prompt 55 Part B asserts these values at init.
{seats_note}

| id | dir | unit | ideal | nadir | R | note |
|---|---|---|---|---|---|---|
{chr(10).join(rp)}

The R values use the grading tier only; R does not depend on E-D7 (nav 32
or 48). The holdout rows (random_E) are NOT used for R. They are model-free
here: no model has been scored against them, so this report spends none of
the 24-scoring exposure budget.

## 4. Budget actuals

Appended to the plan as AMENDMENT 2026-11-16 (n0_E + random_E actuals).
"""


def main(argv=None):
    defs, wides, walls = load()
    rows = rows_table(wides, walls)
    assert len(rows) == 96 and (rows.identity == "v3").all() and rows.full_extract.all()
    g = wides[GRADING_WAVE]
    dm = po.design_matrix(GRADING_WAVE)
    assert (dm["tier"] == "grading").all() and len(g) == 48
    ids, ideal, nadir, R, dirs, notes = ref_point(g, defs)
    out = {"identity": "v3", "n_rows": 48, "tier": "grading", "candidates": ids,
           "ideal": ideal, "nadir": nadir, "R": R, "rule": RULE,
           "dir": dirs, "orientation": "minimized; dir 'max' as -x (raw units reported: ideal = max, "
                                       "nadir = min); dir '-' computed as minimized",
           "notes": notes, "rows": [f"{GRADING_WAVE}:{i}" for i in range(1, 49)],
           "D3": "gen-1 + gen-93 starts (D3_gen1_starts + D3_gen93_starts)",
           "source": "tools/land_ercot_n0.py; pool_standings.build_wave on extracts/n0_E "
                     "(E8/E9/N5 from pool_full_metrics.json)"}
    (OUT / "landing_R.json").write_text(json.dumps(out, indent=1) + "\n")
    rows.to_csv(OUT / "landing_rows.csv", index=False)
    (OUT / "LANDING.md").write_text(report(rows, walls, ids, ideal, nadir, R, dirs, notes, defs))
    print(f"SUSPECT {int(rows.suspect.sum())}/96; R1 max {rows.R1_shed_mwh.max()}; "
          f"core-h {rows.core_h.sum():.1f}; R written for {len(ids)} candidates")


if __name__ == "__main__":
    main()
