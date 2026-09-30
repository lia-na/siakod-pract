import csv
import random
import statistics
import time

from solution import naive_match, two_pointer_match

ELEMENT_SIZE_BYTES = 8
WARMUP_RUNS = 2
REPEATS = 7  #взять медиану


def generate_logs(n, m, seed):
    rnd = random.Random(seed)
    log1 = sorted(rnd.randint(0, 10 ** 9) for _ in range(n))
    log2 = sorted(rnd.randint(0, 10 ** 9) for _ in range(m))
    return log1, log2


def measure_once(func, log1, log2): #один прогон
    start = time.perf_counter_ns() #наносекунды
    result = func(log1, log2)
    elapsed = time.perf_counter_ns() - start
    checksum = len(result) + (result[-1] or 0 if result else 0)
    return elapsed, checksum


def measure_median(func, log1, log2): #прогрев
    acc = 0
    for _ in range(WARMUP_RUNS):
        _, cs = measure_once(func, log1, log2) # распаковка кортежа + добавить только время
        acc += cs

    times = []
    for _ in range(REPEATS):
        t, cs = measure_once(func, log1, log2) #замер
        times.append(t)
        acc += cs

    return statistics.median(times), acc


def run_benchmark(sizes, algorithms, out_csv):
    rows = []
    for n in sizes:
        m = n
        log1, log2 = generate_logs(n, m, seed=n)
        volume_bytes = (n + m) * ELEMENT_SIZE_BYTES

        row = {"n": n, "m": m, "volume_bytes": volume_bytes}
        for name, func in algorithms.items():
            median_ns, _ = measure_median(func, log1, log2)
            row[name] = median_ns
            print(f"N={n:>8}  volume_bytes={volume_bytes:>10}  {name:>16} = {median_ns/1e6:>10.3f} ms")
        rows.append(row)

    fieldnames = ["n", "m", "volume_bytes"] + list(algorithms.keys())
    with open(out_csv, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    return rows


if __name__ == "__main__":
    sizes_both = [50, 100, 200, 400, 800, 1600, 3200, 6400, 12800]

    print("naive_match vs two_pointer_match")
    run_benchmark(
        sizes_both,
        {"naive_ns": naive_match, "two_pointer_ns": two_pointer_match},
        "results_both.csv",
    )

    print()
    print("two_pointer_match на больших N ")
    sizes_large = [12800, 25600, 51200, 102400, 204800, 409600, 819200]
    run_benchmark(
        sizes_large,
        {"two_pointer_ns": two_pointer_match},
        "results_large.csv",
    )

