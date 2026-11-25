
import json


def load_names(path):
    with open(path, encoding="utf-8") as f:
        names = json.load(f)
    if not isinstance(names, list) or not all(isinstance(n, str) for n in names):
        raise ValueError("JSON-список строк")
    return names
