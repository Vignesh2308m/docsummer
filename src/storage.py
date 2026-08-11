import sqlite3
from dataclasses import dataclass
from pathlib import Path
import numpy as np
import faiss


from .util import validate
from .queries import CREATE_DOCUMENTS_TABLE, INSERT_RUST_DOCUMENTS

@dataclass
class SQLiteConnection:
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



def init_database(
    db: Path,
    create_if_missing: bool = False
) -> SQLiteConnection:

    # Database does not exist
    if not db.exists():

        if not create_if_missing:
            raise FileNotFoundError(
                f"Database does not exist: {db}"
            )

        # Create parent directory if necessary
        db.parent.mkdir(
            parents=True,
            exist_ok=True
        )

    conn = sqlite3.connect(db)

    # Create tables only when creating a new database
    if create_if_missing:
        conn.execute(CREATE_DOCUMENTS_TABLE)

        conn.commit()

    return SQLiteConnection(
        conn=conn,
        db=db
    )


def insert_document(
    conn: SQLiteConnection,
    document: RustDocument
) -> None:
    conn.conn.execute(
        INSERT_RUST_DOCUMENTS, 
        (
            document.id,
            document.library,
            document.item,
            document.kind,
            document.definition,
            document.description,
            document.example,
        )
    )

    conn.conn.commit()