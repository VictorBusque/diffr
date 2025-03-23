# cython: boundscheck=False, wraparound=False
# cython: language_level=3

cimport cython

@cython.inline
cdef bint is_ascii_space(int ch):
    """
    Check if ch is one of [tab, newline, vertical-tab, form-feed, carriage-return, space].
    Extend if you want to handle other Unicode whitespace.
    """
    if ch in (9, 10, 11, 12, 13, 32):
        return True
    return False

@cython.inline
cdef bint is_alnum_or_underscore(int ch):
    """
    Check for ASCII letters [a-zA-Z], digits [0-9], or underscore '_'.
    Expand as desired for full Unicode support.
    """
    # uppercase letters [A-Z]
    if 65 <= ch <= 90:
        return True
    # lowercase letters [a-z]
    if 97 <= ch <= 122:
        return True
    # digits [0-9]
    if 48 <= ch <= 57:
        return True
    # underscore
    if ch == 95:
        return True
    return False


cpdef list[str] tokenize(str text):
    """
    Tokenizes text into a list of tokens where each token is either a
    contiguous sequence of word-characters (letters, digits, underscore)
    or a single non-whitespace, non-word character.
    """
    cdef list tokens = []
    cdef Py_ssize_t i = 0, n = len(text)
    cdef int ch
    cdef Py_ssize_t start

    while i < n:
        ch = ord(text[i])
        if is_ascii_space(ch):
            i += 1
        elif is_alnum_or_underscore(ch):
            # gather a contiguous run of letters/digits/underscore
            start = i
            while i < n and is_alnum_or_underscore(ord(text[i])):
                i += 1
            tokens.append(text[start:i])
        else:
            # a single punctuation or symbol
            tokens.append(text[i:i+1])
            i += 1

    return tokens

cpdef list[tuple[str, str]] diff_line(str original, str updated):
    # Tokenize input strings into lists of words
    cdef list[str] words1 = tokenize(original) if original else []
    cdef list[str] words2 = tokenize(updated) if updated else []
    
    # Get lengths of the word lists
    cdef Py_ssize_t N = len(words1)
    cdef Py_ssize_t M = len(words2)

    # Handle edge cases
    if N == 0 and M == 0:
        return []
    if N == 0:
        return [("insert", word) for word in words2]
    if M == 0:
        return [("delete", word) for word in words1]

    # Initialize variables for Myers diff algorithm
    cdef Py_ssize_t max_d = N + M
    cdef dict V = {0: 0}  # Diagonal map: k -> x
    cdef list trace = []  # Store V states for backtracking

    cdef Py_ssize_t d, k, x, y, v_km, v_kp
    cdef dict current_V

    # Forward pass: Build the shortest edit path
    for d in range(max_d + 1):
        current_V = {}
        
        for k in range(-d, d + 1, 2):
            # Get furthest x values for adjacent diagonals
            v_km = V.get(k - 1, -1)  # k - 1 (delete direction)
            v_kp = V.get(k + 1, -1)  # k + 1 (insert direction)
        
            # Choose direction: insert or delete
            if k == -d or (k != d and v_km < v_kp):
                x = V.get(k + 1, 0)  # Insert: take x from k + 1
            else:
                x = V.get(k - 1, 0) + 1  # Delete: take x from k - 1 and advance
            y = x - k

            # Snake forward over matching words
            while x < N and y < M and words1[x] == words2[y]:
                x += 1
                y += 1
            current_V[k] = x

            # If end is reached, backtrack
            if x >= N and y >= M:
                trace.append(current_V)
                return _backtrack(words1, words2, trace)

        trace.append(current_V)
        V = current_V

cpdef list[tuple[str, str]] _backtrack(list[str] words1, list[str] words2, list trace):
    cdef list[tuple[str, str]] script = []
    cdef Py_ssize_t x = len(words1)
    cdef Py_ssize_t y = len(words2)

    cdef dict v
    cdef Py_ssize_t d, k, prev_k, prev_x, prev_y
    cdef str op

    # Backward pass: Reconstruct the edit script
    for d in range(len(trace) - 1, 0, -1):
        v = trace[d - 1]
        k = x - y

        # Determine previous step: insert or delete
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

        # Snake back through equal words
        while x > prev_x and y > prev_y:
            x -= 1
            y -= 1
            script.append(("equal", words1[x]))

        # Add the insert or delete operation
        if op == "insert":
            y -= 1
            script.append(("insert", words2[y]))
        else:
            x -= 1
            script.append(("delete", words1[x]))

    # Handle any remaining matches at the start
    while x > 0 and y > 0 and words1[x - 1] == words2[y - 1]:
        x -= 1
        y -= 1
        script.append(("equal", words1[x]))

    script.reverse()
    return script