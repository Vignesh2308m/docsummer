
TRAIT_TABLE = """
    CREATE TABLE traits (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        type TEXT NOT NULL,
        declaration TEXT,
        description TEXT,
        source_href TEXT,
        source_line INTEGER
    );
"""

TRAIT_METHODS_TABLE = """
    CREATE TABLE trait_methods (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        trait_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        kind TEXT NOT NULL CHECK (kind IN ('required', 'provided')),
        href TEXT,
        signature TEXT,
        description TEXT,
        source_href TEXT,
        source_line INTEGER,

        FOREIGN KEY (trait_id)
            REFERENCES traits(id)
            ON DELETE CASCADE
    );
"""


TRAIT_IMPLEMENTORS_TABLE = """
    CREATE TABLE trait_implementors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        trait_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        href TEXT,
        source_href TEXT,
        source_line INTEGER,

        FOREIGN KEY (trait_id)
            REFERENCES traits(id)
            ON DELETE CASCADE
    );
"""


TRAIT_INSERT = """
    INSERT INTO traits (
        name,
        type,
        declaration,
        description,
        source_href,
        source_line
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
        source_href,
        source_line
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
"""


TRAIT_IMPLEMENTOR_INSERT = """
    INSERT INTO trait_implementors (
        trait_id,
        name,
        href,
        source_href,
        source_line
    )
    VALUES (?, ?, ?, ?, ?)
"""