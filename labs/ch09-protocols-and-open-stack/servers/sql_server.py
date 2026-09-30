#!/usr/bin/env python3
"""SQL MCP teaching server. tools/list and tools/call are TODOs.

Speak JSON-RPC on stdin/stdout, one object per line. The concierge must
use this process. It must not open the database itself.
"""

from __future__ import annotations

import sys
from pathlib import Path

LAB = Path(__file__).resolve().parents[1]
if str(LAB) not in sys.path:
    sys.path.insert(0, str(LAB))

from rpc import read_message, write_message  # noqa: E402

DB_PATH = LAB / "shop.db"
SERVER_VERSION = "shop-sql/0-todo"


def handle(method: str, params: dict) -> dict:
    """Answer one MCP method.

    TODO: set SERVER_VERSION to shop-sql/1 when the schema below is real.
    TODO: tools/list returns sql_query with an inputSchema that requires sql.
    TODO: tools/call runs a single read-only SELECT against DB_PATH.
    Reject writes, multiple statements, and missing files with a result
    the host can show the model, beginning with ERROR.
    Cap the number of rows.
    """
    if method == "initialize":
        return {
            "protocolVersion": "lab",
            "serverInfo": {"name": "shop-sql", "version": SERVER_VERSION},
            "capabilities": {"tools": {}},
        }
    if method == "tools/list":
        raise NotImplementedError("TODO: list sql_query")
    if method == "tools/call":
        raise NotImplementedError("TODO: execute a bounded read and return text")
    raise NotImplementedError(f"TODO: method {method!r} is not implemented")


def main() -> int:
    while True:
        try:
            message = read_message()
        except ValueError as exc:
            write_message(
                {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": str(exc)}}
            )
            continue
        if message is None:
            return 0
        req_id = message.get("id")
        method = str(message.get("method") or "")
        params = message.get("params") or {}
        if not isinstance(params, dict):
            params = {}
        try:
            result = handle(method, params)
        except NotImplementedError as exc:
            write_message(
                {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {"code": -32601, "message": str(exc)},
                }
            )
            continue
        write_message({"jsonrpc": "2.0", "id": req_id, "result": result})


if __name__ == "__main__":
    raise SystemExit(main())
