import json
import re
import sqlite3
import time
from pathlib import Path

HERE = ROOT / "labs" / "tutorial"
DOCS = ROOT / "labs" / "ch02-your-first-loop" / "docs"
DATA = HERE / "data"
VAR = HERE / "var"

HANDLERS = {}
TOOLS = []


def register(name, description, properties, required, fn):
    """Add one Chat Completions tool. ``fn`` runs only if the harness allows it."""
    spec = {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required,
            },
        },
    }
    # Re-running a cell replaces the previous schema instead of stacking a second copy.
    TOOLS[:] = [tool for tool in TOOLS if tool["function"]["name"] != name]
    TOOLS.append(spec)
    HANDLERS[name] = fn


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


def check(condition, message):
    """Fail the demo when the scripted path drifts. Warn, and continue, on a live model."""
    if condition:
        print("check ok:", message)
        return
    if USING_DEMO:
        raise AssertionError(message)
    print("check warning (live model):", message)


def base_rules():
    return (
        "You are the counter concierge for Hearth Lane Café. "
        "Shop facts come from tools, not from guesses in the prompt. "
        "If a tool does not say, say you don't know. "
        "Cite the tool or the docs path you used. "
        "Do not invent a Wi-Fi password, a refund, or a shipping exception. "
        "Do not charge a card or send email yourself."
    )


def call_tool(call):
    """Run one handler. Bad arguments become an ERROR string, not a crash."""
    name = call["name"]
    args = call["arguments"]
    if not isinstance(args, dict):
        return "ERROR: arguments must be a JSON object."
    if args.get("_error"):
        return "ERROR: " + str(args["_error"])
    fn = HANDLERS.get(name)
    if fn is None:
        return "ERROR: unknown tool " + repr(name) + "."
    return fn(args)
