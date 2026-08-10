import sqlite3
from dataclasses import dataclass
from pathlib import Path
import numpy as np
import faiss

from .util import validate

@dataclass
class SQLLiteConnection:
    conn: sqlite3.Connection
    db : Path

    def __post_init__(self):
        validate(self)

@dataclass
class RustDocument:
    id : int
    library: str
    item : str
    kind : str
    definition : str
    description : str
    example : str

    def __post_init__(self):
        validate(self)

@dataclass
class FAISSIndexConfig:
    dimension: int
    m: int
    ef_construction: int
    ef_search: int
    path: str

    def __post_init__(self):
        validate(self)


@dataclass
class FAISSStore:
    index: faiss.Index
    config: FAISSIndexConfig

    def __post_init__(self):
        validate(self)
