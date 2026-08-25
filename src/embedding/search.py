import faiss
import numpy as np


def search(
    index: faiss.Index,
    embedding: np.ndarray,
    k: int = 5,
) -> tuple[np.ndarray, np.ndarray]:

    embedding = np.asarray(embedding, dtype=np.float32)

    if embedding.ndim == 1:
        embedding = embedding.reshape(1, -1)

    scores, ids = index.search(embedding, k)

    return scores[0], ids[0]