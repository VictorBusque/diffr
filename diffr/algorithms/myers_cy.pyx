# cython: language_level=3, boundscheck=False, wraparound=False, nonecheck=False

import cython

@cython.ccall
def shortest_edit_script(old: list, new: list) -> list:
    """
    Optimized Cython implementation of Myers' algorithm to find the shortest edit script.
    """
    # Convert inputs to simple strings for safer comparison
    old_strings = [str(item) if item is not None else "" for item in old]
    new_strings = [str(item) if item is not None else "" for item in new]

    cdef int n = len(old_strings)
    cdef int m = len(new_strings)
    cdef int max_edit_distance = n + m
    cdef dict v = {}
    cdef dict path = {}
    cdef int d, k, x, y, previous_k

    # Handle edge cases
    if n == 0 or m == 0:
        return []

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
            while x < n and y < m and old_strings[x] == new_strings[y]:
                x += 1
                y += 1

            v[k] = x

            # Check if we've reached the end
            if x >= n and y >= m:
                # Reconstruct the path
                return backtrack_path(path, n, m, d)

    return []

@cython.ccall
def backtrack_path(dict path, int n, int m, int d) -> list:
    """
    Optimized Cython implementation to backtrack through the path.
    """
    cdef list points = []
    cdef int x = n
    cdef int y = m
    cdef int k = x - y
    cdef int d_val, previous_k, x_prev, y_prev

    if d == 0:
        # If the sequences are identical
        return [(i, i) for i in range(n)]

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

    # Sort since we built the path out of order
    points.sort()
    return points

@cython.ccall
def create_diff_output(old_lines: list, new_lines: list, lcs_points: list) -> dict:
    """
    Optimized Cython implementation to convert the edit script into a diff object using native structures.
    """
    # Declarations moved to the top of the function
    cdef set lcs_set = set(lcs_points)
    cdef list line_diffs = []
    cdef int old_idx = 0, new_idx = 0, i, current_block_number = 1, n_line_diffs, j
    cdef list blocks = []
    cdef list current_block = []
    cdef bint changes_found
    cdef dict line_diff

    # Build a list of line differences
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

    # Group line diffs into blocks using optimized block creation logic
    if line_diffs:
        n_line_diffs = len(line_diffs)
        for i in range(n_line_diffs):
            changes_found = False
            line_diff = line_diffs[i]
            if i >= 3:
                for j in range(i - 3, i):
                    if line_diffs[j]["added"] or line_diffs[j]["removed"]:
                        changes_found = True
                        break

            if (
                i == 0
                or (
                    not line_diff["added"]
                    and not line_diff["removed"]
                    and (line_diffs[i - 1]["added"] or line_diffs[i - 1]["removed"])
                )
                or (
                    i >= 3
                    and not changes_found
                    and (line_diff["added"] or line_diff["removed"])
                )
            ):
                if current_block:
                    blocks.append({"block_number": current_block_number, "lines": current_block})
                    current_block_number += 1
                    current_block = []
            current_block.append(line_diff)

        if current_block:
            blocks.append({"block_number": current_block_number, "lines": current_block})

    # Create and return the full diff object
    return {"blocks": blocks}
