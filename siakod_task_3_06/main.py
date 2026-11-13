import json
import sys

from timers import NaiveScheduler, TimerScheduler


def main():
    # python3 main.py            - решение на куче
    # python3 main.py --naive    - эталон (словарь + сортировка при ADVANCE)
    sched = NaiveScheduler() if "--naive" in sys.argv else TimerScheduler()
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        cmd = json.loads(line)
        name = cmd["op"]
        if name == "SET":
            sched.set(cmd["id"], cmd["at"])
        elif name == "CANCEL":
            sched.cancel(cmd["id"])
        elif name == "ADVANCE":
            fired = sched.advance(cmd["to"])
            print(json.dumps([{"id": i, "at": at} for i, at in fired]))


if __name__ == "__main__":
    main()
