import sqlite3
from src.storage.queries import DOCUMENT_TABLE, DOCUMENT_INSERT

from src.storage.executor import create_table, batch_insert
from src.extraction.filesystem import lookup
from src.extraction.parser import parse_html, save_document

DOCPATH = "C:/Users/Vickynila/.rustup/toolchains/stable-x86_64-pc-windows-msvc/share/doc/rust/html"
DBPATH = "rust.db"

def init():
    with sqlite3.connect("rust.db") as conn:
        create_table(conn, DOCUMENT_TABLE)
    pass

def main():
    init()
    trait_iter = lookup(DOCPATH, "trait.*.html")
    for i in trait_iter:
        with open(i,encoding="utf-8") as f:
            html = parse_html(f, "main")
            save_document(html, "sample.json")
            
            with sqlite3.connect("rust.db") as conn:
                batch_insert(conn,DOCUMENT_INSERT,html)
            break
    pass

if __name__ == '__main__':
    main()