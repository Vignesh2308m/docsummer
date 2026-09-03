
DOCUMENT_TABLE = '''
CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY,
    parent INTEGER NOT NULL DEFAULT 0,
    html_tag TEXT NOT NULL,
    html_id TEXT,
    html_class TEXT,
    href TEXT,
    content TEXT
);
'''


DOCUMENT_INSERT = """
        INSERT INTO documents (
            id, parent, html_tag,
            html_id, html_class,
            href, content
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
"""