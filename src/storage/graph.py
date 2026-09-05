from dataclasses import dataclass


@dataclass
class Step:
    method: str
    params: dict


class GraphBuilder:

    def __init__(self):
        self.steps: list[Step] = []

    # Starting node
    def entity(self, key, value):
        return self._add("entity", key=key, value=value)

    # Graph traversal
    def out(self, relation):
        return self._add("out", relation=relation)

    def in_(self, relation):
        return self._add("in", relation=relation)

    def both(self, relation):
        return self._add("both", relation=relation)

    # HTML hierarchy
    def parent(self):
        return self._add("parent")

    def children(self):
        return self._add("children")

    def ancestors(self, depth=None):
        return self._add("ancestors", depth=depth)

    def descendants(self, depth=None):
        return self._add("descendants", depth=depth)

    def siblings(self):
        return self._add("siblings")

    # Filtering
    def where(self, key, value):
        return self._add("where", key=key, value=value)

    def contains(self, key, value):
        return self._add("contains", key=key, value=value)

    # Results
    def all(self):
        return self._add("all")

    def first(self):
        return self._add("first")

    def count(self):
        return self._add("count")

    def exists(self):
        return self._add("exists")

    # Add query step
    def _add(self, method, **params):
        self.steps.append(
            Step(
                method=method,
                params=params
            )
        )
        return self

# Node
def entity(table, key, value):
    return f"""
    SELECT *
    FROM {table}
    WHERE {key} LIKE '%{value}%'
    """


# Graph relations
def out(table, relation_table, node_id, relation):
    return f"""
    SELECT target.*
    FROM {relation_table} r
    JOIN {table} target
        ON r.target_id = target.id
    WHERE r.source_id = {node_id}
      AND r.relation = '{relation}'
    """


def in_(table, relation_table, node_id, relation):
    return f"""
    SELECT source.*
    FROM {relation_table} r
    JOIN {table} source
        ON r.source_id = source.id
    WHERE r.target_id = {node_id}
      AND r.relation = '{relation}'
    """


def both(table, relation_table, node_id, relation):
    return f"""
    SELECT target.*
    FROM {relation_table} r
    JOIN {table} target
        ON r.target_id = target.id
    WHERE r.source_id = {node_id}
      AND r.relation = '{relation}'

    UNION

    SELECT source.*
    FROM {relation_table} r
    JOIN {table} source
        ON r.source_id = source.id
    WHERE r.target_id = {node_id}
      AND r.relation = '{relation}'
    """


# HTML hierarchy
def parent(table, node_id):
    return f"""
    SELECT parent.*
    FROM {table} child
    JOIN {table} parent
        ON child.parent = parent.id
    WHERE child.id = {node_id}
    """


def children(table, node_id):
    return f"""
    SELECT *
    FROM {table}
    WHERE parent = {node_id}
    """


def ancestors(table, node_id, depth=None):
    depth_condition = "AND depth <= 1"

    if depth is not None:
        depth_condition = f"AND depth <= {depth}"

    return f"""
    WITH RECURSIVE tree AS (
        SELECT *, 0 AS depth
        FROM {table}
        WHERE id = {node_id}

        UNION ALL

        SELECT parent.*, tree.depth + 1
        FROM {table} parent
        JOIN tree
            ON tree.parent = parent.id
    )
    SELECT *
    FROM tree
    WHERE depth > 0
    {depth_condition}
    """


def descendants(table, node_id, depth=None):
    depth_condition = "AND depth <= 1"

    if depth is not None:
        depth_condition = f"AND depth <= {depth}"

    return f"""
    WITH RECURSIVE tree AS (
        SELECT *, 0 AS depth
        FROM {table}
        WHERE id = {node_id}

        UNION ALL

        SELECT child.*, tree.depth + 1
        FROM {table} child
        JOIN tree
            ON child.parent = tree.id
    )
    SELECT *
    FROM tree
    WHERE depth > 0
    {depth_condition}
    """


def siblings(table, node_id):
    return f"""
    SELECT sibling.*
    FROM {table} sibling
    JOIN {table} node
        ON sibling.parent = node.parent
    WHERE node.id = {node_id}
      AND sibling.id != node.id
    """


# Filtering
def where(table, key, value):
    return f"""
    SELECT *
    FROM {table}
    WHERE {key} LIKE '%{value}%'
    """


def contains(table, key, value):
    return f"""
    SELECT *
    FROM {table}
    WHERE {key} LIKE '%{value}%'
    """


# Results
def all(table):
    return f"""
    SELECT *
    FROM {table}
    """


def first(table):
    return f"""
    SELECT * FROM
    {table}
    LIMIT 1
    """


def count(table):
    return f"""
    SELECT COUNT(*)
    FROM {table}
    """

def build_graph(steps, table="documents", relation_table="relations"):
    ctes = []
    current = None

    for i, step in enumerate(steps):
        name = f"cte_{i}"
        method = step.method
        params = step.params

        if method == "entity":
            query = entity(
                table,
                params["key"],
                params["value"]
            )

        elif method == "out":
            query = out(
                f"cte_{i-1}",
                relation_table,
                params["relation"]
            )

        elif method == "in":
            query = in_(
                f"cte_{i-1}",
                relation_table,
                params["relation"]
            )

        elif method == "both":
            query = both(
                f"cte_{i-1}",
                relation_table,
                params["relation"]
            )

        elif method == "parent":
            query = parent(
                f"cte_{i-1}"
            )

        elif method == "children":
            query = children(
                f"cte_{i-1}"
            )

        elif method == "ancestors":
            query = ancestors(
                f"cte_{i-1}",
                params["depth"]
            )

        elif method == "descendants":
            query = descendants(
                f"cte_{i-1}",
                params["depth"]
            )

        elif method == "siblings":
            query = siblings(
                f"cte_{i-1}"
            )

        elif method == "where":
            query = where(
                f"cte_{i-1}",
                params["key"],
                params["value"]
            )

        elif method == "contains":
            query = contains(
                f"cte_{i-1}",
                params["key"],
                params["value"]
            )

        elif method == "all":
            query = all(f"cte_{i-1}")
            current = f"cte_{i-1}"
            break

        elif method == "first":
            query = first(f"cte_{i-1}")
            current = f"cte_{i-1}"
            break

        elif method == "count":
            query = count(f"cte_{i-1}")
            current = f"cte_{i-1}"
            break

        else:
            raise ValueError(f"Unknown method: {method}")

        ctes.append(f"{name} AS ({query})")
        current = name

    if not ctes:
        raise ValueError("No graph steps")

    if steps[-1].method in {"all", "first", "count", "exists"}:
        final = query
    else:
        final = f"SELECT * FROM {current}"

    return "WITH RECURSIVE\n" + ",\n".join(ctes) + "\n" + final