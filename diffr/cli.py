"""Command-line interface for diffr."""

import argparse
import sys
import time

from .core import diff_hunks
from .data_models.diff_model import Diff


def main():
    """Run entry point for the CLI."""
    parser = argparse.ArgumentParser(description="Compare files and display differences")
    parser.add_argument("file1", help="Path to first file to compare (original)")
    parser.add_argument("file2", help="Path to second file to compare (modified)")

    args = parser.parse_args()

    file1 = args.file1
    file2 = args.file2

    with open(file1, encoding="utf-8") as f1, open(file2, encoding="utf-8") as f2:
        content1, content2 = f1.read(), f2.read()
        lines1, lines2 = content1.splitlines(), content2.splitlines()
        start_time = time.perf_counter()
        hunks = diff_hunks(content1, content2)
        end_time = time.perf_counter()
        diff = Diff.from_hunks(hunks)
        print(diff)
        print(f"Elapsed time: {end_time - start_time:.8f}s")
        print(f"Lines in file 1: {len(lines1)}")
        print(f"Lines in file 2: {len(lines2)}")
        print(f"Speed: {((len(lines1) + len(lines2)) / 1_000_000) / (end_time - start_time):.2f} M/s")

    return 0


if __name__ == "__main__":
    sys.exit(main())
