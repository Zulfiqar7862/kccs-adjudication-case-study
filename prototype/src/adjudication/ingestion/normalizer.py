"""Normalise comparison strings without changing original source values."""


def normalize(value):
    return " ".join(str(value if value is not None else "").casefold().split())
