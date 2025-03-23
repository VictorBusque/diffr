# cython: boundscheck=False, wraparound=False
# cython: language_level=3

from libc.stdlib cimport malloc, free
cimport cython
from cpython.pycapsule cimport PyCapsule_New, PyCapsule_GetPointer

# Helpers for character classification remain unchanged.
@cython.inline
cdef bint is_ascii_space(int ch) nogil:
    return ch == 32 or (9 <= ch <= 13)

@cython.inline
cdef bint is_alnum_or_underscore(int ch) nogil:
    return (48 <= ch <= 57) or (65 <= ch <= 90) or (97 <= ch <= 122) or (ch == 95)

# Helper functions to mimic dict.get() behavior.
@cython.inline
cdef int get_insertion(int* arr, int key, int offset, Py_ssize_t size) nogil:
    cdef int idx = key + offset
    if idx < 0 or idx >= size:
         return 0
    return arr[idx]

@cython.inline
cdef int get_deletion(int* arr, int key, int offset, Py_ssize_t size) nogil:
    cdef int idx = key + offset
    if idx < 0 or idx >= size:
         return -1
    return arr[idx]

@cython.final
cpdef list[str] tokenize(str text):
    cdef list tokens = []
    cdef Py_ssize_t i = 0, n = len(text)
    cdef Py_ssize_t start
    cdef int ch
    while i < n:
        ch = ord(text[i])
        if is_ascii_space(ch):
            i += 1
            continue
        if is_alnum_or_underscore(ch):
            start = i
            while i < n:
                ch = ord(text[i])
                if not is_alnum_or_underscore(ch):
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
    cdef list[str] words1 = tokenize(original) if original else []
    cdef list[str] words2 = tokenize(updated) if updated else []
    
    cdef Py_ssize_t N = len(words1)
    cdef Py_ssize_t M = len(words2)
    if N == 0 and M == 0:
         return []
    if N == 0:
         return [("insert", w) for w in words2]
    if M == 0:
         return [("delete", w) for w in words1]

    cdef Py_ssize_t max_d = N + M
    cdef Py_ssize_t size = 2 * max_d + 1
    cdef int offset = max_d
    cdef Py_ssize_t i, d, k, k_index, x, y

    # Allocate the initial V array.
    cdef int* V = <int*> malloc(size * sizeof(int))
    if not V:
         raise MemoryError()
    # Initialize V: all entries -1, then set V[offset] = 0.
    for i in range(size):
         V[i] = -1
    V[offset] = 0

    # --- Initial snake advancement (d=0) ---
    x = V[offset]
    y = x  # since k == 0 for d=0
    while x < N and y < M and words1[x] == words2[y]:
         x += 1
         y += 1
    V[offset] = x
    # If the entire sequences match, we can return immediately.
    if x >= N and y >= M:
         # Build a script marking all tokens as equal.
         return [("equal", token) for token in words1]
    
    # Trace stores a PyCapsule wrapping each V array.
    cdef list trace = []
    trace.append(PyCapsule_New(V, b"V_ptr", NULL))

    cdef int* current_V
    # Forward pass: iterate d = 1 to max_d.
    for d in range(1, max_d + 1):
         current_V = <int*> malloc(size * sizeof(int))
         if not current_V:
              for capsule in trace:
                   free(<int*> PyCapsule_GetPointer(capsule, b"V_ptr"))
              raise MemoryError()
         # Copy the previous V.
         for i in range(size):
              current_V[i] = V[i]
         for k in range(-d, d + 1, 2):
              k_index = k + offset
              if k == -d:
                   x = get_insertion(V, k + 1, offset, size)
              elif k == d:
                   x = get_deletion(V, k - 1, offset, size) + 1
              else:
                   if get_deletion(V, k - 1, offset, size) < get_deletion(V, k + 1, offset, size):
                        x = get_insertion(V, k + 1, offset, size)
                   else:
                        x = get_deletion(V, k - 1, offset, size) + 1
              y = x - k
              while x < N and y < M and words1[x] == words2[y]:
                   x += 1
                   y += 1
              current_V[k_index] = x
              if x >= N and y >= M:
                   trace.append(PyCapsule_New(current_V, b"V_ptr", NULL))
                   return _backtrack_fast(words1, words2, trace, offset, size)
         trace.append(PyCapsule_New(current_V, b"V_ptr", NULL))
         V = current_V  # use the new V for next iteration
    return _backtrack_fast(words1, words2, trace, offset, size)

cdef list _backtrack_fast(list words1, list words2, list trace, int offset, Py_ssize_t size):
    """
    Backtracks over the stored V arrays (extracted from PyCapsules) to reconstruct
    the edit script. Each V array is freed exactly once.
    """
    cdef list script = []
    cdef Py_ssize_t x = len(words1)
    cdef Py_ssize_t y = len(words2)
    cdef Py_ssize_t n_trace = len(trace)
    cdef Py_ssize_t d, k, prev_k, prev_x, prev_y, snake_len, i
    cdef int* v
    cdef int left, right
    cdef bint is_insert

    for d in range(n_trace - 1, 0, -1):
         v = <int*> PyCapsule_GetPointer(trace[d - 1], b"V_ptr")
         k = x - y
         left = get_deletion(v, k - 1, offset, size)
         right = get_deletion(v, k + 1, offset, size)
         if k == -d or (k != d and left < right):
              prev_k = k + 1
              prev_x = get_insertion(v, prev_k, offset, size)
              is_insert = True
         else:
              prev_k = k - 1
              prev_x = get_deletion(v, prev_k, offset, size) + 1
              is_insert = False
         prev_y = prev_x - prev_k
         snake_len = (x - prev_x) if (x - prev_x) < (y - prev_y) else (y - prev_y)
         for i in range(snake_len):
              x -= 1
              y -= 1
              script.append(("equal", words1[x]))
         if is_insert:
              y -= 1
              script.append(("insert", words2[y]))
         else:
              x -= 1
              script.append(("delete", words1[x]))
    snake_len = x if x < y else y
    for i in range(snake_len):
         x -= 1
         y -= 1
         script.append(("equal", words1[x]))
    script.reverse()
    for capsule in trace:
         free(<int*> PyCapsule_GetPointer(capsule, b"V_ptr"))
    return script
