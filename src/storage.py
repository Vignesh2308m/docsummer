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
    id : str
    library: str
    item : str
    kind : str
    definition : str
    description : str
    example : list[str]

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
    document: RustDocument,
    commit:bool = True
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
            "".join(document.example),
        )
    )
    if commit:
        conn.conn.commit()

def init_faiss(
    config: FAISSIndexConfig,
    create_if_missing: bool = False
) -> FAISSStore:

    path = Path(config.path)

    if path.exists():
        index = faiss.read_index(str(path))

        # Restore search parameter
        if isinstance(index, faiss.IndexHNSW):
            index.hnsw.efSearch = config.ef_search

        return FAISSStore(
            index=index,
            config=config
        )

    if not create_if_missing:
        raise FileNotFoundError(
            f"FAISS index does not exist: {path}"
        )

    path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    index = faiss.IndexHNSWFlat(
        config.dimension,
        config.m
    )

    index.hnsw.efConstruction = config.ef_construction
    index.hnsw.efSearch = config.ef_search

    faiss.write_index(
        index,
        str(path)
    )

    return FAISSStore(
        index=index,
        config=config
    )

def add_vector(
    store: FAISSStore,
    vector: np.ndarray
) -> int:
    vector = np.asarray(vector, dtype=np.float32)

    if vector.ndim == 1:
        vector = vector.reshape(1, -1)

    if vector.shape[1] != store.config.dimension:
        raise ValueError(
            f"Expected dimension {store.config.dimension}, "
            f"got {vector.shape[1]}"
        )

    start_id = store.index.ntotal

    store.index.add(vector)

    faiss.write_index(
        store.index,
        store.config.path
    )

    return start_id