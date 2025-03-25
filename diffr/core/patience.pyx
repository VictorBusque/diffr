# cython: boundscheck=True, wraparound=True, cdivision=False

from typing import List, Tuple
from .myers import diff_line, tokenize  # For inline diffs only

# ---------------------------------------------------------------------
# Patience diff functions (line-level)
# ---------------------------------------------------------------------

def diff_code(original: str, updated: str) -> List[Tuple[str, str]]:
    orig_lines = original.splitlines()
    upd_lines = updated.splitlines()
    return _diff_recursive(orig_lines, upd_lines, 0, len(orig_lines), 0, len(upd_lines))

def _diff_recursive(orig, upd, ostart, oend, ustart, uend):
    result = []

    # Base cases: empty ranges
    if ostart >= oend and ustart >= uend:
        return result
    elif ostart >= oend:
        return [("", line) for line in upd[ustart:uend]]
    elif ustart >= uend:
        return [(line, "") for line in orig[ostart:oend]]

    # Find unique common lines as potential anchors
    orig_uniques = {}
    for i in range(ostart, oend):
        line = orig[i]
        orig_uniques[line] = i if line not in orig_uniques else -1

    upd_uniques = {}
    for j in range(ustart, uend):
        line = upd[j]
        upd_uniques[line] = j if line not in upd_uniques else -1

    # Collect common unique lines (anchors)
    common = []
    for line, i in orig_uniques.items():
        if i != -1 and upd_uniques.get(line, -1) != -1:
            common.append((i, upd_uniques[line]))

    # Sort by original index and find LIS on updated index
    common.sort()
    lis = _longest_increasing_subsequence([j for i, j in common])

    if not lis:
        # No anchors: Fallback to line-level Myers diff for this chunk
        myers_diff = _myers_line_diff(orig[ostart:oend], upd[ustart:uend])
        return myers_diff

    # Recurse around anchors
    prev_o, prev_u = ostart, ustart
    for anchor in lis:
        i, j = common[lis.index(anchor)]  # Match anchor indices
        result += _diff_recursive(orig, upd, prev_o, i, prev_u, j)
        result.append((orig[i], upd[j]))
        prev_o, prev_u = i + 1, j + 1

    result += _diff_recursive(orig, upd, prev_o, oend, prev_u, uend)
    return result

def _longest_increasing_subsequence(indices):
    """Computes LIS using patience sorting."""
    tails = []
    for idx in indices:
        lo, hi = 0, len(tails)
        while lo < hi:
            mid = (lo + hi) // 2
            if tails[mid] < idx:
                lo = mid + 1
            else:
                hi = mid
        if lo == len(tails):
            tails.append(idx)
        else:
            tails[lo] = idx
    return tails

def _myers_line_diff(a, b):
    """Myers algorithm for line-level diffs between lists a and b."""
    # Implement Myers' algorithm here (pseudocode simplified)
    # This is a simplified version focusing on the key logic
    v = {1: 0}
    for d in range(0, len(a) + len(b) + 1):
        for k in range(-d, d + 1, 2):
            if k == -d or (k != d and v[k - 1] < v[k + 1]):
                x = v[k + 1]
            else:
                x = v[k - 1] + 1
            y = x - k
            while x < len(a) and y < len(b) and a[x] == b[y]:
                x += 1
                y += 1
            v[k] = x
            if x >= len(a) and y >= len(b):
                # Trace back to generate diff
                return _trace_myers_diff(a, b, v, d, k)
    return []

def _trace_myers_diff(a, b, v, d, k):
    x, y = len(a), len(b)
    result = []

    while x > 0 or y > 0:
        if x > 0 and y > 0 and a[x - 1] == b[y - 1]:
            result.append((a[x - 1], b[y - 1]))  # equal
            x -= 1
            y -= 1
        elif x > 0 and y > 0:
            result.append((a[x - 1], b[y - 1]))  # replace
            x -= 1
            y -= 1
        elif y > 0:
            result.append(("", b[y - 1]))  # insert
            y -= 1
        elif x > 0:
            result.append((a[x - 1], ""))  # delete
            x -= 1

    return list(reversed(result))

# ---------------------------------------------------------------------
# Grouping into hunks & building final output dict
# ---------------------------------------------------------------------

def diff_hunks(original: str, updated: str) -> dict:
    """
    Compute a diff between two texts and return a dictionary that contains
    only the hunks (changed blocks).

    Args:
        original (str): The original text.
        updated (str): The updated text.

    Returns:
        dict: A dictionary containing the hunks.
    """
    cdef list raw_diff = diff_code(original, updated)
    cdef int i, n = len(raw_diff)
    cdef int old_line_num = 0
    cdef int new_line_num = 0
    cdef list diff_entries = []
    cdef str orig_line, upd_line, entry_type
    cdef dict diff_dict
    cdef object inline_diff
    cdef int line_number_old, line_number_new

    # Process raw diff entries; assign line numbers and diff type.
    for i in range(n):
        orig_line = raw_diff[i][0]
        upd_line = raw_diff[i][1]
        if orig_line != "":
            old_line_num += 1
            line_number_old = old_line_num
        else:
            line_number_old = 0  # 0 indicates no line number (insertion)
        if upd_line != "":
            new_line_num += 1
            line_number_new = new_line_num
        else:
            line_number_new = 0

        if orig_line == upd_line:
            entry_type = "equal"
        elif orig_line == "":
            entry_type = "insert"
        elif upd_line == "":
            entry_type = "delete"
        else:
            entry_type = "replace"

        if entry_type == "replace":
            inline_diff = [ {"type": op[0], "value": op[1]} for op in diff_line(orig_line, upd_line) ]
        else:
            inline_diff = None

        diff_dict = {}
        diff_dict["type"] = entry_type
        if line_number_old:
            diff_dict["line_number_old"] = line_number_old
        if line_number_new:
            diff_dict["line_number_new"] = line_number_new
        if entry_type == "equal":
            diff_dict["content"] = orig_line
        elif entry_type == "insert":
            diff_dict["content_new"] = upd_line
        elif entry_type == "delete":
            diff_dict["content_old"] = orig_line
        elif entry_type == "replace":
            diff_dict["content_old"] = orig_line
            diff_dict["content_new"] = upd_line
            diff_dict["inline_diff"] = inline_diff

        diff_entries.append(diff_dict)

    # Group contiguous non-equal entries into hunks.
    cdef list hunks = []
    cdef list current_hunk = []
    cdef dict entry
    for entry in diff_entries:
        if entry["type"] == "equal":
            if current_hunk:
                hunks.append(_build_hunk(current_hunk))
                current_hunk = []
        else:
            current_hunk.append(entry)
    if current_hunk:
        hunks.append(_build_hunk(current_hunk))

    return {"hunks": hunks}

cdef dict _build_hunk(list hunk_entries):
    """
    Given a list of diff dict entries, compute the old/new line ranges and
    return a hunk dict.

    Args:
        hunk_entries (list): List of diff dict entries.

    Returns:
        dict: A dictionary representing the hunk.
    """
    cdef int ln
    cdef int min_old = 0, max_old = 0, min_new = 0, max_new = 0
    cdef bint first_old = True, first_new = True
    cdef dict entry
    for entry in hunk_entries:
        if "line_number_old" in entry:
            ln = entry["line_number_old"]
            if ln and first_old:
                min_old = ln
                max_old = ln
                first_old = False
            elif ln:
                if ln < min_old:
                    min_old = ln
                if ln > max_old:
                    max_old = ln
        if "line_number_new" in entry:
            ln = entry["line_number_new"]
            if ln and first_new:
                min_new = ln
                max_new = ln
                first_new = False
            elif ln:
                if ln < min_new:
                    min_new = ln
                if ln > max_new:
                    max_new = ln
    return {
        "old_range": {"start": min_old, "end": max_old},
        "new_range": {"start": min_new, "end": max_new},
        "lines": hunk_entries
    }
