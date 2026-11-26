import sys

from resource_hints.hinter import ResourceHinter
from resource_hints.loader import load_names

DEMO_QUERIES = [
    "texture_grass", # точное совпадение
    "texture_grasz", # z в конце
    "xexture_grass",  # х в начале
    "model_trxe",  # одна подсказка
    "model_xree", # две подсказки
    "textuer_grass",  # перестановка
    "sound_jum",  # другая длина
    "cmd_stxx",  # два несовпадения
]


def main():
    hinter = ResourceHinter(log=print)
    for name in load_names("data/resources.json"):
        hinter.add(name)
    print(f"Загружено имён: {len(hinter)}\n")

    for query in (sys.argv[1:] or DEMO_QUERIES):
        hinter.suggest(query)

    print()
    hinter.add("texture_gross")
    hinter.suggest("texture_gruss")


if __name__ == "__main__":
    main()
