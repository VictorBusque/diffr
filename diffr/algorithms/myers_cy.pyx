# cython: boundscheck=False, wraparound=False
# cython: language_level=3

from libc.stdlib cimport malloc, free
cimport cython
from libc.string cimport memcpy
from cpython.pycapsule cimport PyCapsule_New, PyCapsule_GetPointer

@cython.final
cpdef list[str] tokenize(str text):
    """
    Fast ASCII-safe tokenizer using str[start:i] directly (CPython optimizations).
    """
    cdef:
        Py_ssize_t i = 0, n = len(text), start
        list tokens = []
        int ch

    while i < n:
        ch = ord(text[i])
        if ch == 32 or (9 <= ch <= 13):  # ASCII whitespace check
            i += 1
            continue

        if (48 <= ch <= 57) or (65 <= ch <= 90) or (97 <= ch <= 122) or (ch == 95):  # alnum or underscore
            start = i
            while i < n:
                ch = ord(text[i])
                if not ((48 <= ch <= 57) or (65 <= ch <= 90) or (97 <= ch <= 122) or (ch == 95)):
                    break
                i += 1
            tokens.append(text[start:i])
        else:
            tokens.append(text[i])
            i += 1

    return tokens


@cython.final
cpdef list[tuple[str, str]] diff_line(str original, str updated):
    """
    A fast Myers diff that uses C arrays (wrapped in PyCapsules) for the diagonal map.
    This version first advances an initial snake (d=0) so that matching tokens at
    the beginning (like "result") are marked as equal.
    """
    cdef:
        list[str] words1 = tokenize(original) if original else []
        list[str] words2 = tokenize(updated) if updated else []
        Py_ssize_t N = len(words1)
        Py_ssize_t M = len(words2)
        Py_ssize_t max_d, size, i, d, k, k_index, x, y
        int offset
        int* V
        list trace
        int* current_V
        int ch
        object a, b   # for token comparisons
        int idx, idx1, idx2, down, up

    if N == 0 and M == 0:
         return []
    if N == 0:
         return [("insert", w) for w in words2]
    if M == 0:
         return [("delete", w) for w in words1]

    max_d = N + M
    size = 2 * max_d + 1
    offset = max_d

    V = <int*> malloc(size * sizeof(int))
    if not V:
         raise MemoryError()
    for i in range(size):
         V[i] = -1
    V[offset] = 0

    # --- Initial snake advancement (d=0) ---
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

    trace = []
    trace.append(PyCapsule_New(V, b"V_ptr", NULL))

    # Forward pass: iterate d = 1 to max_d.
    for d in range(1, max_d + 1):
         current_V = <int*> malloc(size * sizeof(int))
         if not current_V:
              for capsule in trace:
                   free(<int*> PyCapsule_GetPointer(capsule, b"V_ptr"))
              raise MemoryError()
         memcpy(current_V, V, size * sizeof(int))
         for k in range(-d, d + 1, 2):
              k_index = k + offset
              # Inline get_insertion / get_deletion logic:
              if k == -d:
                   idx = (k + 1) + offset
                   if idx < 0 or idx >= size:
                        x = 0
                   else:
                        x = V[idx]
              elif k == d:
                   idx = (k - 1) + offset
                   if idx < 0 or idx >= size:
                        x = 0  # (-1)+1 == 0
                   else:
                        x = V[idx] + 1
              else:
                   idx1 = (k - 1) + offset
                   idx2 = (k + 1) + offset
                   if idx1 < 0 or idx1 >= size:
                        down = -1
                   else:
                        down = V[idx1]
                   if idx2 < 0 or idx2 >= size:
                        up = 0
                   else:
                        up = V[idx2]
                   if down < up:
                        x = up
                   else:
                        x = down + 1
              y = x - k
              # Advance snake while tokens are equal:
              while x < N and y < M:
                    a = words1[x]
                    b = words2[y]
                    if a is b or a == b:
                        x += 1
                        y += 1
                    else:
                        break
              current_V[k_index] = x
              if x >= N and y >= M:
                   trace.append(PyCapsule_New(current_V, b"V_ptr", NULL))
                   return _backtrack_fast(words1, words2, trace, offset, size)
         trace.append(PyCapsule_New(current_V, b"V_ptr", NULL))
         V = current_V  # use the new V for the next iteration

    return _backtrack_fast(words1, words2, trace, offset, size)


cdef list _backtrack_fast(list words1, list words2, list trace, int offset, Py_ssize_t size):
    """
    Backtracks over the stored V arrays (extracted from PyCapsules) to reconstruct
    the edit script. Each V array is freed exactly once.
    """
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
         if idx < 0 or idx >= size:
             left = -1
         else:
             left = v[idx]
         idx = (k + 1) + offset
         if idx < 0 or idx >= size:
             right = -1
         else:
             right = v[idx]
         if k == -d or (k != d and left < right):
              prev_k = k + 1
              idx = prev_k + offset
              if idx < 0 or idx >= size:
                  prev_x = 0
              else:
                  prev_x = v[idx]
              is_insert = True
         else:
              prev_k = k - 1
              idx = prev_k + offset
              if idx < 0 or idx >= size:
                  prev_x = 0
              else:
                  prev_x = v[idx] + 1
              is_insert = False
         prev_y = prev_x - prev_k
         snake_len = (<int>(x - prev_x) if (x - prev_x) < (y - prev_y) else <int>(y - prev_y))
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
