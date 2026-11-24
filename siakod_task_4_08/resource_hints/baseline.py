
def find_one_mismatch_bruteforce(names, query):
    result = []
    for name in names:
        if len(name) != len(query):
            continue
        diff = sum(1 for a, b in zip(name, query) if a != b)
        if diff == 1:
            result.append(name)
    return sorted(result)
