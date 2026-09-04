import sqlite3
from typing import Optional


class GraphQuery:

    def __init__(self, db_path: str):
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row

    def get_node(self, node_id: int):
        return self.conn.execute(
            "SELECT * FROM document WHERE id = ?",
            (node_id,)
        ).fetchone()

    def children(self, node_id: int):
        return self.conn.execute(
            "SELECT * FROM document WHERE parent = ?",
            (node_id,)
        ).fetchall()

    def parent(self, node_id: int):
        return self.conn.execute(
            """
            SELECT d.*
            FROM document d
            JOIN document child ON child.parent = d.id
            WHERE child.id = ?
            """,
            (node_id,)
        ).fetchone()

    def neighbors(
        self,
        node_id: int,
        relation: Optional[str] = None
    ):
        query = """
            SELECT d.*
            FROM relations r
            JOIN document d ON d.id = r.target_id
            WHERE r.source_id = ?
        """

        params = [node_id]

        if relation:
            query += " AND r.relation = ?"
            params.append(relation)

        return self.conn.execute(query, params).fetchall()

    def incoming(
        self,
        node_id: int,
        relation: Optional[str] = None
    ):
        query = """
            SELECT d.*
            FROM relations r
            JOIN document d ON d.id = r.source_id
            WHERE r.target_id = ?
        """

        params = [node_id]

        if relation:
            query += " AND r.relation = ?"
            params.append(relation)

        return self.conn.execute(query, params).fetchall()

    def traverse(
        self,
        node_id: int,
        depth: int = 2
    ):
        return self.conn.execute(
            """
            WITH RECURSIVE graph AS (

                SELECT
                    source_id,
                    target_id,
                    relation,
                    1 AS depth
                FROM relations
                WHERE source_id = ?

                UNION ALL

                SELECT
                    r.source_id,
                    r.target_id,
                    r.relation,
                    g.depth + 1
                FROM relations r
                JOIN graph g ON r.source_id = g.target_id
                WHERE g.depth < ?
            )

            SELECT *
            FROM graph
            """,
            (node_id, depth)
        ).fetchall()

    def subgraph(
        self,
        node_id: int,
        depth: int = 2
    ):
        return self.conn.execute(
            """
            WITH RECURSIVE graph AS (

                SELECT
                    source_id,
                    target_id,
                    relation,
                    1 AS depth
                FROM relations
                WHERE source_id = ?

                UNION ALL

                SELECT
                    r.source_id,
                    r.target_id,
                    r.relation,
                    g.depth + 1
                FROM relations r
                JOIN graph g ON r.source_id = g.target_id
                WHERE g.depth < ?
            )

            SELECT
                g.source_id,
                g.target_id,
                g.relation,
                g.depth,
                source.content AS source_content,
                target.content AS target_content

            FROM graph g

            JOIN document source
                ON source.id = g.source_id

            JOIN document target
                ON target.id = g.target_id
            """,
            (node_id, depth)
        ).fetchall()

    def find_paths(
        self,
        source_id: int,
        target_id: int,
        max_depth: int = 5
    ):
        paths = []

        def dfs(current_id, path, visited, depth):

            if depth > max_depth:
                return

            if current_id == target_id:
                paths.append(path.copy())
                return

            rows = self.conn.execute(
                """
                SELECT
                    target_id,
                    relation
                FROM relations
                WHERE source_id = ?
                """,
                (current_id,)
            ).fetchall()

            for row in rows:
                next_id = row["target_id"]

                # Prevent cycles
                if next_id in visited:
                    continue

                visited.add(next_id)

                path.append({
                    "source": current_id,
                    "relation": row["relation"],
                    "target": next_id
                })

                dfs(
                    next_id,
                    path,
                    visited,
                    depth + 1
                )

                # Backtrack
                path.pop()
                visited.remove(next_id)

        dfs(
            source_id,
            [],
            {source_id},
            0
        )
        return paths

    def close(self):
        self.conn.close()
