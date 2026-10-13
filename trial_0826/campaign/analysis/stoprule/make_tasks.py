"""Prompt 37 — the pre-registered run grid -> tasks.csv (CRC array) and
local_tasks.csv (2-D M1/M4 + 6-D M4, run on the Mac).

CRC (one task = one trajectory; SGE_TASK_ID = row `task`, 1-based):
  A primary   E-path-1..5 x {M1, M3} x noise 1   x q 8 x seeds 0-49   500
  B noise     E-path-1..5 x {M1, M3} x {0.5, 2}  x q 8 x seeds 0-3     80
  C secondary {E-mean, E-short, Z-needle, Z-plateau, Z-dis}
                          x {M1, M3} x noise 1   x q 8 x seeds 0-19   200
  D batch     E-path-1..5 x {M1, M3} x noise 1   x q 4 x seeds 0-1     20
  E replay M3 17 2-D grids x M3                        x seeds 0-19   340
  + M4 in every 6-D cell (A-D)                                      400
Local: 2-D grids x {M1, M4} x seeds 0-19 only (no 6-D method runs locally).
"""
import csv
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from problems import E_PATHS, problem_names_2d  # noqa: E402

SECONDARY = ["E-mean", "E-short", "Z-needle", "Z-plateau", "Z-dis"]


def cells_6d():
    for p in E_PATHS:
        yield "A", p, 1.0, 8, range(50)
    for p in E_PATHS:
        for n in (0.5, 2.0):
            yield "B", p, n, 8, range(4)
    for p in SECONDARY:
        yield "C", p, 1.0, 8, range(20)
    for p in E_PATHS:
        yield "D", p, 1.0, 4, range(2)


def main():
    crc, local = [], []
    for block, p, n, q, seeds in cells_6d():
        for s in seeds:
            # 6-D work is CRC-only (Kay 10-12): M4 included in the array
            for m in ("M1", "M3", "M4"):
                crc.append({"block": block, "problem": p, "method": m, "seed": s, "noise": n,
                            "q": q, "cand_rule": "subset"})
    for p in problem_names_2d():
        for s in range(20):
            crc.append({"block": "E", "problem": p, "method": "M3", "seed": s, "noise": 1.0,
                        "q": 2, "cand_rule": "full"})
            for m in ("M1", "M4"):
                local.append({"block": "R", "problem": p, "method": m, "seed": s, "noise": 1.0,
                              "q": 2, "cand_rule": "full"})
    # fallback if BOGP_CRC_botorch never appears (PREREG §3): M1 + M4 rows
    m1 = [r for r in crc if r["method"] in ("M1", "M4")]
    for name, rows in (("tasks.csv", crc), ("local_tasks.csv", local), ("tasks_noM3.csv", m1)):
        with open(HERE / name, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["task", *rows[0].keys()])
            w.writeheader()
            for i, r in enumerate(rows, 1):
                w.writerow({"task": i, **r})
        print(name, len(rows))


if __name__ == "__main__":
    main()
