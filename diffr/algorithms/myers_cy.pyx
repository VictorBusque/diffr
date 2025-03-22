import re
from libc.stdlib cimport malloc, free


compiled_re = re.compile(r"\w+|[^\w\s]", re.UNICODE)


cpdef list[str] tokenize(text: str):
    tokens = compiled_re.findall(text, re.UNICODE)
    return tokens


cpdef list diff_line(str original, str updated):
    cdef list[str] words1 = tokenize(original) if original else []
    cdef list[str] words2 = tokenize(updated) if updated else []
    cdef int N = len(words1)
    cdef int M = len(words2)

    if N == 0 and M == 0:
        return []
    if N == 0:
        return [{"op": "insert", "words": [word]} for word in words2]
    if M == 0:
        return [{"op": "delete", "words": [word]} for word in words1]

    cdef int max_d = N + M
    cdef dict V = {0: 0}
    cdef list trace = []

    cdef int d, k, x, y, prev_x, prev_y, prev_k, v_km, v_kp
    cdef dict current_V

    cdef str w1, w2


    for d in range(max_d + 1):
        current_V = {}
        
        for k in range(-d, d + 1, 2):
            v_km = V.get(k - 1, -1)
            v_kp = V.get(k + 1, -1)
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


cpdef list _backtrack(list words1, list words2, list trace):
    cdef list script = []
    cdef int x = len(words1)
    cdef int y = len(words2)

    cdef dict v
    cdef int d, k, prev_k, prev_x, prev_y
    cdef str op

    for d in range(len(trace) - 1, 0, -1):
        v = trace[d - 1]  # ← FIXED: we came from the previous step
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
            script.append({"op": "equal", "words": [words1[x]]})

        # Record the actual insert/delete
        if op == "insert":
            y -= 1
            script.append({"op": "insert", "words": [words2[y]]})
        else:
            x -= 1
            script.append({"op": "delete", "words": [words1[x]]})

    # Final snake to beginning if needed
    while x > 0 and y > 0 and words1[x - 1] == words2[y - 1]:
        x -= 1
        y -= 1
        script.append({"op": "equal", "words": [words1[x]]})

    script.reverse()
    return script


if __name__ == "__main__":
    original = "I love writing code"
    updated = "I enjoy writing Python code"

    result = diff_line(original, updated)
    for r in result:
        print(r)
