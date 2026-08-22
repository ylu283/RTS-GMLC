"""Find wave indices without a completed run, clean up their partial dirs,
and PRINT the SGE resubmission commands (never executes them).

Usage:  python resubmit_missing.py <wave_dir> [--yes]

Success sentinel: runs/run_index_<i>/overall_simulation_output.csv.
SGE `-t` accepts ONLY `n[-m[:s]]` — a single range; comma lists are
Torque/SLURM syntax and are rejected — so missing indices are grouped into
maximal contiguous ranges, one qsub line per range.
"""

import argparse
import csv
import os
import shutil


def wave_indices(wave_dir):
    with open(os.path.join(wave_dir, "design_matrix.csv"), newline="") as f:
        return sorted(int(float(row["index"])) for row in csv.DictReader(f))


def run_dir(wave_dir, index):
    return os.path.join(wave_dir, "runs", f"run_index_{index}")


def missing_indices(wave_dir):
    return [i for i in wave_indices(wave_dir)
            if not os.path.isfile(os.path.join(run_dir(wave_dir, i),
                                               "overall_simulation_output.csv"))]


def contiguous_ranges(indices):
    """[3, 5, 6, 7, 12] -> [(3, 3), (5, 7), (12, 12)]"""
    ranges = []
    for i in sorted(indices):
        if ranges and i == ranges[-1][1] + 1:
            ranges[-1] = (ranges[-1][0], i)
        else:
            ranges.append((i, i))
    return ranges


def resubmit_commands(wave_dir, missing):
    script = f"{os.path.basename(os.path.normpath(wave_dir))}_array.sh"
    return [f"qsub -t {a}-{b} {script}" for a, b in contiguous_ranges(missing)]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("wave_dir")
    parser.add_argument("--yes", action="store_true",
                        help="delete partial run dirs without prompting")
    args = parser.parse_args(argv)

    missing = missing_indices(args.wave_dir)
    if not missing:
        print("all indices complete — nothing to resubmit")
        return

    print(f"missing indices ({len(missing)}): {missing}")
    partial = [i for i in missing if os.path.isdir(run_dir(args.wave_dir, i))]
    if partial:
        print(f"partial run dirs to delete: {[run_dir(args.wave_dir, i) for i in partial]}")
        if not args.yes:
            answer = input("delete these partial run dirs? [y/N] ")
            if answer.strip().lower() not in ("y", "yes"):
                print("leaving partial dirs in place; resubmission would fail on them")
                partial = []
        for i in partial:
            shutil.rmtree(run_dir(args.wave_dir, i))
            print(f"deleted {run_dir(args.wave_dir, i)}")

    print("resubmit with (run from inside the wave dir; NOT executed here):")
    for cmd in resubmit_commands(args.wave_dir, missing):
        print(f"  {cmd}")


if __name__ == "__main__":
    main()
