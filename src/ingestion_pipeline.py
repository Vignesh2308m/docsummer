import sqlite3
import os
import json
from typing import List, Dict, Any

import numpy as np
import faiss
from sentence_transformers import SentenceTransformer


class RustDocStorage:
    """
    SQLite + FAISS storage engine for Rust documentation.

    JSONL
       ↓
    SQLite
       +
    FAISS
    """

    def __init__(
        self,
        jsonl_path: str,
        db_path: str = "rust_docs.db",
        faiss_path: str = "rust_docs.index",
        model_name: str = "all-MiniLM-L6-v2",
        batch_size: int = 64,
    ):
        self.jsonl_path = jsonl_path
        self.db_path = db_path
        self.faiss_path = faiss_path
        self.batch_size = batch_size

        print(f"Loading embedding model: {model_name}")

        self.embedder = SentenceTransformer(model_name)
        self.dimension = self.embedder.get_embedding_dimension()

        # ---------------------------------------------------------
        # SQLite
        # ---------------------------------------------------------

        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()

        # Schema initialization is handled by the storage layer so
        # ingestion can reuse an existing database without creating
        # tables on its own.

        # ---------------------------------------------------------
        # FAISS
        # ---------------------------------------------------------

        self._init_faiss()

    # =============================================================
    # FAISS
    # =============================================================

    def _init_faiss(self):

        if os.path.exists(self.faiss_path):

            print(
                f"Loading FAISS index: "
                f"{self.faiss_path}"
            )

            self.index = faiss.read_index(
                self.faiss_path
            )

        else:

            print("Creating FAISS index")

            base_index = faiss.IndexFlatIP(
                self.dimension
            )

            self.index = faiss.IndexIDMap(
                base_index
            ) 

    # =============================================================
    # Embedding text
    # =============================================================

    def build_embedding_text(
        self,
        record: Dict[str, Any]
    ) -> str:

        library = record.get("library", "")
        item = record.get("item", "")
        kind = record.get("kind", "")
        definition = record.get("definition", "")
        description = record.get("description", "")

        examples = record.get("examples", [])

        if isinstance(examples, str):
            examples = [examples]

        example_text = "\n\n".join(
            examples
        )

        # This is the text that gets embedded.
        #
        # Including the symbol name + library + definition
        # is extremely important for API documentation.

        return f"""
Rust documentation

Library:
{library}

Item:
{item}

Kind:
{kind}

Definition:
{definition}

Description:
{description}

Examples:
{example_text}
""".strip()

    # =============================================================
    # Add documents
    # =============================================================

    def add_documents(
        self,
        records: List[Dict[str, Any]]
    ):

        if not records:
            return

        all_embeddings = []
        all_ids = []

        # ---------------------------------------------------------
        # Process in batches
        # ---------------------------------------------------------

        for batch_start in range(
            0,
            len(records),
            self.batch_size
        ):

            batch = records[
                batch_start:
                batch_start + self.batch_size
            ]

            print(
                f"Processing documents "
                f"{batch_start + 1}-"
                f"{batch_start + len(batch)} "
                f"of {len(records)}"
            )

            texts = []

            batch_ids = []

            # -----------------------------------------------------
            # SQLite
            # -----------------------------------------------------

            for record in batch:

                examples = record.get(
                    "examples",
                    []
                )

                if isinstance(examples, list):

                    examples_json = json.dumps(
                        examples,
                        ensure_ascii=False
                    )

                else:

                    examples_json = json.dumps(
                        [examples],
                        ensure_ascii=False
                    )

                self.cursor.execute(
                    """
                    INSERT INTO rust_doc_chunks (
                        file,
                        library,
                        item,
                        kind,
                        definition,
                        description,
                        examples,
                        source_path
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        record.get("file", ""),
                        record.get("library", ""),
                        record.get("item", ""),
                        record.get("kind", ""),
                        record.get("definition", ""),
                        record.get("description", ""),
                        examples_json,
                        record.get("path", "")
                    )
                )

                doc_id = self.cursor.lastrowid

                batch_ids.append(doc_id)

                # -------------------------------------------------
                # FTS
                # -------------------------------------------------

                self.cursor.execute(
                    """
                    INSERT INTO rust_doc_fts (
                        rowid,
                        library,
                        item,
                        kind,
                        definition,
                        description,
                        examples
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        doc_id,
                        record.get("library", ""),
                        record.get("item", ""),
                        record.get("kind", ""),
                        record.get("definition", ""),
                        record.get("description", ""),
                        examples_json
                    )
                )

                # -------------------------------------------------
                # Embedding text
                # -------------------------------------------------

                texts.append(
                    self.build_embedding_text(record)
                )

            self.conn.commit()

            # -----------------------------------------------------
            # Embeddings
            # -----------------------------------------------------

            embeddings = self.embedder.encode(
                texts,
                normalize_embeddings=True,
                show_progress_bar=True
            )

            embeddings = np.asarray(
                embeddings,
                dtype=np.float32
            )

            ids_np = np.asarray(
                batch_ids,
                dtype=np.int64
            )

            self.index.add_with_ids(
                embeddings,
                ids_np
            )

            all_embeddings.append(
                embeddings
            )

            all_ids.extend(batch_ids)

        # ---------------------------------------------------------
        # Persist FAISS
        # ---------------------------------------------------------

        faiss.write_index(
            self.index,
            self.faiss_path
        )

        print()
        print(
            f"Successfully indexed "
            f"{len(records)} documentation records"
        )

    # =============================================================
    # Vector search
    # =============================================================

    def search_vector(
        self,
        query: str,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:

        query_vector = self.embedder.encode(
            [query],
            normalize_embeddings=True
        )

        query_vector = np.asarray(
            query_vector,
            dtype=np.float32
        )

        distances, ids = self.index.search(
            query_vector,
            top_k
        )

        results = []

        for doc_id, score in zip(
            ids[0],
            distances[0]
        ):

            if doc_id == -1:
                continue

            self.cursor.execute(
                """
                SELECT
                    id,
                    file,
                    library,
                    item,
                    kind,
                    definition,
                    description,
                    examples,
                    source_path
                FROM rust_doc_chunks
                WHERE id = ?
                """,
                (int(doc_id),)
            )

            row = self.cursor.fetchone()

            if row is None:
                continue

            results.append({
                "id": row[0],
                "score": float(score),
                "file": row[1],
                "library": row[2],
                "item": row[3],
                "kind": row[4],
                "definition": row[5],
                "description": row[6],
                "examples": json.loads(row[7]),
                "source_path": row[8]
            })

        return results

    # =============================================================
    # Keyword search
    # =============================================================

    def search_keyword(
        self,
        query: str,
        limit: int = 10
    ):

        self.cursor.execute(
            """
            SELECT
                r.id,
                r.file,
                r.library,
                r.item,
                r.kind,
                r.definition,
                r.description,
                r.examples
            FROM rust_doc_fts f
            JOIN rust_doc_chunks r
                ON r.id = f.rowid
            WHERE rust_doc_fts MATCH ?
            LIMIT ?
            """,
            (query, limit)
        )

        rows = self.cursor.fetchall()

        results = []

        for row in rows:

            results.append({
                "id": row[0],
                "file": row[1],
                "library": row[2],
                "item": row[3],
                "kind": row[4],
                "definition": row[5],
                "description": row[6],
                "examples": json.loads(row[7])
            })

        return results

    # =============================================================
    # Close
    # =============================================================

    def close(self):
        self.conn.close()


# =================================================================
# Main ingestion
# =================================================================

if __name__ == "__main__":

    JSONL_FILE = "rust_std_docs.jsonl"

    storage = RustDocStorage(
        jsonl_path=JSONL_FILE,
        db_path="rust_docs.db",
        faiss_path="rust_docs.index",
        model_name="all-MiniLM-L6-v2"
    )

    # -------------------------------------------------------------
    # Load JSONL
    # -------------------------------------------------------------

    records = storage.load_jsonl()

    # -------------------------------------------------------------
    # Ingest
    # -------------------------------------------------------------

    storage.add_documents(records)

    # -------------------------------------------------------------
    # Test
    # -------------------------------------------------------------

    query = "How do I add an element to a Vec?"

    print()
    print("=" * 70)
    print(f"QUERY: {query}")
    print("=" * 70)

    results = storage.search_vector(
        query,
        top_k=5
    )

    for rank, result in enumerate(
        results,
        1
    ):

        print()
        print(
            f"--- Result #{rank} "
            f"(score={result['score']:.4f}) ---"
        )

        print(
            f"{result['library']}::"
            f"{result['item']}"
        )

        print(
            f"Kind: {result['kind']}"
        )

        print(
            f"Definition: "
            f"{result['definition']}"
        )

        print(
            f"Description: "
            f"{result['description'][:500]}"
        )

        if result["examples"]:

            print("Example:")

            for example in result["examples"][:2]:

                print("```rust")
                print(example)
                print("```")

    storage.close()