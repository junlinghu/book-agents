"""Message helpers shared by the loop and the notebooks.

No other tutorial module is imported here.
"""

import json


def preview(text, limit=500):
    """Shorten a tool result for the printed trace. The model still gets the full string."""
    text = text if isinstance(text, str) else str(text)
    if len(text) <= limit:
        return text
    return text[:limit] + "\n... [" + str(len(text)) + " characters]"


def assistant_message(turned):
    """Copy an assistant turn into the message list, including any tool calls."""
    message = {"role": "assistant", "content": turned["content"] or ""}
    calls = turned["tool_calls"] or []
    if calls:
        message["tool_calls"] = []
        for call in calls:
            raw = call.get("raw") or json.dumps(call["arguments"], sort_keys=True)
            message["tool_calls"].append({
                "id": call["id"],
                "type": "function",
                "function": {"name": call["name"], "arguments": raw},
            })
    return message


__all__ = [
    "assistant_message",
    "preview",
]
