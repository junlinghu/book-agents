"""JSON tool results the model can branch on.

Chapter 2 returns ``ERROR:`` strings. Chapters 4–6 return this object so a
later turn can read ``code`` and ``retryable`` instead of guessing from prose.
"""

from __future__ import annotations

import json


def tool_payload(
    ok: bool,
    code: str,
    message: str,
    *,
    retryable: bool = False,
    hint: str = "",
    **extra: object,
) -> str:
    """Serialize one tool result. ``extra`` is merged after the fixed keys."""
    body: dict[str, object] = {
        "ok": ok,
        "code": code,
        "retryable": retryable,
        "message": message,
        "hint": hint,
    }
    body.update(extra)
    return json.dumps(body, indent=2)
