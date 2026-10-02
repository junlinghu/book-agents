"""Create and open the Harbor Jar catalog.

The model never writes SQL. Reads live in ``tutorial.common.read_db``.
The catalog tool is registered from ``tutorial.common.catalog``.
"""

import sqlite3

# sku, name, category, price_cents, stock, shippable (1 or 0).
# Practice rows for a fictional shop. The model never writes the SQL.
SEED_ROWS = (
    ("HJ-CHI", "Calabrian chili oil", "oils", 1800, 14, 1),
    ("HJ-OLV", "Ligurian olive oil", "oils", 2400, 8, 1),
    ("HJ-FIG", "Fig and thyme jam", "preserves", 1200, 6, 1),
    ("HJ-APR", "Apricot preserve", "preserves", 1100, 11, 1),
    ("HJ-HAR", "Harissa spice blend", "spices", 900, 2, 1),
    ("HJ-SES", "Sesame crunch", "spices", 800, 9, 1),
    ("HJ-BOX", "Harbor gift box", "gifts", 4800, 5, 1),
    ("HJ-LAB", "Fresh labneh", "fresh", 1600, 4, 0),
)

STATE = {"conn": None}


def reset_db():
    """Drop the in-memory catalog and seed it again."""
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
            price_cents INTEGER NOT NULL,
            stock INTEGER NOT NULL,
            shippable INTEGER NOT NULL
        );
        """
    )
    for sku, name, category, price_cents, stock, shippable in SEED_ROWS:
        conn.execute(
            "INSERT INTO products (sku, name, category, price_cents, stock, shippable) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (sku, name, category, price_cents, stock, shippable),
        )
    conn.commit()
    STATE["conn"] = conn
    return conn


def connection():
    """The in-memory catalog. The first call seeds it."""
    if STATE["conn"] is None:
        reset_db()
    return STATE["conn"]


__all__ = [
    "SEED_ROWS",
    "STATE",
    "connection",
    "reset_db",
]
