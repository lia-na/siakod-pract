
class _Node:
    __slots__ = ("children", "is_end", "value")

    def __init__(self):
        self.children = {}
        self.is_end = False
        self.value = None


class CharTrie:
    def __init__(self):
        self._root = _Node()
        self._size = 0 # счетчик полей

    def __len__(self):
        return self._size

    def put(self, key, value=True):

        self._check_key(key)
        node = self._root
        for ch in key:
            node = node.children.setdefault(ch, _Node())
        is_new = not node.is_end
        node.is_end = True
        node.value = value
        if is_new:
            self._size += 1
        return is_new

    def get(self, key, default=None):
        node = self._find_node(key)
        if node is None or not node.is_end:
            return default
        return node.value

    def contains(self, key):
        node = self._find_node(key)
        return node is not None and node.is_end

    def find_one_mismatch(self, query):
        results = []
        if not query:
            return results

        def dfs(node, depth, mismatches, prefix):
            if mismatches >= 2:
                return
            if depth == len(query):
                if node.is_end and mismatches == 1:
                    results.append(prefix)
                return
            for ch in sorted(node.children):
                step = 0 if ch == query[depth] else 1
                dfs(node.children[ch], depth + 1, mismatches + step, prefix + ch)

        dfs(self._root, 0, 0, "")
        return results

    @staticmethod
    def _check_key(key):
        if not isinstance(key, str) or key == "":
            raise ValueError("ключ должен быть непустой строкой")

    def _find_node(self, key):
        if not isinstance(key, str):
            return None
        node = self._root
        for ch in key:
            node = node.children.get(ch)
            if node is None:
                return None
        return node
