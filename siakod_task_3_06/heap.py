class BinaryHeap:
    def __init__(self, less=lambda a, b: a < b):
        self._a = []
        self._less = less

    def size(self):
        return len(self._a)

    def peek(self): #  Вершина без удаления
        if not self._a:
            raise IndexError("peek from empty heap")
        return self._a[0]

    def push(self, x):
        self._a.append(x)
        self._sift_up(len(self._a) - 1)

    def pop(self): # Достать и вернуть вершину
        if not self._a:
            raise IndexError("pop from empty heap")
        top = self._a[0]
        last = self._a.pop()   
        if self._a:                  
            self._a[0] = last       
            self._sift_down(0)     
        return top

    def replace_top(self, x):
        if not self._a:
            raise IndexError("replace_top on empty heap")
        old = self._a[0]
        self._a[0] = x
        self._sift_down(0)
        return old

    @classmethod
    def heapify(cls, items, less=lambda a, b: a < b):
        h = cls(less)
        h._a = items
        for i in range(len(items) // 2 - 1, -1, -1):  # от последнего родителя к корню
            h._sift_down(i)
        return h

    def _sift_up(self, i):
        a = self._a
        while i > 0:
            p = (i - 1) // 2
            if self._less(a[i], a[p]):
                a[i], a[p] = a[p], a[i]
                i = p
            else:
                break

    def _sift_down(self, i):
        a = self._a
        n = len(a)
        while True:
            best = i
            l, r = 2 * i + 1, 2 * i + 2
            if l < n and self._less(a[l], a[best]):
                best = l
            if r < n and self._less(a[r], a[best]):
                best = r
            if best == i:
                break
            a[i], a[best] = a[best], a[i]
            i = best

    def is_valid(self):
        a = self._a
        return all(not self._less(a[i], a[(i - 1) // 2]) for i in range(1, len(a)))
