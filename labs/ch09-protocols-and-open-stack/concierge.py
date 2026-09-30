#!/usr/bin/env python3
"""Chapter 9 scaffold. The concierge may talk to MCP servers and the model.

TODO: start servers/sql_server.py and servers/fetch_server.py as
processes, send JSON-RPC on their stdin, and translate tools/list into
the chat tool list. Do not open the database or the network in this file.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

LAB = Path(__file__).resolve().parent


def list_tools(server_script: Path) -> list[dict]:
    """TODO: initialize the server, call tools/list, return the tool dicts."""
    raise NotImplementedError(f"TODO: tools/list via {server_script.name}")


def call_tool(server_script: Path, name: str, arguments: dict) -> str:
    """TODO: tools/call. Return the text observation, or an ERROR string."""
    raise NotImplementedError(f"TODO: tools/call {name} via {server_script.name}")


def main(argv: list[str] | None = None) -> int:
    question = " ".join(sys.argv[1:] if argv is None else argv).strip()
    if not question:
        question = (
            "Does the public board match the register for the cardamom bun? "
            "The board is http://127.0.0.1:8765/shop.html."
        )
    print(f"LAB={LAB}")
    print(f"QUESTION: {question}")
    print(
        "Concierge scaffold: list_tools and call_tool are not implemented. "
        "Wire MCP before you call the model."
    )
    try:
        list_tools(LAB / "servers" / "sql_server.py")
    except NotImplementedError as exc:
        print(exc, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
