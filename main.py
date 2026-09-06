import sqlite3
from src.storage.queries import DOCUMENT_TABLE, DOCUMENT_INSERT, RELATION_TABLE, RELATION_INSERT
from src.relation.html import TAG_ROLES, CLASS_ROLES, ID_RELATIONS

from src.storage.executor import create_table, batch_insert
from src.extraction.filesystem import lookup
from src.extraction.parser import parse_html, save_document, parse_relation

DOCPATH = "C:/Users/Vickynila/.rustup/toolchains/stable-x86_64-pc-windows-msvc/share/doc/rust/html/std"
DBPATH = "rust.db"

def init():
    with sqlite3.connect("rust.db") as conn:
        create_table(conn, DOCUMENT_TABLE)
        create_table(conn, RELATION_TABLE)
    pass

def main():
    init()
    trait_iter = lookup(DOCPATH, "*.html")
    count = 0
    for i in trait_iter:
        print(str(count) + " " + str(i))
        with open(i,encoding="utf-8") as f:
            html = parse_html(f, str(i), count) 
            tag = parse_relation(html, TAG_ROLES, "html_tag")
            class_role = parse_relation(html, CLASS_ROLES, "html_class")
            id = parse_relation(html, ID_RELATIONS, "html_id")
            with sqlite3.connect("rust.db") as conn:
                batch_insert(conn,DOCUMENT_INSERT,html)
                batch_insert(conn,RELATION_INSERT,tag)
                batch_insert(conn,RELATION_INSERT,class_role)
                batch_insert(conn,RELATION_INSERT,id)
        count+=1
    pass

if __name__ == '__main__':
    main()