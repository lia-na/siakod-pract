import random
import statistics
import time

from resource_hints.baseline import find_one_mismatch_bruteforce
from resource_hints.char_trie import CharTrie

ALPHABET = "abcdefghijklmnopqrstuvwxyz0123456789_"
NAME_LEN = 12
SIZES = [1_000 * 2 ** k for k in range(8)]   # 1000 ... 128000
QUERIES = 50
REPEATS = 7


def random_name(rnd):
    return "".join(rnd.choice(ALPHABET) for _ in range(NAME_LEN))


def break_one_char(rnd, name):
    i = rnd.randrange(len(name))
    new = rnd.choice([c for c in ALPHABET if c != name[i]])
    return name[:i] + new + name[i + 1:]


def median_ns(func):
    times = []
    for _ in range(REPEATS):
        start = time.perf_counter_ns()
        func()
        times.append(time.perf_counter_ns() - start)
    return statistics.median(times)


def main():
    rnd = random.Random(2024)
    checksum = 0   # результат используется, чтобы вычисление не выбросили
    rows = []
    print(f"{'N':>8} {'trie, мс':>12} {'перебор, мс':>14} {'во сколько раз':>16}")
    for n in SIZES:
        names = list({random_name(rnd) for _ in range(n)})
        trie = CharTrie()
        for name in names:
            trie.put(name)
        queries = [break_one_char(rnd, rnd.choice(names)) for _ in range(QUERIES)]

        def run_trie():
            return sum(len(trie.find_one_mismatch(q)) for q in queries)

        def run_brute():
            return sum(len(find_one_mismatch_bruteforce(names, q)) for q in queries)

        assert run_trie() == run_brute()
        t_trie = median_ns(run_trie)
        t_brute = median_ns(run_brute)
        checksum += run_trie() + run_brute()
        rows.append((n, t_trie, t_brute))
        print(f"{n:>8} {t_trie / 1e6:>12.3f} {t_brute / 1e6:>14.3f} {t_brute / t_trie:>16.1f}")
    print("checksum:", checksum)
    save_plot(rows)


def save_plot(rows):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib не установлен — график пропущен (pip install matplotlib)")
        return
    ns = [r[0] for r in rows]
    plt.loglog(ns, [r[1] / 1e6 for r in rows], "o-", label="trie")
    plt.loglog(ns, [r[2] / 1e6 for r in rows], "s-", label="перебор (эталон)")
    plt.xlabel("размер словаря N")
    plt.ylabel(f"время на {QUERIES} запросов, мс")
    plt.legend()
    plt.grid(True, which="both", alpha=0.3)
    plt.savefig("benchmark.png", dpi=150)
    print("график сохранён: benchmark.png")


if __name__ == "__main__":
    main()
