"""Line-delimited JSON-RPC frames for the Chapter 9 teaching servers.

One JSON object per line. This is the local transport the lab uses.
It is not a full MCP SDK.
"""

from __future__ import annotations

import json
import sys
from typing import IO, Any


def read_message(stream: IO[str] | None = None) -> dict[str, Any] | None:
    """Read one JSON object, or return None at end of stream."""
    src = sys.stdin if stream is None else stream
    line = src.readline()
    if not line:
        return None
    message = json.loads(line)
    if not isinstance(message, dict):
        raise ValueError("JSON-RPC message must be an object")
    return message


def write_message(payload: dict[str, Any], stream: IO[str] | None = None) -> None:
    """Write one JSON object and flush."""
    dest = sys.stdout if stream is None else stream
    dest.write(json.dumps(payload) + "\n")
    dest.flush()
