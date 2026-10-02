"""The catalog tool the model may call.

The database is created in ``tutorial.common.get_db`` and read in
``tutorial.common.read_db``. Importing this module registers
``query_catalog``. Store rules stay on ``get_store_fact``.
"""

import json

from tutorial.common.read_db import catalog_rows
from tutorial.common.tools import register


def query_catalog(args):
    """Read the catalog. The SQL stays in read_db. The model passes filters, not a statement."""
    sku = args.get("sku")
    name = args.get("name")
    category = args.get("category")
    only_in_stock = bool(args.get("only_in_stock", False))
    rows = catalog_rows(
        sku=sku,
        name=name,
        category=category,
        only_in_stock=only_in_stock,
    )
    payload = {"rows": rows}
    if isinstance(sku, str) and sku.strip() and not rows:
        payload["error"] = "unknown sku " + sku.strip()
    elif isinstance(name, str) and name.strip() and not rows:
        payload["error"] = "no catalog row matches " + name.strip()
    return json.dumps(payload)


register(
    "query_catalog",
    "Read the Harbor Jar catalog from SQLite. "
    "Each row has sku, name, category, price, price_cents, stock, and shippable. "
    "Pass a name, sku, or category. Do not pass SQL. This tool does not write.",
    {
        "sku": {"type": "string", "description": "Optional sku, such as HJ-CHI."},
        "name": {"type": "string", "description": "Optional product name, such as Calabrian chili oil."},
        "category": {"type": "string", "description": "Optional category: oils, preserves, spices, gifts, or fresh."},
        "only_in_stock": {"type": "boolean", "description": "True to skip rows with stock 0."},
    },
    [],
    query_catalog,
)

__all__ = [
    "query_catalog",
]
