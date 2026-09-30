#!/usr/bin/env python3
"""Chapter 10 scaffold. Each run places an order. That is the bug.

TODO: checkpoint the session under sessions/, pause before placement
when RESTOCK_PAUSE=1, require a recorded confirmation, and make
placement idempotent so a resume does not append a second ledger row.
"""

from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

LAB = Path(__file__).resolve().parent
DB_PATH = LAB / "shop.db"
LEDGER_PATH = LAB / "ledger.jsonl"
SESSIONS = LAB / "sessions"


def read_stock(sku: str) -> dict:
    """Return on_hand and par for sku. Raises if the database or row is missing."""
    if not DB_PATH.is_file():
        raise SystemExit(f"Missing {DB_PATH}. Run init_db.py first.")
    with sqlite3.connect(DB_PATH) as conn:
        row = conn.execute(
            "SELECT sku, name, on_hand, par FROM inventory WHERE sku = ?",
            (sku,),
        ).fetchone()
    if row is None:
        raise SystemExit(f"Unknown sku: {sku}")
    return {"sku": row[0], "name": row[1], "on_hand": row[2], "par": row[3]}


def save_checkpoint(session: dict) -> None:
    """TODO: write session JSON under SESSIONS / session_id.

    Include the draft quantity, completed steps, confirm_status,
    idempotency key, and order_id (null until the ledger returns one).
    """
    raise NotImplementedError("TODO: save_checkpoint")


def load_checkpoint(session_id: str) -> dict | None:
    """TODO: return the checkpoint dict, or None if this session has no file."""
    raise NotImplementedError("TODO: load_checkpoint")


def confirmation_status(session: dict) -> str:
    """TODO: read a human yes bound to this draft.

    A transcript sentence is not enough. Return ``pending``,
    ``confirmed``, or ``refused``. As shipped, nothing is confirmed.
    """
    return "pending"


def append_order(session: dict, qty: int) -> dict:
    """Append a ledger row. TODO: one row per idempotency key.

    A second call for the same session currently appends another order.
    Return the existing row instead once you finish the TODO.
    """
    LEDGER_PATH.parent.mkdir(parents=True, exist_ok=True)
    existing = []
    if LEDGER_PATH.is_file():
        existing = [
            json.loads(line)
            for line in LEDGER_PATH.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
    order = {
        "order_id": f"PO-{len(existing) + 1}",
        "session_id": session["session_id"],
        "sku": session["sku"],
        "qty": qty,
        "idempotency_key": session.get("idempotency_key"),
    }
    with LEDGER_PATH.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(order) + "\n")
    return order


def run_session(session: dict) -> dict:
    """Read stock, draft, and place.

    TODO: resume from load_checkpoint. Skip steps already completed.
    TODO: save a checkpoint after the draft and exit when the
    environment variable RESTOCK_PAUSE is ``1``, before append_order.
    TODO: do not call append_order unless confirmation_status is
    ``confirmed`` and this session has no order_id yet.
    """
    stock = read_stock(session["sku"])
    qty = stock["par"] - stock["on_hand"]
    session["on_hand"] = stock["on_hand"]
    session["par"] = stock["par"]
    session["draft_qty"] = qty
    session["status"] = "placing"
    order = append_order(session, qty)
    session["order_id"] = order["order_id"]
    session["status"] = "placed"
    return session


def ledger_rows() -> list[dict]:
    if not LEDGER_PATH.is_file():
        return []
    return [
        json.loads(line)
        for line in LEDGER_PATH.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    session_id = args[0] if args else "restock-1842"
    session = {
        "session_id": session_id,
        "sku": "house-coffee",
        "idempotency_key": session_id,
        "order_id": None,
        "status": "new",
    }
    print(f"SESSION={session_id}")
    print(f"LEDGER={LEDGER_PATH}")
    finished = run_session(session)
    print(json.dumps(finished, indent=2))
    rows = [row for row in ledger_rows() if row.get("session_id") == session_id]
    print(f"LEDGER_ROWS_FOR_SESSION={len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
