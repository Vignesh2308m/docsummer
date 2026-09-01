import sqlite3

from src.storage.executor import create_table, batch_insert
from src.extraction.filesystem import lookup
from src.extraction.parser import parse_html, save_document

DOCPATH = "C:/Users/Vickynila/.rustup/toolchains/stable-x86_64-pc-windows-msvc/share/doc/rust/html"
DBPATH = "rust.db"

def ingest():
    pass

def main():
    trait_iter = lookup(DOCPATH, "trait.*.html")
    for i in trait_iter:
        with open(i,encoding="utf-8") as f:
            html = parse_html(f)
            save_document(html, "sample.json")
            break
    pass

if __name__ == '__main__':
    main()