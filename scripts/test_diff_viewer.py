import json
import pathlib

from diffr import diff_hunks
from diffr.data_models.diff_model import Diff


def load_file(name: str):
    """Load a file from the sample_files directory."""
    path = pathlib.Path(__file__).parent / "sample_files" / name

    with open(path) as file:
        return file.read()


if __name__ == "__main__":
    original = load_file("diff_0_original.tsx")
    updated = load_file("diff_0_modified.tsx")  # Changed from "diff_0_updated.tsx" to "diff_0_modified.tsx"
    output = diff_hunks(original, updated, 0.4)
    print(json.dumps(output, indent=2))
    diff = Diff.from_hunks(output)
    print(diff)
