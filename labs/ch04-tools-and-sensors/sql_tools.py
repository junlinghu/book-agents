"""SQL sensor and a tightly limited shelf actuator for Hearth Lane Café.

``sql_query`` is read-only and ready to run. ``sql_execute`` will not change
the database until ``parse_restock`` accepts the one allowed statement.
"""

from __future__ import annotations

import json
import re
import sqlite3
import time
from pathlib import Path
from urllib.parse import quote

from labs.common.payload import tool_payload

# Wall-clock budget for one read. The step cap in the loop counts model
# calls, not time. A hung sensor would otherwise sit inside one step.
QUERY_TIMEOUT_S = 2.0

# How many times the harness may run a retryable read before the model sees it.
READ_ATTEMPTS = 2

MAX_ROWS = 20

# Words that must not appear in a statement the read tool will run.
# ATTACH is rejected even though a read-only connection still allows it.
_FORBIDDEN_WORDS = frozenset(
    {
        "alter",
        "analyze",
        "attach",
        "begin",
        "commit",
        "create",
        "delete",
        "detach",
        "drop",
        "insert",
        "load_extension",
        "pragma",
        "reindex",
        "replace",
        "rollback",
        "update",
        "vacuum",
    }
)

# sku, name, category, unit, reorder_point, on_hand, par
SEED_ROWS: tuple[tuple[str, str, str, str, int, int, int], ...] = (
    ("HB-12", "House blend 12oz", "coffee", "bag", 6, 4, 18),
    ("HB-2LB", "House blend 2lb", "coffee", "bag", 4, 9, 10),
    ("ES-1KG", "Espresso beans 1kg", "coffee", "bag", 5, 5, 12),
    ("OM-32", "Oat milk 32oz", "dairy", "carton", 8, 3, 16),
    ("MLK-1", "Whole milk gallon", "dairy", "gallon", 4, 11, 12),
    ("ALM-1", "Almond meal", "bakery", "bag", 2, 1, 4),
    ("FL-01", "Paper filters", "supply", "box", 2, 7, 8),
)

SQL_QUERY_TOOL: dict = {
    "type": "function",
    "function": {
        "name": "sql_query",
        "description": (
            "Read the café shelf. Runs one SELECT against products and "
            "inventory. Low stock means inventory.on_hand <= products.reorder_point. "
            "Columns: products.sku, name, category, unit, reorder_point; "
            "inventory.sku, on_hand, par. "
            "Does not insert, update, or delete. A write belongs in sql_execute. "
            "The result is JSON with ok, code, retryable, and either rows or a hint."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "sql": {
                    "type": "string",
                    "description": "A single SELECT. Do not include a semicolon.",
                }
            },
            "required": ["sql"],
        },
    },
}

SQL_EXECUTE_TOOL: dict = {
    "type": "function",
    "function": {
        "name": "sql_execute",
        "description": (
            "Set the on-hand count for one sku. This does not order from a "
            "supplier and does not take payment. "
            "The only statement that can succeed is "
            "UPDATE inventory SET on_hand = <integer> WHERE sku = '<sku>'. "
            "The integer is the new absolute count, between 0 and that sku's par. "
            "Pass an idempotency_key such as restock-2026-09-30-HB-12. "
            "A repeated key returns the first result and does not write again."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "sql": {
                    "type": "string",
                    "description": "The single UPDATE described above.",
                },
                "idempotency_key": {
                    "type": "string",
                    "description": "Unique key for this restock. Reuse it on a retry.",
                },
            },
            "required": ["sql", "idempotency_key"],
        },
    },
}


def tool_result(
    ok: bool,
    code: str,
    message: str,
    *,
    retryable: bool = False,
    hint: str = "",
    **extra: object,
) -> str:
    return tool_payload(ok, code, message, retryable=retryable, hint=hint, **extra)


def seed_database(db_path: Path) -> None:
    """Rebuild ``shop.db`` so each run starts from the same shelf."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    if db_path.exists():
        db_path.unlink()
    conn = sqlite3.connect(db_path)
    try:
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
              sku TEXT PRIMARY KEY REFERENCES products(sku),
              on_hand INTEGER NOT NULL CHECK (on_hand >= 0),
              par INTEGER NOT NULL
            );
            CREATE TABLE applied_writes (
              idempotency_key TEXT PRIMARY KEY,
              result_json TEXT NOT NULL
            );
            """
        )
        conn.executemany(
            """
            INSERT INTO products (sku, name, category, unit, reorder_point)
            VALUES (?, ?, ?, ?, ?)
            """,
            [
                (sku, name, category, unit, reorder)
                for sku, name, category, unit, reorder, _on_hand, _par in SEED_ROWS
            ],
        )
        conn.executemany(
            "INSERT INTO inventory (sku, on_hand, par) VALUES (?, ?, ?)",
            [
                (sku, on_hand, par)
                for sku, _name, _category, _unit, _reorder, on_hand, par in SEED_ROWS
            ],
        )
        conn.commit()
    finally:
        conn.close()


def _strip_string_literals(sql: str) -> str:
    """Replace quoted strings so a word inside a literal is not a keyword."""
    return re.sub(r"'([^']|'')*'", "''", sql)


def classify_select(sql: str) -> str | None:
    """Return an error code, or None when the statement may be attempted.

    The read-only connection is the real write barrier. This classifier
    rejects shapes that connection would still run, such as ATTACH.
    """
    if not isinstance(sql, str) or not sql.strip():
        return "empty_sql"
    text = sql.strip()
    if ";" in text:
        return "multi_statement"
    if "--" in text or "/*" in text:
        return "comments_not_allowed"
    words = re.findall(r"[A-Za-z_]+", _strip_string_literals(text))
    if any(word.lower() in _FORBIDDEN_WORDS for word in words):
        return "forbidden_sql"
    if not words or words[0].lower() not in {"select", "with"}:
        return "not_select"
    return None


def _readonly(db_path: Path) -> sqlite3.Connection:
    uri = "file:" + quote(db_path.resolve().as_posix(), safe="/:") + "?mode=ro"
    conn = sqlite3.connect(uri, uri=True, timeout=0.2)
    conn.row_factory = sqlite3.Row
    return conn


def _query_once(db_path: Path, sql: str, timeout_s: float) -> str:
    code = classify_select(sql)
    if code == "empty_sql":
        return tool_result(
            False,
            code,
            "sql is required.",
            hint="Send one SELECT. Low stock is on_hand <= reorder_point.",
        )
    if code == "multi_statement":
        return tool_result(
            False,
            code,
            "sql_query runs one statement. A semicolon was present.",
            hint="Remove the semicolon and send a single SELECT.",
        )
    if code == "comments_not_allowed":
        return tool_result(
            False,
            code,
            "sql_query does not accept SQL comments.",
            hint="Remove -- and /* */ and send a single SELECT.",
        )
    if code == "not_select":
        return tool_result(
            False,
            code,
            "sql_query only runs a single read-only SELECT.",
            hint=(
                "Join products to inventory and select sku, name, on_hand, "
                "reorder_point where on_hand <= reorder_point. "
                "Writes belong in sql_execute."
            ),
        )
    if code == "forbidden_sql":
        return tool_result(
            False,
            code,
            "This statement is not a plain SELECT over the shelf.",
            hint="Do not ATTACH another database, and do not write. Use a single SELECT.",
        )

    if not db_path.is_file():
        return tool_result(
            False,
            "no_database",
            "shop.db is not on disk.",
            hint="Run stock_agent.py so the harness can seed the shelf.",
        )

    start = time.monotonic()

    def _progress() -> int:
        if time.monotonic() - start > timeout_s:
            return 1
        return 0

    conn = _readonly(db_path)
    try:
        conn.set_progress_handler(_progress, 1000)
        try:
            cur = conn.execute(sql)
            fetched = cur.fetchmany(MAX_ROWS + 1)
        except sqlite3.OperationalError as exc:
            text = str(exc).lower()
            if "interrupted" in text:
                return tool_result(
                    False,
                    "timeout",
                    f"The read exceeded {timeout_s:.1f}s and was interrupted.",
                    retryable=True,
                    hint="Retry the same SELECT once. Do not switch to a write.",
                )
            if "locked" in text or "busy" in text:
                return tool_result(
                    False,
                    "busy",
                    "The database was locked.",
                    retryable=True,
                    hint="Retry the same SELECT once.",
                )
            if "readonly" in text:
                return tool_result(
                    False,
                    "forbidden_sql",
                    "The read connection refused a write.",
                    hint="Use sql_query for SELECT only. Use sql_execute to set on_hand.",
                )
            return tool_result(
                False,
                "bad_sql",
                f"SQLite refused the statement: {exc}",
                hint="Check table and column names against the tool description.",
            )
        except sqlite3.ProgrammingError as exc:
            return tool_result(
                False,
                "bad_sql",
                f"SQLite refused the statement: {exc}",
                hint="Send one SELECT with no semicolon.",
            )
    finally:
        conn.set_progress_handler(None, 0)
        conn.close()

    truncated = len(fetched) > MAX_ROWS
    rows = fetched[:MAX_ROWS]
    columns = list(rows[0].keys()) if rows else []
    payload_rows = [list(row) for row in rows]
    return tool_result(
        True,
        "ok",
        f"{len(payload_rows)} row(s).",
        columns=columns,
        rows=payload_rows,
        truncated=truncated,
        hint="" if not truncated else f"Only the first {MAX_ROWS} rows were returned.",
    )


def sql_query(db_path: Path, sql: str, *, timeout_s: float = QUERY_TIMEOUT_S) -> str:
    """Run a read. Retry a timeout or a lock inside the harness, once.

    The model sees a single tool result. ``attempts`` is 2 when the harness
    retried. Syntax errors and forbidden statements are not retried.
    """
    result = _query_once(db_path, sql, timeout_s)
    payload = json.loads(result)
    if not payload.get("retryable"):
        return result
    second = _query_once(db_path, sql, timeout_s)
    body = json.loads(second)
    body["attempts"] = READ_ATTEMPTS
    # The harness already spent the one retry. The model should change
    # the statement, not send this one again.
    if body.get("ok") is not True:
        body["retryable"] = False
    return json.dumps(body, indent=2)


def parse_restock(statement: str) -> tuple[str, int] | None:
    """Parse one absolute shelf update, or return None to refuse it.

    TODO(learner): accept only this shape, aside from surrounding whitespace::

        UPDATE inventory SET on_hand = <integer> WHERE sku = '<sku>'

    One statement, no semicolon, no comments, no other columns. Return
    ``(sku, on_hand)``. The starter returns None, so every write is refused
    and the raw statement is never executed.
    """
    return None


def _lookup_write(conn: sqlite3.Connection, key: str) -> str | None:
    row = conn.execute(
        "SELECT result_json FROM applied_writes WHERE idempotency_key = ?",
        (key,),
    ).fetchone()
    if row is None:
        return None
    body = json.loads(row[0])
    body["replayed"] = True
    return json.dumps(body, indent=2)


def sql_execute(db_path: Path, statement: str, idempotency_key: str) -> str:
    """Set one on-hand count, if ``parse_restock`` accepts the statement.

    The model's SQL text is not executed. A successful parse becomes the
    fixed statement ``UPDATE inventory SET on_hand = ? WHERE sku = ?``.
    """
    if not isinstance(idempotency_key, str) or not idempotency_key.strip():
        return tool_result(
            False,
            "missing_key",
            "idempotency_key is required.",
            hint="Pass a key such as restock-2026-09-30-HB-12 and reuse it on a retry.",
        )
    key = idempotency_key.strip()
    if len(key) > 80:
        return tool_result(
            False,
            "missing_key",
            "idempotency_key is too long.",
            hint="Use a key of at most 80 characters.",
        )
    if not db_path.is_file():
        return tool_result(
            False,
            "no_database",
            "shop.db is not on disk.",
            hint="Run stock_agent.py so the harness can seed the shelf.",
        )

    conn = sqlite3.connect(db_path, timeout=0.2)
    conn.row_factory = sqlite3.Row
    try:
        prior = _lookup_write(conn, key)
        if prior is not None:
            return prior

        parsed = parse_restock(statement)
        if parsed is None:
            return tool_result(
                False,
                "write_not_allowed",
                "sql_execute refused this statement.",
                hint=(
                    "Allowed shape: UPDATE inventory SET on_hand = <integer> "
                    "WHERE sku = '<sku>'. parse_restock must return that pair. "
                    "None refuses the write, and the statement is not executed."
                ),
            )
        sku, on_hand = parsed
        if not isinstance(sku, str) or not isinstance(on_hand, int) or isinstance(on_hand, bool):
            return tool_result(
                False,
                "write_not_allowed",
                "parse_restock must return (sku, on_hand) with an int count.",
                hint="Return a tuple of one sku string and one integer.",
            )
        row = conn.execute(
            """
            SELECT inventory.on_hand, inventory.par
            FROM inventory
            JOIN products ON products.sku = inventory.sku
            WHERE inventory.sku = ?
            """,
            (sku,),
        ).fetchone()
        if row is None:
            return tool_result(
                False,
                "unknown_sku",
                f"No inventory row for sku {sku!r}.",
                hint="Read products with sql_query and use a sku from that result.",
            )
        par = int(row["par"])
        if on_hand < 0 or on_hand > par:
            return tool_result(
                False,
                "above_par",
                f"on_hand must be between 0 and par ({par}) for {sku}.",
                hint="Set an absolute count inside that range. Do not add a delta.",
            )
        conn.execute(
            "UPDATE inventory SET on_hand = ? WHERE sku = ?",
            (on_hand, sku),
        )
        result = tool_result(
            True,
            "applied",
            f"Set {sku} on_hand to {on_hand}.",
            sku=sku,
            on_hand=on_hand,
            previous_on_hand=int(row["on_hand"]),
        )
        conn.execute(
            "INSERT INTO applied_writes (idempotency_key, result_json) VALUES (?, ?)",
            (key, result),
        )
        conn.commit()
        return result
    finally:
        conn.close()


def probe_timeout(db_path: Path) -> str:
    """Run a deliberately long read with a short timeout. Used by ``--check``."""
    sql = (
        "WITH RECURSIVE c(x) AS ("
        "SELECT 1 UNION ALL SELECT x + 1 FROM c LIMIT 5000000"
        ") SELECT max(x) FROM c"
    )
    return sql_query(db_path, sql, timeout_s=0.05)
