from src.doc_parser import extract_page
from ingestion_pipeline import RustDocStorage
from storage_pipeline import RAGStorage
from ast_parser import RustASTChunk, RustASTChunker
from pathlib import Path




def main():
    doc_str = extract_page(Path("C://Users//Vickynila//.rustup//toolchains//stable-x86_64-pc-windows-msvc//share//doc//rust//html//alloc//borrow//trait.BorrowMut.html"))
    print(doc_str)


if __name__ == '__main__':
    main()