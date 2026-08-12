

CREATE_DOCUMENTS_TABLE = """
            CREATE TABLE IF NOT EXISTS rust_documents (
                id TEXT PRIMARY KEY,
                library TEXT NOT NULL,
                item TEXT NOT NULL,
                kind TEXT NOT NULL,
                definition TEXT,
                description TEXT,
                example TEXT
            )
"""


INSERT_RUST_DOCUMENTS = """
        INSERT INTO rust_documents (
            id,
            library,
            item,
            kind,
            definition,
            description,
            example
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """

SEARCH_RUST_DOCUMENT="""
            SELECT
                id,
                library,
                item,
                kind,
                definition,
                description,
                example
            FROM documents
            WHERE id = ?
            """