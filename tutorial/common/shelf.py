"""The shelf tool the model may call.

The database is created in ``tutorial.common.get_db`` and read in
``tutorial.common.read_db``. Importing this module registers
``query_inventory``. Shop rules stay on ``get_shop_fact``.
"""

import json

from tutorial.common.read_db import inventory_rows
from tutorial.common.tools import register


def query_inventory(args):
    """Read the shelf. The SQL stays in read_db. The model passes filters, not a statement."""
    only_low = bool(args.get("only_low", False))
    sku = args.get("sku")
    rows = inventory_rows(only_low=only_low, sku=sku)
    payload = {"rows": rows}
    if isinstance(sku, str) and sku.strip() and not rows:
        payload["error"] = "unknown sku " + sku.strip()
    return json.dumps(payload)


register(
    "query_inventory",
    "Read the café shelf from SQLite. Low stock means on_hand <= reorder_point. "
    "Each row includes gap, which is par minus on_hand. This tool does not write.",
    {
        "only_low": {"type": "boolean", "description": "True to keep only low or at-reorder rows."},
        "sku": {"type": "string", "description": "Optional sku, such as OM-32."},
    },
    [],
    query_inventory,
)

__all__ = [
    "query_inventory",
]
