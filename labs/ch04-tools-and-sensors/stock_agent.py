#!/usr/bin/env python3
"""Shelf concierge: a read-only SQL sensor and a stubbed restock actuator.

Chapter 4 lab. The script seeds shop.db on every run, then asks what is
low. sql_execute refuses writes until parse_restock in sql_tools.py
accepts the one allowed UPDATE.

  python labs/ch04-tools-and-sensors/stock_agent.py
  python labs/ch04-tools-and-sensors/stock_agent.py --check
"""

from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LAB_DIR = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(LAB_DIR) not in sys.path:
    sys.path.insert(0, str(LAB_DIR))

from labs.common.client import describe_runtime, make_client, redact, require_settings  # noqa: E402
from labs.common.loop import DEFAULT_MAX_STEPS, run_tool_agent  # noqa: E402
from sql_tools import (  # noqa: E402
    QUERY_TIMEOUT_S,
    SEED_ROWS,
    SQL_EXECUTE_TOOL,
    SQL_QUERY_TOOL,
    probe_timeout,
    seed_database,
    sql_execute,
    sql_query,
)

DB_PATH = Path(__file__).resolve().parent / "shop.db"

DEFAULT_QUESTION = "What's low stock?"

SYSTEM_PROMPT = """You are the counter concierge for Hearth Lane Café, checking the back shelf.
Low stock means inventory.on_hand is less than or equal to products.reorder_point.
Use sql_query before you name a count. It runs one SELECT and returns JSON.
Use sql_execute only when you are asked to set an on-hand count. It does not
order from a supplier, send email, or take payment.
If a tool result has ok false, read code, retryable, and hint, and repair the
next call. Do not invent a count the tool did not return.
Do not claim a count changed unless sql_execute returned ok true.
"""

REPEAT_NOTE = (
    "\n\nNOTE: You already called this tool with the same arguments. "
    "Answer from the result you have."
)


def _dispatch(name: str, args: dict) -> str:
    if name == "sql_query":
        sql = args.get("sql", "")
        if not isinstance(sql, str):
            return sql_query(DB_PATH, "")
        return sql_query(DB_PATH, sql)
    if name == "sql_execute":
        statement = args.get("sql", "")
        key = args.get("idempotency_key", "")
        if not isinstance(statement, str):
            statement = ""
        if not isinstance(key, str):
            key = ""
        return sql_execute(DB_PATH, statement, key)
    return json.dumps(
        {
            "ok": False,
            "code": "unknown_tool",
            "retryable": False,
            "message": f"Unknown tool {name!r}.",
            "hint": "Use sql_query to read and sql_execute to set on_hand.",
        },
        indent=2,
    )


def _low_skus(db_path: Path) -> list[str]:
    conn = sqlite3.connect(db_path)
    try:
        rows = conn.execute(
            """
            SELECT products.sku
            FROM products
            JOIN inventory ON inventory.sku = products.sku
            WHERE inventory.on_hand <= products.reorder_point
            ORDER BY products.sku
            """
        ).fetchall()
    finally:
        conn.close()
    return [row[0] for row in rows]


def run_check() -> int:
    """Exercise the SQL tools without a model. Does not grade a paragraph."""
    seed_database(DB_PATH)
    print(f"DB={DB_PATH}")
    print(f"QUERY_TIMEOUT_S={QUERY_TIMEOUT_S}")
    print(f"SEED_SKUS={[row[0] for row in SEED_ROWS]}")

    low = sql_query(
        DB_PATH,
        """
        SELECT products.sku, products.name, inventory.on_hand, products.reorder_point
        FROM products
        JOIN inventory ON inventory.sku = products.sku
        WHERE inventory.on_hand <= products.reorder_point
        ORDER BY products.sku
        """,
    )
    payload = json.loads(low)
    got = [row[0] for row in payload.get("rows", [])]
    expect = _low_skus(DB_PATH)
    print("--- sql_query low stock ---")
    print(low)
    if payload.get("ok") is not True or got != expect:
        print("CHECK FAIL: the read tool did not return the low-stock skus.")
        return 1

    failures = 0
    probes = [
        "DROP TABLE inventory",
        "UPDATE inventory SET on_hand = 0",
        "SELECT 1; DROP TABLE inventory",
        "ATTACH DATABASE ':memory:' AS other",
        "SELECT load_extension('x')",
    ]
    for sql in probes:
        body = json.loads(sql_query(DB_PATH, sql))
        print(f"--- sql_query refused {sql!r}: code={body.get('code')} ok={body.get('ok')} ---")
        if body.get("ok") is not False:
            print("CHECK FAIL: sql_query accepted a statement it must refuse.")
            failures += 1

    timed = json.loads(probe_timeout(DB_PATH))
    print(f"--- timeout probe: code={timed.get('code')} retryable={timed.get('retryable')} attempts={timed.get('attempts')} ---")
    if timed.get("code") != "timeout" or timed.get("attempts") != 2:
        print("CHECK FAIL: a long read was not retried once inside the harness.")
        failures += 1
    if timed.get("retryable") is not False:
        print("CHECK FAIL: the model-facing timeout is still marked retryable after the harness retry.")
        failures += 1

    before = _snapshot(DB_PATH)
    dropped = json.loads(sql_execute(DB_PATH, "DROP TABLE inventory", "should-not-apply"))
    print(f"--- sql_execute DROP: code={dropped.get('code')} ok={dropped.get('ok')} ---")
    if dropped.get("ok") is not False or _snapshot(DB_PATH) != before:
        print("CHECK FAIL: sql_execute changed the shelf for a DROP statement.")
        failures += 1

    restock_sql = "UPDATE inventory SET on_hand = 16 WHERE sku = 'HB-12'"
    key = "restock-2026-09-30-HB-12"
    first = json.loads(sql_execute(DB_PATH, restock_sql, key))
    print(f"--- sql_execute restock: code={first.get('code')} ok={first.get('ok')} ---")
    if first.get("ok") is not True:
        print(
            "TASK OPEN: parse_restock does not yet accept the allowed UPDATE. "
            "The shelf was not changed. Fill in sql_tools.py and run --check again."
        )
    else:
        hb = _on_hand(DB_PATH, "HB-12")
        replay = json.loads(sql_execute(DB_PATH, restock_sql, key))
        if hb != 16 or replay.get("replayed") is not True or _on_hand(DB_PATH, "HB-12") != 16:
            print("CHECK FAIL: the restock did not apply once and replay.")
            failures += 1
        else:
            print("TASK DONE: HB-12 was set to 16 once. The same key replayed.")
        over = json.loads(
            sql_execute(
                DB_PATH,
                "UPDATE inventory SET on_hand = 99 WHERE sku = 'HB-12'",
                "restock-2026-09-30-HB-12-over",
            )
        )
        print(f"--- above par: code={over.get('code')} ok={over.get('ok')} ---")
        if over.get("code") != "above_par" or _on_hand(DB_PATH, "HB-12") != 16:
            print("CHECK FAIL: a count above par was stored.")
            failures += 1

    if failures:
        return 1
    print("CHECK OK")
    return 0


def _snapshot(db_path: Path) -> list[tuple[str, int]]:
    conn = sqlite3.connect(db_path)
    try:
        return list(conn.execute("SELECT sku, on_hand FROM inventory ORDER BY sku"))
    finally:
        conn.close()


def _on_hand(db_path: Path, sku: str) -> int | None:
    conn = sqlite3.connect(db_path)
    try:
        row = conn.execute("SELECT on_hand FROM inventory WHERE sku = ?", (sku,)).fetchone()
    finally:
        conn.close()
    if row is None:
        return None
    return int(row[0])


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if "--check" in args:
        return run_check()

    question = " ".join(arg for arg in args if not arg.startswith("--")).strip()
    question = question or DEFAULT_QUESTION
    seed_database(DB_PATH)
    print(describe_runtime())
    print(f"DB={DB_PATH}")
    print(f"QUERY_TIMEOUT_S={QUERY_TIMEOUT_S}")
    print(f"MAX_STEPS={DEFAULT_MAX_STEPS}")
    print("WRITE=refused until parse_restock accepts the allowed UPDATE")
    print(f"QUESTION: {question}\n")

    api_key, model = require_settings()
    client = make_client()
    try:
        result = run_tool_agent(
            client,
            model,
            question,
            [SQL_QUERY_TOOL, SQL_EXECUTE_TOOL],
            _dispatch,
            system_prompt=SYSTEM_PROMPT,
            max_steps=DEFAULT_MAX_STEPS,
            verbose=True,
            arguments_hint='{"sql": "SELECT sku, name FROM products"}',
            repeat_note=REPEAT_NOTE,
        )
    except Exception as exc:
        print(redact(f"Request failed: {type(exc).__name__}: {exc}", api_key), file=sys.stderr)
        print(
            "Check OPENAI_API_KEY and MODEL in .env.",
            file=sys.stderr,
        )
        return 1

    print("--- answer ---")
    print(result.text)
    print()
    print(f"--- stop: {result.stopped} after {result.steps} model call(s) ---")
    if result.stopped == "final" and not result.tool_log:
        print(
            "NOTE: No tool ran. Counts in the answer were not read from shop.db. "
            "The lab does not send tool_choice."
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
