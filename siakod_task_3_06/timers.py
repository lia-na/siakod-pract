from heap import BinaryHeap


class TimerScheduler:
    """Таймеры с переносом и отменой: min-куча назначений + словарь активных.

    В куче лежат кортежи (at, seq, id): сравнение даёт сначала время,
    при равенстве - порядок назначений (seq растёт с каждым SET).
    В словаре active: id -> seq актуального назначения.
    Старые назначения из кучи не удаляются: при извлечении их узнают по seq.
    """

    def __init__(self):
        self.heap = BinaryHeap()
        self.active = {}
        self.seq = 0

    def set(self, id, at):
        self.seq += 1
        self.active[id] = self.seq        # прежнее назначение этого id устарело
        self.heap.push((at, self.seq, id))

    def cancel(self, id):
        self.active.pop(id, None)         # нет такого id - ничего не делаем

    def advance(self, to):
        """Вернуть список (id, момент срабатывания) для таймеров с at <= to."""
        fired = []
        while self.heap.size() > 0 and self.heap.peek()[0] <= to:
            at, seq, id = self.heap.pop()
            if self.active.get(id) == seq:  # актуальное назначение
                del self.active[id]
                fired.append((id, at))
            # иначе назначение устарело (перенесено/отменено) - пропускаем
        return fired


class NaiveScheduler:
    """Эталон: словарь активных назначений, при ADVANCE - фильтрация и сортировка."""

    def __init__(self):
        self.active = {}                  # id -> (at, seq)
        self.seq = 0

    def set(self, id, at):
        self.seq += 1
        self.active[id] = (at, self.seq)

    def cancel(self, id):
        self.active.pop(id, None)

    def advance(self, to):
        due = [(at, seq, id) for id, (at, seq) in self.active.items() if at <= to]
        due.sort()
        for at, seq, id in due:
            del self.active[id]
        return [(id, at) for at, seq, id in due]
