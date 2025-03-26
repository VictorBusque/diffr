from typing import List, Tuple, Dict, Any
from .myers import diff_line

# ---------------------------------------------------------------------
# Patience diff functions (line-level)
# ---------------------------------------------------------------------

cpdef list _compute_raw_diff(str original, str updated):
    cdef list orig_lines = original.splitlines()
    cdef list upd_lines = updated.splitlines()
    return _diff_recursive(orig_lines, upd_lines, 0, len(orig_lines), 0, len(upd_lines))


cdef list _diff_recursive(
    list orig, list upd,
    int ostart, int oend,
    int ustart, int uend
):
    cdef list result = []
    cdef dict orig_uniques = {}
    cdef dict upd_uniques = {}
    cdef list common = []
    cdef int i, j, o, u, total, equal
    cdef float similarity
    cdef list word_diff
    cdef list lis
    cdef list j_indices = []

    # Base cases
    if ostart >= oend and ustart >= uend:
        return result
    elif ostart >= oend:
        return [("", line) for line in upd[ustart:uend]]
    elif ustart >= uend:
        return [(line, "") for line in orig[ostart:oend]]

    # Find unique lines for anchoring
    for i in range(ostart, oend):
        line = orig[i]
        orig_uniques[line] = -1 if line in orig_uniques else i

    for j in range(ustart, uend):
        line = upd[j]
        upd_uniques[line] = -1 if line in upd_uniques else j

    # Find common unique lines
    common = []
    for line, i in orig_uniques.items():
        if i != -1 and (j := upd_uniques.get(line, -1)) != -1:
            common.append((i, j))

    # Find LIS of common indices
    j_indices = [j for _, j in common]
    lis = _longest_increasing_subsequence(j_indices)

    if not lis:
        # No common anchors, perform Myers-like line diff
        o, u = ostart, ustart
        while o < oend and u < uend:
            result.append((orig[o], upd[u]))

            o += 1
            u += 1

        # Add remaining lines
        result.extend((line, "") for line in orig[o:oend])
        result.extend(("", line) for line in upd[u:uend])
        return result

    # Recurse between anchors
    cdef int prev_o = ostart
    cdef int prev_u = ustart
    for j_idx in lis:
        for i, j in common:
            if j == j_idx:
                result += _diff_recursive(orig, upd, prev_o, i, prev_u, j)
                result.append((orig[i], upd[j]))
                prev_o = i + 1
                prev_u = j + 1
                break

    # Add remaining after last anchor
    result += _diff_recursive(orig, upd, prev_o, oend, prev_u, uend)
    return result


cpdef list _longest_increasing_subsequence(list indices):
    cdef list tails = []
    cdef int idx, lo, hi, mid
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

# ---------------------------------------------------------------------
# Hunk processing
# ---------------------------------------------------------------------



cdef dict _create_diff_entry(str orig_line, str upd_line, int* old_line_num, int* new_line_num, float threshold=0.4):
    cdef dict entry = {}
    cdef int line_number_old = 0
    cdef int line_number_new = 0

    if orig_line:
        old_line_num[0] += 1
        line_number_old = old_line_num[0]
    if upd_line:
        new_line_num[0] += 1
        line_number_new = new_line_num[0]

    if orig_line == upd_line:
        entry.update({
            "type": "equal",
            "line_number_old": line_number_old,
            "line_number_new": line_number_new,
            "content": orig_line
        })
    elif not orig_line:
        entry.update({
            "type": "insert",
            "line_number_new": line_number_new,
            "content_new": upd_line
        })
    elif not upd_line:
        entry.update({
            "type": "delete",
            "line_number_old": line_number_old,
            "content_old": orig_line
        })
    else:
        # Analyze similarity
        word_diff = diff_line(orig_line, upd_line)
        total = len(word_diff)
        equal = sum(1 for t, _ in word_diff if t == "equal")
        similarity = equal / total if total else 0.0

        if similarity < threshold:
            # Treat as hard replace (mimicking delete + insert), no inline diff
            entry.update({
                "type": "replace",
                "line_number_old": line_number_old,
                "line_number_new": line_number_new,
                "content_old": orig_line,
                "content_new": upd_line
            })
        else:
            # Soft replace with inline diff
            entry.update({
                "type": "replace",
                "line_number_old": line_number_old,
                "line_number_new": line_number_new,
                "content_old": orig_line,
                "content_new": upd_line,
                "inline_diff": [{"type": t, "value": v} for t, v in word_diff]
            })

    return {k: v for k, v in entry.items() if v is not None}


cdef list _group_hunks(list diff_entries):
    cdef list hunks = []
    cdef list current_hunk = []

    for entry in diff_entries:
        if entry["type"] == "equal":
            if current_hunk:
                hunks.append(_build_hunk(current_hunk))
                current_hunk = []
        else:
            current_hunk.append(entry)

    if current_hunk:
        hunks.append(_build_hunk(current_hunk))

    return hunks

cdef dict _build_hunk(list hunk_entries):
    cdef int min_old = 2**30
    cdef int max_old = -1
    cdef int min_new = 2**30
    cdef int max_new = -1

    for entry in hunk_entries:
        if "line_number_old" in entry:
            ln = entry["line_number_old"]
            min_old = min(min_old, ln)
            max_old = max(max_old, ln)
        if "line_number_new" in entry:
            ln = entry["line_number_new"]
            min_new = min(min_new, ln)
            max_new = max(max_new, ln)

    return {
        "old_range": {"start": min_old, "end": max_old},
        "new_range": {"start": min_new, "end": max_new},
        "lines": hunk_entries
    }

# ---------------------------------------------------------------------
# API for processing Hunks
# ---------------------------------------------------------------------


cpdef dict diff_hunks(str original, str updated, float threshold=0.4):
    cdef list raw_diff = _compute_raw_diff(original, updated)
    cdef list diff_entries = []
    cdef int old_line_num = 0
    cdef int new_line_num = 0

    for orig_line, upd_line in raw_diff:
        entry = _create_diff_entry(orig_line, upd_line, &old_line_num, &new_line_num, threshold)
        if entry:
            diff_entries.append(entry)

    return {"hunks": _group_hunks(diff_entries)}
