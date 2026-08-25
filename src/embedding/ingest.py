import faiss
import numpy as np


def ingest(
    index: faiss.Index,
    embeddings: np.ndarray,
    path: str,
) -> faiss.Index:

    embeddings = np.asarray(embeddings, dtype=np.float32)

    index.add(embeddings)
    faiss.write_index(index, path)

    return index