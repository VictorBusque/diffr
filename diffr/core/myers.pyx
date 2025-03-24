# cython: boundscheck=False, wraparound=False
# cython: language_level=3

from libc.stdlib cimport malloc, free
cimport cython
from libc.string cimport memcpy
from cpython.pycapsule cimport PyCapsule_New, PyCapsule_GetPointer

@cython.inline
cdef bint is_separator(int ch):
    return ch == 32 or (9 <= ch <= 13)

@cython.inline
cdef bint is_alphanumeric(int ch):
    return (48 <= ch <= 57) or (65 <= ch <= 90) or (97 <= ch <= 122) or (ch == 95)

@cython.final
cpdef list[str] tokenize(str text):
    cdef:
        Py_ssize_t i = 0, n = len(text), start
        list tokens = []
        int ch

    while i < n:
        ch = ord(text[i])
        if is_separator(ch):
            # Group separators together as tokens
            start = i
            while i < n and is_separator(ord(text[i])):
                i += 1
            tokens.append(text[start:i])
        elif is_alphanumeric(ch):
            start = i
            while i < n:
                ch = ord(text[i])
                if not is_alphanumeric(ch):
                    break
                i += 1
            tokens.append(text[start:i])
        else:
            tokens.append(text[i])
            i += 1

    return tokens


@cython.final
cpdef list[tuple[str, str]] diff_line(str original, str updated):
    cdef:
        list[str] words1 = tokenize(original) if original else []
        list[str] words2 = tokenize(updated) if updated else []
        Py_ssize_t N = len(words1)
        Py_ssize_t M = len(words2)
        Py_ssize_t max_d, size, i, d, k, k_index, x, y
        int offset
        int* V1 = NULL
        int* V2 = NULL
        int* V = NULL
        list trace = []
        int ch
        object a, b
        int idx, idx1, idx2, down, up
        bint toggle = True
        int* snapshot = NULL

    if N == 0 and M == 0:
        return []
    if N == 0:
        return [("insert", w) for w in words2]
    if M == 0:
        return [("delete", w) for w in words1]

    max_d = N + M
    size = 2 * max_d + 1
    offset = max_d

    V1 = <int*> malloc(size * sizeof(int))
    V2 = <int*> malloc(size * sizeof(int))
    if not V1 or not V2:
        if V1: free(V1)
        if V2: free(V2)
        raise MemoryError()

    for i in range(size):
        V1[i] = -1
        V2[i] = -1
    V1[offset] = 0
    V = V1

    try:
        # Initial snake
        x = V[offset]
        y = x
        while x < N and y < M:
            a = words1[x]
            b = words2[y]
            if a is b or a == b:
                x += 1
                y += 1
            else:
                break
        V[offset] = x
        if x >= N and y >= M:
            return [("equal", token) for token in words1]

        snapshot = <int*> malloc(size * sizeof(int))
        if not snapshot:
            raise MemoryError()
        memcpy(snapshot, V, size * sizeof(int))
        trace.append(PyCapsule_New(snapshot, b"V_ptr", NULL))

        for d in range(1, max_d + 1):
            V = V2 if toggle else V1
            memcpy(V, V1 if toggle else V2, size * sizeof(int))
            toggle = not toggle

            for k in range(-d, d + 1, 2):
                k_index = k + offset
                if k == -d:
                    idx = (k + 1) + offset
                    x = 0 if idx < 0 or idx >= size else (V1 if toggle else V2)[idx]
                elif k == d:
                    idx = (k - 1) + offset
                    x = 0 if idx < 0 or idx >= size else (V1 if toggle else V2)[idx] + 1
                else:
                    idx1 = (k - 1) + offset
                    idx2 = (k + 1) + offset
                    down = -1 if idx1 < 0 or idx1 >= size else (V1 if toggle else V2)[idx1]
                    up = 0 if idx2 < 0 or idx2 >= size else (V1 if toggle else V2)[idx2]
                    x = up if down < up else down + 1
                y = x - k
                while x < N and y < M:
                    a = words1[x]
                    b = words2[y]
                    if a is b or a == b:
                        x += 1
                        y += 1
                    else:
                        break
                V[k_index] = x
                if x >= N and y >= M:
                    snapshot = <int*> malloc(size * sizeof(int))
                    if not snapshot:
                        raise MemoryError()
                    memcpy(snapshot, V, size * sizeof(int))
                    trace.append(PyCapsule_New(snapshot, b"V_ptr", NULL))
                    return _backtrack_fast(words1, words2, trace, offset, size)

            snapshot = <int*> malloc(size * sizeof(int))
            if not snapshot:
                raise MemoryError()
            memcpy(snapshot, V, size * sizeof(int))
            trace.append(PyCapsule_New(snapshot, b"V_ptr", NULL))

    finally:
        if V1: free(V1)
        if V2: free(V2)

    return _backtrack_fast(words1, words2, trace, offset, size)


cdef list _backtrack_fast(list words1, list words2, list trace, int offset, Py_ssize_t size):
    cdef:
        list script = []
        Py_ssize_t x = len(words1)
        Py_ssize_t y = len(words2)
        Py_ssize_t n_trace = len(trace)
        Py_ssize_t d, k, prev_k, prev_x, prev_y, snake_len, i
        int* v
        int left, right
        bint is_insert
        int idx
        cdef str tag_equal = "equal"
        cdef str tag_insert = "insert"
        cdef str tag_delete = "delete"

    for d in range(n_trace - 1, 0, -1):
        v = <int*> PyCapsule_GetPointer(trace[d - 1], b"V_ptr")
        k = x - y
        idx = (k - 1) + offset
        left = -1 if idx < 0 or idx >= size else v[idx]
        idx = (k + 1) + offset
        right = -1 if idx < 0 or idx >= size else v[idx]
        if k == -d or (k != d and left < right):
            prev_k = k + 1
            idx = prev_k + offset
            prev_x = 0 if idx < 0 or idx >= size else v[idx]
            is_insert = True
        else:
            prev_k = k - 1
            idx = prev_k + offset
            prev_x = 0 if idx < 0 or idx >= size else v[idx] + 1
            is_insert = False
        prev_y = prev_x - prev_k
        snake_len = x - prev_x if (x - prev_x) < (y - prev_y) else y - prev_y
        for i in range(snake_len):
            x -= 1
            y -= 1
            script.append((tag_equal, words1[x]))
        if is_insert:
            y -= 1
            script.append((tag_insert, words2[y]))
        else:
            x -= 1
            script.append((tag_delete, words1[x]))

    snake_len = x if x < y else y
    for i in range(snake_len):
        x -= 1
        y -= 1
        script.append((tag_equal, words1[x]))
    script.reverse()

    for capsule in trace:
        free(<int*> PyCapsule_GetPointer(capsule, b"V_ptr"))
    return script
