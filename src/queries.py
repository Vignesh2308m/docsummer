

CREATE_DOCUMENTS_TABLE = """
            CREATE TABLE IF NOT EXISTS rust_documents (
                id INTEGER PRIMARY KEY,
                library TEXT NOT NULL,
                item TEXT NOT NULL,
                kind TEXT NOT NULL,
                definition TEXT,
                description TEXT,
                example TEXT
            )
"""