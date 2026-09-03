
DOCUMENT_TABLE = '''
CREATE TABLE IF NOT EXISTS documents (
    path TEXT,
    page_id INTEGER,
    id INTEGER,
    parent INTEGER NOT NULL DEFAULT 0,
    html_tag TEXT NOT NULL,
    html_id TEXT,
    html_class TEXT,
    href TEXT,
    content TEXT
);
'''
RELATION_TABLE = '''
CREATE TABLE IF NOT EXISTS relations (
    path TEXT,
    page_id INTEGER,
    source_id INTEGER,
    target_id INTEGER,
    relation TEXT
);
'''

DOCUMENT_INSERT = """
        INSERT INTO documents (
            path, page_id,
            id, parent, html_tag,
            html_id, html_class,
            href, content
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
"""

RELATION_INSERT = """
        INSERT INTO documents (
            path, page_id,
            source_id, target_id,
            relation
        )
        VALUES (?, ?, ?, ?, ?)
"""