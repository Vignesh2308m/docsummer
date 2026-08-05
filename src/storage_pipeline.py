import sqlite3
import os
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any, Optional


# =====================================================================
# 2. SQLite + FAISS Unified Storage Engine
# =====================================================================
class RAGStorage:
    """Combines SQLite (with FTS5) for full code payload and FAISS for vector search."""

    def __init__(
        self,
        db_path: str = "rust_docs.db",
        faiss_path: str = "rust_docs.index",
        model_name: str = "all-MiniLM-L6-v2"
    ):
        self.db_path = db_path
        self.faiss_path = faiss_path
        
        # 1. Load Embedding Model
        print(f"Loading embedder '{model_name}'...")
        self.embedder = SentenceTransformer(model_name)
        self.dimension = self.embedder.get_sentence_embedding_dimension()

        # 2. Setup SQLite Database with FTS5 Table
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self._init_sqlite()

        # 3. Setup FAISS Index
        self._init_faiss()

    def _init_sqlite(self):
        """Creates main document store table and FTS5 full-text index."""
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS rust_chunks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol_name TEXT NOT NULL,
            symbol_type TEXT NOT NULL,
            file_path TEXT NOT NULL,
            code TEXT NOT NULL,
            start_line INTEGER,
            end_line INTEGER
        )
        """)

        # Virtual table for keyword/symbol fast lookup
        self.cursor.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS rust_chunks_fts USING fts5(
            symbol_name, symbol_type, code, content='rust_chunks', content_rowid='id'
        )
        """)
        self.conn.commit()

    def _init_faiss(self):
        """Loads FAISS index from disk if present, otherwise creates a new IndexIDMap."""
        if os.path.exists(self.faiss_path):
            print(f"Loading existing FAISS index from {self.faiss_path}...")
            self.index = faiss.read_index(self.faiss_path)
        else:
            print("Creating new FAISS IndexIDMap...")
            # Inner Product index used for Cosine Similarity (vectors normalized)
            base_index = faiss.IndexFlatIP(self.dimension)
            self.index = faiss.IndexIDMap(base_index)

    def add_chunks(self, chunks: List[Dict[str, Any]]):
        """Inserts AST chunks into SQLite and populates FAISS vector index."""
        if not chunks:
            return

        texts_to_embed = []
        doc_ids = []

        for chunk in chunks:
            # Insert record into SQLite main table
            self.cursor.execute(
                """
                INSERT INTO rust_chunks (symbol_name, symbol_type, file_path, code, start_line, end_line)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    chunk["symbol_name"],
                    chunk["symbol_type"],
                    chunk["file_path"],
                    chunk["code"],
                    chunk["start_line"],
                    chunk["end_line"]
                )
            )
            doc_id = self.cursor.lastrowid

            # Sync SQLite FTS5 index
            self.cursor.execute(
                "INSERT INTO rust_chunks_fts(rowid, symbol_name, symbol_type, code) VALUES (?, ?, ?, ?)",
                (doc_id, chunk["symbol_name"], chunk["symbol_type"], chunk["code"])
            )

            doc_ids.append(doc_id)
            # Create enriched context string for embeddings
            embed_text = f"// [{chunk['symbol_type']}] {chunk['symbol_name']}\n{chunk['code']}"
            texts_to_embed.append(embed_text)

        self.conn.commit()

        # Generate normalized embeddings
        print(f"Embedding {len(texts_to_embed)} chunks for FAISS...")
        embeddings = self.embedder.encode(
            texts_to_embed, 
            normalize_embeddings=True
        ).astype(np.float32)

        # Add to FAISS IndexIDMap with matching SQLite IDs
        ids_np = np.array(doc_ids, dtype=np.int64)
        self.index.add_with_ids(embeddings, ids_np)

        # Persist FAISS index to disk
        faiss.write_index(self.index, self.faiss_path)
        print(f"Successfully stored {len(chunks)} chunks in SQLite and FAISS.")

    def search_vector(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Queries FAISS vector index and fetches matching chunk data from SQLite."""
        query_vector = self.embedder.encode([query], normalize_embeddings=True).astype(np.float32)
        distances, doc_ids = self.index.search(query_vector, top_k)

        retrieved_ids = doc_ids[0].tolist()
        scores = distances[0].tolist()

        # Filter out invalid match IDs (-1)
        valid_matches = [(id_, score) for id_, score in zip(retrieved_ids, scores) if id_ != -1]
        if not valid_matches:
            return []

        target_ids = [m[0] for m in valid_matches]
        placeholders = ",".join("?" * len(target_ids))

        self.cursor.execute(
            f"SELECT id, symbol_name, symbol_type, file_path, code, start_line, end_line FROM rust_chunks WHERE id IN ({placeholders})",
            target_ids
        )
        rows = {row[0]: row for row in self.cursor.fetchall()}

        results = []
        for doc_id, score in valid_matches:
            if doc_id in rows:
                r = rows[doc_id]
                results.append({
                    "id": r[0],
                    "score": float(score),
                    "symbol_name": r[1],
                    "symbol_type": r[2],
                    "file_path": r[3],
                    "code": r[4],
                    "start_line": r[5],
                    "end_line": r[6],
                })
        return results

    def close(self):
        self.conn.close()


# =====================================================================
# 3. Demonstration & Quick Test
# =====================================================================
if __name__ == "__main__":
    # Remove old databases if re-running test
    for path in ["rust_docs.db", "rust_docs.index"]:
        if os.path.exists(path):
            os.remove(path)

    sample_rust_code = '''
    /// Calculates the dot product of two vectors
    pub fn dot_product(a: &[f32], b: &[f32]) -> f32 {
        a.iter().zip(b).map(|(x, y)| x * y).sum()
    }

    /// Representation of a 3D Point
    pub struct Point3D {
        pub x: f32,
        pub y: f32,
        pub z: f32,
    }

    impl Point3D {
        pub fn new(x: f32, y: f32, z: f32) -> Self {
            Self { x, y, z }
        }
    }
    '''

    # Step 1: Chunk using Tree-Sitter
    chunker = RustASTChunker()
    chunks = chunker.chunk_code(sample_rust_code, file_path="src/vector_math.rs")

    # Step 2: Store in SQLite + FAISS
    storage = RAGStorage()
    storage.add_chunks(chunks)

    # Step 3: Run Retrieval Test
    query = "How do I calculate vector dot product?"
    print(f"\n🔍 Searching for: '{query}'")
    hits = storage.search_vector(query, top_k=2)

    for rank, hit in enumerate(hits, 1):
        print(f"\n--- Result #{rank} (Similarity Score: {hit['score']:.4f}) ---")
        print(f"[{hit['symbol_type']}] {hit['symbol_name']} ({hit['file_path']}:{hit['start_line']}-{hit['end_line']})")
        print("```rust")
        print(hit['code'])
        print("```")

    storage.close()