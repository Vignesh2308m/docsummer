from dataclasses import dataclass

import numpy as np
from sentence_transformers import SentenceTransformer

from .util import validate


@dataclass
class TextEmbedder:
    model: SentenceTransformer
    dimension: int
    model_name: str

    def __post_init__(self):
        validate(self)


def init_embedder(
    model_name: str = "all-MiniLM-L6-v2",
) -> TextEmbedder:

    model = SentenceTransformer(model_name)

    dimension = model.get_embedding_dimension()

    if dimension is None:
        raise ValueError(
            f"Unable to determine embedding dimension "
            f"for model: {model_name}"
        )

    return TextEmbedder(
        model=model,
        dimension=dimension,
        model_name=model_name,
    )


def embed_text(
    embedder: TextEmbedder,
    text: str,
) -> np.ndarray:

    embedding = embedder.model.encode(
        text,
        normalize_embeddings=True,
        show_progress_bar=False,
    )

    return np.asarray(
        embedding,
        dtype=np.float32,
    )


def embed_texts(
    embedder: TextEmbedder,
    texts: list[str],
) -> np.ndarray:

    embeddings = embedder.model.encode(
        texts,
        normalize_embeddings=True,
        show_progress_bar=False,
    )

    return np.asarray(
        embeddings,
        dtype=np.float32,
    )