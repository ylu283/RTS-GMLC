#!/usr/bin/env python3
"""Regenerate Prescient/Egret metadata for the vendored TX-123BT data
(prompt 26 T1.2). Deterministic and idempotent — run from anywhere:

    python make_metadata.py

Operates in place on data/ercot123_2019/ (the pristine vendored state is
commit-pinned; MD5SUMS.vendored + PROVENANCE.md record input -> output).

Transforms:
  1. branch.csv: header 'TR Ratio' -> 'Tr Ratio' (the egret rts-gmlc
     parser reads row['Tr Ratio']; the GTEP template dir carries the same
     fix) and UID '1' -> 'L1' (all-numeric rows are float64-coerced by
     iterrows(), mangling bus-id lookups — see fix_branch_csv).
  2. Year-end lookahead padding (MANDATORY): the six timeseries CSVs hold
     exactly 8,760 rows ending 2019-12-31 Period 24, but GmlcDataProvider
     requests data through start + num_days + (ruc_horizon-24)h
     = 2020-01-01 12:00 with honor_lookahead=False (metadata Look_Ahead /
     Date_To are inert; CSV row coverage is the binding constraint).
     Remedy: append 24 rows stamped 2020-01-01 Period 1..24 copying the
     2019-01-01 profiles. Affects only the final RUC's lookahead tail
     beyond the settled horizon.
  3. timeseries_pointers.csv: Area 'MW Load' rows (123 areas x DA/RT; in
     this dataset bus.csv Area ids are 1:1 with Bus IDs, so the load CSVs'
     bus-id columns double as area columns — asserted below) + Generator
     'PMax MW' rows (82 wind + 72 solar x DA/RT). HYDRO gets NO pointer
     rows — no hydro timeseries exists; the 10 units (497.8 MW) keep
     scalar PMax = constant availability (decision documented in
     CONFIG_ERCOT.md; hydro is excluded from all curtailment accounting).
  4. simulation_objects.csv: 2019 dates, Date_To 1/1/20 0:00 (covered by
     the padding), DA Look_Ahead 24 (>= ruc_horizon-24 = 12), RT 2
     (>= sced_horizon-1 = 0), hourly resolution.

The parser SILENTLY drops pointer rows whose Object doesn't match a
skeleton element (continue + dropna) — so this script asserts the emitted
Objects against gen.csv/bus.csv, and verify_metadata.py re-checks at model
level after parsing.
"""
import csv
import hashlib
import sys
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent / "data" / "ercot123_2019"

TS_FILES = [
    "DAY_AHEAD_load.csv", "REAL_TIME_load.csv",
    "DAY_AHEAD_solar.csv", "REAL_TIME_solar.csv",
    "DAY_AHEAD_wind.csv", "REAL_TIME_wind.csv",
]

# Provenance of the vendored inputs themselves (recorded, not recomputed):
# upstream TX-123BT (arXiv:2302.13231) -> processing notebook -> canonical dir.
NOTEBOOK_MD5S = [
    ("2_demo_processing_kay copy.ipynb (gtep/123_bus_coal/"
     "ERCOT_BUS123_base_XC_editeddata/original_data/)",
     "33c5205947fb5dc67884320f3c57e63f"),
    ("demo_processing_XC.ipynb (gtep/123_bus_coal/"
     "ERCOT_BUS123_base_XC_editeddata/ — the DIFFERENT notebook named by "
     "MANIFEST.md SS2/SS6; recorded so the TODO closes against the right file)",
     "1a143831cbc3638800d41e38729d26eb"),
]


def md5(path: Path) -> str:
    return hashlib.md5(path.read_bytes()).hexdigest()


def fix_branch_csv(path: Path) -> bool:
    """Two egret-parser fixes:
    (a) header 'TR Ratio' -> 'Tr Ratio' (parser reads row['Tr Ratio']);
    (b) branch UID '1' -> 'L1'. With every branch.csv column numeric,
        pandas iterrows() coerces each row to float64, so the parser's
        str(row['From Bus']) yields '98.0' while bus_id_to_name is keyed
        '98' (bus.csv rows stay object-dtyped via the Bus Name strings)
        -> KeyError. A string UID keeps branch rows object-dtyped so bus
        ids survive as ints. Branch names are cosmetic downstream
        (line_detail 'Line' column).
    """
    with open(path, newline="") as f:
        rows = list(csv.reader(f))
    changed = False
    if "TR Ratio" in rows[0]:
        rows[0] = [c.replace("TR Ratio", "Tr Ratio") for c in rows[0]]
        changed = True
    elif "Tr Ratio" not in rows[0]:
        raise SystemExit(f"branch.csv header has neither spelling: {rows[0]}")
    assert rows[0][0] == "UID", rows[0]
    if not rows[1][0].startswith("L"):
        for r in rows[1:]:
            r[0] = f"L{int(r[0])}"
        changed = True
    if changed:
        with open(path, "w", newline="") as f:
            csv.writer(f).writerows(rows)
    return changed


def pad_timeseries(path: Path) -> bool:
    with open(path, newline="") as f:
        rows = list(csv.reader(f))
    header, body = rows[0], rows[1:]
    assert header[:4] == ["Year", "Month", "Day", "Period"], header[:4]
    if body[-1][0] == "2020":
        return False  # already padded (idempotent)
    assert len(body) == 8760, f"{path.name}: {len(body)} rows, expected 8760"
    assert body[-1][:4] == ["2019", "12", "31", "24"], body[-1][:4]
    jan1 = [r for r in body if r[:3] == ["2019", "1", "1"]]
    assert len(jan1) == 24, f"{path.name}: {len(jan1)} Jan-1 rows"
    pad = [["2020", "1", "1", r[3]] + r[4:] for r in jan1]
    with open(path, "a", newline="") as f:
        csv.writer(f).writerows(pad)
    return True


def build_pointers():
    with open(DATA_DIR / "bus.csv", newline="") as f:
        buses = list(csv.DictReader(f))
    assert len(buses) == 123, len(buses)
    # Area ids are 1:1 with Bus IDs here; the load CSVs' columns (bus ids)
    # therefore key the Area pointer rows directly.
    for b in buses:
        assert b["Area"] == b["Bus ID"], (b["Bus ID"], b["Area"])
    areas = [b["Area"] for b in buses]

    with open(DATA_DIR / "gen.csv", newline="") as f:
        gens = list(csv.DictReader(f))
    wind = [g["GEN UID"] for g in gens if g["Unit Type"] == "WIND"]
    solar = [g["GEN UID"] for g in gens if g["Unit Type"] == "PV"]
    hydro = [g["GEN UID"] for g in gens if g["Unit Type"] == "HYDRO"]
    assert (len(wind), len(solar), len(hydro)) == (82, 72, 10), (
        len(wind), len(solar), len(hydro))

    # every pointer Object must exist as a column in its data file
    for fname, objs in [("DAY_AHEAD_load.csv", areas),
                        ("DAY_AHEAD_wind.csv", wind),
                        ("DAY_AHEAD_solar.csv", solar)]:
        with open(DATA_DIR / fname, newline="") as f:
            cols = next(csv.reader(f))[4:]
        missing = set(objs) - set(cols)
        assert not missing, f"{fname}: no column for {sorted(missing)}"
        extra = set(cols) - set(objs)
        assert not extra, f"{fname}: unclaimed columns {sorted(extra)}"

    rows = []
    for sim, prefix in [("DAY_AHEAD", "DAY_AHEAD"), ("REAL_TIME", "REAL_TIME")]:
        for a in areas:
            rows.append([sim, "Area", a, "MW Load", f"{prefix}_load.csv"])
        for g in wind:
            rows.append([sim, "Generator", g, "PMax MW", f"{prefix}_wind.csv"])
        for g in solar:
            rows.append([sim, "Generator", g, "PMax MW", f"{prefix}_solar.csv"])
    out = DATA_DIR / "timeseries_pointers.csv"
    with open(out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Simulation", "Category", "Object", "Parameter", "Data File"])
        w.writerows(rows)
    return len(rows)


def write_simulation_objects():
    lines = [
        ["Simulation_Parameters", "Description", "DAY_AHEAD", "REAL_TIME"],
        ["Periods_per_Step", "the number of discrete periods represented in "
         "each simulation step", "24", "1"],
        ["Period_Resolution", "seconds per period", "3600", "3600"],
        ["Date_From", "simulation beginning period", "1/1/19 0:00", "1/1/19 0:00"],
        ["Date_To", "simulation ending period (must account for lookahead "
         "data availability; rows are padded through 1/1/20 P24)",
         "1/1/20 0:00", "1/1/20 0:00"],
        ["Look_Ahead_Periods_per_Step", "the number of look ahead periods "
         "included in each optimization step", "24", "2"],
        ["Look_Ahead_Resolution", "look-ahead period resolution", "3600", "3600"],
    ]
    with open(DATA_DIR / "simulation_objects.csv", "w", newline="") as f:
        csv.writer(f).writerows(lines)


def main():
    # input hashes = the vendored (pristine) state, so re-runs of this
    # idempotent script keep reporting the true vendored -> output mapping
    vendored = dict(
        reversed(line.split())  # "md5 name" -> {name: md5}
        for line in (DATA_DIR / "MD5SUMS.vendored").read_text().splitlines())
    inputs = {name: vendored[name] for name in ["branch.csv"] + TS_FILES}

    changed = {"branch.csv": fix_branch_csv(DATA_DIR / "branch.csv")}
    for t in TS_FILES:
        changed[t] = pad_timeseries(DATA_DIR / t)
    n_ptr = build_pointers()
    write_simulation_objects()

    gen_files = ["timeseries_pointers.csv", "simulation_objects.csv"]
    with open(DATA_DIR / "PROVENANCE.md", "w") as f:
        f.write("# Generated-metadata provenance (make_metadata.py)\n\n")
        f.write("Vendored state = commit-pinned MD5SUMS.vendored. This run's "
                "input -> output MD5s (32-char):\n\n")
        f.write("| file | input md5 | output md5 |\n|---|---|---|\n")
        for name, in_md5 in inputs.items():
            f.write(f"| {name} | {in_md5} | {md5(DATA_DIR / name)} |\n")
        for name in gen_files:
            f.write(f"| {name} | (generated) | {md5(DATA_DIR / name)} |\n")
        f.write(f"\ntimeseries_pointers rows: {n_ptr} "
                "(2 sims x (123 Area MW Load + 82 wind PMax + 72 solar PMax)); "
                "HYDRO deliberately unpointed (scalar PMax — see "
                "CONFIG_ERCOT.md).\n\n")
        f.write("Processing-notebook identity (upstream Data_public_5year -> "
                "these CSVs):\n\n")
        for desc, h in NOTEBOOK_MD5S:
            f.write(f"- `{h}`  {desc}\n")

    for name, did in changed.items():
        print(f"{name}: {'transformed' if did else 'already transformed (no-op)'}")
    print(f"pointers: {n_ptr} rows; simulation_objects + PROVENANCE.md written")
    return 0


if __name__ == "__main__":
    sys.exit(main())
