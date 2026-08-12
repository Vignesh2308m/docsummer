from pathlib import Path
import json



from src.doc_parser import parse_html
from src.ingestion import read_html
from src.doc_builder import RustDocumentBuilder


PATH = "C:/Users/Vickynila/.rustup/toolchains/stable-x86_64-pc-windows-msvc/share/doc/rust/html/alloc/borrow/trait.BorrowMut.html"

def main():
    html = read_html(Path(PATH))
    doc = parse_html(html)
    builder = RustDocumentBuilder()
    rust_doc = builder.build(doc)
    print(rust_doc)
    pass


if __name__ == '__main__':
    main()