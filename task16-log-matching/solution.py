from typing import List, Optional


def naive_match(log1: List[float], log2: List[float]) -> List[Optional[float]]:
   
    n = len(log1)
    m = len(log2)

    if m == 0:
        return [None] * n

    result: List[Optional[float]] = []

    for t in log1:
        best_value = log2[0]
        best_dist = abs(t - log2[0])

        for s in log2[1:]:
            d = abs(t - s)
            if d <= best_dist:
                best_dist = d
                best_value = s

        result.append(best_value)

    return result


# второй способ
def two_pointer_match(log1: List[float], log2: List[float]) -> List[Optional[float]]:
    
    n = len(log1)
    m = len(log2)

    if m == 0:
        return [None] * n

    result: List[Optional[float]] = []
    j = 0

    for t in log1:
        while j + 1 < m and abs(log2[j + 1] - t) <= abs(log2[j] - t):
            j += 1
        result.append(log2[j])

    return result
