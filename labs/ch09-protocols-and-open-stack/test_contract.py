#!/usr/bin/env python3
"""Contract tests for the Chapter 9 servers. No model call.

Run from the repo root:

    python labs/ch09-protocols-and-open-stack/test_contract.py

The shipped servers fail these tests until tools/list, tools/call, and
the server versions are finished.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

LAB = Path(__file__).resolve().parent
if str(LAB) not in sys.path:
    sys.path.insert(0, str(LAB))

from servers import fetch_server, sql_server  # noqa: E402


def _tool_names(result: dict) -> list[str]:
    tools = result["tools"]
    return [tool["name"] for tool in tools]


def _required(result: dict, name: str) -> list[str]:
    for tool in result["tools"]:
        if tool["name"] == name:
            schema = tool["inputSchema"]
            return list(schema.get("required") or [])
    return []


class SqlContract(unittest.TestCase):
    def test_version(self) -> None:
        result = sql_server.handle("initialize", {})
        self.assertEqual(result["serverInfo"]["version"], "shop-sql/1")

    def test_lists_sql_query(self) -> None:
        result = sql_server.handle("tools/list", {})
        self.assertIn("sql_query", _tool_names(result))
        self.assertIn("sql", _required(result, "sql_query"))

    def test_bun_price_is_register_cents(self) -> None:
        result = sql_server.handle(
            "tools/call",
            {
                "name": "sql_query",
                "arguments": {
                    "sql": "SELECT price_cents FROM products WHERE sku = 'cardamom-bun'"
                },
            },
        )
        text = _result_text(result)
        self.assertIn("475", text)
        self.assertNotIn("ERROR:", text.splitlines()[0])

    def test_write_is_refused(self) -> None:
        result = sql_server.handle(
            "tools/call",
            {
                "name": "sql_query",
                "arguments": {"sql": "DELETE FROM products"},
            },
        )
        text = _result_text(result)
        self.assertTrue(text.startswith("ERROR:"), text)


class FetchContract(unittest.TestCase):
    def test_version(self) -> None:
        result = fetch_server.handle("initialize", {})
        self.assertEqual(result["serverInfo"]["version"], "shop-fetch/1")

    def test_lists_fetch_page(self) -> None:
        result = fetch_server.handle("tools/list", {})
        self.assertIn("fetch_page", _tool_names(result))
        self.assertIn("url", _required(result, "fetch_page"))

    def test_off_allowlist_is_refused(self) -> None:
        result = fetch_server.handle(
            "tools/call",
            {
                "name": "fetch_page",
                "arguments": {"url": "http://example.com/shop.html"},
            },
        )
        text = _result_text(result)
        self.assertTrue(text.startswith("ERROR:"), text)


class ConciergeBoundary(unittest.TestCase):
    def test_concierge_does_not_open_sql_or_http(self) -> None:
        text = (LAB / "concierge.py").read_text(encoding="utf-8")
        for line in text.splitlines():
            stripped = line.strip()
            if stripped.startswith("#"):
                continue
            self.assertNotIn("sqlite3", stripped)
            self.assertNotIn("httpx", stripped)


def _result_text(result: dict) -> str:
    """Accept either a content list or a plain text field."""
    if "content" in result:
        parts = []
        for block in result["content"]:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict):
                parts.append(str(block.get("text", "")))
        return "\n".join(parts)
    if "text" in result:
        return str(result["text"])
    if "isError" in result and result.get("content"):
        return _result_text({"content": result["content"]})
    return str(result)


if __name__ == "__main__":
    unittest.main()
