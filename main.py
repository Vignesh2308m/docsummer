import sqlite3
from src.storage.queries import DOCUMENT_TABLE, DOCUMENT_INSERT

from src.storage.executor import create_table, batch_insert
from src.extraction.filesystem import lookup
from src.extraction.parser import parse_html, save_document

DOCPATH = "C:/Users/Vickynila/.rustup/toolchains/stable-x86_64-pc-windows-msvc/share/doc/rust/html/std"
DBPATH = "rust.db"

def init():
    with sqlite3.connect("rust.db") as conn:
        create_table(conn, DOCUMENT_TABLE)
    pass

def main():
    init()
    trait_iter = lookup(DOCPATH, "*.html")
    count = 0
    for i in trait_iter:
        print(str(count) + " " + str(i))
        with open(i,encoding="utf-8") as f:
            html = parse_html(f, str(i), count) 
            with sqlite3.connect("rust.db") as conn:
                batch_insert(conn,DOCUMENT_INSERT,html)
        count+=1
    pass

if __name__ == '__main__':
    main()