"""Read the shelf. These functions are not Chat Completions tools.

``query_inventory`` is the model-facing tool. It calls ``inventory_rows``.
Checkers call ``row_for`` and ``gap_for``. The SQL stays in this file.
"""

from tutorial.common.get_db import connection


def gap_for(row):
    """Cartons or bags to buy to reach par. The supplier note does not get a vote."""
    return int(row["par"]) - int(row["on_hand"])


def row_for(sku):
    """One shelf row, or None when the sku is not on the shelf."""
    found = connection().execute(
        """
        SELECT p.sku, p.name, p.category, p.unit, p.reorder_point, i.on_hand, i.par
        FROM products p
        JOIN inventory i ON p.sku = i.sku
        WHERE p.sku = ?
        """,
        (sku,),
    ).fetchone()
    if found is None:
        return None
    item = dict(found)
    item["gap"] = gap_for(item)
    return item


def inventory_rows(only_low=False, sku=None):
    """Shelf rows for a filter. Callers pass filters, not a SQL statement."""
    sql = (
        "SELECT p.sku, p.name, p.category, p.unit, p.reorder_point, i.on_hand, i.par "
        "FROM products p JOIN inventory i ON p.sku = i.sku"
    )
    params = []
    where = []
    if isinstance(sku, str) and sku.strip():
        where.append("p.sku = ?")
        params.append(sku.strip())
    if only_low:
        where.append("i.on_hand <= p.reorder_point")
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY p.sku"
    rows = []
    for found in connection().execute(sql, params):
        item = dict(found)
        item["gap"] = gap_for(item)
        rows.append(item)
    return rows


__all__ = [
    "gap_for",
    "inventory_rows",
    "row_for",
]
