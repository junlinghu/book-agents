"""Create and open the tutorial shelf database.

The model never writes SQL. Reads live in ``tutorial.common.read_db``.
The inventory tool is registered from ``tutorial.common.shelf``.
"""

import sqlite3

# Shelf seed for this tutorial. The model never writes the SQL.
# sku, name, category, unit, reorder_point, on_hand, par.
SEED_ROWS = (
    ("HB-12", "House blend 12oz", "coffee", "bag", 6, 4, 18),
    ("HB-2LB", "House blend 2lb", "coffee", "bag", 4, 9, 10),
    ("ES-1KG", "Espresso beans 1kg", "coffee", "bag", 5, 5, 12),
    ("OM-32", "Oat milk 32oz", "dairy", "carton", 8, 3, 16),
    ("MLK-1", "Whole milk gallon", "dairy", "gallon", 4, 11, 12),
    ("ALM-1", "Almond meal", "bakery", "bag", 2, 1, 4),
    ("FL-01", "Paper filters", "supply", "box", 2, 7, 8),
)

STATE = {"conn": None}


def reset_db():
    """Drop the in-memory shelf and seed it again."""
    if STATE["conn"] is not None:
        STATE["conn"].close()
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.executescript(
        """
        CREATE TABLE products (
            sku TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            unit TEXT NOT NULL,
            reorder_point INTEGER NOT NULL
        );
        CREATE TABLE inventory (
            sku TEXT PRIMARY KEY,
            on_hand INTEGER NOT NULL,
            par INTEGER NOT NULL
        );
        """
    )
    for sku, name, category, unit, reorder_point, on_hand, par in SEED_ROWS:
        conn.execute(
            "INSERT INTO products (sku, name, category, unit, reorder_point) VALUES (?, ?, ?, ?, ?)",
            (sku, name, category, unit, reorder_point),
        )
        conn.execute(
            "INSERT INTO inventory (sku, on_hand, par) VALUES (?, ?, ?)",
            (sku, on_hand, par),
        )
    conn.commit()
    STATE["conn"] = conn
    return conn


def connection():
    """The in-memory shelf. The first call seeds it."""
    if STATE["conn"] is None:
        reset_db()
    return STATE["conn"]


__all__ = [
    "SEED_ROWS",
    "STATE",
    "connection",
    "reset_db",
]
