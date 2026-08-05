# 🦀 Rust Doc Local RAG Engine

A high-performance, local Retrieval-Augmented Generation (RAG) backend engineered specifically for Rust documentation and code query understanding.

Powered by **Tree-sitter AST Chunking**, **SQLite FTS5 + FAISS Vector Hybrid Search**, **Cross-Encoder Context Reranking**, and **`Qwen2.5-Coder-1.5B`** via an **OpenAI-Compatible FastAPI Server**.

---

## 💡 Key Features

* **AST-Aware Rust Chunking:** Uses `tree-sitter-rust` to parse syntactic item boundaries (`Function`, `Struct`, `Impl Block`, `Trait`), keeping doc comments (`///`) attached to their code definitions without cutting syntax mid-block.
* **SQLite + FAISS Hybrid Store:**
  * **FAISS IndexIDMap:** Inner product vector search over normalized embeddings (`all-MiniLM-L6-v2`).
  * **SQLite FTS5:** Full-Text keyword search to guarantee exact symbol matching (e.g., `Point3D`, `dot_product`).
* **Cross-Encoder Reranking:** Re-scores retrieved candidates using `ms-marco-MiniLM-L-6-v2` to pass only top 2–3 hyper-relevant chunks to small LLMs like Qwen 2.5 1.5B.
* **OpenAI API Compatibility:** A lightweight FastAPI server exposes standard `/v1/chat/completions` endpoints with Server-Sent Events (SSE) streaming support, seamlessly bridging to local `llama-server` instances.