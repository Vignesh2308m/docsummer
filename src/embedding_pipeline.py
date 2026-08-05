import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any


class TextEmbedder:
    """Wrapper around SentenceTransformer for generating and searching embeddings."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initializes the embedding model.
        - 'all-MiniLM-L6-v2' is fast, lightweight (384-dim), and great for RAG pipelines.
        """
        print(f"Loading SentenceTransformer model: '{model_name}'...")
        self.model = SentenceTransformer(model_name)

    def embed_texts(self, texts: List[str]) -> np.ndarray:
        """Generates normalized vector embeddings for a list of text strings."""
        # normalize_embeddings=True allows us to compute Cosine Similarity using simple Dot Product
        embeddings = self.model.encode(
            texts, 
            show_progress_bar=False, 
            normalize_embeddings=True
        )
        return np.array(embeddings, dtype=np.float32)

    def search(
        self, 
        query: str, 
        corpus: List[str], 
        corpus_embeddings: np.ndarray, 
        top_k: int = 2
    ) -> List[Dict[str, Any]]:
        """Searches the corpus for texts most semantically similar to the query."""
        # Embed query and normalize
        query_embedding = self.model.encode(
            query, 
            normalize_embeddings=True
        ).astype(np.float32)

        # Compute cosine similarity via dot product (since vectors are normalized)
        similarities = np.dot(corpus_embeddings, query_embedding)

        # Get top-k indices sorted by highest similarity score
        top_indices = np.argsort(similarities)[::-1][:top_k]

        results = []
        for idx in top_indices:
            results.append({
                "index": int(idx),
                "score": float(similarities[idx]),
                "text": corpus[idx]
            })

        return results


# =====================================================================
# QUICK TEST / VERIFICATION
# =====================================================================
if __name__ == "__main__":
    print("\n--- Running Sentence Transformer Quick Test ---")

    # 1. Sample Rust Documentation / Code Chunks
    documents = [
        "/// Calculates the dot product of two slice vectors\npub fn dot_product(a: &[f32], b: &[f32]) -> f32",
        "/// Representation of a 3D Point in spatial coordinate space\npub struct Point3D { pub x: f32, pub y: f32, pub z: f32 }",
        "/// Asynchronously spawns a tokio task onto the runtime driver\npub fn spawn<F>(future: F) -> JoinHandle<F::Output>",
        "/// A thread-safe reference-counting pointer (Arc)\npub struct Arc<T: ?Sized> { ptr: NonNull<ArcInner<T>> }",
    ]

    # 2. Initialize Embedder
    embedder = TextEmbedder(model_name="all-MiniLM-L6-v2")

    # 3. Embed Corpus
    print(f"Embedding {len(documents)} document chunks...")
    document_embeddings = embedder.embed_texts(documents)
    print(f"Embedding shape: {document_embeddings.shape} (Count, Dimensions)")

    # 4. Test Queries
    test_queries = [
        "How do I multiply two vectors together?",
        "How do I run background async tasks in threads?",
        "What data structure represents x, y, z coordinates?"
    ]

    # 5. Run Search Tests
    for query in test_queries:
        print(f"\n🔍 Query: '{query}'")
        matches = embedder.search(
            query=query, 
            corpus=documents, 
            corpus_embeddings=document_embeddings, 
            top_k=1
        )
        
        top_match = matches[0]
        print(f"   -> Top Match (Score: {top_match['score']:.4f}):")
        print(f"      {top_match['text'].replace(chr(10), ' ')}")

    print("\n✅ Quick Test Completed Successfully!")