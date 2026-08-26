import sqlite3

from src.storage.executor import create_table
from src.storage.queries import TRAIT_TABLE, TRAIT_IMPLEMENTORS_TABLE, TRAIT_METHODS_TABLE


from src.templates.trait import TRAIT_TEMPLATE
from src.extraction.filesystem import lookup
from src.extraction.parser import extract_html
from src.storage.mapper import trait_to_dataclasses

DOCPATH = "C:/Users/Vickynila/.rustup/toolchains/stable-x86_64-pc-windows-msvc/share/doc/rust/html"
DBPATH = "rust.db"

def init():
    with sqlite3.connect(DBPATH) as conn:
        tbls = [
            TRAIT_TABLE,
            TRAIT_METHODS_TABLE,
            TRAIT_IMPLEMENTORS_TABLE
        ]
        for tbl in tbls:
            create_table(conn, tbl)

def ingest():
    pass

def main():
    init()
    trait_iter = lookup(DOCPATH, "trait.*.html")
    for i in trait_iter:
        with open(i,encoding="utf-8") as f:
            html = extract_html(f, TRAIT_TEMPLATE)
            trait, trait_method, trait_implementor = trait_to_dataclasses(html) 
            print(trait)
            print(trait_method)
            print(trait_implementor)
            break
    pass

if __name__ == '__main__':
    main()