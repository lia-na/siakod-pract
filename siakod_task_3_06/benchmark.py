"""Замеры: куча (TimerScheduler) против эталона (NaiveScheduler).

Сценарий для размера n: n раз SET, затем n/2 переносов (повторных SET),
затем несколько команд ADVANCE, шагами проходящие всё время.
Два режима: мало ADVANCE (100 штук) и много (n/10 штук).
Замеряется только прогон команд; генерация данных - вне замера.
Прогрева нет (в CPython нет JIT); по каждому размеру 7 повторов, берётся медиана.
"""
import random
import statistics
import time
import tracemalloc

from timers import NaiveScheduler, TimerScheduler

REPEATS = 7


def make_commands(n, steps):
    rnd = random.Random(42)
    horizon = n * 10
    cmds = [("SET", i, rnd.randint(0, horizon)) for i in range(n)]
    cmds += [("SET", rnd.randrange(n), rnd.randint(0, horizon)) for _ in range(n // 2)]
    cmds += [("ADVANCE", horizon * k // steps) for k in range(1, steps + 1)]
    return cmds


def run(sched_class, cmds):
    s = sched_class()
    fired_count = 0
    for c in cmds:
        if c[0] == "SET":
            s.set(c[1], c[2])
        else:
            fired_count += len(s.advance(c[1]))
    return fired_count


def measure(sched_class, cmds):
    """Возвращает (медиана времени в мс, число сработавших таймеров)."""
    times = []
    result = 0
    for _ in range(REPEATS):
        t0 = time.perf_counter_ns()
        result = run(sched_class, cmds)
        times.append(time.perf_counter_ns() - t0)
    return statistics.median(times) / 1e6, result


def peak_memory_kb(sched_class, cmds):
    tracemalloc.start()
    run(sched_class, cmds)
    peak = tracemalloc.get_traced_memory()[1]
    tracemalloc.stop()
    return peak / 1024


def table(title, steps_for):
    print(title)
    print(f"{'n':>8} {'куча, мс':>10} {'эталон, мс':>11} {'куча, КБ':>10} {'эталон, КБ':>11}")
    checksum = 0
    n = 1000
    while n <= 16000:
        cmds = make_commands(n, steps_for(n))
        t_heap, fired_heap = measure(TimerScheduler, cmds)
        t_naive, fired_naive = measure(NaiveScheduler, cmds)
        assert fired_heap == fired_naive             # куча и эталон дали одно и то же
        checksum += fired_heap                       # результат используется и печатается
        m_heap = peak_memory_kb(TimerScheduler, cmds)
        m_naive = peak_memory_kb(NaiveScheduler, cmds)
        print(f"{n:>8} {t_heap:>10.1f} {t_naive:>11.1f} {m_heap:>10.0f} {m_naive:>11.0f}")
        n *= 2
    print("контрольная сумма (число сработавших):", checksum)
    print()


if __name__ == "__main__":
    table("Мало ADVANCE (100 штук):", lambda n: 100)
    table("Много ADVANCE (n/10 штук):", lambda n: n // 10)

    # Размер кучи с учётом устаревших назначений
    s = TimerScheduler()
    for i in range(1000):
        s.set(i, 10**9)
    for _ in range(9):                      # каждый из 1000 таймеров переносим 9 раз
        for i in range(1000):
            s.set(i, 10**9)
    print("активных таймеров:", len(s.active), "| назначений в куче:", s.heap.size())
