Python 3.11.5 (v3.11.5:cce6ba91b3, Aug 24 2023, 10:50:31) [Clang 13.0.0 (clang-1300.0.29.30)] on darwin
Type "help", "copyright", "credits" or "license()" for more information.
>>> from typing import List, Optional
... 
... 
... def naive_match(log1: List[float], log2: List[float]) -> List[Optional[float]]:
... 
...     n = len(log1)
...     m = len(log2)
...     if m == 0:
...         return [None] * n # если 2й журнал пуст, то для log1 - None
... 
...     result: List[Optional[float]] = [] # для ответов
... 
...     for t in log1:  # выполнится n раз (log1)
...         best_value = log2[0]
...         best_dist = abs(t - log2[0])
... 
...         # внутренний цикл:
...         for s in log2[1:]:  # до(m-1)раз внутри внешнего
...             d = abs(t - s)
...             if d <= best_dist: # более поздний, если равны
...                 best_dist = d
...                 best_value = s
... 
...         result.append(best_value)
... 
...     return result
