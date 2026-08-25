import numpy as np
from sentence_transformers import SentenceTransformer


def vectorize(
    model: SentenceTransformer,
    text: str | list[str],
) -> np.ndarray:
    return model.encode(
        text,
        convert_to_numpy=True,
        normalize_embeddings=True,
    ).astype(np.float32)