import sqlite3
from dataclasses import fields, is_dataclass
from typing import Iterable, TypeVar

T = TypeVar("T")

def create_table(
    conn: sqlite3.Connection,
    query: str,
) -> None:
    conn.execute(query)
    conn.commit()

def batch_insert(
    conn: sqlite3.Connection,
    query: str,
    items: Iterable[T],
    id: int = 0
) -> None:

    items = list(items)

    if not items:
        return

    if not is_dataclass(items[0]):
        raise TypeError("items must contain dataclass instances")

    field_names = [
        field.name
        for field in fields(items[0])
    ]

    values = (
        tuple(getattr(item, name) for name in field_names)
        for item in items
    )

    conn.executemany(query, values)

def insert(
    conn: sqlite3.Connection,
    query: str,
    item: T,
) -> int:
    if not is_dataclass(item):
        raise TypeError("item must be a dataclass instance")

    field_names = [
        field.name
        for field in fields(item)
        if field.name != "id"
    ]

    values = tuple(
        getattr(item, name)
        for name in field_names
    )

    cursor = conn.execute(query, values)

    return cursor.lastrowid