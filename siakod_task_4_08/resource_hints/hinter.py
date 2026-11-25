from .char_trie import CharTrie


def _silent(message):
    pass


class ResourceHinter:
    def __init__(self, log=_silent):
        self._trie = CharTrie()
        self._log = log

    def __len__(self):
        return len(self._trie)

    def add(self, name, value=True):
        is_new = self._trie.put(name, value)
        action = "добавлено" if is_new else "заменено"
        self._log(f"[add] '{name}': {action}; размер словаря = {len(self._trie)}")
        return is_new

    def suggest(self, query):

        if self._trie.contains(query):
            self._log(f"[suggest] '{query}': точное совпадение")
            return [query]
        hints = self._trie.find_one_mismatch(query)
        if hints:
            self._log(f"[suggest] '{query}': имелось в виду {hints}")
        else:
            self._log(f"[suggest] '{query}': подсказок нет")
        return hints
