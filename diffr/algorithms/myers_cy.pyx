# cython: boundscheck=False, wraparound=False

import re
from libc.stdlib cimport malloc, free


# cython: language_level=3

from cpython.unicode cimport (
    PyUnicode_READ, PyUnicode_KIND, PyUnicode_DATA,
    Py_UNICODE_ISALNUM, Py_UNICODE_ISSPACE
)
cimport cython

cpdef list[str] tokenize(str text):
    """
    Tokenizes the given text into a list of tokens where each token is either
    a contiguous sequence of word characters (letters, digits, underscore)
    or a single non-whitespace, non-word character.
    
    This implementation replicates the behavior of:
        re.compile(r"\w+|[^\w\s]", re.UNICODE).findall(text)
    """
    cdef list[str] tokens = []
    cdef Py_ssize_t i = 0, start, n = len(text)
    cdef int kind = PyUnicode_KIND(text)
    cdef void *data = PyUnicode_DATA(text)
    cdef Py_UCS4 ch

    while i < n:
        ch = PyUnicode_READ(kind, data, i)
        # Skip whitespace characters.
        if Py_UNICODE_ISSPACE(ch):
            i += 1
        # If the character is a word character (alphanumeric) or underscore,
        # collect a full token.
        elif Py_UNICODE_ISALNUM(ch) or ch == 95:  # 95 is the ASCII code for '_'
            start = i
            while i < n:
                ch = PyUnicode_READ(kind, data, i)
                if not (Py_UNICODE_ISALNUM(ch) or ch == 95):
                    break
                i += 1
            tokens.append(text[start:i])
        else:
            # For punctuation (or any other non-word, non-whitespace character),
            # add the single character as a token.
            tokens.append(text[i:i+1])
            i += 1
    return tokens



cpdef list[tuple[str, str]] diff_line(str original, str updated):
    cdef list[str] words1 = tokenize(original) if original else []
    cdef list[str] words2 = tokenize(updated) if updated else []
    
    cdef Py_ssize_t N = len(words1)
    cdef Py_ssize_t M = len(words2)

    if N == 0 and M == 0:
        return []
    if N == 0:
        return [{"op": "insert", "words": [word]} for word in words2]
    if M == 0:
        return [{"op": "delete", "words": [word]} for word in words1]

    cdef Py_ssize_t max_d = N + M
    cdef dict[int, int] V = {0: 0}
    cdef list[dict[int, int]] trace = []

    cdef Py_ssize_t d, k, x, y, prev_x, prev_y, prev_k, v_km, v_kp
    cdef dict[int, int] current_V

    cdef str w1, w2
    cdef list[tuple[str, str]] backtrack

    for d in range(max_d + 1):
        current_V = {}
        
        for k in range(-d, d + 1, 2):
            v_km = V[k - 1] if (k - 1) in V else -1
            v_kp = V[k + 1] if (k + 1) in V else -1
        
            if k == -d or (k != d and v_km < v_kp):
                x = V.get(k + 1, 0)  # Insert
            else:
                x = V.get(k - 1, 0) + 1  # Delete
            y = x - k

            # Snake forward while words match
            while x < N and y < M:
                w1 = words1[x]
                w2 = words2[y]
                if w1 != w2:
                    break
                x += 1
                y += 1
            current_V[k] = x

            if x >= N and y >= M:
                trace.append(current_V)
                return _backtrack(words1, words2, trace)

        trace.append(current_V)
        V = current_V


cpdef list[tuple[str, str]] _backtrack(list[str] words1, list[str] words2, list trace):
    cdef list[tuple[str, str]] script = []
    cdef Py_ssize_t x = len(words1)
    cdef Py_ssize_t y = len(words2)

    cdef dict[int, int] v
    cdef Py_ssize_t d, k, prev_k, prev_x, prev_y
    cdef str op

    for d in range(len(trace) - 1, 0, -1):
        v = trace[d - 1]
        k = x - y

        if k == -d or (k != d and v.get(k - 1, -1) < v.get(k + 1, -1)):
            prev_k = k + 1
            prev_x = v.get(prev_k, 0)
            prev_y = prev_x - prev_k
            op = "insert"
        else:
            prev_k = k - 1
            prev_x = v.get(prev_k, 0) + 1
            prev_y = prev_x - prev_k
            op = "delete"

        # Snake back through matches
        while x > prev_x and y > prev_y:
            x -= 1
            y -= 1
            script.append(("equal", words1[x]))

        # Record the actual insert/delete
        if op == "insert":
            y -= 1
            script.append(("insert", words2[y]))
        else:
            x -= 1
            script.append(("delete", words1[x]))

    # Final snake to beginning if needed
    while x > 0 and y > 0 and words1[x - 1] == words2[y - 1]:
        x -= 1
        y -= 1
        script.append(("equal", words1[x]))

    script.reverse()
    return script


if __name__ == "__main__":
    original = "I love writing code"
    updated = "I enjoy writing Python code"

    result = diff_line(original, updated)
    for r in result:
        print(r)
