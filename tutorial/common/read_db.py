"""Read the catalog. These functions are not Chat Completions tools.

``query_catalog`` is the model-facing tool. It calls ``catalog_rows``.
The checker calls ``row_for``. The SQL stays in this file.
"""

from tutorial.common.get_db import connection


def _as_row(found):
    item = dict(found)
    item["shippable"] = bool(item["shippable"])
    cents = int(item["price_cents"])
    item["price"] = "$" + format(cents / 100, ".2f")
    return item


def row_for(sku):
    """One catalog row, or None when the sku is not in the catalog."""
    if not isinstance(sku, str) or not sku.strip():
        return None
    found = connection().execute(
        """
        SELECT sku, name, category, price_cents, stock, shippable
        FROM products
        WHERE sku = ?
        """,
        (sku.strip(),),
    ).fetchone()
    if found is None:
        return None
    return _as_row(found)


def catalog_rows(sku=None, name=None, category=None, only_in_stock=False):
    """Catalog rows for a filter. Callers pass filters, not a SQL statement."""
    sql = "SELECT sku, name, category, price_cents, stock, shippable FROM products"
    params = []
    where = []
    if isinstance(sku, str) and sku.strip():
        where.append("sku = ?")
        params.append(sku.strip())
    if isinstance(name, str) and name.strip():
        cleaned = name.strip().lower().replace("%", "").replace("_", "")
        where.append("lower(name) LIKE ?")
        params.append("%" + cleaned + "%")
    if isinstance(category, str) and category.strip():
        where.append("lower(category) = ?")
        params.append(category.strip().lower())
    if only_in_stock:
        where.append("stock > 0")
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY sku"
    rows = []
    for found in connection().execute(sql, params):
        rows.append(_as_row(found))
    return rows


__all__ = [
    "catalog_rows",
    "row_for",
]
