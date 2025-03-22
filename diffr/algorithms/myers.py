import re

compiled_re = re.compile(r"\w+|[^\w\s]", re.UNICODE)


def tokenize(text: str) -> list:
    tokens = compiled_re.findall(text, re.UNICODE)
    return tokens


def diff_line(original: str, updated: str) -> list:
    words1 = tokenize(original) if original else []
    words2 = tokenize(updated) if updated else []
    N, M = len(words1), len(words2)

    if N == 0 and M == 0:
        return []
    if N == 0:
        return [{"op": "insert", "words": [word]} for word in words2]
    if M == 0:
        return [{"op": "delete", "words": [word]} for word in words1]

    max_d = N + M
    V = {0: 0}
    trace = []

    for d in range(max_d + 1):
        current_V = {}
        for k in range(-d, d + 1, 2):
            if k == -d or (k != d and V.get(k - 1, -1) < V.get(k + 1, -1)):
                x = V.get(k + 1, 0)  # Insert
            else:
                x = V.get(k - 1, 0) + 1  # Delete
            y = x - k

            # Snake forward while words match
            while x < N and y < M and words1[x] == words2[y]:
                x += 1
                y += 1

            current_V[k] = x

            if x >= N and y >= M:
                trace.append(current_V)
                return _backtrack(words1, words2, trace)

        trace.append(current_V)
        V = current_V


def _backtrack(words1, words2, trace):
    script = []
    x, y = len(words1), len(words2)

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
