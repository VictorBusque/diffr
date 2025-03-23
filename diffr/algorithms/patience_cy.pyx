# cython: boundscheck=False, wraparound=False, cdivision=True

from typing import List, Tuple
from .myers_cy import diff_line

cpdef List[Tuple[str, str]] patience_diff(str original, str updated):
    """
    Compute a diff between two texts using a patience diff algorithm.
    Returns a list of (original_line, updated_line) tuples.
    For unchanged lines, both strings are equal.
    For insertions/deletions one side is the empty string.
    """
    cdef list orig_lines = original.splitlines()
    cdef list upd_lines = updated.splitlines()
    return _diff_recursive(orig_lines, upd_lines, 0, len(orig_lines), 0, len(upd_lines))


cdef list _diff_recursive(list orig, list upd, int ostart, int oend, int ustart, int uend):
    """
    Recursively diff the slices orig[ostart:oend] and upd[ustart:uend]
    using the patience algorithm.
    """
    cdef list result = []
    cdef int i, j, k

    cdef int len_orig
    cdef int len_upd
    cdef int min_len

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
        # No common anchors were found.
        # Fallback: if both slices contain exactly one line, run diff_line.
        if (ostart + 1 == oend) and (ustart + 1 == uend):
            if ostart < len(orig) and ustart < len(upd):
                result.extend(diff_line(orig[ostart], upd[ustart]))
                return result
        else:
            # Otherwise, pair as many lines as possible and mark extras as additions or deletions.
            len_orig = oend - ostart
            len_upd = uend - ustart
            min_len = len_orig if len_orig < len_upd else len_upd
            for k in range(min_len):
                result.extend(diff_line(orig[ostart+k], upd[ustart+k]))
            for k in range(min_len, len_orig):
                result.append((orig[ostart+k], ""))
            for k in range(min_len, len_upd):
                result.append(("", upd[ustart+k]))
            return result

    # Recursively diff segments around each anchor.
    cdef int prev_o = ostart
    cdef int prev_u = ustart
    cdef tuple anchor
    for anchor in lis:
        i = anchor[0]
        j = anchor[1]
        # Diff the segment before the common anchor.
        result.extend(_diff_recursive(orig, upd, prev_o, i, prev_u, j))
        # The anchor itself is common.
        result.append((orig[i], upd[j]))
        prev_o = i + 1
        prev_u = j + 1
    # Diff any remaining segment after the last anchor.
    result.extend(_diff_recursive(orig, upd, prev_o, oend, prev_u, uend))
    return result


cdef list _longest_increasing_subsequence(list common):
    """
    Given a list of tuples (i, j, line) sorted by i (and then j),
    compute the longest increasing subsequence based on the j values.
    Returns the subsequence as a list of tuples.
    """
    cdef int n = len(common)
    if n == 0:
        return []
    cdef list tails = []          # stores the last j value of each subsequence length
    cdef list tails_indices = []  # stores indices in 'common' corresponding to tails
    cdef list prev = [0] * n      # predecessor indices for reconstruction
    cdef int index, pos, lo, hi, mid
    cdef tuple curr

    # Initialize predecessor list.
    for index in range(n):
        prev[index] = -1

    for index in range(n):
        curr = common[index]
        # Binary search in tails for the insertion point for curr[1].
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

    # Reconstruct the longest increasing subsequence.
    cdef list lis = []
    pos = tails_indices[-1]
    while pos != -1:
        lis.append(common[pos])
        pos = prev[pos]
    lis.reverse()
    return lis
