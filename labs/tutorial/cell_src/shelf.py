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


def gap_for(row):
    """Cartons or bags to buy to reach par. The supplier note does not get a vote."""
    return int(row["par"]) - int(row["on_hand"])


def reset_db():
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


def row_for(sku):
    if STATE["conn"] is None:
        reset_db()
    found = STATE["conn"].execute(
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


def query_inventory(args):
    """Read the shelf. The SQL stays in this function. The model passes filters, not a statement."""
    if STATE["conn"] is None:
        reset_db()
    only_low = bool(args.get("only_low", False))
    sku = args.get("sku")
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
    for found in STATE["conn"].execute(sql, params):
        item = dict(found)
        item["gap"] = gap_for(item)
        rows.append(item)
    payload = {"rows": rows}
    if isinstance(sku, str) and sku.strip() and not rows:
        payload["error"] = "unknown sku " + sku.strip()
    return json.dumps(payload)


def read_shop_file(args):
    """Model-facing file tool. Only docs/policy.md and docs/faq.md resolve."""
    return _read_docs(args.get("path", ""))


register(
    "read_shop_file",
    "Read a shop document. path is policy.md or faq.md. "
    "policy.md has returns, shipping, damage, and local delivery. "
    "faq.md has hours, the menu, and allergens. "
    "Paths outside docs/ return ERROR.",
    {"path": {"type": "string", "description": "policy.md or faq.md"}},
    ["path"],
    read_shop_file,
)
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
