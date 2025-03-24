# cython: boundscheck=True, wraparound=True, cdivision=False

from typing import List, Tuple
# Import diff_line and tokenize from your Myers diff module.
from .myers import diff_line, tokenize

# ---------------------------------------------------------------------
# Patience diff functions (line-level)
# ---------------------------------------------------------------------

def diff_code(original: str, updated: str) -> List[Tuple[str, str]]:
    """
    Compute a diff between two texts using a patience diff algorithm.

    Args:
        original (str): The original text.
        updated (str): The updated text.

    Returns:
        List[Tuple[str, str]]: A list of (original_line, updated_line) tuples.
        For unchanged lines, both strings are equal.
        For insertions/deletions one side is the empty string.
    """
    cdef list orig_lines = original.splitlines()
    cdef list upd_lines = updated.splitlines()
    return _diff_recursive(orig_lines, upd_lines, 0, len(orig_lines), 0, len(upd_lines))

def _diff_recursive(orig, upd, int ostart, int oend, int ustart, int uend):
    """
    Recursively diff the slices orig[ostart:oend] and upd[ustart:uend]
    using the patience algorithm. Always returns whole-line tuples.

    Args:
        orig (list): List of original lines.
        upd (list): List of updated lines.
        ostart (int): Start index for original lines.
        oend (int): End index for original lines.
        ustart (int): Start index for updated lines.
        uend (int): End index for updated lines.

    Returns:
        list: A list of tuples representing the diff.
    """
    cdef list result = []
    cdef int len_orig, len_upd, min_len, k
    cdef int prev_o, prev_u, i, j
    cdef tuple anchor

    # Base cases: one or both ranges are empty.
    if ostart >= oend and ustart >= uend:
        return result
    elif ostart >= oend:
        for j in range(ustart, uend):
            result.append(("", upd[j]))
        return result
    elif ustart >= uend:
        for i in range(ostart, oend):
            result.append((orig[i], ""))
        return result

    # Build dictionaries for lines that are unique in each slice.
    cdef dict orig_uniques = {}
    for i in range(ostart, oend):
        line = orig[i]
        if line in orig_uniques:
            orig_uniques[line] = -1
        else:
            orig_uniques[line] = i

    cdef dict upd_uniques = {}
    for j in range(ustart, uend):
        line = upd[j]
        if line in upd_uniques:
            upd_uniques[line] = -1
        else:
            upd_uniques[line] = j

    # Collect common unique lines.
    cdef list common = []
    for line, i_val in orig_uniques.items():
        j_val = upd_uniques.get(line, None)
        if i_val != -1 and j_val is not None and j_val != -1:
            common.append((i_val, j_val, line))
    # Sort common anchors by original then updated index.
    common.sort(key=lambda x: (x[0], x[1]))

    # Compute the longest increasing subsequence (LIS) based on updated index.
    cdef list lis = _longest_increasing_subsequence(common)

    if not lis:
        # No common anchors found.
        if (ostart + 1 == oend) and (ustart + 1 == uend):
            # Simply return the whole line pair.
            result.append((orig[ostart], upd[ustart]))
            return result
        else:
            # Pair as many lines as possible; do not call diff_line here.
            len_orig = oend - ostart
            len_upd = uend - ustart
            min_len = len_orig if len_orig < len_upd else len_upd

            for k in range(min_len):
                result.append((orig[ostart+k], upd[ustart+k]))
            for k in range(min_len, len_orig):
                result.append((orig[ostart+k], ""))
            for k in range(min_len, len_upd):
                result.append(("", upd[ustart+k]))
            return result

    # Recursively diff segments around each common anchor.
    prev_o = ostart
    prev_u = ustart
    for anchor in lis:
        i = anchor[0]
        j = anchor[1]
        result.extend(_diff_recursive(orig, upd, prev_o, i, prev_u, j))
        # The anchor line is common.
        result.append((orig[i], upd[j]))
        prev_o = i + 1
        prev_u = j + 1
    result.extend(_diff_recursive(orig, upd, prev_o, oend, prev_u, uend))
    return result

def _longest_increasing_subsequence(common):
    """
    Given a list of tuples (i, j, line) sorted by i (and then j),
    compute the longest increasing subsequence based on the j values.

    Args:
        common (list): List of tuples (i, j, line).

    Returns:
        list: The longest increasing subsequence as a list of tuples.
    """
    cdef int n = len(common)
    if n == 0:
        return []
    cdef list tails = []          # stores the last j value of each subsequence length
    cdef list tails_indices = []  # stores indices in 'common' corresponding to tails
    cdef list prev = [ -1 for _ in range(n) ]  # predecessor indices for reconstruction
    cdef int index, pos, lo, hi, mid
    cdef tuple curr

    for index in range(n):
        curr = common[index]
        lo = 0
        hi = len(tails)
        while lo < hi:
            mid = (lo + hi) // 2
            if curr[1] > tails[mid]:
                lo = mid + 1
            else:
                hi = mid
        pos = lo
        if pos == len(tails):
            tails.append(curr[1])
            tails_indices.append(index)
        else:
            tails[pos] = curr[1]
            tails_indices[pos] = index
        if pos > 0:
            prev[index] = tails_indices[pos - 1]
        else:
            prev[index] = -1

    cdef list lis = []
    pos = tails_indices[-1]
    while pos != -1:
        lis.append(common[pos])
        pos = prev[pos]
    lis.reverse()
    return lis

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
