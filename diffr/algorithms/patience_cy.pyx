# cython: boundscheck=True, wraparound=True, cdivision=False

from typing import List, Tuple
# Import diff_line from your Myers diff module.
from .myers_cy import diff_line
from diffr.data_models.diff import PatienceDiffResult, LineDiff, TokenDiff
from diffr.utils.intra_line_differ import compute_token_diffs

def patience_diff(original: str, updated: str) -> List[Tuple[str, str]]:
    """
    Compute a diff between two texts using a patience diff algorithm.
    Returns a list of (original_line, updated_line) tuples.
    For unchanged lines, both strings are equal.
    For insertions/deletions one side is the empty string.
    """
    orig_lines = original.splitlines()
    upd_lines = updated.splitlines()
    return _diff_recursive(orig_lines, upd_lines, 0, len(orig_lines), 0, len(upd_lines))

def _diff_recursive(orig, upd, int ostart, int oend, int ustart, int uend):
    """
    Recursively diff the slices orig[ostart:oend] and upd[ustart:uend]
    using the patience algorithm.
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
    prev_o = ostart
    prev_u = ustart
    
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

def _longest_increasing_subsequence(common):
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
    cdef list prev = [ -1 for _ in range(n) ]  # predecessor indices for reconstruction
    cdef int index, pos, lo, hi, mid
    cdef tuple curr

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

    cdef list lis = []
    pos = tails_indices[-1]
    while pos != -1:
        lis.append(common[pos])
        pos = prev[pos]
    lis.reverse()
    return lis

def get_patience_diff_result(original: str, updated: str) -> PatienceDiffResult:
    """
    Compute a diff between two texts and return a PatienceDiffResult model.
    This version includes both line-level and token-level diffs.
    
    Args:
        original: Original text
        updated: Updated text
        
    Returns:
        PatienceDiffResult containing LineDiff and TokenDiff elements
    """
    raw_diff = patience_diff(original, updated)
    diffs = []
    
    for orig, upd in raw_diff:
        if orig == upd:
            # Unchanged lines
            diffs.append(LineDiff(original=orig, updated=upd))
        elif not orig or not upd:
            # Simple addition or deletion
            diffs.append(LineDiff(original=orig, updated=upd))
        else:
            # Changed line - compute token level diffs
            token_diffs = compute_token_diffs(orig, upd)
            diffs.extend(token_diffs)
    
    return PatienceDiffResult(diffs=diffs)
