"""Look up one design-matrix row by SGE task id and print ONLY scalar shell
assignments (INDEX, NUM_DAYS, START_DATE) for `eval` in the array script.
Never prints the retrofit JSON — that is read from its own file by index.

Usage:  python get_row.py <sge_task_id> <design_matrix.csv>
"""

import csv
import re
import sys


def shell_assignments(task_id, csv_path):
    task_id = int(task_id)
    with open(csv_path, newline="") as f:
        matches = [row for row in csv.DictReader(f)
                   if int(float(row["index"])) == task_id]
    if len(matches) != 1:
        raise SystemExit(
            f"expected exactly one row with index {task_id} in {csv_path}, "
            f"found {len(matches)}"
        )
    row = matches[0]
    start_date = row["start_date"]
    # defensive: this string is eval'd in the job shell
    if not re.fullmatch(r"\d{2}-\d{2}-\d{4}", start_date):
        raise SystemExit(f"start_date {start_date!r} is not MM-DD-YYYY")
    return [
        f"INDEX={int(float(row['index']))}",
        f"NUM_DAYS={int(float(row['num_days']))}",
        f"START_DATE={start_date}",
    ]


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 2:
        raise SystemExit(__doc__)
    print("\n".join(shell_assignments(argv[0], argv[1])))


if __name__ == "__main__":
    main()
