# test_patience_diff.py
from diffr.algorithms.patience_cy import patience_diff


def run_test(test_id, original, updated):
    print(f"--- Test {test_id} ---")
    print("Original:")
    print(original)
    print("Updated:")
    print(updated)
    print("Diff Result:")
    result = patience_diff(original, updated)
    for line_pair in result:
        print(line_pair)
    print()

def main():
    # Test 1: Identical text should result in all matching lines.
    original = "line1\nline2\nline3"
    updated = "line1\nline2\nline3"
    run_test(1, original, updated)

    # Test 2: A line inserted in the updated text.
    original = "line1\nline3"
    updated = "line1\nline2\nline3"
    run_test(2, original, updated)

    # Test 3: A line removed from the updated text.
    original = "line1\nline2\nline3"
    updated = "line1\nline3"
    run_test(3, original, updated)

    # Test 4: Completely different content.
    original = "a\nb\nc"
    updated = "x\ny\nz"
    run_test(4, original, updated)

if __name__ == "__main__":
    main()
