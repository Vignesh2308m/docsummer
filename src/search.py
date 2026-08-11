from dataclasses import dataclass

import numpy as np

from .storage import (
    SQLiteConnection,
    FAISSStore,
    RustDocument
)
from .queries import SEARCH_RUST_DOCUMENT

@dataclass
class SearchResult:
    id: list[int]
    distance: list[float]


def search_embedding(
    store: FAISSStore,
    embedding: np.ndarray,
    k: int = 5,
) -> list[SearchResult]:

    embedding = np.asarray(
        embedding,
        dtype=np.float32
    )

    if embedding.ndim == 1:
        embedding = embedding.reshape(1, -1)

    if embedding.shape[1] != store.config.dimension:
        raise ValueError(
            f"Expected embedding dimension "
            f"{store.config.dimension}, "
            f"got {embedding.shape[1]}"
        )

    if k <= 0:
        raise ValueError("k must be greater than 0")

    distances, ids = store.index.search(
        embedding,
        k
    )

    return SearchResult(
            id= [int(i) for i in ids],
            distance= [float(d) for d in distances]
        )

def search_document(
    conn: SQLiteConnection,
    result: SearchResult,
) -> list[RustDocument]:

    documents: list[RustDocument] = []

    for document_id in result.id[0]:
        row = conn.conn.execute(
            SEARCH_RUST_DOCUMENT,
            (document_id,)
        ).fetchone()

        if row is None:
            continue

        documents.append(
            RustDocument(
                id=row[0],
                library=row[1],
                item=row[2],
                kind=row[3],
                definition=row[4],
                description=row[5],
                example=row[6],
            )
        )

    return documents