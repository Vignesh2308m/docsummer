
TRAIT_TABLE = """
    CREATE TABLE IF NOT EXISTS traits (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        type TEXT NOT NULL,
        declaration TEXT,
        description TEXT,
        source_text TEXT,
        source_href TEXT
    );
"""

TRAIT_METHODS_TABLE = """
    CREATE TABLE IF NOT EXISTS trait_methods (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        trait_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        kind TEXT NOT NULL CHECK (kind IN ('required', 'provided')),
        href TEXT,
        signature TEXT,
        description TEXT,
        source_text TEXT,
        source_href TEXT,

        FOREIGN KEY (trait_id)
            REFERENCES traits(id)
            ON DELETE CASCADE
    );
"""


TRAIT_IMPLEMENTORS_TABLE = """
    CREATE TABLE IF NOT EXISTS trait_implementors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        trait_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        href TEXT,
        source_text TEXT,
        source_href TEXT,

        FOREIGN KEY (trait_id)
            REFERENCES traits(id)
            ON DELETE CASCADE
    );
"""


TRAIT_INSERT = """
    INSERT INTO traits (
        title,
        type,
        declaration,
        description,
        source_text,
        source_href
    )
    VALUES (?, ?, ?, ?, ?, ?)
"""


TRAIT_METHOD_INSERT = """
    INSERT INTO trait_methods (
        trait_id,
        name,
        kind,
        href,
        signature,
        description,
        source_text,
        source_href
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
"""


TRAIT_IMPLEMENTOR_INSERT = """
    INSERT INTO trait_implementors (
        trait_id,
        name,
        href,
        source_text,
        source_href
    )
    VALUES (?, ?, ?, ?, ?)
"""