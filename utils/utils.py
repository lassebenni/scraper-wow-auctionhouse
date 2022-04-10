import pickle
from typing import Any


def store_as_pickle(object: Any, path: str):
    with open(path, "wb") as f:
        pickle.dump(object, f)


def write_json(input: str, path: str):
    with open(path, "w") as f:
        f.write(input)


def read_json(input: str, path: str):
    with open(path) as f:
        return f.read()


def load_pickle(path: str) -> Any:
    with open(path, "rb") as f:
        return pickle.load(f)
