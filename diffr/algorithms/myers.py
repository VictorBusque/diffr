import logging

from .base import DiffrAlgorithm

# Import Cython implementations
try:
    from diffr.algorithms.myers_cy import create_diff_output, shortest_edit_script

    _CYTHON_AVAILABLE = True
except ImportError:
    _CYTHON_AVAILABLE = False

logger = logging.getLogger(__name__)


class MyersDiff(DiffrAlgorithm):
    """
    Implementation of the Myers difference algorithm.

    This algorithm finds the shortest edit script between two sequences.

    Reference: "An O(ND) Difference Algorithm and Its Variations" by Eugene W. Myers
    """

    def __init__(self, use_cython=True, **kwargs):
        super().__init__(**kwargs)
        self.use_cython = use_cython and _CYTHON_AVAILABLE

    def diff(self, old: str, new: str) -> dict:
        logger.info("Starting diff computation")
        """
        Compute the diff between old and new strings using Myers algorithm.

        Args:
            old (str): Original text
            new (str): Modified text

        Returns:
            dict: Diff object containing the differences between the two strings
        """
        # Split the strings into lines for line-by-line comparison
        old_lines = old.splitlines(True)
        new_lines = new.splitlines(True)
        logger.debug(f"Old lines: {len(old_lines)}, New lines: {len(new_lines)}")

        # Get the shortest edit script (list of matching points)
        if self.use_cython:
            logger.info("Using Cython implementation")
            lcs: list[tuple[int, int]] = shortest_edit_script(old_lines, new_lines)
            result: dict = create_diff_output(old_lines, new_lines, lcs)
        else:
            logger.info("Using Python implementation")
            lcs: list[tuple[int, int]] = self._shortest_edit_script(old_lines, new_lines)
            result: dict = self._create_diff_output(old_lines, new_lines, lcs)

        logger.info("Diff computation completed")
        return result

    def _shortest_edit_script(self, old: list[str], new: list[str]) -> list[tuple[int, int]]:
        logger.debug("Computing shortest edit script")
        """
        Implements Myers' algorithm to find the shortest edit script between two sequences.
        Returns list of matching points (x, y) in the edit graph.

        This is an optimized version that uses a sparse representation of the edit graph.
        """
        n, m = len(old), len(new)
        max_edit_distance = n + m

        # Handle edge cases
        if n == 0:
            return []
        if m == 0:
            return []

        # V stores the best path endpoints for each diagonal k
        v = {}
        path = {}

        # Find the middle snake
        for d in range(max_edit_distance + 1):
            for k in range(-d, d + 1, 2):
                # Decide whether to go down or right
                if k == -d or (k != d and v.get(k - 1, -1) < v.get(k + 1, -1)):
                    x = v.get(k + 1, -1)
                    previous_k = k + 1
                else:
                    x = v.get(k - 1, -1) + 1
                    previous_k = k - 1

                y = x - k

                # Save the path
                path[(k, d)] = previous_k

                # Follow diagonal
                while x < n and y < m and old[x] == new[y]:
                    x += 1
                    y += 1

                v[k] = x

                # Check if we've reached the end
                if x >= n and y >= m:
                    # Reconstruct the path
                    return self._backtrack_path(path, n, m, d)

        return []

    def _backtrack_path(self, path: dict[tuple[int, int], int], n: int, m: int, d: int) -> list[tuple[int, int]]:
        logger.debug("Backtracking path")
        """
        Backtrack through the path to reconstruct the edit script.
        Returns a list of matching points.
        """
        if d == 0:
            # If the sequences are identical
            return [(i, i) for i in range(n)]

        points = []
        x, y = n, m
        k = x - y

        for d_val in range(d, 0, -1):
            previous_k = path.get((k, d_val))

            # Determine if we moved down or right
            if previous_k == k + 1:
                # Moved down
                y_prev = y - 1
                x_prev = x
            else:
                # Moved right
                x_prev = x - 1
                y_prev = y

            # Add any diagonal moves
            while x > x_prev and y > y_prev:
                x -= 1
                y -= 1
                points.append((x, y))

            if d_val > 0:
                k = previous_k
                x, y = x_prev, y_prev

        # Reverse since we built the path backwards
        return sorted(points)

    def _create_diff_output(
        self, old_lines: list[str], new_lines: list[str], lcs_points: list[tuple[int, int]]
    ) -> dict:
        logger.debug("Creating diff output")
        """
        Convert the edit script into a diff object with proper structure.

        Args:
            old_lines: List of lines from the old text
            new_lines: List of lines from the new text
            lcs_points: List of matching points from the shortest edit script

        Returns:
            dict: A structured diff object
        """
        # Convert to set for faster lookups
        lcs_set = set(lcs_points)

        # Create line diffs
        line_diffs: list[dict] = []
        old_idx, new_idx = 0, 0

        while old_idx < len(old_lines) or new_idx < len(new_lines):
            if old_idx < len(old_lines) and new_idx < len(new_lines) and (old_idx, new_idx) in lcs_set:
                # Lines match
                line_diffs.append(
                    {
                        "line_number": new_idx + 1,
                        "content": old_lines[old_idx],
                        "added": False,
                        "removed": False,
                        "word_diffs": [],  # No word diffs for unchanged lines
                    }
                )
                old_idx += 1
                new_idx += 1
            elif old_idx < len(old_lines) and (old_idx, new_idx) not in lcs_set:
                # Line removed
                line_diffs.append(
                    {
                        "line_number": old_idx + 1,
                        "content": old_lines[old_idx],
                        "added": False,
                        "removed": True,
                        "word_diffs": [{"word": old_lines[old_idx].rstrip(), "added": False, "removed": True}],
                    }
                )
                old_idx += 1
            elif new_idx < len(new_lines) and (old_idx, new_idx) not in lcs_set:
                # Line added
                line_diffs.append(
                    {
                        "line_number": new_idx + 1,
                        "content": new_lines[new_idx],
                        "added": True,
                        "removed": False,
                        "word_diffs": [{"word": new_lines[new_idx].rstrip(), "added": True, "removed": False}],
                    }
                )
                new_idx += 1

        # Group line diffs into blocks
        blocks: list[dict] = []
        if line_diffs:
            current_block: list[dict] = []
            current_block_number = 1

            for i, line_diff in enumerate(line_diffs):
                # Start a new block if:
                # 1. This is the first line diff
                # 2. The previous line was unchanged but this one is changed
                # 3. We've had 3 or more unchanged lines in a row
                if (
                    i == 0
                    or (
                        not line_diff["added"]
                        and not line_diff["removed"]
                        and (line_diffs[i - 1]["added"] or line_diffs[i - 1]["removed"])
                    )
                    or (
                        i >= 3
                        and not any(ld["added"] or ld["removed"] for ld in line_diffs[i - 3 : i])
                        and (line_diff["added"] or line_diff["removed"])
                    )
                ):
                    if current_block:
                        blocks.append({"block_number": current_block_number, "lines": current_block})
                        current_block_number += 1
                        current_block = []

                current_block.append(line_diff)

            # Add the last block
            if current_block:
                blocks.append({"block_number": current_block_number, "lines": current_block})

        # Create and return the full diff
        return {"blocks": blocks}
