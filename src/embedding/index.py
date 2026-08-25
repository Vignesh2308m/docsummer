import faiss


def create_faiss_index(dimension: int, path: str) -> faiss.Index:
    index = faiss.IndexFlatIP(dimension)
    faiss.write_index(index, path)
    return index


def load_faiss_index(path: str) -> faiss.Index:
    return faiss.read_index(path)


