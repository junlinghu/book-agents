#!/usr/bin/env python3
"""Fetch MCP teaching server. tools/list and tools/call are TODOs."""

from __future__ import annotations

import sys
from pathlib import Path

LAB = Path(__file__).resolve().parents[1]
if str(LAB) not in sys.path:
    sys.path.insert(0, str(LAB))

from rpc import read_message, write_message  # noqa: E402

ALLOWED_PREFIX = "http://127.0.0.1:8765/"
SERVER_VERSION = "shop-fetch/0-todo"


def handle(method: str, params: dict) -> dict:
    """Answer one MCP method.

    TODO: set SERVER_VERSION to shop-fetch/1 when fetch_page is real.
    TODO: tools/list returns fetch_page with an inputSchema that requires url.
    TODO: tools/call GETs a URL only when it starts with ALLOWED_PREFIX.
    Success text begins with the URL, the status, and UNTRUSTED PAGE TEXT.
    Any other host returns ERROR and does not perform the request.
    """
    if method == "initialize":
        return {
            "protocolVersion": "lab",
            "serverInfo": {"name": "shop-fetch", "version": SERVER_VERSION},
            "capabilities": {"tools": {}},
        }
    if method == "tools/list":
        raise NotImplementedError("TODO: list fetch_page")
    if method == "tools/call":
        raise NotImplementedError("TODO: fetch an allowlisted URL or return ERROR")
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
